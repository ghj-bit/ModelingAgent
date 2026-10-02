# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence

## Exchange 1 (Structure)

**Question** (expert_question_1.md): "From your experience funding schools, what is the one
on-the-ground sign that a school actually turns money into better student outcomes?"

**Reply** (paraphrased): The observable sign is whether the school already moves its own
students across the finish line with the resources it has — specifically whether students who
arrive with weak preparation actually graduate, rather than the school graduating mainly those
who arrived already likely to succeed. The empirical judgment is the gap between a school's
actual outcomes and what its incoming-student profile would predict.

**How the reply affected the work:** This became the structural form of the model. The
value-added index is defined as the OLS residual of each outcome on the incoming-student
profile (SAT, Pell share, ethnic mix, enrollment size), stratified by degree level. The model
compares schools on the residual (actual minus predicted), not on the raw outcome level. This
is the direct operationalization of "the gap between actual outcomes and what the
incoming-student profile predicts." The stratum split (4-year vs 2-year) is a constraint the
model respects: comparing a 4-year university's completion rate to a 2-year college's would be
physically meaningless, so the residual is computed within stratum.

## Exchange 2 (Bias)

**Question** (expert_question_2.md): "Scorecard numbers like graduation rates and student
earnings come from schools that report them. What is the biggest reason such reported numbers
can mislead a donor?"

**Reply** (paraphrased): The biggest reason is selection, not measurement error: the numbers
describe only the students the school chose to enroll and keep. A school can post strong
graduation and earnings figures simply by admitting advantaged students and letting the weakest
ones leave. Reported rates are also computed on a narrow cohort (first-time, full-time,
degree-seeking entrants), excluding transfers, part-time, and returning students. Earnings
figures cover only those who graduated and were matched to tax records, so schools with high
attrition look better than they are.

**How the reply affected the work:** The model's Stage 1 (value-added residual) is the bias
correction. By conditioning on the incoming-student profile, the residual captures the school's
contribution, not its admissions policy. The cohort-size floor (UGDS >= 100) is the guard
against small-base earnings matching: a school with a tiny reporting base has a residual
dominated by noise, so it is excluded. The bias analysis in solution.json (subtask_outcome_
analysis, "BIAS ANALYSIS AND LIMITATIONS") is structured around the three mechanisms named:
admissions selection, cohort-definition exclusion, and earnings matching. The model's
limitation section states plainly that residual selection bias remains to the extent that
unobserved admissions criteria correlate with the observed profile.

## Exchange 3 (Interpretation)

**Question** (expert_question_3.md): "Before a donor would call a school a good use of money,
how big a margin above average results would you want to see, and why that size?"

**Reply** (paraphrased): The school's actual outcomes must beat what its incoming-student
profile predicts by a margin large enough that it cannot be explained by noise or cohort
composition — roughly 10 to 15 percentage points on a completion-rate measure, sustained over
several cohorts, not a single year. Below ~10 points the gap is within the range that reporting
quirks, small cohort sizes, and year-to-year swings produce on their own. Above ~15 points the
school is either genuinely converting resources into progress or has defined its cohort so
narrowly that the comparison is unfair.

**How the reply affected the work:** The value-added floor (min_resid_z = 0.25, i.e. the
school's index is at least 0.25 standard deviations above the stratum mean) is the operational
translation of "a margin large enough to survive noise." The cohort-size floor (UGDS >= 100)
is the proxy for "sustained over several cohorts" given the file has no year-over-year data:
a large pooled cohort is the closest available stand-in for persistence. The sensitivity
sweep (min_resid = 0.0, 0.25, 0.5, 1.0) shows the eligible pool shrinks from 822 to 39 as the
floor tightens, and the top-5 ranking is stable across all floors, confirming the floor
selects on capacity without reshuffling the top of the list.
