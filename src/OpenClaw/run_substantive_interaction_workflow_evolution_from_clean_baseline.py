"""Evolve interaction workflows by refining the clean-baseline draft reports."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

try:
    from . import run_substantive_interaction_workflow_evolution as workflow
except ImportError:
    import run_substantive_interaction_workflow_evolution as workflow


REPO_ROOT = Path(__file__).resolve().parents[2]
CLEAN_BASELINE_EXPERIMENT = (
    REPO_ROOT
    / "openclaw_experiments"
    / "interaction_strategy_clean_baseline_20260912_202248"
)
CLEAN_BASELINE_ROUND_ROOT = CLEAN_BASELINE_EXPERIMENT / "runs" / "round_1"
CLEAN_BASELINE_PROBLEMS = (
    "2025_Managing_Sustainable_Tourism",
    "2003_Aviation_Baggage_Screening",
)

_active_experiment: Path | None = None
_original_prepare_refinement = (
    workflow.substantive.prepare_refinement_validation_problem
)


def resolve_clean_baseline_report(problem_id: str, report_root: Path) -> Path:
    """Resolve a clean-baseline report through its run metadata."""
    for report in sorted(
        Path(report_root).glob("*/output/results/solution_report.md")
    ):
        metadata_path = report.parents[2] / "meta" / "run.json"
        if not metadata_path.is_file():
            continue
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if metadata.get("problem_id") == problem_id:
            return report
    raise FileNotFoundError(
        f"No clean-baseline draft found for {problem_id} under {report_root}"
    )


def prepare_refinement_from_clean_baseline(*args, **kwargs) -> dict:
    """Install the draft with the shared refiner and identify it in run metadata."""
    prepared = _original_prepare_refinement(*args, **kwargs)
    metadata_path = Path(prepared["run_dir"]) / "meta" / "run.json"
    metadata = workflow.workflow_evolution.read_json(metadata_path, {})
    metadata.update(
        {
            "initial_draft_used": True,
            "initial_draft_source_experiment": str(
                CLEAN_BASELINE_EXPERIMENT.resolve()
            ),
            "initial_draft_source_round": 1,
        }
    )
    workflow.workflow_evolution.write_json(metadata_path, metadata)
    return prepared


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
            "initial_draft_source_experiment": str(
                CLEAN_BASELINE_EXPERIMENT.resolve()
            ),
            "initial_draft_source_round": 1,
        }
    )
    workflow.workflow_evolution.write_json(config_path, config)


def main() -> None:
    workflow.substantive.BASELINE_REPORT_ROOT = CLEAN_BASELINE_ROUND_ROOT
    workflow.substantive.DEFAULT_PROBLEMS = CLEAN_BASELINE_PROBLEMS
    workflow.substantive.resolve_baseline_report = resolve_clean_baseline_report
    workflow.substantive.prepare_refinement_validation_problem = (
        prepare_refinement_from_clean_baseline
    )
    workflow.experiment_path = experiment_path
    try:
        workflow.main()
    finally:
        record_initial_draft_config()


if __name__ == "__main__":
    main()
