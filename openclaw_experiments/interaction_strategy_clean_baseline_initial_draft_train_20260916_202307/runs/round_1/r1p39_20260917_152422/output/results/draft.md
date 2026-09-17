# The Modeling Musical Tour — Initial Modeling Plan Draft

**Problem ID:** 2024_The_Modeling_Musical
**Title:** The Modeling Musical Tour
**Source:** MidMCM 2024, Problem C
**Document type:** Modeling blueprint draft (planning only — no solution, no data analysis, no computations)

---

## 1. Problem Background and Restatement

The problem situates us as a tour manager at the "MidMCM Music Agency." A world-touring
musical performer (the problem uses Taylor Swift's Eras Tour as its motivating example:
roughly 152 shows, ~3.5 hours each, ~72,000 fans per US show, ~$13 million revenue per show,
first tour to exceed $1 billion) has completed past tours. Our task is to design and justify
a plan for that performer's *next* tour.

The problem asks us to:

1. **Select a performer** with at least one documented past tour, and investigate why they
   toured, how long it lasted, how many shows, and which locations were chosen.
2. **Develop a model** that captures planning decisions — number of concerts, venues, ticket
   prices — and that optimizes a chosen objective (attendance, number of venues, profit, or
   another defensible goal).
3. **Apply the model** retrospectively to a past tour (to expose strengths/weaknesses) and
   prospectively to plan a future tour with improvements.
4. **Communicate** the plan in a one- to two-page letter to the performer.
5. **Reflect** on transferability to other performers and on the model's limitations.

**Deliverables implied by the statement:** a one-page summary sheet, a complete solution
(≤ 25 pages), and a one- to two-page letter. This draft covers only the roadmap that would
produce those deliverables.

**Intended scope of this draft:** describe *how* the problem will be approached — objectives,
assumptions, candidate modeling frameworks, data strategy, implementation steps, and
validation. It deliberately stops short of selecting a performer definitively, computing any
numbers, or drawing any conclusions.

---

## 2. Objectives and Subproblems

### 2.1 Primary objective
To construct a defensible, reproducible optimization/simulation model that recommends a
tour schedule (cities, venues, show counts, pricing) for a chosen performer's next tour,
while balancing competing goals such as attendance, revenue/profit, geographic coverage,
artist fatigue, and fan accessibility.

### 2.2 Subproblems to be decomposed

- **SP1 — Performer and historical tour characterization.**
  Decide on a selection criterion for the performer (e.g., multiple completed tours with
  public scheduling/pricing data) and define what a "tour profile" consists of: duration,
  number of shows, routing, venue sizes, ticket tiers, and stated motivation.

- **SP2 — Single-show economics.**
  Conceptualize the revenue and cost structure of one show: ticketing tiers, venue capacity,
  fixed vs. variable costs, and the notion of an "equilibrium" ticket price under demand.

- **SP3 — Multi-show coordination.**
  Conceptualize how shows link into a route: city selection, travel and rest constraints,
  venue assignment, sequencing, and the coupling between adjacent legs.

- **SP4 — Objective formalization.**
  Define one or more candidate objective functions (attendance, profit, venue count,
  coverage-weighted or multi-objective) and the constraint set that bounds them.

- **SP5 — Retrospective application.**
  Specify how the model will be "replayed" against a past tour to diagnose strengths and
  weaknesses (e.g., unmet demand, suboptimal routing, pricing headroom).

- **SP6 — Prospective tour design.**
  Specify how the calibrated model will generate a recommended future schedule and how
  alternative scenarios will be compared.

- **SP7 — Communication and reflection.**
  Plan the structure of the performer letter and the discussion of generality/limitations.

### 2.3 Decision variables (conceptual, non-numerical)
City/region selection, venue selection and capacity, number of shows per stop, ticket price
tiers, scheduling/routing decisions, and tour length.

---

## 3. Assumptions

The following assumptions are proposed for the eventual model; each is stated with a
justification and a planned validation route. All are provisional and will be revisited during
implementation.

### 3.1 Domain / selection assumptions
- **A1.** The chosen performer has at least one completed tour with publicly documented
  schedules, venues, and (ideally) pricing. *Justification:* enables calibration.
  *Validation:* confirm data availability before locking the performer choice.
- **A2.** The performer's next tour is intended to be a large-venue, multi-city tour
  comparable in scale to the historical tour. *Justification:* keeps the model within a
  realistic regime. *Validation:* cross-check against stated career stage and prior size.

### 3.2 Demand assumptions
- **A3.** Demand for a show in a city can be represented as a decreasing function of ticket
  price, with a city- and venue-specific scale. *Justification:* standard microeconomic
  demand modeling. *Validation:* sensitivity across demand-curve families.
- **A4.** City-level demand potential is proxied by observable market features (population,
  income, prior tour attendance/sellout history, comparable-artist activity). *Justification:*
  these are the features a manager could realistically obtain. *Validation:* feature
  importance and hold-out behavior.

### 3.3 Cost assumptions
- **A5.** Costs decompose into a fixed per-show component and a variable per-attendee
  component, plus a travel/route component. *Justification:* tractable and interpretable.
  *Validation:* sanity bounds and scenario testing.
- **A6.** Pricing is primarily a management decision rather than a pure auction; dynamic
  pricing will be treated as a bounded set of tiers, not a continuous process.
  *Justification:* reflects real ticketing practice. *Validation:* compare against tiered
  vs. single-price scenarios.

### 3.4 Operational assumptions
- **A7.** Venue capacities and availability are treated as known constraints for candidate
  cities. *Justification:* reduces the search space. *Validation:* scarcity sensitivity.
- **A8.** Feasible routing must respect travel/rest limits between consecutive stops.
  *Justification:* artist fatigue and logistics are real constraints. *Validation:* vary
  rest parameters.

### 3.5 Simplifying assumptions (to be flagged as limitations)
- **A9.** Secondary markets, resale, and dynamic resale pricing are ignored at first pass.
- **A10.** Weather, local competition, and macro shocks are excluded from the base model.
- **A11.** Fan travel between cities is not modeled explicitly in the base case.

Each of A9–A11 will be recorded as an explicit limitation and revisited in Sections 8–9.

---

## 4. Data Processing Plan

### 4.1 Data needs (to be collected later — none analyzed here)
- **Historical tour data:** dates, cities, venues, capacities, number of shows, sellout
  status, reported attendance, reported gross, ticket price tiers/range.
- **Market/geographic features:** city population, regional income metrics, distance matrix
  between candidate cities, venue inventory and capacities by city.
- **Cost proxies:** typical venue operating costs, crew/logistics cost indicators, travel
  cost proxies.
- **Qualitative inputs:** stated tour motivation, artist statements, industry commentary.

### 4.2 Sources (to be evaluated)
Official tour archives, ticketing/reporting trade publications, venue websites and capacity
registries, and public geographic/economic datasets. Source reliability will be graded and
documented (see Section 7).

### 4.3 Preprocessing steps (planned)
1. **Schema harmonization** — unify heterogeneous tour records into a common table
   (city, venue, date, capacity, attendance, price, gross).
2. **Unit normalization** — currency and capacity units standardized; inflation handling
   policy decided and documented.
3. **Missing-value policy** — rule set for imputation vs. exclusion, applied per column.
4. **Outlier/anomaly screening** — flagging (not deleting) anomalous shows for review.
5. **Deduplication and city/venue canonicalization** — consistent place names and IDs.

### 4.4 Feature construction (planned)
- Per-city demand-potential index from market features.
- Per-venue capacity and tier structure features.
- Inter-city distance/travel-time features from the distance matrix.
- Historical sellout rate and price-per-tier features where available.
- Derived "reachability set" of cities within feasible travel windows.

### 4.5 Data usage strategy
- **Calibration set:** historical tour records used to fit/parameterize demand and cost
  components.
- **Retrospective set:** the past tour used for the strength/weakness diagnosis (may overlap
  with calibration; overlap policy will be documented to avoid leakage).
- **Scenario set:** market features for candidate future cities used for prospective design.
- **Hold-out logic:** where data volume permits, a temporal or geographic hold-out will be
  reserved for evaluation.

---

## 5. Candidate Model Framework

Multiple candidate frameworks will be considered; the plan is to evaluate trade-offs before
committing to one primary model, possibly combining a small set.

### 5.1 Candidate models

- **M1 — Economic equilibrium / demand-pricing model.**
  Represent attendance as a function of price and city demand potential; derive optimal
  single-show pricing and capacity utilization. *Advantages:* interpretable economics, links
  price to attendance. *Limitations:* single-show view; ignores routing coupling.

- **M2 — Integer / mixed-integer optimization for tour design.**
  Decision variables for city selection, show counts, venue assignment; constraints for
  capacity, travel, rest, budget; objective on profit/attendance/coverage. *Advantages:*
  handles combinatorial scheduling and explicit constraints. *Limitations:* needs
  linearizable objectives; demand nonlinearity must be approximated.

- **M3 — Multi-objective optimization (Pareto) framework.**
  Trade off profit vs. attendance vs. geographic coverage vs. artist workload; produce a
  Pareto frontier for managerial choice. *Advantages:* surfaces trade-offs central to the
  problem. *Limitations:* interpretation and decision-tooling overhead.

- **M4 — Stochastic demand-simulation / scenario model.**
  Model demand and sellout uncertainty via scenarios or Monte Carlo, evaluating robustness
  of candidate schedules. *Advantages:* captures risk and capacity mismatches.
  *Limitations:* requires distributional assumptions.

- **M5 — Heuristic routing layer (TSP/VRP-style).**
  Given a selected city set, sequence stops under travel/rest constraints.
  *Advantages:* realistic logistics; complements M2. *Limitations:* depends on upstream
  city selection.

### 5.2 Recommended integration (tentative)
A layered approach is proposed: **M1** supplies per-show economics; **M2/M3** select cities
and show counts under constraints; **M5** sequences the route; **M4** stress-tests the
resulting plan. This layering will be revisited if complexity becomes unmanageable; a simpler
two-layer (economics + optimization) version will be the fallback.

### 5.3 Mathematical ideas to be drawn upon
Demand curves and elasticity, revenue/cost decomposition, facility-capacity/assignment
formulation, network/routing formulation, multi-objective scalarization and Pareto analysis,
and sensitivity/robustness analysis.

### 5.4 Key variables (conceptual)
- Decision: city set, venue assignment, shows per stop, ticket tiers, order of stops.
- Environmental/parameter: capacities, distances, demand-potential indices, cost rates,
  travel/rest limits.
- Output: attendance, revenue, profit, number of stops/shows, coverage, workload.

---

## 6. Implementation Roadmap

### 6.1 Algorithms and modules (planned)
1. **Data ingestion & cleaning module** — parse, harmonize, canonicalize (Section 4).
2. **Feature engineering module** — demand-potential index, distance matrix, venue features.
3. **Calibration module** — fit demand and cost components against historical tour records.
4. **Optimization module** — solve the city/show-selection problem (MILP/MO formulation),
   with a heuristic fallback for large instances.
5. **Routing module** — sequence selected stops under travel/rest constraints.
6. **Scenario/simulation module** — evaluate robustness and alternative objectives.
7. **Reporting/visualization module** — produce comparison tables/figures (to be generated
   in the eventual solution, not in this draft).
8. **Letter-generation outline** — translate the recommended plan into narrative form.

### 6.2 Workflow sequence
Define performer & data → clean & build features → calibrate economics → optimize city/show
plan → route & schedule → stress-test scenarios → diagnose past tour → design future tour →
draft letter → document limitations.

### 6.3 Tooling (to be chosen)
A general-purpose scripting environment for data handling and optimization
(e.g., Python with standard data/optimization libraries) and a solver suitable for MILP.
Tool selection is provisional and will be finalized at implementation time.

### 6.4 Milestones and artifacts
- **Artifact 1:** Data dictionary and cleaned dataset description.
- **Artifact 2:** Documented assumptions register (Section 3).
- **Artifact 3:** Calibrated demand/cost specification.
- **Artifact 4:** Optimization results and alternative schedules.
- **Artifact 5:** Retrospective diagnosis of the past tour.
- **Artifact 6:** Prospective tour plan + performer letter draft.

---

## 7. Validation Strategy

### 7.1 Evaluation metrics (planned)
- **Predictive fit (retrospective):** how well the model reproduces past attendance/revenue
  patterns (error-based metrics such as MAE/MAPE, to be computed later).
- **Optimization quality:** objective value improvement vs. baseline schedules; constraint
  satisfaction and feasibility rate.
- **Robustness:** stability of recommended schedules under demand perturbations.
- **Trade-off insight:** coverage/quality of the Pareto frontier (spread and interpretability).
- **Plausibility:** agreement with domain-consistent expectations (e.g., large markets
  attract more shows).

### 7.2 Validation methods
- **Temporal hold-out** within the historical tour where feasible.
- **Geographic hold-out:** predict/reconstruct held-out cities from market features.
- **Baseline comparison:** compare optimized plan against the actual past schedule and a
  simple heuristic plan.
- **Cross-model comparison:** compare MILP vs. heuristic vs. simpler greedy solutions.
- **External consistency checks:** sanity-check against publicly reported magnitudes.

### 7.3 Sensitivity analysis (planned)
One-at-a-time and (where feasible) joint sensitivity on: demand elasticity, capacity
assumptions, cost components, travel/rest limits, objective weighting, and price-tier
structure. Report ranges rather than point claims.

### 7.4 Assumption auditing
Each assumption in Section 3 will be revisited with a test or a qualitative argument, and
assumptions that materially change recommendations will be elevated to primary limitations.

---

## 8. Expected Result Interpretation

This section describes how eventual outputs *would* be read; no results are produced here.

- **Model outputs** are expected to include a recommended schedule (cities, show counts,
  venues), a pricing strategy, and summary performance under the chosen objective(s).
- **Retrospective outputs** would be interpreted as diagnostic signals: areas where the past
  tour appeared capacity-constrained, underpriced, or over-routed — phrased as hypotheses to
  be confirmed, not verdicts.
- **Prospective outputs** would be framed as conditional recommendations: "if objective X and
  assumptions Y hold, then schedule Z is preferred." Alternative objectives would be presented
  as scenarios rather than a single optimum.
- **Uncertainty framing:** findings would be reported with sensitivity ranges so the performer
  and management can weigh risk.
- **Managerial translation:** the letter would convert model outputs into plain-language
  rationale aligned with the performer's stated goals.

---

## 9. Limitations and Improvements

### 9.1 Anticipated limitations
- **Data quality/coverage:** incomplete or inconsistent public tour data may bias calibration.
- **Demand simplification:** aggregate demand curves omit heterogeneity, resale markets, and
  fan travel.
- **Static vs. dynamic pricing:** tiered/static treatment underrepresents real ticket dynamics.
- **Exogenous shocks:** macro/health/competition effects are excluded from the base model.
- **Solver tractability:** large city/venue sets may force approximations or heuristics.
- **Objective subjectivity:** choice of objective and weights encodes value judgments.

### 9.2 Planned improvements / extensions
- Add stochastic/resale-market layers and richer demand heterogeneity.
- Incorporate dynamic or multi-stage pricing.
- Extend routing with multi-modal travel and venue-availability calendars.
- Generalize the framework to other performers/artists and validate transferability.
- Build an interactive scenario tool for managerial "what-if" exploration.

### 9.3 Generalization to other performers
The layered framework (economics → optimization → routing → robustness) is intended to be
performer-agnostic, with calibration re-run per artist. Transferability will be discussed in
terms of data availability, venue scale, and objective priorities.

---

## Appendix A — Planning Checklist

- [ ] Confirm performer selection criteria and data availability.
- [ ] Lock the assumptions register and document justifications.
- [ ] Finalize data cleaning and feature engineering rules.
- [ ] Choose primary + fallback model frameworks.
- [ ] Define objective(s) and constraint set precisely.
- [ ] Specify validation metrics and hold-out scheme.
- [ ] Prepare retrospective diagnosis plan.
- [ ] Prepare prospective scenario comparison plan.
- [ ] Outline the performer letter.
- [ ] Document limitations and transferability.

> **Note:** This document is a planning blueprint. It contains no computed results, no data
> analysis, no fitted models, and no final conclusions, consistent with the Modeling Planner
> role.
