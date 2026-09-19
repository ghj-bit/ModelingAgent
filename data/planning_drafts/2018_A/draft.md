# MM-Bench 2018_A — Initial Modeling Plan Draft

**Problem ID:** `2018_A`
**Title:** MM-Bench 2018_A (Multi-hop HF Radio Propagation over Ocean and Terrain)
**Document type:** Modeling blueprint / planning draft (NOT a solution)
**Status:** Initial draft — roadmap only. No data analysis, computation, fitting, or results are contained here.

> Scope note: This document is intentionally future-oriented. It specifies the *modeling workflow, assumptions, candidate methods, data plan, implementation roadmap, and validation strategy* that a later solver will execute. All quantities are described as quantities *to be derived*, never as derived values.

---

## 1. Problem Background and Restatement

HF (3–30 MHz) radio waves can reach distant terrestrial points through successive reflections between the ionosphere and the Earth's surface (the "multi-hop" skywave path). For frequencies below the Maximum Usable Frequency (MUF), a ground source emits a signal that reflects off the ionosphere, then off the surface (initially the ocean), then again off the ionosphere, and so on. Each reflection changes the signal's amplitude, phase, and angle, and each hop covers additional ground distance. The MUF itself varies with season, time of day, and solar/geomagnetic conditions; frequencies above MUF penetrate the ionosphere and are lost.

The physical interest centers on **surface reflection quality**. Empirically, a **turbulent** ocean attenuates HF reflections more than a **calm** ocean because turbulence alters the seawater electromagnetic gradient (local permittivity and permeability), the effective reflection height, and the local incidence angle. Ocean turbulence is characterized by rapidly changing wave heights, shapes, frequencies, and directions of travel. The problem asks how such surface conditions govern reflection strength and the usable multi-hop range.

**Restatement of required tasks (native problem wording preserved in intent):**

- **Part I — Ocean reflection model.**
  (a) Build a mathematical model of HF signal reflection off the ocean.
  (b) For a 100 W constant-carrier HF signal below MUF, radiated from a point source on land, determine the strength of the **first** ocean reflection under *turbulent* conditions and compare it with the **first** reflection under *calm* conditions (one prior ionospheric reflection is included by definition).
  (c) For additional reflections 2…n off *calm* oceans, determine the **maximum number of hops** before the signal strength drops below a usable **SNR threshold of 10 dB**.
- **Part II — Terrain comparison.** Compare Part I findings with HF reflections off **mountainous/rugged** terrain versus **smooth** terrain.
- **Part III — Shipboard receiver.** Extend the model to a **shipborne receiver moving on a turbulent ocean**; determine **how long** the ship can remain in communication on the same multi-hop path.
- **Part IV — Synopsis.** Produce a 1–2 page short-note synopsis suitable for IEEE Communications Magazine.

**Deliverables expected of the eventual solution:** a documented reflection/attenuation model, comparative turbulent-vs-calm and rugged-vs-smooth analyses, a hop-count/SNR limit determination, a moving-receiver communication-duration analysis, and a publication-style synopsis. *This draft delivers only the plan for producing them.*

---

## 2. Objectives and Subproblems

### 2.1 Overarching objective
Construct a physically grounded, parameter-driven model of HF multi-hop skywave propagation in which the **surface reflection coefficient** is the central link between ocean/terrain state and end-to-end SNR, then use that model to answer the four native subproblems.

### 2.2 Subproblems and their modeling intent

| # | Subproblem | Modeling intent (to be executed later) |
|---|------------|----------------------------------------|
| S1 | Ocean reflection model | Derive a reflection-coefficient formulation combining seawater electromagnetic properties (conductivity, permittivity, permeability), Fresnel behavior at grazing incidence, and a turbulence/roughness attenuation factor (e.g., sea-surface slope/wave-spectrum based). |
| S2 | Calm vs. turbulent first reflection | Define a controlled comparison at identical geometry (frequency, incidence angle, distance, ionospheric state); isolate the surface term. |
| S3 | Hop budget to 10 dB SNR | Chain single-hop gains (ionospheric reflection + surface reflection + spreading + absorption) into an end-to-end link budget; solve for the hop index at which SNR crosses 10 dB. |
| S4 | Terrain comparison | Replace the ocean surface term with a terrain-surface term distinguishing smooth (specular-like) from mountainous/rugged (diffuse-scattering, multi-path, shadowing) behavior. |
| S5 | Moving shipboard receiver | Add time-varying geometry and sea-state to the model: relative motion between reflection points and receiver, changing incidence angles, platform motion/antenna effects, and time-varying path loss; derive a communication-duration criterion. |
| S6 | Synopsis | Distill S1–S5 into a 1–2 page IEEE-style note (motivation, model, key qualitative findings, implications). |

### 2.3 Key questions the model must be able to answer
- How much do calm and turbulent oceans differ in reflected HF power, and why (which physical mechanism dominates)?
- How does hop count accumulate loss, and where is the 10 dB threshold crossed?
- Does rugged terrain help or hurt relative to smooth terrain, and under what conditions?
- For a moving ship, what is the timescale over which the same multi-hop path remains viable?

---

## 3. Assumptions

Assumptions are grouped by purpose. For each, the plan notes *why it is needed* and *how it will be validated or relaxed later*.

### 3.1 Signal and system assumptions (S1–S3)
- **A1. Constant-carrier (CW), narrowband, 100 W source.** The signal is treated as a single-frequency continuous carrier; modulation and bandwidth effects are deferred. *Justification:* matches the problem's "constant-carrier signal." *Validation:* later sensitivity check with a representative modulation bandwidth.
- **A2. Frequency is below MUF throughout.** MUF itself will be modeled as a scenario parameter (season/day/night/solar activity) rather than derived from first principles. *Justification:* keeps the study within the reflecting regime. *Validation:* compare with climatological MUF ranges from ionospheric models (e.g., IRI-like references).
- **A3. Point source on land; idealized ground/launch condition.** The transmitter is a point source with a defined radiation pattern; land reflection parameters are held as separate, documented constants.
- **A4. Specular (geometric-optics) treatment of the ionosphere per hop, with a documented effective reflection height.** *Justification:* standard for HF skywave link budgeting. *Validation:* compare against ray-tracing-style alternatives if feasible.
- **A5. Additive noise floor referenced to typical HF receiver bandwidth/noise.** Because the SNR threshold is given (10 dB) but the absolute noise level is not, the noise model is an explicit assumption to be stated and varied. *Validation:* sensitivity sweep on noise assumptions.

### 3.2 Surface physics assumptions (S1–S2)
- **A6. Ocean modeled as a lossy dielectric half-space** with frequency-dependent conductivity and relative permittivity/permeability; reflection described by a Fresnel-type reflection coefficient at grazing incidence. *Justification:* standard electromagnetic treatment of seawater. *Validation:* literature comparison of seawater ε/σ values.
- **A7. Turbulence enters as a statistical roughness/tilt field.** Turbulent ocean effects will be represented via wave-spectrum statistics (e.g., significant wave height, slope variance, directionality) mapped to an additional attenuation/depolarization factor. *Justification:* turbulence is described empirically, not analytically. *Validation:* sensitivity to spectrum choice (e.g., different sea-state models).
- **A8. Calm ocean approximated as a smooth lossy surface** (near-specular reflection). *Justification:* provides the reference baseline for comparison.
- **A9. First hop definition.** "First reflection off the ocean" implicitly includes one preceding ionospheric reflection; geometry (incidence angles, hop length) is defined consistently across calm/turbulent cases.

### 3.3 Terrain assumptions (S4)
- **A10. Smooth terrain ≈ specular reflector; rugged/mountainous terrain ≈ partially diffuse scatterer** with shadowing, multi-path spread, and depolarization. *Justification:* standard radar/terrain-scattering dichotomy. *Validation:* qualitative comparison with empirical HF terrain-propagation literature.

### 3.4 Moving-receiver assumptions (S5)
- **A11. Ship position, heading, and speed are modeled as a bounded, parameterized trajectory; sea state is time-varying but statistically stationary over the analysis window.** *Justification:* "how long" implies a time-evolution model.
- **A12. Ionospheric state is quasi-static over the ship's observation window.** *Justification:* isolates the moving-receiver effect. *Validation:* relax later with time-varying ionosphere.
- **A13. Communication breaks when SNR (or path viability) falls below threshold, or when geometric/incidence constraints (e.g., multipath, skip distance) fail.** The precise break criterion will be defined explicitly.

### 3.5 Modeling-discipline assumptions
- **A14. Deterministic link-budget core with probabilistic/statistical treatment of turbulence and roughness.** Mixed deterministic–statistical framing will be documented.
- **A15. Units and reference conventions fixed and documented** (dB, W, m, MHz, sea-state indices) before analysis to avoid ambiguity.

---

## 4. Data Processing Plan

**Important observation on inputs:** The dataset definition supplied with this problem is empty —
`{"dataset_path": [], "dataset_description": {}, "variable_description": {}}` — and the `data/` directory contains no files. Therefore this is a **parameter-and-literature-driven modeling problem**, not a data-fitting problem. The "data plan" is consequently a **parameter governance and evidence-sourcing plan**.

### 4.1 Input categories to be assembled (to be sourced later, not in this draft)
1. **Physical constants:** seawater conductivity, relative permittivity (real/imaginary parts) vs. frequency and temperature; free-space impedance; Earth radius / geometric constants.
2. **Ionospheric parameters:** effective reflection height, absorption (e.g., D-layer) parameters, MUF scenario ranges (day/night, solar activity).
3. **Ocean-state parameters:** significant wave height, wave-spectrum parameters (peak frequency, fetch, directionality), surface slope statistics by sea state.
4. **Terrain parameters:** roughness scales, dielectric properties of land cover, slope statistics for smooth vs. mountainous classes.
5. **System parameters:** transmitter power (100 W), antenna pattern/carrier frequency range, receiver noise model, threshold SNR (10 dB).
6. **Ship dynamics parameters:** speed, heading, motion statistics, antenna behavior under platform motion.

### 4.2 Preprocessing plan
- **Unit harmonization** into a single SI-consistent convention (with dB/linear conversion utilities reserved for the implementation stage).
- **Parameter ranges and priorities:** each parameter tagged as *primary* (materially affects conclusions) or *secondary* (numerical refinement), with a documented plausible interval.
- **Provenance logging:** every parameter receives a source tag (reference, assumption, or scenario choice) so that traceability and sensitivity analysis are possible.
- **Scenario table construction:** explicit scenario matrix (calm/turbulent ocean × smooth/rugged terrain × day/night MUF × static/moving receiver) to be submitted to the model later.

### 4.3 Feature construction (model-ready derived quantities)
- Reflection geometry: incidence/grazing angles, hop arc length, effective Earth curvature corrections.
- Surface descriptors: roughness/slope-variance metrics derived from sea-state or terrain parameters.
- Link-budget terms: spreading loss, absorption loss, reflection loss, per-hop aggregate loss, cumulative loss.
- Time-series features (S5): time-varying path length, incidence angle, SNR trajectory, time-above-threshold.

### 4.4 Data usage strategy
- **No empirical fitting** will be required given the empty dataset; the model will be **forward-computed** from parameters and compared qualitatively/quantitatively against published HF propagation behavior.
- If auxiliary public reference data are used later, they will be labeled as *supporting* (for calibration of default parameter ranges), never as ground-truth fitted targets, and every use will be documented.

---

## 5. Candidate Model Framework

The framework will be layered so each subproblem reuses a common core.

### 5.1 Layer A — Surface reflection core (S1, S2, S4)
- **Candidate A1: Fresnel reflection-coefficient model** for a lossy dielectric medium at grazing incidence, expressed as a function of frequency, conductivity, permittivity/permeability, and incidence angle. Provides the calm-ocean baseline and the smooth-terrain analog.
- **Candidate A2: Roughness-modified reflection (perturbation / statistical roughness).** Multiply the Fresnel coefficient by a roughness attenuation factor derived from surface-height variance and incidence angle. Turbulent ocean and rugged terrain map onto this factor with different statistics.
- **Candidate A3: Kirchhoff / physical-optics or two-scale scattering models** as higher-fidelity alternatives if the perturbation model proves inadequate at strong roughness.
- **Variables:** frequency, grazing angle, ε/σ/μ of surface, surface-height variance/slope statistics, correlation length, polarization.
- **Advantages:** physically interpretable, directly comparable across ocean/terrain. **Limitations:** sensitivity to roughness-statistics assumptions; grazing-incidence numerical care.

### 5.2 Layer B — Multi-hop link budget (S3)
- **Candidate B1: Deterministic per-hop link budget.** End-to-end SNR as a product/sum (in dB) of transmit power, antenna gains, free-space spreading, ionospheric absorption and reflection losses, surface reflection losses, and receiver noise floor.
- **Candidate B2: Recursive hop formulation.** Express SNR after hop *k* as a function of SNR after hop *k−1* and the per-hop loss; solve for the hop index crossing 10 dB *as a model output to be produced later*.
- **Candidate B3: Probabilistic extension** in which per-hop loss is a random variable (sea-state variability), yielding an SNR distribution and a probability-of-usable-link metric.
- **Variables:** Tx power, frequency, per-hop geometry, losses, noise floor, threshold SNR, hop index.
- **Advantages:** transparent, controllable. **Limitations:** accuracy depends on loss-term fidelity; no full wave-turbulence interaction.

### 5.3 Layer C — Terrain-reflection module (S4)
- **Candidate C1: Specular smooth-surface model** (reuses Layer A with terrain parameters).
- **Candidate C2: Diffuse/multi-path terrain scattering model** incorporating surface-slope distribution, shadowing at low grazing angles, and polarization mismatch for mountains.
- **Candidate C3: Comparative normalization** so that calm-ocean, smooth-terrain, and rugged-terrain results are directly comparable at identical geometry.
- **Variables:** terrain roughness spectrum, slope statistics, grazing angle, surface material dielectric constants.

### 5.4 Layer D — Moving-receiver dynamics (S5)
- **Candidate D1: Kinematic trajectory model.** Parametric ship trajectory (speed, heading) updating incidence geometry and hop length over time.
- **Candidate D2: Time-varying surface state.** Sea-state evolution (steady or slowly changing) modulating the reflection coefficient over time.
- **Candidate D3: Time-dependent SNR criterion.** Define communication duration as the time interval over which SNR ≥ threshold (and geometric/path conditions hold); derive the duration as a model output.
- **Candidate D4 (optional): Stochastic platform-motion model** for antenna orientation/pointing fluctuations.
- **Variables:** time, position, velocity, heading, sea-state index, incidence angle, instantaneous SNR.

### 5.5 Cross-layer mathematical ideas to be considered
- Geometric optics + Fresnel coefficients at interfaces.
- Statistical surface-scattering theory (perturbation and two-scale methods).
- Radiative-transfer / scattering-albedo concepts as an optional abstraction for rough surfaces.
- Link-budget algebra and recursive/geometric progression modeling for hop accumulation.
- Stochastic processes (random fields for surface height; time-series for sea state) for the probabilistic extensions.
- Dimensional analysis and nondimensional groups (e.g., roughness-to-wavelength ratio) to generalize results.

### 5.6 Model selection strategy
A **baseline-first, fidelity-escalation** approach will be used: implement the simplest physically defensible combination (Fresnel + roughness factor + deterministic hop budget), document its behavior, then escalate fidelity (Kirchhoff scattering, probabilistic turbulence, stochastic dynamics) only where sensitivity analysis shows the baseline is inadequate.

---

## 6. Implementation Roadmap

This section describes *how a solver would build* the study; no code is written here.

### 6.1 Required modules (planned)
1. **Parameter registry module** — stores constants, ranges, sources, and scenario definitions.
2. **Reflection-core module** — computes surface reflection coefficient (calm/turbulent ocean; smooth/rugged terrain).
3. **Propagation/geometry module** — computes hop geometry, spreading and absorption terms, incidence angles.
4. **Hop-accumulation module** — chains per-hop losses and evaluates SNR vs. hop index.
5. **Terrain-comparison module** — swaps surface models and produces comparative outputs.
6. **Dynamics module** — evolves ship/receiver state and time-varying SNR.
7. **Sensitivity/uncertainty module** — parameter sweeps and scenario comparisons.
8. **Reporting module** — generates tables/figures and the Part IV synopsis draft.

### 6.2 Workflow (planned sequence)
1. Fix notation, units, and scenario matrix (from §4).
2. Implement and sanity-check the reflection core against limiting cases (normal incidence, perfectly conducting limit, grazing-incidence behavior).
3. Implement the multi-hop link budget; verify monotonic loss accumulation.
4. Run the calm-vs-turbulent first-reflection comparison (S2).
5. Determine hop count to the 10 dB threshold (S3).
6. Extend to terrain comparison (S4).
7. Extend to the moving-receiver dynamics and communication-duration criterion (S5).
8. Perform sensitivity/uncertainty analysis (§7.3).
9. Compile results, figures, and the IEEE-style synopsis (S6).

### 6.3 Dependencies and risks (planning-level)
- **Dependency:** accuracy of the noise-floor and absorption assumptions strongly affects the hop-count answer → treated as a first-class sensitivity axis.
- **Risk:** grazing-incidence reflection numerics can be ill-conditioned → plan explicit numerical care and limiting-case checks.
- **Risk:** turbulence lacks an analytic definition → plan scenario-based statistical surrogates with documented ranges.
- **Risk:** over-parameterization → baseline-first strategy mitigates.

---

## 7. Validation Strategy

### 7.1 Evaluation metrics (to be computed later)
- **Reflection-domain:** reflected-power ratio / reflection-coefficient magnitude (calm vs. turbulent; smooth vs. rugged), expressed in dB.
- **Link-domain:** predicted SNR after hop *k*; hop count at which SNR reaches 10 dB.
- **Terrain-domain:** relative difference between ocean, smooth-terrain, and rugged-terrain reflected power/SNR.
- **Dynamics-domain:** communication duration (time above threshold), SNR trajectory statistics, and sensitivity of duration to speed/sea state.
- **Model-quality diagnostics:** limiting-case correctness, internal consistency, and monotonicity checks.

### 7.2 Validation methods
- **Analytic limiting cases:** normal-incidence and perfect-conductor limits, zero-roughness reduction to Fresnel, zero-turbulence reduction to calm case.
- **Cross-model comparison:** perturbation vs. Kirchhoff/physical-optics scattering; deterministic vs. probabilistic link budgets.
- **Literature benchmarking:** qualitative/quantitative comparison with published HF propagation and sea-surface scattering behavior (no fitting, comparison only).
- **Internal consistency:** hop-budget recursion must reproduce the non-recursive total; dB/linear conversions must round-trip.
- **Physical plausibility:** signs, monotonic trends, and orders-of-magnitude sanity (no fabricated values in this draft).

### 7.3 Sensitivity and uncertainty analysis
- One-at-a-time sweeps across: frequency (within HF band), grazing angle, conductivity/permittivity, wave height/roughness spectrum, MUF scenario, noise-floor assumption, ship speed/heading, threshold definition.
- Global sensitivity (variance-based or factorial) if dimensionality warrants, to rank influential parameters.
- Scenario robustness: report how conclusions change across scenario matrix cells and identify parameters whose uncertainty could reverse a qualitative conclusion.

### 7.4 Reproducibility plan
- Fixed seed policy for any stochastic components; documented versions of parameter sources; full scenario matrix recorded; outputs regenerable from the parameter registry.

---

## 8. Expected Result Interpretation

This section describes *how the eventual outputs will be interpreted* — not what they are.

- **Calm vs. turbulent:** the interpretation will focus on the *magnitude and mechanism* of the extra turbulent loss (roughness/tilt/depolarization vs. dielectric change) and the conditions under which turbulence matters most (higher sea state, lower grazing angle).
- **Hop count to 10 dB:** the interpretation will report the crossing hop index together with its dependence on the dominant loss terms, explicitly stating which assumptions (noise floor, absorption) most influence the crossover.
- **Terrain comparison:** interpretation will contrast specular (smooth) vs. diffuse/shadowed (rugged) behavior, noting likely directions of effect while acknowledging terrain variability.
- **Moving receiver:** interpretation will express communication duration as a function of ship speed, heading, sea state, and threshold, and discuss whether the limiting factor is SNR degradation, geometry, or path integrity.
- **Publication synopsis:** interpretation will emphasize the transferable modeling insight (surface state as the controlling factor in multi-hop HF viability) rather than exhaustive numerics.

All interpretation statements are hypotheses to be confirmed or refuted by the later analysis; none are asserted as findings here.

---

## 9. Limitations and Improvements

### 9.1 Anticipated limitations
- **Empty dataset:** conclusions will rest on parameter assumptions and literature, limiting empirical grounding.
- **Idealized ionosphere:** geometric-optics reflection with fixed heights omits horizontal gradients, tilts, and scintillation.
- **Grazing-incidence approximations:** Fresnel + roughness-factor methods degrade at very low angles and very strong roughness.
- **Turbulence surrogates:** wave-spectrum statistics are a proxy for complex electromagnetic-gradient effects.
- **Link-budget granularity:** per-hop loss is aggregated; fine multipath/interference structure is out of scope.
- **Deterministic core:** real HF channels are strongly stochastic; the probabilistic extension is partial.

### 9.2 Planned improvements (future work)
- Couple with a ray-tracing or ionospheric model for more realistic MUF/absorption.
- Use full rough-surface scattering (integral-equation / two-scale) for strong sea states.
- Add a measured/observed reference for parameter calibration if data become available.
- Include modulation/bandwidth, interference, and fading statistics for realistic SNR modeling.
- Extend moving-receiver analysis to adaptive frequency/path selection and antenna pointing.
- Develop a full stochastic channel model with distributions rather than point estimates.

---

## Appendix A — Planning Checklist (to be used by the solver)

- [ ] Notation, units, and scenario matrix frozen.
- [ ] Parameter registry populated with sourced/assumed values and ranges.
- [ ] Reflection core validated against limiting cases.
- [ ] Calm vs. turbulent first-reflection comparison produced (S2).
- [ ] Hop count to 10 dB SNR determined with sensitivity bounds (S3).
- [ ] Terrain comparison produced (S4).
- [ ] Moving-receiver communication-duration analysis produced (S5).
- [ ] Sensitivity/uncertainty analysis completed (§7.3).
- [ ] IEEE-style synopsis drafted (S6).
- [ ] Reproducibility artifacts archived (§7.4).

## Appendix B — Compliance Statement

This draft contains **planning content only**. It performs no calculation, fits no model, runs no code or experiment, analyzes no data, and reports no final results or conclusions. All statements are forward-looking and describe intended workflow, assumptions, candidate methods, data/parameter governance, implementation, validation, and interpretation strategy.
