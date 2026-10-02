# Interaction Evidence — Task 2023_Y (Sailboat Pricing)

Three exchanges were held, one question each, before and between the modeling
work. Each reply was converted into a concrete parameter or decision rule in
the model; the question files, request/reply JSON, and the code lines that
consume the reply are listed below.

## Exchange 1 — structural assumption (asked before modeling)

**Question** (`logs/operator_feedback/expert_question_1.md`): whether the listed
price of a used sailboat reflects the actual selling price, or whether sellers
list above what they finally sell for.

**Reply** (`logs/operator_feedback/expert_reply_1.json`): listing price is an
asking price set with negotiating room; final sales commonly settle below ask.
The expert rejected the assumption that listing = selling price and characterized
the gap as varying with seller motivation, time on market, and condition, with a
working range on the order of 5–15% below list (more for stale or problem boats).
The regional effect estimated from listings reflects asking-price behavior, not
selling-price behavior, one-to-one.

**How the reply changed the work** — became a parameter of the model:

- `haircut_delta = 0.10`, interval `[0.05, 0.15]`, recorded as a calibrated
  input in the parameter table of `mathematical_modeling_process`
  (source: expert exchange 1).
- The model is explicitly a model of *listing (asking) price*, and all
  interpretation statements (regional effects, HK effect, precision) are
  framed as asking-price statements. Sale-price statements carry the haircut:
  `ln(sale) ~ N(ln(list) − 0.10, s)` (see `code/model_price.py`, docstring
  and the `haircut_delta` field in `results/model_results.json`).
- The haircut was swept over its interval (`--delta 0.05,0.10,0.15` in
  `logs/model_price.log`); the fitted listing-price coefficients are invariant
  to delta by construction, and the reported sale-price point estimates shift
  by exactly the haircut, so the interval's effect on conclusions is stated in
  the outcome analysis.

## Exchange 2 — causal mechanism (asked after Exchange 1's assumption was set)

**Question** (`logs/operator_feedback/expert_question_2.md`): if the same
sailboat were listed in Europe, the Caribbean, and the USA at the same time,
would the broker expect different asking prices in each place, and why.

**Reply** (`logs/operator_feedback/expert_reply_2.json`): yes, differences are
expected and often on the order of 10–30%, occasionally more. Drivers named:
market depth/demand (USA and parts of Europe liquid; Caribbean thinner and
transient), taxes and import duties (EU VAT, Caribbean/USA duty and registration
regimes absorbed partly into asking prices), currency and local pricing
conventions, condition/spec differences (ex-charter Caribbean boats, EU vs US
spec), and real logistics/delivery cost that creates a location premium. The
expert also stated the effect is **not uniform across variants** — it depends
on how popular and locally supplied each model is.

**How the reply changed the work** — became constraints and a check:

- The model tests the regional effect empirically (region dummies in the
  log-linear fit, `code/model_price.py` and `code/analysis.py`) instead of
  assuming a single regional premium; the reply supplies the *expected magnitude
  band 10–30%* as a sanity interval for the fitted region coefficients, which is
  checked in the outcome analysis (fitted effects: mono USA +33%, mono Caribbean
  −9%, cat USA +12%, cat Caribbean −9% at age+length controls — inside or
  marginally outside the band, as expected for a USA premium plus age/length
  confounding).
- "Not uniform across variants" became an explicit hypothesis to test:
  `variant_consistency` in `code/analysis.py` computes per-variant region
  contrasts for variants listed in ≥2 regions (mono: 31 Caribbean and 41 USA
  variant-region pairs; cat: 29 and 13). Result: USA contrasts are positive for
  ~88% of mono and ~62% of cat pairs; Caribbean contrasts are negative or
  near-zero for ~61–62% of pairs. The regional effect is therefore
  directionally consistent for USA and opposite/negligible for Caribbean, and
  its *size* varies by variant — matching the expert's mechanism statement.
- The mechanism list (demand depth, tax/duty, currency, spec, logistics) is
  the interpretation used in the regional-effect subtask, including why the
  USA effect is positive and the Caribbean effect negative.

## Exchange 3 — interpretation context / decision threshold (asked last)

**Question** (`logs/operator_feedback/expert_question_3.md`): if a broker in
Hong Kong saw a price estimate with a margin of about 30%, how large a gap
between the estimate and a real comparable sale would make the broker distrust
the estimate.

**Reply** (`logs/operator_feedback/expert_reply_3.json`): a 30% margin is
already roughly the size of the regional and negotiation effects, so such an
estimate is only weakly informative; the broker starts distrusting an estimate
when a genuinely comparable sale falls outside that band (roughly >30% away
from the point estimate) and treats a gap of about 40–50% or more as clear
evidence the estimate is unreliable for that boat. The threshold depends on how
comparable the comparable really is (same variant, year, spec, condition,
region): a 35% gap against a near-identical boat is more damning than a 50% gap
against a loosely similar one.

**How the reply changed the work** — became a decision rule:

- `trust_gap_max = 0.45`, interval `[0.40, 0.50]`, recorded as a calibrated
  input (source: expert exchange 3) in the parameter table of
  `mathematical_modeling_process`.
- `code/hk_pricing.py` applies it as a reliability gate: each subset variant's
  95% predictive band (exp(2·1.96·se) − 1) is compared against 0.45; variants
  whose band exceeds the threshold are labeled `decision_reliable: false` and
  are reported as "not suitable for pricing decisions, use only as a wide
  screen" rather than as point estimates. Outcome: the full variant-level band
  is wide (53–139%) for every subset variant, so no subset variant's *full*
  band clears the 45% gate; the broker-facing guidance is therefore a banded
  price range (lo/mid/hi) with an explicit reliability label per hull type,
  and the tighter pooled-model band (RMSE 21% cat / 44% mono) is used as the
  practical screening precision. This is reported in the HK subtask outcome.
- The comparability caveat from the reply (threshold depends on how near-identical
  the comparable is) is applied by conditioning the reliability label on
  variant, year, and region proximity — i.e., the gate is applied to
  variant-level estimates, not to pooled estimates.

## Files

- Questions: `logs/operator_feedback/expert_question_{1,2,3}.md`
- Request/reply JSON: `logs/operator_feedback/expert_request_{1,2,3}.json`,
  `expert_reply_{1,2,3}.json` (controller-managed)
- Consuming code: `code/model_price.py` (haircut, listing-vs-selling framing),
  `code/analysis.py` (region robustness, variant consistency, hull
  interaction), `code/hk_pricing.py` (trust gate, spread ceiling)
- Result artifacts: `results/model_results.json`, `results/analysis.json`,
  `results/hk_pricing.json`
