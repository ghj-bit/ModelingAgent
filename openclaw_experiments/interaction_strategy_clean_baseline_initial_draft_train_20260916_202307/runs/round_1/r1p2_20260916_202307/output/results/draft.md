# The Bicycle Wheel Problem — Initial Modeling Plan (Draft)

> **Document type:** Modeling blueprint / planning draft
> **Status:** Not a solution. No data has been analyzed, no model has been fitted, and no
> numerical results are reported here. All content is forward-looking and describes how the
> problem *will be* approached.

**Problem ID:** `2001_The_Bicycle_Wheel`
**Title:** The Bicycle Wheel Problem
**Source:** MCM 2001

---

## 1. Problem Background and Restatement

Cyclists may choose between two basic rear-wheel designs: **wire-spoked wheels** (lighter)
and **solid disk wheels** (more aerodynamic). For road races a solid wheel is generally not
used on the front, so the decision reduces to choosing the **rear** wheel while the **front**
wheel is held fixed as a spoked wheel. The director sportif wants a systematic tool that maps
a given race course (hills/grades, weather, wind) to a wheel recommendation.

The problem statement defines three tasks:

- **Task 1.** Produce a table of **wind speeds at which the power required for a solid rear
  wheel becomes less than that for a spoked rear wheel**, tabulated across **road grades from
  0% to 10% in 1% increments**. The rider starts at the bottom of the hill at **45 kph**, and
  the **deceleration is proportional to the road grade**, calibrated so that the rider loses
  about **8 kph for a 5% grade over 100 m**.
- **Task 2.** Demonstrate, with an **example**, how such a table could be used on a specific
  **time-trial course**.
- **Task 3.** Assess whether the table is an **adequate decision aid**, and propose **other
  ways** to make the wheel-selection decision.

The eventual deliverable is therefore a *decision-support framework* built on a physics-based
power model (and possibly richer models), not merely a lookup table.

This planning draft lays out the roadmap used to reach that framework in later phases.

---

## 2. Objectives and Subproblems

### 2.1 Overarching objective
Construct a defensible, physically grounded, and usable procedure that tells a team **which
rear wheel (spoked vs. solid) to choose for a given course and conditions**, and to state the
conditions (grade, wind speed, and other factors) under which the recommendation flips.

### 2.2 Subproblem decomposition

| Sub-ID | Description | Maps to |
|--------|-------------|---------|
| SP-1 | Model the mechanical power required to propel the bicycle/rider up a graded road as a function of speed, grade, mass, and resistance terms | Task 1 |
| SP-2 | Model the aerodynamic drag contribution for **spoked** vs. **solid** rear wheels, including the effect of relative wind (headwind/tailwind/crosswind) | Task 1 |
| SP-3 | Define the rider **speed profile** on a hill using the given start speed and the grade-proportional deceleration rule | Task 1 |
| SP-4 | Derive the **break-even wind speed** for each grade in 0%–10% (1% steps) where solid-wheel power requirement drops below spoked-wheel power requirement | Task 1 |
| SP-5 | Build a **course-to-table lookup / decision procedure** and demonstrate it on an illustrative time-trial course | Task 2 |
| SP-6 | Critically **evaluate the adequacy** of the table and propose richer decision aids (e.g., segment-by-segment simulation, multi-factor scoring, sensitivity-aware advice) | Task 3 |

### 2.3 Deliverables (planned)
- A **decision table / surface** indexed by grade and wind speed (SP-4).
- A **worked course example procedure** with the steps the user would follow (SP-5).
- A **critique and extension menu** of alternative decision methods (SP-6).

---

## 3. Assumptions

The following assumptions are *candidates* to be adopted, defended during modeling, and later
tested. Each is paired with a justification and a planned validation approach.

### 3.1 Physical / mechanical assumptions
- **A1 — Steady power model.** Propulsive power at a point is the sum of rolling resistance,
  aerodynamic drag, and gravity (grade) components. *Justification:* standard cycling power
  balance. *Validation:* compare structure against published cycling power equations.
- **A2 — Negligible drivetrain losses / constant drivetrain efficiency.** *Justification:*
  keeps the two-wheel comparison fair. *Validation:* sensitivity test on efficiency.
- **A3 — Combined rider + bicycle mass is constant and known or treated as a parameter.**
  *Justification:* mass scales gravity and rolling terms. *Validation:* sensitivity sweep.
- **A4 — The front wheel is always spoked**, so only the rear-wheel choice changes drag.
  *Justification:* explicit problem constraint. *Validation:* structural, fixed by statement.
- **A5 — Wheel aerodynamic difference is modeled as a drag-coefficient/area difference**
  between solid and spoked rear wheels. *Justification:* isolates the aerodynamic advantage
  of the disk. *Validation:* compare to published wheel drag data; sensitivity sweep.
- **A6 — Wheel mass difference (spoked lighter) affects acceleration, not steady-state
  power balance**, and will be modeled only if the framework includes acceleration.
  *Justification:* the two wheel types differ in mass and inertia. *Validation:* decide
  whether an inertial term is needed once the speed-profile model (SP-3) is defined.

### 3.2 Grade, speed, and wind assumptions
- **A7 — Hill represented as an inclined plane with constant grade within a segment.**
  *Justification:* matches the triangle/grade definition. *Validation:* contrast with
  piecewise-linear or real elevation profiles in the extension analysis.
- **A8 — Deceleration proportional to road grade, calibrated by the given data point**
  (≈8 kph lost for 5% grade over 100 m; start at 45 kph). *Justification:* supplied by the
  statement. *Validation:* check order of magnitude against the power model; state the
  calibration explicitly.
- **A9 — Wind is horizontal and can be decomposed into headwind/tailwind and crosswind
  components; only the along-course component enters the primary drag model**, with crosswind
  treated as an extension. *Justification:* simplifies Task 1 while acknowledging reality.
  *Validation:* add crosswind as a sensitivity/extension case.
- **A10 — Air density (and thus wind/altitude effects) is treated as constant** in the base
  case. *Justification:* removes a secondary variable. *Validation:* sensitivity sweep on
  density.

### 3.3 Decision / usage assumptions
- **A11 — "Power required is less" is the decision criterion** for Task 1, interpreted as
  the propulsive power needed at the same speed/segment conditions. *Justification:* the task
  is phrased in terms of required power. *Validation:* confirm interpretation consistency.
- **A12 — The table is a first-order decision aid; real courses are non-uniform.**
  *Justification:* drives Task 3. *Validation:* the adequacy critique itself.

> **Note:** Assumptions will be consolidated into a single table with a *risk rating*
> (high/medium/low impact) and an explicit "how it will be tested" column in the modeling
> phase.

---

## 4. Data Processing Plan

The problem provides **no raw dataset**; instead it supplies **parameters, a calibration
rule, and an image**. The "data plan" therefore concerns (a) ingesting the given parameters,
(b) constructing a parameter grid, and (c) preparing derived features for modeling and
presentation.

### 4.1 Inputs to be ingested
- Grade grid: **0%, 1%, …, 10%** (11 values) — the primary independent variable.
- Start speed: **45 kph** (converted to m/s for modeling).
- Deceleration calibration: **≈8 kph loss for 5% grade over 100 m**.
- Fixed front wheel = spoked; variable rear wheel ∈ {spoked, solid}.
- Figure 1 (`image001.png`) as a qualitative visual reference only.

### 4.2 Preprocessing steps (planned)
1. **Unit harmonization** — convert kph ↔ m/s, percent grade ↔ angle, 100 m distance basis.
2. **Grade parameterization** — represent as percent, as sine of angle, and as slope ratio,
   keeping definitions consistent with the problem ('grade = sine of the angle').
3. **Parameter registry** — assemble a single structured parameter dictionary (mass, rolling
   coefficient, drag coefficients/areas, drivetrain efficiency, air density, gravity) with
   placeholder/representative values and clear provenance tags (given vs. assumed).
4. **Wind-speed grid construction** — define candidate wind speeds (including 0 and negative/
   tailwind values if the break-even may fall there) on a reasonable resolution for tabulation.

### 4.3 Feature / variable construction
- **Relative air speed** along the course = rider speed ± along-course wind component.
- **Drag power term** using the relative air speed and the wheel-specific drag coefficient.
- **Gravity power term** from mass, gravity, grade, and speed.
- **Rolling power term** from mass, gravity, rolling coefficient, and speed.
- **Deceleration-derived speed profile** as a function of grade and distance.

### 4.4 Data usage strategy
- All provided numeric facts are treated as **hard constraints** (start speed, calibration
  point, grade range/steps).
- Representative physical constants are treated as **tunable parameters**, clearly flagged,
  and exercised in sensitivity analysis rather than fixed silently.
- No external datasets are required for the core tasks; optional published wheel-drag data
  may be used later to **anchor** A5 and will be cited if adopted.

---

## 5. Candidate Model Framework

### 5.1 Candidate models (to be compared)

| Model | Idea | Advantages | Limitations |
|-------|------|------------|-------------|
| **M1 — Steady power balance (baseline)** | Power = rolling + aero + gravity; solve for break-even wind speed per grade | Simple, transparent, directly matches Task 1 phrasing | Ignores acceleration, cornering, crosswind |
| **M2 — Power balance + calibrated deceleration profile** | Extend M1 with the given grade-proportional speed loss to represent the climb | Uses the stated calibration; more realistic speed on hill | Still segment-averaged; needs careful calibration |
| **M3 — Segment simulation over a course** | Discretize a course into grade/wind segments and accumulate times/work for each wheel | Supports Task 2 example and Task 3 critique | Needs course definition; more computation |
| **M4 — Multi-factor decision score** | Weighted scoring of grade, wind, course length, competition, weather, rider profile | Captures "other considerations" in Task 3 | Weights subjective; needs justification |
| **M5 — Sensitivity/uncertainty model** | Propagate parameter uncertainty into the break-even table | Quantifies robustness of the recommendation | Computational; interpretation overhead |

The plan is to adopt **M1/M2 as the analytical core**, use **M3** to demonstrate Task 2 and to
build the Task 3 critique, and sketch **M4/M5** as recommended extensions.

### 5.2 Key variables (planned symbols)

- Independent: road grade `g`, wind speed `w` (and possibly direction), distance `s`.
- State: rider speed `v` (and its profile along the hill).
- Parameters: combined mass `m`, gravity `k = g_e`, rolling resistance coefficient `C_rr`,
  drag coefficient–area product for spoked `(C_dA)_s` and solid `(C_dA)_d`, drivetrain
  efficiency `η`, air density `ρ`.
- Output: break-even wind speed `w*(g)`; recommendation per course.

### 5.3 Mathematical ideas to be developed
- **Force/power balance:** `P = (F_roll + F_grav + F_aero)·v`, with the aero term using
  relative air speed so that headwind/tailwind shifts required power.
- **Break-even condition:** set `P_solid(g, w) = P_spoked(g, w)` and solve `w*(g)` for each
  grade; interpret sign of `w*` as headwind vs. tailwind regime.
- **Grade-proportional deceleration:** derive `dv/ds` (or `v(s)`) from the given calibration
  and integrate/approximate along the hill.
- **Course accumulation (M3):** sum work or time over segments to compare wheel choices.

### 5.4 Visual/narrative outputs (planned)
- A grade × wind-speed decision **table** and/or **contour/heatmap** of the recommendation.
- A schematic describing how a course is converted into a table lookup (Task 2).
- A decision **flow / extension menu** for Task 3.

---

## 6. Implementation Roadmap

### 6.1 Modules to build
1. **`params`** — parameter registry (given vs. assumed, with units and provenance).
2. **`kinematics`** — grade ↔ angle ↔ slope conversions; start-speed and deceleration profile.
3. **`forces`** — rolling, gravity, aerodynamic (wheel-specific) force/power functions.
4. **`breakeven`** — solve for `w*(g)` per grade; produce the Task 1 table.
5. **`course`** — represent a sample time-trial course as segments; implement lookup and
   alternative simulations (Task 2, Task 3).
6. **`viz`** — table/heatmap and schematic generators.
7. **`report`** — assemble narrative, tables, and figures.

### 6.2 Workflow (phased)
- **Phase 0 — Setup:** freeze assumptions and parameter registry; define units.
- **Phase 1 — Core model:** implement `forces` + `kinematics`; validate at a single point.
- **Phase 2 — Task 1:** implement `breakeven`; generate the grade × wind table.
- **Phase 3 — Task 2:** define an illustrative course; implement `course` lookup/simulation.
- **Phase 4 — Task 3:** run the adequacy critique and build the extension menu (M3–M5).
- **Phase 5 — Sensitivity:** propagate parameter uncertainty; produce robustness statements.
- **Phase 6 — Reporting:** consolidate into the final report (separate from this draft).

### 6.3 Tooling (planned)
- A scripting environment suitable for symbolic/numeric work and plotting; results will be
  reproducible from a single parameter file. *(No code is written in this planning phase.)*

### 6.4 Dependencies / risks to manage
- Ambiguity in "power required" interpretation (same speed vs. same time).
- Uncertainty in drag coefficients and rolling resistance.
- Whether wheel mass/inertia must be modeled for correctness of the recommendation.
- Crosswind modeling complexity.

---

## 7. Validation Strategy

### 7.1 Evaluation metrics / checks (planned)
- **Physical consistency:** power and force terms have correct signs and scales; zero-wind,
  zero-grade degenerate cases behave sensibly.
- **Calibration check:** the deceleration model reproduces the given "≈8 kph per 5% over
  100 m" behavior and the 45 kph start.
- **Monotonicity / trend checks:** break-even wind speed should vary smoothly and plausibly
  with grade; solid-wheel advantage should strengthen with headwind.
- **Cross-model agreement:** M1 vs. M2 vs. M3 should agree in the appropriate limits.

### 7.2 Validation methods
- **Limiting-case analysis** (flat road, no wind, zero friction, etc.).
- **Dimensional/unit audit** of every equation.
- **Independent recomputation** of a few break-even points by a second method (closed-form
  vs. numerical) to confirm agreement.
- **Literature anchoring** of wheel drag and rolling-resistance parameters where available.

### 7.3 Sensitivity analysis
- One-at-a-time sweeps over mass, rolling coefficient, drag coefficients/areas, drivetrain
  efficiency, air density, and deceleration calibration.
- Rank parameters by their influence on `w*(g)`; report which conclusions are robust vs.
  fragile.
- Consider crosswind direction as a scenario sweep rather than a single number.

### 7.4 Adequacy evaluation (Task 3)
- Define criteria for "adequate": accuracy, robustness, usability, and coverage of real
  course features (non-uniform grades, wind shifts, corners, race tactics).
- Test the table against at least one non-uniform course to expose where a single grade+wind
  number is insufficient.

---

## 8. Expected Result Interpretation

*(Interpretation guidance — no results are produced here.)*

- **Task 1 table:** expected to read as a grid where, for each grade, there is a wind speed
  threshold separating "solid rear wheel preferred" from "spoked rear wheel preferred."
  The narrative will explain how the sense of that threshold (headwind vs. tailwind) should
  be interpreted and why.
- **Task 2 example:** will show a *procedure* — decompose the course, find the controlling
  grade/wind conditions, look up the table, and translate the entry into a wheel choice,
  while noting course segments where the choice may differ.
- **Task 3 assessment:** will argue that the table is useful as a **first-order screen** but
  is **limited** for non-uniform courses and multi-factor decisions, and will outline
  extensions (segment simulation, weighted scoring, uncertainty-aware advice).

Deliverables will be framed as **decision support**, explicitly noting the conditions under
which the recommendation is expected to hold or flip.

---

## 9. Limitations and Improvements

### 9.1 Anticipated limitations
- Simplifications (steady state, constant-grade segments, single wind component) may diverge
  from real racing conditions.
- Parameter uncertainty (drag, rolling resistance, mass, efficiency) may materially shift
  break-even wind speeds.
- Treating "required power" as the sole criterion may ignore time-to-completion, tactics,
  and handling/safety (e.g., crosswind stability of a disk wheel).
- The provided visual (Figure 1) is qualitative and not a quantitative data source.

### 9.2 Planned improvements / extensions
- **Segment-level simulation (M3)** over realistic elevation profiles for time-trial courses.
- **Multi-factor decision model (M4)** incorporating hills, weather, wind forecast, rider
  power profile, competition, and course length.
- **Uncertainty/sensitivity model (M5)** yielding probabilistic recommendations rather than
  a single threshold.
- **Robustness to crosswinds and gusts**, including safety considerations.
- **Personalization** to rider mass, power, and equipment (wheel inertias, tire choice).
- **Validation against real race outcomes or published field data** where feasible.

---

### Appendix A — Planning checklist (to be satisfied in later phases)
- [ ] Assumptions table finalized with risk ratings and test plans.
- [ ] Parameter registry frozen with provenance and units.
- [ ] Core power model implemented and limit-checked.
- [ ] Task 1 table generated and internally cross-validated.
- [ ] Task 2 course example constructed and walked through.
- [ ] Task 3 adequacy criteria defined and applied.
- [ ] Sensitivity analysis completed and reported.
- [ ] Final report assembled (separate deliverable).

> **Reminder:** This file is a **planning blueprint only**. It intentionally contains no
> computed numbers, no fitted models, no executed experiments, and no final conclusions.
