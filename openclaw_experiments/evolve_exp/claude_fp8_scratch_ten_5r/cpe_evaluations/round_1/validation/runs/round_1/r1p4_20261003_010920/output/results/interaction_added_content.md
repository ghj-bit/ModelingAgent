# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — MM-Bench 2016_C (Goodgrant Foundation)

Ten expert exchanges, one question per round, each reply converted into a
model parameter, constraint, or decision rule before the next exchange.

## Exchange 1
**Question (expert_question_1.md):** When a foundation's grants measurably improve college
students' outcomes, how many years of funding does a typical school need to show real change?
**Reply (expert_reply_1.json):** Measurable change requires about 4–6 years of sustained
funding; first credible signals around year 3–4. The problem's 5-year horizon is roughly the
minimum; single-year grants cannot demonstrate genuine outcome change.
**Conversion to work:** Funding term T = 5 years (task-given horizon, confirmed adequate by
this exchange). The expected-improvement estimator is a term-scaled quantity,
exp_gain = base_effect × T / 5, so a shorter term scales the effect linearly down.
Interval of validity: [4, 6] years of sustained funding for institution-wide change.

## Exchange 2
**Question (expert_question_2.md):** If the foundation gives a school several hundred thousand
dollars a year instead of several million, which types of student improvements would actually happen?
**Reply (expert_reply_2.json):** At a few hundred thousand dollars per year only targeted,
staff-level interventions happen (a few advisers, small emergency-aid pools, one or two
developmental-course reforms, modest career services). Real but localized: retention and
course pass rates for targeted students. What does not happen at this scale: measurable
change in institution-wide graduation rates, cohort earnings, or repayment rates — those
need multi-million-dollar multi-year commitments.
**Conversion to work:** Defines the effectiveness floor of a grant. Grants below the
institution-wide scale cannot deliver the modeled outcome (completion-rate movement), so the
allocation algorithm enforces a minimum annual grant of $2,000,000 (the lower edge of the
multi-million band given in exchange 4) and zero allocation below it. The portfolio ROI is
therefore measured in institution-wide completion points, not localized effects.

## Exchange 3
**Question (expert_question_3.md):** When deciding whether to fund a college's student-support
work, which student outcomes do donors care most about?
**Reply (expert_reply_3.json):** Priority order: (1) completion/graduation, especially for
low-income and first-generation students — the headline metric for "educational
performance"; (2) retention and progression as the leading indicator of completion;
(3) post-graduation earnings; (4) debt and repayment; (5) access and equity as a
cross-cutting lens. Two qualifications: donors weight equity gaps, not just institutional
averages, and they prefer outcomes that are comparable across schools (federal/Scorecard
measures).
**Conversion to work:** The outcome in the ROI definition is the on-time completion rate
(150% pooled rate for 4-year schools, 200% pooled rate for <4-year schools — the
comparable Scorecard measure), not earnings or retention alone. Because the data set has no
subgroup completion rates, the equity-gap qualification is implemented through need-side
targeting (Pell share, minority share) rather than a subgroup-outcome term. The
cross-school-comparability qualification is why peer benchmarking is within control and
degree-type class (150% vs 200% rates are not comparable across classes).

## Exchange 4
**Question (expert_question_4.md):** Should a foundation's $100 million be spread over
hundreds of schools, or concentrated in a few dozen?
**Reply (expert_reply_4.json):** Concentrated in a few dozen. $100M spread over hundreds is
$200–500K per school — the scale from exchange 2 with only localized effects and many
unverifiable small grants. A few dozen at $2–5M per school per year is the scale at which
institution-wide graduation, earnings, and repayment metrics can plausibly move over a
multi-year horizon, and it supports the multi-year commitment. Trade-off: fewer schools,
more per-school risk — hence a prioritized candidate list with a smaller number of larger,
sustained grants.
**Conversion to work:** Panel size K = 45 (a "few dozen"); per-school annual grant bounded to
[$2,000,000, $5,000,000]; the allocation algorithm fills the budget by topping up the
highest-ROI candidates from $2M toward $5M, so the budget is fully deployed (sum of
annual grants = $100,000,000 exactly). Swept over K ∈ {25, 45, 75} to show the
concentration trade-off (see model_output.json sweep).

## Exchange 5
**Question (expert_question_5.md):** When choosing which schools deserve big multi-year
grants, which student characteristics matter most to a donor?
**Reply (expert_reply_5.json):** Weighted roughly: (1) low-income / Pell-eligible share —
the single most-used characteristic; (2) first-generation status; (3) underrepresented
minority share as an equity lens; (4) academic preparation / entering proficiency (share
needing developmental coursework); (5) part-time and nontraditional/independent enrollment
(stop-out risk). Qualifications: these matter as gaps, not just presence, and should be
comparable federal/Scorecard measures.
**Conversion to work:** The need score is a weighted sum of the data's comparable
proxies: PCTPELL (weight 0.38, the most-used characteristic), minority enrollment share
(UGDS_BLACK + UGDS_HISP + UGDS_AIAN + UGDS_NHPI over UGDS; weight 0.20), share of students
aged 25+ as the nontraditional/enrollment-intensity proxy (UG25abv, weight 0.12),
part-time share PPTUG_EF (weight 0.15), and a financial-stress proxy (PCTFLOAN with a
public/private adjustment, weight 0.15). First-generation status is not a column in this
extract, so PCTPELL carries the means-need weight (documented in solution.json).

## Exchange 6
**Question (expert_question_6.md):** Which kinds of colleges and universities would large
educational grants make the biggest difference for?
**Reply (expert_reply_6.json):** Biggest difference where high need meets demonstrated
capacity to use money well and a realistic path to moving outcomes — typically: public
regional/comprehensive universities and non-flagship state schools; minority-serving
institutions (HBCU, HSI, tribal); community colleges with strong transfer/credential
pathways (noisier metrics, more localized effects); access-oriented private colleges with
modest endowments. Least effect: wealthy highly selective institutions and very small or
financially fragile schools. Key qualifier: demonstrated potential for effective use of
funds, not need alone.
**Conversion to work:** A type-fit multiplier applied to the expected gain: MSI = 1.0,
public 4-year regional = 0.95, community college = 0.85 (noisier/localized per the
reply), private 4-year access-oriented = 0.70; a wealthy-selective screen (top decile of
completion with Pell share below 30%) is cut to 0.15. Very small schools are deprioritized
through the capacity score's enrollment-scale term rather than hard-excluded. The
"capacity, not need alone" qualifier is what splits the model into need × capacity ×
headroom × fit rather than need alone.

## Exchange 7
**Question (expert_question_7.md):** What kinds of data or evidence would you want to see
before trusting a school's claim that it can use grant money well?
**Reply (expert_reply_7.json):** Track record with prior outside money and documented
gains; existing support infrastructure (advising, financial aid, student support already
staffed); outcome data showing it can move the needle on comparable metrics; leadership
stability and commitment; data capacity to track cohorts and report; financial health
(grant not absorbed by deficits); a realistic specific plan. Core test: demonstrated
capacity and results, not stated intent.
**Conversion to work:** The capacity score (the "demonstrated effective use" term) is
proxied with what the data set contains: institutional scale and stability (enrollment
size, 30%), operating financial-aid infrastructure (PCTFLOAN reported with net-price
data, 20%), an existing completion record (the school already produces completers, 30%),
and a concentrated mission where MSI status exists (20%). Items the data set cannot carry
(prior grant history, leadership stability, audited finances, a specific plan) are listed
as limitations in solution.json rather than silently dropped.

## Exchange 8
**Question (expert_question_8.md):** What outcome would make a donor say the grant was a
success, and how big a change would they expect?
**Reply (expert_reply_8.json):** Success = measurable improvement on comparable
cohort-based outcomes the grant plausibly caused — chiefly completion (overall and
low-income/first-generation), with retention and gateway-course pass rates as leading
indicators, earnings/repayment secondary; equity-gap closure counts heavily. Expected
magnitude for a $2–5M/yr multi-year grant: a modest but real shift, roughly 2–5
percentage points in graduation/retention or a comparable narrowing of an equity gap,
sustained over a 4–6 year horizon — not dramatic jumps.
**Conversion to work:** The central effect parameter base_effect = 3.5 completion points
over a 5-year term (midpoint of [2, 5]), with the per-school cap min(0.9 × headroom,
5pp × capacity) so no school's expected gain exceeds the donor-expected band or its
distance to the peer benchmark. The renewal/monitoring rule (task subproblem 3: time
duration) is: monitor retention and gateway-course pass rates in years 1–3 as leading
indicators, with completion as the lagged confirmatory metric in years 4–5.

## Exchange 9
**Question (expert_question_9.md):** If a school's graduation rate is already near the top
of its peer group, would a donor still want to fund it?
**Reply (expert_reply_9.json):** Generally no as a priority target — little headroom,
small marginal effect on the headline outcome, typically ample resources. Two exceptions:
large internal equity gaps that the high average masks (still a legitimate target), and a
proven track record funded to scale/replicate (secondary rationale).
**Conversion to work:** The headroom term is the primary gate: expected gain is capped at
90% of the school's gap to its local peer benchmark, and schools at or above the
benchmark have zero modeled gain and are not funded. The equity-gap exception is honored
because need (Pell/minority share) is a separate multiplicative factor, so a high-average
school with a heavy low-income body retains eligibility through need rather than through
headroom. The wealthy-selective fit cut (0.15) implements the "typically ample resources"
exclusion.

## Exchange 10
**Question (expert_question_10.md):** After funding schools for several years, what would
you do with schools whose students aren't making progress?
**Reply (expert_reply_10.json):** Honor the committed multi-year term, then exit at the end
of the term if there is no credible improvement — no renewal. Distinguish "no progress"
from "no measurable progress" (cohort metrics lag; a school moving on leading indicators
may warrant a short extension). Attribute before judging: separate grant failure from
external shocks (state funding cuts, enrollment collapse, leadership turnover). Redirect
funds to the next candidates on the prioritized list. Require a diagnosis, not just a
verdict, for reconsideration.
**Conversion to work:** The time-duration and exit rule of the strategy: 5-year committed
term with no early exit; a year-3 checkpoint on leading indicators (retention, gateway
pass rates) decides continuation of the remaining term versus short extension; at term end,
schools below a pre-committed completion-gain threshold are not renewed, and freed budget
is reallocated down the ranked 45-school list (which is why the list is prioritized, not a
flat set). External-shock attribution is listed as an operational caveat, not encoded,
because the data set has no shock indicators.
