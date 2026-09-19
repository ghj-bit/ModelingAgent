# Modeling Blueprint Draft — MM-Bench 2018_C
## Four-State Renewable Energy Compact (CA, AZ, NM, TX)

> **Status: planning artifact only.** This document is a roadmap for future modeling work. It contains no computed results, no fitted models, no executed experiments, and no final conclusions. All quantities, criteria, and targets below are placeholders to be instantiated by the downstream modeling team.

---

## 1. Problem Background and Restatement

Energy production and consumption are central to any state economy, and in the United States much energy policy is set at the state level. Geography, industrial mix, population, and climate differ substantially across states and are therefore expected to shape energy profiles. In 1970, twelve western states formed the Western Interstate Energy Compact (WIEC) to coordinate nuclear energy development.

The task will concern a *new* compact among four states along the U.S.–Mexico border — California (CA), Arizona (AZ), New Mexico (NM), and Texas (TX) — focused on increasing the use of cleaner, renewable energy. The four governors will be the audience and the decision-makers.

The governing data source will be `ProblemCData.xlsx`, staged in the `data` directory:

- Worksheet **`seseds`**: an expected long/tidy table with columns `MSN`, `StateCode`, `Year`, `Data`, covering roughly 50 years across a large set of variables (~605 MSN codes) for the four states, including energy production, consumption, and selected demographic/economic series.
- Worksheet **`msncodes`**: a codebook with columns `MSN`, `Description`, `Unit`, providing the human-readable meaning and units of each MSN.

The requested modeling work will be structured in three parts:

- **Part I — Descriptive and predictive modeling**
  - **A.** Build an *energy profile* for each of the four states from the provided data.
  - **B.** Develop a model characterizing how each state's energy profile evolved from 1960–2009, interpret results in an accessible way for governors, and discuss similarities/differences and possible drivers (geography, industry, population, climate).
  - **C.** Determine which state had the "best" profile for cleaner/renewable energy in 2009, with an explicit, defensible criterion.
  - **D.** Predict each state's energy profile for 2025 and 2050 under a no-policy-change (baseline) assumption.
- **Part II — Prescriptive/decision layer**
  - **A.** Set renewable-energy usage targets for 2025 and 2050 as compact goals, grounded in the comparison, "best" criterion, and baseline projections.
  - **B.** Identify and discuss at least three actions the four states could take to meet the goals.
- **Part III — Communication layer**
  - **C.** Produce a one-page memo to the governors summarizing 2009 profiles, no-policy-change predictions, and recommended compact goals.

The plan below is intentionally method-agnostic until the modeling team confirms data realities (e.g., units per MSN, missingness, series coverage).

---

## 2. Objectives and Subproblems

### 2.1 Primary objective
To design a coherent, reproducible modeling pipeline that (i) characterizes the historical energy profiles of CA, AZ, NM, and TX, (ii) projects them to 2025 and 2050 under no policy change, (iii) defines and applies an explicit "best renewable profile" criterion, and (iv) translates all of this into actionable compact goals and recommendations for the governors.

### 2.2 Subproblem decomposition

| ID | Subproblem | Nature | Planned deliverable |
|----|-----------|--------|---------------------|
| S1 | Data inventory & harmonization | Data engineering | A clean, documented panel keyed by (StateCode, Year, MSN) with units resolved |
| S2 | Energy profile construction | Descriptive / index design | Per-state profile definition and normalized indicators |
| S3 | Evolution modeling (1960–2009) | Time-series / structural | Model of profile dynamics + interpretable driver discussion |
| S4 | "Best" profile determination for 2009 | Multi-criteria evaluation | Explicit criteria set + ranking procedure (method-form only) |
| S5 | Baseline projection to 2025 & 2050 | Forecasting | Scenario forecasts under no-policy-change assumption |
| S6 | Compact target-setting for 2025 & 2050 | Prescriptive optimization / goal-setting | Target framework tied to S4/S5 |
| S7 | Action identification (≥3) | Qualitative + quantitative support | Action list linked to measurable levers |
| S8 | Governor memo | Communication | One-page narrative template populated later |

### 2.3 Deliverables (future)
- A reproducible analysis pipeline scaffold (`code/`) with configuration-driven state/var selection.
- A profile definition and indices specification.
- A baseline forecasting specification with documented assumptions.
- A ranked "best profile" procedure.
- A target-setting framework for 2025/2050.
- A memo template (one page) for Part III.

---

## 3. Assumptions

The following will be treated as working assumptions. Each is stated with rationale and a future validation approach; none is taken as a confirmed fact here.

### 3.1 Data-structure assumptions
1. **Tidy/panel structure.** `seseds` will be long-format with one row per (StateCode, Year, MSN) and a single numeric `Data` value; `msncodes` will be a 1:1 codebook joinable on `MSN`.
   - *Justification:* implied by the dataset definition.
   - *Validation:* confirm uniqueness of (StateCode, Year, MSN); confirm MSNs in `seseds` ⊆ MSNs in `msncodes`.
2. **Units are per-MSN and may differ across rows.** Comparisons will require explicit unit normalization.
   - *Validation:* join `Unit` and audit unit homogeneity before any aggregation.
3. **`StateCode` encodes exactly the four target states**, possibly after mapping codes to CA/AZ/NM/TX.
   - *Validation:* enumerate distinct `StateCode` values; map against a documented lookup.
4. **Time coverage spans the stated window (≈1960–2009)** with possible gaps near endpoints.
   - *Validation:* tabulate year coverage per series.

### 3.2 Domain assumptions (to be challenged during modeling)
5. **"Cleaner, renewable" will be operationalized from MSN descriptions** (e.g., renewable generation/consumption categories), because the term is not directly a single column.
   - *Justification:* the dataset is variable-code based; a mapping is required.
   - *Validation:* build a variable-mapping table and have it reviewed for coverage/omissions.
6. **No-policy-change baseline means continuation of observed structural trends**, not a specific legislative forecast.
   - *Justification:* Part I.D explicitly frames 2025/2050 as "in the absence of any policy changes."
   - *Validation:* state this as an explicit scenario definition; stress-test with alternate extrapolations in sensitivity analysis.
7. **Comparability across states is meaningful after normalization** (per capita, per GDP, or share-based).
   - *Validation:* compare absolute vs. normalized rankings; confirm robust ordering.
8. **Data are assumed internally consistent enough for trend modeling**, pending quality checks.
   - *Validation:* outlier/missingness audit (Section 4).

### 3.3 Modeling assumptions (provisional)
9. Structural breaks (policy, price shocks, recessions) may exist; models will be selected with break-awareness or robustification in mind.
10. Aggregation across heterogeneous MSN units will rely on consistent energy units (e.g., a common thermal/electric basis) or on share-based indicators to avoid summation artifacts.

---

## 4. Data Processing Plan

*Planning only — no transformations are executed in this document.*

### 4.1 Ingestion
- Load both worksheets from `ProblemCData.xlsx` (`seseds`, `msncodes`).
- Preserve raw copies; write all derived tables to `code/` outputs or a `results/`-adjacent working area for provenance.

### 4.2 Structural validation (audit, not analysis)
- Verify column names/types against the documented schema.
- Check key uniqueness: (StateCode, Year, MSN).
- Check referential integrity between `seseds.MSN` and `msncodes.MSN`.
- Profile coverage: rows per state, rows per year, series length distribution.

### 4.3 Cleaning and harmonization
- **Missing data:** classify as structural (series not reported for a year) vs. accidental; choose per-case handling (dropping, interpolation only within a state–series, or explicit NA-aware modeling). Document every choice.
- **Unit harmonization:** attach `Unit` from `msncodes`; define conversion rules to a common basis where summation is required.
- **Outliers / errors:** define objective detection rules (e.g., implausible magnitudes, sign flips, discontinuities); flag rather than silently alter.
- **State naming:** map `StateCode` to CA/AZ/NM/TX with a documented crosswalk.

### 4.4 Feature construction (planned)
- **Raw series:** energy production and consumption by category and fuel where identified via MSN descriptions.
- **Derived shares:** renewable share of total energy/electricity; fossil share; per-capita and per-GDP intensities.
- **Profile features:** a compact vector per (state, year) summarizing supply mix, demand mix, renewables penetration, and intensity.
- **Driver covariates:** population and economic series available in the dataset; geography/climate treated qualitatively unless encoded in available variables.
- **Alignment:** resample/aggregate to a consistent annual frequency; construct a balanced panel where feasible for cross-state modeling.

### 4.5 Data-usage strategy
- **Train/validation split:** hold out the most recent years (e.g., last k years) for backtesting before final no-policy-change projection.
- **Variable selection:** prioritize MSNs explicitly identified as renewable and their denominators; maintain a mapping table linking each indicator to its source MSNs.
- **Documentation:** maintain a data dictionary and a decisions log (assumption → choice → rationale) to support reproducibility and the sensitivity analysis.

---

## 5. Candidate Model Framework

*Method candidates to be compared; no method is selected or fitted here.*

### 5.1 Profile construction (Subproblem S2)
- **Descriptor-based profiling:** a fixed feature vector (renewable share, fuel mix, intensity) per state–year.
- **Composite index approaches:** weighted additive indices or Data Envelopment Analysis (DEA)-style efficiency scores to summarize "renewable-ness."
  - *Advantages:* interpretable, governor-friendly; supports ranking.
  - *Limitations:* weighting is subjective; sensitive to variable set — must be transparent.

### 5.2 Evolution modeling 1960–2009 (Subproblem S3)
- **Univariate/structural time-series:** ARIMA/SARIMA, exponential smoothing, and (if warranted) state-space/Kalman formulations per state–series.
- **Trend/break models:** piecewise-linear or segmented regression to capture policy/price regime shifts.
- **Multivariate/panel models:** fixed/random-effects panel regression across states to separate common vs. state-specific dynamics.
- **Dimension reduction:** PCA/factor methods on the profile vector to characterize shared trajectories.
  - *Advantages:* extracts common structure; good for cross-state comparison.
  - *Limitations:* interpretability of factors; needs careful naming for a governor audience.

### 5.3 "Best" profile criterion (Subproblem S4)
- **Multi-criteria decision analysis (MCDA):** define criteria (renewable share, growth rate, diversity, emissions-proxy, reliability/access) with explicit weights; use AHP/TOPSIS-style ranking as candidates.
- **Performance ratio / benchmark approach:** distance-to-frontier (DEA) as a complementary criterion.
- *Requirement:* criteria must be stated before comparison to avoid post-hoc rationalization; robustness of the winner across weighting schemes will be a key check.

### 5.4 Baseline projection 2025 & 2050 (Subproblem S5)
- **Extrapolation models:** fitted ARIMA/ETS extended to horizons.
- **Trend + scenario models:** regression on drivers with stated driver paths (no-policy-change).
- **Structural/system models (if appropriate):** simple supply–demand or energy-mix transition models (e.g., logistic/S-curve diffusion for renewable share) with documented parameters.
  - *Advantages:* long-horizon interpretability; renewable diffusion often better captured by saturating curves than linear trends.
  - *Limitations:* long-horizon uncertainty is large; must be paired with scenario bands, not point "facts."

### 5.5 Target-setting and actions (Subproblem S6–S7)
- **Gap analysis:** baseline projection vs. aspirational reference (e.g., "best" state trajectory or a stated benchmark), translated into required growth.
- **Goal formulation:** targets expressed as ranges with milestones; possibly an optimization framing (minimize gap subject to feasibility/plausibility constraints).
- **Action mapping:** link each goal to quantifiable levers (e.g., capacity additions, efficiency, cross-state coordination) and to measurable indicators.

### 5.6 Variables (planned conceptual set)
- Outcome: renewable share, renewable capacity/generation (as identifiable), total consumption.
- Denominators/normalizers: population, economic output, total energy.
- Drivers: indicators of industry mix, demographics, and (qualitatively) geography/climate.
- Horizon inputs: driver trajectories under no-policy-change.

---

## 6. Implementation Roadmap

*No code is written or run in this draft; this section defines the build plan.*

### 6.1 Proposed module layout (under `code/`)

| Module | Responsibility |
|--------|----------------|
| `io.py` | Load worksheets, enforce schema, preserve raw copies |
| `validate.py` | Key uniqueness, referential integrity, coverage audit |
| `clean.py` | Missing-data policy, unit harmonization, outlier flags |
| `features.py` | Profile vectors, shares, intensities, driver table |
| `mapping.py` | MSN → renewable/category mapping table (versioned) |
| `models_evolution.py` | Trend/ARIMA/panel/PCA candidates for 1960–2009 |
| `models_forecast.py` | Baseline projection to 2025/2050 with scenario bands |
| `criteria.py` | MCDA/DEA ranking for "best" profile |
| `targets.py` | Gap analysis and target framework |
| `report_assets.py` | Tables/figures *specifications* for later report assembly |
| `config.yaml` | State list, variable sets, horizons, weights, split rules |

### 6.2 Workflow sequence (planned)
1. Lock schema and data dictionary from `msncodes`.
2. Audit and clean; store a versioned cleaned panel.
3. Construct profile features and the renewable-mapping table.
4. Fit and compare evolution models; select via validation metrics.
5. Compute 2009 profile and apply the predefined "best" criterion.
6. Fit baseline forecast models; generate 2025/2050 bands.
7. Perform gap analysis; draft target ranges and action list.
8. Assemble memo template; run sensitivity and robustness checks.
9. Freeze artifacts, document assumptions, and hand off for final reporting.

### 6.3 Tooling and reproducibility
- Deterministic environment (pinned dependencies), seeded stochastic components.
- Config-driven runs; every output traceable to config + commit.
- Logs to `logs/`; intermediate artifacts versioned to avoid silent overwrites.

---

## 7. Validation Strategy

### 7.1 Evaluation metrics (planned)
- **Forecast accuracy:** MAE/RMSE/MAPE on held-out recent years; interval coverage for prediction bands.
- **Model fit/robustness:** information criteria (AIC/BIC), residual diagnostics (autocorrelation, heteroscedasticity, structural breaks).
- **Ranking robustness:** stability of the "best" state across criterion weights and indicator subsets.
- **Consistency:** internal coherence of shares (e.g., shares sum to plausible totals after normalization).

### 7.2 Validation methods
- **Backtesting / rolling-origin** evaluation for time-series models.
- **Cross-validation** for panel/regression models where applicable.
- **Hold-out** of the most recent available years before final projection.
- **Qualitative review** by domain-informed reading of the codebook and cross-checks against known historical events (used as sanity checks, not as data analysis here).

### 7.3 Sensitivity analysis
- Vary criterion weights and indicator sets for the "best" ranking.
- Vary baseline trajectory assumptions (linear vs. saturating vs. break-adjusted) for 2025/2050.
- Vary missing-data handling and unit-conversion choices.
- Vary train/validation split boundaries.
- Report ranges/scenarios rather than single-point claims.

---

## 8. Expected Result Interpretation

*Interpretation guidance only; no results are produced here.*

- **State profiles (Part I.A/B):** expect a structured comparison emphasizing each state's renewable share, trajectory, and structural drivers; interpretation will translate model outputs into plain-language narratives (e.g., "renewables growing but from a low base") that a governor can act on.
- **Driver discussion (Part I.B):** similarities/differences will be linked to geography, industry, population, and climate in a qualitative, evidence-referenced way, clearly separating data-derived statements from contextual reasoning.
- **"Best" profile (Part I.C):** the ranking will be presented together with the criteria and a robustness statement; the winner will be reported as *best under the stated criteria*, not as an absolute truth.
- **Baseline projections (Part I.D):** outputs will be *scenario-dependent* tendencies with uncertainty bands, explicitly conditional on no policy change.
- **Targets and actions (Part II):** recommendations will be framed as goals tied to measured gaps, with actions mapped to levers and indicators.
- **Memo (Part III):** a one-page synthesis will prioritize clarity, headline messages, and decision-relevant framing over methodological detail.

---

## 9. Limitations and Improvements

### 9.1 Anticipated limitations
- **Data quality/coverage:** varying series lengths, missingness, and unit heterogeneity may constrain comparability.
- **Definition ambiguity:** "cleaner, renewable" requires a mapping decision that influences all downstream results.
- **Long horizons:** 2025/2050 projections carry substantial uncertainty; structural breaks and policy shifts are not predictable from history alone.
- **Criterion subjectivity:** "best" depends on chosen weights and indicators.
- **Contextual variables:** geography/climate may not be directly quantifiable from the dataset and may remain qualitative.

### 9.2 Planned improvements / extensions
- Encode multiple renewable definitions and report robustness across them.
- Add probabilistic scenarios (e.g., Monte Carlo over driver paths) instead of deterministic extrapolations.
- Incorporate exogenous context (policy, technology cost curves) as explicitly-labeled overlays in later iterations.
- Benchmark against external reference series where permissible, clearly marked as external.
- Strengthen the decision layer with optimization and trade-off analysis (cost vs. renewable penetration).

---

## Appendix A — Reproducibility Checklist (to be satisfied during modeling)
- [ ] Data dictionary derived from `msncodes` and reviewed.
- [ ] Cleaned panel versioned with a documented decisions log.
- [ ] Model selection justified with validation metrics.
- [ ] "Best" criteria frozen before ranking.
- [ ] Baseline scenario definition written and versioned.
- [ ] Sensitivity analyses executed and reported as ranges.
- [ ] All figures/tables generated from config-driven, seeded, logged runs.

## Appendix B — Open Questions for the Modeling Team
- Which MSNs collectively define "renewable" and how will partial coverage be handled?
- What is the correct unit normalization for cross-fuel aggregation?
- Which recent years are reserved for backtesting?
- What constitutes a defensible "no-policy-change" driver path for population and economy?
- How many and which criteria define "best," and who approves the weights?
