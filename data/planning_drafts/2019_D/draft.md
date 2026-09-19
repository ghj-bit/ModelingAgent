# MM-Bench 2019_D — Initial Modeling Plan Draft

**Problem ID:** `2019_D`
**Title:** Louvre Emergency Evacuation Model (ICM 2019 Problem D)
**Document type:** Modeling blueprint draft (roadmap only — not a solution)

> **Scope note.** This document is a *plan for future modeling work*. It contains no data analysis, no computations, no fitted models, no code, and no final results or conclusions. All numerical references are to publicly known problem parameters used only to frame the design; none are used to derive answers here.

---

## 1. Problem Background and Restatement

The host problem concerns emergency evacuation planning for the Louvre Museum in Paris. The museum is one of the largest and most visited in the world, reported as receiving more than 8.1 million visitors in 2017, spread over five floors (two underground) with roughly 380,000 exhibits covering on the order of 72,735 square meters, and wings as long as 480 meters. Visitor volume varies by time of day and season, and the visiting population is highly diverse (multiple languages, groups, and disabled visitors), which complicates evacuation.

There are four main public entrances — the Pyramid (primary/most used), Passage Richelieu, Carrousel du Louvre, and Portes Des Lions — and an unknown set of additional exit points (service doors, employee entrances, VIP entrances, emergency exits, and historical/hidden passages) known only to emergency personnel and officials. The museum also has a public real-time waiting-time application ("Affluences") that could plausibly be repurposed for evacuation coordination.

The planning task is to design an *adaptable* evacuation model that:
- enables museum leaders to explore a range of evacuation options for visitors,
- allows emergency personnel to enter the building as quickly as possible,
- identifies bottlenecks that limit movement toward exits,
- accommodates a broad set of threat types that may alter or remove route segments,
- supports validation and a discussion of practical implementation at the Louvre,
- yields policy/procedural recommendations (including crowd management and control), and
- is transferable to other large, crowded structures.

**Restatement (planning framing):** The modeling effort should produce a decision-support framework whose inputs are (population distribution, building geometry/circulation network, exit/entrance configuration, and threat scenario) and whose outputs are (evacuation time estimates, route assignments, congestion/bottleneck diagnostics, and ingress pathways for responders). Because the provided dataset definition is empty (no staged data files), the framework will be designed to operate on parameters and structures assembled from public documentation, reasonable assumptions, and scenario definitions, and to remain reusable when real layout/occupancy data becomes available.

---

## 2. Objectives and Subproblems

### 2.1 Primary objectives
1. **O1 — Evacuation efficiency:** Provide a model that estimates and supports minimization of total (and per-zone) evacuation time for all occupants.
2. **O2 — Safety and congestion control:** Identify and characterize bottlenecks and high-density regions, and support crowd-management strategies that reduce crushing/congestion risk.
3. **O3 — Dual-flow capability (egress + responder ingress):** Represent and evaluate how simultaneous civilian egress and emergency-personnel ingress can coexist without mutual obstruction.
4. **O4 — Adaptability to threats:** Support scenario conditioning in which arbitrary nodes/edges (or whole routes/exits) can be degraded or removed.
5. **O5 — Implementation and policy guidance:** Translate model outputs into implementable procedures and recommendations, and demonstrate transferability to other crowded structures.

### 2.2 Subproblems
- **S1 — Space modeling:** Abstract the five-floor, multi-wing museum into a routable graph / network of corridors, stairs, elevators, lobbies, galleries, and exits, including capacity and flow-rate attributes.
- **S2 — Population modeling:** Represent occupant counts, spatial distribution, and behavioral heterogeneity (groups, mobility-impaired visitors, languages) as scenario inputs.
- **S3 — Route assignment / flow optimization:** Decide how occupants are allocated to exits and routes (system-optimal vs. user-equilibrium perspectives).
- **S4 — Congestion / bottleneck analysis:** Detect capacity-limiting segments and queue formation; evaluate flow-rate-based congestion models.
- **S5 — Exit-selection policy:** Determine when/what additional non-public exits should be opened, balancing evacuation benefit versus security posture.
- **S6 — Responder ingress:** Model safest/fastest ingress paths and scheduling relative to civilian egress.
- **S7 — Threat scenario library:** Define parametric threat cases (e.g., localized hazard, exit blocking, corridor loss) that modify the network.
- **S8 — Technology integration:** Explore how apps such as Affluences could support dynamic guidance and coordination.
- **S9 — Validation & transferability:** Design validation protocols and generalization to other structures.

### 2.3 Intended deliverables (future work)
- A documented, parametric evacuation network model with scenario inputs.
- A solution/analysis pipeline producing evacuation-time and congestion diagnostics.
- A scenario comparison framework for policy exploration (exit policies, threat cases).
- A validation report and an implementation/policy recommendation section.

---

## 3. Assumptions

The following are *candidate* assumptions to be adopted, justified, and later tested. Each should be treated as a modeling choice subject to sensitivity analysis.

### 3.1 Structural / geometric assumptions
- **A1:** The museum can be abstracted as a connected graph of corridors, galleries, stairwells, and exits with finite capacities, retaining essential connectivity and chokepoints while discarding decorative detail. *Justification:* tractability; preserves routing topology. *Validation later:* compare aggregate flow behavior against documented circulation descriptions; refine granularity where bottlenecks appear.
- **A2:** Floor-to-floor movement is modeled via discrete vertical links (stairs/elevators/escalators) with assigned throughput; elevators may be restricted for general egress (typically reserved for mobility-impaired occupants and responders). *Justification:* vertical transport is a known dominant constraint. *Validation later:* sensitivity to elevator policy and stair counts.
- **A3:** Exit capacity and door widths can be represented by standardized specific-flow values from pedestrian-flow literature. *Justification:* common practice in egress modeling. *Validation later:* vary flow coefficients across accepted ranges.

### 3.2 Population / behavioral assumptions
- **A4:** Occupancy is described by scenario-level zone counts rather than individual identities. *Justification:* individual tracking data is unavailable. *Validation later:* compare per-zone distribution scenarios for robustness.
- **A5:** Occupants are assumed to follow assigned/directed routes with a compliance factor; some fraction may behave sub-optimally (self-routing, backtracking, following crowds). *Justification:* realism in crowd dynamics. *Validation later:* vary compliance ratio and re-test.
- **A6:** Groups move as cohesive units and slow decision-making; mobility-impaired occupants require specific routes (e.g., accessible exits/elevators) and additional service time. *Justification:* stated problem diversity. *Validation later:* dedicated accessibility scenarios.
- **A7:** Communication of directives (via staff/apps) is assumed to reach a scenario-specified fraction of occupants with some delay. *Justification:* technology is an explicit problem element. *Validation later:* vary reach/delay.

### 3.3 Threat / operational assumptions
- **A8:** Threats act by modifying network availability (removing/bottlenecking nodes or edges) or by inducing local hazards; threat dynamics themselves are exogenous scenario parameters. *Justification:* keeps focus on evacuation adaptability. *Validation later:* expand scenario library.
- **A9:** Additional (non-public) exits have limited throughput/security constraints and are only activatable under defined conditions. *Justification:* problem's explicit security trade-off. *Validation later:* policy-threshold sensitivity.
- **A10:** Responders enter through designated controlled points and follow priority corridors. *Justification:* dual-flow requirement. *Validation later:* ingress/egress conflict scenarios.

---

## 4. Data Processing Plan

Because the workspace `data` directory is currently empty and the dataset definition is unpopulated, the plan must specify (a) how to structure inputs if/when data arrives and (b) how to assemble a parameterized baseline from public/reference sources under assumptions.

### 4.1 Data categories to be assembled
- **Geometry/topology:** floor plans, wing layout, corridor/stairs/elevator/exit inventory, and connectivity (from public sources and reasonable schematic reconstruction).
- **Capacities:** door widths, stair widths, corridor widths, elevator/service counts.
- **Occupancy profiles:** seasonal and intraday visitor volume patterns; zone-level distribution (from public visitation statistics and stated totals).
- **Population composition:** estimated proportions of groups, mobility-impaired visitors, and non-native-language visitors.
- **Threat scenarios:** schematic parameter sets (locations, extents, affected segments).
- **Operational/policy parameters:** exit activation rules, security postures, staff deployment.

### 4.2 Preprocessing (planned)
1. **Schema definition:** an agreed file format (e.g., CSV/JSON) for nodes (spaces, exits), edges (connections with length/width), and occupant groups (zone, count, type).
2. **Reconciliation:** align units, coordinate frames, and naming across sources; maintain a provenance log for every parameter.
3. **Graph construction:** convert assembled geometry into a routable graph; validate connectivity and reachability (every occupied zone connects to ≥1 exit).
4. **Cleaning & imputation:** handle missing capacities via documented defaults from pedestrian-flow literature; flag low-confidence values.
5. **Unit normalization:** standardize to consistent SI units and time bases.

### 4.3 Feature construction (planned)
- Derived edge features: effective capacity (width × specific flow), travel time (length / speed), merge/merge-conflict indicators.
- Node features: occupancy, accessibility flags, exit/non-exit classification, responder-priority flags.
- Zone aggregates: population density, accessibility demand, nearest-exit set.
- Scenario features: which nodes/edges are disabled or degraded, and by how much.

### 4.4 Data usage strategy (planned)
- **Baseline study:** a nominal configuration derived from public parameters and assumptions.
- **Scenario studies:** parametric sweeps over occupancy levels, threat cases, and exit policies.
- **Provenance and reproducibility:** every input is versioned; scenarios are declarative so results can be regenerated.
- **Fallback:** if real data is unavailable, proceed with documented parametric placeholders and clearly label confidence; keep the pipeline data-agnostic so real files can be dropped in later.

---

## 5. Candidate Model Framework

This section lists candidate modeling approaches and their roles. **No model is selected or solved here; selection will occur in a later stage.**

### 5.1 Network / flow layer (core)
- **Candidate A — Deterministic minimum-cost / maximum-flow evacuation:** model the museum as a capacitated network; assign occupants to exits to minimize total evacuation time (system optimum), with time-expanded or dynamic-flow formulations.
  - *Variables:* edge flows over time, exit assignment fractions, arrival times.
  - *Math ideas:* multicommodity flow, time-expanded networks, min-cost flow, LP/ILP relaxations.
  - *Advantages:* tractable, gives clear bottleneck diagnostics (saturated edges), naturally handles edge removal.
  - *Limitations:* ignores stochasticity and microscopic congestion dynamics.
- **Candidate B — Cell-transmission / dynamic network loading:** discretize the network into cells/links and propagate occupant density over time.
  - *Advantages:* captures queueing and time-varying congestion better than static flow.
  - *Limitations:* more parameters; calibration needs care.

### 5.2 Crowd-dynamics layer (refinement)
- **Candidate C — Pedestrian/agent-based simulation (e.g., social-force or cellular-automata style):** individuals/cohorts navigate with local interaction rules.
  - *Advantages:* captures bottleneck formation, counter-flow (egress vs ingress), and behavioral heterogeneity.
  - *Limitations:* computationally heavier, parameter-sensitive, needs calibration.
- **Candidate D — Continuum / macroscopic density-flow (LWR-type) models:** treat crowds as a density field with a fundamental diagram.
  - *Advantages:* efficient for large populations; links to flow layer.
  - *Limitations:* loses individual/group behavior.

### 5.3 Decision / optimization layer
- **Candidate E — Multi-objective optimization:** trade off total evacuation time, peak congestion/risk, security exposure from opening extra exits, and responder ingress time.
  - *Math ideas:* multi-objective optimization / Pareto analysis; weighted-sum or ε-constraint.
- **Candidate F — Robust/stochastic optimization:** account for uncertain occupancy, threat location, and compliance.
  - *Math ideas:* scenario-based optimization, chance constraints, robust counterparts.

### 5.4 Behavioral / guidance layer
- **Candidate G — Route-guidance and compliance models:** represent the effect of signage/staff/app directives on route choice; possibly a game-theoretic or user-equilibrium model where occupants self-route.
  - *Advantages:* addresses the "App/Affluences" and human-factor elements.
  - *Limitations:* behavioral parameters are hard to calibrate.

### 5.5 Threat-scenario layer
- **Candidate H — Parametric threat model:** a declarative descriptor that mutates the network (node/edge removal, capacity reduction, hazard zones) enabling rapid scenario generation.
  - *Advantages:* directly satisfies the adaptability requirement; supports stress-testing.

### 5.6 Recommended coupling (to be evaluated later)
A layered architecture is anticipated: **H (scenario)** → **A/B (flow optimization)** → **C/D (crowd dynamics verification)** → **E/F (decision analysis)** → **G (guidance/policy)**. The flow layer provides route/exit assignments and analytical bottlenecks; the crowd layer stresses those assignments microscopically; the decision layer selects among policies; the guidance layer translates to operations.

### 5.7 Key variables (illustrative inventory)
- Structural: node/edge capacities, lengths, connectivity, exit sets (public vs. restricted).
- Population: zone occupancies, group sizes, accessibility demand, language/compliance mix.
- Dynamic: edge flow rates, densities, queue lengths, arrival/clearance times.
- Decision: exit-open policy, route assignment, responder ingress scheduling, guidance activation.
- Objective/performance: total evacuation time, per-zone clearance time, peak density, risk index, ingress delay, security-exposure index.

---

## 6. Implementation Roadmap

### 6.1 Modules (planned)
1. **Scenario & parameter store** — declarative input files; versioned configurations.
2. **Topology builder** — constructs the routable graph from geometry/parameter inputs; performs connectivity checks.
3. **Flow optimizer** — solves the network/dynamic-flow routing problem (Candidate A/B).
4. **Crowd simulator** — optional high-fidelity verification (Candidate C/D).
5. **Threat mutator** — applies scenario descriptors to the network (Candidate H).
6. **Decision analyzer** — runs multi-objective/robust comparisons (Candidate E/F).
7. **Diagnostics & bottleneck reporter** — identifies saturated edges, merging conflicts, and density hotspots.
8. **Ingress planner** — computes responder paths and timing vs. egress (Candidate A/E coupling).
9. **Validation harness** — automated scenarios, metrics, and sensitivity sweeps.
10. **Reporting/visualization** — figures and tables for policy discussion (later stage).

### 6.2 Workflow (planned)
1. Define and document assumptions and parameter provenance.
2. Build the baseline topology and validate connectivity.
3. Define the scenario library (occupancy levels, threat cases, exit policies).
4. Implement the flow layer; obtain baseline routing/exit assignment and bottlenecks.
5. Add dynamic/crowd layer for verification of congestion behavior.
6. Add decision layer to compare policies and trade-offs.
7. Add ingress planning and dual-flow conflict analysis.
8. Run validation, sensitivity, and robustness studies.
9. Translate outputs into implementation and policy recommendations.
10. Generalize the framework to other crowded structures.

### 6.3 Tooling (planned, to be chosen later)
- Optimization/flow: LP/ILP or network-flow solvers; time-expanded formulations.
- Simulation: agent-based or macroscopic crowd tools (selected in a later stage).
- Language/environment: to be finalized; pipeline kept modular and data-agnostic.
- Reproducibility: config-driven runs, versioned inputs, seeded stochastic components.

### 6.4 Milestones (planned)
- **M1:** Documented assumptions + parameter inventory + data schema.
- **M2:** Validated baseline topology with connectivity checks.
- **M3:** Working flow-optimization layer + baseline diagnostics.
- **M4:** Crowd-dynamics verification layer.
- **M5:** Decision/threat scenario comparison capability.
- **M6:** Validation & sensitivity complete.
- **M7:** Policy/implementation + transferability write-up.

---

## 7. Validation Strategy

### 7.1 Evaluation metrics (planned)
- **Total evacuation time** and **per-zone clearance time**.
- **Peak density / congestion indices** and **number/duration of saturated segments**.
- **Exit utilization balance** across available exits.
- **Responder ingress time** and **egress–ingress conflict frequency**.
- **Policy costs / security-exposure index** for extra-exit activation.
- **Robustness measures** (worst-case and variance across scenarios).

### 7.2 Validation methods (planned)
- **Internal consistency:** conservation of occupants (all assigned, all exit), reachability guarantees, and monotonicity checks (e.g., more capacity should not worsen evacuation under identical scenario).
- **Cross-model agreement:** compare flow-layer predictions against crowd-simulation outputs; investigate divergence regions.
- **Benchmarking against literature:** compare specific-flow and clearance behaviors with established egress studies and standards.
- **Boundary/limit tests:** single-exit, single-floor, and mass-exit limiting cases with analytically known behavior.
- **Scenario replay:** verify that threat mutations correctly produce expected route changes.
- **Expert/qualitative validation:** where quantitative data is unavailable, sanity-check against documented museum operations and emergency-management practice.

### 7.3 Sensitivity and robustness analysis (planned)
- Sweep occupancy levels, population composition (groups/accessibility), compliance fraction, and guidance reach/delay.
- Sweep capacity parameters (door widths, stair counts, elevator policy) across plausible ranges.
- Compare system-optimum vs. user-equilibrium routing assumptions and measure the gap.
- Stress-test the threat scenario library, including worst-case multi-blockage cases.
- Report parameter importance rankings and confidence bands for outputs.

### 7.4 Confirmation guardrail
Validation will be judged by whether conclusions remain stable across plausible parameter ranges, not by matching any single dataset (since no dataset is currently provided). Instability itself will be reported as a finding feeding model refinement.

---

## 8. Expected Result Interpretation

*(Interpretation guidance for future results — no results are produced here.)*

- **Evacuation-time outputs** are expected to be reported as ranges/scenario bands rather than single deterministic numbers, reflecting occupancy and threat uncertainty.
- **Bottleneck diagnostics** are expected to be interpreted as prioritized physical sites (specific corridors, stairwells, merges) where capacity interventions or flow control would most reduce clearance time.
- **Exit-policy analysis** is expected to frame the trade-off curve between evacuation speed and security exposure when activating non-public exits, informing *conditional* activation rules.
- **Responder ingress analysis** is expected to identify scheduling/route rules that minimize interference with civilian egress.
- **Guidance/technology findings** are expected to be interpreted as operational levers (signage, staff deployment, app-based dynamic direction) whose value depends on messaging reach and compliance.
- **Transferability** is expected to be expressed as a reusable template: inputs = geometry + occupancy + threat; outputs = routing, timing, bottlenecks — applicable to other crowded structures after parameter adaptation.

---

## 9. Limitations and Improvements

### 9.1 Anticipated limitations
- **No provided dataset:** the current problem package has an empty data directory and empty dataset definition, so the baseline must rely on public information and assumptions; absolute time estimates will carry significant uncertainty.
- **Geometric abstraction error:** coarse graph abstraction may misplace or miss bottlenecks relative to true plans.
- **Behavioral uncertainty:** compliance, panic, group dynamics, and counter-flow behaviors are hard to calibrate.
- **Parameter sensitivity:** pedestrian-flow coefficients and elevator policies strongly influence outcomes.
- **Computational cost:** high-fidelity crowd simulation over a large, multi-floor site may be expensive; a hybrid resolution strategy may be needed.
- **Threat modeling scope:** threats are exogenous descriptors; cascade/secondary effects may be underrepresented.
- **Security trade-offs:** security-exposure quantification is inherently subjective and policy-dependent.

### 9.2 Planned improvements
- Refine topology granularity in identified bottleneck zones (adaptive resolution).
- Add calibration protocol once real floor plans/occupancy data become available.
- Extend to stochastic/robust optimization with explicit uncertainty distributions.
- Incorporate dynamic guidance/feedback and adaptive exit-opening policies.
- Enrich threat library (localized hazards, smoke, structural damage, secondary blockage).
- Formalize accessibility and multi-language guidance considerations as first-class constraints.
- Generalize the framework into a documented, parameterized toolkit for other crowded structures.

---

### Planning completeness checklist
- [x] Problem understanding, objectives, and subproblems stated (Sections 1–2)
- [x] Assumptions with justification and future validation approach (Section 3)
- [x] Candidate models, variables, mathematical ideas, advantages/limitations (Section 5)
- [x] Data processing / feature construction / usage strategy (Section 4)
- [x] Implementation algorithms, workflow, modules (Section 6)
- [x] Validation metrics, methods, sensitivity analysis (Section 7)
- [x] Interpretation guidance, limitations, and improvements (Sections 8–9)
- [x] Future-oriented language only; no computations, fits, code, plots, or final results
