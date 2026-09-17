# Charge! — Modeling Blueprint (Initial Draft)

**Problem ID:** `2019_Charge!`  |  **Source:** HiMCM 2019
**Document type:** Planning blueprint — roadmap only. No data analysis, no computation, no results, no conclusions are included here.

---

## 1. Problem Background and Restatement

Mobile electronic devices — from phones and laptops to electric vehicles (EVs) — are increasingly charged in public places (airports, railway terminals, schools, libraries, malls, coffee shops, offices). Some sites charge a fee; many offer charging "for free." The core question is: **what is the impact of public "plug-in" charging, and who ultimately bears the cost?**

The problem decomposes into five requested deliverables:

1. Describe how public charging energy consumption has evolved and will evolve, and identify the resulting impacts on / requirements of public places.
2. Build a model of the resulting costs of increased energy and demand on public places, discuss the extent of those costs, and explain how they are paid.
3. Discuss how the model changes across venue types (school, cafe, airport, mall, etc.).
4. Propose initiatives to reduce the cost of this increased energy usage, and describe how each would adjust the cost model.
5. Produce a one-page school-newspaper article communicating findings and recommendations.

**Framing to be adopted (to be confirmed during modeling):** treat each public venue as a *cost-bearing entity* that absorbs electricity, infrastructure, and maintenance costs while the direct benefit (charging) is frequently delivered free or below cost. The modeling effort will therefore focus on **(a) demand-side energy flows**, **(b) cost transfer and recovery mechanisms**, and **(c) venue-type differentiation and mitigation strategies**. Deliverable 5 is a communication artifact derived from the model, not an independent quantitative task.

---

## 2. Objectives and Subproblems

**Primary objective.** Construct a modeling framework that quantifies and explains the cost burden of public-device charging on public places, how that burden is transferred/priced, and how it varies by venue type and under mitigation initiatives.

**Subproblems (each to be modeled in a later stage):**

| # | Subproblem | Modeling intent | Linked deliverable |
|---|-----------|-----------------|--------------------|
| S1 | Trend characterization of public charging demand | Describe/forecast growth of device ownership and public charging use over recent and coming years | Problem part 1 |
| S2 | Impact & requirement identification | Translate demand into physical impacts (load, peak, infrastructure, safety) and requirements (outlets, capacity, codes) | Problem part 1 |
| S3 | Cost model of increased demand/energy | Build a cost function combining energy cost, demand charges, infrastructure capex, O&M, and wear | Problem part 2 |
| S4 | Cost-transfer / who-pays analysis | Model how costs are allocated across venue, customers, taxpayers, vendors, sponsors | Problem part 2 |
| S5 | Venue-type generalization | Parameterize the cost model by venue archetypes and compare | Problem part 3 |
| S6 | Mitigation initiative evaluation | Model cost deltas under candidate initiatives (metering, fees, solar, load control, etc.) | Problem part 4 |
| S7 | Communication synthesis | Translate model outputs into a lay-reader one-pager | Problem part 5 |

**Deliverables.** A documented cost model, a venue-type comparison framework, an initiative-adjustment framework, and a communications draft — all as plans now, results later.

---

## 3. Assumptions

Assumptions will be grouped and each will carry a justification and a future validation path. Proposed working assumptions:

**A. System boundary and scope**
- A1. The unit of analysis is a single public venue (building/site) over a representative period (e.g., annualized), with daily/seasonal resolution available as needed.
- A2. Charging services considered include portable devices (USB outlets) and, where relevant, EV charging; heavy industrial or fleet depots are out of scope unless the venue is a transport hub.
- *Justification:* keeps the model tractable and comparable across venues; *Validation:* refine boundary after data reconnaissance, compare against per-site utility bills if available.

**B. Demand and behavior**
- A3. Per-device energy draw and charging duration are representable by distributions (not single constants).
- A4. Usage intensity scales with venue footfall, dwell time, and device ownership; "free" charging induces additional (induced) usage.
- A5. Occupancy/footfall patterns are periodic (daily/weekly/seasonal) and can be represented by profiles.
- *Justification:* avoids over-precise point estimates in absence of device-level data; *Validation:* stress-test against published plug-load and EV-charging studies.

**C. Cost and tariff structure**
- A6. Electricity cost follows a tariff structure with volumetric (per-kWh) and capacity (demand) components; demand charges exist where applicable.
- A7. Infrastructure costs (outlets, stations, wiring, upgrades) are capitalized and amortized; maintenance is a recurring fraction.
- A8. Prices and tariffs are exogenous inputs (modeled with scenario ranges), not strategic decisions of the venue.
- *Justification:* reflects typical commercial tariffs; *Validation:* compare to regional tariff schedules during data collection.

**D. Attribution and payment**
- A9. Costs may be borne by the venue, embedded into product/service prices, covered by public funds, recouped via fees, or offset by sponsors/partners — modeled as allocation shares.
- A10. Where charging is "free," the cost is internalized somewhere in the value chain; the model will trace this explicitly.
- *Justification:* directly answers "who pays"; *Validation:* sensitivity of conclusions to allocation shares.

**E. Temporality and evolution**
- A11. Device penetration, EV adoption, and charging expectations evolve over time; trend/forecast components are scenario-based rather than deterministic.
- *Justification:* problem explicitly asks about change over years; *Validation:* bounded by adopted scenario ranges.

Each assumption will be logged in an assumptions register with: statement, rationale, impact if violated, and test.

---

## 4. Data Processing Plan

**Note on provided data.** The workspace `data/` directory is currently empty — no dataset has been supplied with this statement. The data plan therefore covers (i) reconnaissance of anything later provided, and (ii) a structured public-data collection strategy, all to be executed in a later *solving* stage, not now.

**4.1 Data requirements (by subproblem)**
- *Demand drivers:* device-ownership penetration rates, footfall/occupancy for venue archetypes, dwell times, EV adoption rates.
- *Energy parameters:* per-device/per-station power draw, charging duration distributions, utilization rates for public charging.
- *Cost parameters:* electricity tariffs (energy + demand), station hardware costs, installation/wiring costs, O&M rates, equipment lifetime, discount rates.
- *Attribution parameters:* current pricing policies (free/fee/subscription), funding sources, sponsorship models.
- *Trend inputs:* historical adoption and charging-usage growth series where available.

**4.2 Sourcing strategy (planned)**
- Public/national statistics, energy-information agency data, utility tariff filings, EV-charging network statistics, industry plug-load studies, peer-reviewed literature, venue operational benchmarks.
- Where primary data are unavailable, use expert-elicited ranges and clearly flagged synthetic/assumed parameter ranges (documented, not hidden).
- Maintain a source table with: source, metric, vintage, geography, reliability rating.

**4.3 Preprocessing (planned)**
- Unit harmonization (W/kW, kWh, currency, per-venue vs per-user normalization).
- Time-index alignment (hourly/daily/seasonal) and profile construction.
- Missing-data treatment policy (interpolation rules, exclusion thresholds, range-based imputation).
- Outlier/mismatch checks across sources; reconciliation of conflicting figures into ranges.
- Currency/year normalization using a chosen base year and discounting convention.

**4.4 Feature construction (planned)**
- Derived features: energy per visit, energy per device, cost per kWh delivered, peak-to-average ratio, cost-per-user, recovery ratio (fees vs cost).
- Venue archetype features: footfall band, dwell-time band, tariff class, EV relevance flag.
- Scenario features: adoption level, tariff scenario, mitigation on/off.

**4.5 Data usage strategy (planned)**
- Deterministic core from well-sourced parameters; uncertainty bands from ranges.
- Explicit separation of *assumption inputs* vs *measured inputs* so validation can target each.
- Hold-out/backtest split for any trend or forecast component (see §7).
- All inputs versioned and traceable to the source table.

---

## 5. Candidate Model Framework

The framework will be modular: an energy/demand core, a cost layer, an attribution layer, and a scenario controller.

**5.1 Candidate models (by component)**

- *Demand/energy sub-model (S1–S2, S5):*
  - Bottom-up engineering estimate: (number of devices/stations) × (usage intensity) × (power × duration).
  - Stochastic process view (e.g., arrival/queueing-style representation of simultaneous charging) to capture peak load at outlets/stations.
  - Hybrid: deterministic baseline profile + stochastic peak overlay.
  - Candidate quantitative ideas: probability/queueing reasoning for concurrency, time-series decomposition for profiles, growth/trend extrapolation for adoption.

- *Cost sub-model (S3):* a cost function structured as
  `Total Cost = Energy cost + Demand/capacity cost + amortized infrastructure capex + O&M + ancillary (safety/compliance)`.
  - Each term will be parameterized per venue archetype; demand charges will be modeled as a function of peak load.
  - Candidate ideas: linear/non-linear cost decomposition, piecewise tariffs, life-cycle costing with amortization.

- *Attribution / who-pays sub-model (S4):* an allocation model expressing cost shares across venue, users, public funds, sponsors.
  - Candidate ideas: cost-allocation ratios, simple equilibrium/pricing reasoning, pass-through formulations, or a small game-theoretic view of incentives (to be assessed for tractability).

- *Venue-type differentiation (S5):* parameter sets over archetypes (school, cafe, airport, mall, library, office, transit terminal) with shared functional form and archetype-specific parameters.

- *Mitigation impact (S6):* scenario/delta model where each initiative modifies one or more cost terms or demand parameters (e.g., demand reduction, peak shifting, cost substitution, recovery increase).

**5.2 Key variables (to be formalized later)**
- Endogenous: total cost, peak load, energy delivered, recovery ratio, net venue burden.
- Exogenous: footfall, dwell time, device penetration, EV adoption, tariffs, hardware costs, discount rate.
- Scenario/decision: pricing policy, mitigation adoption level, infrastructure sizing.

**5.3 Advantages / limitations of the candidate framework**
- *Advantages:* transparent, decomposable, interpretable, easy to parameterize for multiple venues and scenarios; supports sensitivity analysis.
- *Limitations:* data-intensive; relies on assumptions where primary data are absent; may under-represent behavioral feedback and long-run market dynamics; attribution choices are inherently normative.
- *Mitigation:* uncertainty ranges, scenario analysis, and clear assumption logging.

---

## 6. Implementation Roadmap

Planned implementation stages (to be executed later; no code is written now):

1. **Scoping & assumption register** — finalize boundary, archetypes, and assumptions.
2. **Parameter & source build** — assemble the source table and parameter ranges (deterministic + bounds).
3. **Demand/energy module** — implement per-venue energy and peak-load estimation with profiles and stochastic overlay.
4. **Cost module** — implement cost decomposition and per-archetype parameterization.
5. **Attribution module** — implement cost-share/allocation logic.
6. **Scenario controller** — implement adoption/tariff/mitigation scenario switches.
7. **Venue comparison harness** — run shared functional form across archetypes and compare structures.
8. **Sensitivity & validation harness** — automate sensitivity runs and backtests.
9. **Synthesis & write-up** — produce figures/tables and the one-page article draft (during solving, not now).

**Required modules (planned):**
- `data_ingest` (sources, cleaning, harmonization)
- `params` (parameter registry, scenario definitions)
- `demand_model` (energy/peak estimation)
- `cost_model` (cost decomposition)
- `attribution_model` (who-pays allocation)
- `scenario_engine` (initiative/adoption/tariff switches)
- `venue_registry` (archetype parameter sets)
- `analysis` (aggregation, comparison)
- `sensitivity` (one-at-a-time, range, and scenario sweeps)
- `viz` (plots/tables for the report; solving stage only)

**Workflow:** scope → parameters/sources → demand → cost → attribution → scenarios → venue comparison → sensitivity → synthesis. Each stage gated by a checklist (inputs traceable, assumptions logged, no hidden constants).

---

## 7. Validation Strategy

**7.1 Evaluation metrics (planned)**
- Internal consistency: dimensional/unit checks, conservation checks on energy delivered vs consumed.
- Plausibility checks: per-venue cost-per-user and cost-per-kWh within literature ranges.
- Backtest accuracy for any trend/forecast component (error metrics to be chosen, e.g., relative error over held-out periods).
- Robustness metrics: sensitivity indices of outputs to key parameters.
- Comparative validity: archetype rankings stable under reasonable parameter variation.

**7.2 Validation methods (planned)**
- *Sanity/limit testing:* degenerate cases (zero footfall, zero charging, infinite tariff) should produce expected behavior.
- *Cross-source triangulation:* compare model-implied parameters against independent public sources.
- *Backtesting:* where historical series exist, calibrate on a training window and evaluate on a hold-out window.
- *Expert/peer review:* check assumption plausibility and cost structure against domain literature.
- *Narrative consistency:* ensure the venue comparison and initiative analysis follow logically from the model structure.

**7.3 Sensitivity & uncertainty analysis (planned)**
- One-at-a-time parameter sweeps to rank influential inputs.
- Range/scenario analysis for adoption, tariffs, dwell time, and cost parameters.
- Monte Carlo-style sampling over parameter ranges to produce cost/attribution distributions (solving stage).
- Stress scenarios: rapid EV growth, high tariff volatility, universal free charging vs universal metered.
- Review of how conclusions change (or hold) across venue archetypes and mitigation combinations.

---

## 8. Expected Result Interpretation

*Planning-level guidance on how future outputs should be read — not results.*

- Outputs will be interpreted as **cost ranges and comparative structures**, not precise point predictions, given assumption-driven inputs.
- The "who pays" analysis will be presented as **allocation shares under stated policies**, acknowledging normative choices.
- Venue-type differences will be framed as **structural and parameter-driven**, showing where cost burden is inherently heavier (e.g., high-dwell, high-footfall hubs vs small low-capacity sites).
- Initiative analysis will be framed as **relative cost adjustments** with associated assumptions, not guarantees.
- Trend discussion will be **scenario-based**, communicating direction and sensitivity rather than single forecasts.
- The newspaper article will translate the model into accessible "what it means for our community" language, using ranges and clear caveats.

---

## 9. Limitations and Improvements

**Anticipated limitations**
- Reliance on public/secondary data and expert ranges; sparse device-level measurement.
- Behavioral feedback (induced usage, behavioral changes under fees) simplified.
- Attribution choices are normative and may shift conclusions.
- Long-run technological change (efficiency gains, wireless charging, building codes) only coarsely represented.
- Single-venue abstraction may miss system-level (grid, city) interactions.

**Planned improvements**
- Refine parameter ranges with better sources during the solving stage.
- Add behavioral/elasticity components if data permit.
- Extend to system-level interactions (grid/utility perspective) if time allows.
- Formalize uncertainty propagation more rigorously (full distributional analysis).
- Validate against at least one real venue case if data can be obtained.
- Iterate the communication draft against model outputs for accuracy and clarity.

---

*End of blueprint. This document is a modeling roadmap only: it defines workflow, assumptions, candidate methods, data handling, implementation, and validation plans. No data was analyzed, no code was run, and no results or final conclusions are stated.*
