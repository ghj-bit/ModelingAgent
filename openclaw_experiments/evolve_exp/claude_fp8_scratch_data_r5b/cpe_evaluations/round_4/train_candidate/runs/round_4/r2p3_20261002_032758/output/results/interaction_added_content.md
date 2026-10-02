# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — 2017_D (MM-Bench)

Policy: 3 fixed exchanges, one question each.

## Exchange 1 (Data provenance)

**Question asked** (`logs/operator_feedback/expert_question_1.md`):
> At a real airport checkpoint, when records like X-ray scan times stop being
> logged partway through the day, what usually causes that to happen on the
> ground?

**Request file**: `logs/operator_feedback/expert_request_1.json` (created by
controller, rubric `interaction_initial_substantive_v1`, stage 2).

**Status: FAILED — no reply received.**

Evidence of attempts (all against the same request file, per policy):

1. First handshake: timeout.
2. Controller later wrote `expert_reply_1.json` with
   `{"ok": false, "exchange": 1, "error": "RuntimeError('Direct human-expert API call failed')"}`.
3. Removed the failed reply file, re-ran handshake: timeout.
4. Polled the directory for 2 minutes: no reply appeared.
5. Re-ran handshake: timeout.
6. Cleared the stale reply again, waited 45 s, re-ran handshake: timeout.
7. One final handshake attempt: timeout.

Total wall time spent on the exchange: ~12 minutes. The controller's
human-expert backend was non-functional for this run (one visible
`ok:false` payload, otherwise the reply file was never produced).

**How the reply was meant to affect the work** (per the interaction
strategy, Exchange 1 = data provenance): the answer would have supplied
the operational reason for the column-level missingness observed in the
audit (ID Check 1/2, X-Ray 1/2, millimeter-wave, and belt columns all stop
being populated in the second half of the day; e.g. X-Ray Scan Time 2 is
missing for 54/58 rows, ID Check 2 for 51/58, ID Check 1 for 49/58,
belt for 29/58). The missing pattern is trailing (each column's values
end, then blanks continue to the end of the file), consistent with
officer/machine logging stopping or a checkpoint change mid-observation,
rather than random sensor dropout.

**Substitution used** (recorded here so the gap is auditable):
- Because no expert reply arrived, the model uses *conservative imputation by
  column truncation*: only the leading populated block of each column is
  treated as representative of steady-state service, and every rate
  parameter is taken from that block (see the parameter table in
  `solution.json`, task 2, field `mathematical_modeling_process`).
- The structural assumption behind this (steady state over the leading
  block) is stated explicitly as assumption A2 in the solution, with its
  qualitative support: arrival gaps are monotone non-negative and
  stationary in the first 10 minutes (pre-check mean gap 9.2 s, regular
  13.0 s, no negative gaps in 58 rows), and the process-time columns that
  are populated early show low coefficient of variation (ID 1/2: 0.29/0.36).
- The decision-relevant threshold (Exchange 3 topic) is instead fixed from
  the problem context: a passenger-facing wait is decision-relevant when
  it threatens a flight connection; the model therefore reports mean,
  p95 and p99 of total wait plus the variance decomposition by zone,
  and all recommendations are conditioned on keeping p95 total wait under
  the ~10-minute level that the base case only achieves after
  modification (see task 4).

No other exchanges were possible: exchanges 2 and 3 must each build on the
previous reply, and no reply arrived for exchange 1.

## Exchanges 2 and 3

Not executed — dependent on the missing Exchange 1 reply. No
`expert_question_2.md` / `expert_question_3.md` were written, and no
further handshake commands were run, because the policy requires each
later question to build on an earlier reply and that reply never
existed. The two topics (structural-assumption validation; uncertainty
interpretation threshold) were covered in the model itself instead:
assumption A2 (steady state) is tested against the data's stationarity in
task 2, and the uncertainty/decision threshold is fixed as above and
carried through task 4.
