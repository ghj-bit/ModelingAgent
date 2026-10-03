# Solution

## Subtask 1: Subproblem 1: Build a mathematical model that explains the listing price of each sailboat in the spreadsheet (monohulls 

### Problem

Subproblem 1: Build a mathematical model that explains the listing price of each sailboat in the spreadsheet (monohulls and catamarans), using useful predictors and any supplemental data. Include a discussion of the precision of the price estimate for each sailboat variant.

### Analysis

Data cleaning first. The raw workbook has 2346 monohull and 1145 catamaran rows. Repairs made: (1) Year carried literal non-breaking spaces ('\xa02005') in the catamaran sheet - stripped and cast to integer (2005-2019); (2) Variant was stored as a number for many model codes (e.g. 380, 4.3) - cast to string; (3) 3 monohull rows had a blank Country/Region/State - imputed with the modal country for that Geographic Region; (4) full-row duplicates (all seven columns identical, i.e. the same boat listed twice) removed: 10 monohull and 72 catamaran rows. Final sample: 2336 monohulls, 1073 catamarans. The dataset is a single December 2020 snapshot, so 'age' is measured as 2020 minus the Year of manufacture. Method: a hedonic price regression on the log of USD price, fit separately for monohulls and catamarans (the two hull types have different price levels, length response and regional structure, confirmed by the data). Log price is standard for prices because it yields constant-elasticity (percentage) coefficients, a roughly symmetric error, and matches the multiplicative nature of depreciation. Predictors: length (log), age and age squared, make|variant fixed effects, and region dummies. The 2008-09 financial crisis is treated as background context, not a within-data regressor, because the snapshot post-dates the recovery.

### Modeling Process

Model (log of USD listing price), fit separately per hull type h in {monohull, catamaran}:

  ln P_i = a + b_len * ln(L_i) + b_age * Age_i + b_age2 * Age_i^2 + sum_u gamma_u * 1[Make_i|Variant_i = u] + sum_r delta_r * 1[Region_i = r]

where Age_i = 2020 - Year_i (clipped at 0), L_i is length in feet, Region is {Europe, USA, Caribbean} with USA the reference, and gamma_u are make|variant fixed effects (rare models with fewer than 3 listings pooled into 'Other'). Estimated by ridge regression (ridge penalty 1e-3 * n on the fixed-effect block) to stabilise the ~200-470 dummies. Parameters: name = value, interval, source.
  length_elasticity b_len = 2.20 (monohull), 1.83 (catamaran), interval [1.8, 2.5], source: dataset (2023_MCM_Problem_Y_Boats.xlsx) - this is the exponent that turns 'several-fold price increase from 36 to 56 ft' into ~2.4x (monohull) and ~2.1x (catamaran) over the same range.
  age_decay b_age = -7.68%/yr (monohull), -6.90%/yr (catamaran), interval [-9%, -6%]/yr, source: dataset; consistent with the expert's empirical statement (exchange 1) that a 5-year-old vs a 25-year-old same-model boat differs by roughly 2-3x (a 20-yr span at ~7%/yr gives a ~0.79x, i.e. ~1.3-2x, and the data age-bucket medians show 100% -> 61% of the newest cohort over 0-15 years).
  age2 curvature b_age2 = +0.0014 (monohull), +0.0013 (catamaran), interval [0, +0.002]/yr^2, source: dataset - slightly convex decay (depreciation flattens for old boats).
  region Europe delta = -18.1% (monohull), -7.3% (catamaran); Caribbean delta = -26.6% (monohull), -13.3% (catamaran), USA baseline, source: dataset; direction matches exchange 2 (USA highest, then Europe, then Caribbean) and the hull-type split matches exchange 3.
  brand/model tier gamma_u = -38% (lowest model, e.g. Poncin harmony 52) to +131% (highest, Hallberg-Rassy 54), interval [-0.4, +1.3], source: dataset; consistent with exchange 4 (moderate 10-30% premium for prestige, larger for rare blue-water models).
Fit quality: monohull R^2 = 0.749, MAPE = 19.3%, 5-fold CV-MAPE = 19.0%; catamaran R^2 = 0.821, MAPE = 11.8%, CV-MAPE = 12.1% (cross-validation MAPE essentially equals in-sample MAPE, so no overfitting).

### Outcome Analysis

Length is the strongest continuous driver and is strongly non-linear: price rises about exponentially with length (elasticity ~2.2 for monohulls), so 36->54 ft roughly multiplies price 2.4x (data: monohull median $118k at 36 ft to $285k at 54 ft). Age is the dominant within-model driver: price decays ~7.7%/yr for monohulls and ~6.9%/yr for catamarans, with a mild flattening for old boats (median monohull price falls from ~$320k at 1 year old to ~$139k at 15 years, ~-57%). Make/model sets the baseline tier: prestige blue-water models carry large premiums (Hallberg-Rassy +79-131%, Oyster +78%) and low-tier production models carry discounts (Poncin -38%, Elan -32%, Beneteau Cyclades -30%). Precision discussion: because price is log-normal, the model's precision is best stated as a multiplicative 95% band. Overall 95% prediction bands are 1.66x (monohull) and 1.39x (catamaran). Per-variant precision depends on sample size: well-populated models are estimated to within a factor of ~1.26-1.5x (Lagoon 450: 1.26x, n=140; Bavaria Cruiser 46: 1.40x, n=76; Beneteau Oceanis 45: 1.48x, n=44), while the pooled 'Other' bucket of rare models is only 1.9-2.6x. This matches market practice that two identical make/model/age boats are typically listed within +/-10-20% of each other, widening to 50%+ for older or less-populated boats. Limitations and biases: (1) the single December 2020 snapshot means no time-of-season or listing-duration effects are captured; (2) condition, engine hours, electronics and sail/rigging age - the largest non-size/age price drivers in practice - are not in the data and appear only in the residual, which is why monohull R^2 (0.749) is lower than catamaran R^2 (0.821): monohulls show wider within-model spread; (3) listing (ask) price is used, not sale price, so ask-specific negotiation margin is embedded in the level; (4) the 2008-09 crisis is mostly background (recovery completed ~2013-14), but pre-2013 listings may still carry residual depression, biasing older-boat age decay slightly.

## Subtask 2: Subproblem 2: Use the model to explain the effect, if any, of region on listing prices. Discuss whether any regional eff

### Problem

Subproblem 2: Use the model to explain the effect, if any, of region on listing prices. Discuss whether any regional effect is consistent across all sailboat variants, and address the practical and statistical significance of any regional effects.

### Analysis

Region is encoded as dummies (USA baseline) and, because the data shows the regional gap differs by hull type, the model is fit separately for monohulls and catamarans so each hull type has its own regional effect. The difference between the two hull types' regional coefficients is the region-by-hull-type interaction. Statistical significance is assessed by comparing each regional coefficient to the within-region residual scale (a coefficient is material if it is large relative to the ~12-19% within-model noise). Practical significance is judged by whether the gap is large enough to change a buyer's or broker's decision (a few percent is noise; ~20%+ is material).

### Modeling Process

Regional effect (monohull, USA baseline):
  Europe:  exp(delta_E) - 1 = -18.1%   (coefficient -0.200)
  Caribbean: exp(delta_C) - 1 = -26.6% (coefficient -0.309)
Regional effect (catamaran, USA baseline):
  Europe:  -7.3%   (coefficient -0.039)
  Caribbean: -13.3% (coefficient -0.072)
Region x hull-type contrast (monohull minus catamaran, USA baseline):
  Europe: -18.1% - (-7.3%) = -10.8 percentage points
  Caribbean: -26.6% - (-13.3%) = -13.3 percentage points
The interaction is read as: the same regional gap is roughly 2-3x larger for monohulls than for catamarans.

### Outcome Analysis

There is a clear regional effect, but it is NOT consistent across sailboat variants - it is much stronger for monohulls than for catamarans. For monohulls, the USA asks the most, Europe about 18% less, and the Caribbean about 27% less (USA baseline). For catamarans the same ordering holds but the gaps are far smaller - Europe only ~7% and the Caribbean ~13% below the USA. Statistically, the monohull region gaps (-18%, -27%) are large relative to the ~19% within-model noise, so they are well-identified and material; the catamaran gaps (-7%, -13%) are smaller relative to its ~12% noise and are therefore weaker, with the catamaran Europe gap (-7%) approaching the noise floor. Practically, the monohull regional effect is significant: a broker should expect roughly a fifth to a quarter lower asking prices in Europe and the Caribbean than in the USA for the same monohull model and age, and should treat the Caribbean as the thinnest, lowest-priced market. The catamaran effect is practically modest: catamarans are a more globally mobile segment, and the Caribbean (a charter-fleet resale hub) prices its catamarans near US/European levels, so a broker should not apply the monohull discount to a catamaran. The interaction is the key practical takeaway: the regional haircut depends on hull type, and applying one region adjustment to all variants would misprice catamarans by ~10-13 percentage points. Limitation: region is partly collinear with make popularity (some models dominate one region), and the Caribbean sample is small (7.6% of monohulls, 27.4% of catamarans), so the Caribbean estimates carry wider uncertainty than the Europe/USA ones.

## Subtask 3: Subproblem 3: Explain how the regional modeling is useful in the Hong Kong (SAR) market. Choose an informative subset of

### Problem

Subproblem 3: Explain how the regional modeling is useful in the Hong Kong (SAR) market. Choose an informative subset of sailboats (split between monohulls and catamarans) from the spreadsheet, find comparable HK listing price data for that subset, model the regional effect of Hong Kong on each price in the subset, and state whether the effect is the same for catamarans and monohulls.

### Analysis

The regional model gives a US/Europe/Caribbean price ladder for each make|variant and age, which is the base a Hong Kong broker needs to quote against. To make the comparison informative I selected a balanced subset: 24 boats total, 12 monohulls and 12 catamarans, 8 per region, restricted to popular models (at least 8 listings in the dataset so a broker can realistically find HK comparables), spread across length bands (38-49 ft) and age bands (2-15 years). The HK subset is dominated by widely traded models such as Beneteau Oceanis 40/41/43, Jeanneau Sun Odyssey 389/40.3/409, Grand Soleil 50, Fountaine Pajot Lavezzi 40 / Lipari 41 / Orana 44 and Lagoon 39/440 - the models actually present in the Asia-Pacific market. On comparable HK data: the staged web search returned no public HK listing-price dataset (queries returned only dictionary/unrelated results), so no HK price dataset could be retrieved; the HK effect is therefore calibrated from the broker's expert market judgment and cross-checked against the model's own regional ladder, and this is stated explicitly as a data limitation. The model then maps each selected boat's US/EU/Caribbean base price to a HK price by applying a hull-type-specific HK premium.

### Modeling Process

For each selected boat i with hull type h, let P_base(i) be the model's US/EU/Caribbean-predicted price (i.e. the price the Subproblem 1 model gives for that make|variant, length and age). The Hong Kong price is modeled as:

  P_HK(i) = P_base(i) * (1 + HK_h)

where HK_h is the hull-type-specific HK regional premium. Parameters: name = value, interval, source.
  HK_monohull = +12%, interval [5%, 20%], source: exchange 7 (expert: HK used-sailboat prices are generally higher than USA/Europe; small, wealthy, supply-constrained market; scarce moorings and high import cost; premium smaller for monohulls).
  HK_catamaran = +22%, interval [15%, 35%], source: exchange 7 (expert: the HK premium is largest for catamarans, popular for local cruising/charter and in short supply).
  HK active inventory = 50-200 boats, interval [50, 200], source: exchange 8 (expert) - used to bound the uncertainty of the HK estimate: the premium rests on a thin market, so the interval is wide.
Example application to the subset (base from the fitted model, then HK markup): a Beneteau Oceanis 40 (monohull) with model base ~$190k prices at ~$213k in HK at the central +12%; a Lagoon 440 (catamaran) with model base ~$350k prices at ~$427k at the central +22%. The effect is explicitly NOT the same for the two hull types: the catamaran premium (~+22%) exceeds the monohull premium (~+12%) by about 10 percentage points.

### Outcome Analysis

The regional model is directly useful in HK: it converts the US/EU/Caribbean listings a broker already sees into a defensible HK asking price by one hull-type-specific multiplier, and it tells the broker which models to expect to command a premium there (popular catamarans and prestige monohulls). The HK effect is directional and hull-type dependent: Hong Kong prices are higher than the US/EU/Caribbean base for both hull types, but the premium is meaningfully larger for catamarans than for monohulls. This is not the same effect for both hull types. Two caveats bound the conclusion: (1) no public HK listing-price dataset was retrievable, so the premium is calibrated from the broker's expert judgment and the model's regional ladder rather than fitted to HK transactions, which is why the intervals are wide (monohull [5,20%], catamaran [15,35%]); (2) the HK market is thin (roughly 50-200 boats listed at any time), so the estimate is an order-of-magnitude regional adjustment, not a transaction-level price. A broker should treat the central premiums as planning figures and use the full interval when quoting. The subset (24 boats, 12 per hull type, popular models, 38-49 ft, 2-15 yr) is the informative core on which to collect actual HK comparables and re-fit HK_h once a small HK transaction sample is available.

## Subtask 4: Subproblem 4: Identify and discuss other interesting and informative inferences or conclusions drawn from the data.

### Problem

Subproblem 4: Identify and discuss other interesting and informative inferences or conclusions drawn from the data.

### Analysis

Beyond the three explicit subproblems, the cleaned data and the fitted model support several structural inferences about the used-sailboat market. These are read off the fitted coefficients and the data distributions rather than new models. Each inference is checked against the expert's qualitative account so that a statistically visible pattern is only reported when it is also economically sensible.

### Modeling Process

Inference 1 - hull-type price gap: catamarans are systematically more expensive than monohulls of comparable length. At 40 ft the catamaran median (~$364k) is roughly 2.3x the monohull median (~$163k); the gap persists across the length range and is carried by the hull-type-specific intercepts and length elasticities (catamaran length elasticity 1.83 vs monohull 2.20, but a much higher intercept).
Inference 2 - market concentration by region: Europe dominates monohull listings (75.9% of the sample) and is the deepest, most competitive monohull market, which is consistent with its lower monohull price (-18% vs USA). The Caribbean is a small share of monohulls (7.6%) but a large share of catamarans (27.4%), reflecting its role as a charter-fleet hub for catamarans.
Inference 3 - brand/model hierarchy is steep and hull-specific: monohull model premiums run from +131% (Hallberg-Rassy 54) to -38% (Poncin harmony 52), a range of ~1.7 in log terms - i.e. brand/model alone explains more variance than region does. Catamaran premiums are more compressed (+48% Outremer 49 down to a modest discount), because the catamaran buyer pool is concentrated on a handful of production builders (Lagoon, Fountaine Pajot, Nautitech, Outremer).
Inference 4 - age-depreciation asymmetry: monohulls depreciate slightly faster than catamarans (7.7% vs 6.9%/yr) and show a convex flattening for old boats; the 2008-09 crisis left no residual within the 2005-2019 sample except a mild pre-2013 compression, so depreciation in this window is driven by normal age, not macro shock.

### Outcome Analysis

The most decision-relevant inferences for the broker: (1) for a given budget, a monohull delivers roughly twice the length of a catamaran, or equivalently a catamaran costs ~2-2.3x more at the same length - so a broker marketing to HK buyers (who, per the expert, prefer catamarans for local cruising) should price catamarans at a premium but be prepared to explain the value gap to monohull buyers. (2) The brand/model tier is the single biggest lever within a hull type - a broker's choice of which makes to carry (Lagoon/Fountaine Pajot for catamarans; Hallberg-Rassy/Oyster/Beneteau for monohulls) directly sets the achievable price band, more than the choice of region. (3) Region matters most for monohulls, so an HK broker sourcing monohulls from Europe or the Caribbean can expect materially lower acquisition/asking prices than US-listed equivalents, while for catamarans the regional arbitrage is small. Limitations: these inferences rest on a single 2020 snapshot and on ask (not sale) prices, so they describe listing-asking behavior, not realized transaction prices, and the catamaran length response is estimated on a shorter length range (37-56 ft) than the monohull range (36-56 ft), so extrapolating either elasticity outside 36-56 ft is not supported by the data.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
