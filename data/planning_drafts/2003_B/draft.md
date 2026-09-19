# MM-Bench 2003_B — Modeling Blueprint (Initial Draft)

**Problem ID:** 2003_B
**Title:** MM-Bench 2003_B (Gamma Knife Radiosurgery: Sphere-Packing Treatment Planning)
**Source:** MM-Bench / MCM 2003 Problem B
**Document type:** Modeling plan / blueprint — *not* a solution
**Status:** Draft for future modeling work

> Scope note: This document is a planning artifact only. It states the intended
> workflow, assumptions, candidate methods, data plan, implementation roadmap,
> and validation strategy. It deliberately contains **no** computed results, no
> fitted parameters, no executed experiments, and no final conclusions. All
> quantitative work is deferred to a future modeling stage.

---

## 1. Problem Background and Restatement

Stereotactic radiosurgery (SRS) delivers a single high dose of ionizing radiation
to a radiographically well-defined, small, intracranial 3D brain tumor while
sparing surrounding healthy brain tissue. The **gamma knife unit** is one of
three common modalities (the others being heavy charged particle beams and
high-energy photon beams from linear accelerators). It irradiates through a heavy
helmet using **201 cobalt-60 sources** whose beams simultaneously intersect at a
single **isocenter**, producing an approximately **spherical dose distribution**
at the effective dose level. Delivering dose by irradiating one isocenter is
termed a **shot**, and each shot can be represented as a **sphere**. Four
interchangeable outer collimators with beam-channel diameters of **4, 8, 14, and
18 mm** let the planner irradiate different size volumes, and a target larger than
one shot is covered by **multiple shots** (in practice **1 to 15**). The target
volume itself is described as a bounded **three-dimensional digital image**
typically containing millions of points.

The problem's modeling charge is explicit and twofold:

1. **Formulate** the optimal gamma-knife treatment planning problem **as a
   sphere-packing problem** — i.e., express the clinical and dosimetric goals and
   the physical constraints of the gamma unit in the vocabulary of packing spheres
   inside a bounded 3D region.
2. **Propose an algorithm** to find a solution, keeping in mind that the algorithm
   **must be reasonably efficient** given the multi-million-voxel scale of the
   target image.

The radiosurgery plan must reconcile six general dose-planning aims (minimize dose
gradient across the target; match specified isodose contours to target volumes;
match dose–volume constraints of target and critical organs; minimize integral
dose to normal tissue; keep dose at specified normal-tissue points below
tolerance; minimize the maximum dose to critical volumes) with **four hard
gamma-unit planning constraints**: shots must **not protrude outside the target**;
shots must **not overlap** (to avoid hot spots); the target must be covered as much
as possible with **at least 90%** of the target volume covered by shots; and **as
few shots as possible** should be used.

**Data note (preserved from the native problem definition).** For this run the
staged dataset is **empty** — `dataset_path` is `[]` and `dataset_description` /
`variable_description` are `{}` — and the workspace `data/` directory contains no
files. The planning approach therefore must be **geometry- and
parameter-driven**, with a clearly specified interface for ingesting a target
image (voxel mask) should one become available in a later round, plus a synthetic
phantom generator to exercise the algorithm during development. This is treated
as a first-class constraint of the plan (Section 4), not as a hidden gap.

**Restatement of the core modeling question.** Given a bounded 3D target region
(represented as a voxel mask or an equivalent analytic geometry) and a finite set
of admissible shot radii derived from the four collimator sizes, select a set of
**non-protruding, mutually non-overlapping** spherical shots, of **minimum (or near
minimum) cardinality**, whose union covers **at least 90%** of the target volume,
while controlling dosimetric quality (dose gradient, isodose conformity, integral
dose, and critical-structure dose) as far as the sphere abstraction permits — and
do so with an algorithm that remains **computationally tractable** on
million-voxel inputs.

---

## 2. Objectives and Subproblems

### 2.1 Overarching objectives
- **O1 (Representation).** Define a rigorous, computationally usable geometric
  representation of the target volume and of the critical structures, suitable for
  voxel data of the stated scale.
- **O2 (Formulation as sphere packing).** Formalize the gamma-knife planning
  problem as a constrained sphere-packing / covering program, making the four hard
  constraints and the six dosimetric aims precise.
- **O3 (Multi-objective / dosimetric layer).** Specify how the six dose-planning
  requirements are expressed as objectives (or constraints) on top of the
  geometric packing core, and how the resulting multi-objective problem should be
  handled.
- **O4 (Algorithm).** Propose a solution algorithm for the sphere-packing
  formulation that respects the constraints and returns a valid, near-minimal shot
  set.
- **O5 (Efficiency / scalability).** Ensure the algorithm is "reasonably
  efficient," i.e., avoids quadratic or worse dependence on the number of voxels
  where possible, and scales to the multi-million-voxel regime.
- **O6 (Verification).** Define how a produced plan is checked for feasibility
  (non-protrusion, non-overlap, coverage) and how near-optimality is assessed.

### 2.2 Subproblems
| ID | Modeling subproblem | Primary output (future) |
|----|---------------------|--------------------------|
| S1 | Target/geometry preprocessing and mask representation | Canonical voxel mask + derived geometric descriptors |
| S2 | Shot geometry and dose-sphere abstraction (radii set, effective dose sphere) | Shot model definition |
| S3 | Covering formulation (union-of-balls coverage ≥ 90%, fewest shots) | Set-cover / covering program |
| S4 | Non-protrusion and non-overlap constraint modeling | Constraint encoding + feasibility-checking rules |
| S5 | Dosimetric multi-objective layer (six aims) | Multi-objective model and trade-off structure |
| S6 | Solution algorithm design (candidate generation + selection + refinement) | Algorithm specification + complexity analysis |
| S7 | Efficiency engineering on voxel-scale data | Data structures + complexity targets |
| S8 | Validation, sensitivity, and plan-quality assessment | Evaluation harness + metrics |

### 2.3 Deliverable artifacts (planned)
- A **geometry/representation module** (mask ingestion, descriptors, distance
  transforms).
- A **packing/covering optimizer** (formulation + algorithm) with a feasibility
  checker.
- A **dosimetric evaluation layer** mapping a shot set to dose-quality metrics.
- A **synthetic phantom suite** for algorithm development in the absence of staged
  data.
- A **validation report** (feasibility, coverage, shot count, runtime) and an
  **efficiency analysis**.

### 2.4 Dependencies between subproblems
S1 underpins everything; S2 fixes the primitives used by S3–S5; S3 and S4 are
coupled (coverage and non-overlap are in tension); S6 consumes S2–S5; S7
constrains every algorithmic choice; S8 closes the loop by feeding quality and
runtime evidence back into S6.

---

## 3. Assumptions

Each assumption is stated with a justification and a planned validation route.
Final numeric values are to be set only during modeling.

### 3.1 Geometric / target assumptions
- **A1 — Target is a bounded 3D binary voxel mask.** The target volume will be
  represented as an occupancy grid over a regular lattice (with optional
  anisotropic spacing), consistent with "a bounded, three-dimensional digital
  image." *Justification:* native problem definition of the target.
  *Validation:* verify representation invariance to lattice resolution (Section
  7).
- **A2 — Critical structures are similarly representable as masks or point sets.**
  Normal-tissue and critical-organ constraints will be modeled as separate regions
  or as individually constrained points. *Justification:* the six dose aims
  reference "critical organ" and "specified normal tissue points."
  *Validation:* confirm that mask-derived constraints reproduce stated point
  constraints in simple tests.
- **A3 — Voxel→volume conversion is exact under the mask model.** Coverage will be
  measured in voxel counts (volumetric fraction), with physical volume obtained by
  a uniform scale factor. *Justification:* coverage is defined as a volume
  fraction. *Validation:* resolution-refinement study.
- **A4 — The target is connected / treatable by a single shot family.** The plan
  assumes a single contiguous target; disconnected or multi-focal targets are
  treated as an extension. *Validation:* connectivity analysis of the mask.

### 3.2 Shot / dose-sphere assumptions
- **A5 — A shot is an idealized closed ball.** Each shot is modeled as a sphere of
  radius r ∈ R with center at the isocenter, where R is the admissible radius set
  implied by the 4/8/14/18 mm collimators. *Justification:* the problem states
  shots "can be represented as different spheres." *Validation:* compare the
  idealized ball against a plateau/Gaussian dose kernel in the dosimetric layer.
- **A6 — The admissible radius set is a small discrete set.** Only the collimator-
  derived radii (and possibly their effective-dose equivalents) are allowed, so
  radius is a categorical decision variable. *Validation:* sensitivity to the
  radius mapping used (channel diameter vs. effective isodose radius).
- **A7 — Dose at the isocenter is treated as the reference "effective dose"
  level.** The sphere abstraction represents the effective-dose region; fine
  isodose shaping is handled only in the optional dosimetric layer.
  *Justification:* the problem's own sphere approximation.
  *Validation:* check with an isodose-simulation extension.
- **A8 — Shots are additively combined in dose (for the dosimetric layer).** Under
  the optional dose model, the total dose is the superposition of shot kernels.
  *Validation:* confirm additive behavior in the kernel model against stated
  isodose-matching logic.

### 3.3 Constraint-interpretation assumptions
- **A9 — Coverage constraint.** "At least 90% of the target volume" will be
  enforced as a hard coverage inequality over the voxel mask. *Validation:*
  coverage recomputation from the union of balls.
- **A10 — Non-protrusion constraint.** "Shots may not protrude outside the target"
  will be enforced, in the strict reading, as full containment of each ball in the
  target. Because irregular targets make strict containment plus 90% coverage
  jointly hard, the plan will carry **two variants**: (i) strict containment, and
  (ii) a relaxed "protrusion budget" (bounded spill outside the target, subject to
  a normal-tissue penalty). *Justification:* the stated constraint plus its
  geometric tension with coverage. *Validation:* compare both variants on coverage,
  shot count, and spill.
- **A11 — Non-overlap constraint.** "Shots may not overlap" will be enforced, in
  the strict reading, as pairwise disjoint balls; a **relaxed variant** allows
  bounded overlap (hot-spot budget). *Justification:* strict disjointness again
  competes with coverage on non-spherical targets. *Validation:* hot-spot volume
  analysis under the relaxed variant, with the dosimetric layer.
- **A12 — Shot-count economy.** Minimizing the number of shots is treated as the
  primary geometric objective, with a practical cap (the stated "1 to 15 shots"
  range informing plausible solution size and search bounds).
  *Validation:* compare returned shot counts against analytic lower bounds.

### 3.4 Algorithmic / scale assumptions
- **A13 — Millions of voxels require sub-quadratic methods.** Distance transforms,
  integral volumes, octrees/k-d trees, and vectorized array operations will be
  preferred over pairwise voxel–shot tests. *Validation:* runtime scaling
  experiments (Section 7).
- **A14 — Continuous isocenter placement is approximated by a candidate set.**
  Candidate centers will be restricted to a geometric skeleton / medial-axis or a
  resolution-controlled lattice, then refined continuously. *Justification:*
  tractability of the combinatorial core. *Validation:* compare candidate-density
  levels against achieved coverage and shot count.
- **A15 — The dose "gradient" aims are secondary to the packing core.** Because the
  sphere model already imposes sharp spherical falloff, dose-gradient and
  integral-dose aims will be handled as a post-hoc evaluation / tie-breaking
  layer rather than baked into the primary packing objective. *Validation:* assess
  the gap between the geometric plan and a refined dosimetric plan.

Any assumption whose value materially changes the recommended shot set will be
escalated to a **critical-assumption register** and subjected to explicit
sensitivity testing (Section 7).

---

## 4. Data Processing Plan

### 4.1 Inputs available now
- **None staged.** `dataset_path` is empty, `dataset_description` and
  `variable_description` are empty objects, and the workspace `data/` directory is
  empty. There is no target-image file, no label map, and no dosimetric parameter
  table attached to this run.

### 4.2 Planned handling of the absent dataset
Because the native problem is defined over a "three-dimensional digital image,"
the plan specifies a **data abstraction** rather than assuming a concrete file:

1. **Canonical input contract.** Define a single target-volume interface that
   accepts either (a) a 3D occupancy array (`.npy` / `.npz` / raw binary), (b) a
   DICOM/NIfTI-style image + segmentation pair (future), or (c) an analytic
   geometry (sphere, ellipsoid, union of primitives). All downstream modules
   consume this abstraction.
2. **Synthetic phantom generator (development only).** Provide parameterized test
   targets (solid sphere, ellipsoid, lobulated/clustered blob, shape-with-cavity,
   and thin-shell cases) plus optional critical-structure phantoms, so the packing
   algorithm can be developed, exercised, and stress-tested without staged data.
   These phantoms are **algorithm test fixtures, not problem answers**.
3. **Parameter register.** All uncertain scalars (voxel spacing, admissible radius
   mapping, coverage threshold, overlap/protrusion tolerances, shot cap) become
   explicit, documented inputs with defaults, enabling the pipeline to be re-run
   unchanged once a real target image is supplied.

### 4.3 Planned preprocessing (future modeling stage)
1. **Ingest & validate** the target image; verify dimensions, spacing, orientation,
   and bit depth; check for empty or degenerate masks.
2. **Segmentation / binarization** into a target mask (with an assumed or supplied
   threshold), plus separation of critical-structure masks.
3. **Morphological conditioning** (fill internal holes, remove specks, smooth
   boundary) — recorded explicitly as a documented, reversible step so its effect
   on coverage and containment can be tested.
4. **Voxelization / resampling** to a canonical lattice; record spacing for
   physical-volume conversion.
5. **Connectivity & component analysis** to confirm the single-target assumption
   (A4) and flag multi-focal cases.
6. **Derived geometry**: bounding box, centroid, principal axes (PCA), surface area
   estimate, volume, and a **distance transform** (distance from each target voxel
   to the nearest non-target voxel) — the central quantity for maximal-inscribed-
   sphere reasoning.
7. **Reproducibility:** fixed seeds for any stochastic step; record the exact
   input contract and parameter set for each run.

### 4.4 Feature / abstraction construction
- **Shape scale features:** equivalent-sphere radius, elongation/topology measures
  from PCA eigenvalues.
- **Maximal-inscribed-sphere field:** from the distance transform, the local maxima
  define candidate shot centers and admissible radii — the geometric backbone for
  candidate generation.
- **Skeleton / medial-axis:** a reduced-dimension representation of the target's
  "spine" used to order and place shots along the shape.
- **Reachability/coverage fields:** for a given radius, the region coverable by a
  ball centered at each voxel, used to score candidate centers.
- **Critical-structure proximity fields:** distance of each candidate center to
  critical regions, used in the dosimetric/penalty layer.

### 4.5 Data usage strategy
Since no dataset is staged, the data plan is **contract-first and
fixture-driven**: the pipeline is built against the canonical contract (4.2) and
exercised on synthetic phantoms, and any real voxel image supplied later flows
through the same preprocessing without code changes. No data will be imputed
silently; every assumed value will be tagged, defaulted, and swept.

---

## 5. Candidate Model Framework

Multiple candidate formulations will be considered, benchmarked, and possibly
combined. Selection criteria: fidelity to the stated constraints, geometric
interpretability, tractability at voxel scale, and clean extensibility to the
dosimetric layer.

### 5.1 Core geometric object
Let the target be a bounded region **T ⊂ R³** (voxel mask, or its geometric
closure). A **shot** is a closed ball **B(c, r)** with center **c** (isocenter)
and radius **r ∈ R = {r₁, …, r_K}** from the collimator-derived admissible set
(A5–A6). A **plan** is a finite collection of shots **P = {(cᵢ, rᵢ)}**. The
coverage of the plan is the volume fraction of T covered by the union ∪ᵢ B(cᵢ, rᵢ),
and the plan's quality is judged against the four hard constraints and six dose
aims.

- **Decision variables:** number of shots N; center coordinates cᵢ ∈ R³; radius
  class rᵢ ∈ R. (Optionally, per-shot "on/off" or weighting in the dosimetric
  layer.)
- **Derived quantities (definitions, not computed here):** covered volume,
  uncovered volume, protrusion (spill) volume, overlap (hot-spot) volume, dose
  field (if the kernel layer is used).

### 5.2 Candidate model families

**M1 — Discrete set-cover / covering ILP.**
Discretize candidate centers to a finite set (lattice, medial-axis points, or
distance-transform maxima) and candidate radii to the collimator set. Let binary
**x_{j,k} = 1** iff a shot of radius class k is placed at candidate j. Subject to
(a) each target voxel must be covered by at least one selected shot, or (b) a
relaxed covering with a 90%-coverage constraint; (c) pairwise conflict constraints
for non-overlap; (d) containment predicates for non-protrusion. Objective:
minimize Σ x_{j,k} (fewest shots). *Advantages:* exact combinatorial core, standard
solvers, directly encodes coverage and shot-count. *Limitations:* candidate
discretization limits optimality; pairwise non-overlap constraints can explode;
containment must be precomputed per candidate.

**M2 — Continuous nonconvex sphere packing.**
Treat centers as continuous variables and minimize shot count (or a smooth proxy)
subject to coverage, containment, and non-overlap. *Advantages:* no discretization
bias; better radii/placement. *Limitations:* nonconvex, nonsmooth (union-of-balls),
needs good initialization and local search.

**M3 — Greedy maximal-inscribed-sphere covering (constructive).**
Use the distance transform / medial axis to place the largest admissible shot at
the deepest unresolved point, mark covered voxels, and iterate until coverage
threshold met — with conflict checks against containment and overlap.
*Advantages:* very fast, naturally respects non-protrusion (centers lie where a
full ball fits), produces intuitive plans. *Limitations:* greedy, not optimal in
shot count; may need post-refinement.

**M4 — Set-cover heuristic over an over-complete candidate pool (lazy greedy /
primal–dual).**
Generate many candidate shots (multi-radii, medial-axis seeds), then select a
small subset to cover ≥90% of the target, using submodularity (coverage is
monotone submodular) to justify greedy/lazy-greedy near-optimality guarantees.
*Advantages:* near-optimal coverage with strong efficiency; submodular bound gives
a principled quality statement. *Limitations:* still subject to candidate pool
richness.

**M5 — Local-search / metaheuristic refinement (SA, GA, tabu, basin-hopping).**
Start from M3/M4's solution and improve shot count and constraint satisfaction by
moving/deleting/upsizing shots. *Advantages:* escapes greedy local optima.
*Limitations:* needs efficiency guards on voxel-scale evaluation.

**M6 — Dosimetric overlay model (secondary).**
Replace/adorn the geometric union with additive shot dose kernels (e.g., a
plateau/Gaussian or a fitted spherical falloff) to evaluate isodose conformity,
dose gradient, integral dose, and critical-structure dose; used for evaluation and
tie-breaking, and (optionally) as a penalty in M2/M5. *Advantages:* connects the
packing solution to the six clinical aims. *Limitations:* requires kernel
parameters not staged with this run.

**M7 — Multi-objective formulation.**
Cast the six dose aims plus the shot-count objective into a multi-objective
program, then handle via weighted-sum, ε-constraint, or Pareto-front exploration,
producing a trade-off family (e.g., coverage vs. shot count vs. spill) rather than
one point. *Advantages:* matches the clinical reality that "optimal" is a
trade-off. *Limitations:* larger solution effort; needs stakeholder weighting.

### 5.3 Shared variable / parameter vocabulary (to be finalized)
- **Decision variables:** N (shot count); for each shot i: center cᵢ, radius class
  rᵢ; optional dose weights wᵢ.
- **Parameters:** voxel spacing; admissible radius set R; coverage threshold
  (0.90); protrusion/overlap tolerances (variant-dependent); shot cap; kernel
  parameters (dosimetric layer); critical-structure tolerance doses.
- **Outputs:** the selected shot set; coverage fraction; spill and hot-spot
  volumes; shot count; dosimetric metrics; runtime.

### 5.4 Advantages / limitations summary
The framework deliberately pairs a **fast constructive core** (M3, M4) with an
**exact/optimization core** (M1, M2) and a **realism/quality layer** (M5–M7). This
staged structure lets the modeling team produce a valid plan quickly, then harden
it toward lower shot counts and better dosimetric conformity — while keeping the
"reasonably efficient" mandate in view throughout.

---

## 6. Implementation Roadmap

Planned workflow (no code is written in this drafting phase):

1. **Stage 0 — Contract & assumption lock.** Freeze the canonical input contract
   (4.2), the parameter register, and the critical-assumption list; record default
   values and their sources.
2. **Stage 1 — Geometry layer.** Implement mask ingestion, validation, morphological
   conditioning, connectivity analysis, and derived geometry including the distance
   transform and medial-axis extraction.
3. **Stage 2 — Shot model.** Encode the admissible radius set and the
   containment/overlap/coverage predicates, plus fast unions-of-balls coverage
   accounting (integral volumes / vectorized boolean grids).
4. **Stage 3 — Constructive baseline.** Implement M3 (greedy maximal-inscribed-
   sphere covering) and report baseline coverage, shot count, spill, hot spots.
5. **Stage 4 — Anti-greedy covering.** Implement M4 (lazy-greedy / primal–dual
   set cover) over a rich candidate pool; compare against M3.
6. **Stage 5 — Optimization core.** Implement M1 (discrete covering ILP) and M2
   (continuous packing/local search) to reduce shot count and tighten feasibility.
7. **Stage 6 — Refinement.** Add M5 local-search/metaheuristic polish with
   efficiency guards; support both strict and relaxed constraint variants
   (A10–A11).
8. **Stage 7 — Dosimetric layer.** Add M6 kernel-based evaluation and M7
   multi-objective trade-off exploration; produce coverage–shotcount–spill
   trade-off curves.
9. **Stage 8 — Efficiency & validation.** Run resolution/scaling experiments,
   feasibility audits, and the sensitivity suite (Section 7); assemble the
   validation report.

### 6.1 Required modules (planned)
- `geometry_loader` (contract-based mask ingestion + validation)
- `phantom_generator` (synthetic development fixtures)
- `shape_features` (PCA, volume, distance transform, medial axis)
- `shot_model` (radii set, containment/overlap/coverage predicates)
- `coverage_engine` (union-of-balls accounting; integral-volume accelerated)
- `packing_greedy` (M3)
- `setcover_solver` (M4; optional M1 ILP interface)
- `packing_refiner` (M2/M5 continuous + metaheuristic)
- `dose_layer` (M6 kernels + M7 multi-objective harness)
- `feasibility_checker` (independent constraint audit)
- `sensitivity` (parameter sweeps + resolution studies)
- `reporting` (metrics tables, trade-off curves, runtime scaling)

### 6.2 Engineering conventions
- Config-driven parameters (YAML/JSON) separated from logic.
- Reproducible seeds; run metadata captured alongside outputs.
- Independent feasibility checker (never reuse the optimizer's internal
  predicates for the final audit).
- Outputs routed to `results/`; generated code and intermediate artifacts to
  `code/` and `logs/` (directories already present in the workspace).

---

## 7. Validation Strategy

### 7.1 Internal consistency checks
- **Definition/dimensional checks:** confirm coverage is a volume fraction in
  [0,1], spill and hot-spot volumes are non-negative, and radius units match the
  collimator-derived set.
- **Independent feasibility audit:** re-verify non-protrusion, non-overlap, and
  coverage with a checker implemented separately from the optimizer.
- **Boundary checks:** behavior at extreme parameters (single radius class, zero
  overlap tolerance, maximum coverage cap) should be monotone and interpretable.
- **Baseline cross-validation:** compare the optimization core (M1/M2) against the
  constructive baselines (M3/M4); a large gap signals either a modeling error or a
  genuinely binding constraint and must be explained.

### 7.2 Analytic / geometric ground truth
- On **analytic targets** (solid sphere, ellipsoid), compare algorithmic output
  against known packing/covering bounds (e.g., best single-shot fit, analytic
  covering numbers for simple shapes) to calibrate correctness and near-optimality.
- **Resolution-refinement study:** verify that coverage and shot count stabilize as
  the lattice is refined (A3), and quantify discretization error.

### 7.3 Robustness & uncertainty
- **One-at-a-time sensitivity** on coverage threshold, admissible radius mapping,
  overlap/protrusion tolerances, and voxel spacing.
- **Variant comparison:** strict vs. relaxed non-protrusion and non-overlap
  variants, evaluated on coverage, shot count, spill, and hot-spot volume.
- **Shape robustness:** run across the synthetic phantom suite (convex, elongated,
  lobulated, cavitated) to expose shape-dependent failure modes.
- **Global sensitivity:** factorial / Monte-Carlo screening over the parameter
  register to identify which assumptions dominate the solution.

### 7.4 Evaluation metrics (to be computed later)
- **Feasibility:** violation counts for containment, overlap, and coverage.
- **Efficiency:** wall-clock runtime and its scaling with voxel count and candidate
  density.
- **Geometry quality:** coverage fraction; number of shots; uncovered/target
  volume; spill volume; hot-spot volume.
- **Dosimetric (optional layer):** isodose conformity index, dose-gradient
  descriptors, integral dose, critical-structure dose metrics.

### 7.5 Algorithmic-claims validation
- Verify the "efficient" claim by measuring runtime vs. image size and vs.
  candidate-pool size, and by demonstrating the intended sub-quadratic behavior
  where claimed (A13).
- Verify near-optimality claims against the M4 submodular bound and against
  analytic lower bounds on shot count.

---

## 8. Expected Result Interpretation

This section describes how future outputs would be *interpreted*, not any actual
findings.

- **Shot set.** The optimizer will propose a collection of spheres with specified
  centers and radii; interpretation should read it jointly with coverage, spill,
  and hot-spot metrics, and with which constraints are binding. A plan whose
  quality is highly sensitive to the coverage-threshold or radius-mapping choice
  should be reported with ranges rather than a single shot list.
- **Coverage vs. shot-count trade-off.** Results are expected to lie on a
  trade-off frontier: more shots (and smaller radii) tend to raise coverage and
  conformity while risking overlap; fewer shots ease the non-overlap constraint but
  may undershoot 90% coverage. The interpretation will present this frontier
  explicitly rather than a single "answer."
- **Constraint tension.** Because non-protrusion and non-overlap can conflict with
  90% coverage on irregular targets, a result should report **which constraints
  were relaxed and by how much**, and how the relaxed plan compares to the strict
  variant.
- **Dosimetric overlay.** If the kernel layer is used, results should be read as
  "how closely a packing solution approaches the six clinical aims," with
  conformity and gradient metrics rather than as a certified plan.
- **Efficiency.** Runtime and its scaling directly address the problem's
  "reasonably efficient" requirement; the interpretation will state the practical
  input-size envelope the algorithm supports.

A recurring interpretive theme: the problem is fundamentally **multi-objective and
constraint-tensioned** — so results should be reported as a validated trade-off
family with explicit relaxation labels, not as a single point claim.

---

## 9. Limitations and Improvements

### 9.1 Known limitations of the planned approach
- **No staged dataset.** The target image is absent for this run; the plan must
  proceed on synthetic phantoms and an input contract, so absolute geometric
  conclusions cannot be made and are deferred until real data (or a specified
  analytic target) is supplied.
- **Sphere idealization.** Representing shots as exact balls ignores real isodose
  shape, penumbra, and beam-channel specifics, so pure packing under-models the six
  dose aims.
- **Constraint tension handled only approximately.** Strict non-protrusion plus
  strict non-overlap plus 90% coverage can be infeasible for irregular targets; the
  relaxed variants introduce tuning parameters whose effect must be characterized.
- **Discretization error.** Candidate-center and lattice choices bound achievable
  optimality; this must be quantified, not assumed negligible.
- **Dosimetric parameters not staged.** Kernel-based evaluation depends on
  parameters not provided with this run, limiting the rigor of the dose layer.

### 9.2 Planned improvements / extensions
- Ingest a real target image (or an explicitly specified analytic geometry) and
  re-run the pipeline unchanged via the canonical contract.
- Replace the ball abstraction with a fitted dose kernel per collimator size and
  re-optimize for isodose conformity and gradient.
- Add explicit re-optimization under critical-structure dose constraints (dose–
  volume constraints) rather than post-hoc evaluation.
- Strengthen the combinatorial core with branch-and-bound / column-generation
  covering to close the gap to the M4 bound.
- Develop a proper Pareto-front explorer and reporting format for the
  multi-objective family.
- Extend to multi-focal / disconnected targets and to shape-selective planning
  (beam weighting / plugging) as a later refinement.
- Formalize a global sensitivity analysis over the full parameter register.

### 9.3 Open questions to resolve before modeling
- What exact target representation will be used if a real image is supplied
  (modality, spacing, segmentation provenance)?
- What is the precise mapping from collimator channel diameter to effective shot
  radius?
- Should "no overlap" be strict disjointness or a bounded hot-spot budget, and who
  sets that budget?
- Is strict non-protrusion required, or is a bounded spill with normal-tissue
  penalty acceptable clinically?
- What target-size regime must the algorithm support (the "1 to 15 shots" /
  million-voxel envelope), and what runtime is "reasonably efficient"?
- Which of the six dose aims are hard constraints versus soft objectives?

---

*End of modeling blueprint draft. No analysis, computation, or results are
included by design; all quantitative work is deferred to the future modeling
stage.*
