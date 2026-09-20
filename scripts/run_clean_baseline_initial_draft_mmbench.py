"""Generate planning ``draft.md`` files for native MM-Bench dataset tasks.

The experiment is written under this repository's ``openclaw_experiments``
directory by default.  Native problem definitions are read without mutation;
only files from ``MMBench/dataset/<problem_id>`` are staged in each Agent
workspace.  The resulting experiment can be passed directly to
``run_substantive_interaction_workflow_test_from_initial_draft.py`` through
``--planning-draft-test-root``.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.OpenClaw import (  # noqa: E402
    run_substantive_interaction_strategy_clean_baseline_initial_draft as draft,
)
from src.OpenClaw import (  # noqa: E402
    run_substantive_interaction_workflow_test_from_initial_draft as solver,
)


DEFAULT_MMBENCH_ROOT = Path(r"D:\vscode_project\LLM-MM-Agent\MMBench")
MMBENCH_PLANNER_PROMPT = (
    REPO_ROOT / "src" / "OpenClaw" / "prompts" / "mmbench_planner_prompt.md"
)
EXPERIMENT_PREFIX = "interaction_strategy_clean_baseline_initial_draft_mmbench_"
EXPERIMENT_TYPE = (
    "substantive_interaction_strategy_clean_baseline_initial_draft_mmbench"
)
DEFAULT_CONCURRENCY = 5


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mmbench-root",
        type=Path,
        default=DEFAULT_MMBENCH_ROOT,
        help=f"MM-Bench root (default: {DEFAULT_MMBENCH_ROOT})",
    )
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument(
        "--problem-id",
        nargs="+",
        help=(
            "MM-Bench problem IDs. Every selected ID must be defined under "
            "MMBench/problem; a dataset directory is staged when one exists. "
            "Default: all dataset task directories."
        ),
    )
    selection.add_argument(
        "--num-problems",
        type=int,
        help="Select only the first N sorted MM-Bench dataset task IDs.",
    )
    parser.add_argument("--experiment", "--exp", type=Path)
    parser.add_argument("--model", default="deepseek/deepseek-v4-flash")
    parser.add_argument("--thinking", default="high")
    parser.add_argument("--timeout", type=int, default=7200)
    parser.add_argument("--completion-grace", type=float, default=60.0)
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY)
    parser.add_argument("--validation-attempts", type=int, default=3)
    parser.add_argument("--validation-retry-delay", type=float, default=10.0)
    parser.add_argument("--openclaw-command")
    parser.add_argument("--initialize-only", action="store_true")
    args = parser.parse_args()
    if args.num_problems is not None and args.num_problems < 1:
        parser.error("--num-problems must be positive")
    if not 1 <= args.timeout <= 86400:
        parser.error("--timeout must be between 1 and 86400 seconds")
    if args.completion_grace <= 0:
        parser.error("--completion-grace must be positive")
    if args.concurrency < 1:
        parser.error("--concurrency must be positive")
    if args.validation_attempts < 1:
        parser.error("--validation-attempts must be positive")
    if args.validation_retry_delay < 0:
        parser.error("--validation-retry-delay must be non-negative")
    return args


def experiment_path(value: Path | None) -> Path:
    if value is not None:
        return value.resolve() if value.is_absolute() else (REPO_ROOT / value).resolve()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return REPO_ROOT / "openclaw_experiments" / f"{EXPERIMENT_PREFIX}{stamp}"


def stage_mmbench_dataset(
    mmbench_root: Path, base_prepare_run, *args, **kwargs
):
    """Run the standard preparation and copy only the selected dataset tree."""
    run_dir, output_dir, prompt_path = base_prepare_run(*args, **kwargs)
    if args:
        problem_id = str(args[0])
    elif "problem_id" in kwargs:
        problem_id = str(kwargs["problem_id"])
    else:
        raise RuntimeError("Initial-draft preparation did not provide a problem ID")
    source_root = mmbench_root / "dataset" / problem_id
    if source_root.is_dir():
        data_dir = Path(output_dir) / "data"
        for source in sorted(source_root.rglob("*")):
            target = data_dir / source.relative_to(source_root)
            if source.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            elif source.is_file():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
    else:
        # Native tasks such as 2003_B ship no dataset directory.
        print(
            f"MM-Bench problem {problem_id} declares no dataset; staging nothing.",
            flush=True,
        )

    metadata_path = Path(run_dir) / "meta" / "run.json"
    metadata = draft.baseline.strategy.workflow_evolution.read_json(metadata_path, {})
    metadata.update(
        {
            "benchmark": "mmbench",
            "mmbench_problem_file": str(
                (mmbench_root / "problem" / f"{problem_id}.json").resolve()
            ),
            "mmbench_dataset_source": (
                str(source_root.resolve()) if source_root.is_dir() else ""
            ),
        }
    )
    draft.baseline.strategy.workflow_evolution.write_json(metadata_path, metadata)
    return run_dir, output_dir, prompt_path


def mmbench_planner_prompt(strategy: dict) -> str:
    """Keep the existing planner contract while identifying the native benchmark."""
    del strategy
    return MMBENCH_PLANNER_PROMPT.read_text(encoding="utf-8")


def forward_arguments(args: argparse.Namespace, problem_ids: list[str], experiment: Path) -> list[str]:
    forwarded = [
        str(Path(__file__).resolve()),
        "--exp",
        str(experiment),
        "--max-rounds",
        "1",
        "--problem-id",
        *problem_ids,
        "--model",
        args.model,
        "--thinking",
        args.thinking,
        "--timeout",
        str(args.timeout),
        "--completion-grace",
        str(args.completion_grace),
        "--concurrency",
        str(min(args.concurrency, len(problem_ids))),
        "--retry-concurrency",
        str(min(args.concurrency, len(problem_ids))),
        "--judge-concurrency",
        str(min(args.concurrency, len(problem_ids))),
        "--validation-repetitions",
        "1",
        "--judge-repeats",
        "1",
        "--validation-attempts",
        str(args.validation_attempts),
        "--validation-retry-delay",
        str(args.validation_retry_delay),
    ]
    if args.openclaw_command:
        forwarded.extend(["--openclaw-command", args.openclaw_command])
    if args.initialize_only:
        forwarded.append("--initialize-only")
    return forwarded


def record_mmbench_config(
    experiment: Path, mmbench_root: Path, problem_ids: list[str]
) -> None:
    config_path = experiment / "runs" / "config.json"
    if not config_path.is_file():
        return
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config.update(
        {
            "benchmark": "mmbench",
            "mmbench_root": str(mmbench_root),
            "mmbench_problem_source": str(mmbench_root / "problem"),
            "mmbench_dataset_source": str(mmbench_root / "dataset"),
            "validation_problems": problem_ids,
        }
    )
    draft.baseline.strategy.workflow_evolution.write_json(config_path, config)


def main() -> int:
    args = parse_args()
    mmbench_root = args.mmbench_root.resolve()
    problems, available_ids = solver.load_mmbench_problems(mmbench_root, None)
    if args.problem_id:
        problems, problem_ids = solver.load_mmbench_problems(
            mmbench_root, args.problem_id
        )
    elif args.num_problems is not None:
        problem_ids = available_ids[: args.num_problems]
        if len(problem_ids) != args.num_problems:
            raise ValueError(
                f"--num-problems={args.num_problems} exceeds the "
                f"{len(available_ids)} MM-Bench dataset tasks"
            )
        problems = {problem_id: problems[problem_id] for problem_id in problem_ids}
    else:
        problem_ids = available_ids
    experiment = experiment_path(args.experiment)

    original_argv = sys.argv
    original_loader = draft.baseline.strategy.baseline.load_problems
    original_prepare = draft._BASE_PREPARE_RUN
    original_prompt = draft.build_initial_draft_prompt
    original_type = draft.EXPERIMENT_TYPE
    original_prefix = draft.EXPERIMENT_PREFIX
    try:
        sys.argv = forward_arguments(args, problem_ids, experiment)
        draft.baseline.strategy.baseline.load_problems = lambda: problems
        draft._BASE_PREPARE_RUN = lambda *positional, **keywords: stage_mmbench_dataset(
            mmbench_root, original_prepare, *positional, **keywords
        )
        draft.build_initial_draft_prompt = mmbench_planner_prompt
        draft.EXPERIMENT_TYPE = EXPERIMENT_TYPE
        draft.EXPERIMENT_PREFIX = EXPERIMENT_PREFIX.rstrip("_")
        print(f"Experiment: {experiment}", flush=True)
        print(
            f"MM-Bench draft tasks: {len(problem_ids)}; "
            f"concurrency: {min(args.concurrency, len(problem_ids))}",
            flush=True,
        )
        draft.main()
        record_mmbench_config(experiment, mmbench_root, problem_ids)
    finally:
        sys.argv = original_argv
        draft.baseline.strategy.baseline.load_problems = original_loader
        draft._BASE_PREPARE_RUN = original_prepare
        draft.build_initial_draft_prompt = original_prompt
        draft.EXPERIMENT_TYPE = original_type
        draft.EXPERIMENT_PREFIX = original_prefix

    print(f"Planning-draft experiment ready: {experiment}", flush=True)
    print(
        "Use it with --planning-draft-test-root " + str(experiment),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
