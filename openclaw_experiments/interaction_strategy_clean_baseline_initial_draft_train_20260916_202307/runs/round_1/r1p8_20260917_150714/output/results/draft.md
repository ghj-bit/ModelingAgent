# Modeling Blueprint Draft
## IT Security Risk Assessment for a New University Campus — "To Be Secure or Not to Be?" (ICM 2004, Problem 2004_To_Be_Secure)

> **Status:** Initial modeling plan draft. This document is a *roadmap for future modeling only*. It contains no computed results, no completed analysis, no executed experiments, and no final conclusions. All quantities referenced below are reproduced from the provided problem statement as *given inputs*; none have been derived, fitted, or evaluated here.

---

## 1. Problem Background and Restatement

A new university campus is being planned and must be protected against IT security threats (hackers, viruses, and related incidents). Protection is envisioned as a *layered defense* that blends:

- **Management and usage policies** — password requirements, formal security audits, usage tracking, wireless-device rules, removable-media controls, personal-use limits, user training.
- **Technological solutions** — Intrusion Detection Systems (IDS), firewalls, anti-virus, vulnerability scanners, redundancy.

The security outcome is expressed through three classic risk categories: **Confidentiality**, **Integrity**, and **Availability** (the "CIA" triad). Failure of these categories produces **opportunity costs** — litigation, loss of proprietary data, loss of consumer confidence, loss of direct revenue, and data/service reconstruction.

The provided statement supplies a table of current opportunity-cost magnitudes and their percentage contribution to each risk category (litigation $3,800,000; proprietary data loss $1,500,000; consumer confidence $2,900,000; data reconstruction $400,000; service reconstruction $80,000; direct revenue loss $250,000), together with campus specifications (10 academic departments; athletics; admissions, bookstore, registrar, dormitories; 600 staff/faculty; 21 labs × 30 computers; 600 staff/faculty computers; 15,000 dormitory network connections; online bookstore and registrar services). Detailed cost/effectiveness data for defensive measures are referenced as **Enclosures A and B** of the original problem.

The problem poses six deliverables: (1) an optimization model for the optimal mix of preventive measures; (2) a *flexible* model adaptable to evolving technology and other organizations; (3) a position paper for the university President; (4) a comparison against a commercial search-engine company; (5) guidance on honeynet deployment; (6) a future-of-IT-security memo for Rite-On Consulting.

**This draft concerns the modeling blueprint for the above, not its solution.**

---

## 2. Objectives and Subproblems

### 2.1 Overarching objective
To design a *transferable modeling framework* that, when later instantiated and solved, would select a portfolio of preventive defensive measures minimizing total cost — where total cost combines (a) direct acquisition/maintenance/training costs and (b) expected residual opportunity costs — subject to a required level of CIA protection and to budget, staffing, and operational constraints.

### 2.2 Subproblem decomposition

| # | Subproblem | Modeling intent (to be realized later) |
|---|-----------|----------------------------------------|
| SP1 | Risk quantification | Map opportunity-cost items onto the three risk categories to obtain an aggregate exposure baseline per category. |
| SP2 | Defense characterization | Represent each candidate measure by cost (procurement, maintenance, training), category-specific effectiveness, coverage scope, and dependencies. |
| SP3 | Resource allocation / optimization | Choose an optimal mix of measures under budget and coverage constraints. |
| SP4 | Flexibility & generalization | Parameterize the model so it can be re-instantiated for new technologies and different organizations. |
| SP5 | Organization comparison | Compare risk-category weighting/structure for a university vs. a commercial search-engine company. |
| SP6 | Honeynet advisement | Frame honeynets as an information-gathering (detection/intelligence) layer with its own cost-benefit and ethical/legal considerations. |
| SP7 | Foresight | Describe how a parameterized model can be updated to anticipate future security risks. |

### 2.3 Deliverables (planned artifacts)
- A formal optimization model specification (objective, decision variables, constraints).
- A parameterization/adaptation scheme for generalization.
- Interpretation guidance and a decision-support narrative (position paper, memo).
- Validation and sensitivity-analysis plan.

---

## 3. Assumptions

The following assumptions are *proposed* for later scrutiny; each is paired with justification and a planned validation approach.

### 3.1 Structural assumptions
1. **Contribution additivity of opportunity costs.** The percentage contributions of each cost item to the CIA categories can be aggregated to form category-level exposure weights. *Justification:* the provided table already supplies such percentages. *Future validation:* stress-test with alternative weighting schemes (e.g., non-linear, min/max, or scenario-based) and compare resulting decisions.
2. **Layered independence (initial).** As a first approximation, measures contribute additively/multiplicatively to category protection, with an explicit plan to relax additivity toward overlapping or diminishing-returns structures (see §5).
3. **Measure effectiveness is expressible per risk category.** Each defensive measure can be scored on its ability to reduce Confidentiality / Integrity / Availability failures. *Validation:* reconcile against Enclosures A and B during data ingestion; where only qualitative data exist, plan an elicitation/encoding scheme.
4. **Costs are decomposable** into procurement (one-time), maintenance (recurring), and training (recurring/one-time), and can be normalized to a common time horizon.
5. **Threat and effectiveness parameters are stable within a planning window**, with explicit revision points (this is the hook for SP4/SP7).

### 3.2 Behavioral / environmental assumptions
6. **Residual risk remains nonzero** for any finite, feasible portfolio (no perfect security) — motivating a residual-cost term rather than a hard zero-risk constraint.
7. **Compliance/regulatory exposure** is captured implicitly through litigation and confidence costs rather than a separate hard constraint.
8. **Campus user population and asset counts** are as stated and treated as the coverage basis for scaling measures.

### 3.3 Assumptions-explicitly-out-of-scope (for the draft)
9. Zero-day dynamics, insider-threat human factors, and adversarial game-theoretic adaptation are *acknowledged as extensions*, not baseline assumptions.

*Justification summary:* these assumptions render the problem tractable as a constrained optimization while preserving hooks to relax them later. *Future validation:* see §7 (sensitivity and assumption-perturbation testing).

---

## 4. Data Processing Plan

### 4.1 Data inventory (anticipated)
- **Provided in-statement data:** opportunity-cost magnitudes and their CIA percentage contributions; campus/system specifications (counts of departments, staff, labs, computers, network connections).
- **Referenced enclosures (Enclosures A & B):** cost and effectiveness data sheets for defensive measures. *Availability to be confirmed and ingested if present in the data folder; otherwise plan a documented synthetic/elicitation fallback.*
- **Supplementary (optional, to be sourced later):** public benchmarks for security-incident frequency and cost where enclosure data are incomplete.

### 4.2 Preprocessing plan (steps, not execution)
1. **Catalog and normalize** all tables into a single schema: measure ID, measure class (policy vs. technology), cost components, coverage scope, effectiveness vector over CIA.
2. **Unit and horizon normalization:** convert procurement/maintenance/training costs to a common annualized basis (e.g., amortize procurement over an assumed lifetime, add recurring items).
3. **Missing-data handling:** define an explicit protocol (documented imputation rules or qualitative-to-quantitative encoding) and flag affected parameters for sensitivity testing.
4. **Consistency checks:** verify that percentage contributions per cost item sum to 100%; log any discrepancies for review.
5. **Provenance tagging:** mark each value as *given*, *derived-by-rule*, or *assumed*, so validation can distinguish evidence strength.

### 4.3 Feature construction (planned)
- **Category exposure baseline:** aggregate opportunity costs into a Confidentiality / Integrity / Availability exposure vector using the given contributions (rule to be specified, not computed here).
- **Measure effectiveness profile:** per-measure vector describing coverage across categories and asset scopes (labs, staff/faculty machines, dormitory connections, online services).
- **Cost profile:** per-measure annualized cost total and its split.
- **Dependency/coverage indicators:** binary or graded flags for prerequisite relationships and asset-scope overlaps.

### 4.4 Data usage strategy
- **Primary use:** instantiate the optimization model (SP1–SP3).
- **Secondary use:** derive comparison weighting for the search-engine scenario (SP5) and define update parameters (SP4/SP7).
- **Held-back use:** reserve a subset of measures or parameters for out-of-sample consistency checking in validation.

---

## 5. Candidate Model Framework

### 5.1 Core formulation (candidate: budget-constrained allocation / knapsack-style optimization)
- **Decision variables:** selection and (optionally) intensity levels of each defensive measure; coverage assignments to asset classes.
- **Objective (to be minimized):** total annualized cost = sum of measure costs + expected residual opportunity cost given the chosen protective coverage.
- **Constraints:** budget caps (by category and total), mandatory-coverage floors, logical/dependency constraints (a measure may require another), and capacity constraints (staff, training throughput).
- **Rationale:** natural fit for "optimal mix" with explicit trade-offs between spend and residual risk.

### 5.2 Alternative / complementary candidate models
1. **Multi-objective optimization (Pareto front).** Treat cost, confidentiality, integrity, availability as separate objectives to expose trade-offs rather than collapsing them into a single scalar.
2. **Multi-attribute utility / weighted-sum decision analysis.** Useful for the position-paper narrative and for encoding stakeholder risk appetite.
3. **Layered-defense reliability model (series/parallel).** Represent measures as layers whose combined "failure probability" reduces incident likelihood; useful for handling overlap and diminishing returns.
4. **Probabilistic risk model (frequency × impact).** Model incident likelihood per threat class and multiply by CIA-weighted impact; supports expected-cost objective.
5. **Scenario / robust optimization.** Account for uncertainty in effectiveness and threats by optimizing over worst-case or scenario sets — a natural bridge to flexibility (SP4) and foresight (SP7).
6. **System-dynamics or Markov-style evolution model (exploratory).** For anticipatory discussion of how threat landscapes and defenses co-evolve (SP7).

### 5.3 Mathematical ideas to be considered (no results derived here)
- Linear / mixed-integer programming for selection variables.
- Separable convex or concave coverage-response functions to encode diminishing returns.
- Robust/minimax and chance-constrained variants for uncertainty.
- Sensitivity via parametric programming and elasticities.
- Game-theoretic layer (optional extension) for adversarial/threat adaptation.

### 5.4 Advantages and limitations (anticipatory)
- **LP/MIP allocation:** *Advantage* — transparent, solvable, interpretable. *Limitation* — relies on linearity and additive independence assumptions.
- **Multi-objective:** *Advantage* — avoids arbitrary weighting. *Limitation* — more complex reporting and decision mapping.
- **Probabilistic risk:** *Advantage* — conceptually faithful to risk. *Limitation* — parameter-hungry; may outrun available data.
- **Robust/scenario:** *Advantage* — resilience to uncertainty. *Limitation* — can yield conservative, costlier solutions.

---

## 6. Implementation Roadmap

### 6.1 Planned workflow
1. **Specification freeze:** lock objectives, variables, constraints, and the effectiveness/coverage semantics.
2. **Data ingestion layer:** schema, normalization, provenance tagging, and fallback encoding rules.
3. **Model assembly:** implement the core allocation model first; then add multi-objective and robust layers as modules.
4. **Instance construction:** build the university instance from given specs and enclosure data.
5. **Scenario builder:** parameterize for the commercial search-engine instance (SP5) and for update cycles (SP4/SP7).
6. **Reporting layer:** generate decision-support outputs (portfolio recommendation, trade-off views, narrative inputs for the position paper and memo).
7. **Validation harness:** run the plan in §7.

### 6.2 Required modules (planned)
- `data/` — raw enclosure data and normalization rules.
- `model/` — objective, constraints, coverage/effectiveness functions.
- `solvers/` — optimization drivers (core + multi-objective + robust variants).
- `scenarios/` — university vs. search-engine parameter sets.
- `analysis/` — sensitivity, trade-off, and assumption-perturbation routines.
- `report/` — structured outputs feeding the four narrative deliverables.

### 6.3 Tooling considerations (to be chosen later)
- MILP/convex solvers for the allocation core.
- Multi-objective tooling for Pareto exploration.
- Reproducibility controls: fixed seeds, versioned parameter files, and documented provenance.

### 6.4 Mapping to the six stated tasks
| Task | Roadmap hook |
|------|--------------|
| Task 1 (model development) | §5.1 core optimization + §6.1 steps 1–4 |
| Task 2 (flexible model / example update) | §5.2 robust/scenario + §6.2 `scenarios/` + update protocol |
| Task 3 (position paper) | §6.1 step 6 + §8 interpretation guidance |
| Task 4 (search-engine comparison) | §6.2 `scenarios/` + comparative risk-weighting module |
| Task 5 (honeynets) | Separate intelligence-layer cost-benefit module (detection value vs. cost/legal risk) |
| Task 6 (future memo) | §5.2 systems/evolutionary view + §5.3 game-theoretic extension |

---

## 7. Validation Strategy

### 7.1 Evaluation metrics (planned)
- **Decision-quality metrics:** total cost of chosen portfolio; residual risk by category; coverage completeness.
- **Robustness metrics:** decision stability across scenarios and parameter perturbations; regret vs. best-case.
- **Interpretability metrics:** transparency of selected measures and their marginal value.

### 7.2 Validation methods
1. **Internal consistency:** constraint satisfaction checks, percentage-sum checks, unit/horizon reconciliation.
2. **Face validity:** expert review of selected portfolios against known security practice.
3. **Back-testing against stated exposure:** compare modeled residual risk against the given cost magnitudes (as an input-based sanity check, not a fitted result).
4. **Assumption-perturbation testing:** re-run under relaxed additivity, alternative weightings, and missing-data encodings.
5. **Cross-instance plausibility:** verify the model behaves sensibly when re-parameterized for the search-engine scenario.

### 7.3 Sensitivity analysis plan
- **One-at-a-time** sweeps of effectiveness and cost parameters.
- **Global/structural** sweeps of the additivity and independence assumptions.
- **Weighting sensitivity** in any multi-attribute aggregation.
- **Break-even / tipping-point** exploration for budget and coverage floors.

*(All of the above are planned procedures; none have been executed in this draft.)*

---

## 8. Expected Result Interpretation

This section describes how results *would later be read*, not what they are.

- **Portfolio recommendation:** the optimized measure mix should be read as a **decision aid** under stated assumptions, not a guarantee of security.
- **Trade-off curves:** Pareto/robust views are expected to show the marginal cost of additional protection in each CIA category, informing budget discussions.
- **Category attribution:** expected to indicate which risk categories dominate cost, guiding where defenses matter most.
- **Flexibility claims:** the *value* of the flexible model is expected to lie in its re-parameterization speed and transparency, enabling updates as technology and threats change.
- **Cross-organization comparison:** differences are expected to stem primarily from differing risk-category weights (e.g., availability and confidentiality priorities likely diverge between a university and a commercial search engine).
- **Honeynet guidance:** expected to be framed as trade-offs between intelligence value and cost/legal/ethical exposure, not a binary endorsement.

**What can be inferred:** relative priorities, marginal trade-offs, and sensitivity of decisions to key parameters.
**What cannot be inferred:** absolute guarantee of security, precise future incident forecasts, or adversarial behavior beyond modeled assumptions.

---

## 9. Limitations and Improvements

### 9.1 Anticipated limitations
- Reliance on enclosure/assumed effectiveness data that may be incomplete or coarse.
- Additivity and independence simplifications that may misrepresent overlapping defenses.
- Static parameterization that may understate co-evolution of threats and defenses.
- Human/organizational factors (training adherence, insider behavior) only partially represented.
- Ethical/legal dimensions of honeynets not fully captured in a pure cost model.

### 9.2 Planned improvements
- Replace additive coverage with layer/stackelberg-style or probabilistic penetration structures.
- Introduce robust/chance-constrained formulations to absorb uncertainty.
- Add explicit update triggers and a documented re-parameterization protocol for technological change.
- Extend to a scenario library (university, search engine, and beyond) to strengthen generalization claims.
- Incorporate human-factor modules and honeynet intelligence valuation as optional extensions.

---

*End of initial modeling blueprint draft. No problem solving, data analysis, computation, model fitting, or experimentation has been performed. All figures cited are reproduced from the given problem statement for planning reference only.*
