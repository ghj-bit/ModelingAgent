# Modeling Blueprint Draft — The Need for Bees (and not just for honey)

**Problem ID:** `2022_The_Need_for`
**Source:** HiMCM 2022, Problem A
**Document type:** Initial modeling plan draft (roadmap only — no solution, no computed results)
**Status:** Draft for review — all content is future-oriented and intended to guide subsequent modeling work.

---

## 1. Problem Background and Restatement

Honeybees play a central role in pollination and agricultural productivity, yet their populations are under pressure from a cluster of stressors collectively associated with Colony Collapse Disorder (CCD). The problem asks the modeling team to reason about how a honeybee colony behaves over time, which biological and management factors dominate that behavior, and how many hives would be required to pollinate a specified parcel of cropland.

The statement provides a set of anchor facts that will serve as the backbone of the eventual model:

- Honeybees may travel up to **20 km**, but typically remain within **6 km** of the hive.
- A typical hive holds **20,000–80,000** bees.
- A single bee may visit roughly **2,000 or more flowers per day**.
- Lifespan is seasonally variable — short in summer under high workload, potentially **4–6 months** in autumn and winter.
- Lifespan is influenced by activity level, pollen consumption, and protein abundance.

**Restatement of the deliverable as a modeling problem.** The work is framed as three coupled modeling subproblems plus a communication artifact:

1. A **dynamic colony-population model** describing how colony size evolves over time under seasonality, brood and mortality dynamics, and environmental stress.
2. A **sensitivity analysis** ranking which parameters (lifespans, egg-laying rates, resource availability, stress factors) most influence colony size.
3. A **hive-count / pollination-demand model** estimating the number of hives needed to service a 20-acre (81,000 m²) crop area.
4. A **non-technical one-page blog or infographic** communicating the findings to a lay audience.

This draft addresses *how* those subproblems will be modeled. It does **not** attempt any of them.

---

## 2. Objectives and Subproblems

### 2.1 Overall objective
To design a coherent, defensible modeling pipeline that will (in a later, separate stage) produce a colony-population model, a sensitivity ranking of influential factors, a hive-count estimate for a given crop area, and a public-facing summary.

### 2.2 Subproblem breakdown (planning view)

| # | Subproblem | Planning question | Intended deliverable |
|---|-----------|-------------------|----------------------|
| SP1 | Colony dynamics | Which model class best represents colony size, stage structure, and seasonality? | Specification of state variables, flows, and parameter semantics |
| SP2 | Sensitivity | Which parameters and structual choices are expected to dominate colony size, and how should influence be measured? | Sensitivity design (method, factors, ranges, target outputs) |
| SP3 | Pollination / hive count | How should flower-visit capacity, forage area, and crop demand be related to hive count? | Accounting framework linking bee-hours, flowers, and area |
| SP4 | Communication | What must the one-page artifact convey and to whom? | Content outline and message plan (not the artifact itself) |

### 2.3 Deliverables to be produced later
- A documented model specification and (eventually) its implementation.
- A sensitivity report with ranked factor influence.
- A hive-count recommendation framework for a 20-acre plot.
- A one-page non-technical summary.

### 2.4 Scope boundaries for this draft
- No equations will be numerically evaluated.
- No datasets will be analyzed.
- No model will be calibrated or fitted.
- No numeric hive counts or population values will be produced.

---

## 3. Assumptions

Assumptions are grouped by category. Each is paired with a justification and a planned validation approach (to be executed in a later stage).

### 3.1 Biological / colony assumptions
1. **A colony is treated as a single super-organism with stage structure (egg → larva → pupa → adult), rather than modeling individual bees.** 
   *Justification:* colony-level behavior is the quantity of interest; individual-based detail is unnecessary for the stated tasks.
   *Validation:* compare aggregate predictions against published colony-growth curves.
2. **Colony size is bounded by a carrying capacity driven by hive space and forage availability.**
   *Justification:* the stated 20,000–80,000 range implies soft upper bounds.
   *Validation:* test sensitivity to the chosen cap; verify predictions stay within plausible bounds.
3. **Queen egg-laying rate is the dominant birth control and is seasonal.**
   *Justification:* the problem explicitly names egg-laying rate as a sensitivity candidate.
   *Validation:* perturb within literature ranges and observe output stability.
4. **Worker lifespan is seasonally dependent (short summer, long autumn/winter).**
   *Justification:* stated explicitly in the problem.
   *Validation:* seasonal scenarios cross-checked against qualitative expectations.
5. **Mortality is driven by a combination of age, workload, resource scarcity, and external stressors (disease, pesticides, predators).**
   *Justification:* these mirror the CCD factors named in the statement.
   *Validation:* decompose mortality into components and test each effect independently.

### 3.2 Environmental / spatial assumptions
6. **Foraging occurs symmetrically within a radius around the hive, with a decay of visit density with distance.**
   *Justification:* the 6 km typical / 20 km maximum travel facts imply a distance-decayed forage footprint.
   *Validation:* compare uniform-disc vs. decayed-kernel footprints and test hive-count sensitivity.
7. **The 20-acre crop area is treated as a homogeneous parcel unless the later stage introduces sub-zones or crop mixes.**
   *Justification:* simplification consistent with the task statement.
   *Validation:* re-run with heterogeneous zoning and compare hive-count ranges.

### 3.3 Modeling / methodological assumptions
8. **Continuous-time deterministic dynamics are the baseline, with stochasticity considered as an extension.**
   *Justification:* deterministic ODEs give clear structural insight; stochastic variants test robustness.
   *Validation:* Monte-Carlo extension as a planned robustness check.
9. **Parameters drawn from literature and problem-stated ranges will be treated as uncertain and reported as ranges, not point values.**
   *Justification:* direct calibration data are not supplied.
   *Validation:* uncertainty propagation via sensitivity/interval analysis.
10. **Pollination demand is proportional to flower density and crop area.**
    *Justification:* needed to translate flower visits into area coverage.
    *Validation:* vary flower density and observe hive-count response.

### 3.4 Communication assumptions
11. **The target audience for the one-page artifact is a non-specialist stakeholder (farmer, policymaker, or general public).**
    *Justification:* the problem calls for a non-technical summary.
    *Validation:* readability/accessibility review as a later step.

---

## 4. Data Processing Plan

*Note: no data will be processed at this stage. The following is the plan for the later modeling stage.*

### 4.1 Data sources to be assembled
- **Problem-stated anchors** (travel range, hive population bounds, flower-visit rate, lifespan ranges) — treated as hard reference values.
- **Published apiculture/entomology references** for egg-laying rates, brood development times, seasonal mortality, and colony growth curves.
- **Forage/flower-density values** for representative crops, to be sourced or assumed with documented ranges.
- **Optional external datasets** (regional climate or crop calendars) if a location-specific scenario is later required.

### 4.2 Preprocessing plan
- Normalize units (distance in km, area in m² and acres, rates in per-day time base).
- Convert all seasonal drivers to a common time index (e.g., day-of-year or month).
- Encode parameter uncertainty as explicit ranges (lower/typical/upper) rather than single values.
- Document provenance and units for every parameter in a central parameter table.

### 4.3 Feature/parameter construction
- **State variables:** egg/larva/pupa counts, adult worker counts, forager counts, stored resources (as the later stage decides).
- **Drivers:** temperature/season profile, forage availability, egg-laying rate, stage-specific mortality, workload.
- **Derived quantities:** effective foraging radius, flowers-visitable per day per hive, crop-area coverage capacity.
- **Stress indicators:** composite index aggregating CCD-relevant stressors.

### 4.4 Data usage strategy
- Split parameters into **pinned** (from the problem statement) and **explored** (ranges to be swept).
- Reserve a subset of literature/expected patterns as qualitative **acceptance targets** for structural validation.
- Keep an explicit **assumption log** so every substituted value is traceable.

---

## 5. Candidate Model Framework

### 5.1 Candidate models (to be compared and selected in the later stage)

**M1 — Stage-structured compartmental (ODE) colony model.**
- Represent egg → larva → pupa → adult stages with transition and mortality rates.
- Add seasonality by making egg-laying and mortality time-dependent.
- *Advantages:* transparent structure, easy sensitivity analysis, biologically interpretable.
- *Limitations:* ignores individual heterogeneity and random events.

**M2 — Delay-differential / age-structured (McKendrick–von Foerster style) model.**
- Captures developmental delays (maturation lags) more faithfully.
- *Advantages:* better timing realism for brood pulses.
- *Limitations:* more complex to specify and analyze; parameter-hungry.

**M3 — Logistic / single-variable population model with seasonal forcing.**
- Simplest baseline for colony size with a carrying capacity.
- *Advantages:* minimal parameters, useful as a benchmark.
- *Limitations:* cannot express stage structure or stress decomposition well.

**M4 — Stochastic / individual-based (or agent-based) extension.**
- Introduces randomness in laying, mortality, and foraging; enables variance analysis and extinction-risk framing.
- *Advantages:* realism and uncertainty quantification.
- *Limitations:* computational cost, calibration difficulty.

**M5 — Pollination accounting / forage-demand model (for SP3).**
- Link hive foraging capacity (bees × visits/day × effective radius) to flower demand of the crop area.
- *Advantages:* directly addresses the hive-count question; can reuse SP1 outputs.
- *Limitations:* highly sensitive to assumed flower density and foraging efficiency.

### 5.2 Key variables (to be finalized later)
- Colony: total adults, foragers, brood counts per stage.
- Rates: egg-laying, maturation, stage-specific mortality, resource intake.
- Environment: seasonal driver, forage availability, stressor intensity.
- Spatial: effective radius, covered area, flower density, crop area (20 acres / 81,000 m²).

### 5.3 Mathematical ideas to be considered
- Mass-balance / conservation of individuals across stages.
- Seasonally forced coefficient functions (e.g., periodic egg-laying and mortality).
- Sensitivity machinery: one-at-a-time sweeps, variance-based (e.g., Sobol-style) global sensitivity.
- Distance-decayed foraging kernel for the spatial/forage component.
- Dimensional and unit-consistency checks to tie bee-visit capacity to land area.

### 5.4 Advantages and limitations summary
The framework intentionally moves from a simple benchmark (M3) to structured (M1/M2) and finally stochastic/agent-based (M4) descriptions, with a separate accounting layer (M5) for the hive-count question. This layered plan allows the later stage to justify its choice of model class on grounds of interpretability, sensitivity needs, and communication goals.

---

## 6. Implementation Roadmap

### 6.1 Planned workflow
1. **Finalize assumptions and parameter table** (with documented sources/ranges).
2. **Implement the baseline model (M3 or M1)** for colony dynamics.
3. **Extend to stage structure / delays (M1/M2)** and validate against qualitative patterns.
4. **Run sensitivity analysis (SP2)** on the selected model.
5. **Implement the pollination accounting layer (M5)** using colony outputs.
6. **Produce the hive-count framework** for the 20-acre area (SP3).
7. **Compile the one-page communication artifact (SP4).**
8. **Consolidate results into the final ≤25-page solution.**

### 6.2 Required modules (planned)
- `params` — parameter definitions, units, and uncertainty ranges.
- `colony_model` — state variables, flow equations, seasonal drivers.
- `sensitivity` — factor sweeps and influence ranking.
- `pollination` — flower/visit/area accounting and hive-count derivation.
- `scenarios` — seasonal and stressor scenario definitions.
- `viz` — plotting utilities for internal inspection (later stage only).
- `reporting` — assembly of tables/figures for the written solution.

### 6.3 Algorithms to be used (later stage)
- Numerical integration of ODEs / DDEs (e.g., Runge–Kutta family).
- Parameter sweep grids plus variance-based global sensitivity.
- Monte-Carlo sampling for stochastic robustness checks.
- Unit/consistency checks between foraging capacity and land area.

### 6.4 Engineering practices
- Version-control the code and keep the parameter table as a single source of truth.
- Reproducible runs with fixed seeds for any stochastic component.
- Log assumptions and deviations in a persistent decision log.

---

## 7. Validation Strategy

### 7.1 Evaluation metrics (planned)
- **Biological plausibility:** predicted colony sizes remain within the stated 20,000–80,000 range under nominal conditions.
- **Qualitative pattern match:** seasonal rise/fall of colony size matches expected colony phenology.
- **Consistency:** foraging throughput × effective area is dimensionally and quantitatively coherent with the crop-area demand.
- **Robustness:** conclusions (e.g., hive-count ranges) remain stable under reasonable parameter variation.

### 7.2 Validation methods (planned)
- **Sanity/limit checks:** zero laying or extreme mortality should collapse the colony, as expected.
- **Comparative validation:** benchmark simple vs. structured models (M3 vs. M1/M2) to see whether added structure changes conclusions.
- **Parameter uncertainty propagation:** report output ranges rather than point estimates.
- **Cross-source checks:** compare model-implied lifespans/rates against literature ranges.

### 7.3 Sensitivity analysis plan (SP2)
- **One-at-a-time screening** to identify obviously influential parameters.
- **Global variance-based analysis** to capture interaction effects.
- **Factor set to test:** egg-laying rate, summer/autumn lifespans, stage mortality, forage availability, stressor intensity, foraging radius.
- **Target outputs:** peak colony size, seasonal minimum, and (derived) required hive count.
- **Reporting:** ranked influence with ranges, and identification of which factors deserve better data in future work.

### 7.4 Planned checkpoints
- Assumptions reviewed against the problem statement.
- Model structure reviewed against qualitative biology.
- Sensitivity design reviewed for coverage of both explicit and implicit factors.

---

## 8. Expected Result Interpretation

*(Interpretation framework only — no values produced at this stage.)*

- **Colony dynamics:** the later solvable model is expected to yield a seasonal colony-size trajectory whose shape can be interpreted as the baseline "healthy colony" reference curve.
- **Sensitivity:** results are expected to be interpreted as a ranking of *relative influence*, not as precise numerical coefficients; egg-laying rate and lifespan parameters are anticipated candidates for high influence, but this must be established rather than assumed.
- **Hive count:** the eventual output should be reported as a **range with stated assumptions** (flower density, foraging efficiency, effective radius), and interpreted as planning guidance rather than a precise prescription.
- **Communication artifact:** expected to translate the above into a plain-language takeaway about why colony health matters to pollination and food supply.

Interpretation principles to be applied:
1. Prefer ranges over point estimates.
2. Always restate which assumptions drive the number.
3. Separate model artifact from policy interpretation.

---

## 9. Limitations and Improvements

### 9.1 Anticipated limitations
- **Data scarcity:** no supplied dataset; heavy reliance on literature ranges and stated anchors.
- **Model abstraction:** individual variability and colony-level emergent effects may be simplified away.
- **Spatial simplification:** homogeneous crop area and symmetric foraging may over- or under-estimate coverage.
- **Stressor treatment:** CCD factors may be aggregated rather than mechanistically separated.
- **Parameter identifiability:** several parameters may be confounded without calibration data.

### 9.2 Planned improvements (future work)
- Introduce spatially explicit forage mapping and heterogeneous crop zones.
- Replace aggregate stressor index with component-level mechanisms (disease, pesticide, predator, habitat).
- Add stochastic/agent-based simulation for variance and extinction-risk analysis.
- Incorporate regional climate and crop-calendar data for location-specific scenarios.
- Develop a decision-support style interface that reports hive-count ranges under user-selected assumptions.
- Strengthen the communication artifact with audience testing.

### 9.3 Risk register (planning)
| Risk | Impact | Planned mitigation |
|------|--------|-------------------|
| No calibration data | Conclusions may be assumption-driven | Report ranges; document every assumption |
| Model too simple | Misses key dynamics | Maintain M1/M2 options; comparative validation |
| Model too complex | Unverifiable, hard to communicate | Keep simple benchmark as anchor |
| Spatial assumptions dominate hive count | Unstable recommendation | Sensitivity on radius/flower density |
| Communication gap | Findings misunderstood | Plain-language review of the one-page artifact |

---

## Appendix A — Planning Checklist

- [ ] Assumptions finalized and logged.
- [ ] Parameter table (with units, ranges, sources) completed.
- [ ] Baseline colony model specified.
- [ ] Structured model (stage/delay) specified.
- [ ] Sensitivity design approved.
- [ ] Pollination accounting framework specified.
- [ ] Hive-count derivation framework specified.
- [ ] One-page communication outline prepared.
- [ ] Validation checklist executed.
- [ ] (No solving, computing, or final results performed in this draft.)

---

*End of initial modeling plan draft. This document is a blueprint only; it intentionally contains no computations, no fitted models, and no final conclusions.*
