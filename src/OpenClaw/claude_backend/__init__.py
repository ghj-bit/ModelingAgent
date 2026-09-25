"""Claude Code solver backend for the interaction-workflow evolution launcher.

This is the third runtime for the same pipeline, alongside the OpenClaw CLI and
OpenHands, and it hooks into exactly the same seam: the engine binds
``interaction.run_local_modeling_phase`` to
``substantive.run_substantive_modeling_phase`` while starting up, so a copy of
the launcher that rebinds ``substantive.run_substantive_modeling_phase`` swaps
the agent framework without disturbing the expert bridge, the MM-Bench judge,
the acceptance gates or the CPE phase concurrency.

Claude Code differs from the other two in that it cannot talk to the local model
at all without help -- it speaks the Anthropic Messages API, and the served
endpoint's Anthropic implementation cannot run this workload (see
``proxy.py``).  Each task therefore carries its own translation shim, started by
``run_claude_task.py`` on a free port.

Agent registration is answered by the OpenHands registry stub, which is a plain
executable and does not depend on either backend's runtime.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

try:
    from .. import baseline
    from .. import record_refinement_changes
    from .. import run_evolution as workflow_evolution
    from .. import run_substantive_interaction_experiment as substantive
    # Rendering the harness's report from the submission container is not
    # specific to any backend -- both here and in OpenHands the solver is told
    # that solution.json is the deliverable -- so it is shared rather than
    # copied, which keeps the two arms from drifting apart.  The registry stub
    # is likewise runtime-independent: it is a plain executable that answers the
    # framework's OpenClaw registry calls, and neither backend has a real one.
    from ..openhands_backend import (
        REGISTRY_STUB,
        submission_path,
        synthesize_report_from_submission,
    )
except ImportError:  # pragma: no cover - flat imports when run as a script tree
    import baseline
    import record_refinement_changes
    import run_evolution as workflow_evolution
    import run_substantive_interaction_experiment as substantive

    from openhands_backend import (
        REGISTRY_STUB,
        submission_path,
        synthesize_report_from_submission,
    )


BACKEND_DIR = Path(__file__).resolve().parent
TASK_DRIVER = BACKEND_DIR / "run_claude_task.py"

# The driver is standard-library only, so it runs under the same interpreter as
# the framework -- no separate environment is needed the way OpenHands needs
# one for its SDK.
DEFAULT_CLAUDE_PYTHON = "/public1/home/stu52275901007/anaconda3/envs/math_modeling/bin/python"
DEFAULT_CLAUDE_BIN = "/public1/home/stu52275901007/.local/bin/claude"
DEFAULT_MODEL = "qwen3.8-27b"
DEFAULT_BASE_URL = "http://gpu6:18763/v1"
DEFAULT_API_KEY = "EMPTY"
# Headless runs have nobody to answer a permission prompt, so the grant is an
# explicit list of the tools the prompt's workflow uses.
DEFAULT_ALLOWED_TOOLS = (
    "Bash,Read,Write,Edit,MultiEdit,Glob,Grep,LS,WebFetch,WebSearch,NotebookEdit,TodoWrite"
)


def setting(name: str, default: str) -> str:
    """Resolve one backend setting from ``CLAUDE_<NAME>``, then the default."""
    return os.environ.get(f"CLAUDE_{name.upper()}") or default


def default_settings() -> dict[str, str]:
    """The backend attributes a run should carry, for config recording."""
    return {
        "claude_python": setting("python", DEFAULT_CLAUDE_PYTHON),
        "claude_bin": setting("bin", DEFAULT_CLAUDE_BIN),
        "claude_model": setting("model", DEFAULT_MODEL),
        "claude_base_url": setting("base_url", DEFAULT_BASE_URL),
        "claude_api_key": setting("api_key", DEFAULT_API_KEY),
        "claude_allowed_tools": setting("allowed_tools", DEFAULT_ALLOWED_TOOLS),
    }


def claude_command(prepared: dict, args, message_file: Path) -> list[str]:
    """Command that runs one Claude Code session for this task."""
    resolved = default_settings()
    return [
        getattr(args, "claude_python", None) or resolved["claude_python"],
        str(TASK_DRIVER),
        "--prompt-file",
        str(message_file),
        # The task workspace is ``output/`` inside the run directory -- the same
        # root the framework registers with OpenClaw and asserts is clean before
        # a run.  Every path the prompt hands the agent lives under it.
        "--workspace",
        str(prepared["output_dir"]),
        # The shim log, the isolated Claude Code config and its session
        # transcripts live beside the run's other meta files rather than inside
        # the task workspace, which the framework keeps clean.
        "--persistence-dir",
        str(prepared["run_dir"] / "meta" / "claude"),
        "--model",
        getattr(args, "claude_model", None) or resolved["claude_model"],
        "--upstream-model",
        getattr(args, "claude_model", None) or resolved["claude_model"],
        "--base-url",
        getattr(args, "claude_base_url", None) or resolved["claude_base_url"],
        "--api-key",
        getattr(args, "claude_api_key", None) or resolved["claude_api_key"],
        "--claude-bin",
        getattr(args, "claude_bin", None) or resolved["claude_bin"],
        "--timeout",
        str(getattr(args, "timeout", 7200)),
        "--permission-mode",
        getattr(args, "claude_permission_mode", None) or "acceptEdits",
        "--allowed-tools",
        getattr(args, "claude_allowed_tools", None) or resolved["claude_allowed_tools"],
        # Accepted for interface parity and recorded in the run config.  The
        # shim turns the local model's thinking off unconditionally, because the
        # Anthropic shape offers no way to ask for it and a reasoning block
        # would otherwise consume the answer's token budget.
        "--thinking",
        str(getattr(args, "thinking", "off")),
    ]


def run_claude_modeling_phase(
    prepared: dict,
    session_id: str,
    message_file: Path,
    args,
    completion_artifact: Path | None,
    check_interaction: bool = True,
) -> None:
    """Run one Claude Code solver and verify the artifacts the pipeline requires.

    Mirrors ``run_openhands_modeling_phase``: stream the run into
    ``meta/solve.log``, resume once when the deliverable is missing, then hand
    off to the shared post-run bookkeeping.
    """
    meta_dir = prepared["run_dir"] / "meta"
    meta_dir.mkdir(parents=True, exist_ok=True)
    transport_log = meta_dir / "transport.log"
    solve_log = meta_dir / "solve.log"
    metadata_path = meta_dir / "run.json"
    metadata = workflow_evolution.read_json(metadata_path, {})
    metadata.update(
        {
            "session_id": session_id,
            "agent_backend": "claude",
            "solve_log": str(solve_log),
            "transport_log": str(transport_log),
        }
    )
    workflow_evolution.write_json(metadata_path, metadata)

    deliverable = submission_path(prepared)

    def run_agent(current_message_file: Path) -> None:
        baseline.stream_command(
            claude_command(prepared, args, current_message_file),
            prepared["run_dir"],
            transport_log,
            completion_artifact=deliverable,
        )

    def artifact_ready() -> bool:
        # Parsed, not merely non-empty: the deliverable is a machine-readable
        # container, and a solver that writes a report here instead would
        # otherwise be accepted and then fail every later gate that reads the
        # container -- with an error that points at the report, not at this.
        try:
            if not deliverable.is_file():
                return False
            return isinstance(json.loads(deliverable.read_text(encoding="utf-8")), dict)
        except (OSError, UnicodeDecodeError, ValueError):
            return False

    try:
        run_agent(message_file)
        if not artifact_ready():
            recovery_prompt = meta_dir / "final_report_recovery_prompt.md"
            recovery_prompt.write_text(
                "# Submission recovery\n\n"
                "The previous turn completed without creating the required "
                "submission. Resume the existing work in this same workspace. Do "
                "not restart completed analysis, repeat web research, or request "
                "another expert interaction. Inspect the existing draft, code, "
                "data, computed results, and expert feedback, then write the "
                "complete machine-readable solution container to this exact "
                "path:\n\n"
                f"`{deliverable}`\n\n"
                "One element in `tasks` per subproblem the problem statement asks "
                "about, with every field filled from the work already done. "
                "Answer every original task, include the assumptions, model, "
                "results, validation, and limitations, and do not generate "
                "images. Verify that the file exists, is non-empty, and parses as "
                "strict JSON before ending.\n",
                encoding="utf-8",
            )
            print(
                "Claude Code exited before writing the submission; resuming once "
                "to complete it.",
                flush=True,
            )
            run_agent(recovery_prompt)
    finally:
        # Claude Code keeps its own session transcripts under the isolated
        # config directory; there is no OpenClaw session transcript to render
        # into meta/solve.log.
        pass
    if not artifact_ready():
        raise RuntimeError(
            "Claude Code did not produce the required non-empty submission "
            f"after one recovery attempt: {deliverable}"
        )
    if synthesize_report_from_submission(prepared, "the Claude Code backend") is None:
        raise RuntimeError(
            "Submission is present but could not be rendered into the report the "
            f"harness requires: {deliverable}"
        )
    if not check_interaction:
        return
    substantive.write_interaction_added_content(prepared["run_dir"])
    output_dir = Path(prepared.get("output_dir", prepared["run_dir"] / "output"))
    manifest_path = output_dir / "results" / "baseline_workspace_manifest.json"
    if manifest_path.is_file():
        record_refinement_changes.write_changes(
            output_dir,
            manifest_path,
            output_dir / "results" / "refinement_changed_files.json",
        )
    substantive.run_consolidated_refinement_check(prepared)


__all__ = [
    "REGISTRY_STUB",
    "TASK_DRIVER",
    "claude_command",
    "default_settings",
    "run_claude_modeling_phase",
    "setting",
    "submission_path",
    "synthesize_report_from_submission",
]
