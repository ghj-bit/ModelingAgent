# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence

## Exchange 1

**Question (exchange 1, before the churn-dynamics and budget modeling it governs):**
"Is one person's quitting usually followed by others around them quitting?"

**Expert reply (summary of the substance):** Yes, turnover clusters: a close
peer's quitting raises the nearby coworker's quit hazard, on the order of a
1.2–1.5× increase over the following months, strongest for similar work,
shared supervisor or small team; strengthened by shared dissatisfaction, dense
ties and visible successful exits; weakened by cohesion, management response
and rapid backfilling. Partial and conditional, not a guaranteed cascade.

**How the reply became work (calibrated parameters, source: exchange 1):**
- Contagion multiplier on quit hazard of exposed employees: λ_c ∈ [1.2, 1.5],
  point estimate 1.35. Implemented in `code/model.py` as
  `contagion_hazard(rates, share_exposed, lam) = rates * (1 + share_exposed*(lam-1))`,
  interval of validity: over the following months after a peer exit, for close
  ties (same team/supervisor).
- Exposed-share of staff: 0.30 (assumption, swept 0.15–0.5); sensitivity run
  `--sweep SHARE_EXPOSED=0.15,0.3,0.5` (2-yr total talent-mgmt budget 330.5–349.6 σ,
  i.e. ±6% — conclusion robust).
- "Weakened by rapid backfilling" → the backfill pipeline (recruitment delay
  TRE_i per level) is kept in the model; fast backfill shrinks the exposed
  window.

## Exchange 2

**Question (exchange 2, building on exchange 1 — the structural assumption of
the backfill/budget model):** "If a manager quits, do you usually fill the post
with a new hire from outside?"

**Expert reply (summary of the substance):** No — managerial vacancies are
filled by internal promotion first; external recruitment is the exception, a
minority of such openings. Drivers: ICM's own promotion rules requiring years
of experience at specific levels (task issue 6), and external managerial
recruitment being slow and expensive.

**How the reply became work (decision rule, source: exchange 2):**
- Default backfill policy in the model changed from external to
  `fill="internal"`: 50% of a managerial vacancy (levels 1–6) is promoted from
  the level below with no delay (promoted worker is assumed already
  qualified — consistent with the experience rules); the remaining 50% is
  externally hired after the level's median recruitment delay. Level 0 has no
  level below, so it is external-only. Implemented in `simulate()` and
  `steady_open_vacancies()` of `code/model.py`.
- Consequence for results: steady-state fill ratio at 18% churn improves from
  0.951 (external default) to 0.974; 2-yr talent-management budget at 18%
  falls from 340.1 σ to 300.1 σ (28.9% of the annual wage bill); T5
  "internal promotion only" scenario now matches the company's actual
  operating default.
- The external-recruiting and no-recruiting variants are retained as
  sensitivity scenarios (t4_25pct, t4_35pct external; t4_*_norecruit).

## Exchange 3

**Question (exchange 3, interpretation context for the 80%-fill question):**
"At what share of open jobs would ICM start to fail customers or miss
deadlines?"

**Expert reply (summary of the substance):** No clean threshold. ICM runs at
~85% filled today and functions. Such organizations generally tolerate
roughly 10–20% vacancy (slack, overtime, informal coverage absorb it);
customer-facing failure and missed deadlines typically appear around 20–30%
unfilled (~75–110 open posts) and become severe beyond ~30–35%. Two
qualifications: which positions are open (vacancies concentrated in
mid-level supervisors/managers hurt far more than the same count spread over
lower levels) and duration (sustained vacancies past the recruitment lead time
erode capacity cumulatively; brief spikes are absorbed).

**How the reply became work (decision-relevant threshold, source: exchange
3):**
- Decision rule for judging the 80%-fill question: the task's 80% full-status
  target (20% vacancy) sits at the top edge of the tolerable band; results
  between 20% and 30% vacancy are reported as "operationally strained,
  delivery at risk", above ~30–35% as "severe breakdown". A scenario that
  ends two years below 80% fill is judged NOT sustainable, and the verdict is
  qualified by the concentration/duration caveats.
- Applied: T4 25% churn with external recruiting ends at ~6.8% vacancy (fine);
  no-external-recruiting variants accumulate 151 and 192 open posts (41–52%
  vacancy) — deep in the severe zone, and the loss is concentrated in the
  high-turnover middle levels, so it is judged unsustainable on both the
  threshold and the concentration caveats. T5 no-external ends at ~30%
  vacancy concentrated in managers/supervisors — borderline severe; reported
  as "delivery at risk, middle-management layer degrading" rather than a
  simple pass.
