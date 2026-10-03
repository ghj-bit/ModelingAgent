# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — Problem 2020_C (Amazon reviews)

Ten expert exchanges, one per round. For each: the question, the expert's reply
(paraphrased), and the concrete change the reply made to the model (parameter,
constraint, equation, or decision rule) with the interval over which it holds.
No reply text was copied into solution.json; only values, constraints and
decision rules below are used there.

## Exchange 1 — review volume vs. satisfaction
- **Q:** A drop in review volume on a popular product — falling out of favor, or
  just fewer buyers?
- **Reply (gist):** Volume = purchases × a low, roughly stable review-propensity
  rate (a few percent of buyers). A volume drop is a demand signal, not a
  satisfaction signal; it only indicates falling favor if the rating average
  declines or negative sentiment rises alongside.
- **Model change:** The reputation-trend rule (Subtask B) is a *conjunction*,
  not a single indicator: a product is flagged "declining" only when the
  trailing-window rating (or 1-star share) worsens; volume alone is never used
  as a satisfaction indicator. Volume is used only as the marketplace-growth
  context that motivates the log-linear volume model
  log V(t) = a + b t (b = 0.042–0.057/month across the three categories).
  Holds for: durable/low-impulse consumer products, review volume in the
  hundreds-to-thousands per month.

## Exchange 2 — what helpful votes signal
- **Q:** What does a review's mostly-positive helpful votes tell a shopper?
- **Reply (gist):** Usefulness/popularity, a weak-to-moderate trust signal;
  early votes create a bandwagon; high helpfulness on a negative review can
  signal a shared complaint; cross-check with verified_purchase and the rating
  distribution.
- **Model change:** The helpfulness measure (helpful_votes / total_votes) was
  screened as a tracking candidate (Subtask A) but, with point-biserial
  correlations of −0.20 to +0.47 across products (no consistent positive sign),
  it was excluded from the recommended tracking set. The decision rule: a
  measure enters the recommendation only if it separates quality products
  consistently across all three categories.

## Exchange 3 — positive wording
- **Q:** Strongly positive words in reviews — genuine enthusiasm or polite habit?
- **Reply (gist):** Mostly genuine, concentrated in 4–5-star reviews; a
  formulaic/Vine minority; positive words inside a low-star review are often
  politeness framing before a complaint.
- **Model change:** The sentiment word counter was kept as a *presence* measure
  (any positive word) and a *net* measure (pos − neg hits). The predicted
  pattern — positive-word presence rising with star level — was confirmed by
  the data (0.50–0.56 of 1-star reviews contain a positive word vs. 0.86–0.92
  of 5-star). Because of the politeness caveat, the *net* sentiment score, not
  the positive count, was used in the classifier (Subtask C) and the letter.

## Exchange 4 — do low ratings trigger more reviews?
- **Q:** After a product gets several 1-star reviews, do shoppers rush to write?
- **Reply (gist):** No onlooker stampede; the people most likely to add a
  review are existing buyers with the same bad experience (shared-complaint
  effect); non-buyers are deterred from buying, which reduces future volume.
- **Model change:** Subtask D's testable hypothesis was written as: prior low
  ratings raise the *odds of a low rating* on the next review (shared complaint
  among buyers), not the review *count*. The design: regress each review's star
  on the mean of the preceding 5 stars on the same product. Result: the effect
  is real but small — pooled β = 0.315 stars (p ≈ 1e-201, R² = 0.065);
  within-category after controlling the product's running mean, β = 0.072–0.089
  (p < 0.002 for dryer/pacifier, n.s. for microwave). Interpretation: a weak
  self-reinforcing feedback loop, consistent with the shared-complaint
  mechanism, not a volume-trigger mechanism.

## Exchange 5 — success vs. failure indicator
- **Q:** For a new product, which matters more for judging success: average
  stars or the count of 1-star reviews?
- **Reply (gist):** The 1-star *share* and its trend is the sharper
  failure-warning; the average rating is the success indicator; for a new
  product, share and trend beat raw counts.
- **Model change:** The failure indicator in Subtasks B/C is the 1-star share
  (and 1–2-star share), not the 1-star count; the classifier's failure label
  is mean_star < 3.4, and the success label mean_star ≥ 4.2, with the
  1–2-star share reported alongside as the warning channel. The "danger
  pattern" rule from the reply (high average + rising 1-star share) is the
  explicit early-warning rule in the letter.

## Exchange 6 — seasonality
- **Q:** Do reviews of products like these spike around holidays?
- **Reply (gist):** Fairly steady, with a modest Nov–Dec lift of tens of
  percent (not multiples); microwaves flatter than hair dryers; reviews lag
  purchases by days-to-weeks.
- **Model change:** The seasonal threshold in the trend test was set to a
  Nov–Dec mean volume ≥15% above the non-Nov–Dec baseline (a "tens of percent"
  lift, per the reply). Measured lifts: dryer −7.6%, microwave −24.5%,
  pacifier +13.7% — none reach the threshold, so no seasonal component is
  included in the trend models; the log-linear volume model stands alone.

## Exchange 7 — failing vs. mediocre
- **Q:** What separates a genuinely failing product from a mediocre one?
- **Reply (gist):** Failing = structural, worsening pattern: growing 1-star
  share, declining ratings across cohorts, the *same specific defect* repeated
  by many reviewers, negative reviews voted highly helpful; mediocre = flat,
  mild, diffuse complaints.
- **Model change:** (a) Subtask B reports the 24-month slope of the 1-star
  share as the worsening test (dryer +0.0005/mo, pacifier −0.0002/mo ≈ flat;
  microwave −0.008/mo = improving). (b) Subtask F's defect-theme counts
  operationalize "same specific defect repeated": top themes in 1–2-star
  reviews are returned/return, safety, broke/broken across all three products —
  repeated across independent reviewers, matching the failure signature, not
  diffuse mediocrity. (c) The classifier's failing profile shows
  defect_rate 0.16–0.34 vs. 0.03–0.10 for success products.

## Exchange 8 — recency weighting
- **Q:** How much should recent reviews outweigh older ones?
- **Reply (gist):** Weight should decay with age; the most recent 6–12 months
  dominate "current reputation"; keep full history for trend; suggested
  exponential decay with half-life ≈ 6–12 months.
- **Model change:** Recency-weighted mean star:
  w_i = 0.5^((t_max − t_i)/180 days), R̄ = Σw_i s_i / Σw_i. Half-life 180 days
  (the lower end of the expert's 6–12 month range) chosen as a conservative
  "current health" estimate. Values: dryer 4.205, microwave 3.724, pacifier
  4.344. The 180-day choice is the interval where the reply's guidance holds;
  90-day and 365-day variants would bracket it.

## Exchange 9 — praise vs. defect complaints
- **Q:** Which carry more signal for a company: praise words or specific defect
  complaints?
- **Reply (gist):** Defect complaints — diagnostic, recurring, the leading
  indicator of failure; specific detailed praise reveals valued design
  features.
- **Model change:** The defect rate (fraction of reviews matching any
  defect pattern) is the primary text-based failure channel (correlation with
  mean star: dryer −0.77, microwave −0.73, pacifier −0.48; monotone gradient
  0.26–0.51 at 1 star → 0.03–0.06 at 5 stars). The feature-keyword rates in
  4–5-star reviews (ease of use, size/portability, value for money, heat/dry
  speed, durability) are the design-feature output for the letter's feature
  recommendations.

## Exchange 10 — new-product rating trajectory
- **Q:** In the first few months, does a new product's rating usually rise,
  fall, or stay flat?
- **Reply (gist):** Slight downward drift from an early-inflated average
  (early adopters + Vine reviews), with high variance; treat early averages as
  unstable.
- **Model change:** The letter's launch-window recommendation uses a
  recency-weighted (180-day) reputation rather than the first-month average,
  and the 30-review floor in the per-product screens (Subtasks A/C) is the
  minimum-evidence rule so that early, unstable averages are not acted on.
  The Vine bias was checked directly: Vine reviews average 4.39 vs. 4.19 for
  non-Vine (pooled), confirming the early-inflation channel.

## Data cleaning (step 2 of the required workflow)
No repair was needed: 0 duplicate review_ids, 0 missing/invalid star ratings,
0 unparseable dates, 0 helpful_votes > total_votes, 3 empty review bodies
retained (length 0). Two inconsistent case codings were normalized:
`vine` and `verified_purchase` contain lower-case 'y'/'n' rows (e.g. pacifier
7,680 lowercase 'n' vine rows); these were upper-cased before any aggregation
so that the Y/N coding is consistent.
