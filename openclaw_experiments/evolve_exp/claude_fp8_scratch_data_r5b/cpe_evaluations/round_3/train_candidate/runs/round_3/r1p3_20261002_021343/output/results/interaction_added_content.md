# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — MM-Bench 2003_C

Three expert exchanges, one qualitative question each, in order. Each reply was
converted into a model constraint before the next exchange. No expert sentence is
reproduced in solution.json; only the values, constraints, and equations derived
from the replies appear there.

## Exchange 1 — Data-model structural fit
- **Question:** When checked bags are scanned in a peak-hour queue, which is worse:
  a bag waiting 30 minutes in the bag, or a passenger waiting 30 minutes at the counter?
- **Expert reply (gist):** Neither is worse in a security sense — a queued bag is not
  being screened, so a 30-minute wait is 30 minutes of unscreened exposure regardless of
  where it is measured. The two are the *same delay* measured at different points. The
  binding constraint is screening throughput (160–210 bags/hr per EDS).
- **Converted to model (value/constraint + interval):** Queue wait time ≡ screening
  time; the queue length is the symptom, throughput is the binding resource. Therefore
  capacity is sized by *throughput* (bags screened per hour ≥ bags arriving per hour),
  not by passenger comfort, and the queue is the correct state variable. This holds over
  the full peak hour and across all device utilizations in the problem's stated ranges
  (EDS 160–210 bags/hr, ETD 40–50 bags/hr). Used in `model.py` as the basis of the
  drain-within-peak sizing rule and the interleave schedule.

## Exchange 2 — Dominant bias / selection mechanism
- **Question:** Besides screening capacity, what real-world factor most often blows a
  peak-hour airport schedule apart?
- **Expert reply (gist):** Weather (convective storms, low ceilings/fog) — it collapses
  regional runway/departure capacity, triggers ground stops and holding — second is
  network propagation of delay (a late inbound aircraft or crew removes the flight from
  the peak hour entirely). Both reach the airport via ATC flow control. For the model,
  the peak-hour flight list is a **nominal** schedule, not a guaranteed one; the 2%
  daily cancellation is a small, steady-state version of the same disruption.
- **Converted to model (value/constraint + interval):** The Table-1 flight counts are
  treated as a *nominal* (unrealized-at-full) schedule. A disruption slack is applied to
  peak-hour demand: `bags_demand = bags × (1 + SLACK)`, SLACK = 0.10, and the 2% daily
  cancellation from the Table-1 note is carried as `DAILY_CANCEL = 0.02`. Interval: the
  slack is a planning buffer over the peak hour, robust to the weather/network
  disruption mechanism the expert named; it does not depend on a specific storm. This
  raises the EDS requirement from the raw-bags count (so the queue does not grow when a
  block of flights is pushed into the hour).

## Exchange 3 — Validation / interpretation criterion
- **Question:** In practice, when would an airport say screening capacity is finally
  acceptable, and what sign of a bad day would trigger a fix?
- **Expert reply (gist):** Acceptable = in the peak hour the bag queue does not grow —
  the EDS line clears bags at least as fast as they arrive, the last bag is screened
  before the peak ends, and no bag waits long enough to miss its flight. The practical
  test is a *stable or shrinking* queue, not a zero queue. Trigger for a fix = a queue
  that grows through the peak hour and does not drain afterward, or bags missing flights
  because screening (not the airline) was the constraint.
- **Converted to model (value/constraint + interval):** The sizing rule is
  `units ≥ ceil(bags_demand / (rate_per_unit × 1 hr))` so that
  `units × rate ≥ bags_demand` — i.e. the queue drains within the peak hour (stable or
  shrinking, not necessarily zero). This is the acceptance criterion used to choose the
  integer device counts, and the "grows through the peak and does not drain" condition
  is the trigger that says *add a device or shift the schedule*. Interval: applies to the
  single peak hour with a 45-minute screen-before-departure lead time; the last bag of
  the peak must be screened before the peak ends.

## How the three constrain the model (summary)
1. **State variable = queue; constraint = throughput.** (exch. 1)
2. **Demand = nominal × (1+0.10 slack) + 2% cancellation carried.** (exch. 2)
3. **Sizing rule = drain-within-peak (stable/shrinking queue, not zero).** (exch. 3)

These are the three structural decisions the exchanges resolved. All device specs
(EDS/ETD rate, accuracy, uptime, cost, the 20% ETD subset, 10× ETD labor) come from the
problem statement, not from an exchange.
