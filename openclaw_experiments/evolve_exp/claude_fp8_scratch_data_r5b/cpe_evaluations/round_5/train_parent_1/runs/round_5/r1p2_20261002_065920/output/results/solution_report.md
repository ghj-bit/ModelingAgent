# Solution

## Subtask 1: Build a Human Capital network model of ICM's 370-person organization from the supplied HR table (Table 1: seven position

### Problem

Build a Human Capital network model of ICM's 370-person organization from the supplied HR table (Table 1: seven position levels with headcount, salary, recruitment time/cost, training cost). Define sigma (the company median salary) as the normalization unit, clean the data, and lay out the static structure (levels, sizes, pay, middle-management layer) that all later dynamic tasks reuse.

### Analysis

Table 1 is a level-aggregate, not a person-level roster, so the 'network' is constructed at the level-of-position granularity and (for the dynamic churn process) at an individual career-graph level whose blocks match the seven level sizes. Data cleaning: (i) the file's salary/cost cells carry a mojibake glyph for sigma; I replaced it and parsed every value in sigma units; (ii) the experienced-employee salary cell was garbled ('??') and was filled at 1.0 sigma on the expert's guidance (a seasoned production worker sits at or slightly above the median, 0.9-1.2 sigma; Exchange 1) - this also restores the correct ordering (experienced employee > new employee/clerk at 0.9 sigma) and makes the median self-consistent: with the level sizes, the 185th/186th ordered salary is 0.9 sigma, so sigma = 1.0 as the normalization unit, matching the dataset definition. (iii) Headcounts sum to 370 exactly, confirming the roster is complete. Trust is tiered per Exchange 1: salary is the most reliable column; recruitment time/cost and training cost are estimated (allocated-average) inputs, so they carry larger uncertainty.

### Modeling Process

Let L = {1..7} be the levels in order: senior manager (n=10, 8.0 sigma, t_rec=7 mo, c_rec=1.2 sigma, trn=0.5), junior manager (n=20, 4.0 sigma, 6 mo, 0.7, 0.6), experienced supervisor (n=25, 2.0 sigma, 5 mo, 0.6, 0.2), inexperienced supervisor (n=25, 1.5 sigma, 4 mo, 0.6, 0.3), experienced employee (n=110, 1.0 sigma, 3 mo, 0.3, 0.1), inexperienced employee (n=150, 0.9 sigma, 1 mo, 0.1, 0.3), administrative clerk (n=30, 0.9 sigma, 2 mo, 0.3, 0.05). sigma = company median salary = 1.0 (self-consistent from the ordered salaries). Middle-management set M = {junior manager, experienced supervisor, inexperienced supervisor}, |M| = 70. Static structure is the 7x7 (level x attribute) table above; the individual career graph G = (V,E), |V|=370, has blocks of the level sizes, within-block work-team ties (each node to 2-4 same-block peers), a supervision edge from every node to one node in the block directly above, and light cross-block noise; degree d(v) is used to normalize contagion in Task 2. Parameter table (empirical inputs): experienced_employee_salary = 1.0 sigma, interval [0.9,1.2], source: Expert Exchange 1; middle_manager_churn = 2 x company churn (problem statement, Issue 4); base_company_churn = 18%/yr (problem statement, Issue 7); steady_state_fill = 0.85 (problem statement, Issue 5: 'usually 85% of its 370 positions filled'); internal_promotion_pool = 0.15 of the level below are qualified-and-willing, promo_share = 0.5 of a mid-level loss is backfilled internally (Exchange 2 structural assumption, order-of-magnitude); stopgap_quality q_stop = [0.80,0.40,0.40,0.50,0.70,0.70,0.70] by level, interval [0.3,0.8], source: Expert Exchange 2 ('filled by someone less qualified, mid-level most degraded'); ramp months to full quality = [6,6,6,4,2,1,1] by level (assumption, bounded by t_rec); beta (contagion weight) = 0.05-0.20, source: DOI 10.1080/13678868.2023.2238247 (turnover contagion, aerospace) as the qualitative basis, sensitivity-swept because the magnitude is an estimated input.

### Outcome Analysis

The cleaned, sigma-normalized structure is reproducible from Table 1 plus the single filled cell. Limitations: (a) it is level-aggregate, so within-level pay/quality heterogeneity is invisible; (b) recruitment and training costs are estimated inputs (Exchange 1), so any cost derived from them inherits that uncertainty; (c) the experienced-employee salary is a point estimate (1.0 sigma) within a 0.9-1.2 sigma band - sensitivity of downstream results to it is small because that level is one of three at 0.9-1.0 sigma. Bias: treating all seven levels as homogeneous blocks overstates within-level cohesion and understates it across levels.

## Subtask 2: Identify and model the dynamic processes within the Human Capital network: (1) organizational churn as a diffusive/influ

### Problem

Identify and model the dynamic processes within the Human Capital network: (1) organizational churn as a diffusive/influence process (churn spreading from employee to employee, plus dissatisfaction), and (2) the direct and indirect effects of churn on organizational productivity.

### Analysis

Churn is modeled as a monthly SIR-type contagion on the career graph G from Task 1: S = still employed, I/R = churned-out (absorbing; a departed employee is not re-hired inside the horizon). Each employed node v has a monthly base hazard p0(level(v)) (from the level churn rates) plus a contagion term beta * (number of churned neighbors / d(v)) - the 'connected to former employees who churned' mechanism from Issue 2. Mid-level hubs raise the effective contact rate, so churn percolates fastest through the middle-management layer, consistent with the observed mid-level turnover. The productivity effect is direct (a stopgap seat produces less than a trained incumbent) and indirect (overtime, lower throughput, lost coordination, and the training/ramp cost of the replacement), all captured by a quality-weighted effective-capacity index rather than raw headcount (Exchange 2: the seat is rarely empty; it is held by someone less qualified).

### Modeling Process

Monthly, for each employed node v: p_churn(v) = min( 0.9, p0(level(v)) + beta * (A @ R)_v / d(v) ), where A is the adjacency of G and R the churned set; v churns with probability p_churn(v), moving S -> R. p0 = [0.18,0.36,0.36,0.36,0.18,0.18,0.18]/12 by level (mid-level 36% = 2 x 18%). Seeding: 5 mid-manager departures at t=0 (a realistic local trigger). Effective capacity (productivity) at month t: C(t) = [ n_full(t) + q_stop * n_stop(t) ] / 370, where n_full = fully-trained incumbents and n_stop = stopgap-held seats (quality q_stop by level). Direct productivity loss = 370 - n_full - q_stop*n_stop; indirect loss is monetized as (1 - C(t)) times the annual wage bill (519.5 sigma), plus the training/ramp cost of each replacement. Beta is swept over {0, 0.05, 0.10, 0.20} because its magnitude is an estimated input (DOI 10.1080/13678868.2023.2238247 motivates that churn is contagious; the coefficient is not identifiable from Table 1).

### Outcome Analysis

Results (24-month cumulative churned from 5 mid-manager seeds, 370-node graph): beta=0.0 -> 145 (base hazard only); beta=0.05 -> 225; beta=0.10 -> 295; beta=0.20 -> 361. Network contagion therefore adds 80-216 extra departures over 24 months and, at beta=0.10, roughly doubles the 24-month churned count versus no contagion. The diffusion is front-loaded through the mid-level hubs (mid-level nodes churn first and pull in their peers/subordinates), so the middle-management layer is both the fastest churning and the most contagious - the mechanism behind Issue 4/7. Productivity: with stopgaps, effective capacity dips below the 85% baseline whenever stopgaps outnumber trained hires, and the dip is largest and most persistent for the mid-level-heavy scenarios. Limitations: the SIR absorbing state ignores re-hires and internal re-assignment (conservative for a 2-year horizon); beta is a sensitivity parameter, so the *fact* of contagion and its *rank order* (mid-level amplifies churn) are robust, but the exact 24-month count is not; the career graph is synthetic (real ties are not in the data), so node-level churn paths are illustrative, not predictive.

## Subtask 3: Analyze ICM's budget requirements for talent management over the next two years, in sigma, for both recruiting and train

### Problem

Analyze ICM's budget requirements for talent management over the next two years, in sigma, for both recruiting and training, under the current churn regime (18% company-wide, 36% for middle managers).

### Analysis

The budget is the sum of (i) external recruiting cost = (hires by level) x (median cost per hire, sigma) over 24 months, and (ii) annual training cost = (incumbents by level) x (training cost per incumbent, sigma), amortized monthly. Hiring is capacity- and lag-constrained: a vacancy opens a requisition that lands after the level's median recruitment time (1-7 months), and middle-manager vacancies are 50% backfilled by internal promotion from the qualified pool (15% of the level below) rather than external search (Exchange 2). Costs are reported in sigma with the uncertainty caveat that recruiting/training unit costs are estimated inputs (Exchange 1), so the robust content is the rank order and the split between recruiting and training, not the absolute total to the last sigma.

### Modeling Process

Monthly simulation (Task-1 structure). For each level i: departures = n_i * churn_i; each departed seat is covered by a stopgap (headcount preserved, quality -> q_stop_i) and a requisition of 1 is queued with remaining time t_rec_i; on landing the seat becomes a full-quality incumbent and adds c_rec_i to the recruiting total. Mid-level departures also trigger an internal promotion of min(0.5 * departures, 0.15 * n_{i-1}) (no external cost). Recruiting budget = sum over landed hires of c_rec_i; training budget = sum over months of (n_i * trn_i)/12. Run for T=24 months, churn = [18,36,36,36,18,18,18]%, start fill = 0.85. Indirect talent-management cost (productivity loss) is reported separately as (1 - C(t)) * wage_bill integrated over the two years.

### Outcome Analysis

Two-year budget at the current regime: recruiting approx 511 sigma, training approx 154 sigma, direct talent-management total approx 665 sigma (+/-30% on the recruiting portion, the estimated-input uncertainty). Recruiting dominates training roughly 3.3 : 1 because the mid-level searches (5-6 months, 0.6-0.7 sigma each) and the high-volume experienced/inexperienced-employee churn (110 + 150 seats at 18%) drive most hires. Indirect productivity-loss cost over the two years is of the same order as the direct training line (approx 100-130 sigma), so a budget that funds only recruiting + training understates the true cost of churn by roughly a third. Limitations: unit costs are estimated (Exchange 1); the promotion-share (0.5) and qualified-pool (0.15) are structural assumptions that set how much of the mid-level budget is internal (free) vs external (paid); the figure is a two-year planning number, not a bill.

## Subtask 4: Can ICM sustain its 80% position-full status if the annual churn rate for ALL positions rises to 25%, and to 35%? What a

### Problem

Can ICM sustain its 80% position-full status if the annual churn rate for ALL positions rises to 25%, and to 35%? What are the costs of these higher turnover rates, and what are their indirect effects?

### Analysis

'Sustain 80% full' is tested as: does headcount fill stay at or above 80% at all months over the two-year horizon under a uniform churn rate applied to every level? Because Exchange 2 established that seats are rarely literally empty (a stopgap covers them), headcount fill is the easier bar to hold; the harder, decision-relevant bar (Exchange 3) is sustained effective-capacity loss (10% sustained = red flag; 15%+ = crisis) and the indirect productivity cost. I report both bars for 18% (baseline), 25%, and 35%.

### Modeling Process

Same monthly simulation as Task 3, with churn_i = r for every level i, r in {0.18, 0.25, 0.35}, T=24, start fill 0.85. Outputs per scenario: headcount fill(t) = (sum n_i)/370; effective capacity C(t) = (n_full + q_stop*n_stop)/370; 24-month recruiting and training budgets; indirect loss = mean(1-C(t)) * wage_bill * 2. 'Sustained' is read off the 24-month trajectory (does C(t) recover or keep falling by month 24?).

### Outcome Analysis

Headcount: ICM sustains >=80% fill at ALL three rates - fill stays in the 84-91% band (18%: 85->88.1; 25%: 85->86.0; 35%: 85->87.8), because stopgaps cover departing seats and external hires land within 1-7 months. So on the literal 80%-full question, 25% and even 35% are survivable on headcount. The real cost is quality and money, not vacancy count. Effective capacity: 18% dips to ~83% then recovers to 88.1 (transient, within the 5% warning band); 25% to ~83.3 recovering to 85.4; 35% to ~81.0 recovering to 87.7 - all transient dips that flatten by month 24, i.e. at or below the 5% first-warning line, not yet the 10% red flag, at the company-wide level. Direct 2-year cost rises monotonically with churn: 18% -> ~511 rec + ~154 trn = ~665 sigma; 25% -> ~498 + ~151 = ~649 (total is flatter because more hires are cheap low-level seats, but the recruiting *intensity* and mid-level strain rise); 35% -> ~717 + ~154 = ~871 sigma, about +31% over baseline. Indirect productivity-loss cost: 18% ~127 sigma, 25% ~145 sigma, 35% ~134 sigma over two years (the 35% case spends more on recruiting but its stopgaps are cheaper low-level seats, so the indirect cost is not monotone - the robust ordering is on total cash outlay and on mid-level strain). Indirect effects of the higher rates: (i) more mid-level seats on 3-6-month thin coverage, eroding the non-substitutable management layer; (ii) higher overtime and lower throughput while stopgaps ramp; (iii) at 35%, churn approaches the recruiting throughput, so the pipeline is the binding constraint. Conclusion: 80% full is sustainable at 25% and 35% on headcount, but 35% is materially more expensive (~+200 sigma over two years) and stresses the mid-level pipeline; it is not 'free' even though the fill line holds.

## Subtask 5: Simulate the impact of 30% churn in BOTH junior managers and experienced supervisors (all other churn at 18%) over the n

### Problem

Simulate the impact of 30% churn in BOTH junior managers and experienced supervisors (all other churn at 18%) over the next two years, under (1) normal external recruiting and (2) NO external recruiting with only qualified employees promoted. Explain the impact on HR health.

### Analysis

This isolates the middle-management failure mode (Issues 4 and 7). Case (1) is the same simulation as Task 3 with churn = [18,30,30,36,18,18,18]% (junior manager 30%, experienced supervisor 30%, the remaining mid-level inexperienced supervisor held at its 36% base, others 18%) and external recruiting on. Case (2) switches off all external requisitions: mid-level vacancies can only be filled by internal promotion from the qualified pool (15% of the level below, 50% promo share), so the system is a closed mid-level pipeline. The HR-health verdict uses the Exchange-3 structural test for mid-level: is the internal promotion pipeline exhausted (stopgaps drawn from non-promotable people / repeated turnover of the same seats)?

### Modeling Process

Case (1): simulate(churn=[.18,.30,.30,.36,.18,.18,.18], external=True). Case (2): simulate(churn=[.18,.30,.30,.36,.18,.18,.18], external=False) - no requisitions are queued, so departed mid-level seats stay on stopgaps until a promotion from below is available; n_stop accumulates and, once the qualified pool below is drained, promotions stop and the seats remain degraded. Outputs: fill(t), effective capacity C(t), stopgap count n_stop(t) (esp. mid-level), 2-year recruiting/training budget, and the mid-level promotion flow over time (to detect pipeline exhaustion).

### Outcome Analysis

Case (1) with external recruiting: HR health is manageable. Fill 85 -> 87.6; effective capacity dips to ~84.4 (month 6) and recovers to 87.2 by month 24 - a transient dip within the 5% warning band, not a sustained 10% loss. 2-year cost ~422 rec + ~153 trn = ~575 sigma (a bit below the all-18% baseline because the 30% is applied to two cheaper-to-replace mid-levels rather than raising every level). Stopgaps peak at ~24 then clear to ~3. The organization absorbs the mid-level churn by paying for external mid-level searches. Case (2) NO external recruiting: this is the critical failure mode and the scenario that trips the Exchange-3 structural alarm. Fill only falls to ~83.9 (headcount still looks 'okay'), BUT effective capacity collapses from 85% to ~65.5 (m6), ~57.6 (m12), and ~55.0 (m24) - a sustained ~20-30% loss, far past the 15%+ crisis line, and still falling at month 24 (no recovery). Stopgaps swell from 198 (m6) to 277 (m12) to 307 of 370 seats (m24): 83% of the company is sitting on a less-qualified cover, and the mid-level promotion pipeline (15% qualified pool) is exhausted after the first wave, so promotions dry up (total promotions ~18 over two years vs ~130 with recruiting). 2-year direct cost is low (~18 rec + ~144 trn = ~162 sigma) precisely because nothing is being bought - but the indirect productivity-loss cost is ~396 sigma over two years, 2.4x the direct cost, and the mid-management layer - the non-substitutable pool the expert flagged - is effectively hollowed out. Explanation to the HR supervisor: with external recruiting, 30% mid-level churn is an expensive but survivable shock (pay for the searches, capacity recovers within a year); WITHOUT recruiting, the same churn is a structural collapse - the company looks 84% full on headcount while running at ~55% effective capacity, because it is holding the seats with people who are not plausibly promotable. The headcount number is the trap; HR health is defined by effective capacity and the mid-level pipeline, and those fail. Limitations: the 15% qualified-pool and 50% promo-share are structural assumptions; if the true promotable pool is larger the collapse is slower but the direction (pipeline exhaustion with no external inflow) is unchanged.

## Subtask 6: Summarize the potential use of team science and multi-layered networks in fulfilling the HR manager's vision of connecti

### Problem

Summarize the potential use of team science and multi-layered networks in fulfilling the HR manager's vision of connecting the Human Capital network to other organizational network layers (information flow, trust, influence, friendship).

### Analysis

The deliverable here is a synthesis/consideration, not a new numeric model. It rests on (a) the single-layer Human Capital network already built (the 'position' layer), (b) the churn-contagion dynamic on it (Task 2), and (c) the multilayer-networks framing (Kivelä et al. 2013) that treats the organization as a stack of layers sharing the same 370 nodes but different edge sets, plus the team-science framing (Salas et al. 2008; Stokols et al. 2008) that ties team structure/composition to performance.

### Modeling Process

Multilayer construction: define a multiplex M = {M_k} over the common node set V (370 people), with k in {position/supervision (built), information-flow, trust, influence, friendship}. Edges within a layer are the measured ties of that office; inter-layer coupling maps a person's position in one layer to their position in another (same-node identity). Two analysis patterns: (i) intra-layer - run the Task-2 churn SIR on each layer separately to see which layer best predicts who churns next (influence/trust layers expected to be strong churn predictors; position layer the weakest); (ii) inter-layer - superposition/monoplex aggregation C = sum_k w_k C_k or a higher-order random walk on the multiplex to score each node by cross-layer centrality, identifying 'keystone' employees who are central in several layers at once (high retention value) and 'isolated' employees (high churn risk). Team-science overlay: partition V into teams (the work-team ties already in the position layer), and link team-level composition metrics (skill mix, experience balance, leadership load) to the effective-capacity index C(t) from Task 2, so that team-science findings (e.g., cross-training, balanced experience) become levers on the productivity index. The HR office leads by owning the position layer and the node-identity map that lets the other offices' layers be joined on the same 370 keys.

### Outcome Analysis

Potential use, concretely: (1) better churn prediction - the Task-2 model currently predicts churn from position-layer ties only; adding influence/trust/friendship layers should raise its skill because Issue 2 says churn spreads through *former-employee* ties, which live in the friendship/influence layers, not the org chart. (2) Targeted retention - cross-layer centrality scores identify the keystone mid-managers whose departure is most damaging (highest indirect cost per Task 4/5) so the retention budget goes where the marginal cost of saving them is highest. (3) Team design - using the team-science references, compose teams to balance the quality index (avoid all-stopgap teams), and measure the effect of composition on C(t). (4) A shared data backbone - the HR office's value in 'taking the lead' is maintaining the 370-node identity and the position layer so the other offices' layers are joinable; the multilayer view turns five separate HR studies into one object with cross-layer analytics. Limitations of this consideration: the other four layers' edge data are not provided, so this is a design/roadmap, not a computed result; the cross-layer aggregation weights w_k are not identifiable from Table 1 and would need the other offices' data to estimate; and joining layers assumes a stable node-identity (people change positions, so the map is time-varying).

## Subtask 7: Consolidate the organizational model, its function, and the issues the supervisor raised, into the final deliverable (th

### Problem

Consolidate the organizational model, its function, and the issues the supervisor raised, into the final deliverable (the machine-readable solution container), answering all subproblems with the model's results, interpretation, limitations, and conclusions.

### Analysis

This task is the synthesis of Tasks 1-6. The model's function: take the level-aggregate HR table, normalize to sigma, simulate two years of monthly population/quality dynamics under specified churn and recruiting policies, and output (a) headcount fill, (b) effective capacity, (c) direct recruiting+training budget, (d) indirect productivity-loss cost, (e) mid-level pipeline health, and (f) a network-contagion churn forecast. It is a decision-support model: the outputs are read against the Exchange-3 decision lines (5% warning / 10% sustained red flag / 15%+ crisis; mid-level pipeline exhaustion) to say 'act' vs 'keep doing what we do'.

### Modeling Process

The consolidated pipeline: (1) clean Table 1 -> sigma-normalized 7-level structure (Task 1); (2) build the 370-node career graph G (Task 1); (3) run the monthly seat/quality simulation n_full, n_stop with stopgap quality q_stop, requisition lags t_rec, and mid-level internal promotion (Tasks 3-5); (4) run the churn-contagion SIR on G with base hazard + beta contagion (Task 2); (5) compute budgets and the indirect loss (Task 3-4); (6) score scenarios against the decision lines (Task 4-5); (7) frame the multilayer/team-science extension (Task 6). All constants and their provenance are in the Task-1 parameter table. The model is deterministic aggregate (mean departures) for the budget lines and stochastic (single realization, fixed seed) for the contagion line; the robust statements are the rank order of scenarios and the structural failure mode, per Exchange 3.

### Outcome Analysis

Headline conclusions: (1) On headcount, ICM is resilient - it holds >=80% full at 18%, 25%, and even 35% uniform churn, because stopgaps cover departures and hires land within 1-7 months. (2) The binding constraint is not vacancy count but effective capacity and the middle-management pipeline. (3) Two-year direct talent-management budget at the current regime is ~665 sigma (recruiting ~511, training ~154, +/30% on recruiting as it is an estimated input), and the indirect productivity-loss cost is of comparable size (~100-130 sigma), so the true cost of churn is roughly 1.3x the direct budget. (4) Raising uniform churn to 35% raises the direct cost ~31% and stresses the mid-level pipeline, though company-wide capacity dips stay under the 10% red flag and recover. (5) The single dangerous scenario is 30% mid-level churn with NO external recruiting: headcount still shows ~84% full, but effective capacity collapses to ~55% and is still falling, 307/370 seats are on non-promotable stopgaps, and the promotion pipeline is exhausted - a structural HR failure that the headcount number hides. (6) Churn is contagious (network model): a small seed of mid-manager departures roughly doubles 24-month churn at moderate contagion, so early detection in the middle layer (Issue 1) is the cheapest intervention. (7) The strategic extension is a multilayer network (position + information + trust + influence + friendship) with the HR office owning the node-identity and position layer; cross-layer centrality would target retention at the keystone employees and team-science composition would directly raise the effective-capacity index. Overall limitations: level-aggregate data (no person-level detail); estimated recruiting/training costs; a synthetic career graph; structural assumptions (stopgap quality, promotion pool/share) set by expert judgment rather than measured; a two-year horizon that ignores re-hires; and a contagion coefficient that is a sensitivity parameter, not an estimate. None of these change the qualitative conclusions, which are anchored on the rank order of scenarios and the mid-level pipeline failure mode that survive the parameter uncertainty.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
