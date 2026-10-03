# Expert Interaction Evidence — MM-Bench 2020_C

Policy followed: structural anchoring before numerical filling. Branch sequence:
mechanism (Q1) → constraint (Q2) → parameter (Q3, Q8) → edge cases (Q4, Q5, Q9, Q10) → context grounding (Q6, Q7). All questions were single, ≤20 words, common-sense, with no modelling terminology. All replies were converted into model parameters, decision rules, or analyses before the next exchange.

## Exchange 1 (structural: dominant mechanism)
**Q:** What matters most when a new product first appears: quality of earliest reviews, or how quickly ratings accumulate?
**A (gist):** Early review quality dominates; volume matters mostly indirectly (stability + popularity signal). First ~10–30 reviews carry outsized weight; after that the average is sticky.
**Work performed:**
- Parameter: early-reputation window K ∈ {10, 20, 30, 50} reviews (interval [10, 30] core).
- Computed `corr(first-30-review mean, full-lifetime mean)` per product: 0.996 (hair dryer), 0.998 (microwave), 1.000 (pacifier) — confirms stickiness; full-lifetime mean ≈ early mean (|diff| ≤ 0.04).
- Became the tracking-rule core: the displayed average is a valid quality proxy only once K reviews exist.

## Exchange 2 (constraint: what stops slide-back)
**Q:** A product's early reviews set a high average. What most prevents that reputation from sliding back down?
**A (gist):** Sustained inflow of new verified high-star reviews keeping pace with sales; consistent quality. Slide-back is caused by early hype vs. later experience mismatch; unverified/Vine-heavy early praise erodes.
**Work performed:**
- Constraint added to model: reputation is a flow, not a stock — protection = verified high-star inflow rate ≥ sales rate; unverified share is a decay term.
- Computed verified vs. unverified star means: hair dryer 4.18 vs. 3.71 (1-star 7.5% vs. 17.7%); microwave 4.03 vs. **2.22** (1-star 10.7% vs. **54.9%**); pacifier 4.41 vs. 4.25.
- The microwave unverified anomaly became an integrity constraint: unverified reviews must be tracked separately and excluded from quality signals.

## Exchange 3 (parameter: when sellers worry)
**Q:** When do sellers start worrying about a new product's ratings: at launch, or after some time? Roughly how long?
**A (gist):** After ~1–3 months or 10–30 reviews, whichever comes first; before that ratings are noise. Exception: competitive category → watch from day one.
**Work performed:**
- Calibration: monitoring window T_monitor ∈ [1, 3] months or [10, 30] reviews — matches exchange-1 K.
- Review-frequency data (reviews/product/month) shows all three categories are competitive and review-rich, so the "watch from day one" exception applies; the K threshold (not a clock) is the operative trigger in the model.

## Exchange 4 (edge case: burst on a strong product)
**Q:** If a few customers suddenly leave scathing reviews of a well-reviewed product, what does that burst usually mean?
**A (gist):** A real, shared defect or discrete event (bad batch, silent change, fulfillment, listing change), not random dissatisfaction. Burst = discrete event; gradual drift = quality decline.
**Work performed:**
- Decision rule added: 3+ one/two-star reviews within 60 days on a product whose cumulative mean ≥ 4.0 → classify as "incident", investigate; do NOT reclassify product reputation.
- Computed: share of 1–2-star reviews in such clusters: hair dryer 30.3% (58 products), microwave 38.6% (21 products), pacifier 20.1% (38 products) — bursts exist in all three categories and are the designed early-warning channel.

## Exchange 5 (edge case: which reviews get read)
**Q:** Which reviews do shoppers actually read: five-star, negative, or the short helpful votes?
**A (gist):** Negative and mid-range reviews first, then most-helpful; five-star skipped. Helpfulness votes are a sorting signal, not content.
**Work performed:**
- Changed the "effective reputation" measure: it is driven by highly-voted negative/mid reviews, not by the star mean alone.
- Computed top-10%-by-helpful-votes share by star: hair dryer 1-star 22.2% vs. 9.0% baseline (2.5× over-represented among what gets read); microwave 1-star 31.6% vs. 24.9%; pacifier 18.7% vs. 6.3% (≈3×). Negative reviews systematically over-represented in the visible, readable set.

## Exchange 6 (edge case: what makes a review worth reading)
**Q:** What makes a review worth reading: long and detailed, short and blunt, or from a verified buyer?
**A (gist):** Verified status is a credibility gate, not a reason to read; concrete specific detail (failure mode, use case, duration) is what matters. Verified + specific > long > short-and-vague.
**Work performed:**
- Added "specificity" text measure: length (words) of negative reviews as a proxy for diagnostic content.
- Computed mean word count of late-half 1–2-star reviews: dipping products 69.7 (hair dryer) vs. 49.8 non-dipping; 127.3 vs. 104.4 (microwave) — diagnostic detail in negative reviews rises before the dip, consistent with the leading-indicator role.

## Exchange 7 (context: category forgiveness)
**Q:** Which of the three product types do customers treat most forgivingly in reviews?
**A (gist):** Pacifiers most forgiving (cheap, time-pressured, low expectations; dissatisfaction exits as returns/switching). Hair dryers middle. Microwaves least forgiving (expensive, expected to last years; failures draw harshest, most detailed negatives).
**Work performed:**
- Category prior on expected rating: pacifier > hair dryer > microwave, and expected negative severity reversed.
- Validated against data: full-sample means 4.305 (pacifier) > 4.116 (hair dryer) > 3.445 (microwave); 1-star shares 6.3% / 9.0% / 24.9%. Data rank matches the expert rank exactly.

## Exchange 8 (parameter: single most trusted sign)
**Q:** When tracking a product post-launch, trust the star average or how fast reviews arrive?
**A (gist):** Star average, but only once stabilized (≈10–30 reviews / 1–3 months). Arrival speed is an attention signal, not a quality signal (fast arrivals can be a defective batch or viral complaint).
**Work performed:**
- Primary KPI = time-averaged star rating, computed only after the K threshold (exchanges 1, 3) — the "stabilized average".
- Review arrival rate demoted to a secondary diagnostic: interpreted as a possible defect/attention event, never as quality (consistent with exchange 4's burst rule).

## Exchange 9 (edge case: earliest failure sign)
**Q:** What is the earliest sign that a product is about to fail, before its overall rating has dropped?
**A (gist):** A shift in the composition of new reviews while the cumulative average is still propped by history: rising share of 1–2 stars in a short window; those negatives drawing helpful votes; text turning specific/diagnostic; verified share of new negatives rising. The average is lagging; the arrival pattern of new low ratings is leading.
**Work performed:**
- Leading-indicator test built (code/analysis3.py): for products with ≥15 reviews, split timeline in half; on the later half compute L1 = late-half 1–2-star share, L2 = verified share of late-half negatives, L3 = mean length of late-half negatives, L4 = 60-day 1–2-star cluster; outcome = late mean ≤ early mean − 0.3.
- Results (n = 124/28/205 products): corr(L1, dip) = 0.404 (hair dryer), 0.420 (pacifier) — L1 is the validated leading indicator; L3 also rises in dipping products (+19.9 words hair dryer, +22.9 microwave). L2, L4: no separation in these data (reported as limits).

## Exchange 10 (context: best long-term bet)
**Q:** Of the three products, which would you bet on for the best long-term customer satisfaction, and why?
**A (gist):** Pacifiers — cheap, repurchased, judged against low expectations; dissatisfaction exits silently (returns/switching) so visible ratings stay high and stable; refresh of satisfied repeat buyers. Hair dryers middle. Microwaves weakest (harshest, most-detailed negatives, which are the reviews shoppers read).
**Work performed:**
- Final recommendation ranking: pacifier (best and most stable), hair dryer (solid middle), microwave (weakest, most at risk).
- Validated: pacifier mean 4.305 with the smallest drift (+0.093 first/second half; slope +0.044/yr) and lowest 1-star share (6.3%); microwave mean 3.445, 24.9% 1-star, unverified reviews averaging 2.22 stars, 31.8% of mature products dipping late vs. early.

## Model parameters table (values from exchanges, with the dataset interval where they hold)

| name | value | interval [a, b] | source |
|---|---|---|---|
| early-reputation window K | first 10–30 reviews | [10, 30] | exchange 1 (corroborated by exchange 3) |
| seller monitoring window | 1–3 months or 10–30 reviews, whichever first | [1, 3] months / [10, 30] reviews | exchange 3 |
| burst (incident) threshold | ≥3 one/two-star reviews in 60 days | [3, 60d] | exchange 4 (threshold value: exchange 4; 60d window: dataset analysis) |
| category rating prior | pacifier > hair dryer > microwave | — | exchange 7 (validated: data means 4.305 / 4.116 / 3.445) |
| primary KPI | time-averaged star rating, read only after K reviews | K ≥ 10 | exchange 8 |
| leading failure indicator | late-half 1–2-star review share | — | exchange 9 (validated: corr 0.404 / 0.420 with late dip) |

Empirical values reported in the submission but not from exchanges (all from the three supplied datasets, computed in code/analysis.py, analysis2.py, analysis3.py): star distributions, verified/unverified means, lag-30d trigger tables, topic-lift tables, helpfulness-by-length tables, product success/failure split means, trajectory shares, leading-indicator correlations. No external literature values were needed.
