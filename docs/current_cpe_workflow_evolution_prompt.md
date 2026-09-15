# 当前 CPE 双父本工作流演化器 Prompt 结构预览

这份文件由当前代码中的 `build_cpe_workflow_evolution_prompt()` 直接生成。尖括号字段和 `0.0` 是运行时占位值。真正执行到第 4 轮及以后时，会替换为两个训练父本在同一批训练题上的工作流、净效用、公开题目、专家交互、交互引起的报告修改摘要和交互成本。

题目级 ModelingBench Judge 分数、维度分、Judge 反馈和 Judge 缺陷摘要不会进入这个 Prompt。验证冠军仍只提供工作流与聚合净效用。

## System message

```text
Return one concise valid JSON workflow object.
```

## User message

```text
Evolve one executable human-expert interaction workflow
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
[
  {
    "parent_rank": 1,
    "workflow_id": "<TRAINING_PARENT_1_WORKFLOW_ID>",
    "workflow": {
      "name": "<TRAINING_PARENT_1_NAME>",
      "entry_action": "<TRAINING_PARENT_1_ENTRY_ACTION>",
      "actions": [
        {
          "action_id": "<TRAINING_PARENT_1_AUDIT_ACTION>",
          "action_type": "agent_audit",
          "rule": "<TRAINING_PARENT_1_AUDIT_RULE>"
        },
        {
          "action_id": "<TRAINING_PARENT_1_EXPERT_ACTION>",
          "action_type": "expert_exchange",
          "rule": "<TRAINING_PARENT_1_EXPERT_RULE>"
        },
        {
          "action_id": "<TRAINING_PARENT_1_VALIDATION_ACTION>",
          "action_type": "agent_validation",
          "rule": "<TRAINING_PARENT_1_VALIDATION_RULE>"
        }
      ],
      "max_exchanges": 2,
      "stop_condition": "<TRAINING_PARENT_1_STOP_CONDITION>",
      "workflow_id": "<TRAINING_PARENT_1_WORKFLOW_ID>"
    },
    "net_utility_on_current_training_batch": 0.0,
    "training_evidence": {
      "round": "<CURRENT_ROUND>",
      "training_runs": [
        {
          "problem_id": "<TRAINING_PARENT_1_PROBLEM_ID>",
          "title": "<TRAINING_PARENT_1_PROBLEM_TITLE>",
          "question": "<FULL_PUBLIC_TRAINING_TASK_STATEMENT>",
          "artifacts": [
            {
              "artifact_type": "expert_interaction",
              "content": "<FULL_RAW_EXPERT_DIALOGUE>"
            }
          ],
          "interaction_report_change_summary": "<INTERACTION_ATTRIBUTABLE_SUMMARY_MAX_50_CHARS>"
        }
      ],
      "average_interaction_cost": 0.0,
      "average_interaction_penalty": 0.0,
      "interaction_cost_parameters": "<RUNTIME_COST_CONFIGURATION>"
    }
  },
  {
    "parent_rank": 2,
    "workflow_id": "<TRAINING_PARENT_2_WORKFLOW_ID>",
    "workflow": {
      "name": "<TRAINING_PARENT_2_NAME>",
      "entry_action": "<TRAINING_PARENT_2_ENTRY_ACTION>",
      "actions": [
        {
          "action_id": "<TRAINING_PARENT_2_AUDIT_ACTION>",
          "action_type": "agent_audit",
          "rule": "<TRAINING_PARENT_2_AUDIT_RULE>"
        },
        {
          "action_id": "<TRAINING_PARENT_2_EXPERT_ACTION>",
          "action_type": "expert_exchange",
          "rule": "<TRAINING_PARENT_2_EXPERT_RULE>"
        },
        {
          "action_id": "<TRAINING_PARENT_2_VALIDATION_ACTION>",
          "action_type": "agent_validation",
          "rule": "<TRAINING_PARENT_2_VALIDATION_RULE>"
        }
      ],
      "max_exchanges": 2,
      "stop_condition": "<TRAINING_PARENT_2_STOP_CONDITION>",
      "workflow_id": "<TRAINING_PARENT_2_WORKFLOW_ID>"
    },
    "net_utility_on_current_training_batch": 0.0,
    "training_evidence": {
      "round": "<CURRENT_ROUND>",
      "training_runs": [
        {
          "problem_id": "<TRAINING_PARENT_2_PROBLEM_ID>",
          "title": "<TRAINING_PARENT_2_PROBLEM_TITLE>",
          "question": "<FULL_PUBLIC_TRAINING_TASK_STATEMENT>",
          "artifacts": [
            {
              "artifact_type": "expert_interaction",
              "content": "<FULL_RAW_EXPERT_DIALOGUE>"
            }
          ],
          "interaction_report_change_summary": "<INTERACTION_ATTRIBUTABLE_SUMMARY_MAX_50_CHARS>"
        }
      ],
      "average_interaction_cost": 0.0,
      "average_interaction_penalty": 0.0,
      "interaction_cost_parameters": "<RUNTIME_COST_CONFIGURATION>"
    }
  }
]

Historical validation champion. This record intentionally contains only its
communication workflow and mean net utility:
{
  "workflow": {
    "name": "<VALIDATION_CHAMPION_NAME>",
    "entry_action": "<VALIDATION_CHAMPION_ENTRY_ACTION>",
    "actions": [
      {
        "action_id": "<VALIDATION_CHAMPION_AUDIT_ACTION>",
        "action_type": "agent_audit",
        "rule": "<VALIDATION_CHAMPION_AUDIT_RULE>"
      },
      {
        "action_id": "<VALIDATION_CHAMPION_EXPERT_ACTION>",
        "action_type": "expert_exchange",
        "rule": "<VALIDATION_CHAMPION_EXPERT_RULE>"
      },
      {
        "action_id": "<VALIDATION_CHAMPION_VALIDATION_ACTION>",
        "action_type": "agent_validation",
        "rule": "<VALIDATION_CHAMPION_VALIDATION_RULE>"
      }
    ],
    "max_exchanges": 2,
    "stop_condition": "<VALIDATION_CHAMPION_STOP_CONDITION>",
    "workflow_id": "<VALIDATION_CHAMPION_WORKFLOW_ID>"
  },
  "utility": 0.0
}

Recent training-only decision history:
[
  {
    "round": "<RECENT_ROUND>",
    "candidate_workflow_id": "<CANDIDATE_WORKFLOW_ID>",
    "parent_train_net_utilities": [
      0.0,
      0.0
    ],
    "candidate_train_net_utility": 0.0,
    "train_accepted": "<true_or_false>"
  }
]

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
{
  "assumption_audit": {
    "purpose": "Challenge the real-world plausibility of assumptions that materially control the conclusion.",
    "rule": "After the agent ranks the draft's high-impact assumptions, present the materially consequential weakly supported assumptions and their real-world meanings without defending them. The request may contain multiple distinct issues when they affect different parts of the conclusion. Ask the expert to challenge their plausibility, identify omitted conditions, or explain when they could fail. The expert supplies qualitative domain judgment; the agent owns every technical translation, calculation, and validation.",
    "output": "Reality-based challenges to high-impact modeling assumptions."
  },
  "model_failure_mode": {
    "purpose": "Use expert challenge to expose real-world failure modes of dangerous technical weaknesses.",
    "rule": "After the agent audits equations, constraints, code, and their consistency, present the real-world implications of the dangerous unresolved technical weaknesses. The request may cover multiple independent weaknesses rather than forcing selection of only one. Ask the expert to attack those implications with plausible failure conditions or counterexamples. Do not ask the expert to inspect code or calculate; the agent must repair the technical model and test every repair independently.",
    "output": "Plausible real-world failure conditions tied to audited technical weaknesses."
  },
  "data_parameter_boundary": {
    "purpose": "Ground the most influential and weakly evidenced parameter before recalibrating the model.",
    "rule": "After the agent identifies conclusion-sensitive parameters, parameter groups, or empirical claims with weak evidence, explain their distinct decision roles and ask the expert for qualitative real-world bounds, observable boundary conditions, and suitable authoritative evidence types. The request may cover multiple independent weak inputs. The expert must not invent numerical estimates. The agent must obtain external evidence when claims are externally verifiable, set defensible values or ranges, recalibrate, and compare conclusions.",
    "output": "Qualitative real-world boundaries and evidence plans for influential weak inputs."
  }
}

Return only one JSON object with name, purpose, entry_action, actions,
max_exchanges, stop_condition, evolution_mode, changed_components, and
evolution_rationale. evolution_mode must be exactly `crossover` or `mutation`.
Use two to eight ordered actions. Each action contains action_id, action_type,
and rule, and at least one action has action_type expert_exchange. Encode the
targeted patch in the returned full workflow. In evolution_rationale, explain
why the selected mode fits the two parents' evidence, how both parents were
considered, and which training signal motivated each changed component.

```

## 重试时追加的内容

```text
The previous proposal was rejected. Return a different targeted behavioral patch. Rejection: <VALIDATION_ERROR>
```
