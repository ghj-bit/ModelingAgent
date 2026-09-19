# DroneGo Disaster Response System — Initial Modeling Plan (Draft)

**Problem ID:** 2019_B (MM-Bench 2019)
**Document type:** Modeling blueprint / planning draft — *not* a solution
**Status:** Pre-modeling. No data has been analyzed, no models have been fitted, and no computations have been performed.

> Scope note: This document plans *how* the DroneGo design problem will be modeled. It intentionally contains no numerical answers, no selected fleet, no candidate sites, and no route schedules. All statements are forward-looking and describe steps that *will* be taken in a later modeling phase. No files were found in the staged `data/` directory for this problem; the plan below therefore includes an explicit data-acquisition/encoding stage.

---

## 1. Problem Background and Restatement

### 1.1 Background (as given)
Hurricane Maria (2017) devastated Puerto Rico, causing widespread loss of power to roughly the entire population, destruction of most utility poles and transmission lines, loss of most cellular communications, and extensive damage to roads and highways, especially along the east and southeast coast. The disaster left dozens of communities isolated and created sustained surge demand for medical supplies and care that overwhelmed clinics, hospitals, and NGO relief operations.

### 1.2 The DroneGo concept
HELP, Inc. plans a transportable disaster-response system, "DroneGo," built around rotor-wing drones that will perform two missions, either simultaneously or separately depending on conditions:

1. **Medical supply delivery** — carrying pre-packaged medical kits (MED1, MED2, MED3) in drone cargo bays and landing to offload; multiple packages may fit in one bay depending on the drone.
2. **Aerial video reconnaissance** — capturing high-resolution imagery of damaged/serviceable road networks to support ground-route planning.

The complete system (all fleet drones, their shipping containers, and all required medical packages) must fit within **at most three ISO dry cargo containers**. Containers may be delivered to a single location or split across up to three locations. Packing should minimize unused space (buffer material).

### 1.3 Restatement of the concrete deliverables to be produced later
- **Part 1.A** — Recommend a drone fleet (from the candidate set) and a medical-package composition, and design a packing configuration for each of up to three ISO containers.
- **Part 1.B** — Determine the best location(s) on Puerto Rico for one, two, or three containers so the fleet can perform both supply delivery and road-network reconnaissance.
- **Part 1.C.i** — For each fleet drone type: payload packing configurations, delivery routes, and a schedule that meets the identified emergency medical package requirements.
- **Part 1.C.ii** — A flight plan that lets the fleet film/assess the major highways and roads.
- **Part 2** — A 1–2 page executive memo to the CEO summarizing recommendations, tradeoffs, and limitations.

### 1.4 What is *not* yet available
The problem references **Attachment 1** (Puerto Rico map), **Attachments 2–3** (candidate drone specifications), and **Attachments 4–5** (medical package contents/dimensions), plus **Table 1** (ISO container dimensions). The staged dataset definition is empty (`dataset_path: []`), and the run's `data/` folder contains no files. Consequently, a first modeling task will be to **transcribe and encode these attachments into structured tables** (or to source their standard published values) before any model is built. This dependency is tracked in Section 4.

---

## 2. Objectives and Subproblems

### 2.1 Overarching objective
Design a **feasible, container-constrained, multi-mission DroneGo fleet system** that (a) satisfies anticipated medical-supply demand under a future Maria-like scenario, (b) provides adequate road-network video coverage, and (c) makes explicit the **tradeoffs** when demand exceeds fleet capability.

### 2.2 Decomposition into subproblems

| ID | Subproblem | Nature | Primary decision variables (to be defined later) |
|----|------------|--------|--------------------------------------------------|
| SP-0 | Demand & geography characterization | Estimation / data | Demand points, package demand vector, distances, road graph |
| SP-1 | Drone & package portfolio selection (1.A) | Multi-objective discrete selection | Number of each drone type; package mix (MED1/2/3) |
| SP-2 | ISO container packing (1.A) | 3-D packing / knapsack | Placement of drones, spares, batteries, packages in ≤3 containers |
| SP-3 | Container/base siting (1.B) | Facility location | Site coordinates; container-to-site assignment (1, 2, or 3 sites) |
| SP-4 | Delivery routing & scheduling (1.C.i) | Vehicle routing + scheduling | Payload assignment, delivery tours, sorties, timing |
| SP-5 | Road reconnaissance flight plan (1.C.ii) | Coverage / arc routing | Camera sorties covering major road segments |
| SP-6 | Tradeoff & shortfall analysis | Sensitivity / multi-objective | Where capability binds; mitigation options |
| SP-7 | Memo synthesis (Part 2) | Communication | — (narrative, no new computation) |

### 2.3 Deliverables to be produced in the later phase
- A recommended fleet table (types × quantities) with justification.
- Medical-package composition and per-container packing diagrams/specs.
- Selected site(s) with rationale.
- Per-drone-type payload configurations, routes, and a time schedule.
- A reconnaissance flight plan mapped to the road network.
- A tradeoff/shortfall discussion and a ≤2-page memo.

---

## 3. Assumptions

Assumptions are grouped; each lists a **justification** and the **validation approach** to be used later.

### 3.1 Scenario & demand assumptions
- **A1.** A *Maria-like future scenario* will be modeled as a re-occurrence of the 2017 impact profile (same island, similar damage pattern). *Justification:* the problem explicitly anchors design to the 2017 event. *Validation:* compare modeled demand against any recoverable 2017 field estimates; stress-test with a more/less severe scenario.
- **A2.** Medical demand will be represented as a **spatially distributed requirement** (units of MED1/2/3 per demand point over a planning horizon). *Justification:* the problem asks for "anticipated medical supply demands." *Validation:* test alternative allocation keys (population, vulnerability index, shelter occupancy).
- **A3.** Demand may exceed fleet capacity; the model must therefore be **capacity-aware and report shortfalls** rather than assume full satisfaction. *Justification:* explicitly required by the problem. *Validation:* verify that shortfall metrics are monotone in demand scaling.

### 3.2 Operational/technical assumptions (to be calibrated from Attachments 2–5)
- **A4.** Drone performance is governed by published specs (payload capacity, unloaded weight, battery/range, cruise speed, cargo-bay volume, recharge/swap time, wind/altitude effects). Values will be transcribed from Attachments 2–3.
- **A5.** Package geometry/weight follows Attachments 4–5; a package count fit in a bay is determined by **both volumetric and mass** limits.
- **A6.** Delivery requires a **landing**; each delivery consumes time for descent, offload, and ascent.
- **A7.** Reconnaissance is assumed to be possible **simultaneously or separately**; camera coverage quality will be abstracted (e.g., road-segment coverage) rather than physically simulated unless data permit.
- **A8.** Line-of-sight/comms and airspace restrictions will initially be ignored, then revisited in sensitivity analysis. *Justification:* standard modeling first-cut. *Validation:* re-run with a connectivity constraint if data allow.
- **A9.** Drones operate from the container/base site(s); energy replenishment occurs at base (or via battery swaps carried in containers).

### 3.3 Container/packing assumptions
- **A10.** ISO container internal dimensions correspond to **Table 1** (standard 20-ft/40-ft dry container envelope) — to be confirmed.
- **A11.** "Minimize buffer material for unused space" will be operationalized as maximizing **volumetric fill efficiency** subject to a small required clearance tolerance. *Justification:* makes the informal requirement quantitative. *Validation:* test sensitivity to assumptions on compartmentalization and clearance.
- **A12.** Total container count ≤ 3; each container is a self-contained deployable unit (drones + batteries + its share of packages).

### 3.4 Modeling-scope assumptions
- **A13.** Time horizon, sortie concurrency limits (operators, charging ports), and site-to-demand travel use straight-line or road-network distances — the choice will be a modeling-design decision tested via sensitivity.
- **A14.** Costs/weights of support equipment (spares, chargers, packing materials) will be estimated and included as fixed overhead per container.

---

## 4. Data Processing Plan

> **Critical dependency:** the staged `data/` directory is currently empty and the dataset definition is empty. The following plan therefore begins with acquisition/encoding and is robust to that gap.

### 4.1 Data inventory to be assembled
1. **Drone specification tables** (from Attachments 2–3): per candidate drone — payload mass capacity, cargo-bay volume, drone mass, range/endurance, cruise speed, dimensions, power/battery characteristics, cost, quantity availability.
2. **Medical package specs** (Attachments 4–5): per MED type — mass, dimensions, contents, and item counts.
3. **Container specs** (Table 1): internal length/width/height, door opening, max payload.
4. **Puerto Rico geography** (Attachment 1 + external): island boundary, coastline, major highways/roads, settlements/population centers, and (if available) 2017 damage indicators.
5. **Demand basis**: population/demand-point layer and any 2017 health/relief figures usable as a planning key.

### 4.2 Preprocessing steps (planned)
- **Transcription & digitization:** convert attachments into machine-readable tables (CSV/JSON) with units normalized (kg, m, L, km, min, W·h).
- **Geometry handling:** georeference Attachment 1 or substitute an authoritative coastline/road vector layer; build a **road graph** (nodes = intersections/settlements, edges = road segments with length and damage/serviceability attributes).
- **Demand-point construction:** define demand nodes (municipalities/shelters/hospitals), aggregate the population key, and derive per-node package demand.
- **Distance/energy precomputation:** build distance matrices (great-circle and, later, road-network shortest paths) between sites, demand nodes, and road segments; precompute per-drone energy cost per unit distance for each payload state.
- **Feasibility filtering:** mark drone–package and drone–bay combinations that are infeasible by mass or volume; flag data gaps.
- **Robustness:** record provenance and uncertainty (spec ranges vs. point values) to feed the sensitivity plan.

### 4.3 Feature/variable construction (planned)
- Per-drone: capacity utilization envelope, cost-per-kg-km, coverage-per-sortie, effective sorties per horizon.
- Per-demand-node: demand vector, remoteness/accessibility score, priority weight.
- Per-road-segment: length, criticality (connectivity/trunk importance), reconnaissance priority.
- Derived scenario features: damage intensity by region (if reconstructable) to bias both demand and reconnaissance priority.

### 4.4 Data-usage strategy
- **Primary inputs** (drone/package/container specs) feed SP-1/SP-2 directly.
- **Spatial data** feeds SP-3/SP-4/SP-5.
- **Uncertain/estimated inputs** (demand keys, distances, energy margins) are declared as parameters and exercised in sensitivity analysis rather than fixed silently.
- **Data-leakage/consistency guard:** ensure the same distance/energy conventions are used consistently across siting, routing, and recon so results remain comparable.

---

## 5. Candidate Model Framework

The problem is inherently **multi-layer**. The plan is a **modular, loosely coupled pipeline** with explicit interfaces, so each layer can be validated and swapped independently.

### 5.1 Layer 0 — Scenario & demand model
- **Candidate methods:** (i) population-proportional allocation; (ii) vulnerability/shelter-weighted allocation; (iii) hybrid key blending population and damage intensity.
- **Variables:** demand magnitude per node and per MED type over the horizon.
- **Advantage:** simple, transparent, tunable. **Limitation:** sensitive to the allocation key; will be stress-tested.

### 5.2 Layer 1 — Fleet & package portfolio selection (SP-1)
- **Candidate methods:** multi-objective integer programming; weighted-sum or ε-constraint scalarization; knapsack-style selection under a container-volume budget; Pareto-front exploration across (cost, delivery throughput, recon coverage, robustness).
- **Objective(s) (to be finalized):** maximize delivered demand / coverage, minimize cost and container count, subject to all-in-≤3-container feasibility.
- **Advantage:** principled tradeoffs. **Limitation:** combinatorial; may need heuristics or decomposition.
- **Key interplay:** selection cannot be finalized before packing feasibility (Layer 2) is known → will use an **iterate-until-feasible loop** or joint formulation.

### 5.3 Layer 2 — ISO container packing (SP-2)
- **Candidate methods:** 3-D bin packing / container-loading heuristics (layer/guillotine/beam search), MIP where tractable, plus a fill-efficiency objective.
- **Constraint types:** geometric non-overlap, container envelope, mass limits, compartmentalization and clearance rules.
- **Output interface:** per-container manifest and **feasibility certificate** consumed by Layer 1 and Layer 3.
- **Advantage:** directly honors the ≤3-container rule. **Limitation:** 3-D packing is NP-hard → heuristic + feasibility check rather than exact optimality.

### 5.4 Layer 3 — Siting of container(s) (SP-3)
- **Candidate methods:** p-median / k-median, maximal covering location, capacitated facility location, with candidate sites drawn from the road/settlement graph; separate scoring for the supply mission vs. the reconnaissance mission and a combined objective.
- **Cases:** one site (all 3 containers together), two sites, three sites (one container each) — to be compared, since the problem explicitly asks for 1/2/3-location alternatives.
- **Advantage:** classical, interpretable. **Limitation:** dynamic post-disaster accessibility may invalidate static distances → sensitivity needed.

### 5.5 Layer 4 — Delivery routing & scheduling (SP-4)
- **Candidate methods:** capacitated vehicle routing / multi-trip VRP with **energy/range** and **time-window** elements; parallel-machine scheduling for charging/operators; MILP for small instances and metaheuristics (e.g., adaptive large-neighborhood search, genetic) for realism.
- **Decision content:** bay packing per sortie, tour sequence, landing/offload times, recharge/swap cycles, and the resulting schedule per drone type.
- **Advantage:** captures the core operational question. **Limitation:** large state space → decomposition by site and by mission.

### 5.6 Layer 5 — Reconnaissance flight plan (SP-5)
- **Candidate methods:** coverage path planning / arc-routing (Chinese-Postman-like) over the major-road subgraph; priority-weighted coverage maximization; possibly a "team orienteering" formulation to trade off supply vs. recon sorties.
- **Output:** sorties over road segments with timing, sharing fleet resources with Layer 4 via a scheduling/assignment link.
- **Advantage:** matches the "film the major highways" requirement. **Limitation:** camera/altitude physics abstracted unless data allow.

### 5.7 Layer 6 — Integration & tradeoff analysis (SP-6)
- **Candidate methods:** layered optimization with shared resource/schedule coupling; scenario/sensitivity sweeps; Pareto analysis for cost-vs-coverage-vs-shortfall.
- **Output:** explicit "capability frontier" describing what cannot be met and the tradeoffs (per the problem's requirement).

### 5.8 Cross-cutting mathematical ideas
- Mixed-integer linear programming, multi-objective optimization and Pareto dominance, bin-packing/knapsack, facility location, VRP/scheduling, coverage/arc routing, and uncertainty/sensitivity analysis. Interfaces between layers will be defined by **shared parameter conventions** and **explicit feasibility certificates**.

---

## 6. Implementation Roadmap

### 6.1 Proposed module structure
1. `data_ingest` — attachment transcription, unit normalization, provenance/uncertainty tags.
2. `geo` — road graph construction, distance/energy matrices, demand-node geocoding.
3. `demand_model` — scenario/demand generation (Layer 0).
4. `fleet_select` — portfolio optimization (Layer 1).
5. `packing` — 3-D container packing + fill-efficiency metrics (Layer 2).
6. `siting` — location optimization for 1/2/3 containers (Layer 3).
7. `routing_schedule` — VRP/scheduling per drone type (Layer 4).
8. `recon_plan` — coverage/arc routing over road network (Layer 5).
9. `integration` — coupling constraints, Pareto/tradeoff sweeps (Layer 6).
10. `report` — figures, tables, and the CEO memo scaffold (Part 2).

### 6.2 Algorithm/workflow plan
- **Phase 0 — Setup:** encode attachments; validate units; build geo layers; define scenario parameters.
- **Phase 1 — Baseline build:** solve Layers 0→2 with simplified objectives; obtain a feasible fleet+packing baseline.
- **Phase 2 — Add operations:** solve Layers 3→4; add recon Layer 5; establish an integrated baseline schedule.
- **Phase 3 — Optimize/tradeoff:** iterate selection↔packing↔operations; produce Pareto/tradeoff results and shortfall analysis.
- **Phase 4 — Communicate:** assemble figures/tables and draft the memo.
- **Orchestration:** solve Layers 3–5 per siting case (1/2/3 sites) and compare; use a common scenario seed and shared distance/energy conventions for fairness.

### 6.3 Tooling considerations (planned, not executed)
- Optimization: MILP solvers and open-source metaheuristic/VRP and bin-packing libraries.
- Geospatial: standard Python GIS/geodesy and graph libraries for the road network.
- Reproducibility: fixed seeds, parameter files, and logged provenance for every input.

### 6.4 Deliverable mapping
- SP-1/SP-2 → 1.A; SP-3 → 1.B; SP-4 → 1.C.i; SP-5 → 1.C.ii; SP-6 → tradeoff section; SP-7 → Part 2 memo.

---

## 7. Validation Strategy

### 7.1 Evaluation metrics (to be computed later)
- **Coverage/demand satisfaction rate** (delivered vs. required package units; overall and per MED type).
- **Reconnaissance coverage** (fraction/length of priority road network imaged within the horizon).
- **Resource efficiency** (sorties per drone per horizon, container fill efficiency, cost per delivered unit).
- **Feasibility metrics** (container count ≤3, all packing/fit constraints satisfied, energy/time feasibility percentage).

### 7.2 Validation methods
- **Constraint verification:** programmatic audits that no container, bay, energy, or time constraint is violated (independent checks from the optimizer's own model).
- **Baseline comparison:** compare optimized designs against simple heuristics (e.g., uniform fleet, single-site siting) to confirm added value.
- **Cross-method agreement:** solve representative small instances with both MIP and metaheuristic to check consistency.
- **Internal consistency:** ensure the same route cost appears correctly in scheduling, energy, and coverage reports.
- **Assumption stress tests:** re-evaluate under alternative demand keys, distance conventions, and damage scenarios.
- **Expert/plausibility review:** sanity-check recommended fleet size, site count, and scheduling against operational intuition and the problem's stated constraints.

### 7.3 Sensitivity analysis plan
- Sweep **demand magnitude and spatial distribution** to find where capability saturates (the shortfall frontier).
- Vary **drone performance margins** (range, payload, charge time) to test robustness of the recommended fleet.
- Vary **container/packing parameters** (clearance, compartmentalization) to test fill-efficiency claims.
- Compare **1 vs. 2 vs. 3 site** deployments and **straight-line vs. road-network** distances.
- Rank inputs by their influence on the objective; report which assumptions are decision-critical.

---

## 8. Expected Result Interpretation

This section describes how results will be *read* once produced (no results are reported here):

- The recommended fleet will be interpreted as a **balance** among delivery throughput, recon coverage, cost, and container feasibility — not a single-metric optimum.
- The siting recommendation will be presented per case (1/2/3 containers), highlighting how splitting containers trades **response latency** against **coverage footprint**.
- Delivery routes/schedules will be read as a **feasible operating plan** under the assumed horizon, with explicit utilization and headroom indicators.
- The recon plan will be interpreted as **prioritized coverage**, not guaranteed full imaging; un-imaged segments will be flagged.
- Where demand exceeds capability, the output will be a **tradeoff/shortfall statement** (what is unmet, why, and candidate mitigations: more sorties, more sites, drone substitution, demand prioritization).
- All interpretations will be conditional on the assumption set in Section 3 and the sensitivity results in Section 7.

---

## 9. Limitations and Improvements

### 9.1 Anticipated limitations
- **Data incompleteness:** the attachments are not staged; parameters will rely on transcription/standard published values, introducing uncertainty.
- **Abstraction of sensor/communication physics:** video quality and link reliability will be approximated.
- **Static/aggregated demand:** real post-disaster demand is dynamic and may shift with population movement.
- **Heuristic optimality:** packing and routing layers may be near-optimal, not provably optimal.
- **Coupling complexity:** independently optimized layers can be globally suboptimal without integration.

### 9.2 Planned improvements
- Add **connectivity/airspace** and **weather/wind** constraints to the energy model.
- Introduce **dynamic/stochastic demand** and rolling-horizon re-planning.
- Explore **joint (integrated) formulations** or decomposition/column-generation to reduce layer coupling losses.
- Improve **road-damage data fusion** (satellite/field data) for more realistic reconnaissance prioritization.
- Provide an **interactive tradeoff tool** so HELP, Inc. can explore cost-vs-coverage-vs-shortfall choices.
- Quantify **uncertainty bounds** on all headline recommendations rather than point estimates.

---

### Appendix — Planning checklist (to be confirmed before the modeling phase begins)
- [ ] Attachments 2–5 and Table 1 transcribed into structured tables with units.
- [ ] Puerto Rico coastline/road/population layers acquired or georeferenced.
- [ ] Demand-key and scenario parameters fixed and documented.
- [ ] Layer interfaces (feasibility certificates, shared distance/energy conventions) specified.
- [ ] Validation audits and sensitivity sweeps implemented before interpreting results.

*End of planning draft — no analysis, computation, or results are included by design.*
