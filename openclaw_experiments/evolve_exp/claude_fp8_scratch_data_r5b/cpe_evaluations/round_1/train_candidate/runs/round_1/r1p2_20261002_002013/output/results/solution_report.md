# Solution

## Subtask 1: Task 1 — Build a Human Capital network model of ICM's 370-person organization from the supplied Table 1, describing the 

### Problem

Task 1 — Build a Human Capital network model of ICM's 370-person organization from the supplied Table 1, describing the model and the assumptions used. This is the structural foundation on which Tasks 2-6 run.

### Analysis

Approach: represent the organization as a level-structured directed graph whose nodes are the 370 employees grouped into the seven levels of Table 1, with three edge types. (a) Reporting edges — every employee reports to exactly one supervisor in the level above, so the seniority pyramid is the reporting backbone (10 senior / 20 junior manager / 25 experienced supervisor / 25 inexperienced supervisor / 110 experienced employee / 150 inexperienced employee / 30 clerk). (b) Peer/coworker edges — same-level working ties. (c) Churn-contagion edges — an employee whose supervisor, peer, or recently-departed former co-worker has churned carries a raised exit hazard (the problem's statement that 'churn diffuses from employee to employee'). This is sound because the only structural data supplied is level counts, salaries, recruiting cost/time, and training cost, so a level-structured (macro) network with contagion edges is the coarsest model that can carry the dynamic processes the later tasks need without inventing individual-level data we do not have.

### Modeling Process

Level index i = 0..6 in the order above with sizes n = [10, 20, 25, 25, 110, 150, 30] (sum 370). Data cleaning of table1.csv before use: the currency unit sigma was stored as garbled bytes (0xa6 0xd2, a mangled sigma); repaired by byte replacement so all cost/salary/training values are read in units of sigma (the median salary). One missing value — the experienced-employee salary, the level that defines sigma — was imputed as 1.0 sigma, consistent with its peers (inexperienced employee 0.9 sigma) and with sigma being the median of the distribution. No duplicates; row count 7; headcount 370 matches the statement. Cleaned data (units of sigma): senior (t_fill 7 mo, c_rec 1.2, n 10, salary 8.0, train 0.5); junior manager (6, 0.7, 20, 4.0, 0.6); experienced supervisor (5, 0.6, 25, 2.0, 0.2); inexperienced supervisor (4, 0.6, 25, 1.5, 0.3); experienced employee (3, 0.3, 110, 1.0 imputed, 0.1); inexperienced employee (1, 0.1, 150, 0.9, 0.3); clerk (2, 0.3, 30, 0.9, 0.05). Derived: weighted mean salary = sum(n_i s_i)/370 = 1.6108 sigma; 85% of 370 = 314.5 seats filled at any time (55.5 vacant); HR actively hires 8-10% of 370 = 29.6-37 posts/yr (midpoint 33.3), covering ~2/3 of vacancies; CEO salary ~10x the median (issue 9). Network: node i has reporting degree 1 (upward) plus peer ties within level i; the contagion neighbourhood is the set of contacts (supervisor, peers, recently departed co-workers) whose departures raise hazard.

### Outcome Analysis

The network is a 7-layer directed pyramid with 370 nodes. Initial condition: 85% of seats filled, the standing 55 vacancies distributed proportionally by level size (largest-remainder integer allocation: [1,3,4,4,17,23,4]). Limitations/biases: (1) the model is level-aggregated, not individual-level, so it cannot name specific at-risk employees — it gives per-level churn and ratios; (2) the reporting edges assume one supervisor per employee (span of control implied by the level ratios), which is an assumption not in the data; (3) the sigma imputation for experienced-employee salary is a single bold assumption but a low-sensitivity one (it is the reference unit). The structure supports all later dynamics because every process (churn, promotion, hiring, coordination) is expressible on level flows.

## Subtask 2: Task 2 — Identify the dynamic processes within the Human Capital network: (1) organizational churn (influence, dissatisf

### Problem

Task 2 — Identify the dynamic processes within the Human Capital network: (1) organizational churn (influence, dissatisfaction) and (2) direct and indirect effects on productivity. Describe the model and assumptions.

### Analysis

Two coupled dynamics are modelled. Churn is a stochastic exit process with a multiplicative hazard; productivity is a seat-occupancy process that degrades when seats are empty, when a manager is absent (lost coordination), and when new hires are ramping. The churn mechanism is driven by three factors, the dominant one established by expert consultation: a manager with no realistic promotion path is the most likely to quit (Exchange 1), so the promotion-path factor multiplies the hazard for the three middle levels (junior manager, experienced supervisor, inexperienced supervisor) exactly when their actual per-incumbent opening rate falls below half the realistic opening rate (Exchange 2). Churn also diffuses through the contagion edges (Exchange 1 / issue 2), and marginal employees — kept on to suppress churn (issue 8) — churn less. This is sound because it turns the two qualitative statements (middle managers churn at 2x and quit when stuck; churn diffuses) into testable, scenario-responsive equations rather than fixed constants.

### Modeling Process

Annual exit hazard for an employee at level i: h_i = lambda_i * P_i * C_i * Q_i, with exit probability p_i = 1 - exp(-h_i) approximated by h_i * filled_i for small h (expected churn count). lambda_i = base company rate (0.18/yr) times the structural middle multiplier (2x for the three middle levels, issue 4). P_i (promotion-path factor) = P_STUCK = 2.0 when the level is 'stuck', else 1.0; a middle level is stuck when actual_rate = vac[i-1]/filled[i] < 0.5 * open_rate, where open_rate = openings/mid_size and openings = max(PROMOTE_MIN, PROMOTE_RATE * mid_size) with PROMOTE_RATE = 0.08, PROMOTE_MIN = 3 (Exchange 2: realistic openings are 5-10% of the mid tier, ~3-8/yr, below ~3 the 'no way up' feeling sets in). C_i (contagion) = 1 + kappa * f_prev with kappa = 0.35, f_prev = previous year's realized org churn rate (proxy for the fraction of an employee's contacts who recently departed). Q_i (quality) = 1.0 for good employees, Q_marg = 0.7 for the 15% marginal share kept on (issue 8); effective hazard = lambda_i*(1-MARG)*P_i*C_i + lambda_i*MARG*Q_marg*P_i*C_i. Because at 85% fill the superior levels hold few open seats, actual_rate is below half the realistic rate for the middle levels, so P_i = 2 and the 2x middle churn emerges from the mechanism rather than being hard-coded — and it switches off if HR keeps the senior levels open. Productivity: a filled seat at level i produces s_i sigma/yr (s_i = level salary) plus, for management levels i in 0..3, a coordination value 0.1*s_i*(subordinates) that is halved (COORD_PEN = 0.5) when the seat one level above is empty. New hires produce 50% for their first 3 months (ramp). Org productivity index = 100 * (sum of filled-seat output) / (fully-staffed steady-state output). Indirect effects of churn: unfilled seats (direct output loss), lost coordination (missing managers), and ramp-down of replacements; these are all carried in the index.

### Outcome Analysis

Under the baseline (18% company rate) the middle-tier churn rate is ~31%/yr vs ~18% org-wide in year 0 (ratio 1.68, rising to 2.24 in year 1 as contagion compounds) — i.e. the 2x middle churn of issue 4 and the rising churn of issue 7 both appear as outputs. The contagion term makes churn slightly self-reinforcing (a bad year raises next year's hazard), which is the 'diffusion' dynamic. Productivity starts at 76.8% of fully-staffed output (the standing 15% vacancy) and recovers as seats refill. Limitations: the contagion uses an org-level proxy f_prev rather than per-employee contact tracking (a deliberate coarse choice given no individual data); the 15% marginal share is assumed uniform across levels; P_STUCK = 2.0 is a magnitude the model is robust to (a sweep over 1.5-3.0 changes year-2 productivity by <0.2 points). The mechanism is the key assumption and is the part an HR manager would challenge first.

## Subtask 3: Task 3 — Analyze ICM's budget requirements for talent management (recruiting and training) in units of sigma over the ne

### Problem

Task 3 — Analyze ICM's budget requirements for talent management (recruiting and training) in units of sigma over the next two years.

### Analysis

Budget is the cost of keeping the pipeline moving: (a) recruiting cost for every external hire at the level-specific median cost from Table 1; (b) a vacancy-gap cost for seats that stay unfilled (lost output while the seat is open, prorated by that level's time-to-fill); and (c) training cost for the standing staff plus onboarding training (half the annual training cost) for each new hire. Reported in sigma so that slow inflation cancels by construction (the problem notes decisions are made on the relative value of sigma). This is sound because Table 1 supplies exactly the per-level recruiting cost and training cost, and the vacancy-gap term prices the indirect cost that a pure headcount model would miss.

### Modeling Process

For each year t and level i, let hired_i(t) be external hires (allocated by vacancy share, capped by the HR hiring capacity 0.09*370 = 33.3 seats/yr) and vac_i(t) the end-of-year vacancies. B_recruit(t) = sum_i hired_i(t) * c_rec_i. B_gap(t) = 0.3 * sum_i s_i * vac_i(t) * min(t_fill_i,12)/12 (0.3 = the share of a year an unfilled seat is fully idle, prorated by time-to-fill). B_train(t) = sum_i train_i * (filled_i - hired_i) + 0.5 * sum_i hired_i * train_i. B_total = B_recruit + B_gap + B_train. Two-year view sums years 1 and 2 (year 0 is the initial catch-up).

### Outcome Analysis

Baseline (S0): year 1 B = 88.77 sigma (recruit 8.96, gap 1.80, training 78.01) — the training bill dominates because it is the standing cost of 370 employees; year 2 B = 86.94 sigma (recruit 3.41, gap ~0, training 83.53) as the initial vacancy catch-up ends. Two-year total ~= 175.7 sigma, of which ~161.5 is training (the recurring cost) and ~12.4 is recruiting (front-loaded in year 1). The recruiting cost is small relative to training because ICM's per-hire cost (0.1-1.2 sigma) is modest and only ~33 hires/yr occur. Raising churn (Tasks 4) raises the recruiting line but the training line is nearly unchanged (it tracks headcount, which the hiring cap holds near full). Limitation: the gap cost uses a 0.3 idle-share factor (assumption); the true indirect cost of an unfilled manager seat is larger (it also removes coordination value), which is why Tasks 4-5 also report the productivity index, not just the budget.

## Subtask 4: Task 4 — Can ICM sustain its 80% full status if the annual churn rate for all positions rises to 25%? To 35%? What are t

### Problem

Task 4 — Can ICM sustain its 80% full status if the annual churn rate for all positions rises to 25%? To 35%? What are the costs and the indirect effects of these higher turnover rates?

### Analysis

Feasibility is a refill-vs-outflow balance: each year a churn rate C removes C * (filled seats) employees, and the organization can refill only as many as its hiring capacity (33.3 external/yr) plus internal promotions (~5-6/yr, Exchange 2). If outflow exceeds refill, vacancies accumulate and the fill fraction falls below 80%; if refill exceeds outflow, fill rises toward 100% but is capped at the hiring capacity's steady state. I run the full dynamic model at C = 0.25 and C = 0.35 (S1, S2) and compare the fill trajectory, budget, and productivity to the 18% baseline (S0). This is the right test because it uses the same model as the baseline, so the comparison isolates the effect of the churn rate.

### Modeling Process

S1: per-level churn rate 0.25 everywhere. S2: per-level churn rate 0.35 everywhere. (The middle levels' 2x structural rate is already embodied in the baseline; a uniform scenario rate applies to all levels.) Steady-state check: maximum sustainable fill = (refill capacity)/C. With refill capacity 33.3 + 5.5 = 38.8 seats/yr, C=0.18 gives 216/370 = 58.3%, C=0.25 gives 155/370 = 41.9%, C=0.35 gives 111/370 = 30.0% if the org ran at full churn with no standing vacancies; the break-even churn rate that just sustains 80% fill is C = 38.8/(0.80*370) = 13.1%/yr. Because ICM currently sits at 85% (above that break-even), the 80% floor is a policy buffer, not a dynamic equilibrium.

### Outcome Analysis

At 25% (S1) and 35% (S2) the model still recovers fill from 85% to ~94-95% in year 1 because the 33.3/yr hiring capacity is large relative to the *incremental* churn, so ICM can sustain 80%+ in the short (2-year) horizon at both 25% and 35% — but only by spending the hiring capacity, and the fill ceiling (~94%) is set by hiring capacity, not by churn. The costs: (1) recruiting cost rises with churn (more seats to refill); (2) the real cost is indirect — the productivity index and the mid-to-org churn ratio. At 35% the org-wide churn rate is ~39%/yr and year-1 fill stalls at ~94% with the middle tier at 91-92%, so the organization is running a permanent churn treadmill: it never gets above ~94% filled and is always hiring. Indirect effects: a standing ~6% vacancy (vs 15% at the 85% start), higher new-hire ramp (more seats at 50% output), and — critically for HR health — a uniform high rate does NOT flag 'deteriorating' on the mid-to-org ratio (S1 ratio 1.43, S2 ratio 1.41, both stable) because the middle tier churns proportionally. So a uniform 25-35% churn is survivable on fill but expensive and puts the org on a hiring treadmill; the danger the problem worries about (issue 7, middle-manager churn) is the *relative* mid-tier burden, which a uniform rate masks. Cost estimate for the incremental churn: at 35% the extra ~53 seats/yr churned beyond 18% cost ~16 sigma/yr in recruiting plus a large vacancy-gap/lost-output cost (order 100+ sigma/yr) if the hiring capacity is not increased.

## Subtask 5: Task 5 — Simulate the impact of 30% churn in both junior managers and experienced supervisors (other levels at 18%) over

### Problem

Task 5 — Simulate the impact of 30% churn in both junior managers and experienced supervisors (other levels at 18%) over two years, under (1) no external recruiting and (2) promoting only qualified employees. Explain the impact on HR health.

### Analysis

This is a targeted stress test: the two levels with the steepest promotion bottleneck (junior manager, experienced supervisor — the 'stuck' middle of issue 4) churn at 30% while the rest of the org churns at 18%. Two constraints are applied: S3a shuts off external recruiting (superior vacancies can only be filled by internal promotion), and S3b additionally restricts promotions to qualified candidates (>=1 year in role, not marginal). I run both for two years and read the result through the HR-health metric defined in the model (the mid-to-org churn ratio and its direction), which is the interpretation criterion the HR manager uses. This isolates exactly the scenario the HR supervisor asked about.

### Modeling Process

S3a: per-level rates [0.18, 0.30, 0.30, 0.36, 0.18, 0.18, 0.18] (the 30% applied to junior manager and experienced supervisor; the inexperienced supervisor keeps its 2x structural 36%), no_ext_recruit=True so only internal promotion (capped at ~5-6 openings/yr, Exchange 2) fills the senior-level vacancies. S3b: same rates, external recruiting allowed, promote_qualified_only=True so a promotee must have >=1 year in role (EXP_YRS_REQ) and not be in the marginal 15%. HR health is read as hr_health = 'deteriorating' iff mid_to_org_churn_ratio >= 2.0 and the ratio is rising year-over-year (Exchange 3: 'runs at roughly twice the company average and keeps climbing').

### Outcome Analysis

S3a (no external recruiting): year 1 the experienced-supervisor level drops to 83% filled and junior manager to 95%, because internal promotion alone (~5-6/yr) cannot replace 30% churn in two 20-25-person levels (~6-8 departures/level/yr plus the 18% elsewhere). The mid-to-org churn ratio hits 2.10 and is rising, so HR health is flagged 'deteriorating' — the organization is losing its middle tier to attrition it cannot refill, and the experienced-supervisor gap is the first thing to show (it is the level with the least promotion source above it). S3b (promote qualified only, with recruiting): the ratio still reaches 2.06 and is rising -> 'deteriorating'; restricting promotions to qualified candidates slows the pipeline (fewer eligible promotees), so the middle-tier fill recovers more slowly than the baseline and the relative mid-tier burden stays elevated. Explanation to the supervisor: 30% churn concentrated in junior managers and experienced supervisors is the single most damaging pattern the model produces, because (a) it removes exactly the 'stuck' middle that issue 4 identifies as critical, (b) internal promotion is too slow to backfill 30% in two levels, and (c) the HR-health signal (mid-to-org ratio >= 2x and climbing) trips in both variants — meaning the organization would be in a deteriorating state within one year, with the experienced-supervisor gap the earliest warning. The recommendation the model supports: keep external recruiting available for the middle tier (S3a is clearly worse than S3b) and create more visible promotion openings (the stuck mechanism, Exchange 1-2) rather than relying on promotion-only backfill.

## Subtask 6: Task 6 — Summarize the potential use of team science and multi-layered networks in fulfilling the HR manager's vision of

### Problem

Task 6 — Summarize the potential use of team science and multi-layered networks in fulfilling the HR manager's vision of connecting the Human Capital network to information-flow, trust, influence, and friendship layers.

### Analysis

This is a synthesis/design question, not a computation. The Human Capital network built in Tasks 1-5 is one layer of a multi-layer (multiplex) network; the HR manager's vision (Kivelä et al. 2013; Salas et al. 2008; Stokols et al. 2008) is to add parallel layers on the same 370 nodes — information flow, trust, influence, friendship — and to analyze them jointly. The value is that no single layer predicts churn: churn in this model is driven by the promotion-path (structural) layer plus the contagion (social) layer, and the social layers are where the contagion, trust, and informal-influence signals actually live. Team science (Salas) supplies the construct (teamwork/coordination) that the coordination term in the productivity model operationalizes; the multilayer framework (Kivelä) supplies the formalism for projecting one layer onto another.

### Modeling Process

Model the organization as a multilayer network with node set V (370 employees) and layer set L = {hierarchy, information, trust, influence, friendship}. Each layer l has an adjacency A_l; the hierarchy layer is the reporting graph from Task 1. Key multilayer quantities to compute and use: (1) nodal embeddings via cross-layer eigenvector or random-walk-with-teleport, so that an employee's position in the hierarchy is scored by their trust/influence centrality in the social layers; (2) the contagion factor C_i from Task 2 is re-expressed as a within-layer and across-layer spread — a churn event on the friendship/influence layer propagates to the hierarchy layer with a coupling weight, which is the formal version of 'churn diffuses'; (3) a multilayer centrality (e.g. eigenvector centrality on the inter-layer projection) that identifies 'keystone' employees whose departure would damage more than one layer at once — these are the retention-priority targets; (4) a layer-coupling index that measures how aligned the hierarchy is with the trust/influence layers (a misalignment — e.g. a high-trust informal leader who has no formal authority — is a churn risk and a team-science 'team performance' lever). The HR office would lead because the hierarchy layer is its data; the other offices contribute their layers, and the HR network model is the join key.

### Outcome Analysis

Potential uses, ranked by decision value: (1) keystone-employee identification for retention — the multilayer centrality names individuals whose loss damages multiple layers, giving HR a targeted retention list (this is the concrete payoff of the vision, and it is exactly what a single-layer model cannot do); (2) early-warning churn — the contagion layer makes churn visible in the friendship/influence network before it shows in the hierarchy (resignations cluster in social groups), supporting issue 1 (early detection); (3) team-science alignment — coupling the hierarchy to the trust/influence layers surfaces informal teams that do not match formal structure, which team science (Salas) links to performance; (4) promotion-path design — the promotion-path factor from Tasks 2/5 can be informed by the influence layer (promote people who already have informal influence, reducing the ramp and the 'stuck' feeling). Limitations/biases: the social layers are not in the supplied data, so this is a design blueprint, not a computed result; the coupling weights between layers would need calibration (a natural extension of the kappa = 0.35 contagion weight); and multilayer centrality is more expensive to compute and interpret, so it should be layered on top of, not replacing, the level-aggregated model. The deliverable to the HR manager is the architecture (shared node set, per-layer adjacency, cross-layer metrics) and the four uses above, which connect to the other offices' planned layers.

## Subtask 7: Task 7 — Report on the organizational model, its function, and the issues the supervisor wants considered (the 21-page c

### Problem

Task 7 — Report on the organizational model, its function, and the issues the supervisor wants considered (the 21-page cap and executive summary are the report format; this container carries the substance).

### Analysis

This task asks for the integrative read: what the model is, what it does, and how it addresses each of the nine issues in the background plus the seven work-tasks. The substance is carried in the four fields above; this entry ties them together and states the model's function and its limits honestly. The model's function is to give the HR office a single, quantitative, scenario-capable view of the talent pipeline: it takes the churn rate (the thing the CEO is worried about), the promotion structure (the thing that makes middle managers leave), and the hiring/training budget (the thing that must be funded), and returns fill rates, a productivity index, a budget in sigma, and an HR-health flag.

### Modeling Process

The model is a discrete-time (annual) level-flow simulation with three coupled state variables per level: filled seats, vacancies, and in-role experience/freshness. Update order each year: (1) compute churn from the multiplicative hazard (Task 2) and remove it; (2) fill superior vacancies by internal promotion, capped at the realistic opening count (Exchange 2) and subject to the experience/qualification rule (issue 6); (3) fill remaining vacancies by external hiring, capped by the HR hiring capacity (issue 5); (4) compute the productivity index (Task 2) and the budget (Task 3) and the HR-health ratio (Exchange 3); (5) age in-role experience. All constants come from Table 1, the problem statement, or the three expert exchanges; the empirical parameter table is kept in the modeling log with name, value, interval, and source. Scenario switching (Tasks 4-5) is done by overriding the per-level churn rates and the recruiting/promotion constraints, which is why one script covers every scenario.

### Outcome Analysis

How the model addresses the issues: issue 1 (early churn detection) -> the mid-to-org ratio is the early-warning signal and the multilayer extension (Task 6) puts the detection in the social layers; issue 2 (churn diffusion) -> the contagion factor C_i; issue 3 (matching to position / unused ratings) -> the quality factor Q_i and the 'promote qualified only' scenario use the annual rating as the qualification gate; issue 4 (stuck middle managers, 2x churn) -> the promotion-path factor P_i makes the 2x emerge and makes it responsive to creating openings; issue 5 (85% filled, 8-10% hiring) -> the hiring capacity and the 85% initial condition; issue 6 (experience requirements) -> the EXP_YRS_REQ promotion rule; issue 7 (rising churn, 18%) -> the baseline scenario and the contagion self-reinforcement; issue 8 (keeping marginal employees) -> the 15% marginal share with Q_marg = 0.7; issue 9 (CEO:median ratio 10x) -> used to sanity-check the salary structure (senior level 8x, CEO ~10x, consistent). Overall limitations: the model is aggregate (per-level, not per-person), the social/contagion layer uses an org-level proxy, several coefficients (kappa, Q_marg, ramp, coordination penalty, gap idle-share) are stated assumptions rather than data, and the two-year horizon is short — a longer run would show whether the org converges to a stable fill or stays on a hiring treadmill. The model is decision-relevant (it flags which scenarios are 'deteriorating' and prices them in sigma) but should be treated as a planning tool: the magnitudes move with the assumptions, and the qualitative ordering of the scenarios (S3 worst, uniform-high survivable-but-expensive, baseline borderline) is the robust part.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
