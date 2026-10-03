# Solution

## Subtask 1: Part (a): Build a model of passenger flow through a US airport security checkpoint and identify where the bottlenecks ar

### Problem

Part (a): Build a model of passenger flow through a US airport security checkpoint and identify where the bottlenecks are. Goal: capture how a passenger moves through the ID check, divesting/belt-loading, body scan, X-ray, and retrieval steps, and show which station(s) limit throughput and drive wait-time variance.

### Analysis

The checkpoint is modeled as a pipeline of single-server stations per screening lane, with one lane per group of passengers (fixed lane membership at arrival, confirmed as the prevailing practice). The data (2017_ICM_Problem_D_Data.csv) was cleaned before use: the 8 columns hold mixed formats (hh:mm.s timestamps for arrivals and station exits, m:ss durations for the belt step) and many missing values (ID-check columns 1 and 2 are ~85% empty, X-ray column 2 ~93% empty, belt column ~50% empty). Repair steps: (1) parsed all timestamp/duration strings to seconds with a single parser; (2) kept only valid numeric entries and computed statistics on the non-missing subsets, recording n per column; (3) verified arrival columns are non-decreasing (no negative inter-arrival gaps) so they are genuine arrival times, not out-of-order records. Because the per-station process-time columns are too sparse to give a full per-passenger trace (58 Pre-Check and 47 regular arrivals, but only 9/7 ID, 40 mmwave, 11/4 X-ray, and 29 belt observations), the model uses the *station exit gaps* from the dense columns (mmwave, X-ray, belt) as throughput calibration and treats the chain structure from the process description. Method: a discrete-event simulation (DES) of the lane pipeline, chosen because the process is serial with overlapping sub-steps (body scan and X-ray run concurrently with belt-loading), queueing is FIFO per lane, and stochastic service times are needed to reproduce wait-time variance. DES is sound here because it represents the actual event ordering (arrive -> ID -> divest -> {scan, xray} -> retrieve) that an analytic M/M/1 chain cannot, since the scan and X-ray overlap.

### Modeling Process

Let a lane be a pipeline of stations. Per passenger i in a lane:
- Arrival time A_i (Poisson, rate lambda per lane).
- ID check: single server, service S_id ~ Exp(mu_id), mu_id = 1/T_ID, T_ID = 18 s.
- Divesting/belt-loading: self-service, D_i ~ Lognormal with mean T_DIV = 28.6 s and CV = 0.49 (both from the dataset belt column, n=29). Pre-Check passengers use D_i * 0.70 (they skip shoes, belts, light jackets; laptops stay in bags).
- Body scan: server S_scan ~ Exp(mu_scan), T_SCAN = 11.6 s (mmwave exit-gap mean, n=40), start = max(ID_end, divest_end, scan_server_free).
- X-ray: continuous-flow server, per-bag S_xray ~ Exp(mu_xray), T_XRAY = 7.5 s (X-ray exit-gap mean, n=11), start = max(divest_end, xray_server_free). With probability P_FLAG = 0.05 a bag is flagged and the server is delayed T_FLAG = 60 s.
- Retrieval: T_RETR = 8 s after max(scan_end, xray_end).

The lane's pacing time is max(ID_end, divest_end): the next passenger cannot begin their ID check until the current one has cleared the shared divesting area, so divest time feeds back into the queue (this is the key throughput coupling). Queue wait for passenger i is W_i = divest_start_i - A_i. Throughput time is total_i = retrieve_end_i - A_i. The baseline checkpoint is 1 Pre-Check lane + 3 regular lanes (the stated 1:3 ratio), each at rush-hour load lambda = 54 pax/hr (utilization rho = lambda*T_cycle, T_cycle = T_ID + T_DIV = 46.6 s, giving rho ~ 0.70, the 'saturated but growing' regime). Flag events and the lognormal divest tail are the variance sources. Simulation: 30-minute horizon, 5 seeds per scenario, event-driven (arrival, serve, and surge-open events on a priority queue).

Parameter table (empirical inputs):
- P_CUT = 0.02, interval [0.01, 0.05], source: expert exchange 2 (cut-in share, well under 5%).
- P_FLAG = 0.05, interval [0.03, 0.08], source: expert exchange 6 (a few percent of bags flagged).
- T_FLAG = 60 s, interval [30, 120], source: expert exchange 6 (secondary search ~1-2 min).
- SURGE_LAG = 300 s, interval [120, 600], source: expert exchange 8 (opening a lane takes minutes to tens of minutes).
- T_ID = 18 s, interval [15, 25], source: expert exchange 9 (ID check is brief, tens of seconds).
- T_DIV = 28.6 s, interval [dataset 5, 68], source: task dataset, 'Time to get scanned property' column, mean over n=29.
- T_SCAN = 11.6 s, interval [dataset 3.5, 37.5], source: task dataset, mmwave exit-gap mean, n=40.
- T_XRAY = 7.5 s, interval [dataset 1.7, 25.9], source: task dataset, X-ray exit-gap mean, n=11.
- T_RETR = 8 s, interval [5, 15], source: estimate (post-X-ray belt retrieval).
- PRE_DIV_SCALE = 0.70, interval [0.6, 0.8], source: problem statement (Pre-Check skips shoes/belts/jackets, laptops in bag).
- lambda per lane = 54 pax/hr, interval [utilization 0.70, 0.85], source: expert exchange 7 (rush-hour lanes saturated, demand exceeds capacity).

### Outcome Analysis

Baseline results (5-seed mean): Pre-Check lane mean wait 899 s (p90 1587 s), regular lanes mean wait 302 s (p90 592 s), overall mean wait 567 s with standard deviation 479 s. The dominant bottleneck is the single Pre-Check lane, which is structurally overloaded: it carries the entire Pre-Check arrival stream (the dataset shows Pre-Check arrivals running faster, 392/hr vs 278/hr for regular, in the 10-minute window) into one lane, while the three regular lanes each carry only a third of the regular stream. This matches the problem statement's observation that 'there is often one Pre-Check lane open for every three regular lanes, despite the fact that more passengers use the Pre-Check process.' The second-order bottleneck is the divesting/belt-loading step within every lane (the slowest station, 28.6 s mean with a heavy lognormal tail), which paces each lane's throughput; the body scan (11.6 s) and X-ray (7.5 s) overlap with divesting and do not extend the cycle. Flagged-bag secondary searches (5% of bags, 60 s each) inject sporadic 60-s server delays that, when they cluster, produce the long tail of the wait distribution — the high variance the problem attributes to 'unexplained and unpredicted long lines.' Limitations: the dataset is a single 10-minute window from one checkpoint, so arrival rates are a point estimate of a peak; the ID-check and X-ray columns are too sparse to fit their service distributions directly (we use expert-calibrated exponential services and the dense mmwave/belt columns for the throughput-critical stations); the model assumes stations stay staffed over the 30-min window (breaks are ~2-hour-scale). Biases: exponential ID service may understate the regularity of real ID checks; the 0.70 Pre-Check divest factor is a single scalar for all skipped items.

## Subtask 2: Part (b): Develop two or more modifications to the current process that improve passenger throughput and reduce wait-tim

### Problem

Part (b): Develop two or more modifications to the current process that improve passenger throughput and reduce wait-time variance, and model them to show the impact.

### Analysis

Two modifications were modeled, both grounded in the bottleneck diagnosis from part (a): (1) rebalancing the lane allocation so Pre-Check and regular passengers each get capacity proportional to their demand, and (2) replacing fixed-lane membership for regular passengers with a single shared line that routes each arrival to the shortest regular queue. A third candidate, 'early divesting at the back of the line,' was explicitly rejected after consultation: the prevailing practice is that divesting is coupled to the belt/bins/table only at the front of the lane, and only a small minority (frequent travelers, Pre-Check) would unload early, so it would not meaningfully relieve the divest bottleneck. A 'surge lane' (opening a spare lane when a queue exceeds a threshold) was also modeled as a baseline-adjacent response and found to be limited by the ~5-minute lead time to staff and power a new lane. Each modification is run in the same DES under identical arrival and service parameters, so differences are attributable to the routing/allocation change alone.

### Modeling Process

Modification 1 — lane-allocation rebalance (precheck_ratio): change the lane configuration from 1 Pre-Check : 3 regular to 2 Pre-Check : 2 regular, splitting the Pre-Check stream across two lanes so each Pre-Check lane carries half the Pre-Check load. All station services, arrival rates (per lane), and the divest-feedback coupling are unchanged; only the lane count per group changes. This directly attacks the diagnosed overload: the single Pre-Check lane's effective load is halved, moving its utilization from the unstable region back into the stable range.

Modification 2 — shared line for regular passengers (shared_line): regular arrivals no longer commit to a fixed lane at joining; instead each regular arrival is routed to the regular lane with the minimum current queue length (shortest-queue join, ties broken uniformly). Pre-Check routing is unchanged. This is the classic 'one line, many servers' arrangement and it equalizes queue lengths across the regular lanes, which is what reduces wait-time *variance* even when it does not change mean throughput.

Surge lane (surge, for contrast): the baseline plus a rule that when the maximum lane queue first exceeds a threshold (15 passengers), a spare lane is opened after SURGE_LAG = 300 s; 50% of arriving Pre-Check passengers are then routed to it. This represents the realistic 'open more capacity' response.

Metrics compared: mean wait, standard deviation of wait, and 90th-percentile wait, for Pre-Check, regular, and overall, over 5 seeds each.

### Outcome Analysis

Results (5-seed means): Modification 1 (rebalance 2:2) is the largest win — overall mean wait falls from 567 s (baseline) to 549 s and, more importantly, overall wait standard deviation falls from 479 s to 312 s (35% variance reduction) with the p90 falling from 1370 s to 954 s; the Pre-Check lane mean wait drops from 899 s to 495 s (45% cut) because its load is halved. The regular lanes absorb the now-larger per-lane regular load (302 s -> 604 s mean), so the rebalance is a deliberate trade: it eliminates the Pre-Check outlier at the cost of a higher (but still stable) regular-lane wait, and it cuts overall variance because it removes the single grossly overloaded lane that was dominating the distribution. Modification 2 (shared line) cuts regular-lane wait variance strongly (std 205 s -> 137 s, 33% reduction) and p90 (592 s -> 443 s) by equalizing the regular queues, with a modest mean-wait reduction (302 s -> 280 s); it does not touch the Pre-Check overload. The surge lane helps little (overall mean 567 s -> 550 s) because the 300-s lead time means it opens only after the queue has already built, and it captures only part of the Pre-Check stream — confirming that a slow capacity response is inferior to a structural allocation fix. Together the two modifications (rebalance + shared line) address both goals: throughput (rebalance removes the overloaded lane) and variance (shared line equalizes queues; rebalance removes the dominant outlier). Limitation: the 2:2 rebalance presumes the airport can re-designate one regular lane as Pre-Check without hardware changes (only signage and officer assignment); if Pre-Check requires dedicated scanners, the cost is higher. Bias: shortest-queue join assumes passengers can see all queue lengths, which holds for a physically shared line but not for separate invisible queues.

## Subtask 3: Part (c): Consider how cultural norms / traveler styles affect how passengers process through the checkpoint, as a sensi

### Problem

Part (c): Consider how cultural norms / traveler styles affect how passengers process through the checkpoint, as a sensitivity analysis, and how the system can accommodate these differences to expedite throughput and reduce variance.

### Analysis

Cultural differences enter the model through two behavioral parameters: the self-service divest speed (how quickly a traveler unloads shoes, electronics, liquids) and the willingness to join the shortest queue / position themselves efficiently (modeled as the cut-in / queue-positioning propensity). These are the two levers the problem names (personal-space norms that discourage cutting, collective-efficiency norms, individual-efficiency norms). Four traveler-style profiles were defined, two tied to the cultures the problem cites and two generic, so the analysis does not over-claim about any single culture: (i) 'US personal-space' (baseline: standard divest speed, low cut-in), (ii) 'Swiss collective-efficiency' (slightly faster self-service, much lower cut-in because queue order is respected as a collective norm), (iii) 'Chinese individual-efficiency' (standard divest speed, higher queue-positioning propensity), and (iv) 'slow traveler' (slower divest, baseline positioning). Each profile is a multiplier on the part-(a) parameters, so the sensitivity is a controlled perturbation of the calibrated base case rather than a separate model.

### Modeling Process

Two profile parameters: div_scale multiplies the divest time D_i (slower divesting raises the lane pacing time and hence queue wait); cut_mult multiplies the cut-in / queue-positioning probability P_CUT. Profiles: us_baseline = (div_scale 1.00, cut_mult 1.0); swiss_collective = (0.90, 0.4); cn_individual = (1.00, 2.5); slow_traveler = (1.35, 1.0). For each profile, the DES is re-run for both the baseline configuration and the rebalanced (2:2) configuration, 5 seeds each, and mean wait, wait std, and p90 are reported. The mechanism: div_scale enters the lane pacing time max(ID_end, divest_end), so a 1.35x slower divest directly lengthens the cycle and the queue; cut_mult changes how often a passenger takes an earlier queue position, which lowers their own wait but adds variance and fairness cost for those behind them.

### Outcome Analysis

Baseline configuration: the slow-traveler profile raises overall mean wait from 567 s to 588 s and, more tellingly, raises regular-lane mean wait from 302 s to 411 s (a 36% increase) because slow divesters extend the lane pacing time that every passenger behind them inherits; the Swiss profile (0.90 divest, low cut-in) lowers overall mean wait to 544 s. The Chinese individual-efficiency profile (higher positioning) changes mean wait little (569 s) but is the one that would raise fairness/variance in a real queue. Rebalanced (2:2) configuration: the fix is robust across all four profiles — overall wait std stays in the 312-395 s band versus 436-488 s for the baseline, and the slow-traveler penalty is still present but bounded (overall 688 s vs 588 s). The key accommodation insight: because divest speed is the throughput-critical, style-sensitive parameter, the system should (a) provide Pre-Check and 'travel light' options that shorten the divest task for fast travelers, (b) staff or coach the divest area for slow/first-time travelers (a helper or clearer signage), and (c) use a shared line so that positioning differences are absorbed by routing rather than by cutting. Culturally, a shared line with visible queue lengths is compatible with collective-efficiency norms (order is respected and everyone sees the same line) and also caps the damage from individual-efficiency positioning, because the router, not the passenger, assigns the lane. Limitation: the two multipliers are a coarse two-parameter proxy for a richer cultural space; real norms affect language, compliance speed, and tolerance of secondary screening as well, which are not modeled. Bias: attributing a scalar 'divest speed' to a whole traveler group risks stereotyping; the analysis is framed as traveler *style* (fast/slow, order-respecting/position-seeking) that any culture can contain, with the named cultures used only as the problem's illustrative anchors.

## Subtask 4: Part (d): Propose policy and procedural recommendations for security managers based on the model, and validate the model

### Problem

Part (d): Propose policy and procedural recommendations for security managers based on the model, and validate the model, assess its strengths and weaknesses, and propose future work.

### Analysis

Recommendations follow directly from the modeled bottleneck and modification results, and are given both as globally applicable rules and as culture/traveler-type-specific adaptations. Validation was done by (i) checking the simulator reproduces the qualitative regime the expert described (saturated lanes, growing queues under demand, divest as the pacing station), (ii) sanity-checking that each parameter has a stated empirical source or dataset basis, and (iii) confirming the model's sensitivity direction is physically reasonable (slower divest -> longer waits; equalizing queues -> lower variance). Strengths and weaknesses are assessed against the data limitations and the modeling assumptions.

### Modeling Process

Recommendations (each traceable to a modeled result):
1. Rebalance lane allocation to demand (globally applicable): assign Pre-Check lanes in proportion to Pre-Check volume, not a fixed 1:3. Modeled effect: cuts the dominant Pre-Check outlier (mean wait 899 s -> 495 s) and overall wait std by 35%.
2. Use a single shared line with visible queue lengths for standard screening (globally applicable): routes to the shortest queue. Modeled effect: cuts regular-lane wait std by 33% and p90 from 592 s to 443 s; compatible with order-respecting (collective-efficiency) norms and caps positioning-driven variance.
3. Pre-position and staff the divest area (traveler-type specific): because divest is the style-sensitive pacing station, provide 'travel light / Pre-Check' fast paths for fast travelers and a helper or plain-language signage for first-time/slow travelers. Modeled effect: the slow-traveler penalty on regular waits (302 s -> 411 s) is the largest single style effect and is directly addressed here.
4. Make surge capacity a staffing reallocation, not a new-lane build (globally applicable): the model shows a 300-s lead time makes a new lane too slow to catch a sudden spike; pre-stage trained officers so a queue threshold triggers a reallocation in minutes.
5. Spread flagged-bag handling (globally applicable): because clustered 60-s secondary searches drive the wait tail, staff a dedicated secondary-search officer so a flag does not pull the only belt monitor off the line.

Validation summary: the DES reproduces the expert-described operating regime (saturated lanes, growing peak queues, divest pacing) and the direction of every sensitivity is physically reasonable; all empirical parameters carry a source. Strengths: represents the true serial/overlapping event ordering; isolates the structural Pre-Check overload; quantifies variance (std, p90), not just mean; parameterized so scenarios are one command apart. Weaknesses: single 10-min dataset window (point-estimate arrival rates); sparse ID/X-ray columns force expert-calibrated service distributions for two of the four stations; exponential ID service may be too regular; breaks and staffing shortages are treated as out-of-window rather than modeled; the cultural proxy is only two parameters. Future work: fit per-station service distributions from a full-day, multi-lane log; add officer-break and understaffing dynamics to model the 'unexplained long lines'; extend the cultural model to compliance speed and secondary-screening tolerance; optimize lane allocation over a full daily arrival curve rather than a single peak; and test the Pre-Check divest factor against a measured Pre-Check vs regular divest-time comparison.

### Outcome Analysis

The recommendations are ranked by modeled impact: (1) the 2:2 rebalance is the highest-leverage single change (removes the overloaded Pre-Check lane, 35% variance cut), (2) the shared line is the best variance reducer for standard screening (33% std cut) and is norm-compatible, and (3) divest-area support is the main traveler-type accommodation (addresses the largest style effect, the 36% slow-traveler wait increase). The model is validated to the extent its structure and sensitivity directions match the expert-described system and every input is sourced; its main uncertainty is the arrival-rate estimate from a short window and the expert-calibrated ID/X-ray services. The strongest bias to flag is that the Pre-Check overload is a *structural* artifact of the 1:3 lane ratio, so the headline recommendation is a policy change (re-allocate lanes) rather than a throughput change — if an airport cannot re-designate lanes, the shared line and divest support carry most of the benefit. Overall the model supports a clear, actionable policy: allocate lanes to demand, share the standard line, support the divest step, and pre-stage surge as reallocation.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
