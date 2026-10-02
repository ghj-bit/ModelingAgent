# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — Problem 2020_C (Amazon reviews: hair dryer, microwave, pacifier)

Exactly 3 exchanges, one question each, in order. File names: `expert_question_N.md` / `expert_reply_N.json` in `logs/operator_feedback/`.

## Exchange 1 — structural fit of data to model
- **Question:** When judging how a product is doing over time, which matters more: review volume lately, or the recent 5-star share?
- **Reply (gist):** Recent 5-star share matters more. Volume is driven by popularity and by dissatisfied customers posting, so it is a weak, biased proxy for reputation; the recent 5-star share directly measures satisfaction.
- **How the reply changed the work:** Defined the reputation metric as a *share* (proportion of 5-star ratings) computed over a rolling window, not as raw review counts. This is the structural form the model must use: a bounded [0,1] ratio, not a count, so it is comparable across products of different popularity. Applied in the time-series model (rolling 5-star share, `s5(t)`), in the Q1 recommendation (track 5-star share + Wilson score), and in the Q4/Q5 analyses (which use shares and proportions, never raw counts, as the headline metric).

## Exchange 2 — dominant bias / selection mechanism
- **Question (built on Ex. 1):** Among buyers who never write a review, who is most likely missing — happy buyers or very angry buyers?
- **Reply (gist):** The very angry buyers. They stop buying, return the product, or complain to the seller rather than posting publicly; written reviews over-represent the satisfied and the mildly disappointed.
- **How the reply changed the work:** Added a stated selection-bias mechanism to the model: the observed 5-star share is an *upper bound* on true satisfaction, because the most negative purchasers under-represent in the written data. Consequences encoded: (a) Wilson-lower-bound confidence on the 5-star share is used so a small number of 5-star early reviews cannot be over-read; (b) a *falling* 1-star share over time is interpreted cautiously — it may reflect selection (angry people stop posting) rather than genuine quality improvement; (c) the limitation section attributes part of the apparent rating level to this self-selection rather than to product quality.

## Exchange 3 — validation / interpretation criterion
- **Question (built on Ex. 1–2):** What does a new product's rating history look like in its first few weeks that tells you it is heading for success?
- **Reply (gist):** A high and stable 5-star share from the first reviews, holding near 4.5–5.0 as volume grows rather than drifting down. Trouble: an early high rating that steadily erodes as volume grows, or a low rating that never recovers.
- **How the reply changed the work:** Supplied the interpretive threshold: 5-star share ≥ ~4.5/5 (i.e. average star ≥ 4.5, equivalently 5-star share high) and *stable* (not decaying) as volume grows = success signal. Operationalized as the decision rule in Q2/Q3: (i) mean star ≥ 4.5 in a recent window; (ii) slope of rolling mean star over that window ≈ 0 or positive (no erosion); (iii) minimum review count for the call to be meaningful (ties into Wilson bound). The "failing" product rule is the mirror: sustained decline of rolling mean star, or mean star well below 4.5 that does not recover.

---
All three replies are input, not content: the submission uses the *metrics and thresholds* above, stated in the model's own terms, and does not copy any expert sentence.
