# Modeling Blueprint Draft — MM-Bench 2020_B
## Best 3-Dimensional Geometric Shape for a Sandcastle Foundation

> **Status:** Initial planning draft (modeling blueprint only).
> This document defines *how* the problem will be modeled. It contains no computed
> results, no completed analysis, and no final conclusions. All statements are
> future-oriented and describe intended methods, assumptions, and validation steps.

---

## 1. Problem Background and Restatement

### 1.1 Background

Recreational sandy ocean beaches worldwide host sandcastles built by children and
adults. Builders typically begin with an initial foundation: a single, nondescript
mound of wetted sand that is then cut and shaped into a recognizable 3-dimensional
geometric form. Ocean waves and rising tides inevitably erode these structures, and
sandcastles built at roughly the same size, on the same beach, and at roughly the
same distance from the water may nevertheless erode at different rates. This
variability motivates the central question: **does a best 3-dimensional geometric
shape exist for a sandcastle foundation, and if so, what is it?**

### 1.2 Native Requirements (to be preserved)

The model to be developed is expected to address the following native requirements:

- **(R1) Foundation shape.** Construct a mathematical model to identify the best
  3-D geometric shape for a sandcastle foundation that survives longest on a
  seashore experiencing waves and tides, subject to the controlled conditions:
  same distance from the water, same sand type, roughly equal sand mass, and equal
  water-to-sand proportion.
- **(R2) Optimal mixture.** Use the model to determine an optimal sand-to-water
  mixture proportion for the foundation, assuming no other additives or materials
  (no plastic/wooden supports, stones, etc.).
- **(R3) Rain robustness.** Adjust the model to determine how the best shape from
  R1 is affected by rain, and whether it remains the best shape under rainfall.
- **(R4) Additional strategies.** Identify other strategies that might extend
  sandcastle lifetime.
- **(R5) Communication.** Produce an informative 1–2 page article for the
  non-technical vacation magazine *Fun in the Sun* describing the model and its
  results.

### 1.3 Critical Framing Notes

- The provided dataset definition is **empty** (`dataset_path`, `dataset_description`,
  and `variable_description` carry no entries) and the local `data/` directory is
  currently **unpopulated**. The plan therefore treats this as a **data-free,
  physics- and theory-driven modeling problem** and must explicitly define a
  data-acquisition / parameter-sourcing strategy (Section 4) rather than assume
  pre-staged measurements.
- "Best" is not yet defined and must be formalized as a measurable objective
  (candidate: maximize a survival-time functional under a fixed erosion forcing
  and fixed initial sand budget).
- The three controlled conditions in R1 are **constraints that equalize the
  comparison**, so the optimization must invert under equal volume and equal
  water fraction, not under equal size.

---

## 2. Objectives and Subproblems

### 2.1 Overall Objective

To design a mathematical-computational framework that ranks candidate 3-D
foundation shapes by predicted survival time under realistic wave/tide forcing at a
fixed waterline distance, and that jointly identifies a favorable sand-to-water
proportion — then to extend the framework to rainfall conditions and to catalog
complementary protective strategies.

### 2.2 Formalized Objective Statement (to be fixed in the modeling stage)

The eventual model should seek a shape and mixture that maximize a survival-time
functional, subject to constraints of equal sand mass, equal initial water fraction,
fixed standoff distance from the waterline, and a specified wave/tide forcing
scenario. The precise functional form will be selected during modeling.

### 2.3 Subproblems (mapped to requirements)

- **SP1 — Shape comparison under equal resources (→ R1).** Define a family of
  candidate geometric foundations, equalize sand volume and water fraction, and
  predict relative erosion resistance.
- **SP2 — Erosion-mechanics core (→ R1, R3).** Build the physics submodel that
  converts wave/tide/rain forcing into shape-dependent sand loss.
- **SP3 — Mixture optimization (→ R2).** Relate water-to-sand proportion to
  cohesion/strength and to erodibility; identify a preferred proportion.
- **SP4 — Rainfall extension (→ R3).** Add rain-driven saturation, surface runoff,
  and slumping mechanisms; re-rank shapes.
- **SP5 — Strategy catalog (→ R4).** Enumerate and qualitatively prioritize
  non-shape interventions (placement, timing, surface treatment, drainage, etc.).
- **SP6 — Communication product (→ R5).** Translate model logic and outputs into a
  lay-reader magazine article.

### 2.4 Deliverables

- A documented modeling framework (equations/mechanisms defined, not evaluated).
- A candidate shape family with a comparison protocol under equal-resource constraints.
- A parameter-sourcing and data-acquisition plan.
- An algorithmic implementation roadmap (simulation + optimization loops).
- A validation and sensitivity-analysis design.
- A communication plan for the *Fun in the Sun* article.

---

## 3. Assumptions

Assumptions are grouped by role. Each must later be tested or bounded (see Section 7).

### 3.1 Physical / Environmental Assumptions

- **A1. Quasi-steady forcing.** Wave climate and tide schedule can be represented by
  a manageable set of statistical descriptors (e.g., representative wave height,
  period, and a tide level curve) rather than a full stochastic sea state.
- **A2. Fixed standoff.** All candidate shapes start at the same distance from the
  waterline, so differences in survival are attributable to shape and mixture only.
- **A3. Homogeneous sand.** Sand grain properties (size, gradation, shape) are
  uniform within a build and constant across candidates.
- **A4. Isothermal, drained/undrained behavior bracketed.** Sand is treated as a
  partially saturated porous medium; behavior is bracketed between drained and
  undrained idealizations at the modeling stage.
- **A5. Erosion mechanisms.** Dominant loss modes are assumed to be (i) wave
  run-up/scour, (ii) tide-driven submergence and saturation softening, (iii)
  surface runoff/slumping from rain (for R3), and (iv) gravity-driven slope failure
  of over-steep faces. Wind and biological disturbance are treated as secondary.
- **A6. No additives.** Only sand and water are present (per R2), so stabilization
  arises solely from moisture-induced capillary cohesion and packing.

### 3.2 Modeling Assumptions

- **A7. Candidate shapes are tractable geometers.** The shape family is restricted to
  analytically or numerically meshable solids (e.g., cone, frustum, hemisphere,
  dome, pyramid, prismatic frustum, and combinations) chosen for buildability and
  symmetry.
- **A8. Scale separation.** Local erosion can be modeled at a fine scale and coupled
  to a coarse survival metric without resolving every grain.
- **A9. Equal resource constraint.** Sand mass/volume and initial water-to-sand
  ratio are held equal across candidates, forcing genuine shape comparisons.
- **A10. Survival metric is definable.** "Last the longest" can be operationalized as
  time to reach a defined failure threshold (e.g., loss of a specified fraction of
  volume, or breach of a load-bearing feature height).

### 3.3 Justification and Future Validation (per assumption)

- A1–A2 keep comparisons apples-to-apples and will be tested by injecting variable
  wave/tide scenarios in sensitivity analysis (Section 7).
- A3 may be relaxed later to explore grain-size effects; validated against
  literature-derived sand properties.
- A4–A6 define the physics scope; each mechanism will be validated against
  documented geotechnical/sediment-transport behavior.
- A7–A10 are modeling conveniences whose impact will be probed via ablation
  (adding/removing shape families, threshold definitions, and mechanisms).

---

## 4. Data Processing Plan

Because the dataset definition is empty and `data/` is currently unpopulated, the
"data plan" is a **data-acquisition and parameterization plan** rather than a
preprocessing pipeline for staged files.

### 4.1 Data Sources to Be Assembled

- **Geotechnical parameter sources:** published values/ranges for sand internal
  friction angle, apparent cohesion vs. moisture content, porosity, permeability,
  and bulk density, used to bound model parameters.
- **Coastal forcing sources:** representative wave height/period and tide-range
  statistics for a generic sandy beach, used to define forcing scenarios.
- **Meteorological sources:** rainfall intensity/duration distributions for the
  rain extension (R3).
- **Analog experimental sources:** any available controlled sandcast/cube erosion
  studies or sediment-transport benchmarks for qualitative calibration.

### 4.2 Preprocessing Steps (planned)

- **Unit harmonization:** normalize all parameters to SI units and consistent
  reference conditions.
- **Bounding/standardization:** express literature parameters as ranges/priors
  rather than point values to preserve uncertainty.
- **Scenario construction:** assemble a small set of forcing scenarios (calm,
  moderate, storm; spring vs. neap tide; light vs. heavy rain).
- **Quality screening:** record provenance for each parameter and flag
  low-confidence values for sensitivity analysis.

### 4.3 Feature / Variable Construction (planned)

- **Shape descriptors:** normalized volume, height-to-base aspect ratio, slope
  angles, curvature/roundness, surface-to-volume ratio, symmetry class.
- **Mixture descriptor:** water-to-sand ratio (and derived saturation degree).
- **Forcing descriptors:** wave energy proxy, tide range, rain intensity–duration.
- **Response descriptor:** survival time (and/or retained-volume curve over time),
  to be produced by the simulation stage.

### 4.4 Data Usage Strategy

- Parameter ranges will feed the physics submodels as inputs and uncertainty bands.
- A **simulation-generated dataset** (parametric sweeps over shapes, mixtures,
  forcing) will be constructed to support the optimization and sensitivity stages;
  this is a modeling artifact, not a claim about measured data.
- No staged empirical dataset will be analyzed, since none is available; this
  limitation will be stated explicitly in the final work.

---

## 5. Candidate Model Framework

The framework is layered so that shape, mixture, and rain effects can be studied
independently and then coupled. All methods below are candidates to be compared and
selected during modeling.

### 5.1 Layer 1 — Geometry & Shape Parameterization

- **Idea:** Represent each candidate foundation as a parametric solid with a small
  number of shape parameters (base radius, height, wall slope, curvature exponent,
  doming factor), enforcing an equal-volume constraint.
- **Candidate methods:** standard analytic solids; superellipsoid/superquadric
  parameterization for smooth interpolation between families; spline/height-field
  surfaces for irregular buildable forms.
- **Purpose:** Provide a common, comparable design space for R1.

### 5.2 Layer 2 — Mixture / Material Model (→ R2)

- **Idea:** Model the wetted sand as a partially saturated granular medium whose
  strength depends on water content through capillary (matric suction) cohesion.
- **Candidate methods:**
  - Mohr–Coulomb strength framework with moisture-dependent apparent cohesion.
  - Capillary-bridge / suction models (e.g., effective-stress with suction term).
  - Empirical strength-vs-water-content curves parameterized from literature.
- **Purpose:** Map water-to-sand ratio to a strength/stability index and to an
  erodibility coefficient, enabling an optimal-proportion search.

### 5.3 Layer 3 — Erosion & Failure Mechanics (→ R1, R3)

- **Idea:** Convert forcing into material loss via mechanism-specific submodels.
- **Candidate methods (per mechanism):**
  - **Wave/scour:** shear-stress–based detachment, threshold-of-motion, or
    empirical erosion-rate laws driven by local near-bed velocity.
  - **Tide/submergence:** progressive saturation softening and buoyancy changes.
  - **Rain (R3):** infiltration, saturation front advance, surface runoff, and
    slope-wash / slumping criteria.
  - **Slope stability:** limit-equilibrium or simple yield checks for over-steep
    faces (identifying shape classes prone to collapse).
- **Candidate solution techniques:** reduced-order analytical models where possible;
  finite-volume/finite-element surface-evolution or sediment-transport simulation
  for higher fidelity; cellular-automaton / discrete erosion models as a lighter
  alternative.
- **Purpose:** Produce shape- and mixture-dependent erosion.

### 5.4 Layer 4 — Survival-Time / Loss-Evolution Model

- **Idea:** Integrate erosion over a forcing timeline to define survival time.
- **Candidate methods:** time-stepping simulation of shape evolution; survival
  functions / hazard-style models; surrogate models (response surfaces, regression,
  or Gaussian-process surrogates) trained on simulation sweeps for fast ranking.
- **Purpose:** Yield a comparable scalar objective for optimization.

### 5.5 Layer 5 — Optimization & Decision (→ R1, R2)

- **Idea:** Search shape-parameter space (and mixture) for the objective maximizer.
- **Candidate methods:** grid/parametric sweeps; gradient-free optimizers
  (Nelder–Mead, pattern search, evolutionary/particle-swarm, Bayesian optimization
  over the surrogate); multi-objective treatment if stability and durability
  conflict.
- **Purpose:** Identify the best shape and preferred water-to-sand proportion.

### 5.6 Layer 6 — Rain-Adjusted Re-ranking (→ R3)

- **Idea:** Re-run the ranking under rain-inclusive forcing using the same protocol.
- **Candidate methods:** reuse Layers 1–5 with the rain mechanisms of Layer 3
  activated (and, if needed, a coupled wetting–strength–erosion loop).
- **Purpose:** Determine whether the R1 winner persists under rainfall.

### 5.7 Layer 7 — Strategy Catalog (→ R4)

- **Idea:** Systematically enumerate non-shape levers and assess them against the
  same survival metric.
- **Candidate levers:** build timing vs. tide, placement/micro-siting, compaction
  and layering, surface sealing/drainage channels, scale effects, temporary
  windbreaks, and moisture management — all without disallowed additives.
- **Purpose:** Complement the shape answer with practical tactics.

### 5.8 Variables (nomenclature to be finalized)

- **Design variables:** shape parameters; water-to-sand ratio.
- **State variables:** saturation degree, local surface elevation, cohesion, stress state.
- **Forcing variables:** wave height/period, tide level vs. time, rain intensity/duration.
- **Response variables:** retained volume over time, time-to-failure, stability margin.
- **Fixed/controlled parameters:** sand type, initial volume, standoff distance.

### 5.9 Advantages and Limitations of Candidate Approaches

- **Reduced-order analytical models:** transparent, fast, good for intuition —
  but oversimplify coupled processes.
- **Full numerical simulation:** higher fidelity for complex flow–structure
  interaction — but computationally expensive and parameter-hungry.
- **Surrogate/response-surface models:** enable fast optimization — but require
  validated training data (here, simulation-generated) and careful extrapolation.
- **Discrete/cellular erosion models:** flexible and simple — but calibration and
  physical fidelity must be justified.

A likely design is a **hybrid**: a reduced-order core for shape ranking, a
numerical component for mechanism validation, and a surrogate for optimization.

---

## 6. Implementation Roadmap

### 6.1 Phased Workflow

1. **Formalization phase.** Fix the objective functional, failure threshold, and
   shape family; encode the equal-resource constraints.
2. **Parameterization phase.** Assemble literature-based parameter ranges and
   forcing scenarios (Section 4).
3. **Geometry module.** Implement parametric shape generation + equal-volume
   constraint enforcement.
4. **Material module.** Implement mixture → strength/erodibility mapping.
5. **Erosion module.** Implement wave, tide, slope, and (later) rain mechanisms.
6. **Simulation/integration module.** Time-step shape evolution to a survival metric.
7. **Optimization module.** Sweep/optimize over shape and mixture; build surrogate
   if needed.
8. **Rain module.** Activate rain mechanisms and re-rank.
9. **Strategy module.** Encode and evaluate R4 levers under the same metric.
10. **Analysis & communication phase.** Sensitivity analysis (Section 7) and draft
    the *Fun in the Sun* article (Section 8).

### 6.2 Required Modules (planned code structure)

- `geometry/` — shape generators, volume constraints, mesh/height-field utilities.
- `material/` — mixture-to-strength/erodibility models.
- `forcing/` — wave/tide/rain scenario generators.
- `erosion/` — per-mechanism erosion operators.
- `simulate/` — time integration and survival-metric computation.
- `optimize/` — search and surrogate-based optimization.
- `analysis/` — sensitivity, uncertainty, and ranking analyses.
- `report/` — tables/figures and the lay-audience article draft.

### 6.3 Algorithms (candidates)

- Parametric/differential-evolution/Bayesian optimization for shape search.
- Finite-volume or finite-element surface evolution for high-fidelity checks.
- Latin-hypercube or Sobol sampling for the simulation sweep and sensitivity study.
- Surrogate fitting (regression / Gaussian process) for fast ranking.

### 6.4 Sequencing / Dependencies

Geometry + material + forcing must precede erosion; erosion precedes simulation;
simulation precedes optimization; all precede the rain re-ranking and the final
communication phase. A minimal end-to-end "thin slice" will be built first, then
refined.

---

## 7. Validation Strategy

### 7.1 Evaluation Metrics (planned)

- **Primary:** predicted survival time (time-to-failure) under each forcing scenario.
- **Secondary:** retained-volume fraction over time; stability margin; robustness of
  ranking (rank stability across parameter settings).
- **Mixture metric:** objective value vs. water-to-sand ratio (to locate a preferred
  band rather than an over-precise point).

### 7.2 Validation Methods

- **Internal consistency:** conservation checks (sand mass/volume), limiting-case
  behavior (e.g., extreme forcing should reduce survival monotonically).
- **Cross-model agreement:** compare reduced-order vs. numerical predictions for
  overlapping cases; convergence checks under mesh/time refinement.
- **Literature benchmarking:** compare qualitative erosion trends and parameter
  sensitivities against published geotechnical and sediment-transport behavior.
- **Physical plausibility:** verify that predicted winners are geometrically and
  practically buildable, not artifacts of the objective.
- **Optional physical spot-check (future):** small-scale controlled sandcastle
  erosion tests to qualitatively confirm rankings (out of scope for this drafting
  stage).

### 7.3 Sensitivity and Uncertainty Analysis (planned)

- **Parameter sensitivity:** local (one-at-a-time) and global (variance-based,
  e.g., Sobol) analyses over sand properties, cohesion parameters, and forcing
  intensities.
- **Scenario sensitivity:** vary wave height/period, tide range, storm frequency,
  and rain intensity/duration; test whether the R1 winner and R2 optimum are stable.
- **Model-structure sensitivity:** ablation of mechanisms (with/without rain, with/
  without slope failure) and of the failure-threshold definition.
- **Robustness of ranking:** report whether the top shape remains top under
  perturbed conditions; flag near-ties honestly.

### 7.4 Validation of the Rain Extension (R3)

- Ensure the rain-augmented model reproduces dry-condition rankings as a limit
  (rain intensity → 0 must recover the R1 ranking).
- Test monotonicity: increasing rain intensity/duration should degrade survival and
  may shift the preferred shape.

---

## 8. Expected Result Interpretation

This section describes how outputs *will be interpreted*, not what they are.

- **Shape result (R1).** The model is expected to output a ranked list of candidate
  shapes and a preferred family. Interpretation will emphasize *why* it wins
  (e.g., lower stress concentration, favorable surface-to-volume ratio, gentler
  slopes resisting collapse) rather than a bare label.
- **Mixture result (R2).** The model is expected to indicate a preferred
  water-to-sand band balancing capillary cohesion against saturation-induced
  weakening and flowability; interpretation will frame this as a practical
  target range with uncertainty, not a single magic number.
- **Rain result (R3).** The model is expected to show whether rainfall changes the
  ranking and, if so, in which direction — with an explicit statement of whether
  the R1 winner remains best under rain.
- **Strategy result (R4).** Interpreted as ranked, practical, no-additive tactics,
  each tied to the mechanism it addresses.
- **Communication result (R5).** Interpreted as a faithful, non-technical
  translation whose claims trace back to the model assumptions and outputs.
- **Confidence framing.** All interpretations will be reported with mechanism
  caveats and uncertainty bands, and with clear separation between robust findings
  and parameter-dependent ones.

---

## 9. Limitations and Improvements

### 9.1 Anticipated Limitations

- **No staged dataset.** The empty dataset definition and unpopulated `data/`
  directory mean the model will rely on literature-derived parameters and
  simulation-generated data, limiting empirical grounding.
- **Idealized physics.** Reduced-order erosion laws and simplified forcing may miss
  real 3-D turbulence, infiltration, and mixed-grain effects.
- **Shape-family bias.** Restricting candidate shapes to a parametric family may
  exclude a superior but non-obvious geometry.
- **Objective sensitivity.** Results may depend on the chosen failure threshold and
  forcing scenario, and near-ties may be hard to resolve.
- **Scale/soil variability.** Beach sand and conditions vary widely; conclusions may
  not transfer across sites.

### 9.2 Planned Improvements

- Enrich the parameter set with additional literature and, if permitted later,
  small controlled physical experiments for calibration.
- Broaden the shape family (including hybrid and irregular forms) and allow
  topology changes.
- Increase model fidelity incrementally (coupled flow–structure, full infiltration
  dynamics) where sensitivity analysis shows it matters.
- Strengthen surrogate models with adaptive sampling and uncertainty quantification.
- Add multi-scenario and multi-site robustness analysis, and explicitly report
  confident vs. fragile conclusions.

### 9.3 Scope Boundaries of This Draft

This document intentionally excludes computed results, executed experiments, and
final conclusions. All content is planning-level: objectives, assumptions, candidate
methods, data strategy, implementation roadmap, validation design, and expected
interpretation. Actual modeling, simulation, optimization, and the magazine article
remain to be carried out in subsequent stages.
