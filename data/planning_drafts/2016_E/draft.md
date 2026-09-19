# Modeling Blueprint Draft — MM-Bench Problem 2016_E
## "Can We Provide Clean Fresh Water to All?" — regional clean-water availability, scarcity drivers, and intervention design

> Status: **planning draft only.** This document is a roadmap for future modeling work.
> It contains no solved results, no fitted models, no computed outputs, and no final conclusions.
> All statements are written in future-oriented / conditional language ("will", "should", "is planned to").

---

## 0. Workspace and Data Reality Check (planning note)

- The staged workspace currently contains only empty scaffold folders:
  `output/code/`, `output/data/`, `output/logs/`, `output/results/`.
- The provided dataset definition is empty:
  `{"dataset_path": [], "dataset_description": {}, "variable_description": {}}`.
- Consequence for planning: **no curated tabular dataset is supplied with the task.**
  The plan therefore treats data acquisition from the public sources named in the problem
  (UNEP *Vital Water*, FAO AQUASTAT, World Water Council / *The World's Water*, WRI,
  GrowingBlue, UNEP State of the World's Fresh and Marine Waters) as a **first-class,
  explicitly scheduled workstream** rather than an assumed input.
- Any external data acquisition will be documented with provenance, retrieval date, geographic
  resolution (national / sub-national / basin), temporal coverage, and license/attribution so
  that later modeling is reproducible and auditable.

---

## 1. Problem Background and Restatement

The task frames global water scarcity as a coupled **human–environment system**. The International
Clean Water Movement (ICM) asks for analytical support in improving access to clean, fresh water.

Restated core question set (to be carried forward as the modeling target):

1. A measurable notion of a region's **ability to supply clean water to meet population needs**,
   accounting for the **dynamic** (time-varying) interaction of supply and demand factors.
2. Diagnosis of a **specific overloaded region**: why and how scarcity arises, separating
   **physical scarcity** (not enough water physically) from **economic scarcity** (water exists but
   management/infrastructure is limiting), and separating **social** from **environmental** drivers.
3. A **~15-year forward projection** of that region under the chosen model, including environmental
   drivers acting on model components, plus the human/livelihood consequences for citizens.
4. An **intervention plan** spanning all scarcity drivers, analyzed for **spillover effects** on
   surrounding areas and the broader water ecosystem, with explicit strengths/weaknesses.
5. A **counterfactual projection** with the intervention: will the region become less susceptible?
   Will water become critical, and if so, when?
6. A **20-page report** (plus one-page summary sheet) communicating model, no-intervention baseline,
   intervention, and regional + surrounding-area effects, with model strengths and weaknesses.

Key qualitative claims in the background that the model will need to be consistent with:
water use has been growing roughly **twice as fast as population**; scarcity has both physical and
economic roots; sanitation deficits can degrade water quality; population growth increases burden;
climate change is expected to compound the problem. The model will be designed to *test* competing
explanations (personal consumption vs. industrial consumption vs. pollution-driven supply depletion)
rather than assume one.

---

## 2. Objectives and Subproblems

### 2.1 Primary objective
Produce one **integrated, dynamic, region-parameterizable framework** that (a) quantifies a region's
capacity to deliver clean water relative to population demand, (b) attributes scarcity to named
drivers, (c) supports scenario projection, and (d) evaluates intervention strategies and their
externalities.

### 2.2 Task-to-subproblem mapping (each is a planned modeling module)

| Task | Planned subproblem | Planned deliverable |
|---|---|---|
| 1 | Define and construct a **scalable clean-water capacity / scarcity metric** | Formal index definition + dynamic formulation |
| 2 | **Region selection + diagnostic decomposition** | Justified region choice + driver attribution framework |
| 3 | **15-year no-intervention projection** | Baseline scenario timeline + human-impact narrative |
| 4 | **Intervention design + externality analysis** | Candidate intervention portfolio + spillover analysis plan |
| 5 | **Intervention scenario projection** | Counterfactual timeline + criticality timing plan |
| 6 | **Report integration** | Report structure + figure/table inventory |

### 2.3 Explicit non-objectives (for this drafting stage)
No data cleaning, no parameter fitting, no numerical simulation, no region finalization, no plots,
no report prose. Those are deferred to later execution stages.

---

## 3. Assumptions

Planned working assumptions, each with justification and a future validation route.

**A. Scope and boundaries**
- A1. A "region" will be treated as a nested unit (country → sub-national → basin), with the model
  parameterizable at the country level first and refinable downward. *Justification:* matches data
  availability granularity (AQUASTAT is largely national; basin data partly available). *Validation:*
  cross-check aggregate consistency between nested levels.
- A2. The system boundary will be the region plus its **inflows/outflows** (shared rivers, virtual
  water in trade, transboundary aquifers), so spillovers can be modeled. *Validation:* mass-balance
  closure tests.

**A.2 Supply-side assumptions**
- A3. Renewable freshwater availability will be approximated from precipitation, runoff, and
  recharged groundwater, with **non-renewable aquifer withdrawal** treated as a depleting stock.
- A4. **Desalination and rainwater harvesting** will be modeled as augmented supply with
  energy/cost and capacity constraints, not as free water.
- A5. Water **quality** will be modeled as a modifier that reduces *usable* supply, not as a
  separate supply. *Justification:* problem explicitly links sanitation and pollution to effective
  availability.

**A.3 Demand-side assumptions**
- A6. Demand will be decomposed into **agricultural, industrial, and municipal/domestic** sectors.
- A7. Population and per-capita demand will evolve; the model will allow both **intensive** change
  (per-capita consumption) and **extensive** change (population) to drive demand, so the
  "twice the population growth rate" observation can be decomposed.
- A8. Prices/policies will be treated as **control levers** rather than exogenous constants in
  intervention scenarios.

**A.4 Modeling-process assumptions**
- A9. Missing values will be handled by documented imputation/interpolation with uncertainty flags.
- A10. Uncertain parameters will be represented as ranges/distributions to enable sensitivity
  analysis rather than single point estimates.

**A.5 Deliberate simplifications (to be acknowledged in limitations)**
- A11. Ecology and groundwater lag effects will be represented coarsely at first (single storage
  compartments), to be refined if data supports it.
- A12. Climate forcing will be represented through bounded scenario ranges (e.g., low/mid/high
  stress trajectories) rather than a fully coupled GCM.

---

## 4. Data Processing Plan

Because the workspace dataset is empty, this section is organized as **acquire → harmonize →
derive → store**.

### 4.1 Data acquisition plan (primary + supporting sources)
- **Physical supply indicators:** UNEP *Vital Water* (renewable freshwater per capita, water stress
  and overuse indices), FAO AQUASTAT (internal/external renewable water resources, withdrawal by
  sector), AQUASTAT land & water resources, WRI Aqueduct-style stress indicators.
- **Demand / demographic indicators:** UN population and urbanization series, WHO/UNICEF JMP for
  water and sanitation access, World Bank development indicators for industrial activity.
- **Intervention-relevant indicators:** desalination capacity and cost, irrigation efficiency
  benchmarks, wastewater treatment/reuse statistics, network leakage estimates.
- **Contextual / auxiliary:** basin boundaries, transboundary agreements, climate projections.

### 4.2 Harmonization plan
- Align all series to a common **region key** and **annual time index**; maintain a mapping table for
  country→basin and country→sub-region.
- Reconcile **units** (km³/yr, m³/capita/yr, %) into a single internal unit system, with unit
  conversions logged.
- Reconcile **vintages** (different reference years across sources) via documented gap-filling rules.
- Record a **provenance/metadata registry** (source, URL, year, resolution, license) for every series.

### 4.3 Feature construction plan (derived quantities to be built later)
- Supply features: total renewable freshwater, per-capita renewable freshwater, non-renewable
  withdrawal rate, augmented supply (desalination + harvesting potentials).
- Demand features: sectoral withdrawal shares, per-capita domestic demand, water-use intensity of
  industry/agriculture.
- Scarcity features: withdrawal-to-availability ratio, treated as a candidate stress index;
  a **usable-supply** adjustment for quality.
- Driver features: population growth rate, urbanization, GDP/industrial share, sanitation coverage,
  pollution proxies (e.g., wastewater discharge relative to dilution capacity).
- The **candidate features will be treated as hypotheses to be screened**, not predetermined inputs.

### 4.4 Data usage strategy
- Split conceptually into: **calibration/parameterization set** (historical panel), **validation
  set** (held-out regions or withheld years), and **scenario inputs** (projected population/climate).
- Preserve a **raw → processed → modeled** data lineage in `output/data/` and log every transform in
  `output/logs/`.

---

## 5. Candidate Model Framework

The blueprint deliberately carries **multiple candidate model families** so the later stage can
compare rather than commit prematurely. Each is described with role, mathematical idea, advantages,
and limitations.

### 5.1 Tier 1 — Composite scarcity index (Task 1 measure)
- **Idea:** a normalized, weighted combination of supply, demand, quality, and infrastructure
  sub-indicators into a single capacity-to-need score (dimensionless, e.g., [0,1] or deficit ratio).
- **Candidate weighting schemes:** entropy weighting (data-driven), AHP / expert weighting
  (judgment-driven), equal weighting as a baseline; multi-criteria decision analysis (TOPSIS-style)
  for ranking.
- **Advantages:** transparent, cheap, comparable across regions, easy to communicate.
- **Limitations:** sensitive to weighting and normalization choices; static unless extended.

### 5.2 Tier 2 — Dynamic stock–flow / system-dynamics model (dynamic core; Tasks 1–5)
- **Idea:** represent water as **stocks** (surface reservoirs, renewable groundwater, non-renewable
  aquifer, treated/usable water) driven by **flows** (precipitation/recharge, withdrawal by sector,
  return flows, evaporation, desalination, reuse), coupled to population and economic stocks.
- **Mathematical ideas:** systems of ordinary differential equations / difference equations;
  feedback loops (supply→use→scarcity→policy→supply); delay terms for aquifer and infrastructure.
- **Advantages:** captures the required *dynamics* and feedback; natural scenario engine;
  intervention = parameter/flow modification.
- **Limitations:** parameter-heavy; calibration data scarce; risk of over-fitting.

### 5.3 Tier 3 — Supply–demand balance and stress-ratio models (Tasks 1, 3, 5)
- **Idea:** compute projected need vs. projected availability; define scarcity as a deficit or as a
  withdrawal-to-availability ratio crossing a threshold; forecast when a threshold will be crossed.
- **Mathematical ideas:** deterministic trend/regression extrapolation; scenario arithmetic;
  optional stochastic demand (Monte-Carlo) for crossing-time distributions.
- **Advantages:** interpretable; directly answers "when will scarcity occur?"
- **Limitations:** trend extrapolation is fragile; ignores feedback unless coupled to Tier 2.

### 5.4 Tier 4 — Attribution / regression layer (Task 2 diagnosis)
- **Idea:** statistically attribute scarcity outcomes to candidate drivers (consumption patterns,
  industrial intensity, pollution, population) to resolve the problem's open "what is the cause?"
  question.
- **Mathematical ideas:** panel regression with fixed/random effects; decomposition analysis
  (e.g., drivers decomposition of water-use growth); possibly LASSO-style variable selection.
- **Advantages:** data-grounded driver ranking; supports narrative.
- **Limitations:** limited, noisy, heterogeneous cross-country data; causality caveats.

### 5.5 Tier 5 — Optimization / decision layer (Tasks 4–5)
- **Idea:** choose an intervention portfolio (desalination, drip irrigation, reuse, leak reduction,
  harvesting, pricing, sanitation investment) subject to budget, energy, and ecological constraints.
- **Mathematical ideas:** linear / mixed-integer programming, multi-objective optimization
  (cost vs. scarcity reduction vs. ecological impact), possibly robust optimization under uncertainty.
- **Advantages:** prescriptive; yields defensible intervention plans and trade-off frontiers.
- **Limitations:** requires cost/benefit parameters that are uncertain; objective weighting choices.

### 5.6 Tier 6 — Spatially explicit / network extension (Task 4 spillover analysis)
- **Idea:** model the region as a node in a network of neighboring regions sharing basins and
  embedded/virtual water, so externalities of interventions are visible (upstream/downstream effects).
- **Mathematical ideas:** network flow with shared resource constraints; input–output / virtual-water
  accounting.
- **Advantages:** directly addresses the "impacts surrounding areas" requirement.
- **Limitations:** cross-border data scarcity; boundary assumptions dominate results.

**Planned integration:** Tier 1 supplies the headline metric; Tier 2 provides dynamics; Tier 3 gives
the projection engine; Tier 4 supplies evidence for driver attribution in prose; Tier 5 turns the
model into a prescriptive plan; Tier 6 contextualizes externalities. The later stage will decide
which combination to actually instantiate.

---

## 6. Implementation Roadmap

Planned execution stages (each will produce artifacts under `output/`):

1. **Stage 0 — Scoping & region shortlist:** confirm modeling scale; draft a candidate region
   shortlist from the UN water-stress map and select one overloaded region (Task 2), documenting
   physical vs. economic scarcity evidence sources. *(No selection made in this draft.)*
2. **Stage 1 — Data pipeline:** build acquisition scripts/scrapers for the named sources; implement
   harmonization, unit reconciliation, gap-filling, and the provenance registry. Output stored in
   `output/data/`, logs in `output/logs/`.
3. **Stage 2 — Feature engineering:** construct supply/demand/quality/driver feature sets per
   Section 4.3.
4. **Stage 3 — Tier 1 index implementation:** build the composite capacity-to-need metric and its
   weighting variants.
5. **Stage 4 — Tier 2 dynamic core:** implement stock–flow dynamics with sectoral demand and quality
   modifier; set up scenario switches.
6. **Stage 5 — Baseline projection (Task 3):** run the no-intervention 15-year projection; produce
   timeline of the scarcity metric and citizen-impact mapping.
7. **Stage 6 — Intervention optimization (Task 4):** formulate and solve the portfolio problem;
   run Tier 6 spillover analysis.
8. **Stage 7 — Intervention projection (Task 5):** re-run dynamics under intervention; estimate
   whether/when scarcity becomes critical.
9. **Stage 8 — Report assembly (Task 6):** integrate model description, region diagnosis, baseline,
   intervention, externality discussion, strengths/weaknesses; build figure/table inventory for the
   20-page report plus one-page summary sheet.

**Planned module inventory (later implementation):**
`data_acquire`, `data_harmonize`, `feature_build`, `index_model`, `dynamics_model`,
`projection_engine`, `attribution_model`, `optimization_model`, `spillover_model`,
`scenario_manager`, `validation`, `reporting`.

**Planned tooling:** Python (pandas / numpy / scipy / statsmodels / scikit-learn / PuLP or OR-Tools
for optimization), with optional a system-dynamics library; all runs logged and version-pinned.

---

## 7. Validation Strategy

### 7.1 Evaluation metrics (to be selected later)
- **Index-level:** agreement of the composite scarcity metric with independent classifications
  (e.g., UNEP stress/overuse categories) — rank correlation / classification agreement.
- **Model-level:** retrospective fit error on historical water-use and stress series (RMSE/MAE),
  and out-of-sample projection error on held-out years.
- **Projection-level:** plausibility checks against published regional outlooks; bounding via
  uncertainty intervals rather than point claims.
- **Intervention-level:** cost-effectiveness metrics, robustness across scenarios, and consistency
  of mass balance.

### 7.2 Validation methods
- **Internal consistency:** physical mass-balance closure (inflow − outflow − storage change ≈ 0).
- **Cross-source triangulation:** compare overlapping indicators from AQUASTAT vs. UNEP vs. WRI.
- **Hold-out / backtesting:** calibrate on earlier decades, validate on later years; or leave-one-
  region-out cross-validation for the attribution layer.
- **Expert/qualitative review:** correspondence between model-attributed drivers and documented
  regional narratives.

### 7.3 Sensitivity and uncertainty analysis
- **One-at-a-time sensitivity** on key parameters (recharge rates, per-capita demand, desalination
  cost/capacity, leakage, efficiency).
- **Global sensitivity** (e.g., variance-based / Sobol-style) to rank parameter influence.
- **Scenario ensembles** (low/mid/high population, climate, and policy) to express projection ranges.
- **Structural sensitivity:** compare Tier 1 vs. Tier 2 vs. Tier 3 conclusions to test whether
  findings are model-dependent.

---

## 8. Expected Result Interpretation

This section states how outputs *will be read*, not what they are.

- The **Tier 1 metric** will be interpreted as a relative, region-comparable indicator of the gap
  between usable clean-water supply and population need — higher/lower values will map to
  "more/less able to meet needs."
- The **baseline projection (Task 3)** will be read as a *conditional* trajectory under stated
  population, climate, and policy assumptions — not a prediction of the future.
- The **attribution layer (Task 2)** will be read as an evidence-weighted ranking of drivers
  (physical vs. economic; social vs. environmental), acknowledging statistical caveats.
- The **intervention analysis (Task 4–5)** will be read as a *trade-off*, expressed as strengths,
  weaknesses, and externalities (upstream/downstream and neighboring-region effects), and as a
  "when does scarcity become critical?" crossing-time range rather than a single date.
- All quantitative outputs will be reported with **ranges/uncertainty bands** and accompanied by
  explicit assumption ledgers.

---

## 9. Limitations and Improvements

### 9.1 Anticipated limitations
- **Data scarcity/heterogeneity:** national aggregation hides within-country inequality; sparse and
  inconsistent time series; differing reference years.
- **Boundary risk:** spillover conclusions depend heavily on where the system boundary is drawn.
- **Parameter uncertainty:** dynamic models will be parameter-rich relative to available data.
- **Causality limits:** attribution from observational panel data cannot establish causation.
- **Climate coupling:** simplified climate forcing may understate extremes.
- **Normative choices:** index weights, objective weights, and thresholds embed value judgments.

### 9.2 Planned improvements
- Move from national to basin/sub-national resolution where data permits.
- Replace single-storage compartments with multi-compartment (surface/soil/deep aquifer) hydrology.
- Add stochastic (Monte-Carlo) demand and climate to convert point projections into distributions.
- Couple Tier 4 attribution with Tier 2 dynamics for an endogenous driver loop.
- Extend Tier 6 to a fuller virtual-water trade network.
- Institute an ongoing sensitivity/uncertainty reporting standard for every headline number.

---

## Appendix — Planned Section-to-Requirement Traceability

| Blueprint section | ICM task(s) served |
|---|---|
| §1 Background, §2 Objectives | All (framing) |
| §5.1 Tier 1, §5.3 Tier 3 | Task 1 |
| §5.4 Tier 4, §6 Stage 0 | Task 2 |
| §5.2 Tier 2, §5.3 Tier 3, §6 Stage 5 | Task 3 |
| §5.5 Tier 5, §5.6 Tier 6, §6 Stage 6 | Task 4 |
| §5.2/modified-Tier 2, §6 Stage 7 | Task 5 |
| §6 Stage 8, §8, §9 | Task 6 |

*End of planning draft. No modeling, computation, or solving has been performed.*
