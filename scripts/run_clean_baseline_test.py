"""Generate clean-baseline drafts for the requested number of test tasks.

Usage:
    python scripts/run_clean_baseline_test.py
    python scripts/run_clean_baseline_test.py --num-problems 18
    python scripts/run_clean_baseline_test.py --initialize-only

Relative experiment paths are resolved from the repository root.
Workspace preparation creates no interaction log subdirectories and does not
copy output/code/wait_for_expert_reply.py.
The experiment root contains only runs; configuration and checkpoints live there.
Tasks are submitted in batches of five. Within one batch, Agents run in
parallel; after that batch finishes, the launcher submits the next cumulative
task list so the clean-baseline runner can resume completed reports and extend
the experiment configuration.
Each Agent begins execution immediately after its own registration completes.
Without --experiment, a new timestamped experiment is created. Resume is only
enabled when the experiment directory is supplied explicitly with --experiment.
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
EXPERIMENT_PREFIX = "interaction_strategy_clean_baseline_test_"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="deepseek/deepseek-v4-flash")
    parser.add_argument("--thinking", default="high")
    parser.add_argument("--timeout", type=int, default=7200)
    parser.add_argument(
        "--num-problems",
        type=int,
        default=DEFAULT_NUM_PROBLEMS,
        help="Number of tasks selected from the start of the test set (default: 5)",
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


def selected_task_ids(num_problems: int) -> list[str]:
    path = REPO_ROOT / "data" / "modeling_data_test.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not payload:
        raise ValueError(f"Dataset must be a non-empty task mapping: {path}")
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
            "Existing clean-baseline experiment has a different task prefix; "
            "use the same test selection or a new --experiment directory."
        )
    if len(saved) > len(problem_ids):
        raise ValueError(
            f"Existing experiment already tracks {len(saved)} task(s), but "
            f"--num-problems selected only {len(problem_ids)}."
        )
    return len(saved)


def completed_problem_ids(experiment: Path, problem_ids: list[str]) -> set[str]:
    """Read durable scored completions from both checkpoint and final results."""
    selected = set(problem_ids)
    completed: set[str] = set()
    round_dir = experiment / "runs" / "round_1"
    checkpoint_path = round_dir / "evaluation_checkpoint.json"
    if checkpoint_path.is_file():
        checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        for problem_id, repetitions in checkpoint.get("completed", {}).items():
            if problem_id not in selected or not isinstance(repetitions, dict):
                continue
            if "1" in repetitions or repetitions.get("problem_id") == problem_id:
                completed.add(problem_id)

    result_path = round_dir / "result.json"
    if result_path.is_file():
        result = json.loads(result_path.read_text(encoding="utf-8"))
        for item in result.get("problem_results", []):
            if isinstance(item, dict) and item.get("problem_id") in selected:
                completed.add(item["problem_id"])
    return completed


def finalized_problem_ids(experiment: Path, problem_ids: list[str]) -> set[str]:
    """Return tasks already present in the aggregate result file."""
    result_path = experiment / "runs" / "round_1" / "result.json"
    if not result_path.is_file():
        return set()
    selected = set(problem_ids)
    result = json.loads(result_path.read_text(encoding="utf-8"))
    return {
        item["problem_id"]
        for item in result.get("problem_results", [])
        if isinstance(item, dict) and item.get("problem_id") in selected
    }


def cumulative_batch_ends(total: int, completed_prefix: int) -> list[int]:
    if completed_prefix >= total:
        return [total]
    starts_with_recovery = completed_prefix > 0 and completed_prefix % BATCH_SIZE != 0
    ends = [completed_prefix] if starts_with_recovery else []
    next_end = max(BATCH_SIZE, completed_prefix + BATCH_SIZE)
    while next_end < total:
        ends.append(next_end)
        next_end += BATCH_SIZE
    ends.append(total)
    return [end for end in ends if end > 0]


def main() -> int:
    args = parse_args()
    problem_ids = selected_task_ids(args.num_problems)
    if len(problem_ids) != len(set(problem_ids)):
        raise ValueError("Selected datasets contain duplicate task IDs")

    experiment = args.experiment
    if experiment is None:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        experiment = (
            REPO_ROOT / "openclaw_experiments" / f"{EXPERIMENT_PREFIX}{stamp}"
        )
    elif not experiment.is_absolute():
        experiment = REPO_ROOT / experiment
    experiment = experiment.resolve()
    print(f"Experiment: {experiment}", flush=True)
    tracked_prefix = existing_problem_count(experiment, problem_ids)
    completed_ids = completed_problem_ids(experiment, problem_ids)
    finalized_ids = finalized_problem_ids(experiment, problem_ids)
    tracked_ids = set(problem_ids[:tracked_prefix])
    tracked_has_unfinished = bool(tracked_ids - completed_ids)
    result_is_complete = set(problem_ids) <= finalized_ids
    if (
        tracked_prefix >= len(problem_ids)
        and not tracked_has_unfinished
        and result_is_complete
    ):
        batch_ends = []
    else:
        batch_ends = cumulative_batch_ends(len(problem_ids), tracked_prefix)
        if tracked_has_unfinished and tracked_prefix not in batch_ends:
            batch_ends.insert(0, tracked_prefix)
    if completed_ids:
        print(
            f"Resume state: {len(completed_ids)}/{len(problem_ids)} task(s) "
            "already scored; completed tasks will be skipped.",
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
            "-m", "src.OpenClaw.run_substantive_interaction_strategy_clean_baseline",
            "--exp", str(experiment),
            "--max-rounds", "1",
            "--model", args.model,
            "--thinking", args.thinking,
            "--timeout", str(args.timeout),
            "--concurrency", concurrency,
            "--retry-concurrency", concurrency,
            "--judge-concurrency", concurrency,
            "--validation-repetitions", "1",
            "--judge-repeats", "1",
            "--problem-id", *cumulative_problem_ids,
        ]
        if args.openclaw_command:
            command.extend(["--openclaw-command", args.openclaw_command])
        if args.initialize_only:
            command.append("--initialize-only")

        print(
            f"Batch {batch_index}/{len(batch_ends)}: "
            f"tasks 1-{end}; new/unfinished window <= {current_batch_size}; "
            f"concurrency: {concurrency}",
            flush=True,
        )
        result = subprocess.run(command, cwd=REPO_ROOT)
        if result.returncode:
            print(
                f'Clean baseline failed with exit code {result.returncode}. '
                f'Resume with the same options and --experiment "{experiment}".',
                file=sys.stderr,
            )
            return result.returncode
        if not args.initialize_only:
            completed_ids.update(cumulative_problem_ids)

    report_root = experiment / "runs" / "round_1"
    print(f"Baseline report root: {report_root}")
    if args.initialize_only:
        print("Initialization only: reports have not been generated.")
    else:
        print(f"Final scores: {report_root / 'result.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
