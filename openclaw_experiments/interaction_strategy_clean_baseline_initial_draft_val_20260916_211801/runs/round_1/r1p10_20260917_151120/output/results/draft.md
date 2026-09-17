# Modeling Blueprint Draft — Making Room for Agriculture (ICM 2025, Problem E)

> **Status:** Planning draft only. This document is a roadmap for future modeling work.
> It intentionally contains **no computed results, no data analysis, no fitted parameters, and no final conclusions**.
> All statements are written in future-oriented / conditional language.

---

## 1. Problem Background and Restatement

### 1.1 Situation (as given)
A forest ecosystem will be assumed to have been cleared and converted to agricultural land. Over time the system is described as transitioning through a sequence of ecological and management regimes:

1. **Pre-conversion forest** — a mature, self-regulating ecosystem.
2. **Clearing / conversion** — replacement of the forest community with cultivated crops; loss of structural and functional diversity.
3. **Early agricultural phase** — soil depletion and pest population growth, prompting increasing reliance on chemical inputs (herbicides, insecticides, fertilizers).
4. **Emergent agricultural ecosystem** — a new web of interactions emerges, including species such as bats and birds that re-colonize or adapt to the farmland matrix.
5. **Long-term management phase** — the farmer must choose among intervention strategies (conventional, reduced-input, organic) that shape ecosystem stability over multi-year horizons.

### 1.2 What the model must represent (restatement)
The task is to design a model of the **transition from forest to farm** that will:

- Track ecosystem state **over time**.
- Integrate **natural processes** (population dynamics, food-web interactions, nutrient/soil dynamics, pollination, pest regulation).
- Integrate **human decisions** (chemical use, herbicide removal, organic practices, crop rotation, timing of interventions).
- Evaluate, comparatively, the consequences of management choices for **crop yield, ecosystem stability, biodiversity, sustainability, and economic cost-effectiveness**.
- Support communication of recommendations to a non-specialist stakeholder (a farmer) through a one-page letter.

### 1.3 Deliverable context
The final competition-style submission would be up to 25 pages: a summary sheet, the complete solution, and a one-page farmer letter. The present draft will serve only as the structural and methodological blueprint that a later solution phase would execute.

---

## 2. Objectives and Subproblems

### 2.1 Primary objective
To design a **coupled ecological–economic dynamic model** that predicts how an agricultural ecosystem will evolve under alternative management strategies, and that can be used to compare the stability, biodiversity, productivity, and profitability of those strategies over time.

### 2.2 Subproblems (planned decomposition)

**SP1 — Food-web representation of the agricultural ecosystem.**
Design a network model of producers (crops, weeds, edge-habitat vegetation), consumers (pest insects, crop pests, natural enemies), and higher trophic levels (birds, bats, small mammals), including the roles of bats as insectivores and potential pollinators.

**SP2 — Agricultural cycle dynamics.**
Represent the within-season cycle (soil preparation → planting → growth → pest control → harvesting → decomposition/residue) and its coupling to inter-season soil fertility and pest carryover.

**SP3 — Chemical-input sub-model.**
Represent how herbicide and insecticide applications will alter pest, weed, and beneficial-species populations, including non-target and indirect effects.

**SP4 — Native-species re-emergence.**
Model the recolonization or recovery of native species into the converted area and how those species will feed back on the food web and on crop outcomes.

**SP5 — Herbicide-removal scenario.**
Design and compare a scenario in which herbicides will be withdrawn, with bats explicitly included as insectivores and pollinators, and evaluate the projected consequences for pest suppression and stability.

**SP6 — Organic-farming strategy analysis.**
Compare organic versus conventional management along dimensions of pest control, crop health, biodiversity, sustainability, and cost-effectiveness.

**SP7 — Economic / decision layer.**
Couple ecological outputs to a cost–benefit accounting structure (input costs, yield revenue, long-run soil and biodiversity value) so trade-offs can be quantified comparatively.

**SP8 — Stakeholder communication design.**
Plan the structure and the message content of the one-page farmer letter (recommendations, economic trade-offs, sustainability strategies), to be produced from the model's comparative findings at a later stage.

### 2.3 Mapping objectives → model components (planned)
| Subproblem | Planned model component |
|---|---|
| SP1 | Multi-trophic food-web / community dynamics block |
| SP2, SP3 | Seasonal crop–soil–pest block with control inputs |
| SP4 | Colonization / establishment sub-model for native species |
| SP5, SP6 | Scenario engine + management policy parameterization |
| SP7 | Economic accounting module |
| SP8 | Visualization + narrative synthesis layer |

---

## 3. Assumptions

Assumptions are grouped by role. Each is paired with a planned justification and a planned validation route.

### 3.1 Ecological / structural assumptions
- **A1 — The system will be represented as a spatially aggregated (well-mixed) unit.** *Justification:* to keep the model tractable and parameter-light at the initial stage; edge habitats would be treated as separate compartments rather than continuous space. *Validation:* later comparison against a spatially explicit or patch version to check whether aggregation changes qualitative conclusions.
- **A2 — A bounded set of functional groups (crops, weeds, pest herbivores, generalist predators, insectivorous bats, birds, soil biota/nutrient pool) will capture the dominant dynamics.** *Justification:* full species-level webs would be unidentifiable; functional grouping is standard in agro-ecology. *Validation:* sensitivity to group granularity (merge/split groups).
- **A3 — Bats will be modeled with dual roles: insectivory (top-down pest control) and pollination (a crop-relevant service).** *Justification:* stated in the problem's key considerations. *Validation:* scenario comparison of bat-present vs bat-absent variants.
- **A4 — Soil fertility will be treated as a state variable driven by residue/decomposition, fertilizer input, and crop uptake.** *Justification:* central to the described "soil depletion" narrative. *Validation:* qualitative check against known nutrient-depletion patterns.
- **A5 — Pests and beneficials will carry over between seasons through explicit overwintering/refuge terms.** *Justification:* multi-year behavior is essential to the problem. *Validation:* behavior under repeated identical seasons.

### 3.2 Management / decision assumptions
- **A6 — Human decisions will be represented as a discrete set of management policies (conventional, reduced-input, organic) applied over defined time windows.** *Justification:* makes scenarios comparable and interpretable. *Validation:* robustness to policy definition boundaries.
- **A7 — Farmers will be assumed to act according to a stated objective (e.g., maximize long-run net benefit subject to stability/sustainability constraints), which will be made explicit and testable.** *Justification:* enables a decision-analytic layer. *Validation:* alternative objective weightings.
- **A8 — Chemical applications will have both target effects and measurable non-target effects.** *Justification:* consistent with the problem's description of chemical disruption. *Validation:* parameter sweeps on non-target toxicity.

### 3.3 Economic / boundary assumptions
- **A9 — Prices, input costs, and yield-response functions will be drawn from literature or clearly stated synthetic values, with a sensitivity band rather than a single point value.** *Justification:* no dataset is supplied with the problem. *Validation:* wide-range sensitivity analysis.
- **A10 — The time horizon will be multi-year (seasonal resolution, several years to a few decades).** *Justification:* transition dynamics are the object of study. *Validation:* horizon-length robustness.
- **A11 — Climate/weather will be treated as either constant or as a stochastic forcing with a stated distribution.** *Justification:* isolates management effects from exogenous variability. *Validation:* deterministic vs stochastic comparison.

---

## 4. Data Processing Plan

> Note: the working directory currently contains **no provided datasets**; therefore the data plan is primarily about (a) sourcing external parameters and (b) constructing a controlled experimental design over model scenarios.

### 4.1 Data sources to be gathered (planned)
- **Ecological parameters:** trophic interaction strengths, growth/reproduction rates, mortality, consumption rates, and functional-response shape parameters for the chosen functional groups (from published agro-ecology and food-web literature).
- **Crop and soil parameters:** yield-response coefficients, nutrient-uptake rates, decomposition/residue rates, rotation effects.
- **Chemical-effect parameters:** efficacy and non-target effects of herbicides/insecticides on pests, weeds, and beneficials.
- **Bat/bird ecology parameters:** insect consumption rates, roost/foraging dependence on edge habitat, pollination contribution.
- **Economic parameters:** input prices, crop prices, transition costs (organic certification, yield drag), and long-run soil/biodiversity valuation proxies.

### 4.2 Preprocessing (planned)
1. **Harmonization:** convert all sourced quantities to a single consistent unit system (per-area, per-season).
2. **Range encoding:** store each parameter as a central tendency **plus a plausible range** to support later uncertainty/sensitivity work.
3. **Provenance tagging:** record source, unit, and confidence for every parameter so results can be traced.
4. **Missing-data policy:** where literature is sparse, plan to use explicitly-labeled synthetic defaults and to subject them to the widest sensitivity sweeps.

### 4.3 Feature / variable construction (planned)
- Field-level state vector: crop biomass, weed biomass, pest density, natural-enemy density, bat/bird abundance, soil nutrient pool, chemical residue/load.
- Derived indicators: crop yield proxy, pest pressure index, predator-to-pest ratio, Shannon-type diversity index for functional groups, stability metrics (variance, resilience proxies, return time after perturbation).
- Economic indicators: seasonal and cumulative net margin, input-cost share, long-run soil-capital proxy.

### 4.4 Data usage strategy (planned)
- **Parameterization split:** use literature-derived central values for the baseline and ranges for uncertainty bands.
- **Scenario design as the "dataset":** treat management × environment combinations as a designed experiment grid (see §6), to be simulated rather than observed.
- **Hold-out logic for validation:** reserve specific qualitative/quantitative empirical patterns (e.g., known pest outbreaks after herbicide removal) as checks the model must reproduce, rather than fitting them.

---

## 5. Candidate Model Framework

This section describes **candidate** model families and their planned roles; no model is fixed yet.

### 5.1 Core dynamical backbone (candidate A: Lotka–Volterra / generalized food-web ODEs)
- **Structure:** a system of coupled ordinary differential equations where each functional-group biomass follows a growth term minus losses to predation and control.
- **Mathematical idea (schematic):**
  - Producer growth: logistic-type with nutrient limitation.
  - Consumer growth: assimilation of consumed prey minus mortality (Holling-type functional responses as the refinement).
  - Control terms: herbicide/insecticide mortality applied as time-windowed, possibly density-dependent removal.
- **Advantages:** transparent, well-understood stability analysis, easy scenario switching.
- **Limitations:** aggregative, sensitive to functional-response choice, may not capture seasonal discreteness.

### 5.2 Candidate B: Seasonal / discrete-time crop–pest–soil model
- **Structure:** within-season continuous or stage-structured dynamics, with between-season discrete update rules (overwintering survival, residue decomposition, carryover).
- **Advantages:** naturally matches the "agricultural cycle" framing; cleanly represents planting/harvest events.
- **Limitations:** event scheduling must be defined; more bookkeeping.

### 5.3 Candidate C: Multi-trophic network / community matrix approach
- **Structure:** represent interaction signs and strengths as a community matrix; study local stability and the effect of adding/removing nodes (e.g., removing herbicide pressure, restoring bats).
- **Advantages:** strong handle on "ecosystem stability" as a formal property; good for structural comparisons.
- **Limitations:** linearized around equilibria; interpretability of absolute magnitudes limited.

### 5.4 Candidate D: Agent- or patch-based extension (spatial / edge-habitat)
- **Structure:** field plus edge-habitat patches with migration of bats/birds/beneficials; possibly agent-based for farmer decisions.
- **Advantages:** captures edge-habitat buffer role and spatial refuges.
- **Limitations:** higher computational and parameter burden; likely a later-stage refinement.

### 5.5 Candidate E: Economic / decision-analytic layer
- **Structure:** mapping from ecological states to economic outcomes; possibly dynamic optimization (optimal-control or Markov-decision framing) to find preferred policies under constraints.
- **Advantages:** converts ecological scenarios into farmer-relevant trade-offs.
- **Limitations:** objective specification is consequential; requires careful sensitivity analysis.

### 5.6 Planned integration architecture
A layered design will be considered: **(C/B) ecological core → (A) continuous-time dynamics → (E) economic overlay → (D) optional spatial refinement.** The core state variables (crop, weeds, pests, natural enemies, bats, birds, soil nutrients, chemical load) will be shared across layers so scenarios propagate consistently.

### 5.7 Stability and biodiversity formalization (planned, not computed)
- Candidate stability notions: local stability of equilibria, resilience/return-time proxies, variance under stochastic forcing, persistence (no extinction of functional groups).
- Candidate biodiversity notions: functional-group richness/evenness indices and predator/pollinator service coverage.

---

## 6. Implementation Roadmap

> Implementation will occur in a later phase. This section defines **what would be built and in what order**.

### 6.1 Runtime and library choices (planned)
- **Language:** Python (numerical ODE/integration and data-handling ecosystem) as the primary choice.
- **Core libraries:** `numpy`/`scipy` for integration and parameter sweeps; `pandas` for structured outputs; a plotting library for later visualization; optional `networkx`-style tooling for food-web structure.
- **Reproducibility:** fixed random seeds, versioned parameter files, and a configuration file describing each scenario.

### 6.2 Module breakdown (planned)
1. `config/` — scenario and parameter definitions (values + ranges + provenance).
2. `core_dynamics/` — food-web and crop–pest–soil equations.
3. `management/` — policy definitions (chemical schedules, organic rules, herbicide withdrawal).
4. `economics/` — cost–benefit accounting.
5. `scenarios/` — grid of management × environment combinations.
6. `analysis/` — stability, biodiversity, and trade-off metrics.
7. `viz/` — time-series, phase, network, and trade-off visualizations.
8. `report/` — assembly of figures/tables and the farmer letter (later phase).
9. `validation/` — checks against reserved qualitative patterns and sensitivity sweeps.

### 6.3 Workflow (planned sequence)
1. Formalize state variables and equations at a conceptual level.
2. Assemble the parameter table with ranges and provenance.
3. Implement the ecological core and verify basic behaviors (stable coexistence, sensible seasonality).
4. Implement management policies and scenario grid.
5. Implement economic overlay and derived indicators.
6. Run the scenario grid and collect time-series and summary indicators.
7. Perform stability, biodiversity, and trade-off analyses.
8. Perform sensitivity/uncertainty analysis.
9. Optionally add spatial/edge-habitat refinement.
10. Synthesize into figures, tables, and the farmer letter (later phase).

### 6.4 Milestones / checkpoints (planned)
- **M1:** conceptual model + variable list finalized.
- **M2:** parameter table complete with ranges.
- **M3:** ecological core verified on sanity scenarios.
- **M4:** scenario grid executed.
- **M5:** analyses + sensitivity complete.
- **M6:** synthesis artifacts ready.

---

## 7. Validation Strategy

### 7.1 Evaluation metrics (planned)
- **Ecological:** persistence of functional groups, predator-to-pest ratio, pest-pressure index, amplitude/variance of biomass time series, recovery time after perturbation, diversity index.
- **Productivity:** crop-yield proxy and its inter-season trend.
- **Economic:** net margin, cumulative profit, input-cost share, long-run soil-capital proxy.
- **Robustness:** fraction of parameter space in which a conclusion holds.

### 7.2 Validation methods (planned)
- **Qualitative pattern checks:** confirm the model can reproduce expected qualitative behaviors (e.g., pest resurgence after herbicide removal; improved natural-enemy control with bats present).
- **Consistency checks:** conservation/positivity of biomasses, boundedness, no spurious blow-ups, and sensible limiting behavior.
- **Cross-model comparison:** compare conclusions across candidate frameworks (e.g., ODE vs community-matrix vs discrete-season) for agreement on qualitative rankings.
- **Boundary testing:** extreme-parameter behavior (no control vs maximal control; zero vs abundant edge habitat).

### 7.3 Sensitivity / uncertainty analysis (planned)
- **One-at-a-time sweeps** over key parameters (interaction strengths, non-target toxicity, reproduction rates, economic weights).
- **Global sensitivity** (e.g., variance-based or factorial screening) to identify which parameters dominate conclusions.
- **Uncertainty bands** on all headline indicators, reported as ranges rather than point values.
- **Scenario robustness** checks: does the preferred management strategy change under plausible parameter shifts?

### 7.4 Threats to validity (planned acknowledgement)
- Aggregation may hide species-specific effects.
- Sparse empirical data for bat/bird parameters will increase uncertainty.
- Economic assumptions may drive conclusions; these will be stress-tested explicitly.

---

## 8. Expected Result Interpretation

> This section describes **how future results would be read**, not any actual finding.

- **Scenario comparisons** would be interpreted as **relative** rather than absolute forecasts: which management strategy would be projected to yield higher stability/biodiversity/profit under stated assumptions.
- **Trade-off structures** would be expected to emerge between short-term yield and long-term soil/biodiversity health; the blueprint anticipates presenting these as trade-off curves/regions.
- **Herbicide-removal analysis** would be interpreted through the lens of whether restored bat/natural-enemy function would compensate for reduced chemical control, and under what conditions.
- **Organic-strategy analysis** would be interpreted along the five stated dimensions (pest control, crop health, biodiversity, sustainability, cost-effectiveness), with an explicit note on which dimensions would be in tension.
- **Uncertainty** would be reported as ranges; conclusions would be framed as conditional on assumptions and would be accompanied by robustness statements.
- **Farmer letter** content would be derived from the comparative structure above, emphasizing actionable methods, economic trade-offs, and sustainability strategies.

---

## 9. Limitations and Improvements

### 9.1 Anticipated limitations
- **Model aggregation** will trade ecological realism for tractability.
- **Parameter scarcity**, especially for bats/birds and non-target chemical effects, will widen uncertainty.
- **Economic layer** will depend on assumed prices/policies that vary by region.
- **Spatial simplification** (well-mixed) will under-represent edge habitats unless the patch extension is added.
- **Stochastic climate** may be simplified to constant or simple noise.

### 9.2 Planned improvements / extensions
- Add **spatial/patch structure** to represent edge habitats and refuges explicitly.
- Upgrade **functional responses** and add **stage structure** (e.g., pest generations, bat breeding).
- Introduce **dynamic decision models** (optimal control / MDP) so farmer behavior is endogenous.
- Incorporate **real regional data** (crops, prices, species lists) where available, replacing synthetic defaults.
- Extend validation with **empirical case studies** of herbicide withdrawal and organic transitions.
- Add **multi-objective optimization** to identify Pareto-optimal management strategies across ecological and economic goals.

---

## Appendix A — Planning Checklist (for the later solution phase)
- [ ] Finalize state-variable list and equation forms.
- [ ] Assemble provenance-tagged parameter table with ranges.
- [ ] Implement and sanity-check the ecological core.
- [ ] Implement management policies and the scenario grid.
- [ ] Implement economic overlay and indicators.
- [ ] Execute scenarios and collect outputs.
- [ ] Run stability, biodiversity, and trade-off analyses.
- [ ] Run sensitivity/uncertainty analyses.
- [ ] Produce figures/tables and the one-page farmer letter.

## Appendix B — Compliance Note
This document contains only planning content: objectives, assumptions, a candidate-model survey, a data plan, an implementation roadmap, a validation strategy, expected interpretation guidance, and limitations. **No problem solving, data analysis, computation, fitting, coding, experimentation, or results are included.**
