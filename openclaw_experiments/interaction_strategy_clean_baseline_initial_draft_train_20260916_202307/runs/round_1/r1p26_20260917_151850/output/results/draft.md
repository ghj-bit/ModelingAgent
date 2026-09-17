# Modeling Blueprint Draft — "Drowning in Plastic" (ICM 2020)

**Problem ID:** `2020_Drowning_in_Plastic`
**Status:** Initial modeling plan (roadmap only). No analysis, computation, or results are included.
**Deliverables to be produced later:** one-page Summary Sheet, two-page Memo to the ICM, and a solution report not exceeding 20 pages.
**Note on inputs:** no raw dataset was supplied with this run. The data plan below therefore treats source discovery, acquisition, and harmonization as an explicit future work item rather than an assumption that data already exists.

---

## 1. Problem Background and Restatement

The world has seen exponential growth in plastic manufacturing since the 1950s, driven by packaging, consumer goods, medical devices, and construction. Roughly 9% of plastic is recycled, and an estimated 4–12 million tons of plastic waste is expected to enter the oceans annually. Under current trends, total ocean plastic mass could exceed fish biomass by mid-century. Marine-life impacts are comparatively well studied, while human-health impacts remain incompletely understood. The core structural issue is a mismatch between product lifetime (very short) and mitigation/degradation lifetime (very long).

The modeling team will be acting as a consultant to the International Council of Plastic Waste Management (ICM). The work will aim to produce a defensible, regionally differentiated roadmap for curbing single-use and disposable plastic product waste, culminating in a proposed global minimum achievable waste target, a timeline, and a two-page memo.

Restated as modeling questions to be addressed in future work:

1. What volume of single-use/disposable plastic waste can be safely mitigated (processed, recycled, contained, or degraded) without causing further environmental damage, given source, current burden, and processing-resource constraints?
2. To what extent can plastic waste be reduced toward an environmentally safe level under realistic behavioral, technological, economic, and policy constraints?
3. What global minimum achievable waste level and timeline should be recommended, and how will that target interact with human welfare, ecosystems, and the plastic industry?
4. How should equity concerns — asymmetric causes and effects across regions — be represented and addressed in the recommendation?

## 2. Objectives and Subproblems

**Primary objective (to be pursued later):** design a modeling system that (a) quantifies safe mitigation capacity, (b) projects reduction pathways under alternative policies, (c) selects a global minimum achievable target with a timeline, and (d) formalizes equity impacts.

**Subproblems to be decomposed:**

- **S1 — Waste accounting baseline.** Construct a stock-and-flow description of single-use/disposable plastic across production, use, collection, recycling, incineration, landfill, leakage, and ocean accumulation.
- **S2 — Safe mitigation capacity.** Define and estimate the maximum waste tonnage that can be processed per unit time without net environmental damage, as a function of processing resources and environmental carrying limits.
- **S3 — Reduction pathway and levers.** Model how policy (bans, taxes, EPR, deposit schemes), substitution by alternatives, and behavioral change will reduce inflow and alter composition over time.
- **S4 — Policy effectiveness and regional heterogeneity.** Represent region-specific constraints (income, infrastructure, governance, trade, tourism) that will make equivalent policies more or less effective across regions.
- **S5 — Target and timeline selection.** Formulate an optimization or multi-criteria decision step that will select a global minimum achievable level and a phased timeline.
- **S6 — Impact and equity analysis.** Assess distributional consequences across regions/income groups and formulate ICM-oriented equity recommendations.
- **S7 — Memo synthesis.** Translate modeled outputs into a two-page memo with target, timeline, enablers, and barriers.

**Mapping of deliverables:** S1–S2 will feed the technical model section; S3–S5 will feed the target/timeline results; S4 and S6 will feed the equity discussion; S7 will feed the memo deliverable.

## 3. Assumptions

The following assumptions are *proposed* and will be revisited and validated (or replaced with data-driven alternatives) during implementation.

**A. System boundary and accounting**
- A1. Single-use/disposable plastics will be treated as a distinguishable category and modeled separately from durable plastics.
- A2. Mass will be conserved across the waste chain: inflow (production destined for single-use) = managed flows + leakage, on an annual basis, with explicit stock terms.
- A3. Ocean accumulation will be approximated as a bounded "leakage" compartment rather than a fully resolved ocean-transport model.

**B. Environmental safety definition**
- B1. "Environmentally safe" will be operationalized as a threshold (or set of thresholds) on net environmental load, not as absolute zero.
- B2. A finite maximum safe mitigation rate will be assumed to exist and to be attributable to processing capacity plus ecosystem assimilation limits.
- B3. Delay/lag effects between inflow reduction and burden reduction will be represented explicitly.

**C. Behavioral, economic, and policy**
- C1. Substitution of single-use plastics by alternatives will be modeled with a partial-substitution coefficient and a cost/feasibility penalty rather than perfect replacement.
- C2. Policy effectiveness will be assumed non-uniform across regions and to depend on enforcement strength and infrastructure.
- C3. Consumer behavior will be modeled as responsive to price and availability, with bounded elasticity.

**D. Data and modeling pragmatics**
- D1. Regional aggregation will be settled at a tractable spatial resolution (e.g., income-tier or continent-level) chosen for data availability.
- D2. Where data is missing, expert-elicited or literature-benchmarked priors will be used and flagged for sensitivity testing.
- D3. Time will be discretized into annual steps, with a horizon long enough to capture policy rollout and lag effects.

**Justification and future validation:** each assumption will be tagged to a rationale, then revisited against data. Assumptions whose removal changes target/timeline materially will be flagged as high-impact and subjected to dedicated sensitivity analysis (Section 7).

## 4. Data Processing Plan

Because no dataset was bundled with this run, step D0 will be source discovery.

- **D0 — Source identification.** Future work will catalog candidate data sources: global plastic production statistics, municipal solid waste and marine-litter compilations, recycling-rate series, policy inventories (bans, EPR, deposit systems), plastics-industry economic data, and region-level socioeconomic indicators. Sources will be recorded with vintage, coverage, and licensing metadata.
- **D1 — Ingestion and schema.** Collected data will be normalized into tidy tables keyed by region and year, with consistent units (tons, USD, per-capita where relevant).
- **D2 — Cleaning.** Duplicate resolution, unit harmonization, currency and inflation normalization, reporting-gap handling, and outlier screening will be performed before any modeling.
- **D3 — Missing-data strategy.** Imputation will be chosen per variable (interpolation for time series, ratio/donor methods for cross-sections), with provenance retained; all imputed values will be flagged.
- **D4 — Feature construction.** Planned derived features include: per-capita single-use plastic consumption, waste composition shares, leakage fraction, effective processing capacity, recycling infrastructure index, policy-intensity index, substitution-readiness index, and socioeconomic/equity indicators.
- **D5 — Data usage strategy.** Data will be split conceptually into (i) series for calibration of the flow model, (ii) variables for scenario levers, and (iii) an anonymized hold-out period/region for backtesting. Documented uncertainty ranges will accompany each input so that scenario analysis can propagate them.

## 5. Candidate Model Framework

Candidate models are listed as options to be compared and combined; selection will occur during implementation.

- **M1 — Stock-and-flow / system-dynamics model.** Compartments: production → consumption → waste generation → collection → recycling/incineration/landfill → leakage. Rationale: natural fit for lifetime mismatch and lag. Advantages: interpretable mass balance, easy scenario switching. Limitations: aggregate, sensitive to rate assumptions.
- **M2 — Optimization model (LP/NLP/MILP).** Decision variables: reduction targets, policy intensities, infrastructure investment by region/year. Objective candidates: minimize residual environmental burden subject to cost/welfare constraints, or minimize cost subject to a residual cap. Advantages: yields explicit "minimum achievable" target. Limitations: risk of infeasibility under hard equity constraints; needs careful constraint design.
- **M3 — Multi-criteria decision analysis (MCDA).** For combining environmental, economic, and social objectives with stakeholder weights. Advantages: handles non-commensurable objectives. Limitations: weight sensitivity.
- **M4 — Policy-effectiveness / elasticity models.** Econometric or elasticity-based relationships linking policy levers to consumption reduction. Advantages: empirically grounded. Limitations: data-hungry, cross-region transfer risk.
- **M5 — Projection/forecasting layer.** Time-series or scenario-based forecasting of baseline inflow to compare against policy scenarios. Advantages: provides counterfactual. Limitations: extrapolation uncertainty.
- **M6 — Equity/indicator layer.** Gini-style or burden-share indicators, plus avoided-burden accounting, to quantify distributional outcomes. Advantages: directly supports ICM equity discussion. Limitations: normative weighting choices.
- **M7 — Multi-objective optimization / Pareto analysis.** To expose trade-offs between environmental gain, cost, and equity, and to identify robust target ranges rather than a single point.

**Core variables (conceptual).** Endogenous: annual single-use plastic inflow, waste generated, collected, recycled, safely mitigated, leaked, accumulated burden. Exogenous/lever: policy intensity, substitution rate, infrastructure capacity, population, GDP, cost parameters. The safe-mitigation threshold will be treated as a target-parameter constrained by processing capacity and environmental limits.

**Overall architecture.** M1 will serve as the system backbone; M5 will provide the baseline projection; M4 will parameterize policy effects within M1; M2/M7 will perform target selection on top of M1's dynamics; M3 and M6 will wrap the environmental/economic/equity trade-offs. Model selection will be justified against data availability and transparency requirements.

## 6. Implementation Roadmap

A staged workflow is planned; each stage will have a clear output artifact.

1. **Stage 0 — Scoping and literature/source review.** Output: assumption register, data-source catalog, candidate-model shortlist.
2. **Stage 1 — Data pipeline build.** Output: cleaned, documented datasets and feature tables with provenance.
3. **Stage 2 — Baseline flow model (M1 + M5).** Output: reproducible baseline projection with uncertainty bands.
4. **Stage 3 — Safe-mitigation capacity characterization (S2).** Output: capacity curve/threshold as a function of resources.
5. **Stage 4 — Policy and substitution layer (M4).** Output: region-specific lever-to-reduction mappings.
6. **Stage 5 — Target and timeline optimization (M2 + M7).** Output: candidate global minimum achievable targets and timelines, with Pareto front.
7. **Stage 6 — Equity and impact analysis (M6 + M3).** Output: distributional metrics and ICM-oriented recommendations.
8. **Stage 7 — Synthesis and memo.** Output: summary sheet, two-page memo, and full report consistent with the modeling blueprint.

**Required modules (planned):** data-ingestion/cleaning utilities; flow-model simulator; parameter/uncertainty manager; optimizer wrapper; scenario manager; visualization/reporting module; test harness for reproducibility. Implementation will be version-controlled and configuration-driven so that scenarios and assumptions can be toggled without code changes.

## 7. Validation Strategy

- **V1 — Mass-balance checks.** Flow accounting will be verified for conservation of mass across all compartments and years.
- **V2 — Backtesting.** Model projections will be compared against held-out historical series and against published independent estimates of waste generation, leakage, and recycling.
- **V3 — Cross-source consistency.** Overlapping data sources will be compared, and discrepancies reconciled or documented.
- **V4 — Benchmark scenarios.** Limiting cases will be checked for expected qualitative behavior (e.g., zero-policy baseline vs. maximal-policy scenario).
- **V5 — Sensitivity analysis.** One-at-a-time and global (e.g., Monte Carlo / variance-based) sensitivity will be run on key parameters (substitution rate, processing capacity, policy effectiveness, cost assumptions) to identify which inputs drive the target and timeline.
- **V6 — Robustness of the target.** The recommended target will be re-derived under alternative objective functions and equity weights to test fragility.
- **V7 — Reproducibility and code review.** Deterministic seeds, environment pinning, and internal review will be used to ensure results can be regenerated.

**Evaluation metrics (planned).** Environmental: residual annual burden and cumulative leakage vs. threshold. Economic: total and per-capita mitigation cost. Social/equity: distribution of burden and benefit across regions/income tiers. Model-quality: backtest error, mass-balance residual, and scenario stability.

## 8. Expected Result Interpretation

At completion, the modeling effort is expected to deliver, and the report to interpret:

- A characterized **safe mitigation capacity** (the volume that could be processed without further environmental damage) with its driving resources and limits.
- A set of **reduction pathways** showing how far single-use/disposable waste could realistically be reduced toward that safe level, and which levers matter most.
- A **recommended global minimum achievable target** with an associated **timeline**, expressed with uncertainty ranges and stated under explicit assumptions.
- A **trade-off map** linking environmental gain to cost and equity outcomes, plus enablers and barriers that could accelerate or slow the timeline.
- An **equity narrative** describing uneven causes/effects and concrete ICM-oriented policy suggestions.

Interpretation will remain conditional: each headline number will be presented as a range conditional on the scenario set, and qualitative caveats will accompany quantitative claims.

## 9. Limitations and Improvements

**Anticipated limitations.**
- Aggregation error from region/time bucketing and from treating heterogeneous plastic types as a single category.
- Dependence on quality and availability of external data, especially for leakage, policy enforcement, and recycling infrastructure.
- Uncertainty in the environmental-safety threshold and in behavioral elasticities.
- Optimization results sensitive to objective weighting and to infeasibility risk under strict equity constraints.
- Simplified ocean fate (leakage compartment) rather than a full transport/ecosystem model.

**Planned improvements.**
- Increase spatial and material resolution as data permits (by polymer type, by product class).
- Add endogenous innovation/learning curves for alternatives and recycling technology.
- Incorporate feedback between policy, prices, and behavior (dynamic elasticities).
- Extend the equity layer to include transition-support mechanisms and to test alternative normative weights.
- Strengthen uncertainty quantification and, if warranted, move from point-target optimization to robust/distributionally-robust optimization.
- Validate against additional independent datasets and, where possible, regional case studies.

---

*This document is a planning blueprint only. It contains no computed results, no executed analysis, and no final conclusions; all quantitative claims are deferred to the future implementation and validation stages.*
