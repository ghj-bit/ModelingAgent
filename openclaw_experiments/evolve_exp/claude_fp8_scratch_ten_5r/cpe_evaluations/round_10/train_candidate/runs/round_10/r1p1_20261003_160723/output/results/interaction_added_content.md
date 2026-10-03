# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — Task 2003_C (EDS/ETD screening, Airports A & B)

Ten exchanges, one question each, mechanism → constraint → parameter order.
Every reply was converted into a model input before the next exchange; values
and intervals below are what the model uses (parameter table in
`results/model_results.json` → `parameters`, and in each task's
`mathematical_modeling_process` in `solution.json`).

## Exchange 1 — bags per passenger (structural/parameter: demand driver)
- **Q:** In practice, about how many checked bags does each passenger at a large U.S. airport carry?
- **A (summary):** ~1.0–1.3 on average at a large U.S. airport (0.8–1.0 domestic leisure, 1.3–1.6 long-haul); common planning figure ≈ 1.2; empirical judgment.
- **Effect on work:** Set demand model `bags/hr = seats × 1.2`, interval [1.0, 1.6]. Sweep `BPP=1.0,1.2,1.4` executed: EDS count moves 33/35 → 39/41 → 45/48 (A/B), i.e. ±25% in bags/passenger moves the fleet by ∓/+15%. Value used: 1.2.

## Exchange 2 — peak drop-line wait (constraint: queue behavior)
- **Q:** With ~1.2 bags per passenger, how long do passengers typically wait in the checked-bag drop line at a busy large airport?
- **A (summary):** ~10–20 min at peak, 5–10 off-peak, 30+ during surges; empirical judgment.
- **Effect on work:** Wait is the service-level output of the schedule. Model reports expected wait per schedule; base case flat load is well under capacity, so expected wait ≈ 5–15 min, consistent with the observed 10–20 min peak band. Interval [10, 20] recorded; used as service-level reference in Task 3/4 interpretation.

## Exchange 3 — minimum pre-departure window (constraint: hard deadline)
- **Q:** With screening lanes added at bag drop, how many minutes before departure do passengers generally need at minimum to avoid missing their flight?
- **A (summary):** ~45–60 min at bag drop/screening to reliably make the flight (airline bag cutoffs commonly 45 domestic / 60 international); 30–45 min only off-peak and risky; empirical judgment.
- **Effect on work:** Cutoff parameter `c = 45 min` (interval [45, 60]). A flight departing at minute d of the peak hour must finish screening by d − 45. Drives the bag-availability window in Task 3 and the feasibility rule in Task 6 (no schedule change needed because ETD lanes are parallel and utilised < 100%).

## Exchange 4 — departure concentration (parameter: intra-hour shape)
- **Q:** For the peak hour at a large airport, what share of the hour's flight departures is concentrated in the busiest 15 minutes?
- **A (summary):** ~30–40% of departures in the busiest 15 min (uniform = 25%); up to 40–45% at strongly banked hubs; empirical judgment.
- **Effect on work:** 15-minute concentration bound `k = 0.35` (interval [0.30, 0.45]) is the Task 3 feasibility criterion: scheduled load in any 15 min ≤ 35% of the hour's bags. Evenly spread departures give 25%, so the schedule passes with margin. Sweep `PEAK_FRAC=0.30,0.35,0.40` shows the EDS count is insensitive to it (39/41 in all three) — only the schedule feasibility depends on it.

## Exchange 5 — downtime load handling (mechanism: failure behavior)
- **Q:** When an EDS machine breaks down, how is its screening load typically handled?
- **A (summary):** Remaining units absorb the load at higher throughput (up to ~210 bags/hr) with brief queuing; if redundancy is insufficient, fallback is manual/alternative (hand search or ETD), never unscreened bags because 100% screening is mandated; airports size counts with spare capacity so one failure does not shut a lane; operational judgment.
- **Effect on work:** Failure mode = capacity loss of one unit, absorbed by spares + short-term queue. This is the mechanism the redundancy parameter calibrates; it also motivates the ETD fallback role in Task 6 (ETD as secondary/fallback layer, not primary).

## Exchange 6 — spare capacity rule (parameter: redundancy)
- **Q:** In practice, how many EDS units do large airports typically keep as spare capacity so one breakdown doesn't stop screening?
- **A (summary):** N+1 practice — one extra unit beyond peak demand, i.e. ~10–15% spare, usually one unit, occasionally two; operational judgment.
- **Effect on work:** Redundancy rule `n_final = ceil(bags/hr / (185 × 0.92)) + 1` (interval [1, 2] spares). A: 38 + 1 = **39 EDS**; B: 40 + 1 = **41 EDS**. Sweep `REDUND=0,1,2` executed: 38/40, 39/41, 40/42. Value used: 1 spare.

## Exchange 7 — airline cost preference (constraint: objective weighting)
- **Q:** When a passenger with checked bags is delayed, what is the typical cost airlines prefer to avoid?
- **A (summary):** Dominant cost is misconnect/downstream disruption, not passenger inconvenience: missed-flight rebooking/reaccommodation ~$200–500 domestic per passenger; departure delay propagation ~tens to low-hundreds $/min per aircraft; bag mishandling ~$100–300 per bag; empirical judgments.
- **Effect on work:** Task 4 cost basis: misconnect cost $350/pax [200, 500], block-delay $150/min [50, 300], bag delay $200/bag [100, 300]. Recommendation: hold departure (costs ~$150/min ≈ $9k for 60 min) is cheaper than letting a bank of large aircraft's passengers misconnect (142-seat × 19 flights ≈ 2,700 pax at peak for A alone; a 10% misconnect would be ~$945k) — supports screening-first, minimal-hold scheduling and the N+1 EDS spare.

## Exchange 8 — screening horizon (mechanism: backlog structure)
- **Q:** How many days of screening demand do large airports typically hold checked bags for before they must be cleared?
- **A (summary):** No multi-day backlog; every bag must be screened before loading, within the 1–2 h before departure; practical hold horizon is hours, not days; operational judgment.
- **Effect on work:** No backlog term in the model (capacity matched per hour, not per day). Screening lead time `L = 90 min` (interval [60, 120]) defines the bag-availability window [d − 90, d − 45] in Task 3. Sweep `LEAD=60,90,120` executed: EDS count unchanged (39/41); longer lead only lowers in-hour load flatness, never raises it.

## Exchange 9 — ETD advantage (constraint: technology role)
- **Q:** In the EDS vs ETD debate, what do airport security operators say is the main practical advantage of ETD?
- **A (summary):** Flexibility/footprint — small $45k portable unit deployable where 8-ton EDS cannot; secondary value is higher accuracy (99.7% vs 98.5%) and reliability (98% vs 92%) as a confirmatory layer for the high-risk subset; low throughput (40–50 vs 160–210) and ~10× labor cost make it a complement, not a replacement; operational judgment.
- **Effect on work:** Task 6 architecture: ETD screens only the 20% dual-screened subset in parallel lanes (29 + 1 = **30 ETD at A**, 31 + 1 = **32 ETD at B**); EDS fleet unchanged; ETD must not replace EDS (throughput gap ~4×, labor gap 10×). Also feeds Task 7 STEM recommendations (portability/space, confirmatory accuracy).

## Exchange 10 — surge timing (parameter: demand calendar)
- **Q:** Besides peak hour, when else in the day do airports most often face bag-drop surges that strain screening capacity?
- **A (summary):** Early-morning bank ~05:00–08:00 (often the single busiest period at hubs), late-afternoon/evening bank ~16:00–19:00, holiday/weekend peaks, and disruption surges (weather/ATC/cancellation re-drops); empirical judgments.
- **Effect on work:** Task 5 memo: size for the worst of the morning bank and evening bank with the same peak-hour method; N+1 spare also covers disruption re-drop surges. Task 4 recommendation: airlines should pre-position screening staff for the 05:00–08:00 and 16:00–19:00 banks and stagger departures within each bank (the Task 3 spacing rule) rather than banking them.

## Exchange-to-work compliance
Each exchange produced a parameter or constraint (all ten are in the PARAMS
table with value, interval, and source tag E1–E10) or a structural decision
(E5/E8/E9 set the no-backlog, fallback, and parallel-lane architecture). No
exchange was left unconverted; no expert wording is reproduced in
`solution.json` — only values, constraints, and equations derived from them.
