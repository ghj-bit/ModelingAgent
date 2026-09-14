"""Repeat a fixed evolved interaction rubric on its three validation problems."""

import argparse
import copy
import json
import statistics
import time
from datetime import datetime
from pathlib import Path

try:
    from . import baseline
    from . import run_evolution as workflow_evolution
    from . import run_interaction_rubric_evolution as interaction
    from . import run_modelingbench_interaction_rubric_test as test_runner
except ImportError:
    import baseline
    import run_evolution as workflow_evolution
    import run_interaction_rubric_evolution as interaction
    import run_modelingbench_interaction_rubric_test as test_runner


DEFAULT_EXPERIMENT = (
    baseline.REPO_ROOT
    / "openclaw_experiments"
    / "interaction_rubric_20260905_154709"
)


def now() -> str:
    return datetime.now().isoformat()


def load_source_round(experiment: Path, round_number: int) -> dict:
    results_path = experiment / "workflows" / "results.json"
    results = workflow_evolution.read_json(results_path, [])
    source = next(
        (item for item in results if item.get("round") == round_number), None
    )
    if source is None:
        raise ValueError(f"Round {round_number} is not completed in {results_path}")

    rubric_path = experiment / "workflows" / f"round_{round_number}" / "rubric.json"
    rubric = workflow_evolution.read_json(rubric_path, {})
    if not rubric:
        raise FileNotFoundError(f"Rubric not found: {rubric_path}")
    interaction.validate_rubric(rubric)
    source = copy.deepcopy(source)
    source["rubric"] = rubric
    source["rubric_path"] = str(rubric_path)
    return source


def source_problem_scores(source: dict) -> dict[str, dict]:
    return {
        item["problem_id"]: {
            "four_dimension_average": item["average_score"],
            "dimension_scores": interaction.objective_dimensions(
                item.get("dimension_scores", {})
            ),
        }
        for item in source.get("problem_results", [])
    }


def metric_statistics(values: list[float], baseline_value: float | None) -> dict:
    mean = statistics.fmean(values)
    return {
        "values": values,
        "mean": mean,
        "population_stddev": statistics.pstdev(values),
        "min": min(values),
        "max": max(values),
        "range": max(values) - min(values),
        "source_round_value": baseline_value,
        "mean_delta_from_source_round": (
            mean - baseline_value if baseline_value is not None else None
        ),
    }


def build_summary(
    experiment: Path,
    source: dict,
    repetitions: int,
    completed: dict,
    failed: dict,
) -> dict:
    baseline_scores = source_problem_scores(source)
    repetition_results = []
    by_problem: dict[str, list[dict]] = {
        problem_id: []
        for problem_id in test_runner.experiment_validation_problems(experiment)
    }
    for repetition in range(1, repetitions + 1):
        key = f"repeat_{repetition}"
        records = completed.get(key, {})
        ordered = [
            records[problem_id]
            for problem_id in by_problem
            if problem_id in records
        ]
        for record in ordered:
            by_problem[record["problem_id"]].append(record)
        repetition_results.append(
            {
                "repetition": repetition,
                "average_score": (
                    statistics.fmean(item["average_score"] for item in ordered)
                    if ordered
                    else None
                ),
                "problems": ordered,
                "failed": failed.get(key, {}),
            }
        )

    problem_statistics = {}
    for problem_id, records in by_problem.items():
        if not records:
            continue
        source_score = baseline_scores.get(problem_id, {})
        dimensions = {
            dimension: metric_statistics(
                [record["dimension_scores"][dimension] for record in records],
                source_score.get("dimension_scores", {}).get(dimension),
            )
            for dimension in interaction.EVALUATION_DIMENSIONS
            if all(dimension in record.get("dimension_scores", {}) for record in records)
        }
        problem_statistics[problem_id] = {
            "four_dimension_average": metric_statistics(
                [record["average_score"] for record in records],
                source_score.get("four_dimension_average"),
            ),
            "dimensions": dimensions,
        }

    repetition_averages = [
        item["average_score"]
        for item in repetition_results
        if item["average_score"] is not None
    ]
    return {
        "evaluation": "fixed_interaction_rubric_repeat_test",
        "generated_at": now(),
        "source_experiment": str(experiment),
        "source_round": source["round"],
        "source_round_utility": source["utility"],
        "rubric_id": source["rubric"]["rubric_id"],
        "rubric_path": source["rubric_path"],
        "requested_repetitions": repetitions,
        "validation_problems": list(by_problem),
        "judge_dimensions": list(interaction.EVALUATION_DIMENSIONS),
        "source_problem_scores": baseline_scores,
        "repetitions": repetition_results,
        "round_utility_statistics": (
            metric_statistics(repetition_averages, source["utility"])
            if repetition_averages
            else None
        ),
        "problem_statistics": problem_statistics,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run a fixed interaction-rubric round repeatedly on the source "
            "experiment's validation problems and quantify score variation."
        )
    )
    parser.add_argument("--exp", default=str(DEFAULT_EXPERIMENT))
    parser.add_argument("--source-round", type=int, default=4)
    parser.add_argument("--repetitions", type=int, default=2)
    parser.add_argument("--concurrency", type=int, default=3)
    parser.add_argument("--judge-repeats", type=int, default=1)
    parser.add_argument("--judge-concurrency", type=int, default=1)
    parser.add_argument("--validation-attempts", type=int, default=3)
    parser.add_argument("--retry-concurrency", type=int, default=1)
    parser.add_argument("--validation-retry-delay", type=float, default=15.0)
    parser.add_argument("--model", default="deepseek/deepseek-v4-flash")
    parser.add_argument("--thinking", default="high")
    parser.add_argument("--timeout", type=int, default=7200)
    parser.add_argument("--completion-grace", type=float, default=60.0)
    parser.add_argument("--openclaw-command")
    parser.add_argument("--output-root")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if min(
        args.source_round,
        args.repetitions,
        args.concurrency,
        args.judge_repeats,
        args.judge_concurrency,
        args.validation_attempts,
        args.retry_concurrency,
    ) < 1:
        raise ValueError("round, repetition, concurrency, Judge, and retry counts must be positive")
    if args.validation_retry_delay < 0:
        raise ValueError("--validation-retry-delay must be non-negative")

    experiment = Path(args.exp).resolve()
    source = load_source_round(experiment, args.source_round)
    problem_ids = test_runner.experiment_validation_problems(experiment)
    problems = baseline.load_problems()
    missing = [problem_id for problem_id in problem_ids if problem_id not in problems]
    if missing:
        raise ValueError("Unknown validation problem(s): " + ", ".join(missing))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_root = (
        Path(args.output_root).resolve()
        if args.output_root
        else experiment
        / "repeat_tests"
        / f"round_{args.source_round}_repeat_{timestamp}"
    )
    output_root.mkdir(parents=True, exist_ok=True)
    prompt_path = output_root / "prompt.md"
    prompt_path.write_text(
        interaction.build_prompt(
            baseline.BASELINE_PROMPT_TEMPLATE_PATH.read_text(encoding="utf-8"),
            source["rubric"],
        ),
        encoding="utf-8",
    )
    workflow_evolution.write_json(
        output_root / "source_rubric.json",
        {
            "source_experiment": str(experiment),
            "source_round": args.source_round,
            "source_utility": source["utility"],
            "rubric_path": source["rubric_path"],
            "rubric": source["rubric"],
        },
    )

    workflow_evolution.configure_completion_grace(
        baseline.run_problem, args.completion_grace
    )
    checkpoint_path = output_root / "checkpoint.json"
    checkpoint = workflow_evolution.read_json(
        checkpoint_path, {"completed": {}, "failed": {}}
    )
    completed = checkpoint.setdefault("completed", {})
    failed = checkpoint.setdefault("failed", {})

    print(
        f"Fixed rubric: round={args.source_round} "
        f"id={source['rubric']['rubric_id']}",
        flush=True,
    )
    print(f"Repeat-test output: {output_root}", flush=True)

    for repetition in range(1, args.repetitions + 1):
        key = f"repeat_{repetition}"
        repeat_completed = completed.setdefault(key, {})
        repeat_failed = failed.setdefault(key, {})
        pending = [problem_id for problem_id in problem_ids if problem_id not in repeat_completed]
        for attempt in range(1, args.validation_attempts + 1):
            if not pending:
                break
            if attempt > 1 and args.validation_retry_delay:
                time.sleep(args.validation_retry_delay)
            run_args = copy.copy(args)
            # Keep physical paths short enough for Windows' traditional
            # MAX_PATH limit. Full problem IDs remain in run metadata/results.
            run_args.output_root = str(output_root)
            run_args.flat_run_layout = True
            run_args.run_directory_prefixes = {
                problem_id: f"r{repetition}p{index}"
                for index, problem_id in enumerate(problem_ids, start=1)
            }
            run_args.prompt_template = str(prompt_path)
            run_args.prepare_only = False
            run_args.skip_judge = False
            run_args.agent = None
            run_args.judge_label = (
                f"interaction-rubric-round-{args.source_round}-{key}"
            )
            run_args.concurrency = (
                min(args.concurrency, len(pending))
                if attempt == 1
                else min(args.retry_concurrency, len(pending))
            )
            print(
                f"{key}: attempt {attempt}/{args.validation_attempts}, "
                f"pending={len(pending)}, concurrency={run_args.concurrency}",
                flush=True,
            )
            selected = [(problem_id, problems[problem_id]) for problem_id in pending]
            succeeded, attempt_failed = test_runner.run_selected(
                selected, run_args, source["rubric"]
            )
            for record in succeeded:
                problem_id = record["problem_id"]
                repeat_completed[problem_id] = record
                repeat_failed.pop(problem_id, None)
            for failure in attempt_failed:
                problem_id = failure["problem_id"]
                history = repeat_failed.setdefault(problem_id, {}).setdefault(
                    "history", []
                )
                history.append(
                    {
                        "attempt": attempt,
                        "time": now(),
                        "error": failure["error"],
                    }
                )
                repeat_failed[problem_id]["error"] = failure["error"]
            workflow_evolution.write_json(checkpoint_path, checkpoint)
            pending = [
                problem_id for problem_id in problem_ids if problem_id not in repeat_completed
            ]
        if pending:
            raise RuntimeError(
                f"{key} still has failed problems after {args.validation_attempts} "
                f"attempt(s): {', '.join(pending)}. Resume with --output-root "
                f"{output_root}"
            )

    summary = build_summary(
        experiment, source, args.repetitions, completed, failed
    )
    summary.update(
        {
            "model": args.model,
            "problem_concurrency": args.concurrency,
            "judge_repeats": args.judge_repeats,
            "judge_concurrency": args.judge_concurrency,
            "checkpoint": str(checkpoint_path),
        }
    )
    summary_path = output_root / "repeat_test_results.json"
    workflow_evolution.write_json(summary_path, summary)
    print(f"Repeat-test summary: {summary_path}", flush=True)


if __name__ == "__main__":
    main()
