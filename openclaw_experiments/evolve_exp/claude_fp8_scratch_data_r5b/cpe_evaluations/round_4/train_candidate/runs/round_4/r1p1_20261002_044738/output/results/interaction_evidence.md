# Expert interaction evidence

## Attempted exchanges

**Exchange 1 (data provenance).**
Question (as written to `logs/operator_feedback/expert_question_1.md`):
> River-flow records are blank for 2000 to 2008. Why, and are the recorded years a fair picture of typical flow?

Outcome: the controller generated `expert_request_1.json` once, then the expert call failed with `RuntimeError('Direct human-expert API call failed')` (recorded in `expert_reply_1.json`). After that, the controller stopped generating request files for any question written to the feedback directory (verified by repeated directory listings over ~15 minutes, no `expert_request_*.json` appearing). No expert reply was ever received for this exchange.

**Exchange 2 (structural assumption).**
Question drafted: "When a lake is full in spring, should dam operators drain it faster to stop flooding, even though big ships need deep water?"
Outcome: not sent — the controller had already stopped generating request files. No exchange took place.

**Exchange 3 (interpretation threshold).**
Question not drafted — the channel was down before exchange 2 could complete. No exchange took place.

## Effect on the work

Per the interaction policy, an exchange that produces no reply "did not happen." No expert value, constraint, or equation entered the model from an exchange, because no exchange completed. The model's empirical inputs therefore come entirely from:
- the task's own dataset (all levels and flows, 2000-2022), and
- the parameter table in `solution.json`, whose sources are cited URLs (NOAA NCEI, NOAA Glerl, IJC LOSLRB) or calibration to the 2017 record in this dataset.

The three gaps the policy intended the exchanges to resolve were instead closed by the following documented choices:
1. **Data provenance (would have been Exchange 1):** the missing spans (St. Mary's/St. Clair/Detroit 2000-2008; Niagara 2021-2022; St. Lawrence 2000-2011) are reported in Subtask 1, and the closure analysis is restricted to 2013-2019, the window in which every term of the Ontario balance is present. The model does not use any pre-2012 river data for the Ontario results.
2. **Structural assumption (would have been Exchange 2):** the flat-surface volume balance is the core assumption; its validity is tested directly by the closure residuals (Subtask 1), which bound it empirically rather than by expert assertion.
3. **Interpretation threshold (would have been Exchange 3):** the stakeholder cost function with its flood ceiling (75.45 m) and shipping floor (74.20 m) is the decision-relevant threshold, sourced to the IJC LOSLRB guidance, and the sensitivity study (Subtask 3) quantifies how far a perturbation must push the level before it crosses those thresholds.

## Record of controller failure

- `expert_request_1.json` was created by the controller and carried the exchange-1 question.
- `expert_reply_1.json` (written by the controller) contained `{"ok": false, "exchange": 1, "error": "RuntimeError('Direct human-expert API call failed')"}`.
- Subsequent writes of `expert_question_1.md` and `expert_question_2.md` were not picked up: no `expert_request_2.json` or later request was ever generated, and no reply file of any kind appeared. The failure is on the controller's expert-API side, not on the question content or the file location (both match the documented handshake).

This is a tooling failure, not a modelling choice: the consultation ran 0 of 3 completed exchanges because the expert endpoint was unavailable for the entire duration of the run.
