# Interaction Evidence — Problem 2016_C (Goodgrant Foundation investment strategy)

## Exchange 1 — Operational definition of the key outcome variable

**Question:** "The College Scorecard file gives each school's typical graduate's median wage ten years after enrollment, from tax records of people who still work. Does that number reflect where the school's graduates actually end up, or does it miss an important group of graduates?"

**Reply (summary):** The Scorecard earnings measure (md_earn_wne_p10) is built from federal tax records covering only students who received federal aid and are working and tax-matched ~10 years after enrollment. It excludes: non-working graduates; students never matched in tax records (no federal aid, abroad, outside matched records); non-graduates. It is a partial, selection-biased figure — typically an overstatement of the typical enrollee's earnings — and says nothing about geography.

**How the reply changed the work:**
- Value/constraint adopted: `md_earn_wne_p10` and `gt_25k_p6` are treated as *upper-bound proxy* indicators of earnings outcomes, not population means. In the ROI model they enter with reduced weight (w_earnings = 0.20, vs 0.45 for the completion/retention composite) and the model does NOT use raw median wages as the ROI numerator — it uses wage *gaps* relative to a matched peer group, with an explicit caveat in the results.
- Interval of validity: constraint holds for the 2013–2016 Scorecard vintage used here (pooled cohort definitions per data dictionary, 09-08-2015).

## Exchange 2 — Causal direction of retention/completion as "absorptive capacity"

**Question:** "Schools that keep first-years coming back and finish degrees are more likely to turn extra money into better student results. Which is the stronger clue, and why?"

**Reply (summary):** Retention and completion are the stronger clue, causally: they are the school's own demonstrated output — the same conversion process new money must work through. Earnings are weaker (confounded by intake quality and tax-record selection bias). Caveat: retention/completion are also partly driven by intake quality, so they are not a clean value-added measure.

**How the reply changed the work:**
- Constraint adopted: the ROI numerator is anchored on the composite `absorptive capacity` score = 0.5·z(completion composite) + 0.5·z(retention composite), NOT on earnings. Earnings enter only as a secondary, bias-discounted term (weight 0.20).
- Intake adjustment adopted: because intake quality still contaminates retention/completion, the model includes an intake-adjustment residual — for each school, the outcome metrics are compared to a peer group (same state, same institution type, size band, Pell band), and only the gap vs peer median counts as "the school's own effect".
- Parameter: w_capacity = 0.5 (completion) + 0.5 (retention), w_earnings = 0.20, w_debt_health = 0.15, w_need = 0.10 — the weights encode the expert's causal ranking.

## Exchange 3 — Robustness threshold for a small observed edge

**Question:** "If a school's numbers only beat similar schools by a small margin, would you still recommend funding it, or do they need a clear lead? What separates real from noise?"

**Reply (summary):** A small margin is neither an automatic reason to fund nor to reject. Real signal: the lead is consistent across several independent measures (retention, completion, earnings, debt repayment), survives intake adjustment, and is large relative to the metric's year-to-year volatility. Noise: a one-year, one-metric edge within the normal fluctuation band; a lead that disappears after intake adjustment; a difference smaller than the cohort-size uncertainty (small schools have very noisy rates). Practical rule: require a clear, multi-measure, intake-adjusted lead before treating a school as a *priority* candidate; a small but consistent, adjusted edge still justifies funding as a lower-priority candidate; a small isolated/unstable edge should not drive a recommendation.

**How the reply changed the work:**
- Decision rule adopted (tiering):
  - Tier 1 (priority, full grant tranche): school ranks in the top quantile on ≥3 of the 4 intake-adjusted outcome dimensions AND its intake-adjusted capacity score ≥ 1.0 standard deviation above its peer-group median.
  - Tier 2 (conditional, smaller tranche): top quantile on 2 dimensions, OR capacity score ≥ 0.5 sd above peer median, with consistency across ≥2 measures.
  - Tier 3 (watch list / no grant): edge is single-measure or below cohort-size uncertainty threshold (for small schools: require the intake-adjusted gap ≥ 2/√n_completers, a binomial-style noise floor derived from the completion cohort).
- Constraint adopted: minimum effective sample guard — schools with completers cohort below n_min = 50 are capped at Tier 2 (their rate uncertainty is too large to support a priority claim).
- These tiers are what produces the 1-to-N prioritized candidate list and the per-school grant tranches in the submission.

## Provenance
All three replies are the source for the weight vector, the peer-group intake-adjustment design, the upper-bound treatment of earnings, and the 3-tier decision rule. The replies themselves are not quoted into solution.json; only the values, constraints, and decision rules derived from them appear there.
