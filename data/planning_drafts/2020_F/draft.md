# Initial Modeling Plan Draft — MM-Bench 2020_F
## Environmentally Displaced Persons (EDPs), Climate Migration, and Cultural Preservation

> **Status: MODELING BLUEPRINT — PLANNING ONLY.**
> This document is a forward-looking roadmap. It contains no solutions, no numerical results,
> no fitted models, no experiments, and no final conclusions. All statements describe what the
> future modeling effort **will** do.

---

## 1. Problem Background and Restatement

### 1.1 Background (as given)

Rising sea levels threaten the territorial existence of several low-lying island nations
(e.g., The Maldives, Tuvalu, Kiribati, The Marshall Islands). When a nation's land disappears,
its people — **environmentally displaced persons (EDPs)** — will need to relocate, and there is a
compounding risk that a unique culture, language, and way of life will be lost. The problem
raises interrelated questions: *Where will EDPs go? Which countries will accept them? Should the
nations that contributed most to greenhouse-gas emissions carry a higher obligation? Who decides
the destination — the individuals, an intergovernmental body such as the UN, or the receiving
states?*

### 1.2 Restatement of the Task

Following a UN ruling that opened the door to recognizing EDPs as a new class of refugees, the
**International Climate Migration Foundation (ICM-F)** has engaged the modeling team to advise
the UN. The team **will develop one or more models** and use them to analyze *when, why, and how*
the UN should intervene in the growing EDP challenge, with explicit attention to **cultural
heritage preservation**.

The final paper will be expected to include, at minimum:

1. An analysis of the **scope of the issue** — the number of people at risk and the risk of
   cultural loss.
2. **Proposed policies** addressing both human rights (resettlement and full participation in the
   new home) and cultural preservation.
3. A description of the **model(s)** used to measure the potential impact of the proposed policies.
4. An explanation of **how the model informed the design/improvement** of those policies.
5. A **justification, backed by the analysis**, of the importance of implementing the policies.

### 1.3 Scope Boundary for This Draft

Because the problem is intentionally broad ("extremely complex"), this plan will define a
**bounded scope**: a quantitative core (displacement scale, timing, allocation) plus a
semi-quantitative cultural-value layer, integrated into a policy-evaluation framework. The plan
will explicitly state which aspects are treated, approximated, or deferred.

---

## 2. Objectives and Subproblems

### 2.1 Primary Objective

To design, validate, and apply a coherent set of models that will **quantify the scale and timing
of EDP displacement**, **represent the value and vulnerability of at-risk cultures**, and
**evaluate candidate international policies** on human-rights and cultural-preservation criteria,
in order to produce defensible recommendations for the UN.

### 2.2 Subproblems (to be addressed by the future modeling work)

| # | Subproblem | Question the model will answer |
|---|------------|-------------------------------|
| S1 | **Exposure & risk mapping** | Which island nations/atolls are at risk, and by what horizon, under sea-level-rise (SLR) scenarios? |
| S2 | **Displacement magnitude & timing** | How many people will become EDPs, and on what time path (annual/decadal)? |
| S3 | **Cultural value & loss risk** | How will the "value" of an at-risk culture be represented, and how does it degrade under dispersal vs. concentrated resettlement? |
| S4 | **Responsibility allocation** | How will historical/current emissions contributions translate into differentiated obligations to accept or fund EDPs? |
| S5 | **Destination & matching** | Which receiving states are feasible, and how will EDP-to-destination matching be optimized? |
| S6 | **Governance & decision rights** | How will the model compare individual choice, UN coordination, and receiving-state discretion? |
| S7 | **Policy design & comparison** | Which policy packages best satisfy human-rights and cultural-preservation objectives, and how will impacts be measured? |
| S8 | **Robustness & implications** | How sensitive are recommendations to assumptions, and what are the implications of adopting vs. rejecting them? |

### 2.3 Deliverables (future)

- A documented **data assembly pipeline** and a **country/atoll-level dataset** (with provenance).
- One or more **descriptive/projection models** (SLR → exposure → displacement).
- A **cultural-value representation** scheme and its dynamics.
- A **policy-evaluation / optimization model** producing comparative impact measures.
- A **validation and sensitivity report**.
- A **synthesis narrative** answering the five minimum requirements (§1.2).

---

## 3. Assumptions

Assumptions will be grouped by function, each with a justification and a planned validation route.
They will be treated as **parameters or switches** wherever possible so that sensitivity analysis
can test them.

### 3.1 Physical / Environmental Assumptions

| ID | Assumption (to be adopted) | Justification | Planned validation |
|----|----------------------------|---------------|--------------------|
| A1 | Future SLR will follow published scenario envelopes (e.g., IPCC-style low/central/high pathways). | Standard, transparent, scenario-based practice. | Compare against multiple published projections; bracket uncertainty. |
| A2 | Inundation is driven primarily by SLR plus tidal/storm surge, with limited protective capacity. | Low-lying atolls have minimal elevation and limited adaptation options. | Cross-check with elevation datasets and case literature. |
| A3 | Land-loss thresholds can be approximated by elevation and habitability criteria rather than full hydrodynamic simulation. | Keeps scope tractable; detailed inundation modeling is out of scope. | Sensitivity to threshold choice. |

### 3.2 Demographic / Migration Assumptions

| ID | Assumption (to be adopted) | Justification | Planned validation |
|----|----------------------------|---------------|--------------------|
| A4 | Population projections will follow UN/World-Bank-style trajectories with migration as a modeled variable. | Consistent baseline sources; comparable across nations. | Compare with published population outlooks. |
| A5 | Some pre-emptive/voluntary migration will occur before full land loss. | Observed behavior in at-risk states. | Sensitivity to migration-propensity parameter. |
| A6 | Displacement is effectively irreversible once habitability thresholds are crossed. | No practical large-scale return option. | Scenario tests with partial-return variants. |

### 3.3 Cultural Assumptions

| ID | Assumption (to be adopted) | Justification | Planned validation |
|----|----------------------------|---------------|--------------------|
| A7 | Cultural persistence depends on factors such as population concentration, language transmission, institutional continuity, and community cohesion. | These are established drivers of cultural survival. | Expert-informed weighting; sensitivity analysis. |
| A8 | Culture will be represented as a multi-indicator value/depreciation construct rather than a single monetary figure, with an optional monetized variant. | Cultural value is multidimensional and contested; monetization alone is inadequate. | Compare index-based and monetized variants. |

### 3.4 Economic / Political Assumptions

| ID | Assumption (to be adopted) | Justification | Planned validation |
|----|----------------------------|---------------|--------------------|
| A9 | Emissions responsibility can be proxied by cumulative and per-capita historical emissions. | Widely used equity metrics (e.g., "historical responsibility"). | Multiple proxy definitions; sensitivity. |
| A10 | Receiving-state capacity and willingness can be proxied by economic size, land/space, and policy openness indicators. | Operationally measurable; data available. | Sensitivity and expert review. |
| A11 | The UN can credibly coordinate/allocate only under agreed rules; sovereign consent will be modeled as a constraint. | Reflects real institutional limits. | Scenario variants (binding vs. voluntary). |

### 3.5 Boundary Assumptions (explicitly stated)

- A12 | The model will **not** attempt full geophysical, legal, or geopolitical simulation.
- A13 | "Value of culture" will be treated as a **modeling construct** with stated limitations,
  not as a definitive valuation.

---

## 4. Data Processing Plan

### 4.1 Data Sources (to be assembled — no data currently staged)

Because the provided dataset definition is empty, the plan will **assemble** inputs from public
sources. Candidate source families (to be finalized and cited with provenance and retrieval date):

- **Sea-level / climate**: IPCC-style SLR scenario tables; satellite altimetry summaries.
- **Topography / land**: global elevation and atoll/coastline datasets.
- **Demography**: UN population and urbanization outlooks; national census summaries.
- **Cultural indicators**: UNESCO/language-vitality datasets; ethnographic and language-atlas sources.
- **Emissions**: historical and current national emissions inventories.
- **Receiving-state capacity**: economic, land-area, and migration-policy indicators.
- **Legal/institutional**: existing refugee/EDP frameworks and UN documents.

> All sources will be stored in the `data/` directory with a **manifest** recording origin, year,
> units, license, and retrieval date. No data will be analyzed within this planning phase.

### 4.2 Preprocessing Steps (planned)

1. **Schema harmonization**: standardize country/territory identifiers (ISO codes) and year keys.
2. **Unit normalization**: align SLR (mm/m), population (counts), emissions (mass), areas (km²).
3. **Temporal alignment**: resample all series to a common time grid (e.g., 5-year steps).
4. **Missing-data handling**: document, impute via transparent rules, or flag for exclusion.
5. **Geographic consistency**: reconcile island/atoll names across datasets.
6. **Provenance logging**: each transformation recorded for reproducibility.

### 4.3 Feature Construction (planned)

- **Exposure features**: fraction of land below habitability threshold per horizon/scenario.
- **Population-at-risk features**: projected population on exposed land.
- **Cultural-vulnerability features**: language transmission, institutional density, dispersion risk.
- **Responsibility features**: cumulative and per-capita emissions shares.
- **Capacity features**: receiving-state absorptive-capacity indicators.
- **Policy features**: resettlement mode (dispersed vs. enclave), funding level, governance rule.

### 4.4 Data Usage Strategy (planned)

- **Calibration set**: historical exposure/population for model tuning.
- **Scenario set**: SLR × demographic × policy combinations for projection.
- **Hold-out / cross-check**: independent country cases for qualitative validation.
- Explicit separation of **observable data** from **elaborated/assumed constructs**.

---

## 5. Candidate Model Framework

The plan will use a **modular multi-model architecture**, because no single model can span
physical, demographic, cultural, and policy dimensions. Modules will be loosely coupled so that
assumptions in one can be varied without rebuilding the others.

### 5.1 Module M1 — Exposure & Land-Loss Module (physical)

- **Candidate approaches**: threshold/bathymetry-based exposure mapping; simple inundation-
  fraction curves; scenario-conditioned habitability functions.
- **Key variables**: SLR scenario \(s\), time \(t\), elevation \(e\), habitability threshold \(\tau\).
- **Mathematical idea**: define exposure as a function \(E(s,t)=\text{share of land with elevation}<\tau(s,t)\).
- **Advantages**: transparent, fast, scenario-driven. **Limitations**: ignores detailed
  hydrodynamics, subsidence, and adaptation.

### 5.2 Module M2 — Population & Displacement Module (demographic)

- **Candidate approaches**: cohort/stock-flow population projection; gravity/agent-based migration
  where feasible; scenario-conditioned displacement curves.
- **Key variables**: population \(P_i(t)\), exposed share, migration propensity \(m\), in/out flows.
- **Mathematical idea**: \(P_i(t+\Delta)=P_i(t)+B-D+\text{in}-\text{out}\), with forced displacement
  triggered when exposure crosses a threshold.
- **Advantages**: standard, interpretable. **Limitations**: migration behavior is uncertain and
  partly assumed.

### 5.3 Module M3 — Cultural Value & Loss Module (semi-quantitative)

- **Candidate approaches**: composite cultural-vulnerability index; survival/propagation model over
  concentration and continuity; optional monetized ("cultural capital") variant.
- **Key variables**: language transmission rate, community concentration, institutional continuity,
  intergenerational contact.
- **Mathematical idea**: represent culture as a vector state that depreciates under dispersal and
  is sustained by concentration/continuity; compare preservation scenarios.
- **Advantages**: makes cultural risk explicit and comparable. **Limitations**: inherently
  value-laden; must be validated by experts and scenario tests.

### 5.4 Module M4 — Responsibility Allocation Module (equity)

- **Candidate approaches**: cumulative-emissions share weighting; per-capita responsibility;
  hybrid "obligation index" combining historical and current contributions.
- **Key variables**: emissions shares, capacity indicators, obligation weights.
- **Mathematical idea**: \(O_j = f(\text{historical emissions}_j, \text{per-capita}_j, \text{capacity}_j)\).
- **Advantages**: operationalizes a contested fairness question transparently.
  **Limitations**: choice of responsibility metric is normative.

### 5.5 Module M5 — Destination Matching & Allocation Module (optimization)

- **Candidate approaches**: assignment/transportation optimization; multi-criteria decision analysis
  (MCDA); fair-division / matching mechanisms.
- **Key variables**: EDP cohorts, receiving-state capacities, welfare/cultural-fit scores.
- **Mathematical idea**: per horizon, choose an allocation \(x_{ij}\) maximizing aggregate welfare
  (and cultural persistence) subject to capacity and consent constraints.
- **Advantages**: quantifies trade-offs and produces candidate allocations.
  **Limitations**: assumes capacities/willingness that are political and uncertain.

### 5.6 Module M6 — Policy Design & Comparison Module (integrated)

- **Candidate approaches**: scenario comparison across a policy portfolio; multi-objective
  evaluation; optional system-dynamics integration across M1–M5.
- **Key variables**: policy levers (governance rule, funding, resettlement mode, legal status).
- **Mathematical idea**: map policy vectors → impacts on demographic, cultural, and equity
  outcomes; compare on a Pareto/weighted objective.
- **Advantages**: directly serves the "how the model informed policy" requirement.
  **Limitations**: nesting of modules introduces compounded uncertainty.

### 5.7 Cross-Module Design Choices

- Prefer **transparent, interpretable** constructions over black-box models given the policy audience.
- Keep **ML/statistical surrogates** as optional accelerators only where data support them.
- Maintain an explicit **assumption register** so every module's behavior is traceable.

---

## 6. Implementation Roadmap

> No code will be written in this phase. The roadmap below describes the planned build order.

### 6.1 Phased Workflow

1. **Phase 0 — Scoping & assumptions**: finalize scope, assumption register, and objective weights.
2. **Phase 1 — Data assembly**: collect, document, and normalize sources into `data/`.
3. **Phase 2 — M1/M2 build**: exposure and displacement projections across scenarios.
4. **Phase 3 — M3 build**: cultural-value/vulnerability representation.
5. **Phase 4 — M4 build**: responsibility/obligation indices.
6. **Phase 5 — M5 build**: destination matching and allocation optimization.
7. **Phase 6 — M6 integration**: policy portfolio comparison.
8. **Phase 7 — Validation & sensitivity**: full test battery (see §7).
9. **Phase 8 — Synthesis**: translate results into recommendations and implications.

### 6.2 Required Modules (software view, planned)

- `data_ingest` — loaders per source with manifest logging.
- `preprocess` — harmonization, alignment, imputation.
- `exposure_model` (M1), `displacement_model` (M2), `culture_model` (M3).
- `responsibility_model` (M4), `allocation_optimizer` (M5).
- `policy_engine` (M6) — scenario orchestration.
- `validation` — metrics, back-tests, sensitivity sweeps.
- `reporting` — tables, figures, and narrative generation (figures only in later solving phases).

### 6.3 Engineering Practices (planned)

- Config-driven scenarios (no hard-coded parameters).
- Versioned assumption register and data manifest.
- Reproducible runs with fixed seeds for any stochastic component.
- Unit checks for each module's outputs before integration.

---

## 7. Validation Strategy

### 7.1 Evaluation Metrics (to be defined)

- **Physical/demographic**: exposure fraction accuracy vs. reference cases; plausibility of
  displacement trajectories; comparison to published outlooks.
- **Cultural**: internal consistency of the vulnerability index; expert-panel agreement;
  scenario discrimination (does it distinguish dispersal vs. enclave outcomes?).
- **Equity/allocation**: coverage of need, respect for capacity constraints, fairness measures
  (e.g., proportionality, minimum-acceptance guarantees).
- **Policy**: objective attainment, Pareto-efficiency, and robustness to perturbation.

### 7.2 Validation Methods (planned)

- **Internal consistency checks** across coupled modules.
- **Face validity** against historical case studies of climate/relocation events.
- **Cross-source triangulation** for demographic and emissions inputs.
- **Expert elicitation** for cultural and normative parameters.
- **Comparative benchmarking** of allocation results against simple heuristic baselines.
- **Scenario back-testing** where historical data permit.

### 7.3 Sensitivity & Uncertainty Analysis (planned)

- One-at-a-time sweeps on key parameters (SLR pathway, migration propensity, cultural weights,
  responsibility metric, capacity assumptions).
- **Global** methods (e.g., Monte Carlo / variance-based) where computational budget allows.
- **Structural sensitivity**: swap module formulations (e.g., index vs. monetized culture) and
  compare conclusions.
- **Scenario matrix**: cross SLR × policy × governance-rule variants.
- **Robustness criterion**: recommendations will be reported only if stable across a defensible
  range of assumptions; otherwise flagged as conditional.

---

## 8. Expected Result Interpretation

*(Interpretation guidance only — no results are produced here.)*

### 8.1 How Future Outputs Will Be Read

- **Scope outputs** (people at risk, timelines) will be read as **scenario-conditioned ranges**,
  not point predictions.
- **Cultural outputs** will be read as **comparative risk signals** across resettlement modes,
  not absolute valuations.
- **Allocation outputs** will be read as **candidate, feasibility-checked options** subject to
  political consent.
- **Policy comparisons** will be read as **trade-off maps** across human-rights, cultural, and
  equity objectives.

### 8.2 Intended Narrative for the ICM-F / UN Briefing

- Frame the issue with a defensible **order-of-magnitude scope** and its **time horizon**.
- Present a **policy portfolio** (not a single silver bullet), each item linked to modeled impact.
- Show explicitly **how each policy lever changes the modeled outcomes**.
- State **implications of accepting vs. rejecting** recommendations in terms of human-rights and
  cultural outcomes, with uncertainty caveats.
- Emphasize **which conclusions are robust** and which depend on normative choices.

### 8.3 Reporting Conventions (planned)

- Always pair estimates with the scenario and assumption set that generated them.
- Separate **model-derived** statements from **normative** statements.
- Provide **confidence/robustness qualifiers** on every headline claim.

---

## 9. Limitations and Improvements

### 9.1 Anticipated Limitations

- **No staged dataset**: all inputs must be assembled externally; provenance and comparability
  risks are high.
- **Geophysical simplification**: inundation, subsidence, and adaptation are approximated.
- **Behavioral uncertainty**: migration decisions and receiving-state willingness are political
  and hard to model.
- **Cultural valuation is contestable**: any index or monetization is a modeling choice.
- **Normative fairness choices**: responsibility metrics embed value judgments.
- **Compounded uncertainty**: coupling multiple uncertain modules can amplify error.

### 9.2 Planned Improvements / Extensions

- Replace threshold exposure with finer inundation modeling when data allow.
- Add **adaptive-capacity** dynamics (sea walls, land reclamation) where feasible.
- Incorporate **agent-based** migration behavior for richer heterogeneity.
- Develop **participatory/expert validation** for the cultural module.
- Add **multi-objective optimization** with explicit equity constraints.
- Build a **decision-support interface** to let stakeholders vary assumptions interactively.
- Extend to **dynamic policy feedback** (policies changing future migration and capacity).

### 9.3 Risk Management

- Maintain a **traceable assumption register** so any conclusion can be audited.
- Report **ranges and conditionalities**, never unsupported point claims.
- Flag **out-of-scope** dimensions explicitly rather than silently ignoring them.

---

## Appendix A — Assumption Register Template (to be populated later)

| ID | Module | Assumption | Type (param/switch) | Value/Range | Source | Validation |
|----|--------|------------|---------------------|-------------|--------|------------|
| — | — | — | — | — | — | — |

## Appendix B — Planned File Structure (later phases)

```
output/
  data/            # assembled, documented source datasets + manifest
  code/            # modules M1–M6, validation, reporting
  results/         # draft.md (this file); later: tables/figures
  logs/            # run logs, provenance
```

## Appendix C — Mapping to Minimum Paper Requirements (§1.2)

| Requirement | Planned sections |
|-------------|------------------|
| (1) Scope: people at risk & cultural loss | M1–M3, §8.1 |
| (2) Proposed policies (rights + culture) | M4–M6, §8.2 |
| (3) Model to measure policy impact | M5–M6 |
| (4) How model informed policy | M6, §8.2 |
| (5) Importance of implementing policies | §8.2, §9 |

---

*End of planning draft. No problem solving, data analysis, computation, or results are included,
by design.*
