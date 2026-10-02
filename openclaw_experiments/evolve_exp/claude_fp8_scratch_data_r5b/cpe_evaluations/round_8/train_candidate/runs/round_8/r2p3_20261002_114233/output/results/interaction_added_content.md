# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — Problem 2023_C (Wordle)

Three expert exchanges, one question each, asked before the work they governed.

## Exchange 1 — Operational mechanism of the count decline

**Question:** When did Wordle's reported score counts on social media start falling through 2022 — a steady daily fade, or did specific news events cause sudden big drops?

**Reply (summary):** The series shows a steady, gradual fade, not event-driven cliffs. It starts near its peak in January 2022 (post-acquisition virality peak) and declines smoothly, with the largest single drop in the first weeks as the novelty spike decayed. Ordinary day-to-day noise and a mild weekly rhythm (weekends/holidays lower) sit on top. No 2022 news event visibly severed the series.

**How it changed the work:** Fixed the structural form of the subtask-1 model. Instead of considering event dummies, regime breaks, or interrupted time series, the count model is a single exponential decay trend (log N_t = b0 + b1·t) plus day-of-week dummies, with no event terms. The expert's "mild weekly rhythm" confirmed the 6 weekday dummies; the "no cliffs" statement removed the need for break detection. Source: exchange 1; validity interval: the 2022 sample and the 60-day extrapolation to 2023-03-01.

## Exchange 2 — Causal direction of word attributes vs Hard Mode

**Question:** Do casual Wordle players pick Hard Mode based on how the day's secret word looks, or do they choose it by personal habit?

**Reply (summary):** Personal habit dominates. Hard Mode is a persistent per-player toggle, set once and kept, so the day's word has essentially no direct influence on whether a given player is in Hard Mode. The word can only shift the reported hard-mode share indirectly (e.g. hard words causing some habitual players to fail/skip reporting). The share is best viewed as a slowly varying player-base characteristic, not a function of word attributes.

**How it changed the work:** Set the hypothesis structure of subtask 2: the regression of hard share on time (player-base adoption) is the primary model, and word attributes enter only as tested secondary terms. The regression results (no word attribute significant, all p > 0.2; time trend highly significant) are then reported as confirmation of the habit mechanism rather than a surprise null result, and the "indirect only" channel is stated as the caveat. Source: exchange 2; validity interval: 2022 player behavior as reported on Twitter.

## Exchange 3 — Decision-relevant error threshold

**Question:** If the paper asks for next week's puzzle crowd size and you're off by 20%, would that forecast still be good enough?

**Reply (summary):** Yes. The count is a noisy self-selected Twitter sample, not a controlled measurement; day-to-day scatter is routinely tens of percent. A forecast within roughly ±20–30% captures the trend and scale correctly. Direction, order of magnitude, and an honest interval matter more than the exact number; a precise-looking point without an interval would be worse even if closer.

**How it changed the work:** (i) Set the validation criterion for subtask 1: the 28-day backtest is reported as MAPE 23.6%, 41% of days within ±20%, 72% within ±30% — judged against the expert's ±20–30% acceptability band rather than an arbitrary target. (ii) Set the reporting style: every prediction in subtasks 1 and 3 is given as point + interval, and the confidence statement in subtask 3 is framed relative to that band (central cells well inside ±20–30% relative; tails weaker). (iii) Rejected a "precision theater" alternative (narrowing the interval to look sharper) because the expert explicitly valued honest interval width over apparent precision. Source: exchange 3; validity interval: crowd-size forecasting use case for this dataset.

## Note on use of replies

No sentence, phrasing, or structure from any reply appears in solution.json. What was carried over is: the no-event-breaks trend form (exch. 1), the habit-based Hard Mode hypothesis and indirect-only caveat (exch. 2), and the ±20–30% relative accuracy acceptability criterion used to judge the backtest and to frame confidence statements (exch. 3) — all integrated as model structure, hypothesis, or evaluation criterion, in the solution's own formulation.
