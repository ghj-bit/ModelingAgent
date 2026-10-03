# Interaction Evidence — 2017_C (AV highway capacity)

Ten expert exchanges. Each entry: question (as asked), reply (summary), and
how the reply was turned into model work (parameter, equation, or decision
rule), with the place it enters the model.

## Exchange 1
**Q:** On a busy highway, when connected self-driving cars cooperate, do they
tend to drive bunched in tight groups close behind each other, or do they stay
spread out like normal traffic?

**Reply (summary):** Bunched. Cooperative ACC / platooning deliberately
shortens gaps; clustering is the intended capacity mechanism.

**Model use:** Establishes the structural choice: AVs are modeled as tight
platoons, not as independent vehicles. Enters the model as the platoon
capacity rule `q_max_av = v_f / g_av` with a platoon headway `g_av` shorter
than the human headway `g_h` (parameter `g_av = 1.0 s`, interval [0.7, 1.5],
~40% tighter than the human ~1.6 s baseline). This is the core capacity
mechanism in `solve_segment()` of `code/model.py`.

## Exchange 2
**Q:** When a group of connected self-driving cars is bunched together, how do
regular non-connected human drivers behave around that group?

**Reply (summary):** Humans do not join platoons; they trail at conventional
spacing or overtake in adjacent lanes. The platoon acts as a moving block;
its tight internal gaps stay unfilled by humans.

**Model use:** Decision rule: AVs and humans are two separate sub-flows with
separate capacity pools (AV platoon headway vs. Greenshields human diagram);
no human flow is allowed into platoon headways. Implemented as the split
`q_h_demand = (1-p)·Q`, `q_av_demand = p·Q` with independent capacities in
`solve_segment()`.

## Exchange 3
**Q:** Do regular human drivers feel it is safe to cut into the short gaps
between the bunched self-driving cars in a group?

**Reply (summary):** No — gaps too short, closing speeds too high; humans
generally do not cut in.

**Model use:** Confirms and hardens the exchange-2 decision rule: the
human/AV capacity split is strict (no leakage of human demand into the
platoon pool). No separate parameter; this is a binary structural rule in the
flow split of `solve_segment()`.

## Exchange 4
**Q:** When a bunched group of self-driving cars slows down, how do human
drivers behind them usually react compared with following a normal car?

**Reply (summary):** More abruptly, with less anticipation; braking
propagates as a sharp, amplified shockwave backward through human traffic.

**Model use:** Enters as the shockwave capacity factor on the human sub-flow:
`S(p,c) = 1 − shock_k·p·(0.3 + 0.7·c)`, where `c` is the congestion ratio.
`shock_k = 0.5` (interval [0.3, 1.0], expert empirical judgement). The factor
is solved self-consistently with `c` by fixed-point iteration. This is the
only negative effect of AVs in the model.

## Exchange 5
**Q:** If a lane were reserved only for connected self-driving cars, would
regular drivers mostly accept that, or fight it?

**Reply (summary):** Mostly fight it, at least initially — classic "empty
lane" backlash; acceptance rises only when the lane is visibly well-used and
general traffic is not clearly worse off.

**Model use:** Policy decision rule for the dedicated-lane scenarios (b) and
(c): a dedicated AV lane is recommended only when the AV share is high enough
that the reserved lane is well-used and the remaining human lanes are not
worse off. Quantified by comparing the dedicated-lane vs. mixed scenarios at
p = 0.5 and p = 0.9 in the dedicated-lane comparison table; the model shows
the dedicated lane only becomes favorable at high p (low human demand),
matching the acceptance threshold the expert described.

## Exchange 6
**Q:** Do self-driving cars generally drive at speeds closer to the posted
speed limit, or noticeably below it?

**Reply (summary):** Closer to the limit, often slightly above; less speed
variance than human traffic.

**Model use:** Parameter `v_f = 60 mph` (interval [55, 65]) for both sub-flows
— AVs track the limit, humans drive near it, so no separate AV speed
parameter is needed; the speed difference between groups is folded into the
shockwave factor instead of a speed gap. Platoon speed set to `v_f` in
`solve_segment()`.

## Exchange 7
**Q:** During rush hour on a crowded highway, is congestion usually worse in
one direction than the other?

**Reply (summary):** Yes — strongly directional; the inbound direction is
worse in the morning, outbound in the evening; the two directions are not
symmetric.

**Model use:** Directional split of peak-hour demand: loaded direction gets
`d_load = 0.55` of the peak-hour flow, unloaded `0.45` (interval [0.45, 0.60]).
Implemented as `d_split` in `analyse()`: the "incr" direction is treated as
the loaded one.

## Exchange 8
**Q:** Is highway congestion on these roads mainly concentrated during rush
hour, or spread fairly evenly through the day?

**Reply (summary):** Mainly concentrated during rush hour; bimodal with two
pronounced peaks; off-peak and overnight near free-flow.

**Model use:** Parameter `f_peak = 0.16` (interval [0.12, 0.20]) — fraction of
daily volume concentrated in the binding peak hour. Peak-hour demand per
segment-direction: `Q = ADT · f_peak · d_split`. The daily ADT in the dataset
is thus converted to a peak-hour demand, which is the binding constraint on
capacity.

## Exchange 9
**Q:** If part of a highway were converted into a bus-and-rideshare lane, how
would everyday drivers usually react?

**Reply (summary):** Mostly negatively, same "empty lane" backlash;
acceptance requires the lane to be visibly well-used.

**Model use:** Supports the policy recommendation structure: dedicated lanes
(in any form — AV-only or HOV/bus) are only advisable when utilization is high
and general traffic is not worse off. The HOV scenario (c) is modeled with the
same lane-removal mechanics as (b) and evaluated against the same acceptance
criterion from exchange 5. Also motivates the alternative policy (AV
platooning in mixed traffic, ramp-metering-style coordination) as the
recommended first step.

## Exchange 10
**Q:** As more cars become self-driving, do most commuters expect to switch to
them quickly, or slowly over many years?

**Reply (summary):** Slowly, over many years — vehicle turnover is the
binding constraint (~12–15 years average fleet life); even 100% new-car
adoption ramps the fleet share gradually.

**Model use:** Parameter `fleet_life = 13 years` (interval [12, 15]). This
bounds the time horizon of the analysis: the 10%→50%→90% penetration path is
a multi-decade process, so policy must be evaluated at each penetration level
as a separate steady state (which the model does via the p grid), and
transitional (mixed-era) effects like the shockwave penalty are the dominant
near-term concern rather than the asymptotic capacity gain.
