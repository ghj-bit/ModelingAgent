# Modeling Plan Draft — MM-Bench 2015_B

**Problem ID:** `2015_B`
**Title:** MM-Bench 2015_B
**Source:** MM-Bench 2015
**Status of this document:** Initial modeling plan draft (blueprint only). No data analysis, no calculations, no model fitting, and no results are included here. All content is prospective and intended to guide later modeling work.

---

## 1. Problem Background and Restatement

### 1.1 Context

The problem is motivated by the disappearance of Malaysian Airlines flight MH370 and the subsequent multinational search effort across vast, deep, open-ocean regions. Searchers face a fundamental difficulty: when an aircraft is lost over open water with **no distress signals and no transmitted position fix**, the search area is enormous relative to the detection range of available sensors. A useful planning model must convert very limited information — the flight plan, last known positions, timing of any ambiguous contacts, and oceanographic drift — into a **prioritized, time-dependent search plan** that maximizes the probability of detection given scarce search resources.

### 1.2 Problem Restatement (native requirements preserved)

Build a **generic mathematical model** that assists "searchers" in planning a useful search for a lost plane feared to have crashed in open water such as the Atlantic, Pacific, Indian, Southern, or Arctic Ocean, while flying from Point A to Point B, under the assumption that **there are no signals from the downed plane**.

The model must recognize that:

- There are **many different types of planes** being searched for (the *target* population) — differing in speed, fuel endurance, size, radar/visual signature, and crash/ditching behavior.
- There are **many different types of search planes**, often using **different electronics or sensors** — differing in speed, range, on-station time, sensor type (visual, radar, IR, sonar, magnetometer), and detection performance.

### 1.3 Addendum requirement

Prepare a **1–2 page non-technical paper** suitable for airline use in press conferences, describing the plan for future searches.

### 1.4 What this deliverable is (and is not)

- It **is** a roadmap: objectives, assumptions, candidate methods, data plan, implementation plan, and validation strategy.
- It **is not** a solution. No search area, no probability values, no drift trajectories, and no resource allocation results are produced here.

---

## 2. Objectives and Subproblems

### 2.1 Primary objective

Produce a decision-support framework that, for a given lost-aircraft scenario and a given set of search assets, will **rank and schedule candidate search regions over time** so as to maximize the expected probability of detection (POD) per unit of search effort, and will **adapt** as new information arrives.

### 2.2 Subproblems

**SP1 — Where could the aircraft be? (Prior / search-space generation).**
Define a probability distribution over the aircraft's position at the moment of "loss" (crash/ditch), conditioned on the intended route, flight performance envelope, last known position/time, and possible deviations (weather, diversion, deliberate route change, systems failure). Output: a spatial prior probability surface over the ocean region.

**SP2 — Where could it have drifted to? (Time-dependent motion).**
Model how a floating or submerged debris field / wreckage location evolves due to ocean currents, wind-driven drift, leeway, and time. Output: a time-evolving probability density that *advects and diffuses* the SP1 prior.

**SP3 — How likely are we to detect it if we search there? (Sensor/detection model).**
Characterize each search platform and sensor as a **Probability of Detection (POD)** function of range, environmental conditions, target signature, and search geometry (e.g., lateral range curves, sweep width). Output: per-sensor detection kernels.

**SP4 — Where should we search next, and with what? (Resource allocation & scheduling).**
Given the time-evolving probability map (SP2) and detection kernels (SP3), allocate finite search effort (sorties, hours, area coverage) across regions and over time to maximize cumulative probability of success. This is an optimization/decision problem with dynamic re-planning.

**SP5 — How do we combine many aircraft types and many sensor types? (Heterogeneity).**
Provide a unified abstraction so that different targets (aircraft types) and different searchers (platform/sensor types) can be plugged in via parameters rather than re-deriving the model. Output: modular parameterization.

**SP6 — Communication deliverable.**
Produce the non-technical 1–2 page press/airline paper conveying the search philosophy, rationale, and commitments in plain language.

### 2.3 Deliverables

1. A generic, parameterized modeling framework (conceptual + planned implementation) covering SP1–SP5.
2. A prioritized, time-dependent search plan generator (specification and algorithm roadmap).
3. A validation and sensitivity strategy for the framework.
4. A 1–2 page non-technical summary for airline press use (structure and content plan).

---

## 3. Assumptions

Assumptions are grouped, with justification and a planned validation approach for each. Values will be treated as parameters to be calibrated or swept later.

### 3.1 Operational / scenario assumptions

| ID | Assumption | Justification | Planned validation |
|----|------------|---------------|--------------------|
| A1 | The aircraft has crashed/ditched in open water and is no longer under control. | Problem statement premise; no signals from the plane. | Consistency with scenario; test alternative "still flying / landed" branches as extensions. |
| A2 | The intended route (Point A → Point B) and basic flight plan (speed, altitude, fuel) are approximately known. | Standard commercial flight planning data exist. | Compare prior sensitivity under route uncertainty. |
| A3 | The time of loss (or a bounded interval) is known to within some uncertainty. | Timing inferred from last contact/handshake events. | Sweep time-of-loss uncertainty. |
| A4 | No reliable position fix is available after loss. | Stated in problem ("no signals"). | Contrast with a "with signal" variant to bound value of information. |

### 3.2 Target (missing aircraft) assumptions

| ID | Assumption | Justification | Planned validation |
|----|------------|---------------|--------------------|
| A5 | Target type is unknown but drawn from a finite set of plausible aircraft classes. | Problem explicitly spans many plane types. | Enumerate classes; test robustness across each. |
| A6 | Each aircraft class has a characterized performance envelope (range, speed, fuel endurance) and a physical signature (size, radar cross-section proxy, buoyancy). | Needed for SP1 priors and SP3 detection. | Literature/manufacturer data; sensitivity to signature uncertainty. |
| A7 | Some wreckage may float and drift; some may sink. | Realistic for ocean crashes. | Model both surface (drifting) and seabed (static) search modes. |

### 3.3 Environment assumptions

| ID | Assumption | Justification | Planned validation |
|----|------------|---------------|--------------------|
| A8 | Ocean currents, winds, and waves can be represented by available oceanographic/atmospheric data products. | Standard for drift modeling. | Compare against multiple current models. |
| A9 | Environmental conditions within a search sortie window are approximately stationary or slowly varying. | Simplifies detection computation. | Compare stationary vs. time-sliced environments. |
| A10 | Ocean region is unbounded/deep enough that boundary effects are secondary for the drift horizon considered. | Typical open-ocean search. | Test boundary sensitivity for coastal/near-shelf cases. |

### 3.4 Search asset assumptions

| ID | Assumption | Justification | Planned validation |
|----|------------|---------------|--------------------|
| A11 | Search platforms have known speed, endurance, fuel, basing, and on-station constraints. | Airline/military asset data. | Parameterize and sweep. |
| A12 | Each sensor can be summarized by a detection kernel (POD vs. range/conditions) and a coverage rate (sweep width × speed). | Standard search-theory abstraction. | Calibrate kernels from detection theory and, where possible, published trials. |
| A13 | Sensors operate independently; combined detection over repeated passes is combined probabilistically. | Enables tractable aggregation. | Test correlated-detection alternative. |

### 3.5 Modeling-convenience assumptions

| ID | Assumption | Justification | Planned validation |
|----|------------|---------------|--------------------|
| A14 | The prior (SP1) and drift (SP2) can be discretized on a grid/particle representation. | Enables numeric computation. | Compare grid vs. particle representations. |
| A15 | Search effort can be treated as a divisible resource allocated over cells and time periods. | Supports optimization formulation. | Compare with integer sortie scheduling. |

---

## 4. Data Processing Plan

### 4.1 Staged data status (as inspected)

The workspace `data/` directory is currently **empty**; the problem's dataset definition provides an empty `dataset_path`, empty `dataset_description`, and empty `variable_description`. Therefore, **no dataset is staged**. All data requirements below are *planned inputs* to be sourced or parameterized in the later modeling phase. No data will be analyzed in this planning task.

### 4.2 Planned input categories (to be sourced later)

1. **Flight/route data:** Point A and Point B coordinates, flight plan, cruise speed/altitude, fuel load and endurance, last known position/time.
2. **Aircraft-class catalog:** A small set of representative missing-aircraft classes with performance envelopes and physical signatures.
3. **Search-asset catalog:** Platform types with speed, endurance, basing, sensor suites, and sensor characteristics.
4. **Sensor models:** Lateral-range curves / sweep widths and POD parameters per sensor and per target class, under varying sea state and visibility.
5. **Environmental fields:** Ocean surface current vectors, wind fields, wave/sea-state, and (optionally) bathymetry for seabed search.
6. **Historical/reference cases:** Any documented search episodes usable for retrospective calibration (e.g., prior MH370-style drift studies) — used only as validation references, not as answers.

### 4.3 Preprocessing plan

- **Coordinate system & grid definition:** Choose a common projection and grid resolution balancing accuracy and computation (e.g., lat/lon with local equal-area projection per region).
- **Time discretization:** Define time steps for drift integration and for search-sortie scheduling; align the two horizons.
- **Unit harmonization:** Normalize distances (nm/km), speeds (kn), areas (nm²), and effort (hours/sorties).
- **Environmental data ingestion:** Interpolate current/wind fields onto the model grid and time steps; handle missing values and land masking.
- **Quality control:** Range checks, temporal alignment, and outlier handling on all sourced layers.

### 4.4 Feature construction (planned)

- **Prior surface (SP1):** Probability mass per grid cell at time of loss, built from route uncertainty and failure-mode branches.
- **Drift kernel:** Per-cell transition operator (advection + diffusion) derived from current/wind fields and leeway coefficients.
- **Detection feature per (sensor, target, environment):** Effective sweep width and POD curve.
- **Effort feature per (platform, period):** Available hours and reachable cells (range/time constraints).
- **Decision variables:** Fraction of effort assigned to each (cell, time, platform, sensor) combination.

### 4.5 Data usage strategy

- **Calibration set:** Environmental-drift and sensor-kernel parameters tuned against reference/analog cases.
- **Hold-out/reference set:** Distinct documented cases reserved for retrospective validation of search-plan quality.
- **Sensitivity layer:** Parameter ranges (not point values) carried through to sensitivity analysis.

---

## 5. Candidate Model Framework

The framework is modular: SP1 → SP2 → SP3 → SP4, with a heterogeneity layer feeding SP1 and SP3.

### 5.1 SP1 — Prior location model (where could it be?)

**Candidate models (to compare):**
- **Route-tube / corridor model:** Probability mass concentrated along the intended track, broadened by navigation uncertainty that grows with time since last fix.
- **Bayesian branch model:** Discrete failure-mode branches (continue on track, turn to alternate, depressurization/ghost flight, etc.), each with a prior weight, each generating its own position distribution; combined by weighted sum.
- **Great-circle / geodesic sampling:** Monte-Carlo sampling of trajectories under speed/heading/fuel constraints, ending where endurance is exhausted.

**Variables:** initial position/time, heading uncertainty, speed distribution, fuel endurance, branch probabilities.

**Mathematical ideas:** conditional probability, mixture distributions, constrained random-walk/Rayleigh flight-path models, fuel-consumption feasibility region.

**Advantages/limitations:** Corridor models are simple and interpretable but ignore deviation branches; Bayesian branch models are flexible but require subjective priors; Monte-Carlo handles complex constraints but needs many samples and careful constraint definition.

### 5.2 SP2 — Drift model (where could it be now?)

**Candidate models (to compare):**
- **Advection–diffusion PDE:** ∂p/∂t + ∇·(u p) = ∇·(K ∇p) on the ocean grid, with u from currents (+ wind-driven leeway).
- **Lagrangian particle/ensemble model:** Release particles from SP1, advect via a stochastic differential equation (deterministic current + wind leeway + random diffusion), estimate density by kernel/particle statistics.
- **Hybrid / ensemble methods:** Multiple current products → ensemble drift cones bounding uncertainty.

**Variables:** current velocity field, wind field, leeway/drift coefficients, diffusion coefficient, time horizon.

**Mathematical ideas:** conservation laws, Fokker–Planck / SDE equivalence, Monte-Carlo density estimation, uncertainty propagation.

**Advantages/limitations:** PDE is fast and smooth but can be dispersive/oversmoothing; particle methods handle inhomogeneous fields and sharp features but are sample-size sensitive; ensembles give uncertainty bounds at higher cost.

### 5.3 SP3 — Detection model (how likely to detect?)

**Candidate models:**
- **Random-search / inverse-cube detection:** POD via lateral-range curve and sweep width; exponential discovery model.
- **Sweep-width (effective) formulation:** reduced from environmental and target factors; coverage rate = sweep width × search speed.
- **Cumulative detection over repeated passes:** POD_cumulative = 1 − ∏(1 − POD_i), with an option to model correlated passes.

**Variables:** sweep width, sensor range, target signature, sea state, visibility, search altitude/speed, pass geometry.

**Mathematical ideas:** detection theory, lateral-range integrals, Poisson/exponential detection.

**Advantages/limitations:** Standard and well-grounded; assumes idealized independent passes and may misstate performance in clutter or against small/low-signature targets.

### 5.4 SP4 — Search optimization & scheduling (what to search next?)

**Candidate models (to compare):**
- **Optimal search theory (Bayesian allocation):** Sequentially allocate effort to cells proportional to (probability mass × detection rate), updating the posterior as unsuccessful searches occur.
- **Dynamic programming / MDP:** State = posterior probability map + remaining resources; action = allocate a search chunk; reward = expected POD. Tractable only in coarse discretizations.
- **Greedy / one-step lookahead with continuous re-planning:** Practical approximation to the MDP; recompute after each sortie (rolling horizon).
- **Mathematical programming (LP/ILP) for a planning window:** Maximize expected detection subject to asset time/range/basing constraints; supports integer sortie scheduling variants.

**Variables:** effort allocation x(cell, time, platform, sensor); asset availability; fuel/time budget; reachability.

**Mathematical ideas:** Bayes update of the posterior, expected-value maximization, coverage/reachability constraints, rolling-horizon planning.

**Advantages/limitations:** Optimal search theory is theoretically sound but assumes accurate priors and homogeneous detection; DP is exact in principle but suffers curse of dimensionality; greedy/rolling-horizon is practical and robust; LP/ILP handles rich constraints but scales poorly.

### 5.5 SP5 — Heterogeneity layer (many targets, many searchers)

**Approach:** Parameterize everything through catalogs:
- **Target catalog** → feeds SP1 priors (performance) and SP3 signatures (detectability, buoyancy).
- **Search-asset catalog** → feeds SP3 kernels (sensor type) and SP4 constraints (speed/range/endurance/basing).
- A **scenario descriptor** selects one target class (or a mixture with weights) and a set of available assets; the pipeline SP1→SP4 runs unmodified.

**Advantages/limitations:** Clean separation of concerns and easy scenario swap; risk of over-simplifying real sensor interactions, which must be acknowledged.

### 5.6 Cross-cutting mathematical ideas

- Probability and Bayesian inference (priors, likelihoods, posterior updating).
- Advection–diffusion / stochastic processes (drift).
- Search theory (sweep width, POD, optimal allocation).
- Optimization (LP/ILP, dynamic programming, greedy heuristics).
- Monte-Carlo simulation and uncertainty propagation (ensembles).

---

## 6. Implementation Roadmap

### 6.1 Architecture (planned modules)

1. **`scenario` module:** Loads a scenario descriptor (Point A/B, timing, target class(es), available assets).
2. **`catalogs` module:** Target-class and search-asset parameter tables.
3. **`prior` module (SP1):** Builds the initial position probability surface (corridor / branch / Monte-Carlo).
4. **`drift` module (SP2):** Advects the prior forward in time (PDE or particle ensemble).
5. **`detection` module (SP3):** Computes sweep widths and POD kernels per sensor/target/environment.
6. **`planner` module (SP4):** Allocates effort and schedules sorties (optimal search / DP / rolling-horizon / LP-ILP).
7. **`simulator` module:** Synthetic forward simulation of detection outcomes to evaluate plans (validation).
8. **`report` module:** Generates the prioritized search plan and the non-technical press paper.
9. **`config` module:** Central parameter store (with documented ranges for sensitivity sweeps).

### 6.2 Planned workflow

1. Define scenario and load catalogs.
2. Compute SP1 prior.
3. Propagate SP2 drift over the planning horizon (with uncertainty ensemble).
4. Build SP3 detection kernels for the available assets.
5. Solve SP4 allocation for the first planning window.
6. Emit an ordered search plan (regions, assets, time windows, expected effort).
7. Re-plan: update the posterior after each (simulated or real) sortie and repeat from step 5 (rolling horizon).
8. Produce the non-technical summary.

### 6.3 Algorithms (candidate choices to be finalized later)

- Prior generation: geodesic Monte-Carlo sampling; mixture construction.
- Drift: explicit/upwind finite-difference for the PDE, or Euler–Maruyama integration for particles.
- Detection: numerical integration of lateral-range curves; sweep-width tables.
- Planning: greedy expected-POD allocation as the baseline; DP/ILP as advanced variants.
- Uncertainty: ensemble runs across current products and parameter ranges.

### 6.4 Non-technical press paper plan (Addendum)

Structure (1–2 pages, plain language; content to be written in the solving phase, no results here):
1. Why a planned search is needed and what "no signals" implies.
2. How we turn the flight plan and ocean conditions into a search area.
3. How different aircraft and sensors are matched to the task.
4. How the plan updates as the search proceeds.
5. Commitments to transparency, coordination, and periodic review.

### 6.5 Engineering considerations (planned)

- Reproducibility: seeded Monte-Carlo, versioned parameters.
- Performance: grid resolution vs. runtime trade-offs; possible parallelization of ensembles.
- Modularity: pluggable target/asset catalogs and swappable drift/planning engines.
- Traceability: log all parameter values and scenario descriptors for each run.

---

## 7. Validation Strategy

### 7.1 Evaluation metrics (planned)

- **Probability of Success (POS):** cumulative probability of detecting the target under the plan.
- **Expected time/effort to detection** (or to a target confidence threshold).
- **Coverage efficiency:** POS per unit of search effort.
- **Robustness:** degradation of POS under perturbed priors/parameters.
- **Calibration:** whether stated probabilities match simulated/realized frequencies.

### 7.2 Validation methods (planned)

- **Synthetic ground-truth simulation:** Generate known target locations from the model's own prior, run the planner, and measure recovery of POS — sanity check for internal consistency.
- **Retrospective/analog cases:** Apply the framework to documented search episodes (using only pre-outcome information) and compare plan quality qualitatively/quantitatively as feasible.
- **Cross-model comparison:** Compare PDE vs. particle drift and greedy vs. DP/ILP planning to bound method-induced differences.
- **Benchmark allocation check:** Compare the planner's allocation against the theoretical optimal-search allocation in simplified homogeneous settings.

### 7.3 Sensitivity analysis (planned)

- Sweep **prior uncertainty** (route deviation probability, time-of-loss window).
- Sweep **drift parameters** (leeway coefficients, diffusion, current-product choice).
- Sweep **detection parameters** (sweep width, sea state, target signature).
- Sweep **resource parameters** (number/type of assets, basing distance, endurance).
- Report which inputs most affect POS, to prioritize data collection.

### 7.4 Limits of validation

- Real-world ground truth is scarce; validation leans on simulation and analog cases.
- Sensor and environment models are approximations; residual uncertainty must be communicated, not hidden.

---

## 8. Expected Result Interpretation

*(Interpretation guidance only — no results produced here.)*

- **Search-probability maps:** Should be read as *relative priorities over space and time*, not as guarantees of location.
- **Effort allocation:** Higher allocation to a region means higher expected "value" of searching there (probability mass × detectability), and should be expected to shift as the drift horizon and posterior update.
- **POD/POS numbers:** Represent model-based expectations under stated assumptions; their reliability is bounded by prior and sensor-model quality.
- **Heterogeneity effects:** Different target classes should visibly change both the search region (prior/signature) and the recommended asset mix (detection/constraints).
- **Update behavior:** After unsuccessful searches, the posterior should down-weight searched areas and redirect effort — this adaptive behavior is a key qualitative outcome to expect.
- **Communication takeaway:** The non-technical paper should convey a defensible, adaptive, transparent process rather than a single predicted location.

---

## 9. Limitations and Improvements

### 9.1 Anticipated limitations

- **Prior subjectivity:** Failure-mode branch probabilities are speculative and drive SP1 strongly.
- **Drift uncertainty:** Current/wind products disagree; long-horizon drift compounds uncertainty.
- **Sensor abstraction:** Lateral-range curves idealize real detection; small/low-signature targets and clutter are hard to model.
- **Optimization tractability:** Full DP/MDP is intractable at fine resolution; practical planners are approximate.
- **Independence assumptions:** Serially correlated detections across passes are ignored in the basic model.
- **Data availability:** No dataset is staged; some inputs must be sourced or parameterized, adding uncertainty.
- **Scenario scope:** Deep seabed search and multi-domain (air + surface + subsurface) coordination are only partially captured.

### 9.2 Planned improvements / extensions

- Add **value-of-information** analysis to show which new data (e.g., a single satellite ping) most reduces search area.
- Implement **adaptive/partially observable planning** (POMDP-style) for richer re-planning.
- Introduce **correlated detection** and **sensor-fusion** models.
- Incorporate **bathymetry and underwater search** (towfish/AUV) as a parallel planning track.
- Support **multi-target uncertainty** with explicit mixture weights and posterior model selection.
- Provide an **interactive planning dashboard** (region ranking, asset assignment, timeline).
- Strengthen **retrospective validation** with more analog cases as they become available.

---

## Appendix A — Planning Checklist

- [ ] Scenario descriptor format defined.
- [ ] Target-class and search-asset catalogs drafted.
- [ ] SP1 prior method(s) selected after comparison.
- [ ] SP2 drift engine (PDE and/or particle) selected.
- [ ] SP3 detection kernels specified per sensor/target/environment.
- [ ] SP4 planning engine (baseline + advanced) specified.
- [ ] Validation harness (synthetic + analog) designed.
- [ ] Sensitivity analysis plan finalized.
- [ ] Non-technical press paper outline agreed.

## Appendix B — Explicit Scope Note

This document is a **planning blueprint**. It contains no data analysis, no computations, no fitted models, no executed experiments, and no final conclusions. All quantitative content is to be produced in the subsequent solving phase under the roadmap described above.
