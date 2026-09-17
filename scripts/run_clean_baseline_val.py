"""Generate clean-baseline reports or planning drafts for validation tasks.

Usage:
    python scripts/run_clean_baseline_val.py
    python scripts/run_clean_baseline_val.py --all-problems --initial-draft
    python scripts/run_clean_baseline_val.py --initialize-only

Relative experiment paths are resolved from the repository root. The designated
experiment is resumed when supplied with --experiment. Completed reports are
reused by the selected runner.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_NUM_PROBLEMS = 3
EXPERIMENT_PREFIX = "interaction_strategy_clean_baseline_val_"
STANDARD_RUNNER = "src.OpenClaw.run_substantive_interaction_strategy_clean_baseline"
INITIAL_DRAFT_RUNNER = (
    "src.OpenClaw.run_substantive_interaction_strategy_clean_baseline_initial_draft"
)
STANDARD_EXPERIMENT_TYPE = "substantive_interaction_strategy_clean_baseline"
INITIAL_DRAFT_EXPERIMENT_TYPE = (
    "substantive_interaction_strategy_clean_baseline_initial_draft"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="deepseek/deepseek-v4-flash")
    parser.add_argument("--thinking", default="high")
    parser.add_argument("--timeout", type=int, default=7200)
    parser.add_argument(
        "--num-problems",
        type=int,
        default=DEFAULT_NUM_PROBLEMS,
        help="Number of tasks selected from the start of the validation set (default: 3)",
    )
    parser.add_argument(
        "--all-problems",
        action="store_true",
        help="Select the complete validation dataset, overriding --num-problems.",
    )
    parser.add_argument("--experiment", "--exp", type=Path)
    parser.add_argument("--concurrency", type=int)
    parser.add_argument("--openclaw-command")
    parser.add_argument(
        "--initial-draft",
        action="store_true",
        help="Use the planning-draft runner when creating or resuming an initial-draft experiment.",
    )
    parser.add_argument("--initialize-only", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.timeout <= 86400:
        parser.error("--timeout must be between 1 and 86400 seconds")
    if args.num_problems < 1:
        parser.error("--num-problems must be positive")
    if args.concurrency is not None and args.concurrency < 1:
        parser.error("--concurrency must be positive")
    return args


def selected_task_ids(num_problems: int, all_problems: bool = False) -> list[str]:
    path = REPO_ROOT / "data" / "modeling_data_validation.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not payload:
        raise ValueError(f"Dataset must be a non-empty task mapping: {path}")
    if all_problems:
        num_problems = len(payload)
    if num_problems > len(payload):
        raise ValueError(
            f"--num-problems={num_problems} exceeds the "
            f"{len(payload)} validation tasks"
        )
    return list(payload)[:num_problems]


def existing_config(experiment: Path) -> dict:
    config_path = experiment / "runs" / "config.json"
    if not config_path.is_file():
        return {}
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise ValueError(f"Expected a JSON object: {config_path}")
    return config


def preserve_existing_problem_order(
    config: dict, problem_ids: list[str]
) -> list[str]:
    saved = config.get("validation_problems")
    if not isinstance(saved, list) or not saved:
        return problem_ids
    missing = [problem_id for problem_id in saved if problem_id not in problem_ids]
    if missing:
        raise ValueError(
            "Existing experiment contains tasks outside the requested validation "
            "selection: " + ", ".join(missing)
        )
    return [*saved, *(problem_id for problem_id in problem_ids if problem_id not in saved)]


def select_runner(config: dict, initial_draft: bool) -> tuple[str, bool]:
    experiment_type = config.get("experiment_type")
    if experiment_type == INITIAL_DRAFT_EXPERIMENT_TYPE:
        return INITIAL_DRAFT_RUNNER, True
    if experiment_type == STANDARD_EXPERIMENT_TYPE:
        if initial_draft:
            raise ValueError(
                "--initial-draft cannot be used with an existing standard-report experiment"
            )
        return STANDARD_RUNNER, False
    if experiment_type is not None:
        raise ValueError(f"Unsupported experiment_type: {experiment_type!r}")
    return (INITIAL_DRAFT_RUNNER, True) if initial_draft else (STANDARD_RUNNER, False)


def main() -> int:
    args = parse_args()
    experiment = args.experiment
    if experiment is None:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix = (
            "interaction_strategy_clean_baseline_initial_draft_val_"
            if args.initial_draft
            else EXPERIMENT_PREFIX
        )
        experiment = REPO_ROOT / "openclaw_experiments" / f"{prefix}{stamp}"
    elif not experiment.is_absolute():
        experiment = REPO_ROOT / experiment
    experiment = experiment.resolve()

    config = existing_config(experiment)
    problem_ids = preserve_existing_problem_order(
        config, selected_task_ids(args.num_problems, args.all_problems)
    )
    if len(problem_ids) != len(set(problem_ids)):
        raise ValueError("Selected validation tasks contain duplicate IDs")
    runner, initial_draft = select_runner(config, args.initial_draft)
    concurrency = str(
        args.concurrency
        or int(config.get("concurrency", 0))
        or len(problem_ids)
    )
    command = [
        sys.executable,
        "-m",
        runner,
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

    mode = "initial draft" if initial_draft else "completed report"
    print(f"Mode: {mode}", flush=True)
    print("Validation tasks: " + ", ".join(problem_ids), flush=True)
    print(f"Tasks: {len(problem_ids)}; concurrency: {concurrency}", flush=True)
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
