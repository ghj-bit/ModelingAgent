"""Generate clean-baseline drafts for the requested number of training tasks.

Usage:
    python scripts/run_clean_baseline_train.py
    python scripts/run_clean_baseline_train.py --num-problems 40
    python scripts/run_clean_baseline_train.py --initialize-only

Relative experiment paths are resolved from the repository root.
Workspace preparation creates no interaction log subdirectories and does not
copy output/code/wait_for_expert_reply.py.
The experiment root contains only runs; configuration and checkpoints live there.
Each Agent begins execution immediately after its own registration completes.
Without --experiment, the latest experiment with the same tasks and model is
resumed automatically; pass a new explicit path to start another experiment.
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
EXPERIMENT_PREFIX = "interaction_strategy_clean_baseline_train_"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="deepseek/deepseek-v4-flash")
    parser.add_argument("--thinking", default="high")
    parser.add_argument("--timeout", type=int, default=7200)
    parser.add_argument(
        "--num-problems",
        type=int,
        default=DEFAULT_NUM_PROBLEMS,
        help="Number of tasks selected from the start of the training set (default: 5)",
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
    path = REPO_ROOT / "data" / "modeling_data_train.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not payload:
        raise ValueError(f"Dataset must be a non-empty task mapping: {path}")
    if num_problems > len(payload):
        raise ValueError(
            f"--num-problems={num_problems} exceeds the {len(payload)} training tasks"
        )
    return list(payload)[:num_problems]


def latest_matching_experiment(problem_ids: list[str], model: str) -> Path | None:
    """Find the newest checkpoint-compatible experiment for automatic resume."""
    experiment_root = REPO_ROOT / "openclaw_experiments"
    if not experiment_root.is_dir():
        return None
    candidates = sorted(
        (
            path
            for path in experiment_root.glob(EXPERIMENT_PREFIX + "*")
            if path.is_dir()
        ),
        key=lambda path: path.name,
        reverse=True,
    )
    for experiment in candidates:
        config_path = experiment / "runs" / "config.json"
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if (
            config.get("experiment_type")
            == "substantive_interaction_strategy_clean_baseline"
            and config.get("validation_problems") == problem_ids
            and config.get("model") == model
            and int(config.get("validation_repetitions", 1)) == 1
        ):
            return experiment
    return None


def main() -> int:
    args = parse_args()
    problem_ids = selected_task_ids(args.num_problems)
    if len(problem_ids) != len(set(problem_ids)):
        raise ValueError("Selected datasets contain duplicate task IDs")

    experiment = args.experiment
    if experiment is None:
        experiment = latest_matching_experiment(problem_ids, args.model)
        if experiment is None:
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            experiment = (
                REPO_ROOT / "openclaw_experiments"
                / f"{EXPERIMENT_PREFIX}{stamp}"
            )
        else:
            print(f"Resuming matching experiment: {experiment}", flush=True)
    elif not experiment.is_absolute():
        experiment = REPO_ROOT / experiment
    experiment = experiment.resolve()
    concurrency = str(len(problem_ids))
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
        "--problem-id", *problem_ids,
    ]
    if args.openclaw_command:
        command.extend(["--openclaw-command", args.openclaw_command])
    if args.initialize_only:
        command.append("--initialize-only")

    print(f"Tasks: {concurrency}; concurrency: {concurrency}", flush=True)
    print(f"Experiment: {experiment}", flush=True)
    result = subprocess.run(command, cwd=REPO_ROOT)
    if result.returncode:
        print(
            f'Clean baseline failed with exit code {result.returncode}. '
            f'Resume with the same options and --experiment "{experiment}".',
            file=sys.stderr,
        )
        return result.returncode

    report_root = experiment / "runs" / "round_1"
    print(f"Baseline report root: {report_root}")
    if args.initialize_only:
        print("Initialization only: reports have not been generated.")
    else:
        print(f"Final scores: {report_root / 'result.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
