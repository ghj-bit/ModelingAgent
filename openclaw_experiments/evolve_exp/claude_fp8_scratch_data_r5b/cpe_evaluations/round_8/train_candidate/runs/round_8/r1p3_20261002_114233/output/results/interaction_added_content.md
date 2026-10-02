# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — Problem 2023_C (Wordle)

Three expert exchanges, one question each, in sequence. Question files:
`logs/operator_feedback/expert_question_N.md`; controller-managed request/reply
files: `logs/operator_feedback/expert_request_N.json`,
`expert_reply_N.json`.

## Exchange 1 — operational mechanism of the reported-results count

**Question (short form):** Whether the daily number of posted Wordle scores
depends more on how hard that day's word was, or on whether it was a weekend.

**Expert reply (key points):**
- Day-of-week/leisure time is the primary, more reliable driver: posting is a
  daily social ritual that happens more in free time (weekends/holidays).
- Word difficulty is a real but secondary, noisier effect, working in both
  directions (easy words → more "got it in 2" brags; very hard words → more
  failures and some non-posting).
- Empirical judgment: the weekly cycle is a swing on the order of tens of
  percent; difficulty effects are a smaller fraction of that.

**How the reply shaped the work:**
- Model choice for subproblem 1: day-of-week dummies retained in the count
  model as the structurally primary explanatory variable, with the time trend
  (measured decay, R² = 0.883) and a difficulty adjustment as secondary terms —
  matching the expert's stated hierarchy rather than dropping the weekday terms
  because their 2022 amplitudes were statistically small.
- Framing of the prediction interval: the interval was presented around a
  trend+weekday prediction, with the weekday effect noted as structural but
  small in this sample.

## Exchange 2 — causal reading of hard days (volume vs failure share)

**Question (short form):** On a hard day, do fewer people post at all, or do
the same people post with a higher failed-result share?

**Expert reply (key points):**
- Fewer people post at all — selective non-posting: people who fail are less
  likely to share than people who succeed.
- Both effects occur at once (volume falls, X-share rises), but the volume
  effect is smaller and noisier; the X-share shift is the cleaner, more
  reliable difficulty signal because it is measured within the fixed pool of
  people who did post.
- Empirical judgment: a hard day brings a modest count decline (a few percent
  to low tens of percent) plus a clear rise in X-share.

**How the reply shaped the work:**
- Subproblem 3 (difficulty classification): the label is the X-share
  (failure rate), not the count, and the write-up explicitly justifies this
  choice by the selective-non-posting mechanism — the count is diluted by
  routine posters who post regardless of outcome.
- Subproblem 2 (distribution prediction): the X category of the predicted
  distribution is treated as the decision-relevant output (it is what the
  expert said carries the difficulty signal), and its MAE (2.16 pp) is the
  number compared against the Exchange 3 threshold.
- Subproblem 1 analysis: the small measured difficulty→count effect in the
  data (Xshare coefficient in the logN model, p = 0.43) is consistent with the
  expert's "smaller and noisier" judgment; the model does not force a larger
  difficulty term.

## Exchange 3 — decision-relevant uncertainty threshold

**Question (short form):** How accurate must a predicted failure rate be for
it to be usable by the NYT when planning a puzzle — at what error size does it
stop being actionable?

**Expert reply (key points):**
- A predicted X-share is useful if accurate to about ±2 to ±3 percentage
  points.
- Rationale: X-share typically runs ~1–2% on easy words to ~10–20% on the
  hardest, most days in the low single digits; ±2–3 pp is small relative to
  that spread and still separates an easy day from a hard day.
- At ±5 pp or more the prediction can no longer distinguish hard from easy and
  is no longer actionable.
- Explicitly an empirical judgment, not a precise figure.

**How the reply shaped the work:**
- Subproblem 2 confidence statement: the model's in-sample MAE for X-share is
  2.16 pp, so the EERIE X prediction (2.9%) is reported as usable within the
  expert's ±2–3 pp planning threshold, while the middle categories (3–6 tries,
  MAE 4–5 pp) are reported as only rough — i.e., the confidence statement is
  split by category against the expert's threshold rather than given as one
  blanket number.
- Subproblem 3: the ±2–3 pp threshold is quoted in the accuracy discussion as
  the decision-relevant standard for the difficulty classifier's output.

## Compliance notes
- Exactly 3 exchanges, one question each, each question ≤ 20 words of direct
  ask, each later question built on the previous reply (Q2 builds on Q1's
  "difficulty is secondary" finding; Q3 builds on Q2's "X-share is the cleaner
  signal" finding).
- No question asked for coding, debugging, computation, or mathematical
  derivation help.
- No expert sentence is copied into `results/solution.json`; the values that
  traveled into the submission are: the DOW-primary/difficulty-secondary
  hierarchy (Exchange 1), the X-share-as-difficulty-label choice and
  selective-non-posting rationale (Exchange 2), and the ±2–3 pp usable /
  ±5 pp unusable threshold with its X-share range (Exchange 3).
