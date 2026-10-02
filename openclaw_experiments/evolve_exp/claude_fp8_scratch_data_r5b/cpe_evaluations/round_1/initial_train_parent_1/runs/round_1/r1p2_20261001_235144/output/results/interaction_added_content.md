# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — Problem 2015_C (ICM churn)

Three exchanges, one question each. Files: `expert_question_N.md` /
`expert_reply_N.json` in `logs/operator_feedback/`.

## Exchange 1

**Question:** When a manager quits, roughly how long before the managers they
directly supervise start thinking about leaving?

**Reply (substance):** No precise figure; an empirical judgment. Subordinate
turnover thinking appears within roughly 3–12 months of a direct supervisor's
departure, strongest in the first 3–6 months. Mechanism is
social/observational: subordinates see the exit was possible and beneficial;
dissatisfaction spreads through the informal tie. Strongest when the departing
manager was well-liked or a mentor, when the subordinate's advancement was
tied to that manager, or when the replacement is slow/poor-fit. Weaker when
the subordinate has strong independent ties or the exit looked involuntary.

**How the reply became work (model change, run: `logs/sweep_churn2.log`):**
The churn-hazard function in `code/model.py` gained a contagion multiplier
`cont_mult(m)` for subordinates of a recently-churned layer: hazard rises from
1.0× to 1.5× over months 0–3, holds at 1.5× through month 6, decays linearly
back to 1.0× by month 12, and stays at 1.0× thereafter. Applied to the hazard
`h_j·mu/12` in the monthly departure step; a layer's departure sets
`last_dep[i, :] = 1` for all layers below it. Sensitivity (exchange 1 supports
an interval, so it was swept): peak multiplier in [1.2, 2.0], window
[6, 18] months. At 18% churn the contagion contributes 26 layer-months of
elevated hazard over 2 years; it is not a dominant driver of the vacancy
dynamics (hiring capacity is), but it raises the early-turnover risk in
middle-manager layers, which is where the problem says the damage concentrates.
Interval of validity: the reply is a generic-practice judgment, used for the
12-month window and the 3–6 month peak; the 1.5× peak is a modeling choice
within the reply's "order of months, not days or years" bounds.

## Exchange 2

**Question:** When an open role stays unfilled for months, which part of the
company feels the strain first?

**Reply (substance):** First the immediate work group of the vacant position —
peers, direct subordinates, and the supervisor owning the slot — within weeks
(workload, overtime, morale). Second, adjacent groups that consume the role's
output (internal customers, downstream teams) after a month or two, once
backlogs accumulate. HR feels administrative strain from day one (process, not
operational). The broader organization feels it last, and only for critical or
bottleneck roles.

**How the reply became work (model change, run: `logs/sweep_churn2.log`):**
The productivity-gap formula in `code/model.py` is now
`prod_gap = Σ_j (vacancy_j + 0.5·ramping_j)/370`: an empty seat removes
1/370 of company output, localized to its own layer (the same layer's peers
and subordinates absorb the load, so the cost stays inside the layer), with no
separate downstream layer for the 1–2 month backlog effect (it is second order
against the vacancy term at this model's resolution). The "broad organization
only for bottleneck roles" point is retained as a limitation: the model has no
bottleneck layer, so organization-wide spillover is not priced.

## Exchange 3

**Question:** In your experience, when is a new hire fully ramped up and
working at full productivity?

**Reply (substance):** Level-dependent. Entry/frontline ~1–3 months; skilled
individual contributors and experienced supervisors ~3–6 months; junior
managers and mid-level ~6–12 months (must learn technical work plus informal
network); senior/executive 12–18+ months. Ramp scales with firm-specific
knowledge and relationship-building; network-dependent roles take far longer.
Planning rule: a new hire is at partial productivity for the first half of
ramp-up and fully productive at the end.

**How the reply became work (model change, run: `logs/task5_external.log`):**
`model.py` tracks new hires as age-counted cohorts; a cohort at age `a`
contributes half its productivity while `a < RAMP_j/2` and full afterwards.
Ramp periods (months), chosen inside the reply's bands: senior executive 15
(mid of 12–18), junior manager 9 (mid of 6–12), experienced supervisor 4.5
(mid of 3–6), inexperienced supervisor 6 (mid of 3–6), experienced employee 3
(top of 1–3, network-dependent), inexperienced employee 3, administrative
clerk 3. The ramp loss shows up in the cumulative productivity gap: at 18%
churn it is ~1.7 fraction·months over 2 years, and the no-external-recruiting
scenario of task 5 shows vacancies plus ramp loss together. Interval of
validity: reply is a generic-practice judgment; the half-productivity-for-the-
first-half rule is used verbatim as the cohort productivity schedule.

## No-exchange parameter decisions (from the task's own data, not the expert)

- Baseline annual churn 18% (problem 7); middle managers (junior manager,
  experienced supervisor, inexperienced supervisor) 36% = 2× company average
  (problem 4).
- 370 seats, level sizes, recruiting costs/times, salaries, training costs:
  Table 1 (`data/table1.csv`).
- HR hiring capacity: 9%/year of seats (midpoint of the problem's stated
  8–10%, which covers about two-thirds of churn-created vacancies at 18%).
- Initial fill 365/370 = 0.986 (85% × 370 = 314.5 is the *current average*
  fill; the simulation starts from a fully staffed book so that churn,
  not the initial deficit, drives the dynamics).
