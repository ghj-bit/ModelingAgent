# Modeling Blueprint Draft

**Problem ID:** `2011_Space_Shuttle_Problem:`
**Title:** Space Shuttle Problem: No More Space Shuttles
**Source:** HiMCM 2011
**Document type:** Initial modeling plan draft (blueprint only — no solving performed)
**Run:** r1p17_20260917_151333 · round_1

> This document is a **roadmap for future modeling**, not a solution. It contains no computed
> results, no data analysis, no fitted models, and no final conclusions. All language is
> future-oriented ("will", "should", "is expected to") to describe planned work.

---

## 1. Problem Background and Restatement

After the 135th and final US Space Shuttle mission landed on July 21, 2011, the United States
lost its own crewed launch capability and will depend on other nations or commercial providers
until a replacement vehicle is developed. The International Space Station (ISS) is scheduled to
remain in service until at least 2020, so a continued resupply and crew-rotation capability must
be arranged in the interim.

The central task is to design a **comprehensive ten-year plan (approximately 2011–2021) that
maintains the ISS**, specifying:

- the **flight/schedule architecture** (how many launches, of which type, when),
- the **payload assignments** (crew rotations, pressurized cargo, external/logistics items),
- the **costs** of the whole program under a chosen strategy,
- and the **feasibility/sustainability** of that plan given capacity and budget constraints.

Key contextual facts to be carried into the modeling (to be verified and expanded during
research, not assumed final):

- ISS nominal crew capacity is 6; it can surge to as high as 13 during docked shuttle missions.
- ISS operational life target: at least through 2020.
- Historical US Shuttle transport cost: roughly \$5,000–10,000 per pound to orbit.
- Shuttle missions lasted about 10–14 days in orbit.
- Typical ISS crew rotations last about six months.
- Private industry has made progress on unmanned launch vehicles.
- Russia offered to launch US astronauts at a cost of about \$60 million each.

Because the source is a competition-style problem, the "data" will largely consist of this
statement plus externally sourced public reference values. The plan below therefore emphasizes a
**research-and-parameterize** approach in which data acquisition is itself a modeled workstream.

---

## 2. Objectives and Subproblems

### 2.1 Primary objective

To produce a ten-year ISS sustainability plan that selects a mix of launch providers and vehicle
types, assigns payloads and crew rotations, and quantifies cost, schedule, and logistics
feasibility in a defensible, reproducible way.

### 2.2 Subproblems (planned decomposition)

1. **Demand modeling** — Determine the ISS's annual requirements over ten years:
   - crew rotation cadence (persons per rotation, rotations per year, overlap/surge handling),
   - consumables and logistics mass (food, water, propellant, spares, experiments),
   - module/equipment and external payload needs,
   - any contingency/reserve demand.
2. **Supply / vehicle characterization** — Characterize candidate transport options:
   - crewed vehicles (e.g., Russian Soyuz-type seats, and future commercial crew concepts),
   - cargo vehicles (uncrewed, national and commercial),
   - any residual or replacement US capability assumed to arrive mid-decade.
3. **Schedule construction** — Build a timeline of launches that meets demand without violating
   capacity, docking, and cadence constraints.
4. **Cost modeling** — Aggregate per-seat, per-kilogram, fixed, and infrastructure costs into a
   ten-year budget, including uncertainty ranges.
5. **Optimization / strategy comparison** — Compare candidate strategies (e.g., heavy reliance on
   purchased seats vs. mixed commercial vs. accelerated domestic replacement).
6. **Robustness and risk analysis** — Stress-test the plan against cost fluctuations, schedule
   slips, and provider availability.
7. **Recommendation synthesis** — Present a preferred plan with sensitivity-informed caveats.

### 2.3 Planned deliverables

- A demand profile per year (structure defined before any numbers are produced).
- A candidate vehicle/provider catalog with parameter slots.
- A schedule template (Gantt-like structure) for the ten-year horizon.
- A cost roll-up framework with uncertainty bands.
- A comparison matrix of strategies with trade-off metrics.
- A validation and sensitivity report.

*(All of the above describe structures to be populated in later stages; this draft defines
them but does not fill them in.)*

---

## 3. Assumptions

Assumptions are grouped by area. Each is listed with a **justification** (why it is reasonable)
and a **future validation approach** (how a later stage should test or refine it).

### 3.1 Scope and horizon
- **A1 — Planning horizon is ten years from mid-2011 (≈2011–2021).** Justification: the problem
  asks for a ten-year plan and the ISS life target is "at least 2020." Future validation: re-check
  against any updated ISS retirement date if the model is extended beyond the competition window.
- **A2 — The ISS remains operational and crewed throughout the horizon.** Justification: the
  statement treats ISS as requiring maintenance until at least 2020. Future validation: scenario
  runs with an earlier/later deorbit.
- **A3 — No major catastrophic loss of ISS or vehicle is modeled as the base case.**
  Justification: base-case planning typically excludes low-probability catastrophic events, which
  can be handled separately as risk scenarios. Future validation: add probabilistic failure
  scenarios in the risk stage.

### 3.2 Demand
- **A4 — Crew rotations occur on a roughly six-month cadence with a target steady-state crew.**
  Justification: stated typical mission length is ~6 months and nominal capacity is 6. Future
  validation: compare against real historical rotation schedules and adjust cadence.
- **A5 — Consumable and logistics demand scales with crew size and elapsed time, plus a fixed
  overhead per increment.** Justification: physical necessity; standard logistic modeling.
  Future validation: calibrate the scaling constant against published ISS resupply mass figures.
- **A6 — Surge occupancy (up to 13) is a temporary docking condition, not a sustained crew
  level.** Justification: stated surge context. Future validation: model docking overlaps
  explicitly in the schedule subproblem.

### 3.3 Supply and cost
- **A7 — Purchased crew seats cost on the order of \$60M each in the early horizon.** Justification:
  the statement cites this Russian offer price. Future validation: build a price path/scenario set
  since seat prices historically rose over time.
- **A8 — Cargo cost can be modeled both per-kilogram and per-flight.** Justification: shuttle-era
  figures are per-pound while vehicle contracts are often per-flight. Future validation: reconcile
  unit conventions and test both.
- **A9 — A domestic/commercial replacement capability will become available at some assumed year
  within the horizon.** Justification: the problem motivates a replacement vehicle; its timing is
  uncertain. Future validation: treat the availability year as a key scenario/sensitivity variable.
- **A10 — Costs are expressed in constant (real) dollars unless a scenario specifies inflation.**
  Justification: avoids conflating price trends with general inflation. Future validation: add an
  escalation scenario.
- **A11 — Fixed program overheads (ground operations, integration, insurance) are either folded
  into unit costs or modeled as a separate annual term.** Justification: keeps the first model
  tractable. Future validation: separate out components and re-aggregate.

### 3.4 Modeling simplifications
- **A12 — Deterministic first pass, with uncertainty introduced via scenarios/sensitivity.**
  Justification: establishes a transparent baseline before stochastic complexity. Future
  validation: upgrade key uncertain inputs to distributions and run Monte Carlo.
- **A13 — Discrete annual or semi-annual time steps for the aggregate model, with an optional
  finer-grained schedule layer.** Justification: matches rotation cadence and keeps optimization
  tractable. Future validation: refine granularity where docking/cadence constraints bind.
- **A14 — Vehicle capacity and mass/volume limits are treated as hard constraints.**
  Justification: physical limits. Future validation: verify against published payload specs.

---

## 4. Data Processing Plan

Because the provided input is principally the problem statement, the data workstream is planned
as **collection → normalization → parameterization → governance**.

### 4.1 Data collection (planned sources, to be gathered in a later stage)
- Statement-derived facts (crew size, surge, costs, mission durations, horizon).
- Public reference data for candidate vehicles: crew capacity, cargo up/down mass and volume,
  launch cadence, mission duration, docking compatibility.
- Historical cost references: per-seat and per-kilogram figures, shuttle-era benchmarks.
- Historical ISS logistics/rotation schedules as a reality check (used for validation, not for
  producing this blueprint).

### 4.2 Preprocessing steps (planned)
- **Unit harmonization:** pounds ↔ kilograms, nominal vs. real dollars, per-flight vs. per-kg.
- **Currency/base-year normalization:** select a base year; note any escalation adjustments.
- **Missing-value policy:** document how gaps in public sources will be filled (bounded ranges or
  conservative defaults) and flag every imputed value.
- **Outlier/consistency checks:** cross-check cited unit costs against multiple references.
- **Source provenance:** record citation, date accessed, and reliability rating for every value.

### 4.3 Feature / parameter construction (planned)
- **Derived demand parameters:** annual crew-seat demand, annual cargo mass, surge headroom.
- **Derived supply parameters:** effective capacity per vehicle per year (sites × cadence ×
  payload).
- **Derived cost parameters:** blended cost per rotation, blended cost per kg, fixed annual cost.
- **Scenario knobs:** replacement-vehicle availability year, seat-price path, cargo-demand growth.

### 4.4 Data usage strategy
- **Parameter table as the single source of truth** feeding every model variant.
- **Separation of calibration data from validation data** where historical series exist.
- **Sensitivity-first design:** every uncertain parameter is tagged so the sensitivity stage can
  vary it systematically.
- **Reproducibility:** values will be stored in an external parameter file (to be created later)
  so this document remains a plan, not a result.

---

## 5. Candidate Model Framework

The plan anticipates a **layered, multi-model framework** rather than a single monolithic model,
because the problem mixes scheduling, logistics, cost, and strategy decisions.

### 5.1 Layer 1 — Demand / requirements model
- **Idea:** Represent ISS annual demand as crew rotations plus logistics mass over time.
- **Candidate methods:** simple deterministic balance equations; ergodic mass-rate model;
  optionally a small system-dynamics (stock-and-flow) formulation for consumables.
- **Variables (symbolic):** annual crew demand, annual cargo mass demand, reserve fraction.
- **Advantages:** transparent, easy to calibrate, exposes key drivers.
- **Limitations:** ignores intra-year timing until Layer 3.

### 5.2 Layer 2 — Supply / capacity model
- **Idea:** Convert vehicle characteristics into effective annual throughput per provider.
- **Candidate methods:** constraint tables / linear capacity inequalities; capacity-expansion
  reasoning if new vehicles enter mid-horizon.
- **Variables:** number of flights per vehicle type per year, payload per flight, seats per flight.
- **Advantages:** captures the core "who can carry what, how often" trade-off.
- **Limitations:** requires externally sourced vehicle specs with uncertainty.

### 5.3 Layer 3 — Scheduling model
- **Idea:** Place flights on a timeline satisfying cadence, docking, and demand constraints.
- **Candidate methods:** constraint programming or MILP scheduling; Gantt/heuristic construction
  for a first feasible plan; possibly bin-packing for payload manifests.
- **Variables:** launch dates/periods, assigned mission type, payload manifest.
- **Advantages:** makes the plan executable and reveals feasibility bottlenecks.
- **Limitations:** combinatorial; needs careful horizon granularity (A13).

### 5.4 Layer 4 — Cost model
- **Idea:** Aggregate per-seat, per-kg, per-flight, and fixed costs over the horizon.
- **Candidate methods:** activity-based cost roll-up; discounted or undiscounted NPV-style
  aggregation (to be decided as a modeling choice); uncertainty bands via ranges/scenarios.
- **Variables:** unit costs, flight counts, mass totals, annual fixed cost, (optional) discount rate.
- **Advantages:** directly answers the "complete with costs" requirement.
- **Limitations:** unit-cost uncertainty dominates; must be stress-tested.

### 5.5 Layer 5 — Strategy optimization
- **Idea:** Select the plan minimizing cost (or a weighted cost/risk objective) subject to demand
  and capacity constraints.
- **Candidate methods:** linear/mixed-integer programming; multi-objective optimization
  (cost vs. risk vs. schedule robustness); scenario-based stochastic programming if upgraded.
- **Variables:** decision variables = flights by type/time; objective = total program cost.
- **Advantages:** produces a defensible recommendation and clean trade-off frontiers.
- **Limitations:** solution quality depends on parameter fidelity; may need decomposition.

### 5.6 Cross-cutting mathematical ideas (candidate toolbox)
- Linear and mixed-integer programming for allocation and scheduling.
- Constraint satisfaction for timing/feasibility.
- Bin-packing / knapsack for payload manifests.
- Multi-criteria decision analysis and Pareto-frontier methods for strategy ranking.
- Scenario analysis and (later) Monte Carlo for uncertainty.
- Systems dynamics as an alternative lens for consumable stocks.

### 5.7 Integration logic
- Layer 1 output feeds constraints in Layer 5; Layer 2 supplies capacity parameters; Layer 5
  chooses flights; Layer 3 validates/realizes the schedule; Layer 4 prices the realized plan; the
  loop iterates if the schedule is infeasible, which triggers re-optimization.

---

## 6. Implementation Roadmap

### 6.1 Planned algorithms and techniques
- Deterministic demand calculation (balance equations).
- Linear/MILP solver for allocation and cost minimization.
- Constraint-based scheduling or heuristic construction for the timeline.
- Bin-packing/knapsack for manifests.
- Scenario sweep and sensitivity experiments.
- (Optional, later) Monte Carlo simulation for uncertainty propagation.

### 6.2 Planned workflow stages
1. **Research & parameterization:** assemble the parameter table and vehicle catalog.
2. **Baseline construction:** build the simplest feasible plan (deterministic, coarse time steps).
3. **Model build-out:** formalize demand, capacity, scheduling, and cost layers.
4. **Optimization run:** generate candidate strategies and compare them.
5. **Schedule refinement:** check dock/cadence constraints, adjust manifests.
6. **Uncertainty treatment:** scenario and sensitivity runs on key parameters.
7. **Synthesis & reporting:** consolidate the recommended plan with caveats.

### 6.3 Required modules (planned file/notebook responsibilities)
- `params` module — centralized parameter/scenario definitions.
- `demand` module — requirement calculations.
- `supply` module — vehicle capacity and catalog handling.
- `schedule` module — timeline construction and feasibility checks.
- `cost` module — cost aggregation and (optional) discounting.
- `optimize` module — LP/MILP or heuristic strategy selection.
- `analysis` module — sensitivity, scenario, and robustness routines.
- `report` module — tables/figures for the final write-up (produced in a later stage).
- Governance: version control, a run log, and provenance notes for every input value.

### 6.4 Tooling (planned, non-binding)
- A scripting environment with optimization and data libraries (e.g., Python with an MILP solver)
  is anticipated; the exact stack will be fixed at build time. *(No code is written in this draft.)*

### 6.5 Milestones (indicative)
- M1: parameter table complete and sourced.
- M2: baseline feasible plan demonstrated (structural, not final numbers).
- M3: optimization layer operational across at least two strategies.
- M4: sensitivity/scenario results available.
- M5: consolidated recommended plan and documentation.

---

## 7. Validation Strategy

### 7.1 Evaluation metrics (planned)
- **Cost metrics:** total ten-year program cost; cost per crew rotation; cost per kilogram
  delivered; cost per crew-day supported.
- **Feasibility metrics:** unmet demand (should be zero in a valid plan); capacity utilization;
  schedule-slack / bottleneck counts.
- **Robustness metrics:** cost dispersion and feasibility stability across scenarios.
- **Trade-off metrics:** Pareto spread across cost, risk, and schedule margin.

### 7.2 Validation methods (planned)
- **Internal consistency:** independent recomputation of demand vs. supply totals; unit and
  dimensional checks; conservation checks (mass and seats carried ≥ required).
- **Constraint verification:** explicit audits that every hard constraint is satisfied.
- **Historical reasonableness check:** compare modeled rotation cadence and resupply levels
  against published historical patterns (used qualitatively, not as a data analysis here).
- **Cross-model agreement:** compare LP/MILP optimum with a heuristic schedule to confirm the
  objective and feasibility are credible.
- **Expert/reference review:** sanity-check parameters against authoritative public sources.
- **Boundary tests:** run limiting cases (e.g., single provider; replacement vehicle never
  arrives) to confirm the model behaves sensibly at the edges.

### 7.3 Sensitivity analysis (planned)
- **One-at-a-time sweeps** over the most influential parameters: seat price, cost per kg,
  replacement-vehicle arrival year, crew rotation cadence, cargo demand growth.
- **Scenario analysis:** bundled futures (optimistic/pessimistic/provider-constrained) rather
  than isolated parameter changes.
- **Tornado/contribution ranking** to identify which inputs most affect total cost and
  feasibility.
- **Threshold analysis:** find break-even points (e.g., the price/year at which switching
  strategy becomes preferable).
- **Optional Monte Carlo** on uncertain inputs to produce confidence bands on cost and
  feasibility (upgrade stage).

---

## 8. Expected Result Interpretation

This section describes **how future results will be read**, not what they are.

- The output will be a **recommended ten-year plan**: a table/list of launches by year and type,
  with crew seats and cargo mass assigned, plus a total cost and its uncertainty range.
- Results will be interpreted **comparatively**: the value of the recommendation comes from how
  it performs against alternative strategies (e.g., all-purchased-seats vs. mixed vs. accelerated
  domestic replacement) on cost, feasibility, and robustness.
- **Sensitivity findings** will indicate which assumptions the recommendation is most exposed to;
  a robust plan should retain feasibility across a reasonable range of those parameters.
- **Scenario results** will bound the outcome: an optimistic case will show a floor on cost and a
  pessimistic case a ceiling, with feasibility flags indicating when a scenario breaks constraints.
- Any apparent optimum should be presented as **conditional on the stated assumptions**, and the
  narrative should foreground trade-offs rather than a single number.
- Where the model cannot discriminate (flat objective regions), the interpretation should
  acknowledge **model insensitivity** and lean on qualitative/robustness arguments.

---

## 9. Limitations and Improvements

### 9.1 Anticipated limitations
- **Parameter uncertainty:** much of the cost and capacity data must come from public sources of
  varying reliability; results are only as good as those inputs.
- **Aggregation loss:** coarse time steps and lumped cost terms may hide dynamic or operational
  details that matter in reality.
- **Deterministic bias:** a deterministic base case can understate risk and overstate precision.
- **Scope assumptions:** fixed horizon, base-case no-catastrophe, and assumed replacement timing
  all shape the answer and may not match reality.
- **Externalities ignored:** geopolitical/regulatory factors, supply-chain constraints, and
  programmatic politics are only loosely representable.
- **Single-objective risk:** optimizing purely on cost may yield plans that are cheap but fragile.

### 9.2 Planned improvements (future iterations)
- Replace point estimates with **distributions** and run Monte Carlo to produce probabilistic
  cost and feasibility statements.
- Refine the **scheduling layer** in time (down to weeks/months) where constraints bind.
- Add a **risk/robustness objective** and explore multi-objective Pareto solutions.
- Extend to **dynamic capacity expansion** (endogenizing when new vehicles enter service).
- Incorporate **inflation/escalation** and real-vs-nominal-dollar analysis.
- Validate against a **broader historical dataset** if one becomes available.
- Broaden the **strategy space** and stress-test against adversarial scenarios.
- Document all assumptions and provenance so the blueprint can be handed off and reproduced.

---

## Appendix A — Planned Workflow at a Glance

| Stage | Focus | Key Output (to be produced later) |
|-------|-------|-----------------------------------|
| 1 | Problem framing | Objectives, subproblems, deliverables |
| 2 | Assumptions | Justified assumption register |
| 3 | Data plan | Sourced, harmonized parameter table |
| 4 | Model build | Demand/capacity/schedule/cost layers |
| 5 | Optimization | Candidate strategy set + trade-offs |
| 6 | Validation | Metrics, constraints, sensitivity |
| 7 | Synthesis | Recommended ten-year plan + caveats |

## Appendix B — Compliance Note

This draft intentionally contains **no computed results, no data analysis, no fitted models, no
executed experiments, and no final conclusions**. It defines only the modeling workflow,
assumptions, candidate methods, data processing plan, implementation plan, and validation
strategy, as required for an initial modeling plan.
