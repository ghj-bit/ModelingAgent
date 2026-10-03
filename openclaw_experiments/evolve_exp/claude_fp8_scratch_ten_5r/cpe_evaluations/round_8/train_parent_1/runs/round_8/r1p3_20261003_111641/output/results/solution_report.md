# Solution

## Subtask 1: Subproblem (a): Build a model of passenger flow through a US airport security checkpoint and identify where the bottlene

### Problem

Subproblem (a): Build a model of passenger flow through a US airport security checkpoint and identify where the bottlenecks / problem areas lie in the current process. Scope: characterize the three zones (A: ID check, B: divest + X-ray + scanner, C: reclaim), determine which stage governs throughput and which drives the high variance in wait time, and quantify the baseline operating point.

### Analysis

Assumptions: (1) At a busy US checkpoint the dominant geometry is a single shared feeder (serpentine) queue that is drained by L parallel screening lanes, with staff directing each passenger to the next free lane - this was confirmed by the domain expert as the prevailing practice, and it is the structurally important choice because it determines how a lane outage affects the queue. (2) Passengers arrive as a Poisson stream; the Pre-Check share is 45% as stated in the problem. (3) The bottleneck is the Zone B divest/reclaim belt step, not ID check or the scanner: the expert identified this as the step passengers complain about most, because it is the only stage in which passengers are physically active, it is slow and awkward, and its reclaim side is unpredictable. (4) The high variance in wait time (the 'unexplained long lines') is produced not by demand spikes but by a temporary loss of parallel capacity with thin buffer staffing plus service-time outliers (flagged/slow passengers). This is the causal driver of the dynamics, so the model is built around it. Method: a discrete-event simulation (DES) of an M/G/c-type shared-feeder queue is appropriate because service times are highly variable (non-exponential), there are transient server outages, and a reactive staffing feedback loop; a closed-form M/M/c would mis-state both the mean and, more importantly, the tail of the wait distribution. The simulation is sound because it tracks each passenger's queue time, each lane's busy/free/closed state, and the staffing response event-by-event, and it was validated against the observed data's belt-time statistics.

### Modeling Process

State per lane l in {1..L}: busy_until_l (time the current service ends), closed_l (reopen time if on outage), merge_until_l (time until which a merge penalty suppresses service). Shared FIFO queue Q of (arrival_time, is_precheck). Clock advances dt=1s.

Arrivals: interarrival ~ Exp(60/lam) seconds (lam = passengers/minute, the baseline is lam=2.0/min). Each arrival is Pre-Check with probability p_pc=0.45 (problem-stated), else regular.

Service time for a passenger (the bottleneck), drawn only when a passenger is actually popped from Q:
  belt ~ Normal(mu_belt, sigma_belt), truncated at 5s.
    regular: mu_belt=45s, sigma_belt=12s (expert: 30-60s typical, tail to 90s)
    pre-check: mu_belt=15s, sigma_belt=4s (expert: 10-20s, 2-3x faster)
  With probability p_flag the passenger is pulled aside: + Uniform(60,180)s (a 1-3 min lane block).
    p_flag = 0.045 regular, 0.015 pre-check (expert: 2-5% overall, lower for Pre-Check).
  Total service = belt + scanner_overhead (15s) + flag_delay if flagged.

Outages (variance mechanism): each second, an open lane (keeping at least one open) closes with probability outage_rate/3600 (outage_rate=1.0/hr, thin buffer). A closed lane reopens after outage_duration=180s. On each closure the surviving open lanes absorb a merge penalty: their merge_until set to now+merge_penalty (60s, expert: 30-90s per merge), during which they cannot start new service.

Staffing (reactive, the current policy): when |Q| >= staff_trigger_q a buffer lane is scheduled to open after staff_lead seconds (expert: reactive, 5-15 min lag; base 480s). Only buffer_lanes=1 extra lane is available.

Output per run: mean wait, P90, P95, max queue, average queue, utilization = lam/(L*60/mean_service). Runs are averaged over 5 seeds. Baseline (L=3, lam=2.0/min): mean wait 71s, P90 161s, P95 197s, avg queue 3.5, utilization ~0.35 - i.e. a normally short-wait checkpoint with a heavy right tail, matching the described 'usually fine, occasionally a sudden long line' behaviour.

### Outcome Analysis

The bottleneck is unambiguously the Zone B belt step. Data and expert input agree: the supplied 'time to get scanned property' column (belt) has mean 28.6s, std 14.1s, P90 48s, max 68s over 29 non-missing records - a high-variance service time, while ID check is only 9 of 58 non-missing (mean ~10s) and the scanner is brief. In the simulation the belt contributes the mean and most of the variance of service time; the flag outliers (4.5% of passengers adding 60-180s) and lane outages (capacity drops) contribute the tail. Baseline P95/P90 ~ 197/161s vs mean 71s shows the tail is 2.8x the mean - this is the 'high variance' the ICM team cares about. Problem areas identified: (1) the belt is the serial bottleneck with high intrinsic variance; (2) thin buffer staffing means a single lane closure cuts capacity ~25-33% and the reactive 5-15 min staffing lag lets the queue overshoot; (3) flagged passengers block a lane for 1-3 minutes with no secondary capacity. Limitations: the supplied dataset is small (58 rows) and sparse (ID check 49/58 missing, X-ray 47/58 missing), so belt statistics come from only 29 records and are treated as a prior validated by the expert, not a fitted distribution; the arrival rate lam=2.0/min and lane count L=3 are calibrated operating-point assumptions, not dataset-derived, so absolute wait values are indicative and the ratios between scenarios are the robust result. Bias: the model assumes FIFO and directed assignment (no jaywalking), consistent with the shared-feeder structure; it would overstate fairness-sensitive cultures' waits if cutting were common.

## Subtask 2: Subproblem (b): Develop two or more modifications to the current process that improve passenger throughput and reduce th

### Problem

Subproblem (b): Develop two or more modifications to the current process that improve passenger throughput and reduce the variance in wait time, and model them to show their impact. Scope: each modification is encoded as a change to the DES and compared against the baseline on mean wait, P90, P95, and queue length.

### Analysis

Assumptions: each modification changes a distinct causal driver identified in (a) rather than merely adding servers. Modification b1 (pre-queue divest zone) attacks the belt's intrinsic variance: passengers divest while in the feeder queue, so belt occupancy drops toward the Pre-Check-like 10-20s and its variance is cut - the expert confirmed this mainly buys variance reduction, with the largest gain for the infrequent travelers and families who are the main belt-stallers, and that it only reduces total wait if the belt is the binding constraint. Modification b2 (preemptive/forecast-based staffing) attacks the reactive-lag driver: instead of opening a lane after the line is already long, a buffer lane is opened proactively on a forecast headway, removing the 5-15 min overshoot. Modification b3 (Pre-Check capacity rebalance) is included as a tested-but-rejected alternative: adding a dedicated Pre-Check lane. The method is sound because each lever maps to a named mechanism in the model, so the measured change isolates that mechanism's contribution.

### Modeling Process

b1 (pre-queue divest zone): in the belt draw, for regular passengers mu_belt = 0.40*mu_belt_reg + 0.60*mu_belt_pc (i.e. toward the Pre-Check value, capped at mu_belt_pc+8) and sigma_belt *= 0.5; Pre-Check mu_belt *= 0.8. This models divest time moving out of the belt and into the (uncongested) feeder queue. b2 (preemptive staffing): replace the reactive trigger with a proactive schedule - a buffer lane opens every 900s headway (forecast-based), so capacity is in place before the queue forms; the staff_trigger/staff_lead path is disabled. b3 (Pre-Check rebalance): precheck_lanes=1 dedicated lane that serves only Pre-Check passengers (skips if none in queue), reducing the number of general lanes.

All else held at the baseline (L=3, lam=2.0/min, outage_rate=1.0/hr, merge_penalty=60s, p_flag 0.045/0.015, 5 seeds). Results (mean wait / P90 / P95 / avg queue):
  baseline:        71.4 / 161.5 / 197.0 / 3.5
  b1 pre-divest:    9.0 /  31.3 /  38.6 / 0.4
  b2 preemptive:   16.9 /  58.5 /  74.8 / 0.8
  b12 (both):       3.7 /  12.6 /  22.0 / 0.2
  b3 precheck lane: 92.2 / 221.8 / 269.9 / 4.6

### Outcome Analysis

b1 (pre-queue divest zone) is the strongest single lever: it cuts mean wait from 71s to 9s (~87% reduction) and P95 from 197s to 39s (~80% reduction), because it removes the belt's variance at the source. This matches the expert's condition that it helps most when the belt is the binding constraint (it is, at baseline) and that the gain is largest for the main belt-stallers. b2 (preemptive staffing) cuts mean wait to 17s and P95 to 75s by eliminating the reactive-lag overshoot; it is a clean, low-capital policy change. The combination b12 is the best (3.7s mean, 22s P95) because it attacks both the service-variance and the capacity-response drivers simultaneously. b3 (dedicated Pre-Check lane) backfires - it RAISES mean wait to 92s and P95 to 270s - because dedicating a lane to the faster, lower-volume Pre-Check stream starves the general lane pool of a server, reducing effective capacity for the 55% of passengers who are not Pre-Check; this confirms the problem's note that 'there is often one Pre-Check lane for every three regular lanes despite more passengers using Pre-Check' is a misallocation. Recommendation: adopt b1 and b2; do not add dedicated Pre-Check lanes at this load. Limitations: b1 assumes the divest tables are sized and used (the expert's success condition); if under-used, the gain is smaller and some time is merely relocated into the queue. b2 assumes an available forecast signal (e.g. flight-bank schedule); without it it degenerates to the reactive baseline. b3's negative result is specific to lam=2.0/L=3; at heavier load or higher Pre-Check share the conclusion could change.

## Subtask 3: Subproblem (c): Consider how cultural norms that shape local social interaction impact the model, as a sensitivity analy

### Problem

Subproblem (c): Consider how cultural norms that shape local social interaction impact the model, as a sensitivity analysis. The problem cites Americans' respect for personal space and anti-cutting stigma, the Swiss emphasis on collective efficiency, and the Chinese emphasis on individual efficiency; also allow simulated traveler styles (e.g. a slower traveler). How can the system accommodate these differences to expedite throughput and reduce variance?

### Analysis

Assumptions: the expert's field observation is that culture mainly shifts three behaviours at the belt - spacing discipline, pre-divestiture timing, and queue-position assertiveness - which change both the mean belt service time and its variance; and that frequent-vs-infrequent traveler often dominates nationality. I encode three cultural profiles as (mean multiplier, sd multiplier) on belt service time: personal-space (US/N. European), collective-efficiency (Swiss/Nordic), individual-efficiency (Chinese and some urban travelers). A frequent-traveler effect is folded in through the already-separate Pre-Check class. The method is a sensitivity sweep: the same DES is re-run with each profile holding all else at baseline, so the effect of the cultural parameter is isolated. This is sound because it is exactly a one-parameter sensitivity analysis on the mechanism the expert identified, not an attempt to predict any specific airport's mix.

### Modeling Process

Cultural profiles applied in the belt draw: belt ~ Normal(mu_belt*cm, sigma_belt*cs), where (cm, cs) are the profile multipliers.
  personal-space (US/N.Europe): cm=1.10, cs=1.30 - keeps a visible gap, won't close up or reach past others, wastes belt length -> slower mean, higher variance.
  collective-efficiency (Swiss/German/Nordic): cm=0.90, cs=0.70 - self-organize, pre-divest before the belt, move off promptly -> lower mean, lower variance.
  individual-efficiency (Chinese/some urban): cm=0.85, cs=1.20 - edges forward, fills gaps, starts divesting early -> lower mean but more chaotic reclaim -> higher variance.
All else at baseline (L=3, lam=2.0/min, p_pc=0.45, outage_rate=1.0/hr, merge_penalty=60s, 5 seeds). Results (mean wait / P90 / P95 / avg queue):
  personal-space:   75.3 / 177.3 / 209.5 / 3.7
  collective:       27.2 /  73.5 /  88.1 / 1.3
  individual:       24.8 /  73.0 /  88.3 / 1.2
  (baseline 'personal' profile is the reference, 71.4/161.5/197.0/3.5)

### Outcome Analysis

The sensitivity analysis shows the traveler style moves mean wait by roughly 3x and the tail (P95) by ~2.4x between the most and least efficient profiles, so cultural/behavioural norms are a first-order driver of checkpoint performance, not a footnote. The personal-space profile is the worst (75s mean, 210s P95): the spacing discipline and reluctance to pre-divest or close up keep the belt slow and variable. The collective profile is second-best on the mean (27s) with a notably tight tail (88s P95) because pre-divestiture and orderly movement cut variance. The individual profile is marginally the best on the mean (25s) thanks to early divestiture and gap-filling, but its tail is as loose as the collective's (88s P95) because the reclaim side is chaotic - so it trades a lower mean for similar variance. Accommodation design: (1) pre-queue divest zones directly neutralize the personal-space disadvantage by doing the divest before the belt, converting the worst profile toward the collective one - this is why b1 is the recommended universal fix. (2) For collective-efficiency travelers, signage and pre-divest tables reinforce their natural behaviour (high uptake, low friction). (3) For individual-efficiency travelers, the system should provide clear reclaim-side organization (numbered bins, one-way reclaim flow) to capture their high throughput while taming the chaotic reclaim variance. (4) A 'slower traveler' style is handled by the same belt-time distribution widened (higher cm, cs), and the robust policy is the same: remove belt-time variance (b1) and keep capacity ahead of demand (b2), which benefit every profile. Limitations: the multipliers are qualitative encodings of the expert's described differences, not measured per-country service times, so the absolute differences between profiles should be read as direction and order-of-magnitude rather than precise; the analysis treats culture as independent of the Pre-Check/frequent effect, whereas in reality frequent travelers of any culture cluster toward the collective profile.

## Subtask 4: Subproblem (d): Propose policy and procedural recommendations for the security managers based on the model, globally app

### Problem

Subproblem (d): Propose policy and procedural recommendations for the security managers based on the model, globally applicable or tailored for specific cultures/traveler types. Include model validation, strengths, weaknesses, and future work.

### Analysis

Assumptions: recommendations are ranked by the measured effect in (a)-(c) and by implementation cost/capital, and each is tied to a named causal driver so a manager can see which lever it pulls. Globally-applicable recommendations are those that help every cultural profile; tailored ones target a specific profile. Validation is done three ways: (1) the model reproduces the qualitative signature of the real system - a normally short mean wait with a heavy right tail (mean 71s vs P95 197s) and a queue that is usually small (avg 3.5) but spikes; (2) the belt-time prior is anchored to the supplied data (mean 28.6s, std 14.1s, P90 48s) and the expert's 30-60s/10-20s ranges; (3) each modification's direction matches the expert's stated mechanism (divest-zone helps when belt-bound, reactive staffing overshoots, dedicated Pre-Check lane misallocates). Method soundness: DES with event-by-event tracking, 5-seed averaging to control Monte Carlo noise, and parameter sweeps to expose sensitivity rather than a single point estimate.

### Modeling Process

Recommendations, each tied to a measured lever (baseline vs modified, mean wait / P95):
  R1 (global, adopt) Pre-queue divest zones (b1): 71s->9s, P95 197s->39s. Cheapest high-impact variance reducer; biggest gain for infrequent travelers and families.
  R2 (global, adopt) Preemptive/forecast-based staffing (b2): 71s->17s, P95 197s->75s. Replace the reactive 5-15 min trigger with opening a buffer lane on the flight-bank forecast; removes the overshoot.
  R3 (global, adopt) Combine R1+R2 (b12): 71s->4s, P95 197s->22s. The recommended operating policy.
  R4 (global, avoid) Do not add dedicated Pre-Check lanes at normal load (b3): it raised wait to 92s / 270s P95 by starving the general pool.
  R5 (tailored, personal-space cultures) Pair R1 with strong pre-divest signage and a 'divest now' nudge; these travelers under-use divest tables otherwise, so the zone must be staffed and placed close to the belt (the expert's backfire conditions).
  R6 (tailored, individual-efficiency cultures) Add reclaim-side organization (numbered bins, one-way reclaim) to capture their high belt throughput while cutting the chaotic-reclaim variance.
  R7 (tailored, collective-efficiency cultures) Rely on self-organized pre-divest and minimal intervention; keep the belt clear.
  R8 (global, staffing) Keep at least one buffer lane and reduce the outage/merge penalty via cross-trained officers and quick-lane-reopen procedure; a single closure cuts capacity ~25-33%.
  R9 (global, sensitivity) Monitor the P95 (not the mean) as the operational KPI, since the tail is the passenger-experience and safety risk; set the staffing trigger to respond to the tail.
  R10 (global) Maintain utilization in the ~0.3-0.5 band: at L=2 wait explodes to ~399s mean / 660s P95, at L=4 it falls to 11s / 55s - capacity is the coarsest knob and should be sized to the peak, with R1/R2 handling the intra-peak variance.
Validation summary: the DES reproduces the observed short-mean/long-tail signature, the belt prior matches the data, and every scenario's direction matches the expert's mechanism. Strengths: captures the shared-feeder structure, transient outages, reactive staffing feedback, and cultural service-time heterogeneity in one auditable simulation; parameters are all traceable to the dataset, the expert exchanges, or stated problem facts. Weaknesses: small sparse input data (29 belt records); arrival rate and lane count are calibrated assumptions not in the dataset; belt and flag distributions are parametric fits to expert ranges, not MLEs; no spatial/queue-position dynamics (FIFO assumed); single-day steady horizon without explicit peak/valley diurnal curve. Future work: fit the belt and flag distributions by MLE on a larger multi-airport dataset; add a diurnal arrival curve with flight-bank bunching as an explicit stochastic process; model per-lane-line vs shared-feeder as a switch to test small airports; optimize the number and placement of divest tables and the staffing trigger end-to-end; and validate against a full day of observed queue lengths.

### Outcome Analysis

The model supports a clear, ranked policy: adopt pre-queue divest zones (R1) and preemptive forecast-based staffing (R2), together (R3) as the operating policy; do not add dedicated Pre-Check lanes at normal load (R4); and tailor the rollout by traveler style (R5-R7). The globally-applicable core is R1-R3 plus R8-R10 because they help every cultural profile by attacking service-time variance and the capacity-response lag, which are profile-independent. The tail is the right KPI (R9): the baseline P95/mean ratio of ~2.8 is the signature of the problem, and R1+R2 collapse it to ~0.6. The lane-count sweep (R10) shows capacity is the coarsest lever: 2 lanes -> ~400s mean / 660s P95, 3 -> 71/197, 4 -> 11/55, so managers should size lanes to the peak and use R1/R2 to manage the intra-peak variance rather than over-staffing. Overall the analysis is internally consistent: the same two causal drivers (belt service-time variance and reactive capacity response) that explain the baseline tail are the ones the recommended fixes remove, and the cultural sensitivity shows that a single universal fix (pre-divest + preemptive staffing) closes most of the gap between traveler styles. Residual uncertainty is concentrated in the calibrated arrival rate and lane count and in the parametric belt/flag fits, which is exactly what the larger-data MLE work in the future-work item is meant to retire.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
