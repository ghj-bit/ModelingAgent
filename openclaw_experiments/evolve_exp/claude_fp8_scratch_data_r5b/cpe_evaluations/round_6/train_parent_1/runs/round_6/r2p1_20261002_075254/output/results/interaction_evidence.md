# Expert Interaction Evidence

## Exchange 1 — Data Provenance (helpfulness votes)

**Question (expert_question_1.md):**
> In Amazon's review data, most star ratings have zero helpful votes. Do you
> think that means the reviews are unhelpful, or that Amazon just doesn't show or
> collect votes for many reviews?

**Expert reply (expert_reply_1.json):**
{"ok": true, "exchange": 1, "question": "Exchange 1 \u2014 Data provenance and representativeness\n\nQuestion: In Amazon's review data, most star ratings have zero helpful votes. Do you\nthink that means the reviews are unhelpful, or that Amazon just doesn't show or\ncollect votes for many reviews?", "answer": "Mostly the latter: zero helpful votes is a display/exposure artifact, not evidence of unhelpfulness.\n\nKey facts:\n\n- Helpfulness voting is optional and passive. A review only accumulates votes if other shoppers happen to see it and bother to click. Most reviews are never surfaced prominently, so they get no votes regardless of quality.\n- Vote counts are heavily right-skewed: a small minority of reviews (often the earliest, longest, or most visible ones) collect most votes; the median review sits at zero.\n- Amazon's \"helpful\" button appears on the review page, but visibility depends on ranking, recency, and how long the review has been posted. Newer reviews have had little time to accrue votes.\n- Zero votes therefore conflates \"no one saw it,\" \"no one voted,\" and \"genuinely unhelpful.\" It cannot distinguish among these.\n\nPractical implication: treat helpful_votes as a sparse, exposure-driven signal. Use total_votes and the helpful/total ratio only on the subset with votes, and do not interpret zero as a quality judgment.", "rubric_id": "interaction_initial_substantive_v1"}

**How the reply affected the work:**
- The helpfulness ratio (helpful_votes / total_votes) is computed **only** on
  reviews with total_votes > 0. Reviews with total_votes = 0 (62-72% of all
  reviews) are excluded from the helpfulness analysis and are not treated as
  "unhelpful."
- In Task 1 (informative measures), the helpfulness ratio is reported with an
  explicit n_voted count and a caveat that it is an exposure-driven signal.
- In Task 6 (letter), the recommendation to track helpfulness is restricted to
  "voted reviews only," with the zero-vote share (62-72%) explicitly identified
  as a display artifact.
- Parameter used: zero-vote reviews are NOT evidence of unhelpfulness; they are
  excluded from ratio calculations. Interval: total_votes > 0.
  Source: expert_reply_1 (Exchange 1).

---

## Exchange 2 — Structural Assumption (negative reviews and volume)

**Question (expert_question_2.md):**
> In practice, does a product with many recent 1-star reviews tend to get
> fewer new reviews overall, or do more shoppers rush to leave reviews?

**Expert reply (expert_reply_2.json):**
{"ok": true, "exchange": 2, "question": "Exchange 2 \u2014 Structural assumption\n\nQuestion: In practice, does a product with many recent 1-star reviews tend to get\nfewer new reviews overall, or do more shoppers rush to leave reviews?", "answer": "More shoppers rush to leave reviews \u2014 a burst of recent 1-star reviews tends to *increase* new review volume, not suppress it.\n\nKey facts:\n\n- Negative experiences are the strongest motivator for writing a review. Dissatisfied customers are more likely to post than satisfied ones, so a wave of 1-star reviews is usually itself a symptom of a surge in posting activity, not a deterrent.\n- Review volume is driven by sales volume and by how many buyers feel strongly enough to write. A product generating many 1-star reviews is typically still selling, and each unhappy buyer adds to the pile.\n- The pattern is self-reinforcing over the short run: visible negative reviews attract attention (and sometimes pile-on), and the product's page stays active.\n- What actually suppresses new reviews is declining sales or the product being delisted/out of stock \u2014 not the negativity of existing reviews.\n\nSo the direction is: more recent 1-star reviews \u2192 more new reviews, at least until sales themselves fall off.", "rubric_id": "interaction_initial_substantive_v1"}

**How the reply affected the work:**
- In Task 4 (lagged autoregression), the null hypothesis tested is b2 = 0
  (no effect of prior-month neg_share on current review count), with the
  directional prior from the expert that b2 > 0. The result (b2 not
  significant, p > 0.3 in all three datasets) is reported as "directionally
  consistent with the expert's prediction but not statistically confirmed."
- In Task 3 (success/failure classification), the assumption that rising
  neg_share accompanied by rising review volume is a genuine quality signal
  (not a volume artifact) is explicitly stated and justified by this exchange.
- The interpretation in Task 4's outcome analysis frames the modest,
  non-significant b2 as consistent with the expert's observation that
  negative waves attract attention at the category level.
- Constraint used: negative review waves do NOT suppress subsequent review
  volume; they increase it, at least until sales decline. This rules out
  a model in which low neg_share is interpreted as "market has moved on."
  Source: expert_reply_2 (Exchange 2).

---

## Exchange 3 — Decision Threshold (actionable neg_share)

**Question (expert_question_3.md):**
> When a product on Amazon has roughly one in three reviews being 1 or 2
> stars, would you treat it as a problem worth acting on, or as normal noise?

**Expert reply (expert_reply_3.json):**
{"ok": true, "exchange": 3, "question": "Exchange 3 \u2014 Decision threshold\n\nQuestion: When a product on Amazon has roughly one in three reviews being 1 or 2\nstars, would you treat it as a problem worth acting on, or as normal noise?", "answer": "Treat it as a problem worth acting on \u2014 a 1\u20132 star share around one-third is well above normal.\n\nKey facts:\n\n- For mainstream consumer products on Amazon, the typical 1\u20132 star share is roughly 10\u201320%; the average star rating usually sits near 4.0\u20134.5. A one-third low-star share implies an average rating around 3.0\u20133.3, which is a clear outlier on the low side.\n- That level of dissatisfaction is not random noise; it signals a systematic product or expectation problem (defects, misleading listing, fit/quality issues) rather than scattered individual complaints.\n- The threshold matters by category: for low-cost, low-expectation items (e.g., a pacifier) some low-star share is more tolerable, but one-third is still high; for a durable appliance (microwave, hair dryer) it is a strong warning.\n- Caveat: judge against the product's own category baseline and review volume \u2014 a one-third share on a handful of reviews is weak evidence; on hundreds it is actionable.\n\nSo: act on it, but confirm it is sustained and category-relative rather than a small-sample artifact.", "rubric_id": "interaction_initial_substantive_v1"}

**How the reply affected the work:**
- The neg_share threshold of 0.38 found by the F1 threshold search in Task 3
  is confirmed as actionable by the expert: one-third low-star share is "well
  above the 10-20% typical for mainstream Amazon products" and signals a
  systematic problem, not noise.
- In Task 1, the typical_neg_share range of [0.10, 0.20] is recorded as an
  empirical parameter sourced from Exchange 3.
- In Task 6 (letter), the microwave alert threshold is set at 30% (lower than
  the 38% for hair dryer and pacifier) because the microwave category has a
  lower baseline mean star (3.45) and the expert noted that for durable
  appliances a one-third share is "a strong warning."
- The expert's caveat — "judge against the product's own category baseline and
  review volume; a one-third share on a handful of reviews is weak evidence" —
  is implemented as the >= 50 reviews minimum before acting on the threshold,
  stated in Task 1 and Task 6.
- Parameter used: typical_neg_share = [0.10, 0.20], actionable threshold
  confirmed at ~0.33, minimum review count for action = 50.
  Source: expert_reply_3 (Exchange 3).

---

## Summary of parameters sourced from expert exchanges

| Parameter | Value | Interval | Source |
|-----------|-------|----------|--------|
| Zero-vote reviews are exposure artifact, not quality signal | constraint | total_votes > 0 for ratio calc | Exchange 1 |
| Negative waves increase subsequent review volume | directional prior | b2 > 0 in lag model | Exchange 2 |
| typical_neg_share for mainstream products | 0.10-0.20 | [0.10, 0.20] | Exchange 3 |
| neg_share threshold is actionable at ~0.33 | confirmed | >= 0.30 for appliance, 0.38 for small goods | Exchange 3 |
| Minimum reviews before acting on threshold | 50 | >= 50 reviews | Exchange 3 (caveat) |
