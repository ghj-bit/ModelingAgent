# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — MM-Bench 2017_D

Three fixed exchanges. Files: `logs/operator_feedback/expert_question_N.md`,
`expert_request_N.json`, `expert_reply_N.json` (N=1,2,3). Each reply was turned
into a concrete parameter, constraint, or change below.

## Exchange 1 — Causal mechanism / data-model consistency
**Question:** At a busy checkpoint, do the short ID-checks at the front keep
up, or is it the bag/passenger scanning behind that builds the long lines?

**Reply (gist):** ID check is *not* the bottleneck (short transaction, parallel
officers, high service rate). Queues build at and behind the screening lanes
(X-ray, millimeter-wave, secondary/pat-down). Two structural drivers: (a) one
X-ray lane serves a whole queue, and (b) the Pre-Check lane allocation — about
1 Pre-Check lane per 3 regular lanes despite ~45% Pre-Check enrollment —
concentrates demand on too few lanes. Variance, not just the mean, causes the
visible spikes (one flagged bag or pat-down stalls a lane).

**How the reply became work (not prose):**
- Set the model's bottleneck hypothesis to the downstream screening lane pool,
  not the ID stage. The ID stage was retained as a separate queue only to
  *verify* it is not the constraint.
- **Validation run (logs/validate.log):** ID stage utilization ρ≈0.23, mean
  wait ≈2 s at the calibrated arrival rate — confirmed *not* the bottleneck,
  matching the expert's claim. Screening pools are where ρ is high.
- Hard-coded the lane-structural driver: `LANES_PRE=1`, `LANES_REG=3`
  (1:3 ratio) and `PRE_SHARE=0.45` as base configuration, making the
  Pre-Check-pool overload (ρ≈1.77 vs regular ρ≈0.85) the model's central
  result (results/base.json).
- Secondary variance driver encoded as `P_SEC=0.10`, `T_SEC=90 s` per-lane
  delay, and swept (mod4) to test the "variance drives the spikes" claim.

## Exchange 2 — Operational constraints / boundary conditions
**Question:** When an extra officer is added to a slow scanning lane, does the
line shrink almost immediately, or take a while?

**Reply (gist):** Takes a while. The queue drains at (service rate − arrival
rate); near saturation that difference is small, so a 20–40 person backlog
(≈15–30 s each) takes minutes to tens of minutes to visibly clear. Arrivals
keep feeding during the drain, so the effect is a gradual decline, not a step.
Also, *where* the officer is added matters: if the true bottleneck is
downstream, adding staff at the lane entrance barely helps.

**How the reply became work:**
- Constrained the decision rule to *sustained* throughput, not instantaneous:
  the model reports **steady-state** (last 10 min) waits and long-horizon
  utilization, not the first-minute response. A modification is only credited
  if it lowers the steady-state ρ and steady-state wait, consistent with the
  "gradual drain over minutes–tens of minutes" dynamic.
- The "where you add matters" point is why the modifications target the
  *screening* pool (add Pre-Check lanes, speed the X-ray bag stage, cut
  secondary referrals) rather than adding ID-check officers — adding ID staff
  (ρ already 0.23) is shown to do essentially nothing to the line.
- Gave each simulation a full 1 h horizon with 8 independent seeds so the
  reported wait is a drained steady state, not a transient.

## Exchange 3 — Decision-relevant uncertainty threshold
**Question:** For a manager deciding between faster scanners and more staff,
how much difference in the average waiting line counts as "worth it"?

**Reply (gist):** No universal threshold. Roughly a 20–30 % reduction in
average wait is the smallest change passengers/managers actually notice;
below ~10 % it is lost in day-to-day noise. Absolute anchors matter at the
extremes (30→15 min is clearly worth it; 4→3 min usually not). Variance / the
worst-case tail (the wait that makes people miss flights) matters as much as
the mean. The real decision rule is cost per minute of wait saved, comparing
scanners vs staff on both the mean and the variance.

**How the reply became work:**
- Set the decision bar in the analysis: a modification is decision-relevant
  only if it cuts the **mean** wait by ≥20–30 % *or* materially cuts the
  **p95/p99 tail** (the missed-flight driver). Results are reported on both
  the blended mean wait and the blended p95/p99, not the mean alone.
- Framed the recommendation in the cost/wait-saved logic: the Pre-Check lane
  reallocation (a procedural/staffing change, near-zero capital) beats buying
  faster scanners on cost per minute saved, because it removes the dominant
  bottleneck (Pre-Check pool ρ>1.7) rather than incrementally speeding an
  already-adequate stage.
- Quantified: the recommended package cuts the blended mean wait by ~88 % and
  the p95 by ~82 % (both far above the 20–30 % notice bar), and brings both
  pools to ρ≈0.8 — i.e., a tail and a mean improvement simultaneously, which
  is the case the expert said is "clearly worth it."

---
No exchange was used for coding, debugging, or computation. All three replies
produced parameters/constraints/decision rules that are used in
`code/model.py`, `code/cultural.py`, and the numbers in
`results/*.json` and the submission.
