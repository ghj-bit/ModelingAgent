"""Generate clean-baseline drafts for three fixed validation tasks.

Usage:
    python scripts/run_clean_baseline_val.py
    python scripts/run_clean_baseline_val.py --initialize-only

Relative experiment paths are resolved from the repository root. The three
tasks run concurrently, and the designated experiment is resumed by default.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXPERIMENT = (
    REPO_ROOT
    / "openclaw_experiments"
    / "interaction_strategy_clean_baseline_val_20260915_154420"
)
SELECTED_PROBLEM_IDS = (
    "2002_Airline_Overbooking",
    "2003_Gamma_Knife_Treatment",
    "2006_A_South_Sea",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="deepseek/deepseek-v4-flash")
    parser.add_argument("--thinking", default="high")
    parser.add_argument("--timeout", type=int, default=7200)
    parser.add_argument("--experiment", "--exp", type=Path)
    parser.add_argument("--openclaw-command")
    parser.add_argument("--initialize-only", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.timeout <= 86400:
        parser.error("--timeout must be between 1 and 86400 seconds")
    return args


def selected_task_ids() -> list[str]:
    path = REPO_ROOT / "data" / "modeling_data_validation.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not payload:
        raise ValueError(f"Dataset must be a non-empty task mapping: {path}")
    missing = [
        problem_id
        for problem_id in SELECTED_PROBLEM_IDS
        if problem_id not in payload
    ]
    if missing:
        raise ValueError(
            "Selected tasks are missing from the validation set: "
            + ", ".join(missing)
        )
    return list(SELECTED_PROBLEM_IDS)


def main() -> int:
    args = parse_args()
    problem_ids = selected_task_ids()
    if len(problem_ids) != len(set(problem_ids)):
        raise ValueError("Selected validation tasks contain duplicate IDs")

    experiment = args.experiment
    if experiment is None:
        experiment = DEFAULT_EXPERIMENT
    elif not experiment.is_absolute():
        experiment = REPO_ROOT / experiment
    experiment = experiment.resolve()

    concurrency = str(len(problem_ids))
    command = [
        sys.executable,
        "-m",
        "src.OpenClaw.run_substantive_interaction_strategy_clean_baseline",
        "--exp",
        str(experiment),
        "--max-rounds",
        "1",
        "--model",
        args.model,
        "--thinking",
        args.thinking,
        "--timeout",
        str(args.timeout),
        "--concurrency",
        concurrency,
        "--retry-concurrency",
        concurrency,
        "--judge-concurrency",
        concurrency,
        "--validation-repetitions",
        "1",
        "--judge-repeats",
        "1",
        "--problem-id",
        *problem_ids,
    ]
    if args.openclaw_command:
        command.extend(["--openclaw-command", args.openclaw_command])
    if args.initialize_only:
        command.append("--initialize-only")

    print("Validation tasks: " + ", ".join(problem_ids), flush=True)
    print(f"Tasks: {concurrency}; concurrency: {concurrency}", flush=True)
    print(f"Experiment: {experiment}", flush=True)
    result = subprocess.run(command, cwd=REPO_ROOT)
    if result.returncode:
        print(
            f"Clean validation baseline failed with exit code {result.returncode}. "
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
