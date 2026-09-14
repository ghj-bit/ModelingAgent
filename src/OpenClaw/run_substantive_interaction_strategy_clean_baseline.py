"""Run a no-interaction baseline with a minimal modeling prompt.

This variant reuses the execution and evaluation behavior of
``run_substantive_interaction_strategy_baseline.py`` while removing the staged
process-report contract and the additional report-integration instructions.
"""

from __future__ import annotations

import sys
import uuid
from pathlib import Path

try:
    from . import run_substantive_interaction_strategy_evolution as strategy
except ImportError:
    import run_substantive_interaction_strategy_evolution as strategy


EXPERIMENT_TYPE = "substantive_interaction_strategy_clean_baseline"
EXPERIMENT_PREFIX = "interaction_strategy_clean_baseline"

_ORIGINAL_INSTALL_RUNTIME_HOOKS = strategy.install_runtime_hooks
_ORIGINAL_PARSE_ARGS = strategy.parse_args
_ORIGINAL_VALIDATE_ARGS = strategy.validate_args


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
    if prompt.count(workflow_summary) != 1 or prompt.count(final_report_contract) != 1:
        raise RuntimeError("Shared prompt has an unexpected workflow/report layout")
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
    if "--max-rounds" not in sys.argv:
        args.max_rounds = 1
    return args


def validate_args(args) -> None:
    _ORIGINAL_VALIDATE_ARGS(args)
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
    _ORIGINAL_INSTALL_RUNTIME_HOOKS()
    strategy.workflow.build_workflow_refinement_prompt = build_clean_baseline_prompt
    strategy.interaction.run_validation_problem = run_baseline_validation_problem


def main() -> None:
    strategy.EXPERIMENT_TYPE = EXPERIMENT_TYPE
    strategy.EXPERIMENT_PREFIX = EXPERIMENT_PREFIX
    strategy.build_end_to_end_prompt = build_clean_baseline_prompt
    strategy.parse_args = parse_args
    strategy.validate_args = validate_args
    strategy.install_runtime_hooks = install_runtime_hooks
    strategy.main()


if __name__ == "__main__":
    main()
