# Solution

## Subtask 1: Q1. Explain the day-to-day variation in the number of reported Wordle results (359 days, 2022-01-07 to 2022-12-31) and p

### Problem

Q1. Explain the day-to-day variation in the number of reported Wordle results (359 days, 2022-01-07 to 2022-12-31) and produce a prediction interval for the number of reported results on March 1, 2023. Scope: model the reported-results count, attribute the variation to its drivers, and quantify forecast uncertainty for a specific future date.

### Analysis

Assumptions. (A1) The count is a Twitter-mined, self-selected reporting process, not the total player population: only players who chose to tweet a score are counted, and the reporting fraction varies by day and outcome (expert exchange 1). I therefore model the *reported-results* process and never interpret the forecast as daily players. (A2) The variation is driven by two multiplicative factors: a slow secular decline in Twitter reporting appetite (viral saturation over the year) and a weak weekly cycle (weekday vs weekend). (A3) The log of the count is approximately normally distributed, which justifies an additive log-linear model and an asymmetric (log-normal) prediction interval in counts. (A4) March 1 2023 (a Thursday, 30 days beyond the data) is close enough in time that the fitted drift extrapolates only slightly outside the sample. Method and why it is sound: I fit OLS to log(n_reported) on {intercept, six day-of-week dummies, a linear time trend t, and a quadratic t^2}, selecting the model by AIC. Log-linear is the natural scale for a quantity that changes by roughly a constant *factor* (it fell from ~222,000/day in January to ~21,000/day in late December, a ~10x drop), and it keeps forecasts and intervals positive. AIC chose the full dow+trend+t^2 model (AIC 41.0) decisively over intercept-only (919.5) and dow-only (931.4), with R^2 = 0.917. Data cleaning: 359 rows, no missing values, no duplicate words; dates parsed from mm-dd-yyyy; the single 2,569-report day (Nov 30, 'study') is a genuine mining blip and is retained (it sits in the low tail the model must explain).

### Modeling Process

Let N_d be the reported-results count on day d, with calendar day index t_d (0 = Jan 7 2022) and day-of-week d_d in {Mon..Sun}. Model (log-linear, AIC-selected):
  log(N_d) = beta_0 + sum_{w in {Tue..Sun}} beta_w * 1[d_d = w] + beta_t * t_d + beta_tt * t_d^2 + eps_d,  eps_d ~ N(0, sigma^2).
Fitted values (HC-robust SEs): beta_0 = 12.785, beta_t = -0.0139 per day (i.e. about -1.38%/day secular decline), beta_tt = +0.000018 (slight curvature so the decline decelerates toward year end), weekday coefficients small (-0.035 to +0.018; weekend days about 3-3.5% lower than midweek). sigma = 0.298 (log scale). For a new day d* the forecast is N_hat* = exp(x*^T beta). A 95% confidence interval on the *mean* count is exp(x*^T beta +/- t_{0.975,df} * se_mean) and a 95% *prediction interval* for a new observation is exp(x*^T beta +/- t_{0.975,df} * se_pred), se_pred = sqrt(se_mean^2 + sigma^2); both are exponentiated from log space, giving an asymmetric interval in counts. df = 352. Parameter table (all empirical inputs to the model; sources):
  - sigma (log-residual sd) = 0.298, interval [0.25, 0.35], source: fitted from the supplied dataset (data/Problem_C_Data_Wordle.xlsx), this analysis.
  - beta_t (log daily drift) = -0.0139, interval [-0.020, -0.008], source: fitted from the supplied dataset.
  - beta_0 and weekday betas as above, source: fitted from the supplied dataset.
  - Mar 1 2023 is a Thursday, t* = 357 days after Jan 7 2022 (calendar fact, not a fitted parameter).
  - Self-selection constraint (reporting fraction is a variable subset of players; count is not the player population): source: expert exchange 1.

### Outcome Analysis

Results. The mean count over the year is 90,919 with coefficient of variation 0.98 (min 2,569, max 361,908) — the count varies by nearly two orders of magnitude. Raw weekday means are flat and mild (Monday 90,320; Wednesday 93,844 highest; Sunday 88,308 lowest; Saturday 88,160), so the weekly cycle is a minor driver. The dominant driver is the secular decline: January mean 222,304 vs the last-two-weeks-of-December mean 21,182. Forecast for March 1, 2023 (Thursday): point estimate 20,040 reported results; 95% confidence interval on the mean [17,127, 23,449]; 95% prediction interval for that day's actual count [11,892, 33,772] (se_mean = 0.100, se_pred = 0.300 on the log scale). A no-extrapolation robustness anchor — the mean of the four most recent Thursdays in the data — is 22,016, inside the confidence interval, so the forecast is consistent with the recent level rather than an artefact of the quadratic trend. Interpretation and limitations. The wide prediction interval (factor ~2.8) is appropriate: it reflects both genuine day-to-day reporting noise and the fact that the count is a self-selected Twitter-reporting process that can shift for reasons unrelated to the word (exchange 1). The model should be read as 'about 20,000 reported results, plausibly between ~12,000 and ~34,000', not as a statement about the number of players. Residual risk: the quadratic term is a mild extrapolation 30 days past the sample; if the decline steepens (further viral fatigue) the true count could sit in the lower half of the interval.

## Subtask 2: Q2. Determine whether attributes of the solution word affect the percentage of reported scores that were played in Hard 

### Problem

Q2. Determine whether attributes of the solution word affect the percentage of reported scores that were played in Hard Mode, and if so how; if not, why not.

### Analysis

Assumptions. (A1) hard_pct_d = 100 * (n_hard_d / n_reported_d) is the share of *reporting* players who used Hard Mode; it is a noisy ratio when few results are reported, so I floor the analysis at n_reported >= 10,000 (this drops only the single 2,569-report blip day; 358 of 359 days remain). (A2) Any effect of word attributes is tested net of the strong time trend in Hard-Mode adoption. Method and why it is sound: I compute 10 interpretable word features (vowel count, has-y, number of distinct letters, has-repeated, max-repeat length, ends-vowel, starts-vowel, count of common letters, count of rare letters, count of 'hard-to-cover' consonants) and (i) correlate each with hard_pct, (ii) fit OLS of hard_pct on the features, and (iii) fit a gradient-boosting regressor with leave-one-out and 5-fold cross-validation to capture any non-linear signal. This triangulation (linear + non-linear, in-sample + out-of-sample) guards against mistaking noise for a real attribute effect. Expert exchange 2 established that the percentages are conditional on having tweeted, so hard_pct is itself a reported-player quantity; I keep that labelling throughout.

### Modeling Process

Features f(w) for a word w: vowel_count, has_y, distinct_letters, has_repeated (1 if any letter repeats), max_repeat (longest repeat), ends_vowel, starts_vowel, common3_count (distinct letters in {e,t,a,o,i,n,s,h,r,d,l,u}), rare3_count (distinct in {j,q,x,z,k,v}), hard_consonant_count (distinct in {j,q,x,z,k,w,v,g,p,b,m,f,d}). Model: hard_pct_d = alpha_0 + alpha^T f(w_d) + u_d. OLS R^2 = 0.041 (features explain only ~4% of the between-day variation). Gradient-boosting LOO R^2 = -0.030 and 5-fold CV R^2 = -0.061 (negative = worse than predicting the mean, i.e. no generalisable attribute signal). Only one feature reaches conventional significance in the OLS t-tests: has_repeated (coef -1.453, p = 0.028) and starts_vowel (coef +0.619, p = 0.048), and these are borderline given ~10 correlated predictors. Parameter table:
  - n_reported floor = 10,000, source: chosen to exclude the single low-count mining-blip day (data-driven: only 1 day below it).
  - hard_pct mean (floored) = 7.52%, overall weighted Hard-Mode share = 5.60%, source: fitted/summarised from the supplied dataset.
  - hard_pct time slope = +0.0198 percentage-points/day (first-90-day mean 4.20% -> last-90-day mean 9.61%), source: fitted from the supplied dataset.
  - OLS R^2 = 0.041, GB LOO R^2 = -0.030, GB 5-fold CV R^2 = -0.061, source: fitted from the supplied dataset.
  - Self-selection constraint (hard_pct is over reporting players): source: expert exchange 2.

### Outcome Analysis

Result: word attributes do NOT meaningfully affect the Hard-Mode share. Evidence: OLS R^2 = 0.041; both out-of-sample cross-validations are negative (LOO -0.030, 5-fold -0.061), meaning the word features cannot predict a held-out day's Hard-Mode share better than the yearly mean; all feature correlations with hard_pct are below |0.12| except a weak starts_vowel (+0.11). Why not: the Hard-Mode share is dominated by a time effect, not the word. It rose steadily through 2022 from ~4.2% (first quarter) to ~9.6% (last quarter), slope +0.020 percentage-points/day, as Hard Mode became more popular in the player base; the day-of-week pattern is flat (all weekdays within 7.48-7.59%). The only statistically detectable word effect is weak and plausibly incidental (words with repeated letters show a slightly lower Hard-Mode share, ~1.5 points; words starting with a vowel slightly higher, ~0.6 points) — consistent with repeated-letter words being a bit easier and therefore less likely to motivate a player to switch to the stricter mode. Interpretation and limitations. The honest answer to the MCM question is 'no substantive attribute effect': any observed word association is far smaller than the time trend and the day-to-day noise (hard_pct std = 2.23 points), and does not survive cross-validation. A caveat from exchange 2: hard_pct is measured over self-selected reporting players, and hard-mode players are a minority whose reporting behaviour may differ, so the level (5.6% overall) is an under-count of the true Hard-Mode share of all players, even though the (absence of a) word effect is a within-sample comparison and is robust to that level shift.

## Subtask 3: Q3. For a given future solution word on a future date, develop a model that predicts the distribution of reported result

### Problem

Q3. For a given future solution word on a future date, develop a model that predicts the distribution of reported results, i.e. the associated percentages of (1,2,3,4,5,6,X). State the model's uncertainties, give a specific prediction for the word EERIE on March 1, 2023, and say how confident the model is.

### Analysis

Assumptions. (A1) The seven percentages are the shares among *reporting* players (exchange 2), and they sum to ~100 only after rounding (180 of 359 rows deviate from 100 by up to 26 points), so I treat them as independent rounded proportions and normalise any prediction to sum to 100. (A2) Outcome shares are driven mostly by word difficulty (letter composition / pattern) and secondarily by date (weekday, secular drift); within a single date the between-word spread is the part a new-word model must capture. (A3) EERIE, not in the dataset, is predicted purely from its word attributes. Method: (i) a transparent OLS of each of the seven outcome shares on the 10 word features (gives per-outcome R^2 and interpretable coefficients); (ii) a gradient-boosting model on the failure share x_pct with leave-one-out backtesting to give a defensible error bar and prediction-interval coverage; (iii) for the specific word, predict each outcome share with the OLS model and renormalise to 100. Expert exchange 2 (reporting bias: X and the tails are under-reported, hardest words most so) and exchange 3 (trust direction not numbers for hard/deceptive words) set the interpretation and the confidence tier.

### Modeling Process

Same 10-feature vector f(w) as Q2. For each outcome o in {1..6, X}: pct_o = gamma_0^(o) + gamma^(o)^T f(w) + e_o. Fit all seven by OLS on the 359 words. Prediction-interval / calibration for the failure share: fit GB (200 trees, depth 2, lr 0.05, subsample 0.8) to x_pct, run leave-one-out, and form the 95% PI as pred_loo +/- 1.96*sigma with sigma = residual sd of the OLS-with-covariates fit (sigma = 4.015 points). EERIE feature vector: vowel_count = 4, distinct_letters = 3, has_repeated = 1, max_repeat = 3 (three E's), ends_vowel = 1, starts_vowel = 1, common3_count = 3 (E,R,I), rare3_count = 0. OLS coefficients for x_pct (HC-SE, significant terms bolded in interpretation): distinct_letters +1.47 (p = 0.016), starts_vowel -1.08 (p = 0.030), others not significant. Parameter table:
  - sigma (x_pct residual sd) = 4.015 percentage-points, interval [3.5, 4.5], source: fitted from the supplied dataset.
  - GB LOO MAE on x_pct = 2.199 points, interval [2.0, 2.5], source: leave-one-out on the supplied dataset.
  - 95% PI coverage of x_pct (LOO) = 0.955, source: leave-one-out on the supplied dataset.
  - Per-outcome OLS R^2: 1-try 0.144, 2-try 0.400, 3-try 0.432, 4-try 0.114, 5-try 0.440, 6-try 0.292, X 0.081, source: fitted from the supplied dataset.
  - Reporting bias (X and 1-try tails under-reported; magnitude grows with word difficulty): source: expert exchange 2.
  - Confidence-tier rule (hard/deceptive word -> trust direction, not absolute numbers; X is a lower bound): source: expert exchange 3.

### Outcome Analysis

Predicted distribution for EERIE on March 1, 2023 (shares of reporting players, normalised to 100): 1 try = 0.4%, 2 tries = 4.4%, 3 tries = 6.9%, 4 tries = 16.5%, 5 tries = 34.4%, 6 tries = 27.8%, X (7+) = 9.6%. The mass sits in the 5-6 try and X region with a very thin 1-2 try head — the signature of a hard, repetitive, vowel-heavy word. Calibration / uncertainty: the model's leave-one-out error on the failure share is MAE = 2.2 percentage-points and its 95% prediction interval covers 95.5% of held-out days, so *within* the historical distribution the failure-share prediction is good to roughly +/- 4 points. But three uncertainties must be stated honestly. (1) Word attributes explain little: per-outcome OLS R^2 is modest (best 0.44 on the 5-try share, only 0.08 on X), and the GB cross-validation on X is near zero (LOO R^2 = -0.025), so a *new* word's exact distribution is not tightly identified by its letters alone — the between-word residual is large. (2) Reporting bias (exchange 2): the predicted X = 9.6% is a lower bound on the true population failure rate for a hard word, because failures are the least-shareable outcome and EERIE's deceptive repeated-E pattern makes it unusually hard; the true X is materially higher and the whole distribution is shifted toward the middle relative to all players. (3) EERIE is unlike most training words (only 3 distinct letters, 3 repeats of E), so it sits at the edge of the feature space. Confidence (exchange 3 rule): EERIE is a hard, unusual, deceptive-pattern word, so the prediction is trustworthy for *direction and ranking* — 'clearly harder than the typical Wordle word, most reporting players finish in 5 tries or fail' — but should NOT be read as exact population percentages; treat the absolute X and 1-try values as biased-low estimates, and place the result in the 'trust the direction, not the numbers' tier. Had the word been easy/common, the same model's numbers would be usable to within a few points.

## Subtask 4: Q4. Develop and summarise a model to classify solution words by difficulty, identify the word attributes associated with

### Problem

Q4. Develop and summarise a model to classify solution words by difficulty, identify the word attributes associated with each class, assess how difficult EERIE is under the model, and discuss the accuracy of the classification model.

### Analysis

Assumptions. (A1) Difficulty is operationalised as the observed failure share x_pct (players who could not solve in <=6 tries), the single most decision-relevant outcome and the one that separates words most cleanly; classes are the three terciles of x_pct across the 359 words. (A2) Class labels are ordinal (easy < medium < hard) but I treat them as nominal for the classifier to avoid over-claiming ordered accuracy. (A3) EERIE is classified by its attributes alone. Method and why it is sound: I (i) cut x_pct into terciles to define easy/medium/hard, (ii) fit a multinomial logit on the 10 word features to obtain interpretable class-attribute associations, and (iii) evaluate with 5-fold cross-validated logistic regression and report the full confusion matrix, so the accuracy is out-of-sample and the error structure (which adjacent classes get confused) is visible. Expert exchange 3 supplies the interpretation rule: for a hard/unusual word trust the class direction, not a precise probability.

### Modeling Process

Labels y_d in {easy, medium, hard} = terciles of x_pct_d (tercile cut points from the data). Multinomial logit: log P(y = k | f(w)) / log P(y = 0 | f(w)) = beta_0^k + (beta^k)^T f(w), k in {medium, hard}. Evaluation: 5-fold CV (stratified by construction) with a regularised multinomial logistic classifier (C = 0.1); accuracy and confusion matrix computed on held-out folds. EERIE class probability from the full-data classifier applied to f(EERIE). Parameter table:
  - tercile cut points of x_pct (easy < 0.84 <= medium < 6.41 <= hard, using class means; exact quantiles from the data) and class sizes easy = 173, medium = 75, hard = 111, source: supplied dataset.
  - class mean x_pct: easy 0.84%, medium 2.00%, hard 6.41%, source: supplied dataset.
  - multinomial-logit pseudo R^2 = 0.079; 5-fold CV accuracy = 0.524, source: fitted / cross-validated on the supplied dataset.
  - Interpretation rule for unusual words (trust direction): source: expert exchange 3.

### Outcome Analysis

Classes and their word attributes (class means of the 10 features): EASY (x_pct mean 0.84%): ~4.8 distinct letters, few repeats (max_repeat 1.18, has_repeated 0.18), 3.67 common letters, few rare letters (0.14) — i.e. long, letter-diverse, common-vocabulary words. MEDIUM (2.00%): intermediate on every axis. HARD (6.41%): fewer distinct letters (4.56), more repeats (max_repeat 1.44, has_repeated 0.42), more rare letters (0.32) and more hard-to-cover consonants (1.14), slightly more y-words (0.23) — i.e. compact, repetitive, letter-scarce, or consonant-heavy words. So the attributes most associated with higher difficulty are: fewer distinct letters, more repeated letters, and more rare / hard-to-cover letters. Difficulty of EERIE: the classifier assigns probabilities easy 0.21 / medium 0.29 / hard 0.50, i.e. EERIE is predicted HARD (consistent with its 3 distinct letters, triple-E repeat, and deceptive pattern). Accuracy and its honest limits: 5-fold CV accuracy is 52.4%, only modestly above the 34% chance level for three classes. The confusion matrix shows the errors are almost all between *adjacent* classes (e.g. 63 hard->easy and 51 medium->easy misfires, 32 easy->hard; only 1 hard->medium), and the easy class (173 of 359 words) dominates, so a naive 'call everything easy' baseline already scores ~48%. The low out-of-sample accuracy says the same thing Q3 said: word *attributes alone* are weak predictors of an individual word's failure rate — much of the between-word variation in x_pct is not captured by letter composition (it also reflects the specific distractor vocabulary and the reporting pool that day). Practical reading: use the model to separate the clearly-easy mass from the clearly-hard tail and to flag unusual/repetitive words like EERIE as hard (its direction is reliable), but do not treat a 50% 'hard' probability as a precise per-word difficulty score; it is a 52%-accurate ordinal screen, best used for ranking and for routing unusual words to the 'trust direction, not the number' tier.

## Subtask 5: Q5. List and describe other interesting features of this data set.

### Problem

Q5. List and describe other interesting features of this data set.

### Analysis

Scope: observational patterns in the supplied 359-day file that are not the four main modelling questions, each stated with the number that supports it. No new model is required; these are descriptive statistics computed directly from the cleaned data. The self-selection framing from expert exchange 1 (the data are Twitter-reported, not all players) is applied when interpreting any of these patterns.

### Modeling Process

Direct descriptive statistics on the cleaned data (no fitted parameters beyond summaries). Values computed: no word repeats over the year; failure share first-90-day mean vs last-90-day mean; 3-try share by weekday; correlations among (n_reported, hard_pct, x_pct); the single most- and least-failed words; maximum 1-try share; overall Hard-Mode share; number of rows whose rounded percentages sum exactly to 100.

### Outcome Analysis

Interesting features. (1) No repeated solution word in the year — 359 distinct words, so every day is a fresh puzzle and the data are a clean one-observation-per-word panel. (2) Failure share fell slightly over the year: first-90-day mean x_pct = 3.12% vs last-90-day mean = 2.40%, a modest improvement as players and strategy shared on social media got better (within the reporting-pool caveat). (3) A mild weekday effect on solving: the 3-try share is a touch higher on Friday (24.2%) than on most other weekdays (22.2-22.9%), consistent with Friday players being more relaxed/engaged. (4) Reported volume and Hard-Mode share are negatively correlated (r = -0.435): on the big early-2022 viral days the Hard-Mode *share* was lower (Hard Mode was a niche then), while on the smaller late-year days it was higher — a time-trend artefact of the self-selected pool rather than a causal link. (5) Failure share is essentially uncorrelated with reported volume (r = 0.033) and with Hard-Mode share (r = 0.016): a day's difficulty is independent of how many people reported, reinforcing that difficulty is a property of the word, not the crowd. (6) Extreme words: the most-failed word is 'parer' (48% could not solve in six tries — a low-frequency, letter-scarce word) and the least-failed is 'thorn' (0%); the largest 1-try share anywhere is only 6%, so 'one-try' solves are a rarity. (7) Overall, only 5.60% of all reported scores were in Hard Mode (weighted), and 179 of 359 days have rounded percentages that sum to exactly 100 — the other 180 deviate by up to 26 points, confirming the percentages are rounded and not a true probability simplex, which is why Q3 normalises predictions. (8) The single lowest-volume day (2,569 reports, Nov 30) is an outlier of a factor ~10 below the year-end norm, almost certainly a Twitter-mining gap rather than real player behaviour; it is the only day below 10,000 reports.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
