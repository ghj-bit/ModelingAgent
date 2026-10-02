# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence

Three expert exchanges, one question each, fixed budget. Each reply is recorded,
and the work it changed is stated (parameter / equation / rule + interval).

## Exchange 1
**Question** (to the expert): Do checked bags for a flight arrive at screening
together as one group, or spread out over time?

**Reply (verbatim)**: In real airport operations, checked bags for a flight do
**not** arrive at screening as one group. They arrive spread out over time, driven
by when each passenger checks in at the ticket counter or curbside. Key facts:
- Bags trickle in over the check-in window for a flight, typically starting ~2–3
  hours before departure for domestic flights and continuing until the check-in
  cutoff (~30–45 minutes before departure).
- Arrival is roughly a smoothed flow with a peak in the last hour before cutoff,
  not a single batch.
- Bags are also fed into a shared, centralized baggage handling system, so bags
  from many flights interleave at the EDS machines.
So for modeling, treat bag arrivals as a time-distributed stream (a rate over the
check-in window), not a single lump. The one exception is connecting/transfer
bags, which can arrive in bursts when an inbound flight lands.

**How the reply changed the work.** Converted to the arrival-structure assumption
of the whole throughput model:
- Bag arrivals are a **time-distributed stream**, not a per-flight batch. The EDS
  requirement is therefore set on the **peak arrival rate** (bags/min) rather than
  the total bag count. `code/model.py`: `peak_rate()` spreads the peak-hour total
  over the screenable span and multiplies by the peak concentration factor `PEF`
  to capture the last-hour peak.
- Interleaving of many flights' bags into a **shared/centralized** EDS pool:
  sizing uses one shared pool per airport (not per-flight dedicated devices), so
  `min_devices()` sizes a single pool against the airport-wide peak rate.
- Interval the statement holds over: domestic check-in window, ~2–3 h before
  departure to the cutoff; the peak-hour model uses the screenable sub-window
  (cutoff − transport lag).

## Exchange 2
**Question** (to the expert): In practice, about how long before departure must a
checked bag be on the plane, at latest?

**Reply (verbatim)**: For domestic flights, checked bags must typically be loaded
and the bag room closed about **30–45 minutes before scheduled departure**
(commonly cited as a 45-minute cutoff for checked bags at large U.S. airports).
International flights often require bags checked earlier, roughly **60 minutes**
before departure. So the practical latest point a checked bag can be processed and
still make the plane is on the order of **30–45 minutes before departure** for
domestic, up to ~60 minutes for international. This is an empirical operational
norm, not a fixed regulatory figure.

**How the reply changed the work.** Converted to the **deadline / transport-lag
constraint** that drives the schedule (Task 3) and the tolerable screening-delay
budget:
- `code/model.py`: `MIN_LAG = 30.0` min (lower end of the 30–45 min domestic
  window, the most conservative value) is the latest a bag may still be in the
  pipeline; the screenable span is `PEAK_HR − MIN_LAG`.
- `MAX_ETA = 6.0` min max tolerable screening wait: the 30–45 min cutoff minus the
  ~30 min transport lag leaves only a few minutes of screening slack, so the
  design must keep 90th-percentile screening ETA small. This is the constraint
  checked by `schedule()`'s per-flight `slack_min`.
- Interval: domestic 30–45 min (model uses 30 min); international ~60 min (noted;
  both airports' Table-1 flights are treated as domestic).

## Exchange 3
**Question** (to the expert): In practice, which hurts airports more — a bag
wrongly flagged as a bomb, or a bomb bag passing through?

**Reply (verbatim)**: A bomb bag passing through hurts far more. A false alarm is
a cost and delay problem; a missed bomb is a catastrophic safety and mission
failure. Concretely:
- False positive (bag wrongly flagged): triggers secondary inspection, delays that
  bag and possibly the flight, consumes screener/ETD labor, and erodes passenger
  tolerance. Costly and disruptive, but bounded and recoverable.
- False negative (bomb passes): the entire purpose of the screening system fails.
  Potential mass casualties, aircraft loss, and collapse of public confidence in
  the mandate.
This asymmetry is why screening systems are tuned to keep the false-negative rate
extremely low, accepting a higher false-positive rate as the price. In practice,
EDS false-alarm rates are high enough that most flagged bags are cleared by
secondary inspection — airports tolerate that because the alternative failure is
unacceptable. So the design objective is: minimize missed threats first, then
manage false alarms to keep throughput and delays workable.

**How the reply changed the work.** Converted to the **lexicographic design
objective** of the detection analysis (Tasks 6 & 7):
- `code/sensitivity.py` orders its outputs **miss rate first, false-alarm/
  throughput second**. The ETS/EDS+ETD comparison is driven by the false-negative
  (missed-threat) reduction, not by cost.
- The ETD add-on is justified primarily by the ~10× reduction in miss rate
  (`miss_per_bag_eds_only` vs `miss_per_bag_eds_etd`), consistent with "minimize
  missed threats first."
- The recommendation to add ETD rather than replace EDS follows from this: ETS
  still carries the bulk of throughput and the first-detection role; ETD is the
  low-miss-rate layer on the high-risk 20%.
- Interval: applies to the whole screening objective function, both airports, all
  of Tasks 6 and 7.
