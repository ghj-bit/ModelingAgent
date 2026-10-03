# Expert Interaction Evidence — MM-Bench 2003_C (TSA checked-baggage screening)

Ten exchanges with an airport baggage-operations expert. Files:
`logs/operator_feedback/expert_question_N.md`, `expert_request_N.json`, `expert_reply_N.json`.
Each reply was converted into a model parameter, constraint, or structural
decision before the next exchange was asked. No expert text is copied into
`solution.json`; only parameter values with `source: exchange N` are used.

## Exchange 1
- **Question:** Do checked bags reach the claim/screening area evenly or in clumps as planes land?
- **Reply (summary):** Bags arrive in sudden bursts tied to aircraft arrivals; bursts partially overlap at busy airports but the flow is lumpy, not even.
- **Effect on work:** Modelled demand as per-flight bag bursts (one burst per flight, spread over `BAG_LAG` = 20 min starting `LAG` = 25 min before departure) instead of a smooth hourly rate. This bursty arrival process is the input to the demand curve `D(t)`; the sizing formula `N ≥ ceil(max_t D(t)/(r·t))` is only meaningful because arrivals are lumpy.

## Exchange 2
- **Question:** What share of passengers on a typical flight checks a bag?
- **Reply (summary):** 60–80% of passengers check; the common planning figure is ≈0.7 checked bags per passenger.
- **Effect on work:** Set planning parameter `bpp = 0.7` (interval 0.55–0.85 for the sensitivity sweep, `logs/sweep_bpp.log`); bag volume per flight = `bpp × seats`. Airport A peak-hour volume 3,777 bags; Airport B 4,047 bags.

## Exchange 3
- **Question:** How are screening lanes staffed — one operator all day or rotating crews?
- **Reply (summary):** Rotating crews; operators rotate positions roughly every 20–30 minutes because detection performance drops with sustained image-reading.
- **Effect on work:** Introduced the relief derating factor `rf = 1 − 0.5·relief/45` with base `relief = 10` min per 45-min rotation block, so `rf = 0.889`. Each machine's effective rate is `r × availability × rf` (e.g. 210 × 0.92 × 0.889 = 171.7 bags/h). Sweep over `relief` ∈ {5, 10, 15} in `logs/sweep_relief.log`.

## Exchange 4
- **Question:** How early must checked bags be on the scanner before the plane leaves?
- **Reply (summary):** Loading closes well before departure; the practical cutoff for a bag to make its flight is roughly 30–45 minutes before scheduled departure domestically.
- **Effect on work:** Set the flight-feasibility deadline `t_due = t_dep − CUTOFF` with base `CUTOFF = 30` min (interval 30–45). A flight is feasible iff all its bags are scanned by `t_due`. Sweep `cutoff` ∈ {30, 38, 45} in `logs/sweep_cutoff.log`. The model also enforces feasibility of the schedule itself: the earliest departure in the hour must satisfy `t_dep ≥ CUTOFF + 5`, which is why wave 1 starts at 45 min.

## Exchange 5
- **Question:** In a peak hour, are departures spread evenly or in a few crowded waves?
- **Reply (summary):** A few crowded waves — hub schedules are built around connecting banks; the peak hour contains one bank, so departures bunch in short windows with lulls between.
- **Effect on work:** Modelled departures as 3 waves (banks) within the hour: windows (45–50), (51–54), (55–58) min. This wave structure, not the average rate, drives the peak of the demand curve (`D(t)` peaks at t = 33 min for both airports) and therefore the machine count.

## Exchange 6
- **Question:** When a burst exceeds scanner capacity, what happens to bags waiting to be scanned?
- **Reply (summary):** They queue in a buffer/staging area, scanned in arrival order, drained in lulls; if the backlog does not clear before the loading cutoff, bags miss the flight.
- **Effect on work:** Justified the worst-case cumulative (EDF) balance as the binding constraint: since screening is in arrival/deadline order, N machines are adequate iff `D(t) ≤ N·r_eff·t` for all t ≥ 0, where `D(t)` counts bags present and due by t. The model's adequacy test is exactly this check, vectorized as `gap = D − N·r_eff·Tpos`.

## Exchange 7
- **Question:** When a scanner briefly breaks down during the busy hour, what do staff do with unscanned bags?
- **Reply (summary):** Queue in a buffer and keep the line moving; on longer outages reroute to another EDS lane or fall back to backup screening (ETD/hand search); protect the departure cutoff.
- **Effect on work:** (a) Hard constraint `N ≥ 2` per airport — one machine must remain as reroute/backup capacity when another is down (otherwise a single failure stops all screening in the hour). (b) The conservative-vs-recommended N gap (rate 160 vs 210 bags/h) is interpreted as the redundancy that absorbs a full machine loss plus slow throughput. (c) ETDs are specified as the backup second stage (task 6), consistent with the fallback practice.

## Exchange 8
- **Question:** Do the >200-seat jets in Table 1 mostly fly as hub connectors or point-to-point?
- **Reply (summary):** Mostly connecting-hub flights — >200-seat aircraft are deployed on high-density hub-feeding trunk routes; point-to-point with that size is the exception.
- **Effect on work:** Scheduled all ≥200-seat aircraft (215- and 350-seat) into wave 1 of the peak-hour bank (the connection-feeding departure wave), largest first; the remaining fleet fills waves 2–3 in descending size order. This determines which bags have the earliest deadlines in the hour.

## Exchange 9
- **Question:** Roughly how late can a pushback be before the delay really hurts?
- **Reply (summary):** About 15 minutes is the on-time threshold; beyond it, missed connections and rotation slippage propagate; 30+ minutes is substantial damage.
- **Effect on work:** Set the schedule margin: flights are held at a minimum 5-minute buffer between the last bag's deadline and departure feasibility, and the recommendations (task 4) quantify the cost of breaching the 15-minute on-time threshold as missed connections plus rebooking/crew costs — the economic weight in the position paper. The 15-minute figure bounds the acceptable delay in the sensitivity discussion (task 7).

## Exchange 10
- **Question:** How many checked bags does a 350-seat widebody typically carry at full load?
- **Reply (summary):** Roughly 200–280 bags; at the 0.7 bags/passenger planning figure, about 245.
- **Effect on work:** Validated the `bpp = 0.7` parameter against the largest flight: the 350-seat flight in both airports' tables yields 245 bags, inside the expert's 200–280 range. This cross-check (parameter from exchange 2 vs. direct answer from exchange 10) is recorded in the parameter table of `solution.json` as a consistency check.
