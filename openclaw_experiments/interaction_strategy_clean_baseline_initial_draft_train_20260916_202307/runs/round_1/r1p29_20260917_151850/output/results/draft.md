# Modeling Blueprint (Initial Draft): Storing the Sun

> **Status notice.** This document is a planning artifact only. It defines the intended workflow, assumptions, candidate models, data plan, implementation roadmap, and validation strategy for a future modeling effort. It intentionally contains **no computed results, no fitted models, no executed experiments, and no final conclusions**. All statements are forward-looking ("will", "is expected to").

Problem ID: `2021_Storing_the_Sun` · Source: HiMCM 2021, Problem A
Workspace: `output/` (subfolders `code/`, `data/`, `logs/`, `results/`)

---

## 1. Problem Background and Restatement

The task concerns designing a solar-powered electricity system, with an emphasis on **energy storage**, for a roughly 1600 square-foot home in a remote area. Solar generation is intermittent: it produces no energy at night and reduced energy during cloudy periods. A storage system (a single battery or a bank of batteries) must bridge generation gaps so the home is reliably served.

The problem will be restated as a decision problem in five connected parts:

1. **Energy needs analysis** — estimate the home's electricity demand profile (how many occupants, which appliances, how much energy each uses, and *when* energy is drawn).
2. **Model development** — formulate a mathematical model/algorithm that selects the "best" battery storage system given the demand profile and a set of criteria.
3. **Battery selection** — apply the model to choose among the five catalogued battery options (lead-acid gel, flooded lead-acid, and several lithium chemistries).
4. **Model generalization** — assess how the model adapts to different homes and owner preferences.
5. **Cement batteries** — explore cement-based energy storage: its promise, limitations, integration into a home system, and what additional data would be required to compare it fairly with current options. A non-technical news-style article is a required deliverable.

The supplied battery catalogue (cost, chemistry, weight, dimensions, continuous power, instantaneous power, round-trip efficiency, usable capacity) will serve as the core structured dataset. Note that the battery table is the only explicit quantitative input; the demand side must be constructed from documented assumptions and external references.

---

## 2. Objectives and Subproblems

**Primary objective.** Build a defensible, reproducible decision framework that recommends a battery storage configuration for a 1600 sq-ft remote home, and that generalizes to other homes and to emerging technologies such as cement batteries.

**Subproblems to be scoped (design-level only):**

- **S1 — Demand characterization.** Define a procedure to convert occupants + appliance inventory + usage timing into a daily/annual load profile and a peak-power profile.
- **S2 — Sizing/storage feasibility.** Define the constraints linking a candidate bank's usable capacity, continuous/instantaneous power, and efficiency to the demand profile (energy autonomy for night + specified cloudy days; peak-power coverage).
- **S3 — Multi-criteria selection.** Define a scoring/optimization rule that trades off capital cost, lifetime/levelized cost, efficiency, reliability, maintenance, safety, footprint, and weight.
- **S4 — Generalization.** Define how inputs (home size, occupancy, climate/insolation region, backup-days requirement, budget, sustainability preference) parameterize the model so it can be re-instantiated for other homes.
- **S5 — Cement battery assessment.** Define a comparative framework and an explicit list of missing parameters required for a fair comparison.
- **S6 — Communication.** Define the structure of a non-technical article translating the decision model and future outlook into accessible language.

**Deliverable mapping (future).** Each subproblem will map to a section of the final paper, a module in `code/`, and an entry in `results/`.

---

## 3. Assumptions

Assumptions will be explicit, justified, and paired with a validation approach. Categories:

**A. Load/demand assumptions**
- A1. Occupancy will be modeled as a small household (a range will be parameterized rather than fixed).
- A2. Appliance inventory will be drawn from typical residential appliance power/usage references; each appliance will be assigned an average power and a duty schedule.
- A3. Load timing will be modeled as a representative daily profile (morning/evening peaks) plus seasonal variation.
- A4. A design margin (safety factor) will account for losses, degradation, and demand growth.
- *Validation:* cross-check against published residential consumption benchmarks and utility-style load-shape references; scenario-test the profile shape.

**B. Battery/system assumptions**
- B1. Usable capacity will be interpreted together with stated efficiency and a depth-of-discharge convention appropriate to each chemistry.
- B2. Continuous/instantaneous power ratings constrain short-duration peaks (inrush/appliance startup).
- B3. Banks will be modeled as parallel/series combinations of identical units, respecting voltage/current limits.
- B4. Environmental derating (temperature, aging) will be modeled at the parameter level, not chemistry-specific detail initially.
- *Validation:* sensitivity analysis on efficiency, depth of discharge, and derating factors.

**C. Economic/operational assumptions**
- C1. Costs will be evaluated both as upfront capital and as a lifetime/levelized-cost concept; discount rate and horizon will be parameters.
- C2. Replacement/maintenance cadence will differ by chemistry and will be an explicit input.
- C3. Only electricity storage is in scope (no thermal storage), unless later added as an extension.
- *Validation:* breakeven and sensitivity analysis across discount rates and lifespans.

**D. Cement battery assumptions**
- D1. Cement storage will be treated as a technology with uncertain but bounded performance parameters (energy density, efficiency, cycle life, power).
- D2. Because data will be incomplete, cement will be placed in a comparative/what-if framework rather than scored on equal footing initially.
- *Validation:* documented parameter ranges from literature; explicit "data-gap" register.

**E. Scope boundaries**
- E1. No grid connection is assumed (remote location).
- E2. Solar array sizing is a companion input; storage sizing will be considered jointly but the focus remains storage.

---

## 4. Data Processing Plan

**Data sources (planned).**
1. **Provided catalogue (primary structured data):** the five battery rows with cost, chemistry, weight, dimensions, continuous power, instantaneous power, efficiency, and capacity.
2. **Reference/derived data (to be collected):** appliance power/usage tables, residential load-shape references, solar insolation/availability by region, economic parameters (discount rate, electricity value), and cement-battery literature ranges.

**Preprocessing steps (planned).**
- Parse the catalogue into a tidy table with consistent units (USD, kW, kWh, lbs, inches).
- Normalize ranges (e.g., efficiency given as a band; power given as load-dependent values) into a defined point estimate plus an uncertainty band, with the rule for choosing the point value documented.
- Derive volume and footprint from dimensions; derive capacity/weight ratios where useful as features.
- Flag missing values (e.g., instantaneous power "N/A" for lead-acid) and define how they will be handled (treated as a constraint on peak coverage rather than imputed blindly).

**Feature construction (planned).**
- **Economic features:** capital cost per usable kWh, cost per cycle, levelized-cost ingredients.
- **Performance features:** usable energy, continuous/instantaneous power, round-trip efficiency.
- **Physical features:** weight, volume, footprint.
- **Robustness features:** chemistry-specific qualitative attributes (maintenance, safety, lifespan) encoded via a documented rubric.

**Data usage strategy.**
- The catalogue will feed the feasibility filter and the multi-criteria scoring.
- Demand and economic tables will be parameterized so the model can be re-run for other homes.
- A **data-gap register** will list every assumption-derived or missing quantity, its source/justification, and its effect on conclusions.
- No value will be treated as exact; all inputs will carry a range for sensitivity analysis.

---

## 5. Candidate Model Framework

The framework will be layered so each layer can be validated independently.

**Layer 1 — Demand model.**
- Build a daily/annual load profile from the appliance inventory and schedules (start with an hourly resolution, aggregated to daily totals and peak).
- Candidate representations: (a) deterministic scenario profiles (base/peak/seasonal), (b) a simple stochastic/statistical load generator for variability, (c) an extreme-day design case for autonomy sizing.

**Layer 2 — Storage feasibility / sizing model.**
- Constraint-based sizing: usable capacity must satisfy night + N cloudy-day autonomy, adjusted by round-trip efficiency and depth-of-discharge; power ratings must cover peak and inrush.
- Candidate formulations: (a) closed-form energy-balance sizing, (b) an energy-flow simulation over the load/generation time series, (c) a small optimization (linear/integer) to pick a bank configuration (number of units, series/parallel) minimizing cost subject to constraints.

**Layer 3 — Multi-criteria decision model.**
- Candidate methods (to be compared, not assumed): weighted-sum / weighted-product scoring, TOPSIS, AHP for weight elicitation, and a Pareto-front analysis across cost vs reliability vs lifetime.
- Weights will be treated as *preference parameters*, enabling the generalization subproblem (different owners → different weights).

**Layer 4 — Economic/lifecycle model.**
- Levelized cost of storage and payback framing, with discounting and replacement schedules as parameters.

**Layer 5 — Cement-battery comparative model.**
- A parameterized version of Layers 2–3 in which cement-technology parameters are varied across literature-informed ranges, producing a break-even/what-if analysis rather than a definitive ranking.

**Variables (planned, qualitative listing).**
- Decision variables: number/type of battery units, bank topology, backup-days target.
- Parameters: load profile, efficiency, depth of discharge, derating, costs, discount rate, preference weights, insolation.
- Outputs: feasibility (yes/no), recommended configuration, score/ranking, levelized cost, sensitivity ranges.

**Advantages and limitations (to be recorded for each candidate).**
- Closed-form sizing: transparent, fast; limited realism.
- Time-series simulation: realistic dynamics; more parameters and data needs.
- Optimization: prescriptive and constraint-aware; sensitive to objective/weight choices.
- MCDM methods: handle heterogeneous criteria; sensitive to weights and normalization.
- Comparative cement model: flexible under uncertainty; conclusions bound by data quality.

---

## 6. Implementation Roadmap

**Planned modules (in `code/`).**
- `data_ingest` — read/clean the catalogue and reference tables; unit normalization.
- `demand_model` — assemble the load profile from appliance/schedule inputs.
- `storage_model` — feasibility/sizing and energy-flow simulation.
- `bank_optimizer` — configuration optimization under constraints.
- `mcdm` — scoring/ranking with configurable weights.
- `economics` — levelized cost / payback computations.
- `cement_compare` — parameterized comparison and data-gap handling.
- `pipeline` — orchestrate end-to-end runs; write artifacts to `results/`.
- `reporting` — tables/figures for the paper and the news article (no results produced at plan stage).

**Workflow (planned).**
1. Define scenarios (baseline home + generalized homes).
2. Ingest and normalize data.
3. Construct demand profiles.
4. Run feasibility/sizing for each battery option.
5. Optimize bank configuration per option.
6. Score/rank options under multiple weight sets.
7. Compute economic indicators.
8. Run cement comparison under parameter ranges.
9. Sensitivity/uncertainty analysis.
10. Freeze artifacts for the write-up and article.

**Engineering practices (planned).**
- Configuration-driven runs (YAML/JSON) so scenarios and weights are data, not code.
- Deterministic seeds for any stochastic load generation; full run logs in `logs/`.
- Unit tests for unit conversion, constraint logic, and normalization.
- Every output traceable to an input assumption via the data-gap register.

---

## 7. Validation Strategy

**Internal validation (planned).**
- Unit consistency and dimensional checks across all models.
- Energy-balance audit: simulated supply must equal/dispatch load plus losses over the horizon.
- Constraint satisfaction checks (autonomy, peak power, topology validity).

**Cross-validation / robustness.**
- Compare sizing results across the three Layer-2 formulations (closed-form vs simulation vs optimization); disagreements flag modeling risk.
- Compare ranking stability across MCDM methods (weighted-sum vs TOPSIS vs AHP) and across weight sets.

**Sensitivity analysis (planned).**
- One-at-a-time sensitivities on efficiency, depth of discharge, derating, load magnitude/shape, discount rate, lifespan, and backup-days target.
- Multi-factor/scenario analysis (best/worst/base cases) and, where feasible, Monte Carlo sampling over uncertain inputs.
- Critical-threshold identification: which parameters flip the recommended choice.

**External/qualitative validation.**
- Sanity-check demand estimates against published residential benchmarks.
- Sanity-check economic outputs against typical market ranges for the same chemistries.
- For cement batteries, validate parameter ranges against multiple literature sources and document disagreements.

**Success criteria (planning-level).**
- The framework is reproducible from configurations, robust to reasonable input variation, transparent about assumptions, and consistent across methods.

---

## 8. Expected Result Interpretation

This section describes how future outputs will be *read*, not what they will be.

- **Feasibility outcomes** (which options can meet autonomy and peak constraints) will be interpreted jointly with their capital cost and lifecycle cost, since feasibility alone may exclude cheaper options.
- **Rankings** will be presented as preference-dependent: the "best" battery will be reported as a function of owner priorities (cost vs reliability vs maintenance vs sustainability).
- **Levelized-cost figures** will be interpreted as comparative indicators under stated assumptions, with break-even interpretations for competing chemistries.
- **Generalization results** will be read as evidence of model flexibility (how recommendations shift with home size, occupancy, climate, and budget).
- **Cement-battery results** will be interpreted as scenario/what-if statements, explicitly bounded by data quality and parameter uncertainty, and accompanied by the data needed to firm up the comparison.

---

## 9. Limitations and Improvements

**Anticipated limitations.**
- Demand side relies on assumptions and reference data rather than a measured household.
- Battery performance parameters are simplified (bands collapsed to point estimates with ranges).
- Single-value weights can obscure preference trade-offs if not reported as fronts.
- Cement-battery data will be sparse/uncertain, limiting firm conclusions.
- Environmental/aging effects modeled at a coarse level initially.

**Planned improvements / extensions.**
- Incorporate stochastic load and solar generation for probabilistic autonomy.
- Add joint solar-array + storage co-optimization.
- Introduce degradation-aware lifecycle costing and multi-year replacement optimization.
- Extend MCDM with robust/regret-based decision rules.
- Add thermal and safety modeling, and grid-interaction scenarios for non-remote homes.
- Build a user-facing scoring tool so non-technical owners can set their own weights (supporting the news article's narrative).

**Open questions to resolve during modeling.**
- Preferred resolution of the load profile (hourly vs daily aggregated).
- How to treat the ambiguous lead-acid power/efficiency ranges.
- Which MCDM method will serve as primary versus cross-check.
- How much cement-battery uncertainty is tolerable before the comparison becomes non-actionable.

---

*End of planning draft. No analysis, computation, or conclusions were produced in this document.*
