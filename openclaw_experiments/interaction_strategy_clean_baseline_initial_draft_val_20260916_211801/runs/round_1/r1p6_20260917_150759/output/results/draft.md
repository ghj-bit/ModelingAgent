# The Next Plague? — Initial Modeling Plan Draft

**Problem ID:** 2014_The_Next_Plague?
**Source:** HiMCM 2014
**Artifact type:** Modeling blueprint draft (planning only — not a solution)
**Status:** Initial draft, to be expanded in later rounds

> This document is a roadmap for future modeling work. It contains **no** computed results, fitted parameters, solved cases, or final conclusions. All quantities are described in terms of *what will be estimated* and *how*, using future-oriented language.

---

## 1. Problem Background and Restatement

An island village in Indonesia (≈300 inhabitants) is experiencing an outbreak: roughly half of the population shows similar symptoms, and 15 deaths occurred within the past week. The village trades with nearby villages and other islands, so transmission across a small contact network is plausible.

The modeling team acts as an analyst for a national center for disease control (or the WHO). The decision context is **resource allocation under scarcity**: doctors, containment facilities, money, research capacity, and serums (countermeasures) are limited, so the team must decide not only *whether* an epidemic is contained but *when* to act and *how much* resource to commit.

The problem has five requirement clusters:

- **R1 — Surveillance & decision model.** A model (or family of models) that (a) classifies the type and severity of the spread, (b) determines whether an epidemic is contained, and (c) triggers appropriate measures (treat, transport victims, restrict movement, or let the disease run its course) with a rule for *when* to allocate scarce resources.
- **R2 — Recommendations.** 3–5 justified initial recommendations for the CDC, grounded in the model and stated assumptions.
- **R3 — Elicitation.** Up to 3 questions to the returning multi-national research team (7 days of field data collection) that would most improve the model, with justification.
- **R4 — Model revision.** How new information changes the model: contact/bodily-fluid transmission, age-dependent mortality (elderly and children), a second island showing signs, and a returning researcher who appears infected.
- **R5 — Communication.** A one-page non-technical synopsis for a local news outlet.

The central difficulty is not merely forecasting infections but coupling an epidemiological model to a **decision/control layer** that is robust to sparse, delayed, and noisy field data.

## 2. Objectives and Subproblems

### 2.1 Primary objective
Design a modular, decision-oriented modeling framework that links (i) outbreak characterization, (ii) epidemic forecasting/containment assessment, and (iii) resource-allocation rules, so that a CDC can act early under uncertainty.

### 2.2 Subproblems (to be addressed in later modeling rounds)

- **S1 — Outbreak characterization.** Define features and decision rules that will classify *type* (e.g., transmission route proxies, contact vs. vector vs. environmental) and *severity* (e.g., case-fatality, doubling behavior, attack rate) from sparse early signals.
- **S2 — Compartmental transmission model.** Formulate a base SIR-family model and candidate extensions (SEIR for latent period, SEIRD for mortality, age-structured compartments, spatial/multi-patch coupling) that will describe within-village and between-island spread.
- **S3 — Containment criterion.** Define a quantitative criterion for "contained" (e.g., effective reproduction number trajectory, threshold conditions) and a prediction of whether the outbreak will be contained under no intervention vs. intervention.
- **S4 — Intervention/trigger layer.** Specify state-dependent, time-dependent trigger rules (when to treat, when to transport, when to restrict movement, when to stand down) and the associated decision thresholds to be calibrated.
- **S5 — Resource allocation.** Formulate an optimization or decision-analytic layer (e.g., constrained optimization, dynamic programming, or portfolio/priority rule) allocating scarce doctors, facilities, funds, and serums across competing needs and regions.
- **S6 — Uncertainty & robustness.** Specify how parameter uncertainty, reporting delays, and under-ascertainment will be represented and propagated into recommendations.
- **S7 — Elicitation (R3) and model revision (R4).** Prepare the three highest-value questions and pre-plan how each answer will update specific model components.
- **S8 — Communication (R5).** Plan the structure of the non-technical synopsis and its translation of model outputs into plain-language guidance.

### 2.3 Deliverables
- A documented modeling framework (equations/architecture described, to be instantiated later).
- A trigger/decision table linking model states to recommended actions.
- An allocation plan specifying objective functions and constraints (to be solved later).
- Three elicitation questions and a revision map.
- A one-page non-technical synopsis outline.

## 3. Assumptions

Assumptions are provisional and will be tested/refined in later rounds. Each is paired with a planned validation route.

**A. Population & structure**
- A1. The village is treated as a well-mixed population of ≈300 for a first-cut model; age structure will be added in a later sub-model. *Justification:* small, dense community. *Validation:* compare well-mixed vs. structured output; assess sensitivity to mixing.
- A2. Neighboring villages/islands will be represented as coupled sub-populations connected by a trade-travel contact matrix. *Validation:* compare against connectivity data requested in R3.

**B. Disease natural history**
- A3. A latent/exposed period exists (motivating SEIR-type structure). *Validation:* literature ranges; elicit from field team.
- A4. Transmission is primarily contact/bodily-fluid driven (per R4), modeled as frequency/density-dependent contact. *Validation:* consistency check against reported attack rate.
- A5. Mortality is age-dependent, with elevated risk for the elderly and children (per R4). *Validation:* age-stratified data request; sensitivity to mortality weighting.
- A6. Some recovered individuals may be assumed immune for the horizon of the model (final/exponential decay of susceptibility). *Validation:* sensitivity to waning-immunity assumption.

**C. Data & reporting**
- A7. Reported cases underestimate true infections (under-ascertainment) and are subject to delay. *Validation:* estimate reporting fraction range and test its effect on thresholds.
- A8. Initial conditions (initial exposed/infectious counts) are uncertain and will be treated as a range, not a point. *Validation:* scenario sweeps over initial-condition priors.

**D. Intervention & control**
- A9. Interventions (treatment, isolation, movement restriction) act by reducing transmission rate and/or shortening infectious period. *Validation:* test alternative efficacy parameterizations.
- A10. Resource supply is fixed over the planning horizon (scarcity assumption). *Validation:* sensitivity to supply elasticity.

**E. Modeling scope**
- A11. Demographic change (births/deaths from non-disease causes) is negligible over the horizon. *Validation:* order-of-magnitude check.
- A12. Behavior is exogenous for a first-cut model; behavioral feedback may be added later. *Validation:* note as limitation; scenario test.

## 4. Data Processing Plan

No raw dataset accompanies this statement; therefore the plan distinguishes **available inputs** (the scenario facts) from **data to be elicited/acquired**.

### 4.1 Currently available inputs (from the statement)
- Village population size (≈300).
- Fraction showing symptoms (≈half).
- Deaths in the past week (15).
- Presence of trade/travel links to nearby villages and other islands.
- R4 additions: contact/bodily-fluid transmission; age-dependent mortality; a second island affected; an infected returning researcher.

### 4.2 Inputs to be requested/acquired (future)
- Case counts by day and by age band; symptom onset vs. reporting dates (for delay/back-calculation).
- Case-fatality by age and care status.
- Contact/travel volume between village, neighboring villages, and islands.
- Healthcare capacity (beds, isolation units, staff) and serum/antiviral availability.
- Genetic/pathogen information if available, to inform transmission route.

### 4.3 Preprocessing steps (planned)
- **Cleaning & reconciliation:** resolve duplicate/ambiguous counts; standardize time units (days since first observed case).
- **Under-ascertainment adjustment:** define a reporting-fraction parameter and decide whether to model observed or latent case series.
- **Delay correction:** plan for back-calculation / nowcasting of onset-to-report delay.
- **Age stratification:** bin into children / adults / elderly per the mortality risk structure.
- **Spatial aggregation:** build village-level and island-level strata with a connectivity matrix.
- **Normalization/derived features:** attack rate, apparent doubling behavior, crude case-fatality, effective contact proxies.

### 4.4 Feature construction (for classification and triggers)
- Epidemiological features: apparent growth rate, generation-interval-adjusted reproduction estimate, severity index, spread-velocity proxy.
- Decision features: available resources, response time, isolation capacity, cross-border connectivity.
- Trigger features: deviations of observed signals from model-predicted trajectories (for early-warning residuals).

### 4.5 Data usage strategy
- Split the horizon into **calibration window** (fit/estimate), **decision window** (apply triggers), and **evaluation window** (backtest), acknowledging that real-world data will be limited.
- Where data are absent, use literature-range priors and design scenario-based inputs rather than single-point guesses.

## 5. Candidate Model Framework

The framework is intended to be **layered and modular**, so components can be swapped as data arrive. The following candidates are planning options, not final choices.

### 5.1 Layer 1 — Outbreak characterization (classification)
- **Candidate methods:** rule-based severity indices; logistic/decision-tree or other classifiers on epidemiological features; clustering of outbreak trajectories; threshold logic derived from reproduction-number estimates.
- **Variables (planned):** apparent growth rate, attack rate, case-fatality, spread velocity, connectivity index.
- **Ideas:** map feature vectors to discrete classes (type: contact-borne vs. other; severity: contained / emerging / severe / critical).
- **Advantages:** interpretable, fast, supports triggers.
- **Limitations:** sensitive to under-reporting and small-sample noise.

### 5.2 Layer 2 — Transmission dynamics
- **Candidate models (increasing complexity):**
  - SIR / SIS baselines.
  - SEIR (adds latent period) as the primary candidate given contact transmission.
  - SEIRD / SEIR with age-structured mortality.
  - Age-structured SEIR (children/adults/elderly compartments).
  - Metapopulation / multi-patch SEIR with a trade-travel mixing matrix (village ↔ villages ↔ islands).
  - Stochastic versions (continuous-time Markov chains, Gillespie, or stochastic ODE ensembles) for small populations where extinction/outbreak probability matters.
- **Variables (planned):** S, E, I, R, D by patch and age group; transmission rate β, contact matrix, latent rate σ, recovery γ, disease mortality μ, reporting fraction.
- **Mathematical ideas:** system of ODEs/CTMC; next-generation matrix for R0; spatial coupling via mixing operator; branching-process approximation for early spread.
- **Advantages:** standard, extensible, links directly to R0-like thresholds and control levers.
- **Limitations:** well-mixed assumption, parameter identifiability under sparse data; requires extensions for the R4 case of an infected traveler.

### 5.3 Layer 3 — Containment assessment
- **Candidate approaches:** trajectory of the effective reproduction number (threshold logic), threshold theorems from the model, and probabilistic "containment probability" from stochastic simulations.
- **Ideas:** define containment as (a) predicted decline in active infections, (b) R_eff persistently < 1, and/or (c) outbreak-extinction probability above a tolerance.
- **Limitations:** threshold definition depends on data quality; will require sensitivity analysis.

### 5.4 Layer 4 — Intervention triggers and control
- **Candidate methods:** state-feedback threshold policies; epidemic-alarm/early-warning rules; optionally optimal-control formulations (e.g., minimize infections + resource cost with control terms for treatment, isolation, movement restriction).
- **Variables (planned):** intervention intensity per channel; activation times; coverage rates.
- **Ideas:** define trigger table mapping (severity class × trajectory) → recommended action (treat / transport / restrict movement / stand down).
- **Limitations:** policy realism, behavioral response, and implementation lag (to be acknowledged).

### 5.5 Layer 5 — Resource allocation
- **Candidate methods:** constrained optimization (linear/nonlinear), priority/portfolio rules, dynamic programming over epidemic stages, and multi-criteria decision analysis for competing objectives.
- **Variables (planned):** allocation of doctors, beds/isolation capacity, funds, countermeasures/serum, research effort.
- **Ideas:** objective combines expected health burden averted and resource cost; constraints encode scarcity and logistics.
- **Limitations:** requires cost/efficacy inputs; risk of overfitting to assumed utilities.

### 5.6 Uncertainty layer
- Bayesian calibration (priors from literature/scenario, likelihood on observed series) or likelihood-free approaches (ABC, simulation-based inference) for intractable models.
- Ensemble/scenario-based outputs rather than single-point forecasts.

### 5.7 Tooling (planned, not executed)
- Language: Python (NumPy/SciPy, `scipy.integrate` for ODEs, stochastic libraries) or equivalent.
- Optimization: SciPy / `cvxpy`-style or heuristic search, depending on formulation.
- Bayesian: PyMC/Stan-style samplers or ABC where needed.

## 6. Implementation Roadmap

A staged build, each stage independently testable:

1. **Stage 0 — Scaffolding.** Define repository layout (`code/`, `data/`, `results/`), configuration schema for parameters/scenarios, and a data-contract for expected field inputs.
2. **Stage 1 — Base dynamics.** Implement SEIR single-patch with configurable parameters; verify conservation and basic behavior qualitatively (no results reported here).
3. **Stage 2 — Structure extension.** Add (a) mortality/age structure and (b) metapopulation coupling with a mixing matrix.
4. **Stage 3 — Stochasticity.** Add stochastic realizations and outbreak-probability estimation for small populations.
5. **Stage 4 — Characterization module.** Implement feature extraction and the classification/severity rule set.
6. **Stage 5 — Trigger engine.** Implement the state/trajectory → action decision table with configurable thresholds.
7. **Stage 6 — Allocation module.** Implement the optimization/decision-analytic layer with scarcity constraints.
8. **Stage 7 — Scenario & uncertainty runner.** Batch scenarios, sensitivity sweeps, and ensemble generation.
9. **Stage 8 — Reporting.** Generate decision-support summaries and the R5 synopsis outline.

**Required modules (planned):** parameter/config manager; ODE/CTMC integrator; intervention model; feature extractor; classifier/rule engine; trigger evaluator; allocation optimizer; uncertainty sampler; visualization/reporting (later rounds only).

**Workflow conventions:** version parameters, log scenario configurations, keep calibration and evaluation strictly separated, and record all assumption decisions for reproducibility.

## 7. Validation Strategy

### 7.1 Evaluation metrics (planned)
- **Dynamics:** ability to reproduce qualitative outbreak behavior (growth, peak, decline) under plausible parameter ranges; calibration error on held-out windows.
- **Characterization:** classification/severity accuracy against expert-labeled scenarios or literature archetypes.
- **Containment:** calibration of predicted containment vs. simulated ground-truth outcomes in synthetic scenarios; classification metrics (sensitivity/specificity for "will be contained").
- **Control/allocation:** expected burden averted and cost per outcome under simulated scenarios; regret vs. an oracle allocation baseline.
- **Robustness:** stability of recommended actions under parameter perturbation.

### 7.2 Validation methods
- **Internal consistency & conservation checks** on the dynamical system.
- **Synthetic-data recovery (inverse problem):** generate data from the model and test whether parameters/thresholds can be recovered — the primary validation route given no dataset.
- **Scenario-based backtesting:** apply trigger rules to simulated epidemics and measure decision quality.
- **Cross-model comparison:** compare SIR vs. SEIR vs. metapopulation vs. stochastic predictions to bound structural uncertainty.
- **Expert/qualitative review:** check outputs against epidemiological expectations and the R4 qualitative facts.

### 7.3 Sensitivity & uncertainty analysis (planned)
- One-at-a-time and global sensitivity (e.g., variance-based / Sobol-style) on β, σ, γ, μ, reporting fraction, contact matrix, initial conditions, and intervention efficacy.
- Threshold robustness: how trigger boundaries shift under uncertainty.
- Scenario ensemble: baseline, optimistic, pessimistic, and policy-variant scenarios.
- Reporting-delay and under-ascertainment stress tests.

## 8. Expected Result Interpretation

This section describes **how outputs will be read**, not what they are.

- **Severity/type classification outputs** will be interpreted as a graded early-warning label carrying explicit uncertainty, not a diagnosis.
- **Containment outputs** will be interpreted as probabilistic statements (likelihood of containment) rather than binary certainties, informing escalation vs. de-escalation.
- **Trigger outputs** will be interpreted as recommended action windows; the framework's value will be in *timing and prioritization*, not in point predictions.
- **Allocation outputs** will be interpreted comparatively (which option does better under which scenario), acknowledging that optimality depends on the chosen objective and assumed costs.
- **R3 questions** are expected to yield constraint reductions — i.e., which parameters become identifiable and how conclusions narrow once answered.
- **R4 revisions** are expected to shift model structure (transmission mode, age stratification, spatial coupling, importation risk from a traveler), changing which interventions dominate.

## 9. Limitations and Improvements

**Known limitations of the planned framework**
- Well-mixed and exogenous-behavior assumptions simplify real contact dynamics.
- Sparse data implies weak identifiability; results will be scenario-dependent rather than precise.
- Under-ascertainment and reporting delay can bias growth and severity estimates unless corrected.
- Allocation models depend on assumed costs/utilities that may not reflect real policy constraints.
- Small population size makes stochastic effects important; deterministic models may mislead near extinction.

**Planned improvements / extensions**
- Behavior-feedback (awareness-driven contact reduction) as an extension.
- Time-varying intervention efficacy and implementation lag modeling.
- Pathogen-evolution or waning-immunity extensions if relevant.
- Value-of-information analysis to prioritize R3 questions by expected decision impact.
- Development of a policy-clean trigger table and an allocation tool intended for practical use by a CDC.

---

### Appendix A — R3 Elicitation Question Plan (to be refined)

Three questions will be selected to maximize decision-relevant information. Planned selection criteria and candidate directions:

1. **Transmission & contact structure** — e.g., how are contacts and trade-travel links structured (who mixes with whom, how often across islands)? *Why:* determines the mixing matrix and spatial coupling, the largest structural uncertainty.
2. **Natural history & severity** — e.g., onset-to-report/onset-to-death timing, attack rate, and age-specific fatality? *Why:* calibrates latent/recovery/mortality parameters and severity classification.
3. **Infrastructure & countermeasure feasibility** — e.g., available isolation capacity, transport feasibility, and any effective treatment/serum? *Why:* defines the feasible action set and allocation constraints.

### Appendix B — R4 Revision Map (to be refined)

| New information | Planned model change |
|---|---|
| Bodily-fluid/contact transmission | Confirm contact-driven β; emphasize isolation/hygiene interventions over airborne assumptions |
| Elderly & children more likely to die | Add age-structured mortality; age-targeted allocation of care/serum |
| Second island affected | Activate multi-patch coupling; add importation terms and cross-island movement restriction |
| Returning researcher infected | Add importation/exportation event into capital; model case-importation and local containment trigger |

### Appendix C — R5 Synopsis Outline (planning only)

- Plain-language statement of the risk.
- One or two simple analogies for how the disease spreads.
- What the model suggests about acting early vs. late (qualitative only).
- What the public should expect and can do.
- One clear call to action for officials and citizens.

---

*End of initial modeling plan draft. Subsequent rounds will instantiate equations, estimate parameters, solve allocations, and generate validated results.*
