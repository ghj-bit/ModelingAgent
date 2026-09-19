# Modeling Blueprint Draft — MM-Bench 2016_A

**Problem ID:** `2016_A`
**Title:** Bathtub Water Temperature Control Strategy
**Document type:** Initial modeling plan draft (roadmap only)
**Status:** Planning stage — no data analyzed, no models fitted, no results computed
**Language:** Future-oriented ("will", "should", "is planned to")

> This document is a modeling blueprint. It describes *how* the problem will be
> approached. It intentionally contains no computed results, no fitted parameters,
> no experiments, and no final conclusions.

---

## 1. Problem Background and Restatement

### 1.1 Background (as stated)

A person fills a bathtub with hot water from a single faucet and then settles into
the tub to cleanse and relax. The tub is a simple water containment vessel — it has
no spa-style secondary heating system and no circulating jets. Over time the bath
water cools noticeably. To reheat the bathing water, the person will add a constant
trickle of hot water from the faucet. The tub is designed so that once it reaches
its capacity, any excess water will escape through an overflow drain.

### 1.2 Restatement of the Modeling Task

The task will be to develop a model of the bathtub water temperature **in space and
time**, and to use that model to determine the **best strategy** the bather can
adopt in order to:

- keep the temperature **even throughout the bathtub** (spatial uniformity), and
- keep the temperature **as close as possible to the initial temperature**
  (temporal stability),
- **without wasting too much water** (water-conservation constraint).

The model will then be used to explore how the recommended strategy will depend on:

- the **shape and volume** of the tub,
- the **shape, volume, and temperature** of the person in the tub,
- the **motions** made by the person in the tub.

Finally, the effect of a **bubble bath additive** (added during initial filling to
assist cleansing) on the model's behavior will be considered.

### 1.3 Nature of the Problem

This is an open-ended, physically-grounded modeling problem. It is expected to be
formulated as a **coupled heat- and mass-transport system** on a bounded domain with
a moving/overflow free surface, driven by discrete control decisions (faucet trickle
rate and duration, bather stirring/motion). It will likely require a combination of:

- continuum heat-transfer modeling (conduction / convection / advection),
- lumped or multi-zone thermal modeling as a reduced-order alternative,
- an optimization layer over candidate control strategies,
- a sensitivity/robustness layer over geometry, occupant, and additive parameters.

---

## 2. Objectives and Subproblems

### 2.1 Primary Objective

To construct a defensible, calibratable model that predicts the spatio-temporal
temperature field of bathtub water and to derive a control strategy that will
balance three competing goals: **spatial evenness**, **temperature retention**,
and **water economy**.

### 2.2 Subproblems (to be addressed in sequence)

| ID | Subproblem | Purpose |
|----|------------|---------|
| S1 | **Thermal state model** | Define the governing equation(s) for water temperature `T(x, t)` inside the tub, including loss mechanisms. |
| S2 | **Heat-loss characterization** | Plan how conduction (walls/floor/air interface) and radiation will be represented and how their coefficients will be estimated. |
| S3 | **Occupant coupling** | Plan how the bather's body volume, shape, temperature, and metabolic heat output will enter the energy balance. |
| S4 | **Mixing / buoyancy / motion** | Plan how natural convection, bather motion, and (optionally) jets-free stirring will be represented to govern spatial evenness. |
| S5 | **Overflow and water exchange** | Plan how the trickle inlet and overflow drain will be modeled as a coupled inflow/outflow boundary condition that conserves mass. |
| S6 | **Control strategy optimization** | Plan the decision variables and objective function for identifying the "best" reheating strategy. |
| S7 | **Geometry sensitivity** | Plan how tub shape/volume changes will be swept and compared. |
| S8 | **Occupant sensitivity** | Plan how occupant shape/volume/temperature will be swept and compared. |
| S9 | **Additive (bubble bath) effect** | Plan how a surfactant additive will be represented as a modification to transport and loss properties. |
| S10 | **Validation & uncertainty** | Plan how the model's credibility will be assessed in the absence of a provided dataset. |

### 2.3 Deliverables (planned)

1. A documented mathematical formulation for `T(x, t)` and water mass balance.
2. A reduced-order model suitable for fast strategy search.
3. A defined control strategy (faucet schedule + mixing protocol) with rationale.
4. A sensitivity map showing dependence on geometry, occupant, and motion.
5. A qualitative-to-semi-quantitative account of the additive effect.
6. A validation and uncertainty plan.

---

## 3. Assumptions

Assumptions are grouped by type. Each will be stated explicitly, justified, and
paired with a planned validation approach. Assumptions marked **[R]** are planned as
"relax later" candidates in the sensitivity analysis.

### 3.1 Geometric and Domain Assumptions

| ID | Assumption (planned) | Justification | Planned Validation |
|----|----------------------|---------------|--------------------|
| A1 | The tub will be treated as a simple geometric domain (e.g., rectangular or axisymmetric) with a fixed wall thickness. | Standard simplification; enables analytic/numerical treatment. | Compare reduced geometry against a more realistic shape in sensitivity runs. |
| A2 | Water volume will be treated as constant at capacity once overflow begins; overflow removes excess at the surface. **[R]** | Matches the overflow-drain description. | Relax by allowing pre-overflow fill transient. |
| A3 | Water is incompressible and the free surface remains approximately horizontal. **[R]** | Justified at low faucet flow rates. | Relax for strong bather motion. |

### 3.2 Thermal Assumptions

| ID | Assumption (planned) | Justification | Planned Validation |
|----|----------------------|---------------|--------------------|
| A4 | Water properties (density, specific heat, conductivity, viscosity) will be treated as temperature-dependent only where first-order important, else constant. **[R]** | Reduces nonlinearity. | Test constant vs. variable properties. |
| A5 | Heat loss to ambient will be modeled through wall conduction plus an effective air-side heat-transfer coefficient. | Standard building-physics analogy. | Bracket coefficient over plausible range. |
| A6 | Evaporative loss will be included as an optional surface-flux term. **[R]** | Relevant for a warm open surface; amplified by additive. | Compare with/without evaporation. |
| A7 | Faucet inflow will be treated as a prescribed hot-water stream at fixed temperature. | Directly follows problem statement. | Vary inlet temperature in sensitivity. |

### 3.3 Occupant Assumptions

| ID | Assumption (planned) | Justification | Planned Validation |
|----|----------------------|---------------|--------------------|
| A8 | The bather will be represented as a warm, finite-volume body with a surface heat-transfer boundary at approximately skin temperature. | Captures dominant thermal effect. | Sweep body volume/shape/temperature. |
| A9 | Metabolic heat generation will be treated as a bounded volumetric source. **[R]** | Real but usually second-order vs. body surface exchange. | Test with/without source term. |
| A10 | Bather motion will be represented as an effective enhanced mixing diffusivity / advective field rather than full body kinematics. **[R]** | Tractable; captures the mixing outcome. | Compare effective-mixing vs. explicit motion models. |

### 3.4 Additive (Bubble Bath) Assumptions

| ID | Assumption (planned) | Justification | Planned Validation |
|----|----------------------|---------------|--------------------|
| A11 | The additive will be modeled as a change to surface tension, evaporation rate, and effective surface insulation due to foam. **[R]** | Foam blanket alters both evaporation and insulation. | Treat as a parametric perturbation and sweep. |
| A12 | The additive will be assumed not to change bulk water properties appreciably at low concentration. **[R]** | Low-concentration surfactant. | Test sensitivity to concentration proxy. |

### 3.5 Modeling-Philosophy Assumptions

| ID | Assumption (planned) | Justification | Planned Validation |
|----|----------------------|---------------|--------------------|
| A13 | A hierarchy of models (lumped → multi-zone → distributed PDE) will be used, with the lumped model as a fast surrogate. | Enables both insight and tractability. | Cross-compare tiers for consistency. |
| A14 | Parameters without literature values will be treated as calibrated/uncertain and carried through sensitivity analysis. | Honest treatment of unknowns. | Report parameter ranges, not point claims. |

---

## 4. Data Processing Plan

### 4.1 Data Situation

The provided dataset definition is empty (`dataset_path: []`,
`dataset_description: {}`, `variable_description: {}`), and the staged `data`
directory currently contains no files. **No empirical dataset is available.**

Consequently, the plan will be to build the analysis on a combination of:

1. **First-principles physical parameters** (water properties, geometry ranges,
   typical household hot-water supply temperatures, ambient room conditions),
   sourced from standard references rather than a supplied dataset.
2. **Parameter ranges** derived from the problem statement's qualitative
   descriptions and reasonable domestic-tub scales.
3. **Synthetic scenario generation**, i.e., constructing idealised scenarios
   (tub shapes, occupant sizes, motion levels) internally for model exploration.

### 4.2 Planned Preprocessing Steps (when/if data becomes available)

- **Ingestion:** Detect any later-provided files (CSV/JSON/XLSX) and load them with
  a schema check against `variable_description`.
- **Unit harmonization:** Normalize lengths (m/mm), volumes (L/m³), temperatures
  (°C/K), and flow rates (L/min, m³/s) into a single consistent SI basis.
- **Missing-value handling:** Document strategy (drop vs. impute) with justification;
  flag time-series gaps before any use.
- **Outlier screening:** Apply physical-plausibility bounds (e.g., water temperature
  cannot exceed supply temperature; volume cannot exceed tub capacity).
- **Time-base alignment:** If time series exist, resample to a uniform sampling
  interval and record the interpolation method used.
- **Provenance logging:** Record every transformation for reproducibility.

### 4.3 Feature / Variable Construction Plan

Even without a dataset, the following model-level variables will be defined for
later construction:

- **State variables:** temperature field `T(x, y, z, t)`; water volume `V(t)`.
- **Control variables:** faucet trickle rate `q_in(t)`; inlet temperature `T_in`;
  mixing intensity `m(t)` representing bather motion.
- **Geometry parameters:** surface area `A`, volume `V_0`, characteristic depth `H`,
  wall thickness and material.
- **Occupant parameters:** body volume `V_b`, surface area `A_b`, body temperature
  `T_b`, metabolic source `Q_met`.
- **Environment parameters:** ambient temperature `T_amb`, air-side coefficient,
  evaporation coefficient.
- **Derived metrics (planned):** spatial temperature variance, drift from initial
  temperature, cumulative water use, settling time, thermal recovery time.

### 4.4 Data Usage Strategy

- If no data is supplied, models will be run as **scenario-based simulations** and
  conclusions stated as conditional on assumptions.
- If partial data is supplied later, a **split** (calibration vs. hold-out) will be
  planned, and no parameter will be tuned on the hold-out set.

---

## 5. Candidate Model Framework

### 5.1 Tiered Model Hierarchy

| Tier | Model class | Representation | Purpose |
|------|-------------|----------------|---------|
| T1 | **Lumped (0-D) energy balance** | Single well-mixed temperature `T(t)` | Fast strategy scan, baseline intuition. |
| T2 | **Multi-zone (1-D / 2-zone)** | Stratified layers or core–shell zones | Captures vertical/horizontal non-uniformity cheaply. |
| T3 | **Distributed (PDE)** | `T(x, t)` via heat/advection–diffusion equation | Spatial evenness, motion effects, geometry sensitivity. |

The plan will be to develop all three tiers and cross-validate them, using T1/T2 as
surrogates and T3 as the reference formulation.

### 5.2 Governing Ideas (to be formalized later)

- **Energy balance skeleton:** rate of change of internal energy = advective inflow
  − overflow outflow − conduction through walls/floor − convective loss at surface
  − radiative loss − heat exchange with the occupant.
- **Advection–diffusion transport:** `∂T/∂t + u·∇T = α∇²T + S`, with `u` representing
  bulk motion (faucet jet / bather-induced stirring) and `S` any volumetric source.
- **Buoyancy-driven mixing:** stratification described via a buoyancy term / reduced
  gravity to capture warm water rising near the bather and inlet.
- **Mass conservation with overflow:** `dV/dt = q_in − q_overflow`, with overflow
  engaged at capacity; outflow temperature taken at surface layer.
- **Surface exchange:** combined convective + evaporative + radiative flux at the
  free surface, and an optional foam (additive) resistance layer.

### 5.3 Control-Strategy Formulation (planned)

Decision variables will likely include:

- trickle rate `q_in` (possibly constant, per problem statement, but also tested as
  piecewise-constant),
- timing/duty cycle of reheating,
- inlet temperature `T_in`,
- mixing protocol `m(t)` (periodic bather motion vs. continuous).

The objective will be a **weighted multi-criteria function** combining:

- spatial variance penalty (evenness),
- mean-temperature drift penalty (closeness to initial temperature),
- cumulative water-use penalty (waste).

The relative weighting will be treated as a policy parameter and swept, so that the
"best" strategy can be reported as a family of Pareto-optimal trade-offs rather than
a single unsupported claim.

### 5.4 Advantages and Limitations of Candidates

| Model | Advantages | Limitations |
|-------|-----------|-------------|
| T1 Lumped | Trivial to simulate and optimize; clear insight. | Cannot represent spatial evenness — the core requirement. |
| T2 Multi-zone | Cheap spatial resolution; good for sensitivity sweeps. | Zone boundaries are somewhat arbitrary; limited fidelity. |
| T3 PDE | Physically faithful; directly addresses `T(x,t)`. | More parameters, higher compute, harder calibration with no data. |
| Effective-mixing surrogate | Captures bather motion without full kinematics. | Simplified; needs sensitivity checks. |
| Foam-layer surface model | Simple way to encode additive effect. | Phenomenological; needs bounding. |

### 5.5 Dependence Questions to be Mapped

- **Shape/volume of tub:** how surface-to-volume ratio controls loss rate and how
  depth controls stratification and mixing distance.
- **Occupant shape/volume/temperature:** how displaced volume, contact/surface area,
  and body temperature shift equilibrium and local gradients.
- **Motion:** how motion intensity changes effective mixing and hence spatial
  uniformity vs. water-use requirements.
- **Additive:** how foam alters surface loss (evaporation suppression / insulation)
  and, in turn, changes the recommended strategy.

---

## 6. Implementation Roadmap

### 6.1 Planned Algorithms

- **T1:** closed-form or simple ODE integration (explicit/analytic) for `T(t)`.
- **T2:** small system of coupled ODEs per zone, integrated with a stiff-aware solver.
- **T3:** finite-difference / finite-volume discretization with explicit or
  implicit time stepping (implicit preferred for stability).
- **Mixing/motion:** prescribed velocity field or effective-diffusivity parameterization.
- **Optimization:** grid/random search over control parameters, plus gradient-free
  optimizers (e.g., Nelder–Mead, differential evolution) and Pareto-front extraction.
- **Sensitivity:** one-at-a-time sweeps and variance-based global sensitivity
  (e.g., Sobol-style) over the key parameter set.

### 6.2 Planned Workflow

1. **Formulate** the physics and equations for each tier (T1 → T2 → T3).
2. **Parameterize** from first principles/references; record every parameter with a
   range and source tag.
3. **Implement** the simulation engine per tier with unit tests for conservation
   (energy and mass balances must close).
4. **Cross-validate tiers** (T1 ≈ T2 ≈ T3 in the limits where they should agree).
5. **Define control problem** and encode the multi-criteria objective.
6. **Search strategies** across the control space.
7. **Run sensitivity sweeps** over geometry, occupant, motion, and additive.
8. **Document** assumptions, ranges, and conditional conclusions.

### 6.3 Required Modules

- `geometry` — tub and occupant shape/volume descriptors.
- `thermaldynamics` — energy-balance / PDE kernels.
- `transport` — advection–diffusion and mixing models.
- `surface` — evaporation/convection/radiation and foam layer.
- `overflow` — mass balance and drain logic.
- `control` — strategy parameterization and objective function.
- `optimizer` — search routines and Pareto extraction.
- `sensitivity` — sweep orchestration and global sensitivity.
- `validation` — conservation checks, tier cross-comparison, uncertainty reporting.
- `viz` — planned temperature-field and trajectory visualizations (to be generated
  only at a later, execution stage).

### 6.4 Implementation Guardrails

- Every simulation will assert **energy and mass conservation** within tolerance.
- All random searches will use fixed seeds for reproducibility.
- No parameter will be reported without an accompanying range or source.

---

## 7. Validation Strategy

Because no dataset is supplied, validation will be largely **internal and
physical-consistency based**, supplemented by literature-informed parameter bracketing.

### 7.1 Planned Evaluation Metrics

- **Spatial evenness:** standard deviation / range of `T` across the domain.
- **Thermal retention:** deviation of mean temperature from the initial temperature.
- **Water use:** cumulative (or per-unit-time) overflow volume.
- **Stability/response:** time to re-equilibrate after reheating or motion.
- **Conservation residuals:** energy-balance and mass-balance closure errors.

### 7.2 Planned Validation Methods

1. **Physical plausibility checks:** monotone cooling without reheating; temperature
   bounded by inlet and ambient; overflow only at capacity.
2. **Limit-case cross-checks:** well-mixed limit (T3 with large diffusivity → T1);
   no-loss limit; no-occupant limit.
3. **Conservation audits:** explicit accounting of energy and water in/out over time.
4. **Tier agreement:** T1/T2/T3 convergence in the regimes where they should coincide.
5. **Literature benchmarking (qualitative):** compare predicted cooling/reheating
   timescales against ranges reported for domestic bathtubs.
6. **Internal replication:** independent re-implementation of the reduced model to
   reduce coding-error risk.

### 7.3 Planned Sensitivity Analysis

- **One-at-a-time sweeps** over geometry, occupant, motion, and additive parameters.
- **Global variance-based sensitivity** to rank parameter importance.
- **Scenario grid:** small/large tubs × small/large occupants × low/high motion ×
  additive on/off.
- **Robustness check:** whether the recommended strategy family remains stable under
  parameter perturbation (i.e., strategy robustness, not just model fit).

### 7.4 Uncertainty Communication Plan

- Report parameters as ranges; report strategies as Pareto families.
- Clearly separate **assumption-driven** from **physics-driven** behaviors.
- Flag conclusions that depend on phenomenological (unvalidated) terms such as the
  foam-layer or effective-mixing models.

---

## 8. Expected Result Interpretation

### 8.1 What the Results Are Expected to Show (planned direction, not computed)

- A **lumped model** will likely predict monotone cooling punctuated by reheating
  events and a trade-off curve between water use and temperature retention — but
  will be unable to speak to evenness.
- A **distributed model** will likely reveal that, without mixing, reheating creates
  local hot plumes and persistent stratification, so evenness will depend heavily on
  mixing (motion).
- The **best strategy** is expected to emerge as a *family* of trade-offs (reheating
  frequency/rate vs. mixing effort vs. water use), rather than a single optimal point.
- **Geometry** is expected to matter mainly through surface-to-volume ratio (loss
  rate) and depth (stratification/mixing length).
- **Occupant** effects are expected to scale with displaced volume and surface area,
  with body temperature setting a local equilibrium.
- **Motion** is expected to be the dominant lever for spatial evenness.
- The **additive** is expected to reduce surface losses (suppressed evaporation /
  foam insulation), shifting the recommended reheating strategy toward less frequent,
  smaller reheating.

### 8.2 Interpretation Principles

- Present behavior as **conditional** on stated assumptions.
- Distinguish **robust** conclusions (likely stable across parameter ranges) from
  **fragile** ones (dependent on unvalidated parameters).
- Express the strategy recommendation as a **policy rule** (when to add water, how
  much, how to mix) rather than a single hard number.
- Keep all interpretation at the blueprint level until execution is completed.

---

## 9. Limitations and Improvements

### 9.1 Anticipated Limitations

1. **No empirical data** — calibration and validation will be limited to physical
   consistency and literature bracketing.
2. **Phenomenological closures** — effective-mixing and foam-layer models introduce
   unvalidated structure.
3. **Simplified geometry** — real tubs have curved, tapered, and uneven walls.
4. **Occupant simplification** — a real body has complex posture, contact, and
   surface wetting behavior.
5. **Turbulence** — full turbulent mixing is not planned to be resolved from first
   principles; only parameterized.
6. **Evaporation and radiation coefficients** are environment-dependent and uncertain.
7. **Single-occupant assumption** — multiple occupants are out of scope.

### 9.2 Planned Improvements / Extensions (future work)

- Replace effective-mixing with a **CFD-style** treatment of bather-induced flow.
- Add **temperature-dependent** and **concentration-dependent** fluid properties.
- Include a **full 3-D conduction model** of the tub shell and surround.
- Incorporate **measured** household-tub geometries and hot-water supply data.
- Introduce a **formal optimal-control** formulation (e.g., Pontryagin / MPC-style
  periodic control) instead of parametric search.
- Develop a **probabilistic (Bayesian)** treatment of uncertain parameters to give
  posterior strategy distributions.
- Validate against a **controlled physical experiment** (e.g., instrumented tub).
- Extend the additive model to a **two-phase foam** treatment with measured
  surface-loss reduction.

### 9.3 Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| Over-fitting to arbitrary assumptions | Report ranges; sweep assumptions; flag fragile conclusions. |
| Numerical instability in PDE tier | Prefer implicit schemes; run conservation audits. |
| Ambiguous objective weighting | Present Pareto family; sweep weights. |
| Missing/late dataset | Build scenario-based plan that can absorb data if provided. |

---

## Appendix A — Planned Symbol Table (to be finalized during formulation)

| Symbol | Planned meaning |
|--------|-----------------|
| `T(x,t)` | Water temperature field |
| `T_0` | Initial bath temperature |
| `T_in` | Faucet hot-water temperature |
| `T_amb` | Ambient air temperature |
| `T_b` | Bather body temperature |
| `q_in` | Faucet trickle flow rate |
| `q_ov` | Overflow flow rate |
| `V(t)` | Water volume |
| `A` | Water surface area |
| `H` | Characteristic depth |
| `α` | Thermal diffusivity |
| `u` | Bulk/mixing velocity field |
| `h` | Effective heat-transfer coefficient |
| `S` | Volumetric source (metabolic or other) |

## Appendix B — Planned Deliverable Checklist

- [ ] Tier-1 lumped model formulation and closed-form/ODE solution plan
- [ ] Tier-2 multi-zone model plan
- [ ] Tier-3 distributed PDE plan
- [ ] Control/objective formulation plan
- [ ] Sensitivity & scenario grid plan
- [ ] Additive (foam) effect plan
- [ ] Validation & conservation audit plan
- [ ] Reporting/interpretation plan

---

*End of initial modeling blueprint draft. No data was analyzed, no model was fitted,
no computation was performed, and no results or conclusions are stated herein.*
