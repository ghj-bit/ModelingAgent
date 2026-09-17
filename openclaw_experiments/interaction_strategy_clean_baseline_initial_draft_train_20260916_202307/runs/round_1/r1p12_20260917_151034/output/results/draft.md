# Modeling Blueprint Draft
## Organ Transplant: The Kidney Exchange Problem (ICM 2007, Problem C)

> **Status:** Initial modeling plan draft. This document is a *roadmap for future modeling work*, not a completed solution. It contains no computed results, no fitted models, no executed experiments, and no final conclusions. All statements are prospective ("will", "should", "is expected to").

---

## 1. Problem Background and Restatement

The core issue is a structural mismatch between the demand for kidney transplants and the available supply. The US Organ Procurement and Transplantation Network (OPTN) coordinates allocation, yet waiting lists remain long (nearly 94,000 candidates, expected to exceed 100,000) and matching remains inefficient. Roughly 68,000 patients are waiting for kidneys, with approximately 10,000 annual transplants from cadaveric donors and 6,000 from living donors.

This planning draft will treat the kidney exchange system as a **resource-allocation and matching problem embedded in a policy and ethical environment**. The problem will be decomposed into a modeling hierarchy:

- A **system-level network model** describing flow, capacity, and bottlenecks (Task 1).
- A **comparative policy layer** contrasting US practice with another national system, reporting to Congress (Task 2).
- An **optimization layer** for maximizing the number and quality of kidney exchanges, including paired and chain donation (Task 3).
- A **decision-theoretic layer** for individual patient acceptance and exchange-participation decisions (Task 4).
- A **policy/ethics layer** translating model outputs into actionable criteria and recommendations (Task 5).
- A **donor-behavior layer** modeling donor risk perception, incentives, and recruitment (Task 6).

### Restatement of Tasks (as planning targets)

- **Task 1 (System Model):** Will develop a mathematical representation of the US transplant network to locate bottlenecks, evaluate resource re-allocation, assess state-level fragmentation, and test policy levers.
- **Task 2 (Policy Comparison):** Will contrast US allocation policy with a comparison country's system and produce a one-page congressional brief grounded in Task 1 outputs.
- **Task 3 (Exchange Maximization):** Will formulate a procedure to maximize the count and quality of kidney exchanges under medical and psychological constraints, and will estimate downstream effects on transplant volume and waiting lists.
- **Task 4 (Patient Strategy):** Will define a decision framework for a patient choosing between accepting an offer and entering an exchange, weighing risks, alternatives, cadaveric vs. living-donor trade-offs.
- **Task 5 (Policy Recommendations):** Will recommend revisions to allocation criteria and policies, including ethical analysis and a discussion of organ sales.
- **Task 6 (Donor Perspective):** Will analyze donor-side risk and decision factors, including recipient success probability, donor survival/health risk, social network effects, and altruistic donor recruitment.

---

## 2. Objectives and Subproblems

The overarching objective will be to build an **integrated modeling framework** that links organ flow, matching optimization, individual decision-making, and policy evaluation. Specific planning objectives:

1. **Characterize the system** — Define state variables and flows (candidates, donors, transplants, deaths/dropouts) so that bottlenecks can be expressed quantitatively.
2. **Identify bottlenecks** — Plan to locate constraints in supply, matching compatibility, geography, and allocation rules.
3. **Quantify exchange gains** — Prepare to estimate additional transplants achievable through optimized exchange (paired exchange, chains, altruistic donors).
4. **Support individual decisions** — Design a decision model for accept-vs-wait and exchange participation.
5. **Evaluate policy levers** — Plan scenario experiments on allocation criteria, regionalization, and consent/compensation policies.
6. **Address ethics and feasibility** — Incorporate fairness, equity by age, and the organ-sale debate into the evaluation layer.

### Subproblem Map (planned decomposition)

| Subproblem | Planning Question | Links To |
|---|---|---|
| S1 Flow/queue dynamics | How do waiting lists evolve under current rates? | Tasks 1, 3 |
| S2 Network & geography | Where do geographic and capacity bottlenecks arise? | Task 1 |
| S3 Exchange optimization | What exchange structures maximize volume/quality? | Task 3 |
| S4 Patient decision | When should a patient accept vs. wait/exchange? | Task 4 |
| S5 Policy scenarios | Which policy changes improve key metrics? | Tasks 1, 2, 5 |
| S6 Donor behavior | What drives donor participation and risks? | Task 6 |
| S7 Ethics/fairness | Are allocations defensible and equitable? | Tasks 5, 6 |

---

## 3. Assumptions

All assumptions below are **working hypotheses** to be revisited during modeling. Each is paired with a planned validation approach.

### 3.1 Structural / Population Assumptions
- **A1 — Aggregated population dynamics:** The candidate pool will be modeled at an aggregate (cohort) level rather than as fully individual agents, to keep the system tractable. *Validation:* Compare aggregate trajectories against any provided age-distribution data (under 18, 18–34, 35–49, 50–64, 65+).
- **A2 — Age-cohort stratification:** Waiting patients will be stratified by the provided age bands, since transplant suitability and priority will likely depend on age. *Validation:* Check sensitivity of results to alternative band definitions.
- **A3 — Steady vs. dynamic rates:** We will first assume constant annual arrival/transplant rates for a baseline, then relax to time-varying rates. *Validation:* Back-test against any historical trend information available.

### 3.2 Clinical / Compatibility Assumptions
- **A4 — Defined compatibility rule set:** Blood-type and HLA compatibility will be represented as binary/ordinal compatibility constraints. *Validation:* Sanity-check compatibility matrices against documented medical criteria.
- **A5 — Survival/outcome probabilities:** Patient and graft survival will be modeled as age- and donor-type-dependent probability functions (parameters to be sourced or assumed). *Validation:* One-way sensitivity analysis on survival parameters.
- **A6 — Cadaveric vs. living distinction:** These two sources will be modeled as distinct supply channels with different quality and timing characteristics. *Validation:* Compare modeled quality differentials to reported differences.

### 3.3 Behavioral / Institutional Assumptions
- **A7 — Rational patient behavior:** Patients will be assumed to make utility-maximizing accept/wait decisions under uncertainty, with a tunable risk-aversion parameter. *Validation:* Stress-test under alternative behavioral rules (e.g., risk-seeking, myopic).
- **A8 — Donor participation model:** Donor entry will be modeled as a function of altruism, perceived risk, and network effects. *Validation:* Compare qualitative predictions to qualitative case discussions.
- **A9 — Policy levers are independent:** Policy scenarios will initially be varied one at a time before combined analysis. *Validation:* Interaction checks in multi-lever scenarios.

### 3.4 Scope Assumptions
- **A10 — Single-organ focus:** Only kidneys will be modeled (other organs out of scope), though the framework could later be generalized.
- **A11 — No explicit financial market:** Organ sales will be treated as a *policy scenario*, not as an assumed baseline, given legal and ethical constraints.

---

## 4. Data Processing Plan

The supplied data are limited and descriptive; a substantial part of the plan will be to **define required inputs and their provenance**.

### 4.1 Provided Inputs to Be Used
- Waiting list magnitude: ~94,000 candidates, expected to exceed 100,000.
- Kidney transplant volumes: ~68,000 waiting; ~10,000 cadaveric and ~6,000 living-donor transplants annually.
- Age distribution of waiting patients: Under 18 = 748; 18–34 = 8,033; 35–49 = 20,553; 50–64 = 28,530; 65+ = 10,628.

### 4.2 Planned Preprocessing Steps
1. **Tabulation and normalization:** Convert the given counts into cohort proportions and verify internal consistency (sum vs. reported total).
2. **Unit harmonization:** Standardize all rates to a common time base (e.g., per-year) and all stock quantities to a common reference date.
3. **Missing-parameter register:** Maintain an explicit register of parameters not provided (compatibility rates, survival curves, donor supply rates, geographic distributions) with planned sourcing or assumption tags.
4. **Category alignment:** Map provided age bands to any modeling strata so that aggregation/disaggregation is reversible.

### 4.3 Feature / Variable Construction (planned)
- **Stock variables:** candidates by age band, active vs. inactive waiters, donor pools.
- **Flow variables:** annual additions, transplants (cadaveric/living), removals (death, dropout, recovery).
- **Derived indicators:** transplant rate per candidate, wait-time proxies, compatibility-scarcity ratio.
- **Quality attributes:** donor-type indicators, expected graft-survival proxies.

### 4.4 Data Usage Strategy
- The provided figures will be used **only** to calibrate baseline stocks/flows and to define cohort structure; they will **not** be treated as outputs to reproduce.
- Where data are insufficient, the plan will use **parameterized assumptions** with explicit ranges, feeding directly into the sensitivity analysis in Section 7.

---

## 5. Candidate Model Framework

Multiple candidate models will be evaluated and, where useful, combined into a layered framework.

### 5.1 System Flow Layer (Task 1)
- **Candidate models:** Compartmental / queueing model (fluid-flow approximation of the waiting list); discrete-time stock-flow simulation; Markov chain cohort progression.
- **Key variables:** candidate stock by cohort, arrival rate, transplant rate, removal rate, service capacity.
- **Mathematical ideas:** conservation/flow equations (inflow − outflow = change in stock), Little's Law as a diagnostic for wait time, bottleneck identification via saturation analysis.
- **Advantages:** transparent, low data demand, good for bottleneck reasoning.
- **Limitations:** aggregate models hide individual matching detail; constant-rate assumptions may not hold.

### 5.2 Network / Geographic Layer (Task 1, 2)
- **Candidate models:** graph/network flow model with nodes (regions/states) and edges (allocation pathways); capacity-constrained flow optimization.
- **Key variables:** region-level supply/demand, cross-region exchange flows, capacity limits.
- **Mathematical ideas:** max-flow / min-cut to expose structural bottlenecks; regionalization scenarios (single national pool vs. state-level pools).
- **Advantages:** directly addresses the "divide into smaller units" question.
- **Limitations:** needs geographic supply/demand data that may not be provided.

### 5.3 Exchange Optimization Layer (Task 3)
- **Candidate models:** directed-graph matching (compatibility digraph) with cycle/path selection; integer programming for maximum-weight cycle packing; chain construction from altruistic donors.
- **Key variables:** donor–patient pairs, compatibility edges, cycle/chains, quality weights.
- **Mathematical ideas:** maximum-cardinality / maximum-weight cycle cover; prize-collecting variants to trade off quantity vs. quality.
- **Advantages:** the natural formalism for kidney exchange; supports both volume and quality objectives.
- **Limitations:** NP-hard in general; requires good compatibility/graph-generation assumptions.

### 5.4 Patient Decision Layer (Task 4)
- **Candidate models:** decision tree / Markov decision process for accept-vs-wait; expected-utility maximization; multi-criteria decision analysis.
- **Key variables:** offer quality, expected waiting time, survival probabilities, risk-aversion.
- **Mathematical ideas:** dynamic programming for optimal stopping under uncertainty; value-of-information for exchange participation.
- **Advantages:** captures individual-level trade-offs and donor-type differences.
- **Limitations:** sensitive to assumed utility and probability inputs.

### 5.5 Policy / Ethics Layer (Tasks 2, 5, 6)
- **Candidate models:** scenario-based simulation over policy levers; multi-criteria evaluation (efficiency vs. equity); qualitative ethical framework.
- **Key variables:** allocation-rule parameters, consent regime, compensation level, priority-by-age weights.
- **Mathematical ideas:** Pareto-frontier analysis of efficiency–equity trade-offs; counterfactual policy comparison.
- **Advantages:** connects model outputs to the congressional-brief deliverable.
- **Limitations:** value judgments are not fully quantifiable; results are scenario-contingent.

### 5.6 Donor-Behavior Layer (Task 6)
- **Candidate models:** probabilistic participation model; network-diffusion / influence model for altruistic donor recruitment.
- **Key variables:** perceived donor risk, recipient success probability, social-network size, incentive level.
- **Mathematical ideas:** risk-benefit utility framing; threshold/diffusion dynamics for outreach.
- **Advantages:** addresses the supply side, which is central to the bottleneck.
- **Limitations:** behavioral parameters are hard to ground without survey data.

### 5.7 Integrated Framework (planned)
A layered architecture is planned: **Flow (S1) → Network (S2) → Exchange Optimization (S3)**, with **Patient Decision (S4)** and **Donor Behavior (S6)** as behavioral modules feeding the flow layer, and **Policy/Ethics (S5, S7)** as an evaluation shell around the whole. Interfaces between layers will be defined as explicit input/output contracts (e.g., accepted exchange volume feeds back into flow rates).

---

## 6. Implementation Roadmap

> This section describes *planned* algorithm choices and module structure. No code will be written or executed as part of this draft.

### 6.1 Planned Algorithms
- **Flow/queue:** time-stepped simulation loop; numerical integration of flow equations.
- **Network flow:** standard max-flow / min-cut procedures.
- **Exchange optimization:** integer-programming solver (or heuristic — greedy/cycle-cover heuristics) for cycle packing; chain-generation routine.
- **Patient decision:** backward-induction dynamic programming over a discretized state space.
- **Policy scenarios:** parameter sweep / grid search over lever values; Pareto computation.
- **Donor behavior:** Monte Carlo sampling of participation outcomes.

### 6.2 Planned Workflow
1. Define model interfaces and parameter register (from Section 4).
2. Build the flow layer and calibrate baseline stocks/flows to provided figures.
3. Construct the compatibility digraph and exchange optimizer.
4. Add patient-decision and donor-behavior modules.
5. Wrap with the policy-scenario and evaluation shell.
6. Run planned scenario sets, then sensitivity and validation passes.

### 6.3 Required Modules
- **Module M1:** Data intake & aggregation (cohort tabulation).
- **Module M2:** Flow/queue engine.
- **Module M3:** Network/geography model.
- **Module M4:** Exchange graph & optimizer.
- **Module M5:** Patient decision engine.
- **Module M6:** Donor behavior engine.
- **Module M7:** Policy scenario manager.
- **Module M8:** Evaluation & reporting (incl. congressional brief generator).
- **Module M9:** Sensitivity & validation harness.

### 6.4 Planned Dependencies & Sequencing
- M2 will depend on M1; M4 will depend on M3; M5/M6 will feed M2; M7/M8 will sit on top of M2–M6; M9 will validate all modules. A critical-path plan will prioritize M1–M4 before M5–M9.

---

## 7. Validation Strategy

### 7.1 Evaluation Metrics (planned)
- **Volume metrics:** total transplants, number of exchanges, added transplants from optimization.
- **Wait metrics:** mean/median projected wait, list length over time.
- **Equity metrics:** distribution of access across age cohorts; disparity indices.
- **Quality metrics:** expected graft/patient survival proxies; quantity–quality trade-off frontier.
- **Policy metrics:** responsiveness of key metrics to each lever.

### 7.2 Validation Methods
- **Internal consistency:** conservation checks (inflow/outflow balance), unit and boundary checks.
- **Structural validation:** confirm that identified bottlenecks match qualitatively expected system behavior.
- **Cross-model validation:** compare aggregate flow results against network-flow and optimization layers for coherence.
- **Face validity:** review assumptions and outputs for plausibility against the problem narrative.
- **Comparative validation:** benchmark qualitative implications against the international comparison (Task 2).

### 7.3 Sensitivity and Uncertainty Analysis
- One-way sensitivity on each key parameter (arrival rates, survival probabilities, compatibility rates, donor participation, risk-aversion).
- Multi-way / scenario sensitivity to test interactions among policy levers.
- Range-based uncertainty reporting (best/worst/central cases) rather than single point estimates.
- Robustness check on structural choices (cohort definitions, aggregation level).

---

## 8. Expected Result Interpretation

This section describes **how results would be interpreted**, not what they are.

- **Bottleneck outputs** will be interpreted as ranked constraints, indicating where additional resources would most likely relieve system pressure.
- **Exchange-optimization outputs** will be interpreted as an *estimated upper bound* on achievable additional transplants under stated assumptions, with explicit dependence on compatibility and participation parameters.
- **Regionalization outputs** will be interpreted as trade-offs between local responsiveness and pooled-matching efficiency.
- **Patient-decision outputs** will be interpreted as decision rules (thresholds/conditions) rather than fixed advice.
- **Policy outputs** will be interpreted as scenario comparisons supporting a congressional brief; recommendations will be conditional on the assumed ethical weights.
- **All interpretations will be qualified** by model scope (Section 3) and uncertainty (Section 7).

---

## 9. Limitations and Improvements

### 9.1 Anticipated Limitations
- **Data scarcity:** core parameters (compatibility rates, survival curves, geography) are not supplied and will require assumptions.
- **Aggregation loss:** cohort-level modeling will obscure individual matching nuance.
- **Behavioral uncertainty:** donor and patient behavior parameters are hard to ground.
- **Computational hardness:** optimal exchange selection is NP-hard; heuristics will be approximate.
- **Value-laden policy layer:** ethical weighting is inherently contestable and not purely quantitative.
- **Static scope:** single-organ, non-financial baseline limits generality.

### 9.2 Planned Improvements / Extensions
- Incorporate more granular individual-level simulation if richer data become available.
- Extend the exchange optimizer with multi-objective (equity-aware) formulations.
- Add stochastic/time-varying arrival processes and seasonal effects.
- Interface the model with external real-world registries for calibration.
- Generalize the framework to multiple organ types and to international data.
- Develop a formal ethical decision framework to make policy weights transparent and adjustable.

---

## Appendix: Planning Checklist

- [x] Problem restated and decomposed into subproblems.
- [x] Objectives mapped to tasks and deliverables.
- [x] Assumptions listed with planned validation.
- [x] Data processing plan defined (using provided figures only as calibration targets).
- [x] Candidate models enumerated with advantages/limitations.
- [x] Implementation roadmap and module structure outlined.
- [x] Validation and sensitivity strategy specified.
- [x] Interpretation and limitations documented.
- [ ] *No computation, fitting, code, experiments, or final results performed (by design).*
