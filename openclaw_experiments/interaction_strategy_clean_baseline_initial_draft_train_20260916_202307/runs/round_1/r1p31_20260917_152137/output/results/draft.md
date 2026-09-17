# Modeling Blueprint Draft — Power Profile of a Cyclist (MCM 2022, Problem A)

**Document type:** Modeling plan / roadmap (not a solution).
**Status:** Initial draft for planning only. No data has been analyzed, no model has been fitted, and no results are reported here.
**Problem ID:** `2022_Power_Profile_of`

---

## 1. Problem Background and Restatement

In bicycle road races such as individual time trials (ITTs), a rider aims to complete a fixed course in the shortest possible time. A rider's power curve describes the maximum power they can sustain for a given duration, and sustaining high power accumulates fatigue that reduces future sustainable power. The rider therefore faces a continuous, history-dependent control problem: choose power output as a function of position on the course so as to minimize total finishing time while respecting both the instantaneous power ceiling and the cumulative energy/fatigue budget.

**Restated objective (to be addressed by the eventual model):** develop a model that determines the relationship between a cyclist's position on a course and the power they should apply, explicitly accounting for energy limits and past exertion.

**Sub-requirements implied by the problem statement:**

1. Define power profiles for at least two rider types — a time trial specialist and a contrasting type — with consideration of gender differences.
2. Apply the eventual model to (a) the 2021 Olympic ITT course in Tokyo and (b) a self-designed course containing at least four sharp turns and a nontrivial road grade, ending near its start.
3. Assess the impact of weather, especially wind direction and strength.
4. Evaluate sensitivity of performance to deviations from the target power distribution.
5. Extend the framework to a six-rider team time trial (TTT), with particular attention to the finish time of the fourth rider.

**Deliverables named by the problem:** (i) a two-page race guidance document for a Directeur Sportif focused on one rider and one course; (ii) a full ≤25-page solution comprising a one-page summary sheet, the complete solution, and the two-page rider guidance.

**Scoping note for this draft:** this document plans *how* the above will be modeled. It deliberately stops before any data work or computation.

---

## 2. Objectives and Subproblems

The planning effort decomposes the problem into the following subproblems, each of which will later be matched to methods, data, and validation criteria.

- **SP1 — Power-profile representation.** Construct a parametric representation of the sustainable-power-vs-duration relationship (the power curve) per rider type and per gender, and define how fatigue from prior exertion will reduce the *available* power going forward.
- **SP2 — Position-to-power policy.** Formulate the decision of applied power as a function of course position/state (speed, grade, distance remaining, accumulated work), producing a race plan (target power or target speed trajectory) rather than a single constant.
- **SP3 — Motion/dynamics model.** Define the equations that map applied power, rider/course characteristics, and environment into speed and hence time, so that a power plan can be evaluated against finish time.
- **SP4 — Course modeling.** Represent (a) the 2021 Tokyo Olympic ITT course and (b) a designed multi-turn, graded loop course as position-indexed profiles of grade, curvature, and surface/state.
- **SP5 — Environment (weather) modeling.** Incorporate wind (direction and strength) and related conditions into the dynamics, and plan how performance will be assessed across weather scenarios.
- **SP6 — Sensitivity and robustness.** Define how deviations from the target power distribution (execution error) will be characterized and how sensitive finishing time will be to those deviations.
- **SP7 — Team time trial extension.** Extend the single-rider framework to six riders, incorporating drafting/relay structure and a team pacing policy, with emphasis on the fourth rider's finish time.
- **SP8 — Communication deliverables.** Plan the structure of the two-page Directeur Sportif guidance and the overall solution document, ensuring the model output is operationalized into actionable race guidance.

**Deliverable mapping (planned):** SP1–SP6 feed the analysis narrative and figures; SP7 adds a dedicated section; SP8 determines the summary sheet and the two-page guidance.

---

## 3. Assumptions

The following assumptions are proposed as a starting set. Each is paired with a justification and a planned validation approach; assumptions are expected to be revised during implementation.

**A1. Deterministic power curve per rider.** A rider's maximum sustainable power as a function of duration will be treated as a fixed, known curve for a given rider type/gender. *Justification:* enables tractable optimization and matches the problem's power-curve framing. *Validation:* compare modeled curve shape against published/derived endurance-power data ranges; test sensitivity to curve-shape choice.

**A2. Fatigue is history-dependent and monotone in accumulated work.** Degradation of available power will be modeled as a function of accumulated work/exertion and/or time-at-intensity rather than as an instantaneous state. *Justification:* the objective explicitly names "energy limits and past exertion." *Validation:* compare alternative fatigue kernels and check plausibility of recovery/limits.

**A3. Quasi-steady (or segment-lumped) dynamics.** Over short intervals the rider is modeled in quasi-steady state (or each segment lumped to an average), neglecting very fast transient dynamics. *Justification:* keeps optimization well-posed and reduces data needs. *Validation:* check sensitivity of finish time to segment resolution.

**A4. Constant or piecewise-constant environmental conditions per run.** Wind and other weather will be fixed per scenario (or piecewise along the course), not modeled as fully stochastic within a run. *Justification:* isolates the effect of weather variables as the problem requests. *Validation:* scenario sweeps over wind speed/direction.

**A5. Course profiles can be represented as position-indexed functions.** Grade, curvature, and wind exposure will be approximated by smooth or piecewise functions of distance along the course. *Justification:* supports the position-to-power objective. *Validation:* resolution/smoothing sensitivity.

**A6. Rider parameters (mass, aerodynamics, rolling resistance, drivetrain efficiency) are estimated constants per rider type.** *Justification:* needed to convert power to speed. *Validation:* literature ranges and sensitivity analysis; note these are calibration parameters.

**A7. Gender differences are captured primarily through scaling of power capacity (and, if supported, rider parameters).** *Justification:* the problem asks to "consider gender differences." *Validation:* compare against reported power distributions for female vs male riders; test alternative scaling forms.

**A8. Team-time-trial simplification.** Drafting benefit will be modeled with simplified, well-documented shielding/relay rules rather than full fluid dynamics. *Justification:* required for a six-rider extension to be tractable. *Validation:* sanity checks against known drafting-savings ranges and relay-rotation logic.

**A9. Objective is deterministic time minimization (expected time minimization if any variability is later added).** *Justification:* matches "complete a course in the shortest time." *Validation:* if stochastic elements are introduced, compare deterministic vs expected-time policies.

---

## 4. Data Processing Plan

**Note:** no data has yet been inspected. This section plans what data would be needed, sourced, and prepared. The workspace currently contains empty `code/`, `data/`, `logs/`, `results/` folders and only the problem text; no external dataset has been supplied.

**4.1 Data sources to be assembled (candidate, subject to availability review):**
- *Course data:* elevation/grade profiles and turn geometry for the 2021 Tokyo Olympic ITT course; a self-designed course defined by the team (with ≥4 sharp turns, nontrivial grade, ending near its start — i.e., a near-loop).
- *Rider/power data:* published power-curve/endurance-power characterizations for time trial specialists and contrasting rider types, differentiated by gender where possible; typical rider physical and aerodynamic parameters (mass, Cd·A, rolling resistance, drivetrain efficiency).
- *Environmental data:* representative wind speed/direction and other weather scenarios for the target course and season.
- *TTT/reference data:* relay/speed ranges and drafting-savings references for the team extension.

**4.2 Preprocessing plan (to be applied later, not now):**
- Convert raw elevation/geometry into a cleaned, distance-indexed course profile (grade, curvature, turns).
- Segment courses into analysis units (by distance or by constant-grade/turn segments); decide segment resolution.
- Standardize units and coordinate frames; align course position with the control variable.
- De-duplicate, smooth (with documented method), and flag outliers or gaps in any downloaded profiles.
- Assemble a consistent rider parameter table with source provenance for each value.

**4.3 Feature construction plan:**
- Position-indexed features: cumulative distance, local grade, curvature/turn indicator, distance-to-go.
- State features: current speed, accumulated work/energy expended, fatigue state.
- Environmental features: headwind/tailwind/crosswind decomposition relative to course heading.
- Derived features: aerodynamic and gravitational power components as functions of state and environment.

**4.4 Data usage strategy:**
- Course data → SP4 (course modeling) inputs.
- Power/endurance data → SP1 calibration of power curves by type/gender.
- Weather scenarios → SP5 scenario design.
- Rider parameters → SP3 dynamics.
- All data used to *parameterize and contextualize* the model; none used to pre-compute final answers in this planning phase.

**4.5 Data-quality risks to track:** availability of exact Olympic course geometry, representativeness of published power curves, uncertainty in aerodynamic/rolling parameters, and handling of missing/ambiguous turn data.

---

## 5. Candidate Model Framework

This section lists candidate modeling approaches and mathematical ideas to be compared later. It is intentionally non-committal; method selection will follow data review.

**5.1 Power-curve / fatigue submodels (SP1):**
- Parametric power-duration curves (e.g., hyperbolic, two/three-parameter critical-power-type forms, or piecewise envelopes).
- Fatigue dynamics: an energy/w' depletion-type reservoir model; an exponential or power-law fatigue kernel; or a state-space "fatigue-impulse" accumulator.
- Candidate comparison criterion: flexible fit + interpretable parameters + stability under optimization.

**5.2 Dynamics (SP3):**
- Point-mass motion with force balance: propulsive power vs. aerodynamic drag, rolling resistance, gravitational component, and inertia.
- Options: quasi-steady per segment, or ordinary/partial differential equation in distance/time with inertia retained.
- Environment coupling: airspeed corrected for wind vector relative to heading.

**5.3 Position-to-power policy (SP2) — optimization formulations:**
- Optimal control / calculus of variations: minimize finish-time functional subject to dynamics, power ceiling, and energy/fatigue constraints.
- Nonlinear program (NLP) discretization over the course (direct transcription) as a practical alternative.
- Dynamic programming in a discretized state space (position × speed × fatigue).
- Heuristic/practical policies for comparison (constant power, constant speed, grade-based rules), used as baselines.
- Variables to be tracked: control = power (or target speed); states = speed, fatigue/energy; parameters = rider and environment; objective = total time.

**5.4 Course and environment (SP4, SP5):**
- Course as a lookup/functional model mapping position → (grade, curvature, wind exposure).
- Weather as a set of deterministic scenarios (wind speed/direction, plus optional temperature/air-density effects), enabling scenario comparison.

**5.5 Sensitivity/robustness (SP6):**
- Perturbation model for execution error: deviations in applied power (bias, noise, segment-level miss) relative to the recommended plan.
- Robust or chance-constrained variants to test stability of the policy.

**5.6 Team time trial (SP7):**
- Multi-agent extension with drafting benefit and relay/rotation logic; team objective defined on the team (and specifically the fourth rider's) finish time.
- Candidate coordination policies: fixed rotation schedule, leader-protection policy, and optimized shared pacing.

**Advantages/limitations to record for each candidate:** computational cost, data requirements, interpretability for a Directeur Sportif, and fidelity to the stated objective and constraints.

---

## 6. Implementation Roadmap

Planned modules and workflow (to be built after method selection):

- **M1 Course builder:** ingest/constitute course profiles (Tokyo ITT and designed course), segment them, expose position-indexed grade/curvature.
- **M2 Rider/power module:** represent power curves by rider type and gender; encode fatigue/energy dynamics.
- **M3 Dynamics simulator:** given a power policy and scenario, integrate motion to produce speed and time trajectories.
- **M4 Pacing optimizer:** implement the chosen optimization method (optimal control / NLP transcription / DP) to produce a target power distribution by position.
- **M5 Scenario engine:** run weather scenarios and course variants; manage parameter sweeps.
- **M6 Sensitivity module:** inject execution deviations and quantify finish-time effects.
- **M7 TTT module:** extend dynamics and optimization to six riders with drafting/relay logic; extract fourth-rider finish time.
- **M8 Reporting/visualization:** produce figures, summary tables, and the two-page Directeur Sportif guidance structure (planned, not generated in this phase).

**Planned workflow sequence:** M1 → M2 → M3 (validate forward simulation) → M4 (single-rider optimal plan) → M5 (weather) → M6 (sensitivity) → M7 (TTT) → M8 (deliverables).

**Engineering considerations:** reproducible configuration of parameters; separated scenario definitions; logging of runs; versioned outputs; clear interfaces so submodels can be swapped without rewriting the pipeline.

---

## 7. Validation Strategy

Validation will be planned at multiple levels; no validation is executed in this draft.

- **Unit/consistency checks:** power balance closes; units consistent; limiting cases (flat course, no wind, constant power) behave sensibly; energy/fatigue constraints respected.
- **Plausibility checks:** resulting speeds/powers fall within documented ranges for the rider types; finishing times reasonable for the course distances.
- **Cross-method comparison:** compare optimal-control/NLP/DP solutions and baseline heuristics; agreement increases confidence.
- **Criterion metrics (to be defined):** total finish time; deviation from target power distribution; constraint-violation rate; robustness margins under perturbation; consistency of TTT relay behavior.
- **Validation methods:** internal consistency, comparison against reference ranges and independent formulations, and boundary-case testing.
- **Sensitivity analysis plan:** sweep rider-parameter uncertainty (mass, Cd·A, rolling resistance), power-curve shape, fatigue-kernel choice, segment resolution, and weather severity; identify dominant drivers and stability of the recommended policy.
- **Robustness assessment:** characterize how finish time changes with bias and noise in executed power, addressing the problem's explicit sensitivity requirement.

---

## 8. Expected Result Interpretation

This section anticipates *how results will be read*, not the results themselves.

- The eventual model is expected to yield a position-dependent target power (and implied speed) trajectory per rider/course, plus a predicted finish time — a race plan.
- Weather scenarios are expected to be compared in terms of plan adaptation (e.g., where power should be increased or conserved under wind), with interpretation framed as guidance rather than fixed instructions.
- Sensitivity results are expected to be interpreted as tolerance bands: how precisely a rider must follow the plan, and where deviations hurt most.
- The TTT extension is expected to produce a coordinated relay/pacing plan and an interpretation of the fourth rider's finish-time dependence on team policy.
- All interpretations will be presented as *conditional on assumptions and inputs*, with uncertainty explicitly acknowledged.

---

## 9. Limitations and Improvements

**Anticipated limitations:**
- Simplified fatigue and drafting models may not capture full physiological/physical complexity.
- Data availability (exact course geometry, representative power curves, aerodynamic parameters) will bound fidelity.
- Deterministic treatment may under-represent real variability in execution and environment.
- Optimal solutions may be sensitive to parameter choices and model structure.

**Planned improvements / extensions:**
- Refine fatigue and recovery modeling with richer physiological state; consider stochastic/chance-constrained pacing.
- Improve environment modeling (spatially varying wind, air density/temperature effects).
- Richer multi-rider interaction for the TTT and, potentially, general peloton/pack tactics.
- Systematic parameter calibration and uncertainty quantification to strengthen the Directeur Sportif guidance.

---

## Appendix — Planning Checklist

- [ ] Confirm data sources and availability; document provenance.
- [ ] Finalize assumption set (Section 3) and justification log.
- [ ] Select submodels from Section 5 candidates.
- [ ] Instantiate implementation modules (Section 6).
- [ ] Execute validation plan (Section 7).
- [ ] Produce deliverables: summary sheet, full solution, two-page Directeur Sportif guidance.

*End of planning draft. No data analysis, modeling, computation, or results are included by design.*
