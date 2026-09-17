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
      "rule": "inspect the mathematical formulation, units, constraints, algorithms, and executable code for internal consistency and agreement with the problem statement. use targeted sanity or boundary checks to rank weaknesses, then retain at most two independent weaknesses most likely to reverse the primary recommendation or invalidate a headline result. group redundant findings by causal chain and record lower-priority findings as residual limitations.",
      "policy": null,
      "input_fields": null,
      "output_fields": null,
      "budget": null
    },
    {
      "action_id": "action_2",
      "action_type": "expert_exchange",
      "rule": "present the real-world implications of only the selected one or two dangerous technical weaknesses. ask the expert to attack those implications with plausible failure conditions or counterexamples. do not ask the expert to inspect code or calculate; the agent must repair the selected weaknesses and test each repair independently.",
      "policy": null,
      "input_fields": null,
      "output_fields": null,
      "budget": null
    },
    {
      "action_id": "action_3",
      "action_type": "agent_analysis",
      "rule": "convert each selected material failure condition into one precise technical test. make the smallest sufficient correction to the affected equations, constraints, algorithms, data transformations, or code, and regenerate outputs that directly depend on that correction. do not repair unrelated weaknesses or broaden the model unless the selected failure condition cannot otherwise be tested.",
      "policy": null,
      "input_fields": null,
      "output_fields": null,
      "budget": null
    },
    {
      "action_id": "action_4",
      "action_type": "agent_validation",
      "rule": "validate each selected repair with one proportionate independent check, preferring an analytical special case, invariant, or targeted boundary test over a second full implementation. compare the decision-relevant old and repaired results and update the recommendation and confidence boundary.",
      "policy": null,
      "input_fields": null,
      "output_fields": null,
      "budget": null
    },
    {
      "action_id": "action_5",
      "action_type": "close",
      "rule": "re-audit only the selected failure modes after the first repair pass. use a second exchange when a selected unresolved failure mode still requires expert judgment; otherwise stop, integrate the verified results, and record remaining lower-priority weaknesses as limitations.",
      "policy": null,
      "input_fields": null,
      "output_fields": null,
      "budget": null
    }
  ],
  "max_exchanges": 2,
  "stop_condition": "stop after the selected one or two failure conditions have each received one focused repair and one proportionate independent check, or after a second exchange for an unresolved selected failure mode followed by that bounded validation. record other weaknesses as residual limitations rather than expanding the run."
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
