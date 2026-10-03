# Interaction Evidence — Task 2024_D (Great Lakes water-level control)

10 exchanges, one question each. Each entry: question (verbatim), reply
(verbatim), and the concrete change it forced into the model.

---

## Exchange 1

**Q:** When Lake Ontario's water gets too high or too low, what does the dam
operator actually change to fix it?

**A:** The operator changes the **outflow through the Moses-Saunders Dam at
Cornwall** — how much water is released down the St. Lawrence River. Too high →
increase release to lower the lake; too low → decrease release to hold water
and raise the lake. Constraint: it is a trade-off, since raising Lake Ontario
outflow lowers the lake but raises downstream St. Lawrence/Montreal flooding
risk, and vice versa. The operator balances Lake Ontario levels against
downstream St. Lawrence levels within the applicable regulation plan
(historically Plan 2014). Inflow (Lake Erie via Niagara River, plus local
runoff and the Ottawa River joining downstream) is not controllable.

**Effect on the work:**
- Fixed the control topology: the single decision variable for the Ontario
  sub-problem is the St. Lawrence outflow at Cornwall, `Q_LS(t)`. It is the
  lever, not the lake level itself.
- Made the control objective bi-objective: minimize |lake level − target| while
  penalizing downstream (St. Lawrence) level excursions. This becomes the
  weighted objective in the Ontario controller.
- Set the sign convention: `Q_LS` up ⇔ lake down; `Q_LS` down ⇔ lake up.
- Inflows (Niagara + Ottawa + local runoff) are exogenous inputs, not
  decision variables.

---

## Exchange 2

**Q:** What level should the dam keep Lake Ontario at year-round, and does that
target level change through the seasons?

**A:** No single fixed target; the regulation plan (Plan 2014) defines a
**seasonal band**, not a flat setpoint. Levels rise in spring (snowmelt +
rainfall inflow) and decline summer→fall/winter. The plan specifies a desired
range of levels that varies month by month, and the operator keeps the lake
within that band while respecting downstream St. Lawrence conditions. The band
balances stakeholders: higher favors boating/recreation/wetland health, lower
reduces shoreline flooding/erosion, mid-range supports navigation and
hydropower. Band width is roughly a few tenths of a meter to about a meter
around the seasonal norm; exact monthly values come from the regulation plan.

**Effect on the work:**
- The control target is a **seasonal band** `L_target(t) ∈ [L_low(t), L_high(t)]`,
  not a constant. I estimate the monthly band from the 2000–2022 Lake Ontario
  record (mean ± a fixed fraction of the standard deviation per month), since
  the plan's exact monthly values are not in the dataset.
- The cost is a **quadratic penalty for leaving the band** (deadzone), not a
  penalty toward a point: zero cost inside `[L_low, L_high]`, quadratic outside.
- Confirmed the seasonal phase: spring high, autumn low — this shapes the
  `L_target(t)` seasonal cycle.

---

## Exchange 3

**Q:** About how much can the dam actually change Lake Ontario's level in a
month, in meters?

**A:** Roughly a few centimeters to about 0.1–0.2 m per month under normal
operation (empirical judgment). Lake Ontario's surface area is large
(~19,000 km²), so a sustained outflow change of order 1,000 m³/s shifts the
level by only ~0.1 m over a month. The dam's controllable release range (a few
thousand m³/s at most, usually less due to downstream constraints) translates
to roughly 0.05–0.2 m/month achievable level change. Caveats: this is the *net*
controllable effect, superimposed on much larger uncontrolled inflow/outflow
(Niagara, precipitation, evaporation) that can move the level several tenths of
a meter in a month on their own. Over a full season the accumulated effect can
reach a few tenths of a meter, but the dam cannot make large month-to-month
corrections — it only nudges the trajectory.

**Effect on the work:**
- Sets the **actuator slew-rate limit**: `|L_{t+1} − L_t| ≤ 0.2 m/month` is the
  maximum the control can produce; I model the control as able to move the lake
  at up to `ΔL_max = 0.2 m/month`.
- Implies a **control-effort penalty**: large month-to-month changes in
  `Q_LS` (and hence in the lake level) are costly and should be penalized in the
  objective to keep the trajectory smooth ("nudge the trajectory").
- Establishes that the dam is a **weak actuator** relative to uncontrolled
  inflow — so the controller should not be blamed for level deviations larger
  than ~0.2 m/month beyond what inflow forcing causes. This bounds the
  achievable performance and sets the sensitivity-analysis expectations.
- Cross-checked against the data: a 1,000 m³/s change for one month
  (≈ 2.6×10⁹ m³) over ~1.9×10¹⁰ m² (19,000 km²) ≈ 0.14 m — consistent with
  the ~0.1 m figure and with the Lake Ontario area (~1.9×10⁴ km²).

---

## Exchange 4

**Q:** Which group worries most about Lake Ontario being too high — shipping,
shoreline property owners, or someone else?

**A:** **Shoreline property owners** on the low-lying south shore (Rochester–
Oswego, NY) and the Bay of Quinte / eastern Ontario shore. High levels cause
flooding, erosion, and structure damage, and they are the most harmed/vocal when
the lake runs high (as in 2017 and 2019). Shipping worries most about levels
being **too low** (insufficient draft in the St. Lawrence Seaway and harbors);
recreational boaters/marina operators generally prefer higher water. Downstream
St. Lawrence/Montreal residents are a separate group that worries about high
levels too, but that is driven by the *release* downstream, not the lake level.

**Effect on the work:**
- Defines the **stakeholder cost asymmetry** for Lake Ontario:
  - *High-side* cost (flooding) borne by shoreline owners → penalize
    `L > L_high`.
  - *Low-side* cost (navigation/draft) borne by shipping → penalize
    `L < L_low`.
- This makes the band penalty **asymmetric**: the upper penalty (flooding) is
  weighted more heavily than the lower (navigation), because shoreline flooding
  causes direct structural damage and is the "more recent concern" flagged in
  the problem. I set the high-side penalty weight above the low-side.
- The 2017 and 2019 high-water events in the data are the empirical
  calibration anchors for the upper band edge.
- Confirms the downstream (Montreal) penalty attaches to `Q_LS` (release),
  not to the lake level — separate objective term.

---

## Exchange 5

**Q:** In a big spring snowmelt year, does the extra water mostly pass straight
through, or does it pile up in the lakes?

**A:** Mostly it **piles up in the lakes** — it does not pass straight through.
The connecting rivers and the two control dams can only pass a limited amount of
water, and the dams are constrained by downstream flooding limits. When a large
snowmelt pulse arrives, inflow temporarily exceeds what can be released, so the
excess is stored in the lake basins, raising levels across the chain with the
effect propagating downstream over weeks to months. A big snowmelt year shows up
as high lake levels that **persist for a season or more**, not as a quick
flush-through. The lakes act as large buffers/reservoirs, which is why high-water
years (2017, 2019) linger rather than spike and vanish.

**Effect on the work:**
- Justifies the **mass-balance (storage) dynamics** as the core mechanism:
  `dS/dt = Q_in(t) − Q_out(t)`, with the lake level `L` a function of storage
  `S` (via the area-height relation). Inflow exceeding releasable outflow
  accumulates in storage.
- Establishes **outflow-capacity constraint**: the dam/river release is bounded
  above by downstream flooding limits, so `Q_out ≤ Q_cap`. This is the hard
  ceiling the controller must respect.
- Explains **persistent high-water**: once storage is high it decays slowly
  (the lake is a low-pass filter), so the control can only nudge it — consistent
  with the 0.05–0.2 m/month actuator limit from Exchange 3.
- Justifies a **stateful controller** (the current level carries into the next
  month's decision) rather than an open-loop monthly rule.

---

## Exchange 6

**Q:** When the lake is swelling fast in a flood spring, does the operator crank
up the outflow as much as possible, or hold back?

**A:** **Hold back** — the operator does not crank outflow to the maximum. The
binding constraint is downstream, not the lake. Dumping maximum release down the
St. Lawrence raises water levels and flooding risk in the Montreal / downstream
St. Lawrence region, which is exactly the harm the regulation plan is designed
to avoid. During a fast-rising flood spring the operator releases as much as
downstream conditions safely allow — often less than the lake alone would
justify — and accepts that some excess must be stored in the lake. Result: the
trade-off seen in high-water years — Lake Ontario runs high (south-shore
flooding) precisely because the operator is holding back to protect downstream.
The dam cannot simultaneously protect both ends; the plan allocates the pain
between them.

**Effect on the work:**
- Adds the **downstream-flood penalty** as a first-class objective term:
  `pen_ds = w_ds * max(0, Q_ls(t) − Q_ds_flood(t))^2`, where `Q_ds_flood(t)` is
  the monthly downstream-flood-release threshold. The controller will now
  *hold back* in flood springs rather than drain to the band, reproducing the
  observed high-water years.
- Reframes the 2017 comparison: the "improvement" a controller can claim is not
  "match the high levels" but "allocate the pain between the lake and
  downstream optimally." The objective is the joint stakeholder cost
  (shoreline flooding + downstream flooding + navigation), and the managed
  trajectory is the Pareto-optimal split.
- Sets `Q_ds_flood` from the St. Lawrence record (its own seasonal
  mean + band), so the release is capped at what downstream can safely absorb.
- Explains why the actual 2017 levels (which the real dam produced) are a
  *reference allocation*, not the optimum: my managed policy should keep the
  downstream within its safe band while improving the lake's band adherence
  relative to a naive drain-to-max policy.

---

## Exchange 7

**Q:** How directly does the Soo Locks at Sault Ste. Marie control the water
level of Lake Ontario?

**A:** Very indirectly — essentially not at all in any direct sense. The Soo /
Compensating Works control the outflow of **Lake Superior** into the St. Mary's
River, which feeds Michigan–Huron. Lake Ontario is at the far downstream end
(Superior → Michigan–Huron → St. Clair → Erie → Ontario), so any Soo effect on
Ontario is transmitted only through the intervening lakes and channels, over
long lags (months to years), heavily damped by the storage in those basins.
Ontario's level is controlled directly by the **Moses-Saunders Dam at Cornwall**
(its outflow) plus uncontrolled Niagara inflow, precipitation, evaporation, and
local runoff. The Soo is not a meaningful lever for Lake Ontario.

**Effect on the work:**
- Fixes the **network topology** for the Ontario sub-problem: the only control
  lever on Lake Ontario is `Q_LS` (Moses-Saunders). The Soo/Compensating Works
  is a control lever only upstream (on Lake Superior), and its influence on
  Ontario is a long-lag, damped, second-order term — negligible at monthly
  resolution. So the Ontario controller has **one decision variable**.
- The full five-lake network model (Superior → Michigan–Huron → St. Clair →
  Erie → Ontario) is a **cascade of mass balances**, each lake's level driven by
  its own inflow and outflow; the two dams are the two decision points (Soo for
  Superior, Cornwall for Ontario). For the Ontario focus, the upstream lakes
  enter only as the Niagara inflow forcing.
- Justifies treating Niagara + local runoff as exogenous forcing for Ontario,
  and not attempting to close the loop through the upper lakes in the Ontario
  controller.

---

## Exchange 8

**Q:** Which month is the riskiest for shoreline flooding on Lake Ontario's south
shore — late spring, summer, or fall?

**A:** **Late spring — typically May–June.** Lake Ontario's level peaks
seasonally in late spring/early summer, driven by snowmelt and spring rainfall
inflow from the upper lakes and local runoff. The seasonal maximum normally
occurs around late May to June, when the highest water sits against the south
shore and flooding/erosion risk is greatest. Summer and fall are lower-risk: the
lake declines through summer into fall as inflow drops and evaporation
continues. The worst observed events (2017, 2019) were late-spring/early-summer
peaks, consistent with this.

**Effect on the work:**
- Confirms the **seasonal phase and the flood-critical window**: the upper band
  `L_hi(t)` is tightest (and the high-side penalty `w_hi` most consequential)
  in **May–June**, matching the data's seasonal maximum (monthly-mean peak in
  Jun = 75.154 m; 2017 and 2019 both peaked in June).
- Justifies a **seasonally modulated high-side penalty**: `w_hi(t)` is weighted
  highest in the May–June flood window so the controller holds back most
  aggressively exactly when shoreline risk is greatest, and relaxes it in the
  low-risk fall/winter months.
- Sets the **validation target**: the managed trajectory must not exceed the
  observed seasonal peak in May–June by more than the actuator limit
  (~0.2 m/month).

---

## Exchange 9

**Q:** Does the dam operator set each month's release using just that month's
data, or do they also plan ahead to the coming season?

**A:** They **plan ahead** — the release is not set month-by-month on current
data alone. The operator uses **forecasts of the coming season** (expected
snowmelt runoff, precipitation, upper-lake inflows, and downstream St. Lawrence
conditions) and sets releases to manage the lake's trajectory over the next
weeks to months, not just to react to the present level. This is necessary
because the dam can only nudge the level (~0.05–0.2 m/month), so corrections
must be made early and in anticipation of the seasonal rise or decline. In
practice it is a **rolling, forward-looking operation**: each decision accounts
for both current conditions and the projected seasonal outlook, within the
seasonal band defined by the regulation plan.

**Effect on the work:**
- Upgrades the controller from **myopic (one-step)** to **rolling
  forward-looking (model-predictive)**: at each month the controller minimizes
  the band-violation cost over a *look-ahead horizon* (I use 3 months), using
  the forecast inflow for the horizon, then commits only the first release and
  re-optimizes next month (receding horizon).
- The forecast inflow for the horizon is the **seasonal climatology** (monthly
  mean inflow from the record), which is the operator's best seasonal outlook
  absent a real-time forecast.
- Justifies the management plan's **seasonal operating rule**: pre-position the
  lake in winter (lower storage) so the spring rise can be absorbed, rather than
  reacting in April. The MPC naturally produces this pre-positioning.
- The look-ahead also lets the controller *anticipate* the May–June flood peak
  and hold back storage starting in March–April, improving the critical-window
  performance.

---

## Exchange 10

**Q:** If you had to pick one group whose damage to avoid matters most when
levels get high, who would it be?

**A:** **Shoreline property owners on Lake Ontario's low-lying south shore**
(Rochester–Oswego, NY) and the Bay of Quinte / eastern Ontario shore. They
suffer direct, concentrated, largely irreversible damage when the lake runs high
— flooded homes, erosion, destroyed shoreline structures — and were the most
harmed and most vocal in the high-water years (2017, 2019). Shipping and
recreational interests are hurt mainly by *low* water, so they are not the
binding concern when levels get high. Caveat: downstream St. Lawrence / Montreal
residents also face high-water damage, but that is driven by the *release*, not
the lake level — a separate trade-off, not the same "avoid high levels" concern.

**Effect on the work:**
- Sets the **stakeholder priority order** for the management plan's objective:
  1. Avoid south-shore/Bay of Quinte shoreline flooding (highest weight,
     high-side lake-level penalty).
  2. Avoid downstream St. Lawrence / Montreal flooding (high-side *release*
     penalty, separate term).
  3. Maintain navigation draft (low-side lake-level penalty, lowest weight).
  4. Recreation / wetland (mid-range preference, folded into the band).
- Justifies the **asymmetric, prioritized multi-objective** structure: the
  high-side lake-level penalty dominates, and the downstream-release penalty is
  the second-priority constraint. This is the weighting the IJC memo should
  present as the "social objective."
- Confirms the **two distinct high-side costs** (lake-level flooding vs
  release-driven downstream flooding) must be modeled as separate terms, which
  the controller already does (`pen_hi` on L, `pen_ds` on Q_ls).









