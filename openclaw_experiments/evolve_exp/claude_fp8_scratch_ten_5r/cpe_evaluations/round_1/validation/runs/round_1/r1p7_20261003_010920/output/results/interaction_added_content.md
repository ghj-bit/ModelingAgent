# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction evidence — 2023_Y sailboat pricing (10 exchanges)

Consultation log: question, reply, and the concrete work each reply drove.
Files: `logs/operator_feedback/expert_question_N.md`, `expert_request_N.json`, `expert_reply_N.json`.

## Exchange 1 — time on market
- **Q:** For a 40-foot cruising sailboat listed in December, about how many weeks or months does it usually take to sell?
- **Reply (values):** 3–9 months on market, central 4–6 months (~15–25 weeks); well-priced popular models 1–3 months; overpriced/niche/off-season 6–12+ months; December listings face slower northern-hemisphere winter demand.
- **Work it drove:** Established that the data are *asking* prices at one moment (Dec 2020), not transactions. Used as a constraint in the model's validity discussion: listing prices of slow-moving boats carry a motivated-seller discount, which is one contributor to the model's residual variance (sigma_log = 0.316). Recorded in the Task 1 outcome as a source of bias (asking ≠ clearing price).

## Exchange 2 — negotiated discount
- **Q:** For the same 40-footer, is the final sale price usually higher or lower than the asking price, and by roughly how much?
- **Reply (values):** Usually lower; typical negotiated discount ~5–15% off asking, central ~10%; 0–5% for in-demand production boats, 15–25%+ for overpriced/long-listed boats; December favors buyers.
- **Work it drove:** Parameter `NEGOTIATE_MARGIN = 0.10` (interval [0.05, 0.15]) in the code (`hk_model` in `code/model.py`), used to convert the model's predicted asking price into an expected *sale* price for the broker. Sensitivity of the HK sale estimate to this margin is reported in Task 3.

## Exchange 3 — listing strategy
- **Q:** In the boat trade, is asking price usually set with room left to negotiate, or close to the seller's true price?
- **Reply (values):** Asking is set with deliberate negotiation room (a margin above the seller's floor); brokers list above the seller's acceptance level; for in-demand production models the margin is small.
- **Work it drove:** Justification for treating `Listing Price (USD)` as the modeling target (the observable the broker controls) rather than imputing an unobserved reservation price. Feeds the Task 1 discussion: the model's error is relative to asking prices, which is the right target for a broker pricing inventory.

## Exchange 4 — condition premium
- **Q:** Among used 40-footers, do well-maintained boats command noticeably higher prices than the same model in tired condition?
- **Reply (values):** Yes — condition often outweighs year or region for the same model; a well-maintained survey-clean boat lists ~15–30% more than a tired example of the same make/variant/year; >40% gap when major items (sails, rigging, engine, osmosis repair) are needed; spread widest for 20+ year boats.
- **Work it drove:** Condition is unobserved in the dataset. The reply bounds what the unexplained variance must contain: at minimum a 15–30% condition spread for identical model/year, i.e. at least ~0.14–0.26 log units of spread, versus the model's sigma_log of 0.316 — so the residual is consistent with mostly condition. Recorded in the precision discussion (Task 1) as the dominant limitation: per-variant prediction intervals of ±20–30% are expected *even for a perfect model of the observed variables*.

## Exchange 5 — catamaran premium
- **Q:** Do catamarans of the same length usually list for more than monohulls, and about how much?
- **Reply (values):** Yes, substantially; typical catamaran premium ~30–60% over a monohull of comparable length and age, >100% for popular cruising cats vs budget monohulls; largest in the 40–50 ft range; narrows at 36–38 ft.
- **Work it drove:** Prior/expectation against which the fitted hull effect is checked. Model: `Cat` coefficient +0.4074 log (t=3.17) = ~+50% holding length and age fixed — inside the expert's 30–60% band; `Length:Cat` +0.0084 (t=3.02) means the premium grows with size, consistent with the 40–50 ft emphasis. Task 2/4 report the agreement.

## Exchange 6 — depreciation rate
- **Q:** How quickly do 15-year-old sailboats usually lose value each year, as a rough share of their value?
- **Reply (values):** ~3–6% of current value per year at the 15-year mark, central 4–5%; depreciation is non-linear (steepest when new at 10–15%/yr, flattening with age); well-maintained popular models 2–4%/yr, neglected/discontinued 6–10%/yr.
- **Work it drove:** The age term in the log-linear model is a *per-year multiplicative* depreciation: model's base `Age` coefficient −0.0417 = −4.0%/yr, right at the expert's central estimate; region-specific age effects (USA −0.0153, Europe −0.0119 extra) and the catamaran age interaction (−0.0014, n.s.) are tested against this. The model's 4%/yr is used as the validated anchor for depreciation in Task 4.

## Exchange 7 — cross-country price variation
- **Q:** How much does a boat's listing price usually change when it moves from one country to another?
- **Reply (values):** No fixed rule; small and region-specific, typically ±5–15% and often indistinguishable from noise once make/variant/year/condition are controlled; where it matters: tax/duty regimes (EU VAT-paid vs non-VAT-paid ~10–20%), local demand, currency, import costs; within-region variation often exceeds between-country variation.
- **Work it drove:** (a) Justifies the `Country_EU_VAT` dummy (DE, FR, NL, BE, ES, IT, PT, GR, DK, SE, FI) as the only country-level structural term, as a proxy for VAT-paid status rather than a full country effect set (collinearity + expert's "country is a weak predictor" guidance). Fitted +0.1282 log (t=9.47) = ~14% VAT-paid premium, inside the expert's 10–20% VAT band. (b) Informs the practical-significance test in Task 2 (region effects measured after controlling for model, size, age, hull, and VAT status).

## Exchange 8 — how China brokers price foreign boats
- **Q:** What do brokers in China mostly use as a baseline when pricing a foreign-built used sailboat?
- **Reply (values):** The overseas asking price of the same make/variant/year (USA/Europe/Caribbean comparables) is the anchor; adjustments layered on: import duty and VAT/tax status, shipping/import cost, thin local supply, currency.
- **Work it drove:** Defines the Task 3 methodology: Hong Kong price = (model-predicted foreign asking price for the comparable) × (1 + HK regional premium), then × (1 − negotiation margin) for the expected sale price. The subset construction (boats with ≥3 cross-regional listings, 40–52 ft, age 5–25) targets exactly the comparables the expert says Chinese brokers anchor on.

## Exchange 9 — HK landed-price level
- **Q:** After importing duties and shipping, do used sailboats in Hong Kong usually list higher or lower than identical foreign boats?
- **Reply (values):** Higher, noticeably; commonly ~20–50% above the equivalent foreign asking price, sometimes more for larger/valuable boats; premium smaller for already-landed/duty-paid boats, can vanish for niche/older boats with weak local demand.
- **Work it drove:** Parameter `HK_PREMIUM = 0.35` (interval [0.20, 0.50]) in `code/model.py` `hk_model`. Applied to the 539-boat-type informative subset: predicted HK asking premium +35% over the foreign comparable median; after the 10% negotiation margin, expected HK *sale* price ≈ +21.5% over the foreign asking price. Sensitivity of both hull classes to the premium range [0.20, 0.50] is reported in Task 3.

## Exchange 10 — seasonality
- **Q:** In your region, do December boat listings tend to be priced lower than listings in the spring?
- **Reply (values):** Yes in northern-hemisphere regions (USA, Europe); December listings are a few percent to ~10% lower for the same boat, driven by weak winter demand and motivated sellers; much weaker or absent in warm markets (Caribbean, Florida, HK).
- **Work it drove:** All 3,491 records are December 2020 listings, so the December effect is absorbed in the level (unidentifiable) — recorded as a limitation in Task 4. But the *warm-market qualifier* gives a testable prediction: the December discount should be smaller in the Caribbean and Florida than in Europe. The model's region effects (USA +52%, Europe +12% vs Caribbean) are consistent with demand-side differences; the residual means by region (Caribbean mono +0.028, USA −0.051, Europe +0.019 log units for 36–41 ft) are used in Task 2 as a consistency check, and the December caveat is included in the broker report (Task 3): HK, a warm market, should show little seasonal softening, supporting year-round listing in HK.

## Parameter table built from exchanges (used in the model)

| name | value | interval | source |
|---|---|---|---|
| NEGOTIATE_MARGIN (asking→sale discount) | 0.10 | [0.05, 0.15] | expert exchange 2 (confirmed by exchange 3) |
| HK_PREMIUM (HK asking over foreign asking) | 0.35 | [0.20, 0.50] | expert exchange 9 |
| depreciation rate sanity anchor (per yr, multiplicative) | 4.0% | [3%, 6%] at 15 yr age | expert exchange 6; model fits −4.17%/yr |
| catamaran premium sanity band | +50% (fitted +40.7 log pts) | [30%, 60%] | expert exchange 5; model fits 0.4074 log (t=3.17) |
| EU VAT-paid premium | +12.8% (fitted) | [10%, 20%] | expert exchange 7; model fits 0.1282 log (t=9.47) |
| time on market (context) | 4–6 months | [3, 9] | expert exchange 1 |
| condition spread for same model/year (unobserved, limitation) | 15–30% | [15%, 40%+ with major repairs] | expert exchange 4 |
| seasonal (December) discount in northern regions | 2–10% | — (absorbed in level; unidentifiable from single-month data) | expert exchange 10 |

External data: none successfully retrieved in this environment. A staged search (`code/search.py`) for the EUR/USD rate of Dec 2020 returned no readable value (FRED/ECB/XE endpoints 403/404/timeouts; open.er-api.com gives only current rates, not history). The model therefore uses a *currency-free* formulation: all prices are already USD listing prices, so FX cancels in the USD regression, and the EU-VAT term (fit on the data, validated against exchange 7) is used instead of an FX dummy. The HK premium from exchange 9 is already net of landed costs (duty, shipping, tax) per the expert's framing.
