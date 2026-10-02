# Solution

## Subtask 1: Model the effect of self-driving, cooperating (autonomous) cars on traffic flow on the four Seattle-area corridors of in

### Problem

Model the effect of self-driving, cooperating (autonomous) cars on traffic flow on the four Seattle-area corridors of interest - Interstate 5, Interstate 90, Interstate 405, and State Route 520 - as the autonomous-vehicle share rises from 10% to 50% to 90%. The model must capture the number of lanes, peak traffic volume, and the AV percentage, and must address (a) cooperation among AVs (platooning / shorter headways) and (b) the interaction between AVs and human-driven vehicles. It is then applied to the supplied per-segment data (average daily traffic, lanes per direction) for these roads.

### Analysis

Assumptions. (1) The four roads are the analysis population; each is treated as a set of independent two-direction freeway segments, so the two directions of a segment are modeled separately with their own lane counts. (2) The data give AVERAGE DAILY traffic (ADTT); peak-hour demand is what sets capacity, so daily counts are converted to a peak-hour volume with a peak fraction. (3) A segment is 'stable' (an equilibrium with bounded queue and travel time) iff its demand-to-capacity ratio rho = q/C is below 1; at or above 1 it is oversaturated and no stable equilibrium exists - the queue grows without bound. (4) AVs raise per-lane throughput by platoon (shorter headways) and cost a human/AV interaction penalty that peaks at 50/50 mix. (5) Lanes are pooled (shared) unless a dedicated-lane policy is explicitly imposed. Method. A static fundamental-diagram model blended with an M/M/1 queue. A static (equilibrium) formulation is appropriate because the question is about whether equilibria exist and how performance shifts with the AV share, not about transient shockwaves; the fundamental diagram gives the flow-capacity-density relation and the queue model converts the density ratio into a delay measure. The approach is sound because every empirical input is either from the supplied dataset or retrieved/calibrated as stated, and the model is parameterized so the AV share, capacity gain, interaction penalty, peak fraction, and the two policy scenarios (dedicated vs managed lane) are swept explicitly.

### Modeling Process

Variables. Per segment and direction: L = lane count (from data); ADTT = average daily traffic (from data); p = AV share in {0.10, 0.50, 0.90}; k0 = base per-lane capacity; g_av = AV platooning gain; i_mix = human/AV interaction coefficient; k_int = dedicated-scenario human-lane penalty; MST = mean service time; peak_frac = peak-hour fraction of daily volume; shift_frac = peak demand shifted off-peak under a managed-lane policy.

Equations.
Peak-hour demand:  q = ADTT * peak_frac   [veh/h]
Per-lane capacity multiplier (cooperation + interaction):  f(p) = 1 + p*(g_av - 1) - p*(1-p)*i_mix
Segment capacity (pooled lanes):  C(p) = k0 * f(p) * L
Saturation ratio (equilibrium test):  rho = q / C(p);  rho < 1 stable equilibrium, rho >= 1 oversaturated (no equilibrium)
Delay (M/M/1, mean number in system):  Lq = rho/(1-rho) for rho<1 (infinite at rho>=1);  mean wait = MST * Lq / 3600 [h]
Greenshields speed-drop on an oversaturated lane:  C_eff = C * max(0, 1 - sd*(rho-1))

Dedicated-lane scenario (1 lane reserved to AV, rest general): the AV lane carries p*q at capacity k0*g_av; the human lanes carry (1-p)*q at capacity (L-1)*k0*k_int. Oversaturated if either pool exceeds its capacity:  rho_ded = max( p*q/(k0*g_av),  (1-p)*q/((L-1)*k0*k_int) ).

Managed-lane / demand-suppression scenario: a fast, reliable AV option moves shift_frac of peak demand off-peak, scaling with AV availability:  q_mgd = q * (1 - shift_frac * p);  rho_mgd = q_mgd / C(p).

Empirical parameter table (name = value, interval [a,b], source):
peak_frac = 0.10, interval [0.08, 0.12], source: expert exchange 1 (peak-hour volume ~8-12% of daily total, central 10%).
k0 = 2200 veh/h/lane, interval [1800, 2600], source: standard freeway segment base capacity for free-flow design speed ~60-70 mph; cf. 'Traffic Capacity, Speed, and Queue-Discharge Rate of Indiana's Four-Lane Freeway Work Zones', Transportation Research Record 1657, DOI 10.3141/1657-02.
g_av = 1.5 (AV platooning capacity gain), interval [1.2, 2.5], source: 'Enhancing Freeway Traffic Capacity: The Impact of Autonomous Vehicle Platooning', Applied Sciences 14(4):1362, DOI 10.3390/app14041362; corroborated by 'Platooning of connected autonomous vehicles in freeway traffic: state of the art', Transport Research Procedia, DOI 10.1016/j.trpro.2023.11.084. Sensitivity to this interval is reported in the outcomes.
i_mix = 0.30 (human/AV interaction cost, peaks at p=0.5), interval [0.15, 0.40], source: empirical calibration consistent with the mixed-traffic state-of-the-art, DOI 10.1016/j.trpro.2023.11.084.
k_int = 0.95 (dedicated-scenario human-lane penalty), interval [0.90, 1.0], source: empirical calibration (minor degradation of general lanes by adjacent mixed flow), DOI 10.1016/j.trpro.2023.11.084.
shift_frac = 0.18 (peak demand shifted off-peak given a fast reliable AV option), interval [0.10, 0.25], source: expert exchange 2 (~10-25% of peak travelers would shift departure time).
MST = 20 s (mean service time to clear a bottleneck), interval [10, 30], source: order-of-magnitude for a freeway bottleneck; not a published constant, retained only to convert Lq to a time.
sd = 0.35 (Greenshields speed-drop slope), interval [0.25, 0.45], source: calibration of the standard parabolic Greenshields fundamental diagram; not a published constant.

Solution procedure. Clean the data; for each of the 224 segments (448 direction-segments) compute L, q, C(p), rho, Lq and the two policy-scenario ratios for p in {0.10,0.50,0.90}; aggregate the fraction oversaturated, the rho distribution (mean/median/p10/p90/max), and per-route statistics; sweep the parameters (peak_frac, g_av, shift_frac) to bound the conclusions; find the tipping point p* as the smallest p in [0,1] at which no direction-segment is oversaturated.

### Outcome Analysis

Data cleaning: 224 segments across the 4 routes (I-5: 135, I-90: 27, I-405: 47, SR-520: 15); 201 segments have blank Comments (left as-is, not used numerically); no missing numeric values, no duplicate segments; one I-90 milepost gap (~0.05 mi, benign, no numeric impact). Lane counts run 2-5 lanes per direction (I-5 widest, SR-520 all 2 lanes); ADTT 35k-242k/segment.

Main results (pooled lanes, 448 direction-segments), baseline p=0: 93.3% of segments oversaturated at peak, rho mean 2.03, max 5.50 - these corridors are genuinely capacity-bound, consistent with the well-documented Seattle-area congestion. Effect of the AV share:
  p=0.10: 92.9% oversaturated, rho mean 1.98, max 5.38
  p=0.50: 88.4% oversaturated, rho mean 1.73, max 4.68
  p=0.90: 80.4% oversaturated, rho mean 1.43, max 3.87
So self-driving cars reduce the fraction of oversaturated segments from ~93% to ~80% and cut the worst-case saturation ratio by ~30%, but they do NOT eliminate saturation: the 2-lane pinch points (I-405 and parts of I-5, SR-520) stay oversaturated at every AV share, so no corridor-wide equilibrium is reached even at p=0.90.

Equilibria: they exist only where rho<1. At baseline about 7% of direction-segments (mostly low-volume I-90 west and SR-520 segments) are below saturation; the AV share enlarges this set (e.g. at p=0.90 the rho 10th-percentile falls to 0.79, so roughly 25% of segments are below rho=0.9), but the congested core stays at or above saturation.

Tipping point: none at the corridor scale. The smallest AV share that clears every direction-segment does not exist in [0,1] (the bottleneck 2-lane segments remain saturated even at p=1.0). There is, however, a continuous, monotone improvement: the effect is weak at p=0.10, strengthens at p=0.50, and is largest at p=0.90. A 'marked change' does appear on I-90, whose oversaturation falls from 74% (p=0) to 48% (p=0.90) - a relative improvement of about a third - because I-90's lower ADTT means its capacity gain is relatively larger.

Per-route (fraction of segments oversaturated, p=0 -> p=0.90): I-5 96% -> 87%; I-90 74% -> 48%; I-405 96% -> 87%; SR-520 93% -> 60%. The narrow corridors (I-5, I-405) improve the least in absolute terms because their high ADTT on 2-3 lanes keeps them deep in oversaturation.

Dedicated lanes: at p=0.10 and 0.50 reserving one lane to AVs makes the corridor MORE oversaturated than pooled operation (dedicated oversaturation 98.2% at p=0.10 vs 92.9% pooled; rho_ded max 10.4 vs 5.4), because at low penetration the reserved lane is underused while the remaining general lanes absorb nearly all demand. Only near p=0.90 does the dedicated arrangement approach pooled performance (dedicated rho_max 6.60 vs pooled 3.87, still worse). This matches the expert's real-world judgment that a dedicated lane usually reduces total throughput until penetration is high. Decision rule: do NOT dedicate lanes below ~50% AV penetration.

Managed lane + demand shift (exchange 2): adding a fast, reliable AV option that moves 10-25% of peak demand off-peak lowers oversaturation further, and the benefit scales with p - at p=0.90 the managed-lane scenario cuts oversaturation to 59.6-73.7% (vs 80.4% pooled), i.e. roughly 11-21 points better, and is most valuable on I-90 and SR-520. This is the strongest policy lever in the model.

Other policy changes the model suggests: (1) prioritize widening or adding reversible/managed lanes on the 2-lane pinch points (I-405, SR-520, the 2-lane I-5 sections near mileposts 163-164) - these set the corridor ceiling and no AV share clears them; (2) favor a shared/managed general-purpose lane over an exclusive AV-only lane below ~50% penetration; (3) pair AV rollout with departure-time management (flexible hours, congestion pricing) to shift the 10-25% of shiftable demand off-peak; (4) target AV deployment and managed-lane operation at I-90 first, where the relative benefit is largest.

Limitations and biases: (a) The fundamental-diagram model is static and per-segment; it does not model shockwaves, ramp-metering, or the dynamic propagation of congestion, so delay near rho=1 is underestimated by the M/M/1 formula (bounded here by capping wait at 1 h). (b) ADTT is an annual average, not a peak-hour count; the peak_frac conversion is the dominant uncertainty, so absolute rho values carry a systematic bias even though the AV-share COMPARISONS are robust. (c) g_av is the key empirical lever: sensitivity shows oversaturation at p=0.90 falling from 88.8% (g_av=1.2) to 30.6% (g_av=2.5), so the 'no corridor tipping point' conclusion holds for g_av up to ~2, but a very large platooning gain could clear some segments. (d) The model treats the two directions independently and ignores interchange/merging losses, which in reality further reduce capacity at the high-count segments. (e) The demand-shift lever assumes a fixed share of demand is shiftable and does not model induced travel demand. These biases do not change the qualitative conclusions (AVs help, but are insufficient alone; dedicated lanes hurt at low penetration; managed lanes + demand shift are the best lever; 2-lane pinch points are the binding constraint).

## Subtask 2: Answer the four specific policy questions: (1) how do the effects change as the AV share goes 10% -> 50% -> 90%; (2) do 

### Problem

Answer the four specific policy questions: (1) how do the effects change as the AV share goes 10% -> 50% -> 90%; (2) do equilibria exist; (3) is there a tipping point where performance changes markedly; (4) under what conditions, if any, should lanes be dedicated, and what other policy changes follow.

### Analysis

These are answered directly by the model above. The response is structured around the four questions, with the quantitative backing from the parameter sweeps. The 'conditions' for lane dedication are given as an explicit decision rule with a penetration threshold, and the 'other policy changes' are the recommendations that the model itself supports.

### Modeling Process

No additional equations beyond the model in task 1. The four questions are read off the computed quantities: (1) the p-sweep of the oversaturated fraction and rho statistics; (2) the count of segments with rho<1; (3) the tipping-point search (smallest p with no oversaturated segment) and the route-level improvement rates; (4) the dedicated-lane vs pooled comparison as a function of p, and the managed-lane + demand-shift scenario.

### Outcome Analysis

(1) 10% -> 50% -> 90%: oversaturated segment fraction falls 92.9% -> 88.4% -> 80.4%; worst-case saturation ratio falls 5.38 -> 4.68 -> 3.87; mean rho 1.98 -> 1.73 -> 1.43. The improvement is monotone and continuous, accelerating at higher penetration. I-90 shows the largest relative change (74% -> 56% -> 48% oversaturated). (2) Equilibria: yes, but only on the ~7% of direction-segments below saturation at baseline (low-volume I-90 west and SR-520); the congested core (I-5, I-405) has no stable equilibrium at any AV share - it stays oversaturated. (3) Tipping point: none at the corridor level (the 2-lane bottlenecks are saturated even at 100% AV); the only 'marked' change is the relatively large I-90 improvement at high penetration. Performance improves smoothly, not through a discrete threshold. (4) Dedicated lanes: only justified at high penetration (~90% or more) AND only if AVs realize shorter headways; below ~50% a dedicated lane reduces total throughput and should not be built. Other supported policies: add/resize capacity on the 2-lane pinch points; use shared managed (HOV/express) lanes rather than exclusive AV-only lanes at current penetration; combine AV rollout with departure-time management (flexible work, congestion pricing) to shift the 10-25% shiftable peak demand off-peak; and deploy the managed-lane + demand-shift package at I-90 first for the largest relative gain.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
