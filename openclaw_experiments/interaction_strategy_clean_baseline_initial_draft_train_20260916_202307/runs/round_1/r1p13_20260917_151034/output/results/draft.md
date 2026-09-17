# Modeling Blueprint Draft — The Airplane Seating Problem (MCM 2007, `2007_The_Airplane_Seating`)

> **Status: PLANNING DRAFT (initial).** This document is a *roadmap for future modeling work only*.
> It intentionally contains no computations, no fitted parameters, no executed experiments, and no final
> conclusions. All statements are written in future/conditional tense and describe what *will* be done,
> compared, and validated in later rounds.

---

## 1. Problem Background and Restatement

Airlines may board and deboard passengers in essentially any order they choose. Current common practice
is roughly: passengers with special needs first, then first-class passengers (seated at the front of the
cabin), then coach and business-class passengers boarded in row-blocks that begin at the rear of the
cabin and sweep forward. Because an aircraft only earns revenue while it is in motion, long boarding and
deboarding times directly reduce the number of turns (flights) an aircraft can complete per day. The
advent of very large aircraft (e.g., the Airbus A380 with up to ~800 passengers) will amplify this
problem, making efficient boarding/deboarding procedures increasingly valuable to airlines.

The task will be to **devise and compare boarding and deboarding procedures** across three passenger-scale
regimes:

- **Small aircraft:** ~85–210 passengers
- **Midsize aircraft:** ~210–330 passengers
- **Large aircraft:** ~450–800 passengers

The work will culminate in an **executive summary (≤ 2 single-spaced pages)** written for airline
executives, gate agents, and flight crews, in addition to the standard contest-format technical report.
A referenced NY Times article (Nov 14, 2006) will inform the framing of current practice and the
perceived importance of improved solutions.

**Framing for the plan.** The problem will be treated as a *stochastic service-system / scheduling*
problem whose central quantity is the total boarding (and separately, deboarding) time or, more
operationally, the *seat-interference delay* induced by passenger interactions inside a constrained,
single- or twin-aisle cabin geometry.

---

## 2. Objectives and Subproblems

### 2.1 Overarching objective (to be pursued later)
To construct a comparative, mechanism-based framework that will predict and rank candidate boarding and
deboarding procedures with respect to total turn time, robustness (variability), passenger waiting
experience, and implementation feasibility, across the three aircraft-size classes.

### 2.2 Subproblems to be decomposed
- **SP1 — Geometry & capacity abstraction.** How will the cabin be parameterized (rows, columns,
  aisle(s), seat pitch, overhead-bin/stowage layout, galley/lavatory obstructions) so the same engine
  can represent small, midsize, and large aircraft?
- **SP2 — Boarding procedure taxonomy.** Which procedures will be enumerated and compared (see §5.3)?
- **SP3 — Boarding-time model.** Which mechanistic model will map a procedure + passenger/aircraft
  parameters to a distribution of total boarding time?
- **SP4 — Deboarding model.** How will deboarding be modeled (reverse-flow interference, aisle
  occupancy, carry-on removal, mixed rows), and can it share the same engine as boarding?
- **SP5 — Interaction/blocking dynamics.** How will aisle congestion, seat-row interference, and
  stowage contention be represented as dynamic delay mechanisms?
- **SP6 — Optimization/selection.** Given the model, how will procedures (or procedure variants, e.g.,
  block orderings, window-middle-aisle sequencing) be tuned and ranked?
- **SP7 — Multi-criteria trade-off.** How will time-optimal procedures be balanced against passenger
  fairness/waiting, special-needs compliance, safety, and gate-agent operability?
- **SP8 — Scaling study.** How will conclusions be extended/checked as passenger count and cabin
  dimensions grow from small to large regimes?
- **SP9 — Communication.** How will findings be translated into an executive summary suitable for a
  non-technical stakeholder audience?

### 2.3 Deliverables (planned)
- A formalized model specification and parameter table.
- A simulation/analytical evaluation harness (designed in later rounds, not executed here).
- A comparative procedure matrix across the three size classes.
- Sensitivity/robustness report.
- The two-page executive summary (later round).

---

## 3. Assumptions

The following assumptions will be adopted as *working hypotheses*, each to be revisited during validation.

### 3.1 Structural / geometric assumptions
- **A1.** The cabin will be idealized as a rectangular grid of rows × columns with one or two aisles;
  seat pitch and aisle width will be treated as tunable parameters rather than aircraft-specific values.
- **A2.** All seats will be assumed occupied (full flight) unless a load-factor parameter is later
  introduced to study under-booked flights.
- **A3.** Passengers will be assigned (or will self-select) seats according to the procedure under study;
  seat assignment is not left fully random unless that is itself the procedure being tested.

### 3.2 Behavioral assumptions
- **A4.** Each passenger will be modeled as an agent with a small set of attributes (walking speed,
  carry-on count/size, mobility, group size, stowage time) drawn from a *postulated* distribution.
- **A5.** Passengers will follow the prescribed boarding order; deviations/non-compliance will be
  introduced later only as a robustness perturbation.
- **A6.** Stowing carry-on luggage in overhead bins will be the dominant individual-service-time
  component and the primary source of aisle blockage.
- **A7.** Window/middle/aisle seat interference will be modeled explicitly: an aisle-seated passenger
  will be assumed to block the row until row-mates are seated when boarding in arbitrary order.

### 3.3 Modeling / operational assumptions
- **A8.** The aircraft will be assumed ready for boarding at t=0 (no cleaning/fueling delay in scope).
- **A9.** Boarding and deboarding will initially be analyzed independently; a later extension will
  couple them into a single turn-time model.
- **A10.** Time will be measured in seconds; the primary output is expected total boarding duration.
- **A11.** Safety/regulatory constraints (e.g., priority for passengers with special needs) will be
  treated as hard feasibility constraints, not soft penalties.

### 3.4 Justification (to be elaborated)
- These assumptions will aim to capture the *mechanisms* (aisle congestion, row interference, stowage)
  known from prior literature to dominate boarding time, while keeping the model tractable enough for
  rapid comparison across many procedures and aircraft sizes.

### 3.5 Future validation approach for assumptions
- Each assumption will be classified as **structural** (needed to define the model) or **empirical**
  (could be measured). Empirical assumptions will be targeted for literature calibration and, where
  possible, sensitivity sweeps; structural assumptions will be stress-tested by comparing model
  families (§5).

---

## 4. Data Processing Plan

> **Note on data availability.** The `data/` directory currently contains **no problem-provided
> dataset**; consistent with the MCM structure, this is a *modeling* problem. The plan below therefore
> treats "data" as (a) parameters to be elicited from published sources, and (b) synthetic agent
> populations to be generated by the model itself in later rounds. No data will be analyzed in this
> draft.

### 4.1 Data sources to be assembled (later rounds)
- **D1 — Aircraft geometry references.** Public seat maps and cabin dimensions for representative
  small, midsize, and large aircraft, to be used only for parameter ranges.
- **D2 — Behavioral/service-time literature.** Published values or ranges for walking speed, stowage
  time, and interference time in airline boarding studies.
- **D3 — Operational references.** The referenced NY Times (Nov 14, 2006) article and comparable
  industry reporting, to be used to characterize current practice and stakeholder priorities.
- **D4 — Synthetic agent populations.** Passenger attribute vectors generated from postulated
  distributions for Monte-Carlo evaluation.

### 4.2 Preprocessing plan
- Normalize/standardize aircraft geometry into a common *canonical cabin schema* (rows, columns, aisle
  positions, bin capacity per row).
- Convert all literature values into a consistent unit system (seconds, meters, passengers).
- Record every parameter with a **source tag** and an **uncertainty range** (min / nominal / max) so
  that uncertainty propagates into sensitivity analysis later.

### 4.3 Feature construction (model inputs)
- Cabin descriptors: rows, seats per row, aisle count/width, bin capacity, obstructions.
- Passenger descriptors: seat row/column, group size, walking speed, carry-on count, mobility flag.
- Procedure descriptors: boarding group definition, group ordering rule, interleaving rules,
  pre-boarding rules.

### 4.4 Data usage strategy
- **No train/test split** is anticipated because fitting to empirical boarding data is not assumed
  available; instead, the plan will use *scenario design* (a factorial grid of aircraft sizes ×
  procedures × behavioral regimes) and *Monte-Carlo replication* for stochastic runs.
- If empirical boarding-time data becomes available later, it will be reserved for **external
  validation** rather than for fitting the mechanistic model.

---

## 5. Candidate Model Framework

### 5.1 Modeling philosophy
Two complementary model families will be compared: a **fast analytical/queueing abstraction** for
breadth of procedure comparison, and a **detailed agent-based simulation (ABM)** for fidelity and
mechanism checking. A third, **optimization/metaheuristic** layer will search the procedure design space.

### 5.2 Candidate models
- **M1 — Queueing / flow-network approximation.** Treat the aisle as a service channel and boarding as
  a multi-stage flow; estimate throughput-limited boarding time analytically. *Advantages:* fast, closed-
  form insight, easy sensitivity analysis. *Limitations:* coarse treatment of row interference.
- **M2 — Probabilistic delay / interference model.** Model boarding time as the sum of walking time,
  seat-row interference time, and stowage time, with interference modeled per seat-conflict. *Advantages:*
  captures the dominant mechanism with interpretable terms. *Limitations:* requires distributional
  assumptions.
- **M3 — Agent-based discrete-event simulation.** Each passenger/row is an agent in a discretized cabin;
  delays emerge from explicit movement/competition rules. *Advantages:* high fidelity, tests emergent
  congestion. *Limitations:* computationally heavier, more parameters.
- **M4 — Optimization / metaheuristic layer.** Over procedure variants (block sizes, orderings, W-M-A
  sequencing), search for time-minimizing or multi-objective-optimal designs using M1–M3 as evaluators.
  *Advantages:* turns comparison into optimization. *Limitations:* dependent on evaluator fidelity.
- **M5 — Deboarding counterpart model.** A reverse-flow variant of M1–M3 with aisle-emptying dynamics.
  *Advantages:* completes the turn-time picture. *Limitations:* different interference structure than
  boarding.

**Likely backbone:** M3 (ABM) as the evaluation engine, with M1/M2 as analytical sanity checks, and M4
layered on top; M5 as a parallel engine.

### 5.3 Procedures to be enumerated (taxonomy under design)
- Back-to-front row blocks (current customary practice; baseline).
- Front-to-back and outside-in / window-middle-aisle (WMA) sequencing.
- Randomized / unassigned seating.
- Seat-number / seat-type interleaving schemes.
- Group-based boarding (families/groups together) and its variants.
- Hybrid/adaptive schemes depending on load factor or aircraft class.
- Deboarding orderings: row-front-to-back, row-back-to-front, group release, and aisle-aware release.

### 5.4 Key variables (symbolic, to be defined later)
- **Decision variables:** group definition, group order, sequence rule, pre-boarding rules.
- **State variables:** aisle occupancy, row-completion state, bin occupancy, passenger position.
- **Parameters:** cabin geometry, passenger attribute distributions, walking speed, stowage duration.
- **Outputs:** total boarding time, time-to-last-seat, variability, individual wait times.

### 5.5 Mathematical ideas to be used
- Queueing/network flow and Little's law for throughput bounds.
- Order statistics / probabilistic conflict counting for interference estimates.
- Discrete-event simulation semantics (event calendars, resource contention, blocking).
- Multi-objective optimization and Pareto-frontier analysis for time vs. fairness trade-offs.
- Scaling/dimensional analysis to compare procedures as passenger count grows.

### 5.6 Advantages and limitations (framework level)
- The **multi-model strategy** will provide both speed (M1/M2) and fidelity (M3), with cross-checks that
  reduce the risk of over-trusting a single abstraction. Limitations will include sensitivity to
  behavioral assumptions and the difficulty of validating against scarce public data.

---

## 6. Implementation Roadmap

### 6.1 Algorithmic components (to be built later)
1. **Cabin geometry builder** — generates canonical layouts for each size class.
2. **Passenger population generator** — samples agent attributes from parameterized distributions.
3. **Procedure compiler** — converts a procedure description into an ordered boarding schedule.
4. **Interference/blocking engine** — core dynamics shared by boarding and deboarding.
5. **Simulation driver / Monte-Carlo harness** — runs replications and aggregates distributions.
6. **Analytical evaluators** — M1/M2 closed-form estimators for cross-checking.
7. **Optimization driver** — metaheuristic search over procedure design space.
8. **Reporting/visualization module** — comparative tables, distributions, and Pareto plots.
9. **Sensitivity-analysis module** — parameter sweeps and global sensitivity ranking.

### 6.2 Workflow (planned sequencing)
1. Formalize cabin schema and parameter table.
2. Implement and unit-test the interference engine against simple hand-checkable scenarios.
3. Implement boarding procedures and the Monte-Carlo driver.
4. Cross-check ABM against analytical estimates on limiting cases.
5. Extend to deboarding.
6. Add optimization and multi-objective search.
7. Run the scenario grid across the three size classes.
8. Produce technical report and the ≤2-page executive summary.

### 6.3 Required modules / artifacts (planned)
- `code/` — geometry, agents, simulator, evaluators, optimizer, sensitivity.
- `data/` — parameter tables (literature-sourced) and generated scenario definitions.
- `results/` — model outputs (later rounds), plus this planning draft.
- `logs/` — run logs/configuration snapshots for reproducibility.

### 6.4 Reproducibility plan
- All scenarios will be fully specified by parameter/config files.
- Random seeds will be fixed and recorded for every reported run.
- Intermediate artifacts will be versioned so procedures can be re-evaluated consistently.

---

## 7. Validation Strategy

### 7.1 Evaluation metrics
- **Primary:** total boarding time distribution (mean, median, tail percentiles).
- **Secondary:** deboarding time; total turn time (board + deboard + turnaround).
- **Robustness:** variance / 95th-percentile under perturbed behavior and non-compliance.
- **Experience:** individual passenger waiting-time distribution and equity across seat types.
- **Feasibility:** operational complexity score for gate agents/crew.

### 7.2 Validation methods
- **Analytical cross-validation:** compare ABM results against M1/M2 in limiting regimes.
- **Internal consistency:** conservation checks (all passengers seated), monotonicity checks with
  passenger count, boundary tests.
- **Literature benchmarking:** compare model-implied relative rankings of known procedures against
  published findings/ranges (no fitting to unavailable data).
- **External validation (conditional):** should empirical boarding-time data become available, compare
  predicted vs. observed boarding times as a held-out test.

### 7.3 Sensitivity and robustness analysis
- One-at-a-time sweeps of geometry, walking speed, stowage time, group size, and non-compliance rate.
- Global sensitivity (e.g., variance-based or regression-based ranking) to identify dominant parameters.
- Scenario/robustness analysis across the small/midsize/large grid and across load factors.
- Adversarial/edge cases (worst-case carry-on load, extreme group sizes, blocked aisle).

### 7.4 Threats to validity (to be documented)
- Behavioral parameter uncertainty; idealized geometry; single-station boarding assumption; independence
  of boarding and deboarding in the baseline model.

---

## 8. Expected Result Interpretation

This section describes only how results *will be interpreted* in later rounds; no results are produced here.

- **Comparative rankings.** Procedures will be ranked by total boarding time and by robustness; it is
  anticipated (subject to confirmation) that interference-reducing sequences will tend to outperform
  naive back-to-front blocking, with the magnitude of the advantage depending on aircraft size and
  behavioral regime — this expectation will be explicitly tested rather than assumed.
- **Size dependence.** The relative benefit of a procedure may change with cabin size; scaling curves
  will be used to indicate where a procedure transitions from beneficial to marginal.
- **Trade-off interpretation.** Time-optimal procedures may impose higher passenger wait or operational
  complexity; the multi-objective frontier will be interpreted to recommend procedures based on the
  airline's weighting of time vs. experience vs. simplicity.
- **Robustness interpretation.** Procedures whose advantage persists under behavioral perturbation
  will be preferred over procedures that win only in idealized conditions.
- **Stakeholder translation.** Findings will be distilled (later) into actionable recommendations for
  executives (turn-time economics), gate agents (operability), and flight crews (safety/compliance).

---

## 9. Limitations and Improvements

### 9.1 Anticipated limitations
- Heavy reliance on assumed behavioral distributions rather than measured boarding data.
- Idealized cabin geometry may omit real obstructions (galleys, lavatories, exits) and multi-door boarding.
- Independent treatment of boarding and deboarding in the baseline may understate interaction effects.
- Optimization may overfit to the chosen evaluator model (model-induced bias).
- Special-needs and safety constraints add combinatorial complexity that simplified models may miss.

### 9.2 Planned improvements / extensions
- Introduce load-factor and multi-door/multi-aisle boarding.
- Add group/family-aware and non-compliance-aware boarding variants.
- Calibrate key behavioral parameters if/when empirical data becomes available.
- Couple boarding and deboarding into a unified turn-time optimization.
- Expand to uncertainty quantification and formal robust-optimization formulations.
- Add a cost/economic layer translating time savings into daily-turn and revenue impacts for the
  executive summary.

---

### Verification Checklist (self-audit for this draft)
- [x] `results/draft.md` created.
- [x] Contains only planning content (workflow, assumptions, candidate methods, data plan,
      implementation plan, validation strategy).
- [x] No problem solving, data analysis, calculations, model fitting, code execution, experiments,
      plots, or final conclusions included.
- [x] All statements written in future/conditional/planning tense.
