# School Busing — Modeling Blueprint (Initial Draft)

**Problem ID:** 2002_School_Busing
**Title:** School Busing
**Source:** HiMCM 2002
**Document type:** Planning blueprint / modeling roadmap (not a solution)
**Status:** Initial draft for future modeling work

> Scope note: This document is a *plan*. It specifies objectives, assumptions, candidate
> model families, data plans, an implementation roadmap, and a validation strategy. It does
> **not** contain computed results, executed experiments, fitted models, or final
> conclusions. All statements are written in future-oriented / conditional form.

---

## 1. Problem Background and Restatement

### 1.1 Background

A rural school district (and by extension comparable urban districts) must transport most
students by bus because students live far from their schools. The district operates at
least two school levels of interest — an **elementary school** and a **high school** —
whose start times and attendance boundaries may differ. Buses represent a major recurring
cost (vehicles, fuel, drivers, maintenance), and there are hard service constraints on how
long a student may remain on a bus.

The central operational tension described in the statement is:

- **Route reuse / chained ("double-run") service:** one bus picks up elementary students,
  delivers them to the elementary school, then continues to pick up high-school students —
  which may require the bus to retrace shared segments of the route.
- **Dedicated (separate) service:** distinct buses are assigned to each school, which
  avoids chaining complexity but may duplicate travel over the same roads.

The district wants to choose routes and schedules that **optimize budget dollars while
balancing bus-ride time across student groups**, subject to limits on time, drivers,
equipment, and money.

### 1.2 Restatement as a decision problem (to be formalized later)

The eventual modeling effort will seek to determine:

- how many buses/drivers will be needed,
- which stops will be assigned to which bus and in what order,
- whether a bus will serve one school or be chained across schools,
- at what times buses will depart and arrive so that school start times are met,
- how the resulting cost and the distribution of student ride times will be evaluated
  against a set of explicit objectives and constraints.

### 1.3 Why this is a modeling (not computational) task

The problem is deliberately open-ended: the statement provides no dataset, so a key portion
of the future work will be **model scoping and data acquisition planning** rather than fixed
numeric optimization on a given instance. The blueprint therefore treats the district's
scale, geography, and policy environment as parameters of a *reusable, generalizable model*
that could be applied to different rural and urban districts.

---

## 2. Objectives and Subproblems

### 2.1 Primary objective (planned)

Design a **school bus routing and scheduling model** that will:

1. minimize (or suitably trade off) total transportation cost, and
2. keep student ride times within acceptable and fairly distributed bounds,
3. while satisfying operational constraints (ride-time cap, driver, vehicle, budget, and
   school-bell timing), and
4. remain **portable across districts** with different geography and demographics.

### 2.2 Secondary objectives (planned)

- Provide a decision tool that a school board can interpret (cost vs. fairness trade-offs).
- Offer a documented, testable procedure for pre-implementation validation.
- Support a short, non-technical explanatory article for the school board.

### 2.3 Decomposition into subproblems

| ID | Subproblem | Nature (planned) |
|----|------------|------------------|
| SP1 | **Student-to-stop assignment** (walk/group students to a manageable set of bus stops) | Assignment / clustering |
| SP2 | **Route generation per school** (sequence stops for a bus serving one school) | Vehicle routing (VRP family) |
| SP3 | **Chained / multi-school routing** (a bus serves elementary then high school) | Multi-trip VRP / scheduling |
| SP4 | **Fleet and driver sizing** (how many buses/drivers, which vehicle types) | Resource sizing / integer planning |
| SP5 | **Timetable synchronization** (departures tied to school start/end bells, ride-time caps) | Scheduling / temporal constraints |
| SP6 | **Cost vs. fairness trade-off analysis** (budget dollars vs. ride-time balance) | Multi-objective optimization |
| SP7 | **Generalization / transferability** (rural vs. urban parameterization) | Scenario & sensitivity analysis |
| SP8 | **Pre-implementation testing plan** and **school-board communication** | Validation design & communication |

### 2.4 Deliverables (planned)

- A formal model specification (decision variables, objective(s), constraints).
- An instance data schema and a data-acquisition/parameterization procedure.
- An algorithmic solution approach and an implementation architecture.
- A validation plan (metrics, methods, sensitivity analyses).
- A narrative article outline addressed to the school board.
- (Future) representative scenario runs and trade-off summaries — to be produced in a later,
  separate solving phase, not in this draft.

---

## 3. Assumptions

Assumptions are grouped by type. Each is paired with a rationale and a future validation
approach. These are *proposed* assumptions to be confirmed or revised during modeling.

### 3.1 Structural / scope assumptions

| # | Assumption | Rationale | Future validation approach |
|---|------------|-----------|----------------------------|
| A1 | The district has a finite, known set of schools (at minimum one elementary and one high school) with fixed locations. | Matches the statement; needed to define depots. | Confirm with district facility records. |
| A2 | Students are "demand points" that can be aggregated to a finite set of candidate bus stops. | Full door-to-door routing is intractable and unrealistic. | Compare stop-aggregation granularity in scenario tests. |
| A3 | The road network can be represented as a graph with known inter-node travel distances/times. | Enables routing/VRP formulations. | Validate against map/road-distance data sources. |
| A4 | Each school has, or can be assigned, a bell (start/end) time; arrival must precede the bell. | Drives scheduling constraints. | Confirm actual bell schedules with the district. |
| A5 | Buses operate within a daily window; no overnight repositioning requirements are modeled initially. | Simplifies the first model. | Extend later if depots require repositioning. |
| A6 | The model addresses daily (regular) service; special trips (field trips, athletics) are out of scope initially. | Focuses the first model. | Add as an extension if the board requests. |

### 3.2 Demand / demographic assumptions

| # | Assumption | Rationale | Future validation approach |
|---|------------|-----------|----------------------------|
| A7 | Student counts per stop/area are known or estimable (e.g., from enrollment and residence data). | Required to size buses and estimate load. | Reconcile against enrollment and GIS residence data. |
| A8 | Demand is treated as deterministic and approximately constant across weekdays within a season. | First model is deterministic; avoids stochastic complexity. | Later test stochastic/day-to-day variation. |
| A9 | Every eligible student must be transported (no voluntary non-riders), unless flagged. | Consistency with "most students must be bused". | Confirm eligibility policy with the district. |

### 3.3 Operational / policy assumptions

| # | Assumption | Rationale | Future validation approach |
|---|------------|-----------|----------------------------|
| A10 | A hard cap on student ride time exists (the statement cites one hour); it will be treated as a tunable parameter. | Statement gives "no student should be in the bus more than an hour". | Sensitivity analysis around the cap (e.g., 45–75 min). |
| A11 | Bus capacity per vehicle is finite and may vary by vehicle type. | Physical and safety reality. | Confirm fleet composition and capacities. |
| A12 | Drivers are a constrained resource with working-time limits and possible duty rules. | Statement lists "drivers" as a restriction. | Confirm labor rules/duty limits with the district. |
| A13 | Buses return to a depot/base between or after runs (single-depot initially; multi-depot as an extension). | Standard school-bus practice. | Confirm depot location(s). |
| A14 | Chained service is allowed only when it does not violate ride-time or bell constraints. | Makes chaining a *decision*, not an assumption. | Compare chained vs. dedicated in scenarios. |

### 3.4 Cost / economic assumptions

| # | Assumption | Rationale | Future validation approach |
|---|------------|-----------|----------------------------|
| A15 | Cost decomposes into fixed per-bus (ownership/driver) and variable per-distance/per-time components. | Standard transportation cost structure. | Calibrate against district budget lines. |
| A16 | Money is comparable across options within one district; no external subsidies are modeled initially. | Keeps objective well-defined. | Add subsidy/reimbursement rules if relevant. |

### 3.5 Assumption-management note

All assumptions above will be stored in an **assumptions register** that links each
assumption to (a) the model component it affects, (b) its confidence, and (c) the planned
sensitivity test. The register will be revisited after each validation pass.

---

## 4. Data Processing Plan

Because the source statement supplies **no dataset**, the data plan has two layers:
(1) a **general data schema** and (2) an **acquisition & parameterization procedure** for
applying the model to a concrete district.

### 4.1 Required data schema (to be defined)

| Data block | Representative fields | Purpose |
|------------|-----------------------|---------|
| Schools | id, level (elementary/high), location (lat/long), bell times | Depots & arrival deadlines |
| Stops / demand points | id, location, assigned students (by school level) | Demand nodes |
| Road network | node pairs, distance, travel time, road class | Routing graph |
| Fleet | vehicle id, capacity, cost rates, availability | Vehicle resources |
| Drivers | count, duty-time limits, cost | Labor constraints |
| Costs | fixed & variable rates, budget ceiling | Objective calibration |
| Policy | ride-time cap, eligibility rules, walking-distance policy | Constraints |

### 4.2 Preprocessing plan (to be implemented later)

1. **Geocoding & cleansing** — normalize school/stop addresses to coordinates.
2. **Coordinate validation** — remove duplicates, detect out-of-district points, verify
   location plausibility.
3. **Network construction** — build the travel-time/distance graph from a routing source.
4. **Demand aggregation** — cluster nearby student residences into candidate stops using a
   planned distance/size rule (parameters to be tuned).
5. **Capacity & feasibility screening** — flag stops or areas that appear infeasible under
   initial capacity/ride-time parameters.
6. **Cost calibration** — map budget line items onto fixed/variable cost coefficients.
7. **Parameter tables** — assemble a tidy configuration file of all tunable parameters.

### 4.3 Feature construction (to be planned)

- **Stop-level features:** number of students by school level, distance to each school,
  nearest-neighbor distances, isolation/remoteness indicator.
- **Graph features:** pairwise travel time/distance matrices, shortest-path trees to each
  school, connectivity/sparsity indicators.
- **Scenario features:** rural vs. urban density proxies (stops per area, mean spacing),
  fleet size, budget ceiling.
- **Fairness features:** per-stop and per-group ride-time estimates (to be used in the
  balancing objective).

### 4.4 Data usage strategy

- **Primary usage:** all district-specific data feeds the routing/scheduling model instance.
- **Synthetic/generative usage:** since the original problem lacks data, **plausible
  synthetic districts** will be generated (ranging from sparse-rural to denser-urban) to
  exercise the model, probe sensitivity, and demonstrate transferability. Synthetic
  generation is a *planned test harness*, not a source of "results".
- **Held-out usage:** where multiple real districts become available, reserve at least one
  district as a **transfer set** (build/tune on others, test on the held-out district).
- **Provenance:** every dataset will record source, date, and processing steps for
  reproducibility.

### 4.5 Data quality / risk notes (planned)

- Missing or inconsistent enrollment vs. residence data.
- Ambiguous walking-distance and eligibility policies.
- Uncertainty in travel-time estimates (traffic, road closures, weather).
- Privacy constraints on student residence data (aggregation required).

---

## 5. Candidate Model Framework

The plan is to build a **layered framework**: a core deterministic optimizer (VRP/
scheduling) with an optional fairness mechanism and scenario wrapper. Candidate model
families are listed with anticipated strengths and limits. Final selection will be deferred
to the modeling phase.

### 5.1 Core routing model — candidate families

| Candidate | Idea | Advantages | Limitations |
|-----------|------|-----------|-------------|
| C1: **Capacitated VRP (CVRP)** per school | Route stops for one school's students with capacity + ride-time limits. | Mature, well-understood, easy to explain. | Ignores cross-school chaining. |
| C2: **Multi-trip / chained VRP** | One vehicle performs sequential trips (elementary, then high school). | Captures the "double-run" option in the statement. | More complex sequencing & timing. |
| C3: **School Bus Routing Problem (SBRP)** formulation | Combined stop selection + routing + scheduling with bell constraints. | Closest to the real problem; integrates SP1–SP5. | Larger, harder to solve exactly. |
| C4: **Mixed-Integer Program (MIP)** for route selection over a candidate route pool | Generate candidate routes, then select a cost-minimal covering set. | Clean budget/resource modeling; good with column-generation. | Needs a good route-generation step. |
| C5: **Set-covering / set-partitioning** view | Select routes covering all stops at minimum cost. | Natural for "how many buses" question. | Requires route enumeration/generation. |

### 5.2 Scheduling / timing model (SP5)

- Model departures and arrivals with **time-window constraints** anchored to school bells.
- Enforce **ride-time cap** per student (max on-board time).
- Handle **chained trips** by ordering trips within a vehicle's day and enforcing turnaround.

### 5.3 Multi-objective / fairness model (SP6)

Planned candidate approaches:

- **Weighted-sum scalarization** of cost vs. ride-time dispersion (simple, tunable).
- **ε-constraint** method to trace a Pareto frontier of cost vs. fairness.
- **Min–max / lexicographic** formulations that bound the worst-case ride time.
- **Equity metrics** (e.g., spread between student groups' ride times) as additional
  objectives or constraints to be defined carefully in the modeling phase.

### 5.4 Decision variables (planned, symbolic)

- `x` route/assignment variables: which stop is served by which vehicle/trip and in what
  order.
- `y` vehicle-usage variables: whether a vehicle is used and how many trips it performs.
- `t` time variables: departure/arrival times and on-board durations.
- `z` chaining variables: whether a vehicle transitions from one school's trip to another.
- Parameter set: capacities, ride-time cap, cost rates, bell times, demand.

### 5.5 Mathematical ideas to be employed (planned)

- Graph shortest paths and travel-time matrices.
- Vehicle routing (CVRP, multi-trip VRP, pick-up routing).
- Mixed-integer linear programming and set partitioning/covering.
- Clustering / facility-location style stop aggregation.
- Multi-objective optimization and Pareto analysis.
- Queuing/throughput reasoning for depot turnaround (optional extension).

### 5.6 Framework-wide advantages / limitations (anticipated)

- **Advantages:** modular; supports chained vs. dedicated comparison; generalizes to rural
  and urban via parameters; produces interpretable cost/fairness trade-offs.
- **Limitations:** deterministic core ignores day-to-day variability; realism depends on
  data quality; large instances may need heuristics; fairness definition is policy-driven
  and may need board input.

---

## 6. Implementation Roadmap

This section describes *how the future work will be organized*. No code will be written in
this draft.

### 6.1 Proposed module architecture

| Module | Responsibility |
|--------|----------------|
| M1 Data layer | Schema, ingestion, cleansing, geocoding, provenance. |
| M2 Network layer | Graph/travel-time matrix construction, shortest paths. |
| M3 Demand layer | Stop generation/aggregation, demand assignment to stops. |
| M4 Route generation | Candidate route construction (per-school and chained). |
| M5 Optimization core | MIP/set-partitioning CVRP + scheduling solver. |
| M6 Objective/fairness layer | Weighted-sum / ε-constraint / min–max wrappers. |
| M7 Scenario engine | Rural↔urban parameterization, synthetic district generator. |
| M8 Evaluation layer | Metrics computation, Pareto extraction, reporting artifacts. |
| M9 Reporting layer | School-board article, tables, (future) figures. |

### 6.2 Workflow (planned sequence)

1. Finalize assumptions register and model specification (Sections 3 & 5).
2. Implement data & network layers (M1–M2) and freeze the data contract.
3. Implement demand/stop layer (M3) and validate stop aggregation choices.
4. Implement route generation (M4) and the optimization core (M5).
5. Add scheduling/time constraints and chaining logic.
6. Add objective/fairness layer (M6) and trace trade-offs.
7. Build the scenario engine (M7) and generate test districts.
8. Run validation (Section 7) and iterate on assumptions.
9. Produce outputs: trade-off summaries and the school-board article (M9).

### 6.3 Algorithms (candidate, to be selected later)

- Exact: MILP solvers for moderate instances; column generation for route-pool methods.
- Heuristic/metaheuristic: construction + local search, savings algorithms, genetic or
  large-neighborhood search for large instances.
- Clustering: k-means / facility-location variants for stop aggregation.
- Multi-objective: scalarization sweeps and ε-constraint for Pareto fronts.

### 6.4 Reproducibility & engineering practices (planned)

- Versioned configuration files for all parameters.
- Deterministic random seeds for any stochastic components.
- Automated pipeline with logging of every run's inputs/outputs.
- Unit tests for distance matrices, feasibility checks, and constraint enforcement.
- Separate `build` (model) and `run` (scenarios) stages.

### 6.5 Tooling (anticipated, not yet chosen)

- A general-purpose programming language for the pipeline.
- An off-the-shelf MILP/optimization solver.
- A routing/geospatial library for network and distance computation.
- A lightweight reporting layer for the board article.

---

## 7. Validation Strategy

Validation will be multi-layered and *planned before* implementation.

### 7.1 Evaluation metrics (to be defined)

| Metric group | Example metrics (planned) |
|--------------|---------------------------|
| Cost | Total daily cost; cost per student; cost per bus; fleet count. |
| Ride time | Mean/median ride time; max ride time; % over cap; variance. |
| Fairness | Spread of ride times between groups; worst-group vs. best-group gap. |
| Feasibility | Constraint-violation counts (capacity, bell time, duty hours). |
| Service coverage | % of students assigned; unserved/flagged stops. |
| Robustness | Metric variation under demand/travel-time perturbations. |

### 7.2 Validation methods (planned)

1. **Internal consistency checks** — verify every route satisfies capacity, ride-time, and
   bell constraints; reconcile cost decomposition.
2. **Benchmarking on small instances** — solve tiny hand-checkable cases exactly to confirm
   the formulation behaves as intended.
3. **Heuristic-vs-exact comparison** — where instances are small enough, compare heuristic
   solutions to exact optima to bound the optimality gap.
4. **Cross-model comparison** — compare candidate families (C1 vs. C2 vs. C3) on the same
   instances for cost and fairness.
5. **Synthetic scenario testing** — sweep rural↔urban density and demand parameters.
6. **Stress/edge testing** — extreme caps, tight budgets, isolated students, single-bus
   districts.
7. **Held-out district transfer test** — tune on some districts, test on an unseen district.
8. **Expert / stakeholder review** — sanity-check routes and assumptions with transportation
   staff and the school board.

### 7.3 Sensitivity analysis (planned)

- Ride-time cap (e.g., varying around one hour).
- Bus capacity and fleet composition.
- Cost coefficients (fixed vs. variable split, fuel/driver rates).
- Demand levels (enrollment growth/decline).
- Travel-time uncertainty (traffic, weather, road closures).
- Policy levers (walking distance, eligibility, chaining allowed or not).

### 7.4 Pre-implementation testing plan (for the board)

A staged pilot will be proposed: (i) offline replay against a past academic year, (ii) a
limited live trial on a subset of routes, (iii) monitoring of actual versus predicted ride
times and costs, and (iv) a go/no-go review before full deployment.

### 7.5 Uncertainty & robustness stance (planned)

Because the first model will be deterministic, validation will explicitly probe how
solutions degrade under perturbation; robustness (not just optimality on a nominal instance)
will be a key acceptance criterion.

---

## 8. Expected Result Interpretation

This section describes **how future outputs should be read**, not what they are.

### 8.1 Anticipated output artifacts (future)

- A specified model with documented variables, objectives, and constraints.
- Cost and ride-time summaries for representative (synthetic or real) districts.
- A **Pareto / trade-off view** of budget dollars versus ride-time fairness.
- A comparison of **chained vs. dedicated** service configurations.
- A school-board article explaining assumptions, trade-offs, and recommended decision
  levers.

### 8.2 How trade-offs should be interpreted

- There will likely be **no single "best" plan**; instead a frontier that trades cost
  against ride-time balance. Decision-makers will choose a point on that frontier according
  to policy priorities.
- Chained service will plausibly reduce fleet size/cost in sparse settings but may increase
  some students' ride times — the interpretation must weigh these explicitly.
- Fairness metrics will require a stated definition (max ride time vs. variance vs.
  group-gap); different definitions will favor different plans.

### 8.3 Guardrails for interpretation

- Findings will be **district-specific** until transferability is tested.
- Any recommendation will be conditioned on assumption validity and data quality.
- Results will be framed as decision support, not as automatic prescriptions.

---

## 9. Limitations and Improvements

### 9.1 Anticipated limitations

- **No supplied data** — realism depends on acquisition and synthetic generation.
- **Determinism** — day-to-day variability is not captured in the first model.
- **Aggregation** — student-to-stop aggregation introduces approximation error.
- **Scalability** — exact methods may not scale to large districts.
- **Fairness ambiguity** — the definition of "balanced" is policy-dependent.
- **Static modeling** — enrollment changes and long-term fleet planning are out of scope
  initially.

### 9.2 Planned improvements / extensions

- Stochastic and robust optimization for travel time and demand.
- Multi-depot and heterogeneous-fleet extensions.
- Special-needs transport and accessibility constraints.
- Time-dependent travel times (traffic/weather).
- Dynamic re-optimization (e.g., day-of disruptions).
- Richer equity modeling and stakeholder-weighted objectives.
- Integration with budget planning and multi-year fleet replacement analysis.
- Interactive decision-support tooling for the board.

### 9.3 Open questions to resolve during modeling

- Precise ride-time cap and whether it is per-trip or per-day.
- Whether drivers' duty time or vehicle availability is the binding resource.
- How much chaining is operationally acceptable to the district.
- Which fairness definition the board will prioritize.
- What level of stop aggregation the district will accept.

---

## Appendix A — Planned Modeling Workflow (summary)

1. **Understand** the problem and decompose into subproblems (SP1–SP8).
2. **Assume** and register assumptions with confidence and planned tests.
3. **Formalize** the model framework (candidate families, variables, objectives).
4. **Plan data** schema, preprocessing, features, and usage strategy.
5. **Implement** modules M1–M9 and select algorithms.
6. **Validate** via metrics, benchmarks, scenarios, sensitivity, and pilot design.
7. **Interpret** trade-offs and translate into board-facing recommendations.

## Appendix B — Compliance with Task Restrictions

- This document contains **no computed results**, **no data analysis**, **no fitted
  models**, **no executed code/experiments**, and **no generated plots**.
- It contains **no final conclusions**; all content is future-oriented planning.
- Its purpose is to serve as a **roadmap** for a later, separate modeling and solving phase.
