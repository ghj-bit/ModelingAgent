# Interaction Evidence

## Exchange 1
- Q: On congested Seattle freeways (I-5/90/405), do human drivers keep a few-second gap or run much closer, bumper to bumper?
- Reply (value extracted): at near-capacity flow human headways ≈ 1.5–2 s, dropping toward ~1 s or less in stop-and-go; "few seconds" is free-flow behavior.
- Use in model: human free-flow time headway = 1.5–2.0 s (central 1.75 s) as baseline gap parameter g_hum; human gap in unstable flow shrinks toward 1 s, which is why instability (phantom jams) exists in the human-only system. Sets baseline for the AV-gap-reduction contrast. Holds for: U.S. urban freeways at/near capacity, 2015-era conventional traffic.
## Exchange 2
- Q: When Seattle freeways are jammed at rush hour, what do officials usually propose first, more lanes or special express/carpool lanes?
- Reply (value extracted): engineers manage existing lanes first (HOV, express toll lanes, ramp metering, demand management); adding general-purpose lanes is last resort (expensive, 10+ years). Regional practice: SR 520 & I-405 express toll lanes, I-5 HOV.
- Use in model: policy question answered structurally — dedicated-lane recommendation is conditional; the model compares (a) mixed-lane penetration p, (b) one dedicated lane removed from general flow (L->L-1) with its capacity given to the AV class, (c) express-lane pricing as demand management. The dedicated-lane branch is only recommended if AV share is high enough that the dedicated-lane capacity gain exceeds the lost general lane at peak (computed in the model).
## Exchange 3
- Q: Are express toll lanes on Seattle freeways mainly full of solo drivers?
- Reply (value extracted): yes, largely — single-occupant paying vehicles are a large (majority) share of express-lane traffic at peak; the pricing mechanism exists so solo drivers buy in.
- Use in model: dedicated/express lane at high AV penetration will be filled by a large share of solo drivers, so a dedicated AV lane does NOT crowd out carpool demand — the AV lane carries solo drivers who would otherwise clog general lanes. This supports recommending a dedicated lane at high p: solo AV users migrate in, freeing general lanes.
## Exchange 4
- Q: On the same freeways, about how many minutes does a rush-hour trip take compared to off-peak?
- Reply (value extracted): peak trip time ≈ 1.5–2.5× off-peak (2.5–3× on worst corridors/bad days); e.g. 20 min off-peak → 30–50 min peak.
- Use in model: peak:off-peak time ratio r_peak ∈ [1.5, 2.5] (central 2.0) calibrates the diurnal demand profile: V_peak = 15×V_avg (AASHTO peak-hour factor implied), and peak congestion level of service derived from speed ratio ≈ 1/2 of free-flow. Bounds the time-in-day demand curve D(t) used in the flow model.
## Exchange 5
- Q: In heavy rush hour, do cars stay in one lane and follow, or keep changing lanes?
- Reply (value extracted): at near-capacity flow car-following dominates; lane changes are suppressed (difficult/risky), only a small fraction of vehicles jockey. Throughput governed by headway behavior, not lateral movement.
- Use in model: justifies lane-wise independent car-following formulation — each lane treated as a 1-D flow line with per-lane capacity, no lane-change coupling term needed at high density. The capacity of a corridor = sum of lane capacities (valid at near-capacity where lane changes are rare).
## Exchange 6
- Q: When stuck in jams, do drivers keep driving and wait, or do many leave the freeway / switch to side streets?
- Reply (value extracted): large majority stay in the queue and creep; bail-out (exit, parallel arterial, trip abandon) is a small minority, growing only when delay is severe and a known alternate exists.
- Use in model: demand in the corridor is inelastic over the modeled period — no route-diversion outflow term; all demand must be carried by the freeway corridor (V(t) fixed, only flow-through adjusts). This is what makes the tipping-point / equilibrium questions well-posed: congestion is absorbed by the corridor, not shed to alternatives.
## Exchange 7
- Q: On the Seattle freeways, are buses and big trucks a large part of daily traffic, or mostly regular cars?
- Reply (value extracted): passenger vehicles 90%+ of vehicles; heavy trucks low single digits to ~5–10% (higher on I-5 as freight corridor); buses a tiny fraction.
- Use in model: traffic is modeled as a single passenger-vehicle class with a truck adjustment factor f_HV ∈ [0.95, 1.0] applied to capacity (heavier on I-5). No separate transit or heavy-freight flow equations needed; AV penetration p is applied to the passenger-vehicle stream.
## Exchange 8
- Q: If one lane were reserved only for driverless cars, would ordinary drivers be glad or annoyed about losing a lane?
- Reply (value extracted): at 10% or 50% AV share the dominant reaction is annoyance (perceived loss of general capacity); acceptance only if the reserved lane is clearly underused/surplus and the driver's own trip measurably improves.
- Use in model: dedicated-lane recommendation is gated: recommend a dedicated AV lane only when (i) p is high enough (90%) AND (ii) the model shows general-lane delay improves despite losing one lane. At p=10%, 50% recommend NO dedicated lane; the AV benefit is delivered within mixed lanes via headway reduction.
## Exchange 9
- Q: When self-driving fleets first tested on public roads, did they mainly use outside or inside fast lanes?
- Reply (value extracted): early fleets concentrated in the outside (right-hand) lane and surface streets; avoided inside fast lanes (highest speed, least forgiving).
- Use in model: at low-to-mid penetration, AVs are disproportionately present in the right (slower, merge-heavy) lanes, so the rightmost lane's effective capacity gains from AV headway reduction first; the model applies a lane-position weighting w_j with w_j largest in the outer lanes, decaying toward the left. This means early penetration benefits the outer lanes, where ramps/merges also occur — the bottleneck segments.
## Exchange 10
- Q: On the Seattle freeways, which is the bigger source of rush-hour slowdowns, heavy traffic volume, or the many on-ramps and off-ramps?
- Reply (value extracted): volume (demand exceeding capacity) is the primary cause; ramps/merges are a secondary trigger that causes breakdown earlier than volume alone would (merge turbulence, weaving, ramp-metering effects).
- Use in model: the capacity-demand (V/C) ratio is the dominant driver of congestion; ramps add a localized stability penalty at merge points, modeled as a small reduction in critical density at bottleneck segments (critical density reduced by ~10-20% at interchange segments) rather than a separate flow path. This means AV headway reduction helps primarily by raising stable capacity (the volume problem), while merge turbulence is a secondary correction.
