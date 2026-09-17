# School Busing — Initial Modeling Plan (Blueprint Draft)

> Status: **Planning draft only.** This document describes a modeling roadmap for future work.
> It contains no computed results, no data analysis, no fitted models, and no final conclusions.

---

## 1. Problem Background and Restatement

The scenario concerns a school district in which most students live in rural areas and therefore
must be transported by bus. Two school levels are involved: an elementary school and a high school.
A key structural feature of the problem is the possibility of **route sharing**: buses might first
pick up students and drop them at the elementary school, then continue along (possibly overlapping)
routes to serve the high school. A clearly different design philosophy is to operate **separate
fleets for each school**, accepting duplicated route segments in exchange for simpler scheduling and
independent capacity management.

The district faces multiple simultaneous constraints:

- **Time**: no student should spend more than one hour on the bus.
- **Drivers**: a limited pool with working-hour and shift constraints.
- **Equipment**: a finite, heterogeneous bus fleet with differing capacities and operating costs.
- **Budget**: total transportation spending must be optimized (minimized subject to service quality,
  or balanced against service quality).
- **Equity / service quality**: time-on-bus should be balanced reasonably across student groups and
  across the two schools.

The problem asks how to design bus routes that **optimize budget dollars while balancing time on the
bus for various school groups**, in a form general enough to be reusable by other rural (and possibly
urban) districts. It further asks how such a model would be tested before implementation, and it
requests a short explanatory article for a school board.

**Restatement as a planning object:** the deliverable is a transferable decision-support modeling
framework — not a single numerical answer — that maps a district's student, road, and fleet
descriptions to a set of bus routes, schedules, and assignments, together with a testable validation
protocol and a non-technical communication artifact.

---

## 2. Objectives and Subproblems

### 2.1 Primary Objective

To formulate a **general, parameterized optimization model** that determines bus routes, schedules,
and fleet assignments for a multi-school (here: elementary + high) rural district, minimizing total
transportation cost while respecting time-on-bus limits and balancing service quality across school
groups.

### 2.2 Secondary Objectives

- To make the model **portable**: parameters and data schema should allow re-use by other rural or
  urban districts with minimal restructuring.
- To make the cost-versus-equity trade-off **explicit and tunable** rather than hidden.
- To define a **pre-implementation test protocol** for the model.
- To produce a **communication artifact** (school board article) that explains assumptions and
  behavior of the model in accessible language.

### 2.3 Subproblems (decomposition for later work)

1. **Data representation / spatial abstraction** — How should students, stops, schools, and the road
   network be represented compactly and portably (e.g., aggregated demand nodes, distance/cost
   matrices)?
2. **Stop & demand aggregation** — How to group individual student addresses into feasible pickup
   points without inflating cost or violating walk/access limits.
3. **Routing subproblem** — How to construct routes (sequences of stops) under capacity and time
   limits, allowing or disallowing inter-school chaining.
4. **Scheduling / synchronization subproblem** — How to sequence arrival/departure times so that a
   bus can serve school A then school B within driver/vehicle availability and bell schedules.
5. **Fleet composition subproblem** — How many and which bus types to use, and how to assign them.
6. **Equity / balance subproblem** — How to measure and constrain the distribution of time-on-bus
   across student groups.
7. **Scenario comparison** — How to structure the comparison between "shared/chained" and
   "separate fleet" operating regimes.
8. **Validation design** — How to test the model before real-world implementation.

### 2.4 Deliverables (planned)

- A formal model specification (objective, decision variables, constraints, parameters).
- A parameterized implementation (solver/pipeline) able to ingest a district dataset.
- A scenario-comparison report structure (shared vs. separate fleets).
- A validation protocol and sensitivity-analysis plan.
- A school board article draft.

---

## 3. Assumptions

The following assumptions are **proposed** for the modeling stage; each is paired with justification
and a planned validation approach. They are stated as working assumptions to be confirmed during
later stages.

### 3.1 Structural / Abstracting Assumptions

| # | Assumption | Justification | Planned Validation |
|---|-----------|---------------|--------------------|
| A1 | Student demand can be aggregated into a finite set of pickup nodes/stops. | Individual-address routing is intractable; stop-based systems are standard in practice. | Compare aggregated vs. finer-grained routing on a pilot area; check walk-distance feasibility. |
| A2 | Travel times between nodes can be approximated by a static matrix (e.g., from distances and average speeds). | Full traffic simulation is out of scope for a planning model; static times are common. | Test sensitivity to time perturbations; validate a sample of routes against observed times. |
| A3 | A single bus may serve both schools sequentially (chaining), subject to bell-schedule feasibility. | This is the core design alternative the problem highlights. | Compare chained vs. separate-fleet scenarios explicitly. |
| A4 | School bell times / start-end times are fixed parameters (or a small set of scenarios). | Districts set these administratively; model treats them as inputs. | Run scenarios across plausible bell-time configurations. |
| A5 | Bus capacity is defined per bus type; no standing capacity is used. | Safety regulation; standard fleet assumption. | Verify against local capacity regulations. |
| A6 | Drivers are interchangeable with respect to a bus type, subject to shift-length rules. | Simplifies assignment; justified unless licensing restricts types. | Relax to type-specific driver pools as a sensitivity case. |
| A7 | One-hour time-on-bus limit applies per student per trip and is a hard constraint. | Explicit in the problem statement. | Test near-boundary routes; case-study check. |
| A8 | Route segments may be traversed by more than one bus in the separate-fleet regime. | Reflects the "trace over the same routes" alternative. | Explicit cost accounting for duplicated distance. |

### 3.2 Modeling Assumptions

| # | Assumption | Justification | Planned Validation |
|---|-----------|---------------|--------------------|
| A9 | Cost is dominated by fixed per-bus costs plus per-distance/per-time operating costs. | Standard transportation costing. | Compare against district budget line items. |
| A10 | Stop locations are chosen from a candidate set (existing intersections/home clusters) rather than continuous space. | Keeps stop-selection discrete and comparable. | Compare candidate-generation strategies. |
| A11 | Time-on-bus equity can be encoded via a convex/penalty term or explicit fairness constraints. | Allows tunable balance between cost and equity. | Sensitivity across equity formulations. |
| A12 | Demand is deterministic for a given school day (no stochastic ridership in first version). | Simplifies the base model. | Later extension to stochastic/robust demand. |
| A13 | Vehicle routes are per-trip (morning/afternoon) and can be mirrored, but not necessarily symmetric. | Real routes may differ by direction. | Compare symmetric vs. asymmetric route assumptions. |

### 3.3 Assumptions to Revisit

- Whether chained service is operationally acceptable given driver rest rules.
- Whether crossing between elementary and high school attendance zones is permitted.
- Whether walking to stops is safe/allowed for young elementary students (may force door-side stops).

---

## 4. Data Processing Plan

*This section describes how data will be prepared in a future stage. No data will be analyzed here.*

### 4.1 Data Inventory (to be obtained / constructed)

- **Student/demand data**: counts by residence location (or aggregated neighborhood), grade level,
  school assignment; potentially walk-distance tolerance by age.
- **Spatial data**: road network, distances, average travel speeds, one-way/restriction attributes,
  candidate stop locations (intersections, community nodes).
- **School data**: locations, bell times, capacity, school-attendance-zone rules.
- **Fleet data**: bus types, capacities, fixed and per-km/per-hour operating costs, availability.
- **Driver data**: count, shift limits, licensing-by-type (if applicable).
- **Policy data**: maximum time-on-bus (1 hour), budget envelope, equity expectations.
- **Baseline data**: current routes/costs (for comparison and calibration).

### 4.2 Preprocessing Plan

1. **Geocoding & spatial joining** — map student addresses (or clusters) to a spatial reference.
2. **Demand aggregation** — cluster demand points into candidate stops using a distance/density rule
   (e.g., radius or k-means-style grouping) constrained by walk distance and stop capacity.
3. **Network construction** — build a graph over stops and schools; compute all-pairs travel
   time/distance matrices using distances and assumed speeds.
4. **School linkage** — attach each demand node to its served school(s) and, if relevant, allowed
   chaining relationships between the elementary and high school.
5. **Fleet parameterization** — tabulate bus types with capacity and cost vectors.
6. **Scenario parameterization** — define regime flags (chained vs. separate; bell-time options).
7. **Data quality checks** — completeness, duplicate removal, outlier/edge location handling,
   consistency of units.

### 4.3 Feature / Structure Construction

- Node-level features: demand by school, coordinates, candidate-stop candidacy.
- Edge-level features: travel time, distance, cost, directionality.
- Route-level derived quantities (to be computed inside the model, not by hand): load profile,
  time-on-bus per student, cost per route.
- Equity features: per-group time-on-bus distributions for balance constraints/objectives.

### 4.4 Data Usage Strategy

- **Training/calibration slice**: baseline routes and costs for parameter tuning.
- **Scenario slices**: shared-fleet vs. separate-fleet inputs.
- **Hold-out / pilot area**: a sub-district reserved for testing model behavior on unseen demand.
- **Synthetic / scaled instances**: generated configurable districts to test portability across
  rural-to-urban scales (since the model must generalize).

---

## 5. Candidate Model Framework

*Candidate methods are listed as options to be evaluated, not as a committed solution.*

### 5.1 Overall Framing

The problem is a **rich vehicle routing problem with time windows, heterogeneous fleet, multi-depot /
multi-school service, and equity considerations** — i.e., a variant of the **School Bus Routing
Problem (SBRP)**. It will likely be decomposed into sub-models that interact through shared
parameters.

### 5.2 Candidate Model Families

**A. Mixed-Integer Programming (MIP) formulations**
- Vehicle-flow / arc-based formulations for routing and assignment.
- Set-partitioning formulations: generate feasible routes, then choose a covering set (strong for
  medium instances, pairs well with column generation).
- Advantages: explicit constraints, provable bounds, clear objective structure.
- Limitations: combinatorial blow-up; requires careful formulation and possibly decomposition.

**B. Decomposition / Hierarchical Models**
- Stage 1: stop selection / clustering.
- Stage 2: route generation per school or per chained sequence.
- Stage 3: scheduling & fleet assignment.
- Advantages: tractable; mirrors real planning workflow.
- Limitations: sub-optimality due to sequential decisions; needs feedback loops.

**C. Metaheuristics / Heuristics (for large or hard instances)**
- Genetic algorithms, simulated annealing, tabu search, ant-colony, large-neighborhood search.
- Advantages: scale to realistic districts; flexible objective/constraint handling.
- Limitations: no optimality guarantee; requires tuning; stochastic results.

**D. Constraint Programming (CP) / Hybrid CP-MIP**
- Advantages: strong scheduling/time-window handling; combines well with routing.
- Limitations: performance variability; modeling effort.

**E. Simulation Model (supporting / validation)**
- Discrete-event simulation of routes, loads, and timing to stress-test plans.
- Advantages: captures stochasticity and operational dynamics the optimizer ignores.
- Limitations: not an optimizer; requires data.

**F. Multi-Objective Optimization**
- Objectives: minimize cost; minimize/balance time-on-bus; possibly minimize number of buses.
- Techniques: weighted-sum, ε-constraint, Pareto-frontier exploration.
- Advantages: surfaces the cost–equity trade-off explicitly.
- Limitations: choice of weights; interpretation of Pareto sets.

### 5.3 Candidate Decision Variables (sketch)

- Binary route-selection variables (which generated routes are used).
- Assignment variables (which stops/students are served by which route/bus).
- Sequence/ordering variables (visit order within a route).
- Scheduling variables (arrival/departure times at stops and schools).
- Fleet variables (number and type of buses of each kind).
- Chaining/regime variables (whether a bus serves school A then school B).
- Equity/balancing auxiliary variables (e.g., max/mean deviations of time-on-bus).

### 5.4 Candidate Parameters

- Demand per node per school; bus capacities; fixed and variable costs; travel times/distances;
  bell times; maximum ride time; driver shift limits; equity tolerance/weights; regime flags.

### 5.5 Candidate Constraints (sketch)

- Coverage: every student reaches the correct school.
- Capacity: route load ≤ selected bus capacity.
- Time-on-bus: ride duration ≤ 1 hour (hard), with optional tighter targets (soft/equity).
- Time windows: arrival within school bell-tolerance windows.
- Fleet availability: buses used ≤ buses owned (by type).
- Driver rules: shift length and (if modeled) rest constraints.
- Chaining feasibility: sequential school service consistent with schedules.
- Budget: total cost ≤ budget (or budget is the objective).

### 5.6 Objective Function Candidates

1. Pure cost minimization (fixed + distance + time).
2. Cost with equity penalty: `Cost + λ · imbalance(time-on-bus)`.
3. Lexicographic: minimize buses, then minimize ride time, subject to cost cap.
4. Multi-objective Pareto exploration of cost vs. equity.

### 5.7 Recommended Working Hypothesis (to be tested later)

A **hierarchical decomposition** (stop formation → route generation → scheduling/fleet assignment)
with a **set-partitioning / MIP core** and a **metaheuristic fallback for large instances**, embedded
in a **multi-objective cost–equity** evaluation, is anticipated to be the most practical starting
point. This is a hypothesis for later evaluation, not a conclusion.

---

## 6. Implementation Roadmap

*Planned stages; no code is written or executed in this draft.*

### 6.1 Module Plan

1. **Data ingestion module** — schema for students, stops, network, fleet, policy; loaders/validators.
2. **Spatial/preprocessing module** — clustering, matrix construction, candidate-stop generation.
3. **Model-builder module** — construct MIP/set-partitioning/CP models from parameters.
4. **Route-generation module** — enumerate feasible routes (with pruning) for set-partitioning.
5. **Optimization/solver module** — MIP solver interface; metaheuristic implementations.
6. **Scheduling module** — time-window and chaining feasibility.
7. **Equity/objective module** — balance metrics and trade-off handling.
8. **Scenario manager** — shared vs. separate fleet; bell-time and budget scenarios.
9. **Evaluation/validation module** — metrics, sensitivity runs, comparison tables.
10. **Reporting module** — board-facing summaries and technical appendix generation.

### 6.2 Suggested Work Order

1. Formalize data schema and generate a small **toy instance** for structural testing.
2. Implement preprocessing (clustering + matrices) and validate on the toy instance.
3. Implement the base routing/assignment model (single school) and validate constraints.
4. Extend to two schools with **chaining** capability.
5. Add **fleet heterogeneity** and cost accounting.
6. Add **equity** terms and multi-objective handling.
7. Add scaling: route generation + metaheuristic for larger instances.
8. Build scenario manager (shared vs. separate).
9. Build evaluation, sensitivity, and reporting tooling.

### 6.3 Tooling (candidate, to be chosen later)

- Language/ecosystem: Python (or Julia) for modeling; open-source MIP solver (e.g., CBC/HiGHS) with
  option to switch to commercial solver for large instances.
- CP option: a CP-SAT-style toolkit.
- Simulation: a lightweight discrete-event component.
- Reproducibility: configuration files, fixed seeds, versioned datasets, scripted pipelines.

### 6.4 Engineering Considerations

- Keep model **data-driven** (no hard-coded district values) to satisfy portability requirement.
- Separate **model definition** from **solver choice**.
- Design scenario flags so shared/separate fleets are a configuration, not a code fork.
- Log model infeasibilities clearly (which constraints bind) to aid validation.

---

## 7. Validation Strategy

### 7.1 Verification (does the model do what we intend?)

- **Unit/structural tests** on toy instances with known-by-construction behavior.
- **Constraint feasibility checks**: no capacity or time-limit violations in produced plans.
- **Accounting checks**: recompute costs independently from the route output.
- **Coverage checks**: every student served exactly once per trip.

### 7.2 Validation (does the model reflect reality / remain useful?)

- **Baseline comparison**: compare model-proposed plans with the district's current routes/costs
  (where baseline data exists).
- **Expert review**: route feasibility judged by transportation staff.
- **Pilot deployment**: run a limited area/route set before full implementation.
- **Cross-scenario consistency**: shared vs. separate fleets should be comparable on identical data.

### 7.3 Evaluation Metrics (candidate)

- Total transportation cost (fixed + operating).
- Number of buses / fleet composition used.
- Average and maximum time-on-bus; percentage of students near the 1-hour limit.
- Equity imbalance measures across groups/schools (e.g., max–mean or variance of ride times).
- Route count, total distance, total driver-hours.
- Solver performance: runtime, optimality gap (for exact methods).
- Feasibility rate across generated/synthetic instances (portability test).

### 7.4 Sensitivity Analysis Plan

- Vary **travel times** (±) to test robustness to traffic assumptions.
- Vary **demand** (growth/shrinkage) and **demand distribution**.
- Vary **fleet mix / capacity** and **driver availability**.
- Vary **bell times** and **maximum ride-time** (e.g., 45/60/75 minutes).
- Vary **equity weight λ** and **budget envelope** to trace the cost–equity trade-off.
- Vary **stop granularity** to test aggregation assumptions.

### 7.5 Testing Prior to Implementation (answering the problem's explicit ask)

1. Offline verification on toy + realistic-but-historical instances.
2. Retrospective comparison against prior years' routes and budgets.
3. Shadow planning: produce a full-year plan without deploying it; have staff critique it.
4. Limited live pilot on selected routes/areas, with monitored time-on-bus and cost.
5. Staged rollout contingent on pilot metrics meeting agreed thresholds.

---

## 8. Expected Result Interpretation

*This section describes how results will be interpreted once produced — no results are produced here.*

- The model is expected to output, for a given district and scenario, a set of routes, an associated
  schedule, and a fleet assignment, along with cost and equity indicators.
- Comparison between **chained/shared** and **separate-fleet** regimes is expected to reveal a
  trade-off: chaining may reduce distance/buses while increasing scheduling complexity and possibly
  ride times; separate fleets may simplify operations at higher duplicated-distance cost.
- The **cost–equity frontier** (from varying λ / constraints) is expected to inform policy: how much
  extra budget buys how much reduction in the worst-case or most-unequal ride times.
- Results should be read as **decision support under stated assumptions**, sensitive to the
  assumptions in Section 3 — not as definitive prescriptions.
- Portability is interpreted by how consistently the framework reproduces sensible plans across
  rescaled/synthetic districts (rural to urban).

---

## 9. Limitations and Improvements

### 9.1 Anticipated Limitations

- **Static travel times** ignore congestion, weather, and time-of-day variation.
- **Deterministic demand** ignores absences, enrollment shifts, and special-needs variability.
- **Aggregated stops** may misestimate door-to-door access and equity for young students.
- **Hard 1-hour limit** modeling may create infeasibility in sparse rural areas; needs fallback logic.
- **Solver scalability** may limit exact optimality for large districts, forcing heuristics.
- **Equity quantification** is inherently normative; choice of metric affects conclusions.
- **Driver/union rules** are simplified and may not capture contractual nuances.
- The framework cannot capture political/community constraints that fall outside the model.

### 9.2 Planned Improvements / Extensions

- Stochastic or robust demand and travel-time formulations.
- Time-dependent travel times and traffic-aware routing.
- Special-needs and accessibility constraints; mixed student categories.
- Integrated stop-selection with routing (rather than two-stage) where tractable.
- Interactive tooling so district planners can explore scenarios directly.
- Richer driver scheduling with break/rest and multi-trip constraints.
- Calibration/learning from historical GPS/route data if available.
- Explicit uncertainty reporting (confidence/cost ranges) to accompany point plans.

---

## Appendix A — Section Coverage Checklist

- [x] Problem Background and Restatement (§1)
- [x] Objectives and Subproblems (§2)
- [x] Assumptions (§3)
- [x] Data Processing Plan (§4)
- [x] Candidate Model Framework (§5)
- [x] Implementation Roadmap (§6)
- [x] Validation Strategy (§7)
- [x] Expected Result Interpretation (§8)
- [x] Limitations and Improvements (§9)

## Appendix B — Scope Statement

This document is a **planning blueprint**. It intentionally excludes computed results, executed
experiments, data analysis, fitted models, and final conclusions. All content is future-oriented and
intended to guide the subsequent modeling stage.
