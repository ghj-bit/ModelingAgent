# Modeling Blueprint Draft — MM-Bench 2017_E (Smart Growth City Design)

> Status: **planning draft only**. This document describes a planned workflow, candidate
> methods, and validation strategy. It intentionally contains no computed results,
> no fitted models, and no final conclusions. All statements are future-oriented.

---

## 1. Problem Background and Restatement

### 1.1 Context

Many communities are adopting **smart growth** initiatives to pursue long-range,
sustainable planning. Smart growth is an urban-planning theory (originating in the
1990s) intended to curb urban sprawl and preserve farmland around urban centers.
It is organized around the **three E's of sustainability**:

- **Economically prosperous**
- **Socially Equitable**
- **Environmentally Sustainable**

and around **ten guiding principles**:

1. Mix land uses
2. Take advantage of compact building design
3. Create a range of housing opportunities and choices
4. Create walkable neighborhoods
5. Foster distinctive, attractive communities with a strong sense of place
6. Preserve open space, farmland, natural beauty, and critical environmental areas
7. Strengthen and direct development toward existing communities
8. Provide a variety of transportation choices
9. Make development decisions predictable, fair, and cost effective
10. Encourage community and stakeholder collaboration in development decisions

Because urbanization is projected to continue rapidly (a widely cited projection places
~66% of the world's population in urban areas by 2050, with roughly 2.5 billion people
added to the urban population), measuring and steering the success of smart growth has
become a central planning concern.

### 1.2 The task to be modeled

The International City Management Group (ICM) is the client. The modeling effort will
produce a planning blueprint that supports the following requested deliverables. Note that
all of the below are **targets of the future modeling work**, not results produced here.

- **Deliverable A.** Select **two mid-sized cities** (population between 100,000 and
  500,000) located on **two different continents**.
- **Deliverable B.** Define a **quantitative metric** for the success of smart growth that
  reflects the three E's and/or the ten smart-growth principles.
- **Deliverable C.** Research each city's **current growth plan** and assess how well it
  satisfies the smart-growth principles, scored by the metric.
- **Deliverable D.** Develop a **redesigned growth plan** for each city over the coming
  decades, justified by geography, expected growth rates, and economic opportunities, and
  evaluated with the metric.
- **Deliverable E.** **Rank the individual initiatives** inside each redesigned plan from
  highest to lowest potential, and compare/contrast the rankings across the two cities.
- **Deliverable F.** Explain how the redesigned plans **support an additional 50% population
  increase by 2050**.

### 1.3 Restatement as a modeling problem

The task will be restated as: *construct a transparent, reproducible, multi-criteria
scoring-index pipeline that (i) measures baseline smart-growth performance of two
mid-sized cities, (ii) ranks candidate planning initiatives, and (iii) stress-tests the
resulting plans against a population-growth scenario.* The core modeling object will be a
**composite smart-growth index (SGI)** coupled to an **initiative-ranking model** and a
**growth-scenario feasibility model**.

---

## 2. Objectives and Subproblems

### 2.1 Overall objective

To design a defensible, transferable framework that converts the qualitative
smart-growth principles into a measurable index, applies it to two comparable
mid-sized cities on different continents, generates data-informed growth-plan
recommendations, and ranks those recommendations under a future population scenario.

### 2.2 Subproblems to be addressed by the future solver

| ID | Subproblem | Nature of output |
|----|------------|------------------|
| SP1 | City selection and justification | Two cities, two continents, 100k–500k population, with comparable data availability |
| SP2 | Composite smart-growth metric construction | Weighted, normalized index spanning three E's / ten principles |
| SP3 | Baseline assessment of current growth plans | Principle-level and aggregate scores (planned) |
| SP4 | Redesigned growth plan generation | Set of candidate initiatives per city with stated mechanisms |
| SP5 | Initiative ranking | Ordered priority list per city from MCDM model |
| SP6 | Cross-city comparison | Method for contrasting rankings and detecting divergence |
| SP7 | 50% growth stress test | Framework for testing plan capacity under +50% population by 2050 |
| SP8 | Sensitivity/robustness analysis | Rank stability under weight and data perturbations |

### 2.3 Deliverables (planned artifacts)

- A documented metric specification (indicators, normalization, weights, aggregation).
- A city-selection rationale with a comparison table of candidate cities.
- A plan-design template mapping initiatives → principles → indicator effects.
- A ranking procedure and comparison protocol.
- A growth-scenario evaluation protocol.
- Reproducible code modules (to be written later) and a modeling report.

---

## 3. Assumptions

The following assumptions will be adopted to make the problem tractable. Each is
paired with a justification and a planned validation/relaxation approach.

### 3.1 Assumptions about metric construction

- **A1. Principles are measurable via proxy indicators.** Each of the ten principles and
  each of the three E's can be represented by at least one observable, city-level
  socio-economic, environmental, or land-use indicator.
  - *Justification:* planning literature routinely uses proxies (e.g., transit share,
    housing-mix entropy, land-consumption per capita, job accessibility).
  - *Future validation:* check that proxies correlate with documented qualitative
    assessments; drop or replace weak proxies.
- **A2. Commensurability via normalization.** Heterogeneous indicators can be made
  comparable through min–max normalization (or z-scores) on a common [0,1] scale.
  - *Future validation:* compare min–max vs z-score vs rank normalization; test index
    stability.
- **A3. Additive aggregation with explicit weights is acceptable as a first model.**
  A weighted sum (or weighted geometric mean for penalty sensitivity) will aggregate
  normalized indicators.
  - *Justification:* transparency and auditability for a planning client outweigh the
    complexity of non-compensatory models at first pass.
  - *Future validation:* benchmark against a non-compensatory method (e.g., TOPSIS or
    outranking) to detect compensation artifacts.
- **A4. Weights are elicitable.** Expert judgment / stakeholder input / literature can
  supply defensible weights across the three E's and principles.
  - *Future validation:* AHP consistency ratio checks; weight-perturbation sensitivity.

### 3.2 Assumptions about cities and context

- **A5. Comparable scale allows comparison.** Two mid-sized cities of comparable
  population band can be compared even across different continents once indicators are
  normalized. Differences in governance/currency/geography will be treated as contextual
  modifiers rather than as blockers.
- **A6. Public data availability.** Sufficient open data (censuses, city plans, land-use
  maps, transport statistics, environmental records) will be obtainable for the chosen
  cities; if not, the selection will be revisited.
- **A7. Continuity of current plans.** Current published growth plans will be treated as
  the baseline "as-implemented" trajectory, with announced-but-unbuilt elements flagged
  separately.

### 3.3 Assumptions about growth and dynamics

- **A8. A single scenario band is sufficient at first.** The +50% population-by-2050
  requirement will be treated as a primary scenario, with lower/higher variants used only
  for sensitivity analysis.
- **A9. Initiative effects are approximately independent at first order.** Each initiative's
  marginal contribution to the index will be estimated independently, with interaction
  effects deferred to a second-pass refinement.
- **A10. Linear or piecewise-linear capacity responses are a reasonable first
  approximation** for housing, transport, and infrastructure capacity under growth.
  - *Future validation:* test saturating / threshold nonlinearities.

### 3.4 Explicit non-assumptions / caveats

- The model will **not** claim to predict exact future indicator values; it will aim for
  comparative ranking and directional robustness.
- Political feasibility, funding cycles, and regulatory constraints will be treated as
  documented qualitative modifiers, not as fully modeled constraints, in the first pass.

---

## 4. Data Processing Plan

> Note: the staged dataset for this problem is declared empty
> (`dataset_path: []`, `dataset_description: {}`, `variable_description: {}`).
> Therefore the data plan below is a **data-acquisition and construction plan** for the
> future solver, not an analysis of existing files.

### 4.1 Candidate data sources (to be collected)

- **Population & demographics:** national statistical offices, census bureaus, UN
  World Urbanization Prospects, city open-data portals.
- **Economic:** GDP/GVA by sector, employment rates, median income, business-formation
  rates, cost-of-living indices (regional/national statistical agencies).
- **Social equity:** housing affordability ratios, Gini or income deciles, access to
  services, segregation/accessibility indices, public-transit equity.
- **Environmental:** green-space per capita, land-consumption rate, CO₂/emissions
  inventories, air-quality indices, impervious-surface/ farmland loss, energy use.
- **Land use & planning:** municipal comprehensive/growth plans, zoning and land-use maps,
  urban-growth-boundary documents, building-permit history.
- **Transport:** modal share, transit network length/coverage, walkability scores,
  vehicle-miles traveled, commuting times.
- **Governance/process:** planning-process transparency records, public-participation
  documentation (for principles 9 and 10).

### 4.2 Preprocessing pipeline (planned)

1. **Ingest & catalog:** assemble a source register with origin, year, spatial unit,
   and license for each dataset.
2. **Unit harmonization:** convert currencies to a common base year, areas to km²,
   rates to consistent denominators.
3. **Spatial alignment:** reconcile municipal vs metropolitan boundaries; use
   consistent administrative units (ideally the functional urban area).
4. **Temporal alignment:** build a common time index; interpolate within reasonable
   bounds where series are incomplete.
5. **Missing-data handling:** document and apply a rule hierarchy
   (national/regional substitution → interpolation → exclusion), with flags.
6. **Outlier / anomaly screening:** detect implausible values and document corrections.
7. **Quality scoring:** assign a per-indicator provenance/quality tier to feed later
   robustness checks.

### 4.3 Feature construction (planned)

- **Principle-level features:** map each of the 10 principles to ≥1 indicator
  (e.g., land-use mix entropy; dwelling-type diversity; intersection density/walk score;
  transit modal share; green-space ratio; infill share of permits).
- **Three-E's features:** group principle indicators into Economic, Equity, and
  Environmental pillars (a principle may contribute to more than one pillar, with
  documented cross-walk).
- **Directionality:** mark each indicator as "higher-is-better" or "lower-is-better"
  prior to normalization.
- **Derived composites:** raw → normalized → pillar sub-scores → overall SGI.

### 4.4 Data usage strategy (planned)

- **Baseline layer:** current indicator values → describe each city's present
  smart-growth position.
- **Plan layer:** textual/structural encoding of each city's current and proposed plans
  → mapping to principles and to expected indicator deltas.
- **Scenario layer:** population-growth and economic-growth projections used only to
  define test scenarios for the redesigned plans.
- **Cross-validation layer:** independent sources for key indicators to bound uncertainty.

---

## 5. Candidate Model Framework

### 5.1 Overview of the planned model stack

The framework will consist of four coupled components:

1. **Composite Smart-Growth Index (SGI)** — a multi-criteria measurement model.
2. **Plan-to-Principle Mapping Model** — converts plans/initiatives into expected
   indicator effects.
3. **Initiative Ranking Model** — MCDM ranking of initiatives within each plan.
4. **Growth-Scenario Feasibility Model** — capacity/consistency check under +50% growth.

### 5.2 Component 1 — Composite Smart-Growth Index (SGI)

- **Representation.** Two-level hierarchy: `SGI → pillars (Econ, Equity, Env) → principles
  → indicators`, or alternatively `SGI → 10 principles → indicators`. Both hierarchies
  will be considered and compared.
- **Normalization.** Min–max scaling (with z-score and rank-transform alternatives).
- **Aggregation.** Weighted arithmetic mean (compensatory) as primary; weighted geometric
  mean and TOPSIS-style distance aggregation as robustness alternatives.
- **Weighting.** AHP / pairwise comparison with consistency ratio checks; equal-weight
  and entropy-weight baselines for comparison.
- **Mathematical ideas.** Linear additive utility; entropy/CRITIC objective weights;
  possibly fuzzy membership functions for qualitative principles.

### 5.3 Component 2 — Plan-to-Principle Mapping Model

- **Representation.** Each initiative will be encoded as a vector of expected impacts on
  indicators/principles, with a magnitude band and a confidence level.
- **Mathematical ideas.** Structured impact matrices; qualitative-to-quantitative
  translation via ordinal scales; logic-model / theory-of-change chains.
- **Advantages.** Keeps plans interpretable and traceable to principles.
- **Limitations.** Impact estimates are judgment-based and require sensitivity analysis.

### 5.4 Component 3 — Initiative Ranking Model

- **Candidate methods (to be compared):**
  - **TOPSIS** — distance to ideal/anti-ideal on normalized criteria.
  - **AHP** — pairwise-derived priorities for ranking and weighting.
  - **Weighted Sum Model / weighted product model** — transparent baselines.
  - **PROMETHEE / outranking** — non-compensatory alternative.
  - **Entropy or CRITIC weighting** — data-driven weight cross-check.
- **Ranking criteria (candidate set):** estimated index gain, cost/feasibility,
  time-to-impact, equity benefit, environmental benefit, alignment with geography,
  scalability under growth, stakeholder support, risk.
- **Output (planned).** An ordered initiative list per city plus stability intervals.

### 5.5 Component 4 — Growth-Scenario Feasibility Model

- **Question.** Will the redesigned plan plausibly accommodate a +50% population by 2050?
- **Candidate approaches:**
  - **Capacity accounting:** per-sector capacity (housing units, transit throughput,
    water/energy, school/health) compared against projected demand.
  - **Land-sufficiency check:** land required under different density assumptions vs
    developable/infill land available.
  - **System-dynamics sketch:** stocks and flows (housing stock, infrastructure,
    employment) with feedback; used qualitatively if calibration data are thin.
  - **Scenario matrix:** combinations of growth rate × density × modal shift ×
    investment level, evaluated by the SGI and capacity ratios.
- **Mathematical ideas.** Linear/piecewise capacity constraints; logistic growth curves;
  elasticity-based demand estimation; optional optimization (LP/MIP) for land allocation.

### 5.6 Variables (candidate taxonomy)

- **Decision variables (plan design):** initiative selection/intensity, land-allocation
  shares, transit investment levels, housing-mix targets, green-space targets.
- **State variables:** population, housing stock, employment, modal shares, emissions,
  land consumed, affordability index.
- **Parameters:** growth rates, cost coefficients, density limits, elasticities.
- **Outputs:** SGI value, pillar scores, initiative rankings, capacity ratios.

### 5.7 Advantages and limitations of the overall framework

- **Advantages.** Transparent, auditable, transferable; separates measurement from
  judgment; supports comparison across cities; explicitly scenario-driven.
- **Limitations.** Weight subjectivity; proxy quality; compensation effects in additive
  aggregation; limited modeling of politics and financing; cross-continental
  comparability constraints.

---

## 6. Implementation Roadmap

### 6.1 Planned workflow phases

1. **Scoping & city selection (SP1).** Build a candidate list of mid-sized cities on
   ≥2 continents; screen by data availability, growth context, and geographic contrast;
   document the selection rationale and finalize two cities.
2. **Indicator design (SP2).** Finalize principle/three-E's indicator set; define
   directionality, normalization, weights; freeze a metric specification document.
3. **Data acquisition & preprocessing (SP2/SP3).** Assemble datasets per Section 4;
   produce a clean, documented indicator table per city.
4. **Baseline scoring (SP3).** Compute baseline SGI and pillar/principle sub-scores;
   document uncertainty bands. *(Future execution only.)*
5. **Plan encoding (SP4).** Encode current plans and design redesigned plan initiatives;
   build the plan-to-principle impact matrix.
6. **Ranking (SP5/SP6).** Apply the ranking model; produce ordered lists; compare cities.
7. **Growth stress test (SP7).** Run the capacity/scenario analysis under +50% growth.
8. **Sensitivity & robustness (SP8).** Perturb weights, proxies, and impact bands.
9. **Synthesis & reporting.** Produce the modeling report and supporting artifacts.

### 6.2 Required modules (to be implemented later)

- `data/` ingestion and source-register module
- `preprocessing/` normalization, imputation, spatial/temporal alignment
- `metrics/` SGI construction, weighting (AHP/entropy), aggregation
- `planning/` plan encoding and impact-matrix builder
- `ranking/` TOPSIS/AHP/WPM/PROMETHEE implementations and comparison harness
- `scenario/` capacity accounting, land-sufficiency, optional optimization
- `sensitivity/` weight/scenario perturbation engine
- `reporting/` table/figure generation (deferred)
- `config/` frozen metric specification, weight sets, city metadata

### 6.3 Algorithms (candidate)

- Normalization: min–max, z-score, rank.
- Weighting: AHP eigenvector method, entropy, CRITIC, equal weights baseline.
- Aggregation/ranking: weighted sum, weighted product, TOPSIS, PROMETHEE, AHP.
- Scenario: LP/MIP land allocation; logistic growth; capacity-ratio arithmetic;
  Monte-Carlo sampling over parameter bands.
- Sensitivity: one-at-a-time perturbation, rank-correlation stability, scenario sweeps.

### 6.4 Suggested sequencing and dependencies

- Metric specification must be frozen **before** baseline scoring and ranking.
- City selection must precede data acquisition.
- Impact-matrix design must precede ranking and scenario testing.
- Sensitivity analysis runs **after** the primary pipeline yields a stable configuration.

---

## 7. Validation Strategy

### 7.1 Evaluation metrics (planned)

- **Internal consistency:** AHP consistency ratio; weight-sum sanity; monotonicity of
  index w.r.t. improved indicators.
- **Rank stability:** Spearman/Kendall correlation of initiative rankings across weight
  sets and methods; rank-flip counts.
- **Index robustness:** variance of SGI under normalization/aggregation alternatives.
- **Face validity:** expert/stakeholder review of whether scores align with documented
  planning reality.
- **Comparative validity:** internal consistency of cross-city comparisons.

### 7.2 Validation methods (planned)

- **Cross-method triangulation:** compare weighted-sum, TOPSIS, and PROMETHEE rankings.
- **Cross-weight triangulation:** equal vs entropy vs AHP vs stakeholder weights.
- **Leave-one-indicator-out:** test whether a single proxy drives the outcome.
- **Data-source triangulation:** validate key indicators against independent sources.
- **Scenario validation:** verify capacity ratios behave plausibly across growth cases.
- **Back-of-envelope checks:** ensure capacity arithmetic is dimensionally and
  logically coherent (no unit-mismatch artifacts).

### 7.3 Sensitivity analysis (planned)

- **Weight sensitivity:** uniform ± perturbations and targeted swings on dominant pillars.
- **Impact-band sensitivity:** optimistic/neutral/pessimistic plan-effect estimates.
- **Growth-scenario sensitivity:** ±variants around the +50% primary case.
- **Structural sensitivity:** additive vs geometric vs outranking aggregation.
- **Reporting of results:** present rankings as intervals/robustness classes where
  unstable, rather than as spurious single-point orders.

---

## 8. Expected Result Interpretation

> This section describes how the eventual outputs *would* be read. No outputs are
> produced in this draft.

- **SGI per city (planned).** A single comparable number per city interpreted as a
  relative smart-growth performance level, decomposed into Economic, Equity, and
  Environmental pillar scores and further into principle-level diagnoses.
- **Baseline assessment (planned).** A profile of which principles each city's current
  plan already serves well and which it neglects — intended as a diagnostic, not a verdict.
- **Redesigned plan evaluation (planned).** Predicted SGI movement under the new plan,
  with each initiative's marginal contribution isolated.
- **Initiative ranking (planned).** A priority ordering interpreted as *relative potential*
  under stated criteria — expected to be reported with stability bands.
- **Cross-city contrast (planned).** Explanation of why rankings may diverge (drivers such
  as geography, growth rate, economic structure) and what transfers between cities.
- **Growth stress test (planned).** A statement of whether, and under which density,
  modal, and investment assumptions, the plan is consistent with absorbing +50% population.

Interpretation guidance: results will be framed as **decision-support evidence with
uncertainty**, emphasizing comparative and directional robustness over point precision.

---

## 9. Limitations and Improvements

### 9.1 Anticipated limitations

- **Subjectivity of weights and impact bands** despite structured elicitation.
- **Proxy validity:** indicators may imperfectly represent principles (especially
  principles 5, 9, and 10, which are process/qualitative).
- **Cross-continental comparability:** differing data standards and administrative
  definitions may bias comparison.
- **Compensation effects** in additive aggregation can mask severe single-pillar deficits.
- **Limited treatment of politics, financing, and legal constraints.**
- **Uncertain long-horizon projections** (to 2050) with compounding uncertainty.
- **Independence assumption** among initiatives may over/understate combined effects.

### 9.2 Planned improvements / extensions

- Replace or complement additive aggregation with non-compensatory methods.
- Introduce fuzzy or possibility-based handling of qualitative principles.
- Add a system-dynamics layer with feedback loops once calibration data are available.
- Incorporate stakeholder-weighted co-design for weights and initiative scoring.
- Expand to a portfolio of cities to test transferability of the metric.
- Add explicit financing/cost-benefit and political-feasibility modules.
- Adopt probabilistic (Monte-Carlo) scenario ensembles instead of single scenarios.
- Validate against realized outcomes as data become available over time.

---

## Appendix A — Planned Section-to-Requirement Traceability

| Requirement | Planned treatment | Section |
|-------------|-------------------|---------|
| Two mid-sized cities, two continents | City-selection protocol | 2, 4, 6 |
| Metric covering 3 E's / 10 principles | Composite Smart-Growth Index | 5.2 |
| Assess current growth plans | Baseline scoring + plan encoding | 5.3, 6.1 |
| Redesigned growth plan | Initiative design + impact matrix | 5.3, 6.1 |
| Rank initiatives, compare cities | MCDM ranking + comparison protocol | 5.4, 6.1 |
| +50% population by 2050 | Growth-scenario feasibility model | 5.5, 6.1 |

## Appendix B — Planning Checklist for the Future Solver

- [ ] Freeze city selection with documented rationale.
- [ ] Freeze metric specification (indicators, directionality, weights).
- [ ] Complete and document the data source register.
- [ ] Build cleaned indicator tables per city.
- [ ] Encode plans and build the impact matrix.
- [ ] Run baseline scoring (future execution).
- [ ] Generate redesigned plans and rank initiatives.
- [ ] Run +50% growth scenario and capacity checks.
- [ ] Complete sensitivity/robustness analysis.
- [ ] Produce the final modeling report.

---

*End of planning draft. No calculations, fits, experiments, or results are included by design.*
