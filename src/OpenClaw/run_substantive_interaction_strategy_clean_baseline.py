"""Run a no-interaction baseline on ModelingBench or MM-Bench.

This variant reuses the execution and evaluation behavior of
``run_substantive_interaction_strategy_baseline.py`` while removing the staged
process-report contract and the additional report-integration instructions.
By default, run every task in data/modeling_data_train.json with one worker
per task. MM-Bench mode currently accepts only native task ``2003_C`` and uses
its unchanged problem definition, dataset directory, and native evaluator.
"""

from __future__ import annotations

import argparse
import atexit
import json
import os
import shutil
import sys
import tempfile
import uuid
from datetime import datetime
from functools import partial
from pathlib import Path

try:
    from . import claude_backend
    from . import openhands_backend
    from . import run_substantive_interaction_strategy_evolution as strategy
    from . import run_substantive_interaction_workflow_test_from_initial_draft as mmbench_support
except ImportError:
    import claude_backend
    import openhands_backend
    import run_substantive_interaction_strategy_evolution as strategy
    import run_substantive_interaction_workflow_test_from_initial_draft as mmbench_support


EXPERIMENT_TYPE = "substantive_interaction_strategy_clean_baseline"
EXPERIMENT_PREFIX = "interaction_strategy_clean_baseline"
TRAIN_DATASET = Path(__file__).resolve().parents[2] / "data" / "modeling_data_train.json"
DEFAULT_MMBENCH_ROOT = Path(r"D:\vscode_project\LLM-MM-Agent\MMBench")
SUPPORTED_MMBENCH_PROBLEMS = ("2003_C", "2003_B")

# ``openhands`` and ``claude`` modes run the same task the interactive arm does --
# same planning draft, same pre-gathered empirical data -- and differ only in the
# prompt: the expert-interaction section is removed and nothing replaces it.
# They differ from each other only in which executable solves the task, so every
# step that keys off "is this a draft-based backend" keys off this tuple rather
# than one name.  OpenClaw mode keeps the historic behaviour, which starts from
# the problem statement alone.
DRAFT_BACKENDS = ("openhands", "claude")
# The solver prompt carries the draft's location under this name.  Kept as a
# literal, matching the launchers, because this module imports them lazily.
DRAFT_PATH_PLACEHOLDER = "{{DRAFT_PATH}}"
_AGENT_BACKEND = "openclaw"
# Resolved once in main(): one planning draft per problem, by problem_id.  The
# values are strings, as resolve_planning_drafts returns them.
_DRAFT_REPORTS: dict[str, str] = {}
# Whether this run actually stages a planning draft.  DRAFT_BACKENDS names the
# backends that *can* use one; handed no --planning-draft-root they run the
# problem statement alone instead, which is the behaviour the openclaw backend
# has always had.  Set in main() from the parsed args, so a backend string alone
# never decides it.
_DRAFT_MODE = False
# Whether to take only each draft's evidence and not its proposed solution.  The
# solver then runs the problem statement plus data/external_data.md, which is the
# one thing the draft pool is uniquely good for and the one thing the solver
# cannot gather itself.  Set in main().
_REUSE_DRAFT_DATA = False

_ORIGINAL_PARSE_ARGS = strategy.parse_args
_ORIGINAL_VALIDATE_ARGS = strategy.validate_args
_ORIGINAL_RUNTIME_ARGS = strategy.runtime_args


def active_openclaw_config_path() -> Path:
    explicit = os.environ.get("OPENCLAW_CONFIG_PATH", "").strip()
    if explicit:
        return Path(explicit).expanduser().resolve()
    home_override = os.environ.get("OPENCLAW_HOME", "").strip()
    home = Path(home_override).expanduser() if home_override else Path.home()
    state_override = os.environ.get("OPENCLAW_STATE_DIR", "").strip()
    state_dirs = (
        [Path(state_override).expanduser()]
        if state_override
        else [home / ".openclaw", home / ".clawdbot"]
    )
    for state_dir in state_dirs:
        for filename in ("openclaw.json", "clawdbot.json"):
            candidate = state_dir / filename
            if candidate.is_file():
                return candidate.resolve()
    return (state_dirs[0] / "openclaw.json").resolve()


NESTED_AGENT_TOOL_DENY = ("sessions_spawn", "sessions_send", "subagents")


def activate_clean_openclaw_config(
    *, deny_nested_agents: bool = False
) -> tuple[Path, str | None]:
    """Use a private config with optional single-Agent execution enforcement."""
    source = active_openclaw_config_path()
    try:
        config = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise RuntimeError(f"Cannot read OpenClaw config: {source}") from error
    agents = config.setdefault("agents", {})
    agents.setdefault("defaults", {})["skipBootstrap"] = True
    agents["list"] = []
    if deny_nested_agents:
        tools = config.setdefault("tools", {})
        existing_deny = tools.get("deny") or []
        if not isinstance(existing_deny, list):
            raise RuntimeError("OpenClaw tools.deny must be a JSON list")
        tools["deny"] = list(
            dict.fromkeys([*existing_deny, *NESTED_AGENT_TOOL_DENY])
        )

    handle, filename = tempfile.mkstemp(prefix="modelingagent-clean-", suffix=".json")
    config_path = Path(filename)
    with os.fdopen(handle, "w", encoding="utf-8") as file:
        json.dump(config, file, ensure_ascii=False, indent=2)
        file.write("\n")
    os.chmod(config_path, 0o600)
    previous = os.environ.get("OPENCLAW_CONFIG_PATH")
    os.environ["OPENCLAW_CONFIG_PATH"] = str(config_path)
    return config_path, previous


def remove_clean_openclaw_config(path: Path, previous: str | None) -> None:
    if previous is None:
        os.environ.pop("OPENCLAW_CONFIG_PATH", None)
    else:
        os.environ["OPENCLAW_CONFIG_PATH"] = previous
    path.unlink(missing_ok=True)


def build_clean_baseline_prompt(
    _strategy: dict, benchmark: str = "modelingbench"
) -> str:
    """Return the no-interaction prompt without staged artifact requirements."""
    prompt = strategy.reference_baseline_prompt_template()

    current_data_step = (
        "4. Search only for external evidence necessary to support or validate "
        "high-impact factual assumptions, empirical parameters, or real-world "
        "mechanisms. Do not impose a fixed limit on the number of variables or "
        "sources, and do not perform searches that cannot affect the model, "
        "validation, or conclusion. Record each source and its intended use."
    )
    bounded_data_step = (
        "4. Search for at most 1-2 verifiable empirical data items that materially "
        "affect the model or validation, and record their sources and intended use."
    )
    if prompt.count(current_data_step) != 1:
        raise RuntimeError("Shared prompt has an unexpected data-search step")
    prompt = prompt.replace(current_data_step, bounded_data_step, 1)

    workflow_summary = "## Workflow Summary Contract\n"
    final_report_contract = "## Final Report Contract\n"
    if prompt.count(workflow_summary) > 1 or prompt.count(final_report_contract) != 1:
        raise RuntimeError("Shared prompt has an unexpected workflow/report layout")
    if workflow_summary in prompt:
        before_summary, remainder = prompt.split(workflow_summary, 1)
        _, final_report = remainder.split(final_report_contract, 1)
        prompt = before_summary.rstrip() + "\n\n" + final_report_contract + final_report

    report_method = (
        "Use equations, tables, numerical results, and citations where they materially "
        "support the solution."
    )
    text_only_report = "The final report must be text-only Markdown;"
    if prompt.count(report_method) != 1 or prompt.count(text_only_report) != 1:
        raise RuntimeError("Shared prompt has an unexpected final-report layout")
    before_extra, remainder = prompt.split(report_method, 1)
    _, after_extra = remainder.split(text_only_report, 1)
    prompt = (
        before_extra
        + report_method
        + "\n\n"
        + text_only_report
        + after_extra
    )

    prompt = prompt.replace(
        "Only `{{FINAL_REPORT}}` will be submitted to ModelingBench Judge. "
        "Intermediate files and your conversational reply will not be scored. "
        "Before finishing,",
        "Only `{{FINAL_REPORT}}` will be submitted to ModelingBench Judge. "
        "Before finishing,",
        1,
    )
    if benchmark == "mmbench":
        prompt = prompt.replace("# ModelingBench Task", "# MM-Bench Task", 1)
        prompt = prompt.replace("ModelingBench Judge", "MM-Bench Judge", 1)
        workspace_marker = (
            "Create these directories when needed. Use the problem statement "
            "above as the task definition."
        )
        mmbench_workspace = (
            "Create these directories when needed. Use the problem statement "
            "above as the task definition. Use only the native benchmark files staged "
            "in the Data directory as supplied task data, and do not alter the "
            "native problem requirements or dataset definitions."
        )
        if prompt.count(workspace_marker) != 1:
            raise RuntimeError("Shared prompt has an unexpected workspace section")
        prompt = prompt.replace(workspace_marker, mmbench_workspace, 1)
    return prompt


def build_solution_only_prompt(benchmark: str = "mmbench") -> str:
    """The draft-free prompt whose only deliverable is solution.json.

    Three deliberate differences from build_clean_baseline_prompt:

    1. No report contract.  The Claude backend already renders solution_report.md
       from solution.json (claude_backend.synthesize_report_from_submission), so a
       solver-written report is a file nothing reads -- asking for it only spends
       turns on prose the scored container has to repeat anyway.
    2. No data-search step.  The evidence is staged into the workspace from the
       draft pool, so searching would duplicate what is already on disk; the
       citation duty transfers to the supplied sources instead.
    3. An explicit stop.  The run is over once solution.json is complete.

    Unlike the draft arm this needs no substitute for {{DRAFT_PATH}}: the planning
    draft section is absent rather than pointed elsewhere.
    """
    prompt = build_clean_baseline_prompt({}, benchmark)

    final_report_line = "- Final report: `{{FINAL_REPORT}}`\n"
    search_step = (
        "4. Search for at most 1-2 verifiable empirical data items that materially "
        "affect the model or validation, and record their sources and intended use."
    )
    report_step = "7. Produce the final report at the required path.\n"
    staged_data_step = (
        "4. Use the empirical evidence already staged in the Data directory: read "
        "`data/external_data.md` first and treat it as the factual basis for the "
        "model, its validation, and its conclusions. It records the sources and "
        "the intended use of each. Do not search for other data -- everything "
        "this task is scored against is already provided."
    )
    for label, needle in (
        ("workspace report line", final_report_line),
        ("bounded data-search step", search_step),
        ("final-report workflow step", report_step),
    ):
        if prompt.count(needle) != 1:
            raise RuntimeError(f"Shared prompt has an unexpected {label}")
    prompt = prompt.replace(final_report_line, "", 1)
    prompt = prompt.replace(search_step, staged_data_step, 1)
    prompt = prompt.replace(report_step, "", 1)

    report_header = "## Final Report Contract\n"
    solution_header = "## MM-Bench Solution File\n"
    if prompt.count(report_header) != 1 or prompt.count(solution_header) != 1:
        raise RuntimeError("Shared prompt has an unexpected report/solution layout")
    before_report, remainder = prompt.split(report_header, 1)
    _, solution_section = remainder.split(solution_header, 1)
    prompt = before_report.rstrip() + "\n\n" + solution_header + solution_section

    report_intro = (
        "When the task is an MM-Bench problem, the Markdown report is not the "
        "complete\nsubmission. Also write the machine-readable solution container "
        "that MM-Bench\nJudge reads:"
    )
    solution_intro = (
        "Write the machine-readable solution container that MM-Bench Judge reads:"
    )
    report_consistency = (
        "The solution file must state the same models, numbers,\n"
        "and conclusions as the report."
    )
    solution_consistency = (
        "State the models, the numbers, and the conclusions in full here: this "
        "file is\nthe only thing that is submitted."
    )
    for label, needle in (
        ("solution-file introduction", report_intro),
        ("solution/report consistency sentence", report_consistency),
    ):
        if prompt.count(needle) != 1:
            raise RuntimeError(f"Shared prompt has an unexpected {label}")
    prompt = prompt.replace(report_intro, solution_intro, 1)
    prompt = prompt.replace(report_consistency, solution_consistency, 1)

    closing = "Start immediately and do not ask the user follow-up questions."
    stop_instruction = (
        "Start immediately and do not ask the user follow-up questions.\n\n"
        "Finish as soon as `{{RESULTS_DIR}}/solution.json` is complete: valid JSON, "
        "one `tasks` element per subproblem in the original order, every field "
        "filled in, and the same models and numbers throughout. That file is the "
        "whole submission -- once it is written and verified, stop. Do not write a "
        "separate report, do not keep exploring after the answers are in hand, and "
        "do not start work beyond the subproblems the problem asks about."
    )
    if prompt.count(closing) != 1:
        raise RuntimeError("Shared prompt has an unexpected closing instruction")
    prompt = prompt.replace(closing, stop_instruction, 1)
    return prompt


def runtime_args(args):
    """Prepare clean workspaces and start each Agent as soon as it registers."""
    run_args = _ORIGINAL_RUNTIME_ARGS(args)
    run_args.prepare_interaction_artifacts = False
    run_args.require_clean_task_workspace = True
    run_args.pipeline_agent_start = True
    run_args.benchmark = args.benchmark
    run_args.mmbench_root = args.mmbench_root
    run_args.mmbench_judge_model = args.mmbench_judge_model
    run_args.mmbench_judge_api_key = args.mmbench_judge_api_key
    run_args.mmbench_judge_base_url = args.mmbench_judge_base_url
    run_args.mmbench_judge_timeout = args.mmbench_judge_timeout
    return run_args


def stage_planning_draft(problem_id: str, output_dir: Path) -> dict:
    """Copy the planning draft and its pre-gathered evidence into the run.

    The solver prompt is the interactive arm's with the interaction section
    removed: it tells the agent to refine ``draft.md`` and to read the empirical
    facts from ``data/external_data.md`` instead of searching.  Both have to be
    present here or the run has nothing to refine and no sanctioned way to obtain
    external facts.
    """
    resolved = _DRAFT_REPORTS.get(problem_id)
    if resolved is None:
        raise FileNotFoundError(
            f"No planning draft resolved for MM-Bench problem {problem_id}"
        )
    # resolve_planning_drafts hands back strings, not Paths.
    source = Path(resolved)
    draft_target = output_dir / "results" / "draft.md"
    shutil.copy2(source, draft_target)
    if not draft_target.read_text(encoding="utf-8", errors="replace").strip():
        raise RuntimeError(f"Planning draft is empty: {draft_target}")
    empirical_source = source.parents[1] / "data" / "external_data.md"
    empirical_target = output_dir / "data" / "external_data.md"
    if empirical_source.is_file() and empirical_source.read_text(
        encoding="utf-8", errors="replace"
    ).strip():
        empirical_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(empirical_source, empirical_target)
    else:
        # Warn rather than fail, matching the interactive arm: a pool that is
        # only partly regenerated still runs, but the gap stays visible.
        print(
            f"Planning draft for {problem_id} has no data/external_data.md at "
            f"{empirical_source}; the solver will have no pre-gathered evidence.",
            flush=True,
        )
    # Point the solver prompt at the draft it was staged for.  The interactive
    # launchers substitute this placeholder while preparing their own runs, but
    # this path stages the draft itself, so without this the prompt hands the
    # solver a literal "{{DRAFT_PATH}}" and it has to infer the location from
    # the surrounding prose.  Mirrors DRAFT_PATH_PLACEHOLDER in the launchers.
    prompt_path = Path(output_dir).parent / "prompt.md"
    if prompt_path.is_file():
        prompt = prompt_path.read_text(encoding="utf-8", errors="replace")
        if DRAFT_PATH_PLACEHOLDER in prompt:
            prompt_path.write_text(
                prompt.replace(DRAFT_PATH_PLACEHOLDER, str(draft_target.resolve())),
                encoding="utf-8",
            )
        elif str(draft_target.resolve()) not in prompt:
            print(
                "Warning: solver prompt names neither {{DRAFT_PATH}} nor the "
                f"staged draft at {draft_target}",
                flush=True,
            )
    return {
        "initial_draft_used": True,
        "initial_draft_source": str(source),
        "initial_draft_path": str(draft_target),
        "empirical_data_source": (
            str(empirical_source) if empirical_target.is_file() else ""
        ),
        "empirical_data_path": (
            str(empirical_target) if empirical_target.is_file() else ""
        ),
    }


def stage_draft_data(problem_id: str, output_dir: Path) -> dict:
    """Stage a draft's pre-gathered evidence, but not the draft itself.

    The draft arm is handed the pool's proposed solution and refines it; this arm
    is handed the same evidence and the problem statement alone, so what it builds
    is comparable to that arm without inheriting its plan.

    Raises rather than warning when the evidence is absent: the prompt tells the
    solver to read data/external_data.md and forbids searching, so a run without
    it would be scored on a factual basis it was never given.
    """
    resolved = _DRAFT_REPORTS.get(problem_id)
    if resolved is None:
        raise FileNotFoundError(
            f"No planning draft resolved for MM-Bench problem {problem_id}"
        )
    # resolve_planning_drafts hands back strings, not Paths.
    source = Path(resolved)
    empirical_source = source.parents[1] / "data" / "external_data.md"
    if not (
        empirical_source.is_file()
        and empirical_source.read_text(encoding="utf-8", errors="replace").strip()
    ):
        raise RuntimeError(
            f"Planning draft for {problem_id} has no data/external_data.md at "
            f"{empirical_source}; this arm reuses exactly that evidence and has no "
            "way to obtain it otherwise."
        )
    empirical_target = output_dir / "data" / "external_data.md"
    empirical_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(empirical_source, empirical_target)
    return {
        # No planning draft reached the solver, so the report and config must not
        # claim one did.
        "initial_draft_used": False,
        "empirical_data_source": str(empirical_source),
        "empirical_data_path": str(empirical_target),
    }


def prepare_mmbench_validation_problem(
    mmbench_root: Path,
    problem_id: str,
    problem: dict,
    prompt_path: Path,
    round_number: int,
    repetition: int,
    experiment: Path,
    args,
) -> dict:
    """Prepare a fresh clean-baseline run and stage native MM-Bench data."""
    prepared = strategy.PREPARE_FRESH_PROBLEM(
        problem_id,
        problem,
        prompt_path,
        round_number,
        repetition,
        experiment,
        args,
    )
    if prepared["recovered"]:
        return prepared

    source_root = Path(mmbench_root).resolve() / "dataset" / problem_id
    declared_paths = problem.get("dataset_path", [])
    if source_root.is_dir():
        data_dir = Path(prepared["output_dir"]) / "data"
        for source in sorted(source_root.rglob("*")):
            target = data_dir / source.relative_to(source_root)
            if source.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            elif source.is_file():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
    elif declared_paths:
        # The native definition names dataset files that this MMBench checkout
        # does not ship (2018_B is the only such task, and its data is a COMAP
        # contest file the upstream bundle omits).  The definition is still
        # rendered verbatim into the prompt, so the agent sees what the
        # benchmark declares and copes with the absence exactly as it does for a
        # task that ships no data.  Failing here would drop the task from an
        # otherwise fixed split and invalidate comparisons across rounds.
        print(
            f"MM-Bench problem {problem_id} declares dataset files "
            f"({', '.join(map(str, declared_paths))}) but {source_root} does not "
            "exist; staging nothing.",
            flush=True,
        )
    else:
        print(
            f"MM-Bench problem {problem_id} declares no dataset; staging nothing.",
            flush=True,
        )

    metadata_path = Path(prepared["run_dir"]) / "meta" / "run.json"
    metadata = strategy.workflow_evolution.read_json(metadata_path, {})
    metadata.update(
        {
            "benchmark": "mmbench",
            "mmbench_problem_file": str(
                (Path(mmbench_root).resolve() / "problem" / f"{problem_id}.json")
            ),
            "mmbench_dataset_source": (
                str(source_root) if source_root.is_dir() else ""
            ),
            "mmbench_declared_dataset_paths": declared_paths,
        }
    )
    if _DRAFT_MODE:
        metadata.update(
            stage_planning_draft(problem_id, Path(prepared["output_dir"]))
        )
    elif _REUSE_DRAFT_DATA:
        metadata.update(
            stage_draft_data(problem_id, Path(prepared["output_dir"]))
        )
    strategy.workflow_evolution.write_json(metadata_path, metadata)
    return prepared


def run_baseline_validation_problem(
    prepared: dict,
    _rubric: dict,
    round_number: int,
    experiment: Path,
    args,
) -> dict:
    """Execute and judge one problem without starting the expert bridge."""
    problem_id = prepared["problem_id"]
    result = {
        "run_dir": prepared["run_dir"],
        "prompt": prepared["prompt"],
        "final_report": prepared["final_report"],
    }
    if not prepared["recovered"]:
        session_id = strategy.baseline.slugify(
            f"{problem_id}-clean-baseline-r{round_number}-"
            f"x{prepared['repetition']}-{uuid.uuid4().hex[:8]}"
        )
        # The three backends take the same arguments; the draft-based ones are
        # told there is no dialogue to account for, so they stop after the
        # submission instead of running the interaction bookkeeping and gate.
        if _AGENT_BACKEND == "openhands":
            phase = partial(
                openhands_backend.run_openhands_modeling_phase,
                check_interaction=False,
            )
        elif _AGENT_BACKEND == "claude":
            phase = partial(
                claude_backend.run_claude_modeling_phase,
                check_interaction=False,
            )
        else:
            phase = strategy.run_end_to_end_modeling_phase
        try:
            phase(
                prepared,
                session_id,
                prepared["prompt"],
                args,
                prepared["final_report"],
            )
        finally:
            strategy.interaction.assert_clean_task_output_workspace(
                Path(prepared["output_dir"])
            )
        final_report = Path(prepared["final_report"])
        if not final_report.is_file() or not final_report.read_text(
            encoding="utf-8"
        ).strip():
            raise RuntimeError(
                "OpenClaw completed without a non-empty final report at "
                f"{final_report}. See {Path(prepared['run_dir']) / 'meta' / 'solve.log'}."
            )
        strategy.baseline.record_disabled_workflow_check(
            Path(prepared["run_dir"]) / "meta" / "workflow_check.json"
        )

    judged = strategy.interaction.judge_report(
        problem_id, result, round_number, experiment, args
    )
    return {
        "problem_id": problem_id,
        "repetition": prepared["repetition"],
        "run_dir": str(result["run_dir"]),
        "final_report": str(result["final_report"]),
        "baseline_no_interaction": True,
        "clean_prompt": True,
        "interaction_receipt": {},
        **judged,
    }


def parse_args():
    extension_parser = argparse.ArgumentParser(add_help=False)
    extension_parser.add_argument(
        "--benchmark",
        choices=("modelingbench", "mmbench"),
        default="modelingbench",
    )
    extension_parser.add_argument(
        "--mmbench-root", type=Path, default=DEFAULT_MMBENCH_ROOT
    )
    extension_parser.add_argument(
        "--mmbench-judge-model", default="deepseek-v4-flash"
    )
    extension_parser.add_argument("--mmbench-judge-api-key")
    extension_parser.add_argument("--mmbench-judge-base-url")
    extension_parser.add_argument(
        "--mmbench-judge-timeout", type=float, default=600.0
    )
    extension_parser.add_argument(
        "--agent-backend",
        choices=("openclaw", "openhands", "claude"),
        default="openclaw",
        help=(
            "Which agent runtime solves the task. openhands and claude "
            "additionally need --planning-draft-root and run the same prompt as "
            "the interactive arm minus its expert-interaction section."
        ),
    )
    extension_parser.add_argument(
        "--planning-draft-root",
        type=Path,
        nargs="+",
        help=(
            "Roots holding planning drafts (with their data/external_data.md). "
            "Only used with --agent-backend openhands or claude."
        ),
    )
    extension_parser.add_argument(
        "--reuse-draft-data",
        action="store_true",
        help=(
            "Take only each planning draft's data/external_data.md -- the "
            "evidence it gathered -- and not the draft's proposed solution. The "
            "solver is given the problem statement plus that evidence, is told "
            "not to search, and stops once solution.json is complete."
        ),
    )
    raw_argv = sys.argv[1:]
    extension, remaining = extension_parser.parse_known_args(raw_argv)
    original_argv = sys.argv
    sys.argv = [sys.argv[0], *remaining]
    try:
        args = _ORIGINAL_PARSE_ARGS()
    finally:
        sys.argv = original_argv
    args.benchmark = extension.benchmark
    args.mmbench_root = extension.mmbench_root.resolve()
    args.mmbench_judge_model = extension.mmbench_judge_model
    args.mmbench_judge_api_key = extension.mmbench_judge_api_key
    args.mmbench_judge_base_url = extension.mmbench_judge_base_url
    args.mmbench_judge_timeout = extension.mmbench_judge_timeout
    args.agent_backend = extension.agent_backend
    args.planning_draft_root = (
        [path.resolve() for path in extension.planning_draft_root]
        if extension.planning_draft_root
        else None
    )
    args.reuse_draft_data = extension.reuse_draft_data

    def supplied(option: str) -> bool:
        return any(
            value == option or value.startswith(option + "=")
            for value in raw_argv
        )

    if args.benchmark == "mmbench":
        if args.agent_backend == "openclaw":
            # The OpenClaw integration was only ever wired for these two tasks.
            # The OpenHands mode takes any task that has a planning draft, which
            # resolve_planning_drafts verifies, so it is not held to this list.
            if not supplied("--problem-id"):
                args.problem_id = list(SUPPORTED_MMBENCH_PROBLEMS)
            unsupported = [
                problem_id
                for problem_id in args.problem_id
                if problem_id not in SUPPORTED_MMBENCH_PROBLEMS
            ]
            if unsupported:
                raise ValueError(
                    "This clean-baseline MM-Bench integration currently supports only "
                    + ", ".join(SUPPORTED_MMBENCH_PROBLEMS)
                    + "; got: "
                    + ", ".join(unsupported)
                )
        elif not args.planning_draft_root and not supplied("--problem-id"):
            # A draft backend pins its task list through the draft root.  Without
            # one it runs the problem statement alone, so the task list has to be
            # named explicitly -- nothing else pins which tasks can run.
            raise ValueError(
                f"--benchmark mmbench with --agent-backend {args.agent_backend} "
                "needs --planning-draft-root or --problem-id; nothing else pins "
                "which tasks can run."
            )
    elif not supplied("--problem-id"):
        problems = json.loads(TRAIN_DATASET.read_text(encoding="utf-8"))
        if not isinstance(problems, dict) or not problems:
            raise ValueError(f"Training dataset must be a non-empty task mapping: {TRAIN_DATASET}")
        args.problem_id = list(problems)
    for option in ("concurrency", "retry-concurrency", "judge-concurrency"):
        if not supplied("--" + option):
            setattr(args, option.replace("-", "_"), len(args.problem_id))
    if not supplied("--max-rounds"):
        args.max_rounds = 1
    return args


def validate_args(args) -> None:
    _ORIGINAL_VALIDATE_ARGS(args)
    if args.mmbench_judge_timeout <= 0:
        raise ValueError("--mmbench-judge-timeout must be positive")
    if args.exp:
        config_path = Path(args.exp) / "runs" / "config.json"
        if not config_path.is_file():
            config_path = Path(args.exp) / "config.json"
        if config_path.is_file():
            config = json.loads(config_path.read_text(encoding="utf-8"))
            if config.get("experiment_type") != EXPERIMENT_TYPE:
                raise ValueError("--exp is not a clean-baseline experiment")
            saved_benchmark = config.get("benchmark", "modelingbench")
            if saved_benchmark != args.benchmark:
                raise ValueError(
                    "Cannot resume a clean baseline with a different benchmark; "
                    "use a new --exp directory."
                )
            saved_problems = config.get("validation_problems")
            requested_problems = list(args.problem_id)
            can_extend = (
                isinstance(saved_problems, list)
                and bool(saved_problems)
                and set(saved_problems) < set(requested_problems)
            )
            if saved_problems != requested_problems and not can_extend:
                raise ValueError(
                    "Cannot resume a clean baseline with a different task list; "
                    "use a new --exp directory."
                )
            if can_extend:
                print(
                    "Extending clean baseline task list from "
                    f"{len(saved_problems)} to {len(requested_problems)}; "
                    "completed reports will be reused.",
                    flush=True,
                )
    if args.max_rounds != 1:
        raise ValueError(
            "The clean no-interaction baseline has one round; use "
            "--validation-repetitions for repeated samples."
        )
    if args.enforce_substantive_interaction_gate:
        raise ValueError(
            "--enforce-substantive-interaction-gate is incompatible with the "
            "clean no-interaction baseline."
        )
    if args.agent_backend in DRAFT_BACKENDS:
        if args.benchmark != "mmbench":
            raise ValueError(
                f"--agent-backend {args.agent_backend} needs --benchmark mmbench: "
                "the prompt it reuses is the MM-Bench solver prompt."
            )
        # No --planning-draft-root check here any more.  parse_args has already
        # accepted the run only when a draft root or an explicit --problem-id
        # pins the task list, and without a draft root the solver is handed the
        # problem statement alone, so there is no draft to insist on.
    if getattr(args, "reuse_draft_data", False):
        if args.benchmark != "mmbench":
            raise ValueError(
                "--reuse-draft-data needs --benchmark mmbench: the evidence it "
                "stages comes from the MM-Bench draft pool."
            )
        if not args.planning_draft_root:
            raise ValueError(
                "--reuse-draft-data needs --planning-draft-root: that is where "
                "each problem's data/external_data.md is read from."
            )


def install_runtime_hooks(args, problems: dict) -> None:
    if args.benchmark == "mmbench":
        strategy.interaction.prepare_validation_problem = partial(
            prepare_mmbench_validation_problem, args.mmbench_root
        )
        strategy.interaction.judge_report = partial(
            mmbench_support.judge_report_with_mmbench,
            problems,
            args.mmbench_root,
        )
    else:
        strategy.interaction.prepare_validation_problem = strategy.PREPARE_FRESH_PROBLEM
    strategy.interaction.run_validation_problem = run_baseline_validation_problem


def main() -> None:
    """Run one clean baseline without creating strategy-evolution artifacts."""
    global _AGENT_BACKEND, _DRAFT_MODE, _DRAFT_REPORTS, _REUSE_DRAFT_DATA
    args = parse_args()
    _AGENT_BACKEND = args.agent_backend
    # A draft-capable backend stages one only when handed a draft root; without
    # it the solver gets the problem statement alone, as openclaw always has.
    # --reuse-draft-data borrows that root for its evidence instead, so the draft
    # itself stays out of the run.
    _REUSE_DRAFT_DATA = bool(getattr(args, "reuse_draft_data", False))
    _DRAFT_MODE = (
        _AGENT_BACKEND in DRAFT_BACKENDS
        and bool(args.planning_draft_root)
        and not _REUSE_DRAFT_DATA
    )
    validate_args(args)
    if args.benchmark == "mmbench":
        problems, selected_problem_ids = mmbench_support.load_mmbench_problems(
            args.mmbench_root, list(args.problem_id)
        )
        args.problem_id = selected_problem_ids
    else:
        problems = strategy.baseline.load_problems()
    unknown = [problem_id for problem_id in args.problem_id if problem_id not in problems]
    if unknown:
        raise ValueError("Unknown problem ID(s): " + ", ".join(unknown))
    if len(args.problem_id) != len(set(args.problem_id)):
        raise ValueError("problem IDs must be unique")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    experiment = (
        Path(args.exp).resolve() if args.exp else
        TRAIN_DATASET.parents[1]
        / "openclaw_experiments"
        / (
            f"{EXPERIMENT_PREFIX}_mmbench_{stamp}"
            if args.benchmark == "mmbench"
            else f"{EXPERIMENT_PREFIX}_{stamp}"
        )
    )
    if experiment.is_dir() and any(path.name != "runs" for path in experiment.iterdir()):
        raise ValueError(
            "This experiment contains the old layout. Use a new --exp directory "
            "for a clean baseline containing only runs."
        )
    round_dir = experiment / "runs" / "round_1"
    round_dir.mkdir(parents=True, exist_ok=True)
    prompt_path = round_dir / "prompt.md"
    if _DRAFT_MODE:
        # Same prompt as the interactive arm with the expert-interaction section
        # removed and nothing put in its place: that section is the only
        # difference between the two arms, so the rest has to stay identical.
        # Each backend launcher carries its own copy of that prompt rather than
        # importing a shared one, so the matching module is the one whose text
        # this arm runs -- editing a copy has to move only that arm.
        import importlib

        module_name = (
            "run_substantive_interaction_workflow_evolution_from_initial_draft_"
            + _AGENT_BACKEND
        )
        try:
            launcher = importlib.import_module(f".{module_name}", __package__ or "src.OpenClaw")
        except ImportError:
            launcher = importlib.import_module(module_name)
        _DRAFT_REPORTS = mmbench_support.resolve_planning_drafts(
            args.planning_draft_root, list(args.problem_id)
        )
        launcher._benchmark = "mmbench"
        prompt = launcher.build_interactive_solver_prompt(
            launcher.fixed_initial_workflow(), include_interaction=False
        )
        print(
            f"Resolved {len(_DRAFT_REPORTS)} planning draft(s) from "
            + ", ".join(str(root) for root in args.planning_draft_root),
            flush=True,
        )
    elif _REUSE_DRAFT_DATA:
        # The draft root is still read, but only to locate each problem's
        # data/external_data.md -- the draft's own plan never reaches the solver.
        _DRAFT_REPORTS = mmbench_support.resolve_planning_drafts(
            args.planning_draft_root, list(args.problem_id)
        )
        prompt = build_solution_only_prompt("mmbench")
        print(
            f"Resolved {len(_DRAFT_REPORTS)} planning draft(s) for their evidence "
            "only, from "
            + ", ".join(str(root) for root in args.planning_draft_root),
            flush=True,
        )
    else:
        prompt = (
            build_clean_baseline_prompt({}, "mmbench")
            if args.benchmark == "mmbench"
            else build_clean_baseline_prompt({})
        )
    prompt_path.write_text(
        prompt, encoding="utf-8"
    )
    config = {
        "experiment_type": EXPERIMENT_TYPE,
        "execution_mode": "clean_baseline_no_interaction",
        "agent_backend": _AGENT_BACKEND,
        "initial_draft_used": _DRAFT_MODE,
        "planning_draft_roots": (
            [str(root) for root in args.planning_draft_root]
            if _DRAFT_MODE
            else []
        ),
        "benchmark": args.benchmark,
        "split": (
            "mmbench_dataset_tasks"
            if args.benchmark == "mmbench"
            else "modelingbench_train"
        ),
        "max_rounds": 1,
        "validation_problems": args.problem_id,
        "model": args.model,
        "thinking": args.thinking,
        "timeout": args.timeout,
        "concurrency": args.concurrency,
        "retry_concurrency": args.retry_concurrency,
        "judge_concurrency": args.judge_concurrency,
        "pipeline_agent_start": True,
        "isolated_openclaw_config": True,
        "openclaw_bootstrap_suppressed_before_agent_registration": True,
        "workspace_root_entries": ["code", "data", "results", "logs"],
        "validation_repetitions": args.validation_repetitions,
        "judge_repeats": args.judge_repeats,
    }
    if args.benchmark == "mmbench":
        config.update(
            {
                "mmbench_root": str(args.mmbench_root),
                "mmbench_judge_model": args.mmbench_judge_model,
            }
        )
    strategy.workflow_evolution.write_json(experiment / "runs" / "config.json", config)
    print(f"Experiment: {experiment}", flush=True)
    print(f"Problems: {len(args.problem_id)}; concurrency: {args.concurrency}", flush=True)
    if args.initialize_only:
        print(f"Initialization complete; prompt: {prompt_path}")
        return

    strategy.interaction.VALIDATION_PROBLEMS = tuple(args.problem_id)
    install_runtime_hooks(args, problems)
    strategy.workflow_evolution.configure_completion_grace(
        strategy.baseline.run_problem, args.completion_grace
    )
    # Required for both backends: the preparation path still registers the task
    # through the OpenClaw CLI, and that CLI initialises the workspace with
    # AGENTS.md, SOUL.md and a git repo unless this config suppresses it.  Those
    # entries fail the clean-workspace assertion, so skipping this call breaks
    # the OpenHands mode just as surely as it would break the OpenClaw one.
    isolated_config, previous_config = activate_clean_openclaw_config()
    atexit.register(
        remove_clean_openclaw_config, isolated_config, previous_config
    )
    run_args = runtime_args(args)
    run_args.evaluation_round_dir = round_dir
    existing_result = strategy.workflow_evolution.read_json(
        round_dir / "result.json", {}
    )
    result = strategy.interaction.evaluate_round(
        experiment, 1, {"rubric_id": "clean_baseline_no_interaction"},
        problems, prompt_path, run_args, existing_result=existing_result,
    )
    result.pop("rubric", None)
    result.pop("rubric_id", None)
    result["baseline_no_interaction"] = True
    strategy.workflow_evolution.write_json(round_dir / "result.json", result)
    print(f"Clean baseline complete; results: {round_dir / 'result.json'}", flush=True)


if __name__ == "__main__":
    main()
