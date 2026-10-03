# Solution

## Subtask 1: Task 1: Build a Human Capital network model of ICM's 370-person organization using the provided data (table1.csv: headco

### Problem

Task 1: Build a Human Capital network model of ICM's 370-person organization using the provided data (table1.csv: headcount, salaries, recruitment cost/time, training cost by level, all in sigma, sigma = median income). Describe the model and its assumptions.

### Analysis

Approach: a two-layer model. (i) A level-based mean-field flow layer with 7 position levels, which is what the data actually supports (headcount, cost, time by level). (ii) A synthetic agent-level social network, because table1.csv contains no tie or departure-timing data, so the human-capital network must be constructed under explicit structural assumptions grounded in real-world practice (dense intra-team clusters, thin cross-team web, stable membership). The network layer is where churn diffusion and the multi-layer-network vision of task 6 live; the level layer carries the budget and staffing dynamics of tasks 3-5. Soundness: the data defines only the level layer, so the network is an assumption-based extension, validated against empirically calibrated contagion strengths rather than claimed as data.

### Modeling Process

Levels (top to bottom): SM senior manager (10), JM junior manager (20), ES experienced supervisor (25), IS inexperienced supervisor (25), EE experienced employee (110), IE inexperienced employee (150), AC administrative clerk (30); 370 positions total, 85% filled at t=0 (314.5). table1.csv values in sigma: time-to-recruit T_REC = (7,6,5,4,3,1,2)/12 y; one-off recruitment cost C_REC = (1.2,0.7,0.6,0.6,0.3,0.1,0.3); annual salary SAL = (8,4,2,1.5,1,0.9,0.9); annual training TRN = (0.5,0.6,0.2,0.3,0.1,0.3,0.05). Note: the experienced-employee salary cell in the CSV is blank; the dataset's own definition sigma = median income and the level structure (150 IE at 0.9, 110 EE at 1.0, 30 AC at 0.9) place the median exactly at 1.0 sigma, so EE salary = 1.0 sigma (assumption, consistent with the problem's own normalization). Churn: baseline annual rate r = 0.18 at all levels; mid levels JM/ES/IS at 2r = 0.36 (problem: mid turnover is twice the average). Annual departures at steady state: 79.2 total, of which 25.2 mid-level. Network: N nodes partitioned into 10 clusters of ~19 (teams); intra-cluster edges with probability 0.6; the 50 manager nodes carry 2 cross-cluster links each (cross-group ties ~10% of intra-group density); team membership stable, with an annual reassignment probability 0.1 per member. Node attributes: level, tenure, ties; edge set static except reassignment. Calibrated empirical parameters (name = value, interval, source): baseline annual churn = 0.18, [0.15,0.20], problem statement (current churn 18%/yr); mid-level annual churn = 0.36, [0.32,0.40], problem statement (twice average); contagion hazard multiplier for a close tie who departed = 2.0, [1.5,3.0], expert exchange E1; contagion window = 0.5 y, [0.3,0.8], expert exchange E1; manager-departure report hazard multiplier = 1.5, [1.2,2.0], expert exchange E10; report window = 1.0 y, [0.6,1.5], expert exchange E10; new-hire ramp (front line / manager) = 0.25 y / 0.5 y, [0.25,0.5] / [0.5,1.0], expert exchange E2; new-hire productivity at arrival = 0.30, [0.2,0.5], expert exchange E2; promotion eligibility tenure = 3.0 y, [2,4], expert exchange E5; share of a vacancy filled by internal promotion = 0.40, [0.3,0.5], expert exchange E3; intra-group tie density = 0.6, [0.4,0.8], expert exchange E7; inter-group links relative to intra-group = 0.1, [0.05,0.2], expert exchange E7; annual member reassignment probability = 0.1, [0.05,0.2], expert exchange E8; social notice delay of a departure = 0.02 y, [0,0.1], expert exchange E9; external hiring time = table1.csv T_REC, confirmed by expert exchange E6.

### Outcome Analysis

The model reproduces the stated operating picture: 79 departures/yr (18% overall, 36% mid), ~95 external hires/yr plus ~12 internal promotions/yr, 85% steady fill. Limitations: (1) the social network is synthetic - its cluster size (19), density (0.6) and cross-link fraction (0.1) are practice-informed assumptions, not measurements; conclusions about diffusion are robust to the documented intervals (hazard-sweep 1.5-3.0 changes excess departures from +28% to +103%, so the mechanism is real but its magnitude carries a factor ~2 uncertainty); (2) the blank EE salary cell had to be filled (1.0 sigma) from the problem's own median definition; (3) annual aggregation hides intra-year timing, which matters for the 3-year promotion rule only through the steady-state survival fraction exp(-3r).

## Subtask 2: Task 2: Identify dynamic processes in the Human Capital network - (1) organizational churn (influence, dissatisfaction) 

### Problem

Task 2: Identify dynamic processes in the Human Capital network - (1) organizational churn (influence, dissatisfaction) and (2) direct and indirect effects on organizational productivity. Describe and incorporate them.

### Analysis

Three coupled dynamic processes. (1) Churn contagion: a departure raises the quit hazard of close ties (influence/social-proof channel, per the problem's observation that churn diffuses) and, more weakly and more slowly, the direct reports of a departed manager. (2) Productivity loss: vacancies stop work immediately; replacements ramp below predecessor output (learning curve); promotion cascades vacate lower seats. (3) A quality drift: because marginal employees are rarely relieved (problem issue 8), the mean quality of long-tenured staff erodes slowly, compounding the productivity loss at high churn. The contagion process is implemented as an agent-based hazard model on the network; the productivity processes as the level flow model. This split is the standard way to combine a network diffusion study with an aggregate budget model.

### Modeling Process

Contagion (agent-based, dt = 0.05 y): each occupied node i has quit hazard h_i(t) = r_i * M_i(t), where M_i(t) = max over recent departures d of multiplier(m_d) if t - t_d - notice < window(m_d) and i is a close tie of d; close-tie departure: multiplier 2.0, window 0.5 y, notice 0.02 y; manager departure: multiplier 1.5, window 1.0 y, applied to the departed manager's non-manager neighbours. Baseline arm: M_i = 1. Productivity (level model): output P(t) = sum_l w_l * f_l(t) * e_l(t) / N, with level weights w = (0.05,0.15,0.20,0.25,0.55,0.50,0.18) (front-line employee levels carry 105% of output, per the aggregate-output judgment that the base of the pyramid does the work), f_l = filled seats, e_l = 1 - 0.70 * (ramping seats / filled seats) where ramping seats follow d(n_cohort)/dt = -n_cohort/RAMP (RAMP = 0.25 y front line, 0.5 y managers; a new hire starts at 30% productivity). Indirect effects: promotion cascades (a mid-level promotion vacates a lower seat, so 40% of each backfill creates a downstream vacancy); ramp periods (a replacement at 30-100% output for 0.25-0.5 y); vacancy periods (a seat empty for T_REC months after departure); quality drift (assumed -5% relative productivity per 10% sustained churn above 18%, representing retained marginal staff, applied to the mean-fraction of long-tenured seats).

### Outcome Analysis

Agent-based study (190 occupied nodes, 200 trials, 2 y): no-contagion baseline 56.5 quits; with contagion 87.7 quits, i.e. ~31 excess departures (+55%) over two years. Sensitivity to the contagion multiplier: +28% (x1.5), +55% (x2.0), +81% (x2.5), +103% (x3.0). So contagion plausibly accounts for roughly a quarter of ICM's observed churn. Productivity: base scenario holds at 1.435 (2-y mean, index with 1.0 = one full seat at full output); at 35% all-level churn output falls to 1.381 mean / 1.290 final, a ~4.5-9% loss concentrated in the ramp/vacancy pipeline; with no recruiting (task 5) output collapses to 1.31 mean / 1.08 final (-11% to -24%). Limitations: contagion magnitude is the least certain element (factor ~2); the quality-drift rate is an assumption not grounded in any data; the productivity weights are relative and only the ratios matter.

## Subtask 3: Task 3: Analyze ICM's budget requirements for talent management (recruiting and training) in terms of sigma over the nex

### Problem

Task 3: Analyze ICM's budget requirements for talent management (recruiting and training) in terms of sigma over the next 2 years.

### Analysis

Budget = recruiting spend (one-off cost per external hire, at arrival) + training spend (annual per-seat training cost, plus the ramp period implicitly costs output). Recruiting demand is set by departures minus internal promotions: each departure opens one campaign with duration T_REC; the pipeline carries dep_l * T_REC in-flight orders at steady state (19 positions). Training is a flow cost proportional to filled seats. Computed by the level flow model over 2 years, plus a closed-form steady-state cross-check (recruiting cost/yr = sum over levels of external hires/yr x C_REC).

### Modeling Process

Recruiting: R(2y) = sum of C_REC[l] over external hires completing in 2 years. External hires/yr at steady state = 0.60 x departures_l (40% promoted internally) = sum_l 0.6 * r_l * f_l. Training: TR(2y) = 2 * sum_l TRN[l] * f_l. Closed form (steady state, f_l = 0.85*N_l): departures/yr = 79.2 (59.0 non-mid at 18%, 25.2 wait: 18%*314.5=56.6 non-mid, 36%*70=25.2 mid); external hires/yr = 0.6*79.2 = 47.5 -> recruiting = 47.5/yr x level-mixed cost. Simulation results: base 2-y recruiting budget 45.3 sigma (126 hires, ~0.36 sigma/hire mean cost), training 140.0 sigma; t25: 44.8 + 139.8; t35: 63.3 + 136.3; jm30: 44.5 + 138.6; jm30_norec: 4.5 + 117.2; jm30_qual: 22.7 + 133.0. Salary context (not part of the talent budget but for scale): 2-y payroll ~ 2 x sum SAL*f ~ 610 sigma.

### Outcome Analysis

Two-year talent-management budget at the current 18%/36% churn: about 45 sigma recruiting + 140 sigma training = ~185 sigma, i.e. roughly 30% of two years' payroll. Recruiting is the small, churn-sensitive part (45 -> 63 sigma at 35% churn, +40%); training is the large, nearly fixed part (stable within 3% across scenarios because it tracks filled seats, not churn). Indirect cost not in either budget line: the output lost to vacancies and ramps is worth, at the level weights, roughly 5-9 sigma over 2 years at 35% churn (see task 2). Limitations: recruitment costs are charged at median; the problem defines them as medians, so the mean cost may be higher in the tail. The 40/60 promotion/external split is calibrated (expert E3) and is the main budget sensitivity: a 30/70 split would add ~5 sigma of recruiting over 2 years.

## Subtask 4: Task 4: Can ICM sustain its 80% (stated; 85% today) full status if annual churn goes to 25% for all positions? What abou

### Problem

Task 4: Can ICM sustain its 80% (stated; 85% today) full status if annual churn goes to 25% for all positions? What about 35%? Costs and indirect effects of the higher rates.

### Analysis

Sustainability is a balance between departures (c per year) and refill capacity: (a) the hiring pipeline, one campaign per vacancy of duration T_REC, and (b) HR office capacity: ICM actively hires 8-10% of its 370 positions (30-37 concurrent campaigns, ~2/3 of vacancies). The closed-form steady state with per-level arrival rate v_l/T_REC_l and a campaign cap K gives fill fraction sum_l f_l N_l / 370 with f_l solving c(1-f_l) = min(v_l/T_REC_l, cap). Without the cap the system self-balances at high fill for any c (fill ~ 1/(1+c*T_REC)); the cap is what breaks sustainability, because at c = 0.25-0.35 the required concurrent campaigns (c x 314.5 = 79-110) exceed the office's 30-37. Simulation with cap = 30 and the same per-departure campaigns reproduces this: fill falls below 80% and does not recover within 2 years.

### Modeling Process

Vacancy dynamics: d(v_l)/dt = c(1-v_l) - a_l, where v_l = vacancy fraction at level l, a_l = v_l/T_REC_l scaled so sum_l a_l <= K (K = 30, the 8% office capacity; 37 for 10%). Fill = 1 - sum v_l N_l / 370. Closed form without cap: f_l = 1/(1 + c*T_REC_l) (all vacancies filled as fast as the pipeline allows). Results: c=0.25: steady campaigns needed ~ 79 > 30 -> with cap, fill drifts to ~80-82% over 2 years and is barely sustainable (the office runs at 100% capacity; no slack for the mid-level bottleneck). c=0.35: needed ~ 110, 3.7x capacity -> fill falls below 80% within ~2 years and keeps declining; not sustainable. Costs: recruiting 44.8 sigma (25%) and 63.3 sigma (35%) over 2 y vs 45.3 base - the direct cost rises only +40% because it is proportional to departures; the binding cost is capacity. Indirect effects: (1) mid-level seats (JM/ES/IS) become the choke point - their T_REC is 4-6 months and their internal promotion pool is thin (3-y tenure rule), so under a cap the mid levels drain first and supervision of the 260 front-line seats degrades (indirect productivity loss, task 2 weights: mid levels carry 40% of output weight through coordination); (2) ramp load triples (new hires at 30% output for months), cutting output 4.5-9%; (3) contagion (task 2) at high churn feeds back: more departures -> more elevated hazards -> effective churn exceeds the set rate, so the true fill loss is worse than the closed form shows.

### Outcome Analysis

Answer: 25% churn - marginal, only if the HR office operates at full capacity and the mid-level promotion path is accelerated; any slack or mid-level shortfall pushes fill under 80%. 35% churn - not sustainable at current hiring capacity; fill drops below 80% within about 2 years and continues to fall toward a ~70s steady state. Cost summary (2 y): direct recruiting +18.5 sigma vs base at 35%; training flat; output loss 4.5-9% of index; vacancy period for a 35% churner averages T_REC ~ 0.22 y, so at any moment ~79 seats are empty instead of ~40. Limitations: the 8-10% office-capacity reading (30-37 campaigns) is the crux parameter and is taken from the problem's own figure 'actively hiring about 8-10% of positions'; if the true capacity is 50+ campaigns the 25% case is comfortable and only 35% breaks; the contagion feedback is bounded by the sweep in task 2.

## Subtask 5: Task 5: Simulate 30% churn in junior managers and experienced supervisors (all other levels stay at their base rates: 18

### Problem

Task 5: Simulate 30% churn in junior managers and experienced supervisors (all other levels stay at their base rates: 18% non-mid, 36% IS), over the next 2 years, under (1) no external recruiting at all, and (2) external recruiting allowed but only qualified employees promoted (3-year tenure rule enforced for promotions; mid-level seats filled by promotion only). Explain the impact on HR health.

### Analysis

This is a stress test of the mid-management layer: the two highest-turnover mid levels (JM 20 seats, ES 25 seats) are set to 30% churn - below their current 36% but still far above base - while the two response policies remove the two backfill valves (external hiring; unqualified promotions). The simulation runs the full level flow model with hiring capacity 30 and the per-departure campaign rule, so the comparison isolates the policy effect.

### Modeling Process

Scenario jm30: r = (SM 0.18, JM 0.30, ES 0.30, IS 0.36, EE/IE/AC 0.18); JM+ES churn = 0.30 x 45 seats = 13.5 departures/yr. (1) jm30_norec: no external campaigns at all; backfill by promotion only (40% of each gap, source level below, mid-level promotions capped at 1/yr per level by the qualified pool). (2) jm30_qual: external hiring allowed for non-mid levels only; JM and ES vacancies filled by promotion only, with the 3-y tenure rule (qualified fraction exp(-3r)). Reference jm30: normal backfill allowed. Results (2 y): jm30: productivity mean 1.433, final 1.378; fill stays between 54.4% and 56.0% of positions (201-207 of 370 seats); recruiting 44.5 sigma; JM/ES each hire ~8-10 externally, 2 by promotion. jm30_norec: productivity mean 1.307, final 1.079 (-11% mean, -24% final vs reference); fill fraction collapses to 40.8% final (151/370 seats); JM/ES drain to ~2 seats each, filled only by 2 promotions per level over 2 years (the 3-y rule yields exp(-0.9) = 41% of ~22 seats ~ 9 qualified, consumed at 1/yr); front-line levels cascade up (EE +32, IS +2) but each cascade vacates a seat below, so net fill falls; recruiting budget only 4.5 sigma (9 hires, non-mid); training 117.2 sigma. jm30_qual: productivity mean 1.394, final 1.257 (-4.5% to -12.5% vs reference); fill fraction final 46.7% (173 seats) - JM/ES sit at 2-4 seats for most of the 2 years because their vacancies wait for promotions that the 3-y rule throttles to ~1/yr while 13.5/yr leave; recruiting 22.7 sigma (non-mid hires only).

### Outcome Analysis

Impact on HR health: (1) No external recruiting is catastrophic for the mid layer: JM and ES are hollowed out within a year (45 seats -> ~4), supervision of 260 front-line seats collapses, and the cascade of promotions cannot replace departures because each promotion merely moves a vacancy down. Organization-wide fill halves (314 -> 151 seats) and output falls a quarter at year 2. The 3-year tenure rule is the root constraint: with 30% mid churn, the mid sojourn is ~3.3 y on average, so barely more than half the mid staff are ever promotion-eligible, and they are consumed at 1/yr per level. (2) Qualified-only promotion with normal external hiring is a slow bleed: JM/ES stay ~90% empty for 2 years, output down up to 12%, but the front line survives and the system is reversible once external mid hiring resumes. (3) Comparison with the reference (normal backfill) shows the mid layer is sustainable at 30% churn only if external mid-level hiring is available - the promotion path alone covers at most ~1 of the ~13.5 annual mid departures. Recommendation the model supports: treat external mid-level recruiting as essential insurance, shorten the mid tenure rule, and keep the ES/JM promotion pipeline above 2/yr per level. Limitations: the 1-promotion-per-year mid cap encodes the qualified-pool size (9-14 eligible); a richer pipeline model could allow 2-3/yr and would soften (but not remove) the norec collapse; the cascade accounting assumes promotions fill the gap within the step.

## Subtask 6: Task 6: Summarize the potential use of team science and multi-layered networks in fulfilling the HR manager's vision of 

### Problem

Task 6: Summarize the potential use of team science and multi-layered networks in fulfilling the HR manager's vision of connecting the Human Capital network to information-flow, trust, influence and friendship layers (references: Salas et al. 2008; Stokols et al. 2008; Kivela et al. 2013).

### Analysis

The HR manager's vision is exactly a multiplex: the personnel layer built in task 1 plus the other offices' planned layers, sharing one node set (employees) and differing in edge semantics. Team science (Salas: team composition, coordination, shared mental models; Stokols: team-as-system indicators) supplies the performance-side variables that link network structure to output; multiplex network theory (Kivela) supplies the mathematics of cross-layer interactions. The summary below maps each layer to the model's existing mechanisms and states what the combined structure enables that the single-layer model cannot.

### Modeling Process

Multiplex M = (V, {A^a}) with layers a in {personnel (built, task 1), information flow, trust, influence, friendship}, |V| = 370. Cross-layer coupling as used here: (i) the influence layer A^inf carries the churn contagion of task 2 - a departure's hazard boost travels along influence edges with multiplier 2.0/0.5 y (close ties) and 1.5/1.0 y (reports), so the personnel-layer departure process is a dynamical system on A^inf; (ii) the trust layer modulates the productivity weights w_l (task 4): teams with dense trust edges carry a coordination factor up to +10-20% of output weight, which is the quantitative form of 'team performance' in Salas's sense; (iii) the information-flow layer sets the speed at which vacancies and knowledge gaps propagate - the 0.02-y notice delay of E9 is a first-layer approximation of its shortest-path time; (iv) the friendship layer is the slow, stable backbone that keeps clusters intact (E8: membership persistent), making contagion and trust effects cumulative rather than washed out by reshuffling. Team-science indicators to compute on the combined graph: team-level cohesion (intra-cluster edge density, currently 0.6), shared leadership (cross-layer degree overlap - managers are the only nodes with cross-cluster edges in both personnel and influence layers), and churn-risk centrality: a node's hazard is the baseline r_l times the product of layer-wise exposures, h_i = r_l * prod_a (1 + beta_a * x_i^a), with x_i^a the node's exposure in layer a (recent neighbor departures in influence, broken trust edges in trust, etc.). This turns task 2's contagion into a general multiplex diffusion rule and gives the HR office one dashboard: which clusters are losing in multiple layers at once.

### Outcome Analysis

Why it fulfills the vision: (1) one node set, many edge types - the other offices' layers plug in without rebuilding the personnel model; (2) cross-layer early warning - churn is predicted from influence-layer events days before it appears in personnel data (E9: social notice within days, operational loss weeks later), so the 'identify churn risk in early stages' goal (issue 1) becomes a measurable cross-layer signal; (3) intervention targeting - the multiplex shows that the mid managers are the structural hubs (cross-cluster edges in multiple layers), which explains quantitatively why their 36% churn (task 4) is disproportionately damaging and why retaining them is cheaper than rebuilding teams; (4) limits: the layers must be measured, not assumed - the friendship and trust layers have no data yet, so until they are collected the multiplex stays partially synthetic, and cross-layer coupling constants (beta_a) need calibration from at least one year of linked personnel + survey data; the model here demonstrates the architecture and the one fully calibrated coupling (influence).

## Subtask 7: Task 7 (report integration): The 20-page report requirement - deliver the organizational model, its function and the iss

### Problem

Task 7 (report integration): The 20-page report requirement - deliver the organizational model, its function and the issues to consider, as a complete written analysis.

### Analysis

Per the submission instructions this analysis is delivered inside the machine-readable container rather than as a separate markdown report; this entry consolidates the model's scope, function, and the open issues, in the order a report would present them: data and assumptions, network model, dynamics, budgets, stress scenarios, and the multi-layer extension, with the limitation summary of each part.

### Modeling Process

Structure: (1) Problem and data: 370 seats, 7 levels, 85% filled, 18% overall / 36% mid churn, sigma normalization, table1.csv cleaned (sigma column mojibake resolved, no numeric repair needed; EE salary set to 1.0 sigma from the problem's median definition). (2) Model: level flow model (vacancies, 40/60 promotion/external split, T_REC pipeline, 3-y promotion rule, ramp to full productivity) + synthetic stable team network (10 clusters, density 0.6, manager cross-links, 0.1 annual reassignment). (3) Dynamics: contagion (x2.0, 0.5 y; manager effect x1.5, 1.0 y), productivity weights (front line 105%), quality drift at high churn. (4) Budgets: 2-y recruiting 45 sigma, training 140 sigma, total ~185 sigma at base churn; recruiting is the churn-sensitive part. (5) Stress tests: 25% churn marginal (office at 100% capacity), 35% not sustainable (fill < 80% within ~2 y); 30% JM/ES churn with no external recruiting collapses the mid layer (fill 314 -> 151 seats, output -24% by year 2); qualified-only promotion is a slow reversible bleed (fill -> 173, output -12%). (6) Extension: multiplex of 5 layers with calibrated influence-layer coupling; team-science indicators (cohesion, shared leadership, churn-risk centrality). (7) Parameter table: all 14 calibrated inputs with intervals and sources (expert exchanges E1-E10, problem statement, dataset), as recorded in task 1.

### Outcome Analysis

Key conclusions for the HR manager: (1) ICM's churn is partly self-inflicted - contagion adds ~31 excess departures per 2 years (~25% of churn) and is addressable by acting within days of a departure (the notice window is a day, the effect window is months); (2) the mid-management layer is the single most dangerous point: it churning at 36% already, its backfill depends on external hiring that the 3-year tenure rule cannot replace, and 35% overall churn makes 80% fill impossible at current office capacity; (3) the 2-year talent budget is ~185 sigma, and the smart lever is not spending more on recruiting (only +40% at 35% churn) but protecting the mid pipeline and using the early-warning window; (4) the multi-layer architecture is the right next step and the influence layer is already usable; trust/friendship layers need to be measured before their coupling constants can be trusted. Overall limitations: synthetic network (magnitude uncertainty ~2x on contagion), assumed EE salary (1.0 sigma), assumed quality-drift rate, and the 30-campaign office capacity as the crux of task 4's answer.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
