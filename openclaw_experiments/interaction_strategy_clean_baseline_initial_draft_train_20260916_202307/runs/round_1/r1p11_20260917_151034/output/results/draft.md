# Modeling Blueprint Draft
## Wheelchair Access at Airports — Consultant Bid Modeling Plan

**Problem ID:** 2006_Wheel_Chair_Access
**Source:** MCM 2006 (Epsilon Airlines consultant bid)
**Document type:** Initial modeling plan draft (blueprint only — no results, no solving)

> This document is a *roadmap for future modeling work*. It intentionally contains no computations, no data analysis, no fitted models, and no conclusions. All statements are framed as planned actions, candidate approaches, and hypotheses to be validated later.

---

## 1. Problem Background and Restatement

### 1.1 Background
Air travel frequently involves multi-leg journeys in which passengers must transfer between flights at intermediate airports. For passengers with reduced mobility (PRM), these transfers can be difficult, and airlines mitigate the difficulty by providing wheelchairs and human escorts on request. Requests typically arrive with ample notice, but may also arrive at check-in or even immediately before landing. Epsilon Airlines faces a cost-minimization and service-quality trade-off in a space- and labor-constrained terminal environment.

### 1.2 Restatement (planning view)
The airline will eventually need a decision-support algorithm that, for any given airport topology and daily flight/passenger schedule, will:

- position wheelchair stock and escort staff,
- schedule the movement of wheelchairs and escorts among concourses/gates,
- respond to both pre-registered and last-minute assistance requests,
- and minimize a composite total cost while meeting an acceptable level of service.

The consultant bid must (a) demonstrate understanding of the problem, (b) propose a detailed algorithm, (c) demonstrate applicability across small, medium, and large airports under high and low traffic, (d) define and weight all relevant costs, and (e) project future costs/needs as the traveling population ages.

### 1.3 Why this is a planning problem
The core structure is a **dynamic, stochastic resource-repositioning and assignment problem on a spatial network with hard service constraints**. It will combine scheduling, inventory, routing, and queueing elements. This framing will drive the candidate model selection in Section 5.

---

## 2. Objectives and Subproblems

### 2.1 Primary objective
To design a modeling and algorithmic framework that will determine the **day-long, cost-minimal placement and movement of wheelchairs and escorts** while satisfying a target service level for passenger assistance.

### 2.2 Secondary objectives
- Define a **complete and transparent cost taxonomy** with defensible relative weights.
- Ensure the framework will **scale** across airport size (1, ≥2, ≥4 concourses) and demand intensity (high/low).
- Provide a **short-term and long-term budget projection** mechanism.
- Anticipate demographic-driven demand growth and recommend adaptation levers.

### 2.3 Subproblems (to be modeled)
1. **SP1 — Demand characterization:** model the arrival process of assistance requests (known-in-advance vs. check-in vs. pre-landing).
2. **SP2 — Space/time topology:** represent the airport as a graph of nodes (gates, concourses, storage, transfer points) with traversal times.
3. **SP3 — Resource inventory:** model wheelchair fleet size/condition/maintenance and escort headcount/shifts.
4. **SP4 — Movement/repositioning:** schedule proactive relocation of wheelchairs and escorts to match anticipated demand.
5. **SP5 — Assignment/serving:** match available wheelchair+escort to each request with routing and timing.
6. **SP6 — Service constraints:** bound passenger wait and, critically, avoid flight-holding/delay caused by late assistance.
7. **SP7 — Cost aggregation and weighting:** build a composite objective emphasizing delay-avoidance.
8. **SP8 — Scenario testing:** instantiate SP1–SP7 for the 3×2 airport/traffic matrix.
9. **SP9 — Future projection:** extend the model over a multi-year demand-population horizon.

### 2.4 Deliverables (planned)
A written bid document, a formal model specification, an algorithm description with pseudocode, a scenario-generation scheme, a validation protocol, and a cost/projection framework.

---

## 3. Assumptions

Each assumption is listed with its rationale and a planned future validation approach.

| # | Assumption | Justification | Planned validation |
|---|-----------|---------------|--------------------|
| A1 | The airport layout can be abstracted as a weighted, undirected graph of gates, concourses, storage points, and transfer corridors, with deterministic nominal travel times. | Simplifies routing while preserving the dominant cross-terminal travel cost. | Compare graph distances against published terminal maps / walk-time studies. |
| A2 | Assistance demand will be modeled as a stochastic point process per gate/time window, with three notice classes. | Captures the known/unknown request structure described in the problem. | Stress-test with synthetic high/low arrival rates; later calibrate to airline records. |
| A3 | Wheelchair service time (pickup → escort → delivery) will be a distribution rather than a constant. | Real service is variable due to distance and congestion. | Sensitivity over service-time variance. |
| A4 | Escorts will be treated as interchangeable, shift-scheduled resources with hourly cost; wheelchair pool will be treated as finite with wear/maintenance cost. | Matches stated cost drivers (labor, equipment wear, maintenance). | Vary fleet size to find cost-minimizing region. |
| A5 | Flight-holding/delay cost will dominate the objective and will be modeled as a nonlinear penalty in departure-delay minutes. | The problem explicitly flags flight-holding as the most troubling cost. | Test weighting sensitivity; compare linear vs. nonlinear penalty forms. |
| A6 | Storage capacity at each terminal region will be finite and expensive; violations incur "space" cost. | Problem states storage space is limited and costly. | Sweep capacity to observe cost trade-offs. |
| A7 | Left wheelchairs in high-traffic areas will incur a liability-risk cost term. | Explicitly mentioned as a liability. | Proxy cost parameter, tested via sensitivity. |
| A8 | Demand is statistically homogeneous across days within a traffic regime (high/low), enabling representative-day modeling. | Practical simplification for planning. | Compare representative-day vs. multi-day simulation in validation. |
| A9 | Future demand growth will be scenario-driven (population aging) rather than predicted precisely. | Uncertainty is high over multi-year horizons. | Build low/medium/high demographic scenarios. |

*Validation note:* All assumptions will be revisited after data provisioning; those with largest objective impact will be prioritized for empirical calibration.

---

## 4. Data Processing Plan

> No data analysis has been performed. The workspace `data/` directory is currently empty; the following describes the data that **will** be required, how it **will** be obtained/constructed, and how it **will** be prepared.

### 4.1 Data inventory to be assembled
- **Airport topology:** concourse/gate coordinates, corridor connectivity, nominal walking/traversal times, storage location capacities.
- **Flight schedule:** arrivals/departures per gate, aircraft type, scheduled and minimum connection times.
- **Assistance-request records (or synthetic generator):** request time, notice class, origin gate, destination gate, party size.
- **Resource parameters:** wheelchair purchase price, maintenance interval/cost, lifetime; escort hourly wage, shift rules, headcount limits.
- **Cost parameters:** cost of delay per minute, space cost per wheelchair-slot, liability proxy cost.
- **Demographic projection inputs:** aging-traveler share over future horizon.

### 4.2 Sourcing strategy
- Primary: parameterize from public aviation/accessibility literature and published terminal data where available.
- Secondary: construct a **synthetic scenario generator** producing reproducible schedules and request streams across the 3×2 test matrix.
- Tertiary: calibrate ranges later against real airline operational data if the bid is selected.

### 4.3 Preprocessing plan (future)
- Normalize time units to a common clock; align schedules to local time.
- Build the graph representation with travel-time edge weights.
- Discretize the operational day into planning epochs (candidate: 5–15 minute buckets).
- Clean/deduplicate request records; impute missing gate/notice fields with documented rules.
- Define consistent currency/unit conventions.

### 4.4 Feature construction (future)
- Per-gate, per-epoch demand intensity.
- Peak-window detection and congestion indicators.
- Travel-time matrix derived from the graph (shortest paths) for use as routing costs.
- Resource-utilization and idle-time features for the scheduler.

### 4.5 Data usage strategy
- Strict separation of **calibration inputs** vs. **scenario evaluation inputs**.
- All synthetic data generation will be seeded for reproducibility.
- A held-out set of high/low scenarios will be reserved for validation (Section 7).

---

## 5. Candidate Model Framework

### 5.1 Overall framing
A **multi-layer, hybrid** framework is anticipated, since no single classic model covers inventory, routing, scheduling, and stochastic demand simultaneously.

### 5.2 Candidate models (to be compared later)

**(a) Spatio-temporal resource-flow / inventory model**
- Treats wheelchairs and escorts as inventory parcels that will be repositioned across the graph.
- Variables: stock level per node per epoch; flow on each edge per epoch.
- Pros: naturally captures repositioning and storage. Cons: ignores fine-grained request sequencing.

**(b) Dynamic assignment / scheduling model**
- Assigns each request to a wheelchair+escort pair over time.
- Candidate formulations: time-expanded network flow; mixed-integer program; dispatching heuristic.
- Pros: directly optimizes service. Cons: combinatorial growth with request count.

**(c) Queueing model**
- Models gates/concourses as service stations where requests queue for resources.
- Used primarily to estimate waits and congestion, and to feed cost terms.
- Pros: analytic insight into service levels. Cons: simplifying distributional assumptions.

**(d) Stochastic optimization / robust optimization**
- Handles the three notice classes and demand uncertainty.
- Candidate: two-stage stochastic program (here-and-now positioning, wait-and-see assignment) or robust counterpart.
- Pros: aligns with uncertainty structure. Cons: computational cost; needs scenario reduction.

**(e) Rolling-horizon / model-predictive control**
- Re-solves the schedule each epoch with updated demand; excellent for late requests.
- Pros: real-time responsiveness. Cons: requires careful terminal conditions.

**(f) Agent-based / discrete-event simulation**
- Virtual escorts and wheelchairs act in a simulated terminal.
- Role: **evaluation testbed** for the algorithms above, especially scenario testing.
- Pros: high fidelity, intuitive for stakeholders. Cons: not itself an optimizer.

### 5.3 Proposed integrated architecture (candidate)
1. **Demand layer (SP1):** stochastic request generator + notice classification.
2. **Graph layer (SP2):** airport topology and travel-time matrix.
3. **Optimization layer (SP4–SP6):** rolling-horizon stochastic scheduling core combining (a)+(b)+(d).
4. **Cost layer (SP7):** composite objective with tunable weights.
5. **Evaluation layer (SP8):** discrete-event simulation (f).
6. **Projection layer (SP9):** scenario-driven scaling over time.

### 5.4 Key variables (preliminary)
- Decision: stock placement, repositioning flows, request-to-resource assignment, escort shift allocation.
- State: current resource locations, pending queues, time.
- Parameters: travel times, service-time distribution, arrival rates, cost coefficients, capacities.
- Objective terms: escort labor, wheelchair wear/maintenance, repositioning effort, storage space, liability proxy, flight-delay/holding penalty.

### 5.5 Advantages / limitations
- **Advantages:** coverage of all cost drivers; scenario scalability; explicit handling of last-minute requests; validation via simulation.
- **Limitations:** model complexity and runtime; parameter uncertainty; abstraction of human behavior; potential scenario-generation bias.

---

## 6. Implementation Roadmap

### 6.1 Planned algorithms
- **Scenario generator** for airports, schedules, and request streams (seeded).
- **Graph/shortest-path module** for travel-time matrices.
- **Rolling-horizon optimizer**: likely a MIP or a decomposition heuristic (e.g., column generation or Lagrangian relaxation) for large instances; greedy/priority dispatch for fast fallback.
- **Discrete-event simulator** for fidelity evaluation.
- **Cost-aggregation module** with configurable weight profiles.
- **Projection module** applying demographic scenarios to demand rates.

### 6.2 Workflow (stages)
1. Specify data schemas and scenario parameters.
2. Implement graph + scenario generator.
3. Prototype demand model and queueing estimates.
4. Implement optimization core (start with tractable MIP on small instances).
5. Wrap in rolling-horizon controller.
6. Build discrete-event simulator and connect for evaluation.
7. Instantiate the 3×2 airport/traffic test matrix.
8. Add cost-weighting calibration and sensitivity suite.
9. Add future-projection layer.
10. Produce bid document, pseudocode, and reproducibility package.

### 6.3 Required modules
`scenario_generator`, `airport_graph`, `demand_model`, `queue_estimator`, `optimizer_core`, `rolling_horizon_controller`, `simulator`, `cost_model`, `projection_model`, `experiment_runner`, `reporting`.

### 6.4 Test matrix (planned)
| | Small (1 concourse) | Medium (≥2) | Large (≥4) |
|---|---|---|---|
| Low traffic | scenario S-L | M-L | L-L |
| High traffic | scenario S-H | M-H | L-H |

Each scenario will be evaluated by the simulator under the same objective definition to permit fair comparison.

### 6.5 Reproducibility plan
- Fixed random seeds for all synthetic data.
- Versioned configuration files for every scenario.
- Scripted end-to-end run: generate → optimize → simulate → aggregate → report.

---

## 7. Validation Strategy

### 7.1 Evaluation metrics (planned)
- **Total composite cost** (primary), decomposed into cost categories.
- **Service metrics:** average/max passenger wait, percent of requests served within target window.
- **Operational metrics:** flight delays caused, total delay minutes, planes held.
- **Resource metrics:** wheelchair utilization, escort utilization/idle time, repositioning distance.
- **Robustness metrics:** cost variance across demand realizations.

### 7.2 Validation methods
- **Internal consistency:** verify optimizer output is executable in the simulator.
- **Benchmark comparison:** compare against naive baselines (e.g., static stock allocation, first-come-first-served dispatch).
- **Cross-model check:** compare MIP optimum on small instances against heuristic performance.
- **Scenario coverage:** run full 3×2 matrix and stress extremes.
- **Reproducibility:** re-run with fixed seeds to confirm stable results.
- **Expert review:** sanity-check cost definitions and service targets with domain reasoning.

### 7.3 Sensitivity analysis plan
- Vary cost weights (especially delay penalty) to map the cost landscape.
- Vary wheelchair fleet size and escort headcount to locate cost-minimizing regions.
- Vary service-time variance and arrival rates.
- Vary storage capacity and liability-cost assumptions.
- Vary notice-class mix (more last-minute requests).

### 7.4 Threats to validity (to monitor)
- Synthetic-data bias and parameter guesswork.
- Overfitting cost weights to a single regime.
- Simulation fidelity vs. real terminal behavior.

---

## 8. Expected Result Interpretation

> Interpretations are stated as *anticipated patterns to be examined*, not conclusions.

The future modeling effort is expected to reveal:

- A **cost trade-off curve** between resource abundance (more staff/chairs) and delay-avoidance, with an interior optimum.
- The likely **dominance of flight-delay costs** in the composite objective, implying that service-level constraints matter more than raw inventory savings.
- Differing optimal strategies by airport scale: small airports may favor simple dispatch, while large airports likely require proactive repositioning and stochastic planning.
- High-traffic regimes expected to demand more proactive stocking; low-traffic regimes may tolerate reactive dispatch.
- Demographic projections expected to increase required fleet/headcount, motivating forward-looking budget buffers and efficiency measures.

These will be framed as **findings to be confirmed or rejected** during validation, with explicit reporting of uncertainty.

---

## 9. Limitations and Improvements

### 9.1 Anticipated limitations
- Heavy reliance on assumed/parametrized data in the absence of real operational records.
- Computational tractability of the full stochastic formulation at large scale.
- Abstraction of escort behavior, wheelchair condition dynamics, and terminal congestion.
- Cost-weight subjectivity and the risk of mis-specification.
- Discrete-event simulation calibration uncertainty.

### 9.2 Planned improvements
- **Calibration pathway:** replace synthetic parameters with real data if available.
- **Decomposition techniques:** column generation / Benders / Lagrangian methods for scale.
- **Machine-learning demand forecasting:** learn arrival patterns instead of assuming distributions.
- **Robust/stochastic enhancements:** chance-constrained service guarantees for last-minute requests.
- **Human-factors layer:** model escort fatigue, shift equity, and training constraints.
- **Generalization:** expose topology and demand knobs so the framework will transfer to arbitrary airports, not just the test matrix.
- **Uncertainty quantification:** confidence bounds on cost projections for the long-term budget.

### 9.3 Open questions for the modeling phase
- How should flight-delay cost be penalized (linear, convex, or step-like) to reflect passenger churn?
- What target service level is "acceptable" and who sets it?
- How should wheelchairs be pooled vs. dedicated per concourse?
- Should escorts double as general staff during idle time?

---

## Appendix A — Planning Checklist (future execution)
- [ ] Finalize data schemas and scenario parameters
- [ ] Build graph + scenario generator
- [ ] Prototype demand/queue models
- [ ] Implement optimization core + rolling horizon
- [ ] Build simulator and integrate
- [ ] Instantiate 3×2 matrix
- [ ] Calibrate and sensitivity-test cost weights
- [ ] Add projection layer
- [ ] Produce bid report with pseudocode and reproducibility package

---

*End of blueprint draft. No solving, computation, experiment, or result is included by design.*
