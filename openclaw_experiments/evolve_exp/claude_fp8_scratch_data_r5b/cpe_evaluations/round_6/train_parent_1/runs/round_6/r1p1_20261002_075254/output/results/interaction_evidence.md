# Interaction evidence — MM-Bench 2020_C

Three expert exchanges were held, one question each, in the order the policy
requires. For each: the question, the reply (summarized, not copied into the
submission), and the concrete work the reply produced.

## Exchange 1 — data provenance and completeness

**Question** (`logs/operator_feedback/expert_question_1.md`): the files contain
many zero-vote reviews and short/empty bodies — when you buy something on a
marketplace, how do you decide which reviews to actually read?

**Reply (abridged):** read reviews that are verified purchases with a body
long enough to state a concrete reason; treat helpfulness votes as weak
evidence because most reviews get zero votes from lack of exposure, not lack
of quality; zero-vote and empty-body reviews are uninformative, not negative.

**Work produced by the reply:**
- Parameter `Z` (zero-vote share) and the exposure interpretation entered the
  model: helpfulness ratio H_c is computed only where total_votes > 0, and the
  outcome analysis states votes measure exposure, not quality. Zero-vote
  shares: hair 0.6226, microwave 0.3307, pacifier 0.7197 (data).
- The "substantive review" flag `text_len >= 10 tokens` (a body long enough to
  contain a reason) is used in S_c (substantive shares 0.880/0.894/0.848).
- Product-level statistics are computed only for products with >= 20 reviews
  (T0), the product-level analogue of "no exposure, no information": 124 / 22
  / 152 stable products per category.

## Exchange 2 — key structural assumption

**Question** (`logs/operator_feedback/expert_question_2.md`): when a new
product launches, do customer opinions tend to change as more people buy it,
or stay steady from the start?

**Reply (abridged):** opinions change — front-loaded then flattening: early
buyers are self-selected so early ratings skew high, then sag to true quality
and plateau; it is an empirical regularity, not a law (good products hold,
defective products decline sharply and permanently); mix shifts (seasonal,
promotional, verified mix) move the average without the product changing.
"Steady from the start" is not a safe assumption; "early ratings biased
upward" is.

**Work produced by the reply:**
- The per-product decline rule (Model M3) compares the last-3-month mean to
  the product's *own* early-3-month baseline rather than to the category
  level, and the interpretation section states that a level drop toward the
  baseline is settling.
- The category-level trend analysis is read with the mix-shift warning: the
  microwave "improvement" (early thin months mean 3.31 vs late ~4.0) is
  reported as product-mix/exposure change, not quality change, per the
  qualification.
- The decay model m(t) = a + b·e^(−λt) was fitted and *reported as failing*
  (no category shows the early-bias-then-plateau shape at category scale),
  which is itself a result: at category level the snapshot is a cross-section
  of products, so the early-adoptor bias is visible only per product.

## Exchange 3 — interpretation context / decision threshold

**Question** (`logs/operator_feedback/expert_question_3.md`): early reviews
may sit a few stars above where they settle; how big a drop is a genuine
warning versus normal settling?

**Reply (abridged):** a drop of about half a star or less is normal settling;
a decline of about a full star or more from the early average, sustained over
several months rather than a one-month dip, is a genuine signal — and it
should be accompanied by a text shift (more defect/complaint language), not
just a lower number; a drop driven by a change in who is reviewing is not
evidence about the product. These are empirical judgment, not precise values.

**Work produced by the reply:**
- Decision parameters `theta_settle = 0.5 star`, `theta_warn = 1.0 star`
  entered the decline rule R_dec: decline iff (a) m_last3 − m_first3 ≤ −1.0,
  (b) at least 2 of the last 3 months below the early mean (sustained), and
  (c) negative-word density in the last 3 months exceeds its prior density
  (text shift). All three conditions were implemented and run
  (`code/analysis.py`); results: 3/124 hair, 1/22 microwave, 3/152 pacifier
  products flagged (5/1/4 without condition (c)).
- The success/failure decision rule R_success uses the same calibration:
  "act" thresholds (L_p > 0.25 or rising complaint density) correspond to the
  fitted P(success) ≤ 0.08 region, i.e. the "something is wrong" zone, while
  L_p ≤ 0.10 with low complaint density is the "no problem" zone consistent
  with the settling band.
- The letter's third claim (do not alarm on a half-star dip; do alarm on a
  sustained one-star drop with complaint shift) is the threshold stated as an
  operating rule.

## Use-in-submission check

No sentence, phrasing or structure from any reply was copied into
`results/solution.json`. What traveled from the exchanges is: (1) the
exposure-vs-quality interpretation of helpfulness votes and the >= 10-token
substantive standard; (2) the early-bias/plateau assumption and the
mix-shift caveat used to read the time series; (3) the two numeric
thresholds (0.5 / 1.0 star) and the sustained-plus-text-shift condition,
implemented in code and reported with the counts of products they flag.
