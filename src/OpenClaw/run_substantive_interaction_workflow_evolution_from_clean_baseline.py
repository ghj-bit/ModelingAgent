"""Run CPE-style workflow evolution over clean-baseline draft reports."""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

try:
    from . import run_substantive_interaction_workflow_evolution as workflow
    from . import run_substantive_interaction_strategy_clean_baseline as clean_baseline
except ImportError:
    import run_substantive_interaction_workflow_evolution as workflow
    import run_substantive_interaction_strategy_clean_baseline as clean_baseline


REPO_ROOT = Path(__file__).resolve().parents[2]
TRAIN_CLEAN_BASELINE_EXPERIMENT = (
    REPO_ROOT
    / "openclaw_experiments"
    / "interaction_strategy_clean_baseline_train_20260915_151525"
)
VALIDATION_CLEAN_BASELINE_EXPERIMENT = (
    REPO_ROOT
    / "openclaw_experiments"
    / "interaction_strategy_clean_baseline_val_20260915_154420"
)
TRAIN_CLEAN_BASELINE_ROUND_ROOT = (
    TRAIN_CLEAN_BASELINE_EXPERIMENT / "runs" / "round_1"
)
VALIDATION_CLEAN_BASELINE_ROUND_ROOT = (
    VALIDATION_CLEAN_BASELINE_EXPERIMENT / "runs" / "round_1"
)
TRAIN_PROBLEMS = (
    "2001_Adolescent_Pregnancy",
    "2001_Forest_Service",
    "2001_Skyscrapers",
    "2001_The_Bicycle_Wheel",
    "2002_School_Busing",
)
VALIDATION_PROBLEMS = (
    "2002_Airline_Overbooking",
    "2003_Gamma_Knife_Treatment",
    "2006_A_South_Sea",
)
TRAIN_PROBLEM_SET = frozenset(TRAIN_PROBLEMS)
VALIDATION_PROBLEM_SET = frozenset(VALIDATION_PROBLEMS)

_active_experiment: Path | None = None
_original_prepare_refinement = (
    workflow.substantive.prepare_refinement_validation_problem
)
_original_runtime_args = workflow.substantive.runtime_args
_original_parse_args = workflow.parse_args


def source_experiment_from_report_root(report_root: Path) -> Path:
    report_root = Path(report_root).resolve()
    if report_root.parent.name == "runs":
        return report_root.parent.parent
    return report_root


def load_current_clean_baseline_split(_path: Path) -> tuple[list[str], list[str]]:
    """Use exactly the tasks already completed in the two source experiments."""
    return list(TRAIN_PROBLEMS), list(VALIDATION_PROBLEMS)


def clean_baseline_report_root(problem_id: str, fallback: Path) -> Path:
    """Route each CPE split to its dedicated clean-baseline experiment."""
    if problem_id in TRAIN_PROBLEM_SET:
        return TRAIN_CLEAN_BASELINE_ROUND_ROOT
    if problem_id in VALIDATION_PROBLEM_SET:
        return VALIDATION_CLEAN_BASELINE_ROUND_ROOT
    return Path(fallback)


def clean_baseline_split(problem_id: str) -> str:
    if problem_id in TRAIN_PROBLEM_SET:
        return "train"
    if problem_id in VALIDATION_PROBLEM_SET:
        return "validation"
    return "unspecified"


def clean_baseline_report_matches_problem(problem_id: str, report: Path) -> bool:
    """Reject cached drafts from the wrong train/validation source experiment."""
    expected_root = clean_baseline_report_root(problem_id, report.parent)
    try:
        Path(report).resolve().relative_to(expected_root.resolve())
    except ValueError:
        return False
    metadata_path = Path(report).resolve().parents[2] / "meta" / "run.json"
    metadata = workflow.workflow_evolution.read_json(metadata_path, {})
    return metadata.get("problem_id") == problem_id


def resolve_clean_baseline_report(problem_id: str, report_root: Path) -> Path:
    """Resolve a draft strictly from the clean experiment for its data split."""
    report_root = clean_baseline_report_root(problem_id, report_root)
    for report in sorted(
        Path(report_root).glob("*/output/results/solution_report.md")
    ):
        metadata_path = report.parents[2] / "meta" / "run.json"
        if not metadata_path.is_file():
            continue
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if metadata.get("problem_id") == problem_id:
            return report
    return _resolve_flat_clean_baseline_report(problem_id, report_root)


def _resolve_flat_clean_baseline_report(problem_id: str, report_root: Path) -> Path:
    candidates = [
        path
        for path in Path(report_root).glob(
            f"{problem_id}_*/output/results/solution_report.md"
        )
        if path.is_file()
        and path.read_text(encoding="utf-8", errors="replace").strip()
    ]
    if not candidates:
        raise FileNotFoundError(
            f"No clean-baseline draft found for {problem_id} under {report_root}"
        )
    return max(candidates, key=lambda path: (path.stat().st_mtime_ns, str(path)))


def prepare_refinement_from_clean_baseline(*args, **kwargs) -> dict:
    """Install the draft with the shared refiner and identify it in run metadata."""
    prepared = _original_prepare_refinement(*args, **kwargs)
    metadata_path = Path(prepared["run_dir"]) / "meta" / "run.json"
    metadata = workflow.workflow_evolution.read_json(metadata_path, {})
    source_report = Path(metadata["baseline_report_source"])
    source_experiment = source_experiment_from_report_root(source_report.parents[3])
    metadata.update(
        {
            "initial_draft_used": True,
            "initial_draft_source_experiment": str(
                source_experiment
            ),
            "initial_draft_source_round": 1,
            "initial_draft_split": clean_baseline_split(
                str(metadata.get("problem_id", ""))
            ),
            "pipeline_agent_start": True,
        }
    )
    workflow.workflow_evolution.write_json(metadata_path, metadata)
    return prepared


def runtime_args_with_immediate_agent_start(*args, **kwargs):
    """Start each Agent immediately and enforce a bootstrap-free task workspace."""
    run_args = _original_runtime_args(*args, **kwargs)
    run_args.pipeline_agent_start = True
    run_args.require_clean_task_workspace = True
    return run_args


def parse_args_with_current_pool_defaults():
    """Default each workflow node to one worker per task in its largest phase."""
    args = _original_parse_args()

    def supplied(option: str) -> bool:
        return any(
            value == option or value.startswith(option + "=")
            for value in sys.argv[1:]
        )

    phase_concurrency = max(args.train_batch_size, len(VALIDATION_PROBLEMS))
    if not supplied("--validation-size"):
        args.validation_size = len(VALIDATION_PROBLEMS)
    if not supplied("--concurrency"):
        args.concurrency = phase_concurrency
    if not supplied("--retry-concurrency"):
        args.retry_concurrency = phase_concurrency
    if not supplied("--judge-concurrency"):
        args.judge_concurrency = phase_concurrency
    return args


def experiment_path(value: str | None) -> tuple[Path, bool]:
    """Use a distinct default directory name while preserving --exp resume support."""
    global _active_experiment
    if value:
        path = Path(value).resolve()
        _active_experiment = path
        return path, path.is_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = (
        REPO_ROOT
        / "openclaw_experiments"
        / f"interaction_workflow_clean_baseline_refinement_{timestamp}"
    )
    _active_experiment = path
    return path, False


def record_initial_draft_config() -> None:
    if _active_experiment is None:
        return
    config_path = _active_experiment / "config.json"
    if not config_path.is_file():
        return
    config = workflow.workflow_evolution.read_json(config_path, {})
    config.update(
        {
            "initial_draft_used": True,
            "initial_draft_source_experiments": {
                "train": str(TRAIN_CLEAN_BASELINE_EXPERIMENT.resolve()),
                "validation": str(
                    VALIDATION_CLEAN_BASELINE_EXPERIMENT.resolve()
                ),
            },
            "initial_draft_report_roots": {
                "train": str(TRAIN_CLEAN_BASELINE_ROUND_ROOT.resolve()),
                "validation": str(
                    VALIDATION_CLEAN_BASELINE_ROUND_ROOT.resolve()
                ),
            },
            "initial_draft_source_round": 1,
            "training_initial_drafts": "sampled_round_batch_only",
            "validation_initial_drafts": "complete_current_validation_pool",
            "pipeline_agent_start": True,
            "agent_start_policy": "run_immediately_after_own_registration",
            "agent_registration_policy": "serialized_shared_config_mutation",
            "isolated_openclaw_config": True,
            "openclaw_bootstrap_suppressed_before_agent_registration": True,
            "workspace_root_entries": ["code", "data", "results", "logs"],
        }
    )
    cpe = config.get("cpe")
    if isinstance(cpe, dict):
        cpe["split_file"] = None
        cpe["split_source"] = "completed_clean_baseline_experiment_tasks"
        cpe["train_pool"] = list(TRAIN_PROBLEMS)
        cpe["validation_pool"] = list(VALIDATION_PROBLEMS)
        cpe["validation_size"] = len(VALIDATION_PROBLEMS)
        cpe["validation_problems"] = list(VALIDATION_PROBLEMS)
    config.pop("initial_draft_source_experiment", None)
    workflow.workflow_evolution.write_json(config_path, config)


def main() -> None:
    workflow.load_cpe_split = load_current_clean_baseline_split
    workflow.parse_args = parse_args_with_current_pool_defaults
    workflow.substantive.BASELINE_REPORT_ROOT = TRAIN_CLEAN_BASELINE_ROUND_ROOT
    workflow.substantive.DEFAULT_PROBLEMS = tuple(VALIDATION_PROBLEMS)
    workflow.substantive.resolve_baseline_report = resolve_clean_baseline_report
    workflow.substantive.baseline_report_matches_problem = (
        clean_baseline_report_matches_problem
    )
    workflow.substantive.prepare_refinement_validation_problem = (
        prepare_refinement_from_clean_baseline
    )
    workflow.substantive.runtime_args = runtime_args_with_immediate_agent_start
    workflow.experiment_path = experiment_path
    isolated_config = None
    previous_config = None
    try:
        if "--initialize-only" not in sys.argv[1:]:
            isolated_config, previous_config = (
                clean_baseline.activate_clean_openclaw_config()
            )
        workflow.main(cpe_mode=True, compact_experiment_inputs=True)
    finally:
        record_initial_draft_config()
        if isolated_config is not None:
            clean_baseline.remove_clean_openclaw_config(
                isolated_config, previous_config
            )


if __name__ == "__main__":
    main()
