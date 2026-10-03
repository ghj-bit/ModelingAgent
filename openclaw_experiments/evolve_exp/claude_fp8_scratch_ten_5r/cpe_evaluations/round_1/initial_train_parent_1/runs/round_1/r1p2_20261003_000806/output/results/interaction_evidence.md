# Expert Interaction Evidence

## Exchange 1
**Question:** At a busy airport checkpoint, which step usually makes the longest line form?
**Reply:** The ID/document check (Zone A) is usually the longest queue. It is the first mandatory stop, staffed by the fewest officers, and every passenger must pass through it. The second-longest queue is the Zone B wait for an open screening lane. The X-ray/scanner steps rarely form the dominant line because they are pipelined and parallel.
**Effect on work:** Used to prioritize bottleneck identification. The model computes queue wait at every stage; the simulation confirms Zone B (lane capacity) is the binding constraint at the CSV arrival rate, while Zone A has low utilization. This is consistent with the expert's "second-longest" characterization for Zone B. The finding that Zone A is the "primary bottleneck" at very high load is captured in the arrival-rate sweep (task d).

## Exchange 2
**Question:** How many passengers per minute typically walk through the ID check station?
**Reply:** Roughly 4-8 passengers per minute per ID-check officer (7-15 seconds service per passenger). Sustained rates above ~8/min per officer are uncommon.
**Effect on work:** Set id_svc_mean = 11.0 s (midpoint of 7-15 s range), id_svc_std = 4.0 s. This is also consistent with the CSV: Officer 1 mean 10.2 s (n=9), Officer 2 mean 12.6 s (n=7). The 4-8 pax/min rate implies 7.5-15 s service, matching the model.

## Exchange 3
**Question:** Do passengers who arrive together usually stay together through the whole checkpoint?
**Reply:** No. Groups split at the scanner (each person goes individually) and at Pre-Check/regular lane divergence. They re-converge at the belt, but with variable delay. Groups behave as correlated arrivals that fragment and rejoin, not as independent individuals or an indivisible batch.
**Effect on work:** Set group_mean_size = 1.3 (Poisson). Group members arrive within Exp(2 s) of each other but are modeled independently after Zone A. This is a reasonable approximation given the expert's statement that groups split at the scanner. The correlation in arrival times is captured; the correlation in service times is neglected (acceptable for throughput analysis).

## Exchange 4
**Question:** How often do bags get flagged for extra screening at the X-ray machine?
**Reply:** Roughly 5-15% of bags are flagged, typically low single digits to about 10% under normal conditions; up to 15%+ during heightened alert. Most flags are resolved quickly; a minority require full Zone D inspection.
**Effect on work:** Set flag_rate = 0.10 (midpoint of the "normal conditions" range). The flag-rate sweep (5%-20%) brackets the expert's full range. Secondary screening time set to 180 s mean (3 min) for the "full Zone D inspection" case.

## Exchange 5
**Question:** How does the wait for Pre-Check lanes usually compare to regular lanes?
**Reply:** Pre-Check waits are much shorter (a few minutes vs 10-30+ min for regular). The reason is not intrinsic speed but underload: 45% of passengers are eligible, yet only ~1 Pre-Check lane per 3 regular lanes. Pre-Check screening is only modestly faster (no shoe/belt/jacket removal, no laptop out of bag).
**Effect on work:** Set precheck_speedup = 0.80 (20% faster bin prep). The lane configuration (3 regular + 1 Pre-Check) matches the 1:3 ratio. This exchange directly motivates mod2 (add a second Pre-Check lane) as the primary modification. The 71% wait reduction from mod2 is consistent with the expert's observation that Pre-Check is underloaded.

## Exchange 6
**Question:** Do passengers often join a different screening lane when the line is too long?
**Reply:** Yes, but only within limits. Lane shopping is normal at the decision point. Pre-Check vs regular is not swappable. Physical layout limits switching to the lane-assignment point. Social norms (stigma against cutting) limit mid-queue switching. Net: moderate, mostly at lane selection, largely blocked across the Pre-Check/regular boundary.
**Effect on work:** Set lane_switch_prob = 0.30 (moderate). Pre-Check and regular lane assignment is enforced (no cross-boundary switching). Lane selection is "join shortest same-type lane," consistent with the expert's description of shopping at the decision point. The cultural sensitivity analysis varies this parameter (0.10 for slow/privacy-conscious, 0.50 for efficiency-focused).

## Exchange 7
**Question:** Which takes longer: standing in line, or sorting belongings into the bins?
**Reply:** Standing in line takes much longer (10-30+ min at busy checkpoints). Bin sorting is on the order of 30 seconds to 2 minutes per passenger, depending on removal requirements and familiarity. Pre-Check passengers are at the low end.
**Effect on work:** Set bin_prep_mean = 60.0 s (midpoint of 30-120 s), bin_prep_std = 30.0 s. Pre-Check speedup of 0.80 reflects the "low end" for Pre-Check. This exchange confirms that bin prep is a local per-passenger delay, not the main time sink, consistent with the model's finding that Zone B queue wait dominates.

## Exchange 8
**Question:** How do passengers usually react when told their bag needs extra checking?
**Reply:** Most comply, but the reaction adds time and variance. Typical: surprise/confusion then compliance, cooperation with mild annoyance, occasional resistance or anxiety. Group disruption: companions wait nearby or continue to Zone C. Net: the flag adds seconds to a couple of minutes of variability per flagged bag.
**Effect on work:** Added a reaction time component to Zone D service: reaction ~ Normal(30, 15) s, added to the 180 s secondary screening time. This captures the "seconds to a couple of minutes" variability. The flag-rate sweep (task b) shows the impact of this additional variability on total wait.

## Exchange 9
**Question:** When do checkpoint lines get longest: early morning or late afternoon?
**Reply:** Late afternoon/early evening is usually worse (broader, longer-lasting congestion). Early morning gives a steeper but shorter spike. The peak depends on the airport's flight schedule.
**Effect on work:** Set peak_mult = 1.5 (50% above baseline at the peak). The arrival process uses a Gaussian bump centered at the middle of the 4-hour window to represent the afternoon peak. The arrival-rate sweep (task d) brackets off-peak (60 pax/hr) to peak (168 pax/hr) conditions.

## Exchange 10
**Question:** What is the one change that would most cut checkpoint wait times?
**Reply:** Add more ID-check capacity (Zone A) - either more officers or automation (document/ID verification kiosks or biometric e-gates). Zone A is the single mandatory serial step, staffed by the fewest officers, and is the primary bottleneck. Adding lanes or X-ray machines only relieves downstream steps that are already pipelined.
**Effect on work:** Set up mod1 (4 ID officers + kiosks reducing service to 8 s) as a modeled modification. The simulation shows mod1 is ineffective at normal load (Zone A not binding) but provides surge insurance. This is reported honestly in the results. The expert's identification of Zone A as "the primary bottleneck" is consistent with the arrival-rate sweep showing that at 168 pax/hr, Zone A wait rises to 0.6 min (still low, but the system is degrading). The policy recommendation includes ID kiosks as medium-priority surge insurance, with the Pre-Check lane addition as the high-priority intervention.
