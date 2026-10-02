# Interaction Evidence — MM-Bench 2023_C (Wordle)

Three expert exchanges, one question each, in the order prescribed by the
interaction policy. Each reply was turned into a concrete model component
before the next exchange was made.

---

## Exchange 1 — Structural fit of the solve-distribution data

**Question (expert_question_1.md):**
> In the Wordle Twitter data, the solve-count percentages (1, 2, 3, 4, 5, 6 tries,
> and X) come from the same day's players. If I predict them for a future word, is
> it right that they must stay a valid whole — never negative and always adding up
> to 100 — rather than being predicted as separate unrelated numbers?

**Expert reply (expert_reply_1.json):**
Yes. The seven percentages are a compositional vector: each is bounded in
[0, 100] and the seven must sum to 100 up to integer rounding. Predicting them
as seven independent regressions can produce negative values or sums far from
100, which are not valid outcomes. The constraint should be imposed, not
ignored — e.g. model on a simplex or normalise/clip predictions after fitting.
The data are rounded to whole percents, so exact sums may deviate by a fraction
of a percent; that rounding slack is the only legitimate departure.

**How the reply became work:**
- The seven OLS predictors for the try-count percentages are followed by a
  **clip-at-zero and renormalise-to-100 step** (`model.py`, Q2 block:
  `dist_pred = np.clip(dist_pred, 0, None); dist_pred = 100 * dist_pred /
  dist_pred.sum()`), so every published prediction is a valid composition.
  The same clip-and-renormalise is applied inside every bootstrap replicate,
  so the entire predictive distribution lives on the simplex.
- The solution.json (task 2, mathematical_modeling_process) records the
  simplex constraint and its source as this exchange.
- The data check `pct_rowsums` (100, 101, 99, 102, 98, 126) confirms the
  rounding slack the expert described; the one row summing to 126 is noted as
  an outlier in the cleaning description.

---

## Exchange 2 — Selection mechanism in the Twitter-reported data

**Question (expert_question_2.md):**
> Only some players post their score on Twitter. Do you think the people who
> post are the ones who struggled, the ones who solved it fast, or is it a fair
> mix?

**Expert reply (expert_reply_2.json):**
Not a fair mix — the skew is toward the fast/strong solvers. Posting is a
mild brag/share behaviour, so people who solved it (especially in few tries)
are more motivated to post than people who failed. The X (unsolved) share in
the Twitter data is almost certainly understated relative to the true player
base, and the 1–3 try shares are likely somewhat overstated. Two caveats: the
skew is not constant — on a hard word even strong solvers struggle, so the
composition of posters shifts with word difficulty; and the bias is a
reporting/selection effect, not a property of the word, so it should be
treated as a systematic distortion of the observed percentages rather than as
signal about difficulty. Empirical judgment: expect the true X rate to be
meaningfully higher than reported, but no reliable precise magnitude.

**How the reply became work:**
- The EERIE prediction in solution.json (task 2) carries an explicit
  **self-selection sensitivity band**: reported X point 9.36%, with the true
  X stated as likely higher and a sensitivity of up to +4 percentage points
  (X up to ~13%). The direction (X understated, 1–3 overstated) is recorded
  as the qualitative content of the bias, attributed to this exchange.
- The task-2 subtask_outcome_analysis names the bias as the model's main
  systematic error and explains why it interacts with word difficulty
  (posters shift on hard words), matching the expert's caveat.
- The task-3 analysis uses the difficulty score (mean tries) as the label
  rather than treating the Twitter percentages as an unbiased measure of
  player performance, consistent with the expert's "systematic distortion,
  not signal" framing.

---

## Exchange 3 — Interpretation criterion for extrapolating the count

**Question (expert_question_3.md):**
> Players post scores on Twitter. When you predict next month's Wordle score
> count, should you expect the game to have grown, shrunk, or stayed about the
> same since late 2022?

**Expert reply (expert_reply_3.json):**
Expect it to have shrunk — modestly, not dramatically. Twitter-posting volume
peaked in early 2022 (the January–April surge after the NYT acquisition) and
declined through the rest of 2022 as the novelty faded; the downward trend is
visible within the data file itself, so extrapolating a flat or growing count
into 2023 would be wrong. Qualifications: the decline is a slow decay, not a
collapse — the game retained a large stable base, so month-over-month drops
are on the order of a few percent, not tens of percent; and the count is also
driven by day-of-week and word difficulty, which can swamp the trend on any
single day. For March 1, 2023, expect a count somewhat below the late-2022
level, continuing the mild downward drift; no reliable precise rate.

**How the reply became work:**
- The March 1, 2023 prediction (task 1) is built on a **downward** trend,
  never on a flat or growing one. The last-90-days log-linear trend
  (-3.49%/week) is used as the primary point estimate (≈14,689) precisely
  because it reflects the recent, milder decay the expert described, while
  the full-year trend (-5.36%/week → ≈9,193) is reported as the
  conservative lower alternative. The spread between the two is stated as
  the main uncertainty.
- The expert's "a few percent per month, not tens" judgment is checked
  against the data: the recent monthly step (Nov→Dec, 25,953 → 22,154, ≈
  -14.6%) is larger than "a few percent", and this tension is surfaced in
  the solution (task 1 outcome) rather than hidden — the model's PI is
  flagged as likely too narrow for the same reason.
- The day-of-week and difficulty effects the expert says "can swamp the
  trend on any single day" are exactly the terms in the count model (dow
  dummies; and the task-4 finding that count is uncorrelated with X,
  r = 0.033), so the model structure matches the expert's qualitative
  account.

---

## Summary of where each exchange lives in the submission

| Exchange | Constraint / value it supplied | Where used |
|---|---|---|
| 1 | Simplex: 7 percentages ≥ 0, sum 100 (±rounding) | clip + renormalise in `model.py` Q2 (incl. bootstrap); task 2 process field |
| 2 | Self-selection: X understated, 1–3 overstated; varies with difficulty; not a word property | X sensitivity band (+4 pct) in task 2; label choice in task 3 |
| 3 | Count must be predicted on a mild downward drift, not flat/growing; dow/difficulty swamp the trend | recent-90d trend as primary PI anchor in task 1; conservative full-year alternative; dow terms in count model |

No expert sentence is copied into solution.json; only the constraints,
directions, and values above travel, in the model's own formulation.
