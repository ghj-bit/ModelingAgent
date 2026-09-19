# Modeling Blueprint Draft — MM-Bench 2017_A
## Managing the Zambezi River / Kariba Dam Replacement Study

> **Document status:** Initial modeling plan (blueprint) — planning content only.
> No data analysis, computation, model fitting, or results are included.
> All statements are forward-looking proposals for the future modeling effort.
>
> **Note on staged data:** The provided `data/` directory contains no staged files and
> the dataset definition given with the problem is empty (`{}`). Consequently, this
> plan assumes all inputs will be **acquired from external/public sources** during
> execution (see §4). Any variable names below are proposals, not observed fields.

---

## 1. Problem Background and Restatement

### 1.1 Real-world setting (as given)
The Kariba Dam sits on the Zambezi River and is described in the problem statement as
one of the larger dams in Africa. Its construction was controversial, and a 2015 report
by the Institute of Risk Management of South Africa included a warning that the dam is
in dire need of maintenance. The Zambezi River Authority (ZRA) is presented with three
candidate courses of action:

- **(Option 1) Repair** the existing Kariba Dam.
- **(Option 2) Rebuild** the existing Kariba Dam.
- **(Option 3) Remove** the Kariba Dam and **replace it with a series of ten to twenty
  smaller dams** along the Zambezi River.

### 1.2 Restatement of what the ZRA requires
The future report will have to satisfy two distinct, explicitly separated requirements:

- **Requirement 1 — Comparative executive brief (≤ 2 pages, in addition to the main
  report).** A brief assessment of the three options listed, with enough detail to give
  an overview of the potential **costs and benefits** associated with each option.
- **Requirement 2 — Detailed Option 3 analysis (main report).** A detailed analysis of
  removing Kariba and replacing it with **ten to twenty smaller dams**, where the new
  system must:
  1. have the **same overall water management capabilities** as the existing Kariba Dam;
  2. provide **the same or greater levels of protection and water-management options**
     for Lake Kariba as the existing dam;
  3. be analyzed well enough to **support a recommendation on the number and placement**
     of the new dams along the Zambezi River;
  4. include a **strategy for modulating water flow** through the multiple-dam system
     that balances **safety against costs**;
  5. address **known or predicted normal water cycles**, and give ZRA managers
     **explained and justified actions** for **emergency water flow** situations
     (flooding and/or prolonged low water);
  6. provide **specific guidance for extreme water flows ranging from maximum expected
     discharges to minimum expected discharges**;
  7. include **restrictions on the locations and lengths of time** that different areas
     of the Zambezi River should be exposed to the most detrimental effects of the
     extreme conditions.

### 1.3 Why this is a systems-modeling problem
The task couples (a) hydrological uncertainty, (b) hydraulic/routing behavior of a
cascade of reservoirs, (c) engineering/economic lifecycle cost, (d) operational policy
under normal and extreme conditions, and (e) multi-criteria decision-making. It is
therefore planned as a **multi-model, multi-scale planning study**, not a single
equation.

---

## 2. Objectives and Subproblems

### 2.1 Overall objective (proposed)
To design and recommend a replacement multi-dam configuration (number + placement +
operating policy) that is hydrologically and hydraulically equivalent or superior to the
existing Kariba Dam, and to communicate the trade-offs among Options 1–3 to ZRA
management.

### 2.2 Deliverables (planned)
| ID | Deliverable | Requirement |
|----|-------------|-------------|
| D1 | Two-page executive brief comparing Options 1–3 (costs/benefits) | Req. 1 |
| D2 | Recommended **number N** (10–20) and **placement** of new dams | Req. 2 |
| D3 | **Flow-modulation strategy** balancing safety vs. cost | Req. 2 |
| D4 | **Emergency-flow playbook** for floods and prolonged low water | Req. 2 |
| D5 | **Extreme-flow guidance** from maximum to minimum expected discharge | Req. 2 |
| D6 | **Exposure restrictions** (locations × durations) for detrimental conditions | Req. 2 |
| D7 | Main technical report integrating D2–D6 with assumptions & validation | Req. 2 |

### 2.3 Subproblems (planned decomposition)
- **SP1 — Baseline characterization.** Describe the present-day Kariba system: reservoir
  storage dynamics, inflow regime, releases, hydropower, and flood-control role, using
  documented characteristics and acquired time series.
- **SP2 — Options 1 & 2 assessment.** Build a comparable lifecycle cost/benefit framing
  for *repair* vs. *rebuild* (capital, downtime, risk reduction, lost generation,
  residual life).
- **SP3 — Multi-dam configuration generation.** Propose a systematic way to enumerate
  candidate layouts (N and siting) along the river, respecting terrain and valley
  geometry.
- **SP4 — Cascade simulation.** Model the reservoir network (continuity + routing) to
  evaluate whether a given configuration reproduces Kariba's aggregate storage and
  regulation capability.
- **SP5 — Configuration optimization.** Search over N and placement (and sizes) to
  satisfy equivalence/protection constraints at minimum cost/risk.
- **SP6 — Operating policy design.** Derive rule curves / release schedules that perform
  across normal, flood, and drought regimes.
- **SP7 — Extreme-flow strategy.** Convert policy into actionable guidance for maximum
  through minimum discharges, plus exposure-location/duration restrictions.
- **SP8 — Synthesis and decision support.** MCDA to produce D1 and the final
  recommendation, with uncertainty and sensitivity.

---

## 3. Assumptions

Each assumption below is stated with **(a)** justification for adopting it in the first
pass, and **(b)** the future validation step that will test it.

### 3.1 Hydrological / environmental
- **A1 — Reference hydrology is represented by historical gauge records**, possibly
  extended by regionalization. *Justification:* direct long records on the Zambezi are
  limited; regionalization is standard practice. *Validation:* compare reconstructed
  series against independent records and documented lake-level history.
- **A2 — A baseline stationarity assumption for calibration, with non-stationarity
  handled as scenarios.** *Justification:* enables tractable stochastic models while
  acknowledging climate risk. *Validation:* trend/change-point tests; scenario
  re-evaluation under shifted means/variance.
- **A3 — Lake evaporation and seepage are modeled as deterministic seasonal functions**
  (or with bounded uncertainty). *Justification:* evaporation is a major but slowly
  varying loss term. *Validation:* sensitivity to evaporation amplitude.
- **A4 — Sediment transport and morphological change are initially neglected**, then
  examined in a later phase. *Justification:* first-pass capacity/regulation modeling is
  dominated by water balance. *Validation:* scoping check of reservoir sedimentation
  rates and their effect on usable storage.
- **A5 — Environmental/ecological and social performance are treated as qualitative
  criteria in the first pass**, quantified later if data allow.

### 3.2 Engineering / hydraulic
- **A6 — One-dimensional routing is adequate for the first-pass cascade**, with 2D
  refinement only at critical reaches. *Justification:* balances fidelity and cost.
  *Validation:* convergence checks and spot comparison against higher-fidelity models.
- **A7 — Each candidate dam is characterized by a storage–elevation–area relationship
  and an outlet/spillway capacity curve.** *Justification:* required for mass-balance
  simulation. *Validation:* consistency with terrain data at proposed sites.
- **A8 — Downstream boundary conditions (e.g., at major confluences and the downstream
  international boundary) can be treated as constraints/fixed demands.**
  *Validation:* sensitivity to boundary assumptions.

### 3.3 Economic / operational
- **A9 — Costs follow parametric cost functions** (per unit storage, per unit height,
  per MW) calibrated from comparable projects. *Justification:* site-specific bids are
  unavailable at planning stage. *Validation:* benchmark against documented dam cost
  ranges; scenario swings on unit costs.
- **A10 — Operations aim to balance firm energy/water supply, flood attenuation, and
  ecological minimum flow.** *Justification:* reflects ZRA's multi-purpose mandate.
  *Validation:* expert review of rule curves; reliability metrics.
- **A11 — Stakeholders (Zambia/Zimbabwe power utilities, downstream Mozambique) are
  represented through demand and constraint targets rather than game-theoretic
  negotiation in the first pass.** *Validation:* later transboundary extension.

### 3.4 Modeling-scope assumptions
- **A12 — The three options are compared on a common time horizon and common currency
  basis** (discounted). *Validation:* sensitivity to discount rate and horizon.
- **A13 — Emergency events are drawn from an extreme-value framework** (return-period
  based), not only from observed maxima. *Validation:* goodness-of-fit of extreme-value
  models.

---

## 4. Data Processing Plan

> Because no data are staged, this section defines the **acquisition → cleaning →
  feature** pipeline that the future work will follow.

### 4.1 Candidate data sources (to be acquired)
- **Hydrology:** Zambezi River Authority records; Global Runoff Data Centre (GRDC);
  national water authorities of Zambia/Zimbabwe/Mozambique; published gauge series at
  key stations (e.g., upstream of Kariba, Victoria Falls, and downstream reaches).
- **Lake/reservoir:** documented storage–elevation–area curves, lake-level histories,
  spillway and outlet capacities, historical generation and release records.
- **Climate/meteorology:** reanalysis (e.g., ERA5) and gridded precipitation for
  inflow modeling and evaporation; drought indices.
- **Terrain/geospatial:** digital elevation models (e.g., SRTM) for candidate siting,
  reach slopes, and inundation geometry; satellite imagery for reservoir extent.
- **Engineering/economic:** published project costs, lifecycle O&M, discount-rate
  conventions, hydropower valuations.
- **Downstream sector:** irrigation/urban demand estimates and environmental flow
  requirements.

### 4.2 Preprocessing steps (planned)
1. **Unit and time-base harmonization** (m³/s, km³, monthly vs. daily; timezone/seasonal
   alignment to the Zambezi water year).
2. **Quality control:** outlier/speciation checks, physically implausible value flagging,
   consistency across stations (upstream vs. downstream mass balance).
3. **Missing-data treatment:** interpolation for short gaps; regional regression or
   multiple imputation for long gaps; explicit provenance flags.
4. **Rating-curve derivation/validation** to convert stage to discharge where needed.
5. **Resampling and aggregation** to the modeling time step(s) (e.g., daily for floods,
   monthly for planning).
6. **Derived-geometry construction:** storage–elevation–area polynomials from DEM and
   documented survey data.

### 4.3 Feature/derived-quantity construction (planned)
- **Seasonal climatology** and flow-duration characteristics of historic inflows.
- **Extreme-flow quantiles** via extreme-value theory (flood peaks, low-flow minima) to
  define the maximum/minimum expected discharge envelope demanded by the problem.
- **Drought indicators** (e.g., standardized precipitation/evaporation indices) mapped to
  reservoir stress.
- **Energy/head proxies** linking reservoir level to power potential.
- **Candidate site descriptors:** valley width, slope, upstream contributing area,
  accessible storage volume, distance between sites.
- **Economic descriptors:** unit-cost parameters, discount factors, demand trajectories.

### 4.4 Data usage strategy (planned)
- **Calibration/validation split** (e.g., earlier decades for calibration, withheld
  years/events for validation), with no leakage.
- **Scenario library:** normal-near-average, dry cycle, wet cycle, and extreme
  flood/drought events synthesized or selected from the record.
- **Synthetic generation** where the record is too short for extreme events (stochastic
  inflow generation), clearly labeled as synthetic.
- **Traceability:** every value used in modeling will carry a source and
  processing-provenance tag.

---

## 5. Candidate Model Framework

The study will be organized as a **layered model stack**; each layer has alternative
candidate methods to be benchmarked.

### 5.1 Layer 1 — Inflow / hydrology models
| Candidate | Mathematical idea | Advantages | Limitations |
|-----------|-------------------|------------|-------------|
| Seasonal decomposition + ARIMA/SARIMA | Autoregressive structure on detrended/seasonal series | Interpretable, fast | Linear, Gaussian-ish |
| Stochastic Markov / periodic Markov | State-transition probabilities | Good for scenario generation | Discretization choices |
| Copulas (multivariate) | Joint dependence across sites/season | Models dependence flexibly | Data-hungry |
| Extreme Value Theory (GEV/GPD, peaks-over-threshold) | Tail behavior of floods/droughts | Directly yields extreme envelope | Sensitive to threshold |
| Conceptual rainfall–runoff (e.g., tank/GHM) | Convert rainfall to inflow | Uses climate inputs | Parameter identifiability |

### 5.2 Layer 2 — Single-reservoir water balance & operation
- **Continuity (mass-balance) equation** for each reservoir as the core dynamic:
  change in storage = inflow + direct rainfall − outflow/release − evaporation − seepage
  (formulated symbolically at planning stage).
- **Rule curves / hedging policies** expressed as functions of storage and season.
- **Release decision models:** linear programming (for economics), dynamic programming
  (Bellman recursion) for multistage release decisions, stochastic DP for uncertainty.

### 5.3 Layer 3 — Multi-dam cascade / river routing
- **Network representation:** reservoirs as nodes, river reaches as arcs; each arc
  carries a routing model.
- **Routing candidates:** Muskingum / Muskingum–Cunge (lumped), kinematic wave, and
  full **1D Saint-Venant (shallow-water) equations** for critical reaches; optional 2D
  refinement.
- **Aggregate equivalence metric:** does the cascade reproduce the existing dam's
  storage, regulation, and flood-attenuation role?

### 5.4 Layer 4 — Configuration optimization (number & placement)
- **Decision variables:** number N (integer, 10–20), site locations along the river,
  and sizes/heights (and thus storage and outlet capacity).
- **Candidate formulations:**
  - Mixed-integer nonlinear programming (MINLP) for joint siting/sizing.
  - Facility-location-style models (candidate sites → selection + capacity).
  - Metaheuristics: **NSGA-II / multi-objective evolutionary algorithms** for
    cost-vs-safety Pareto fronts; simulated annealing / particle swarm as alternatives.
- **Constraints:** summed usable storage/regulation ≥ existing Kariba capability;
  flood protection ≥ existing; environmental minimum flows; siting feasibility
  (terrain, spacing, community constraints).

### 5.5 Layer 5 — Operating policy & extreme-flow strategy
- Derive **rule curves** by optimizing release policy against a scenario ensemble.
- Build an **emergency decision table** keyed to observed/forecast conditions (e.g.,
  incoming discharge percentile bands, lake-level thresholds) with explicit
  justification for each action.
- Express extreme guidance as **bands from maximum expected to minimum expected
  discharge**, with pre-release, spill, and rationing protocols.

### 5.6 Layer 6 — Economics, risk, and decision analysis
- **Lifecycle cost model:** capital + O&M + replacement, discounted to NPV; for the
  multi-dam option, sum across dams plus land/relocation proxies.
- **Benefit streams:** firm energy, water supply, flood-damage avoided, grid reliability.
- **Risk metrics:** exceedance probability, expected annual damage, downside risk.
- **MCDA:** weighted-sum, AHP, and TOPSIS to rank Options 1–3 and to choose among
  Pareto-optimal configurations for D1.
- **Robustness framing:** regret/robust decision-making over climate and cost scenarios.

### 5.7 Key mathematical ideas (summary)
Continuity/mass conservation; Muskingum and Saint-Venant routing; Bellman dynamic
programming; Pareto multi-objective optimization; extreme-value tail modeling;
discounted-NPV economics; reliability–resilience–vulnerability (RRV) metrics; MCDA
scoring.

### 5.8 Variables (proposed taxonomy)
- **Decision:** N; site positions; dam heights/volumes; outlet/spillway capacities;
  rule-curve parameters.
- **State:** reservoir storage per dam; river discharge along reaches; lake level.
- **Exogenous:** inflow series, rainfall, evaporation, demand, costs.
- **Output/objective:** firm energy, reliability, flood-peak reduction, NPV cost,
  environmental compliance.

---

## 6. Implementation Roadmap

### 6.1 Phased plan
0. **Setup & governance:** repository, reproducibility environment, data dictionary,
   assumption register, version control.
1. **Baseline characterization (SP1):** assemble documented Kariba characteristics and
   hydrology; build the inflow scenario library.
2. **Options 1–2 cost/benefit (SP2):** construct comparable lifecycle cost/benefit
   framing for repair vs. rebuild.
3. **Hydrology model build (Layer 1):** calibrate inflow/extreme-flow models.
4. **Cascade simulation engine (Layers 2–3):** single-dam balance → multi-dam network
   with routing; validate conservation of mass.
5. **Configuration optimization (Layer 4):** generate candidate layouts; run
   multi-objective search to obtain Pareto fronts of cost vs. protection/capacity.
6. **Operating policy (Layer 5):** derive rule curves and validate across scenarios.
7. **Extreme-flow strategy & exposure rules (D4–D6):** translate policy into manager
   guidance and location/duration restrictions.
8. **Decision synthesis (Layer 6):** MCDA, ranking, and drafting of D1 (≤2 pages).
9. **Sensitivity & uncertainty:** see §7.
10. **Report assembly:** integrate D1–D7 with assumptions, limitations, and roadmap to
    future work.

### 6.2 Required software modules (planned)
- `data_acquisition` & `provenance` — sourcing and tagging.
- `preprocessing` — QC, gap-filling, resampling, geometry construction.
- `hydrology` — inflow and extreme-value models.
- `reservoir` — mass-balance and rule-curve engine.
- `routing` — Muskingum/1D solver for reaches.
- `network` — cascade assembly and aggregate-capability metrics.
- `optimizer` — MINLP/metaheuristic multi-objective search.
- `policy` — operating strategy generator and simulator.
- `economics` — NPV/lifecycle cost, risk.
- `mcda` — ranking and trade-off visualization (for the brief).
- `viz_report` — figures and document generation.

### 6.3 Candidate tooling (to be confirmed)
Python scientific stack (NumPy/Pandas/SciPy), optimization (Pyomo + solver,
OR-Tools), evolutionary optimization (pymoo), geospatial (GeoPandas/rasterio),
hydraulics (1D/2D solver of choice), plus reproducible notebook/pipeline tooling.
*(Tooling choice is a planning decision, not an executed step.)*

### 6.4 Milestone/dependency notes
- Steps 4 and 5 depend on step 3 (inflow scenarios) and step 1 (geometry/characteristics).
- Steps 6–7 depend on the validated cascade engine.
- Step 8 depends on all prior layers.
- Continuous integration of the assumption register and provenance at every step.

---

## 7. Validation Strategy

### 7.1 Evaluation metrics (planned)
- **Hydrology:** goodness-of-fit (e.g., RMSE, NSE, KGE), and extreme-value fit diagnostics.
- **Reservoir/cascade:** mass-balance closure error; simulated vs. documented lake-level
  behavior; flood-peak attenuation accuracy.
- **Performance:** water-supply **reliability, resilience, vulnerability (RRV)**; firm
  energy; energy/water shortfall frequency.
- **Optimization:** constraint satisfaction; Pareto-front spread and convergence;
  optimality-gap (for exact solvers) or stability (for metaheuristics).
- **Economics/MCDA:** cost-model plausibility; ranking stability under weight changes.

### 7.2 Validation methods (planned)
- **Split-sample** calibration/validation and **cross-validation** across decades.
- **Historical event replay:** reproduce documented flood and drought episodes as a
  stress test.
- **Benchmarking** against documented Kariba performance envelopes.
- **Conservation-law checks** and numerical convergence studies for hydraulic models.
- **Independent recomputation / expert review** of model outputs and rule curves.

### 7.3 Sensitivity & uncertainty analysis (planned)
- **Local (one-at-a-time)** screening of parameters.
- **Global (variance-based, e.g., Sobol / Morris)** sensitivity to identify dominant
  drivers.
- **Monte Carlo / ensemble** propagation of hydrological and cost uncertainty.
- **Scenario analysis:** climate shift, demand growth, cost escalation, discount-rate
  choice.
- **Robustness of the recommendation:** test whether the preferred N and placement remain
  preferred across scenarios, and report the regret of alternatives.

---

## 8. Expected Result Interpretation

This section describes how outputs **will** be read; it contains no findings.

- **D1 brief:** a two-page side-by-side comparison of Options 1–3 summarizing
  cost/benefit ranges and key risks; interpretation will emphasize that figures are
  planning-stage estimates with stated uncertainty.
- **Number & placement (D2):** expected in the form of a recommended N (within 10–20)
  and a siting scheme, presented with a Pareto trade-off (cost vs. protection/capacity)
  rather than a single point; multiple near-optimal layouts may be reported.
- **Flow-modulation strategy (D3):** expected as rule curves / release schedules that
  map reservoir state and season to release decisions, with the safety–cost trade-off
  made explicit.
- **Emergency playbook (D4):** expected as condition→action tables (forecast/threshold
  triggers) with justifications, covering both flood and prolonged-low-water cases.
- **Extreme-flow guidance (D5):** expected as discharge bands from maximum expected to
  minimum expected discharge, each with recommended operator actions.
- **Exposure restrictions (D6):** expected as a matrix of river locations × permitted
  durations under extreme conditions, derived from hydraulic/habitat reasoning.
- **Overall:** interpretation will stress conditionality on assumptions, the range of
  plausible outcomes, and the distinction between robust and fragile conclusions.

---

## 9. Limitations and Improvements

### 9.1 Anticipated limitations
- **Data scarcity/quality** on a large transboundary river; potential dependence on
  synthetic or regionalized hydrology.
- **Stationarity and climate change:** historical statistics may not represent the
  future; extreme events are under-sampled.
- **Hydraulic simplification:** 1D routing may miss local 2D effects (backwater,
  confluences, floodplain storage).
- **Neglected processes:** sediment transport, ecology, navigation, and social/
  resettlement impacts are only partially captured.
- **Economic uncertainty:** parametric cost functions and discount rate choices can
  dominate the ranking.
- **Transboundary/regulatory politics** simplified into constraints rather than modeled
  as negotiation.
- **Computational limits** may constrain the resolution of the joint siting/sizing
  optimization and the scenario ensemble size.

### 9.2 Planned improvements / extensions
- Enrich data through additional gauges, satellite altimetry, and remote sensing.
- Upgrade to 2D/3D hydraulic modeling at critical reaches and dam sites.
- Move to **stochastic/robust optimization** and real-options framing for staged
  investment.
- Quantify ecosystem services and environmental flows explicitly.
- Add sediment-management and reservoir-lifetime modules.
- Incorporate a transboundary negotiation/agent-based layer (Zambia, Zimbabwe,
  Mozambique).
- Couple with downscaled climate projections for long-horizon stress testing.
- Strengthen MCDA with participatory weighting and explicit value trade-offs.

---

### Appendix — Planning Checklist (self-audit for this draft)
- [x] Addresses both problem requirements (brief + detailed Option 3 analysis).
- [x] Covers number/placement recommendation approach, flow-modulation strategy,
      emergency guidance, extreme-flow band, and exposure restrictions.
- [x] Data plan provided despite empty staged dataset (acquisition defined).
- [x] Candidate methods, implementation roadmap, validation, limitations included.
- [x] No computations, no data analysis, no results, no final conclusions presented.
- [x] Future-oriented language used throughout.
