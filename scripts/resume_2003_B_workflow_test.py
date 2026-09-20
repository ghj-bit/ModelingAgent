"""Resume an interrupted MM-Bench ``2003_B`` fixed-interaction-policy test.

Resume the experiment the runner already created instead of starting over, so
completed work is reused and only the unfinished problems are re-evaluated:

    python scripts/resume_2003_B_workflow_test.py
    python scripts/resume_2003_B_workflow_test.py --exp <experiment directory>

``--exp`` accepts either the runner's experiment directory or the CPE evaluation
directory inside it:

    .../interaction_workflow_initial_draft_test_20260918_213109
    .../interaction_workflow_initial_draft_test_20260918_213109/cpe_evaluations/round_0/selected_test_workflow

Without ``--exp`` the newest ``interaction_workflow_initial_draft_test_*``
experiment is resumed. The runner's checkpoint records which problems completed,
so a resumed run replays only the failures.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.OpenClaw import run_substantive_interaction_workflow_test_from_initial_draft as runner

PROBLEM_ID = "2003_B"
EXPERIMENT_GLOB = "interaction_workflow_initial_draft_test_*"
CPE_MARKER = ("cpe_evaluations",)


def resolve_experiment(value: Path | None) -> Path:
    """Accept the runner's experiment dir or the CPE evaluation dir inside it."""
    if value is None:
        candidates = sorted(
            (REPO_ROOT / "openclaw_experiments").glob(EXPERIMENT_GLOB),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        if not candidates:
            raise SystemExit(
                "No experiment matching "
                f"openclaw_experiments/{EXPERIMENT_GLOB} was found; "
                "pass --exp explicitly."
            )
        return candidates[0]

    path = value if value.is_absolute() else REPO_ROOT / value
    path = path.resolve()
    if not path.is_dir():
        raise SystemExit(f"Experiment directory does not exist: {path}")
    # Walk back out of a CPE evaluation directory to the runner's experiment.
    parts = path.parts
    for marker in CPE_MARKER:
        if marker in parts:
            return Path(*parts[: parts.index(marker)])
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--exp", "--experiment", type=Path,
        help="Experiment to resume; defaults to the newest one.",
    )
    known, forwarded = parser.parse_known_args()

    experiment = resolve_experiment(known.exp)
    checkpoint = (
        experiment / "cpe_evaluations" / "round_0" / "selected_test_workflow"
        / "workflows" / "round_0" / "evaluation_checkpoint.json"
    )
    saved = runner.workflow.workflow_evolution.read_json(checkpoint, {})
    completed = saved.get("completed", {})
    failed = saved.get("failed", {})
    print(f"Resuming: {experiment}", flush=True)
    print(f"Checkpoint: {checkpoint}", flush=True)
    print(
        f"Completed in checkpoint: {sorted(completed) or 'none'}; "
        f"failed: {sorted(failed) or 'none'}",
        flush=True,
    )

    command = [
        sys.executable,
        "-m",
        "src.OpenClaw.run_substantive_interaction_workflow_test_from_initial_draft",
        "--benchmark",
        "mmbench",
        "--problem-id",
        PROBLEM_ID,
        "--planning-draft-test-root",
        *[str(root) for root in runner.DEFAULT_PLANNING_DRAFT_ROOTS],
        "--exp",
        str(experiment),
        *forwarded,
    ]
    print("Command: " + subprocess.list2cmdline(command), flush=True)
    return subprocess.run(command, cwd=REPO_ROOT).returncode


if __name__ == "__main__":
    raise SystemExit(main())
