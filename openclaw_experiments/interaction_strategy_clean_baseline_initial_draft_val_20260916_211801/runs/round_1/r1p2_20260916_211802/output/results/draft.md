# Gamma Knife Treatment Planning — Modeling Blueprint (Initial Draft)

> **Status:** Planning draft only. This document proposes a roadmap for future modeling
> work. It intentionally contains no computed results, no executed experiments, no fitted
> models, and no final conclusions. All statements are written in future-oriented language.

---

## 1. Problem Background and Restatement

Stereotactic radiosurgery (SRS) aims to deliver a single high dose of ionizing radiation
to a small, well-defined intracranial target while sparing surrounding healthy tissue and
critical structures. The **Gamma Knife** modality delivers this dose from 201 cobalt-60
sources arranged in a helmet; the beams simultaneously converge at an **isocenter**,
producing an approximately spherical dose distribution at the effective dose level. A
single delivery at one isocenter is called a **shot**. Collimator helmets of beam-channel
diameters 4, 8, 14, and 18 mm will be treated as available, interchangeable options, and
each shot will be characterized by its position (isocenter) and its effective radius
(determined by the chosen collimator).

The clinical planning problem will be restated as a **geometric coverage and dose-shaping
optimization problem**: given a discretized 3D target volume (a bounded digital image,
typically millions of voxels) and a set of critical/normal structures, a treatment plan
will be designed as a set of shots whose union approximates the target volume while
respecting physical, dosimetric, and clinical constraints.

Key planning requirements that will guide the future model:

- **Dose-gradient uniformity** across the target volume should be minimized.
- **Isodose contours** should be matched to the target and to specified dose-volume
  constraints of target and critical organs.
- **Integral dose** to normal tissue should be minimized, and dose at specified normal
  tissue points should remain below tolerance.
- **Maximum dose to critical volumes** should be minimized.
- **Hard geometric constraints:** shots should not protrude outside the target; shots
  should not overlap (to avoid hot spots); at least **90%** of the target volume must be
  covered; the number of shots should be minimized (typical clinical practice: 1–15 shots).

**Deliverables (to be produced later, not in this draft):**

- A formal mathematical formulation of the shot-placement / dose-shaping problem.
- An algorithmic pipeline that generates and evaluates candidate shot configurations.
- A reproducible implementation (data handling, optimization, evaluation).
- A validation report with metrics, sensitivity analysis, and interpretation.

---

## 2. Objectives and Subproblems

The overall objective will be decomposed into tractable subproblems so that each can be
modeled and validated independently before integration.

**Primary objective (to be pursued later):**
Construct a treatment plan — a finite set of shots, each with isocenter position and
collimator/radius — that maximizes target coverage quality while satisfying non-protrusion,
non-overlap, and dose-limiting constraints, using as few shots as possible.

**Decomposed subproblems:**

1. **Target representation.** Convert the raw 3D target image into a tractable geometric
   object (voxel mask, level sets, and/or shape descriptors).
2. **Shot model.** Formalize the dose contribution of a single shot as a function of
   position, radius, and collimator, including the notion of an "effective" spherical
   dose region at the relevant prescription level.
3. **Coverage subproblem.** Select and place shots to cover at least 90% of the target
   while respecting non-protrusion and non-overlap.
4. **Conformality / gradient subproblem.** Shape the aggregate dose so isodose surfaces
   follow the target boundary and dose gradients remain controlled.
5. **Sparing subproblem.** Minimize integral dose to normal tissue and constrain dose at
   critical structures/points below tolerance.
6. **Cardinality subproblem.** Minimize the number of shots, which couples back into all
   other subproblems.
7. **Trade-off / decision layer.** Reconcile competing objectives (coverage vs. sparing vs.
   cardinality) into a defensible planning criterion.

Each subproblem will be mapped to a candidate model in Section 5.

---

## 3. Assumptions

The following assumptions will be adopted for the initial modeling effort. Each will be
paired with a justification and a planned validation approach.

**A1. Single-isocenter spherical shot model.** Each shot will be modeled as an
approximately spherical isodose region at the effective dose level, centered at the
isocenter, with radius determined by the collimator diameter.
*Justification:* This reflects the stated physical design of the Gamma Knife (201 beams
converging at one isocenter).
*Future validation:* Compare simplified spherical predictions against a more detailed
dose-kernel or ray-trace model, and against any available reference plans.

**A2. Discretized target representation.** The target will be represented as a finite
voxel set on a regular 3D grid, and coverage/dose quantities will be evaluated on this
grid.
*Justification:* The problem statement describes the target as a bounded digital image;
voxel discretization enables tractable computation.
*Future validation:* Study grid-resolution sensitivity; verify that metric trends are
stable across voxel sizes.

**A3. Additivity of dose contributions.** The total dose at a point will be approximated
as the sum of contributions from all shots.
*Justification:* Standard dose-superposition assumption underlying multiple-shot planning.
*Future validation:* Compare against nonlinear/attenuation-aware models where feasible.

**A4. Effective radius per collimator.** Each collimator helmet will be associated with a
representative spherical dose radius (a modeling parameter to be fixed or calibrated
later).
*Justification:* Provides a clean geometric abstraction; matches the four stated helmet
sizes.
*Future validation:* Sensitivity analysis over radius parameterization; calibrate from
reference data if available.

**A5. Hard geometric constraints are strict.** Non-protrusion (shots inside the target)
and non-overlap of shots will be treated as hard constraints in the base model, with
relaxations explored later.
*Justification:* Directly stated in the problem as prohibitions.
*Future validation:* Compare strict vs. relaxed variants to characterize the cost of
strictness.

**A6. Coverage threshold as a target.** The ≥90% coverage requirement will be treated as a
feasibility floor, with higher coverage pursued as a secondary objective.
*Justification:* Stated minimum requirement.
*Future validation:* Monitor achieved coverage across configurations and the trade-off
curve vs. shot count.

**A7. Static, noise-free geometry.** The plan will assume a static target geometry with
no imaging noise or motion.
*Justification:* Simplifies the initial model; established planning abstraction.
*Future validation:* Robustness experiments perturbing target boundary and structure
positions.

**A8. Structure set is given.** Critical organs/points and tolerance doses will be assumed
available as an input parameter set.
*Justification:* Required for the dose-volume and tolerance constraints.
*Future validation:* Sensitivity analysis over tolerance values and structure extents.

---

## 4. Data Processing Plan

*No data analysis will be performed in this draft; the following is a plan for later
execution. The `data/` directory is currently empty and will be populated or synthesized
as part of the future implementation.*

**4.1 Data sources and inventory.**
- Identify whether an accompanying 3D target image/volume and structure masks will be
  provided with the problem, or whether representative synthetic phantoms will be
  constructed for evaluation.
- Record a data manifest: format, resolution, coordinate convention, units, and any
  provided tolerance/dose parameters.

**4.2 Preprocessing (planned).**
- Load the volumetric target and any structure masks.
- Normalize coordinate systems and grid spacing; document voxel-to-physical mapping.
- Clean the target mask (fill interior holes, remove isolated speckles).
- Optionally extract a level-set / distance field representation of the target for
  shape-aware placement.
- Segment the target into sub-regions (e.g., via connected components / skeleton) to
  guide multi-shot decomposition.

**4.3 Feature construction (planned).**
- Geometric features: target volume, bounding box, principal axes, curvature, and
  distance-to-boundary field.
- Coverage features: voxel membership, boundary voxel set, and the "erosion margin"
  relevant to the non-protrusion constraint.
- Structure features: distance from target to critical structures and tolerance
  parameters.

**4.4 Data usage strategy (planned).**
- Reserve a set of target geometries (real or phantom) for development and a separate
  set for validation.
- Define deterministic train/test-style splits for tuning algorithmic parameters without
  leaking into final validation.
- Standardize inputs into a single internal representation consumed by the solver
  module, so that different targets are handled uniformly.

---

## 5. Candidate Model Framework

Several candidate formulations will be considered; the plan is to prototype the simpler
ones first and escalate to richer ones only if needed.

**M1. Geometric set-cover / covering model (baseline).**
- *Idea:* Discretize candidate shot positions (e.g., on a grid or from target-centric
  candidate generation); each candidate covers a subset of target voxels. Choose a
  minimal set of candidates whose union covers ≥90% of the target.
- *Variables:* binary selection of candidate shots.
- *Constraints:* coverage floor; non-protrusion (candidate shots only within target);
  non-overlap (pairwise exclusion).
- *Objective:* minimize shot count; secondary term for under-coverage.
- *Strengths:* Tractable, directly encodes stated hard constraints.
- *Limitations:* Ignores continuous dose shaping and dose gradient; candidates may be
  coarse.

**M2. Continuous geometric optimization (shot-placement refinement).**
- *Idea:* Treat shot centers and radii as continuous variables; optimize a coverage /
  conformality objective (e.g., Jaccard-type overlap between union-of-spheres and target).
- *Variables:* center coordinates (and selected radii from the four collimators).
- *Constraints:* same geometric constraints as M1, expressed via distance/penetration
  penalties or projections.
- *Strengths:* Fine-grained shaping; can improve conformality.
- *Limitations:* Non-convex; requires careful initialization and constraint handling.

**M3. Dose-aware optimization (forward planning with dose model).**
- *Idea:* Define a simplified dose field (sum of shot kernels) and optimize dosimetric
  objectives: target dose homogeneity, isodose conformality, integral normal-tissue dose,
  critical-structure dose limits, and maximum critical dose.
- *Variables:* shot set, positions, radii/weights.
- *Constraints:* dose-volume constraints (e.g., ≥90% target coverage at prescription),
  tolerance constraints at critical points, non-protrusion, non-overlap.
- *Strengths:* Directly represents the clinical requirements beyond pure geometry.
- *Limitations:* Higher computational cost; requires a defensible shot-kernel model.

**M4. Multi-objective / Pareto framework.**
- *Idea:* Treat coverage, conformality, sparing, and shot count as competing objectives;
  explore the Pareto frontier rather than fixing arbitrary weights.
- *Variables:* shared with M1–M3.
- *Strengths:* Exposes trade-offs for clinical-style judgment.
- *Limitations:* Frontier exploration cost; needs good visualization and selection rules.

**M5. Heuristic / metaheuristic search layer (integration).**
- *Idea:* Use greedy + local search and/or evolutionary/swarm methods to search the
  combinatorial-continuous space efficiently, using M1 candidate generation and M3 dose
  evaluation as subroutines.
- *Strengths:* Scales to realistic problem sizes.
- *Limitations:* No optimality guarantee; requires seed/parameter robustness checks.

**Mathematical ideas to be leveraged (planned):**
- Set-cover / integer programming relaxations and rounding.
- Distance fields and computational geometry for non-protrusion/non-overlap.
- Coverage metrics (Jaccard/Dice, conformity index, coverage fraction).
- Multi-objective optimization and Pareto dominance.
- Sensitivity/robustness analysis via perturbation.

---

## 6. Implementation Roadmap

**6.1 Proposed module breakdown (to be implemented later):**

1. `io` — loaders/parsers for target and structure representations; manifest handling.
2. `geometry` — voxel grid utilities, distance fields, sphere/volume overlap tests.
3. `candidates` — candidate shot generation (grid, skeleton-based, boundary-aware).
4. `shot_model` — single-shot dose/coverage kernel and collimator→radius mapping.
5. `planner` — core optimization (set-cover baseline → continuous refinement).
6. `evaluate` — metrics computation (coverage, conformality, sparing, shot count).
7. `experiment` — orchestration of scenarios, parameter sweeps, and logging.
8. `report` — tables/figures summarizing plan quality and trade-offs.

**6.2 Workflow (planned):**
- Step 1: Finalize problem formalization and constraint definitions.
- Step 2: Implement geometry + candidate generation.
- Step 3: Implement baseline set-cover planner (M1) and validate on simple phantoms.
- Step 4: Add continuous refinement (M2) and dose-aware objectives (M3).
- Step 5: Add multi-objective exploration (M4) and heuristic search (M5).
- Step 6: Run scenario suite, produce metrics, and document trade-offs.
- Step 7: Package results, code, and reproducible scripts.

**6.3 Practical considerations (planned):**
- Version-control code under `code/`; store raw and derived artifacts under `data/`;
  write logs to `logs/`; place final report artifacts in `results/`.
- Keep deterministic seeds and configuration files for reproducibility.
- Build incrementally: validate each module on synthetic toy cases before scaling up.

**6.4 Milestone gates (planned):**
- Gate A: Baseline planner produces feasible plans satisfying ≥90% coverage on test
  phantoms.
- Gate B: Coverage/conformality improve when continuous refinement is added.
- Gate C: Dose-aware objectives demonstrably reduce sparing metrics without violating
  constraints.

---

## 7. Validation Strategy

**7.1 Evaluation metrics (to be computed later):**
- *Coverage:* fraction of target voxels covered at the effective dose level (must meet
  the ≥90% floor).
- *Conformality:* overlap between covered region and target (e.g., Jaccard/Dice,
  conformity index); leakage volume outside target.
- *Gradient / homogeneity:* variability of dose across the target and steepness of the
  dose fall-off outside it.
- *Sparing:* integral dose to normal tissue; dose at critical points vs. tolerance;
  maximum dose to critical volumes.
- *Complexity:* number of shots used (goal: minimal, typically within 1–15).
- *Feasibility:* satisfaction of non-protrusion and non-overlap constraints.

**7.2 Validation methods (planned):**
- *Constraint verification:* explicit geometric checks that every shot lies inside the
  target and no two shots overlap.
- *Phantom tests:* analytic/synthetic targets (sphere, ellipsoid, irregular shapes) with
  known coverage expectations.
- *Comparisons:* baseline M1 vs. refined M2/M3 vs. multi-objective M4 to quantify gains.
- *Reproducibility:* rerun with fixed seeds; confirm stable metrics.
- *Cross-validation:* evaluate the pipeline across multiple target geometries.

**7.3 Sensitivity analysis (planned):**
- Vary voxel resolution and candidate-generation density.
- Vary effective-radius parameterization per collimator.
- Vary the coverage threshold (e.g., around 90%) to reveal the shot-count cost.
- Vary constraint strictness (strict vs. relaxed non-overlap/non-protrusion).
- Vary critical-structure tolerances and positions to test robustness.

**7.4 Planned acceptance criteria (qualitative):**
- All hard constraints satisfied in reported plans.
- Coverage floor met with headroom where possible.
- Metrics stable under reasonable parameter perturbation.

---

## 8. Expected Result Interpretation

*This section describes how future results would be interpreted; it contains no results.*

- **Coverage vs. shot count:** We expect a trade-off curve: coverage improves with more
  shots, with diminishing returns. The plan will interpret the "knee" of this curve as a
  clinically attractive operating point.
- **Conformality:** Higher-grade plans are expected to yield more conformal coverage with
  less leakage outside the target; improvements will be attributed to finer shot
  placement and/or dose-aware objective terms.
- **Sparing:** Dose-aware planning is expected to reduce integral normal-tissue dose and
  critical-structure exposure relative to the purely geometric baseline; the magnitude
  will be reported as a comparative effect, not a fixed number.
- **Multi-objective frontier:** The Pareto set will be interpreted as a menu of plans
  trading coverage, sparing, and complexity, supporting transparent clinical-style
  trade-off discussion.
- **Robustness:** Sensitivity trends will indicate which parameters (grid resolution,
  radius mapping, thresholds) most influence plan quality, guiding where future modeling
  effort should concentrate.

Interpretation will always be framed as relative/comparative and conditional on the
stated assumptions.

---

## 9. Limitations and Improvements

**Anticipated limitations:**
- The spherical-shot abstraction will neglect real beam-profiles, attenuation, and
  non-ideal isodose shapes.
- Voxel discretization will introduce resolution artifacts and metric quantization.
- The non-overlap constraint may be overly conservative relative to clinical practice.
- Multi-objective weighting and final plan selection will involve subjective judgment.
- Computational cost may limit full high-resolution search.
- The absence of (or synthetic nature of) provided data will constrain realism.

**Planned improvements:**
- Replace the spherical shot model with a calibrated dose kernel or ray-traced beamlet
  model.
- Introduce soft constraints / penalty methods to explore the non-overlap relaxation.
- Adopt adaptive resolution (coarse search, fine refinement) for efficiency.
- Incorporate automated Pareto pruning and selection heuristics.
- Extend to uncertainty-aware planning (boundary/structure perturbations) as a robustness
  layer.
- If reference plans become available, calibrate parameters and benchmark directly.

---

*End of planning draft. No problem solving, data analysis, computation, or experiments
were performed in the preparation of this document.*
