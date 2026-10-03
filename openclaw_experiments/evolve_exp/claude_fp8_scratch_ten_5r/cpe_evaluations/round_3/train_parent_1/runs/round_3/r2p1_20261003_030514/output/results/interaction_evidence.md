# Expert Interaction Evidence — Problem 2024_D (Great Lakes)

Ten exchanges, one question each, in order. For each: the question (paraphrased),
the expert's reply (key values), and how the reply became a parameter,
constraint, equation, or test in the model. The reply is input, not content;
the values below are restated in the model's own formulation.

## Exchange 1 — navigation constraint (high water)
- **Q:** Do ships get through when a lake is ~0.5 ft above normal, or do
  operators start restricting the locks?
- **Reply (key values):** High water does NOT restrict navigation. The
  binding constraint is LOW water: under-keel clearance limits light-loading
  at ~0.3–0.6 m below chart datum. High-water limits (lock/bridge clearance,
  shoreline flooding) only matter at ~1–2 ft above normal or more. The 0.55 ft
  (0.165 m) IJC daily band above target is well inside tolerance.
- **Became in model:**
  - Navigation is modeled as a LOW-water constraint, not high-water.
  - `NAV_LOW = 0.30 m` below chart datum = start of light-loading (used in
    the stakeholder cost for shipping).
  - Confirmed the IJC 0.55 ft daily band (0.165 m) is the correct operating
    tolerance; the controller's monthly-mean band `w = 0.10` (≈0.9 m, the
    monthly analogue of the 0.165 m daily band scaled by √30) is set so the
    release stays within operational tolerance.

## Exchange 2 — Lake Ontario flood threshold (lower than other lakes)
- **Q:** Does shoreline flooding on Lake Ontario begin at the same height
  above normal as other lakes, or lower?
- **Reply (key values):** Notably LOWER on Lake Ontario (steeper, more
  developed shoreline; smaller area so a given surplus raises level faster).
  Flooding complaints start at ~0.3–0.6 m (1–2 ft) above long-term average;
  serious above ~0.75 m (2.5 ft). This is lower than the 1–2 ft+ threshold
  for the other lakes.
- **Became in model:**
  - `FLOOD_THRESHOLD = 0.30 m` above seasonal target = start of flood damage
    (LO-specific, lower than upper lakes).
  - `SERIOUS_THRESHOLD = 0.75 m` above seasonal target = serious damage.
  - These define the flood-cost terms in the stakeholder objective and the
    "months above flood threshold" KPI. The 2017 (peak +0.69 m) and 2019
    (peak +0.76 m) episodes are thus correctly classified: 2019 crossed into
    "serious" territory, 2017 did not.

## Exchange 3 — seasonal swing amplitude
- **Q:** In a normal spring, how big is the swing from the Feb/Mar low to
  the May/Jun high, in feet?
- **Reply (key values):** ~1–2 ft (0.3–0.6 m) on Lake Ontario, usually near
  the lower end (~1 ft), up to ~1.5–2 ft in wet years.
- **Became in model:**
  - The Plan-2014-style seasonal target level `lo_mean[m]` (long-term monthly
    mean) has a swing of 74.56 (Nov) → 75.15 (Jun) = 0.59 m, consistent with
    the expert's 0.3–0.6 m. This validates the choice of the long-term
    monthly mean as the seasonal target (the target the controller aims to
    hold the lake at).
  - Inflow-driven spring rise: the controller's `Kd` term (freshet slope)
    responds to the rate of inflow increase, matching the expert's "respond
    within days" (next exchange).

## Exchange 4 — operator response time and limits
- **Q:** When water rises fast in spring, do operators respond within days
  or wait to see if it peaks on its own?
- **Reply (key values):** Respond within days, not weeks. But the response is
  CONSTRAINED, not free: (a) downstream constraint — increasing outflow raises
  the St. Lawrence level at Montreal, so releases are capped when downstream
  flood risk is high (exactly the wet-spring condition); (b) ice and channel
  limits in early spring.
- **Became in model:**
  - The control law is a FEEDBACK controller (responds to current inflow and
    its slope), not an open-loop seasonal schedule — matching "respond within
    days."
  - The `Kd` term (inflow slope) implements the fast response to a rising
    freshet.
  - The downstream (Montreal) constraint becomes the Ottawa-freshet cap (see
    exchange 5): the controller trims release when the Ottawa is high,
    because releasing more would flood Montreal.

## Exchange 5 — how often the downstream cap binds
- **Q:** How often in a typical wet spring does the downstream flood risk
  force the dam to hold back water it would otherwise release?
- **Reply (key values):** In a wet spring, the cap binds repeatedly during the
  freshet window (days to ~2 weeks around the Ottawa peak), in most
  unusually-wet springs and only occasionally in a normal year. The Ottawa
  River's freshet peaks at roughly the same time as the Lake Ontario rise.
- **Became in model:**
  - The cap is modeled as a THRESHOLD trigger on the Ottawa: it binds when
    `Ottawa[m] / Ottawa_base[m] > 1.5` (i.e., the Ottawa is >50% above its
    monthly normal). This is the "Montreal flood risk" condition.
  - `FLOOD_TRIGGER = 1.5` (dimensionless ratio).
  - The cap is modeled as BINDING IN WET SPRINGS (2017: 4 months; 2019: 2
    months) and not binding in normal years — matching the expert's "repeatedly
    in wet springs, rarely in normal years."

## Exchange 6 — Ottawa freshet magnitude
- **Q:** In a wet year, how many feet above its usual late-winter level does
  the Ottawa climb at its spring peak?
- **Reply (key values):** ~3–6 ft (1–2 m) above late-winter low at the
  Carillon gauge in a wet year; the Ottawa's basin is large, snow-fed, and
  unregulated in its upper reaches, so its spring rise is much bigger than
  Lake Ontario's ~1 ft seasonal swing.
- **Became in model:**
  - Confirms the Ottawa is the DOMINANT flood driver (its freshet is 3–6× the
    lake's own seasonal swing). This justifies modeling the Ottawa as the
    trigger for the Montreal cap, not the lake inflow.
  - The data confirm: Ottawa Apr–Jun mean / Jan–Mar mean ratio is 2.06 (2017)
    and 2.51 (2019) — i.e., the freshet is 2–2.5× the base flow, consistent
    with the expert's "much bigger than the lake's swing."
  - `FLOOD_TRIGGER = 1.5` is set below these observed ratios, so the cap
    binds in exactly the wet years (2017, 2019) and not in normal years.

## Exchange 7 — which lever to pull for Montreal
- **Q:** To keep Montreal below flood stage, would you hold back the
  Cornwall release, trim Ottawa releases upstream, or both?
- **Reply (key values):** Both, but NOT equal levers. The Ottawa is the BIGGER
  one: trimming Ottawa releases upstream (50 dams, 13 reservoirs) directly
  reduces the peak reaching Montreal, and those reservoirs exist precisely to
  store spring runoff for that purpose. The Cornwall holdback is the SMALLER,
  more constrained lever — it protects Montreal only indirectly and raises
  Lake Ontario (its own flood stakeholders). Use both, with Ottawa-side
  storage doing most of the work.
- **Became in model:**
  - The Cornwall (Moses-Saunders) release is modeled as the SECONDARY trim,
    not the primary flood control. The primary control is the Ottawa-side
    storage, which is outside the two-dam control scope but is the dominant
    lever.
  - The `Kf` gain on the Ottawa cap is set to `0.25` (a partial trim, not a
    full cutoff), reflecting that the Cornwall lever is the smaller of the two.
  - This is the key structural insight: the two-dam model CANNOT fully solve
    the Montreal flood problem; it can only trim. The Ottawa-side storage must
    do most of the work.

## Exchange 8 — Ottawa reservoir peak-shaving capacity
- **Q:** During the spring freshet, about what share of the Ottawa's peak
  flow can its reservoirs typically hold back before their spillways must
  pass it anyway?
- **Reply (key values):** A modest share — ~10–25% of the peak freshet flow,
  and only for a limited window. The reservoirs SHAVE the peak (flatten and
  delay) rather than absorb it; they fill early in the freshet, and once full
  the spillways pass inflow. Realistic peak reduction ~10–25%, occasionally
  more, near zero once storage is exhausted.
- **Became in model:**
  - The Ottawa-side storage is modeled as a PEAK-SHAVING element with
    capacity ~10–25% of the freshet peak. This bounds how much the Montreal
    cap can actually be relieved by the Ottawa lever.
  - The `Kf = 0.25` gain (25% trim at full excess) is consistent with the
    upper end of the expert's 10–25% range — i.e., the Cornwall trim is set
    at the level the Ottawa storage can support before the spillways pass.
  - Once storage is exhausted (late freshet), the trim goes to zero — the
    model's cap is time-limited to the freshet window, not permanent.

## Exchange 9 — duration of post-flood grievance
- **Q:** After a 2017-style high-water episode, how long does the shoreline
  damage and public anger typically last?
- **Reply (key values):** Physical damage is permanent (erosion, undermined
  foundations, destroyed breakwalls don't heal). Public anger fades over
  ~6–12 months from the peak, but on Lake Ontario the issue NEVER fully goes
  quiet: the 2017 and 2019 episodes are still cited in IJC consultations years
  later, and every subsequent high-water year reopens it. Long tail of
  low-level grievance + periodic flare-ups, not a clean return to calm.
- **Became in model:**
  - The flood-cost term in the stakeholder objective is modeled as a
    PERSISTENT (non-decaying) cost after a threshold crossing, not a one-time
    cost. This reflects that high-water episodes have a long political tail.
  - The KPI "months above 0.75 m (serious threshold)" is reported separately
    from "months above 0.30 m" because the serious-threshold months carry a
    disproportionate, long-lasting stakeholder cost.
  - The 2019 episode (1 month above 0.75 m) is flagged as the one that
    "reopens" the grievance, consistent with the expert's account.

## Exchange 10 — flood vs. navigation weighting in plan review
- **Q:** When the IJC/boards review the regulating plan, do they weigh
  avoiding the next flood more heavily, or avoiding low-water shipping
  disruption more heavily?
- **Reply (key values):** NEITHER dominates permanently — the weighting FLIPS
  with recent experience. After a high-water episode (2017, 2019), the boards
  tilt toward flood avoidance (shoreline owners are organized, vocal,
  litigious). After a sustained low-water period (late 1990s–early 2000s),
  the tilt reverses toward navigation/hydropower. Structurally, flood
  avoidance gets somewhat MORE weight in the Lake Ontario–St. Lawrence
  context specifically, because the shoreline is heavily developed and the
  damage is concentrated and visible, whereas low-water shipping losses are
  diffuse and partly mitigated by light-loading.
- **Became in model:**
  - The stakeholder objective is a WEIGHTED sum with flood avoidance given
    the higher structural weight for Lake Ontario (per the expert's "flood
    avoidance tends to get somewhat more weight" in the LO-SLR context).
  - The model is a POST-2017/2019 model, so it is built under the
    "flood-avoidance-tilt" regime. The weighting is reported as a parameter
    that would shift after a low-water period (the model's domain of validity
    is the current high-water-concern regime).
  - This justifies the controller's priority: keeping the lake below the
    flood threshold (0.30 m) is the PRIMARY objective; keeping it above the
    navigation threshold (0.30 m below chart datum) is the SECONDARY
    objective. The two are asymmetric in weight for Lake Ontario.

## Summary of parameters sourced from exchanges
| Parameter | Value | Exchange | Interval / condition |
|---|---|---|---|
| NAV_LOW (light-loading start) | 0.30 m below chart datum | 1 | low-water regime |
| FLOOD_THRESHOLD (LO flood start) | 0.30 m above seasonal target | 2 | LO-specific, wet season |
| SERIOUS_THRESHOLD (LO serious) | 0.75 m above seasonal target | 2 | LO-specific, wet season |
| Seasonal swing (validates target) | 0.3–0.6 m (model: 0.59 m) | 3 | normal spring |
| Operator response time | days (feedback, not open-loop) | 4 | rising freshet |
| FLOOD_TRIGGER (Ottawa cap onset) | 1.5× monthly normal | 5,6 | wet spring |
| Cornwall lever role | secondary trim (not primary) | 7 | Montreal flood |
| Ottawa storage peak-shave | 10–25% of freshet peak | 8 | freshet window |
| Kf (Cornwall trim gain) | 0.25 | 7,8 | freshet window |
| Post-flood grievance | persistent, 6–12 mo acute | 9 | after threshold crossing |
| Flood vs navigation weight | flood > navigation (LO, post-2017) | 10 | current regime |
