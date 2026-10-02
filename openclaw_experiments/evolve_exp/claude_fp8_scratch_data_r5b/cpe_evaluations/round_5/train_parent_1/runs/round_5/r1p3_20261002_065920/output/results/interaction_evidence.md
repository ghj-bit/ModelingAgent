# Interaction Evidence — Problem 2017_D (TSA Checkpoint)

## Exchange 1 — Data provenance and completeness

**Question** (expert_question_1.md): "At the airport, when the scan machines stop reporting times partway through the day, why does that usually happen, and can you still trust the times that were recorded?"

**Reply (key points)**: Machine logging stops mid-day for mundane operational reasons (shift change without re-logging, lane closure/re-purposing, device or logging-link dropout, export mid-shift, manual logging abandoned when queues back up). The stoppage is a data-collection artifact, not evidence about passenger flow. Recorded values are broadly usable as direct observations, but the sample is **not missing-at-random**: dropouts cluster in busy periods and shift changes, so the surviving sample is biased toward calmer, better-staffed conditions; it under-states peak waits. Cross-check plausibility before use; do not extrapolate the recorded rate to unlogged hours.

**How the reply was turned into work**:
- Data-cleaning decision: the right-censoring pattern in the dataset (ID Check 1: 9/58, ID Check 2: 7/58, X-Ray 2: 4/58, belt time: 29/58 values, all right-censored from a row onward) is treated as a *logging artifact*, not as evidence of process change; no values imputed from censored tails.
- Service-time parameters are calibrated only on the non-missing early observations (ID check means 10.2 s / 12.6 s from the 9 and 7 recorded rows; belt time mean 28.6 s, range 5–68 s, n=29).
- The arrival rate observed in the 10-minute data window (~10.5 pax/min blended) is treated as the **over-capacity morning rush rate, not the all-day average** — this is exactly the non-representativeness the expert flagged. The model therefore uses a non-stationary arrival curve that peaks near the observed rate (7.5/min) on an off-peak base (2.5/min) instead of using the recorded rate as a constant (which would be the "extrapolate to unlogged hours" mistake).
- The 58-row window is treated as one busy-period burst; steady-state conclusions are drawn only for the peak window, not extrapolated to the day.

## Exchange 2 — Structural assumption: arrival process character

**Question** (expert_question_2.md): "Is one airport's checkpoint morning rush like a steady, even stream of passengers, or does it come in big groups?"

**Reply (key points)**: Neither — a **non-stationary, clustered (over-dispersed)** process: rate rises steeply into a morning peak and falls off (a window, not a constant); passengers arrive in **groups** — families, parties, banks released together from ticketing/baggage drop/shuttle, connecting-flight waves. A simple Poisson (steady, memoryless) arrival model will understate peak queues and wait-time variance.

**How the reply was turned into work**:
- Arrival process in `code/tsa_model.py` is `lambda(t) = base * (1 + 3*exp(-0.5*((t-t_peak)/1200)^2))` per minute (non-homogeneous exponential via thinning) **plus batch arrivals**: with probability `batch_p` an arrival is a bank of k passengers (k from a geometric tail, capped at 6, members within ~1 s). This directly encodes both the non-stationary peak and the over-dispersed clustering, replacing a homogeneous Poisson assumption.
- `batch_p` is a structural parameter varied in the cultural sensitivity analysis (part c): 0.15 (US-orderly), 0.25 (Swiss), 0.35 (China/group travel), 0.10 (slow solo traveler).
- Validation check: a homogeneous Poisson model under-states p90 wait relative to the batchy model; the batchy model is retained as the base case for all modification comparisons, so all comparisons are made under the same (expert-endorsed) arrival structure.

## Exchange 3 — Interpretation context / decision threshold

**Question** (expert_question_3.md): "How long is a passenger wait at a security line acceptable before most travelers start to complain?"

**Reply (key points)**: No hard threshold; empirical tolerance band: under ~10 min = normal; ~10–20 min = acceptable with mild grumbling, the range airports target, where published standards sit; ~20–30 min = complaints common, "long line" perception; beyond ~30 min = widespread dissatisfaction, missed flights, public/political issue (O'Hare 2016). TSA/airports treat **~10–15 min as target maximum** for regular lanes, **20 min** as the outer acceptable bound; Pre-Check expects a few minutes. Tolerance shifts with predictability: unpredictable waits are resented more than long-but-expected ones.

**How the reply was turned into work**:
- Decision thresholds set in the model as `TOL_TARGET = 15 min`, `TOL_OUTER = 20 min` (regular lanes), and Pre-Check target "a few minutes" (used as ~10 min in reporting).
- Every scenario result is reported against these thresholds (p50, p90, max vs 15/20 min), and the modification recommendations in `solution.json` are framed as: reach p90 ≤ 20 min for regular passengers and ≤ 10 min for Pre-Check at the morning peak.
- The predictability point drove a modeling choice: the variance (p50→p90 spread, max) is reported alongside the mean for every scenario, and Modification M3 (staffing flex at the peak, which removes the *unpredictable* part of the wait) is evaluated on both mean and spread.

## Note on scope discipline
No coding, debugging, computation, or derivation questions were asked; all three exchanges concerned real-world data practice, arrival behavior, and traveler tolerance only. Replies were used as parameter values/constraints and scenario-structure choices, never quoted into the submission.
