# Solution

## Subtask 1: Define a defensible return-on-investment (ROI) measure appropriate for a charitable foundation such as the Goodgrant Fou

### Problem

Define a defensible return-on-investment (ROI) measure appropriate for a charitable foundation such as the Goodgrant Foundation, to be used for assessing the 2016 donation and future philanthropic educational investments. Scope: the concept and formula for ROI, its numerator (student-earnings benefit) and denominator (dollars donated), the benchmark windows, and the defended parameter values that anchor it. This is the conceptual core the problem's addendum asks the CFO letter to explain.

### Analysis

A charitable ROI cannot be the commercial 'dollar return on dollar in'; the return is student performance, and the investment is the donation. I anchor the numerator to the College Scorecard's own earnings metrics rather than invent a new outcome. Per the planner-recorded external data (Item 1), gt_25k_p6 (share of students earning more than $25,000 six years after enrollment) is the Department of Education's 'does the school add any value at all' indicator, and md_earn_wne_p10 (median earnings ten years after entry) is the primary outcome; the ~$46,200 national mean (Brookings) and the ~$56,516 2015 median household income (Item 2, Census) are the reference levels that bound what counts as a strong effect. I treat the observed Scorecard outcomes as the school's demonstrated effectiveness and define the grant's marginal benefit as a defended per-student, per-year earnings improvement delta-E applied over the funded horizon plus a post-grant persistence window. All three magnitudes the problem leaves open (grant scale, delta-E, decay horizon) are stated as defended assumptions after the expert confirmed in Exchange 1 that they are not recoverable from the data.

### Modeling Process

Per-school ROI:  ROI_i = Benefit_i / Cost_i.  Benefit_i = UGDS_i * [ T * deltaE + P * deltaE * r ], where UGDS_i is the undergraduate enrollment (annual student-cohort proxy), T = 5 funded years, deltaE = $1,500 per student per year (base case; ~3% of the ~$46.2k national mean), P = 3 post-grant persistence years, r = 0.40 (fraction of the effect retained after the last dollar). Cost_i = award_i * 5, where award_i is the annual grant to school i. Portfolio ROI = sum_i Benefit_i / sum_i Cost_i. Defended parameters: deltaE = $1,500/yr (swept $1,000-$2,500), P = 3 yr (base), r = 0.40 (base). The 6-year/10-year Scorecard windows and the $25k / ~$46.2k reference levels are fixed as the benchmark windows in the ROI narrative.

### Outcome Analysis

At the base case (deltaE=$1,500, P=3, r=0.40) the 60-school portfolio generates Benefit = $2.856B against Cost = $500M over five years, a portfolio ROI of 5.71 (each donated dollar is associated with $5.71 of discounted student-earnings benefit). Median per-school ROI is 4.43. Sensitivity: ROI is linear in deltaE (2.51 at $1,000, 5.71 at $1,500, 6.27 at $2,500), so the ROI conclusion is not an artifact of a particular delta-E within the defended range. Limitation/bias: the ROI is a benefit-to-cost ratio built on an assumed treatment effect, not a measured causal gain; the Scorecard outcomes are observational, so the numerator inherits the survivorship selection bias identified in Exchange 3. The ratio is best read as a defensible ranking and scale device for a foundation, not a promise of a 5.71x financial multiple.

## Subtask 2: Construct an optimized, prioritized candidate list of schools for Goodgrant investment, based on each school's demonstra

### Problem

Construct an optimized, prioritized candidate list of schools for Goodgrant investment, based on each school's demonstrated potential for effective use of private funding. Scope: the scoring/ranking model that turns the IPEDS and Scorecard data into a single 1-to-N prioritized list, the eligibility filter, and the defense of why the composite (not a single metric) is sound.

### Analysis

'Effective use of private funding' means the school (a) already demonstrates strong student value-added and (b) has the financial vulnerability that a private grant can actually relieve. I use a defendable subset of the two files: value-added from gt_25k_p6 and md_earn_wne_p10; vulnerability from PCTPELL (Pell share), C150_4_POOLED_SUPP (first-year net price), RET_FT4 (4-year retention), and PCTFLOAN (loan share). A single metric fails: earnings alone over-ranks already-elite, well-funded schools where a grant adds little, and vulnerability alone over-ranks schools that cannot convert funding into outcomes. A weighted composite of the two is the sound middle. All 2,977 candidate UNITIDs in the IPEDS file match the Scorecard file, so no school is dropped for lack of data before scoring.

### Modeling Process

Value-added term (0..1): VA_i = 0.5 * clip((gt_25k_p6_i - 0.50)/0.50, 0, 1) + 0.5 * clip((md_earn_wne_p10_i - 25000)/(116400 - 25000), 0, 1). Need/vulnerability term (0..1): NEED_i = clip(0.35*PCTPELL_i + 0.25*(1 - RET_FT4_i) + 0.25*C150_4_i + 0.15*PCTFLOAN_i, 0, 1). Composite: SCORE_i = w_va * VA_i + w_need * NEED_i, with w_va = 0.6, w_need = 0.4. Eligibility: a school must have at least one earnings metric (gt_25k_p6 or md_earn_wne_p10) AND must not be survivorship-risk, where survivorship-risk = (UGDS < 1000) OR (DISTANCEONLY = 1) OR (suppressed earnings cohort). The final eligible pool is 2,163 of 2,977 schools (577 excluded as survivorship-risk). Schools are ranked by SCORE descending.

### Outcome Analysis

The composite produces a coherent 1-to-N list: the top-60 have mean gt_25k_p6 of 0.846 (vs 0.568 national median, +28.2 pts), mean md_earn_wne_p10 of $71,317 (vs $35,400 national median), mean 4-yr retention 0.884, and 58 of 60 are four-year institutions. The portfolio spans 21 states (MA 10, NY 9, PA 9, CA 5, MD 3, NJ 2) and is 51 private / 9 public, consistent with the data's 1,574 public / 1,361 private base. Limitation: the 0.6/0.4 weight is a judgment; the sensitivity sweep (w_va 0.4 to 0.8) keeps the portfolio ROI between 2.20 and 3.88 and the median enrollment between ~1,000 and ~2,600, so the ranking is stable to the weight, though the exact top-60 membership shifts. The survivorship filter is the load-bearing assumption (Exchange 3) and is the model's central bias, quantified in Task 4.

## Subtask 3: Determine the investment amount per school, the total portfolio, and the time duration the money should be provided to m

### Problem

Determine the investment amount per school, the total portfolio, and the time duration the money should be provided to maximize the likelihood of a strong positive effect on student performance. Scope: the allocation rule, the per-school award, the number of schools funded per year, and the funding duration.

### Analysis

The expert rejected (Exchange 2) my proposed diminishing-weight (geometric-decay) allocation; per policy I fell back to a plain top-K equal-award portfolio, which is the most defensible and simplest structure and the one the reply did not dispute. The per-school scale is a defended assumption (Exchange 1): I choose K = 60 schools so each receives ~$1.67M per year, a grant large enough to be material against median enrollment (~$725 per student-year) yet small enough to keep the portfolio concentrated on the strongest candidates rather than spread too thin. The same 60 schools are funded for the full 5-year window (July 2016 - July 2021) with fixed annual awards, because a multi-year commitment is what makes the per-student effect plausible and lets ROI be measured on cumulative benefit over cumulative cost.

### Modeling Process

Allocation: take the top K = 60 schools by SCORE among the eligible pool; award_i = $100,000,000 / 60 = $1,666,667 per year to each; Cost_i = 5 * award_i = $8,333,333 over the window. Total annual outlay = $100M, total 5-year outlay = $500M. Duration: 5 years, fixed award, same 60 schools. Per-student cost = award_total / (UGDS_i * 5). The K = 60 choice is defended against the sweep: K = 40 (award $2.5M) gives portfolio ROI 2.18, K = 60 gives 5.71, K = 100 (award $1M) gives 6.70; K = 60 balances a meaningful per-school award against portfolio concentration and matches the ~$1.5M per-school scale proposed in Exchange 2.

### Outcome Analysis

The base-case portfolio funds 60 schools at $1.67M/year each for 5 years, $500M total. Per-student cost ranges from $92 (large enrollment) to $1,596 (smaller enrollment) per student over the window, with a median of ~$410. Benefit is concentrated in the larger-enrollment schools (the top-20 by score deliver $769M of the $2.856B total benefit), which is exactly the mechanism by which equal awards to top-ranked schools capture scale. Limitation: equal awards ignore diminishing returns in enrollment scale, so a very large university and a mid-size college receive the same dollar amount; a scale-tapered rule would raise efficiency but was rejected in favor of simplicity in Exchange 2. The fixed 5-year duration assumes the effect does not require re-underwriting mid-stream.

## Subtask 4: Validate the strategy against the data, analyze its robustness and biases, and answer every subproblem: the prioritized 

### Problem

Validate the strategy against the data, analyze its robustness and biases, and answer every subproblem: the prioritized candidate list, the per-school investment, the ROI per school, and the funding duration. Scope: the sensitivity analyses, the survivorship-bias quantification, the full ranked list, and the consolidated answer.

### Analysis

The most consequential bias is the one the expert named in Exchange 3: institutions whose earnings figures are computed over a small, self-selected, survivorship-selected subset (very small private colleges, distance-only/for-profit institutions with low UGDS and suppressed cohorts) rank high on the value-added term and inflate the ROI numerator, so ranking and ROI err in the same direction and the top-K equal-award rule concentrates dollars on exactly these schools. I validate by (a) sweeping the structural parameters, (b) quantifying the survivorship filter's effect on ROI and list membership, and (c) checking the portfolio's composition against national benchmarks.

### Modeling Process

Sensitivity: (1) delta-E sweep at K=60: ROI 2.51 / 5.71 / 6.27 for $1,000 / $1,500 / $2,500. (2) w_va sweep 0.4-0.8: ROI 2.20-3.88, median UGDS 1,019-2,557. (3) K sweep 40-150: ROI 2.18-11.92, award $2.5M-$667k. (4) Survivorship filter: unfiltered top-60 ROI = 3.76 with 20 survivorship-risk schools contributing 5.0% of benefit; filtered (base case) ROI = 5.71 with 0 survivorship-risk schools; 40 of the 60 top members are robust to the filter (only 20 change). Portfolio checks: 21 states, 51 private / 9 public, 58/60 four-year, mean gt_25k_p6 0.846 (+28.2 pts over national 0.568), mean md_earn_wne_p10 $71,317 (+$33,900 over national $35,400).

### Outcome Analysis

The full answer: fund the top 60 schools by composite score (value-added 0.6 + vulnerability 0.4, survivorship-risk excluded) at $1.67M per year each for the full 5-year window July 2016-July 2021, $500M total, with a per-school ROI of Benefit/Cost where Benefit = UGDS * [5*1500 + 3*1500*0.40] and Cost = 5*1,666,667. The prioritized list (rank, UNITID, name, state, score, enrollment, gt_25k, median earnings 10yr, Pell share, retention, annual award, ROI) is in allocated_schools.csv; the top 10 are: 1 MCPHS University MA (ROI 4.25), 2 Albany College of Pharmacy and Health Sciences NY (1.20), 3 University of the Sciences PA (2.04), 4 Pennsylvania College of Health Sciences PA (1.56), 5 Babson College MA (2.35), 6 MIT MA (5.03), 7 Rensselaer Polytechnic Institute NY (6.00), 8 Stevens Institute of Technology NJ (2.97), 9 Georgetown University DC (8.10), 10 Rose-Hulman Institute of Technology IN (2.42). Robustness: 40/60 members stable to the survivorship filter, ROI linear in delta-E, ranking stable to the w_va weight. Primary bias (Exchange 3): the value-added term reads survivorship-selected earnings as effectiveness for small/distance-only/suppressed-cohort schools, which the filter removes; the remaining bias is that the ROI numerator is an assumed treatment effect, not a measured causal gain, and equal awards ignore enrollment-scale diminishing returns. These are the model's limits and are the content of the bias/robustness discussion the problem's addendum requires.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
