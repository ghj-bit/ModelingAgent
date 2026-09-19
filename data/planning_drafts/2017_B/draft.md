# Modeling Blueprint Draft — MM-Bench 2017_B
## Fan-In Geometry and Merging Pattern for a Barrier Toll Plaza

> **Status: planning draft.** This document is a roadmap for future modeling only. It contains no computed results, no data analysis, no fitted models, and no final conclusions. All quantitative placeholders (notation, parameter symbols, ranges) are to be resolved in the later modeling stage.

---

## 1. Problem Background and Restatement

A multi-lane divided limited-access toll highway has **L travel lanes per direction** and a **barrier toll with B tollbooths per direction**, where **B > L**. A barrier toll is a row of tollbooths spanning the roadway, perpendicular to traffic flow. Because the number of tollbooth egress lanes (B) exceeds the number of downstream travel lanes (L), vehicles must **fan in** from B lanes down to L lanes.

The physical facility consists of three regions:
1. **Fan-out area** — upstream, where L lanes spread out to feed B tollbooths.
2. **Toll barrier** — the row of B booth service channels.
3. **Fan-in area** — downstream, where B booth egress lanes merge back down to L travel lanes.

This task concerns **only the fan-in area after the barrier**: its **shape, size, and merging pattern**. The goal is not to evaluate an existing plaza design, but to determine whether **better solutions exist** than those in common use.

The problem explicitly requires the model to balance three competing considerations:
- **Accident prevention / safety** (conflicts, merges, lane-change risk),
- **Throughput** (vehicles per hour passing the point where the plaza ends and joins the L outgoing lanes),
- **Cost** (land acquisition and road construction are expensive, so the fan-in footprint should be economical).

The model must also:
- Report **performance in light and heavy traffic**,
- Show how the design changes as the share of **autonomous (self-driving) vehicles** grows,
- Show how the design is affected by the **mix of booth types** — conventional (human-staffed), exact-change (automated), and electronic toll collection (ETC / transponder).

**Restatement of the deliverable:** a design-oriented mathematical model that, given (L, B, traffic demand, vehicle mix, booth mix, cost parameters), proposes a fan-in **shape**, **size**, and **merging pattern**, together with a principled way to compare candidate designs on safety, throughput, and cost.

**Note on data:** The provided dataset definition is empty (`dataset_path: []`, empty `dataset_description` and `variable_description`). The workspace `data/` directory contains no staged files. Consequently, the plan below treats the problem as **model-and-parameter driven** (literature-derived and/or synthesized parameters), with any future empirical data treated as optional calibration/validation input.

---

## 2. Objectives and Subproblems

### 2.1 Primary objective
Produce a **design methodology** (not a single answer) that determines the optimal fan-in shape, size, and merging pattern for a barrier toll plaza with parameters (L, B), optimizing a balanced trade-off among **safety, throughput, and cost**, and characterizing how the optimal design responds to traffic level, autonomous-vehicle penetration, and booth-type mix.

### 2.2 Subproblems (to be decomposed for later modeling)

- **SP1 — Geometric representation.** Define a parameterized family of fan-in geometries (taper length, lateral offset, number and placement of merge points, curvature, auxiliary-lane provision) so that "shape" and "size" become design variables rather than fixed assumptions.
- **SP2 — Merging-pattern taxonomy.** Formalize candidate merging patterns: sequential/one-at-a-time, pairwise, multi-lane "zipper" merge, batched merges with dedicated lanes, and grade/priority variants. Define each as a discrete design choice combinable with SP1 geometry.
- **SP3 — Traffic flow & throughput model.** Represent vehicle arrivals from B booths and their merge behavior to estimate capacity and throughput at the plaza exit under light and heavy demand.
- **SP4 — Safety/conflict model.** Quantify conflict exposure (merge conflicts, weaving, forced lane changes, speed differentials) as a surrogate for accident risk, since direct crash data are assumed unavailable.
- **SP5 — Cost model.** Estimate land consumption (footprint area) and construction cost as functions of geometry and number of merge structures.
- **SP6 — Multi-objective optimization.** Formulate and solve the trade-off among SP3–SP5 to identify Pareto-optimal designs and select/rank candidates under explicit preference assumptions.
- **SP7 — Demand & mix scenarios.** Characterize performance across light/heavy traffic and across autonomous-vehicle penetration and booth-type mix; identify how the recommended design shifts with each.
- **SP8 — Autonomous-vehicle adaptation.** Extend the behavioral submodels (car-following, gap acceptance, lane choice) to represent autonomous vehicles' tighter gaps, higher precision, and possible cooperative merging, and study its effect on design.

### 2.3 Planned deliverables
- A parameterized design space and notation set.
- A multi-objective evaluation framework coupling throughput, safety surrogates, and cost.
- A scenario-analysis protocol (traffic level × AV penetration × booth mix).
- A validation and sensitivity-analysis plan.
- A documented pipeline sketch (models + algorithm choices) for the later implementation stage.

---

## 3. Assumptions

Each assumption below is listed with its **justification** and a **future validation approach**. Assumptions are grouped by category and are to be re-examined during the modeling stage.

### 3.1 Scope and topology
- **A1.** The analysis considers one direction of travel with L downstream lanes; the two directions are symmetric and independent. *Justification:* the plaza is split by a median; cross-direction interaction is negligible. *Validation:* relax by modeling a shared barrier service region in a later extension.
- **A2.** Fan-out (upstream) is out of scope except as it sets boundary inflow; focus is the fan-in area downstream of the barrier. *Justification:* problem statement explicitly targets the post-barrier merging area. *Validation:* couple inflow from a simple queueing model of the booths.
- **A3.** The downstream highway retains L lanes and its posted speed limit; the design must terminate in a clean L-lane cross-section. *Validation:* check exit cross-section width and lane continuity in geometric checks.

### 3.2 Traffic behavior
- **A4.** Traffic is modeled with macroscopic/cellular flow relations plus stochastic elements; heterogeneous driving behavior is summarized by distributions (desired speed, critical gap, driver aggressiveness). *Justification:* full microscopic calibration data are unavailable. *Validation:* compare emergent flow–density behavior against literature fundamental-diagram ranges.
- **A5.** Merging follows gap-acceptance logic with a critical gap parameter; capacity of a merge is limited by the gap-acceptance process, not only by lane capacity. *Validation:* compare merge capacity estimates to published merge/weaving capacity ranges.
- **A6.** Arrivals from the B booths are treated as a stochastic process (e.g., Poisson-like with booth-specific rates), reflecting service-rate differences by booth type. *Validation:* re-test with bursty/platoon arrivals to represent release patterns.
- **A7.** Autonomous vehicles (AVs) will be modeled as having (i) shorter accepted gaps, (ii) more precise speed/lateral control, and (iii) a cooperative merging mode. AV penetration is a controllable scenario parameter. *Justification:* reflects the trend motivating the question. *Validation:* bracket AV behavior with conservative and optimistic parameter sets.

### 3.3 Cost and safety abstraction
- **A8.** Land and construction cost scales with footprint area and number/shape of merge structures, using unit-cost parameters. *Justification:* exact parcel pricing is location-specific and unknown. *Validation:* parametric sweep over unit costs.
- **A9.** Direct crash data are unavailable; accident risk is represented by **surrogate safety measures** (conflict counts, time-to-collision exposure, required lane changes, speed variance). *Validation:* benchmark surrogate rankings against known design heuristics (e.g., fewer merge points generally safer).
- **A10.** Steady-state/period analysis is used, with demand treated as a controllable rate; transient congestion is handled by capacity-exceedance checks rather than full queue dynamics initially. *Validation:* add time-dependent demand later.

### 3.4 Modeling conventions
- **A11.** Vehicles are point- or length-based discrete entities in the microsimulation layer and continuous densities in the macroscopic layer; the two layers are linked by shared flow/geometry parameters.
- **A12.** Geometry is idealized (straight/tapered alignments, continuous curvature), excluding micro-details (signage, pavement markings) except as design variables where relevant.

---

## 4. Data Processing Plan

Because the problem ships with **no dataset**, the "data plan" is a plan for **parameter sourcing, synthesis, and calibration**, not for cleaning a given file.

### 4.1 Data sourcing strategy
- **Literature/standards extraction.** Compile parameter ranges for: booth service times by type (conventional / exact-change / ETC), lane capacity, merge critical gaps, design speeds, safe taper rates, and unit land/construction costs. Sources to be cited in the modeling stage.
- **Synthetic data generation.** Where literature is silent, generate scenario grids (L, B, demand, AV share, booth mix) as the input space for the models.
- **Optional empirical hooks.** If any plaza observations, counts, or videos later become available, define a slot to ingest them as calibration/validation data without changing the model structure.

### 4.2 Preprocessing (to be applied to whatever inputs are used)
- **Unit harmonization** (vehicles/hour vs vehicles/second/km, meters vs feet).
- **Consistency checks** on dimensions (B > L, non-negative flows, sum of booth-type shares = 1).
- **Outlier/robustness screening** for any empirical inputs (e.g., distorted service times).
- **Re-scaling/normalization** of heterogeneous inputs before optimization (costs, flows, risk surrogates have different units).

### 4.3 Feature / parameter construction
- **Design variables (geometry):** fan-in length, number of merge stages, lateral positions of merge points, curvature/taper geometry, presence of auxiliary/collector lanes.
- **Design variables (pattern):** merge sequencing/topology, priority rules, dedicated AV lanes.
- **Scenario variables:** total demand (light/heavy), directional imbalance, AV penetration p_AV, booth-type mix (share conventional/exact-change/ETC), truck/heavy-vehicle share.
- **Derived quantities:** exit throughput, conflict-surrogate indices, total footprint, cost.

### 4.4 Data usage strategy
- Use literature ranges for **primary parameterization**.
- Use scenario grids for **exploration** (space-filling/random designs over the design-space).
- Reserve any external data strictly for **calibration and validation**, keeping model structure fixed to avoid overfitting to unavailable inputs.

---

## 5. Candidate Model Framework

The blueprint couples **geometry**, **traffic dynamics**, **safety surrogates**, and **cost** inside a **multi-objective optimization** shell. Candidate models at each layer are listed with advantages and limitations.

### 5.1 Geometry / design-space model
- **Parameterized fan-in family.** Define a mapping from a vector of geometric parameters to the fan-in footprint and merge topology. Options:
  - **Linear taper** (simple, low cost, single/continuous merge zone).
  - **Staged merges** (series of localized merges with tangent sections).
  - **Curvilinear/streamline taper** (smooth spline alignment; better comfort, larger footprint).
  - **Auxiliary/collector lane designs** (extra lane to buffer merges; more capacity, more cost).
- *Advantages:* makes "shape/size/pattern" explicit decision variables. *Limitations:* geometric richness increases design-space dimension and computational cost.

### 5.2 Traffic flow / throughput models
- **Macroscopic (fundamental-diagram) model:** link flow–density–speed relations and merge capacity. *Advantages:* fast, analytic, good for throughput/capacity. *Limitations:* coarse for merge conflicts.
- **Queueing / bottleneck model:** treat the plaza exit as a bottleneck with merging-limited service; booth service as M/M/c or M/G/c with booth-type-dependent rates. *Advantages:* captures booth-mix effects and demand sensitivity. *Limitations:* abstracts merging detail.
- **Microsimulation / cellular automata:** car-following + lane-changing (e.g., MOBIL-style) + gap-acceptance merging. *Advantages:* produces conflict counts, throughput, and can encode AV behavior. *Limitations:* parameter-sensitive and computationally heavier; needs careful calibration.
- **Hybrid plan:** macroscopic for capacity screening, microsimulation for finalist designs.

### 5.3 Safety / conflict model
- **Surrogate safety measures:** number and severity of merge conflicts, required lane changes per vehicle, speed differential at merge points, occupancy of merge zones (conflict-area exposure).
- **Emergent measures from microsimulation:** conflict events, hard-braking events, time-to-collision exposure.
- *Advantages:* works without crash data. *Limitations:* surrogates need mapping assumptions to real risk; treat as relative, not absolute.

### 5.4 Cost model
- **Footprint-based cost:** area × unit land cost + structure cost scaling with merge count and curvature/widening.
- *Advantages:* transparent and parametric. *Limitations:* ignores location-specific pricing; mitigated by sensitivity sweeps.

### 5.5 Objective aggregation and optimization
- **Multi-objective formulation:** vector objective {maximize throughput, minimize risk surrogate, minimize cost}, constraints on safety geometry, design speed, and continuity.
- **Solution approaches:**
  - **Pareto/multi-objective evolutionary algorithms** to generate trade-off frontiers.
  - **Weighted-sum / scalarization** for preference-dependent single recommendations.
  - **Constraint-based feasibility screening** (e.g., minimum radii, maximum taper) before optimization.
- **Decision layer:** rank Pareto designs under explicit stakeholder preferences (e.g., safety-first vs cost-first) to select a recommended family.

### 5.6 AV and booth-mix submodels
- **AV behavior module:** parameterize gap acceptance, reaction time, headway, and cooperative-merge willingness by penetration p_AV; interpolate between human and AV behavior distributions.
- **Booth-mix module:** service-rate distribution determined by shares of conventional/exact-change/ETC booths, feeding the arrival process into the fan-in.

---

## 6. Implementation Roadmap

*(No code is written at this stage; this is a module and workflow plan.)*

### 6.1 Planned modules
1. **`design_space`** — parameterization and encoding of fan-in geometries and merge patterns; validity/constraint checks.
2. **`geometry`** — converts design vectors into footprint area, lane assignments, and merge-point coordinates.
3. **`demand`** — generates arrivals and booth service by type; applies scenario parameters (demand level, booth mix, AV share).
4. **`traffic`** — macroscopic capacity screening and/or microsimulation engine with car-following, lane-changing, gap-acceptance merging, and AV behavior.
5. **`safety`** — computes conflict surrogates from simulation traces.
6. **`cost`** — footprint/structure cost estimation.
7. **`evaluate`** — assembles the objective vector per design per scenario.
8. **`optimize`** — multi-objective search (evolutionary / scalarized) over the design space.
9. **`scenarios`** — orchestrates light/heavy traffic × AV penetration grid × booth mix.
10. **`reporting`** — comparative tables/figures for the final modeling stage (planner only defines the interface here).

### 6.2 Workflow (prospective)
1. Fix the geometric/pattern parameterization and constraints.
2. Choose parameter values/ranges from literature for SP3–SP5.
3. Implement the coupled evaluator (geometry → demand → traffic → safety/throughput → cost).
4. Verify against literature benchmarks and analytic limits.
5. Run scenario sweeps for light/heavy traffic.
6. Run the multi-objective optimizer to obtain Pareto sets.
7. Repeat across AV penetration and booth-mix scenarios; track how the recommended design changes.
8. Perform sensitivity analyses and document recommended design families.

### 6.3 Computational considerations
- Start with fast analytic/queuing screening; promote finalists to microsimulation to control cost.
- Use parallel scenario evaluation; fix random seeds and document replication protocol for stochastic runs.
- Maintain a single configuration source for parameters to keep runs reproducible.

---

## 7. Validation Strategy

### 7.1 Evaluation metrics
- **Throughput:** vehicles/hour at the fan-in exit (the L-lane junction point), and capacity before breakdown.
- **Safety surrogates:** merge conflicts per vehicle (or per hour), required lane changes, speed-differential exposure, conflict-zone occupancy.
- **Cost:** footprint area and estimated cost index.
- **Robustness:** dispersion of metrics across scenarios/seeds.

### 7.2 Validation methods
- **Analytic/limit checks:** single-merge and no-merge limits should recover well-known capacities; degenerate cases (B = L) should behave as a plain multi-lane section.
- **Internal consistency:** conservation of flow (arrivals = departures) in simulation; monotonicity checks (e.g., throughput non-decreasing in lanes under fixed demand).
- **Cross-model comparison:** macroscopic vs microsimulation throughput agreement within an acceptable band for the same scenario.
- **Benchmark against practice:** compare candidate designs' relative ranking to documented design heuristics (taper length, merging precedence).
- **Parameter calibration protocol:** where literature ranges exist, calibrate within them and report post-calibration consistency.

### 7.3 Sensitivity analysis (planned)
- **One-at-a-time and global (e.g., variance-based) sensitivity** on: critical gap, service rates by booth type, demand level, unit costs, AV behavior parameters, and geometric constraints.
- **Scenario sensitivity:** light vs heavy traffic, low vs high AV penetration, and booth-mix corners (all conventional, all ETC, balanced).
- **Robustness of rankings:** test whether the preferred design family is stable under parameter perturbation; flag fragile conclusions.

### 7.4 Uncertainty handling
- Report metric ranges rather than single values where stochasticity dominates.
- Clearly separate model-structural uncertainty (choice of model form) from parameter uncertainty.

---

## 8. Expected Result Interpretation

*(Interpretation guidance only — no results are produced here.)*

- **Design-family, not a single number:** the output is expected to be a *family* of recommended fan-in shapes/sizes/merging patterns, plus the reasoning mapping parameters to recommendations — not one universal plaza design.
- **Trade-off frontier reading:** any recommended design will sit on a safety–throughput–cost trade-off frontier; interpretation must state which objective was prioritized and how much was conceded on the others.
- **Regime dependence:** as traffic moves from light to heavy, the relative value of extra capacity (auxiliary lanes, longer merges) is expected to rise, while cost pressure favors compact designs; the recommendation may shift with regime.
- **AV effects:** increasing AV penetration is expected to be interpretable as a relaxation of effective gap/headway constraints, potentially enabling more compact and more uniform merging — to be confirmed by the model, not asserted here.
- **Booth-mix effects:** a mix weighted toward ETC/exact-change is expected to change the arrival pattern (more uniform, faster releases) feeding the fan-in, which may alter optimal merge staging; interpretation should link booth-mix → arrival process → design.
- **Reportable outputs (final stage):** recommended design parameters, comparative tables across scenarios, trade-off charts, and a sensitivity summary — all to be produced later, not in this draft.

---

## 9. Limitations and Improvements

### 9.1 Anticipated limitations
- **No dataset:** all parameterization relies on literature/synthesis; absolute values may not transfer to specific sites.
- **Surrogate safety measures:** conflict counts approximate, but do not equal, crash rates.
- **Behavioral abstraction:** aggregated driver/AV behavior may smooth out rare but important events.
- **Geometry idealization:** real-world constraints (terrain, right-of-way, signage, enforcement) are simplified.
- **Steady-state bias:** transient and time-varying demand effects are initially limited.
- **Cost simplification:** unit-cost parameters are location-insensitive.

### 9.2 Planned improvements / extensions
- Ingest any empirically available plaza data for calibration and re-validation.
- Replace steady-state analysis with time-dependent demand and queue dynamics.
- Enrich the AV submodel with cooperative/coordinated merging and dedicated AV lanes.
- Include heterogeneous traffic (trucks, buses) with vehicle-class-specific behavior.
- Couple fan-out and barrier (booth) regions for an end-to-end plaza model.
- Add scenario-robust optimization (designs resilient across demand/mix uncertainty).
- Incorporate explicit real-world geometry constraints (right-of-way boundaries, sight distance, sight-line safety checks).
- Move from surrogate to probabilistic risk estimates where local crash data can be obtained.

---

### Appendix A — Notation to be finalized in the modeling stage

| Symbol | Intended meaning |
|---|---|
| L | Number of downstream travel lanes (per direction) |
| B | Number of tollbooths (per direction), B > L |
| N_m | Number of merge stages / merge points (design variable) |
| ℓ_f | Fan-in length (design variable) |
| w_f | Fan-in lateral width / footprint width (derived) |
| A_f | Fan-in footprint area (derived) |
| λ | Total arrival rate (veh/h) |
| μ_k | Service rate of booth type k (conventional/exact-change/ETC) |
| s_k | Share of booth type k (Σ s_k = 1) |
| p_AV | Autonomous-vehicle penetration |
| t_c | Critical gap for merging |
| Θ | Throughput objective |
| R | Safety/risk surrogate objective |
| C | Cost objective |

> All symbols and ranges are provisional and will be defined precisely when modeling begins.

---

*End of planning draft. No problem-solving, computation, or analysis has been performed in this document.*
