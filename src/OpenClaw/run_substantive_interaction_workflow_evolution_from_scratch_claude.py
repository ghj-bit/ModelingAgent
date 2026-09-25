"""Evolve expert-interaction workflows whose solvers start from scratch.

Claude Code backend sibling of
``run_substantive_interaction_workflow_evolution_from_initial_draft_claude``.
The engine, the gate margins, the utility, the judge wiring and the evolution
prompt are that launcher's, unchanged; what differs is what a Solver is handed.
Nothing precedes the run: the solver receives the problem statement and the
task's pre-gathered evidence, and owns the modeling plan itself.  Every hook that
launcher uses to stage or to compare against a prior plan is replaced here, and
the prompt it builds carries no reference to one.

The pre-gathered evidence is still reused: the prompt forbids external searches,
so without it a run would have no factual basis.  It is read out of the planner
runs' directories, which is where it was collected; the planner's own proposed
solution is never copied or read.

The initial interaction strategy is the same frozen seed the other Claude arm
uses (``interaction_policy.STRATEGIC_DECISION_CONSULTATION``), so the two arms
differ in the starting point of the *work*, not in the policy being evolved.

One prompt addition is arm-specific rather than policy: the consultation is
capped at one settled strategic decision and the solver is told so, because a
faithful consultation must not crowd out the modeling work the report is scored
on.  That paragraph is appended to the interaction section and is not part of
the policy text the optimizer rewrites.
"""

from __future__ import annotations

import shutil
from functools import partial
from pathlib import Path

try:
    from . import run_substantive_interaction_workflow_evolution as workflow
    from . import (
        run_substantive_interaction_workflow_evolution_from_initial_draft_claude as base,
    )
    from . import run_substantive_interaction_workflow_test_from_initial_draft as support
except ImportError:  # pragma: no cover - direct-file invocation support
    import run_substantive_interaction_workflow_evolution as workflow
    import run_substantive_interaction_workflow_evolution_from_initial_draft_claude as base
    import run_substantive_interaction_workflow_test_from_initial_draft as support


# Arm-specific, not policy: the optimizer may rewrite the policy, so a rule that
# must survive every round is stated outside it.  Kept short on purpose -- a
# long reminder here competes with the task itself for the solver's attention.
INTERACTION_PROPORTIONALITY_NOTE = """\
### Keep the consultation proportionate

The expert settles at most one strategic decision. The model, the code, the
results, the validation, and the submission container are yours to complete in
full, to the same standard as any other run; a good reply discharges the
interaction requirement and nothing else."""


def stage_evidence(problem_id: str, output_dir: Path, args) -> str:
    """Copy a task's pre-gathered evidence, and never the planner's solution.

    ``args.baseline_reports`` is the engine's name for the source path it hands
    this hook; only the ``data/external_data.md`` beside it is read, so nothing
    the planner proposed reaches the run.
    """
    source = Path(args.baseline_reports[problem_id])
    empirical_source = source.parents[1] / "data" / "external_data.md"
    empirical_target = Path(output_dir) / "data" / "external_data.md"
    if not (
        empirical_source.is_file()
        and empirical_source.read_text(encoding="utf-8", errors="replace").strip()
    ):
        print(
            f"No pre-gathered evidence for {problem_id} at {empirical_source}; "
            "the solver will have no factual basis.",
            flush=True,
        )
        return ""
    if not empirical_target.is_file():
        empirical_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(empirical_source, empirical_target)
    return str(empirical_target)


def strip_plan_references(policy_text: str) -> str:
    """Drop policy lines that describe a plan this arm never has.

    The seed is shared with the arm that does start from a planning draft, where
    those trigger conditions are meaningful.  Here they can never fire, and a
    solver reading them would be told to check a file it was never given.
    """
    kept = [
        line
        for line in str(policy_text).splitlines()
        if "draft" not in line.lower()
    ]
    return "\n".join(kept)


def fixed_initial_workflow() -> dict:
    """The sibling launcher's seed, with plan references dropped and re-hashed."""
    selected = _ORIGINAL_FIXED_INITIAL_WORKFLOW()
    selected["policy_text"] = strip_plan_references(selected["policy_text"])
    base.validate_workflow_with_inferred_start(selected)
    selected["workflow_id"] = workflow.workflow_id(selected)
    return selected


def prepare_from_evidence(
    problem_id: str,
    problem: dict,
    prompt_path: Path,
    round_number: int,
    repetition: int,
    experiment: Path,
    args,
) -> dict:
    """Prepare a fresh Solver workspace holding the task's evidence alone."""
    prepared = workflow.substantive.ORIGINAL_PREPARE_VALIDATION_PROBLEM(
        problem_id,
        problem,
        prompt_path,
        round_number,
        repetition,
        experiment,
        args,
    )
    output_dir = Path(prepared["output_dir"])
    empirical_path = stage_evidence(problem_id, output_dir, args)
    metadata_path = Path(prepared["run_dir"]) / "meta" / "run.json"
    metadata = workflow.workflow_evolution.read_json(metadata_path, {})
    metadata.update(
        {
            "initial_draft_used": False,
            "empirical_data_source": str(Path(args.baseline_reports[problem_id]).parents[1] / "data" / "external_data.md"),
            "empirical_data_path": empirical_path,
            "execution_mode": "expert_guided_solution_from_scratch",
        }
    )
    workflow.workflow_evolution.write_json(metadata_path, metadata)
    if prepared["recovered"]:
        base.ensure_planning_interaction_evidence(output_dir)
    return prepared


def prepare_mmbench_from_evidence(
    mmbench_root: Path,
    problem_id: str,
    problem: dict,
    prompt_path: Path,
    round_number: int,
    repetition: int,
    experiment: Path,
    args,
) -> dict:
    """MM-Bench preparation: native dataset plus the pre-gathered evidence."""
    prepared = prepare_from_evidence(
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
    # The native dataset directory is the benchmark's own input, not the
    # planner's: stage it exactly as the other arm does.
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
    else:
        # Declared-or-not, an absent dataset is not a failure: the definition is
        # rendered verbatim into the prompt and the solver copes with it.
        print(
            f"MM-Bench problem {problem_id} declares "
            f"{'dataset files that are not shipped' if declared_paths else 'no dataset'}"
            "; staging nothing.",
            flush=True,
        )
    metadata_path = Path(prepared["run_dir"]) / "meta" / "run.json"
    metadata = workflow.workflow_evolution.read_json(metadata_path, {})
    metadata.update(
        {
            "benchmark": "mmbench",
            "mmbench_problem_file": str(
                (Path(mmbench_root).resolve() / "problem" / f"{problem_id}.json")
            ),
            "mmbench_dataset_source": str(source_root) if source_root.is_dir() else "",
            "mmbench_declared_dataset_paths": declared_paths,
        }
    )
    workflow.workflow_evolution.write_json(metadata_path, metadata)
    return prepared


def write_added_content_without_baseline(run_dir: Path) -> Path:
    """Record what the exchange changed when there is nothing to diff against.

    The other arm derives this artifact from a diff, which a run that starts from
    nothing cannot do.  The run's own account of the exchange is the remaining
    evidence of what the reply moved, so it is carried through unchanged instead
    of being recomputed.
    """
    results_dir = Path(run_dir) / "output" / "results"
    evidence_path = results_dir / "interaction_evidence.md"
    if not evidence_path.is_file():
        raise FileNotFoundError(
            f"Cannot record interaction-attributed content without {evidence_path}"
        )
    output_path = results_dir / "interaction_added_content.md"
    output_path.write_text(
        "\n".join(
            [
                "# Interaction-Attributed Content",
                "",
                "This arm starts from the problem statement alone, so there is",
                "nothing to diff against. The run's own record of the exchange is",
                "reproduced below; treat the reported change as its account of the",
                "work, not as a controller-computed diff.",
                "",
                evidence_path.read_text(encoding="utf-8", errors="replace").strip(),
                "",
            ]
        ),
        encoding="utf-8",
    )
    return output_path


def run_solution_only_check(prepared: dict) -> Path:
    """Validate a run that starts from nothing: report, evidence, one real reply.

    The other arm's check compares the final report with the plan it was handed.
    There is no such plan here, so the check verifies what this arm's contract
    actually requires -- a non-empty report, the interaction evidence, and at
    least one successful expert reply, which is what makes the run a
    consultation rather than a silent one.
    """
    output_dir = Path(prepared["output_dir"])
    results_dir = output_dir / "results"
    checks: list[dict] = []

    def require_text(relative: str) -> str:
        path = output_dir / relative
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            raise RuntimeError(f"Cannot read UTF-8 artifact {relative}: {error}") from error
        if not text.strip():
            raise RuntimeError(f"Required artifact is empty: {relative}")
        if "\x00" in text:
            raise RuntimeError(f"NUL bytes detected in text artifact: {relative}")
        checks.append({"check": "utf8_nonempty", "path": relative, "passed": True})
        return text

    base.ensure_planning_interaction_evidence(output_dir)
    solution = require_text("results/solution_report.md")
    require_text("results/interaction_evidence.md")
    if workflow.substantive.has_expert_interaction_impact_section(solution):
        raise RuntimeError(
            "Final report must not contain an 'Expert Interaction Impact' section"
        )
    checks.append({"check": "expert_impact_section_absent", "passed": True})
    if not any(
        payload.get("ok") is True and str(payload.get("answer", "")).strip()
        for payload in (
            workflow.workflow_evolution.read_json(path, {})
            for path in sorted(
                (output_dir / "logs" / "operator_feedback").glob("expert_reply_*.json")
            )
        )
    ):
        raise RuntimeError("No successful expert reply is available")
    checks.append({"check": "successful_expert_reply", "passed": True})
    output_path = results_dir / "refinement_validation.json"
    workflow.workflow_evolution.write_json(
        output_path,
        {
            "generated_at": workflow.substantive.now(),
            "generated_by": "python_controller",
            "execution_count": 1,
            "checks": checks,
            "passed": True,
        },
    )
    return output_path


# Captured before main() rebinds the launcher's name: calling it through the
# module attribute afterwards would call this function back.
_ORIGINAL_SOLVER_PROMPT = base.build_interactive_solver_prompt
_ORIGINAL_FIXED_INITIAL_WORKFLOW = base.fixed_initial_workflow


def build_from_scratch_solver_prompt(workflow_value: dict, include_interaction: bool = True) -> str:
    """The sibling launcher's prompt, with no plan section, plus the note."""
    return _ORIGINAL_SOLVER_PROMPT(
        workflow_value,
        include_interaction=include_interaction,
        include_draft=False,
        interaction_note=INTERACTION_PROPORTIONALITY_NOTE,
    )


def patch_sibling_launcher() -> None:
    """Rebind the sibling launcher's plan hooks to this arm's from-scratch ones.

    Separate from :func:`main` so another arm can lay its own hook on top of the
    same launcher without restating this list -- and so a test can check the
    composed chain without starting an experiment.
    """
    # MM-Bench preparation is wired as `partial(support.<name>, root)`, so the
    # name is patched on the support module rather than in the launcher.
    support.prepare_mmbench_from_planning_draft = prepare_mmbench_from_evidence
    base.fixed_initial_workflow = fixed_initial_workflow
    base.SOLVER_SOURCE_CONTEXT = "from the problem statement alone"
    base.SOLVER_START_CONTEXT = "starts from the problem statement alone"
    base.prepare_from_planning_draft = prepare_from_evidence
    base.build_interactive_solver_prompt = build_from_scratch_solver_prompt
    base.write_planning_draft_added_content = write_added_content_without_baseline
    base.run_planning_draft_solution_check = run_solution_only_check


def main() -> None:
    """Rebind the sibling launcher's plan hooks, then run it unchanged."""
    patch_sibling_launcher()

    print(
        "Interaction-workflow evolution from scratch: the solver is handed the "
        "problem statement and the task's pre-gathered evidence.",
        flush=True,
    )
    base.main()


if __name__ == "__main__":
    main()
