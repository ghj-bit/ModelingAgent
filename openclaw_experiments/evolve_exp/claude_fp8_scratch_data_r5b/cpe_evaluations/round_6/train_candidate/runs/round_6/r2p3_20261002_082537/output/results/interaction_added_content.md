# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction evidence — 2017_C (self-driving cars on I-5 / I-90 / I-405 / SR-520)

Three exchanges, one question each, in `logs/operator_feedback/expert_question_N.md`;
replies in `expert_reply_N.json` (controller-managed). Each reply was converted
into a model parameter or rule before the next exchange.

## Exchange 1 — data-selection mechanism (governs data cleaning)

**Question:** In practice, which highway segments are skipped or reported zero
by traffic counters, and is that tied to how busy the segment is?

**Reply (substance):** Missing or zero-count records are *not* the busiest
segments. They concentrate on short/ramp-like stubs without a permanent count
station, low-volume rural SR segments where a counter is not justified,
directions with no separate count, and newly reconfigured segments with no
full-year record. Busy I-5/I-90/I-405/SR-520 mainline segments are almost
always counted. Empirical judgment about DOT practice, not a precise figure.

**Effect on the work (recorded in the model):**
- The cleaning rule in `code/model.py` (`clean_data`) was kept *additive*: a
  row is dropped only if AADT, lane count, or segment length is missing or
  non-positive, and the audit reports rows_raw vs rows_used. Nothing was
  imputed or reweighted, because the expert mechanism says the bias is
  concentrated on low-volume short stubs — imputing those would bias the
  *mean* downward and distort the capacity audit of the binding segments.
- Because the observed AADT distribution is selection-truncated (missingness
  anti-correlated with volume), all corridor statistics are reported on
  observed segments, and the interpretation is bounded below: true corridor
  volume is at least as high as computed, and congestion is at least as bad.
  This enters `subtask_outcome_analysis` as a stated bias, with the interval
  over which it holds: the whole dataset, strongest on SR 520 outlying segments
  (all SR, lowest volumes).

## Exchange 2 — structure of the dedicated-lane effect (governs the SDC/SDC-vs-human interaction term)

**Question:** On busy Seattle-area freeways, do drivers get in and out of
carpool lanes often enough that the carpool flow itself gets choppy?

**Reply (substance):** Yes, but the choppiness concentrates at access points
and interchange weave zones, where HOV users cross the buffer and intruders
merge; between access points the low-volume carpool lane is the *least*
choppy lane on the corridor. Effect is strongest at peak, when the speed
differential across the buffer is large. Empirical judgment.

**Effect on the work (recorded in the model):**
- The dedicated-lane term is treated as a *clean, full-speed* platoon stream
  (capacity `L_d · K_J^SDC · V_D`) rather than a discounted stream, but the
  *cooperation benefit in mixed lanes* is gated by a sensitivity parameter
  `s ∈ [0.3, 1.0]` — the range the reply supports (choppiness is real but
  localized, so the shockwave-damping benefit is partial, not total). The
  model is swept over `s = 0.3, 0.6, 1.0` and the result tables in
  `mathematical_modeling_process` / `subtask_outcome_analysis` carry that
  interval.
- The peak-time weighting is why the peak-hour factor (not AADT) drives the
  stress test: the expert says the lane-separation effect is strongest at
  peak, so a baseline computed at off-peak would understate the dedicated-lane
  advantage.

## Exchange 3 — bias-aware interpretation threshold (governs the tipping point and robustness claims)

**Question:** Once one in five or so drivers uses self-driving, does overall
freeway driving become noticeably smoother?

**Reply (substance):** No — not at 20%. Marked smoothing generally requires a
substantially higher share; roughly 50%+ is associated with marked smoothing,
clear robust improvement with 70–90%. The exact threshold is not precisely
known and depends on cooperation level, lane policy, and whether automated
cars are clustered or dispersed. One human driver in a platoon can still
trigger instability.

**Effect on the work (recorded in the model):**
- Tipping parameter `p_t = 0.50` (marked-smoothing onset) and
  `p_low = 0.20` (no marked change) fixed the shape of the stabilisation
  function `alpha(p)`: below 20% the effect is marginal (alpha ≈ 1), ramping
  to its minimum at 50%, with a saturating tail toward 90%.
- Interpretation rule adopted: a result is reported as a *robust signal* only
  if it survives the joint interval `p_t ∈ [0.5, 0.7]` and `s ∈ [0.3, 1.0]`;
  anything that flips inside that interval is labelled sensitivity-dependent.
  In the run: the dedicated-lane benefit and the I-5 2-lane bottleneck
  ranking are stable across the whole interval (robust); the exact LOS of
  individual segments is not (labelled accordingly).
- The answer to "is there a tipping point" is therefore: structurally yes at
  p ≈ 0.5 for flow stabilisation, but it does *not* fix capacity; the
  capacity tipping is lane-geometry driven (see solution.json).
