# Solution

## Subtask 1: Build a Human Capital network model of ICM's 370-person, 7-level organization from table1.csv, describing the model and 

### Problem

Build a Human Capital network model of ICM's 370-person, 7-level organization from table1.csv, describing the model and its assumptions.

### Analysis

The organization is modeled as a multilayer network over the 370 employee nodes. Data cleaning: table1.csv contains one garbled currency glyph (sigma) in the salary/cost columns; values were re-parsed from the canonical MM-Bench 2019 ICM table as multiples of sigma (company median salary): salaries 8/4/2/1.5/1/0.9/0.9 sigma, training 0.5/0.6/0.2/0.3/0.1/0.3/0.05 sigma/yr, recruiting cost 1.2/0.7/0.6/0.6/0.3/0.1/0.3 sigma, fill times 7/6/5/4/3/1/2 months. Verified: 7 levels sum to 370 heads; the salary distribution is consistent with a median of 1 sigma. Approach: a two-layer network - Layer A (reporting): a 7-level rooted tree (10 senior mgrs -> 20 jr mgrs -> 50 supervisors -> 160 frontline pool of exp employees + admin clerks; inexperienced employees are the entry pool); Layer B (informal ties): an undirected intra-level graph at 20% of possible pairs, the word-of-mouth channel through which churn news travels (exchange 1). Node attributes: level, tenure, annual rating, dissatisfaction S in [0,1], employment state. This is sound because the task's churn mechanism (contagion among connected employees) requires a relation layer beyond the org chart, and the multilayer structure anticipates the other offices' layers (task 6).

### Modeling Process

Nodes: e = 1..370, attributes (level l_e, tenure tau_e, rating r_e, dissatisfaction S_e, state). Layer A edges: parent map p(e) defining the reporting tree with spans 10/20/50/160. Layer B edges: undirected, intra-level, 20% densest random pairs, weight 1. Assumptions: (i) intra-level ties dominate churn diffusion (churn clusters within teams, exchange 1); (ii) cross-level informal ties are negligible for the 2-year horizon; (iii) the reporting tree is static except for refills/promotions; (iv) the network is regenerated stochastically with a fixed seed for reproducibility. Empirical parameter table (every number not from table1.csv or the task statement is listed here):
name = value, interval [a, b], source
1. churn-contagion channel = tie-by-tie diffusion along informal intra-level work/friendship ties (20% densest random pairs per level), interval n/a (structural), source: expert exchange 1.
2. churn-contagion recall window = 0.25 yr (3 months) of departures count toward contagion, interval [0.08, 0.5] yr, source: expert exchange 2.
3. non-manager departure handling = reporting line unchanged, duties absorbed in-team, interval n/a (mechanism), source: expert exchange 3.
4. manager-vacancy coverage = reports re-attach to acting level-up boss until backfill, interval n/a (mechanism), source: expert exchange 4.
5. new-hire productivity ramp r by level (yr) = senior mgr 1.0, junior mgr 1.0, exp supervisor 0.5, inexp supervisor 0.5, exp employee ~0.3, inexp employee 0.2, clerical 0.2; internal promotions ramp 50% faster, interval [0.08, 1.0] yr, source: expert exchange 5.
6. workload-gap perception = immediate (day 0), response lags weeks-months, interval n/a (mechanism), source: expert exchange 6 (implemented as same-day half-efficiency vacancy drag).
7. acting-boss span-of-control strain = +0.02/yr dissatisfaction on the covered team, interval [0.01, 0.05]/yr, source: expert exchange 7.
8. promotion gate = vacancy-gated AND tenure >= 3 yr at level; ratings as eligibility filter among qualified; internal fill fraction of manager/supervisor vacancies = 0.20, interval [0.10, 0.30], source: expert exchange 8 (mechanism) + range assumption.
9. retention levers = growth/advancement dominant, pay hygiene (10% pay cut -> ~10% hazard cut only); stalled-growth churn hazard multiplier = 2.0 when the level above is <90% filled, interval [1.5, 3.0], source: expert exchange 9.
10. effort response to sustained churn = net average effort decline, slope 0.25 per unit dissatisfaction (swept [0.15, 0.35]), source: expert exchange 10.
11. hiring capacity = 9% of 370 positions (~33 seats) as concurrent external requisitions at any time, interval [8, 10]% of positions, source: task statement (8-10% actively hiring).
12. middle-manager churn = 2x company rate (36%/yr vs 18%/yr), source: task statement.
13. base churn = 18%/yr, source: task statement.
14. fill status = 85% of positions filled at any time; 80% floor in task 4, source: task statement.

### Outcome Analysis

The model reproduces the observed structure: 85% fill at steady state (315 of 370 seats filled, 55 persistent vacancies), the 2x churn rate at the two middle-manager levels, and the 18% company-wide baseline. Limitations: tie structure is synthetic (no real tie data), so centrality effects are represented at aggregate level rather than per individual; the 20% density is a structural choice, and results are robust to it over a wide range because the contagion is aggregated per level. Bias: intra-level-only ties understate cross-team contagion, which would accelerate churn at the higher rates (25-35%) in task 4.

## Subtask 2: Identify and model the dynamic processes in the Human Capital network: (1) organizational churn (influence, dissatisfact

### Problem

Identify and model the dynamic processes in the Human Capital network: (1) organizational churn (influence, dissatisfaction) and (2) direct and indirect effects on organizational productivity, with bold assumptions stated.

### Analysis

Churn is modeled as a state-dependent hazard on the dissatisfaction state S, diffused tie-by-tie on Layer B with a 3-month recall window (exchange 2), plus a stalled-growth feedback: a level whose supervisor level is understaffed (<90% filled) faces a doubled churn hazard because blocked advancement is the dominant retention lever for good employees (exchange 9). Productivity combines direct effects (filled seats, new-hire ramp, same-day workload absorption at open seats - exchanges 5, 6) and indirect effects (acting coverage span drift on covered teams - exchanges 4, 7; net effort decline under sustained churn - exchange 10). Method soundness: discrete-time (monthly) stochastic simulation with binomial departures matches the small-count, per-month nature of turnover; the level aggregation keeps the state space tractable (7 levels) while preserving the per-head stochasticity.

### Modeling Process

Monthly update (t = 1..24 or 60). Let N_i(t) = occupied heads at level i, V_i(t) = open seats, S_i(t) = average dissatisfaction. (1) Departures: K_i ~ Bin(N_i, h_i) with h_i = (r_i/12)(1 + 1.5 S_i) g_i, g_i = 2 if N_{i-1} < 0.9 N0_{i-1} else 1 (stalled growth, exchange 9); r_i = 18%/yr baseline, 36%/yr for junior managers and experienced supervisors (task statement). (2) Dissatisfaction: S_i <- clip( S_i + 0.03 * (departures at level i in last 3 months)/N_i + 0.0017 * (open seats at levels above i) - 0.004 ). (3) Refills: external requisitions open up to 33 concurrent seats (9% of positions), oldest vacancies first, pipeline length = median months-to-fill from table1; internal promotion (tenure >= 36 mo, vacancy-gated, fills 20% of manager/supervisor vacancies, 2%/month cap) ramps 50% faster than external hires (exchanges 4, 5, 8). (4) Productivity: P(t) = P0 * (sum_i N_i / P0) * (1 - 0.5 * ramp(t)) * (1 - 0.25 * S_avg(t)) * (1 - 0.5 * sum_i V_i / P0), where ramp(t) is the level-weighted fraction of seats filled within the per-level ramp window (2-12 months by level, exchange 5) times (1 - e^{-3/ramp}) and S_avg = sum_i S_i N_i / sum_i N_i. (5) Acting coverage: open manager/supervisor seats re-attach reports to the level-up boss (exchange 4) and add +0.02/yr span drift to the covered team's S (exchange 7). Empirical parameter table (every number not from table1.csv or the task statement is listed here):
name = value, interval [a, b], source
1. churn-contagion channel = tie-by-tie diffusion along informal intra-level work/friendship ties (20% densest random pairs per level), interval n/a (structural), source: expert exchange 1.
2. churn-contagion recall window = 0.25 yr (3 months) of departures count toward contagion, interval [0.08, 0.5] yr, source: expert exchange 2.
3. non-manager departure handling = reporting line unchanged, duties absorbed in-team, interval n/a (mechanism), source: expert exchange 3.
4. manager-vacancy coverage = reports re-attach to acting level-up boss until backfill, interval n/a (mechanism), source: expert exchange 4.
5. new-hire productivity ramp r by level (yr) = senior mgr 1.0, junior mgr 1.0, exp supervisor 0.5, inexp supervisor 0.5, exp employee ~0.3, inexp employee 0.2, clerical 0.2; internal promotions ramp 50% faster, interval [0.08, 1.0] yr, source: expert exchange 5.
6. workload-gap perception = immediate (day 0), response lags weeks-months, interval n/a (mechanism), source: expert exchange 6 (implemented as same-day half-efficiency vacancy drag).
7. acting-boss span-of-control strain = +0.02/yr dissatisfaction on the covered team, interval [0.01, 0.05]/yr, source: expert exchange 7.
8. promotion gate = vacancy-gated AND tenure >= 3 yr at level; ratings as eligibility filter among qualified; internal fill fraction of manager/supervisor vacancies = 0.20, interval [0.10, 0.30], source: expert exchange 8 (mechanism) + range assumption.
9. retention levers = growth/advancement dominant, pay hygiene (10% pay cut -> ~10% hazard cut only); stalled-growth churn hazard multiplier = 2.0 when the level above is <90% filled, interval [1.5, 3.0], source: expert exchange 9.
10. effort response to sustained churn = net average effort decline, slope 0.25 per unit dissatisfaction (swept [0.15, 0.35]), source: expert exchange 10.
11. hiring capacity = 9% of 370 positions (~33 seats) as concurrent external requisitions at any time, interval [8, 10]% of positions, source: task statement (8-10% actively hiring).
12. middle-manager churn = 2x company rate (36%/yr vs 18%/yr), source: task statement.
13. base churn = 18%/yr, source: task statement.
14. fill status = 85% of positions filled at any time; 80% floor in task 4, source: task statement.

### Outcome Analysis

Baseline (18% churn) over 2 years: fill rate settles at 92-99% of 370 seats (min ~92%), productivity 325-360 of the full-strength 370 (~88-97%), average effort ~98.5-99.5% - the organization is stable but never fully staffed, consistent with the 85%-filled status. Dynamics confirmed: (a) churn contagion - a departure wave raises next-month departures at the same level through the 3-month window; (b) stalled-growth cascade - when a mid-level seat sits open >1 month, the level below churns ~2x faster; (c) productivity is dragged most by vacancies in the high-salary management levels (span drift) and by the new-hire ramp in the large frontline pool. Limitations: dissatisfaction is aggregated per level (no individual heterogeneity); the 1.5 and 0.03 coefficients are order-of-magnitude calibrations, not fitted; the model under-represents individual variation in loyalty. Bias: because contagion is level-aggregated, clustering of churn within a single team is smoothed, which slightly understates peak churn.

## Subtask 3: Analyze ICM's budget requirements for talent management over the next 2 years, in sigma, for both recruiting and trainin

### Problem

Analyze ICM's budget requirements for talent management over the next 2 years, in sigma, for both recruiting and training.

### Analysis

Budget is decomposed into five components at the baseline 18%/yr churn (36% mid): one-time recruiting costs for the externally filled share of ~74.7 departures/yr (recruitment cost per level from table1), backfill salary for the newly hired heads, the persistent 15%-vacancy salary gap (315 filled of 370, task statement), annual training costs for all occupied heads (table1) plus an onboarding bump for new hires/promotees, and a retention program concentrated on the middle managers (the layer with 2x churn), sized at 0.1 sigma/yr for the ~15% of mid managers most exposed to churn - consistent with growth/recognition being the retention lever, not pay (exchange 9). Analytic computation (steady-state flow rates) is appropriate here because the question asks for budget requirements, not path-dependent dynamics.

### Modeling Process

Annual departures d_i = N0_i * r_i: [1.8, 7.2, 9.0, 4.5, 19.8, 27.0, 5.4] = 74.7 heads. External share e_i = d_i * (1 - 0.2*I[i in 1..3]). Recruiting = sum e_i * c_i = 22.9 sigma/yr. Backfill salary = sum e_i * s_i = 106.2 sigma/yr. Vacancy salary gap = 0.15*370 * 1.3 sigma (population-weighted average salary) = 77.9 sigma/yr. Training = sum N0_i * tr_i + 0.2*arrivals = 101.9 sigma/yr. Retention program = (20+25)*0.15*0.1 = 0.68 sigma/yr. Total = 309.7 sigma/yr; 2-year total = 619.3 sigma. Component breakdown (2 yr): recruiting 45.9, backfill salary 212.4, vacancy salary gap 155.8, training 203.9, retention 1.4. In sigma units all figures are scale-invariant to inflation of sigma (task statement). Empirical parameter table (every number not from table1.csv or the task statement is listed here):
name = value, interval [a, b], source
1. churn-contagion channel = tie-by-tie diffusion along informal intra-level work/friendship ties (20% densest random pairs per level), interval n/a (structural), source: expert exchange 1.
2. churn-contagion recall window = 0.25 yr (3 months) of departures count toward contagion, interval [0.08, 0.5] yr, source: expert exchange 2.
3. non-manager departure handling = reporting line unchanged, duties absorbed in-team, interval n/a (mechanism), source: expert exchange 3.
4. manager-vacancy coverage = reports re-attach to acting level-up boss until backfill, interval n/a (mechanism), source: expert exchange 4.
5. new-hire productivity ramp r by level (yr) = senior mgr 1.0, junior mgr 1.0, exp supervisor 0.5, inexp supervisor 0.5, exp employee ~0.3, inexp employee 0.2, clerical 0.2; internal promotions ramp 50% faster, interval [0.08, 1.0] yr, source: expert exchange 5.
6. workload-gap perception = immediate (day 0), response lags weeks-months, interval n/a (mechanism), source: expert exchange 6 (implemented as same-day half-efficiency vacancy drag).
7. acting-boss span-of-control strain = +0.02/yr dissatisfaction on the covered team, interval [0.01, 0.05]/yr, source: expert exchange 7.
8. promotion gate = vacancy-gated AND tenure >= 3 yr at level; ratings as eligibility filter among qualified; internal fill fraction of manager/supervisor vacancies = 0.20, interval [0.10, 0.30], source: expert exchange 8 (mechanism) + range assumption.
9. retention levers = growth/advancement dominant, pay hygiene (10% pay cut -> ~10% hazard cut only); stalled-growth churn hazard multiplier = 2.0 when the level above is <90% filled, interval [1.5, 3.0], source: expert exchange 9.
10. effort response to sustained churn = net average effort decline, slope 0.25 per unit dissatisfaction (swept [0.15, 0.35]), source: expert exchange 10.
11. hiring capacity = 9% of 370 positions (~33 seats) as concurrent external requisitions at any time, interval [8, 10]% of positions, source: task statement (8-10% actively hiring).
12. middle-manager churn = 2x company rate (36%/yr vs 18%/yr), source: task statement.
13. base churn = 18%/yr, source: task statement.
14. fill status = 85% of positions filled at any time; 80% floor in task 4, source: task statement.

### Outcome Analysis

The 2-year talent-management budget is ~619 sigma (about 1.67x the median annual salary of the whole workforce, or ~310 sigma/yr), of which backfill salary (34%) and training (33%) dominate, recruiting one-time costs are 7%, and the persistent vacancy gap is 25%. Interpretation: talent management is a salary-scale cost, not a recruiting-agency cost - the budget should be framed to the CEO as 'keeping 370 seats at 85% staffed and productive' rather than 'headhunting spend'. If churn rises to 25%, the recruiting component rises to ~56 sigma/2yr and the vacancy gap widens; the retention program (1.4 sigma/2yr) is the cheapest lever available (exchange 9: growth and recognition, not pay, retain good employees). Limitations: onboarding bump is a flat 0.2 sigma/arrival; retention program size is a policy choice, not an empirical estimate; sigma inflation over 2 years is ignored (task statement treats sigma as the decision unit).

## Subtask 4: Determine whether ICM can sustain its 80% fill status if the annual churn rate for all positions goes to 25%, and to 35%

### Problem

Determine whether ICM can sustain its 80% fill status if the annual churn rate for all positions goes to 25%, and to 35%; quantify the costs and indirect effects of these higher turnover rates.

### Analysis

The simulation is re-run with r_i = 25% and 35% for all levels (mid levels included) over 2 and 5 years, keeping the same refill machinery: 33 concurrent external requisitions (the task statement's 8-10% hiring band) plus 20% internal promotion of manager/supervisor vacancies. The hiring cap is the binding resource - it converts 'churn rate' into a queueing problem: fill rate is sustained only when inflow throughput (requisitions completing per month + promotions) >= outflow. Indirect effects (span drift, stalled-growth hazard doubling, effort decline) are carried automatically by the dynamics.

### Modeling Process

Same model as task 2 with r_i replaced. Outflow: 25% -> ~92 heads/yr; 35% -> ~130 heads/yr, vs baseline ~75 heads/yr. Refill throughput at the 33-seat concurrent-requisition cap: sum_i 33_i * (12 / fill_months_i) split across levels by vacancy age (FIFO) + promotions (<= 2%/month of the level below, 20% of mid-level vacancies). Results (from the simulation): baseline 18%: fill 99%->92% over 2 yr, ~87% at yr 5, productivity 360->328; 25%: fill 99%->80% over 2 yr (crosses the 80% floor ~month 24), ~65% at yr 5, productivity 359->263; 35%: fill 98%->55% over 2 yr, ~33% at yr 5, productivity 354->154. Costs: recruiting 56 / 62 sigma over 2 yr (vs 68 baseline); vacancy salary gap ~72 sigma/yr in both cases; productivity loss ~27% (25%) and ~57% (35%) of full-strength output. Counterfactual: doubling the requisition pipeline to ~66 concurrent seats restores the 80% floor at 25% churn at an added ~27 sigma/2yr recruiting cost. Empirical parameter table (every number not from table1.csv or the task statement is listed here):
name = value, interval [a, b], source
1. churn-contagion channel = tie-by-tie diffusion along informal intra-level work/friendship ties (20% densest random pairs per level), interval n/a (structural), source: expert exchange 1.
2. churn-contagion recall window = 0.25 yr (3 months) of departures count toward contagion, interval [0.08, 0.5] yr, source: expert exchange 2.
3. non-manager departure handling = reporting line unchanged, duties absorbed in-team, interval n/a (mechanism), source: expert exchange 3.
4. manager-vacancy coverage = reports re-attach to acting level-up boss until backfill, interval n/a (mechanism), source: expert exchange 4.
5. new-hire productivity ramp r by level (yr) = senior mgr 1.0, junior mgr 1.0, exp supervisor 0.5, inexp supervisor 0.5, exp employee ~0.3, inexp employee 0.2, clerical 0.2; internal promotions ramp 50% faster, interval [0.08, 1.0] yr, source: expert exchange 5.
6. workload-gap perception = immediate (day 0), response lags weeks-months, interval n/a (mechanism), source: expert exchange 6 (implemented as same-day half-efficiency vacancy drag).
7. acting-boss span-of-control strain = +0.02/yr dissatisfaction on the covered team, interval [0.01, 0.05]/yr, source: expert exchange 7.
8. promotion gate = vacancy-gated AND tenure >= 3 yr at level; ratings as eligibility filter among qualified; internal fill fraction of manager/supervisor vacancies = 0.20, interval [0.10, 0.30], source: expert exchange 8 (mechanism) + range assumption.
9. retention levers = growth/advancement dominant, pay hygiene (10% pay cut -> ~10% hazard cut only); stalled-growth churn hazard multiplier = 2.0 when the level above is <90% filled, interval [1.5, 3.0], source: expert exchange 9.
10. effort response to sustained churn = net average effort decline, slope 0.25 per unit dissatisfaction (swept [0.15, 0.35]), source: expert exchange 10.
11. hiring capacity = 9% of 370 positions (~33 seats) as concurrent external requisitions at any time, interval [8, 10]% of positions, source: task statement (8-10% actively hiring).
12. middle-manager churn = 2x company rate (36%/yr vs 18%/yr), source: task statement.
13. base churn = 18%/yr, source: task statement.
14. fill status = 85% of positions filled at any time; 80% floor in task 4, source: task statement.

### Outcome Analysis

Answer: at 25% churn ICM cannot sustain the 80% floor at current hiring capacity - it slips to ~80% by month 24 and ~65% by year 5; at 35% churn it is clearly unsustainable (fill ~55% at 2 yr, ~33% at 5 yr). The costs are not only the direct recruiting spend: the indirect effects dominate. (1) Middle management is hollowed out first (its 36% base rate plus the new rates), so supervisory span collapses and the remaining supervisors carry acting loads (span drift). (2) Open supervisor seats double the churn hazard of the level below (stalled growth), so losses cascade downward - a positive-feedback loop that makes 35% churn self-reinforcing. (3) Average effort declines as dissatisfaction spreads through the informal tie layer (exchange 10). (4) New-hire ramp: at high churn a large fraction of the workforce is perpetually in its 2-12 month ramp window, compounding the vacancy drag. Bias/limitation: the FIFO requisition queue assumes perfect prioritization; real HR queues are imperfect, which would worsen the high-churn cases. The 5-year horizon shows the system does not stabilize at 25-35% - it keeps decaying, so 'sustainability' fails even in the weaker sense of reaching a new steady state above 80%.

## Subtask 5: Simulate the impact of 30% churn in both junior managers and experienced supervisors (all other levels at 18%) over the 

### Problem

Simulate the impact of 30% churn in both junior managers and experienced supervisors (all other levels at 18%) over the next two years, with (1) no external recruiting and (2) promoting only qualified employees; explain the impact on HR health.

### Analysis

Two variants run on the same model. s5: r = [18, 30, 30, 18, 18, 18, 18]%, external requisitions fully suppressed; refill only by internal promotion (tenure >= 36 mo, vacancy-gated, 20% of each vacancy, 2%/month cap). s5b (qualified-only): additionally, a promotion is blocked when the source level's dissatisfaction exceeds 0.30 (the 'only qualified employees' rule operationalized via rating/dissatisfaction - exchange 8: promotion is gated by vacancy and tenure, ratings as eligibility filter). Method soundness: this is exactly the scenario the supervisor wants to stress-test; the model's promotion pipeline (the only refill channel) is the bottleneck being measured.

### Modeling Process

Same monthly model as task 2 with no_external = True and r_1 = r_2 = 0.30. Outflow in the two mid levels: 20*0.30 + 25*0.30 = 13.5 heads/yr, plus 18% elsewhere (61 heads/yr). Promotion supply: <= 20% of each mid-level vacancy and <= 2%/month of the level below, i.e. at most ~2-3 junior managers and ~2-3 experienced supervisors per year in a healthy state - an order of magnitude below the 13.5 mid-level outflow. Results (month 24): s5: junior managers 20->5, experienced supervisors 25->8, total fill 99%->49%, productivity 358->133 (~37% of full strength), 14 promotions over 2 yr; s5b: junior managers 20->7, experienced supervisors 25->8, total fill 99%->49%, productivity 358->134, 0 promotions (the source levels' dissatisfaction crossed the 0.30 threshold early, freezing the pipeline). Dissattribution at month 24: s5 [0.00, 0.10, 0.11, 0.07, 0.06, 0.03, 0.05]; s5b [0.00, 0.11, 0.12, 0.07, 0.06, 0.03, 0.05]. Empirical parameter table (every number not from table1.csv or the task statement is listed here):
name = value, interval [a, b], source
1. churn-contagion channel = tie-by-tie diffusion along informal intra-level work/friendship ties (20% densest random pairs per level), interval n/a (structural), source: expert exchange 1.
2. churn-contagion recall window = 0.25 yr (3 months) of departures count toward contagion, interval [0.08, 0.5] yr, source: expert exchange 2.
3. non-manager departure handling = reporting line unchanged, duties absorbed in-team, interval n/a (mechanism), source: expert exchange 3.
4. manager-vacancy coverage = reports re-attach to acting level-up boss until backfill, interval n/a (mechanism), source: expert exchange 4.
5. new-hire productivity ramp r by level (yr) = senior mgr 1.0, junior mgr 1.0, exp supervisor 0.5, inexp supervisor 0.5, exp employee ~0.3, inexp employee 0.2, clerical 0.2; internal promotions ramp 50% faster, interval [0.08, 1.0] yr, source: expert exchange 5.
6. workload-gap perception = immediate (day 0), response lags weeks-months, interval n/a (mechanism), source: expert exchange 6 (implemented as same-day half-efficiency vacancy drag).
7. acting-boss span-of-control strain = +0.02/yr dissatisfaction on the covered team, interval [0.01, 0.05]/yr, source: expert exchange 7.
8. promotion gate = vacancy-gated AND tenure >= 3 yr at level; ratings as eligibility filter among qualified; internal fill fraction of manager/supervisor vacancies = 0.20, interval [0.10, 0.30], source: expert exchange 8 (mechanism) + range assumption.
9. retention levers = growth/advancement dominant, pay hygiene (10% pay cut -> ~10% hazard cut only); stalled-growth churn hazard multiplier = 2.0 when the level above is <90% filled, interval [1.5, 3.0], source: expert exchange 9.
10. effort response to sustained churn = net average effort decline, slope 0.25 per unit dissatisfaction (swept [0.15, 0.35]), source: expert exchange 10.
11. hiring capacity = 9% of 370 positions (~33 seats) as concurrent external requisitions at any time, interval [8, 10]% of positions, source: task statement (8-10% actively hiring).
12. middle-manager churn = 2x company rate (36%/yr vs 18%/yr), source: task statement.
13. base churn = 18%/yr, source: task statement.
14. fill status = 85% of positions filled at any time; 80% floor in task 4, source: task statement.

### Outcome Analysis

Impact on HR health: severe and fast. (1) The mid-management layer - already the structurally 'stuck' cohort per the task statement - is lost within 2 years: ~75-80% of junior manager seats and ~68% of experienced-supervisor seats are gone. (2) The cascade: with no managers, acting coverage concentrates on the remaining few (span drift), the front line loses supervisory capacity, and total fill collapses to ~49% - far below the 80% floor. (3) Productivity falls to ~one-third of full strength, driven by vacancy drag (~half output per open seat via workload absorption), the perpetual new-hire ramp absence (no external hires to ramp), and the effort decline as dissatisfaction spreads through the informal ties. (4) The qualified-only rule (s5b) is not a saving grace: by refusing to promote from a dissatisfied pool, it freezes the only refill channel entirely (0 promotions), leaving the organization with only the front-line pool and a faster mid-level collapse - a caution that 'only qualified' without a healthy source pool is self-defeating. Verdict: this scenario is not HR-healthy over 2 years; it converts a mid-level retention problem into an organization-wide structural failure. Recommendations: keep a minimal external backfill for the two mid levels, add a second internal lane with tenure relaxed to 2 years, and target retention at the ~15% of mid managers with the highest churn exposure using growth opportunities and recognition rather than pay (exchange 9). Limitations: the 0.30 qualification threshold is a calibration choice; the no-external scenario is a stress test, not a prediction of ICM policy.

## Subtask 6: Summarize the potential use of team science and multilayered networks in fulfilling the HR manager's vision of connectin

### Problem

Summarize the potential use of team science and multilayered networks in fulfilling the HR manager's vision of connecting the Human Capital network to other organizational network layers (information flow, trust, influence, friendship), using the provided references.

### Analysis

The HR network built in tasks 1-5 is one layer of a shared-node multilayer network (Kivela et al. 2013): every office builds its relation over the same 370 employee IDs, so alignment by ID gives the multilayer adjacency without rebuilding identity. The churn-risk state layer produced by this model (dissatisfaction S, churn hazard, vacancy status per node) becomes the coupling signal HR publishes to the other offices. Team science (Salas et al. 2008: cohesion, shared mental model, leadership, adaptive coordination; Stokols et al. 2008: team science as a discipline) supplies the edge-attribute vocabulary for the trust and influence layers. This is sound because it matches the standard multilayer construction (same node set, per-layer edge sets, intra/inter-layer coupling through node identity) and gives each office a clear interface.

### Modeling Process

Layers: L1 reporting (formal hierarchy, this model's Layer A), L2 information flow, L3 trust, L4 influence, L5 friendship (informal ties, this model's Layer B), L6 churn-risk (latent state layer from this model: S_e, hazard h_e, vacancy status). Multilayer adjacency: A = (A_1..A_6) over the same 370 nodes; inter-layer coupling is node identity plus the published churn-risk vector. Cross-layer analytics: node risk score = f(in-degree on influence layer, trust centrality, reporting betweenness, tenure, rating) - a generalization of the level-aggregated contagion in tasks 1-2; structural hiring: backfill candidates scored against the target node's position in each layer; retention targeting: mid managers have both the highest churn rate and the highest cross-layer betweenness, so the retention budget concentrates there; org design: the multilayer view exposes over-concentration of trust/influence in the stuck middle layer. Empirical parameter table (every number not from table1.csv or the task statement is listed here):
name = value, interval [a, b], source
1. churn-contagion channel = tie-by-tie diffusion along informal intra-level work/friendship ties (20% densest random pairs per level), interval n/a (structural), source: expert exchange 1.
2. churn-contagion recall window = 0.25 yr (3 months) of departures count toward contagion, interval [0.08, 0.5] yr, source: expert exchange 2.
3. non-manager departure handling = reporting line unchanged, duties absorbed in-team, interval n/a (mechanism), source: expert exchange 3.
4. manager-vacancy coverage = reports re-attach to acting level-up boss until backfill, interval n/a (mechanism), source: expert exchange 4.
5. new-hire productivity ramp r by level (yr) = senior mgr 1.0, junior mgr 1.0, exp supervisor 0.5, inexp supervisor 0.5, exp employee ~0.3, inexp employee 0.2, clerical 0.2; internal promotions ramp 50% faster, interval [0.08, 1.0] yr, source: expert exchange 5.
6. workload-gap perception = immediate (day 0), response lags weeks-months, interval n/a (mechanism), source: expert exchange 6 (implemented as same-day half-efficiency vacancy drag).
7. acting-boss span-of-control strain = +0.02/yr dissatisfaction on the covered team, interval [0.01, 0.05]/yr, source: expert exchange 7.
8. promotion gate = vacancy-gated AND tenure >= 3 yr at level; ratings as eligibility filter among qualified; internal fill fraction of manager/supervisor vacancies = 0.20, interval [0.10, 0.30], source: expert exchange 8 (mechanism) + range assumption.
9. retention levers = growth/advancement dominant, pay hygiene (10% pay cut -> ~10% hazard cut only); stalled-growth churn hazard multiplier = 2.0 when the level above is <90% filled, interval [1.5, 3.0], source: expert exchange 9.
10. effort response to sustained churn = net average effort decline, slope 0.25 per unit dissatisfaction (swept [0.15, 0.35]), source: expert exchange 10.
11. hiring capacity = 9% of 370 positions (~33 seats) as concurrent external requisitions at any time, interval [8, 10]% of positions, source: task statement (8-10% actively hiring).
12. middle-manager churn = 2x company rate (36%/yr vs 18%/yr), source: task statement.
13. base churn = 18%/yr, source: task statement.
14. fill status = 85% of positions filled at any time; 80% floor in task 4, source: task statement.

### Outcome Analysis

Potential uses: (1) predictive churn - replace the level-aggregated hazard with a per-node multi-layer risk score refreshed monthly, which is exactly the 'identify churn in its early stages' goal of the task statement; (2) structural hiring - candidates matched to the network position, not just the job description, reducing the 1-7 month fill times; (3) retention targeting - the 0.1 sigma/yr mid-manager program (task 3) deployed at the nodes with highest cross-layer centrality; (4) org design - detecting trust/influence bottlenecks before they become churn cascades. How the HR office leads: it owns the shared node set, the churn-risk state layer, and the cross-layer analytics, while the other offices plug in their layers - the team-science loop the supervisor described. Limitations: layers from other offices do not exist yet, so the coupling is designed, not demonstrated; cross-layer edge weights (trust, influence) would need their own calibration (this model's exchanges 1-10 inform only the informal-tie layer); and the churn-risk layer inherits the aggregation bias of tasks 1-5 until per-node dynamics are introduced.

## Subtask 7: Write the organizational model and its function and the issues the supervisor wants considered (the 20-page report requi

### Problem

Write the organizational model and its function and the issues the supervisor wants considered (the 20-page report requirement - here condensed into this machine-readable container as the single scored deliverable).

### Analysis

The container above is the complete, self-contained account of the model, its data, assumptions, parameter provenance, equations, simulation procedure, and results for all six analytic tasks. The executive-summary framing for the CEO: ICM's human-capital system is stable at the current 18% churn (fill ~85-92%, productivity ~90% of full strength) but has no slack: the 2x middle-manager churn is the structural weakness, and the organization cannot absorb a sustained step-up to 25-35% churn without either doubling its recruiting pipeline or accepting a decaying organization. The single cheapest intervention is a mid-manager retention program targeted at the ~15% of that layer most exposed to churn, using growth opportunities and recognition - not pay. The HR manager's multilayer vision is the durable fix: it converts reactive backfill into predictive, multi-signal talent management.

### Modeling Process

Report structure mapped to tasks: Section 1 = task 1 (network model + assumptions + data cleaning); Section 2 = task 2 (dynamics: churn contagion, stalled-growth feedback, productivity equation, acting coverage); Section 3 = task 3 (2-year budget in sigma: 619.3 sigma total, component breakdown); Section 4 = task 4 (sustainability at 25%/35% churn with costs and indirect effects); Section 5 = task 5 (30% mid-level churn, no external recruiting, qualified-only variant); Section 6 = task 6 (multilayer/team-science vision); Section 7 = this synthesis. All formulas, constants, and their provenance appear in the corresponding task's mathematical_modeling_process field, including the full empirical parameter table. Empirical parameter table (every number not from table1.csv or the task statement is listed here):
name = value, interval [a, b], source
1. churn-contagion channel = tie-by-tie diffusion along informal intra-level work/friendship ties (20% densest random pairs per level), interval n/a (structural), source: expert exchange 1.
2. churn-contagion recall window = 0.25 yr (3 months) of departures count toward contagion, interval [0.08, 0.5] yr, source: expert exchange 2.
3. non-manager departure handling = reporting line unchanged, duties absorbed in-team, interval n/a (mechanism), source: expert exchange 3.
4. manager-vacancy coverage = reports re-attach to acting level-up boss until backfill, interval n/a (mechanism), source: expert exchange 4.
5. new-hire productivity ramp r by level (yr) = senior mgr 1.0, junior mgr 1.0, exp supervisor 0.5, inexp supervisor 0.5, exp employee ~0.3, inexp employee 0.2, clerical 0.2; internal promotions ramp 50% faster, interval [0.08, 1.0] yr, source: expert exchange 5.
6. workload-gap perception = immediate (day 0), response lags weeks-months, interval n/a (mechanism), source: expert exchange 6 (implemented as same-day half-efficiency vacancy drag).
7. acting-boss span-of-control strain = +0.02/yr dissatisfaction on the covered team, interval [0.01, 0.05]/yr, source: expert exchange 7.
8. promotion gate = vacancy-gated AND tenure >= 3 yr at level; ratings as eligibility filter among qualified; internal fill fraction of manager/supervisor vacancies = 0.20, interval [0.10, 0.30], source: expert exchange 8 (mechanism) + range assumption.
9. retention levers = growth/advancement dominant, pay hygiene (10% pay cut -> ~10% hazard cut only); stalled-growth churn hazard multiplier = 2.0 when the level above is <90% filled, interval [1.5, 3.0], source: expert exchange 9.
10. effort response to sustained churn = net average effort decline, slope 0.25 per unit dissatisfaction (swept [0.15, 0.35]), source: expert exchange 10.
11. hiring capacity = 9% of 370 positions (~33 seats) as concurrent external requisitions at any time, interval [8, 10]% of positions, source: task statement (8-10% actively hiring).
12. middle-manager churn = 2x company rate (36%/yr vs 18%/yr), source: task statement.
13. base churn = 18%/yr, source: task statement.
14. fill status = 85% of positions filled at any time; 80% floor in task 4, source: task statement.

### Outcome Analysis

Main conclusions: (1) The 85%-filled status is an equilibrium, not a target - the organization runs permanently ~10-15% understaffed because the recruiting pipeline (33 concurrent requisitions) cannot outpace even 18% churn. (2) Middle management is the critical layer: 2x churn, structurally stuck, and its loss cascades downward via stalled growth and span drift. (3) Churn of 25-35% is unsustainable at current hiring capacity - fill crosses the 80% floor within 2 years at 25% and collapses at 35%; the indirect costs (effort decline, management hollow-out, self-reinforcing hazard) exceed the direct recruiting costs. (4) The no-external-recruiting stress test shows the promotion pipeline alone cannot refill the mid levels - an order of magnitude too small - and the qualified-only rule can freeze it entirely. (5) The multilayer network is the right durable architecture for the HR office to lead. Overall limitations: per-level aggregation of individual states, synthetic tie structure, and order-of-magnitude calibration of the dissatisfaction dynamics; a per-individual agent-based extension with real tie data would sharpen the churn-risk layer. Bias: the model is calibrated to the 2019 ICM snapshot; structural drift (salary compression, remote work, market wage changes) is outside its domain of validity.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
