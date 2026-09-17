# Light Pollution — Initial Modeling Plan Draft

**Problem ID:** 2023_Light_Pollution (ICM 2023, Problem E)
**Document type:** Modeling blueprint / roadmap (planning only)
**Status:** Initial draft — no analysis, computation, or results are included.
**Note on data:** At the time of drafting, the `data/` directory is empty. The data plan below is therefore framed around data that will be *sourced or assembled* during execution.

---

## 1. Problem Background and Restatement

Light pollution is the excessive or poorly targeted use of artificial light, expressed as light trespass, over-illumination, glare, and light clutter. It degrades night-sky visibility and interacts with ecological, health, and safety systems — affecting plant growth, wildlife migration, human circadian rhythms, and road safety.

COMAP's Illumination Control Mission (ICM) needs a defensible way to **measure** and **mitigate** light pollution. The visible light problem is broad and multi-dimensional; any metric must be able to compare very different location types and must support intervention decision-making under both human and non-human concerns.

**Restatement of required deliverables (to be produced in a later solving phase):**

1. A composite **risk-level metric** for the light pollution of a location.
2. Application/interpretation of that metric across four location archetypes:
   - Protected land
   - Rural community
   - Suburban community
   - Urban community
3. Selection of **two** of these locations and determination of the **most effective intervention strategy** for each, using the metric; discussion of the strategy's effect on the location's risk level.
4. A one-page promotional flyer for the most effective strategy at one chosen location.

**Working scope statement:** *This draft specifies only how the metric, the interventions, and the flyer will be designed, validated, and reported. It produces no values, rankings, or recommendations.*

---

## 2. Objectives and Subproblems

### 2.1 Primary objective
Design a transparent, reproducible, and interpretable framework that (a) scores a location's light pollution risk and (b) supports selection of the intervention strategy that most reduces that risk.

### 2.2 Decomposed subproblems

| ID | Subproblem | Planning intent |
|----|------------|-----------------|
| SP1 | Define the light-pollution risk construct | Decide which dimensions (sky brightness, ecological exposure, human exposure, sensitivity/vulnerability) belong in the metric and why. |
| SP2 | Specify a computable metric | Choose an aggregation form (weighted index, scoring rubric, or multi-criteria aggregation) and define each indicator's direction and scaling. |
| SP3 | Calibrate/parameterize the metric | Plan how weights and thresholds will be set and tested. |
| SP4 | Instantiate the four archetypes | Define representative profiles for protected land, rural, suburban, urban so the metric can be exercised comparatively. |
| SP5 | Model intervention effects | Represent candidate interventions as parameter/indicator changes and predict post-intervention risk. |
| SP6 | Strategy selection for two locations | Define the decision rule that maps post-intervention risk (and cost/side-effect tradeoffs) to a recommended strategy. |
| SP7 | Communicate | Plan the contents and design logic of the one-page flyer. |
| SP8 | Validate and stress-test | Plan internal, external, and sensitivity checks for all of the above. |

### 2.3 Deliverable-to-subproblem mapping
- Metric → SP1–SP3
- Location comparison → SP4
- Two-location strategy selection → SP5–SP6
- Flyer → SP7
- Credibility → SP8

---

## 3. Assumptions

Each assumption is stated with a justification and a planned validation route. All are provisionally adopted for the draft and are subject to revision.

**A1. Locality decomposition.** A location's light pollution risk will be treated as a function of a manageable set of measurable indicators rather than as a single raw radiance value.
- *Justification:* enables comparison across heterogeneous locations and connects to intervention levers.
- *Validation:* check indicator set against literature-recommended dimensions; test indicator redundancy (correlation screening) in the execution phase.

**A2. Archetype representativeness.** Each of the four location types will be represented by a coherent profile (or a small ensemble of profiles) capturing typical development level, population density, biodiversity exposure, geography, and climate.
- *Justification:* the task explicitly asks for interpretation by location type, not for arbitrary single points.
- *Validation:* compare planned profiles against published characteristics of real analogs during execution.

**A3. Additive/composable risk.** The metric will assume that individual indicators can be combined into one score (e.g., normalized weighted sum or geometric mean) with bounded, comparable units.
- *Justification:* yields interpretable, auditable scoring.
- *Validation:* benchmark against alternative aggregation forms; document rank changes.

**A4. Static comparison window.** The metric will describe a point-in-time (or representative-period) risk rather than a fully dynamic time series.
- *Justification:* matches the task's comparative framing and keeps the design tractable.
- *Validation:* discuss temporal sensitivity as a limitation; optionally prototype a coarse seasonal/time-of-night extension.

**A5. Intervention separability.** Each candidate intervention can be modeled as a change in a defined subset of indicators while others are held fixed.
- *Justification:* makes counterfactual comparison well-defined.
- *Validation:* test cross-indicator coupling as a sensitivity scenario.

**A6. Data availability.** Sufficient public/synthetic data will exist to populate indicators for the archetypes; where gaps remain, documented proxy variables or expert-judgment ranges will be used.
- *Justification:* light-pollution data are sparse and unevenly global.
- *Validation:* maintain a data-provenance table and a proxy-justification log.

**A7. Objective neutrality across human/non-human concerns.** Both human and non-human (ecological) dimensions will be represented explicitly rather than collapsed by default.
- *Justification:* the problem statement requires both.
- *Validation:* confirm every metric dimension maps to at least one human or ecological concern.

---

## 4. Data Processing Plan

*(No data have been analyzed. This section specifies intended collection and preparation steps.)*

### 4.1 Candidate data sources to be assembled
- Night-sky brightness / artificial radiance imagery (satellite-derived composites).
- Population density and urbanization/land-use layers.
- Land-protection boundaries and ecological sensitivity proxies (protected-area extents, migratory corridors, biodiversity indicators).
- Human-exposure proxies (population-weighted exposure, road network density) and health/safety proxies (traffic or sleep-risk indicators).
- Geography/climate descriptors (latitude, cloud cover, terrain, seasonal daylight patterns).
- Intervention cost/feasibility parameters (retrofit costs, dimming schedules, shielding effectiveness) from published regulations and standards.

### 4.2 Preprocessing plan
1. **Inventory and provenance:** catalogue every source with resolution, vintage, coverage, license, and known bias.
2. **Alignment:** establish a common spatial framework (grid or administrative unit) and a common temporal window across layers.
3. **Cleaning:** handle missing values, outliers, saturation in radiance products, and unit inconsistencies.
4. **Normalization:** define a direction (benefit vs cost indicator) for every variable and a scaling rule (min–max, percentile, or z-score) for comparability.
5. **Spatial aggregation:** aggregate pixels to the chosen analysis unit so archetypes and interventions share one frame.

### 4.3 Feature/indicator construction plan
- **Sky-brightness indicators:** aggregate radiance statistics (mean, upper percentile) per unit.
- **Ecological-exposure indicators:** radiance intersecting sensitive/protected zones; proximity-weighted exposure.
- **Human-exposure indicators:** population-weighted radiance; area share above a brightness band.
- **Vulnerability/sensitivity modifiers:** biodiversity weight, protected status, seasonal sensitivity.
- **Intervention-related features:** modifiable brightness fraction, shielding/coverage proxies, retrofit readiness.
- Each indicator will be documented with formula sketch, units, range, and rationale (no values computed here).

### 4.4 Data usage strategy
- **Calibration subset:** a set of locations used only to set/refine weights and thresholds.
- **Illustration subset:** the four modeled archetypes used to demonstrate metric behavior.
- **Intervention scenarios:** synthetic-but-grounded perturbations applied to archetype profiles.
- **Hold-out/robustness subset (where feasible):** reserved for testing whether the metric's ordering is stable.

---

## 5. Candidate Model Framework

### 5.1 Metric design (SP1–SP3)

**Candidate A — Weighted composite index (baseline).**
- Form: normalized indicators combined via weighted sum, optionally weighted by a vulnerability modifier.
- Mathematical idea: `Risk = f( Σ w_i · x_i' )` where `x_i'` are scaled indicators and `w_i` are weights.
- Advantages: transparent, easy to interpret, easy to explain in a flyer.
- Limitations: linearity and weight subjectivity; may hide interactions.

**Candidate B — Multi-criteria decision-analysis (MCDA) aggregation.**
- Form: AHP / entropy weighting / TOPSIS-style ranking of units.
- Advantages: structured weight elicitation, handles many criteria.
- Limitations: rank-reversal risk; requires careful pairwise design.

**Candidate C — Tiered/scoring rubric.**
- Form: banded thresholds producing an ordinal risk class (e.g., low→severe) plus a numeric sub-score.
- Advantages: highly interpretable; robust to noisy inputs.
- Limitations: threshold placement sensitivity; coarser resolution.

**Candidate D — Hybrid composite + rubric.**
- Form: continuous composite for ranking, banded rubric for communication.
- Advantages: combines analytic sensitivity with communication clarity.
- Limitations: two outputs to reconcile.

*Planned direction for execution:* prototype A and C, use B for weight cross-checking, and adopt D if reconciliation is clean. Final choice deferred to the solving phase.

### 5.2 Variables (conceptual)
- **Inputs:** radiance, population density, protection/land-use class, biodiversity proxy, climate/geography descriptors, road/transport proxies.
- **Intermediate:** normalized indicators and weight vectors.
- **Outputs:** risk score (continuous), risk class (ordinal), and dimension sub-scores (sky / ecological / human).
- **Decision variables (interventions):** dimming level, shielding/coverage, spectral shift (warm-white), curfew schedules, smart adaptive control, zoning/ordinance strength, retrofits.

### 5.3 Intervention modeling (SP5–SP6)
- Represent each intervention as a multiplier/modifier on the affected brightness or coverage indicators.
- Encode cost/feasibility as a constraint or penalty in the selection rule.
- Define decision rule candidates: (i) maximize risk reduction subject to budget; (ii) maximize risk-reduction-per-cost; (iii) lexicographic (must meet ecological floor, then minimize risk). Final rule deferred to execution.

---

## 6. Implementation Roadmap

*(No code will be written or run in this planning phase; the steps below define the intended build order.)*

1. **Design specification:** finalize metric definition, indicator formulas, weights approach, and decision rule (SP1–SP6).
2. **Data pipeline module:** ingestion → alignment → cleaning → normalization → aggregation, with a provenance log.
3. **Metric module:** scoring engine producing continuous score, class, and sub-scores.
4. **Archetype module:** population of the four location profiles.
5. **Intervention module:** scenario perturbations and post-intervention scoring.
6. **Decision module:** strategy selection under the chosen rule.
7. **Reporting/visual module:** comparative charts/tables (for later use) and the one-page flyer.
8. **Validation module:** sensitivity sweeps, alternative-weight runs, robustness checks.

### 6.1 Planned modules / artifacts
- `data/` — raw and processed layers + provenance table.
- `code/` — pipeline, metric, intervention, decision, validation scripts.
- `logs/` — run records and configuration snapshots.
- `results/` — this plan plus future outputs (tables, figures, flyer).
- Configuration file capturing weights, thresholds, and scenario definitions for reproducibility.

### 6.2 Draft workflow
Problem framing → indicator set → data assembly → normalization → metric build → archetype instantiation → intervention scenarios → strategy selection → sensitivity testing → flyer design → report assembly (≤25 pages).

---

## 7. Validation Strategy

### 7.1 Evaluation concepts (to be quantified later)
- **Internal consistency:** do sub-scores agree with the composite in expected directions?
- **Discriminative power:** does the metric separate the four archetypes meaningfully?
- **Stability:** how much do rankings move under alternative weights/aggregations?
- **Plausibility:** do results align with qualitative expectations for known location types?
- **Sensitivity:** which inputs dominate the score?

### 7.2 Validation methods
- **Weight sensitivity:** systematic sweeps and rank-correlation checks across weight scenarios.
- **Aggregation robustness:** compare weighted sum vs geometric mean vs MCDA.
- **Scenario stress tests:** extreme intervention cases and coupled-indicator cases.
- **Proxy substitution tests:** swap proxy variables and re-check ordering.
- **Cross-method triangulation:** verify that the composite and the ordinal rubric tell a consistent story.
- **Face validation:** qualitative review against domain literature and ICM criteria.

### 7.3 Reporting of uncertainty
- Plan to report result ranges, not single points, where inputs are uncertain.
- Document every assumption that materially affects ordering.

---

## 8. Expected Result Interpretation

*(Described only as the shape of anticipated outputs; no values.)*

- A metric that yields a **continuous risk score**, a **discrete risk class**, and **dimension sub-scores** (sky, ecological, human).
- A comparative view showing the metric ordering the four archetypes along a plausible gradient (protected → rural → suburban → urban), to be confirmed—not assumed—during execution.
- For each of the two chosen locations, a **before/after risk profile** under the recommended intervention, plus a discussion of which indicators drove the change and any tradeoffs (e.g., safety vs ecology, cost vs benefit).
- A **one-page flyer** translating the recommended strategy into audience-friendly language: the problem, the strategy, expected benefit, and an actionable call to action, using only verified solving-phase results.
- Interpretation guidance emphasizing that scores are **relative and context-dependent**, dependent on weight/threshold choices, and intended to support—not replace—local judgment.

---

## 9. Limitations and Improvements

### 9.1 Anticipated limitations
- **Data sparsity and bias:** uneven global coverage; satellite saturation in bright cores; proxies for ecological sensitivity.
- **Weight subjectivity:** composite weighting can embed value judgments.
- **Static snapshot:** limited representation of dynamics (seasonality, time-of-night, growth).
- **Intervention abstraction:** real-world effectiveness depends on enforcement and behavior, which may not be fully modeled.
- **Scale mismatch:** combining pixel-level and community-level data can introduce aggregation error.

### 9.2 Planned improvements
- Multi-scenario weighting with explicit uncertainty bands.
- Dynamic/seasonal extension (time-of-night and seasonal profiles).
- Cost-effectiveness and equity dimensions added to the decision rule.
- Validation against additional real-world locations if data permit.
- Replacement of proxy variables with direct measurements as better data are sourced.
- Clearer separation of measurement error vs model-structure uncertainty in reporting.

---

## Planning Checklist (self-verification before submission)

- [x] `draft.md` authored at the required path.
- [x] Contains only planning content (workflow, assumptions, methods, data plan, implementation, validation).
- [x] No calculations, no fitted models, no executed experiments, no final results or conclusions.
- [x] Future-oriented language used throughout.
- [x] All nine required sections present.
