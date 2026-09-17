"""Generate planned initial modeling-report drafts for test tasks.

This launcher is the draft-only counterpart to ``run_clean_baseline_test.py``.
It retains cumulative batches of five and uses the same test dataset, but
the Agent is asked for a report framework and a step-by-step completion plan
rather than a fully executed final report.

Resume is enabled only when an existing directory is supplied explicitly with
``--experiment``. Without it, the launcher always creates a new experiment.

Usage:
    python draft_gen/run_clean_baseline_test_initial_draft.py
    python draft_gen/run_clean_baseline_test_initial_draft.py --num-problems 18
    python draft_gen/run_clean_baseline_test_initial_draft.py --initialize-only
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_NUM_PROBLEMS = 5
BATCH_SIZE = 5
EXPERIMENT_PREFIX = "interaction_strategy_clean_baseline_initial_draft_test_"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="deepseek/deepseek-v4-flash")
    parser.add_argument("--thinking", default="high")
    parser.add_argument("--timeout", type=int, default=7200)
    parser.add_argument(
        "--num-problems",
        type=int,
        default=DEFAULT_NUM_PROBLEMS,
        help="Number of tasks selected from the start of the test set when --problem-id is omitted (default: 5)",
    )
    parser.add_argument(
        "--problem-id",
        action="append",
        nargs="+",
        metavar="ID",
        help="Specific test task ID(s) to run, in the supplied order; may be repeated",
    )
    parser.add_argument("--experiment", "--exp", type=Path)
    parser.add_argument("--openclaw-command")
    parser.add_argument("--initialize-only", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.timeout <= 86400:
        parser.error("--timeout must be between 1 and 86400 seconds")
    if args.num_problems < 1:
        parser.error("--num-problems must be positive")
    return args


def selected_task_ids(
    num_problems: int, requested_problem_ids: list[str] | None = None
) -> list[str]:
    path = REPO_ROOT / "data" / "modeling_data_test.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not payload:
        raise ValueError(f"Dataset must be a non-empty task mapping: {path}")
    if requested_problem_ids:
        unknown = [problem_id for problem_id in requested_problem_ids if problem_id not in payload]
        if unknown:
            raise ValueError("Unknown test problem ID(s): " + ", ".join(unknown))
        if len(requested_problem_ids) != len(set(requested_problem_ids)):
            raise ValueError("--problem-id values must be unique")
        return requested_problem_ids
    if num_problems > len(payload):
        raise ValueError(
            f"--num-problems={num_problems} exceeds the {len(payload)} test tasks"
        )
    return list(payload)[:num_problems]


def existing_problem_count(experiment: Path, problem_ids: list[str]) -> int:
    config_path = experiment / "runs" / "config.json"
    if not config_path.is_file():
        return 0
    config = json.loads(config_path.read_text(encoding="utf-8"))
    saved = config.get("validation_problems")
    if not isinstance(saved, list) or not saved:
        return 0
    if saved != problem_ids[: len(saved)]:
        raise ValueError(
            "Existing initial-draft experiment has a different task prefix; "
            "use the same test selection or a new --experiment directory."
        )
    if len(saved) > len(problem_ids):
        raise ValueError(
            f"Existing experiment already tracks {len(saved)} task(s), but "
            f"--num-problems selected only {len(problem_ids)}."
        )
    return len(saved)


def merge_existing_and_requested_problem_ids(
    experiment: Path, requested_problem_ids: list[str]
) -> tuple[list[str], list[str]]:
    """Keep the experiment order and append only newly requested task IDs."""
    config_path = experiment / "runs" / "config.json"
    if not config_path.is_file():
        return requested_problem_ids, []
    config = json.loads(config_path.read_text(encoding="utf-8"))
    saved = config.get("validation_problems")
    if not isinstance(saved, list) or not saved:
        return requested_problem_ids, []
    saved_set = set(saved)
    duplicates = [problem_id for problem_id in requested_problem_ids if problem_id in saved_set]
    merged = [*saved, *(problem_id for problem_id in requested_problem_ids if problem_id not in saved_set)]
    return merged, duplicates


def completed_problem_ids(
    experiment: Path, problem_ids: list[str] | None = None
) -> set[str]:
    """Return durable completions from the checkpoint or aggregate result."""
    selected = set(problem_ids) if problem_ids is not None else None
    completed_ids: set[str] = set()
    checkpoint_path = experiment / "runs" / "round_1" / "evaluation_checkpoint.json"
    if checkpoint_path.is_file():
        checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        completed = checkpoint.get("completed", {})
        if isinstance(completed, dict):
            completed_ids.update(
                problem_id
                for problem_id, repetitions in completed.items()
                if (selected is None or problem_id in selected)
                and isinstance(repetitions, dict)
                and ("1" in repetitions or repetitions.get("problem_id") == problem_id)
            )
    completed_ids.update(finalized_problem_ids(experiment, problem_ids))
    return completed_ids


def finalized_problem_ids(
    experiment: Path, problem_ids: list[str] | None = None
) -> set[str]:
    """Return tasks already written to the aggregate result file."""
    result_path = experiment / "runs" / "round_1" / "result.json"
    if not result_path.is_file():
        return set()
    selected = set(problem_ids) if problem_ids is not None else None
    result = json.loads(result_path.read_text(encoding="utf-8"))
    return {
        item["problem_id"]
        for item in result.get("problem_results", [])
        if isinstance(item, dict)
        and isinstance(item.get("problem_id"), str)
        and (selected is None or item["problem_id"] in selected)
    }


def cumulative_batch_ends(
    total: int, tracked_prefix: int, recover_tracked: bool = False
) -> list[int]:
    ends = [tracked_prefix] if recover_tracked and tracked_prefix > 0 else []
    next_end = tracked_prefix
    while next_end < total:
        next_end = min(total, max(BATCH_SIZE, next_end + BATCH_SIZE))
        ends.append(next_end)
    return ends


def main() -> int:
    args = parse_args()
    requested_problem_ids = [
        problem_id for group in (args.problem_id or []) for problem_id in group
    ]
    problem_ids = selected_task_ids(args.num_problems, requested_problem_ids or None)
    if len(problem_ids) != len(set(problem_ids)):
        raise ValueError("Selected datasets contain duplicate task IDs")

    experiment = args.experiment
    if experiment is None:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        experiment = REPO_ROOT / "openclaw_experiments" / f"{EXPERIMENT_PREFIX}{stamp}"
    elif not experiment.is_absolute():
        experiment = REPO_ROOT / experiment
    experiment = experiment.resolve()
    if args.experiment is not None and requested_problem_ids:
        problem_ids, duplicates = merge_existing_and_requested_problem_ids(
            experiment, problem_ids
        )
        if duplicates:
            print(
                "Skipping task ID(s) already registered in the experiment: "
                + ", ".join(duplicates),
                flush=True,
            )
    print(f"Experiment: {experiment}", flush=True)
    tracked_prefix = existing_problem_count(experiment, problem_ids)
    completed_ids = completed_problem_ids(experiment, problem_ids)
    finalized_ids = finalized_problem_ids(experiment, problem_ids)
    tracked_ids = set(problem_ids[:tracked_prefix])
    tracked_has_unfinished = bool(tracked_ids - completed_ids)
    if (
        tracked_prefix >= len(problem_ids)
        and not tracked_has_unfinished
        and set(problem_ids) <= finalized_ids
    ):
        batch_ends = []
    else:
        batch_ends = cumulative_batch_ends(
            len(problem_ids), tracked_prefix, tracked_has_unfinished
        )
        if not batch_ends:
            batch_ends = [len(problem_ids)]
    if completed_ids:
        print(
            f"Resume state: {len(completed_ids)}/{len(problem_ids)} task(s) "
            "already completed; completed tasks will be skipped.",
            flush=True,
        )
    for batch_index, end in enumerate(batch_ends, 1):
        cumulative_problem_ids = problem_ids[:end]
        pending_ids = [
            problem_id
            for problem_id in cumulative_problem_ids
            if problem_id not in completed_ids
        ]
        current_batch_size = max(1, len(pending_ids))
        concurrency = str(min(BATCH_SIZE, current_batch_size))
        command = [
            sys.executable,
            "-m", "src.OpenClaw.run_substantive_interaction_strategy_clean_baseline_initial_draft",
            "--exp", str(experiment),
            "--max-rounds", "1",
            "--model", args.model,
            "--thinking", args.thinking,
            "--timeout", str(args.timeout),
            "--concurrency", concurrency,
            "--retry-concurrency", concurrency,
            "--validation-repetitions", "1",
            "--problem-id", *cumulative_problem_ids,
        ]
        if args.openclaw_command:
            command.extend(["--openclaw-command", args.openclaw_command])
        if args.initialize_only:
            command.append("--initialize-only")
        print(
            f"Batch {batch_index}/{len(batch_ends)}: tasks 1-{end}; "
            f"new/unfinished window <= {current_batch_size}; concurrency: {concurrency}",
            flush=True,
        )
        result = subprocess.run(command, cwd=REPO_ROOT)
        if result.returncode:
            print(
                f"Initial-draft baseline failed with exit code {result.returncode}. "
                f'Resume with the same options and --experiment "{experiment}".',
                file=sys.stderr,
            )
            return result.returncode
        if not args.initialize_only:
            completed_ids.update(cumulative_problem_ids)

    report_root = experiment / "runs" / "round_1"
    print(f"Initial-draft report root: {report_root}")
    if args.initialize_only:
        print("Initialization only: reports have not been generated.")
    else:
        print(f"Final scores: {report_root / 'result.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
