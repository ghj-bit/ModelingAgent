# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — 2023_Y (used sailboat pricing)

Three fixed exchanges, one question each. Each reply is recorded below and the
specific way it changed the model.

## Exchange 1 — Operational mechanism (asked before model formulation)

**Question (expert_question_1.md):** "When an owner lists a used sailboat for
sale, what typically determines the asking price they choose?"

**Reply (summarized):** The asking price is an anchored, negotiated quantity set
by the owner/broker off comparable listings and recent sales for the same
make/variant/year (dominant factor), then age/condition, size/configuration,
equipment inventory, region (market depth, duties, currency, transport), and
seller motivation. Asking prices are set above the expected transaction price
to leave negotiating room; sales typically close below ask.

**How it changed the work:**
- Chose a **variant-level baseline price as the dominant term**: for each
  Make+Variant the data's own median/typical price is the anchor, rather than a
  global regression through the origin. This is a model structure decision
  (Exchange 1, source: expert reply 1).
- Recognized listing price as an **ask**, not the realized transaction: the
  reported prices are systematically above expected sale value, so model
  "precision" is framed against the ask and this systematic gap is stated as a
  bias (subtask 1 precision discussion).
- Condition/equipment, seller motivation and negotiating room are **not in the
  data**, so they enter the model as the irreducible residual variance (the
  unexplained spread within a variant), which bounds per-variant estimate
  precision.

## Exchange 2 — Causal hierarchy of regional differences (asked after the baseline model, before the regional-effect model)

**Question (expert_question_2.md):** "When you compare several boats of the
same make, variant, and year listed in different regions, what mainly explains
the price differences between them?"

**Reply (summarized):** For identical make/variant/year the remaining
differences are driven mainly by condition/equipment (largest single driver),
seller motivation/time-on-market, local market depth/seasonality, and
region-specific costs (duties, VAT, currency, delivery). **Region itself is
often a proxy for these factors rather than an independent cause.**

**How it changed the work:**
- The regional-effect model is framed as an **additive price-level shift on the
  same-variant baseline** (a region factor per Make+Variant), i.e. the
  question "how much more/less does the same boat ask in this region" — not a
  claim that region is an independent causal lever. The interpretation section
  states the region term conflates true market-depth effects with condition
  mix, seller motivation, duties/currency, and data idiosyncrasies (subtask 2
  "practical vs statistical significance" and "consistent across variants").
- Because condition is the largest within-variant driver and is unobserved,
  region coefficients that are driven by a few listings of a given variant are
  down-weighted: the regional model reports only effects whose supporting
  sample is adequate, and treats small-sample region/variant cells as
  unreliable (a decision-rule change, Exchange 2).

## Exchange 3 — Decision-relevant uncertainty threshold (asked after the regional model, before the precision/accuracy framing)

**Question (expert_question_3.md):** "When a broker uses a price estimate to
advise on a boat, how far off would the estimate need to be before it becomes
useless to them?"

**Reply (summarized):** An estimate is useful within roughly **±10%** of the
realistic transaction price (the scale of normal asking-to-selling negotiation
and condition variation); beyond about **±15–20%** it stops being actionable.
Empirical judgment, scale-dependent (a ±10% band is a larger dollar amount on
a $500k boat than a $100k one).

**How it changed the work:**
- Sets the **acceptance band for estimate precision**: the model's per-variant
  prediction intervals are evaluated against a ±10% useful / ±20% unusable
  scale (subtask 1 precision discussion and subtask 4 conclusions).
- Frames all reported errors **relatively** (percent of price) rather than
  absolute dollars, matching the broker's decision scale.
- The final report's "is this estimate actionable" criterion is: within ±10%
  of observed ask for the same variant → useful; the model is judged on how
  many variants fall inside that band, not on a single global RMSE.
