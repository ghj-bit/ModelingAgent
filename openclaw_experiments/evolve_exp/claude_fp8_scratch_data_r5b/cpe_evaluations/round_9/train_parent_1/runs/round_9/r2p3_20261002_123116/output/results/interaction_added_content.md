# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence

Three exchanges, one question each, in `logs/operator_feedback/`.

## Exchange 1 — operational mechanism
**Question:** Wordle players post scores to Twitter after playing. Do these daily
reported results arrive as a steady, uniform stream through the day, or in
bursts tied to the day's schedule (morning routine, lunch break, commute)?

**Reply (summary):** Bursts, not a steady stream. Wordle releases at midnight;
the dominant pattern is a morning-routine spike, with smaller lunch/evening
bumps, strongly front-loaded on release day. The daily count reflects who
played-and-posted that day, driven by weekday/weekend routine differences
(weekends shift and flatten the peak), not a constant arrival process.

**Effect on work:** The count model (Part 1) treats the daily count as a
non-constant mean driven by calendar (day-of-week dummies) plus a time trend —
not a uniform arrival rate — and keeps weekend coefficients separate from
weekday ones. Used in `code/model_wordle.py`, `q1_count_model`.

## Exchange 2 — causal hierarchy
**Question:** On days when more people report scores, is that because the puzzle
was genuinely easier, or because the day's word is simply a word more people
recognize and therefore feel confident posting?

**Reply (summary):** Both are real, but recognition/confidence dominates
genuine difficulty. The count is a self-selected sample (people post when they
solve, especially in few tries); a common, familiar, easy-to-spell word draws
more players and more posting. Easier words also raise the solve rate, so the
two are correlated and hard to separate. Non-word factors — weekday/weekend
routine, virality, the growing/decaying 2022 Twitter base — often move the
daily total more than intrinsic difficulty.

**Effect on work:** (Part 1) word features are treated as secondary relative to
trend + calendar. (Part 2) word attributes enter the hard-mode logit as
plausible but confounded drivers, and significance is reported with that
caveat. (Part 3) the difficulty signal is taken from the try distribution
(fewer self-selection artifacts) rather than the raw count.

## Exchange 3 — decision-relevant threshold
**Question:** If the New York Times uses this model to plan how many players to
expect on a future day, roughly how far off would the predicted count be before
it stops being useful for that planning?

**Reply (summary):** Usefulness is decision-relative, not a fixed statistical
threshold. Counts run from tens of thousands to a few hundred thousand. An
interval of roughly +/-20-30% of the point estimate is usable for coarse
planning; beyond about +/-50% it spans nearly a factor of two and no longer
distinguishes a normal day from a busy one. A word-attribute-only model would
plausibly sit at +/-30-50% on a future day, i.e. borderline.

**Effect on work:** The March 1, 2023 interval half-width (+46.5% / -31.7% of
the 9,193 point) is reported explicitly against this band: the upper half-width
sits at the borderline of planning usefulness, so the forecast is framed as
planning-grade, not operational-grade. It also justifies the log-scale interval,
whose natural error unit is a percentage of the estimate.
