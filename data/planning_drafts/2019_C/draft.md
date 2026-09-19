# Modeling Blueprint Draft — MM-Bench 2019_C
## Opioid (Synthetic Opioid & Heroin) Incident Spread Across Five U.S. States

> **Status: PLANNING DRAFT (roadmap only).**
> This document is a modeling blueprint. It contains no computed results, no fitted
> parameters, no data analysis outcomes, and no final conclusions. All statements are
> forward-looking descriptions of *how* the problem will be modeled, validated, and reported.

---

## 1. Problem Background and Restatement

The United States faces a sustained public-health crisis driven by both synthetic
(non-synthetic and synthetic) opioids prescribed for pain management and opioids used
recreationally. Federal agencies (CDC, FBI, DEA) and the DEA's National Forensic
Laboratory Information System (NFLIS) track this crisis through forensic drug
identification records. Understanding how opioid incidents spread across geography and
time — and how that spread relates to socio-economic conditions — is intended to
support counter-crisis strategy design.

**Scope of the supplied data (to be used as the sole quantitative input):**

- `MCM_NFLIS_Data.xlsx` — a workbook (including a `Data` sheet) of drug identification
  counts for narcotic analgesics (synthetic opioids) and heroin for **2010–2017**, for
  each county in five states: **Ohio, Kentucky, West Virginia, Virginia, Tennessee**.
  Fields per the problem definition include: `YYYY`, `State`, `COUNTY`, `FIPS_State`,
  `FIPS_County`, `FIPS_Combined`, `SubstanceName`, `DrugReports`,
  `TotalDrugReportsCounty`, `TotalDrugReportsState`.
- Seven ACS 5-Year DP02 socio-economic extracts (2010–2016), each with a data CSV
  (`*_with_ann.csv`), a `.txt` notes file, and a `*_metadata.csv` code sheet. **Note:
  no ACS extract exists for 2017.**

**Restatement of delivered problem requirements:**

- **Part 1 (Descriptive + Predictive Spread Model):** Build a mathematical model that
  describes the spread and characteristics of reported synthetic-opioid and heroin
  incidents within and between the five states and their counties over time; identify
  candidate "origin" locations where opioid use may have started in each state; assess
  what the continuation of identified patterns implies for U.S. government concerns;
  identify the drug-identification threshold levels at which those concerns arise; and
  predict where and when such thresholds are likely to be reached in the future.
- **Part 2 (Socio-economic Association):** Using the ACS data, examine whether levels or
  trends of opioid incidents are associated with available socio-economic variables, and
  if so, extend the Part 1 model to incorporate the important factors.
- **Part 3 (Strategy Design and Testing):** Combine Parts 1–2 to propose a counter-crisis
  strategy, test its effectiveness through the model(s), and identify the significant
  parameter bounds on which success (or failure) depends.
- **Deliverable forms:** a main modeling report plus a **1–2 page memo** to the Chief
  Administrator, DEA/NFLIS Database, summarizing significant insights.

---

## 2. Objectives and Subproblems

**Primary objective:** produce an integrated, defensible modeling framework that
(a) describes and predicts opioid-incident spread, (b) links spread to socio-economic
covariates, and (c) supports quantitative testing of an intervention strategy — all
using only the supplied NFLIS and ACS data.

**Subproblem decomposition (to be resolved sequentially):**

| ID | Subproblem | Intended output (planned, not computed) |
|----|------------|------------------------------------------|
| S0 | Data harmonization: build a county × year × substance panel aligned with county × year socio-economic panel | Unified analysis-ready dataset spec |
| S1 | Describe temporal growth and spatial distribution of incidents | Candidate descriptive/statistical characterization plan |
| S2 | Model within-state and between-state/county spread dynamics | Compartmental / network / spatio-temporal model candidates |
| S3 | Detect candidate origin locations per state | Source-attribution / inverse-flow candidate procedures |
| S4 | Identify threshold levels of concern and forecast where/when reached | Threshold definition + forecasting protocol |
| S5 | Test association of incidents/trends with ACS socio-economic variables | Regression/feature-selection candidate designs |
| S6 | Integrate socio-economic factors into the spread model | Extended model specification plan |
| S7 | Propose and stress-test a counter-strategy | Scenario/intervention protocol and parameter-bound analysis |
| S8 | Synthesize report + 1–2 page DEA memo | Reporting structure and message templates |

**Explicit non-goals for this draft:** no solving, no data analysis, no fitting, no
coding/execution, no plots, no numeric findings, no policy conclusions.

---

## 3. Assumptions

Assumptions are stated with justification and the future validation step that will test each.

**A1. Reported incidents proxy true underlying use.** *Justification:* forensic
identifications are the only signal available; law-enforcement submission behavior and
lab capacity confound this. *Future validation:* sensitivity analysis on reporting-rate
drift; comparison of count-based vs. share-based (normalized) outcomes.

**A2. County location data are correct.** *Justification:* explicitly granted by the
problem statement. *Future validation:* none required beyond documenting the grant;
sensitivity to aggregation at state level retained.

**A3. Classification of substances.** *Justification:* the `SubstanceName` field is
assumed to permit separation of narcotic analgesics (synthetic opioids) from heroin and
"other." *Future validation:* an explicit substance-mapping audit against the file's own
categories prior to modeling.

**A4. Temporal comparability 2010–2017.** *Justification:* annual counts are assumed
comparable across years modulo reporting growth. *Future validation:* control for
year-level effects; detrending; per-capita normalization.

**A5. ACS coverage mismatch.** *Justification:* ACS exists only 2010–2016; 2017 ACS
effects will be handled by forecasting covariates or by restricting socio-economic
modeling windows to 2010–2016. *Future validation:* hold-out year design and explicit
missing-2017 sensitivity.

**A6. Population baseline dependence.** *Justification:* county counts scale with
population; ACS provides population-linked variables suitable for rate construction.
*Future validation:* compare count vs. per-capita results for robustness.

**A7. Well-mixed / flow assumptions for compartmental models.** *Justification:*
needed for tractability of SIR-like S2 models. *Future validation:* compare against
network/graph models that relax mixing; residual diagnostics.

**A8. Behavioral/structural stationarity within calibration windows.**
*Justification:* parameters are assumed stable enough over short windows for estimation.
*Future validation:* time-varying parameter checks; rolling-origin evaluation.

---

## 4. Data Processing Plan

*(Plan only — no preprocessing will be executed in this draft.)*

**4.1 Inventory and integrity checks (planned)**
- Confirm the `Data` sheet and any auxiliary sheets in `MCM_NFLIS_Data.xlsx`.
- Verify presence and column structure of the seven ACS `*_with_ann.csv` files; note
  that row 1 = header names and row 2 = metadata (must be handled on import).
- Cross-check ACS header definitions against each `*_metadata.csv` and `.txt` notes.

**4.2 NFLIS panel construction (planned)**
- Long-format panel keyed on `(FIPS_Combined, YYYY, SubstanceName)`.
- Derive substance groups: synthetic opioids (narcotic analgesics), heroin, and totals.
- Retain `DrugReports`, `TotalDrugReportsCounty`, `TotalDrugReportsState`.
- Build derived outcomes: county-year counts, incident shares of total drug reports,
  per-capita rates (pending population source from ACS).

**4.3 ACS harmonization (planned)**
- Wide-to-long transform across the seven year files.
- Join to the county panel on FIPS and year.
- Handle ACS margin-of-error / annotation columns and metadata row robustly.
- Document variable families relevant to the opioid hypotheses (e.g., economic status,
  education, family/household structure, housing, mobility, health insurance/access,
  veteran status, etc., as their actual codes are confirmed from the code sheets).

**4.4 Feature engineering (planned)**
- Time features: year index, lagged counts, growth ratios, cumulative counts.
- Spatial features: state membership, county adjacency/flows, distance proxies.
- Socio-economic features: levels, ranks, changes since 2010, lagged values.
- Normalization: per-capita and share-based variants to reduce scale artifacts.

**4.5 Data usage strategy (planned)**
- **Temporal split:** early years for calibration/description; later years held out for
  forecasting evaluation.
- **Spatial split (secondary):** propose leave-counties-out or leave-states-out checks
  where feasible to test generality.
- **Leakage control:** strictly avoid using future-year information in feature building.

**4.6 Known risks to be documented**
- Missing/inconsistent county-year records across sources; zero-inflation and sparse
  counties; ACS 2017 absence; identification-vs-prevalence gap; sparse early years.

---

## 5. Candidate Model Framework

The plan is a **layered model stack**: descriptive → dynamical → socio-economic →
intervention, with each layer able to feed the next.

**5.1 Layer D — Descriptive / exploratory characterization (planned candidates)**
- Trend decomposition of incident counts (level, growth, acceleration) by county/state.
- Distribution analysis and concentration measures across counties.
- Cluster analysis of counties by temporal trajectory shape.
- *Role:* motivate structural choices; not a final result.

**5.2 Layer T — Spread dynamics (planned candidates)**
- **Compartmental epidemic models** (e.g., SIR/SEIR-type or "susceptible–initiated–"
  style) at county/state scale, with parameters for initiation/transmission-like growth
  and decay; extended with a spatial coupling term.
- **Reaction–diffusion / spatio-temporal models** to represent geographic spread via
  proximity/flow coupling.
- **Network / graph models** over counties (edges via adjacency, distance, or flow
  proxies) using diffusion or cascade formulations.
- **Time-series models**: ARIMA/SARIMA, panel regressions, and growth-curve (logistic /
  Gompertz) fits per county or per state for forecasting.
- **Multivariate/stochastic variants**: state-space and possibly agent-based sketches to
  represent heterogeneous sub-populations.

**5.3 Layer O — Origin detection (planned candidates)**
- Retrospective "earliest onset / highest early growth" ranking per state.
- Inverse-flow or source-score methods (e.g., influence/graph centrality or
  source-inference analogs) to propose candidate initiation counties.
- Robustness criteria: agreement across methods and across substance types.

**5.4 Layer S — Socio-economic association (planned candidates)**
- Panel regression (fixed/random effects) of incident outcomes on ACS covariates.
- Regularized regression / feature selection to handle many correlated variables.
- Correlation and partial-dependence style analyses of use/trends vs. covariates.
- Spatially-aware models account for geographic autocorrelation.

**5.5 Layer I — Integrated & Intervention (planned candidates)**
- Extend Layer T with significant Layer S factors as covariates/modifiers.
- Scenario/intervention module: reduce initiation or transmission rates, target specific
  counties, allocate effort under budget constraints; compare counterfactual trajectories.
- Parameter-bound analysis to identify the ranges over which an intervention succeeds or
  fails.

**5.6 Variables (planned, to be finalized after inventory)**
- *Endogenous:* incident counts/rates/shares by substance group, growth and acceleration
  metrics, cumulative burden.
- *State variables (dynamic models):* modeled population fractions by stage.
- *Exogenous:* socio-economic covariates from ACS (level, change, lag), temporal and
  spatial structure.
- *Parameters:* growth/transmission-like rates, decay/spillover rates, coupling weights,
  intervention intensity and reach, threshold constants.

**5.7 Advantages / limitations of candidates**
- Compartmental: interpretable and forecastable, but coarse spatial resolution.
- Network/spatio-temporal: captures geography, but data-hungry and sensitive to graph
  construction.
- Time-series/growth curves: simple and testable, but weaker mechanistic explanation.
- Regression/regularized models: strong association detection, but causality-limited.
- Integrated intervention models: decision-relevant, but parameter uncertainty is high.

---

## 6. Implementation Roadmap

*(No code will be written in this draft; this is the planned build order.)*

**Phase 0 — Scoping & data dictionary.** Finalize understanding of NFLIS and ACS fields
from the provided notes/metadata; lock the substance-mapping and county-keying rules.

**Phase 1 — Dataset build.** Implement planned ingestion of the Excel and CSV sources;
produce the unified panel; write data-quality reports.

**Phase 2 — Descriptive layer (Layer D).** Planned exploratory characterization to guide
model choice.

**Phase 3 — Dynamics layer (Layer T).** Implement compartmental, spatio-temporal, and
time-series candidates; establish baseline predictive behavior.

**Phase 4 — Origin detection (Layer O).** Implement candidate origin-scoring methods and
cross-method comparison plan.

**Phase 5 — Socio-economic layer (Layer S).** Implement panel/regularized association
models; produce a ranked, robustness-checked covariate plan.

**Phase 6 — Integration (Layer I).** Build the combined model and the intervention/
scenario engine.

**Phase 7 — Validation pack.** Execute the validation strategy in §7 and assemble
evidence tables.

**Phase 8 — Reporting.** Produce the main report and the 1–2 page DEA/NFLIS memo.

**Required modules (planned):**
1. Data ingestion & harmonization (`MCM_NFLIS_Data.xlsx`, seven ACS folders, readme).
2. Panel/feature construction (rates, lags, spatial joins).
3. Descriptive analytics module.
4. Dynamic/forecasting module (compartmental, network, time-series).
5. Origin-detection module.
6. Socio-economic modeling module.
7. Intervention/scenario simulation module.
8. Validation & sensitivity harness.
9. Reporting/memo generator (tables/figures to be produced only in the solving phase).

---

## 7. Validation Strategy

**7.1 Evaluation metrics (planned)**
- Point-forecast accuracy: MAE, RMSE, MAPE; and their per-capita normalized variants.
- Probabilistic/interval accuracy where stochastic models are used (coverage, interval
  score analogs).
- Classification-style metrics for origin detection (agreement/consistency across methods,
  rank stability).
- Fit diagnostics: residuals, information criteria for nested model comparison,
  pseudo-R² for association models.
- Intervention evaluation: scenario-delta metrics (relative change under treatment vs.
  counterfactual).

**7.2 Validation methods (planned)**
- **Temporal hold-out / rolling-origin backtesting** across 2010–2017 (with awareness of
  the shorter ACS window).
- **Cross-validation** appropriate to panel data; leave-county-out / leave-state-out for
  spatial generality.
- **Model comparison protocol** across Layers D/T (mechanistic vs. statistical) on the
  same splits.
- **Cross-substance consistency:** concurrence on synthetic-opioid vs. heroin conclusions.
- **Data-source validation:** sensitivity to count vs. per-capita vs. share outcomes.

**7.3 Sensitivity & uncertainty analysis (planned)**
- One-at-a-time and simultaneous perturbation of key parameters (growth, coupling,
  intervention intensity/reach, thresholds).
- Robustness to graph construction (adjacency vs. distance vs. flow weights).
- Robustness to reporting-rate assumptions and to missing-2017 ACS handling.
- Identification of "parameter bounds for success/failure" of the proposed strategy
  (Part 3 requirement).
- Documented uncertainty propagation from inputs to forecasts.

---

## 8. Expected Result Interpretation

*This section describes how future results will be read; it reports no findings.*

- **Descriptive/spread outputs** will be interpreted as trajectory characteristics of
  reported incidents, with explicit caveats that they reflect forensic reporting rather
  than true prevalence.
- **Origin-location outputs** will be interpreted as *model-based candidate* initiation
  locations, valid only insofar as methods agree and assumptions (A1–A8) hold.
- **Threshold outputs** will be framed as model-defined alert levels mapped to "concerns
  the U.S. government should have," presented with the corresponding location/time
  windows.
- **Socio-economic outputs** will be interpreted as associations and candidate drivers,
  with causal claims withheld unless identification strategies permit.
- **Intervention outputs** will be interpreted conditionally: strategy effectiveness is
  expected to depend on identifiable parameter bounds, which will be reported explicitly.
- **Forecasts** will be delivered with uncertainty ranges and assumption caveats, and the
  DEA memo will prioritize actionable, defensible statements over precision.

---

## 9. Limitations and Improvements

**Anticipated limitations**
- Reporting/lab-capacity bias makes counts an imperfect proxy for use (A1).
- ACS coverage ends at 2016, limiting socio-economic coverage of the final year (A5).
- County-level aggregation hides within-county heterogeneity; sparse counties are noisy.
- Compartmental/network abstractions simplify real behavioral and supply dynamics.
- Association analyses cannot by themselves establish causation.
- Intervention parameters will carry wide uncertainty, limiting confident prescriptions.

**Planned improvements / extensions**
- Incorporate population- and share-based normalizations to mitigate scale bias.
- Use multi-method triangulation to strengthen origin and driver conclusions.
- Explore hierarchical/Bayesian formulations to quantify uncertainty and pool sparse
  counties.
- Consider hybrid mechanistic–statistical models for forecasting robustness.
- Extend scenario analysis to include budget-constrained allocation logic.
- Document a reproducible data/analysis specification so results can be audited later.

---

*(End of planning draft. No data has been analyzed; no models have been solved; no results are reported.)*
