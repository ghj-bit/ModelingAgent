# Expert Interaction Evidence — Problem 2020_C

Ten exchanges, one question each. For each: the question, the essence of the expert reply, and how the reply was turned into work (a parameter, constraint, or model component, with its interval of validity).

## Exchange 1
**Q:** For consumer products like microwaves, baby pacifiers, and hair dryers, which single number from customer ratings would you watch most closely to decide early if a new product is winning or failing?
**Reply (essence):** Watch the trailing-window mean star rating, not the lifetime average. Below ~3.5 stars a product is in trouble; 4.0–4.3 acceptable; 4.4+ a strong winner. Trend of the recent-window mean is the early-warning indicator; pair with review volume only to confirm the trend is not noise.
**Turned into work:**
- Model parameter: primary health metric = trailing-window mean star rating over [30, 180] days. The sweep over window (90/180/365) showed success/failure classification stable, so 180 d is a valid interval.
- Decision thresholds adopted into the composite: `mean_star < 3.5` → trouble zone, `>= 4.4` → strong winner (used to interpret, and cross-check, the composite score).

## Exchange 2
**Q:** When a product's recent average star rating starts sliding down over a few weeks, what's the usual first sign you see in the written reviews that explains the slide?
**Reply (essence):** A rise in the share of reviews containing negative quality descriptors ("broke," "stopped working," "disappointed," "returned"); complaints clustering on the same feature (one production batch / time window); and a growing gap between headline/body sentiment and the star rating (a 3-star that reads like a 1).
**Turned into work:**
- Defined two model components from this: (a) *negative-descriptor share* = fraction of reviews in the window containing >=1 defect/failure word; (b) *sentiment–star gap* = hedge-and-neg presence on 3–5-star reviews. Both feed the composite success index.
- Built a defect-cluster detector that groups low-star reviews by feature (stopped_working, breakage, leak, smell, return, noise, electric/burn, fit, dirt/cleaning) to flag "the same defect recurring."

## Exchange 3
**Q:** Among Amazon customers, does seeing a run of low star ratings make someone more likely to write a review, or does it make them just stop buying?
**Reply (essence):** Neither strongly. The dominant effect of a visible run of low ratings is to suppress purchases, which shrinks the pool of future reviewers. There is only a modest tilt toward negative-review writing (a "me too" / corrective effect). Expect negative-share up AND review count down — not a review surge.
**Turned into work:**
- Became a testable constraint in the "do low ratings incite reviews?" analysis: the model was asked to test whether a prior-month low-star share predicts next-month review count. Result: partial coefficients on the prior low-share were ~0 to negative (microwave +0.013, hair dryer -0.16, pacifier -0.046); simple correlations small and negative (-0.04 to -0.08). This confirms the "no surge; if anything a shrinking pool" mechanism, so the model does NOT assume a review spike after rating declines.

## Exchange 4
**Q:** For products like these, how long before a quality problem or a genuinely new product launch shows up clearly in customer reviews?
**Reply (essence):** A quality problem shows first signs in ~2–6 weeks, a visible shift in ~1–2 months. A reliable launch read takes ~2–3 months; a stable reputation 6+ months. Early reviews skew to enthusiasts/Vine.
**Turned into work:**
- Calibrated the analysis time horizons: the monthly trend is fit over the trailing 12 months (a "stable" read), the defect cluster uses the trailing 365 days, and the composite uses a 90–180 d window. The <15-review / ~30 / 50–100+ tiers (Ex.10) bound where these reads are trustworthy.

## Exchange 5
**Q:** When you read online product reviews, which words in the text tell you most about the reviewer's true satisfaction, beyond the stars?
**Reply (essence):** Highest signal = specific failure/defect verbs ("broke," "stopped working," "died," "leaked," "cracked," "returned," "refunded"), concrete functional praise ("works great," "easy to use," "exactly as described"), and effort/regret language ("waste of money," "disappointed," "unfortunately"). Hedge/contrast words ("but," "however," "although") mark reviews whose stars overstate the negativity. Weakest = generic intensifiers ("amazing," "perfect," "awesome") and headline-only enthusiasm. Most telling = star-vs-text-concreteness mismatch.
**Turned into work:**
- The negative-descriptor lexicon (defect/failure verbs + regret) and positive lexicon (concrete functional praise) used in the text analysis were taken directly from this list. Hedge words are used to compute the sentiment–star gap. Generic intensifiers are deliberately NOT used as quality signal.
- Validated: mean text sentiment is monotone in star level for all three products (1★ ≈ -0.26 to -0.46, 5★ ≈ +0.59 to +0.71), so the lexicon captures the star dimension.

## Exchange 6
**Q:** Among the three products — microwave, baby pacifier, hair dryer — which has customers who are usually the harshest or most demanding in their reviews?
**Reply (essence):** Baby-pacifier customers are the harshest (safety/health-adjacent, emotionally charged, unforgiving of any flaw). Microwaves and hair dryers are ordinary adult appliances, expressed more matter-of-factly.
**Turned into work:**
- Used to interpret, not to change, the numbers: a given star average on a pacifier is harder-won than on an appliance, so cross-product comparison of raw mean stars is biased. The model therefore does not rank products by raw mean star; it compares each product's own trailing trend and defect composition. Data check consistent with this: pacifier 5★ share is 66.9% and negative-descriptor rate per low star is the lowest of the three (1★ = 52.8% vs microwave 74.9%), i.e. pacifier parents still give relatively fewer defect words per complaint — the harshness shows up in the emotional/return framing rather than defect count.

## Exchange 7
**Q:** When deciding whether a competing product on Amazon is winning or failing, do you trust the overall star rating or the helpfulness votes more?
**Reply (essence):** Trust the star rating (recent-window mean and trend). Helpfulness votes are a weak, confounded signal — they depend on visibility, ranking, age, Vine; most reviews get zero votes; a review can be "helpful" while negative. Use helpfulness only as a secondary cue for which complaints resonate, never as the primary win/fail indicator.
**Turned into work:**
- Fixed the measure hierarchy: star-based metrics are primary; helpfulness is demoted to a secondary, diagnostic tool. The model therefore reports helpfulness only to rank *which specific defects/caveats resonate* (via high-vote review content), not as a quality score.

## Exchange 8
**Q:** For these everyday products, does a review with many helpful votes usually describe a big problem, or a minor one?
**Reply (essence):** Usually a minor-to-moderate, well-articulated issue — a detailed, balanced account of a small annoyance, a workaround, or a "what to know before buying" caveat. High helpfulness = well-written/informative, not severe. Severe failures (safety, dead-on-arrival) are short/emotional and rarely accumulate many votes.
**Turned into work:**
- The high-helpfulness-vote review set is interpreted as the set of *recurring practical caveats / design-feature signals* for Sunshine (the "what to know before buying" content), not as a severity ranking. This is what the "top helpful" content analysis reports.

## Exchange 9
**Q:** If you were launching one of these products, which customer behavior after launch would worry you most in the first month?
**Reply (essence):** A rising share of negative reviews naming the SAME specific defect across independent reviewers (often a single batch/window), especially paired with a falling review count. That combination in month one is the clearest sign the launch is failing and needs intervention before the reputation sets.
**Turned into work:**
- Became the failure-detection rule in the composite: low composite score is driven by (mean_star in the trouble zone) AND (high negative-descriptor share) AND (a dominant single defect feature in the cluster) AND (falling review count). A product is flagged "failing" when it hits several of these simultaneously, not on any one alone.

## Exchange 10
**Q:** For a new product launch, what's the minimum number of customer reviews you'd want before trusting the average star rating at all?
**Reply (essence):** <15 reviews anecdotal; ~30 a first tentative read (SE ≈ 1.1/√n, so ±0.2 stars at n=30); 50–100+ before the average is stable enough to act on. Early reviews skew to enthusiasts/Vine, biasing the mean upward.
**Turned into work:**
- Model parameter: `min_reviews = 30` is the minimum product-level sample before the composite score is reported (products below it are excluded from the success/failure counts). The ~30 value also matches the computed SE ≈ ±0.2 stars. The enthusiast/Vine upward bias is recorded as a known limitation.

---
## Summary of how replies changed the model
- Primary metric = trailing-window mean star rating; thresholds 3.5 / 4.4 (Ex.1,4).
- Text components = negative-descriptor share, positive/functional-praise count, hedge-word sentiment–star gap (Ex.2,5).
- Defect clustering = feature-level recurrence detector (Ex.2,9).
- Helpfulness = demoted to a secondary "which caveats resonate" tool (Ex.7,8).
- Failure rule = trouble-zone stars + high negative share + dominant single defect + falling count (Ex.9).
- Review-count incitement = tested and confirmed absent (Ex.3).
- Cross-product comparability = not by raw stars (Ex.6).
- Sample-size gating = 30 reviews min (Ex.10).
