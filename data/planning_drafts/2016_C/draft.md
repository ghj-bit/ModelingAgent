# Modeling Blueprint Draft — MM-Bench 2016_C

**Problem ID:** `2016_C`
**Title:** Goodgrant Foundation — Optimal Philanthropic Investment Strategy for U.S. Undergraduate Education
**Document type:** Initial modeling plan draft (roadmap only — no solving, no data analysis, no results)
**Status:** Draft for review before any execution

---

## 1. Problem Background and Restatement

The Goodgrant Foundation intends to commit **$100,000,000 per year for five years starting July 2016** to a selected group of U.S. post-secondary institutions, with the goal of improving undergraduate educational performance. The Foundation explicitly does **not** want to duplicate the investment focus of other large grantmakers (e.g., the Gates Foundation, the Lumina Foundation). The team must design a model that determines:

- **Which** schools to fund (an optimized, prioritized candidate list of size **1 to N**);
- **How much** to invest per school;
- **What return** the investment is expected to produce;
- **How long** funding should be provided per school.

The recommended list should be grounded in each candidate school's **demonstrated potential for effective use of private funding**, and each school should carry an **estimated Return on Investment (ROI)** defined in a manner appropriate for a charitable foundation rather than a purely financial investor.

**Available data (three staged workbooks):**

1. `Problem C - IPEDS UID for Potential Candidate Schools.xlsx` — sheet `IPEDS UID for Schools`, 2,978 rows × 4 columns. Institution identifiers and location: `UNITID`, `INSTNM`, `CITY`, `STABBR`. This defines the **candidate universe**.
2. `Problem C - Most Recent Cohorts Data (Scorecard Elements).xlsx` — sheet `Most+Recent+Cohorts+(Scorecard+`, 7,805 rows × 122 columns. College Scorecard institutional performance and cohort data, keyed on `UNITID` (with `OPEID`, `opeid6`, name, city, state, URL, degree type, control, locale, special-mission flags, admissions test scores, field-of-study shares `PCIP*`, enrollment/`UGDS*` composition, net price `NPT4*`, `PCTPELL`, `PCTFLOAN`, retention `RET_*`, and outcome/loan/earnings fields). Note that many cells carry `'NULL'` sentinels as text.
3. `Problem C - CollegeScorecardDataDictionary-09-08-2015.xlsx` — sheet `CollegeScorecardDataDictionary-`, 1,954 rows × 9 columns. Variable metadata: `NAME OF DATA ELEMENT`, `dev-category`, `developer-friendly name`, `API data type`, `VARIABLE NAME`, `VALUE`, `LABEL`, `SOURCE`, `NOTES`. This is the **codebook** and is expected to contain missing values.

Additionally, the problem statement references `IPEDS Variables for Data Selection.pdf`, which describes the IPEDS selection logic and is expected to interpret/annotate the candidate-universe construction.

**Outcome-level deliverable set:** an investment model + prioritized school list + ROI concept, culminating in a report and a ≤2-page letter to the CFO (Mr. Alpha Chiang) describing the strategy, modeling approach, major results, and the proposed ROI concept.

---

## 2. Objectives and Subproblems

**Primary objective:** Produce a defensible, optimized, and prioritized funding allocation over a 1-to-N list of schools that maximizes the likelihood of a strong positive effect on undergraduate student performance, subject to a $100M/year × 5-year budget and a non-duplication constraint relative to peer foundations.

**Decomposed subproblems (will be planned, then modeled, then solved):**

- **SP1 — Candidate universe construction.** Define and justify the eligible school set from the IPEDS candidate list and reconcile it against the Scorecard cohorts file (join keys `UNITID`).
- **SP2 — Effect/performance measurement.** Define the "student performance" target constructs to be improved (e.g., completion, retention, post-graduation earnings, repayment, debt burden) using Scorecard outcomes, and specify how they map to measurable indicators.
- **SP3 — Funding-response ("potential for effective use") modeling.** Build a defensible proxy for a school's capacity to convert private funding into performance gains (need + readiness + marginal-return potential).
- **SP4 — ROI definition for a charitable organization.** Formalize a non-profit ROI concept (social/educational return per dollar) that a foundation can defend and reuse in future years.
- **SP5 — Portfolio optimization.** Select the school subset and allocate annual dollars and funding duration to maximize aggregate expected ROI under budget and diversification/equity constraints.
- **SP6 — Prioritization and rank ordering.** Produce the final 1-to-N ranked candidate list with per-school allocation, duration, and expected return.
- **SP7 — Communication artifacts.** Plan the report structure and the CFO letter (strategy, method, results, ROI concept).
- **Cross-cutting — Non-duplication.** Encode a constraint or penalty reflecting overlap with Gates/Lumina-type focus areas so recommendations complement rather than duplicate peer efforts.

**Deliverables (planned):** a ranked investment portfolio; per-school recommended amount and duration; an estimated ROI per school and in aggregate; a documented ROI framework for future years; sensitivity/robustness evidence; the MCM report and the CFO letter.

---

## 3. Assumptions

Each assumption is stated with a justification and a future validation route. These are planning hypotheses to be tested, not verified facts.

- **A1 — Candidate universe is authoritative.** The IPEDS UID workbook defines the eligible pool. *Justification:* the problem frames it as "Potential Candidate Schools." *Validation (future):* reconcile counts and identifiers against the cohorts file; inspect the IPEDS PDF selection logic.
- **A2 — Scorecard outcomes are valid proxies for "student performance."** Completion/retention/earnings/repayment indicators stand in for educational performance. *Justification:* the problem directs the model to use these datasets. *Validation:* cross-check indicator definitions in the data dictionary; test construct consistency across years/cohorts where available.
- **A3 — Cross-sectional stationarity within the funding horizon.** Indicators observed in the most recent cohorts will reasonably proxy near-term conditions. *Justification:* the task provides a single "most recent cohorts" snapshot. *Validation:* where the dictionary/source permits, compare against any historical fields; treat as a sensitivity axis.
- **A4 — Funding has a monotone, diminishing-marginal effect proxy.** More funding per school is expected to yield non-decreasing but concave expected benefit. *Justification:* standard diminishing-returns logic in resource allocation. *Validation:* sensitivity-test alternative response shapes (linear, saturating, threshold).
- **A5 — "Potential for effective use" is inferable from observable characteristics.** Need (e.g., Pell/loan shares, net price, enrollment), capacity (retention, resources), and outcome gaps jointly indicate effective-use potential. *Justification:* these are the observable levers in the data. *Validation:* feature-importance and rank-stability checks.
- **A6 — Missingness/`NULL` sentinels are non-informative or predictable.** Missing values will be handled by documented rules rather than treated as true zeros. *Justification:* the raw file uses `'NULL'` text sentinels. *Validation:* missingness-pattern review and imputation-sensitivity checks.
- **A7 — Non-duplication is representable as a constraint/penalty.** Peer-foundation focus (e.g., large research institutions, community-college reform, specific missions) can be approximated via control type, degree type, and mission flags. *Justification:* available categorical fields (`CONTROL`, `PREDDEG`, `HBCU`, `HSI`, `TRIBAAL`, etc.). *Validation:* scenario tests over alternative overlap definitions.
- **A8 — Budget is committed annually and may be re-evaluated per year.** The model will plan a 5-year schedule but allow annual re-planning. *Justification:* the statement says "per year, for five years." *Validation:* multi-year vs. single-year allocation comparison in the roadmap.
- **A9 — ROI is measurable on a normalized, comparable scale across heterogeneous schools.** A common ROI scale will be constructed. *Justification:* enables ranking across a diverse pool. *Validation:* normalization robustness and rank correlation under alternate scales.

---

## 4. Data Processing Plan

*(Plan only — no preprocessing will be executed in this draft.)*

**4.1 Ingestion and schema reconciliation**
- Load all three workbooks; catalog sheets, column names, dtypes, and row counts.
- Build a **variable dictionary from the codebook** mapping `VARIABLE NAME` → meaning, category, source, and notes; use it to select a **meaningful, defendable subset** of columns rather than all 122.
- Normalize the `'NULL'` text sentinels to true missing values across all files.
- Confirm identifier consistency: `UNITID` is the primary key; `OPEID`/`opeid6` are secondary.

**4.2 Candidate universe alignment**
- Start from the IPEDS candidate list (`UNITID`, `INSTNM`, `CITY`, `STABBR`).
- Inner-join with the cohorts file on `UNITID`; flag schools present in one file but not the other.
- Document and justify any exclusions (e.g., non-degree-granting, closed, non-operating institutions via `CURROPER`).

**4.3 Missing-data strategy (planned)**
- Quantify missingness per field; classify fields as usable / partial / unusable.
- For partial fields, plan documented imputation (e.g., within-group medians by `CONTROL`/`PREDDEG`) with missingness indicators.
- Define a maximum-tolerated-missingness threshold per selected feature.

**4.4 Feature construction (planned groups)**
- **Need / access indicators:** `PCTPELL`, `PCTFLOAN`, net price (`NPT4_PUB`/`NPT4_PRIV`), enrollment `UGDS`, demographic mix `UGDS_*`.
- **Capacity / quality signals:** retention `RET_FT4`/`RET_PT4`, admissions selectivity (`SAT_AVG`, `ACT*MID`), degree mix (`PCIP*`).
- **Outcome indicators (performance targets):** `C150_4_POOLED_SUPP` (4-yr completion), `C200_L4_POOLED_SUPP`, `md_earn_wne_p10` (earnings), `gt_25k_p6`, `RPY_3YR_RT_SUPP` (repayment), `GRAD_DEBT_MDN10YR_SUPP` (debt burden).
- **Institutional context:** `CONTROL`, `PREDDEG`, `LOCALE`, and special-mission flags for segmentation and non-duplication logic.
- **Derived composites (planned):** need index, capacity index, outcome-gap index, and an "effective-use potential" score; definitions to be fixed before modeling.

**4.5 Transformations and normalization**
- Winsorize/robust-scale continuous fields; standardize for distance/gradient-based methods.
- Keep the raw-value option for interpretable, dollar-denominated outputs.
- Decide per-feature treatment (raw, log, rank) and record rationale.

**4.6 Data usage strategy**
- **Training/estimation set vs. holdout:** reserve a subset for out-of-sample robustness checks of the scoring/ranking logic.
- **Time framing:** treat the snapshot as the baseline period; plan a documented multi-year view where fields allow.
- **Auditability:** maintain a lineage from raw column → selected feature → model input, to satisfy "meaningful and defendable subset."

---

## 5. Candidate Model Framework

*(Candidate methods to be compared — none will be fit in this draft.)*

**5.1 "Performance" target definition (SP2)**
- Option A: a composite **Student Performance Index (SPI)** combining completion, retention, earnings, repayment, and debt with defensible weights.
- Option B: multi-output outcome vector with no forced aggregation, ranked via multi-criteria methods.
- Trade-off: Option A gives a single tractable ROI scale; Option B preserves nuance but complicates ranking.

**5.2 Effective-use potential (SP3)**
- Candidate approaches: weighted additive scoring (AHP/entropy weights), TOPSIS/DEA-style efficiency frontiers, or a supervised model if a suitable target proxy exists.
- DEA is attractive for "effective use" framing (need-adjusted output efficiency); TOPSIS is attractive for transparent multi-criteria ranking.

**5.3 ROI definition for a charitable foundation (SP4)**
- Candidate forms: educational ROI = expected improvement in outcome per dollar; social ROI = weighted outcome gain × beneficiary reach per dollar; cost-effectiveness framing = dollars per unit of expected improvement.
- Plan to present ROI as a normalized, interpretable quantity with units stated explicitly and a stated discount/horizon convention.

**5.4 Portfolio optimization (SP5–SP6)**
- Candidate formulations:
  - **Knapsack / integer allocation** — discrete school selection with continuous or tiered dollar amounts under the annual budget.
  - **Convex/concave resource allocation** — maximize aggregate expected benefit under a concave funding-response function.
  - **Risk-aware portfolio** — mean–variance or CVaR-style penalty over uncertain ROI to limit concentration.
  - **Multi-objective optimization** — maximize total ROI while satisfying equity/diversification and non-duplication objectives (Pareto frontier).
- Decision variables (planned): binary selection \(x_i\); annual allocation \(a_i\) or tier \(t_i\); duration \(d_i\); subject to \(\sum_i a_i \le \$100\text{M}\) per year and multi-year smoothing constraints.

**5.5 Non-duplication (cross-cutting)**
- Encode as hard constraints (exclude overlap segments) or soft penalties (down-weight schools in peer-foundation priority areas).

**5.6 Advantages / limitations summary (to be completed at selection time)**
- Linear scoring: transparent, fast; limited nonlinearity.
- DEA/TOPSIS: interpretable efficiency/ranking; sensitive to input/output selection.
- Optimization (LP/MILP/convex): optimal within model; depends on response-function assumptions.
- ML surrogate: flexible; risks opacity and needs a credible label.

---

## 6. Implementation Roadmap

*(Planned modules and sequence — no code will be written in this draft.)*

- **M0 — Setup & data audit.** Inventory files, sheets, schema, missingness; build the codebook-driven variable selection shortlist.
- **M1 — Preprocessing pipeline.** Sentinal handling, universe alignment, imputation rules, feature construction, normalization; produce an auditable analysis table.
- **M2 — Indicator & composite construction.** Finalize SPI and effective-use-potential definitions with documented weights.
- **M3 — ROI formulation.** Implement the chosen charitable-ROI definition and its normalization/horizon conventions.
- **M4 — Impact/response model.** Implement the planned funding-response assumption (concave/saturating) and estimate first-order expected returns.
- **M5 — Portfolio optimizer.** Implement selection + allocation + duration under budget, diversification, and non-duplication constraints.
- **M6 — Prioritization output.** Generate the 1-to-N ranked list with per-school amount, duration, expected ROI, and rationale tags.
- **M7 — Sensitivity & robustness suite.** Run scenario and parameter sweeps (see Section 7).
- **M8 — Reporting.** Assemble the MCM report and the ≤2-page CFO letter.

**Suggested toolchain (planning-level):** Python with spreadsheet I/O and data libraries for M1–M2; optimization libraries for equality/inequality-constrained LP/MILP or convex solvers in M5; a plotting layer for later figures (not produced now). Modular design so each stage has a saved intermediate artifact for reproducibility.

**Dependencies & sequencing:** M1 → M2 → M3 → M4 → M5 → M6, with M7 after M6 and feeding back into M3/M4 assumptions; M8 last.

---

## 7. Validation Strategy

**7.1 Conceptual / model validation**
- Confirm each selected variable is defined in the codebook and justifiably tied to "student performance" or "effective use."
- Verify the ROI definition is coherent for a charity (stated units, horizon, and interpretation).

**7.2 Data validation**
- Reconcile join coverage between candidate universe and cohorts file; document unmatched rows.
- Compare alternative missing-data treatments for impact on rankings.
- Stress-test feature scaling choices (raw vs. standardized vs. rank).

**7.3 Model validation**
- **Out-of-sample checks:** hold out a subset of schools for score/rank stability.
- **Rank stability:** Spearman/Kendall correlation of prioritized lists across method variants (e.g., TOPSIS vs. DEA vs. weighted sum).
- **Constraint feasibility:** confirm budget, duration, and non-duplication constraints are satisfied and binding constraints are identified.

**7.4 Sensitivity analysis (planned axes)**
- ROI definition and weights of the composite indices.
- Funding-response curvature (linear/saturating/threshold).
- Budget split assumptions and duration caps.
- Non-duplication penalty strength and overlap definitions.
- Missing-data imputation and outlier handling.

**7.5 Evaluation metrics (planned)**
- Portfolio-level: aggregate expected ROI, outcome-gain per dollar, coverage/breadth, concentration (e.g., HHI), and equity/geographic balance.
- Rank-level: stability correlations and top-N overlap across scenarios.
- Robustness: fraction of the recommended list persisting across plausible parameter regimes.

**7.6 Scenario / stress testing**
- Extreme-budget and reduced-budget scenarios; single-year vs. five-year rollouts; alternative peer-foundation overlap regimes.

---

## 8. Expected Result Interpretation

*(What the future outputs will mean and how they should be read — no values are produced here.)*

- **Prioritized list:** the top of the 1-to-N list should be read as schools combining high effective-use potential with high expected charitable ROI under the stated constraints; the tail should shrink in confidence.
- **Allocation bands:** per-school funding amounts and durations should be interpreted as *recommended ranges/tiers*, reflecting model and data uncertainty rather than exact point prescriptions.
- **ROI concept:** the reported ROI should be understood as an expected, normalized educational/social return per dollar over the funding horizon, comparable across schools but dependent on the documented definition.
- **Non-duplication:** recommended schools should be describable as complementary to peer-foundation portfolios, with the rationale traceable to categorical segmentation.
- **Actionable framing for the CFO letter:** the strategy should translate the ranked portfolio and ROI concept into a plain-language narrative: where to invest, how much, for how long, why, and how returns will be assessed in 2016 and beyond.

---

## 9. Limitations and Improvements

**Planned/anticipated limitations**
- Single-snapshot data may not capture dynamic or causal funding effects; associations are not causal.
- The funding-response function is assumed, not observed; results will be assumption-sensitive.
- Scorecard coverage gaps and heavy missingness may bias certain segments.
- Charitable ROI inherently resists full quantification; the chosen proxy will simplify social value.
- Non-duplication is approximated from available categorical fields, not actual grantee data.
- Composite weighting choices can materially shift rankings.

**Planned improvements / next steps**
- Incorporate multi-year data if obtainable to test temporal stability and better estimate response.
- Augment with external peer-foundation grantee data to sharpen the non-duplication constraint.
- Add causal-inference or quasi-experimental designs to move from association to effect estimation.
- Extend to a dynamic, multi-year stochastic optimization with annual re-planning and uncertainty on returns.
- Provide an interactive prioritization view for the Foundation to adjust weights and constraints.

---

*End of draft. This document is a modeling blueprint only: it contains no computed results, no data analysis, and no final conclusions. All modeling, computation, and reporting steps listed here are planned future work.*
