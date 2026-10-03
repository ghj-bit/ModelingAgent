# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — Great Lakes 2024_D

Ten expert exchanges (one question each), in order. Each reply was turned into a
model parameter, structural rule, or test outcome before the next exchange.
The reply is input, not content: only the value/constraint travels into the
model, never the expert's sentences.

---

## X1 — Structural control priority (the dominant rule)
**Q:** When a lake's level is about to drop low enough to block ships, do
operators hold back outflow to keep the level up?
**Reply (gist):** Yes — navigation is a high-priority, legally protected
interest; regulation plans are written to avoid navigation-limiting depths.
Priority order: (1) safety/flood/erosion at the extremes, (2) navigation
depth, (3) hydropower, (4) recreation/ecosystem. Dams modulate flow, they
cannot create water, so in a sustained dry spell they can only slow a decline.
**Effect on work:** Defines the control-law hierarchy the model implements:
flooding avoided at high levels, navigation depth protected at low levels,
hydropower is the flexible slack. Also the hard structural limit "dams cannot
create water" that bounds what any control algorithm can achieve.

## X2 — Navigation floor (quantitative, low side)
**Q:** About how many feet below normal does Lake Ontario's level drop before
ships start being blocked?
**Reply (gist):** First operational problems ~1–2 ft below the long-term
average (deep-draft vessels lighten loads / slow); actual stoppages nearer
2–3 ft below average, only for the largest ships in the shallowest reaches
(St. Lawrence channel, harbor approaches). Planning figure: a sustained
~2 ft below average begins to bite.
**Effect on work:** Sets the navigation floor at `normal - 2 ft` in the
stakeholder cost (low-side threshold) and in the control band.

## X3 — Flood ceiling (quantitative, high side)
**Q:** About how many feet above normal does Lake Ontario's level rise before
shoreline flooding starts hurting homes and businesses?
**Reply (gist):** Real damage ~2–3 ft above average; nuisance flooding/erosion
at the low end, significant property damage, road closures, septic/sewer
problems near/exceeding ~3 ft. Severe events (2017, 2019) ran ~2.5–3+ ft above
average. Planning figure: sustained departure beyond ~2 ft above average begins
to bite shore property.
**Effect on work:** Sets the flood ceiling at `normal + 2 ft` (low end of the
damage band) in the stakeholder cost and control band. Confirms 2017 was a
severe high-water event, motivating the whole exercise.

## X4 — Ottawa freshet management (structural rule)
**Q:** When spring snowmelt floods the Ottawa River, do operators store the
extra water in reservoirs, or release it gradually downstream?
**Reply (gist):** They store it — the 13 large reservoirs hold back a
significant portion of spring runoff and release it over the following weeks,
specifically to cut downstream (Montreal harbor) flooding. Reservoirs are
drawn down in winter to create space, filled during the freshet. Storage is
finite: once full, excess must pass.
**Effect on work:** Justifies treating the Ottawa inflow as a regulated,
peak-shaved series (not raw runoff), and including it as an inflow to Lake
Ontario's balance. Explains the sharp Ottawa spring peak (Apr–May) that the
model's `v = Niagara + Ottawa - Cornwall` term captures.

## X5 — Freshet storage fraction (quantitative)
**Q:** What fraction of the spring freshet do Ottawa reservoirs typically
store rather than release downstream?
**Reply (gist):** Roughly 10–25% of freshet volume is held back (shaves the
Montreal peak by a meaningful margin); low end in large snowmelt years, upper
end in moderate years.
**Effect on work:** Calibration range for the Ottawa regulation term. The model
uses the observed (already-regulated) Carillon series, so this bounds how much
further peak-shaving a control could plausibly add (a limited lever, 10–25%).

## X6 — Lake Ontario local basin area (structural parameter)
**Q:** Roughly how large is the Lake Ontario basin area (km²) draining into the
lake besides the Niagara inflow?
**Reply (gist):** ~60,000–65,000 km² of direct local drainage (commonly cited
~64,000 km²), largest contributor the Trent River. Total basin including
upstream lakes is 700,000+ km², but the local direct-drainage area is the
~64,000 km² figure.
**Effect on work:** Defines the catchment area `A_basin ≈ 64,000 km²` over
which the net direct-basin gain (P - E + runoff) applies, distinct from the
lake surface area. The regression's implied area (~29,500 km²) is a
data-driven effective value between the lake surface (~19,000 km²) and the
full basin, reported honestly as the empirically-fitted area.

## X7 — Net precipitation minus evaporation (quantitative)
**Q:** On average, does Lake Ontario receive more water each year from rain
than it loses to evaporation? By about how many mm/year?
**Reply (gist):** Yes — a net water-surplus basin. Lake surface: precipitation
exceeds evaporation by ~100–200 mm/yr (lake precip ~800–900 mm/yr, lake evap
~600–750 mm/yr); with the land basin included the net surplus is larger.
Precipitation-dominated, net-positive, which is why inflows (not evaporation)
drive high-level periods.
**Effect on work:** Establishes the sign and magnitude of the unobserved
direct-catchment term R_t as net-positive (~100–200 mm/yr over the lake
surface). This is the physical reason the regression intercept `c` is negative
(the river data net out > in on average, so the basin gain must supply the
difference) and the reason wet years run high.

## X8 — Ice jams (edge case / failure mode)
**Q:** During ice jams in late winter on Lake Ontario and its rivers, which way
do water levels tend to move?
**Reply (gist):** Up, locally and abruptly — ice jams act as temporary dams
backing water upstream of the jam (sometimes a foot or more within hours);
downstream of the jam levels can fall. The whole-lake effect is smaller and
unpredictable: a jam on an outflow river (e.g. the St. Lawrence at
Moses-Saunders) can temporarily restrict outflow and nudge the lake up; a jam
on an inflow river can reduce inflow.
**Effect on work:** Defines the model's edge case: ice jams are a transient,
local, sign-ambiguous perturbation that the monthly-mean model cannot resolve.
The model's domain of validity excludes intra-month ice-jam spikes; late-winter
levels carry extra uncertainty. Reported as a limitation and sensitivity driver.

## X9 — Cornwall release band (quantitative, the control actuator)
**Q:** Over what range of outflow (m³/s) does the Cornwall dam actually vary
the St. Lawrence release in a normal year?
**Reply (gist):** ~6,000–9,000 m³/s is the normal operating band: held to
~6,000–7,000 m³/s in late winter/early spring (outflow held back to limit
downstream flooding/ice), raised to ~8,000–9,000 m³/s in summer/fall to draw
the lake down. Bounded by the regulation plan, not a fixed number; extremes
can exceed the band.
**Effect on work:** Sets the actuator limits `CORN_LOW = 6000`, `CORN_HIGH =
9000` m³/s and the seasonal shape of the control law (release low in
spring, high in fall). The 2017 backtest's mean release (8271 m³/s) sits
inside this band, confirming the control law respects the real dam authority.

## X10 — 2017 cause (validation / diagnostic)
**Q:** In 2017 Lake Ontario ran several months above normal. Main cause —
unusually heavy rain, or too much upstream inflow?
**Reply (gist):** Mainly heavy rain / wet basin conditions — 2017 was an
exceptionally wet year over the lake and its ~64,000 km² local basin, with a
very wet spring and high runoff. Upstream (Niagara) inflow was near or only
modestly above normal, not the dominant driver. The wet conditions filled the
lake faster than Cornwall could release, and outflow was also constrained by
downstream St. Lawrence flooding concerns.
**Effect on work:** Validation anchor for the 2017 backtest. The model
reproduces 2017 as a precipitation-driven high-water year (peak ~+2.3 ft in
May), and the backtest shows the dam release alone cannot restore the level in
such a year — matching the expert's diagnosis. This is the key management
finding: control is a mitigation tool, not a cure, for a wet-basin year.

---

### Parameter table (as used in the model)
| name | value | interval | source (exchange) |
|---|---|---|---|
| navigation floor | normal − 2 ft | [1,2] ft soft, [2,3] ft hard | X2 |
| flood ceiling | normal + 2 ft | [2,3] ft damage band | X3 |
| Cornwall release band | 6000–9000 m³/s | [6000,7000] spring, [8000,9000] fall | X9 |
| Ottawa freshet stored | ~15% of freshet | [10,25]% | X5 |
| local direct basin area | ~64,000 km² | [60000,65000] km² | X6 |
| net P−E on lake surface | +150 mm/yr | [100,200] mm/yr | X7 |
| implied effective area (fit) | 29,497 km² | — | data regression (model) |
| regression R² (in-sample) | 0.700 | — | data regression (model) |
| OOS level RMSE | 0.295 ft | bias 0.053 ft | data regression 2017-2022 |
