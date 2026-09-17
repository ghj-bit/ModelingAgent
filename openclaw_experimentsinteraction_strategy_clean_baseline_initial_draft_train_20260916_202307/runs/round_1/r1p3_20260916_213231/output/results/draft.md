# Modeling Blueprint Draft — Skyscraper Evacuation (HiMCM 2001, Problem 2001_Skyscrapers)

> **Status: Planning document only.** This draft contains no computed results, no data analysis, and no final conclusions. All statements are forward-looking design intentions to be executed in a later modeling phase.

---

## 1. Problem Background and Restatement

Skyscrapers differ widely in height, floor area, occupancy rate, and usage (office, residential, mixed-use). In a catastrophe — whether human-induced or natural (earthquake, tornado, hurricane, fire, or other emergency) — building height can severely impede escape.

The scenario to be modeled is:

- A single high-rise building must be fully evacuated.
- Electrical power has been lost, so **elevator banks are inoperative for ordinary occupants**; they may only be used by firefighters and rescue personnel holding special keys.
- A mathematical model is to be constructed such that the building can be **cleared within X minutes**.
- The model should then be used to **state the building height, the maximum occupancy, and the type of evacuation methods** that are consistent with each clearance target.
- The model is to be applied for **X = 15, 30, and 60 minutes**.

The restatement reframes the task as: given a clearance time budget, determine the triple *(height, maximum occupancy, evacuation method mix)* that satisfies the budget, and conversely, for a given building, determine whether the budget can be met. This is fundamentally a **capacity / throughput feasibility problem** with stochastic congestion and vertical-transport dynamics.

---

## 2. Objectives and Subproblems

**Primary objective (to be pursued later):**
Produce a defensible mathematical model that links building geometry, occupant load, evacuation method mix, and emergency dynamics to a total clearance time, and that can be inverted to answer the three X-minute cases.

**Subproblems to be framed:**

1. **Vertical transport subproblem** — characterize how occupants move down stairs (and up/out via other means) as a function of stair width, number of stairs, travel speed, density, and counterflow of rescue personnel.
2. **Capacity subproblem** — model the flow rate through bottlenecks (stairwell doors, landings, exit widths, assembly points) and identify limiting elements.
3. **Method-mix subproblem** — compare evacuation methods: protected stairways, firefighter-operated elevators (per special-key protocol), rooftop rescue, helicopter rescue, external escape, and shelter/defend-in-place as complements.
4. **Occupancy subproblem** — relate floor area, floor count, and usage type to code-based occupant load, and determine the maximum occupancy compatible with a clearance budget.
5. **Inversion subproblem** — given X, solve for feasible *(height, occupancy, method mix)*; identify the feasible region and trade-off frontier.
6. **Uncertainty subproblem** — propagate variability (occupant response, mobility impairment, congestion, rescue timing) into clearance-time distributions rather than point estimates.
7. **Trade-off / policy subproblem** — express the cost-complexity of methods (more elevators for rescue, more stair capacity, training) against clearance-time benefit.

**Deliverables (later phase):**
- A documented model with stated assumptions and variables.
- A computational procedure (e.g., simulation and/or flow-network optimization) to evaluate clearance time.
- Scenario outputs for X = 15, 30, 60 minutes stated as feasibility statements (not yet computed here).
- Sensitivity and robustness discussion.

---

## 3. Assumptions

The following are candidate assumptions to adopt, each with a justification and a planned validation path. Numerical values will be assigned in the later modeling phase from cited sources, not in this draft.

**A. Building and geometry**
- A1. *Rectangular floor plates with uniform or near-uniform usable area per floor.* Justification: standard high-rise layout; simplifies stair travel distance. Validation: laxer setting with varying plate sizes in sensitivity analysis.
- A2. *Discrete floor model with identical inter-floor rise.* Justification: tracks vertical distance deterministically. Validation: compare against continuous height model.
- A3. *Occupant load density per usage type is derived from building-code standards (to be cited later).* Justification: gives defensible maximum occupation. Validation: cross-check against occupancy-rate data ranges.

**B. Occupant behavior**
- B1. *Occupants begin evacuation after a detection/notification delay, then move with a specified unimpeded speed.* Justification: separates pre-movement from movement, standard in evacuation modeling. Validation: sensitivity to delay and speed distributions.
- B2. *A fraction of occupants have reduced mobility (injured, elderly, disabled) and require assistance.* Justification: realistic catastrophes produce casualties. Validation: vary fraction across scenarios.
- B3. *Occupants act cooperatively (no counterflow sabotage, queue discipline at stairs).* Justification: baseline tractable case. Validation: relax with non-cooperative/panic behavior.

**C. System and emergency**
- C1. *Elevators are unavailable to ordinary occupants; rescue personnel may use them under special-key operation.* Justification: stated scenario. Validation: model a controlled assistance fleet with capacity per trip.
- C2. *Fire/rescue personnel enter the stairwells and may cause counterflow congestion.* Justification: realistic for firefighting operations. Validation: vary personnel counts and entry timing.
- C3. *Exits at grade have finite width and a finite number of egress paths.* Justification: bottleneck realism. Validation: vary exit width and count.

**D. Modeling scope**
- D1. *Clearance is measured as time until the last occupant reaches a safe assembly area.* Justification: matches "clear the building." Validation: alternative metric = time until 95% cleared.
- D2. *No structural collapse during the evacuation window (baseline).* Justification: isolate evacuation dynamics from structural failure. Validation: add a hazard-timing variant.
- D3. *Deterministic baseline with stochastic sensitivity layer.* Justification: yields interpretable first results plus robustness. Validation: Monte Carlo comparison.

**Assumption ledger:** each assumption will be tagged as *critical* or *non-critical* in the later phase, and the model will be re-run with critical assumptions relaxed.

---

## 4. Data Processing Plan

No dataset is bundled with this problem; the model is primarily analytical/simulation-based. The "data" plan therefore focuses on **parameter sourcing, scenario generation, and provenance**, not on cleaning an existing table.

**4.1 Parameter sourcing (external references to be collected later)**
- Building-code occupant-load factors by usage type (office, residential, assembly, mixed-use).
- Stairway and exit-width capacity values from life-safety standards.
- Unimpeded walking speeds and pre-movement delays from evacuation literature.
- Elevator capacity and cycle times for firefighter operation.
- Empirical high-rise evacuation drill timings for calibration reference.

**4.2 Preprocessing plan (for any collected tabular data)**
- Normalize units to SI; record conversion provenance.
- Validate ranges and flag physically implausible values.
- Standardize usage categories into a controlled vocabulary.
- Preserve a data dictionary recording each parameter, its unit, source, and uncertainty range.

**4.3 Feature / scenario construction**
- Construct synthetic buildings on a grid of *(height, floors, floor area, usage, stair capacity, exit width, elevator assistance capacity)*.
- Construct occupant profiles: total load, mobility-impaired fraction, arrival distribution per floor.
- Construct emergency profiles: notification delay, personnel count and entry schedule, hazard timing.

**4.4 Data usage strategy**
- Use literature values as *nominal* parameters and encode uncertainty ranges.
- Reserve a subset of published drill cases as **calibration/validation** references, kept separate from scenario generation.
- Document all sources so results remain reproducible and auditable.

---

## 5. Candidate Model Framework

Several candidate models will be considered, then combined as appropriate. No model is fitted or evaluated in this draft.

**5.1 Model families**

- **M1 — Deterministic flow / hydraulic (network) model.** Treat occupants as a continuum flowing through nodes (floors, stairs, doors, exits) with capacity limits. *Variables:* flow rates, densities, widths, travel distances, clearance time. *Ideas:* conservation of flow, bottleneck/queueing at nodes, min-cut capacity. *Advantages:* transparent, fast, invertible for X. *Limitations:* ignores individual stochasticity and behavior.

- **M2 — Queueing / network-queue model.** Represent stairwells, landings, and exits as service stations with service rates. *Variables:* arrival rates, service rates, queue lengths, waiting times. *Ideas:* per-floor arrival processes, tandem queues, bottleneck identification. *Advantages:* gives waiting-time distributions. *Limitations:* simplifying distributional assumptions.

- **M3 — Agent-based simulation (ABM).** Model each occupant (or cohorts) with speed, mobility, and behavior; simulate movement on stairs and corridors. *Variables:* individual positions, speeds, interactions. *Ideas:* cellular/continuous space, congestion-dependent speed. *Advantages:* captures heterogeneity and counterflow. *Limitations:* computationally heavier; needs calibration.

- **M4 — Coupled flow + elevator-assistance model.** Combine M1/M2 with a discrete elevator fleet used by rescue personnel to move mobility-impaired occupants. *Variables:* number of elevators, trip capacity, cycle time, staging. *Ideas:* scheduling/flows of assisted trips competing for stair capacity. *Advantages:* addresses the special-key protocol directly. *Limitations:* scheduling assumptions.

- **M5 — Optimization / inverse model.** Formulate clearance time as an objective or constraint to invert for *(height, max occupancy, method mix)*. *Variables:* decision variables for geometry, capacity, and method allocation. *Ideas:* feasibility region, Pareto frontier of clearance time vs. capacity/complexity. *Advantages:* answers the X = 15/30/60 questions directly. *Limitations:* depends on fidelity of underlying dynamic model.

- **M6 — Stochastic / uncertainty layer.** Wrap M1–M5 in Monte Carlo sampling over key uncertain parameters. *Variables:* random speeds, delays, mobility fractions, personnel timing. *Ideas:* clearance-time distributions and exceedance probabilities. *Advantages:* robustness statements. *Limitations:* computational cost.

**5.2 Illustrative (not computed) mathematical ideas**
- Occupant flow as `flow = density × speed × effective width` with congestion-limited speed.
- Stairwell throughput as a bottleneck: total clearance ≈ (occupants routed through the critical stair/exit) / (capacity of that element) plus traversal time.
- Elevator-assisted trips as `trips × capacity` per cycle time, scheduled to serve mobility-impaired occupants.
- Feasibility formulation: clearance time `T(height, N, method mix) ≤ X`.

**5.3 Recommended direction (to be tested in the later phase)**
Use M1/M2 as the interpretable backbone, validate against M3 (ABM), incorporate M4 for rescue/elevator assistance, and use M5–M6 to produce the X-minute feasibility statements and robustness bands.

---

## 6. Implementation Roadmap

A staged plan; no code will be written in this draft phase.

**Stage 0 — Setup (later).**
- Finalize variable dictionary, units, and assumption ledger.
- Collect and cite parameter sources; build the data dictionary.

**Stage 1 — Baseline deterministic model.**
- Implement the flow/network backbone (M1/M2) for a single building configuration.
- Verify conservation of occupants and bottleneck behavior on trivial cases.

**Stage 2 — Method-mix extension.**
- Add elevator-assisted rescue and alternative evacuation methods (M4).
- Model counterflow of rescue personnel.

**Stage 3 — Stochastic layer.**
- Add Monte Carlo sampling over uncertainty ranges (M6); produce clearance-time distributions.

**Stage 4 — Inversion and scenarios.**
- Implement the optimization/feasibility formulation (M5).
- Generate feasibility statements for X = 15, 30, and 60 minutes across building archetypes.

**Stage 5 — Sensitivity and reporting.**
- Run sensitivity/robustness studies; assemble narrative, tables, and (later) figures.

**Required modules (planned):**
- `params` — parameter registry with sources and uncertainty.
- `building` — geometry and occupancy generator.
- `flow_model` — deterministic network/queue dynamics.
- `elevator_model` — assisted-evacuation scheduler.
- `agent_model` — optional ABM cross-check.
- `inversion` — feasibility/Pareto optimization.
- `uncertainty` — Monte Carlo driver.
- `reporting` — scenario tables and interpretation helpers.

**Quality controls:** unit tests for conservation and monotonicity, reproducible seeds, and a config-driven scenario runner.

---

## 7. Validation Strategy

**7.1 Evaluation metrics (planned)**
- Total clearance time (last occupant out) and time-to-X% cleared.
- Bottleneck utilization and queue-length statistics.
- Feasibility indicators for each X target (meets / does not meet budget).
- Method-mix contribution shares to total clearance.
- Uncertainty metrics: percentiles, exceedance probability, sensitivity indices.

**7.2 Validation methods**
- **Internal consistency:** conservation of occupants; monotonicity (more capacity → shorter clearance); limiting-case checks (e.g., zero occupants, single floor).
- **Cross-model agreement:** compare deterministic flow/queue results against ABM (M3) on shared scenarios.
- **External benchmarking:** compare against published high-rise evacuation drill timings and code-based capacity expectations.
- **Assumption stress tests:** relax each critical assumption and quantify the effect on clearance time.
- **Inversion check:** confirm that model-generated feasible points, when re-evaluated forward, satisfy the X budget.

**7.3 Sensitivity and uncertainty analysis**
- One-at-a-time sweeps over stair width, stair count, exit width, occupancy, mobility-impaired fraction, notification delay, personnel count, elevator assistance capacity.
- Global sensitivity (variance-based / screening) to rank influential parameters.
- Scenario families: best case / nominal / worst case / hazard-with-timing.
- Report clearance time as distributions, not single numbers, with clearly stated uncertainty sources.

---

## 8. Expected Result Interpretation

This section describes how results will be *read* once computed; no results are produced here.

- **Feasibility statements per X.** For each of X = 15, 30, and 60 minutes, the model should yield a feasible region of *(height, maximum occupancy, method mix)* and, where useful, the limiting (binding) constraint.
- **Binding-bottleneck narrative.** The interpretation should identify whether stairs, exits, elevator-assistance capacity, or occupant response time dominates the clearance budget, and how that changes with X and building type.
- **Method-mix guidance.** Expected trade-offs: longer budgets permit taller/higher-occupancy buildings with conventional protected stairs; tighter budgets will require larger stair/exit capacity and/or assisted/elevator-supported evacuation, with corresponding design and operational complexity.
- **Height–occupancy trade surface.** Results should be expressed as a frontier (or set of contours) rather than a single point, so that building designers/authorities can trade height against occupancy and method mix.
- **Robustness framing.** For each X, results should be accompanied by uncertainty bands and the probability of exceeding the budget under adverse but plausible conditions.
- **Scope caveat.** All interpretations will be conditional on stated assumptions; alternative hazard sequences (e.g., structural degradation) will be treated as scenario extensions.

---

## 9. Limitations and Improvements

**Anticipated limitations**
- Deterministic backbone may understate congestion non-linearities and panic/counterflow effects.
- Behavioral parameters (delay, speed, cooperation) are uncertain and context-dependent.
- Elevator-assisted evacuation scheduling is idealized; real operations involve coordination delays.
- Single-building framing may not generalize to connected/complex multi-tower structures.
- Clearance-time metric (last person out) is sensitive to rare slow occupants.

**Planned improvements**
- Enrich the behavioral layer with more realistic pre-movement distributions and heterogeneous speeds.
- Add hazard-coupling (smoke/fire/structural timing) to study evacuation under evolving threat.
- Include defend-in-place and phased evacuation as alternatives to full immediate evacuation.
- Extend to multi-building/campus and to network-of-exits optimization.
- Improve calibration using real drill data and, if available, expert elicitation.
- Add formal optimization for method allocation and robustness (e.g., min worst-case clearance).

**Open questions to resolve in the later phase**
- What is the most defensible occupant-load and stair/exit-capacity basis for citation?
- How should mobility-impaired occupants be prioritized within the elevator-assistance schedule?
- Which metric (last-out vs. 95%-cleared) best matches the problem's intent?
- How much model complexity is warranted before results become unverifiable?

---

*End of planning draft. No computations, data analysis, experiments, or final results are contained in this document; all content is a forward-looking blueprint for the subsequent modeling phase.*
