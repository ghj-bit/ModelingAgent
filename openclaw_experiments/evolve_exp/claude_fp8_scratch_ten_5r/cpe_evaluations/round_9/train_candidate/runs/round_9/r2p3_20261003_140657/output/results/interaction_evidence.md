# Expert Interaction Evidence — MM-Bench 2020_C

Policy: mechanism → constraint → parameter; 10 exchanges, one question each.
All questions were single, ≤20 words, common-sense, non-prescriptive.

## Exchange 1
- **Question:** When shoppers pick between similar products on an online store, what factor matters most to you personally when deciding what to buy: the star rating, or reading the written reviews?
- **Reply (essence):** Rating is used first as a fast filter; written reviews decide among the shortlist. Reviews are the decisive signal because they say *why* and match the buyer's use case; a star average is coarse and gameable.
- **Effect on work:** Fixed the dominant mechanism: purchase decisions are a two-stage filter (star average gates, review text decides). This justifies modeling both star distributions and text content as informative, with text as the tie-breaker. Basis for the "most informative measures" answer (Q2a) and for the composite product-health score that conditions text features on the star filter.

## Exchange 2
- **Question:** You said written reviews decide the purchase. About how many reviews do you typically read before you decide?
- **Reply (essence):** 3–10 reviews, read selectively: recent, most-helpful, and some lowest-rated ones; stop when themes repeat.
- **Effect on work:** Parameter `n_reviews_read ≈ 5 (interval 3–10)` — used as the size of the decision-relevant sample: a product's "reputation as perceived by a buyer" is the content of ~5 strategically sampled reviews, not the full history. This motivates tracking (a) most-helpful review themes, (b) recent reviews, and (c) low-star complaints separately, rather than one aggregate number.

## Exchange 3
- **Question:** You mentioned checking low-star complaints. For a new product launch, what kind of failure in these products kills a purchase for you?
- **Reply (essence):** Safety/reliability failures (pacifier: choking/material hazard; microwave: fire/electrical or dies quickly; hair dryer: overheating, burning smell, cord failure) are non-negotiable — one credible report kills the purchase. Ordinary performance complaints do not.
- **Effect on work:** Established the primary constraint: a binary, asymmetric "red flag" channel that overrides the average. Built the safety-lexicon channel (overheat, smoke, smell, burn, fire, choke, detach, melt, BPA, spark, shock, injury) and found 27.5% and 29.2% of 1–2-star hair-dryer and microwave reviews hit it, vs ~2.8% of 4–5-star ones (8.5× concentration). This drives the "safety_flag_count" term that overrides the score in the health model.

## Exchange 4
- **Question:** How long does a product's reputation usually take to settle on an online store — how many weeks or months?
- **Reply (essence):** ~2–3 months to look stable, ~6 months settled; the driver is review volume (few dozen to ~100 reviews), not calendar time. Early reviews skew positive; a safety failure can reset reputation at any time.
- **Effect on work:** Parameters: `settled_volume ≈ 30 (interval 30–100)` reviews; trend window 14 weeks. Defined two time-based measures: (a) rolling 14-week mean star and 4–5-star share with min 30 reviews in window ("settled" trend), and (b) early-bias check: first-half vs second-half means (hair dryer +0.365, pacifier +0.27, microwave −0.035). Confirmed the positive early-bias pattern is visible (low-volume early windows) and that reputation can reset (2006 hair-dryer collapse to ~2.2–2.6 in rolling windows).

## Exchange 5
- **Question:** What star rating would you personally consider too risky to buy a product at, even with positive written reviews?
- **Reply (essence):** Hard floor ~3.0, caution zone 3.0–3.5; volume matters (3.2 on 500 reviews is firm, 3.2 on 8 is noise); shape matters more than the number — 4.2 with a 1-star safety cluster is riskier than a uniform 3.8.
- **Effect on work:** Parameters `star_floor = 3.0`, `star_caution = 3.5`, applied via Wilson lower bound (small samples shrink toward the prior, formalizing the volume caveat). Applied: share of products with Wilson-lo(4–5 share) in low band: hair dryer 18/124, microwave 26/42, pacifier 55/275 (min 10 reviews). "Shape matters" is operationalized as polarization (|1-star − 5-star| mass) plus the safety-override from exchange 3.

## Exchange 6
- **Question:** If a product's average star rating drops after it has been on sale, what do you assume went wrong?
- **Reply (essence):** First suspect is reviewer-mix change (early adopters vs mainstream buyers); then, in order: defects surfacing at scale, durability problems, silent component/sourcing changes, expectation mismatch, a safety issue. A sustained multi-review decline is "something real", not noise.
- **Effect on work:** Defined the decreasing-reputation decision rule: a decline is real if the rolling 14-week 4–5-star share falls ≥10 percentage points from the prior 14 weeks *and* the window has ≥30 reviews (ex4 volume rule); if it also carries a rise in safety-flag share, it is flagged as product-caused rather than mix-driven. Used to classify the microwave dataset's flat/declining state and the hair dryer's 2006 reset episode.

## Exchange 7
- **Question:** After buying a product, do you write a review when it impressed you, disappointed you, or both equally?
- **Reply (essence):** Disappointment is the stronger trigger — roughly twice as likely to write after a bad experience as a good one; the neutral middle produces no review.
- **Effect on work:** Parameter `review_asym ≈ 2.0` (interval ~1.5–2.5). Used to interpret the star distribution as biased: a steady product with neutral majority still yields ~2:1 negative/positive review inflow, so the 4–5-star *share of reviews* is a lower bound on satisfied customers; the review inflow rate is a leading indicator (surge in 1–2-star inflow precedes average decline). Checked against data: low-star share is 11–32% across the three categories, consistent with a 2:1 asymmetry on top of genuinely mixed satisfaction.

## Exchange 8
- **Question:** You mentioned checking the most helpful reviews. What makes a review feel genuinely helpful to you when reading?
- **Reply (essence):** Specifics over adjectives; context (ownership duration, usage, comparisons); both sides; failure detail; outcome (returned/replaced/kept). Length and polish don't matter. Helpful votes are a weak proxy — they reward early and vivid reviews.
- **Effect on work:** Validated the text-feature design (concrete-failure lexicon, outcome words) and justified *not* using helpful_votes as the quality metric. Confirmed in data: corr(helpful_votes, body length) is only 0.20–0.42 and corr(helpful_votes, star) ≈ 0; the most-voted reviews include 24-word and 2-word bodies. So helpful votes are reported as a visibility measure, not an information measure.

## Exchange 9
- **Question:** When a product is new on the store and has only a handful of reviews, do you trust them?
- **Reply (essence):** Not as a quality signal — anecdotes, not evidence; averages at low volume mean nothing (and skew positive). But specific failure reports are worth acting on even at low volume.
- **Effect on work:** Formalized with the Wilson lower bound: at n=6, the interval on a 4.8 average is wide (~0.61–0.98); the 30-review `settled_volume` threshold is where the average "means anything". Red-flag channel (ex3) remains active at all volumes — this is exactly the "low-volume, high-value" content.

## Exchange 10
- **Question:** When a competitor's similar product gets many 5-star reviews, what makes you still consider buying it?
- **Reply (essence):** Shape and content behind the 5s: low-star complaints about trivial things (size, noise, color), specific 5-star reviews matched to the use case, real volume (hundreds), and no credible safety/reliability report anywhere. Vague praise + dangerous low reviews = walk away.
- **Effect on work:** Completed the "failing product" indicator set: a high mean is *not* sufficient; the composite requires (i) Wilson-lo(4–5 share) above the caution threshold, (ii) safety-flag rate among low-star reviews below the baseline, (iii) specific (non-boilerplate) high-star text. Boils down the final success/failure classifier used in Q2c.

## Parameter table (calibrated inputs from exchanges)
| name | value | interval | source |
|---|---|---|---|
| n_reviews_read | 5 | [3, 10] | exchange 2 |
| settled_volume | 30 | [30, 100] | exchange 4 |
| star_floor | 3.0 | [2.8, 3.2] | exchange 5 |
| star_caution | 3.5 | [3.3, 3.7] | exchange 5 |
| review_asym | 2.0 | [1.5, 2.5] | exchange 7 |
| trend_window | 14 weeks | [8, 26] | exchange 4 |

No web/literature search was required: every empirical parameter the model needs was either computed from the three supplied datasets or supplied by the exchanges above.
