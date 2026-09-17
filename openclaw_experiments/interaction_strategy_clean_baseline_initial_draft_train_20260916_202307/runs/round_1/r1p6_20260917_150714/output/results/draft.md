# Aviation Baggage Screening Strategies — Modeling Blueprint (Initial Draft)

**Problem ID:** `2003_Aviation_Baggage_Screening`
**Source:** ICM 2003 — *Aviation Baggage Screening Strategies: To Screen or Not to Screen, that is the Question*
**Document type:** Modeling plan draft (roadmap only). This document intentionally contains **no computed results, no fitted models, no executed experiments, and no final conclusions**.

---

## 1. Problem Background and Restatement

The Transportation Security Administration (TSA) is planning to mandate **100% screening of all checked baggage** at 429 passenger airports using Explosive Detection Systems (EDS) based on computed tomography (CT). The operational and economic context to be incorporated in the modeling includes:

- EDS units operate approximately **92% of the time** (availability/reliability factor).
- Each EDS can process roughly **160–210 bags per hour** (throughput range).
- Each unit costs nearly **$1 million**, plus installation costs of **$100,000 at Airport A** and **$80,000 at Airport B**.
- Production capacity is limited, so deployment must be prioritized and phased.
- Emerging detection technologies may later offer cheaper or more capable alternatives.

The problem is framed around two specific airports (Airport A and Airport B) but must ultimately generalize to a **regional scale (193 airports in the Midwest Region)** and to **national implementation**.

The planning problem therefore sits at the intersection of:

1. **Capacity planning / resource sizing** (how many machines are required to meet a throughput mandate under stochastic demand and reliability constraints).
2. **Scheduling / queueing** (how to spread departure demand across peak hours so that screening capacity is not exceeded).
3. **Cost-effectiveness analysis** (EDS alone vs. hybrid EDS + ETD screening policies).
4. **Policy recommendation and generalization** (transferring a calibrated model from two airports to a national network).

**Restatement in planning terms:** We must design a modeling framework that will later (a) size the EDS fleet needed at Airports A and B, (b) schedule peak-hour departures to match screening capacity, (c) evaluate adding Explosive Trace Detection (ETD) machines, and (d) generalize results to a wider airport network — all under stated uncertainty in occupancy, baggage behavior, and arrival timing.

The only quantitative input provided up front is **Table 1** (peak-hour flight departures by flight type, seats per flight, and counts at Airports A and B), supplemented by occupancy/arrival/baggage assumptions in the Technical Information Sheet (TIS).

---

## 2. Objectives and Subproblems

The eventual study is expected to address seven linked subproblems. For each, this blueprint states the **planning objective**, not a solution.

| # | Subproblem | Planning objective (to be modeled later) |
|---|------------|------------------------------------------|
| 1 | **EDS requirement model** | Determine the number of EDS units needed at Airports A & B given peak-hour passenger/bag volumes, occupancy assumptions, and reliability. |
| 2 | **Position paper on security objectives & constraints** | Formalize the security objectives and operational/economic constraints facing airlines, grounded in Table 1 flight data. |
| 3 | **Departure scheduling model** | Build a model to reschedule peak-hour departures so screening demand stays within feasible capacity. |
| 4 | **Recommendations to Mr. Sheldon & airlines** | Translate model outputs into actionable guidance for peak-hour screening policy. |
| 5 | **National impact memo** | Describe how the two-airport model can be adapted to the 193 Midwest airports and scaled nationally. |
| 6 | **ETD-augmented model** | Extend the EDS framework to include ETD machines; size the ETD fleet, assess schedule impacts, and evaluate cost-effectiveness. |
| 7 | **Future research recommendations** | Identify how technology/cost/accuracy/speed/reliability changes affect the system, and recommend STEM research directions. |

**Cross-cutting deliverables (planning-level):**

- A single coherent, parameterized **capacity–demand model** reusable across subproblems.
- A **cost model** that separates capital (unit + installation) from operational and downstream (delay) costs.
- A **schedule optimizer** operating on the same demand model.
- A **generalization framework** with explicit scaling assumptions for network rollout.

**Explicit non-goals for this draft:** choosing final parameters, reporting numeric machine counts, or delivering schedules/results.

---

## 3. Assumptions

Assumptions are grouped by role, with proposed justification and a planned validation approach. All will be treated as **parameterizable** wherever feasible.

### 3.1 Demand-side assumptions

- **A1 — Flight-level capacity → passenger count.** Passenger counts will be derived from *seats per flight × assumed occupancy rate*, using the TIS occupancy bands:
  - ≤85 seats: 70%–100% occupancy.
  - 128–215 seats: 60%–100%.
  - 350 seats: 50%–100%.
  - *Justification:* TIS provides only ranges; a distributional or scenario treatment is needed rather than a point value.
  - *Planned validation:* Compare deterministic mid-range vs. distributional (low/high) scenarios for sensitivity.

- **A2 — Baggage-per-passenger distribution.** 20% of passengers check no bag, 20% check one bag, 60% check two bags.
  - *Justification:* Stated directly in TIS.
  - *Planned validation:* Re-derive expected bags/passenger and test alternate distributions in sensitivity analysis.

- **A3 — Peak-hour interpretation.** Table 1 represents departures **within a single peak hour**, and all associated passengers must be screened within that same window (worst-case), unless the scheduling model redistributes them.
  - *Justification:* The scenario defines peak-hour departure volumes; a "screen everything before departure" rule implies a tight screening window.
  - *Planned validation:* Re-run under an extended screening window (e.g., 2 hours) to test sensitivity.

- **A4 — Passenger arrival timing.** Passengers will be modeled as arriving between 45 minutes and 2 hours before departure; the screening demand curve is therefore spread, not instantaneous.
  - *Justification:* TIS states this range.
  - *Planned validation:* Compare uniform vs. peaked arrival profiles.

- **A5 — Transfer/connecting and crew bags** are either negligible or folded into the per-passenger baggage rate.
  - *Justification:* Not specified; a simplifying exclusion is needed.
  - *Planned validation:* Stress-test via an added fractional "extra bags" parameter.

### 3.2 Capacity-side assumptions

- **A6 — EDS throughput.** Each unit processes a value within 160–210 bags/hour; the model will treat throughput as a parameter (lower bound = conservative sizing).
  - *Planned validation:* Sensitivity across the 160–210 range.

- **A7 — Reliability/availability.** EDS availability ≈ 92%, so effective capacity = nominal throughput × 0.92 (or an explicit up/down stochastic process).
  - *Planned validation:* Compare derating factor vs. Markov up/down availability model.

- **A8 — No batching shortcuts / 100% screening.** Every checked bag must pass EDS; no exemption by flight type or carrier.
  - *Justification:* Federal 100% mandate.

- **A9 — Cost structure.** Capital cost = unit cost (≈$1M) + installation ($100K at A, $80K at B); operational costs (staffing, maintenance, downtime) will be parameterized.
  - *Planned validation:* Vary unit/installation/operational cost assumptions in a cost–benefit sweep.

### 3.3 Modeling-scope assumptions

- **A10 — Independence of airports** for the two-site analysis; network-level interactions (shared production capacity) handled later in the national-scaling subproblem.
- **A11 — Steady-state vs. peak-hour focus.** Primary focus is the peak hour; off-peak behavior will be handled by a capacity-utilization ratio.
- **A12 — ETD role.** ETD will be modeled as a secondary/alarm-resolution or supplemental screening stage (exact role to be decided in the ETD subproblem).

> **Note on assumption risk:** A1, A3, A4, and A7 are the highest-leverage assumptions. The validation plan (§7) assigns them explicit sensitivity and stress-testing treatment.

---

## 4. Data Processing Plan

### 4.1 Data sources

- **Primary structured input:** Table 1 (flight types 1–8, seats per flight, departure counts at Airports A & B).
- **Parameter blocks from TIS:** occupancy bands, baggage distribution, arrival-time window, EDS availability/throughput, installation costs.
- **No external data required initially**, but the plan should allow optional calibration data (real airport throughput, delay statistics) if available.

### 4.2 Preprocessing plan (to be executed in the modeling phase, not now)

1. **Encode Table 1** into a tidy structure: `(flight_type, seats, count_A, count_B)`.
2. **Derive derived quantities conceptually:**
   - Expected passengers per flight type = seats × representative occupancy.
   - Expected checked bags per flight type = passengers × expected bags/passenger (from A2).
   - Aggregate peak-hour bags per airport = Σ over flight types (count × bags/type).
3. **Define scenario grids** for occupancy (low/central/high) rather than committing to a single number.
4. **Construct arrival-time demand profiles** over the screening window using A4 (e.g., piecewise-uniform or triangular kernels).
5. **QC checks to schedule for the modeling phase:** unit consistency, monotonicity of demand in seats, reconciliation of total flights vs. counts.

### 4.3 Feature / variable construction

- **Demand features:** seats, occupancy, passengers, bags/passenger, bags per flight type, peak-hour bag load per airport, arrival-rate function.
- **Capacity features:** machines available, throughput (bags/hr), availability, effective capacity, utilization ratio.
- **Cost features:** unit + installation capital, operational cost, delay/queue penalty, ETD cost.
- **Schedule features:** departure times (decision), inter-departure spacing, load-balancing index.

### 4.4 Data usage strategy

- Use Table 1 **as the fixed demand backbone**; treat TIS quantities as **parameters/distributions**, not constants.
- Reserve a portion of the assumption space for **calibration-free scenario exploration** (since no ground-truth labels exist).
- Keep all raw and derived data transforms **documented and reproducible** for the eventual write-up.

---

## 5. Candidate Model Framework

The framework should be **modular**: a shared demand engine feeding three model families (sizing, scheduling, cost), later extended for ETD and network scaling.

### 5.1 Module A — Demand generation model

- **Idea:** Map flight schedule → expected baggage load per unit time.
- **Candidate methods:**
  - Deterministic expected-value model (seats × occupancy × bags/passenger).
  - Scenario/envelope model (low/central/high occupancy).
  - Stochastic arrival model (arrival-time distribution convolved with bag counts).
- **Advantages:** Simple, transparent, directly tied to Table 1.
- **Limitations:** Ignores correlations (e.g., full flights with many bags) and day-to-day variability unless extended.

### 5.2 Module B — EDS capacity-sizing model

- **Idea:** Convert peak-hour bag load into required machine count under reliability and throughput constraints.
- **Candidate methods:**
  - **Deterministic sizing:** required machines = ceil(peak bag load ÷ effective hourly capacity).
  - **Stochastic/queueing sizing:** M/M/c- or M/G/c-style screening queue to capture waiting and utilization; or a fluid/deterministic-capacity model with reliability derating.
  - **Reliability-aware models:** up/down (Markov) availability for machines, or a binomial derating factor.
- **Key variables:** number of machines (decision), effective capacity, arrival rate, service rate, availability.
- **Advantages:** Direct answer to Subproblem 1.
- **Limitations:** Queueing models require distributional assumptions; deterministic models may under-size under variability.

### 5.3 Module C — Departure scheduling model

- **Idea:** Choose departure times (or allowed shifts) to flatten screening demand across the peak window.
- **Candidate methods:**
  - **Optimization:** integer/mixed-integer program minimizing peak load, delay cost, or machine count subject to capacity and airline constraints.
  - **Load-balancing / smoothing:** heuristic redistribution of departures within an allowed shift window.
  - **Simulation:** discrete-event model of the screening process to test schedules under stochastic arrivals.
- **Key variables:** departure time per flight (decision), allowed shift bounds, capacity per slot, delay penalty.
- **Advantages:** Turns capacity constraints into an actionable schedule.
- **Limitations:** Airline operational constraints and fairness/turnaround limits must be added.

### 5.4 Module D — Cost-effectiveness model

- **Idea:** Compare policies (EDS-only vs. EDS+ETD, more machines vs. schedule smoothing) on total cost.
- **Candidate methods:**
  - Life-cycle cost model (capital + installation + operations + delay).
  - Break-even / trade-off analysis between capital and scheduling delay.
  - Multi-criteria scoring (security performance vs. cost vs. feasibility).
- **Variables:** machine counts per type, cost parameters, delay costs, screening accuracy/throughput.
- **Advantages:** Answers Subproblem 6 (ETD) and supports Subproblem 4 recommendations.
- **Limitations:** Parameter uncertainty dominates; must be paired with sensitivity analysis.

### 5.5 Module E — Network scaling model (national memo)

- **Idea:** Generalize two-airport results to N airports (193 Midwest; 429 national).
- **Candidate methods:**
  - Parameterized template with airport archetypes (traffic tiers).
  - Aggregation/scale-up with production-capacity constraints (phased deployment).
  - Prioritization model (risk-weighted or volume-weighted allocation under limited EDS supply).
- **Advantages:** Directly supports Subproblem 5.
- **Limitations:** Missing data on other airports; requires explicit extrapolation assumptions.

### 5.6 Module F — Future technology / research scenario model

- **Idea:** Parameter sweeps over technology characteristics (speed, accuracy, cost, reliability).
- **Candidate methods:**
  - One-factor-at-a-time and global sensitivity analysis.
  - Scenario planning / technology roadmapping narrative.
- **Advantages:** Supports Subproblem 7.
- **Limitations:** Speculative; must be clearly framed as exploratory.

---

## 6. Implementation Roadmap

A staged, dependency-ordered plan follows. Each stage lists the intended modules, algorithms, and artifacts. **No implementation is performed in this draft.**

### Stage 0 — Scaffolding
- Organize workspace: `data/` (inputs, Table 1 encoding), `code/` (modules), `results/` (outputs), `logs/`.
- Define a single configuration file for all parameters (occupancy, bags/passenger, throughput, availability, costs).
- Establish reproducible random seeds for any stochastic components.

### Stage 1 — Demand engine (Module A)
- Encode Table 1; implement expected-value and scenario demand builders.
- Build arrival-time profile generator from A4.
- **Artifacts:** demand tables (peak-hour bags per airport per scenario), arrival curves.

### Stage 2 — EDS sizing (Module B)
- Implement deterministic sizing and a queueing-based sizing alternative.
- Add reliability derating / availability treatment.
- **Artifacts:** required-machine estimates as functions of parameters; utilization summaries.

### Stage 3 — Scheduling (Module C)
- Formulate optimization model (MIP) and/or load-balancing heuristic.
- Optionally build a discrete-event simulation to stress-test schedules.
- **Artifacts:** candidate departure schedules; peak-load reduction metrics.

### Stage 4 — Cost & policy comparison (Module D)
- Implement life-cycle cost aggregation across policies.
- Produce trade-off curves (capital vs. delay) and break-even points.
- **Artifacts:** cost comparison tables/curves for EDS-only vs. EDS+ETD.

### Stage 5 — ETD extension (Module D + B/C)
- Define ETD role and capacity model; integrate into sizing and scheduling.
- **Artifacts:** ETD fleet sizing, revised schedules, cost-effectiveness summary.

### Stage 6 — Network scaling (Module E)
- Build airport-archetype template and phased deployment/prioritization model.
- **Artifacts:** national/midwest scaling memo inputs.

### Stage 7 — Future research synthesis (Module F)
- Run sensitivity/scenario sweeps; write research recommendations.
- **Artifacts:** scenario tables, narrative recommendations.

### Required modules (planned code organization)
- `params.py` / config loader
- `demand.py` (Table 1 → demand)
- `eds_sizing.py`
- `scheduling.py`
- `cost.py`
- `etd.py`
- `network_scale.py`
- `sensitivity.py`
- `viz.py` (plots for the later report, not this draft)

### Tooling considerations
- Python (NumPy/Pandas) for data handling; SciPy/OR-Tools for optimization; SimPy for discrete-event simulation (candidates to be confirmed later).
- All results to be written under `results/`; logs under `logs/`; scripts under `code/`.

---

## 7. Validation Strategy

Because no ground-truth labels are available, validation will be **internal, structural, and sensitivity-based**.

### 7.1 Evaluation metrics (planned)
- **Sizing:** required machine count, capacity utilization (load factor), probability of overload, queue length/wait time.
- **Scheduling:** peak-to-average demand ratio, number of flights shifted, average added delay, schedule feasibility.
- **Cost:** total life-cycle cost, cost per passenger/bag, break-even thresholds.
- **Robustness:** variability of outputs across scenarios; worst-case performance.

### 7.2 Validation methods
- **Internal consistency checks:** demand monotonic in seats; capacity ≥ demand in feasible solutions; conservation of passengers/bags across stages.
- **Cross-model agreement:** compare deterministic sizing vs. queueing-based sizing; compare optimization schedule vs. heuristic schedule.
- **Analytical/special-case checks:** e.g., single-flight-type or uniform-demand cases with known closed-form expectations.
- **Simulation validation:** verify optimization/heuristic schedules against a discrete-event simulation under stochastic arrivals.
- **Assumption stress tests:** individually and jointly vary the high-leverage assumptions (A1, A3, A4, A7).

### 7.3 Sensitivity and uncertainty analysis (planned)
- **One-factor-at-a-time (OAT)** sweeps over occupancy, bags/passenger, throughput (160–210), availability (92%), installation costs.
- **Global sensitivity** (e.g., variance-based or Morris screening) to rank parameter influence.
- **Scenario analysis:** low/central/high occupancy envelopes; tight vs. extended screening windows.
- **Boundary analysis:** identify when EDS-only becomes infeasible and ETD augmentation or schedule shifting is required.

### 7.4 Validity threats to acknowledge
- Occupancy and baggage behavior are assumed distributions, not observed.
- Peak-hour abstraction may misrepresent real arrival dynamics.
- Cost parameters (esp. operational and delay costs) are uncertain.
- Network scaling relies on archetype extrapolation rather than airport-specific data.

---

## 8. Expected Result Interpretation

This section describes **how future results will be read**, not what they are.

- **Machine-count outputs** will be interpreted as **minimum capacity requirements under stated assumptions**, reported as ranges across scenarios rather than single numbers.
- **Schedule outputs** will be interpreted as **candidate departure redistributions**, with expected trade-offs between peak-load reduction and added delay.
- **Cost comparisons** will be interpreted as **decision-support trade-off curves**, emphasizing break-even conditions rather than absolute dollar verdicts.
- **ETD integration results** will be framed as **conditional cost-effectiveness** relative to EDS-only baselines.
- **National scaling results** will be presented as **order-of-magnitude national impact estimates** with explicit scaling caveats.
- All outputs will be accompanied by the assumptions and scenario context that produced them; results outside the modeled range will be flagged as unsupported extrapolation.

**Interpretation principles:**
1. Report ranges/scenarios, not point estimates alone.
2. Attach every conclusion to its driving assumptions.
3. Distinguish robust findings (stable across scenarios) from fragile ones (sensitive to one assumption).

---

## 9. Limitations and Improvements

### 9.1 Anticipated limitations
- Reliance on range-based occupancy and unvalidated baggage/arrival distributions.
- Simplification of the screening process (batching, secondary inspection, human factors) unless explicitly modeled.
- Cost model may omit staffing, maintenance, downtime, and passenger-experience externalities.
- Two-airport model may not transfer cleanly to all 193/429 airports.
- Deterministic models may under-represent variability; stochastic models add parameterization burden.
- ETD integration role is not yet fixed (primary vs. alarm-resolution) and may drive results.

### 9.2 Planned improvements / extensions
- Incorporate richer arrival distributions (empirical/bimodal) if data become available.
- Add full queueing-network and simulation fidelity, including secondary screening and alarms.
- Introduce explicit uncertainty quantification (distributions over parameters) and value-of-information analysis.
- Extend scheduling model with airline operational constraints (turnarounds, connections, fairness).
- Develop a formal prioritization model for phased national deployment under limited EDS production.
- Phase 7 technology scenarios: model accuracy (false positive/negative) as an explicit objective alongside throughput and cost.

### 9.3 Open questions to resolve during modeling
- Should screening capacity be sized to the strict peak hour or to a smoothed profile?
- What is the correct ETD role and its interaction with EDS throughput?
- How should limited EDS production be allocated across airports?
- Which cost components dominate the EDS-only vs. EDS+ETD decision?

---

## Closing Note on Scope

This document is a **planning blueprint only**. It defines the workflow, assumptions, candidate methods, data plan, implementation roadmap, and validation strategy required to later solve the ICM 2003 Aviation Baggage Screening problem. No calculations, data analysis, model fitting, code execution, experiments, plots, or final results are included, by design.
