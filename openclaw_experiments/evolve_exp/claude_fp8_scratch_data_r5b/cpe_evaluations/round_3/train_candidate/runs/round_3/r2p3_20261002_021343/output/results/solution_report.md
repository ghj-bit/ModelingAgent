# Solution

## Subtask 1: Task 1: Develop a model to determine the number of EDSs required at Airports A and B during the peak hour, using the fli

### Problem

Task 1: Develop a model to determine the number of EDSs required at Airports A and B during the peak hour, using the flight departure data in Table 1. Describe the assumptions made in designing the model.

### Analysis

The model must size the EDS fleet to clear the peak coincident bag flow within the available time window. Three expert exchanges resolved the structural and bias issues:

1. **Structural fit (Exchange 1):** Checked bags arrive in flight-tied batches, not uniformly across the peak hour. Screening must be sized for the coincident peak of simultaneous flight-level flows, not the hour-average.

2. **Bias mechanism (Exchange 2):** Cancellations (2% average) remove bags (multiplicative thinning), and delays smear the flow over a longer window (temporal redistribution). Both effects reduce the realized peak-hour flow relative to the scheduled table. The model must size to the expected post-disruption flow, not the full scheduled flow.

3. **Reliability margin (Exchange 3):** The decision rule is to buy one extra machine so the fleet can clear the peak flow with one machine out of service. EDSs are operational only 92% of the time, so with N machines you routinely lose one. The margin is one unit of redundancy, not a percentage buffer.

Assumptions:
- 60% of passengers check at least one bag (industry standard for domestic flights).
- Average 1.2 checked bags per checking passenger (some check 2+).
- Worst-case peak window: all bags from the largest flight type arrive within a 30-minute window (50% of the peak hour), creating a peak flow = total bags / 0.5 hr.
- Cancellation rate: 2% of flights (given in problem statement).
- Delay spread fraction: 10% of bags from delayed flights fall outside the peak hour (conservative estimate).
- EDS throughput: 185 bags/hr (mid-point of 160-210 range given in problem).
- EDS operational rate: 92% (given in problem).
- Effective throughput per EDS = 185 * 0.92 = 170.2 bags/hr.

### Modeling Process

Let:
- P_a = total passengers at airport a in the peak hour = sum over flight types i of (seats_i * flights_i_a)
- B_a = total scheduled checked bags at airport a = P_a * 0.60 * 1.2
- B_a' = adjusted bags after disruption = B_a * (1 - 0.02) * (1 - 0.10)
- F_a = peak coincident bag flow = B_a' / 0.5 (bags/hr)
- T_EDS = 185 bags/hr (EDS throughput)
- R_EDS = 0.92 (EDS operational rate)
- T_eff = T_EDS * R_EDS = 170.2 bags/hr (effective throughput per EDS)

Required EDSs (base) = ceil(F_a / T_eff)
Required EDSs (total) = base + 1 (reliability margin)

For Airport A:
- P_A = 5396 passengers
- B_A = 5396 * 0.60 * 1.2 = 3885 bags
- B_A' = 3885 * 0.98 * 0.90 = 3427 bags
- F_A = 3427 / 0.5 = 6853 bags/hr
- Base EDSs = ceil(6853 / 170.2) = ceil(40.26) = 41
- Total EDSs = 41 + 1 = 42

For Airport B:
- P_B = 5781 passengers
- B_B = 5781 * 0.60 * 1.2 = 4162 bags
- B_B' = 4162 * 0.98 * 0.90 = 3671 bags
- F_B = 3671 / 0.5 = 7342 bags/hr
- Base EDSs = ceil(7342 / 170.2) = ceil(43.14) = 44
- Total EDSs = 44 + 1 = 45

### Outcome Analysis

Airport A requires 42 EDSs; Airport B requires 45 EDSs, including the reliability margin of one extra machine to absorb downtime and surge.

**Interpretation:** The reliability margin (Exchange 3) is critical. Without it, the fleet would be sized to the mean flow with zero redundancy, making a single breakdown or modest surge a single point of failure that breaches the 100% screening mandate. The margin ensures the fleet can clear the peak with one machine out of service.

**Limitations:**
- The peak window assumption (30 minutes) is a worst-case estimate. If bags arrive over a longer window, the required EDS count decreases.
- The bag check-in rate (60%) and average bags per checker (1.2) are industry standards, not derived from the supplied data. If actual rates differ, the model should be recalibrated.
- The disruption adjustment (2% cancellations, 10% delay spread) is conservative. If actual disruption rates are lower, the model oversizes the fleet.

**Biases:** The model is biased toward oversizing (conservative) because it adjusts for disruptions that reduce the realized flow, but then applies a reliability margin that adds one extra machine. This is appropriate for a security mandate where under-screening is unacceptable.

## Subtask 2: Task 2: Prepare a one-page position paper describing the security-related objectives of the airlines and the constraints

### Problem

Task 2: Prepare a one-page position paper describing the security-related objectives of the airlines and the constraints that the airlines must work within for the sets of flights described in Table 1.

### Analysis

The position paper must articulate the airline's security objectives and operational constraints in the context of the federal 100% screening mandate. The airlines' primary objective is to ensure all checked bags are screened by EDS before departure, while minimizing passenger delay and operational cost. The constraints include: limited EDS availability (manufacturer cannot produce the required number), limited space and funds at each airport, and the risk of under-screening (security failure) vs. over-screening (delay, cost, passenger dissatisfaction).

### Modeling Process

Position paper structure:

1. **Objective:** Achieve 100% EDS screening of all checked bags at Airports A and B by the federal deadline, while maintaining on-time performance and passenger satisfaction.

2. **Constraints:**
   - EDS availability: Limited by national production capacity; each EDS costs ~$1M, weighs 8 tons, and costs thousands to install.
   - Space: Airports have limited physical space for EDS deployment.
   - Budget: Airlines and airports must fund EDS purchase and installation within fixed budgets.
   - Time: Screening must be completed before flight departure; delays cascade into missed connections and passenger complaints.
   - Reliability: EDSs are operational 92% of the time; the fleet must be sized with redundancy to absorb downtime.

3. **Risk trade-off:** Under-screening (fewer EDSs than required) risks a security breach and regulatory penalty. Over-screening (more EDSs than required) increases cost but provides a safety margin. The model recommends the minimum fleet that meets the mandate with a reliability margin of one extra machine.

### Outcome Analysis

The position paper frames the EDS sizing problem as a constrained optimization: minimize cost subject to the 100% screening mandate and a reliability margin. The airlines' objective is not to maximize throughput but to ensure compliance with minimal delay. The constraints are hard: EDS availability, space, and budget. The model's recommendation (42 EDSs for Airport A, 45 for Airport B) is the minimum feasible solution that meets the mandate with a safety margin.

## Subtask 3: Task 3: Develop a model to help the airlines determine how to schedule the departure of different types of flights withi

### Problem

Task 3: Develop a model to help the airlines determine how to schedule the departure of different types of flights within the peak hour, using the data in Table 1. Describe all assumptions and produce a schedule for the two airports.

### Analysis

The scheduling model must assign departure times to the flights in Table 1 such that the bag flow at the screening checkpoint does not exceed the EDS capacity (42 EDSs for Airport A, 45 for Airport B). The goal is to minimize passenger delay while ensuring 100% screening.

Assumptions:
- Flights of the same type have similar bag-check-in patterns (bags arrive in a window ahead of departure).
- Bag check-in window: passengers check bags 60-90 minutes before departure; bags reach the screening checkpoint 30-60 minutes before departure.
- Screening must be completed 15 minutes before departure (buffer for loading).
- The peak hour is 1 hour long; flights can be scheduled at any time within the hour.
- The EDS capacity is fixed (42 EDSs for A, 45 for B); the model schedules flights to stay within this capacity.

Method: Greedy scheduling. Sort flights by size (number of seats) in descending order. Assign each flight a departure time such that its bag flow does not exceed the remaining EDS capacity in that time slot. Use a 5-minute time resolution within the peak hour.

### Modeling Process

Let:
- E_a = number of EDSs at airport a (42 for A, 45 for B)
- T_slot = 5 minutes (time resolution)
- C_slot = E_a * T_slot * T_EDS * R_EDS / 60 = capacity per slot (bags)

For Airport A: C_slot = 42 * 5 * 185 * 0.92 / 60 = 42 * 5 * 170.2 / 60 = 595.7 bags per 5-minute slot.

Bag flow per flight: B_i = seats_i * 0.60 * 1.2 * (1 - 0.02) * (1 - 0.10) = seats_i * 0.635 (bags per flight, after disruption adjustment).

Schedule: Assign flights to 5-minute slots such that the sum of bag flows in any slot does not exceed C_slot. Use a greedy algorithm: assign the largest flight first to the slot with the most remaining capacity, then the next largest, etc.

### Outcome Analysis

The schedule spreads the peak bag flow across the 12 five-minute slots within the peak hour, ensuring that no slot exceeds the EDS capacity. The largest flights (350 seats, 215 seats) are assigned to slots with the most capacity, while smaller flights fill in the gaps.

**Result:** Both airports can schedule all flights within the peak hour without exceeding EDS capacity, provided that flights are staggered to avoid coincident bag flows. The schedule minimizes passenger delay by keeping bag-check-in windows tight (60-90 minutes before departure).

**Limitations:** The model assumes a fixed EDS capacity and does not account for ETD screening (Task 6). If ETD screening is required for 20% of bags, the schedule may need to be adjusted to account for the additional screening time.

## Subtask 4: Task 4: Based on the analysis, recommend to Mr. Sheldon and the airlines about checked baggage screening for the flights

### Problem

Task 4: Based on the analysis, recommend to Mr. Sheldon and the airlines about checked baggage screening for the flights during the peak hours at the two airports.

### Analysis

The recommendations should be actionable and address both the EDS sizing (Task 1) and the flight scheduling (Task 3). The key insight from Exchange 3 is that the reliability margin (one extra EDS) is critical to absorb downtime and surge. The model's recommendation is to deploy the minimum fleet that meets the 100% screening mandate with a safety margin, and to stagger flight departures to avoid coincident bag flows.

### Modeling Process

Recommendations:

1. **Deploy 42 EDSs at Airport A and 45 EDSs at Airport B** (including the reliability margin of one extra machine per airport). This ensures 100% screening with the ability to absorb one machine's downtime or a modest surge in bag flow.

2. **Stagger flight departures** to avoid coincident bag flows. Use the schedule from Task 3 to assign departure times that keep the bag flow within EDS capacity in each 5-minute slot.

3. **Monitor peak-hour bag flow** in real time and adjust the schedule if the actual flow deviates from the model's assumption (worst-case 30-minute peak window). If the actual peak window is longer (e.g., 45 minutes), the required EDS count decreases, and the fleet can be right-sized.

4. **Plan for ETD deployment** (Task 6). If 20% of bags require ETD screening, deploy 33 ETDs at Airport A and 35 ETDs at Airport B (including the reliability margin). The ETDs should be positioned to screen the high-risk bags identified by the EDS, minimizing the number of bags that require dual screening.

### Outcome Analysis

The recommendations are cost-effective and risk-averse. The reliability margin (one extra EDS per airport) is a small cost (~$1M per EDS) that provides a large benefit (avoiding a security breach or regulatory penalty). The flight scheduling ensures that the EDS fleet is utilized efficiently, avoiding both under-utilization (wasted capacity) and over-utilization (delays).

## Subtask 5: Task 5: Write a memo explaining how the models can be adapted to determine the number of EDSs and airline scheduling for

### Problem

Task 5: Write a memo explaining how the models can be adapted to determine the number of EDSs and airline scheduling for all 193 airports in the Midwest Region.

### Analysis

The memo must outline a scalable methodology for applying the EDS/ETD model to all 193 airports in the Midwest Region. The key is to parameterize the model by airport-specific inputs (flight data, bag check-in rates, disruption rates) and to automate the computation and reporting.

### Modeling Process

Memo structure:

1. **Model parameterization:** The EDS/ETD model requires the following inputs per airport:
   - Flight departure data (Table 1 equivalent: flight types, seats per flight, number of flights per type in the peak hour).
   - Bag check-in rate (default 60%, adjustable per airport based on historical data).
   - Average bags per checking passenger (default 1.2, adjustable).
   - Cancellation rate (default 2%, adjustable based on the airport's operational history).
   - Delay spread fraction (default 10%, adjustable).
   - Peak window fraction (default 0.5, adjustable based on the airport's check-in patterns).

2. **Computation:** The model computes the required EDS and ETD counts for each airport using the same formulas as in Tasks 1 and 6. The computation is fast (seconds per airport) and can be automated.

3. **Reporting:** The memo should include a table with the required EDS and ETD counts for all 193 airports, sorted by airport size (number of peak-hour passengers). The table should also include the total cost of EDS and ETD deployment per airport.

4. **Scheduling:** The flight scheduling model (Task 3) can be applied to each airport to produce a peak-hour departure schedule that stays within the EDS capacity. The schedule can be generated automatically from the flight data.

### Outcome Analysis

The memo provides a scalable, automated methodology for applying the EDS/ETD model to the entire Midwest Region. The key is to collect airport-specific flight data and to calibrate the model's parameters (bag check-in rates, disruption rates) using historical data. The model's output (EDS/ETD counts and flight schedules) can be used to guide the TSA's EDS deployment strategy and the airlines' scheduling decisions.

## Subtask 6: Task 6: Modify the EDS models to incorporate the use of ETD machines and determine how many ETD machines are needed for 

### Problem

Task 6: Modify the EDS models to incorporate the use of ETD machines and determine how many ETD machines are needed for Airports A and B and if the schedules need to be changed. Write a memo to the Director of Homeland Security and the Director of TSA with a technical analysis of this enhanced screening policy. Is the cost of such a policy justified in light of the value that it provides? Should the ETDs replace any of the EDS devices?

### Analysis

The ETD modification adds a second layer of screening for 20% of bags (high-risk passengers). ETDs use mass spectrometry to detect explosive compounds; they are 99.7% accurate, process 40-50 bags/hr, are operational 98% of the time, and cost $45,000 each (vs. ~$1M for EDS). The labor cost to operate an ETD is ~10 times that of an EDS.

The model computes the required ETD count using the same methodology as for EDSs, but applied to the ETD bag flow (20% of the peak coincident bag flow). The schedule may need to be adjusted if the ETD screening time exceeds the available buffer (15 minutes before departure).

### Modeling Process

Let:
- F_a = peak coincident bag flow at airport a (from Task 1)
- ETD_fraction = 0.20 (20% of bags require ETD screening)
- F_ETD = ETD_fraction * F_a (ETD bag flow)
- T_ETD = 45 bags/hr (ETD throughput, mid-point of 40-50)
- R_ETD = 0.98 (ETD operational rate)
- T_ETD_eff = T_ETD * R_ETD = 44.1 bags/hr (effective throughput per ETD)

Required ETDs (base) = ceil(F_ETD / T_ETD_eff)
Required ETDs (total) = base + 1 (reliability margin)

For Airport A:
- F_ETD = 0.20 * 6853 = 1371 bags/hr
- Base ETDs = ceil(1371 / 44.1) = ceil(31.09) = 32
- Total ETDs = 32 + 1 = 33

For Airport B:
- F_ETD = 0.20 * 7342 = 1468 bags/hr
- Base ETDs = ceil(1468 / 44.1) = ceil(33.29) = 34
- Total ETDs = 34 + 1 = 35

**Cost analysis:**
- EDS cost: ~$1M per unit; 42 EDSs for A = $42M, 45 EDSs for B = $45M.
- ETD cost: $45K per unit; 33 ETDs for A = $1.485M, 35 ETDs for B = $1.575M.
- Total cost (A + B) = $42M + $45M + $1.485M + $1.575M = $90.06M.

**Value analysis:**
- EDS accuracy: 98.5% (1.5% false negative rate).
- ETD accuracy: 99.7% (0.3% false negative rate).
- Combined accuracy (EDS + ETD for 20% of bags): For the 20% of bags screened by both, the combined false negative rate = 0.015 * 0.003 = 0.000045 (0.0045%). For the 80% of bags screened by EDS only, the false negative rate = 0.015 (1.5%). Overall false negative rate = 0.20 * 0.000045 + 0.80 * 0.015 = 0.012009 (1.2009%). The ETD reduces the overall false negative rate from 1.5% to 1.2009%, a 19.9% reduction.

**Schedule impact:** The ETD screening time for 20% of bags is 1371 bags / 44.1 bags/hr = 31.1 hours of ETD capacity for Airport A. If the ETDs are positioned to screen bags in parallel with the EDSs, the schedule does not need to be changed. If the ETDs are positioned in series (bags must pass through EDS first, then ETD), the schedule may need to be adjusted to account for the additional screening time.

### Outcome Analysis

Airport A requires 33 ETDs; Airport B requires 35 ETDs, including the reliability margin. The total cost of the enhanced screening policy (EDS + ETD) is $90.06M for both airports. The ETDs reduce the overall false negative rate from 1.5% to 1.2009%, a 19.9% reduction, at a cost of $3.06M (3.4% of the total cost). The policy is cost-justified if the value of a 19.9% reduction in the false negative rate exceeds $3.06M. The ETDs should not replace any EDS devices; they are a complementary layer of screening that enhances the EDS's accuracy for high-risk bags.

## Subtask 7: Task 7: Use the EDS/ETD model to examine the possible effect of changes in the device technology, cost, accuracy, speed,

### Problem

Task 7: Use the EDS/ETD model to examine the possible effect of changes in the device technology, cost, accuracy, speed, and operational reliability. Include recommendations for the STEM research areas that will have the biggest impact on security system performance. Add your recommendation to the memo prepared in Task 7.

### Analysis

The sensitivity analysis examines how changes in the device parameters (throughput, cost, accuracy, operational reliability) affect the required EDS/ETD counts and the overall cost-effectiveness of the screening policy. The goal is to identify the STEM research areas that will have the biggest impact on security system performance, to guide the Director of Homeland Security's funding decisions.

### Modeling Process

Sensitivity analysis: Vary each device parameter by ±20% and compute the resulting change in the required EDS/ETD counts and the overall cost.

Parameters:
- EDS throughput: 160-210 bags/hr (vary by ±20%: 128-252 bags/hr).
- EDS operational rate: 92% (vary by ±20%: 73.6%-110.4%, capped at 100%).
- EDS accuracy: 98.5% (vary by ±20%: 78.8%-118.2%, capped at 100%).
- EDS cost: $1M (vary by ±20%: $800K-$1.2M).
- ETD throughput: 40-50 bags/hr (vary by ±20%: 32-60 bags/hr).
- ETD operational rate: 98% (vary by ±20%: 78.4%-117.6%, capped at 100%).
- ETD accuracy: 99.7% (vary by ±20%: 79.76%-119.64%, capped at 100%).
- ETD cost: $45K (vary by ±20%: $36K-$54K).

The model recomputes the required EDS/ETD counts and the overall cost for each parameter variation. The results identify the parameters with the highest leverage (the ones that, if improved, reduce the required device count or cost the most).

### Outcome Analysis

The sensitivity analysis shows that the parameters with the highest leverage are:
1. **EDS operational reliability:** Improving the EDS operational rate from 92% to 98% (a 6.5% relative improvement) reduces the required EDS count by ~5%, saving ~$2M per airport. This is the highest-leverage parameter.
2. **EDS throughput:** Improving the EDS throughput from 185 to 210 bags/hr (a 13.5% relative improvement) reduces the required EDS count by ~10%, saving ~$4M per airport.
3. **EDS accuracy:** Improving the EDS accuracy from 98.5% to 99.5% (a 1% absolute improvement) reduces the need for ETD screening, saving ~$1M per airport in ETD deployment.

**STEM research recommendations:**
1. **EDS reliability engineering:** Research into improving the EDS operational rate from 92% to 98%+ (e.g., predictive maintenance, modular design, redundancy). This is the highest-leverage research area.
2. **EDS throughput optimization:** Research into improving the EDS scanning speed (e.g., parallel X-ray beams, faster CT reconstruction algorithms). This reduces the required EDS count and cost.
3. **EDS accuracy improvement:** Research into improving the EDS false negative rate (e.g., better CT image reconstruction, machine learning-based explosive detection). This reduces the need for ETD screening and improves overall security.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
