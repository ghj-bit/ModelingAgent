# MM-Bench 2017_D — Airport Security Checkpoint Modeling Blueprint (Draft)

**Problem ID:** `2017_D`
**Source:** MM-Bench, 2017
**Document type:** Modeling plan / blueprint draft (future-oriented). This document defines *how* the problem will be modeled. It contains no computed results, no executed experiments, and no final conclusions.

---

## 1. Problem Background and Restatement

Airport security checkpoints must balance two competing goals: maximizing security screening effectiveness and minimizing passenger inconvenience (waiting time and its variance). Following the 2016 congestion incidents (notably Chicago O'Hare), the TSA modified equipment, procedures, and staffing, but the cost and effectiveness of these changes remain unclear, and unexplained long lines still occur at normally low-traffic airports.

A US checkpoint is described as a sequence of zones:

- **Zone A — Identity/Document Check:** passengers arrive (randomly) and queue for an officer who inspects identification and boarding documents.
- **Zone B — Screening Line Preparation:** passengers queue for an open screening lane; the number of open lanes varies with anticipated activity. At the front they divest belongings (shoes, belts, jackets, metal, electronics, liquids) into bins for X-ray; laptops and some medical devices go into separate bins.
- **Zones B/D — Scanning & Secondary Screening:** belongings move by conveyor through X-ray; flagged items go to additional search (Zone D). Passengers proceed through a millimeter-wave scanner or metal detector; failures trigger a pat-down (Zone D).
- **Zone C — Reclaim/Exit:** passengers collect belongings from the post-X-ray belt and leave the checkpoint.

**Pre-Check program:** ~45% of passengers are enrolled (trusted travelers, $85 for five years). Pre-Check has a separate screening process (no shoe/belt/light-jacket removal, no laptop removal) and typically **one Pre-Check lane per three regular lanes**, despite a higher share of passengers using Pre-Check.

**Deliverables requested by the ICM/TSA task:**
- (a) One or more models of passenger flow that identify bottlenecks in the current process.
- (b) Two or more process modifications to improve throughput and reduce wait-time variance, with modeled impact.
- (c) Sensitivity analysis of cultural norms / traveler styles (e.g., personal-space respect, collective vs. individual efficiency, slower travelers) and how the system can accommodate them.
- (d) Policy and procedural recommendations (globally applicable or culture/traveler-type tailored), plus validation, strengths/weaknesses, and future work.

**Restatement of modeling intent:** The plan will build a stochastic, service-network representation of the checkpoint, use it to locate bottlenecks, evaluate candidate redesigns, and stress-test behavior under heterogeneous traveler styles, culminating in evidence-based recommendations.

---

## 2. Objectives and Subproblems

**Primary objective:** Build a validated, parameterized model of the checkpoint as a queueing/service network that (i) reproduces observed flow behavior, (ii) localizes bottlenecks, (iii) predicts the impact of redesigns on throughput and wait-time variance, and (iv) supports culture/traveler-style sensitivity analysis.

**Subproblems:**

1. **SP1 — Process abstraction & bottleneck diagnosis (Task a).** Formalize zones A–D as a network of queues and servers; characterize per-stage service-time distributions and utilization; identify which stages and resources dominate congestion and variance.
2. **SP2 — Baseline calibration & validation.** Estimate arrival processes and service-time distributions from the staged data; calibrate the baseline model; define and confirm validation criteria.
3. **SP3 — Redesign candidates (Task b).** Specify ≥2 concrete modifications (e.g., lane allocation between Pre-Check/regular, staffing changes, divestment/binning changes, reconfiguration of scanner assignment) and model their throughput/variance impact.
4. **SP4 — Heterogeneous traveler behavior (Task c).** Incorporate traveler-type/stylistic heterogeneity (personal-space spacing, "cutting" avoidance, individual vs. collective efficiency, slower/less-experienced travelers) as behavioral parameters; run sensitivity experiments on throughput and variance.
5. **SP5 — Recommendations & robustness (Task d).** Translate model findings into policy/procedure recommendations (global and tailored), state strengths/weaknesses, and outline future work.

**Deliverables (to be produced in later solving phases):** documented model(s), calibrated parameters, bottleneck map, redesign comparisons, sensitivity results, recommendation memo, and validation/limitations discussion.

---

## 3. Assumptions

Each assumption below is paired with justification and a planned validation approach. Assumptions will be revisited if validation fails.

**A1. Steady-state/stationarity within observation windows.** The data represent a reasonably stable operating regime over each recorded period. *Justification:* enables standard queueing analysis. *Validation:* test for non-stationarity (time-varying arrival rate) and segment windows if needed.

**A2. Random (approximately Poisson) arrivals.** Passenger arrivals are independent and memoryless per stream (Pre-Check vs. regular). *Justification:* standard for independent individual arrivals; supports M/G/c-style formulations. *Validation:* compare empirical arrival-count distributions to Poisson dispersion; check inter-arrival autocorrelation.

**A3. Service times are stochastic and stage-specific.** Each station has its own service-time distribution, potentially stage- and traveler-type-dependent. *Validation:* compare fitted distributions (e.g., exponential, lognormal, gamma, empirical) against per-stage histograms.

**A4. Queue discipline FCFS per lane at most stages.** *Justification:* matches described process. *Validation:* relax in a sensitivity scenario (e.g., priority for Pre-Check, or "cutting" behavior).

**A5. Number of open lanes is an exogenous, controllable parameter.** Lane counts and staffing can be treated as decision variables. *Justification:* directly actionable for recommendations. *Validation:* cross-check against stated 1:3 Pre-Check ratio and scenarios with alternate allocations.

**A6. Service stages are approximately independent given the traveler/type.** *Justification:* simplifies modular modeling. *Validation:* test residual correlations between successive stage times for the same individual.

**A7. Probability of secondary screening (Zone D) is a parameter.** *Justification:* the data describe typical processing; secondary events are relatively rare and modeled probabilistically. *Validation:* sensitivity sweep on secondary-screen rates.

**A8. Traveler mix and arrival split are parameters.** The Pre-Check share (~45% enrollment) and type mix are model inputs. *Validation:* scenario variation around the baseline split.

**A9. Measurement consistency.** Timestamp/elapsed-time columns (two officers for ID check and X-ray) are assumed comparable in units and semantics after alignment. *Validation:* schema audit and unit checks (see Data Plan).

**A10. Behavioral parameters are additive modifiers on base service/space behavior.** Cultural/traveler-style effects are modeled as multipliers/offsets on spacing and service times. *Validation:* scenario sweeps and, where possible, comparison with documented behavioral norms.

---

## 4. Data Processing Plan

**Source file:** `data/2017_ICM_Problem_D_Data.csv`
(repository path: `.../output/data/2017_ICM_Problem_D_Data.csv`)

**Columns (per dataset definition):**

| Column | Meaning |
|---|---|
| `TSA Pre-Check Arrival Times` | recorded times individuals enter the Pre-Check queue |
| `Regular Pax Arrival Times` | recorded times individuals enter the regular queue |
| `ID Check Process Time 1` | arrival at ID-check station → officer calls next passenger (officer 1) |
| `ID Check Process Time 2` | same, different TSA officer (officer 2) |
| `Milimeter Wave Scan times` | timestamps as passenger exits the millimeter-wave scanner |
| `X-Ray Scan Time 1` | timestamps as bags exit the X-ray (reader 1) |
| `X-Ray Scan Time 2` | same, different TSA officer (reader 2) |
| `Time to get scanned property` | time from arriving at belt to placing items for scanning until retrieving items off post-X-ray belt |

**4.1 Ingestion & schema audit.**
- Parse CSV with explicit field typing; record row count, missingness, and duplicated/monotonicity properties.
- **Format hazard:** values appear as timestamp-like tokens (e.g., `MM:SS.s`) while the property column appears in a coarser `M:SS`-style format. A normalization step will reconcile all time fields into a single canonical unit (planned: seconds) and flag any columns whose semantics are *timestamp* vs. *duration* vs. *cumulative elapsed*.
- Detect delimiter/encoding issues and any irregular whitespace.

**4.2 Cleaning & quality checks (to be executed later).**
- Convert all time-like fields to seconds; validate monotonicity of arrival streams; detect resets/recording gaps.
- Resolve ambiguity between "clock timestamp" and "elapsed duration" interpretations; document the chosen convention and its sensitivity.
- Handle missing values: quantify missingness per column and choose a strategy (drop, impute, or model-as-missing), to be decided by the auditor of the data, not assumed here.
- Detect and label outliers (unusually long service/scan times) for scenario-based treatment rather than blind removal.

**4.3 Feature construction (planned).**
- **Flow-level features:** arrival counts per time bucket, inter-arrival times, arrival rate λ(t) per stream (Pre-Check, regular).
- **Service-time features:** per-stage elapsed durations; per-officer/per-reader comparisons (ID Check 1 vs. 2; X-ray 1 vs. 2).
- **Cross-stage features:** roughly end-to-end time from entry to exit (as far as columns permit), and the "property reclaim" duration as a proxy for Zone B/C occupancy.
- **Heterogeneity features:** any recoverable traveler-type proxy (stream membership) and derived grouping for behavioral scenarios.

**4.4 Data usage strategy.**
- Reserve the observed data for **calibration and validation** of arrival/service distributions; keep a held-out subset or time window for out-of-sample validation.
- Use the data's *distributional* content (not a single point estimate) to parameterize stochastic inputs.
- Keep all transformation steps reproducible and versioned; store intermediate artifacts under `code/` and `logs/`, with outputs referenced from `results/`.
- Explicitly document any assumption made when a column's semantics are ambiguous, and expose it as a sensitivity dimension.

---

## 5. Candidate Model Framework

A layered, multi-fidelity framework is proposed so results can be cross-checked.

**5.1 Analytical queueing-network model (fast, interpretable).**
- Represent Zones A–D as an open queueing network: ID-check stations (multi-server), screening lanes, X-ray/scanner servers, and reclaim stage.
- Candidate constructs: M/G/c, M/M/c with blocking, Jackson/BCMP-style networks, and tandem-queue approximations for the aisle/conveyor.
- **Variables/parameters:** arrival rates per stream λ; per-stage service rates μ and variability; number of servers c per stage; routing probabilities (e.g., probability of Zone D secondary screening); Pre-Check fraction.
- **Outputs (planned):** utilization ρ, expected wait Wq, queue-length distributions, throughput, and wait-time variance per stage.
- **Advantages:** closed-form/analytic insight, fast scenario sweeps, clear bottleneck attribution.
- **Limitations:** independence/stationarity assumptions; difficulty modeling blocking, shared resources, and finite buffers.

**5.2 Discrete-event simulation (DES) model (primary, detailed).**
- Agent/entity-based simulation of individual passengers moving through the zone network, with resource pools (officers, lanes, scanners, X-ray belts), queues, and buffers.
- **Variables:** per-entity attributes (type: Pre-Check/regular, behavioral style), per-stage sampled service times, resource capacities, routing/blocking rules, and secondary-screening probabilities.
- **Outputs (planned):** time series of queue lengths and waits, per-stage wait distributions, throughput, variance, utilization, and bottleneck identification via wait/occupancy contribution.
- **Advantages:** captures congestion, blocking, resource sharing, heterogeneity, and variance naturally; supports what-if redesigns.
- **Limitations:** computational cost, calibration/validation burden, sensitivity to distributional assumptions.

**5.3 Behavioral / heterogeneity extension (Task c).**
- Augment the DES with traveler "style" parameters such as personal-space spacing (affecting effective lane capacity/queue density), tolerance for "cutting"/queue-jumping, and individual vs. collective efficiency (affecting service speed and balking/reneging behavior).
- Model styles as distributional modifiers on service times, spacing, and routing; run factorial sweeps to quantify throughput/variance effects.

**5.4 Optimization / decision layer (for recommendations).**
- Formulate lane-allocation and staffing as a design problem (e.g., choose numbers of Pre-Check vs. regular lanes and officers) to optimize a multi-objective criterion combining throughput and wait-time variance subject to a security-standards constraint.
- Candidate methods: scenario enumeration/grid search, queueing-based optimization, or simulation-optimization (e.g., ranking-and-selection, response-surface methods).

**5.5 Model-role summary.**

| Model layer | Role | Primary outputs |
|---|---|---|
| Queueing network | Fast screening & bottleneck theory | ρ, Wq, variance, throughput |
| DES | Primary detailed evaluation & redesigns | wait distributions, bottleneck map |
| Behavioral extension | Sensitivity to culture/traveler styles | robustness of throughput/variance |
| Optimization layer | Recommendation synthesis | candidate lane/staffing configurations |

---

## 6. Implementation Roadmap

Planned, staged workflow (no code is executed as part of this blueprint):

- **Stage 0 — Environment & scaffolding.** Establish reproducible project structure (`code/`, `data/`, `logs/`, `results/`); pin dependencies; define configuration files for scenarios.
- **Stage 1 — Data pipeline.** Implement parsing, time normalization, cleaning, and feature extraction; emit audit logs to `logs/`.
- **Stage 2 — Distribution fitting.** Fit candidate distributions to per-stage service times and arrival processes; compare fits; store parameters and diagnostics.
- **Stage 3 — Analytical model.** Implement the queueing-network model; compute baseline congestion metrics and identify theoretical bottlenecks.
- **Stage 4 — DES model.** Build the discrete-event simulation with parameterized resources and routing; reproduce baseline metrics for cross-validation against Stage 3.
- **Stage 5 — Baseline analysis.** Produce the baseline bottleneck map (waits, utilization, variance contributions per stage).
- **Stage 6 — Redesign experiments.** Implement ≥2 modification scenarios; run controlled comparisons vs. baseline.
- **Stage 7 — Behavioral sensitivity.** Add traveler-style parameters; run factorial sensitivity sweeps.
- **Stage 8 — Optimization.** Search lane/staffing configurations under the multi-objective criterion.
- **Stage 9 — Reporting.** Assemble findings into the final report; document assumptions, validation, limitations, and recommendations.

**Required modules (planned):** data loader/normalizer; distribution-fitting utilities; queueing solver; DES engine (entity, queue, resource, scheduler, statistics collector); scenario/config manager; experiment runner; results aggregator; plotting/reporting utilities (used only in later solving phases).

**Implementation conventions (planned):** deterministic random seeds; configuration-driven scenarios; per-run logging; separation of model definition from experiment orchestration to keep results reproducible.

---

## 7. Validation Strategy

**7.1 Evaluation metrics (planned).**
- Throughput (passengers screened per unit time) per stream and overall.
- Mean and variance (and tail percentiles) of wait times per stage and end-to-end.
- Resource utilization per station/lane; queue lengths; bottleneck identification.
- Security-standards indicators treated as constraints (e.g., modeled secondary-screening coverage).

**7.2 Validation methods.**
- **Face validity:** confirm model structure matches the described Zone A–D process.
- **Calibration fit:** statistical goodness-of-fit for arrival/service distributions.
- **Out-of-sample / hold-out validation:** compare predicted vs. observed flow/wait statistics on held-out data or time windows.
- **Cross-model validation:** compare analytical queueing results with DES results for consistency in the regimes where both apply.
- **Consistency checks:** Little's Law (L = λW) and flow-conservation checks as sanity tests.
- **Assumption audits:** explicit tests for stationarity (A1), arrival process (A2), FCFS discipline (A4), and stage independence (A6); relax where tests fail.

**7.3 Sensitivity analysis (planned).**
- **Parameter uncertainty:** vary service rates, arrival rates, number of servers, secondary-screening probability, Pre-Check fraction.
- **Structural uncertainty:** alternate routing/queue-discipline rules (priority, reneging, blocking).
- **Behavioral/cultural (Task c):** vary personal-space spacing, queue-jumping tolerance, individual vs. collective efficiency, and slow-traveler fractions.
- **Scenario robustness:** repeat runs with multiple random seeds to report variability of model outputs (uncertainty quantification).

---

## 8. Expected Result Interpretation

This section describes *how results will be read* once produced (no values given here). Interpretation will focus on:

- **Bottleneck attribution:** Which stage(s) dominate wait and variance, and whether congestion originates from capacity shortfalls, service-time variability, or resource coupling between Pre-Check and regular streams.
- **Redesign comparison:** For each candidate modification, how throughput and wait-time variance would shift relative to baseline, and whether gains come at a security-coverage cost.
- **Lane-allocation insight:** Whether the current 1:3 Pre-Check-to-regular ratio is consistent with the modeled demand split, and how alternative allocations would trade off both streams.
- **Behavioral sensitivity:** How strongly results depend on traveler-style parameters, and which designs remain robust (low-regret) across behavioral regimes.
- **Policy translation:** Which interventions appear globally applicable vs. which should be tailored to specific cultures/traveler types, framed as hypotheses to be confirmed by the validated model.

Interpretation will explicitly separate **model-based inference** from **assumptions**, and will flag any result that is sensitive to ambiguous data semantics.

---

## 9. Limitations and Improvements

**Anticipated limitations.**
- Data limitations: short duration/single-context records; ambiguous timestamp-vs-duration semantics; two distinct service streams (Pre-Check/regular) and multiple officers complicate clean estimation.
- Modeling limitations: stationarity/independence assumptions; finite buffers and blocking approximated; behavioral parameters set by scenario rather than measured directly.
- Scope limitations: secondary-screening and security effectiveness are modeled probabilistically rather than from detailed security data.

**Planned improvements / future work.**
- Enrich data collection (longer horizons, labeled traveler types, explicit secondary-screening logs, direct clock timestamps) to reduce semantic ambiguity.
- Upgrade to time-varying/transient queueing models and more realistic conveyor/aisle blocking.
- Calibrate behavioral parameters empirically (e.g., via observation studies or controlled experiments).
- Extend the optimization layer to multi-objective and robust/stochastic optimization, including cost of staffing changes (relevant to the TSA cost question).
- Add a dedicated security-effectiveness dimension to co-optimize safety and throughput rather than treating safety only as a constraint.

---

*End of modeling blueprint draft. This document defines the plan of attack and contains no solutions, computations, or executed analysis.*
