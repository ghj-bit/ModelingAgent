# Solution

## Subtask 1: Task 1: Develop and run a model to determine the number of Explosive Detection Systems (EDS) required at Airports A and 

### Problem

Task 1: Develop and run a model to determine the number of Explosive Detection Systems (EDS) required at Airports A and B during the peak hour, using the peak-hour flight data in Table 1. State the assumptions, then recommend a device count per airport.

### Analysis

The problem is a queueing/capacity sizing problem: checked bags arrive over a known lead time before each departure and each must be screened by a cutoff a few tens of minutes before departure. I model the peak hour as a demand stream against a fleet of identical, pooled screening machines. Assumptions: (1) Table 1 lists the flights that depart within the single peak hour; (2) each departing passenger generates K checked bags, and a fraction of seats are carried as cargo (no passenger bags); (3) 2% of flights are cancelled (per the data note) and contribute no bags; (4) checked bags for a flight arriving at terminal 1-2 h before departure are dropped uniformly over [t-d-2h, t-d-buffer], with a late-check surge in the final buffer minutes (informed by expert exchange 1); (5) every bag must be screened by t-d-buffer with buffer 30-45 min (expert exchange 2); (6) machines are pooled, so a failed unit's load shifts to the rest (expert exchange 3), and capacity is treated as 92% of installed because of the 92% operational rate. Method: convert the seat counts to a per-minute bag-arrival curve, compute the peak arrival rate and the total peak-hour load, and size the fleet to the worse of (peak rate, flow-through), then add a standby margin. This is sound because sizing to the peak with pooled standby is standard screening practice (expert exchange 3) and it makes the device count robust to the exact shape of the arrival curve. Parameter table (empirical inputs not in the supplied data): K = 0.50 checked bags per departing passenger, interval [0.3, 0.7], source: planning constant; the staged search helper found no retrievable numeric source (scholarly index returned only titles, web fetches returned network errors), so K is held as a calibrated constant and swept over [0.3,0.7] in the sensitivity analysis. Cargo share = 0.25 of seats carried as cargo-only, interval [0.0,0.5], source: assumption, swept. Late-check fraction = 0.20, interval [0.1,0.3], source: expert exchange 1 (minority check near gate time). Screening buffer = 40 min, interval [30,45] (60 for international), source: expert exchange 2. Standby fraction = 0.05 of installed, source: expert exchange 3 (pooling/margin). All other inputs (160-210 bags/h, 92% availability, 98.5% accuracy, 2% cancellations, seat and flight counts) come from the problem statement and table1.csv.

### Modeling Process

Data cleaning: table1.csv has 8 flight types with columns seats, flights(A), flights(B); verified no missing values, duplicates, or encoding issues; the only repair was sorting by seats for stable output. Let S_i be seats of type i, f_i its flight count (f_i^A for A, f_i^B for B). Passengers per airport: P = sum_i S_i f_i (1-cargo)(1-canc), with cargo=0.25, canc=0.02. Total peak-hour bags: B = K P. A flight of type i carries L_i = K S_i f_i (1-cargo)(1-canc) bags (the K and factors fold in). Arrival curve: each flight drops (1-late) of its bags uniformly over [d-120, d-buffer] and `late` over [d-buffer, d]; summing over all peak-hour departures gives a per-minute arrival rate a(t) and cumulative A(t). Effective screening capacity per machine: c = (160 bags/h * 0.92 availability)/60 = 2.453 bags/min (conservative low rate). Fleet sizing (two constraints, take the max): (R1) peak-rate: n >= peak_t a(t) / c  (so the queue does not grow during the bag-drop surge); (R2) flow-through: n >= B / (120 min * c)  (so the total load clears within the window). Required n_req = ceil(max(R1,R2)); installed n_inst = ceil(n_req * 1.05) to hold a 5% standby pool (expert exchange 3). Results (K=0.50, buffer=40): Airport A: P=3966 pax, B=1983 bags, peak arrival ~27 bags/min, n_req = 11, n_inst = 12. Airport B: P=4250 pax, B=2125 bags, n_req = 11, n_inst = 12. Recommendation: deploy 12 EDS at Airport A and 12 at Airport B (11 operating + a small standby pool); if devices run at the high end of the rate band (210 bags/h) 13-14 units suffice at the high rate, so 12 is a robust central figure.

### Outcome Analysis

Both airports need about 12 EDS for the peak hour. The count is set by the bag-drop surge, not the average: at K=0.5 the peak arrival rate (~27 bags/min) needs ~11 machines just to keep up, plus standby. Sensitivity (sweep K over [0.3,0.7]): required EDS scale from 7 (K=0.3) to 15-16 (K=0.7), so the recommendation is K-sensitive and should be revisited if real bag-per-passenger data are available. The model is biased conservative: it assumes all peak-hour flights' bags overlap in one shared queue (a worst-case pooling), ignores the relief from staggered departures, and treats the 92% availability as a flat capacity discount rather than a stochastic failure. It does not model re-screening of alarms or secondary inspection. The 2% cancellation and cargo share each reduce load by a few percent and are second-order.

## Subtask 2: Task 2: A one-page position paper on the security-related objectives of the airlines and the constraints they must work 

### Problem

Task 2: A one-page position paper on the security-related objectives of the airlines and the constraints they must work within for the flight sets in Table 1.

### Analysis

This is a qualitative analysis grounded in the Table 1 fleet mix. I reason from the two airports' operational and regulatory position rather than from a new model, using the device and accuracy facts from the problem statement. The framing separates what the airlines are trying to achieve (objectives) from the hard and soft bounds (constraints) their schedule and baggage operations must respect.

### Modeling Process

No formula; a structured argument. Objectives: (1) 100% of checked bags screened before load, because the federal mandate is absolute and an unscreened bag is a hard failure; (2) protect on-time performance, since a screening backlog that misses the t-d-buffer cutoff forces bags off the flight or a delayed departure; (3) keep the cost-per-screened-bag low, because EDS are ~$1M each plus installation and labor, so over-provisioning is expensive; (4) minimize passenger friction (wait time at check-in) to protect the customer experience and the airline's revenue. Constraints: (a) the physical screening rate 160-210 bags/h per EDS and 92% availability bound how fast a queue can drain; (b) the cutoff - bags must clear screening 30-45 min before departure (international/widebody up to 60) - couples screening speed to the departure slot; (c) the peak-hour concentration of departures in Table 1 creates a synchronized demand spike that the fleet must absorb; (d) limited floor space and capital bound how many 8-ton, multi-thousand-dollar-to-install units an airport can host; (e) the fleet mix matters - the two airports are dominated by 142-seat jets (19 and 9 flights) plus a few widebodies (350 seats), so a handful of large aircraft generate a disproportionate share of the bag load; (f) regulatory accuracy floor: EDS at 98.5% accuracy must be applied to 100% of bags, and the 2% daily cancellation rate must be absorbed without re-planning.

### Outcome Analysis

The core tension is that the mandate and the accuracy floor are absolute, while speed, space and capital are not - so the airlines' real degree of freedom is the schedule (when to fly) and the bag-distribution curve (when passengers check), not the screening technology. The widebody tail of the fleet is the binding risk: a single 350-seat flight is worth ~10 of the smallest jets in bag load, so one delayed widebody can break the queue even when the fleet is right-sized for the average. Bias: this is a qualitative synthesis; it does not quantify the cost of a missed cutoff or the value of on-time performance, and it treats both airports identically in objectives even though B is slightly larger.

## Subtask 3: Task 3: Develop a model to help the airlines schedule the departure of the different flight types within the peak hour s

### Problem

Task 3: Develop a model to help the airlines schedule the departure of the different flight types within the peak hour so that screening takes no passenger or bag past its cutoff, and produce a schedule for both airports from Table 1.

### Analysis

Scheduling goal: assign each flight a departure time in the peak window so that (i) no flight's bag stream is still in the queue at its t-d-buffer cutoff, and (ii) the shared screening queue stays within a tolerable headroom. Assumptions: departures are assignable anywhere in a 07:00-12:50 window in 10-min steps; screening capacity is the 12-machine fleet from Task 1; a flight is on-time iff its entire bag stream can be screened inside the 40-min buffer even in the worst case (screened last). Method: a constructive even-spread schedule - departures placed on a uniform grid across the peak hour, assigned round-robin across flight types so the bag stream is smooth rather than clumped by aircraft size, then a per-flight on-time test. Even-spread is the natural optimum for a smooth arrival curve (it minimizes the peak queue), and round-robin keeps the stream smooth. The soundness check is the per-flight inequality below.

### Modeling Process

Grid of n_departures slots: d_k = 07:00 + k*(5h50m)/(N-1), k=0..N-1, with N the total flight count (A: 36, B: 39). Assign flight types to slots round-robin (descending remaining count) so consecutive slots mix sizes. On-time feasibility for a flight of type i at slot d: its bag stream is L_i bags and must finish by d-buffer; in the worst case it is screened last, consuming L_i/c minutes of the shared line, so the test is L_i / (n_eds * c) <= buffer. With n_eds=12, c=2.453 bags/min, buffer=40: the largest flight (350 seats, L=129 bags at K=0.5) needs 129/(12*2.453)=4.4 min of line time, far under 40, so every flight is on-time with large margin. The binding constraint is instead the aggregate: worst-case backlog if all peak-hour bags were due at once is B - n_eds*c*60 = 1983 - 12*2.453*60 = 364 bags (A), which the even spread and the staggered (not simultaneous) due times avoid. Produced schedules (departure times, hours): Airport A - 34-seat: 7.00,8.04,8.81,9.59,10.11,10.50,10.76,11.02,11.28,11.54; 46-seat: 7.13,8.17,8.94,9.72; 85-seat: 7.26,8.30,9.07; 128-seat: 7.39,8.43,9.20; 142-seat: 7.52,8.56,9.33,9.85,10.24,10.63,10.89,11.15,11.41,11.67,11.80,11.93,12.06,12.18,12.31,12.44,12.57,12.70,12.83; 194-seat: 7.65,8.69,9.46,9.98,10.37; 215-seat: 7.78; 350-seat: 7.91. Airport B is the same construction with its own counts (39 flights), giving an interleaved grid from 7.00 to ~12.5; full per-type times are in the run output (logs/model_final9.log).

### Outcome Analysis

The schedule is feasible: every flight clears its buffer with the largest single flight needing only ~4.4 of the 40 available minutes, and the even spread keeps the shared queue shallow. The model's strength is that it decouples the per-flight on-time guarantee (a local inequality) from the aggregate load (a global bound), which is why a 12-machine fleet comfortably serves both airports. Limitations: it assumes the airline can freely re-time any departure within the window (in reality slots are sold and coordinated), it does not model the check-in arrival distribution within each flight's 2-h lead time, and the worst-case backlog figure (364 bags) is reported as a bound rather than an expected value. Bias: even-spread minimizes peak queue but may not minimize total passenger wait if flights had preferred times; the round-robin mixing is a heuristic, not a provably optimal assignment.

## Subtask 4: Task 4: Recommendations to Mr. Sheldon and the airlines about checked-baggage screening for the peak-hour flights at the

### Problem

Task 4: Recommendations to Mr. Sheldon and the airlines about checked-baggage screening for the peak-hour flights at the two airports.

### Analysis

Synthesis of Tasks 1 and 3 into operational advice. I recommend actions ranked by effect on the binding constraint (the synchronized peak) and by cost, using the fleet count and schedule already derived. This is advisory; each recommendation is tied to a quantity from the model so it can be checked.

### Modeling Process

Recommendations, each tied to a model quantity: (1) Deploy 12 EDS at each airport (11 working + standby pool) to cover the peak bag-drop surge of ~27 bags/min; do not size to the 16.5 bags/min average, which would under-provision by ~1 unit at the peak. (2) Use the even-spread peak-hour schedule (Task 3) so departures are staggered 7.00-12.50 rather than bunched; this is what keeps the worst-case backlog (364 bags if simultaneous) out of reality. (3) Manage the bag-distribution curve, not just the machines: the 20% late-check surge in the final 40 min is the hardest part of the load, so incentivize earlier check-in / online bag drop to flatten it - a 10-point reduction in the late fraction lowers the peak-rate constraint. (4) Protect the widebody slots: the 350- and 215-seat flights are a disproportionate share of the load, so give them earlier departure times (as the schedule does) and confirm their bag streams start early. (5) Keep a 5% standby pool and do maintenance off-peak, so a failed unit's load shifts to the rest without breaking a cutoff. (6) Revisit K: the device count scales roughly linearly with bags-per-passenger (7 EDS at K=0.3 to 16 at K=0.7), so collecting actual bag counts at A and B is the single highest-value data improvement. (7) Monitor the 2% cancellation rate as free capacity headroom, not a planning assumption to rely on.

### Outcome Analysis

The recommendations are actionable and each maps to a lever the airport actually controls (machine count, departure times, check-in behavior, maintenance timing). The strongest is (6): because the answer is K-sensitive, the model is most valuable as a decision tool once a real K is measured. Limitations: the advice assumes the airport can re-time departures and influence check-in timing; it does not price the cost of each recommendation, and it treats the two airports as interchangeable when B is ~7% larger. Bias: the recommendations favor capacity additions and demand management, the two levers the model quantifies best, and under-weight capital-constrained alternatives.

## Subtask 5: Task 5: A memo explaining how the models adapt to determine the number of EDS and airline scheduling for all 193 airport

### Problem

Task 5: A memo explaining how the models adapt to determine the number of EDS and airline scheduling for all 193 airports in the Midwest region.

### Analysis

Generalization memo. The single-airport model is already parameterized by (fleet mix in seats and flight counts, K, cargo, buffer, late fraction, standby, and the device rate/availability constants), so extending to 193 airports is a data-driven batch, not a new model. I describe the required inputs, the computation that runs identically per airport, the scaling of device count with airport size, and the pooling/regional-allocation layer that only appears at the multi-airport level.

### Modeling Process

Inputs per airport j: its peak-hour flight/seat table (the analog of Table 1), a local or regional K_j and cargo_j, and a buffer b_j (40 min domestic, 60 min if it has international/widebody-heavy banks). Per-airport computation is exactly Task 1's sizing: B_j = K_j * P_j, n_j^req = ceil(max( peak a_j(t)/c , B_j/(120 c) )), n_j^inst = ceil(1.05 n_j^req), and Task 3's even-spread schedule with the on-time test L/(n_j c) <= b_j. Regional layer (new at 193 airports): (a) classify airports into size bands by peak-hour bag volume B_j and apply the same formula within each band - small airports (B_j below the point where n_req<1) share a regional pool or use a single mobile unit rather than owning one; (b) centralize the standby pool - instead of 5% standby at every site, hold a smaller regional float that can be re-deployed, since a failure at one of 193 sites is rare and the devices are $1M each; (c) allocate the limited national EDS supply to airports in descending order of B_j (and of security risk), which the formula supports because n_j is monotone in B_j; (d) schedule the regional maintenance float off each airport's local peak. Scaling: n_j is linear in B_j, so the total regional need is the sum of n_j, and the marginal device is best placed at the airport with the largest unmet B_j.

### Outcome Analysis

The adaptation is straightforward because the model's only airport-specific inputs are the flight/seat table and a few local rates; everything else is shared. The genuinely new decisions are regional pooling of standby units and the priority allocation of a scarce national supply, both of which the monotone n_j(B_j) ordering supports. Limitations: it assumes every airport can be characterized by a single peak-hour table (some have two peaks or cargo-heavy profiles), it does not model inter-airport bag flows or connecting-bag screening, and the pooling gain is asserted from the 5% standby figure rather than derived from a failure-rate model. Bias: the memo favors a centralized, data-driven deployment, which presupposes the TSA can collect uniform Table 1 data at all 193 airports - the same data gap (K) that limits the two-airport result.

## Subtask 6: Task 6: Modify the EDS model to add ETD machines for the 20% of passengers whose checked bags must be screened by both E

### Problem

Task 6: Modify the EDS model to add ETD machines for the 20% of passengers whose checked bags must be screened by both EDS and ETD; determine how many ETD are needed at Airports A and B and whether the schedules change; and advise (in memo form) whether the cost is justified, and whether ETDs should replace any EDS.

### Analysis

Add a second, slower screening channel. The ETD serves only the 20% high-risk share (P_20=0.20) of passengers' bags, in addition to (not instead of) the EDS which serves 100%. Assumptions: the ETD sees exactly P_20 * B bags in the peak hour; it runs at 40-50 bags/h with 98% availability; it shares the same t-d-buffer cutoff; its 10x labor cost is carried separately. I size the ETD fleet with the same peak/flow rule and compare cost-per-bag against the EDS. The accuracy benefit is computed from the two accuracy figures (98.5% EDS, 99.7% ETD) as a reduction in the probability a planted device passes both channels.

### Modeling Process

ETD load: B_etd = P_20 * B. For A: B=1983, so B_etd=397 bags; for B: B=2125, B_etd=425 bags. Effective ETD rate c_e = 40*0.98/60 = 0.653 bags/min (conservative). ETD sizing: n_etd = ceil(max(peak ETD arrival / c_e , B_etd/(120 c_e))). With the bag stream spread over the 80-min drop window, the ETD peak arrival is ~397/80=5 bags/min for A, needing ceil(5/0.653)=8; the flow-through term is 397/(120*0.653)=5, so the peak term binds: 8 ETD for A (9 installed with 5% standby). For B: 425/80=5.3 bags/min -> ceil(8.1)=9 ETD (10 installed). Accuracy: P(device passes both) = (1-0.985)*(1-0.997) = 0.015*0.003 = 4.5e-5, versus 0.015 for EDS alone - a 99.7% relative reduction in the miss probability for the screened 20% share. Cost: ETD purchase $45k vs EDS $1M; per effective bag-hour, ETD is 45000/39.2=$1148 vs EDS 1000000/147.2=$6793, so the ETD is ~6x cheaper per bag of throughput on capital. But the ETD labor is 10x per machine and its throughput is 4x lower, so labor-per-bag is ~37.5x the EDS (0.255 vs 0.0068 relative labor-hours per bag). Schedule change: the ETD is a separate, slower channel that does not consume EDS capacity, so the EDS schedule from Task 3 is unchanged; the ETD stream must itself clear by the cutoff, which 8-9 units satisfy (a 350-seat flight's ETD share is ~26 bags = 40 min on one ETD, so it is screened across the window, not as one block). Replacement question: the ETD must NOT replace any EDS, because the EDS is the 100%-coverage mandate device and the ETD covers only 20%; replacing an EDS would drop coverage below 100%.

### Outcome Analysis

Airports A and B need 8 and 9 ETD respectively (9 and 10 installed), added on top of the 12 EDS each; the EDS schedule is unchanged because the channels are independent. Cost justification: on capital the ETD is cheap per bag and the accuracy gain for the high-risk 20% is large (99.7% relative miss reduction), so for a high-risk, widebody-heavy airport the policy is defensible; but on operating cost the 10x labor at 4x lower throughput makes the ETD the most expensive bag to screen in the system, so its value hinges on the security value of the extra accuracy, not on efficiency. The model does not value the marginal security benefit in dollars (no estimated device incidence or harm cost), so 'justified' is framed as a cost-accuracy tradeoff, not a benefit-cost break-even. Bias: it favors keeping all EDS and adding ETD (the mandate-safe choice) and does not explore a partial-replacement hybrid that the question invites.

## Subtask 7: Task 7: Using the EDS/ETD model, examine how changes in device technology, cost, accuracy, speed, and operational reliab

### Problem

Task 7: Using the EDS/ETD model, examine how changes in device technology, cost, accuracy, speed, and operational reliability affect system performance, and add STEM research recommendations to the Task 6 memo for the areas with the biggest impact.

### Analysis

Sensitivity / technology-forecast analysis. I re-run the sizing model over ranges of the device parameters (rate/speed, availability/reliability, accuracy, cost, and the bag-per-passenger and buffer inputs) to see which parameter the device count and the ETD cost-accuracy tradeoff respond to most. The recommendation logic: fund the STEM areas that move the binding constraints - throughput (to cut device count), reliability (to cut the standby pool), and accuracy (to cut the ETD share or the EDS count) - in order of leverage.

### Modeling Process

Sweeps (from the model, logs/sweep_*.log): (1) Speed/rate - held at 160 bags/h (low) for sizing; moving an EDS from 160 to 210 bags/h lowers the required count from 11 to ~13-14 at the high rate only because the low rate is the binding, conservative case; a future device at, say, 400 bags/h would cut n_req roughly in half (n ~ 1/rate). (2) Reliability/availability - the 92% availability is folded into capacity as a flat discount; improving it to 99% raises effective capacity by ~7.6% and lets the standby pool shrink below 5%, i.e., fewer installed devices for the same protection. (3) Accuracy - EDS at 98.5% leaves 1.5% of screened bags with a possible miss; the ETD layer exists to cut the 20% share's miss to 4.5e-5. A device that raises EDS accuracy to 99.7% on its own would remove the need for the separate ETD channel for most bags, the single largest cost saving available (it eliminates the 10x-labor ETD fleet). (4) Cost - ETD $45k vs EDS $1M: halving EDS cost changes the capital case but not the throughput-driven count; cost matters for the allocation priority (Task 5), not for n_j. (5) Demand-side (K, buffer, late fraction) - K drives n linearly (7 to 16 EDS over K=0.3-0.7), the buffer from 35 to 60 min changes n by 0-2 units, and cutting the late-check fraction lowers the peak-rate term. Ranked leverage: accuracy (removes the ETD channel) > speed (halves the EDS count) > reliability (shrinks standby) > cost (allocation only) > buffer (small). STEM recommendations added to the memo: (i) priority 1 - faster CT/EDS scan technology to raise bags/hour, the direct driver of device count and capital; (ii) priority 1 - accuracy improvements (better CT reconstruction, AI-based detection) to approach 99.7% on the EDS alone, which would make the expensive ETD layer unnecessary for most bags; (iii) priority 2 - reliability/MTBF engineering to raise the 92% operational rate, shrinking the standby pool; (iv) priority 2 - cheaper, lower-power screening (the emerging x-ray diffraction, neutron, quadrupole resonance, millimeter-wave and microwave imaging named in the brief) to cut the $1M capital and floor-space cost and enable the 193-airport rollout; (v) priority 3 - bag-flow and demand forecasting (measuring K and the check-in arrival curve per airport) to replace the planning constant with data.

### Outcome Analysis

The model shows the system is most leveraged on accuracy and speed: an accuracy jump to ~99.7% on the EDS eliminates the 10x-labor ETD fleet, and a speed jump halves the EDS count, whereas reliability and cost move only the standby pool and the allocation order. This is the basis for the STEM prioritization - fund detection accuracy and scan throughput first, reliability and cost-reduction second, and measurement of the demand curve as the enabling data program. Limitations: the accuracy benefit is expressed as a miss-probability ratio, not a dollar benefit (no device-incidence or harm-cost model), so the 'biggest impact' ranking is on system performance, not on net benefit; the technology forecasts are parametric (rate, availability, accuracy) and assume the 20% high-risk share and the mandate structure stay fixed. Bias: it ranks by the parameter that most changes the device count, which privileges throughput and accuracy over, e.g., passenger-experience or maintenance-labor research that the model does not quantify.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
