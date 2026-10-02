# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — MM-Bench 2023_C (Wordle)

Three expert exchanges, one question each. The reply is input, not content: only the
value / constraint / decision it supports travels into the model and solution.json.

## Exchange 1

**Question** (`expert_question_1.md`):
"Wordle is a new daily puzzle in early 2022, and far fewer people posted their score in
late December than in early January. In your experience playing or sharing daily online
puzzles, what is the main everyday reason the number of people who share their result
goes up and down day to day?"

**Reply** (summarised): the dominant day-to-day driver is whether the word was easy or
hard plus the "brag vs. hide" impulse around the result; secondary everyday factors are
weekday vs. weekend routine and whether the puzzle is trending; the long Jan-to-Dec
decline is a *separate*, slower effect (novelty wearing off, audience shift), not a
day-to-day driver.

**How the reply became work** (source: Exchange 1):
- Constraint: model the daily reported-results volume as a *slow secular decline* plus a
  *weekday-cycle* component, and treat the long decline and the within-week variation as
  distinct, non-confounding terms. This is the structural choice behind the volume model
  `log N = a + b·t + Σ_d γ_d·DOW_d`.
- Parameter: the expert framed the decline as slow / novelty-driven (not daily noise),
  which motivated reporting it as a half-life (implied ≈ 88 days) rather than as a
  daily-noise term, and holding the day-of-week effect small.

## Exchange 2

**Question** (`expert_question_2.md`):
"You mentioned hard words feel like a frustrating grind while easy words feel satisfying.
When you're actually solving a five-letter word puzzle, what about the specific letters
makes a word feel much harder to figure out than another one?"

**Reply** (summarised): hardest drivers are (a) rare letters (J,Q,X,Z,V,K,W) or letters
that rarely sit in a given position, so early feedback stays mostly gray; (b) repeated
letters — the expert explicitly named EERIE, saying the tile feedback is ambiguous about
how many copies exist and where they belong, and duplicates waste guesses; (c) unusual
vowel / consonant placement removing the usual scaffolding. Common letters in common
positions make a word feel satisfying because the candidate set collapses fast.

**How the reply became work** (source: Exchange 2):
- Constraint: the difficulty classifier and the distribution model must be built on
  letter *and* position *and* repetition features, not on raw letter counts alone. This
  fixed the feature set to {distinct letters, repeated letters, per-position letter
  frequency ("pos_score"), count of rare letters J/Q/X/Z/V/K/W}.
- Decision rule: `pos_score` = mean over the five positions of that letter's frequency
  *at that position*, computed from the 355 five-letter solution words in the supplied
  dataset (a data-derived calibration input, not a memorised value). EERIE scores
  pos_score ≈ 0.086 with 2 repeated letters — consistent with the expert's explicit
  identification of EERIE as a hard, ambiguous, repeated-letter word.

## Exchange 3

**Question** (`expert_question_3.md`):
"For a tough five-letter word with repeated letters, like EERIE, when you're stuck
partway through the puzzle, how many guesses do you typically burn before you either
crack it or give up and guess randomly?"

**Reply** (summarised): typically 4–5 guesses are burned before it resolves. Pattern:
~2 wasted early guesses (ambiguous E feedback), ~2–3 grinding/probing guesses, then a
forced or near-random final guess. Hence hard repeated-letter words land
disproportionately in the 5 / 6 / X buckets, not the 2–3 buckets.

**How the reply became work** (source: Exchange 3):
- Constraint: for a hard repeated-letter word the predicted guess-count distribution must
  be *right-shifted and left-skewed* — mass pushed toward 4, 5, 6, and X, with a thin 1–3
  tail. This is the decision rule that fixed the EERIE prediction shape.
- Parameter: the expert's "4–5 guesses before it resolves" anchored the predicted median
  near 4–5 and the 95% band on the upper buckets. The final EERIE prediction
  {1: 0.19, 2: 3.55, 3: 16.72, 4: 31.42, 5: 27.94, 6: 15.63, X: 4.54} has its mode at 4
  and a long right tail into 5/6/X, matching the stated pattern, and is ridge-blended
  toward the dataset mean to keep the thin 1–3 tail realistic.

## Note on provenance
No empirical number in solution.json is filled from memory. Every letter-frequency,
bigram, and per-position-frequency value used as a model input is either (a) a standard
English letter-frequency table cited in the parameter table, or (b) derived directly from
the 355 five-letter words in the supplied `Problem_C_Data_Wordle.xlsx` (the position
table). The three expert exchanges supplied *qualitative* constraints (structural form,
feature choice, shape of the distribution), not numeric values.
