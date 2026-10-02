# Expert Interaction Evidence — Task 2017_C (MM-Bench traffic / AV capacity model)

## Exchange 1 (structural validity: capacity curve shape)

**Question (expert_question_1.md):** Does slowdown on a freeway like I-5 near
Seattle build gradually as volume approaches lane capacity, or flip abruptly
into stop-and-go?

**Reply (expert_reply_1.json, verbatim):** Abruptly. "Freeway flow is not a
smooth function of volume near capacity — it exhibits a capacity
discontinuity." Flow holds a stable synchronized regime, then flips within
minutes into stop-and-go once a perturbation (lane change, merge, brake tap)
pushes density past a critical point. Recovery is hysteresic: flow does not
return to free flow at the volume that triggered breakdown; demand must drop
well below it. Practical signature: 55–65 mph moderate spacing, then a
backward-moving shockwave of brake lights (propagates upstream ~10–15 mph)
carried by repeated stop-and-go pulses. Triggered locally (on-ramps, merges,
bottlenecks), spreads upstream. Flip typically occurs when volume reaches
roughly 90–100% of design capacity for that segment; the trigger is a
perturbation, not the volume level alone.

**How the reply became work:**
- The macroscopic fundamental diagram (MFD) in `model.py` is specified as a
  smooth S-shaped flow-density curve whose congested branch crosses the
  demand line up to three times, giving three equilibria (free,
  metastable, congested) and a saddle-node point that IS the tipping point
  asked for in the problem. This directly encodes the reported capacity
  discontinuity; a simple parabola (Greenshields) with one equilibrium was
  rejected as structurally invalid for these roads.
- Hysteresis is modeled by a hysteresis coefficient H (congested-branch
  capacity multiplier, base H = 0.85): the congested-branch maximum is
  0.85 x capacity, so re-stabilization needs demand to fall below
  ~0.85 x capacity, not the breakdown level.
- The critical-density (breakdown) fraction of free-flow density is set to
  d_crit = 0.92, in the 90–100%-of-capacity band the expert reported; the
  tipping point is reported in units of both density and volume ratio.
- The upstream shockwave speed (~10–15 mph, backward) is recorded as
  context for the congestion-propagation limitation, not a fitted
  parameter (no time-series data in the dataset to calibrate it).

## Exchange 2 (bias mechanism: suppressed demand in daily counts)

**Question (expert_question_2.md):** Since daily counts only record vehicles
that completed the trip, what main way does the daily count misstate how
congested the highway is on a bad day?

**Reply (expert_reply_2.json, verbatim):** It understates congestion because
it counts only completed trips, so it misses suppressed and diverted demand.
On a bad day, some drivers don't travel at all, shift to other routes or
times, or abandon trips — those vehicles never appear in the count. The
count reflects the traffic the road *carried*, not the demand that *wanted*
to use it. A segment can show a moderate daily count while actually being at
or beyond capacity during peak hours, because the peak is where the unmet
demand is hidden. Daily averages also smear the peak: a few hours of
stop-and-go averaged against many free-flow hours look far less severe than
the worst-hour experience.

**How the reply became work:**
- The model's demand input is the PEAK-HOUR flow, not the daily count:
  q_peak = ADT x peak-factor PF / 24, with PF = 11.0 (planning-level
  highway peak-hour factor, interval [10, 12]), retrieved via the search
  helper (step 5 of the workflow) and listed in the solution's parameter
  table. This is the correction for the "daily average smears the peak"
  mechanism.
- Because daily counts count only carried (completed) trips, the model
  reports equilibrium and tipping points in terms of *potential* demand,
  and flags every segment whose carried peak flow already sits within
  ~10% of capacity as one where true (unsuppressed) demand is likely at or
  beyond capacity — i.e., where the tipping point has effectively already
  been reached on peak days. This bias direction (understatement) is stated
  explicitly as a limitation in subtask_outcome_analysis, and no
  performance metric is claimed from the daily data alone: validation
  would require peak-hour measurements or loop-detector time series,
  which the dataset does not contain (temporal/spatial holdout
  impossible on this data; stated as a bias-analysis limitation).

## Exchange 3 (decision threshold: dedicated-lane condition)

**Question (expert_question_3.md):** If a planning study forecasts that
self-driving cars would raise a highway's usable capacity by, say, 15%, how
large must that estimate be for the state to commit to reserving a lane for
them?

**Reply (expert_reply_3.json, verbatim, condensed):** No fixed threshold —
the decision is not driven by the capacity gain alone. Reserving a lane
removes ~1/N of the road's capacity for general traffic (~25% on a 4-lane
segment, ~33% on a 3-lane), so the self-driving capacity gain must exceed
that loss AND the self-driving share must be high enough to fill the
dedicated lane. A 15% gain is generally not enough to justify a dedicated
lane at low adoption (10–50%). Dedication typically only becomes defensible
at high penetration — empirically somewhere around 70–90% self-driving
share. At a 15% gain, the condition is unlikely to hold below roughly 70%
adoption.

**How the reply became work:**
- The dedicated-lane decision rule in `model.py` is a net-benefit test, not
  a fixed capacity-gain threshold: a lane is dedicated only if
  (a) the AV capacity gain g (fraction, base 0.15) exceeds the fractional
  lane loss 1/N for the remaining general-traffic lanes, and
  (b) the AV share p is high enough to fill it, with the defensible
  adoption range taken as p >= 0.70 (interval [0.70, 0.90] per the reply;
  the rule is evaluated at p = 0.90, the highest share in the problem).
  The model's own numbers are then checked against this: the
  net-benefit calculation at p in {0.10, 0.50, 0.90} is reported per
  route, and the dedicated-lane recommendation is only asserted where the
  net-benefit test AND the p >= 0.70 condition both hold.
- Because the problem only asks about p = 10/50/90%, the model evaluates
  the rule at exactly those shares, and reports that at p = 0.90 the
  condition can hold on the segments with the largest AV gain and smallest
  remaining-lane penalty, while at p = 0.10 and 0.50 no dedicated lane is
  justified (gain < lane loss, or lane under-filled).
