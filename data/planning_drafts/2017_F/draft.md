# Modeling Blueprint Draft — MM-Bench 2017_F

**Problem ID:** `2017_F`
**Title:** MM-Bench 2017_F (Project UTOPIA: 2100 — Population Zero on Mars)
**Source:** MM-Bench 2017
**Document type:** Modeling plan / blueprint draft (planning only — no solution, no data analysis, no computation performed)
**Status:** Initial draft for future modeling work

> This document is a roadmap. It intentionally contains **no computed results, no fitted models, no executed experiments, and no final conclusions**. All statements are prospective ("will", "intend to", "plan to") and describe how the modeling effort should be organized.

---

## 1. Problem Background and Restatement

### 1.1 Narrative setting

By 2095 the international agency **LIFE (Laboratory of Interstellar Financial & Exploration Policy)** has completed short-term planned-living experiments on Mars. Personalized artificial augmentation units and manufactured cities will allow human habitation of Mars by **2100**. The first migration wave, **Population Zero**, will consist of **10,000 people**. LIFE has launched **Project UTOPIA: 2100** to design an optimal 22nd-century workforce and to give all citizens the greatest quality of life with a 100-year sustainability vision.

The agent is asked to develop **mathematical and computational models** that inform the **International Coalition on Mars (ICM)** on how to design an **economic workforce–education system** for Population Zero. The mission is to build a **sustainable society that maximizes both economic output (GDP) and workplace happiness**, while managing the tension between those two goals. **Health care is explicitly out of scope** (handled by a separate team).

### 1.2 Restatement of the modeling mandate

The effort must produce a **policy model plus policy recommendations** that create a sustainable life-plan and that make life on Mars in 2100 better than Earthly life in 2095. Three **priority factors** must be defined, parameterized, modeled, integrated, stress-tested, and translated into policy:

1. **Income** — adequate compensation so all citizens can afford fundamental necessities (shelter, food, clothes); minimum wage and salary distribution.
2. **Education** — high-quality education preparing citizens for 22nd-century needs; required skills, and the governance/infrastructure to obtain them.
3. **Social Equality** — improving retention of women in the workforce (especially underrepresented fields); maternity/paternity leave; affordable childcare enabling continued workforce participation.

### 1.3 Scope boundaries that shape the plan

- **In scope:** workforce economics, education/skills pipelines, income distribution, gender/workforce equality, childcare and parental leave, governance and infrastructure for skills, migration scaling, robustness.
- **Out of scope:** health-care policy (explicitly excluded by ICM).
- **Deliverable form:** a defensible quantitative model suite + policy recommendation addressed to the LIFE director, justified by model outputs and sensitivity/robustness analysis.

### 1.4 Data situation (as observed)

- The staged `data` directory is currently **empty**, and the provided dataset definition is **vacuous** (`dataset_path: []`, `dataset_description: {}`, `variable_description: {}`).
- Consequence for planning: the data plan (Section 4) must treat **data acquisition or synthesis as a first-class task** — either by extracting a real census source (e.g., ACS PUMS 1-year) or by generating a **synthetic Population Zero**, both explicitly permitted by Task 2 of the problem.

---

## 2. Objectives and Subproblems

### 2.1 Overarching objective

Design a **modeling framework** whose outputs can determine, for a 10-year horizon (2100–2110) and a 100-year vision, an **optimal minimum wage and salary distribution, an education/skills pipeline, and childcare/parental-leave policies** that jointly maximize a balanced objective of **economic output** and **workplace happiness**, subject to equality and sustainability constraints — and that remains functional when migration is scaled up dramatically (comet evacuation).

### 2.2 Objectives decomposed (what the future model must be able to answer)

- **O1 — Outcomes & metrics:** identify and define positive-result outcomes for each of income, education, and equality over 2100–2110, and define the critical parameters/metrics that evaluate whether the system meets its objective (Task 1).
- **O2 — Population construction:** generate/obtain a 10,000-person sample population, describe its demographic distributions, and judge whether additional structural distributions (innovators vs. producers, skilled vs. unskilled, families vs. singles) are needed (Task 2).
- **O3 — Factor models:** build an income model, an education model, and an equality model; integrate them; capture interdependencies; add preservation constraints over the horizon; define re-evaluation cadence; and identify external economic/social/cultural/global risk factors (Task 3).
- **O4 — Global + subgroup models:** merge factor models into a global model, then adapt it to workforce subgroups with distinct priorities without significantly degrading global outcomes (Task 4).
- **O5 — Multi-phase migration:** test sensitivity to population selection across migration phases and extend the model to repeated 10,000-person waves over 100 years (Task 5).
- **O6 — Catastrophic scaling:** evaluate model functionality, phased vs. single-wave behavior, robustness, strengths, and weaknesses under an Earth-evacuation-scale migration (Task 6).
- **O7 — Policy recommendation:** translate the model into a policy memo to the LIFE director covering income, education, and equality, with reasoning and expected (not yet computed) achievement outcomes, and discuss dependence on Population Zero composition/size (Task 7).

### 2.3 Subproblem → method-family map (planning view)

| Subproblem | Planning intent | Candidate method families (details in §5) |
|---|---|---|
| Task 1 (parameters/metrics) | Define outcome variables, KPIs, thresholds | Indicator design, multi-criteria decision analysis |
| Task 2 (population) | Build 10,000-person synthetic/real sample | Stratified sampling, IPF/synthetic population, PUMS extraction |
| Task 3 (three-factor integrated model) | Coupled income–education–equality system + control cadence | System dynamics, constrained multi-objective optimization, human-capital production functions |
| Task 4 (global + subgroups) | Subgroup-aware optimization | Clustering / latent-class, multi-objective Pareto analysis |
| Task 5 (multi-phase migration) | Sensitivity to sampling and scaling over 100 yr | Monte Carlo, sampling-variance analysis, dynamic re-optimization |
| Task 6 (catastrophe scaling) | Robustness under large-scale evacuation | Scaling laws, capacity-constrained optimization, robustness/sensitivity analysis |
| Task 7 (policy memo) | Translate model outputs into decisions | Decision synthesis, scenario comparison |

### 2.4 Deliverables the plan must ultimately enable

1. A defined **parameter/KPI dictionary** for income, education, equality.
2. A **demographic dataset** (real or synthetic) for Population Zero with documented sampling procedure.
3. A **three-factor integrated model** with interdependency and constraint specification.
4. A **global, subgroup-aware model** with constraints balancing subgroup vs. global objectives.
5. A **multi-phase / 100-year extension** and **catastrophic-scaling robustness study design**.
6. A **policy recommendation** structure addressed to the LIFE director.

---

## 3. Assumptions

Assumptions are grouped by role. Each lists a **justification** and a **future validation approach** (how the eventual modeler will test the assumption rather than accept it blindly).

### 3.1 Population and demography

- **A1 — Population is closed and self-contained.** Population Zero is an isolated 10,000-person society; external labor migration is absent within the 10-year horizon.
  - *Justification:* Mars settlement is physically isolated during 2100–2110.
  - *Future validation:* compare model behavior with and without inter-phase migration inflows; test sensitivity of outputs to inflow rate.
- **A2 — Demographic structure can be represented by a finite set of strata** (age, gender, ethnicity, education, skill, family status).
  - *Justification:* enables tractable stratified sampling and aggregation.
  - *Future validation:* test whether adding finer strata materially changes headline outcomes (stratification granularity sensitivity).
- **A3 — Skill and education levels are measurable on an ordinal scale** and map to productivity ranges.
  - *Justification:* needed to connect education policy to economic output.
  - *Future validation:* perturb the skill→productivity mapping and re-examine policy rankings.

### 3.2 Economic mechanisms

- **A4 — Aggregate output is a function of labor quantity and quality (human capital).** No fully automated post-labor economy within the horizon.
  - *Justification:* the problem frames Population Zero around a workforce and GDP.
  - *Future validation:* introduce automation/augmentation productivity multiplier and re-run.
- **A5 — Wage distribution can be modeled as a parametric/structural distribution shaped by policy levers** (minimum wage, subsidies, leave costs).
  - *Justification:* needed to optimize "minimum wage + salary distribution."
  - *Future validation:* compare parametric fits against nonparametric alternatives and against synthetic labor-market simulations.
- **A6 — Wellbeing/happiness has a measurable, monotone-in-income-but-saturating relationship with income, leisure, and security.**
  - *Justification:* the mission explicitly balances GDP against workplace happiness.
  - *Future validation:* test alternative utility/satisfaction functional forms and check ranking stability.

### 3.3 Education and equality

- **A7 — Education investment translates into skill supply with a lag** (multi-year pipeline).
  - *Justification:* curricula and training take time; relevant to 10-year and 100-year horizons.
  - *Future validation:* vary the pipeline delay and observe policy timing effects.
- **A8 — Childcare availability and parental leave are the dominant levers for female workforce retention** in the modeled context.
  - *Justification:* directly named in the problem's equality factor.
  - *Future validation:* include alternative levers (flexible work, anti-discrimination enforcement) and compare explanatory power.
- **A9 — Equality is a multi-dimensional construct** (participation rate, wage gap, representation by field, advancement).
  - *Justification:* the problem names retention, underrepresentation, and discrimination.
  - *Future validation:* check whether optimizing one equality dimension degrades another (trade-off analysis).

### 3.4 Modeling-method assumptions

- **A10 — A coupled system-dynamics + multi-objective optimization representation is expressive enough** to capture income–education–equality feedbacks at this scale.
  - *Justification:* balances interpretability (needed for policy) with dynamic feedback.
  - *Future validation:* cross-check key conclusions with an independent agent-based simulation.
- **A11 — Near-term (2100–2110) policy is the primary optimization target**, with the 100-year vision treated as a sustainability constraint set rather than a fully optimized objective.
  - *Justification:* the problem asks for concrete 10-year outcomes and separately for 100-year sustainability.
  - *Future validation:* re-optimize directly on 100-year objectives and compare recommended policies.
- **A12 — Parameters not derivable from data will be set from literature/domain reasoning and subjected to sensitivity analysis** rather than assumed exact.
  - *Justification:* many Mars-2100 quantities are unobservable.
  - *Future validation:* global sensitivity analysis to rank which assumed parameters most affect policy choice (see §7).

### 3.5 Out-of-scope assumptions

- **A13 — Health care is excluded** from all objectives, constraints, and metrics (per ICM).
- **A14 — Legal/governance structure for enforcement is assumed available** (the model recommends policy, not political feasibility).

---

## 4. Data Processing Plan

Because the staged `data` directory is empty and the dataset definition is vacuous, the plan must specify **both** data-source pathways and a synthetic-generation pathway, and must document whichever is chosen.

### 4.1 Data source strategy (choose-and-document)

- **Pathway P1 — Real census extraction (ACS PUMS 1-year).** Plan to use the ACS PUMS 1-year microdata referenced in the problem (2015 1-year PUMS; documentation links provided). Extract person-level and household-level records.
- **Pathway P2 — Synthetic population generation.** If PUMS access/coverage is unsuitable, synthesize a population with controlled marginal distributions calibrated to published demographic targets (age × gender × education × household structure), using iterative proportional fitting (IPF) or a similar raking/synthesis approach.
- **Pathway P3 — Hybrid.** Use PUMS marginals to calibrate a synthetic generator, combining realism with controllable structure.
- *Planned decision record:* document source, vintage, license, sample size, weighting, and any resampling to exactly 10,000.

### 4.2 Sampling design for Population Zero (10,000 people)

- **Stratified sampling** across key strata (age band, gender, education, skill category, family status, ethnicity), with target strata proportions to be chosen to serve the UTOPIA egalitarian goals as well as realism.
- **Weighting / calibration** so the synthetic sample matches intended Population Zero composition (a lever the plan will expose for Task 5 sensitivity — the composition choice is a *model input*, not a fixed fact).
- **Reproducibility:** fixed sampling seeds, documented strata definitions, and stored sample draws so migration phases can be compared under controlled variation.

### 4.3 Preprocessing pipeline (planned steps)

1. **Ingestion & schema mapping** — align raw fields to a canonical person/household schema.
2. **Cleaning** — missing-value handling, out-of-range flagging, unit harmonization.
3. **Recoding** — categorical consolidation (education levels, occupation groups, industry), ordinal skill coding.
4. **Derived features** — dependency ratio, household composition, potential labor supply, caregiving demand, skill–occupation match indicators.
5. **Aggregation layers** — stratified tables by subgroup for the global/subgroup models.
6. **Documentation** — a data dictionary capturing each transformation and its rationale.

### 4.4 Feature construction (planned categories)

- **Income features:** wage/salary bands, household income, cost-of-necessities baseline, income adequacy ratio.
- **Education features:** attainment level, field-of-study grouping, training participation, skill match index, education pipeline lag.
- **Equality features:** labor-force participation by gender, wage-gap indicators, representation indices by field, parental-leave uptake, childcare accessibility proxies.
- **Population structure features:** age structure, family vs. single distribution, innovator/producer and skilled/unskilled splits (per Task 2b).

### 4.5 Data usage strategy

- **Training/calibration vs. validation splits** at the synthetic-population level (calibrate structural parameters on a base draw; hold out alternate draws for validation).
- **Scenario population sets:** the plan will define several composition scenarios (varying gender balance, skill mix, family structure) to drive Task 5 sensitivity rather than a single fixed population.
- **Traceability:** every downstream result will be linked to the exact population draw and preprocessing version.

---

## 5. Candidate Model Framework

The framework is layered; the plan will build lower layers first and integrate upward. All families are candidates whose final inclusion will be justified by interpretability, data support, and sensitivity.

### 5.1 Layer 0 — Population / demography model

- **Candidate methods:** stratified sampling; synthetic population generation (IPF/raking); optional agent-based demographic microsimulation for household formation.
- **Role:** supplies the state vector (counts by stratum) that all higher layers consume.

### 5.2 Layer 1 — Income model

- **Candidate methods:**
  - Structural wage-distribution modeling (e.g., parametric heavy-tailed wage distributions conditioned on skill/education/gender).
  - Minimum-wage impact modeling (labor-demand elasticity, employment effects, adequcy-to-necessities constraint).
  - Constrained optimization for minimum wage + salary-distribution levers balancing **wellbeing vs. support for the least-equipped** (Task 3a).
- **Key variables (planned):** minimum wage, wage dispersion parameters, subsidy/transfer levels, cost-of-necessities basket, employment level, labor-demand response.
- **Interdependencies flagged:** wage levels ↔ education returns ↔ workforce participation ↔ childcare affordability.

### 5.3 Layer 2 — Education model

- **Candidate methods:**
  - Human-capital accumulation model (stock–flow of skills with pipeline lag).
  - Skill–demand matching / production-function coupling (education supply ↔ productive need).
  - Network/knowledge-diffusion models for identifying roles where new ideas matter most (Task 3b).
  - Incentive design for innovation contributions (rewards, recognition, IP-like structures).
- **Key variables (planned):** education investment, curriculum mix, training capacity, skill stock by tier, innovation contribution rate, incentive strength.
- **Interdependencies flagged:** education ↔ wages ↔ equality (access) ↔ productivity ↔ GDP.

### 5.4 Layer 3 — Social equality model

- **Candidate methods:**
  - Workforce-participation dynamics (Markov/stock–flow of participation states incl. leave).
  - Childcare capacity/cost model (supply–demand, subsidization).
  - Parental-leave policy evaluation (duration, split, wage replacement) against retention and cost.
  - Wage-gap decomposition (explained vs. unexplained components) — to be handled as a planning construct, not computed here.
- **Key variables (planned):** leave duration and replacement rate, childcare slots and fees, participation rates by gender, retention rates, representation indices.
- **Interdependencies flagged:** childcare/leave ↔ participation ↔ income ↔ GDP ↔ equality.

### 5.5 Layer 4 — Integrated three-factor model

- **Candidate methods:**
  - **System dynamics (stock–flow)** capturing feedback loops among income, education, equality, GDP, and wellbeing.
  - **Multi-objective optimization** (e.g., Pareto-based evolutionary methods) over policy levers, with GDP and happiness as competing objectives.
  - **Constraint set for 10-year preservation:** budget balance, adequacy/minimum-standard constraints, participation floor, inequality bounds, sustainability caps.
- **Integration artifacts (planned):** a variable/parameter dictionary; an interdependency matrix; a re-evaluation cadence specification (Task 3 asks *how often* the model should be evaluated); an exogenous-risk register (economic, social, cultural, global shocks).

### 5.6 Layer 5 — Global + subgroup model

- **Candidate methods:**
  - **Subgroup identification** via clustering / latent-class segmentation of the workforce (unskilled labor, professional, caregivers, etc.) with priority weights per subgroup.
  - **Multi-objective optimization with subgroup constraints** — maximize subgroup priority outcomes subject to a bounded degradation of global outcomes.
  - **Multi-criteria decision analysis** (e.g., AHP/TOPSIS) to formalize differing subgroup success criteria.
- **Planned outputs:** subgroup priority maps; constraint adjustments; global-vs-subgroup trade-off curves.

### 5.7 Layer 6 — Scaling / robustness extension

- **Candidate methods:**
  - **Sampling-variance and Monte Carlo analysis** across population draws (Task 5a).
  - **Scaling-law / capacity-constrained models** for large-scale evacuation (Task 6a–b), including phased vs. single-wave comparison.
  - **Robustness measures** (worst-case, regret, feasible-region stability) rather than point-optimal policies.
- **Planned outputs:** sensitivity ranking of population-selection choices; degradation curves as scale grows; a strengths/weaknesses statement relative to mass migration.

### 5.8 Model-candidate comparative summary

| Layer | Primary candidate | Backup candidate | Why both are kept |
|---|---|---|---|
| Population | Stratified sampling + IPF | Agent-based microsimulation | Simplicity vs. richer household dynamics |
| Income | Structural wage + constrained optimization | Direct optimization over policy grid | Analytical transparency vs. flexibility |
| Education | Human-capital stock–flow | Network diffusion of ideas | Aggregate supply vs. innovation targeting |
| Equality | Participation/leave/childcare dynamic model | Statistical gap decomposition | Mechanism vs. descriptive |
| Integration | System dynamics + multi-objective optimization | Coupled ODE + Pareto search | Physical intuition vs. computational search |
| Subgroups | Clustering + constrained MOO | MCDA weighting | Data-driven vs. preference-driven |
| Scaling | Monte Carlo + capacity constraints | Scenario-based stress testing | Distributional vs. worst-case |

---

## 6. Implementation Roadmap

### 6.1 Planned module decomposition

1. **`data_ingest`** — PUMS extraction or synthetic generation; schema/versioning.
2. **`preprocess`** — cleaning, recoding, derived features, stratification tables.
3. **`pop_model`** — sampling/generation of Population Zero draws and scenario populations.
4. **`income_model`** — wage distribution + minimum-wage optimization component.
5. **`education_model`** — human-capital pipeline + innovation-incentive component.
6. **`equality_model`** — participation/leave/childcare dynamics.
7. **`integration`** — system-dynamics core + multi-objective optimizer + constraint set.
8. **`subgroup`** — segmentation + subgroup-constrained optimization.
9. **`scaling`** — Monte Carlo, capacity constraints, catastrophe scenarios.
10. **`policy`** — recommendation synthesis and reporting layer.
11. **`validation`** — metrics harness, sensitivity engine, reproducibility checks.

### 6.2 Workflow (planned sequence)

1. **Frame** — finalize objective definitions, KPI dictionary, scope boundaries. *(Tasks 1)*
2. **Populate** — acquire or synthesize the 10,000-person dataset; document sampling. *(Task 2)*
3. **Model factors** — build income, education, equality models independently; document interdependencies. *(Task 3)*
4. **Integrate** — merge into a system-dynamics + multi-objective framework; define constraints and cadence. *(Task 3)*
5. **Segment** — identify subgroups; add subgroup constraints; re-optimize. *(Task 4)*
6. **Scale** — run Monte Carlo / multi-phase sensitivity and 100-year extension. *(Task 5)*
7. **Stress** — catastrophe-scale robustness study. *(Task 6)*
8. **Translate** — produce the policy recommendation memo. *(Task 7)*

### 6.3 Tooling outlook (planning, not executed)

- **Language/environment:** R or Python for data handling and optimization; MATLAB acceptable per the problem's hints; a system-dynamics package and a multi-objective optimizer library will be selected during implementation.
- **Reproducibility:** versioned data snapshots, fixed random seeds, parameter registries, and configuration files driving each run.
- **Compute:** standard workstation or modest cluster is expected to suffice for a 10,000-agent/population-scale study; larger catastrophe scenarios will drive the need for efficient simulation or surrogate models.

### 6.4 Planned artifacts per task

| Task | Planned artifact |
|---|---|
| 1 | Parameter/KPI dictionary + outcome definitions |
| 2 | Documented Population Zero dataset + demographic profile |
| 3 | Three-factor integrated model + interdependency matrix + risk register |
| 4 | Subgroup map + adjusted global model |
| 5 | Multi-phase sensitivity study design + 100-year extension spec |
| 6 | Robustness report structure (strengths/weaknesses) |
| 7 | Policy recommendation memo skeleton |

---

## 7. Validation Strategy

### 7.1 Evaluation metrics (to be computed by the future solver, not here)

- **Economic output:** GDP per capita and aggregate GDP; productivity; labor-force utilization.
- **Wellbeing:** workplace-happiness index; income adequacy vs. necessities basket.
- **Equality:** female participation/retention rate; wage-gap measures; representation indices; childcare-access coverage.
- **Education:** skill-match rate; attainment distribution; pipeline throughput.
- **Balancing measures:** a composite objective representing the GDP-vs-happiness tension (e.g., Pareto frontier position, weighted trade-off, or distance-to-frontier).

### 7.2 Validation methods (planned)

- **Internal consistency checks:** stock–flow conservation, budget balance, non-negativity, constraint satisfaction.
- **Face validity with domain reasoning:** do directions of effects align with established labor-economics intuition?
- **Cross-model validation:** compare system-dynamics conclusions against an independent agent-based or reduced-form model.
- **Historical/analogue back-testing:** calibrate on Earth's tested planned-community data where available and replay to check qualitative behavior.
- **Scenario-based validation:** compare against explicitly constructed "policy counterfactuals."

### 7.3 Sensitivity and robustness analysis (planned)

- **Global sensitivity analysis:** variance-based (e.g., Sobol) and screening (e.g., Morris) methods to rank which parameters drive policy choice.
- **Sampling sensitivity:** vary Population Zero composition draws to quantify outcome dispersion and sampling-procedure dependence (Task 5a).
- **Structural sensitivity:** swap functional forms (wage distribution, wellbeing curve, production function) and test ranking stability.
- **Scaling robustness:** sweep migration size and phasing; measure feasible-region shrinkage and recommendation stability (Task 6a–b).
- **Regret/worst-case analysis:** evaluate policies under adversarial/uncertain scenarios to prefer robust over fragile recommendations.

### 7.4 Reproducibility and documentation plan

- Registered seeds, versioned inputs, and a parameter ledger; every reported number traceable to a configuration and data version.
- A decision log recording why a given candidate model family was included or excluded.

---

## 8. Expected Result Interpretation

This section describes **how the future results should be read**, not what they will be.

- **Policies as regions, not points.** The minimum wage/salary, education, and leave policies will likely be interpreted as **feasible regions / Pareto sets** rather than single optima, because GDP and happiness are in tension.
- **Cadence recommendation framing.** The model will be interpreted to suggest a **re-evaluation cadence** for the 10-year horizon (e.g., periodic recalibration triggered by milestone indicators), with rationale tied to feedback lag and exogenous risk.
- **Trade-off interpretation.** Subgroup optimization will be read as **how much global loss is acceptable** to raise specific subgroup priorities — a negotiated trade-off, not a mathematical certainty.
- **Scaling interpretation.** Results will be interpreted as **how recommendations degrade** as migration grows and how phased vs. single-wave structures differ, informing contingency planning.
- **Policy-memo interpretation.** The recommendation will be framed as **conditional guidance**: "if Population Zero composition is X and scale is Y, prefer policy set P," with explicit reasoning chain and expected-achievement claims that are hypotheses for the eventual solver to test.

---

## 9. Limitations and Improvements

### 9.1 Planned limitations (anticipated)

- **Data limitation:** absence of a real Mars-2100 dataset; reliance on Earth census proxies or synthetic populations introduces representativeness risk.
- **Unobservable parameters:** many future/Mars parameters cannot be estimated from data and must be assumed, so conclusions will be assumption-sensitive.
- **Model-class limitation:** system-dynamics aggregation may miss fine-grained behavioral heterogeneity; multi-objective optimization may face scalability limits as constraints multiply.
- **Equilibrium-vs-disequilibrium:** many labor/economic relations will be modeled as smooth responses, potentially underrepresenting shocks and path dependence.
- **Health exclusion:** excluding health care limits realism of wellbeing but respects ICM scope.

### 9.2 Planned improvements / future extensions

- Add **innovation/idea-contribution mechanisms** with explicit incentive design (Task 3b) as a first-class model element.
- Incorporate **behavioral heterogeneity** (agent-based layer) for subgroup realism.
- Introduce **dynamic re-optimization / control** so policies adapt within the horizon rather than being static.
- Build **surrogate models** to enable broad catastrophe-scale sensitivity studies.
- Add **governance/infrastructure feasibility constraints** to check political-administrative implementability.
- Strengthen **robustness-first policy design** so recommendations remain valid under deep uncertainty about composition, scale, and shocks.

### 9.3 Open planning questions to resolve during implementation

1. Which data pathway (P1/P2/P3) will be adopted, and how will composition targets be chosen?
2. What exactly constitutes the "workplace happiness" objective and how will it be operationalized?
3. Which re-evaluation cadence and trigger thresholds should the model recommend?
4. How should subgroup priority weights be elicited (data-driven vs. stakeholder-set)?
5. What robustness criterion (minimax vs. regret vs. CVaR-style) best fits UTOPIA's sustainability mandate?

---

## Appendix A — Task-to-Section Traceability

| Problem Task | Covered by plan sections |
|---|---|
| Task 1 (params/metrics) | §2.2 O1, §3.1–3.3, §5.2–5.5 |
| Task 2 (population) | §2.2 O2, §4, §5.1 |
| Task 3 (three-factor model) | §2.2 O3, §5.2–5.5, §7 |
| Task 4 (global + subgroups) | §2.2 O4, §5.6 |
| Task 5 (multi-phase / 100 yr) | §2.2 O5, §5.7, §7.3 |
| Task 6 (catastrophe scaling) | §2.2 O6, §5.7, §7.3, §8 |
| Task 7 (policy memo) | §2.2 O7, §8 |

## Appendix B — Planning Guardrails (compliance with blueprint-only mandate)

- No computation, fitting, or data analysis has been performed.
- No results, plots, or conclusions have been produced.
- All quantities are described as planned parameters/variables, not observed values.
- The staged data directory is empty; the plan therefore treats data acquisition/synthesis as an explicit, documented task.
