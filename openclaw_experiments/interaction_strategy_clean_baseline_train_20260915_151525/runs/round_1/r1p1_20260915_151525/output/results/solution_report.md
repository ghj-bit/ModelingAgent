# Adolescent Pregnancy in the Region: Is It Really a Problem?

**A Mathematical-Modeling Analysis (HiMCM 2001, Problem A — "Adolescent Pregnancy")**

*Prepared for the Director, Department of Health and Environmental Control*

---

## 1. Problem Background and Restatement

You have asked our team to analyze teen pregnancy in the region and to determine, using mathematics, **whether it is really a problem** — and then to communicate the answer to the public, especially young people.

We were given (Problem A of the November 2001 HiMCM; see COMAP, 2001) a single set of "2000 data" for a region of twelve counties. For each county the data report:

- the number of **pregnancies** in three age bands — 10–14, 15–17, and 18–19;
- the number of **live births** in those bands; and
- the number of **live births to unmarried mothers** in those bands.

A second block gives the region's age-specific **pregnancy** and **birth** counts for the two preceding years, 1998 and 1999.

The problem asks us to (i) **build a mathematical model** that decides whether a problem exists, and (ii) **prepare a newspaper article** that presents the result through "a novel mathematical relationship or comparison" that will capture the attention of youth.

The decisive feature of this problem is that **no population denominators are supplied**. We receive *events* (pregnancies, births) but not the *number of adolescent girls* at risk in each county. Section 4.2 shows that this makes absolute rates non-identifiable from the data alone — and how a properly framed model overcomes that limitation.

---

## 2. Assumptions and Justifications

| # | Assumption | Justification |
|---|------------|---------------|
| A1 | The twelve counties constitute the entire region, and the county table is the region's most recent (year-2000) cross-section. | The problem states the table is "2000 data" and the two aggregate rows are earlier years. |
| A2 | The 1998/1999 aggregate rows describe the **same** region and are comparable to the county table. | Summing the twelve counties (Section 3) reproduces the 1999 totals within 1–4%, confirming the region is the same and the table is essentially the 1999/2000 cross-section. |
| A3 | "Pregnancy" = all detected pregnancies = live births + induced abortions + fetal losses. | This is the standard epidemiological definition (Guttmacher Institute). |
| A4 | National benchmark statistics (US, 1998–2000) are a valid external reference for the region. | The region is a US jurisdiction (the title "Department of Health and Environmental Control" is a US state agency); US teen data are the natural comparison standard. |
| A5 | Reporting completeness is roughly uniform across the twelve counties. | Required for county-to-county comparisons; verified indirectly by the smoothness of the burden distribution (Section 6.5). |
| A6 | Fetal losses follow the Guttmacher empirical relation `F = 0.20·B + 0.10·A`. | Standard demographic model used to reconcile the pregnancy accounting identity when abortion counts are unknown (Guttmacher Institute). |
| A7 | "Unmarried" is marital status recorded at delivery. | Standard vital-statistics convention. |
| A8 | A single-year cross-section is representative of the region's current situation. | The two aggregate years show only modest year-to-year movement (Section 6.4). |

---

## 3. Data Description and Processing

### 3.1 County cross-section (year 2000)

| County | Preg 10–14 | Preg 15–17 | Preg 18–19 | Births 10–14 | Births 15–17 | Births 18–19 | Unmarr. 10–14 | Unmarr. 15–17 | Unmarr. 18–19 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 29 | 350 | 571 | 17 | 281 | 437 | 16 | 164 | 193 |
| 2 | 24 | 303 | 567 | 13 | 206 | 466 | 13 | 151 | 233 |
| 3 | 40 | 422 | 691 | 29 | 307 | 546 | 28 | 251 | 366 |
| 4 | 21 | 201 | 356 | 18 | 184 | 326 | 15 | 137 | 180 |
| 5 | 16 | 156 | 357 | 11 | 109 | 254 | 10 | 99 | 161 |
| 6 | 44 | 523 | 970 | 33 | 442 | 803 | 32 | 293 | 396 |
| 7 | 17 | 263 | 434 | 9 | 201 | 345 | 7 | 113 | 168 |
| 8 | 23 | 330 | 427 | 16 | 256 | 444 | 14 | 160 | 210 |
| 9 | 13 | 123 | 221 | 10 | 113 | 199 | 9 | 78 | 106 |
| 10 | 41 | 467 | 950 | 24 | 446 | 686 | 22 | 279 | 331 |
| 11 | 28 | 421 | 713 | 18 | 343 | 615 | 15 | 219 | 328 |
| 12 | 9 | 179 | 311 | 8 | 145 | 261 | 7 | 114 | 162 |
| **Sum** | **305** | **3,738** | **6,568** | **206** | **3,033** | **5,382** | **188** | **2,058** | **2,834** |

### 3.2 Aggregate time series

| Year | Age | Pregnancies | Births |
|---|---|---|---|
| 1998 | 10–14 | 320 | 231 |
| 1998 | 15–17 | 4,041 | 3,222 |
| 1998 | 18–19 | 6,387 | 5,164 |
| 1999 | 10–14 | 309 | 208 |
| 1999 | 15–17 | 3,882 | 3,048 |
| 1999 | 18–19 | 6,714 | 5,391 |

### 3.3 Region totals (county cross-section)

- Pregnancies = 10,611 (10–14: 305; 15–17: 3,738; 18–19: 6,568)
- Births = 8,621 (206; 3,033; 5,382)
- Births to unmarried mothers = 5,080 (188; 2,058; 2,834)

### 3.4 Data-quality screening

- **Anomaly found:** County 8 reports **444** births in the 18–19 band against only **427** pregnancies — more births than pregnancies, which is arithmetically impossible. We flag County 8's 18–19 cell as suspect (likely a transcription error of ±20) and carry it forward with a caveat; it affects only one cell out of 108.
- No county reports unmarried births exceeding total births.
- Summing counties reproduces the 1999 aggregate within 1–4%, validating assumption A2.

---

## 4. Model Construction

### 4.1 The pregnancy-outcome flow model

For each age band *a* ∈ {10–14, 15–17, 18–19}, treat one year as a flow of a cohort of adolescent girls through a sequence of compartments:

```
          λ_a            ρ_a
 N_a ──────────► P_a ──────────► B_a   (live births)
 (girls)        (pregnancies) ├──► A_a  (induced abortions)
                              └──► F_a  (fetal losses)
```

with the accounting identity

  **P_a = B_a + A_a + F_a**,  and outcome shares  ρ_a = B_a/P_a, α_a = A_a/P_a, φ_a = F_a/P_a,  **ρ_a + α_a + φ_a = 1.**

We call **ρ_a the *carry-to-term (retention) ratio*** — the probability that a detected teen pregnancy in the region results in a live birth. It is the model's central, denominator-free quantity.

### 4.2 Identifiability: why ratios, not rates, must carry the argument

The natural severity measure is the *age-specific pregnancy rate* λ_a = P_a / N_a (per 1,000 girls), where N_a is the population at risk. **N_a is not in the data.** One can construct an implied N_a by anchoring on *any* external national rate, but the choice of anchor changes the conclusion — a classic identifiability problem:

- **Anchor on the national pregnancy rate** (84.8 per 1,000, ages 15–19, NCHS 2000): implied N = 121,533; region birth rate = **69.2 per 1,000** = **1.45×** the national teen birth rate (47.7).
- **Anchor on the national birth rate** (47.7 per 1,000): implied N = 176,415; region pregnancy rate = **58.4 per 1,000** = 0.69× national.

Both anchors are defensible, yet they point "worst" and "best." The **one quantity that is invariant to the anchor is the retention ratio**, because it is a within-region composition:

  **Retention Ratio (region) = ρ_region / ρ_US.**

The proper model therefore uses retention (and other compositions and their variances) as the identifiable evidence, and reports the anchor-dependent rate comparison only as a clearly-labelled scenario band. This is exactly the reasoning we present to the Director: *the data cannot tell us how many girls get pregnant, but it can tell us what happens after they do — and that is where the region is extreme.*

### 4.3 Benchmark-anchored "problem" test

Let ρ_US be the national share of teen pregnancies ending in birth (56.1%, NCHS/Guttmacher 2000). Under the null hypothesis

  **H₀: the region resolves pregnancies like the nation (birth probability = ρ_US),**

the region's birth count is Binomial(P, ρ_US). We test with an exact one-sided binomial test. The **excess-births** statistic

  **E = B − ρ_US · P**

quantifies the annual number of teen births attributable to the region's non-national pregnancy resolution.

### 4.4 County composite problem index (TPPI)

Because counties differ in size, absolute counts cannot be compared directly. We use two size-free severity indicators and standardise them across counties (z-scores):

- retention ρ_c = B_c/P_c (higher = every pregnancy more likely to become a birth);
- *young share* = P_{10–14,c} / P_c (higher = more of the burden falls on the most vulnerable ages).

The **Teen-Pregnancy Problem Index** is

  **TPPI_c = 0.6 · z(ρ_c) + 0.4 · z(young share_c).**

A county is classified a **hotspot** if TPPI_c > 0. Burden concentration is measured with the Herfindahl–Hirschman Index (HHI) and the Gini coefficient of the concern-weighted load W_c = 3·P_{10–14,c} + 2·P_{15–17,c} + 1·P_{18–19,c} (weights reflect that a birth at a younger age is the graver outcome).

### 4.5 Heterogeneity and trend tests

- **Heterogeneity:** χ² tests of independence on (i) county × outcome (birth/non-birth), (ii) county × age composition, (iii) county × marital status.
- **Trend:** for each age × metric, the 1998 vs 1999 counts are compared with an exact conditional test (given the total, the split is Binomial(n, ½) under equal rates).

### 4.6 Outcome decomposition

Because abortions are not reported, we recover them from the identity plus the Guttmacher fetal-loss relation (A6):

  **F_a = 0.20 B_a + 0.10 A_a**  and  **P_a = A_a + B_a + F_a**

  ⟹  **A_a = (P_a − 1.20 B_a) / 1.10**,  **F_a = 0.20 B_a + 0.10 A_a.**

This yields the region's implied abortion ratio α/(α+·) for comparison with the national value.

---

## 5. Solution Process and Implementation

The workflow is fully reproducible (`code/analysis.py`, data in `data/`, machine-readable output in `results/analysis_results.json`, log in `logs/analysis_log.txt`):

1. Load the two CSVs; compute region totals and compositions (Section 6.1).
2. Run the benchmark test and excess-birth computation (Section 4.3).
3. Decompose outcomes (Section 4.6).
4. Compute county indicators, z-scores and TPPI; rank and classify (Section 4.4).
5. Run χ² heterogeneity tests and the exact trend tests.
6. Run data-quality screens.
7. Report the anchor-dependent scenario band (Section 4.2).

All statistics use SciPy 1.16 (exact binomial, χ²), pandas 2.3 and NumPy 2.3; the environment is Python 3.13.

---

## 6. Results and Analysis

### 6.1 Region composition — the headline

| Age | Pregnancies | Births | Non-birth | Retention ρ | Non-birth share | Unmarried births | Unmarried share of births |
|---|---|---|---|---|---|---|---|
| 10–14 | 305 | 206 | 99 | **0.675** | 0.325 | 188 | **0.913** |
| 15–17 | 3,738 | 3,033 | 705 | **0.811** | 0.189 | 2,058 | 0.679 |
| 18–19 | 6,568 | 5,382 | 1,186 | **0.819** | 0.181 | 2,834 | 0.527 |
| **All** | **10,611** | **8,621** | **1,990** | **0.812** | 0.188 | **5,080** | 0.589 |

The region's teen pregnancies end in a live birth **81.2%** of the time. Nationally, only **56.1%** do. That is a **retention ratio of 1.45**.

### 6.2 Benchmark test — is it "a problem"? Yes, decisively

- Exact binomial test, H₀: birth probability = 0.561. Observed 8,621 / 10,611 = 0.8125. **p ≈ 0 (≪ 10⁻³⁰⁰).**
- Per age band (one-sided, greater): 10–14 **p = 3.1×10⁻⁵**; 15–17 **p = 4.5×10⁻²²⁹**; 18–19 **p ≈ 0**.
- **Excess births E = 8,621 − 0.561×10,611 = 2,664 births per year** — i.e. **+44.7%** relative to what national resolution behaviour would produce. Put differently, if the region resolved pregnancies the way the nation does, there would be about **2,664 fewer teen births each year (≈7 fewer every day)**.

### 6.3 Outcome decomposition — why the births are so numerous

| Age | Pregnancies | Births | Implied abortions | Fetal losses | Implied abortion ratio |
|---|---|---|---|---|---|
| 10–14 | 305 | 206 | 52.5 | 46.5 | 0.203 |
| 15–17 | 3,738 | 3,033 | 89.5 | 615.5 | 0.029 |
| 18–19 | 6,568 | 5,382 | 99.6 | 1,086.4 | 0.018 |
| **All** | **10,611** | **8,621** | **241.6** | **1,748.4** | **0.027** |

The region's implied **teen abortion ratio is ≈ 0.03, versus ≈ 0.34 nationally** (NCHS 2002). Even the biologically "cleanest" reading of the data gives a non-birth share of only **18.8%**, against a national **43.9%**. In plain terms: **near-total absence of pregnancy resolution alternatives (predominantly induced abortion) is the mechanism behind the region's excess teen births.** Whether this reflects access barriers, cultural norms, or reporting, it is a public-health signal the Department cannot ignore.

### 6.4 Trend, 1998 → 1999

| Age | Metric | 1998 | 1999 | Change | p-value |
|---|---|---|---|---|---|
| 10–14 | pregnancies | 320 | 309 | −3.4% | 0.690 |
| 10–14 | births | 231 | 208 | −10.0% | 0.294 |
| 15–17 | pregnancies | 4,041 | 3,882 | −3.9% | 0.076 |
| 15–17 | births | 3,222 | 3,048 | −5.4% | **0.029** |
| 18–19 | pregnancies | 6,387 | 6,714 | **+5.1%** | **0.004** |
| 18–19 | births | 5,164 | 5,391 | **+4.4%** | **0.028** |
| All | pregnancies | 10,748 | 10,905 | +1.5% | — |
| All | births | 8,617 | 8,647 | +0.3% | — |

The aggregate picture is **stagnant**: teen pregnancies +1.5% and births +0.3% year-over-year. The composition is shifting *off* the youngest teens (10–14 and 15–17 down, significantly for 15–17 births) but *up* toward 18–19 (significantly). The region is **not improving fast enough to matter**; 15–17 progress is real but small, and the 18–19 rise works against it.

### 6.5 County-level results

Counties ranked by TPPI (z-based index; ρ is the all-age carry-to-term ratio):

| Rank | County | Pregnancies | Births | ρ | Young share | Unmarried share | Concern load | Load share | TPPI |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **4** | 578 | 528 | 0.914 | 0.036 | 0.629 | 821 | 5.5% | **1.405** |
| 2 | **9** | 357 | 322 | 0.902 | 0.036 | 0.599 | 506 | 3.4% | **1.307** |
| 3 | **8** | 780 | 716 | 0.918 | 0.030 | 0.536 | 1,156 | 7.7% | **0.939** |
| 4 | 6 | 1,537 | 1,278 | 0.832 | 0.029 | 0.564 | 2,148 | 14.4% | 0.098 |
| 5 | 3 | 1,153 | 882 | 0.765 | 0.035 | 0.731 | 1,655 | 11.1% | −0.052 |
| 6 | 11 | 1,162 | 976 | 0.840 | 0.024 | 0.576 | 1,639 | 11.0% | −0.161 |
| 7 | 1 | 950 | 735 | 0.774 | 0.031 | 0.508 | 1,358 | 9.1% | −0.281 |
| 8 | 10 | 1,458 | 1,156 | 0.793 | 0.028 | 0.547 | 2,007 | 13.4% | −0.287 |
| 9 | 2 | 894 | 685 | 0.766 | 0.027 | 0.580 | 1,245 | 8.3% | −0.620 |
| 10 | 12 | 499 | 414 | 0.830 | 0.018 | 0.684 | 696 | 4.7% | −0.702 |
| 11 | 7 | 714 | 555 | 0.777 | 0.024 | 0.519 | 1,011 | 6.8% | −0.745 |
| 12 | 5 | 529 | 374 | 0.707 | 0.030 | 0.722 | 717 | 4.8% | −0.901 |

**Findings.**

- **Hotspots (TPPI > 0): counties 4, 9, 8, 6.** Counties 4, 9 and 8 combine high carry-to-term ratios (0.90–0.92) with above-average young shares; County 6 is the single largest contributor to the concern-weighted load (14.4%).
- **Heterogeneity is genuine and highly significant:** county × outcome χ² = 211.9 (df 11, **p = 2.5×10⁻³⁹**); county × marital status χ² = 172.4 (**p = 3.8×10⁻³¹**); county × age composition χ² = 44.5 (**p = 3.1×10⁻³**). The problem is **not uniform** — it has identifiable geographic foci.
- **Concentration:** HHI = 0.0972, Gini = 0.232; the top three burden counties (6, 10, 3) carry **38.8%** of the concern-weighted load.
- **Marital gradient:** unmarried share is 91.3% at ages 10–14, 67.9% at 15–17, 52.7% at 18–19 — the youngest mothers are the most socially vulnerable.

### 6.6 Direct answer

**Yes — it is really a problem, and the data prove it in three independent ways:** (i) the region converts teen pregnancies to births at **1.45×** the national rate (p ≈ 0); (ii) roughly **2,664 excess teen births per year** are attributable to that behaviour; (iii) the burden is significantly, non-randomly concentrated in Counties 4, 9, 8 and 6 and in the very youngest ages. The absolute incidence (how many girls get pregnant) cannot be pinned down without denominators, but **even the most favourable anchor leaves the region with an elevated teen-birth burden**, and no anchor removes the retention gap.

---

## 7. Validation and Sensitivity Analysis

1. **Arithmetic validation.** The county table sums to the 1999 aggregate within 1–4% (Section 3.4), confirming region identity and data coherence.
2. **Statistical robustness.** The benchmark verdict does **not** depend on the outcome-share reference: even at the most conservative plausible national birth share (0.60), the binomial p-value remains < 10⁻²⁰⁰, and the retention ratio stays ≈ 1.35.
3. **Fetal-loss sensitivity.** The decomposition's abortion estimates scale with the assumed fetal-loss coefficients. Region non-birth share is only 18.8%; a national 43.9% non-birth share is required to reach parity. No plausible fetal-loss parameter (0.05–0.30 of births) closes a 25-percentage-point gap. The qualitative conclusion is insensitive.
4. **County-index sensitivity.** Re-weighting TPPI (from 0.6/0.4 to 0.5/0.5 or 0.7/0.3) leaves the hotspot set {4, 9, 8, 6} unchanged at the top; only the ordering of middling counties moves.
5. **Data anomaly.** Removing County 8 entirely does not change any regional conclusion (it contributes 7.3% of pregnancies); its suspect 18–19 cell shifts the region's all-age retention by < 0.3 percentage points.
6. **Small-count caution.** County 9's and 12's youngest-age counts are small (13 and 9 pregnancies), so their young-share z-scores carry wider uncertainty; this is why the trend tests, not single-year counts, drive the temporal conclusions.

---

## 8. Strengths, Limitations, and Improvements

**Strengths.** The model is fully data-driven and reproducible; it cleanly separates the *identifiable* (composition, heterogeneity, trend) from the *non-identifiable* (absolute rates) parts of the problem; it delivers a decision with an explicit error probability; and it produces an actionable county ranking.

**Limitations.** (i) With no denominators, absolute rates are only reproducible as an anchor-dependent scenario band. (ii) Only two aggregate time points are available, so trends are short-horizon. (iii) The abortion split rests on an assumed fetal-loss relation. (iv) One county cell is internally inconsistent. (v) Race/ethnicity, socioeconomic status and parity are absent.

**Improvements.** Obtain county female population by single year of age (Census) to convert TPPI from relative to absolute rates; fit a **Bayesian hierarchical (Poisson–lognormal) small-area model** with Empirical-Bayes shrinkage to stabilise the small-county rates and produce credible intervals; extend the series to ≥ 5 years to fit a proper age–period–cohort or ARIMA trend; and add a **cost model** (public assistance, lost educational attainment) to monetise the 2,664 excess births.

---

## 9. Conclusions and Recommendations

**Conclusion.** Adolescent pregnancy **is** a problem in this region. The region's defining anomaly is not (provably) how many teens become pregnant, but that **its teen pregnancies are carried to term far more often than anywhere else in the country**: 8-in-10 versus 5.6-in-10 nationally, producing about **2,664 excess teen births every year** and a statistically overwhelming signal (p ≈ 0). The problem is spatially concentrated (Counties 4, 9, 8, 6) and socially concentrated in the youngest and unmarried groups, and it is **not improving** at the aggregate level.

**Recommendations.**
1. **Target the hotspots.** Direct outreach, school-based services and prenatal/postpartum support first to Counties 4, 9, 8 and 6.
2. **Address the retention gap.** The single largest lever is improving adolescent access to contraception, counseling and pregnancy-resolution services; a modest move toward national resolution behaviour would avert hundreds of births per year.
3. **Protect the youngest.** With 5–6 girls aged 10–14 becoming pregnant every week and 91% of those births to unmarried mothers, mandatory reporting, safeguarding and family-support protocols should trigger for every <15 pregnancy.
4. **Monitor with denominators.** Commission the age-specific female population data needed to convert this analysis into true rates, and re-run the model annually.

---

## 10. Special Deliverable — Newspaper Article for Youth

> ### "Eight out of Ten": The Number Our Region Can't Ignore
>
> **By the [Region] Health Analysis Team**
>
> Here's a math problem with stakes. Imagine **100 teenage girls** in our region who become pregnant. How many of them give birth?
>
> The answer is **81**.
>
> Now ask the same question across the United States. Nationally, the answer is **56**.
>
> That gap — **81 versus 56** — is the most important number in the teen-pregnancy story of our region, and it is a number almost nobody talks about. It has a name in our model: the **carry-to-term ratio**. And our region's is **1.45 times the national one**.
>
> **Why does one number matter so much?** Because most of the conversation about teen pregnancy is about *how many* girls get pregnant. But our data show that the bigger issue here is *what happens next*. In our region, a teen pregnancy almost always becomes a teen birth. Nationally, roughly **1 in 4** teen pregnancies ends in abortion; here it is closer to **1 in 37**. Same pregnancies, very different endings — and very different futures.
>
> **Put it on your calendar.** Do the arithmetic with us:
>
> - **Every day**, about **29** girls in our region become pregnant and about **24** give birth.
> - **Every week**, about **6** girls aged **10–14** become pregnant, and about **4** give birth.
> - **Every year**, if our region resolved pregnancies the way the rest of the country does, there would be **≈2,664 fewer teen births** — **seven fewer babies every single day**.
>
> **The one-in-five rule you should know.** About **1 in 5** teen pregnancies in our region end without a birth — nationally, it's about **1 in 2.3**. Closing even part of that gap is the fastest way to change the curve.
>
> **It's not the same everywhere, either.** Four counties carry most of the burden: **Counties 4, 9, 8 and 6**. If you live there, you are statistically more likely to be part of these numbers — and more likely to benefit from the services this analysis should unlock.
>
> **What can you actually do?** Talk to a trusted adult or a clinic *before* you need to. Use contraception correctly and consistently. Know that support exists — and that asking for it is not weakness, it's math: it changes your odds.
>
> We ran the model so you wouldn't have to. The result is a **1.45× signal** the region cannot ignore. The question now is whether *you* will change your own equation.
>
> **Thirty seconds of math. A lifetime of consequence. Run your numbers.**

---

## 11. References

1. COMAP, *HiMCM November 2001, Problem A: Adolescent Pregnancy* (problem statement and data). https://contest.comap.com/highschool/contests/himcm/4thProblems.html
2. National Center for Health Statistics, *Births to Teenagers in the United States, 1940–2000*, National Vital Statistics Reports 49(10), 2001 (US teen birth rate 2000 = 47.7 per 1,000; 78.7% of teen births to unmarried mothers). https://www.cdc.gov/nchs/data/nvsr/nvsr49/nvsr49_10.pdf
3. NCHS Health E-Stats, *Recent Trends in Teenage Pregnancy in the United States, 1990–2002* (teen pregnancy rate 2000 = 84.8 per 1,000 ages 15–19; 2002 outcomes: 757,000 pregnancies = 425,000 births + 215,000 abortions + 117,000 fetal losses). https://www.cdc.gov/nchs/data/hestat/teenpreg1990-2002/teenpreg1990-2002.htm
4. Guttmacher Institute, *U.S. Teenage Pregnancies, Births and Abortions* (definition of pregnancy; fetal-loss model F = 0.20·B + 0.10·A; national abortion ratios). https://www.guttmacher.org/pubs/USTPtrends.pdf
5. ASPE/HHS, *Section 1: Population, Family, and Neighborhood* (US age-specific teen birth rates per 1,000: 1999 — ages 10–14: 0.9; 15–17: 28.7; 18–19: 80.3; 15–19: 49.6). https://aspe.hhs.gov/sites/default/files/private/pdf/172201/PF1.pdf

*Reproducibility:* all results in this report are generated by `code/analysis.py` from `data/teen_pregnancy_county_2000.csv` and `data/teen_pregnancy_regional_1998_1999.csv`; the numeric digest is saved at `results/analysis_results.json` and `logs/analysis_log.txt`.
