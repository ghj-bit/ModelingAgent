# Modeling Blueprint Draft — Sustainable Cities Needed! (ICM 2017, Problem E)

> **Status:** Planning draft only. This document is a modeling roadmap. It contains **no computed results, no data analysis, no fitted models, and no final conclusions.** All statements are future-oriented (what *will* be built, measured, or validated).

---

## 1. Problem Background and Restatement

**Context.** Communities worldwide are adopting *smart growth* initiatives to pursue long-term, sustainable urban planning. Smart growth seeks to balance the three E's of sustainability — **economic prosperity, social equity, and environmental sustainability** — and is codified in ten principles (mixed land use, compact design, diverse housing, walkable neighborhoods, sense of place, open-space preservation, infill development, diverse transportation, predictable/fair/cost-effective decisions, and stakeholder collaboration). With global urbanization projected to push ~66% of the population into cities by 2050 (an additional ~2.5 billion urban residents), the way mid-sized cities plan growth will materially shape global sustainability outcomes.

**Restated task.** The International City Management Group (ICM) requests a transferable methodology for applying smart growth theory to city design worldwide. The problem asks the modeling team to:

- **(Task 1)** Define a metric that measures smart growth success, grounded in the three E's and/or the 10 smart growth principles.
- **(Task 2)** Research and evaluate the *current growth plans* of two selected mid-sized cities (population 100,000–500,000) on **different continents**, using the defined metric.
- **(Task 3)** Develop a smart growth plan for both cities for the coming decades, justified by geography, growth rates, and economic opportunities, and evaluate plan success with the metric.
- **(Task 4)** Rank the initiatives within the plan from most to least potential by the metric; compare and contrast initiative rankings across the two cities.
- **(Task 5)** Explain how the plan supports a **50% population increase by 2050**.

**Deliverable of this draft.** A coherent modeling blueprint: objectives, subproblems, assumptions, data plan, candidate model framework, implementation roadmap, validation strategy, interpretability expectations, and limitations. The blueprint is the handoff artifact for a future modeling/solving phase.

**Key design tension to be addressed (not resolved here).** The metric must be simultaneously (a) *general* enough to compare cities across continents and (b) *sensitive* enough to rank individual initiatives within a single city. The blueprint therefore anticipates a **two-level metric architecture** (composite macro-index + initiative-level scoring) rather than a single scalar.

---

## 2. Objectives and Subproblems

### 2.1 Primary Objective
Produce a defensible, reproducible, and transferable methodology that (i) quantifies smart growth success, (ii) audits existing city growth plans, (iii) generates and evaluates forward-looking smart growth plans for two mid-sized cities on different continents, (iv) ranks and compares initiatives, and (v) demonstrates scalability to a 50% population increase by 2050.

### 2.2 Subproblem Decomposition

| # | Subproblem | Central Question | Maps to Task |
|---|------------|------------------|--------------|
| SP1 | Metric design | How should smart growth success be operationalized into measurable indicators and aggregated? | Task 1 |
| SP2 | City selection & profiling | Which two continent-distinct mid-sized cities should be chosen, and how should their baseline conditions be characterized? | Task 1–2 |
| SP3 | Baseline evaluation | How do the cities' current growth plans score against the metric? | Task 2 |
| SP4 | Plan generation | What initiative portfolios should be proposed for each city, conditioned on geography, growth rate, and economic opportunity? | Task 3 |
| SP5 | Plan evaluation | How do the proposed portfolios perform under the metric and under growth scenarios? | Task 3 |
| SP6 | Initiative ranking & cross-city contrast | What is the initiative ordering within each city, and why do rankings differ? | Task 4 |
| SP7 | Scalability demonstration | How do the plans accommodate a 50% population increase by 2050? | Task 5 |
| SP8 | Uncertainty & sensitivity | How robust are scores and rankings to weights, data gaps, and scenario assumptions? | Cross-cutting |

### 2.3 Deliverable Set (future outputs)
- A defined, documented smart growth metric with indicator taxonomy and aggregation rule.
- A city selection justification and comparable baseline profiles.
- Baseline scorecards for both cities.
- Two forward-looking initiative portfolios with justification logic.
- Ranked initiative lists per city plus a comparative analysis.
- Capacity/scalability narrative for +50% population by 2050.
- Sensitivity and robustness appendix.

---

## 3. Assumptions

Assumptions are grouped by type and each is paired with a **future validation approach** (validation is not performed in this draft).

### 3.1 Scope & Selection Assumptions
- **A1.** "Mid-sized" will be interpreted as population 100,000–500,000 at the reference baseline year (consistent with the prompt).
- **A2.** Two cities will be selected on **different continents**, chosen to maximize contrast in development stage and geography (e.g., one rapidly growing emerging-economy city and one slower-growing mature city) while remaining comparable in size.
- **A3.** "Coming decades" will be interpreted as the horizon **2025 → 2050**, with 2050 as the explicit target year for the +50% population scenario.
- *Validation:* Selection criteria will be documented and stress-tested via a **reproducible selection rubric** (population, growth rate, data availability, continental distinctness); a shortlist will be re-scored to confirm the final pair is not arbitrary.

### 3.2 Metric & Measurement Assumptions
- **A4.** Smart growth success can be **approximated by a finite, weighted, hierarchical indicator set** derived from the three E's and the 10 principles.
- **A5.** Indicators will be comparable across cities via **normalization** (min–max or z-score against a reference band) rather than raw units.
- **A6.** Where direct measurements are unavailable, **proxy indicators** (documented and flagged) will be acceptable.
- *Validation:* The indicator taxonomy will be checked for **construct coverage** (does every principle map to ≥1 indicator?), **redundancy** (correlation screening), and **face validity** against authoritative sources (Smart Growth America, EPA, UN WUP).

### 3.3 Growth & Dynamics Assumptions
- **A7.** City population and economic activity will follow a **smooth, monotone growth trajectory** over the horizon absent major shocks (with scenario branches for high/low growth).
- **A8.** Land, housing, and transportation capacity can be represented as **aggregate stocks and flows** (not parcel-level micro-simulation) at the planning stage.
- **A9.** The +50% population increase is applied **uniformly as a planning target** for both cities, enabling cross-city comparability.
- *Validation:* Growth assumptions will be **triangulated** against published urban projections (UN WUP) and national statistical trajectories; scenario spread will be reported rather than a single point forecast.

### 3.4 Modeling & Behavioral Assumptions
- **A10.** Composite weighting reflects **stakeholder policy priorities** and will be treated as an explicit input (not a hidden choice).
- **A11.** Initial conditions and policy levers are **separable enough** to attribute score changes to initiatives (for ranking purposes).
- **A12.** Rankings will be interpreted as **relative potential**, not guaranteed outcomes.
- *Validation:* Weighting and attribution assumptions will be tested via **sensitivity analysis** (Section 7).

### 3.5 Data & Provenance Assumptions
- **A13.** Public, citable sources (city master plans, national statistics offices, World Bank, UN, OECD, OpenStreetMap, satellite/land-cover products) will supply the input evidence base.
- **A14.** Cross-source inconsistencies will be **reconciled by documented rules** (year alignment, unit conversion, definition harmonization).
- *Validation:* A **data provenance log** and **gap register** will accompany the model; triangulation across ≥2 sources per key indicator where feasible.

---

## 4. Data Processing Plan

> No data is analyzed here; the workspace `data/` directory currently contains no supplied files. The plan below describes how data **will** be sourced, structured, cleaned, and used.

### 4.1 Data Sources (planned categories)
1. **Problem-provided statements** (`2017_ICM_Problem_E.pdf`) — objective, principles, tasks.
2. **Official city plans** — comprehensive/master plans, zoning, housing, transport strategy documents for both cities.
3. **National/regional statistics** — census, population projections, employment, GDP, housing, transport modal split.
4. **International comparators** — UN World Urbanization Prospects; World Bank / OECD urban indicators.
5. **Geo-spatial layers** — administrative boundaries, land cover, road/transit networks, green-space extents.
6. **Methodological references** — Smart Growth America, EPA Smart Growth publications, The Smart Growth Manual.

### 4.2 Indicator / Feature Construction (planned)
- **Principle → indicator mapping table:** each of the 10 principles mapped to 1–3 measurable indicators; each indicator tagged to an E (economic / equity / environment).
- **Normalization layer:** min–max or z-score scaling to a common [0,1] band, with directionality flags (benefit vs. cost indicators).
- **Composite construction:** hierarchical aggregation (indicators → sub-scores → E-dimension scores → overall index).
- **Initiative feature vector:** each candidate initiative encoded as a vector of expected impacts on the indicator set (expert-anchored, documented).

### 4.3 Preprocessing Steps (planned)
1. Ingest and catalog raw documents/datasets into a structured manifest.
2. Align **reference years** and geographic boundaries across sources.
3. Convert units and harmonize definitions (e.g., density measures, transit access definitions).
4. Handle missing values via documented imputation or proxy substitution; log every decision.
5. Screen for **outliers and inconsistencies**; flag rather than silently drop.
6. Version and freeze the cleaned dataset before modeling (reproducibility).

### 4.4 Data Usage Strategy
- **Baseline profile** (SP2/SP3) uses current-year indicators.
- **Projection inputs** (SP4/SP5/SP7) use growth-rate and economic-opportunity parameters.
- **Ranking inputs** (SP6) use initiative impact vectors + policy weights.
- **Held-out/reference bands** reserved for sanity-checking composite behavior.
- All derived features will carry **provenance tags** for auditability.

---

## 5. Candidate Model Framework

The framework is deliberately **multi-model**: a metric core, an evaluation layer, a projection layer, and a decision-ranking layer. Candidate methods are listed with advantages and limitations.

### 5.1 Layer A — Metric / Composite Index (SP1)
- **Candidate A1: Weighted additive composite index** (normalized indicators × weights).
  *Pros:* transparent, explainable, easy to communicate. *Cons:* fully compensatory (weak performance can be masked).
- **Candidate A2: Weighted geometric mean / multiplicative composite.**
  *Pros:* penalizes severe single-dimension weakness (non-compensatory). *Cons:* sensitive to zero/near-zero indicators; less intuitive.
- **Candidate A3: AHP / Delphi-weighted hierarchy.**
  *Pros:* structured stakeholder-derived weights; handles qualitative principles. *Cons:* subjectivity; consistency-ratio discipline required.
- **Candidate A4: Entropy-weight / data-driven weighting.**
  *Pros:* reduces analyst bias. *Cons:* weights become data-dependent and less policy-meaningful; fragile with small samples.
- *Lean (to be confirmed):* **Hierarchical AHP-weighted composite with a geometric mean at the E-dimension level**, giving both transparency and non-compensation across the three E's.

**Variables (indicative):** density/intensity metrics, land-use mix index, housing diversity/affordability ratios, walkability/transit-access scores, open-space/green-area share, infill-vs-sprawl ratio, fiscal/economic indicators, equity distribution measures. Each with a defined direction and normalization.

### 5.2 Layer B — Baseline Evaluation (SP2–SP3)
- **Scoring rubric** applied to documented current plans → baseline scorecard per city.
- **Gap analysis** vs. a target/reference profile to highlight principle-level shortfalls.
- *Candidate supporting method:* **SWOT-style qualitative coding** aligned to the metric to capture plan intent not visible in numbers.

### 5.3 Layer C — Forward Planning & Projection (SP4–SP5, SP7)
- **Candidate C1: Scenario-based projection** (low/base/high growth) with initiative-conditioned indicator trajectories. *Pros:* simple, interpretable. *Cons:* not endogenously dynamic.
- **Candidate C2: System-dynamics-inspired stock–flow model** (population, housing stock, land, transport capacity). *Pros:* captures feedback and capacity constraints. *Cons:* parameter-heavy; calibration risk.
- **Candidate C3: Linear / goal programming** to select initiative bundles meeting capacity and budget constraints while maximizing the composite. *Pros:* optimization-native, links directly to metric. *Cons:* assumes linearity/additivity.
- **Candidate C4: Multi-criteria decision analysis (MCDA)** for structured comparison of portfolios. *Pros:* handles qualitative criteria. *Cons:* depends on weight choices.
- *Lean (to be confirmed):* **C1 (scenario projection) + C3 (goal programming) hybrid**, so the plan is both explainable and optimized under explicit constraints.

### 5.4 Layer D — Initiative Ranking & Comparison (SP6)
- **Candidate D1: Metric-delta ranking** — rank initiatives by marginal contribution to the composite under constraints.
- **Candidate D2: TOPSIS / PROMETHEE ranking.**
  *Pros:* handles multi-criteria ranking with minimal assumptions; PROMETHEE exposes preference structure. *Cons:* rank reversals under weight changes.
- **Candidate D3: Sensitivity-weighted ranking** — principal rank + stability band across weight perturbations.
- *Lean (to be confirmed):* **D1 for primary ranking + D3 for stability bands**, with D2 as a cross-check.

### 5.5 Cross-Layer Interactions (planned)
- Metric (A) defines the objective function for optimization (C) and the ranking criterion (D).
- Projections (C) feed initiative impacts back into metric (A) for evaluation (SP5).
- Rankings (D) are reported against both cities to produce the Task 4 contrast.

---

## 6. Implementation Roadmap

> Implementation is **planned**, not executed. No code is written in this draft.

### 6.1 Module Breakdown (planned)
1. **`config/`** — metric weights, scenario parameters, city-selection criteria, horizon definitions.
2. **`data_ingest/`** — document/data loaders + provenance manifest.
3. **`cleaning/`** — normalization, alignment, imputation, QC logging.
4. **`features/`** — indicator construction and principle→indicator mapping.
5. **`metric_core/`** — composite index computation (Layer A).
6. **`evaluation/`** — baseline scoring and gap analysis (Layer B).
7. **`projection/`** — scenario and stock–flow projection engine (Layer C).
8. **`optimization/`** — goal-programming initiative selection (Layer C3).
9. **`ranking/`** — initiative ranking and stability analysis (Layer D).
10. **`validation/`** — sensitivity, robustness, and triangulation routines.
11. **`reporting/`** — scorecards, ranked tables, and narrative generators.

### 6.2 Suggested Work Sequence (phased)
- **Phase 0 — Scoping & selection:** finalize city pair and metric taxonomy.
- **Phase 1 — Data assembly:** build the evidence base and provenance log.
- **Phase 2 — Metric implementation:** implement and unit-test the composite index.
- **Phase 3 — Baseline audit:** score current plans; produce gap analyses.
- **Phase 4 — Plan generation:** build scenario/projection and optimization layers.
- **Phase 5 — Plan evaluation:** score portfolios; iterate on constraints.
- **Phase 6 — Ranking & contrast:** rank initiatives; compare cities.
- **Phase 7 — Scalability:** stress the plans against +50% population by 2050.
- **Phase 8 — Validation & write-up:** sensitivity, robustness, limitations, reporting.

### 6.3 Required Tooling (planned)
- Data handling & geospatial processing; numerical/optimization libraries; MCDA utilities; a reproducible pipeline (seeded, versioned, scripted); logging aligned to the `logs/` directory convention.

### 6.4 Reproducibility Requirements (planned)
- Deterministic runs via fixed seeds and pinned versions.
- Config-driven parameters (no hard-coded weights).
- Every figure/table regenerable from raw inputs + config.

---

## 7. Validation Strategy

### 7.1 Evaluation Metrics (planned)
- **Internal consistency:** composite-index coherence, weight-vector validity (AHP consistency ratio where applicable).
- **Rank stability:** rank-correlation (e.g., Spearman) of initiative orderings across weight/scenario perturbations.
- **Scenario robustness:** spread of composite scores across low/base/high growth.
- **Cross-city plausibility:** sanity checks that scores align with qualitative expert expectations.
- **Scalability check:** whether the +50% scenario remains feasible under stated capacity constraints.

### 7.2 Validation Methods (planned)
- **Sensitivity analysis:** one-at-a-time and multi-way perturbation of weights and key assumptions; report rank-reversal thresholds.
- **Triangulation:** cross-check key indicators against ≥2 independent sources.
- **Expert/face validation:** map results back to the 10 principles and three E's for interpretability.
- **Back-testing (where historical data permits):** does the metric's logic reproduce known directionality of past plan outcomes?
- **Boundary/edge-case testing:** extreme growth and extreme budget constraints.

### 7.3 Robustness & Uncertainty Handling (planned)
- Monte-Carlo propagation of input uncertainty into composite scores and rankings (where distributions can be justified).
- Explicit **stability bands** around rankings rather than single-point orders.
- Reporting of **data gaps** and their modeled impact, not silent imputation.

---

## 8. Expected Result Interpretation

> Interpretive *framework* only — no actual results are produced in this draft.

- **Metric (Task 1):** the composite index is expected to yield an interpretable 0–1 (or 0–100) success score per city, decomposable into the three E's and down to principle-level sub-scores, allowing both diagnosis and comparison.
- **Baseline audit (Task 2):** current plans are expected to score unevenly — strong on some principles, weak on others — with the gap analysis indicating which principles are under-served.
- **Forward plans (Task 3):** proposed portfolios are expected to improve the composite relative to baseline within the constraints, with the magnitude of improvement serving as the plan's justification.
- **Ranking & contrast (Task 4):** initiatives are expected to order differently between the two cities due to distinct geography, growth rate, and economic structure; the contrast is expected to reveal **which initiative types are context-dependent vs. universally high-value**.
- **Scalability (Task 5):** the plans are expected to be evaluated against capacity constraints to argue whether +50% growth by 2050 is feasible and under what policy conditions.

Interpretation will emphasize **relative comparison and policy insight**, not absolute prediction.

---

## 9. Limitations and Improvements

### 9.1 Anticipated Limitations
- **Subjectivity in weighting** — composite scores and rankings depend on policy weights.
- **Data availability asymmetry** — the two cities may differ in data richness, biasing comparability.
- **Proxy reliance** — some principles (e.g., "sense of place," "stakeholder collaboration") are hard to quantify and will rely on proxies.
- **Aggregation trade-offs** — compensatory vs. non-compensatory choice affects outcomes.
- **Projection uncertainty** — long-horizon (to 2050) forecasts are inherently uncertain.
- **Attribution difficulty** — isolating individual initiative contributions assumes approximate separability.
- **Aggregate granularity** — stock–flow stylization omits parcel-level and behavioral complexity.

### 9.2 Planned Improvements (future work)
- Move from MCDA to **integrated dynamic simulation** (system dynamics / agent-based) as data and time permit.
- Incorporate **spatially explicit land-use modeling** for finer initiative ranking.
- Adopt **participatory weighting** (stakeholder workshops) to strengthen AHP/Delphi legitimacy.
- Build **transfer templates** so the methodology generalizes beyond the two selected cities.
- Extend validation with **longitudinal back-testing** as historical data accrues.
- Add **uncertainty quantification** as a first-class output (distributions, not point scores).

---

*End of modeling blueprint draft. This document intentionally contains no computations, no data analysis, no fitted models, and no final results.*
