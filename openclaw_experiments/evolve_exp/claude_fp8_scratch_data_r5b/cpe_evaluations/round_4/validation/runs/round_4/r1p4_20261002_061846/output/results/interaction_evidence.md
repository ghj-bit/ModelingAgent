# Interaction Evidence — Problem 2016_C (Goodgrant Foundation)

Three expert exchanges, one question each, sequenced per policy. Files:
`logs/operator_feedback/expert_question_N.md` / `expert_reply_N.json`.

## Exchange 1 — Data provenance and completeness

**Question:** Why would a college stop reporting, or report less, to the federal education surveys, and do the schools that still report well enough count as a fair sample of all American colleges?

**Reply (summary):** Reporting is tied to Title IV participation; full non-reporting usually means closure, loss of aid eligibility, or a non-Title-IV school. Partial non-reporting comes from small institutions without administrative capacity, optional or non-computable items (e.g., small-cohort graduation rates), privacy suppression of small cells, and Scorecard elements populated only for sufficiently large cohorts. Missingness is therefore systematically tied to size, sector, and aid status — not random. The reporting population is **not** a representative sample of all U.S. colleges: it over-represents large, public, four-year, Title IV schools and under-represents small, private, for-profit, and two-year schools.

**How the reply was turned into work:**
- Eligibility filter applied in `code/build_model.py::load_and_clean`: only Title IV–type candidates present in the Scorecard extract with `CURROPER==1`, a 4-year designation (`PREDDEG==1` or 150% completion rate reported), usable `PCTPELL`, and `UGDS>0`. Result: 2,106 of 2,977 candidates retained (87.2%).
- `PrivacySuppressed` strings in the seven NSLDS/Treasury/Scorecard columns were converted to missing rather than 0 (a suppression is non-reporting, not a zero value).
- Selection bias recorded as a standing limitation: results describe the reporting, Title IV, 4-year candidate population, not "all American colleges" (see limitations in solution.json, task 1).
- Small-cell suppression observed in data (e.g., `RET_FT4` populated for only 2,348 of 7,804 rows) motivated the imputation-free design below: the model never fills structural zeros; it uses indicators for which outcomes are observable.

## Exchange 2 — Key structural assumption

**Question:** When a college gets new money, do its graduates tend to earn more several years later, and why would that link be weak or unreliable?

**Reply (summary):** The money-to-earnings link is weak and unreliable at best. Money is not the binding constraint at most schools (it flows to facilities, administration, enrollment growth); earnings are driven mostly by factors schools do not control (field of study, labor market, selectivity, family background); selection confounds spending comparisons; 6–10-year earnings reflect labor-market timing, not a 2016 grant; and small per-school grants relative to a school's budget are unlikely to move earnings measurably. Treat "investment → later earnings" as a weak, noisy, confounded relationship, not a reliable causal lever.

**How the reply was turned into work:**
- The structural link **grant → retention/completion (intermediate, school-controlled outcomes)** is used instead of grant → 10-year earnings. 10-year earnings enter only as a *valuation* of an extra completion/retention, never as the causal claim.
- Dose–response bounded: expected retention gain per school saturates, `η_i = η_max·(1 − e^(−g_i/SAT))` with `η_max = 1.5 pp` (interval [0.5, 3.0] from the sweep) and saturation `SAT = $6M` per school over 5 years (interval [$3M, $12M]). This encodes "small per-school grants are unlikely to move outcomes measurably" — the marginal effect decays as grant size grows, and the portfolio is spread (per-school cap $3M, max share 3% of the annual pool).
- The allocation objective maximizes *intermediate* expected outflow (retention + completion + collateral program funds), not a claimed earnings effect.

## Exchange 3 — Interpretation context / decision threshold

**Question:** Since grant dollars rarely prove they raised earnings, what would make a school worthy of funding in your view?

**Reply (summary):** Fund when the money can plausibly change what the school does for students and the school has shown it can convert resources into student progress. Markers: demonstrated capacity to use money well; a student body where the marginal dollar matters (high low-income/Pell share); measurable headroom — outcomes weak relative to peer group and inputs; a plausible mechanism (retention, completion, advising, remediation); non-duplication of existing large-grant funding; stability and reporting quality. Unifying idea: fund capacity + need + headroom, judged on intermediate outcomes the school controls.

**How the reply was turned into work:**
- The opportunity score is exactly this composition: `Opportunity = w_cap·Capacity + w_need·Need + w_head·Headroom` with `w_cap = 0.35, w_need = 0.35, w_head = 0.30` (all three swept: W_HEAD ∈ {0.1, 0.3, 0.5} changes portfolio ROI by <3%).
  - `Capacity` = size ≥ 500 FTE, reports retention, low loan reliance (≤75%), repayment rate above the 45th percentile.
  - `Need` = `PCTPELL` (share of undergraduates on Pell grants).
  - `Headroom` = value-added residual from an OLS of `RET_FT4` on composition/context (Pell share, size, sector, selectivity proxy, loan and debt load, institutional flags) — i.e., underperformance not explained by who the students are.
- Decision rule: fund schools with a complete profile (all three components computable) ranked by opportunity; portfolio constrained to ≤40 new schools per year and ≤$3M per school (5-yr cap), which operationalizes the risk tolerance: any single school cannot carry more than 3% of the annual pool, so no school's uncertain effect can dominate the portfolio.
- "Non-duplication": the model funds schools with *headroom* (underperforming their profile) and high need — not already high-performing institutions whose outcomes do not move with added money — and the 40-school/yr breadth cap keeps the portfolio diversified across states (top states: OH 21, TX 17, MI 12 of 170).
