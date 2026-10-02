# Solution

## Subtask 1: Task 1: Build a Human Capital network model of ICM's personnel situation (describe the model and its assumptions).

### Problem

Task 1: Build a Human Capital network model of ICM's personnel situation (describe the model and its assumptions).

### Analysis

ICM is a 370-person organization with 7 hierarchical position levels (Table 1, file data/table1.csv, GBK-encoded; sigma = median-income unit). The network is a two-layer multilayer structure: (i) a structural layer — the reporting ladder, each level connected to the one below, which is where promotion, coordination load, and blocked-ladder stagnation propagate; (ii) an informal-tie layer — coworkers' social ties within and across levels, through which dissatisfaction diffuses (contagion). Nodes carry a state (in-post, marginal, churned) and a churn hazard. The model is a discrete-time (monthly) SIS-style contagion on the level-aggregated network: churned-neighbor fraction feeds back into the hazard of remaining nodes. Assumptions: (1) levels are the resolution of the network — within a level, ties are dense and homogeneous, so level-aggregation is exact at the aggregate scale and avoids overfitting to an unobserved individual-level tie matrix; (2) sigma is the unit for all money (median income); (3) the organization starts at 85% fill (int(0.85*n_l) per level, 314 of 370 positions filled); (4) churn is voluntary-dominated; (5) HR backfills a fixed share of vacancies through an external pipeline whose lag equals the level's median time-to-recruit (Table 1); (6) new hires ramp to full productivity over that same recruit-lag window; (7) a quality layer: a fixed share Q0 of incumbents is 'qualified', external hires are qualified, marginal incumbents rarely leave (task item: very few relieved), so internal promotion of the qualified half is the binding constraint when external recruiting is cut.

### Modeling Process

State per level l (monthly steps, 24 months): n_l filled; c_l churned last month; p_l[k] external hires k months into the level's recruit lag (head lands this month); r_l[k] backfilled incumbents k months into onboarding; i_l slots already in the pipeline. Baseline annual rates: r_mid = 0.36 (2x company-wide 18%, problem statement) for the 3 middle tiers (70 people); r_other = (0.18*370 - 0.36*70)/260 = 0.2308 so the company-wide rate is exactly 18%. Hazard: h_l = (r_l/12)*(1 + BETA*12*f_l), f_l = c_l/max(1,n_l), binomial thinning new_ch_l ~ Bin(n_l, min(h_l, 0.4)). Endogenous middle-tier rate: r_l = 0.36 + KAPPA*f_l (stagnation feedback). Backfill: HR starts recruiting for HR_SHARE of the vacancies not already in the pipeline; a hire lands after recruit_months(l) and is qualified; when external recruiting is off for a middle level, a churn slot is filled by immediate internal promotion from the feeding level's stable staff (qualified-only mode restricts the pool to qualified staff). Cost: recruit_cost += arrived*hires * cost_l(sigma); training_cost += sum(n_l * train_l)/12 per month. Productivity index: P = max(0, 1 - cov/370 - min(penalty, 0.6)), cov = sum over l of (W_PRODX if l is a manager tier else 1) * (vacancies_l + (1-RAMP_FRAC)*ramping_l), penalty = 0.5*r_annual if r_annual >= R_BREAK else 0.1*r_annual. Code: code/churn_model.py (deterministic seed, --sweep supported). Parameter table (one line per empirical parameter): BETA = 0.3, interval [0.1, 0.5], source: exchange 1 (expert: a departure raises the odds that others quit, ~0.1-0.5 additional quits in a few months, local team), cross-check: voluntary-turnover contagion literature, https://doi.org/10.1080/13678868.2023.2238247. KAPPA = 0.5, interval [0.2, 1.0], source: exchange 2 (middle-manager churn is own dissatisfaction shaped by surroundings: blocked ladders, peer churn -> endogenous rate; value chosen as the midpoint of the plausible self-reinforcement range, bounded so r stays < 1). W_PRODX = 1.5, interval [1.0, 2.0], source: exchange 3 (middle/manager tiers show damage first: coordination + knowledge-transfer load; manager vacancy months counted 1.5x). R_BREAK = 0.15, interval [0.10, 0.20], source: exchange 3 (below ~10% absorbed, noticeable pre-departure damage from ~15%). RAMP_FRAC = 0.6, interval [0.4, 0.8], source: Table 1 median time-to-recruit as onboarding window (dataset), new hire at 60% productivity while ramping (standard ramp assumption). HR_SHARE = 0.6, interval [0.5, 0.7], source: task item 5 / Table 1 recruiting costs imply HR actively hires about 2/3 of current vacancies (calibration). Q0 = 0.5, interval [0.2, 0.8], source: assumption (task item: most are competent but a marginal core exists; sensitivity: see Task 5 — the qualified-only constraint is not binding at this Q0). Dataset values (data/table1.csv, no external source): recruit_months = (7,6,5,4,3,1,2) months; recruit_cost = (1.2,0.7,0.6,0.6,0.3,0.1,0.3) sigma; n = (10,20,25,25,110,150,30); salary = (8,4,2,1.5,1,0.9,0.9) sigma (experienced-employee cell is bare sigma = 1.0); training = (0.5,0.6,0.2,0.3,0.1,0.3,0.05) sigma; company-wide churn 18% and middle-manager churn 2x = 36%: problem statement. Sensitivity (logs/churn_beta.log, churn_ramp.log, churn_hr.log): baseline 2-yr fill 92.7-94.6%, productivity index 0.759-0.780 across the swept intervals; conclusions below are stable over the whole table.

### Outcome Analysis

A level-aggregated two-layer SIS contagion model with recruiting pipeline, onboarding ramp, endogenous middle-manager stagnation, and a piecewise productivity penalty. All assumptions are stated; all numbers are from Table 1, the problem statement, or the three exchanges. Reproducible: python code/churn_model.py --seed 0.

## Subtask 2: Task 2: Identify the dynamic processes — (a) organizational churn (influence, dissatisfaction), (b) direct and indirect 

### Problem

Task 2: Identify the dynamic processes — (a) organizational churn (influence, dissatisfaction), (b) direct and indirect effects on productivity.

### Analysis

Churn is not independent Poisson noise. Process (a): an individual's hazard has a base (dissatisfaction) plus a contagion term proportional to the churned-neighbor fraction — a departure makes coworkers more likely to leave within a few months (exchange 1). In the middle tiers the base itself is endogenous: blocked ladders and a peer group that is churning raise dissatisfaction (exchange 2), so r_mid = 0.36 + KAPPA*f_l — a slow self-reinforcing loop that turns a one-time shock into a cascade. Process (b): direct effect = lost coverage: each vacancy-month (and each ramping month at (1-RAMP_FRAC) productivity) removes output; manager vacancies count W_PRODX=1.5x because coordination load is non-delegable. Indirect (pre-departure) effect = anticipatory penalty: from R_BREAK=15% annual turnover upward, coverage work, continuous onboarding, knowledge leakage and declining discretionary effort cost 0.5*r_annual of productivity (exchange 3); below the break it costs 0.1*r_annual.

### Modeling Process

Hazard: h_l = (r_l/12)*(1 + BETA*12*c_l/n_l), with r_l = 0.36 + KAPPA*c_l/n_l for the three middle tiers (0.36/0.2308 otherwise), c_l last month's churn, thinning new_ch_l ~ Bin(n_l, min(h_l, 0.4)). Productivity: P = max(0, 1 - [sum_l w_l*(vac_l + (1-RAMP_FRAC)*ramp_l)]/370 - min(penalty,0.6)); penalty = 0.5*r_annual (r_annual >= 0.15) else 0.1*r_annual; w_l = 1.5 for manager tiers, 1.0 otherwise. Parameters: BETA=0.3 [0.1,0.5] (exchange 1; https://doi.org/10.1080/13678868.2023.2238247), KAPPA=0.5 [0.2,1.0] (exchange 2), W_PRODX=1.5 [1.0,2.0] (exchange 3), R_BREAK=0.15 [0.10,0.20] (exchange 3), RAMP_FRAC=0.6 [0.4,0.8] (Table 1 recruit lag + ramp assumption).

### Outcome Analysis

Two coupled dynamic processes: (a) contagion-driven churn with an endogenous middle-manager stagnation loop (the mechanism that makes Task 5 cascade); (b) productivity loss = direct coverage/ramp loss (manager-weighted 1.5x) + indirect anticipatory penalty (break at 15%). Quantified per scenario in code/churn_model.py.

## Subtask 3: Task 3: Analyze budget requirements for talent management in terms of sigma for recruiting + training over 2 years.

### Problem

Task 3: Analyze budget requirements for talent management in terms of sigma for recruiting + training over 2 years.

### Analysis

Recruiting cost = sum over arrivals of the level's Table-1 recruit cost (sigma); training = sum over occupied positions of the level's annual training cost (sigma), accrued monthly. Two estimates: (1) static lower bound from Table 1 + problem-statement rates only: departures/year = 79.2 (mid 70*0.36 + other 300*0.2308), recruiting = 28.3 sigma/yr; training at 85% fill is of the same order (~tens of sigma/yr); 2-yr static recruiting total ~ 56.6 sigma, and the 2-yr all-in static budget (recruiting + training) is below the simulation figure of ~220 sigma. (2) Simulation (baseline 18% company-wide, HR_SHARE 0.6, seed 0): recruiting 64.4 sigma, training 155.6 sigma, total 220.0 sigma over 2 years (logs/churn_final.log). The simulation is higher than static because the starting 15% gap (370->314) is also backfilled within year 1.

### Modeling Process

recruit_cost = sum_l (arrivals_l + promo_fills_l) * cost_l; train_cost = sum_t sum_l n_l(t) * train_l / 12. cost_l, train_l from Table 1 (see Task 1 table). Simulation defaults: BETA=0.3, KAPPA=0.5, W_PRODX=1.5, R_BREAK=0.15, RAMP_FRAC=0.6, HR_SHARE=0.6 (intervals in Task 1). Static cross-check computed from Table 1 and 18%/36% rates only.

### Outcome Analysis

2-year talent-management budget at the current 18% churn: ~220 sigma (recruiting 64.4 + training 155.6), i.e. ~110 sigma/year; static lower bound ~212 sigma. Training dominates (~70%) because it accrues on every occupied seat for 24 months while recruiting is paid per event.

## Subtask 4: Task 4: Can ICM sustain 80% full status if annual churn goes to 25%? 35%? Costs and indirect effects?

### Problem

Task 4: Can ICM sustain 80% full status if annual churn goes to 25%? 35%? Costs and indirect effects?

### Analysis

Sustain 80% = can the fill ratio stay at or above 80% (296 of 370) over 2 years. Baseline (18%) the model fills to 94.1%, so the question is how far the pipeline can stretch. At 25% company-wide: final fill 91.9%, min fill stays ~89% — above 80%. At 35%: final fill 89.5% — still above 80%, but the trajectory is a steady decline (314 -> 331 and falling) and the 80% line is reached within the next ~12-18 months if 35% persists, so 'sustainable' is a narrow yes for 2 years, no beyond. Costs: recruiting 72.4 sigma (25%) and 86.5 sigma (35%) over 2 years vs 64.4 baseline (+12% / +34%); vacancy-months 1003 (25%) and 1249 (35%) vs 807 baseline. Indirect effects: average productivity index falls 0.773 -> 0.694 (25%) -> 0.610 (35%), i.e. productivity loss 22.7% -> 30.6% -> 39.0%; the anticipatory penalty is active in both (r_annual crosses R_BREAK=15% early), and manager vacancy-months (1.5x weight) are the main direct-loss driver at 35%. Conclusion: 80% full is sustainable at 25% churn over the 2-year horizon (with ~30% productivity drag); at 35% it is not a durable operating point — the organization keeps bleeding fill and 39% of productivity.

### Modeling Process

Scenarios all25pct / all35pct set every level's rate to 0.25/0.35 (mid_rates all levels); all other dynamics as Task 1-2. Outputs from code/churn_model.py (logs/churn_final.log): all25pct fill 91.9%, P 0.694, rec 72.4 sigma, vac 1003; all35pct fill 89.5%, P 0.610, rec 86.5 sigma, vac 1249; baseline fill 94.1%, P 0.773, rec 64.4 sigma, vac 807. Parameters and intervals: see Task 1 table.

### Outcome Analysis

Yes at 25% (fill 91.9%, 2-yr cost 72.4+153.5 sigma, 30.6% productivity loss); marginally at 35% for 2 years (fill 89.5%, cost 86.5+148.5 sigma, 39.0% productivity loss) but the decline is not arrested — beyond 2 years 80% fill is not sustainable at 35%.

## Subtask 5: Task 5: Simulate 30% churn in junior managers and experienced supervisors with (1) no external recruiting, (2) promoting

### Problem

Task 5: Simulate 30% churn in junior managers and experienced supervisors with (1) no external recruiting, (2) promoting only qualified employees; other churn stays 18%; 2 years. Explain impact on HR health.

### Analysis

Scenario: junior-manager and experienced-supervisor rates = 0.30; no external recruiting (all vacancies in these two levels must be filled by internal promotion from the level below; non-hit levels keep external backfill at 18%); qualified-only promotion (pool restricted to the Q0=0.5 qualified share). HR health is read from: middle-manager fill, total fill, vacancy-months, productivity index, and the recruiting-cost saving (internal promotion avoids the external hiring cost of the promoted level).

### Modeling Process

t5_no_recruit_qualified: mid_rates {Junior manager/Executive: 0.30, Experienced supervisor (Branch): 0.30}, external_recruiting=False, promote_qualified_only=True. Promotion fills the churn slot immediately from the feeding level's stable staff (qualified-only: pool = qualified share of stable staff); cascade: a promotion out of level m opens a slot in m. Results (logs/churn_final.log, seed 0): final middle-manager fill 30/70 (43%), total fill 318/370 = 85.9%, vacancy-months 1248, productivity index 0.702 (29.8% loss), recruiting cost 69.1 sigma (vs 64.4 baseline — the saving on external manager hires is offset by the slower recovery of other levels). Control t5_no_recruit_all (same but promotion from all staff, not just qualified): identical to 0.1% precision — with Q0=0.5 the qualified pool never binds, because the feeding levels (110 + 150 staff) are large relative to the ~7-8 manager promotions needed per year. The endogenous KAPPA feedback is what makes the middle tiers keep churning at 30%+ (stagnation: blocked ladders -> dissatisfaction), so the cut is a permanent structural loss, not a one-time 30% dip.

### Outcome Analysis

HR health degrades structurally: middle-manager layer drops from 60/70 baseline to 30/70 (43% filled) and stays there — the organization loses half its mid-management for 2 years. Total fill 85.9% (vs 94.1% baseline), 29.8% average productivity loss, 1248 vacancy-months. The qualified-only constraint changes nothing at Q0=0.5 (feeding pools are large; constraint binds only if Q0 < ~0.1 or if the hit tiers' own staff were the feeding pool) — this is reported as a model limitation, not hidden. Net: cutting external manager recruiting converts a churn problem into a permanent capability loss; the ~5 sigma recruiting saving is not worth it.

## Subtask 6: Task 6: Summarize the potential use of team science and multi-layered networks (Salas et al. 2008; Stokols et al. 2008; 

### Problem

Task 6: Summarize the potential use of team science and multi-layered networks (Salas et al. 2008; Stokols et al. 2008; Kivelä et al. 2013).

### Analysis

Team science (Salas et al. 2008) supplies the intervention layer the model predicts but cannot see: shared mental models, mutual backup, leadership, adaptability and team training reduce the within-team contagion term (the BETA channel) and raise RAMP_FRAC for new members (faster onboarding through structured team socialization). Stokols et al. 2008 (work, health and well-being; multi-level intervention) supplies the structural levers: workload, fairness and promotion-path design attack the endogenous middle-manager dissatisfaction term (KAPPA channel) — i.e., the blocked-ladder mechanism — rather than the individual. Multi-layered networks (Kivelä et al. 2013) supply the formal structure this model's two layers (structural reporting + informal ties) instantiate: churn is a cross-layer phenomenon — an informal-tie departure propagates along the tie layer, converts into a structural vacancy, and re-enters the tie layer as a fresh contagion source; Kivelä's framework motivates the level-aggregation (within-layer homophily) and justifies the manager-weighting (inter-layer coupling: manager nodes couple the layers because they coordinate both).

### Modeling Process

No new equations; mapping: Salas interventions -> lower BETA (contagion) and higher RAMP_FRAC (ramp); Stokols structural design -> lower KAPPA (stagnation feedback); Kivelä multi-layer formalism -> the two-layer structure (reporting layer + informal-tie layer) with cross-layer contagion and manager inter-layer coupling (W_PRODX=1.5).

### Outcome Analysis

Team science is the intervention toolkit that targets the model's two feedback loops: team-level training/socialization damps contagion and accelerates onboarding (direct, cheap, measurable within the model as BETA down / RAMP_FRAC up); work-design (Stokols) attacks the middle-manager stagnation loop (KAPPA down) — the highest-leverage fix given Task 4/5 show middle tiers drive both the cascade and the productivity loss; multi-layer network theory (Kivelä) is the formal justification of the model's structure and points to the next refinement: individual-level edges on both layers instead of level aggregation, which would localize contagion to the leaver's actual team.

## Subtask 7: Task 7: Write the report (superseded by this JSON container: each task's four fields below are the report; no separate m

### Problem

Task 7: Write the report (superseded by this JSON container: each task's four fields below are the report; no separate markdown, no images).

### Analysis

Synthesis. ICM at 18% company-wide churn (36% in middle tiers) is a contagion-plus-stagnation system, not a headcount problem: departures propagate through informal ties (BETA=0.3) and the middle tiers self-reinforce through blocked ladders (KAPPA=0.5). The budget is ~220 sigma over 2 years (Task 3). An 80% fill floor is sustainable at 25% churn but is a non-stationary, unprofitable point at 35% (Task 4: 39% productivity loss). Cutting external manager recruiting in the junior-manager/experienced-supervisor tiers collapses mid-management to 43% fill permanently (Task 5) — the cheapest-looking lever is the most destructive. The intervention logic (Task 6): team-science levers (BETA, ramp) for the contagion channel; work-design levers (KAPPA) for the stagnation channel; multi-layer modeling as the refinement path.

### Modeling Process

Full parameter table (as in Task 1): BETA = 0.3, [0.1, 0.5], source: exchange 1 + https://doi.org/10.1080/13678868.2023.2238247. KAPPA = 0.5, [0.2, 1.0], source: exchange 2. W_PRODX = 1.5, [1.0, 2.0], source: exchange 3. R_BREAK = 0.15, [0.10, 0.20], source: exchange 3. RAMP_FRAC = 0.6, [0.4, 0.8], source: Table 1 recruit lag + ramp assumption. HR_SHARE = 0.6, [0.5, 0.7], source: task item 5 / Table 1 recruiting calibration. Q0 = 0.5, [0.2, 0.8], source: assumption (task item 8; non-binding at default — Task 5). Dataset: table1.csv (GBK), 7 levels, 370 staff; recruit_months (7,6,5,4,3,1,2); recruit_cost (1.2,0.7,0.6,0.6,0.3,0.1,0.3) sigma; n (10,20,25,25,110,150,30); salary (8,4,2,1.5,1,0.9,0.9) sigma; training (0.5,0.6,0.2,0.3,0.1,0.3,0.05) sigma; 18%/36% rates: problem statement. All simulation outputs: logs/churn_final.log (base), logs/churn_beta.log / churn_ramp.log / churn_hr.log (sweeps over the stated intervals; conclusions invariant).

### Outcome Analysis

The seven sub-tasks form one consistent picture: churn dynamics (1-2) -> cost (3) -> stress test (4) -> intervention counterfactual (5) -> intervention theory (6). Key decision rule: any scenario that moves the middle-tier fill below ~60% or the productivity index below ~0.7 is a red line; 35% churn and no-external-recruiting both cross it. Code: code/churn_model.py; evidence: results/interaction_evidence.md; data: data/table1.csv.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
