# Modeling Blueprint Draft — MM-Bench 2017_C
## Effects of Self-Driving, Cooperating Vehicles on Highway Capacity (Thurston, Pierce, King, Snohomish Counties)

> Status: **Planning draft only.** This document is a roadmap for future modeling work.
> It contains no computed results, no fitted models, no executed experiments, and no final conclusions.
> All statements are future-oriented ("will", "is planned to", "is expected to").

---

## 1. Problem Background and Restatement

### 1.1 Background
Traffic capacity in several regions of the United States is limited by the number of physical lanes on roadways. In the Greater Seattle area, peak-hour demand routinely exceeds the designed capacity of the road network, producing long delays — most acutely on Interstates 5, 90, and 405 and State Route 520. These four corridors, crossing Thurston, Pierce, King, and Snohomish counties, are the corridors of interest for this problem.

Self-driving, cooperating cars have been proposed as a way to increase effective highway capacity without adding lanes. However, the interaction between autonomous/cooperative vehicles, human-driven vehicles, and each other is not yet well understood. The Governor of Washington has therefore requested an analysis of the effects of permitting self-driving, cooperating cars on these roads.

### 1.2 Restatement of the Native Requirements
The future model will need to address the following native problem requirements:

1. **Model the effects on traffic flow** as a function of:
   - the **number of lanes**,
   - **peak and/or average traffic volume**,
   - the **percentage of vehicles using self-driving, cooperating systems**.
2. **Represent cooperation between self-driving cars** (platooning/coordination behavior).
3. **Represent the interaction between self-driving and non-self-driving vehicles** (mixed traffic).
4. **Apply the model to the provided road data** for I-5, I-90, I-405 and SR 520 using the staged spreadsheet.
5. **Answer the policy questions:**
   - How will effects change as the share of self-driving cars rises from **10% → 50% → 90%**?
   - Do **equilibria** exist (and in what sense — flow/behavioral/system-level)?
   - Is there a **tipping point** where performance changes markedly?
   - Under what conditions, if any, should **lanes be dedicated** to self-driving vehicles?
   - Do the model results suggest **any other policy changes**?

### 1.3 Deliverables
The future solving effort is expected to produce:
- a documented traffic-flow model (analytical and/or simulation-based),
- a data-driven parameterization for the four corridors,
- comparative performance characterizations across the 10%/50%/90% autonomy-share scenarios,
- an equilibria/tipping-point characterization,
- an assessment of dedicated-lane policies and other policy recommendations,
- a written report with assumptions, validation evidence, and sensitivity analysis.

---

## 2. Objectives and Subproblems

### 2.1 Overall Objective
To design a model that quantifies how the effective capacity, throughput, and travel-time/delay performance of the four target corridors will respond to increasing penetration of self-driving, cooperating vehicles, and to translate that into policy guidance.

### 2.2 Subproblems

- **SP1 — Capacity as a function of autonomy share.** Define and relate the key capacity quantities:
  effective lane capacity, vehicle throughput, and how they change with the fraction `p` of cooperating/self-driving vehicles (p ∈ {0.10, 0.50, 0.90} as required checkpoints, with continuous sweep between).
- **SP2 — Cooperation mechanism (AV–AV).** Model how cooperating vehicles form platoons, how minimum headway shortens with coordination, and how platoon size/formation times affect lane capacity.
- **SP3 — Mixed interaction (AV–HDV).** Model the interaction between cooperative and human-driven vehicles, including the effect of human reaction-time uncertainty and mixed-fleet headway distributions.
- **SP4 — Network/corridor application.** Map the model onto the supplied segmentation data (route, milepost spans, lane counts by direction, ADT) for I-5, I-90, I-405, SR 520.
- **SP5 — Equilibrium & tipping-point analysis.** Characterize whether stable equilibria exist and whether a marked performance change (tipping point) appears as `p` increases.
- **SP6 — Dedicated-lane policy analysis.** Determine, as a function of `p` and demand, when reserving lane(s) for AVs improves (or worsens) overall system performance.
- **SP7 — Additional policy implications.** Derive secondary policy insights (ramp management, demand pricing, adoption incentives, mixed-fleet transition guidance).

### 2.3 Key Questions to be Resolved at Modeling Time
- What is the correct definition of "equilibrium" here — a fixed-point in a flow–density relation, a routing/choice equilibrium, or a behavioral/platoon-formation equilibrium?
- What constitutes a "marked" performance change (threshold metric: delay, throughput, travel time)?
- How should a partial market share map onto physical lane usage under a dedicated-lane regime?

---

## 3. Assumptions

Assumptions will be split into categories, each with a justification and a planned validation approach.

### 3.1 Physical / Traffic-Flow Assumptions
- **A1. Steady-state analytical base.** The base car-following/flow model will assume steady-state (or quasi-steady) conditions; dynamic transients (shockwaves, incidents) will be layered later or handled in simulation.
  - *Justification:* steady-state relations (fundamental diagram) are tractable and standard for capacity analysis.
  - *Validation:* compare steady-state predictions against a microsimulation that includes transients.
- **A2. Homogeneous lane behavior.** Within a segment, lanes will initially be treated as identical; heterogeneity (HOV, ramps, curvature) will be treated via adjustment factors.
- **A3. Deterministic demand levels.** ADT from the spreadsheet will be used as the demand driver, converted to peak/average flow using an assumed (to-be-established) peak-hour factor.
  - *Validation:* sensitivity testing over a range of peak-hour factors.
- **A4. Directional independence.** The two directions (INCR/DECR MP) will initially be modeled separately; cross-direction effects (e.g., shared ramps) will be treated as a refinement.

### 3.2 Behavioral / Technology Assumptions
- **A5. Capacity gain mechanism.** Self-driving, cooperating vehicles will be assumed to reduce effective headway via shorter reaction time and coordinated platooning.
- **A6. Cooperation benefit scaling.** The benefit of cooperation will be modeled as increasing with the local density of cooperative vehicles (platooning requires nearby partners).
- **A7. Human drivers remain conservative.** Human-driven vehicle headways will remain governed by established (larger) safe-following-distance behavior.
- **A8. Adoption is exogenous.** The autonomy share `p` will be treated as an exogenous scenario parameter (10%, 50%, 90%) rather than a market-equilibrium outcome, unless a later sub-model endogenizes it.
- **A9. Compliance / interoperability.** Cooperating vehicles will be assumed interoperable across manufacturers (a policy assumption that must be flagged).

### 3.3 Simplifying / Scope Assumptions
- **A10. No induced demand in the base model** (latent demand effects deferred to sensitivity analysis).
- **A11. Single-occupancy focus.** Occupancy effects (carpooling, shared AVs) deferred or treated as an extension.
- **A12. Data quality.** The spreadsheet is accepted as the ground truth for lane counts and 2015 ADT, with known missing values handled per Section 4.

### 3.4 Assumption → Validation Map
Each of A1–A12 will be revisited during validation (Section 7); the plan is to mark assumptions as "supported," "weakly supported," or "untested," and to run sensitivity analysis on the most consequential ones (A5, A6, A7, A8).

---

## 4. Data Processing Plan

### 4.1 Data Inventory
The staged dataset (`data/2017_MCM_Problem_C_Data.csv`) provides one row per directional road segment with the fields:

| Field | Role in the plan |
|---|---|
| `Route_ID` | Corridor identifier (I-5, I-90, I-405, SR 520 among others) |
| `startMilepost`, `endMilepost` | Segment boundaries; used to compute segment length and to order segments |
| `Average daily traffic counts Year_2015` | Demand driver (ADT) |
| `RteType (IS / SR)` | Classifies Interstate vs State Route for capacity baseline |
| `Number of Lanes DECR MP direction` | Directional lane count (SB for N–S, WB for E–W) |
| `Number of Lanes INCR MP direction` | Directional lane count (NB for N–S, EB for E–W) |
| `Comments` | Auxiliary notes; known to contain missing values and landmark references (e.g., interchanges) |

### 4.2 Preprocessing Steps (planned)
1. **Load and schema confirmation.** Parse the CSV, normalize column names, verify dtypes.
2. **Route filtering.** Retain the four corridors of interest (I-5, I-90, I-405, SR 520) for the target analysis; other routes may be kept as comparison context.
3. **Segment sanitization.**
   - Validate that `endMilepost > startMilepost`; flag/inspect anomalies.
   - Compute `segment_length = endMilepost − startMilepost`.
   - Ensure contiguous, non-overlapping coverage per direction; document gaps.
4. **Missing-value handling.** `Comments` is expected to contain missing values — this is an auxiliary field and will be masked rather than imputed into core variables. Any missing numeric lane/ADT entries will be resolved via (a) carry-forward within the same direction, (b) interpolation between adjacent mileposts, or (c) nearest-neighbor by corridor/direction, with all choices logged.
5. **Directional reshaping.** Convert the two lane-count columns into a long format keyed by (Route, direction, segment) to model each direction symmetrically.
6. **Lane/ADT sanity checks.** Flag physically implausible lane counts or ADT values for manual review (no cleaning decisions frozen yet).
7. **Units and consistency.** Confirm ADT units (vehicles/day), milepost units (miles), and lane counts (integer lanes).
8. **Provenance log.** Record every transformation so the parameterization is reproducible.

### 4.3 Feature Construction (planned)
- **Capacity baseline per segment:** a lane-based HCM-style capacity baseline using `RteType` and lane count.
- **Demand ratio:** a demand-to-capacity (v/c) style ratio at the ADT or peak-hour level (definition to be fixed).
- **Autonomy scenario column:** replicate/expand each segment across `p ∈ {0.10, 0.50, 0.90}` (and a continuous grid) for scenario analysis.
- **Corridor aggregation keys:** county/corridor grouping so that results can be reported both at segment level and at corridor level.
- **Bottleneck indicators:** derived flags for locations where v/c is high, informed by the `Comments` landmarks (interchanges, intersections) — used only as descriptive context.
- **Peak-hour conversion feature:** an assumption-driven transformation from ADT to peak-hour flow (e.g., via a peak-hour factor and directional split), to be calibrated as a scenario variable rather than a fixed constant.

### 4.4 Data Usage Strategy
- **Calibration/target data:** the spreadsheet supplies geometry (lanes) and demand (ADT). Where the model requires behavioral parameters (headways, reaction times, platoon formation rates), these will come from the literature or from clearly labeled assumptions — the dataset itself does not contain behavioral measurements.
- **Train/validation separation (conceptual):** because the dataset is a single 2015 snapshot, no temporal train/test split is possible. Instead, validation will rely on internal consistency, literature benchmarks, and simulation cross-checks (Section 7).
- **Held-out segments:** a subset of segments may be withheld from informal parameter tuning to check that the model generalizes across corridors.

---

## 5. Candidate Model Framework

The plan is a **layered, multi-scale framework** rather than a single model, so that each candidate's strengths cover another's limitations.

### 5.1 Layer A — Analytical Capacity / Fundamental-Diagram Model
- **Idea:** Extend a car-following/headway-based capacity relation to mixed traffic. Effective capacity per lane will be expressed as a function of the headway distribution, which in turn depends on the mix of AV–AV, AV–HDV, and HDV–HDV vehicle pairs weighted by `p`.
- **Core variables:** `p` (autonomy share), headways (by interaction type), free-flow speed, critical density, jam density, lane count, demand flow.
- **Mathematical ideas:** expected-headway mixture model; capacity as `1/E[headway]` style relation; piecewise or smooth fundamental diagram with `p`-dependent parameters.
- **Advantages:** transparent, fast, parametrically interpretable, directly answers the 10/50/90% question.
- **Limitations:** steady-state only; treats platooning statistically rather than dynamically.

### 5.2 Layer B — Platoon / Cooperation Model
- **Idea:** Model the formation, growth, and dissolution of cooperative platoons as a stochastic process; translate platoon statistics into effective capacity.
- **Mathematical ideas:** Markov/queuing-style platoon-formation models; random-encounter reasoning; platoon-size distributions; penetration-dependent string stability.
- **Advantages:** captures AV–AV cooperation explicitly (SP2) and explains nonlinear/tipping behavior.
- **Limitations:** requires assumption-heavy formation parameters.

### 5.3 Layer C — Microsimulation (Corridor-Level)
- **Idea:** A microscopic traffic simulation in which AV/HDV car-following and lane-changing rules differ, with platooning logic and mixed-fleet headways, run on the four corridors' segment geometry.
- **Mathematical/algorithmic ideas:** car-following (e.g., IDM/Gipps-style) and lane-changing rules; AV-specific shorter desired headways; platoon controller; Monte Carlo scenario sampling.
- **Advantages:** captures dynamics, merging, bottlenecks; can validate Layer A/B.
- **Limitations:** computational cost; calibration burden; results sensitive to behavioral parameter choices.

### 5.4 Layer D — Network / Assignment and Policy Layer
- **Idea:** Represent each corridor as a capacity-constrained link (or a small network) and analyze flow allocation, dedicated lanes, and equilibria.
- **Mathematical ideas:** fundamental-diagram-constrained link performance functions; user equilibrium / system optimum formulations; dedicated-lane capacity partitioning (a fraction of lanes reserved for AVs vs shared lanes).
- **Advantages:** directly supports SP5 (equilibria) and SP6 (dedicated lanes).
- **Limitations:** depends on demand assumptions and on the capacity functions produced by Layers A–C.

### 5.5 Layer E — Scenario & Sensitivity Engine
- **Idea:** Wrap the above in a scenario grid over `p`, demand level, lane configuration, and behavioral parameters to locate tipping points and equilibria.
- **Mathematical ideas:** parameter sweeps, bifurcation-style analysis over `p`, threshold detection.

### 5.6 Variable Glossary (to be finalized)
- **Exogenous/scenario:** autonomy share `p`, demand level, peak-hour factor, dedicated-lane allocation, number of lanes, `RteType`.
- **Endogenous/state:** effective lane capacity, throughput, speed, density, travel time/delay, platoon size distribution, equilibrium flow.
- **Behavioral parameters:** AV desired headway, HDV reaction time, platoon coordination gain, lane-change aggressiveness.

### 5.7 Model-Selection Intent
The plan is to use **Layer A as the interpretable backbone**, **Layer B to capture the cooperation nonlinearity**, **Layer C to validate and add realism**, and **Layer D to answer policy/equilibrium questions** — with Layer E coordinating all scenario runs. Dependencies: C validates A/B; D consumes outputs of A/B/C; E orchestrates.

---

## 6. Implementation Roadmap

### 6.1 Workflow (phased)
1. **Phase 1 — Environment & data pipeline.** Set up the repo skeleton (`code/`, `data/`, `results/`, `logs/`), implement the preprocessing described in Section 4, and produce a clean, logged segment table.
2. **Phase 2 — Layer A implementation.** Code the mixture-headway capacity model; expose `p`, lane count, and demand as inputs.
3. **Phase 3 — Layer B implementation.** Add stochastic platoon formation and derive platoon-based capacity corrections.
4. **Phase 4 — Layer C implementation.** Build the microsimulation for the corridor geometry; compare against Layers A/B.
5. **Phase 5 — Layer D implementation.** Build the link-performance/equilibrium and dedicated-lane models.
6. **Phase 6 — Scenario engine (Layer E).** Sweep `p`, demand, and lane policies; generate the equilibrium/tipping diagnostics.
7. **Phase 7 — Packaging.** Produce figures/tables from the (future) runs, and write the final report.

### 6.2 Required Modules (planned)
- `data_loader` — CSV ingestion and schema handling.
- `preprocess` — cleaning, segment length, directional reshaping, missing-value logic, logging.
- `capacity_model` — Layer A fundamental-diagram/mixture-headway model.
- `platoon_model` — Layer B stochastic cooperation model.
- `microsim` — Layer C corridor simulation.
- `network_policy` — Layer D equilibrium and dedicated-lane analysis.
- `scenarios` — Layer E parameter sweeps and threshold detection.
- `viz` — publication-quality plots (built later, not in this draft).
- `validation` — cross-model comparison and sensitivity harness.

### 6.3 Algorithms / Methods to Be Selected Later
- Car-following and lane-changing update rules for the simulation.
- Platoon-formation stochastic process (e.g., Markov-chain or queuing representation).
- Root-finding / fixed-point iteration for equilibria.
- Threshold/change-point detection for tipping-point identification.
- Global sensitivity analysis (e.g., variance-based) over assumptions A5–A8.

### 6.4 Reproducibility & Engineering Notes
- All parameters will be centralized in a single config to support scenario sweeps.
- Every run will write a log and a machine-readable results artifact into `results/` and `logs/`.
- Random seeds will be fixed for simulation-based layers.
- Unit and sanity tests will be added per module.

---

## 7. Validation Strategy

### 7.1 Evaluation Metrics (planned)
- **Capacity metrics:** effective per-lane capacity, corridor throughput.
- **Level-of-service metrics:** average speed, density, travel time, delay relative to free-flow.
- **Scenario-difference metrics:** marginal change in performance per increment of `p`; threshold/tipping indicators.
- **Policy metrics:** system-wide delay under dedicated-lane vs shared-lane regimes; equity/feasibility flags.

### 7.2 Validation Methods
- **Internal consistency:** dimensional checks, limiting-case checks (at `p = 0` the model should reduce to a conventional-capacity baseline; as cooperation gain → 0 the AV benefit should vanish).
- **Cross-model validation:** compare Layer A (analytical) against Layer C (microsimulation) on identical scenarios.
- **Literature benchmarking:** compare effective-capacity gains at given `p` against published mixed-traffic capacity results.
- **Data-consistency validation:** verify that the parameterized model produces demand levels and lane usage consistent with the spreadsheet's ADT and lane counts on each corridor.
- **Monotonicity/behavioral checks:** expect (and test) monotone non-decreasing benefits in `p`, saturating behavior at high `p`, and no unphysical capacity inflation.

### 7.3 Sensitivity Analysis
- Sweep behavioral parameters (AV headway, HDV reaction time, platoon coordination gain).
- Sweep demand assumptions (peak-hour factor, directional split, induced demand on/off).
- Sweep structural assumptions (homogeneous vs heterogeneous lanes, compliance/interoperability).
- Report which conclusions are robust vs fragile to these parameters.

### 7.4 Verification of the Plan Itself
- Confirm each of the six native subproblems (SP1–SP7) maps to at least one implemented module and one validation check.
- Maintain an assumptions→evidence table, marking each assumption's status.

---

## 8. Expected Result Interpretation

*(Interpretation framework only — no results are produced in this draft.)*

The future results are expected to be interpreted through the following lenses:

- **Monotone-yet-nonlinear capacity response.** Performance (throughput / delay) is expected to improve with `p`, but likely nonlinearly, because cooperation benefits depend on neighboring AV density (assumption A6).
- **Tipping-point reading.** If the model exhibits a sharp change in slope (in delay or throughput vs `p`), that region will be identified as a candidate tipping point and reported with the sensitivity of its location.
- **Equilibrium reading.** Equilibria will be interpreted as fixed points of the flow/capacity or assignment system; the plan is to report existence, multiplicity, and stability (stable vs unstable), and to clarify which equilibrium notion applies.
- **Dedicated-lane reading.** A dedicated-lane policy will be interpreted via a trade-off: reserving lanes reduces capacity available to HDVs while potentially increasing AV throughput; the interpretation will identify the `p`/demand regimes where the trade-off favors dedication.
- **Scenario comparison.** The 10%/50%/90% checkpoints will be presented as a progression, with the marginal benefit of each step interpreted against policy cost.
- **Policy implications.** Secondary findings (e.g., transition-period management, interoperability requirements) will be framed as conditional recommendations that are valid only within the model's stated assumptions.

All interpretations will be explicitly conditioned on the assumptions in Section 3 and the sensitivity results in Section 7.

---

## 9. Limitations and Improvements

### 9.1 Anticipated Limitations
- **Single-snapshot data.** The dataset is a single-year (2015) cross-section with no time series, limiting dynamic calibration.
- **No behavioral ground truth.** Headway/reaction parameters must come from assumptions or literature, not from the provided file.
- **Steady-state bias.** Analytical layers ignore transients, incidents, and weather.
- **Aggregation effects.** Corridor-level results may mask localized bottlenecks.
- **Exogenous adoption.** Treating `p` as a scenario parameter sidesteps market/adoption dynamics.
- **Exclusion of induced demand and occupancy effects** in the base model.

### 9.2 Planned Improvements / Extensions
- Endogenize adoption (market/behavioral feedback on `p`).
- Add temporal demand profiles (peak vs off-peak) and dynamic traffic assignment.
- Incorporate ramp metering, incident modeling, and weather.
- Include multi-occupancy and shared-AV effects.
- Extend to a fuller regional network beyond the four corridors for spillover analysis.
- Formalize the tipping-point/equilibrium analysis (e.g., bifurcation and stability theory).
- Calibrate behavioral parameters against external empirical AV platooning studies.

### 9.3 Risk Register
- **High risk:** behavioral parameter uncertainty driving tipping-point location.
- **Medium risk:** data gaps / missing lane or ADT values distorting per-segment capacity.
- **Medium risk:** definition ambiguity of "equilibrium" affecting conclusions.
- **Low risk:** computational cost of large scenario sweeps (mitigated by analytical surrogates).

---

*End of planning draft. No problem solving, data analysis, or results are included by design; this document will be used to guide subsequent modeling work.*
