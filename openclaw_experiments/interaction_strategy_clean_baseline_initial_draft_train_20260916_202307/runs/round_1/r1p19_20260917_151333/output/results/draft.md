# Bank Service Problem — Modeling Blueprint (Initial Draft)

> Status: **Planning draft only.** This document is a roadmap for future modeling work. It contains no computed results, no data analysis, and no final conclusions.

---

## 1. Problem Background and Restatement

A bank branch manager intends to raise customer satisfaction by improving service operations. Management has set two explicit service-level targets:

- The average time a customer waits before being served should be **less than 2 minutes**.
- The average queue length (number of customers waiting in line) should be **2 persons or fewer**.

The branch estimates an average volume of about **150 customers per day**. The current system description is given by two discrete probability distributions:

- **Arrival process:** the distribution of the *time between successive arrivals* (inter-arrival time), defined over 0–5 minutes with given probabilities (Table 1).
- **Service process:** the distribution of *service time* per customer, defined over 1–4 minutes with given probabilities (Table 2).

The modeling effort will be organized around three deliverables that mirror the three sub-questions:

1. A mathematical model of the service system that reproduces the queueing behavior implied by the two tables.
2. A comparison of current performance against the two management targets, followed by an exploration of what **minimal changes in the number of servers** would be required to meet those targets if the current configuration falls short.
3. A short (1–2 page) **non-technical management letter** that will summarize recommendations in plain language (to be produced at a later solving/reporting stage, guided by this blueprint).

Because the network here is small but not trivially characterized by textbook closed-form formulas, both **analytical queueing** and **discrete-event simulation** approaches will be considered as candidate frameworks rather than committing in advance.

---

## 2. Objectives and Subproblems

**Primary objective.** Design a modeling approach capable of (a) reproducing the current service-system performance and (b) identifying the minimal server-count change that would satisfy management's two targets.

**Subproblem breakdown:**

- **SP1 — System model construction.**
  Formalize the arrival and service processes, the queue discipline, the number of servers, and the performance measures of interest. Decide on a level of abstraction that preserves the empirical distributions in Tables 1 and 2.

- **SP2 — Current-state performance assessment.**
  Define the procedure by which the model will later be used to estimate average waiting time and average queue length under the *current* server configuration, and how those estimates will be compared to the 2-minute / 2-person thresholds.

- **SP3 — Minimal-change search.**
  Define how the required number of servers (and, if relevant, related levers) will be searched to find the *minimal* change satisfying both targets. This subproblem includes defining what "minimal" means (fewest additional servers; smallest change in staffing) and how ties or near-ties will be handled.

- **SP4 — Communication artifact plan.**
  Outline the content, structure, and tone of the non-technical management letter and how its recommendations will be derived from the model outputs (without producing the letter here).

**Deliverable mapping:** SP1 → model section; SP2 + SP3 → analysis/decision section; SP4 → management letter.

---

## 3. Assumptions

The following assumptions are proposed as working hypotheses to be documented and stress-tested. Each is paired with its justification and a planned validation approach.

| # | Assumption | Justification | Planned validation |
|---|------------|---------------|--------------------|
| A1 | Arrivals follow a renewal process: inter-arrival times are i.i.d. draws from Table 1. | The statement provides a single time-between-arrival distribution and no time-of-day detail. | Compare aggregate arrival counts against the stated ~150 customers/day; consider time-varying sensitivity. |
| A2 | Service times are i.i.d. draws from Table 2 and independent of arrivals. | The statement provides one service-time distribution. | Sensitivity analysis on service-time variance; test correlation assumptions as a scenario. |
| A3 | Customers are served on a first-come-first-served basis, single queue feeding all servers. | Standard bank-teller operation; statement does not specify otherwise. | Scenario comparison against per-server queues (jockeying) as a robustness check. |
| A4 | A single homogeneous pool of servers with identical service distributions. | Only one service-time table is given. | Sensitivity to heterogeneous server speeds. |
| A5 | The system reaches steady state within the operating day, and the relevant performance measures are long-run (or full-day) averages. | Management targets are described as averages. | Test warm-up / finite-horizon effects in simulation; compare transient vs. steady-state estimates. |
| A6 | Customers are patient: no balking, reneging, or abandonment. | Statement gives no abandonment data. | Model abandonment as an extension scenario. |
| A7 | The distributions in Tables 1–2 describe typical conditions; day-to-day variation is modeled as sampling variability. | Tables are the only data source provided. | Monte Carlo replication and confidence intervals. |
| A8 | "Minimal changes for servers" is interpreted as the smallest achievable server count (or smallest increment) meeting both targets. | Direct reading of sub-question (2). | Reframe as cost-based optimization in a sensitivity scenario. |

These assumptions will be revisited and either confirmed, relaxed, or replaced as the modeling proceeds.

---

## 4. Data Processing Plan

**Note:** No data will be processed or analyzed in this planning stage. The steps below describe the intended pipeline.

- **D1 — Distribution encoding.** Convert Tables 1 and 2 into normalized discrete probability mass functions for inter-arrival time and service time, ensuring probabilities sum to one and documenting any rounding conventions.
- **D2 — Derived parameters.** Plan to derive summary statistics (mean, variance, coefficient of variation) of both distributions to inform the choice between closed-form queueing formulas and simulation. *(Derivation deferred to the solving stage.)*
- **D3 — Arrival-rate reconciliation.** Plan a cross-check between the mean inter-arrival time implied by Table 1 and the stated ~150 customers/day figure, and document how any discrepancy will be handled (e.g., scaling, operating-hours inference).
- **D4 — Random-variate generation design.** Specify the intended inverse-transform / table-lookup procedure for sampling inter-arrival and service times, including how zero inter-arrival times (simultaneous arrivals) will be treated.
- **D5 — Scenario table construction.** Define the structure of a scenario/parameter table that will hold server-count candidates and any alternative assumptions (queue discipline, abandonment), so that analysis runs are reproducible and comparable.
- **D6 — Data usage strategy.** Use all provided probability tables as the primary evidence base. Where the problem references ~150 customers/day, treat it as a validation anchor rather than a hard constraint, and document the treatment.

---

## 5. Candidate Model Framework

Two complementary candidate frameworks are proposed; their outputs will later be cross-validated against each other.

### 5.1 Candidate A — Analytical queueing model (M/G/c / G/G/c approximations)

- **Variables / notation:** arrival rate λ, service rate μ, number of servers c, utilization ρ = λ/(cμ), traffic intensity, expected waiting time W_q, expected queue length L_q.
- **Mathematical ideas:** classical single-server M/M/1 and multi-server M/M/c formulas as a baseline; since arrival and service times are discrete and not exponential, plan to use **M/G/c / G/G/c approximation methods** (e.g., Kingman-type or Sakasegawa approximations) and/or the **Erlang-C** family with correction factors.
- **Advantages:** fast, transparent, closed-form, easy to embed in a search over c; produces interpretable utilization-based insights.
- **Limitations:** approximations may be inaccurate for discrete, non-exponential distributions with high variance; steady-state assumptions; limited ability to model transient or time-varying behavior.

### 5.2 Candidate B — Discrete-event simulation (DES)

- **Variables / notation:** simulation clock, event list (arrival, service-start, service-end), server state, queue state, per-customer wait and queue-length statistics.
- **Mathematical ideas:** stochastic process simulation of a G/G/c queue; discrete event scheduling; Monte Carlo replication for confidence intervals.
- **Advantages:** directly uses the discrete distributions in Tables 1–2 with no distributional approximation; handles transient behavior, multiple servers, queue discipline variants, and abandonment extensions naturally.
- **Limitations:** stochastic error requiring replication; implementation and validation overhead; results are estimates rather than expressions.

### 5.3 Candidate C — Optimization layer over the model

- **Mathematical ideas:** treat the chosen performance model (A or B) as an oracle and search over candidate server counts c (and optionally scheduling variants) for the minimal configuration meeting both targets; formulate as a constrained minimization ("minimize c subject to W_q < 2 and L_q ≤ 2").
- **Advantages:** directly answers sub-question (2); can be extended to cost-based objectives.
- **Limitations:** search cost if simulation is the oracle; need to handle stochastic noise in comparisons (paired runs, common random numbers).

**Recommendation for the next stage:** build Candidate B (DES) as the primary engine, use Candidate A as a rapid analytical cross-check, and wrap the engine in Candidate C for the minimal-change search. Final choice of primary vs. secondary will be confirmed after a small calibration comparison.

---

## 6. Implementation Roadmap

The implementation will proceed in modular stages; no code is written in this planning stage.

- **M1 — Input encoding module.** Represent the two probability tables as reusable data structures and provide sampling utilities.
- **M2 — Queueing engine module.** Either implement a DES engine (event scheduler, server pool, statistics collector) or an analytical evaluator, or both behind a common interface.
- **M3 — Performance-measurement module.** Aggregate per-customer and per-time-unit statistics into average wait time and average queue length (plus secondary measures such as server utilization and maximum wait).
- **M4 — Scenario/experiment runner.** Sweep over server counts and assumption variants; record results in a structured results table.
- **M5 — Minimal-change search module.** Implement the constrained search that identifies the smallest server configuration satisfying both targets.
- **M6 — Reporting module.** Generate the contest-format technical write-up and the plain-language management letter from the structured results.

**Suggested workflow order:**
1. Encode distributions (M1).
2. Build and sanity-check the engine (M2–M3) against simple limiting cases.
3. Estimate current-state performance for the existing server configuration (SP2).
4. Sweep server counts and run the minimal-change search (M5, SP3).
5. Conduct sensitivity analyses (Section 7).
6. Produce the technical report and the management letter outline (M6, SP4).

**Required modules/interfaces:** a probability-sampling interface, a system-state model, a statistics-aggregation interface, an experiment-configuration interface, and a results-serialization format. These interfaces will be defined so the analytical and simulation engines are interchangeable.

---

## 7. Validation Strategy

**Evaluation metrics (to be computed in the solving stage):**

- Average customer waiting time (primary, threshold 2 min).
- Average queue length (primary, threshold 2 persons).
- Secondary: server utilization, 95th-percentile wait, maximum queue length, probability that wait exceeds threshold, throughput.

**Validation methods:**

- **V1 — Analytical vs. simulation cross-check.** Compare Candidate A and Candidate B on the same scenarios; investigate and explain any divergence.
- **V2 — Limiting-case checks.** Verify the engine against special cases where known results exist (e.g., degenerate service times, single server with exponential-like inputs as a benchmark).
- **V3 — Traffic-rate consistency.** Confirm that realized arrival throughput is consistent with the ~150 customers/day estimate.
- **V4 — Monte Carlo convergence.** Use replication counts and confidence intervals to ensure estimates are stable; apply common random numbers for fair comparisons between server counts.
- **V5 — Assumption stress tests.** Re-run key scenarios under relaxed assumptions (per-server queues, abandonment, heterogeneous servers, time-varying arrivals) to bound the robustness of conclusions.

**Sensitivity analysis plan:**

- Vary distributional shape (mean/variance) within plausible ranges.
- Vary the queue discipline (FCFS vs. alternatives).
- Vary the interpretation of "minimal change" (server count vs. cost).
- Test finite-horizon / warm-up effects to assess steady-state sensitivity.

---

## 8. Expected Result Interpretation

This section describes how results will be interpreted *once produced*; it does not contain results.

- **Current-state verdict.** The model is expected to yield estimates of average wait and average queue length that will be compared directly to the 2-minute and 2-person thresholds, producing a clear "satisfactory / not satisfactory" characterization under the stated assumptions.
- **Minimal-change finding.** If the current configuration is insufficient, the search will identify the smallest server count meeting both targets; results will be reported as a candidate configuration plus a margin-of-comfort discussion (how close the targets are to being met).
- **Uncertainty framing.** All reported figures will be accompanied by uncertainty statements (confidence intervals from replication, or approximation-error caveats for analytical results).
- **Sensitivity framing.** Conclusions will be presented alongside the range of assumptions under which they hold, and flagged where conclusions are fragile.
- **Management-facing summary.** The management letter will translate the technical findings into a short recommendation emphasizing expected wait improvement, staffing implications, and confidence in the recommendation.

---

## 9. Limitations and Improvements

**Anticipated limitations:**

- Reliance on the two provided discrete distributions; no time-of-day, day-of-week, or customer-type structure.
- Steady-state or full-day averaging may mask peak-period congestion relevant to customer perception.
- Approximation error in analytical models; stochastic error in simulation.
- No abandonment, balking, or priority behavior in the base model.
- "Minimal change" defined primarily in server count; cost trade-offs are secondary.

**Planned improvements / extensions:**

- Introduce time-varying arrival rates to model peak periods.
- Model customer abandonment and balking to better reflect real satisfaction.
- Add a cost model (staffing cost vs. waiting-time cost) to make the minimal-change recommendation economically grounded.
- Explore heterogeneous server service rates and more flexible scheduling.
- Consider service-quality metrics beyond averages (e.g., tail waits, proportion served within target).
- Strengthen empirical grounding if additional data become available (arrival timestamps, service logs).

---

## Planning Checklist

- [x] Problem restated and deliverables identified.
- [x] Objectives and subproblems decomposed (SP1–SP4).
- [x] Assumptions stated with justification and validation approach.
- [x] Data processing plan described (no processing performed).
- [x] Candidate models proposed with advantages/limitations.
- [x] Implementation roadmap and modules defined.
- [x] Validation and sensitivity strategy outlined.
- [x] Result interpretation and limitations prepared.

*End of planning draft — no computations, experiments, or results are included by design.*
