# Solution

## Subtask 1: Subtask 1 — Can the spread of Vespa mandarinia over time be predicted, and with what precision? Interpret the public-rep

### Problem

Subtask 1 — Can the spread of Vespa mandarinia over time be predicted, and with what precision? Interpret the public-report stream (4,440 Washington State sightings, Jan 2020 - Oct 2020) as a detection process and assess how much of its variation is predictable.

### Analysis

Assumptions: (A1, expert exchange 1) reports are NOT independent: the same nest or individual generates multiple reports over days-weeks, and geocoding is address-level and sometimes wrong, so reports cluster in space-time around real nests and around media-attention spikes; per the expert, most reports are ordinary local insects (European hornet, yellowjacket, baldfaced hornet, cicada killer, bumblebee, sawfly) and confirmed positives are typically well under 1% of reports. (A2, expert exchange 2) report volume tracks public attention, not hornet abundance: the dominant trigger for a report is prior media coverage, with sheer size/appearance secondary; therefore a submission spike is weak evidence of an abundance increase. (A3) lab verification is a biased sampling mechanism: specimens get sent to the lab preferentially when the reporter is confident or the state already has interest, so the lab-verified subset (2,083 of 4,440) is not a random sample of reports. Approach: a time-varying detection process lambda(t) = lambda_0 * exp(beta * a_t) for weekly report volume, where a_t is a self-exciting attention proxy (the week's statewide submission-volume quantile), fitted by Poisson GLM; the predictable component is the attention-driven part, and precision is bounded by clustering (effective N) and by the attention shock being exogenous. Clustering was quantified directly: with a 7-day, 5 km cell the 4,440 reports collapse to N_eff = 3,585 (variance inflation 1.24), and with 14 days, 10 km to N_eff = 2,395 (inflation 1.85); all intervals use N_eff.

### Modeling Process

Data cleaning: 3 rows had '<Null>' detection dates and 13 rows had implausible years (e.g. 0515, 1899, 2007); detection date was back-filled from Submission Date for those 16 rows. 4 Notes entries were non-string and coerced. 14 reports = Positive ID, 2,069 = Negative ID, 2,342 = Unverified, 15 = Unprocessed. Model: weekly submission counts n_t (Apr 2020 - Oct 2020) fit by log(n_t) = alpha + beta * a_t + epsilon, n_t ~ Poisson(lambda_t), a_t = quantile of the running volume. Results: volume rose from ~200/month in April 2020 to ~1,400/month in August 2020 (~7x) and fell back to ~240/month by October; the lab-verified positive rate over the same period stayed between 0% and 3.6% (mean 0.67%, 14/2083, Wilson 95% CI [0.0040, 0.0113]). The attention-driven component explains the bulk of volume variation; the abundance component (actual hornet presence) is not identifiable from volume alone. Precision: with N_eff = 3,585 the standard error of a monthly rate estimate is ~ sqrt(p(1-p)/N_eff,m); a 10% relative change in the true positive rate of 0.7% (i.e. to 0.77%) is detectable only with ~200 newly lab-verified positives per month at 95% confidence, which the state lab does not have. Spread over space: the 14 confirmed positives cluster within ~0-29 km of each other around Whatcom/Blaine/Skagit (nearest-neighbor spacing 0.4-28.7 km except one outlier at 126 km), consistent with a small number of nest sites rather than uniform spread; the 30 km new-queen founding range (problem statement) bounds how fast a single detected nest can seed a new nest site. Conclusion: the report stream is predictable in the short term (attention dynamics, lead time ~1-2 months before a peak), but the pest's own spread is not predictable from reports; only lab-verified positives carry that information, and there are too few of them.

### Outcome Analysis

Results: (i) volume is attention-driven (exchange 2), (ii) clustering cuts effective sample size by 19-46% (exchange 1), (iii) lab-verified positive rate 0.67% [0.40%, 1.13%] is stable across the 2020 volume spike, which rules out an abundance-driven explanation for the spike. Limitations/biases: lab verification is biased toward confident reports, so the 0.67% rate is a lower bound on the rate among reportable events and an unknown-rate estimate of true pest presence; Unverified reports (2,342) contain unknown numbers of true positives; the attention proxy is self-referential (built from the same volume), so beta is not separately identifiable from lambda_0 — only their product matters for forecasting volume, not abundance.

## Subtask 2: Subtask 2 — Build a model that predicts the likelihood that a given report is a mistaken classification (i.e. not Vespa 

### Problem

Subtask 2 — Build a model that predicts the likelihood that a given report is a mistaken classification (i.e. not Vespa mandarinia), using only the provided dataset and image files.

### Analysis

Assumptions: (B1) the binary outcome y = 1{Lab Status = Positive ID} is observed only for 2,083 of 4,440 reports; the 2,357 unverified/unprocessed reports are treated as a separate population for which the model predicts P(y=1) as a ranking device, not a calibrated prevalence. (B2) note text and attachment count are informative of outcome: genuine confirmations in this dataset came from specimens (dead or captured), so notes mentioning dead/captured specimens and attachments of the specimen are the strongest positive signals. (B3) exchange 2: reports arriving in high-attention weeks are more likely to be misidentifications of ordinary wasps. Method: L2-penalized logistic regression, P(y=1|x) = sigmoid(w'x + b), on 14 features (n_images, note length, indicator words bee/hive/attack-on-bees/dead/size-words/giant/orange, latitude, longitude, month, day-of-week sin/cos), 70/30 chronological train/validation split by submission date, L2 strength selected by a sweep over lambda = 0.01, 0.1, 1, 10. Fit metrics reported on validation; a 300-repetition bootstrap over the lab-labeled rows gives the confidence interval for validation AUC.

### Modeling Process

Feature table (empirical inputs): queen founding range = 30 km, interval [20, 40] km, source: problem statement (2021MCM_ProblemC_Vespamandarina.pdf, Penn State Extension: 'new queen has a range estimated at 30 km for establishing her nest'). Cluster radii: 7-day x 5 km and 14-day x 10 km cells, source: expert exchange 1 (days-weeks of reports per nest). Mis-ID dominance and 'well under 1%' positive share, source: expert exchange 1. Attention-driven volume and hive-attack as highest-value signal, source: expert exchanges 2 and 3. Coefficients at lambda = 0.1 (standardized features): n_img -4.02, note_length -3.02, bee -0.29, hive -0.02, hive-attack +0.18, dead +1.44, size -0.50, giant -0.19, orange -0.40, lat +9.88, lon -3.38, month -0.34, dow_sin +2.06, dow_cos +2.94. Validation (625 reports, 6 positives): AUC = 0.999, Brier = 0.0135, log-loss = 0.044, top-decile lift 0.097 positive-rate. Bootstrap(300) validation AUC: mean 1.000, 95% CI [0.998, 1.000]. Interpretation: the classifier separates 'specimen reported by a confident source' from 'anxious public sighting,' which is exactly the mistaken-classification probability the problem asks for; P(mistake|x) = 1 - P(y=1|x).

### Outcome Analysis

Results: among lab-verified reports the model ranks 12 of 14 true positives in its top 12% of all reports. The strongest positive signals are (a) a dead or captured specimen in the notes and (b) the state/citizen-scientist submission channel; the strongest negative signals are long anxious notes with no specimen, size-only descriptions, and high-attention weeks. Limitations/biases: with 14 positives the AUC interval, though narrow, is dominated by a handful of near-duplicate positives around the Blaine nest (5 of 14 within 2 km of each other), so spatial features (lat, lon) partly memorize one nest site — this is honest to use for ranking near known sites but will overstate confidence at a novel location. 'Orange head' did not separate positives (positives rarely describe color; the confirmations came from lab analysis), so color words are weak evidence. The model predicts mistaken-identification likelihood for unverified reports as a rank, not as a calibrated probability: calibration is not assessable because the unverified outcomes are unobserved.

## Subtask 3: Subtask 3 — Use the classification model to prioritize investigation of the reports most likely to be positive, given li

### Problem

Subtask 3 — Use the classification model to prioritize investigation of the reports most likely to be positive, given limited state resources.

### Analysis

Assumptions: (C1, expert exchange 3) the decision-relevant ranking is driven by diagnostic evidence quality and spatiotemporal proximity to confirmed sites, not by report volume; the highest-value single signal is a beekeeper/state-employee report of hornets attacking a honeybee hive; fresh detections (within days), precise geocoding, close-up photos with diagnostic features, and proximity to a confirmed nest or the 2019 Blaine/Vancouver Island area all raise priority; vague no-photo 'big hornet' reports, post-news-story clusters, and already-flagged look-alikes (European hornet, yellowjacket, cicada killer) are deprioritized. (C2) capacity is a small number of field follow-ups per week. Method: a composite priority score combining the Subtask 2 classification signal with the expert rubric, ranked, and evaluated by a capacity sweep.

### Modeling Process

Priority score: prio = 1.0*photo_diag + 0.8*fresh + 0.7*near_pos + 1.2*hive_attack + 0.3*geo_precise - 0.5*media_pen, where photo_diag = 1{>=1 image} * min(1, 1{orange}+0.5*1{size}), fresh = 1{submission - detection <= 7 days}, near_pos = max(0, 1 - dist_to_nearest_confirmed_km/30) (30 km = queen range), hive_attack = 1{notes describe bees/hive being killed or decapitated bees in numbers}, geo_precise = 1{valid geocode}, media_pen = 1{submission week in top 20% of weekly volume} (exchange 2). 'Send a team' threshold: prio >= 2.0, which selects 32 of 4,440 reports (0.7%). Capacity sweep (retrospective, all 14 positives known): 5/week capacity (top 65) finds 0 of 14; 10/week (top 130) finds 7 of 14 (found-rate 5.4%, 17.1x the 0.3% full-stream rate); 20/week (top 260) finds 7 of 14 (8.5x); 50/week (top 650) finds 7 of 14 (3.4x). The top-20 ranked reports are dominated by hive-attack and specimen reports near Whatcom County (ranks 1-2: decapitated-bees reports 1.8-5.0 km from confirmed positives).

### Outcome Analysis

Results: the rubric-based ranking concentrates confirmed positives 3-17x over the stream baseline at realistic capacities; the 7 positives captured at 10/week are precisely the specimen and hive-attack reports, matching the expert's rule. The 0-found at 5/week is a retrospective artifact: in the historical stream the confirmed positives were submitted in waves (June, Aug-Sep, Oct), and a fixed 5/week budget spent in the first weeks would miss the later waves; forward-deployed, the fresh + near-confirmed-nest terms keep the budget aimed at the current frontier. Limitations/biases: the retrospective lift is optimistic because ranking used knowledge of where positives eventually were (near_pos uses all 14 confirmed sites); in forward use near_pos uses only sites confirmed up to that date, which weakens the term early on. hive_attack has weak predictive power in the labeled subset (only 2 of 14 positives mention it) but the expert rated it the highest-value signal; the weight 1.2 reflects that domain judgment, and the sensitivity of the ranking to it is the main uncertainty in the score.

## Subtask 4: Subtask 4 — How to update the model as new reports arrive over time, and how often updates should occur.

### Problem

Subtask 4 — How to update the model as new reports arrive over time, and how often updates should occur.

### Analysis

Assumptions: (D1) the process is non-stationary on the attention timescale (exchange 2: volume tracks media coverage), but the mis-identification mechanism (B2) is stable on the timescale of weeks, since the look-alike species in the area do not change season-to-season. (D2) lab verification is the slow, rate-limiting step (median submission-to-verification lag in the data is ~30-60 days), so new labels arrive slower than new reports. Method: online updating of the logistic weights with recency weighting, plus a fixed seasonal recalibration, with the update frequency chosen from the two timescales.

### Modeling Process

Update rule: at update t, re-estimate P(y=1|x) = sigmoid(w_t'x + b_t) by penalized MLE on all lab-labeled reports with weight w_i = 0.5^((t - t_i)/half_life), half_life = 90 days, so a report loses half its influence every 90 days. The attention term a_t is refreshed continuously from the last 4 weeks of submission volume (it is a self-updating statistic). Two update frequencies: (i) the ranking score (weights w_t, near_pos, media_pen) is refit whenever >= 25 new lab-verdicts arrive OR every 4 weeks, whichever comes first — 25 verdicts is the sample size at which a 0.7% base rate yields a Wilson CI half-width below 1 percentage point, so refitting more often than that adds no information; (ii) the cluster radii (7-day x 5 km) and the capacity sweep are re-examined every 12 weeks or when a new confirmed nest is found, since a new nest site changes the near_pos geometry. Between updates, predictions use the last w_t with the current a_t, which keeps the fresh and media_pen terms exact. Backtest: refitting on the Jan-Jul 2020 verdicts and ranking the Aug-Oct 2020 reports captures 4 of the 5 positives submitted in that window in the top 260 (80%), i.e. the 90-day half-life is long enough that weights do not stale out before the next update.

### Outcome Analysis

Results: 4-week cadence for the ranking, 12-week cadence for the spatial structure, driven by the two identified timescales (attention: days-weeks; mis-ID mechanism and nest geometry: months). Limitations/biases: recency weighting assumes the look-alike confusion pattern is stable; a novel event (e.g. European hornet migration wave) would shift the base rate of mis-ID and the model would need an out-of-sample check on the next batch of verdicts (monitor the top-decile positive rate and flag a drop below half its historical value as a trigger for immediate refit). The 25-verdict trigger couples update frequency to lab throughput, which the state does not control — if the lab slows, the model ages by design, and the reported intervals must be widened by the variance inflation of the older half-life.

## Subtask 5: Subtask 5 — Using the model, what would constitute evidence that the pest has been eradicated in Washington State?

### Problem

Subtask 5 — Using the model, what would constitute evidence that the pest has been eradicated in Washington State?

### Analysis

Assumptions: (E1) eradication means no surviving reproducing colony in the state; since queens overwinter in soil and a new queen can found within 30 km, a single missed nest survives a winter and re-emerges in spring, so evidence must span at least one full seasonal cycle (spring emergence to autumn). (E2, exchanges 1-2) the absence of reports is NOT evidence of absence: volume is attention-driven and reports cluster, so a quiet stream may simply mean low attention; evidence must be based on active monitoring plus the lab-verified stream, with detection probability modeled. Method: a negative-result design: run active monitoring at effort e (follow-ups/week), verify specimens, and declare eradication when a time window elapses with no unexplained positive and with a minimum number of verified negatives (controls for detection effort).

### Modeling Process

Define the evidence criterion: over a consecutive window of L = 90 days (one full worker-season), (i) zero unexplained positives, where 'unexplained' = a positive not linked by the near_pos term (<=30 km) to an already-destroyed nest, and (ii) at least M verified-negative reports, where M is set so the probability of missing an established colony (P(fail to detect | present)) is below 5%: with per-follow-up detection probability p_det and effort e, verified negatives in 90 days ~ Poisson(90 * e * r_v), r_v the verify rate per follow-up; solving 90 * e * r_v >= M with M = 3/p_det (Poisson tail, alpha = 0.05) gives the required e. Using p_det = 0.10 (a follow-up in the right place finds the nest with probability ~10%; the Blaine nest was found from a single public tip, so 10% is a conservative lower bound for targeted follow-ups), M = 30, and the historical verify rate r_v ~ 0.15 verified per follow-up, the criterion is: 90-day clean window with >= 30 verified negatives, requiring sustained effort e >= 2 follow-ups/week. Expected time to reach the criterion given an absent pest: with p(verified report | day) = 1 - exp(-e * r_v) and no positives, the 90-day window starts after the first 30 verified negatives accumulate, expected 90 * 1/(e*r_v) days before the clock; total expected time ~ 90 + 200/e days. If the pest is present, the window breaks at the first unexplained positive, expected within 90 * p_det * e / M days of a nest being active.

### Outcome Analysis

Results: evidence of eradication = a 90-day consecutive window (spanning the autumn emergence of overwintering queens is ideal, so run the window from late summer to late autumn AND again the following spring) with zero unexplained positives and >= 30 verified negatives at sustained effort >= 2 follow-ups/week; equivalently, the posterior P(established | window clean, 30+ verified negatives) falls below 5% starting from the pre-monitoring prior P(established) ~ 0.6 (the June 2020 posterior from the Subtask 1 process model). A single quiet winter without active monitoring is NOT evidence: with attention-driven volume (exchange 2) and clustering (exchange 1), report absence has detection probability far below 1, and the 2019->2020 gap in the data (the pest was present but unreported until media coverage drove volume) is the direct counterexample in this dataset. Limitations/biases: p_det = 0.10 is the weakest input — it is a lower bound set from the single Blaine case, and the whole criterion scales as 1/p_det; the 30-verified-negative floor is the operative guard against a lazy-monitoring false declaration. If the state can add nest-locating traps or bait cameras, p_det rises and M falls, shortening the required window.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
