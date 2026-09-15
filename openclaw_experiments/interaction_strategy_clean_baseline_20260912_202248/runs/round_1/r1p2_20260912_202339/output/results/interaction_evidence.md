# Interaction evidence — 2003_Aviation_Baggage_Screening

Run: `interaction_strategy_clean_baseline_20260912_202248 / round_1 / r1p2_20260912_202339`
Variant: **clean baseline** (`execution_mode = end_to_end_expert_guided_modeling`,
`initial_draft_used = false`).

## 1. Baseline plan (agent-owned)

1. Parse TIS Table 1 → per-airport passengers and checked-bag demand with formal
   moments (1.4 bags/passenger; variance propagated across 46 (A) / 48 (B) flights).
2. Size EDS capacity under three planning assumptions (M1 aggregate, M2 arrival
   rate, M3 scheduling) with throughput 160–210 bags/h and 92% availability.
3. Build a scheduling model; prove the arrival-window invariance; optimise the
   departure-bank span `H`.
4. Add ETD as alarm-resolution layer; cost and policy comparison.
5. Scale to 193 Midwest airports and 429 national airports.
6. Empirical checks: Federal Register 67 FR 48436 (ETD ≥180 samples/h) and
   Leidos Reveal CT throughput (226/250 bags/h).

## 2. Expert consultation attempt (no reply received)

- Per the run protocol, the agent wrote the qualitative question to
  `logs/operator_feedback/expert_question_1.md` (2026-09-12 20:34) and executed
  once in the foreground:

  `python code/wait_for_expert_reply.py --request logs/operator_feedback/expert_request_1.json --reply logs/operator_feedback/expert_reply_1.json --timeout 300`

- Outcome: **timed out (exit code 1)**. The Python controller never created
  `expert_request_1.json`, and no `expert_reply_1.json` or
  `human_expert_dialogue.md` was produced. This is consistent with the controller
  source for this variant, whose entry point is documented as *"Execute and judge
  one problem **without starting the expert bridge**."*
- Consequence: **no live expert reply existed**, so no expert-derived content is
  claimed anywhere in the report. The attempted question is retained at
  `logs/operator_feedback/expert_question_1.md`; no request/reply JSON was
  fabricated or edited.

## 3. Reply-triggered change

None (no reply was received). The robustness change below was made independently
by the agent, prompted by the residual uncertainty the question targeted
(enforceability of departure-bank re-timing), not by any received advice.

## 4. Independent robustness change and its downstream effect

- **Change:** replaced the single full-adoption scheduling optimum with an
  adoption-conditional procurement curve. Let `f` be the share of peak-hour
  flights that can be re-timed; then `r_peak(f) = Λ[(1−f)/75 + f/120]` and
  `N(f) = ⌈60 r_peak(f)/(cη)⌉` (report eq. 3a, §6.3.1, model code
  `adoption_curve` / `break_even_adoption` in `code/baggage_model.py`).
- **Affected evidence:** `results/model_results.json` →
  `scheduling.A.adoption`, `scheduling.B.adoption`, `scheduling.*.break_even`;
  report Executive Summary, §4.4, §6.3, §6.3.1, §6.5, §8.2, §9, §10.
- **Result:** A 30/27/24/22/19 and B 32/29/26/23/20 EDS at `f` = 0/25/50/75/100%;
  break-even A `f ≥ 0.22` (27 EDS), B `f ≥ 0.14` (30 EDS).
- **Effect on conclusion / confidence / presentation:** the report no longer
  headlines the full-adoption minimum (19/20 EDS). It leads with the enforceable
  no-cooperation base (A 30 / B 32), states the confidence boundary (A 19–30 /
  B 20–32) and the caveat that the re-timing saving is contingent on cooperation
  the airport cannot compel. Recommendations are now framed conditionally rather
  than as an unconditional optimum.
