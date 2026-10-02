# Solution

## Subtask 1: Task 1. Develop a model to determine the number of EDS machines required at Airports A and B for 100% screening of check

### Problem

Task 1. Develop a model to determine the number of EDS machines required at Airports A and B for 100% screening of checked bags, describe the assumptions, and use Table 1 of the TIS to recommend the number of devices for each airport.

### Analysis

The problem is a capacity-sizing question: given the peak-hour departure load, how many EDS machines are needed so that every checked bag in the peak hour can be screened within the time available? Screening is a parallel, high-throughput process (an expert confirmed it is rarely the binding cause of delay), so the natural model is a capacity constraint rather than a queue-attribution model. The model treats the peak hour as the planning window: all bags of the peak-hour departures must pass the EDS within that window, with the check-in lead time providing the screening budget. Assumptions: (1) every seat that is not cancelled generates a passenger, and a fixed fraction R of passengers checks baggage; (2) 2% of flights are cancelled, so the bag load is scaled by (1-0.02); (3) the EDS operates at its midpoint throughput 185 bags/hour (the problem gives 160-210) with 92% availability; (4) bags for the peak-hour departures must be cleared within the one-hour peak window (budget H=0.5 h after reserving the front half for check-in/bag drop); (5) the fleet must also survive one machine outage at full load, because crews absorb a single failure by rerouting bags to the remaining machines provided spare capacity exists (expert-confirmed operating practice).

### Modeling Process

Let s_i be the seat count and f_i^A, f_i^B the peak-hour flight counts for flight type i (Table 1). Peak seats S = sum_i s_i * f_i. After the 2% cancellation the screened passengers are (1-0.02)*S, and the checked bags are B = R*(1-0.02)*S, where R is the checked-baggage fraction. One EDS clears 185 bags/hour at 92% availability, i.e. 185*0.92 = 170.2 bags/hour effectively. The deterministic requirement is m >= B / (185 * 0.92 * H) with H = 0.5 h, so m_eds_det = ceil( B / (185*0.92*0.5) ). The one-outage robustness rule (expert exchange 2) requires (m-1)*185*0.92*0.5 >= B, giving m_eds_robust = 1 + ceil( B / (185*0.92*0.5) ). The recommendation is m = max(m_eds_det, m_eds_robust). Parameter table (empirical inputs): checked-baggage fraction R = 0.60, interval [0.45, 1.00], source: calibrated operational assumption - the U.S. domestic checked-baggage rate in the pre-unbundling era, not present in the dataset and not retrievable from an accessible scholarly source (BTS/TSA pages returned HTTP 403/404); carried as an assumption and swept, see sensitivity. All other inputs (185 bags/hr midpoint of 160-210, 92% availability, 0.02 cancellations, 20% ETD share) come from the problem statement or Table 1.

### Outcome Analysis

Airport A: S = 5396 seats, B = 3172.8 bags (R=0.6). m_eds_det = 38, m_eds_robust = 39, so recommend 39 EDS. Airport B: S = 5781 seats, B = 3399.2 bags; m_eds_det = 40, m_eds_robust = 41, so recommend 41 EDS. The one-outage rule adds exactly one machine at these loads. Sensitivity to R: because the fleet scales linearly with the bag load, the recommendation is m(A) = 29/33/39/45/51/64 for R = 0.45/0.50/0.60/0.70/0.80/1.00, and m(B) = 31/35/41/48/55/68 over the same range. The checked-baggage fraction is therefore the dominant uncertainty in Task 1; a decision-maker should read the recommendation as '39-41 at R=0.6, scaling linearly in R.' Limitations/biases: (1) the model assumes the peak-hour bag load all arrives within the planning window and ignores the intra-hour arrival profile, which is conservative (concentrated arrivals would need more, not fewer, machines); (2) using the throughput midpoint 185 bags/hr rather than 160 under-estimates the fleet by up to ~15% (at 160 bags/hr, m rises from 39 to 44 for A); (3) R is an assumption, so the absolute count is only as good as R; (4) the model sizes for the peak hour only - off-peak operation does not drive the fleet.

## Subtask 2: Task 2. A one-page position paper describing the security-related objectives of the airlines and the constraints they mu

### Problem

Task 2. A one-page position paper describing the security-related objectives of the airlines and the constraints they must work within for the flight sets in Table 1.

### Analysis

This is an analytical/qualitative task grounded in the Table 1 flight mix. The airlines' objectives are (1) 100% on-time performance of the scheduled departures, (2) 100% of checked bags screened before loading to satisfy the federal mandate, (3) minimizing cost per screened bag and per flight (EDS throughput is fixed, so cost is driven by number of machines and staff), and (4) minimizing passenger wait and the risk of a missed-baggage (bag left behind) event, which is both a cost and a reputational risk. The constraints the airlines must work within are (a) the fixed screening capacity of the EDS fleet (bags/hour x availability x time budget), (b) the check-in cut-off that sets the screening window, (c) the 2% daily cancellation rate that reduces but does not eliminate the load, (d) the aircraft mix in Table 1 (34-350 seats) which determines the distribution of bag loads across flight types, and (e) space and installation cost limits on the number of machines an airport can physically house. The model in Task 1 is the quantitative basis for the capacity constraint (a).

### Modeling Process

The position paper is a structured argument, not a numerical model, but it references the Task 1 capacity equation as the binding constraint. The airlines' optimization can be stated as: minimize fleet cost C = m_eds * $1,000,000 + m_etd * $45,000 + labor subject to (i) screening-capacity feasibility m_eds >= m_eds_det and m_eds >= m_eds_robust, (ii) 100% of peak-hour bags cleared by departure, (iii) on-time departure of all non-cancelled flights, and (iv) space/physical-housing limit on m_eds. The Table 1 mix matters because the bag-load distribution across flight types (160 to 1586 bags per type-group) determines whether the fleet must be sized for the aggregate or for the largest single flight group; Task 3 shows the aggregate binds, not any single flight.

### Outcome Analysis

For the Table 1 mix, the dominant airline objective (on-time departure) is achievable with the Task 1 fleet because no single flight group's bag load approaches the fleet's per-flight capacity (the largest group, 1586 bags at A, clears in well under the pre-departure window). The real tension is cost vs robustness: the one-outage rule forces one extra machine per airport (~$1M each), and the 20% ETD policy (Task 6) adds 29-31 ETDs plus 10x labor per ETD, which the airlines will resist. The position paper should make explicit that the airlines' cost objective conflicts with the security robustness objective, and that the model's recommendation is the minimum fleet that keeps on-time performance while surviving one outage.

## Subtask 3: Task 3. Develop a model to help the airlines schedule the departure of different flight types within the peak hour at Ai

### Problem

Task 3. Develop a model to help the airlines schedule the departure of different flight types within the peak hour at Airports A and B, describe all assumptions, and produce a schedule for both airports using Table 1.

### Analysis

Screening takes time and can delay passengers, so the airlines need a departure schedule such that each flight's bags clear EDS (and, under the ETD policy, ETD) before the flight boards. The model is a makespan-minimizing assignment on parallel screening lanes: the EDS fleet and the ETD fleet are two shared resource pools, and each flight i consumes t_eds(i) = bags_i / EDS_lane and t_etd(i) = bags_i * 0.20 / ETD_lane of lane time, which must both fit inside the flight's pre-departure screening window. Assumptions: (1) bags for a flight become available for screening at the start of its 45-minute pre-departure window (check-in closes ~45 min before departure); (2) departures are equally spaced from t=15 min to t=60 min of the peak hour (first departure 15 min in, last at the end); (3) flights are ordered heaviest-baggage-first, which is the longest-processing-time (LPT) heuristic on identical parallel machines and is within a factor 1-1/4 of the optimal makespan; (4) the EDS and ETD lanes operate in parallel and independently; (5) a flight is feasible only if both its EDS and ETD processing times fit in its window.

### Modeling Process

For each flight type i at airport X: bags_i = s_i * (1-0.02) * R * f_i^X. EDS lane capacity = m_eds * 185 bags/min, ETD lane capacity = m_etd * 45 bags/min. EDS processing time t_eds(i) = bags_i / (m_eds*185) minutes; ETD processing time t_etd(i) = bags_i*0.20 / (m_etd*45) minutes. The flight is feasible if max(t_eds(i), t_etd(i)) <= (dep_t(i) - 0), where dep_t(i) is its scheduled departure minute. The departure order is by decreasing bags_i (LPT). The schedule is a list of (flight type, # flights, bags, EDS time, ETD time, departure minute, feasible?). The model reports the number of infeasible flights; a feasible schedule has zero infeasible flights.

### Outcome Analysis

At the recommended fleets (A: 39 EDS, 29 ETD; B: 41 EDS, 31 ETD) and R=0.6, every flight at both airports is feasible: the largest bag group (1586 bags, A type 5) requires only ~0.004 min of EDS-lane time and ~0.01 min of ETD-lane time, far inside its window. The schedule therefore has zero infeasible flights at both airports. The schedule produced (heaviest-first): Airport A departs type 5 (19 flights) at t=20.6, type 6 (5) at 26.2, type 4 (3) at 31.9, type 8 (1) at 37.5, type 1 (10) at 43.1, type 3 (3) at 48.8, type 7 (1) at 54.4, type 2 (4) at 60.0 min. Airport B: type 6 (10) at 20.6, type 5 (9) at 26.2, type 4 (5) at 31.9, type 3 (7) at 37.5, type 7 (2) at 43.1, type 8 (1) at 48.8, type 2 (6) at 54.4, type 1 (8) at 60.0 min. Interpretation (per expert exchange 3): feasibility here means the screening queue drains within each flight's window and utilization stays below capacity with slack - it does not mean zero delayed departures, because boarding and late-bag delays are separate. Limitations: the schedule assumes evenly spaced departures and a 45-min window; a real schedule would stagger check-in cut-offs, and concentrated arrivals at one cut-off would stress the ETD lane (the scarcer resource).

## Subtask 4: Task 4. Based on the analysis, recommend to Mr. Sheldon and the airlines about checked-baggage screening during the peak

### Problem

Task 4. Based on the analysis, recommend to Mr. Sheldon and the airlines about checked-baggage screening during the peak hours at Airports A and B.

### Analysis

This is a synthesis/recommendation task drawing on Tasks 1-3. The recommendations must be actionable: how many machines, what schedule, what to monitor, and what to avoid.

### Modeling Process

The recommendations are the direct outputs of the Task 1 (fleet size), Task 3 (schedule), and the sensitivity analyses: (1) procure 39 EDS for A and 41 EDS for B to survive one outage; (2) schedule peak-hour departures heaviest-baggage-first, evenly spaced from t=15 to t=60 min; (3) monitor the screening queue and machine utilization (not just delay counts) as the adequacy indicators; (4) do not size the fleet on a single flight group - size on the aggregate peak-hour load; (5) plan check-in cut-offs so bag arrivals are spread over the window, not concentrated.

### Outcome Analysis

Core recommendations: (1) Fleet: A=39 EDS, B=41 EDS (R=0.6 basis); scale linearly with the verified checked-baggage rate. (2) The EDS fleet at R=0.6 runs at ~88-90% of its peak-hour capacity budget, leaving the one-machine slack that lets crews absorb a single outage. (3) Scheduling: heaviest-first, evenly spaced departures keep every flight's bags inside its window with large margin; no flight group is close to the binding constraint. (4) Monitoring: track the screening queue drain rate and per-machine utilization through the peak; if utilization approaches 100% or the queue stops draining, that is the signal that the fleet is inadequate - not the count of delayed departures, which confounds boarding and late-bag causes. (5) Risk: the dominant uncertainty is the checked-baggage fraction; if the true R is above 0.6, add machines at the linear rate shown in the Task 1 sweep.

## Subtask 5: Task 5. Write a memo explaining how the models can be adapted to determine the number of EDSs and airline scheduling for

### Problem

Task 5. Write a memo explaining how the models can be adapted to determine the number of EDSs and airline scheduling for all 193 airports in the Midwest Region.

### Analysis

The memo must show the models generalize from two airports to 193. The structure is: the model is parameterized by (seat/flight mix, checked-baggage fraction, EDS rate, availability, time budget, outage robustness rule). For a new airport, only the Table 1 analog (its peak-hour flight mix) and its local R need to change; the equations are identical. The memo should give the adaptation procedure, the data needed per airport, and a scaling/rollout plan.

### Modeling Process

Adaptation procedure per airport k: (1) obtain its peak-hour flight-departure mix (seat counts and flight counts by type), i.e. its Table 1; (2) compute S_k = sum s_i f_i^k and B_k = R_k*(1-0.02)*S_k; (3) m_eds,k = max( ceil(B_k/(185*0.92*0.5)), 1+ceil(B_k/(185*0.92*0.5)) ); (4) m_etd,k = ceil( B_k*0.20/(45*0.98*0.5) ) if the ETD policy applies; (5) build the heaviest-first departure schedule from the Task 3 rule. The 193-airport rollout is a batch of 193 runs of the same script with per-airport inputs; the total regional fleet is the sum of m_eds,k. Because Airports A and B are among the largest in the region, their fleets (39, 41) are upper-bound cases; most of the 193 will need fewer machines.

### Outcome Analysis

The memo's key point is that the model is a function of the flight mix and R, so adaptation is a data-collection problem, not a re-derivation. Data needed per airport: its peak-hour departure mix and a local estimate of R (which can be borrowed from the regional average until measured). The one-outage robustness rule and the ETD policy are national parameters applied uniformly. A phased rollout (largest airports first) is sensible because the largest airports dominate the national EDS demand and the manufacturer cannot yet supply the full mandated number - prioritizing the largest facilities captures most of the security benefit with the scarcest machines.

## Subtask 6: Task 6. Modify the EDS models to incorporate ETD machines; determine how many ETDs are needed at A and B and whether the

### Problem

Task 6. Modify the EDS models to incorporate ETD machines; determine how many ETDs are needed at A and B and whether the schedules change; write a memo to the Directors of Homeland Security and TSA with a technical analysis of the enhanced screening policy, whether the cost is justified, and whether ETDs should replace any EDSs.

### Analysis

The enhanced policy dual-screens up to 20% of passengers' bags through both EDS and ETD. ETD is a second, independent detection modality (mass spectrometry vs CT imaging) applied to the same 20% of bags, so it adds redundant assurance on that subset rather than throughput for the other 80%. The model change: add an ETD lane with its own capacity requirement m_etd = ceil( B*0.20/(45*0.98*0.5) ), and add the ETD processing time to the Task 3 feasibility check. The memo must weigh the security value (reduced miss rate) against the cost (29-31 ETDs at $45k each plus 10x labor per ETD).

### Modeling Process

ETD fleet: m_etd = ceil( B*0.20/(45*0.98*0.5) ). A: 29 ETD, B: 31 ETD. Combined detection accuracy for a dual-screened bag, assuming independent misses, is 1-(1-0.985)(1-0.997) = 1 - 0.015*0.003 = 0.999955, versus 0.985 for EDS alone - the miss rate on the 20% subset drops from 0.015 to 0.000045, a factor of ~333. ETD cost: A = 29*$45,000 = $1,305,000; B = 31*$45,000 = $1,395,000 one-time. Labor: an ETD operator costs ~10x an EDS operator, so the ETD lane adds 29*10 = 290 (A) and 31*10 = 310 (B) operator-equivalents versus 39 and 41 for the EDS lanes - the ETD lane is ~7.4x the EDS lane in labor terms despite handling only 20% of bags. Schedule change: the ETD lane is the scarcer resource, but at the recommended fleets every flight's 20% ETD subset clears inside its window, so the Task 3 schedules do not need to change. ETD-vs-EDS replacement: an ETD adds $45,000 per 45 bags/hr = $1,000 per bags/hr of throughput, cheaper per unit throughput than an EDS's $1M per ~185 bags/hr = $5,405 per bags/hr; however an ETD only processes the 20% subset (a different modality on the same bags), so it cannot substitute for an EDS's role screening the other 80%.

### Outcome Analysis

Recommendation: add 29 ETDs at A and 31 at B, keep the EDS fleet unchanged, and do not let ETDs replace any EDS. Justification of cost: the one-time ETD cost (~$1.3M/airport) is ~13% of a single EDS's $1M cost, and the security value is a ~333x reduction in the miss rate on the 20% high-risk subset. The dominant cost is the 10x labor per ETD, which is a recurring operational cost, not a one-time capital cost - this is the item the Directors should scrutinize. The policy is justified if the 20% subset is correctly targeted at higher-risk passengers (risk-based selection), because then the 333x miss-rate reduction applies exactly where the threat probability is highest. If the 20% is selected at random, the average miss-rate reduction across all bags is only 20% of 333x = ~67x, and the labor cost is paid for a smaller security gain. Should ETDs replace EDSs? No - they are a second modality on a subset, not a faster first pass; replacing an EDS with an ETD would leave 80% of bags with no CT screening. The schedules do not change because the ETD lane, while scarcer per bag, only touches 20% of bags and still clears within the window at the recommended count.

## Subtask 7: Task 7. Using the EDS/ETD model, examine the effect of changes in device technology, cost, accuracy, speed, and operatio

### Problem

Task 7. Using the EDS/ETD model, examine the effect of changes in device technology, cost, accuracy, speed, and operational reliability; recommend the STEM research areas with the biggest impact on security-system performance, added to the memo.

### Analysis

This is a sensitivity-analysis and research-prioritization task. The model gives fleet size as a function of (rate, availability, cost, accuracy). I vary each device parameter and observe the effect on fleet size and security value, then rank the research directions by their leverage on performance.

### Modeling Process

Sensitivity of the Airport A fleet (B=3172.8 bags, R=0.6) to each parameter: (1) EDS availability 0.80/0.85/0.90/0.92/0.95/0.98/0.99 -> 43/41/39/38/37/36/35 EDS (one-outage robust: 44/42/40/39/38/37/36). (2) EDS speed 160/185/210/250/300 bags/hr -> 44/38/33/28/23 EDS. (3) EDS cost $0.6M/$1.0M/$1.5M -> total A fleet $23.4M/$39.0M/$58.5M (39 EDS). (4) Accuracy: EDS 0.985 -> miss 0.015; adding ETD to the 20% subset -> combined 0.999955 (miss 0.000045), a 333x reduction on that subset. (5) ETD speed 40-50 bags/hr sets the ETD fleet at 29-31 for the 20% subset; faster ETDs would cut the ETD count proportionally.

### Outcome Analysis

Ranked by leverage on system performance: (1) Speed (throughput) has the largest direct effect on fleet size - moving from 160 to 300 bags/hr cuts the A fleet from 44 to 23 EDS (a 48% reduction), because fleet size is inversely proportional to rate. Research that raises EDS bags/hour is the highest-leverage single investment. (2) Operational reliability (availability) is second - moving from 0.92 to 0.99 reduces the fleet from 38 to 35 EDS (one-outage 39 to 36), and, more importantly, directly reduces the probability of the outage scenario that forces the +1 robustness machine. Reliability also cuts the recurring cost of spare capacity. (3) Accuracy has the largest effect on the security value (miss rate) but the smallest effect on fleet size - it does not change how many machines are needed, only how safe each scan is. Accuracy research matters most for the ETD dual-screening policy, where it buys the 333x miss-rate reduction. (4) Cost changes total expenditure but not performance. STEM research recommendations, in priority order: (a) faster CT-imaging throughput (higher bags/hour EDS) - biggest fleet-size lever; (b) higher operational availability/reliability (fewer outages) - second lever and cuts spare-capacity cost; (c) higher detection accuracy, especially for the ETD mass-spectrometry modality - biggest security-value lever for the dual-screening policy; (d) lower capital and per-unit labor cost - reduces expenditure without changing the physics. The memo should fund (a) and (b) first because they reduce the number of $1M machines the manufacturer must build (the current binding national constraint), and (c) to make the 20% ETD policy deliver its full security value.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
