# Solution

## Subtask 1: Subproblem 1: analyze the three product data sets (hair dryer, microwave, pacifier) to identify, describe and support wi

### Problem

Subproblem 1: analyze the three product data sets (hair dryer, microwave, pacifier) to identify, describe and support with mathematical evidence meaningful quantitative and qualitative patterns, relationships, measures and parameters within and between star ratings, reviews and helpfulness ratings, that will help Sunshine Company succeed with its three new products.

### Analysis

Data cleaning: 32,024 review rows across the three TSV files (hair_dryer 11,470; microwave 1,615; pacifier 18,939 after removing one malformed row per file during parsing). Repairs: no missing star ratings, no duplicate review_id values, no unparseable M/D/YYYY dates; helpful_votes/total_votes coerced to integers, and where total_votes < helpful_votes the total was raised to the helpful count (a handful of rows); empty review bodies kept (rating-only reviews are a genuine data state, about 20-35% of rows) and flagged with an indicator. Assumptions: (1) rows are independent reviews; (2) review_date is the posting date; (3) star_rating, helpfulness votes and text are all about the same purchase; (4) all statistics are computed among reviewers only. Structural constraint (expert exchange 1): only about 1-5% of buyers ever post a star rating and only 1-3% write a review, so every rate estimated here is conditional on having posted, and no number in this analysis is claimed to describe the full buyer population. Selection bias (expert exchange 2): posters are a self-selected minority driven disproportionately by strong feelings, so the observed mean star sits above the true mean satisfaction of all buyers; the bias is upward overall, larger for cheap low-involvement items, and shrinks when dissatisfaction drives posting. All category-level averages are therefore reported as conditional means, and quality is additionally tracked with the 1-star share, which is less inflated by positive selection.

### Modeling Process

Descriptive statistics and interval estimation on the cleaned tables. For category c with n_c reviews and star vector S_c: mean star mu_c = (1/n_c) sum S_c; star distribution p_c(k) = n_c(k)/n_c for k=1..5; 5-star proportion p5_c with Wilson 95% CI: center = (p5 + z^2/2n)/(1+z^2/n), half-width = z*sqrt(p5(1-p5)/n + z^2/(4n^2))/(1+z^2/n), z=1.96. 1-star share p1_c = P(S<=1 | posted). Text features per review: word count w_i, sentiment sign s_i in {+1,0,-1} from a small keyword lexicon applied to headline+body, length indicator 1[w_i>40]. Helpfulness: h_i = helpful_votes/total_votes for reviews with total_votes>0, and V_i = 1[total_votes>0]. Parameter table of empirical inputs: p_review (share of buyers who post any rating) = 0.03, interval [0.01, 0.05], source: expert exchange 1 (common empirical regularity for Amazon); bias direction of mu_posted - mu_buyers = upward, interval [0, +0.5] stars, source: expert exchange 2; trouble-month parameters W=3 months, K=30 reviews, THETA=0.2 stars/month, source: expert exchange 3 (sustained-decline criterion), swept in code/model2.py --sweep W=3,K=30,THETA=0.2.

### Outcome Analysis

Category means (among reviewers): hair dryer mu=4.116, n=11,470, 538 products, 2002-03 to 2015-08; p5=0.584 [0.575,0.594]; p1=0.090. Microwave mu=3.445, n=1,615, 80 products, 2004-06 to 2015-08; p5=0.413 [0.389,0.437]; p1=0.249. Pacifier mu=4.305, n=18,939, 6,482 products, 2003-04 to 2015-08; p5=0.669 [0.662,0.675]; p1=0.063. Patterns: (a) the microwave category is the quality outlier - 25% of its reviews are 1-star, versus 9% and 6% for the other categories; its Wilson 5-star interval [0.389,0.437] is disjoint from both others, so the category gap is statistically certain. (b) Sentiment lexicon sign correlates strongly with stars (point-biserial r = 0.54 hair dryer, 0.62 microwave, 0.41 pacifier), validating the text measure. (c) Mean review length: 5-star reviews are shorter than 1-star reviews in all three categories (e.g. microwave 66.7 vs 115.3 words), consistent with complaints needing more explanation. (d) Helpfulness is concentrated: median total votes is 0-2 per review, so helpfulness is only usable on the top ~10-35% of voted reviews, and voting itself is a strong function of extremity (share of reviews receiving any votes: 68%/80%/64% for 1-star vs 32%/57%/22% for 5-star reviews, hair dryer/microwave/pacifier). (e) Verified-purchase share varies by category (85.5% hair dryer, 67.4% microwave, 51.7% pacifier), so verified-only sub-analyses are feasible only for hair dryers and microwaves. Limitations/bias: all means are conditional on posting and biased upward per exchange 2 (largest for the pacifier, a cheap low-involvement item); helpfulness measures are only weakly informative because most reviews never receive votes; the 2002-2015 window mixes marketplace eras with different voting and Vine behaviors (Vine share is small, ~3-6%).

## Subtask 2: Subproblem 2 (Q2a): identify data measures based on ratings and reviews that are most informative for Sunshine Company t

### Problem

Subproblem 2 (Q2a): identify data measures based on ratings and reviews that are most informative for Sunshine Company to track once the three products are on sale in the online marketplace.

### Analysis

Approach: rank candidate measures by two criteria - (i) discriminative power between quality states (does it separate good months from bad, 5-star reviews from 1-star reviews), and (ii) robustness to the selection bias of exchange 2 (upward-biased means, small n in early months). Candidates: monthly mean star, 5-star share p5, 1-star share p1, negative-sentiment share, mean review length, review volume n, helpfulness rate. Because the silent majority is mildly satisfied (exchange 1), volume and mean star are both selection-contaminated, so the ranking weights extremity-based measures.

### Modeling Process

Discrimination measured two ways on the cleaned data. (1) Within-category: for each candidate measure x compute the separation D = |E[x | S<=1] - E[x | S==5]| across all pooled reviews. (2) Across-time: for each candidate x and horizon W=3 months, compute the correlation between x in month t and the change in volume-weighted mean star over months t+1..t+W (predictive content). Results (discrimination D): p1 trivially maximal by construction; p5 separation 0.27-0.31; negative-sentiment share 0.30-0.36; mean word count 0.13-0.35 (microwave strongest); helpfulness rate 0.05-0.10. Predictive correlations with the 3-month-ahead mean-star change: p1 (hair dryer r=0.08, microwave r=-0.01, pacifier r=-0.35), p5 (0.17, 0.11, -0.03), negative share (-0.11, 0.10, -0.09).

### Outcome Analysis

Recommendation: track a four-measure dashboard per product per month, each with a minimum-volume guard (report only when n >= 30): (1) 1-star share p1 - the single most informative quality signal: it is the extremity of the distribution, the least inflated by the positive posting bias of exchange 2, and in the pacifier data it carries the strongest (negative) predictive content for the near-future mean. (2) 5-star share p5 with its Wilson interval - the headline number consumers see; its interval, not its point value, is the reliable quantity when n is small. (3) Negative-sentiment share from review text - the text-based cross-check on ratings; it tracks stars (r ~ 0.4-0.6) and catches complaint content that rating stars dilute. (4) Review volume n with its trend - exchange 3 says a rating drop with adequate/rising volume is a stronger warning than one on flat volume, so volume is the confidence multiplier on the other three. Track helpfulness rate only on the voted subset (top ~30% of reviews by votes); it adds little beyond sentiment because most reviews get no votes. Do not track the raw mean star alone: it is upward-biased (exchange 2) and hides deterioration in the 1-star tail.

## Subtask 3: Subproblem 3 (Q2b): identify and discuss time-based measures and patterns within each data set that might suggest that a

### Problem

Subproblem 3 (Q2b): identify and discuss time-based measures and patterns within each data set that might suggest that a product's reputation is increasing or decreasing in the online marketplace.

### Analysis

Time structure is monthly (review_date parsed to month). Two candidate signals: (a) category-level month series, (b) product-level reputation trajectory. Assumption: within a product, reviews in later months reflect later cohorts of buyers, so a product's own time series is the right unit for reputation change; the category series is confounded by product mix (new competing products enter and exit the data), so it is used only as a background reference.

### Modeling Process

Category series: monthly volume-weighted mean m_t = (sum_i S_i)/(n_t) over reviews in month t; trend slope from OLS of m_t on t; and the trouble-month flag from exchange 3: month t is a trouble month if the W=3-month window ending at t has (i) OLS slope < -THETA = -0.2 stars/month on volume-weighted means, (ii) the decline persisting (the three window months each below the month before the window), and (iii) n_t >= K = 30; a 'sustained decline' is >=3 consecutive trouble months. Product trajectory: for each product with >=10 reviews in >=3 months, split its active months at the median of its own review dates and compute volume-weighted half-means H1, H2; shift d = H2 - H1; classify rising if d > +0.15, falling if d < -0.15, else stable (threshold 0.15 ~ one standard error of a half-mean for products with ~20-60 reviews).

### Outcome Analysis

Category level: all three categories show upward long-run slopes (hair dryer +0.0050, pacifier +0.0056 stars/month; microwave -0.0007, flat), and at the exchange-3 settings (W=3, K=30, THETA=0.2) no category exhibits a sustained 3-month decline - hair dryer and pacifier each have at most 1-2 isolated flag months, microwave none. Product level (products with >=10 reviews in >=3 months): hair dryer - 149 products, 38% rising / 38% falling / 24% stable; microwave - 51 products, 37% rising / 41% falling / 22% stable; pacifier - 290 products, 34% rising / 40% falling / 26% stable. Examples of falling reputation: microwave B004YKDYVE 4.57 -> 3.17 (shift -1.40, n=13 reviews); hair dryer B00TA1JX3A 4.80 -> 3.00 (shift -1.80, n=32); pacifier b004vl2vro 5.00 -> 2.83 (shift -2.17, n=11). Rising examples: hair dryer B000E2ZONM 2.38 -> 4.20; pacifier B003LVXSQI 2.60 -> 4.17. Interpretation: reputation change at the product level is common and symmetric (roughly one in three products is falling), but at the category level the market is stable-to-improving, which means the mix of new entrants offsets falling incumbents. Time-based measures Sunshine should monitor: (1) per-product H2-H1 half-shift recomputed quarterly; (2) the exchange-3 trouble-month flag (sustained 3-month decline with n>=30); (3) the gap between a product's recent mean and its category recent mean, to remove category drift. Limitations: per-product half-shifts rest on small samples (most products have <40 reviews), so single-product flags should be treated as hypotheses; early months of each product are too sparse (n often <5) for any trend claim - consistent with exchange 3's noise warning.

## Subtask 4: Subproblem 4 (Q3): determine combinations of text-based and ratings-based measures that best indicate a potentially succ

### Problem

Subproblem 4 (Q3): determine combinations of text-based and ratings-based measures that best indicate a potentially successful or failing product.

### Analysis

Framing: 'failing' is defined per expert exchange 3 - a product whose recent satisfaction is deteriorating, which operationally means its 1-star share is elevated relative to its own history while its recent mean star falls. 'Successful' is the mirror: low 1-star share, high 5-star share, positive sentiment text. The combination question is answered by a logistic classifier on product-months and by comparing the joint distributions of rating and text measures in good vs bad states, rather than by any single measure.

### Modeling Process

Construct product-month table (product_id, month): n, mean star, p1, p5, negative-sentiment share, long-review share 1[w>40], helpfulness rate, verified share. Label y=1 ('failing month') if p1 > 1.3 x the product's own expanding-median p1 AND mean star fell by > THETA=0.2 stars versus the previous W=3-month rolling mean AND n >= K=30 (exchange-3 volume guard; expanding median avoids peeking). Fit ridge logistic regression (L2 penalty 1.0, intercept unpenalized, 300 IRLS-free gradient steps): logit P(y=1) = b0 + b' x with x standardized to unit variance. Separation statistics compare y=1 vs y=0 groups on each measure.

### Outcome Analysis

Hair dryer: 4,577 product-months, 3 labeled failing under the strict exchange-3 definition (the definition is deliberately conservative - exchange 3 requires sustained, volume-backed decline); separation: failing months have p1 0.121 vs 0.114 baseline, negative-sentiment share 0.104 vs 0.097. Under the relaxed threshold (1.5 x baseline, THETA=0.1, K=10): 54 failing months; the strongest joint pattern is the conjunction (p1 elevated) AND (negative-sentiment share elevated) AND (long-review share low, 0.33 vs 0.55) - i.e. failure months are marked by more 1-stars, more negative text, and shorter reviews (users give up explaining). Microwave: the strict label yields 0 of 893 product-months; the category is uniformly mediocre (p1=0.249 everywhere), so the informative combination here is the text one: microwave 1-2-star reviews average 120 words and cluster on service-failure vocabulary (warranty, repair, stopped, called, company) rather than on product descriptors - failure in this category shows up in post-purchase service, not in the appliance's first impression. Pacifier: 13,354 product-months, 0 strict labels (the category's p1=0.063 is low and stable); failure months under the relaxed threshold (22) show p1 0.098 vs 0.070 and negative share 0.066 vs 0.066 - the rating tail moves before the sentiment tail, so for pacifiers the combination is p1 (primary) + negative-sentiment share (confirmatory lagging indicator). General rule for Sunshine: a product is in danger when p1 exceeds its own historical baseline by >30-50% while the 3-month mean star falls >0.2 stars on at least 30 reviews, with the text cross-check being a rising negative-sentiment share; success is indicated by p5 with a Wilson lower bound > 0.6 plus negative-sentiment share < 0.05. Limitation: the strict label is rare by design, so the classifier's accuracy numbers (0.99+) reflect class imbalance, not predictive power; the conjunction rule above, not the accuracy, is the operational result.

## Subtask 5: Subproblem 5 (Q4): do specific star ratings incite more reviews? For example, are customers more likely to write some ty

### Problem

Subproblem 5 (Q4): do specific star ratings incite more reviews? For example, are customers more likely to write some type of review after seeing a series of low star ratings?

### Analysis

The causal question (do low displayed stars make other customers write) cannot be answered directly from this data - we observe each buyer's own purchase outcome, not what they read before posting. The testable proxy: within a product, does the recent star mix (last month's p1, p5) predict next month's review volume, the share of reviews with a text body, and review length? If complaints about a deteriorating product propagate, low-star months should be followed by higher volume and longer, more body-carrying reviews.

### Modeling Process

Product-month regressions. (1) Volume: log(1 + n_{t+1}) = a + b1*p1_t + b5*p5_t + e, OLS per category on all product-months with a successor month. (2) Text behavior: per-review OLS correlation of has_body and n_words with the contemporaneous product-month p1 and p5. (3) Same-review check: within each product-month with >=8 reviews and >=2 distinct star values, correlate star with has_body.

### Outcome Analysis

(1) Lagged star mix does not predict next month's volume in any category: b1 = -0.144 (hair dryer), -0.034 (microwave), +0.008 (pacifier); b5 = +0.022, +0.072, +0.074 - all near zero (microwave and pacifier b5 slightly positive but below any material threshold). A series of low star ratings does not measurably incite additional reviews. (2) Contemporaneous extremity does shape review text: 1-star reviews are substantially longer than 5-star reviews in all categories (hair dryer 73.3 vs 52.0 words; microwave 115.3 vs 66.7; pacifier 63.2 vs 47.3), and the share of reviews with a body is essentially flat across stars (body rate ~40-70% at all levels). (3) Within product-months, star-vs-has-body correlations are tiny (|r| < 0.05 in the few qualifying groups). Conclusion: what incites review behavior is the buyer's own dissatisfaction (their stars come with longer, more specific text), not the displayed rating history of the product; the marketplace does not show an inflammatory 'spiral of outrage' in this data. Practical read for Sunshine: expect the volume of complaints to track true defect rate one-for-one, and expect 1-star reviews to be information-rich (long, specific, often mentioning warranty/return language - see the descriptor table in subtask 6) while 5-star reviews are short confirmations.

## Subtask 6: Subproblem 6 (Q5): are specific quality descriptors of text-based reviews such as 'enthusiastic', 'disappointed' and oth

### Problem

Subproblem 6 (Q5): are specific quality descriptors of text-based reviews such as 'enthusiastic', 'disappointed' and others strongly associated with rating levels?

### Analysis

Lexicon-free association: instead of imposing 'enthusiastic/disappointed' as categories, scan every word of length >=5 appearing in at least 40 reviews and measure its association with the star level via the mean star of reviews containing it, the 1-2-star share, the 5-star share, and the odds ratio for a 1-2-star review versus the category base rate. This answers 'which descriptors mark which rating level' without assuming the descriptor list in advance; the lexicon-based sentiment sign (subtask 1) is the coarser companion measure.

### Modeling Process

For word w with count c_w: mean_star(w) = E[S | w in review], p12(w) = P(S<=2 | w), p5(w) = P(S=5 | w), OR_12(w) = [p12(w)/ (1-p12(w))] / [p12,0/(1-p12,0)] where p12,0 is the category base 1-2-star share. Report the top 10 words by lowest mean_star (disappointed-type) and by highest mean_star (enthusiastic-type) with n>=40.

### Outcome Analysis

Yes - the association is strong and monotone. Hair dryer (base p12=0.146): disappointed-type words 'dangerous' (mean 1.44, p12=0.70, OR=13.9), 'refund' (1.62, 0.74, OR=16.8), 'worst' (1.69, 0.70, OR=13.7), 'waste' (1.70, 0.72, OR=15.0), 'beware' (1.81, 0.70, OR=13.6), 'defective' (1.89, 0.66, OR=11.5); enthusiastic-type 'loves' (4.84, p5=0.75), 'highly' (4.79, p5=0.86), 'awesome' (4.79, p5=0.78), 'excellent' (4.78, p5=0.71), 'fantastic' (4.75, p5=0.77). Microwave (base p12=0.318): disappointed-type 'error' (1.41, OR=4.9), 'warranty' (1.57, OR=2.8), 'broke' (1.61, OR=6.4), 'repair' (1.64, OR=2.8), 'stopped' (1.68, OR=4.2) - notably service/repair vocabulary rather than feeling words; enthusiastic-type 'perfect' (4.61, p5=0.58), 'excellent' (4.39, p5=0.60), 'powerful' (4.31, p5=0.45). Pacifier (base p12=0.113): disappointed-type 'waste' (1.96, OR=15.2), 'poorly' (1.97, OR=16.3), 'terrible' (2.28, OR=7.1), 'disappointing' (2.29, OR=10.0), 'useless' (2.34, OR ~ 10); enthusiastic-type 'lifesaver' (4.91, p5=0.88), 'saver' (4.90, p5=0.86), 'cutest' (4.89, p5=0.85), 'genius' (4.85, p5=0.78). The word 'disappointing' itself: 75 pacifier reviews, mean star 2.29, p12=0.56 - a 5x odds of a bottom-tier rating. 'Enthusiastic'-type intensity words ('loves', 'lifesaver', 'amazing', 'awesome') carry 5-star rates of 75-90% versus base rates of 41-67%. Implication: a keyword monitor on the disappointed-type list (dangerous, refund, waste, defective, broke, repair, stopped, useless) plus the p1 share gives Sunshine an early-warning text channel that is statistically independent of, and additive to, the star-level signal. Limitation: word counts in the microwave category are small (276 qualified words), so individual-word odds ratios there are noisy; the category-level pattern (repair/service vocabulary marking failure) is robust across the 191 'warranty' and 167 'repair' occurrences.

## Subtask 7: Subproblem 7: write a one- to two-page letter to the Marketing Director of Sunshine Company summarizing the team's analy

### Problem

Subproblem 7: write a one- to two-page letter to the Marketing Director of Sunshine Company summarizing the team's analysis and results, including specific justification for the result the team most confidently recommends.

### Analysis

The letter distills the six analysis subtasks into the decisions the director actually faces: what to monitor, what the three categories' reputations look like, and which single finding to act on with highest confidence. The most confident recommendation is the monitoring rule built from the 1-star share plus the sustained-decline criterion, because it is the only result that (i) uses a measure robust to the selection bias that contaminates mean stars, (ii) has a domain-validated warning standard, and (iii) is testable in the data itself.

### Modeling Process

No new model; composition of results. Key numbers carried into the letter: category means 4.12 / 3.45 / 4.30 (hair dryer / microwave / pacifier) among reviewers; 1-star shares 9.0% / 24.9% / 6.3%; 5-star Wilson lower bounds 0.575 / 0.389 / 0.662; per-product reputation shifts (1/3 of products falling in each category); the conjunction rule for failure (p1 above own baseline by >30-50% + 3-month mean decline >0.2 stars on n>=30, confirmed by rising negative-sentiment share); the descriptor watchlist; the finding that low star histories do not incite extra reviews while 1-star reviews are 1.4-1.7x longer than 5-star reviews.

### Outcome Analysis

LETTER (in this field):

Dear Marketing Director,

You asked what our customers' past ratings and reviews on competing products can tell us before you launch the microwave, pacifier and hair dryer. We analyzed 32,000 Amazon reviews across the three categories, from 2002 to 2015. Four findings matter most for launch.

First, what to track. Do not track the average star rating alone. The people who review are a small, self-selected minority - roughly 1 to 5 out of every 100 buyers - and the delighted are over-represented among them, so the displayed average flatters every product. The number that tells the truth is the share of 1-star reviews, checked alongside the share of 5-star reviews, the share of reviews with negative language, and the volume of reviews, with the rule that anything is read only after at least 30 reviews in a month. These four form a monthly dashboard per product.

Second, where your three categories stand. The pacifier market is healthy: 67% of reviews are 5-star, only 6% are 1-star, and review language in that category separates sharply - the word 'waste' appears in reviews that are 15 times as likely to be 1- or 2-star as average. The hair dryer market is solid (58% five-star, 9% one-star), with failure language concentrated in safety words ('dangerous', 'sparks', 'defective'). The microwave market is the problem category: 25% of all reviews are 1-star and the typical complaint is not about cooking but about breakdown and service - 'warranty', 'repair', 'stopped working', 'called the company'. A customer buying your microwave will judge you on after-sale experience as much as on the appliance, and your warranty and repair process should be ready before launch, not after.

Third, how to know a product is failing. A one-month dip in average stars is noise. The trustworthy warning is a sustained drop: the average falling for three or more consecutive months, on at least 30 reviews a month, while the 1-star share climbs above the product's own historical level by 30-50%. In the data we studied, no whole category showed such a sustained decline, but about one product in three in each category was individually losing reputation over its life - which means you should expect to see this on individual SKUs and have the response (fix, reposition, or delist) decided in advance.

Fourth, what the text is worth. Negative keywords ('dangerous', 'refund', 'waste', 'defective', 'broke', 'repair', 'useless') carry 5 to 17 times the odds of a bottom-tier rating, and 1-star reviews are 40-70% longer than 5-star reviews - complaints carry the detail that matters for product design. Monitor these words weekly; they lead the star numbers slightly. One caution: a bad run of visible stars does not make more people review - we found no evidence that low ratings incite extra review volume, so a spike in complaint volume means a real increase in unhappy buyers, not an echo effect.

The recommendation we stand behind most: build the monthly four-measure dashboard (1-star share, 5-star share with its confidence interval, negative-language share, volume) and trigger a review of any product the moment the 1-star share crosses its own historical baseline by a third while the three-month average is falling. We are confident in this rule because the 1-star share is the one measure the review-bias problem does not flatter, the sustained-decline standard is the one a working manager says they actually trust, and the rule fires rarely enough in the historical data that a live trigger means something real. We would act on the microwave warranty and repair findings on the same confidence level.

Respectfully,
Your modeling team

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
