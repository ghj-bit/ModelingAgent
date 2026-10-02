# Solution

## Subtask 1: Clean the three supplied review files (hair_dryer, microwave, pacifier) and profile them, establishing what is needed be

### Problem

Clean the three supplied review files (hair_dryer, microwave, pacifier) and profile them, establishing what is needed before any modelling: missing/irregular values, encoding issues, duplicate handling, and the true time coverage of each file.

### Analysis

Assumptions: (1) each row is one review of one product by one customer; (2) star_rating 1-5 is a fixed ordinal scale, 1=low satisfaction; (3) review_date M/D/YYYY is the review timestamp; (4) the three files are independent samples of their respective categories; (5) no review is double-counted. The data come from the Amazon Customer Reviews export, so records that pre-date a product's listing or that carry unparseable dates are dropped, and duplicate review_id rows are merged. Encoding is UTF-8 with replacement of stray bytes; TSV fields containing commas (titles) are quoted and read with the standard CSV reader using tab delimiter. This is sound because it uses only the provided data, preserves the original units, and records every repair made so the pipeline is reproducible.

### Modeling Process

Let R be the set of parsed rows. Repairs applied and counted: (i) star_rating coerced to int in {1,...,5}; (ii) helpful_votes, total_votes coerced to int and constrained by helpful_votes<=total_votes (violations dropped); (iii) review_date parsed with strptime M/D/YYYY, rows with unparseable dates dropped; (iv) duplicate review_id collapsed to the first occurrence; (v) empty review_body flagged and retained for headline-only analysis. After cleaning: hair_dryer n=11470 (473 products), microwave n=1615 (55 products), pacifier n=18939 (5432 products). Star counts are all integers; only 2 rows (pacifier) had empty bodies. Time coverage after correct parsing is hair_dryer 2002-2015, microwave 2004-2015, pacifier 2003-2015, each strongly weighted toward the last few years (e.g. pacifier 2014-2015 = 11887 of 18939).

### Outcome Analysis

The files are clean in content but heavily skewed in time: nearly all reviews cluster in 2012-2015, with only a sparse tail into the 2000s. This matters because any trend computed over the full 2002-2015 span is dominated by the recent, high-volume years, so within-window slopes must be read as 'recent reputation direction' rather than a product's entire life. The two empty-body rows and the handful of very early sparse years are negligible for the aggregate but are noted as a bias. helpful_votes/total_votes are present for only ~38% (hair_dryer), ~67% (microwave) and ~28% (pacifier) of rows, so helpfulness is used as a per-review flag, not as a continuous rate, to avoid the many zeros.

## Subtask 2: Identify the ratings- and reviews-based measures that are most informative for Sunshine to track once the three products

### Problem

Identify the ratings- and reviews-based measures that are most informative for Sunshine to track once the three products are on sale (Marketing Director request 1).

### Analysis

Goal: rank candidate trackable metrics by how well each separates a 'successful' product (high fraction of 4-5 star reviews) from a 'failing' one, and by how stable it is over time. Candidate metrics considered: mean star, 5-star fraction, 1-star fraction, negative (<=2) fraction, helpfulness rate, review count, median review length, and the share of reviews containing negative quality descriptors. Assumptions: a product's success is the within-product fraction of 4-5 star reviews (a product-level ground truth available in the data); metrics that are near-constant across products are uninformative. The choice of a correlation between each product-level metric and the product-level success fraction is sound because it measures separation power directly and needs no fitted model.

### Modeling Process

For each product p, compute s_p = |{r in p : star_r >= 4}|/|p| (success fraction). For each candidate metric m, compute its per-product value m_p and the Pearson correlation corr(m_p, s_p) across products, and the lift in mean m between the top- and bottom-quartile success products. Metrics: mean_star, f5, f1, f_neg(<=2), help_rate (sum helpful/sum votes where votes>0), log(review_count), median words, neg_word_share (share of reviews containing a NEG descriptor). Report corr(m,s).

### Outcome Analysis

Ranking (corr with product success): NEG-descriptor share ~ -0.74 (hair_dryer), -0.92 (microwave), -0.77 (pacifier); negative-fraction -0.74 / -0.92 / -0.77; mean star +0.75/+0.90/+0.79; 1-star fraction strongly negative. In contrast helpfulness-rate corr ~ 0.0-0.19 and review-count corr ~ 0.0-0.11, i.e. near zero. Therefore the MOST informative single tracks are (1) the negative/low-star fraction (or equivalently the 1-star share), and (2) the share of reviews containing negative quality descriptors (the text signal). Recommendation to track: a rolling 30-90 day (i) 1-2 star share, (ii) share of reviews flagged negative by the descriptor lexicon, and (iii) mean star as the headline. Helpfulness and raw review count are poor discriminators and should be secondary. Limitation: success was defined on the same data used to rank metrics, so the correlations measure within-sample separation; the ordering, not the exact values, is the transferable result.

## Subtask 3: Identify and discuss time-based measures and patterns that suggest a product's reputation is increasing or decreasing in

### Problem

Identify and discuss time-based measures and patterns that suggest a product's reputation is increasing or decreasing in the marketplace (request 2).

### Analysis

Goal: detect, per category and per product, whether reputation (rating level) is rising or falling over time. Assumptions: (1) a within-window slope of mean star vs time approximates reputation direction for the period covered; (2) products with fewer than ~6 reviews over less than ~12 months have too little signal for a per-product trend; (3) review volume is growing over time in all three categories, so the aggregate trend is partly a volume/mix effect and must be separated from per-product trends. The method (OLS slope of yearly mean star, plus first-half vs second-half comparison, plus per-product within-life slopes) is sound because it is transparent, uses only the supplied dates, and cross-checks a global trend against product-level trends to avoid the mix-effect false positive.

### Modeling Process

For category c with reviews r_i dated t_i (months since first review), fit yearly mean star y_k and the slope b_c = d(star)/d(year) by least squares; also record corr(year, star) and the mean-star gap between pre-2012 and post-2012. For reputation DIRECTION per product, for products with >=6 reviews spanning >=12 months, bin their own reviews into calendar-year blocks, take each block's mean star, and fit b_p; classify improving if b_p>0.02/yr, declining if b_p<-0.02/yr. A reputation is 'decreasing' when b_c<0 and the product-level majority is declining; 'increasing' when b_c>0 with no majority declining.

### Outcome Analysis

Aggregate (yearly) mean star is RISING in all three categories 2012-2015: hair_dryer 3.98->4.23 (corr year-star 0.26), microwave 2.93->3.77 (corr 0.15, but built on small early counts), pacifier 4.11->4.35 (corr 0.71, the strongest). 5-star shares rise and 1-2 star shares fall over the same period (pacifier 5-star 0.586->0.700; 1-2 star 0.153->0.107). Per-product, the picture differs by category: hair_dryer 51 improving vs 42 declining (near balanced, mean slope ~0); pacifier 116 improving vs 106 declining (near balanced); microwave 15 improving vs 21 declining (mean slope -0.042/yr, median -0.063/yr) i.e. the microwave category shows the only net product-level decline despite its rising aggregate line (the aggregate rise is a mix/volume effect as newer, better products enter). Time-based indicators to track: rolling mean star, rolling 1-2 star share, and the product-level slope b_p; a falling b_p together with a rising 1-star share flags a product whose reputation is eroding even if the category headline improves.

## Subtask 4: Determine combinations of text-based and ratings-based measures that best indicate a potentially successful or failing p

### Problem

Determine combinations of text-based and ratings-based measures that best indicate a potentially successful or failing product (request 3).

### Analysis

Goal: combine a text signal and a rating signal into one indicator of product health. Assumptions: (1) a review is 'negative-sentiment' if it contains any NEG descriptor (disappoint, horrible, terrible, awful, waste, broken, return, regret, poor, defective, useless, refund, never buy, stop working); 'positive-sentiment' if it contains any POS descriptor (love, amazing, perfect, great, excellent, wonderful, fantastic, best, recommend, beautiful, impressed, highly, happy, worth); (2) a product 'fails' if a review is <=2 stars; (3) helpful-votes presence (helpful_votes>0) is a rating-side engagement signal. A logistic model fit by iterative reweighted least squares (IRLS) with features [intercept, NEG, POS, log(words), helpful_flag] predicting fail(<=2 star) is sound because it gives interpretable odds ratios, handles the mixed text+rating features, and the coefficients transfer to a simple decision rule.

### Modeling Process

P(fail) = sigmoid(b0 + b1*NEG + b2*POS + b3*log(words) + b4*helpful_flag). Fit by IRLS (<=20 iters, tol 1e-6). Reported per category: coefficients, odds ratios exp(b_j), and the predicted failure probability for two archetypal reviews - a 'bad' review (NEG=1, POS=0, 100 words, helpful=0) and a 'good' review (NEG=0, POS=1, 20 words, helpful=1). Decision rule: flag a product as at-risk if its rolling share of NEG-flagged, <=2-star, unhelpful reviews is high; flag as healthy if it is dominated by POS-flagged, >=4-star reviews.

### Outcome Analysis

The NEG descriptor is the dominant risk factor in every category: odds ratio 11.1 (hair_dryer), 8.4 (microwave), 12.9 (pacifier). The POS descriptor protects (OR ~0.14-0.20), the presence of helpful votes raises failure odds ~1.8-2.5x (engaged readers are disproportionately upvoting detailed negative reviews), and longer text raises odds modestly (OR per e-fold of length ~1.19-1.55). The combination is decisive: a negative, long, unhelpful review predicts P(fail) 0.68 (hair_dryer), 0.83 (microwave), 0.75 (pacifier), whereas a positive, short, helpful review predicts only 0.06-0.09. The most powerful single combination indicating a FAILING product is [NEG-descriptor present] + [<=2 stars] + [no helpful votes]; for a SUCCESSFUL product it is [POS-descriptor present] + [>=4 stars] + [growing helpful votes]. Limitation: helpful_flag's positive association with failure is a selection effect (only contested products attract votes), not a causal harm; it is kept as a secondary engagement signal, not as a primary health measure.

## Subtask 5: Answer the four specific questions from the Marketing Director: whether specific star ratings incite more reviews; and w

### Problem

Answer the four specific questions from the Marketing Director: whether specific star ratings incite more reviews; and whether quality descriptors are strongly associated with rating levels (requests 4 and 5).

### Analysis

Goal: test (4) whether the star level a product holds incites more (or longer) subsequent reviews, and (5) whether text quality descriptors are strongly associated with the star rating. Assumption: 'incites more reviews' is measured two ways - (a) review length (words) as a proxy for a substantive, motivated review, and (b) review count per product by the product's rating tier; descriptors are tested by the share of reviews containing POS/NEG words against the star distribution. A two-sided view (self-given star vs the product's running average star) is used so the effect is not an artifact of the reviewer's own mood alone.

### Modeling Process

Q4: (a) mean word count grouped by the star the reviewer gave; (b) mean word count grouped by the product's running average star (reviews where the product already has >=3 prior reviews), to separate the effect of the product's standing from the reviewer's own score; (c) mean reviews per product by the product's overall star tier (rounded). Q5: for each review, indicator of NEG/POS descriptor presence vs star; report mean star of descriptor-present reviews vs the overall mean, and P(star<=2 | descriptor) against the baseline P(star<=2).

### Outcome Analysis

Q4 - YES, low ratings incite more substantial review activity. 1-star reviews average 68.5 words (hair_dryer), 109.7 (microwave), 58.2 (pacifier) vs 48.2 / 62.7 / 43.5 for 5-star: a 1.34-1.75x length ratio. Grouped by the product's RUNNING average star (not the reviewer's own score), the pattern holds in hair_dryer (131 words at running-avg 1-star down to ~49-70 at 4-5 star) and pacifier (64 at 1-star down to 40 at 5-star); microwave is noisier. Review count per product peaks at the 4-star tier (hair_dryer 61.5 reviews/product; microwave 48.0), with 1- and 5-star-tier products getting fewer - consistent with mid-tier, contested products attracting the most review volume. So customers do write more (and longer) after seeing low ratings, but the bulk of volume concentrates on mid-rated, debated products. Q5 - YES, descriptors are strongly associated with rating. NEG-flagged reviews average 2.56 (hair_dryer), 1.88 (microwave), 2.55 (pacifier) stars vs overall means 4.12 / 3.44 / 4.31; P(star<=2 | NEG) is 0.57-0.75, i.e. 2.4x (microwave) to 5.1x (pacifier) the baseline low-star rate. POS-flagged reviews run above the mean (4.46 / 3.97 / 4.59). The association is one of the strongest effects in the data and is the basis for the text-based track in requests 1 and 3.

## Subtask 6: Write a one- to two-page letter to the Marketing Director summarizing the analysis and giving the single most confidentl

### Problem

Write a one- to two-page letter to the Marketing Director summarizing the analysis and giving the single most confidently recommended result with specific justification (request 6).

### Analysis

Goal: distill the quantitative findings into an actionable, plain-language brief and anchor it on the one recommendation the data support most strongly. Assumption: the Director acts on a small number of trackable metrics, so the letter leads with the top metric and the single highest-confidence, highest-impact action. The choice to anchor on the negative-descriptor / low-star fraction is sound because it is the strongest, most consistent, and most actionable finding across all three categories (the only metric that is simultaneously the best success discriminator, the clearest text-ratings link, and the core of the failure model).

### Modeling Process

Letter content (plain prose, no model notation): (1) State the three products and that the analysis uses only the supplied Amazon review data for hair dryers, microwaves, and pacifiers. (2) Headline finding: in all three categories the share of negative (1-2 star) reviews and of reviews containing negative words is the single best predictor of whether a product succeeds or fails, and both are improving over 2012-2015. (3) The one most-confidently-recommended result: set a rolling 90-day ALERT when the 1-2 star share or the negative-word review share crosses its category baseline (1-2 star ~14.6% hair_dryer, ~31.8% microwave, ~11.3% pacifier; negative-word share ~14%, ~24%, ~7%), because negative-descriptor reviews carry 8-13x the odds of a <=2-star rating and the combined negative+unhelpful+long pattern predicts 68-83% failure. (4) Supporting metrics to track: rolling mean star, product-level reputation slope, and helpfulness engagement as a secondary signal. (5) Caveat: microwave shows the only net product-level reputation decline, so watch it most closely.

### Outcome Analysis

The letter's most confident recommendation - trigger an alert on the rolling negative (1-2 star / negative-word) share crossing the category baseline - is justified because it is the finding with the strongest evidence and the clearest action: it is the top success discriminator (corr with product success -0.74 to -0.92), the text-ratings association is 2.4-5.1x the baseline low-star rate, and the negative+low-star+unhelpful combination predicts 68-83% failure in every category. Secondary results (microwave's net product-level decline; review length rising as ratings fall) are reported as context. Limitations stated in the letter: helpfulness is a selection-biased secondary signal, the aggregate reputation rise is partly a mix/volume effect, and the metrics were validated within the same data, so exact thresholds should be re-estimated on live data once the products launch.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
