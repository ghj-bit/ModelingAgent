# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — MM-Bench 2020_C

Three expert exchanges, one question each. Every reply was converted into a
concrete parameter, constraint, or decision rule before the next exchange; the
value used, its source exchange, and the interval over which it holds are listed
below. No expert phrasing is carried into solution.json.

## Exchange 1 — structural validity / data-model fit

**Question asked** (verbatim, `logs/operator_feedback/expert_question_1.md`):
"Do most buyers skip writing a review entirely, or does a typical buyer write
one?" — asked because the plan was to judge reputation from the average star
rating and monthly review activity, which presupposes that written reviews are
a fair sample of all buyers' opinions.

**Reply (summary of substance, `expert_reply_1.json`):**
- Within one product, ratings are polarized (J-shaped / bimodal: mass at 5
  stars, substantial mass at 1 star, few in between), not clustered.
- The "reviews are a fair sample" assumption is rejected: reviewers are
  self-selected toward strong opinions, so the mean of posted reviews is a
  biased estimator of true buyer satisfaction; the bias is not constant
  (shifts with product age, price, contentiousness).
- Working practice: track the volume and *mix* of reviews — specifically the
  share of low-star reviews — on verified-purchase reviews only; a rising
  low-star share is the reliable "reputation falling" signal, not a falling
  mean.

**How the reply changed the work (before Exchange 2):**
- Constraint C1: all reputation indicators are computed on
  `verified_purchase = Y` rows only (data check: 85.5% / 67.8% / 85.9% of rows
  for hair_dryer / microwave / pacifier).
- Constraint C2: the reputation metric is the low-star share
  L(t) = (#reviews with star ≤ 2 in month t) / (#reviews in month t), not the
  mean star rating. The mean is retained only as a secondary descriptive
  number.
- Constraint C3: the primary "failing" indicator is the *direction and
  persistence* of L(t), not its level. This replaced the initial
  mean-based moving-average plan.

## Exchange 2 — dominant bias mechanism and validation design

**Question asked** (verbatim, `expert_question_2.md`): "After a batch of
low-rated reviews appears, do more complaints follow, or is that noise?" —
asked because a temporal holdout (train on first half of months, OLS-predict
the second half) had test R² ≈ −0.4 to −4.7 across the three data sets, i.e. a
linear trend fit predicts the low-star share worse than its mean.

**Reply (summary of substance, `expert_reply_2.json`):**
- The complaint cascade is real but modest and short-lived (days to a few
  weeks), stronger for products with a small review base.
- It is *not* the dominant cause of unpredictability. The dominant drivers are:
  bursty arrival tied to sales batches/promotions, small monthly counts
  (a handful of reviews swings the share), and seasonal/listing changes. A
  spike is more often a sampling/volume artifact than a quality shift.
- Working practice before believing a run of bad reviews means quality decline:
  (a) the spike must be in verified-purchase reviews and survive removing Vine
  reviews; (b) the low-star reviews should describe the *same specific
  defect*, not scattered complaints; (c) check for a coinciding sales/promo
  batch or listing change; (d) the elevated share must *persist* over several
  months rather than revert; (e) below a few dozen reviews per month the
  monthly share is unstable and month-to-month swings are noise.

**How the reply changed the work (before Exchange 3):**
- Validation design V1: the model is validated by a temporal holdout
  (first 50% of months → predict last 50%) rather than random splits, to
  mirror how the model will actually be used (forecasting the future).
  Outcome reported in solution.json: test R² = −4.74 (hair_dryer), −0.44
  (microwave), −0.72 (pacifier); MAE of the low-star-share forecast
  0.106 / 0.051 / 0.018. Interpretation: a single-month trend is not
  forecastable, so the decision rule must be robust to that.
- Constraint C4 (Vine exclusion): Vine reviews (1.6% / 1.2% / 0.7% of rows)
  are removed from the reputation stream because they are supplied products.
- Constraint C5 (defect coherence): a "failing" flag now additionally
  requires the low-star reviews in the tail window to share a recurring
  defect theme (regex defect lexicon on headline+body), implementing
  "same specific defect, not scattered complaints".
- Constraint C6 (volume floor): months with fewer reviews than a floor are
  treated as noise and excluded from the persistence test (floor set in
  Exchange 3).
- Cascade check computed from the data: within each product,
  P(next review low-star | previous review low-star) = 0.155 / 0.211 / 0.161
  vs P(low | previous high) = 0.123 / 0.145 / 0.085 vs baseline 0.127 / 0.155
  / 0.092 (hair_dryer / microwave / pacifier). The conditional lift is small
  and consistent with a short-lived, bounded cascade — supporting the
  persistence-over-spike rule rather than a change-detection rule.

## Exchange 3 — decision-relevant uncertainty threshold

**Question asked** (verbatim, `expert_question_3.md`): "How many months of
steady complaints before a product manager treats a product as failing?"

**Reply (summary of substance, `expert_reply_3.json`):**
- Do not act on a low-rating trend shorter than about 3 consecutive months;
  4–6 months of sustained elevation is the working "failing" threshold.
  One month = noise, two months = watch, three-plus months of persistently
  elevated low-star share with the same defect recurring = actionable.
  Persistence, not depth, distinguishes real decline from a burst.
- Practical floor for the monthly share to be readable: roughly 30–50
  verified reviews per month; below ~30/month swings are sampling noise.
  The floor is somewhat higher for microwaves (more heterogeneous category)
  than for pacifiers or hair dryers.

**How the reply changed the work (final parameters, used in `code/reputation.py`):**
- Parameter P_MONTHS = 3 (persistence window; sensitivity sweep run at
  2, 3, 4 — conclusions unchanged: zero products with a solid verified
  history cross the elevated threshold in any window).
- Parameter FLOOR_REVIEWS = 30 (minimum verified reviews per month for a
  month to count; sensitivity sweep 20 / 30 / 50).
- Decision rule (final, per product): flag `failing_signal` iff
  (i) at least P_MONTHS trailing months each have ≥ FLOOR_REVIEWS verified
  non-Vine reviews;
  (ii) the mean low-star share over those months exceeds
  max(baseline + 1 SD over the product's solid months, 1.5 × baseline);
  (iii) the defect-theme share over the tail is at least 2× the product's
  solid-month defect share.
- Result across all three data sets: 0 products flagged as failing at
  (P_MONTHS=3, FLOOR=30) — and at every swept combination. This is a
  substantive finding (see solution.json): after the bias gates, no product
  in these competing-product data sets shows a persistent, defect-coherent
  decline, so the reliable signal to track is the *level and mix* of the
  low-star share with the volume floor as a confidence gate, not a
  change-detector on monthly spikes.

## Parameter table (values used in the model, with source)

| name | value | interval tested | source |
|---|---|---|---|
| verified-only gate | verified_purchase = Y | n/a (binary) | Exchange 1 |
| Vine exclusion | vine = N | n/a (binary) | Exchange 2 |
| low-star cutoff | star_rating ≤ 2 | n/a (definition) | Exchange 1 |
| P_MONTHS (persistence) | 3 | 2–4 | Exchange 3 (sweep: 2,3,4) |
| FLOOR_REVIEWS (monthly volume floor) | 30 | 20–50 | Exchange 3 (sweep: 20,30,50) |
| elevation threshold | mean(L_t) > max(baseline+1SD, 1.5×baseline) | n/a | Exchange 2 (persistence, not depth) |
| defect-coherence factor | tail defect share ≥ 2× baseline | n/a | Exchange 2 (same defect recurring) |

All other numbers in solution.json come from the three supplied TSV files.
