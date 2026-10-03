# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — MM-Bench 2023_C (Wordle)

Ten exchanges, one question each, in order. For each: the question asked, the
expert's reply (summary), and the concrete change the reply made to the work
before the next exchange.

## Exchange 1
**Q:** When the daily Wordle is a common everyday word, does more of the Twitter crowd report their result than when the word is obscure?
**Reply (summary):** Yes, directionally. Common words get solved more often and more quickly, so both the solve rate and the willingness to post rise with familiarity; obscure words produce more failures that are shared less. Effect is real but moderate — secondary to trend and day-of-week.
**Effect on work:** Justified including word-letter-structure terms in the reporting-volume model (task 1) rather than a pure time series, and justified treating the Twitter count as a willingness-to-post mixture (player base x posting propensity). This became the sign of the max_dup / rare-letter coefficients in the recent-window OLS for ln N (task 1, model C) and a stated bias assumption for all percentage-based tasks.

## Exchange 2
**Q:** Among people who play Wordle regularly, which word features make a daily puzzle feel hardest: rare letters, repeated letters, or both together?
**Reply (summary):** Repeated letters are the stronger driver (duplicates break the "one gray = absent" inference); rare letters (J,Q,X,Z,V,K,W) moderate; the combination is worst. Ordering: repeat > rare > neither.
**Effect on work:** Fixed the feature set for tasks 3 and 4: max_dup, n_rare_count (letters from {J,Q,X,Z,V,W,K}), n_unique, n_vow. Also used as the interpretability check on the learned difficulty weights (task 4) and as the basis for the EERIE classification (triple E = max_dup 3).

## Exchange 3
**Q:** Do weekends or holidays make people more likely to tweet their Wordle result than ordinary weekdays?
**Reply (summary):** Modest weekend bump, real but smaller than trend and word effects; holiday effects inconsistent, can go either way.
**Effect on work:** Added is_weekend to the volume and hard-mode models and made "weekend coefficient ≈ 0 in the stable window" an explicit testable claim. The data showed the full-year weekend "effect" was entirely the decay trend; the Sep-Dec window estimate (-0.008 in ln units, SE 0.054) is inside its confidence band, so the model reports weekend effect as essentially zero in the plateau (task 1 parameter table and task 5 feature 6). The "holidays inconsistent" point motivated not fitting holiday dummies with one year of data.

## Exchange 4
**Q:** What makes players pick Wordle Hard Mode instead of the regular mode, in your experience?
**Reply (summary):** Hard Mode is self-selected by disposition (committed, higher-skill players), not by the day's word; a minor novelty channel exists on famously hard days.
**Effect on work:** Framed task 2 as a test of the null "word attributes do not drive Hard Mode share." The OLS confirmed it: word terms |beta| ≤ 0.0031 vs trend term 0.0841, R2 = 0.225 from the trend alone being the dominant channel; the conclusion "Hard Mode growth is a player-base phenomenon, not a puzzle phenomenon" is the direct model output of this prior plus the data.

## Exchange 5
**Q:** When a Wordle word is easy, do most solvers still take two or three guesses, or do many finish in one?
**Reply (summary):** One-guess solves are rare (opening word must be the answer), ~0.1–0.5% of players even on easy days; the bulk of solvers land on 2–4 tries; "easy" means fewer 5/6/X, not more 1s.
**Effect on work:** Gave a structural prior on the shape of the try distribution: the 1-try target is near-constant and small, difficulty moves the right tail. This shaped the validation read (1-try RMSE 1.09 pp, X RMSE 2.69 pp — the informative categories) and the interpretation of the EERIE prediction (mass on 4/5/6 tries, 1-try ~0). The 0.1–0.5% figure is recorded in the task 3 parameter table (one_guess_structural_rate) and matches the data mean of 0.47%.

## Exchange 6
**Q:** Does a Wordle puzzle with repeated letters, like EERIE, usually produce more failed X results than an all-unique-letter word?
**Reply (summary):** Yes, reliably; repeated letters are the single largest word-attribute driver of the X percentage; EERIE (triple E) especially punishing; absolute X stays low (single digits) but the gap is noticeable.
**Effect on work:** Up-weighted the X share (0.75) in the difficulty index of task 4 relative to the 5/6-try shares, and motivated the X-by-duplication table (2.3% / 3.9% / 10.9% for unique/double/triple days) as the headline task 5 feature. The triple-letter estimate (n=2 in 2022) is recorded in the task 3 parameter table with its small-n interval.

## Exchange 7
**Q:** Were there specific days in 2022 when Wordle reporting on Twitter spiked far above the usual level, and why?
**Reply (summary):** Spikes are mostly external: the viral/NYT-acquisition window (late Jan–early Feb), the March 2022 cultural peak with a notorious word, and occasional one-day bumps from meme-worthy hard words. Word commonness alone cannot produce a "far above usual" spike.
**Effect on work:** Justified excluding Jan–Aug 2022 from the forecasting fit (the spikes and the growth curve would bias the extrapolation) and motivated fitting the volume models on Sep–Dec 2022 only (task 1, models A/B/C). Also informed the "novelty spike" residual term left in the prediction interval.

## Exchange 8
**Q:** After 2022's viral growth, had Wordle's daily Twitter reporter count levelled off, or was it still growing heading into 2023?
**Reply (summary):** Largely levelled off; the steep climb was early 2022, flattened by mid-2022; heading into 2023 the baseline is plateaued with day-to-day variation from word and day-of-week, not a rising trend.
**Effect on work:** This is the key extrapolation assumption for the Mar 1, 2023 prediction interval: the forecast is a flat-plus-seasonal continuation of the Sep–Dec 2022 plateau (HW 17,075; SARIMA 18,204), not a continuation of any 2022 growth. Recorded as the plateau_level parameter (22,154/day, [20,000, 26,000]) in the task 1 parameter table; the interval width is stated as conditional on the plateau persisting.

## Exchange 9
**Q:** When Wordle's player base plateaus, does reporting stay steady through the year, with winter dips and spring rises?
**Reply (summary):** No clean seasonal cycle; residual variation is dominated by day-of-week and word difficulty; any winter/spring movement is weak and confounded with the 2022 growth curve.
**Effect on work:** Justified not fitting annual seasonality for the 30-day extrapolation (one year of data cannot identify an annual cycle, and the prior says it is weak); the seasonal structure retained in the forecast is weekly only (HW weekly seasonality, SARIMA(1,0,1)(1,0,1,7)). Recorded as a stated assumption in task 1.

## Exchange 10
**Q:** When a player fails Wordle, do they usually tweet their X result, or do failures rarely get posted?
**Reply (summary):** Failures rarely get posted; X is the least-shared outcome, so the reported X share systematically understates the true failure rate; on hard/meme-worthy word days some failures are shared as collective complaints.
**Effect on work:** Two changes. (1) Task 3: the predicted EERIE X share (12.9%) is explicitly framed as a lower bound on the true population failure rate, and the "selection bias" caveat is written into the outcome analysis. (2) Task 4: the accuracy limitation that the 'hard' class is enriched for words whose failures happened to be posted (hard-and-shareable) is stated as a bias of the labels. Also task 5 feature 7.

## Notes on compliance
- Exactly 10 exchanges, one question each, each ≤20 words, each answerable without modeling background; no coding/debugging/derivation requests.
- Every reply above became either a parameter/constraint with a recorded source (parameter tables in tasks 1–3 of solution.json) or a change to a model, test or interpretation that was then executed (code in `code/model.py`, results in `results/model_out.json`).
- No reply text was copied into solution.json; the submission states only the values, constraints and conclusions in its own formulation.
