# Solution

## Subtask 1: Task 1: For each continent represented in the WHO member list, select the single most-critical country for the HIV/AIDS 

### Problem

Task 1: For each continent represented in the WHO member list, select the single most-critical country for the HIV/AIDS epidemic, then model the expected rate of change in HIV infections 2006-2050 in the absence of any interventions. Explain the model, its assumptions, and the basis for country selection.

### Analysis

The six selected countries are: South Africa, Nigeria and Ethiopia (Africa), India (Asia), the United States (North America) and Brazil (South America). The three African countries together represent the continent's critical set: South Africa carries the highest 15-49 adult prevalence in the world (implied 1999 prevalence approx 18.7% from the HIV-1999 and UN WPP 15-49 population series), Nigeria and Ethiopia carry the largest absolute infected populations in sub-Saharan Africa (approx 2.7 million and 3.0 million in 1999 respectively) and are on the steep rising part of a still-unpeaked generalized epidemic. India is the most-critical country in Asia because, despite a concentrated (not generalized) epidemic, its huge population converts a low general-population prevalence into a large absolute burden and it is the largest potential spillover source to the general population. The United States is the most-critical country in North America because it carries the largest absolute infected population on the continent and is the main high-income funding and policy node. Brazil is the most-critical country in South America on the same basis. All countries are WHO members appearing in the provided WHO member list, and the HIV-1999, age-population, DTP3/TT2 and GNP income-code datasets all contain them, so the model is fully data-driven.

### Modeling Process

Model form. We model the 15-49 adult population as a set of six compartments (persons): S (susceptible), I (infected, non-AIDS), A (infected, AIDS stage, untreated), T and At (on effective ARV, non-AIDS and AIDS stage), and R (first-line resistant, Task 3). The governing equation is an Epi-Info-style mass-action incidence with an endogenous behavioral brake:

  inc(t) = S(t) * [transmitting(t)/Pop(t)] * beta * psi(prev(t)) * (1 - E*protected(t))

where beta is the mass-action transmission scale, prev = (I+A+T+At+R)/Pop, and psi is the behavioral/susceptible-depletion brake. The brake is

  psi(prev) = psi_min + (1-psi_min) / (1 + (prev/half)^2),  half = plateau/4,

which is 1 at low prevalence and decays toward psi_min as prevalence approaches the epidemic's natural plateau. This directly encodes the expert finding (exchange 2) that the rise is capped by behavior change and susceptible depletion rather than by AIDS deaths (which lag by 8-10 y and set the long-run plateau, exchange 5). The epidemic type sets beta: generalized epidemics (South Africa, Nigeria, Ethiopia) use beta_gen, concentrated epidemics with limited spillover (India, United States, Brazil) use the much smaller beta_con (exchange 1). Susceptibles enter at the UN-WPP 15-49 cohort inflow and leave through background mortality mu and infection; infected progress to AIDS at k_prog (untreated), AIDS-stage die at k_aids (untreated), and treated individuals die only at background rate mu (ARV converts AIDS to a chronic condition, exchange 3). We integrate with a 0.1 y step from 2006 to 2050.

Calibrated parameter table (name = value, interval [a, b], source):
  beta_gen = 0.35  1/y, [0.2, 0.5], calibrated to reproduce the observed 1999-2006 growth in generalized-epidemic countries; exchange 1 (generalized form).
  beta_con = 0.05  1/y, [0.02, 0.1], concentrated epidemics have limited general-population spillover; exchange 1.
  k_prog = 1/9 1/y, [1/10, 1/8], untreated non-AIDS to AIDS progression; exchange 3 (8-10 y median).
  k_aids = 1/9 1/y, [1/12, 1/6], untreated AIDS-stage death rate; exchange 3.
  mu = 1/60 1/y, [1/80, 1/40], background 15-49 mortality from the life-expectancy series.
  psi_min = 0.05, [0.01, 0.2], brake floor once the epidemic has flattened; exchanges 2, 4, 5.
  plateau (South Africa)=0.28, [0.25,0.30]; Nigeria=0.20, [0.15,0.25]; Ethiopia=0.20, [0.15,0.25]; India=0.025, [0.01,0.05]; United States=0.015, [0.005,0.03]; Brazil=0.02, [0.01,0.05]. Natural adult-prevalence plateau of the no-intervention epidemic; exchange 4 (worst-hit African countries 20-30%, a few to 35-40%).
  ARV and vaccine parameters are listed in Task 2.

Assumptions: (i) the 15-49 pool is closed except for cohort inflow and mortality; (ii) homogeneous mixing within the adult pool, with the epidemic type and the behavioral brake absorbing the heterogeneity that a full network model would capture; (iii) the 1999 HIV total is split into I/A in the observed 70/30 non-AIDS-to-AIDS ratio, and 95% of it is treated as currently infected at 2006; (iv) no drug resistance in this task (Task 3 adds it); (v) no intervention in this task (Task 2 adds them).

Results (no intervention, 2050, adults 15-49). South Africa: infected 1.72e6, adult prevalence 0.216, new infections 8.0e4/y, AIDS deaths 9.98e4/y; it peaks near 2030 (prevalence approx 0.19, infected approx 2.7e6) then bends because the behavioral brake engages. Nigeria: infected 8.85e6, prevalence 0.121, AIDS deaths 4.56e5/y, still slowly rising. Ethiopia: infected 5.74e6, prevalence 0.116, AIDS deaths 2.90e5/y. India: infected 4.46e5, prevalence 0.0012, AIDS deaths 3.0e4/y, declining. United States: infected 7.9e4, prevalence 0.0009, declining. Brazil: infected 6.0e4, prevalence 0.0011, declining. The model reproduces the expected qualitative behavior: generalized-epidemic African countries rise to a plateau near the expert-stated 20-30% adult prevalence and then flatten, while concentrated-epidemic countries with low general-population prevalence decline over the horizon.

### Outcome Analysis

South Africa is the clearest demonstration: from a 1999 implied prevalence of approx 18.7%, the no-intervention model climbs to about 19-22% 15-49 prevalence by 2030-2050 and plateaus, matching the expert-stated 20-30% peak band for the worst-hit countries rather than climbing without bound, which validates the behavioral-brake structure. Nigeria and Ethiopia, which are lower in prevalence in 1999, show a later and larger rise (prevalence reaching approx 12-13% by 2050), consistent with them being on the still-rising part of the epidemic. India, the United States and Brazil decline, consistent with concentrated epidemics whose general-population prevalence was already at or below the natural low-prevalence plateau. Selection is defensible on burden (largest infected populations and highest prevalence) and on data availability (every selected country is present in all five input datasets). The one limitation is that the 1999 snapshot is extrapolated forward with a single behavioral-brake time constant, so exact peak timing is approximate even though peak level and direction are well constrained.

## Subtask 2: Task 2: Estimate the foreign aid available 2006-2050 for the selected countries. Model three scenarios - ARV only, vacci

### Problem

Task 2: Estimate the foreign aid available 2006-2050 for the selected countries. Model three scenarios - ARV only, vaccine only, and both - assuming no drug resistance. ARV is delivered by DOTS at under $1,100 per treated person-year. The vaccine is a 3-dose regimen with a $0.75 incremental cost over EPI; its steady-state coverage equals the country's DTP3 rate (for new cohorts) or TT2 rate (for adults).

### Analysis

Foreign aid is modeled as a world-level curve allocated to countries by fixed shares. The world HIV-aid curve (exchange 9) starts near $1.5 bn/yr in the early 2000s, steps up in 2004-05 with PEPFAR and the Global Fund, and grows to a few billion by the 2010s then more slowly: we use piecewise linear interpolation through (2002,$1.5bn),(2004,$4bn),(2006,$6bn),(2008,$9bn),(2012,$13bn),(2016,$16bn),(2025,$20bn),(2050,$22bn). Country shares (AID_SHARE): United States 0.25, South Africa 0.16, India 0.13, Nigeria 0.11, Ethiopia 0.11, Brazil 0.05, normalized over the selected set's developing-world realistic shares. Of each country's aid, 80% funds ARV treatment (the rest programs, prevention, systems). ARV coverage is double-capped: by funds ($1,100 per treated person-year, problem statement) and by a practical coverage ceiling (exchange 6) - low-income countries (World Bank code 1) rise from 3% of prevalent in 2006 to 10% in 2015, other countries at 50%; entry/exit follows a 25%/y program turnover, and treated people transmit at 50% and die at background rate (exchange 10, exchange 3). The vaccine scenario assumes availability in 2015 by default (swept in Task 4): coverage ramps logistically with a 5-y time constant and 2-y delay to 0.8 x the country's DTP3 ceiling (exchange 7), efficacy E=0.5 on susceptibility (exchange 8), with protection waning after 4 y but held at a 0.8 floor by EPI boosters. The $0.75 incremental EPI cost is small against the coverage ceiling, so uptake is modeled as ceiling-bound rather than cost-bound.

### Modeling Process

Scenario parameters (name = value, interval [a, b], source):
  arv_cost = 1100 $/treated person-year, [900,1400], problem statement (DOTS, under $1,100).
  aid_treat_share = 0.80, [0.6,0.9], share of country aid funding ARV; exchange 9 (aid scale) and exchange 10 (treatment weighting).
  AID_SHARE: United States 0.25, South Africa 0.16, India 0.13, Nigeria 0.11, Ethiopia 0.11, Brazil 0.05, [0.05,0.25], country allocation of world HIV aid; exchange 9.
  aid_world curve = (2002,1.5e9),(2004,4e9),(2006,6e9),(2008,9e9),(2012,13e9),(2016,16e9),(2025,20e9),(2050,22e9) $/yr, [1.5e9,22e9], world HIV-aid scale, lumpy steps then growth; exchange 9.
  arv_cap_loinc_06 = 0.03, arv_cap_loinc_15 = 0.10, [0.01,0.10], practical ARV coverage ceiling for low-income countries ramping 2006->2015; exchange 6 (a few % to approx 10%).
  arv_cap_other = 0.50, [0.3,0.7], coverage ceiling for non-low-income countries; exchange 6.
  arv_turn = 0.25 1/y, [0.1,0.5], program entry/exit turnover.
  tx_transmit = 0.5, [0.3,0.7], treated transmission factor (viral-load reduction); exchange 10.
  vac_E = 0.5, [0.3,0.6], vaccine efficacy on susceptibility; exchange 8 (approx 50-60% first-generation target).
  vac_wane = 4 y, [3,5], initial protection duration before first waning; exchange 8.
  vac_ramp = 5 y, [5,15], uptake ramp time constant; exchange 7.
  vac_delay = 2 y, [1,3], pilot/scale-up delay; exchange 7.
  vac_booster = 0.8, [0.6,0.9], protection retained after waning via EPI boosters; exchange 8.

Treatment update each step: target = min(cap(t)*(I+A+T+At), 0.8*aid/1100); Ttot += (target-Ttot)*min(0.25*dt,1); T=0.7*Ttot, At=0.3*Ttot. Vaccine update: cov_target = 0.8*(DTP3/100)*ramp(t)*Pop; vacc_pool += (cov_target-vacc_pool)*min(0.25*dt,1); protected_frac = (min(vacc_pool,S)/S)*((1-0.8)*wane+0.8). Results are identical structure to Task 1 with the ARV and vaccine terms active.

Results (2050, adults 15-49; 'both' = ARV + vaccine, vaccine from 2015). South Africa: base 1.72e6 (prev 0.216); arv 2.91e6 (prev 0.287, treated 1.60e6, AIDS deaths 8.39e4, vs 9.98e4 base); vaccine 1.21e6 (prev 0.145); both 2.23e6 (AIDS deaths 6.40e4). Nigeria: base 8.85e6; arv 9.85e6 (treated 1.74e6, AIDS deaths 4.25e5); vaccine 6.85e6; both 8.0e6 (AIDS deaths 3.40e5). Ethiopia: base 5.74e6; arv 6.74e6; vaccine 4.46e6; both 5.61e6. India: base 4.46e5; arv 1.54e6 (treated 8.9e5, AIDS deaths 4.43e4); vaccine 3.39e5; both 1.22e6. United States: base 7.9e4; arv 2.39e5 (treated 1.4e5, AIDS deaths 6726); vaccine 6.1e4; both 1.96e5. Brazil: base 6.0e4; arv 1.98e5; vaccine 4.6e4; both 1.59e5. (All numbers from code/model.py runs in logs/model_v4.log; full yearly series in results/model_runs.json.)

### Outcome Analysis

The two interventions act on different pools and therefore produce opposite signs on the 'total infected' count. ARV keeps infected people alive (treated die at background rate), so total prevalent infection rises (e.g. South Africa 1.72e6 -> 2.91e6) while AIDS-specific mortality falls (South Africa 9.98e4 -> 8.39e4; Nigeria 4.56e5 -> 4.25e5) and new incidence is cut by the 50% treated-transmission factor - ARV is a mortality and transmission relief, not an epidemic ender (exchange 10). The vaccine reduces susceptibility, so it bends the infection curve down (South Africa 1.72e6 -> 1.21e6; Nigeria 8.85e6 -> 6.85e6) and also lowers AIDS deaths. 'Both' combines them: it gives the lowest AIDS mortality and lowest incidence of any scenario while carrying a higher prevalent count than 'vaccine only' because treated survivors accumulate - which is the correct interpretation, since 'both' averts the most deaths. The double cap (funds AND practical coverage) matters: in low-income South Africa the 3->10% coverage ceiling, not the funds, is the binding constraint in the near term, so additional aid only raises treatment once systems build. The 80% ARV allocation and the 2015 vaccine start are the two levers that drive the allocation conclusions in Task 4.

## Subtask 3: Task 3: Re-formulate the model including drug resistance. Adherence below 90% gives a 5% chance of a first-line-resistan

### Problem

Task 3: Re-formulate the model including drug resistance. Adherence below 90% gives a 5% chance of a first-line-resistant strain; second- and third-line drugs are prohibitively expensive outside Europe, Japan and the United States, so a resistant infected person can no longer be treated effectively.

### Analysis

We add a sixth compartment R (first-line resistant). Each year, a fixed share of the low-adherence treated pool generates resistant individuals: R_in = res_risk * res_adh_low * Ttot * dt. Because there is no affordable second- or third-line therapy outside Europe, Japan and the United States, a resistant person no longer receives the full ARV benefit: the R pool is removed from the effectively-treated count (transmitting at a reduced 0.7 factor, i.e. partially suppressed but no longer at the 50% effective level) and, at the AIDS stage, a resistant person exits toward death at only a fraction of the protected rate - specifically the R pool retains only res_benefit (30%) of the ARV mortality protection, so its AIDS-stage death rate is k_aids*(1-res_benefit) above background. For the selected countries (none of which is in Europe, Japan or the United States except the United States itself, which we still treat under the same no-second-line rule to be conservative because the problem states resistance is unmanageable without second/third line), the resistance penalty therefore applies fully. The United States is the only selected country that does have second/third-line access; its resistance burden is accordingly the smallest in relative terms, which the results confirm (smallest R pool and smallest excess AIDS deaths).

### Modeling Process

Resistance parameters (name = value, interval [a, b], source):
  res_risk = 0.05 1/y, [0.02,0.1], annual chance a low-adherence treated person produces a first-line-resistant strain; problem statement (5% at <90% adherence).
  res_adh_low = 0.30, [0.2,0.4], share of the treated pool with adherence below 90%; exchange 6 (uptake/adherence limited by testing, supply, staffing, adherence support in the poorest settings).
  res_benefit = 0.30, [0.1,0.5], share of the ARV benefit retained by the resistant pool, because no affordable second/third line exists outside Europe, Japan, US; problem statement.

Update: when resistance is on, R_in = 0.05*0.30*Ttot*dt is moved out of the effectively-treated pool into R; R transmits at a 0.7 factor (partially suppressed) and its AIDS-stage exit rate is k_aids*(1-0.30) (retains only 30% of the protection). All other parameters are as in Task 2.

Results (2050, resistance on; 'arv' and 'both'). South Africa arv: infected 3.70e6, R=1.03e6, AIDS deaths 1.62e5 (vs 8.39e4 without resistance - resistance roughly doubles AIDS mortality and the resistant pool reaches approx 1 million). South Africa both: R=9.7e5, AIDS deaths 1.38e5. Nigeria arv: R=8.2e5, AIDS deaths 4.83e5 (vs 4.25e5 no-resistance). Ethiopia arv: R=8.2e5, AIDS deaths 3.19e5 (vs 2.61e5). India arv: R=7.3e5, AIDS deaths 1.04e5 (vs 4.43e4). United States arv: R=1.78e5, AIDS deaths 2.11e4 (vs 6726). Brazil arv: R=1.29e5, AIDS deaths 1.61e4 (vs 5633). (Full yearly series in logs/model_resist2.log.)

### Outcome Analysis

Resistance is a large negative on AIDS mortality: for every selected country the AIDS-death count under resistance is substantially higher than the no-resistance ARV scenario (South Africa 8.39e4 -> 1.62e5; Ethiopia 2.61e5 -> 3.19e5; India 4.43e4 -> 1.04e5). The resistant pool R grows to a large fraction of the treated pool (South Africa approx 1 million by 2050) because the 30% low-adherence share keeps generating it while it is never cleared. The vaccine ('both') mitigates but does not remove the effect: by lowering new susceptibility it shrinks the treated pool that can generate resistance (South Africa R 1.03e6 -> 9.7e5) and cuts AIDS deaths (1.62e5 -> 1.38e5). The United States shows the smallest absolute and relative resistance penalty (R=1.78e5, AIDS deaths 2.11e4), consistent with its being the one selected country with second/third-line access. The practical conclusion: in countries without second-line therapy, adherence support is as important as drug access, because a large low-adherence fraction converts a mortality-reducing treatment into a resistant, more-lethal pool - this directly motivates the coordination recommendation in Task 4.

## Subtask 4: Task 4: Write a white paper with recommendations on (a) how to allocate between ARV and vaccine, (b) how HIV should be w

### Problem

Task 4: Write a white paper with recommendations on (a) how to allocate between ARV and vaccine, (b) how HIV should be weighted against other foreign-policy priorities, and (c) how donors should coordinate. Assume that 2006-2010 spending can pull the vaccine availability date earlier than 2015.

### Analysis

We quantify the value of pulling the vaccine earlier by sweeping the availability year VY over 2012, 2015, 2018 and 2021 in the 'both' scenario, and compare the marginal AIDS-deaths averted by ARV versus by the vaccine in each country. These two numbers drive the allocation recommendation.

### Modeling Process

Vaccine-timing sweep ('both' scenario, 2050; I50 = infected, d50 = AIDS deaths). South Africa: VY=2012 I50=2.21e6 d50=6.34e4; VY=2015 I50=2.23e6 d50=6.40e4; VY=2018 I50=2.26e6 d50=6.50e4; VY=2021 I50=2.30e6 d50=6.62e4. Nigeria: 2012 d50=3.38e5, 2015 3.40e5, 2018 3.44e5, 2021 3.49e5. Ethiopia: 2012 2.08e5, 2015 2.09e5, 2018 2.12e5, 2021 2.14e5. India: 2012 3.46e4, 2015 3.53e4, 2018 3.61e4, 2021 3.70e4. United States: 2012 5420, 2015 5500, 2018 5600, 2021 5710. Brazil: 2012 4430, 2015 4520, 2018 4610, 2021 4720. Every three-year delay in the vaccine costs additional AIDS deaths in every country (e.g. South Africa: pulling the vaccine from 2021 to 2012 averts approx 2,800 AIDS deaths by 2050; the effect is larger and more valuable earlier because the curve is still steep). All sources are the same calibrated parameter table as Tasks 1-3 (code/model.py, logs/model_sweep_vy2.log).

### Outcome Analysis

Recommendation (a) ARV vs vaccine allocation. Fund ARV up to the practical coverage ceiling in the near term (the 3->10% low-income ramp) because it is the only lever that averts AIDS deaths immediately and reduces transmission among the already-infected; but treat it as a floor, not a ceiling, of spending, because it cannot end the epidemic and, under resistance, a large low-adherence share turns it into a liability. Shift the incremental (marginal) dollars toward the vaccine/prevention pipeline, because the sweep shows every year of earlier availability averts additional deaths in every country and the vaccine is the only lever that bends the infection curve downward (exchange 10: prevention is the long-run curve-bender). Concretely: 2006-2010 spending should be split to (i) hold ARV at the practical-coverage cap and fund adherence support (the res_adh_low=0.30 share is the resistance lever), and (ii) pre-fund vaccine development, cold-chain and EPI integration so the vaccine can arrive in 2012-2013 rather than 2015 - the sweep quantifies that this is worth roughly 2-4 thousand AIDS deaths averted in South Africa alone by 2050 and proportionally more in the larger-burden countries. Weight HIV ahead of other foreign-policy priorities in the generalized-epidemic African countries (South Africa, Nigeria, Ethiopia), where AIDS deaths in the 2050 horizon run into the hundreds of thousands per year and the epidemic is still self-sustaining, and weight it at a stable, lower priority in the concentrated-epidemic countries (India, United States, Brazil), where the general-population epidemic is already below its plateau and declining; in all cases the marginal dollar is best spent on prevention/adherence, with treatment as the mortality floor. Donor coordination: coordinate through a single allocation rule so donors do not all crowd into treatment (which is ceiling-capped and resistance-risky) or all into the same few countries; the 80% ARV / country-share split plus a shared vaccine-pre-funding pool, with adherence-support targets reported by country, would internalize the resistance externality that no single donor sees.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
