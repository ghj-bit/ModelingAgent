# Skyscrapers — Initial Modeling Plan (Blueprint Draft)

**Problem ID:** `2001_Skyscrapers`
**Source:** HiMCM 2001
**Document type:** Modeling blueprint / roadmap only. No results, no data analysis, no code, and no conclusions are included here. All statements are forward-looking.

---

## 1. Problem Background and Restatement

### 1.1 Background
Skyscrapers differ in height, floor area, occupancy, and use (office, residential, mixed-use). During a catastrophe (fire, earthquake, tornado, hurricane), a full building evacuation may be required. In the scenario under study, electrical power is lost, so passenger elevators are inoperative; only firefighters and rescue personnel carrying special keys can use the elevator banks.

### 1.2 Restatement (planned framing)
The task will be to build a mathematical model that determines how to clear a given building within a prescribed time budget **X** minutes. The model will be expected to characterize — as decision variables or design outputs — the following:

- the **height** of the building (and thus the number of floors),
- the **maximum occupation** the building may hold while still meeting the target clearance time,
- the **type(s) of evacuation methods** employed (e.g., stairways alone, stairways combined with elevator-assisted rescue, phased/zonal evacuation, refuge areas, etc.).

The model will then be evaluated (in a later solver stage) for **X = 15, 30, and 60 minutes**.

### 1.3 Why this is a modeling problem (not a lookup problem)
Clearance time is an emergent quantity that couples: building geometry, occupant distribution, pedestrian dynamics on stairs and through doors, merging/counterflow congestion, and the availability of non-stair egress for rescue personnel. The blueprint therefore targets a coupled **geometry–flow–time** model rather than a single closed-form formula.

---

## 2. Objectives and Subproblems

### 2.1 Primary objective
Construct a model that maps building/occupancy/egress design parameters to an **evacuation time** T, and invert it to determine, for each target X, the feasible combinations of building height, maximum occupancy, and evacuation method.

### 2.2 Subproblems (to be decomposed for the solver stage)
1. **Geometry parameterization:** relate building height H (floors N), floor plate area A, and stairwell count/dimensions in a consistent way.
2. **Occupancy model:** define maximum occupation as a function of usable floor area, occupancy-density standards, and usage type.
3. **Stair descent / pedestrian flow submodel:** model vertical movement speed under varying density, including door entry and merge points.
4. **Congestion / queuing submodel:** represent bottlenecks (stair doors, stair landings, final exit discharge) as servers or flow-capacity constraints.
5. **Evacuation-method submodel:** represent the trade-off between pure-stair evacuation and elevator-assisted rescue by special-key personnel; decide whether phased/zonal schemes are included.
6. **Inversion / feasibility subproblem:** for each X, determine the maximum H and maximum occupancy consistent with T ≤ X.
7. **Sensitivity/robustness framing:** identify which parameters dominate the predicted clearance time.

### 2.3 Planned deliverables
- A parameterized evacuation-time model (set of equations + a computational scheme) — *to be built later*.
- A procedure to produce, for each X ∈ {15, 30, 60} min, a feasible (height, occupancy, method) region — *to be computed later*.
- A validation and sensitivity protocol.

---

## 3. Assumptions

The following assumptions are proposed for the blueprint. Each will be revisited and defended (or relaxed) during the solver stage.

### 3.1 Initial assumptions (to be tested later)
1. **Occupant population is homogeneous** in walking speed and mobility at first pass; heterogeneity (children, elderly, mobility-impaired) will be a later refinement.
2. **Occupants are distributed uniformly** across occupied floors at the onset of evacuation; non-uniform (worst-case top-floor clustering) will be examined in sensitivity analysis.
3. **Egress via stairs only** for general occupants; elevators are reserved for trained rescue personnel (special keys), as stated in the problem.
4. **No structural failure and no re-entry;** evacuation is a one-way discharge to the exterior.
5. **Stair capacity is limited by geometry** (width, tread/riser, landings) and by pedestrian density–speed relations rather than by fatigue at first pass; fatigue will be a refinement.
6. **Deterministic first-order model** on average behavior; stochastic/agent-level variability handled later via simulation.
7. **Discharge at ground level is unconstrained** (exits wide enough not to be the governing bottleneck) — this will be checked and, if false, modeled as a final bottleneck.
8. **Rescue personnel use of elevators does not increase general-occupant flow** but may enable clearing specific zones (e.g., refuge floors, upper stories) faster.

### 3.2 Justification sketch
These assumptions are chosen to yield a tractable, auditable baseline whose terms correspond to measurable quantities (floor geometry, stair width, walking speed, density). Simplicity here is deliberate: it makes the later inversion for X transparent.

### 3.3 Planned validation of assumptions
- Compare homogeneous-population predictions against heterogeneous/agent-based variants later.
- Test the "unconstrained discharge" assumption by treating discharge as a finite-capacity server.
- Verify elevator-rescue assumption against phased-evacuation literature/standards frameworks (to be surveyed in the solver stage).

---

## 4. Data Processing Plan

> **Note:** No dataset is supplied with this problem. The plan below describes how data/sources will be assembled and prepared during the solver stage.

### 4.1 Data sources to be assembled (later)
- **Building geometry references:** representative high-rise dimensions (floor height, floor-plate areas, stairwell widths) drawn from published building codes/case studies.
- **Pedestrian flow parameters:** density–speed–flow relations and specific-flow (persons/m/s) values for stairs, doors, and corridors, taken from established pedestrian-movement literature/standards (e.g., SFPE/Fruin-style parameters) — to be sourced and cited in the solver stage.
- **Occupancy standards:** code-based occupancy load factors (area per person) by usage type.
- **Scenario parameters:** evacuation time budgets X = 15, 30, 60 min.

### 4.2 Preprocessing plan (later)
- Normalize units consistently (SI): meters, seconds, persons/m², persons/(m·s).
- Build a **parameter table** with nominal value + plausible range for each input (for sensitivity analysis).
- Encode geometry as a structured object (floors, per-floor area, stair count/width, door widths).
- Tag each parameter with **source/provenance** and **confidence level** so assumptions remain auditable.

### 4.3 Feature construction (later)
- Derived quantities: total floor count N from height H and floor-to-floor height; effective stair capacity; number of parallel stair lanes per stairwell; exit-door effective width; total path length per occupant.
- Aggregated descriptors: total occupant load, occupant load per stair, per-floor release rate.

### 4.4 Data-usage strategy
- Use parameters as **scenario inputs** (not for statistical fitting), since the problem is design-oriented.
- Reserve a designated subset of parameter combinations as **stress scenarios** for validation, not for model calibration.
- Document every chosen value so the model is reproducible.

---

## 5. Candidate Model Framework

The blueprint proposes a **tiered** modeling strategy: start with an analytically tractable baseline, then layer congestion and stochasticity. The solver stage will select and combine tiers.

### 5.1 Tier 0 — Deterministic egress-time decomposition (baseline)
Evacuation time will be decomposed into additive phases:

- **Detection/decision time** (pre-movement, may be set to a scenario value).
- **Travel time** to the nearest stair (horizontal).
- **Stair descent time** (vertical).
- **Queueing/merge delay** at stair doors and landings.
- **Discharge time** at the final exit.

Form: T = t_pre + t_travel + t_stair + t_queue + t_discharge (planned form; to be specified and calibrated later).

Key variables (planned):
- H: building height; N = H / h_f (floors, with floor height h_f);
- N_occ: maximum occupation;
- W_s: stair width; k: number of stairwells;
- q: specific flow (persons per unit width per second);
- v: descent speed as a function of density ρ;
- A_f: floor plate area; occupancy load factor L (area/person).

### 5.2 Tier 1 — Fluid / continuum pedestrian-flow model
- Treat occupant flow along stairs as a **one-dimensional continuum** with density–speed–flow (fundamental diagram) relations.
- Model stairwell entrance doors and landings as **capacity constrictions** with finite specific flow.
- Use **conservation of persons** along each path.

### 5.3 Tier 2 — Queueing-network model
- Represent stair door/landing/exit as **servers**; each floor as a population source.
- Approximate using M/M/c- or M/G/c-style waiting-time expressions for merge bottlenecks (planned approximation; exact queue discipline to be decided later).
- Couple servers in series (per-floor entry → stair lane → exit) to produce total delay.

### 5.4 Tier 3 — Dynamic network flow / optimization
- Formulate the building as a **time-expanded flow network** (nodes = floors/landings, arcs = stairs/doors with capacities).
- Pose an **evacuation-time minimization** or **maximum-occupancy-for-given-X** problem.
- Inversion: for each X, find the feasible (H, N_occ, method) region as a constraint set — planned as an optimization problem to be solved later.

### 5.5 Tier 4 — Elevator-assisted / phased evacuation submodel
- Model elevator banks as **restricted servers** available to rescue personnel only.
- Explore whether **phased/zonal evacuation** or **refuge-floor staging** reduces total clearance time.
- Represent the interaction between stair-based occupant flow and key-holder elevator traffic.

### 5.6 Tier 5 — Agent-based / microscopic simulation (optional later)
- Social-force or cellular-automata pedestrian models to capture counterflow, merge imbalance, and local jamming.
- Intended as a **cross-check** of the aggregate tiers rather than the primary model.

### 5.7 Advantages and limitations (planned assessment)

| Tier | Advantages | Limitations |
|------|-----------|-------------|
| 0 | Simple, transparent, auditable, easy to invert | Ignores congestion dynamics; assumes independent phases |
| 1 | Captures density-dependent speed | Needs reliable fundamental-diagram parameters |
| 2 | Explicit handling of bottlenecks | Queueing approximations may oversimplify merging |
| 3 | Rigorous feasibility/inversion for X | Larger model; needs careful discretization |
| 4 | Reflects the special-key elevator rule | Depends on rescue-protocol assumptions |
| 5 | Realistic local dynamics | Computationally heavier; parameter-hungry |

---

## 6. Implementation Roadmap

### 6.1 Algorithms and methods (planned)
- Deterministic time-decomposition computation (Tier 0) as a baseline calculator.
- Numerical integration of continuum flow along stairs (Tier 1).
- Queueing-network evaluation (Tier 2).
- Linear/network-flow or LP/MILP formulation for inversion and max-occupancy feasibility (Tier 3).
- Optional discrete-event or agent-based simulation for Tier 5 cross-checks.

### 6.2 Required modules (planned structure)
1. **Geometry module** — builds building objects from height/floor-area/stair parameters.
2. **Occupancy module** — maps area and usage type to maximum occupation.
3. **Flow module** — computes travel and descent times from pedestrian parameters.
4. **Congestion module** — computes queueing/merge/exit delays.
5. **Method module** — encodes stair-only vs elevator-assisted vs phased schemes.
6. **Inversion/optimization module** — solves for feasible (H, N_occ, method) per X.
7. **Reporting module** — assembles charts/tables of the feasible regions (produced later).
8. **Configuration/provenance module** — parameter table with sources and ranges.

### 6.3 Workflow (planned sequence)
1. Define geometry and occupancy parameterizations.
2. Specify the Tier 0 baseline model.
3. Add congestion (Tiers 1–2).
4. Formulate the inversion/optimization (Tier 3).
5. Add elevator/phased submodels (Tier 4).
6. Optionally add simulation cross-checks (Tier 5).
7. Run the three X scenarios and assemble deliverables.
8. Document assumptions, sources, and reproducibility.

### 6.4 Software/engineering plan
- Language/stack to be chosen in the solver stage (Python ecosystem anticipated for numerical/optimization work).
- Repository layout anticipated: `data/` (parameters/sources), `code/` (modules), `results/` (outputs), `logs/` (run records).
- Emphasis on a clean separation between model specification and numerical execution.

---

## 7. Validation Strategy

### 7.1 Evaluation metrics (planned)
- **Predicted total evacuation time T** vs. target X (feasibility margin).
- **Predicted clearance curve** — fraction of occupants evacuated over time.
- **Maximum occupation** supported for each X.
- **Bottleneck identification** — which component dominates T.

### 7.2 Validation methods
1. **Internal consistency:** check phase decomposition against an end-to-end computation.
2. **Cross-tier comparison:** Tier 0 vs Tier 1–2 vs optional Tier 5 simulation; disagreement flags model-form error.
3. **Benchmarking against standards:** compare specific-flow/descent-time values with published pedestrian-movement references (sources to be cited later).
4. **Limiting-case checks:** zero-occupancy and single-floor limits; very wide vs. very narrow stairs.
5. **Back-of-envelope sanity checks** on each component time.

### 7.3 Sensitivity analysis (planned)
- One-at-a-time sweeps over: descent speed, specific flow, stair width, number of stairwells, floor height, occupancy load factor, pre-movement time.
- Global sensitivity (e.g., variance-based methods) to rank parameter dominance — planned for later.
- Worst-case scenarios: non-uniform occupant distribution, one stairwell blocked, reduced widths.

### 7.4 Uncertainty handling (planned)
- Present results as ranges/regions rather than single points.
- Propagate parameter ranges into the feasible (H, N_occ, method) sets.

---

## 8. Expected Result Interpretation

This section describes how results **will be interpreted** once the solver stage is complete. No results are presented here.

- The model is expected to output, for each X ∈ {15, 30, 60} min, a **family of feasible building designs**: combinations of height, maximum occupation, and evacuation method that satisfy T ≤ X.
- Expected qualitative structure (to be confirmed later): taller buildings and higher occupancies will require more stairwells, wider stairs, or elevator-assisted/phased schemes to meet shorter X; the 15-minute budget is expected to bind far more tightly than 60 minutes.
- Results will be framed as **design envelopes** (trade-off surfaces) rather than unique answers.
- The interpretation will emphasize **which design lever** (height, occupancy, method) most efficiently buys time.

---

## 9. Limitations and Improvements

### 9.1 Anticipated limitations
- Homogeneous-population and uniform-distribution assumptions ignore real heterogeneity and clustering.
- Deterministic baseline omits behavioral variance (pre-movement delays, route choice, panic).
- Elevator-assisted rescue modeling depends on unverified rescue-protocol assumptions.
- Parameter values from literature may not match any specific real building.
- Simplified geometry may omit sky-lobbies, transfer stairs, or horizontal refuge passages.

### 9.2 Planned improvements
- Introduce heterogeneous agents and mobility-impaired occupant subpopulations.
- Add stochastic pre-movement and speed distributions.
- Include detailed floor plans, sky-lobbies, and phased/zonal strategies.
- Model blocked-stair and counterflow (evacuees vs. responders) scenarios.
- Couple with fire/smoke-spread submodels for a fuller catastrophe analysis.
- Extend the inversion to multi-objective trade-offs (cost vs. clearance time).

---

## Planning Notes

- This document is a **blueprint only**: it specifies what will be modeled, how, and how it will be validated.
- No calculations, data analysis, code, experiments, plots, or final conclusions are included, by design.
- All numerical work (parameter selection, model solving, scenario runs for X = 15/30/60) is deferred to the solver stage.
