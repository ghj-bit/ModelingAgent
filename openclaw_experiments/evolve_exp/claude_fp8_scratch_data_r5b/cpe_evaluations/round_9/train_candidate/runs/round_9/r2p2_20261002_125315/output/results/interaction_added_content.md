# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — 2017_C

Three fixed exchanges, one question each. Files: `logs/operator_feedback/expert_question_N.md`,
`expert_request_N.json`, `expert_reply_N.json`. This file records what the expert said and,
critically, *how each reply was turned into work* (a parameter, a constraint, an equation,
a test, or a decision rule) rather than prose about what the expert meant.

## Exchange 1 — structural validity: steady flow vs. stop-and-go

**Question (expert_question_1.md):** "On a congested Seattle freeway peak-hour, does traffic
stop and go (rolling stop-and-go waves) most of the time, or does it mostly keep moving
slowly but steadily?"

**Expert reply (summary):** On these routes at peak, traffic is **mostly stop-and-go** —
repeated acceleration/deceleration ("phantom") waves propagating backward once demand exceeds
capacity. Smooth slow-but-steady crawling occurs mainly in transitional / moderately congested
conditions, **not** in the fully congested peak regime.

**Turned into work:**
- **Constraint on the base model:** a naive steady pipe (capacity = lanes × per-lane rate at
  free flow) would **overstate** usable capacity on the saturated segments, because sustained
  peak flow is degraded by stop-and-go. So the model applies a *congestion penalty*
  `η(V/C) ≤ 1` to usable throughput that is 1 at low volume and falls to a floor `η_min` as
  `V/C → 1`. Parameter `η_min` = 0.80 (sensitivity 0.70–0.85): a ~15–30% effective-throughput
  loss at saturation, consistent with the expert's stop-and-go regime. Source: Exchange 1.
- **AV benefit reframed:** the capacity gain from cooperating cars is modeled primarily as
  **damping of the stop-and-go penalty** (shorter, more stable headways keep flow stable),
  which is exactly the regime the expert identified as the dominant failure mode. This keeps
  the AV benefit physically consistent with the congestion structure rather than a free
  multiplier on an over-optimistic base.

## Exchange 2 — bias mechanism and validation

**Question (expert_question_2.md):** "On the same freeway, do the extra delays from a
congestion 'toll' (like the SR 520) and the stop-and-go waves make the traffic data you
gather look like there are more problems than are really there?"

**Expert reply (summary):** **No** net exaggeration. AADT counts are vehicle counts, not
problem counts; congestion *suppresses* latent demand (trips not taken / shifted), so the
data **understate** true demand. The **SR 520 toll** suppresses demand on that facility and
diverts it to the untolled parallels (I-90, I-405), so the **tolled route's counts look better
than the true travel demand warrants** and the parallel untolled routes look worse. The
distortion is in **where** the problem appears, not the total.

**Turned into work:**
- **Bias treatment applied in `model.py` (flag `--tolled 520`):** SR 520's low V/C is read as
  *partly demand-suppressed by the toll*, not as genuine spare capacity. The model therefore
  does **not** use SR 520's low congestion as evidence that AVs help it least; and it does not
  credit SR 520's apparent headroom in any network "spare capacity" tally.
- **Validation framing:** the tolled vs. untolled comparison is the model's built-in robustness
  check — a result that depended on SR 520 looking healthy would be flagged as a possible
  toll artifact. Confirmed the model's per-route conclusions do not hinge on SR 520's
  suppressed counts (its AAVT gain is computed, but the *interpretation* discounts it).

## Exchange 3 — decision-relevant threshold

**Question (expert_question_3.md):** "For deciding whether to dedicate a lane to self-driving
cars, how much faster must those cars make the road run (say, a few percent more cars
passing) before that gain is big enough to be worth taking a lane away from other drivers?"

**Expert reply (summary):** A dedicated lane pays off only if the throughput gain on the
remaining general-purpose lanes **more than offsets the capacity removed**. Removing one of
three lanes removes ~a third of general-purpose capacity, so the AV lane plus induced
efficiency must recover **on the order of tens of percent** of total facility throughput —
**not a few percent** — to break even. The crossover is sensitive to how many lanes remain;
high AV share + strong platooning are required.

**Turned into work:**
- **Decision rule (hard threshold) in `model.py`:** dedicate a lane **only if** the net
  facility capacity gain `ΔQ_net = (Q_dedicated − Q_baseline) / Q_baseline ≥ 20%` (the
  "tens of percent" bar; sensitivity 10–30%). A "few percent" gain never triggers the rule.
- **Parameter `Q_gain_threshold` = 0.20**, interval [0.10, 0.30], source: Exchange 3.
- This makes the dedicated-lane answer **quantitative and conservative**: at 10% AV the net
  gain is far below the bar (no lane), and the model reports the AV share at which a
  dedicated lane first clears the threshold.
