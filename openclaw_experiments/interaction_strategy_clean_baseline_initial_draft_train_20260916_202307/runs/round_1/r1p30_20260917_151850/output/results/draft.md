# Forestry for Carbon Sequestration — Modeling Blueprint (Initial Draft)

> **Document status:** Planning draft only. This file is a *roadmap* for future modeling work.
> It contains **no** computed results, **no** executed experiments, **no** fitted models, and **no**
> final conclusions. All statements are written in future/conditional tense to describe what a
> downstream solver *will* do.

Problem ID: `2022_Forestry_for_Carbon`
Title: Forestry for Carbon Sequestration
Source: ICM 2022 (Problem E)
Deliverable target: a complete modeling solution (≤25 pages) with Summary Sheet, full solution,
and a 1–2 page newspaper article.

---

## 1. Problem Background and Restatement

### 1.1 Background as given
Climate change will remain a central global concern, and reducing atmospheric greenhouse gases
will be a priority. Carbon sequestration — capturing and storing carbon dioxide — will be a key
lever. Forests will play a major role by storing carbon in living biomass and in harvested wood
products (e.g., furniture, paper). Forest management decisions (when and how much to harvest, and
how to regenerate) will therefore influence net carbon outcomes. Harvesting will create product
pools and substitution benefits, but overharvesting will erode sequestration capacity. A forest
manager will face a trade-off between the market value of forest products and the long-run climate
value of standing forests.

### 1.2 High-level tasks to be planned
1. **Carbon sequestration model.** A model will be developed to estimate how much carbon dioxide a
   forest *and its associated product pools* will sequester over time, and to identify which
   management plan will be most effective for carbon sequestration.
2. **Decision model.** A decision model will be developed that will balance carbon sequestration
   against other forest values: conservation, recreation, cultural/spiritual values, biodiversity,
   water, and economic returns.
3. **Application.** The models will be applied to several forest types, and at least one forest will
   be chosen where harvesting *should* be part of the management plan. A 100-year carbon
   sequestration estimate will be produced, a management plan will be recommended and justified,
   and a transition strategy will be designed for the case where the best plan extends the rotation
   interval by 10 years.
4. **Public communication.** A newspaper article will explain why harvesting will be included in a
   chosen forest's plan and will address community concerns.

### 1.3 Key questions the future models should be able to answer
- What management plans will the decision model suggest?
- Under what conditions will a forest be left uncut?
- Will there be universal transition points between management plans?
- How will specific forest characteristics and location shift those transition points?

### 1.4 Scope note
The problem will be treated as a *forest-level planning* problem, not a plot-level measurement
exercise. The plan will span a 100-year planning horizon and will consider multiple representative
forest archetypes rather than a single forest.

---

## 2. Objectives and Subproblems

### 2.1 Overall objective
To produce a defensible, transparent, and reusable modeling framework that (a) quantifies
carbon sequestration flows of forests and wood products over a long horizon and (b) supports
management decisions that trade carbon against other values.

### 2.2 Subproblem decomposition

| ID | Subproblem | Purpose | Intended output (planning level) |
|----|-----------|---------|----------------------------------|
| SP1 | Biomass growth dynamics | Describe how standing-tree carbon will accumulate over time | A growth sub-model specification |
| SP2 | Harvest and regeneration dynamics | Describe how harvesting and replanting will move carbon between pools | A harvest-scheduling sub-model specification |
| SP3 | Product pool and end-of-life accounting | Track carbon in short-lived and long-lived wood products and disposal | A product-pool sub-model specification |
| SP4 | Carbon accounting aggregation | Combine pools into net CO2e sequestered over the horizon | A carbon-balance formulation |
| SP5 | Multi-objective decision model | Combine carbon with conservation, recreation, culture, economics | A decision/optimization formulation |
| SP6 | Transition-point analysis | Identify when plans switch (e.g., cut vs. no-cut) | A comparative/parametric analysis design |
| SP7 | Location and characteristic sensitivity | Determine how climate, species, and site shift transitions | A scenario-parameterization plan |
| SP8 | Communication artifact | Translate findings into a newspaper article | A communication outline (to be written later) |

### 2.3 Deliverables that the future solver will produce
- A defined carbon sequestration model with explicit state variables and flows.
- A decision model with stated objective(s) and constraints.
- A set of forest archetypes and a recommended plan for at least one.
- A 100-year sequestration projection for that forest.
- A transition strategy for a +10-year rotation extension.
- A newspaper article draft.
- Validation, sensitivity, and limitation discussion.

---

## 3. Assumptions

Assumptions will be grouped by category. Each will be recorded with (i) the reason it will be
needed, (ii) the justification that will be offered, and (iii) how it will later be validated or
relaxed. **No assumption evaluation is performed here.**

### 3.1 System-boundary assumptions (to be adopted)
- A1. The system boundary will include standing biomass, soil carbon (at least a simplified
  surface layer), and harvested wood product (HWP) pools.
- A2. Carbon transfers to the atmosphere from decomposition and combustion will be counted as
  emissions; sequestration will be reported as net CO2e over the horizon.
- A3. The planning horizon will be 100 years, potentially with a terminal-value convention for
  carbon still stored at year 100.

### 3.2 Biological/ecological assumptions (to be adopted)
- A4. Tree growth will follow a smooth, saturating growth function that will be parameterized per
  species/site class.
- A5. Regeneration will occur deterministically after harvest, with a fixed establishment delay.
- A6. Disturbance (fire, pest, storm) will be handled as an exogenous scenario parameter rather
  than an endogenous stochastic process in the first framework.

### 3.3 Product and economic assumptions (to be adopted)
- A7. Harvested wood will be allocated to product classes with different lifetimes (e.g.,
  short-lived paper, medium-lived panels, long-lived sawn timber).
- A8. Product decay will be modeled with class-specific retention functions.
- A9. Prices/costs will be treated as exogenous parameters, used only to express the economic
  dimension of the trade-off unless a substitution module is later added.

### 3.4 Decision and preference assumptions (to be adopted)
- A10. Non-carbon values (conservation, recreation, cultural) will be represented as commensurable
  utility/indicator terms or as constraints, with weights that will be treated as policy inputs.
- A11. The forest manager will be assumed to be a rational planner maximizing a weighted objective
  subject to sustainability constraints.

### 3.5 Justification and future validation approach
Each assumption will be justified from first principles or from the need to keep the model
tractable. Later validation will: (i) replace the most sensitive assumptions with data-driven or
stochastic versions, (ii) test whether conclusions will change under alternative formulations, and
(iii) document which assumptions dominate the results. Assumption robustness will be a required
part of the final write-up.

---

## 4. Data Processing Plan

### 4.1 Data sources that will be sought
- Public forest inventory data (e.g., national forest inventory summaries, species-level yield
  tables).
- Ecological/forestry literature for growth parameters, biomass expansion factors, and root-to-shoot
  ratios.
- IPCC-style guidance for carbon fraction of biomass and HWP accounting conventions.
- Climate and site data (temperature, precipitation, soil class) for the forest archetypes.
- Regional socio-economic context for the communication section.

### 4.2 Preprocessing steps that will be applied
1. **Inventory and cataloguing** of every dataset: provenance, units, spatial/temporal resolution.
2. **Unit harmonization** to common units (biomass in tC or tC/ha; carbon flows in tCO2e).
3. **Schema normalization** into a table format with consistent identifiers per species/site.
4. **Missing-value strategy**: documented imputation or explicit exclusion, never silent dropping.
5. **Quality screening**: outlier detection, plausibility bounds, and duplicate removal.
6. **Reproducible ingestion**: raw data will be left untouched; all transformations will be scripted
   and versioned.

### 4.3 Feature construction that will occur
- Derived growth-curve parameters per archetype (e.g., asymptote, growth rate, inflection).
- Biomass expansion factors linking merchantable volume to total tree carbon.
- Product-pool allocation fractions and decay-rate constants.
- Site/climate covariates that will serve as sensitivity parameters.
- Composite non-carbon value indices (recreation access, conservation score, cultural weight) as
  ordinal/scaled indicators.

### 4.4 Data usage strategy
- A small set of clearly documented **forest archetypes** (e.g., fast-growing plantation,
  temperate mixed hardwood, boreal slow-growth, tropical humid) will be defined to span the
  characteristic space.
- Data will be used to parameterize rather than to curve-fit a single forest.
- Where data will be unavailable, a documented literature-based default range will be used, and
  that range will feed directly into the sensitivity analysis.

---

## 5. Candidate Model Framework

### 5.1 Modeling philosophy
The framework will be a layered, modular pipeline: a bio-physical carbon engine (Subproblems
SP1–SP4) feeding a decision layer (SP5) whose behavior will be studied via parametric scenario
analysis (SP6–SP7). Modularity will let each layer be validated and replaced independently.

### 5.2 Layer A — Forest carbon dynamics (SP1–SP3)

**Candidate models (to be compared):**
- **A-1 Continuous stand-level growth model.** A saturating function (e.g., logistic or
  Chapman–Richards-type) describing standing carbon C(t) under no harvest.
- **A-2 Cohort/age-class model.** Discrete age cohorts advanced yearly with harvest and
  regeneration operators; suited to even-aged management.
- **A-3 State-and-flow carbon-pool model.** Compartmental pools (biomass, litter/soil, products,
  atmosphere) with yearly transfer rates; a system-dynamics style formulation.

**State variables (planned):** standing biomass carbon, soil/litter carbon, wood-product carbon by
class, cumulative atmospheric transfer, age/cohort structure.

**Mathematical ideas that will be used:** ordinary difference/differential equations,
compartmental mass balance, parameterized growth curves, retention/decay kernels.

**Advantages:** transparent, parameter-light, interpretable.
**Limitations:** simplified disturbance and soil processes; limited spatial detail.

### 5.3 Layer B — Harvest scheduling (SP2)
- Candidate methods: rotation-age parameterization, harvest-intensity fraction, and (later) an
  optimization over harvest timing.
- Mathematical ideas: decision variables for harvest time/amount; recurrence relations for
  regeneration; constraints on sustainability (e.g., non-declining carbon stock or volume).

### 5.4 Layer C — Product pools and substitution (SP3)
- Candidate model: multi-class decay model with first-order (exponential) retention functions and
  optional displacement/substitution credits.
- Mathematical ideas: linear decay operators; convolution of harvest flows with retention kernels.

### 5.5 Layer D — Multi-objective decision model (SP5)

**Candidate models (to be compared):**
- **D-1 Weighted-sum / utility model.** Maximize a weighted sum of carbon, economics, and
  non-carbon values.
- **D-2 Multi-attribute utility / analytic hierarchy style scoring.** Structurally score
  alternatives against weighted criteria.
- **D-3 Constrained optimization.** Maximize carbon subject to minimum levels of conservation,
  recreation, and cultural values (or vice versa).
- **D-4 Pareto/efficient-frontier analysis.** Generate a trade-off frontier between carbon and
  non-carbon objectives rather than a single scalar optimum.

**Decision variables (planned):** rotation length, harvest intensity, fraction of area under each
regime, regeneration choice.
**Constraints (planned):** non-declining carbon, minimum habitat/cultural protection, budget, and
land-availability limits.
**Advantages/limitations:** weighted-sum models will be simple and interpretable but will require
weight elicitation (a known subjectivity); Pareto analysis will avoid arbitrary weights but will
produce a set rather than a single recommendation.

### 5.6 Layer E — Transition and universality analysis (SP6–SP7)
- A parametric study will sweep key parameters (growth rate, decay rates, discount rate, value
  weights, site productivity) to locate **transition points** where the recommended plan will
  switch (e.g., from harvest to no-cut).
- The analysis will test whether these transitions will be *universal* (same across forests) or
  *local* (dependent on characteristics/location), which directly addresses the problem's key
  questions.

### 5.7 Cross-cutting mathematical toolkit (to be planned, not applied)
Difference/differential equations, compartmental mass balance, logistic/Chapman–Richards growth,
linear/nonlinear programming, multi-objective optimization, Pareto analysis, sensitivity/OAT and
global sensitivity methods.

---

## 6. Implementation Roadmap

### 6.1 Planned module structure
```
modules/
  data_ingest      # load, catalog, clean, harmonize units
  growth           # Layer A growth model(s) and parameters
  harvest          # Layer B scheduling operators
  products         # Layer C product pools and decay
  carbon_balance   # SP4 aggregation to net CO2e
  decision         # Layer D objective/constraint assembly
  scenarios        # archetype and parameter sweep drivers
  reporting        # tables/figures for the final write-up
```

### 6.2 Planned workflow (ordered steps)
1. Freeze the assumption list and system boundary.
2. Assemble and clean the parameter dataset and archetype definitions.
3. Implement the growth sub-model and verify against no-harvest baselines.
4. Add harvest and regeneration operators; verify mass balance across pools.
5. Add product pools and decay; verify carbon conservation through the full chain.
6. Implement the carbon-balance aggregation (SP4).
7. Implement one decision model (start with weighted-sum, then add constrained/Pareto variants).
8. Run the scenario sweep for the archetypes and locate candidate transitions.
9. Select a forest where harvesting enters the plan and generate the 100-year projection.
10. Design the +10-year rotation-extension transition strategy.
11. Run validation and sensitivity analyses.
12. Write the solution, summary sheet, and newspaper article.

### 6.3 Algorithms that will be used
Numerical integration of growth curves; recurrence evaluation for cohorts; linear/quadratic
programming for the decision layer; grid/parametric sweeps for transitions; OAT and variance-based
sensitivity sampling.

### 6.4 Engineering practices that will be enforced
- Reproducible scripts with fixed seeds and versioned inputs.
- Unit tests for mass-balance conservation.
- Clear separation between parameters, model logic, and scenario drivers.
- Logging of every scenario run for traceability.

---

## 7. Validation Strategy

### 7.1 Internal consistency checks
- **Mass-balance audit:** carbon leaving biomass will be shown to equal carbon entering
  atmosphere + products + soil sinks.
- **Boundary tests:** zero-harvest and full-harvest extremes will be checked for expected monotone
  behavior.
- **Dimensional/unit checks** throughout the pipeline.

### 7.2 Benchmarking against external references
- Growth curves will be benchmarked against published yield tables.
- Carbon fractions and HWP decay conventions will be benchmarked against IPCC-style guidance.
- Decision outcomes will be sanity-checked against documented real-world management regimes.

### 7.3 Scenario and sensitivity analysis
- **One-at-a-time (OAT)** sweeps on growth rate, decay constants, discount rate, and value weights.
- **Global sensitivity** (e.g., variance-based sampling) to rank parameter influence.
- **Structural sensitivity:** compare weighted-sum vs. constrained vs. Pareto decision models to
  see whether recommendations will be robust to model choice.

### 7.4 Robustness of the transition points
The location of transition points will be reported together with the parameter ranges over which
they will persist, distinguishing "universal" from "local" transitions.

### 7.5 Planned evaluation metrics (to be reported later)
- Net CO2e sequestered over 100 years (per ha and total).
- Peak standing carbon and time-to-peak.
- Product-pool carbon at horizon.
- Non-carbon value indices by scenario.
- Robustness/uncertainty bands on each of the above.
- Stability of recommended plan across model variants.

---

## 8. Expected Result Interpretation

This section anticipates *how* future results will be read; it does **not** state any results.

- The carbon model will likely reveal a tension: frequent harvest will build product pools quickly
  but will suppress standing-carbon accumulation, while long rotations will maximize standing
  carbon but delay product benefits.
- The decision model will likely produce **regime regions** in parameter space: a no-cut region
  where non-carbon values or slow growth will dominate, and a harvest region where fast growth and
  strong product markets will dominate.
- Transition points will be interpreted as the boundaries between these regions. Whether a
  transition will be called *universal* will depend on how stable it will be across archetypes.
- Location and characteristics will be interpreted as covariates that will shift the transitions —
  e.g., higher productivity or higher decay credits will push the boundary toward harvesting.
- The chosen forest will be justified by showing that harvesting will keep the total system carbon
  (including products) competitive with or better than no-cut, while also serving other values.
- The +10-year rotation extension will be framed as a management transition with phased schedules,
  stakeholder communication, and interim income/carbon bridges.

---

## 9. Limitations and Improvements

### 9.1 Anticipated limitations
- Simplified soil-carbon and disturbance dynamics will bound realism.
- Value weights in the decision model will introduce subjectivity.
- Exogenous prices and product lifetimes will limit economic fidelity.
- Archetype-based parameterization will not capture within-forest heterogeneity.
- The 100-year horizon and terminal-value convention will influence rankings.

### 9.2 Planned improvements / future work
- Add stochastic disturbance and climate-driven growth scenarios.
- Introduce spatially explicit or landscape-level scheduling.
- Add substitution/displacement credits and market feedback.
- Elicit weights via structured stakeholder methods (e.g., AHP or deliberative workshops).
- Extend the decision model to robust/stochastic optimization under deep uncertainty.
- Expand archetype coverage and validate against additional real-world case forests.

### 9.3 Reporting commitments
- Every assumption, parameter source, and model variant will be documented.
- Uncertainty will be reported alongside every headline number.
- The newspaper article will communicate trade-offs honestly and will explicitly address
  community concerns (jobs, habitat, aesthetics, culture).

---

## Appendix A — Planned Artifacts Checklist

- [ ] Assumption register (with justification + validation method).
- [ ] Data catalog and preprocessing log.
- [ ] Growth/harvest/product sub-model specifications.
- [ ] Carbon-balance formulation.
- [ ] Decision model formulations (weighted-sum, constrained, Pareto).
- [ ] Archetype definition table.
- [ ] Scenario/sensitivity run plan.
- [ ] 100-year projection plan for the chosen forest.
- [ ] +10-year rotation-extension transition plan.
- [ ] Newspaper article outline.
- [ ] Validation and limitations memo.

## Appendix B — Planning-Level Open Questions (to be resolved later)

1. Will soil carbon be modeled explicitly or as a simplified sink?
2. Will substitution credits be included in the primary framework or reserved for extensions?
3. Will the decision model use a single scalar objective or a Pareto frontier as its primary output?
4. Which archetypes will be reported in depth vs. summarized?
5. Will the terminal value at year 100 be discounted, carried, or excluded?

---

*End of planning draft. No model was solved, no data was analyzed, and no results were computed in
the preparation of this document.*
