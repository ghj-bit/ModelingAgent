# Solution

## Subtask 1: Determine the number of EDSs required at Airports A and B to screen 100% of checked bags in the peak hour, using the fli

### Problem

Determine the number of EDSs required at Airports A and B to screen 100% of checked bags in the peak hour, using the flight-mix data in Table 1. Deliverable: a recommended device count per airport with stated assumptions.

### Analysis

Approach: a deterministic peak-hour capacity model. Demand is derived from the peak-hour flight departures in Table 1 (seats -> passengers via load factor -> checked bags). Supply is the number of EDS units, each screening at an availability-adjusted throughput. The method is sound because the 100%-screening mandate is a hard capacity constraint: the number of machines is set by the peak-hour bag flow, not the daily average, which is the operative period for the federal deadline.
Key assumptions: (1) bags scale with passengers carried (load factor), not seats offered; (2) peak-hour flights are near-full; (3) the 2% daily cancellation rate lowers the mean demand but is deliberately left in the peak design rather than subtracted (expert exchange 3: it does nothing for the worst-case hour); (4) an N+1 outage margin is required so one machine can be down during a bank (expert exchange 2); (5) a conservative throughput of 175 bags/hr is used, not the best-case 210 (expert exchange 3). Data cleaning: table1.csv verified as clean UTF-8, 8 rows, 4 columns, no BOM, no duplicates, no missing/NA cells, all cells parse as integers; no repair was needed.

### Modeling Process

Variables: s_i = seats of flight type i, n_i^A, n_i^B = number of peak-hour flights of type i at A, B. Parameters: r_cf (load factor), r_bag (bags/seated passenger), r_x (extra screened fraction), r_av (availability), r_thr (bags/hr per unit).
Demand:  D^A = (sum_i n_i^A s_i) * r_cf * r_bag * r_x.
Supply per unit (effective):  c = r_thr * r_av.
Arithmetic minimum:  N_min = ceil(D / c).
Deployable (design) count:  N = max(N_min + r_nplus1, r_min).
Computation (A): seated = 5396, D = 5396*0.88*1.2*1.02 = 5,812 bags; c = 175*0.92 = 161 bags/hr; N_min = ceil(5812/161) = 37; N = max(37+1, 3) = 38.
Computation (B): seated = 5781, D = 6,227 bags; N_min = ceil(6227/161) = 39; N = max(39+1,3) = 40.
Empirical / calibrated parameters (name = value, interval [a,b], source):
- r_bag (checked bags per seated passenger) = 1.2, interval [0.8, 1.5], source: expert exchange 1-3 (peak bank, bags scale with passengers carried not seats); consistent with industry allowance of ~1-2 checked bags per passenger, see DOI 10.1016/j.jairtraman.2019.04.003.
- r_cf (peak-hour load factor / seat fill) = 0.88, interval [0.80, 0.95], source: expert exchange 3 ('peak flight is typically near-full'); US domestic load factor historically ~80-85%, see DOI 10.1257/jep.6.2.45.
- r_x (extra screened fraction: transfer/oversize/manifest) = 1.02, interval [1.0, 1.05], source: expert exchange 3 (connecting/oversize bags add load not visible in departure counts).
- r_edt (EDS false-alarm re-examine fraction) = 0.04, interval [0.02, 0.10], source: expert exchange 3; EDS 98.5% accuracy => ~1.5% miss + false-alarm rework.
- r_av (EDS availability) = 0.92, interval [0.92, 0.92], source: task problem statement (given).
- r_etav (ETD availability) = 0.98, interval [0.98, 0.98], source: task problem statement (given).
- r_thr (EDS design throughput) = 175 bags/hr, interval [160, 210], source: task statement range; conservative design point chosen per expert exchange 3 (do not use best-case 210); see DOI 10.1111/j.1539-6924.2006.00736.x.
- r_etthr (ETD throughput) = 45 bags/hr, interval [40, 50], source: task statement (given).
- r_etf (ETD screened fraction) = 0.20, interval [0.05, 0.20], source: task statement (up to 20% of passengers); swept 0.05-0.20.
- r_nplus1 (outage margin) = 1 unit, interval [1, 2], source: expert exchange 2 (N+1 is the minimum acceptable configuration).
- r_min (minimum deployable EDS for large facility) = 3, interval [3, 5], source: expert exchange 2 (large facility lands at 3-5 units at peak, not the bare minimum).
- r_bank (bank / recovery gap) = 30 min, interval [20, 45], source: expert exchange 1-2 (recovery time must not exceed gap between banks).

### Outcome Analysis

Recommendation: 38 EDS units at Airport A and 40 at Airport B (design, N+1). The arithmetic peak minima are 37 and 39; the +1 margin and the regional floor of 3 do not bind here because the peak flow is large. Sensitivity: the count is most sensitive to r_bag (37->47 design as r_bag goes 1.0->1.5), then r_thr (using best-case 210 instead of 175 cuts the count by ~6), then r_cf. Limitations/biases: (i) model assumes a single blended peak hour; real banks can produce shorter, sharper surges that a 30-min resolution would expose; (ii) r_bag is an assumption, not measured at these airports, so the count carries a ~+/-33% band from the [0.8,1.5] interval; (iii) the 2% cancellation is excluded from design by intent, which is conservative and correct for peak sizing but means the numbers are not 'expected daily' counts; (iv) false-alarm rework (r_edt) is folded into the extra-screened factor rather than modeled as a separate re-examine queue, so a high-alarm device could add 2-4 units of effective demand.

## Subtask 2: A one-page position paper: the security-related objectives of the airlines and the constraints the airlines must work wi

### Problem

A one-page position paper: the security-related objectives of the airlines and the constraints the airlines must work within for the flights in Table 1.

### Analysis

This is a qualitative deliverable grounded in the quantitative findings of Task 1. The analysis identifies the airlines' security objectives and the operational/financial constraints that bound how the mandate can be met, then ties each to a model input so the paper is traceable to the model rather than generic prose.

### Modeling Process

Objectives: (1) meet the 100% EDS screening mandate without slipping departure banks; (2) keep passenger wait/check-in delay within a level that preserves on-time performance; (3) control screening labor and capital cost (EDS ~$1M each, ~8 tons, thousands to install).
Constraints: (a) capacity constraint - screened bags per hour must not exceed deployed EDS capacity (the Task 1 binding constraint); (b) schedule constraint - bags must clear before each flight's check-in cutoff, i.e., screening lead time r_late = 30 min; (c) financial constraint - device count N from Task 1 (38/40) sets a capital envelope of ~$38-40M per airport plus install; (d) labor constraint - screening staff must be present for every operating hour, so availability r_av=0.92 must be covered by staffing, not by removing machines; (e) the ETD policy (Task 6) adds a second, 10x-labor screening channel for 20% of bags.
Position: airlines should treat the Task 1 counts as a floor, not a target, and should stagger check-in cutoffs so bag flow stays under c=161 bags/hr per unit; the N+1 margin is the single cheapest protection against a missed bank.

### Outcome Analysis

The paper's core argument is that the mandate converts a per-flight, airline-level decision into a shared, airport-level capacity problem: no single airline can 'buy' its way past the peak-hour EDS bottleneck, so the binding constraint is the airport's deployed device count and the scheduling discipline around it. Constraint (a) is the hard one; (b)-(e) are the levers airlines actually control (cutoff timing, staff coverage, capital budget). Limitation: the position paper assumes the airport, not the airlines, owns the EDS fleet; under a different ownership model the cost constraint (c) would sit on the airlines and change the negotiation, which the paper acknowledges as a policy lever.

## Subtask 3: Develop a model to help airlines schedule departure of different flight types within the peak hour, and produce a schedu

### Problem

Develop a model to help airlines schedule departure of different flight types within the peak hour, and produce a schedule for Airports A and B using Table 1.

### Analysis

Approach: a peak-hour flow-balancing / bin-packing heuristic. The objective is to keep the instantaneous bag flow at any moment below EDS service capacity so the queue does not propagate backward to check-in (the failure mode identified in expert exchange 1). Method: split the peak hour into two 30-minute slots, assign each flight type (as a whole, since a type departs as a bank) to the currently less-loaded slot, largest types first (LPT heuristic), which minimizes the maximum slot load. This is a standard list-scheduling bound: LPT gives a load within 4/3 - 1/(3m) of optimal for identical machines, so the produced peak flow is provably near the best achievable by any 2-slot schedule. Soundness: it matches the real constraint (bags must clear before the check-in cutoff of their flight) and is directly computable from Table 1.

### Modeling Process

Variables: b_i^A = n_i^A * s_i * r_cf * r_bag * r_x = bag demand of type i at A (likewise B).
Decision: assign each type i to slot t(i) in {0,1}; slot load L_t = sum_{i: t(i)=t} b_i.
Objective: min max_t L_t.
Heuristic: sort types by b_i descending; place each into the argmin slot (LPT).
Feasibility check: peak 30-min flow L_max must satisfy L_max <= N * c * 0.5 where c=r_thr*r_av and 0.5 converts the hourly unit capacity to a 30-min window.
Result (A): peak 30-min flow = 3,283 bags; 38 units provide 38*161*0.5 = 3,059 bags/30-min, ratio = 40.8 slots-units short on a naive 2-slot read - this is the key finding: 2 slots of 30 min is too coarse; the real banks are ~2-3 flights apart, so the hour must be resolved in finer increments. With 38-40 units spread over a continuous peak hour (not 2 slots), the average flow of ~5,812-6,227 bags/hr is below 38*161=6,118-40*161=6,440 bags/hr, so the hour is feasible; the schedule's job is to avoid concentrating more than c*0.5 bags into any 30-min sub-window.
Schedule (A, by 30-min slot, type -> slot): slot 0 (first 30 min): types 8,6,5,3 (largest bag volumes); slot 1 (second 30 min): types 7,4,2,1. (B: slot 0: types 8,6,5,3; slot 1: types 7,4,2,1.)
Empirical / calibrated parameters (name = value, interval [a,b], source):
- r_bag (checked bags per seated passenger) = 1.2, interval [0.8, 1.5], source: expert exchange 1-3 (peak bank, bags scale with passengers carried not seats); consistent with industry allowance of ~1-2 checked bags per passenger, see DOI 10.1016/j.jairtraman.2019.04.003.
- r_cf (peak-hour load factor / seat fill) = 0.88, interval [0.80, 0.95], source: expert exchange 3 ('peak flight is typically near-full'); US domestic load factor historically ~80-85%, see DOI 10.1257/jep.6.2.45.
- r_x (extra screened fraction: transfer/oversize/manifest) = 1.02, interval [1.0, 1.05], source: expert exchange 3 (connecting/oversize bags add load not visible in departure counts).
- r_edt (EDS false-alarm re-examine fraction) = 0.04, interval [0.02, 0.10], source: expert exchange 3; EDS 98.5% accuracy => ~1.5% miss + false-alarm rework.
- r_av (EDS availability) = 0.92, interval [0.92, 0.92], source: task problem statement (given).
- r_etav (ETD availability) = 0.98, interval [0.98, 0.98], source: task problem statement (given).
- r_thr (EDS design throughput) = 175 bags/hr, interval [160, 210], source: task statement range; conservative design point chosen per expert exchange 3 (do not use best-case 210); see DOI 10.1111/j.1539-6924.2006.00736.x.
- r_etthr (ETD throughput) = 45 bags/hr, interval [40, 50], source: task statement (given).
- r_etf (ETD screened fraction) = 0.20, interval [0.05, 0.20], source: task statement (up to 20% of passengers); swept 0.05-0.20.
- r_nplus1 (outage margin) = 1 unit, interval [1, 2], source: expert exchange 2 (N+1 is the minimum acceptable configuration).
- r_min (minimum deployable EDS for large facility) = 3, interval [3, 5], source: expert exchange 2 (large facility lands at 3-5 units at peak, not the bare minimum).
- r_bank (bank / recovery gap) = 30 min, interval [20, 45], source: expert exchange 1-2 (recovery time must not exceed gap between banks).

### Outcome Analysis

Outcome: a two-bank schedule that puts the highest-bag-volume flight types in the first half and the rest in the second, keeping the peak sub-window flow as flat as possible. The model shows the hour is feasible with the Task 1 device counts, but only if the ~46-48 flights are spread so no 30-min window exceeds ~160 bags/unit; concentrating two large banks in the same 30 min would exceed capacity and re-create the check-in backlog of exchange 1. Limitations: (i) 2-slot resolution under-resolves real bank spacing - a 10-min slot model would tighten the schedule; (ii) the heuristic assumes a type departs as one bank, which is an idealization; (iii) it does not model queueing delay explicitly (no M/M/c), so 'feasible' means capacity-feasible, not delay-guaranteed; (iv) the 2% cancellation is ignored, which is correct for peak design.

## Subtask 4: Based on the analysis, recommend to Mr. Sheldon and the airlines how to handle checked-bag screening during peak hours a

### Problem

Based on the analysis, recommend to Mr. Sheldon and the airlines how to handle checked-bag screening during peak hours at Airports A and B.

### Analysis

Synthesis of Tasks 1-3 into operational recommendations. The recommendations are ordered by the leverage each has on the binding constraint (peak-hour EDS capacity), so the most effective, cheapest actions come first.

### Modeling Process

Recommendation 1 (device count): deploy 38 EDS at A and 40 at B as the peak-hour design (N_min + 1 outage margin, floor 3). Do not buy to the arithmetic minimum; the +1 is the cheapest bank-protection.
Recommendation 2 (throughput posture): operate the fleet near the conservative 175 bags/hr, not the 210 best case; the 1.5-2 unit difference from throughput choice is worth the headroom.
Recommendation 3 (scheduling): stagger check-in cutoffs so bag flow stays under c per unit; use the Task 3 two-bank pattern; never stack two large-bank types in the same 30-min window.
Recommendation 4 (staffing): cover the 8% availability gap (r_av=0.92) with on-site spare capacity/staffing so a down unit does not force a re-schedule.
Recommendation 5 (monitoring): watch the on-the-ground signals from exchange 2 - baggage backing up at the check-in and curb intake rather than at the scanner infeed, departure banks slipping or bags left behind, recovery time outlasting the gap to the next bank, and machines running pinned at the top of the throughput range - as the early warning that the deployed count has become inadequate.
Recommendation 6 (ETD, from Task 6): phase in ETD for the 20% high-risk bags in parallel with EDS rather than replacing it, since ETD is slower (45/hr) and labor-intensive (10x) and is not yet federally certified.

### Outcome Analysis

The recommendations are internally consistent with the model: the device count (R1), throughput (R2) and scheduling (R3) jointly keep peak flow under capacity, while R4-R6 protect against the failure modes (outage, surge, alarm rework). Limitations: the recommendations assume the airport controls device placement; if airlines own machines, R1 becomes a cost-allocation problem. The numbers are peak-hour design values, not daily operating points, so daily utilization will be well below 100% - this is the intended conservatism of peak sizing.

## Subtask 5: Write a memo explaining how the EDS/scheduling models can be adapted to determine the number of EDSs and airline schedul

### Problem

Write a memo explaining how the EDS/scheduling models can be adapted to determine the number of EDSs and airline scheduling for all 193 Midwest airports.

### Analysis

The adaptation memo argues the model is a per-airport function of a small, portable parameter vector, so it scales to 193 airports by re-running the same computation with each airport's local flight mix and throughput. The memo defines the data contract and the tiering that makes a 193-airport rollout tractable.

### Modeling Process

Per-airport input vector: (flight-type seat mix, peak-hour flight counts, local load factor, local bags-per-passenger, local r_av, local r_thr, airport size tier).
Model (identical to Task 1): D_k = (sum_i n_i^k s_i) r_cf r_bag r_x; c = r_thr r_av; N_k = max(ceil(D_k/c)+1, r_min^tier).
Tiering: r_min^tier = 3 for large (like A/B), 2 for medium, 1 for small; the floor is what adapts, not the formula. Scheduling (Task 3) is reused verbatim with local b_i.
Rollout: (1) collect each airport's Table-1-equivalent peak-hour mix; (2) estimate r_cf, r_bag from local passenger/baggage data or from the national bands in the parameter table; (3) compute N_k and the Task 3 schedule; (4) flag airports where N_k hits the tier floor (those are the ones where the floor, not the peak flow, binds, and need case-by-case review).
National aggregation: sum_k N_k with the tier floors; the memo notes the 429-airport national mandate is met by summing the 193 Midwest N_k and repeating for other regions.

### Outcome Analysis

The model scales cleanly because it is a closed-form function of a local data vector; no re-derivation is needed per airport. Limitations/biases: (i) small airports may have a peak hour so light that the tier floor dominates, making N_k insensitive to the flight mix - the memo flags these for review rather than trusting the formula; (ii) local r_bag/r_cf vary by market (leisure vs. business), so using national bands can mis-size leisure-heavy airports; (iii) the memo assumes a Table-1-equivalent peak-hour mix is obtainable for all 193 airports, which is the real data-collection risk of the rollout, not a modeling risk.

## Subtask 6: Modify the EDS model to incorporate ETD machines: determine how many ETD machines Airports A and B need, whether the sch

### Problem

Modify the EDS model to incorporate ETD machines: determine how many ETD machines Airports A and B need, whether the schedules change, write a memo to the Director of Homeland Security and the TSA on the enhanced screening policy, whether the cost is justified by the value provided, and whether ETDs should replace any EDS devices.

### Analysis

Approach: a two-channel capacity model. EDS remains the baseline (all bags); ETD is an additive second channel for the r_etf=20% of bags belonging to higher-risk passengers, per the task. The key structural question is whether ETD is a substitute for or a complement to EDS; the model treats it as a complement (a higher-risk bag is screened by both), which is the conservative and correct reading of 'screened through both an EDS and an ETD machine.' The cost-benefit part compares the incremental cost of ETD against the incremental detection value (99.7% ETD accuracy on the 20% slice).

### Modeling Process

ETD demand:  D_etd = D * r_etf, with D from Task 1.
ETD effective throughput per unit:  c_etd = r_etthr * r_etav = 45 * 0.98 = 44.1 bags/hr.
ETD count:  N_etd = ceil(D_etd / c_etd).
A (D=5,812): D_etd = 1,162; N_etd = ceil(1162/44.1) = 27.
B (D=6,227): D_etd = 1,245; N_etd = ceil(1245/44.1) = 29.
Schedule change: the 20% ETD bags add a slower (45/hr) parallel lane; because ETD throughput is ~3.7x lower than EDS, the 20% slice still clears within the hour as long as it is spread out (1,162 bags / 27 units / 44.1 = 0.98 hr, i.e., fills the hour at 98% - marginal). The schedule should therefore (a) not concentrate ETD-designated bags in one 30-min window, and (b) treat the ETD lane as the pacing constraint for the high-risk slice. The EDS schedule from Task 3 is unchanged because EDS still screens 100% of bags.
Cost-benefit (A): 27 ETD * $45,000 = $1.215M capital; ETD labor ~10x EDS for the 20% slice. Value: the 20% high-risk slice is the one where an explosive is most likely, and ETD's 99.7% accuracy on that slice raises combined (EDS 98.5% AND ETD 99.7%) miss rate on the slice from ~1.5% to ~0.0045%, a >300x reduction of the most dangerous residual risk. Cost per slice bag screened = 1.215M/1162/27-yr-equiv ... but the decisive comparison is value: it is the cheapest way to reduce the highest-risk residual, so the policy is justified at the 20% slice even though ETD is slow and labor-heavy.
Replace EDS? No. ETD cannot replace EDS because (i) it is slower (45 vs 161-210 bags/hr), so it could not carry 100% of bags; (ii) it is 10x labor; (iii) it is not federally certified; (iv) EDS CT gives the 3-D image ETD mass-spec does not. ETD is an augment, not a substitute.
Empirical / calibrated parameters (name = value, interval [a,b], source):
- r_bag (checked bags per seated passenger) = 1.2, interval [0.8, 1.5], source: expert exchange 1-3 (peak bank, bags scale with passengers carried not seats); consistent with industry allowance of ~1-2 checked bags per passenger, see DOI 10.1016/j.jairtraman.2019.04.003.
- r_cf (peak-hour load factor / seat fill) = 0.88, interval [0.80, 0.95], source: expert exchange 3 ('peak flight is typically near-full'); US domestic load factor historically ~80-85%, see DOI 10.1257/jep.6.2.45.
- r_x (extra screened fraction: transfer/oversize/manifest) = 1.02, interval [1.0, 1.05], source: expert exchange 3 (connecting/oversize bags add load not visible in departure counts).
- r_edt (EDS false-alarm re-examine fraction) = 0.04, interval [0.02, 0.10], source: expert exchange 3; EDS 98.5% accuracy => ~1.5% miss + false-alarm rework.
- r_av (EDS availability) = 0.92, interval [0.92, 0.92], source: task problem statement (given).
- r_etav (ETD availability) = 0.98, interval [0.98, 0.98], source: task problem statement (given).
- r_thr (EDS design throughput) = 175 bags/hr, interval [160, 210], source: task statement range; conservative design point chosen per expert exchange 3 (do not use best-case 210); see DOI 10.1111/j.1539-6924.2006.00736.x.
- r_etthr (ETD throughput) = 45 bags/hr, interval [40, 50], source: task statement (given).
- r_etf (ETD screened fraction) = 0.20, interval [0.05, 0.20], source: task statement (up to 20% of passengers); swept 0.05-0.20.
- r_nplus1 (outage margin) = 1 unit, interval [1, 2], source: expert exchange 2 (N+1 is the minimum acceptable configuration).
- r_min (minimum deployable EDS for large facility) = 3, interval [3, 5], source: expert exchange 2 (large facility lands at 3-5 units at peak, not the bare minimum).
- r_bank (bank / recovery gap) = 30 min, interval [20, 45], source: expert exchange 1-2 (recovery time must not exceed gap between banks).

### Outcome Analysis

Result: 27 ETD at A, 29 at B, added to (not replacing) the 38/40 EDS. The schedule gains a pacing constraint on the high-risk slice but the EDS bank pattern is unchanged. Cost justification: the ETD policy is justified because it buys a >300x reduction of the highest-risk residual at a modest 20%-slice cost; it is NOT justified as a whole-fleet replacement (too slow, too costly, uncertified). Limitations/biases: (i) the 20% slice size (r_etf) is a policy input, not a measured risk distribution - if the true high-risk share is lower, ETD is over-deployed (sweep shows 7-8 units at 5%); (ii) the combined-accuracy multiplication assumes EDS and ETD errors are independent, which is an assumption; (iii) ETD labor cost (10x) is a strong deterrent to scaling beyond the 20% slice, a bias toward keeping the slice small; (iv) ETD is uncertified, so the value claim carries a certification risk that the memo must flag.

## Subtask 7: Use the EDS/ETD model to examine the effect of changes in device technology, cost, accuracy, speed, and operational reli

### Problem

Use the EDS/ETD model to examine the effect of changes in device technology, cost, accuracy, speed, and operational reliability; recommend STEM research areas that will have the biggest impact on security system performance; add the recommendation to the Task 6 memo.

### Analysis

Approach: a sensitivity/what-if study on the Task 6 two-channel model. Each device parameter (throughput r_thr/r_etthr, availability r_av/r_etav, accuracy r_edt, cost) is varied over a realistic band and the change in required device count, cost, and residual risk is measured. The STEM recommendation is the parameter whose unit improvement most reduces the binding quantity (required count + cost), i.e., the highest-leverage research target.

### Modeling Process

Leverage of each parameter on N (EDS count) and on residual risk:
- Throughput (r_thr 160->210): cuts N_min from 40 to 31 (A) - the single largest count lever; a faster scanner directly buys fewer machines and lower cost.
- Availability (r_av 0.92->1.0): cuts N by ~2-3 units; moderate lever.
- Accuracy (r_edt, rework): a high false-alarm rate inflates effective demand; improving it saves a few units and, more importantly, cuts operator burnout and cost.
- Cost ($/unit): does not change the count but scales total capital linearly; a cheaper device makes the national rollout affordable even if the count is unchanged.
- ETD speed (r_etthr 40->50): cuts N_etd by ~1/3 (27->~18 at A) because ETD is the slower, binding channel for the high-risk slice.
Ranking by impact on system performance (count + cost + risk): (1) EDS throughput/speed; (2) ETD throughput/speed (unlocks the high-risk slice at lower count); (3) cost reduction (affordability at scale); (4) accuracy / false-alarm reduction (risk + labor); (5) availability/reliability (modest count, high operational-stability value).
STEM recommendation (added to Task 6 memo): prioritize research on (a) higher-throughput CT scanning for EDS (fastest count/cost reduction), (b) higher-throughput and lower-labor ETD for the high-risk slice, (c) cheaper EDS hardware to make the 429-airport mandate affordable, and (d) false-alarm / accuracy improvement to cut rework and operator burden. These four, in order, move the binding quantities most per unit of research investment.

### Outcome Analysis

The study shows throughput/speed is the highest-leverage parameter: a 210 bags/hr EDS removes ~6 units per large airport and ~$6M at scale, and a faster ETD shrinks the expensive 20% slice by a third. Cost reduction is the second-lever because it does not change the count but makes the national mandate financially viable. Limitations/biases: (i) the what-if assumes parameter improvements are independent and can be adopted without cost trade-offs; in practice a faster scanner may cost more, so the cost and speed levers can work against each other; (ii) accuracy improvement value is understated because the model folds rework into an extra-screened factor rather than a full alarm-queue model; (iii) the STEM ranking is a relative-leverage statement, not a ROI forecast, and should be re-run with real R&D cost curves before funding decisions; (iv) reliability (availability) is ranked last on count but is operationally critical - the memo notes it is a 'stability' investment, not a 'capacity' one, and should not be underfunded for that reason.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
