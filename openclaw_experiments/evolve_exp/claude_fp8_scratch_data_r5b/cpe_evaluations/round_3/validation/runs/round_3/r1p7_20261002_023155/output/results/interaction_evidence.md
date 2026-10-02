# Expert Interaction Evidence — 2023_Y (used-sailboat listing price)

Three exchanges, one question each. Each reply is turned into a concrete
model input before the next exchange.

## Exchange 1 — dominant price driver (structural fit)

**Question (expert_question_1.md):** When you price an older sailboat, which
single thing dominates how much it is worth today: how long the boat is, how
old it is, or what brand and model it is?

**Reply (expert_reply_1.json):** Brand and model dominates; length and age are
secondary. A sailboat is not a commodity like a used car — value is set by the
specific design (make/variant sets hull design, build quality, reputation,
sailing characteristics, buyer-pool size). Two boats of identical length and
year can differ by a factor of two purely on make/model. Length is largely
already embedded in the model identity ("Beneteau Oceanis 46" is 46 ft); age
acts as a depreciation modifier on top of the model's baseline, not the primary
driver.

**How it changed the work (→ model):** The model uses make/variant as a large
fixed-effect vocabulary (467 monohull and 111 catamaran level effects) as the
primary predictor, with length and age as secondary continuous terms. Age is
entered as a depreciation modifier (`b1*age`) rather than a main driver, and a
`L^2*age` interaction lets depreciation differ with size. This is what gives
the model R²≈0.90 (mono) / 0.87 (cat).

## Exchange 2 — listing vs. sale price (bias mechanism)

**Question (expert_question_2.md):** When you price a used boat, does the
asking price usually land above, below, or at what it finally sells for?
Roughly how far off?

**Reply (expert_reply_2.json):** Asking price lands above the final sale price;
the listing is an opening position, not a transaction price. Final sale is
typically ~5–15% below asking, widening to 20%+ for boats that sit long or are
overpriced/niche/older; in a hot market sale can be within a few percent of
asking, occasionally at or slightly above.

**How it changed the work (→ model):** The outcome variable is *listing* price,
so the model is fitted to ask, not to sale. The 5–15% (up to 20%) ask/sale gap
is carried as a stated bias: model predictions are asking prices and are
therefore an upper bound on likely transaction value; the HK-market comparison
is made on the listing-price basis (like-for-like) and the 5–15% gap is
disclosed so a broker reading an HK "value" does not treat an ask as a sale
price.

## Exchange 3 — acceptable uncertainty band (interpretation criterion)

**Question (expert_question_3.md):** When a broker wants to estimate what a
boat is worth in a new market with few past sales there, how wide a band around
the estimate do you consider acceptable before you stop trusting it?

**Reply (expert_reply_3.json):** For few local comparables, an acceptable band
is roughly ±15–20% around the point estimate; inside that the estimate is
usable for a pricing conversation. Beyond ~±25–30% the estimate stops telling
the boat's worth and is a range only. Two conditions widen the band: a thin or
absent local market, and a boat that is old/rare/heavily customized; when both
hold the honest band can exceed ±30% and the estimate should be presented as a
range anchored to comparables, not a single number.

**How it changed the work (→ model/conclusions):** Per-variant precision is
reported as a prediction standard deviation and a 95% band; the model's
residual standard deviation in log-price is 0.162 (mono) / 0.146 (cat), i.e. a
typical 95% band of ≈ ±32%/±29% — wider than the ±15–20% comfort band, so the
conclusions are framed as *ranges* with the anchoring comparables named,
exactly the presentation the expert prescribes for a thin new market (HK). The
HK effect is therefore reported as a factor *range* (cat anchor 0.72–1.07×)
rather than a single point, and flagged as range-only per this criterion.
