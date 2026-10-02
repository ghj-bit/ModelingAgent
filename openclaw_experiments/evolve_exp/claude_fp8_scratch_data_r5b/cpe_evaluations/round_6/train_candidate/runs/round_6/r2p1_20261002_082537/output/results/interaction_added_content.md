# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — MM-Bench 2020_C

Three expert exchanges, one question each, sequenced to isolate the
data-generation selection mechanism, then the temporal/state structure it
implies, then the bias-aware interpretation threshold. Each reply was
converted into a concrete constraint in the model before the next exchange.

## Exchange 1 — Selection mechanism (data generation)

**Question (expert_question_1.md):** Do most Amazon buyers simply never vote on
review helpfulness, so a zero-vote review tells us nothing about the review's
or product's quality?

**Reply (expert_reply_1.json):** Yes — voting is a small-minority behavior; the
modal review legitimately has zero votes, reflecting low exposure (few views,
recent, obscure product), not poor quality. Qualification: zero votes are not
pure noise — votes accumulate with exposure and age, so zero/nonzero carries
information about *visibility and timing*, not quality. Treat helpful_votes as
a **censored, exposure-driven count, not a quality score**.

**How it changed the work (became a model constraint):**
- Parameter/constraint `E1`: all helpfulness metrics are computed **only over
  voted reviews (total_votes > 0)**; `helpful_rate = mean(helpful/total)` over
  that sub-population, and `voted_frac = P(total_votes>0)` is reported as an
  exposure indicator. Implemented in `analyze.py:category_metrics`.
- Decision rule: `helpful_votes` is **excluded** as a headline quality KPI in
  the tracking task and the success/failure task; it is reported only as a
  visibility modifier. Without this constraint the analysis would have treated
  the modal zero as a "no helpfulness" quality signal, biasing every
  helpfulness-by-star table.
- The constraint holds over the whole 2002-2015 window and all three
  categories (voted_frac 37.7% / 66.9% / 28.0% confirms the zero is structural,
  not missing-at-random).

## Exchange 2 — Temporal / state-dependence structure

**Question (expert_question_2.md):** When a popular product's average star
rating steadily falls over several years, is that a real lasting product
decline, or mostly shoppers' expectations rising (a shifting standard)?

**Reply (expert_reply_2.json):** No — a multi-year fall is usually **not** a real
product decline and only partly rising expectations. The dominant cause is
**compositional change in who reviews and which listing is rated**: early
enthusiastic adopters are replaced by mainstream then marginal buyers, and a
product_parent aggregates a long window during which the item may be
reformulated, re-sourced, or sold by third parties. Rising expectations is
secondary and hard to separate from cohort composition. A falling average is
best read as a change in the *reviewing population and listing history*, not
that the product got worse.

**How it changed the work:**
- Constraint `E2`: the temporal-reputation model fits a review-count-weighted
  quarterly trend and labels any slope as a shift in the *reviewing population
  / listing history*, never as physical product degradation. Implemented in
  `analyze.py:temporal_reputation`.
- The model normalises review flow against expected volume (weighted regression
  on quarter, min 20 reviews/quarter) instead of reading raw mean-star drift as
  a quality trajectory. This directly re-framed the microwave result: the
  strong positive slope (+0.075/quarter) is interpreted as the review
  population stabilising, not the product improving in a physical sense.
- Holds over the quarterly window with n_q>=20 in all three categories.

## Exchange 3 — Bias-aware signal threshold

**Question (expert_question_3.md):** Judging a new product against established
category peers, how large and how consistent a star-rating gap would you want
before trusting it as a real signal rather than noise?

**Reply (expert_reply_3.json):** Roughly a **0.3-0.5 star gap sustained over at
least several months and a few dozen reviews** before it is real; gaps under
~0.2 are within small-sample and cohort-mix noise, and a gap that swings back
and forth across months is not a signal regardless of size.

**How it changed the work:**
- Constraint `E3`: a numeric robustness threshold `THR = 0.3` (with 0.5 as the
  upper end of the stated range) is hard-coded in `analyze.py`
  (`gap_meets_03_threshold = abs(gap) >= 0.3`) and applied to every temporal
  gap and cross-category comparison. A finding is labelled "real" only if
  |gap| >= 0.3 AND sustained (low month-to-month variance) over >= 3 months
  with >= ~30 reviews/month; otherwise "noise".
- Applied results: hair gap -0.068 -> noise; microwave gap +0.195 -> improving
  but **below** 0.3, so "not yet confirmed"; pacifier gap -0.036 -> noise.
  Descriptor gaps (disappointment -1.73 to -1.84, enthusiasm +0.35 to +0.78)
  are all far above 0.3 on large n -> robust. This threshold is what separates
  the actionable recommendations (letter, task 6) from statistical noise.
- The threshold is qualitative common-sense (from the expert's practical
  judgment), used as a decision boundary, not as a fitted parameter.

## Notes on what the exchanges did NOT supply

No empirical numeric value the model needed was taken from memory or from the
expert. The only numbers that entered the model from outside the dataset are
the threshold 0.3-0.5 (a decision boundary from exchange 3) and the
interpretive labels from exchanges 1-2; every other statistic in
solution.json is computed from the three supplied TSV files. The expert replies
are input only — no reply text is copied verbatim into solution.json.
