# MM-Bench 2015_A — Modeling Blueprint Draft

**Problem ID:** 2015_A
**Source:** MM-Bench 2015
**Document type:** Initial modeling plan (blueprint). This document is a roadmap only — it contains no solved results, no executed experiments, and no final conclusions.

---

## 1. Problem Background and Restatement

The world medical association has announced that a new medication could stop Ebola and cure patients whose disease is not advanced. The modeling task is to build a realistic, sensible, and useful model that supports the optimization of Ebola eradication (or at least control of the current strain).

The model must account for, at minimum:

- the spread of the disease (transmission dynamics),
- the quantity of medicine needed (demand forecasting),
- feasible delivery systems (how medicine reaches where it is needed),
- geographic locations of delivery (spatial distribution of need and logistics),
- the speed of manufacturing of the vaccine or drug (production capacity ramp-up),
- any other critical factors the team considers necessary.

**Restated objective (planning form):** Design a framework that, given an epidemic scenario, will determine an allocation and logistics strategy for a curative/stopping medication — deciding how much to produce, where to send it, how fast, and by which routes — in order to minimize disease burden and time-to-eradication under resource, production, and logistical constraints.

**Note on staged data:** The provided workspace `data/` directory contains no staged files, and the problem's dataset definition is empty (`dataset_path: []`, `dataset_description: {}`, `variable_description: {}`). Therefore the plan below treats data acquisition from authoritative public sources as an explicit subproblem of the workflow rather than relying on pre-staged inputs.

---

## 2. Objectives and Subproblems

### 2.1 Primary objective
Produce a decision-support model that recommends medicine production levels and geographic allocation/delivery scheduling that minimizes epidemic impact (e.g., cumulative infections/deaths and/or time to eradication) subject to manufacturing, budget, and logistics constraints.

### 2.2 Subproblems (planned decomposition)

1. **Epidemic dynamics subproblem** — Represent the transmission of Ebola across a set of affected regions and characterize how it responds to treatment availability (reduced infectious duration, reduced mortality, possible reduced transmission).
2. **Demand subproblem** — Forecast the quantity of medicine required over time and space (per region), including uncertainty.
3. **Supply / manufacturing subproblem** — Model the ramp-up of production capacity and the lead time to scale output; characterize cumulative supply as a function of time.
4. **Logistics / delivery subproblem** — Model feasible delivery routes, transport modes, capacities, costs, and travel/transit times between supply origins and demand locations.
5. **Geographic allocation subproblem** — Decide spatial distribution of limited drug doses so as to maximize marginal epidemic impact reduction.
6. **Integration / optimization subproblem** — Combine the above into a single objective with trade-offs (e.g., speed vs. coverage, equity vs. efficiency).
7. **Uncertainty / robustness subproblem** — Address parameter uncertainty (transmission rates, production yields, transport delays) and scenario stress-testing.

### 2.3 Deliverables (planned)
- A documented multi-stage modeling framework (epidemic + supply + logistics + optimization).
- A defined set of decision variables, parameters, and constraints.
- A reproducible implementation roadmap (module decomposition and data flow).
- A validation and sensitivity-analysis design.
- A scenario/result-interpretation scheme for stakeholders (policy-oriented reading of outputs).

---

## 3. Assumptions

The following are proposed working assumptions. Each will be revisited and validated (or relaxed) during later modeling stages.

### 3.1 Epidemiological assumptions
- **A1.** Population within each region will be treated as homogeneous and well-mixed (compartmental approximation), with possible later extension to metapopulation/network coupling between regions.
- **A2.** The medication is curative for non-advanced cases, reducing infectious duration and/or mortality for treated individuals (treatment effect to be parameterized).
- **A3.** Disease progression follows a standard staged structure (susceptible → exposed → infectious → removed/recovered/deceased), to be refined as needed.
- **Justification:** Standard for rapid-response planning when detailed individual contact data is unavailable.
- **Future validation:** Compare structural variants (SIR/SEIR vs. staged) and calibrate against historically reported outbreak trajectories.

### 3.2 Supply/production assumptions
- **A4.** Production capacity grows over time with a finite ramp rate; there is a fixed initial stock and a maximum achievable production rate.
- **A5.** Batch yields and production lead times are constant per scenario, with parametric uncertainty.
- **Future validation:** Stress-test against optimistic/pessimistic ramp scenarios.

### 3.3 Logistics assumptions
- **A6.** Delivery capacity per route is bounded (doses per trip), with finite transit times and possibly limited trip frequency.
- **A7.** A limited set of origin hubs and destination regions exists; cost is proportional to transported quantity and distance, with fixed per-trip costs.
- **Future validation:** Sensitivity analysis on transit delays and capacity limits.

### 3.4 Behavioral/policy assumptions
- **A8.** Non-pharmaceutical interventions (isolation, safe burial, contact tracing) act as background modifiers and may be represented as scenario parameters rather than decision variables in the initial draft.
- **A9.** Population and geographic structure are stable over the modeled horizon.

### 3.5 Assumptions explicitly flagged for scrutiny
- Homogeneous mixing may overstate/understate spread in rural vs. urban settings.
- The "cure if not advanced" claim implies a staging/triage mechanism that may require its own submodel (diagnosis timing).
- Data availability from public sources may be coarse-grained (country/region level) rather than facility-level.

---

## 4. Data Processing Plan

Because no data is staged, the plan distinguishes **acquisition**, **preprocessing**, **feature construction**, and **data usage**.

### 4.1 Data acquisition (planned sources)
- **Epidemiological counts:** Historical outbreak case/death time series by region (e.g., WHO situation reports, CDC, national health ministries).
- **Geographic data:** Region boundaries, centroids, population estimates (e.g., public GIS/administrative datasets).
- **Transport/logistics data:** Road/air network connectivity, approximate distances/travel times between candidate hubs and regions.
- **Manufacturing parameters:** Literature-derived production rates, dose requirements per patient, and ramp timelines.
- **Socioeconomic/health-system covariates:** Healthcare capacity, population density, urbanization (optional covariates).

### 4.2 Preprocessing (planned)
- Standardize time units (weeks) and geographic units (a fixed region set) across all tables.
- Reconcile reporting artifacts (missing reports, late reporting, cumulative-vs-incident counts).
- Smooth/annotate series for reporting noise without altering the underlying trajectory.
- Build a consistent region index and join all datasets on that index and on time.

### 4.3 Feature construction (planned)
- Derived epidemiological quantities (incidence, doubling-time proxies, effective reproductive number estimates) as model inputs for calibration targets — **not** as final results.
- Demand features: projected doses needed per region per period (from a demand model, to be built).
- Logistics features: distance/time matrices, per-route capacity, cost coefficients.
- Supply features: cumulative supply curves by scenario.

### 4.4 Data usage strategy (planned)
- **Calibration set:** historical outbreak window used to fit epidemic parameters.
- **Scenario generation:** alternative future trajectories under parameter uncertainty (not a single point forecast).
- **Constraint set:** production and logistics limits encoded as data-driven bounds.
- **Traceability:** every parameter will be tagged with source, unit, and uncertainty range.

---

## 5. Candidate Model Framework

The plan is to build a **coupled multi-layer framework**: disease dynamics → demand → supply → logistics → allocation, wrapped by optimization and uncertainty layers.

### 5.1 Layer 1 — Epidemic dynamics
- **Candidate A:** Compartmental ODE models (SIR/SEIR variants) with treatment-modified rates.
- **Candidate B:** Staged/clinical-progression models distinguishing non-advanced vs. advanced cases.
- **Candidate C (extension):** Metapopulation / multi-region coupled models for spatial spread.
- **Variables:** compartment sizes per region over time; transmission, progression, recovery, mortality rates; treatment coverage.
- **Mathematical ideas:** nonlinear ODE systems; basic/effective reproduction number; parameter estimation via least squares/likelihood.
- **Advantages / limitations:** transparent and parameter-light (A) vs. richer but data-hungry (B/C).

### 5.2 Layer 2 — Demand and supply
- **Candidate:** Time-varying demand derived from the epidemic layer; supply modeled as a ramp-limited cumulative curve (with optional stochastic yields).
- **Mathematical ideas:** differential equations or difference equations for supply; queueing/backlog formulations for unmet demand.
- **Advantages / limitations:** simple to communicate; may smooth over real production lumpiness.

### 5.3 Layer 3 — Logistics and geography
- **Candidate:** Network flow on a graph (hubs → regions) with capacity and cost edges.
- **Mathematical ideas:** min-cost flow / transportation problem / vehicle-routing-style scheduling; time-expanded networks for scheduling over weeks.
- **Advantages / limitations:** directly encodes geography and speed; grows complex with fine resolution.

### 5.4 Layer 4 — Allocation and optimization
- **Candidate:** Constrained optimization minimizing a weighted combination of epidemic burden and time-to-control, subject to supply and logistics limits.
- **Candidate methods:** linear/integer programming, nonlinear programming, and (for stochastic versions) stochastic programming or robust optimization.
- **Candidate heuristics:** greedy marginal-impact allocation, priority-index policies for interpretability.
- **Decision variables:** production quantities over time; doses shipped per route per period; allocation shares per region.
- **Constraints:** production capacity/ramp, transport capacity, budget, timing/delivery delays, coverage floor (equity option).

### 5.5 Layer 5 — Uncertainty and robustness
- **Candidate:** scenario ensembles, Monte Carlo simulation, and robust/stochastic optimization to select strategies that perform acceptably across futures.
- **Key ideas:** parametric sensitivity, worst-case stress tests, value-of-information style reasoning (planned, not executed).

### 5.6 Integration shape (planned)
A closed loop in which allocation strategies feed back into epidemic outcomes, which in turn update demand — iterated within the optimization to evaluate candidate policies.

---

## 6. Implementation Roadmap

### 6.1 Proposed modules
1. `data_ingest` — acquisition and normalization of epidemiological, geographic, logistics, and manufacturing data.
2. `epi_model` — disease dynamics simulator/calibrator.
3. `demand_supply` — demand projection and supply ramp model.
4. `logistics_network` — graph construction, distances/times, capacities, costs.
5. `optimizer` — allocation/production optimization (LP/MILP/NLP + heuristics).
6. `uncertainty` — scenario generation, Monte Carlo, robust evaluation.
7. `reporting` — structured outputs, plots, and policy summaries (to be produced only in the later solving stage).
8. `pipeline_driver` — orchestrates the workflow end-to-end.

### 6.2 Workflow (planned sequence)
1. Define geographic region set and time horizon.
2. Acquire and normalize data; document assumptions and units.
3. Build and calibrate the epidemic layer; produce scenario trajectories.
4. Derive demand from scenarios; construct supply curves.
5. Build logistics network with capacities/costs.
6. Formulate and solve the allocation optimization under constraints.
7. Run uncertainty/robustness analyses across scenarios.
8. Interpret, summarize, and communicate policy options.

### 6.3 Algorithm choices (candidate)
- Parameter estimation: gradient-based / derivative-free optimization, or Bayesian methods for uncertainty quantification.
- ODE integration: adaptive-step solvers.
- Optimization: LP/MILP solvers for linear formulations; metaheuristics if the formulation becomes nonconvex.
- Simulation: Monte Carlo for uncertainty propagation.

### 6.4 Engineering considerations (planned)
- Reproducibility: fixed seeds, config-driven parameters, logged runs.
- Modularity: each layer independently testable.
- Scalability: start coarse (region-level, weekly), refine only if justified.

---

## 7. Validation Strategy

### 7.1 Evaluation metrics (planned)
- **Epidemic fit:** agreement between simulated and observed trajectories (error metrics to be chosen, e.g., RMSE-style or profile-likelihood measures).
- **Policy performance:** cumulative infections/averted cases, time to control/eradication, unmet demand, cost per averted case.
- **Logistics performance:** delivery timeliness, coverage achieved, capacity utilization.
- **Equity metrics (optional):** distribution of coverage across regions.

### 7.2 Validation methods (planned)
- **Internal validation:** held-out historical periods for calibration targets; cross-scenario consistency checks.
- **Structural validation:** compare alternative model structures (e.g., SEIR vs. staged) to check robustness of conclusions.
- **Face validity:** review of parameters and behavior with domain plausibility ranges.
- **Backtesting:** replay a past outbreak period and assess whether the model's recommendations would have been reasonable given information available at the time (design only).

### 7.3 Sensitivity and robustness analysis (planned)
- **One-at-a-time** parameter sweeps for key transmission, production, and transport parameters.
- **Global sensitivity** (e.g., variance-based methods) to rank influential parameters.
- **Scenario/ensemble analysis** for worst-case and best-case futures.
- **Constraint stress tests:** reduced budget, slower production, transport disruption.

### 7.4 Success criteria (planned)
- Model behavior consistent with epidemiological plausibility across scenarios.
- Optimization outputs stable under reasonable parameter perturbations.
- Recommendations that remain defensible under uncertainty.

---

## 8. Expected Result Interpretation

The later solving stage is expected to yield, and this plan anticipates interpreting:

- **Production timelines:** how fast medicine must be produced to matter, and where the binding constraint lies (manufacturing vs. logistics vs. allocation).
- **Allocation maps/schedules:** which regions would receive doses when, and why, under the chosen objective.
- **Trade-off curves:** e.g., coverage vs. speed, efficiency vs. equity, and the marginal value of additional manufacturing capacity or transport capacity.
- **Bottleneck diagnostics:** identification of the limiting factor in each scenario.
- **Policy implications:** qualitative guidance on priorities and on which uncertainties most affect decisions.

Interpretation guidance (planned): results should be read as **conditional on assumptions and scenarios**, not as unconditional forecasts. Reporting will emphasize ranges and trade-offs rather than single headline numbers.

---

## 9. Limitations and Improvements

### 9.1 Anticipated limitations
- **Data scarcity/quality:** no staged data; reliance on coarse public data introduces measurement and reporting bias.
- **Homogeneous-mixing simplification:** may misrepresent local outbreak clustering and superspreading.
- **Static logistics:** network and capacities may be treated as fixed, ignoring dynamic disruptions.
- **Model coupling complexity:** integrating epi + supply + logistics + optimization raises parameter and computational burden.
- **Behavioral factors:** compliance, healthcare-seeking behavior, and intervention effectiveness are hard to model and may be treated as exogenous.
- **Single-strain assumption:** "current strain" framing may not capture mutation/evolution.

### 9.2 Planned improvements
- Refine spatial resolution and move toward metapopulation/agent-based extension where data allows.
- Add stochastic and robust optimization formulations for decision-making under deep uncertainty.
- Incorporate dynamic logistics with disruption scenarios.
- Add triage/diagnosis-timing submodel to reflect "cure if not advanced."
- Include equity/ethics constraints explicitly as policy options.
- Perform systematic uncertainty quantification and value-of-information analysis.

---

## Planning Checklist (self-verification for this document)

- [x] Contains only planning/roadmap content.
- [x] No computed results, no completed analysis, no executed experiments, no final conclusions.
- [x] All nine required sections present.
- [x] Future-oriented language used throughout.
- [x] Uses only the native problem requirements (Ebola eradication model) and notes workspace data state.
