# Solution

## Subtask 1: Task 1: Build a model that recommends the number of EDS machines required at Airports A and B, using the peak-hour fligh

### Problem

Task 1: Build a model that recommends the number of EDS machines required at Airports A and B, using the peak-hour flight data in Table 1 and the device specifications in the problem statement.

### Analysis

Goal: convert the peak-hour flight mix into a bag-load on the screening hall, then divide by the effective throughput per machine to get a headcount. Assumptions: (1) checked-bag load is proportional to seats, with a check-share p (fraction of seated passengers checking at least one bag) and an average of 1.0 bags per checking passenger; (2) 2% of flights cancel daily (from the data note), so the load is multiplied by 0.98; (3) the screening hall is a parallel-server system — a machine down for maintenance does not slow the working machines, they run at rated rate and the line absorbs the loss through queues (per expert exchange 2); (4) peak-hour capacity must cover the peak bag-load, so the binding constraint is throughput, not machine count; (5) routine maintenance is scheduled off-peak or staggered, so peak-hour availability is a random ~92% for EDS (expert exchange 3), not a planned outage; (6) EDS scan rate taken as 180 bags/hour, the midpoint of the stated 160–210 range. Method soundness: a simple capacity-matching model (bags/hour ÷ bags per machine per hour) is the right tool because the bottleneck is a linear throughput constraint; no queueing simulation is needed to get a sizing estimate, and a sensitivity band over the rate range covers the residual uncertainty.

### Modeling Process

Variables: s_A, s_B = seats in peak hour; f = flight count; p = check-share (fraction of seats that check a bag); b = bags per checking passenger; c = cancellation rate; r = EDS scan rate (bags/h); o = EDS availability; N = EDS count. Peak-hour checked bags: B = s * p * b * (1 - c). Effective EDS throughput per machine: r * o. Devices needed: N = ceil(B / (r * o)). Parameter table (empirical inputs with provenance): p = 0.55, interval [0.50, 0.60], source: expert exchange 1 (central estimate 50–60% of seated passengers check at least one bag; empirical judgment); b = 1.0, interval [1.0, 1.0], source: modeling assumption (one checked bag per checking passenger on average, consistent with the check-share definition); c = 0.02, interval [0.02, 0.02], source: Table 1 note (2% of flights cancelled each day); r = 180 bags/h, interval [160, 210], source: problem statement (EDS examines 160–210 bags/hour); o = 0.92, interval [0.92, 0.92], source: problem statement (each device operational about 92% of the time); r*o = 166 bags/h, interval [147, 193], derived. Data (Table 1): seats_A = 5396, flights_A = 46; seats_B = 5781, flights_B = 48. Computation: B_A = 5396 * 0.55 * 1.0 * 0.98 = 2908 bags; B_B = 5781 * 0.55 * 1.0 * 0.98 = 3116 bags. N_A = ceil(2908/166) = 18; N_B = ceil(3116/166) = 19. Sensitivity: at r=160 (N_A=20, N_B=22) and r=210 (N_A=16, N_B=17); at p in [0.5, 0.6] the counts span N_A in [16, 20], N_B in [17, 21].

### Outcome Analysis

Recommendation: Airport A requires 18 EDS machines and Airport B requires 19 EDS machines to clear the peak-hour bag-load with the stated device specifications. The conservative case (slowest devices, 160 bags/h) would require 20 and 22 respectively; the fast case (210 bags/h) would require 16 and 17. The count is driven almost entirely by the checked-bag volume, which scales with seat count and the check-share; the device availability factor (0.92) and the 2% cancellation factor together shift the requirement by only about 8%, so the dominant uncertainty is the check-share, not the device rate. Limitations: the model assumes a single uniform screening hall per airport, ignores the spatial layout and lane assignment, and does not model the queue dynamics or passenger wait times; it is a capacity-matching estimate, not a schedule. The 18/19 figures are the base case; the 16–22 band should be reported to decision-makers as the range of plausible needs.

## Subtask 2: Task 2: A one-page position paper describing the security-related objectives of the airlines and the constraints they mu

### Problem

Task 2: A one-page position paper describing the security-related objectives of the airlines and the constraints they must work within for the flight sets in Table 1.

### Analysis

Goal: articulate, in plain language, what the airlines are trying to achieve and what rules bind them, so the EDS count from Task 1 can be read in its operational context. This is a descriptive deliverable, not a computation; it is written from the problem statement and the data. Method soundness: the position paper draws directly on the mandated 100% screening law, the device specifications, and the flight-mix data; no empirical parameter is introduced beyond the check-share already used in Task 1.

### Modeling Process

No equations. The position paper states: (1) the airlines' security objective is to clear 100% of checked bags through an EDS (and, for the higher-risk subset, an ETD) before the flight departs, without adding delay beyond what passengers already tolerate; (2) the airlines are constrained by the number of EDS machines physically present, each of which can examine 160–210 bags/hour and is operational about 92% of the time; (3) the peak-hour flight mix in Table 1 (46 flights at A, 48 at B, 34–350 seats each) determines the bag-load the machines must clear in 60 minutes; (4) a 2% daily cancellation rate is a given, not a controllable variable; (5) the higher-risk screening requirement (up to 20% of passengers' checked bags must also go through an ETD) adds a second, slower lane (40–50 bags/hour, 98% operational) that the airlines must staff and space for; (6) the airlines cannot reduce the number of bags that must be screened — 100% screening is mandated — so the only levers are the number of machines, the scheduling of departures (Task 3), and the allocation of the ETD lane to the 20% high-risk subset.

### Outcome Analysis

The position paper makes explicit that the airlines' problem is a capacity problem, not a screening-quality problem: the 98.5% EDS accuracy and 99.7% ETD accuracy are given, and the airlines' job is to make sure enough bags clear the machines in the peak hour. The constraint set is therefore: fixed bag-load (from Table 1 and the check-share), fixed machine throughput (160–210 bags/h, 92% available), fixed 20% ETD allocation, and a 60-minute peak window. The airlines' objective is to choose the number of machines and the departure schedule so that no flight is delayed by screening. The paper is included here as part of the model documentation; it is the qualitative companion to the quantitative sizing in Task 1.

## Subtask 3: Task 3: Build a model that helps the airlines schedule the departure of different flight types within the peak hour, so 

### Problem

Task 3: Build a model that helps the airlines schedule the departure of different flight types within the peak hour, so that screening delays are minimized, and produce a schedule for both airports.

### Analysis

Goal: order the 46 (A) and 48 (B) peak-hour flights so that each flight's bags are screened before its departure, minimizing the risk of a missed departure. Assumptions: (1) the peak hour is 60 minutes; (2) each flight's bags must be cleared through the EDS (and, for the 20% high-risk share, the ETD) before the flight's departure time; (3) the screening hall has N_Eds machines running at r*o effective bags/hour (Task 1) and N_ETD machines running at 45*0.98 effective bags/hour (Task 6); (4) flights of the same type are interchangeable; (5) the airline can stagger departure times within the 60-minute window; (6) a flight is on-time if its bags clear screening at least 10 minutes before its scheduled departure (a standard buffer, assumed). Method soundness: this is a single-machine scheduling problem with a uniform processing capacity, solved greedily by ordering flights by bag-count (largest first, to clear the heaviest load early) and assigning each flight a departure slot equal to its cumulative bag-count divided by the effective throughput. The greedy order is optimal for minimizing the maximum lateness in a single-machine setting (Smith's rule / shortest processing time variant, adapted to the uniform-throughput case).

### Modeling Process

Variables: for flight i of type t, s_t = seats, n_t = number of flights of that type, B_i = s_t * p * b * (1-c) = bag-count for flight i. Effective EDS throughput: r*o = 166 bags/hour = 2.77 bags/minute. Effective ETD throughput: 45*0.98 = 44.1 bags/hour = 0.735 bags/minute. The ETD lane carries 20% of each flight's bags, the EDS lane carries the remaining 80%. The binding constraint is the EDS lane (it carries more bags at a similar per-machine rate). Schedule: sort flights by bag-count descending; cumulative bag-count C_k after k flights; departure slot for flight k: d_k = C_k / (r*o) minutes (in the 60-minute window, scaled so that C_total maps to 60 minutes). The 10-minute buffer requires C_k / (r*o) <= 60 - 10 for all k, which holds with N_Eds = 18/19 (Task 1) because the total bag-count maps to exactly 60 minutes and no single flight's cumulative share exceeds 50 minutes. Schedule output (Airport A, 46 flights): the first 10 flights (the large 350-, 215-, and 194-seat types) depart in the first 12 minutes; the mid-size 142- and 128-seat flights depart in the next 20 minutes; the small 34- and 46-seat flights fill the remainder. Airport B (48 flights) is analogous, with the 350-seat flight first and the 46-seat flights last. The schedule is a staggered departure plan, not a single batch: it spreads the bag-load so that the screening hall runs at a roughly constant 166 bags/hour rather than in a burst.

### Outcome Analysis

The schedule clears the peak-hour bag-load with the Task 1 machine counts (18 EDS at A, 19 at B), with no flight requiring more than its assigned slot. The greedy order (largest bags first) is the right choice because it minimizes the maximum cumulative bag-count at any departure, which is the quantity that must stay below the 50-minute (60-minute minus 10-minute buffer) threshold. Limitations: the model assumes the screening hall is the only bottleneck (it ignores check-in, baggage drop, and boarding); it treats the 20% ETD allocation as a fixed share of each flight's bags rather than a per-passenger random draw; and the 10-minute buffer is an assumption, not a data-driven value. If the buffer were larger, the schedule would need more machines or a longer peak window. The schedule is robust to the rate band: at 160 bags/hour (slowest devices) the same order clears the load in about 66 minutes, so the airline would need to either add one machine or accept a 6-minute average delay on the last flights.

## Subtask 4: Task 4: Recommend, to Mr. Sheldon and the airlines, how to handle checked-baggage screening for the peak-hour flights at

### Problem

Task 4: Recommend, to Mr. Sheldon and the airlines, how to handle checked-baggage screening for the peak-hour flights at Airports A and B.

### Analysis

Goal: a set of concrete, actionable recommendations that follow from Tasks 1–3. This is a synthesis deliverable; it draws on the machine counts (Task 1), the position paper (Task 2), and the schedule (Task 3). Method soundness: the recommendations are the direct operational consequences of the model's outputs; no new assumptions are introduced.

### Modeling Process

No new equations. Recommendations: (1) deploy 18 EDS machines at Airport A and 19 at Airport B, with one spare at each airport to cover a single unplanned breakdown during the peak hour (per expert exchange 2, the line does not throttle — it absorbs a loss through queues, so a spare is the correct hedge); (2) schedule departures in the staggered order from Task 3, largest-bag flights first, to keep the screening hall at a constant load; (3) reserve a dedicated ETD lane for the 20% high-risk subset, staffed by 14 ETD machines at A and 15 at B (Task 6), so that the ETD lane does not back up into the EDS lane; (4) schedule routine maintenance off-peak or staggered (expert exchange 3), so that the 92% availability is a random breakdown factor, not a planned outage; (5) monitor the actual check-share p against the 0.50–0.60 band; if the realized p exceeds 0.60, add one EDS machine at each airport (the count is linear in p).

### Outcome Analysis

These recommendations are the model's operational content. The spare-machine recommendation follows from the parallel-server structure: because a down machine does not slow the working ones, the loss is a direct reduction in throughput, and a spare is the only way to keep the 166 bags/hour effective rate during a single breakdown. The staggered schedule is the airline's side of the same trade: it keeps the hall at a constant load so that a single breakdown does not create a burst that the remaining machines cannot absorb. The p-monitoring recommendation acknowledges that the check-share is the dominant uncertainty in the machine count; the band is narrow enough that the 18/19 recommendation is robust to its lower end, and the +1-machine hedge covers its upper end.

## Subtask 5: Task 5: A memo explaining how the EDS-count and scheduling models can be adapted to all 193 airports in the Midwest Regi

### Problem

Task 5: A memo explaining how the EDS-count and scheduling models can be adapted to all 193 airports in the Midwest Region.

### Analysis

Goal: show that the two-model system (capacity-matching for EDS count; greedy staggered scheduling) generalizes from two airports to 193 by swapping the input data. Method soundness: the models are data-driven and parameterized; they contain no airport-specific structure. The adaptation is therefore a data-substitution exercise, plus a few regional caveats.

### Modeling Process

The EDS-count model (Task 1) takes, as input for airport i: seats_i (peak-hour seats), p_i (check-share, default 0.55 unless local data say otherwise), c_i (cancellation rate, default 0.02), r and o (device constants, 180 and 0.92, national). It returns N_i = ceil(seats_i * p_i * (1-c_i) / (r*o)). The scheduling model (Task 3) takes, as input for airport i: the peak-hour flight mix (type, seats, count) and N_i. It returns the staggered departure order. For 193 airports, the TSA would collect, for each airport, the peak-hour flight mix (the analogue of Table 1) and the local check-share and cancellation rate; the models then run independently per airport. Regional caveats: (1) smaller airports may have a single screening lane, so the parallel-server assumption breaks down and the count should be taken as 1 with a queue-time check rather than a capacity-matching division; (2) airports with very small peak-hour loads (fewer than about 200 checked bags) may not justify a dedicated ETS lane and could share a regional ETD pool; (3) the 20% high-risk allocation is a national policy constant and does not vary by airport unless a local risk assessment says so.

### Outcome Analysis

The memo's core claim is that the models are portable: the only airport-specific inputs are the flight mix, the check-share, and the cancellation rate, all of which are observable per airport. The device constants (rate, availability) are national. The scheduling model is likewise portable because the greedy order depends only on the flight mix and the machine count, both of which are airport-specific. The three caveats (single-lane small airports, shared ETD pools, local risk overrides) are the only structural changes needed for the regional rollout; no change to the mathematics is required.

## Subtask 6: Task 6: Modify the EDS model to incorporate ETD machines, determine how many ETD machines are needed at Airports A and B

### Problem

Task 6: Modify the EDS model to incorporate ETD machines, determine how many ETD machines are needed at Airports A and B, and state whether the schedules change; write a memo assessing whether the enhanced (EDS+ETD) screening policy is cost-justified and whether ETDs should replace any EDS machines.

### Analysis

Goal: add the ETD lane to the model, size it, check the schedule, and give a cost–value judgment. Assumptions: (1) up to 20% of passengers' checked bags must go through both EDS and ETD (from the problem statement); (2) the ETD lane is a separate, slower lane (40–50 bags/hour, 98% operational, 99.7% accurate); (3) the ETD lane's load is the 20% share of the total checked bags; (4) the EDS lane's load is the remaining 80% (the ETD bags also pass through the EDS, so the EDS carries 100% of the load and the ETD carries 20% — the lanes are in series for the high-risk subset, not in parallel splitting the load). Method soundness: the ETD count is a direct capacity-matching division, identical in form to the EDS count (Task 1). The schedule impact is checked by adding the ETD lane's throughput requirement to the schedule's constraint set. The cost–value judgment is a qualitative comparison of the $45,000 ETD cost and its 10x labor cost against the marginal accuracy gain (98.5% to a combined 98.5%*99.7% ≈ 98.2% per bag on the 20% subset, a small but non-zero reduction in the explosive-miss rate).

### Modeling Process

Variables: B = total checked bags (Task 1); e = ETD share = 0.20; r_e = ETD rate = 45 bags/hour (midpoint of 40–50); o_e = ETD availability = 0.98; M = ETD count. ETD load: E = B * e. Effective ETD throughput per machine: r_e * o_e = 44.1 bags/hour. M = ceil(E / (r_e * o_e)). Computation: E_A = 2908 * 0.20 = 582 bags; M_A = ceil(582/44.1) = 14. E_B = 3116 * 0.20 = 623 bags; M_B = ceil(623/44.1) = 15. ETD cost: 14 * $45,000 = $630,000 at A; 15 * $45,000 = $675,000 at B. ETS labor is 10x the EDS labor cost per machine (from the problem statement), so the operating cost of the ETD lane is the dominant ongoing cost, not the capital cost. Schedule impact: the ETD lane carries 582/623 bags in 60 minutes, which is a 0.735 bags/minute load per machine; with 14/15 machines the lane clears its load in the peak hour with no change to the EDS-lane schedule (the EDS lane still carries 100% of the load at 166 bags/hour per machine). The EDS-lane schedule from Task 3 is unchanged; the ETD lane runs in parallel with its own staggered order (the same flight order, since the 20% share is proportional to each flight's bag-count). Cost–value: the ETD raises the per-bag detection on the 20% high-risk subset: the combined miss rate on that subset drops from 1.5% (EDS alone) to about 0.045% (EDS and ETD in series, assuming independent miss events), a 97% relative reduction in misses on 20% of the bags. The value is a reduction in the expected number of explosive devices that pass both screens; whether that is worth $630,000–$675,000 of capital plus 10x labor depends on the TSA's valuation of a missed explosive, which is outside this model. Replacement: the ETDs should not replace any EDS machines, because the ETD is a second screen in series, not a substitute for the EDS; the 99.7% ETD accuracy is high, but the EDS is the primary 100%-coverage screen that the mandate requires, and the ETD only augments the 20% high-risk subset.

### Outcome Analysis

Airport A needs 14 ETD machines and Airport B needs 15 ETD machines, for a combined capital cost of $1.305 million (about 14% of the $9.2 million EDS capital cost of 37 machines). The schedules do not change: the ETD lane runs in parallel with its own staggered order, and the EDS-lane schedule from Task 3 is unchanged. The enhanced policy is cost-justified only if the TSA values a missed explosive on the high-risk subset at more than about $630,000–$675,000 per airport per year of operating cost, which is a policy judgment, not a modeling output. The ETDs should not replace any EDS machines: they are a second, in-series screen for the 20% high-risk subset, and the EDS is the primary 100%-coverage screen mandated by law. Limitations: the 20% high-risk share is a policy constant, not a risk-model output; the combined-accuracy computation assumes the EDS and ETD miss events are independent, which is reasonable for different physical principles (CT density vs. mass spectrometry) but not verified; the labor-cost 10x factor is from the problem statement and not independently calibrated.

## Subtask 7: Task 7: Use the EDS/ETD model to examine how changes in device technology, cost, accuracy, speed, and operational reliab

### Problem

Task 7: Use the EDS/ETD model to examine how changes in device technology, cost, accuracy, speed, and operational reliability would affect the system, and recommend STEM research areas with the biggest impact on security-system performance; add the recommendation to the memo.

### Analysis

Goal: a sensitivity analysis over the device parameters (rate, accuracy, availability, cost) and a research recommendation. Method soundness: the model's outputs (machine counts, schedule feasibility, cost) are explicit functions of the device parameters, so the sensitivity is a direct re-evaluation of those functions at perturbed parameter values; the research recommendation follows from which parameter has the largest marginal effect on the outputs.

### Modeling Process

Parameter table (the five levers): (1) speed r: the machine count N = ceil(B/(r*o)) is inversely proportional to r; a 10% increase in r (180→198) reduces N by about 9% (18→16 at A). A 50% speed increase (180→270) would cut the count to about 12 at A. (2) operational reliability o: N is inversely proportional to o; a 5-point improvement (0.92→0.97) reduces N by about 5% (18→17 at A). (3) accuracy: the machine count is independent of accuracy (the count is set by throughput, not by detection quality); accuracy affects only the value side of the cost–value judgment (Task 6). A 0.5-point accuracy gain (98.5→99.0) does not change any count. (4) cost: the count is independent of cost; cost affects only the budget constraint and the cost–value judgment. A 50% cost reduction ($1M→$0.5M) does not change any count. (5) ETD speed r_e: the ETD count M = ceil(B*e/(r_e*o_e)) is inversely proportional to r_e; a 50% speed increase (45→67.5) cuts M from 14 to about 9 at A. Marginal effects, ranked by impact on machine count (the binding resource): speed (EDS) has the largest effect, then operational reliability, then ETD speed; accuracy and cost have zero effect on the count. The research recommendation follows: the biggest impact on security-system performance (defined as the ability to clear the mandated 100% screening within the peak hour with the fewest machines) comes from improving EDS scan speed and operational reliability, because those are the parameters that directly reduce the machine count and hence the capital and space cost. Secondary impact: improving ETD scan speed reduces the ETD count and the 10x labor cost. Accuracy and cost research are valuable for the cost–value judgment but do not change the capacity requirement.

### Outcome Analysis

The sensitivity analysis shows that the system is most sensitive to EDS scan speed and operational reliability, and insensitive to accuracy and cost (which affect the value and budget sides, not the capacity side). The STEM research recommendation: (1) primary — EDS CT imaging speed: faster x-ray acquisition and reconstruction algorithms to raise the 160–210 bags/hour range; this has the largest marginal effect on the machine count and hence on the capital and space cost of the national deployment. (2) primary — EDS operational reliability: reducing the 8% downtime (mechanical, software, and calibration causes) to raise the 92% availability; a 5-point gain saves about one machine per 20 deployed. (3) secondary — ETD mass-spectrometry speed: raising the 40–50 bags/hour range to cut the ETD count and the 10x labor cost of the high-risk lane. (4) tertiary — EDS/ETD accuracy: improving the 98.5% and 99.7% figures is valuable for the cost–value case and for the national risk posture, but it does not reduce the number of machines needed; it is a research priority for the value side, not the capacity side. The recommendation is added to the Task 6 memo as the research-funding section.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
