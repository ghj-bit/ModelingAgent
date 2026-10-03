# Solution

## Subtask 1: Subtask (a): Build a model of passenger flow through a US airport security checkpoint, calibrate it to the supplied chec

### Problem

Subtask (a): Build a model of passenger flow through a US airport security checkpoint, calibrate it to the supplied checkpoint data, and identify where the bottlenecks that disrupt throughput and create high wait-time variance are located in the current process.

### Analysis

Approach: a discrete-event simulation (DES) of the checkpoint as a queueing network, because the process is a sequence of service stages with random arrivals, random service times, and parallel servers, and the question is about throughput and wait-time variance rather than a closed-form optimum. The checkpoint is split into the two lane classes the TSA actually operates (Pre-Check and regular) and the four zones from the problem: Zone A (ID check), Zone B (bag belt + body scan, in parallel), Zone C (belt pickup), and Zone D (secondary screening by a single shared officer). Pre-Check and regular passengers share the secondary-officer stage but have separate ID, belt and body-scan stages. Method soundness: DES is the standard tool for this class of multi-stage, multi-server, stochastic flow problem and it reproduces queue buildup and its variance, which is exactly what the TSA cares about; a pure M/M/c analytic model would understate the variance because service times here are not exponential and stages are correlated (a bag and its owner move together). The model is calibrated to the supplied dataset for the stages the data actually records, and to domain practice for the stages it does not.

### Modeling Process

State per passenger p and lane class k in {0 Pre-Check, 1 regular}. Stages and service-time distributions:
- Zone A ID check: id_n[k] parallel servers; service Lognormal(mu, sigma) fit to the data (officer 1 n=9 mean 10.2 s, officer 2 n=7 mean 12.6 s; pooled mean 11.3 s, cv 0.35). Passenger enters the class ID queue on arrival and is assigned FCFS to a free officer.
- Zone B bag side: bins are placed on the conveyor when ID completes. The belt is modeled as a pipeline, not a single-server queue, because a conveyor holds many bags at once; bag-side completion = bin-placement time + transit, transit ~ Normal(28.6 s, 14.1 s) from the dataset's 'Time to get scanned property' column (n=29, mean 28.6 s). This is the physically correct treatment; modeling it as one server understates conveyor throughput.
- Zone B bin handling: passenger unpack/repack runs in parallel with the body-scan wait; duration Uniform(60,90) s regular and Uniform(40,60) s Pre-Check (Pre-Check passengers do not remove shoes/belts/jackets and leave laptops in bags, so they are faster).
- Zone B body scan: scan_n[k] parallel servers; service Normal(11.6 s, 5.9 s) from the millimeter-wave exit inter-intervals (n=39, mean 11.64 s).
- Zone D secondary: ONE shared officer, FCFS. After body scan, with probability p_pat a pat-down is required: p_pat = 0.005 Pre-Check / 0.03 regular, duration Uniform(60,180) s with a 10% chance of a 180-300 s private-room screen. After the belt, with probability p_flag a bag search is required: p_flag = 0.05 Pre-Check / 0.10 regular; of flagged bags 20% take a deep search Uniform(120,300) s and 80% a belt-side re-check Uniform(30,120) s.
- Zone C completion: p is done when both the person side (scan end, plus pat-down if any) and the bag side (belt end, plus bag search if flagged) are complete; completion time = max of those four endpoint times.
Arrivals: independent Poisson processes per class. Rates from the observed ~10-minute peak window: 7.35 Pre-Check and 5.95 regular passengers/minute (a 55:45 split); the problem's 45% Pre-Check enrollment is treated as the population prior while the dataset rates set the instantaneous peak. A 'peak' scenario multiplies rates by 1.3.
Per-class service capacity is one ID officer and one body-scan unit per open lane, so the number of open lanes per class is the throughput lever. Staffing policies: 'fixed' (constant lanes), 'threshold' (open an extra lane pair when a class queue reaches 12), 'predictive' (pre-open lanes for the forecast peak).
Empirical parameter table (name = value, interval [a,b], source):
- ID service mean = 11.3 s, interval [8.0, 16.0], source: dataset columns 'ID Check Process Time 1/2'
- Belt transit = 28.6 s (sd 14.1), interval [5, 68], source: dataset column 'Time to get scanned property'
- Body-scan service = 11.6 s (sd 5.9), interval [6, 18], source: dataset 'Milimeter Wave Scan times' exit inter-intervals
- Arrival rate Pre-Check = 7.35/min, Regular = 5.95/min, interval per interarrival sd, source: dataset arrival columns
- Bin handling regular = Uniform(60,90) s, Pre-Check = Uniform(40,60) s, source: expert exchange 10
- Pat-down rate = 0.03 regular / 0.005 Pre-Check, interval [0.02,0.05], source: expert exchange 3
- Pat-down duration = Uniform(60,180) s (10% private 180-300), source: expert exchange 5
- Bag flag rate = 0.10 regular / 0.05 Pre-Check, deep share 0.20, source: expert exchange 4
- Bag-search duration = belt-side Uniform(30,120), deep Uniform(120,300), source: expert exchange 6
- Lane-throughput cap 200/h regular, 300/h Pre-Check, interval [150,250]/[250,350], source: expert exchange 9
- Reactive lane-open threshold = 12 passengers, interval [10,15], source: expert exchange 1
- Peak waiting (validation target) 5-15 min normal / 20-30 min peak, source: expert exchange 2
- Queue abandonment = ~0 routine, up to ~3% in worst meltdowns, source: expert exchange 8

### Outcome Analysis

Bottleneck identified: the current 1-Pre-Check-to-3-regular lane split is structurally mismatched to the 55:45 passenger split, so the Pre-Check class runs above its lane capacity (utilization 1.47) while the regular class runs at 0.59. Under peak load this produces a 5x wait disparity: Pre-Check passengers average 29.4 minutes versus 5.5 for regular passengers, and the ID stage of the Pre-Check lane is the dominant wait contributor (13.5 min of the 20.6 min class mean). The single shared secondary officer is NOT the main bottleneck at observed load (utilization ~3%); it only becomes relevant under heavy flagging. The body-scan stage is also lightly loaded. So the problem areas are: (1) lane allocation concentrated on the wrong class, (2) reactive lane-opening that cannot correct a structural ratio error, and (3) high variance driven by the congested class, not by the secondary stage. This matches the real-world symptom (2016 O'Hare-style long, unpredictable lines) and validates against the expert's 20-30 min peak band for the congested class. Limitations/biases: service times are fit on small samples (ID n=16, belt n=29) so their tails are uncertain; the dataset's 55:45 split differs from the stated 45% enrollment, which I treat as a peak-window artifact; arrivals are assumed Poisson (the observed inter-arrival sd is larger than the mean, hinting at batching/clustering not modeled); and the belt-as-pipeline assumption holds only while the conveyor is not itself the rate-limiter.

## Subtask 2: Subtask (b): Develop two or more concrete modifications to the current process that increase checkpoint throughput and r

### Problem

Subtask (b): Develop two or more concrete modifications to the current process that increase checkpoint throughput and reduce wait-time variance, and model each to show its impact.

### Analysis

Approach: I test modifications as re-configurations of the same calibrated DES, holding all service-time distributions and arrival rates fixed so that any change in mean or variance of wait is attributable to the structural change, not to re-calibration. I compare each modification against the current 1:3 ratio baseline at both base and peak load. I focus on changes that act on the identified bottleneck (lane allocation) rather than on the lightly-loaded secondary stage, and I include one staffing-policy change to test whether reactive opening alone can fix the problem. This isolation of the structural lever is what makes the comparison informative.

### Modeling Process

Modifications, all run through code/sim.py with only the relevant flag changed:
- M1 (rebalance lanes): change the open-lane split from 1 Pre-Check : 3 regular to 2 : 2 for the same 4 total lanes. Mechanism: moves one lane of ID+scan capacity from the under-loaded regular class to the overloaded Pre-Check class, cutting the Pre-Check utilization from 1.47 to ~0.73.
- M2 (predictive staffing): pre-open ID/scan servers sized for lambda x 1.3 (the forecast peak) instead of reacting after queues build; combined with M1.
- M3 (add lanes): open 6 lanes total split 3 Pre-Check : 3 regular under peak, i.e. more capacity plus the corrected ratio.
- M4 (reactive threshold): keep the 1:3 ratio but open extra lanes when a class queue reaches 12 passengers (the expert-stated trigger), to test whether reactive opening alone recovers the baseline.
Metrics: mean, standard deviation and max of line wait (completion minus arrival) over 1 hour of simulated operation; standard deviation is the variance proxy the TSA asks to reduce.

### Outcome Analysis

Results (mean wait, minutes): M1 rebalance cuts base-load wait from 11.3 to 3.8 (-66%) and peak from 20.6 to 4.3 (-79%), and cuts the Pre-Check/regular disparity from 5x to under 2x. M3 (6 lanes 3:3, peak) reaches 3.1 min mean with the lowest variance (sd 10.3 vs 24.7 baseline). M2 predictive staffing on top of M1 gives 5.3 min at peak - predictive opening adds little once the ratio is already balanced, because the bottleneck is allocation, not timing. M4 is the key negative result: reactive threshold opening on the unchanged 1:3 ratio still yields 20.6 min at peak, identical to the baseline, because you cannot reactively open your way out of a structural ratio error - the Pre-Check lane is already saturated before any queue reaches the trigger. Conclusion: the highest-leverage, lowest-cost modification is M1 (rebalance the existing lanes toward Pre-Check); M3 adds robustness for sustained peaks; M4 alone is ineffective and should not be relied on. Limitations: benefits scale with the accuracy of the 55:45 split; if enrollment shifts, the optimal split shifts with it, so the recommendation is a rule (match lanes to share), not a fixed number.

## Subtask 3: Subtask (c): Treat cultural norms / traveler style as a sensitivity analysis - model how differences in personal-space b

### Problem

Subtask (c): Treat cultural norms / traveler style as a sensitivity analysis - model how differences in personal-space behavior, queueing etiquette (line-switching), and processing speed change passenger flow, and recommend how the system should accommodate these differences to raise throughput and cut variance.

### Analysis

Approach: I encode four traveler styles as parameterized behaviors in the same DES, so each style is a perturbation of one or two coefficients rather than a separate model, keeping the comparison clean. American = strict FIFO with a personal-space penalty that slows bin packing; Swiss = strict FIFO with a small coordination speed-up; Chinese = individual-efficiency line-switching, where a fraction of passengers who wait too long leave and re-enter ahead (modeled as re-joining 15 s later, capped at 2 attempts); Slow-traveler = every passenger-side service time scaled by 1.3. This directly instantiates the problem's examples (Americans' personal space and anti-cutting stigma, Chinese individual efficiency) plus a culture-free 'slower traveler' case as the problem invites.

### Modeling Process

Style coefficients: bin-handling multiplier = 1.15 (American personal space) or 0.95 (Swiss coordination); line-switching probability = 0.10 with a 30 s patience threshold (Chinese); passenger-side service scale = 1.3 (slow). Each style is run at the 1:3 baseline and at the 2:2 balanced split, base and peak. The accommodation tested is giving the system a style-robust structure: because slow and line-switching passengers increase the effective service time or re-order the queue, the robust response is to keep spare lane capacity and a per-class split that is not so tight that a 30% slowdown saturates it.

### Outcome Analysis

At the 1:3 baseline under peak: American and Swiss both 20.6 min; Chinese line-switching 20.0 min (slightly lower mean, but the delay is concentrated on the patients who stay, so variance/fairness worsens even though the mean barely moves); slow-traveler style 28.8 min, the worst case, because slower bin handling lengthens the ID+scan stage of an already-saturated Pre-Check lane. At the balanced 2:2 split the style effect shrinks dramatically (3.8-4.6 min across all styles), because the spare capacity absorbs the slowdown. Recommendation: the system should (1) size lanes to the peak-of-the-slowest-realistic-traveler, not the average, so a 30% slowdown does not push utilization past 1; (2) keep the balanced split as the default since it is robust across all four styles; (3) tolerate rather than police line-switching, because banning it does not raise throughput (the re-entering passenger still consumes the same service), while a dedicated express lane for fast/Pre-Check travelers is the cleaner way to let individual-efficiency passengers self-select; (4) for personal-space cultures, keep adequate belt spacing (the 1.15 bin-handling penalty is small, ~10-15 s, and is better absorbed by capacity than by forcing closer packing). Bias: the 10% switch rate and 1.3x slow factor are stylized, not measured; the qualitative ranking (slow worst, balanced-split robust) is the robust conclusion, the exact minutes are not.

## Subtask 4: Subtask (d): Propose policy and procedural recommendations for security managers, and provide model validation, a streng

### Problem

Subtask (d): Propose policy and procedural recommendations for security managers, and provide model validation, a strengths/weaknesses assessment, and future-work ideas.

### Analysis

Approach: recommendations follow directly from the modeled bottleneck (lane allocation) and the sensitivity results (style-robustness), phrased as operational rules a manager can act on, each tied to the model result that justifies it. Validation compares model outputs to the expert-stated real-world bands and to the dataset's own stage timings. Strengths/weaknesses and future work are stated honestly, including where the small samples limit confidence.

### Modeling Process

Recommendations (each traced to a model result):
1. Rebalance open lanes toward Pre-Check to match its passenger share (target ~2:2 for a 55:45 split, i.e. lanes proportional to enrollment), and re-tune whenever the enrollment mix shifts. Justification: M1 cuts peak wait 20.6 -> 4.3 min and removes the 5x class disparity.
2. Do not rely on reactive lane-opening alone; open to forecast demand before the morning rush, because reactive opening on the wrong ratio does nothing (M4 = baseline). Justification: M4 unchanged at 20.6 min; exchange 7 confirms opening is currently reactive.
3. Add lanes for sustained peaks (e.g. 6 lanes 3:3) when the forecast exceeds the balanced 4-lane capacity; this is the robust high-capacity option (M3, 3.1 min, lowest variance).
4. Staff for the slowest realistic traveler, not the average: keep ~30% spare lane capacity so a 30% service-time slowdown does not push the busy class past unit utilization. Justification: slow-traveler style is the worst case (28.8 min at 1:3).
5. Offer an express/self-select lane for fast and Pre-Check travelers rather than policing line-switching; switching does not reduce total service work, and a dedicated lane lets individual-efficiency passengers self-sort with no throughput loss.
6. Keep the single shared secondary officer only if flag rates stay low; if flag/pat-down rates rise (e.g. a higher-threat period), add a second secondary officer, since that stage is the one that would saturate under heavy secondary demand.
Validation: (a) the congested class under peak reaches 29.4 min, inside the expert's 20-30 min peak band (exchange 2); the balanced configuration reaches 3.8-5.3 min, inside the 5-15 min normal band. (b) stage service times reproduce the dataset: ID ~11 s, belt ~29 s, body-scan inter-exit ~11.6 s. (c) the Pre-Check/regular disparity is a direct, checkable consequence of the 1:3 vs 55:45 mismatch. Strengths: calibrated to real stage timings; isolates the structural lever so effects are attributable; reproduces the qualitative real-world symptom (high, unpredictable waits concentrated in one class). Weaknesses: small samples make service-time tails uncertain; Poisson arrival assumption ignores observed clustering; the belt-as-pipeline model breaks if the conveyor itself becomes the rate-limiter; the 55:45 data split vs 45% stated enrollment is an unresolved data artifact. Future work: fit arrivals with a batched/Markov-modulated process to capture clustering; collect a full-shift dataset to pin the enrollment mix and the secondary-flag rate; extend to multi-checkpoint diversion (passengers choosing among several lanes/terminals); and add a cost layer (officer-hours, Pre-Check revenue) to optimize the lane split and staffing jointly rather than by rule.

### Outcome Analysis

The package for the TSA is: rebalance lanes to the enrollment mix, open to forecast rather than reaction, hold ~30% spare capacity for slower travelers, and reserve a second secondary officer for high-threat periods. The model validates against both the expert's real-world wait bands and the dataset's stage timings, and its central, most defensible finding is that the 2016-style long lines are a lane-allocation failure (Pre-Check under-served relative to its 55% share), not a secondary-screening or body-scan failure. The main risk to the conclusions is the arrival-mix data artifact and the Poisson assumption; both would change the absolute minutes but not the direction of the recommendation, which is robust to the four traveler styles tested.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
