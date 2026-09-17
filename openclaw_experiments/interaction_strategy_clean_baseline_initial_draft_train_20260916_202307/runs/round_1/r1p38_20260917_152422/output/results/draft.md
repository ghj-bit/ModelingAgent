# Modeling Blueprint Draft — Searching for Submersibles

**Problem ID:** 2024_Searching_for_Submersibles
**Source:** MCM 2024, Problem B
**Document type:** Initial modeling plan / blueprint draft (planning only)
**Status:** Not a solution. No results, computations, or executed experiments are contained here.

---

## 1. Problem Background and Restatement

### 1.1 Context

Maritime Cruises Mini-Submarines (MCMS), based in Greece, operates a small deep-sea
submersible supported by a host ship and plans tourist excursions in the Ionian Sea to
explore shipwrecks. To obtain regulatory approval, MCMS must demonstrate defensible
safety procedures for emergency scenarios such as loss of communication, mechanical
failure, and loss of propulsion.

### 1.2 Restatement of the Task

The problem will be reframed as a chain of decisions that must be supported by modeling:

- **Locate** — predict where a submersible may be at any time after an emergency, quantify
  the uncertainty of that prediction, and decide what position/status information the
  submersible should transmit (and with what equipment) to shrink that uncertainty.
- **Prepare** — recommend search equipment for the host ship and for a rescue vessel,
  balancing cost, maintenance burden, and readiness.
- **Search** — recommend where and how to begin searching, and characterize the
  probability of finding the submersible as a function of time and of accumulated search
  history.
- **Extrapolate** — generalize the framework to other tourist regions (e.g., the
  Caribbean Sea) and to multiple simultaneous submersibles.

### 1.3 Characterization of the Setting

The plan will treat the problem as a stochastic, spatial, sequential-decision problem
over an underwater environment. Three physical–operational domains are expected to
interact:

1. **Submersible dynamics** (drift/buoyancy/motion after a fault).
2. **Information flow** (what can be sensed, transmitted, and received).
3. **Search operations** (sensor coverage, search patterns, and update of belief).

### 1.4 Deliverables (planned)

- A reproducible modeling framework spanning the four tasks.
- A modeling narrative suitable for the report deliverables (one-page summary, full
  solution body, and a one- to two-page memo to the Greek government).
- Documentation of assumptions, parameter sources, and validation evidence.

---

## 2. Objectives and Subproblems

### 2.1 Global Objective

To build an integrated, uncertainty-aware framework that predicts a lost submersible's
position, guides communication/equipment design, and schedules search operations so that
expected time-to-location is minimized, while remaining extensible to new regions and
multiple vehicles.

### 2.2 Subproblem Breakdown

| ID | Subproblem | Planning objective |
|----|-----------|--------------------|
| SP1 | Position prediction over time | Define state, dynamics, and probabilistic forecast of location |
| SP2 | Uncertainty quantification | Represent, propagate, and attribute uncertainty |
| SP3 | Communication design | Decide what data to transmit and what equipment enables it |
| SP4 | Host-ship equipment | Prioritize equipment by cost/effectiveness/readiness |
| SP5 | Rescue-vessel equipment | Identify complementary capabilities for recovery |
| SP6 | Initial deployment & search pattern | Choose start points and sweep geometry to minimize search time |
| SP7 | Detection probability vs. time/history | Define and update a probability-of-detection function |
| SP8 | Regional extrapolation | Transfer model to other seas |
| SP9 | Multi-vehicle extension | Adapt to several submersibles simultaneously |

### 2.3 Objective Decomposition Logic

The plan will organize SP1–SP9 into three layers:

- **Layer A — Belief layer (SP1, SP2):** a probability distribution over submersible
  location and status versus time.
- **Layer B — Information layer (SP3):** update rules that reduce Layer A uncertainty.
- **Layer C — Execution layer (SP4–SP9):** search scheduling, equipment, and
  generalization that act on Layer A.

---

## 3. Assumptions

Assumptions are grouped by domain. Each will be justified in the eventual report and
carries a proposed future validation approach.

### 3.1 Environmental Assumptions

- **A1.** Local current fields can be approximated as a smoothly varying mean flow plus
  turbulent perturbation over the relevant time horizon.
  *Justification:* standard ocean-drift practice; keeps drift tractable.
  *Validation:* compare against regional current/bathymetry products during future work.
- **A2.** Depth-dependent water density and buoyancy can be modeled with a simplified
  stratification profile.
  *Justification:* neutral-buoyancy behavior drives post-fault motion.
  *Validation:* sensitivity sweep over stratification parameter choices.
- **A3.** The seabed/boundary can be represented at the resolution needed for drift
  confinement (walls, ridges, coastline).
  *Validation:* compare coarse vs. fine geometries.

### 3.2 Vehicle and Failure Assumptions

- **A4.** At least one plausible fault mode (e.g., propulsion loss) is chosen as the
  canonical drift scenario; other modes are treated as variants.
- **A5.** The submersible retains passive buoyancy and can be modeled as a drifting body
  after fault onset, with optional surface-seeking behavior as a scenario branch.
- **A6.** Time of fault onset is known only within an interval (or is itself uncertain).

### 3.3 Communication Assumptions

- **A7.** Some low-bandwidth channel (e.g., acoustic) remains available in at least some
  scenarios; its reliability degrades with depth/range.
  *Validation:* parameterize reliability envelope and test sensitivity.
- **A8.** The host ship knows the last safe contact point/time.

### 3.4 Search Assumptions

- **A9.** Sensor detection is distance/angle dependent and captured by a detection
  function (e.g., lateral-range curve).
- **A10.** Search effort is rate-limited by vehicle speed and sensor swath.
- **A11.** Detections are conditionally independent given true target location and sensor
  geometry (a baseline that will be challenged in sensitivity analysis).

### 3.5 Modeling-Scope Assumptions

- **A12.** Two-dimensional (surface plane) planning will be the primary abstraction, with
  a vertical dimension treated as a reduced/parameterized extension.
- **A13.** Weather windows and operational downtime will be represented as scenario
  modifiers rather than fully exogenous time series in the first pass.

**Deliverable of this section:** a consolidated assumption register (ID, statement,
justification, validation action, risk if violated).

---

## 4. Data Processing Plan

### 4.1 Data Situation

The task currently provides **no attached dataset**; `data/` and `code/` are empty at
plan time. The plan will therefore distinguish:

- **Synthetic/derived data** generated from physical and operational models, and
- **External reference data** that would be sourced later (regional current fields,
  bathymetry, sample search assets, cost schedules).

### 4.2 Preprocessing Plan

1. **Geometry preparation:** define the operating area boundary, coastline, and depth
   zones; standardize coordinate systems (local metric grid vs. geographic coordinates).
2. **Environment preparation:** rasterize/standardize any candidate current and
   bathymetry layers onto a common grid and time step.
3. **Unit and reference harmonization:** depth in meters, speed in m/s or kn, distances
   in m/km, times in seconds with derived hours.
4. **Missing/degenerate handling:** rules for gaps in environment layers (interpolation
   policy) and for uncertain fault-onset times (interval representation).

### 4.3 Feature / State Construction

- **State features:** position, depth, velocity, time-since-fault, drift regime flags.
- **Environmental features:** local mean current vector, turbulence intensity, depth.
- **Operational features:** transmitter status, last-known position age, sensor
  availability, vehicle readiness state.
- **Search features:** cumulative swept area, coverage history, detection history.

### 4.4 Data Usage Strategy

- **Calibration set:** synthetic scenarios generated under baseline assumptions used to
  tune model parameters (e.g., diffusion coefficient, detection curve).
- **Scenario library:** a designed grid of environmental/fault/communication conditions
  for stress testing.
- **Held-out scenarios:** for out-of-sample checks of the belief update and search
  scheduler.
- **Reference data (future):** regional current/bathymetry products and any cost/asset
  catalogs for equipment prioritization; kept separate from synthetic calibration.

### 4.5 Provenance and Reproducibility Plan

- Record all parameter values, sources, and versions.
- Fix random seeds for any stochastic scenario generation (to be done in later phases).
- Maintain a data dictionary mapping every variable to its source and units.

---

## 5. Candidate Model Framework

### 5.1 Modeling Philosophy

The plan will adopt a **layered stochastic architecture**: dynamics generate a belief;
information updates the belief; search decisions consume the belief. Each layer will be
described with candidate methods, variables, mathematical ideas, and trade-offs.

### 5.2 Layer A — Position Prediction and Uncertainty (SP1, SP2)

**Candidate models**

- **M-A1: Deterministic drift + advection–diffusion.** Model motion as mean current
  advection plus a diffusion/random-walk term (a Fokker–Planck / Kolmogorov forward
  view).
- **M-A2: Stochastic differential-equation (SDE) drift model.** Candidate SDE with
  drift (current/buoyancy) and diffusion terms; forward solve by Monte Carlo ensemble.
- **M-A3: Monte Carlo particle ensemble ("particle cloud").** Represent belief as a
  weighted set of particles propagated with stochastic forcing. Natural bridge to
  Bayesian search.
- **M-A4: Reduced-order/analytic approximations** (e.g., Gaussian plume-like kernels)
  for speed and interpretability.

**Core variables:** position x(t), depth z(t), velocity v(t), fault-onset time t0,
current field u(x,t), diffusion coefficient D, buoyancy residual.

**Key mathematical ideas:** continuity/transport equations; independent-increment
diffusion; ensemble statistics (mean, covariance, quantiles); scenario branching for
surface-seeking vs. continued drift.

**Advantages / limitations (to weigh later):** particle ensembles are flexible and
map to Bayesian search but are computationally heavier; analytic kernels are fast but
may misrepresent boundaries and multimodal beliefs.

### 5.3 Layer B — Information and Communication (SP3)

**Candidate approaches**

- **M-B1: Value-of-Information (VoI) analysis** to decide which telemetry messages
  (position, depth, status, time) most reduce belief entropy.
- **M-B2: Entropy/information-gain metrics** over the belief distribution to quantify
  uncertainty reduction per message.
- **M-B3: Channel model** for candidate acoustic/link technologies with depth/range
  reliability envelopes; map information content to required bandwidth.

**Core variables:** message content set, transmission rate, reliability vs. depth/range,
resulting belief variance/entropy.

**Mathematical ideas:** mutual information, differential entropy, expected posterior
uncertainty, communication-rate constraints.

### 5.4 Layer C1 — Equipment and Preparedness (SP4, SP5)

**Candidate approaches**

- **M-C1: Multi-criteria decision analysis (MCDA)** (weighted scoring / AHP-style)
  across cost, maintenance, readiness, and search effectiveness.
- **M-C2: Cost–effectiveness / budget allocation model** mapping equipment choices to
  expected search-time reduction.
- **M-C3: Readiness-state model** (reliability/availability) to keep recommendations
  operationally honest.

**Core variables:** equipment capability metrics (swath, depth rating, endurance),
annualized cost, maintenance intervals, readiness probability.

### 5.5 Layer C2 — Search Scheduling (SP6, SP7)

**Candidate models**

- **M-D1: Bayesian search theory.** Maintain a prior location distribution; update with
  non-detections via a detection function; this yields posterior probability of location.
- **M-D2: Detection function model** P(detect | distance) with sweep-width/lateral-range
  characterization; supports cumulative detection probability over time.
- **M-D3: Optimal search-path planning.** Candidate structures: boustrophedon (lawnmower)
  and expanding-square patterns for baseline; dynamic/adaptive replanning where path
  decisions depend on search history; formulation as a partially observable Markov
  decision process (POMDP) or as a coverage-optimization problem.
- **M-D4: Probability-of-success (POS) curve.** Cumulative probability of detection as a
  function of elapsed search time, paired with belief updates after null results.

**Core variables:** prior belief π(x), detection function b(z), sweep rate, cumulative
swept area, posterior belief, POS(t), expected time-to-find.

**Mathematical ideas:** Bayes' rule with non-detection; optimal effort allocation over
cells (Koopman-style); coverage functions; sequential decision under uncertainty.

### 5.6 Layer C3 — Extrapolation and Multi-Vehicle (SP8, SP9)

- **M-E1: Parameterized/scaled model** where region-specific parameters (currents,
  bathymetry, traffic, depth regime) act as inputs, enabling transfer to the Caribbean.
- **M-E2: Multi-target belief** as a joint/independent distribution over several
  submersibles, with search-effort allocation across hypotheses.
- **M-E3: Scenario-based transferability assessment** to define which model components
  are region-invariant vs. region-specific.

### 5.7 Method Selection Matrix (planned)

A matrix will compare candidate models on: interpretability, fidelity, computational
cost, data demands, and suitability for the search layer. Selection will be deferred to
the modeling phase once requirements are fixed.

---

## 6. Implementation Roadmap

### 6.1 Planned Modules

1. **Environment module** — geometry, current field, depth/bathymetry handling.
2. **Dynamics module** — SDE/particle propagation and scenario branching.
3. **Belief module** — distribution representation, entropy/variance metrics, updates.
4. **Communication module** — VoI computation and channel-reliability envelope.
5. **Equipment module** — MCDA/cost–effectiveness and readiness modeling.
6. **Search module** — detection functions, Bayesian updates, path planners, POS curves.
7. **Transfer module** — parameterization for new regions and multi-vehicle extension.
8. **Orchestration/reporting module** — experiment configuration, logging, and figure
   generation (executed only in later, non-planning phases).

### 6.2 Workflow Sequence (planned)

1. Fix scope, notations, and the assumption register.
2. Build environment + dynamics modules; establish belief representation.
3. Add communication/VoI layer; produce uncertainty-reduction logic.
4. Build search module (detection, update, pathing, POS).
5. Add equipment/preparedness analysis and the government memo logic.
6. Add transfer and multi-vehicle extensions.
7. Run validation suite (Section 7) and sensitivity sweeps.
8. Assemble report artifacts (summary, body, memo).

### 6.3 Algorithms (candidate, to be selected later)

- Monte Carlo ensemble propagation; resampling for particle degeneracy.
- Grid-based Bayes update for non-detections.
- Coverage/boustrophedon and expanding-square search construction.
- Optional POMDP / dynamic programming for adaptive search (feasibility to be assessed).
- Sensitivity sampling (one-at-a-time and variance-based/Sobol-style, if affordable).

### 6.4 Interfaces and Reproducibility

- Define a common state/belief data structure shared across modules.
- Configuration-driven scenarios (parameter files) with fixed seeds.
- Log every run's parameters and version for later traceability.

### 6.5 Planned Artifact Layout

- `code/` — module implementation (later phase).
- `data/` — synthetic scenario outputs and external reference layers (later phase).
- `results/` — this planning draft, plus future intermediate and final outputs.
- `logs/` — run records (later phase).

---

## 7. Validation Strategy

### 7.1 Evaluation Metrics (planned)

- **Dynamics/belief:** calibration of prediction intervals (coverage probability),
  sharpness (interval width), and error between predicted and realized positions in
  synthetic truth runs.
- **Communication:** information gain / entropy reduction per message; robustness to
  channel loss.
- **Equipment:** cost-effectiveness ratio; ranking stability under weight changes.
- **Search:** probability of success vs. time, expected time-to-detection, and fraction
  of area covered; regret versus an idealized full-knowledge baseline.

### 7.2 Validation Methods

- **Synthetic ground-truth tests:** generate scenarios from a "truth" configuration,
  then evaluate whether the model's belief and search policy recover the target
  efficiently.
- **Internal consistency checks:** conservation of probability in the belief; correct
  Bayesian posterior behavior as detection goes to certainty/none.
- **Cross-model comparison:** analytic vs. particle representations on shared scenarios.
- **Out-of-sample scenarios:** held-out environmental/fault settings.
- **Bounds/limiting cases:** verify behavior as diffusion → 0, detection → perfect, and
  as search area → whole domain.

### 7.3 Sensitivity and Robustness Plan

- One-at-a-time sweeps over key parameters (current speed, diffusion, fault-onset
  uncertainty, detection range, sweep rate, equipment costs, readiness).
- Multi-parameter screening (e.g., variance-based) for dominant drivers.
- Scenario stress tests: strong currents, long communication loss, multiple vehicles,
  alternate regions.
- Assess stability of recommendations (equipment ranking, search start point) under
  parameter perturbation.

### 7.4 Threats to Validity (to document)

- Realism of synthetic environments vs. actual Ionian Sea conditions.
- Independence assumptions in detection and in failure modes.
- Unmodeled operational constraints (weather, crew, regulations).
- Transfer risk when applying to the Caribbean with different conditions.

---

## 8. Expected Result Interpretation

*This section describes how future outputs will be interpreted; it contains no computed
results.*

- **Position prediction outputs** will be read as probabilistic maps (or distributions)
  over location versus time, accompanied by uncertainty bands/quantiles rather than a
  single track.
- **Communication recommendations** will be interpreted as which information payloads
  yield the greatest uncertainty reduction per unit of transmission effort, framed as
  design guidance for equipment selection.
- **Equipment recommendations** will be presented as prioritized, justified lists
  balancing capability against cost, maintenance, and readiness, with explicit trade-off
  discussion rather than a single "best" item.
- **Search outputs** will be interpreted through probability-of-success curves and
  recommended initial deployment points/patterns; the value of adaptive replanning will
  be discussed relative to static patterns.
- **Extrapolation outputs** will be framed as a parameterized procedure for new regions
  and for multiple vehicles, with clearly flagged region-specific inputs.
- **Overall interpretation** will emphasize uncertainty quantification and decision
  support, suitable for a regulatory/government audience.

---

## 9. Limitations and Improvements

### 9.1 Anticipated Limitations

- **Simulation dependence:** without real incident data, validation will rely on
  synthetic truth and must be presented cautiously.
- **Model fidelity trade-offs:** simplified ocean physics and 2D abstraction may omit
  important vertical and boundary effects.
- **Computational scale:** particle/Bayesian methods and adaptive search may be
  expensive for large domains or many vehicles.
- **Assumption sensitivity:** conclusions may hinge on detection-function and
  current-field assumptions.
- **Transfer uncertainty:** regional generalization may require substantial
  re-parameterization.

### 9.2 Planned Improvements

- Incorporate real regional current/bathymetry datasets and, if obtainable, historical
  search/incident statistics.
- Add 3D or depth-layer treatment and refined boundary handling.
- Move from static to adaptive (POMDP/online) search policies if feasible.
- Add structured uncertainty propagation (e.g., hierarchical priors over environment
  parameters).
- Extend multi-vehicle modeling to coordination and shared-information search.
- Strengthen validation with external benchmarks or expert review where possible.

### 9.3 Risk Register (planned)

| Risk | Impact | Planned mitigation |
|------|--------|--------------------|
| Weak validation data | Reduced credibility | Emphasize synthetic-truth validation + sensitivity + bounds |
| Excessive model complexity | Unfinished deliverables | Staged layering; defer adaptive search until core validated |
| Parameter ambiguity | Unstable recommendations | Robustness sweeps + ranking-stability checks |
| Transfer misapplication | Wrong regional guidance | Explicit region-specific vs. invariant component list |

---

## Appendix A — Planning Checklist

- [ ] Assumption register consolidated and justified.
- [ ] Candidate models compared via selection matrix.
- [ ] Data provenance and data dictionary established.
- [ ] Module interfaces defined.
- [ ] Validation and sensitivity suites specified.
- [ ] Reporting artifacts (summary / body / government memo) outlined.

## Appendix B — Scope Note

This document is a **modeling blueprint / planning draft only**. It intentionally
contains no computed values, no data analysis, no fitted models, no executed
experiments, no plots, and no final conclusions. All quantitative work is deferred to
subsequent modeling phases.
