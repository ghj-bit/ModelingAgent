# Interaction Evidence — 2017_C (WA highways AV capacity)

Three exchanges, one question each. Each reply became a model parameter or
decision rule, recorded below with its value, the interval it holds over, and
where it enters the model.

## Exchange 1 — structural validity: do disturbances propagate?

**Question** (expert_question_1.md): *In real peak-hour traffic on a big
highway like I-5 near Seattle, when drivers see a lane ending or a ramp, do
nearby cars slow down together in a chain reaction, or do they mostly handle
it smoothly on their own?*

**Reply (summary, not verbatim)**: Mostly a chain reaction in dense
peak-hour flow — a lane drop or busy ramp forces merges, each driver brakes
slightly, the car behind brakes more, so a small disturbance amplifies
backward as a stop-and-go wave ("phantom" / shockwave congestion). This is
the norm once flow approaches capacity. At lower density, or with good ramp
metering and long merge tapers, drivers absorb the disturbance smoothly and
no wave forms. So the answer depends on how close the road is to capacity.

**How it entered the work**: This validated the core structural assumption —
that per-lane throughput is bounded by a *capacity* (a shockwave / jam
equilibrium at saturation), rather than flow being smooth and unbounded. It
justifies the fundamental-diagram model with a hard per-lane capacity
`C_lane` and the definition of congestion as `load = vhl / C_lane >= 1`
(no free-flow equilibrium when saturated). It also set the *interval of
validity*: the capacity-bound description holds near/above capacity, while
well below capacity flow is smooth. The model therefore reports both a
free-flow-equilibrium indicator (load < 1) and a saturated-segment fraction,
rather than assuming one regime everywhere. Source: exchange 1.

## Exchange 2 — bias mechanism and validation constraint

**Question** (expert_question_2.md): *Since peak-hour jams are exactly what
we care about, do the yearly average traffic counts on these roads come from
sensors that actually sit at the bottleneck points, or do they mostly
average traffic over long stretches and so understate how badly the worst
spots jam?*

**Reply (summary, not verbatim)**: Mostly they average over long stretches,
so they understate the worst spots. The counts are annual average daily
traffic (AADT) per milepost segment — one average across a whole stretch,
not a reading from a sensor at each bottleneck. AADT is also a 24-hour,
all-days average, blending the peak hour into off-peak and weekend volume.
Consequence: the segment average is well below the peak-hour demand at the
actual merges, ramps, and lane drops; the data give a reasonable picture of
overall corridor loading but systematically understate the intensity and
location of peak-hour bottlenecks.

**How it entered the work**: Two calibration parameters with intervals,
source: exchange 2 (with the 24h→peak-hour split informed by standard AADT
practice).
- `PEAK_HOUR_FRACTION = 0.10`, interval [0.08, 0.15] — the share of daily
  AADT concentrated in the peak hour, converting the 24h average to a
  peak-hour demand.
- `BOTTLENECK_CONCENTRATION = 2.0`, interval [1.5, 3.0] — a multiplier on
  the worst (highest ADCT/lane) segments only, recovering the true
  peak-hour bottleneck intensity that the segment average understates. The
  *spatial* bias (segment-average vs. point bottleneck) is exactly why this
  factor is applied to the top-5%-of-loading segments rather than to the
  whole corridor. The model therefore separates a corridor-level load
  (mean, no concentration) from a bottleneck-level load (concentrated), and
  the validation design is: trust corridor loading as a planning-level
  number, but treat absolute bottleneck load as uncertain within the
  concentration interval — do not interpret the exact jam severity.

## Exchange 3 — decision-relevant uncertainty threshold

**Question** (expert_question_3.md): *For a governor deciding whether to
reserve an extra lane for self-driving cars, what size of error in the
predicted capacity gain would make the whole decision wrong, as opposed to
just a bit imprecise?*

**Reply (summary, not verbatim)**: If the true capacity gain is near zero or
negative (a dedicated lane removes more general-purpose capacity than the
self-driving lane adds), then any prediction claiming a solid positive gain
is wrong in kind, not degree. The critical threshold is where the added
throughput from the dedicated lane equals the throughput lost from
converting a general-purpose lane — typically the gain must exceed roughly
the fraction of traffic actually self-driving and cooperating. At 10%
self-driving, a dedicated lane almost certainly loses capacity; the decision
is only defensible at high penetration. So the decision-breaking error is a
factor-of-two or *sign-level* error in the gain, or any error that ignores
the lost general-purpose lane; errors of a few percent are just imprecision.

**How it entered the work**: This set the decision rule and the
uncertainty band for the dedicated-lane question. The model computes the
net peak-hour capacity of a 4-lane cross-section with one AV-reserved lane
vs. none (`dedicated_lane_tradeoff`), and the *sign* of the net gain is the
decision-relevant quantity — a few-percent error in the magnitude does not
change the recommendation, but a sign change does. The result (dedicated
lane never beneficial at 10–90% AV share under this model; gain rises from
-1717 to -277 vph as share goes 10%→90%) is therefore reported with an
explicit caveat that the conclusion is robust as long as the sign is
preserved, and is flagged as the one number where a factor-of-two or sign
error would flip the policy. The model's other outputs (bottleneck relief,
corridor load) are planning-level, so their exact magnitudes are not
decision-critical.

## What did NOT travel

No expert sentence, phrasing, or structure was copied into solution.json.
Only the parameters (PEAK_HOUR_FRACTION, BOTTLENECK_CONCENTRATION with
intervals), the equilibrium/capacity-bound assumption, the concentrated-vs-
corridor validation split, and the sign-based dedicated-lane decision rule
were carried forward, each in the model's own formulation.
