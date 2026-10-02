# Interaction Evidence — MM-Bench 2023_Y

## Exchange 1 — Data Provenance

**Question (expert_question_1.md):** The data set contains a few listings with prices far below or far above the norm for their size, plus a handful of missing or duplicated records. From your experience listing boats for sale, are such extreme prices usually genuine bargains or luxury specs, or do they most often signal listing errors — and would you still trust the bulk of the data as a fair picture of the market?

**Reply (expert_reply_1.json):** Extreme prices in brokerage listings are far more often listing errors than genuine bargains or luxury specs. Typical causes: a misplaced decimal or currency-conversion slip, a price entered as a deposit or monthly payment, a "project boat" / damaged hull priced for quick sale, or a typo in length/year. Genuine outliers exist but are the minority and are explainable from the listing text, not price alone. Treat the extreme tails as suspect — verify or exclude — but trust the bulk of the data; with ~3,500 listings a handful of bad records will not materially distort size/age/region price relationships provided they are trimmed rather than left to pull a regression. Duplicates and missing fields are routine and easily handled. The central tendency and broad regional/size gradients are a fair picture of the December 2020 asking-price market.

**How it shaped the work:**
- Parameter: **winning/trimmed-price rule** adopted. Extreme price records (those deviating far from the make/variant/length/age norm) are treated as suspect and trimmed from the fitted sample, rather than retained to pull a regression. Implementation: per-variant (or per make/length) robust z-score on log price; drop records beyond a 4-sigma threshold, and drop the absolute low-price (<$50k) / high-price (>$1.5M) tails flagged in the profile. The trimmed sample is the fitted sample; the full sample is reported alongside.
- Constraint: the bulk of the data is treated as a fair picture of the Dec-2020 asking market, so central-tendency and regional/size gradients are trusted and reported; only the tails are trimmed.
- Interval: applies to the whole fitted sample (n after trim), Dec 2020 snapshot.
- Source: Exchange 1.


## Exchange 2 — Structural Assumption

**Question (expert_question_2.md):** When you price a used boat, does its asking price come mainly from its size, its age, which part of the world it's listed in, and its make/model — combining roughly independently — or do these factors tangle together in a way (e.g. big boats worth far more, or some regions only holding certain models) that can't be separated?

**Reply (expert_reply_2.json):** The factors tangle together, and the tangling is the main thing to worry about.
- Size and age are the dominant, roughly separable drivers — a bigger, newer boat is worth more, and those two effects are largely independent of each other.
- Make/model is also strong but is not independent of size: a builder's reputation and price premium are attached to specific models, which have specific lengths, so "make premium" and "length" partly measure the same thing.
- Region is the most entangled. Regions do not hold a random sample of boats: the Caribbean and certain US regions skew toward larger charter-derived and bluewater boats, Europe toward smaller and a different mix of builders, and some makes/models appear almost exclusively in one region. So a raw regional price gap partly reflects a different boat mix, not a regional market premium. To isolate a true regional effect you must compare like with like — same make/model, similar size and age — otherwise the region coefficient absorbs the composition difference.

**How it shaped the work:**
- Structural assumption adopted: price is **additive on the log scale** (a hedonic / log-linear model), i.e.
  `ln Price = f(size) + g(age) + h(make/variant) + R(region) + ε`,
  but with two caveats the expert flagged:
  1. **make/variant premium is partially collinear with length** — so the model carries *variant* (make+model) as the identity term and length *inside* that, rather than a separate global "make premium" on top of a global length term; a variant's level already embeds its builder premium. Where a variant is rare, length and age supply the smoothing.
  2. **region must be estimated like-with-like.** The regional coefficient is the *within-composition* effect: it is estimated from the same hedonic regression that also controls for variant (identity), length and age, so the region effect is the residual market premium after composition is held constant — not the raw regional price gap. This is the crux of subtask 2 (is the region effect consistent across variants) and subtask 3 (the Hong Kong effect).
- Method consequence: a single pooled regression with **region dummies + variant (or make+length) + length + age** gives a composition-adjusted regional effect; a raw between-region mean comparison is reported only for contrast and is *not* the estimated regional effect.
- Interval / scope: holds across the Dec-2020 listing sample, both monohull and catamaran sheets, all three regions; the composition-mix caveat is strongest for Caribbean and US (larger, charter/bluewater mix) vs Europe (smaller mix).
- Source: Exchange 2.

## Exchange 3 — Interpretation Context / Decision Threshold

**Question (expert_question_3.md):** For a specific make/model, how far off an estimated asking price is before a broker would stop trusting it for a real deal — and does that tolerance differ between a common model with many listings and a rare one with only a few?

**Reply (expert_reply_3.json):** A broker typically wants an estimate within roughly ±10% to be useful for a real deal; beyond about ±15–20% they will not trust it and will fall back on their own comparables. That is an empirical judgment, not a fixed rule. The tolerance is not the same for common and rare models. A model with many listings (dozens) supports a tight estimate — often within ±5–10% — because the comparables are dense and the model's price level is well pinned down. A rare model with only a few listings gives a much wider interval, easily ±20–30% or more, because the estimate leans on the general size/age/region relationship rather than on that model's own sales. So the precision is model-specific: report a per-model interval, and expect the rare models to be the ones the broker cannot rely on.

**How it shaped the work:**
- **Decision-relevant threshold adopted:** a per-variant (make/model) price estimate is "broker-reliable" when its 95% prediction half-width ≤ ~10% of the estimate (usable band); estimates in the 10–20% band are "marginal"; >20% are "not broker-reliable — fall back to comparables." These are reported as the per-model precision tiers (subtask 1, "precision of your estimate for each variant").
- **Per-variant intervals:** the model reports, for each variant, its listing count `n`, the model's point estimate, and the 95% prediction interval (or an effective half-width derived from the regression residual + the variance of the mean prediction). Variants are then tiered common (n large, tight) / rare (n small, wide) consistent with the expert's common-vs-rare distinction. The interval widens as `n` shrinks, matching the expert's guidance that rare models borrow from the global size/age/relationship.
- **Interval:** the ±10%/±20% decision thresholds are broker practice values (source: Exchange 3), applied to the per-variant 95% prediction intervals computed from the Dec-2020 hedonic fit.
- **Source:** Exchange 3.
