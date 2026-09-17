# Modeling Blueprint Draft — The Bicycle Wheel Problem (MCM 2001)

> **Status:** Initial planning draft. This document is a roadmap for future modeling only.
> It contains no computed results, no executed analysis, and no final conclusions.
> All statements about outcomes are written in future-oriented / conditional language.

---

## 1. Problem Background and Restatement

A cycling team's director sportif must decide, for a given racecourse, whether to mount a
**solid disk rear wheel** or a **spoked rear wheel**, given that the **front wheel is always a
spoked wheel**. The two wheel types trade off along two axes:

- **Spoked wheels** — lower mass / lower rotational inertia, but higher aerodynamic drag.
- **Solid (disk) wheels** — heavier / higher inertia, but lower aerodynamic drag.
- A solid wheel is never used on the front for a road race but may be used on the rear.

The decision depends on course and environmental factors cited in the problem: number and
steepness of hills, weather, wind speed, competition, and other considerations.

The problem asks for three deliverables to support this decision:

- **Task 1.** A table of the **wind speed threshold** at which the power required by a solid
  rear wheel becomes **less** than that of a spoked rear wheel, tabulated across **road grades
  from 0% to 10% in 1% increments**. Boundary/known conditions stated: rider starts the hill at
  **45 kph**; deceleration is **proportional to road grade**; the rider **loses about 8 kph for a
  5% grade over 100 meters**.
- **Task 2.** A worked **example of applying the table** to a specific time-trial course.
- **Task 3.** An assessment of whether the table is an **adequate decision aid**, plus
  **alternative / complementary decision methods**.

> Restatement framing: the core question is not "which wheel is faster," but
> "at what wind conditions does the aerodynamic advantage of the disk wheel overcome its
> inertial/mass penalty, as a function of grade, for a rider entering a hill at 45 kph."

---

## 2. Objectives and Subproblems

### 2.1 Primary objective
Produce a **decision-support framework** that maps course/environmental conditions
(grade, wind speed, entry speed, and possibly others) to a recommended rear-wheel type,
with an explicit threshold table as the centerpiece.

### 2.2 Subproblems to be planned (not yet solved)
- **SP1 — Power balance model.** Formulate the net propulsive power a rider must supply as a
  function of resistive forces (gravity on grade, rolling resistance, aerodynamic drag,
  drivetrain loss, and inertial acceleration).
- **SP2 — Wheel-differentiating terms.** Isolate the physical terms that differ between a solid
  and spoked rear wheel (aerodynamic drag coefficient/area, rotational inertia, mass).
- **SP3 — Kinematic/deceleration relation.** Encode the stated deceleration rule: deceleration
  proportional to grade, calibrated so that a 5% grade over 100 m ~ 8 kph loss.
- **SP4 — Threshold condition.** Define the inequality
  `P_solid(wind, grade, v) < P_spoked(wind, grade, v)` and plan how the crossing wind speed will
  be located for each grade 0%–10%.
- **SP5 — Threshold table construction.** Plan the structure, resolution, and units of the
  grade × wind-speed table.
- **SP6 — Use-case demonstration (Task 2).** Plan a template for translating a real course
  profile into a wheel recommendation.
- **SP7 — Adequacy critique (Task 3).** Plan the criteria under which the table is sufficient
  or insufficient, and enumerate alternative decision methods.

### 2.3 Deliverables
- D1: A **threshold table** (grade → critical wind speed) with stated assumptions.
- D2: A **worked application example** on a hypothetical time-trial course.
- D3: A **critique + alternative methods** section.
- D4: (Supporting) a reproducible model description allowing re-derivation under new inputs.

---

## 3. Assumptions

Each assumption will be recorded with its **justification**, **impact if wrong**, and a
**future validation approach**. Initial candidate list:

### 3.1 Physical / mechanical assumptions
- **A1 — Steady rider power target is not the comparison metric; instantaneous required power is.**
  Justification: the problem asks which wheel *requires less power* under given conditions.
  Validation: compare against alternative formulations (constant-speed vs. constant-power).
- **A2 — Same rider, same front spoked wheel, same tire pressure, same total system mass except
  for the rear-wheel difference.** Validation: sensitivity sweep over rear-wheel mass/inertia.
- **A3 — Aerodynamic drag is quadratic in effective airspeed:** `F_drag = ½·ρ·C_d·A·(v + v_wind_eff)²`,
  with an effective headwind component from wind direction. Justification: standard cycling
  aerodynamics. Validation: literature C_d·A values for disk vs. spoked wheels.
- **A4 — Rolling resistance is linear/collinear with normal load and roughly equal across wheel
  types** (or differs only slightly). Validation: sensitivity to rolling-resistance coefficient.
- **A5 — Drivetrain efficiency is a constant factor shared by both configurations**, so it
  cancels in the threshold comparison. Validation: vary efficiency.
- **A6 — Air density ρ is treated as a fixed nominal value (with a planned sensitivity range).**
- **A7 — Rotational-inertia effects matter only during acceleration phases; on steady grade
  the two wheels differ primarily by mass and aerodynamics.** Validation: compare an
  inertia-aware model to a quasi-static model.

### 3.2 Modeling-scope assumptions
- **A8 — Grade is constant over the analysis segment** (consistent with the table being indexed
  by a single grade value). Validation: piecewise-constant / segmented extension.
- **A9 — Deceleration is proportional to grade, calibrated from the 8 kph / 5% / 100 m datum.**
  Justification: directly stated in the problem. Validation: check dimensional consistency and
  compare with a first-principles energy/force model.
- **A10 — Entry speed of 45 kph applies at the bottom of each graded segment.** Validation:
  sweep entry speed.
- **A11 — Wind is treated as a steady effective headwind/tailwind along the direction of travel**
  for the baseline; crosswind and gustiness are deferred to sensitivity analysis.

### 3.3 Interpretation assumptions
- **A12 — "Wind speed" in the table refers to the effective wind component opposing/aiding the
  rider**, not arbitrary meteorological wind. Validation: define and test alternative
  interpretations (absolute wind vs. component).
- **A13 — "Power required" means mechanical power at the wheel/pedal required to sustain the
  modeled motion**, including the deceleration rule where applicable.

> Planned handling: assumptions A1–A13 will be re-examined in the validation phase and their
> influence ranked (see §7.4).

---

## 4. Data Processing Plan

> Note: the workspace `data/` directory is currently **empty**. The plan below therefore covers
> both (a) **parameter inputs derived from the problem statement** and (b) **external / literature
> parameters** to be sourced during modeling, plus (c) any course-profile data needed for Task 2.

### 4.1 Inputs explicitly provided by the problem
- Grade grid: **0% … 10% in 1% increments** (11 values).
- Entry speed: **45 kph** (to be converted to m/s).
- Calibration datum: **8 kph per 100 m at 5% grade** →
  used to derive the proportionality constant for deceleration-vs-grade.
- Front wheel: **always spoked** (fixed).

### 4.2 Parameters to be sourced / justified
- Drag area `C_d·A` for **spoked vs. disk rear wheels** (candidate source: cycling-aerodynamics
  literature, published wind-tunnel data, or manufacturer data).
- Air density `ρ` (nominal + range).
- Rear-wheel masses and moments of inertia for both types (nominal + range).
- Rolling-resistance coefficients for typical time-trial tires.
- Drivetrain efficiency.

### 4.3 Preprocessing plan
- **Unit harmonization:** kph ↔ m/s, percent grade ↔ sine-of-angle ↔ radians, watts/Newtons.
- **Grade transformation:** convert percent grade `g` to geometric angle via `sin θ = g/100`
  (as the problem defines grade as the sine of the bottom angle).
- **Derived-quantity construction:** gravitational force component, drag force, inertial terms as
  explicit functions of `(g, v, v_wind)`.
- **Calibration step:** determine the proportionality coefficient in the deceleration rule using
  the 8 kph / 5% / 100 m datum (this is a **planned** derivation, not performed here).
- **Parameter table assembly:** build a single tidy parameter registry (name, symbol, value,
  unit, source, uncertainty range) to drive the model.

### 4.4 Feature construction (model inputs → decision features)
- Effective airspeed as a function of rider speed and wind component.
- Required-power difference `ΔP(g, v_wind) = P_solid − P_spoked`.
- Signed threshold feature: the wind speed where `ΔP = 0` for each grade.
- Optional composite features: course energy demand, average grade, wind exposure weighting.

### 4.5 Data usage strategy
- **Synthetic/parametric grid:** because the table is analytic, the primary "data" will be a
  parameter grid evaluated by the model (grade × wind-speed sweep). This is a modeling plan,
  not an executed computation.
- **External-parameter sensitivity:** each literature-sourced parameter will be swept over a
  plausible range to test threshold stability.
- **Course-profile ingestion (Task 2):** plan a schema for a course file
  (segment index, length, grade, heading, wind vector) to be consumed by the decision routine.

---

## 5. Candidate Model Framework

### 5.1 Modeling philosophy
Build a **physics-based point-mass bicycle-rider power model** as the primary framework,
with the wheel-type difference expressed entirely through a small number of physical terms
(aerodynamic drag area, mass, rotational inertia). This keeps the threshold comparison
transparent and auditable.

### 5.2 Candidate models (primary + alternatives)
- **M1 — Quasi-static power-balance model (primary).**
  Required power = (gravity + rolling + aero + drive-loss + inertial) terms, evaluated at each
  `(grade, wind, speed)` state. Threshold found by solving `P_solid = P_spoked` for wind speed.
  *Advantages:* transparent, minimal parameters, directly satisfies Task 1 structure.
  *Limitations:* ignores transient dynamics, cornering, rider position changes.
- **M2 — Longitudinal dynamics / ODE model (refinement).**
  Integrate the equation of motion along the hill using the stated deceleration rule, tracking
  speed as a function of distance. Provides the speed profile that feeds a time-averaged power
  comparison. *Advantages:* respects the deceleration statement and non-constant speed.
  *Limitations:* more parameters, needs numerical integration.
- **M3 — Energy / work comparison model (alternative view).**
  Compare total mechanical work over the segment for each wheel type.
  *Advantages:* intuitive for course-level decisions; bridges to Task 2.
  *Limitations:* requires an assumed speed profile (couples with M2).
- **M4 — Empirical / data-driven correction layer (optional enhancement).**
  Use literature drag values and, if available, published time-trial data to calibrate or correct
  M1/M2. *Advantages:* grounds the model in measured behavior. *Limitations:* data scarcity,
  risk of overfitting to non-representative conditions.
- **M5 — Multi-criteria decision model (for Task 3).**
  Weighted scoring over speed, safety/stability, wind gusts, rider preference, competition
  context. *Advantages:* addresses the "adequacy" question beyond a single table.

### 5.3 Variables (candidate)
| Symbol | Meaning | Role |
|---|---|---|
| `g` | road grade (%) / `θ` | independent (table index) |
| `v_wind` | effective wind speed | independent (table output axis) |
| `v` | rider speed (f(v), decelerating on grade) | state |
| `ρ` | air density | parameter |
| `C_dA_solid`, `C_dA_spoked` | drag area per wheel type | parameter (differentiating) |
| `m_solid`, `m_spoked` | rear-wheel mass | parameter (differentiating) |
| `I_solid`, `I_spoked` | rear-wheel inertia | parameter (differentiating) |
| `C_rr` | rolling-resistance coefficient | parameter |
| `η` | drivetrain efficiency | parameter |
| `P_solid`, `P_spoked` | required power | output |
| `v_wind*` | critical wind speed at `ΔP=0` | **key deliverable** |
| `L`, `heading` | segment length/direction | Task 2 inputs |

### 5.4 Mathematical ideas to be developed (planned, not derived here)
- A **power-balance identity** separating common terms from wheel-differentiating terms.
- A **calibrated deceleration function** from the stated datum.
- A **root-finding condition** `ΔP(g, v_wind) = 0` defining the threshold table.
- A **monotonicity argument** to explain how `v_wind*` should trend with grade
  (to be verified later, not asserted as a result).
- A **segment-decomposition rule** for applying the table to a multi-segment course.

### 5.5 Advantages / limitations of the overall framework
- *Advantages:* physically interpretable, auditable, naturally produces the required table,
  extensible to richer scenarios.
- *Limitations:* sensitive to assumed drag/mass parameters; idealized wind and grade;
  ignores rider tactics, fatigue, and handling constraints.

---

## 6. Implementation Roadmap

> All steps below are **planned**; no code will be written or executed in this draft.

### 6.1 Modules to build
1. **`units` / constants module** — unit conversions and physical constants.
2. **`params` registry** — tidy parameter table with sources and uncertainty ranges.
3. **`wheel` module** — wheel-type descriptors (drag area, mass, inertia).
4. **`physics` module** — force/power terms; deceleration calibration from the 8 kph datum.
5. **`threshold` module** — root-finding of `ΔP = 0` across the grade grid.
6. **`table` module** — assembly and formatting of the grade × wind-speed threshold table.
7. **`course` module** — course-profile ingestion + segment-wise decision (Task 2).
8. **`critique` module** — adequacy checks + alternative-method scoring (Task 3).
9. **`report` module** — generation of tables/figures for the final write-up.

### 6.2 Workflow (planned sequence)
1. Encode assumptions and parameter registry.
2. Implement the common power terms and the wheel-differentiating terms.
3. Calibrate the deceleration rule from the given datum.
4. Define the threshold condition and implement the root-finder.
5. Produce the threshold table over grades 0–10%.
6. Build the course-application routine and a worked example template.
7. Run the adequacy checks and construct alternative-method comparisons.
8. Assemble the final report artifacts.

### 6.3 Algorithmic choices to consider
- **Root-finding:** bracketing + bisection/Newton for the wind-speed crossing; robust to
  non-monotonic drag terms.
- **ODE integration (M2):** explicit RK4 or adaptive solver for the speed profile.
- **Sweep design:** grid over grade (1% steps) and a fine wind-speed sweep for table resolution.
- **Reproducibility:** fixed seeds/parameters, configuration files, logged runs.

### 6.4 Tooling / environment plan
- Language: Python (numerical stack: NumPy/SciPy) for modeling and plotting.
- Config-driven parameter files (e.g., YAML/JSON) to support sensitivity sweeps.
- Outputs written to `results/`; intermediate artifacts to `logs/`; code under `code/`.

---

## 7. Validation Strategy

### 7.1 Internal consistency checks
- **Dimensional analysis** of every power term.
- **Limiting cases:** zero-grade, zero-wind, very high wind; check expected qualitative behavior.
- **Calibration check:** confirm the deceleration rule reproduces the 8 kph / 5% / 100 m datum.
- **Term decomposition:** verify common terms cancel correctly so only wheel-differentiating
  terms drive the threshold.

### 7.2 Cross-model validation
- Compare **M1 (quasi-static)** vs. **M2 (dynamic ODE)** thresholds.
- Compare **M3 (energy)** recommendations on a test course against M1/M2.
- Assess magnitude of disagreement and attribute it to specific assumptions.

### 7.3 External / literature validation
- Bench-test `C_dA` values against published wind-tunnel / field data for disk vs. spoked wheels.
- Cross-check against reported time-trial performance differences where available.

### 7.4 Sensitivity analysis (planned)
- Sweep: drag-area difference, rear-wheel mass/inertia, air density, rolling resistance,
  drivetrain efficiency, wind direction (head/tail/cross), entry speed.
- Rank parameters by their influence on the threshold table (tornado-style sensitivity).
- Identify which assumptions, if wrong, would **flip** a wheel recommendation.

### 7.5 Evaluation metrics (candidate)
- **Threshold stability:** variation of `v_wind*` under parameter perturbations.
- **Decision agreement:** fraction of course segments where recommendations are unchanged
  across models/assumption sets.
- **Power-gap magnitude:** `|ΔP|` at representative conditions (as a confidence indicator).
- **Robustness score:** how often the table alone would mislead vs. a multi-criteria method.

### 7.6 Uncertainty quantification plan
- Propagate parameter ranges via interval / Monte-Carlo style sweeps (planned, not executed).
- Report thresholds with uncertainty bands rather than single numbers.

---

## 8. Expected Result Interpretation

> Interpretive guidance only; no values will be produced in this draft.

- The threshold table will be interpreted as: **for each grade, the wind speed below/above which
  the solid rear wheel is predicted to require less power** than the spoked wheel.
- Expected *qualitative* direction (to be verified later): as grade steepens, the inertial/mass
  penalty of the disk wheel should grow while its aero advantage may weaken, so the favorable
  wind-speed window is expected to narrow — this is a **hypothesis to test**, not a result.
- A worked Task 2 example will be interpreted as translating a course profile into a
  **segment-by-segment recommendation**, aggregated to an overall wheel choice.
- Task 3 interpretation: the table will be assessed as an **approximate, condition-conditional
  aid**, useful for coarse decisions but likely insufficient alone when wind is variable,
  grades are mixed, or safety/handling dominate.
- Recommended reading: thresholds should be treated as **probabilistic guidance**, with
  sensitivity bands, rather than as hard cutoffs.

---

## 9. Limitations and Improvements

### 9.1 Known limitations of the planned approach
- Idealized **point-mass** rider with no rider-position or steering dynamics.
- **Single fixed grade** per evaluation; real courses have varying grade.
- **Steady effective wind** assumption; ignores gusts, crosswinds, and direction changes.
- **Wheel parameters** (drag area, mass, inertia) are assumed rather than measured, so results
  will be only as good as those inputs.
- The **deceleration rule** ("proportional to grade") is a stylization; a first-principles
  model may differ.
- Exclusion of **tactics/competition**, fatigue, cornering, and safety/handling constraints.
- No consideration of front-wheel interactions beyond the stated fixed choice.

### 9.2 Planned improvements / extensions
- Move from M1 to **M2 dynamics** for speed-profile realism, then to **course-integrated**
  energy comparisons.
- Replace assumed wheel parameters with **measured/literature-calibrated** values.
- Add **crosswind and gust modeling** and a **stability/handling** criterion for disk wheels.
- Develop a **multi-criteria decision-support tool** (M5) with user-tunable weights.
- Provide **uncertainty bands** in the threshold table and an interactive lookup for courses.
- Consider **segment-wise optimization** (choose wheel per segment) vs. a single race wheel.
- Validate against real **time-trial data** if obtainable.

### 9.3 Open questions deferred to modeling phase
- What exactly does "wind speed" index — absolute or effective component?
- Should the comparison be at constant speed or along the decelerating profile?
- How should the table be aggregated for multi-grade courses?
- What safety threshold should override pure power considerations?

---

### Draft scope statement
This document is a **blueprint only**. It defines the workflow, assumptions, candidate methods,
data plan, implementation plan, and validation strategy needed to later solve the Bicycle Wheel
Problem. It deliberately contains **no results, no executed computation, and no final
recommendation**. All quantitative statements are to be produced in a subsequent modeling phase.
