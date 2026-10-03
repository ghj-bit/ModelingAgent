# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — Problem 2003_C (EDS/ETD peak-hour screening)

Policy: mechanism → constraint → parameter, 10 fixed exchanges. Every reply below was
converted into a model input (parameter table in `solution.json` → Task 1) or a model
equation (effective throughput, redundancy rule, serial ETD queue, schedule window).

## Exchange 1 — bags per passenger
- **Q:** "In practice, roughly how many checked bags per passenger do you see on domestic flights at these airports?"
- **A:** ~0.6–0.8, commonly modeled as 0.7; empirical range 0.5–1.0.
- **Work:** `bags_per_pax = 0.7, interval [0.5, 1.0], source: exchange 1` — multiplies checked passengers to get bag volume; swept 0.5–1.0.

## Exchange 2 — checked-bag share of passengers
- **Q:** "During a busy hour, does nearly every passenger board with checked bags, or is a fair share carry-on only?"
- **A:** only ~60–70% check at least one bag; rest carry-on only.
- **Work:** `checked_rate = 0.65, interval [0.6, 0.7], source: exchange 2` — first factor in bags/hour; swept 0.60/0.70.

## Exchange 3 — check-in timing vs departure
- **Q:** "How far before a domestic flight's scheduled departure do passengers normally finish checking bags?"
- **A:** cutoff 30–45 min pre-departure; most bags tendered 60–120 min out, peaking 60–90 min out.
- **Work:** defines the Task 3 screening window: bags for a departure slot must clear EDS by t−35 min (mid of 30–45), i.e. screening must finish ~35 min before each slot; arrival concentration at 60–90 min out justifies treating the peak hour as the binding interval; `cutoff_min = 35, interval [30, 45], source: exchange 3`.

## Exchange 4 — operating hours / staffing
- **Q:** "Do EDS screening lanes run around the clock, and how many shifts do airports typically staff them?"
- **A:** not round-the-clock; staffed to match departures; peak hour fully staffed; constraint is per-lane throughput in that hour.
- **Work:** model scoped to the fully-staffed peak hour (no 24-h capacity credit); no night staffing assumed.

## Exchange 5 — re-scan behavior
- **Q:** "When a scanned bag is uncertain, is it re-scanned, and how often does that happen?"
- **A:** routine; ~10–30% of bags re-scanned/secondary-handled; practical planning allowance 10–20% throughput reduction.
- **Work:** effective rate `r_eff = r_rated × uptime / (1 + rescan_frac)`; `rescan_frac = 0.15, interval [0.10, 0.20], source: exchange 5` — applied to both EDS (185 → ~148 bags/h) and ETD (45 → ~38 bags/h); swept 0.10/0.20.

## Exchange 6 — cost of missed bags
- **Q:** "If some bags still couldn't be screened by the deadline, what's actually at stake for that flight?"
- **A:** unscreened bag cannot legally fly: offload + passenger travel without bag, or departure delay cascading to crew; no "skip" option.
- **Work:** binary feasibility constraint in scheduling: every bag of every peak-hour flight must clear by its cutoff; sizing rule becomes "zero missed bags in peak hour", and the Task 4 recommendation (delays/offloads only if N below the computed N).

## Exchange 7 — ETD queue effect of the 20% double screen
- **Q:** "If only about a fifth of passengers' checked bags needed the extra trace-detection step, what would that do to the queue?"
- **A:** adds 20% of bag volume to a far slower (40–50/h) serial lane; ETD is the bottleneck and dominates waits unless sized to the 20% peak flow.
- **Work:** serial EDS→ETD model: ETD demand = 0.20 × bags/hour; ETD count computed independently from the ETD effective rate; conclusion ETD, not EDS, is the binding constraint — drives Task 6 "schedules need no change if ETDs provisioned at the 20% ceiling" and the redundancy argument.

## Exchange 8 — fixed vs risk-based 20%
- **Q:** "Is the 20% double-screened share a fixed fraction of all passengers, or picked based on risk?"
- **A:** risk-based; 20% is an upper bound that *may* be applied, not a quota.
- **Work:** 20% modeled as a planning ceiling (base case), with 10% as a lower scenario; cost/benefit in Task 6 computed at the ceiling and flagged as conservative.

## Exchange 9 — machine counts at large airports
- **Q:** "How many EDS scanners does a large airport usually spread across its terminals and bag belts?"
- **A:** ~10–40 total, a handful (3–8) per terminal/belt; scales with bag volume.
- **Work:** plausibility check: computed 16/17 EDS at A/B (each ≈ one machine per 2–3 bag belts) sits at the low end of the stated 10–40 range for the region's two largest airports — consistent, no correction.

## Exchange 10 — absorbing a mid-peak failure
- **Q:** "If one scanner broke down mid-peak hour, how would operations normally absorb that lost capacity?"
- **A:** re-route to adjacent lanes; airports plan redundancy/spare capacity; if no slack, delays or offloads follow.
- **Work:** redundancy rule: N chosen so N−1 machines still cover peak demand (`required_machines` with redundancy=1 in `code/model.py`); this is the +1 over the bare ceiling and underlies the Task 4/Task 6 "keep one spare" recommendation and Task 7 reliability sensitivity.
