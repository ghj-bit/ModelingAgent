# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — Task 2003_C (EDS/ETD screening capacity, Airports A & B)

Three exchanges, one question each, exactly as the policy requires.

## Exchange 1 — input structure (arrivals)

- **Question (expert_question_1.md):** During the peak departure hour, do checked
  bags arrive at the screening line steadily, or in bursts that follow each
  flight's check-in cutoff?
- **Reply (expert_reply_1.json):** Arrivals are in bursts, not a steady stream.
  For a given departure most bags arrive over roughly 30–60 minutes before the
  flight's cutoff, with a pronounced spike in the final 10–15 minutes. Across the
  peak hour the line sees overlapping bursts; the mix of flight types and
  staggered departure times smooths the aggregate into a lumpy (not uniform)
  curve; connecting/curbside arrivals are less tightly coupled. Stated as an
  empirical judgment: treat arrivals as a non-stationary, peaked process keyed
  to departure times, not a constant rate.
- **How it entered the work:**
  - Replaced a uniform arrival assumption with a peaked, non-stationary arrival
    process in the queue simulation (model.py, `simulate` + per-airport arrival
    profile): bags for a departure spread over the 45–105 minutes before
    departure, weighted toward the cutoff, with departures staggered within the
    hour; profile is seat-weighted per flight type.
  - Parameter interval supported by the reply: arrival window 30–60 min before
    cutoff with a late spike; modeled as a tent over 45–105 min before
    departure (cutoff 45 min). Holds for the peak hour of a large airport with
    staggered departures.
  - The burstiness justifies reserving capacity slack (15%) instead of sizing
    machines exactly to mean demand.

## Exchange 2 — dominant driver (what the failure actually costs)

- **Question (expert_question_2.md):** When the screening line can't keep up with
  a burst of bags, what actually hurts the airline the most?
- **Reply (expert_reply_2.json):** The missed departure. A bag that misses its
  flight forces the airline to hold the aircraft (delaying everyone, cascading
  through rotations) or to pull the bag and re-route it. The pulled-bag case is
  the lesser operational evil but the worse cost/security outcome, and an
  unscreened or late-screened bag is a chain-of-custody gap security cannot
  tolerate. The binding pain is bags failing to clear screening before the
  flight's cutoff — which is why scheduling matters as much as machine count.
- **How it entered the work:**
  - Set the binding service constraint: every bag must clear screening by its
    flight's cutoff; model the objective as minimizing bags that would be late
    relative to cutoff (queue build in `simulate` measured against the
    30-minutes-before-departure clear-by lag, `LAG_MIN = 30`).
  - Changed Task 3 from "spread departures evenly" to a schedule that (a)
    staggers departures so concurrent bursts do not coincide, and (b) departs
    the largest flights (biggest cutoff bursts) early, giving their bags the
    longest clear-by margin. Schedule produced in model.py, `schedule()`.
  - No model structure was put to the expert; only the real-world consequence.

## Exchange 3 — decision-relevant threshold

- **Question (expert_question_3.md):** How many unscreened or late bags in a
  peak hour is too many before an airport must add screening machines?
- **Reply (expert_reply_3.json):** No defensible numeric count. Under a 100%
  screening mandate the acceptable number of unscreened bags reaching an aircraft
  is zero; any late bag is a chain-of-custody failure. What triggers adding
  machines is a chosen service-level target — e.g. treating even 1–2% of
  peak-hour bags failing to clear in time as unacceptable (empirical judgment,
  not a precise figure).
- **How it entered the work:**
  - Machine-count rule in model.py, `n_devices`: size devices so peak-hour
    demand stays at/below (1 − slack) of effective capacity, i.e. a
    service-level formulation (near-zero late bags) rather than a fixed
    late-bag count.
  - Fixed slack = 0.15 as the operationalization of the "near-zero missed
    bags / 1–2% is already unacceptable" service level: with 15% capacity
    headroom the simulated peak queue in the base case reaches at most ~18% of
    one hour's arrivals and drains before the cutoff lag is consumed, and the
    fraction of bags at risk stays far below the 1–2% level the expert flagged
    as unacceptable. Interval: service level valid for a 100% mandate
    environment; if the mandate relaxes, slack can shrink.

## Provenance summary

- Exchange 1 → arrival-process shape and window (30–60 min pre-cutoff, late
  spike); non-stationary peaked arrivals; smoothed aggregate.
- Exchange 2 → cutoff-clearing as the binding constraint; schedule ordering rule
  (largest flights early, staggered).
- Exchange 3 → service-level machine-count rule; slack 0.15 calibrated to the
  "1–2% late is unacceptable" judgment; zero tolerated unscreened bags under
  the mandate.
