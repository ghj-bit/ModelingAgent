"""Run the clean baseline while requesting a planned modeling-report draft only.

This preserves clean-baseline task execution, retry, and checkpoint behavior,
but intentionally skips ModelingBench Judge evaluation. The Agent produces an
initial report outline and a concrete plan for completing each section instead
of a fully executed modeling report.
"""

from __future__ import annotations

from pathlib import Path

try:
    from . import run_substantive_interaction_strategy_clean_baseline as baseline
except ImportError:
    import run_substantive_interaction_strategy_clean_baseline as baseline


EXPERIMENT_TYPE = "substantive_interaction_strategy_clean_baseline_initial_draft"
EXPERIMENT_PREFIX = "interaction_strategy_clean_baseline_initial_draft"
_BASE_PREPARE_RUN = baseline.strategy.baseline.prepare_run
_BASE_INSTALL_RUNTIME_HOOKS = baseline.install_runtime_hooks


def build_initial_draft_prompt(_strategy: dict) -> str:
    """Return the planner-only prompt, rendered later with task placeholders."""
    return """# ModelingBench Task — Modeling Planner

You are a mathematical modeling planning agent.

Your task is to generate an initial modeling plan draft for the given problem.

You are NOT a solver. Design only a roadmap for future modeling.

## Restrictions

Do NOT:

- solve the problem,
- analyze data,
- perform calculations,
- fit models,
- write or run code,
- run experiments,
- generate plots/images,
- provide final results or conclusions.

Only provide:

- modeling workflow,
- assumptions,
- candidate methods,
- data processing plan,
- implementation plan,
- validation strategy.

---

# Problem

Use the provided problem statement and data directly.

Problem ID: `{{PROBLEM_ID}}`
Title: {{TITLE}}
Source: {{SOURCE}} {{YEAR}}

{{QUESTION}}

---

# Planning Workflow

1. Problem Understanding

- objectives
- subproblems
- deliverables

2. Assumptions

- necessary assumptions
- justification
- future validation approach

3. Modeling Framework

- candidate models
- variables
- mathematical ideas
- advantages and limitations

4. Data Plan

- preprocessing
- feature construction
- data usage strategy

5. Implementation Plan

- algorithms
- workflow
- required modules

6. Validation Plan

- evaluation metrics
- validation methods
- sensitivity analysis

---

# Output

Create:

`{{FINAL_REPORT}}`

The report must be a **modeling blueprint draft**, not a completed solution.

Required sections:

1. Problem Background and Restatement
2. Objectives and Subproblems
3. Assumptions
4. Data Processing Plan
5. Candidate Model Framework
6. Implementation Roadmap
7. Validation Strategy
8. Expected Result Interpretation
9. Limitations and Improvements

Use future-oriented language.

Do not include:

- computed results,
- completed analysis,
- executed experiments,
- final conclusions.

Before finishing, verify:

- `draft.md` exists,
- the file contains only planning content,
- no actual solving was performed.

Start immediately.
"""


def prepare_initial_draft_run(*args, **kwargs):
    """Render the planner prompt with ``draft.md`` as its required artifact."""
    run_dir, output_dir, prompt_path = _BASE_PREPARE_RUN(*args, **kwargs)
    standard_report = output_dir / "results" / "solution_report.md"
    draft_report = output_dir / "results" / "draft.md"
    prompt = prompt_path.read_text(encoding="utf-8")
    if str(standard_report) not in prompt:
        raise RuntimeError("Initial-draft prompt did not render the final report path")
    prompt_path.write_text(
        prompt.replace(str(standard_report), str(draft_report)), encoding="utf-8"
    )
    metadata_path = run_dir / "meta" / "run.json"
    metadata = baseline.strategy.workflow_evolution.read_json(metadata_path, {})
    metadata["final_report"] = str(draft_report)
    baseline.strategy.workflow_evolution.write_json(metadata_path, metadata)
    return run_dir, output_dir, prompt_path


def prepare_initial_draft_validation_problem(
    problem_id: str,
    problem: dict,
    prompt_path: Path,
    round_number: int,
    repetition: int,
    experiment: Path,
    args,
) -> dict:
    """Prepare or recover a task whose sole report artifact is ``draft.md``."""
    evaluation_ids = tuple(
        getattr(args, "evaluation_problem_ids", baseline.strategy.interaction.VALIDATION_PROBLEMS)
    )
    problem_index = evaluation_ids.index(problem_id) + 1
    run_prefix = f"r{repetition}p{problem_index}"
    run_root = experiment / "runs" / f"round_{round_number}"
    existing = sorted(
        run_root.glob(f"{run_prefix}_*/output/results/draft.md"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    for draft in existing:
        run_dir = draft.parents[2]
        metadata = baseline.strategy.workflow_evolution.read_json(run_dir / "meta" / "run.json", {})
        if metadata.get("problem_id") == problem_id and draft.read_text(
            encoding="utf-8", errors="replace"
        ).strip():
            return {
                "problem_id": problem_id,
                "repetition": repetition,
                "run_dir": run_dir,
                "output_dir": run_dir / "output",
                "prompt": run_dir / "prompt.md",
                "final_report": draft,
                "agent_id": None,
                "openclaw": None,
                "recovered": True,
            }

    prepared = baseline.strategy.PREPARE_FRESH_PROBLEM(
        problem_id, problem, prompt_path, round_number, repetition, experiment, args
    )
    prepared["final_report"] = Path(prepared["output_dir"]) / "results" / "draft.md"
    return prepared


def run_initial_draft_validation_problem(
    prepared: dict,
    _rubric: dict,
    round_number: int,
    _experiment: Path,
    args,
) -> dict:
    """Execute one planner task and checkpoint its draft without invoking Judge."""
    problem_id = prepared["problem_id"]
    final_report = Path(prepared["final_report"])
    if not prepared["recovered"]:
        session_id = baseline.strategy.baseline.slugify(
            f"{problem_id}-initial-draft-r{round_number}-"
            f"x{prepared['repetition']}-{baseline.uuid.uuid4().hex[:8]}"
        )
        try:
            baseline.strategy.run_end_to_end_modeling_phase(
                prepared,
                session_id,
                prepared["prompt"],
                args,
                final_report,
            )
        finally:
            baseline.strategy.interaction.assert_clean_task_output_workspace(
                Path(prepared["output_dir"])
            )
        if not final_report.is_file() or not final_report.read_text(
            encoding="utf-8"
        ).strip():
            raise RuntimeError(
                "OpenClaw completed without a non-empty initial draft at "
                f"{final_report}. See {Path(prepared['run_dir']) / 'meta' / 'solve.log'}."
            )
        baseline.strategy.baseline.record_disabled_workflow_check(
            Path(prepared["run_dir"]) / "meta" / "workflow_check.json"
        )

    # ``evaluate_round`` requires a numeric objective to aggregate checkpoints.
    # This sentinel is explicitly not a score and is never sent to Judge.
    return {
        "problem_id": problem_id,
        "repetition": prepared["repetition"],
        "run_dir": str(prepared["run_dir"]),
        "final_report": str(final_report),
        "baseline_no_interaction": True,
        "clean_prompt": True,
        "judge_skipped": True,
        "interaction_receipt": {},
        "average_score": 0.0,
        "dimension_scores": {"draft_not_judged": 0.0},
        "judge_repeats": 0,
        "judge_stability_result": None,
        "judge_result": None,
    }


def install_initial_draft_runtime_hooks(*args, **kwargs) -> None:
    """Use the clean runner's evaluator with draft-aware preparation.

    The base hook takes the clean runner's own arguments; forward them so this
    override tracks whatever signature ``baseline.install_runtime_hooks`` has.
    """
    _BASE_INSTALL_RUNTIME_HOOKS(*args, **kwargs)
    baseline.strategy.interaction.prepare_validation_problem = (
        prepare_initial_draft_validation_problem
    )
    baseline.strategy.interaction.run_validation_problem = (
        run_initial_draft_validation_problem
    )


def main() -> None:
    """Run the base launcher with a draft-only prompt and distinct experiment type."""
    original_prompt = baseline.build_clean_baseline_prompt
    original_type = baseline.EXPERIMENT_TYPE
    original_prefix = baseline.EXPERIMENT_PREFIX
    original_prepare_run = baseline.strategy.baseline.prepare_run
    original_install_runtime_hooks = baseline.install_runtime_hooks
    baseline.build_clean_baseline_prompt = build_initial_draft_prompt
    baseline.EXPERIMENT_TYPE = EXPERIMENT_TYPE
    baseline.EXPERIMENT_PREFIX = EXPERIMENT_PREFIX
    baseline.strategy.baseline.prepare_run = prepare_initial_draft_run
    baseline.install_runtime_hooks = install_initial_draft_runtime_hooks
    try:
        baseline.main()
    finally:
        baseline.build_clean_baseline_prompt = original_prompt
        baseline.EXPERIMENT_TYPE = original_type
        baseline.EXPERIMENT_PREFIX = original_prefix
        baseline.strategy.baseline.prepare_run = original_prepare_run
        baseline.install_runtime_hooks = original_install_runtime_hooks


if __name__ == "__main__":
    main()
