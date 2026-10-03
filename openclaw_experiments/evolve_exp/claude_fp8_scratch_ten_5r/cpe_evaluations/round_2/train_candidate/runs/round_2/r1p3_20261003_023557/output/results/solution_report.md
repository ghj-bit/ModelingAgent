# Solution

## Subtask 1: Task 1: Build a Human Capital network model of ICM's 370-person organization from the supplied Table 1, stating the mode

### Problem

Task 1: Build a Human Capital network model of ICM's 370-person organization from the supplied Table 1, stating the model and its assumptions. Scope: represent the personnel structure as a network (positions, reporting, and a peer/friendship layer) and a population that can be churned, replaced, and trained.

### Analysis

Approach: a two-layer network over the 7 position levels. Layer 1 (formal) is the reporting tree: CEO -> Senior/Junior managers -> supervisors (branch/division) -> experienced/inexperienced employees, with administrative clerks attached to the levels they serve. Layer 2 (informal) is a friendship/peer layer, which expert exchange 2 identified as the dominant channel for churn contagion (weaker than the reporting tie on its own). The population per level is the count in Table 1 (10,20,25,25,110,150,30 = 370). Assumptions: (a) the network is level-structured (agents within a level are interchangeable, so the model tracks level populations plus a peer-neighbour count rather than 370 named nodes — this keeps the dynamics exact at aggregate scale and reproducible); (b) the friendship layer is approximated by each employee's ties to the adjacent levels (their work team), so 'connected to a churned former employee' is measured as the fraction of recent churn in the neighbouring level; (c) the company is in a steady staffing state at ~85% of 370 seats filled (the problem's stated 85%), the remainder being positions open while being recruited; (d) churn is voluntary and diffuses peer-to-peer. Data cleaning: the CSV encoded sigma as the Latin-1 byte pair 0xA6D2 (mojibake of UTF-8 sigma); all dollar figures were recovered as multiples of sigma and no rows were dropped or duplicated. Soundness: a level-aggregated network is the standard reduction for an HR churn problem where only level-level data is given, and it preserves the total, the per-level churn, and the peer-diffusion effect that the problem asks us to model.

### Modeling Process

Nodes: 7 levels L_i with capacity N_i (i=1..7) and incumbent count s_i(t). Formal edges: reporting link L_i -> L_{i+1}. Informal edges: peer ties between L_i and its neighbours L_{i-1}, L_{i+1}. State at year t: s_i (staffed), plus a recruitment pipeline of open seats. Recruitment of level i has median lead time lag_i (months, Table 1) and cost rc_i (sigma, Table 1); a seat that churns is OPEN (vacant) for lag_i before a hire arrives. Training cost per level tr_i (sigma, Table 1). The network's role is to set the churn of each seat from its neighbourhood: the peer layer supplies the contagion term, the reporting layer supplies the 'blocked-advancement' term (a mid-level seat with no upward path churns more). Churn per level is r_i(t) (see Task 2), and s_i(t+1) = s_i(t) - C_i(t) + A_i(t) where C_i is churn and A_i are arrivals whose lag has completed. All monetary quantities are in sigma (the company's median income), consistent with the problem's use of relative values.

### Outcome Analysis

The model reproduces the given structure exactly (370 positions, 7 levels, the 85% steady-state fill) and carries the two network layers the problem asks for. Limitations: (a) the friendship layer is proxied by adjacent-level ties, so it captures 'a colleague in my work team left' but not long-range friendship edges; (b) level-aggregation assumes interchangeability within a level, so it cannot name which specific individual churns — adequate for population dynamics, not for individual-level prediction. These are the bold assumptions the task permits; they are stated, not hidden.

## Subtask 2: Task 2: Use the model to identify and incorporate the dynamic processes in (1) organizational churn (influence, dissatis

### Problem

Task 2: Use the model to identify and incorporate the dynamic processes in (1) organizational churn (influence, dissatisfaction) and (2) the direct and indirect effects of churn on productivity.

### Analysis

Churn is modeled as a discrete-time dynamic with two drivers: a baseline rate and a peer-contagion (influence) term, modulated by a blocked-advancement (dissatisfaction) term for middle managers. Expert exchange 1 fixed middle-manager churn at ~2x the company rate (36%/yr at an 18% base); exchange 2 set the contagion as a weak, probabilistic, friendship-driven effect; exchange 8 set churn to be highest among low/marginal performers and to spike for the 'high-rated but blocked' subset. Productivity has a direct effect (the leaver's output is gone until replaced, damped by teammates absorbing some load) and indirect effects (a vacancy is an open, unproductive seat for the whole recruitment lag; a new hire ramps below full productivity for 3-6 months; and low fill erodes morale, which feeds further churn). Exchange 3 set the direct loss at ~1x the leaver's share (interval 0.5-1.5); exchange 4 set the ramp window; exchange 6 set the morale->churn feedback and the boundary at which the model stops being a steady state.

### Modeling Process

Per-level annual churn: C_i(t) = round( r_i(t) * boost_i(t) * s_i(t) ), where the base rate r_i(t) = 0.18 for most levels and 2*0.18 = 0.36 for the three middle levels (Junior manager, Experienced supervisor, Inexperienced supervisor) per exchange 1, and boost_i(t) = 1 + w_c * (fraction of recent churned neighbours in the peer layer), with w_c = 0.15 (exchange 2; the peer-neighbour fraction is computed over the adjacent levels as the work-team proxy). The blocked-advancement dissatisfaction is carried in the 2x middle rate: a mid-level seat whose upward path is gated by the rigid experience rule (issue 6) churns at the elevated rate. Direct productivity loss per leaver = PRODUCTIVITY_LOSS = 1.0 leaver-output units (interval 0.5-1.5, exchange 3). Indirect effects: (i) vacancy person-years V = sum over seats of the recruitment lag while open; (ii) ramp deficit = (1 - 0.70) * (new hires this year) with ramp productivity 0.70 over a 3-6 month window (exchange 4); (iii) morale feedback: when cumulative fill falls below ~80%, an additional churn multiplier is applied (exchange 6), so the model has a documented domain of validity above that fill. Workforce productivity P(t) = fill(t) * (1 - 0.30*(1-0.70)*rampshare(t)), where fill(t) = sum_i s_i / 370 and rampshare is the share of staff still ramping.

### Outcome Analysis

The dynamics are: churn -> open vacancy (unproductive for the level's lag) -> hire arrives -> new hire ramps below full output -> net productivity dip that recovers as the ramp completes; and a peer layer that makes churn cluster in teams, so a departure raises the exit probability of connected colleagues. At the 18% base the system reaches a steady ~85% fill and ~100%-of-capacity productivity after the ramp, because lags and ramps are short relative to the low churn. The model's indirect-effect accounting is what makes higher-churn cases costly even when seats are eventually refilled. Limitations: the morale term is a threshold switch rather than a smooth curve, so behavior exactly at the 80% boundary is a kink; the 2x middle rate is a constant multiplier and does not by itself model the *growth* of dissatisfaction over years, only its elevated level.

## Subtask 3: Task 3: Analyze the organization's budget requirements for talent management (recruiting and training) in sigma over the

### Problem

Task 3: Analyze the organization's budget requirements for talent management (recruiting and training) in sigma over the next two years at the current churn.

### Analysis

At the current 18% annual churn, two years require replacing 2*0.18 = 36% of each level's incumbents (plus the middle levels at 36%/yr, so 2*0.36 = 72% of them). Recruiting budget is the number of replacements times each level's median recruitment cost (Table 1, in sigma); training budget covers (a) the training cost of the continuing workforce and (b) the onboarding training of the new hires. Because sigma rises with inflation, all figures are reported in sigma (relative units), as the problem directs. This is the steady-state annual demand doubled for the two-year horizon.

### Modeling Process

For each level i: churn_per_yr_i = r_i * N_i; hires_2yr_i = 2 * churn_per_yr_i (using r_i = 0.18 for non-middle and 0.36 for the three middle levels); recruit_cost_i = hires_2yr_i * rc_i; training_cost_i = (N_i + hires_2yr_i) * tr_i, where (N_i + hires_2yr_i) is the staffed population being trained (incumbents plus new hires) and tr_i is the level's annual training cost. Totals: Recruiting = sum_i recruit_cost_i, Training = sum_i training_cost_i, Grand total = sum. Computed from Table 1. (The simulation's in-year recruiting/training, which counts only hires that actually arrive within the 2-year window, is lower — e.g. ~38.4 sigma recruiting — because some hires are still in their recruitment lag; the budget below is the full requirement the HR office must plan for.)

### Outcome Analysis

Two-year talent-management budget at current churn: Recruiting = 40.68 sigma; Training = 118.32 sigma; Total = 159.0 sigma. By level (recruiting / training, sigma): Senior mgr 4.32 / 6.80; Junior mgr 5.04 / 16.32; Experienced supervisor 5.40 / 6.80; Inexperienced supervisor 5.40 / 10.20; Experienced employee 11.88 / 14.96; Inexperienced employee 5.40 / 61.20; Admin clerk 3.24 / 2.04. The training budget is dominated by the 150 inexperienced employees (high count, 0.3 sigma each) and is ~2.9x the recruiting budget, which is the practical takeaway: at current churn, ICM spends far more on keeping people trained than on hiring them. Limitation: this treats churn as a deterministic 18%/yr and does not add a contingency reserve for the 'increasing churn' trend (issue 7); a prudent plan would carry the 25% case (Task 4) as the upper band.

## Subtask 4: Task 4: Can ICM sustain its 80% full status if annual churn goes to 25%? To 35%? What are the costs and indirect effects

### Problem

Task 4: Can ICM sustain its 80% full status if annual churn goes to 25%? To 35%? What are the costs and indirect effects of these higher turnover rates?

### Analysis

Run the population simulation with every level's churn at 25% and 35% (the problem says 'for all positions') and read the steady-state fill, the minimum fill reached, and the cost/indirect-effect totals. The 80% test is whether the steady-state fill stays at or above 80% of 370. Because a churned seat is open for its level's recruitment lag, higher churn means more simultaneous open seats, so fill falls; the question is whether it falls below 80%.

### Modeling Process

simulate(base_churn = 0.25) and simulate(base_churn = 0.35) over a 4-year horizon (2 years is too short to reach steady state at these rates), with the same lag, ramp, and peer-contagion terms as Task 2. Steady-state fill is the last-year fill; cost = 2-year recruiting + training in sigma; indirect effects = cumulative vacancy person-years and the direct productivity-loss units. The 80% test compares steady-state fill to 0.80*370 = 296 staffed.

### Outcome Analysis

25% churn: steady-state fill = 80.5% (year-1 dip 74.3%), so ICM *just barely* holds 80% — it is at the threshold, not comfortably above it, and the first-year dip breaches it. Cost over 2 years: recruiting 50.3 sigma, training 21.95 sigma; indirect effects: 167 vacancy person-years and 167 direct productivity-loss units. 35% churn: steady-state fill = 76.5% (year-1 dip 63.2%), so ICM *cannot* sustain 80%; it sits ~3.5 points below for the rest of the period and dips to 63% in year 1. Cost over 2 years: recruiting 68.1 sigma, training 31.75 sigma; indirect effects: 223 vacancy person-years and 223 productivity-loss units. Interpretation: at 25% the 80% target is marginal and the morale feedback (exchange 6) means the company is operating in the regime where morale, not customer output, is the first thing to degrade — an early-warning zone. At 35% the company is structurally short-handed: fill is permanently below 80%, vacancies are chronic (223 person-years over two years means on average ~30% of all seats open at once), recruiting cost is ~77% higher than at 18%, and the morale->churn loop risks pushing the realized rate even above 35%. The indirect effect that matters most is not the recruiting invoice but the sustained productivity loss and the loss of firm-specific knowledge that each departure carries (exchange 10: total replacement cost ~1.0 annual salary, interval 0.5-2.0). Limitation: the model holds the churn rate exogenous at 25%/35%; in reality the morale feedback would raise it further, so the true fill at '35%' is likely lower than 76.5% — these are best read as floors.

## Subtask 5: Task 5: Simulate 30% churn in junior managers and experienced supervisors (other levels at 18%) with (a) no external rec

### Problem

Task 5: Simulate 30% churn in junior managers and experienced supervisors (other levels at 18%) with (a) no external recruiting and (b) promoting only qualified employees, over two years; explain the impact on HR health.

### Analysis

This isolates the middle-management churn problem (issue 4) under a hiring freeze: the two affected levels churn at 30%/yr, all others at 18%, and the only way to refill is internal promotion of qualified incumbents from the level below (qualified share = 0.50, exchange 5). Because external recruiting is off, the senior levels cannot be filled from outside, so the pipeline for the whole chain is throttled by how many qualified people sit one level down. The test is whether the mid-levels can be sustained by promotion alone and what the organization-wide effect is.

### Modeling Process

simulate(case='scenario5', base_churn=0.18, external_recruit=False, only_qualified=True, horizon=2), with churn_rate_for returning 0.30 for 'Junior manager / Executive' and 'Experienced supervisor (Branch)' and 0.18 otherwise. A vacancy in level i is filled by min(open, floor(s_{i+1} * 0.50)) qualified incumbents promoted from level i+1; those incumbents leave level i+1, opening seats there, which then must be promoted from level i+2, and so on down the chain. No external hires, so recruiting cost = 0 and the only training is promotion training (0.3x the level's training cost). Read fill, vacancies, and productivity by year.

### Outcome Analysis

Year 1: 295 staffed (79.7% fill, 75 vacancies). Year 2: 235 staffed (63.5% fill, 135 vacancies). The organization collapses to ~64% fill over two years: promotion alone cannot keep up with 30% mid-level churn plus 18% everywhere else, because each promoted person opens a seat one level down that must itself be filled by promotion, so the deficit cascades down the chain faster than it can be refilled. Recuriting cost is 0 (by assumption), but the real cost is the 210 vacancy person-years and the productivity falling from ~0.80 to ~0.64. HR-health explanation for the supervisor: this scenario is the 'no external recruiting + promote only qualified' worst case — it drains the whole mid-to-lower chain, leaves 135 of 370 seats empty by the end of year 2, and (per exchange 6) pushes the company well into the morale-degradation regime where remaining staff are overworked and churn accelerates. The practical lesson is that a mid-level hiring freeze is not locally contained: it converts a two-level problem into a company-wide staffing collapse, which is why the recommendation (Tasks 6/7) is to reopen targeted external recruiting for the two draining levels rather than rely on internal promotion under a freeze. Limitation: the 0.50 qualified-share is a single estimate; if more of the lower levels are qualified, the collapse is slower but still real, because the chain must be refilled level by level with no external inflow.

## Subtask 6: Task 6: Summarize the potential use of team science and multi-layered networks in fulfilling the HR manager's vision of 

### Problem

Task 6: Summarize the potential use of team science and multi-layered networks in fulfilling the HR manager's vision of connecting the Human Capital network to information-flow, trust, influence, and friendship layers.

### Analysis

The HR manager's vision is a multi-layer (multiplex) organizational network in which the human-capital layer built in Tasks 1-5 is one slice, and the other offices build information-flow, trust, influence, and friendship layers on the same node set (the 370 people / 7 levels). Team science (Salas, Cooke & Rosen 2008; Stokols et al. 2008) supplies the constructs — team coordination, shared mental models, communication quality — that link individual-level turnover to team-level performance, and the Kivelä et al. (2013) multiplex-network framework supplies the mathematics for coupling layers that share nodes but have different edge meanings. The model built here already contains two layers (reporting + friendship), so the extension is a matter of adding the other three layers and a cross-layer coupling term.

### Modeling Process

Let the node set V be the 370 people (or, in the aggregated form, the 7 levels) and the layers G_k = (V, E_k) for k in {capital, information, trust, influence, friendship}, each E_k encoding a different relation (reporting/replacement edges; information-flow edges; trust edges; influence edges; friendship edges). A multiplex network is the tuple (V, E_1..E_m) with a per-layer adjacency A_k. Cross-layer dynamics are captured by a coupling matrix C whose entry C_{kl} weights how a state change on layer l (e.g. a churn event on the capital layer) perturbs the state on layer k (e.g. raises the churn risk via the influence/friendship layers). The churn contagion term already in Task 2, boost_i = 1 + w_c * (churned-neighbour fraction), is exactly a one-step coupling from the capital layer into the churn state via the friendship/influence layers. Adding the other layers means: information-flow layer -> sets how fast a 'blocked' or 'dissatisfied' signal propagates (speeds up or dampens the morale feedback); trust layer -> scales the baseline retention (high trust lowers r_i); influence layer -> the weighted contagion channel (exchange 2 ranked peer/influence ties as the dominant channel). Team science then connects the layer states to team performance: team coordination and shared mental models (Salas et al.) map to a per-team productivity multiplier that the model's workforce-productivity term P(t) can carry, so a layer disruption (a key influencer churns) shows up as a team-level output drop, not just a headcount drop.

### Outcome Analysis

The value to the HR manager's vision is that the human-capital model is already the anchor layer and is extensible without re-derivation: each new office's layer plugs into the same node set and the same coupling matrix, so the HR office can lead the integration (its vision) and quantify cross-layer effects. Concretely, the model can answer 'if we lose the top influencer on the influence layer, how much does team performance and downstream churn move' — a question no single-layer model can answer. Team science supplies the validated team-level constructs so the productivity coupling is defensible. Limitations: (a) building four more layers needs data ICM does not yet have (the other offices are still 'considering' them), so at present only the capital and friendship layers are populated and the rest are structural placeholders; (b) the coupling matrix is small and low-dimensional in the aggregated model, so the multiplex richness Kivelä et al. describe (many layers, many node types) is only sketched, not fully exploited; (c) the framework is a design/summary as the task asks, not a simulation run over five populated layers.

## Subtask 7: Task 7: Report on the organizational model and its function, and the issues the supervisor wants considered (retention, 

### Problem

Task 7: Report on the organizational model and its function, and the issues the supervisor wants considered (retention, the middle-management churn problem, the salary-ratio quality issue, and the path forward).

### Analysis

This is the synthesis. The model's function is to turn ICM's HR data into a forward-looking, quantified picture of churn risk, its budget, its productivity cost, and the interventions that change it. The supervisor's issues are: (1) early churn risk identification; (2) churn diffusing from employee to employee; (3) unused annual performance ratings; (4) middle managers feeling stuck and leaving; (5) the 85%-filled reality and 8-10% active hiring; (6) rigid experience requirements blocking advancement; (7) rising churn, 18% overall; (8) keeping marginal employees to lower churn, degrading quality; (9) the modest CEO-to-worker salary ratio as a cultural asset.

### Modeling Process

The findings, all from the simulations in Tasks 1-5: (a) The network model holds ICM at ~85% fill at the current 18% churn, with middle managers churning at ~36%/yr (2x) — the single largest per-level churn concentration (36 of 370 seats/yr are middle-management). (b) Churn is peer-diffusive: the friendship/peer layer raises a colleague's exit probability after a departure (contagion weight 0.15), so early identification of at-risk nodes (those adjacent to churned former employees) is the cheap intervention the problem's issue 1 calls for. (c) The 2-year talent budget is 159 sigma (recruiting 40.68, training 118.32) — training dominates, so the cheapest lever is keeping and retraining people, not recruiting. (d) 25% churn puts the company exactly at the 80% fill threshold (a warning zone); 35% churn breaks it (steady 76.5%) and is not sustainable. (e) A mid-level hiring freeze (30% churn in junior managers + experienced supervisors, promote-only-qualified, no external recruiting) collapses the organization to 63.5% fill in two years — a hiring freeze is not contained to the mid-levels. (f) On quality (issue 8): the model prices keeping a poor performer at their full salary plus training with no retention benefit, while the all-in replacement cost is ~1.0 annual salary (0.5-2.0); the net effect of 'keeping marginal staff to lower churn' is a slowly degrading workforce that the model can flag by rating — the unused annual evaluations (issue 3) are the missing signal, and exchange 8/9 show top performers are the ones *not* to lose, so retention effort should target high-rated-but-blocked employees, not poor ones. (g) On the salary ratio (issue 9): the modest CEO-to-median ratio (10:1) is a retention asset for good employees; combined with exchange 9 (a promotion path retains better than pay), the recommendation is to preserve the pay-equity culture and invest the retention budget in a visible promotion path rather than in pay raises.

### Outcome Analysis

Recommendations: 1) Identify churn risk early by scoring each employee's adjacency to churned former employees on the peer layer (issue 1, 2); this is the model's most actionable output. 2) Open the promotion path for middle managers (relax the rigid experience gates, issue 6) — exchange 9 says the path, not pay, is what keeps good people, and it directly attacks the 2x mid-level churn. 3) Use the unused annual ratings (issue 3) to separate 'high-rated but blocked' (retain) from 'marginal' (do not spend retention budget on, per exchange 10's caveat) — this addresses the quality problem (issue 8) without the blunt 'keep everyone' policy. 4) Keep targeted external recruiting for the two mid-levels that drain under a freeze (Task 5 showed promotion-only collapses the chain). 5) Fund the 159 sigma two-year budget with training-weighted emphasis, and carry the 25%-churn case as the planning upper band given the rising trend (issue 7). 6) Lead the multi-layer integration (Task 6) so the human-capital model becomes the anchor of the organization-wide network. Overall: the model shows ICM's churn is manageable at 18% and marginal at 25%, but structurally unsustainable at 35% or under a mid-level hiring freeze, and that the highest-leverage, cheapest interventions are retention of high-rated blocked employees and a real promotion path — consistent with the company's low pay-ratio culture. Limitations: single-organization calibration, deterministic churn rates, aggregated (not named-individual) dynamics, and the friendship/influence layer proxied by adjacency — all stated, and all directions that would tighten the model are identified for follow-up data.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
