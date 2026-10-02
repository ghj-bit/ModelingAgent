# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — MM-Bench 2020_C (r2p2_20261002_051443)

Policy: 3 exchanges, one question each, each later question built on the previous reply.
All questions were written to `logs/operator_feedback/expert_question_N.md` and submitted
with `code/wait_for_expert_reply.py` (`--timeout 70 --exchanges 3`).

## Exchange 1 — data provenance and completeness

**Question** (see `expert_question_1.md`): "Is it fair to treat the reviews in these data as a
representative picture of how customers of these products actually rated and reviewed them over
the years, or would you expect the collection to be biased in a way that changes what conclusions
you would draw?"

**Reply**: NOT RECEIVED. The controller created `expert_request_1.json` at 05:16:16; the
bridge's expert API call failed at 05:19:22 (`expert_bridge.log`:
`RuntimeError('Direct human-expert API call failed')`) and `expert_reply_1.json` contains
`{"ok": false, ...}`. The bridge made no further attempt (no new log lines after 05:19:22;
`expert_request_2/3.json` were never created). This was an infrastructure failure of the
human-expert channel, not an answer. No parameter or rule may therefore be attributed to
Exchange 1.

**Effect on work**: none direct. Because no reply arrived, every representativeness
conclusion in the submission is grounded in the data itself rather than in an expert
assertion:
- zero missing values in the five numeric/flag columns of all three files;
- `review_date` present in 100% of rows, all in M/D/YYYY, range 2002-03-02 to 2015-08-31
  (a right-censored snapshot — a fact observable in the data, not an expert claim);
- the 7 case-variant rows (microwave: 7 of 1615; pacifier: 7741/7761 in two string columns)
  were normalized, not dropped;
- vote fields show a mechanical zeroing pattern (62–79% of reviews carry zero
  `total_votes`, concentrated in old records), treated as an absence of voting, not an
  absence of review, and all helpfulness statistics are computed on the voted subset;
- the 2 blank `review_body` cells (pacifier) are flagged and contribute 0 text metrics.

## Exchange 2 — structural assumption (category-level rating trends)

**Question** (see `expert_question_2.md`, builds on Exchange 1's data provenance): "When the
average customer rating of a whole product category rises steadily over the years, does that
usually mean the products themselves got better, or that the rating system and the people using
it changed?"

**Reply**: NOT RECEIVED (see Exchange 1: the bridge failed before the first expert call and
never restarted; no `expert_request_2.json` was ever written).

**Effect on work**: the assumption is instead validated from the data, with the
decomposition the question was meant to elicit:
- between-products (category) level: mean star of tercile-1 vs tercile-3 (by review count,
  2005+) — hair dryer 3.97 → 4.22 (+0.25), microwave 3.08 → 3.76 (+0.68), pacifier 4.24 →
  4.35 (+0.11); all significant (3 points, slopes' SE 0.034/0.050/0.018).
- within-product level (same `product_parent`, pre- vs post-2013, ≥20 reviews with ≥5 on each
  side): hair dryer +0.22 stars (paired t = 3.16, n = 70), microwave −0.09 (t = −0.66, n = 15,
  not significant), pacifier +0.05 (t = 0.94, n = 76, not significant).
- scale-drift evidence: the share of 5-star ratings rose (hair dryer 0.58 → 0.63 over 2013–15;
  pacifier 0.66 → 0.70) while the share of 1-star fell (0.07 → 0.08 after a 2006 peak of 0.24),
  i.e. the distribution compresses toward the top — a change in rating behavior, not only in
  products.
Decision rule adopted: a product's reputation is judged against recent same-category
ratings (rolling 12-month category baseline), and within-product improvement is reported
only where the paired test is significant (hair dryer only). This decomposition is the
structural-assumption check Exchange 2 was meant to supply, computed instead of assumed.

## Exchange 3 — decision-relevant uncertainty threshold

**Question** (see `expert_question_3.md`, builds on Exchange 2's drift finding): "When a company
is deciding whether a new product's early customer ratings are good enough, how many reviews and
how low a negative-rating share would you say are needed before the signal can be trusted?"

**Reply**: NOT RECEIVED (same cause: bridge dead since 05:19:22).

**Effect on work**: the threshold is set from the data via Wilson 95% confidence intervals on
the negative share (k = number of 1–2 star reviews, n = reviews) rather than from an expert
figure:
- the analysis reports a product-level signal only for products with n ≥ 20 reviews; at n = 20
  the Wilson half-width is about ±0.15, so the "failing" label (CI upper bound > 0.30) and the
  "excellent" label (CI lower bound < 0.12) cannot cross without a real difference of roughly
  0.20 in negative share;
- at n = 50 the half-width is ±0.09, and the labels are stable to within ±0.10 of negative
  share; results below n = 20 are reported as "insufficient evidence", never as a verdict;
- cross-check that the thresholds are discriminative: with n ≥ 20, 38/124 hair-dryer products,
  16/22 microwave products, and 36/152 pacifier products are flagged failing; in every
  category the flagged set's mean negative share (0.36–0.62) is at least 2× the unflagged
  set's, and Spearman(negative-affective-word share, product mean star) is −0.58 / −0.85 /
  −0.47, so the rating-based and text-based failure signals agree.
Decision rule adopted (used in the recommendation in `solution.json`): track a new product's
negative share with its Wilson CI; act when the CI upper bound exceeds 0.30 (reputation risk)
and celebrate when the CI lower bound is below 0.12 with n ≥ 50 (reputation established).

## Record of the consultation channel

| # | question file | request file | reply file | outcome |
|---|---------------|--------------|------------|---------|
| 1 | expert_question_1.md | expert_request_1.json (05:16:16) | expert_reply_1.json (05:19:22) | ok=false — expert API call failed |
| 2 | expert_question_2.md | never created | — | bridge down |
| 3 | expert_question_3.md | never created | — | bridge down |

The wait command was run in the foreground once per exchange, as prescribed
(`logs/expert_reply_1.txt`, `logs/expert_reply_2.txt`, `logs/expert_reply_3.txt`).
Per the policy, no reply text is reproduced in `solution.json`; the three exchanges above
each converted into a data-grounded parameter or decision rule as documented.
