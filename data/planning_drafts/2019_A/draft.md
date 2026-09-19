# MM-Bench 2019_A — Modeling Blueprint Draft

**Problem ID:** `2019_A`
**Title:** MM-Bench 2019_A (Dragons of *A Song of Ice and Fire*)
**Document type:** Initial modeling plan draft (roadmap only — no solving, no data analysis, no computations)
**Status:** Blueprint for future modeling work

> This document is a planning artifact. It defines objectives, assumptions, candidate
> models, a data strategy, an implementation roadmap, and a validation plan. It contains
> no computed results, no fitted parameters, and no final conclusions. All quantities are
> described symbolically or as *to-be-estimated* placeholders.

---

## 1. Problem Background and Restatement

The problem is set in the fictional world of *A Song of Ice and Fire* / *Game of Thrones*,
where three dragons are raised by Daenerys Targaryen. Documented (in-universe) biological
facts to be preserved:

- Three dragons exist today; they were hatched small and grow throughout life.
- Approximate mass at hatching is on the order of **10 kg**.
- After approximately one year they reach roughly **30–40 kg**.
- Continued growth is **conditions- and food-dependent** (not fixed).
- Dragons are assumed able to **fly great distances, breathe fire, and resist tremendous trauma**.

The problem asks for an analysis of dragon **characteristics, behavior, habits, diet, and
interaction with the environment**, and at minimum requires answers to:

1. **Ecological impact and requirements** of the dragons.
2. **Energy expenditures** and **caloric intake requirements**.
3. **Land area** required to support the three dragons.
4. **Community size** necessary to support a dragon under **varying levels of human assistance**.
5. **Climate sensitivity** — does moving a dragon between an **arid**, **warm temperate**,
   and **arctic** region materially change the resources required to maintain and grow it?
6. A **cross-domain transfer** discussion: what real-world (non-fictional) situations could
   this modeling inform?
7. A **two-page letter to George R. R. Martin** giving guidance on maintaining a realistic
   ecological underpinning, especially regarding dragon movement across climate zones.

**Restatement framing.** The task is a coupled *bioenergetics + ecology + logistics* problem.
It links a dynamic growth model (mass over time under feeding and climate), an energy-budget
model (metabolic cost vs. intake), a spatial-resource model (area → prey productivity →
sustainable dragon biomass), and a socioeconomic model (community size vs. assistance level),
with a narrative deliverable (the letter) derived from the model's qualitative conclusions.

**Note on inputs.** The dataset definition supplied with this task is empty
(`dataset_path: []`, empty description/variable objects), and the staged `data/` directory
contains no files. The plan therefore treats the problem as **parameter-driven by
literature and first-principles estimation**, with all numerical inputs to be sourced or
assumed during execution and documented explicitly.

---

## 2. Objectives and Subproblems

### 2.1 Primary objective
Produce a defensible, internally consistent quantitative framework describing the
bioenergetics, ecological footprint, and support requirements of three dragons, robust to
reasonable variation in assumptions, and translate it into ecological guidance.

### 2.2 Subproblems (planned decomposition)

| ID | Subproblem | Planned deliverable |
|----|------------|---------------------|
| S1 | **Growth law** — mass(t) as function of age, diet, climate | Growth model family + parameterization plan |
| S2 | **Energy budget** — maintenance + activity + thermoregulation + growth | Symbolic energy-balance equations |
| S3 | **Caloric intake** — prey/food mass required per unit time | Intake-to-prey-mass conversion framework |
| S4 | **Ecological impact & requirements** — prey base, predation pressure, waste/heat/fire effects | Food-web / trophic-demand model |
| S5 | **Land area** — area needed to sustain prey for 3 dragons | Primary productivity → carrying-capacity chain |
| S6 | **Community size** — humans needed vs. assistance level (wild → fully husbanded) | Assistance-scenario matrix |
| S7 | **Climate sensitivity** — arid vs. temperate vs. arctic resource multipliers | Climate-parameter overlay on S1–S5 |
| S8 | **Cross-domain transfer** — real-world analogies | Discussion grounded in model structure |
| S9 | **Letter to GRRM** | Narrative synthesis (two pages, no new math) |

### 2.3 Deliverables (final, future)
- A documented modeling framework with explicit assumptions register.
- Scenario results for the three climate zones and assistance levels.
- A sensitivity/uncertainty summary.
- The two-page guidance letter.
- (Optional) Supporting diagrams of the model architecture and scenario trees.

---

## 3. Assumptions

Assumptions are grouped by role. Each will be registered with: statement, rationale,
range/uncertainty, and the validation approach that will later test it.

### 3.1 Biological / physiological assumptions (to be documented and later stress-tested)
| # | Assumption (intent) | Rationale | Future validation approach |
|---|---|---|---|
| A1 | Dragon metabolism scales with body mass via a power law (metabolic scaling exponent to be estimated/hypothesized) | Standard comparative physiology; enables scaling | Compare with reptile/bird/mammal scaling ranges; sensitivity on exponent |
| A2 | Dragons are (at least partially) endothermic or regionally warm-bodied, given fire-breathing and long-distance flight | Flight and fire imply high power output | Bracket ectotherm-like vs. endotherm-like scenarios |
| A3 | Growth continues indefinitely but decelerates (asymptotic or allometric growth form) | Consistent with "grow throughout life" and 10→30–40 kg/yr | Bracket logistic vs. Gompertz vs. von Bertalanffy vs. power law |
| A4 | Adult mass range (large but finite) | Needed for bounded resource estimates | Treat as scenario parameter, not fixed |
| A5 | Energy costs: basal/maintenance, locomotion (flapping flight), thermoregulation, growth, fire production | Decomposition of energy budget | Sub-model cross-check against analogous large avians/bats |
| A6 | Fire-breathing is metabolically costly and consumes a fuel/energy store | Physical plausibility | Sensitivity on fire frequency and cost per event |
| A7 | Flight range implies either high energy reserves or refueling stops; metabolic rate during flight is elevated | "Fly great distances" | Range-vs-energy feasibility check |
| A8 | Dragons are predators at or near the top of a food web | Ecological impact framing | Trophic-level sensitivity |

### 3.2 Ecological assumptions
| # | Assumption (intent) | Rationale | Future validation approach |
|---|---|---|---|
| A9 | Prey energy content and trophic transfer efficiency follow standard ecological efficiency ranges | Enables biomass→area translation | Bracket transfer efficiency (low/high) |
| A10 | Land carrying capacity is limited by net primary productivity → herbivore → predator chain | Standard food-web energetics | Compare across biomes |
| A11 | Environmental heat loss depends on ambient temperature and body size/surface area | Drives climate sensitivity | Sensitivity to insulation/behavior |
| A12 | Dragons disturb the ecosystem (predation pressure, fire, nutrient deposition, thermal effects) | "Ecological impact" requirement | Qualitative + semi-quantitative scenario review |

### 3.3 Socioeconomic / operational assumptions
| # | Assumption (intent) | Rationale | Future validation approach |
|---|---|---|---|
| A13 | Assistance levels form a continuum from fully wild to fully provisioned (food, shelter, veterinary, security) | Required "varying levels of assistance" | Define discrete scenario ladder |
| A14 | Human assistance substitutes for foraging/thermoregulation effort by some efficiency factor | Enables community-size model | Sensitivity on substitution efficiency |
| A15 | Community size scales with the labor/food/land needed to supply a dragon at a given assistance level | Links ecology to demography | Historical analogies (e.g., large-animal husbandry) |

### 3.4 Simplifying / modeling assumptions
| # | Assumption (intent) | Rationale | Future validation approach |
|---|---|---|---|
| A16 | Single-dragon dynamics generalize to three via linear or shared-resource coupling | Simplifies from 1→3 | Test resource-sharing (cooperative vs. competitive foraging) |
| A17 | Climate zones represented by representative annual temperature profiles and biome productivities | Enables comparison | Use climate/biome parameter tables |
| A18 | Time horizon for maintenance estimates is a defined planning window (e.g., year-scale) | Bounds answer | Sensitivity to horizon length |
| A19 | No explicit magic beyond stated traits; "fictional" traits are treated as physical constraints | Keeps model physically grounded | Physics/biology consistency checks |

*All assumption values are placeholders to be fixed (with justification) during execution;
none are computed here.*

---

## 4. Data Processing Plan

Because **no dataset is staged**, the data plan is a *parameter-sourcing and
structure-building* plan rather than a file-processing pipeline.

### 4.1 Data/parameter sources to be assembled (future)
- **Physiological scaling data:** metabolic rate vs. mass for reptiles, birds, mammals, bats.
- **Flight energetics data:** power curves / flight cost coefficients for large flying animals.
- **Diet/energy content:** energy densities of candidate prey (livestock, large game, fish).
- **Ecological efficiency:** trophic transfer efficiency and net primary productivity by biome.
- **Climate data:** representative monthly temperature profiles and productivity for arid,
  warm-temperate, and arctic zones.
- **Socioeconomic analogs:** stocking/feeding/labor data from large-animal husbandry operations.

### 4.2 Preprocessing plan
1. **Unit harmonization** — normalize all inputs to a single system (SI: kg, J, m², K).
2. **Traceability tagging** — every parameter gets a source label (literature / assumed / derived)
   and a plausible range, not a single point value.
3. **Imputation strategy** — where data are missing, define *scenario brackets* (low/central/high)
   rather than a single estimate.
4. **Consistency screening** — flag physically impossible combinations (e.g., energy intake
   exceeding plausible consumption rates).

### 4.3 Feature / derived-quantity construction (future)
- Body mass and surface area as the primary scaling variables.
- Metabolic rate, thermoregulatory load, and flight power as derived energy terms.
- Prey biomass demand and required land area as derived ecological quantities.
- Assistance-level and climate-zone indices as scenario features.

### 4.4 Data usage strategy
- Maintain a **central parameter table** with ranges; drive all scenario runs from it.
- Keep an **assumptions register** alongside the parameter table for auditability.
- Treat "data" as evidence to bound the model, not as ground truth to be fit to.

---

## 5. Candidate Model Framework

A layered framework is proposed; each layer can be swapped independently, enabling
scenario comparison and sensitivity analysis.

### 5.1 Layer 1 — Growth model (S1)
- **Candidates:** von Bertalanffy, Gompertz, logistic, and power-law (allometric growth).
- **Variables:** mass M(t), age t, asymptotic mass parameter, growth-rate parameter,
  feed-availability modifier, climate modifier.
- **Rationale:** each form encodes different biology (indeterminate vs. asymptotic growth).
- **Advantages/limits:** simple and interpretable, but the growth form is uncertain →
  treat as a scenario choice, not a fixed truth.

### 5.2 Layer 2 — Energy budget (S2, S3)
- **Structure (symbolic):** total daily energy demand = maintenance + activity/locomotion +
  thermoregulation + growth + optional fire production; compared against intake from prey.
- **Candidates:** allometric metabolic scaling; heat-transfer (conductive/convective) terms
  for thermoregulation; biomechanical flight-power estimates for locomotion.
- **Variables:** metabolic coefficient & exponent, activity fraction, ambient temperature,
  insulation/effective surface area, specific energy content of prey.
- **Advantages/limits:** physically grounded; but exponent and activity assumptions dominate
  results → sensitivity is essential.

### 5.3 Layer 3 — Ecological demand (S4, S5)
- **Structure (symbolic):** prey energy demand → prey biomass → prey production → required
  net primary productivity → land area, using trophic transfer efficiency.
- **Candidates:** trophic-dynamic energy-chain model; carrying-capacity model; optional
  Lotka–Volterra-style predator–prey interaction for impact assessment.
- **Variables:** transfer efficiency, prey energy density, prey productivity per unit area,
  number of dragons (3), foraging radius.
- **Advantages/limits:** connects bioenergetics to geography; sensitive to assumed
  efficiency and productivity ranges.

### 5.4 Layer 4 — Climate overlay (S7)
- **Structure (symbolic):** climate zone modifies (a) thermoregulation energy term,
  (b) prey productivity, (c) foraging/activity behavior, (d) shelter needs.
- **Candidates:** parameter overlays (temperature multiplier, productivity multiplier) applied
  to Layers 2–3; optionally a seasonal (time-varying) forcing model.
- **Advantages/limits:** directly answers the arid/temperate/arctic question; requires
  representative climate parameters.

### 5.5 Layer 5 — Support & community model (S6)
- **Structure (symbolic):** assistance level defines fraction of energy/shelter provided;
  remaining demand must be met by landscape → links to land area; human labor/food supply
  → community size.
- **Candidates:** scenario matrix (wild / semi-assisted / intensive husbandry); resource-balance
  equations; optional optimization (minimize land or community size subject to dragon survival).
- **Advantages/limits:** yields the required community-size answer across assistance levels.

### 5.6 Layer 6 — Impact & synthesis (S4, S8, S9)
- Qualitative and semi-quantitative assessment of ecological impact; cross-domain transfer
  narrative; the two-page letter.

### 5.7 Integrated view
A single **parameter table** feeds Layers 1–5; a **scenario driver** enumerates
(climate zone × assistance level × growth form) combinations; outputs feed sensitivity
analysis and narrative synthesis.

---

## 6. Implementation Roadmap

### 6.1 Modules to be built (future)
1. **`params`** — central parameter/assumption registry with ranges and source tags.
2. **`growth`** — pluggable growth-law implementations (Layer 1).
3. **`energy`** — energy-budget terms (maintenance, flight, thermoregulation, growth, fire).
4. **`ecology`** — trophic/land-area/impact computations (Layer 3).
5. **`climate`** — climate-zone parameter overlays and seasonal forcing (Layer 4).
6. **`support`** — assistance-level and community-size model (Layer 5).
7. **`scenarios`** — scenario enumeration and orchestration.
8. **`analysis`** — sensitivity, uncertainty, and comparison summaries.
9. **`report`** — table/figure/narrative generation, including the GRRM letter.

### 6.2 Workflow (planned sequence)
1. Finalize the assumptions register and parameter table (with ranges).
2. Implement and unit-check each layer independently on nominal inputs.
3. Integrate layers and run the scenario matrix.
4. Perform sensitivity analyses across dominant parameters.
5. Summarize results into the ecological-impact discussion and the letter.
6. Document limitations and reproducibility notes.

### 6.3 Implementation considerations
- Keep layers decoupled so growth form, scaling exponent, and efficiency can be swapped.
- Every run must record its parameter draws for reproducibility.
- Prefer bracketed/scenario outputs over single point estimates.
- Guard against physically inconsistent parameter combinations.

---

## 7. Validation Strategy

### 7.1 Internal consistency checks
- **Mass/energy closure:** energy intake must be sufficient to cover all budget terms plus growth.
- **Dimensional analysis:** verify every equation is dimensionally consistent.
- **Endpoint checks:** verify the model can reproduce the stated anchors (≈10 kg at hatch,
  ≈30–40 kg at ~1 year) under central assumptions — used only as a plausibility check, not
  as fitting performed here.

### 7.2 Comparative / plausibility validation
- Compare metabolic and flight-energy estimates against analogous large flying/kite-scale
  animals and against ecological efficiency norms.
- Compare land-area results against known predator home-range scaling relationships.

### 7.3 Sensitivity analysis (planned)
- **One-at-a-time:** metabolic exponent, growth form, trophic efficiency, activity fraction,
  thermoregulation coefficient, ambient temperature.
- **Global:** Monte Carlo / Latin-hypercube sampling over parameter ranges to obtain output
  distributions and rank parameter influence.
- **Scenario (structural):** arid vs. temperate vs. arctic; wild vs. assisted vs. husbanded.

### 7.4 Uncertainty communication
- Report outputs as ranges/bands, not single values.
- Clearly separate *assumed* vs. *literature-sourced* vs. *derived* inputs.
- State which conclusions are robust vs. parameter-dependent.

### 7.5 Evaluation metrics (to be defined in execution)
- Consistency residuals (energy/mass closure).
- Sensitivity indices (influence ranking).
- Scenario deltas (relative change across climate/assistance scenarios).

---

## 8. Expected Result Interpretation

This section anticipates *how* outputs will be read once produced (no results are given here).

- **Growth model:** expected to yield a monotone, decelerating mass–age curve consistent with
  the stated anchors; different growth forms are expected to diverge mainly at later ages.
- **Energy/intake:** expected to scale strongly with mass; climate and activity are expected to
  be major modifiers, so results should be presented as bands.
- **Land area & ecological impact:** expected to depend primarily on trophic transfer
  efficiency and prey productivity; results should be expressed per-dragon and for three dragons,
  with impact framed qualitatively (predation pressure, fire/thermal disturbance).
- **Community size:** expected to decrease monotonically as assistance level rises
  (wild landscape support vs. fully provisioned husbandry); the interesting result is the
  *relative* change across the assistance ladder.
- **Climate sensitivity:** expected to show that arctic zones impose the largest
  thermoregulatory and provisioning burden and arid zones the largest water/prey-productivity
  constraints, with temperate zones intermediate — a hypothesis to be tested, not a conclusion.
- **Cross-domain transfer:** the framework is expected to inform real problems such as
  managing large introduced predators, invasive-species resource demands, rewilding and
  carrying-capacity planning, and food/energy provisioning for large captive animals.
- **Letter to GRRM:** will translate model structure into narrative guidance: how climate
  migrations should plausibly alter dragon resource needs and ecological pressure.

All of the above are *expected interpretive frames*, not findings.

---

## 9. Limitations and Improvements

### 9.1 Anticipated limitations
- **No staged data:** model is parameter/literature-driven; results inherit input uncertainty.
- **Fiction–physics gap:** traits like fire-breathing and trauma resistance have no direct
  biological analog, so their costs must be assumed.
- **Model-form uncertainty:** growth law, metabolic exponent, and trophic efficiency are all
  uncertain and can dominate outputs.
- **Aggregation:** treating three dragons via single-dragon dynamics may miss
  resource competition or cooperation.
- **Spatial generality:** climate zones are represented abstractly, not as real geographies.

### 9.2 Planned improvements / extensions
- Replace scalar climate parameters with seasonal time-series forcing.
- Add explicit multi-dragon interaction (competition vs. cooperation) and spatial foraging models.
- Introduce optimization formulations (minimize land or community size subject to survival constraints).
- Expand the assumption register into a fully auditable uncertainty budget.
- Add agent-based or system-dynamics extensions for ecological impact dynamics.

### 9.3 Scope discipline
This blueprint intentionally excludes: solved equations, numeric results, fitted parameters,
executed experiments, generated plots, and final conclusions. Those belong to the subsequent
modeling stage.

---

## Appendix A — Section-to-Requirement Traceability

| Problem requirement | Blueprint section(s) |
|---|---|
| Ecological impact & requirements | §2 (S4), §3.2, §5.3, §5.6, §8 |
| Energy expenditures & caloric intake | §2 (S2,S3), §3.1, §5.2, §8 |
| Land area for three dragons | §2 (S5), §5.3, §8 |
| Community size vs. assistance level | §2 (S6), §3.3, §5.5, §8 |
| Climate-zone importance | §2 (S7), §3.4, §5.4, §8 |
| Cross-domain transfer discussion | §2 (S8), §5.6, §8 |
| Two-page letter to GRRM | §2 (S9), §5.6, §8 |

## Appendix B — Assumption Register Template (to be completed in execution)

| Field | Description |
|---|---|
| ID | Unique assumption identifier |
| Statement | Precise assumption text |
| Category | Biological / Ecological / Socioeconomic / Modeling |
| Value or range | Placeholder pending execution |
| Justification | Rationale / literature basis |
| Sensitivity | Expected influence on outputs |
| Validation | How it will be tested |

---

*End of initial modeling blueprint draft. No problem solving, data analysis, or computation
has been performed; this document is a roadmap for future work only.*
