# Interaction Evidence — Problem 2020_C (Amazon ratings/reviews)

## Exchange 1 — Structural validity of the temporal reading

**Question (as asked, ≤20 words):** When you watch Amazon reviews of a product across a year, does the flow of new reviews roughly reflect how real buyers are experiencing the product at that moment, or do reviews mainly lag and accumulate in bursts?

**Reply (summary):** Review flow is a lagging, bursty, self-selected proxy, not a real-time sensor of product experience. Two drivers: seasonal/promotion-driven sales volume, and extreme-voice self-selection (delighted/angry buyers over-post). Reviews arrive in bursts after launch, price drops, holidays, viral complaints, then go quiet. A product can be improving while recent reviews look bad (old unhappy buyers still posting) and vice versa. Empirical judgment: treat flow as a noisy delayed indicator with a lag of weeks to months; reliable for trend direction over long windows, unreliable for "reputation right now."

**How it became work:**
- Constraint C1: no per-window "current reputation" reading is published; all reputation signals are computed over windows long relative to the bursty arrival process.
- Parameter W (long-window size) = 26 weeks (half-year) for the trend indicator; sensitivity tested at W ∈ {13, 26, 52} weeks. Interval over which it holds: the multi-year spans in all three files. Source: exchange 1 (weeks-to-months lag → window must span multiple bursts).
- Model form: EWMA reputation score R_t = Σ_k w_k · x_{t-k}, w_k = (1-λ)λ^k, with λ tuned so effective memory ≈ W (see code/model.py, constant λ, swept). This is the operationalization of "trend direction over long windows."

## Exchange 2 — Bias mechanism and validation design

**Question (as asked, ≤20 words):** You just said disappointed buyers over-post. When a product's reviews suddenly turn negative in a season, how can a marketer tell whether it's the product actually getting worse, or just the unhappy buyers who always post?

**Reply (summary):** The review stream gives the sum of (a) a real quality shift and (b) the standing self-selection bias, not the parts. Separation needs (1) a baseline — the product's own long-run negative share; the excess above baseline is the candidate real signal, and (2) a control — a comparable same-category product that did not change; if the control's negativity also spikes in the same window, the spike is seasonal/selection, not degradation.

**How it became work:**
- Model change (implemented and run): every per-product trend statistic is de-biased by the product's own pre-window baseline. Excess negativity Δ_t = NegShare(window t) − NegShare(baseline). Baseline = pre-window period of the product in the same file.
- Validation design: cross-product control test within each category. For each product and window, compute Δ_t for that product and the category-aggregate Δ_t^cat excluding the product; flag = "decline" only when Δ_t > 0 AND Δ_t > Δ_t^cat (excess not matched by the control). Temporal holdout: trend indicators and the star-rating→review-propensity model are fit on the first 70% of each product's date span (by review date, within product) and evaluated on the last 30% — no fit/test overlap in time.
- Source: exchange 2 (baseline + control rule).

## Exchange 3 — Decision-relevant uncertainty threshold

**Question (as asked, ≤20 words):** Your analytics team hands you a dashboard flagging one of the three new products: its recent reviews look clearly worse than its own history, but the number of reviews behind that flag is small. At what point do you treat the flag as an actionable warning rather than noise?

**Reply (summary):** Actionable only when the excess is large, backed by enough reviews to beat sampling noise, persistent across more than one window, and not matched by the control. Empirical judgment: a handful of reviews (under ~20–30 in the window) is noise — one buyer swings the share by tens of points; want a few dozen before reading a shift, and roughly 50–100+ before acting on a moderate shift. Magnitude must be substantial (jump from ~15% to ~35–40%+ negative), not a drift of a few points. Small-N flag = watch, not act.

**How it became work:**
- Parameters (decision thresholds, one table line each, source: exchange 3):
  - n_min_watch = 30 reviews in window before a shift is read at all (range 20–30).
  - n_min_act = 50 reviews in window before acting on a moderate shift (range 50–100).
  - δ_min = 10 percentage points of excess negativity above own baseline before the flag is "substantial" (range: a drift of a few points is not; ~15%→35–40%+ is).
  - persistence = flag must hold in 2 consecutive windows of W.
- Decision rule (implemented): status ∈ {act, watch, quiet} = f(Δ_t, n_window, Δ_t^cat, persistence), with thresholds above. Results reported per product under this rule in subtask 2 of solution.json.
- Separation of planning-level insight (direction and ranking, valid even at small n) from operational trigger (the act/watch rule) is stated explicitly in the outcome analysis.

## What each exchange did NOT provide
No empirical constant was taken from memory: all numbers the model reports either come from the three TSVs or from the three exchange values above (window size, thresholds). External search was not needed for any model parameter.
