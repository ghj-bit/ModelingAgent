# Modeling Blueprint Draft — MM-Bench 2020_E
## Managing Single-Use / Disposable Plastic Product Waste

> **Status:** Planning draft only. This document is a *roadmap* for future modeling.
> It contains no calculations, no fitted parameters, no data analysis, and no results.
> All quantitative statements are placeholders to be determined during execution.

---

## 1. Problem Background and Restatement

### 1.1 Background
Global plastics manufacturing has grown roughly exponentially since the 1950s, driven by
packaging, consumer goods, medical devices, and construction. Plastic waste is persistent,
difficult to dispose of, and only a small fraction is recycled; a large and growing mass of
waste escapes into the environment and oceans each year. Marine-life impacts are relatively
well documented, whereas human-health effects remain incompletely understood. The core
structural problem is temporal: the *useful lifetime* of single-use/disposable plastic is far
shorter than the time required to safely mitigate its waste. The client, the **International
Council of Plastic Waste Management (ICM)**, therefore needs a scientific plan to
significantly reduce (ideally eliminate) single-use and disposable plastic product waste.

### 1.2 Restatement of Deliverables (as stated by the client)
The eventual solution must address four interrelated requirements:

1. **Mitigation-capacity model** — estimate the maximum levels of single-use/disposable
   plastic product waste that can be *safely mitigated without further environmental damage*,
   accounting for waste sources, current problem magnitude, and processing-resource availability.
2. **Reduction-potential discussion** — assess the extent to which plastic waste can be reduced
   to an environmentally safe level, considering sources/uses, availability of alternatives,
   impacts on citizens' lives, and regional/national/continental policies and their effectiveness.
3. **Target-setting** — using the model, set a target for the *minimal achievable* level of global
   single-use/disposable plastic waste and discuss consequences (human life, environment,
   multi-trillion-dollar plastic industry).
4. **Equity analysis** — discuss how causes/effects are unequally distributed across nations and
   regions, and recommend how ICM should address these inequities.

### 1.3 Final Communication Product
A **two-page memo to ICM** presenting a realistic global target minimum achievable waste level,
a timeline to reach it, and circumstances that accelerate or hinder attainment. The memo is the
integration layer that translates model outputs and discussion into an actionable recommendation.

### 1.4 Data-Situation Note
The staged `data/` directory is empty and the problem provides no structured dataset
(`dataset_path: []`, empty descriptions). The problem is therefore **open-data / literature-driven**.
The modeling plan must include an explicit external data-sourcing component (see §4).

---

## 2. Objectives and Subproblems

### 2.1 Overall Objective
Design a defensible, regionally-resolved, dynamic decision-support framework that (a) quantifies
the current and projected flow of single-use/disposable plastic waste, (b) estimates the maximum
safely-mitigable waste volume under resource constraints, (c) identifies a minimal achievable
global waste target with a timeline, and (d) evaluates equity implications and policy levers.

### 2.2 Subproblem Decomposition

| ID | Subproblem | Guiding Question | Preliminary Method Family (to be confirmed) |
|----|-----------|------------------|----------------------------------------------|
| SP1 | Waste-flow accounting | How much single-use/disposable plastic is produced, consumed, and discarded, by region and product class? | Material-flow / mass-balance accounting |
| SP2 | Mitigation capacity | What is the maximum waste mass that can be safely processed given available resources and environmental limits? | Constrained optimization / capacity (throughput) model |
| SP3 | Environmental safety threshold | What defines an "environmentally safe" waste level, and how is it bounded? | Threshold / carrying-capacity / damage-function formulation |
| SP4 | Reduction potential & policy effectiveness | Which reduction levers (alternatives, bans, fees, EPR, recycling) yield what effect, where? | Scenario modeling + policy-lever elasticity |
| SP5 | Target & timeline | What is the minimal achievable global target and a feasible trajectory to it? | Optimal-control / dynamic pathway optimization |
| SP6 | Equity | How are burdens/benefits distributed, and what does ICM do about it? | Multi-criteria / distributional-equity indices |
| SP7 | Recommendation synthesis | How to compress everything into a 2-page memo? | Structured narrative + figure/table schema |

### 2.3 Cross-Cutting Design Principles
- **Regionally disaggregated**, because causes and effects differ by nation/region.
- **Time-dynamic**, because production, mitigation and policy effects evolve.
- **Uncertainty-aware**, because data are sparse and heterogeneous.
- **Policy-relevant**, because outputs must drive ICM decisions.

---

## 3. Assumptions

Assumptions are grouped by role. Each states a *justification* and how it will be
*validated or relaxed* later.

### 3.1 Environmental / Physical
- **A1 — Finite safe-accumulation budget.** A bounded environmental carrying capacity exists for
  plastic waste in a given medium/region beyond which damage is deemed unacceptable.
  *Justification:* ecological thresholds and persistence of plastic pollutants.
  *Validation:* sensitivity of final target to the chosen threshold; cross-check vs. literature bounds.
- **A2 — Persistence / slow degradation.** Single-use plastic is treated as effectively persistent
  over the planning horizon relative to its use lifetime.
  *Justification:* slow degradation vs. short product life.
  *Validation:* test alternative decay/sink rates and observe target stability.
- **A3 — No catastrophic regime shift** within the planning horizon (avoiding step-change tipping
  events in the baseline model; handled as scenario stress-tests instead).

### 3.2 Economic / Behavioral
- **A4 — Substitutability is partial and cost-constrained.** Alternatives exist for most single-use
  functions but at varying cost and performance penalties.
  *Justification:* existing material-substitution evidence.
  *Validation:* vary substitution-elasticity parameters in scenario analysis.
- **A5 — Policy levers act with measurable, bounded elasticity** on consumption and waste rates.
  *Validation:* benchmark elasticities against observed policy outcomes where available.
- **A6 — Producers/consumers respond to price and regulation signals** (no fully irrational behavior).

### 3.3 Data / Modeling
- **A7 — Proxy/aggregated data acceptable.** Where regional granularity is missing, use documented
  proxies and aggregated national/continental data with explicit uncertainty flags.
- **A8 — Mass conservation** holds in the accounting framework (production = use + waste + stock;
  waste = recycled + incinerated + landfilled + leaked).
- **A9 — Stationary data-generating relationships** for parameter estimation unless a scenario
  explicitly models structural change.
- **A10 — Homogeneity within a mapped product class** for tractability, subject to documented caveats.

### 3.4 Scope Assumptions (stated so the memo is honest)
- Focus is on **single-use/disposable** plastic, not durable plastics (a boundary to be
  documented and revisited).
- Planning horizon and target year are **decision variables to be chosen**, not assumed.

---

## 4. Data Processing Plan

### 4.1 Data Sourcing Strategy (no data were staged)
Because there is no provided dataset, the plan is to assemble a **multi-source, multi-scale
data layer**. Candidate source categories (to be identified, licensed, and documented):
- Global/regional plastic production, consumption, and waste-generation statistics.
- Municipal-solid-waste and recycling/incineration/landfill rate datasets.
- Ocean-leakage and mismanaged-waste estimates.
- Population, GDP, urbanization, and waste-per-capita indicators (for drivers/forecasting).
- Policy inventories (bans, fees, EPR, deposit schemes) with dates and coverage.
- Material-substitution / alternative-material cost and performance references.

### 4.2 Data Governance and Provenance
- Record **source, year, geography, definition, and units** for every series (a data dictionary).
- Maintain a **confidence/uncertainty grade** per series (measured / estimated / modeled / proxy).
- Keep raw data immutable; all transformation is scripted and traceable (see §6).

### 4.3 Preprocessing Pipeline (planned steps)
1. **Harmonization of units** (mass units, currency, population base) and reference years.
2. **Geography reconciliation** to a common regional taxonomy (e.g., country → continent/income group).
3. **Product-class reconciliation** to a consistent single-use/disposable taxonomy.
4. **Missing-data handling**: interpolation, proxy substitution, or explicit exclusion —
   each choice logged and flagged.
5. **Outlier / consistency checks** using mass-balance identities (A8).
6. **Vintage alignment** so all series share a consistent time base.

### 4.4 Feature Construction (planned)
- **Per-capita waste intensity** and its drivers.
- **Regional aggregation features** (continent, income tier, coastal vs. landlocked).
- **Policy-intensity indices** (coverage × stringency × duration).
- **Substitution-potential indices** per product class.
- **Mitigation-capacity features** (treatment infrastructure, recycling capability, resource budgets).
- **Equity features** (per-capita burden, contribution share, mitigation capacity share).

### 4.5 Data Usage Strategy
- **Training/calibration** data for parameter estimation (historical relationships).
- **Scenario inputs** for future pathways (drivers, policies, technology).
- **Held-out / cross-source checks** for validation (§7).
- Because sources are heterogeneous, prefer **structured reconciliation over naive concatenation**,
  and prefer **ranges over point values** where uncertainty is high.

---

## 5. Candidate Model Framework

The framework is modular so each block can be developed, validated, and swapped independently.

### 5.1 Module M1 — Waste-Flow / Mass-Balance Accounting (supports SP1, SP3)
- **Idea:** a regionally-disaggregated, time-indexed material-flow model tracking plastic from
  production → consumption → end-of-life → fate (recycled / incinerated / landfilled / leaked).
- **Candidate formalisms:** input–output / material-flow analysis; system-dynamics stock–flow model.
- **Key variables:** production, consumption, waste generation, treatment capacities, leakage.
- **Advantages:** transparent, conserves mass, policy-interpretable.
- **Limitations:** sensitive to data quality; may under-represent informal systems.

### 5.2 Module M2 — Safe-Mitigation Capacity Model (supports SP1, SP2, SP3)
- **Idea:** determine the maximum waste mass that can be mitigated without further environmental
  damage, given resource and environmental constraints.
- **Candidate formalisms:** constrained optimization (maximize mitigated waste s.t. capacity and
  environmental-threshold constraints); bottleneck/throughput analysis for treatment infrastructure.
- **Key variables:** treatment throughput, cost per unit, resource budgets, allowable environmental load.
- **Advantages:** directly answers the client's "maximum safely mitigated" question.
- **Limitations:** constraint specification is judgment-heavy; capacity data are uncertain.

### 5.3 Module M3 — Environmental Safety Threshold (supports SP3)
- **Idea:** formalize "environmentally safe" as a bounded damage/carrying-capacity condition.
- **Candidate formalisms:** damage-function / carrying-capacity formulation; threshold or
  cumulative-exposure constraint; optionally a soft penalty rather than a hard bound.
- **Advantages:** converts a fuzzy concept into a modelable constraint.
- **Limitations:** normative; must be stress-tested and disclosed.

### 5.4 Module M4 — Policy / Substitution Scenario Model (supports SP4)
- **Idea:** map policy levers and substitution options to changes in waste flows.
- **Candidate formalisms:** elasticity-based response model; scenario/systems simulation;
  optionally agent-based for behavioral heterogeneity (secondary).
- **Key variables:** policy coverage/stringency, price signals, substitution rates, adoption curves.
- **Advantages:** lets regional policies be compared and combined.
- **Limitations:** behavioral parameters uncertain; causal attribution is difficult.

### 5.5 Module M5 — Dynamic Target & Timeline Optimization (supports SP5)
- **Idea:** find the *minimal achievable* global waste level and a feasible trajectory toward it.
- **Candidate formalisms:** optimal control / dynamic optimization of a waste-reduction pathway;
  multi-stage programming with technology-adoption and policy-rollout dynamics; scenario-based
  feasibility search as a robust fallback.
- **Key variables:** target level, target year, investment/policy schedule, adoption rates.
- **Advantages:** produces the exact deliverables (target + timeline) requested for the memo.
- **Limitations:** solution depends on M1–M4 parameters; needs strong sensitivity analysis.

### 5.6 Module M6 — Equity / Distributional Analysis (supports SP6)
- **Idea:** quantify unequal distribution of causes, burdens, and mitigation capacity.
- **Candidate formalisms:** distributional equity indices (contribution vs. burden vs.
  capacity shares), Gini-style/ratio measures, multi-criteria decision analysis (MCDA) to rank
  ICM interventions under equity-weighted objectives.
- **Advantages:** addresses an explicit problem requirement and strengthens recommendations.
- **Limitations:** normative weighting; data scarcity for informal/most-affected regions.

### 5.7 Module M7 — Synthesis / Recommendation Layer (supports SP7)
- **Idea:** integrate M1–M6 into the target, timeline, and 2-page memo, with explicit
  mechanisms for acceleration/hindrance.
- **Candidate formalisms:** structured narrative synthesis; decision matrix summarizing
  target, timeline, levers, risks, and equity actions.
- **Advantages:** ensures the modeling *communicates* a decision, not just numbers.
- **Limitations:** must avoid overclaiming precision.

### 5.8 Integration View
```
External data → [Data layer §4] → M1 flow → M2 capacity → M3 threshold
                                              ↓
                          M4 policy/substitution → M5 target+timeline
                                              ↓
                                  M6 equity → M7 synthesis → 2-page memo
```
A **coupled-simulation** approach is preferred over a single monolithic model, so modules can be
validated independently and their interactions examined via scenario sweeps.

---

## 6. Implementation Roadmap

### 6.1 Planned Workflow (phases)
1. **Scoping & variable dictionary** — finalize regions, product classes, horizon, and glossary.
2. **Data acquisition & dictionary** — assemble sources, log provenance and uncertainty grades.
3. **Data preprocessing** — harmonize, reconcile, impute/proxy, and validate via mass balance.
4. **Module development** — implement M1→M6 incrementally, each with unit-level checks.
5. **Coupling & scenario engine** — connect modules; define scenario grid (policy × tech × region).
6. **Optimization / pathway search** — run M5 target-and-timeline search.
7. **Equity analysis** — run M6 on candidate solutions.
8. **Validation & sensitivity** — execute §7.
9. **Synthesis** — build the memo, figures, and decision tables.
10. **Reproducibility packaging** — freeze environment, scripts, and data manifest.

### 6.2 Required Modules / Components (deliverables of code, not this draft)
- Data ingestion + provenance logger.
- Harmonization/cleaning utilities and consistency (mass-balance) checker.
- M1 flow model, M2 capacity optimizer, M3 threshold block.
- M4 scenario/policy engine.
- M5 pathway optimizer.
- M6 equity/MCDA analysis.
- Visualization/summary generator (for the memo's figures/tables).
- Configuration + experiment-tracking layer (so scenarios are reproducible).

### 6.3 Engineering Practices (planned)
- Configuration-driven runs (all assumptions exposed as parameters).
- Deterministic seeds and version pinning for reproducibility.
- Modular interfaces so any module can be replaced without rewriting the pipeline.
- Automated smoke tests per module; full-pipeline regression before final synthesis.

### 6.4 Deliverable Artifacts (future outputs, not produced here)
- `results/` figures and tables (waste trajectories, capacity curves, equity maps, scenario compares).
- The final two-page ICM memo.
- Reproducibility bundle (data manifest + scripts + config).

---

## 7. Validation Strategy

### 7.1 Evaluation Metrics (candidate)
- **Structural correctness:** mass-balance residuals (should approach zero by construction).
- **Predictive/backtest fit:** error on held-out historical periods (e.g., MAPE/RMSE on waste series).
- **Cross-source agreement:** consistency between independent datasets for overlapping regions/years.
- **Feasibility metrics:** optimizer feasibility rates and slack on capacity/environmental constraints.
- **Robustness:** stability of the target/timeline under parameter perturbation.
- **Equity metrics:** distributional indices and their response to interventions.

### 7.2 Validation Methods
- **Internal consistency checks** (conservation identities, unit/dimension checks).
- **Backtesting** on historical data withheld from calibration.
- **Cross-validation across regions** (fit some regions, test others).
- **Benchmarking** against published estimates and policy-outcome case studies.
- **Expert/plausibility review** of assumptions and thresholds.

### 7.3 Sensitivity and Uncertainty Analysis
- **One-at-a-time (OAT) sweeps** on key parameters (substitution elasticity, capacity growth,
  environmental threshold, policy stringency).
- **Global sensitivity** (e.g., variance-based methods) to rank influential parameters.
- **Monte-Carlo simulation** to propagate input uncertainty into target/timeline distributions.
- **Scenario / stress testing** (accelerants vs. hindrances; tipping-point sensitivity).
- **Bounds testing:** report target and timeline as intervals, not single points.

### 7.4 Skeptical-Hypothesis Checks
- Actively test whether the recommended target is **robust** to pessimistic assumptions, and
  whether it depends on any single contested parameter. Document where conclusions are fragile.

---

## 8. Expected Result Interpretation

*(Interpretation guidance only — no results are produced in this draft.)*

### 8.1 What the Outputs Would Represent
- **M1–M3** would characterize the current waste problem and the *maximum safely mitigable* volume.
- **M5** would yield a **candidate global minimum waste level** plus a **timeline**, expressed as
  a range/interval reflecting uncertainty.
- **M6** would express the **distributional consequences** of that target across regions.

### 8.2 Interpretation Principles
- Report targets as **ranges with key assumptions**, never as false precision.
- Distinguish **technically achievable** from **economically/politically feasible** levels.
- Identify which levers and regions are **binding** (bottlenecks) for the target.
- Explicitly surface **accelerators and hindrances** for the memo's timeline discussion.

### 8.3 Mapping to the Client's Memo
The memo will translate the above into: the recommended target, a phased timeline, the
conditions that speed up or slow down progress, and concrete equity actions for ICM.

---

## 9. Limitations and Improvements

### 9.1 Anticipated Limitations
- **Data scarcity/heterogeneity** for informal waste systems and many regions; proxies introduce bias.
- **Normative thresholds** (environmental safety, equity weights) are value-laden.
- **Behavioral/economic parameters** are uncertain and context-dependent.
- **Module coupling** can amplify or mask individual errors.
- **Aggregation** loses sub-national detail.
- **Deterministic core** may understate extreme/tail scenarios (reserved for stress tests).

### 9.2 Planned Improvements
- Progressively **finer regional resolution** and informal-sector modeling.
- **Probabilistic** treatment of key parameters and robustness-optimization variants.
- **Causal-inference / policy-evaluation** methods to firm up policy-effect estimates.
- **Endogenous technology and adoption** dynamics instead of exogenous assumptions.
- **Broader equity frameworks** (multi-dimensional, affected-population weighted).
- **Open, versioned data pipeline** to allow external review and extension.

---

## Appendix A — Planning Checklist (pre-execution)
- [ ] Regions, product classes, horizon, and target-year definition fixed.
- [ ] Data sources identified, licensed, documented with uncertainty grades.
- [ ] Assumptions A1–A10 reviewed and logged as configurable parameters.
- [ ] Module interfaces (M1–M6) specified before implementation.
- [ ] Metrics, validation splits, and sensitivity grid defined.
- [ ] Memo structure and required figures/tables drafted (as a template, not data).

## Appendix B — Explicit Non-Goals of This Draft
This document does **not** solve the problem; it deliberately excludes any computation,
data analysis, model fitting, code, experiments, plots, or results. It defines *how* the
modeling will be done.
