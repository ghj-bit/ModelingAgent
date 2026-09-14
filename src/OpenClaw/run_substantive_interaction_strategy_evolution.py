"""Evolve expert-interaction strategies during end-to-end modeling runs.

Unlike ``run_substantive_interaction_workflow_evolution.py``, this runner does
not inherit or refine a baseline report.  Every candidate strategy is evaluated
by asking OpenClaw to solve each validation problem from a fresh workspace while
following the candidate's interaction actions during the modeling process.

The workflow evolution, parent selection, stagnation-triggered operator
evolution, judging, checkpoints, spreadsheets, and plots use a private copied
core so execution-time adaptations cannot mutate or depend on the refinement
runner's module state.
"""

from __future__ import annotations

import argparse
import atexit
import copy
import hashlib
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    from . import baseline
    from . import run_interaction_rubric_evolution as interaction
    from . import run_substantive_interaction_experiment as substantive
    from . import run_substantive_interaction_strategy_core as workflow
    from . import run_evolution as workflow_evolution
except ImportError:
    import baseline
    import run_interaction_rubric_evolution as interaction
    import run_substantive_interaction_experiment as substantive
    import run_substantive_interaction_strategy_core as workflow
    import run_evolution as workflow_evolution


EXPERIMENT_TYPE = "substantive_interaction_strategy_evolution"
EXPERIMENT_PREFIX = "interaction_strategy_substantive"
ACTIVE_STRATEGY_WORKFLOWS_DIR: Path | None = None
REFERENCE_BASELINE_PROMPT_PATH = (
    REPO_ROOT
    / "openclaw_experiments"
    / "interaction_strategy_clean_baseline_20260912_193324"
    / "workflows"
    / "round_1"
    / "prompt.md"
)

STRATEGY_INTERACTION_OPERATORS = {
    "structure_assumption_discovery": {
        "stage": "after_step_2",
        "purpose": "Resolve the single highest-value structural uncertainty before the formulation is committed.",
        "rule": "After Steps 1 and 2, rank unresolved qualitative structural assumptions by decision impact, evidence gap, and deliverable relevance. Consult on the top assumption through one focal question with at most two tightly coupled subquestions. Ask for a recommendation or challenge, its main failure mode, and its applicability boundary. The agent owns formalization and validation; other issues remain deferred.",
        "output": "One focused qualitative challenge that discriminates among candidate structures, with its main failure mode and applicability boundary.",
    },
    "provisional_model_red_team": {
        "stage": "after_step_5",
        "purpose": "Attack the real-world consequences of technical weaknesses found in a provisional executable model.",
        "rule": "After the agent builds and audits a provisional model, present the real-world implications of the distinct high-risk weaknesses that remain after definite technical errors are repaired. Ask the expert for plausible failure conditions or counterexamples. The expert does not inspect code or calculate; the agent implements and independently validates every justified repair.",
        "output": "Failure conditions tied to independently audited weaknesses in a provisional model.",
    },
    "sensitivity_evidence_calibration": {
        "stage": "during_step_6",
        "purpose": "Ground influential weak parameter groups after preliminary results reveal where conclusions are unstable.",
        "rule": "After sensitivity and identifiability screening, present the influential weakly evidenced parameter groups or empirical claims and their decision roles. The request may cover multiple independent groups. Ask the expert for qualitative real-world boundaries and authoritative evidence types, then require the agent to verify externally, recalibrate jointly, and compare decisions.",
        "output": "Real-world boundaries and evidence directions for sensitivity-critical parameter groups.",
    },
    "implemented_model_interpretation_audit": {
        "stage": "after_step_5",
        "purpose": "Resolve the single highest-risk conflict between an implemented mechanism and the real process it represents.",
        "rule": "After auditing the provisional model and outputs, rank interpretation-dependent conflicts by their effect on the main conclusion and deliverables. Consult on the top conflict through one focal question with at most two tightly coupled subquestions. Ask for the faithful interpretation, its applicability boundary, and the main consequence of retaining the current interpretation. The agent owns repair and validation; other issues remain deferred.",
        "output": "One scoped operational interpretation, its applicability boundary, and the main consequence of choosing incorrectly.",
    },
    "validation_failure_signal_probe": {
        "stage": "during_step_6",
        "purpose": "Use one lightweight diagnostic to challenge the conclusion whose residual validation gap matters most.",
        "rule": "After a minimal preliminary validation, select the one unresolved gap most likely to change the main decision. Ask one concise focal question for an observable failure signal or boundary case and, only if necessary, one tightly coupled subquestion about the evidence needed to observe it. After the reply, use existing model outputs where possible and run at most one bounded analytic check or small scenario comparison. Do not launch broad searches, nested optimization, Monte Carlo, or multi-parameter sweeps solely for this exchange. Revise only the affected claim; defer other gaps.",
        "output": "One decision-relevant failure signal and one bounded validation consequence.",
    },
}

EXECUTION_EXPERT_ROLE_PROMPT = """\
You are an independent human mathematical-modeling expert represented through
an API. You are a non-computational domain and decision adviser, not a
calculator, code reviewer, or model implementer.

Read the complete problem statement appended below before answering. Address
the parent's one focal qualitative uncertainty and up to two tightly coupled
subquestions. If multiple topics appear, answer the one with the greatest effect
on the main conclusion and briefly mark the rest as deferred.

Challenge omissions in mechanisms, stakeholder objectives, failure modes, or
task interpretation when material. Provide one concise recommendation or
challenge, its main reason or failure mode, and an applicability boundary or
caveat. Tag reasons Fact/Judgment/Assumption where applicable. Stay qualitative;
leave calculation, parameter estimation, code, tools, and literature search to
the parent. Keep the complete reply under 180 words.
"""


INITIAL_EXECUTION_STRATEGY_DESCRIPTIONS = (
    {
        "name": "结构与假设发现时序工作流",
        "description": (
            "完成Step 2后调用结构与假设发现算子，再根据专家提供的现实边界完成"
            "Step 3及后续建模。"
        ),
        "operator_id": "structure_assumption_discovery",
        "stage": "after_step_2",
        "entry_action": "complete_through_assumptions",
        "actions": [
            {
                "action_id": "complete_through_assumptions",
                "action_type": "agent_modeling",
                "stage": "through_step_2",
                "rule": "Complete Steps 1 and 2 and record the problem understanding and modeling assumptions.",
            },
            {
                "action_id": "challenge_structure_and_assumptions",
                "action_type": "expert_exchange",
                "stage": "after_step_2",
                "interaction_stage": 2,
                "operator_id": "structure_assumption_discovery",
                "rule": "Select the highest-priority unresolved structural assumption and apply the referenced operator.",
            },
            {
                "action_id": "model_from_challenged_assumptions",
                "action_type": "agent_modeling",
                "stage": "steps_3_to_7",
                "rule": "Incorporate relevant advice into the model, validate affected results, and complete Steps 3 through 7.",
            },
        ],
        "stop_condition": "Stop after completing the model and validating the consultation's downstream effects.",
    },
    {
        "name": "实现模型解释一致性时序工作流",
        "description": (
            "完成可执行模型后调用实现模型解释一致性算子，消解现实解释、公式、结果和"
            "报告之间的冲突。"
        ),
        "operator_id": "implemented_model_interpretation_audit",
        "stage": "after_step_5",
        "entry_action": "build_and_audit_provisional_model",
        "actions": [
            {
                "action_id": "build_and_audit_provisional_model",
                "action_type": "agent_modeling",
                "stage": "through_step_5",
                "rule": "Complete Steps 1 through 5 and audit the provisional model and outputs for high-risk inconsistencies.",
            },
            {
                "action_id": "resolve_implemented_interpretations",
                "action_type": "expert_exchange",
                "stage": "after_step_5",
                "interaction_stage": 5,
                "operator_id": "implemented_model_interpretation_audit",
                "rule": "Select the highest-priority interpretation-dependent inconsistency and apply the referenced operator.",
            },
            {
                "action_id": "repair_and_regression_test",
                "action_type": "agent_validation",
                "stage": "steps_5_to_7",
                "rule": "Apply relevant advice, regenerate dependent outputs, run the existing regression checks, and complete Steps 6 and 7.",
            },
        ],
        "stop_condition": "Stop after testing the focal conflict and reconciling its dependent outputs.",
    },
    {
        "name": "验证失败信号证伪时序工作流",
        "description": (
            "初步验证后调用验证失败信号算子，针对残留差异、边界情景和外部比较目标"
            "执行独立证伪。"
        ),
        "operator_id": "validation_failure_signal_probe",
        "stage": "during_step_6",
        "entry_action": "screen_sensitive_weak_inputs",
        "actions": [
            {
                "action_id": "screen_sensitive_weak_inputs",
                "action_type": "agent_validation",
                "stage": "through_step_6",
                "rule": "Complete Steps 1 through 5 and use existing outputs plus one lightweight preliminary check to identify the single residual gap most likely to change the main decision.",
            },
            {
                "action_id": "elicit_validation_failure_signals",
                "action_type": "expert_exchange",
                "stage": "during_step_6",
                "interaction_stage": 6,
                "operator_id": "validation_failure_signal_probe",
                "rule": "Select the highest-priority residual validation gap and apply the referenced operator.",
            },
            {
                "action_id": "verify_recalibrate_and_finish",
                "action_type": "agent_validation",
                "stage": "finish_steps_6_and_7",
                "rule": "Test the focal signal with at most one bounded analytic check or small scenario comparison, revise only the affected claim, and complete Steps 6 and 7 without interaction-driven broad search, nested optimization, Monte Carlo, or multi-parameter sweeps.",
            },
        ],
        "stop_condition": "Stop after one bounded test of the focal gap and one localized claim revision.",
    },
)


def _initial_strategy_record(definition: dict[str, str]) -> dict[str, Any]:
    """Create one self-contained temporal operator-orchestration seed."""
    description = definition["description"]
    strategy = {
        "name": definition["name"],
        "purpose": description,
        "entry_action": definition["entry_action"],
        "actions": copy.deepcopy(definition["actions"]),
        "max_exchanges": 1,
        "stop_condition": definition["stop_condition"],
        "seed_operator": definition["operator_id"],
    }
    workflow.validate_workflow_operator_bindings(
        strategy, STRATEGY_INTERACTION_OPERATORS, require=True
    )
    return strategy


def initial_execution_strategy_population() -> list[dict[str, Any]]:
    """Return three stage-distinct temporal operator-orchestration seeds."""
    strategies = [
        _initial_strategy_record(definition)
        for definition in INITIAL_EXECUTION_STRATEGY_DESCRIPTIONS
    ]
    for strategy in strategies:
        strategy["evolution_operator"] = "initial_strategy"
        workflow.validate_workflow(strategy)
        strategy["workflow_id"] = workflow.workflow_id(strategy)
    return strategies


def load_execution_seed_population(
    experiment: Path, resumed: bool, source: str | None
) -> list[dict[str, Any]]:
    """Load fresh-modeling strategies without consulting refinement defaults."""
    target = experiment / "initial_interaction_strategies.json"
    compatibility_target = experiment / "initial_interaction_workflows.json"
    if target.is_file():
        population = workflow_evolution.read_json(target, [])
    elif resumed and compatibility_target.is_file():
        population = workflow_evolution.read_json(compatibility_target, [])
    elif source:
        value = workflow_evolution.read_json(Path(source).resolve(), {})
        population = value if isinstance(value, list) else [value]
    elif resumed:
        raise ValueError(
            "Resumed experiment has no saved initial strategy; supply --initial-strategy"
        )
    else:
        population = initial_execution_strategy_population()
    if not isinstance(population, list) or not population:
        raise ValueError("Initial interaction strategies must be a non-empty list")
    population = [workflow.without_removed_workflow_fields(item) for item in population]
    for strategy in population:
        workflow.validate_workflow(strategy)
        strategy["workflow_id"] = workflow.workflow_id(strategy)
    if len({item["workflow_id"] for item in population}) != len(population):
        raise ValueError("Initial interaction strategies must have distinct behavior")
    workflow_evolution.write_json(target, population)
    workflow_evolution.write_json(compatibility_target, population)
    return population

# Capture the original from-scratch preparation function before runtime hooks
# are installed. Importing the private strategy core does not execute its main.
PREPARE_FRESH_PROBLEM = interaction.prepare_validation_problem


def now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def reference_baseline_prompt_template() -> str:
    """Read the designated clean baseline prompt verbatim."""
    prompt = REFERENCE_BASELINE_PROMPT_PATH.read_text(encoding="utf-8")
    return prompt
def render_strategy_with_operators(strategy: dict[str, Any]) -> str:
    """Render temporal actions and resolve their operator references for the Agent."""
    operators = workflow.available_dialogue_operators(ACTIVE_STRATEGY_WORKFLOWS_DIR)
    lines = [f"Maximum expert exchanges: {strategy.get('max_exchanges')}"]
    exchange_count = 0
    for index, action in enumerate(strategy.get("actions", []), 1):
        action_type = str(action.get("action_type", "")).strip()
        stage = str(action.get("stage", "")).strip()
        rule = str(action.get("rule", "")).strip()
        lines.append(f"{index}. [{stage}] {action_type}: {rule}")
        if action_type != "expert_exchange":
            continue
        exchange_count += 1
        operator_id = str(action.get("operator_id", "")).strip()
        operator = operators.get(operator_id)
        if operator is None:
            raise ValueError(f"Unknown dialogue operator in strategy: {operator_id!r}")
        lines.extend(
            [
                f"   Dialogue operator: `{operator_id}`",
                f"   Operator rule: {operator['rule']}",
                f"   Expected expert contribution: {operator['output']}",
            ]
        )
    if exchange_count < 1:
        raise ValueError("Strategy contains no expert exchange")
    lines.append(f"Stop condition: {strategy.get('stop_condition')}")
    return "\n".join(lines)


def build_end_to_end_prompt(strategy: dict[str, Any]) -> str:
    """Add the interaction strategy and required intermediate-file contract."""
    baseline_prompt = reference_baseline_prompt_template()
    workflow_marker = "## Required Workflow\n"
    report_marker = "## Final Report Contract\n"
    if baseline_prompt.count(workflow_marker) != 1:
        raise RuntimeError(
            "Baseline prompt template must contain exactly one Required Workflow section"
        )
    if baseline_prompt.count(report_marker) != 1:
        raise RuntimeError(
            "Baseline prompt template must contain exactly one Final Report Contract section"
        )
    strategy_text = render_strategy_with_operators(strategy)

    interaction_section = f"""## Expert Interaction Strategy

{strategy_text}

At the strategy's expert-exchange point, write only the question body to
`{{{{OPERATOR_FEEDBACK_DIR}}}}/expert_question_N.md` (N starts at 1) and run
once in the foreground:

   `python "{{{{OUTPUT_DIR}}}}/code/wait_for_expert_reply.py" --request "{{{{OPERATOR_FEEDBACK_DIR}}}}/expert_request_N.json" --reply "{{{{OPERATOR_FEEDBACK_DIR}}}}/expert_reply_N.json" --timeout {substantive.EXPERT_REQUEST_TIMEOUT:.0f}`

Read the reply before continuing; do not edit the controller-created JSON or
poll manually. Apply every exchange at its specified stage and use accepted
advice downstream. For exchange N, each applicable `[through_step_K]` strategy
action identifies the Step K process report to revise: rename its current version
to `<stem>.pre_interaction_N.md`, then write the revision at its required path.
Repeat for every marked step and exchange, preserve all backups, and use the
required paths as the latest versions in step 7. Briefly record the question,
use of the reply, and affected artifact paths in
`{{{{RESULTS_DIR}}}}/interaction_evidence.md`.
"""
    intermediate_section = """## Workflow Summary Contract

Execute the first six Required Workflow steps in order. At the end of each
step, write one concise UTF-8 Markdown process report containing that step's
decisions, evidence, outputs, unresolved limitations, and downstream handoff:

1. `{{RESULTS_DIR}}/step_01_problem_understanding.md`
2. `{{RESULTS_DIR}}/step_02_modeling_assumptions.md`
3. `{{RESULTS_DIR}}/step_03_model_construction.md`
4. `{{DATA_DIR}}/external_data.md`
5. `{{RESULTS_DIR}}/step_05_implementation.md`
6. `{{RESULTS_DIR}}/step_06_validation_analysis.md`

Before starting a later step, read the preceding process reports and the
supporting artifacts they identify. Supporting data, code, and numerical result
files may be created when required, but do not create generic `step_NN.json`
receipts or extra per-step bookkeeping files. Begin step 7 and produce the final
report only after all six process reports are complete. In step 7, assemble the
final report from those six process reports.
"""
    prompt = baseline_prompt.replace(
        workflow_marker, interaction_section + "\n" + workflow_marker, 1
    )
    prompt = prompt.replace(
        report_marker, intermediate_section + "\n" + report_marker, 1
    )
    prompt = prompt.replace(
        "Use equations, tables, numerical results, and citations where they "
        "materially support the solution.\n\n",
        "Use equations, tables, numerical results, and citations where they "
        "materially support the solution.\n\n"
        "对每个关键计算方法，报告必须自包含地说明输入、模型或目标、核心算法步骤、关键设置、停止条件及验证方法，不得将关键解释仅放在代码或中间文件中。\n\n"
        "生成最终报告时，必须整合各阶段中间报告。整合前须统一各阶段的公式、单位、参数含义、数值和结论；发现冲突时必须消解并说明取舍。最终报告须自包含地列出所有影响模型或结论的假设，并分别说明具体依据和影响；不得只引用中间文件，也不得用 `standard`、`expert` 等标签代替论证。 Do not expose private chain-of-thought. Present only the final reasoning, evidence, methods, and conclusions needed to evaluate the work.\n\n",
        1,
    )
    submission_marker = (
        "Only `{{FINAL_REPORT}}` will be submitted to ModelingBench Judge."
    )
    return prompt.replace(
        submission_marker,
        submission_marker
        + " Intermediate files and your conversational reply will not be scored.",
        1,
    )


def optimizer_parent_artifacts(run_dir: Path) -> list[dict[str, Any]]:
    """Expose dialogue plus its concise downstream-effect trace."""
    return [
        artifact
        for artifact in substantive.parent_artifacts(run_dir)
        if artifact.get("artifact_type")
        in {"expert_interaction", "interaction_evidence"}
    ]


def _compact_judge_judgement(judgement: dict[str, Any]) -> dict[str, Any]:
    """Keep actionable, below-full-score feedback for LLM summarization."""
    compact: dict[str, Any] = {}
    scores = judgement.get("scores")
    explanations = judgement.get("explanation")
    if isinstance(scores, dict):
        compact["criteria"] = {
            name: {
                "score": score,
                "feedback": explanations.get(name, "")
                if isinstance(explanations, dict)
                else "",
            }
            for name, score in scores.items()
            if isinstance(score, (int, float)) and float(score) < 1.0
        }

    role_feedback = []
    for result in judgement.get("role_based_results", []):
        if not isinstance(result, dict):
            continue
        role = result.get("role", {})
        item: dict[str, Any] = {
            "role": role.get("name", "") if isinstance(role, dict) else "",
            "overall_feedback": result.get("overall_feedback", ""),
        }
        weak_criteria = {}
        for name, value in result.items():
            if not isinstance(value, dict):
                continue
            score = value.get("score")
            if isinstance(score, (int, float)) and float(score) < 1.0:
                weak_criteria[name] = {
                    "score": score,
                    "feedback": value.get("explanation", ""),
                }
        if weak_criteria:
            item["criteria"] = weak_criteria
        if item["overall_feedback"] or weak_criteria:
            role_feedback.append(item)
    if role_feedback:
        compact["role_feedback"] = role_feedback
    return compact


def _nonperfect_judge_feedback(run: dict[str, Any]) -> dict[str, Any]:
    """Load raw judge feedback only for aggregate dimensions below 1.0."""
    dimension_scores = run.get("dimension_scores", {})
    target_dimensions = {
        dimension: float(score)
        for dimension, score in dimension_scores.items()
        if isinstance(score, (int, float)) and float(score) < 1.0
    }
    if not target_dimensions:
        return {}

    feedback: dict[str, Any] = {
        dimension: {"score": score, "judgements": []}
        for dimension, score in target_dimensions.items()
    }
    repetitions = run.get("repetitions") or [run]
    for repetition in repetitions:
        if not isinstance(repetition, dict):
            continue
        repetition_scores = repetition.get("dimension_scores", {})
        judge_path = repetition.get("judge_result")
        if not judge_path:
            continue
        judge = workflow_evolution.read_json(Path(judge_path), {})
        judgements = judge.get("judgements", {})
        for dimension in target_dimensions:
            repetition_score = repetition_scores.get(dimension)
            if isinstance(repetition_score, (int, float)) and float(repetition_score) >= 1.0:
                continue
            judgement = judgements.get(dimension)
            if not isinstance(judgement, dict):
                continue
            compact = _compact_judge_judgement(judgement)
            if compact:
                feedback[dimension]["judgements"].append(compact)
    return {
        dimension: value
        for dimension, value in feedback.items()
        if value["judgements"]
    }


def summarize_nonperfect_judge_feedback(
    run: dict[str, Any], round_dir: Path, args
) -> dict[str, Any]:
    """Use Flash to extract weaknesses one non-perfect dimension at a time."""
    raw_feedback = _nonperfect_judge_feedback(run)
    if not raw_feedback:
        return {}
    summary_dir = round_dir / "judge_feedback_summaries"
    summary_dir.mkdir(parents=True, exist_ok=True)
    extracted = {}
    for dimension, feedback in raw_feedback.items():
        payload = json.dumps(
            {"dimension": dimension, **feedback},
            ensure_ascii=False,
            sort_keys=True,
        )
        cache_key = hashlib.sha256(
            (
                "judge-dimension-weaknesses-v2\0"
                + args.judge_feedback_model
                + "\0"
                + payload
            ).encode("utf-8")
        ).hexdigest()
        cache_path = summary_dir / f"{cache_key}.json"
        cached = workflow_evolution.read_json(cache_path, {})
        weakness = cached.get("weaknesses")
        if not isinstance(weakness, str) or not weakness.strip():
            messages = [
                {
                    "role": "system",
                    "content": (
                        "你是评审不足抽取器。输入只含一个未满分维度。只抽取明确不足、"
                        "矛盾、错误、缺失交付物或验证缺口及具体修正方向；不要写优点或总评，"
                        "不要增加其他维度。限180个中文字符。仅返回JSON："
                        "{\"weaknesses\":\"不足抽取\"}。"
                    ),
                },
                {"role": "user", "content": payload},
            ]
            weakness = None
            for attempt in range(1, 4):
                workflow_evolution.write_json(
                    summary_dir / f"{cache_key}_prompt_{attempt}.json", messages
                )
                response = interaction.local.optimizer_response(
                    {
                        "model": args.judge_feedback_model,
                        "messages": messages,
                        "temperature": 0.1,
                        "max_tokens": 600,
                        "response_format": {"type": "json_object"},
                    },
                    args,
                )
                workflow_evolution.write_json(
                    summary_dir / f"{cache_key}_response_{attempt}.json", response
                )
                value = response.get("weaknesses") if isinstance(response, dict) else None
                if isinstance(value, str) and value.strip():
                    weakness = value.strip()
                    break
                if isinstance(value, dict):
                    direct = value.get(dimension)
                    if isinstance(direct, str) and direct.strip():
                        weakness = direct.strip()
                        break
                messages.extend(
                    [
                        {
                            "role": "assistant",
                            "content": json.dumps(response, ensure_ascii=False),
                        },
                        {
                            "role": "user",
                            "content": "weaknesses必须是一个非空字符串，请修正格式。",
                        },
                    ]
                )
            if weakness is None:
                raise RuntimeError(
                    f"Judge-feedback weakness extraction failed for {dimension}"
                )
            workflow_evolution.write_json(
                cache_path,
                {
                    "dimension": dimension,
                    "model": args.judge_feedback_model,
                    "weaknesses": weakness,
                },
            )
        extracted[dimension] = {
            "score": feedback["score"],
            "weaknesses": weakness.strip(),
        }
    return extracted


def optimizer_evidence(
    selected_nodes: list[dict], problems: dict, round_dir: Path, args
) -> list[dict[str, Any]]:
    """Build parent evidence and extract judge weaknesses concurrently by run."""
    problem_context = {
        item["problem_id"]: item
        for item in interaction.optimizer_problem_context(problems)
    }
    evidence = []
    summary_jobs: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for rank, node in enumerate(selected_nodes, 1):
        validation_runs = []
        for run in node.get("problem_results", []):
            run_evidence = {
                **problem_context[run["problem_id"]],
                "artifacts": optimizer_parent_artifacts(Path(run["run_dir"])),
            }
            summary_jobs.append((run, run_evidence))
            validation_runs.append(run_evidence)
        evidence.append(
            {
                "rank": rank,
                "round": node["round"],
                "utility": node["utility"],
                "workflow": workflow.optimizer_workflow(node["workflow"]),
                "validation_runs": validation_runs,
            }
        )
    if summary_jobs:
        worker_count = min(args.judge_feedback_concurrency, len(summary_jobs))
        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            futures = {
                executor.submit(
                    summarize_nonperfect_judge_feedback,
                    run,
                    round_dir,
                    args,
                ): run_evidence
                for run, run_evidence in summary_jobs
            }
            for future in as_completed(futures):
                judge_summary = future.result()
                if judge_summary:
                    futures[future]["judge_dimension_weaknesses"] = judge_summary
    return evidence


def build_strategy_evolution_prompt(
    primary: dict,
    secondary: dict | None,
    evidence: list[dict[str, Any]],
    operator: str,
    dialogue_operators: dict[str, dict] | None = None,
) -> str:
    """Build the optimizer prompt for end-to-end interaction strategies."""
    dialogue_operators = dialogue_operators or workflow.available_dialogue_operators()
    primary_workflow = primary["workflow"]
    secondary_workflow = secondary["workflow"] if secondary else None
    primary_input = (
        primary_workflow.get("plain_language_description")
        or workflow.optimizer_workflow(primary_workflow)
    )
    secondary_input = (
        secondary_workflow.get("plain_language_description")
        if secondary_workflow
        else None
    ) or (
        workflow.optimizer_workflow(secondary_workflow)
        if secondary_workflow
        else None
    )
    return f"""Evolve one executable multi-turn human-expert interaction
strategy for end-to-end mathematical-modeling work. You, the optimizer, must
choose whether this proposal uses workflow mutation or workflow crossover plus
mutation; the Python controller does not choose for you.

The strategy controls when consultation occurs during modeling, what distinct
qualitative information each exchange requests, how later exchanges depend on
earlier replies, what the modeling agent does between exchanges, and when the
dialogue stops. It may use one to three expert exchanges. The modeling agent
retains all calculation, implementation, external-data validation, simulation,
and report-writing responsibility.

Evolution direction is unrestricted. Make a behaviorally testable change to at
least one action, trigger, condition, follow-up policy, integration action, stop
condition, or exchange budget. Changes only to names, rationales, action IDs, or
stylistic wording are not novel. If you choose workflow_mutation, mutate the
primary directly and use the secondary only as comparative evidence. If you
choose workflow_crossover_mutation, combine useful nonredundant mechanisms from
both supplied parents and introduce a real behavioral mutation. Crossover is
invalid when no secondary parent is supplied.

Optimize mean final-report score across the validation tasks while avoiding
redundant exchanges. Every later exchange must build on earlier dialogue and
have a distinct decision-relevant purpose. Keep the strategy general and do not
copy task-specific facts, parameters, methods, or conclusions.

Evolution-operator selection mode: {operator}

Available dialogue operators (information functions, not mandatory steps):
{json.dumps(dialogue_operators, ensure_ascii=False, indent=2)}

Structure-assumption discovery challenges candidate formulations before
commitment; provisional-model red teaming attacks the real-world consequences
of audited technical weaknesses; sensitivity-evidence calibration grounds weak
parameter groups after preliminary results exist. Treat these as equally
available functions. Compose, reorder, replace, or condition registered
operators when justified. Do not invent an operator in this workflow proposal;
new operators are evolved by a separate optimizer prompt and then registered.
Do not force every operator into every strategy.

Primary parent strategy:
{primary_input if isinstance(primary_input, str) else json.dumps(primary_input, ensure_ascii=False, indent=2)}

Secondary parent strategy:
{secondary_input if isinstance(secondary_input, str) else json.dumps(secondary_input, ensure_ascii=False, indent=2)}

Prior validation evidence:
{json.dumps(evidence, ensure_ascii=False, indent=2)}

The evidence contains the actual expert dialogue and its concise downstream-
effect trace. The separate `judge_dimension_weaknesses` field is produced by an
external LLM that reads only Judger dimensions below 1.0 and extracts only their
shortcomings. A dimension omitted from that field was perfect or had no usable
feedback and must not be reintroduced. Use recurring weaknesses to target
strategy changes without copying problem-specific fixes. Infer changes
only from the supplied parent behavior, utility, task context, dialogue, trace,
and summarized judge feedback. Do not ask for a consultation-
process section in the final report; only substantive modeling consequences
belong there.

Return only one JSON object with evolution_operator, name, purpose,
entry_action, actions, max_exchanges, stop_condition, changed_components,
mutation_rationale, and crossover_rationale. evolution_operator must be exactly
workflow_mutation or workflow_crossover_mutation. Use two to eight actions in
execution order. Every action contains action_id, action_type, stage, and rule.
Every expert_exchange action must additionally contain operator_id referencing
the supplied catalog and numeric interaction_stage matching its Required
Workflow step. Its stage must exactly equal the registered operator stage.
Before each exchange at step N, include an applicable action staged
through_step_N; that marker selects the Step N process report for versioning.
Encode conditional follow-up and early stopping in the relevant rule and
stop_condition. At least one action must have action_type expert_exchange.
"""


def build_strategy_operator_prompt(
    existing: dict[str, dict],
    parents: list[dict],
    evidence: list[dict[str, Any]],
) -> str:
    """Adapt the separate operator prompt to fresh modeling execution."""
    prompt = workflow.ORIGINAL_BUILD_OPERATOR_EVOLUTION_PROMPT(
        existing, parents, evidence
    )
    prompt = prompt.replace(
        "for mathematical-\nmodeling report refinement",
        "for end-to-end mathematical-\nmodeling work",
        1,
    )
    return prompt.replace(
        "Create a genuinely different information function",
        "The judge_dimension_weaknesses field is extracted by an external LLM "
        "from Judger dimensions below 1.0 and contains shortcomings only; omitted "
        "dimensions must not be reintroduced. Use recurring weaknesses when they "
        "identify an interaction-addressable gap.\n\n"
        "Create a genuinely different information function",
        1,
    )


def prepare_strategy_validation_problem(
    problem_id: str,
    problem: dict,
    prompt_path: Path,
    round_number: int,
    repetition: int,
    experiment: Path,
    args,
) -> dict:
    """Prepare a fresh workspace and attach the active strategy metadata."""
    prepared = PREPARE_FRESH_PROBLEM(
        problem_id,
        problem,
        prompt_path,
        round_number,
        repetition,
        experiment,
        args,
    )
    strategy = workflow.ACTIVE_WORKFLOWS.get(round_number)
    if strategy is None:
        raise RuntimeError(f"No active interaction strategy for round {round_number}")
    run_dir = Path(prepared["run_dir"])
    metadata_path = run_dir / "meta" / "run.json"
    metadata = workflow_evolution.read_json(metadata_path, {})
    metadata.update(
        {
            "execution_mode": "end_to_end_expert_guided_modeling",
            "initial_draft_used": False,
            "interaction_strategy_id": strategy["workflow_id"],
            "interaction_strategy": strategy,
        }
    )
    workflow_evolution.write_json(metadata_path, metadata)
    workflow_evolution.write_json(run_dir / "strategy.json", strategy)
    # Keep workflow.json as a compatibility artifact for receipt generation and
    # existing analysis/export utilities.
    workflow_evolution.write_json(run_dir / "workflow.json", strategy)
    return prepared


def run_end_to_end_modeling_phase(
    prepared: dict,
    session_id: str,
    message_file: Path,
    args,
    completion_artifact: Path | None,
) -> None:
    """Run one OpenClaw session without baseline-refinement post-processing."""
    run_dir = Path(prepared["run_dir"])
    meta_dir = run_dir / "meta"
    meta_dir.mkdir(parents=True, exist_ok=True)
    transport_log = meta_dir / "transport.log"
    solve_log = meta_dir / "solve.log"
    metadata_path = meta_dir / "run.json"
    metadata = workflow_evolution.read_json(metadata_path, {})
    metadata.update(
        {
            "session_id": session_id,
            "session_transcript": str(
                substantive.openclaw_session_file(prepared["agent_id"], session_id)
            ),
            "solve_log": str(solve_log),
            "transport_log": str(transport_log),
        }
    )
    workflow_evolution.write_json(metadata_path, metadata)
    try:
        baseline.stream_command(
            [
                prepared["openclaw"],
                "agent",
                "--local",
                "--agent",
                prepared["agent_id"],
                "--session-id",
                session_id,
                "--message-file",
                str(message_file),
                "--thinking",
                args.thinking,
                "--timeout",
                str(args.timeout),
            ],
            run_dir,
            transport_log,
            completion_artifact=completion_artifact,
        )
    finally:
        substantive.render_openclaw_session_log(
            prepared["agent_id"], session_id, message_file, solve_log
        )


def execute_strategy_round(*args, **kwargs) -> tuple[dict, list[dict]]:
    """Run through the compatibility layer and expose strategy aliases."""
    result, failures = workflow.execute_workflow_round(*args, **kwargs)
    result["strategy_id"] = result["workflow_id"]
    result["strategy"] = result["workflow"]
    return result, failures


def experiment_path(value: str | None) -> tuple[Path, bool]:
    if value:
        path = Path(value).resolve()
        return path, path.is_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return (
        REPO_ROOT / "openclaw_experiments" / f"{EXPERIMENT_PREFIX}_{timestamp}",
        False,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Evolve multi-turn expert-interaction strategies during fresh, "
            "end-to-end mathematical-modeling runs."
        )
    )
    parser.add_argument("--max-rounds", type=int, default=10)
    parser.add_argument(
        "--problem-id", nargs="+", default=list(substantive.DEFAULT_PROBLEMS)
    )
    parser.add_argument("--exp")
    parser.add_argument("--fixed-rubric", default=str(workflow.DEFAULT_FIXED_RUBRIC_PATH))
    parser.add_argument(
        "--interaction-strategy",
        "--initial-strategy",
        "--initial-workflow",
        dest="initial_workflow",
        default=None,
        help=(
            "Optional single strategy JSON or strategy population JSON; "
            "default: three stage-distinct operator-orchestration seeds."
        ),
    )
    parser.add_argument("--model", default="deepseek/deepseek-v4-flash")
    parser.add_argument("--opt-model", default="deepseek-v4-pro")
    parser.add_argument("--judge-feedback-model", default="deepseek-v4-flash")
    parser.add_argument("--judge-feedback-concurrency", type=int, default=6)
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
        "--parent-similarity-threshold",
        type=float,
        default=workflow.DEFAULT_PARENT_SIMILARITY_THRESHOLD,
    )
    parser.add_argument(
        "--candidate-similarity-threshold",
        type=float,
        default=workflow.DEFAULT_CANDIDATE_SIMILARITY_THRESHOLD,
    )
    return parser.parse_args()


def runtime_args(args: argparse.Namespace) -> SimpleNamespace:
    """Build the shared evaluator namespace without baseline report inputs."""
    return SimpleNamespace(
        model=args.model,
        openclaw_command=args.openclaw_command,
        expert_model=args.expert_model,
        expert_api_key=args.expert_api_key,
        expert_base_url=args.expert_base_url,
        expert_timeout=args.expert_timeout,
        expert_request_timeout=args.expert_request_timeout,
        expert_attempts=args.expert_attempts,
        opt_model=args.opt_model,
        opt_api_key=args.opt_api_key,
        opt_base_url=args.opt_base_url,
        optimizer_retries=args.optimizer_retries,
        thinking=args.thinking,
        timeout=args.timeout,
        concurrency=args.concurrency,
        judge_repeats=args.judge_repeats,
        judge_concurrency=args.judge_concurrency,
        validation_repetitions=args.validation_repetitions,
        validation_attempts=args.validation_attempts,
        retry_concurrency=args.retry_concurrency,
        validation_retry_delay=args.validation_retry_delay,
        skip_interaction_receipt_validation=True,
    )


def validate_args(args: argparse.Namespace) -> None:
    numeric = (
        args.max_rounds,
        args.optimizer_retries,
        args.concurrency,
        args.judge_repeats,
        args.judge_concurrency,
        args.validation_repetitions,
        args.validation_attempts,
        args.retry_concurrency,
        args.expert_attempts,
        args.judge_feedback_concurrency,
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
    for name, threshold in (
        ("parent", args.parent_similarity_threshold),
        ("candidate", args.candidate_similarity_threshold),
    ):
        if not 0.0 < threshold <= 1.0:
            raise ValueError(f"{name} similarity threshold must be in (0, 1]")


def install_runtime_hooks() -> None:
    """Route the private strategy core to end-to-end behavior for this process."""
    workflow.INTERACTION_OPERATORS = copy.deepcopy(
        STRATEGY_INTERACTION_OPERATORS
    )
    workflow.build_workflow_refinement_prompt = build_end_to_end_prompt
    workflow.optimizer_parent_artifacts = optimizer_parent_artifacts
    workflow.optimizer_evidence = optimizer_evidence
    workflow.build_workflow_evolution_prompt = build_strategy_evolution_prompt
    if not hasattr(workflow, "ORIGINAL_BUILD_OPERATOR_EVOLUTION_PROMPT"):
        workflow.ORIGINAL_BUILD_OPERATOR_EVOLUTION_PROMPT = (
            workflow.build_operator_evolution_prompt
        )
    workflow.build_operator_evolution_prompt = build_strategy_operator_prompt
    interaction.finalize_interaction_receipt = workflow.finalize_workflow_receipt
    interaction.run_local_modeling_phase = run_end_to_end_modeling_phase
    interaction.prepare_validation_problem = prepare_strategy_validation_problem
    interaction.serve_expert_requests = substantive.serve_substantive_expert_requests
    baseline.HUMAN_MODELING_EXPERT_ROLE_PROMPT = EXECUTION_EXPERT_ROLE_PROMPT
    baseline.create_operator_role_prompts = substantive.create_substantive_operator_role_prompt


def main() -> None:
    global ACTIVE_STRATEGY_WORKFLOWS_DIR
    args = parse_args()
    validate_args(args)

    problems = baseline.load_problems()
    unknown = [item for item in args.problem_id if item not in problems]
    if unknown:
        raise ValueError("Unknown problem ID(s): " + ", ".join(unknown))
    if len(args.problem_id) != len(set(args.problem_id)):
        raise ValueError("problem IDs must be unique")

    experiment, resumed = experiment_path(args.exp)
    workflows_dir = experiment / "workflows"
    ACTIVE_STRATEGY_WORKFLOWS_DIR = workflows_dir
    results_path = workflows_dir / "results.json"
    if not resumed:
        workflows_dir.mkdir(parents=True, exist_ok=False)
        workflow_evolution.write_json(results_path, [])
    else:
        previous_config = workflow_evolution.read_json(experiment / "config.json", {})
        if previous_config.get("experiment_type") != EXPERIMENT_TYPE:
            raise ValueError("--exp is not an end-to-end interaction-strategy experiment")

    fixed_target = experiment / "interaction_transport_rubric.json"
    if fixed_target.is_file():
        fixed_rubric_path = fixed_target
    else:
        fixed_rubric_path = workflow.resolve_fixed_rubric_path(args.fixed_rubric)
    fixed_rubric = workflow.load_fixed_rubric(fixed_rubric_path)
    workflow_evolution.write_json(fixed_target, fixed_rubric)

    initial_population = load_execution_seed_population(
        experiment, resumed, args.initial_workflow
    )
    initial_target = experiment / "initial_interaction_strategies.json"

    interaction.VALIDATION_PROBLEMS = tuple(args.problem_id)
    interaction.INITIAL_RUBRIC = fixed_rubric
    install_runtime_hooks()

    config = {
        "experiment_type": EXPERIMENT_TYPE,
        "evolution_subject": "interaction_strategy",
        "strategy_evolution": True,
        "rubric_evolution": False,
        "max_rounds": args.max_rounds,
        "execution_mode": "end_to_end_expert_guided_modeling",
        "initial_draft_used": False,
        "baseline_report_root": None,
        "baseline_reports": {},
        "interaction_rubric_in_optimizer_prompt": False,
        "interaction_rubric_in_agent_prompt": False,
        "transport_rubric": str(fixed_target.resolve()),
        "initial_interaction_strategies": str(initial_target.resolve()),
        "optimizer_artifacts": ["expert_interaction", "interaction_evidence"],
        "initial_strategy_count": len(initial_population),
        "initial_strategy_rounds_parallel": len(initial_population) > 1,
        "initial_round_problem_concurrency": args.concurrency,
        "initial_strategy_rounds": list(
            range(1, min(len(initial_population), args.max_rounds) + 1)
        ),
        "evolved_rounds_serial": True,
        "stagnation_operator_evolution": {
            "enabled": True,
            "counting_starts_at_round": workflow.FIRST_STAGNATION_COUNTED_ROUND,
            "rounds_without_meaningful_improvement": (
                workflow.STAGNATION_ROUNDS_FOR_OPERATOR_EVOLUTION
            ),
            "minimum_utility_improvement": workflow.MIN_UTILITY_IMPROVEMENT,
            "operators_per_event": workflow.OPERATORS_PER_STAGNATION_EVENT,
            "registry": str(
                workflow.evolved_operator_registry_path(workflows_dir).resolve()
            ),
        },
        "round_dimension_plot": str(
            (workflows_dir / "round_average_dimension_scores.png").resolve()
        ),
        "execution_time_excel": str(
            (workflows_dir / "round_execution_times.xlsx").resolve()
        ),
        "validation_problems": args.problem_id,
        "model": args.model,
        "opt_model": args.opt_model,
        "expert_model": args.expert_model,
        "parent_similarity_threshold": args.parent_similarity_threshold,
        "candidate_similarity_threshold": args.candidate_similarity_threshold,
        "judge_repeats": args.judge_repeats,
        "judge_feedback_model": args.judge_feedback_model,
        "judge_feedback_concurrency": args.judge_feedback_concurrency,
        "validation_repetitions": args.validation_repetitions,
        "updated_at": now(),
    }
    workflow_evolution.write_json(experiment / "config.json", config)
    print(f"Experiment: {experiment}")
    print(f"Initial interaction strategies: {initial_target}")
    print("Problems: " + ", ".join(args.problem_id))

    if args.initialize_only:
        for index, seed in enumerate(initial_population[: args.max_rounds], 1):
            round_dir = workflows_dir / f"round_{index}"
            round_dir.mkdir(parents=True, exist_ok=True)
            strategy_path = round_dir / "strategy.json"
            strategy = workflow_evolution.read_json(strategy_path, {}) or seed
            workflow_evolution.write_json(strategy_path, strategy)
            workflow_evolution.write_json(round_dir / "workflow.json", strategy)
            (round_dir / "prompt.md").write_text(
                build_end_to_end_prompt(strategy), encoding="utf-8"
            )
            print(f"Initialization complete; prompt: {round_dir / 'prompt.md'}")
        return

    workflow.write_execution_time_excel(
        workflows_dir / "round_execution_times.xlsx",
        workflow.normalized_results(results_path),
    )
    workflow_evolution.configure_completion_grace(
        baseline.run_problem, args.completion_grace
    )
    openclaw = baseline.find_openclaw_command(args.openclaw_command)
    atexit.register(interaction.cleanup_experiment_agents_at_exit, openclaw, experiment)
    run_args = runtime_args(args)

    seed_count = min(len(initial_population), args.max_rounds)
    results = workflow.normalized_results(results_path)
    pending_seeds = []
    for round_number in range(1, seed_count + 1):
        if workflow.completed_round_result(
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
        saved = workflow.without_removed_workflow_fields(
            workflow_evolution.read_json(round_dir / "strategy.json", {})
            or workflow_evolution.read_json(round_dir / "workflow.json", {})
        )
        strategy = saved or copy.deepcopy(initial_population[round_number - 1])
        round_dir.mkdir(parents=True, exist_ok=True)
        workflow_evolution.write_json(round_dir / "strategy.json", strategy)
        pending_seeds.append((round_number, strategy, existing))

    initial_errors: list[Exception] = []
    if pending_seeds:
        print(
            f"Running {len(pending_seeds)} independent initial strategy rounds "
            f"in parallel (per-round problem concurrency={args.concurrency})",
            flush=True,
        )
        with ThreadPoolExecutor(max_workers=len(pending_seeds)) as executor:
            futures = {}
            for round_number, strategy, existing in pending_seeds:
                seed_args = copy.copy(run_args)
                seed_args.concurrency = args.concurrency
                seed_args.retry_concurrency = args.retry_concurrency
                future = executor.submit(
                    execute_strategy_round,
                    experiment,
                    round_number,
                    strategy,
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
                    workflow.persist_round_result(experiment, results_path, result)
                    if failures:
                        initial_errors.append(
                            RuntimeError(
                                f"{len(failures)} run(s) failed the substantive "
                                f"interaction gate in round {round_number}"
                            )
                        )
                except Exception as error:
                    initial_errors.append(error)
    if initial_errors:
        raise RuntimeError(
            f"{len(initial_errors)} initial strategy round(s) failed; "
            "their checkpoints were preserved"
        ) from initial_errors[0]

    results = workflow.normalized_results(results_path)
    workflow.maybe_evolve_dialogue_operator(results, workflows_dir, args, problems)

    for round_number in range(seed_count + 1, args.max_rounds + 1):
        results = workflow.normalized_results(results_path)
        if workflow.completed_round_result(
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
        saved = workflow.without_removed_workflow_fields(
            workflow_evolution.read_json(round_dir / "strategy.json", {})
            or workflow_evolution.read_json(round_dir / "workflow.json", {})
        )
        strategy = saved or workflow.propose_workflow(
            results, round_number, round_dir, args, problems
        )
        workflow_evolution.write_json(round_dir / "strategy.json", strategy)
        result, failures = execute_strategy_round(
            experiment,
            round_number,
            strategy,
            fixed_rubric,
            problems,
            run_args,
            existing,
            args.enforce_substantive_interaction_gate,
        )
        results = workflow.persist_round_result(experiment, results_path, result)
        if failures:
            raise RuntimeError(
                f"{len(failures)} run(s) failed the substantive-interaction gate; "
                f"see {round_dir / 'result.json'}"
            )
        workflow.maybe_evolve_dialogue_operator(results, workflows_dir, args, problems)

    final_results = workflow.normalized_results(results_path)
    incomplete_rounds = [
        round_number
        for round_number in range(1, args.max_rounds + 1)
        if workflow.completed_round_result(
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
    plot_path = workflow.plot_round_average_dimension_scores(
        final_results, workflows_dir / "round_average_dimension_scores.png"
    )
    print(f"Round dimension plot: {plot_path}", flush=True)


if __name__ == "__main__":
    main()
