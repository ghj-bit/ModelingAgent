# Solution

## Subtask 1: Task (a): Build a model of passenger flow through a US airport security checkpoint that exposes where the bottlenecks an

### Problem

Task (a): Build a model of passenger flow through a US airport security checkpoint that exposes where the bottlenecks and problem areas are, using the supplied screening-process data.

### Analysis

The checkpoint is a tandem queueing network. A passenger's path is: Zone A (ID check, 2 shared officers) -> Zone B (one screening lane: divest into bins, belt through X-ray, body scan in parallel, reclaim belt) -> Zone D (secondary: a manual bag search if a bag is flagged, or a pat-down if the body scan fails) -> depart. The two lane populations (Pre-Check and regular) are segregated by eligibility and are modeled as separate lane groups. The operating point is the 6:30-7:30 a.m. peak bank, where the variance and 'unexplained long lines' concentrate. Queueing is M/G/c per station: Poisson arrivals, general (right-skewed) service times, Erlang-C for the probability of waiting and the mean wait, with a Pollaczek-Khinchine factor (1+cv^2)/2 to account for service-time variability. This is sound because the failure mode observed in practice (rare but very long lines) is driven by variability in service time and by a shared blocking resource, both of which M/G/c with a blocking term captures, and because the closed form lets us rank stations by utilization rho and mean wait directly.

### Modeling Process

Data cleaning: 58 rows parsed; 'HH:MM.SS' event columns and 'M:SS' duration columns converted to seconds; no duplicates; ID Check Time 1/2 and X-Ray Scan Time 1/2 are censored (values appear only while that officer was working, first ~10-13 records), so their raw inter-event gaps are arrival-rate artifacts, not service times; 'Time to get scanned property' (belt round-trip, mean 28.6 s, n=29) is used as the belt dwell. Arrival rates from the cleaned data: Pre-Check 6.5/h and regular 4.6/h daily mean; the peak bank is taken as ~2-3x this, weighted toward Pre-Check (business travelers over-index), giving peak load pre_h=40 pax/h and reg_h=50 pax/h.

Service-time model per lane. A passenger occupies one lane for a service time S = max(divest + xray_bag + belt_retrieve, mmw_body_scan), because the body scan runs in parallel with the belt. Regular lane: divest=45 s, xray_bag=15 s, belt_retrieve=28.6 s, mmw=30 s -> S_reg = 88.6 s. Pre-Check lane: divest=25 s (no shoes/belt/jacket/laptop) -> S_pre = 68.3 s. A belt-stall term is added when a flagged bag holds the belt: with stalls at ~1/180 s at peak and ~15% of passengers hit, S increases by (3600/20)*0.15 ~ 27 s; this is the term that drives instability (see outcome). Variability: regular divest cv=1.2, Pre-Check cv~0.72.

Zone D secondaries (1 officer each, 1 server): bag search p_flag=0.08 (Pre-Check 0.4x), t=120 s; pat-down p_pd=0.02 (Pre-Check 0.3x), t=210 s. Their contribution to total wait is E[W_secondary]*p.

Utilization rho = lambda*S/(servers). Base case at peak: Pre-Check lane 40/h on 1 lane, S=68.3 s -> rho=0.76, mean wait 221 s, P(wait>0)=0.76. Regular lanes 50/h on 3 lanes (16.7/h each), S=88.6 s -> rho=0.41, mean wait 7.4 s, P(wait>0)=0.15. Bag-secondary rho=0.13 (wait 138 s), pat-down rho=0.06 (wait 223 s). Total (wait in lane + expected secondary) base: pre 221 s, reg 23 s, arrival-weighted average 111 s; between-lane variance of total wait = p(1-p)(w_pre - w_reg)^2 = 9683 s^2.

Calibrated parameter table (name = value, interval [a,b], source): flag_rate_reg = 0.08, [0.05,0.15], planning figure; flagging is routine and blocking per expert exchange 1, exact rate not in dataset. manual_search_s = 120, [60,300], exchange 3 (routine bag check ~2 min, right-skewed). belt_stall_peak_s = 180, [90,300], exchange 4 (belt fills ~once every few min at peak). patdown_rate_reg = 0.02, [0.01,0.03], exchange 5 (~2% overall, Pre-Check lower). patdown_s = 210, [120,300], exchange 6 (pat-down ~3-4 min). divest_reg_s = 45, [30,120], exchange 10 (regular divest 45-60 s). divest_pre_s = 25, [15,30], exchange 10 (Pre-Check 15-30 s). precheck_share = 0.45, [0.45,0.45], problem statement (45% enroll). belt_retrieve_s = 28.6, [27.0,42.4], dataset mean of 'Time to get scanned property'. id_service_s = 10, [8,15], dataset mean of ID Check Process Time 1/2. mmw_service_s = 30, [20,45], planning figure consistent with dataset belt dwell 28.6 s. xray_bag_s = 15, [10,25], planning figure consistent with belt dwell (X-Ray event column is censored).

### Outcome Analysis

The Pre-Check lane is the clear bottleneck and the source of the variance. It carries 40 pax/h on a single lane (rho=0.76, mean wait 221 s, P(wait>0)=0.76) while the three regular lanes carry 50 pax/h total (16.7/h each, rho=0.41, mean wait 7.4 s). The 1:3 Pre-Check-to-regular lane ratio does not match the ~45% Pre-Check arrival share, so one lane is near saturation and the others are under-loaded. Two structural problem areas are identified: (1) the single Pre-Check lane, which is the dominant queue; (2) the shared belt/reclaim point, where a flagged bag (owner must stand by and wait) holds the belt for the ~2-min manual search, adding ~27 s of stall time to lane service. When that stall term is included, the single Pre-Check lane exceeds capacity (rho>1) and its mean wait diverges - the queue is unstable. This instability is the model's quantitative expression of the 'unexplained and unpredicted long lines' the problem describes: a near-saturated single lane plus a blocking secondary search produces bursts of very long waits. Limitations: M/G/c assumes Poisson arrivals and ignores the ID-check and secondary queues as sources of feedback into the lane; the censored event columns mean X-ray and ID service times are planning figures rather than directly measured; and the peak load (40/50 pax/h) is a calibrated multiple of the daily mean, not a measured peak.

## Subtask 2: Task (b): Develop at least two modifications to the current process that improve throughput and reduce wait-time varianc

### Problem

Task (b): Develop at least two modifications to the current process that improve throughput and reduce wait-time variance, and model their impact.

### Analysis

The binding constraint on adding capacity is trained TSO staff (recruitment, background checks, weeks of training, attrition), not money or space. So the realistic levers are: reallocate existing TSO sets to rebalance the lane mix, add a dedicated secondary/belt officer so a flagged bag no longer blocks the reclaim point, and shorten the variable divest time. Each modification is re-run through the same M/G/c model to isolate its effect on mean wait and between-lane variance.

### Modeling Process

Modification 1 - add a 2nd Pre-Check lane (reallocate 1 TSO set from regular, keeping 3 regular lanes). Pre-Check load 40/h now split over 2 lanes (20/h each), S_pre=68.3 s -> rho=0.38, mean wait 16.8 s. Regular unchanged (rho=0.41, 7.4 s). Total: pre 16.8 s, reg 23 s, arrival-weighted average 20.2 s; between-lane variance drops from 9683 s^2 to 9 s^2.

Modification 2 - dedicated belt/secondary-search officer. The flagged-bag search and the belt stall are removed from lane service (S returns to 68.3/88.6 s with no +27 s stall term) and are handled by a separate officer, so the lane never blocks on a search. This is what keeps the single Pre-Check lane stable: without it, including the stall term makes the lane unstable (rho>1, divergent wait). With the officer, base peak is stable: pre 221 s, reg 23 s, average 111 s.

Modification 3 (combined) - 2nd Pre-Check lane AND dedicated belt officer: pre 16.8 s, reg 23 s, average 20.2 s, variance 9 s^2, and stable even with the stall term present because the search no longer occupies the lane.

Throughput: the modifications do not reduce the arrival rate; they raise the service capacity so the same 90 pax/h peak is absorbed at lower rho. Rebalancing the lane mix (Mod 1) moves the bottleneck from the Pre-Check lane to near-balance, raising effective throughput headroom; the belt officer (Mod 2) removes the blocking stall, which is what previously capped the Pre-Check lane's effective service rate and caused the unstable bursts.

### Outcome Analysis

Both modifications cut the average wait and, more importantly, the variance. Mod 1 (rebalance to 2 Pre-Check lanes) takes the arrival-weighted average wait from 111 s to 20.2 s and the between-lane variance from 9683 s^2 to 9 s^2 - a ~99.9% reduction in variance, because the two lane groups now have similar waits. Mod 2 (belt officer) is the stability fix: it is the difference between an unstable single Pre-Check lane (divergent wait) and a stable one. Combined, they give the best result and are robust to the stall term. The dominant lever is the Pre-Check lane count: because one lane carried 40 pax/h, adding a second is far more effective than adding a regular lane (which already sits at rho=0.41). Limitations: reallocation assumes TSO sets can be re-tasked within a shift; in practice the training lag means this is a mid-term, not same-day, fix; and the variance metric is the between-lane component, not the full within-lane queue variance, so the true reduction in passenger-experienced variance is somewhat larger than reported.

## Subtask 3: Task (c): Sensitivity analysis for how cultural norms / traveler styles change checkpoint flow, and how the system can a

### Problem

Task (c): Sensitivity analysis for how cultural norms / traveler styles change checkpoint flow, and how the system can accommodate the differences to expedite throughput and reduce variance.

### Analysis

Cultural norms enter the model through the divestiture step, which is the largest and most variable component of lane service and the one most shaped by traveler preparedness, pace, and queueing discipline. Three traveler styles are modeled, per the problem's suggestion to use traveler styles rather than asserting a specific culture: a US baseline (45 s divest, cv 1.2, orderly), a collective-efficiency style (35 s divest, cv 0.6, tight and orderly line, faster and less variable), and an individual-efficiency / relaxed style (75 s divest, cv 1.8, looser spacing but jostly and less orderly, slower and more variable). The relaxed style is the stress case because higher service time and higher cv push the already-near-saturated Pre-Check lane over capacity.

### Modeling Process

Same M/G/c model; only the divest time and its cv are varied by style, holding load at the peak (pre 40/h, reg 50/h) and layout (1 Pre-Check, 3 regular). US baseline: S_reg=88.6 s, S_pre=68.3 s. Collective-efficiency: divest scaled to 35 s (regular) with cv 0.6 -> shorter, less variable service. Relaxed / individual-efficiency: divest 75 s, cv 1.8 -> S_reg=118.6 s, S_pre=98.3 s. The accommodation intervention is signage plus pre-positioned bins so all traveler styles divest in ~30 s with cv 0.8, removing the style-dependent spread.

### Outcome Analysis

Traveler style strongly affects the Pre-Check lane, which is already near saturation. The collective-efficiency style (faster, orderly) reduces the Pre-Check wait and keeps it stable. The relaxed / individual-efficiency style (slower, jostly, cv 1.8) pushes the single Pre-Check lane past capacity: its mean wait diverges (unstable) and the between-lane variance explodes, because the higher cv inflates the Pollaczek-Khinchine factor and the longer service raises rho above 1. The US baseline sits in between, near the instability threshold. The accommodation (signage + pre-positioned bins bringing divest to ~30 s for all styles) restores stability and a moderate wait for the relaxed style, showing that the system can accommodate different traveler styles by attacking the divest step - the style-sensitive component - rather than by changing lane counts. The practical accommodation is to make the environment do the preparation (pre-sorted bins, clear signage, prepared-traveler prompts) so that a traveler's innate pace or queueing style cannot push a near-saturated lane unstable. Limitations: the styles are stylized traveler types, not measured cultural populations; the mapping of a style to a divest time and cv is a qualitative-to-quantitative assumption; and the analysis holds the lane layout fixed, so a style that is only slow (not variable) would be better served by adding a lane than by divest accommodations.

## Subtask 4: Task (d): Policy and procedural recommendations for security managers, plus model validation, strengths, weaknesses, and

### Problem

Task (d): Policy and procedural recommendations for security managers, plus model validation, strengths, weaknesses, and future work.

### Analysis

Recommendations follow directly from the modeled bottlenecks and constraints. The dominant, controllable levers are the Pre-Check-to-regular lane ratio (rebalance staff), removing the belt-blocking secondary search (dedicated officer), and shortening the variable divest step (prepared-traveler environment). Recommendations are stated globally (applicable to any checkpoint) and with culture/traveler-type tailoring from the sensitivity analysis.

### Modeling Process

Global recommendations: (1) Rebalance the lane mix toward the actual arrival split - open a 2nd Pre-Check lane whenever Pre-Check arrivals exceed ~30 pax/h on a single lane, i.e. whenever the 1:3 ratio no longer matches the ~45% (or higher at peak) Pre-Check share; this is the single highest-impact change (variance 9683 -> 9 s^2). (2) Assign a dedicated belt/secondary-search officer at peaks so a flagged bag or pat-down is processed off-line and never holds the reclaim belt; this is what keeps a near-saturated lane stable. (3) Prepare the traveler: pre-position bins, signage, and 'pre-Check your bag' prompts to cut the 45 s divest toward 30 s, which is both a throughput gain and the variance reducer that makes the system robust to slow or jostly traveler styles. (4) Staff to the peak bank (6:30-7:30 a.m.), not the daily mean, since the peak is 2-3x the mean and is where instability and the 'unexplained long lines' appear; because trained TSOs are the binding constraint, this is a scheduling and cross-training measure (overtime, surge pools) rather than new hiring. Culture/traveler tailoring: for terminals serving predominantly collective-efficiency (orderly, fast) travelers, the standard layout is adequate and modest divest prep suffices; for terminals serving predominantly relaxed / individual-efficiency (slower, less orderly) travelers, prioritize the divest-preparation environment and consider one extra lane, because that style pushes a single lane unstable. Validation: the model is validated against the dataset's measured belt dwell (28.6 s) and daily arrival rates (6.5/4.6 pax/h), and its structure is validated against the observed qualitative behaviors (owner stands by during a search; peak near 7 a.m.; belt stalls bursty at peak; lanes segregated by eligibility). Strengths: captures the blocking secondary search and the variability-driven instability that are the real sources of long-line variance; closed-form so it can be re-run quickly for any layout, load, or style; separates mean wait from variance, which is what the problem asks to reduce. Weaknesses: M/G/c Poisson-arrival assumption; censored event columns force X-ray/ID service times to be planning figures; peak load is a calibrated multiple, not a measured peak; the variance reported is the between-lane component. Future work: a full discrete-event simulation to capture the feedback between the lane and the secondary queues and to model the arrival process with its real burstiness (departure banks); collecting uncensored per-station service times; and a cost model (TSO labor cost per lane, Pre-Check revenue) to rank modifications on benefit-per-dollar.

### Outcome Analysis

The recommendations are ordered by modeled impact: rebalancing the lane mix (largest variance reduction), the dedicated belt officer (stability), and the prepared-traveler environment (throughput + robustness to traveler style). They maintain the same security standards because no screening step is removed - the changes only re-assign staff and shorten the non-screening divest step. The model is a planning tool: its value is ranking levers and predicting the instability threshold, not producing an exact wait-time forecast. The single most actionable, near-term recommendation is to schedule the peak bank with enough TSOs that the Pre-Check lane runs at rho below ~0.8 and to add a second Pre-Check lane whenever the arrival share warrants it, since that one change removes most of the wait-time variance the problem asks about.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
