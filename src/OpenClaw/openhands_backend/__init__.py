"""OpenHands solver backend for the interaction-workflow evolution launcher.

The engine binds ``interaction.run_local_modeling_phase`` to
``substantive.run_substantive_modeling_phase``, an OpenClaw CLI invocation, at
``run_substantive_interaction_workflow_evolution.py:3704``.  That binding is the
single seam that decides which executable runs a solver, what prompt it is fed,
and what artifact marks it complete, so replacing it with an OpenHands
conversation swaps the agent framework without touching the rest of the
pipeline: the file-based expert bridge, the MM-Bench judge, the acceptance
gates, the CPE phase concurrency and the pipelined register-then-run workers all
keep working unchanged.

The copy of the launcher that uses this backend patches
``substantive.run_substantive_modeling_phase`` (not ``interaction.*``) before
calling ``workflow.main()``, because the engine re-assigns the latter from the
former while starting up and would otherwise overwrite the patch.

Agent registration is answered by ``registry_stub.py``, passed through the
framework's existing ``--openclaw-command`` option.
"""

from __future__ import annotations

import os
from pathlib import Path

try:
    from .. import baseline
    from .. import record_refinement_changes
    from .. import run_evolution as workflow_evolution
    from .. import run_substantive_interaction_experiment as substantive
except ImportError:  # pragma: no cover - flat imports when run as a script tree
    import baseline
    import record_refinement_changes
    import run_evolution as workflow_evolution
    import run_substantive_interaction_experiment as substantive


BACKEND_DIR = Path(__file__).resolve().parent
REGISTRY_STUB = BACKEND_DIR / "registry_stub.py"
TASK_DRIVER = BACKEND_DIR / "run_openhands_task.py"

# Cluster defaults: the local vLLM endpoint that serves the solver model.  Each
# value is overridable per run through an environment variable, so the backend
# works on another node without editing this file.
DEFAULT_OPENHANDS_PYTHON = "/public1/home/stu52275901007/anaconda3/envs/openhands/bin/python"
DEFAULT_MODEL = "qwen3.8-27b"
DEFAULT_BASE_URL = "http://gpu6:18763/v1"
DEFAULT_API_KEY = "EMPTY"
# Terminal silence tolerance, chosen above the expert bridge's 180s wait.
DEFAULT_NO_CHANGE_TIMEOUT = "1800"
# Per-request model-call timeout, kept well above the endpoint's queueing delay
# under a fully parallel phase.
DEFAULT_LLM_TIMEOUT = "1800"
# Concurrent tool calls per agent step, i.e. how many sub-agents one solver may
# fan out to.  Matches the sub-agent delegation the OpenClaw launcher enables.
DEFAULT_SUBAGENT_CONCURRENCY = "6"


def setting(name: str, default: str) -> str:
    """Resolve one backend setting from ``OPENHANDS_<NAME>``, then the default."""
    return os.environ.get(f"OPENHANDS_{name.upper()}") or default


def default_settings() -> dict[str, str]:
    """The backend attributes a run should carry, for config recording."""
    return {
        "openhands_python": setting("python", DEFAULT_OPENHANDS_PYTHON),
        "openhands_model": setting("model", DEFAULT_MODEL),
        "openhands_base_url": setting("base_url", DEFAULT_BASE_URL),
        "openhands_api_key": setting("api_key", DEFAULT_API_KEY),
        "openhands_no_change_timeout": setting(
            "no_change_timeout", DEFAULT_NO_CHANGE_TIMEOUT
        ),
        "openhands_llm_timeout": setting("llm_timeout", DEFAULT_LLM_TIMEOUT),
        "openhands_subagent_concurrency": setting(
            "subagent_concurrency", DEFAULT_SUBAGENT_CONCURRENCY
        ),
    }


def openhands_command(prepared: dict, args, message_file: Path) -> list[str]:
    """Command that runs one OpenHands conversation for this task."""
    resolved = default_settings()
    return [
        getattr(args, "openhands_python", None) or resolved["openhands_python"],
        str(TASK_DRIVER),
        "--prompt-file",
        str(message_file),
        # The task workspace is ``output/`` inside the run directory -- the same
        # root the framework registers with OpenClaw and asserts is clean before
        # a run.  Every path the prompt hands the agent (code/, data/, results/,
        # logs/) lives under it.
        "--workspace",
        str(prepared["output_dir"]),
        # Conversation transcripts live beside the run's other meta files rather
        # than inside the task workspace, which the framework keeps clean.
        "--persistence-dir",
        str(prepared["run_dir"] / "meta" / "openhands"),
        "--model",
        getattr(args, "openhands_model", None) or resolved["openhands_model"],
        "--base-url",
        getattr(args, "openhands_base_url", None) or resolved["openhands_base_url"],
        "--api-key",
        getattr(args, "openhands_api_key", None) or resolved["openhands_api_key"],
        "--timeout",
        str(getattr(args, "timeout", 7200)),
        # Long enough that the expert-bridge wait and long computations read as
        # "still running" instead of tripping the terminal's soft timeout.
        "--no-change-timeout",
        str(getattr(args, "openhands_no_change_timeout", None) or resolved["openhands_no_change_timeout"]),
        "--llm-timeout",
        str(getattr(args, "openhands_llm_timeout", None) or resolved["openhands_llm_timeout"]),
        "--subagent-concurrency",
        str(
            getattr(args, "openhands_subagent_concurrency", None)
            or resolved["openhands_subagent_concurrency"]
        ),
        # The framework's own thinking level for the solver, translated for the
        # local model by the driver.
        "--thinking",
        str(getattr(args, "thinking", "off")),
    ]


def submission_path(prepared: dict) -> Path:
    """The machine-readable container the solver is told to produce."""
    return Path(prepared["output_dir"]) / "results" / "solution.json"


def synthesize_report_from_submission(
    prepared: dict, backend_name: str = "the solver backend"
) -> Path | None:
    """Render the Markdown report the harness insists on, from the submission.

    The solver prompt makes ``results/solution.json`` the submission and tells
    the agent not to spend its time on a second, unscored Markdown write-up --
    for a long problem that duplication ran to tens of minutes.  The harness,
    however, still treats ``results/solution_report.md`` as the run's completion
    artifact and several of its gates require that file to exist, be non-empty,
    and differ from the planning draft.

    Rendering it here from the container satisfies all of those without the
    agent paying for the same content twice, and without editing the shared
    engine.  The text is assembled from the container's own fields, so the two
    cannot disagree.

    Each backend passes its own name so the rendered file records which one
    produced it; the function is shared, so it cannot infer that itself.
    """
    submission = submission_path(prepared)
    # Hardcoded rather than read from prepared["final_report"]: launchers that
    # make the container the completion artifact point that field at
    # solution.json, and rendering onto it would replace the machine-readable
    # submission with the Markdown derived from it -- which then fails every
    # gate that reads the container, and the report is never written at all.
    report = Path(prepared["output_dir"]) / "results" / "solution_report.md"
    if not submission.is_file():
        return None
    try:
        container = workflow_evolution.read_json(submission, {})
    except (OSError, ValueError):
        return None
    tasks = container.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        return None

    # Field order mirrors the container's own schema, so the rendered report
    # reads in the order the subtasks were answered.
    sections = (
        ("task_description", "Problem"),
        ("task_analysis", "Analysis"),
        ("preliminary_formulas", "Preliminary Formulas"),
        ("mathematical_modeling_process", "Modeling Process"),
        ("task_code", "Code"),
        ("execution_result", "Execution Result"),
        ("solution_interpretation", "Interpretation"),
        ("subtask_outcome_analysis", "Outcome Analysis"),
    )
    lines = ["# Solution", ""]
    for index, task in enumerate(tasks, start=1):
        if not isinstance(task, dict):
            continue
        title = str(task.get("task_description", "")).strip().splitlines()
        heading = title[0][:120] if title else f"Subtask {index}"
        lines.extend([f"## Subtask {index}: {heading}", ""])
        for key, label in sections:
            value = str(task.get(key, "")).strip()
            if not value:
                continue
            lines.extend([f"### {label}", "", value, ""])
    lines.extend(
        [
            "---",
            "",
            f"_Rendered by {backend_name} from `{submission.name}`; "
            "the JSON container is the submission of record._",
            "",
        ]
    )
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines), encoding="utf-8")
    print(
        f"Rendered {report.name} from {submission.name} "
        f"({len(tasks)} subtask(s)); the solver was not asked to write a report.",
        flush=True,
    )
    return report


def run_openhands_modeling_phase(
    prepared: dict,
    session_id: str,
    message_file: Path,
    args,
    completion_artifact: Path | None,
    check_interaction: bool = True,
) -> None:
    """Run one OpenHands solver and verify the artifacts the pipeline requires.

    Mirrors ``run_substantive_modeling_phase``: stream the run into
    ``meta/solve.log``, resume once when the deliverable is missing, then hand
    off to the shared post-run bookkeeping.

    The deliverable is ``results/solution.json`` rather than the harness's
    ``results/solution_report.md``: the prompt names the container as the
    submission and tells the agent not to duplicate it as Markdown, so waiting
    on the report would wait for a file nobody is going to write.  The report is
    rendered from the container afterwards, before the engine's own checks run.
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
            "agent_backend": "openhands",
            "solve_log": str(solve_log),
            "transport_log": str(transport_log),
        }
    )
    workflow_evolution.write_json(metadata_path, metadata)

    # What the agent is actually asked to produce.  ``completion_artifact`` (the
    # harness's report path) is kept only as the fallback target in case the
    # prompt is run without the container section.
    deliverable = submission_path(prepared)

    def run_agent(current_message_file: Path) -> None:
        baseline.stream_command(
            openhands_command(prepared, args, current_message_file),
            prepared["run_dir"],
            transport_log,
            completion_artifact=deliverable,
        )

    def artifact_ready() -> bool:
        try:
            return bool(
                deliverable.is_file()
                and deliverable.read_text(encoding="utf-8").strip()
            )
        except (OSError, UnicodeDecodeError):
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
                "OpenHands exited before writing the submission; resuming once "
                "to complete it.",
                flush=True,
            )
            run_agent(recovery_prompt)
    finally:
        # OpenHands writes its own conversation logs; there is no OpenClaw
        # session transcript to render into meta/solve.log.
        pass
    if not artifact_ready():
        raise RuntimeError(
            "OpenHands did not produce the required non-empty submission "
            f"after one recovery attempt: {deliverable}"
        )
    # Everything below runs the engine's own gates, several of which still read
    # ``results/solution_report.md``; render it from the container before they
    # do, so the agent is never asked to write the same content twice.
    if synthesize_report_from_submission(prepared, "the OpenHands backend") is None:
        raise RuntimeError(
            "Submission is present but could not be rendered into the report the "
            f"harness requires: {deliverable}"
        )
    if not check_interaction:
        # No-interaction baseline: there is no dialogue to account for and no
        # interaction gate to clear, so the post-run bookkeeping that reads the
        # expert exchange is skipped rather than made to tolerate its absence.
        return
    # Both of these are launcher-patched module globals on ``substantive``, so
    # they are resolved through the module rather than imported directly.
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
    "default_settings",
    "openhands_command",
    "run_openhands_modeling_phase",
    "submission_path",
    "synthesize_report_from_submission",
    "setting",
]
