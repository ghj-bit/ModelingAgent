"""Evolve multi-turn expert-interaction workflows under one fixed rubric."""

from __future__ import annotations

import argparse
import atexit
import copy
import difflib
import hashlib
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from . import baseline
    from . import run_evolution as workflow_evolution
    from . import run_interaction_rubric_evolution as interaction
    from . import run_substantive_interaction_experiment as substantive
except ImportError:
    import baseline
    import run_evolution as workflow_evolution
    import run_interaction_rubric_evolution as interaction
    import run_substantive_interaction_experiment as substantive


REPO_ROOT = Path(__file__).resolve().parents[2]
INITIAL_WORKFLOW_PATH = Path(__file__).with_name(
    "interaction_initial_workflow_v1.json"
)
DEFAULT_FIXED_RUBRIC_PATH = (
    REPO_ROOT
    / "openclaw_experiments"
    / "interaction_rubric_substantive_20260908_205735"
    / "workflows"
    / "round_4"
    / "rubric.json"
)
DEFAULT_CANDIDATE_SIMILARITY_THRESHOLD = 0.96
STAGNATION_ROUNDS_FOR_OPERATOR_EVOLUTION = 5
FIRST_STAGNATION_COUNTED_ROUND = 4
OPERATOR_SIMILARITY_THRESHOLD = 0.90
REPORT_CHANGE_SUMMARY_MAX_CHARS = 50
JUDGE_FEEDBACK_DIMENSIONS = (
    "analysis_groundedness",
    "modeling_groundedness",
)
ACTIVE_WORKFLOWS: dict[int, dict[str, Any]] = {}

# These are seed interaction mechanisms, not Python mutation operators. Each
# couples a distinct expert contribution to an agent-owned technical audit and
# validation loop.
INTERACTION_OPERATORS = {
    "assumption_audit": {
        "purpose": "Challenge the real-world plausibility of assumptions that materially control the conclusion.",
        "rule": "After the agent ranks the draft's high-impact assumptions, present the materially consequential weakly supported assumptions and their real-world meanings without defending them. The request may contain multiple distinct issues when they affect different parts of the conclusion. Ask the expert to challenge their plausibility, identify omitted conditions, or explain when they could fail. The expert supplies qualitative domain judgment; the agent owns every technical translation, calculation, and validation.",
        "output": "Reality-based challenges to high-impact modeling assumptions.",
    },
    "model_failure_mode": {
        "purpose": "Use expert challenge to expose real-world failure modes of dangerous technical weaknesses.",
        "rule": "After the agent audits equations, constraints, code, and their consistency, present the real-world implications of the dangerous unresolved technical weaknesses. The request may cover multiple independent weaknesses rather than forcing selection of only one. Ask the expert to attack those implications with plausible failure conditions or counterexamples. Do not ask the expert to inspect code or calculate; the agent must repair the technical model and test every repair independently.",
        "output": "Plausible real-world failure conditions tied to audited technical weaknesses.",
    },
    "data_parameter_boundary": {
        "purpose": "Ground the most influential and weakly evidenced parameter before recalibrating the model.",
        "rule": "After the agent identifies conclusion-sensitive parameters, parameter groups, or empirical claims with weak evidence, explain their distinct decision roles and ask the expert for qualitative real-world bounds, observable boundary conditions, and suitable authoritative evidence types. The request may cover multiple independent weak inputs. The expert must not invent numerical estimates. The agent must obtain external evidence when claims are externally verifiable, set defensible values or ranges, recalibrate, and compare conclusions.",
        "output": "Qualitative real-world boundaries and evidence plans for influential weak inputs.",
    },
}


def evolved_operator_registry_path(workflows_dir: Path) -> Path:
    return workflows_dir / "evolved_operators.json"


def load_evolved_operator_events(workflows_dir: Path) -> list[dict[str, Any]]:
    """Load persisted operator-evolution events for restart-safe continuation."""
    events = workflow_evolution.read_json(
        evolved_operator_registry_path(workflows_dir), []
    )
    if not isinstance(events, list):
        raise ValueError("evolved operator registry must be a JSON list")
    return [event for event in events if isinstance(event, dict)]


def available_dialogue_operators(workflows_dir: Path | None = None) -> dict[str, dict]:
    """Return seed operators plus every valid operator evolved after stagnation."""
    operators = copy.deepcopy(INTERACTION_OPERATORS)
    if workflows_dir is None:
        return operators
    for event in load_evolved_operator_events(workflows_dir):
        operator = event.get("operator")
        if not isinstance(operator, dict):
            continue
        name = str(operator.get("name", "")).strip()
        if not name:
            continue
        operators[name] = {
            key: operator[key]
            for key in ("purpose", "rule", "output")
            if key in operator
        }
    return operators


def initial_strategy_population() -> list[dict[str, Any]]:
    """Return three distinct audit-to-validation interaction workflows."""
    definitions = [
        {
            "name": "High-impact assumption audit workflow",
            "purpose": INTERACTION_OPERATORS["assumption_audit"]["purpose"],
            "entry_action": "rank_high_impact_assumptions",
            "actions": [
                {
                    "action_id": "rank_high_impact_assumptions",
                    "action_type": "agent_audit",
                    "rule": "List the assumptions that could materially change the model's principal conclusions. Rank them by decision impact and evidential weakness, retain the distinct high-risk assumptions that remain insufficiently justified, and do not force the audit to select only one. Exclude redundant assumptions from the same causal chain and do not assume that the inherited formulation is correct.",
                },
                {
                    "action_id": "expert_reality_challenge",
                    "action_type": "expert_exchange",
                    "rule": INTERACTION_OPERATORS["assumption_audit"]["rule"],
                },
                {
                    "action_id": "technical_translation",
                    "action_type": "agent_analysis",
                    "rule": "Translate every material expert challenge into explicit, falsifiable model alternatives or boundary scenarios. State which assumptions, equations, constraints, parameters, code paths, or decision criteria each translation affects; do not directly adopt an expert-supplied number or technical prescription.",
                },
                {
                    "action_id": "recompute_and_compare",
                    "action_type": "agent_validation",
                    "rule": "Implement the justified alternatives, rerun every affected computation, and compare them individually and jointly with the original formulation. Repair the model and revise the conclusions when the evidence warrants it; otherwise document the tested robustness boundaries.",
                },
                {
                    "action_id": "close_dialogue",
                    "action_type": "close",
                    "rule": "After the first validation pass, review the full assumption register again. End consultation only when the remaining high-risk assumptions either have been tested or do not require further expert judgment; otherwise use a second exchange for the unresolved independent issues and then integrate the supported consequences into the report.",
                },
            ],
            "max_exchanges": 2,
            "stop_condition": "Stop after all material challenges raised in the consultation have been translated and tested and a residual-risk review finds no independent high-risk assumption needing another expert reply, or after the second exchange followed by recomputation. Do not stop merely because the original conclusion survives.",
            "seed_operator": "assumption_audit",
        },
        {
            "name": "Model failure-mode repair workflow",
            "purpose": INTERACTION_OPERATORS["model_failure_mode"]["purpose"],
            "entry_action": "audit_model_implementation",
            "actions": [
                {
                    "action_id": "audit_model_implementation",
                    "action_type": "agent_audit",
                    "rule": "Inspect the mathematical formulation, units, constraints, algorithms, and executable code for internal consistency and agreement with the problem statement. Use targeted sanity or boundary checks to identify all unresolved weaknesses capable of invalidating material results, group redundant findings by causal chain, and retain the distinct high-risk weaknesses rather than selecting only one.",
                },
                {
                    "action_id": "expert_failure_attack",
                    "action_type": "expert_exchange",
                    "rule": INTERACTION_OPERATORS["model_failure_mode"]["rule"],
                },
                {
                    "action_id": "repair_model",
                    "action_type": "agent_analysis",
                    "rule": "Convert every material failure condition into a precise technical test. Correct all affected equations, constraints, algorithms, data transformations, or code implementations, and regenerate all dependent outputs rather than preserving an invalid inherited result.",
                },
                {
                    "action_id": "independent_regression_test",
                    "action_type": "agent_validation",
                    "rule": "Validate every repaired component and the integrated model with independent checks such as analytical special cases, a second implementation, invariant checks, or targeted regression and boundary tests. Compare old and repaired results and update the recommendation and confidence boundary accordingly.",
                },
                {
                    "action_id": "close_dialogue",
                    "action_type": "close",
                    "rule": "Re-audit the integrated model after the first repair pass. End consultation only when the remaining high-risk failure modes have been tested or need no further expert judgment; otherwise use a second exchange for unresolved independent failure modes before integrating the verified model and results into the report.",
                },
            ],
            "max_exchanges": 2,
            "stop_condition": "Stop after all material failure conditions raised in the consultation pass independent tests and a residual technical audit finds no independent high-risk issue needing another expert reply, or after the second exchange followed by integrated regression testing.",
            "seed_operator": "model_failure_mode",
        },
        {
            "name": "Data and parameter grounding workflow",
            "purpose": INTERACTION_OPERATORS["data_parameter_boundary"]["purpose"],
            "entry_action": "find_weak_sensitive_parameter",
            "actions": [
                {
                    "action_id": "find_weak_sensitive_parameter",
                    "action_type": "agent_audit",
                    "rule": "Trace the material conclusions to their data and parameters. Identify all influential parameters, parameter groups, or empirical claims with weak evidence, using targeted sensitivity checks when needed. Rank and group them by causal role without forcing the audit to retain only one quantity.",
                },
                {
                    "action_id": "expert_real_world_boundary",
                    "action_type": "expert_exchange",
                    "rule": INTERACTION_OPERATORS["data_parameter_boundary"]["rule"],
                },
                {
                    "action_id": "verify_external_evidence",
                    "action_type": "agent_research",
                    "rule": "When the selected parameters or claims are externally verifiable, consult one or two authoritative sources per distinct evidence decision and record their provenance. Reconcile source scope, units, population, and time period with the model; do not treat the expert reply itself as empirical verification.",
                },
                {
                    "action_id": "recalibrate_and_compare",
                    "action_type": "agent_validation",
                    "rule": "Recalibrate every supported parameter or defensible joint range, rerun affected analyses, and compare the updated outputs and decisions individually and jointly with the original. Revise the model, recommendation, limitations, and confidence bounds wherever the comparison shows a material difference.",
                },
                {
                    "action_id": "close_dialogue",
                    "action_type": "close",
                    "rule": "After recalibration, repeat the sensitivity and evidence-gap review. End consultation only when the remaining influential weak inputs have been addressed or require no further expert judgment; otherwise use a second exchange for the unresolved independent parameter groups, then integrate only supported consequences into the report.",
                },
            ],
            "max_exchanges": 2,
            "stop_condition": "Stop after the material weak inputs raised in consultation have been externally verified when applicable and recalibrated, and a residual sensitivity review finds no independent high-risk input needing another expert reply, or after the second exchange followed by a documented joint comparison.",
            "seed_operator": "data_parameter_boundary",
        },
    ]
    population = []
    for workflow in definitions:
        workflow["evolution_operator"] = "initial_strategy"
        validate_workflow(workflow)
        workflow["workflow_id"] = workflow_id(workflow)
        population.append(workflow)
    return population


def optimizer_workflow(workflow: dict) -> dict:
    """Return an optimizer-only copy without excluded workflow attributes."""
    compact = copy.deepcopy(workflow)
    for key in (
        "purpose",
        "changed_components",
        "mutation_rationale",
        "crossover_rationale",
        "evolution_rationale",
        "parent_round",
        "parent_rounds",
        "secondary_parent_round",
    ):
        compact.pop(key, None)
    return compact


def load_seed_population(experiment: Path, resumed: bool, source: str | None) -> list[dict]:
    target = experiment / "initial_interaction_workflows.json"
    legacy = experiment / "initial_interaction_workflow.json"
    if target.is_file():
        population = workflow_evolution.read_json(target, [])
    elif resumed and legacy.is_file():
        population = [workflow_evolution.read_json(legacy, {})]
    elif source:
        value = workflow_evolution.read_json(Path(source).resolve(), {})
        population = value if isinstance(value, list) else [value]
    elif resumed:
        raise ValueError("Resumed experiment has no saved initial workflow; supply --initial-workflow")
    else:
        population = initial_strategy_population()
    if not isinstance(population, list) or not population:
        raise ValueError("Initial workflows must be a non-empty list")
    population = [without_removed_workflow_fields(item) for item in population]
    for item in population:
        validate_workflow(item)
        item["workflow_id"] = workflow_id(item)
    if len({item["workflow_id"] for item in population}) != len(population):
        raise ValueError("Initial workflows must have distinct behavior")
    workflow_evolution.write_json(target, population)
    if not legacy.exists():
        workflow_evolution.write_json(legacy, population[0])
    return population


def now() -> str:
    return datetime.now().isoformat()


def normalize_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip().lower()


def workflow_behavior(workflow: dict[str, Any]) -> dict[str, Any]:
    """Return behavior only, excluding labels and evolution prose."""
    actions = workflow.get("actions") or []
    action_ids = [str(item.get("action_id", "")) for item in actions]
    id_map = {value: f"action_{index}" for index, value in enumerate(action_ids, 1)}
    normalized_actions = []
    for action in actions:
        normalized_actions.append(
            {
                "action_id": id_map.get(
                    str(action.get("action_id", "")),
                    str(action.get("action_id", "")),
                ),
                "action_type": normalize_text(action.get("action_type")),
                "rule": normalize_text(action.get("rule")),
                "policy": action.get("policy"),
                "input_fields": action.get("input_fields"),
                "output_fields": action.get("output_fields"),
                "budget": action.get("budget"),
            }
        )
    return {
        "entry_action": id_map.get(
            str(workflow.get("entry_action", "")),
            str(workflow.get("entry_action", "")),
        ),
        "actions": normalized_actions,
        "max_exchanges": workflow.get("max_exchanges"),
        "stop_condition": normalize_text(workflow.get("stop_condition")),
    }


def without_removed_workflow_fields(workflow: dict[str, Any]) -> dict[str, Any]:
    """Return the current workflow schema, including when resuming an old run."""
    compact = copy.deepcopy(workflow)
    for field in (
        "transitions",
        "completion_output",
        "success_test",
        "parent_round",
        "parent_rounds",
        "secondary_parent_round",
        "mutation_rationale",
        "crossover_rationale",
    ):
        compact.pop(field, None)
    return compact


def workflow_id(workflow: dict[str, Any]) -> str:
    canonical = json.dumps(
        workflow_behavior(workflow), ensure_ascii=False, sort_keys=True
    )
    return "interaction_workflow_" + hashlib.sha1(
        canonical.encode("utf-8")
    ).hexdigest()[:12]


def workflow_similarity(left: dict[str, Any], right: dict[str, Any]) -> float:
    left_text = json.dumps(
        workflow_behavior(left), ensure_ascii=False, sort_keys=True
    )
    right_text = json.dumps(
        workflow_behavior(right), ensure_ascii=False, sort_keys=True
    )
    return difflib.SequenceMatcher(None, left_text, right_text).ratio()


def validate_workflow(workflow: dict[str, Any]) -> None:
    for field in ("name", "purpose", "stop_condition"):
        if len(str(workflow.get(field, "")).strip()) < 12:
            raise ValueError(f"interaction workflow has invalid {field}")
    for removed_field in ("transitions", "completion_output", "success_test"):
        if removed_field in workflow:
            raise ValueError(
                f"interaction workflow must not contain removed field {removed_field}"
            )
    max_exchanges = workflow.get("max_exchanges")
    if not isinstance(max_exchanges, int) or not 1 <= max_exchanges <= 3:
        raise ValueError("interaction workflow max_exchanges must be 1, 2, or 3")
    actions = workflow.get("actions")
    if not isinstance(actions, list) or not 2 <= len(actions) <= 8:
        raise ValueError("interaction workflow must contain two to eight actions")
    action_ids = []
    expert_actions = 0
    for action in actions:
        if not isinstance(action, dict):
            raise ValueError("interaction workflow contains a non-object action")
        action_id = str(action.get("action_id", "")).strip()
        action_type = str(action.get("action_type", "")).strip()
        rule = str(action.get("rule", "")).strip()
        if not action_id or not re.fullmatch(r"[a-z][a-z0-9_]*", action_id):
            raise ValueError(f"invalid workflow action_id: {action_id!r}")
        if len(action_type) < 3 or len(rule) < 20:
            raise ValueError(f"incomplete workflow action: {action_id}")
        action_ids.append(action_id)
        expert_actions += action_type == "expert_exchange"
    if len(action_ids) != len(set(action_ids)):
        raise ValueError("interaction workflow action IDs must be unique")
    if expert_actions < 1:
        raise ValueError("interaction workflow must contain an expert_exchange action")
    if workflow.get("entry_action") not in action_ids:
        raise ValueError("interaction workflow entry_action is not an action")
    if workflow.get("entry_action") != action_ids[0]:
        raise ValueError("interaction workflow entry_action must be its first action")


def load_initial_workflow() -> dict[str, Any]:
    workflow = workflow_evolution.read_json(INITIAL_WORKFLOW_PATH, {})
    validate_workflow(workflow)
    workflow["workflow_id"] = workflow_id(workflow)
    return workflow


def resolve_fixed_rubric_path(value: str | Path) -> Path:
    path = Path(value).resolve()
    if path.is_file():
        return path
    if path.is_dir():
        direct = path / "rubric.json"
        if direct.is_file():
            return direct
        if path.name.startswith("round_") and path.parent.name == "runs":
            candidate = path.parent.parent / "workflows" / path.name / "rubric.json"
            if candidate.is_file():
                return candidate
    raise FileNotFoundError(f"Fixed interaction rubric not found from: {path}")


def load_fixed_rubric(path: Path) -> dict[str, Any]:
    rubric = workflow_evolution.read_json(path, {})
    rubric.pop("attention_budget", None)
    rubric.pop("success_test", None)
    # Workflow experiments use their own compact rubric schema, including resume.
    for key in ("name", "purpose"):
        if len(str(rubric.get(key, "")).strip()) < 12:
            raise ValueError(f"fixed interaction rubric has invalid {key}")
    criteria = rubric.get("criteria")
    if not isinstance(criteria, list) or not 1 <= len(criteria) <= 4:
        raise ValueError("fixed interaction rubric must contain one to four criteria")
    for criterion in criteria:
        if not isinstance(criterion, dict) or any(
            len(str(criterion.get(key, "")).strip()) < 12
            for key in ("name", "rule", "positive_example", "negative_example")
        ):
            raise ValueError("fixed interaction rubric contains an incomplete criterion")
    if not str(rubric.get("rubric_id", "")).strip():
        rubric["rubric_id"] = interaction.rubric_id(rubric)
    return rubric


def workflow_nodes(results: list[dict]) -> list[dict]:
    return [
        node
        for node in results
        if isinstance(node.get("workflow"), dict) and node["workflow"].get("actions")
    ]


def evolution_evidence_nodes(results: list[dict]) -> list[dict]:
    """Keep all three seeds and a later global best."""
    nodes = workflow_nodes(results)
    initial = sorted(
        (
            node
            for node in nodes
            if node.get("evolution_operator") == "initial_strategy"
        ),
        key=lambda item: int(item["round"]),
    )[:3]
    best = max(
        nodes,
        key=lambda item: (float(item["utility"]), -int(item["round"])),
        default=None,
    )
    ordered = [*initial]
    if best is not None and int(best["round"]) not in {
        int(node["round"]) for node in initial
    }:
        ordered.append(best)

    selected = []
    seen_rounds = set()
    for node in ordered:
        round_number = int(node["round"])
        if round_number in seen_rounds:
            continue
        seen_rounds.add(round_number)
        selected.append(node)
    return selected


def summarize_workflow_judge_feedback(
    run: dict[str, Any], round_dir: Path, args
) -> dict[str, Any]:
    """Summarize only non-perfect analysis/modeling groundedness feedback."""
    try:
        from . import run_substantive_interaction_strategy_evolution as strategy
    except ImportError:
        import run_substantive_interaction_strategy_evolution as strategy

    focused_run = dict(run)
    focused_run["dimension_scores"] = {
        dimension: score
        for dimension, score in run.get("dimension_scores", {}).items()
        if dimension in JUDGE_FEEDBACK_DIMENSIONS
    }
    return strategy.summarize_nonperfect_judge_feedback(
        focused_run, round_dir, args
    )


def summarize_interaction_report_changes(
    run: dict[str, Any], round_dir: Path, args
) -> str:
    """Compress interaction-attributable report changes to at most 50 chars."""
    artifacts = {
        artifact["artifact_type"]: artifact["content"]
        for artifact in substantive.parent_artifacts(Path(run["run_dir"]))
    }
    changed_content = artifacts.get("interaction_added_content", "").strip()
    if not changed_content:
        return ""
    payload = json.dumps(
        {
            "expert_dialogue": artifacts.get("expert_interaction", ""),
            "interaction_evidence": artifacts.get("interaction_evidence", ""),
            "report_added_or_revised_content": changed_content,
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    summary_dir = round_dir / "interaction_report_change_summaries"
    summary_dir.mkdir(parents=True, exist_ok=True)
    cache_key = hashlib.sha256(
        (
            "interaction-report-change-summary-v1\0"
            + args.judge_feedback_model
            + "\0"
            + payload
        ).encode("utf-8")
    ).hexdigest()
    cache_path = summary_dir / f"{cache_key}.json"
    cached = workflow_evolution.read_json(cache_path, {})
    summary = cached.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        response = interaction.local.optimizer_response(
            {
                "model": args.judge_feedback_model,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "仅摘要由专家交互直接促成的最终报告新增或修改内容。"
                            "排除与专家回复无关的Agent自主审计、反思、常规补全和格式改写。"
                            "不评价优缺点，不补充输入外信息；最多50个字符。"
                            "仅返回JSON：{\"summary\":\"摘要\"}。"
                        ),
                    },
                    {"role": "user", "content": payload},
                ],
                "temperature": 0.1,
                "max_tokens": 200,
                "response_format": {"type": "json_object"},
            },
            args,
        )
        summary = response.get("summary") if isinstance(response, dict) else None
        if not isinstance(summary, str) or not summary.strip():
            raise RuntimeError("Interaction report-change summarization failed")
        summary = summary.strip()[:REPORT_CHANGE_SUMMARY_MAX_CHARS]
        workflow_evolution.write_json(
            cache_path,
            {
                "model": args.judge_feedback_model,
                "max_chars": REPORT_CHANGE_SUMMARY_MAX_CHARS,
                "summary": summary,
            },
        )
    return summary.strip()[:REPORT_CHANGE_SUMMARY_MAX_CHARS]


def summarize_workflow_run_evidence(
    run: dict[str, Any], round_dir: Path, args
) -> dict[str, Any]:
    """Produce the two compact LLM-derived inputs for one validation run."""
    return {
        "interaction_report_change_summary": summarize_interaction_report_changes(
            run, round_dir, args
        ),
        "judge_groundedness_weakness_summary": summarize_workflow_judge_feedback(
            run, round_dir, args
        ),
    }


def optimizer_evidence(
    selected_nodes: list[dict], problems: dict, round_dir: Path, args
) -> list[dict[str, Any]]:
    """Build workflow evidence with dialogue and compact report/Judge summaries."""
    problem_context = {
        item["problem_id"]: item
        for item in interaction.optimizer_problem_context(problems)
    }
    evidence = []
    summary_jobs: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for evidence_index, node in enumerate(selected_nodes, 1):
        validation_runs = []
        for run in node.get("problem_results", []):
            artifacts = optimizer_interaction_artifacts(Path(run["run_dir"]))
            run_evidence = {
                **problem_context[run["problem_id"]],
                "artifacts": artifacts,
            }
            summary_jobs.append((run, run_evidence))
            validation_runs.append(run_evidence)
        evidence.append(
            {
                "evidence_index": evidence_index,
                "round": node["round"],
                "average_utility": node["utility"],
                "workflow": optimizer_workflow(node["workflow"]),
                "validation_runs": validation_runs,
            }
        )
    if summary_jobs:
        worker_count = min(args.judge_feedback_concurrency, len(summary_jobs))
        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            futures = {
                executor.submit(
                    summarize_workflow_run_evidence,
                    run,
                    round_dir,
                    args,
                ): run_evidence
                for run, run_evidence in summary_jobs
            }
            for future in as_completed(futures):
                summaries = future.result()
                for field, summary in summaries.items():
                    if summary:
                        futures[future][field] = summary
    return evidence


def optimizer_interaction_artifacts(run_dir: Path) -> list[dict[str, Any]]:
    """Keep only the raw dialogue in optimizer evidence.

    ``interaction_evidence`` and ``interaction_receipt`` remain on disk for
    auditing and runtime checks. Raw report changes are represented separately
    by a 50-character interaction-attributable summary.
    """
    allowed_types = {"expert_interaction"}
    return [
        artifact
        for artifact in substantive.parent_artifacts(run_dir)
        if artifact.get("artifact_type") in allowed_types
    ]


def stagnation_window(
    results: list[dict], after_round: int = 0
) -> tuple[list[int], float]:
    """Return the trailing rounds that did not strictly improve the global best."""
    best = float("-inf")
    stagnant: list[int] = []
    for node in sorted(workflow_nodes(results), key=lambda item: int(item["round"])):
        utility = float(node["utility"])
        improved = utility > best + 1e-12
        best = max(best, utility)
        if (
            int(node["round"]) < FIRST_STAGNATION_COUNTED_ROUND
            or int(node["round"]) <= after_round
        ):
            continue
        if improved:
            stagnant = []
        else:
            stagnant.append(int(node["round"]))
    return stagnant, best


def validate_dialogue_operator(
    candidate: dict[str, Any], existing: dict[str, dict]
) -> dict[str, Any]:
    """Validate a novel qualitative information function returned by the optimizer."""
    if not isinstance(candidate, dict):
        raise ValueError("operator optimizer did not return a JSON object")
    name = str(candidate.get("name", "")).strip()
    if not re.fullmatch(r"[a-z][a-z0-9_]*", name):
        raise ValueError("evolved operator name must be lower snake_case")
    for key in ("purpose", "rule", "output", "mutation_rationale"):
        if len(str(candidate.get(key, "")).strip()) < 20:
            raise ValueError(f"evolved operator has invalid {key}")
    if name in existing:
        raise ValueError(f"dialogue operator already exists: {name}")
    candidate_text = normalize_text(
        " ".join(str(candidate[key]) for key in ("purpose", "rule", "output"))
    )
    for old_name, old in existing.items():
        old_text = normalize_text(
            " ".join(str(old.get(key, "")) for key in ("purpose", "rule", "output"))
        )
        similarity = difflib.SequenceMatcher(None, candidate_text, old_text).ratio()
        if similarity >= OPERATOR_SIMILARITY_THRESHOLD:
            raise ValueError(
                f"evolved operator is too similar to {old_name} "
                f"(similarity={similarity:.4f})"
            )
    return candidate


def build_operator_evolution_prompt(
    existing: dict[str, dict],
    evidence: list[dict[str, Any]],
) -> str:
    """Build the standalone dialogue-operator optimizer prompt."""
    return f"""Evolve one new human-expert dialogue operator for mathematical-
modeling report refinement. A dialogue operator is a distinct qualitative
information function used inside an interaction workflow; it is not a complete
workflow, scoring rubric, report section, or Python mutation operator.

Existing dialogue operators:
{json.dumps(existing, ensure_ascii=False, indent=2)}

Workflow validation evidence:
{json.dumps(evidence, ensure_ascii=False, indent=2)}

Create a genuinely different information function that could address a recurring
interaction-related weakness visible across the evidence. Consider every supplied
workflow evidence node rather than selecting a subset. Do not merely rename,
broaden, combine, or paraphrase an existing operator. State what the expert is
asked to contribute and keep calculations, implementation, simulation, external-
data validation, and final decisions with the modeling agent. Keep it general;
do not copy task-specific facts, parameters, methods, or conclusions.

Return only one JSON object with name, purpose, rule, output, and
mutation_rationale. The name must be lower snake_case. The rule must be directly
usable as an expert_exchange instruction. mutation_rationale must explain the
new information function and why existing operators did not provide it.
"""


def maybe_evolve_dialogue_operator(
    results: list[dict], workflows_dir: Path, args, problems: dict
) -> dict[str, Any] | None:
    """Persist one new operator whenever a fresh five-round plateau is reached."""
    events = load_evolved_operator_events(workflows_dir)
    last_trigger = max(
        (int(event.get("trigger_after_round", 0)) for event in events), default=0
    )
    stagnant, historical_best = stagnation_window(results, last_trigger)
    if len(stagnant) < STAGNATION_ROUNDS_FOR_OPERATOR_EVOLUTION:
        return None

    trigger_round = stagnant[-1]
    event_dir = workflows_dir / "operator_evolution" / f"after_round_{trigger_round}"
    event_dir.mkdir(parents=True, exist_ok=True)
    existing = available_dialogue_operators(workflows_dir)
    evidence_nodes = evolution_evidence_nodes(results)
    if not evidence_nodes:
        raise ValueError("cannot evolve a dialogue operator without workflow evidence")
    evidence = optimizer_evidence(evidence_nodes, problems, event_dir, args)
    operator_prompt_base = build_operator_evolution_prompt(existing, evidence)
    last_error: Exception | None = None
    for attempt in range(1, args.optimizer_retries + 1):
        retry = (
            "\nThe previous proposal was rejected. Produce a different information "
            f"function. Rejection: {last_error}\n"
            if last_error
            else ""
        )
        operator_attempt_prompt = operator_prompt_base + retry
        (event_dir / f"operator_prompt_attempt_{attempt}.md").write_text(
            operator_attempt_prompt, encoding="utf-8"
        )
        (event_dir / "operator_prompt.md").write_text(
            operator_attempt_prompt, encoding="utf-8"
        )
        try:
            candidate = interaction.local.optimizer_response(
                {
                    "model": args.opt_model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "Return one concise valid JSON dialogue operator.",
                        },
                        {"role": "user", "content": operator_attempt_prompt},
                    ],
                    "temperature": min(0.35 + 0.15 * (attempt - 1), 0.85),
                    "max_tokens": 1800,
                    "response_format": {"type": "json_object"},
                },
                args,
            )
            workflow_evolution.write_json(
                event_dir / f"operator_response_attempt_{attempt}.json", candidate
            )
            workflow_evolution.write_json(
                event_dir / "operator_response.json", candidate
            )
            candidate = validate_dialogue_operator(candidate, existing)
            semantic = json.dumps(
                {key: candidate[key] for key in ("name", "purpose", "rule", "output")},
                ensure_ascii=False,
                sort_keys=True,
            )
            candidate["operator_id"] = "dialogue_operator_" + hashlib.sha1(
                semantic.encode("utf-8")
            ).hexdigest()[:12]
            event = {
                "trigger_after_round": trigger_round,
                "stagnant_rounds": stagnant[-STAGNATION_ROUNDS_FOR_OPERATOR_EVOLUTION:],
                "historical_best_utility": historical_best,
                "operator": candidate,
                "created_at": now(),
            }
            workflow_evolution.write_json(event_dir / "operator.json", candidate)
            events.append(event)
            workflow_evolution.write_json(
                evolved_operator_registry_path(workflows_dir), events
            )
            print(
                f"Evolved dialogue operator {candidate['name']} after round "
                f"{trigger_round} stagnation",
                flush=True,
            )
            return event
        except Exception as error:
            last_error = error
            print(
                f"Dialogue operator proposal attempt {attempt}/"
                f"{args.optimizer_retries} failed: {error}",
                flush=True,
            )
    raise RuntimeError("Could not produce a novel valid dialogue operator") from last_error


def workflow_archive(results: list[dict]) -> list[dict[str, Any]]:
    return [
        {
            "round": node["round"],
            "utility": node["utility"],
            "workflow_id": node["workflow"]["workflow_id"],
            "name": node["workflow"]["name"],
            "action_types": [
                action["action_type"] for action in node["workflow"]["actions"]
            ],
            "max_exchanges": node["workflow"]["max_exchanges"],
        }
        for node in sorted(workflow_nodes(results), key=lambda item: item["round"])
    ]


def build_workflow_evolution_prompt(
    evidence: list[dict[str, Any]],
    dialogue_operators: dict[str, dict] | None = None,
) -> str:
    """Build the exact user prompt sent to the workflow optimizer."""
    dialogue_operators = dialogue_operators or available_dialogue_operators()
    return f"""Evolve one executable multi-turn human-expert interaction
workflow for mathematical-modeling report refinement.

The workflow controls the dialogue itself: its ordered interaction actions,
conditional follow-ups, reflection between exchanges, and stopping behavior.
It may use one to three expert exchanges. The modeling agent
retains all calculation, implementation, external-data validation, simulation,
and report-writing responsibility.

Evolution direction is otherwise unrestricted. A valid proposal must make a
behaviorally testable change to at least one action, condition, follow-up policy,
stop condition, or exchange budget. Changes
only to names, purpose text, examples, rationales, action IDs, or stylistic
wording are not novel. Treat every supplied workflow evidence node as a parent
input and consider all of them when producing the candidate; do not select or
ignore a subset. Decide freely whether the resulting use of all parents is best
described as crossover, mutation, or a mixture; no pattern is prescribed.

Optimize mean final-report score across the validation tasks while avoiding
redundant exchanges. Every later expert exchange must build on earlier dialogue
and have a distinct decision-relevant purpose. Keep the workflow general; do not
copy task-specific facts, parameters, methods, or conclusions. Keep the workflow
compact: merge actions that serve the same information purpose, do not split one
purpose across repetitive steps, and use no more actions or expert exchanges than
are needed to carry out the substantive interaction.

Available dialogue operators (distinct information functions, not mandatory steps):
{json.dumps(dialogue_operators, ensure_ascii=False, indent=2)}

Assumption audits challenge the real-world plausibility of high-impact
assumptions; model-failure attacks connect an audited technical weakness to a
plausible failure condition; data-parameter boundaries ground influential weak
inputs before recalibration. Treat every item in the supplied catalog as an
equally available information function. Keep technical translation,
implementation, calculation, and validation with the modeling agent. Compose,
reorder, replace, or condition operators when justified; you may invent a
different information function. Do not force every operator into every workflow.
Compare both a local improvement and a different dialogue mechanism internally
before selecting one proposal. Explain in evolution_rationale which supplied
parent inputs motivated each substantive behavioral change and how every parent
was considered. Extra reflection logs or paraphrases alone are insufficient.

Workflow parent-input archive. It contains all three initial workflows and the
current global-best evolved workflow when a later round has become the global
best. All listed workflows must be considered:
{json.dumps(evidence, ensure_ascii=False, indent=2)}

Each evidence node contains its mean validation utility. Its validation runs
contain the complete expert dialogue, an at-most-50-character summary of report
changes directly attributable to interaction, and LLM weakness summaries only
for non-perfect `analysis_groundedness` and `modeling_groundedness` Judge
feedback. Other Judge dimensions are omitted. Compare the three seed mechanisms
explicitly and use a later global best as evidence of successful evolution.
Treat final-report weaknesses as workflow evidence only when the dialogue process
could plausibly affect them.
Do not create a workflow action that adds an `Expert Interaction Impact` section or
other consultation-process account to the final modeling report; only the
substantive consequences should be integrated into its normal sections.

Return only one JSON object with name, purpose, entry_action, actions,
max_exchanges, stop_condition, changed_components, and evolution_rationale.
Use two to eight actions in execution order. Each action
contains action_id, action_type, and rule. Encode any conditional follow-up or
early stopping directly in the relevant action rule and stop_condition. At
least one action must have action_type expert_exchange.
"""


def propose_workflow(
    results: list[dict],
    round_number: int,
    round_dir: Path,
    args,
    problems: dict,
) -> dict[str, Any]:
    evidence_nodes = evolution_evidence_nodes(results)
    if not evidence_nodes:
        raise ValueError("cannot evolve a workflow without workflow evidence")
    evidence = optimizer_evidence(evidence_nodes, problems, round_dir, args)
    dialogue_operators = available_dialogue_operators(round_dir.parent)
    workflow_prompt_base = build_workflow_evolution_prompt(
        evidence, dialogue_operators
    )
    previous = workflow_nodes(results)
    last_error: Exception | None = None
    for attempt in range(1, args.optimizer_retries + 1):
        retry = (
            "\nThe previous proposal was rejected. Make a different behavioral "
            f"change, not a paraphrase. Rejection: {last_error}\n"
            if last_error
            else ""
        )
        workflow_attempt_prompt = workflow_prompt_base + retry
        (round_dir / f"evolution_prompt_attempt_{attempt}.md").write_text(
            workflow_attempt_prompt, encoding="utf-8"
        )
        (round_dir / "evolution_prompt.md").write_text(
            workflow_attempt_prompt, encoding="utf-8"
        )
        try:
            candidate = interaction.local.optimizer_response(
                {
                    "model": args.opt_model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "Return one concise valid JSON workflow object.",
                        },
                        {"role": "user", "content": workflow_attempt_prompt},
                    ],
                    "temperature": min(0.2 + 0.15 * (attempt - 1), 0.8),
                    "max_tokens": 3000,
                    "response_format": {"type": "json_object"},
                },
                args,
            )
            candidate = without_removed_workflow_fields(candidate)
            workflow_evolution.write_json(
                round_dir / f"evolution_response_attempt_{attempt}.json",
                candidate,
            )
            workflow_evolution.write_json(
                round_dir / "evolution_response.json", candidate
            )
            changed = candidate.get("changed_components")
            if not isinstance(changed, list) or not any(
                str(item).strip() for item in changed
            ):
                raise ValueError("optimizer did not identify a changed workflow component")
            validate_workflow(candidate)
            candidate["workflow_id"] = workflow_id(candidate)
            similarities = [
                (node["round"], workflow_similarity(candidate, node["workflow"]))
                for node in previous
            ]
            duplicate = max(similarities, key=lambda item: item[1], default=None)
            if duplicate and duplicate[1] >= args.candidate_similarity_threshold:
                raise ValueError(
                    "candidate workflow is too similar to evaluated round "
                    f"{duplicate[0]} (similarity={duplicate[1]:.4f})"
                )
            candidate.update(
                {
                    "evolution_operator": "evidence_guided_workflow_evolution",
                    "created_round": round_number,
                    "evidence_rounds": [item["round"] for item in evidence_nodes],
                }
            )
            return candidate
        except Exception as error:
            last_error = error
            print(
                f"Interaction workflow proposal attempt {attempt}/"
                f"{args.optimizer_retries} failed: {error}",
                flush=True,
            )
    raise RuntimeError("Could not produce a novel valid interaction workflow") from last_error


def build_workflow_refinement_prompt(workflow: dict[str, Any]) -> str:
    # The shared builder requires a rubric-shaped value. Use private sentinels
    # and remove that whole section before the prompt reaches the Agent.
    omitted_field = "__WORKFLOW_RUNNER_OMITTED_FIELD__"
    prompt_rubric = {
        "name": omitted_field,
        "purpose": omitted_field,
        "criteria": [{"name": omitted_field, "rule": omitted_field}],
        "attention_budget": omitted_field,
        "success_test": omitted_field,
    }
    base = substantive.build_refinement_prompt(prompt_rubric)
    base = base.replace(
        "Refine the supplied no-interaction draft; do not solve the task again from\n"
        "scratch.",
        "Use the supplied no-interaction draft as a starting point, then independently "
        "audit and improve the complete modeling solution. Rebuild any part of the "
        "model or analysis when the evidence indicates that the inherited approach "
        "is inadequate.",
    )
    base = base.replace(
        "Read the original draft first. Preserve correct, unaffected material. Modify\n"
        "the inherited files only where the expert interaction or necessary downstream\n"
        "analysis justifies a change. If you modify executable code, model parameters,\n"
        "or data-processing logic, execute the affected code again and regenerate every\n"
        "dependent numerical result, table, and figure before updating the report. Do\n"
        "not cite stale inherited outputs produced by an older version of the code.",
        "Read the original draft and inherited artifacts as inputs, not as presumptively "
        "correct constraints. Actively inspect the assumptions, formulation, data, "
        "calculations, code, and conclusions for weaknesses, and modify or replace any "
        "part needed to produce a stronger solution. If you modify executable code, "
        "model parameters, or data-processing logic, execute the affected code again "
        "and regenerate every dependent numerical result, table, and figure before "
        "updating the report. Do not cite stale inherited outputs produced by an older "
        "version of the code.",
    )
    base = base.replace(
        f"Expert-attention budget: {omitted_field}\n\n"
        f"Success test: {omitted_field}\n\n",
        "",
    )
    rubric_start = base.index("## Interaction Rubric\n")
    interaction_start = base.index("## Expert Interaction\n")
    base = base[:rubric_start] + base[interaction_start:]
    start = base.index("## Expert Interaction\n")
    end = base.index("## Refinement Output\n")
    section = f"""## Expert Interaction Workflow

Follow this interaction workflow as an ordered, condition-aware action list:

```json
{json.dumps(workflow_behavior(workflow), ensure_ascii=False, indent=2)}
```

Start with `entry_action`, which is the first item in `actions`, and execute the
remaining actions in listed order. Apply conditional follow-up and early-stop
logic from each action's `rule` and the workflow's `stop_condition`. For each
`expert_exchange`, write only the new qualitative question body to
`{{{{OPERATOR_FEEDBACK_DIR}}}}/expert_question_N.md`, using N=1, 2, then 3, and
run the following command once in the foreground:

`python "{{{{OUTPUT_DIR}}}}/code/wait_for_expert_reply.py" --request "{{{{OPERATOR_FEEDBACK_DIR}}}}/expert_request_N.json" --reply "{{{{OPERATOR_FEEDBACK_DIR}}}}/expert_reply_N.json" --timeout {substantive.EXPERT_REQUEST_TIMEOUT:.0f}`

The controller creates request/reply JSON. Do not edit those JSON files and do
not start process-poll or command-retry loops. A later question must explicitly
build on the earlier reply and perform the next workflow action; do not repeat
the question or seek approval. Stop according to the workflow and never exceed
`max_exchanges`.

After the dialogue, write one concise
`{{{{RESULTS_DIR}}}}/interaction_evidence.md` containing the baseline plan, each
exchange's distinct decision contribution, the resolved consultation output,
the independently implemented analytical change and evidence paths, and its
effect on the conclusion, confidence, scope, or presentation. Keep this full
process account in `interaction_evidence.md`. Integrate only the substantive
modeling consequences into the final report's normal sections, without naming
the expert interaction or adding an `Expert Interaction Impact` section.

"""
    return base[:start] + section + base[end:]


def prepare_workflow_validation_problem(
    problem_id: str,
    problem: dict,
    prompt_path: Path,
    round_number: int,
    repetition: int,
    experiment: Path,
    args,
) -> dict:
    prepared = substantive.prepare_refinement_validation_problem(
        problem_id,
        problem,
        prompt_path,
        round_number,
        repetition,
        experiment,
        args,
    )
    workflow = ACTIVE_WORKFLOWS.get(round_number)
    if workflow is None:
        raise RuntimeError(f"No active interaction workflow for round {round_number}")
    metadata_path = Path(prepared["run_dir"]) / "meta" / "run.json"
    metadata = workflow_evolution.read_json(metadata_path, {})
    metadata.update(
        {
            "interaction_workflow_id": workflow["workflow_id"],
            "interaction_workflow": workflow,
        }
    )
    workflow_evolution.write_json(metadata_path, metadata)
    workflow_evolution.write_json(
        Path(prepared["run_dir"]) / "workflow.json", workflow
    )
    return prepared


def finalize_workflow_receipt(result: dict, rubric: dict) -> dict:
    receipt = substantive.finalize_substantive_receipt(result, rubric)
    workflow = workflow_evolution.read_json(
        Path(result["run_dir"]) / "workflow.json", {}
    )
    if workflow:
        receipt.update(
            {
                "workflow_id": workflow["workflow_id"],
                "workflow_max_exchanges": workflow["max_exchanges"],
            }
        )
        output = (
            Path(result["run_dir"])
            / "output"
            / "results"
            / "interaction_receipt.json"
        )
        interaction.write_json_atomic(output, receipt)
    return receipt


def experiment_path(value: str | None) -> tuple[Path, bool]:
    if value:
        path = Path(value).resolve()
        return path, path.is_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return (
        REPO_ROOT
        / "openclaw_experiments"
        / f"interaction_workflow_substantive_{timestamp}",
        False,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Evolve multi-turn substantive expert-interaction workflows while "
            "holding one interaction rubric fixed."
        )
    )
    parser.add_argument("--max-rounds", type=int, default=10)
    parser.add_argument("--problem-id", nargs="+", default=list(substantive.DEFAULT_PROBLEMS))
    parser.add_argument("--exp")
    parser.add_argument("--fixed-rubric", default=str(DEFAULT_FIXED_RUBRIC_PATH))
    parser.add_argument(
        "--initial-workflow", default=None,
        help="Optional single workflow or population JSON; default: three distinct strategies."
    )
    parser.add_argument(
        "--baseline-report-root", default=str(substantive.BASELINE_REPORT_ROOT)
    )
    parser.add_argument("--model", default="deepseek/deepseek-v4-flash")
    parser.add_argument("--opt-model", default="deepseek-v4-pro")
    parser.add_argument("--opt-api-key")
    parser.add_argument("--opt-base-url")
    parser.add_argument("--optimizer-retries", type=int, default=5)
    parser.add_argument("--expert-model", default=substantive.DEFAULT_EXPERT_MODEL)
    parser.add_argument("--expert-api-key")
    parser.add_argument("--expert-base-url")
    parser.add_argument("--expert-timeout", type=float, default=600.0)
    parser.add_argument(
        "--expert-request-timeout",
        type=float,
        default=substantive.EXPERT_REQUEST_TIMEOUT,
    )
    parser.add_argument("--expert-attempts", type=int, default=3)
    parser.add_argument("--thinking", default="high")
    parser.add_argument("--timeout", type=int, default=7200)
    parser.add_argument("--completion-grace", type=float, default=60.0)
    parser.add_argument("--concurrency", type=int, default=1)
    parser.add_argument("--judge-repeats", type=int, default=1)
    parser.add_argument("--judge-concurrency", type=int, default=1)
    parser.add_argument("--judge-feedback-model", default="deepseek-v4-flash")
    parser.add_argument("--judge-feedback-concurrency", type=int, default=6)
    parser.add_argument("--validation-repetitions", type=int, default=1)
    parser.add_argument("--validation-attempts", type=int, default=3)
    parser.add_argument("--retry-concurrency", type=int, default=1)
    parser.add_argument("--validation-retry-delay", type=float, default=10.0)
    parser.add_argument("--openclaw-command")
    parser.add_argument("--initialize-only", action="store_true")
    parser.add_argument(
        "--enforce-substantive-interaction-gate",
        action="store_true",
        default=substantive.ENFORCE_SUBSTANTIVE_INTERACTION_GATE,
    )
    parser.add_argument(
        "--candidate-similarity-threshold",
        type=float,
        default=DEFAULT_CANDIDATE_SIMILARITY_THRESHOLD,
    )
    return parser.parse_args()


def normalized_results(results_path: Path) -> list[dict]:
    results = interaction.normalize_results(
        workflow_evolution.read_json(results_path, [])
    )
    for node in results:
        for field in ("parent_round", "parent_rounds", "secondary_parent_round"):
            node.pop(field, None)
        if isinstance(node.get("workflow"), dict):
            node["workflow"] = without_removed_workflow_fields(node["workflow"])
    return results


def completed_round_result(
    results: list[dict], round_number: int, problem_count: int, repetitions: int
) -> dict | None:
    existing = next(
        (item for item in results if item.get("round") == round_number), None
    )
    if (
        existing
        and len(existing.get("problem_results", [])) == problem_count
        and all(
            item.get("repetition_count", 1) >= repetitions
            for item in existing["problem_results"]
        )
    ):
        return existing
    return None


def execute_workflow_round(
    experiment: Path,
    round_number: int,
    workflow: dict,
    fixed_rubric: dict,
    problems: dict,
    run_args,
    existing: dict | None,
    enforce_gate: bool,
) -> tuple[dict, list[dict]]:
    round_dir = experiment / "workflows" / f"round_{round_number}"
    round_dir.mkdir(parents=True, exist_ok=True)
    workflow = without_removed_workflow_fields(copy.deepcopy(workflow))
    workflow["workflow_id"] = workflow_id(workflow)
    validate_workflow(workflow)
    workflow_evolution.write_json(round_dir / "workflow.json", workflow)
    ACTIVE_WORKFLOWS[round_number] = workflow
    prompt_path = round_dir / "prompt.md"
    prompt_path.write_text(
        build_workflow_refinement_prompt(workflow), encoding="utf-8"
    )
    result = interaction.evaluate_round(
        experiment,
        round_number,
        fixed_rubric,
        problems,
        prompt_path,
        run_args,
        existing,
    )
    checks, failures = [], []
    if enforce_gate:
        for aggregate in result["problem_results"]:
            repetitions = aggregate.get("repetitions") or [aggregate]
            for repetition in repetitions:
                run_dir = Path(repetition["run_dir"])
                try:
                    check = substantive.validate_substantive_interaction(run_dir)
                except Exception as error:
                    check = {
                        "passed": False,
                        "run_dir": str(run_dir),
                        "error": repr(error),
                        "checked_at": now(),
                    }
                    failures.append(check)
                else:
                    check["run_dir"] = str(run_dir)
                repetition["substantive_interaction_check"] = check
                checks.append(check)
    result.update(
        {
            "fixed_rubric_id": fixed_rubric["rubric_id"],
            "fixed_rubric": fixed_rubric,
            "workflow_id": workflow["workflow_id"],
            "workflow": workflow,
            "evolution_operator": workflow.get(
                "evolution_operator", "initial_workflow"
            ),
            "substantive_interaction_checks": checks,
            "substantive_interaction_gate_enabled": enforce_gate,
            "substantive_interaction_passed": (
                not failures if enforce_gate else None
            ),
        }
    )
    return result, failures


def persist_round_result(
    experiment: Path, results_path: Path, result: dict
) -> list[dict]:
    results = normalized_results(results_path)
    results = [item for item in results if item.get("round") != result["round"]]
    results.append(result)
    results = interaction.normalize_results(
        sorted(results, key=lambda item: item["round"])
    )
    result = next(item for item in results if item["round"] == result["round"])
    workflows_dir = experiment / "workflows"
    round_dir = workflows_dir / f"round_{result['round']}"
    workflow_evolution.write_json(round_dir / "result.json", result)
    workflow_evolution.write_json(results_path, results)
    interaction.write_score_outputs(
        workflows_dir / "round_problem_dimension_scores.json",
        workflows_dir / "round_problem_dimension_scores.xlsx",
        workflows_dir / "round_problem_interactions.xlsx",
        experiment,
        results,
    )
    write_execution_time_excel(
        workflows_dir / "round_execution_times.xlsx", results
    )
    print(
        f"Round {result['round']} workflow {result['workflow_id']} "
        f"utility: {result['utility']:.6f}",
        flush=True,
    )
    return results


def parse_iso_datetime(value: Any) -> datetime | None:
    try:
        return datetime.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None


def run_artifact_timing(run: dict[str, Any]) -> dict[str, Any] | None:
    """Recover one completed problem run's wall interval from its artifacts."""
    run_dir = Path(str(run.get("run_dir", "")))
    metadata = workflow_evolution.read_json(run_dir / "meta" / "run.json", {})
    judge = workflow_evolution.read_json(
        run_dir / "meta" / "judge_stability.json", {}
    )
    started = parse_iso_datetime(metadata.get("created_at"))
    completed = parse_iso_datetime(judge.get("completed_at"))
    if started is None or completed is None or completed < started:
        return None
    return {
        "started_at": started.isoformat(),
        "completed_at": completed.isoformat(),
        "elapsed_seconds": (completed - started).total_seconds(),
        "source": "run_and_judge_artifact_timestamps",
    }


def problem_result_timing(problem: dict[str, Any]) -> dict[str, Any] | None:
    """Aggregate repetitions as a wall interval rather than summing overlaps."""
    repetitions = problem.get("repetitions") or [problem]
    timings = [run_artifact_timing(run) for run in repetitions]
    timings = [timing for timing in timings if timing is not None]
    if not timings:
        return None
    starts = [parse_iso_datetime(timing["started_at"]) for timing in timings]
    ends = [parse_iso_datetime(timing["completed_at"]) for timing in timings]
    starts = [value for value in starts if value is not None]
    ends = [value for value in ends if value is not None]
    if not starts or not ends:
        return None
    started, completed = min(starts), max(ends)
    return {
        "started_at": started.isoformat(),
        "completed_at": completed.isoformat(),
        "elapsed_seconds": (completed - started).total_seconds(),
        "source": (
            timings[0].get("source", "recorded")
            if len({timing.get("source") for timing in timings}) == 1
            else "mixed_timing_sources"
        ),
    }


def round_result_timing(result: dict[str, Any]) -> dict[str, Any] | None:
    timings = [
        problem_result_timing(problem)
        for problem in result.get("problem_results", [])
    ]
    timings = [timing for timing in timings if timing is not None]
    if not timings:
        return None
    starts = [parse_iso_datetime(timing["started_at"]) for timing in timings]
    ends = [parse_iso_datetime(timing["completed_at"]) for timing in timings]
    starts = [value for value in starts if value is not None]
    ends = [value for value in ends if value is not None]
    if not starts or not ends:
        return None
    started, completed = min(starts), max(ends)
    return {
        "started_at": started.isoformat(),
        "completed_at": completed.isoformat(),
        "elapsed_seconds": (completed - started).total_seconds(),
        "execution_mode": "parallel_problem_evaluation",
        "source": "derived_from_problem_artifact_intervals",
    }


def write_execution_time_excel(output_path: Path, results: list[dict]) -> Path:
    """Rewrite the analysis workbook after each completed workflow round."""
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill

    workbook = Workbook()
    rounds_sheet = workbook.active
    rounds_sheet.title = "轮次耗时"
    problem_sheet = workbook.create_sheet("题目耗时")
    round_headers = [
        "轮次",
        "工作流ID",
        "开始时间",
        "完成时间",
        "并行总耗时(秒)",
        "并行总耗时(分钟)",
        "题目数",
        "计时来源",
    ]
    problem_headers = [
        "轮次",
        "题目ID",
        "重复次数",
        "开始时间",
        "完成时间",
        "题目墙钟耗时(秒)",
        "题目墙钟耗时(分钟)",
        "运行目录",
        "计时来源",
    ]
    rounds_sheet.append(round_headers)
    problem_sheet.append(problem_headers)
    for result in sorted(results, key=lambda item: int(item["round"])):
        timing = round_result_timing(result)
        seconds = timing.get("elapsed_seconds") if timing else None
        rounds_sheet.append(
            [
                int(result["round"]),
                result.get("workflow_id", ""),
                timing.get("started_at") if timing else None,
                timing.get("completed_at") if timing else None,
                seconds,
                seconds / 60.0 if seconds is not None else None,
                len(result.get("problem_results", [])),
                timing.get("source") if timing else "unavailable",
            ]
        )
        for problem in result.get("problem_results", []):
            problem_timing = problem_result_timing(problem)
            problem_seconds = (
                problem_timing.get("elapsed_seconds") if problem_timing else None
            )
            repetitions = problem.get("repetitions") or [problem]
            run_dirs = "; ".join(
                str(repetition.get("run_dir", "")) for repetition in repetitions
            )
            problem_sheet.append(
                [
                    int(result["round"]),
                    problem.get("problem_id", ""),
                    problem.get("repetition_count", len(repetitions)),
                    problem_timing.get("started_at") if problem_timing else None,
                    problem_timing.get("completed_at") if problem_timing else None,
                    problem_seconds,
                    problem_seconds / 60.0 if problem_seconds is not None else None,
                    run_dirs,
                    problem_timing.get("source") if problem_timing else "unavailable",
                ]
            )

    header_fill = PatternFill("solid", fgColor="1F4E78")
    for sheet in (rounds_sheet, problem_sheet):
        sheet.freeze_panes = "A2"
        sheet.auto_filter.ref = sheet.dimensions
        for cell in sheet[1]:
            cell.font = Font(color="FFFFFF", bold=True)
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
        for row in sheet.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = Alignment(vertical="top")
        for column in (5, 6):
            if sheet is rounds_sheet:
                for cell in sheet.iter_cols(
                    min_col=column, max_col=column, min_row=2
                ):
                    for value in cell:
                        value.number_format = "0.00"
        for column in (6, 7):
            if sheet is problem_sheet:
                for cell in sheet.iter_cols(
                    min_col=column, max_col=column, min_row=2
                ):
                    for value in cell:
                        value.number_format = "0.00"
    rounds_sheet.column_dimensions["A"].width = 9
    rounds_sheet.column_dimensions["B"].width = 34
    rounds_sheet.column_dimensions["C"].width = 27
    rounds_sheet.column_dimensions["D"].width = 27
    rounds_sheet.column_dimensions["E"].width = 18
    rounds_sheet.column_dimensions["F"].width = 20
    rounds_sheet.column_dimensions["G"].width = 10
    rounds_sheet.column_dimensions["H"].width = 42
    problem_sheet.column_dimensions["A"].width = 9
    problem_sheet.column_dimensions["B"].width = 42
    problem_sheet.column_dimensions["C"].width = 12
    problem_sheet.column_dimensions["D"].width = 27
    problem_sheet.column_dimensions["E"].width = 27
    problem_sheet.column_dimensions["F"].width = 20
    problem_sheet.column_dimensions["G"].width = 22
    problem_sheet.column_dimensions["H"].width = 70
    problem_sheet.column_dimensions["I"].width = 42
    output_path.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(output_path)
    return output_path


def plot_round_average_dimension_scores(
    results: list[dict], output_path: Path
) -> Path:
    """Plot round averages and per-problem scores together on one axis."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    dimensions = tuple(interaction.EVALUATION_DIMENSIONS)
    if len(dimensions) != 4:
        raise ValueError(
            f"expected four objective dimensions for plotting; got {dimensions}"
        )
    ordered = sorted(results, key=lambda item: int(item["round"]))
    rounds = [int(item["round"]) for item in ordered]
    if not rounds:
        raise ValueError("cannot plot round scores without completed results")

    scores: dict[str, list[float]] = {dimension: [] for dimension in dimensions}
    problem_ids = tuple(interaction.VALIDATION_PROBLEMS)
    problem_scores = {
        problem_id: {dimension: [] for dimension in dimensions}
        for problem_id in problem_ids
    }
    for item in ordered:
        averages = item.get("average_dimension_scores") or interaction.average_dimensions(
            item.get("problem_results", [])
        )
        missing = [dimension for dimension in dimensions if dimension not in averages]
        if missing:
            raise ValueError(
                f"round {item['round']} lacks average scores for: "
                + ", ".join(missing)
            )
        for dimension in dimensions:
            scores[dimension].append(float(averages[dimension]))
        by_problem = {
            problem.get("problem_id"): problem
            for problem in item.get("problem_results", [])
        }
        for problem_id in problem_ids:
            dimension_scores = by_problem.get(problem_id, {}).get(
                "dimension_scores", {}
            )
            for dimension in dimensions:
                value = dimension_scores.get(dimension)
                problem_scores[problem_id][dimension].append(
                    float(value) if isinstance(value, (int, float)) else float("nan")
                )

    titles = {
        "structural_coherency": "Structural Coherency",
        "scoring_decomposition": "Scoring Decomposition",
        "modeling_groundedness": "Modeling Groundedness",
        "analysis_groundedness": "Analysis Groundedness",
    }
    colors = {
        "structural_coherency": "#1f77b4",
        "scoring_decomposition": "#ff7f0e",
        "modeling_groundedness": "#2ca02c",
        "analysis_groundedness": "#d62728",
    }
    problem_titles = {
        "2013_Bank_Service_Problem": "Bank Service",
        "2025_Managing_Sustainable_Tourism": "Sustainable Tourism",
        "2003_Aviation_Baggage_Screening": "Baggage Screening",
    }
    panels = [("Round Average Across Three Problems", scores)] + [
        (problem_titles.get(problem_id, problem_id), problem_scores[problem_id])
        for problem_id in problem_ids
    ]
    fig, axes = plt.subplots(2, 2, figsize=(16, 10), sharex=True, sharey=True)
    for axis, (panel_title, panel_scores) in zip(axes.flat, panels):
        for dimension in dimensions:
            axis.plot(
                rounds,
                panel_scores[dimension],
                marker="o",
                color=colors[dimension],
                linewidth=2.2,
                markersize=4,
            )
        axis.set_title(panel_title)
        axis.set_xlabel("Round")
        axis.set_ylabel("Score")
        axis.set_xticks(rounds)
        axis.set_ylim(0.0, 1.02)
        axis.grid(True, linestyle="--", alpha=0.3)
    from matplotlib.lines import Line2D

    dimension_legend = [
        Line2D(
            [0], [0], color=colors[dimension], linewidth=3,
            label=titles.get(dimension, dimension),
        )
        for dimension in dimensions
    ]
    fig.legend(
        handles=dimension_legend,
        title="Dimension",
        loc="lower center",
        ncol=4,
        bbox_to_anchor=(0.5, 0.01),
    )
    fig.suptitle(
        "Four-Dimension Scores by Evolution Round", fontsize=15
    )
    fig.tight_layout(rect=(0, 0.07, 1, 0.96))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return output_path


def main() -> None:
    args = parse_args()
    numeric = (
        args.max_rounds,
        args.optimizer_retries,
        args.concurrency,
        args.judge_repeats,
        args.judge_concurrency,
        args.judge_feedback_concurrency,
        args.validation_repetitions,
        args.validation_attempts,
        args.retry_concurrency,
        args.expert_attempts,
    )
    if (
        min(numeric) < 1
        or args.timeout < 1
        or args.expert_timeout <= 0
        or args.expert_request_timeout <= 0
    ):
        raise ValueError("Concurrency, retries, repetitions, and timeouts must be positive")
    if args.validation_retry_delay < 0:
        raise ValueError("validation retry delay must be non-negative")
    if not 0.0 < args.candidate_similarity_threshold <= 1.0:
        raise ValueError("candidate similarity threshold must be in (0, 1]")

    problems = baseline.load_problems()
    unknown = [item for item in args.problem_id if item not in problems]
    if unknown:
        raise ValueError("Unknown problem ID(s): " + ", ".join(unknown))
    if len(args.problem_id) != len(set(args.problem_id)):
        raise ValueError("problem IDs must be unique")

    experiment, resumed = experiment_path(args.exp)
    workflows_dir = experiment / "workflows"
    results_path = workflows_dir / "results.json"
    previous_config = {}
    if not resumed:
        workflows_dir.mkdir(parents=True, exist_ok=False)
        workflow_evolution.write_json(results_path, [])
    else:
        previous_config = workflow_evolution.read_json(
            experiment / "config.json", {}
        )
        if previous_config.get("experiment_type") != (
            "substantive_interaction_workflow_evolution"
        ):
            raise ValueError("--exp is not an interaction-workflow experiment")

    interaction.OBJECTIVE_WEIGHTS = dict(previous_config.get("utility_weights", {}))

    fixed_target = experiment / "fixed_interaction_rubric.json"
    if fixed_target.is_file():
        fixed_rubric_path = fixed_target
    else:
        fixed_rubric_path = resolve_fixed_rubric_path(args.fixed_rubric)
    fixed_rubric = load_fixed_rubric(fixed_rubric_path)
    workflow_evolution.write_json(fixed_target, fixed_rubric)

    initial_target = experiment / "initial_interaction_workflows.json"
    initial_population = load_seed_population(experiment, resumed, args.initial_workflow)

    configured_reports = previous_config.get("baseline_reports", {})
    if not isinstance(configured_reports, dict):
        configured_reports = {}
    baseline_reports = {}
    for problem_id in args.problem_id:
        configured = Path(str(configured_reports.get(problem_id, "")))
        source = (
            configured
            if configured.is_file()
            else substantive.resolve_baseline_report(
                problem_id, Path(args.baseline_report_root)
            )
        )
        baseline_reports[problem_id] = str(source.resolve())

    interaction.VALIDATION_PROBLEMS = tuple(args.problem_id)
    interaction.INITIAL_RUBRIC = fixed_rubric
    interaction.finalize_interaction_receipt = finalize_workflow_receipt
    interaction.run_local_modeling_phase = substantive.run_substantive_modeling_phase
    interaction.prepare_validation_problem = prepare_workflow_validation_problem
    interaction.serve_expert_requests = substantive.serve_substantive_expert_requests
    baseline.HUMAN_MODELING_EXPERT_ROLE_PROMPT = substantive.SUBSTANTIVE_EXPERT_ROLE_PROMPT
    baseline.create_operator_role_prompts = substantive.create_substantive_operator_role_prompt

    config = {
        "experiment_type": "substantive_interaction_workflow_evolution",
        "evolution_subject": "interaction_workflow",
        "rubric_evolution": False,
        "workflow_evolution": True,
        "max_rounds": args.max_rounds,
        "execution_mode": "expert_guided_baseline_report_refinement",
        "fixed_interaction_rubric": str(fixed_target.resolve()),
        "fixed_interaction_rubric_source": str(fixed_rubric_path.resolve()),
        "interaction_rubric_in_optimizer_prompt": False,
        "interaction_rubric_in_agent_prompt": False,
        "initial_interaction_workflow": str(initial_target.resolve()),
        "initial_strategy_count": len(initial_population),
        "initial_strategy_rounds_parallel": True,
        "initial_round_problem_concurrency": args.concurrency,
        "initial_strategy_rounds": list(
            range(1, min(len(initial_population), args.max_rounds) + 1)
        ),
        "evolved_rounds_serial": True,
        "stagnation_operator_evolution": {
            "enabled": True,
            "rounds_without_strict_improvement": (
                STAGNATION_ROUNDS_FOR_OPERATOR_EVOLUTION
            ),
            "strict_improvement": True,
            "registry": str(evolved_operator_registry_path(workflows_dir).resolve()),
        },
        "round_dimension_plot": str(
            (workflows_dir / "round_average_dimension_scores.png").resolve()
        ),
        "execution_time_excel": str(
            (workflows_dir / "round_execution_times.xlsx").resolve()
        ),
        "baseline_report_root": str(Path(args.baseline_report_root).resolve()),
        "baseline_reports": baseline_reports,
        "validation_problems": args.problem_id,
        "model": args.model,
        "opt_model": args.opt_model,
        "expert_model": args.expert_model,
        "candidate_similarity_threshold": args.candidate_similarity_threshold,
        "utility_weights": dict(interaction.OBJECTIVE_WEIGHTS),
        "judge_repeats": args.judge_repeats,
        "judge_feedback_model": args.judge_feedback_model,
        "judge_feedback_concurrency": args.judge_feedback_concurrency,
        "optimizer_evidence": {
            "nodes": (
                "all_three_initial_workflows_plus_current_global_best_"
                "evolved_workflow"
            ),
            "fields": [
                "workflow",
                "average_utility",
                "expert_interaction",
                "interaction_report_change_summary",
                "judge_groundedness_weakness_summary",
            ],
            "report_change_summary_max_chars": REPORT_CHANGE_SUMMARY_MAX_CHARS,
            "judge_feedback_dimensions": list(JUDGE_FEEDBACK_DIMENSIONS),
            "all_workflow_nodes_required_as_parent_inputs": True,
        },
        "validation_repetitions": args.validation_repetitions,
        "updated_at": now(),
    }
    workflow_evolution.write_json(experiment / "config.json", config)
    print(f"Experiment: {experiment}")
    print(f"Fixed interaction rubric: {fixed_target}")
    print(f"Initial interaction workflow: {initial_target}")
    print("Problems: " + ", ".join(args.problem_id))

    if args.initialize_only:
        for index, seed in enumerate(initial_population[:args.max_rounds], 1):
            round_dir = workflows_dir / f"round_{index}"
            round_dir.mkdir(parents=True, exist_ok=True)
            path = round_dir / "workflow.json"
            workflow = workflow_evolution.read_json(path, {}) or seed
            workflow_evolution.write_json(path, workflow)
            (round_dir / "prompt.md").write_text(
                build_workflow_refinement_prompt(workflow), encoding="utf-8"
            )
            print(f"Initialization complete; prompt: {round_dir / 'prompt.md'}")
        return

    write_execution_time_excel(
        workflows_dir / "round_execution_times.xlsx",
        normalized_results(results_path),
    )
    workflow_evolution.configure_completion_grace(
        baseline.run_problem, args.completion_grace
    )
    openclaw = baseline.find_openclaw_command(args.openclaw_command)
    atexit.register(
        interaction.cleanup_experiment_agents_at_exit, openclaw, experiment
    )
    run_args = substantive.runtime_args(args, baseline_reports)

    # The initial strategies are independent population members. Start all
    # unfinished seed rounds together, then wait for the entire population
    # before allowing any score-dependent evolution.
    seed_count = min(len(initial_population), args.max_rounds)
    results = normalized_results(results_path)
    pending_seeds = []
    for round_number in range(1, seed_count + 1):
        if completed_round_result(
            results,
            round_number,
            len(args.problem_id),
            args.validation_repetitions,
        ):
            print(f"Round {round_number} is complete; skipping", flush=True)
            continue
        existing = next(
            (item for item in results if item.get("round") == round_number), None
        )
        round_dir = workflows_dir / f"round_{round_number}"
        saved = without_removed_workflow_fields(
            workflow_evolution.read_json(round_dir / "workflow.json", {})
        )
        workflow = saved or copy.deepcopy(initial_population[round_number - 1])
        pending_seeds.append((round_number, workflow, existing))

    initial_errors = []
    if pending_seeds:
        # Each independent seed round receives the full per-round problem
        # concurrency. Three seed rounds and --concurrency 3 therefore permit
        # all nine one-repetition problem runs to execute concurrently.
        per_round_concurrency = args.concurrency
        print(
            f"Running {len(pending_seeds)} independent initial workflow rounds "
            f"in parallel (per-round problem concurrency={per_round_concurrency})",
            flush=True,
        )
        with ThreadPoolExecutor(max_workers=len(pending_seeds)) as executor:
            futures = {}
            for round_number, workflow, existing in pending_seeds:
                seed_args = copy.copy(run_args)
                seed_args.concurrency = per_round_concurrency
                seed_args.retry_concurrency = args.retry_concurrency
                future = executor.submit(
                    execute_workflow_round,
                    experiment,
                    round_number,
                    workflow,
                    fixed_rubric,
                    problems,
                    seed_args,
                    existing,
                    args.enforce_substantive_interaction_gate,
                )
                futures[future] = round_number
            for future in as_completed(futures):
                round_number = futures[future]
                try:
                    result, failures = future.result()
                    persist_round_result(experiment, results_path, result)
                    if failures:
                        initial_errors.append(
                            RuntimeError(
                                f"{len(failures)} run(s) failed the substantive-"
                                f"interaction gate in round {round_number}"
                            )
                        )
                except Exception as error:
                    initial_errors.append(error)
    if initial_errors:
        raise RuntimeError(
            f"{len(initial_errors)} initial workflow round(s) failed; "
            "their checkpoints were preserved"
        ) from initial_errors[0]

    # This also handles a resumed experiment that had already reached a plateau
    # before the operator-evolution rule was introduced.
    results = normalized_results(results_path)
    maybe_evolve_dialogue_operator(results, workflows_dir, args, problems)

    # Every evolved round depends on all earlier scores, so these rounds remain
    # strictly serial even though problems within one round may run concurrently.
    for round_number in range(seed_count + 1, args.max_rounds + 1):
        results = normalized_results(results_path)
        if completed_round_result(
            results,
            round_number,
            len(args.problem_id),
            args.validation_repetitions,
        ):
            print(f"Round {round_number} is complete; skipping", flush=True)
            continue
        existing = next(
            (item for item in results if item.get("round") == round_number), None
        )
        round_dir = workflows_dir / f"round_{round_number}"
        round_dir.mkdir(parents=True, exist_ok=True)
        saved = without_removed_workflow_fields(
            workflow_evolution.read_json(round_dir / "workflow.json", {})
        )
        workflow = saved or propose_workflow(
            results,
            round_number,
            round_dir,
            args,
            problems,
        )
        result, failures = execute_workflow_round(
            experiment,
            round_number,
            workflow,
            fixed_rubric,
            problems,
            run_args,
            existing,
            args.enforce_substantive_interaction_gate,
        )
        results = persist_round_result(experiment, results_path, result)
        if failures:
            raise RuntimeError(
                f"{len(failures)} run(s) failed the substantive-interaction gate; "
                f"see {round_dir / 'result.json'}"
            )
        maybe_evolve_dialogue_operator(results, workflows_dir, args, problems)

    final_results = normalized_results(results_path)
    incomplete_rounds = [
        round_number
        for round_number in range(1, args.max_rounds + 1)
        if completed_round_result(
            final_results,
            round_number,
            len(args.problem_id),
            args.validation_repetitions,
        )
        is None
    ]
    if incomplete_rounds:
        raise RuntimeError(
            "Cannot generate final dimension plot; incomplete rounds: "
            + ", ".join(map(str, incomplete_rounds))
        )
    plot_path = plot_round_average_dimension_scores(
        final_results, workflows_dir / "round_average_dimension_scores.png"
    )
    print(f"Round dimension plot: {plot_path}", flush=True)


if __name__ == "__main__":
    main()
