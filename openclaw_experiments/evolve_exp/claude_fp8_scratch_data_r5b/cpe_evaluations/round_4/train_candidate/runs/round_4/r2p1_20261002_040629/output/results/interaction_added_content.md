# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — 2024_D (Great Lakes)

**Outcome: the consultation did not happen.** The expert endpoint was down for the entire run. 13 foreground + 2 background attempts between 04:08 and ~04:55 (plus a 3-minute cron probe), each a single bounded wait of `wait_for_expert_reply.py`, all returned `RuntimeError('Direct human-expert API call failed')`; no reply file ever contained `ok: true`. Per policy, an exchange that produces no reply "did not happen" — recorded here instead of in prose in the submission. Nothing in `solution.json` is drawn from an expert reply; every empirical value there is either from the task dataset or from a source cited in its parameter table.

---

Expert channel: human-modeling-expert via `wait_for_expert_reply.py` (3 exchanges planned).

## Exchange 1 — Data provenance (IN PROGRESS)

**Question asked (04:16, 20 words):** "In the Great Lakes river records, some monthly flow months are left blank instead of showing a number. When you see such blanks in the records, what do they usually mean in practice: the flow was not measured, nothing was flowing, or the agency did not report it?"

**Context the question answers:** 11 sheets contain '---' blanks: St. Mary's / St. Clair / Detroit flows 2000-2008 + Dec 2022, St. Lawrence flow 2000-2011, Niagara flow 2021-22, one Ottawa cell (Sep 2022). The model's handling of these blanks (treat as missing, exclude from means, never impute to zero, calibrate on the complete 2012-2022 window) rests on their meaning.

**Status:** the expert API endpoint has failed on every attempt since 04:07 with `RuntimeError('Direct human-expert API call failed')` — 8 foreground attempts (04:08-04:3x), each a single bounded wait per policy; a 3-minute cron retry is scheduled so the exchange completes as soon as the endpoint recovers. The request file (`expert_request_1.json`) carries the question; `expert_reply_1.json` currently holds the controller's error record.

**Working assumption pending the reply (recorded here, NOT as expert input):** blanks are non-reporting / missing measurements, consistent with the dataset description's "empty values as '---'" and with the pattern (whole early years missing on stations that report later years — an availability pattern, not a zero-flow pattern; a river cannot be at 0 m3/s for 12 straight months while its downstream station reports normal flow).

## Exchange 2 — Structural assumption (pending)

Planned question, builds on Exchange 1's answer about representativeness of the remaining years: whether, for someone who has seen these records, the months that ARE reported look like a fair sample of normal conditions, or like the easy/dry months. Model use if confirmed: 2012-2022 window is representative for the seasonal targets T_m and inflow climatology I_m.

## Exchange 3 — Interpretation context (pending)

Planned question, builds on 1-2: from a decision-making point of view, how far off the normal level would a lake have to be before its managers treat that as a real problem rather than normal seasonal variation. Model use: the no-penalty band (currently 0.61 m from the problem statement's 2 ft) and the point at which stakeholder scores drop off.

## Impact record

To be completed per exchange once replies arrive: question, verbatim reply, the parameter/constraint/decision-rule it changed, and the run that consumed it.
