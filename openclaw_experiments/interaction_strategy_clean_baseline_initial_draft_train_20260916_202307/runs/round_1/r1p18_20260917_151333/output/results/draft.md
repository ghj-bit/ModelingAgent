# Modeling Blueprint Draft — Camping along the Big Long River (MCM 2012)

> Status: **Planning draft / blueprint only.** This document describes *how* the problem will be modeled in future work. It intentionally contains no computed results, no data analysis, no fitted models, and no final conclusions.

---

## 1. Problem Background and Restatement

The Big Long River is a 225-mile corridor, accessible only by boat. Every trip launches at **First Launch** and exits at **Final Exit** (225 miles downstream). Two propulsion classes will be considered: **oar-powered rubber rafts** (nominal average speed ≈ 4 mph) and **motorized boats** (nominal average speed ≈ 8 mph). Each trip involves **6 to 18 nights of camping** on the river. Along the corridor there are **Y campsites**, distributed "fairly uniformly." Currently **X trips** travel the river per year within a **six-month (≈ 183-day) season**.

A hard feasibility rule governs the system: **no two groups may occupy the same campsite on the same night.** The managing agency also seeks a "wilderness experience," which will be interpreted in future modeling as a preference for **minimal contact** between groups (spatially and/or temporally).

The managers wish to know:
- how to **schedule an optimal mix of trips** (varying in *duration* and *propulsion*) that uses campsites as efficiently as possible, and
- how to determine the river's **carrying capacity**, i.e. **how many additional trips** could be admitted to the season.

**Deliverables (to be produced later, not here):** a one-page summary sheet, a one-page manager-facing memo, and the supporting model/schedule artifacts.

*Restatement note:* X and Y are symbolic parameters. The future model should be designed to be **parametric in (X, Y)** and to report capacity relative to the current baseline of X.

---

## 2. Objectives and Subproblems

**Primary objective (to be pursued later):** Determine a schedule of trips (mix of durations and propulsion types) maximizing the number of trips admitted to the six-month season subject to campsite non-overlap and wilderness-quality constraints, and quantify the **additional trips** beyond X.

**Subproblems (planned decomposition):**

1. **S1 — Trip representation.** Define how a trip is described (launch day, propulsion class, nights, per-night campsite sequence) and derive travel/night structure from speed, river length, and trip duration.
2. **S2 — Capacity model.** Build a first capacity estimate from a resource-conservation/occupancy viewpoint (campsite-nights available vs. campsite-nights demanded).
3. **S3 — Conflict/occupancy model.** Formalize the no-simultaneous-occupancy rule and the "minimal contact" preference into constraints and/or objective terms.
4. **S4 — Scheduling optimization.** Construct a mixed schedule of trips satisfying the constraints and maximizing throughput.
5. **S5 — Scenario analysis.** Study capacity as a function of *mix* (share of motor vs. oar; duration distribution) and of parameter choices for X and Y.
6. **S6 — Policy recommendations.** Translate model outputs into scheduling rules and operational guidance (to be written later as the memo).

**Deliverables mapping:** S2–S4 → capacity/schedule artifacts; S5 → sensitivity tables (future); S6 → memo and summary sheet.

---

## 3. Assumptions

Each assumption will be stated, justified, and flagged for later validation/sensitivity testing.

**A1. Geometry and launch/exit.** The river is treated as a 1-D segment of length L = 225 miles; trip position is a continuous coordinate x ∈ [0, L]. *Justification:* only downstream travel is relevant. *Validation:* relax to discretized-mile segments and compare results.

**A2. Average speeds are constant within a propulsion class.** Oar ≈ 4 mph, motor ≈ 8 mph; day-time travel assumed concentrated in a fixed daily travel window. *Justification:* problem gives only averages. *Validation:* sensitivity to ±speed; test travel-window length.

**A3. Uniform campsite spacing.** Y sites are placed at roughly equal intervals along the corridor. *Justification:* the problem states "fairly uniformly." *Validation:* compare uniform placement against a jittered/clustered placement.

**A4. One trip occupies one campsite per night; one site hosts at most one group per night.** Direct from the statement; treated as a hard constraint.

**A5. A trip spends one night per day on the river; trip duration = number of nights ∈ {6, …, 18}.** Derived interpretation linking speed, distance, and duration.

**A6. Trip atomicity.** Each trip runs start-to-finish without splitting/merging groups; a group may return or start over only in later scenarios. *Validation:* consider multi-segment trips as an extension.

**A7. Season length is a fixed 183-day window.** *Justification:* six months. *Validation:* sensitivity across season lengths.

**A8. "Minimal contact" is quantifiable.** Contact will be proxied by counts of near-simultaneous co-location / close-spacing events between trips. *Justification:* needed to make "wilderness" operational. *Validation:* test alternative contact metrics.

**A9. Deterministic demand.** Initial models treat arrivals/scheduling as deterministic and centrally planned, not as stochastic bookings. *Validation:* later add stochastic arrivals.

**A10. No overtaking interference.** Slower (oar) and faster (motor) boats coexist without physically blocking one another on the river. *Validation:* test with congestion constraints.

---

## 4. Data Processing Plan

**Important context:** the problem statement supplies symbolic parameters X and Y rather than a concrete dataset, and the provided workspace contains no data files. Therefore the future work will follow a **parameter-driven, synthetic-data strategy**:

1. **Parameter intake.** Establish the baseline values for X (current annual trips), Y (number of campsites), speed constants, length (225 mi), duration range (6–18 nights), and season length (≈183 days) as model inputs.
2. **Synthetic instance construction.** Generate parameterized river/campsite configurations (uniform, jittered, clustered) and candidate trip-demand profiles (duration distributions, propulsion mixes).
3. **Feature/derived-quantity construction (definitions only, no computation here):** campsite-nights available per season; required campsite-nights per trip by duration class; per-trip positional-day trajectory; pairwise overlap/temporal-separation indicators.
4. **Data usage strategy.** Reserve the synthetic instances as the modeling corpus; partition into a *development set* (for model construction) and a *holdout set* (for validation). If any external empirical data on river-trip throughput is later provided, it would be used strictly for calibration/validation, never for tuning to a single instance.
5. **Data quality/format plan.** Define a canonical schedule table schema (trip_id, launch_day, propulsion, nights, site_seq) and a canonical campsite table (site_id, mile) for downstream tooling; standardize units and date encodings.

*No preprocessing, feature computation, or data analysis is performed in this draft.*

---

## 5. Candidate Model Framework

Multiple candidate formulations will be explored and compared in later work.

### 5.1 Candidate Model A — Resource/occupancy (capacity) upper bound
- **Idea:** upper-bound throughput from campsite-nights conservation: capacity ≤ (available campsite-nights in season) / (average campsite-nights per trip), adjusted for launch/exit capacity and the impossibility of perfectly filling the season edges.
- **Variables:** Y, season days, mean trip duration, campsite-turnover assumptions.
- **Advantages:** transparent, quickly yields a bound and a "why." **Limitations:** ignores scheduling granularity, propulsion mix, and edge effects.

### 5.2 Candidate Model B — Discrete-event / time–space simulation
- **Idea:** simulate trips moving along a 1-D river over time, allocating campsites each night via a scheduling policy (e.g., greedy/earliest-available), recording usable throughput and contact metrics.
- **Variables:** trip trajectories, site occupancy calendar, contact events.
- **Advantages:** captures dynamics, edge effects, and mix effects; good for policy testing. **Limitations:** policy-dependent; needs careful calibration; not a proof of optimality.

### 5.3 Candidate Model C — Optimization (MILP / scheduling / flow)
- **Idea:** formulate an integer program where decision variables assign trips to launch days, durations, propulsion, and nightly campsites, subject to non-overlap constraints, maximizing admitted trips (or maximizing welfare / capacity) with a contact-penalty term.
- **Mathematical ideas:** time-expanded network / multi-commodity flow on (site × night) nodes; interval scheduling; set-packing with conflict constraints.
- **Advantages:** principled optimum; supports "how much more is possible." **Limitations:** size/complexity grows with Y and season length; requires relaxation/heuristics at scale.

### 5.4 Candidate Model D — Queuing / arrival–service analogy
- **Idea:** view campsites as servers and trip-nights as service demand to estimate congestion and sustainable arrival rates.
- **Advantages:** compact theoretical lens for carrying capacity. **Limitations:** abstraction may hide spatial/route structure; best used as a cross-check.

### 5.5 Cross-cutting components
- **Metric layer:** define throughput, campsite utilization, and contact/wilderness indicators as measurable objectives.
- **Mix layer:** treat propulsion mix and duration mix as strategic decision variables to be traded off (e.g., faster motor trips shorten occupancy but may reduce wilderness quality).
- **Uncertainty layer:** later incorporate stochastic durations/arrivals.

A future comparison matrix will evaluate candidates A–D on fidelity, tractability, interpretability, and how directly each answers the "how many more trips" question.

---

## 6. Implementation Roadmap

**Planned workflow (no code executed in this phase):**

1. **Specification.** Fix notation, parameters (X, Y, L, speeds, duration range, season length), and the canonical schedule/site schemas from §4.
2. **Model A first (bound).** Implement the occupancy upper bound to establish a reference envelope.
3. **Model B (simulation).** Implement the time–space simulator with a configurable allocation policy; use it to generate candidate schedules and contact statistics.
4. **Model C (optimization).** Build the integer/flow formulation; solve small-to-medium instances exactly, then adopt relaxations/heuristics (e.g., rolling-horizon, decomposition, greedy + local search) for larger ones.
5. **Model D (queuing cross-check).** Implement the analytical cross-check for consistency.
6. **Scenario runner.** Sweep propulsion mix, duration mix, X, and Y; record throughput and wilderness metrics.
7. **Reporting layer.** Produce the summary sheet and the manager memo from scenario outputs (later stage).

**Required conceptual modules:** parameter/config manager; instance generator; trajectory/occupancy engine; constraint/feasibility checker; optimizer (exact + heuristics); contact/wilderness metric module; scenario + sensitivity driver; results table/report generator.

**Engineering notes:** design for parametric (X, Y); keep feasibility checking independent of the optimizer; log inputs and random seeds; ensure the schedule schema is exportable for later memo/summary generation.

---

## 7. Validation Strategy

**Evaluation metrics (to be defined and then computed later):**
- Total trips admitted vs. baseline X (**the headline "how many more"**).
- Campsite utilization (occupied campsite-nights / available campsite-nights).
- Contact / wilderness-quality indicators (near-simultaneous co-location counts, minimum spacing distributions).
- Solver metrics for Model C (gap to bound, runtime, feasibility rate).

**Validation methods:**
- **Constraint verification:** programmatic checks that no site is double-booked (feasibility checker independent from the solver).
- **Bound consistency:** simulation/optimization results must not exceed Model A's upper bound; investigate any violation.
- **Cross-model agreement:** compare Models B, C, and D on shared instances for order-of-magnitude consistency.
- **Instance variation:** repeat across uniform/jittered/clustered site layouts and varied demand mixes.
- **Holdout scenarios:** evaluate the chosen schedule policy on configurations not used during tuning.

**Sensitivity analysis (planned):**
- Sensitivity to Y (site count) and to season length.
- Sensitivity to speed constants (± around 4/8 mph) and travel-window assumptions.
- Sensitivity to campsite-uniformity (uniform vs. clustered).
- Sensitivity to propulsion and duration mix.
- Sensitivity to the definition/weighting of the "wilderness/contact" metric.
- Sensitivity to stochasticity (future extension) via repeated randomized runs.

**Robustness/limits tests:** stress instances near the theoretical bound; test degenerate cases (Y very small/large, extreme mixes).

---

## 8. Expected Result Interpretation

Future outputs are expected to take the following *forms* (values to be produced later — none are given here):
- **A capacity envelope** (upper bound plus achievable throughput) expressed both absolutely and as **additional trips beyond X**.
- **A recommended schedule policy** describing how to admit a mix of motor/oar trips and duration classes.
- **Trade-off characterizations** between throughput and wilderness/contact quality, and guidance on the best-use regime for campsites.
- **Interpretation aids:** an occupancy/contact map of the season and a manager-oriented explanation of *why* the capacity is what it is.
- Explicit statements of which conclusions are robust (stable across scenarios) vs. assumption-sensitive.

*This section describes how results will be read, not what they are.*

---

## 9. Limitations and Improvements

**Anticipated limitations:**
- Symbolic X, Y and the absence of empirical data mean results will be **model- and parameter-dependent**, not calibrated to a specific river.
- Constant-average-speed and fixed-daily-window assumptions simplify real travel behavior.
- The "minimal contact"/wilderness notion is inherently subjective and only proxied by metrics.
- Model C may face scalability limits when Y and the season are large, forcing heuristic solutions with no optimality guarantee.
- Deterministic treatment of arrivals overstates control over real booking patterns.

**Planned improvements (future):**
- Introduce stochastic arrivals, durations, and travel times; move toward probabilistic capacity statements.
- Refine spatial fidelity with real site spacing and river features (rapids affecting speed).
- Enrich the wilderness objective with empirically motivated contact thresholds.
- Develop stronger decompositions/metaheuristics and tighter bounds for large instances.
- Validate against any real-world river-management data if it becomes available.

---

## Appendix — Planning Checklist (to be satisfied in later phases)

- [ ] Parameter set (X, Y, L, speeds, duration range, season) fixed and documented.
- [ ] Canonical schedule/site schemas defined and exportable.
- [ ] Models A–D specified; comparison matrix prepared.
- [ ] Independent feasibility checker implemented.
- [ ] Metrics layer (throughput, utilization, contact) defined.
- [ ] Scenario + sensitivity driver designed.
- [ ] Summary sheet and manager memo produced from model outputs.

*End of planning draft. No solving, computation, or experiments were performed as part of this document.*
