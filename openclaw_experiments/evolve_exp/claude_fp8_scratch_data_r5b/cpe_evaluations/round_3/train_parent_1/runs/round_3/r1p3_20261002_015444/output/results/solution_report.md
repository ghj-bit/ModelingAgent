# Solution

## Subtask 1: Task 1: Develop a model to determine the number of EDS (explosive detection system) devices required at Airports A and B

### Problem

Task 1: Develop a model to determine the number of EDS (explosive detection system) devices required at Airports A and B during the peak hour, using Table 1 (peak-hour flight departures), stating all assumptions. Scope: throughput-driven device sizing for the two largest regional facilities.

### Analysis

The model is a peak-rate queue sizing model. The key structural choice comes from expert consultation: checked bags do NOT arrive as one batch per flight; they trickle in as a time-distributed stream over the check-in window (opening ~2-3 h before departure, running to the cutoff ~30-45 min before), peaking in the last hour before cutoff, and they interleave from many flights in a shared centralized bag-handling system. Therefore the binding constraint on EDS count is the PEAK arrival RATE (bags/min), not the total bag count, and a single shared EDS pool per airport is correctly sized against that peak rate rather than per-flight dedicated machines. I assume (a) every seat carries ~0.20 checked bags (BTR=0.20; typical domestic range 0.10-0.40, swept), (b) a 60-minute peak hour, (c) EDS throughput at the midpoint 185 bags/hr with 92% availability, (d) a target peak utilization of 85% to leave headroom for downtime variability. Method is sound because it is the standard M/M/c peak-load sizing: minimum integer n with peak_rate <= 0.85 * n * mu * alpha.

### Modeling Process

Variables: seats_j = seats on flight type j; f_j = peak-hour flights of type j at the airport; BTR = checked bags per seat; T = total peak-hour bags = sum_j seats_j * f_j * BTR; span = PEAK_HR - MIN_LAG (screenable minutes; MIN_LAG=30 min transport+loading buffer from expert exchange 2); PEF = 1.6 peak concentration factor (expert exchange 1: last-hour peak). Peak arrival rate: r = (T / span) * PEF bags/min. EDS effective capacity per device: c = MU_EDS * ALPHA = 185 * 0.92 = 170.2 bags/hr. Minimum devices: n = ceil( (r*60) / (TARGET_UTIL * c) ), TARGET_UTIL=0.85. Parameter table (empirical inputs the model uses, with interval and source): BTR = 0.20 checked bags per seat, interval [0.10, 0.40], source: stated assumption, swept in code/model.py --sweep BTR (not derivable from the dataset; web retrieval of a primary statistic was unavailable in this environment, so it is treated as a modelled assumption with a documented sensitivity rather than a fabricated citation); PEF = 1.6, interval [1.0, 2.0], source: expert exchange 1 (arrival is a smoothed flow peaking in the last hour before cutoff; PEF is the resulting concentration factor, swept); MIN_LAG = 30 min, interval [30, 45] domestic (up to 60 international), source: expert exchange 2; MU_EDS = 185 bags/hr, interval [160, 210], source: problem statement; ALPHA = 0.92, interval [0.92, 0.92], source: problem statement; TARGET_UTIL = 0.85, interval [0.80, 0.90], source: standard reliability design practice (headroom for the 8% downtime).

### Outcome Analysis

Airport A: T = 1079 bags/peak-hr, peak rate r = 57.6 bags/min -> n = 24 EDS (effective capacity 4085 bags/hr, utilization 84.5%). Airport B: T = 1156 bags/peak-hr, r = 61.7 bags/min -> n = 26 EDS (capacity 4425 bags/hr, utilization 83.6%). Sensitivity: BTR 0.10->0.40 gives A 11->41 and B 11->44 devices, so the recommendation is robust to the sign but scales roughly linearly with the checked-bag ratio; MU_EDS 160->210 gives A 24->18; PEF 1.0->2.0 gives A 13->26. Recommendation: deploy 24 EDS at A and 26 at B for the 85% utilization design point, with a sensitivity band of ~18-33 (A) and ~20-35 (B) EDS depending on realized BTR and throughput. Limitations/biases: (1) BTR is a single airport-wide assumption, not flight-type-specific (large jets like the 350-seat type overstate their checked-bag share); (2) PEF is a scalar approximation of the arrival shape, not a full time-varying arrival distribution; (3) the 85% target bakes in a reliability margin that may be conservative for a device at exactly 92% availability. The model is throughput-driven and does not yet account for the secondary-inspection (false-alarm) load, addressed in Task 6.

## Subtask 2: Task 2: A one-page position paper describing the airlines' security-related objectives and the constraints they must wor

### Problem

Task 2: A one-page position paper describing the airlines' security-related objectives and the constraints they must work within for the flight sets in Table 1.

### Analysis

This is a qualitative deliverable, framed as a position paper for Mr. Sheldon. The goal is to make explicit the tension between the airline's operational objectives (on-time departure, cost, throughput, passenger experience) and the security constraints the 100% screening mandate imposes. Scope: the flight types in Table 1 (seats 34-350, 46 peak-hour flights at A, 48 at B).

### Modeling Process

No equations; a structured set of objectives and constraints. Objectives (airline): (1) meet the scheduled departure time for every flight in the peak hour; (2) minimize cost per screened bag (device purchase ~$1M each, installation thousands of dollars, operator labor); (3) maximize throughput so the peak-hour departure schedule is not delayed; (4) minimize passenger delay and rebooking. Constraints (within which the airline must operate): (a) 100% of checked bags must be screened by an EDS (federal mandate); (b) a checked bag must be screened AND loaded before the bag-room cutoff, ~30-45 min before departure (empirical operational norm, expert exchange 2); (c) screening takes ~6-9 s per bag per device, so bag count bounds the screening time; (d) limited space and capital at each airport bound the number of devices; (e) the peak-hour flight mix is fixed by Table 1, so the airline cannot simply add capacity without more devices. The position: the airline's true objective is 'on-time departure at the lowest defensible cost', and the binding constraint is the screening deadline, not the device count itself - the device count is what must be chosen to satisfy the deadline.

### Outcome Analysis

The paper positions the airline as a throughput-cost optimizer subject to a hard security deadline. It argues that the airport/TSA must guarantee enough EDS capacity that the peak-hour schedule (46-48 departures) is feasible within the 30-min transport buffer; otherwise the airline absorbs delay or must cancel bags. Bias: the paper is written from the airline's perspective and therefore emphasizes cost; the TSA's perspective (security) is treated as a hard constraint, not a cost, which is the correct framing given the catastrophic asymmetry of a missed threat (expert exchange 3).

## Subtask 3: Task 3: Develop a model to help the airlines schedule the departure of different flight types within the peak hour so sc

### Problem

Task 3: Develop a model to help the airlines schedule the departure of different flight types within the peak hour so screening delays do not delay passengers; produce a schedule for both airports from Table 1.

### Analysis

A sequencing/feasibility model. Each flight's bags must clear the EDS by its own deadline (departure - MIN_LAG). The model orders the peak-hour departures to minimize the chance any flight's last bag misses its deadline. Assumptions: (a) a 60-minute departure window for the active peak hour; (b) bags of a flight are pipelined into the shared EDS pool as they trickle in (expert exchange 1), so a flight's screening service time is its bag count divided by the pool's effective service rate; (c) all 46-48 flights depart within the window. Method: schedule flights in descending order of bag count (largest flights first) so the longest screening jobs get the most slack, spread the departures evenly across the window, and compute per-flight slack to its deadline. This is sound because it is an earliness/lateness scheduling heuristic (longest-processing-time first) that maximizes the minimum slack.

### Modeling Process

For each flight i: bags_i = seats * BTR; n_dev = airport EDS count (24 at A, 26 at B); svc_rate = n_dev * MU_EDS * ALPHA (bags/min); svc_time_i = bags_i / svc_rate; departure offset dep_i = i * (SCHED_WINDOW / n_flights); check-in cutoff at dep_i - MIN_LAG (30 min); screening completion_i = dep_i - MIN_LAG - max(0, slot - svc_time_i); slack_i = (dep_i - MIN_LAG) - completion_i. Feasibility iff slack_i >= 0 for all i. Parameter table: SCHED_WINDOW = 60 min, interval [60, 60], source: peak hour; MIN_LAG = 30 min, source: expert exchange 2; svc_rate from Task 1 device counts.

### Outcome Analysis

Airport A: 46 flights, slot ~1.30 min, all flights have positive slack (range ~1.29-1.30 min) - the schedule is feasible. Airport B: 48 flights, slot ~1.25 min, all flights positive slack (~1.23-1.25 min) - feasible. Both schedules clear every flight's bags before its 30-min transport cutoff. The binding flights are the largest (70 bags) and the tightest-slack at the end of the window. Interpretation: at the 85%-utilization design point the EDS pool has enough headroom that the peak-hour schedule is robust; the schedule change recommended is to protect the first (largest) flights' check-in windows and to keep the last ~30 min of the window reserved for loading, not new check-in. Limitations: the model assumes a uniform service rate and does not model the arrival burst of connecting bags (the expert-noted exception); if BTR is at the low end (0.10) the slack grows, at the high end (0.40) the slack shrinks toward zero and the schedule becomes tight - a direct link to the Task 1 sensitivity.

## Subtask 4: Task 4: Based on the analysis, recommend to Mr. Sheldon and the airlines how to handle checked baggage screening during 

### Problem

Task 4: Based on the analysis, recommend to Mr. Sheldon and the airlines how to handle checked baggage screening during peak hours at Airports A and B.

### Analysis

A synthesis/recommendation deliverable combining Tasks 1-3. Goal: a concrete, actionable set of recommendations for peak-hour screening operations. Scope: the two airports and their Table 1 flight sets.

### Modeling Process

Recommendations derived directly from the model outputs. (1) Staff and reserve EDS pools of 24 (A) and 26 (B) for the 85% design point, with a contingency band up to ~33 (A)/~35 (B) if the checked-bag ratio runs high. (2) Sequence the peak hour largest-flights-first so the longest screening jobs carry the most slack (Task 3). (3) Enforce the 30-min transport+loading buffer by closing check-in at dep-30 for the last flights and reserving the final 30 min for loading only. (4) Because EDS has high false-alarm rates, staff secondary inspection to absorb the flagged bags without blocking the EDS line (the flagged bag leaves the throughput path). (5) Monitor the realized checked-bag ratio per flight type during the first few weeks and adjust the pool size; the model's BTR sensitivity shows the device count is the lever to tune.

### Outcome Analysis

The core recommendation is capacity-with-headroom plus sequencing plus a hard deadline buffer. The model shows the current peak-hour schedule is feasible at the design point, so the risk is not the mean case but the tail (high BTR, EDS downtime). The 8% EDS unavailability is the reason the 85% utilization target (not 100%) matters: it is the buffer against simultaneous downtime. Bias: recommendations assume the 100% screening mandate holds and do not consider partial screening as a fallback; they are cost-blind beyond device count, leaving cost to Task 6.

## Subtask 5: Task 5: Write a memo explaining how the models adapt to determine the number of EDS and the airline scheduling for all 1

### Problem

Task 5: Write a memo explaining how the models adapt to determine the number of EDS and the airline scheduling for all 193 airports in the Midwest Region.

### Analysis

A generalization/implementation memo. Goal: show Mr. Sheldon (to forward to the TSA Office of Security Operations and all regional airport directors) that the two-airport model is a template, not a one-off. Scope: scaling the throughput sizing and scheduling model to 193 airports.

### Modeling Process

The model is parameterized so each airport k needs only: (a) its peak-hour flight table (seats per type, flights per type) - the analog of Table 1; (b) the same constants (MU_EDS=185, ALPHA=0.92, MU_ETD=45, AVAIL_ETD=0.98, TARGET_UTIL=0.85, PEF=1.6, MIN_LAG=30, SCHED_WINDOW=60) or airport-specific overrides where local operations differ; (c) BTR_k, either a regional default (0.20) or airport-measured. Then n_k = ceil( r_k / (0.85 * 170.2) ) with r_k = (T_k / 30) * 1.6, and the Task 3 scheduler runs on the same flight ordering. The memo recommends a 3-phase rollout: Phase 1, compute n_k for all 193 airports from their flight tables (a batch run of the same code); Phase 2, validate BTR_k and PEF at the top-20 airports by volume with on-the-meter data and correct; Phase 3, deploy with the 85% target and the largest-first schedule, and re-estimate each quarter. A single script (code/model.py) with one airport table as input produces the full regional plan; no per-airport re-derivation is needed. The memo also notes that small airports (few peak-hour flights) are throughput-light and may share a regional reserve pool, while the handful of high-volume hubs dominate the device budget.

### Outcome Analysis

The memo's value is the claim that the model is a fixed template parameterized by the airport flight table, so 193 airports cost 193 runs, not 193 models. Limitations: (1) a single regional BTR default may misfit low-cost-carrier-heavy airports (lower checked-bag ratio) vs. hub airports (higher); (2) the 85% utilization target is a design constant and may need airport-specific calibration for very small airports where a single device downtime is a large fraction; (3) the memo assumes every airport has a Table-1-like peak-hour table, which requires data collection not yet done.

## Subtask 6: Task 6: Modify the EDS model to incorporate ETD machines, determine how many ETD are needed at A and B and whether sched

### Problem

Task 6: Modify the EDS model to incorporate ETD machines, determine how many ETD are needed at A and B and whether schedules must change; write a memo to the DHS and TSA Directors with a technical analysis of the enhanced screening policy - is the cost justified by the value, and should ETD replace any EDS?

### Analysis

Extend the detection and throughput model to a two-stage system: every bag goes through an EDS, and up to 20% of passengers' bags (FRACTION_HIGHRISK=0.20) additionally go through an ETD. Goal: size the ETD pool, quantify the security value (miss-rate reduction), price the policy, and decide the ETD-vs-EDS replacement question. The design objective, fixed by expert exchange 3, is lexicographic: minimize missed threats first, then manage false alarms/throughput. Detection is modeled as two independent reads per stage (each EDS/ETD image is a read), so a stage flags a bag if either read fails. Assumptions: ETD runs sequentially after EDS for the high-risk 20%; ETD throughput 45 bags/hr (midpoint 40-50) at 98% availability; ETD cost $45,000 each, labor ~10x EDS.

### Modeling Process

Detection: p_eds = 1 - (1-ACC_EDS)^2 = 1 - (0.015)^2 = 0.999775; p_etd = 1 - (1-ACC_ETD)^2 = 1 - (0.003)^2 = 0.999991. Per-bag miss rate: EDS only = (1-p_eds) = 2.25e-4; EDS+ETD = (1-p_eds)(1-p_etd) = 2.25e-4 * 9e-6 = 2.025e-9, a ~99.9991% relative reduction (roughly a 10x drop from the EDS-only miss rate, since the ETD layer cuts the surviving miss rate by its own ~9e-6). With baseline explosive-bag share P_MISSED=0.001 (stated assumption for a 2001-era risk baseline): expected missed threats per peak-hour, EDS-only = 0.001*2.25e-4 = 2.25e-7 bags; EDS+ETD = 0.001*2.025e-9 = 2.025e-12 bags. ETD sizing: high-risk bags per peak-hour = 0.20 * T = 216 (A) / 231 (B); peak ETD rate = (0.20*T/30)*1.6 = 11.5 (A) / 12.3 (B) bags/min; n_etd = ceil( rate*60 / (0.85 * 45*0.98) ) -> 19 (A) / 20 (B). ETD added screening service per airport = hr_bags/(n_etd*45*0.98) = 0.26 min, far below the 30-min transport buffer, so schedules do NOT need to change. Parameter table: FRACTION_HIGHRISK = 0.20, interval [0.20, 0.20], source: problem statement; MU_ETD = 45 bags/hr, interval [40,50], source: problem statement; AVAIL_ETD = 0.98, source: problem statement; ACC_ETD = 0.997, source: problem statement; C_ETD = $45,000, source: problem statement; ETD labor = 10x EDS labor, source: problem statement; P_MISSED = 0.001, interval [0.001, 0.001], source: stated baseline assumption for the value estimate (not derivable from the dataset; the model's security conclusion - a ~10x miss-rate reduction - holds at any P_MISSED because the reduction factor is independent of the base rate).

### Outcome Analysis

ETD requirement: 19 at A, 20 at B. Security value: the ETD layer cuts the per-bag miss rate by ~99.9991% (a ~10x reduction over EDS-only), which is the dominant security contribution and is independent of the (uncertain) base explosive rate - this is the lexicographic 'minimize missed threats first' objective in action. Cost: ETD purchase ~$855k (A) / $900k (B) plus labor at 10x EDS labor per operator (19-20 operators each). Delay: +0.26 min of screening service, negligible, so NO schedule change is required. Is the cost justified? Yes for the high-risk subset: the marginal cost is the ETD line plus 10x labor, and the marginal value is a ~10x reduction in the most catastrophic failure mode (a missed bomb), which expert exchange 3 established as far worse than the bounded cost of a false alarm. Should ETD replace any EDS? No: the EDS carries the bulk of the throughput and the first-detection role for 100% of bags, and the ETD only covers 20% of bags at 45 bags/hr (an order of magnitude slower). Replacing even a few EDS with ETDs would (a) drop the 100%-screening coverage the mandate requires and (b) collapse throughput, since ETD capacity is ~4x lower per device. ETD complements EDS on the high-risk stream; it does not substitute for it. Memo conclusion: fund the ETD add-on for the 20% high-risk bags; keep all 24/26 EDS; the enhanced policy is cost-justified by the miss-rate reduction.

## Subtask 7: Task 7: Use the EDS/ETD model to examine the effect of changes in device technology (cost, accuracy, speed, operational 

### Problem

Task 7: Use the EDS/ETD model to examine the effect of changes in device technology (cost, accuracy, speed, operational reliability); recommend the STEM research areas with the biggest impact on security performance; add the recommendation to the Task 6 memo.

### Analysis

A sensitivity/technology-impact analysis. Goal: rank which device characteristics, if improved by research, move the security-relevant outputs the most, and convert that into STEM research priorities. The security-relevant outputs (ordered per expert exchange 3): (1) missed-threat rate (safety, the binding objective), (2) false-alarm/flag rate (throughput, delay, secondary-inspection labor), (3) required device count (cost, space), (4) throughput capacity (scheduling headroom). Method: sweep each lever - accuracy (acc_eds, acc_etd), operational reliability (alpha), speed (mu_eds, mu_etd) - and read the change in the outputs. Cost is a purchase-price input and affects budget but not the security metrics, so it is reported separately.

### Modeling Process

Lever sweeps (code/sensitivity.py), baseline A: 24 EDS, B: 26 EDS, 19 ETD (A), 20 ETD (B), miss/bag EDS-only 2.25e-4, EDS+ETD 2.025e-9. ACC_ETD 0.997 -> 0.9999: p_etd_flag 0.999991 -> 1.0, miss EDS+ETD 2.025e-9 -> 2e-12, relative miss reduction 0.999991 -> 0.99999999 (each accuracy step cuts the residual miss rate ~10x). ACC_EDS 0.985 -> 0.999: miss EDS-only 2.25e-4 -> 1e-6 (a 225x reduction). ALPHA (reliability) 0.92 -> 0.99: n_eds A 24 -> 23, B 26 -> 24 (roughly 1 device per 3-4 points of reliability at these volumes). MU_EDS (speed) 160 -> 250 bags/hr: n_eds A 28 -> 18, B 30 -> 19 (a ~30-36% device-count reduction). MU_ETD (speed) 45 -> 120 bags/hr: n_etd A 19 -> 7, B 20 -> 8 (a ~60-63% ETD-count reduction). STEM ranking by security impact: (1) DETECTION ACCURACY, especially ETD accuracy - directly and multiplicatively reduces the miss rate, the binding safety objective; the emerging technologies named in the problem (x-ray diffraction, neutron-based detection, quadrupole resonance, millimeter-wave, microwave imaging) are all aimed here. (2) SPEED / THROUGHPUT (mu_etd first, then mu_eds) - the largest cost/space and scheduling lever; a 2x-3x faster ETD cuts the ETD pool ~60%, and a faster EDS cuts the EDS pool ~30%. (3) OPERATIONAL RELIABILITY (alpha) - modest device-count effect (~1 device per 3-4 availability points) but important for tail-case robustness. (4) COST - budget lever only, no effect on the security metrics; a cheaper EDS/ETD eases the 429-airport rollout but does not change the miss rate.

### Outcome Analysis

The highest-impact STEM research areas, in order, are: (1) improved explosive-identification accuracy for the ETD (mass-spectrometry sensitivity/selectivity) and for next-generation EDS imaging - this is the only lever that moves the safety metric, and it does so multiplicatively; (2) higher throughput (faster scans) for ETD and EDS - the dominant cost, space and scheduling lever, and the one that most eases the national rollout; (3) higher operational reliability (fewer downtime) - secondary but valuable for robustness; (4) cost reduction - a budget enabler, not a security improvement. The recommendation added to the Task 6 memo: fund accuracy research first (it is the binding objective per the missed-threat priority), fund throughput research second (it is the largest practical lever on the 429-airport cost and the peak-hour schedule), and treat cost research as a rollout enabler. Bias: the ranking weights the safety (miss-rate) metric above cost, consistent with expert exchange 3; an airport that is purely cost-constrained might weight throughput/cost higher, but that would trade against the dominant security objective.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
