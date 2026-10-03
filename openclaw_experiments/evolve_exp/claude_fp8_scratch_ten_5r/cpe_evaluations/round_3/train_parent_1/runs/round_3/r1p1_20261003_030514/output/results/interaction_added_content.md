# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — Problem 2024_D (Great Lakes / Lake Ontario)

Ten exchanges, one question each. Questions asked before the work they govern;
each later question builds on the prior reply. Replies were turned into model
parameters or decision rules (see "Effect on the work" per exchange). No reply
text was copied into the submission.

## Exchange 1
- **Question:** How many centimeters of lake level change before problems start to show up (shipping + shoreline)?
- **Reply (key values):** ~30 cm (1 ft) is where problems begin; 60–90 cm (2–3 ft) is dramatic. Seasonal/multi-year swings of 30–100+ cm are normal; ~30 cm of lost depth starts reducing draft, ~30 cm rise starts threatening low-lying property.
- **Effect on the work:** Set the stakeholder tolerance bands. The model's cost function uses D_SAFE = 0.30 m (problem onset) and D_DRAM = 0.90 m (dramatic) as the band edges for the severe-deviation penalty, and the ±0.30 m band around the seasonal target defines "acceptable" water level.

## Exchange 2
- **Question:** Low water: which is hurt first — ships aground, or shoreline property damage?
- **Reply (key facts):** Low water is one-sided (removes depth); shipping (light-loading then groundings) is the first and dominant casualty. Shoreline damage is primarily a high-water phenomenon (flooding, erosion).
- **Effect on the work:** Made the stakeholder cost function asymmetric — a low-side (shipping/draft) term and a high-side (shoreline/flood) term with separate weights (P_LOW, P_ON), rather than a single symmetric error. This encodes "low hurts ships, high hurts shore."

## Exchange 3
- **Question:** How fast does a big lake's level react to an outflow change? Days, weeks, months?
- **Reply (key values):** Weeks to months, not days. A 1000 m³/s step for a day moves the level only ~1 cm; full adjustment to a new equilibrium takes several months to a season.
- **Effect on the work:** Justified a monthly control period (not daily) and a first-order storage dynamics with a response time of months. The backtest integrates month-to-month, consistent with the "weeks-to-months" response.

## Exchange 4
- **Question:** Niagara River monthly variation — mostly power-plant water or natural rain/snowmelt?
- **Reply (key facts):** Mostly natural (rain/snowmelt via Lake Erie). Power diversions are large but steady and Treaty-limited (1950 Niagara Treaty minimums); they modulate around a stable level rather than create the month-to-month swings.
- **Effect on the work:** Treated the Niagara River as a *natural, uncontrolled inflow* to Lake Ontario in the balance (not a control variable). Only the St. Lawrence outflow is manipulated. This is the structure of the Ontario node: inflow = Niagara + Ottawa + N, outflow = controllable Q.

## Exchange 5
- **Question:** What level do shipping interests most want Lake Ontario at? Do they care about high water?
- **Reply (key values):** Upper end of normal range, near the long-term average or somewhat above (~75.2 m IGLD, mid-to-upper of the ~74.2–75.8 m operating range). They want "high but stable" — dislike the low end (lost draft) and rapid drawdowns; secondary casualties of high-water management.
- **Effect on the work:** Set the control target as the long-term seasonal mean curve m(month) (the "normal" level), not a flat low level. The controller tracks this trajectory, which sits in the mid-to-upper range, matching the shipping preference for "high but stable."

## Exchange 6
- **Question:** High water threatening homes: what do operators do first — open dams more, or ask upstream to release less?
- **Reply (key facts):** Open the dams more — increase outflow at Moses-Saunders/Compensating Works. Inflows (Niagara, Ottawa/St. Lawrence) are uncontrolled (no upstream reservoir to hold back the Niagara). Response is capped by downstream flood constraints (St. Lawrence corridor / Montreal).
- **Effect on the work:** Defined the control variable as the St. Lawrence *outflow* Q(t) (the only lever), and the inflows as fixed/uncontrolled. This is exactly the state equation used: dL/dt = (N + Q_Niagara + Q_Ottawa − Q)/A, with Q the decision.

## Exchange 7
- **Question:** How much can St. Lawrence outflow safely vary from usual before downstream (Montreal) has problems?
- **Reply (key values):** Asymmetric. High side: small margin, ~10–20% above normal/regulated outflow (Montreal–Lachine reach limits it, esp. with Ottawa spring runoff). Low side: can be cut substantially (tens of percent) before navigation/water-quality affected; minimum-flow rules set a floor.
- **Effect on the work:** Set the control bounds on Q(t): upper cap Q_max = (1 + headroom)·Q_base with headroom in the 10–20% range (model default 15%, swept 10–30%), and a lower floor Q_min ≈ 75–80% of Q_base. The sensitivity table shows cost/RMSE trade-off across the headroom range.

## Exchange 8
- **Question:** If a dam's flow is nudged, how long until the next lake downriver shows the change?
- **Reply (key values):** Weeks to a couple of months — same order as the lake's own response; the channel travel time is days at most, the real delay is hydraulic (the downriver lake must accumulate volume).
- **Effect on the work:** Confirmed the network is well-approximated by independent monthly storage nodes for the 5 lakes (no fast wave-coupling needed), and that the control effect on a lake accumulates over the monthly horizon — consistent with the per-lake state equations.

## Exchange 9
- **Question:** Deciding monthly release: bigger worry — this month's flow, or where the level ends up next spring?
- **Reply (key facts):** Where the level ends up (the multi-month trajectory / seasonal endpoint), not this month's flow. Each month's flow is a step toward a target seasonal trajectory, bounded only by immediate downstream limits.
- **Effect on the work:** Framed the problem as a *trajectory-tracking optimal control* over the year, with the seasonal target curve m(month) as the reference and the monthly outflow as the bounded input. The cost penalizes deviation from the seasonal trajectory (endpoint/seasonal position), not month-to-month flow variation.

## Exchange 10
- **Question:** Drought year with less inflow: keep levels normal, or accept a lower level?
- **Reply (key facts):** Accept a lower level — cannot hold levels at normal in drought. Outflow is the only lever and is bounded below by downstream needs; cannot manufacture inflow. Management shifts to slowing the decline and distributing the shortfall. No upstream reservoir can top the lake up.
- **Effect on the work:** Defined the drought/failure behavior: the controller does not fight a genuine supply deficit by over-releasing; it manages the *rate of decline* within the bounded Q, letting the level fall and allocating the shortfall between shipping and shoreline. This is the edge-case (boundary) behavior encoded by the lower bound on Q and the one-sided low-side cost.
