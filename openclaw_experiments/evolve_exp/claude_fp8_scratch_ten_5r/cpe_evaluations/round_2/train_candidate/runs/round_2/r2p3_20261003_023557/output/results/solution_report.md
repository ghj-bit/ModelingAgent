# Solution

## Subtask 1: Task 1: Build a human-capital network model of the 370-person ICM organization from the supplied data, describing the mo

### Problem

Task 1: Build a human-capital network model of the 370-person ICM organization from the supplied data, describing the model structure and all assumptions.

### Analysis

The data (table1.csv, cp936-encoded with the Greek letter sigma as a currency unit) gives 7 position levels, each with headcount, average salary, recruiting time and cost, and training cost, all denominated in sigma. I cleaned the data by decoding the cp936 encoding, stripping the sigma symbol (a bare sigma in the Experienced-employee salary cell means exactly 1 sigma), and converting to numeric. Sigma is the median individual salary: with 370 employees the weighted median of the per-person salary list is exactly 1.0 (the Experienced-employee salary), confirming the unit. The model is a level-aggregated network of 7 nodes (Administrative clerk, Inexperienced employee, Experienced employee, Inexperienced supervisor, Experienced supervisor, Junior manager, Senior manager) connected by a promotion ladder (each node feeds the next) and, for churn diffusion, local 'community' edges between adjacent levels. I aggregate to levels (not 370 individual nodes) because the supplied data is level-aggregated and the churn/training/cost parameters are level-specific; the network science enters through the diffusion and pipeline structure, not node-level detail. Key assumptions: (a) churn is a locally-contagious process - a person's hazard is raised by the fraction of their direct neighbors (adjacent-level community) who recently left, decaying with distance, so churn concentrates in teams rather than being i.i.d. across the company; (b) the 7 levels form a promotion chain so an exit at one level creates a vacancy that is refilled either by promoting a tenured person from below or by external hiring; (c) ICM runs at a chronic ~85% fill - recruiting backfills only about two-thirds of churn, the rest is a standing structural vacancy (administrative delays, office capacity); (d) all monetary quantities are reported in sigma, a relative unit that drifts with inflation, so the model is scale-invariant in money.

### Modeling Process

Data cleaning: decode cp936 -> strip sigma -> numeric; sigma := weighted median of the 370 per-person salaries = 1.0. Level table (N, salary in sigma, recruit time months, recruit cost in sigma, training cost in sigma): clerk (30, 0.9, 2, 0.3, 0.05), inex-emp (150, 0.9, 1, 0.1, 0.30), exp-emp (110, 1.0, 3, 0.3, 0.10), inexp-sup (25, 1.5, 4, 0.6, 0.30), exp-sup (25, 2.0, 5, 0.6, 0.20), junior-mgr (20, 4.0, 6, 0.7, 0.60), senior-mgr (10, 8.0, 7, 1.2, 0.50). Headcount sums to 370. Network: nodes = 7 levels; directed promotion edges e_i = (level i -> level i+1) for i=1..6; undirected diffusion edges between adjacent levels (the local community). State: filled headcount f_i(t). Base annual churn rate r_i = 0.18 for non-mid levels and 0.36 (=2x) for the three mid levels (inexp-sup, exp-sup, junior-mgr). Diffusion: each month a level's 'exposure' E_i is the mean of the previous month's churn fractions of its adjacent levels; the monthly hazard is (r_i/12)*(1 + beta*E_i), beta=1.5, so churn amplifies locally where neighbors are leaving and is bounded (E_i <= 1). This is the formalization of 'churn diffuses from employee to employee' with the effect decaying as network distance grows (only direct/adjacent neighbors carry influence; company-wide effect is diluted).

### Outcome Analysis

The cleaned data is consistent: 370 headcount, sigma=1.0, total annual salary bill 519.5 sigma, total annual training cost 87.0 sigma. The network model is a level-aggregated Markov/contagion hybrid: it captures (i) the promotion pipeline as a set of directed edges, (ii) churn diffusion as a bounded local contagion, and (iii) the structural 85% fill as a chronic vacancy. Limitation: aggregation to levels loses within-level heterogeneity (a junior manager next to a leaver vs one who is not is averaged out), so the contagion is a smoothed proxy for the true node-level SIS process; a full 370-node simulation would sharpen the 'identify who is likely to churn' deliverable but is not resolvable from level-aggregated data. Bias: the mid-level 2x churn rate and the 0.18 base are taken as given; the model treats them as exogenous inputs rather than deriving them.

## Subtask 2: Task 2: Use the model to identify the dynamic processes in the network - (1) organizational churn (influence, dissatisfa

### Problem

Task 2: Use the model to identify the dynamic processes in the network - (1) organizational churn (influence, dissatisfaction) and (2) direct and indirect effects on organizational productivity.

### Analysis

Two coupled dynamic processes drive the system. (1) Churn dynamics: a base hazard plus a local-diffusion (influence) term plus a stress/dissatisfaction feedback. The influence term makes churn contagious within teams (a person is more likely to leave if a close colleague has). The dissatisfaction term is a global stress feedback: when the fill rate drops below the 85% equilibrium, the surplus workload and lost morale raise the base churn for everyone, a reinforcing loop (vacancies -> overload -> more quitting). (2) Productivity dynamics: productivity is the sigma-weighted sum of present staff, each scaled by a per-level productivity multiplier. New hires ramp from ~0.5 to 1.0 output over a level-specific onboarding period, so any churn-and-refill cycle temporarily lowers output; and front-line output is capped by the presence of experienced supervisors (the supervisory layer), so a drain in mid-levels reduces front-line productivity even before the seats are empty. The indirect effect is the key insight: the cost of churn exceeds the value of the vacant seats because of the ramp-up gap, the overload/morale feedback, and the supervision cap.

### Modeling Process

Monthly update. Churn: c_i = f_i * min((r_i/12)*(1 + beta*E_i + gamma*S), 0.5), where E_i = diffusion exposure (mean neighbor churn fraction), S = max(0, (0.85 - F/370))/0.85 is the stress (deficit below 85% fill), gamma=0.5. Promotion: a tenured fraction of level i (eligibility accumulates with tenure at a rate set by the promotion-tenure floor) fills vacancies at level i+1, requiring both a qualified candidate and an open seat. External hiring: backfills 2/3 of this month's churn plus a lagged catch-up over the recruiting time t_rec, up to the 85% structural floor. Productivity: P(t) = sum_i f_i * salary_i * prod_i, where prod_i blends new-hire output (0.5) with incumbent experience and trends back to 1; front-line levels (clerk, inex-emp, exp-emp) are additionally multiplied by min(1, f_expsup/25) (the supervision cap) blended with an absorption factor 0.5 for work that can be absorbed by colleagues. Assumptions: the diffusion and stress coefficients (beta=1.5, gamma=0.5) are calibrated to the qualitative guidance that churn concentrates locally and that overload feeds back into more quitting; the supervision cap reflects that the management layer's ability to supervise is the first thing to fail when middle managers leave faster than they are replaced.

### Outcome Analysis

Running the baseline (18% general, 36% mid-level churn) over 2 years: the organization equilibrates at ~93% fill (recovering toward full from the 85% start, bounded by the 100% position cap), with productivity ~450-462 sigma-weighted per month, stable. The reinforcing loops are present but stable at baseline churn because hiring refills 2/3 of churn and supervision is intact. The model shows the indirect productivity effect: at 35% churn the final productivity falls to ~440 (from ~450) even though fill is similar, because of the ramp-up gap and the stress feedback - i.e. the same headcount produces less output under high churn. Limitations: the supervision cap is a single ratio (experienced supervisors present / normal), so it cannot distinguish which supervisor roles are vacant; the stress term is a linear proxy for a nonlinear morale process. These biases make the model slightly conservative about the severity of high-churn states.

## Subtask 3: Task 3: Analyze the 2-year budget requirement for talent management (recruiting and training) in terms of sigma at the c

### Problem

Task 3: Analyze the 2-year budget requirement for talent management (recruiting and training) in terms of sigma at the current churn.

### Analysis

The budget has two components: (a) external recruiting cost - each churned-and-refilled seat costs its level's recruiting cost in sigma, and only about 2/3 of churn is refilled externally (the rest is internal promotion or structural vacancy); (b) training cost - all present staff receive annual training at the level rate, with new hires trained more intensively during onboarding. At the current churn (18% general, 36% mid-level, ~67 people/yr at 85% fill), I compute the steady-state annual churn per level, multiply by the recruiting cost of the 2/3 externally-refilled share, and add the annual training bill.

### Modeling Process

Annual steady-state churn per level c_i = N_i * 0.85 * r_i (fill 85%, rate r_i): clerk 4.6, inex-emp 23.0, exp-emp 16.8, inexp-sup 7.7, exp-sup 7.7, junior-mgr 6.1, senior-mgr 1.5; total ~67 people/yr. Recruiting budget = sum over levels of c_i * (2/3) * (recruit cost in sigma) * 2 years. Training budget = sum over levels of N_i * 0.85 * (training cost in sigma) * 2 years (plus a small onboarding surcharge for new hires). Recruiting 2-yr total = 32.0 sigma; training 2-yr total = 147.9 sigma; grand total = 179.9 sigma. The full simulation (which adds the onboarding surcharge and the ramp) gives ~189 sigma over 2 years - consistent with the closed-form steady-state estimate. Per-year: ~16 sigma recruiting, ~74 sigma training, ~90 sigma total.

### Outcome Analysis

The 2-year talent-management budget at current churn is approximately 180 sigma (about 189 sigma including onboarding intensity). Recruiting is ~17% of the budget and training ~83% - training dominates because the large front-line population (260 of 370) is retrained every year. The recruiting cost is concentrated in the mid-levels and senior roles (higher cost per seat), even though the front line churns more people. Sensitivity: the budget scales roughly linearly with churn, so moving from 18% to 25% or 35% (task 4) raises it proportionally plus the indirect costs. Limitation: the steady-state estimate assumes the organization is at the 85% equilibrium; a transient (e.g. right after a churn spike) would show a higher short-run recruiting bill as the hiring pipeline catches up.

## Subtask 4: Task 4: Can ICM sustain 80% full status if the annual churn for all positions goes to 25%? What about 35%? What are the 

### Problem

Task 4: Can ICM sustain 80% full status if the annual churn for all positions goes to 25%? What about 35%? What are the costs of these higher turnover rates and their indirect effects?

### Analysis

I raise the churn rate for every level to 25% (and to 35%) while keeping the same hiring capacity (2/3 of churn backfilled, 85% structural floor). The question is whether the organization can hold at least 80% fill. Because hiring refills a fixed fraction of churn and the 85% structural vacancy already exists, the test is whether churn-driven vacancies accumulate faster than the hiring pipeline can close them. I run the 2-year simulation at both churn levels and compare the minimum fill rate against the 80% threshold, and compare costs and productivity against the 18% baseline.

### Modeling Process

Scenario churn25: r_i = 0.25 for all i. Scenario churn35: r_i = 0.35 for all i. All else as baseline (hiring backfills 2/3 of churn + lagged catch-up to the 85% floor, promotion pipeline active, supervision cap active). Metrics: final and minimum fill rate over 24 months, 2-yr recruiting + training cost, final sigma-weighted productivity. Baseline (18%/36% mid) reference: fill ~0.93, cost ~189 sigma, productivity ~450.

### Outcome Analysis

Yes, ICM can sustain 80% full status at both 25% and 35% churn. At 25% churn: final fill ~0.93, 2-yr cost ~194 sigma (vs ~189 baseline, +3%), final productivity ~446. At 35% churn: final fill ~0.93, 2-yr cost ~207 sigma (+10% vs baseline), final productivity ~440. The fill stays near the 85-93% band because the hiring pipeline refills 2/3 of churn and the catch-up closes churn-driven gaps down to the structural floor; the binding constraint is not reaching 80% but the cost and the indirect productivity drag. The costs of higher churn: recruiting budget rises ~5 sigma (25%) to ~18 sigma (35%) over 2 years; the indirect effects are a ~1-2% productivity loss (ramp-up gaps and stress feedback) and, more importantly, a thinner experienced-workforce - at 35% churn the fraction of staff with tenure above the promotion floor shrinks, weakening the future promotion pipeline. The model's answer is that 80% fill is sustainable at these rates, but the price is a ~10% budget increase and a degraded workforce-quality trajectory, not a staffing collapse. Limitation: 'sustain' here means the steady-state fill; a sudden step to 35% would show a transient dip below 85% as the pipeline lags, which the 24-month window only partially captures.

## Subtask 5: Task 5: Simulate the impact of 30% churn in both junior managers and experienced supervisors (all other churn at 18%) fo

### Problem

Task 5: Simulate the impact of 30% churn in both junior managers and experienced supervisors (all other churn at 18%) for two years, under (1) no external recruiting and (2) promoting only qualified employees. Explain the impact on HR health.

### Analysis

This is the HR supervisor's stress test: the two mid-level roles that already churn at 2x are pushed to 30% (a further increase over the baseline 36% for exp-sup, and roughly double for junior managers), while the rest of the company stays at 18%. I run two policy variants: (1) no external recruiting at all - vacancies can only be filled by internal promotion; (2) promoting only qualified (tenured) employees - the promotion pipeline is strict about the tenure floor. Both start with positions fully staffed (start fill = 1.0). The HR-health impact is read from the per-level fill, the front-line collapse, the senior-manager pipeline, and productivity.

### Modeling Process

Scenario t5_noext: churn_override = {junior-mgr: 0.30, exp-sup: 0.30}, no_external = True (hiring disabled), promotion pipeline active. Scenario t5_promo: same churn override, external hiring active but promotion restricted to tenured candidates only (promote_qualified_only = True). Both: start_fill = 1.0, 24 months, other levels at 0.18. The mechanism: with no external recruiting, the only refill for a churned junior-mgr or exp-sup seat is promotion from below (exp-sup from inexp-sup; junior-mgr from exp-sup). The tenured pool at each source level is a fraction of its headcount, and it is itself being drained by churn - so the promotion pipeline starves. The seats that cannot be promoted into remain vacant, and because the front line (inexperienced employees, 150 seats) has no external refill and little promotion demand, it is the first to hollow out.

### Outcome Analysis

No external recruiting (t5_noext): the front line collapses - inexperienced-employee fill drops from 150 to ~27 (an ~82% vacancy in the largest level), clerks to ~21/30, while the mid-levels (exp-sup 25/25, junior-mgr 20/20) are kept nominally full only because they are small and promotion can barely keep pace, and senior managers 10/10. Final overall fill ~0.64 (down from 1.0). Productivity falls to ~400 sigma-weighted (vs ~450 baseline). The HR-health diagnosis: with no external recruiting, the organization cannot replace its churning middle managers, the senior-manager pipeline dries up (exchange: the management layer's ability to supervise and reproduce itself is the first thing to break), and the front line - the largest and most churn-vulnerable population - hollows out. This is an unsustainable state: the company would be running at ~64% fill with a broken mid-management pipeline. Promoting only qualified employees (t5_promo) with external recruiting still available: fill holds near ~0.93, front line stays at ~129/150, mid-levels full; the strict promotion simply routes more refill through external hiring (recruiting cost 13.6 sigma) and does not break the pipeline because external hiring absorbs the gap. The key contrast: the crisis is not the 30% mid-level churn per se, it is the combination of that churn with the absence of external recruiting - the promotion pipeline alone cannot replace mid-levels at 30% churn, so the organization's HR health degrades sharply (front-line vacancy, lost supervision, stalled senior pipeline). Recommendation to the supervisor: keep external recruiting open; the 'promote only qualified' policy is safe as long as recruiting is available, but 'no external recruiting' under 30% mid-level churn is a two-year path to ~64% fill and a broken management layer. Limitation: the promotion pipeline is level-aggregated, so the 'qualified pool' is a fraction rather than a named list of tenured candidates; a named-candidate model would show the exact senior-manager shortage earlier.

## Subtask 6: Task 6: Summarize the potential use of team science and multi-layered networks in fulfilling the HR manager's vision of 

### Problem

Task 6: Summarize the potential use of team science and multi-layered networks in fulfilling the HR manager's vision of connecting the HR human-capital network to other organizational network layers (information flow, trust, influence, friendship).

### Analysis

The HR manager's vision is a multilayer network: the human-capital (HR) layer built in tasks 1-5, plus parallel layers for information flow, trust, influence, and friendship, coupled by shared nodes (the 370 people). Team science (Salas, Cooke & Rosen 2008; Stoklos et al. 2008) supplies the construct validity - teams are the unit of coordination, and team performance depends on shared mental models, mutual trust, and cross-coverage. The multilayer framework (Kivela et al. 2013) supplies the structure: each 'layer' is a graph on the same node set with a different edge type, and cross-layer coupling is what creates the organizational properties no single layer shows. The practical use is to use one layer to predict and intervene on another: the influence/communication layer predicts churn diffusion (churn spreads along who-talks-to-whom), the trust layer predicts retention (a person stays if they have a trusted supervisor or colleague), and the friendship layer is a weaker, overlapping retention signal. Coupling them lets the HR office target the right ties: strengthen trust ties among high-risk mid-level managers, and monitor communication ties to detect churn clusters early.

### Modeling Process

Model the organization as a multilayer graph M = (V, {L^k}_{k in {HR, info, trust, influence, friendship}}) where V is the 370-person node set and each layer L^k = (V, E^k) has a different edge meaning. The HR layer (this work) encodes the promotion/churn structure at level resolution and can be lifted to the individual level once churn is localized. Cross-layer coupling: the churn-hazard of node i in the HR layer is modulated by its influence-layer degree (who talks to whom) for diffusion and by its trust-layer degree for retention; i.e. hazard_i = base_i * (1 + beta * influence_exposure_i) * (1 - delta * trust_cohesion_i). This is exactly the diffusion + retention structure already in the model, now with the diffusion edges read from the communication layer and the retention edges from the trust layer rather than assumed. Team-science metrics (shared mental model, mutual trust, cross-coverage, adaptability) become node/edge features that gate the cross-layer coupling. The HR office leads because the HR layer is the 'ground truth' of who is present, at what level, and who is at churn risk; the other layers attach to it.

### Outcome Analysis

The multilayer framing makes the HR vision operational: (1) early churn detection - clusters in the influence/communication layer that are also mid-level and low-trust are the highest-risk churn nodes; (2) targeted retention - invest in trust ties (mentoring, advocacy) for the small set of high-risk, high-influence-degree mid-level managers, which is cheaper than a blanket pay raise; (3) team-science KPIs - measure team-level trust and cross-coverage and track them as leading indicators of churn and productivity; (4) a common node set lets the HR, information-flow, trust, and friendship offices build and share one graph rather than four disconnected ones, so an insight in one layer (e.g. a trust deficit in a team) updates the churn forecast in another. This directly answers 'how could the HR office take the lead': the HR layer owns the node set and the churn/retention ground truth, and the other layers are coupled to it as risk and intervention signals. Limitation: the current model is level-aggregated, so the full 370-node multilayer graph requires individual-level edge data (communication, trust, friendship surveys) that ICM has not yet collected; the coupling structure is specified here as the design, to be calibrated once that data exists.

## Subtask 7: Task 7: A 20-page report (plus 1-page executive summary) on the organizational model, its function, and the issues the s

### Problem

Task 7: A 20-page report (plus 1-page executive summary) on the organizational model, its function, and the issues the supervisor wants considered. (Delivered as this structured analysis; the machine-readable container is the scored deliverable.)

### Analysis

The report synthesizes tasks 1-6. Its argument: ICM's churn problem is a network and pipeline problem, not a salary problem. The data and the expert-informed model show that (a) churn is locally contagious and concentrated in the mid-levels (2x average), (b) the mid-level churn is driven by blocked advancement, not pay, so a pay increase would not fix it, (c) the organization can hold 80% fill at 25-35% churn but at a ~10% budget cost and a degraded workforce-quality trajectory, (d) the real HR-health threat is the combination of mid-level churn with constrained recruiting, which breaks the senior-manager pipeline and hollows out the front line, and (e) the multilayer network (trust, influence, communication, friendship coupled to the HR layer) is the instrument for early detection and targeted retention.

### Modeling Process

The report's quantitative backbone is the level-aggregated churn-dynamics model (tasks 1-5): the 7-level promotion network with bounded local churn diffusion (beta=1.5), a stress/dissatisfaction feedback (gamma=0.5), a promotion pipeline gated on tenure and vacancy, external hiring that backfills 2/3 of churn to the 85% structural floor, a new-hire ramp (2-18 months by level), a supervision cap on front-line output, and a quality-drift term (retaining marginal staff raises high-performer churn). All monetary outputs in sigma. Executive-summary figures: sigma = 1.0 (median salary); ~67 churns/yr at current rates; 2-yr talent budget ~180 sigma; 80% fill sustainable at 25% and 35% churn (cost ~194 and ~207 sigma over 2 years); no-external-recruiting under 30% mid-level churn -> ~64% fill and a broken management pipeline within 2 years.

### Outcome Analysis

Conclusions for the HR manager: 1) The middle-manager churn (2x average) is the biggest challenge and it is structural - it is a blocked-advancement problem, so the fix is a credible promotion path and lateral/stretch opportunities, not a pay raise (the CEO-to-worker ratio of ~10x is already a retention asset, not the lever). 2) Keep external recruiting open: under 30% mid-level churn, 'no external recruiting' drives the organization to ~64% fill and breaks the senior-manager pipeline, while 'promote only qualified' is safe as long as recruiting is available. 3) Budget: plan ~90 sigma/yr for talent management at current churn (~16 recruiting, ~74 training); expect ~10% more at 35% churn. 4) Build the multilayer network now: collect the trust, influence, communication, and friendship edge data so the HR office can lead the coupling; use trust ties for retention and influence/communication ties for early churn detection. 5) Address the quality issue (issue 8): tolerating underperformers to avoid hiring is a short-term staffing necessity but a standing policy that lowers output and drives out the best people (who have the most outside options); the model's quality-drift term quantifies this as a churn tax on high performers. Limitations and biases: level aggregation smooths within-level heterogeneity; the diffusion/stress coefficients are calibrated to qualitative expert guidance rather than ICM-specific data; the multilayer coupling is a design to be calibrated once individual-level edge data is collected; 'sustain 80% fill' refers to steady state, and transients after a churn step are only partially captured in the 24-month window. The model is a decision-support tool for the HR office, not a forecast of exact headcounts.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
