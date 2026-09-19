# Modeling Blueprint Draft — MM-Bench 2015_C (ICM Human Capital & Churn)

**Problem ID:** `2015_C`
**Type of document:** Modeling plan / blueprint draft (NOT a solution)
**Status:** Initial draft for future modeling work
**Date context:** Prepared as a first-pass roadmap; all numbers, fits, simulations, and conclusions are deliberately deferred to a later phase.

> Note on scope. This document is a **roadmap**. It describes *what will be modeled, how, with which data, and how it will be validated*. It intentionally contains **no computed results, no fitted parameters, no executed experiments, and no final conclusions**. Any quantities mentioned are either taken verbatim from the problem statement or are symbolic placeholders to be estimated later.

---

## 1. Problem Background and Restatement

### 1.1 Context

The Information Cooperative Manufacturing (ICM) organization is a structured company of roughly 370 positions arranged across seven hierarchical levels, from administrative clerks and inexperienced employees at the base through experienced employees, two supervisor tiers, two manager tiers, and a senior manager/executive tier at the top. ICM operates in a highly competitive labor market where recruiting is slow, costly, and uncertain, and where the manager believes organizational "churn" is rising — currently around 18% per year, with middle-manager turnover reportedly about twice the company average.

The company maintains only about 85% of its positions filled at any time. The HR office reports actively hiring for roughly 8–10% of positions. Marginal or poor performers are often retained to avoid short-staffing, which raises longer-run quality concerns. Compensation is deliberately compressed (CEO pay is approximately ten times the median salary of all employees, denoted σ). Advancement into higher management levels currently requires several years of experience at specific levels and position types, which constrains internal promotion pipelines.

No modeling, simulation, or quantitative analysis of HR dynamics has been done before. The HR manager wants to change this by building a network-science-based Human Capital model and, eventually, connecting it to other organizational layers (information flow, trust, influence, friendship).

### 1.2 Restatement of the problem asks

The team is asked to design (and later execute) a **framework and model** that will, in the future modeling phase:

- **T1.** Build a Human Capital network model of the ICM personnel situation from the provided data, stating all assumptions explicitly.
- **T2.** Identify and describe dynamic processes on that network — (a) churn dynamics (influence, dissatisfaction, diffusion) and (b) direct and indirect effects on productivity.
- **T3.** Analyze budget requirements for talent management over the next two years, expressed in units of σ, for both recruiting and training.
- **T4.** Assess whether ICM can sustain 80% staffing if the annual churn rate rises to 25%, and to 35%, including the costs and indirect effects of those higher rates.
- **T5.** Simulate the effects of a 30% churn scenario in junior managers and experienced supervisors under (i) no external recruiting and (ii) promotion-only (qualified internal) staffing, holding other churn at 18%, and interpret the impact on organization HR health.
- **T6.** Articulate how team science concepts and multi-layer (multiplex) network models could fulfill the HR manager's vision of connecting organizational network layers under HR leadership.
- **T7.** Deliver a report (≤21 pages including a one-page executive summary) documenting the model, its behavior, and the above considerations.

### 1.3 Deliverables expected from the eventual modeling effort

1. A documented, reproducible **Human Capital network model** plus its generation procedure.
2. A **dynamic churn / productivity simulator** layered on that network.
3. A **budget model** producing two-year recruiting and training requirements in σ units.
4. A **scenario engine** for the churn stresses (25%, 35%, and the T5 promotion/recruiting variants).
5. A **conceptual integration plan** for multilayer networks and team science.
6. A **written report** with executive summary, supported by figures and tables generated in the modeling phase.

---

## 2. Objectives and Subproblems

### 2.1 Overarching objective

To design a quantitative, network-based framework that will allow ICM to (a) represent its human capital as a structured, dynamic network, (b) simulate how churn propagates and affects productivity, and (c) evaluate staffing, promotion, recruiting, and budget policies in σ-normalized terms.

### 2.2 Subproblem decomposition

| ID | Subproblem | Question it will answer | Planned output artifact |
|----|------------|-------------------------|-------------------------|
| SP1 | **Static Human Capital network construction** | What does the organizational graph look like, and what edge semantics are defensible from the data? | Graph schema + generation rules + assumption register |
| SP2 | **Level structure & flow accounting** | How do employees move between the seven levels over time? | Compartmental / Markov flow model spec |
| SP3 | **Churn dynamics** | How does churn depend on position, tenure, connectedness, and influence from churned peers? | Churn hazard + diffusion model spec |
| SP4 | **Productivity linkage** | How do vacancies, turbulence, and training states translate into productivity (direct and indirect)? | Productivity sub-model spec |
| SP5 | **Budget in σ units** | What are the two-year recruiting and training requirements in σ? | Cost/budget model spec |
| SP6 | **Stress scenarios (25%/35%, T5 variants)** | Can 80% staffing be sustained? At what cost and with what indirect effects? | Scenario definition + decision rules (no runs yet) |
| SP7 | **Team science & multilayer integration** | How should the HR-led multilayer network vision be structured? | Conceptual architecture + roadmap |
| SP8 | **Sensitivity & uncertainty design** | Which assumptions dominate the conclusions? | Sensitivity/validation design |

### 2.3 Mapping of subproblems to the tasks

- T1 → SP1, SP2
- T2 → SP3, SP4
- T3 → SP5
- T4 → SP6 (rate stress) + SP5
- T5 → SP6 (promotion/recruiting variants) + SP2
- T6 → SP7
- T7 → all, plus reporting

---

## 3. Assumptions

Assumptions are grouped by role. Each carries a **justification** and a **future validation approach**, since these are the items most likely to drive results and therefore the most important to stress-test later.

### 3.1 Structural / data-level assumptions

| # | Assumption | Justification | Future validation approach |
|---|------------|---------------|----------------------------|
| A1 | The seven levels in `table1.csv` form the primary structural hierarchy of the organization. | Directly reflected by the provided dataset's "Level of Position" column. | Cross-check against Figure 1 organizational graph description in the problem. |
| A2 | Salary and recruitment figures reported as multiples of σ are treated as exact planning coefficients; σ itself drifts with inflation and is handled relatively. | The dataset and problem state that decisions are made in relative σ terms. | Sensitivity to inflation drift rate; re-express all outputs in σ. |
| A3 | Position counts in the dataset represent the intended establishment (target) structure, not necessarily current filled staff; actual staffing is treated as a separate, partially filled state. | Problem states ICM is usually ~85% filled. | Calibrate filled-vs-established ratio once time-series staffing data becomes available. |
| A4 | No individual-level HR microdata (tenure, evaluations, ties) is available; individual-level attributes must be synthesized from level-level aggregates. | Only `table1.csv` level aggregates are staged. | If ICM later supplies individual records, replace synthesis with empirical calibration. |
| A5 | Supervisor performance ratings exist but are currently unused by HR; they will be treated as a latent suitability signal rather than a known quantity. | Stated in the problem's item 3. | Obtain rating distributions in a later data phase. |

### 3.2 Network-construction assumptions

| # | Assumption | Justification | Future validation approach |
|---|------------|---------------|----------------------------|
| A6 | Formal reporting edges will be derived from the hierarchical level structure (level adjacency + span-of-control rules). | Figure 1 is described as an organizational graph; no explicit edge list is provided. | Compare with any staffing/org-chart detail released later. |
| A7 | Informal edges (trust, friendship, influence, information flow) will be modeled as additional layers with plausible generative rules (homophily by level/tenure, proximity, small-world/link-density parameters). | Required by T2 and T6; no informal-edge data is provided. | Calibrate layer statistics later against survey/communication logs, if collected. |
| A8 | Communication is assumed to be roughly proportional to structural proximity and to decline with hierarchical distance. | Common organizational-network regularity; enables a defensible baseline. | Empirical fit against information-flow layer once measured. |
| A9 | Churn influence propagates along informal and formal ties (a churned contact raises a member's churn hazard). | Problem item 2 states churn appears to diffuse employee-to-employee. | Test alternative diffusion kernels and compare to observed churn clustering. |

### 3.3 Dynamic-process assumptions

| # | Assumption | Justification | Future validation approach |
|---|------------|---------------|----------------------------|
| A10 | A baseline annual churn rate of ~18% applies to the whole organization, with middle-manager tiers elevated (reported ~2× average) before any scenario overrides. | Stated in the problem. | Recalibrate to internal HR time series if released. |
| A11 | Recruitment takes the median times reported per level and is stochastic around that median. | Dataset reports median time-to-recruit per level. | Fit a recruitment-time distribution in the modeling phase. |
| A12 | Vacancies reduce effective productivity with diminishing returns and additionally impose indirect costs (overload, knowledge loss, training drag). | Aligns with problem's "direct and indirect effects" ask. | Elicit overload/elasticity parameters and test sensitivity. |
| A13 | Promotion eligibility is governed by experience requirements in specific levels/position types, so internal pipelines are the binding constraint on replacement. | Stated in problem item 6. | Encode eligibility rules explicitly and test alternative strictness levels. |
| A14 | Quality composition evolves slowly and is driven by retention bias toward marginal performers; it will be modeled as an aggregate quality state, not individual traits. | Problem item 8 describes this retention bias. | Extend to individual heterogeneity if evaluation data becomes available. |
| A15 | σ is treated as the numeraire; all budget outputs are reported as multiples of σ, with a separate, optional inflation sensitivity. | Problem framing. | None needed beyond inflation-drift sensitivity. |

### 3.4 Scope assumptions

- **A16.** The model horizon of primary interest is two years, discretized at monthly or quarterly steps for dynamics and annually for budget aggregation.
- **A17.** External labor-market conditions are exogenous; recruiting success is not modeled as a function of internal policy except through budget and time.
- **A18.** Personnel departures are modeled as absences from the network, not as re-entry, unless a boomerang-hire variant is explicitly configured.

**Assumption-management plan:** all assumptions will be maintained in a single register with a stable ID, a status flag (baseline / variant / to-be-validated), and links to the subproblems they affect, so that the later sensitivity phase can trace which assumption drives which conclusion.

---

## 4. Data Processing Plan

### 4.1 Staged data inventory

| File | Role | Key fields |
|------|------|------------|
| `data/table1.csv` | Primary and currently only dataset | Level of Position; Median time to recruit (months); Median cost of recruitment; Number of Employees at this level; Average annual salary rate; Average annual training cost |

### 4.2 Raw-data handling plan (future execution)

1. **Ingestion & schema normalization.** Parse `table1.csv` into a tidy level-indexed table. Normalize the σ-denominated cells (e.g., "1.2σ", "0.5σ") into numeric coefficients with an explicit `unit = sigma` marker rather than converting to currency, preserving the problem's relative-value convention.
2. **Level ordering.** Establish a canonical ordinal hierarchy (Administrative clerk / Inexperienced employee / Experienced employee / Inexperienced supervisor / Experienced supervisor / Junior manager / Senior manager) and define the mapping between problem-named middle-manager tiers (Junior Managers, Experienced Supervisors, Inexperienced Supervisors) and dataset rows for scenario targeting.
3. **Integrity checks.** Verify internal consistency (see §4.5) without yet drawing conclusions.
4. **Derived aggregates (structure only).** Construct helper tables such as a level→adjacency matrix, span-of-control candidates, and salary/training cost lookups. These are structural scaffolding, not results.
5. **Synthesis of individual-level proxy records.** Because only level aggregates exist, generate a *pseudo-population* of individuals whose counts and salary/training attributes match the level aggregates, with placeholder tenure and suitability attributes drawn from declared priors. The synthesis procedure will be documented as an assumption (A4).
6. **Provenance & reproducibility.** Every transformation will be scripted (planned in `code/`) and logged (planned in `logs/`) so the pipeline is auditable.

### 4.3 Feature construction plan

Planned derived features (structure only, computed in the modeling phase):

- **Level features:** headcount share, salary coefficient, training coefficient, recruit time and recruit cost coefficients, middle-manager flag, eligibility depth for promotion.
- **Node features (synthetic individuals):** level, tenure bucket, seniority rank, suitability/evaluation proxy, connectedness degree, cumulative churn-exposure signal.
- **Edge/relation features:** formal reporting link, hierarchical distance, informal-tie probability, layer membership, tie strength proxy.
- **Organizational features:** total establishment, presumed filled fraction, vacancy vector, span-of-control distribution, churn-exposure clustering.

### 4.4 Data usage strategy

- `table1.csv` will supply **all level-level parameters**: per-level establishment counts, salary coefficients, training coefficients, recruit time, and recruit cost.
- Structural and dynamic models (SP1–SP4) will consume these as inputs to generate the network and processes.
- Budget models (SP5) will consume salary/training/recruit coefficients per level and combine them with flow quantities produced by the dynamic model.
- Scenario models (SP6) will override selected per-level churn parameters while holding others at the stated baseline.
- Validation (SP8) will reuse the same table for structural sanity checks and, where possible, for consistency between model-implied and stated organizational attributes.

### 4.5 Data-quality and consistency checks (planned)

- Confirm the reported level counts reconcile with the stated organization size of 370 positions (as a stated-fact check, not an analytical result).
- Confirm the σ-denominated salary column is monotone or near-monotone in level (a structural plausibility check).
- Flag any tension between the stated 85% fill rate, the stated 8–10% active-hiring rate, and the level counts; document rather than resolve at this stage.
- Enumerate missing-but-desired fields (individual tenure, evaluations, explicit ties, time-series churn) as a **data gap register** to guide later collection.

---

## 5. Candidate Model Framework

The framework is intended to be **layered and pluralistic**: a structural network layer, a dynamic flow layer, a churn/hazard layer, a productivity layer, and a budget layer, with an explicit interface between them. Candidate methods are listed with advantages and limitations so a later phase can select among them.

### 5.1 Layer A — Static Human Capital network (SP1)

**Goal:** represent ICM as a graph $G=(V,E)$ where nodes are (synthetic) individuals or aggregated level-groups, and edges encode formal and informal relations.

Candidate constructions:

1. **Hierarchical/span-of-control generator.** Build formal edges from level adjacency and plausible spans of control.
   - *Advantages:* faithful to the described org chart; interpretable.
   - *Limitations:* requires span-of-control assumptions; sensitive to how supervisors map to divisions/branches.
2. **Random-graph / configuration model with layer constraints.** Generate informal ties via a configuration or Chung–Lu model with degree targets and homophily.
   - *Advantages:* standard, analytically tractable, easy to vary density.
   - *Limitations:* not organizationally specific; needs calibration to feel realistic.
3. **Small-world / Watts–Strogatz variant** for informal communication paths.
   - *Advantages:* captures clustering + short paths typical of organizations.
   - *Limitations:* parameter choice (rewiring) is arbitrary without data.
4. **Stochastic block model** with blocks = levels.
   - *Advantages:* naturally expresses level-based mixing; supports inference later.
   - *Limitations:* needs a mixing prior; may underrepresent cross-level bridges.

Planned variables: number of nodes per level; out-degree (span) per supervisor role; intra- vs inter-level tie probabilities; layer count.

### 5.2 Layer B — Level flow / staffing dynamics (SP2)

**Goal:** track headcount and vacancies across the seven levels over time, including hiring, promotion, and exit.

Candidate methods:

1. **Compartmental (system-dynamics) flow model** — stocks (filled, vacant, in-training) and flows (hire, promote, churn, retire) governed by rate equations.
   - *Advantages:* transparent, matches budget aggregation, easy scenario overrides.
   - *Limitations:* homogeneous within compartments; ignores individual network effects unless coupled.
2. **Markov / semi-Markov chain over levels and employment states.**
   - *Advantages:* yields transition structure, expected occupation times, promotion pipelines.
   - *Limitations:* stationarity assumptions; state explosion if too granular.
3. **Queueing/inventory view of vacancies** (positions as servers, hiring as replenishment with lead time).
   - *Advantages:* naturally handles recruit lead times and backlog.
   - *Limitations:* abstraction may hide promotion-eligibility constraints.

Planned variables/parameters: per-level headcount, vacancy rate, hire rate, promotion rate, churn rate, tenure distributions, recruit lead time.

### 5.3 Layer C — Churn hazard & diffusion (SP3)

**Goal:** model each member's instantaneous churn propensity as a function of individual, positional, and network-influence factors.

Candidate methods:

1. **Proportional-hazard style churn model** $\lambda_i(t)=\lambda_0(t)\exp(\beta^\top x_i + \gamma\,(\text{churn exposure}_i))$, where churn exposure aggregates churned contacts along ties.
   - *Advantages:* interpretable coefficients; directly encodes the "connected to former employees" hypothesis.
   - *Limitations:* needs coefficient priors; proportional-hazards assumption unverifiable on synthetic data.
2. **Compartmental diffusion / epidemic-style model (SIR/SIS-like)** on the network, with churn as the "infection."
   - *Advantages:* captures diffusion and thresholds; well-studied cascade math.
   - *Limitations:* churn may not be reversible; mapping sentiment states needs care.
3. **Threshold / complex-contagion cascade model** where dissatisfaction accumulates and triggers exit past a threshold.
   - *Advantages:* models the "soured culture" dynamic and tipping points.
   - *Limitations:* threshold and accumulation parameters are latent.
4. **Agent-based simulation** combining individual decision rules with network interaction.
   - *Advantages:* integrates Layers A–D flexibly; supports the T5 scenarios naturally.
   - *Limitations:* computationally heavier; requires careful rule documentation and calibration.

Planned variables: baseline hazard, individual covariates $x_i$ (tenure, level, suitability proxy), churn-exposure count/weight, influence strength $\gamma$, recovery/immunity terms if used.

### 5.4 Layer D — Productivity linkage (SP4)

**Goal:** translate staffing, turbulence, and training states into a productivity signal, capturing both direct and indirect effects.

Candidate ideas:

1. **Productivity as a function of fill rate and experience mix** (diminishing-returns curve over fill rate; penalty for lost knowledge and onboarding).
2. **Network-dependent productivity** where output depends on communication efficiency, cluster cohesion, and coordination cost rising with hierarchical distance.
3. **Turbulence/overload penalty** where vacancies raise per-capita load, accelerate further churn, and reduce quality — creating a feedback loop into Layer C.
4. **Quality-composition term** reflecting the retention bias toward marginal performers (A14).

Planned variables: effective productivity index, fill-rate elasticity, onboarding drag, coordination cost, quality stock.

### 5.5 Layer E — Budget / talent-management cost (SP5)

**Goal:** express two-year recruiting and training requirements **in σ units**.

Candidate methods:

- A **unit-cost accounting model**: (expected hires per level × recruit cost coefficient) + (expected training load per level × training cost coefficient), aggregated and divided by σ to remain unitless.
- Optionally embedded inside the simulation so budget responds endogenously to churn scenarios.

Planned variables: expected hires by level and year, recruit cost coefficients, training cost coefficients, σ-relative totals.

### 5.6 Layer F — Scenario & policy engine (SP6, T5)

**Goal:** configure churn overrides and staffing policies without recomputation of the entire model.

Candidate designs:

- A **scenario configuration object** specifying per-level churn rates, recruiting on/off, promotion-only mode, and horizon.
- Decision rules for "HR health" metrics (fill rate trajectory, vacancy backlog, promotion-pipeline throughput, quality trend), defined in advance so scenarios are comparable.

### 5.7 Layer G — Multilayer network integration (SP7, T6)

**Goal:** describe how formal + informal layers (information, trust, influence, friendship) combine.

Candidate frameworks:

- **Multiplex / multilayer network formalism** (Kivelä et al.) with per-layer adjacency, inter-layer coupling, and multiplex measures (multidegree, layer overlap, edge overlap).
- **Team-science framing** (Salas et al.; Stokols et al.) connecting team composition, coordination, and productivity to network structure.
- A **layer-coupling plan**: how churn on one layer propagates to others; how HR would aggregate layer signals into a dashboard.

Planned variables: layers present, coupling strengths, multiplex centrality, layer-overlap metrics.

### 5.8 Integration architecture

The intended pipeline is: **Layer A (structure) → Layers B/C (flow + churn dynamics, coupled with feedback from Layer D) → Layer D (productivity) → Layer E (budget)**, with **Layer F** wrapping scenarios and **Layer G** providing the multi-layer extension. Feedback loops (vacancy → overload → churn) will be made explicit so the later analysis can identify tipping behavior.

### 5.9 Advantages and limitations of the overall framework

- *Advantages:* interpretable, modular, scenario-friendly, matched to σ-relative reporting, extensible to multilayer networks.
- *Limitations:* heavy reliance on assumptions (A4, A6–A9) because individual and tie-level data are absent; synthetic-population artifacts may bias network statistics; overlapping model layers risk double-counting unless interfaces are disciplined.

---

## 6. Implementation Roadmap

### 6.1 Planned modules

| Module | Responsibility | Depends on |
|--------|----------------|------------|
| `ingest` | Load and tidy `table1.csv`; normalize σ-denominated fields | — |
| `structure` | Build the hierarchical + informal network (Layer A) | ingest |
| `population` | Synthesize individual proxy records consistent with level aggregates | ingest, structure |
| `flow` | Compartmental/Markov staffing dynamics (Layer B) | ingest, population |
| `churn` | Hazard + diffusion model (Layer C) | structure, flow |
| `productivity` | Direct/indirect productivity linkage (Layer D) | flow, churn |
| `budget` | σ-unit recruiting/training cost model (Layer E) | flow, productivity |
| `scenario` | Configuration-driven scenario runner (Layer F) | all dynamic layers |
| `multilayer` | Layer coupling + multiplex metrics (Layer G) | structure |
| `validation` | Sanity checks, sensitivity sweeps, diagnostics | all |
| `reporting` | Figure/table generation for the final ≤21-page report | all |

### 6.2 Planned workflow

1. Finalize the assumption register and scenario configuration schema.
2. Implement `ingest` and produce the normalized level table and structural scaffolding.
3. Implement `structure` and `population`; verify synthetic-population aggregates match the source table.
4. Implement `flow` and `churn`; wire the vacancy→overload feedback.
5. Implement `productivity` and `budget`.
6. Implement `scenario` and run the T4/T5 configurations **in the later phase** (not now).
7. Implement `multilayer` coupling and multiplex metrics for the T6 narrative.
8. Run validation and sensitivity sweeps; freeze a parameter set.
9. Generate figures/tables and draft the final report with executive summary.

### 6.3 Planned tooling (to be selected later)

- A Python stack (network analysis + numerical simulation + tabular data), with reproducible scripting under `code/`, run logs under `logs/`, and generated artifacts under `results/`.
- Configuration files for scenarios so that churn overrides and recruiting toggles are declarative rather than hard-coded.
- Determinism controls (fixed seeds) so validation is repeatable.

### 6.4 Milestones and dependencies

- **M1:** Data ingestion + assumption register complete.
- **M2:** Static network + synthetic population reproducible.
- **M3:** Dynamics (flow + churn) integrated and internally consistent.
- **M4:** Productivity + budget layers wired.
- **M5:** Scenario engine validated on the baseline configuration.
- **M6:** Multilayer extension specified and demonstrated conceptually.
- **M7:** Sensitivity study + frozen parameter set.
- **M8:** Report-ready artifacts and narrative.

### 6.5 Risk register (planning-level)

| Risk | Impact | Planned mitigation |
|------|--------|--------------------|
| Assumption-driven artifacts (no individual data) | Conclusions may be fragile | Strong sensitivity analysis; declare assumptions prominently |
| Over-parameterization of churn/diffusion | Non-identifiability | Prefer sparse priors; sweep key parameters |
| Scenario contradictions (e.g., no recruiting vs. 80% target) | Counterintuitive outcomes | Define scenarios precisely; report trade-offs, not single numbers |
| Layer coupling ambiguity | Multilayer analysis may be under-specified | Publish a coupling specification before analysis |

---

## 7. Validation Strategy

### 7.1 Evaluation metrics (to be computed in the later phase)

**Structural validation**
- Synthetic-population aggregates vs. `table1.csv` counts and coefficients (exact-match targets).
- Degree distribution, clustering, and layer-overlap statistics plausibility checks.

**Dynamic validation**
- Stability of baseline simulation: does 18% aggregate churn emerge from the parameterization?
- Internal consistency: stock-flow conservation (hires + promotions − churns ≈ headcount change).
- Reproduction of stated organizational attributes (≈85% fill; middle-tier elevated turnover).

**Scenario validation**
- Monotonicity checks (higher churn should not improve fill rate or cost).
- Bounds checks (costs and productivity within plausible ranges).
- Cross-scenario comparability on a fixed "HR health" metric set.

### 7.2 Validation methods

1. **Face validity** — expert review of rules, structure, and outputs by the (future) HR stakeholder lens.
2. **Internal consistency / invariants** — accounting identities and conservation laws enforced and tested.
3. **Back-of-envelope reconciliation** — compare model-implied level totals and σ-ratios to the stated problem facts (e.g., 370 positions, 85% fill, 18% churn) as plausibility anchors.
4. **Cross-model comparison** — run the compartmental and agent-based variants side by side and compare aggregate behavior; divergence flags fragile assumptions.
5. **Stress/extreme-value testing** — push churn to extreme values to confirm the model behaves sensibly (no negative headcounts, no runaway loops without cause).

### 7.3 Sensitivity and uncertainty analysis plan

- **One-at-a-time (OAT) sweeps** over the highest-leverage assumptions: influence strength, informal-tie density, recruit lead time, fill-rate productivity elasticity, promotion-eligibility strictness, quality-retention bias.
- **Global sensitivity / variance-based methods** (e.g., variance decomposition or elementary-effects designs) to rank which assumptions dominate outputs.
- **Scenario-parameter sweeps** across churn levels spanning the T4 values (25%, 35%) and the T5 configuration (30% in the two middle tiers), with others held at baseline.
- **σ-inflation sensitivity** to confirm that σ-relative conclusions are robust to the drift mentioned in the data description.
- **Robustness of conclusions** — a conclusion will be reported as durable only if it survives the above perturbations; otherwise it will be labeled assumption-dependent.

---

## 8. Expected Result Interpretation

This section describes **how future outputs will be read**, not what they are.

- **Churn dynamics:** if the model will show influence-driven diffusion, we would expect churn to cluster in connected subgraphs; interpretation will focus on whether targetting highly exposed or highly central individuals would plausibly damp cascades, and on early-career intervention points.
- **Budget (σ units):** two-year recruiting and training requirements will be read as σ-multiples, compared against each other and against the organization's stated cost structure; the interpretation will emphasize relative magnitude and the recruiting-vs-training trade-off rather than absolute currency.
- **Sustained staffing at 25%/35% churn:** the interpretation will consider whether fill rate can remain near 80% under the recruiting lead times, and what indirect costs (overload, quality, coordination) may co-move with the required hiring effort.
- **T5 promotion-only / no-recruiting scenarios:** the reading will center on pipeline bottlenecks and vacancy accumulation in the two middle tiers, and on the downstream HR-health consequences, with explicit statements of which effects are direct vs. indirect.
- **Multilayer / team-science vision:** the interpretation will frame HR-led multilayer integration as a governance and data strategy, positioning formal and informal layers as complementary signals for talent management.

All interpretations will be conditional and assumption-annotated. **No interpretive statement will be presented as a final conclusion in this blueprint.**

---

## 9. Limitations and Improvements

### 9.1 Known limitations of the planned approach

- **Data sparsity.** Only level-level aggregates are staged; individuals, ties, tenure, and evaluations must be synthesized, so the network's fine structure is assumption-driven (A4, A6–A9).
- **Model plurality.** Multiple candidate models (compartmental vs. agent-based vs. Markov) may give divergent answers; reconciliation is nontrivial.
- **Scenario paradoxes.** Instructions such as "no external recruiting while sustaining staffing" are internally tense; the model will surface, not hide, such tensions.
- **Parameter non-identifiability.** Several dynamic parameters (influence, thresholds, elasticities) cannot be uniquely pinned without more data.
- **Quality modeling.** The retention bias toward marginal performers is hard to quantify from the available data alone (A14).
- **Multilayer realism.** Informal layers will initially be plausible constructs rather than measured structures.

### 9.2 Planned improvements and extensions

- **Data enrichment:** pursue individual tenure, evaluation, and tie data to replace synthesized attributes; add time-series churn for calibration.
- **Richer churn mechanisms:** differentiate voluntary vs. involuntary exit, retirement, and boomerang hires; add career-stage effects.
- **Refined promotion constraints:** encode experience-eligibility rules explicitly and test alternative strictness regimes.
- **Dynamic multilayer coupling:** move from a conceptual Layer G to a calibrated multiplex model with cross-layer metrics.
- **Optimal-policy layer:** add an optimization/control layer that proposes recruiting, training, and promotion policies against stated HR-health objectives.
- **Uncertainty communication:** adopt a consistent scheme (scenarios, ranges, or distributions) for reporting uncertainty in the final report.
- **Reproducibility:** freeze seeds, versions, and configuration files so all later results are auditable.

---

## Appendix A — Planning Checklist (for the later phase)

- [ ] Assumption register finalized and versioned.
- [ ] `table1.csv` ingested, normalized, and structural scaffolding built.
- [ ] Static network + synthetic population reproduce source aggregates exactly.
- [ ] Dynamic layers integrated with explicit feedback loops.
- [ ] Scenario configuration schema supports all T4/T5 variants.
- [ ] Validation invariants and sensitivity sweeps pass.
- [ ] Multilayer/team-science architecture documented.
- [ ] Report artifacts generated; narrative drafted (≤21 pages incl. executive summary).

## Appendix B — Traceability Matrix (task → planned modules)

| Task | Planned modules | Planned output |
|------|-----------------|----------------|
| T1 | ingest, structure, population | network schema + assumption register |
| T2 | flow, churn, productivity | dynamic-process specification |
| T3 | budget | σ-unit two-year cost framework |
| T4 | scenario, budget, productivity | staffing-sustainability scenario design |
| T5 | scenario, flow | promotion/recruiting scenario design |
| T6 | multilayer | integration architecture narrative |
| T7 | reporting | report skeleton + figure plan |
