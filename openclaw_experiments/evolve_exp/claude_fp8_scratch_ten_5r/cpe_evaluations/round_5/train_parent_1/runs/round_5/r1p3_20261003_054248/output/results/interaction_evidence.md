# Expert Interaction Evidence — Task 2024_D (Great Lakes control)

Ten exchanges, one question each. Each reply is turned into a model parameter
or constraint; the value/range used and where it enters the model are recorded.
The expert's phrasing is not copied into the submission.

## Exchange 1 — Lake Ontario summer working level
- **Question:** For Lake Ontario in summer, roughly what water level is a good
  working level — avoiding both shoreline flooding and shipping trouble?
- **Reply (gist):** good summer level ≈ 75.0 m (IGLD 1985); upper flood concern
  ~75.5 m, lower navigation/draft concern ~74.2 m.
- **Model use:** `LON_TGT[Jun..Sep] = 75.0 m`; `LON_HI = 75.5 m` (hard
  upper); `LON_LO = 74.2 m` (soft lower). Interval: summer months, IGLD 1985.

## Exchange 2 — Lake Ontario winter hold level
- **Question:** For the coldest months, around what level to hold the lake to
  create storage for spring melt without flooding?
- **Reply (gist):** hold ~74.2–74.7 m in Dec–Mar, near/below winter mean ~74.7;
  hard lower bound ~74.0–74.2 m (navigation + hydropower draft).
- **Model use:** `LON_TGT[Dec..Mar] = 74.6 m`; `LON_FLOOR = 74.2 m`.
  Interval: winter/spring storage season.

## Exchange 3 — How much level change causes trouble
- **Question:** How much up/down change from a normal year starts to cause real
  trouble for shorelines or ships?
- **Reply (gist):** trouble begins ±0.3 m, serious at ±0.6 m. High: flooding
  0.3–0.6 m above, damage >0.6 m. Low: draft trouble 0.3 m below, restrictions
  <0.6 m below.
- **Model use:** band tolerance. `|LON − target| ≤ 0.3 m` = satisfactory;
  `>0.6 m` = serious. Used in the 2017 backtest objective (penalty) and as the
  satisfactory/better classification threshold.

## Exchange 4 — Which lake the Soo Locks governs
- **Question:** The Soo Locks outflow into the St. Mary's is mainly a lever for
  which lake's level?
- **Reply (gist):** Lake Superior's level; downstream effect on Huron–Michigan
  is secondary/small relative to their volumes.
- **Model use:** control-to-state mapping `Q_soo → ΔSuperior` (primary). Soo
  outflow is the release term in the Lake Superior mass balance.

## Exchange 5 — Practical monthly swing limits at the dams
- **Question:** How big a monthly swing in released flow is typically practical
  before it is disruptive?
- **Reply (gist):** a few hundred to ~1000 m³/s/month. Soo releases ~1000–2500
  m³/s; moves in steps of a few hundred; >1000 m³/s/month disruptive.
  Moses-Saunders releases ~6000–9000 m³/s; >1000–2000 m³/s/month risks
  downstream flooding/navigation. Limits are downstream-consequence driven.
- **Model use:** control-smoothing constraints
  `|Q_soo(t)−Q_soo(t−1)| ≤ 1000 m³/s`;
  `|Q_msd(t)−Q_msd(t−1)| ≤ 2000 m³/s`. Bounds:
  `Q_soo ∈ [1000, 2500]`; `Q_msd ∈ [6000, 9000]` m³/s.

## Exchange 6 — Priority when shipping vs shoreline conflict
- **Question:** If keeping Ontario high for ships conflicts with keeping it low
  to protect shorelines, which is prioritized first?
- **Reply (gist):** shoreline/flood protection first — err toward keeping the
  lake lower. Asymmetry: flood damage is immediate/irreversible; low-water cost
  is economic and recoverable. Plans encode flood criteria as hard constraints;
  navigation as secondary objective.
- **Model use:** objective weighting. Upper excursion (flooding) penalty
  `w_hi = 3×` the lower (draft) penalty `w_lo = 1×`. `LON_HI = 75.5 m` treated
  as a hard (infeasibility) constraint in the LP; `LON_LO` soft.

## Exchange 7 — Dominant environmental driver
- **Question:** Which single factor — spring snowmelt, rain, or evaporation —
  drives the biggest level swings in the lower Great Lakes?
- **Reply (gist):** spring snowmelt/runoff dominates the *annual* cycle
  (±0.3–0.5 m rise on Ontario). Multi-year extremes dominated by precipitation
  minus evaporation (~0.6–1 m), evaporation important on shallow warm lakes.
- **Model use:** sensitivity-analysis shock design. Annual-cycle test perturbs
  spring inflow; multi-year test perturbs precipitation−evaporation balance.

## Exchange 8 — Which lake the St. Lawrence outlet governs
- **Question:** The St. Lawrence below the dam, where the Ottawa joins, is
  mostly a concern for which single lake's level?
- **Reply (gist):** Lake Ontario's level — Moses-Saunders is Ontario's outlet
  control. Ottawa joins *downstream* of the dam, so it does not feed back into
  Ontario; it only affects Montreal/St. Lawrence downstream.
- **Model use:** topology: `Q_msd` is the outflow term in the Lake Ontario
  mass balance. `Q_ottawa` enters the St. Lawrence *downstream* and is excluded
  from the Ontario state equation.

## Exchange 9 — What a well-managed year looks like
- **Question:** Do levels stay within a normal band, or wander well outside
  even with good control?
- **Reply (gist):** follow the natural seasonal cycle; winter drawdown,
  spring–early-summer rise 0.3–0.5 m, fall decline. Control shaves peaks /
  fills troughs but cannot eliminate the swing. Realistic: within ±0.3 m of
  seasonal normal, excursions toward ±0.6 m in wet/dry years.
- **Model use:** acceptance criterion for the 2017 backtest. A controlled year
  is "satisfactory" if deviations stay ≤0.3 m and brief, "better" if the
  time-in-band and max-exursion improve over the recorded 2017 path. Sets the
  target seasonal cycle (not a flat level).

## Exchange 10 — Worst outcome and its risk window
- **Question:** What is the worst outcome operators most want to avoid, and
  roughly when?
- **Reply (gist):** sustained high water → widespread shoreline flooding and
  erosion; the hard constraint. Risk window: late spring–early summer
  (May–July), when snowmelt/runoff peaks and a wet year pushes the lake to its
  seasonal max. Secondary window: Feb–Apr rapid melt / ice-jam surge.
- **Model use:** primary failure mode → the model's hard upper constraint is
  weighted toward May–July; the sensitivity test stresses spring inflow with an
  added ice-jam/snowmelt surge in Feb–Apr.

## Parameters supplied by the task dataset (not expert)
- All lake levels (m) and river flows (m³/s), 2000–2022: from
  `Problem_D_Great_Lakes.xlsx`.
- Lake areas / storage constants: derived by mass-balance calibration against
  the 2009–2022 observed record (documented in the model script).
- 2017 control backtest uses the observed 2017 flows and levels.

## Search-helper retrieval (for empirical constants, with DOIs)
- Great Lakes surface areas / volumes — used for level-to-volume conversion.
- IJC Lake Ontario–St. Lawrence regulation range — cross-checked against
  exchanges 1–3.
