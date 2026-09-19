# Modeling Blueprint Draft — MM-Bench 2020_A
## Scottish Herring & Mackerel Habitat Migration Under Ocean Warming

> **Document type:** Initial modeling plan / blueprint (design only).
> **Status:** Draft for planning. No data has been analyzed, no models have been fitted, no results have been computed.
> **Language note:** All statements below are future-oriented intentions ("will", "should", "is planned to"), not findings.

---

## 1. Problem Background and Restatement

Global ocean temperature change is expected to alter the geographic distribution of marine species. When ocean temperatures shift beyond a species' tolerance, populations are expected to relocate toward more suitable habitats. A documented analogue is the observed northward migration of the Maine (USA) lobster population toward cooler Canadian waters. Such shifts can disrupt onshore fishing economies that depend on the spatial stability of target stocks.

The client is a **Scottish North Atlantic fishery management consortium**. The two focal species are **Scottish herring** and **Scottish mackerel**, both economically important to the Scottish fishing industry. The key concern is that warming may move suitable habitat for these stocks away from present Scottish fishing grounds, making it economically impractical for **small Scottish fishing companies that operate vessels without on-board refrigeration** to continue harvesting and delivering fresh fish to Scottish ports.

**Restatement of the central question (planning framing):**
- Where will suitable habitat for Scottish herring and mackerel most plausibly be located over the next ~50 years under warming scenarios?
- Under different rates of ocean warming, what elapsed times (best case / worst case / most likely) would be required before the populations are too distant for small, non-refrigerated vessels operating from current Scottish ports?
- Should small companies change operations, and if so, which measures (fleet relocation, partial use of extended-endurance or refrigerated vessels, other options) would be practical and economically attractive?
- How would these strategies be affected if a portion of the stock moves into the territorial waters of another country?
- How should the technical findings be communicated to a fishing-industry readership (a short magazine-style article)?

**Note on the dataset:** the staged data directory is empty and the problem's dataset definition is empty (`dataset_path: []`). This blueprint therefore assumes that **all inputs will be acquired from public/external sources** (Section 4). No initial data files exist to inspect at planning time.

---

## 2. Objectives and Subproblems

### 2.1 Primary objective
Produce an integrated model that links (i) projected ocean-temperature change to (ii) habitat suitability shifts for Scottish herring and mackerel, and then to (iii) the operational and economic viability of small, non-refrigerated Scottish fishing companies, culminating in (iv) actionable strategic recommendations.

### 2.2 Subproblems (to be modeled as linked modules)

| ID | Subproblem | Intended deliverable |
|----|-----------|----------------------|
| SP1 | Construct a temperature/environment projection field for the North Atlantic / Scottish waters over the next 50 years under multiple scenarios/rates. | A spatially explicit temperature-change field (grid or region-based) for chosen scenario(s). |
| SP2 | Build a habitat-suitability model for herring and mackerel as a function of temperature and other environmental covariates. | Suitability maps and their temporal evolution for both species. |
| SP3 | Translate habitat shifts into catchability/accessibility from current Scottish ports. | Distance/accessibility-to-port trajectory over time for each species. |
| SP4 | Define the "too far / not viable" threshold for small, non-refrigerated vessels and derive elapsed-time estimates (best/worst/most-likely). | Distribution/variants of elapsed time to non-viability under rate scenarios. |
| SP5 | Assess whether operational change is warranted and model candidate strategies. | Comparative assessment of strategy options (relocation, partial refrigerated/extended-endurance fleet, other). |
| SP6 | Incorporate foreign-territorial-waters (EEZ / other national waters) effects into strategy assessment. | Adjusted feasibility/economics when stock crosses into another country's waters. |
| SP7 | Prepare the public-facing summary article. | Short magazine-style article draft grounded in the model narrative (not raw results). |

### 2.3 Deliverables (planned)
- A multi-module modeling framework (temperature → habitat → accessibility → economics → strategy).
- Scenario-based accessibility and elapsed-time analyses for both species.
- A strategy evaluation matrix for small companies.
- A territorial-waters sensitivity extension.
- A technical report structure plus a 1–2 page outreach article.
- Reproducible pipeline (code + configuration), with documented data sources and assumptions.

---

## 3. Assumptions

Assumptions are grouped by module. Each is listed with justification and a planned validation approach. All are provisional and will be revisited after data acquisition.

### 3.1 Environmental / climate assumptions
- **A1: A structured warming signal exists and can be represented by published scenarios.** Justification: warming projections are standard in climate literature; using established scenario families (e.g., representative concentration pathways, translated to sea-surface-temperature anomalies) avoids ad hoc trend invention. Validation: compare chosen scenario/rate against multiple published SST projection products; cross-check regional trends.
- **A2: Sea-surface temperature (SST) is the dominant environmental driver for these pelagic stocks.** Justification: herring and mackerel distributions correlate strongly with temperature and related water-mass properties. Validation: include additional covariates (salinity, chlorophyll/primary productivity, depth, currents) later and test whether SST-only models are adequate.
- **A3: Forecast horizon of ~50 years with the rate of warming treated as a scenario parameter.** Justification: the problem explicitly asks for a 50-year view and for best/worst/most-likely timing tied to *rate* of change. Validation: scenario sweep rather than single-point assumption.

### 3.2 Habitat / species assumptions
- **A4: Habitat suitability can be summarized by a bounded suitability index (0–1) driven mainly by temperature ranges.** Justification: provides a tractable, interpretable mapping from temperature to presence/likelihood. Validation: compare with independent occurrence/presence data and with published thermal niches.
- **A5: Both species shift toward cooler waters (generally poleward / deeper) as temperature rises, at a rate linked to the thermal field, not instantaneous.** Justification: consistent with observed poleward migration patterns; populations track suitable isotherms. Validation: test against historical distribution records over past decades.
- **A6: Population relocation is directional and gradual; no abrupt regime flips are modeled in the base case (early-warning extensions can relax this).** Justification: base-case tractability; abrupt behavior handled as a sensitivity case. Validation: sensitivity analysis with threshold-type responses.

### 3.3 Fleet / operational assumptions
- **A7: "Small fishing company" is characterized by vessels without on-board refrigeration and limited operational endurance.** Justification: this is stated in the problem as the defining constraint. Validation: parameterize a representative vessel profile and vary it in sensitivity analysis.
- **A8: Freshness/quality imposes a maximum time-to-port (or maximum distance at a given speed), which defines the viability threshold.** Justification: without refrigeration, catch quality degrades with time at sea; this yields a concrete "too far" criterion. Validation: cross-check the threshold against plausible vessel speed and trip-duration ranges; treat as a swept parameter.
- **A9: Current port locations remain fixed in the base case; relocation is a modeled decision variable, not a baseline.** Justification: separates the "do nothing" baseline from the strategy comparison. Validation: strategy model compares fixed-port operation against relocation scenarios.

### 3.4 Economic / regulatory assumptions
- **A10: Economic attractiveness can be represented by an aggregated cost–revenue proxy (e.g., distance/fuel/time costs vs. catch value) rather than a full market model.** Justification: sufficient for comparative strategy ranking without needing proprietary market data. Validation: sensitivity tests on cost and price parameters.
- **A11: Territorial-waters boundaries are treated as legal/geographic constraints with a policy-cost or restriction effect, not modeled as conflict dynamics.** Justification: keeps scope bounded while still addressing the problem's requirement. Validation: scenario-based analysis across boundary assumptions.

---

## 4. Data Processing Plan

Because the staged data directory is empty, the plan is acquisition-first.

### 4.1 Candidate data sources (to be acquired and vetted)
- **Sea-surface temperature / temperature projections:** public climate and ocean reanalysis/projection products (observational SST reanalysis for calibration; scenario-based SST projections for the 50-year horizon), including regional subsets for the North Atlantic / Scottish shelf seas.
- **Species occurrence/distribution:** public fisheries and biodiversity occurrence databases, stock assessment/landings summaries, and published distribution studies for herring and mackerel in the Northeast Atlantic.
- **Species thermal tolerance:** published literature values on preferred/suitable temperature ranges for both species.
- **Geospatial context:** coastline, port locations (Scottish fishing ports), bathymetry, EEZ/territorial-water boundaries.
- **Vessel/operational parameters:** representative small-vessel speed, endurance, and cost parameters (from public/industry sources or documented assumptions).
- **Economic parameters:** catch value proxies and fuel/operating cost proxies (public or literature-based).

### 4.2 Preprocessing (planned)
- Standardize coordinate systems and grid resolutions across temperature, habitat, and geospatial layers.
- Temporal alignment: reconcile observation periods, projection horizons, and reporting resolutions.
- Spatial cropping to the relevant domain (Scottish waters plus adjacent Northeast Atlantic / migration corridor), with buffer zones.
- Handle missing data via documented interpolation/aggregation rules; flag coverage gaps.
- Convert units to consistent conventions (temperature, distance, speed, time).
- Provenance logging: every acquired layer recorded with source, version, retrieval date, and license.

### 4.3 Feature construction (planned)
- Temperature-derived features: seasonal mean/summary statistics, decadal anomalies, and rate-of-change fields.
- Habitat features: suitability-index inputs and derived persistence/stability measures over time.
- Accessibility features: distance from port(s) to suitable-habitat centroid(s)/regions; travel-time proxies from vessel speed.
- Temporal features: year/decade indices to support 50-year trajectory construction.
- Indicator features for territorial-water crossing (share of suitable habitat inside vs. outside domestic waters).

### 4.4 Data usage strategy
- **Calibration/validation split:** historical period used to build/tune habitat relationships; separated holdout period for validation.
- **Scenario design:** multiple warming-rate scenarios used as parallel inputs (best/worst/most-likely framing).
- **Reproducibility:** all raw and processed layers stored with a manifest; acquisition steps scripted so the pipeline can be re-run.
- **Fallback:** if a source is unavailable, a documented literature-based alternative or a stated-assumption substitute will be used.

---

## 5. Candidate Model Framework

A layered, coupled framework is proposed. Each layer is independently validatable and connected by explicit interfaces.

### 5.1 Layer 1 — Temperature / environment projection (SP1)
- **Candidate approaches:** (a) use published scenario SST fields as exogenous inputs; (b) fit a spatial trend model to historical SST and extrapolate under rate parameters; (c) region-based aggregation for robustness.
- **Variables:** SST (scenario, location, season, year), warming-rate parameter, spatial coordinates.
- **Advantages:** grounded in established climate data; interpretable.
- **Limitations:** projection uncertainty; coarse resolution; scenario dependence.

### 5.2 Layer 2 — Habitat suitability model (SP2)
- **Candidate approaches:** (a) thermal-niche/suitability-index model (bounded response to temperature); (b) statistical distribution model (e.g., generalized additive/linear or MaxEnt-style presence model) using temperature plus covariates; (c) hybrid niche–statistical blending.
- **Variables:** temperature (and covariates), species-specific thermal parameters, suitability index (0–1).
- **Advantages:** interpretable, data-efficient, directly mappable.
- **Limitations:** sensitivity to occurrence-data bias; niche-shift assumption (species' tolerance held constant vs. adaptability).

### 5.3 Layer 3 — Spatial population shift / habitat movement (SP1+SP2 → SP3)
- **Candidate approaches:** (a) isotherm-tracking (suitable habitat shifts with temperature contour movement); (b) gravity/centroid-shift model of habitat centroid over time; (c) agent/cellular movement proxy for population redistribution.
- **Variables:** habitat centroid, migration rate, direction, habitat area, spatial overlap with current grounds.
- **Advantages:** converts suitability fields into human-interpretable "where the fish go" trajectories.
- **Limitations:** simplifying assumptions about movement speed vs. environmental change; possible lag effects.

### 5.4 Layer 4 — Accessibility and viability timing (SP3 → SP4)
- **Candidate approaches:** (a) distance/travel-time threshold model from port to habitat; (b) catchability decay function (accessibility diminishing with distance); (c) survival/quality-decay model for non-refrigerated catch constraining trip range.
- **Variables:** distance-to-habitat, vessel speed/endurance, time-to-port threshold, accessibility index, first-crossing year of viability threshold.
- **Advantages:** yields concrete best/worst/most-likely elapsed times via scenario sweeps.
- **Limitations:** threshold definition sensitivity; dependence on representative vessel profile.

### 5.5 Layer 5 — Economic strategy model (SP5)
- **Candidate approaches:** (a) comparative cost–revenue framework across strategy options; (b) multi-criteria decision analysis (weighted criteria: cost, freshness/quality, risk, feasibility); (c) scenario-based break-even analysis for relocation/investment decisions.
- **Strategy options to model:** partial/complete asset relocation to ports closer to projected habitat; deploying a proportion of vessels with on-board refrigeration / extended endurance (operating without land-based support for a period); improved trip planning; mixed-fleet portfolios; cooperative/shared logistics (additional options to be proposed).
- **Variables:** investment cost, operating cost, revenue/catch value, freshness quality indicator, strategy mix fraction(s), decision horizon.
- **Advantages:** directly answers problem part 3 with comparable, auditable options.
- **Limitations:** proxy economics; parameter uncertainty handled by sensitivity analysis.

### 5.6 Layer 6 — Territorial-waters extension (SP6)
- **Candidate approaches:** (a) overlay of projected suitable habitat with EEZ/territorial boundaries to compute foreign-water exposure over time; (b) access-constraint adjustment to the economic model (access fees, quota/legal restrictions, permit costs); (c) worst-case exclusion scenario.
- **Variables:** share of suitable habitat in foreign waters (by year), access-cost/restriction parameter, feasibility flag.
- **Advantages:** addresses problem part 4 within the same framework.
- **Limitations:** geopolitical/policy uncertainty; treated as scenarios, not predictions.

### 5.7 Layer 7 — Communication layer (SP7)
- A narrative framework that will translate model outputs into a magazine-style article: the problem, why it matters, what the model suggests will happen, and the recommended practical options.

### 5.8 Cross-cutting math ideas
- Bounded monotone response functions for suitability.
- Spatial interpolation / gridded fields and contour (isotherm) tracking.
- Threshold/first-crossing analysis for timing questions.
- Scenario sweeps and Monte-Carlo-style uncertainty propagation (planned, not executed here).
- Multi-criteria decision weighting for strategy ranking.

---

## 6. Implementation Roadmap

### 6.1 Planned workflow (staged)
1. **Stage 0 — Data acquisition & vetting:** collect and document all external layers; record provenance; verify coverage of the Scottish / North Atlantic domain.
2. **Stage 1 — Preprocessing:** harmonize grids, units, time axes; build the spatial domain and port/boundary layers.
3. **Stage 2 — Environment layer:** assemble temperature fields under baseline and warming scenarios/rates.
4. **Stage 3 — Habitat layer:** build suitability models for herring and mackerel; validate against historical distribution.
5. **Stage 4 — Shift layer:** project habitat centroids/areas over the 50-year horizon under each scenario.
6. **Stage 5 — Accessibility layer:** compute distance/travel-time-to-habitat trajectories; derive viability-threshold crossing times.
7. **Stage 6 — Economic/strategy layer:** evaluate strategy options and produce comparison matrix.
8. **Stage 7 — Territorial-waters extension:** overlay boundaries and re-evaluate feasibility.
9. **Stage 8 — Sensitivity & uncertainty:** sweep key parameters and scenarios.
10. **Stage 9 — Reporting:** assemble technical report and the outreach article.

### 6.2 Required modules (planned code structure)
- `data_acquisition/` — sourced fetchers/downloaders with provenance manifests.
- `preprocessing/` — grid/unit/time harmonization, geospatial utilities.
- `environment/` — temperature field construction and scenario handling.
- `habitat/` — suitability model builders and evaluators.
- `shift/` — centroid/isotherm movement and habitat trajectory tools.
- `accessibility/` — distance/travel-time and threshold-crossing analysis.
- `economics/` — cost–revenue and multi-criteria strategy comparison.
- `territorial/` — boundary overlay and access-constraint adjustments.
- `sensitivity/` — scenario sweeps and uncertainty propagation.
- `reporting/` — figures/tables generation and narrative assembly.
- `config/` — scenario, vessel, and economic parameter definitions.
- `tests/` — unit and integration checks for each module interface.

### 6.3 Tooling intent (not executed here)
- Geospatial and scientific computing stack for gridded fields and statistical modeling; a reproducible scripting environment; version-controlled configuration so scenarios can be re-run deterministically.

### 6.4 Milestones (planning-level)
- M1: Data sources finalized and downloaded.
- M2: Preprocessing complete and validated.
- M3: Temperature field and habitat models validated on historical data.
- M4: Projection trajectories and timing estimates available.
- M5: Strategy matrix and territorial extension complete.
- M6: Report and article drafted.

---

## 7. Validation Strategy

### 7.1 Evaluation metrics (planned)
- **Habitat model:** discrimination/calibration metrics against held-out occurrence data (e.g., AUC-type or skill-score measures), plus qualitative agreement with published distribution maps.
- **Environmental layer:** consistency of chosen scenarios with published regional trends; stability of conclusions across scenarios.
- **Accessibility/timing:** robustness of threshold-crossing years to parameter variation (report as ranges, not point values).
- **Economic/strategy model:** rank stability of strategy options under cost/price perturbations; break-even consistency.
- **Territorial extension:** sensitivity of feasibility conclusions to boundary and access-cost assumptions.

### 7.2 Validation methods (planned)
- **Temporal holdout:** calibrate on earlier periods, validate on later held-out periods.
- **Spatial holdout:** test habitat predictions in held-out subregions.
- **Cross-source consistency:** compare outputs across independent data products where available.
- **Scenario triangulation:** confirm that qualitative conclusions hold across multiple warming scenarios and rates.
- **Expert/qualitative plausibility checks:** compare against documented ecological expectations.

### 7.3 Sensitivity analysis (planned)
- Cruise key parameters: warming rate, thermal-tolerance bounds, vessel speed/endurance, time-to-port threshold, cost/price proxies, strategy mix fractions, and territorial-access assumptions.
- One-at-a-time sweeps plus multi-parameter/Monte-Carlo-style propagation to produce best/worst/most-likely bands.
- Report which assumptions most strongly influence conclusions (identify dominant uncertainties).

---

## 8. Expected Result Interpretation

This section describes how outputs *will* be read once produced — not what they are.

- **Habitat maps over time** will be interpreted as probabilistic suitability surfaces, with the centroid trajectory indicating the direction and pace of population shift.
- **Elapsed-time estimates** will be reported as best-case / worst-case / most-likely bands tied to specific warming-rate scenarios, with the spread reflecting model and parameter uncertainty.
- **Strategy comparisons** will be interpreted as relative rankings under stated assumptions; a strategy is "economically attractive" only if it maintains viability (freshness/quality and cost) across the majority of plausible scenarios.
- **Territorial-waters results** will be interpreted as a feasibility modifier: if projected habitat increasingly falls inside another country's waters, strategies dependent on that habitat will carry added access/legal risk, possibly favoring alternative ports or fleet configurations.
- **Desk and outreach outputs** will translate the above into practical guidance: whether to change operations, and which mix of measures is most robust.

**Interpretation guardrails:**
- No conclusion will be treated as definitive; all timing and economic statements will be conditional on the stated assumptions and scenarios.
- Uncertainty bands, not single numbers, will accompany timing claims.
- The "too far" concept will be tied explicitly to the defined time-to-port/quality threshold.

---

## 9. Limitations and Improvements

### 9.1 Anticipated limitations
- **Model simplification:** SST-only or few-covariate habitat models may miss ecological complexity (prey, predation, fishing pressure, recruitment).
- **Data gaps:** reliance on external/public sources; coverage, resolution, and licensing constraints; no staged dataset was provided.
- **Scenario dependence:** results inherit the uncertainty of the chosen climate scenarios.
- **Niche-stationarity assumption:** species' thermal tolerances are treated as fixed; adaptation/evolution is not modeled in the base case.
- **Economic proxies:** aggregate cost–revenue and multi-criteria models approximate real industry economics.
- **Territorial/policy dynamics** are represented as static scenarios rather than evolving negotiations.
- **Behavioral/lag effects:** population movement modeled smoothly; real ecosystems may exhibit thresholds and lags.

### 9.2 Planned improvements
- Add multi-covariate habitat modeling and test incremental skill.
- Incorporate fishing-pressure and biomass dynamics to avoid conflating habitat shift with stock decline.
- Move from deterministic scenarios to fuller probabilistic uncertainty propagation.
- Introduce lag/threshold movement models and adaptive-niche variants.
- Refine economics with richer cost structures and vessel-level trip simulation.
- Extend territorial analysis with dynamic policy/access scenarios.
- Strengthen external validation with additional independent datasets and expert review.

---

## Appendix A — Assumption → Validation Traceability (planned)

| Assumption | Planned validation |
|-----------|--------------------|
| A1 Warming signal representable | Compare across published scenario products |
| A2 SST dominant driver | Add covariates; test incremental skill |
| A3 50-yr horizon, rate as parameter | Scenario sweep |
| A4 Bounded suitability index | Compare with occurrence data + literature niches |
| A5 Gradual poleward shift | Test against historical distributions |
| A6 No abrupt flips (base case) | Threshold sensitivity test |
| A7 Small = no refrigeration, limited endurance | Representative vessel profile + sweeps |
| A8 Max time-to-port threshold | Vessel speed/trip-duration plausibility + sweep |
| A9 Ports fixed in baseline | Baseline vs. relocation comparison |
| A10 Aggregate economic proxy | Cost/price sensitivity |
| A11 Territorial waters as constraint | Boundary/access-cost scenarios |

---

## Appendix B — Deliverable Checklist (planned)
- [ ] Multi-module model framework (temperature → habitat → accessibility → economics → strategy)
- [ ] Scenario-based habitat trajectories for herring and mackerel
- [ ] Best/worst/most-likely timing estimates (as ranges)
- [ ] Strategy comparison matrix
- [ ] Territorial-waters extension analysis
- [ ] Technical report structure
- [ ] 1–2 page outreach article draft
- [ ] Reproducible pipeline with documented data provenance

---

*End of blueprint draft. Planning only — no solving, data analysis, computation, or results are included by design.*
