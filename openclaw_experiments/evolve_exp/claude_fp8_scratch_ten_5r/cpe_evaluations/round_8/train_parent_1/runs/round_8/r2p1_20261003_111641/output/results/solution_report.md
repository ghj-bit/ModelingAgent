# Solution

## Subtask 1: Task 1: Develop a model to determine the number of EDS machines required at Airports A and B, state the assumptions, and

### Problem

Task 1: Develop a model to determine the number of EDS machines required at Airports A and B, state the assumptions, and recommend a number using the data in Table 1 of the Technical Information Sheet.

### Analysis

The dominant operational behavior (established first, per the expert) is that checked bags reach the screening line as a time-distributed, flight-correlated arrival stream: each flight's bags are unloaded and delivered over a pre-screening window (bag drop, unload, belt transport), so the load is bursty per flight but the instantaneous arrival rate stays within ~1.6x the hourly mean, not a single simultaneous batch. The binding deadline is the bag-acceptance cutoff, ~30 minutes before departure: a flight's bags must clear by that cutoff. Because the line is a continuously fed pipeline that drains each flight's bags before its cutoff, the governing sizing constraint is the peak-hour volume against hourly line capacity, not a sub-minute spike. Secondary inspection (the flagged share of bags) is modeled as an added cycle-time penalty on the line. The 2% daily flight cancellation is absorbed as capacity slack. The method is sound because it sizes on the volume the line must actually move in the hour, funds the per-flight lumps with an explicit surge buffer, and uses a target utilization below 100% so the line is not saturated at its rated maximum.

### Modeling Process

Inputs from Table 1: Airport A = 46 flights, 5396 seats; Airport B = 48 flights, 5781 seats (8 flight types, seats 34-350).

Empirical parameter table (name = value, interval [a,b], source):
  bag_yield = 0.65, [0.5,0.8], expert exchange 2 (checked bags per passenger)
  occupancy = 0.85, [0.80,0.95], model assumption within exchange-2 anchor (70-130 bags per 130-180-seat narrowbody)
  eds_cycle_s = 20, [17,23], expert exchange 3 (start-to-finish per-bag machine cycle)
  eds_availability = 0.92, [0.92,0.92], problem statement
  flag_rate = 0.20, [0.10,0.30], expert exchange 4 (share sent to secondary inspection)
  secondary_clear_s = 120, [60,180], expert exchange 5 (per flagged bag)
  cutoff_min = 30, [30,45], expert exchange 6 (bag-acceptance cutoff before departure)
  pre_screen_min = 90, [60,120], model assumption (bag drop + unload + belt delivery window)
  surge_buffer = 1.15, [1.10,1.35], model assumption funding the per-flight lumps + cancel slack
  util_target = 0.90, [0.85,0.95], model assumption (design utilization)
  cancel_rate = 0.02, [0.02,0.02], problem statement

Formulas:
  bags_per_flight(seats) = occupancy * bag_yield * seats
  total_bags_peak = sum over flights of bags_per_flight
  cap_per_machine_h = eds_availability * 3600 / eds_cycle_s  (primary)
  eff_cap_per_machine_h = cap_per_machine_h * (1 - flag_rate * secondary_clear_s/3600)  (secondary penalty)
     = 0.92*3600/20 = 165.6; with flag_rate 0.20 -> 164.5 bags/h
  n_eds = ceil( total_bags_peak / (eff_cap_per_machine_h * util_target) * surge_buffer )

Demand profile: each flight's bags enter the line as a linear ramp over pre_screen_min ending at its departure; the superposition gives the per-minute arrival curve (peak/mean ratio 1.57 for A, 1.54 for B).

Results: Airport A: total_bags_peak = 2981, n_eds = 25 (hourly view 21, x1.15 buffer). Airport B: total_bags_peak = 3194, n_eds = 26 (hourly view 22, x1.15 buffer). Design utilization 0.72 (A) and 0.75 (B); the peak minute uses 1.12x of the fleet's per-minute capacity, within the surge buffer.

### Outcome Analysis

Recommended: 25 EDS machines at Airport A and 26 at Airport B. Results are robust: bag_yield 0.5->0.8 moves the count 19/20 to 29/32; eds_cycle_s 17->23 s moves 21/22 to 28/29; surge_buffer 1.10->1.35 moves 24/25 to 29/30; flag_rate 0.10->0.30 leaves the count unchanged (the secondary penalty is small relative to the buffer). The recommendation sits in the central band of these ranges. Limitations and biases: the model sizes on the peak-hour mean volume and assumes a smooth ramp within the hour; if flights cluster more tightly in practice (higher peak/mean), more machines or a larger buffer are needed. It treats all flights as equally likely to be active and folds the 2% cancellation into the buffer rather than simulating it. The 10-ton footprint and installation cost are not modeled as a binding constraint here (space is assumed available at these two large facilities); that is where the 25-26 figure could be pushed up in a space-constrained airport. Slightly conservative because it uses the upper end of the bag_yield range's center (0.65) and a 15% surge buffer.

## Subtask 2: Task 2: A one-page position paper describing the security-related objectives of the airlines and the constraints they mu

### Problem

Task 2: A one-page position paper describing the security-related objectives of the airlines and the constraints they must work within for the flight sets in Table 1.

### Analysis

This is an analysis of objectives vs. constraints, not a new computation. It is grounded in the same operating logic established for Task 1 (the bag-acceptance cutoff is the binding security deadline) and in the two airports' flight mixes from Table 1: Airport A is dominated by type-5 (142-seat, 19 flights) plus 10 small type-1 (34-seat) flights; Airport B is more evenly spread with more mid-size and widebody (type-6,7,8) flights. The objectives are framed from the airline/airport perspective the expert grounded (keep departures on time, keep bags with flights, manage labor and cost), and the constraints are the federal mandate, the device physics, the labor and space/funding limits, and the flight-mix data.

### Modeling Process

Objectives (airlines): (1) 100% screened checked bags with no missed departure - every flight departs with its bags cleared by the bag-acceptance cutoff; (2) minimize passenger delay and missed connections from screening wait; (3) minimize operating cost (device count, installation, labor) subject to meeting (1); (4) maximize on-time performance across the peak hour; (5) maintain a security posture that satisfies the federal mandate and TSA risk-based policy.

Constraints: (a) Federal mandate - 100% of checked bags screened by EDS by the compliance date; (b) Device throughput - each EDS examines 160-210 bags/hour and is operational 92% of the time, so effective capacity is ~165 bags/h per machine before secondary review; (c) Labor - one operator per EDS line; secondary inspection of ~20% of bags adds ~2 min of staff time per flagged bag, a major labor driver; (d) Space and funds - ~8-ton machines and several thousand dollars to install per airport bound the count at each facility; (e) Cutoff - bags must clear ~30 min before departure (30-45 min), compressing the screening window; (f) Flight mix - Table 1 volumes: Airport A 46 flights / 5396 seats, Airport B 48 flights / 5781 seats, with a long tail of small 34-46 seat flights (24 of A's 46, 14 of B's 48) that generate few bags each but many connection-sensitive departures; (g) ETD is not federally certified, so it cannot by itself satisfy the mandate and must supplement, not replace, EDS.

### Outcome Analysis

The paper's argument: airlines must treat the bag-acceptance cutoff, not the departure time, as the real deadline, because it is where the security work must finish; a missed cutoff means a bag held to a later flight (the passenger flies, the bag follows), which is accepted practice but degrades the customer experience and incurs handling cost. Given the device physics, the peak-hour volume at each airport (≈3000 checked bags) requires roughly 20-26 EDS machines to keep the line feasible; buying fewer saves capital but risks cutoff misses and cascading delays. The small-flight tail matters: many short-notice, connection-sensitive departures mean that a screening backlog is most damaging to exactly the flights with the least schedule slack, so airlines should protect screening capacity for peak-hour connection flights. Limitation: the paper does not price the trade-off (no explicit cost-minimization objective function is solved); it is a qualitative position that the Task 1/3 models can quantify.

## Subtask 3: Task 3: Develop a model to help the airlines schedule the departure of different flight types within the peak hour so th

### Problem

Task 3: Develop a model to help the airlines schedule the departure of different flight types within the peak hour so that security screening does not delay passengers, and produce a schedule for Airports A and B using Table 1.

### Analysis

The scheduling problem is to assign each flight a departure time within the peak hour so that its checked bags clear by its bag-acceptance cutoff (30 min before departure) and the superposition of arrival ramps does not exceed the line's per-minute capacity. The mechanism (from the expert): bags arrive as per-flight lumps tied to the flight's arrival; the binding deadline is the cutoff; when the line is at risk the standard response is to stagger and divert, not to delay the departure. The model spreads departures so the earliest-cutoff / largest-bag flights get the earliest slots (they have the most screening work and the least tolerance for a backlog), and verifies the peak-minute load against fleet capacity.

### Modeling Process

Decision variable: departure time dep_i in [30, 60] (minutes into the peak hour) for each flight i; the first departure is no earlier than the cutoff (30 min) so every flight's bags screen inside the hour. Constraints: (1) dep_i >= 30 for all i; (2) bags of flight i clear by dep_i - 30, i.e. screen_time_i = bags_i / per_min_capacity must be <= (dep_i - 30) - delivery_start, which holds with large margin because screen_time_i <= ~3 min; (3) the superposition of the per-flight arrival ramps at any minute does not exceed per_min_capacity (verified: peak minute uses 1.12x the mean-minute capacity, absorbed by the surge buffer and the 90-min pre-screening ramp).

Rule: order flights by descending bag count (largest first) and assign departures evenly spaced from 30 to 60 min (spacing = 30/N): dep_i = 30 + (rank_i + 1)*(30/N). Airport A: N=46, spacing 0.65 min. Airport B: N=48, spacing 0.625 min. per_min_capacity = n_eds * eff_cap_per_machine_h / 60 = 25*164.5/60 = 68.5 bags/min (A); 26*164.5/60 = 71.3 (B).

Schedule (Airport A, first / representative / last): t=30.7 type-8 350-seat (193 bags, cutoff 0.7, screen 2.8 min); mid hour types 3-6 mid-size; t=60.0 type-1 34-seat (19 bags, cutoff 30.0, screen 0.27 min). Airport B analogous: first t=30.6 type-8, last t=60.0 type-1. The full 46/48-flight schedules are in results/model_output.json.

### Outcome Analysis

The schedule staggers all departures across the back half of the peak hour so that (i) no flight has a negative cutoff (all bags clear inside the hour), (ii) the largest flights (most bags, least slack) depart earliest and their screening finishes earliest, and (iii) the per-minute screening load stays near the hourly mean, keeping the line feasible. Max screen time is ~2.8 min (the 350-seat flight) against a ~28-min screening window, so there is ample margin; the design is robust to the arrival lumps. Limitations: it assumes departures can be shifted within [30,60]; real slot coordination with air-traffic and gate availability is outside the model. It schedules on expected (non-cancelled) flights; a cancelled flight simply frees capacity. The even-spacing rule is a feasible, near-optimal heuristic; an exact optimization (minimizing expected cutoff-miss or passenger wait) would give marginal refinements but the even stagger already keeps utilization in the 70-80% band.

## Subtask 4: Task 4: Based on the analysis, recommend to Mr. Sheldon and the airlines what to do about checked-baggage screening for 

### Problem

Task 4: Based on the analysis, recommend to Mr. Sheldon and the airlines what to do about checked-baggage screening for peak-hour flights at the two airports.

### Analysis

This is a synthesis recommendation built on Tasks 1-3: the device counts, the schedule, and the operational levers the expert identified for when the line is at risk (divert to overflow, hold bags to a later flight, triage by risk/cutoff, add labor, loosen thresholds; delay departure only as a last resort). The recommendation is to buy the recommended EDS count, stagger departures as in Task 3, and stand up the overflow/hold-bag response as the contingency rather than defaulting to departure delays.

### Modeling Process

Recommendations: (1) Purchase and install 25 EDS machines at Airport A and 26 at Airport B (Task 1), sized for the peak-hour volume with a 15% surge buffer and 90% design utilization, leaving room to absorb the 2% daily cancellations and late-arriving bags. (2) Adopt the Task 3 staggered departure schedule: departures in [30,60] of the peak hour, largest-bag flights first, so no flight's bags miss its bag-acceptance cutoff and the line runs at a steady ~70-75% utilization rather than in spikes. (3) Stand up the peak-hour contingency playbook: divert bags to an overflow EDS/second line, hold a missed-cutoff bag to the next flight (passenger flies, bag follows), triage screening by risk and by earliest cutoff, and add temporary screening labor rather than holding flights. Delaying a departure is a last resort because it cascades through the day. (4) Protect capacity for the small-flight tail: at both airports a large share of flights are 34-85 seat (24 of 46 at A, 14 of 48 at B) that are connection-sensitive; keep the earliest, most slack-free slots' screening protected. (5) Monitor the flag rate: at ~20% secondary-inspection share the secondary-review labor is the dominant labor cost and the main source of variability; tuning EDS alarm thresholds (tighten for risk, loosen for throughput) is the fastest lever to manage peak-hour load without new machines.

### Outcome Analysis

These recommendations keep both airports feasible with margin: design utilization 0.72 (A) and 0.75 (B), peak-minute load 1.12-1.13x the mean-minute capacity, all inside the surge buffer. The hold-bag/overflow response means a bad day (more bags, higher flag rate, a machine down for the 8% of the time) degrades gracefully into a few held bags rather than departure delays. Biases/limits: the recommendation assumes the space and capital to install 25-26 machines at each airport; a space-constrained terminal would need fewer, denser machines plus more overflow labor, which trades capital for labor and raises the risk of cutoff misses. It does not model inter-connection delays at other airports.

## Subtask 5: Task 5: Write a memo explaining how the models can be adapted to determine the number of EDS and the airline scheduling 

### Problem

Task 5: Write a memo explaining how the models can be adapted to determine the number of EDS and the airline scheduling for all 193 airports in the Midwest Region.

### Analysis

The adaptation is a parameterization, not a re-derivation: the same sizing and scheduling logic applies to any airport once its peak-hour flight mix is known. The memo describes the general formula, the data needed per airport, and the scaling/adjustment rules (size class, space limits, ETD eligibility, multi-terminal effects).

### Modeling Process

For any airport k with peak-hour flight mix {seats_j, n_j}: bags_peak_k = occupancy*bag_yield*sum_j(seats_j*n_j). n_eds_k = ceil( bags_peak_k / (eff_cap_per_machine_h*util_target) * surge_buffer_k ), where surge_buffer_k is raised for airports with tight flight clustering, limited overflow space, or high-risk profiles, and lowered where the line is already over-deployed. eff_cap_per_machine_h and util_target are the same network-wide (device physics and policy do not change by airport). Scheduling: the same [cutoff, 60] even-stagger rule with dep = cutoff + (rank+1)*(60-cutoff)/N_k, ordered by descending bag count. Scaling rules in the memo: (1) size the surge buffer by airport class - large hub (193-airport Midwest includes regional and small fields): hubs 1.20-1.35, medium 1.15, small 1.10, because small airports have less overflow room and fewer flights to absorb a lump; (2) space/funding bound: cap n_eds_k by the terminal's available footprint and budget; where the bound binds, shift the deficit to overflow labor and a hold-bag policy; (3) multi-terminal airports sum the per-terminal peak-hour volumes but do not sum machines across terminals (a machine serves one terminal's line); (4) ETD-eligible high-risk airports additionally apply the Task 6 ETD count on the mandated dual-screen share. The memo provides a per-airport worksheet: input the Table-1-equivalent flight mix, run the formula, read off n_eds_k and the schedule; the 193-airport plan is 193 instances of the same computation.

### Outcome Analysis

The adaptation is direct and reproducible: the model is fully parameterized by the peak-hour flight mix, so the 193-airport plan is a batch of 193 evaluations, not 193 new models. The only airport-specific judgment is the surge buffer (set by size class and overflow space) and the space/funding cap, both documented in the memo as decision rules. Limitations: it assumes each airport's peak-hour mix is stationary and well-represented by a single Table-1-equivalent snapshot; seasonal or day-type variation would need a peak-of-distributions input. It does not model regional sharing of overflow capacity (a bag from a small airport cannot easily divert to a hub's line), so small airports are sized conservatively. The memo's decision rules (buffer by class, cap by space) are the main places a regional director would adjust the numbers to local reality.

## Subtask 6: Task 6: Modify the EDS models to incorporate ETD machines, determine how many ETDs are needed at Airports A and B and wh

### Problem

Task 6: Modify the EDS models to incorporate ETD machines, determine how many ETDs are needed at Airports A and B and whether the schedules change, and write a memo (to the Homeland Security and TSA Directors) with a technical analysis of the enhanced screening policy - is the cost justified by the value, and should ETDs replace any EDS devices?

### Analysis

The expert established the ETD as a separate, slower, labor-intensive secondary station in series with the EDS, handling only the mandated dual-screened share (up to 20% of passengers' bags for higher-risk flights; routine share 2-5%). The model adds an ETD capacity constraint on that share, and tests whether the ETS stage changes the departure schedule. The cost-benefit is the added detection (EDS 98.5% -> combined 99.996% on dual-screened bags) against the added capital and ~10x labor cost.

### Modeling Process

ETD inputs: etd_cycle_s = 75, [60,120], expert exchange 8; etd_availability = 0.98 (problem); etd_accuracy = 0.997 (problem); dual_share = 0.20, [0.03,0.20], expert exchange 9 (mandated ceiling) with routine 0.03; etd cost $45,000; labor 10x the EDS (problem).
  etd_bags = total_bags_peak * dual_share
  cap_per_etd_h = etd_availability*3600/etd_cycle_s = 0.98*3600/75 = 47 bags/h
  n_etd = ceil( etd_bags / (cap_per_etd_h*util_target) * surge_buffer )

Results (dual_share 0.20, mandated): Airport A etd_bags=596, n_etd=18. Airport B etd_bags=639, n_etd=19. Sensitivity: dual_share 0.03->4, 0.05->5, 0.10->10, 0.20->18/19; etd_cycle_s 60->14/15, 75->18/19, 120->27/29.

Schedule effect: the ETD stage is serial and adds ~75 s per dual-screened bag, but it acts only on the 20% dual share and runs as a separate station; it does not add to the EDS line's per-minute load, so the Task 3 departure schedule is unchanged. The dual-screened bags are a subset already cleared by the EDS; the ETD is a downstream checkpoint. The only schedule interaction is that dual-screened bags need ~1 min of extra handling before reconciliation, which is inside the existing screening-window margin. Hence: no change to the departure schedule is required.

Cost-benefit (per airport, mandated 20%): EDS capex 25-26 machines x $1M = $25-26M; ETD capex 18-19 x $45k = $0.81-0.86M; total ~$25.8M (A), $26.9M (B). Detection on dual-screened bags rises from 98.5% (EDS alone) to 1-(0.015*0.003)=99.996%, a ~400x reduction in the miss rate on that subset (1.5% -> 0.004%). Labor: ETD labor is 10x the EDS per machine-hour, and the 18-19 ETDs each need an operator plus swabbing staff, so the recurring labor cost of the ETD stage is the dominant ongoing expense, not the $45k capital.

Should ETDs replace EDS? No. The ETD is not federally certified and cannot by itself satisfy the 100% EDS mandate; it is a complement. Replacing an EDS (165 bags/h, 98.5%) with an ETD (47 bags/h, 99.7%) would cut throughput ~3.5x and drop certification coverage, so no EDS is replaced. ETDs are added on top of the EDS count for the mandated high-risk share.

### Outcome Analysis

Recommended: 18 ETD machines at Airport A and 19 at Airport B for the mandated 20% dual-screen policy; the departure schedule is unchanged. The cost is justified in a risk-based sense only for the targeted high-risk flights: the 400x miss-rate reduction on the dual-screened subset is valuable where a miss is catastrophic, but at ~$0.85M capital plus 10x labor it is not justified to apply at the 20% ceiling to every flight - the routine share (2-5%, needing only 4-5 ETDs) captures most of the value at a fraction of the cost. The memo's recommendation is to apply ETD at the mandated 20% to the specific high-risk flights the policy names, and at the routine 3-5% (4-5 ETDs) elsewhere, rather than 20% across the board. ETDs do not replace any EDS. Limitations: the 400x miss-rate figure is a point estimate from the stated accuracies and assumes the two devices' errors are independent (in practice some bags are missed by both for the same physical reason, so the combined improvement is somewhat less); the labor cost estimate uses the stated 10x multiple and is the largest source of uncertainty in the cost-benefit.

## Subtask 7: Task 7: Use the EDS/ETD model to examine the effect of changes in device technology, cost, accuracy, speed, and operatio

### Problem

Task 7: Use the EDS/ETD model to examine the effect of changes in device technology, cost, accuracy, speed, and operational reliability; recommend the STEM research areas with the biggest impact on security system performance; add the recommendation to the memo.

### Analysis

This is a sensitivity/leverage analysis: which device parameter, if improved by research, moves the system performance (machines needed, miss rate, cost) the most. The model is already parameterized on cycle time, accuracy, availability, cost, and dual_share, so the effect of each is a sweep. The STEM recommendation ranks the research levers by their effect on the binding constraints (throughput -> machine count, accuracy -> miss rate, reliability -> effective capacity, cost -> capital).

### Modeling Process

Leverage (from the model's sweeps): (1) Speed (cycle time) - eds_cycle_s 17->23 s moves the EDS count 21/22 -> 28/29 (~30% of the count); a 25% speed improvement (20s->15s) cuts the machine count by ~25%. This is the largest single lever on capital. etd_cycle_s 60->120 s moves the ETD count 14/15 -> 27/29 (~2x). (2) Operational reliability (availability) - the 92% EDS availability is a fixed ~8% throughput loss; improving 0.92->0.98 raises effective capacity ~6.5% and cuts the machine count by a comparable share; reliability is a cheaper lever than speed for a given gain. (3) Accuracy - eds_accuracy 98.5% and etd_accuracy 99.7% set the miss rate; raising EDS accuracy to 99.5% cuts the EDS-only miss rate by two-thirds and reduces the need for the ETD supplement; accuracy research has the largest effect on the security outcome (misses) per unit of effort, but the largest effect on machine count is speed. (4) Cost - a 20% EDS cost reduction (=$200k/machine) saves ~$5M per airport on the 25-26 machines; cost does not change performance, only the budget. (5) Dual-screen share / risk-targeting - lowering the mandated 20% to the routine 3-5% cuts the ETD count 18/19 -> 4/5 (~75%) at a modest miss-rate change, the largest lever on ETD cost.

STEM research recommendations (ranked by impact on system performance): (1) CT imaging speed / faster reconstruction - biggest effect on machine count (throughput is the binding capital constraint); (2) CT image accuracy / lower false-alarm rate - reduces the secondary-inspection labor (the dominant labor cost and main variability) and the miss rate simultaneously; a lower flag_rate (0.20 -> 0.10) would recover the secondary penalty and cut required labor; (3) Device reliability / uptime engineering - cheap, high-yield lever on effective capacity; (4) ETD throughput and miniaturization - faster swab-to-answer and a smaller footprint cut the ETD count and space need; (5) Cost reduction in CT detector and x-ray source manufacturing - lowers the capital barrier for the 193-airport rollout.

Added to the memo: prioritize R&D on (a) faster CT reconstruction and (b) lower false-alarm CT image analysis (both cut machine count and secondary labor), then (c) uptime/reliability, (d) ETD speed, (e) detector cost. This sequence targets the binding constraints first.

### Outcome Analysis

The model shows throughput (speed) and accuracy/false-alarm rate are the two highest-leverage research targets: speed cuts the machine count (the capital binding constraint) and a lower false-alarm rate cuts both the secondary labor cost and the miss rate. Reliability is a cheap, high-yield second lever. Cost reduction helps the rollout budget but not performance. The STEM recommendation is therefore to fund faster CT and better CT image analysis first, ETD miniaturization second, and detector cost reduction to enable the regional rollout. Limitations: the leverage is measured at the current operating point; if the system is re-tuned (e.g., ETD applied at the routine 3-5% share), the ETD-speed lever becomes more important and the EDS-speed lever less so. The accuracy gains assume independent device errors; correlated misses would blunt the combined-accuracy benefit. The cost figures use the stated per-device prices and do not model bulk-purchase or technology-curve discounts.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
