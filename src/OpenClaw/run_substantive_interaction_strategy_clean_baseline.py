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
    from . import run_substantive_interaction_strategy_evolution as strategy
    from . import run_substantive_interaction_workflow_test_from_initial_draft as mmbench_support
except ImportError:
    import run_substantive_interaction_strategy_evolution as strategy
    import run_substantive_interaction_workflow_test_from_initial_draft as mmbench_support


EXPERIMENT_TYPE = "substantive_interaction_strategy_clean_baseline"
EXPERIMENT_PREFIX = "interaction_strategy_clean_baseline"
TRAIN_DATASET = Path(__file__).resolve().parents[2] / "data" / "modeling_data_train.json"
DEFAULT_MMBENCH_ROOT = Path(r"D:\vscode_project\LLM-MM-Agent\MMBench")
SUPPORTED_MMBENCH_PROBLEMS = ("2003_C", "2003_B")

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
        try:
            strategy.run_end_to_end_modeling_phase(
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

    def supplied(option: str) -> bool:
        return any(
            value == option or value.startswith(option + "=")
            for value in raw_argv
        )

    if args.benchmark == "mmbench":
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
    args = parse_args()
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
        "initial_draft_used": False,
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
