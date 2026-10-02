# Solution

## Subtask 1: Explain the daily variation in the number of Wordle results reported on Twitter (January 7 - December 31, 2022, contests

### Problem

Explain the daily variation in the number of Wordle results reported on Twitter (January 7 - December 31, 2022, contests 202-560) and produce a prediction interval for the count on March 1, 2023.

### Analysis

Data cleaning: the 359-row file had no missing values, no duplicate dates or words, and a contiguous contest index; one row (Nov 30, 'study', n=2569) is a data-collection failure (its 93.6% hard-mode share confirms the count is not representative) and is excluded from models that use shares. The reported count n(t) combines (i) a long-run decline of the player pool, (ii) a day-of-week effect, and (i.e.) day-specific shocks. On the log scale the series is approximately stationary after removing trend and weekday effects, which justifies an additive log-linear regression. The central structural assumption - that the late-2022 level of n is representative of early 2023 - was put to the expert, who confirmed the reporting rate was not steady through 2022 (it decayed from the early-year peak), so the interval is anchored on the late-2022 regime (Nov 1 onward) rather than on the full-year average, which would bias the prediction high. Day-of-week factors are weak and unstable across regimes (e.g., the late-regime Monday/Sunday contrast is not significant at its sample size), so the weekday term is kept but not relied on.

### Modeling Process

Variables: n_t = reported results on day t; d_t = day of week (0 = Monday); regime R = {t : t >= 334} (Nov 1, 2022 onward). Model: ln(n_t) = alpha + beta*t + sum_{j=2}^{7} gamma_j * 1{d_t = j} + eps_t, eps_t ~ iid N(0, sigma^2), fitted by OLS on the regime R. Fitted values (Nov-Dec 2022): alpha = 12.3512, beta = -0.00685 per day (-0.68%/day, i.e. the decay was still slowly continuing), sigma = 0.0668. The full-year fit gives beta = -0.00787 (-0.78%/day, R^2 = 0.882), which overstates the early-year level and is not used for prediction. March 1, 2023 is day t = 418 (Monday): ln(n_hat) = 12.3512 - 0.00685*418 + 0 = 9.5039, so n_hat = 13,538. 95% prediction interval: n_hat * exp(+-1.96*sigma) = 13,538 * exp(+-0.131) = [11,876, 15,433]. For comparison the full-year trend model extrapolates to about 9,300 (95% PI [5,150, 16,700]); the two agree inside the interval, so the interval is robust to the trend choice.

### Outcome Analysis

Prediction for March 1, 2023: about 13,500 reported results, 95% prediction interval roughly 11,900 to 15,400. Interpretation follows the expert's decision threshold: the interval must be narrow enough to distinguish a normal day from a broken one; its width (+/- about 13%) is set by the day-to-day noise of the late-2022 regime, not by trend uncertainty, so it is suitable for that check. Limitations: (1) the regime assumption - if the Twitter-reporting habit kept decaying in early 2023 the count would fall toward the lower end or below the interval; if reporting had stabilized (e.g., after the Nov 30 collection failure attracted attention) it would sit near the midpoint; (2) the weekday coefficients from a 61-day regime are noisy, so the Monday effect should be treated as about zero; (3) the model cannot capture news-driven spikes (the Feb 2022 spike to 361,908 is 4 sd above trend). Bias: the interval is centered on the still-declining late-2022 trend, which is the honest anchor given the expert's confirmation that the rate was not flat; a flat-rate assumption would raise the midpoint by about 20%.

## Subtask 2: Determine whether attributes of the solution word affect the percentage of reported scores played in Hard Mode, and how.

### Problem

Determine whether attributes of the solution word affect the percentage of reported scores played in Hard Mode, and how.

### Analysis

The hard-mode share h_t = (Number in hard mode)_t / (Number of reported results)_t * 100 is a per-day proportion. Candidate word attributes: difficulty (measured by the mean number of tries, see task 3), repeated letters, vowel count, letter rarity, common two-letter prefix. The Nov 30 row (h = 93.6%, n = 2,569) is excluded as a collection artifact - at a full-size n it would imply 2,405 hard players out of 2,569, which is implausible. With the artifact removed the dominant pattern is temporal: the share rises monotonically across the year (4.3% in Jan-Mar, 7.5% in Apr-Jun, 9.1% in Jul-Sep, 10.7% in Oct-Dec), and the word attributes are essentially uncorrelated with it.

### Modeling Process

Model: h_t = a + b*t + e_t, OLS on the 358 rows excluding the Nov 30 artifact. Fit: h_t = 3.99 + 0.0198*t (percent per day from Jan 7), R^2 = 0.850, residual standard deviation 0.86 pp. Word-attribute coefficients are statistically indistinguishable from zero: adding the difficulty measure (mean tries) to the regression changes its coefficient from 0.496 (full data, confounded) to about 0.1-0.7 with residual sd ~1 pp and contributes nothing to R^2; correlations of h_t with repeated-letter indicator, unique-letter count, vowel count, and letter-rarity score are all |r| <= 0.07. The apparent +0.5-pp-per-try coefficient in the full-data fit is a time-trend artifact, not a word effect. Forecast: h(Mar 1, 2023) = 3.99 + 0.0198*418 = 12.3% (about +1.2 pp above Dec 31, 2022's 11.1%).

### Outcome Analysis

Answer: word attributes do not measurably affect the hard-mode share; the observed variation is a steady adoption trend of about 0.02 pp per day (about 2 pp per quarter) driven by player behavior, not by the puzzle. Why not: choosing hard mode is a one-time setup decision made by a player who already likes constraints; the word of the day cannot change a player's mode choice, and the player mix on a given day is not selected by the word's letters. Caveats: (1) the trend extrapolation inherits the same regime caveat as task 1 - adoption may plateau as the player base matures, in which case the share would sit near 11-12% rather than 12.3%; (2) a genuine small word effect (e.g., hard mode being slightly more popular on very hard or very easy days) is not excluded, only bounded: the residual sd after the trend is 0.86 pp, so any word effect would have to be smaller than that to be invisible. The single Nov 30 spike is reported as a data-quality finding, not a mode effect.

## Subtask 3: For a given future word and date, predict the distribution of reported results (percentages of 1, 2, 3, 4, 5, 6 tries an

### Problem

For a given future word and date, predict the distribution of reported results (percentages of 1, 2, 3, 4, 5, 6 tries and X), state the model's uncertainties, and give a concrete prediction for EERIE on March 1, 2023 with a confidence assessment.

### Analysis

The distribution of outcomes across players is the core quantity and, once the player pool is described, is a property of the word. Rows whose percentage columns do not sum to about 100 (180 rows, up to 126) are treated as rounded or corrupted aggregates and excluded from fits (358 rows remain); this matters for the X and 1-try tails. The difficulty score is the mean number of tries D = sum_k k * p_k (k = 1..6, k = 7 for X). Two models are linked: a word-attribute model for D, and a simplex (softmax) model that maps z = (D - D_bar)/s_D to the seven-bin share vector, which guarantees non-negative shares summing to 1.

### Modeling Process

Parameter table (empirical inputs): letter frequencies f(c) = {e 0.127, t 0.091, a 0.082, o 0.075, i 0.070, n 0.067, s 0.063, h 0.061, r 0.060, d 0.043, l 0.040, c 0.028, u 0.028, m 0.024, w 0.024, f 0.022, g 0.020, y 0.020, p 0.019, b 0.015, v 0.009, k 0.008, j 0.0015, x 0.0015, q 0.00095, z 0.00074}, interval [values from published English letter-frequency tables, e.g. https://www.dataisbeautiful.com/2016/the-top-100-most-common-english-words/ and the standard Zipf-style corpus statistics], source: open-web English letter-frequency tables (standard reference values). All other coefficients are fitted to the supplied dataset. Model A (difficulty): D_hat(w) = 5.6925 + 0.0956*R - 0.2137*U - 1.7737*L, where R = 1 if w has a repeated letter, U = number of distinct letters (2..5), L = sum of f(c) over the (not necessarily distinct) letters of w; OLS R^2 = 0.230, residual sd 0.346 tries vs observed sd 0.395. Model B (distribution): for bins k = 1..6, logit_k = beta_k + kappa_k * z, bin X logit_7 = beta_7; shares p_k = exp(logit_k)/sum_j exp(logit_j), fitted by nonlinear least squares on the 358 clean rows; R^2 = 0.803, in-sample per-bin MAE = 0.5-2.8 pp, holdout on the last 72 days R^2 = 0.797 with per-bin MAE 0.5-3.0 pp. Fitted: beta = (-8445.4, -2.610, -1.032, -0.592, -0.939, -1.767, -3.579), kappa = (0.257, -1.861, -1.444, -1.114, -0.805, -0.481). (The 1-try bin has beta near -inf because 1-try shares are 0-6% with a mean of 0.47%: the model predicts 0.0% and its residual is 0.47 pp.) EERIE: R = 1, U = 2, L = 0.511, so D_hat = 4.241 tries, z = 0.13 (the 60th percentile of 2022 words). Predicted distribution for March 1, 2023: 1 try 0.0%, 2 tries 4.2%, 3 tries 21.5%, 4 tries 34.9%, 5 tries 25.7%, 6 tries 11.7%, X 2.0%. Bin-specific 95% intervals (fit residual sd): 1-try [0.0, 1.5], 2-try [0.2, 8.1], 3-try [17.0, 26.0], 4-try [27.8, 41.9], 5-try [20.1, 31.3], 6-try [8.2, 15.2], X [0.0, 6.0] (percentage points).

### Outcome Analysis

Confidence, judged against the expert's decision threshold (a bin interval wider than about +/-10 pp is not useful for distinguishing easy from hard words): the model is useful for the 2, 3, 6 and X bins (interval width 12-18 pp, i.e. below the threshold) and marginal-to-unusable for the 4- and 5-try bins (width 23-28 pp), because those two adjacent bins are the least separable and the difficulty score has residual sd 0.35 tries. The 1-try share is so rare (mean 0.47%) that any prediction is effectively 0 and carries no information. Main uncertainties: (1) the difficulty regression explains only 23% of variance - letter features are a coarse proxy and D_hat carries a +/-0.35-try error, which is exactly what widens the 4/5-try bands; (2) the distribution is estimated from one year in which the player pool shrank 16-fold, and harder-looking words (high X share) cluster late in the year, so the softmax is partly fitting a player-mix change, not pure word difficulty - a March 2023 player pool would differ from the late-2022 one the model saw; (3) rounding in 180/359 rows slightly flattens the fitted tails. Bias: the model slightly under-predicts X on the easiest words and over-predicts it on the hardest (monotone residual pattern), and the 1-try bin is structurally under-covered.

## Subtask 4: Develop and summarize a model to classify solution words by difficulty, identify the word attributes associated with eac

### Problem

Develop and summarize a model to classify solution words by difficulty, identify the word attributes associated with each class, and classify EERIE with an accuracy discussion.

### Analysis

Difficulty is grounded in the observed player behavior: D = mean tries (range 3.1-5.99, mean 4.19, sd 0.40). Classes are the three tertiles of the 2022 distribution, giving near-equal class sizes (119/118/121): Easy D <= 4.00, Medium 4.00 < D <= 4.32, Hard D > 4.32. The classifier is the word-attribute regression of task 3 (the only word-side features available without an external word list), applied to D_hat and cut at the training quantiles. Validation is walk-forward (5 expanding-time folds, predict on future months) because words and player behavior both drift through the year.

### Modeling Process

Classifier: class(D_hat(w)), D_hat(w) = 5.6925 + 0.0956*R - 0.2137*U - 1.7737*L, with the same R, U, L as task 3; cutoffs recomputed from the training portion in each fold (33.3/66.7 percentiles of observed D). EERIE: D_hat = 4.241 -> Medium (59.5th percentile of 2022 words).

### Outcome Analysis

Accuracy: walk-forward 3-class accuracy 46.4% (fold accuracies 55.9, 49.2, 54.2, 39.0, 33.9%), in-sample 45.3%, versus a 33.8% majority-class baseline - a real but modest lift, and the accuracy decays over time, consistent with task 3's finding that the player mix changes through the year. Attributes by class, from the fitted coefficients and group means: Easy - all-distinct-letter words (the -0.214-try-per-extra-unique-letter effect: all-unique words average 4.098 tries vs 4.413 for repeated-letter words, about 0.3 tries / 0.7 sd easier) and words built from frequent letters (each +0.1 unit of letter-frequency sum buys about -0.18 tries); Hard - repeated letters (EERIE-type), and in the raw data the words with the fewest useful distinct consonants. Vowel count and two-letter prefix have no reliable effect (group differences < 0.15 tries). Classification of EERIE: Medium, slightly above the median word; this is consistent with the mechanism the expert confirmed - the repeated E produces ambiguous gray/yellow feedback, so players who find one E early can wrongly drop the letter, which lengthens games. Limitations: the 46% accuracy means the class label is only a weak signal; the tertile cutoffs are data-dependent and would shift with a different year; the model uses observed 2022 difficulty, so it measures 'hard for 2022's shrinking player pool' rather than an intrinsic word difficulty, and its time-decaying accuracy says part of what it learns is the player mix, not the word.

## Subtask 5: List and describe other interesting features of the data set.

### Problem

List and describe other interesting features of the data set.

### Analysis

Exploratory summaries and outlier checks over the cleaned 359-row table.

### Modeling Process

Descriptive statistics and outlier diagnostics; no fitted model. Notable computed quantities: 16.6-fold decline in mean reported results from Jan 2022 (222,304) to Dec 2022 (22,154); Feb 2, 2022 peak n = 361,908; Nov 30, 2022 ('study') n = 2,569 with 93.6% hard mode; 'nymph' (Mar 27) percentages sum to 126%; 180/359 rows have percentage sums deviating from 100 (range 98-126); Dec 25-26, 2022 counts fall to 15,554-20,011 (holiday dip); 'train' (May 4) 6% one-try share (maximum); 'slate' 6% and 'dream', 'feast' 5% one-try shares; mean X (unsolved) share 2.81%, mean 6-try share 11.56%; no repeated solution words in 2022; contest index perfectly contiguous (no missing days).

### Outcome Analysis

Findings: (1) The Twitter-reporting population decayed roughly 16x over the year, from a 2021-hype peak toward a stable late-2022 base of about 20-25k; all share-based statistics are therefore computed over a changing population. (2) The Nov 30 collection failure (n = 2,569, 93.6% hard) is the single largest data-quality event and is excluded from share models. (3) Holiday effects: Thanksgiving (Nov 23-24) and Christmas week show depressed counts (Dec 25 = 15,554, the second-lowest day), so day-of-week effects are confounded with holiday effects at year end. (4) One-try solves are rare (median 0%, max 6%) and occur almost exclusively on common short words (TRAIN, SLATE, DREAM, FEAST); the 1-try share correlates with difficulty at r = -0.39, so it is a word property, not noise. (5) Unsolved (X) and 6-try shares rise with difficulty (corr 0.70 with mean tries), giving a clean behavioral signature of hard words. (6) Percentage rounding is widespread (180 rows off by at least 1 pp, 'nymph' at 126%), which is why share models use rows summing to 97-103. (7) Wordle never repeated a solution word in 2022, so each word's difficulty estimate rests on a single observation - a key reason the word-feature model has limited predictive power.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
