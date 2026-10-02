# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence

Three exchanges, one question each, asked before the work each governs.
Every reply is turned into a named parameter/constraint in `code/hr_model.py`
with its value, interval, and the exchange that supplied it. The submission
(`results/solution.json`) contains only my own formulation — the parameters,
equations, and results — not the experts' sentences.

## Exchange 1 — Data provenance / dynamics

**Question (expert_question_1.md):**
"In real companies, when an employee quits, does it tend to make the coworkers
close to them more likely to quit too?"

**Reply (expert_reply_1.json), distilled:**
Yes — turnover contagion / churn clustering is real. Coworkers with close
friendship or advice ties to a leaver show a measurably higher subsequent quit
probability. The effect is real but moderate (order of tens of percent relative
to baseline, not a doubling), decays with social distance (weaker for
second-order ties), is strongest for friendship ties and directly-connected
people, and is stronger in dense informal networks and periods of high churn.

**How it shaped the work:**
- Confirms the task's churn-diffusion premise (Issue 2) and justifies the
  contagion term rather than treating quits as independent.
- `CONTAGION = 0.30, interval [0.10, 0.50]` — the relative hazard multiplier
  applied to seats with a recently-churned direct neighbour ("tens of percent").
- `DECAY = 0.50, interval [0.30, 0.70]` — second-order / next-year exposure
  carried forward at ~half strength (effect "decays with social distance").
- Implemented as a per-level exposure counter in `simulate()`: each leaver
  exposes ~`TIES=4` direct neighbours; exposed seats quit at
  `base*(1+CONTAGION)`, the rest at `base`; exposure is saturated at the level
  size (ties overlap) and decayed by `DECAY`.
- Sweep (`code/hr_model.py --sweep CONTAGION=0.0,0.1,0.3,0.5`) shows baseline
  final fill 81.3% → 74.5% as contagion rises, and turns the 25%-churn case
  into a self-reinforcing collapse (year-2 leaves 85→98). Sensitivity is
  moderate, matching the expert's "real but moderate."

## Exchange 2 — Structural assumption (no-external / qualified-only pipeline)

**Question (expert_question_2.md):**
"When a company quits hiring and promotes only people already qualified, do
middle-level roles stay empty for a long time?"

**Reply (expert_reply_2.json), distilled:**
Yes. With no external recruiting the only source of middle replacements is
internal promotion, and "qualified" is defined by several years at specific
lower levels, so the pipeline is thin and slow. With mid-level turnover running
about twice the average, departures outpace qualified-candidate supply, and
vacancies accumulate. The gap is structural, not temporary — the qualification
requirement caps how fast the pipeline refills. Strongest for the most senior
of the middle roles (longest prior experience).

**How it shaped the work:**
- `QUALIFIED = 0.50, interval [0.30, 0.70]` — fraction of a level that has
  accrued the required tenure and is therefore promotable.
- `PROMO_LAG = 3, interval [2, 5]` — years of tenure required before a seat is
  eligible to promote (task Issue 6: "several years of experience").
- Drives the qualify-only branch of `simulate()`: promotions move only
  qualified candidates up one level, into existing vacancies only; the vacated
  lower seat is then backfilled. This is what makes T5b (qualified-only) a
  *persistent* structural shortfall rather than a one-year dip, and T5a
  (no external recruiting at all) a cascading collapse to ~51% fill — exactly
  the "structural, not temporary" gap the expert described.

## Exchange 3 — Interpretation context / decision threshold

**Question (expert_question_3.md):**
"For a company budget decision, at what fill-rate would you say the
organization is genuinely at risk, not just a bit short?"

**Reply (expert_reply_3.json), distilled:**
No universal threshold, but from staffing practice: an organization is
genuinely at risk when sustained fill drops below ~80–85%, and clearly in
trouble below ~75%. 85–90% is normal; 80–85% is where strain becomes visible
(workload redistribution, rationing); below ~75–80% critical and mid-level
roles stay vacant long enough to break the pipeline, and the shortfall becomes
self-reinforcing (overload drives further churn). Since ICM normally runs at
85%, treat sustained fill below ~80% as genuine risk and below ~75% as crisis.

**How it shaped the work:**
- `RISK_FILL = 0.80, interval [0.78, 0.85]` — sustained fill below this =
  "genuine risk" band.
- `CRISIS_FILL = 0.75, interval [0.72, 0.80]` — sustained fill below this =
  "crisis."
- These become the decision rule in `simulate()`: each year's fill is classified
  `ok / risk / crisis`, which is how every scenario result is interpreted and
  reported (e.g. baseline stays `ok`/`risk`-edge, 25% churn = `risk`/`crisis`,
  35% churn = `crisis`, T5a = `crisis`).

---
All three replies were converted into named, sourced, interval-bounded model
parameters before the next exchange was asked, and their effect is visible in
the scenario outputs above.
