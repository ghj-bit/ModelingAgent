# Are We Heading Towards a Thirsty Planet?
## Modeling Blueprint Draft (Planning Document, Not a Solution)

**Problem ID:** 2016_Are_we_heading
**Source:** ICM 2016, Problem E
**Document type:** Initial modeling plan / roadmap only. No data has been analyzed, no model has been fitted, and no results are reported here. All sections are written in future-oriented language and describe what *will* be done in later stages.

---

## 1. Problem Background and Restatement

The United Nations reports that approximately 1.6 billion people face water scarcity, and that water use is growing at roughly twice the rate of population growth. Water scarcity is understood to arise from two distinct but interacting mechanisms: **physical scarcity** (insufficient natural supply relative to demand) and **economic scarcity** (inadequate management, infrastructure, and institutions). Climate change and demographic growth are expected to amplify both.

The International Clean Water Movement (ICM) asks the modeling team to improve access to clean, fresh water. The problem decomposes into a request for:

- a **quantitative characterization** of a region's ability to supply clean water under dynamic supply and demand,
- a **diagnosis** of the drivers of scarcity in a selected heavily/moderately water-stressed region,
- a **projection** of the region's water situation roughly 15 years ahead, including consequences for citizens' lives,
- an **intervention plan** that addresses all identified drivers, with an assessment of its ripple effects on the region and its neighbors,
- a **re-projection** under the intervention plan, to judge whether susceptibility to scarcity can be reduced and when scarcity could become critical,
- a **20-page report** communicating the model, the no-intervention baseline, the intervention, and model strengths and weaknesses.

This blueprint does not attempt to answer these questions. It defines the modeling architecture, data plan, implementation roadmap, and validation strategy that a subsequent solving phase will execute.

### Framing notes for later stages

- The problem is fundamentally a **coupled human–natural system** problem: a hydrological supply side, a socioeconomic demand side, and a policy feedback loop.
- The requested deliverable is both **descriptive** (explain current scarcity) and **prescriptive** (design and evaluate intervention), so the framework must support *counterfactual simulation*, not only curve-fitting.
- The "15 years" horizon implies a **medium-term projection**, which favors scenario-based trajectory modeling over long-run equilibrium economics.

---

## 2. Objectives and Subproblems

### 2.1 Primary objective

To construct a transparent, reproducible, and policy-relevant modeling framework that (a) measures a region's capacity to provide clean water, (b) explains the social and environmental drivers of that capacity, and (c) evaluates interventions under a 15-year horizon.

### 2.2 Subproblems (mapped to the ICM tasks)

| ID | Subproblem | Nature | Planned output |
|----|-----------|--------|----------------|
| SP1 | Define and formalize a **Water Access / Scarcity Index** combining supply and demand | Conceptual + quantitative | A composite index definition and its component taxonomy |
| SP2 | Build a **dynamic supply model** (natural + engineered freshwater availability) | Mechanistic/stochastic | Governing equations + calibration plan |
| SP3 | Build a **dynamic demand model** (domestic, agricultural, industrial, environmental) | Structural/statistical | Demand decomposition + drivers |
| SP4 | **Region selection and diagnosis** of scarcity causes (social + environmental) | Analytical | Selection criteria + diagnostic framework |
| SP5 | **15-year baseline projection** (no intervention) and citizen-impact translation | Scenario simulation | Scenario protocol + impact indicators |
| SP6 | **Intervention design** across all drivers | Optimization + design | Candidate intervention taxonomy + evaluation criteria |
| SP7 | **Re-projection under intervention** and criticality-timing detection | Scenario simulation | Threshold definitions + comparison protocol |
| SP8 | **Validation and sensitivity** across all model components | Methodological | Metric suite + experiment matrix |
| SP9 | **Reporting and communication** architecture | Structural | Report outline + figure/table plan |

### 2.3 Deliverables (planning level)

- A documented, modular model specification (equations, variables, parameters).
- A data dictionary and preprocessing pipeline specification.
- A scenario matrix (baseline vs. intervention families).
- A validation and sensitivity analysis protocol.
- A report skeleton aligned with the 20-page requirement.

### 2.4 Success criteria (to be *evaluated* in later stages, not now)

- The index must be interpretable and decomposable into physical vs. economic scarcity components.
- Projections must be reproducible from documented inputs.
- Intervention evaluation must be comparable across alternatives on a common metric.
- Assumptions must be explicitly traceable to sensitivity results.

---

## 3. Assumptions

The following assumptions are *proposed* as working hypotheses. Each will be revisited and stress-tested during validation (Section 7).

### 3.1 System boundary and scale assumptions

1. **Spatial unit:** Modeling will be conducted at the **national or sub-national river-basin scale**, because water is managed within hydrological and administrative boundaries. The final region will be chosen from the UN water-scarcity map (heavily or moderately overloaded).
2. **Temporal resolution:** Annual timesteps will be the default, with monthly disaggregation *only if* seasonality proves material to scarcity-criticality timing.
3. **Horizon:** A 15-year projection horizon will be primary; a 30-year extension may be run for sensitivity to long-run climate signals.

### 3.2 Supply-side assumptions

4. **Renewable freshwater supply** is bounded by precipitation minus evapotranspiration, adjusted by surface storage and aquifer recharge; groundwater will be treated as a depletable stock rather than an infinite flow.
5. **Non-renewable (fossil) groundwater** withdrawal will be modeled as a drawdown term with a finite reserve, because ignoring it would understate physical scarcity.
6. **Climate effects** will be represented through scenario ranges on precipitation/temperature rather than a single deterministic path.

### 3.3 Demand-side assumptions

7. **Demand is decomposable** into domestic, agricultural, industrial, and environmental-requirement components, each with distinct drivers.
8. **Per-capita domestic demand** will be treated as income- and urbanization-dependent, within documented bounds.
9. **Agricultural demand** will be modeled as a function of irrigated area, cropping intensity, and irrigation efficiency, acknowledging trade-offs with food security.
10. **Price and policy responses** are exogenous in the baseline but endogenous (feedback) under intervention scenarios.

### 3.4 Data and modeling assumptions

11. **Data heterogeneity:** National statistics from different sources will be assumed commensurable after unit harmonization and documented imputation.
12. **Stationarity limitation:** Historical relationships will be assumed *locally* stable for short-horizon projection, with explicit acknowledgment that this is a key weakness under regime change.
13. **No free lunch:** Interventions will be assumed to carry capital, energy, and environmental costs; no intervention is treated as costless.

### 3.5 Justification and future validation of assumptions

- Each assumption above will be tagged with a **rationale**, a **plausible falsifier**, and a **validation route** (cross-source comparison, out-of-sample backtest, or expert/stakeholder review).
- Assumptions identified as high-impact-low-confidence will be promoted to **primary sensitivity parameters**.

---

## 4. Data Processing Plan

> No data will be analyzed in this planning phase. This section specifies *how* data will be obtained, cleaned, and structured later.

### 4.1 Anticipated data sources (to be confirmed)

- **AQUASTAT (FAO):** withdrawal by sector, renewable freshwater resources, irrigation.
- **World Resources Institute (Aqueduct):** baseline water stress, variability, drought risk.
- **UN / World Bank / UNEP:** population, urbanization, GDP, sanitation access, health indicators.
- **The World's Water / Pacific Institute:** governance and infrastructure proxies.
- **Climate sources (e.g., IPCC scenario ranges, CRU/GPCC-style gridded climate):** precipitation and temperature.
- **Geological/hydrogeological references:** aquifer characteristics and recharge estimates.
- **National statistical yearbooks:** region-specific calibration data.

### 4.2 Preprocessing pipeline (planned steps)

1. **Ingestion and provenance logging:** record source URL, vintage year, spatial resolution, and license for every series.
2. **Spatial harmonization:** reconcile national vs. basin vs. gridded units onto a single spatial key.
3. **Temporal harmonization:** align to a common annual (optionally monthly) axis; document interpolation rules.
4. **Unit normalization:** convert all volumes to km³/year and all per-capita terms to m³/person/year.
5. **Missing-data strategy:** prefer authoritative fills; otherwise use documented interpolation/regression imputation with uncertainty flags. Never silently drop.
6. **Outlier and consistency checks:** cross-validate totals (e.g., sectoral withdrawals vs. reported totals); flag reconciliation gaps.
7. **Quality tiering:** label each series as *primary*, *derived*, or *proxy* to control downstream weighting.

### 4.3 Feature construction (planned)

- **Supply features:** renewable freshwater per capita, storage capacity, recharge, variability index.
- **Demand features:** sectoral withdrawal shares, withdrawal intensity per unit GDP, irrigation efficiency.
- **Stress features:** withdrawal-to-availability ratio, depletion rate, seasonal gap.
- **Socioeconomic features:** population growth, urbanization, income, sanitation/health coverage.
- **Governance/infrastructure features:** loss rates, treatment coverage, institutional proxies.
- **Composite features:** constructed indices for physical scarcity and economic scarcity separately.

### 4.4 Data usage strategy

- **Calibration set:** historical record for the selected region.
- **Validation set:** held-out recent years and/or a *different* region for cross-region transfer tests.
- **Scenario inputs:** climate and demographic scenario ranges, not point estimates.
- **Traceability:** every model input will map to a provenance record so results can be audited.

---

## 5. Candidate Model Framework

The framework will be **modular and layered**, so each component can be validated independently and swapped without rebuilding the whole system.

### 5.1 Layer A — Scarcity/access index (SP1)

- **Candidate approaches:**
  - *Composite indicator* (normalized component aggregation, e.g., weighted or geometric mean) with explicit weights.
  - *Ratio-based hydrological indicators* (withdrawal-to-availability, Falkenmark-style per-capita thresholds) as interpretable anchors.
  - *Multi-criteria decision analysis* if stakeholder weighting is emphasized.
- **Key variables:** availability per capita, withdrawal ratio, infrastructure/access coverage, variability.
- **Advantages:** transparent, communicable, decomposable.
- **Limitations:** weight subjectivity, aggregation masking of local heterogeneity — to be probed by sensitivity analysis.

### 5.2 Layer B — Dynamic supply model (SP2)

- **Candidate approaches:**
  - *Water-balance / mass-balance model* (inflows, outflows, storage, recharge, depletion).
  - *Stock-and-flow / system-dynamics* representation enabling feedback (a natural fit for the policy loop).
  - *Stochastic inflow generator* to represent climate variability.
- **Mathematical ideas:** conservation equations, reservoir/storage difference equations, autoregressive or scenario-driven climate inputs.
- **Advantages:** physically interpretable, supports depletion realism.
- **Limitations:** data-hungry; sub-grid processes must be lumped.

### 5.3 Layer C — Dynamic demand model (SP3)

- **Candidate approaches:**
  - *Structural decomposition* of demand into sectoral drivers.
  - *Regression / econometric demand functions* (income, price, population, efficiency elasticities).
  - *System-dynamics feedback* where demand responds to supply stress and policy.
- **Mathematical ideas:** coupled difference/differential equations, elasticity-based response functions.
- **Advantages:** links water to demography and economics as the problem requires.
- **Limitations:** elasticity estimation uncertainty; structural breaks.

### 5.4 Layer D — Coupled simulation and projection engine (SP4–SP7)

- **Candidate approaches:**
  - *Coupled supply–demand dynamical system* advanced in annual steps.
  - *Scenario simulation* (baseline vs. intervention families).
  - *Optimization layer* (e.g., linear/nonlinear programming or multi-objective optimization) to allocate interventions under budget/equity constraints.
- **Mathematical ideas:** state–space recursion, scenario parameter sets, objective functions balancing scarcity reduction, cost, equity, and ecological constraints.
- **Advantages:** enables counterfactuals required by Tasks 3–5.
- **Limitations:** compounding uncertainty over the horizon; risk of over-precision.

### 5.5 Layer E — Impact translation (citizen effects)

- **Candidate approaches:** mapping scarcity index states to health/access/demographic indicators via documented relationships; qualitative-to-quantitative scoring where data is thin.
- **Advantages:** connects model output to human consequences the problem explicitly requests.
- **Limitations:** causal attribution uncertainty.

### 5.6 Why a coupled, scenario-based framework

The problem demands explanation *and* intervention evaluation. A single predictive model cannot deliver counterfactual policy analysis; therefore the plan favors a **system-dynamics core with an optimization overlay**, transparently coupled to the index layer.

---

## 6. Implementation Roadmap

> No code will be written or executed in this phase. This is the planned engineering sequence.

### 6.1 Proposed module structure

- `data/ingest` — source loaders and provenance registry.
- `data/clean` — harmonization, imputation, quality tiering.
- `features/build` — feature and index construction.
- `models/supply` — supply dynamics.
- `models/demand` — demand dynamics.
- `models/coupling` — simulation engine.
- `models/optimize` — intervention optimization.
- `eval/metrics` — validation metrics.
- `eval/sensitivity` — sensitivity and scenario experiments.
- `report/figures` — visualization and report assets.

### 6.2 Workflow sequence (planned)

1. **Specification freeze:** formalize variables, equations, and index definition (Sections 3–5).
2. **Data assembly:** run the Section 4 pipeline; produce a data dictionary.
3. **Component calibration:** fit/parameterize supply and demand layers independently.
4. **Coupling:** integrate into the simulation engine; verify mass balance and conservation.
5. **Baseline scenario:** define and run the no-intervention trajectory protocol.
6. **Region selection finalization:** apply explicit criteria to choose the focal region.
7. **Intervention design:** enumerate intervention families; encode costs and constraints.
8. **Intervention simulation:** run re-projections and comparisons.
9. **Validation and sensitivity:** execute the Section 7 matrix.
10. **Reporting:** assemble the 20-page structure.

### 6.3 Reproducibility requirements (planned)

- Fixed random seeds and version-pinned dependencies.
- Configuration files for every scenario.
- Logged provenance for each output (extending the existing `logs/` area).
- One-command regeneration of figures from raw inputs.

### 6.4 Risk register (planning level)

| Risk | Impact | Planned mitigation |
|------|--------|-------------------|
| Sparse/heterogeneous data | High | Quality tiering, explicit uncertainty flags |
| Over-parameterization | Medium | Prefer interpretable structure; regularization; sensitivity |
| Regime change invalidating history | High | Scenario ranges; structural-break diagnostics |
| Optimizer finding unrealistic plans | Medium | Constraint feasibility review; stakeholder plausibility check |
| Precision overreach in projections | High | Report ranges, not point forecasts |

---

## 7. Validation Strategy

### 7.1 Evaluation metrics (planned)

- **Index layer:** internal consistency, rank stability, decomposition sensitivity.
- **Supply/demand layers:** out-of-sample error (e.g., normalized RMSE/MAE), mass-balance residual, directional accuracy.
- **Projection:** backtest on historical windows; scenario plausibility bounds.
- **Intervention optimization:** cost-effectiveness, feasibility, robustness across scenarios.
- **Overall:** coverage of the ICM task requirements and traceability of every claim to a model output.

### 7.2 Validation methods (planned)

1. **Hold-out temporal backtesting** on the historical record.
2. **Cross-region transfer test:** calibrate on one region, test on another of similar class.
3. **Cross-source triangulation** using independent datasets.
4. **Conservation/consistency audits** (supply–demand closure).
5. **Expert/stakeholder plausibility review** of scenarios and interventions.
6. **Reproducibility check** from raw inputs to reported figures.

### 7.3 Sensitivity analysis (planned)

- **Local (one-at-a-time)** sensitivity on high-impact parameters.
- **Global (variance-based, e.g., Sobol-style) sensitivity** where dimensionality permits.
- **Scenario analysis** over climate and demographic ranges.
- **Structural sensitivity:** compare alternative index weightings and alternative model forms.
- **Criticality-timing sensitivity:** test how the projected scarcity-critical year shifts under parameter ranges.

### 7.4 Uncertainty communication

Results will be reported as **ranges and scenario bands**, with explicit statements of which conclusions are robust and which are parameter-dependent. The 15-year projection will be framed as conditional on stated assumptions, not as a forecast.

---

## 8. Expected Result Interpretation

> No results exist yet. This section defines *how* results will be interpreted once produced.

### 8.1 Interpreting the index

- The composite index will be read as a **relative** measure across regions and time, not an absolute physical law.
- A physical-vs-economic decomposition will distinguish whether scarcity is a *nature* problem or a *management/infrastructure* problem for the selected region, directly addressing the ICM framing.

### 8.2 Interpreting projections

- Baseline trajectories will be interpreted as **conditional scenarios**, answering "if current drivers persist."
- Criticality timing will be reported as a range with the drivers that most control it.
- Citizen-impact translation will be presented qualitatively where data supports it and cautiously quantified elsewhere.

### 8.3 Interpreting interventions

- Interventions will be compared on a common multi-criteria scale (scarcity reduction, cost, equity, ecological side effects, time-to-effect).
- Strengths and weaknesses of each intervention family will be stated explicitly, including spillover effects on neighboring regions.
- The re-projection will determine whether the region can move from a *stressed* to a *less susceptible* regime and under what conditions.

### 8.4 Interpreting model quality

- Strengths and weaknesses will be reported alongside results, as ICM Task 6 requires.
- Claim strength will be matched to evidence strength: robust findings stated plainly; fragile findings flagged.

---

## 9. Limitations and Improvements

### 9.1 Anticipated limitations (to be documented, not hidden)

- **Data limitations:** sparsity, differing vintages, and national-level aggregation may mask sub-national scarcity hotspots.
- **Model-form limitations:** lumped hydrological representations omit fine-grained ecological dynamics.
- **Behavioral limitations:** economic/demographic response functions may not capture tipping points or institutional shocks.
- **Projection limitations:** medium-term projections accumulate uncertainty; stationarity assumptions may fail under climate change.
- **Optimization limitations:** intervention plans may be idealized relative to political/implementation realities.
- **Ethical/equity limitations:** aggregate metrics can hide distributional inequities unless explicitly tracked.

### 9.2 Planned improvements (future iterations)

1. **Finer spatial resolution** via basin-level or gridded data where available.
2. **Seasonality and extremes:** move from annual to monthly or event-based modeling.
3. **Endogenous policy feedback:** allow governance and investment to respond to scarcity dynamically.
4. **Stochastic ensemble projections** replacing single scenario paths.
5. **Distributional analysis** of who bears scarcity within a region.
6. **Cross-sector trade-off modeling** (water–food–energy nexus).
7. **Stakeholder calibration** of index weights and intervention priorities.
8. **Open reproducibility packaging** for independent replication.

### 9.3 Scope discipline

This document is deliberately a **blueprint**. The subsequent solving phase will execute the plan, generate the actual quantitative results, and produce the 20-page report. Until then, no numerical conclusions should be attributed to this plan.

---

*End of modeling blueprint draft.*
