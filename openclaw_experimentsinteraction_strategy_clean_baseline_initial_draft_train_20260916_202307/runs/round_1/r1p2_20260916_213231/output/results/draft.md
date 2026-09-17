# Modeling Blueprint Draft — Forest Service Wildfire Resource Allocation

**Problem ID:** `2001_Forest_Service`
**Title:** Forest Service
**Source:** HiMCM 2001
**Document type:** Initial modeling plan draft (blueprint only — no solution, no computation, no results)

> This document is a *roadmap*. It proposes how a future modeling effort *should* be structured. It deliberately contains no numerical answers, no fitted models, and no final conclusions.

---

## 1. Problem Background and Restatement

The Forest Service must allocate firefighting resources against wildfires in a wilderness area during the upcoming dry season.

Restated setting (as given, to be assumed going forward):

- The wilderness area is a square region, **80 km on a side**.
- A rectangular grid of north–south and east–west firebreaks already exists across the interior, spaced at **5 km intervals**.
- Wildfires are most likely during the **dry season (July–September)**.
- A **prevailing westerly wind** blows throughout the day.
- Fires are frequently ignited by **lightning bursts**.
- The Service plans to deploy **four firefighting units** for the next dry season.
- Each unit comprises: **10 firefighters, 1 pickup truck, 1 dump truck, 1 water truck (50,000 L), 1 bulldozer (with truck + trailer)**, plus chainsaws, hand tools, and other equipment.
- **Personnel can be moved quickly by helicopter** within the wilderness area; **all equipment must be driven along existing firebreaks**.
- **One helicopter** is on standby at all times during the dry season.
- Base camps for the units may be placed **anywhere within the area**.

Two deliverables are requested:

1. The **best distribution of the four firefighting units** within the wilderness area.
2. A **damage assessment forecast** — estimating the amount of wilderness likely to burn, and serving as a mechanism to decide **when additional units must be brought in from elsewhere**.

Future modeling work will need to interpret "best distribution" in terms of an explicitly defined objective (for example, minimizing expected burned area, minimizing worst-case response time, or maximizing coverage of fire-prone regions), and to interpret "damage assessment forecast" as a predictive/probabilistic tool rather than a single number.

---

## 2. Objectives and Subproblems

### 2.1 Primary objectives

- **O1 — Allocation (deployment) objective:** Determine a placement scheme for the four units (base camp locations, and possibly a response/movement policy) that best protects the wilderness area under the stated wind, ignition, and infrastructure conditions.
- **O2 — Damage assessment objective:** Build a forecasting mechanism that estimates the amount of wilderness likely to burn under a given unit deployment, and that supports decisions about requesting additional units.

### 2.2 Subproblems to be decomposed

- **S1 — Spatial discretization:** Representing the 80×80 km area and the 5 km firebreak grid as a tractable computational structure.
- **S2 — Ignition modeling:** Characterizing where and how often lightning-ignited fires start (spatial intensity + seasonal/temporal pattern).
- **S3 — Fire spread modeling:** Describing how a fire grows and propagates under westerly wind, fuel type (small trees and brush), and grid/firebreak constraints.
- **S4 — Suppression/response modeling:** Representing detection, helicopter transport of personnel, ground transport of equipment along firebreaks, containment capability, and water/equipment limits.
- **S5 — Deployment optimization:** Choosing base camp locations (and response rules) for the four units to optimize the chosen objective.
- **S6 — Damage forecast construction:** Producing expected burned-area estimates and a decision rule/threshold for escalating to additional units.
- **S7 — Validation and sensitivity:** Testing robustness of the allocation and the forecast to assumption changes.

### 2.3 Deliverable mapping

| Deliverable | Supported by subproblems |
|---|---|
| Best unit distribution | S1, S2, S3, S4, S5 |
| Damage assessment forecast | S1, S2, S3, S6 |
| Escalation guidance | S6, S7 |

---

## 3. Assumptions

Each assumption is paired with a justification and a planned future validation approach. Assumptions are grouped so they can be revisited independently.

### 3.1 Geometry and infrastructure

- **A1:** The wilderness is idealized as a flat 80×80 km square; the firebreak grid is a uniform 5 km lattice covering the interior.
  - *Justification:* The statement explicitly gives these values.
  - *Validation:* Check sensitivity to treating the grid as a finer/coarser lattice, and to perimeter fractions that lie outside the interior grid.
- **A2:** Vehicles travel only along the firebreak network (Manhattan/grid movement), not off-road.
  - *Justification:* "All the equipment must be driven via the existing firebreaks."
  - *Validation:* Compare grid-constrained travel with a relaxed Euclidean-access variant.

### 3.2 Fire behavior

- **A3:** Wind is predominantly westerly with constant nominal direction during the day; speed may be treated as a parameter (or a distribution) rather than a fixed value.
  - *Justification:* "There is a prevailing westerly wind throughout the day."
  - *Validation:* Sweep wind speed/direction; test occasional shifts.
- **A4:** Fuel is homogeneous small trees and brush, so a single or few nominal fuel/spread parameters can represent the area.
  - *Justification:* Statement describes uniform vegetation.
  - *Validation:* Introduce 2–3 fuel classes and measure effect on allocation.
- **A5:** Fire spread can be represented by a discrete cell-to-cell process (e.g., grid/CA-style) with a wind-biased, fuel-dependent rate.
  - *Justification:* Grid infrastructure and square domain make a cellular representation natural.
  - *Validation:* Cross-check against a continuous front (Huygens/level-set) approximation.

### 3.3 Ignition

- **A6:** Lightning ignitions follow a spatial point process (e.g., inhomogeneous Poisson) with a seasonal intensity; multiple ignitions are possible.
  - *Justification:* "Frequent lightning bursts that cause wildfires."
  - *Validation:* Vary intensity and clustering; compare uniform vs. terrain/cluster-biased ignition maps.

### 3.4 Resources and operations

- **A7:** Units are homogeneous in capability; each can suppress/fire-line at some rate limited by personnel, water (50,000 L), and bulldozer line construction.
  - *Justification:* Each unit is described with identical composition.
  - *Validation:* Test asymmetric/reinforced units.
- **A8:** Personnel move essentially instantaneously (or with fixed delay) by the single standby helicopter; equipment moves at grid-road speeds.
  - *Justification:* "People can be quickly moved by helicopter… equipment must be driven."
  - *Validation:* Parameterize transport delays; test helicopter availability conflicts when multiple fires occur.
- **A9:** Base camps can be placed anywhere inside the area (not restricted to grid nodes, though grid nodes are a convenient candidate set).
  - *Justification:* "…set up base camps for those units at sites anywhere within the area."
  - *Validation:* Compare continuous vs. grid-node candidate placement.

### 3.5 Temporal and decision scope

- **A10:** The planning horizon is one dry season (July–September), modeled as a sequence of fire events rather than a single fire.
  - *Justification:* Deployment is "during the next dry season."
  - *Validation:* Vary season length and event rate.
- **A11:** "Best" is defined by an explicit chosen objective function (to be fixed early in the modeling effort), e.g., expected burned area minimization, possibly with a worst-case/robustness term.
  - *Justification:* "Best distribution" is otherwise ambiguous.
  - *Validation:* Re-run optimization under alternative objectives and compare solutions.

---

## 4. Data Processing Plan

> The problem provides a narrative statement rather than a dataset. The plan therefore centers on constructing a synthetic/parametric data layer consistent with the statement, and on documenting all derived inputs.

### 4.1 Inputs to be established

- **Domain representation:** An 80×80 km square discretized into cells; a derived representation of the 5 km firebreak lattice.
- **Fuel model parameters:** Nominal spread-rate/flammability parameters for "small trees and brush."
- **Wind parameters:** Nominal westerly speed and direction; optional variability envelopes.
- **Ignition parameters:** Seasonal ignition intensity and spatial distribution over the domain.
- **Resource parameters:** Per-unit suppression rate, water capacity, line-construction rate, transport speeds, helicopter service model.

### 4.2 Preprocessing steps (planned)

1. **Discretization and indexing:** Build the cell grid and road network graph; precompute adjacency, distances, and grid-road travel times between candidate base sites and cells.
2. **Candidate site enumeration:** Define a candidate set for base camps (e.g., grid nodes, cell centroids, or a refined mesh) for the optimization stage.
3. **Scenario generation:** Define procedures to generate stochastic fire scenarios (ignition time/location, wind realization, event multiplicity).
4. **Parameter bookkeeping:** Centralize all parameters in one configuration object so that scenarios/sensitivity runs are reproducible.
5. **Documentation:** Record sources/rationale for every assumed value (statement-derived vs. literature-derived vs. assumed).

### 4.3 Feature construction

- Spatial features: distance to nearest road, distance to westerly upwind boundary, cell connectivity, "fire arrival time" fields.
- Risk features: expected ignition density per cell, expected downwind exposure.
- Access features: travel time from each candidate base to each cell (by road, plus helicopter for personnel).
- Operational features: per-cell suppression feasibility, water-limited coverage radius.

### 4.4 Data usage strategy

- No historical dataset is assumed. Where external parameters are needed (e.g., typical fire spread rates for brush), they will be cited as documented assumptions and then stress-tested.
- All synthetic scenarios will be generated from a fixed random seed set so that allocation comparisons are fair and reproducible.

---

## 5. Candidate Model Framework

The framework is organized as a layered pipeline so that components can be swapped and compared.

### 5.1 Layer A — Spatial/network representation

- **Candidates:** (a) cell grid graph; (b) road-network graph for equipment; (c) combined graph with helicopter links for personnel.
- **Variables:** cell states (unburned/burning/burned), road-graph distances, travel times.
- **Ideas:** graph shortest paths; Manhattan metric on the lattice; Voronoi-like service regions.
- **Advantages/Limitations:** Graph models are tractable and match the firebreak constraint; they may oversimplify off-grid terrain effects.

### 5.2 Layer B — Fire ignition model

- **Candidates:** inhomogeneous Poisson point process; seasonal (non-homogeneous) temporal process; optional clustering (Bartlett/Cox-type) for "bursts."
- **Variables:** ignition intensity λ(x,t), event count, clustering parameters.
- **Advantages/Limitations:** Poisson is tractable and matches "frequent lightning"; clustering adds realism at higher complexity.

### 5.3 Layer C — Fire spread model

- **Candidates:**
  - (C1) **Cellular automaton / discrete-time spread** with wind-biased probabilities (e.g., directional weights favoring eastward advance).
  - (C2) **Level-set / Huygens front propagation** with wind-elongated ellipse spread.
  - (C3) **Empirical/percolation-style spread** on the grid with suppression as a competing process.
- **Variables:** per-cell spread rate, wind factor, directional bias, arrival times.
- **Ideas:** anisotropic neighbor weighting; effective wind-driven spread ellipse; burn-probability fields.
- **Advantages/Limitations:** CA is simple, interpretable, and grid-friendly; level-set is smoother/continuous but heavier; empirical models are fast but less mechanistic.

### 5.4 Layer D — Suppression / response model

- **Candidates:** deterministic containment model (suppression rate vs. fire perimeter growth); stochastic containment probability; queueing model for simultaneous incidents.
- **Variables:** detection delay, personnel deployment time (helicopter), equipment arrival time (road), suppression rate, water budget, containment success.
- **Ideas:** fireline construction rate vs. fire perimeter growth rate; "containment if suppression ≥ growth"; water-limited total suppression work.
- **Advantages/Limitations:** Deterministic models are analyzable; stochastic/queueing models capture multi-fire contention but require more assumptions.

### 5.5 Layer E — Deployment optimization

- **Candidates:**
  - (E1) **Facility-location / k-median / k-center style** formulation (four facilities = four base camps) minimizing expected/ worst-case response or burned area.
  - (E2) **Coverage-maximization** formulation (maximize protected area/risk-weighted coverage within a response-time threshold).
  - (E3) **Simulation-optimization** (heuristic search over placements using the fire+suppression simulator as the objective evaluator).
  - (E4) **Multi-objective / robust optimization** balancing expected damage and worst-case damage.
- **Variables:** base camp coordinates (or chosen grid nodes), assignment rules, response thresholds.
- **Ideas:** expected burned area as a function of placement and response time; risk-weighted spatial coverage; robust/min-max variants.
- **Advantages/Limitations:** Location models are clean and fast but may abstract fire dynamics; simulation-optimization is faithful but computationally heavier.

### 5.6 Layer F — Damage assessment forecast

- **Candidates:** Monte-Carlo scenario simulation producing burned-area distributions; regression/surrogate model mapping conditions → expected burned area; threshold/decision rule for escalation.
- **Variables:** burned area (per event, per season), exceedance probabilities, escalation triggers.
- **Ideas:** expected value + tail risk (e.g., high quantiles) as decision inputs; simple surrogate models trained on simulator outputs to enable fast "when to call for more units" guidance.
- **Advantages/Limitations:** Monte-Carlo gives distributional insight but needs many runs; surrogates speed decisions but need validation.

### 5.7 Integrated candidate architectures

- **Architecture 1 (analytical-first):** location model (Layer E1/E2) with simplified spread/response proxies. Fast, transparent.
- **Architecture 2 (simulation-first):** CA/level-set fire sim (Layer C) + suppression sim (Layer D) + search-based placement (Layer E3). Faithful, heavier.
- **Architecture 3 (hybrid):** fast proxies for optimization, then verify top candidates with the full simulator and build the forecast surrogate (Layer F).

---

## 6. Implementation Roadmap

### 6.1 Modules to build

1. **Domain & network module:** grid construction, road graph, distance/time precomputation, candidate site generation.
2. **Scenario generator:** ignition, wind, and event-multiplicity sampling with seeded reproducibility.
3. **Fire-spread engine:** choosable CA or level-set implementation with parameter hooks.
4. **Suppression/response engine:** detection/transport/suppression/water accounting.
5. **Objective & metrics module:** expected burned area, response time, risk-weighted coverage, tail-risk metrics.
6. **Optimization driver:** facility-location solver and/or simulation-optimization loop.
7. **Forecast module:** Monte-Carlo aggregation + surrogate/regression + escalation threshold logic.
8. **Reporting & visualization module:** maps of allocation, scenario summaries, sensitivity charts (to be generated only in the *solving* stage, not now).

### 6.2 Workflow (planned sequence)

1. Fix the objective definition(s) and the discretization resolution.
2. Implement and unit-test the domain/network module.
3. Implement a baseline fire-spread engine and sanity-check qualitative behavior (directionally correct spread under westerly wind) — no results reported here.
4. Add the suppression/response engine and verify resource-conservation logic.
5. Implement the objective/metrics module.
6. Run the placement optimization under a simplified proxy; produce candidate deployments.
7. Evaluate top candidates with the full simulator across many scenarios.
8. Build the damage forecast (distributions + escalation rule) from simulated outcomes.
9. Perform sensitivity/robustness analysis and, if time allows, a multi-objective trade-off study.
10. Document assumptions, parameters, and reproducible seeds.

### 6.3 Engineering considerations

- **Modularity:** each layer behind a clear interface so alternatives (CA vs. level-set; deterministic vs. stochastic suppression) can be swapped.
- **Reproducibility:** central config, seeded RNG, versioned scenario sets.
- **Scalability:** choose grid resolution balancing fidelity and runtime; cache distances/travel times; consider vectorized/parallel scenario evaluation.
- **Complexity guards:** start with minimal viable models, then enrich only where sensitivity indicates it matters.

---

## 7. Validation Strategy

### 7.1 Evaluation metrics (candidate)

- Expected burned area per fire and per season.
- Worst-case / high-quantile burned area (tail risk).
- Response time (personnel and equipment) to ignition points.
- Risk-weighted coverage fraction within a response threshold.
- Containment success rate / number of fires controlled before threshold size.
- Robustness gap across scenarios (performance spread).

### 7.2 Validation methods

- **Internal consistency checks:** resource conservation (water, personnel, equipment), monotonicity checks (more suppression should not increase burn), boundary/direction sanity checks.
- **Cross-model validation:** compare CA vs. level-set spread outputs on shared scenarios; compare deterministic vs. stochastic suppression.
- **Optimization validation:** compare analytical location solutions against simulation-evaluated performance; check solution stability across seeds.
- **Out-of-sample scenarios:** evaluate chosen deployments on scenario sets not used during optimization.
- **Benchmark comparisons:** compare against naive baselines (e.g., evenly spaced camps, corners, single-central camp) to confirm benefit.

### 7.3 Sensitivity analysis

- Sweep wind speed/direction and variability.
- Vary fuel parameters and fuel homogeneity.
- Vary ignition intensity and clustering.
- Vary suppression rates, water limits, transport delays, helicopter availability.
- Vary grid resolution and candidate-site granularity.
- Vary the objective weighting (expected vs. worst-case).

### 7.4 Robustness / decision validation

- Assess whether the recommended allocation remains near-optimal under a range of assumptions (robustness).
- Test the escalation rule against extreme seasons to confirm it triggers appropriately.

---

## 8. Expected Result Interpretation

> Descriptive only — no results are produced in this draft.

- The **allocation deliverable** is expected to take the form of base camp locations (grid nodes or coordinates) for the four units, accompanied by the objective criterion used and a comparison against baselines. It may also include a response/movement policy if the chosen architecture requires it.
- The **damage forecast deliverable** is expected to take the form of a distributional estimate of burned area under the proposed deployment, plus an interpretable escalation rule (e.g., trigger conditions under which additional units should be requested).
- Results should be presented with **ranges/uncertainty** rather than single numbers, given the stochastic inputs.
- Interpretation should map model outputs back to operational meaning: which regions are best protected, which are the most exposed under westerly wind, and how sensitive the plan is to assumptions.
- Any recommended deployment should be accompanied by the **assumptions under which it holds** and the **conditions under which it should be reconsidered**.

---

## 9. Limitations and Improvements

### 9.1 Anticipated limitations

- Homogeneous fuel and constant wind are strong simplifications that may overstate certainty.
- Grid-only vehicle access ignores possible road damage, congestion, or off-grid terrain.
- Single helicopter may be a bottleneck for simultaneous incidents; treating personnel movement as near-instant may be optimistic under contention.
- Objective choice ("best") is not uniquely defined by the statement; different objectives may yield different deployments.
- Discretization resolution trades fidelity against runtime.
- No real historical data means parameters are assumption-driven and confidence is limited.

### 9.2 Planned improvements / extensions

- Introduce heterogeneous fuel classes and time-varying wind.
- Add multi-fire queueing with explicit helicopter scheduling.
- Explore multi-objective/robust optimization and Pareto trade-offs.
- Develop surrogate models for faster scenario evaluation and richer forecast tools.
- Incorporate cost/benefit framing for the "additional units" escalation decision.
- Validate against any external fire-spread literature or benchmark datasets if made available.

---

## Appendix — Scope Statement

This document is intentionally limited to planning. It contains:

- no computed values or fitted parameters,
- no executed experiments or simulations,
- no plots or images,
- no final recommendations or conclusions.

All quantitative work is deferred to the subsequent modeling (solving) stage, at which point the roadmap above will be executed, validated, and reported.
