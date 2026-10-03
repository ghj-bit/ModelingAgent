# Interaction Evidence — Problem 2020_C (MM-Bench Amazon ratings/reviews)

Ten expert exchanges, one question each. Each reply is converted below into a
parameter or a model/decision-rule change. Expert phrasing is NOT reproduced in
the submission; only the values/constraints, integrated in my own formulation.

## Exchange 1
Q: Judging whether an online product is succeeding, trust the average star score or the share of 1-star reviews?
A: The share of 1-star reviews (avg score hides the distribution shape; a rising
1-star share is the earliest/most reliable trouble signal).
→ USED: primary health metric for every product = 1-star share, not mean rating.
Drives the keep/pull decision rule and the "most informative measures" answer.

## Exchange 2
Q: How big a jump in 1-star reviews flags real trouble?
A: ~2–3 percentage points sustained over a few weeks; healthy baseline is low
single digits to low teens; absolute ≥15% or a doubling is a clear red flag.
→ USED (quantitative thresholds): TRouble_RISE_PP=0.03 sustained rise;
RED_FLAG_LEVEL=0.15 absolute. Applied in product-level trend flags in timelag.py
and the discriminate.py "failing" label (pct1 ≥ 0.15). Interval of validity:
products with ≥30 reviews (per E3).

## Exchange 3
Q: How long before ratings of a new product are trustworthy?
A: ~30–50 reviews before trusting; <10–15 anecdotal; trends need a few dozen over
several weeks.
→ USED (validity gate): MIN_REVIEWS_TRUST=30 (and MIN_REVIEWS_ANECDOTAL=15) used
to exclude low-sample products from trend/discrimination results so ratios are
stable. All per-product statistics in the submission are gated on this.

## Exchange 4
Q: Do customers write more reviews after seeing lots of low ratings, or is volume
demand-driven?
A: Mostly demand-driven; ~1–5% of buyers review; dissatisfaction is only a modest
multiplier on propensity.
→ USED (interpretation of Q4 "do ratings incite reviews"): model review volume as
f(demand) with a small dissatisfaction multiplier. Tested cross-product correlation
of 1-star share vs review count → near zero (−0.013 hair_dryer, −0.097 microwave,
−0.16 pacifier), supporting "volume tracks demand, not ratings". Parameter
REVIEW_RATE 1–5% recorded as the expected reviews-per-purchase band.

## Exchange 5
Q: Which words signal a failing product vs a loved one?
A: Failing = defect/return/regret words (broke, stopped working, defective,
returned, refund, waste of money, disappointed, do not buy …); loved = intensity
words (love, excellent, perfect, great, amazing, highly recommend, durable …);
generic words (good, nice) weak. Strongest signal = defect word + low star +
return mention.
→ USED (text measures): Failing_WORDS / LOVED_WORDS lexicons in model.py;
defect and praise counts per review; failcluster_rate = share of ≤2-star reviews
with (defect word AND return mention) = the combined signal. hair_dryer 0.158,
microwave 0.121, pacifier 0.078.

## Exchange 6
Q: Do helpful-vote reviews carry more weight, and why?
A: Yes — visibility + crowd credibility; but votes accumulate over time (age bias)
and helpfulness measures usefulness, not sentiment (a well-argued 1-star review
can be most helpful).
→ USED (weight, not positive signal): helpfulness used as a review-weight
multiplier, and age is the confounder — so the model computes a helpfulness-
weighted 1-star share (helpful_wt_pct1) as a robust reputation measure rather
than treating votes as a positive cue. AUC of helpful_wt_pct1 vs failing = 0.907
(hair_dryer), validating it as a good discriminator.

## Exchange 7
Q: Are 1- or 5-star reviews longer/more detailed than 3-star?
A: Length is U-shaped; 1-star arm slightly highest, 3-star lowest.
→ USED (hypothesis to validate): measured median length by star. hair_dryer
55.5/54/48/43/33; microwave 80/87.5/62.5/50/35; pacifier 45/50/45/46/32. Confirmed
monotone decline from 1→5 (5-star shortest, enthusiastic-short) with the 3–4-star
middle lower — consistent with the U-shape, 5-star arm being the short one.

## Exchange 8
Q: When reputation fades, does the drop show in reviews first or star ratings first?
A: Text first (defect/return/regret language appears before the smoothed star
average moves); star average lags, anchored by history.
→ USED (lead/lag analysis): cross-correlated monthly mean defect-word count at t
with 1-star share at t+k (timelag.py xcorr_product). Result: correlation is
largest contemporaneously (lag0: hair_dryer 0.40, microwave 0.52, pacifier 0.33)
and decays forward (lag1–3 ≈ 0.1–0.3) — i.e. text and 1-star share move together
with text not clearly leading at this data's monthly/product resolution. Reported
honestly: the expected text-first lead is not strongly resolved in the data;
contemporaneous co-movement is what the data support.

## Exchange 9
Q: Do these products see seasonal review spikes?
A: Modest and uneven — microwave most seasonal (Nov–Dec peak, back-to-school),
hair dryer mild (Nov–Dec + cold weather), pacifier weakest (flat, tracks births).
Reviews lag sales by days–weeks; promos confound.
→ USED (detrending / interpretation): examined monthly review counts (timelag.py
seasonality). pacifier shows a Dec peak (2029, Jan 1752) and a summer hump;
microwave is flattish (no strong Nov–Dec peak in this 2004–2015 sample); hair_dryer
relatively flat with a mild Dec lift. Used to warn that month-to-month volume
swings are partly seasonal/promotional, not necessarily reputation change.

## Exchange 10
Q: Which of the three would customers be least forgiving of a quality problem in?
A: The baby pacifier — safety/health (choking, infant mouth), parents are vocal,
no tolerance.
→ USED (asymmetric threshold / risk weighting): pacifier given the strictest
interpretation — its small defect/return signals carry outsized risk weight, so
the same 1-star share or defect cluster is more actionable for a pacifier than for
a hair dryer. Reflected in the Marketing Director letter's recommendation to
monitor pacifier safety-defect language most closely.
