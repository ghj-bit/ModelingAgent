# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — ICM churn model (task 2015_C)

Three expert exchanges, one question each. Each reply was turned into a
concrete model parameter or decision rule before the next exchange.

## Exchange 1 — structural assumption (independence vs. contagion of churn)

**Question (expert_question_1.md):**
"When a few people quit at once in a company like ICM, does that tend to draw
coworkers to quit soon after, or do most people leave for reasons completely
unrelated to who else left?"

**Reply (expert_reply_1.json), substance:**
Mostly unrelated; a modest contagious component. Dominant drivers are
individual (pay, promotion blockage, supervisor, outside offers) and largely
independent. Contagion is real but secondary — a modest elevation in quit
hazard among close coworkers of a leaver, strongest for strong ties, same-level
peers, and when the departure signals good outside options or blocked
advancement. For ICM, mid-level manager churn is better explained by the
structural cause (stuck in role, no advancement) than by contagion — many
mid-level managers leaving at once reflects a shared condition, not one person
pulling others out.

**How the reply changed the work:**
- Set the base churn model to *independent* per-person hazards
  (`left_i ~ Binomial(P_i, c_i)`) — the dominant mechanism.
- Added a *secondary* contagion channel as a sensitivity parameter
  (`--contagion`, default 0): same-level coworkers of a prior-year leaver get
  an elevated hazard. Calibrated at 30% of the base hazard as the
  "modest" upper bound; base case runs at 0 (independence), the sensitivity at
  0.3 shows a 3.8 pp drop in year-2 fill (0.6757 → 0.6378) — confirming the
  expert's "secondary" framing: real, but not the driver.
- Interpreted the mid-level 2× churn rate as a *common-cause* structural effect
  (advancement blockage), not contagion — so the model sets mid-level
  `c_i = 2×` base rather than coupling them to neighbor departures.

## Exchange 2 — causal mechanism (headcount gap vs. ramp-up as the binding loss)

**Question (expert_question_2.md):**
"When a company is short-staffed and loses workers, what usually hits the
business hardest: fewer people doing the work, or the time it takes new hires
to become fully productive?"

**Reply (expert_reply_2.json), substance:**
Ramp-up usually hits harder. A headcount gap is a throughput loss partly
absorbed by overtime/triage/deferral; a new hire's time-to-full-productivity is
a capability loss that cannot be compressed by effort. Typical: 3–6 months for
individual contributors, 6–12+ months for supervisory/managerial roles; during
that window the team also loses the leaver's informal knowledge and network.
Exception: low-skill standardized work, where a replacement is near-fully
productive in days–weeks and the headcount gap dominates. For ICM, with
mid-level manager churn and experience requirements, ramp-up is the binding
constraint.

**How the reply changed the work:**
- Added a ramp-up productivity loss: this year's new hires/promotions run at a
  `ramp` fraction of full productivity (default 0.5, representing the
  3–12+ month ramp for ICM's skill-based and managerial roles), so
  `productivity = (ΣP − (1−ramp)·new) / 370`.
- Quantified the split: at base churn, ramp-up costs 4.46 pp of effective
  capacity (0.0446 × 370 ≈ 16.5 person-equivalents per year) on top of the
  vacancy loss. This is the "indirect effect on productivity" the problem
  asks for (task 2), and it is *additional* to, not a restatement of, the
  headcount gap — matching the expert's "cannot be compressed by effort."
- Kept low-skill roles (clerks) as the partial exception: their 1-month recruit
  time means their ramp is short; the model applies the ramp uniformly but the
  per-level recruit-time column documents where the loss is smallest.

## Exchange 3 — interpretation context (decision-relevant vacancy threshold)

**Question (expert_question_3.md):**
"In a company like ICM, what level of unfilled positions would leadership
start treating as a crisis and act on, rather than just accepting?"

**Reply (expert_reply_3.json), substance:**
Low single digits to ~10% vacancy is normal operating friction. Crisis begins
around 15–20% unfilled — the point where the gap visibly degrades output,
forces chronic overtime, and blocks the promotion pipeline. ICM's stated 85%
fill (15% vacancy) already sits at the edge of the crisis band, consistent with
the "always short-handed" framing. Above ~20–25% unfilled it becomes an
operational emergency. Empirical judgment, not a precise threshold.

**How the reply changed the work:**
- Adopted a decision rule for interpreting every scenario: classify the
  end-of-horizon *vacancy rate* (1 − fill) as (i) normal ≤10%, (ii) crisis
  15–20%, (iii) emergency >20–25%.
- This turns the raw fill numbers into the actionable conclusion the problem
  wants (task 4): ICM **cannot** sustain 80% full at 25% churn (vacancy hits
  ~42% by year 2 — deep in the emergency band) nor at 35% (vacancy ~55% by
  year 2). Even at the base 18% the vacancy is already ~32% by year 2
  (emergency), so the 85% start point is not sustainable under current
  recruiting capacity.
- Framed the cost/indirect-effect answers relative to these bands rather than
  as abstract percentages.

## Provenance note

No expert sentence, phrasing, or structure is copied into solution.json. The
replies supplied only three inputs — the independence/contagion split, the
ramp-up as the binding productivity loss, and the 10/15-20/25% vacancy
decision bands — which are stated in the solution as the model's own calibrated
parameters and decision rule with the exchange number as source.
