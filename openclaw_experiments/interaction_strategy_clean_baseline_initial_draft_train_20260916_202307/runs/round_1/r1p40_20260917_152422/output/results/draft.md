# Modeling Blueprint Draft — Managing Sustainable Tourism in Juneau, Alaska

**Problem ID:** `2025_Managing_Sustainable_Tourism`
**Source:** MCM 2025, Problem B
**Document type:** Modeling plan / blueprint draft (design only — no solution, no computed results)

> This document is a roadmap for future modeling work. It intentionally contains **no results, no data analysis, no fitted models, and no conclusions**. All statements are forward-looking descriptions of *what will be done* and *how it will be validated*.

---

## 1. Problem Background and Restatement

Juneau, Alaska, is a small community (population ≈ 30,000) that receives an outsized volume of tourism, driven primarily by cruise passengers (≈ 1.6 million in 2023, with peak-day visitor loads on the order of 20,000). Tourism generates substantial revenue (≈ \$375 million in the referenced year) but also produces "hidden costs": pressure on physical and organizational infrastructure, an elevated carbon footprint, housing and cost-of-living stress for residents, and environmental degradation at natural attractions (e.g., the receding Mendenhall Glacier).

Local authorities have begun deploying stabilization measures — increased hotel taxes, visitor fees, and daily visitor caps — but the system-level consequences of these interventions are not well understood.

**Restatement in planning terms:** The future modeling effort will build a decision-support framework that links *visitor flows*, *economic outcomes*, and *environmental and social costs* into a single coupled system, so that management levers (fees, taxes, caps, promotion of alternative attractions, infrastructure investment) can be evaluated against sustainable-tourism objectives. The framework will then be generalized for other overtourism-prone destinations and summarized in a one-page memo for a tourist council.

**Deliverables to be produced later (not now):**
- A complete modeling solution (model definition, calibration plan, analysis results).
- A sensitivity analysis identifying the dominant factors.
- A generalization/adaptation demonstration for other destinations.
- A one-page executive memo for the tourist council.

---

## 2. Objectives and Subproblems

The eventual work will be organized around three primary objectives and their subproblems.

### Objective A — Develop a sustainable-tourism system model
- **A1: System boundary and variable definition.** Decide which stocks and flows (visitor population, revenue, costs, environmental load, resident welfare) are endogenous vs. exogenous.
- **A2: Objective function(s) and constraints.** Formulate what is being optimized (e.g., a weighted multi-objective function over economic benefit, environmental impact, and resident quality-of-life) and define constraints (budget, caps, carrying capacity, legal/administrative feasibility).
- **A3: Stabilization-measure modeling.** Represent taxes, fees, and daily caps as controllable levers that feed back into visitor demand and revenue.
- **A4: Expenditure planning.** Plan how additional revenue is allocated across mitigation streams (infrastructure, environmental restoration, resident benefits, attraction diversification).
- **A5: Sensitivity analysis.** Determine which parameters and factors most strongly influence sustainability outcomes.

### Objective B — Adapt the model to other destinations
- **B1: Parameter-transfer framework.** Define which parameters are location-specific (climate, seasonality, accessibility, carrying capacity, economic baseline) and which are structural.
- **B2: Location-dependence of measure effectiveness.** Plan an analysis of how the same measure performs differently under different destination profiles.
- **B3: Redistribution mechanism.** Design a mechanism that promotes less-visited attractions to balance load across a region.

### Objective C — Policy communication product
- **C1:** Plan the structure of the one-page memo (predictions, effects of measures, recommendations) as a downstream translation of model outputs.

**Cross-cutting success criteria (to be evaluated later):** internal consistency, transparency of assumptions, reproducibility, robustness of recommendations to parameter uncertainty, and defensibility before a non-technical council.

---

## 3. Assumptions

Assumptions will be stated explicitly, classified, and each will carry a planned validation route.

### 3.1 Scope and boundary assumptions
1. Juneau is treated as a closed decision unit for the primary model, with external visitor demand as an exogenous input.
2. The primary decision horizon is a multi-year planning horizon with annual (or seasonal) resolution; short-term daily dynamics may be handled in a secondary sub-model.
3. Cruise tourism dominates visitor volume and is therefore the primary controllable channel.

### 3.2 Behavioral assumptions
4. Visitor demand responds to price signals (fees/taxes) with a finite, estimate-able elasticity; demand does not respond instantaneously.
5. Visitor spending patterns can be represented as an average spend distribution per visitor type.
6. Residents' welfare can be proxied by a composite index combining crowding, housing pressure, and environmental quality.

### 3.3 Environmental assumptions
7. Environmental impact (including carbon footprint) scales with visitor volume and activity mix, with distinct coefficients per activity.
8. Environmental degradation (e.g., glacier retreat) is only partially attributable to tourism and is modeled as tourism-attributable pressure plus a natural baseline trend.

### 3.4 Methodological assumptions
9. Parameters unknown at design time will be treated as tunable and subjected to sensitivity/uncertainty analysis rather than fixed silently.
10. Linearity is an acceptable first-order approximation where non-linear feedbacks are not yet justified by evidence.

### 3.5 Justification and future validation
- Each assumption will be tagged with (a) why it is plausible, (b) its expected influence on conclusions, and (c) a planned validation method — e.g., literature/benchmark comparison, refitting against observed years, or perturbation analysis to test whether conclusions flip if the assumption is relaxed.
- Assumptions expected to be most fragile (demand elasticity, activity attribution of environmental load) will receive dedicated sensitivity treatment.

---

## 4. Data Processing Plan

> No data will be analyzed in this draft. This section describes the *intended* pipeline.

### 4.1 Candidate data sources (to be collected/confirmed later)
- Cruise and visitor volume statistics (port calls, passenger counts, seasonality).
- Economic data: tourism revenue, taxes/fees collected, employment, business activity.
- Environmental indicators: emissions estimates per activity, air/water quality, glacier-retreat records.
- Infrastructure and social indicators: road/utility load, housing costs, resident sentiment surveys.
- Reference material from the problem's cited sources (cruise-limits reporting, the cruise-impacts report, Mendenhall Glacier reporting, the "invisible burden" framework).

### 4.2 Preprocessing plan
- **Harmonization:** standardize units, time resolution, and geographic scope across sources.
- **Gap handling:** define rules for interpolating missing years vs. flagging unknowns for sensitivity treatment.
- **Outlier/consistency checks:** identify anomalous reporting years and treat them explicitly.
- **Provenance tracking:** maintain a source/assumption register so every input is traceable.

### 4.3 Feature construction plan
- Derived demand features (seasonal indices, peak-to-average ratios).
- Per-visitor normalized metrics (revenue per visitor, emissions per visitor, infrastructure load per visitor).
- Composite sustainability indicators (economic, social, environmental sub-indices).
- Control-lever variables (fee level, tax rate, cap value, promotion intensity for secondary attractions).

### 4.4 Data usage strategy
- Split observed history into a calibration window and a held-out validation window.
- Keep exogenous inputs (external demand trends) separate from endogenous state variables.
- Prepare synthetic/stress scenarios for parameters with no direct observation, to be handled through scenario analysis rather than point estimation.

---

## 5. Candidate Model Framework

Multiple candidate approaches will be considered and compared; the plan does not commit to a single model until comparison and validation.

### 5.1 Candidate model families
1. **System dynamics / stock-and-flow model** — visitor stock, revenue stock, environmental pressure stock, resident-welfare stock, with feedback loops (crowding → satisfaction → demand; fees → demand → revenue → investment).
2. **Optimization model (LP / NLP / multi-objective)** — choose control levels (fees, caps, allocation of revenue) to optimize a weighted objective subject to constraints.
3. **Agent-based / disaggregated simulation** — visitor segments and resident groups as agents, useful for distributional and behavioral effects.
4. **Econometric demand model** — estimate visitor response to price and capacity changes from observed data.
5. **Multi-criteria decision analysis (MCDA)** — structured comparison of policy bundles across economic, social, and environmental criteria.

### 5.2 Proposed composite architecture
- A **demand module** (econometric or behavioral) that maps levers → visitor volume.
- A **cost/benefit module** that maps visitor volume → revenue and → economic, social, environmental costs.
- An **allocation module** that distributes additional revenue across mitigation streams.
- An **evaluation module** that scores outcomes against sustainability objectives.
- A **sensitivity/uncertainty shell** wrapping the whole pipeline.

### 5.3 Key variables (to be finalized)
- *State:* visitor volume by segment, cumulative environmental pressure, resident-welfare index.
- *Control:* fee/tax levels, daily caps, promotion weights for secondary attractions, investment allocations.
- *Exogenous:* external demand trend, macro prices, climate baseline.
- *Outputs:* net economic benefit, environmental impact, resident welfare, sustainability composite.

### 5.4 Advantages and limitations (to be assessed during model selection)
- System dynamics: strong on feedback and policy intuition; weaker on empirical grounding if uncalibrated.
- Optimization: crisp recommendations; risks over-confidence under uncertain parameters.
- Agent-based: rich heterogeneity; heavier to calibrate and validate.
- Econometrics: empirically grounded; may struggle with novel interventions (limited historical variation in caps/fees).
- MCDA: transparent for stakeholders; not predictive by itself.
- Planned resolution: use a hybrid — econometric demand + system-dynamics/optimization core + MCDA for communication — with explicit note of where each component's limits apply.

---

## 6. Implementation Roadmap

> Planning only — no code will be written in this draft.

### 6.1 Phased workflow
1. **Phase 0 — Framing:** finalize boundaries, objectives, indicator definitions, assumption register.
2. **Phase 1 — Data assembly:** collect and preprocess candidate sources; build the data dictionary and provenance log.
3. **Phase 2 — Sub-model prototyping:** prototype demand, cost/benefit, and allocation components independently.
4. **Phase 3 — Integration:** couple components into the composite model; establish baseline (status-quo) scenario.
5. **Phase 4 — Policy experiments:** design lever combinations (fees, caps, promotion, investment) to be evaluated.
6. **Phase 5 — Sensitivity & uncertainty:** run the planned sensitivity protocol (Section 7).
7. **Phase 6 — Generalization:** apply the transfer framework to alternative destinations.
8. **Phase 7 — Communication:** produce the one-page memo structure and any supporting visuals (later deliverable).

### 6.2 Proposed module structure
- `data/` — raw and processed inputs + data dictionary.
- `model/demand/` — demand-response component.
- `model/costbenefit/` — economic, social, environmental accounting.
- `model/allocation/` — revenue allocation logic.
- `evaluation/` — objective/indicator computation.
- `scenarios/` — lever configurations and scenario definitions.
- `sensitivity/` — sensitivity and uncertainty drivers.
- `docs/` — assumption register, provenance log, communication products.

### 6.3 Engineering practices to adopt
- Reproducible configuration-driven runs; parameters externalized, not hard-coded.
- Versioned scenarios and results; every figure traceable to a configuration.
- Automated checks that scenario constraints (budgets, caps) are satisfied.

### 6.4 Risk register (planning risks)
- Data availability/quality gaps → mitigate with scenario treatment and transparent flags.
- Over-fitting to Juneau's unique profile → mitigate with the transfer framework and multi-destination testing.
- Ambiguous objective weighting → mitigate with MCDA and stakeholder-facing ranges rather than single numbers.

---

## 7. Validation Strategy

### 7.1 Evaluation metrics (to be defined and justified)
- **Fit metrics (where history exists):** error measures between modeled and observed visitor volume, revenue, and indicators over the held-out window.
- **Policy metrics:** predicted change in environmental pressure per unit of revenue, resident-welfare trajectory, and stability of the system under each lever.
- **Robustness metrics:** ranking stability of recommended policies across parameter draws and scenario variants.

### 7.2 Validation methods
- **Hold-out / temporal validation:** calibrate on early years, validate on later years.
- **Cross-source consistency:** compare modeled magnitudes against independent reporting where available.
- **Face validity with domain logic:** check that directional responses (e.g., higher fees → lower demand) behave sensibly.
- **Scenario stress tests:** extreme but plausible lever values to test model stability.

### 7.3 Sensitivity analysis plan
- **One-at-a-time (OAT) screening:** vary each parameter across a defensible range; identify influential inputs.
- **Global sensitivity:** plan a variance-decomposition approach (e.g., Sobol-style) to capture interactions among key parameters.
- **Elasticity focus:** give special attention to demand elasticity, activity-based environmental coefficients, and objective weights, as these are expected to dominate.
- **Regime/threshold search:** look for parameter regions where the optimal policy changes qualitatively.

### 7.4 Uncertainty communication
- Report outcomes as ranges/scenarios rather than single point estimates.
- Identify which conclusions are robust (stable across the range) vs. contingent (only valid under narrow conditions).

---

## 8. Expected Result Interpretation

> Descriptions of *how* future results will be read — not actual results.

- **Baseline (status-quo) scenario:** expected to serve as the reference against which all levers are compared; interpretation will focus on whether the unmanaged trajectory trends toward or away from sustainability targets.
- **Single-lever effects:** the model is expected to show that price levers (fees/taxes) primarily affect demand and revenue, while caps directly bound environmental/social pressure but may reduce revenue — interpretation will weigh these trade-offs explicitly.
- **Combined-lever behavior:** interactions are expected to matter (e.g., fees generating revenue that funds mitigation); the reading will emphasize non-additivity and synergy/conflict.
- **Expenditure allocation:** results will be interpreted as marginal sustainability return per dollar across mitigation streams.
- **Sensitivity outcomes:** the key takeaway will be a ranked list of "factors that matter," with an explicit statement of which findings are robust.
- **Generalization results:** interpretation will focus on which mechanisms transfer vs. which must be re-tuned per location, and on the conditions under which promoting secondary attractions meaningfully rebalances load.

All interpretations will be framed as conditional on the stated assumptions and validated ranges.

---

## 9. Limitations and Improvements

### 9.1 Anticipated limitations
- **Data constraints:** sparse or inconsistent historical data on caps/fees limits precise causal estimation.
- **Simplification risk:** aggregating heterogeneous visitors and residents can hide distributional effects.
- **Attribution difficulty:** separating tourism-driven environmental change from natural trends (e.g., glacier retreat) is inherently uncertain.
- **Objective subjectivity:** weighting economic vs. social vs. environmental objectives embeds value judgments.
- **Transferability:** Juneau's cruise-dominated, small-population context may not generalize cleanly.

### 9.2 Planned improvements
- Enrich the model with segment-level detail (visitor types, resident groups) where data permits.
- Move from point estimates to probabilistic/scenario-based outputs as evidence improves.
- Iterate the transfer framework against a portfolio of destinations to test generality.
- Add adaptive/feedback policy logic (measures that respond dynamically to crowding indicators).
- Establish a stakeholder feedback loop so objective weights reflect council priorities.

### 9.3 Open questions to resolve in later phases
- Which objective weighting is defensible and by whom?
- How should "hidden costs" be monetized, if at all?
- What is the appropriate spatial resolution for the redistribution mechanism?
- How much behavioral realism (vs. tractability) is warranted?

---

## Planning Checklist (self-verification for this draft)

- [x] This document is a modeling **blueprint**, not a solution.
- [x] No computed results, no data analysis, no fitted models, no experiments, no plots.
- [x] All nine required sections are present.
- [x] Language is future-oriented ("will", "is expected to", "plan to").
- [x] Assumptions include justification and planned validation routes.
- [x] Data plan, implementation roadmap, and validation/sensitivity strategy are specified.

*End of blueprint draft.*
