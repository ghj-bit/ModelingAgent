# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — Problem 2023_Y (used-sailboat pricing)

Ten exchanges, one question each, strictly sequential. Each reply was turned into
a model parameter, constraint, equation, or decision rule before the next
exchange. The strategy followed "structural anchoring before numerical filling":
mechanism first, then its constraint, then the governing magnitude, then edges.

| # | Question (≤20 words) | Expert reply (summary) | How it changed the work |
|---|---|---|---|
| 1 | What mainly sets the listing price of a used sailboat: its make and model, or its size and age? | Size (length) and age dominate; price rises steeply (~exponential) with length, falls steadily with age. Make/model are a secondary modifier (tens of %), partly confounded with size. | Set the dominant mechanism. Chose a log-linear price surface with `length` and `age` as the primary predictors and `make` as a secondary effect. This is the skeleton of `model.py`. |
| 2 | Do catamarans and monohulls of the same size and age follow the same price curve? | No. Catamarans carry a substantial premium over monohulls at the same length/age (tens of %, more at larger sizes), with different depreciation and steeper length response. | Added `is_cat` main effect and a `cat_len` interaction to let the premium depend on size. Model estimate: premium ≈ +22.5% at 40 ft, +42.5% at 50 ft — matching "more at larger sizes". |
| 3 | Why would the same boat list at different prices in Europe, the USA, and the Caribbean? | Market size/demand, currency & tax (VAT), shipping/delivery cost capitalized into price, condition/use history (ex-charter wear), brokerage norms, local supply. Effects real but secondary, not uniform across variants. | Justified including `region` dummies in the price surface and motivated testing whether the regional effect is consistent across variants (sub-task 2). |
| 4 | How much below its asking price does a used sailboat usually sell? | Roughly 5–15% below asking; ~10% central. Larger for stale/overpriced/soft-market boats. | Calibrated the listing-vs-sale gap. Used as a precision/uncertainty statement: a listing price is a mark, expected ~10% above the eventual sale (exch 4), so point predictions carry that additional market-liquidity band. |
| 5 | Does a sailboat's value drop evenly every year, or mainly in its first years? | Front-loaded: steepest drop in the first few years, then flattens; closer to exponential decay than linear, with a residual floor. | Added a quadratic `age²` term so depreciation is convex (steeper early). Model: −6.7%/yr at age 5 → −4.4%/yr at age 12, i.e. the rate declines with age, as described. |
| 6 | Do buyers pay much more for a brand-name boat than a lesser-known one? | Yes, but modestly: ~10–30% premium for a respected brand at the same size/age; larger for quality/bluewater/resale-demand brands. Brand is a secondary modifier. | Kept `make` effects in the model but treated them as secondary (secondary to size/age), consistent with exch 1 and 6. |
| 7 | What kind of listing prices in a boat sheet look clearly wrong or unrealistic? | Implausibly low (a seaworthy 36–56 ft boat lists well above ~$10k), implausibly high / orders of magnitude off the make-variant-year cluster, unit/currency errors, placeholders, internal inconsistency. Reliable test: compare within make/variant/year & length. | Drove the cleaning in `clean_data.py`: removed exact duplicates, applied a $10k absolute floor, and a cluster test dropping values >3× or <0.33× the make/variant/year median. Documented in the cleaning report. |
| 8 | Compared to Europe or the USA, is a used sailboat in Hong Kong usually pricier or cheaper? | Cheaper, generally. Thin market, few berths, often older/ex-charter boats; comparable boats list below Europe/USA, order of 10–30% lower (empirical, not precise). Offsets (scarce berths, duties, small local supply) can push specific well-kept boats to/above Western levels. | Set the Hong Kong regional effect as a calibrated prior: central factor 0.80 (−20%), sensitivity band 0.70–0.90 (−30% to −10%). Applied to the European-baseline predictions in `hk.py`. |
| 9 | Is a catamaran's price premium over a monohull similar across all boat sizes? | No — it widens with length. Modest (tens of %) at 36–40 ft, typically larger at 50–56 ft (more living/charter space, scarcer supply). Curves diverge with length. | Confirmed the need for the `cat_len` interaction rather than a constant catamaran premium; validated the model's size-dependent premium (exch 2 + 9 jointly). |
| 10 | Which boat features make a used boat sell at a higher price than its similar neighbors? | Condition/maintenance & recent refit, low engine hours (private vs ex-charter), equipment/upgrades (electronics, AC, watermaker), layout/berths, documentation (clear title, EU VAT-paid), location/berth, brand desirability, rarity. Secondary to size/age but can move price by tens of %. | Defined the residual (unexplained) drivers and bounded the model's error: these omitted, boat-specific features are the main source of the ~24% out-of-sample prediction error, and explain why the same make/variant/year/length cluster still spreads over tens of percent. |

## Provenance of every empirical number
- Listing-vs-sale discount ≈ 10% (range 5–15%): exchange 4.
- Brand premium ≈ 10–30%: exchange 6.
- Catamaran-over-monohull premium, widening with size: exchanges 2 & 9.
- Front-loaded (convex) depreciation: exchange 5.
- HK ≈ 10–30% below Europe/USA, central −20%: exchange 8.
- Cleaning thresholds ($10k floor; 3× / 0.33× cluster rule): exchange 7.
- All price, length, year, region, make, hull figures: the task's own dataset
  (`2023_MCM_Problem_Y_Boats.xlsx`), after cleaning.
- Search for HK comparable listings (`code/search.py`, logs `search_hk*.log`):
  returned no usable HK price data (Chinese dictionary / machinery noise), so the
  HK effect rests on the exchange-8 calibrated prior, not on a retrieved listing.
