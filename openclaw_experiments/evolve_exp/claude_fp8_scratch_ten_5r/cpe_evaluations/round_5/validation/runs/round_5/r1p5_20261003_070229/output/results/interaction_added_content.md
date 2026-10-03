# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction evidence — 2018_C (four-state energy compact)

Ten expert exchanges. Each reply was converted into a model element before the next question was asked. Values and constraints that travel into the model are recorded here with the exchange that supplied them.

## Exchange 1 — profile criterion (structural)
- **Question:** When comparing how a state uses energy, which matters most — the share of each fuel in total consumption, or the amount each resident uses?
- **Reply (gist):** Fuel-share of total consumption is the primary criterion; per-capita use is secondary context. A state can be "clean" with high per-capita use if it is mostly renewable, or dirty with low per-capita use if it is mostly coal.
- **Turned into work:** Profile is defined as fuel-share of `TETCB` (primary) with per-capita energy as a reported context column, not a ranking input. Implemented in `model.py:build_profile` (`sh_*` columns) and used by `rank_best`.

## Exchange 2 — renewable scope (structural)
- **Question:** Which sources count as "cleaner, renewable energy": solar, wind, hydro, geothermal, biomass — or a narrower set?
- **Reply (gist):** All five (EIA standard). Include hydro (dominant historically) but report it separately from the "new" renewables (solar, wind, geothermal) because its growth potential is capped. Biomass is renewable; be transparent about the grouping. Nuclear is NOT renewable — exclude from the renewable share but mention as low-carbon context.
- **Turned into work:** `RENEW_SUB = {hydro, solar, wind, geothermal, biomass}`; renewable share = `RETCB` (= the five). `ren_new` = solar+wind+geothermal reported separately. `NUEGB` (nuclear) is reported as context and excluded from the renewable share. Implemented in `model.py` (`RENEW_SUB`, `GEN`, `sh_nuclear`).

## Exchange 3 — historical baseline (calibration)
- **Question:** In the 1960s–70s, was hydro already the main renewable before the oil shocks?
- **Reply (gist):** Yes — hydro was essentially the only significant renewable through the 1960s–80s; solar/wind negligible until the 1980s+; geothermal small and concentrated in CA.
- **Turned into work:** Used to interpret the 1960–2009 evolution (hydro-dominated early) and to justify holding hydro flat (capacity-capped) in the projection rather than extrapolating its 1989–2009 streamflow decline. Documented in the task II/III outcome analysis.

## Exchange 4 — expected leader (calibration)
- **Question:** Which of the four states would most likely be the biggest solar/wind adopter, and why?
- **Reply (gist):** Texas (largest land area, strong wind + solar resources, large demand, deregulated market), California a close second (policy + solar); AZ/NM have good solar but smaller demand/capital, so smaller absolute adoption but can have high shares.
- **Turned into work:** Consistency check on the projection: the model's 2050 result (TX rising to the highest renewable share, driven by its 2000s wind ramp) matches the expert's expectation. Recorded as a validation point in the outcome analysis.

## Exchange 5 — prediction mode (structural)
- **Question:** For 2025/2050 with no new policy, should growth continue as in past decades?
- **Reply (gist):** No — the 1960–2009 record has structural breaks (oil shocks, efficiency response, generation-mix shift, hydro-cap vs later solar/wind). Carry forward the *recent* trend (last ~10–20 years) per fuel, holding current policy/technology; treat 2050 as a scenario, not a forecast.
- **Turned into work:** Projection uses the recent window (15/20 y), not the 50-year CAGR. Fossil fuels and population use a robust recent rate (median year-on-year, bounded); new renewables use the 2000s ramp (2004–2009) endpoint growth. 2050 is labeled a scenario. Implemented in `model.py:project_profile` and `robust_rate`.

## Exchange 6 — 2050 target level (parameter)
- **Question:** How big should the 2050 renewable share be to be ambitious but achievable?
- **Reply (gist):** ~50–70% for a leading state, 30–50% for laggards, for *total energy* (hard, since transport/industrial are hardest). Electricity can reach 60–80%+. A compact goal in the 40–60% total-energy band, with higher electricity targets, is defensible.
- **Turned into work:** The 2050 compact goal is set in the 40–60% total-energy band (with an electricity-sector sub-target), explicitly above the no-policy baseline (≈7–31% renewable in 2050), which is what makes it a goal rather than a forecast. Recorded in Part II.A.

## Exchange 7 — policy actions (structural)
- **Question:** Which concrete steps would most help the governors reach a renewable target?
- **Reply (gist):** (1) a regional/coordinated renewable portfolio standard; (2) transmission and grid interconnection (the largest barrier — moving power from resource-rich rural areas to load); (3) shared financing/incentives; (4) demand-side efficiency; (5) coordinated siting/permitting. The compact's real advantage is coordination on transmission and standards.
- **Turned into work:** Part II.B lists three+ actions: (1) a binding four-state RPS with a shared metric, (2) joint transmission planning and cost-sharing across the compact, (3) pooled financing/procurement and coordinated permitting, with efficiency as a fourth.

## Exchange 8 — memo lead (content)
- **Question:** For the one-page memo, which single fact about the states' energy would you lead with?
- **Reply (gist):** That in 2009 all four states still drew the large majority of their energy from fossil fuels and renewables (dominated by hydro) were a small share — the starting point is low, the opportunity large; it is true of all four.
- **Turned into work:** Part III memo opens with that baseline fact (fossil majority, small renewable share in 2009), then predictions, then goals.

## Exchange 9 — validation (robustness)
- **Question:** If checking our work, which state would you look at first, and what would convince you the numbers were right?
- **Reply (gist):** California (largest, most documented system). Convincing checks: 2009 renewable shares in the right ballpark with hydro separated from solar/wind/geothermal; hydro roughly flat/capped (not growing); solar/wind near zero before the 1980s; per-capita/total magnitudes consistent (CA & TX much larger than AZ & NM); 2025/2050 projections continue recent trends, not the 50-year average.
- **Turned into work:** Used as the validation checklist. The model satisfies it: CA renewable share ~8.9% in 2009 (modest), hydro flat in the projection, solar/wind negligible before the 1980s in the data, CA/TX absolute magnitudes >> AZ/NM, projections use recent trends. Documented in the outcome analysis.

## Exchange 10 — memo secondary content (content)
- **Question:** Besides the renewable share, what one thing in the memo would the governors most want to see?
- **Reply (gist):** The cost and reliability implication of the target — what hitting the goal means for electricity prices and keeping the lights on; ideally that renewables are now cost-competitive and the main risk is transmission, not generation.
- **Turned into work:** Part III memo includes a plain cost/reliability statement: renewable generation is cost-competitive; the binding constraint is transmission/interconnection, which the compact addresses.

## Parameter table (empirical inputs and their provenance)
| name | value | interval | source |
|---|---|---|---|
| Renewable energy definition (5 sources) | solar+wind+hydro+geothermal+biomass | — | Exchange 2 (EIA standard) |
| Hydro treated as capacity-capped (flat in projection) | hold 2009 level | — | Exchange 2 + 3 |
| Projection recent window | last 15–20 y per fuel | — | Exchange 5 |
| 2050 total-energy renewable goal band | 40–60% | [40%, 60%] | Exchange 6 |
| 2050 electricity-sector renewable sub-target | 60–80% | [60%, 80%] | Exchange 6 |
| Renewable share cap (edge-case guard) | 85% | [85%, 100%] | model constraint (Exchange 6 context) |
| Fossil/population recent-rate clamp | ±1.5%/yr | [-1.5%, +1.5%] | model constraint (outlier guard) |
| All energy/population magnitudes | from `ProblemCData.xlsx` (EIA State Energy Data System, 1960–2009) | 1960–2009 | task dataset |
