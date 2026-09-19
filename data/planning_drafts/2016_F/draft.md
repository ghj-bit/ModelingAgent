# Modeling Blueprint Draft — MM-Bench 2016_F
## Refugee Migration: Metrics, Flow, Dynamics, Policy, Exogenous Shocks, and Scalability

> **Document status:** Planning-only blueprint (initial draft). This document describes *how* a future
> modeling effort will be structured. It contains no computed results, no data analysis, no fitted
> parameters, no executed experiments, and no final conclusions. All statements are prospective and
> intended as a roadmap for downstream modeling work.

---

## 1. Problem Background and Restatement

### 1.1 Context (as stated in the problem)

- Since 2015, a large and accelerating movement of refugees has been entering Europe and parts of Asia,
  driven primarily by political and social unrest and warfare in the Middle East.
- By the end of October 2015, European countries had reportedly received more than 715,000 asylum
  applications. Hungary recorded the highest per-capita application rate (nearly 1,450 per 100,000
  inhabitants) while granting only a small fraction (about 32% in 2014).
- Europe operates a quota/resettlement system with a disproportionate burden on countries such as France
  and Germany.
- Migration occurs along six named routes: (1) West Mediterranean, (2) Central Mediterranean,
  (3) Eastern Mediterranean, (4) West Balkans, (5) Eastern Borders, and (6) Albania–Greece.
- Routes differ in safety and accessibility; Eastern Mediterranean is the most popular and Central
  Mediterranean the most dangerous.
- Host countries are concerned about capacity to supply food, water, shelter, and healthcare.
- Refugee decisions are described as depending on transportation availability, route safety, and access
  to basic needs at the destination.

### 1.2 Restatement of the requested deliverable

The modeling team (framed as "ICM-RUN") will develop an analytical framework that:

1. Defines **metrics/parameters** that enable or inhibit safe, efficient refugee movement.
2. Builds an **optimal flow model** across the six routes, considering accessibility, safety, and
   country resource capacity, including possible multi-entry-point and multi-country extensions.
3. Captures **crisis dynamics over time** (changing capacities, cascade effects, prepositioned resources,
   NGO roles, and additional destinations such as Canada, China, and the United States).
4. Translates the model into **policy recommendations** that prioritize refugee and local-population
   health and safety within legal and cultural constraints.
5. Analyzes **exogenous events** (e.g., terrorism-linked shocks) — which parameters shift, cascading
   regional effects, and how to make recommended policy resilient.
6. Evaluates **scalability** — behavior under a 10× expansion, parameters that break down or become
   irrelevant, new parameters required, and time-related issues (disease control, childbirth, education).

### 1.3 What this document is *not*

This is a design blueprint. It deliberately stops before any quantitative work: no data will be
processed, no models will be estimated, and no results will be produced within this document.

---

## 2. Objectives and Subproblems

### 2.1 Overall objective

Produce a coherent, defensible, multi-scale modeling framework that links **route-level refugee flow
decisions**, **dynamic host-country capacity**, **policy levers**, **exogenous shocks**, and
**scalability** into a single planning architecture, with an explicit validation strategy.

### 2.2 Subproblem decomposition (mapped to the six tasks)

| ID | Subproblem | Core question to be modeled | Placeholder deliverable |
|----|------------|-----------------------------|--------------------------|
| SP1 | Metrics of the crisis | Which enabling/inhibiting factors and measures should be defined, and why? | Metric taxonomy + parameter list |
| SP2 | Flow of refugees | What is the "optimal" route/entry assignment and flow rate? | Flow optimization model |
| SP3 | Dynamics of the crisis | How do capacity, demand, and destinations evolve and cascade over time? | Dynamic/state-transition model |
| SP4 | Policy support | Which policies best sustain optimal, health-and-safety-first migration? | Policy evaluation layer |
| SP5 | Exogenous events | What parameters shift, what cascades occur, how resilient is policy? | Shock/scenario layer |
| SP6 | Scalability | How does the framework behave under 10× load and over long horizons? | Scaling analysis plan |

### 2.3 Intended outputs (of the future effort, not this draft)

- A parameter/metric dictionary with justification.
- One or more optimization/dynamic model specifications (equations described conceptually).
- A policy-scenario comparison framework.
- A shock-response and scaling protocol.
- A validation and sensitivity plan.

---

## 3. Assumptions

Assumptions are grouped by the subproblem they support. Each includes a justification and a future
validation approach. (None are validated here.)

### 3.1 Scope and population assumptions

- **A1 — Aggregation level.** Refugee flow will be modeled at the group/population level (not
  individual-agent level) for the base models, with agent-based extensions reserved for behavioral
  detail. *Justification:* group-level flows are more tractable and align with aggregate data.
  *Validation:* compare group-level aggregates against any future individual/disaggregate evidence.
- **A2 — Planning horizon.** The primary horizon will be short-to-medium term (weeks–months), with a
  long-horizon variant for scalability. *Justification:* crisis conditions change rapidly.
  *Validation:* re-run with altered horizons to test robustness.
- **A3 — Geographic scope.** Base models focus on the six named routes and European/Asian destinations;
  the extended scope adds Canada, China, and the United States. *Justification:* matches the problem
  statement. *Validation:* assess whether added destinations require structural (not just parameter) change.

### 3.2 Route and behavior assumptions

- **A4 — Route set.** The six named routes are the initial route universe; additional routes may be
  introduced as model extensions. *Justification:* stated in the problem. *Validation:* sensitivity to
  route inclusion/exclusion.
- **A5 — Decision drivers.** Route choice is assumed to depend principally on safety, accessibility/
  transportation availability, cost, and destination capacity/needs access. *Justification:* explicitly
  indicated in the problem. *Validation:* compare against behavioral literature and alternative driver sets.
- **A6 — Rationality-with-friction.** Decision units behave in a boundedly rational, utility-seeking way
  subject to information limits and constraints, rather than fully optimal. *Justification:* realistic for
  crisis settings. *Validation:* compare optimization vs. behavioral model variants.

### 3.3 Capacity and resource assumptions

- **A7 — Finite capacity.** Each destination has finite capacity across resource categories (shelter,
  food, water, healthcare, processing). *Justification:* central to the problem. *Validation:* test
  capacity-bound vs. capacity-relaxed regimes.
- **A8 — Non-substitutability (first pass).** Resource categories are treated as separately constrained
  in the first pass; substitution may be introduced later. *Justification:* simplifies early specification.
  *Validation:* relax and compare.
- **A9 — Prepositioning.** Some resources can be prepositioned ahead of demand, subject to lead times and
  budget. *Justification:* explicitly requested. *Validation:* vary prepositioning policy in scenarios.

### 3.4 Dynamic and shock assumptions

- **A10 — Cascading saturation.** The most desirable destinations saturate first, altering downstream
  parameters (a cascade). *Justification:* stated in task 3. *Validation:* detect cascade patterns in
  dynamic simulations.
- **A11 — Exogenous shocks.** Shocks (e.g., security events) act as sudden parameter shifts
  (policy stringency, perceived safety, capacity) rather than smooth trends. *Justification:* task 5.
  *Validation:* scenario-based stress testing.
- **A12 — NGO effect.** NGO involvement expands effective capacity and alters allocation efficiency.
  *Justification:* task 3. *Validation:* compare with/without NGO module.

### 3.5 Data and measurement assumptions

- **A13 — Public-source reliance.** Because no local dataset was staged (the dataset definition is empty),
  the plan assumes data will be assembled from named public sources (UNHCR, IOM, WHO, Eurostat-type
  aggregators, and the referenced articles). *Justification:* observed empty data directory.
  *Validation:* source triangulation and provenance logging.
- **A14 — Measurement consistency.** Cross-country metrics will be harmonized to common units/definitions
  before use. *Justification:* heterogeneous reporting. *Validation:* consistency checks and unit audits.

---

## 4. Data Processing Plan

> No data will actually be collected or processed in this draft. The following is the intended pipeline.

### 4.1 Data inventory plan (to be sourced later)

Because the staged data directory is empty, the future effort will assemble:

- **Flow/volume series:** asylum applications, border crossings, arrivals by route and country.
- **Route attributes:** accessibility, transport modes, cost, travel time, and safety/risk proxies.
- **Capacity indicators:** shelter/housing, food/water, healthcare, processing throughput, per-capita
  burden.
- **Outcome indicators:** asylum grant rates, homelessness/pressure indices.
- **Policy/jurisdiction metadata:** quotas, entry-point counts, legal/cultural constraints.
- **Shock/event records:** dated security and policy events for scenario layer.
- **Reference sources:** the URLs listed in the problem Addendum (BBC route map, IOM, UNHCR, WHO/Europe,
  ICRC, NYT).

### 4.2 Preprocessing plan

1. **Source registration & provenance:** record source, URL, retrieval date, license, and units.
2. **Schema harmonization:** map all sources to a common schema (entity, region, route, time, category,
   unit, value).
3. **Unit & definition normalization:** standardize counts (absolute vs. per-100K), rates, and periods.
4. **Temporal alignment:** resample to a common cadence (e.g., weekly/monthly), handling irregular
   reporting.
5. **Missing-data treatment:** document and apply a consistent strategy (interpolation, flagging,
   imputation placeholder) — to be decided per variable, not fixed here.
6. **Outlier/shock labeling:** tag known shock periods for exclusions or separate treatment (link to SP5).
7. **De-duplication:** reconcile overlapping sources to avoid double counting.
8. **Quality scoring:** attach confidence/provenance scores per series.

### 4.3 Feature construction plan

- **Route safety index** (composite; weights to be defined and stress-tested).
- **Accessibility/transport index** (mode availability, cost, travel time).
- **Destination capacity-pressure index** (demand-to-capacity ratio by resource type).
- **Entry-point flexibility** (number and type of entry points).
- **Policy stringency indicators** (quota adherence, acceptance rate, border controls).
- **Per-capita burden indicators** (to compare asymmetric burden).
- **Temporal features** (trend, seasonality, event flags).

### 4.4 Data usage strategy

- **Calibration vs. estimation vs. validation partitions** to be defined (no leakage between them).
- **Scenario data** (shocks, policy changes) kept separate from baseline series.
- **Cross-source triangulation** for robustness; prefer ranges over single points where sources disagree.
- **Assumption ledger** linking every numeric input back to a documented assumption (A1–A14).

---

## 5. Candidate Model Framework

Candidate models are listed with their role, key variables, mathematical ideas, and trade-offs. Final
selection will follow comparative validation; multiple candidates may be combined in a layered
architecture.

### 5.1 Layer 1 — Metric layer (SP1)

- **Approach:** define a documented metric taxonomy (enabling vs. inhibiting factors; individual, route,
  transport, and country-capacity dimensions).
- **Mathematical idea:** composite indices built from normalized indicators (weighted or entropy-based
  weighting); explicit rationale per factor.
- **Key variables (conceptual):** safety, accessibility, cost, capacity, burden, entry-point count.
- **Pros/cons:** transparent and reusable; subjectivity in weighting must be managed via sensitivity
  analysis.

### 5.2 Layer 2 — Flow optimization (SP2)

- **Candidate A: Network flow / min-cost flow.** Nodes = origins, transit hubs, entry points;
  arcs = routes with cost/capacity. Objective: route refugees to safe, efficient paths.
- **Candidate B: Linear/Integer programming.** Decision variables = flow per route/entry point;
  constraints = route capacity, safety thresholds, destination capacity; objective = weighted
  safety/accessibility/cost.
- **Candidate C: Multi-objective optimization.** Explicit trade-offs (safety vs. speed vs. cost vs.
  burden equity); Pareto front as the planning object.
- **Candidate D: Utility-based assignment.** Refugee decision units maximize expected utility subject to
  constraints; supports discrete choice / logit-style route probabilities.
- **Pros/cons:** A–C give system-optimal plans but may over-assume central control; D captures behavior
  but is harder to calibrate. A hybrid (system optimum with behavioral elasticities) is a likely candidate.

### 5.3 Layer 3 — Dynamics and cascade (SP3)

- **Candidate A: System dynamics / stock–flow.** Stocks = refugee populations at nodes; flows = arrivals/
  departures; feedback = capacity saturation slowing inflow and rerouting.
- **Candidate B: Dynamic network flow.** Time-expanded network with capacity that changes over time.
- **Candidate C: State-transition / compartmental (queuing & congestion).** Nodes as service systems with
  queues and congestion-dependent service rates; saturation triggers cascades.
- **Candidate D: Agent-based model (extension).** Individual/group agents with rules; used to test
  emergent cascades and heterogeneity.
- **Resource allocation sub-layer:** prepositioning decisions, priority rules (what to stock, where,
  when), government vs. NGO resource pools, and allocation policy.
- **Pros/cons:** A–C are tractable and interpretable; D is richer but costlier and harder to validate.

### 5.4 Layer 4 — Policy evaluation (SP4)

- **Approach:** embed policy levers (quotas, entry limits, acceptance criteria, funding, NGO
  integration) as controllable parameters and evaluate scenario outcomes.
- **Mathematical idea:** policy-parameter sweep + multi-criteria decision analysis (MCDA) weighting
  health, safety, equity, feasibility, and legal/cultural constraints.
- **Key variables:** policy stringency, quota shares, resource budgets, NGO participation rate.
- **Pros/cons:** supports decision support; requires careful criterion weighting and stakeholder framing.

### 5.5 Layer 5 — Exogenous shocks (SP5)

- **Approach:** scenario/event model that applies discrete parameter shifts to Layers 2–4.
- **Mathematical idea:** step-change / regime-switch parameters; shock propagation across network edges;
  resilience metrics (recovery time, residual flow hit).
- **Key variables:** perceived safety, policy stringency, capacity cuts, demand surges.
- **Pros/cons:** transparent stress testing; shock timing/magnitude uncertainty must be handled with
  scenario ensembles.

### 5.6 Layer 6 — Scalability (SP6)

- **Approach:** re-run the integrated framework at 10× scale and extended horizon.
- **Mathematical idea:** scaling analysis (linear/nonlinear behavior of flow, congestion, and resolution
  time); identify non-scalable features and new state variables.
- **Key new concerns:** disease control, maternal/childbirth care, education — likely new compartments
  once resolution time exceeds an unspecified threshold (threshold itself is a modeling output to be
  derived later).
- **Pros/cons:** exposes structural limits; may require new parameters and possibly model restructuring.

### 5.7 Integrated architecture (proposed)

A layered pipeline: **Metrics (L1) → Flow optimization (L2) → Dynamic/cascade simulation (L3) →
Policy layer (L4) → Shock scenarios (L5) → Scalability (L6)**, with an assumptions ledger threading
through every layer.

---

## 6. Implementation Roadmap

> This roadmap describes *what will be built later*. No code is written or executed here.

### 6.1 Workflow phases

1. **Phase 0 — Setup.** Environment, directories, provenance logging, configuration registry.
2. **Phase 1 — Data assembly & preprocessing** (per §4).
3. **Phase 2 — Metric layer build** (composite indices, weighting options).
4. **Phase 3 — Flow model build** (network + optimization candidates).
5. **Phase 4 — Dynamic layer** (stock–flow / dynamic network flow / cascade).
6. **Phase 5 — Policy layer** (levers + MCDA comparison).
7. **Phase 6 — Shock scenarios** (parameter-shift ensembles, propagation).
8. **Phase 7 — Scalability study** (10× + horizon extension).
9. **Phase 8 — Validation & sensitivity** (per §7).
10. **Phase 9 — Documentation & policy report synthesis.**

### 6.2 Required modules (to be implemented)

- Data ingestion & provenance module.
- Preprocessing/feature engineering module.
- Metric/index module with configurable weights.
- Network/graph construction module (routes, entry points, destinations).
- Optimization module (LP/MILP/network flow/multi-objective).
- Dynamic simulation module (stock–flow or time-expanded network).
- Resource allocation & prepositioning module.
- Policy-parameter & MCDA module.
- Shock/scenario injection module.
- Scalability harness.
- Validation, sensitivity, and reporting modules.

### 6.3 Algorithms (candidate list)

- Graph/network construction (adjacency, capacities, costs).
- Linear/integer programming; min-cost flow; multi-objective (e.g., ε-constraint, weighted-sum, Pareto).
- Discrete-choice / logit estimation for behavioral route probabilities.
- Numerical integration / time-stepping for dynamic systems.
- Queuing/congestion models for node saturation.
- Monte Carlo / scenario ensembles for uncertainty and shocks.
- Sensitivity analysis (one-at-a-time, global/variance-based, scenario grids).
- MCDA (weighted scoring / AHP-style) for policy ranking.

### 6.4 Tooling and reproducibility plan

- Reproducible pipeline with fixed seeds and configuration files.
- Versioned outputs and an assumptions ledger.
- Modular design so each layer can be swapped/validated independently.
- All numeric inputs traceable to documented sources (or explicitly flagged as assumed/placeholder).

### 6.5 Interfaces between layers

- L1 outputs → parameters/index inputs for L2–L6.
- L2 route/flow decisions → initial conditions for L3.
- L3 dynamics → time-varying constraints fed back to L2 (iterative coupling).
- L4 policy levers → parameters in L2/L3.
- L5 shocks → transient overrides on L2/L3/L4.
- L6 scaling → applies scale factors and horizon changes across all layers.

---

## 7. Validation Strategy

### 7.1 Evaluation metrics (to be defined)

- **Fit/consistency:** agreement between modeled flows and any observed flow series (where available).
- **Safety/efficiency:** route-risk exposure, travel efficiency, unmet-need indicators.
- **Equity:** burden distribution across countries/destinations.
- **Robustness:** outcome stability under parameter perturbation and shocks.
- **Resilience:** recovery time and residual impact after shocks.
- **Scalability:** relative performance and resolution-time behavior at 10× scale.

### 7.2 Validation methods

- **Internal consistency checks** (units, conservation of flow, non-negativity, capacity feasibility).
- **Historical back-check** against the observed 2014–2015 baseline (as available), using held-out
  periods where possible.
- **Face validity** review by domain logic (does the model behave plausibly?).
- **Cross-model comparison:** agreement/divergence across candidate models (L2 variants, L3 variants).
- **Out-of-sample / scenario validation** for shock and policy layers (not for prediction of specific
  politics, but for structural behavior).
- **Expert/stakeholder review** of assumptions and policy translation.

### 7.3 Sensitivity and uncertainty analysis

- **One-at-a-time (OAT)** sweeps on key parameters (safety weights, capacities, costs, policy
  stringency).
- **Global sensitivity** (variance-based, e.g., Sobol-style) to rank influential parameters.
- **Scenario ensembles** for shocks and policy combinations.
- **Weight sensitivity** for composite indices and MCDA to test robustness of rankings.
- **Scaling sensitivity** to identify which parameters dominate as scale/horizon grow.

### 7.4 Validation of assumptions (A1–A14)

Each assumption will carry a testable prediction where feasible, and results will be reported as ranges
rather than point claims when evidence is weak.

---

## 8. Expected Result Interpretation

> Interpretive guidance for the future work — no results are produced here.

- **Metric layer:** expect a ranked set of enabling/inhibiting factors; interpretation will emphasize
  *why* each factor matters and how sensitive conclusions are to weighting choices.
- **Flow layer:** expect system-optimal route/entry allocations and their dependence on safety, capacity,
  and cost; interpretations should present trade-offs (e.g., safety vs. speed) rather than a single
  "answer."
- **Dynamic layer:** expect cascade phenomena — early saturation at preferred destinations rerouting flow;
  interpretation will focus on the mechanism and its sensitivity to capacity growth/prepositioning.
- **Policy layer:** expect comparative policy rankings under explicit criteria; interpretation must
  acknowledge normative choices and legal/cultural constraints, presenting policies as trade-off bundles.
- **Shock layer:** expect identifying which parameters are most shock-sensitive and which policies are
  most resilient; interpretation will be scenario-conditional, not deterministic.
- **Scalability layer:** expect identification of non-scalable features and horizon-triggered new concerns
  (disease, childbirth, education); interpretation will state thresholds qualitatively and flag where the
  model must be restructured.
- **Overall caveat:** all outputs should be framed as conditional, model-based guidance intended to
  support — not replace — human policy judgment.

---

## 9. Limitations and Improvements

### 9.1 Anticipated limitations

- **No staged data:** the local dataset is empty, so the framework will depend on external public
  sources with varying quality, coverage, and definitions.
- **Data scarcity/heterogeneity:** crisis data are noisy, inconsistent, and politically sensitive.
- **Behavioral simplification:** group-level and utility-based assumptions omit rich individual behavior
  and information asymmetry.
- **Central-control assumption:** optimization layers may overstate achievable coordination across
  sovereign states and agencies.
- **Weighting subjectivity:** composite indices and MCDA depend on contested weights.
- **Shock unpredictability:** exogenous events are inherently hard to enumerate or date.
- **Scaling unknowns:** 10× behavior may require structural changes not fully foreseen at design time.
- **Ethical/normative framing:** policy recommendations embed value judgments about health, safety, and
  burden-sharing that must be made transparent.

### 9.2 Planned improvements

- **Triangulate multiple sources** and maintain a provenance/assumptions ledger (A1–A14).
- **Couple behavioral and optimization layers** for more realistic route choice.
- **Introduce agent-based extensions** for heterogeneity and emergent cascades.
- **Expand the destination set** (Canada, China, United States) and test structural adequacy.
- **Institutionalize uncertainty reporting** (ranges, ensembles, sensitivity rankings).
- **Add equity/fairness metrics** and stakeholder-weighted MCDA.
- **Design modular/pluggable layers** so improved sub-models can replace early approximations.
- **Prepare a scalability-robust variant** that pre-anticipates long-horizon concerns (disease,
  childbirth, education) rather than adding them reactively.

### 9.3 Open questions to resolve in the next iteration

- Which candidate flow model (network flow vs. LP/MILP vs. multi-objective vs. utility) best balances
  fidelity and tractability?
- What is the appropriate time cadence and horizon for the dynamic layer?
- How should NGO capacity be modeled (additive resource pool vs. efficiency multiplier)?
- What is the right trigger definition for long-horizon concerns (what "resolution time threshold" applies)?
- How to weight equity vs. efficiency in policy ranking, and who decides?

---

*End of planning blueprint draft. No problem solving, data analysis, computation, or experiments were
performed in producing this document.*
