# Expert Interaction Evidence — 2017_D

The consultation policy required exactly three exchanges, one question each,
sequenced as data provenance → structural assumption → interpretation context.
All three questions were asked through the prescribed handshake (question file
written to `logs/operator_feedback/expert_question_N.md`, then
`wait_for_expert_reply.py` run once against the matching
`expert_request_N.json` / `expert_reply_N.json`).

## Exchange 1 — Data provenance and completeness

- Question (file `expert_question_1.md`): whether the blank entries in the
  ID-check and X-ray columns reflect sensor/equipment failures and missed
  recordings, and whether the surviving readings still represent a typical day.
- Handshake: `expert_request_1.json` was created by the controller at
  03:30 and contains the verbatim question (rubric `interaction_initial_substantive_v1`).
- **No reply arrived.** `wait_for_expert_reply.py` (timeout 70 s) was run once;
  the controller created the request but never wrote `expert_reply_1.json`, and
  the wait timed out. Per the interaction rules the request/reply files are
  owned by the controller, and the agent must not poll or retry, so the
  consultation is recorded as attempted and unanswered for this run.

  **Effect on the work (declared in lieu of a reply):** the model treats the
  missingness as a hard input constraint rather than imputing it. The ID-check
  columns stop recording after ~7 min and the X-ray columns after ~1.5 min, so
  no rate is estimated from those columns past their recording windows; every
  service rate used in the model is either estimated from the columns while
  they are populated (body scanner: 40 stamps over 7.6 min → 5.16/min;
  X-ray: 15 bag stamps → 11.55/min combined; ID officers: 16 stamps →
  27.7–47.5/min per officer, mean 31.6/min) or an explicit documented
  assumption (see the parameter table in solution.json). The small samples
  (n ≤ 40 per column) are carried into the stated uncertainty of the results.

## Exchange 2 — Structural assumption

- Question (file `expert_question_2.md`): given the early stoppage of the
  ID-check recording, is it reasonable to treat each checkpoint step as
  working at a steady, independent pace hour after hour, and what practice
  supports or undermines that.
- Handshake: written after exchange 1; `wait_for_expert_reply.py` run once;
  timed out (no request/reply produced for this exchange in this run).

  **Effect on the work (declared in lieu of a reply):** the steady-pace,
  independent-stations assumption is retained but stress-tested in the model
  instead of assumed away. Concretely: (i) the Poisson arrival assumption is
  justified by the observed interarrival CV = 1.11 (close to 1 for a Poisson
  process); (ii) service times are drawn from exponential/lognormal
  distributions rather than fixed, so pacing variation enters the queue
  dynamics; (iii) an arrival-rate sensitivity sweep (λ = 8…14/min, log
  `checkpoint_model_sweep_lam.log`) shows mean checkpoint time moving
  30.5 → 74.0 min, so the conclusion that the line-front is the bottleneck is
  stated over that whole range, not only at the single observed rate.

## Exchange 3 — Interpretation context for uncertainty

- Question (file `expert_question_3.md`): when a queue is estimated rather
  than measured, what level of wait-time error is still useful for staffing
  decisions, and at what point the number should no longer be trusted.
- Handshake: written after exchange 2; `wait_for_expert_reply.py` run once;
  timed out.

  **Effect on the work (declared in lieu of a reply):** the decision-relevant
  framing is built into the results. All comparisons are made as *relative*
  changes of the same model (modification vs baseline, culture share vs
  share 0), which cancels the absolute calibration error; the absolute mean
  wait (≈50 min at λ = 10.58/min) is reported with the explicit caveat that it
  inherits the single-day, 58-passenger, partial-recording calibration, while
  the *ranking* of modifications (pre-binning > scanner additions > pooled
  single line) is robust across the swept ranges (bin prep 10–40 s,
  c_x 2–6, c_m 1–3, λ 8–14). For staffing decisions the model's guidance is
  therefore: trust the direction and the size of the improvement (e.g.
  bin-prep 25 s → 20 s cuts mean checkpoint time from 49.9 to 48.3 min,
  ≈ 3%), not the absolute minutes.

## Record

| # | question file | request file | reply file | outcome |
|---|---------------|--------------|------------|---------|
| 1 | expert_question_1.md | expert_request_1.json (controller-created) | — | no reply; 70 s timeout |
| 2 | expert_question_2.md | — | — | no request produced; 70 s timeout |
| 3 | expert_question_3.md | — | — | no request produced; 70 s timeout |

No expert sentences were copied into the submission; the three "declared in
lieu" notes above are the only trace of the exchanges, and they state what the
model does with the gaps.
