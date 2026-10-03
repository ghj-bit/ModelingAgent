# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — ICM Human Capital Churn (MM-Bench 2015_C)

Ten expert exchanges, one question each. Question files: `logs/operator_feedback/expert_question_N.md`;
replies: `expert_reply_N.json`. The model consumes the values below as calibrated inputs
(recorded in `code/model.py` as the `PARAMS` table) and as structural assumptions.
No reply text is copied into the submission; only values, constraints and mechanisms travel.

## Exchange 1 — churn contagion magnitude and window
- **Question:** How often does a close colleague of a quitting worker also quit within six months; is it above chance?
- **Reply (summary):** Not observable from the dataset (no tie or departure-timing data). Empirical norm: elevated
  quit risk among socially close coworkers, roughly 1.5×–3× baseline in the months after a colleague departs.
- **Use in model:** contagion hazard multiplier HZ = 2.0, interval [1.5, 3.0]; window = 0.5 y, interval [0.3, 0.8]
  (agent-based diffusion study, `diffusion_study()`). Sensitivity: `--sweep HZ=1.5,2.0,2.5,3.0` gives excess
  departures of 15.9 / 31.3 / 45.8 / 58.1 over 2 years (28–103% above no-contagion baseline).

## Exchange 2 — new-hire productivity ramp
- **Question:** Is a replacement productive from day one, or does it take months?
- **Reply (summary):** Not day-one; roughly 3–6 months to full proficiency for most positions, 6–12+ months for
  higher-level roles; output starts at a fraction and climbs.
- **Use in model:** ramp time 0.25 y (front line) / 0.5 y (managers), intervals [0.25, 0.5] / [0.5, 1.0];
  productivity of a new hire at arrival = 0.30 (fraction), interval [0.2, 0.5]. Implemented as an exponential
  ramp in `run_scenario()` (`new_cohort`, `RAMP`).

## Exchange 3 — vacancy fill route
- **Question:** When a junior manager quits, is the seat filled by promotion, external hire, or left empty?
- **Reply (summary):** Promotion from below is the usual first choice but cascades downward; seats are vacant for a
  period in any case (slow recruiting, 85% fill norm); external hire is least common for mid-level slots.
- **Use in model:** backfill rule in `run_scenario()`: 40% of each vacancy targeted by internal promotion from the
  level directly below (promotions consume source seats, so the vacancy propagates downward), 60% by external
  recruitment; promotion only after a 0.1-y vacancy lag (the "seat vacant for a period" gap). Promotion share
  0.40, interval [0.3, 0.5].

## Exchange 4 — where the work is produced
- **Question:** Which level produces the most work: executives, middle managers, or front-line experienced employees?
- **Reply (summary):** Front-line experienced employees, in aggregate — headcount dominates; managers enable but
  contribute far less direct output.
- **Use in model:** per-level productivity weights PROD = (SM 0.05, JM 0.15, ES 0.20, IS 0.25, EE 0.55,
  IE 0.50, AC 0.18), normalized to 1.0; the two employee levels carry 105% of output weight. This is the
  "direct effect on productivity" channel: filled seats weighted by these factors, discounted by ramp state.

## Exchange 5 — promotion eligibility tenure
- **Question:** How many years at a level before promotion?
- **Reply (summary):** No datum; typical minimum on the order of 2–4 years, central value ~3.
- **Use in model:** promotion eligibility = 3.0 y at a level, interval [2, 4]; steady-state qualified fraction at
  level i = exp(−3·r_i) (survival of the sojourn time beyond 3 years); under the qualified-only policy this
  fraction gates promotion flow. A 1-promotion-per-year cap per mid level encodes the small qualified pool
  (25–30 seats × exp(−3·0.36) ≈ 4–7 eligible).

## Exchange 6 — external hiring time by level
- **Question:** How long to hire an experienced worker externally versus an entry-level clerk?
- **Reply (summary):** Scales strongly with level: entry 2–6 weeks; experienced front line 1–3 months; mid-level
  3–6 months; senior 6–12 months. Consistent with the provided data — use table1.csv values.
- **Use in model:** confirms table1.csv median time-to-recruit (1–7 months) as the hiring pipeline duration
  `T_REC`; no separate parameter needed. Pipeline carries dep·T_REC in-flight orders at steady state.

## Exchange 7 — cross-department acquaintance
- **Question:** Do middle managers/supervisors know each other well across departments, or only their own group?
- **Reply (summary):** Mostly only their own group: dense intra-group clusters connected by a thin cross-group web
  at management level.
- **Use in model:** network structure of the diffusion study: 10 clusters of 19 nodes with intra-cluster ER
  density 0.6 (interval [0.4, 0.8]); 50 manager nodes get 2 cross-cluster links each (inter-group links = 10% of
  intra-group scale, interval [0.05, 0.2]). Contagion therefore spreads fast within a team and slow across teams.

## Exchange 8 — team rotation
- **Question:** Do experienced employees/supervisors stay on one team long-term or rotate every year or two?
- **Reply (summary):** Mostly one team long-term; rotation is the exception.
- **Use in model:** network is stable over the 2-y horizon; a small random edge reassignment (annual
  probability 0.1, interval [0.05, 0.2]) represents occasional reassignment. Churn diffusion propagates through a
  roughly fixed structure.

## Exchange 9 — speed of noticing a departure
- **Question:** Do coworkers notice a departure within days or weeks?
- **Reply (summary):** Social notice within days (drives contagion onset); functional/operational impact surfaces
  over weeks to months as backlog and overload.
- **Use in model:** contagion applied with a 0.02-y (≈1-day) notice delay, interval [0, 0.1]; the slow operational
  side is the ramp + vacancy period in the level model, not the network study.

## Exchange 10 — reports following a departing manager
- **Question:** When a junior manager quits, do several direct reports leave with him within a year?
- **Reply (summary):** Mostly they stay; a modest temporary hazard increase (one, occasionally two or three follow
  within a year).
- **Use in model:** manager-departure effect in the diffusion study: neighbours in non-manager nodes get hazard
  multiplier 1.5 (interval [1.2, 2.0]) for 1.0 y (interval [0.6, 1.5]) after a manager departs — an effect
  distinct from, and weaker than, the close-tie contagion (×2.0 for 0.5 y).

## Data note
`data/table1.csv` arrived with the σ column mojibake'd (`σ` mis-encoded as `a6 d2` = CP1252). The bytes decode
cleanly to σ, so no numeric repair was needed: salaries, training and recruitment costs are read directly in σ
units (median income σ = 1.0 by definition). Headcounts sum to 370 as stated.
