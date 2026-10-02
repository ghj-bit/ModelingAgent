# Interaction Evidence — Problem 2016_C

Three expert exchanges, one question each, each reply converted into a model
parameter or constraint before the next exchange.

## Exchange 1

**Question (expert_question_1.md):** When judging whether a college grant truly
improved student outcomes, what do you look at in practice first — which
real-world signals tell you the money was well spent?

**Reply (expert_reply_1.json, summarized):** In practice the first signals are
completion and post-graduation earnings, not inputs like spending or
enrollment. Completion rate combined with earnings is the strongest single
signal; completion without earnings suggests a credential of little value.
These are empirical judgments about which indicators matter, not precise
thresholds.

**How the reply became work:** defined the outcome side of the model. The
primary outcome pair was fixed to C150_4_POOLED_SUPP (completion) and
md_earn_wne_p10 (10-year median earnings), and the eligibility filter
"both signals present" was adopted, cutting the analytic universe from 2,935
matched schools to 626 evaluable schools (results/selected_K30.csv,
logs/clean_report.json). Earnings also entered the value-per-completion term
V = 0.5*COST_STU + 0.25*max(0, earnings - 25000).

## Exchange 2 (builds on exchange 1: with outcomes defined, what kind of school should receive the money)

**Question (expert_question_2.md):** When choosing which colleges to fund,
would you favor large schools that reach thousands of students per dollar, or
small struggling schools where a grant can actually move outcomes?

**Reply (expert_reply_2.json, summarized):** Neither as a blanket rule. The
marginal-impact case is usually stronger for a foundation: a $100M pool is a
rounding error against large schools' budgets, while small struggling schools
may lack the capacity to convert money into outcomes. Favor schools with
demonstrated ability to convert resources into outcomes, where the grant is
material relative to scale — mid-sized schools with decent but improvable
outcomes.

**How the reply became work:** introduced the materiality term and the
diminishing-returns lift. Selection score S_i = 0.45*rank(potential) +
0.35*rank(marginal completions per $M) + 0.20*rank(materiality), with
materiality M_i = 1 - exp(-(100/K)/B_i) and B_i = UGDS_i*COST_STU_i/1e6;
realized lift dC*_i = dC_i*(1 - exp(-g_i/B_i)). Allocation capped every grant
at 20% of school budget. This changed the top of the list from largest
schools to the mid-sized mix in results/selected_K30.csv.

## Exchange 3 (builds on exchange 2: how many of the mid-sized schools can actually be managed)

**Question (expert_question_3.md):** A foundation has $100 million a year for
five years. Roughly how many colleges should receive money in a year for the
foundation to actually manage the grants and check results?

**Reply (expert_reply_3.json, summarized):** A workable annual cohort is
roughly 20 to 50 schools, with about 30 as the practical center, driven by
grant-management capacity (program officers manage ~10-20 active grants each).
At 30 schools the average grant is ~$3.3M/year — material to a mid-sized
institution; at 100+ schools oversight becomes superficial.

**How the reply became work:** fixed K = 30 schools per year, so base grant
= 100/30 = $3.33M, matching the expert's materiality band. Sensitivity sweep
K in {20,30,50} (logs/model_sweep.log) confirms the conclusion is stable
across the 20-50 interval the reply supports; K=30 chosen as the working point.
