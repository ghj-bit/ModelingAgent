"""Run the fixed OpenClaw ModelingBench baseline with problem-level concurrency."""

import argparse
import copy
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

try:
    from . import baseline
    from . import run_judge_stability
except ImportError:
    import baseline
    import run_judge_stability


def select_problems(
    problems: dict[str, dict], problem_ids: list[str], run_all: bool
) -> list[tuple[str, dict]]:
    if bool(problem_ids) == bool(run_all):
        raise ValueError("provide one or more problem IDs, or use --all")
    unknown = [problem_id for problem_id in problem_ids if problem_id not in problems]
    if unknown:
        raise ValueError(f"unknown problem ID(s): {', '.join(unknown)}")
    if run_all:
        return list(problems.items())
    return [(problem_id, problems[problem_id]) for problem_id in problem_ids]


def result_record(problem_id: str, result: dict) -> dict:
    if result.get("repeated_judge"):
        return {
            "problem_id": problem_id,
            "status": "completed",
            "run_dir": str(result["run_dir"]),
            "final_report": str(result["final_report"]),
            "judge_result": str(result["judge_result"]),
            "judge_stability_result": str(result["judge_stability_result"]),
            "judge_repeats": result["judge_repeats"],
            "average_score": result["average_score"],
            "dimension_scores": result["dimension_scores"],
        }
    judge_result = result.get("judge_result")
    dimension_scores = (
        baseline.calculate_dimension_scores(Path(judge_result))
        if judge_result
        else None
    )
    return {
        "problem_id": problem_id,
        "status": "completed",
        "run_dir": str(result["run_dir"]),
        "final_report": str(result["final_report"]),
        "judge_result": (
            str(result["judge_result"]) if result.get("judge_result") else None
        ),
        "average_score": result.get("average_score"),
        "dimension_scores": dimension_scores,
    }


def aggregate_scores(completed: list[dict]) -> tuple[float | None, dict[str, float]]:
    overall_scores = [
        item["average_score"]
        for item in completed
        if isinstance(item.get("average_score"), (int, float))
    ]
    dimension_scores = {}
    for dimension in baseline.EXPECTED_JUDGERS:
        values = [
            item["dimension_scores"][dimension]
            for item in completed
            if isinstance(item.get("dimension_scores"), dict)
            and isinstance(item["dimension_scores"].get(dimension), (int, float))
        ]
        if values:
            dimension_scores[dimension] = sum(values) / len(values)
    overall = sum(overall_scores) / len(overall_scores) if overall_scores else None
    return overall, dimension_scores


def run_selected(selected: list[tuple[str, dict]], args) -> tuple[list[dict], list[dict]]:
    completed = []
    failed = []

    def run_one(problem_id: str, problem: dict) -> dict:
        task_args = copy.copy(args)
        # Repeated evaluation below is the sole Judge path for this runner.
        task_args.skip_judge = True
        result = baseline.run_problem(problem_id, problem, task_args)
        if args.skip_judge or args.prepare_only:
            return result

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
        return result

    with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        futures = {
            executor.submit(run_one, problem_id, problem): problem_id
            for problem_id, problem in selected
        }
        for future in as_completed(futures):
            problem_id = futures[future]
            try:
                completed.append(result_record(problem_id, future.result()))
            except Exception as error:
                failed.append(
                    {
                        "problem_id": problem_id,
                        "status": "failed",
                        "error": repr(error),
                    }
                )
                print(f"[{problem_id}] failed: {error}", flush=True)
    completed.sort(key=lambda item: item["problem_id"])
    failed.sort(key=lambda item: item["problem_id"])
    return completed, failed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the fixed OpenClaw baseline on selected ModelingBench problems "
            "and judge only each final report."
        )
    )
    parser.add_argument("problem_ids", nargs="*", help="One or more problem IDs.")
    parser.add_argument("--all", action="store_true", help="Run all benchmark problems.")
    parser.add_argument(
        "--concurrency",
        type=int,
        default=1,
        help="Maximum number of benchmark problems run concurrently.",
    )
    parser.add_argument("--agent", help="Use an existing OpenClaw agent ID.")
    parser.add_argument("--model", default="deepseek/deepseek-v4-flash")
    parser.add_argument("--thinking", default="high")
    parser.add_argument("--timeout", type=int, default=7200)
    parser.add_argument("--openclaw-command")
    parser.add_argument(
        "--prompt-template",
        default=str(baseline.BASELINE_PROMPT_TEMPLATE_PATH),
    )
    parser.add_argument(
        "--output-root",
        default=str(baseline.REPO_ROOT / "output_workspace_openclaw_baseline"),
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
        default="baseline-judge-deepseek-v4-flash",
        help="Output label only; Judge model configuration remains unchanged.",
    )
    parser.add_argument("--prepare-only", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.concurrency < 1:
        raise ValueError("--concurrency must be at least 1")
    if args.judge_repeats < 1:
        raise ValueError("--judge-repeats must be at least 1")
    if args.agent and args.concurrency > 1:
        raise ValueError("--agent cannot be shared by concurrent problem runs")

    problems = baseline.load_problems()
    selected = select_problems(problems, args.problem_ids, args.all)
    output_root = Path(args.output_root).resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    started_at = datetime.now()
    completed, failed = run_selected(selected, args)
    finished_at = datetime.now()
    average_score, average_dimension_scores = aggregate_scores(completed)
    summary = {
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "elapsed_seconds": (finished_at - started_at).total_seconds(),
        "prompt_template": str(Path(args.prompt_template).resolve()),
        "model": args.model,
        "concurrency": args.concurrency,
        "judge_repeats": args.judge_repeats,
        "average_score": average_score,
        "average_dimension_scores": average_dimension_scores,
        "completed": completed,
        "failed": failed,
    }
    summary_path = output_root / (
        f"baseline_results_{finished_at.strftime('%Y%m%d_%H%M%S')}.json"
    )
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Baseline summary: {summary_path}", flush=True)
    if failed:
        raise RuntimeError(f"{len(failed)} benchmark problem(s) failed")


if __name__ == "__main__":
    main()
