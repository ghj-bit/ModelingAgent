# Solution

## Subtask 1: Task 1: Develop a model that determines a country's fragility and simultaneously measures the impact of climate change; 

### Problem

Task 1: Develop a model that determines a country's fragility and simultaneously measures the impact of climate change; identify whether a state is fragile, vulnerable, or stable; and show how climate change increases fragility directly and indirectly through other indicators.

### Analysis

Following the expert's round-1 directive (Option C, hybrid), the model is an FSI-aligned weighted composite over the 12 published Fragile States Index indicators (Cohesion: C1 security apparatus, C2 factionalized elites, C3 group grievance; Economy: E1 demographic pressures, E2 economic decline, E3 uneven economic development, E4 human flight/brain drain; Society: P1 state legitimacy, P2 public services, P3 human rights/rule of law, P4 refugees/IDPs, X1 external intervention), each scored 0-10, so the composite F = 120 * sum(w_i x_i)/10 with equal weights w_i = 1/12 lies on the published 0-120 FSI scale and is directly comparable to FSI rankings. Climate change enters through a set of structural transfer functions that map climate stressors - drought severity d (0-1, multi-year), temperature anomaly t (C vs 1986-2005), sea-level rise s (m) - to indicator deltas. This keeps the index auditable and FSI-comparable (required for Task 2 benchmarking) while making the climate contribution a clean additive decomposition: F = F(baseline) + 12*sum(d_k)/10, where each d_k is a climate-induced increment on indicator k. Classification thresholds on the composite, anchored to FSI practice (top-10 floor ~90, 'Very High Alert' ~110): F < 45 stable; 45 <= F < 85 vulnerable; F >= 85 fragile. Direct climate pathways: yield loss -> E2/E3 (economic decline, uneven development); water/fiscal stress -> P2 (public services). Indirect pathways: scarcity -> stress-driven conflict terms loading on C1-C3, P1, P3, P4; scarcity-driven emigration -> E4; fiscal shock from GDP loss -> P2. All transfer-function magnitudes are anchored to the gathered empirical data (0.8% ag-GDP loss per drought event; 3-12% multi-year staple yield losses; -1.7% yield loss per +10% irrigation share).

### Modeling Process

Composite: F(x) = 120 * (1/12) * sum_k x_k / 10 = (12/10) * sum_k x_k, x_k in [0,10]. Yield-loss submodel (anchored to Wu et al. 2019 and Nature Comms 2025 benchmarks): yl(d,t) = 0.03 + 0.07*(1 - exp(-1.2*d)) + 0.02*max(0, t-1), giving ~3% loss at moderate multi-year drought (d=0.5) and ~10-12% at severe drought, matching the 3-12% benchmark band; irrigation mitigation: yl <- yl*(1 - 0.017*irrigation), i.e. -1.7% loss per +10% irrigation share. Climate deltas (points on the 0-10 scale), with agrarian GDP share alpha = 0.30 and GDP shock g = yl*alpha: E2 = 10*g/0.06 (6% GDP shock saturates at 10 pts), E3 = 10*0.7*g/0.06, E1 = 4*d^2 (food-scarcity demographic pressure), E4 = 0.5*E2, P2 = 8*0.35*d + 5*0.3*g/0.06, stress sigma = clip(0.6*d + 0.4*max(0,t-1), 0, 1.5), P4 = min(10, 4*sigma^2), P3 = 1.5*sigma, C1 = 1.2*sigma, C2 = 1.8*sigma, C3 = 2.2*sigma, P1 = 1.0*sigma, X1 = 0.6*sigma; sea-level rise adds 3*min(1,s) to P4 and 2*min(1,s) to E2. All deltas clipped to [0, 10 - x_k]. Calibration: reconstructed 2018 indicator scores give Yemen 93.5 (baseline; 98 observed including climate), South Sudan 107.0, Ethiopia 59.5 - consistent with the published 2018 FSI pattern (Yemen ~98 top-10, South Sudan #1, Ethiopia outside top 10).

### Outcome Analysis

Calibration reproduces the 2018 FSI ordering: South Sudan (107.0, fragile) > Yemen (98 observed, fragile) > Ethiopia (59.5, vulnerable). For Yemen at drought severity d=0.85 and +1.2 C, the climate deltas sum to ~25 indicator points (~19.6 composite points after clipping), largest in E2 (+3.9), P2 (+3.0), E1 (+2.9), E3 (+2.8), E4 (+2.0) - the direct (yield/fiscal) and demographic pathways dominate, with the conflict-side indicators (C1-C3, P1, P3, P4) contributing the indirect spiral of violence described in the problem background. Classification bands: stable < 45 < vulnerable < 85 < fragile; the 85 fragile threshold sits just below the 2018 top-10 floor, so being classified 'fragile' is approximately equivalent to top-10 status. Limitations: (1) indicator-level scores for Yemen/South Sudan are model reconstructions of the published totals (FSI publishes only totals at country level), so category/indicator detail carries reconstruction uncertainty while the totals are anchored; (2) transfer functions are literature-anchored estimates, not fitted to panel data; (3) the climate delta decomposition attributes the 2015-18 drought contribution but cannot fully separate concurrent war effects in Yemen; (4) equal indicator weights follow the FSI convention but alternative weightings shift composites by a few points without changing classifications in this range.

## Subtask 2: Task 2: Select one of the top-10 most fragile states per the 2018 Fragile States Index and determine how climate change 

### Problem

Task 2: Select one of the top-10 most fragile states per the 2018 Fragile States Index and determine how climate change increased its fragility; show in what way(s) the state may be less fragile without these climate effects.

### Analysis

Yemen was selected: it is in the 2018 top-10 (published FSI ~98) and is climate-exposed (arid, documented 2015-2018 multi-year drought and water stress). Per the expert's round-2 directive (Option A), the published 2018 total of 98 is decomposed into a no-climate baseline plus model-implied climate deltas from the 2015-18 drought (d=0.85) and warming (+1.2 C), with a uniform baseline shift solved so baseline + deltas reproduces the published 98 exactly. This makes the climate contribution a single auditable number and directly answers 'how much less fragile without these effects.' The 2014->2018 FSI rise (~75 -> ~98) is used as corroborating context, with the civil war as the dominant non-climate driver.

### Modeling Process

Observed: FSI_2018(Yemen) = 98 (fragile). Climate deltas at (d=0.85, t=1.2, s=0): E2 +3.93, E3 +2.75, E1 +2.89, E4 +1.97, P2 +2.97, P4 +1.39, P3 +0.88, C2 +1.06, C3 +1.30, C1 +0.71, P1 +0.59, X1 +0.35 (0-10 scale; ~19.6 composite points after clipping). Solve for uniform baseline shift a via bisection/brentq such that composite(YEMEN_BASE + a, with delta clipping) = 98. Counterfactual no-climate 2018 score = composite(YEMEN_BASE + a) = 78.4; with-climate score = 98.0.

### Outcome Analysis

Without the 2015-18 drought and warming, Yemen's composite would be ~78.4 instead of 98.0: classified VULNERABLE (45-85 band) rather than FRAGILE (>85), avoiding ~19.6 FSI points. The largest avoided losses are in public services (P2, +3.0 pts - water service collapse and fiscal shock), economic decline (E2, +3.9 pts - ag-sector/yield losses on an agrarian economy), and demographic pressure (E1, +2.9 pts - food-scarcity undernutrition/mortality), with material secondary effects on uneven development (E3), brain drain (E4), and the conflict-side indicators (C2, C3, P4). In other words: the drought is what pushed Yemen across the fragile threshold; without it the war alone leaves Yemen severely vulnerable but below the fragile-state line. Caveat (stated per expert directive): the indicator-level split is model-implied because FSI publishes only the total; the anchoring to the published 98 keeps the headline (19.6 points, vulnerable-vs-fragile crossing) auditable.

## Subtask 3: Task 3: Apply the model to a state not in the top-10 list to measure its fragility; determine in what way and when clima

### Problem

Task 3: Apply the model to a state not in the top-10 list to measure its fragility; determine in what way and when climate change may push it more fragile; identify definitive indicators; define a tipping point and predict when the country may reach it.

### Analysis

Ethiopia was selected: outside the 2018 top-10 (composite 59.5, 'vulnerable') and heavily exposed to Horn of Africa climate shocks (consecutive failed rainy seasons 2020-22, rising temperatures). The model projects Ethiopia's composite 2025-2050 under climate forcing: baseline governance drifts mildly upward (+0.4%/yr, modest institutional improvement), while climate deltas worsen at 6%/yr (climate_growth) from an initial drought severity of 0.30 and +0.8 C anomaly, compounding the Horn's consecutive-failed-rainy-seasons trajectory. Tipping point definition (per expert round 1): the first year at which the composite reaches or exceeds the fragile threshold (85) for two consecutive years (persistency condition to filter single-year noise), AND at least one 'definitive indicator' (E2 economic decline, E1 demographic pressures, or P4 refugees/IDPs) is at or above 6.5 (the 'severe' band). This is a first-passage threshold-crossing criterion, not a true dynamical bifurcation - a limitation stated explicitly, as directed.

### Modeling Process

Projection: F(y) = composite( clip(x_k^0 + d_k * 1.06^y, 0, 10) ) for y = 0..25, where d_k are the climate deltas at (d=0.30, t=0.8, s=0, irrigation=0.10) and the baseline includes a +0.4%/yr governance drift. Definitive-indicator tracking: first y with x_k^0 + d_k*1.06^y >= 6.5 for k in {E2, E1, P4}. Tipping year = smallest y with F(y) >= 85 and F(y+1) >= 85.

### Outcome Analysis

Ethiopia: F = 68.3 in 2025 (vulnerable) rising to 86.0 by 2050 (fragile). The composite crosses 85 at year 24 (2049) and holds above it in 2050, so the predicted tipping year is 2049 (persistency satisfied). Definitive indicators: E1 (demographic pressures) and E2 (economic decline) are already in the severe band (>= 6.5) from 2025 under the assumed climate trajectory - the demographic/economic stress leads, and the composite crossing is the binding constraint; P4 (refugees/IDPs) crosses later and acts as the confirming displacement signal. The way climate pushes Ethiopia more fragile is predominantly the direct agricultural pathway: repeated drought -> yield losses (3-12% multi-year benchmark) -> E2/E1 deterioration -> fiscal stress (P2) -> rising displacement pressure (P4) -> conflict-side loading (C3, P3). Definitive early-warning indicators to monitor: E1/E2 (food security and economic decline) trending >= 6.5 for two consecutive years, followed by P4 (rural-urban and cross-border displacement) - the sequence mirrors the Syria 2006-10 drought -> 2011 conflict pattern. Limitations: (1) first-passage construct, not a bifurcation - it predicts a crossing date, not an irreversible phase change; (2) the 6%/yr climate worsening is a scenario assumption (consistent with SSP2-4.5-class trajectories for the Horn), not a fitted rate; (3) Ethiopia's governance drift is assumed mildly positive; a war or political shock would shift the crossing earlier; (4) threshold sensitivity: at the 85 threshold the crossing is 2049; a 5-point threshold shift moves it ~4-5 years.

## Subtask 4: Task 4: Use the model to show which state-driven interventions could mitigate climate risk and prevent the country from 

### Problem

Task 4: Use the model to show which state-driven interventions could mitigate climate risk and prevent the country from becoming a fragile state; explain the effect of human intervention and predict the total cost of intervention for this country (Ethiopia).

### Analysis

Per the expert's round-3 directive (Option C, hybrid): the total cost is reported as a sum of traceable per-unit program norms (benchmark-anchored assumptions, stated as such), and the model's own benefit side - the avoided fragility crossing and the quantified yield-loss reduction - is used to show the bundle is sufficient. Three state-driven interventions target the model's dominant pathways: (I1) irrigation expansion, hitting the E2/E3 direct yield pathway (data benchmark: -1.7% yield loss per +10% irrigation share); (I2) crop adaptation - drought-resistant seed and water harvesting - hitting the yield-loss term (data benchmark: adaptation raises yields 15-64% vs no adaptation, Qin et al. 2023 envelope); (I3) social safety-net and community resilience programs, dampening the conflict-side indicators (C1-C3, P1, P3, P4) through which scarcity converts into the spiral of violence.

### Modeling Process

Intervention effects on the climate deltas: E2 <- E2*(1 - 0.6*adaptation) - 0.017*(irrigate_gain*10)*0.6 (adaptation recovers ~60% of the loss at intensity 0.5 within the 15-64% envelope; irrigation term is the -1.7% per +10% share effect on the E2 loading); E3 <- E3*(1 - 0.6*adaptation); each of C1, C2, C3, P1, P3, P4 <- value*(1 - 0.5*resilience_invest). Bundle: irrigate_gain = 0.10, adaptation = 0.50, resilience_invest = 0.40, applied from 2025. Cost lines (benchmark-anchored norms for a mid-sized low-income agrarian economy, ~$140B GDP, ~120M people): I1 irrigation +10 pts share: $0.8B one-off (norm $0.5-1.5B per +10% share); I2 drought-tolerant seed + water harvesting: $0.5B one-off (norm $0.1-0.5B); I3 safety-net/resilience: $0.3B/yr for 5 years (norm: safety nets at ~2-4% of GDP for LICs, here ~0.2% of GDP, targeted). Total 5-year cost = 0.8 + 0.5 + 5*0.3 = $2.8B (~0.4% of GDP/yr over the period). Projected trajectory with interventions: F(2025) = 66.7 -> F(2050) = 84.7, never reaching 85 (crossing averted; tipping year = none within horizon).

### Outcome Analysis

The bundle keeps Ethiopia below the fragile threshold through 2050 (F = 84.7 < 85), averting the 2049 crossing predicted without intervention - a 1.3-point margin that is the direct 'effect of human intervention' in model terms: the intervention bundle subtracts ~1.3 composite points from the 2050 trajectory and ~1.6 points in the near term (68.3 -> 66.7 in 2025). Mechanism: I1+I2 cut the direct yield-loss pathway (the dominant E2/E3/E1 loading), while I3 dampens the conflict-conversion of scarcity (C/P indicators). Cost-effectiveness: $2.8B over 5 years (~0.4% of GDP/yr) protects against a full fragile-state transition, whose downstream costs (fragile states run several GDP points below trend; the model's own climate-damage pathway compounds at ~0.8% ag-GDP per drought event) far exceed the bundle; the margin is thin (1.3 points), so the recommendation is to treat the bundle as the minimum sufficient set and to monitor the definitive indicators (E1, E2, P4) annually - if E1/E2 decline faster than the assumed 6%/yr climate growth, the margin closes and the safety-net component should be scaled up first (it has the best cost-to-damping ratio in the model). Limitations: (1) unit costs are benchmark-anchored assumptions, not from the gathered data file (stated per expert directive); (2) the 60% loss-recovery at adaptation intensity 0.5 is a midpoint of the 15-64% envelope, so effectiveness uncertainty is asymmetric (best case averts the crossing with margin; worst case the margin narrows but the crossing is still delayed); (3) implementation risk (funding, conflict disruption of programs) is not modeled; (4) costs exclude international co-financing, which for Ethiopia would plausibly cover a substantial share of I1/I2.

## Subtask 5: Task 5: Will the model work on smaller 'states' (cities) or larger 'states' (continents)? If not, how would it be modifi

### Problem

Task 5: Will the model work on smaller 'states' (cities) or larger 'states' (continents)? If not, how would it be modified?

### Analysis

The model's functional form (weighted composite over functional indicators + climate transfer functions + threshold classification) is scale-invariant in design, but the indicator CONTENT is sovereign-state-specific. The question is therefore handled as: same architecture, re-mapped indicators and localized forcing - with explicit loss of FSI comparability below the national scale, and loss of sovereignty-based indicators above it.

### Modeling Process

Cities: re-map the 12 indicators to municipal analogs - C1 security apparatus -> police/security capacity and crime; C2 factionalized elites -> local political fragmentation/corruption; C3 group grievance -> neighborhood/ethnic segregation grievances; E1 demographic pressures -> population growth and housing pressure; E2 economic decline -> municipal revenue/GDP trend; E3 uneven development -> intra-city inequality; E4 human flight -> out-migration from the city; P1 state legitimacy -> local government trust; P2 public services -> water/power/sanitation service coverage; P3 human rights/rule of law -> municipal rule of law; P4 refugees/IDPs -> internally displaced and informal-settlement share; X1 external intervention -> outside (provincial/international) governance involvement. Climate deltas are localized: urban heat-island temperature anomaly (replacing the national t), local flood/drought exposure (replacing the national d), coastal/river flood exposure (replacing s); the composite becomes a city-fragility index of identical functional form F = (12/10)*sum x_k, classified on the same 45/85 bands but not comparable to the national FSI. Continents: sovereignty-based indicators (P1, X1) are undefined at continental scale and are dropped or replaced by regional-institutional analogs (regional organization effectiveness, cross-border intervention); the composite is computed as a population/GDP-weighted mean of member-state composites, F_cont = sum_i (pop_i/sum_j pop_j) F_i, plus a regional-level climate delta term applied to the weighted indicators; the result is a regional fragility-exposure index, not a state score, and the tipping-point criterion is applied to the weighted composite with the same 45/85 bands.

### Outcome Analysis

Cities: the model works with re-mapping and localized climate forcing; the main modifications are (1) spatial disaggregation of the climate forcing (city-scale heat, flood, drought exposure), (2) sub-national fiscal weights in the E2/P2 loadings (municipal budgets are small, so a given yield/revenue shock hits P2 harder per point - the P2 loading coefficient should be increased), and (3) re-estimation of the 45/85 classification thresholds against a city-level benchmark distribution (the FSI bands do not transfer). Continents: the model does not work as-is because P1 (state legitimacy) and X1 (external intervention) presuppose sovereignty; the weighted-aggregation modification above makes it usable as a regional exposure index, at the cost of losing indicator-level comparability and of masking within-region dispersion (a continent 'average' can be stable while individual states are fragile - a limitation to report alongside any continental score). In both directions the tipping-point machinery (persistency-based first passage plus definitive indicators) transfers unchanged in form, with thresholds re-anchored to the new scale's distribution.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
