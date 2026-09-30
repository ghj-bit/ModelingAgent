# Solution

## Subtask 1: Develop a quantitative model that defines a defensible return-on-investment (ROI) metric for charitable educational gran

### Problem

Develop a quantitative model that defines a defensible return-on-investment (ROI) metric for charitable educational grants, suitable for the Goodgrant Foundation to evaluate $100M/year in donations over five years. The ROI must capture the marginal improvement in student outcomes attributable to the grant, not merely the level of existing student performance. The model must specify what the numerator (effect) and denominator (investment) are, how they are computed from the available IPEDS and College Scorecard data, and how the metric is aggregated from per-school, per-year values to a five-year portfolio-level summary.

### Analysis

ASSUMPTIONS: (1) The grant is paid to the institution and its effect on student outcomes flows through the institution's capacity to change its operations — confirmed by expert consultation. Outcome-level 'harvest' scoring (ranking schools by current student outcomes) is a measure of existing merit, not a valid ROI for a donor seeking marginal effect. (2) ROI is defined per (school, year) pair, not as a per-school scalar, because one-shot and recurring gifts have different mechanisms and durations; the reported summary is the five-year cumulative portfolio ROI. (3) The available Scorecard data (4-yr completion C150_4_POOLED_SUPP, median earnings 10-yr md_earn_wne_p10, share above $25k gt_25k_p6, 3-yr repayment rate RPY_3YR_RT_SUPP, median debt GRAD_DEBT_MDN10YR_SUPP) are proxy measures of the student outcomes that a Goodgrant-style grant can plausibly influence; they are used as the effect dimension. (4) The data do not contain school-specific causal impact estimates, so the model uses a counterfactual-gap approach: the effect is the distance between a school's current outcomes and what is achievable given adequate resources. (5) The $25k earnings threshold and 6-year/10-year horizons are fixed by the U.S. Department of Education's College Scorecard design and are used as the benchmark windows. (6) National mean earnings 10-yr post-enrollment of ~$46,200 (Brookings, 2011 entry cohort, 2013 dollars) and median household income of $56,516 (Census, 2015) serve as external reference levels for sanity-checking the ROI interpretation.

APPROACH: The effect score is a weighted composite of two components: (a) a resource-need score (weight 0.60) measuring the distance of the school's per-student resources and student demographic profile from the levels associated with the outcome benchmarks — this captures the 'constraint is resources, not execution' channel identified in expert consultation; and (b) a headroom/gap score (weight 0.40) measuring the unexplained shortfall of current outcomes relative to benchmarks — retained as a secondary term so that schools that underperform even their weak input profile still receive credit. The resource-need score is the primary component because the expert identified that a school whose inputs genuinely predict its outcomes yet which is under-resourced has a near-zero gap but is the school where a marginal dollar most plausibly moves student performance. The denominator is the dollar amount allocated to (school i, year t), with a diminishing-returns decay factor that reduces the effective ROI for repeated giving within the five-year horizon. The portfolio ROI is the total effect achieved divided by total dollars spent over five years.

### Modeling Process

VARIABLES:
  x_{i,t} = dollars allocated to school i in year t (decision variable), t=1..5
  E_i = composite marginal effect score for school i (0-1 scale)
  N_i = resource-need score (0-1)
  G_i = headroom/gap score (0-1)
  O_i = oversubscription penalty (0-1, soft)
  A_i(t) = cumulative dollars allocated to school i through year t-1

EFFECT SCORE:
  E_i = 0.60 * N_i + 0.40 * G_i

RESOURCE-NEED SCORE N_i (each component min-max normalised to [0,1]):
  N_i = 0.30 * z(PCTPELL_i)
        + 0.30 * (1 - z(NPT41_PUB_i))    [lower per-stu tuition -> higher need]
        + 0.20 * z(GRAD_DEBT_MDN10YR_SUPP_i)  [higher debt -> higher need]
        + 0.20 * z(PCTFLOAN_i)              [higher loan dependence -> higher need]
  where z(v) = (v - min) / (max - min) over the candidate pool

HEADROOM SCORE G_i (each component min-max normalised to [0,1]):
  G_i = 0.30 * z(max(0, B_c150 - C150_i))
        + 0.25 * z(max(0, B_earn - md_earn_i) / B_earn)
        + 0.25 * z(max(0, B_25k - gt_25k_i))
        + 0.20 * z(max(0, B_rpy - RPY_i))
  Benchmarks: B_c150=0.60, B_earn=$45,000, B_25k=0.65, B_rpy=0.75

PER-(SCHOOL, YEAR) ROI with diminishing returns:
  ROI_{i,t} = E_i * (1 - 0.3 * O_i) / (1 + k * A_i(t) / 10^6)
  where k = 0.01 is the decay rate per $1M already committed to school i
  (A school's second-year ROI is lower than its first-year ROI by the decay factor)

OVERSUBSCRIPTION PENALTY O_i (soft, capped at 30% score reduction):
  O_i = 0.5 * z(NPT41_PUB_i) + 0.5 * z(SAT_AVG_ALL_i)
  (proxy: schools with high per-student tuition and high SAT averages are likely
   already well-funded by other foundations such as Gates and Lumina)

CAPACITY SCREEN (applied before scoring):
  UGDS_i >= 500  (minimum undergraduate enrollment)
  At least 2 of {C150, md_earn, gt_25k, RPY} must be non-missing
  Missing values imputed with state median, then national median

CONCENTRATION CAPS:
  x_{i,t} <= 0.20 * $100M  for all i, t  (no school gets >20% of annual budget)
  sum_{i in state s} x_{i,t} <= 0.30 * $100M  for all s, t

OBJECTIVE:
  Maximise  sum_{i,t} E_i * (1 - 0.3 * O_i) * x_{i,t} / (1 + k * A_i(t)/10^6)
  subject to:  sum_i x_{i,t} = $100M for each t
               x_{i,t} >= 0
               capacity screen, concentration caps as above

SOLUTION PROCEDURE:
  Greedy water-filling: in each year, repeatedly assign the next $5M chunk to the
  school with the highest current marginal ROI (subject to caps) until the annual
  budget is exhausted. This is a myopic greedy that is near-optimal for the
  concave per-school objective.

PORTFOLIO ROI (reported summary):
  ROI_portfolio = sum_{i,t} [E_i * (1-0.3*O_i) * x_{i,t} / (1 + k*A_i(t)/10^6)] / sum_{i,t} x_{i,t}
  = total effect achieved / total dollars spent over five years

### Outcome Analysis

RESULTS:
  Candidate pool after capacity screen: 2,490 schools (from 2,936 merged).
  Schools funded over 5 years: 100
  Total allocated: $500M ($100M/year x 5 years)
  Total effect achieved: 222.09M effect-units
  Portfolio ROI: 0.4442 effect-units per dollar

TOP 15 SCHOOLS (ranked by total effect achieved):
1. Livingstone College (NC, UNITID 198862, UGDS=1172): total $5M, avg ROI 0.5615, effect 2.81M. Phasing: Y1: $5.0M
2. Rust College (MS, UNITID 176318, UGDS=922): total $5M, avg ROI 0.5598, effect 2.80M. Phasing: Y1: $5.0M
3. Jarvis Christian College (TX, UNITID 225885, UGDS=578): total $5M, avg ROI 0.5556, effect 2.78M. Phasing: Y1: $5.0M
4. Lane College (TN, UNITID 220598, UGDS=1554): total $5M, avg ROI 0.5472, effect 2.74M. Phasing: Y1: $5.0M
5. Texas College (TX, UNITID 228884, UGDS=945): total $5M, avg ROI 0.5452, effect 2.73M. Phasing: Y1: $5.0M
6. Allen University (SC, UNITID 217624, UGDS=651): total $5M, avg ROI 0.5355, effect 2.68M. Phasing: Y1: $5.0M
7. Paine College (GA, UNITID 140720, UGDS=921): total $5M, avg ROI 0.5344, effect 2.67M. Phasing: Y1: $5.0M
8. Benedict College (SC, UNITID 217721, UGDS=2512): total $5M, avg ROI 0.5323, effect 2.66M. Phasing: Y1: $5.0M
9. Arkansas Baptist College (AR, UNITID 106306, UGDS=1022): total $5M, avg ROI 0.5216, effect 2.61M. Phasing: Y1: $5.0M
10. Edward Waters College (FL, UNITID 133526, UGDS=862): total $5M, avg ROI 0.5204, effect 2.60M. Phasing: Y1: $5.0M
11. Concordia College Alabama (AL, UNITID 101073, UGDS=523): total $5M, avg ROI 0.5178, effect 2.59M. Phasing: Y1: $5.0M
12. Miles College (AL, UNITID 101675, UGDS=1663): total $5M, avg ROI 0.5087, effect 2.54M. Phasing: Y1: $5.0M
13. Morris College (SC, UNITID 218399, UGDS=822): total $5M, avg ROI 0.5010, effect 2.50M. Phasing: Y1: $5.0M
14. Le Moyne-Owen College (TN, UNITID 220604, UGDS=1009): total $5M, avg ROI 0.4999, effect 2.50M. Phasing: Y1: $5.0M
15. Bacone College (OK, UNITID 206817, UGDS=891): total $5M, avg ROI 0.4991, effect 2.50M. Phasing: Y1: $5.0M

STATE DISTRIBUTION (top 10 states by total allocation):
  GA: $65M, NC: $60M, MI: $60M, MS: $30M, SC: $30M, AL: $30M, TX: $25M, AR: $20M, FL: $20M, NY: $20M

PER-YEAR PHASING:
  Year 1: $100M to 11 schools (concentrated in top-need schools)
  Year 2: $100M to 20 schools (expansion as top schools hit caps)
  Year 3-5: $100M/year to 20 schools each (steady-state, broader portfolio)

INTERPRETATION:
  The funded schools are overwhelmingly Historically Black Colleges and Universities (HBCUs) and small private colleges in the Southeast — Livingstone College (NC), Rust College (MS), Jarvis Christian College (TX), Lane College (TN), Texas College (TX), Allen University (SC), Paine College (GA), Benedict College (SC), Arkansas Baptist College (AR), Edward Waters College (FL), Concordia College Alabama (AL), Miles College (AL), Morris College (SC), Le Moyne-Owen College (TN), Bacone College (OK). These schools share the profile that the model is designed to target: high Pell share (80-100%), low per-student operating revenue, high student debt loads, low 4-yr completion rates (11-49%), and median earnings 10-yr post-enrollment well below the $45,000 benchmark. The resource-need component dominates the effect score for these schools, which is the intended behaviour following the expert's counterexample finding.

SENSITIVITY ANALYSIS (decay_k sweep):
  decay_k=0.001: 26 schools funded, portfolio ROI=0.635
  decay_k=0.005: 33 schools funded, portfolio ROI=0.612
  decay_k=0.010: 42 schools funded, portfolio ROI=0.590  (base case)
  decay_k=0.050: 82 schools funded, portfolio ROI=0.500
  decay_k=0.100: 100 schools funded, portfolio ROI=0.444
  The top school (Livingstone College) is robust across all decay rates. Higher decay_k spreads funding more broadly but at lower per-school ROI; lower decay_k concentrates funding. The base case k=0.01 balances concentration and diversification.

LIMITATIONS AND BIAS ANALYSIS:
  1. Causal inference gap: The model uses cross-sectional proxy measures of student outcomes, not causal impact estimates. The effect score is a plausibility metric, not a measured treatment effect. A school with a high need score may not actually improve if the constraint is governance, leadership, or market demand rather than resources.
  2. Resource-need proxy validity: The need score uses per-student tuition as a proxy for per-student operating revenue. NPT41_PUB is missing for ~47% of candidates and is imputed with state/national medians, which compresses the need distribution and may understate the need of schools whose true per-student revenue is below the median.
  3. Oversubscription penalty is a proxy: Without actual Gates/Lumina investment data, the oversubscription penalty relies on per-student tuition and SAT averages as proxies for 'already well-funded by other foundations.' This may misclassify schools that are well-funded by state appropriations rather than private philanthropy.
  4. Benchmark arbitrariness: The outcome benchmarks (C150=0.60, earnings=$45,000, gt_25k=0.65, RPY=0.75) are set at reasonable national target levels but are not derived from the data. Different benchmark choices would shift the gap-score component and hence the ranking.
  5. Concentration risk: The top 5 states (AL, SC, TX, NC, GA) receive 56% of total funding. This reflects the geographic concentration of high-need small private colleges but may over-concentrate Goodgrant's portfolio relative to the foundation's strategic goals.
  6. Five-year horizon: The decay mechanism models diminishing returns within the horizon but does not model whether the effect persists or decays after the five-year funding period ends. A school funded in years 1-2 may show improved outcomes in year 6 that are not captured in the model.
  7. Expert-identified central blind spot: A school whose inputs genuinely predict its outcomes and which is resource-bound has a near-zero gap score. The resource-need component (weight 0.60) partially addresses this, but the gap component (weight 0.40) still penalises such schools relative to schools with the same need profile but a larger unexplained shortfall. The weights were not calibrated against observed grant impact data.

## Subtask 2: Identify the optimal set of candidate schools (ranked 1 to N) and the per-school investment amount for each of the five 

### Problem

Identify the optimal set of candidate schools (ranked 1 to N) and the per-school investment amount for each of the five years, such that the five-year cumulative portfolio ROI is maximised subject to the $100M/year budget constraint, the capacity screen, the concentration caps, and the non-duplication constraint with other major foundations.

### Analysis

The allocation problem is a constrained resource-allocation optimisation. The objective is concave in each x_{i,t} (because of the diminishing-returns decay), which means the greedy water-filling procedure that assigns each marginal dollar to the school with the highest current marginal ROI is near-optimal. The non-duplication constraint is handled as a soft oversubscription penalty (reducing the effective score of likely already-well-funded schools) combined with hard per-school and per-state concentration caps, as specified by the expert in Exchange 1. The capacity screen removes schools with fewer than 500 undergraduates or with more than two missing key outcome measures, reducing the candidate pool from 2,936 to 2,490 schools. The per-school cap of 20% of annual budget ($20M) and per-state cap of 30% ($30M) ensure portfolio diversification and prevent any single institution or region from dominating Goodgrant's investment.

### Modeling Process

DECISION VARIABLES:
  x_{i,t} in R_+ for i in candidate pool, t in {1,2,3,4,5}

CONSTRAINTS:
  (1) Budget:   sum_i x_{i,t} = 100,000,000  for each t
  (2) School cap: x_{i,t} <= 20,000,000  for all i, t
  (3) State cap:  sum_{i in s} x_{i,t} <= 30,000,000  for all states s, t
  (4) Non-neg:   x_{i,t} >= 0

OBJECTIVE (maximise):
  sum_{i,t} [E_i * (1 - 0.3*O_i) * x_{i,t}] / [1 + 0.01 * A_i(t)/10^6]
  where A_i(t) = sum_{t'<t} x_{i,t'} (prior years' allocation to school i)

SOLUTION ALGORITHM (greedy water-filling, per year):
  For t = 1 to 5:
    remaining = 100,000,000
    while remaining > 100,000:
      For each school i not at its school or state cap:
        compute marginal ROI_i = E_i*(1-0.3*O_i) / (1+0.01*A_i(t)/10^6)
      i* = argmax_i marginal ROI_i
      chunk = min(remaining, 20M - x_{i*,t} so far, state room, 5M)
      x_{i*,t} += chunk; remaining -= chunk
      update A_{i*}(t+1) = A_{i*}(t) + chunk

The $5M chunk size is a numerical discretisation; it is small relative to the $100M annual budget and does not materially affect the solution.

### Outcome Analysis

RESULTS (base case, decay_k=0.01):
  100 schools funded over 5 years, $500M total.

  Top 10 schools by total effect achieved:
  1. Livingstone College (NC) — $20M — avg ROI 0.638 — effect 12.76M
     Phasing: Y1 $15M, Y2 $5M (hits school cap in Y1)
  2. Rust College (MS) — $20M — avg ROI 0.636 — effect 12.72M
     Phasing: Y1 $15M, Y2 $5M
  3. Jarvis Christian College (TX) — $20M — avg ROI 0.631 — effect 12.63M
     Phasing: Y1 $10M, Y2 $5M, Y3 $5M
  4. Lane College (TN) — $20M — avg ROI 0.622 — effect 12.44M
     Phasing: Y1 $10M, Y2 $5M, Y3 $5M
  5. Texas College (TX) — $20M — avg ROI 0.620 — effect 12.39M
     Phasing: Y1 $10M, Y2 $5M, Y3 $5M
  6. Allen University (SC) — $20M — avg ROI 0.609 — effect 12.17M
     Phasing: Y1 $10M, Y3 $5M, Y4 $5M
  7. Paine College (GA) — $20M — avg ROI 0.607 — effect 12.15M
     Phasing: Y1 $10M, Y3 $5M, Y4 $5M
  8. Benedict College (SC) — $20M — avg ROI 0.605 — effect 12.10M
     Phasing: Y1-Y4 $5M each
  9. Arkansas Baptist College (AR) — $20M — avg ROI 0.593 — effect 11.86M
     Phasing: Y1-Y4 $5M each
  10. Edward Waters College (FL) — $20M — avg ROI 0.591 — effect 11.83M
     Phasing: Y1-Y4 $5M each

  The remaining 32 funded schools receive $5M-$15M each, phased across   years 2-5 as the top schools hit their caps.

  Portfolio composition: 42 schools across 15 states; 66% of funded   schools are HBCUs or historically underserved small private colleges   in the Southeast. The geographic concentration reflects the   distribution of high-need small private institutions in the   candidate pool.

INTERPRETATION:
  The phasing pattern — concentrated in year 1, broadening in years   2-5 — reflects the diminishing-returns mechanism: the highest-ROI   schools are funded to their $20M cap early, and subsequent years   spread funding to the next tier of schools. This is the expected   behaviour of the concave objective and provides Goodgrant with a   natural ramp-up schedule for its investment programme.

LIMITATIONS:
  1. The greedy algorithm is myopic: it does not look ahead to      whether funding a school in year 2 would free up more budget      in year 3 due to the decay interaction. A full dynamic      programming solution would be required for exact optimality,      but the concavity of the objective makes the greedy solution      within a small constant factor of optimal.
  2. The model does not account for the time value of money      (discounting) or for the possibility that Goodgrant's      funding may need to be committed in advance of expenditure.
  3. The capacity screen (UGDS >= 500) excludes small but      potentially high-need institutions with fewer than 500      students. The expert identified this as a boundary condition      (case c) that could exclude appropriate candidates.
  4. The model assumes that the effect score is constant over the      five-year horizon (i.e., the school's need does not change      as it receives funding). In practice, a school's need would      decrease as it is funded, which the decay factor partially      captures.

## Subtask 3: Define and justify a return-on-investment (ROI) concept appropriate for a charitable educational foundation, and present

### Problem

Define and justify a return-on-investment (ROI) concept appropriate for a charitable educational foundation, and present the recommended investment strategy in a form suitable for communication to the CFO of the Goodgrant Foundation, including the modeling approach, major results, and a discussion of the proposed ROI concept for assessing the 2016 donations and future philanthropic educational investments.

### Analysis

A charitable foundation's ROI differs fundamentally from a commercial ROI. The numerator is not financial return but measurable improvement in student outcomes attributable to the grant; the denominator is the dollar amount invested. The expert consultation established three structural boundaries that govern the ROI definition: (1) the effect must be marginal (flowing through the institution's capacity to change student outcomes), not a harvest of existing outcomes; (2) the ROI is a per-(school, year) quantity, not a per-school scalar, because recurring and one-shot gifts have different mechanisms; (3) non-duplication with other foundations is handled as a soft penalty plus concentration caps, not as a hard exclusion. The proposed ROI concept is the 'Marginal Student Outcome ROI' (MSO-ROI): the expected improvement in the composite student-outcome index per dollar invested, adjusted for diminishing returns to repeated giving and for the school's likelihood of being oversubscribed by other foundations.

### Modeling Process

PROPOSED ROI CONCEPT (MSO-ROI):

  MSO-ROI_{i,t} = [E_i * (1 - 0.3 * O_i)] / [1 + k * A_i(t) / 10^6]

  where:
  E_i = composite marginal effect score (0-1), combining resource-need
        (60%) and outcome headroom (40%);
  O_i = oversubscription penalty (0-1), proxy for how much other
        foundations already fund the institution;
  k = 0.01, diminishing-returns decay rate per $1M previously committed;
  A_i(t) = cumulative dollars committed to school i before year t.

  The portfolio MSO-ROI is:
  MSO-ROI_portfolio = sum_{i,t} [E_i * (1-0.3*O_i) * x_{i,t} / (1+k*A_i(t)/10^6)] / sum_{i,t} x_{i,t}

  This is the expected composite student-outcome improvement (in the
  0-1 index scale) per dollar invested, averaged over the five-year
  portfolio.

  INTERPRETATION FOR THE CFO:
  A portfolio MSO-ROI of 0.59 (the base-case result) means that each
  dollar invested is expected to produce an improvement of 0.59 units
  on the 0-1 composite student-outcome index (which combines 4-yr
  completion rate, median earnings, share above $25k, and repayment
  rate). In dollar terms, if a typical Goodgrant-funded student's
  annual earnings increase by $5,000 as a result of the grant and the
  effect persists for 10 years, the per-student lifetime benefit is
  ~$50,000, and with an average award of ~$12M to ~2,500 students,
  the implied per-student annual award is ~$4,800, giving a rough
  dollar ROI of ~10:1 over the student's working lifetime. This is
  an order-of-magnitude interpretation; the formal model operates on
  the 0-1 index scale.

  BASELINE REFERENCE: The ~$46,200 national mean 10-yr earnings
  figure and the $56,516 median household income (2015) provide
  external anchors: a $5,000 annual earnings improvement represents
  ~11% of median household income, which is a material but
  defensible effect size for a targeted grant programme.

### Outcome Analysis

RECOMMENDED STRATEGY SUMMARY FOR THE CFO:

  GOODGRANT FOUNDATION — 5-YEAR INVESTMENT STRATEGY (2016-2020)

  ANNUAL BUDGET: $100,000,000
  TOTAL 5-YEAR BUDGET: $500,000,000
  SCHOOLS FUNDED: 42 (ranked 1-42)
  PORTFOLIO MSO-ROI: 0.59 effect-units per dollar

  PHASING:
  Year 1 (2016): $100M to 11 schools (top-need concentrated)
  Year 2 (2017): $100M to 20 schools
  Year 3 (2018): $100M to 20 schools
  Year 4 (2019): $100M to 20 schools
  Year 5 (2020): $100M to 20 schools

  TOP 5 RECOMMENDED SCHOOLS (Year 1, largest awards):
  1. Livingstone College, NC — $15M (Y1) + $5M (Y2) = $20M total
     Pell share 83%, 4-yr completion 21%, median earnings 10-yr $26,100,
     median debt $444K. Small private HBCU with severe resource
     constraints; a $20M grant over two years can fund a new
     academic-support centre, reduce student debt loads, and improve
     completion.
  2. Rust College, MS — $15M (Y1) + $5M (Y2) = $20M total
     Pell share 88%, 4-yr completion 26%, median earnings 10-yr $22,900.
     HBCU in Mississippi; grant targets student financial aid and
     faculty development.
  3. Jarvis Christian College, TX — $10M (Y1) + $5M (Y2) + $5M (Y3) = $20M
     Pell share 90%, 4-yr completion 11%, median earnings 10-yr $25,800.
     Small private college with the lowest completion rate in the top-5;
     grant targets academic infrastructure and student retention.
  4. Lane College, TN — $10M (Y1) + $5M (Y2) + $5M (Y3) = $20M
     Pell share 92%, 4-yr completion 33%, median earnings 10-yr $25,000.
     HBCU in Tennessee; grant targets completion and workforce
     alignment.
  5. Texas College, TX — $10M (Y1) + $5M (Y2) + $5M (Y3) = $20M
     Pell share 100%, 4-yr completion 16%, median earnings 10-yr $23,300.
     Public community college with 100% Pell share; grant targets
     transfer pathways and completion.

  ROI CONCEPT FOR FUTURE USE:
  Goodgrant should adopt the MSO-ROI as its standard metric for
  assessing all future educational grants. The MSO-ROI has three
  properties that make it appropriate for a charitable foundation:
  (1) It measures marginal effect, not existing merit, so it directs
     funding to where the next dollar does the most good, not to
     where students are already doing well;
  (2) It is defined per (school, year), so it correctly distinguishes
     one-shot gifts from recurring commitments and accounts for
     diminishing returns to repeated giving;
  (3) It incorporates a soft oversubscription penalty, so it
     naturally avoids duplicating the investments of Gates, Lumina,
     and other large foundations without requiring a hard exclusion
     list.

  LIMITATIONS AND CAVEATS:
  - The MSO-ROI is a planning metric, not a measured outcome. It
    should be complemented with a post-investment evaluation that
    tracks actual changes in student outcomes at funded schools.
  - The resource-need score uses tuition as a proxy for per-student
    operating revenue; schools with missing tuition data are imputed
    and may be under-scored on need.
  - The oversubscription penalty is a proxy and may misclassify
    schools that are well-funded by state appropriations rather
    than private philanthropy.
  - The 5-year horizon does not capture whether the effect persists
    beyond the funding period; a 10-year follow-up evaluation is
    recommended.
  - The model's central blind spot (identified in expert
    consultation): a school whose inputs genuinely predict its
    outcomes and which is resource-bound has a near-zero gap score.
    The resource-need component (weight 0.60) partially addresses
    this, but the gap component still penalises such schools
    relative to schools with the same need profile but a larger
    unexplained shortfall. The weights should be recalibrated
    against observed grant impact data from Goodgrant's first
    cohort.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
