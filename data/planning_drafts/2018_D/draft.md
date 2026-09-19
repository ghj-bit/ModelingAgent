# MM-Bench 2018_D — Modeling Plan Draft (Blueprint)

**Problem ID:** `2018_D`
**Title:** MM-Bench 2018_D
**Source:** MM-Bench 2018
**Document type:** Initial modeling plan draft (roadmap only — no solving, no data analysis, no results)

> This document is a *planning blueprint*. It specifies how a future modeling effort
> could be organized. It deliberately contains **no computed numbers, no fitted
> models, no executed experiments, and no final conclusions**. All quantities are
> referenced as *to be determined* in later phases.

---

## 1. Problem Background and Restatement

### 1.1 Context (as given)

Nations are moving to replace gasoline/diesel personal vehicles with all-electric
vehicles (EVs). A prerequisite for a full switch is a sufficient charging network,
located in the right places, sized for daily use and occasional long-distance trips.
The transition cannot happen instantly: resources are limited, adoption is gradual,
and the location/convenience of charging stations strongly influences adoption.

Planners must therefore reason about:

- the **final (steady-state) architecture** of the charging network —
  number of stations, their locations, chargers per station, and the differing
  needs of **urban, suburban, and rural** areas;
- the **growth/evolution path** of that network over time, tied to EV adoption
  milestones (~10%, 30%, 50%, 90%, and eventually 100% of the car fleet).

Scope restriction: **personal passenger vehicles only** (cars, vans, light
passenger trucks). Commercial/heavy vehicles (heavy trucks, buses) are out of
scope except for a brief commentary in the final deliverable.

### 1.2 Restated task structure

- **Task 1 — US / Tesla case study.** Examine the current and growing Tesla
  charging network (destination charging, supercharging, plus home charging).
  Assess whether Tesla is "on track" for a complete US switch. Estimate how many
  charging stations would be needed under full EV adoption and how they should be
  distributed across urban, suburban, and rural areas.
- **Task 2 — Single-nation design** (choose one of South Korea, Ireland, Uruguay):
  - **2a** Optimal number, placement, and distribution under *instantaneous* full
    migration (no transition time), plus the key shaping factors.
  - **2b** A clean-slate *evolution* proposal from zero chargers to full EV
    system: investment sequencing (city-first vs. rural-first vs. mixed),
    supply-push (chargers before cars) vs. demand-pull (chargers in response to
    purchases), and shaping factors.
  - **2c** A proposed *timeline* to full EV adoption, anchored on
    ~10%/30%/50%/100% milestones, plus shaping factors.
- **Task 3 — Cross-country generalization.** Test whether the Task-2 plan
  transfers to very different geographies/densities/wealth (Australia, China,
  Indonesia, Saudi Arabia, Singapore); identify the factors that trigger different
  growth models; discuss feasibility of a **classification system** for matching
  nations to a growth model.
- **Task 4 — Technology foreshocks.** Discuss how car-share/ride-share,
  self-driving cars, battery-swap stations, flying cars, and Hyperloop could
  alter the analyses.
- **Task 5 — One-page policy handout** for heads of state at an international
  energy summit: key factors plus a suggested gas-vehicle-ban date.

### 1.3 Deliverable types implied

A written technical report (Tasks 1–4) plus a standalone one-page handout
(Task 5), both grounded in the models and data assembled in Phases 1–5 below.

---

## 2. Objectives and Subproblems

### 2.1 Overarching objective

Build a **defensible, parameterized framework** that, for a given country, can:
(i) estimate the *steady-state* charging network required for full EV adoption,
(ii) prescribe an *investment and sequencing policy* to evolve from zero to that
network, and (iii) project a *plausible adoption timeline* and ban date — while
exposing sensitivity to geography, density, wealth, and technology change.

### 2.2 Subproblem decomposition (mapping to Tasks)

| ID  | Subproblem | Maps to | Nature |
|-----|-----------|---------|--------|
| SP0 | Demand characterization: daily driving demand, trip-length distribution, at-home charging access | All | Statistical / empirical |
| SP1 | Steady-state network sizing & spatial allocation (US; urban/suburban/rural) | Task 1 | Optimization + spatial allocation |
| SP2 | Steady-state optimal siting/count for the selected nation | Task 2a | Facility location optimization |
| SP3 | Network evolution from zero: sequencing, supply-push vs. demand-pull | Task 2b | Dynamic/sequential decision model |
| SP4 | Adoption timeline to 10/30/50/100% EV | Task 2c | Diffusion / system-dynamics model |
| SP5 | Cross-country transferability & classification system | Task 3 | Comparative framework / taxonomy |
| SP6 | Technology-foreshock scenario analysis | Task 4 | Sensitivity / scenario modeling |
| SP7 | Policy synthesis and handout | Task 5 | Synthesis (non-numeric) |

### 2.3 Key questions each subproblem must eventually answer (specification)

- SP0: What is the expected charging demand (kWh/day, sessions/day) as a function
  of region type and fleet size? What fraction can be satisfied at home?
- SP1/SP2: What station count and spatial allocation minimizes a defined
  total-cost objective (build + operate + user travel/inconvenience) subject to
  coverage and wait-time constraints?
- SP3: Given a budget stream, what is the optimal sequencing rule, and under what
  conditions is supply-push vs. demand-pull preferred?
- SP4: What functional form best describes adoption, and what levers (charger
  availability, price parity, policy) drive the transition dates?
- SP5: Which continuous indices (density, area, wealth, grid readiness, driving
  patterns) explain the choice of growth model?
- SP6: How do demand-suppression/relocation effects (shared, autonomous,
  swap, aerial) shift network requirements?
- SP7: Which handful of factors is decision-critical for a national leader?

### 2.4 Explicit non-goals for this draft

No solving, no data ingestion, no model fitting, no numeric answers, no map
production, no code execution. Those belong to subsequent phases.

---

## 3. Assumptions

Each assumption is labeled **[N]** necessary, **[W]** working/simplifying, or
**[V]** validation-target, with a stated justification and a future validation path.

### 3.1 Scope & fleet assumptions

1. **[N] Personal passenger vehicles only.** Justification: problem scoping to
   cars, vans, light passenger trucks. *Validation:* check that any fleet figure
   used excludes heavy trucks/buses; align with the final brief commentary.
2. **[W] Fleet size is treated as approximately fixed** over the planning horizon
   (replacement rather than net growth). Justification: isolates the
   electrification problem from unrelated demographic growth. *Validation:*
   compare against population/vehicle-ownership trend series; test relaxation.
3. **[V] Home-charging availability is heterogeneous.** Owners with garages/
   driveways (mostly suburban/rural, detached housing) can charge overnight;
   many urban dwellers cannot. Justification: stated in the problem statement.
   *Validation:* anchor the urban/suburban/rural home-access split to housing-type
   data during Phase 2.

### 3.2 Behavioral & demand assumptions

4. **[W] Charging demand scales with vehicle-km traveled** and is separable into
   (a) routine local energy needs and (b) occasional long-distance trips.
   Justification: matches the destination-vs-supercharging design distinction.
   *Validation:* compare modeled trip-length distribution against national travel
   surveys.
5. **[W] Range anxiety is a coverage constraint, not just a cost term.**
   Justification: convenience/location is emphasized as a key adoption driver.
   *Validation:* test both "average-service" and "worst-case-corridor" coverage
   constraints in sensitivity analysis.
6. **[V] Adoption is influenced by charger availability (two-way coupling).**
   Justification: the task explicitly asks whether to build chargers first or in
   response to purchases. *Validation:* treat coupling strength as a tunable
   parameter in SP3/SP4 and sweep it.

### 3.3 Technology & cost assumptions

7. **[W] Charging technology mix** = Level-2 destination/home + DC fast
   (supercharger-class, ~30 min for ~170 mi). Justification: matches the Tesla
   product split named in the problem. *Validation:* re-parameterize with current
   charger power/economics in Phase 2.
8. **[W] Station build cost, per-charger cost, and grid-upgrade cost are
   region-dependent** (urban land premium, rural grid extension). Justification:
   geography materially affects both cost and need. *Validation:* benchmark
   against published infrastructure-cost ranges.
9. **[W] Reasonable utilization/wait-time service standard** is imposed
   (e.g., a target queue/wait bound and a minimum coverage radius — numeric
   values to be set in Phase 2). Justification: needed to make "how many
   stations" well-posed. *Validation:* sensitivity sweep across service
   standards.

### 3.4 Modeling-form assumptions

10. **[W] Spatial demand can be aggregated into regions/zones** (e.g., census-
    tract, city, corridor) rather than modeled continuously. Justification:
    tractability without losing urban/suburban/rural structure. *Validation:*
    refine granularity for the selected nation in Phase 3.
11. **[W] Country-level parameters (density, wealth, area) can be compressed into
    a few **continuous indices** that predict the suitable growth model
    (feeds SP5). Justification: the task asks for a classification system.
    *Validation:* test the index's discriminative power on the six named countries
    using scenario analysis, not on fitted outcomes.

### 3.5 Recording convention

Every assumption will be logged in an **assumption register** (ID, statement,
type, justification, validation method, status) so that Phase 4 sensitivity runs
can trace which results depend on which assumption.

---

## 4. Data Processing Plan

> No data is present in the staged `data/` directory (`dataset_path: []`).
> The plan below therefore specifies what would be gathered/derived in Phase 2,
> how external sources would be used, and how any provided files would be
> processed if/when staged.

### 4.1 Data inventory (planned)

| Group | Needed quantities (illustrative) | Purpose | Typical source class |
|-------|----------------------------------|---------|----------------------|
| Fleet & adoption | vehicle counts, EV share history, sales mix | SP0, SP4 | national vehicle registries / transport statistics |
| Driving behavior | annual VMT, trip-length & trip-purpose distributions | SP0 | national household travel surveys |
| Geography | area, population, density, urban/suburban/rural delineation | SP1–SP3, SP5 | census/administrative geographies |
| Charging network | existing station counts, locations, chargers per station, power | SP1, SP3 baseline | operator/registry charger databases |
| Economics | electricity prices, charger capex/opex, land costs, vehicle prices | SP1–SP4 | energy agencies / industry reports |
| Grid & housing | grid capacity/readiness, housing type (garage/driveway share) | SP0, SP3 | utility & housing statistics |
| Wealth & policy | GDP per capita, subsidies, ban announcements | SP4, SP5 | national statistics / policy trackers |
| Cross-country panel | same fields for AU, CN, ID, SA, SG | SP5 | comparable international datasets |

### 4.2 Preprocessing plan

1. **Schema harmonization.** Standardize country/region identifiers, units
   (kWh, km vs. mi, currency, year), and geographic codes across sources.
2. **Spatial join.** Attach every demand/vehicle/station record to a common zone
   layer (tract → city → metro → region) so urban/suburban/rural classes are
   consistently defined per country.
3. **Temporal alignment.** Resample all series to a common annual grid; define a
   reference year; document interpolation rules for gaps.
4. **Outlier & missingness handling.** Flag implausible values; choose
   imputation or exclusion per field; retain flags so downstream models can
   exclude low-confidence zones.
5. **Unit & scope filters.** Enforce the passenger-vehicle restriction
   (exclude heavy/commercial categories); convert VMT to the modeled unit.
6. **Provenance log.** Record source, retrieval date, license, version, and any
   transformation for each field (reproducibility).

### 4.3 Feature construction (derived variables)

- **Demand intensity:** energy demand per zone = f(vehicles, VMT, efficiency),
  split into local vs. long-trip components.
- **Home-chargeable share:** fraction of vehicles in a zone with off-street
  overnight charging access (from housing-type mix).
- **Public-charge demand:** local demand minus home-chargeable share, plus
  en-route demand allocated to corridors.
- **Corridor/route abstraction:** origin–destination or major-highway graph for
  long-distance coverage.
- **Cost surfaces:** per-zone station and per-charger cost multipliers.
- **Country indices:** density index, dispersion/area index, wealth index,
  grid-readiness proxy — the candidate drivers for the classification system.
- **Adoption-driver features:** charger-per-EV ratio, price-parity proxy,
  policy-stringency proxy.

### 4.4 Data usage strategy

- **Calibration vs. validation split.** Use historical time slices to calibrate
  behavioral parameters (Phase 3) and hold out later slices to validate
  projections (Phase 5). Exact split boundaries to be fixed once provenance and
  coverage are known.
- **Scenario datasets.** Construct coherent "country scenarios" (fleet, density,
  wealth bundles) for SP5/SP6 rather than extrapolating one country's data.
- **Data-quality tiers.** Rank zones/fields by reliability; run the analysis once
  on the full set and once on the high-confidence subset to gauge fragility.
- **No fabrication rule.** Any gap that cannot be sourced will be handled by an
  explicit, logged assumption — never by silent invention.

---

## 5. Candidate Model Framework

The framework is a **layered pipeline**: demand model → steady-state network
optimization → dynamic deployment → adoption dynamics → comparative taxonomy →
scenario overlays. Candidate methods are listed with advantages/limitations so
the modeler can select.

### 5.1 Layer A — Charging demand model (SP0)

- **Candidate methods:**
  - (A1) Stochastic trip-generation model: distributions of trips/day and
    trip length per zone, converted to energy demand.
  - (A2) Aggregate intensity model: demand = vehicles × VMT × energy/km,
    partitioned by home/public/route.
  - (A3) Agent/activity-based simulation (heavier); reserve for a focused
    case-study region if resources allow.
- **Variables:** vehicles by zone, VMT distribution, efficiency, home-access
  share, public-demand share, corridor demand.
- **Mathematical ideas:** probability distributions over trip length; convolution
  of session energy; peak/off-peak load separation.
- **Advantages/limits:** A2 is transparent and data-light but coarse; A1 captures
  variability but needs travel-survey data; A3 is realistic but costly.

### 5.2 Layer B — Steady-state network optimization (SP1, SP2a)

- **Candidate methods:**
  - (B1) **Facility-location / p-median / capacitated covering** formulations:
    choose station set minimizing build+operate+user-access cost subject to
    coverage and queue constraints.
  - (B2) **Multi-objective optimization** (cost vs. coverage vs. equity) via
    weighted sum, ε-constraint, or Pareto front exploration.
  - (B3) **Queueing sizing layer** (e.g., M/M/c or Erlang-type approximation)
    to translate charger demand into chargers-per-station subject to a wait-time
    target.
  - (B4) **Hierarchical/tiered design:** mandatory coverage backbone (e.g.,
    corridor spacing) + demand-driven urban fill.
- **Variables:** station locations (zone or candidate-site selection), number of
  chargers per station, station type (destination vs. fast), coverage radius,
  served demand allocation, queue metrics.
- **Mathematical ideas:** mixed-integer programming; set-cover duality; gravity/
  Huff-type demand allocation; queueing approximations; Pareto dominance.
- **Advantages/limits:** MIP is exact but may scale poorly on fine grids;
  queueing gives service realism but needs arrival-rate assumptions; hierarchical
  design is interpretable but presupposes a spacing rule.

### 5.3 Layer C — Deployment-path / sequencing model (SP2b)

- **Candidate methods:**
  - (C1) **Multi-period network design** (dynamic facility location): decide what
    to build each period under budget, minimizing cumulative regret/cost.
  - (C2) **Supply-push vs. demand-pull policy model:** exogenous charger-led
    build schedule vs. adoption-reactive (threshold) build rule; compare outcomes.
  - (C3) **Coverage-first vs. demand-first heuristics:** city-priority,
    rural-connectivity-priority, and mixed strategies, evaluated on coverage,
    utilization, equity, and cost trajectories.
  - (C4) **Option-value framing:** when early investment reduces later adoption
    friction (real-options flavor) — qualitative or small parametric.
- **Variables:** build schedule by zone/period, budget stream, coverage level,
  utilization, adoption feedback.
- **Mathematical ideas:** dynamic programming / multi-period MIP; greedy coverage
  heuristics; threshold/feedback rules; regret minimization.
- **Advantages/limits:** dynamic MIP is rigorous but data-hungry; heuristics are
  explainable and robust but not provably optimal.

### 5.4 Layer D — Adoption-timeline model (SP2c, feeds SP4)

- **Candidate methods:**
  - (D1) **Diffusion models:** logistic/Bass-style adoption curves driven by
    price parity, charger density, and policy — used to date the
    10/30/50/100% milestones.
  - (D2) **System-dynamics model:** stocks/flows of vehicles, chargers, grid
    capacity, with feedback loops (chargers → adoption → charger demand).
  - (D3) **Discrete-choice / transition model:** probability a household/zone
    switches as function of attributes; aggregates to fleet adoption.
  - (D4) **Scenario/timeline synthesis:** combine D1–D3 outputs into a banded
    timeline with a proposed ban date and confidence ranges.
- **Variables:** adoption fraction over time, charger-per-EV ratio, price gap,
  policy intensity, feedback strength.
- **Mathematical ideas:** ODE diffusion; coupled ODE systems; logit/proportional-
  hazard transitions; Monte-Carlo uncertainty propagation.
- **Advantages/limits:** diffusion is simple/interpretable but can overfit
  history; system-dynamics captures feedback but has many loosely-known
  parameters; choice models are micro-grounded but data-demanding.

### 5.5 Layer E — Comparative taxonomy / classification system (SP5)

- **Candidate methods:**
  - (E1) **Index-based decision rules:** map countries into a 2-D/3-D space
    (density × dispersion/area × wealth, plus grid readiness) and define regions
    that prescribe a growth model.
  - (E2) **Decision-tree / rule-based classifier** over the country indices with
    human-interpretable splits.
  - (E3) **Clustering** of the country panel into archetypes (with the caveat
    that the panel is small; rely on interpretability over fit).
- **Variables:** density index, dispersion/area index, wealth index, grid-readiness
  proxy, driving-pattern index, policy intensity.
- **Mathematical ideas:** normalization & weighting scheme; interpretable
  partitions; archetype centroids.
- **Advantages/limits:** E1 is transparent and policy-usable; E2/E3 risk
  overfitting on a handful of countries — use as illustration, validate by
  out-of-sample reasoning, and keep the taxonomy diagnostic rather than
  prescriptive.

### 5.6 Layer F — Technology-foreshock overlays (SP6)

- **Candidate methods:**
  - (F1) **Demand-shift multipliers:** car-share/ride-share reduce private fleet &
    home charging need; adjust Layer A demand.
  - (F2) **Autonomous-vehicle scenarios:** self-charging/fleet repositioning
    changes station location and timing needs.
  - (F3) **Battery-swap vs. plug-in network substitution:** swap stations as an
    alternative to (or complement of) fast charging.
  - (F4) **Aerial/Hyperloop long-distance substitution:** compress en-route fast-
    charging demand on specific corridors.
- **Variables:** fleet-reduction factor, charging-behavior shift, corridor demand
  reallocation, swap-station coverage.
- **Mathematical ideas:** scenario multipliers on Layer-A/B outputs; re-solved
  network optimization under shifted demand; corridor demand subtraction.
- **Advantages/limits:** scenario overlays are cheap and policy-relevant but are
  not forecasts — must be presented as conditional envelopes.

### 5.7 Layer G — Policy synthesis (SP7, Task 5)

- **Method:** structured extraction of the *most sensitive, most actionable*
  factors from Layers A–F into a compact, non-technical factor list plus a
  proposed ban-date recommendation with rationale. No new model; a synthesis
  step with explicit traceability back to the layers.

### 5.8 Framework integration view

```
Data (Phase 2)
   → A Demand model
   → B Steady-state network optimization (Tasks 1, 2a)
   → C Deployment path (Task 2b)  ──┐
   → D Adoption timeline (Task 2c) ─┤ feedback (B↔C↔D)
   → E Comparative taxonomy (Task 3)
   → F Technology overlays (Task 4)
   → G Policy synthesis / handout (Task 5)
   → Validation & sensitivity (Phase 5)
```

### 5.9 Modeling-idea shortlist (cross-cutting)

- Mixed-integer facility location with coverage + service-level constraints.
- Queueing-based charger sizing.
- Multi-period dynamic network design for deployment sequencing.
- Coupled diffusion/system-dynamics for adoption with charger feedback.
- Index/rule-based cross-country taxonomy.
- Scenario multipliers and Monte-Carlo sensitivity for technology and parameter
  uncertainty.

---

## 6. Implementation Roadmap

> Roadmap only. No code is written, run, or executed in this draft.

### 6.1 Phase structure

- **Phase 1 — Problem framing (this document).** Objectives, subproblems,
  assumptions, framework. *Output:* this blueprint.
- **Phase 2 — Data assembly & preprocessing.** Acquire sources per §4.1,
  harmonize schemas, build zones/corridors, construct derived features,
  produce a data dictionary and provenance log. *Output:* analysis-ready
  zone-level dataset + data dictionary.
- **Phase 3 — Model construction & calibration.** Implement Layers A–D, calibrate
  behavioral/cost/queueing parameters, fit adoption curves to historical data.
  *Output:* calibrated model set with parameter table.
- **Phase 4 — Country case studies.** SP1 (US urban/suburban/rural), SP2 (selected
  nation: 2a/2b/2c), SP3–SP4 timelines, SP5 cross-country taxonomy, SP6
  overlays. *Output:* per-task analyses.
- **Phase 5 — Validation & sensitivity.** Run hold-out validation, assumption and
  parameter sweeps, scenario envelopes. *Output:* robustness report.
- **Phase 6 — Synthesis & deliverables.** Technical report + one-page handout,
  with a clear factor list and ban-date recommendation.

### 6.2 Required modules (planned software components)

| Module | Responsibility | Consumes | Produces |
|--------|----------------|----------|----------|
| `data_loader` | ingest & validate raw sources | source files/APIs | raw tables |
| `geo_harmonizer` | build zones, joins, urban/sub/rural classes, corridors | raw tables | zone tables + graphs |
| `feature_builder` | demand, home-access, cost, index features | zone tables | feature matrices |
| `demand_model` | Layer A | features | zonal/corridor demand |
| `network_optimizer` | Layer B (facility location + queueing) | demand + costs | station/charger design |
| `deployment_model` | Layer C multi-period design | design + budgets | build schedules |
| `adoption_model` | Layer D diffusion/system-dynamics | policy/econ features | adoption timelines |
| `taxonomy` | Layer E indices + rules | country panel | archetypes/decision rules |
| `scenario_overlay` | Layer F multipliers | Layer A/B outputs | shifted designs |
| `validation` | hold-out checks, sensitivity, uncertainty | all model outputs | metrics + envelopes |
| `reporting` | tables/figures/handout scaffolding | all outputs | draft report + handout |

### 6.3 Supporting infrastructure (planned, not built here)

- Configuration files for all tunable parameters (costs, service standards,
  feedback strengths) so scenarios are reproducible without code edits.
- A run manifest capturing inputs, parameters, and code version per experiment.
- Deterministic seeding for any stochastic component (Monte-Carlo, simulation).
- Unit tests for geometry joins, unit conversions, and constraint feasibility.

### 6.4 Algorithm choices (indicative)

- Facility location: exact MIP for coarse zone sets; Lagrangian/greedy or
  local-search heuristics for fine grids; report optimality gap.
- Charger sizing: closed-form/approximate queueing with numeric checks.
- Deployment: multi-period MIP if tractable, else rolling-horizon greedy with
  regret accounting.
- Adoption: ODE integration for diffusion; Monte-Carlo over parameter bands.
- Taxonomy: normalized-index decision rules first; classifiers/clustering only as
  interpretability-checked illustrations.

### 6.5 Sequencing notes

Data (Phase 2) must precede calibration; calibration must precede country
studies; validation must precede synthesis. The Task-2 nation choice should be
made early (Phase 1/2) because it determines which national data sources are
prioritized.

---

## 7. Validation Strategy

### 7.1 Evaluation metrics (to be computed in later phases)

- **Network design (Layer B):** total system cost per vehicle; fraction of demand
  served within a coverage radius; average/95th-percentile queue wait;
  chargers-per-EV ratio; utilization; urban/suburban/rural balance (equity).
- **Deployment (Layer C):** cumulative cost vs. coverage trajectory; regret vs. a
  hindsight-optimal schedule; utilization during ramp-up; stranded-capacity
  measure.
- **Adoption (Layer D):** accuracy of milestone dates vs. historical analogues
  (calibration fit); sensitivity of milestone dates to key parameters.
- **Taxonomy (Layer E):** consistency of archetype assignment under small
  perturbations; face-validity against the six named countries' qualitative
  situations.
- **Scenario overlays (Layer F):** width of outcome envelopes; identification of
  which technologies materially change conclusions.

### 7.2 Validation methods

1. **Hold-out temporal validation.** Calibrate on earlier data; predict later
   periods; measure milestone/coverage error.
2. **Cross-country out-of-sample reasoning.** Fit taxonomy rules on some
   countries; check plausibility of their prescriptions on held-out countries.
3. **Back-testing against known network states.** Compare model's implied
   steady-state structure against observed charger density patterns where data
   exists (US, selected nation).
4. **Internal consistency checks.** Verify demand conservation (served demand ≤
   demand), coverage constraint satisfaction, and cost accounting closure.
5. **Expert/plausibility review.** Sanity-check outputs against published
   infrastructure studies (qualitative, not a numeric fit).
6. **Assumption stress tests.** Re-run key results under alternative assumptions
   (fixed vs. growing fleet, different home-access shares, different service
   standards).

### 7.3 Sensitivity & uncertainty analysis

- **One-at-a-time sweeps** over: service standard (wait time, coverage radius),
  home-charging share, cost multipliers (urban land premium, rural grid),
  charger power/economics, adoption-feedback strength.
- **Global sensitivity** (e.g., variance-based screening) to rank which
  parameters drive network size and milestone dates.
- **Scenario envelopes** for technology foreshocks (Layer F) and for
  wealth/density variation (Layer E).
- **Structural sensitivity:** compare candidate model families (MIP vs. heuristic,
  diffusion vs. system-dynamics) to confirm conclusions are not model artifacts.
- **Reporting rule:** every headline statement in the final report must be
  traceable to a validated model output and accompanied by its sensitivity range.

---

## 8. Expected Result Interpretation

> Interpretation *types* and *forms* only — no computed values are claimed here.

### 8.1 Expected outputs per task (form, not value)

- **Task 1:** a characterization of the Tesla network's coverage and capacity
  relative to a full-adoption requirement, and a **steady-state station
  blueprint** expressed as ranges by region type (urban/suburban/rural) with the
  dominant drivers identified (e.g., home-access share, trip-length mix,
  corridor spacing).
- **Task 2a:** a **cost/coverage-efficient station design** for the selected
  nation — count, spatial allocation, and charger mix — with a Pareto view of
  cost vs. coverage vs. equity and a ranked factor list.
- **Task 2b:** a **deployment policy** — a sequencing rule (city-first,
  rural-first, or mixed) and a supply-push/demand-pull recommendation —
  justified by which approach yields better coverage-to-cost and lower regret
  under plausible budgets.
- **Task 2c:** a **banded adoption timeline** at 10/30/50/100% milestones with a
  proposed ban window and the levers (charger density, price parity, policy)
  that most move those dates.
- **Task 3:** a **classification scheme** mapping nation archetypes to growth
  models, plus which factors flip a country from one model to another, and an
  honest feasibility assessment of such a system.
- **Task 4:** **conditional envelopes** showing which technological shifts
  materially reduce or reshape charging needs.
- **Task 5:** a **one-page factor handout** with a recommended ban-date logic.

### 8.2 Interpretation guidance

- Results should be read as **design guidance under stated assumptions**, not
  point predictions.
- Steady-state counts are **requirements under a service standard**, so the
  standard (coverage radius, wait target) must always be reported alongside the
  count.
- Timeline outputs are **scenario-dependent bands**; the ban-date recommendation
  should be robust across the band or explicitly hedged.
- Regional splits (urban/suburban/rural) will likely differ more in **charger
  type and utilization** than in headline station counts; interpret accordingly.
- Cross-country taxonomy results are **diagnostic aids**, not deterministic
  prescriptions.

### 8.3 Decision-relevance mapping

| Stakeholder question | Which layer answers it | What to report |
|----------------------|------------------------|----------------|
| "How many chargers at full adoption?" | B | Ranges by region + service standard |
| "Where should we build?" | B | Allocation + corridors + tiering |
| "What do we build first?" | C | Sequencing rule + regret |
| "When will we get to 30%/100%?" | D | Banded timeline + drivers |
| "Does our plan transfer?" | E | Archetype + flip factors |
| "How might technology change this?" | F | Envelopes + materiality |
| "What should leaders do Monday?" | G | Top factors + ban-date logic |

---

## 9. Limitations and Improvements

### 9.1 Known limitations of the planned approach

1. **Empty staged dataset.** No files are present (`dataset_path: []`), so Phase 2
   depends on externally sourced data; coverage and comparability across the six
   countries may be uneven.
2. **Fleet-invariance assumption (3.2).** Holding fleet size fixed may
   misstate long-run totals if vehicle ownership or shared mobility shifts
   materially.
3. **Aggregated spatial zones.** Zone-level modeling may hide intra-city siting
   nuances (street-level land, parking, dwell patterns).
4. **Behavioral data gaps.** Home-charging access and dwell-time behavior are
   approximated by proxies; range-anxiety parameters remain uncertain.
5. **Adoption feedback complexity.** Two-way charger↔adoption coupling is
   inherently hard to identify from limited historical data; strong conclusions
   would be fragile.
6. **Small country panel for taxonomy.** Only a handful of named countries limits
   statistical taxonomy; risk of overfitting and of over-generalization.
7. **Technology foreshocks are scenarios, not forecasts.** Their envelopes are
   illustrative and could be wide.
8. **Cost and grid data volatility.** Infrastructure costs and grid readiness
   change quickly; parameters may go stale between calibration and reporting.
9. **Scope restriction.** Excluding commercial/heavy vehicles may understate
   total national charging demand; only briefly addressed per the brief.

### 9.2 Planned improvements / extensions

- **Data upgrade:** acquire higher-resolution urban data (point-level parking,
  dwell) for the selected nation to refine siting beyond zoning.
- **Behavioral calibration:** incorporate surveys/telematics where available to
  replace proxy assumptions with measured distributions.
- **Endogenous adoption:** move from exogenous feedback strength to an estimated
  charger→adoption response using staggered historical rollouts.
- **Richer equity modeling:** explicit accessibility metrics for underserved and
  rural populations in the Layer-B objective.
- **Robust/stochastic optimization:** hedge network design against demand and cost
  uncertainty rather than optimizing on point estimates.
- **Intermodal integration:** model charging needs jointly with transit, car-share,
  and ride-share to avoid double-counting or missing substitution.
- **Multi-country empirical taxonomy:** expand the panel (beyond the named six)
  when data permits, to test and refine classification rules.
- **Grid co-optimization:** couple charger sizing with local grid capacity and
  demand-response/off-peak management.
- **Policy experiments:** evaluate ban-date scenarios against charger-readiness
  trajectories to bound feasible transition windows.

### 9.3 Success criteria for the future effort (not met by this draft)

A future modeling effort would be judged successful if it: (i) produces
transparent, reproducible steady-state network blueprints for the US and the
selected nation under an explicit service standard; (ii) yields a sequencing
policy with quantified regret versus hindsight; (iii) yields adoption timelines
whose milestone bands are robust across the pooled sensitivity analyses; (iv)
offers a defensible cross-country classification with clearly stated flip
factors; and (v) delivers a decision-usable one-page handout whose claims trace
back to validated outputs.

---

### Draft Status

- **Stage:** initial modeling plan (blueprint).
- **Contains computed results:** no.
- **Contains executed analysis/experiments:** no.
- **Next action (future phase):** execute Phase 2 (data assembly & preprocessing)
  per §4 and §6.1.
