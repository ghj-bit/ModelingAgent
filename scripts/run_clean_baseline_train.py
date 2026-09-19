"""Generate clean-baseline reports or planning drafts for training tasks.

Usage:
    python scripts/run_clean_baseline_train.py
    python scripts/run_clean_baseline_train.py --num-problems 40
    python scripts/run_clean_baseline_train.py --all-problems --initial-draft
    python scripts/run_clean_baseline_train.py --benchmark mmbench --problem-id 2003_C
    python scripts/run_clean_baseline_train.py --initialize-only

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
EXPERIMENT_PREFIX = "interaction_strategy_clean_baseline_train_"
MMBENCH_EXPERIMENT_PREFIX = "interaction_strategy_clean_baseline_mmbench_"
DEFAULT_MMBENCH_ROOT = Path(r"D:\vscode_project\LLM-MM-Agent\MMBench")
SUPPORTED_MMBENCH_PROBLEMS = ("2003_C", "2003_B")
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
    parser.add_argument(
        "--benchmark",
        choices=("modelingbench", "mmbench"),
        default="modelingbench",
        help="Problem/data/evaluation source (default: modelingbench).",
    )
    parser.add_argument(
        "--mmbench-root",
        type=Path,
        default=DEFAULT_MMBENCH_ROOT,
        help=f"MM-Bench root (default: {DEFAULT_MMBENCH_ROOT}).",
    )
    parser.add_argument(
        "--problem-id",
        nargs="+",
        help=(
            "MM-Bench problem IDs; the enabled set is "
            + ", ".join(SUPPORTED_MMBENCH_PROBLEMS)
            + " (default: all of them)."
        ),
    )
    parser.add_argument("--model", default="deepseek/deepseek-v4-flash")
    parser.add_argument("--thinking", default="high")
    parser.add_argument("--timeout", type=int, default=7200)
    parser.add_argument(
        "--num-problems",
        type=int,
        default=DEFAULT_NUM_PROBLEMS,
        help="Number of tasks selected from the start of the training set (default: 5)",
    )
    parser.add_argument(
        "--all-problems",
        action="store_true",
        help="Select the complete training dataset, overriding --num-problems.",
    )
    parser.add_argument("--experiment", "--exp", type=Path)
    parser.add_argument("--concurrency", type=int)
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    parser.add_argument("--openclaw-command")
    parser.add_argument("--mmbench-judge-model", default="deepseek-v4-flash")
    parser.add_argument("--mmbench-judge-api-key")
    parser.add_argument("--mmbench-judge-base-url")
    parser.add_argument("--mmbench-judge-timeout", type=float, default=600.0)
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
    if args.batch_size < 1:
        parser.error("--batch-size must be positive")
    if args.mmbench_judge_timeout <= 0:
        parser.error("--mmbench-judge-timeout must be positive")
    if args.benchmark == "modelingbench" and args.problem_id:
        parser.error("--problem-id is currently available only with --benchmark mmbench")
    if args.benchmark == "mmbench" and args.initial_draft:
        parser.error("--initial-draft is not supported by this MMBench report runner")
    if args.benchmark == "mmbench" and args.all_problems:
        parser.error(
            "--all-problems is unavailable while the MMBench integration is "
            "pinned to " + ", ".join(SUPPORTED_MMBENCH_PROBLEMS)
        )
    return args


def selected_task_ids(
    num_problems: int,
    all_problems: bool = False,
    benchmark: str = "modelingbench",
    requested: list[str] | None = None,
) -> list[str]:
    if benchmark == "mmbench":
        problem_ids = list(requested or SUPPORTED_MMBENCH_PROBLEMS)
        unsupported = [
            problem_id
            for problem_id in problem_ids
            if problem_id not in SUPPORTED_MMBENCH_PROBLEMS
        ]
        if unsupported:
            raise ValueError(
                "MM-Bench support is currently pinned to "
                + ", ".join(SUPPORTED_MMBENCH_PROBLEMS)
                + "; got: "
                + ", ".join(unsupported)
            )
        return problem_ids
    path = REPO_ROOT / "data" / "modeling_data_train.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not payload:
        raise ValueError(f"Dataset must be a non-empty task mapping: {path}")
    if all_problems:
        num_problems = len(payload)
    if num_problems > len(payload):
        raise ValueError(
            f"--num-problems={num_problems} exceeds the {len(payload)} training tasks"
        )
    return list(payload)[:num_problems]


def preserve_existing_problem_order(
    experiment: Path, problem_ids: list[str]
) -> list[str]:
    """Keep existing rXpN task positions stable when extending an experiment."""
    config_path = experiment / "runs" / "config.json"
    if not config_path.is_file():
        return problem_ids
    config = json.loads(config_path.read_text(encoding="utf-8"))
    saved = config.get("validation_problems")
    if not isinstance(saved, list) or not saved:
        return problem_ids
    missing = [problem_id for problem_id in saved if problem_id not in problem_ids]
    if missing:
        raise ValueError(
            "Existing experiment contains tasks outside the requested training "
            "selection: " + ", ".join(missing)
        )
    return [*saved, *(problem_id for problem_id in problem_ids if problem_id not in saved)]


def existing_config(experiment: Path) -> dict:
    config_path = experiment / "runs" / "config.json"
    if not config_path.is_file():
        return {}
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise ValueError(f"Expected a JSON object: {config_path}")
    return config


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
            "use the same training selection or a new --experiment directory."
        )
    if len(saved) > len(problem_ids):
        raise ValueError(
            f"Existing experiment already tracks {len(saved)} task(s), but "
            f"--num-problems selected only {len(problem_ids)}."
        )
    return len(saved)


def cumulative_batch_ends(
    total: int, completed_prefix: int, batch_size: int = BATCH_SIZE
) -> list[int]:
    if completed_prefix >= total:
        return [total]
    starts_with_recovery = completed_prefix > 0 and completed_prefix % batch_size != 0
    ends = [completed_prefix] if starts_with_recovery else []
    next_end = max(batch_size, completed_prefix + batch_size)
    while next_end < total:
        ends.append(next_end)
        next_end += batch_size
    ends.append(total)
    return [end for end in ends if end > 0]


def main() -> int:
    args = parse_args()
    problem_ids = selected_task_ids(
        args.num_problems,
        args.all_problems,
        args.benchmark,
        args.problem_id,
    )
    if len(problem_ids) != len(set(problem_ids)):
        raise ValueError("Selected datasets contain duplicate task IDs")

    experiment = args.experiment
    if experiment is None:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix = (
            "interaction_strategy_clean_baseline_initial_draft_train_"
            if args.initial_draft
            else MMBENCH_EXPERIMENT_PREFIX
            if args.benchmark == "mmbench"
            else EXPERIMENT_PREFIX
        )
        experiment = (
            REPO_ROOT / "openclaw_experiments"
            / f"{prefix}{stamp}"
        )
    elif not experiment.is_absolute():
        experiment = REPO_ROOT / experiment
    experiment = experiment.resolve()
    problem_ids = preserve_existing_problem_order(experiment, problem_ids)
    config = existing_config(experiment)
    runner, initial_draft = select_runner(config, args.initial_draft)
    print(f"Experiment: {experiment}", flush=True)
    completed_prefix = existing_problem_count(experiment, problem_ids)
    batch_ends = cumulative_batch_ends(
        len(problem_ids), completed_prefix, args.batch_size
    )
    for batch_index, end in enumerate(batch_ends, 1):
        previous_end = batch_ends[batch_index - 2] if batch_index > 1 else min(
            completed_prefix, end
        )
        current_batch_size = max(1, end - previous_end)
        concurrency = str(
            args.concurrency
            or int(config.get("concurrency", 0))
            or min(args.batch_size, current_batch_size)
        )
        cumulative_problem_ids = problem_ids[:end]
        command = [
            sys.executable,
            "-m", runner,
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
        if not initial_draft:
            command.extend(["--benchmark", args.benchmark])
        if args.benchmark == "mmbench":
            command.extend(
                [
                    "--mmbench-root",
                    str(args.mmbench_root.resolve()),
                    "--mmbench-judge-model",
                    args.mmbench_judge_model,
                    "--mmbench-judge-timeout",
                    str(args.mmbench_judge_timeout),
                ]
            )
            if args.mmbench_judge_api_key:
                command.extend(
                    ["--mmbench-judge-api-key", args.mmbench_judge_api_key]
                )
            if args.mmbench_judge_base_url:
                command.extend(
                    ["--mmbench-judge-base-url", args.mmbench_judge_base_url]
                )
        if args.openclaw_command:
            command.extend(["--openclaw-command", args.openclaw_command])
        if args.initialize_only:
            command.append("--initialize-only")

        print(
            f"Batch {batch_index}/{len(batch_ends)}: "
            f"tasks 1-{end}; new/unfinished window <= {current_batch_size}; "
            f"concurrency: {concurrency}; "
            f"mode: {'initial draft' if initial_draft else 'completed report'}",
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

    report_root = experiment / "runs" / "round_1"
    print(f"Baseline report root: {report_root}")
    if args.initialize_only:
        print("Initialization only: reports have not been generated.")
    else:
        print(f"Final scores: {report_root / 'result.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
