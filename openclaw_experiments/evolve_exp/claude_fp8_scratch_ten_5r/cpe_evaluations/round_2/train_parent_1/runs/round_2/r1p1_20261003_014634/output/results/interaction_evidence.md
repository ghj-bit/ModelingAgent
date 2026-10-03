# Interaction Evidence — MM-Bench 2020_C

Ten expert exchanges, one question each. Each reply was turned into a
parameter, constraint, or code change before the next exchange; the affected
code is cited.

## Exchange 1 — reputation decay lag
- Q: When a product's recent customer reviews turn mostly negative, how quickly do shoppers notice and stop buying it?
- Reply (gist): no fixed lag; erosion over roughly 1–3 months for mainstream
  consumer products, faster with high review velocity or safety/core-function
  defects, slower with low volume or strong brand loyalty.
- Use: set the memory horizon τ (months) of the exponential-decay reputation
  index in `code/reputation.py` and swept τ = 1, 3, 6 months
  (`logs/reputation.log`); 3 months adopted as central (upper end of the
  expert's 1–3 month band), with 1 and 6 as robustness bounds.
- Interval of validity: stated for mainstream consumer products on a large
  platform; our categories (microwave, hair dryer, pacifier) fit this.

## Exchange 2 — dominant early-failure defect
- Q: When buyers complain that a microwave or hair dryer fails quickly, which single defect do they mention most often?
- Reply (gist): premature death of the unit — "stopped working" / "died"
  within weeks to months; magnetron burnout for microwaves, heating element or
  motor failure for hair dryers, often with burning smell or overheating.
- Use: defined the category failure-theme regexes in
  `code/product_health.py` (THEMES dict) and `code/describe.py` theme analysis;
  validated against data: in 1–2 star reviews, "died/stopped working" appears
  in 21.8% of microwave low reviews and 15.5% of hair-dryer low reviews, vs
  2.6% / 1.9% in 4–5 star reviews (`logs/describe.log`, themes section) — the
  data confirms the expert's ranking.

## Exchange 3 — what shoppers actually read
- Q: Do customers usually read only recent reviews, or the full history, before judging a product?
- Reply (gist): a small recent slice (default "most recent" sort) dominates the
  impression; the displayed all-history average still anchors the decision.
- Use: two-part reputation model in `code/reputation.py`:
  R_recent (exponentially weighted, τ from exchange 1) vs R_all (full-history
  mean); the gap R_recent − R_all is the declining/improving indicator.

## Exchange 4 — review propensity
- Q: After receiving a very bad product, do most people write a review, or say nothing?
- Reply (gist): most say nothing; a very bad product sharply raises the odds of
  writing — dissatisfied buyers several times more likely to post; roughly
  1 in 5 to 1 in 3 of very dissatisfied buyers will post a negative review.
- Use: review-generative process assumed for the marketing tracker (Q1):
  low-star reviews are the reliable early-warning signal, high-star reviews are
  a silent-majority phenomenon. Quantified in data (`logs/star_effects.log`):
  1-star reviews are longer (e.g., microwave 1-star mean 109.7 words vs
  5-star 62.7) and attract more vote participation (microwave: 79.1% of 1-star
  vs 56.8% of 5-star reviews get at least one vote).

## Exchange 5 — negativity bias
- Q: Before buying a hair dryer, do most shoppers weigh negative warnings or positive praise more heavily?
- Reply (gist): negative warnings weigh more (negativity bias), strongest for
  safety and durability complaints; a repeated specific warning can deter even
  with a high average; weak for subjective gripes.
- Use: set product-health weights in `code/product_health.py` — star level
  w1=0.40, low-star share w2=0.25, failure-theme text w3=0.30,
  unhelpful-consensus penalty w4=0.05 (penalty form so text warnings enter
  asymmetrically against success, matching "warnings dominate praise").
  Swept w1 = 0.3/0.4/0.5 (`logs/product_health.log`); conclusions stable.

## Exchange 6 — pacifier acceptance vs durability
- Q: When judging a pacifier, do parents care more about how long it lasts or whether their baby takes to it?
- Reply (gist): acceptance is make-or-break; rejection dominates negatives;
  durability matters only as safety/hygiene (tearing, cracking) and is
  secondary.
- Use: pacifier failure theme in `code/product_health.py` changed from generic
  "died" to rejection/tear vocabulary (reject, refuse, won't take, spits out,
  bit through, tore, cracked). Result: pacifier base failure-theme share in
  low reviews 8.0%, failing-decile share 18.0% vs ok-decile 4.8%
  (`logs/product_health.log`), confirming rejection as the pacifier failure
  signal.

## Exchange 7 — verified-purchase weighting
- Q: Do shoppers trust reviews from verified purchases more than regular ones? Roughly how much?
- Reply (gist): yes; a verified review is worth roughly 2–3 unverified ones;
  unverified positives are discounted most, unverified negatives least.
- Use: credibility weighting c (unverified = 1/c) swept in
  `code/verified_effect.py` over c = 1, 2, 3 (`logs/verified_effect.log`),
  c = 2 adopted as central. Effect is real but modest on these datasets:
  microwave weighted mean star 3.68 (c=2) vs 3.45 plain; weighted top-minus-
  bottom product separation improves from 1.96 (plain) to 2.07 (c=2) stars.
  Verified fractions: hair dryer 85.5%, microwave 67.4%, pacifier 51.7%.

## Exchange 8 — helpfulness votes as a filter
- Q: Do shoppers read the most helpful reviews before deciding on a product? How do they pick?
- Reply (gist): helpfulness sorting is a secondary path; used by deliberate
  buyers, mainly the top 3–5 voted reviews; a high-vote negative review
  signals a widely-shared complaint; vote lists skew old.
- Use: `code/helpfulness_signal.py` compares top-decile-voted vs low-voted
  reviews (`logs/helpfulness_signal.log`): top-voted reviews carry
  mean_helpful_ratio 0.90–0.93 vs 0.75–0.80 for low-voted, and their
  star distribution is meaningfully more positive (microwave top-voted mean
  star 3.71–4.19 vs low-voted 2.70–2.86) — the crowd-vote channel
  concentrates on consensus content. Tracker implication: track the
  helpful-ratio trend of recent low-star reviews as an early-warning.

## Exchange 9 — minimum reviews to trust a rating
- Q: When a new product launches, how many reviews do shoppers typically need before trusting its rating?
- Reply (gist): no fixed threshold; ~10–30 reviews before the rating is
  treated as meaningful, 30–50 for reasonable confidence; safety/high-ticket
  items raise the bar to 50–100; below ~10 shoppers rely on text and badges.
- Use: `code/min_reviews.py` computes Wilson 95% lower bounds of the star
  scale as a function of n (`logs/min_reviews.log`): at n=10 a true 5-star
  product has lower bound 3.89, a true 3-star product 1.95; at n=30: 4.55 /
  2.33; at n=50 (3-star): 2.47. The data confirms the trust-gap concern:
  80.6% of pacifier products have <10 reviews (median 3), 66.7% of microwave
  products have 10–30 (median 22) — so for these launches, review count is
  the binding constraint in the first months and text/badge signals must
  substitute.

## Exchange 10 — count vs recency
- Q: Which matters more when judging a product's reputation: recent review quality or total review count?
- Reply (gist): recent quality matters far more; count is a credibility gate
  (10–30), beyond which additional volume adds little and can mask decline by
  diluting the average; for a brand-new product count temporarily dominates.
- Use: fixed the interpretation of the Q2 deliverable: the primary
  reputation metric is R_recent (τ=3 months) with R_all as the anchor; the
  all-history average is explicitly *not* used as the health signal because
  dilution can hide a live decline. For the launch phase (products with
  <10–30 reviews) the tracker switches to the exchange-9 regime: review
  count itself, plus verified fraction and text themes, is the metric.

## Notes
- No reply text was copied into solution.json; only values (τ, weights, c,
  thresholds), constraints (asymmetric warning weight, acceptance-dominates-
  durability for pacifiers), and the resulting code/tests are used.
- All empirical parameters appear in the parameter table of
  solution.json `mathematical_modeling_process` with source = exchange number.
