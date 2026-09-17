"""Evolve multi-turn expert-interaction workflows under one fixed rubric."""

from __future__ import annotations

import argparse
import atexit
import copy
import difflib
import hashlib
import json
import math
import random
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from . import baseline
    from . import run_evolution as workflow_evolution
    from . import run_interaction_rubric_evolution as interaction
    from . import run_judge_stability
    from . import run_substantive_interaction_experiment as substantive
except ImportError:
    import baseline
    import run_evolution as workflow_evolution
    import run_interaction_rubric_evolution as interaction
    import run_judge_stability
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
DEFAULT_CANDIDATE_SIMILARITY_THRESHOLD = 0.90
STAGNATION_ROUNDS_FOR_OPERATOR_EVOLUTION = 5
SIMILARITY_REJECTIONS_FOR_OPERATOR_EVOLUTION = 3
CPE_TRAINING_PARENT_COUNT = 2
MIN_CPE_EVOLUTION_ROUNDS: int | None = CPE_TRAINING_PARENT_COUNT + 1
# Opt-in compatibility switch used by launchers that want the two seed parents,
# their first child, and that child's validation to comprise CPE round 1.
CPE_COLLAPSE_INITIAL_PARENTS = False
MAX_WORKFLOW_EXCHANGES: int | None = 3
FIRST_STAGNATION_COUNTED_ROUND = 4
OPERATOR_SIMILARITY_THRESHOLD = 0.90
REPORT_CHANGE_SUMMARY_MAX_CHARS = 50
JUDGE_FEEDBACK_DIMENSIONS = (
    "analysis_groundedness",
    "modeling_groundedness",
)
DEFAULT_CPE_SPLIT_PATH = REPO_ROOT / "data" / "modelingbench_train_test_split.json"
DEFAULT_CPE_TRAIN_BATCH_SIZE = 3
DEFAULT_CPE_VALIDATION_SIZE = 10
DEFAULT_CPE_SELECTION_EPSILON = 0.0
DEFAULT_CPE_MAX_EXCHANGES = 3
DEFAULT_CPE_TOTAL_TOKEN_REFERENCE = 5000
DEFAULT_CPE_TOTAL_LATENCY_MAX_SECONDS = 540.0
DEFAULT_CPE_EXCHANGE_COST_WEIGHT = 0.5
DEFAULT_CPE_TOKEN_COST_WEIGHT = 0.4
DEFAULT_CPE_LATENCY_COST_WEIGHT = 0.1
DEFAULT_CPE_COST_PENALTY_WEIGHT = 0.01
CPE_UTILITY_BASIS_QUALITY_GAIN = "mean_quality_gain_minus_interaction_cost"
CPE_UTILITY_BASIS_ABSOLUTE_SCORE = "mean_report_score_minus_interaction_cost"
# Entry points may select the absolute-score basis for experiments whose
# baseline reports are inputs rather than a quality reference.
CPE_UTILITY_BASIS = CPE_UTILITY_BASIS_QUALITY_GAIN
EXPERT_REPLY_LATENCY_PATTERN = re.compile(
    r"completed exchange\s+(\d+)\s+reply\s+\([^;]*;\s*([0-9]+(?:\.[0-9]+)?)s\)"
)
ACTIVE_WORKFLOWS: dict[tuple[str, int], dict[str, Any]] = {}

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
                    "rule": "List the assumptions that could materially change the model's principal conclusions. Rank them by decision impact and evidential weakness, then retain at most two independent assumptions most likely to reverse the primary recommendation or invalidate a headline result. Exclude redundant assumptions from the same causal chain, record lower-priority assumptions as residual limitations, and do not assume that the inherited formulation is correct.",
                },
                {
                    "action_id": "expert_reality_challenge",
                    "action_type": "expert_exchange",
                    "rule": "Present only the selected one or two materially consequential weakly supported assumptions and their real-world meanings without defending them. Ask the expert to challenge their plausibility, identify omitted conditions, or explain when they could fail. The expert supplies qualitative domain judgment; the agent owns every technical translation, calculation, and validation.",
                },
                {
                    "action_id": "technical_translation",
                    "action_type": "agent_analysis",
                    "rule": "Translate the material challenges to the selected assumptions into explicit, falsifiable model alternatives or boundary scenarios. State the smallest set of assumptions, equations, constraints, parameters, code paths, or decision criteria affected; do not directly adopt an expert-supplied number or technical prescription and do not expand the repair to unrelated model components.",
                },
                {
                    "action_id": "recompute_and_compare",
                    "action_type": "agent_validation",
                    "rule": "Implement the smallest justified alternatives for the selected assumptions. For each selected assumption, perform one primary recomputation and one proportionate independent check, then compare the decision-relevant outputs with the original formulation. Regenerate outputs that directly depend on changed code or parameters.",
                },
                {
                    "action_id": "close_dialogue",
                    "action_type": "close",
                    "rule": "After the first validation pass, review only the selected assumptions. Use a second exchange when a selected unresolved issue still requires expert judgment; otherwise stop, integrate the supported consequences, and record unselected or unresolved lower-priority assumptions as limitations.",
                },
            ],
            "max_exchanges": 2,
            "stop_condition": "Stop after the selected one or two assumptions have each received one primary recomputation and one proportionate independent check, or after a second exchange for an unresolved selected issue followed by that bounded validation. Record other assumptions as residual limitations rather than expanding the run.",
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
                    "rule": "Inspect the mathematical formulation, units, constraints, algorithms, and executable code for internal consistency and agreement with the problem statement. Use targeted sanity or boundary checks to rank weaknesses, then retain at most two independent weaknesses most likely to reverse the primary recommendation or invalidate a headline result. Group redundant findings by causal chain and record lower-priority findings as residual limitations.",
                },
                {
                    "action_id": "expert_failure_attack",
                    "action_type": "expert_exchange",
                    "rule": "Present the real-world implications of only the selected one or two dangerous technical weaknesses. Ask the expert to attack those implications with plausible failure conditions or counterexamples. Do not ask the expert to inspect code or calculate; the agent must repair the selected weaknesses and test each repair independently.",
                },
                {
                    "action_id": "repair_model",
                    "action_type": "agent_analysis",
                    "rule": "Convert each selected material failure condition into one precise technical test. Make the smallest sufficient correction to the affected equations, constraints, algorithms, data transformations, or code, and regenerate outputs that directly depend on that correction. Do not repair unrelated weaknesses or broaden the model unless the selected failure condition cannot otherwise be tested.",
                },
                {
                    "action_id": "independent_regression_test",
                    "action_type": "agent_validation",
                    "rule": "Validate each selected repair with one proportionate independent check, preferring an analytical special case, invariant, or targeted boundary test over a second full implementation. Compare the decision-relevant old and repaired results and update the recommendation and confidence boundary.",
                },
                {
                    "action_id": "close_dialogue",
                    "action_type": "close",
                    "rule": "Re-audit only the selected failure modes after the first repair pass. Use a second exchange when a selected unresolved failure mode still requires expert judgment; otherwise stop, integrate the verified results, and record remaining lower-priority weaknesses as limitations.",
                },
            ],
            "max_exchanges": 2,
            "stop_condition": "Stop after the selected one or two failure conditions have each received one focused repair and one proportionate independent check, or after a second exchange for an unresolved selected failure mode followed by that bounded validation. Record other weaknesses as residual limitations rather than expanding the run.",
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
                    "rule": "Trace the material conclusions to their data and parameters. Rank influential weakly evidenced parameters, parameter groups, or empirical claims using targeted sensitivity checks when needed, then retain at most two independent inputs most likely to reverse the primary recommendation or invalidate a headline result. Group related quantities by causal role and record lower-priority evidence gaps as limitations.",
                },
                {
                    "action_id": "expert_real_world_boundary",
                    "action_type": "expert_exchange",
                    "rule": "Explain the distinct decision roles of only the selected one or two weak inputs and ask the expert for qualitative real-world bounds, observable boundary conditions, and suitable authoritative evidence types. The expert must not invent numerical estimates. The agent must independently verify externally testable claims, set defensible values or ranges, recalibrate, and compare conclusions.",
                },
                {
                    "action_id": "verify_external_evidence",
                    "action_type": "agent_research",
                    "rule": "When a selected input is externally verifiable, consult one or two authoritative sources for that evidence decision and record their provenance. Reconcile source scope, units, population, and time period with the model; do not treat the expert reply itself as empirical verification or expand research to unselected inputs.",
                },
                {
                    "action_id": "recalibrate_and_compare",
                    "action_type": "agent_validation",
                    "rule": "Recalibrate only the selected supported inputs or their defensible joint range. Run one primary recalibration and one proportionate independent check, then compare the decision-relevant outputs individually and jointly with the original. Revise the model, recommendation, limitations, and confidence bounds when the comparison shows a material difference.",
                },
                {
                    "action_id": "close_dialogue",
                    "action_type": "close",
                    "rule": "After recalibration, review only the selected inputs. Use a second exchange when a selected unresolved input still requires expert judgment; otherwise stop, integrate only supported consequences, and record remaining evidence gaps as limitations.",
                },
            ],
            "max_exchanges": 2,
            "stop_condition": "Stop after the selected one or two weak inputs have been verified when applicable, recalibrated once, and checked once, or after a second exchange for an unresolved selected input followed by that bounded comparison. Record other evidence gaps as residual limitations rather than expanding the run.",
            "seed_operator": "data_parameter_boundary",
        },
    ]
    # CPE starts directly from the two parent mechanisms. The former third
    # data-grounding seed is no longer an initial validation rollout.
    population = []
    for workflow in definitions[:CPE_TRAINING_PARENT_COUNT]:
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
        "training_batch",
    ):
        compact.pop(key, None)
    return compact


def load_seed_population(
    experiment: Path,
    resumed: bool,
    source: str | None,
    *,
    persist_legacy_file: bool = True,
) -> list[dict]:
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
    if persist_legacy_file and not legacy.exists():
        workflow_evolution.write_json(legacy, population[0])
    return population


def now() -> str:
    return datetime.now().isoformat()


def load_cpe_split(path: Path) -> tuple[list[str], list[str]]:
    """Load the already materialized ModelingBench train/validation split."""
    payload = workflow_evolution.read_json(Path(path).resolve(), {})
    if not isinstance(payload, dict):
        raise ValueError("CPE split file must contain a JSON object")
    train = payload.get("train")
    validation = payload.get("validation")
    if not isinstance(train, list) or not train:
        raise ValueError("CPE split file has no non-empty train list")
    if not isinstance(validation, list) or not validation:
        raise ValueError("CPE split file has no non-empty validation list")
    train = [str(item) for item in train]
    validation = [str(item) for item in validation]
    if len(train) != len(set(train)) or len(validation) != len(set(validation)):
        raise ValueError("CPE train and validation lists must not contain duplicates")
    overlap = sorted(set(train) & set(validation))
    if overlap:
        raise ValueError("CPE train/validation overlap: " + ", ".join(overlap))
    return train, validation


def cpe_state_path(experiment: Path) -> Path:
    return experiment / "workflows" / "cpe_state.json"


def load_or_create_cpe_state(
    experiment: Path,
    train_pool: list[str],
    validation_pool: list[str],
    train_batch_size: int,
    validation_size: int,
    sampling_seed: int | None,
    selection_epsilon: float = DEFAULT_CPE_SELECTION_EPSILON,
) -> dict[str, Any]:
    """Create a full-validation, restart-safe CPE sampling state."""
    path = cpe_state_path(experiment)
    saved = workflow_evolution.read_json(path, {})
    if saved:
        expected = {
            "schema_version": 5,
            "train_pool": train_pool,
            "validation_pool": validation_pool,
            "train_batch_size": train_batch_size,
            "validation_size": validation_size,
            "selection_epsilon": float(selection_epsilon),
            "train_sampling": "independent_batches_with_replacement_across_rounds",
            "validation_problems": validation_pool,
            "utility_basis": CPE_UTILITY_BASIS,
            "interaction_cost": {
                "max_exchanges": DEFAULT_CPE_MAX_EXCHANGES,
                "total_token_reference": DEFAULT_CPE_TOTAL_TOKEN_REFERENCE,
                "total_latency_max_seconds": (
                    DEFAULT_CPE_TOTAL_LATENCY_MAX_SECONDS
                ),
                "exchange_weight": DEFAULT_CPE_EXCHANGE_COST_WEIGHT,
                "token_weight": DEFAULT_CPE_TOKEN_COST_WEIGHT,
                "latency_weight": DEFAULT_CPE_LATENCY_COST_WEIGHT,
                "penalty_weight": DEFAULT_CPE_COST_PENALTY_WEIGHT,
            },
        }
        mismatches = [key for key, value in expected.items() if saved.get(key) != value]
        if sampling_seed is not None and saved.get("sampling_seed") != sampling_seed:
            mismatches.append("sampling_seed")
        if mismatches:
            raise ValueError(
                "Cannot resume CPE with changed sampling configuration: "
                + ", ".join(sorted(set(mismatches)))
            )
        return saved

    if train_batch_size > len(train_pool):
        raise ValueError("CPE train batch size exceeds the training pool")
    if validation_size != len(validation_pool):
        raise ValueError(
            "CPE validation size must equal the complete validation pool size "
            f"({len(validation_pool)})"
        )
    seed = (
        int(sampling_seed)
        if sampling_seed is not None
        else random.SystemRandom().randrange(0, 2**63)
    )
    state = {
        "schema_version": 5,
        "sampling_seed": seed,
        "train_pool": train_pool,
        "validation_pool": validation_pool,
        "train_batch_size": train_batch_size,
        "validation_size": validation_size,
        "selection_epsilon": float(selection_epsilon),
        "validation_problems": list(validation_pool),
        "train_sampling": "independent_batches_with_replacement_across_rounds",
        "utility_basis": CPE_UTILITY_BASIS,
        "interaction_cost": {
            "max_exchanges": DEFAULT_CPE_MAX_EXCHANGES,
            "total_token_reference": DEFAULT_CPE_TOTAL_TOKEN_REFERENCE,
            "total_latency_max_seconds": DEFAULT_CPE_TOTAL_LATENCY_MAX_SECONDS,
            "exchange_weight": DEFAULT_CPE_EXCHANGE_COST_WEIGHT,
            "token_weight": DEFAULT_CPE_TOKEN_COST_WEIGHT,
            "latency_weight": DEFAULT_CPE_LATENCY_COST_WEIGHT,
            "penalty_weight": DEFAULT_CPE_COST_PENALTY_WEIGHT,
        },
        "rounds": {},
        "patch_history": [],
        "current_policy": None,
        "best_policy": None,
        "training_elites": [],
        "validation_stagnation_rounds": [],
        "created_at": now(),
        "updated_at": now(),
    }
    workflow_evolution.write_json(path, state)
    return state


def reserve_cpe_train_batch(state: dict[str, Any], round_number: int) -> list[str]:
    """Sample a fresh batch per round and return all tasks to the pool afterward."""
    rounds = state.setdefault("rounds", {})
    round_state = rounds.setdefault(str(round_number), {})
    existing = round_state.get("train_batch")
    if isinstance(existing, list) and existing:
        return [str(item) for item in existing]

    pool = [str(item) for item in state["train_pool"]]
    batch_size = int(state["train_batch_size"])
    seed = int(state["sampling_seed"])
    batch = random.Random(f"{seed}:round:{round_number}").sample(pool, batch_size)
    round_state["train_batch"] = batch
    round_state["batch_reserved_at"] = now()
    state["updated_at"] = now()
    return batch


def reserve_cpe_initial_train_batch(state: dict[str, Any]) -> list[str]:
    """Reserve one shared batch for the two initial training parents."""
    existing = state.get("initial_training_batch")
    if isinstance(existing, list) and existing:
        return [str(item) for item in existing]

    pool = [str(item) for item in state["train_pool"]]
    batch_size = int(state["train_batch_size"])
    seed = int(state["sampling_seed"])
    batch = random.Random(f"{seed}:initial_training").sample(pool, batch_size)
    state["initial_training_batch"] = batch
    state["initial_training_batch_reserved_at"] = now()
    state["updated_at"] = now()
    return batch


def cpe_accepts(candidate_score: float, reference_score: float, epsilon: float) -> bool:
    """Apply CPE's strict improvement gate with an explicit tolerance."""
    return float(candidate_score) > float(reference_score) + float(epsilon)


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
    if not isinstance(max_exchanges, int) or max_exchanges < 1:
        raise ValueError("interaction workflow max_exchanges must be a positive integer")
    if (
        MAX_WORKFLOW_EXCHANGES is not None
        and max_exchanges > MAX_WORKFLOW_EXCHANGES
    ):
        raise ValueError(
            "interaction workflow max_exchanges exceeds the configured limit "
            f"({MAX_WORKFLOW_EXCHANGES})"
        )
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
    """Keep the two seeds and the all-history mean-utility champion."""
    nodes = workflow_nodes(results)
    initial = sorted(
        (
            node
            for node in nodes
            if node.get("evolution_operator") == "initial_strategy"
        ),
        key=lambda item: int(item["round"]),
    )[:CPE_TRAINING_PARENT_COUNT]
    best = max(
        nodes,
        key=lambda item: (float(item["utility"]), -int(item["round"])),
        default=None,
    )
    selected = [{**node, "parent_archive_roles": [
        {"role": "initial_parent", "seed_index": seed_index}
    ]} for seed_index, node in enumerate(initial, 1)]
    if best is not None:
        best_round = int(best["round"])
        archived = next(
            (node for node in selected if int(node["round"]) == best_round), None
        )
        role = {
            "role": "global_best_parent",
            "scope": "historical",
            "objective": "average_utility",
        }
        if archived is None:
            selected.append({**best, "parent_archive_roles": [role]})
        else:
            archived["parent_archive_roles"].append(role)
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
                "average_dimension_scores": node.get(
                    "average_dimension_scores", {}
                ),
                "parent_roles": node.get("parent_archive_roles", []),
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


CPE_WITHHELD_JUDGE_FIELDS = frozenset(
    {
        "average_score",
        "average_dimension_scores",
        "dimension_scores",
        "judge_feedback",
        "judge_groundedness_weakness_summary",
        "judge_stability_result",
        "original_report_utility",
        "refined_report_utility",
        "quality_gain",
        "utility_gain",
    }
)


def assert_no_cpe_judge_evidence(value: Any, path: str = "evidence") -> None:
    """Prevent task-level ModelingBench Judge outputs entering a CPE prompt."""
    if isinstance(value, dict):
        leaked = sorted(CPE_WITHHELD_JUDGE_FIELDS & set(value))
        if leaked:
            raise ValueError(f"CPE optimizer evidence leaks Judge fields at {path}: {leaked}")
        for key, child in value.items():
            assert_no_cpe_judge_evidence(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            assert_no_cpe_judge_evidence(child, f"{path}[{index}]")


def cpe_training_parent_evidence(
    result: dict[str, Any],
    parent_rank: int,
    problems: dict,
    evidence_dir: Path,
    args,
) -> dict[str, Any]:
    """Expose one training parent and its rollouts without Judge outputs."""
    training_runs = []
    for run in result.get("problem_results", []):
        problem_id = str(run["problem_id"])
        problem = problems[problem_id]
        run_evidence = {
            "problem_id": problem_id,
            "title": problem.get("title", problem_id),
            "question": problem["question"],
            "artifacts": optimizer_interaction_artifacts(Path(run["run_dir"])),
        }
        summary = summarize_interaction_report_changes(run, evidence_dir, args)
        if summary:
            run_evidence["interaction_report_change_summary"] = summary
        training_runs.append(run_evidence)
    evidence = {
        "parent_rank": parent_rank,
        "workflow_id": result["workflow_id"],
        "workflow": optimizer_workflow(result["workflow"]),
        "net_utility_on_current_training_batch": float(result["utility"]),
        "training_evidence": {
            "round": int(result["round"]),
            "training_runs": training_runs,
            "average_interaction_cost": float(result.get("interaction_cost", 0.0)),
            "average_interaction_penalty": float(
                result.get("interaction_penalty", 0.0)
            ),
            "interaction_cost_parameters": result.get(
                "interaction_cost_parameters", {}
            ),
        },
    }
    assert_no_cpe_judge_evidence(evidence)
    return evidence


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

Workflow interaction evidence (task-level ModelingBench Judge outputs withheld):
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


def evolve_cpe_dialogue_operator(
    workflows_dir: Path,
    args,
    evidence: list[dict[str, Any]],
    trigger_round: int,
    trigger_reason: str,
    trigger_details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Evolve and persist one standalone operator from Judge-free CPE evidence."""
    assert_no_cpe_judge_evidence(evidence)
    events = load_evolved_operator_events(workflows_dir)
    event_number = len(events) + 1
    safe_reason = re.sub(r"[^a-z0-9]+", "_", trigger_reason.lower()).strip("_")
    event_dir = (
        workflows_dir
        / "operator_evolution"
        / f"event_{event_number:02d}_round_{trigger_round}_{safe_reason}"
    )
    event_dir.mkdir(parents=True, exist_ok=True)
    existing = available_dialogue_operators(workflows_dir)
    operator_prompt_base = build_operator_evolution_prompt(existing, evidence)
    last_error: Exception | None = None
    for attempt in range(1, args.optimizer_retries + 1):
        retry = (
            "\nThe previous proposal was rejected. Produce a different information "
            f"function. Rejection: {last_error}\n"
            if last_error
            else ""
        )
        prompt = operator_prompt_base + retry
        (event_dir / f"operator_prompt_attempt_{attempt}.md").write_text(
            prompt, encoding="utf-8"
        )
        (event_dir / "operator_prompt.md").write_text(prompt, encoding="utf-8")
        try:
            candidate = interaction.local.optimizer_response(
                {
                    "model": args.opt_model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "Return one concise valid JSON dialogue operator.",
                        },
                        {"role": "user", "content": prompt},
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
                {
                    key: candidate[key]
                    for key in ("name", "purpose", "rule", "output")
                },
                ensure_ascii=False,
                sort_keys=True,
            )
            candidate["operator_id"] = "dialogue_operator_" + hashlib.sha1(
                semantic.encode("utf-8")
            ).hexdigest()[:12]
            event = {
                "trigger_after_round": trigger_round,
                "trigger_reason": trigger_reason,
                "trigger_details": trigger_details or {},
                "judge_outputs_withheld": True,
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
                f"{trigger_round} ({trigger_reason})",
                flush=True,
            )
            return event
        except Exception as error:
            last_error = error
            print(
                f"CPE dialogue operator proposal attempt {attempt}/"
                f"{args.optimizer_retries} failed: {error}",
                flush=True,
            )
    raise RuntimeError("Could not produce a novel valid CPE dialogue operator") from last_error


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

Workflow parent-input archive. It contains both initial workflows and the
all-history global-best workflow by mean utility across every completed round.
If an initial workflow is also the historical best, it appears only once and
its `parent_roles` field carries both roles. All listed workflows must be
considered:
{json.dumps(evidence, ensure_ascii=False, indent=2)}

Each evidence node contains its mean validation utility and average dimension
scores. Its validation runs
contain the complete expert dialogue, an at-most-50-character summary of report
changes directly attributable to interaction, and LLM weakness summaries only
for non-perfect `analysis_groundedness` and `modeling_groundedness` Judge
feedback. Other Judge dimensions are omitted. Compare the two seed mechanisms
explicitly and use the all-history global best as evidence of successful
evolution.
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


def cpe_operator_evidence(
    training_parents: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Keep workflows and interaction trajectories while removing fitness values."""
    evidence = copy.deepcopy(training_parents)
    for parent in evidence:
        parent.pop("net_utility_on_current_training_batch", None)
    assert_no_cpe_judge_evidence(evidence)
    return evidence


def build_cpe_workflow_evolution_prompt(
    training_parents: list[dict[str, Any]],
    validation_champion: dict[str, Any],
    patch_history: list[dict[str, Any]],
    dialogue_operators: dict[str, dict] | None = None,
) -> str:
    """Build a CPE prompt with explicit train/validation information barriers."""
    if len(training_parents) != CPE_TRAINING_PARENT_COUNT:
        raise ValueError(
            f"CPE workflow evolution requires {CPE_TRAINING_PARENT_COUNT} "
            "training parents"
        )
    assert_no_cpe_judge_evidence(training_parents)
    dialogue_operators = dialogue_operators or available_dialogue_operators()
    visible_history = [
        {
            "round": event.get("round"),
            "candidate_workflow_id": event.get("candidate_workflow_id"),
            "parent_train_net_utilities": event.get(
                "parent_train_net_utilities", []
            ),
            "candidate_train_net_utility": event.get(
                "candidate_train_net_utility"
            ),
            "train_accepted": event.get("train_accepted"),
        }
        for event in patch_history[-8:]
    ]
    return f"""Evolve one executable human-expert interaction workflow
for mathematical-modeling report refinement. Treat the workflow text as the
communication policy: change only how the modeling agent audits, asks the human
expert, translates the reply, validates consequences, follows up, and stops.

Two training-parent workflows were selected as the strongest policies from the
preceding training stage and reevaluated on the same sampled training batch.
Each parent contains its workflow, aggregate net utility, public task statements,
complete expert dialogue, interaction-attributable report-change summaries, and
interaction-cost information. Task-level ModelingBench Judge scores, dimension
scores, Judge feedback, and Judge-derived weakness summaries are intentionally
withheld. Compare both parents, then choose the evolution mode yourself from the
evidence:
- crossover: combine compatible mechanisms or complementary strengths from both
  parents into one behaviorally coherent workflow;
- mutation: choose either parent as the primary base and make a targeted
  behavioral change when recombination would add conflict or unnecessary
  complexity. In this mode, use the other parent as comparative evidence rather
  than requiring it to donate a workflow component.
Do not choose randomly, alternate modes mechanically, or force crossover when a
focused mutation is better. In either mode, do not ignore either parent's
training evidence:
{json.dumps(training_parents, ensure_ascii=False, indent=2)}

Historical validation champion. This record intentionally contains only its
communication workflow and mean net utility:
{json.dumps(validation_champion, ensure_ascii=False, indent=2)}

Recent training-only decision history:
{json.dumps(visible_history, ensure_ascii=False, indent=2)}

Use the two parents' training interactions to identify contrasting communication
failures and transferable successes. Use their aggregate net utilities and the
training-only decision history as coarse fitness signals. Propose a targeted
behavioral patch rather than a task-specific solution. Validation task identities,
trajectories, dimension scores, reports, dialogues, and decision history are
withheld; do not infer them or optimize for individual validation tasks. Do not
infer or reconstruct withheld ModelingBench Judge judgments from the task text.

The modeling agent retains all calculation, implementation, external-data
validation, simulation, and report-writing responsibility. The workflow may use
one to three expert exchanges. Every later exchange must build on an earlier
reply and have a distinct decision-relevant purpose. Keep the workflow general
and compact, and never copy task-specific facts, entities, parameters, methods,
or conclusions from the rollouts.

Available dialogue operators (optional qualitative information functions):
{json.dumps(dialogue_operators, ensure_ascii=False, indent=2)}

Return only one JSON object with name, purpose, entry_action, actions,
max_exchanges, stop_condition, evolution_mode, changed_components, and
evolution_rationale. evolution_mode must be exactly `crossover` or `mutation`.
Use two to eight ordered actions. Each action contains action_id, action_type,
and rule, and at least one action has action_type expert_exchange. Encode the
targeted patch in the returned full workflow. In evolution_rationale, explain
why the selected mode fits the two parents' evidence, how both parents were
considered, and which training signal motivated each changed component.
"""


def propose_cpe_workflow(
    training_parents: list[dict[str, Any]],
    validation_champion: dict[str, Any],
    previous_results: list[dict],
    patch_history: list[dict[str, Any]],
    round_number: int,
    round_dir: Path,
    args,
    dialogue_operator_evolution: bool = True,
) -> dict[str, Any]:
    """Evolve from two Judge-free training parents under CPE boundaries."""
    workflow_prompt_base = build_cpe_workflow_evolution_prompt(
        training_parents,
        validation_champion,
        patch_history,
        available_dialogue_operators(
            round_dir.parent if dialogue_operator_evolution else None
        ),
    )
    previous = workflow_nodes(previous_results)
    last_error: Exception | None = None
    similarity_rejections = 0
    operator_event = None
    for attempt in range(1, args.optimizer_retries + 1):
        retry = (
            "\nThe previous proposal was rejected. Return a different targeted "
            f"behavioral patch. Rejection: {last_error}\n"
            if last_error
            else ""
        )
        prompt = workflow_prompt_base + retry
        (round_dir / f"evolution_prompt_attempt_{attempt}.md").write_text(
            prompt, encoding="utf-8"
        )
        (round_dir / "evolution_prompt.md").write_text(prompt, encoding="utf-8")
        try:
            candidate = interaction.local.optimizer_response(
                {
                    "model": args.opt_model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "Return one concise valid JSON workflow object.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": min(0.2 + 0.15 * (attempt - 1), 0.8),
                    "max_tokens": 3000,
                    "response_format": {"type": "json_object"},
                },
                args,
            )
            candidate = without_removed_workflow_fields(candidate)
            workflow_evolution.write_json(
                round_dir / f"evolution_response_attempt_{attempt}.json", candidate
            )
            workflow_evolution.write_json(round_dir / "evolution_response.json", candidate)
            changed = candidate.get("changed_components")
            if not isinstance(changed, list) or not any(
                str(item).strip() for item in changed
            ):
                raise ValueError("optimizer did not identify a changed workflow component")
            evolution_mode = str(candidate.get("evolution_mode", "")).strip().lower()
            if evolution_mode not in {"crossover", "mutation"}:
                raise ValueError(
                    "optimizer evolution_mode must be crossover or mutation"
                )
            candidate["evolution_mode"] = evolution_mode
            validate_workflow(candidate)
            candidate["workflow_id"] = workflow_id(candidate)
            similarities = [
                (node["round"], workflow_similarity(candidate, node["workflow"]))
                for node in previous
            ]
            duplicate = max(similarities, key=lambda item: item[1], default=None)
            if duplicate and duplicate[1] >= args.candidate_similarity_threshold:
                similarity_rejections += 1
                similarity_error = ValueError(
                    "candidate workflow is too similar to evaluated round "
                    f"{duplicate[0]} (similarity={duplicate[1]:.4f})"
                )
                if (
                    dialogue_operator_evolution
                    and similarity_rejections
                    == SIMILARITY_REJECTIONS_FOR_OPERATOR_EVOLUTION
                ):
                    operator_event = evolve_cpe_dialogue_operator(
                        round_dir.parent,
                        args,
                        cpe_operator_evidence(training_parents),
                        round_number,
                        "workflow_similarity_retry_limit",
                        {
                            "similarity_rejections": similarity_rejections,
                            "candidate_similarity_threshold": (
                                args.candidate_similarity_threshold
                            ),
                            "most_similar_round": duplicate[0],
                            "similarity": duplicate[1],
                        },
                    )
                    workflow_prompt_base = build_cpe_workflow_evolution_prompt(
                        training_parents,
                        validation_champion,
                        patch_history,
                        available_dialogue_operators(round_dir.parent),
                    )
                raise similarity_error
            candidate.update(
                {
                    "evolution_operator": "cpe_batch_reflection_patch",
                    "created_round": round_number,
                    "parent_workflow_ids": [
                        parent["workflow_id"] for parent in training_parents
                    ],
                    "training_batch": [
                        item["problem_id"]
                        for item in training_parents[0]
                        .get("training_evidence", {})
                        .get("training_runs", [])
                    ],
                }
            )
            if dialogue_operator_evolution:
                candidate["operator_evolution_trigger"] = (
                    {
                        "trigger_reason": operator_event["trigger_reason"],
                        "operator_id": operator_event["operator"]["operator_id"],
                    }
                    if operator_event is not None
                    else None
                )
            return candidate
        except Exception as error:
            last_error = error
            print(
                f"CPE workflow proposal attempt {attempt}/{args.optimizer_retries} "
                f"failed: {error}",
                flush=True,
            )
    raise RuntimeError("Could not produce a novel valid CPE workflow") from last_error


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
    workflow = ACTIVE_WORKFLOWS.get(
        (str(Path(experiment).resolve()), round_number)
    )
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
    parser.add_argument("--cpe-split-file", type=Path, default=DEFAULT_CPE_SPLIT_PATH)
    parser.add_argument(
        "--train-batch-size",
        type=int,
        default=DEFAULT_CPE_TRAIN_BATCH_SIZE,
        help=(
            "CPE distinct tasks per round; all tasks return to the pool before "
            "the next round."
        ),
    )
    parser.add_argument(
        "--validation-size",
        type=int,
        default=DEFAULT_CPE_VALIDATION_SIZE,
        help="Must equal the complete validation split size (currently 10).",
    )
    parser.add_argument("--sampling-seed", type=int)
    parser.add_argument(
        "--selection-epsilon", type=float, default=DEFAULT_CPE_SELECTION_EPSILON
    )
    return parser.parse_args()


def restore_cpe_net_utilities(results: list[dict]) -> list[dict]:
    """Restore net CPE utility after the shared absolute-score normalizer."""
    for item in results:
        if item.get("utility_basis") not in {
            CPE_UTILITY_BASIS_QUALITY_GAIN,
            CPE_UTILITY_BASIS_ABSOLUTE_SCORE,
        }:
            continue
        problem_results = item.get("problem_results", [])
        net_utilities = [
            float(result["net_utility"])
            for result in problem_results
            if isinstance(result.get("net_utility"), (int, float))
        ]
        if len(net_utilities) == len(problem_results) and net_utilities:
            item["net_utility"] = sum(net_utilities) / len(net_utilities)
            item["utility"] = item["net_utility"]
    return results


def normalized_results(results_path: Path) -> list[dict]:
    results = restore_cpe_net_utilities(
        interaction.normalize_results(workflow_evolution.read_json(results_path, []))
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
    ACTIVE_WORKFLOWS[(str(Path(experiment).resolve()), round_number)] = workflow
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


def execute_cpe_evaluation(
    experiment: Path,
    round_number: int,
    phase: str,
    split_name: str,
    problem_ids: list[str],
    workflow: dict[str, Any],
    fixed_rubric: dict[str, Any],
    problems: dict,
    run_args,
    enforce_gate: bool,
    original_scores: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], list[dict]]:
    """Evaluate one policy in an isolated CPE phase with restart checkpoints."""
    evaluation_experiment = (
        experiment / "cpe_evaluations" / f"round_{round_number}" / phase
    )
    result_path = (
        evaluation_experiment / "workflows" / f"round_{round_number}" / "result.json"
    )
    existing = workflow_evolution.read_json(result_path, {})
    evaluation_args = copy.copy(run_args)
    evaluation_args.evaluation_problem_ids = tuple(problem_ids)
    if completed_round_result(
        [existing] if existing else [],
        round_number,
        len(problem_ids),
        evaluation_args.validation_repetitions,
    ):
        apply_cpe_net_utility(existing, original_scores)
        workflow_evolution.write_json(result_path, existing)
        return existing, []
    result, failures = execute_workflow_round(
        evaluation_experiment,
        round_number,
        workflow,
        fixed_rubric,
        problems,
        evaluation_args,
        existing or None,
        enforce_gate,
    )
    result.update(
        {
            "cpe_phase": phase,
            "evaluation_split": split_name,
            "evaluation_problems": list(problem_ids),
        }
    )
    apply_cpe_net_utility(result, original_scores)
    workflow_evolution.write_json(result_path, result)
    return result, failures


def persist_round_result(
    experiment: Path, results_path: Path, result: dict
) -> list[dict]:
    results = normalized_results(results_path)
    results = [item for item in results if item.get("round") != result["round"]]
    results.append(result)
    results = restore_cpe_net_utilities(
        interaction.normalize_results(
            sorted(results, key=lambda item: item["round"])
        )
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


def persist_cpe_round_result(results_path: Path, result: dict[str, Any]) -> list[dict]:
    """Persist a CPE round whose sampled tasks can differ from other rounds."""
    results = normalized_results(results_path)
    results = [item for item in results if item.get("round") != result["round"]]
    results.append(result)
    results = sorted(results, key=lambda item: int(item["round"]))
    workflow_evolution.write_json(
        results_path.parent / f"round_{result['round']}" / "result.json", result
    )
    workflow_evolution.write_json(results_path, results)
    write_execution_time_excel(results_path.parent / "round_execution_times.xlsx", results)
    print(
        f"Round {result['round']} CPE train net utility: "
        f"{result['train_post_utility']:.6f}; "
        f"train accepted={result['train_accepted']}; "
        f"validation accepted={result.get('validation_accepted')}",
        flush=True,
    )
    return results


def initialize_cpe_policies(
    state: dict[str, Any],
    seed_results: list[dict[str, Any]],
) -> None:
    """Initialize two training parents from one shared initial train batch."""
    if (
        state.get("current_policy")
        and state.get("best_policy")
        and len(state.get("training_elites", [])) == CPE_TRAINING_PARENT_COUNT
    ):
        return
    if len(seed_results) != CPE_TRAINING_PARENT_COUNT:
        raise ValueError("CPE initialization requires exactly two seed results")
    ranked = sorted(
        seed_results,
        key=lambda item: (-float(item["utility"]), int(item["round"])),
    )
    best = ranked[0]
    policy = {
        "source_round": int(best["round"]),
        "workflow_id": best["workflow_id"],
        "workflow": without_removed_workflow_fields(best["workflow"]),
        "train_utility": float(best["utility"]),
        "utility_basis": CPE_UTILITY_BASIS,
    }
    state["current_policy"] = copy.deepcopy(policy)
    state["best_policy"] = None
    state["training_elites"] = [
        {
            "rank": rank,
            "source_round": int(item["round"]),
            "source_phase": "initial_train_parent",
            "workflow_id": item["workflow_id"],
            "workflow": without_removed_workflow_fields(item["workflow"]),
            "selection_utility": float(item["utility"]),
            "selection_basis": "initial_shared_training_batch_net_utility",
        }
        for rank, item in enumerate(
            ranked[:CPE_TRAINING_PARENT_COUNT], start=1
        )
    ]
    state["initial_seed_train"] = [
        {
            "round": int(item["round"]),
            "workflow_id": item["workflow_id"],
            "train_utility": float(item["utility"]),
        }
        for item in sorted(seed_results, key=lambda item: int(item["round"]))
    ]
    state["updated_at"] = now()


def run_cpe_collapsed_initial_parent_evaluations(
    experiment: Path,
    initial_problem_ids: list[str],
    initial_population: list[dict[str, Any]],
    fixed_rubric: dict[str, Any],
    problems: dict,
    run_args,
    args,
    state: dict[str, Any],
    original_scores: dict[str, dict[str, Any]],
) -> None:
    """Evaluate both seed parents inside CPE round 1 before creating its child.

    This opt-in path deliberately keeps the parent training and validation
    artifacts separate from the round-level result.  The latter remains the
    evolved child, just as it does in every later CPE round.
    """
    if len(initial_population) != CPE_TRAINING_PARENT_COUNT:
        raise ValueError("Collapsed CPE initialization requires two seed workflows")
    initialization_mode = "collapsed_initial_parents_in_round_1"
    saved_mode = state.get("initialization_mode")
    if saved_mode not in (None, initialization_mode):
        raise ValueError(
            "This experiment was created with a different CPE initialization mode; "
            "start a new experiment directory instead of resuming it."
        )
    existing_rounds = normalized_results(experiment / "workflows" / "results.json")
    if (
        saved_mode is None
        and any(int(item.get("round", 0)) in (1, 2) for item in existing_rounds)
    ):
        raise ValueError(
            "This experiment contains legacy initial-parent rounds. Start a new "
            "experiment directory for collapsed round-1 CPE scheduling."
        )
    state["initialization_mode"] = initialization_mode
    validation_problems = [str(item) for item in state["validation_problems"]]
    parent_train_results: list[dict[str, Any] | None] = [None] * CPE_TRAINING_PARENT_COUNT
    print(
        "Running two initial training-parent workflows in parallel "
        "inside CPE round 1",
        flush=True,
    )
    with ThreadPoolExecutor(max_workers=CPE_TRAINING_PARENT_COUNT) as executor:
        futures = {
            executor.submit(
                execute_cpe_evaluation,
                experiment,
                1,
                f"initial_train_parent_{parent_rank}",
                "train",
                initial_problem_ids,
                without_removed_workflow_fields(parent),
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
                    f"{len(failures)} initial training-parent run(s) failed the "
                    "substantive gate"
                )
            parent_train_results[parent_rank - 1] = result
    parent_train_results = [
        result for result in parent_train_results if result is not None
    ]
    if len(parent_train_results) != CPE_TRAINING_PARENT_COUNT:
        raise RuntimeError("Initial CPE parent training did not produce two results")

    original_scores.update(
        ensure_cpe_original_report_scores(experiment, validation_problems, run_args)
    )
    parent_validation_results: list[dict[str, Any] | None] = [None] * CPE_TRAINING_PARENT_COUNT
    print(
        "Running the two initial parent validations in parallel inside CPE round 1",
        flush=True,
    )
    with ThreadPoolExecutor(max_workers=CPE_TRAINING_PARENT_COUNT) as executor:
        futures = {
            executor.submit(
                execute_cpe_evaluation,
                experiment,
                1,
                f"initial_validation_parent_{parent_rank}",
                "validation",
                validation_problems,
                without_removed_workflow_fields(parent),
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
                    f"{len(failures)} initial parent validation run(s) failed the "
                    "substantive gate"
                )
            parent_validation_results[parent_rank - 1] = result
    parent_validation_results = [
        result for result in parent_validation_results if result is not None
    ]
    if len(parent_validation_results) != CPE_TRAINING_PARENT_COUNT:
        raise RuntimeError("Initial CPE parent validation did not produce two results")

    state["initial_parent_train_results"] = copy.deepcopy(parent_train_results)
    state["initial_parent_validation_results"] = copy.deepcopy(parent_validation_results)
    state["initial_seed_train"] = [
        {
            "round": 1,
            "workflow_id": result["workflow_id"],
            "train_utility": float(result["utility"]),
        }
        for result in parent_train_results
    ]
    state["training_elites"] = select_cpe_training_elites(parent_train_results)
    best_train = state["training_elites"][0]
    state["current_policy"] = {
        **copy.deepcopy(best_train),
        "train_utility": float(best_train["selection_utility"]),
        "utility_basis": CPE_UTILITY_BASIS,
    }
    validation_champion = max(
        parent_validation_results,
        key=lambda result: (float(result["utility"]), str(result["workflow_id"])),
    )
    state["best_policy"] = {
        "source_round": 1,
        "source_phase": "initial_validation_parent",
        "workflow_id": validation_champion["workflow_id"],
        "workflow": without_removed_workflow_fields(validation_champion["workflow"]),
        "validation_utility": float(validation_champion["utility"]),
        "utility_basis": CPE_UTILITY_BASIS,
    }
    state["updated_at"] = now()
    workflow_evolution.write_json(cpe_state_path(experiment), state)


def select_cpe_training_elites(
    eligible_results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Keep the two strongest distinct workflows on the current shared batch."""
    ranked = sorted(
        eligible_results,
        key=lambda item: (-float(item["utility"]), str(item["workflow_id"])),
    )
    selected = []
    seen = set()
    for item in ranked:
        workflow_id_value = str(item["workflow_id"])
        if workflow_id_value in seen:
            continue
        seen.add(workflow_id_value)
        selected.append(
            {
                "rank": len(selected) + 1,
                "source_round": int(item["round"]),
                "source_phase": str(item.get("cpe_phase", "train_candidate")),
                "workflow_id": workflow_id_value,
                "workflow": without_removed_workflow_fields(item["workflow"]),
                "selection_utility": float(item["utility"]),
                "selection_basis": "current_shared_training_batch_net_utility",
            }
        )
        if len(selected) == CPE_TRAINING_PARENT_COUNT:
            break
    if len(selected) != CPE_TRAINING_PARENT_COUNT:
        raise ValueError("CPE training selection did not produce two distinct elites")
    return selected


def maybe_evolve_cpe_operator_for_validation_stagnation(
    state: dict[str, Any],
    workflows_dir: Path,
    args,
    training_parents: list[dict[str, Any]],
    round_number: int,
    validation_improved: bool,
) -> dict[str, Any] | None:
    """Evolve an operator after five rounds without a validation-best gain."""
    if validation_improved:
        state["validation_stagnation_rounds"] = []
        return None
    stagnant = [
        int(value) for value in state.get("validation_stagnation_rounds", [])
    ]
    if round_number not in stagnant:
        stagnant.append(round_number)
    state["validation_stagnation_rounds"] = stagnant
    if len(stagnant) < STAGNATION_ROUNDS_FOR_OPERATOR_EVOLUTION:
        return None
    trigger_rounds = stagnant[-STAGNATION_ROUNDS_FOR_OPERATOR_EVOLUTION:]
    champion = state.get("best_policy")
    event = evolve_cpe_dialogue_operator(
        workflows_dir,
        args,
        cpe_operator_evidence(training_parents),
        round_number,
        "validation_champion_stagnation",
        {
            "stagnant_rounds": trigger_rounds,
            "historical_validation_utility": (
                float(champion["validation_utility"])
                if isinstance(champion, dict)
                else None
            ),
        },
    )
    state["validation_stagnation_rounds"] = []
    state["last_operator_evolution"] = {
        "trigger_after_round": round_number,
        "trigger_reason": event["trigger_reason"],
        "operator_id": event["operator"]["operator_id"],
    }
    return event


def ensure_cpe_baseline_reports(
    experiment: Path,
    problem_ids: list[str],
    run_args,
    baseline_report_root: Path,
) -> None:
    """Resolve only the clean drafts needed by the current sampled batch."""
    missing = []
    for problem_id in problem_ids:
        configured = Path(str(run_args.baseline_reports.get(problem_id, "")))
        report_validator = getattr(
            substantive, "baseline_report_matches_problem", None
        )
        configured_matches = configured.is_file() and (
            not callable(report_validator)
            or report_validator(problem_id, configured)
        )
        if configured_matches:
            continue
        try:
            source = substantive.resolve_baseline_report(
                problem_id, baseline_report_root
            )
        except FileNotFoundError:
            missing.append(problem_id)
        else:
            run_args.baseline_reports[problem_id] = str(source.resolve())
    if missing:
        raise FileNotFoundError(
            "Missing clean baseline reports for sampled training tasks: "
            + ", ".join(missing)
            + ". Generate these no-interaction baselines and resume the same "
            "experiment; its sampled batch is already checkpointed."
        )
    config_path = experiment / "config.json"
    config = workflow_evolution.read_json(config_path, {})
    config["baseline_reports"] = dict(run_args.baseline_reports)
    config["updated_at"] = now()
    workflow_evolution.write_json(config_path, config)


def ensure_cpe_original_report_scores(
    experiment: Path,
    problem_ids: list[str],
    run_args,
) -> dict[str, dict[str, Any]]:
    """Judge each original draft once per configured repetition and cache it."""
    score_root = experiment / "cpe_original_report_scores"
    score_root.mkdir(parents=True, exist_ok=True)

    def score_one(problem_id: str) -> tuple[str, dict[str, Any]]:
        report = Path(str(run_args.baseline_reports[problem_id])).resolve()
        problem_root = score_root / baseline.safe_path_component(problem_id)
        output = problem_root / "judge_stability.json"
        source_stability = workflow_evolution.read_json(
            report.parents[2] / "meta" / "judge_stability.json", {}
        )
        source_trials = source_stability.get("evaluations", {}).get("report", [])
        source_trial = next(
            (
                item
                for item in source_trials
                if int(item.get("trial", -1)) == 1
                and Path(str(item.get("raw_result", ""))).is_file()
            ),
            None,
        )
        seed_results = (
            {"original": Path(source_trial["raw_result"])}
            if source_trial is not None
            else None
        )
        payload = run_judge_stability.evaluate_reports_repeated(
            problem_id,
            {"original": report},
            run_args.judge_repeats,
            f"interaction-rubric-{experiment.name}-original",
            output,
            problem_root,
            experiment=experiment,
            seed_results=seed_results,
            concurrency=run_args.judge_concurrency,
            judgers=interaction.EVALUATION_DIMENSIONS,
        )
        averaged = payload["average_scores"]["round_original"]
        dimensions = interaction.objective_dimensions(
            averaged["average_dimension_scores"]
        )
        return problem_id, {
            "problem_id": problem_id,
            "report": str(report),
            "utility": interaction.objective_score(dimensions),
            "dimension_scores": dimensions,
            "judge_repeats": averaged["trial_count"],
            "judge_stability_result": str(output),
        }

    scores: dict[str, dict[str, Any]] = {}
    worker_count = min(max(1, int(run_args.concurrency)), len(problem_ids))
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        futures = {executor.submit(score_one, item): item for item in problem_ids}
        for future in as_completed(futures):
            problem_id, score = future.result()
            scores[problem_id] = score
    scores = {problem_id: scores[problem_id] for problem_id in problem_ids}
    summary_path = experiment / "workflows" / "cpe_original_report_scores.json"
    all_scores = workflow_evolution.read_json(summary_path, {})
    if not isinstance(all_scores, dict):
        all_scores = {}
    all_scores.update(scores)
    workflow_evolution.write_json(
        summary_path, all_scores
    )
    return scores


def approximate_interaction_tokens(text: str) -> int:
    """Estimate tokens without adding a tokenizer dependency to the runner."""
    cjk = sum(1 for char in text if "\u3400" <= char <= "\u9fff")
    other_non_ascii = sum(
        1 for char in text if ord(char) >= 128 and not "\u3400" <= char <= "\u9fff"
    )
    ascii_characters = sum(1 for char in text if ord(char) < 128)
    return math.ceil(cjk + other_non_ascii + ascii_characters / 4)


def expert_reply_latencies(run_dir: Path) -> dict[int, float]:
    """Read exact expert API elapsed seconds, with filesystem-time fallback."""
    run_dir = Path(run_dir)
    bridge_log = run_dir / "meta" / "expert_bridge.log"
    latencies: dict[int, float] = {}
    if bridge_log.is_file():
        for match in EXPERT_REPLY_LATENCY_PATTERN.finditer(
            bridge_log.read_text(encoding="utf-8", errors="replace")
        ):
            latencies[int(match.group(1))] = float(match.group(2))
    feedback_dir = run_dir / "output" / "logs" / "operator_feedback"
    for exchange in range(1, DEFAULT_CPE_MAX_EXCHANGES + 1):
        if exchange in latencies:
            continue
        request_path = feedback_dir / f"expert_request_{exchange}.json"
        reply_path = feedback_dir / f"expert_reply_{exchange}.json"
        if request_path.is_file() and reply_path.is_file():
            latencies[exchange] = max(
                0.0, reply_path.stat().st_mtime - request_path.stat().st_mtime
            )
    return latencies


def cpe_interaction_cost(run_dir: Path) -> dict[str, Any]:
    """Calculate the normalized interaction cost for one completed run."""
    exchanges = interaction.completed_expert_exchanges(Path(run_dir))
    if not exchanges:
        raise ValueError(f"Cannot calculate interaction cost without dialogue: {run_dir}")
    exchange_count = len(exchanges)
    total_tokens = sum(
        approximate_interaction_tokens(item["question"])
        + approximate_interaction_tokens(item["answer"])
        for item in exchanges
    )
    latencies = expert_reply_latencies(Path(run_dir))
    total_latency = sum(
        float(latencies.get(int(item["exchange"]), 0.0)) for item in exchanges
    )
    exchange_component = max(exchange_count - 1, 0) / (
        DEFAULT_CPE_MAX_EXCHANGES - 1
    )
    token_component = math.log1p(total_tokens) / math.log1p(
        DEFAULT_CPE_TOTAL_TOKEN_REFERENCE
    )
    latency_component = math.log1p(total_latency) / math.log1p(
        DEFAULT_CPE_TOTAL_LATENCY_MAX_SECONDS
    )
    cost = (
        DEFAULT_CPE_EXCHANGE_COST_WEIGHT * exchange_component
        + DEFAULT_CPE_TOKEN_COST_WEIGHT * token_component
        + DEFAULT_CPE_LATENCY_COST_WEIGHT * latency_component
    )
    return {
        "exchange_count": exchange_count,
        "total_tokens_approx": total_tokens,
        "total_expert_latency_seconds": total_latency,
        "exchange_cost_component": exchange_component,
        "token_cost_component": token_component,
        "latency_cost_component": latency_component,
        "interaction_cost": cost,
        "token_count_method": (
            "ceil(CJK + other_non_ASCII + ASCII_characters/4)"
        ),
        "latency_source": "expert_bridge_elapsed_with_file_mtime_fallback",
    }


def apply_cpe_net_utility(
    result: dict[str, Any], original_scores: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    """Apply the configured CPE score-minus-interaction-cost utility."""
    problem_results = result.get("problem_results", [])
    if not problem_results:
        raise ValueError("Cannot calculate CPE net utility without problem results")
    use_quality_gain = CPE_UTILITY_BASIS == CPE_UTILITY_BASIS_QUALITY_GAIN
    if use_quality_gain:
        missing = [
            str(item.get("problem_id"))
            for item in problem_results
            if str(item.get("problem_id")) not in original_scores
        ]
        if missing:
            raise ValueError(
                "Missing original-report scores for: " + ", ".join(missing)
            )

    gains = []
    original_utilities = []
    refined_utilities = []
    interaction_costs = []
    penalties = []
    net_utilities = []
    for item in problem_results:
        problem_id = str(item["problem_id"])
        refined_utility = float(item["average_score"])
        original_utility = (
            float(original_scores[problem_id]["utility"])
            if use_quality_gain
            else None
        )
        quality_component = (
            refined_utility - original_utility
            if original_utility is not None
            else refined_utility
        )
        repetitions = item.get("repetitions") or [item]
        run_costs = [
            cpe_interaction_cost(Path(str(repetition["run_dir"])))
            for repetition in repetitions
        ]
        interaction_cost = sum(
            float(run_cost["interaction_cost"]) for run_cost in run_costs
        ) / len(run_costs)
        penalty = DEFAULT_CPE_COST_PENALTY_WEIGHT * interaction_cost
        net_utility = quality_component - penalty
        if original_utility is not None:
            item["original_report_utility"] = original_utility
        item["refined_report_utility"] = refined_utility
        if original_utility is not None:
            item["quality_gain"] = quality_component
            item["utility_gain"] = quality_component
        item["interaction_cost"] = interaction_cost
        item["interaction_penalty"] = penalty
        item["net_utility"] = net_utility
        item["interaction_cost_runs"] = run_costs
        if original_utility is not None:
            original_utilities.append(original_utility)
        refined_utilities.append(refined_utility)
        if original_utility is not None:
            gains.append(quality_component)
        interaction_costs.append(interaction_cost)
        penalties.append(penalty)
        net_utilities.append(net_utility)

    result["absolute_utility"] = sum(refined_utilities) / len(refined_utilities)
    if original_utilities:
        result["original_report_utility"] = sum(original_utilities) / len(
            original_utilities
        )
        result["quality_gain"] = sum(gains) / len(gains)
        result["utility_gain"] = result["quality_gain"]
    result["interaction_cost"] = sum(interaction_costs) / len(
        interaction_costs
    )
    result["interaction_penalty"] = sum(penalties) / len(penalties)
    result["net_utility"] = sum(net_utilities) / len(net_utilities)
    result["utility"] = result["net_utility"]
    result["utility_basis"] = CPE_UTILITY_BASIS
    result["interaction_cost_parameters"] = {
        "max_exchanges": DEFAULT_CPE_MAX_EXCHANGES,
        "total_token_reference": DEFAULT_CPE_TOTAL_TOKEN_REFERENCE,
        "total_latency_max_seconds": DEFAULT_CPE_TOTAL_LATENCY_MAX_SECONDS,
        "exchange_weight": DEFAULT_CPE_EXCHANGE_COST_WEIGHT,
        "token_weight": DEFAULT_CPE_TOKEN_COST_WEIGHT,
        "latency_weight": DEFAULT_CPE_LATENCY_COST_WEIGHT,
        "penalty_weight": DEFAULT_CPE_COST_PENALTY_WEIGHT,
    }
    return result


def cpe_validation_champion_signal(state: dict[str, Any]) -> dict[str, Any]:
    """Expose exactly the validation champion workflow and net utility."""
    champion = state.get("best_policy")
    if not isinstance(champion, dict):
        return {
            "workflow": None,
            "utility": None,
            "status": "no_validation_champion_yet",
        }
    return {
        "workflow": optimizer_workflow(champion["workflow"]),
        "utility": float(champion["validation_utility"]),
    }


def run_cpe_evolved_rounds(
    experiment: Path,
    results_path: Path,
    initial_results: list[dict[str, Any]],
    initial_population: list[dict[str, Any]],
    fixed_rubric: dict[str, Any],
    problems: dict,
    run_args,
    args,
    state: dict[str, Any],
    original_scores: dict[str, dict[str, Any]],
    dialogue_operator_evolution: bool = True,
) -> list[dict[str, Any]]:
    """Run two-parent train gating and validation only after strict improvement."""
    seed_count = len(initial_population)
    collapsed_initial_round = CPE_COLLAPSE_INITIAL_PARENTS
    if collapsed_initial_round:
        seed_results = list(state.get("initial_parent_train_results", []))
        if len(seed_results) != CPE_TRAINING_PARENT_COUNT:
            raise ValueError(
                "Collapsed CPE initialization requires two stored parent train results"
            )
        first_evolved_round = 1
    else:
        seed_results = [
            item
            for item in initial_results
            if 1 <= int(item.get("round", 0)) <= seed_count
        ]
        initialize_cpe_policies(
            state,
            seed_results,
        )
        first_evolved_round = seed_count + 1
    workflow_evolution.write_json(cpe_state_path(experiment), state)
    results = initial_results
    validation_problems = [str(item) for item in state["validation_problems"]]

    for round_number in range(first_evolved_round, args.max_rounds + 1):
        round_state = state.setdefault("rounds", {}).setdefault(
            str(round_number), {}
        )
        if round_state.get("status") == "complete":
            stored_result = round_state.get("result")
            if isinstance(stored_result, dict):
                results = persist_cpe_round_result(results_path, stored_result)
            continue

        if round_number == first_evolved_round:
            train_batch = reserve_cpe_initial_train_batch(state)
            round_state.setdefault("train_batch", list(train_batch))
        else:
            train_batch = reserve_cpe_train_batch(state, round_number)
        workflow_evolution.write_json(cpe_state_path(experiment), state)
        ensure_cpe_baseline_reports(
            experiment,
            train_batch,
            run_args,
            Path(args.baseline_report_root),
        )
        original_scores.update(
            ensure_cpe_original_report_scores(experiment, train_batch, run_args)
        )
        round_dir = results_path.parent / f"round_{round_number}"
        round_dir.mkdir(parents=True, exist_ok=True)
        elite_policies = state.get("training_elites", [])
        if len(elite_policies) != CPE_TRAINING_PARENT_COUNT:
            raise ValueError("CPE state must contain exactly two training elites")
        workflow_evolution.write_json(
            round_dir / "training_elites_at_start.json", elite_policies
        )
        initial_parent_by_id = {
            str(result.get("workflow_id")): result for result in seed_results
        }
        reuse_initial_parent_results = (
            round_number == first_evolved_round
            and len(seed_results) == CPE_TRAINING_PARENT_COUNT
            and all(
                str(elite["workflow_id"]) in initial_parent_by_id
                for elite in elite_policies
            )
        )
        if reuse_initial_parent_results:
            print(
                "Reusing the two initial shared-training-batch parent results",
                flush=True,
            )
            parent_results = [
                copy.deepcopy(initial_parent_by_id[str(elite["workflow_id"])])
                for elite in elite_policies
            ]
        else:
            parent_results = [None] * CPE_TRAINING_PARENT_COUNT
            parent_failures = []
            print(
                "Running two training-parent workflows in parallel "
                "(per-parent problem concurrency="
                f"{getattr(run_args, 'concurrency', 1)})",
                flush=True,
            )
            with ThreadPoolExecutor(max_workers=CPE_TRAINING_PARENT_COUNT) as executor:
                futures = {
                    executor.submit(
                        execute_cpe_evaluation,
                        experiment,
                        round_number,
                        f"train_parent_{parent_rank}",
                        "train",
                        train_batch,
                        without_removed_workflow_fields(elite["workflow"]),
                        fixed_rubric,
                        problems,
                        run_args,
                        args.enforce_substantive_interaction_gate,
                        original_scores,
                    ): parent_rank
                    for parent_rank, elite in enumerate(elite_policies, start=1)
                }
                for future in as_completed(futures):
                    parent_rank = futures[future]
                    parent_result, failures = future.result()
                    parent_results[parent_rank - 1] = parent_result
                    parent_failures.extend(failures)
            parent_results = [
                result for result in parent_results if result is not None
            ]
            if len(parent_results) != CPE_TRAINING_PARENT_COUNT:
                raise RuntimeError(
                    "A parallel training-parent evaluation produced no result"
                )
            if parent_failures:
                raise RuntimeError(
                    f"{len(parent_failures)} training-parent run(s) failed the "
                    "substantive gate"
                )

        training_parent_evidence = [
            cpe_training_parent_evidence(
                result,
                parent_rank,
                problems,
                round_dir / f"train_parent_{parent_rank}_evidence",
                args,
            )
            for parent_rank, result in enumerate(parent_results, start=1)
        ]
        workflow_evolution.write_json(
            round_dir / "training_parent_evidence.json", training_parent_evidence
        )

        saved_candidate = without_removed_workflow_fields(
            workflow_evolution.read_json(round_dir / "workflow.json", {})
        )
        candidate = saved_candidate or propose_cpe_workflow(
            training_parent_evidence,
            cpe_validation_champion_signal(state),
            results,
            state.get("patch_history", []),
            round_number,
            round_dir,
            args,
            dialogue_operator_evolution,
        )
        workflow_evolution.write_json(round_dir / "workflow.json", candidate)

        train_candidate, candidate_failures = execute_cpe_evaluation(
            experiment,
            round_number,
            "train_candidate",
            "train",
            train_batch,
            candidate,
            fixed_rubric,
            problems,
            run_args,
            args.enforce_substantive_interaction_gate,
            original_scores,
        )
        if candidate_failures:
            raise RuntimeError(
                f"{len(candidate_failures)} train-candidate run(s) failed the "
                "substantive gate"
            )

        parent_utilities = [float(result["utility"]) for result in parent_results]
        train_reference_utility = max(parent_utilities)
        train_accepted = cpe_accepts(
            train_candidate["utility"],
            train_reference_utility,
            args.selection_epsilon,
        )
        next_elites = select_cpe_training_elites(
            [*parent_results, train_candidate] if train_accepted else parent_results
        )
        state["training_elites"] = next_elites
        state["current_policy"] = {
            **copy.deepcopy(next_elites[0]),
            "train_utility": float(next_elites[0]["selection_utility"]),
            "utility_basis": CPE_UTILITY_BASIS,
        }
        validation_result = None
        validation_accepted = None
        if train_accepted:
            original_scores.update(
                ensure_cpe_original_report_scores(
                    experiment, validation_problems, run_args
                )
            )
            validation_result, validation_failures = execute_cpe_evaluation(
                experiment,
                round_number,
                "validation",
                "validation",
                validation_problems,
                candidate,
                fixed_rubric,
                problems,
                run_args,
                args.enforce_substantive_interaction_gate,
                original_scores,
            )
            if validation_failures:
                raise RuntimeError(
                    f"{len(validation_failures)} validation run(s) failed the "
                    "substantive gate"
                )
            existing_champion = state.get("best_policy")
            validation_accepted = (
                True
                if not isinstance(existing_champion, dict)
                else cpe_accepts(
                    validation_result["utility"],
                    existing_champion["validation_utility"],
                    args.selection_epsilon,
                )
            )
            if validation_accepted:
                state["best_policy"] = {
                    "source_round": round_number,
                    "workflow_id": candidate["workflow_id"],
                    "workflow": without_removed_workflow_fields(candidate),
                    "validation_utility": float(validation_result["utility"]),
                    "utility_basis": CPE_UTILITY_BASIS,
                }

        patch_event = {
            "round": round_number,
            "candidate_workflow_id": candidate["workflow_id"],
            "evolution_mode": candidate.get("evolution_mode"),
            "training_parent_workflow_ids": [
                result["workflow_id"] for result in parent_results
            ],
            "changed_components": candidate.get("changed_components", []),
            "evolution_rationale": candidate.get("evolution_rationale", ""),
            "parent_train_net_utilities": parent_utilities,
            "candidate_train_net_utility": float(train_candidate["utility"]),
            "train_pre_utility": max(parent_utilities),
            "train_acceptance_reference_utility": train_reference_utility,
            "train_acceptance_rule": "must_beat_all_training_parents",
            "train_post_utility": float(train_candidate["utility"]),
            "train_pre_net_utility": max(parent_utilities),
            "train_post_net_utility": float(train_candidate["utility"]),
            "train_accepted": train_accepted,
            "training_elites_after_selection": copy.deepcopy(next_elites),
            "validation_utility": (
                float(validation_result["utility"])
                if validation_result is not None
                else None
            ),
            "validation_accepted": validation_accepted,
        }
        history = [
            event
            for event in state.setdefault("patch_history", [])
            if int(event.get("round", -1)) != round_number
        ]
        history.append(patch_event)
        state["patch_history"] = history

        if dialogue_operator_evolution:
            if candidate.get("operator_evolution_trigger"):
                state["validation_stagnation_rounds"] = []
                stagnation_operator_event = None
            else:
                stagnation_operator_event = (
                    maybe_evolve_cpe_operator_for_validation_stagnation(
                        state,
                        results_path.parent,
                        args,
                        training_parent_evidence,
                        round_number,
                        validation_accepted is True,
                    )
                )
            patch_event["stagnation_operator_evolution"] = (
                {
                    "trigger_reason": stagnation_operator_event["trigger_reason"],
                    "operator_id": stagnation_operator_event["operator"]["operator_id"],
                }
                if stagnation_operator_event is not None
                else None
            )

        result = {
            **train_candidate,
            "round": round_number,
            "workflow": candidate,
            "workflow_id": candidate["workflow_id"],
            "evolution_operator": "cpe_batch_reflection_patch",
            "evaluation_split": "train",
            "training_batch": train_batch,
            "training_parent_workflow_ids": patch_event[
                "training_parent_workflow_ids"
            ],
            "parent_train_net_utilities": parent_utilities,
            "candidate_train_net_utility": float(train_candidate["utility"]),
            "train_pre_utility": max(parent_utilities),
            "train_post_utility": float(train_candidate["utility"]),
            "train_accepted": train_accepted,
            "training_elites_after_selection": copy.deepcopy(next_elites),
            "validation_utility": patch_event["validation_utility"],
            "validation_accepted": validation_accepted,
            "validation_result_path": (
                str(
                    experiment
                    / "cpe_evaluations"
                    / f"round_{round_number}"
                    / "validation"
                    / "workflows"
                    / f"round_{round_number}"
                    / "result.json"
                )
                if validation_result is not None
                else None
            ),
            "best_validation_utility": (
                float(state["best_policy"]["validation_utility"])
                if isinstance(state.get("best_policy"), dict)
                else None
            ),
            "best_workflow_id": (
                state["best_policy"]["workflow_id"]
                if isinstance(state.get("best_policy"), dict)
                else None
            ),
            "cpe_round_complete": True,
        }
        round_state.update(
            {
                "status": "complete",
                "completed_at": now(),
                "result": result,
            }
        )
        state["updated_at"] = now()
        workflow_evolution.write_json(cpe_state_path(experiment), state)
        workflow_evolution.write_json(
            results_path.parent / "best_workflow.json", state["best_policy"]
        )
        workflow_evolution.write_json(
            results_path.parent / "cpe_patch_history.json", state["patch_history"]
        )
        results = persist_cpe_round_result(results_path, result)

    workflow_evolution.write_json(
        results_path.parent / "best_workflow.json", state["best_policy"]
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


def main(
    *,
    cpe_mode: bool = False,
    compact_experiment_inputs: bool = False,
    dialogue_operator_evolution: bool = True,
) -> None:
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
    if args.selection_epsilon < 0:
        raise ValueError("selection epsilon must be non-negative")
    if (
        cpe_mode
        and MIN_CPE_EVOLUTION_ROUNDS is not None
        and args.max_rounds < MIN_CPE_EVOLUTION_ROUNDS
    ):
        raise ValueError(
            "CPE mode requires at least "
            f"{MIN_CPE_EVOLUTION_ROUNDS} rounds"
        )
    if cpe_mode and (args.train_batch_size < 1 or args.validation_size < 1):
        raise ValueError("CPE train batch size and validation size must be positive")

    problems = baseline.load_problems()
    if cpe_mode:
        train_pool, validation_pool = load_cpe_split(args.cpe_split_file)
        requested_problems = [*train_pool, *validation_pool]
    else:
        train_pool, validation_pool = [], []
        requested_problems = list(args.problem_id)
    unknown = [item for item in requested_problems if item not in problems]
    if unknown:
        raise ValueError("Unknown problem ID(s): " + ", ".join(unknown))
    if not cpe_mode and len(args.problem_id) != len(set(args.problem_id)):
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
        if previous_config and previous_config.get("experiment_type") != (
            "substantive_interaction_workflow_evolution"
        ):
            raise ValueError("--exp is not an interaction-workflow experiment")
        has_results = bool(workflow_evolution.read_json(results_path, []))
        if has_results and not previous_config:
            raise ValueError("Resumed experiment has results but no valid config.json")
        saved_cpe = previous_config.get("cpe", {})
        saved_cpe_mode = bool(
            saved_cpe.get("enabled") if isinstance(saved_cpe, dict) else False
        )
        if has_results and saved_cpe_mode != cpe_mode:
            raise ValueError(
                "Cannot resume an experiment with a different CPE mode; start a "
                "new experiment or use the matching entry point."
            )

    interaction.OBJECTIVE_WEIGHTS = dict(previous_config.get("utility_weights", {}))

    fixed_target = experiment / "fixed_interaction_rubric.json"
    configured_fixed_source = Path(
        str(
            previous_config.get("fixed_interaction_rubric_source")
            or previous_config.get("fixed_interaction_rubric")
            or ""
        )
    )
    if compact_experiment_inputs and configured_fixed_source.is_file():
        fixed_rubric_path = configured_fixed_source
    elif not compact_experiment_inputs and fixed_target.is_file():
        fixed_rubric_path = fixed_target
    else:
        fixed_rubric_path = resolve_fixed_rubric_path(args.fixed_rubric)
    fixed_rubric = load_fixed_rubric(fixed_rubric_path)
    if not compact_experiment_inputs:
        workflow_evolution.write_json(fixed_target, fixed_rubric)

    initial_target = experiment / "initial_interaction_workflows.json"
    initial_population = load_seed_population(
        experiment,
        resumed,
        args.initial_workflow,
        persist_legacy_file=not compact_experiment_inputs,
    )
    if cpe_mode and len(initial_population) != CPE_TRAINING_PARENT_COUNT:
        raise ValueError("CPE mode requires exactly two initial workflows")

    cpe_state = None
    if cpe_mode:
        cpe_state = load_or_create_cpe_state(
            experiment,
            train_pool,
            validation_pool,
            args.train_batch_size,
            args.validation_size,
            args.sampling_seed,
            args.selection_epsilon,
        )
        initial_problem_ids = reserve_cpe_initial_train_batch(cpe_state)
        report_problem_ids = list(initial_problem_ids)
    else:
        initial_problem_ids = list(args.problem_id)
        report_problem_ids = list(args.problem_id)

    configured_reports = previous_config.get("baseline_reports", {})
    if not isinstance(configured_reports, dict):
        configured_reports = {}
    baseline_reports = {}
    missing_reports = []
    for problem_id in report_problem_ids:
        configured = Path(str(configured_reports.get(problem_id, "")))
        report_validator = getattr(
            substantive, "baseline_report_matches_problem", None
        )
        configured_matches = configured.is_file() and (
            not callable(report_validator)
            or report_validator(problem_id, configured)
        )
        try:
            source = (
                configured
                if configured_matches
                else substantive.resolve_baseline_report(
                    problem_id, Path(args.baseline_report_root)
                )
            )
        except FileNotFoundError:
            missing_reports.append(problem_id)
            continue
        baseline_reports[problem_id] = str(source.resolve())
    if missing_reports:
        missing_scope = (
            "selected initial validation tasks"
            if cpe_mode
            else "selected workflow-evaluation tasks"
        )
        raise FileNotFoundError(
            f"Missing clean baseline reports for the {missing_scope}: "
            + ", ".join(missing_reports)
            + ". Generate those no-interaction baselines first or pass a complete "
            "--baseline-report-root."
        )

    interaction.VALIDATION_PROBLEMS = tuple(initial_problem_ids)
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
        "fixed_interaction_rubric_source": str(fixed_rubric_path.resolve()),
        "interaction_rubric_in_optimizer_prompt": False,
        "interaction_rubric_in_agent_prompt": False,
        "initial_interaction_workflows": str(initial_target.resolve()),
        "initial_strategy_count": len(initial_population),
        "initial_strategy_rounds_parallel": True,
        "initial_round_problem_concurrency": args.concurrency,
        "initial_strategy_rounds": list(
            range(1, min(len(initial_population), args.max_rounds) + 1)
        ),
        "evolved_rounds_serial": True,
        "standalone_dialogue_operator_evolution": dialogue_operator_evolution,
        "round_dimension_plot": (
            None
            if cpe_mode
            else str(
                (workflows_dir / "round_average_dimension_scores.png").resolve()
            )
        ),
        "execution_time_excel": str(
            (workflows_dir / "round_execution_times.xlsx").resolve()
        ),
        "baseline_report_root": str(Path(args.baseline_report_root).resolve()),
        "baseline_reports": baseline_reports,
        "validation_problems": initial_problem_ids,
        "cpe": {
            "enabled": cpe_mode,
            "algorithm": (
                "two_parent_net_utility_batch_evolution_"
                "full_validation_champion_gate"
            ),
            "split_file": str(Path(args.cpe_split_file).resolve()),
            "train_pool": train_pool if cpe_mode else [],
            "train_batch_size": args.train_batch_size if cpe_mode else None,
            "train_sampling": (
                "independent_batches_with_replacement_across_rounds"
                if cpe_mode
                else None
            ),
            "validation_pool": validation_pool if cpe_mode else [],
            "validation_size": args.validation_size if cpe_mode else None,
            "validation_problems": initial_problem_ids if cpe_mode else [],
            "sampling_seed": cpe_state["sampling_seed"] if cpe_state else None,
            "selection_epsilon": args.selection_epsilon if cpe_mode else None,
            "initial_seed_protocol": (
                "two_initial_workflows_run_on_one_shared_training_batch"
                if cpe_mode
                else None
            ),
            "initial_seed_count": (
                CPE_TRAINING_PARENT_COUNT if cpe_mode else None
            ),
            "initial_seed_split": "train" if cpe_mode else None,
            "training_parent_count": (
                CPE_TRAINING_PARENT_COUNT if cpe_mode else None
            ),
            "training_parent_evaluations_parallel": cpe_mode,
            "training_parent_parallelism": (
                CPE_TRAINING_PARENT_COUNT if cpe_mode else None
            ),
            "per_parent_problem_concurrency": (
                args.concurrency if cpe_mode else None
            ),
            "initial_training_parents": (
                "two_initial_shared_training_batch_workflows"
                if cpe_mode
                else None
            ),
            "training_parent_selection": (
                "top_two_distinct_workflows_on_current_shared_training_batch"
                if cpe_mode
                else None
            ),
            "candidate_enters_population_if_better_than_weakest_parent": False,
            "candidate_requires_beating_all_training_parents": cpe_mode,
            "best_policy_requires_validation_accept": cpe_mode,
            "utility_basis": (
                CPE_UTILITY_BASIS if cpe_mode else None
            ),
            "original_report_role": (
                (
                    "quality_reference_only_no_net_utility"
                    if CPE_UTILITY_BASIS == CPE_UTILITY_BASIS_QUALITY_GAIN
                    else "not_scored_for_utility"
                )
                if cpe_mode
                else None
            ),
            "interaction_cost": (
                {
                    "max_exchanges": DEFAULT_CPE_MAX_EXCHANGES,
                    "total_token_reference": DEFAULT_CPE_TOTAL_TOKEN_REFERENCE,
                    "total_latency_max_seconds": (
                        DEFAULT_CPE_TOTAL_LATENCY_MAX_SECONDS
                    ),
                    "exchange_weight": DEFAULT_CPE_EXCHANGE_COST_WEIGHT,
                    "token_weight": DEFAULT_CPE_TOKEN_COST_WEIGHT,
                    "latency_weight": DEFAULT_CPE_LATENCY_COST_WEIGHT,
                    "penalty_weight_lambda": DEFAULT_CPE_COST_PENALTY_WEIGHT,
                    "token_count_method": (
                        "ceil(CJK + other_non_ASCII + ASCII_characters/4)"
                    ),
                }
                if cpe_mode
                else None
            ),
            "validation_champion_optimizer_fields": (
                ["workflow", "utility"] if cpe_mode else []
            ),
            "training_parent_evidence_includes": (
                [
                    "workflow",
                    "aggregate_net_utility",
                    "public_task_statement",
                    "expert_dialogue",
                    "interaction_report_change_summary",
                    "interaction_cost",
                ]
                if cpe_mode
                else []
            ),
            "training_parent_evidence_withholds": (
                sorted(CPE_WITHHELD_JUDGE_FIELDS) if cpe_mode else []
            ),
            "pareto_champions": False,
        },
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
                "two_current_batch_training_parents_plus_validation_champion_signal"
                if cpe_mode
                else "all_three_initial_workflows_plus_historical_global_best"
            ),
            "fields": (
                [
                    "two_training_parent_workflows",
                    "two_training_parent_net_utilities",
                    "two_training_parent_task_statements",
                    "two_training_parent_expert_dialogues",
                    "two_training_parent_report_change_summaries",
                    "two_training_parent_interaction_costs",
                    "validation_champion_workflow",
                    "validation_champion_net_utility",
                    "training_only_decision_history",
                ]
                if cpe_mode
                else [
                    "workflow",
                    "average_utility",
                    "average_dimension_scores",
                    "parent_roles",
                    "expert_interaction",
                    "interaction_report_change_summary",
                    "judge_groundedness_weakness_summary",
                ]
            ),
            "report_change_summary_max_chars": REPORT_CHANGE_SUMMARY_MAX_CHARS,
            "judge_feedback_dimensions": (
                [] if cpe_mode else list(JUDGE_FEEDBACK_DIMENSIONS)
            ),
            "task_level_judge_outputs_withheld": cpe_mode,
            "parent_archive_scope": (
                "current_two_training_elites"
                if cpe_mode
                else "all_completed_rounds"
            ),
            "all_workflow_nodes_required_as_parent_inputs": not cpe_mode,
            "validation_rollouts_withheld_from_optimizer": cpe_mode,
        },
        "validation_repetitions": args.validation_repetitions,
        "updated_at": now(),
    }
    if dialogue_operator_evolution:
        config["stagnation_operator_evolution"] = {
            "enabled": True,
            "rounds_without_strict_improvement": (
                STAGNATION_ROUNDS_FOR_OPERATOR_EVOLUTION
            ),
            "strict_improvement": True,
            "registry": str(evolved_operator_registry_path(workflows_dir).resolve()),
            "objective": (
                "historical_best_validation_net_utility"
                if cpe_mode
                else "historical_best_round_utility"
            ),
            "similarity_retry_trigger": (
                SIMILARITY_REJECTIONS_FOR_OPERATOR_EVOLUTION
                if cpe_mode
                else None
            ),
        }
    if not compact_experiment_inputs:
        config.update(
            {
                "fixed_interaction_rubric": str(fixed_target.resolve()),
                "initial_interaction_workflow": str(initial_target.resolve()),
            }
        )
    workflow_evolution.write_json(experiment / "config.json", config)
    print(f"Experiment: {experiment}")
    displayed_fixed_rubric = (
        fixed_rubric_path if compact_experiment_inputs else fixed_target
    )
    print(f"Fixed interaction rubric: {displayed_fixed_rubric}")
    print(f"Initial interaction workflows: {initial_target}")
    if cpe_mode:
        print("Training pool: " + ", ".join(train_pool))
        print("Full fixed validation set: " + ", ".join(initial_problem_ids))
    else:
        print("Problems: " + ", ".join(initial_problem_ids))

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
    cpe_original_scores: dict[str, dict[str, Any]] = {}
    if cpe_mode:
        cpe_original_scores = ensure_cpe_original_report_scores(
            experiment, initial_problem_ids, run_args
        )

    collapsed_initial_round = cpe_mode and CPE_COLLAPSE_INITIAL_PARENTS
    if collapsed_initial_round:
        run_cpe_collapsed_initial_parent_evaluations(
            experiment,
            initial_problem_ids,
            initial_population,
            fixed_rubric,
            problems,
            run_args,
            args,
            cpe_state,
            cpe_original_scores,
        )

    # The initial strategies are independent population members. Start all
    # unfinished seed rounds together, then wait for the entire population
    # before allowing any score-dependent evolution.
    seed_count = (
        0
        if collapsed_initial_round
        else min(len(initial_population), args.max_rounds)
    )
    results = normalized_results(results_path)
    pending_seeds = []
    for round_number in range(1, seed_count + 1):
        if completed_round_result(
            results,
            round_number,
            len(initial_problem_ids),
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
        # concurrency. They use one shared initial split and start together
        # before score-dependent evolution.
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
                if cpe_mode:
                    future = executor.submit(
                        execute_cpe_evaluation,
                        experiment,
                        round_number,
                        f"initial_train_parent_{round_number}",
                        "train",
                        initial_problem_ids,
                        workflow,
                        fixed_rubric,
                        problems,
                        seed_args,
                        args.enforce_substantive_interaction_gate,
                        cpe_original_scores,
                    )
                else:
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
                    if cpe_mode:
                        apply_cpe_net_utility(result, cpe_original_scores)
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

    results = normalized_results(results_path)
    if cpe_mode:
        if not collapsed_initial_round:
            for result in results:
                if 1 <= int(result.get("round", 0)) <= seed_count:
                    apply_cpe_net_utility(result, cpe_original_scores)
                    workflow_evolution.write_json(
                        workflows_dir / f"round_{result['round']}" / "result.json",
                        result,
                    )
            workflow_evolution.write_json(results_path, results)
        results = run_cpe_evolved_rounds(
            experiment,
            results_path,
            results,
            initial_population,
            fixed_rubric,
            problems,
            run_args,
            args,
            cpe_state,
            cpe_original_scores,
            dialogue_operator_evolution,
        )
        best_path = workflows_dir / "best_workflow.json"
        print(f"CPE best workflow: {best_path}", flush=True)
        return

    # This also handles a resumed experiment that had already reached a plateau
    # before the operator-evolution rule was introduced.
    results = normalized_results(results_path)
    if dialogue_operator_evolution:
        maybe_evolve_dialogue_operator(results, workflows_dir, args, problems)

    # Every evolved round depends on all earlier scores, so these rounds remain
    # strictly serial even though problems within one round may run concurrently.
    for round_number in range(seed_count + 1, args.max_rounds + 1):
        results = normalized_results(results_path)
        if completed_round_result(
            results,
            round_number,
            len(initial_problem_ids),
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
        if dialogue_operator_evolution:
            maybe_evolve_dialogue_operator(results, workflows_dir, args, problems)

    final_results = normalized_results(results_path)
    incomplete_rounds = [
        round_number
        for round_number in range(1, args.max_rounds + 1)
        if completed_round_result(
            final_results,
            round_number,
            len(initial_problem_ids),
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
