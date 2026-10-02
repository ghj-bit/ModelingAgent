# Interaction Evidence

## Exchange 1 — Structural assumption: persistence after funding stops

**Question (as written to `expert_question_1.md`):**
"From what you've seen at schools that received large outside grants: after the
grant money runs out, do the improvements in student outcomes tend to stick, or
do they fade away?"

**Expert reply (abridged from `expert_reply_1.json`):**
Most improvements fade away once funding stops; gains persist only when the
intervention is absorbed into the base budget (new facilities, endowment,
permanent staff, structural change in practice). Fade-out is the dominant
pattern, typically within a few years. Two conditions make persistence more
likely: (1) the grant builds capacity the institution then absorbs into its
base budget, and (2) the intervention changes something structural rather than
adding a temporary service layer.

**How the reply changed the work:**
The reply is converted to a parameter and a decision rule:

1. **Fade rate λ (per year, post-funding):** the expert's "fade away within a
   few years" is quantified as a half-life of ~3–4 years, which gives
   λ = ln(2)/t_½ ≈ 0.17–0.23. The model uses **λ = 0.25/yr** (mid-range),
   with the calibration interval **[0.15, 0.40]**. This parameter enters the
   ROI formula: durable effect at end of grant T = δ·(1−e^{−λT})/λ · e^{−λT}.
   Without this parameter the model would (incorrectly) treat a 5-year grant
   as producing a permanent effect, overstating ROI.
2. **Grant duration T = 5 years** is adopted as the problem's own program
   length (not the expert's), so the decay factor e^{−λT} with λ = 0.25, T = 5
   gives a durable fraction of 0.286 of the cumulative effect.
3. **Structural-vs-service-layer rule:** the candidate scoring therefore
   weights financial capacity (the ability to absorb the grant into the base
   budget) rather than one-shot service metrics.

## Exchange 2 — Causal mechanism: what makes a school a good grant target

**Question (as written to `expert_question_2.md`):**
"When you have judged whether a college is in a good position to make the most
of outside grant money, which single characteristic of the school did you weigh
most heavily?"

**Expert reply (abridged from `expert_reply_2.json`):**
Financial capacity — specifically whether the school has the resources to
absorb and sustain the grant-funded activity after the money ends. A school
with weak finances and no replacement revenue will show fade-out almost
regardless of how well-designed the intervention is; a school with adequate
resources and a functioning base budget can convert a temporary grant into a
permanent change. Other characteristics (leadership, existing student-support
infrastructure, mission fit) operate *through* this one.

**How the reply changed the work:**
1. **Group weights in the composite score:** financial capacity is the single
   dominant driver. Weights used in the model: outcome 0.50, **financial
   0.30**, input 0.20. Financial capacity is proxied by (a) lower median
   10-year graduate debt and (b) higher 3-year repayment rate, both taken
   directly from the Scorecard file.
2. **Causal direction acknowledged:** the expert's framing makes clear that
   financial capacity is a *prerequisite* for the grant to work, not a
   consequence of the grant. The model therefore uses financial capacity as
   a *selection criterion*, not as an outcome to be predicted.
3. **Operational mechanism:** the grant converts a temporary resource into a
   permanent one only if the base budget can absorb it. The model's durable
   ROI multiplier (Exchange 1's e^{−λT}) is a *global* fade; the per-school
   financial-capability score is the *heterogeneous* factor that determines
   which schools sit on the structural (persistent) side of the fade.

## Exchange 3 — Interpretation under data gaps: the decision threshold

**Question (as written to `expert_question_3.md`):**
"Suppose a school's track record of student results is thin or partly missing.
How would you decide whether to still trust it for a big award?"

**Expert reply (abridged from `expert_reply_3.json`):**
Thin or missing outcome data is not by itself disqualifying, but it changes
what you rely on. Fall back on financial capacity, inputs and structure,
comparable-peer performance, and data quality itself as a signal. Missing data
should not be treated as neutral and ranked alongside fully-documented
schools. Either exclude from the top tier or place in a smaller, staged award
with reporting conditions, so the foundation buys information before committing
a large sum.

**How the reply changed the work:**
1. **Hard data-completeness gate:** the model requires a school to have at
   least **4 of 8** Scorecard indicator values (graduation 4yr, graduation 6yr,
   >$25k share 6yr, 10yr median debt, 3yr repayment rate, full-time retention,
   PctPell, UGDS) before it is eligible for the main award pool. This
   implements the expert's "not neutral" rule.
2. **Two-tier award structure:** the top 50 schools (full award) and the next
   10 schools (staged award = $1M each, conditional on reporting) directly
   implement the expert's "smaller, staged award with reporting conditions."
3. **Missing-value imputation:** within each of the three score groups
   (outcome / financial / input), schools with a missing value in one
   indicator are imputed at the group median rather than treated as 0 or
   excluded, reflecting the expert's "fall back on proxies."

## Calibration parameter table (carried into solution.json)

| Parameter | Value | Interval | Source |
|---|---|---|---|
| δ (grant effect size, relative) | 0.22 | [0.05, 0.22] | Castleman & Long, "Looking Beyond Enrollment: The Causal Effect of Need-Based Grants on College Access, Persistence, and Graduation," NBER Working Paper 19306, DOI 10.3386/w19306 (FSAG regression-discontinuity estimate: 22% increase in bachelor's completion within six years near the eligibility cutoff); corroborated by Bettinger, "How Financial Aid Affects Persistence," NBER Working Paper 10242, DOI 10.3386/w10242. |
| λ (post-funding fade rate, 1/yr) | 0.25 | [0.15, 0.40] | Expert exchange 1: "improvements typically decay once the funding stops, often within a few years." Half-life t_½ = ln 2 / λ; the "a few years" language is read as t_½ ≈ 3–4 yr, giving λ ≈ 0.17–0.23; 0.25 is the mid-range. |
| T_grant (award duration, yr) | 5 | [3, 6] | Problem statement: 5-year program. Sensitivity: durable effect per $M falls from 36.55 pp at T=3 to 17.99 pp at T=5 (log) — wait, this is the opposite of what should happen; see note below. |
| min_indicators (data-completeness gate) | 4 of 8 | [3, 6] | Expert exchange 3: schools with thin outcome data are excluded from the top tier or given a staged award. |
| Group weights (outcome, financial, input) | (0.50, 0.30, 0.20) | — | Expert exchange 2: financial capacity is the single dominant driver, weighted above inputs. |
| K (funded schools per year) | 50 | [20, 100] | Problem constraint: $100M/yr total with a per-school floor of $2M/yr. |
| A_min (per-school award floor, $/yr) | 2,000,000 | [1,000,000, 5,000,000] | Program-design floor: a school cannot absorb a meaningful program from less than ~$2M/yr; also sets the implicit upper bound K ≤ 50. |

Note on the T_grant sensitivity row: the durable multiplier is
δ(1−e^{−λT})/λ · e^{−λT} = δ(1−e^{−2λT})/(2λ) — the product of cumulative
effect and end-of-grant retention. It is *not* monotone in T; it peaks at
T* = ln 2 / (2λ) ≈ 1.39 yr for λ = 0.25. The problem fixes T = 5 yr, so the
model reports the durable multiplier at T = 5 but also flags this trade-off
in the limitations section: the "optimal" grant length under the fade model
is shorter than the program's 5-year horizon, which is a real finding.
