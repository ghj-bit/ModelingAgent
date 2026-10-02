# Solution

## Subtask 1: Part 1: Explain the daily variation in the number of reported Wordle results and produce a prediction interval for the n

### Problem

Part 1: Explain the daily variation in the number of reported Wordle results and produce a prediction interval for the number of reported results on March 1, 2023.

### Analysis

The daily count N_t is a self-selected Twitter sample, so it is modelled as a count with a non-constant mean. Per the expert's operational clarification (exchange 1), postings are not a uniform stream: they arrive in bursts tied to the day's routine, so the daily total reflects how many people played-and-posted that day, driven by calendar routine rather than a constant arrival rate. Per the causal clarification (exchange 2), the dominant drivers of day-to-day variation are the player-base level and its time trend plus weekday/weekend routine, with word recognizability a secondary effect; genuine difficulty does not dominate the count. The model is therefore a log-linear trend-plus-day-of-week regression, fit by ordinary least squares on log counts, with residual spikes identified as viral days. March 1, 2023 is a Wednesday, 395 days after the first puzzle; the trend is extrapolated from the data period and the day-of-week coefficient for Wednesday applies.

### Modeling Process

log(N_t) = a + b*t + sum_{j=1}^{6} gamma_j * I(dow = j) + eps_t, t = (Date - 2022-01-07)/365, dow coded Mon..Sun with Sunday as reference, eps_t ~ N(0, s^2). OLS estimate: a = 12.426, b = -2.874 per year, s = 0.298 (log units). Day-of-week coefficients (Mon..Sat vs Sunday): +0.018, -0.009, +0.016, +0.012, -0.023, -0.035. For March 1, 2023 (Wednesday, t = 1.082): mu = exp(12.426 - 2.874*1.082 + 0.016) = 9193. 80% prediction interval on the log scale, using z = 1.282: N in [exp(mu - 1.282*0.298), exp(mu + 1.282*0.298)] = [6274, 13469]. Validation: a backtest in which the last-fit model is trained on days 31-359 and applied to the first 30 days gives 30/30 (100%) coverage of the 80% interval, so the interval is, if anything, conservative in-sample. Parameter table (all from the supplied dataset unless noted): a = 12.426, interval [12.40, 12.46], source: OLS fit to Problem_C_Data_Wordle.xlsx; b = -2.874, interval [-2.95, -2.80], source: OLS fit to the same file; s = 0.298, interval [0.28, 0.32], source: OLS residual standard deviation; day-of-week coefficients as above, source: same fit; z(90th pct) = 1.282, interval [1.28, 1.29], source: standard normal quantile; planning-usefulness band of roughly +/-20-30% usable up to about +/-50% of the point estimate, source: expert exchange 3.

### Outcome Analysis

Point estimate for March 1, 2023: about 9,193 reported results; 80% prediction interval [6,274, 13,469], i.e. roughly -32% / +47% of the point. Against the planning threshold from expert exchange 3 (usable up to about +/-30%, not useful beyond about +/-50%), the upper half-width sits at the border of usefulness and the interval is planning-grade, not operational-grade. The main structural finding is that the Twitter-reported base declined steeply through 2022: the January-February 2022 monthly mean of daily counts is about 260,409, while the November-December 2022 mean is about 24,023, a decline of roughly 91%. The trend coefficient of -2.87 per year (log units, about -24% per month) is the driver. The February 2022 viral window is the one genuine upside spike in the year: 'shake' (2022-02-17) recorded 342,003 reports, z = +2.10, and the top five all-time counts (moist 361,908; pleat 359,679; shard 358,176; those 351,663; shake 342,003) all fall in early-to-mid February 2022. The lowest day is 'study' (2022-11-30) with 2,569 reports. Weekday means (Mon..Sun): 90,320 / 92,754 / 93,844 / 91,749 / 91,342 / 88,160 / 88,308 - a mild weekday peak on Wednesday and a small weekend dip, consistent with routine-driven posting. Limitations: (i) the 2022 decline is a single, unexplained collapse - the model extrapolates it linearly in log time, so the interval inherits whatever causes the collapse (platform shift, game aging) continuing unchanged; (ii) the interval excludes rare viral spikes, so on a viral day the true count can exceed the upper bound by an order of magnitude; (iii) the self-selection of reporters means N_t tracks the Twitter-playing subset, not all players; (iv) coverage was validated only in-sample on the early high-volume regime, so it may overstate precision for the low-count regime the forecast lands in.

## Subtask 2: Part 2: Determine whether word attributes affect the percentage of scores reported in Hard Mode, and if so how; if not, 

### Problem

Part 2: Determine whether word attributes affect the percentage of scores reported in Hard Mode, and if so how; if not, why.

### Analysis

The hard-mode share h_t = (Number in hard mode)/(Number of reported results) is a proportion in [0,1] with strong daily overdispersion (day-level values range from 1.2% to 93.6%, mean 7.76%), so it is modelled as a weighted logit, with weights equal to the daily sample sizes, regressed on word attributes and a weekend indicator. Per the causal clarification (exchange 2), word familiarity and difficulty are confounded with the composition of the player base, so word attributes are treated as plausible but not cleanly causal drivers; only coefficients robust under that caveat are reported as effects.

### Modeling Process

logit(h_t) = sum_j beta_j x_tj, x_tj in {unique letters, repeated letters, has double, number of vowels, rare consonant (q,x,z,j), letter-position entropy, e-count, s-count, weekend}, no intercept (coefficients identified relative to the sample mean share, whose logit is b0 = -2.475). Fitted by IRLS with day-size weights; standard errors from the sandwich (robust) form. Results: repeated letters beta = -0.520, z = -3.37 (OR = 0.595) - the only statistically significant attribute; e-count beta = +0.071, z = +1.54 (OR = 1.073) and rare consonant beta = +0.190, z = +1.40 (OR = 1.210) - suggestive, not significant at 5%; unique letters beta = -0.809 (z = -0.83), double (z = -0.27), vowels (z = +0.01), entropy (z = +0.24), s-count (z = -0.11) and weekend (z = -0.08) - no evidence of an effect. Parameter table: all coefficients, intervals and z-scores as listed, source: weighted logit fit to Problem_C_Data_Wordle.xlsx (359 days, weighted by daily reported counts).

### Outcome Analysis

Yes, word attributes do affect the hard-mode share, but weakly. The robust finding is that words with repeated letters are played in hard mode less: each repeated letter multiplies the odds of hard-mode use by about 0.59 (z = -3.4). The direction is consistent with the expert's self-selection account (exchange 2): a word with repeated letters is typically more familiar or easier to crack, and players switch to hard mode when they want a challenge, so easy-looking words are played in regular mode. The e-count and rare-consonant coefficients are suggestive in the same qualitative direction (words with more e's or an uncommon letter look harder, drawing slightly more hard-mode use) but do not reach significance. Attributes such as vowel count, letter uniqueness, doubles per se and weekend do not matter. Caveats: (i) the day-level shares are extremely overdispersed - 93.6% on some small-sample days, 1.2% on others - so most daily variation is sample noise, not a word effect, and the significant coefficient is the one with the cleanest signal; (ii) because the player base's composition shifts over the year (see Part 1), the word effect is entangled with time and is read as an association; (iii) the model extrapolates for words with attribute values outside the 2022 range (e.g. EERIE, with 3 e's and 3 repeated letters, is predicted a hard share of about 0.6% before clipping to the observed range), so predictions for such words are bounded by the observed 1.2-93.6% range rather than the raw model value.

## Subtask 3: Part 3: Build a model to classify solution words by difficulty, identify the word attributes associated with each class,

### Problem

Part 3: Build a model to classify solution words by difficulty, identify the word attributes associated with each class, apply it to EERIE, and discuss accuracy. Also predict, with confidence, the try-count distribution (1..6, X) for EERIE on March 1, 2023.

### Analysis

Difficulty is measured from the outcome the players themselves produce - the distribution of solves over tries - rather than from the reported count, which is dominated by self-selection (exchange 2). The score is the try-weighted mean plus a tail penalty, difficulty_t = sum_i i * p_i + 2 * p_X. Unsupervised clustering (KMeans on standardized [mean tries, X-share]) separates the words, and a decision tree on word attributes provides the classification rule and the attribute interpretation. The two-class split was chosen over k = 3, 4, 5 by both silhouette and holdout accuracy: k = 2 gives silhouette 0.599 and holdout accuracy 0.900, versus 0.497/0.667 (k = 3), 0.498/0.633 (k = 4), 0.443/0.567 (k = 5).

### Modeling Process

difficulty_t = mean_tries_t + 2 * X_share_t, with mean_tries = 1*p1 + ... + 6*p6 + 7*pX. KMeans(k = 2) on standardized (mean_tries, X_share); the cluster with the lower mean score is 'easy' (302 words), the higher 'hard' (57 words). Classification rule: a depth-4 decision tree on 13 word attributes (unique, repeated, double, vowels, rare consonant, letter entropy, e/s/o/t counts, starts-vowel, max letter run, has-vowel). Feature importances: letter entropy 0.245, vowel count 0.155, starts-vowel 0.112, t-count 0.103, s-count 0.096, rare consonant 0.091, e-count 0.075, repeated 0.050, double 0.042, o-count 0.032. EERIE's features: 3 unique letters, 2 repeated, 4 vowels, 1 double (E-E), starts with a vowel, 3 e's, letter entropy 0.950, max run 3 -> the tree classifies it HARD. Distribution prediction for EERIE on March 1, 2023 = mean of the 57 hard-class words, in percent: 1 try 0.3, 2 tries 2.7, 3 tries 12.3, 4 tries 25.1, 5 tries 28.1, 6 tries 22.3, X 9.2. Parameter table: k = 2, silhouette 0.599, holdout accuracy 0.900, source: KMeans + decision-tree fit to Problem_C_Data_Wordle.xlsx (sweep over k = 2..5); class-attribute profile means, source: same file, per-class averages.

### Outcome Analysis

The two difficulty classes: easy (302 words) - mean 4.07 tries, only 1.6% failed (X), 4.75 distinct letters on average, few repeated letters (0.25), 10% contain a double, 5% a rare consonant; examples: wedge, enjoy, comma, waltz, epoxy. Hard (57 words) - mean 4.82 tries, 9.2% failed, 4.42 distinct letters, 0.58 repeated, 18% with a double, 12% with a rare consonant; examples: parer, mummy, foyer, coyly, judge. The attributes that separate them are letter diversity and repetition: hard words are less diverse, repeat letters more, and more often contain a rare consonant - exactly the letters that are hard to place. EERIE is classified HARD: its low letter entropy (0.950, only 3 distinct letters), 4 vowels, and the E-E run put it with words like mummy and parer. Prediction for March 1, 2023: roughly 1/3 of reporters solve it by try 3, the mode is the 5th try (28.1%), and about 9.2% fail; the class-level standard deviations (e.g. X: 7.3 percentage points) show the within-class spread, so a realistic 95% band for the X share is about 9.2 +/- 14.6 points. Confidence: the classifier itself is reliable (0.900 holdout accuracy), but the distribution prediction is a class-average, not an EERIE-specific fit, so treat individual cells as accurate to within about +/-5-7 percentage points and the X share to within about +/-10-15 points; the model cannot see EERIE in the training data, and no 2022 word contains the pattern of 3 e's plus a double in this combination.

## Subtask 4: Part 4: List and describe other interesting features of the data set.

### Problem

Part 4: List and describe other interesting features of the data set.

### Analysis

Descriptive scan of the 359-day file after cleaning (one day - the row whose try percentages did not sum to 100 within rounding - was renormalized; no missing values, no duplicate contest numbers or dates).

### Modeling Process

No fitted model; direct summary statistics over the dataset: monthly means of the reported count, extreme days, weekday means, two-try and X-share leaders, and the hard-mode share range. All values are sample means/quantiles of Problem_C_Data_Wordle.xlsx.

### Outcome Analysis

(1) The defining feature of 2022 is the collapse of the Twitter-reported base: the daily-count mean falls from about 260,409 in Jan-Feb to about 24,023 in Nov-Dec (about 91% decline), with a single dramatic low point on 'study' (2022-11-30, 2,569 reports) and the all-time low December values (extra 15,554; havoc 20,001; judge 20,011; impel 20,160). (2) The February 2022 viral window: the top five counts of the year are all in February - moist (2022-02-02, 361,908), pleat (02-04, 359,679), shard (02-03, 358,176), those (02-01, 351,663), shake (02-17, 342,003) - roughly ten times the late-year base. (3) Difficulty is rare but extreme: the mean X share is 2.8%, but 'parer' (2022-09-16) hit 48% failed, and foyer 26%, catch 23%, watch 20%, mummy 18% - the hardest words are obscure or awkwardly-shaped ones. (4) Easy-to-guess words produce high one-and-two-try shares: 'train' (2022-05-04) had 26% on two tries, followed by treat 22%, stair 21%, plant 19%, tash 19%. (5) Weekday rhythm in the count is mild: Wednesday is the busiest day (93,844 mean) and Saturday the quietest (88,160), a spread of only about 6%. (6) Hard-mode usage is a small but volatile minority: the daily share ranges from 1.2% to 93.6% around a 7.8% mean, the extremes occurring on small-sample days.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
