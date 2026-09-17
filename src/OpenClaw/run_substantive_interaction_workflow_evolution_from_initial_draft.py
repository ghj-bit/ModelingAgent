"""Evolve expert-interaction workflows that solve from planning ``draft.md`` files.

This is intentionally separate from the clean-baseline refinement launcher. It
starts each Solver from a planning blueprint, not from an inherited completed
solution report, and supplies two planning-derived initial workflows.
"""

from __future__ import annotations

import argparse
import copy
import difflib
import json
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

try:
    from . import run_substantive_interaction_workflow_evolution as workflow
    from . import run_substantive_interaction_workflow_evolution_from_clean_baseline as clean
except ImportError:
    import run_substantive_interaction_workflow_evolution as workflow
    import run_substantive_interaction_workflow_evolution_from_clean_baseline as clean


REPO_ROOT = Path(__file__).resolve().parents[2]
# These are default source experiments. Their task IDs are discovered from
# completed draft artifacts at runtime rather than duplicated here.
PLANNING_DRAFT_TRAIN_ROOT = (
    REPO_ROOT
    / "openclaw_experiments"
    / "interaction_strategy_clean_baseline_initial_draft_train_20260916_202307"
)
PLANNING_DRAFT_VALIDATION_ROOT = (
    REPO_ROOT
    / "openclaw_experiments"
    / "interaction_strategy_clean_baseline_initial_draft_val_20260916_211801"
)
TRAIN_PROBLEMS: list[str] = []
VALIDATION_PROBLEMS: list[str] = []
DEFAULT_INITIAL_DRAFT_TRAIN_BATCH_SIZE = 4
INTERACTION_WORKFLOW_PLACEHOLDER = "{{INTERACTION_WORKFLOW}}"
DRAFT_PATH_PLACEHOLDER = "{{DRAFT_PATH}}"

INITIAL_STRATEGIC_UNCERTAINTY_POLICY = """# Human Expert Interaction

## Principle

The agent should solve the modeling problem autonomously.

Human feedback is only used for resolving high-impact strategic decisions that cannot be solved through standard modeling knowledge and self-analysis.

---

## Trigger Conditions

Request expert feedback only when ALL conditions hold:

1. Multiple feasible strategies remain.
2. The choice may change the modeling direction or conclusions.
3. The uncertainty cannot be resolved autonomously.
4. Expert feedback can produce a clear decision.

Do NOT request feedback for:

- implementation, coding, debugging;
- parameter tuning;
- derivations;
- computation or routine validation.

Maximum interactions: 1.

If multiple uncertainties exist, select the highest-impact one.

---

## Interaction Workflow

When requesting feedback, provide:

- current problem understanding and modeling stage;
- key strategic uncertainty and its impact;
- candidate strategies with trade-offs.

Ask the expert to classify suggestions as:

- **Required**: necessary for the original objective;
- **Optional**: extensions or improvements.

Only apply Required suggestions to the core model.

After feedback:

- update the strategy if necessary;
- evaluate feasibility and cost;
- continue autonomously.

Freeze the modeling scope after applying feedback. Treat new issues as assumptions, limitations, or sensitivity analysis.

---

## Interaction Termination

Terminate interaction when:

- the strategic uncertainty is resolved;
- the modeling direction is determined;
- remaining tasks can be completed autonomously."""

INITIAL_STRATEGIC_CHECKPOINT_POLICY = """# Human Expert Interaction

## Principle

The agent should complete the modeling process independently while using human feedback as a strategic alignment mechanism at predefined modeling checkpoints.

Human feedback is used to validate critical modeling assumptions, problem formulation, and overall solution direction before irreversible modeling decisions are made.

Human interaction should prevent major deviations in modeling objectives rather than solve routine modeling tasks or technical details.

---

## Trigger Conditions

Request expert feedback at predefined strategic checkpoints:

1. After initial problem understanding and requirement analysis.
2. Before selecting the final modeling framework or paradigm.
3. Before introducing major assumptions that significantly affect the solution.
4. Before executing a modeling pipeline with substantial downstream impact.

Do NOT request feedback for:

- implementation, coding, debugging;
- parameter tuning;
- mathematical derivations;
- computation or routine validation;
- minor assumption adjustments.

Maximum interactions: 1.

If multiple checkpoints are reached, select the earliest checkpoint with the highest potential impact on the final modeling outcome.

---

## Interaction Workflow

When requesting feedback, provide:

- current understanding of the problem and modeling objectives;
- current modeling stage and planned next steps;
- key decisions requiring strategic alignment;
- possible directions with advantages, limitations, and expected consequences.

Ask the expert to provide:

- **Confirmation**: whether the current direction is consistent with the objective;
- **Correction**: necessary changes to assumptions, formulation, or framework;
- **Suggestion**: optional improvements or extensions.

Only apply Confirmation and Correction to the core modeling process.

Optional suggestions should only be considered if they do not expand the original modeling scope.

After feedback:

- revise the modeling strategy if required;
- record confirmed assumptions and decisions;
- continue the remaining modeling process autonomously.

Once the strategic direction is confirmed, do not reopen the same decision unless new evidence fundamentally invalidates the assumption.

---

## Interaction Termination

Terminate interaction when:

- the strategic direction has been confirmed;
- critical assumptions have been validated;
- the remaining modeling process can proceed autonomously."""

_active_experiment: Path | None = None
_draft_train_root: Path | None = None
_draft_validation_root: Path | None = None
_initialize_only = False

_original_prepare_refinement = workflow.substantive.prepare_refinement_validation_problem
_original_runtime_args = workflow.substantive.runtime_args
_original_parse_args = workflow.parse_args
_original_load_cpe_split = workflow.load_cpe_split
_original_baseline_report_root = workflow.substantive.BASELINE_REPORT_ROOT
_original_default_problems = workflow.substantive.DEFAULT_PROBLEMS
_original_resolve_baseline_report = workflow.substantive.resolve_baseline_report
_missing = object()
_original_baseline_report_matches = getattr(
    workflow.substantive, "baseline_report_matches_problem", _missing
)
_original_experiment_path = workflow.experiment_path
_original_build_refinement_prompt = workflow.build_workflow_refinement_prompt
_original_build_cpe_prompt = workflow.build_cpe_workflow_evolution_prompt
_original_initial_population = workflow.initial_strategy_population
_original_validate_workflow = workflow.validate_workflow
_original_ensure_original_scores = workflow.ensure_cpe_original_report_scores
_original_execute_cpe_evaluation = workflow.execute_cpe_evaluation
_original_utility_basis = workflow.CPE_UTILITY_BASIS
_original_cost_weight = workflow.DEFAULT_CPE_COST_PENALTY_WEIGHT
_original_latency_cost_weight = workflow.DEFAULT_CPE_LATENCY_COST_WEIGHT
_original_min_rounds = workflow.MIN_CPE_EVOLUTION_ROUNDS
_original_max_exchanges = workflow.MAX_WORKFLOW_EXCHANGES
_original_collapse_initial_parents = workflow.CPE_COLLAPSE_INITIAL_PARENTS
_original_run_collapsed_initial_parents = (
    workflow.run_cpe_collapsed_initial_parent_evaluations
)
_original_write_interaction_added_content = (
    workflow.substantive.write_interaction_added_content
)
_original_run_consolidated_refinement_check = (
    workflow.substantive.run_consolidated_refinement_check
)


def parse_planning_draft_sources() -> argparse.Namespace:
    """Consume this launcher's source arguments before the shared parser runs."""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--planning-draft-train-root", type=Path)
    parser.add_argument("--planning-draft-validation-root", type=Path)
    values, remainder = parser.parse_known_args(sys.argv[1:])
    sys.argv = [sys.argv[0], *remainder]
    return values


def load_current_draft_split(_path: Path) -> tuple[list[str], list[str]]:
    return list(TRAIN_PROBLEMS), list(VALIDATION_PROBLEMS)


def run_initial_draft_parent_evaluations(
    experiment: Path,
    initial_problem_ids: list[str],
    initial_population: list[dict],
    fixed_rubric: dict,
    problems: dict,
    run_args,
    args,
    state: dict,
    original_scores: dict[str, dict],
) -> None:
    """Validate seed policies in round 0, then train them in round 1."""
    if len(initial_population) != workflow.CPE_TRAINING_PARENT_COUNT:
        raise ValueError("Initial-draft CPE initialization requires two seed workflows")

    initialization_mode = "round_0_validation_then_round_1_training"
    saved_mode = state.get("initialization_mode")
    if saved_mode not in (None, initialization_mode):
        raise ValueError(
            "This experiment was created with a different CPE initialization mode; "
            "start a new experiment directory instead of resuming it."
        )
    state["initialization_mode"] = initialization_mode
    validation_problems = [str(item) for item in state["validation_problems"]]

    workflow.ensure_cpe_baseline_reports(
        experiment,
        validation_problems,
        run_args,
        Path(args.baseline_report_root),
    )
    original_scores.update(
        workflow.ensure_cpe_original_report_scores(
            experiment, validation_problems, run_args
        )
    )
    parent_validation_results: list[dict | None] = [
        None
    ] * workflow.CPE_TRAINING_PARENT_COUNT
    print(
        "Running the two initial parent validations in parallel in CPE round 0",
        flush=True,
    )
    with ThreadPoolExecutor(
        max_workers=workflow.CPE_TRAINING_PARENT_COUNT
    ) as executor:
        futures = {
            executor.submit(
                workflow.execute_cpe_evaluation,
                experiment,
                0,
                f"initial_validation_parent_{parent_rank}",
                "validation",
                validation_problems,
                workflow.without_removed_workflow_fields(parent),
                fixed_rubric,
                problems,
                run_args,
                args.enforce_substantive_interaction_gate,
                original_scores,
            ): parent_rank
            for parent_rank, parent in enumerate(initial_population, start=1)
        }
        for future in as_completed(futures):
            parent_rank = futures[future]
            result, failures = future.result()
            if failures:
                raise RuntimeError(
                    f"{len(failures)} round-0 initial parent validation run(s) "
                    "failed the substantive gate"
                )
            parent_validation_results[parent_rank - 1] = result
    parent_validation_results = [
        result for result in parent_validation_results if result is not None
    ]
    if len(parent_validation_results) != workflow.CPE_TRAINING_PARENT_COUNT:
        raise RuntimeError("Round-0 initial parent validation did not produce two results")

    validation_champion = max(
        parent_validation_results,
        key=lambda result: (float(result["utility"]), str(result["workflow_id"])),
    )
    state["initial_parent_validation_results"] = copy.deepcopy(
        parent_validation_results
    )
    state["best_policy"] = {
        "source_round": 0,
        "source_phase": "initial_validation_parent",
        "workflow_id": validation_champion["workflow_id"],
        "workflow": workflow.without_removed_workflow_fields(
            validation_champion["workflow"]
        ),
        "validation_utility": float(validation_champion["utility"]),
        "utility_basis": workflow.CPE_UTILITY_BASIS,
    }
    state["updated_at"] = workflow.now()
    workflow.workflow_evolution.write_json(workflow.cpe_state_path(experiment), state)

    parent_train_results: list[dict | None] = [
        None
    ] * workflow.CPE_TRAINING_PARENT_COUNT
    print(
        "Running the two initial training-parent workflows in parallel in CPE round 1",
        flush=True,
    )
    with ThreadPoolExecutor(
        max_workers=workflow.CPE_TRAINING_PARENT_COUNT
    ) as executor:
        futures = {
            executor.submit(
                workflow.execute_cpe_evaluation,
                experiment,
                1,
                f"initial_train_parent_{parent_rank}",
                "train",
                initial_problem_ids,
                workflow.without_removed_workflow_fields(parent),
                fixed_rubric,
                problems,
                run_args,
                args.enforce_substantive_interaction_gate,
                original_scores,
            ): parent_rank
            for parent_rank, parent in enumerate(initial_population, start=1)
        }
        for future in as_completed(futures):
            parent_rank = futures[future]
            result, failures = future.result()
            if failures:
                raise RuntimeError(
                    f"{len(failures)} round-1 initial training-parent run(s) "
                    "failed the substantive gate"
                )
            parent_train_results[parent_rank - 1] = result
    parent_train_results = [
        result for result in parent_train_results if result is not None
    ]
    if len(parent_train_results) != workflow.CPE_TRAINING_PARENT_COUNT:
        raise RuntimeError("Round-1 initial parent training did not produce two results")

    state["initial_parent_train_results"] = copy.deepcopy(parent_train_results)
    state["initial_seed_train"] = [
        {
            "round": 1,
            "workflow_id": result["workflow_id"],
            "train_utility": float(result["utility"]),
        }
        for result in parent_train_results
    ]
    state["training_elites"] = workflow.select_cpe_training_elites(
        parent_train_results
    )
    best_train = state["training_elites"][0]
    state["current_policy"] = {
        **copy.deepcopy(best_train),
        "train_utility": float(best_train["selection_utility"]),
        "utility_basis": workflow.CPE_UTILITY_BASIS,
    }
    state["updated_at"] = workflow.now()
    workflow.workflow_evolution.write_json(workflow.cpe_state_path(experiment), state)


def discover_planning_draft_problem_ids(root: Path) -> list[str]:
    """Return completed planner IDs, preserving the source experiment's order."""
    problem_ids: set[str] = set()
    for draft in root.glob("**/output/results/draft.md"):
        if not draft.read_text(encoding="utf-8", errors="replace").strip():
            continue
        metadata = workflow.workflow_evolution.read_json(
            draft.parents[2] / "meta" / "run.json", {}
        )
        problem_id = metadata.get("problem_id")
        if isinstance(problem_id, str) and problem_id.strip():
            problem_ids.add(problem_id)
    if not problem_ids:
        raise FileNotFoundError(f"No non-empty output/results/draft.md files found under {root}")
    config = workflow.workflow_evolution.read_json(root / "runs" / "config.json", {})
    configured = config.get("validation_problems", [])
    if isinstance(configured, list):
        missing = [
            str(problem_id)
            for problem_id in configured
            if str(problem_id) not in problem_ids
        ]
        if missing:
            raise FileNotFoundError(
                f"Configured planning drafts missing under {root}: "
                + ", ".join(missing)
            )
        ordered = [str(problem_id) for problem_id in configured]
    else:
        ordered = []
    ordered.extend(sorted(problem_ids - set(ordered)))
    return ordered


def source_root_for_problem(problem_id: str) -> Path:
    if problem_id in TRAIN_PROBLEMS and _draft_train_root is not None:
        return _draft_train_root
    if problem_id in VALIDATION_PROBLEMS and _draft_validation_root is not None:
        return _draft_validation_root
    raise ValueError(
        f"No planning-draft root configured for {problem_id}. Supply the matching "
        "--planning-draft-train-root or --planning-draft-validation-root."
    )


def resolve_planning_draft(problem_id: str, _unused_root: Path) -> Path:
    """Resolve one non-empty draft.md by its controller-authored problem metadata."""
    # The shared engine validates source artifacts before it branches for
    # --initialize-only. No task is executed in that mode, so an existing
    # placeholder avoids requiring draft roots merely to materialize seeds.
    if _initialize_only:
        return Path(__file__).resolve()
    root = source_root_for_problem(problem_id)
    candidates = []
    for draft in root.glob("**/output/results/draft.md"):
        metadata_path = draft.parents[2] / "meta" / "run.json"
        metadata = workflow.workflow_evolution.read_json(metadata_path, {})
        if (
            metadata.get("problem_id") == problem_id
            and draft.read_text(encoding="utf-8", errors="replace").strip()
        ):
            candidates.append(draft)
    if not candidates:
        raise FileNotFoundError(
            f"No non-empty planning draft.md for {problem_id} under {root}"
        )
    return max(candidates, key=lambda path: (path.stat().st_mtime_ns, str(path)))


def planning_draft_matches_problem(problem_id: str, draft: Path) -> bool:
    expected_root = source_root_for_problem(problem_id).resolve()
    try:
        Path(draft).resolve().relative_to(expected_root)
    except ValueError:
        return False
    metadata = workflow.workflow_evolution.read_json(
        Path(draft).parents[2] / "meta" / "run.json", {}
    )
    return metadata.get("problem_id") == problem_id


def interaction_workflow_block(workflow_value: dict) -> str:
    """Render every seed or evolved workflow as ordinary Markdown prose."""
    name = str(workflow_value.get("name", "Interaction workflow"))
    purpose = str(workflow_value.get("purpose", "")).strip()
    actions = list(workflow_value.get("actions", []))
    max_exchanges = int(workflow_value.get("max_exchanges", 1))
    stop_condition = str(workflow_value.get("stop_condition", "")).strip()
    policy_text = str(workflow_value.get("policy_text", "")).strip()
    if policy_text:
        lines = policy_text.splitlines()
        lines.append("")
    else:
        lines = [
            "# Human Expert Interaction",
            "",
            f"## {name}",
            "",
            purpose,
            "",
            "## Interaction Workflow",
            "",
        ]
        for index, action in enumerate(actions, start=1):
            lines.extend(
                [
                    f"### Step {index}",
                    "",
                    str(action["rule"]),
                    "",
                ]
            )
    lines.extend(
        [
            f"Maximum expert exchanges: **{max_exchanges}**.",
            "",
            f"Stop condition: {stop_condition}",
            "",
            "### How to request expert feedback",
            "",
            "When a step requests expert feedback:",
            "",
            "1. Set `N` to the exchange number, starting at 1 and increasing by one.",
            "2. Write only the qualitative question to "
            "`{{OPERATOR_FEEDBACK_DIR}}/expert_question_N.md`.",
            "3. Run this command once in the foreground:",
            "",
            f'`python "{{{{OUTPUT_DIR}}}}/code/wait_for_expert_reply.py" '
            f'--request "{{{{OPERATOR_FEEDBACK_DIR}}}}/expert_request_N.json" '
            f'--reply "{{{{OPERATOR_FEEDBACK_DIR}}}}/expert_reply_N.json" '
            f'--timeout {workflow.substantive.EXPERT_REQUEST_TIMEOUT:.0f}`',
            "",
            "4. Read the returned expert reply, apply it as required by the current "
            "step, and then continue to the next step.",
            "",
            "The controller owns the request and reply files. Do not edit them, poll "
            "for them, or retry the command. Every later question must build on an "
            f"earlier reply. Follow the stop condition and never exceed {max_exchanges} "
            "expert interaction(s).",
            "",
        ]
    )
    return "\n".join(lines)


def policy_text_for_evolution(workflow_value: dict) -> str:
    """Render policy behavior without exposing internal graph field names."""
    policy_text = str(workflow_value.get("policy_text", "")).strip()
    if policy_text:
        return policy_text
    lines = [
        f"### {workflow_value.get('name', 'Interaction policy')}",
        "",
        str(workflow_value.get("purpose", "")).strip(),
        "",
        "#### Interaction workflow",
        "",
    ]
    for index, action in enumerate(workflow_value.get("actions", []), start=1):
        lines.extend([f"Step {index}: {action.get('rule', '')}", ""])
    lines.extend(
        [
            f"Maximum expert interactions: {workflow_value.get('max_exchanges', 1)}.",
            "",
            f"Termination: {workflow_value.get('stop_condition', '')}",
        ]
    )
    return "\n".join(lines).strip()


def build_initial_draft_cpe_workflow_evolution_prompt(
    training_parents: list[dict],
    validation_champion: dict,
    patch_history: list[dict],
    dialogue_operators: dict | None = None,
) -> str:
    """Build policy evolution evidence without the retired operator catalogue."""
    del dialogue_operators
    del patch_history
    if len(training_parents) != workflow.CPE_TRAINING_PARENT_COUNT:
        raise ValueError(
            f"CPE workflow evolution requires {workflow.CPE_TRAINING_PARENT_COUNT} "
            "training parents"
        )
    workflow.assert_no_cpe_judge_evidence(training_parents)
    champion_workflow = validation_champion.get("workflow", {})
    evidence_parents = []
    for parent in training_parents:
        training_evidence = copy.deepcopy(parent.get("training_evidence", {}))
        training_evidence.pop("average_interaction_penalty", None)
        training_evidence.pop("interaction_cost_parameters", None)
        evidence_parent = {
            "parent_rank": parent.get("parent_rank"),
            "workflow_id": parent.get("workflow_id"),
            "interaction_policy": policy_text_for_evolution(
                parent.get("workflow", {})
            ),
            "net_utility_on_current_training_batch": parent.get(
                "net_utility_on_current_training_batch"
            ),
            "training_evidence": training_evidence,
        }
        evidence_parents.append(evidence_parent)
    evidence_bundle = {
        "training_parents": evidence_parents,
        "historical_validation_champion": {
            "workflow_id": champion_workflow.get("workflow_id"),
            "interaction_policy": policy_text_for_evolution(champion_workflow),
            "mean_net_utility": validation_champion.get("utility"),
        },
    }
    workflow.assert_no_cpe_judge_evidence(evidence_bundle)
    evidence_json = json.dumps(evidence_bundle, ensure_ascii=False, indent=2)
    return f"""Evolve one executable human-expert interaction policy for a modeling
agent that starts from a planning draft and otherwise solves autonomously.

The evidence JSON contains two parent policies. Each policy is stored as a complete
Markdown string in `interaction_policy`, alongside its sampled-task executions,
expert dialogues, report-change summaries, aggregate net utility, and interaction
cost. Compare how the parents define:

- when strategic expert feedback is required;
- what context and decision alternatives are presented to the expert;
- how the reply changes the subsequent modeling strategy;
- when interaction terminates and autonomous execution resumes.

Choose one evidence-based evolution mode:

- `crossover`: write one coherent text policy that combines compatible or
  complementary behavioral strengths from both parents;
- `mutation`: retain one parent as the textual base and make a focused behavioral
  revision when combining the policies would create redundancy, conflict, or
  unnecessary interaction.

Use both parents as evidence regardless of the selected mode. Evolve the policy's
behavior and wording directly; do not reconstruct an action graph or operator-based
workflow.

## Evolution evidence

The following single JSON object contains each interaction policy as a Markdown text
string, together with the parent utilities, every sampled task, complete expert-
interaction history, interaction-attributable report changes, interaction costs, the
validation-champion policy and utility. Treat each
`interaction_policy` value as the complete policy text; it is text stored in JSON, not
a nested JSON workflow definition.

```json
{evidence_json}
```

Analyze how each parent policy shaped when expert feedback was requested, what
strategic information was elicited, how the reply changed the subsequent modeling
work, and when interaction stopped. Use aggregate net utility and the sampled-task
interaction evidence as coarse fitness signals. Evolve a general interaction policy rather than any
task-specific model, parameter, method, or conclusion.

The evolved policy must preserve autonomous modeling: the agent owns all calculation,
implementation, external-data validation, simulation, debugging, and report writing.
Human feedback is limited to high-impact strategic judgment. Avoid repeated
confirmation of an already resolved decision, and state a clear interaction limit and
termination condition.

Return only one JSON object with these fields:

- `name`: concise policy name;
- `purpose`: the strategic role of human interaction;
- `interaction_policy`: the complete evolved policy as one Markdown text string,
  using the same Principle, Trigger Conditions, Interaction Workflow, and Interaction
  Constraints style as the parent policies;
- `maximum_expert_interactions`: a positive integer;
- `termination_condition`: a concise textual stopping rule;
- `evolution_mode`: exactly `crossover` or `mutation`;
- `changed_components`: a non-empty list describing the behavioral changes;
- `evolution_rationale`: why the selected mode and changes fit both parents' evidence.

Do not return `entry_action`, `actions`, `action_id`, `action_type`, operator names, or
a nested workflow graph. The value of `interaction_policy` must be policy prose stored
as a JSON string.
"""


def validate_workflow_with_inferred_start(workflow_value: dict) -> None:
    """Translate prose-policy output into the shared engine's internal graph."""
    interaction_policy = str(
        workflow_value.get("interaction_policy")
        or workflow_value.get("policy_text")
        or ""
    ).strip()
    if interaction_policy:
        workflow_value["policy_text"] = interaction_policy
    if not workflow_value.get("max_exchanges"):
        maximum = workflow_value.get("maximum_expert_interactions", 1)
        try:
            workflow_value["max_exchanges"] = int(maximum)
        except (TypeError, ValueError):
            workflow_value["max_exchanges"] = 1
    if not workflow_value.get("stop_condition"):
        termination = workflow_value.get("termination_condition", "")
        if isinstance(termination, list):
            termination = "; ".join(str(item) for item in termination)
        workflow_value["stop_condition"] = str(termination).strip()
    actions = workflow_value.get("actions")
    if not actions and interaction_policy:
        workflow_value["actions"] = [
            {
                "action_id": "apply_policy_trigger",
                "action_type": "agent_audit",
                "rule": "Apply the complete natural-language interaction policy below to decide whether and when strategic expert feedback is required.\n\n"
                + interaction_policy,
            },
            {
                "action_id": "request_strategic_feedback",
                "action_type": "expert_exchange",
                "rule": "When the interaction policy requires consultation, present the specified strategic context and request only the qualitative expert judgment defined by that policy.",
            },
            {
                "action_id": "integrate_strategic_feedback",
                "action_type": "agent_analysis",
                "rule": "Evaluate and apply the expert reply according to the interaction policy, then continue all technical modeling work autonomously.",
            },
            {
                "action_id": "close_policy_interaction",
                "action_type": "close",
                "rule": "Stop expert interaction at the stated limit or termination condition and complete the remaining modeling work autonomously.",
            },
        ]
        actions = workflow_value["actions"]
    actions = workflow_value.get("actions")
    if not workflow_value.get("entry_action") and isinstance(actions, list) and actions:
        first_action = actions[0]
        if isinstance(first_action, dict):
            workflow_value["entry_action"] = first_action.get("action_id")
    _original_validate_workflow(workflow_value)


def build_interactive_solver_prompt(workflow_value: dict) -> str:
    """Build the Planner-to-Solver prompt with a workflow insertion point."""
    template = f"""# ModelingBench Task — Interactive Modeling Solver Agent

You are an advanced mathematical modeling solver agent.

Your task is to solve the given modeling problem by following the provided
modeling plan draft and collaborating with a human expert when needed.

You are NOT starting from scratch.

A previous planning agent has generated a modeling blueprint (`draft.md`).

Your role is to:

1. Review the draft.
2. Refine the modeling strategy with human expert feedback.
3. Execute the modeling workflow.
4. Produce the final solution report.

---

# Inputs

## Problem

Problem ID: `{{{{PROBLEM_ID}}}}`

Title: `{{{{TITLE}}}}`

Source: `{{{{SOURCE}}}}`

Problem Statement:

{{{{QUESTION}}}}

---

## Planning Draft

A preliminary modeling blueprint is available at:

`{DRAFT_PATH_PLACEHOLDER}`

Read and analyze this file before starting. It provides planned assumptions,
candidate models, a data strategy, and validation ideas. Treat it as a starting
hypothesis. You may modify assumptions, model choices, implementation strategy,
and validation methods when improvements are justified.

---

# Source Restrictions

Do not search for, retrieve, consult, quote, imitate, or use an existing answer,
worked solution, contest paper, answer key, or prior report for this exact
problem. Do not search by the problem ID, title, distinctive problem wording, or
competition/year metadata to locate such material. If exact-problem solution
material is encountered incidentally, ignore it and do not use it.

External search is limited to at most 1-2 independent, authoritative empirical
facts needed for model parameters or validation. Those sources must be general
domain references, not solutions to this task. Derive the model, calculations,
code, results, and conclusions independently from the problem statement and
draft.md.

---

{INTERACTION_WORKFLOW_PLACEHOLDER}

---

# Required Workflow

1. Understand the complete problem and all requested deliverables.
2. State the necessary modeling assumptions.
3. Choose and formulate suitable models.
4. Search for at most 1-2 verifiable empirical data items that materially affect
   the model or validation, and record their sources and intended use.
5. Write and execute reproducible code when needed.
6. Validate and analyze the results, then answer every subproblem.
7. Produce the final report at the required path.

---

# Final Report Requirements

The report should contain:

1. Problem Background and Restatement
2. Modeling Assumptions
3. Data Description and Processing
4. Model Construction
5. Mathematical Formulation
6. Solution Process and Implementation
7. Results and Analysis
8. Validation and Sensitivity Analysis
9. Limitations and Improvements
10. Conclusions

Do not generate or include images.

---

# Workspace

Workspace: `{{{{OUTPUT_DIR}}}}`

Final report: `{{{{FINAL_REPORT}}}}`

Interaction evidence: `{{{{RESULTS_DIR}}}}/interaction_evidence.md`

Code: `{{{{CODE_DIR}}}}`

Results: `{{{{RESULTS_DIR}}}}`

Data: `{{{{DATA_DIR}}}}`

Logs: `{{{{LOGS_DIR}}}}`

Create directories when needed.

Record the expert question, expert reply, and how the reply affected the work in
`interaction_evidence.md`. Keep this evidence separate from the final report.

Start by reading draft.md and reviewing the proposed modeling plan.
"""
    if template.count(INTERACTION_WORKFLOW_PLACEHOLDER) != 1:
        raise RuntimeError("Interactive Solver prompt has an invalid workflow placeholder")
    return template.replace(
        INTERACTION_WORKFLOW_PLACEHOLDER, interaction_workflow_block(workflow_value), 1
    )


def initial_planning_workflows() -> list[dict]:
    """Use the two user-specified strategic policies as the initial population."""
    definitions = [
        {
            "name": "Strategic uncertainty interaction policy",
            "purpose": "Resolve one highest-impact strategic uncertainty only when it cannot be settled autonomously and expert feedback can produce a clear decision.",
            "policy_text": INITIAL_STRATEGIC_UNCERTAINTY_POLICY,
            "actions": [
                {
                    "action_id": "audit_strategic_uncertainty",
                    "action_type": "agent_audit",
                    "rule": "Solve autonomously. Request feedback only when all four conditions hold: multiple feasible strategies remain; the choice may change the modeling direction or conclusions; standard modeling knowledge and self-analysis cannot resolve it; and expert feedback can produce a clear decision. Never escalate implementation, coding, debugging, parameter tuning, derivations, computation, or routine validation. If several uncertainties qualify, select only the highest-impact one.",
                },
                {
                    "action_id": "request_required_optional_decision",
                    "action_type": "expert_exchange",
                    "rule": "Present the current problem understanding and modeling stage, the single highest-impact strategic uncertainty and its impact, and candidate strategies with trade-offs. Ask the expert to classify each suggestion as Required when necessary for the original objective or Optional when it is an extension or improvement.",
                },
                {
                    "action_id": "apply_required_guidance_and_freeze_scope",
                    "action_type": "agent_analysis",
                    "rule": "Evaluate the reply and the feasibility and cost of the guidance. Apply only Required suggestions to the core model, update the strategy when necessary, then freeze the modeling scope and continue autonomously. Treat new issues as assumptions, limitations, or sensitivity analysis rather than reopening or expanding the core scope.",
                },
                {
                    "action_id": "close_interaction",
                    "action_type": "close",
                    "rule": "Terminate when the strategic uncertainty is resolved, the modeling direction is determined, or the remaining tasks can be completed autonomously. Do not exceed one expert interaction.",
                },
            ],
            "max_exchanges": 1,
            "stop_condition": "Stop without interaction unless every trigger condition holds; otherwise stop after the single reply has resolved the strategic uncertainty and the scope has been frozen.",
        },
        {
            "name": "Strategic checkpoint alignment policy",
            "purpose": "Use one high-impact predefined checkpoint to confirm or correct critical assumptions, problem formulation, and solution direction before an irreversible modeling decision.",
            "policy_text": INITIAL_STRATEGIC_CHECKPOINT_POLICY,
            "actions": [
                {
                    "action_id": "select_strategic_checkpoint",
                    "action_type": "agent_audit",
                    "rule": "Request feedback only after initial problem and requirement analysis, before final framework selection, before introducing a major outcome-sensitive assumption, or before executing a pipeline with substantial downstream impact. If several checkpoints have been reached, select the earliest one with the highest potential impact. Never escalate implementation, coding, debugging, parameter tuning, mathematical derivations, computation, routine validation, or minor assumption adjustments.",
                },
                {
                    "action_id": "request_confirmation_correction_suggestion",
                    "action_type": "expert_exchange",
                    "rule": "Present the current problem understanding and objectives, modeling stage and planned next steps, decisions requiring strategic alignment, and possible directions with advantages, limitations, and expected consequences. Ask the expert to classify feedback as Confirmation of alignment, Correction necessary to assumptions, formulation, or framework, or Suggestion for an optional improvement or extension.",
                },
                {
                    "action_id": "apply_confirmations_and_corrections",
                    "action_type": "agent_analysis",
                    "rule": "Apply Confirmation and Correction to the core modeling process, revise the strategy when required, and record the confirmed assumptions and decisions. Consider Suggestions only when they do not expand the original scope, then continue the remaining modeling process autonomously.",
                },
                {
                    "action_id": "close_checkpoint",
                    "action_type": "close",
                    "rule": "Terminate after the strategic direction and critical assumptions are confirmed and the remaining process can proceed autonomously. Do not reopen the same decision unless new evidence fundamentally invalidates its assumption, and never exceed one interaction.",
                },
            ],
            "max_exchanges": 1,
            "stop_condition": "Stop after the single selected checkpoint has confirmed or corrected the strategic direction and critical assumptions; continue the remaining modeling process autonomously.",
        },
    ]
    population = []
    for value in definitions:
        validate_workflow_with_inferred_start(value)
        value["workflow_id"] = workflow.workflow_id(value)
        population.append(value)
    return population


def prepare_from_planning_draft(
    problem_id: str,
    problem: dict,
    prompt_path: Path,
    round_number: int,
    repetition: int,
    experiment: Path,
    args,
) -> dict:
    """Prepare a fresh Solver workspace containing only the prior planning draft."""
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
    # The shared evaluator resolves this source into args.baseline_reports before
    # calling this preparation hook; the legacy field name is retained for API
    # compatibility only.
    source = Path(args.baseline_reports[problem_id])
    draft_target = output_dir / "results" / "draft.md"
    if not prepared["recovered"] or not draft_target.is_file():
        shutil.copy2(source, draft_target)
    if not draft_target.read_text(encoding="utf-8", errors="replace").strip():
        raise RuntimeError(f"Planning draft is empty: {draft_target}")
    prompt_path = Path(prepared["prompt"])
    prompt = prompt_path.read_text(encoding="utf-8")
    resolved_draft = str(draft_target.resolve())
    if DRAFT_PATH_PLACEHOLDER in prompt:
        prompt_path.write_text(
            prompt.replace(DRAFT_PATH_PLACEHOLDER, resolved_draft),
            encoding="utf-8",
        )
    elif resolved_draft not in prompt:
        raise RuntimeError(
            "Interactive Solver prompt contains neither {{DRAFT_PATH}} nor its "
            "resolved planning-draft path"
        )
    metadata_path = Path(prepared["run_dir"]) / "meta" / "run.json"
    metadata = workflow.workflow_evolution.read_json(metadata_path, {})
    metadata.update(
        {
            "initial_draft_used": True,
            "initial_draft_source": str(source),
            "initial_draft_path": str(draft_target),
            "execution_mode": "expert_guided_planning_draft_solution",
        }
    )
    workflow.workflow_evolution.write_json(metadata_path, metadata)
    if prepared["recovered"]:
        ensure_planning_interaction_evidence(output_dir)
    return prepared


def write_planning_draft_added_content(run_dir: Path) -> Path:
    """Record solution additions relative to draft.md without an original-report copy."""
    results_dir = Path(run_dir) / "output" / "results"
    draft_path = results_dir / "draft.md"
    solution_path = results_dir / "solution_report.md"
    if not draft_path.is_file() or not solution_path.is_file():
        raise FileNotFoundError(
            f"Cannot compare missing draft/solution report under {results_dir}"
        )
    draft = draft_path.read_text(encoding="utf-8", errors="replace").splitlines()
    solution = solution_path.read_text(encoding="utf-8", errors="replace").splitlines()
    blocks = []
    for tag, _, _, start, end in difflib.SequenceMatcher(
        None, draft, solution, autojunk=False
    ).get_opcodes():
        if tag in {"insert", "replace"} and start != end:
            blocks.append((tag, solution[start:end]))
    lines = [
        "# Interaction-Attributed Added Content",
        "",
        "Generated programmatically by comparing `draft.md` with the final "
        "`solution_report.md`.",
        "",
    ]
    if not blocks:
        lines.extend(["No added or revised content was detected.", ""])
    for index, (change_type, content) in enumerate(blocks, start=1):
        lines.extend(
            [f"## Change {index} ({change_type})", "", *content, ""]
        )
    output_path = results_dir / "interaction_added_content.md"
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def ensure_planning_interaction_evidence(output_dir: Path) -> Path:
    """Build missing evidence from controller-owned completed exchanges."""
    output_dir = Path(output_dir)
    evidence_path = output_dir / "results" / "interaction_evidence.md"
    if evidence_path.is_file() and evidence_path.read_text(
        encoding="utf-8", errors="replace"
    ).strip():
        return evidence_path
    feedback_dir = output_dir / "logs" / "operator_feedback"
    exchanges = []
    for reply_path in sorted(feedback_dir.glob("expert_reply_*.json")):
        payload = workflow.workflow_evolution.read_json(reply_path, {})
        answer = str(payload.get("answer", "")).strip()
        if payload.get("ok") is not True or not answer:
            continue
        suffix = reply_path.stem.removeprefix("expert_reply_")
        question_path = feedback_dir / f"expert_question_{suffix}.md"
        question = (
            question_path.read_text(encoding="utf-8", errors="replace").strip()
            if question_path.is_file()
            else "Question text unavailable."
        )
        exchanges.append((suffix, question, answer))
    if not exchanges:
        return evidence_path
    lines = [
        "# Interaction Evidence",
        "",
        "Generated from the controller-owned expert exchange artifacts.",
        "",
    ]
    for suffix, question, answer in exchanges:
        lines.extend(
            [
                f"## Exchange {suffix}",
                "",
                "### Agent question",
                "",
                question,
                "",
                "### Expert reply",
                "",
                answer,
                "",
            ]
        )
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text("\n".join(lines), encoding="utf-8")
    return evidence_path


def run_planning_draft_solution_check(prepared: dict) -> Path:
    """Validate the planning draft and final Solver artifacts directly."""
    output_dir = Path(prepared["output_dir"])
    results_dir = output_dir / "results"
    checks = []

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

    ensure_planning_interaction_evidence(output_dir)
    draft = require_text("results/draft.md")
    solution = require_text("results/solution_report.md")
    require_text("results/interaction_evidence.md")
    if draft == solution:
        raise RuntimeError("Final report is byte-for-byte identical to draft.md")
    checks.append({"check": "draft_expanded_into_solution", "passed": True})
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


def runtime_args_with_immediate_agent_start(*args, **kwargs):
    run_args = _original_runtime_args(*args, **kwargs)
    run_args.pipeline_agent_start = True
    run_args.require_clean_task_workspace = True
    return run_args


def execute_cpe_evaluation_with_phase_concurrency(
    experiment: Path,
    round_number: int,
    phase: str,
    split_name: str,
    problem_ids: list[str],
    interaction_workflow: dict,
    fixed_rubric: dict,
    problems: dict,
    run_args,
    enforce_gate: bool,
    original_scores: dict[str, dict],
):
    """Use one immediately-started worker per task in the current CPE phase."""
    if not problem_ids:
        raise ValueError(f"CPE {split_name} phase has no problems")
    phase_args = copy.copy(run_args)
    phase_concurrency = len(problem_ids)
    phase_args.concurrency = phase_concurrency
    phase_args.retry_concurrency = phase_concurrency
    phase_args.judge_concurrency = phase_concurrency
    phase_args.pipeline_agent_start = True
    print(
        f"CPE {split_name} phase {phase}: problems={len(problem_ids)}, "
        f"agent concurrency={phase_concurrency}, immediate start enabled",
        flush=True,
    )
    return _original_execute_cpe_evaluation(
        experiment,
        round_number,
        phase,
        split_name,
        problem_ids,
        interaction_workflow,
        fixed_rubric,
        problems,
        phase_args,
        enforce_gate,
        original_scores,
    )


def parse_args_with_pool_defaults():
    args = _original_parse_args()

    def supplied(option: str) -> bool:
        return any(value == option or value.startswith(option + "=") for value in sys.argv[1:])

    if not supplied("--train-batch-size"):
        args.train_batch_size = DEFAULT_INITIAL_DRAFT_TRAIN_BATCH_SIZE
    if not supplied("--validation-size"):
        args.validation_size = len(VALIDATION_PROBLEMS)
    # CPE evaluations replace this base value with the size of their current
    # problem list: the sampled train batch or the complete validation pool.
    phase_concurrency = args.train_batch_size
    if not supplied("--concurrency"):
        args.concurrency = phase_concurrency
    if not supplied("--retry-concurrency"):
        args.retry_concurrency = phase_concurrency
    if not supplied("--judge-concurrency"):
        args.judge_concurrency = phase_concurrency
    return args


def experiment_path(value: str | None) -> tuple[Path, bool]:
    global _active_experiment
    if value:
        path = Path(value).resolve()
        _active_experiment = path
        return path, path.is_dir()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = REPO_ROOT / "openclaw_experiments" / f"interaction_workflow_initial_draft_solution_{stamp}"
    _active_experiment = path
    return path, False


def record_config() -> None:
    if _active_experiment is None:
        return
    path = _active_experiment / "config.json"
    config = workflow.workflow_evolution.read_json(path, {})
    if not config:
        return
    config.update(
        {
            "initial_draft_used": True,
            "initial_draft_source_roots": {
                "train": str(_draft_train_root) if _draft_train_root else None,
                "validation": str(_draft_validation_root) if _draft_validation_root else None,
            },
            "initial_draft_train_pool_size": len(TRAIN_PROBLEMS),
            "initial_draft_validation_pool_size": len(VALIDATION_PROBLEMS),
            "phase_agent_concurrency": {
                "train": "current_train_batch_size",
                "validation": "complete_validation_pool_size",
                "pipeline_agent_start": True,
            },
            "interaction_latency_cost_ignored": True,
            "solver_prompt": "interactive_modeling_solver_agent_from_planning_draft",
            "initial_workflows": [
                "strategic_uncertainty_interaction_policy",
                "strategic_checkpoint_alignment_policy",
            ],
            "initial_evaluation_schedule": {
                "round_0": "validate_both_initial_parents",
                "round_1": "train_both_parents_then_evolve_candidate",
                "round_1_parent_validation": False,
            },
        }
    )
    workflow.workflow_evolution.write_json(path, config)


def main() -> None:
    global _draft_train_root, _draft_validation_root, _initialize_only
    global TRAIN_PROBLEMS, VALIDATION_PROBLEMS
    sources = parse_planning_draft_sources()
    _initialize_only = "--initialize-only" in sys.argv[1:]
    _draft_train_root = (
        sources.planning_draft_train_root or PLANNING_DRAFT_TRAIN_ROOT
    ).resolve()
    _draft_validation_root = (
        sources.planning_draft_validation_root or PLANNING_DRAFT_VALIDATION_ROOT
    ).resolve()
    TRAIN_PROBLEMS = discover_planning_draft_problem_ids(_draft_train_root)
    VALIDATION_PROBLEMS = discover_planning_draft_problem_ids(
        _draft_validation_root
    )
    overlap = sorted(set(TRAIN_PROBLEMS) & set(VALIDATION_PROBLEMS))
    if overlap:
        raise ValueError(
            "Planning-draft train and validation pools overlap: "
            + ", ".join(overlap)
        )
    print(
        "Planning-draft pools: "
        f"train={len(TRAIN_PROBLEMS)}, validation={len(VALIDATION_PROBLEMS)}; "
        f"default train batch={DEFAULT_INITIAL_DRAFT_TRAIN_BATCH_SIZE}",
        flush=True,
    )

    workflow.load_cpe_split = load_current_draft_split
    workflow.parse_args = parse_args_with_pool_defaults
    workflow.substantive.BASELINE_REPORT_ROOT = _draft_train_root or REPO_ROOT
    workflow.substantive.DEFAULT_PROBLEMS = tuple(VALIDATION_PROBLEMS)
    workflow.substantive.resolve_baseline_report = resolve_planning_draft
    workflow.substantive.baseline_report_matches_problem = planning_draft_matches_problem
    workflow.substantive.prepare_refinement_validation_problem = prepare_from_planning_draft
    workflow.substantive.write_interaction_added_content = (
        write_planning_draft_added_content
    )
    workflow.substantive.run_consolidated_refinement_check = (
        run_planning_draft_solution_check
    )
    workflow.substantive.runtime_args = runtime_args_with_immediate_agent_start
    workflow.build_workflow_refinement_prompt = build_interactive_solver_prompt
    workflow.build_cpe_workflow_evolution_prompt = (
        build_initial_draft_cpe_workflow_evolution_prompt
    )
    workflow.initial_strategy_population = initial_planning_workflows
    workflow.validate_workflow = validate_workflow_with_inferred_start
    workflow.execute_cpe_evaluation = execute_cpe_evaluation_with_phase_concurrency
    workflow.CPE_UTILITY_BASIS = workflow.CPE_UTILITY_BASIS_ABSOLUTE_SCORE
    workflow.DEFAULT_CPE_COST_PENALTY_WEIGHT = 0.05
    workflow.DEFAULT_CPE_LATENCY_COST_WEIGHT = 0.0
    workflow.ensure_cpe_original_report_scores = lambda *_args, **_kwargs: {}
    workflow.MIN_CPE_EVOLUTION_ROUNDS = None
    workflow.MAX_WORKFLOW_EXCHANGES = None
    workflow.CPE_COLLAPSE_INITIAL_PARENTS = True
    workflow.run_cpe_collapsed_initial_parent_evaluations = (
        run_initial_draft_parent_evaluations
    )
    workflow.experiment_path = experiment_path
    isolated_config = previous_config = None
    try:
        if not _initialize_only:
            isolated_config, previous_config = clean.activate_subagent_enabled_openclaw_config()
        workflow.main(cpe_mode=True, compact_experiment_inputs=True, dialogue_operator_evolution=False)
    finally:
        workflow.load_cpe_split = _original_load_cpe_split
        workflow.parse_args = _original_parse_args
        workflow.substantive.BASELINE_REPORT_ROOT = _original_baseline_report_root
        workflow.substantive.DEFAULT_PROBLEMS = _original_default_problems
        workflow.substantive.resolve_baseline_report = _original_resolve_baseline_report
        if _original_baseline_report_matches is _missing:
            delattr(workflow.substantive, "baseline_report_matches_problem")
        else:
            workflow.substantive.baseline_report_matches_problem = _original_baseline_report_matches
        workflow.substantive.prepare_refinement_validation_problem = _original_prepare_refinement
        workflow.substantive.write_interaction_added_content = (
            _original_write_interaction_added_content
        )
        workflow.substantive.run_consolidated_refinement_check = (
            _original_run_consolidated_refinement_check
        )
        workflow.substantive.runtime_args = _original_runtime_args
        workflow.build_workflow_refinement_prompt = _original_build_refinement_prompt
        workflow.build_cpe_workflow_evolution_prompt = _original_build_cpe_prompt
        workflow.initial_strategy_population = _original_initial_population
        workflow.validate_workflow = _original_validate_workflow
        workflow.execute_cpe_evaluation = _original_execute_cpe_evaluation
        workflow.CPE_UTILITY_BASIS = _original_utility_basis
        workflow.DEFAULT_CPE_COST_PENALTY_WEIGHT = _original_cost_weight
        workflow.DEFAULT_CPE_LATENCY_COST_WEIGHT = _original_latency_cost_weight
        workflow.ensure_cpe_original_report_scores = _original_ensure_original_scores
        workflow.MIN_CPE_EVOLUTION_ROUNDS = _original_min_rounds
        workflow.MAX_WORKFLOW_EXCHANGES = _original_max_exchanges
        workflow.CPE_COLLAPSE_INITIAL_PARENTS = _original_collapse_initial_parents
        workflow.run_cpe_collapsed_initial_parent_evaluations = (
            _original_run_collapsed_initial_parents
        )
        workflow.experiment_path = _original_experiment_path
        _initialize_only = False
        record_config()
        if isolated_config is not None:
            clean.clean_baseline.remove_clean_openclaw_config(isolated_config, previous_config)


if __name__ == "__main__":
    main()
