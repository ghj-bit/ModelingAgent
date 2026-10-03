# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert interaction evidence — problem 2015_C

Ten exchanges, one question each. Questions and replies are stored verbatim in
`logs/operator_feedback/expert_question_N.md` / `expert_reply_N.json`; for each
exchange this file records the question, a short summary of the reply, and the
concrete change the reply forced in the model (parameter, equation, or scenario).
No reply text was copied into the submission; only values, ranges and rules
travelled into `results/solution.json`.

## Exchange 1
- **Question:** Is the 18% annual churn the same at every level, or do middle managers turn over faster?
- **Reply (summary):** 18% is the company-wide average; middle-manager bands churn at roughly twice the average (~36%/yr), the remaining levels well below 18% (~9–12%/yr).
- **Effect on work:** Set per-level churn: 36%/yr for junior managers, experienced and inexperienced supervisors; 12%/yr for all other bands so the headcount-weighted mean is exactly 18% (`calibrate_churn` in `code/model.py`, verified by the `other_frac` assertion). Drives every departure count in tasks 1, 3 and 4.

## Exchange 2
- **Question:** When a key employee quits, do coworkers' quitting chances rise right away, or after several months?
- **Reply (summary):** Risk rises with a lag — the elevated hazard is concentrated in the first ~6–12 months after the departure and then decays; the effect is social contagion, not instant.
- **Effect on work:** Churn contagion implemented as a lagged, decaying hazard add-on: each teammate who quit in the window [t−12, t−6] months raises the position's annual hazard by k/span (cont_lag=6, cont_decay=12). Without this exchange the model would have used synchronous contagion.

## Exchange 3
- **Question:** What fraction of a fully productive employee's output does a new hire typically reach in their first year?
- **Reply (summary):** Roughly 50–75% company-wide: routine roles near 70–80%, complex/management roles near 40–60% (full productivity 1–2 years).
- **Effect on work:** Productivity ramp: staff bands start at 0.70 and reach 1.0 over 12 months; management starts at 0.50 over 18 months (`prod_staff/ramp_staff/prod_mgr/ramp_mgr`). Sets the onboarding component of the productivity loss in tasks 2, 4 and 5.

## Exchange 4
- **Question:** When an employee quits, how much of their institutional knowledge is usually lost for good?
- **Reply (summary):** Not a fixed fraction: routine/documented roles lose a small minority (order 10–25%); relationship- and network-embedded roles (managers, long-tenured staff) lose the majority (commonly ~half or more), unrecoverable by handover.
- **Effect on work:** Knowledge-loss constants 0.20 (routine) and 0.60 (managerial) in the parameter table; the loss is represented through the persistent vacancy effect plus the span-of-control penalty rather than as a tracked stock (no knowledge data exist), and stated as a limitation in task 2.

## Exchange 5
- **Question:** How many months does it take a manager to fill an internal vacancy after it opens?
- **Reply (summary):** Typically 2–4 months for internal vacancies (posting ~1 month, selection ~1–2, transition ~1), longer (4–6) for senior/hard-to-fill posts.
- **Effect on work:** Internal promotion fill time set to 3 months (`internal_fill = 3.0`); external fills wait until the vacancy age reaches the band's median recruiting time from Table 1 (1–7 months). This lag is what makes the fill ratio drift instead of snapping back in tasks 4–5.

## Exchange 6
- **Question:** If middle management churns and vacancies go unfilled, what usually suffers first?
- **Reply (summary):** The work the managers did, not the org chart: supervision/coordination of direct reports first, then decision throughput, then training/mentoring/onboarding, then cross-team communication — i.e. people-management functions degrade before measurable output does, with a lag.
- **Effect on work:** Added the supervision channel: any team whose supervisor post is vacant loses 10% of output (`supervision_loss = 0.10`); this is the model's mechanism for the "indirect effects" in tasks 2 and 4 and explains why middle-band fill (not total fill) is the early-warning variable.

## Exchange 7
- **Question:** Can a 370-person company absorb 25% annual quits while keeping at least 80% of posts filled?
- **Reply (summary):** No at 25%, certainly not at 35%: ~90+ exits/yr at 25% exceed realistic replacement throughput (recruiting takes months, only ~2/3 of vacancies actively hired), so the filled fraction drifts below 80% and keeps falling; the binding constraint is replacement throughput, not willingness to hire.
- **Effect on work:** Validated the 30/yr hiring cap (8–10% of 370) as the binding constraint and the simulation's fill-ratio answers in task 4 (25% → ~70% final fill, 35% → ~62%) as the model counterpart of this judgment; the "cannot sustain 80%" conclusion in task 4 cites both.

## Exchange 8
- **Question:** When a company stops external hiring and fills posts only with internal promotions, what breaks first?
- **Reply (summary):** The bottom of the pipeline: the entry-level base empties first (no intake), then promotion eligibility dries up (years-at-level rules), then span-of-control/supervision collapse, plus promotion beyond readiness.
- **Effect on work:** Structured the task-5 scenario mechanics: promotions are zero-sum — filling a destination post opens the source post, so the vacancy propagates down a band (`pos_level` reassignment in the promotion step), which is exactly why the entry bands and the middle both lose fill in the task-5 run, and why the promotion rate collapses by year two.

## Exchange 9
- **Question:** Does quitting usually spread fastest among same-team coworkers, or across the whole company?
- **Reply (summary):** Fastest within the same team; the effect weakens sharply with social distance (same-team > same-department > same-company); influence should be weighted by network proximity, not a single company-wide rate.
- **Effect on work:** Contagion is computed per supervision team (the model's social unit), with the hazard scaled by 1/span rather than by team size; this is the network-model justification for building the Human Capital network at all (task 1) and the prior for the supervision-layer contagion weight in the multilayer extension (task 6).

## Exchange 10
- **Question:** In a company that keeps marginal employees to avoid vacancies, what does the workforce slowly become?
- **Reply (summary):** Adverse-selected and low-performing: capable, mobile people churn while marginal people stay for full careers, so the mix shifts to lower quality and compounds; high performers are demoralized and the internal talent pool thins.
- **Effect on work:** Added the quality-drift factor (1 − 0.005)^{years}, active in the no-external-hiring scenario, and the "pipeline starvation" interpretation of task 5 (eligible pool for the 3-year rule shrinks each year); stated as the adverse-selection limitation in tasks 4 and 5.

## How the exchanges were used overall
Exchanges 1–3 and 5 fixed the model's rates and lags; 2 and 9 fixed its network
structure (team-local, lagged contagion); 4 and 6 fixed the productivity/indirect
channel; 7–8 validated the throughput bottleneck and the zero-sum promotion
mechanics used in task 5; 10 added the quality-drift term. Every empirical value
carried into `results/solution.json` is listed in the parameter table of task 1
with its exchange as source and the interval over which the judgment holds.
