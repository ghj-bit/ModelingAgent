"""Run ModelingBench after retrieving only the most relevant workspace skills."""

import argparse
import copy
import json
import math
import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

try:
    from . import baseline
    from . import run_modelingbench_baseline as baseline_runner
    from . import run_judge_stability
except ImportError:
    import baseline
    import run_modelingbench_baseline as baseline_runner
    import run_judge_stability


SKILL_RETRIEVAL_PROMPT_TEMPLATE_PATH = (
    baseline.SCRIPT_DIR / "prompt_modelingbench_skill_retrieval.md"
)


TOKEN_PATTERN = re.compile(r"[a-z][a-z0-9_-]{2,}")
STOPWORDS = {
    "about", "after", "also", "among", "and", "are", "been", "before",
    "being", "between", "both", "build", "can", "complete", "could",
    "data", "determine", "each", "from", "has", "have", "into", "its",
    "final", "for", "model", "modeling", "more", "must", "needed", "not",
    "only", "other",
    "problem", "report", "results", "should", "solution", "such", "than",
    "that", "the", "their", "then", "these", "they", "this", "through",
    "use", "using", "when", "where", "which", "while", "will", "with",
}
DEFAULT_EXCLUDED_SKILLS = {"fuse-verified-patches"}


def tokenize(text: str) -> list[str]:
    return [
        token
        for token in TOKEN_PATTERN.findall(text.lower())
        if token not in STOPWORDS
    ]


def parse_skill(skill_dir: Path) -> dict:
    skill_path = skill_dir / "SKILL.md"
    text = skill_path.read_text(encoding="utf-8")
    name = skill_dir.name
    description = ""
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            for line in parts[1].splitlines():
                key, separator, value = line.partition(":")
                if not separator:
                    continue
                if key.strip() == "name":
                    name = value.strip().strip("'\"") or name
                elif key.strip() == "description":
                    description = value.strip().strip("'\"")
    examples_match = re.search(
        r"^## Generalization Examples\s*$\n(.*?)(?=^##\s|\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    generalization_examples = examples_match.group(1).strip() if examples_match else ""
    weighted_text = " ".join(
        [name] * 4 + [description] * 3 + [generalization_examples]
    )
    return {
        "directory": skill_dir.name,
        "name": name,
        "description": description,
        "generalization_examples": generalization_examples,
        "path": str(skill_path.resolve()),
        "tokens": tokenize(weighted_text),
    }


def load_skill_catalog(
    skills_source: Path,
    excluded_skills: set[str] | None = None,
) -> list[dict]:
    skills_source = skills_source.resolve()
    if not skills_source.is_dir():
        raise FileNotFoundError(f"Skills source not found: {skills_source}")
    excluded_skills = excluded_skills or set()
    catalog = [
        parse_skill(path)
        for path in sorted(skills_source.iterdir())
        if path.is_dir()
        and path.name not in excluded_skills
        and (path / "SKILL.md").is_file()
    ]
    if not catalog:
        raise ValueError(f"No SKILL.md files found under: {skills_source}")
    return catalog


def problem_query(problem: dict) -> str:
    # Deliberately exclude decomposition, eval_roles, and all Judge information.
    return "\n".join(
        str(problem.get(field, "")) for field in ("title", "question")
    )


def bm25_rank(query: str, catalog: list[dict]) -> list[dict]:
    query_counts = Counter(tokenize(query))
    document_counts = [Counter(item["tokens"]) for item in catalog]
    lengths = [sum(counts.values()) for counts in document_counts]
    average_length = sum(lengths) / len(lengths) if lengths else 1.0
    document_frequency = Counter()
    for counts in document_counts:
        document_frequency.update(counts.keys())

    ranked = []
    document_total = len(catalog)
    k1, b = 1.5, 0.75
    for item, counts, length in zip(catalog, document_counts, lengths):
        contributions = []
        score = 0.0
        for token, query_frequency in query_counts.items():
            frequency = counts.get(token, 0)
            if not frequency:
                continue
            df = document_frequency[token]
            inverse_frequency = math.log(
                1.0 + (document_total - df + 0.5) / (df + 0.5)
            )
            denominator = frequency + k1 * (
                1.0 - b + b * length / max(average_length, 1.0)
            )
            contribution = (
                inverse_frequency
                * frequency
                * (k1 + 1.0)
                / denominator
                * (1.0 + math.log(min(query_frequency, 3)))
            )
            score += contribution
            contributions.append((token, contribution))
        ranked.append(
            {
                "directory": item["directory"],
                "name": item["name"],
                "description": item["description"],
                "score": score,
                "matched_terms": [
                    token
                    for token, _ in sorted(
                        contributions, key=lambda pair: (-pair[1], pair[0])
                    )[:8]
                ],
            }
        )
    return sorted(ranked, key=lambda item: (-item["score"], item["directory"]))


def retrieve_skills(
    problem: dict,
    catalog: list[dict],
    top_k: int,
    relative_threshold: float,
) -> dict:
    ranking = bm25_rank(problem_query(problem), catalog)
    best_score = ranking[0]["score"]
    cutoff = best_score * relative_threshold
    selected = [
        item["directory"]
        for item in ranking
        if item["score"] > 0 and item["score"] >= cutoff
    ][:top_k]
    if not selected:
        selected = [ranking[0]["directory"]]
    return {
        "selected_skills": selected,
        "top_k": top_k,
        "relative_threshold": relative_threshold,
        "ranking": ranking,
    }


def result_record(problem_id: str, result: dict, retrieval: dict) -> dict:
    repeated_judge = result.get("repeated_judge")
    if repeated_judge:
        record = {
            "problem_id": problem_id,
            "status": "completed",
            "run_dir": str(result["run_dir"]),
            "final_report": str(result["final_report"]),
            "judge_result": (
                str(result["judge_result"]) if result.get("judge_result") else None
            ),
            "judge_stability_result": str(result["judge_stability_result"]),
            "judge_repeats": result["judge_repeats"],
            "average_score": result["average_score"],
            "dimension_scores": result["dimension_scores"],
        }
    else:
        record = baseline_runner.result_record(problem_id, result)
    record["skill_retrieval"] = retrieval
    return record


def load_existing_run(
    problem_id: str,
    args,
    retrieval: dict,
) -> dict:
    """Load one prepared run so scoring/summary generation can be resumed."""
    output_root = Path(args.output_root).resolve()
    model_dir = output_root / baseline.slugify(args.model)
    run_name = (
        f"{baseline.safe_path_component(problem_id)}_"
        f"{args.resume_run_timestamp}"
    )
    run_dir = model_dir / run_name
    metadata_path = run_dir / "meta" / "run.json"
    if not metadata_path.is_file():
        raise FileNotFoundError(f"Existing run metadata is missing: {metadata_path}")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata.get("problem_id") != problem_id:
        raise ValueError(f"Existing run has a different problem ID: {metadata_path}")
    if metadata.get("model") != args.model:
        raise ValueError(f"Existing run uses a different model: {metadata_path}")
    installed_skills = metadata.get("installed_skills")
    if installed_skills != retrieval["selected_skills"]:
        raise ValueError(
            "Existing run's installed skills do not match the current retrieval "
            f"settings: {run_dir}"
        )
    final_report = Path(metadata.get("final_report", ""))
    if not final_report.is_file() or not final_report.read_text(
        encoding="utf-8"
    ).strip():
        raise FileNotFoundError(
            f"Existing run has no non-empty final report: {final_report}"
        )
    print(f"[{problem_id}] resuming existing run: {run_dir}", flush=True)
    return {
        "run_dir": run_dir,
        "final_report": final_report,
        "judge_result": None,
        "average_score": None,
        "workflow_check": None,
    }


def run_selected(selected, args, catalog) -> tuple[list[dict], list[dict]]:
    completed, failed = [], []

    def run_one(problem_id: str, problem: dict, retrieval: dict):
        task_args = copy.copy(args)
        task_args.selected_skills = retrieval["selected_skills"]
        # The repeated evaluator below is the sole Judge path for this run.
        task_args.skip_judge = True
        print(
            f"[{problem_id}] retrieved skills: "
            + ", ".join(retrieval["selected_skills"]),
            flush=True,
        )
        result = (
            load_existing_run(problem_id, task_args, retrieval)
            if args.resume_run_timestamp
            else baseline.run_problem(problem_id, problem, task_args)
        )
        if args.skip_judge or args.prepare_only:
            return result, retrieval

        stability_path = result["run_dir"] / "meta" / "judge_stability.json"
        payload = run_judge_stability.evaluate_reports_repeated(
            problem_id,
            {"report": result["final_report"]},
            args.judge_repeats,
            args.judge_label,
            stability_path,
            result["run_dir"] / "meta",
        )
        repeated = payload["average_scores"]["round_report"]
        trials = payload["evaluations"]["report"]
        result.update(
            {
                "repeated_judge": True,
                "judge_stability_result": stability_path,
                "judge_repeats": repeated["trial_count"],
                "judge_result": Path(trials[-1]["raw_result"]),
                "average_score": repeated["average_overall_score"],
                "dimension_scores": repeated["average_dimension_scores"],
            }
        )
        return result, retrieval

    with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        futures = {}
        for problem_id, problem in selected:
            retrieval = retrieve_skills(
                problem, catalog, args.top_k, args.relative_threshold
            )
            future = executor.submit(run_one, problem_id, problem, retrieval)
            futures[future] = (problem_id, retrieval)
        for future in as_completed(futures):
            problem_id, retrieval = futures[future]
            try:
                result, retrieval = future.result()
                completed.append(result_record(problem_id, result, retrieval))
            except Exception as error:
                failed.append(
                    {
                        "problem_id": problem_id,
                        "status": "failed",
                        "error": repr(error),
                        "skill_retrieval": retrieval,
                    }
                )
                print(f"[{problem_id}] failed: {error}", flush=True)
    completed.sort(key=lambda item: item["problem_id"])
    failed.sort(key=lambda item: item["problem_id"])
    return completed, failed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run ModelingBench with per-problem BM25 skill retrieval."
    )
    parser.add_argument("problem_ids", nargs="*", help="One or more problem IDs.")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--concurrency", type=int, default=1)
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--relative-threshold", type=float, default=0.6)
    parser.add_argument("--agent")
    parser.add_argument("--model", default="deepseek/deepseek-v4-flash")
    parser.add_argument("--thinking", default="high")
    parser.add_argument("--timeout", type=int, default=7200)
    parser.add_argument("--openclaw-command")
    parser.add_argument(
        "--prompt-template", default=str(SKILL_RETRIEVAL_PROMPT_TEMPLATE_PATH)
    )
    parser.add_argument(
        "--output-root",
        default=str(baseline.REPO_ROOT / "output_workspace_openclaw_skill_retrieval"),
    )
    parser.add_argument(
        "--skills-source", default=str(baseline.SCRIPT_DIR / "skills")
    )
    parser.add_argument("--skip-judge", action="store_true")
    parser.add_argument(
        "--judge-repeats",
        type=int,
        default=3,
        help="Number of repeated six-metric Judge evaluations per final report.",
    )
    parser.add_argument(
        "--judge-label",
        default="skill-retrieval-judge-deepseek-v4-flash",
        help="Output label only; Judge model configuration remains unchanged.",
    )
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument(
        "--resume-run-timestamp",
        metavar="YYYYMMDD_HHMMSS",
        help=(
            "Resume scoring and summary generation from existing per-problem "
            "runs with this timestamp; do not invoke OpenClaw to regenerate reports."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.concurrency < 1:
        raise ValueError("--concurrency must be at least 1")
    if args.top_k < 1:
        raise ValueError("--top-k must be at least 1")
    if not 0 <= args.relative_threshold <= 1:
        raise ValueError("--relative-threshold must be between 0 and 1")
    if args.judge_repeats < 1:
        raise ValueError("--judge-repeats must be at least 1")
    if args.agent and args.concurrency > 1:
        raise ValueError("--agent cannot be shared by concurrent problem runs")
    if args.resume_run_timestamp and not re.fullmatch(
        r"\d{8}_\d{6}", args.resume_run_timestamp
    ):
        raise ValueError("--resume-run-timestamp must use YYYYMMDD_HHMMSS")

    problems = baseline.load_problems()
    selected = baseline_runner.select_problems(
        problems, args.problem_ids, args.all
    )
    catalog = load_skill_catalog(
        Path(args.skills_source), DEFAULT_EXCLUDED_SKILLS
    )
    output_root = Path(args.output_root).resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    started_at = datetime.now()
    completed, failed = run_selected(selected, args, catalog)
    finished_at = datetime.now()
    average_score, average_dimensions = baseline_runner.aggregate_scores(completed)
    summary = {
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "elapsed_seconds": (finished_at - started_at).total_seconds(),
        "model": args.model,
        "concurrency": args.concurrency,
        "retrieval": {
            "method": "BM25",
            "query_fields": ["title", "question"],
            "indexed_skill_fields": [
                "name",
                "description",
                "Generalization Examples",
            ],
            "top_k": args.top_k,
            "relative_threshold": args.relative_threshold,
            "skills_source": str(Path(args.skills_source).resolve()),
            "catalog_size": len(catalog),
            "excluded_skills": sorted(DEFAULT_EXCLUDED_SKILLS),
        },
        "average_score": average_score,
        "average_dimension_scores": average_dimensions,
        "completed": completed,
        "failed": failed,
    }
    summary_path = output_root / (
        f"skill_retrieval_results_{finished_at.strftime('%Y%m%d_%H%M%S')}.json"
    )
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Skill retrieval summary: {summary_path}", flush=True)
    if failed:
        raise RuntimeError(f"{len(failed)} benchmark problem(s) failed")


if __name__ == "__main__":
    main()
