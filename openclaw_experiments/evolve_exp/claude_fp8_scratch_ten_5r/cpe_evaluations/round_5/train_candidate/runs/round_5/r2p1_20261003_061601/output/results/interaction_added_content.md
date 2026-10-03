# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — 2023_C (MM-Bench Wordle)

Ten expert exchanges. For each: the question, the substance of the reply, and the
concrete change it produced in the model/code. The reply is input, not content —
only the parameter, constraint, or decision rule travels into the submission.

## Exchange 1 — dominant driver of daily count swings
- **Q:** Word-novelty vs. the social calendar as the dominant driver of the
  day-to-day swing in reported counts.
- **Reply (substance):** The social calendar dominates; reporting is a habitual
  social-sharing act whose volume tracks routine (holidays, weekends). Word
  novelty is a secondary, smaller effect that operates on a base the calendar
  has already set.
- **Effect on work:** Set the model hierarchy for subtask 1 — the count model is
  built around calendar (day-of-week + holiday) effects as the primary
  explanatory block, with the word effect included as a small secondary term.
  This is the structural decision that the whole subtask 1 framework rests on.

## Exchange 2 — size of calendar swings and the word bump
- **Q:** Rough magnitudes: how much do holidays/weekends dip the count vs. a
  normal weekday, and how large is the newsy-word bump?
- **Reply (substance):** Major holidays cut counts by ~20–40% vs. an adjacent
  weekday; ordinary weekends ~10–20% below; a common/newsy word nudges the count
  up only ~5–15%. Calendar effect is ~2–4× the word effect.
- **Effect on work:** Gave the order-of-magnitude prior used to sanity-check the
  fitted coefficients. The fitted holiday effect in the data is a large dip and
  the word effect is a small positive — consistent with this range. These are
  the empirical ranges recorded in the parameter table of the submission
  (interval [0.05, 0.40] for calendar dip magnitude; [0.05, 0.15] for the word
  bump), sourced to this exchange.

## Exchange 3 — what drives the hard-mode fraction
- **Q:** Is the hard-mode *fraction* driven by the word (repeated/unusual
  letters) or is it a stable player-mix property with the word having almost no
  effect?
- **Reply (substance):** The fraction is mostly a stable self-selected player
  mix; both numerator and denominator dip together on holidays/weekends, which
  is why the hard-mode *count* tracks the total. Word effects on the fraction
  are real but small (a few percentage points at most, hard to separate from
  noise).
- **Effect on work:** Defined the null hypothesis for subtask 2: the hard-mode
  fraction should be far less volatile than the count and only weakly
  word-dependent. The logit test (word block p-values all > 0.8, time trend the
  real driver) confirms this — the answer to subtask 2 is "word attributes have
  at most a negligible effect on the fraction."

## Exchange 4 — what makes a word hard
- **Q:** For the solve distribution, does rarity (unfamiliar word) or letter
  structure (repeats / missing common letters) matter more?
- **Reply (substance):** Letter structure clearly dominates; rarity is
  secondary. Repeated letters and absence of common letters mechanically break
  the standard probe strategy and push mass into 5/6/X. Rarity adds only a
  modest tail.
- **Effect on work:** Set the feature set for the subtask 3/4 models to
  letter-structure attributes (n_rep, max_mult, n_common, n_vowel) rather than
  any rarity/frequency proxy. This is the structural choice for the difficulty
  classifier.

## Exchange 5 — distinctive patterns to expect
- **Q:** One or two recurring, distinctive patterns in a year of Wordle
  statistics that would surprise a first-time reader.
- **Reply (substance):** (1) The 6-try bucket is a "cliff-edge" quantity that
  rises on hard days and moves with X (unsolved); (2) repeated-letter words
  (esp. repeated vowels like EERIE) show a fatter tail (more 5/6/X) and a lower
  3-try share.
- **Effect on work:** Defined the two patterns to verify in subtask 5. Both were
  confirmed in the data: corr(6try, X)=0.655, 6-try share 16.1% (hard half) vs
  7.0% (easy half); repeated-letter words have 3-try 18.0% vs 24.6% all-unique
  and X 4.0% vs 2.3%.

## Exchange 6 — where prediction confidence sits
- **Q:** For an unseen future word, is the middle of the distribution (3,4
  tries) more predictable than the tail (6, X), or does it vary as much?
- **Reply (substance):** The middle is much more predictable; the tail is where
  word-to-word variance lives and is driven by the structural features that
  break the standard strategy. The 6-try and X buckets are coupled (both
  inflate together on hard words).
- **Effect on work:** Guided the uncertainty reporting in subtask 3 — the
  per-bucket CV intervals are reported with the expectation (and the data show)
  that the tail buckets (6, X) have wider spread than the middle (3, 4). This
  is the basis for the confidence statement: pin the middle tightly, attach
  most of the predictive uncertainty to the tail.

## Exchange 7 — extrapolating the 2022 trend to March 2023
- **Q:** When extrapolating the 2022 count trend to 2023-03-01, does the growth
  pace stay steady or decelerate/flatten as the puzzle matures?
- **Reply (substance):** Growth decelerates and flattens toward a plateau; do
  NOT extrapolate the 2022 multiplicative pace. The 2022 rise is the steep part
  of an adoption S-curve; the reporting base is finite. A March 2023 prediction
  should sit near or modestly above the late-2022 level, not on a straight-line
  continuation of the year's slope.
- **Effect on work:** This is the key structural constraint on the subtask 1
  forecast. The 2022 data show a *declining* count (post-viral decay), so the
  forecast anchors on the stable late-2022 level (last-30-day mean) and applies
  only a *decelerated* (halved) decay slope rather than the full 2022 slope.
  The full-slope linear extrapolation is reported as a bound, not the point
  estimate.

## Exchange 8 — structural difficulty vs. "would I have guessed it"
- **Q:** Is a word's "difficulty" (as a pre-play classification) based on letter
  structure alone, or does it also mix in familiarity/unexpectedness — i.e.
  should the easy/medium/hard label merge the two, or keep them separate?
- **Reply (substance):** They are two separate ideas. Structural difficulty is
  a property of the word's letters alone, knowable before anyone plays.
  "Would I have guessed it" is a familiarity judgment that shows up mainly as a
  modest tail effect. For a pre-play classifier, build it on structural
  attributes and treat rarity as a distinct, secondary feature — do not merge
  them.
- **Effect on work:** Confirmed the subtask 4 design: the easy/medium/hard
  classifier is built purely from structural attributes (n_rep, max_mult,
  n_common, n_vowel); rarity/familiarity is not folded into the label.

## Exchange 9 — day-to-day noise on a plain weekday
- **Q:** On a single plain, non-holiday weekday (like 2023-03-01), is the count
  mostly the stable committed core, or is there noticeable day-to-day noise on
  top, and roughly how big?
- **Reply (substance):** The committed core sets the level (fairly stable day to
  day), but there is real day-to-day scatter on top — order of roughly 5–15%
  (one standard deviation) around the local trend, versus 20–40% holiday dips.
  A single plain day should land near the trend level with a band of that size,
  not a tight point value.
- **Effect on work:** Set the width of the prediction interval for the
  2023-03-01 count. The model's residual standard deviation (in log units) is
  used to build the 80% and 95% prediction intervals, and the reported band is
  checked against this ~5–15% (plain-day) / 20–40% (holiday) order of
  magnitude. Recorded in the parameter table as the day-to-day noise interval.

## Exchange 10 — how to read difficulty from the percentages
- **Q:** When judging a day's ease/hardness from the 1..6/X percentages, rely on
  the aggregate distribution shape or a single number; if one number, which?
- **Reply (substance):** Judge by the aggregate shape of the whole distribution,
  not a single number. If forced to pick one, X (unsolved) is the cleanest
  single screen, but it is a coarse proxy and noisy at small values; the 6-try
  share is a useful companion because it moves with X.
- **Effect on work:** Set the validation metric for the subtask 4 classifier:
  classes are validated by the *shape* of the observed distribution (mean tries,
  3-try share, 6-try share, X share) rather than a single bucket, with X used as
  the primary quick screen. The ANOVA on X% (p=2e-3) and mean tries (p=1.3e-18)
  is the accuracy discussion.
