# Interaction Evidence — 2016_C (Goodgrant $100M/yr × 5)

All three expert exchanges completed. Each reply was converted into a
concrete model component before the next exchange.

## Exchange 1 — structural validity

**Question (expert_question_1.md):**
"Past student performance as a gauge of how well a never-before-funded
school would use new grant money: fair gauge or not?"

**Reply (substance):** Past performance mostly reflects intake
(selectivity, family resources), not the school's capacity to convert
money into outcomes. Weak past performance can mean "doing well with
little"; strong performance can mean advantaged admits. For a first-time
grantee the fair gauge is (a) administrative/financial capacity to absorb
and deploy funds, and (b) a measurable gap between resources and outcomes
— evidence of being under-resourced rather than ineffective. Past
performance is, at best, a weak, confounded signal.

**How it changed the work:** The school score was built as
`Score = 0.6 · shortfall + 0.4 · capacity`, where *shortfall* is a
standardized gap between per-student outcomes and a like-for-like
peer benchmark (resource-controlled), and *capacity* proxies
administrative/financial deployment ability from size, program
breadth and retention. Raw performance levels were deliberately excluded
as a positive input: a high raw score is treated as possible advantaged
intake, and only the *negative* tail of raw outcomes enters, as part of
the shortfall signal. Weight 0.6/0.4 chosen so shortfall dominates,
consistent with the expert's ranking of the two signals. Sensitivity
of the funded set to a 0.5/0.5 vs 0.7/0.3 split is reported in
`subtask_outcome_analysis`.

## Exchange 2 — bias and validation

**Question (expert_question_2.md):**
"Schools can hide or withhold numbers — does that bias the published
records toward one kind of school, and which ones?"

**Reply (substance):** Non-reporting is systematic, not random. Withholders
are disproportionately small institutions, for-profits, weak-outcome
schools, and those lacking institutional-research staff. Large,
well-resourced, better-performing schools almost always report. Missingness
is correlated with the outcomes of interest: rankings built on reported
figures flatter reporters and silently drop many under-resourced schools —
exactly the population a foundation most wants to reach. Non-reporting is
informative, not a neutral gap.

**How it changed the work:** (1) Every standardized input carries a
completeness flag: missing outcome variables lower the school's *confidence*
rather than being imputed with peer means — a missing indicator can
increase, not decrease, its score because it is evidence of
weak administrative capacity (part of `capacity`), while a missing
outcome is capped: schools with missing core outcome data (debt or
earnings) are ranked no higher than the 40th percentile of fully
observed schools, an explicit uncertainty cap. (2) Validation design:
state-blocked leave-one-state-out cross-validation (51 states) instead of
random CV, because reporting rates and peer structures are state-specific;
reported is state-blocked re-ranking stability (Spearman ρ of within-state
ranks), not predictive accuracy on a held-out school, since there is no
future outcome to predict in the supplied data. (3) For-profit/very small
schools get a hard review flag (not auto-exclusion) so the list does not
silently drop them.

## Exchange 3 — decision threshold

**Question (expert_question_3.md):**
"How big a misjudgment in picking a school — in rank or expected benefit —
would be bad enough to abandon the recommendation?"

**Reply (substance):** No clean numeric threshold; the binding test is
rank error relative to the funding cutoff, not absolute rank error.
Tolerable if a school moves a few ranks but stays inside the funded set;
disqualifying if the error would swap a funded school for a materially
better unfunded one — i.e., uncertainty comparable to the gap between
adjacent candidates near the cutoff. If the uncertainty band is wider
than the spacing between the last funded and first unfunded school, the
recommendation is not defensible.

**How it changed the work:** The decision rule now reports, at the
funding cutoff, (a) the score gap Δ between the last funded and first
unfunded school, and (b) a bootstrap uncertainty band on each school's
score (500 resamples of the observed candidate schools within state,
preserving the missingness pattern). The recommendation is declared
defensible only where Δ exceeds the band width of the cutoff-adjacent
school; schools whose bands straddle Δ are listed as "borderline —
verify before funding" rather than ranked as if certain. Award amounts
are then allocated proportionally to score *within* the confident set,
and a small holdback (5% of annual budget) is assigned to borderline
schools as a verification tranche.

## Parameters sourced from the exchanges (not from memory or literature)

- Weight shortfall:capacity = 0.6:0.4 — exchange 1.
- Missingness-as-capacity signal and uncertainty cap at the 40th
  percentile of fully observed schools — exchange 2 (the cap percentile
  is a defensible implementation choice made explicit in the model).
- State-blocked leave-one-state-out validation — exchange 2.
- Cutoff-margin decision rule, Δ vs bootstrap band — exchange 3.

Empirical magnitudes (per-student grant effect) come from staged search,
not from these replies.
