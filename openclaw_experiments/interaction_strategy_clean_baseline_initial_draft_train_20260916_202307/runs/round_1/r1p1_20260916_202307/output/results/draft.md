# Modeling Blueprint Draft — Forest Service Wildfire Resource Allocation

**Problem ID:** `2001_Forest_Service`
**Source:** HiMCM 2001
**Document type:** Initial modeling plan draft (blueprint / roadmap only)
**Status:** Planning stage — no solving, computation, or results included
**Date prepared:** 2026-09-16

> This document is a *modeling blueprint*. It describes how a future modeling effort
> *could* be structured. It deliberately contains no computed results, no data analysis,
> no fitted parameters, and no final conclusions. All statements are future-oriented.

---

## 1. Problem Background and Restatement

The Forest Service must allocate fire-fighting resources across a wilderness area
during the upcoming dry season. The relevant setting, as given, can be restated as
follows:

- **Wilderness geometry.** A square park region with side length 80 km.
- **Surface fuels.** The area consists of small trees and brush (fast-spreading,
  light fuels).
- **Firebreak grid.** A rectangular grid of north–south and east–west firebreaks was
  constructed across the entire interior at **5 km intervals**, producing a regular
  lattice of cells and drivable corridors.
- **Seasonality.** The dry season runs **July–September**.
- **Wind.** A **prevailing westerly wind throughout the day** during the season.
- **Ignition.** **Frequent lightning bursts** are the dominant ignition source.
- **Fire-fighting units.** Four units are to be deployed, each comprising 10 firefighters,
  one pickup truck, one dump truck, one 50,000 L water truck, and one bulldozer with
  truck and trailer, plus chainsaws, hand tools, and general equipment.
- **Mobility.** Personnel can be moved quickly by helicopter anywhere inside the
  wilderness; **all equipment must travel on the existing firebreaks**.
- **Helicopter.** Exactly one helicopter is on standby at all times during the season.
- **Base camps.** The Service may place base camps for the units **anywhere in the area**.
- **Two deliverables.** (a) the *best distribution* of the four units (base-camp siting),
  and (b) a *damage-assessment forecast* used both to estimate likely burned wilderness
  and to help decide *when* additional outside units should be requested.

The modeling problem is therefore a **facility-location + dynamic-response** problem
coupled to a **stochastic fire-spread / damage-forecasting** problem, all constrained
by a discrete road network and a single shared helicopter.

---

## 2. Objectives and Subproblems

### 2.1 Primary objectives

1. **Placement objective.** Determine base-camp locations for the four units that
   optimize a defined performance criterion (to be chosen — see §5), respecting the
   firebreak network for equipment movement.
2. **Forecast objective.** Produce a damage-assessment forecast that estimates the
   wilderness area likely to be burned per fire event and per season, given the chosen
   deployment.

### 2.2 Subproblems to be decomposed

| ID | Subproblem | Nature |
|----|------------|--------|
| S1 | Represent the wilderness, firebreak grid, and fire-spread geometry | Spatial/environmental modeling |
| S2 | Model ignition (lightning) as a stochastic process over space and time | Stochastic input modeling |
| S3 | Model fire growth and spread under westerly wind and fuel characteristics | Dynamic spread model |
| S4 | Model detection, dispatch, and suppression as a response-time process | Operations/queueing model |
| S5 | Model equipment movement constraints over the firebreak network | Network/travel-time model |
| S6 | Formulate and solve the base-camp siting optimization | Optimization |
| S7 | Quantify burned area / damage under a given deployment | Damage estimation |
| S8 | Define the criterion for requesting additional units | Decision rule / threshold |
| S9 | Sensitivity and robustness analysis of the deployment | Validation |

### 2.3 Deliverable map

- **Deliverable A** → Subproblems S1–S6 (deployment plan).
- **Deliverable B** → Subproblems S1–S4, S7–S8 (damage forecast + escalation trigger).

---

## 3. Assumptions

Assumptions are grouped by theme. Each is stated with *justification* and a planned
*future validation approach*. Final assumptions will be fixed only after validation.

### 3.1 Spatial / environmental

- **A1.** The wilderness is represented as a continuous 80 km × 80 km square, discretized
  later into cells aligned with the 5 km firebreak grid (candidate grid: 16 × 16 cells)
  or a finer sub-grid for spread fidelity.
  *Justification:* firebreaks are built at fixed 5 km intervals, suggesting the natural
  management unit. *Future validation:* compare coarse vs. finer discretization for
  stability of results.
- **A2.** Fuels are treated as spatially homogeneous (uniform small trees/brush) in the
  baseline, with optional heterogeneity added later.
  *Justification:* problem gives no fuel map. *Future validation:* perturbation study.
- **A3.** Firebreaks act as partial barriers: they slow but may not fully stop spread,
  and they simultaneously serve as drivable equipment corridors.
  *Justification:* real firebreaks are partly effective and are the only equipment routes.
  *Future validation:* sensitivity to firebreak-effectiveness parameter.

### 3.2 Fire behavior

- **A4.** Fire spreads with a directional bias due to the prevailing westerly wind
  (faster eastward/with-wind spread), modeled via a directional spread-rate function.
  *Justification:* stated prevailing wind. *Future validation:* vary wind direction/speed.
- **A5.** Spread rate increases with dry-season conditions (e.g., a season-phase factor).
  *Justification:* dry season July–September is fire-prone. *Future validation:* scenario sweep.
- **A6.** Fire ignition points occur by lightning as a stochastic spatial–temporal process
  (e.g., Poisson-type arrivals in time, spatially dispersed).
  *Justification:* "frequent lightning bursts." *Future validation:* compare arrival models.

### 3.3 Operational response

- **A7.** Detection and reporting of an ignition is effectively immediate or delayed by a
  small, modelable detection lag.
  *Justification:* single standby helicopter + lightning-caused fires. *Future validation:*
  sensitivity to detection-lag distribution.
- **A8.** Personnel travel by helicopter (fast, near-straight-line within the area);
  equipment travels only along firebreaks (network distance).
  *Justification:* explicitly stated. *Future validation:* compare helicopter-only vs.
  equipment-constrained arrival; assess whether equipment arrival is the bottleneck.
- **A9.** A unit can suppress a fire if it arrives with sufficient capacity before the fire
  exceeds a suppression-capacity threshold; otherwise the fire escapes and grows.
  *Justification:* standard containment logic. *Future validation:* vary capacity thresholds.
- **A10.** Each of the four units is independent and can be assigned to at most one active
  fire at a time; the single helicopter may create contention (to be modeled as a shared
  resource or ignored in baseline).
  *Justification:* resource realism. *Future validation:* model with/without helicopter contention.
- **A11.** Base camps hold a unit's full equipment set and are static over the season.
  *Justification:* season-long deployment framing. *Future validation:* static vs. dynamic relocation.

### 3.4 Modeling-scope assumptions

- **A12.** Season length and daily wind cycle can be aggregated into representative
  "fire-day" scenarios to keep the model tractable.
- **A13.** Monetary valuation of damage is optional; the baseline may measure damage as
  burned area and add a value function later.
- **A14.** No external units are available at time 0; the escalation rule (Deliverable B)
  governs when they should be requested.

---

## 4. Data Processing Plan

No dataset files are currently present in the workspace, so the plan assumes the model
will rely on **parameters derived from the problem statement plus literature values**,
with a clearly documented parameter table.

### 4.1 Data sources to be assembled

- **Geometric data (given):** square side 80 km; firebreak spacing 5 km; derived lattice
  of cells, nodes, and edges.
- **Environmental parameters (to be sourced/estimated):** typical surface-fire spread
  rates for light fuels, wind-speed influence, firebreak effectiveness.
- **Operational parameters (given/estimated):** unit composition, water-truck capacity
  (50,000 L), vehicle speeds on firebreaks, helicopter speed, suppression productivity.
- **Stochastic parameters (to be estimated):** lightning-strike arrival rate and spatial
  distribution for the region and season.
- **Optional external data (future):** historical lightning/fire records, terrain, fuel maps.

### 4.2 Preprocessing steps (planned)

1. **Grid construction.** Build the node/edge graph of firebreaks; define cell adjacency.
2. **Network travel-time matrix.** Compute equipment travel times between all candidate
   camp sites and all cells via shortest paths on the firebreak graph.
3. **Coordinate normalization.** Map problem coordinates to a consistent metric frame.
4. **Parameter normalization.** Put all rates/lengths in consistent units (km, hours).
5. **Stochastic input generation.** Define distributions for ignition times/locations and
   wind; plan random-seed control for reproducibility.

### 4.3 Feature / derived-quantity construction (planned)

- Expected **distance / response time** from each candidate camp to each cell.
- **Coverage maps** (fraction of area reachable within a response-time budget) per camp.
- **Priority weights** per cell reflecting damage potential (e.g., area, spread-prone
  direction relative to westerly wind).
- **Fire-event descriptors** for the forecast model (size, duration, containment status).

### 4.4 Data usage strategy

- **Calibration split:** parameters tuned on a set of synthetic/reference scenarios.
- **Validation split:** independent scenarios reserved for out-of-sample checks.
- **Scenario library:** a designed set of seasonal and wind/ignition scenarios used
  consistently across all subproblems.
- All inputs, assumptions, and parameter values to be logged in a single parameter table
  for auditability.

---

## 5. Candidate Model Framework

Candidate models are offered as alternatives to be compared, not as final choices.

### 5.1 Spatial representation layer

- **Option A — Lattice/cellular grid** (16 × 16 aligned to firebreaks).
  *Advantages:* matches management units; simple. *Limitations:* coarse spread geometry.
- **Option B — Fine raster + network overlay.**
  *Advantages:* smoother spread. *Limitations:* more computation.

### 5.2 Fire-spread models (S3)

- **Candidate 1 — Deterministic cellular-automaton spread** with directional (wind-biased)
  transition rules and a firebreak dampening factor.
- **Candidate 2 — Probabilistic/epidemic-style spread** (percolation or stochastic CA)
  giving distributions of burned area rather than a single value.
- **Candidate 3 — Continuous front model** (e.g., Huygens/elliptical wavefront growth),
  suited to smooth spread-rate fields.
- *Comparison plan:* choose based on fidelity vs. tractability and on validation stability.

### 5.3 Ignition model (S2)

- **Candidate:** Poisson process in time with a spatial intensity over cells; alternatives
  include clustered (Cox / self-exciting) arrivals to mimic "bursts."
- *Key outputs to the forecast:* expected number of fires per season, ignition-location
  distribution.

### 5.4 Response / suppression model (S4–S5)

- **Candidate:** a detection–dispatch–travel–suppression pipeline. Travel uses the
  network matrix for equipment and near-direct distance for personnel/helicopter.
- **Containment logic:** fire is contained if total suppression capacity delivered before
  fire size exceeds a threshold; else it becomes an "escaped" fire feeding the spread model.
- **Possible formalisms:** discrete-event simulation, or a queueing-style assignment of
  units to fires.

### 5.5 Deployment optimization (S6)

- **Objective candidates (to be finalized):**
  - minimize expected burned area over the season;
  - minimize expected response time weighted by damage potential;
  - maximize coverage within a response-time budget;
  - minimize worst-case (robust) burned area.
- **Decision variables:** locations of the 4 base camps (continuous in-area, or restricted
  to firebreak nodes); optional assignment of units to sectors.
- **Candidate methods:**
  - *Exact/relaxed optimization:* mixed-integer program (p-median / maximal covering /
    facility-location variants) over candidate sites.
  - *Heuristic/metaheuristic:* greedy + local search, simulated annealing, or genetic
    algorithm when the objective involves expensive simulation.
  - *Simulation-optimization loop:* wrap the fire/response simulation inside the siting
    search (approach for the full stochastic objective).
- **Constraints:** 4 units; equipment reachable only via firebreaks; one helicopter shared.

### 5.6 Damage forecast & escalation rule (S7–S8)

- **Forecast model:** derive a distribution of burned area per fire and per season from
  simulation or analytical approximations; report expected value plus uncertainty bands.
- **Escalation rule candidates:** trigger additional-unit requests when (i) expected
  burned area exceeds a threshold, (ii) simultaneous active fires exceed unit capacity,
  or (iii) a fire exceeds a size/duration trigger. The rule's parameters will themselves
  be tuned in validation.

### 5.7 Variables (indicative)

- **Decision:** camp coordinates `(x_i, y_i)`, i = 1..4; optional sector assignment.
- **Environmental state:** fire perimeter/occupied cells, wind direction/speed, dryness.
- **Operational state:** unit availability, travel progress, water/consumables remaining.
- **Performance:** response time, contained/escaped flag, burned area, units-required flag.

---

## 6. Implementation Roadmap

### 6.1 Modules to be built

1. **Geometry & network module** — grid, graph, shortest-path travel-time matrices.
2. **Ignition generator** — configurable stochastic ignition scenarios.
3. **Fire-spread engine** — chosen spread model with wind and firebreak effects.
4. **Response simulator** — detection, dispatch, travel, suppression, contention.
5. **Optimizer** — siting search (exact/heuristic/simulation-optimization).
6. **Forecast & rule module** — damage distribution + escalation trigger.
7. **Experiment driver** — scenario library, seeds, batch runs, logging.
8. **Reporting module** — tables/figures for the eventual write-up (not produced here).

### 6.2 Workflow sequence (planned)

1. Fix assumptions and parameter table (from §3–§4).
2. Build geometry + network; verify travel-time sanity qualitatively.
3. Implement baseline deterministic spread; then stochastic variant.
4. Implement response/suppression pipeline.
5. Couple spread + response into a single scenario simulator.
6. Embed simulator in siting optimizer to produce candidate deployments.
7. Generate damage forecast distributions and calibrate the escalation rule.
8. Run validation and sensitivity studies; iterate assumptions if unstable.
9. Produce deployment recommendation + forecast outputs for the final report.

### 6.3 Engineering considerations

- **Reproducibility:** fixed random seeds; single parameter config file.
- **Modularity:** each subproblem independently testable before coupling.
- **Tractability:** start deterministic and coarse; increase fidelity only if it changes
  conclusions.
- **Compute budget:** precompute network matrices once; cache simulation outputs.

---

## 7. Validation Strategy

### 7.1 Evaluation metrics (to be used later)

- **Deployment quality:** expected burned area per season; expected response time;
  coverage fraction within time budgets; worst-case burned area.
- **Forecast quality:** calibration (predicted vs. realized burned area across scenarios),
  sharpness of prediction intervals, error in expected fire count.
- **Rule quality:** false-alarm rate and missed-escalation rate for the additional-units
  trigger.

### 7.2 Validation methods (planned)

- **Internal consistency:** verify simulation conserves plausible fire growth; check that
  containment logic responds sensibly to capacity changes.
- **Out-of-sample scenarios:** hold out scenario sets from tuning and evaluate forecast.
- **Baseline comparisons:** compare optimized deployment against reference deployments
  (e.g., evenly spaced camps, corner camps, single central camp).
- **Optimizer robustness:** multiple random restarts / seeds to confirm near-optimality
  and avoid local optima.
- **Cross-model agreement:** compare deterministic vs. stochastic spread conclusions.

### 7.3 Sensitivity analysis (planned)

- Vary: wind speed/direction, firebreak effectiveness, spread-rate parameters, detection
  lag, unit suppression capacity, helicopter availability/contention, ignition rate.
- Report how optimal camp locations and forecasted burned area shift under each variation;
  identify which parameters most influence decisions.
- Robustness check: does the recommended deployment remain near-optimal under plausible
  perturbations?

---

## 8. Expected Result Interpretation

This section describes *how results would be read later*; no results are produced here.

- **Deployment output:** a set of four base-camp locations (and possibly sector
  assignments) with the rationale tied to wind-biased spread (likely favoring windward/
  western positioning to intercept eastward-spreading fires) and road-network access.
- **Coverage/response maps:** an expected interpretation is that camps cluster where
  rapid equipment access and high damage-potential areas coincide.
- **Damage forecast:** reported as expected burned area with uncertainty ranges per fire
  and per season, plus the probability of exceeding defined loss thresholds.
- **Escalation guidance:** a rule/threshold indicating when the Service should request
  outside units, expressed in observable triggers (e.g., number of simultaneous fires,
  size/duration of an uncontrolled fire, cumulative burned area).
- **Interpretation caveat:** conclusions should be presented as conditional on the stated
  assumptions and scenario library.

---

## 9. Limitations and Improvements

### 9.1 Anticipated limitations

- Homogeneous-fuel and simplified-weather assumptions may over- or under-state spread.
- Single-helicopter contention and equipment network constraints may dominate outcomes in
  ways sensitive to travel-time assumptions.
- Coarse discretization may misrepresent fine-scale fire geometry.
- Stochastic ignition parameters are not given and will rely on estimates.
- The four-unit fixed budget limits achievable coverage; trade-offs must be explicit.

### 9.2 Planned improvements (future iterations)

- Introduce fuel/terrain heterogeneity and time-varying wind (diurnal cycle).
- Refine firebreak effectiveness (partial barriers, breached firebreaks).
- Add helicopter scheduling/site-selection as a decision variable.
- Extend damage to economic/ecological valuation.
- Support dynamic unit relocation during the season.
- Incorporate real historical lightning/fire records for calibration where available.
- Perform formal multi-objective trade-off analysis and robust/Pareto optimization.

---

## Appendix A — Planning Checklist

- [x] Problem restated in the blueprint's own words.
- [x] Objectives and subproblems enumerated.
- [x] Assumptions listed with justification + validation approach.
- [x] Data processing plan drafted (sources, preprocessing, features, usage).
- [x] Candidate models, variables, advantages/limitations outlined.
- [x] Implementation roadmap and modules defined.
- [x] Validation metrics, methods, and sensitivity plan specified.
- [x] Expected interpretation and limitations discussed.
- [x] No solving, computation, data analysis, or results included.

*End of planning draft.*
