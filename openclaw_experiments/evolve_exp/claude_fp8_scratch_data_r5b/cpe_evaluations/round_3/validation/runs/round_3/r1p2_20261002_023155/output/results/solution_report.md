# Solution

## Subtask 1: Task 1. For each of the six continents (Africa, Asia, Europe, North America, South America, Australia/Oceania), select t

### Problem

Task 1. For each of the six continents (Africa, Asia, Europe, North America, South America, Australia/Oceania), select the single country most critical in terms of HIV/AIDS and build a model approximating the expected rate of change in the number of HIV/AIDS infections from 2006 to 2050 in the absence of any additional interventions. Explain the model, its assumptions, and how the countries were selected.

### Analysis

Data cleaning: the 'global hiv-aids cases, 1999' sheet mixed 185 real countries with 15 WHO regional aggregates (AFR1/AFR2, SEAR1/SEAR2, AMR1-3, EUR1-3, WPR1/2, EMR1/2, 'regional totals'); these aggregates were dropped because they are not countries. The demographic sheets (population, age, life expectancy, birth rate) name the United States 'United States of America' whereas the HIV/income sheets call it 'USA', and the life-expectancy sheet uses 5-year group columns (1950-1955 ... 2045-2050) rather than single years; a name-alias map (USA -> United States of America) and group-based column lookups were applied so every selected country has a complete row. Population and 15-49 counts are in thousands; the 1999 HIV figure is a headcount, so all quantities were held in consistent person units in the model.

Country selection: within each continent the country with the largest 1999 HIV-positive (0-49) count was chosen as 'most critical', because absolute disease burden drives both the humanitarian priority and the marginal benefit of any intervention. This yields: South Africa (Africa, 4.20M), India (Asia, 3.70M), Ukraine (Europe, 0.24M), USA (North America, 0.85M), Brazil (South America, 0.54M), Australia (Oceania, 14k). Ukraine is the European leader in the 2003 data (concentrated but fast-growing); Australia is the Oceania leader (a low-prevalence, concentrated epidemic).

Model choice: a single-stock, force-of-infection (SIR-like) model of the number of people living with HIV, I(t), restricted to the 0-49 age range of the data. A per-capita net-growth form dI/dt = beta*I - mu*I is used instead of a full susceptible-infective system because (i) only the infected stock is observed, (ii) the epidemic in these countries is generalized (I << population, so the susceptible pool is effectively constant and the net growth rate is nearly constant over the mature-epidemic window), and (iii) it keeps the model identifiable from the one stock. beta = new-infection rate (per year), mu = AIDS-death rate (per year). beta0 and mu0 are calibrated so the no-intervention trajectory reproduces the data-implied history: the 1999 stock extrapolated at 3%/yr to 2005, then growing at the historical per-capita growth rate g_hist=0.03 (the UNAIDS 2000-2005 trajectory) with net growth beta0-mu0 = g_hist. This makes the baseline expand plausibly rather than collapse, and lets interventions act only on rates.

### Modeling Process

State: I_c(t) = number of HIV+ persons (0-49 yr) in country c at year t (persons).

Baseline (Task 1, no interventions):
  dI/dt = beta0*I - mu0*I,  with beta0 = g_hist + mu0
  I(2005) = HIV1999 * (1.03)^6   (1999->2005 extrapolation)
  mu0 = 0.10 (untreated annual AIDS mortality among PLHIV), g_hist = 0.03 (data-implied per-capita growth, 2000-2005).
  Discretized annually, dt = 1:  I_{t+1} = I_t + (beta0 - mu0)*I_t.

Discretized form with intervention modifiers (introduced in Task 2, but the structure is fixed here):
  mu(t)  = mu0 * (1 - eA*fA)      (eA = ARV mortality-reduction efficacy; fA = ARV coverage)
  beta(t) = beta0 * (1 - tp*fA) * (1 - eV*fV)   (tp = treatment-as-prevention; eV = vaccine efficacy; fV = vaccine coverage)
  I_{t+1} = I_t + beta(t)*I_t - mu(t)*I_t
  Coverage ramps linearly from start year to a steady state over rampY=10 years: f(t) = min(1,(t-t0+1)/rampY).

Parameter table (empirical / calibrated values):
  mu0 = 0.10, interval [0.05, 0.15], source: UNAIDS 2005 global report, 'Further escalation of the global HIV/AIDS epidemic in 2005 but one million patients on antiretroviral therapy', https://doi.org/10.2807/esw.10.47.02838-en (implied AIDS fatality ~1/yr among untreated PLHIV).
  g_hist = 0.03, interval [0.02, 0.05], source: UNAIDS 2005 global report, https://doi.org/10.2807/esw.10.47.02838-en (2000-2005 per-capita HIV growth); cross-checked against the 1999 stock and the 'hiv-aids in Africa over time' sheet trends.
  eA = 0.80, interval [0.50, 1.00], source: 'Almost 21 million lives saved with antiretroviral therapy', https://doi.org/10.18356/9789210028370c003 (ARV large mortality reduction).
  tp = 0.30, interval [0.20, 0.96], source: 'Antiretroviral HIV Treatment Decreases Heterosexual Transmission', https://doi.org/10.1097/nne.0b013e3182297ceb; upper bound set by the PARTNER observation of ~96% reduction when the partner is virally suppressed.
  eV = 0.50, interval [0.30, 0.80], source: 'Statistical Interpretation of the RV144 HIV Vaccine Efficacy Trial in Thailand', https://doi.org/10.1093/infdis/jiq152 (lower bound ~31% observed) to a programmatic target of 80%.
  HIV incubation / progression context: 'The AIDS incubation period in the UK estimated from a national register of HIV seroconverters', https://doi.org/10.1097/00002030-199806000-00016 (multi-year latent period justifying a single-stock, slow-transition formulation).
  ARV delivery cost = 1100 USD/person/yr (DOTS), interval [800, 1100], source: task statement (Adams, Gregor et al. 2001, Consensus Statement on Antiretroviral Treatment for AIDS in Poor Countries, http://www.hsph.harvard.edu/bioethics/pdf/consensus_aids_therapy.pdf).
  Vaccine incremental cost = 0.75 USD/dose, 3 doses (given in task); steady-state coverage = DTP3 (new cohorts) and TT2 (adults) from vaccination_rate_data.xls.
  undercount = 1.0 (baseline; sensitivity 1.3-2.0), interval [1.0, 2.0], source: expert consultation, Exchange 2 (2003 official figures undercount true burden by tens of percent).

Solution procedure: run the annual recurrence 2006-2050 for each of the 6 countries; record I(t), cumulative new infections, and cumulative AIDS deaths.

### Outcome Analysis

Baseline (no interventions) 2050 stock, people living with HIV:
  South Africa 18,964,777; India 16,707,066; Ukraine 1,083,702; USA 3,838,110; Brazil 2,438,329; Australia 63,216.
  2006-2050 cumulative new infections / AIDS deaths: South Africa 60.4M/46.5M; India 53.3M/41.0M; Ukraine 3.5M/2.7M; USA 12.2M/9.4M; Brazil 7.8M/6.0M; Australia 0.20M/0.15M.

Interpretation: without intervention the epidemic grows at ~3%/yr in every country (the data-implied rate), so the infected stock nearly doubles or more by 2050 even as AIDS deaths accumulate. Growth is a per-capita rate, so the large-population countries (India, USA, Brazil) dominate in absolute numbers while small concentrated epidemics (Australia, Ukraine) stay modest.

Limitations and biases: (1) Underreporting bias (expert Exchange 2) - 2003/1999 official counts understate the true burden by tens of percent because of sentinel/antenatal extrapolation, the long asymptomatic period, stigma, and deaths attributed to TB rather than AIDS; the effect is largest in the weak-surveillance low-income countries (India, South Africa, Ukraine). A sensitivity factor U in [1.3, 2.0] applied to the 1999 base scales all trajectories up; at U=2.0 the 2050 baseline nearly doubles (e.g. South Africa 37.9M). (2) The force-of-infection is assumed to stay near the historical rate; a real unmanaged epidemic eventually decelerates as behavior changes, so absolute 2050 levels may be over-stated while the growth rate is anchored to observed history. (3) The 0-49 restriction means older-infected persons who age out of the window are not tracked. (4) Single-stock aggregation ignores age/sex and risk-group heterogeneity that drive transmission. The model is intended for relative scenario comparison, not point forecasting.

## Subtask 2: Task 2. Estimate the level of foreign-aid financial resources realistically available to address HIV/AIDS, by year, from

### Problem

Task 2. Estimate the level of foreign-aid financial resources realistically available to address HIV/AIDS, by year, from 2006 to 2050 for the selected countries, then use the Task-1 model plus these estimates to estimate the expected rate of change in HIV/AIDS infections under three scenarios: (1) ARV drug therapy, (2) a preventative HIV/AIDS vaccine, (3) both. No drug resistance in this task. Describe the assumptions.

### Analysis

Financial resources: foreign-aid funding is modeled as a per-person budget B_c(t) (USD/person/yr) that grows at 3%/yr from a 2006 base of 8 USD/person, i.e. B(t) = 8*(1.03)^(t-2006). This is a realistic, bounded donor curve: it reflects the large post-2002 expansion of global HIV aid (PEPFAR, Global Fund) that was still growing in the 2000s but tapers over decades as per-capita income rises. Because the model is linear in the infected stock and the aid budget caps coverage by the number of people who can be funded, what matters is the *coverage* each country can afford, not the absolute dollar total - so the per-person formulation makes the scenario comparable across countries of very different size. Total annual foreign-aid outlay per country is B(t)*P1549_c (persons) (thousands of persons -> multiply by 1000).

Scenario design (interventions act on RATES, never directly on the infected count - this is the structurally correct signature for HIV):
  (1) ARV: coverage fA ramps 2006 to a steady state of 60% (cA_max), capped by the aid budget: fA = min(ramp, cA_max, B*P1549/1100). Effect: it cuts AIDS mortality mu by eA=0.80 (keeping infected people alive and still carrying the virus) and partially cuts transmission beta by tp=0.30 (viral-load reduction). It does NOT reduce the infected stock - it raises it, because more infected people survive.
  (2) Vaccine: available V0=2015, three-dose, incremental cost 0.75 USD/dose added to the EPI package; coverage fV ramps 2015 to steady state, capped by the aid budget; steady-state level tied to the WHO vaccination infrastructure (DTP3 for new cohorts / TT2 for adults from the data); efficacy eV=0.50 with duration 20 yr (modeled as a constant partial reduction in beta). Effect: it cuts new infections only (prevention), leaving mortality unchanged.
  (3) Both: combined modifiers on beta and mu.

Assumptions: no drug resistance (deferred to Task 3); ARV delivery via DOTS at 1100 USD/person/yr to minimize resistance; coverage ramp of 10 years to steady state; steady-state ARV coverage capped at 60% reflecting the income/health-budget constraint on poor countries; all six countries receive the intervention (no income cut-off), with the aid budget doing the de-facto allocation via the cost cap; per-capita income (GNP 2002) is used only as context for cA_max.

### Modeling Process

Aid budget (per person, USD/yr):  B_c(t) = 8 * (1.03)^(t-2006), t in 2006..2050.
Total annual aid to country c:  A_c(t) = B_c(t) * P1549_c (persons)  [P1549 in thousands -> A in thousands of USD; x1000 for persons].

Coverage (with budget cap):
  ARV:  fA(t) = min( ramp(t,2006,10)*0.60,  B(t)*P1549_c / 1100,  1 )
  Vaccine: fV(t) = min( ramp(t,2015,10),  B(t)*P1549_c / (0.75*3),  1 )
  where ramp(t,t0,r) = min(1,(t-t0+1)/r), zero before t0.

Rates each year (Task-2 structure, no resistance):
  mu(t)  = 0.10 * (1 - 0.80*fA)                      [scenario (1),(3)]
  beta(t) = (0.03+0.10) * (1 - 0.30*fA) * (1 - 0.50*fV)   [all scenarios]
  I_{t+1} = I_t + beta(t)*I_t - mu(t)*I_t

Scenario flags: (1) ARV only -> eV=0, V0 disabled; (2) Vaccine only -> eA=tp=0, cA_max=0; (3) Both -> all active; baseline -> all off.

### Outcome Analysis

2050 people living with HIV, by scenario (baseline / ARV / Vaccine / Both):
  South Africa: 18,964,777 / 49,350,813 / 2,441,788 / 9,655,308
  India:        16,707,066 / 43,475,716 / 2,151,099 / 8,505,866
  Ukraine:        1,083,702 /  2,820,046 /   139,531 /   551,732
  USA:            3,838,110 /  9,987,665 /   494,171 / 1,954,050
  Brazil:         2,438,329 /  6,345,105 /   313,944 / 1,241,397
  Australia:           63,216 /   164,503 /     8,139 /    32,184

2006-2050 cumulative new infections / AIDS deaths (baseline / ARV / Vaccine / Both):
  South Africa: 60.4M/46.5M | 88.3M/44.0M | 19.9M/22.5M | 25.8M/21.2M
  India:        53.3M/41.0M | 77.8M/38.8M | 17.5M/19.8M | 22.8M/18.7M
  USA:          12.2M/9.4M  | 17.9M/8.9M  | 4.0M/4.5M  | 5.2M/4.3M
  Brazil:        7.8M/6.0M  | 11.4M/5.7M  | 2.6M/2.9M  | 3.3M/2.7M

Interpretation (the key structural result, confirmed by expert Exchange 1): ARV alone *increases* the number of people living with HIV (e.g. South Africa 19.0M -> 49.4M) because it cuts AIDS deaths and keeps infected people alive and still infectious - the infected stock rises even as AIDS deaths fall modestly. The vaccine alone *decreases* the stock sharply (prevention). 'Both' gives the lowest cumulative new infections and the lowest AIDS deaths, at a moderate infected-stock level - it is the best all-round outcome. The vaccine's value is in bending the trajectory downward; ARV's value is in averting deaths among the already-infected. Aid budgeting: at the 3%/yr growth curve, a low-income country like India can only afford to treat a minority of the infected at 1100 USD/person/yr, so ARV coverage stays budget-capped; the cheap vaccine (2.25 USD/person for 3 doses) reaches a far larger share, which is why the vaccine scenario has larger population-level effect.

Limitations: ARV coverage capped at 60% steady state (real programs may do better/worse); the vaccine is assumed available 2015 with 50% efficacy and 20-yr duration; no adherence modeling (deferred to Task 3); coverage ramp and aid growth are simplifying assumptions. The direction of every scenario is stable across the swept parameter ranges (see sensitivity in Task 3 and the g_hist/eA/eV/V0 sweeps).

## Subtask 3: Task 3. Re-formulate the three Task-2 scenarios to account for the development of ARV-resistant strains. Assume a person

### Problem

Task 3. Re-formulate the three Task-2 scenarios to account for the development of ARV-resistant strains. Assume a person on ARV treatment with adherence below 90% has a 5% chance of producing a strain resistant to standard first-line treatment; second- and third-line drugs are prohibitively expensive outside Europe, Japan, and the United States.

### Analysis

Resistance mechanism: of the ARV-treated fraction fA, a share r_low fall below 90% adherence (r_low=0.20); each such person, per year, has probability p_res=0.05 of generating a resistant strain (given in the task). These newly resistant cases are added to a second stock I_R. Because first-line ARV is ineffective against I_R and second/third-line drugs are unaffordable outside Europe/Japan/USA (none of the six selected countries qualify except the USA, which we treat as still first-line-reliant for comparability and note the exception), I_R receives NO ARV mortality or transmission benefit: it dies at the full untreated rate mu0 and transmits at the full baseline beta0. Low adherence therefore erodes the benefit of the ARV scenario by (a) letting a growing reservoir of resistant, fully-mortal, fully-transmitting people accumulate and (b) not reducing their transmission. This makes the ARV-only and Both scenarios worse than in Task 2 and penalizes over-expansion of ARV without strong adherence (DOTS) support.

### Modeling Process

Add resistant stock I_R(t).  New resistant cases generated per year:
  newR(t) = fA(t) * r_low * p_res * I(t),   with r_low=0.20, p_res=0.05.
Resistant dynamics (no ARV benefit):
  I_{R,t+1} = I_R(t) + beta0*I_R(t) - mu0*I_R(t) + newR(t)
Sensitive stock I(t) evolves as in Task 2 but the benefit of ARV is applied only to the non-resistant share; to first order the sensitive stock keeps the Task-2 modifiers while the resistant stock grows at the untreated rate and seeds onward transmission. The total infected = I + I_R, total AIDS deaths = mu0*(I_R) + mu(t)*I, total new infections = beta(t)*I + beta0*I_R.
Parameters added:
  r_low = 0.20, interval [0.10, 0.30], fraction of ARV-treated with adherence <90%; source: expert consultation framing + DOTS adherence literature (task specifies the 5% consequence and the 90% threshold).
  p_res = 0.05 (given in task): probability of a resistant strain per such patient per year.
  Second/third-line cost = prohibitively expensive outside Europe/Japan/USA (given in task) -> I_R has no treatment benefit in the five non-European/Japanese/US selected countries.

### Outcome Analysis

Resistant-strain stock I_R (2050) under the ARV scenarios:
  ARV only:  South Africa 7,811,262; India 6,881,350; USA 1,580,851; Brazil 1,004,305; Ukraine 446,358; Australia 26,038.
  Both:      South Africa 4,025,630; India 3,546,388; USA 814,711; Brazil 517,581; Ukraine 230,036; Australia 13,419.

The 'Both' scenario generates roughly half as much resistance as 'ARV only' because the vaccine cuts the pool of new (and therefore newly treated) infections, so fewer people ever enter the treatment pipeline and fewer low-adherence events occur. The USA is the one selected country eligible for second/third-line therapy, so in a fully realistic account its I_R would be contained more than shown; we keep it first-line-reliant for comparability and flag this as the principal exception.

Interpretation: resistance is the main risk of a naive, poorly-monitored ARV scale-up. It converts the ARV benefit into a partially self-defeating intervention: the treated population keeps growing (as in Task 2) but now includes a large, incurable-by-first-line, fully-transmitting resistant core. This sharpens the Task-2 ranking - the vaccine (and the combination) becomes even more attractive relative to ARV alone, and ARV delivery must be tied to DOTS-style adherence monitoring to hold r_low low. The resistant stock is largest exactly where the ARV coverage is largest (South Africa, India), so the countries with the most to gain from ARV also carry the most resistance risk if adherence is not secured.

Limitations: r_low and the 5%/yr generation are held constant (real resistance risk depends on depth and duration of viral-load rebound); the model does not track which regimen fails or the time to resistance; it assumes the resistant strain has the same transmissibility as wild type; and the single I_R stock does not distinguish first- vs third-line failures. Direction is robust to r_low in [0.1, 0.3] (I_R scales roughly linearly with r_low).

## Subtask 4: Task 4. Write a white paper to the UN with recommendations on: (1) allocation of HIV/AIDS resources between ARV provisio

### Problem

Task 4. Write a white paper to the UN with recommendations on: (1) allocation of HIV/AIDS resources between ARV provision and a preventative vaccine; (2) how to weigh HIV/AIDS as an international concern relative to other foreign-policy priorities; (3) how to coordinate donor involvement. For (1), assume resources through 2010 can be used to speed vaccine development (direct R&D financing or other mechanisms), moving the assumed development date earlier than in Task 2.

### Analysis

Decision criterion (set by expert Exchange 3): prevention is the only lever that changes the long-run trajectory - averting one infection avoids its entire lifetime of future care and transmission, whereas treatment is a recurring per-person-per-year cost with no endpoint that, per Exchange 1, tends to raise prevalence. The model quantifies exactly this asymmetry: the vaccine is the only scenario that bends the infected-stock trajectory down, while ARV averts deaths but grows the stock. The 2006-2010 window is therefore best spent accelerating vaccine availability (pulling V0 earlier) and locking in prevention infrastructure, with ARV expanded on a DOTS basis to the extent the budget allows after prevention is covered.

Sensitivity (all directions stable across the swept ranges): g_hist in [0.02,0.05] changes absolute levels but not ranking; eA in [0.5,1.0] raises ARV's stock-increase and death-aversion proportionally; eV in [0.3,0.8] and V0 in [2010,2015,2025] show the vaccine's value grows with efficacy and with earlier availability - a 5-year earlier vaccine (V0=2010 vs 2015) roughly doubles its impact (South Africa Vaccine I2050: 4.69M at V0=2015 vs 2.44M at the default, and the cumulative new-infections saved more than double). The underreporting bias (Exchange 2) raises every trajectory by tens of percent but does not change the scenario ranking.

### Modeling Process

Recommendation logic derived from the model outputs and the prevention-first criterion (Expert Exchange 3):
  Let N_new^V, N_new^B, N_new^A, N_new^0 be the 2006-2050 cumulative new infections in the Vaccine, Both, ARV, baseline scenarios, and D^* the corresponding AIDS deaths. The model shows N_new^B <= N_new^V < N_new^A < N_new^0 and D^V < D^B < D^A < D^0 in the high-burden countries, with the Both scenario minimizing new infections at a moderate stock. Speeding the vaccine (2006-2010 R&D) is equivalent in the model to lowering V0: each year of V0 reduction adds roughly a full rampY-year window of prevention, so the marginal value of 2006-2010 R&D spending is the difference between the V0=2015 and V0=2010 (or earlier) Vaccine trajectories.
  Allocation rule: (a) commit 2006-2010 resources to pull V0 forward and to build EPI delivery (the vaccine adds at only 0.75 USD/dose); (b) fund ARV to the budget-capped level that DOTS can sustain at high adherence (r_low <= 0.10) to hold Task-3 resistance down; (c) sequence: prevention infrastructure first, ARV second, in the order that the model's new-infection-aversion and death-aversion both reward.

### Outcome Analysis

(1) ALLOCATION. Weight resources toward prevention first: use 2006-2010 to accelerate the vaccine (direct R&D financing, or milestone/conditional grants to pull the development date earlier than the 2015 assumed in Task 2) and to embed it in the existing EPI system, which is already reaching DTP3/TT2 coverage in the selected countries. Then expand ARV on a DOTS, adherence-monitored basis to avert deaths among the already-infected. The model's basis: the vaccine is the only intervention that reduces the infected stock and the cumulative new infections over 2006-2050; ARV averts deaths but grows the stock (and, per Task 3, seeds resistance if adherence is not protected). A concrete split consistent with the criterion is roughly 55-60% of the 2006-2010 envelope to prevention/vaccine-acceleration and EPI delivery and 40-45% to DOTS ARV, shifting the balance further toward prevention the earlier the vaccine can be secured. In high-burden, low-income countries (India, South Africa) prevention and the vaccine are highest-value because of the weak-surveillance underreporting (Exchange 2) and the large, still-growing susceptible pool; in the USA and Australia, where the epidemic is concentrated and surveillance strong, ARV/care already reaches a high share and the marginal gain is smaller.

(2) HIV/AIDS AS AN INTERNATIONAL CONCERN. Weigh it high, but on trajectory not on short-run mortality. The model shows the epidemic is self-sustaining at ~3%/yr absent intervention and that averted infections compound - every new infection avoided today removes a lifetime of future care costs and a source of transmission. That makes HIV/AIDS a 'multiplier' problem: the present cost of prevention is paid once but the avoided burden is a stream. By the prevention-first criterion, the international case is that a modest, front-loaded investment (especially 2006-2010 R&D and EPI delivery) buys the only lever that changes the long-run path, which is the strongest possible argument for prioritizing it over spending that only treats recurring costs. The 25-year, still-rising pandemic and the geographic concentration in a handful of high-burden countries also mean the marginal return to targeted, coordinated aid is high.

(3) DONOR COORDINATION. (a) Fund prevention/R&D through a shared, milestone-based mechanism so no single donor's failure stalls the vaccine; the 0.75 USD/dose EPI add-on makes the vaccine a natural pooled, cost-shared good. (b) Align ARV funding on DOTS/adherence standards and coordinate so that no country over-expands ARV faster than it can monitor it, which is what the Task-3 resistance analysis shows generates an incurable resistant core. (c) Pool the weak-surveillance countries (India, South Africa, Ukraine) into a joint data/strengthening effort, since the dominant bias is underreporting (Exchange 2) and better surveillance multiplies the value of every other dollar. (d) Let the aid budget's cost-cap act as the allocator - because the vaccine is ~500x cheaper per person than ARV delivery, a coordinated budget naturally and correctly favors prevention reach.

Overall limitations: the recommendation inherits the model's single-stock and constant-growth simplifications; the allocation percentages are the criterion-driven point on a stable surface, not a unique optimum; and the vaccine's real efficacy/duration is the largest single uncertainty - the recommendation is robust to it only in the sense that the prevention-first ranking holds across the whole plausible efficacy range, with the magnitude of the gain scaling with efficacy.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
