"""Run the end-to-end strategy experiment as a no-interaction baseline.

The modeling prompt is the same prompt assembled by
``run_substantive_interaction_strategy_evolution.py`` except that no expert-
interaction strategy section is injected.  The original strategy-evolution
runner is imported rather than modified so the two experiment paths remain
independent.

This baseline intentionally supports one round.  Use
``--validation-repetitions`` when repeated baseline samples are needed.
"""

from __future__ import annotations

import sys
import uuid
from pathlib import Path

try:
    from . import run_substantive_interaction_strategy_evolution as strategy
except ImportError:
    import run_substantive_interaction_strategy_evolution as strategy


EXPERIMENT_TYPE = "substantive_interaction_strategy_baseline"
EXPERIMENT_PREFIX = "interaction_strategy_baseline"

_ORIGINAL_INSTALL_RUNTIME_HOOKS = strategy.install_runtime_hooks
_ORIGINAL_PARSE_ARGS = strategy.parse_args
_ORIGINAL_VALIDATE_ARGS = strategy.validate_args


def build_baseline_prompt(_strategy: dict) -> str:
    """Return the shared modeling prompt without an interaction section."""
    return strategy.reference_baseline_prompt_template()


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
            f"{problem_id}-baseline-r{round_number}-"
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
            "The no-interaction baseline has one round; use "
            "--validation-repetitions for repeated samples."
        )
    if args.enforce_substantive_interaction_gate:
        raise ValueError(
            "--enforce-substantive-interaction-gate is incompatible with the "
            "no-interaction baseline."
        )


def install_runtime_hooks() -> None:
    _ORIGINAL_INSTALL_RUNTIME_HOOKS()
    strategy.workflow.build_workflow_refinement_prompt = build_baseline_prompt
    strategy.interaction.run_validation_problem = run_baseline_validation_problem


def main() -> None:
    strategy.EXPERIMENT_TYPE = EXPERIMENT_TYPE
    strategy.EXPERIMENT_PREFIX = EXPERIMENT_PREFIX
    strategy.build_end_to_end_prompt = build_baseline_prompt
    strategy.parse_args = parse_args
    strategy.validate_args = validate_args
    strategy.install_runtime_hooks = install_runtime_hooks
    strategy.main()


if __name__ == "__main__":
    main()
