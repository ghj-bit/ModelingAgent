# Adolescent Pregnancy — Modeling Blueprint Draft

**Problem ID:** `2001_Adolescent_Pregnancy`
**Source:** HiMCM 2001
**Document type:** Initial modeling plan draft (roadmap only — not a solution)

> This document is a planning blueprint. It describes *how* a future modeling
> effort could be structured. It deliberately contains no computed results,
> no fitted models, no executed analyses, and no final conclusions.

---

## 1. Problem Background and Restatement

A Department of Health and Environmental Control is concerned about teenage
pregnancy in its region. A 2000 dataset has been assembled that describes, for
each of twelve counties, counts of pregnancies and births stratified by three
adolescent age bands (10–14, 15–17, 18–19). For the two age bands 10–14 and
15–17, additional counts of births to unmarried individuals are available, and
for the 18–19 band an unmarried-birth count is also supplied. Two years of
regional aggregates (1998 and 1999) are also provided, broken down by age band
into pregnancies and births.

The central question raised by the director is whether teenage pregnancy is
"really a problem" in this region. That framing is deliberately open-ended and
must be translated into a set of measurable criteria before any modeling is
attempted. Restated for planning purposes:

- A future analysis will need to **describe** the current adolescent pregnancy
  and birth situation across counties and age bands.
- It will need to **quantify** disparities between counties and between age
  bands, and track whether the situation appears to be improving or worsening
  over the two supplied years.
- It will need to **compare** the region against external benchmarks or
  reference expectations, since "a problem" is a relative judgment.
- It will need to **translate** those measurements into an evidence-based
  judgment and, potentially, into priorities for intervention.

The problem is thus as much a definitional and comparative exercise as it is a
quantitative one. Counts alone will not answer it; the population base against
which those counts occur will matter, and that base is not contained in the
supplied material (see Section 3, Assumptions).

**Deliverable for the future effort:** a defensible, transparent argument that
takes the supplied counts, relates them to appropriate denominators and
benchmarks, and yields a reasoned judgment on whether adolescent pregnancy
constitutes a problem in this region — together with a description of where and
for whom it is most severe.

---

## 2. Objectives and Subproblems

### 2.1 Primary objective

To determine, using the supplied 2000 county-level data and the 1998–1999
regional aggregates, whether adolescent pregnancy is a significant problem in
the region, and to characterize its magnitude, distribution, and trend.

### 2.2 Subproblems

- **SP1 — Data structuring and quality.** Organize the county table and the
  yearly aggregates into a clean, consistent schema; identify missing fields,
  ambiguities, and internal-consistency issues (e.g., whether pregnancies
  should equal or exceed births, and where unmarried counts sit relative to
  total births).
- **SP2 — Descriptive characterization.** Summarize pregnancy and birth
  distribution across counties and age bands; describe concentration,
  dispersion, and the relative weight of the youngest age band.
- **SP3 — Rate construction.** Define and construct meaningful rates using
  candidate denominators (population estimates by age band, or births as a
  share of pregnancies). This subproblem is dependent on external data
  acquisition or on clearly stated proxy choices.
- **SP4 — Comparative benchmarking.** Compare regional levels and county-level
  levels against external reference values (state or national adolescent
  pregnancy/birth rates) to give "problem" an operational meaning.
- **SP5 — Trend assessment.** Use the 1998 and 1999 aggregates to assess
  direction and rough magnitude of change by age band, acknowledging that two
  points constrain the strength of any trend claim.
- **SP6 — Unmarried-birth dimension.** Examine the unmarried-birth counts as a
  secondary dimension (proportion of births to unmarried individuals by age
  band and county) and consider how this affects interpretation.
- **SP7 — Disparity and prioritization.** Identify which counties and age bands
  are relatively most affected, to inform where future intervention planning
  might focus.
- **SP8 — Judgment and communication.** Synthesize SP1–SP7 into a clear,
  defensible answer to the director's question, with explicit uncertainty.

### 2.3 Deliverables (future)

- A structured dataset derived from the supplied table and aggregates.
- A defined set of indicators (counts, rates, ratios) with stated denominators.
- Comparative and trend descriptions grounded in those indicators.
- A ranking or tiering of counties/age bands by severity, with method disclosed.
- A written argument answering whether the situation is a problem, and why.
- A sensitivity summary showing how the judgment would move under alternative
  assumptions.

---

## 3. Assumptions

Assumptions are grouped by type. Each lists a justification and a planned way
to challenge or validate it later.

### 3.1 Structural / data-integrity assumptions

- **A1.** Each row in the county table corresponds to one distinct county, and
  county indices are stable across all columns.
  *Justification:* the table is presented as a 12-row county matrix.
  *Future validation:* check row counts, index uniqueness, and whether any
  column is a subset of another.
- **A2.** The three age bands are mutually exclusive and exhaustive of
  adolescent pregnancy (10–14, 15–17, 18–19), with no overlap.
  *Justification:* standard age-band construction.
  *Future validation:* confirm band boundaries are non-overlapping and that no
  "unknown age" residual is implied.
- **A3.** Births are a subset of pregnancies within each age band (i.e.,
  pregnancies ≥ births), so any recorded violation flags a data issue rather
  than a modeling insight.
  *Justification:* biological/definitional relationship between pregnancy and
  live birth.
  *Future validation:* test this inequality per county/band and document any
  exceptions.
- **A4.** Unmarried-birth counts are a subset of total births in the same
  band, so their ratio should lie in [0, 1].
  *Justification:* categorization logic.
  *Future validation:* bound-check every county/band ratio.

### 3.2 Population / denominator assumptions

- **A5.** County-level adolescent population by age band is **not** supplied and
  will need to be either acquired externally or approximated.
  *Justification:* only event counts appear in the source material.
  *Future validation:* if external denominators are used, cross-check their
  vintage and geography against the 2000 data.
- **A6.** If denominators cannot be obtained, birth-to-pregnancy and
  unmarried-birth ratios will be used as *compositional* indicators, clearly
  labeled as non-population-normalized.
  *Justification:* these ratios are computable from the given data alone.
  *Future validation:* state explicitly that such indicators cannot support
  cross-county population-size comparisons on their own.

### 3.3 Temporal assumptions

- **A7.** The 1998 and 1999 aggregates describe the same region and the same
  age-band definitions as the 2000 county table.
  *Justification:* they are presented together as a regional summary.
  *Future validation:* check that aggregate totals are plausible relative to
  the summed county counts.
- **A8.** Two consecutive years permit a *directional* statement but not a
  statistically robust trend.
  *Justification:* two data points constrain inference.
  *Future validation:* report trend as indicative only, and clearly flag the
  limitation.

### 3.4 Comparative / interpretational assumptions

- **A9.** "A problem" will be operationalized as a set of thresholds or
  benchmarks (e.g., comparison to a reference region, or a stated rate target)
  rather than treated as a self-evident fact.
  *Justification:* the director's question is inherently relative.
  *Future validation:* run the analysis under at least two alternative
  benchmark definitions.

### 3.5 Boundary and behavioral assumptions

- **A10.** Counts reflect reported/recorded events and are subject to reporting
  and definitional artifacts (e.g., pregnancy reporting completeness).
  *Justification:* administrative health data are typically incomplete.
  *Future validation:* discuss direction of likely bias and how it affects the
  judgment.

---

## 4. Data Processing Plan

This section describes intended preprocessing and feature construction. No
processing is performed here; it is a plan for a future stage.

### 4.1 Input inventory

- **County table:** 12 rows; columns covering county id, pregnancies by three
  age bands, births by age band(s), and unmarried births by age band.
- **Yearly aggregates:** 1998 and 1999, each split into pregnancies and births
  for the 10–14, 15–17, and 18–19 bands.

### 4.2 Preprocessing steps (planned)

1. **Schema normalization.** Define canonical column names, dtypes, and units;
   separate identifier columns from measure columns.
2. **Completeness audit.** Flag any empty, truncated, or ambiguous cells; note
   which measures are present only for some age bands.
3. **Consistency checks.**
   - Verify births ≤ pregnancies per band.
   - Verify unmarried births ≤ total births per band.
   - Verify non-negativity and integrality of all counts.
   - Compare the sum of county-level counts against the 2000 context and against
     the supplied yearly aggregates where comparable.
4. **Missing-data policy.** Because the source is count data (not time series),
   imputation is unlikely to be appropriate; the plan is to document gaps and
   analyze complete cases, with sensitivity to any excluded units.
5. **Outlier / anomaly flagging.** Identify counties that are extreme on raw
   counts; treat flags as items to explain, not to silently remove.

### 4.3 Feature construction (planned)

- **Raw measures:** pregnancies and births by band and county.
- **Derived ratios (within-record, no external data):**
  - Birth-to-pregnancy ratio by band.
  - Unmarried share of births by band.
  - Age-band composition of total pregnancies and births.
  - County share of regional pregnancies/births.
- **Derived summary statistics (planned, not computed here):** totals,
  per-county profiles, dispersion measures across counties.
- **External joins (conditional):** adolescent population by county/age band,
  and a benchmark pregnancy/birth rate, if such data are obtained.

### 4.4 Data usage strategy

- **County table:** primary unit for cross-sectional description and disparity
  analysis (SP2, SP4, SP6, SP7).
- **Yearly aggregates:** primary unit for the trend subproblem only (SP5).
- **Cross-use:** treat the aggregates as a consistency reference for the
  county table, not as additional independent observations.
- **Explicit separation:** keep within-data descriptive indicators distinct
  from any externally-normalized rate indicators, so that conclusions can be
  traced to their evidence base.

---

## 5. Candidate Model Framework

The problem is primarily descriptive and comparative, so the candidate methods
are a suite of complementary statistical and multi-criteria tools rather than a
single mechanistic model. Each is listed with its role, key variables, the
underlying mathematical idea, and its advantages and limitations.

### 5.1 Descriptive statistics and distributional profiling

- **Role:** baseline characterization of counts and ratios across counties and
  age bands (SP2).
- **Variables:** county id, age band, pregnancies, births, unmarried births.
- **Idea:** central tendency, dispersion, quantiles, and distributional shape
  of each measure; contingency-style tabulations across band × county.
- **Advantages:** transparent, assumption-light, directly interpretable.
- **Limitations:** descriptive only; sensitive to a few large counties; no
  population normalization.

### 5.2 Rate / standardization models

- **Role:** produce comparable measures across counties and bands (SP3, SP4).
- **Variables:** counts plus denominators; possibly age-standardized rates.
- **Idea:** rate = events / population-at-risk; standardization adjusts for
  differing age structure across counties.
- **Advantages:** corrects for size and composition; widely understood.
- **Limitations:** requires denominators that are not supplied; standardization
  introduces its own reference-population choice.

### 5.3 Comparative benchmarking

- **Role:** give "problem" an operational meaning (SP4, SP8).
- **Idea:** compare regional/county indicators against external reference
  values or against internally defined thresholds/quantiles.
- **Advantages:** converts a vague question into a testable comparison.
- **Limitations:** benchmark choice drives the conclusion; benchmarks may not
  be geographically or temporally matched.

### 5.4 Trend / change analysis

- **Role:** assess direction of movement between 1998 and 1999 (SP5).
- **Idea:** compare band-wise pregnancies and births across the two years;
  consider simple indices of change.
- **Advantages:** directly uses supplied aggregates.
- **Limitations:** only two time points; no ability to separate signal from
  year-to-year noise or to estimate a slope reliably.

### 5.5 Ratio / compositional analysis (unmarried dimension)

- **Role:** incorporate the unmarried-birth dimension (SP6).
- **Idea:** proportion of births to unmarried individuals by band/county, and
  how it co-varies with the youngest age band and with overall levels.
- **Advantages:** uses all supplied columns; adds a social dimension.
- **Limitations:** ratio denominators vary by county; interpretation is
  culturally and contextually sensitive.

### 5.6 Multi-indicator ranking / multi-criteria decision approach

- **Role:** synthesize several indicators into a severity ordering of counties
  and age bands (SP7).
- **Idea:** normalize indicators, apply weights or rank aggregation (ordinal or
  cardinal), and produce a tiering; optionally test weight sensitivity.
- **Advantages:** integrates multiple facets; produces actionable priorities.
- **Limitations:** weighting is subjective; ranking can hide magnitude
  differences; composite scores are sensitive to normalization choices.

### 5.7 Multivariate exploration (candidate, conditional)

- **Role:** explore structure among counties across several measures (SP7).
- **Idea:** dimensionality reduction or clustering of county profiles to detect
  groups of similarly affected counties.
- **Advantages:** reveals patterns not obvious univariately.
- **Limitations:** with only twelve units, clustering is unstable and results
  should be treated as suggestive, not confirmatory.

### 5.8 Uncertainty and sensitivity framing

- **Role:** qualify every judgment (cross-cutting, feeds SP8).
- **Idea:** propagate alternative assumptions (denominators, benchmarks,
  weights, and data-quality choices) through the descriptive and ranking
  methods and observe how conclusions move.
- **Advantages:** makes the robustness of the final judgment explicit.
- **Limitations:** can only span choices the analyst enumerates; does not
  substitute for real data.

### 5.9 Recommendation on model selection (planning stance)

The future effort is expected to proceed primarily with **5.1–5.4**, augmented
by **5.5** and **5.6**, using **5.7** only as exploratory support and **5.8**
throughout. A single complex model is unlikely to be appropriate given the
coarse, two-year, twelve-county dataset.

---

## 6. Implementation Roadmap

No implementation is performed in this draft. The roadmap below sequences the
future work.

### 6.1 Stage plan

1. **Stage 0 — Setup.** Fix the repository structure, define the data schema,
   and record the source material verbatim as the ground truth.
2. **Stage 1 — Data structuring (SP1).** Encode the county table and yearly
   aggregates; run the completeness and consistency checks from Section 4.2.
3. **Stage 2 — Descriptive analysis (SP2).** Produce the profiling of counts
   and ratios; tabulate by band × county.
4. **Stage 3 — Indicator construction (SP3, SP6).** Build the derived ratios;
   separately document any external denominators acquired.
5. **Stage 4 — Benchmarking (SP4).** Assemble reference values and define
   comparison rules.
6. **Stage 5 — Trend (SP5).** Compare 1998 vs 1999 aggregates by band.
7. **Stage 6 — Ranking / synthesis (SP7).** Apply the multi-indicator approach
   with explicit weights and sensitivity.
8. **Stage 7 — Judgment and write-up (SP8).** State whether the situation is a
   problem, under which definitions, and with what confidence.
9. **Stage 8 — Review.** Adversarially test the argument against Section 3
   assumptions and Section 7 sensitivity.

### 6.2 Required modules (conceptual)

- **Ingestion module:** reads and validates the supplied table and aggregates.
- **Validation module:** enforces A1–A4 style consistency rules.
- **Indicator module:** computes counts, ratios, and (if available) rates.
- **Comparison module:** applies benchmarks and thresholds.
- **Trend module:** handles the two-year aggregates.
- **Synthesis module:** rank aggregation and composite scoring.
- **Reporting module:** table/figure generation and narrative assembly.
- **Sensitivity module:** re-runs the pipeline under alternative assumptions.

### 6.3 Dependencies and risks

- **Critical dependency:** denominators and benchmarks (A5, A6). If unavailable,
  the scope narrows to within-data descriptive and compositional claims.
- **Key risk:** over-claiming from two years of aggregates and twelve counties.
- **Key risk:** letting benchmark choice silently determine the answer.
- **Mitigation:** pre-register the primary benchmark and record alternatives;
  label every indicator by its evidence base.

---

## 7. Validation Strategy

Validation here is about **defensibility of the reasoning**, not model fit,
because the task is predominantly descriptive.

### 7.1 Internal consistency checks

- Reproduce all supplied aggregates from the county table where the comparison
  is meaningful, or document why exact reproduction is not expected.
- Enforce the subset inequalities (births ≤ pregnancies; unmarried ≤ births).
- Confirm that ratio-type indicators stay within their valid ranges.

### 7.2 Robustness / sensitivity analyses (planned)

- **Denominator sensitivity:** where rates are used, vary the denominator
  source or vintage and observe the effect on rankings and conclusions.
- **Benchmark sensitivity:** repeat the comparison under at least two reference
  standards and report any conclusion changes.
- **Weighting sensitivity:** for the multi-criteria ranking, test alternative
  weight sets and normalization schemes.
- **Data-quality sensitivity:** re-run after excluding any flagged/anomalous
  counties to see whether the judgment depends on a few units.
- **Inclusion sensitivity:** test how the conclusion changes if the youngest
  band (10–14) is emphasized versus the 15–17 band.

### 7.3 Interpretive validation

- Cross-check the resulting narrative against known public-health context for
  adolescent pregnancy (qualitative triangulation).
- Ensure the final judgment is explicitly conditional on the stated
  assumptions and does not drift beyond what the data support.
- Have the argument reviewed against the alternative interpretations implied in
  Section 5.4 and 5.6.

### 7.4 Evaluation criteria for the future report

- **Traceability:** every claim links to a specific indicator and source.
- **Transparency:** all definitions, denominators, and weights are disclosed.
- **Robustness:** the qualitative conclusion survives reasonable variations in
  assumptions, or its fragility is stated.
- **Clarity:** the answer to "is it a problem?" is unambiguous, with its
  conditions attached.

---

## 8. Expected Result Interpretation

This section describes how future outputs should be read. It does **not**
present results.

- **Counts and totals** will describe scale and where events concentrate, but
  on their own will not settle the "problem" question because they ignore
  population size and age structure.
- **Ratios** (birth-to-pregnancy, unmarried share) will describe composition
  within each age band and county; they are informative about process but are
  not population-normalized rates.
- **Rates** (if denominators are obtained) will be the primary basis for
  comparing counties and for benchmarking; their interpretation will depend on
  the denominator source.
- **Trends** from 1998–1999 will be read as directional indications only, with
  explicit caution about the two-point limitation.
- **Rankings/tiers** will identify relative priority areas, and should be read
  as ordering information conditioned on the chosen weights, not as absolute
  severity scores.
- **Final judgment** should be expressed as a conditional statement: e.g., "the
  situation appears to be (or not be) a problem *if* one adopts benchmark X and
  denominator Y," together with the conditions under which that judgment would
  change.

---

## 9. Limitations and Improvements

### 9.1 Anticipated limitations

- **Missing denominators:** county-level adolescent population by age band is
  not in the supplied data, limiting rate-based comparison.
- **Short time series:** only two years of aggregates constrain trend analysis.
- **Small cross-section:** twelve counties limits the stability of any
  multivariate or clustering approach.
- **Self-reported/administrative data quality:** reporting completeness and
  definitional consistency are assumed but not verifiable from the source.
- **Subjective elements:** benchmark choice and criteria weights influence the
  synthesis and must be disclosed.
- **Band granularity:** three broad age bands may mask within-band variation.

### 9.2 Planned improvements

- Acquire matched adolescent population estimates and a comparable reference
  region to enable genuine rate comparison and age standardization.
- Extend the time series beyond two years to support a real trend analysis.
- Obtain finer age or sub-county resolution if available.
- Expand the indicator set (e.g., repeat pregnancies, outcomes other than live
  birth) if additional data can be sourced.
- Formalize the multi-criteria weights through documented, auditable criteria
  and run structured sensitivity across them.
- Consider a small, explicit uncertainty analysis (ranges or scenario
  analysis) to accompany the final judgment.

### 9.3 Improvement priority (planning stance)

Highest value would come from **obtaining denominators and a benchmark**, since
these convert the analysis from a within-data description into a genuine
comparison. Second would be **extending the time series**. Remaining
improvements refine rather than change the overall judgment.

---

*End of modeling blueprint draft. No analysis, computations, or conclusions
have been produced in this document; all content is forward-looking planning.*
