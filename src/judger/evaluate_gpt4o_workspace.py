import argparse
import json
import os
from pathlib import Path
from typing import Any

from openai import OpenAI

from main_judge import MainJudger


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROBLEM_ID = "2013_Bank_Service_Problem"
DEFAULT_WORKSPACE = (
    REPO_ROOT
    / "output_workspace_modeltool"
    / "deepseek-v4-flash"
    / "2013_Bank_Service_Problem_20260817_232902"
)
DEFAULT_MODEL = "gpt-4o"
DEFAULT_BASE_URL = "https://api.openai.com/v1"
DIMENSIONS = (
    "structural_coherency",
    "scoring_decomposition",
    "modeling_groundedness",
    "data_groundedness",
    "analysis_groundedness",
    "innovativeness",
)


class _CompletionsProxy:
    """Force the configured model while preserving the existing judge code."""

    def __init__(self, completions: Any, model: str):
        self._completions = completions
        self._model = model

    def create(self, *args: Any, **kwargs: Any) -> Any:
        kwargs["model"] = self._model
        return self._completions.create(*args, **kwargs)


class _ChatProxy:
    def __init__(self, chat: Any, model: str):
        self.completions = _CompletionsProxy(chat.completions, model)


class _ClientProxy:
    def __init__(self, client: OpenAI, model: str):
        self.chat = _ChatProxy(client.chat, model)


def configure_judgers(judger: MainJudger, api_key: str, base_url: str, model: str) -> None:
    for metric_judger in judger.judgers.values():
        client = OpenAI(api_key=api_key, base_url=base_url)
        metric_judger.client = _ClientProxy(client, model)


def load_benchmark() -> dict[str, Any]:
    data_path = REPO_ROOT / "data" / "modeling_data_final.json"
    with data_path.open(encoding="utf-8") as file:
        return json.load(file)


def resolve_submission_path(raw_path: Path) -> Path:
    candidates = [raw_path.expanduser()]
    if not raw_path.is_absolute():
        candidates.append(REPO_ROOT / raw_path)
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved.exists():
            return resolved
    searched = ", ".join(str(candidate.resolve()) for candidate in candidates)
    raise ValueError(f"Submission path not found. Checked: {searched}")


def infer_problem_id(submission: Path, benchmark: dict[str, Any]) -> str:
    path_parts = [part.lower() for part in submission.parts]
    for problem_id in sorted(benchmark, key=len, reverse=True):
        problem_key = problem_id.lower()
        if any(
            part == problem_key or part.startswith(problem_key + "_")
            for part in path_parts
        ):
            return problem_id
    raise ValueError(
        "Could not infer the problem ID from the submission path; "
        "provide --problem-id explicitly."
    )


def load_submission(
    problem_id: str | None, submission: Path
) -> tuple[str, list, list, list[Path], str, Path]:
    submission_path = resolve_submission_path(submission)
    if submission_path.is_file():
        if submission_path.suffix.lower() != ".md":
            raise ValueError(f"The submitted report must be Markdown: {submission_path}")
        report_files = [submission_path]
    elif submission_path.is_dir():
        report_files = sorted(submission_path.glob("*.md"))
        if not report_files:
            raise ValueError(f"No Markdown reports found in: {submission_path}")
    else:
        raise ValueError(f"Unsupported submission path: {submission_path}")

    benchmark = load_benchmark()
    resolved_problem_id = problem_id or infer_problem_id(submission_path, benchmark)
    if resolved_problem_id not in benchmark:
        raise ValueError(f"Unknown problem ID: {resolved_problem_id}")

    writing = "\n\n---\n\n".join(
        f"# Submitted file: {report_file.name}\n\n"
        + report_file.read_text(encoding="utf-8")
        for report_file in report_files
    )
    criteria = benchmark[resolved_problem_id]
    grading_points = criteria.get("decomposition", {}).get("grading_points", [])
    roles = criteria.get("eval_roles", [])
    return (
        writing,
        grading_points,
        roles,
        report_files,
        resolved_problem_id,
        submission_path,
    )


def infer_output_group(submission: Path) -> str:
    parts = {part.lower() for part in submission.parts}
    if "openclaw_experiments" in parts or "output_workspace_openclaw" in parts:
        return "OpenClaw"
    if "output_workspace_modeltool" in parts:
        return "ModelTool"
    return "Reports"


def infer_run_name(submission: Path, problem_id: str) -> str:
    start = submission.parent if submission.is_file() else submission
    for directory in (start, *start.parents):
        if directory.name == problem_id or directory.name.startswith(problem_id + "_"):
            return directory.name
    return start.name


def dimension_score(result: dict[str, Any]) -> float | None:
    if result.get("error"):
        return None
    if result.get("aggregated_score") is not None:
        return float(result["aggregated_score"])
    if result.get("calculated_overall") is not None:
        return float(result["calculated_overall"])
    return None


def print_score_summary(results: dict[str, Any]) -> None:
    scores = []
    print("\nDimension scores:")
    for name in DIMENSIONS:
        score = dimension_score(results.get("judgements", {}).get(name, {}))
        if score is None:
            print(f"  {name}: unavailable")
            continue
        scores.append(score)
        print(f"  {name}: {score:.4f}")
    if scores:
        print(f"Macro average ({len(scores)} dimensions): {sum(scores) / len(scores):.4f}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate one ModelingBench workspace with an OpenAI-compatible API."
    )
    parser.add_argument(
        "submission",
        nargs="?",
        type=Path,
        help="Markdown report file or experiment directory. Uses the default ModelTool run when omitted.",
    )
    parser.add_argument(
        "--problem-id",
        help="Optional problem ID; inferred from the submission path when omitted.",
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        help="Legacy directory option; prefer the positional submission path.",
    )
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument(
        "--api-key",
        default=(
            os.environ.get("GPT4O_JUDGE_API_KEY")
            or os.environ.get("OPENAI_API_KEY")
        ),
        help="Defaults to GPT4O_JUDGE_API_KEY, then OPENAI_API_KEY.",
    )
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate paths and configuration without calling the API.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    benchmark = load_benchmark()
    problem_id = args.problem_id
    if args.workspace:
        if args.submission:
            legacy_problem_id = str(args.submission)
            if legacy_problem_id not in benchmark:
                raise ValueError(
                    "Do not provide both a positional submission path and --workspace."
                )
            problem_id = problem_id or legacy_problem_id
        submission = args.workspace
    else:
        submission = args.submission or DEFAULT_WORKSPACE

    (
        writing,
        grading_points,
        roles,
        report_files,
        problem_id,
        submission_path,
    ) = load_submission(problem_id, submission)
    output_group = infer_output_group(submission_path)
    run_name = infer_run_name(submission_path, problem_id)
    output_dir = (
        args.output_dir.resolve()
        if args.output_dir
        else REPO_ROOT
        / "output_judge"
        / output_group
        / args.model
        / run_name
    )

    print(f"Problem: {problem_id}")
    print(f"Submission: {submission_path}")
    print("Submitted reports: " + ", ".join(path.name for path in report_files))
    print(f"Judge model: {args.model}")
    print(f"API base: {args.base_url}")
    print(f"Output: {output_dir}")

    if args.dry_run:
        print(
            f"Dry run passed: {len(grading_points)} grading points, "
            f"{len(roles)} evaluation roles."
        )
        return

    if not str(args.api_key or "").strip():
        raise ValueError(
            "API key is missing; set GPT4O_JUDGE_API_KEY or OPENAI_API_KEY, "
            "or pass --api-key"
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    judger = MainJudger()
    configure_judgers(judger, args.api_key, args.base_url, args.model)
    results = judger.judge(
        str(output_dir), problem_id, writing, grading_points, roles
    )
    result_path = output_dir / f"{problem_id}.json"
    print(f"Judgement saved to: {result_path}")
    print_score_summary(results)


if __name__ == "__main__":
    main()
