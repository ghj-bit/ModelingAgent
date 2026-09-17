# Modeling Blueprint Draft
## The Stunt Person — Motorcycle Jump over an Elephant into a Cardboard-Box Cushion
**Problem ID:** 2003_The_Stunt_Person · **Source:** MCM 2003

> This document is an **initial modeling plan draft**. It defines a roadmap for future modeling work only. It contains no solved results, no data analysis, no fitted parameters, no executed experiments, and no final conclusions. All statements are prospective and are intended to guide the later solution phase.

---

## 1. Problem Background and Restatement

### 1.1 Background
A movie production will film an action scene in which a **stunt person riding a motorcycle jumps over an elephant** and lands inside a **pile of cardboard boxes** that cushions the impact. The stunt coordinator (the problem's stakeholder) must design that cushion so the rider survives the landing while keeping the number of boxes — and therefore cost, setup labor, and on-camera footprint — as low as reasonable. Cardboard boxes are attractive because they are cheap, can be hidden from the camera, and crush progressively to absorb energy; but an under-built pile risks injury, while an over-built pile wastes budget and logistics.

### 1.2 Restatement (Planning Level)
The future model should determine, for a specified jump scenario:

- the **size** of the cardboard boxes to use (per-box dimensions and, likely, board grade),
- the **number** of boxes to use,
- the **stacking arrangement** (pile footprint, number of layers, interlocking of layers, possible density gradation),
- whether any **modifications to the boxes** (e.g., pre-crushing, scoring, internal baffling, partial filling, variable-density layering) would materially improve — or make more robust — the cushion,

subject to the requirement that the landing be **non-injurious** to the stunt person and that the pile be **as economical as feasible**. A further expectation is that whatever design logic is produced should **generalize** to different combined weights (rider + motorcycle) and different jump heights.

### 1.3 Physical System Description (as given)
- A **motorcycle + rider** (a combined mass that must be treated as a parameter) leaves a ramp, flies over an elephant, and arrives at the landing zone with a significant horizontal velocity component and a downward velocity component.
- The **landing surface** is a pile of **corrugated cardboard boxes** whose material is the energy-absorbing medium.
- The problem text does **not** supply numeric values for mass, speed, jump geometry, box material, or injury thresholds. These will be treated as **parameters and ranges to be specified in the modeling phase**, not as facts available now.

### 1.4 Scope of This Draft
This draft establishes the modeling workflow, assumptions, candidate methods, data-processing plan, implementation plan, and validation strategy. It deliberately stops short of execution, computation, and results.

---

## 2. Objectives and Subproblems

### 2.1 Primary Objective
Design a **cardboard-box landing cushion** (box size, count, stacking, and optional box modifications) that **protects the stunt person** from injury during the landing while **minimizing the number/cost of boxes**, for a given jump scenario.

### 2.2 Secondary Objectives
- Keep peak deceleration (or another injury index) within a tolerable envelope for the expected impact duration.
- Guarantee the rider+bike is brought to rest **before the pile bottoms out** (no rigid ground contact).
- Ensure the pile is **geometrically adequate**: tall enough, wide enough, and positioned to capture the actual landing point.
- Provide a **generalizable design rule** (or scaling law) as a function of combined mass and jump height.

### 2.3 Subproblems (Decomposition)
1. **Trajectory / landing-state subproblem** — Characterize the landing state (impact speed, its horizontal and vertical components, and contact angle) as a function of ramp geometry, launch speed, jump height, and evasive geometry over the elephant.
2. **Energy-absorption subproblem** — Relate the kinetic and potential energy at landing to the crush behavior of a box pile, so that the rider's deceleration can be bounded.
3. **Crush / structural subproblem** — Describe how a single corrugated box deforms and how its crush strength depends on its dimensions, board grade, orientation, and loading.
4. **Stack / topology subproblem** — Determine how boxes should be arranged (layers, interlocking, footprint, optional vertical density gradation) so the pile delivers a controlled, progressive crush rather than a stiff or collapsing response.
5. **Safety-criterion subproblem** — Choose and justify an injury-tolerance criterion (deceleration magnitude/duration, and/or a biomechanical index) that the design must satisfy.
6. **Optimization subproblem** — Minimize the number of boxes subject to the safety, geometric, and bottom-out constraints.
7. **Generalization / modification subproblem** — Decide whether box modifications are worthwhile and derive how the design scales with combined weight and jump height.
8. **Communication subproblem** — Express the design procedure as a reproducible rule set the stunt coordinator could apply.

### 2.4 Deliverables (Future)
- A formal model linking jump scenario → landing energy → pile crush response → rider deceleration.
- A recommended box design (size, count, stacking) for a baseline scenario.
- A scaling/generalization rule for varying mass and jump height.
- A reasoned recommendation on box modifications.
- Validation evidence and a sensitivity discussion.

---

## 3. Assumptions

Each assumption is paired with a justification and a planned future validation approach. These are **working assumptions** to be revisited during modeling.

### 3.1 Physical / Kinematic Assumptions
| # | Assumption | Justification | Planned Validation |
|---|-----------|---------------|--------------------|
| A1 | The rider+bike behaves as a single **point mass** during flight, with combined mass `m` treated as a parameter | Simplifies trajectory; dominant translation is the mass center | Compare against a two-body or rigid-body variant if data allow |
| A2 | Flight is well described by **projectile motion** with a constant gravity field and negligible air drag at the relevant speeds | Speeds and durations are short; drag is second-order | Compare with a drag-inclusive trajectory in sensitivity runs |
| A3 | The **landing angle and speed** are set by the ramp and jump geometry; the landing point is deterministic (or bounded by a small uncertainty band) | Problem implies a planned, repeatable jump | Test a landing-point uncertainty band as robustness stress |
| A4 | The **elephant clearance** constrains flight geometry and thus the achievable landing state | The jump must clear the animal | Re-derive for alternative clearance heights |
| A5 | Rotational energy, tumbling, and rider limb motion are ignored at this stage | Second-order versus translational kinetic energy | Assess as an extension; note as a limitation |

### 3.2 Impact / Crush-Response Assumptions
| # | Assumption | Justification | Planned Validation |
|---|-----------|---------------|--------------------|
| B1 | A corrugated box, when compressed top-down, exhibits an approximately **plateau crush force** over a working stroke (a progressive, near-constant-force absorber) | Corrugated board commonly shows a plateau in compression | Compare constant-force vs. linear-stiffness vs. densifying models |
| B2 | The pile can be treated as a **series/parallel arrangement of crushable layers**, where layer properties combine in a predictable way | Standard lumped-parameter idealization | Compare lumped model against a finer discrete model |
| B3 | Crush energy per box scales with box dimensions and board grade in a **power-law / dimensional** manner (to be calibrated) | Structural mechanics of corrugated compression suggests such scaling | Compare against box-compression-strength relations from packaging literature |
| B4 | The load is applied over the **pile footprint** with limited lateral spread; edge/boundary effects are second-order for a sufficiently wide pile | Pile is wide relative to impact patch | Sensitivity to pile width and edge proximity |
| B5 | Energy is absorbed primarily by **crushing** (not by elastic rebound, friction between boxes, or ground penetration) | Boxes are the designated absorber | Test with friction- and rebound-inclusive variants |
| B6 | The pile **must not bottom out**: the required stroke must be less than the available pile height | Conservative safety requirement | Enforce explicitly as a constraint in optimization |

### 3.3 Safety / Criterion Assumptions
| # | Assumption | Justification | Planned Validation |
|---|-----------|---------------|--------------------|
| C1 | Injury risk is controlled by bounding **peak deceleration x duration** (an acceleration-tolerance envelope) | Classical biomechanical tolerance framing | Compare against alternative indices (e.g., injury-criterion-style integrals) |
| C2 | The tolerance threshold is treated as a **parameter with a conservative default and a range** | Real thresholds are population- and circumstance-dependent | Sweep the threshold to show design sensitivity |
| C3 | The relevant exposure is the **primary landing impact**; secondary bounces are secondary | Primary impact dominates peak load | Include secondary-impact check as an extension |

### 3.4 Modeling / Scope Assumptions
| # | Assumption | Justification | Planned Validation |
|---|-----------|---------------|--------------------|
| D1 | Boxes are **identical within a layer** and arranged in a regular pattern | Enables a compact parameterization | Compare regular vs. optimized mixed layouts |
| D2 | Environmental factors (wind, rain, humidity softening board, temperature) are neglected at this stage | No data given | Discuss as robustness scenarios |
| D3 | The objective is a **count/cost proxy** (number of boxes), possibly with a small penalty for pile height/volume | "Use relatively few boxes" is the stated economy goal | Test volume- and height-weighted objectives |
| D4 | The design should be **conservative for safety** before it is minimal for cost | Safety dominates in a stunt context | Report the safety-versus-cost trade-off curve |

### 3.5 Assumption-Handling Strategy
- Record all assumptions in a **single registry** with IDs (as above) so that sensitivity analysis can toggle them systematically.
- Flag any assumption whose relaxation changes the recommended design **qualitatively** (e.g., flips the choice of box size or eliminates the need for box modification).

---

## 4. Data Processing Plan

> The problem is largely **analytically specified**. There is no provided dataset; the "data" comprises physical parameters, material properties, and threshold criteria to be assembled and bounded in the modeling phase. **No data will be analyzed or transformed in this planning phase.**

### 4.1 Data Sources and Roles
1. **Given problem parameters** — the qualitative scenario (motorcycle + rider over an elephant into boxes). Role: framing the jump and the deliverable.
2. **Scenario parameters to be specified** — rider+bike combined mass, ramp height/angle, launch speed, jump height and distance, elephant dimensions/clearance. Role: model inputs and sensitivity ranges.
3. **Material properties (external references)** — corrugated-board compression strength, plateau crush stress, crush stroke fraction, board grade options, box sizes commonly available. Role: calibrating the crush model.
4. **Biomechanical tolerance references (external)** — deceleration magnitude/duration tolerance envelopes. Role: defining the safety constraint.
5. **Derived quantities** — landing speed components, kinetic/potential energy, total crush stroke required, per-box energy absorption, required box count. Role: model outputs (to be produced later).

### 4.2 Preprocessing Plan (Future)
- **Unit standardization:** keep a single unit layer (SI lengths in meters, mass in kilograms, velocity in m/s, force in newtons, energy in joules, deceleration in g) with explicit conversions.
- **Parameter table construction:** assemble a machine-readable constants table with a **nominal value, lower bound, and upper bound** for every scenario and material parameter.
- **Scenario normalization:** express jump geometry in a compact, dimensionless form where possible (e.g., normalized free-fall height) to ease generalization.
- **Criterion encoding:** express the safety criterion as a numerically checkable inequality with explicit margins.

### 4.3 Feature / Quantity Construction (Future)
- **Landing-state vector** `(v_x, v_y, contact angle, E_kin, E_pot)` as a function of jump parameters.
- **Crush-response descriptor** per box and per layer: plateau force, working stroke, energy absorbed per box before densification.
- **Pile descriptors:** number of layers, footprint area, total available stroke, vertical density profile.
- **Safety descriptors:** peak deceleration, deceleration duration, stroke utilization (fraction of pile height consumed), margin to bottom-out.
- **Economy descriptors:** box count, pile volume, pile height (camera visibility proxy).

### 4.4 Data Usage Strategy
- Use scenario parameters as **inputs with ranges**, not as single fixed numbers, so the design can be reported robustly.
- Treat material and tolerance references as **calibrations with uncertainty**, to be swept, not as exact truths.
- Keep external references **optional and clearly separated**, so the model can degrade gracefully to first-principles estimates if a reference is unavailable.
- Define all discretization choices (e.g., layer granularity, landing-point grid) as **tunable parameters**, not fixed facts.

---

## 5. Candidate Model Framework

### 5.1 Modeling Paradigm
A **deterministic, physics-based design model** combining (i) a projectile/trajectory component, (ii) a nonlinear energy-absorber (crush) component, and (iii) a discrete/combinatorial stacking component, wrapped in an **optimization over box design and count** subject to a safety constraint.

### 5.2 Decision Variables (Candidate)
- `L, W, H` — box dimensions (length, width, height).
- `g_b` — board grade / wall construction (parameterizing crush strength).
- `n_layers` — number of stacked layers.
- `n_boxes_per_layer` (or footprint `P`) — how many boxes per layer / pile footprint.
- `S` — stacking pattern / interlocking scheme (regular grid, staggered, graded density).
- Optional **modification variables:** pre-crush fraction, scoring/baffling flags, layer-wise density gradation, partial fill.
- Possibly a **landing-point offset** decision if the pile may be positioned relative to the projected landing point.

### 5.3 Objective Function (Candidate)
Minimize a **cost proxy** dominated by **box count**, e.g. `Cost = n_boxes`, optionally augmented with penalties for pile height (camera visibility) or pile volume. Alternative objectives to be compared: minimize pile volume; minimize pile height; maximize safety margin for a fixed budget.

### 5.4 Constraints
- **Safety:** peak deceleration and its duration within tolerance (or injury index below threshold).
- **Bottom-out:** required crush stroke `≤` available pile height with a margin.
- **Capture geometry:** pile footprint must cover the landing uncertainty band and the expected slide/travel distance after first contact.
- **Energy balance:** total absorptive capacity `≥` landing energy (kinetic at contact plus any residual descent during crush).
- **Stability:** the stack must remain standing and not topple before or during impact.
- **Practicality:** box sizes limited to manufacturable/available dimensions; box count integer; pile height physically buildable.

### 5.5 Candidate Modeling Approaches (to be compared)
1. **Lumped point-mass + plateau-force absorber (analytic core).** Energy/work balance with a near-constant crush force, yielding stroke and peak-deceleration relations. Fast, transparent, good for scaling laws.
2. **Multi-degree-of-freedom layered spring/crush model.** Each layer as a nonlinear element; simulate the deceleration history. Captures progressive crush and bottom-out risk.
3. **Dimensional-analysis / scaling model.** Derive dimensionless groups linking mass, jump height, box strength, and required count; the natural vehicle for generalization.
4. **Discrete/combinatorial stacking optimization.** Enumerate or search over stacking patterns and layer counts; pair with an LP/feasibility check on per-layer forces.
5. **Continuum crushable-foam analogy.** Treat the pile as a homogenized crushable medium with a densification law; retrieve equivalent box requirements.
6. **Metaheuristic search (GA / simulated annealing) over mixed discrete-continuous design variables** where the feasible set is nonconvex.

### 5.6 Mathematical Ideas to Draw On
- **Projectile motion** for the landing state; **work–energy theorem** and **impulse–momentum** for the crushing phase.
- **Constant-force absorber energy balance:** absorbed energy `≈ F_crush · d_stroke` (candidate form, to be confirmed), giving required stroke as a function of mass and impact speed.
- **Peak deceleration relation:** `a_peak ≈ F_crush / m` (candidate form) bounded by the tolerance criterion.
- **Crush force–displacement plateau with densification** (progressive crumpling) as the constitutive idealization.
- **Box compression strength scaling** with dimensions and board grade (packaging-mechanics relations) to relate box size to load capacity.
- **Layer combination laws** for series/parallel crush elements.
- **Buckling / structural stability** arguments for why larger boxes may be weaker per unit area, motivating optimal box size.
- **Dimensional analysis / Buckingham-style grouping** for the generalization rule.

### 5.7 Advantages and Limitations (per approach)
- *Analytic core:* transparent and generalizable, but idealized (no progressive crush detail).
- *Layered spring model:* captures bottom-out and deceleration history, but needs material parameters and is more complex.
- *Scaling model:* the cleanest route to generalization, but only as good as the assumed dominant physics.
- *Discrete stacking optimization:* directly addresses "how stacked", but is combinatorial.
- *Metaheuristics:* flexible with messy constraints, but no optimality guarantee.
- Each candidate will be assessed during modeling for tractability, safety fidelity, and generalization power; this draft only enumerates them for future comparison.

---

## 6. Implementation Roadmap

### 6.1 Proposed Workflow
1. **Parameter & unit module** — encode scenario and material parameters with ranges.
2. **Trajectory module** — map ramp/jump parameters to the landing-state vector.
3. **Crush-model module** — per-box and per-layer force–displacement and energy-absorption relations.
4. **Stack-assembly module** — build the pile from layer specifications; compute series/parallel response and footprint.
5. **Impact-simulation / feasibility module** — integrate the rider mass through the pile response; compute peak deceleration, stroke utilization, and bottom-out check.
6. **Safety-check module** — evaluate the chosen tolerance criterion against computed deceleration.
7. **Optimization module** — search over (box size, grade, count, layers, stacking, modifications) to minimize cost subject to safety.
8. **Generalization module** — fit/derive the scaling rule across mass and jump height.
9. **Reporting module** — produce design recommendations, trade-off curves, and safety margins.
10. **Design-rule module** — package the workflow as a reproducible procedure for the stunt coordinator.

### 6.2 Required Modules / Components
- Trajectory/kinematics utility.
- Crush-model library (plateau, linear, densifying variants).
- Stack builder + layer-combination utility.
- Time-stepping impact integrator (or closed-form work–energy evaluator).
- Safety-criterion evaluator.
- Optimizer driver (enumerative and/or metaheuristic).
- Sensitivity/experiment harness.
- Design serializer (machine-readable + human-readable recommendation).

### 6.3 Algorithmic Candidates to Implement
- Baseline: analytic constant-force absorber sizing (reference only; not to be evaluated here).
- Layer-wise time-stepping simulation for deceleration history.
- Enumerative search over discrete box sizes/stack patterns with closed-form feasibility.
- Metaheuristic over mixed discrete-continuous variables.
- Hybrid: metaheuristic design search + analytic safety check.

### 6.4 Engineering Practices (Future)
- Configuration-driven runs (no hard-coded constants).
- Reproducible seeds, logged parameters, versioned outputs.
- Strict separation of physics model, solver, and reporting code.
- Explicit uncertainty ranges attached to every calibration input.

---

## 7. Validation Strategy

### 7.1 Evaluation Metrics (to be computed later)
- **Primary:** box count (cost proxy) required for a safe design.
- **Safety indicators:** peak deceleration, deceleration duration, margin to the tolerance threshold.
- **Bottom-out indicator:** stroke utilization (required stroke ÷ available pile height) and its margin.
- **Energy accounting:** total pile absorptive capacity versus required landing energy; residual/left-over capacity.
- **Geometry indicators:** pile footprint coverage of the landing uncertainty band; pile height (camera visibility).
- **Robustness metrics:** performance spread across assumption and parameter variants.

### 7.2 Validation Methods
1. **Energy-conservation audit** — absorbed energy must reconcile with the landing kinetic plus descent potential energy within the modeled stroke.
2. **Constraint re-check** — independently re-evaluate the safety and bottom-out constraints on the recommended design.
3. **Cross-model comparison** — compare the analytic constant-force model, the layered simulation, and the scaling model for consistency in required count and stroke.
4. **Extremes and limits** — verify that designs blow up sensibly as mass or jump height grows, and that small-jump limits reduce to near-zero boxes.
5. **Physical plausibility** — required stroke, deceleration, and box sizes must fall in realistic stunt/packaging ranges.
6. **Comparison to practice (qualitative)** — sanity-check the design logic against how real stunt cushions/arrestor beds are built (differences only, no results).
7. **Discretization/convergence** — confirm results stabilize as layer granularity and time-step are refined.

### 7.3 Sensitivity Analysis Plan
- Vary **combined mass** and **jump height** across their ranges (the stated generalization axes).
- Toggle the **crush law**: constant-force vs. linear vs. densifying.
- Vary **box material strength** and **box size** within realistic bounds.
- Vary the **safety threshold** (conservative to permissive) to expose the safety–cost trade-off.
- Vary **landing-point uncertainty** and post-contact slide distance.
- Vary **stacking pattern** (regular vs. staggered vs. graded density).
- Toggle environmental softening of board (humidity) as a robustness stress.

### 7.4 Threats to Validity
- Over-idealized crush response could bias the required box count.
- Point-mass assumption could understate rotational/limb loads.
- Uncertain material properties and tolerance thresholds propagate into the design.
- Landing-point uncertainty could make a minimal design unsafe in practice.
- Each threat will be mapped to a mitigation in the modeling phase.

---

## 8. Expected Result Interpretation

> Interpretation guidance only — **no results are produced in this draft.**

The future solution is expected to yield:
- A recommended **box size** and **box count** for a baseline jump scenario.
- A **stacking scheme** — footprint, number of layers, interlocking and any vertical density gradation.
- A **verdict on box modifications** (e.g., pre-crushing, scoring, baffling, graded fill): whether they help, hurt, or matter only in edge cases.
- A **generalization rule** expressing required cushion capacity as a function of combined weight and jump height.

Interpretation should emphasize:
- How the design balances the **safety constraint (upper bound on deceleration)** against the **bottom-out constraint (lower bound on stroke)** — the feasible window is the working range.
- Whether the binding factor is **material strength** (boxes too weak to hold the load without excessive stroke), **geometry** (pile too tall for the camera or too small for the footprint), or **cost** (box count).
- Why an **optimal box size** is expected to exist: larger boxes may absorb more energy individually but carry weaker sidewalls per unit load, so a trade-off is likely.
- The practical usability of the recommendation for a real stunt coordinator (buildable, hidden from camera, few boxes).

---

## 9. Limitations and Improvements

### 9.1 Anticipated Limitations
- Idealized crush behavior and point-mass impact may not capture real crush of a heterogeneous box pile.
- Rotational energy, rider posture, tumbling, and secondary impacts are out of scope at this stage.
- Material properties and human tolerance thresholds are uncertain and treated only as ranges.
- Environmental effects (humidity, temperature, prior box damage) are neglected.
- The elephant/ramp design and the launch mechanics are treated as given rather than co-designed.

### 9.2 Planned Improvements / Extensions
- Incorporate empirical box-compression data and crash-cushion references if obtainable.
- Replace the point mass with a two-body or rigid-body impact model; include rotational effects.
- Model progressive multi-stage crush with explicit densification and lateral spreading.
- Add a secondary-impact / bounce analysis after the primary absorption stroke.
- Co-optimize ramp geometry and box design jointly rather than treating the jump as fixed.
- Extend the stacking search to arbitrary interlocking and mixed box sizes.
- Strengthen the generalization rule into a closed-form scaling law validated across a design grid.
- Compare cardboard boxes against alternative absorbers (airbags, foam, loose fill) as benchmarks.

### 9.3 Open Questions to Resolve in the Modeling Phase
- What is the dominant physics: impact-speed deceleration, crush stroke, or stack stability?
- Is a single uniform box type sufficient, or does a **graded-density stack** (softer on top, stiffer below) materially improve safety?
- How large is the safety–cost trade-off, and how many "extra" boxes does a conservative margin cost?
- Does the required box count scale primarily with kinetic energy (mass × height) or with impact speed squared?
- Under what conditions do box modifications become worthwhile?
- How much landing-point uncertainty can the design tolerate before it must be oversized?

---

*End of initial modeling plan draft. This document is a roadmap; execution, computation, and results are deferred to the subsequent modeling phase.*
