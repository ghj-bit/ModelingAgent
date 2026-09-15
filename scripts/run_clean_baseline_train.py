"""Generate clean-baseline drafts for five fixed training tasks.

Usage:
    python scripts/run_clean_baseline_train.py
    python scripts/run_clean_baseline_train.py --initialize-only

Relative experiment paths are resolved from the repository root.
Workspace preparation creates no interaction log subdirectories and does not
copy output/code/wait_for_expert_reply.py.
The experiment root contains only runs; configuration and checkpoints live there.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SELECTED_PROBLEM_IDS = (
    "2001_Adolescent_Pregnancy",
    "2001_Forest_Service",
    "2001_Skyscrapers",
    "2001_The_Bicycle_Wheel",
    "2002_School_Busing",
)
EXCLUDED_PROBLEM_IDS = {
    "2003_Aviation_Baggage_Screening",
    "2013_Bank_Service_Problem",
    "2025_Managing_Sustainable_Tourism",
}


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
    path = REPO_ROOT / "data" / "modeling_data_train.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not payload:
        raise ValueError(f"Dataset must be a non-empty task mapping: {path}")
    missing = [problem_id for problem_id in SELECTED_PROBLEM_IDS if problem_id not in payload]
    if missing:
        raise ValueError("Selected tasks are missing from the training set: " + ", ".join(missing))
    if len(SELECTED_PROBLEM_IDS) != 5 or set(SELECTED_PROBLEM_IDS) & EXCLUDED_PROBLEM_IDS:
        raise ValueError("The fixed selection must contain five tasks and no excluded task")
    return list(SELECTED_PROBLEM_IDS)


def main() -> int:
    args = parse_args()
    problem_ids = selected_task_ids()
    if len(problem_ids) != len(set(problem_ids)):
        raise ValueError("Selected datasets contain duplicate task IDs")

    experiment = args.experiment
    if experiment is None:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        experiment = (
            REPO_ROOT / "openclaw_experiments"
            / f"interaction_strategy_clean_baseline_train_{stamp}"
        )
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
