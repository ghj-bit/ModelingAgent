# Modeling Blueprint Draft
## Water and Hydroelectric Power Sharing (MCM 2022, Problem B)

> **Document purpose.** This is a *planning blueprint* for a future modeling effort. It contains no computed results, no fitted parameters, no executed experiments, and no final conclusions. All statements are future-oriented: they describe *what will be designed, built, and evaluated* in later stages. Numeric placeholders (e.g., "reservoir level L", "demand D") refer to quantities to be defined, not to computed values.

---

## 1. Problem Background and Restatement

### 1.1 Domain background
Dams along the Colorado River system — most notably **Glen Canyon Dam (Lake Powell)** and **Hoover Dam (Lake Mead)** — serve two intertwined functions: they store and route water to downstream users, and they convert released water into hydroelectric power. Prolonged drought and climate-driven reductions in inflow have reduced stored volumes, while demand from the states of Arizona, California, Wyoming, New Mexico, and Colorado continues to press against supply. Existing interstate allocation agreements were written for a wetter baseline and may collectively promise more water than the system reliably delivers. Mexico additionally holds residual-water rights, and ecological and legal considerations extend to flows reaching the Gulf of California.

### 1.2 Restatement of the modeling problem
A future model will be built to design a **water allocation and release plan** across the two-dam system that balances multiple, partly conflicting objectives:

- **Water supply allocation** — distribute a fixed (or declining) volume among agriculture, industry, and residential consumers across the five U.S. states plus Mexico.
- **Hydropower production** — generate electricity via controlled releases through both dams, subject to turbine and head constraints.
- **Dam coordination** — operate Lake Powell and Lake Mead as a coupled system rather than independent reservoirs.
- **Environmental / legal residual flow** — preserve a designated residual release to Mexico and a potential flow into the Gulf of California.
- **Sustainability horizon** — estimate how long demands can be met under the assumption of no additional inflow.
- **Scarcity / curtailment regimes** — define allocation rules and priorities when total demand exceeds available supply.

### 1.3 Why a blueprint is needed
The problem couples hydrology, energy conversion, economics, and policy. A single monolithic model would be hard to justify and impossible to validate. The blueprint instead proposes a **layered, modular modeling framework** whose components can be built, tested, and questioned independently before integration.

---

## 2. Objectives and Subproblems

### 2.1 Primary objective
Design a transparent, agreement-independent allocation policy that, for a given water state, specifies reservoir releases, sectoral deliveries, hydropower output, and residual flows, while tracking the long-term sustainability of the system.

### 2.2 Subproblems to be modeled
1. **SP1 — Supply characterization.** Define the water balance of the coupled system: inflow, net evaporation, seepage, storage in each reservoir, and connectivity between Powell → Mead → downstream → Mexico → Gulf of California.
2. **SP2 — Demand characterization.** Represent sectoral water demand (agriculture, industry, residential) by state, and the electricity demand they and the wider grid place on the dams.
3. **SP3 — Hydropower conversion.** Model the relationship between released flow, hydraulic head, turbine efficiency, and generated electricity.
4. **SP4 — Baseline allocation.** Under fixed supply and demand, determine the release/withdrawal schedule that best satisfies stated priorities.
5. **SP5 — Sustainability horizon.** Estimate the time until storage falls below functional thresholds (dead pool / minimum power pool) absent new inflow.
6. **SP6 — Trade-off analysis.** Quantify the competing interests between water usage and electricity production and propose compromise solutions.
7. **SP7 — Scarcity and curtailment.** Define priority-ordered allocation rules for shortage scenarios and residual-flow shortfalls.
8. **SP8 — Dynamic extensions.** Incorporate population/industrial growth or decline, renewable-energy penetration, and conservation measures as scenario modifiers.

### 2.3 Deliverables to be produced later
- A documented mathematical formulation with clearly named variable sets and constraint families.
- An implementation architecture (modules, data contracts, solver choices).
- A validation and sensitivity protocol.
- Material sufficient to draft (a) a concise magazine-style article and (b) a full technical report, subject to the competition's page limits.

---

## 3. Assumptions

The following assumptions will be adopted for the first-generation model and revisited during validation. Each is paired with its rationale and a planned validation approach.

| # | Assumption (draft) | Justification | Planned validation approach |
|---|--------------------|---------------|-----------------------------|
| A1 | The system is treated as two coupled reservoirs with unidirectional Powell→Mead linkage via Glen Canyon release. | Captures dominant hydrology while limiting dimensionality. | Compare modeled storage trajectories with historical reservoir-level time series. |
| A2 | A single annual or monthly time-step is used for the primary model. | Matches the granularity of typical allocation policy and avoids over-parameterization. | Repeat a subsample at finer resolution to confirm stability of qualitative behavior. |
| A3 | Net evaporation and seepage are represented as state-dependent losses. | Reservoir losses depend on surface area / elevation. | Sensitivity-test loss coefficients; bound their effect on the horizon estimate. |
| A4 | Sectoral demand is exogenous per period, with scenario-based growth rates. | Demand drivers (population, industry) are better treated as scenarios than endogenous. | Stress-test with high/low growth assumptions. |
| A5 | Hydropower output is a deterministic function of release, head, and efficiency. | Power-house physics is well understood; short-term stochasticity is secondary. | Compare against nameplate/typical output ranges and efficiency curves. |
| A6 | Minimum environmental / residual flow to Mexico is a hard or soft constraint. | Reflects legal and ecological obligations. | Explore both hard-constraint and penalty-based formulations. |
| A7 | Water quality, salinity, and intra-seasonal weather variability are initially excluded. | Keeps the first model tractable. | Flag as extension; qualitatively discuss impact. |
| A8 | Policy is modeled as an optimization objective rather than as a fixed historical agreement. | The task explicitly requests an agreement-independent solution. | Compare optimized allocations against historical practice as a reference benchmark. |

*Assumptions A1–A8 are provisional and will be converted into either retained assumptions or model extensions after data inspection and sensitivity analysis.*

---

## 4. Data Processing Plan

> No data analysis is performed in this draft. This section only specifies *what data will be sought, how it will be prepared, and how it will be used*.

### 4.1 Data sources to be identified
- **Hydrologic data:** historical inflow to Lake Powell / Lake Mead, reservoir storage-elevation-area curves, net evaporation rates.
- **Operational data:** historical releases, power generation, minimum power-pool and dead-pool elevations.
- **Demand data:** sectoral water withdrawals and electricity demand for the five states and the downstream/Mexico region.
- **Policy/reference data:** treaty and agreement allocations (for benchmark comparison only), residual-flow obligations.
- **Scenario drivers:** population projections, industrial growth indices, renewable-energy adoption trends, documented conservation measures.

### 4.2 Preprocessing to be applied later
- Harmonize units (volume in acre-feet vs. m³; power in MW vs. GWh) and time stamps.
- Fill or flag missing records; document every imputation rule.
- Convert storage-elevation relationships into interpolation functions for head and surface area.
- Decompose series into trend and seasonal components for scenario construction.

### 4.3 Feature / variable construction
- **State variables:** storage levels S_Powell(t), S_Mead(t).
- **Control variables:** release R(t), sectoral deliveries x_sector,state(t), residual flow R_res(t).
- **Derived features:** hydraulic head h(S), power output P(R, h, η), demand-satisfaction ratios.
- **Scenario features:** growth multipliers, conservation-reduction factors, renewable-substitution fractions.

### 4.4 Data usage strategy
- **Calibration set:** historical inflow/level records to tune loss and efficiency parameters.
- **Reference set:** historical operations to benchmark optimized policies.
- **Scenario set:** synthetic demand/inflow trajectories for stress testing.
- All data provenance and transformation steps will be logged to keep the model reproducible and auditable.

---

## 5. Candidate Model Framework

A **layered framework** is proposed so that each subproblem maps to a distinct, testable component.

### 5.1 Layer A — Water balance (mass-conservation) model
- Conceptual form: `S(t+1) = S(t) + Inflow(t) − Release(t) − Evaporation(S) − Seepage(S)`, applied to each reservoir, with Powell release feeding Mead inflow.
- Purpose: define feasibility of any allocation candidate.
- Candidate methods: deterministic discrete-time balance; optional stochastic inflow coupling (e.g., scenario trees) as an extension.

### 5.2 Layer B — Hydropower conversion model
- Conceptual form: `P = η · ρ · g · Q · h(S)`, aggregated over turbines, bounded by capacity.
- Purpose: link water release to electricity output and expose the release/electricity trade-off.
- Candidate methods: piecewise-linear efficiency curve; optional head-dependent efficiency refinement.

### 5.3 Layer C — Demand and allocation model
- Purpose: distribute available water across sectors and states under priority rules.
- Candidate methods:
  - **Linear programming (LP)** for fixed-supply allocation maximizing weighted satisfaction.
  - **Multi-objective optimization** (weighted-sum or ε-constraint) to expose water-vs-energy trade-offs.
  - **Goal programming** representing prioritization tiers (residential → environmental → agriculture → industry), or alternative orderings as scenarios.

### 5.4 Layer D — Sustainability / depletion model
- Purpose: forward-simulate storage under policy-consistent releases to estimate time until functional thresholds are reached.
- Candidate methods: deterministic simulation; survival/`time-to-threshold` estimation; scenario ensembles for uncertainty bands.

### 5.5 Layer E — Scarcity / curtailment model
- Purpose: when demand exceeds supply, apply a documented curtailment policy.
- Candidate methods: lexicographic or priority-weighted allocation; penalty-based soft constraints; rule-based rationing.

### 5.6 Layer F — Dynamic extension model
- Purpose: overlay growth/decline, renewable penetration, and conservation.
- Candidate methods: scenario multipliers on demand; parameterized substitution of hydropower by renewables; parametric conservation efficiency.

### 5.7 Variable summary (to be finalized)
- **Indices:** t (time), i ∈ {Powell, Mead}, s (state), k (sector).
- **State:** S_i(t).
- **Control:** R_i(t), x_{s,k}(t), R_res(t).
- **Derived:** h_i, P_i(t), satisfaction ratios, deficit variables.
- **Objective weights / priority parameters:** to be specified and sensitivity-tested.

### 5.8 Advantages and limitations (per candidate)
- **LP allocation** — advantages: tractable, transparent, provably optimal for a given objective. Limitations: linearity assumptions on efficiency and losses.
- **Multi-objective** — advantages: exposes trade-off frontier. Limitations: weighting is subjective; requires careful reporting.
- **Simulation** — advantages: flexible, supports non-linear dynamics. Limitations: no optimality guarantee; scenario-dependent.
- **Stochastic extension** — advantages: quantifies uncertainty. Limitations: data-hungry; heavier computation.

---

## 6. Implementation Roadmap

> No code will be written at this stage. This section describes the planned build sequence and module architecture.

### 6.1 Proposed modules
1. `data_layer` — ingestion, unit harmonization, interpolation of storage-elevation-area curves.
2. `balance_model` — reservoir mass balance and coupling.
3. `power_model` — head- and release-dependent generation.
4. `demand_model` — sectoral/state demand construction and scenario multipliers.
5. `allocation_solver` — LP / multi-objective optimization engine.
6. `sustainability` — forward simulation and threshold detection.
7. `scarcity_rules` — curtailment and priority logic.
8. `scenario_engine` — driver overlays (growth, renewables, conservation).
9. `validation` — metrics, sensitivity sweeps, and reporting.
10. `reporting` — figure/table generation for the technical report and magazine article.

### 6.2 Build workflow
1. Specify interfaces and data contracts between modules.
2. Prototype Layer A + Layer B on a reduced system to confirm coupling logic.
3. Add Layer C allocation and verify constraint feasibility.
4. Integrate Layer D forward simulation.
5. Layer in Layer E scarcity rules and Layer F scenario overlays.
6. Run validation suite, then finalize documentation.

### 6.3 Algorithms to be considered
- Linear/quadratic programming solvers for allocation.
- Weighted-sum and ε-constraint sweeps for trade-off frontiers.
- Discrete-time forward simulation for depletion.
- Monte Carlo / scenario ensembles for uncertainty propagation.
- Sensitivity-sweep tooling for key parameters.

### 6.4 Practical considerations
- Keep every assumption and parameter in a single configuration file for auditability.
- Log all scenario definitions alongside results for reproducibility.
- Maintain a clear separation between "policy model" and "reference/historical data" so the agreement-independent requirement is respected.

---

## 7. Validation Strategy

### 7.1 Evaluation metrics (planned)
- **Water side:** demand-satisfaction ratio by sector/state; total unmet demand; residual-flow compliance.
- **Energy side:** fraction of potential generation realized; capacity-factor deviation from typical operation.
- **System side:** time-to-threshold (dead pool / minimum power pool); minimum storage buffer maintained.
- **Policy side:** equity/balance across states; robustness of the trade-off frontier to weight changes.

### 7.2 Validation methods
- **Internal consistency:** verify mass balance closes to within a defined tolerance in every simulated period.
- **Benchmarking:** compare modeled baseline operation against historical reservoir levels and generation as a sanity reference (not as ground truth).
- **Back-testing:** replay historical inflow under the proposed policy and examine whether constraints would have held.
- **Cross-model check:** compare LP allocation outcomes with goal-programming outcomes to confirm qualitative agreement.
- **Scenario stress tests:** extreme drought, rapid growth, and aggressive conservation.

### 7.3 Sensitivity and uncertainty analysis
- One-at-a-time sweeps on loss coefficients, efficiency, demand growth, and priority weights.
- Multi-parameter / global sensitivity screening to rank influential inputs.
- Ensemble runs to produce uncertainty bands on the sustainability horizon.
- Trade-off frontier stability analysis under varying objective weights.

### 7.4 Validation acceptance criteria (to be defined)
- Mass-balance closure within a chosen tolerance for all periods.
- Qualitative agreement between independent allocation methods.
- Sensitivity findings that are explainable and documented, not artifacts.

---

## 8. Expected Result Interpretation

> This section describes *how future outputs will be read*, not what the values are. No results are reported here.

- **Allocation schedules** will be interpreted as policy prescriptions: which sectors/states receive water, under what priority, and at what residual-flow level.
- **Electricity outcomes** will be read jointly with water allocation to expose the water-vs-energy trade-off curve rather than a single "answer".
- **Sustainability horizon** estimates will be presented as ranges tied to assumptions, with explicit warnings that they are conditional on the no-new-inflow premise.
- **Scarcity regimes** will be interpreted as decision rules (who curtails first) rather than as predictions.
- **Scenario comparisons** will highlight how growth, renewables, and conservation shift the feasible region.
- **Magazine article** messaging will translate the blueprint into accessible language about trade-offs, conservation leverage, and the value of transparent priority rules.

Interpretation caveats: all outputs will be conditional on the assumption set; no single scenario will be presented as *the* forecast.

---

## 9. Limitations and Improvements

### 9.1 Anticipated limitations (to be confirmed later)
- Coarse temporal resolution may hide intra-seasonal shortages and peaking-power dynamics.
- Treating demand as exogenous may understate feedback between policy and behavior.
- Deterministic efficiency/loss models may misstate energy output at low heads.
- Excluding water quality, salinity, and ecological detail limits environmental realism.
- Optimization weights/priorities are normative choices and may be contested.

### 9.2 Planned improvements / extensions
- Move to finer time resolution and add stochastic inflow scenario trees.
- Endogenize parts of demand (price/conservation response) if data permit.
- Add head-dependent efficiency and turbine-specific constraints.
- Introduce salinity/water-quality constraints for the downstream and Gulf-of-California reaches.
- Extend to a game-theoretic / negotiation layer to model interstate bargaining.
- Add formal uncertainty quantification and robust-optimization variants for policy robustness.

### 9.3 Out of scope for the first generation
- Real-time operational control.
- Legal adjudication of water rights.
- Full economic input–output modeling of the regional economy.

---

## Appendix — Planning Checklist (to be tracked)
- [ ] Confirm data sources and licensing/provenance.
- [ ] Freeze assumption list (A1–A8) after data inspection.
- [ ] Finalize objective weighting and priority tiers.
- [ ] Implement and unit-test each module.
- [ ] Run full validation and sensitivity suite.
- [ ] Draft magazine article and full technical report within page limits.
- [ ] Verify reproducibility package (config + logs + scripts).

*End of blueprint draft — planning content only; no computation performed.*
