# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert interaction evidence — MM-Bench 2023_C (Wordle)

Three exchanges, one question each. Question/reply files in `logs/operator_feedback/`.
Each reply is recorded below as a parameter/constraint used by the model in
`code/wordle_model.py` (values, not prose), and in `results/solution.json`.

## Exchange 1 — operational definition of "Number of reported results"

Question: does the column count only people who posted on Twitter, so a low day
may mean fewer posters rather than fewer players?

Reply: yes — it is a count of scores mined from Twitter, i.e. only people who
actually posted that day; not the total player base. Day-to-day variation
therefore reflects posting/reporting behaviour and general Twitter activity,
not the total player base (which is far larger and unobserved).

How the reply entered the work:
- **Interpretation constraint (E1):** the dependent variable `N` in the count
  model is a *posting count*, so the model is explicitly framed as a model of
  reporting behaviour, not of the player population. Stated as an assumption in
  solution.json subtask 1 and as the first limitation.
- **Model structure:** this is what makes a *trend + weekday* model (posting
  behaviour) the right object rather than a demand model; the model is not
  claimed to recover total play.

## Exchange 2 — dominant driver of count variation

Question (building on E1): on high-posting days, what drove the extra posting —
the word's difficulty, or the day/game buzz?

Reply: both, but the dominant driver is the day/game-buzz factor (viral waves,
media coverage, holidays/weekends, peak popularity in early 2022), which
produces broad sustained increases; word difficulty adds only a smaller,
short-lived single-day increment.

How the reply entered the work:
- **Model structure (E2):** the count model `log N = a + Σ b_dow·1[dow] + c·t`
  carries the dominant effects (weekday, slow trend/buzz) but deliberately
  *excludes* a word-difficulty regressor, because per the reply the
  difficulty effect on the count is a minor one-day bump; a 359-day series has
  no statistical power to resolve it and including it would only add noise.
- **Prediction choice:** the March-1-2023 point estimate is anchored to the
  *stable late-2022 posting regime* (the last 100 days, 22 Nov – 31 Dec 2022),
  not to the viral peak, because the dominant driver (buzz) had already
  stabilised by then and the target is 60 days past the end of the observed
  window.

## Exchange 3 — robustness / decision threshold

Question (building on E2): when is a future-day forecast trustworthy, and what
sign says it is mainly noise?

Reply: trust a forecast when the target date sits in a stable, well-established
posting regime (smooth recent trend, not near a known external event); treat it
as noise when the underlying history is volatile, the date is far outside the
observed window, or the forecast's uncertainty interval is as wide as or wider
than the typical day-to-day variation (so the point estimate carries little
information).

How the reply entered the work:
- **Robustness rule (E3), operationalised as a computed test:** the 95% PI width
  for 2023-03-01 is compared to the median absolute day-to-day change in the
  stable window. `e3_flag = (hi − lo) ≥ median|ΔN|`.
  - Computed: PI = [8520, 20699], width = 12179; median|ΔN| (stable window) =
    1451 → **e3_flag = True** → the forecast is flagged as *low-confidence /
    largely noise-sensitive*, and this is reported as the model's confidence
    statement rather than a false precision claim.
- **Honest confidence:** because the target (Mar 1, 2023) is 60 days past the
  data end and past the popularity peak, the submission states the point
  estimate is only weakly informative and the interval is the operative
  quantity; no narrower interval is asserted.

All three exchanges produced a concrete parameter/constraint/test above; none
is quoted verbatim in the submission, and none stands in for a computation.
