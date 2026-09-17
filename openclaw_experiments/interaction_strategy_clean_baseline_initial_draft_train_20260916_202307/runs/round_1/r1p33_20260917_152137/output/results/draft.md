# Modeling Blueprint Draft

**Problem ID:** 2023_Dandelions:_Friend?_Foe?
**Title:** Dandelions: Friend? Foe? Both? Neither?
**Source:** HiMCM 2023, Problem A
**Document status:** Planning draft (roadmap only) — no results, no analysis, no solved components.

---

## 1. Problem Background and Restatement

### 1.1 Background

Dandelion (*Taraxacum officinale*) is a flowering plant native to Eurasia that has become
established worldwide. It is easily recognized by its yellow composite flowers and its
puffball seed head, whose achenes are dispersed by wind. Because of its efficient dispersal,
rapid reproduction, and tolerance of disturbed ground, dandelion occupies an ambiguous role:
it is valued as an early-season food source for pollinators and as a culinary/medicinal plant,
yet it is also frequently treated as a weed and, in some regions, as an invasive or
"naturalized" species with economic and ecological consequences.

The problem asks for two linked modeling efforts: (a) a predictive model of dandelion spread
over defined time horizons under different climate regimes, and (b) a general "impact factor"
model for invasive species that can be tested on dandelion and applied to other invasive
plants in specified regions.

### 1.2 Restatement of Deliverables

The final solution (to be produced later) is expected to include:

- A **spread prediction model** for dandelions at 1, 2, 3, 6, and 12 month horizons.
- Consideration of **three climate regimes**: temperate, arid, and tropical.
- An **impact factor model** for invasive species incorporating plant characteristics and
  environmental harm.
- **Testing** of the impact factor model on dandelions.
- **Application** of the impact factor model to **two additional invasive plant species**,
  each with a specified region of invasion.
- A submission of at most 25 pages, including a one-page summary sheet and the complete
  solution.

### 1.3 Scope Note

This document defines *how* the problem would be approached. It intentionally contains no
numerical predictions, no fitted parameters, no model outputs, and no conclusions.

---

## 2. Objectives and Subproblems

### 2.1 Primary Objectives

- **O1.** Design a defensible mathematical framework that predicts the spatial and/or
  population spread of dandelions over multiple time horizons.
- **O2.** Make the spread framework climate-aware so that temperate, arid, and tropical
  conditions can be compared under a shared modeling language.
- **O3.** Design a general, transparent, and transferable "impact factor" index for invasive
  species.
- **O4.** Define how the impact factor index would be instantiated for dandelions and for two
  further invasive plants in named regions.

### 2.2 Subproblems

- **S1 — Spread dynamics core.** Population growth and dispersal mechanism (seed production,
  wind dispersal kernel, germination, mortality).
- **S2 — Spatial-temporal expansion.** Conversion of local demography into an expanding
  spatial footprint at 1/2/3/6/12 months.
- **S3 — Climate parameterization.** Mapping temperate / arid / tropical conditions onto
  model parameters (growth rate, seasonality, germination thresholds, dispersal conditions).
- **S4 — Impact factor construction.** Selection of indicator dimensions (ecological,
  economic, health, management), weighting scheme, normalization, and aggregation.
- **S5 — Impact factor validation and transfer.** Test on dandelion and apply to two other
  invasive species in declared regions.
- **S6 — Communication.** A concise, page-limited report including a one-page summary sheet.

### 2.3 Deliverable Mapping

| Deliverable | Subproblems | Section reference |
|---|---|---|
| Spread model (1–12 months) | S1, S2 | Section 5.2 |
| Climate comparison | S3 | Section 5.3 |
| Impact factor model | S4 | Section 5.4 |
| Dandelion test case | S5 | Section 7.4 |
| Two extra species + regions | S5 | Section 7.4 |
| 25-page report + summary | S6 | Section 6.5 |

---

## 3. Assumptions

### 3.1 Necessary Assumptions (to be justified and, where possible, tested)

**A1 — Modeling unit.** A representative patch of suitable habitat is assumed, with the model
tracking either plant density or occupied area rather than individual plants (unless an
agent-based approach is later selected; see Section 5.2).

**A2 — Initial condition.** The simulation starts from a small, localized founding population
or seed bank, consistent with a new introduction or a defined study plot.

**A3 — Reproducibility.** Dandelion reproduction in the model is assumed to be dominated by
apomictic (seed-based) reproduction, with clonal/root-fragment spread treated as a secondary
or optional mechanism.

**A4 — Dispersal symmetry.** Wind dispersal is assumed to be anisotropic in reality but
treated initially with a symmetric (radial) kernel for tractability, with anisotropy added as a
refinement (see Section 5.2 and Section 8).

**A5 — Climate as parameter sets.** Temperate, arid, and tropical climates are represented by
distinct parameter regimes (growth rate, germination fraction, seed viability, growing-season
length) rather than by full meteorological simulation.

**A6 — Homogeneous environment.** Within a single scenario, habitat quality, soil, and
competition pressure are assumed spatially homogeneous unless heterogeneity is explicitly
added in a later refinement.

**A7 — No catastrophic events.** Extreme stochastic events (fire, mass herbivory, eradication
programs) are excluded from the baseline scenarios and reserved for sensitivity analysis.

**A8 — Impact factor comparability.** Indicators chosen for the impact factor are assumed
comparable across species after normalization, and the weighting is assumed to be
documented and defensible rather than objectively unique.

**A9 — Region definition.** For the two additional invasive species, the "region where it is
invasive" is a declared, bounded geographic area rather than a vague global label.

### 3.2 Justification Approach

Each assumption will be justified in the final report by reference to the problem's source
materials (ANPC dandelion fact sheet, Wisconsin Extension article, invasivespeciesinfo.gov)
and by standard practice in population ecology / invasion biology.

### 3.3 Future Validation Approach for Assumptions

- **Parameter plausibility:** compare assumed ranges against literature values in the final
  write-up (no fitting in this planning stage).
- **Structural checks:** confirm that model behavior is invariant to reasonable changes in
  assumptions (assumption-sensitivity sweep, Section 7.3).
- **Anisotropy/dispersal:** compare isotropic vs anisotropic variants as an optional
  extension.
- **Impact factor robustness:** vary weights and normalization choices to test ranking
  stability.

---

## 4. Data Processing Plan

### 4.1 Data Sources Anticipated

- Problem-supplied references:
  - ANPC dandelion fact sheet (life history, dispersal, control).
  - University of Wisconsin Extension dandelion article (biology, habitat).
  - invasivespeciesinfo.gov (definition and criteria for invasive species).
- Public ecological/agronomic references for parameter ranges (to be cited, not fitted here):
  seed output per plant, seed mass, terminal velocity / settling speed, germination
  temperature thresholds, rosette growth rates, flowering phenology.
- Climate classification references (e.g., Köppen-style temperate / arid / tropical grouping)
  to bucket climate regimes.

### 4.2 Preprocessing Steps (planned)

1. **Source triage:** classify each source as (i) qualitative/descriptive or (ii)
   quantitative/parameterizable.
2. **Parameter table construction:** build a candidate parameter table with symbol, meaning,
   unit, plausible range, and source; flag values needing later justification.
3. **Unit harmonization:** standardize to SI-consistent units (metres, days, individuals or
   biomass per area).
4. **Climate bucketing:** map climate regimes to parameter sets; document conversion rules
   (e.g., growing-season length in days per year).
5. **Missing-data policy:** where a parameter is unknown, define a default and mark it for
   sensitivity analysis rather than silently fixing it.
6. **Data dictionary:** maintain a single dictionary so spread model and impact factor model
   share consistent terminology.

### 4.3 Feature / Variable Construction (planned)

- **Spread model features:** intrinsic growth rate, carrying capacity, seed production rate,
  dispersal distance scale, germination fraction, survival/mortality, season length, initial
  population/area.
- **Impact factor features (candidate dimensions):**
  - *Ecological:* competitive displacement, habitat alteration, native biodiversity impact.
  - *Economic:* agricultural yield loss, management/control cost, land-value effects.
  - *Health:* allergenicity (relevant for dandelion pollen), toxicity, human nuisance.
  - *Spread potential:* dispersal ability, reproduction rate, climate breadth.
  - *Management difficulty:* persistence, resistance to control, recolonization speed.
- **Derived features:** normalized sub-scores per dimension; aggregated composite indices.

### 4.4 Data Usage Strategy

- **No data fitting in this planning phase.** The plan only specifies how data *will* be used.
- Consolidate all quantitative inputs into one parameter table, version-controlled in the
  final repository.
- Reserve a subset of qualitative knowledge for narrative validation of model behavior.
- Clearly separate literature-derived parameters (defensible, citable) from assumed defaults
  (flagged for sensitivity testing).

---

## 5. Candidate Model Framework

### 5.1 Overview

Two coupled modeling streams:

- **Stream A — Spread prediction** (S1–S3): temporal population dynamics + spatial dispersal.
- **Stream B — Impact factor** (S4–S5): multi-criteria composite index for invasive species.

### 5.2 Stream A — Spread Prediction Models

**Candidate A-1: Reaction–Diffusion (Fisher–KPP) model (baseline).**
- Idea: a scalar density *u(x,t)* evolves under local logistic growth plus Fickian diffusion,
  yielding traveling-wave expansion.
- Advantages: analytically tractable; gives a clean characteristic spread speed; easy to
  compare climates via parameter changes.
- Limitations: assumes homogeneous habitat, isotropic diffusion, and a single dispersal scale;
  may over-simplify long-distance jumps.

**Candidate A-2: Integro-difference equation (IDE) with dispersal kernel (refinement).**
- Idea: discrete-time growth followed by a convolution with a wind-dispersal kernel (e.g.,
  exponential, Gaussian, or fat-tailed).
- Advantages: realistic wind-dispersal representation; naturally produces fat-tailed spread and
  accelerating invasion fronts.
- Limitations: kernel choice matters, parameter-hungry, requires careful numerical treatment.

**Candidate A-3: Stage-structured / matrix population model (demography).**
- Idea: Leslie/Lefkovitch matrix over seed, seedling, rosette, flowering stages, to capture
  delayed reproduction and seed-bank effects.
- Advantages: captures life-history detail; links well to climate-driven stage transitions.
- Limitations: less directly spatial; needs coupling to A-1/A-2 for spread geometry.

**Candidate A-4: Stochastic / agent-based simulation (extension).**
- Idea: individual-plant or grid-cell stochastic process with random dispersal events.
- Advantages: models rare long-distance dispersal and variability; supports uncertainty bounds.
- Limitations: computationally heavy; harder to analytically validate.

**Planned combination:** use A-1 as the conceptual baseline and A-2 (with A-3 demography) as
the main predictive engine; keep A-4 as an extension for stochastic realism. The final report
would state which is chosen for which horizon.

**Spread output definition (planning only):** report predicted occupied area or radial extent
(and/or population density) at 1, 2, 3, 6, and 12 months, with the metric explicitly stated.

### 5.3 Stream A — Climate Parameterization (S3)

- **Temperate:** moderate but seasonal growth; a distinct cold dormant period; spring/autumn
  flushes; moderate moisture.
- **Arid:** growth limited by water availability; short, rainfall-triggered germination
  windows; high seed-bank dormancy; slower effective spread.
- **Tropical:** continuous or multi-cycle growing season; high growth and reproduction rates;
  potential for year-round flowering; competition-limited spread.

Plan: express each regime as a distinct parameter set (growth rate, germination fraction,
season length, dormancy, mortality) applied to the same Stream-A equations, so climates are
directly comparable.

### 5.4 Stream B — Impact Factor Model (S4)

**Candidate B-1: Weighted additive multi-criteria index.**
- Idea: select indicator dimensions (Section 4.3), normalize each to a common scale, assign
  weights, and sum to an "impact factor" score.
- Advantages: transparent, explainable, easy to test on multiple species.
- Limitations: weight subjectivity; compensability (high scores can offset low ones).

**Candidate B-2: Hierarchical / AHP-weighted index.**
- Idea: use Analytic Hierarchy Process to derive weights from pairwise importance judgments.
- Advantages: structured, documented weighting; reduces arbitrary weight choice.
- Limitations: still relies on expert judgment; rank-reversal risk.

**Candidate B-3: Multi-attribute utility / scoring rubric.**
- Idea: define anchored rubrics per indicator (e.g., 0–5 scales) and aggregate.
- Advantages: simple, reproducible, easy to communicate.
- Limitations: coarse resolution; boundary effects.

**Candidate B-4: Comparative ranking / composite normalization (e.g., min–max or
z-score aggregation).**
- Idea: rank species relative to each other after normalization.
- Advantages: directly answers "how bad is this species relative to another."
- Limitations: depends on the comparison set; not absolute.

**Planned combination:** B-1 as the core structure, with B-2 (AHP) for weight elicitation and
B-3 rubric anchors for scoring; B-4 for cross-species ranking presentation.

### 5.5 Variables (shared glossary, planned)

- *N(t)* or *u(x,t)*: population density / occupancy.
- *r*: intrinsic growth rate. *K*: carrying capacity.
- *D*: diffusion coefficient. *L*: dispersal distance scale. *k(·)*: dispersal kernel.
- *g*: germination fraction. *s*: seed survival / viability. *m*: mortality.
- *T*: season length / growing-season days.
- *IF*: impact factor composite score; *w_i*: indicator weights; *x_i*: normalized indicator
  values.

### 5.6 Advantages and Limitations Summary

| Model | Key advantage | Key limitation |
|---|---|---|
| A-1 Reaction–diffusion | Analytic spread speed | Isotropic, homogeneous |
| A-2 IDE kernel | Realistic wind dispersal | Kernel sensitivity |
| A-3 Matrix demography | Life-history fidelity | Weak spatial link |
| A-4 Stochastic/ABM | Variability, rare events | Computationally heavy |
| B-1 Weighted index | Transparent | Weight subjectivity |
| B-2 AHP index | Structured weights | Judgment-dependent |
| B-3 Rubric scoring | Simple, reproducible | Coarse |
| B-4 Comparative ranking | Relative clarity | Comparison-set dependence |

---

## 6. Implementation Roadmap

### 6.1 Algorithms (planned, not executed here)

- Numerical integration of reaction–diffusion PDEs (finite-difference or spectral).
- Discrete convolution for IDE kernel evolution (FFT or direct summation).
- Matrix iteration / eigen-analysis for stage-structured demography.
- Monte Carlo sampling for stochastic scenarios and uncertainty bounds.
- Weighted aggregation and normalization routines for the impact factor.
- Optional: AHP eigenvector computation for weights.
- Optional: agent-based or grid-based simulation for stochastic spread.

### 6.2 Workflow Phases

1. **Phase 0 — Framing:** finalize objectives, scope, and metric definitions.
2. **Phase 1 — Parameter assembly:** build parameter table and climate parameter sets.
3. **Phase 2 — Core spread model:** implement baseline A-1, then A-2 (+A-3) with simple
   configurations.
4. **Phase 3 — Climate scenarios:** run temperate / arid / tropical parameterizations.
5. **Phase 4 — Impact factor:** define indicators, weights, normalization, aggregation.
6. **Phase 5 — Testing & transfer:** instantiate for dandelion; apply to two invasive species.
7. **Phase 6 — Validation & sensitivity:** see Section 7.
8. **Phase 7 — Reporting:** assemble ≤25-page solution + one-page summary sheet.

### 6.3 Required Modules

- `parameters` — parameter table, units, sources, climate sets.
- `spread_core` — PDE / IDE / matrix demography engines.
- `climate` — regime definitions and parameter mapping.
- `impact_factor` — indicator definitions, normalization, weighting, aggregation.
- `scenarios` — 1/2/3/6/12-month configurations per climate.
- `analysis` — sensitivity, uncertainty, and scenario comparison.
- `reporting` — tables/figures generation and summary drafting.
- `docs` — data dictionary and assumption log.

### 6.4 Tooling (planned)

- A single scripting environment (e.g., Python) for models and analysis.
- A version-controlled parameter/data dictionary.
- Reproducible run configuration per scenario.

### 6.5 Reporting Plan

- One-page summary sheet: problem restatement, approach, key qualitative findings,
  applicability, and limitations (written in final solution stage).
- Main body ≤25 pages including model derivations, parameter justification, scenario design,
  validation, and limitations.

---

## 7. Validation Strategy

### 7.1 Evaluation Metrics (planned)

- **Spread model:**
  - Internal consistency of predicted occupied area / radial extent across horizons.
  - Monotonicity and growth-rate plausibility (qualitative check).
  - Sensitivity of predicted spread to each parameter (elasticity-style measures).
  - Qualitative agreement with known dandelion biology (e.g., rapid spring establishment).
- **Impact factor:**
  - Ranking stability under weight and normalization variations.
  - Rank correlation between weighting schemes.
  - Face validity: does the dandelion score match qualitative expectations?

### 7.2 Validation Methods (planned)

- **Analytical checks:** compare numerical PDE/IDE solutions to known analytic results in
  simplified limits (e.g., traveling-wave speed in the KPP regime).
- **Mass-conservation / boundedness checks:** confirm no negative densities and no unbounded
  growth beyond carrying capacity in the spatial model.
- **Cross-model comparison:** compare A-1 vs A-2 predictions to see where they diverge and why.
- **Qualitative validation:** check model behavior against the descriptive sources used for
  assumptions.
- **Residual-type reasoning (if data become available):** if any field data can be used later,
  compare model vs observation qualitatively; no fitting here.

### 7.3 Sensitivity Analysis (planned)

- One-at-a-time (OAT) sweeps of growth rate, dispersal scale, germination fraction,
  mortality, and season length.
- Multi-parameter sampling (Monte Carlo / Latin hypercube) for uncertainty bounds.
- Climate-regime contrast: isolate which parameters drive differences among temperate, arid,
  and tropical scenarios.
- Assumption sensitivity: toggle assumptions A4 (anisotropy), A6 (heterogeneity), A7
  (catastrophic events).
- Impact factor weight/normalization sweeps.

### 7.4 Testing and Transfer Plan

- Instantiate the impact factor for **dandelion** using the assembled indicators.
- Apply the *same* framework to **two additional invasive plant species**, each with an
  explicitly named region of invasion, to demonstrate transferability.
- Compare impact factor scores across species and interpret ordering (interpretation written
  in final stage).

---

## 8. Expected Result Interpretation

This section describes *how results will be interpreted later*, not what they are.

- **Spread horizons (1/2/3/6/12 months):** expect to express spread as occupied area or radial
  extent and to interpret growth as early exponential-ish expansion slowing toward a
  carrying-capacity-limited regime; expect climate to modulate both speed and eventual extent.
- **Climate contrast:** expect temperate and tropical regimes to favor faster establishment
  than arid regimes, with the mechanism (growth vs moisture-limited germination) to be
  reported explicitly.
- **Impact factor:** expect a composite score that ranks dandelion relative to other invasive
  species; expect to state clearly that dandelion's role is context-dependent ("friend, foe,
  both, neither") — a moderate ecological impact combined with high visibility/nuisance in
  some settings.
- **Transfer to other species:** expect the ordering to be sensitive to chosen indicators and
  weights; plan to report the ranking with uncertainty/stability statements.
- **Overall:** results will be presented as scenario-based predictions with explicit
  assumptions, not as universal statements.

---

## 9. Limitations and Improvements

### 9.1 Anticipated Limitations

- **Data scarcity:** limited field data for calibration; heavy reliance on literature ranges
  and assumed defaults.
- **Homogeneity assumption:** real habitats are heterogeneous; results may overstate uniform
  spread.
- **Isotropy assumption:** wind directionality not captured in the baseline.
- **Parameter uncertainty:** growth, dispersal, and germination parameters vary widely in
  nature.
- **Impact factor subjectivity:** weights and indicator choices are judgment-dependent.
- **Cross-species transferability:** an index tuned conceptually for dandelion may not capture
  species-specific harm (e.g., fire-regime alteration).
- **Metric ambiguity:** "spread" could mean area, density, or distribution range; choice
  affects interpretation.

### 9.2 Planned Improvements / Extensions

- Add anisotropic, wind-direction-dependent dispersal kernels.
- Introduce spatially heterogeneous habitat suitability maps.
- Couple to real climate data (temperature/precipitation time series) instead of static
  regimes.
- Add stochastic long-distance dispersal and Allee effects.
- Implement a rigorous expert-elicited AHP weighting and report rank-reversal analysis.
- Validate against field or citizen-science occurrence records if obtainable.
- Provide interactive or parameterized exploration for scenario analysis.

### 9.3 Planning-Stage Caveats

This document is a blueprint only. No computations, fits, data analyses, plots, or
conclusions have been produced. All statements above describe intended future work and the
rationale for design choices.

---

*End of modeling blueprint draft.*
