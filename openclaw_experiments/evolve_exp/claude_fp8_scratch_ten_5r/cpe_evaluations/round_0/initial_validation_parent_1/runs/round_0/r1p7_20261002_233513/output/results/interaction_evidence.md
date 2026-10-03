# Expert Interaction Evidence — 2023_Y (MM-Bench)

Ten exchanges, one question each. Questions in `logs/operator_feedback/expert_question_N.md`,
replies in `logs/operator_feedback/expert_reply_N.json`, run logs in `logs/exchange_N.log`.

For each exchange: question, reply (summarized verbatim-in-substance), and how the reply
entered the model as a calibrated parameter, constraint, or decision rule.

## Exchange 1 — catamaran vs monohull premium

**Q:** For a used 45-foot luxury sailing yacht, do buyers pay more for a catamaran or a monohull? About how much more?

**Reply (substance):** Catamaran, typically 20–40% more than a comparable monohull of the same length and year, often more at the upper end. 45 ft cats commonly $400k–$700k vs monohulls $250k–$500k. Premium not uniform across makes; length-for-length can overstate it (more volume per foot).

**Entered work as:** calibration target `cat_premium ≈ +20%…+40%` (midpoint +30%, interval [+20%, +40%]).
Applied in `model.py` as a prior for the `catamaran` main effect: the fitted catamaran
coefficient (multiplicative, log-price model) must land inside [1.20, 1.45] to be accepted;
if it does not, the estimate is reported with the expert band noted (see results). It also
constrains the HK cat-vs-mono premium comparison in subtask 3.

## Exchange 2 — which region is cheapest

**Q:** In the data, the same make and model often lists at very different prices in different regions. From your buying experience, which region — Caribbean, Europe, or USA — has the lowest prices for used boats?

**Reply (substance):** Caribbean lowest, roughly 10–25% below comparable USA listings; Europe between or close to USA. Discount not uniform; smallest for blue-water cats and heavy-displacement monohulls (local/charter demand).

**Entered work as:** constraint on regional ordering `Caribbean < {Europe, USA}` and
`Caribbean/USA ratio ∈ [0.75, 0.90]` (i.e. −10%…−25%). Used as a validity check on the fitted
region coefficients (subtask 2); the fitted ratio is reported against this band. It also sets
the sign/direction prior for the HK effect in subtask 3 (HK is not "thin-market cheap" but
"thin-market expensive").

## Exchange 3 — annual depreciation

**Q:** In the listings, the same model can be from different years. Roughly how much does a used sailboat's price fall per year of age?

**Reply (substance):** Roughly 5–10%/yr typical; not linear — steepest in first ~5–10 years (10–15%/yr off new), flattening to ~3–6%/yr for 15–30-year-old boats; catamarans depreciate a bit more slowly in % terms.

**Entered work as:** age-decay prior `λ ∈ [3%, 15%]/yr` with the piecewise shape (steeper young,
flatter old) motivating a non-linear age term. In `model.py` the age effect is modeled in the
log-price model as `−λ·age` plus an optional age² term; the fitted λ is checked against
[0.03, 0.15] and the sign of the quadratic against "flattening". Reported as interval
[3, 15] %/yr, source: exchange 3.

## Exchange 4 — length premium

**Q:** Between a 40-foot and a 50-foot boat of the same year, roughly how much does the price grow per extra foot of length?

**Reply (substance):** ~10–20% more per extra foot; a 50-ft lists for roughly 2.5–4× a 40-ft of same year/type. Not linear — steepens at the larger end (volume ~ L³). Cats carry a steeper length premium.

**Entered work as:** length-effect prior `exp(β_L)·per-foot ∈ [1.10, 1.20]` and
`P(50)/P(40) ∈ [2.5, 4.0]` (same year/type). In `model.py` the length term is `γ·L` (plus an
optional `γ₂·L²` to capture the steepening); fitted per-foot factor checked against [1.10, 1.20],
and the fitted 50/40 ratio checked against [2.5, 4.0]. Interval [1.10, 1.20] per foot,
source: exchange 4.

## Exchange 5 — make/brand spread

**Q:** Two identical-year, same-length boats from different makes can differ a lot in price. How wide are typical price gaps between well-known makes and lesser-known ones?

**Reply (substance):** Well-known makes list 30–60% above lesser-known ones at same year/length; can exceed 2× at extremes (blue-water brands vs obscure/mass builders). Widest for older boats, narrowest for near-new.

**Entered work as:** brand-effect prior: ratio of top-quartile to bottom-quartile make effects
≈ [1.3, 1.6], up to 2× at extremes. Used to (a) justify keeping `Make` in the model rather than
dropping it, and (b) set the regularization strength on make random effects (see model below)
so that small-sample makes shrink toward the brand-level mean rather than overfitting. Source:
exchange 5.

## Exchange 6 — listing vs actual sale

**Q:** Do used-boat listing prices usually sit above the price the boat actually sells for? If so, by roughly how much?

**Reply (substance):** Yes; final sale typically ~5–15% below asking, rule of thumb ~10%. Wider for stale listings, overpriced/lesser-known makes, thin markets (Caribbean); narrower (near zero) for well-priced popular models. Asking prices = upper bound on transaction value.

**Entered work as:** interpretive parameter `ask−sale ≈ +5%…+15%` (midpoint +10%). The model
predicts *asking* (listing) price, so every price estimate is an upper bound on transaction
value; the precision discussion (subtask 1) states estimates as listing-price confidence
intervals and notes that the realized-sale interval would sit ~5–15% lower. Source: exchange 6.

## Exchange 7 — Hong Kong market

**Q:** Compared with USA or Europe, what is the used sailboat market like in Hong Kong — and do boats there usually list higher or lower than the same boat would in the USA?

**Reply (substance):** Small, thin, high-cost market; far fewer listings; wealthy local/expat buyers; scarce/expensive berthing (Aberdeen, Discovery Bay, Sai Kung). HK boats list ~10–30% higher than the same boat in the USA, sometimes more. Drivers: limited supply, import duties/shipping, expensive moorage, less price-sensitive buyers. Premium largest for popular cruising cats and well-known blue-water monohulls; can be offset if boat already in-region.

**Entered work as:** HK premium prior `HK/USA ∈ [1.10, 1.30]` for the subtask-3 effect, with a
qualitative note that the premium is *larger for catamarans than monohulls* (drives the
"same effect for both types?" answer). The subtask-3 model estimates the HK regional effect as
a multiplicative coefficient and compares it against [1.10, 1.30] (monohull baseline) and a
wider band for cats. Source: exchange 7.

## Exchange 8 — data quality / variant strings

**Q:** In broker listings like this one, how common are errors such as wrong model names, or prices that are just round placeholder numbers?

**Reply (substance):** Fairly common. Variant strings inconsistent (e.g. "Beneteau Oceanis 45" vs "Oceanis 45" vs "45"), misspelled, conflated — roughly 5–15% of rows need normalization before make/variant grouping is reliable. Round placeholder prices also common but NOT necessarily errors (sellers genuinely ask round numbers) — treat as a quality flag, not auto-delete.

**Entered work as:** (a) variant-normalization pass in `clean.py` (strip make prefix if present,
whitespace/NFKC) before grouping; (b) a `round_price` flag (price % 10000 == 0 or % 100000 == 0)
computed but NOT used to delete rows — only used to report sensitivity. The 5–15% figure is
recorded as the expected normalization burden; actual number of variant strings changed by
normalization is reported. Source: exchange 8.

## Exchange 9 — December seasonality

**Q:** The data covers only December 2020 listings. Do used-boat listings and prices in late winter differ much from those in summer months?

**Reply (substance):** Yes but modest. Listing volume swings more than price; N-Hemisphere inventory peaks spring (Mar–May), thins late fall/winter, so December under-represents the annual pool. Asking prices move only a few % to ~10%. Caribbean peaks in late fall/winter (cruising season), so December is active there. 2020 distorted by COVID. Treat December snapshot as broadly representative of level, mild downward inventory bias, small uncertain price effect.

**Entered work as:** representativeness constraint — the December 2020 snapshot is treated as
broadly representative of the price *level*, with a noted mild downward bias in inventory (fewer
rows than an annual snapshot) and a small, unmodeled price effect (few–10%). This justifies
modeling levels rather than time-indexed prices, and is stated as a limitation. Source:
exchange 9.

## Exchange 10 — what brokers anchor on

**Q:** When pricing a used boat for sale, do brokers rely mainly on recent comparable sales, on age and size, or on brand reputation? Which matters most?

**Reply (substance):** Primarily recent comparable sales (same make, model, year, region) — the anchor; age and size are the main objective adjustment factors; brand reputation is a secondary modifier that widens/narrows the comp range. In thin markets (HK, Caribbean) comps are scarce, so brokers lean more on age/size/brand heuristics and condition.

**Entered work as:** modeling-structure decision — the model is built as a **comparables-based**
model anchored on (make, variant, year, region) with explicit adjustment terms for age and size,
rather than a top-down regression from scratch. This is the "comps + adjusters" structure. It also
motivates the precision discussion: for a variant with few comps, the estimate leans on the
age/size/brand adjusters and is less precise. Source: exchange 10.
