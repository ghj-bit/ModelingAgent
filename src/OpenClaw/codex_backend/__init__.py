"""Codex CLI backend for the substantive interaction workflow evolution.

The workflow engine is shared with the Claude arm.  This backend only replaces
the solver process: it runs ``codex exec`` in the prepared task workspace and
keeps the same submission, report-rendering, expert-interaction, and recovery
contracts as the Claude backend.
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
    from ..openhands_backend import (
        REGISTRY_STUB,
        submission_path,
        synthesize_report_from_submission,
    )
except ImportError:  # pragma: no cover
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
TASK_DRIVER = BACKEND_DIR / "run_codex_task.py"
DEFAULT_CODEX_PYTHON = "/public1/home/stu52275901007/anaconda3/envs/math_modeling/bin/python"
DEFAULT_CODEX_BIN = "/public1/home/stu52275901007/.local/bin/codex"
DEFAULT_MODEL = "qwen3.8-27b"
DEFAULT_BASE_URL = "http://gpu6:18763/v1"
DEFAULT_API_KEY = "EMPTY"


def setting(name: str, default: str) -> str:
    return os.environ.get(f"CODEX_{name.upper()}") or default


def default_settings() -> dict[str, str]:
    """Return run metadata keys retained for compatibility with the engine."""
    return {
        "claude_python": setting("python", DEFAULT_CODEX_PYTHON),
        "claude_bin": setting("bin", DEFAULT_CODEX_BIN),
        "claude_model": setting("model", DEFAULT_MODEL),
        "claude_base_url": setting("base_url", DEFAULT_BASE_URL),
        "claude_api_key": setting("api_key", DEFAULT_API_KEY),
        "claude_allowed_tools": "codex_exec",
        "codex_reasoning_effort": setting("reasoning_effort", "low"),
        "codex_model_verbosity": "low",
    }


def codex_command(prepared: dict, args, message_file: Path) -> list[str]:
    resolved = default_settings()
    run_dir = Path(prepared["run_dir"])
    return [
        resolved["claude_python"],
        str(TASK_DRIVER),
        "--prompt-file",
        str(message_file),
        "--workspace",
        str(prepared["output_dir"]),
        "--persistence-dir",
        str(run_dir / "meta" / "codex"),
        "--model",
        resolved["claude_model"],
        "--base-url",
        resolved["claude_base_url"],
        "--api-key",
        resolved["claude_api_key"],
        "--codex-bin",
        resolved["claude_bin"],
        "--timeout",
        str(getattr(args, "timeout", 7200)),
        "--reasoning-effort",
        resolved["codex_reasoning_effort"],
    ]


def codex_log_dir(prepared: dict) -> Path:
    """Return the per-run directory that stores Codex execution logs."""
    path = Path(prepared["run_dir"]) / "meta" / "codex_logs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def run_codex_modeling_phase(
    prepared: dict,
    session_id: str,
    message_file: Path,
    args,
    completion_artifact: Path | None,
    check_interaction: bool = True,
) -> None:
    """Run Codex once, then perform the same single recovery as Claude."""
    meta_dir = Path(prepared["run_dir"]) / "meta"
    meta_dir.mkdir(parents=True, exist_ok=True)
    transport_log = meta_dir / "transport.log"
    codex_logs = codex_log_dir(prepared)
    stdout_log = codex_logs / "codex.stdout.log"
    stderr_log = codex_logs / "codex.stderr.log"
    metadata_path = meta_dir / "run.json"
    metadata = workflow_evolution.read_json(metadata_path, {})
    metadata.update(
        {
            "session_id": session_id,
            "agent_backend": "codex",
            "reasoning_effort": setting("reasoning_effort", "low"),
            "solve_log": str(meta_dir / "solve.log"),
            "transport_log": str(transport_log),
            "codex_log_dir": str(codex_logs),
            "codex_stdout_log": str(stdout_log),
            "codex_stderr_log": str(stderr_log),
        }
    )
    workflow_evolution.write_json(metadata_path, metadata)

    deliverable = submission_path(prepared)

    def run_agent(current_message_file: Path) -> None:
        baseline.stream_command(
            codex_command(prepared, args, current_message_file),
            prepared["run_dir"],
            transport_log,
            completion_artifact=deliverable,
        )

    def artifact_ready() -> bool:
        try:
            return deliverable.is_file() and isinstance(
                json.loads(deliverable.read_text(encoding="utf-8")), dict
            )
        except (OSError, UnicodeDecodeError, ValueError):
            return False

    run_agent(message_file)
    if not artifact_ready():
        recovery_prompt = meta_dir / "final_report_recovery_prompt.md"
        recovery_prompt.write_text(
            "# Submission recovery\n\n"
            "Resume the existing work in this same workspace. Do not restart "
            "completed analysis or request another expert interaction. Write the "
            "complete JSON solution container to this exact path:\n\n"
            f"`{deliverable}`\n\n"
            "Use exactly the four task fields required by the prompt and ensure "
            "the file parses as strict JSON before ending.\n",
            encoding="utf-8",
        )
        run_agent(recovery_prompt)

    if not artifact_ready():
        raise RuntimeError(
            "Codex did not produce the required solution container after one "
            f"recovery attempt: {deliverable}"
        )
    if synthesize_report_from_submission(prepared, "the Codex backend") is None:
        raise RuntimeError(
            "Codex submission could not be rendered into the required report: "
            f"{deliverable}"
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


# The existing Claude-oriented launcher asks for this attribute by name.  The
# alias lets the from-scratch wrapper swap the backend without changing the
# shared workflow engine.
run_claude_modeling_phase = run_codex_modeling_phase


__all__ = [
    "REGISTRY_STUB",
    "TASK_DRIVER",
    "codex_command",
    "default_settings",
    "run_codex_modeling_phase",
    "run_claude_modeling_phase",
    "setting",
    "submission_path",
    "synthesize_report_from_submission",
]
