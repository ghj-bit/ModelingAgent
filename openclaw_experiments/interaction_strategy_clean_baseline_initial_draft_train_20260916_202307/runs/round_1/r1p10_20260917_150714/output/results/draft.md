# Modeling Blueprint Draft
## Positioning and Moving Sprinkler Systems for Irrigation
**Problem ID:** 2006_Positioning_and_Moving · **Source:** MCM 2006

> This document is an **initial modeling plan draft**. It defines a roadmap for future modeling work only. It contains no solved results, no data analysis, no fitted parameters, and no final conclusions. All statements are prospective and intended to guide the later solution phase.

---

## 1. Problem Background and Restatement

### 1.1 Background
Irrigation of fields can be performed through a spectrum of technologies, from advanced drip systems to periodic flooding. On smaller ranches, a cheaper and more flexible option is a **"hand move" sprinkler system**: lightweight aluminum pipes fitted with sprinkler heads are laid across the field and must be manually relocated at regular intervals so that the whole field receives adequate water. The trade-off is that moving and re-setting the equipment demands substantial time and labor.

### 1.2 Restatement (Planning Level)
Given a rectangular field of **80 m × 30 m**, a single hand-move pipe set, and a fixed water supply (pressure 420 kPa, flow rate 150 L/min), the future model should determine:

- the **number of sprinkler heads** to fit on the pipe set,
- the **spacing between sprinklers** along the pipe,
- a **move schedule** — specifically how many positions the pipe set occupies and where each position is,
- such that the **total irrigation time (labor/move time)** is minimized while meeting water-depth constraints.

### 1.3 Physical System Description (as given)
- Pipelines: 10 cm inner diameter; spray nozzles: 0.6 cm inner diameter (rotating).
- A full assembled pipe set is **20 m long** (one set of connectable straight pipes).
- Source: **420 kPa** pressure, **150 L/min** flow rate.
- Coverage constraints (to be respected, not evaluated here):
  - no point may receive **more than 0.75 cm/hour**,
  - every point must receive **at least 2 cm every 4 days**,
  - application should be **as uniform as possible**.

### 1.4 Scope of the Draft
This draft establishes the modeling workflow, assumptions, candidate methods, data-processing plan, implementation plan, and validation strategy. It deliberately stops short of execution.

---

## 2. Objectives and Subproblems

### 2.1 Primary Objective
Formulate an **algorithm** that determines a sprinkler configuration and a move schedule which **minimizes the rancher's total labor/move time** required to irrigate the 80 m × 30 m field with one hand-move pipe set.

### 2.2 Secondary Objectives
- Respect the maximum application rate (≤ 0.75 cm/h) at every point.
- Satisfy the minimum cumulative depth (≥ 2 cm per 4 days) at every point.
- Maximize **spatial and temporal uniformity** of applied water.

### 2.3 Subproblems (Decomposition)
1. **Hydraulics / emission subproblem** — Characterize, at the planning level, how nozzle spacing and system pressure/flow relate to per-head discharge and coverage radius (to be derived, not computed here).
2. **Coverage geometry subproblem** — Model each sprinkler's wetted footprint and how overlapping footprints from multiple heads on a 20 m line combine into a coverage strip.
3. **Layout subproblem** — Choose number of heads, head spacing, and the set of pipe-set positions (translations) across the field.
4. **Scheduling subproblem** — Choose dwell time per position and the order/sequence of moves to achieve depth targets within the 4-day window.
5. **Optimization subproblem** — Combine geometry, hydraulics, and scheduling into a single objective (move time) with the water constraints as feasibility conditions.
6. **Algorithmic-communication subproblem** — Express the final approach as a clear, reproducible algorithm the rancher could follow.

### 2.4 Deliverables (Future)
- A formal model describing coverage, discharge, and depth accumulation.
- A move schedule (positions + dwell times) obtained from the optimization.
- A general algorithm/pseudocode generalizing beyond this specific field.
- Validation evidence and sensitivity discussion.

---

## 3. Assumptions

Each assumption is paired with a justification and a planned future validation approach. These are **working assumptions** to be revisited during modeling.

### 3.1 Physical / Hydraulic Assumptions
| # | Assumption | Justification | Planned Validation |
|---|-----------|---------------|--------------------|
| A1 | Sprinklers are identical and evenly spaced along the pipe set | Simplifies geometry; standard hand-move practice | Compare even vs. optimized non-uniform spacing in sensitivity runs |
| A2 | The pipe set is straight and spans 20 m; it may be repositioned by translation (and optionally rotation) | Matches the "straight line" description | Test rotation-enabled variant against translation-only baseline |
| A3 | Per-head discharge is governed by a standard orifice model driven by available pressure/flow | Orifice flow is standard for nozzle emission | Compare against manufacturer-style discharge-vs-pressure curves if data obtainable |
| A4 | Pressure losses along the pipe (friction, elevation) are either negligible or modeled with a simple friction relation | Field is short (20 m) and roughly level | Compare negligible-loss vs. Hazen–Williams/Darcy friction variants |
| A5 | The supply is a fixed total flow (150 L/min) that is divided among heads | Given constraint | Check consistency if number of heads changes emission per head |
| A6 | Coverage footprint of each head is circular (possibly with a radial intensity profile) | Standard sprinkler model | Test uniform-disk vs. triangular/wedge radial profiles |
| A7 | Water infiltrates without runoff; depth accumulates independently of rate over the tolerated range | Required to use additive depth accounting | Sensitivity to reduced infiltration in the max-rate regime |
| A8 | Wind, evaporation, and crop-specific demand are ignored at this stage | Data not provided | Discuss as extension / robustness scenario |

### 3.2 Modeling Assumptions
| # | Assumption | Justification | Planned Validation |
|---|-----------|---------------|--------------------|
| B1 | The field is homogeneous (same crop/soil throughout) | No zoning data given | Test zoned variants |
| B2 | Move time is dominated by a per-move setup cost; travel geometry is second-order | Problem emphasis on "time to move and set up" | Compare constant per-move cost vs. distance-proportional cost |
| B3 | Dwell time per position is a continuous decision variable | Enables continuous optimization | Compare against discrete switching schedules |
| B4 | Boundary/surplus over-application outside the field is not penalized (only in-field uniformity matters) | Field is the region of interest | Test with edge-clipping penalty variants |
| B5 | The 4-day requirement is treated as a rolling/cyclic constraint over irrigation cycles | Matches agronomic intent | Compare single-cycle vs. multi-cycle horizons |

### 3.3 Assumption-Handling Strategy
- Record all assumptions in a **single registry** with IDs (as above) so sensitivity analysis can toggle them systematically.
- Flag any assumption whose relaxation changes the optimal configuration qualitatively.

---

## 4. Data Processing Plan

> The problem is largely **analytically specified** (geometry, diameters, pressure, flow). The "data" primarily comprises derived quantities and any external references. No data will be analyzed or transformed in this planning phase.

### 4.1 Data Sources and Roles
1. **Given problem parameters** — field dimensions, pipe/nozzle diameters, pipe length, pressure, flow rate, depth limits. Role: model constants/constraints.
2. **Derived hydrodynamic quantities** — per-head discharge, coverage radius, application intensity profile. Role: computed in the modeling phase from physics relations.
3. **Optional external references** — standard sprinkler discharge/coverage tables, friction-loss coefficients. Role: calibrating functional forms of A3/A4.

### 4.2 Preprocessing Plan (Future)
- **Unit standardization:** express all lengths in meters, time in hours/days, volumes in liters, depths in cm; maintain a single unit-conversion layer.
- **Parameter table construction:** assemble a machine-readable constants table (field, pipe, nozzle, source) for the future solver.
- **Constraint normalization:** express the max-rate and min-depth constraints per unit area and per time window.

### 4.3 Feature / Quantity Construction (Future)
- **Coverage-intensity function** `I(r)` per head (candidate forms: uniform disk, linear/triangular decay, Gaussian-like).
- **Superposition map**: aggregated intensity at each field point from all active heads at a given position.
- **Depth-accumulation map**: integral of intensity over dwell time per position, summed over the schedule.
- **Uniformity descriptors**: planned uniformity metrics (e.g., Christiansen's uniformity coefficient, distribution uniformity) to be computed later.

### 4.4 Data Usage Strategy
- Use given constants directly as constraints/inputs; treat derived quantities as model outputs.
- Keep external references optional and clearly separated so the model can degrade gracefully to first-principles if unreferenced.
- Define a **spatial discretization** (grid) resolution as a tunable parameter, not a fixed fact.

---

## 5. Candidate Model Framework

### 5.1 Modeling Paradigm
A **deterministic, continuous optimization model** with a geometric coverage component and a scheduling component, embedded in a discrete search over candidate configurations.

### 5.2 Decision Variables (Candidate)
- `n` — number of sprinkler heads on the 20 m set.
- `s` — spacing between heads (subject to `(n-1)·s ≤ 20 m`).
- `{p_k}` — positions of the pipe set (translation offset, optionally angle) for each move step `k`.
- `{t_k}` — dwell time at position `k`.
- `K` — number of moves/positions.
- Possibly nozzle-orientation or partial-coverage decisions.

### 5.3 Objective Function (Candidate)
Minimize total **labor/move time**, modeled as `TotalTime = Σ_k ( move_cost + setup_cost )` plus any time attributable to repositioning distance, subject to feasibility of the water constraints. Alternative objective: minimize total number of moves subject to uniformity — to be compared.

### 5.4 Constraints
- **Max rate:** for all points `x` and all active configurations, instantaneous intensity `≤ 0.75 cm/h`.
- **Min cumulative depth:** for all points `x`, `Σ_k I_k(x)·t_k ≥ 2 cm` within each 4-day window.
- **Geometry:** heads lie on a 20 m segment; set lies within/relative to the 80 m × 30 m field.
- **Hydraulics:** total discharge `≤ 150 L/min`; per-head discharge consistent with available pressure (A3/A4).
- **Uniformity:** optional constraint or penalty on a uniformity coefficient.

### 5.5 Candidate Modeling Approaches (to be compared)
1. **Analytic coverage-strip model** — treat the 20 m line as generating an effective coverage band; derive required band width and number of passes analytically.
2. **Grid-based optimization (LP / MILP)** — discretize field into cells; solve for intensities and dwell times. Pros: handles constraints directly. Cons: scalability, discretization artifacts.
3. **Continuous geometric optimization** — optimize spacing and offsets in continuous space with coverage functions. Pros: elegance. Cons: nonconvexity.
4. **Heuristic / metaheuristic search** — simulated annealing / genetic search over (n, s, positions, dwell times). Pros: flexible with messy constraints. Cons: no optimality guarantee.
5. **Two-stage decomposition** — first determine geometric layout for feasibility, then solve a small linear program for dwell times (or vice versa).

### 5.6 Mathematical Ideas to Draw On
- Orifice flow: `Q ∝ d²√P` (functional form to be confirmed).
- Overlap/superposition of coverage intensity.
- Christiansen uniformity coefficient and related distribution-uniformity metrics.
- Linear programming for dwell-time feasibility given a fixed coverage matrix.
- Set-cover / covering-problem framing for "which positions cover the field".
- Traveling-salesperson-like sequencing if reorder distance matters.

### 5.7 Advantages and Limitations (per approach)
To be completed during modeling; each candidate will be assessed for tractability, constraint fidelity, and generalization. This draft only enumerates them for future comparison.

---

## 6. Implementation Roadmap

### 6.1 Proposed Workflow
1. **Parameter & unit module** — encode all given constants and conversions.
2. **Hydraulics module** — per-head discharge and coverage function (parameterized by A3/A4 choices).
3. **Coverage/geometry module** — compute intensity maps for candidate layouts on a discretized field.
4. **Feasibility module** — check max-rate and min-depth constraints; compute uniformity metric.
5. **Optimization module** — search over `(n, s, {p_k}, {t_k}, K)` for minimal move time.
6. **Schedule-construction module** — output the ordered move plan with positions and dwell times.
7. **Reporting module** — produce configuration, schedule, uniformity, and sensitivity summaries.
8. **Algorithm-package module** — generalize the pipeline into a reproducible algorithm/pseudocode.

### 6.2 Required Modules / Components
- Geometry & field-discretization utilities.
- Coverage-intensity model library (multiple radial profiles).
- Constraint checker.
- Optimizer driver (LP/MILP and/or metaheuristic).
- Schedule serializer (machine-readable + human-readable).
- Experiment/config harness for sensitivity sweeps.

### 6.3 Algorithmic Candidates to Implement
- Baseline: uniform grid of pipe positions with uniform dwell time (reference only; not to be evaluated here).
- LP-based dwell-time optimizer for a fixed layout.
- Metaheuristic over layout variables.
- Hybrid: metaheuristic layout + LP dwell time.

### 6.4 Engineering Practices (Future)
- Configuration-driven runs (no hard-coded constants).
- Reproducible seeds, logged parameters, versioned outputs.
- Separation of model, solver, and reporting code.

---

## 7. Validation Strategy

### 7.1 Evaluation Metrics (to be computed later)
- **Primary:** total move/labor time (objective value).
- **Constraint-satisfaction indicators:** max intensity vs. 0.75 cm/h; min cumulative depth vs. 2 cm.
- **Uniformity metrics:** Christiansen's uniformity coefficient, distribution uniformity, coefficient of variation of applied depth.
- **Coverage completeness:** fraction of field points meeting the depth target.
- **Robustness metrics:** performance spread across assumption variants.

### 7.2 Validation Methods
1. **Physical plausibility checks** — discharge and coverage must lie within realistic agricultural ranges; total volume must be consistent with flow rate × time.
2. **Constraint verification** — independent recheck of both water constraints over the scheduled plan.
3. **Cross-model comparison** — compare outputs of LP-based, geometric, and metaheuristic approaches for consistency.
4. **Discretization convergence** — refine the spatial grid and confirm the solution stabilizes.
5. **Mass-balance audit** — total applied water should reconcile with supply flow × operating time minus expected losses.
6. **Sanity baselines** — compare against simple uniform schedules as reference (differences only, not results).

### 7.3 Sensitivity Analysis Plan
- Toggle pipe-friction model (A4): negligible vs. friction-inclusive.
- Toggle coverage profile (A6): uniform disk vs. decaying profiles.
- Toggle per-move cost model (B2): constant vs. distance-proportional.
- Vary discretization resolution and dwell-time granularity.
- Vary wind/evaporation scenarios (A8) as robustness stressors.
- Vary edge-penalty treatment (B4).

### 7.4 Threats to Validity
- Over-simplified hydraulics could bias head count/spacing.
- Discretization artifacts could misstate uniformity.
- Assumption mismatch with real ranch practice could reduce practical relevance. Each threat will be mapped to a mitigation in the modeling phase.

---

## 8. Expected Result Interpretation

> Interpretation guidance only — **no results are produced in this draft.**

The future solution is expected to yield:
- A recommended **number of sprinklers** and **inter-sprinkler spacing** on the 20 m set.
- A **move schedule**: number of positions, their locations, and how long to dwell at each.
- A characterization of the **trade-off** between fewer moves (less labor, possibly lower uniformity or rate violations) and more moves (better uniformity, more time).
- A generalization: an **algorithm** parameterized by field dimensions, supply characteristics, and depth constraints, not just the 80 m × 30 m case.

Interpretation should emphasize:
- How the optimal configuration balances rate limits (upper bound) against depth requirements (lower bound).
- Whether the binding constraint is hydraulic (flow/pressure), geometric (coverage overlap), or labor (number of moves).
- The practical usability of the schedule for an actual rancher (few moves, clear positions).

---

## 9. Limitations and Improvements

### 9.1 Anticipated Limitations
- Idealized hydraulics and coverage profiles may not capture real sprinkler behavior.
- Wind, evaporation, soil heterogeneity, and crop water demand are out of scope at this stage.
- Uniformity and labor-time cost models are simplified.
- Grid-based methods introduce discretization error; continuous methods may be nonconvex and locally optimal.

### 9.2 Planned Improvements / Extensions
- Incorporate empirical sprinkler discharge/coverage data if available.
- Add time-varying wind/evaporation and a soil-infiltration model.
- Extend from translation-only to rotation/tilt of the pipe set.
- Multi-cycle scheduling over longer horizons with rotation of wetting patterns.
- Formal proof or bounds of optimality for restricted model classes.
- Generalize the algorithm and test on non-rectangular or larger fields.
- Compare against alternative irrigation technologies as a benchmark (drip, flooding) for context.

### 9.3 Open Questions to Resolve in the Modeling Phase
- Is translation-only sufficient, or does rotation materially reduce move time?
- Is a single pipe set sufficient to cover 80 m × 30 m within the stated depth window, and how many passes are needed?
- Which constraint binds first — max rate, min depth, or hydraulic supply?
- How sensitive is the optimal configuration to the assumed coverage profile?

---

*End of initial modeling plan draft. This document is a roadmap; execution, computation, and results are deferred to the subsequent modeling phase.*
