# Interaction Evidence — Task 2015_C (ICM Human Capital Network)

Ten expert exchanges, one question each. Each reply is converted into a model
parameter, constraint, or structural decision below. Values are my own
formulation; the reply is input, not content.

## Exchange 1 — Productivity cost of a vacant seat
- Q: In a factory or service company, if a job stays empty for a month, roughly
  what fraction of that job's output is lost?
- Reply (gist): a vacancy loses ~100% of the position's monthly output (~8% of
  annual). Coworker absorption and backlog buffers reduce the *organizational*
  net loss, sometimes to well under half.
- Used as: base productivity-loss coefficient per vacant position-month =
  1.0 (position weight). Absorption modifier applied: net organizational loss
  = 0.5 × nominal when work is absorbable (front-line), 1.0 when not
  (management). Parameter `absorb_frontline = 0.5`, `absorb_mgmt = 1.0`.
  Validity: per-month granularity, steady-state staffing.

## Exchange 2 — Churn diffusion mechanism
- Q: When one person quits, is the next likely quitter close to them or anywhere?
- Reply (gist): close to them, within the same team/immediate work group.
  Direct social ties carry the influence; probability decays sharply with
  network distance; company-wide effect is diluted.
- Used as: churn is an SIS-style contagion on a locally-connected (community)
  network, NOT a global i.i.d. Poisson process. Each node's hazard is
  amplified by the fraction of *direct* neighbors who recently left:
  `hazard_i = base_rate * (1 + beta * n_left_direct_neighbors / n_neighbors)`.
  Structure: 7 level-nodes with intra-community ties and a few inter-level
  edges; diffusion weight `beta` calibrated (see parameter table). This
  replaces the naive "everyone leaves at the same rate" assumption.

## Exchange 3 — Onboarding ramp
- Q: How many months after starting does a new employee reach full productivity?
- Reply (gist): skilled role ~6–12 months, ~50% output within first 1–3 months;
  routine roles weeks to ~3 months; senior/specialized 12–24 months.
- Used as: hire-productivity ramp function by level. Ramp months
  `ramp = {clerk:2, inex_emp:3, exp_emp:6, inex_sup:9, exp_sup:12,
  jr_mgr:12, sr_mgr:18}`. Output multiplier for a hire of age a months:
  `min(1, a/ramp)`, with a fast start (50% by month 1–3) folded into the
  linear ramp for simplicity. This lowers effective output during the first
  year after any refill, and raises the cost of high churn.

## Exchange 4 — Indirect churn effects on remaining staff
- Q: Beyond the empty seat, what does high turnover do to remaining staff?
- Reply (gist): workload/overtime → burnout → more quitting (reinforcing loop);
  lost tacit knowledge; eroded trust/ties; broken mentoring; lower morale.
  Net cost larger than vacancies alone.
- Used as: a global morale/stress feedback term. When fill rate falls below
  target, a stress multiplier `1 + gamma*(deficit)` raises base churn for all
  levels (the reinforcing loop). `gamma` calibrated. Also a one-time
  "knowledge loss" penalty proportional to the number of experienced
  (tenure>2yr) leavers.

## Exchange 5 — Promotion tenure requirement
- Q: Before promotion up a level, how long must someone have worked in the
  current role?
- Reply (gist): ~2–4 years (commonly 3); mid-level 3–5 yrs; senior 5+; also
  requires an open higher position (vacancy-gated).
- Used as: promotion eligibility = tenure_in_level >= T_prom(level) AND a
  vacancy exists at the higher level. `T_prom = {inex_emp->exp_emp:2,
  exp_emp->inex_sup:3, inex_sup->exp_sup:3, exp_sup->jr_mgr:4,
  jr_mgr->sr_mgr:5}`. In task 5's "promote only qualified employees" scenario
  the vacancy-gating is the binding constraint: with 30% mid-level churn the
  qualified-pool is too small to backfill, so vacancies persist.

## Exchange 6 — Vacancy fill dynamics
- Q: If ICM can only fill two-thirds of open positions by hiring, how long do
  the rest stay empty?
- Reply (gist): no fixed duration — the unfilled third persists indefinitely as
  a standing structural gap (~85% fill is the equilibrium), not a temporary
  delay.
- Used as: hiring backfills a fixed fraction (2/3) of churn-driven vacancies
  each year; the remaining 1/3 is a chronic structural vacancy that does not
  auto-fill. This is why ICM sits at ~85% fill and why higher churn cannot be
  fully absorbed by recruiting. Equilibrium fill ≈ 85%.

## Exchange 7 — Middle-manager retention lever
- Q: Middle managers feel stuck and quit for better jobs. What would keep them,
  aside from a raise?
- Reply (gist): the decisive lever is perceived opportunity to advance —
  credible promotion path, lateral moves, stretch assignments — not pay.
- Used as: mid-level base churn is reduced by a "path-up" factor when
  promotion openings exist. `mid_churn_mult = 1/(1 + 0.3*P_prom_available)`.
  Explains why mid-level churn (2× average) is a *structural* problem: it is
  driven by blocked advancement, not salary, so a pay increase would not fix it.

## Exchange 8 — Edge case: management layer breaks first
- Q: If middle managers keep leaving faster than replaced, what breaks first?
- Reply (gist): the management layer's ability to supervise and reproduce
  itself — widened spans of control, loss of the senior-manager pipeline,
  degraded front-line supervision (reinforcing loop), severed information
  flow.
- Used as: a supervisory-capacity constraint. Effective front-line
  productivity is capped by the number of experienced supervisors present:
  `frontline_productivity_cap = min(1, n_exp_sup_present / n_exp_sup_normal)`.
  When mid-level churn outpaces replacement, the org's output falls faster
  than the raw vacancy count predicts — this is the "breaks first" mechanism.

## Exchange 9 — Most important informal network layer
- Q: Which informal network matters most for who stays?
- Reply (gist): trust ties most for retention; communication/who-talks-to-whom
  strongest for churn diffusion; friendship a weaker overlapping signal.
- Used as: the multilayer network design (task 6). Retention layer = trust;
  churn-diffusion layer = communication/influence; the HR office leads by
  coupling the churn (influence) layer to the trust layer so retention
  interventions target the right ties. This maps the Kivelä et al. multilayer
  framework onto the specific retention mechanism.

## Exchange 10 — Quality issue (keeping marginal employees)
- Q: Keeping underperformers to avoid hiring — help or hurt?
- Reply (gist): usually hurts — work shifts to others (burnout loop), standards
  and morale erode, best people leave first, supervision cost rises, the seat
  is blocked from a better candidate. A short-term necessity, but a standing
  policy that lowers output and raises churn.
- Used as: a quality drift term. Retaining marginal (low-rated) employees
  raises base churn for high performers (best exit first) by
  `delta_churn_high = 0.02 * fraction_marginal_retained`. This is the model's
  formalization of issue #8 and the reason "no firings" is not a stable
  policy.

## Parameter provenance table
| name | value | interval | source |
|---|---|---|---|
| sigma | 1.0 (median salary = experienced-employee salary) | — | dataset table1.csv (computed) |
| base churn non-mid | 0.18/yr | [0.15,0.20] | dataset (task statement issue 7) |
| base churn mid-level | 0.36/yr (2× avg) | [0.30,0.40] | dataset (issue 4) |
| vacancy monthly output loss | 1.0 × position weight | [0.5,1.0] | exchange 1 |
| absorption modifier (front-line) | 0.5 | [0.3,0.7] | exchange 1 |
| absorption modifier (mgmt) | 1.0 | [0.8,1.0] | exchange 1 |
| churn diffusion beta | 1.5 | [1.0,2.0] | exchange 2 (mechanism) + calibration |
| hire ramp months (by level) | 2–18 | [1,24] | exchange 3 |
| stress feedback gamma | 0.5 | [0.3,0.8] | exchange 4 |
| promotion tenure T_prom (yrs) | 2–5 by level | [1,5] | exchange 5 |
| hire fill fraction of churn | 2/3 | [0.6,0.7] | dataset (issue 5) + exchange 6 |
| equilibrium fill | 0.85 | [0.83,0.87] | dataset (issue 5) + exchange 6 |
| path-up retention factor | 0.3 | [0.2,0.4] | exchange 7 |
| frontline productivity cap | n_exp_sup/n_exp_sup_normal | [0,1] | exchange 8 |
| marginal-retention churn drag | 0.02 | [0.01,0.03] | exchange 10 |
| recruiting cost (by level) | 0.1–1.2 σ | — | dataset table1.csv |
| training cost (by level) | 0.05–0.6 σ | — | dataset table1.csv |

All other numbers (headcounts, salaries, recruiting times) are from
table1.csv directly.
