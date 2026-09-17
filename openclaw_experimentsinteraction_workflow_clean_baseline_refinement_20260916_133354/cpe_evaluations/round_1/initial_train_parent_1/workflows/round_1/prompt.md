# Expert-Guided Modeling Report Refinement

Use the supplied no-interaction draft as a starting point, then independently audit and improve the complete modeling solution. Rebuild any part of the model or analysis when the evidence indicates that the inherited approach is inadequate.

## Problem Metadata

- Problem ID: `{{PROBLEM_ID}}`
- Title: {{TITLE}}
- Source: {{SOURCE}}
- Year: {{YEAR}}

## Authoritative Problem Statement

{{QUESTION}}

## Files

- Original draft (read-only): `{{RESULTS_DIR}}/original_report.md`
- Refined standalone report: `{{FINAL_REPORT}}`
- Interaction evidence: `{{RESULTS_DIR}}/interaction_evidence.md`
- Expert request/reply/dialogue: `{{OPERATOR_FEEDBACK_DIR}}`
- The rest of the baseline modeling workspace has been inherited at the same
  relative paths under `{{OUTPUT_DIR}}`, including reusable code, data,
  numerical results, and figures.

Read the original draft and inherited artifacts as inputs, not as presumptively correct constraints. Actively inspect the assumptions, formulation, data, calculations, code, and conclusions for weaknesses, and modify or replace any part needed to produce a stronger solution. If you modify executable code, model parameters, or data-processing logic, execute the affected code again and regenerate every dependent numerical result, table, and figure before updating the report. Do not cite stale inherited outputs produced by an older version of the code.
Ensure that the refined report still answers the complete authoritative
problem.

## Single-Agent Execution Boundary

Complete the full problem refinement in this solver Agent. Do not spawn, call,
message, or delegate work to a child Agent or any other Agent, and do not use
`sessions_spawn`, `sessions_send`, or `subagents`. Perform research, coding,
calculation, validation, and report writing with this Agent's own tools. The
controller-managed human-expert exchanges required by the interaction workflow
remain available and are not subagents.

## Expert Interaction Workflow

Follow this interaction workflow as an ordered, condition-aware action list:

```json
{
  "entry_action": "action_1",
  "actions": [
    {
      "action_id": "action_1",
      "action_type": "agent_audit",
      "rule": "list the assumptions that could materially change the model's principal conclusions. rank them by decision impact and evidential weakness, then retain at most two independent assumptions most likely to reverse the primary recommendation or invalidate a headline result. exclude redundant assumptions from the same causal chain, record lower-priority assumptions as residual limitations, and do not assume that the inherited formulation is correct.",
      "policy": null,
      "input_fields": null,
      "output_fields": null,
      "budget": null
    },
    {
      "action_id": "action_2",
      "action_type": "expert_exchange",
      "rule": "present only the selected one or two materially consequential weakly supported assumptions and their real-world meanings without defending them. ask the expert to challenge their plausibility, identify omitted conditions, or explain when they could fail. the expert supplies qualitative domain judgment; the agent owns every technical translation, calculation, and validation.",
      "policy": null,
      "input_fields": null,
      "output_fields": null,
      "budget": null
    },
    {
      "action_id": "action_3",
      "action_type": "agent_analysis",
      "rule": "translate the material challenges to the selected assumptions into explicit, falsifiable model alternatives or boundary scenarios. state the smallest set of assumptions, equations, constraints, parameters, code paths, or decision criteria affected; do not directly adopt an expert-supplied number or technical prescription and do not expand the repair to unrelated model components.",
      "policy": null,
      "input_fields": null,
      "output_fields": null,
      "budget": null
    },
    {
      "action_id": "action_4",
      "action_type": "agent_validation",
      "rule": "implement the smallest justified alternatives for the selected assumptions. for each selected assumption, perform one primary recomputation and one proportionate independent check, then compare the decision-relevant outputs with the original formulation. regenerate outputs that directly depend on changed code or parameters.",
      "policy": null,
      "input_fields": null,
      "output_fields": null,
      "budget": null
    },
    {
      "action_id": "action_5",
      "action_type": "close",
      "rule": "after the first validation pass, review only the selected assumptions. use a second exchange when a selected unresolved issue still requires expert judgment; otherwise stop, integrate the supported consequences, and record unselected or unresolved lower-priority assumptions as limitations.",
      "policy": null,
      "input_fields": null,
      "output_fields": null,
      "budget": null
    }
  ],
  "max_exchanges": 2,
  "stop_condition": "stop after the selected one or two assumptions have each received one primary recomputation and one proportionate independent check, or after a second exchange for an unresolved selected issue followed by that bounded validation. record other assumptions as residual limitations rather than expanding the run."
}
```

Start with `entry_action`, which is the first item in `actions`, and execute the
remaining actions in listed order. Apply conditional follow-up and early-stop
logic from each action's `rule` and the workflow's `stop_condition`. For each
`expert_exchange`, write only the new qualitative question body to
`{{OPERATOR_FEEDBACK_DIR}}/expert_question_N.md`, using N=1, 2, then 3, and
run the following command once in the foreground:

`python "{{OUTPUT_DIR}}/code/wait_for_expert_reply.py" --request "{{OPERATOR_FEEDBACK_DIR}}/expert_request_N.json" --reply "{{OPERATOR_FEEDBACK_DIR}}/expert_reply_N.json" --timeout 180`

The controller creates request/reply JSON. Do not edit those JSON files and do
not start process-poll or command-retry loops. A later question must explicitly
build on the earlier reply and perform the next workflow action; do not repeat
the question or seek approval. Stop according to the workflow and never exceed
`max_exchanges`.

After the dialogue, write one concise
`{{RESULTS_DIR}}/interaction_evidence.md` containing the baseline plan, each
exchange's distinct decision contribution, the resolved consultation output,
the independently implemented analytical change and evidence paths, and its
effect on the conclusion, confidence, scope, or presentation. Keep this full
process account in `interaction_evidence.md`. Integrate only the substantive
modeling consequences into the final report's normal sections, without naming
the expert interaction or adding an `Expert Interaction Impact` section.

## Refinement Output

Write the complete refined Markdown report to `{{FINAL_REPORT}}`. Do not
edit `original_report.md`. The Python controller will compute the added or
revised content, file-change record, and one consolidated consistency check
after the run. Run affected Python programs directly; do not use shell output
redirection or Git. Do not expose private chain-of-thought.
