# Modeling Blueprint Draft — MM-Bench 2018_E
### Climate Change, State Fragility, and Intervention Planning

> **Document status:** Initial modeling *plan draft* (roadmap only).
> **Scope:** This document designs a plan for future modeling. It contains no computed
> results, no executed analysis, no fitted models, and no final conclusions.
> **Problem ID:** `2018_E`  |  **Source:** MM-Bench (2018)
> **Language convention:** Future-oriented ("will", "is planned to", "is expected to").
> **Data note:** The staged `data/` directory is currently empty and the dataset
> definition is an empty schema (`{}`). Accordingly, the Data Processing Plan
> (Section 4) specifies the datasets that *will be acquired/assembled* and the
> staged-data handling that *will be applied once files exist*.

---

## 1. Problem Background and Restatement

### 1.1 Background (as given)
Climate change effects — increased droughts, shrinking glaciers, shifting animal
and plant ranges, and sea-level rise — are already being realized and vary by region.
The IPCC indicates that net damage costs of climate change are likely significant.
These effects may weaken or break down social and governmental structures, and
destabilized governments can produce *fragile states*. A fragile state is one whose
government cannot, or chooses not to, provide basic essentials to its people.
Fragility increases a population's vulnerability to climate shocks (natural
disasters, decreasing arable land, unpredictable weather, rising temperatures), and
non-sustainable environmental practices, migration, and resource shortages commonly
aggravate weakly governed states. Environmental stress alone need not trigger
violent conflict, but evidence suggests it *enables* conflict when combined with weak
governance and social fragmentation, potentially producing a spiral of violence along
latent ethnic and political divisions.

### 1.2 Restatement of the Modeling Problem
The task is to design a modeling framework that (a) quantifies a country's
**fragility** while (b) simultaneously measuring the **impact of climate change**,
including both **direct** effects and **indirect** effects mediated through other
factors/indicators. The framework is expected to:
- classify states as **fragile**, **vulnerable**, or **stable**;
- attribute how climate change increases fragility (direct vs. indirect pathways);
- support retrospective analysis of a highly fragile state;
- support forward projection and **tipping-point** detection for a non-top-10 state;
- support evaluation of **state-driven interventions** and their **cost**; and
- be assessed for **scale transferability** to sub-national (city) and supra-national
  (continent) "states," with proposed modifications.

### 1.3 Native Requirements to Preserve
- Reference to the **Fragile State Index (FSI)** (`http://fundforpeace.org/fsi/data/`)
  as the external benchmark for the "top 10 most fragile states."
- The three-way state classification (fragile / vulnerable / stable).
- Explicit treatment of **direct and indirect** climate-to-fragility pathways.
- A defined notion of a **tipping point** and a method to **predict when** a country
  may reach it.
- An **intervention** analysis with an **estimated total cost**.
- A **scale-transferability** discussion (cities and continents).

---

## 2. Objectives and Subproblems

### 2.1 Overall Objective
To design a reproducible, data-grounded modeling framework that jointly measures
national fragility and climate-change impact, classifies state status, explains
direct/indirect climate pathways, projects future fragility and tipping points, and
quantifies intervention effects and costs.

### 2.2 Subproblems (mapped to native Tasks)

| ID | Subproblem | Native Task | Planned deliverable |
|----|------------|-------------|---------------------|
| S1 | Fragility–climate joint model with three-way classification and direct/indirect pathway attribution | Task 1 | Model specification, variable/indicator scheme, classification rule |
| S2 | Retrospective case analysis of one top-10 FSI fragile state and counterfactual "less fragile" scenario | Task 2 | Case-study protocol + counterfactual design |
| S3 | Forward fragility projection for a non-top-10 state, definitive-indicator identification, tipping-point definition & prediction | Task 3 | Projection + tipping-point detection protocol |
| S4 | Intervention portfolio design, effect estimation, and total-cost estimation | Task 4 | Intervention optimization specification + cost model |
| S5 | Scale transferability assessment and required model modifications | Task 5 | Scaling analysis protocol |

### 2.3 Deliverables (to be produced in later modeling rounds)
- A documented **fragility index / latent-state model** with climate coupling.
- A **classification** scheme with thresholds for fragile/vulnerable/stable.
- A **direct/indirect pathway decomposition** method.
- A **case-study narrative template** for Task 2.
- A **projection and tipping-point** methodology for Task 3.
- An **intervention optimization + costing** methodology for Task 4.
- A **scaling assessment** for Task 5.
- Reproducible code, config, and validation artifacts (planned, not yet built).

---

## 3. Assumptions

Each assumption below will be revisited in Section 7 validation.

### 3.1 Structural / Modeling Assumptions
1. **Fragility is a latent, multi-dimensional construct.** It will be treated as a
   continuous latent score (per country, per year) with classification thresholds,
   rather than as a purely binary label.
   *Justification:* the FSI is itself a composite; three-way classification requires a
   continuous underlying score.
   *Future validation:* threshold stability under re-specification and comparison to
   FSI category assignments.
2. **Climate variables influence fragility through both direct and mediated
   pathways.** A set of mediator variables (e.g., food/water security, economic
   capacity, migration) will carry indirect effects.
   *Justification:* the problem statement explicitly distinguishes direct and indirect
   means.
   *Future validation:* mediation analysis; comparison of total vs. direct effects.
3. **Near-term continuity / incremental change.** Over a planning horizon, most
   drivers will be assumed to evolve smoothly, with discontinuity modeled explicitly
   via threshold/regime mechanisms rather than assumed away.
   *Justification:* enables tractable projection and tipping-point analysis.
   *Future validation:* out-of-sample backtesting of projections.
4. **Comparative stability of governance and social-structure indicators over short
   horizons**, with climate as an amplifying stressor rather than a sole cause.
   *Justification:* consistent with the statement that environmental stress *enables*
   conflict under weak governance.
   *Future validation:* sensitivity to governance-data revisions and lags.

### 3.2 Data / Measurement Assumptions
5. **Cross-country comparability of composite indicators** will be taken as
   approximately valid after normalization and (where needed) harmonization.
   *Future validation:* rank-correlation checks against independent indices.
6. **Time alignment.** Annual indices, climate anomalies, and event datasets will be
   aligned to a common annual grid; sub-annual climate data will be summarized to
   annual hazard/ exposure statistics.
   *Future validation:* robustness to monthly vs. annual aggregation.
7. **Missingness is assumed to be non-structural but informative of coverage bias**;
   imputation will be explicit and documented.
   *Future validation:* comparison of complete-case vs. imputed results.

### 3.3 Scenario / Behavioral Assumptions (for Tasks 2–4)
8. **Counterfactuals will be model-based** ("no climate effect," "reduced exposure,"
   "intervention X") rather than observed, and will be stated explicitly as scenarios.
9. **Intervention responses will be modeled as effect functions on drivers** (e.g.,
   irrigation, early-warning, governance strengthening), with cost curves derived from
   documented unit costs; both effect and cost are assumed estimable with uncertainty.
   *Future validation:* expert elicitation + literature triangulation.

### 3.4 Scope Assumptions
10. **"State" = sovereign country** for Tasks 1–4; Section/Task 5 will treat the term
    as a scale parameter to be tested for cities and continents.

---

## 4. Data Processing Plan

> The staged `data/` folder is empty; the following specifies the datasets that
> **will be acquired** and the processing pipeline that **will be implemented** when
> data are staged. The empty dataset schema (`{}`) implies **no pre-defined variable
> contract**, so the pipeline will begin with schema definition and provenance
> logging.

### 4.1 Data Sources to Assemble
- **Fragility / country risk indices:** Fragile State Index (FSI) full series and its
  12 sub-indicators (cohesion, economic, political, social/cross-cutting), used as
  reference labels and/or benchmark features.
- **Governance & institutions:** World Bank Worldwide Governance Indicators (WGI);
  transparency/perception indices.
- **Socioeconomic & development:** World Bank / UN (GDP per capita, poverty,
  inequality, food and water security, urbanization, demographics).
- **Climate & environment:** gridded/reanalysis climate (temperature anomalies,
  precipitation variability, drought indices such as SPEI/SPI), glacier/sea-level
  indicators, arable-land change, ND-GAIN vulnerability/readiness.
- **Hazards & disasters:** EM-DAT or equivalent (event frequency, affected
  population, damages).
- **Conflict & displacement:** conflict-event datasets and displacement/migration
  statistics (optional mediators/outcomes).
- **Intervention cost references:** documented unit costs (per hectare irrigation,
  per capita early-warning, infrastructure cost benchmarks) for Section 6/Task 4.

### 4.2 Preprocessing Pipeline (planned)
1. **Schema definition & provenance manifest** for every staged file (source, URL,
   license, version/date, checksum).
2. **Entity reconciliation:** harmonize country identifiers (ISO-3), handle
   historical country changes and micro-states; define inclusion criteria.
3. **Time-grid alignment:** annual (or chosen) panel; document aggregation rules for
   sub-annual climate and event data.
4. **Unit and scale harmonization:** consistent units; log/level transforms decided
   per variable.
5. **Missing-data handling:** document missingness, apply and flag imputation
   (e.g., interpolation within country, model-based imputation, or masked exclusion);
   retain imputation flags for sensitivity analysis.
6. **Normalization / rescaling:** min–max, z-score, or rank normalization per
   selected aggregation scheme (fixed reference windows to avoid drift).
7. **Outlier & regime-break screening:** flag structural breaks and extreme events
   for separate treatment.
8. **Versioning:** immutable raw layer + reproducible processed layer.

### 4.3 Feature Construction (planned)
- **Climate-stress features:** trend, anomaly, variability, drought severity/duration,
  compound-event indicators.
- **Exposure & sensitivity features:** agricultural dependence, water stress,
  population pressure, infrastructure fragility.
- **Adaptive-capacity features:** governance quality, economic resources, service
  provision.
- **Lag & window features:** cumulative and lagged climate stress (multi-year).
- **Interaction features:** climate-stress × governance-weakness (to represent the
  "enabling" effect).
- **Derived composite candidates:** normalized sub-scores feeding the fragility model.

### 4.4 Data Usage Strategy
- **Reference labels:** FSI (and FSI category) used as an external anchor and/or
  validation target.
- **Feature partition:** predictors (climate, socio-economic, governance) vs.
  mediators vs. outcome (fragility score/category).
- **Panel structure:** country × year; preservation of a held-out time block and
  held-out countries for out-of-sample validation.
- **Scenario data:** counterfactual and intervention scenarios generated by
  perturbing driver inputs (not from raw observed series).

---

## 5. Candidate Model Framework

The framework will be assembled as a **layered pipeline**: (A) fragility scoring,
(B) climate coupling & pathway attribution, (C) state-space dynamics for projection
and tipping points, (D) intervention optimization and costing, (E) scale
generalization. Multiple candidates will be compared per layer.

### 5.1 Layer A — Fragility Quantification and Classification
| Candidate method | Key mathematical idea | Advantages | Limitations |
|---|---|---|---|
| **Composite index (weighted sum)** | `F = Σ w_i x_i` over normalized indicators | Transparent, matches FSI logic | Weights subjective |
| **Entropy / CRITIC weighting** | Data-driven weights from dispersion/conflict | Reduces subjectivity | Sensitive to outliers |
| **PCA / factor analysis** | Latent factors from indicator covariance | Handles collinearity | Interpretability cost |
| **Fuzzy comprehensive evaluation** | Membership functions → fuzzy score | Handles gradation/uncertainty | Membership design choices |
| **Latent-variable / SEM** | `η = Bη + Γx + ζ` | Explicit latent structure | Identification/lag choices |

Classification into **fragile / vulnerable / stable** will use thresholds derived
from score distributional properties and/or alignment with FSI categories, with a
rule that is planned to be re-tested for stability.

### 5.2 Layer B — Climate Coupling and Direct/Indirect Pathway Attribution
- **Regression / panel models** (fixed/random effects, dynamic panels) with climate
  terms and interaction terms.
- **Mediation / path analysis (SEM)** to decompose **direct** climate→fragility
  effects and **indirect** effects via mediators (food/water security, economy,
  migration).
- **Bayesian networks / DAGs** to represent conditional dependencies and to compute
  pathway contributions probabilistically.
- **Shapley-value / variance-decomposition attribution** as a model-agnostic
  cross-check on each driver's contribution.

### 5.3 Layer C — Dynamics, Projection, and Tipping Points
- **System-dynamics / coupled ODE or difference-equation model** for driver–state
  feedbacks (stress → fragility → reduced adaptive capacity → higher sensitivity).
- **State-space / latent-transition model** for regime shifts.
- **Tipping-point formalization (planned definitions):**
  - **(i) Threshold crossing:** fragility score exceeding a critical level (or
    entering a "fragile" band) and remaining there.
  - **(ii) Bifurcation / regime shift:** parameter change past a critical value in a
    nonlinear dynamic model, identified via stability analysis.
  - **(iii) Early-warning signals:** rising variance / autocorrelation ("critical
    slowing down") in the fragility time series.
- **Prediction approach (planned):** scenario-conditioned projection (climate
  trajectories × governance/socio-economic assumptions) with uncertainty bands;
  "when" reported as the first horizon at which the chosen criterion is met.

### 5.4 Layer D — Intervention Optimization and Costing (Task 4)
- **Effect model:** interventions mapped to driver perturbations
  (e.g., irrigation → reduced drought sensitivity; early-warning → reduced hazard
  impact; governance strengthening → higher adaptive capacity).
- **Optimization:** multi-objective / constrained optimization to select a portfolio
  minimizing fragility subject to budget, over a horizon; candidates include linear/
  nonlinear programming, dynamic programming, and cost-effectiveness ranking.
- **Cost model:** total cost = Σ (unit cost × quantity) + fixed/implementation costs,
  with discounting; uncertainty propagated to a cost range.
- **Counterfactual:** compare intervened vs. non-intervened trajectories.

### 5.5 Layer E — Scale Generalization (Task 5)
- Treat "state" as a **scale parameter** (city ↔ country ↔ continent).
- Test whether indicator definitions, thresholds, and dynamics remain valid at other
  scales; where they fail, modify by (i) rescaling indicators, (ii) adding
  scale-specific governance/infrastructure variables, (iii) replacing national
  governance proxies with municipal/regional equivalents, and (iv) re-estimating
  weights/thresholds.

### 5.6 Core Variable Groups (planned)
- **Outcome:** fragility score / latent fragility / class.
- **Climate stressors:** temperature anomaly, precipitation variability, drought
  severity/duration, hazard frequency.
- **Exposure/sensitivity:** arable-land change, water stress, agricultural
  dependence, population pressure.
- **Adaptive capacity/governance:** governance quality, service provision, economic
  resources.
- **Mediators:** food/water security, economic performance, migration/displacement.

---

## 6. Implementation Roadmap

### 6.1 Workflow (planned phases)
1. **Phase 0 — Setup & governance:** schema definition, provenance manifest, repo/
   config scaffolding, reproducibility policy.
2. **Phase 1 — Data assembly & QA:** acquire sources, reconcile entities, align time
   grid, document missingness.
3. **Phase 2 — Feature engineering:** construct climate, exposure, capacity, lag, and
   interaction features.
4. **Phase 3 — Layer A:** build and compare fragility scoring models; calibrate
   classification thresholds.
5. **Phase 4 — Layer B:** estimate climate coupling and decompose direct/indirect
   pathways.
6. **Phase 5 — Layer C:** fit dynamics; define and operationalize tipping points;
   generate projections.
7. **Phase 6 — Task 2 case study:** top-10 FSI state retrospective + counterfactual.
8. **Phase 7 — Task 3 projection:** non-top-10 state forward analysis + definitive
   indicators.
9. **Phase 8 — Layer D:** intervention optimization and cost estimation.
10. **Phase 9 — Task 5 scaling:** city/continent assessment and modifications.
11. **Phase 10 — Validation, sensitivity, and reporting.**

### 6.2 Required Modules (planned)
- `io/` — data acquisition, parsing, provenance/checksum logging.
- `preprocess/` — reconciliation, alignment, imputation, normalization.
- `features/` — feature and interaction construction.
- `models_fragility/` — Layer A scoring + classification.
- `models_pathway/` — Layer B regression/SEM/BN + attribution.
- `models_dynamics/` — Layer C ODE/state-space + tipping-point detectors.
- `models_intervention/` — Layer D effect/cost/optimization.
- `scaling/` — Layer E adaptation tests.
- `validation/` — metrics, backtesting, sensitivity harness.
- `viz/` — reporting figures (to be generated in later rounds, not now).
- `config/` + `run/` — reproducible orchestration and logs.

### 6.3 Algorithms (candidate selection, not committed)
- Weighting: entropy/CRITIC, PCA/factor analysis, expert-weighted composites.
- Estimation: panel regression, SEM/path analysis, Bayesian networks, gradient-
  boosted trees / random forests with SHAP for attribution cross-checks.
- Dynamics: numerical ODE integration, state-space filtering, bifurcation/EWS
  detection (rolling variance/autocorrelation).
- Optimization: LP/NLP, dynamic programming, cost-effectiveness ranking, possibly
  multi-objective Pareto search.

### 6.4 Tooling (planned)
- Python (data/statistical/ML stack) and/or R for panel/SEM methods; version-pinned
  environments; config-driven runs; deterministic seeds; artifacts logged per run.

---

## 7. Validation Strategy

### 7.1 Evaluation Metrics (planned)
- **Classification:** accuracy, precision/recall, F1, macro-F1, ROC-AUC for
  fragile/vulnerable/stable; confusion analysis against FSI categories.
- **Scoring fidelity:** rank correlation (Spearman/Kendall) between the model score
  and FSI; calibration checks.
- **Attribution:** stability of direct/indirect decomposition across methods
  (regression vs. SEM vs. SHAP).
- **Projection:** out-of-sample error (RMSE/MAE), directional accuracy, horizon-wise
  performance.
- **Tipping-point:** lead-time reliability, false-alarm vs. missed-shift tradeoff.
- **Intervention/cost:** cost-effectiveness metrics, robustness of optimum to
  parameter perturbation.

### 7.2 Validation Methods (planned)
- **Temporal hold-out / backtesting:** train on earlier periods, test on later.
- **Country hold-out / cross-validation:** generalization across states.
- **Benchmark comparison:** align against FSI and independent indices.
- **Counterfactual sanity checks:** verify that "no-climate" scenarios reduce
  fragility in the expected direction (direction only; magnitudes deferred).
- **Methodological triangulation:** corroborate key pathway conclusions across
  independent model families.
- **Reproducibility audit:** identical configs → identical artifacts.

### 7.3 Sensitivity and Uncertainty Analysis (planned)
- **Parameter sensitivity:** weights, thresholds, lags, horizons (one-at-a-time and
  global, e.g., Sobol/Morris screening).
- **Data sensitivity:** imputation choices, normalization schemes, aggregation
  granularity.
- **Structural sensitivity:** compare across candidate model families (Layer A–D).
- **Scenario uncertainty:** multiple climate and socio-economic trajectories.
- **Robustness of tipping points:** stability of predicted timing/criteria under
  perturbation.

---

## 8. Expected Result Interpretation

> This section describes how future outputs *would be interpreted*; it reports no
> results.

- **Fragility score & class:** will be read as a relative, uncertainty-bounded
  measure; class labels will be interpreted with threshold sensitivity in mind.
- **Direct vs. indirect climate effects:** will be interpreted as relative pathway
  contributions within the model's structure — useful for prioritizing intervention
  targets (e.g., mediating sectors vs. direct exposure).
- **Counterfactuals (Task 2):** "less fragile without these effects" will be stated
  as a scenario-based magnitude and direction, not a causal law.
- **Projections & tipping points (Task 3):** will be presented as scenario-
  conditioned horizons with confidence bands; "definitive indicators" will be ranked
  by stability and effect size, and the tipping-point definition will be reported
  alongside its criterion.
- **Interventions & cost (Task 4):** will be interpreted as a portfolio with
  expected effect and an estimated total cost range; intervention benefits relative
  to cost will guide prioritization.
- **Scaling (Task 5):** will be interpreted as an assessment of transferability,
  clearly stating where the model holds, where it fails, and what modifications are
  required.

---

## 9. Limitations and Improvements

### 9.1 Anticipated Limitations
- **Data availability/quality:** composite indices differ in methodology and update
  cadence; climate and conflict data have coverage and reporting biases.
- **Causality vs. association:** observational panel methods cannot fully establish
  causation; climate–conflict relationships are contested in the literature.
- **Latent and subjective constructs:** fragility and governance proxies embed
  normative choices.
- **Counterfactual assumptions:** intervention and "no-climate" scenarios are
  model-based.
- **Tipping-point uncertainty:** regime-shift detection is sensitive to noise,
  windows, and model structure.
- **Scale transferability:** national-scale indicators may not map cleanly to
  cities or continents.
- **Cost estimation:** unit-cost data are uncertain and context-dependent.

### 9.2 Planned Improvements
- **Multi-source data assimilation** and explicit uncertainty propagation end-to-end.
- **Ensemble/multi-model comparison** with consensus and disagreement reporting.
- **Causal-inference extensions** (instrumental variables, difference-in-differences,
  or natural experiments) where data permit.
- **Probabilistic fragility modeling** (Bayesian hierarchical/state-space) for
  calibrated uncertainty.
- **Automated sensitivity/robustness dashboards** for thresholds and weights.
- **Scale-aware model variants** for city and continent analyses.
- **Stakeholder-informed weighting** and scenario co-design for intervention studies.
- **Transparent reproducibility artifacts** (config, seeds, provenance) for every
  later modeling round.

---

## Appendix A — Traceability to Native Tasks
| Native Task | Addressed in plan by |
|---|---|
| Task 1 (joint fragility + climate model; classification; direct/indirect) | Sections 2 (S1), 3.1–3.2, 5.1–5.2, 7 |
| Task 2 (top-10 FSI state retrospective; less-fragile counterfactual) | Sections 2 (S2), 5.4, 6.1 (Phase 6), 8 |
| Task 3 (non-top-10 state; definitive indicators; tipping point) | Sections 2 (S3), 5.3, 6.1 (Phase 7), 8 |
| Task 4 (interventions; effect; total cost) | Sections 2 (S4), 3.3, 5.4, 6.2, 8 |
| Task 5 (cities/continents transferability) | Sections 2 (S5), 5.5, 8, 9 |

## Appendix B — Open Questions to Resolve Before Modeling
- Which aggregation/normalization scheme best matches the FSI reference logic?
- Which mediators will carry the indirect climate pathway, and are they observable?
- How will the tipping-point criterion be operationalized (threshold vs. bifurcation
  vs. early-warning) and combined?
- What intervention taxonomy and unit-cost sources will be adopted?
- Which data sources will be staged into `data/`, and under what schema?

---

*End of modeling blueprint draft. No problem-solving, computation, fitting, or
experimentation has been performed; this document specifies a plan only.*
