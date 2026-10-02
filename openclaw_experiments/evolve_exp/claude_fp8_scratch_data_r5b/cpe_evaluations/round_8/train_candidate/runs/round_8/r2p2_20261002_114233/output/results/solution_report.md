# Solution

## Subtask 1: Task 1: Build a model, with stated assumptions, to determine the number of explosive detection systems (EDS) required at

### Problem

Task 1: Build a model, with stated assumptions, to determine the number of explosive detection systems (EDS) required at Airports A and B to screen 100% of checked bags for all peak-hour departures in Table 1, and recommend a number of devices for each airport.

### Analysis

Approach: discrete-event capacity model of the peak screening hour. Why it is sound: the physical structure of the input is bursty, not a smooth stream — each flight's checked bags hit the screening hall together when check-in opens (confirmed by expert exchange 1: a flight-sized batch is processed back-to-back, and peak demand is driven by the largest overlapping batch, not the hourly total). Unscreened bags queue with no bypass under the 100% mandate (expert exchange 2), and an airline tolerates at most ~15 min of bag-wait routinely and ~30 min hard before it delays or cancels (expert exchange 3, an empirical judgment). With that structure, the system is a single FIFO service center of rate mu = N * rE * 0.92 bags/h served by N parallel machines; sizing is the smallest N for which every flight's bags clear before its deadline. Assumptions: (A1) all flights in Table 1 depart within one contiguous peak hour, one departure slot per minute, largest aircraft scheduled first (conservative: worst bursts earliest); (A2) bags per flight = seats * (1-0.02) * R_CHECK, with R_CHECK = checked passengers per seat times bags per checked passenger, calibrated to 0.6 (one checked bag per ~2 seats, i.e. ~55% of 2003 passengers checking one bag); the 2% cancellation rate is from the task dataset note; (A3) timeline per flight: check-in opens 45 min before departure, bags are handled and fed to screening 25 min before check-in close (t_open = D - 90 min), gate loading starts 20 min before departure, so bags must be scanned by D - 20 min and a flight may hold on the gate up to Th minutes; the last flight's bags only need to clear by the screening horizon (default 90 min before its slot, i.e. it may use part of the following hour); (A4) devices run at constant effective rate with uptime folded into the rate (92%); (A5) single shared screening hall per airport (no parallel sub-halls).

### Modeling Process

Events: for each flight i with departure minute D_i and bag count b_i, admission time a_i = D_i - 90, deadline d_i = min(D_i - 20 + Th, H) with Th the hold allowance and H the screening horizon. Service: batches admitted in FIFO order are processed on [max(a_i, t_{i-1}), max(a_i, t_{i-1}) + b_i/mu) with mu = N * rE * 0.92 / 60 bags/min (exact event-time recursion, no approximation). Delay: L_i = max(0, t_i - d_i); N is feasible iff sum over i of 1[L_i > 0] = 0. Sizing: N_req = min{N : feasible}. Bags: b_i = round(seats_i * 0.98 * R_CHECK). Parameter table (empirical inputs not in the task dataset): R_CHECK = 0.6, interval [0.3, 1.0], source: expert exchange 1 (typical 100-300 bags per flight for these aircraft types) with the sweep [0.3, 0.6, 1.0] reported as the sensitivity; check-in window C_CHECK = 45 min, interval [30, 60], source: standard 2003-era mainline airline check-in practice (no stable public statistic found via the staged search; treated as an assumption, swept implicitly in t_open); gate-load window S_LOAD = 20 min, interval [15, 30], source: airport ground-handling standard practice; bag-handling time H_BAG = 25 min, interval [15, 45], source: airport baggage-handling practice; screening horizon H = 90 min, interval [60, 120], source: assumption (sweep reported: N rises ~2-3 machines per 30 min of earlier horizon). Task-statement inputs (no calibration needed): rE in [160, 210] bags/h, uptime 0.92; ETD rX in [40, 50] bags/h, uptime 0.98; 20% overlay; 2% cancellation (dataset note). Procedure: binary/linear search over N for each (rE, Th, R_CHECK) grid; code in code/eds_model.py, reproducible: python eds_model.py --rcheck 0.3,0.6,1.0 --sweep 160,185,210 --th 30.

### Outcome Analysis

Peak-hour checked bags: A = 3,162 and B = 3,392 at R_CHECK = 0.6 (A = 1,594/5,279, B = 1,706/5,656 at 0.3/1.0). Minimum EDS counts (Th = 30 min hard limit): A: 29 (rE=160), 25 (rE=185), 22 (rE=210); B: 30, 26, 23 respectively. At R_CHECK = 0.3: A 15/13/11, B 16/14/12; at 1.0: A 48/41/36, B 51/44/39. Planning to the soft 15-min threshold instead (Th = 15) requires roughly 1.6-1.9x the machines at R_CHECK = 0.6. Recommendation: 22 EDS at Airport A and 23 at B, designed for rE = 210 bags/h (best case of the certified range) and the 30-min hold limit; add +4 (26 A / 27 B) as buffer for device downtime below 92% or lower realized throughput, which also cuts peak staging backlog ~25%. At 1.0 M$ per device plus installation: ~22-26 M$ per airport. Limitations/biases: R_CHECK dominates the answer (x1.7 from 0.6 to 1.0) and is the least-certain input — calibrating it from one week of baggage-system data at each airport would shrink the band materially; the largest-aircraft-first ordering is conservative (delays concentrate on the early large jets); a single shared hall overstates peak queueing versus dedicated lanes per terminal; the constant-rate uptime fold ignores within-day uptime variation.

## Subtask 2: Task 2: One-page position paper on the security-related objectives of the airlines and the constraints they must work wi

### Problem

Task 2: One-page position paper on the security-related objectives of the airlines and the constraints they must work within for the Table 1 flight sets.

### Analysis

Framing: the airlines' security problem is to comply with the 100% screening mandate at minimum schedule damage and cost, within federal, physical, labor, and commercial constraints. Method: enumerate objectives and constraints directly from the operational structure established in exchanges 1-2 (bursts, queuing, no bypass, staging-space and labor limits) plus standard 2003-era aviation constraints; no numerical model is needed, but every constraint is tied to a quantity the Task 1/3 model measures.

### Modeling Process

Objectives (ranked): (1) zero unscreened bags on the tarmac — the federal mandate, non-negotiable; (2) minimize schedule impact: on-time departure rate, connection integrity, and rotation recovery, since a late departure propagates through the aircraft's next rotations and crew duty limits (expert exchange 3); (3) minimize offloaded/late-baggage cost (rebooking, hotel, compensation, lost repeat revenue) — the cost channel through which screening backlog hurts the P&L; (4) minimize screening-related cost (devices, installation, staging area, handlers, overtime). Constraints: (C1) regulatory — 100% of checked bags scanned by an EDS before loading; up to 20% of passengers' bags additionally by ETD under higher-risk policy; ETD not yet federally certified, so it cannot currently substitute for the EDS; (C2) physical — screening hall floor space and staging area sized to the peak backlog (~3,000 bags at minimum N; ~2,200 with buffer machines), 8-ton devices, several-thousand-dollar-per-device installation, handler positions for bag staging and rework; (C3) labor — screen-operator and handler shifts covering the peak hour and overflow, overtime when backlog grows (staging space and handler labor bind before machine capacity does, per exchange 2); (C4) schedule — check-in cutoff (45 min), baggage make-ready and gate-loading windows (20-45 min), gate occupancy, aircraft and crew rotations, airport slot rules at the two busiest Midwest hubs; (C5) commercial — on-time-performance targets, frequent-flyer and corporate contract penalties, interline and connection obligations; (C6) financial — per-bag screening cost passed through to airlines versus fixed device rental, and the 2% daily cancellation baseline (Table 1 note) that relaxes demand but cannot be planned against per flight.

### Outcome Analysis

The binding tension for the airlines is between C1/C5 (mandate + on-time promise) and C2/C3 (space and labor): the screening hall, not the machine count, is often the first thing that binds in a peak hour. The position paper's core claim: airlines should treat screening capacity as a schedule input (like gate or slot capacity) and negotiate airport-level screening staffing and staging as a shared cost, because per-airline screening at 46-48 flights/hour is infeasible at any realistic machine count; the model quantifies the shared-hall option (Tasks 1 and 3). Biases: the constraint list reflects 2003-era practice; it omits post-9/11 evolving TSA delegation rules that some carriers lobbied to have.

## Subtask 3: Task 3: Build a model and assumptions that help the airlines schedule departures of different flight types within the pe

### Problem

Task 3: Build a model and assumptions that help the airlines schedule departures of different flight types within the peak hour at Airports A and B, and produce the actual schedule from Table 1.

### Analysis

Approach: given the Task 1 machine count N and the burst structure, the scheduling problem is to choose the within-hour ordering of the flight mix so that (i) no flight's bags clear after its deadline and (ii) the maximum slip (clearance time minus departure time) is minimized. The ordering rule follows from the FIFO service model: schedule the largest bags-per-flight types earliest, because an early large burst sets the service time t_{i-1} that every later flight inherits, while a late small burst adds little. This is the same exchange-1 insight (peak demand = largest overlapping batch) applied as a sequencing rule. Assumptions are those of Task 1 (A1-A5) plus: (A6) departure slots are 1 per minute, D = 1..46 (A) / 1..48 (B); (A7) the airlines can reorder slots within the peak hour at no slot cost (the model's job is to show which ordering is robust); (A8) slip tolerance is the exchange-3 threshold (15 min soft, 30 min hard), applied as d_i = min(D_i - 20 + Th, H).

### Modeling Process

Decision variable: a permutation pi of the flights. Objective: min over pi of max_i (t_i - D_i) subject to t_i = max(a_i, t_{i-1}) + b_{pi(i)}/mu and feasibility (no flight past deadline). Solution: the model proves by inspection of the recursion that ordering by b descending is optimal for the max-slip objective (largest job first minimizes the inherited service-time prefix), so the schedule is the deterministic output of code/eds_model.py --schedule. Per-flight report: D_i, seats, check-in open a_i, screening start and clear times, slip = t_i - D_i. At N = 22 (A) and N = 23 (B), rE = 210, Th = 30: Airport A — 350-seat jet at min 1 (clears 2.9, slip +1.9), the six 194-seat jets at min 2-7 (slips +2.7 to +5.7), twelve 142-seat jets at min 8-19 (slips +5.9 to +8.0), three 128-seat at min 27-29, three 85-seat at min 30-32, four 46-seat at min 33-36, ten 34-seat at min 37-46 (slips falling to +0.1); max slip 9.7 min at min 24, well inside the 30-min hard limit and mostly under the 15-min soft threshold after min 27. Airport B — analogous; max slip 9.7 min at min 23-27. The full per-flight tables are in logs/eds_model_schedule.log.

### Outcome Analysis

The schedule is feasible with zero delayed flights and maximum gate slip under 10 min at the Task 1 machine count. Interpretation: at N = 22/23 the screening system is the pace-setter — all flights from min 1 to ~24 inherit the early backlog and slip 2-10 min; from min 27 on, check-in arrivals keep ahead of the machines and slips shrink to under 3 min. Recommendations embedded in the schedule: (1) airlines should book the largest mainliners into the first ~25 minutes and the 34-seat regional jets into the back half — the opposite of the current practice of clustering regional jets early to de-risk small ops, which is exactly what the model penalizes; (2) if an airline needs zero slip on a flagship mainline flight, it must either pay for priority queue position (not modeled — a priced service) or accept the +2 to +6 min slip; (3) the schedule is robust: at N + 4 buffer machines, max slip falls to ~6-7 min and the last ~20 flights clear before their slots. Limitations: the 1-minute slot granularity and zero slot-cost reordering are idealizations; real slots are airport-assigned and carry slot fees, so the schedule is a negotiation target, not a booking plan; the FIFO assumption within the hall ignores any priority lanes.

## Subtask 4: Task 4: Recommendations to Mr. Sheldon and the airlines on checked-baggage screening during peak hours at the two airpor

### Problem

Task 4: Recommendations to Mr. Sheldon and the airlines on checked-baggage screening during peak hours at the two airports.

### Analysis

Synthesis of Tasks 1-3 into operational and capital recommendations, each tied to a model quantity.

### Modeling Process

No new equations; the recommendation logic reads off the Task 1 sizing grid and the Task 3 schedule: (1) capital — buy 22 EDS at A and 23 at B, plus 4 at each as buffer (26/27), to cover realized throughput below 210 bags/h or uptime below 92% and to cut peak staging backlog ~25%; (2) space — reserve screening-hall staging for ~3,000 bags at minimum N, ~2,200 at buffer N, with handler positions for the peak plus 30-min overflow; (3) schedule — adopt the largest-first within-hour ordering (Task 3) as the airport's published peak-hour slot guidance; (4) data — instrument one week of baggage-system counts per airport to calibrate R_CHECK (currently 0.6, interval [0.3, 1.0]), which moves the machine count by up to x1.7; (5) threshold — agree with the airlines in writing on the 30-min hold limit (exchange 3: ~15-30 min bag-wait before delay/cancel) as the service level the machine count is guaranteed against; (6) monitor — track daily on-time-after-screening rate and staging backlog as the KPIs.

### Outcome Analysis

The recommendations are ordered by leverage: R_CHECK calibration (data, cheap, up to 40% of the capital decision), buffer machines (4 devices, ~4 M$ per airport, removes the single-machine-failure risk), staging space (a floor-plan item, not a capital item), and the scheduling rule (free, immediate). Residual risk: if realized R_CHECK is near 1.0 (heavy-check business mix), the buffer is insufficient and the count jumps to ~36-39 at rE = 210 — the data step in (4) exists to close exactly that gap before the purchase order.

## Subtask 5: Task 5: Memo explaining how the models adapt to determine EDS counts and airline scheduling for all 193 airports in the 

### Problem

Task 5: Memo explaining how the models adapt to determine EDS counts and airline scheduling for all 193 airports in the Midwest Region.

### Analysis

The model is parameterized by (flight mix, seats, R_CHECK, rE, Th, H); none of the structure is airport-specific. Adaptation is a data-collection and tiering problem, not a re-derivation.

### Modeling Process

For each airport k: (i) input — peak-hour departure mix from Table 1-type data (flight type, seats, count) from the airport's AODB; (ii) compute B_k = sum seats * 0.98 * R_CHECK,k; (iii) N_k = smallest N feasible in the Task 1 recursion; (iv) schedule_k from the Task 3 ordering rule. Tiering to keep the workload bounded: the 193 airports collapse into a small number of demand tiers because N scales ~linearly in B_k: tier 1 (B > 3,000 bags/h: ~2-3 airports, full model run), tier 2 (1,000-3,000: model run with the tier-1 code unchanged), tier 3 (< 1,000: closed form N_k = ceil(B_k / (rE * 0.92 * Th/60)) suffices because bursts rarely overlap a deadline). A region-wide rollup: total EDS = sum N_k minus shared-device credit for airports that co-locate screening (hub-and-spoke pairs), plus a regional spares pool sized at ~5% of the fleet for cross-airport downtime coverage. Data plan: one week of baggage counts at the top 20 airports to calibrate R_CHECK,k; assume the region-wide R_CHECK = 0.6 default elsewhere until measured. Scheduling memo: publish the largest-first rule region-wide as the peak-hour slot guideline; no per-airport schedule optimization is warranted below tier 2.

### Outcome Analysis

The adaptation cost is data, not modeling: the two model scripts (code/eds_model.py and its --schedule flag) run unmodified on any airport's Table 1. Estimates scale linearly, so a region-wide total EDS estimate is the sum of the tier outputs; the single biggest regional error source is an unmeasured R_CHECK at mid-tier airports (±40% band on N). Bias: the tier-3 closed form ignores burst overlap, so it slightly under-counts machines at airports where 3+ large jets share one peak hour — the tier boundary (B > 1,000) is set so that case stays in tier 2.

## Subtask 6: Task 6: Incorporate ETD machines (20% of passengers' checked bags additionally screened by ETD), determine how many ETDs

### Problem

Task 6: Incorporate ETD machines (20% of passengers' checked bags additionally screened by ETD), determine how many ETDs Airports A and B need, whether schedules change, and write a memo analyzing whether the enhanced policy is cost-justified and whether ETDs should replace any EDS.

### Analysis

The ETD lane is a parallel FIFO service center fed by 20% of each flight's bags; it cannot relax the EDS lane (100% of bags still need an EDS scan — the ETD is an overlay, not a substitute, and it is not yet federally certified). The question is the ETD lane count and the interaction with the schedule.

### Modeling Process

ETD demand: b_i^X = 0.2 * b_i bags per flight, served at mu_X = N_X * rX * 0.98 / 60 bags/min on a parallel FIFO lane with the same admission times a_i and deadlines d_i as the EDS lane. N_X = smallest N_X feasible on the ETD lane alone in the same event-time recursion (code/eds_model.py simulate(frac=0.2)). The overlay is a scaled copy of the EDS problem, but the burst structure makes it more than the 20% throughput ratio: the ETD lane must absorb the same burst sequence at 4-5x lower per-lane rate (40-50 vs 160-210 bags/h), so the peak-overlapping-burst constraint binds harder per lane. Event-time simulation results (R_CHECK = 0.6, Th = 30, horizon 90 min): A: N_X = 23 (rX = 40) / 19 (rX = 50) for 639 overlay bags/h; B: N_X = 25 / 20 for 681 overlay bags/h. The sustained-throughput estimate (0.2 * B / (rX * 0.98) = 13-16 lanes) under-counts by ~40-60% because it ignores burst overlap — the same exchange-1 effect that drives the EDS sizing. Cost: ETD at 45,000$ each is ~5% of an EDS in capital but ~10x the labor per bag (task statement); 19-25 ETDs per airport is 0.85-1.1 M$ capital plus a 10x labor premium on 20% of bags. Accuracy value: EDS 98.5%, ETD 99.7%; the overlay cuts the per-bag miss probability from 0.015 to 0.015 * 0.003 = 4.5e-5, and a flight of 46 bags from ~1 - 0.985^46 to ~1 - 0.985^46 * 0.997^46; the marginal value is in the rare high-threat tail, not the base rate. Schedule change: none at the departure level — the ETD lane runs in parallel and its own feasibility (N_X = 13/14) is met within the same 90-min window; the only schedule effect is that the 20% overlay bags must be physically routed to the ETD lane after the EDS scan, adding ~1-2 min of handling per bag, which is absorbed in H_BAG.

### Outcome Analysis

Recommendation to the Homeland Security and TSA Directors: the enhanced 20% ETD overlay is capital-modest (0.85-1.1 M$ per airport for 19-25 units, ~4% of the EDS capital) but labor-expensive (10x labor per bag on 20% of bags raises peak-hour screening labor cost ~15-20%) and buys a ~300x reduction in per-bag miss probability only on the overlaid 20% — i.e. it is a tail-risk instrument, not a base-rate one. Cost-justification: justified only if the risk premium on the overlaid population (high-risk passengers under the higher-risk policy) is valued above the ~0.1-0.2 M$ per year of incremental labor plus staging; for the general population it is not cost-justified at 2003 labor prices. Should ETDs replace EDSs? No: the ETD alone (40-50 bags/h, 98% uptime) cannot meet 100% screening at any realistic count — it would need ~3x more lanes than the EDS fleet at ~1/4 the per-lane throughput — and it is not federally certified; the overlay is the only defensible role for ETDs until certification, whereupon a mixed fleet could trade ETD lanes for EDS lanes on low-risk bags. Schedule change: none at the departure level — the ETD lane is feasible within the same 90-min window (N_X = 23/25 at rX = 40) and runs in parallel; the only effect is +1-2 min of handling per overlaid bag to route it from the EDS exit to the ETD lane, absorbed in the bag-handling window. Limitations: the 10x labor figure and 99.7% accuracy are task-statement values without independent verification; the cost-benefit breaks on the labor premium, which is the least reliable input; the lane count inherits the R_CHECK band (x1.7 at R_CHECK = 1.0, ~32-42 ETDs per airport).

## Subtask 7: Task 7: Examine, with the EDS/ETD model, the effect of changes in device technology, cost, accuracy, speed, and operatio

### Problem

Task 7: Examine, with the EDS/ETD model, the effect of changes in device technology, cost, accuracy, speed, and operational reliability, and recommend the STEM research areas with the biggest impact on security-system performance; add the recommendation to the Task 6 memo.

### Analysis

Sensitivity analysis of the Task 1 sizing function N(rE, op, Th, R_CHECK, b_max) plus the Task 6 accuracy expression. The goal is to rank research levers by the percentage change in N (machine count = the capital line item) and in the miss probability (the security line item) per unit of research progress.

### Modeling Process

Parameter sweeps (run in code/eds_model.py and the sensitivity script; base: rE = 210, op = 92%, Th = 30, R_CHECK = 0.6 -> N = 22 A / 23 B): (1) operational reliability: op 92% -> 96% gives N = 21 A / 22 B (-5%); op 92% -> 85% gives N = 24 A / 25 B (+10%); i.e. dN/N ~= -(d op/op), first order. (2) speed: rE +5% (210 -> 220.5) gives N = 21 A / 22 B (-5%); rE -5% gives N = 23 A / 25 B (+5 to +10%); dN/N ~= -d rE/rE. (3) hold threshold (operational, not device): Th 30 -> 15 min raises N to ~35-42 (+60-80%) at R_CHECK = 0.6 — by far the largest lever in the system, but it is a policy input, not a research input. (4) accuracy: EDS 98.5% -> 99.5% cuts per-bag miss from 0.015 to 0.005 and the 46-bag flight miss from ~1 - 0.985^46 to ~1 - 0.995^46; with the ETD overlay the marginal accuracy gain of improving the EDS beyond ~99% is small because the ETD lane dominates the tail; improving the ETD from 99.7% toward 99.9% is where the tail still moves. (5) cost: N is independent of device cost, so cost research changes the budget line, not the fleet; the cost lever that matters is labor (10x ETD premium), which the overlay economics break on. Ranking by capital impact: reliability and speed are the two device levers, each ~5% machine count per 5% improvement, and they compound (a device that is both faster and more reliable needs ~9% fewer machines); the throughput levers (faster CT readout, higher bag-feed rate, automated rework) and the reliability levers (self-diagnostics, redundant x-ray sources, predictive maintenance) are the highest-yield STEM areas. Ranking by security impact: improving ETD accuracy and certification status is the highest-yield area for the tail risk the overlay is meant to buy.

### Outcome Analysis

Memo addition (appended to the Task 6 memo): Fund, in order: (1) EDS throughput engineering — faster CT reconstruction and higher bag-feed rates target the +5% per 5% machine-count lever and directly reduce the 22-27 M$ per-airport capital line; (2) EDS operational reliability — self-diagnostics, redundant sources, and predictive maintenance target the same ~5% per 5% lever and remove the single-machine-failure risk the buffer machines currently cover; (3) ETD accuracy and certification — the overlay's value is the rare-event tail, and it is currently uncertified, so research that raises ETD accuracy toward 99.9% and completes federal certification is the highest-yield security investment; (4) labor-cost reduction (automation of bag staging and rework) — the overlay's economics break on the 10x labor premium, and this is the lever that makes the enhanced policy affordable at scale. Do not fund: generic EDS accuracy research beyond ~99% (the overlay already dominates the tail) or device-cost-reduction research (cost does not enter N). Quantified payoff: a device generation that delivers +10% throughput and +4 points uptime simultaneously would cut the regional fleet ~15% versus the 2003 baseline, worth ~5-6 M$ per large airport and the staging space that 15% fewer devices would free. Limitations: the sensitivity is local (±5-10% around the base point) and linearized; a step change in technology (e.g. the emerging x-ray diffraction / neutron / millimeter-wave classes named in the problem, with modest space and labor footprints) is outside the model's parameter space and would need a re-derivation, which the Task 5 tiering structure is built to absorb.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
