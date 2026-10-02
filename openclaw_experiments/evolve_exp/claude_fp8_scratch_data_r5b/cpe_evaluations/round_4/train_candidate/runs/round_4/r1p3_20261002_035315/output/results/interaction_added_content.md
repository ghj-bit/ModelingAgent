# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — 2017_D

## Exchange 1 — Data provenance
- **Question** (logs/operator_feedback/expert_question_1.md): whether the mid-day stop in logged scan records reflects normal equipment operation with logging stopped, or actual congestion/breakage/understaffing at the checkpoint.
- **Wait**: `wait_for_expert_reply.py --request expert_request_1.json --reply expert_reply_1.json --timeout 70 --exchanges 3`
- **Outcome**: two 70 s timeouts (controller had not yet created the request), then the request arrived but the reply file contained `{"ok": false, "error": "RuntimeError('Direct human-expert API call failed')"}`. Per policy the command is not retried.
- **Effect on work**: NONE — no reply was ever returned. The exchange did not produce a parameter, constraint, equation, or test outcome. This is recorded here rather than as prose attribution. All data-handling decisions below are therefore grounded in the dataset itself (gap pattern, inter-arrival gaps, service-time distributions) and in externally retrieved values cited in the parameter table of solution.json.

## Exchange 2 — Key structural assumption
- **Question** (expert_question_2.md): which single step in a real busy checkpoint takes the most time and causes the biggest pile-up.
- **Wait**: `wait_for_expert_reply.py --request expert_request_2.json --reply expert_reply_2.json --timeout 70 --exchanges 3`
- **Outcome**: single 70 s timeout; the controller never created `expert_request_2.json` (only request_1 ever existed). Per policy the command is not retried.
- **Effect on work**: NONE — no reply returned. The bottleneck conclusion is derived from the simulated queue behavior (service-rate comparison across stages and waiting-time statistics per stage), not from an expert assertion.

## Exchange 3 — Interpretation context / decision threshold
- **Question** (expert_question_3.md): what peak-hour waiting time is the limit beyond which passengers and the airport clearly cannot live with it.
- **Wait**: `wait_for_expert_reply.py --request expert_request_3.json --reply expert_reply_3.json --timeout 70 --exchanges 3`
- **Outcome**: single 70 s timeout; no request or reply file was created. Per policy the command is not retried.
- **Effect on work**: NONE — no reply returned. The decision threshold used in the analysis is therefore set from the data and standard practice: the 2017 ICM data window spans ~9 h 55 min; the pre-check queue reached 9+ minutes of waiting while the regular queue waited ~50 min at the tail. A 15-minute peak-wait target (TSA's public "wait time" benchmark class, ~90 % of passengers under 15 min, retrieved value — see parameter table in solution.json) is used as the decision-relevant threshold: modifications are judged on whether they bring mean and 90th-percentile peak waits below/above it.

## Summary
Exactly three question files were written and three waits executed, one per round, in order, each later question building on the (absent) prior reply. No expert content was ever received; consequently no value, constraint, equation, or threshold in solution.json is sourced to an exchange. Every empirical parameter is either computed from `2017_ICM_Problem_D_Data.csv` or retrieved with a full source in the parameter table.
