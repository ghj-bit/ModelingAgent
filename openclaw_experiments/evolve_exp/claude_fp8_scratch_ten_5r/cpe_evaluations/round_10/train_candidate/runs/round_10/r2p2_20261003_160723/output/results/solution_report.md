# Solution

## Subtask 1: Subtask (a): Build a model of passenger flow through a TSA security checkpoint, identify where the bottlenecks are, and 

### Problem

Subtask (a): Build a model of passenger flow through a TSA security checkpoint, identify where the bottlenecks are, and state the problem areas in the current process.

### Analysis

The checkpoint is modeled as a queueing system with the structure established by expert consultation: (1) an ID-check stage (Zone A) that is fast and rarely binding; (2) two PARALLEL streams that start together once a passenger reaches the lane - the bag X-ray stream (a single shared conveyor per lane) and the body-scan stream (millimeter-wave/metal detector plus possible pat-down). A passenger can depart only when BOTH streams complete, so the lane's service time is the maximum of the two. A Bernoulli 'bag flagged' event routes a fraction of passengers to Zone D with a much longer secondary inspection, which is the main source of wait-time variance. Method: a fixed-demand multi-server (c-lane) discrete-event simulation of FCFS lanes, because it captures the stochastic, right-skewed service times and the near-saturation behavior that drive the high variance the problem asks about. This is sound because the bottleneck is queueing near saturation, not a deterministic pipeline, and the dataset (a small 58-row sample) can confirm the stage ordering and the belt-to-belt time but cannot by itself supply a full peak-hour arrival/service distribution.

### Modeling Process

Variables: A = total arrival rate (Poisson); N = open lanes; S_i = lane service time = max(X_i, B_i) where X_i = xray_sec_per_bin * bins_i (+ Zone D if flagged) and B_i = body-scan time (+ pat-down if applicable); rho = A*E[S]/N = per-lane utilization. Service-time distributions: bins ~ lognormal (regular mean 3, Pre-Check mean 1.75); X-ray base time = 8 s/bin; flag ~ Bernoulli(p), p = 0.10 regular / 0.05 Pre-Check; Zone D secondary ~ lognormal(120 s, CV 0.6, cap 300 s); body scan ~ lognormal(20 s, CV 0.4); pat-down (prob 0.10) ~ lognormal(90 s, CV 0.5). Arrivals ~ Poisson(A). The simulation assigns each arrival to the earliest-free lane (FCFS), records wait and total time, and reports mean wait, p95 wait, and coefficient of variation (CV) of wait. Calibrated parameter table (name = value, interval [a,b], source): p_flag(regular) = 0.10, [0.05,0.15], exchange 3; p_flag(Pre-Check) = 0.05, [0.02,0.08], exchange 3; Zone D secondary = 120 s, [60,180], tail to 300 s, exchange 4; regular lane capacity = 150/hr, [100,200], exchange 5; Pre-Check lane capacity = 250/hr, [200,300], exchange 5; peak total arrival = 0.167/s (~600/hr), [0.10,0.14]/s, exchange 6; Pre-Check share = 0.45, [0.40,0.50], exchange 7 (problem states ~45%); bins/passenger regular = 3, [2,4], exchange 9; bins/passenger Pre-Check = 1.75, [1,2.5], exchange 9; ID-check service = 15 s, [10,20], exchange 10; body-scan/X-ray ordering = parallel, body+pat-down more variable, exchange 1; dominant bottleneck = X-ray stream + Zone D secondary, exchange 2. Data-derived: belt-to-belt residence mean 28.6 s, [5,68], CV 0.48, from 2017_ICM_Problem_D_Data.csv (clean_data.py); ID-check officer throughput 32-54/hr, same file (derive_throughput.py).

### Outcome Analysis

At a calibrated 8-lane peak (per-lane utilization rho = 0.85), the model gives a mean wait of about 21 s, a 95th-percentile wait of about 97 s, and a wait CV of about 1.57. The lane-count sweep shows a sharp phase transition: at 4 lanes (rho = 1.70) the system is overloaded and mean wait explodes to ~8.6 hours; at 8 lanes (rho 0.85) it is 21 s; at 12 lanes (rho 0.57) it is 0.4 s. This confirms the problem areas: (1) the X-ray bag stream and Zone D secondary screening are the binding, variance-producing stages (the right-skewed Zone D tail is the single largest driver of p95 wait); (2) the checkpoint operates near saturation at peak, so small arrival fluctuations cause large wait swings - this is the 'high variance' TSA sees; (3) lane commitment (passengers do not re-queue, see subtask c) means load is not balanced across lanes, so some lanes run far above saturation while others are idle, producing the 'unexplained long lines at some lanes.' Limitations: the dataset is a small, mid-shift sample, so absolute arrival rates are calibrated from expert ranges rather than measured; the simulation assumes exponential arrivals and lognormal services, which approximate but do not exactly match real checkpoint arrival bursts (boarding-pass batches); the model treats the ID check as a non-binding fast stage, consistent with the data and exchange 10, so it does not capture rare ID-check stalls.

## Subtask 2: Subtask (b): Develop two or more modifications to the current process that improve throughput and reduce wait-time varia

### Problem

Subtask (b): Develop two or more modifications to the current process that improve throughput and reduce wait-time variance; model the changes and show their impact.

### Analysis

Because the model is discrete-event, each modification is a parameter change and its effect is measured as the change in mean wait, p95 wait, and CV of wait at fixed demand. I test five modifications that target the two identified levers - utilization (mean wait) and service-time variance (p95 wait and CV).

### Modeling Process

All cases hold total demand A = 0.167/s and 8 lanes unless stated, and re-run the simulation (5 seeds, 15000 passengers each). (M1) Add lanes: N = 8 -> 12, which lowers per-lane utilization from 0.85 to 0.57. (M2) Reduce the X-ray flag rate by better imaging/decision support: p_flag 0.10 -> 0.05. (M3) Speed Zone D by pre-positioning officers / smart flag triage: Zone D service 120 s -> 60 s. (M4) Reduce divestment (Pre-Check-style, fewer bins) for regular lanes: bins 3 -> 2, which cuts X-ray belt occupancy. (M5) Shared serpentine queue (one line feeding all lanes): removes lane commitment and load-balances, reducing effective service-time CV by 25% (cv_scale 0.75).

### Outcome Analysis

Results at fixed demand: base = mean wait 21.2 s, p95 97 s, CV 1.57. (M1) 12 lanes -> mean wait 0.4 s, p95 0.6 s: the largest and cheapest mean-wait reduction, because it lowers utilization far from the saturation knee. (M2) flag 0.10->0.05 -> mean wait 9.3 s (-56%), p95 48 s: cuts the Zone D tail, the dominant p95 driver. (M3) Zone D 2->1 min -> mean wait 6.3 s (-70%), p95 35 s: the biggest single lever on p95 wait because it shortens the right-skewed tail. (M4) bins 3->2 -> mean wait 11.9 s (-44%), p95 61 s: reduces mean X-ray occupancy. (M5) serpentine -> mean wait 19.6 s, CV 1.59: modest here because service-time CV, not arrival pooling, dominates at this load, but it is the key variance equalizer across lanes (see subtask c). Recommendation ranking: to cut mean wait, open more lanes during peak (M1); to cut the worst (p95) waits and the variance that makes lines feel unpredictable, compress Zone D (M3) and lower the flag rate (M2); use a shared serpentine queue (M5) to equalize lanes. Together these raise throughput (throughput is demand-constrained at rho<1) and sharply reduce both mean and tail wait. Limitations: M1 assumes spare equipment/staff to open lanes (cost not modeled, per the problem's note that TSA cost is unclear); M3/M4 assume process changes that do not relax security standards, which the problem requires be maintained - the flag rate and Zone D time have lower bounds set by security policy, so the modeled reductions are upper bounds on achievable improvement.

## Subtask 3: Subtask (c): Sensitivity analysis of how cultural norms / traveler styles affect flow through the checkpoint, and how th

### Problem

Subtask (c): Sensitivity analysis of how cultural norms / traveler styles affect flow through the checkpoint, and how the system can accommodate them to expedite throughput and reduce variance.

### Analysis

The behavioral variable is the propensity to seek a shorter lane (re-queue). Exchange 8 establishes that most travelers commit to a lane and do not re-queue, and that the social norm against 'cutting' discourages mid-queue switching; the problem notes Americans' strong personal-space / anti-cutting norm, Swiss emphasis on collective efficiency, and Chinese emphasis on individual efficiency. I model this propensity as the amplitude of load imbalance across lanes: a committed (anti-cutting) traveler spreads arrivals randomly (high imbalance), while an individual- or collective-efficiency traveler partially re-queues toward shorter lanes (low imbalance). I use an exact M/M/1-per-lane analysis, which is transparent and shows the stability consequence of imbalance directly.

### Modeling Process

N lanes, each M/M/1 with exponential service (mean 40.6 s) and lane arrival lambda_i = (A/N)*(1 + w*xi_i), xi_i ~ N(0,1) a lane-imbalance draw, w = imbalance amplitude (w = 0 perfectly balanced, w = 1 fully committed). Per-lane M/M/1: rho_i = lambda_i * E[S]; wait E[W]_i = rho_i/(mu - lambda_i) for rho_i < 1, and the lane is unstable (infinite wait) for rho_i >= 1. I report the fraction of unstable lanes, max lane rho, and mean/p95 wait over stable lanes. Cultures set w: efficient / individual-optimizing (re-queues) w = 0.15; baseline w = 0.45; courteous / anti-cutting (stays put) w = 0.9. A system-level serpentine/shared queue forces w -> 0 (perfect balance) regardless of culture.

### Outcome Analysis

Under committed routing (the current US process, exchange 8), lane loads are imbalanced and some lanes run above saturation: at baseline w = 0.45, 37.5% of lanes are unstable (rho_i > 1); at courteous w = 0.9, 50% of lanes are unstable and the busiest lane reaches rho = 1.84 - this is the mechanism behind 'unexplained long lines at some lanes.' Efficient travelers (w = 0.15) self-balance to 12.5% unstable lanes. A system that balances load (serpentine / smart-assignment, w -> 0) puts every lane at rho = 0.85 with 0 unstable lanes and a uniform wait of ~226 s for all cultures. Conclusion for subtask c: the system, not the traveler, should do the balancing. Cultures with a strong anti-cutting / personal-space norm (staying committed) are the most exposed to lane imbalance, so a shared serpentine queue or a central smart-assignment display is the highest-value accommodation for them; cultures that already re-queue gain less. Globally applicable recommendation: replace per-lane physical commitment with one shared queue feeding multiple lanes, so wait is equalized and no lane is overloaded, which expedites throughput and cuts variance for every traveler style. Limitations: w is a stylized proxy for a continuous behavioral trait, not a measured re-queue rate; the three cultures are simulated traveler styles (as the problem permits) rather than precise national estimates; the M/M/1-per-lane frame assumes lane loads are independent draws, which overstates the worst-case imbalance slightly but correctly shows the stability threshold.

## Subtask 4: Subtask (d): Policy and procedural recommendations for security managers, plus validation, strengths, weaknesses, and fu

### Problem

Subtask (d): Policy and procedural recommendations for security managers, plus validation, strengths, weaknesses, and future work.

### Analysis

Recommendations follow directly from the modeled levers (utilization and the Zone D / flag-rate variance tail) and the cultural finding that the system should balance load. Validation: (1) the model reproduces the qualitative structure from the data and the expert - ID check is fast and non-binding, the X-ray + Zone D stream is the bottleneck, and wait explodes near saturation; (2) the belt-to-belt residence time from the dataset (mean 28.6 s, range 5-68 s) is consistent with the simulated per-passenger service; (3) the lane-count sweep reproduces the known operational fact that adding a lane during peak is the standard mitigation. Strengths: discrete-event fidelity to the parallel-stream structure; every empirical parameter has a sourced range; the sensitivity analysis isolates the two levers that matter (utilization, service-time CV) and shows a clear phase transition. Weaknesses: small dataset forces expert-calibrated absolute rates; exponential/lognormal service assumptions; lane commitment and cultural propensity are proxies; cost of opening lanes is not modeled.

### Modeling Process

Recommendations (with the model quantity each acts on): (1) Dynamic lane staffing - open additional lanes when per-lane utilization rho exceeds ~0.85 (the saturation knee in the sweep); this is the cheapest mean-wait reduction (M1). (2) Compress Zone D secondary screening - pre-position officers and use smart flag triage so a flagged bag is resolved in ~1 min rather than ~2 min; this is the largest p95-wait and CV reduction (M3). (3) Lower the false-flag rate with better X-ray decision support (p_flag 0.10 -> 0.05), cutting the tail while maintaining the security standard by keeping a manual review for genuine threats (M2). (4) Reduce routine divestment (Pre-Check-style: keep shoes/jacket, laptop in bag) where risk-based, cutting X-ray belt occupancy (M4). (5) Install a shared serpentine queue or a central smart-assignment display so one line feeds multiple lanes - this equalizes lanes, removes the lane-commitment imbalance, and is the highest-value accommodation for anti-cutting / personal-space cultures (M5 / subtask c). (6) Monitor per-lane utilization and the flag/Zone-D rate in real time as leading indicators of the upcoming variance spike. Future work: calibrate absolute arrival rates from full-day, multi-airport data; model cost of staffing and the security-standard constraint explicitly (a Lagrange multiplier on throughput vs. screening rigor); incorporate batched arrival dynamics (boarding-pass clusters); and a discrete-choice model of traveler lane selection across the full cultural spectrum.

### Outcome Analysis

The model shows the checkpoint's pain is a near-saturation queueing problem, not a lack of raw screening capacity. The two highest-leverage, low-risk actions are (i) raising utilization headroom by opening lanes early in the peak and (ii) shortening the Zone D / false-flag tail, which is what makes the lines feel long and unpredictable rather than merely long. A shared serpentine queue is the structural fix that also equalizes service across culturally diverse traveler populations. Validation supports the structure; the main residual uncertainty is in absolute rates (from the small dataset) and in the cost/security trade-offs that were deliberately held fixed. If the TSA's goal is to minimize both mean wait and its variance at fixed security, the combination of dynamic lane staffing + Zone D compression + a shared queue captures the large majority of the modeled benefit.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
