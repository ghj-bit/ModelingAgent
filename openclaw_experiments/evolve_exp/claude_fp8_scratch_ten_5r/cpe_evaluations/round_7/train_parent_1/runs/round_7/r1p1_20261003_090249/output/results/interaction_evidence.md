# Expert Interaction Evidence

## Exchange 1
**Question:** Do self-driving cars on a busy freeway cluster together or stay spread out among human cars?
**Reply:** Tighter groups. Cooperative ACC lets communicating vehicles follow at time headways ~0.3–0.7 s vs ~1.2–2.0 s for humans. Effect is real but bounded; requires a high enough share to form stable platoons; string stability degrades with heterogeneous mix.
**How used:** Sets the headway ratio parameter h = 0.5 s (AV) vs h_human = 1.5 s. Platoon formation threshold encoded as minimum AV fraction for capacity gain.

## Exchange 2
**Question:** Do human drivers cut in front of a tight AV group or let it pass?
**Reply:** Mixed; some cut in, most don't. Cutting-in rate rises sharply with gap size. If gap ≥ ~1 car length, a meaningful minority cuts in; if tight, most follow.
**How used:** Human cut-in modeled as a capacity-reduction factor on mixed lanes: c_mixed = c_human + p*(c_av - c_human) * (1 - cut_in_rate(p)), where cut_in_rate is low at low p and rises with p.

## Exchange 3
**Question:** What fraction of self-driving cars is needed for noticeable flow improvement?
**Reply:** ~20–30% threshold. Below that, benefit is marginal. Above 30%, improvement is visible; strengthens substantially by 50%; saturates toward high end.
**How used:** Sets the tipping-point parameter p_crit = 0.25. Capacity gain function C(p) is flat for p < 0.20, rises for 0.20 ≤ p ≤ 0.50, saturates for p > 0.70.

## Exchange 4
**Question:** Do AVs in a dedicated lane drive at constant speed or adjust with traffic?
**Reply:** Steady, not constant. Hold stable target speed; smooth out surrounding oscillation. Still adjust to vehicle ahead and lane density; slow as lane approaches capacity.
**How used:** Dedicated lane modeled as a free-flow lane with capacity c_ded = c_av and speed v_ded = v_ff when demand < capacity, and v_ded = v_jam * (c_ded - demand)/c_ded when at/over capacity.

## Exchange 5
**Question:** Does capacity keep rising with more AVs or hit a ceiling?
**Reply:** Rises with diminishing returns and a ceiling. Largest gain in 20–50% range; flattens toward high penetration. Ceiling set by minimum headway and string-stability limits. Bounded factor ~1.5–2× over human flow.
**How used:** Capacity multiplier capped at 2.0. C(p) = c_human * (1 + 1.0 * sigmoid((p - 0.30) / 0.10)), bounded above by 2.0 * c_human.

## Exchange 6
**Question:** Does a congestion backup end in one place or taper gradually?
**Reply:** Sharp front with short taper. Well-defined downstream boundary (shockwave front). Front moves upstream as demand continues. Recovery zone is a few hundred meters, not miles.
**How used:** Congestion modeled as a single shockwave front position x_front(t) moving upstream at speed dx/dt = (q_in - q_out) / (k - k_0), not a distributed fade.

## Exchange 7
**Question:** In slow-moving traffic, do cars bunch up or stay evenly spaced?
**Reply:** Bunch up into dense packs separated by gaps. Same stop-and-go instability. Dynamic, not static. Spacing within a pack is tight but bounded by minimum safe headway.
**How used:** Jam density k_jam set at ~180 veh/km (dense but not bumper-to-bumper), consistent with ~0.5 s headway at low speed.

## Exchange 8
**Question:** Do drivers in stopped lanes force into a dedicated AV lane?
**Reply:** Some try, but minority. With soft separation (painted line), meaningful minority crosses; with physical barrier, rare.
**How used:** Dedicated lane effectiveness reduced by erosion factor e = 0.15 for soft separation (painted line, typical freeway), e = 0.02 for hard separation. Model uses e = 0.15 as baseline.

## Exchange 9
**Question:** When freeway is gridlocked 30+ minutes, do drivers reroute or wait?
**Reply:** Mostly wait. Minority reroutes, share grows with jam duration. Bounded; by 30 min, most who could leave already have.
**How used:** Demand reduction from rerouting modeled as d_reroute = 0.10 * min(1, t_jam / 30 min), applied to demand after 15 min of jam. Baseline d_reroute = 0.05 for the Seattle corridors (limited substitutes).

## Exchange 10
**Question:** Do merging cars at on-ramps cause noticeable slowdown?
**Reply:** Yes, merging is a main local congestion source. At/near capacity, yield/slow creates perturbation that amplifies into stop-and-go wave. Worst where merge is short.
**How used:** Merge bottleneck modeled as a local capacity reduction at each interchange. Effective capacity reduced by factor 0.85 at ramp locations in the base case, recovering to 1.0 between ramps.
