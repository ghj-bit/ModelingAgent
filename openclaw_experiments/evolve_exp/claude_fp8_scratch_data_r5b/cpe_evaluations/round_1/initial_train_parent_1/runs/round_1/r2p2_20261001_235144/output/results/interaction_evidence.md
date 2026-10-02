# Expert Interaction Evidence — Task 2015_C (ICM Human Capital / Churn)

Three exchanges, one question each, in order. Each reply was converted into a
concrete model element before the next exchange.

---

## Exchange 1

**Question** (`expert_question_1.md`):
> In a real company like this, if the departure rate suddenly doubles, do more
> people start leaving because of it, or does the rate stay roughly flat?

**Reply** (`expert_reply_1.json`), condensed:
More people start leaving — the rate does not stay flat. Churn is
self-reinforcing through the network mechanism the problem describes (issue 2):
a worker connected to former employees who have churned is more likely to churn;
a departure removes a stabilizing tie and exposes that person's contacts to the
churn "signal." Two bounds: the amplification is **strongest in the first wave
or two and then saturates** (the pool of still-connected, still-dissatisfied
employees shrinks and HR responds), and it is **concentrated in the mid-level
manager/supervisor tiers**, which already run at ~2× the company average.
Expect a genuine upward cascade over the following months, not an indefinite
doubling — but a flat rate is not realistic.

**How it became work** (constraint entered the model):
- `eff_churn(sc, i, dep_frac)` in `code/model.py` adds an **endogenous churn
  boost** `base_i * (1 + CASCADE * w_i * S(dep_frac))` where
  `S = dep_frac/(dep_frac + k)` is a **saturation** function of the cumulative
  departure fraction (so the cascade strengthens then plateaus — "saturates over
  the first wave or two"), and `w_i` weights the **three middle tiers** most
  heavily ("concentrated in the mid tiers").
- Parameter `CASCADE` (amplification strength) is swept
  (`--sweep CASCADE=0,0.15,0.3,0.6,1.0`): raising it increases annual
  departures (131 → 145 over 2 yr) but is damped because external hiring is
  capacity-limited, consistent with the expert's "upward cascade … then
  saturates." Source: **expert exchange 1, 2026-10-01**.

---

## Exchange 2

**Question** (`expert_question_2.md`):
> If a company suddenly needs to hire for far more open seats than usual, does
> it realistically scale up external hiring to fill them quickly, or is external
> hiring stuck at a near-fixed small pace?

**Reply** (`expert_reply_2.json`), condensed:
External hiring is stuck at a near-fixed small pace — it does not scale up
quickly. Binding constraints are real and slow: recruiting lead times (the table's
median time-to-recruit runs on the order of months per position), limited
HR/recruiting capacity, budget, and the scarcity of qualified mid-level/management
candidates. The problem statement reflects this: ICM is actively hiring only
about 8–10% of positions (≈2/3 of current vacancies) despite carrying ~15%
vacancies, citing "administrative delays and office capacity." So when open seats
spike, the realistic response is a modest, gradual increase — not a proportional
jump. **Vacancies therefore accumulate and persist; high churn cannot be offset
by simply hiring faster.**

**How it became work** (constraint entered the model):
- External hiring is modelled as a **fixed annual throughput**
  `hr_hire_share * 370` people/yr that does **not scale with the vacancy spike**
  (the `ext_cap_step` in the backfill loop; whatever the fixed capacity cannot
  absorb that step stays a vacancy and accumulates).
- This is the **binding constraint** that produces the task-4 answer: at 25% and
  35% churn the external demand exceeds the fixed ceiling, so the maximum
  sustainably-holdable fill drops (fixed point: 25% → 68.0%, 35% → 47.6%),
  i.e. ICM **cannot** hold 80% at those rates. Source: **expert exchange 2,
  2026-10-01**.

---

## Exchange 3

**Question** (`expert_question_3.md`):
> When an experienced worker quits, roughly how long until a full replacement
> restores the same output, and does the lost experience hurt the whole team?

**Reply** (`expert_reply_3.json`), condensed:
A full replacement typically takes **on the order of several months to a year**
to reach the departed worker's output — the recruiting lead time (months) plus
onboarding and ramp-up. For experienced/mid-level roles expect roughly **6–12
months** to full productivity; junior roles shorter, senior/managerial longer.
Yes, the lost experience hurts the **whole team**, not just the vacated seat:
the departing person carried informal knowledge, contacts, and coordination that
others relied on, so their absence degrades team output and can slow or
destabilize peers (and, per the problem's own mechanism, raises their contacts'
churn risk). The team-level dip is real and often **exceeds the individual output
gap**, though it is largest in the first months and **partially recovers** as the
replacement and remaining members adapt.

**How it became work** (calibration entered the model):
- `ramp_months(i)` in `code/model.py` = the level's median time-to-recruit (from
  `table1.csv`) **plus an onboarding ramp of 6 months (9 for mid-level &
  senior)**, implementing "6–12 months to full productivity for experienced /
  mid-level roles."
- `productivity(sc, N, ramped)` multiplies a **vacancy loss** (unfilled seats
  produce nothing) by a **ramp loss** (a seat just refilled produces at partial
  rate until `ramp_months(i)` elapse; recent additions count at half credit —
  "front-loaded dip, partially recovers"). The integrated area
  `(1 - productivity) * salary-weighted seats * dt` is reported as
  `lost_productivity` (sigma-equivalent), the **indirect productivity cost** of
  churn required by tasks 2 and 4.
- The team-level amplification ("hurts the whole team … exceeds the individual
  gap") is represented by applying the ramp discount to *team* output and is the
  reason the productivity loss (~192–246 σ over 2 yr) exceeds the raw
  vacancy-value loss. Source: **expert exchange 3, 2026-10-01**.

---

## Summary of model elements sourced to each exchange

| Exchange | Model element | File / function |
|---|---|---|
| 1 | Endogenous, saturating, mid-tier-weighted churn cascade | `eff_churn`, param `CASCADE` |
| 2 | Fixed (non-scaling) external-hiring ceiling → task-4 sustainability | `ext_cap_step`, `sustainable_fill` |
| 3 | Ramp-up time (6–12 mo) + team productivity loss | `ramp_months`, `productivity`, `lost_productivity` |

All three replies were used as **calibrated inputs / constraints**, not as
content. No reply text is copied into `solution.json`; the values, constraints,
and equations above are in the model's own formulation.
