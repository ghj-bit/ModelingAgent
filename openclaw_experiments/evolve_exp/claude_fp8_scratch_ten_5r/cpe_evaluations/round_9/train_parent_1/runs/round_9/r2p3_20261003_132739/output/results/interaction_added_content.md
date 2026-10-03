# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — MM-Bench 2020_C (Amazon review data)

Ten expert exchanges. The policy sequence followed: mechanism (E1) → constraint
(E2) → parameters (E3, E4) → edge cases (E5–E9) → operating norm (E10).

## Exchange 1 — dominant mechanism (structural)

- **Q:** When shoppers decide between competing products, what do they rely on
  most: average star rating, written reviews, or recency of reviews?
- **A (summary):** Rating = screening filter; review text = the deciding
  signal inside the consideration set; recency = the trust factor that
  discounts the other two. Below ~4 stars a product is filtered before
  reviews are read; among 4.0–4.5 products the rating is nearly uninformative,
  so the marginal decision comes from recent + most-helpful text. A recent
  cluster of negative reviews outweighs the long historical average.
- **Used in work (value/constraint, not prose):** defines the measurement
  hierarchy the analysis is built on: (i) star rating is the primary
  screening variable → tracked at product level via Bayesian-smoothed mean;
  (ii) review text is the decision variable → lexicon sentiment and length
  are computed per review; (iii) recency is the trust gate → all "reputation"
  measures are rolling-window (30/90-day, 6-month) rather than lifetime, and
  per-product trend = late-window mean minus early-window mean.
  Parameter adopted: screening threshold ≈ 4.0 stars (source: exchange 1).

## Exchange 2 — constraint on the text signal

- **Q:** What limits how much weight shoppers put on written reviews?
- **A (summary):** (1) volume/representativeness — only the top few
  most-helpful + most recent are read, a biased slice; (2) interpretation
  cost — text only comparable inside a small consideration set, discounted
  when vague or incentivized; (3) credibility — unverified/Vine/variant
  reviews are discounted.
- **Used in work:** constraint → the "effective review window" is the
  most-voted subset. Operationalized as: helpfulness (total_votes,
  helpful_votes) is treated as the visibility/weight variable, and
  verified_purchase as the credibility filter; analyses separate voted vs
  unvoted reviews. This is why helpfulness-vote statistics are a first-class
  output (share of helpful votes landing on 1–2-star reviews, vote rate by
  star, votes-vs-length gradient) rather than a side product.

## Exchange 3 — parameter: size of the decision window

- **Q:** How many reviews does a typical shopper actually read?
- **A:** a handful — about 5–10, often fewer; low-risk items 1–3; even
  careful shoppers rarely beyond ~20–30.
- **Used in work:** parameter N_read ≈ 5–10 (range 1–30; source: exchange 3).
  Consequence: the top ~10 most-voted reviews dominate perceived reputation,
  so vote-weighted sentiment (sentiment of voted reviews, especially voted
  negatives) is the reputation measure that matters, and a single viral
  negative review can shift perception far more than the average. This sets
  the interpretation threshold for helpfulness statistics: changes in the
  top-voted set, not the full review pool, drive the perceived trajectory.

## Exchange 4 — parameter: staleness window

- **Q:** How long without new reviews before trust in the rating fades?
- **A:** ~6–12 months of silence starts fading trust; beyond ~1 year a stale
  high rating is discounted. Durable, low-churn products (hair dryer,
  microwave) tolerate up to ~1 year+; what matters is the gap relative to the
  product's own prior cadence.
- **Used in work:** parameter T_stale = 6–12 months (durable goods up to
  12+; source: exchange 4). Operationalized: the "reputation freshness"
  indicator is months since last review compared to the product's median
  inter-arrival gap; a product is flagged stale if silent for >12 months or
  for >3× its own median gap. The tracking section reports per-category
  weekly velocity so a drop below the product's own baseline cadence is
  detectable.

## Exchange 5 — edge case: cold start

- **Q:** Do shoppers skip a zero-review product, or will they be early
  reviewers? What drives that?
- **A:** mostly skip; willingness to be early is driven by price/risk (low
  cost tolerated), brand/seller trust, verified-purchase/return protection,
  category novelty, and incentives (Vine/discount). Early organic reviewers
  are a small minority and shape the first rating disproportionately.
- **Used in work:** edge case → cold-start regime. Consequence for the model:
  lifetime averages of few-review products are not comparable to mature
  products; the success model therefore uses (a) a Bayesian prior
  (pseudo-count m = 5–20, category-median prior) for products below ~30
  reviews, and (b) flags vine/verified composition of early reviews as an
  incentive bias. Verified-purchase share enters the tracking metric set.

## Exchange 6 — edge case: early-wave bias

- **Q:** Does the first wave of reviews skew more positive or more negative
  than the long-run average?
- **A:** more positive (enthusiast self-selection, incentivized/Vine
  reviews, novelty halo, returned-but-never-reviewed unhappy buyers). A
  genuinely defective launch is the exception that skews early negative.
  Early ratings regress to, and usually land below, the long-run mean.
- **Used in work:** constraint on interpretation: a new product's early high
  rating is an upper bound, not the steady state. Operationalized: the
  success model compares first-half vs second-half per-product means
  (regression-to-mean check), and the recommendation to Sunshine uses
  smoothed/recent-window ratings, never the raw early rating, for launch
  success prediction. Data check: category-level yearly means are flat to
  rising while review volumes grow 10–100×, consistent with an early
  positive wave being diluted as volume scales.

## Exchange 7 — parameter: time to steady state

- **Q:** Roughly how long until a rating settles to steady state?
- **A:** ~6–12 months after launch, longer end for durable low-churn
  categories (hair dryer, microwave); marker = when the marginal new review
  stops moving the average; needs a few hundred reviews or a full seasonal
  cycle.
- **Used in work:** parameter T_settle = 6–12 months (durable goods
  toward 12; source: exchange 7). Operationalized: the "stable reputation"
  window is the trailing 12 months; products younger than T_settle are
  reported with wider uncertainty (the Wilson/Bayesian intervals widen with
  1/n, which is exactly the marginal-review-still-moving condition).
  Half/half per-product trend test uses this as the minimum lifetime.

## Exchange 8 — edge case: failure mode

- **Q:** What is the biggest threat to a product's online reputation over
  time?
- **A:** a product defect/safety issue producing a sustained,
  self-reinforcing stream of negative reviews: it hits rating and text at
  once, compounds (negatives rise to the top of the read window), is durable
  (fresh negatives keep coming, so recency works against the product), and
  is hard to reverse (fixes reset review history).
- **Used in work:** defines the failure signature the model must detect:
  (i) rising recent 1–2-star share; (ii) sustained (not one-off) negative
  flow; (iii) rising helpfulness on the negatives; (iv) declining
  rolling-90-day mean star. The tracking section implements exactly this
  compound detector (rolling 3-month star peak-to-last drop > 0.35 with
  last < 4.0) and reports, for flagged products, the helpful-vote volume on
  their recent negatives — the compounding mechanism.

## Exchange 9 — edge case: early discrimination

- **Q:** How to tell early that a product is heading toward a compounding
  negative wave rather than a rough launch?
- **A:** concentration + persistence: negatives naming the same recurring,
  product-intrinsic cause; new negatives still arriving months in; rising
  helpfulness on negatives; sliding (not dip-and-recover) rating trajectory;
  verified-purchase negatives; corroboration in returns/Q&A. A rough launch
  fades and the rating recovers.
- **Used in work:** sharpens the detector into a rule distinguishing
  "rough launch" (transient dip) from "compounding defect wave"
  (sustained decline). Implemented as: decline persists across ≥3 consecutive
  3-month windows AND recent (last 3 months) 1–2-star share exceeds the
  product's early 3-month share by >10 points AND helpful votes on recent
  negatives are above the product's median negative-review vote count.
  Dip-and-recover products (negative dip followed by ≥0.3 star recovery)
  are classified rough-launch; products without recovery are flagged
  compounding. Result: see analysis.json tracking block.

## Exchange 10 — operating norm: what to track

- **Q:** If you could track just a handful of numbers per product, which?
- **A:** per product, per week: (1) average star rating; (2) rating
  trajectory (rolling 30/90-day mean or slope); (3) new reviews per week;
  (4) share of 1–2-star among recent reviews; (5) helpfulness votes on
  negative reviews; (6) verified-purchase share of recent reviews. If
  forced to three: average rating, its recent trajectory, new-review
  velocity.
- **Used in work:** the final tracking-dashboard specification. All six
  metrics are computed per product per week (analysis.json "tracking" block
  and the per-product trend CSVs), and the recommendation letter (subtask
  outcome) is organized around the top-three: level, trajectory, velocity —
  plus the two defect-wave indicators (recent 1–2-star share; helpfulness
  on negatives) because exchange 8/9 made them the failure early-warning.
