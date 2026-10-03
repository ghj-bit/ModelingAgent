# Expert Interaction Evidence — Task 2015_C (ICM human capital / churn)

Policy: 10 exchanges, one question each, all qualitative real-world questions.
Each section: question, expert reply (abridged), and the concrete work the reply
drove (model constant / equation / decision rule, with the value it supports).

All ten replies were converted into model work before the next exchange;
none was used as prose in the submission.

## Exchange 1 — How departure news spreads
Q: How do employees typically learn that a colleague left the company in a small workplace of a few hundred people?
Reply (abridged): news travels tie-by-tie along informal friendship/work ties; same-team
coworkers and managers know first; word of mouth within days; formal channels
(email, job posting) only confirm what gossip already conveyed; churn clusters among
people connected to the leaver.
Work produced: fixed the churn-contagion mechanism as tie-by-tie diffusion on the
informal tie layer (not firm-wide uniform hazard, not formal announcement):
`S_{i}(t+1) = S_i(t) + (1-S_i(t)) * min(1, p_c * (# churning contacts of i in last 3 months))`
with S_i a cumulative dissatisfaction state, and the edge set = the 20% densest
intra-level informal ties (see model). Source of mechanism: this exchange.

## Exchange 2 — Lag from a colleague's departure to one's own exit thoughts
Q: When one person leaves a job, how long until coworkers typically start thinking of leaving too, if they do?
Reply (abridged): no fixed lag; variable; the relevant window is weeks to a few months
for the minority who are influenced; effect concentrated in close ties and already-
dissatisfied people; a single departure often produces no effect.
Work produced: chose the 3-month (0.25 yr) recall window in the contagion term above
and decayed the influence of a departure after it (window, not permanent memory):
departures older than 3 months stop contributing to the contagion count. Range
supported: 1–6 months; model value 3 months. Source: this exchange.

## Exchange 3 — What happens to coworkers when a non-manager leaves
Q: When one person leaves a job, do remaining coworkers usually stay with the same manager or get reassigned elsewhere?
Reply (abridged): default is continuity — same manager keeps the team; the vacancy is
backfilled after a delay or duties are absorbed by the existing team; reassignment
only when the leaver was the manager, a team is restructured, or a promotion fills
the slot.
Work produced: structural decision rule for the simulator: non-manager departures
leave the reporting layer untouched; workload redistribution and vacancy tracking
happen within the same team (vacancy queue with level-specific median fill times
from table1.csv). No re-edges in the reporting layer except for manager nodes.

## Exchange 4 — Acting coverage when a supervisor/manager leaves
Q: When a supervisor or manager leaves, do their direct reports typically keep working for the acting boss in the meantime?
Reply (abridged): yes — reports keep their reporting line, pointed at an acting/interim
boss (peer supervisor, level-up manager, or senior team member) for weeks to several
months, matching slow recruiting; the interim boss's span of control grows.
Work produced: manager-vacancy rule: the supervisor's children are re-attached to
the manager's own parent node (span-of-control growth), not dissolved or deleted;
they return to a new child once backfilled. This is how the "churned-manager"
state of the org graph is represented between departure and refill.

## Exchange 5 — Productivity ramp of a new hire
Q: How long does a freshly hired new employee usually take before they work as productively as an experienced one?
Reply (abridged): role-dependent: simple/routine roles ~1–3 months; skilled individual
contributors ~3–6 months; managerial roles ~6–12 months; internal promotions ramp
faster than external hires; ramps are slower where the role is relationship/tacit-
knowledge based.
Work produced: per-level productivity ramp constant r in the output equation
P(t) = P0 * Σ_j e_j(t) * (1 - exp(-age_j / r_level)):
inexperienced employee and clerical 0.25 yr; experienced employee 0.5 yr;
inexperienced and experienced supervisors 0.5 yr; junior manager 1.0 yr;
senior manager 1.0 yr. Internal promotions ramp 50% faster (r/2). Values are
central points of the stated ranges. Source: this exchange.

## Exchange 6 — When coworkers feel the workload gap
Q: When a key person quits, how quickly do coworkers typically notice their extra workload?
Reply (abridged): noticing is near-immediate (days, often the first days); what lags is
the response (weeks–months); strain is immediate and persists during the vacancy;
intensity depends on how critical the role was.
Work produced: the productivity-loss term in the vacancy equation is applied from
day 0 of a vacancy (no lag):
P(t) = P0 * [1 - Σ_levels δ_level * V_level(t)/N_level], δ = 0.5 * (vacancy effect
halves the marginal output of the absorbing coworker's share, consistent with
"duties absorbed at reduced efficiency"); persistence matches the vacancy duration.

## Exchange 7 — Who covers a long-open manager vacancy
Q: When a manager vacancy sits open for months, who usually covers the role day to day during that time?
Reply (abridged): an acting/interim arrangement always in practice: a peer absorbs the
duties, the level-up manager takes direct oversight (temporary flattening), or a
senior team member is tapped; the stretched actor and reduced managerial attention
are the main costs.
Work produced: operationalized as the same rule as exchange 4 plus a secondary cost:
while a manager seat is open, its team's satisfaction drift rises by an extra
δ_span = 0.02/yr (stretched acting boss, less managerial attention) — folded into
the dissatisfaction accumulation equation as the "management-attention" term.

## Exchange 8 — Do evaluations drive promotions?
Q: Do the annual performance evaluations tend to lead to promotions within the company, or are people rarely promoted?
Reply (abridged): evaluations mostly drive pay/retention/documentation; promotion is
gated by vacancy availability and tenure/experience rules, not rating; for ICM the
problem statement says ratings are unused by HR and advancement needs several years
at specific levels, so promotions are rare and slow.
Work produced: promotion decision rule: an employee becomes eligible only when
tenure at current level ≥ 3 yr (the "several years" rule) AND the next level has a
vacancy; among eligible candidates, the highest-rated get picked (ratings matter as
eligibility filter among qualified, consistent with the task-5 "promote only
qualified employees" variant). Baseline promotion flow: ≈ 20% of vacancies at
manager/supervisor levels are filled internally (the rest externally) — the
internal-fill fraction f_int = 0.20 is a calibrated parameter (range 10–30%);
senior level 0 (top 10) never gets external-only refill in the baseline because
external executive hiring is rare. Source: this exchange (mechanism) + range assumption noted in the parameter table.

## Exchange 9 — What keeps a good employee from leaving a struggling company
Q: In your experience, what typically stops a good employee from leaving a struggling company: money, recognition, job growth, or something else?
Reply (abridged): no single factor; for good employees the empirical ordering is
growth/advancement first, recognition second, money third (hygiene — a raise alone
seldom retains someone already deciding to go), relationships fourth; for a
struggling firm the binding constraint is perceived growth and stability.
Work produced: retention-lever hierarchy used in the intervention analysis and the
dissatisfaction dynamics: the model's churn sensitivity to growth-opportunity loss
(stalled promotion pipeline, i.e., the tenure gate clogging) is set to dominate its
sensitivity to salary: a vacancy at the level above doubles the churn hazard of
eligible-but-stuck employees (hazard multiplier m_growth = 2.0), while a uniform
10% pay increase cuts baseline hazard by only ~10% (hazard multiplier 0.9),
implementing "pay is hygiene, growth is the lever" as quantitative weights.

## Exchange 10 — Do remaining staff push harder or cut back when churn persists?
Q: When a company keeps struggling and people keep quitting, do the remaining staff usually push harder or start cutting back on effort?
Reply (abridged): both, split by group: a committed core (strongest performers, most
loyal, fewest outside options) pushes harder; a larger group cuts back
(disengagement, presenteeism, quiet job searching); net average effort declines
because the cutback group is larger, and the push-harder group burns out over time.
Work produced: effort function in the productivity equation became state-dependent
rather than constant: e_j(t) = 1 + g * (1 - 2*E_j(t)) where E_j ∈ [0,1] is the
dissatisfaction of the "committed core" share... concretely: average effort
e_avg(t) = 1 - 0.25 * D_avg(t) + 0.10 * D_avg(t)^2, i.e. linearly declining effort
with average dissatisfaction, consistent with "declining average effort" as the
net effect, with the quadratic term capturing that the small committed core adds a
little back early (bump) before net decline; sensitivity analysis sweeps the slope
0.25 over [0.15, 0.35]. Source: this exchange.

---

## Empirical parameter table (provenance for solution.json)

| name | value | interval [a,b] | source |
|---|---|---|---|
| churn-contagion mechanism (tie-by-tie, informal ties) | 20% densest intra-level ties | n/a (structural) | expert exchange 1 |
| contagion recall window | 0.25 yr (3 months) | [0.08, 0.5] yr | expert exchange 2 |
| per-level new-hire productivity ramp r (yr) | 0.25–1.0 by level (table in code) | [0.08,1.0] | expert exchange 5 |
| internal promotion ramp factor | 0.5 (r/2) | n/a | expert exchange 5 |
| internal fill fraction for manager/supervisor vacancies f_int | 0.20 | [0.10, 0.30] | expert exchange 8 (mechanism); range assumption |
| stalled-growth churn hazard multiplier m_growth | 2.0 | [1.5, 3.0] | expert exchange 9 |
| pay-raise hazard cut per 10% pay | 0.9 | [0.85, 0.95] | expert exchange 9 |
| effort slope vs dissatisfaction | 0.25 | [0.15, 0.35] | expert exchange 10 |
| acting-boss span-of-control dissatisfaction drift δ_span | 0.02/yr | [0.01, 0.05]/yr | expert exchange 7 |
| base churn (baseline) | 18%/yr (middle levels 36%/yr) | task statement | task 2015_C problem statement |
| σ = 1 (company median salary, 2019 MM-Bench ICM data) | $75,000 | n/a | MM-Bench 2019 problem set, Table 1 convention (median income of company = σ; dollar figures given in σ units); used only as scale reference — all model outputs reported in σ. |

All other numbers (headcount, salaries, recruiting costs/times, training costs,
fill fractions, churn scenarios) come from table1.csv or the task statement.
