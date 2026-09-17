# Modeling Blueprint Draft — A South Sea Island Resort
### (HiMCM 2006, Problem 2006_A_South_Sea)

> **Status:** Planning-only draft. This document is a *roadmap* for future modeling work.
> It contains no computed results, no executed analysis, and no final conclusions.
> All statements are written in future-oriented language and are intended to be
> refined, validated, or replaced during subsequent modeling rounds.

---

## 1. Problem Background and Restatement

An island chain intends to convert one of its islands into a resort. The island is
described as roughly circular, approximately 5 km across, and dominated by a single
mountain that covers almost the entire island. The mountain will be treated as
approximately conical, with an approximate height on the order of 1000 m at the
center, an apparently sandy composition, and little vegetation. The proposed plan is
to lease fire-fighting ships and to *wash the mountain into the harbor* using directed
streams of water. The stated objective is to accomplish this removal as quickly as
possible.

The following questions will be addressed by the eventual model:

1. **Stream direction over time.** How should the water stream be aimed at the
   mountain as a function of time so that the mountain is removed efficiently?
2. **Single-ship duration.** How long would the removal take if a single
   fire-fighting ship were used?
3. **Multi-ship scaling.** Would using 2, 3, 4, … ships reduce the total time by more
   than a factor of 2, 3, 4, … respectively (i.e., is there super-linear or
   sub-linear scaling)?
4. **Recommendation.** What course of action should be recommended to the resort
   committee?

This draft will map the geometry, the physics of sand removal and transport, the
control problem of aiming the jet, and the multi-agent (multi-ship) scaling question
into a coherent modeling workflow.

---

## 2. Objectives and Subproblems

### 2.1 Overall objective
To construct a model that predicts the evolution of the island's terrain under
directed water-jet erosion and that supports a time-optimal strategy for one or more
fire-fighting ships, culminating in a committee-facing recommendation.

### 2.2 Subproblems (to be decomposed during modeling)

- **S1 — Geometry & representation.** Establish a tractable geometric
  representation of the conical mountain and the target (post-removal) terrain,
  including the island boundary and the harbor drainage direction.
- **S2 — Jet–sand interaction.** Characterize the local material-removal rate of a
  water jet as a function of controllable parameters (flow rate/pressure, nozzle
  standoff, impingement angle, height above the surface) and sediment properties.
- **S3 — Sediment transport & drainage.** Represent how loosened sand is carried to
  the harbor, including the possibility of a bottleneck (channel capacity,
  re-deposition, harbor clearance).
- **S4 — Terrain evolution law.** Formulate the time evolution of the terrain
  height field under one or more jets (a rate/transport law, likely an
  ordinary/partial differential description or a discretized update rule).
- **S5 — Optimal aiming policy.** Determine the stream direction (and its schedule)
  that minimizes total removal time, potentially as an optimal-control or
  scheduling problem.
- **S6 — Multi-ship scaling.** Model interactions among multiple ships (overlap,
  interference, shared drainage, access/geometry limits) to predict how completion
  time scales with the number of ships.
- **S7 — Recommendation synthesis.** Translate the modeled trade-offs (time, cost,
  feasibility, risk) into a defensible recommendation framework.

### 2.3 Deliverables (future artifacts)
- A documented model formulation (assumptions + equations/rules).
- A simulation or solver harness able to produce terrain-evolution trajectories.
- A comparison of aiming strategies and of 1…N ship configurations.
- A sensitivity/robustness assessment.
- A recommendation memo grounded in the model's comparative outputs.

---

## 3. Assumptions

Assumptions are grouped by purpose. Each will carry an explicit justification and a
plan for later validation or relaxation.

### 3.1 Geometric / environmental assumptions
- **A1.** The mountain will be modeled as a right circular cone (possibly truncated)
  with base diameter on the order of the island diameter and apex height on the
  order of the stated elevation; a more general surface (e.g., convex profile) will
  be considered as a refinement.
  *Justification:* the statement describes the mountain as "approximately conical."
  *Validation:* compare idealized cone outcomes against a curved-profile variant.
- **A2.** The island is surrounded by water and bounded; the harbor will be
  represented as a designated drainage sink (sector or boundary) where removed sand
  is deposited or carried away.
  *Validation:* test alternate sink geometries and capacities.
- **A3.** Sea level / waterline and harbor water depth will be treated as fixed
  reference levels; tidal and wave effects will initially be neglected and later
  probed as perturbations.
- **A4.** The target end-state (what "washed away" means — full removal vs. removal
  below a threshold height/slope) will be parameterized rather than fixed.

### 3.2 Material / physical assumptions
- **A5.** The mountain material behaves as loosely consolidated, cohesionless sand
  (low vegetation, low cohesion), so erosion is dominated by fluid-jet momentum and
  gravity-driven slumping rather than by rooted vegetation or rock strength.
- **A6.** Removal rate at a point is increasing in delivered jet energy/momentum and
  decreasing in standoff distance and in the local slope resisting transport;
  a phenomenological rate law will be used and calibrated against plausible ranges.
- **A7.** Loosened material either (a) is immediately transported to the harbor, or
  (b) accumulates in a converging channel whose throughput may become a bottleneck;
  the degree of bottleneck behavior will be a modeling choice to be tested.
- **A8.** Water supply from ships is effectively unlimited over operational
  timescales; the binding constraints are jet performance, drainage throughput,
  and access geometry rather than water availability.

### 3.3 Operational assumptions
- **A9.** A "fire-fighting ship" will be characterized by a small set of
  controllable/quantified attributes (deliverable flow rate, achievable pressure,
  attainable standoff, maneuverability, repositioning time).
- **A10.** Ships are interchangeable and may operate concurrently; excluding
  interactions, a single-ship model is assumed to compose additively for multiple
  ships (this assumption is precisely what S6 will test rather than accept).
- **A11.** Operational time is continuous and no explicit labor/shift/weather
  interruptions are modeled initially.

### 3.4 Justification & validation approach (cross-cutting)
- Assumptions with strong geometric or physical grounding (A1, A5) will be
  justified from the problem statement and general sand-erosion mechanics.
- Assumptions that carry the most modeling risk (A6 rate law, A7 bottleneck, A10
  additivity) will be flagged as *high-uncertainty* and subjected to dedicated
  sensitivity analysis (Section 7).

---

## 4. Data Processing Plan

No numeric datasets are bundled with the provided statement; the plan therefore
describes how *inputs* will be sourced, encoded, and organized, and how *synthetic*
or literature-based values will be used as placeholders pending calibration.

### 4.1 Input acquisition
- **Given parameters:** extract the stated quantities from the problem — island
  diameter (~5 km), center height (~1000 m), conical/ sandy description — and record
  them as *nominal* values with explicit uncertainty ranges.
- **External parameters (to be researched during modeling):** fire-fighting ship
  flow rate/pressure/nozzle characteristics; typical sand grain size, density,
  angle of repose, and critical shear/erosion thresholds; representative jet
  impingement erosion behavior.
- **Derived parameters:** total removable volume proxy, base slope, harbor distance,
  sediment concentration limits, channel capacity.

### 4.2 Preprocessing
- Convert all quantities to a single consistent unit system (SI).
- Build a parameter table with columns: symbol, nominal value, plausible range,
  source/basis, confidence.
- Flag each parameter as *fixed*, *tunable*, or *uncertain* to drive later
  sensitivity analysis.

### 4.3 Feature / state construction
- Define the terrain state as a height field (or radial profile) over a spatial grid.
- Derive auxiliary features used by the rate law: local slope, distance from jet,
  impingement angle, downstream transport path length, cumulative removed volume.
- Define *outcome features* for comparison: total completion time, peak throughput,
  residual unmet geometry.

### 4.4 Data usage strategy
- Since no measured terrain-evolution data is available, the model will be
  *calibrated by plausibility* (literature ranges) and validated by *internal
  consistency* rather than by fitting to observations.
- Any future observational data (e.g., pilot removals, hydraulic lab tests) will be
  integrated as calibration/validation points; the preprocessing pipeline will be
  built to accept them without structural change.

---

## 5. Candidate Model Framework

Several model families will be considered, spanning simpler analytic descriptions to
fuller numerical simulations. The modeling workflow is expected to proceed from
coarse to fine, using simple models to sanity-check complex ones.

### 5.1 Model family A — Lumped / geometric volume-removal model
- Represent the mountain by its volume and track a single lumped removal rate.
- Postulate a governing relation such as a first-order removal law where the removed
  volume rate depends on delivered jet power, material resistance, and geometry.
- **Use:** rapid order-of-magnitude reasoning; baseline for multi-ship scaling logic.
- **Advantages:** transparent, analytic, easy to interrogate.
- **Limitations:** ignores spatial geometry, aiming, and bottlenecks.

### 5.2 Model family B — Continuum terrain-evolution (rate) model
- Model the terrain height as a function of space and time; a PDE-style or
  radial-profile evolution law describes how removal and slumping lower the surface.
- Couple a local removal term (driven by jet position/intensity) with a transport /
  relaxation term (gravity-driven downslope movement toward the harbor).
- **Use:** spatially resolved prediction of shape evolution and completion time.
- **Advantages:** captures aiming, shape change, and self-accelerating exposure.
- **Limitations:** requires rate-law calibration; more parameters.

### 5.3 Model family C — Discrete / cellular terrain simulation
- Discretize the island into a grid (or radial cells) and apply local update rules
  each timestep: water delivered → sand loosened → sand moved → terrain lowered.
- Naturally supports multiple jets, overlapping influence zones, and drainage limits.
- **Use:** flexible scenario testing for multi-ship configurations.
- **Advantages:** intuitive, handles heterogeneous rules and bottlenecks.
- **Limitations:** grid/schedule artifacts; computational cost; needs validation.

### 5.4 Model family D — Optimal-control / scheduling formulation
- Treat jet direction as a control input; seek the control schedule that minimizes
  completion time (or maximizes removed volume per unit time) subject to dynamics
  from family B or C and to operational constraints.
- Consider greedy heuristics (aim where marginal removal is highest), time-optimal
  bang-bang style strategies, and sweep patterns.
- **Use:** answers "how should the stream be directed as a function of time?"
- **Advantages:** directly targets the stated optimization objective.
- **Limitations:** non-convexity, dependence on the underlying dynamics model.

### 5.5 Model family E — Multi-agent scaling model
- Extend B/C/D to k concurrent ships with (i) shared drainage, (ii) jet overlap and
  mutual interference, (iii) finite useful surface area/target access.
- Predict completion time T(k) and the ratio T(1)/T(k) versus k, to test whether
  time drops by more than a factor of k (super-linear gain) or less (sub-linear).
- **Use:** answers questions 3 and 4.

### 5.6 Variables (to be formalized)
- **State:** terrain height field / radial profile; cumulative removed volume;
  sediment in transit; harbor/channel loading.
- **Control:** jet aim direction and elevation; standoff; sweep schedule; active
  ship set and assignments.
- **Parameters:** jet flow rate/pressure/nozzle; material properties; harbor/channel
  capacity; number of ships k; target end-state.
- **Outputs:** completion time; volume-time trajectory; residual geometry; marginal
  productivity of additional ships.

### 5.7 Mathematical ideas (candidate toolkit)
- Volume/geometry relations for cones and truncations.
- Rate laws and (nonlinear) ODE/PDE evolution; possibly kinematic-wave / transport
  analogies for the slurry channel.
- Optimal control and scheduling; monotone/greedy search for aiming.
- Dimensional analysis and scaling arguments for multi-ship behavior.
- Discrete-time simulation as a common integrative layer.

### 5.8 Cross-model strategy
- Start with family A to establish scale and the qualitative multi-ship logic.
- Use family B/C for spatially resolved trajectories and validation of A's limits.
- Layer family D on top of B/C to generate aiming policies.
- Use family E to produce the T(k) scaling curve and the committee recommendation.

---

## 6. Implementation Roadmap

Implementation is planned in modular stages so each component can be tested in
isolation before integration. (No code will be written or run in this planning phase.)

### 6.1 Proposed modules
- **M1 — Parameter & unit manager:** holds nominal/uncertain parameters with ranges;
  supports scenario overrides.
- **M2 — Geometry engine:** constructs the idealized cone/truncated-cone and any
  refined profile; computes volumes and slopes; provides the discretized grid.
- **M3 — Jet–material model:** maps jet aim/standoff/flow to a local removal rate.
- **M4 — Terrain evolution integrator:** advances the height field over time under a
  chosen rate law and transport rule.
- **M5 — Transport/drainage module:** routes removed material to the harbor and
  enforces any capacity/bottleneck constraints.
- **M6 — Controller/policy module:** implements aiming strategies (greedy, sweep,
  scheduled) and, optionally, an optimization loop.
- **M7 — Multi-ship orchestrator:** instantiates k ships, assigns regions/targets,
  applies interaction rules.
- **M8 — Experiment driver & reporting:** runs scenario batches, aggregates outcomes
  (time, trajectories, scaling), produces comparable outputs.

### 6.2 Staged workflow
1. **Stage 0 — Formulation lock-in:** finalize assumptions and the candidate model(s)
   to be explored first; freeze units and parameter tables.
2. **Stage 1 — Single-jet, single-ship baseline:** implement M1–M4(+M5) with a fixed
   aim to obtain a baseline removal trajectory.
3. **Stage 2 — Aiming policy:** add M6; compare heuristic aiming rules to a greedy
   "highest marginal removal" policy and, if feasible, a simplified optimal-control
   search.
4. **Stage 3 — Multi-ship scaling:** add M7; compute T(k) for k = 1,2,3,4,… under
   different interaction assumptions (shared drainage, overlap, access limits).
5. **Stage 4 — Scenario & sensitivity sweep:** drive M8 across parameter ranges and
   assumption variants; collect robustness statistics.
6. **Stage 5 — Synthesis:** translate comparative outputs into the recommendation
   framework; document limitations.

### 6.3 Tooling expectations
- A general-purpose scientific computing stack (numeric arrays, ODE/PDE integration,
  lightweight optimization, plotting for internal diagnostics).
- Configuration-driven runs so that assumptions/parameters can be varied without
  editing core logic.
- Reproducibility: fixed seeds, versioned parameter files, and logged run metadata.

### 6.4 Milestone checks (planned)
- Milestone 1: baseline single-jet trajectory reproduces expected monotone volume
  decrease within plausible bounds.
- Milestone 2: an aiming policy measurably improves removal rate over fixed aiming
  (qualitative check, to be quantified later).
- Milestone 3: T(k) curve is produced and the sign of its marginal-gain behavior is
  characterized, not assumed.
- Milestone 4: sensitivity sweep completed and documented.

---

## 7. Validation Strategy

### 7.1 Evaluation metrics (candidate)
- **Completion time** to reach the target end-state.
- **Volume-removal trajectory** and **instantaneous removal rate** over time.
- **Marginal productivity** of the k-th ship (Δ(1/T) per added ship).
- **Scaling exponent / ratio** comparison of T(1)/T(k) against k.
- **Residual geometry error** relative to the desired end-state.

### 7.2 Validation methods
- **Dimensional analysis & limiting cases:** verify that model outputs behave
  correctly as jet power, standoff, mountain size, or ship count approach extremes
  (e.g., negligible delivered energy ⇒ negligible removal).
- **Consistency / conservation checks:** removed volume must match material routed to
  the harbor (accounting for in-transit storage); no spurious mass creation/loss.
- **Cross-model agreement:** compare lumped (A) against continuum (B) and discrete
  (C) results under matched parameters; investigate divergences.
- **Monotonicity & plausibility:** removal rate should increase with delivered power,
  decrease with standoff, and (all else equal) completion time should
  non-increase with more ships.
- **Internal reproducibility:** independent runs of the same configuration agree
  under fixed seeds/settings.

### 7.3 Sensitivity & uncertainty analysis
- **One-at-a-time sweeps** over the highest-uncertainty parameters (A6 rate law,
  A7 bottleneck, material properties, jet performance).
- **Global / multi-parameter exploration** (e.g., sampling across ranges) to map
  which assumptions dominate completion time and the T(k) scaling.
- **Structural sensitivity:** re-run key scenarios under alternate assumptions
  (immediate transport vs. bottleneck; additive vs. interfering jets; cone vs.
  curved profile) to test whether conclusions are robust to modeling choices.
- **Scenario analysis** for realistic ship configurations and cost/time trade-offs.

### 7.4 Robustness criteria (planned)
Findings will be considered robust only if the *qualitative* ordering of strategies
and the *sign* of the multi-ship marginal-gain behavior persist across the range of
tested assumptions and parameter values. Precise quantitative times will be reported
only as ranges/with uncertainty in later rounds.

---

## 8. Expected Result Interpretation

This section describes how future outputs will be read and what forms of answers are
anticipated — without asserting any specific values.

- **Stream direction over time:** the model is expected to yield a *policy* (or
  family of policies) for aiming — e.g., concentrating on high-marginal-removal
  regions and progressively descending/refocusing as the terrain flattens — expressed
  as a function of time or of the evolving terrain state. Alternative policies will
  be compared on removal rate and completion time.
- **Single-ship duration:** the model will produce an estimate (with credible range)
  of the total time for one ship, together with the dominant drivers of that estimate
  and how tightly it is constrained by the assumptions.
- **Multi-ship scaling:** the model will produce a T(k) relationship and interpret the
  ratio T(1)/T(k) relative to k. Two qualitatively different regimes will be
  distinguished: gains *at least proportional* to ship count (near- or super-linear
  speed-up) versus *diminishing returns* (sub-linear speed-up), with the mechanism
  (drainage bottleneck, jet overlap/interference, limited useful target area,
  access/maneuvering constraints) identified as the cause.
- **Recommendation:** the committee-facing recommendation will be framed as a
  decision under uncertainty, weighing time-to-completion, number of ships, cost,
  and operational risk, and will state the conditions under which each option
  (few vs. many ships) is preferable.

Interpretation will emphasize *comparative and directional* conclusions
(which strategy is better, and why) over single point estimates, and will explicitly
separate assumption-dependent findings from assumption-robust ones.

---

## 9. Limitations and Improvements

### 9.1 Anticipated limitations
- **No empirical calibration data:** the rate law and material parameters will rely on
  literature ranges and plausibility, so absolute time estimates will carry
  substantial uncertainty.
- **Idealized geometry:** the conical representation and uniform material neglect
  natural terrain variability, internal structures, and the possibility of exposed
  harder material.
- **Simplified transport/drainage:** a single channel or sink may miss real
  sediment dynamics (re-deposition, plumes, current-driven dispersal).
- **Interaction modeling:** assumptions about jet overlap, interference, and access
  for multiple ships may significantly affect the T(k) conclusion.
- **Environmental/operational omissions:** tides, waves, weather, and human
  operational constraints are initially excluded.
- **Ecological/regulatory effects:** broad environmental impact of washing an island
  into a harbor is outside the core model.

### 9.2 Planned improvements
- Incorporate a higher-fidelity *material/erosion law*, ideally calibrated to
  hydraulic or field data if any can be sourced.
- Replace the idealized cone with a *curved/variable profile* and possibly a
  digitized terrain model.
- Add a *channel hydrodynamic/transport* submodel (kinematic wave or similar) to
  better represent bottlenecks and re-deposition.
- Upgrade multi-ship interaction from additive to *explicit interference and
  scheduling* rules informed by access geometry.
- Introduce *stochastic elements* (parameter uncertainty, operational interruptions)
  to produce confidence intervals rather than point estimates.
- Add an *economic/decision layer* (cost of ships, operational duration, risk) to
  sharpen the recommendation.
- Extend scope to *environmental impact assessment* (sediment plume, harbor
  siltation, ecosystem effects) for a more complete committee recommendation.

### 9.3 Open questions to resolve in later rounds
- What exactly constitutes the target end-state (full removal vs. threshold)?
- To what extent is drainage/transport the true bottleneck versus jet delivery?
- Does multi-ship operation exhibit genuine super-linear speed-up, or do physical
  coupling effects force sub-linear returns?
- How sensitive is the recommendation to the assumed jet/material parameters?

---

*End of planning draft. No problem solving, data analysis, computation, or final
conclusions are included by design; all content above is a roadmap for future
modeling rounds.*
