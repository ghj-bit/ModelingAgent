"""Run a no-interaction baseline with a minimal modeling prompt.

This variant reuses the execution and evaluation behavior of
``run_substantive_interaction_strategy_baseline.py`` while removing the staged
process-report contract and the additional report-integration instructions.
By default, run every task in data/modeling_data_train.json with one worker
per task. Explicit problem IDs and concurrency flags override these defaults.
"""

from __future__ import annotations

import atexit
import json
import sys
import uuid
from datetime import datetime
from pathlib import Path

try:
    from . import run_substantive_interaction_strategy_evolution as strategy
except ImportError:
    import run_substantive_interaction_strategy_evolution as strategy


EXPERIMENT_TYPE = "substantive_interaction_strategy_clean_baseline"
EXPERIMENT_PREFIX = "interaction_strategy_clean_baseline"
TRAIN_DATASET = Path(__file__).resolve().parents[2] / "data" / "modeling_data_train.json"

_ORIGINAL_PARSE_ARGS = strategy.parse_args
_ORIGINAL_VALIDATE_ARGS = strategy.validate_args
_ORIGINAL_RUNTIME_ARGS = strategy.runtime_args


def build_clean_baseline_prompt(_strategy: dict) -> str:
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
    return prompt


def runtime_args(args):
    """Prepare clean workspaces without expert-interaction files or folders."""
    run_args = _ORIGINAL_RUNTIME_ARGS(args)
    run_args.prepare_interaction_artifacts = False
    return run_args


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
        strategy.run_end_to_end_modeling_phase(
            prepared,
            session_id,
            prepared["prompt"],
            args,
            prepared["final_report"],
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
    args = _ORIGINAL_PARSE_ARGS()

    def supplied(option: str) -> bool:
        return any(
            value == option or value.startswith(option + "=")
            for value in sys.argv[1:]
        )

    if not supplied("--problem-id"):
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
    if args.exp:
        config_path = Path(args.exp) / "runs" / "config.json"
        if not config_path.is_file():
            config_path = Path(args.exp) / "config.json"
        if config_path.is_file():
            config = json.loads(config_path.read_text(encoding="utf-8"))
            if config.get("experiment_type") != EXPERIMENT_TYPE:
                raise ValueError("--exp is not a clean-baseline experiment")
            if config.get("validation_problems") != args.problem_id:
                raise ValueError(
                    "Cannot resume a clean baseline with a different task list; "
                    "use a new --exp directory."
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


def install_runtime_hooks() -> None:
    strategy.interaction.prepare_validation_problem = strategy.PREPARE_FRESH_PROBLEM
    strategy.interaction.run_validation_problem = run_baseline_validation_problem


def main() -> None:
    """Run one clean baseline without creating strategy-evolution artifacts."""
    args = parse_args()
    validate_args(args)
    problems = strategy.baseline.load_problems()
    unknown = [problem_id for problem_id in args.problem_id if problem_id not in problems]
    if unknown:
        raise ValueError("Unknown problem ID(s): " + ", ".join(unknown))
    if len(args.problem_id) != len(set(args.problem_id)):
        raise ValueError("problem IDs must be unique")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    experiment = (
        Path(args.exp).resolve() if args.exp else
        TRAIN_DATASET.parents[1] / "openclaw_experiments" / f"{EXPERIMENT_PREFIX}_{stamp}"
    )
    if experiment.is_dir() and any(path.name != "runs" for path in experiment.iterdir()):
        raise ValueError(
            "This experiment contains the old layout. Use a new --exp directory "
            "for a clean baseline containing only runs."
        )
    round_dir = experiment / "runs" / "round_1"
    round_dir.mkdir(parents=True, exist_ok=True)
    prompt_path = round_dir / "prompt.md"
    prompt_path.write_text(build_clean_baseline_prompt({}), encoding="utf-8")
    config = {
        "experiment_type": EXPERIMENT_TYPE,
        "execution_mode": "clean_baseline_no_interaction",
        "initial_draft_used": False,
        "max_rounds": 1,
        "validation_problems": args.problem_id,
        "model": args.model,
        "thinking": args.thinking,
        "timeout": args.timeout,
        "concurrency": args.concurrency,
        "retry_concurrency": args.retry_concurrency,
        "judge_concurrency": args.judge_concurrency,
        "validation_repetitions": args.validation_repetitions,
        "judge_repeats": args.judge_repeats,
    }
    strategy.workflow_evolution.write_json(experiment / "runs" / "config.json", config)
    print(f"Experiment: {experiment}", flush=True)
    print(f"Problems: {len(args.problem_id)}; concurrency: {args.concurrency}", flush=True)
    if args.initialize_only:
        print(f"Initialization complete; prompt: {prompt_path}")
        return

    strategy.interaction.VALIDATION_PROBLEMS = tuple(args.problem_id)
    install_runtime_hooks()
    strategy.workflow_evolution.configure_completion_grace(
        strategy.baseline.run_problem, args.completion_grace
    )
    openclaw = strategy.baseline.find_openclaw_command(args.openclaw_command)
    atexit.register(
        strategy.interaction.cleanup_experiment_agents_at_exit, openclaw, experiment
    )
    run_args = runtime_args(args)
    run_args.evaluation_round_dir = round_dir
    result = strategy.interaction.evaluate_round(
        experiment, 1, {"rubric_id": "clean_baseline_no_interaction"},
        problems, prompt_path, run_args,
    )
    result.pop("rubric", None)
    result.pop("rubric_id", None)
    result["baseline_no_interaction"] = True
    strategy.workflow_evolution.write_json(round_dir / "result.json", result)
    print(f"Clean baseline complete; results: {round_dir / 'result.json'}", flush=True)


if __name__ == "__main__":
    main()
