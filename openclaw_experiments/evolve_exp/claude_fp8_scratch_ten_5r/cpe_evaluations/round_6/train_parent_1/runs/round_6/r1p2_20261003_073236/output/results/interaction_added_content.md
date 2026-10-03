# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — 2017_C (self-driving cars on Seattle freeways)

All exchanges are qualitative, single-question consultations with a traffic-domain
expert. Each reply is converted into a model parameter or rule before the next
question is asked. Exchange numbers N=1..10.

## N=1
**Q:** At rush hour on these Seattle freeways, is every lane usually full, or do
the left lanes often have space?
**Reply (summary):** Every lane ends up packed; demand exceeds capacity so
density is high across the full cross-section. Left-right differences exist but
do not leave lanes empty.
**Effect on work:** Congestion is measured by the aggregate volume-to-capacity
ratio rather than a single "bottleneck lane"; the fundamental-diagram baseline is
a uniform cross-section.

## N=2
**Q:** On a busy Seattle freeway, about what fraction of the day's total cars
pass during the morning rush hour?
**Reply (summary):** Peak hour alone ≈ 8–10% of daily traffic; the 3-hour morning
peak ≈ 20–25%. Empirical planning figures, not precise measurements.
**Effect on work:** Parameter `f_peak = 0.09` (interval [0.08, 0.10], source:
exchange N=2) converts daily AADT into peak-hour demand V_peak = f_peak · AADT.
Sensitivity swept at 0.08–0.10.

## N=3
**Q:** Roughly how many cars can a single busy freeway lane carry per hour
before it starts backing up?
**Reply (summary):** Standard planning capacity ≈ 1,800–2,000 veh/h/lane;
congestion sets in around 1,500–1,800. Empirical, not precise.
**Effect on work:** Parameter `c = 1900` veh/h/lane (interval [1800, 2000],
source: exchange N=3) sets the per-lane baseline capacity. Breakdown onset
treated at ≈ 1500–1800 vph/lane.

## N=4
**Q:** Compared with a human driver, can a coordinated self-driving car follow
another car at roughly half the usual gap distance?
**Reply (summary):** Yes, roughly — in coordinated platoons, gap can be about
halved (reaction time ~tens of ms vs 1–1.5 s). The gain shrinks at high speed
and when the lead car is human.
**Effect on work:** Parameter `k_avav = 0.5` (gap multiplier, i.e. 2× capacity,
interval [0.45, 0.6], source: exchange N=4) applies to an AV following another
AV.

## N=5
**Q:** When a self-driving car follows a human driver in traffic, does it still
gain from driving closer than usual?
**Reply (summary):** Yes but only partially — gap reduction is maybe a third to
a half of the normal gap (not the full halving), because the human lead's
braking forces a larger safety margin.
**Effect on work:** Parameter `k_avhu = 0.75` (interval [0.70, 0.85], i.e.
gap reduction of 1/3 to 1/2, source: exchange N=5) applies to an AV following a
human. Capacity multiplier = 1/k.

## N=6
**Q:** If one freeway lane were reserved for self-driving cars, would human
drivers still speed into the open lanes?
**Reply (summary):** Yes — compliance is imperfect and enforcement is hard; the
incentive to cheat rises exactly when congestion is worst. A dedicated lane is
not perfectly exclusive; expect a nonzero fraction of human vehicles in it,
eroding the benefit.
**Effect on work:** Dedicated-lane policy modeled with compliance factor
`eps = 0.15` (fraction of human demand encroaching, interval [0.10, 0.20],
source: exchange N=6) instead of a perfectly exclusive lane.

## N=7
**Q:** In a traffic jam, can self-driving cars safely drive faster than the
human traffic around them?
**Reply (summary):** No — constrained by the vehicle ahead. The advantage is
shorter reaction time and smoother braking (damps stop-and-go waves), not a
higher speed. Exceeding local flow needs a clear lane, which doesn't exist in
a jam.
**Effect on work:** The AV benefit enters as flow stabilization and headway
reduction, not as a speed boost. The model has no "AV speed premium" term;
equilibrium flow is bounded by the capacity envelope.

## N=8
**Q:** If only a few percent of cars were self-driving, would those cars
really form long smooth driving groups?
**Reply (summary):** No — platooning needs consecutive AVs in the same lane,
which is rare at low penetration. Long groups only begin at tens of percent and
become common at high share.
**Effect on work:** Platoon probability modeled as a function of penetration p:
P(two consecutive vehicles are both AV) = p² for the ideal mixing baseline, so
the platoon benefit scales super-linearly in p. This is the mechanism behind the
tipping point.

## N=9
**Q:** When a freeway runs at full capacity, does traffic settle into steady
slow flow, or keep surging and stopping?
**Reply (summary):** It keeps surging — flow at capacity is unstable; small
disturbances amplify into backward-propagating stop-and-go waves. Steady slow
flow can occur in some congested regimes, but the characteristic behavior at
capacity is oscillation (breakdown).
**Effect on work:** The fundamental diagram includes a breakdown/oscillation
regime above ~1500–1800 vph/lane where effective capacity drops. Equilibria:
free-flow equilibrium exists below breakdown; above it the system oscillates
(no stable steady state) until AV damping reduces the effective demand.

## N=10
**Q:** Roughly what share of self-driving cars would drivers need before the
stop-and-go traffic clearly eased?
**Reply (summary):** Roughly 30–50% penetration, with marked improvement around
40–50%. Below ~20–30% AVs are too sparse to form enough consecutive platoons,
so they only damp locally and the jam persists.
**Effect on work:** Sets the expected tipping-point location (t ≈ 0.3–0.5) that
the platoon-probability model is tuned to reproduce. The model's effective
capacity gain is calibrated so that the volume-to-capacity ratio crosses the
breakdown threshold for a representative over-capacity segment between 30% and
50% AV penetration.

---

## Parameter table (all expert-sourced)

| name | value | interval | source |
|---|---|---|---|
| f_peak (peak-hour share of daily volume) | 0.09 | [0.08, 0.10] | exchange N=2 |
| c (per-lane baseline capacity, veh/h/lane) | 1900 | [1800, 2000] | exchange N=3 |
| breakdown onset (veh/h/lane) | 1650 | [1500, 1800] | exchange N=3 |
| k_avav (gap multiplier, AV follows AV) | 0.50 | [0.45, 0.60] | exchange N=4 |
| k_avhu (gap multiplier, AV follows human) | 0.75 | [0.70, 0.85] | exchange N=5 |
| eps (human encroachment on dedicated lane) | 0.15 | [0.10, 0.20] | exchange N=6 |
| t_tip (tipping-point AV share) | 0.40 | [0.30, 0.50] | exchange N=10 |

Structural rules (no numeric value): uniform cross-section packing at peak
(N=1); no AV speed premium, benefit is damping + headway (N=7); platoon
probability ~ p² (N=8); at-capacity oscillation rather than steady slow flow
(N=9); dedicated lanes imperfectly exclusive (N=6).
