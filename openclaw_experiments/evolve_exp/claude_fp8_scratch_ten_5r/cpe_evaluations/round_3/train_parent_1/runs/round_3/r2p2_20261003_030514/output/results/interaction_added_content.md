# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence

## Exchange 1
**Question:** At a busy morning airport checkpoint, how many open regular screening lanes do you typically see? Roughly how many Pre-Check lanes too?

**Reply (key facts):** Large-US-airport peak: 4–8 regular screening lanes open (hubs 8–12+); 1–3 Pre-Check lanes. Matches ~1 Pre-Check lane per 3 regular lanes; Pre-Check is ~45% of passengers but ~25% of lanes, so Pre-Check is relatively congested.

**How the reply became work:** Set the baseline checkpoint capacity used in the discrete-event simulation to L_reg = 6 regular lanes and L_pre = 2 Pre-Check lanes (central value of the expert's 4–8 / 1–3 ranges), with a sensitivity sweep over L_reg in {4,5,6,8} and L_pre in {1,2,3}. The lane split is the server count c in the M/G/c model for each queue and the core knob for the modification scenarios. Interval of validity: large US airport, peak morning, current TSA configuration.

## Exchange 2
**Question:** When many people fail the walk-through metal detector, what fraction of all passengers typically end up needing a pat-down?

**Reply (key facts):** 1–3% of all passengers; usually ~1–2%, rising to 3–5% at busy checkpoints or with less-experienced travelers.

**How the reply became work:** Set the secondary-process (Zone D pat-down) diversion probability to p_patdown = 0.02 baseline, swept over {0.01, 0.02, 0.05}. In the simulation, each passenger exiting the scanner/metal-detector step draws a Bernoulli(p_patdown) and, if triggered, receives an additional service at the secondary inspection station before rejoining the baggage-reclaim flow. Interval: typical US checkpoint operations.

## Exchange 3
**Question:** How long does a secondary pat-down inspection usually take, start to finish?

**Reply (key facts):** 2–5 minutes normally; 5–10 minutes if bag search, mobility issues, supervisor, or rescreening needed.

**How the reply became work:** Secondary inspection service time modeled as lognormal with mean 300 s (median) and tail to 600 s; specifically lognormal(median 180 s, sigma 0.35) giving ~90th percentile near 5–6 min, plus a 15% chance of a +300 s aggravator (bag search/supervisor) matching the expert's 5–10 min tail. This is the service-time distribution G of the secondary (M/G/1-type) sub-queue in Zone D. Interval: typical operations, peak.

## Exchange 4
**Question:** How many ID-check officers typically staff one checkpoint area at a busy airport?

**Reply (key facts):** 1–2 officers per ID station, 2–4 stations total at a large checkpoint, i.e. 2–6 officers (6–8 at peak hubs); staffing adjusted so ID-check keeps pace with screening lanes.

**How the reply became work:** ID-check stage (Zone A) modeled as an M/M/c server pool with c_id = 2 stations × 1 officer = 2 servers baseline (range 2–6), service time from the data (id1/id2 inter-call times ≈ 5.3–20.5 s per passenger). The expert's "keep pace" rule becomes a design constraint: ID-check throughput c_id / E[service] must be ≥ arrival rate to Zone A, used to check Zone A is not the binding bottleneck in each scenario. Interval: busy peak, large US airport.

## Exchange 5
**Question:** Do travelers usually grab their bags off the belt right away, or do they linger there?

**Reply (key facts):** Mostly immediate: 10–30 s dwell. Lingering is exceptional (flagged bag, many bins/slow mobility, repacking at belt) and holds a spot 1–3 min — a real local bottleneck since the belt and collection area are shared.

**How the reply became work:** Bag-reclaim stage (Zone C) modeled as a shared finite-capacity resource: reclaim dwell = 20 s typical (data "Time to get scanned property" median 27 s is consistent), plus a 10% probability of a 90–180 s linger. The belt/reclaim area has finite space (k=10 positions), so a slow reclaiming passenger blocks the lane behind — this coupling is one of the variance sources the modifications must fix (Modification 2: dedicated reclaim side-aisle / staggered bin placement removes the blocking). Interval: peak, shared collection area.

## Exchange 5
**Question:** Do travelers usually grab their bags off the belt right away, or do they linger there?

**Reply (key facts):** Mostly immediate: 10–30 s dwell. Lingering is exceptional (flagged bag, many bins/slow mobility, repacking at belt) and holds a spot 1–3 min — a real local bottleneck since the belt and collection area are shared.

**How the reply became work:** Bag-reclaim stage (Zone C) modeled as a shared finite-capacity resource: reclaim dwell = 20 s typical (data "Time to get scanned property" median 27 s is consistent), plus a 10% probability of a 90–180 s linger. The belt/reclaim area has finite space (k=10 positions), so a slow reclaiming passenger blocks the lane behind — this coupling is one of the variance sources the modifications must fix (Modification 2: dedicated reclaim side-aisle / staggered bin placement removes the blocking). Interval: peak, shared collection area.

## Exchange 6
**Question:** At a crowded checkpoint, do some passengers step aside to let others pass, or do lines jam up?

**Reply (key facts):** Queues stay orderly (US personal-space / no-cutting norm) — no passing, queue just grows long. At the belt/bin area, side-stepping is common (slow passengers move aside), which helps locally but creates the shared-area bottleneck. Jams concentrate at merge points and shared equipment (belt, scanner exit, lane merges), not in the queue itself.

**How the reply became work:** (1) Queues modeled FCFS with no overtaking (no-cutting), i.e. standard M/G/c — the no-cutting norm validates FCFS. (2) This reply directly motivates Modification 2's mechanism: give slow reclaimers a side pocket so stepping aside no longer blocks the lane (decouples the finite reclaim resource). (3) It anchors the cultural sensitivity analysis (part c): the US norm = orderly FCFS + belt side-stepping; the variance reduction comes from fixing the shared-resource jam, not from queue dynamics. Interval: US checkpoint behavior, peak.

## Exchange 7
**Question:** Compared to American travelers, do European travelers tend to move through security checkpoints faster or slower?

**Reply (key facts):** Roughly the same on average — no reliable nationality effect. Differences are driven by procedure/equipment (scanner mix, shoe rules, CT scanners that keep liquids/laptops in bags). Per-passenger speed is dominated by familiarity, carry-on amount, and mobility. Treat Europe vs US as equal service time unless modeling a specific airport's equipment.

**How the reply became work:** This reframes the part-(c) cultural sensitivity analysis honestly: instead of a false nationality speed gap, the sensitivity analysis is parameterized by traveler-style factors the expert says actually matter — familiarity with the process, carry-on/bin count, and mobility — implemented as three traveler archetypes ("familiar/low-bins", "typical", "unfamiliar/many-bins or slower") that shift the screening-assembly service time by −15%/0/+30% and the reclaim dwell by −10%/0/+50%. A "CT-scanner equipment" scenario (liquids/laptops stay in bags) is also run as an equipment variant. Interval: general.

## Exchange 8
**Question:** How often do security lanes shut down mid-morning due to equipment failure or re-staffing?

**Reply (key facts):** Rare but not negligible — ~2–3 outages per week at a large checkpoint, each 5–20 min (X-ray/scanner faults, belt jams, calibration). Re-staffing closures are uncommon and short. Net: low-frequency, short-duration random event, ~1–3% chance per lane per hour of a 5–20 min outage.

**How the reply became work:** Added a disruption process to the simulation: each open lane has a 2%/hour hazard of a 5–20 min (exponential, mean 10 min) closure during the peak window. This is the stochastic shock that produces the "unexplained long lines at normally quiet airports" the problem mentions — it explains the high variance (tail waits) and motivates Modification 3: cross-trained flex officers + a reserve/standby lane so one closure does not cut capacity by 17%. Interval: peak hours, large US airport.

## Exchange 9
**Question:** What do travelers most often forget or fumble at the checkpoint that slows them down?

**Reply (key facts):** Most common fumbles: liquids/3-1-1 (oversized → flagged), laptops left in bag (regular only), metal on body (shoes, belts, phones, coins), jackets, and forgetting pocket items → pat-down. The slowdown comes from discovering the item at the wrong moment (scanner/alarm), forcing a re-do, pat-down, or bag search. Pre-Check exists to remove shoe/belt/laptop steps, which is why those travelers are faster.

**How the reply became work:** (1) Assembly/screening-prep service time for regular passengers is given a fumble tail: base 60 s plus, with probability 0.25, a discovery delay of 30–90 s (item found at scanner → re-do), and this fumble raises the effective pat-down probability (feeds the Zone D queue from exchanges 2/3). (2) The reply quantifies the Pre-Check advantage mechanistically: Pre-Check prep = 40 s (no shoes/belt/laptop), regular = 60 s + fumble tail. This differential is used in the Pre-Check lane-allocation modification (Modification 1) to compute the fair lane split. Interval: US checkpoint, regular vs Pre-Check.

## Exchange 10
**Question:** At peak, do airports usually add more lanes, or just add more officers to existing lanes?

**Reply (key facts):** Both, but adding officers to existing lanes is the common/faster lever (extra divestiture help, second X-ray reader, more secondary staff); opening a new lane needs a full staffing set + equipment and only for sustained peaks. Short peaks → more officers on existing lanes; sustained peaks → additional lanes.

**How the reply became work:** Shapes the policy recommendations and the third modification tier: (a) first response = add officers to existing lanes (modelled as raising per-lane X-ray read rate and secondary-station staffing, i.e. faster service at fixed c); (b) sustained-peak response = open the standby reserve lane (exchange 8). The two levers are distinct model parameters: service-rate multiplier vs. server count c, and the simulation is run with each to show the cheaper one suffices for short peaks. Interval: US airport peak management practice.
