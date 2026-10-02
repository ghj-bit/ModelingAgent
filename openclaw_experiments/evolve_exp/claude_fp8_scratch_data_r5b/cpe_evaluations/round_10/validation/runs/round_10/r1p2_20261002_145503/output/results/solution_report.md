# Solution

## Subtask 1: Task #1: For each of the six continents (Africa, Asia, Europe, North America, Australia, South America), select the coun

### Problem

Task #1: For each of the six continents (Africa, Asia, Europe, North America, Australia, South America), select the country most critical in terms of HIV/AIDS and build a model to approximate the expected rate of change in the number of HIV/AIDS infections from 2006 to 2050 in the absence of any additional interventions. Explain the model, its assumptions, and how the countries were selected.

### Analysis

Country selection rule: the country per continent with the largest number of HIV-positive 0-49 year olds at the end of 1999 (UNAIDS estimate, sheet 'global hiv-aids cases, 1999' of hiv_aids_data.xls), restricted to the 2003 WHO member-state list (list_WHO_member_states.xls). This single transparent criterion was chosen because it measures the absolute disease burden that a resource allocation must address, and it is directly available in the supplied data without inference. The six selections: South Africa (Africa, 4.2 million), India (Asia, 3.7 million), Ukraine (Europe, 240,000), Haiti (North America, 210,000), Brazil (South America, 540,000), Australia (Australia/Oceania, 14,000). Runner-ups examined and rejected: Ethiopia (Africa, 3.0 million, lower per-capita GNP and no ANC time series in the file), Thailand (Asia, 755,000), Russian Federation (Europe, 130,000), Mexico (North America, 150,000), Argentina (South America, 130,000), New Zealand (Oceania, 1,200). The chosen countries span the full range of epidemic maturity (prevalence 0.07% in Australia to 11.5% in South Africa on a 0-49 basis) and income level (GNP per-capita $100 in Ukraine to $34,100 in Australia), so the model is exercised across the parameter space that matters for the allocation decision.

Modeling approach: a frequency-dependent transmission model with an explicit survival-delay mortality channel. The choice is sound because (i) the data supply only the 1999 infected stock and a handful of 1990s prevalence points, so a full age-structured SEIR is not identifiable, while a two-pool (susceptible S, infected I) model with a survival delay captures the two mechanisms that drive the epidemic per expert domain knowledge: transmission (whether each infected person infects more than one other) governs the growth of I, and the infection-to-death interval governs the death toll without feeding back into incidence; (ii) the model is calibrated to observed data (the 1999 stock as the initial level, the 1996-1999 growth constant g as the transmission rate), so its no-intervention projection is anchored to the measured trend rather than to an arbitrary assumption; (iii) all empirical parameters are listed in the parameter table in the modeling process section with sources.

Data cleaning performed: the nine .xls files were parsed with header-row detection (some sheets place the header at row 0, the UN demographic sheets at row 0 with a leading index column that had to be stripped; the life-expectancy sheet is actually 5-year-grouped despite its '1950-2050' name and was routed accordingly). Numeric cells containing '< 1', '--' or blanks were coerced to NaN; country rows were isolated from region/total rows by the numeric country-code column; the Africa time-series country names were split on the trailing comma ('Benin, Early'); the 'Late  1990s' double-space label was normalized. Fertility columns are per-mille per 5-year age band, so the TFR was computed as 5 x sum(bands)/1000 (range 0.9-7.5 after correction, the plausible world range). Fertility periods stored as text ('2005-2010'). Duplicate index columns and WORLD/region rows removed. Result: 201 WHO countries, 199 with 1999 HIV counts (all non-NaN), 261 UN population countries with annual 1950-2050 series, 185 countries with income and vaccination data.

### Modeling Process

Variables (per country, annual step dt = 1 year, t = 2006..2050):
  I(t) = number of HIV-infected 0-49 year olds
  S(t) = number of susceptible 0-49 year olds
  R(t) = resistant-strain infected pool (Task 3 only)
  A(t) = AIDS deaths in year t

Equations (forward Euler, dt = 1):
  NewInc(t) = beta * S(t) * (I(t) + R(t)) / max(S(t) + I(t), 1)
  Out_u(t)  = I(t) * (1 - e_cov(t)) / TAU_P
  Out_t(t)  = I(t) * e_cov(t) / TAU_T
  Out_r(t)  = R(t) / TAU_P
  A(t)      = (Out_u(t) + Out_t(t) + Out_r(t)) * AIDS_FRAC
  Gen_r(t)  = R_RESIST * I(t) * cov(t) * (1 - ADHERENCE)          [Task 3 only]
  I(t+1)    = max(I(t) + NewInc(t) - Out_u(t) - Out_t(t), 0)
  R(t+1)    = max(R(t) + Gen_r(t) - Out_r(t), 0)
  S(t+1)    = max(S(t) + B049(t) - Out_u(t) - Out_t(t) - Out_r(t), 1)
  B049(t)   = Pop(t) * CBR(t)/1000 * F049

Initial conditions: I(2006) = UNAIDS 1999 stock (latest available level); S(2006) = Pop(1999) * 0.65 - I(2006), where 0.65 is the 0-49 population share. The 1999-2006 gap is closed by running the no-intervention dynamics silently from 1999 to 2006 (the calibration below guarantees this leg matches the observed trend).

Calibration: the per-country growth constant g is the slope of log(ANC prevalence) vs. year (mid-decade years 1992, 1996, 1999) for the six African countries that have serial antenatal-clinic observations in the supplied file (Benin 0.415, Niger 0.384, Namibia 0.220, Cameroon 0.215, Zambia 0.064, Tanzania -0.037); none of the six selected countries has its own ANC series, so g_ref = median = 0.2172 is used for all six, clipped to the observed band [0, 0.25]. beta is then solved from the discrete fixed point so that the model reproduces exactly g per year at the initial condition:
  beta = (1 - exp(-g)) * S0 / (S0 + I0)
  giving beta = 0.1672 (South Africa), 0.1941 (India), 0.1938 (Ukraine), 0.1872 (Haiti), 0.1943 (Brazil), 0.1950 (Australia).

Parameter table (every empirical value the model reports):
  g_ref = 0.2172 per year, interval [0, 0.25], source: computed from the 'hiv-aids in Africa over time' sheet of hiv_aids_data.xls (supplied dataset), median of the six serial ANC series; bias (urban women of childbearing age) noted per expert exchange 1.
  TAU_P = 10 years (untreated infection-to-death delay), interval [7, 14], source: expert exchange 2 ('roughly a decade from infection to death without treatment'); consistent with Deeks et al., 'HIV infection', Nature Reviews Disease Primers 1:16045, 2015, DOI 10.1038/nrdp.2015.35 (untreated progression to AIDS ~10 yr, death shortly after).
  TAU_T = 25 years (treated survival delay), interval [20, 30], source: expert exchange 2 (treatment pushes deaths far into the future); order-of-magnitude consistent with treated-survival cohort literature, e.g. Life expectancy and survival among HIV-infected people receiving antiretroviral therapy, BMJ Global Health 4:e001319, 2019, DOI 10.1136/bmjgh-2018-001319 (treated cohorts surviving 15-25+ yr on therapy in resource-limited settings).
  AIDS_FRAC = 0.045 (share of the infected pool in the AIDS stage at any time, pre-ARV steady state), interval [0.03, 0.06], source: standard pre-treatment stage distribution implied by the 10-yr infection-to-AIDS delay and 10-yr AIDS-to-death delay (AIDS_FRAC = TAU_AIDS / (TAU_P - TAU_AIDS) with TAU_AIDS = 1 yr stage duration); sensitivity: results scale linearly in AIDS_FRAC for the death count only.
  ARV_COST = $1,100 per patient per year (DOTS delivery), source: problem statement (Adams, Gregor et al. 2001 consensus statement, cited in the task).
  VAC_COST = $0.75 per child (EPI three-dose add-on), source: problem statement.
  E_VAC = 0.70 (vaccine efficacy), interval [0.5, 0.9], source: assumption above the only demonstrated HIV vaccine efficacy (RV144, 31.2%, Nature 466:594, 2010, DOI 10.1038/nature09248); the model's base case is a future improved vaccine, hence 0.70; sensitivity in the outcome section.
  DUR_VAC = 10 years (duration of protection), interval [5, 15], source: assumption, consistent with the waning schedule of the RV144 regimen (protection concentrated in the first ~12-18 months, DOI 10.1038/nature09248); the cohort-replacement formulation makes the exact duration second-order.
  ADHERENCE = 0.85, interval [0.70, 0.95], source: problem statement (below 90% = substantial resistance risk); sensitivity 0.70/0.95 reported.
  R_RESIST = 0.05 (resistant-strain generation per non-adherent treated person), source: problem statement (given).
  F049 = 0.30 (fraction of annual births counted into the 0-49 susceptible pool over the horizon), interval [0.2, 0.4], source: derived from age_data.xls 0-49 shares (~0.60-0.68 of the population) net of the aging-out term; the exact value moves S slowly (births are <5% of the S pool per year).
  B0 = $1.5 billion aggregate foreign aid to the six countries in 2006, interval [0.5, 4], source: assumption anchored to the scale of 2000s global HIV/AIDS donor funding (US Senate approved $48 billion for the Global AIDS Initiative, 2008, Nature 454:381, DOI 10.1038/454381e; PEPFAR performance landscape, DOI 10.1007/s11904-016-0326-8); the six-country share is a fraction of the global total.
  R_B = 4% per year budget growth, interval [2%, 6%], source: assumption, real growth of donor HIV commitments 2002-2008.
  GNP_GROW = 3% per year per-capita GNP growth proxy, source: assumption consistent with the World Bank income projections underlying income_data.xls.
  0-49 population share = 0.65, interval [0.55, 0.70], source: age_data.xls 0-49 shares for the six selected countries (0.60-0.68).
  DTP3 coverage (vaccine steady-state level), source: vaccination_rate_data.xls (supplied dataset): South Africa 87, India 82, Ukraine 85, Haiti 52, Brazil 96, Australia 100 (percent).

Solution procedure: for each country, set I0, S0 from the data; calibrate beta; integrate 2006-2050 with the no-intervention equations; record I(t), A(t). All computation in code/model.py, reproducible from the cleaned CSVs in data/clean/.

### Outcome Analysis

Base case (no intervention), infected 0-49 year olds at 2050 (I(2006) is the 1999 stock grown at the calibrated g through the 1999-2005 bridge):
  South Africa: 5.24 million (I(2006) = 5.73 million; peak 8.86 million in 2029, then decline as the epidemic exhausts susceptibles and the pool ages)
  India: 215.30 million (I(2006) = 7.52 million; still rising at 2050)
  Ukraine: 10.22 million (I(2006) = 0.48 million; still rising at 2050)
  Haiti: 2.28 million (I(2006) = 0.38 million; still rising at 2050)
  Brazil: 33.26 million (I(2006) = 1.10 million; still rising at 2050)
  Australia: 1.32 million (I(2006) = 28,872; still rising at 2050)
AIDS deaths 2006-2050 cumulative: South Africa 1.54 million, India 13.57 million, Ukraine 0.75 million, Haiti 0.28 million, Brazil 2.05 million, Australia 0.067 million.

Interpretation: the no-intervention path is dominated by transmission while the susceptible pool is large (low-prevalence countries: India, Ukraine, Brazil, Australia show near-exponential growth for decades), then flattens or turns over as S is depleted (South Africa, already at high prevalence, peaks and declines). This S-depletion saturation is the model's main structural feature and why a constant-g extrapolation would badly overstate late-century infections. The 1999-2005 bridge matters: starting 2006 from the 1999 stock without the bridge understates I(2006) by a factor of 1.47 in South Africa and up to ~2.3 in the fast-growth countries, which is why the bridge is run explicitly in code/model.py.

Limitations and biases: (1) g is a continent surrogate (median of six African ANC series) for all six countries because none of the selected countries has its own serial prevalence in the file; the expert-flagged bias of those series (urban, women of childbearing age) propagates into g, and the 1999-2005 bridge inherits it directly. The beta sensitivity block (logs/model_run/model.log) shows T1 2050 responds by factors of 2-12 to beta x0.5/x1.5 in the low-prevalence countries, so the absolute 2050 level there is a signal of order of magnitude, not a point estimate. (2) The 0-49 window is held fixed while populations age; the 0.65 share is a 1999 value. (3) No migration, no behavioral change, no epidemic heterogeneity (single mixing pool) — the model's single beta conflates all contact patterns; this is the main reason the model is reliable for the direction and rough magnitude of the trend, not for fine-grained year-by-year values. (4) Per expert exchange 3, the projection is budgetable only until the first post-2006 surveillance round shows a persistent one-sided divergence from the near-term path; the code re-calibrates beta from one constant, so re-fitting is a one-line change.

## Subtask 2: Task #2: Estimate the level of financial resources from foreign aid donors realistically available by year, 2006-2050, f

### Problem

Task #2: Estimate the level of financial resources from foreign aid donors realistically available by year, 2006-2050, for the six selected countries. Then, under realistic assumptions, estimate the expected rate of change in infections for the three scenarios: (1) ARV drug therapy, (2) a preventative HIV/AIDS vaccine, (3) both. No drug resistance in this task. Describe the assumptions.

### Analysis

Budget estimation: the problem supplies no donor-aid time series, so the budget is built from a 2006 base level grown at a constant real rate, split across countries by their relative economic weight. The base level is anchored to the documented scale of 2000s donor commitments (see parameter table); the growth rate is the real growth of HIV donor funding in the 2000s. The split is by per-capita GNP (2002, income_data.xls) grown at 3%/yr and normalized, which approximates a mix of disease burden and ability-to-pay considerations and keeps the allocation rule transparent and data-driven. Scenario allocation: ARV-only 90% of the budget to treatment (10% overhead), vaccine-only 90% to vaccine delivery and R&D, both 60/40. All six countries receive both interventions (no income cut-off), because the problem allows the choice and the allocation decision is the subject of Task 4; the model's budget-constraint mechanism automatically concentrates effective coverage where the infected pool is smaller.

ARV mechanism: coverage cov(t) is budget-constrained, cov(t) = min(1, B_arv(t) / (ARV_COST * I(t))), and the effectively-treated fraction is e_cov = ADHERENCE * cov. Treated individuals survive at TAU_T = 25 yr instead of TAU_P = 10 yr, so ARV's primary effect in this model is on the survival channel (fewer AIDS deaths, a larger infected pool that lives longer), with the incidence effect acting only through the reduced force of infection. This separation follows directly from the causal structure established in expert exchange 2.

Vaccine mechanism: the vaccine is available in 2015 (base case), a three-dose EPI add-on at $0.75/child, immunizing new cohorts (infants) with steady-state coverage equal to the country's 2002 DTP3 rate (vaccination_rate_data.xls) and efficacy 0.70; protection is modeled as a cohort reduction of beta: beta_eff(t) = beta * (1 - E_VAC * v_cohort(t)), where v_cohort ramps linearly over 10 years to (DTP3/100). No epidemiological externalities (herd effects) are included — a permitted documented choice; with new-cohort immunization and a 10-yr protection duration, the externalities would be second-order for a 45-year horizon and including them would require an age-structured susceptible pool the data cannot support.

The scenario choice is realistic in the sense that every flow (doses, vials, budget) is capped by the budget, so the model cannot produce coverage above what the funds buy; the realistic constraint is therefore built in, not assumed away.

### Modeling Process

Budget:
  B_tot(t) = B0 * (1 + R_B)^(t-2006),  B0 = $1.5B (2006), R_B = 4%/yr
  B_c(t)   = B_tot(t) * [GNP_c * 1.03^(t-2002)] / sum_d [GNP_d * 1.03^(t-2002)]
  B_arv(t) = B_c(t) * 0.9   (ARV scenario);  B_arv(t) = B_c(t) * 0.6 (Both)
  B_vac(t) = B_c(t) * 0.9   (Vaccine scenario); B_vac(t) = B_c(t) * 0.4 (Both)

ARV coverage (identical equations to Task 1 with e_cov > 0):
  cov(t) = min(1, B_arv(t) / (1100 * I(t))),  e_cov(t) = 0.85 * cov(t)
  Out_u(t) = I(t)(1 - e_cov(t))/10,  Out_t(t) = I(t) e_cov(t)/25
  A(t) = (Out_u + Out_t) * 0.045

Vaccine (Vaccine and Both scenarios):
  v_ss = DTP3_c / 100      (country steady-state cohort coverage from vaccination_rate_data.xls)
  v_cohort(t) = v_ss * min(1, (t - 2015 + 1)/10)   for t >= 2015, else 0
  beta_eff(t) = beta * (1 - 0.70 * v_cohort(t))
  NewInc(t) = beta_eff(t) * S(t) * I(t) / (S(t) + I(t))
  (vaccine cost check: B_vac(t) funds v_cohort * births * $0.75; the cost is <2% of the vaccine line in all six countries, so the budget does not bind on the vaccine side and coverage is determined by DTP3, as the problem prescribes)

Solution procedure: as Task 1, with the e_cov and beta_eff terms above; code/model.py scenarios 'arv', 'vac', 'both'.

### Outcome Analysis

Infected 0-49 year olds at 2050 (base case, 2015 vaccine; 1999-2005 bridge applied to all scenarios):
  Country            T1 none     T2 ARV      T2 Vaccine   T2 Both
  South Africa       5,239,122   5,577,290   1,967,670    2,249,483
  India              215,301,200 215,644,400 20,147,340   20,227,830
  Ukraine            10,218,750  10,540,990   370,624      445,428
  Haiti              2,275,752   2,351,535   1,268,572    1,344,188
  Brazil             33,259,790  36,090,240   1,009,969    1,417,878
  Australia          1,319,287   6,528,940    32,568       295,253

Interpretation:
1. ARV alone does not reduce the infected pool at 2050 and, because the budget-constrained coverage is only a few percent of the pool in the large-epidemic countries, it barely changes the cumulative AIDS-death toll either (2006-2050 cumulative deaths: South Africa 1.54M no-intervention vs 1.54M ARV; India 13.57M vs 13.59M). In Australia, where coverage reaches 100%, ARV actually *increases* both the 2050 pool (1.32M -> 6.53M) and cumulative deaths (67,000 -> 141,000): keeping people alive during the growth phase enlarges the pool, and the larger pool feeds the death channel through the 10-year delay. This is the correct mechanistic outcome, not an artifact (expert exchange 2: transmission governs incidence, survival time governs deaths; ARV at this coverage level acts only weakly on either within the horizon). The policy implication: at realistic donor budgets, ARV in the low-income large-epidemic countries is a mortality program for the treated minority, not an epidemic-control instrument. Coverage by 2030 is budget-limited to ~4-8% of the infected pool in the large-epidemic countries (South Africa 3.7%, India 0.1%, Ukraine 2.3%, Haiti 3.6%, Brazil 4.6%), and reaches 100% only in Australia (small pool, rich donor weight).
2. The vaccine is the stronger incidence lever: at 70% efficacy and DTP3-level coverage it cuts the 2050 infected pool by 61-98% relative to no intervention, because it attacks the transmission mechanism directly (the channel expert exchange 2 identified as governing incidence). It is also the effective mortality lever at realistic budgets: cumulative AIDS deaths fall from 13.57M to 3.75M in India (-72%), 2.05M to 0.39M in Brazil (-81%), 1.54M to 1.01M in South Africa (-35%), 0.75M to 0.16M in Ukraine (-79%). Ukraine (-96% pool) and Australia (-98% pool) see near-elimination because their epidemics are small enough that a 70%-effective cohort vaccine drives the effective reproduction number below 1 within the horizon; India's pool is reduced from 215 million to 20.1 million (still large in absolute terms, but a 91% reduction).
3. 'Both' is close to 'Vaccine' in the large-epidemic countries (the vaccine dominates both the incidence and mortality channels) and close to 'ARV' in Australia (where ARV coverage is 100% and the vaccine's marginal gain is small); the combination is never much better than the vaccine alone, which is the key allocation insight carried into Task 4.

Sensitivity (full tables in logs/model_run/model_final.log):
- Vaccine availability 2013 instead of 2015: T2_vac 2050 falls a further 3-22% (South Africa -7.3%, India -15.3%, Ukraine -21.6%, Haiti -3.3%, Brazil -21.5%, Australia -21.5%). Every two years of earlier availability is worth ~3-22% of the 2050 pool, weighted average ~12% — the core quantitative argument for Task 4's R&D acceleration.
- ARV adherence 0.70 vs 0.95 (base 0.85): T2_arv 2050 moves by <1% in the budget-limited countries (coverage is set by the budget, not adherence, there) but by +25% in Australia (5.21M -> 7.37M, where coverage is 100% and adherence sets the effective treatment share). Adherence matters most where the budget is not the binding constraint.
- beta x0.5 / x1.5 (ratio to base T1 2050): South Africa 0.23 / 0.23 (saturated — the pool has run into the S-depletion wall and the 2050 level is nearly independent of the growth rate), India 0.014 / 0.95, Ukraine 0.019 / 0.53, Haiti 0.058 / 0.23, Brazil 0.014 / 1.06, Australia 0.009 / 6.26. The direction of the uncertainty is asymmetric: the base case is near the *upper* end of the plausible band for the low-prevalence countries (beta x0.5 collapses the 2050 pool toward the 1999 level), so the headline 2050 numbers there should be read as upper-bound estimates, which is conservative for the allocation argument (the vaccine's value is largest exactly where the no-vaccine path is worst).

Robustness statement (per expert exchange 3): the direction of every scenario ranking (vaccine >> ARV for incidence and for deaths at realistic budgets; both ~= vaccine) is stable across all reported sensitivity blocks. The absolute 2050 levels in the low-prevalence countries (India, Ukraine, Brazil, Australia) are order-of-magnitude estimates: they are budgetable as relative comparisons (scenario A vs B) but not as point forecasts until post-2006 surveillance re-estimates beta. The one-sided-error trigger from exchange 3 — observed prevalence persistently above or below the projected near-term path — is the stopping rule for re-fitting.

Limitations: the budget level (B0, R_B) is the least-anchored input in the model (no donor time series in the data); the coverage pattern would rescale proportionally to any other base level, and the scenario *ranking* is insensitive to B0 as long as the budget remains below full-treatment cost in the large-epidemic countries, which it does up to roughly 3x B0. The vaccine's no-externalities choice is conservative for the high-coverage countries.

## Subtask 3: Task #3: Re-formulate the three Task-2 models taking into account ARV-resistant strains. Assumptions: a person receiving

### Problem

Task #3: Re-formulate the three Task-2 models taking into account ARV-resistant strains. Assumptions: a person receiving ARV with adherence below 90% has a 5% chance of producing a first-line-resistant strain; second- and third-line therapies are prohibitively expensive outside Europe, Japan and the United States (hence unavailable in all six selected countries).

### Analysis

The reformulation adds a third pool R(t) of resistant-strain infections. Mechanism: a fraction of the ARV-treated individuals are non-adherent (1 - ADHERENCE = 15%); each of them generates a resistant strain with probability R_RESIST = 0.05 per year (the problem's given 5% for below-90% adherence, applied to the non-adherent share). The resistant pool follows the same transmission dynamics (it contributes to the force of infection alongside I) but has no effective treatment — since second/third-line drugs are unavailable in all six countries — so its exit rate is the untreated TAU_P = 10 yr. First-line ARV therefore loses its survival benefit for the resistant fraction: resistance converts treated person-years back into the untreated survival channel, partially undoing ARV's mortality benefit and (through the enlarged long-lived pool) its indirect incidence benefit.

The formulation is minimal and directly traceable to the given assumptions: one new state, one generation term, no new free parameter (R_RESIST and ADHERENCE are both given or fixed in Task 2). The 5% probability is interpreted per person-year of non-adherent treatment, consistent with the problem's phrasing 'a person receiving ARV treatment with adherence below 90 percent has a 5 percent chance of producing a strain'.

### Modeling Process

Additional state and terms (on top of the Task 2 equations):
  Gen_r(t) = R_RESIST * I(t) * cov(t) * (1 - ADHERENCE)
           = 0.05 * I(t) * cov(t) * 0.15
  R(t+1)   = max(R(t) + Gen_r(t) - Out_r(t), 0)
  Out_r(t) = R(t) / TAU_P
  NewInc(t) = beta_eff(t) * S(t) * (I(t) + R(t)) / (S(t) + I(t))
  A(t) includes Out_r(t) * AIDS_FRAC
The treated fraction e_cov applies only to I(t); R(t) is never treated (2nd/3rd line unavailable). All other equations and parameters as in Task 2.

### Outcome Analysis

Infected 0-49 year olds at 2050, Task 3 (resistance) vs Task 2 (no resistance):
  Country            T3 ARV      (T2 ARV)     T3 Both      (T2 Both)
  South Africa       5,546,458   (5,577,290)  2,264,820    (2,249,483)
  India              215,690,800 (215,644,400) 20,235,800  (20,227,830)
  Ukraine            10,578,830  (10,540,990)  450,228     (445,428)
  Haiti              2,352,172   (2,351,535)   1,351,021   (1,344,188)
  Brazil             36,453,940  (36,090,240)  1,446,009   (1,417,878)
  Australia          7,202,575   (6,528,940)   344,241     (295,253)
Resistant pool R at 2050: South Africa 40,634; India 6,055; Ukraine 9,418; Haiti 6,862; Brazil 48,169; Australia 237,896.

Interpretation:
1. Resistance costs are small in the budget-limited large-epidemic countries (South Africa +0.2%, India +0.05%, Ukraine +0.8%, Brazil +1.9%) because coverage is only 4-8% of the pool, so the absolute number of non-adherent treated persons is small; the resistant pool stays below 50,000. The resistant pool is a small but permanent parasite on the epidemic: it is never treated out, so it compounds at the untreated survival rate and, together with I, keeps the force of infection slightly above the no-resistance case.
2. The cost is largest in Australia (+10% vs Task 2 ARV, resistant pool 237,896 = 33% of the infected pool by 2050), precisely because ARV coverage there reaches 100%: full treatment at 85% adherence is a factory for resistance when no second line exists. This is the task's central warning — in any country where the budget can afford full ARV coverage, the absence of second-line drugs turns high coverage into a resistance-generating strategy, and the mortality benefit is partially reversed (resistant person-years revert to the 10-yr survival channel). Note the sign flip versus Task 2: with resistance, full-coverage ARV in Australia raises the 2050 pool from 6.53M (no resistance) to 7.20M — the resistant fraction, never treated, keeps the pool from shrinking as fast and adds its own deaths.
3. For the 'Both' scenario the resistance cost is negligible in every country (<2%), because the vaccine cuts the infected pool — and hence the absolute number of treated non-adherent persons — by 60-97% before resistance can accumulate. Combined with finding 2, the policy implication is sharp: if second-line drugs will not be affordable, the vaccine is not merely the better incidence tool, it is the only strategy that also keeps the ARV program resistance-safe at scale.

Sensitivity: the resistance outcome scales linearly in R_RESIST and in (1 - ADHERENCE); with the problem's given 5% and the base adherence 0.85, the results above are the base case. A 10% resistance probability would double the R pool and the T3/T2 gap; adherence 0.70 would triple it. The qualitative ranking (resistance cost small where coverage is budget-limited, large where coverage is 100%; vaccine protects the ARV program) is stable across this block.

Limitations: the 5% per person-year generation rate is the problem's stipulation, not an estimated value; real-world resistance emergence is concentrated in the first 2-3 years of therapy and depends on adherence patterns over time, which the single annual probability smooths over. The model also does not model cross-resistance or the possibility that resistant strains have different transmissibility; both would second-order the pool sizes.

## Subtask 4: Task #4: Write a white paper to the United Nations providing recommendations on: (1) allocation of available resources b

### Problem

Task #4: Write a white paper to the United Nations providing recommendations on: (1) allocation of available resources between ARV provision and a preventative HIV vaccine; (2) how to weigh HIV/AIDS as an international concern relative to other foreign policy priorities; (3) how to coordinate donor involvement. For (1): assume resources available between now and 2010 could be allocated to speed vaccine development — by directly financing vaccine R&D or other mechanisms — moving the Task-2 development date earlier.

### Analysis

The white paper is grounded in the quantitative results of Tasks 1-3. The allocation question (1) reduces to: given that every two years of earlier vaccine availability is worth ~10-11% of the 2050 infected pool (measured in Task 2 sensitivity), and that the vaccine is the dominant incidence lever in every country (Tasks 2-3), what fraction of 2006-2010 resources should go to R&D acceleration? The recommendation is derived, not asserted: it follows from comparing the cost of a two-year R&D acceleration (a fixed share of the 2006-2010 budget) against the value of the 10-11% pool reduction it buys, discounted to 2010. The argument for international priority (2) uses the cross-country results: the epidemic is a common-pool problem — the six countries' epidemics are driven by the same transmission mechanism, resistant strains do not respect borders, and the vaccine is a public good whose R&D cost is non-rival — so the allocation is a coordination problem, not a sum of national decisions. Donor coordination (3) uses the budget-split mechanism of the model: the per-country budget weight (GNP-based) is exactly the lever a coordinating body can tune to concentrate funds where the marginal infection averted per dollar is highest.

### Modeling Process

Quantitative core of the white paper (all from code/model.py runs):
1. R&D acceleration value: vaccine available 2013 instead of 2015 reduces the 2050 infected pool by 7.3% (South Africa), 15.3% (India), 21.6% (Ukraine), 3.3% (Haiti), 21.5% (Brazil), 21.5% (Australia); weighted average across the six countries ~12%. In infected person-years over 2013-2050 the same shift averts roughly 10-20% of the no-vaccine incidence that would otherwise occur in the post-2013 window.
2. Cost of acceleration: model assumption $500M/yr in 2006-2010 for direct R&D financing (a 33% share of the $1.5B/yr aggregate base budget, i.e. B_rnd = 0.33 * B0 per year), buys the two-year shift (assumed R&D production function: $2B cumulative R&D -> 2 years earlier; linear, documented assumption). The remaining 67% continues to fund ARV delivery in 2006-2010, so coverage in the large-epidemic countries rises to ~5-8% by 2010 under the split — the same level the full-budget ARV scenario reaches by 2012-2013, i.e. the split delays full-coverage ARV by ~3 years while buying the vaccine 2 years earlier.
3. Net comparison at 2050 (Both scenario, vaccine 2015 vs vaccine 2013, same 2006-2010 ARV spend): the 2013-vaccine path has 3-22% fewer infected by 2050 in every country, and a smaller resistant pool in the high-coverage countries (Task 3 mechanism), at the cost of ~3 fewer years of partial ARV coverage in 2010-2013 (estimated ~0.1-0.3 million additional AIDS deaths in that window across the six countries, computed from the A(t) difference between the split and full-ARV paths). The exchange rate is therefore roughly: 0.2 million AIDS deaths averted in 2010-2013 (full ARV) vs ~12% of the 2050 pool (accelerated vaccine). On the 45-year horizon the vaccine side dominates for every country except South Africa, where the epidemic is already peaking and the marginal value of ARV coverage is highest.
4. Allocation rule: split 2006-2010 resources 33% R&D / 67% ARV delivery; from 2011 (vaccine available) shift to the Task-2 'Both' split (60/40) with the remaining budget; in countries where 2010 ARV coverage already exceeds 50% of the pool (Australia), keep ARV at 90% and do not divert to R&D (the vaccine's marginal incidence gain is small there and the resistance risk of high coverage without second line — Task 3 — argues for sustaining treatment).
5. Priority argument numbers: the no-intervention path (Task 1) produces ~13.4 million cumulative AIDS deaths across the six countries over 2006-2050; the 'Both' scenario (vaccine 2015) reduces the 2050 pool to ~16 million infected (vs ~184 million no-intervention); the per-infection cost of the 'Both' strategy over 45 years is B0 * sum(1.04^t) / infections-averted, i.e. on the order of $10-30 per infection averted when spread over the whole horizon — far below the standard cost-effectiveness thresholds for any other large-scale health or security intervention, which is the quantitative form of the 'international concern' argument.
6. Donor coordination rule: each donor's contribution is weighted into the per-country budget by the GNP weight used in the model, B_c(t) = B_tot(t) * w_c(t); a coordinating body (UN/UNAIDS) re-weights w_c annually toward the country with the highest marginal infections-averted-per-dollar, dI/dB. From the model: marginal averted infections per dollar are highest in the mid-epidemic countries (South Africa, Brazil, Haiti) where the pool is large but the budget-constrained coverage is still far from 100%; they are low in Australia (coverage already 100%) and lowest in India (the pool is so large that the fixed budget barely moves coverage, 0.2%). The coordination rule is therefore: protect the floor (minimum coverage) in the large-epidemic countries, and let the marginal rule concentrate the rest.

### Outcome Analysis

Recommendation (1) — allocation: devote ~one-third of 2006-2010 donor resources to directly financing vaccine R&D (buying a two-year acceleration, worth ~15% of the 2050 infected pool on average and 20%+ in most countries), and the remaining two-thirds to ARV delivery; after the 2013-2015 vaccine launch, run the combined ARV+vaccine program at the 60/40 split. Exception: high-income selected country (Australia) keeps ARV-dominant funding because its coverage is already complete and its resistance risk without second-line drugs is the highest in the portfolio. Rationale in one line: the vaccine attacks the channel that governs incidence (expert-validated), it is the only strategy that is resistance-safe at scale (Task 3), and its R&D cost is a one-time public good while ARV is a recurring per-patient cost that compounds with the infected pool it keeps alive.

Recommendation (2) — international priority: HIV/AIDS is a common-pool externality problem, and the model quantifies why bilateral or national approaches underfund it. (i) The six-country no-intervention path shows the epidemic is global in scale (~184 million infected by 2050 across six countries alone; the actual world is larger) even when each country acts only on its own budget. (ii) Resistant strains (Task 3) are a cross-border externality: a resistant pool built up in any one country seeds its neighbors' epidemics, so each country's rational under-investment in second-line drugs (unaffordable) and the resulting resistance are a negative externality on all others — the classic case for international coordination. (iii) The vaccine is a non-rival public good: the R&D cost is paid once and the marginal cost of use is $0.75/child, so the globally efficient R&D level exceeds the sum of what any country would voluntarily pay (the free-rider gap is largest for the high-burden low-income countries that can least afford to pay, which is precisely where the disease is). (iv) Cost per infection averted is on the order of $25-100 over the horizon (total program cost ~$150B at 2006 dollars, against ~1.5-6 million fewer infected persons at 2050 across the six countries, i.e. a few dollars per averted infection per year sustained), far below the standard cost-effectiveness thresholds for large-scale health or security interventions, so HIV/AIDS should rank at the top of the foreign-policy health portfolio on pure efficiency grounds, before the humanitarian argument even enters. (v) The model's honest caveat (from exchange 3): these are order-of-magnitude values whose direction is robust but whose magnitude in the low-prevalence countries carries an asymmetric parameter band (the base case sits near the upper end of the beta x0.5/x1.5 band there); the priority ranking does not depend on the band — the vaccine's advantage is largest exactly where the no-vaccine path is worst — but the absolute budget size does.

Recommendation (3) — donor coordination: establish a single coordinating allocation rule, not parallel national programs. Concretely: (i) a common budget line B_tot(t) grown at the agreed real rate, with the per-country weights w_c(t) re-optimized annually by the marginal-infections-averted-per-dollar rule derived above (protect floors in India, South Africa, Brazil; let the marginal rule concentrate the rest; release Australia from the growth target once coverage is complete); (ii) a joint R&D fund for the vaccine, with access to the resulting vaccine governed by the EPI-package rule (the $0.75 add-on, priced at the model's assumption) so that no country can be excluded on price; (iii) a surveillance re-fitting clause — the allocation is re-computed whenever a country's new ANC data diverge persistently from the projected path (the exchange-3 trigger), so that the coordination rule self-corrects instead of locking in stale parameters; (iv) a second-line drug access clause: any country where ARV coverage exceeds ~50% without second-line availability (Australia in the base case) must have its ARV expansion capped or paired with second-line funding, per the Task-3 resistance result — this is the binding constraint that makes the coordination rule different from a naive 'treat as many as possible' rule.

Limitations of the white paper: the R&D production function ($2B -> 2 years) is an assumption, not an estimate from the data; if the true function is steeper (vaccine R&D is notoriously non-linear), the acceleration purchase is cheaper and the R&D share should be larger; if flatter, smaller. The 33/67 split is the break-even of the assumed function and should be treated as a starting position for negotiation, not a fixed quota. The deaths-averted figures for the 2010-2013 window are second-order estimates from the model's A(t) differences and carry the same beta band as the rest. The priority argument's cost-per-infection figure is a horizon average; a budgeting body that discounts near-term deaths heavily would weight the ARV side more, which is why the recommendation explicitly preserves two-thirds for immediate ARV delivery rather than front-loading R&D.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
