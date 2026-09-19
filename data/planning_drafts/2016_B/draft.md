# Modeling Blueprint Draft — MM-Bench 2016_B
## A Time-Dependent Decision Model for Commercial Space-Debris Removal

> **Status:** Planning draft only. This document is a modeling roadmap (workflow, assumptions,
> candidate methods, data plan, implementation plan, validation strategy). It contains **no
> solved results, no fitted parameters, no executed experiments, and no final conclusions.**
> All statements describe what *will be* or *is planned to be* done.

---

## 1. Problem Background and Restatement

### 1.1 Context
Earth orbit hosts an estimated population of more than 500,000 tracked/untracked debris
objects ranging from paint flakes to abandoned satellites. The 2009 Kosmos-2251 / Iridium-33
collision demonstrated that even a single conjunction can degrade the orbital environment and
threaten spacecraft. Because debris objects orbit at very high relative velocities, capture and
removal are technically difficult and expensive. Proposed removal approaches include small
space-based water jets, high-energy lasers targeting specific objects, and large "sweeper"
satellites, among others.

### 1.2 What the Model Must Deliver
A **time-dependent model** that:
1. Evaluates **independent alternatives** and **combinations of alternatives** for debris removal.
2. Quantifies **costs, risks, benefits** and other important (possibly qualitative) factors.
3. Represents the space-debris environment as a **dynamic system** evolving over a planning horizon.
4. Supports exploration of **"What if?" scenarios** (budget, technology, regulation, demand, environment).
5. Answers two linked decision questions:
   - Does an **economically attractive commercial opportunity** exist for a private firm?
   - If yes: how do the alternatives compare, and which removal strategy/combination is recommended?
   - If no: what **innovative collision-avoidance alternatives** should be recommended instead?

### 1.3 Restatement as a Modeling Problem
Restated as an operations-research / systems-dynamics problem, the task is to build a
**stochastic, time-indexed cost–risk–benefit decision model** in which:
- A **state** describes the debris environment and the firm's assets/finances at each time step.
- **Control/decision variables** select which alternatives (or mix) to deploy, when, and at what scale.
- The **objective** is to maximize an economic attractiveness measure (e.g., discounted net
  benefit / risk-adjusted return) subject to budget, technical, and regulatory constraints, while
  tracking risk and non-monetized benefits.
- The model must be **scenario-parametric** so that "what if?" questions can be answered by
  re-evaluating under alternative parameter sets rather than re-deriving the model.

---

## 2. Objectives and Subproblems

### 2.1 Primary Objective
Determine whether a private firm can profitably undertake space-debris removal (alone or in
combination), and produce a defensible recommendation — or, if no opportunity exists,
recommend advanced collision-avoidance strategies.

### 2.2 Subproblems (planned decomposition)
| # | Subproblem | Question it will answer |
|---|---|---|
| S1 | **Environment dynamics** | How will the debris population (by size, mass, altitude, inclination) evolve over the horizon under launch, decay, and collision processes? |
| S2 | **Collision-risk model** | What is the time-dependent probability/expected number of damaging collisions, and how does removal change it? |
| S3 | **Alternative characterization** | What are the technical performance envelopes (objects/unit-time removable, altitude/size coverage) of each alternative and combinations? |
| S4 | **Cost model** | What are the R&D, manufacturing, launch, and operating costs over time for each alternative/mix? |
| S5 | **Benefit & revenue model** | What monetizable and non-monetizable benefits/revenues can a private firm capture (services, contracts, insurance, data, servicing)? |
| S6 | **Risk & uncertainty model** | What are technical, financial, regulatory, and liability risks, and how are they quantified/propagated? |
| S7 | **Decision/portfolio model** | Which single alternative or combination is economically optimal under constraints and uncertainty? |
| S8 | **Scenario engine** | How do rankings and viability react to "what if?" perturbations? |
| S9 | **Fallback design** | If no opportunity exists, which collision-avoidance options dominate? |

### 2.3 Deliverables (planned)
- A documented **model architecture** and assumption register.
- A **scenario-parametric simulator** linking environment → risk → cost/benefit → decision.
- A **comparison framework** for alternatives and combinations.
- A **sensitivity/what-if analysis protocol**.
- An **interpretation guide** mapping model outputs to a recommendation logic (with the
  fallback branch to collision avoidance).

---

## 3. Assumptions

Assumptions will be logged in an **assumption register** with three fields each: statement,
justification, and planned validation approach. Initial assumptions to be adopted and later
tested:

### 3.1 Environment / Physical
- **A1.** The environment will be discretized into altitude shells × size/mass classes (and
  possibly inclination bands); within-shell behavior will be treated as a well-mixed population.
- **A2.** Orbital decay will be modeled as a deterministic (or solar-activity-parameterized)
  function of altitude and area-to-mass ratio; solar cycle effects will enter as exogenous scenarios.
- **A3.** Collision events will be modeled as a Poisson-type process whose rate depends on
  object densities and relative-velocity distributions.
- **A4.** Debris fragmentation (collisional cascading) will be represented by a
  source term derived from a chosen fragment-distribution law (to be selected, not yet fitted).
- **A5.** Launch traffic and post-mission-disposal compliance will be treated as exogenous
  scenario inputs rather than predicted endogenously in the first iteration.

### 3.2 Economic / Institutional
- **A6.** The firm will be modeled as risk-aware and financially constrained, optimizing a
  discounted, risk-adjusted objective over a multi-decade horizon.
- **A7.** Debris removal will be treated as having **public-good characteristics**; the model
  will therefore explicitly represent plausible **revenue mechanisms** (government/agency
  contracts, insurance-linked incentives, service subscriptions, SSA/data products, salvage,
  or regulatory credit) rather than assuming a market price exists.
- **A8.** Costs will be expressed in constant currency with an explicit discount rate that
  will be a key sensitivity variable.
- **A9.** Liability and policy will be treated as scenario constraints derived from existing
  space-law frameworks, without attempting a legal determination.

### 3.3 Modeling / Methodological
- **A10.** Qualitative factors will be handled via a multi-criteria layer rather than forced
  into monetary units where conversion is not defensible.
- **A11.** Model granularity will be chosen as a trade-off between fidelity and tractability;
  both a coarse continuum model and a finer Monte Carlo variant will be planned for cross-checking.
- **A12.** Parameter values not available from staged data will be sourced from public
  datasets or elicited from experts, and flagged with provenance and confidence levels.

### 3.4 Future Validation of Assumptions
Each assumption will be revisited through the validation plan in §7 (limiting-case checks,
cross-model comparison, literature/dataset benchmarking, and sensitivity analysis).

---

## 4. Data Processing Plan

> **Note:** The staged `data/` directory is currently empty and the problem's dataset
> definition contains no paths/descriptions. The data plan is therefore primarily an
> **acquisition-and-synthesis plan**, with a preprocessing pipeline designed to accept
> whatever catalog/environment data become available.

### 4.1 Data to be Acquired or Synthesized
| Category | Example sources (planned) | Intended use |
|---|---|---|
| Object catalog / populations | Public debris catalogs, two-line-element style element sets, orbital-debris environment model outputs | S1, S2 |
| Physical/statistical parameters | Size–mass distributions, area-to-mass ratios, fragment laws, decay relations | S1, S3 |
| Collision/conjunction history | Historical on-orbit collision and breakup records | S2 validation |
| Cost data | Launch cost per unit mass, spacecraft bus costs, instrument costs, comparable removal-mission budgets | S4 |
| Market/revenue data | Space insurance premiums, servicing contracts, agency budgets | S5 |
| Policy/regulatory | Existing space-law texts, mitigation guidelines | A9, S7 constraints |
| Expert judgment | Elicited ranges for uncertain technical/economic parameters | uncertainty priors |

### 4.2 Preprocessing (planned)
- **Cleaning & deduplication** of catalog records; handling of missing/erroneous orbital elements.
- **Unit harmonization** (SI) and **epoch alignment** to a common time base.
- **Binning** into altitude shells, size/mass classes, and inclination bands.
- **Outlier/anomaly flagging** and documentation of exclusions.
- **Uncertainty tagging**: each derived quantity will carry a range or distribution rather than a point value.
- **Provenance log**: every dataset will be recorded with origin, retrieval date, and license/usage note.

### 4.3 Feature Construction (planned derived quantities)
- Debris **spatial density** per shell and **mass/area distribution** per class.
- **Flux/encounter-rate** metrics per shell and per protected-asset template.
- **Expected decays** and **residence times** by altitude.
- **Cost-per-object-removed** and **cost-per-unit-risk-reduced** for each alternative.
- **Net-benefit and risk-adjusted-return** features per alternative/mix per time step.
- **Scenario indices** (e.g., budget level, demand level, technology maturity) for the scenario engine.

### 4.4 Data Usage Strategy
- **Calibration set vs. validation set**: physical/environment parameters will be calibrated on
  one subset of history and checked on held-out observations (e.g., known breakups).
- **Surrogate/synthetic data**: where public data are sparse, distributions will be synthesized
  from literature ranges; these will be labeled and stressed in sensitivity analysis.
- **Staged-data integration**: the pipeline will be designed so that if data files are later
  placed in `data/`, they drop into the ingest step without changing downstream modules.

---

## 5. Candidate Model Framework

The framework will be a **layered, modular chain** so that alternatives, combinations, and
scenarios can be swapped without rebuilding the whole model:

```
[Environment Dynamics] -> [Risk Engine] -> [Performance/Cost Engine] -> [Benefit/Revenue Engine]
        -> [Portfolio/Decision Optimizer] -> [Scenario & Sensitivity Manager] -> [Reporting]
```

### 5.1 Environment Dynamics (S1) — Candidate Models
- **M1a. Deterministic continuum source–sink model.** Coupled ODE/PDE over
  (altitude bin × size class) with source terms (launches, fragmentations) and sink terms
  (decay, removal) plus a collision-coupling term. *Advantages:* tractable, transparent,
  suited to scenario sweeps. *Limitations:* ignores object-level stochasticity, smears collisions.
- **M1b. Individual-object Monte Carlo.** Each tracked object simulated with orbital
  propagation and probabilistic conjunctions. *Advantages:* realistic granularity, natural
  stochastic risk output. *Limitations:* computationally heavy, needs large catalogs.
- **M1c. Hybrid.** Coarse continuum for the bulk population plus explicit high-stakes objects.
  *Advantages:* balance of fidelity and cost. *Limitations:* interface/consistency complexity.

### 5.2 Collision-Risk Engine (S2) — Candidate Models
- **M2a. Kinetic-theory flux + Poisson model** for expected collisions per time step.
- **M2b. Conjunction-based probabilistic risk assessment (PRA)** with fault/event trees for
  asset-loss consequences.
- **M2c. Stochastic process model** (Poisson / renewal) for event counts, feeding uncertainty
  into the decision layer.

### 5.3 Alternative & Performance Characterization (S3)
Alternatives to be modeled as **technology profiles** with parameters such as reachable
altitude/inclination, removable-object size range, removal rate, success probability, mission
cadence, and technology-readiness risk:
- **ALT-1** Small water-jet / ion-beam / drag-augmentation nudgers for small debris.
- **ALT-2** High-energy laser systems (ground- or space-based) for targeted small objects.
- **ALT-3** Dedicated ADR spacecraft (capture mechanisms) for large debris.
- **ALT-4** Large "sweeper" satellite concepts for bulk removal.
- **ALT-5** Avoidance/mitigation technologies (tracking, maneuver support, avoidance-as-a-service).
- **Combinations** formed as portfolios, e.g., (ALT-1 + ALT-3), (ALT-2 + ALT-5), staged mixes.

### 5.4 Cost Engine (S4)
- Cost build-up model: R&D + manufacturing + launch + operations + disposal, as functions of
  scale, time, and learning (learning-curve/experience effects).
- **Discounting**: NPV/IRR variants with configurable discount rate; optional real-options
  treatment of staged investment.

### 5.5 Benefit / Revenue Engine (S5)
- Monetized channels: service contracts, insurance-premium reduction, data/SSA products,
  salvage/servicing, regulatory credits.
- Non-monetized benefits: risk reduction, scientific/strategic value — carried into a
  **multi-criteria** layer rather than forced monetization.

### 5.6 Risk & Uncertainty Engine (S6)
- Technical risk (mission failure), financial risk (cost overrun, demand shortfall),
  regulatory/liability risk, and environment risk (cascade / Kessler-type tipping).
- Sources of uncertainty propagated via Monte Carlo and global sensitivity methods.

### 5.7 Decision / Portfolio Model (S7) — Candidate Methods
- **M7a. Optimization:** integer/knapsack or MILP to select alternatives/mix under budget constraints.
- **M7b. Multi-objective optimization** (e.g., evolutionary many-objective) over
  cost–risk–benefit tri-objective, producing a trade-off frontier.
- **M7c. Multi-criteria decision analysis (AHP/TOPSIS)** to fold quantitative + qualitative factors.
- **M7d. Real options / decision trees** for staged, sequential deployment decisions.
- **M7e. System-dynamics / feedback model** capturing debris→collision→debris loops and
  the public-good/free-rider interaction.

### 5.8 Scenario Engine (S8)
Parameterized drivers: budget levels, discount rate, launch-cost trajectories, technology
maturity, demand for removal, regulation stringency, solar activity, and catastrophic-event
shocks — combined via structured scenarios and Monte Carlo "what if?" sampling.

---

## 6. Implementation Roadmap

### 6.1 Modules to be Built
1. **`ingest`** — data acquisition/cleaning/binning and assumption-register loader.
2. **`environment`** — M1a/M1b/M1c dynamics simulator with time stepping.
3. **`risk`** — M2a/M2b/M2c risk engine consuming environment state.
4. **`costbenefit`** — cost build-up and benefit/revenue engine.
5. **`portfolio`** — optimizer + MCDA layer over alternatives and combinations.
6. **`scenario`** — scenario definitions, Monte Carlo driver, sensitivity sampler.
7. **`report`** — output tables/figures generation (**only at execution stage, not now**).
8. **`validate`** — benchmark and consistency-check harness.

### 6.2 Planned Workflow
1. Fix horizon, time step, and units; load assumptions and scenario parameter sets.
2. Build baseline environment trajectory (no intervention) as the counterfactual reference.
3. For each alternative and combination, simulate the perturbed environment.
4. Feed environment states into the risk engine to obtain time-dependent risk trajectories.
5. Compute time-indexed cost and benefit/revenue streams; discount and aggregate to metrics.
6. Run the decision/portfolio layer to rank alternatives and select optimal mix(es).
7. Sweep scenarios ("what if?") and run global sensitivity to test ranking stability.
8. Apply the interpretation logic (§8) to output a recommendation or a fallback avoidance strategy.

### 6.3 Algorithms (planned, implementation-stage)
- Numerical integrators for ODE/PDE environment models; Monte Carlo ensemble propagation.
- Poisson/point-process estimators for collision events.
- MILP / knapsack and evolutionary multi-objective optimizers for portfolio selection.
- Sobol/Morris global sensitivity and scenario matrix sampling.
- AHP/TOPSIS scoring for non-monetized factors.

### 6.4 Engineering Practices (planned)
- Deterministic, seed-controlled stochastic runs for reproducibility.
- Configuration-driven runs so scenarios are data, not code edits.
- Unit tests for each module; golden-reference checks for limiting cases.
- Versioned assumption register and provenance log.

---

## 7. Validation Strategy

### 7.1 Evaluation Metrics (planned)
- **Physical:** conservation of object counts/mass, agreement of decay statistics with known
  relations, plausible collision-rate magnitudes vs. literature.
- **Economic:** NPV/IRR distributions, probability of positive net benefit, payback period,
  break-even thresholds in key parameters.
- **Decision quality:** rank stability of alternatives across scenarios; regret vs. best
  ex-post alternative; robustness of the recommended mix.
- **Risk calibration:** coverage of prediction intervals; consistency of modeled event rates
  with historical frequency.

### 7.2 Validation Methods (planned)
- **Internal consistency:** dimensional checks, boundary/limiting cases (zero debris, zero
  removal, single-alternative extremes), conservation audits.
- **Cross-model validation:** compare M1a (continuum) against M1b (Monte Carlo) on matched
  scenarios; reconcile discrepancies.
- **External benchmarking:** compare environment projections and collision rates to published
  debris-environment models/historical breakups (where public data permit).
- **Economic benchmarking:** compare cost estimates to comparable real-world removal/servicing
  program budgets and insurance-market data.
- **Backtesting:** initialize the model at a historical epoch and check it reproduces observed
  subsequent environment statistics.

### 7.3 Sensitivity Analysis (planned)
- **Local:** one-at-a-time (OAT) sweeps over each key parameter to identify dominant drivers.
- **Global:** variance-based (Sobol) and screening (Morris) methods to rank parameter influence
  and interactions.
- **Scenario/stress tests:** extreme but plausible "what if?" cases (budget cuts, technology
  failure, demand collapse, regulatory change, cascade shock).
- **Uncertainty propagation:** Monte Carlo over parameter priors to produce output distributions
  rather than point estimates.

---

## 8. Expected Result Interpretation

This section describes **how outputs will be read** once the model is executed (no results are
produced in this draft).

- **Viability test.** The primary output will be the distribution of the economic-attractiveness
  metric per alternative/mix. The firm will be judged to have a viable opportunity if a
  robustly positive, risk-adjusted outcome persists across plausible scenarios; otherwise the
  fallback branch is triggered.
- **Comparison.** Alternatives and combinations will be compared on a trade-off frontier of
  cost vs. risk-reduction vs. benefit, with qualitative factors overlaid via MCDA weights.
- **Recommendation logic.** A recommendation will name a primary strategy (or staged mix),
  the conditions under which it dominates, and the key thresholds that would change the answer.
- **What-if narrative.** Scenario outputs will be reported as conditional statements
  (e.g., "if budget is low and discount rate high, then ranking X changes to Y"), never as a
  single unconditional verdict.
- **Fallback branch.** If no opportunity is viable, the output will shift to a ranked set of
  collision-avoidance options with their cost/benefit and risk profiles.
- **Uncertainty framing.** All headline numbers will be presented as ranges/distributions with
  explicit caveats about parameter and structural uncertainty.

---

## 9. Limitations and Improvements

### 9.1 Anticipated Limitations
- **Data scarcity:** little or no staged data; reliance on public/synthetic/expert inputs limits
  external validity.
- **Public-good economics:** debris removal benefits accrue broadly; any single-firm model must
  rely on assumed revenue mechanisms, which may not materialize.
- **Model granularity trade-off:** coarse models may misrepresent cascading dynamics; fine
  models are computationally expensive and need data that may be unavailable.
- **Deep uncertainty:** solar activity, future launch traffic, geopolitics, and technology
  breakthroughs are hard to bound.
- **Discounting sensitivity:** multi-decade benefits are extremely sensitive to the discount rate.
- **Non-monetized factors:** compressing qualitative values into scores introduces subjectivity.
- **Legal/liability simplification:** real liability frameworks are complex and evolving.

### 9.2 Planned Improvements (future iterations)
- Expand to **multi-actor / game-theoretic** settings to model coordination and free-riding.
- Add **real-options staging** to value deferral and pilot programs.
- Incorporate **adaptive/learning** behavior and technology-cost learning curves.
- Add **higher-fidelity conjunction and propagation models** as data/compute permit.
- Introduce **robust and distributionally-robust optimization** to hedge deep uncertainty.
- Build a **validation dataset** by initializing at historical epochs and backtesting.
- Extend the scenario engine to **participatory/expert-elicited** scenarios for policy relevance.

---

### Verification Checklist (self-audit of this draft)
- [x] `draft.md` created at `results/draft.md`.
- [x] Contains only planning content (workflow, assumptions, candidate methods, data plan,
      implementation plan, validation strategy).
- [x] No data analysis, no calculations, no fitted models, no code execution, no plots,
      no final results or conclusions.
- [x] Uses future-oriented language throughout.

*This blueprint will be refined into an executable modeling specification in the next stage.*
