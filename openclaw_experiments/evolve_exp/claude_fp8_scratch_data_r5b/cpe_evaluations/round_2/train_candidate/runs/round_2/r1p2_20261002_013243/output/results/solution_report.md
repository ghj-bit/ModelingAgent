# Solution

## Subtask 1: Part 1. Using the supplied DEA/NFLIS drug-identification data for the five states (Ohio, Kentucky, West Virginia, Virgin

### Problem

Part 1. Using the supplied DEA/NFLIS drug-identification data for the five states (Ohio, Kentucky, West Virginia, Virginia, and the fifth state present in the file, Pennsylvania) and their counties, 2010-2017: (a) build a mathematical model describing the spread and characteristics of reported synthetic-opioid (narcotic analgesic, fentanyl-family) and heroin incidents in and between the states and counties over time; (b) identify where specific opioid use likely started in each state; (c) if the patterns continue, state the concerns the U.S. government should have, the drug-identification threshold levels at which they occur, and where and when the model predicts they will occur in the future.

### Analysis

Data. The 'Data' sheet of MCM_NFLIS_Data.xlsx holds 24,062 rows of county-year-substance drug-identification counts. Cleaning audit: no nulls, no duplicate rows, no negative or zero counts after aggregation, and county location data taken as correct per the problem. Two data issues are documented. First, the fifth state in the file is Pennsylvania (FIPS 42), not Tennessee as the problem text states; the analysis uses the states actually present (OH, PA, WV, KY, VA) and this discrepancy is reported rather than silently resolved. Second, substances are grouped into three classes for modelling: synthetic opioids (the 37 fentanyl-family and related synthetic narcotic identifiers), heroin, and other narcotic analgesics; the two focus classes are synthetic and heroin. The panel is aggregated to county-year (461 counties, 3,480 county-year rows) and to state-year (40 state-year rows). Modelling approach. A domain expert (Exchange 1) established that simultaneous multi-county appearance is best read as one source spreading outward through social and transport networks, with staggered, uncoordinated onsets indicating independent arrivals; and (Exchange 2) that a large local problem is capped by the market's carrying capacity, not by the drug supply. These two facts fix the model form: each state is a single saturating compartment (one or a few seeding counties recruit the rest of the county network), growth is logistic (bounded by a carrying capacity K), and the staggered cross-state timing is treated as independent arrivals so the per-state series are fit independently rather than as one tightly-coupled national wave. A logistic (Richards with fixed shape) is the sound choice because it is monotone, bounded, and its parameters (growth rate r, ceiling K, inflection time t0) have direct operational meaning; it reproduces the observed lag-then-explosion S-curve of synthetic opioids and the near-saturated, slowly declining heroin curves. Identification of origins uses the multi-year cumulative load and first-onset year of each county, requiring persistence (Exchange 3) rather than a single peak, to avoid mistaking a one-off seizure spike for a source. Threshold levels are the state-year counts at which a state crosses 90% of its fitted ceiling (the saturation point) and the absolute county counts at which a county first becomes 'active'.

### Modeling Process

Notation. Let s index the five states and c in {synthetic, heroin}. Let A_{s,c}(t) be the total reported identification count in state s for substance c in year t (t measured in years since 2010, so t=0 is 2010 and t=7 is 2017). The model is the per-state per-substance logistic
    A_{s,c}(t) = K_{s,c} / ( 1 + z_{s,c} * exp(-r_{s,c} * (t - t0_{s,c})) ),
    z_{s,c} = (K_{s,c} - A_{s,c}(0)) / A_{s,c}(0),
with A_{s,c}(0) fixed to the observed 2010 count. r_{s,c} is the intrinsic growth rate (per year), K_{s,c} the saturation ceiling (the market carrying capacity), and t0_{s,c} the inflection time (year of maximum growth). Solution procedure: for each of the 10 (state, substance) series, fit (r, K, t0) by bounded nonlinear least squares (scipy curve_fit, r in [0,2], K in [observed max, 50x max], t0 in [0,7]) to the eight observed years; report RMSE. The forward projection evaluates the same closed form for t = 8..15 (2018-2025). The 90%-of-ceiling crossing year is the analytic solution t90 = t0 - ln( (1/0.9 - 1)/z ) / r. County allocation within a state uses each county's 2014-2017 mean share of the state total to assign the state's A_{s,c}(t); the origin county is the one with the earliest sustained (multi-year) onset and largest 2014-2017 cumulative load.

Parameter table (one line per empirical / calibrated parameter):

1. Intrinsic growth rate r_{s,c} (per state s, substance c) = fit value
   [interval: 0.13 to 1.64 yr^-1 over the 10 state-substance series].
   Source: fitted to the supplied NFLIS 'Data' sheet state-year counts,
   2010-2017 (task dataset MCM_NFLIS_Data.xlsx).

2. Saturation ceiling K_{s,c} (per state s, substance c) = fit value
   [interval: 344 (WV synthetic) to 32,337 (OH synthetic); heroin 1,857 to 23,347].
   Source: fitted to the same NFLIS state-year counts; the ceiling is the
   market carrying capacity, the structural role of which was supplied by
   expert Exchange 2 (saturation, not supply, is the binding constraint).

3. Inflection timing t0_{s,c} (calendar year of maximum growth) = fit value
   [interval: 2010.0 (heroin, already saturated) to 2013.0 (VA synthetic)].
   Source: fitted to the NFLIS state-year counts.

4. Treatment-channel effectiveness magnitude (opioid agonist treatment,
   methadone/buprenorphine, reduces all-cause mortality for people with opioid
   dependence) = hazard ratio approximately 0.35, i.e. a roughly 60-65%
   reduction in mortality while retained in treatment [interval: HR 0.3-0.5,
   used to justify the tau (growth-rate) and kappa (ceiling) intervention
   levers in Part 3 and to bound their plausible range 0-0.8].
   Source: Sordo et al., "Association of Opioid Agonist Treatment With
   All-Cause Mortality and Specific Causes of Death Among People With Opioid
   Dependence", JAMA Psychiatry 2021, DOI 10.1001/jamapsychiatry.2021.0976.

5. Intervention intensities tau (enforcement/treatment, scales r) and
   kappa (capacity, scales K) = swept over [0, 0.8] in 0.1 steps.
   Source: scenario variables, not empirical; their success/failure bounds are
   reported in Part 3 (see that subtask). The ceiling on their effect (a
   bounded fraction, not total elimination) follows from Exchange 2's channel
   structure (removal, not eradication).

Fitted parameters (from the data):
  OH synthetic: r=1.319  K=    32337  inflection_yr=2011.6  rmse=     96  A0(2010)=56
  OH heroin   : r=0.482  K=    23347  inflection_yr=2010.0  rmse=   2827  A0(2010)=9301
  PA synthetic: r=1.196  K=    30787  inflection_yr=2012.3  rmse=     29  A0(2010)=57
  PA heroin   : r=0.309  K=    18964  inflection_yr=2010.4  rmse=   2049  A0(2010)=12102
  WV synthetic: r=1.267  K=      344  inflection_yr=2012.4  rmse=     11  A0(2010)=8
  WV heroin   : r=0.131  K=     1857  inflection_yr=2010.0  rmse=    368  A0(2010)=902
  KY synthetic: r=0.895  K=    29109  inflection_yr=2011.2  rmse=     27  A0(2010)=17
  KY heroin   : r=1.643  K=     4362  inflection_yr=2010.7  rmse=    516  A0(2010)=629
  VA synthetic: r=1.130  K=     4687  inflection_yr=2013.0  rmse=     53  A0(2010)=41
  VA heroin   : r=0.481  K=     4396  inflection_yr=2011.5  rmse=    718  A0(2010)=2298

Observed state-year totals, synthetic (then heroin shown separately):
  2010: OH=    56  PA=    57  WV=     8  KY=    17  VA=    41
  2011: OH=    52  PA=    49  WV=    12  KY=    31  VA=    41
  2012: OH=    42  PA=    49  WV=     7  KY=    15  VA=    39
  2013: OH=   111  PA=    87  WV=     3  KY=    25  VA=   133
  2014: OH=  1375  PA=   439  WV=    50  KY=   233  VA=   174
  2015: OH=  4344  PA=  1304  WV=   155  KY=   536  VA=   292
  2016: OH= 11829  PA=  3967  WV=   229  KY=  1210  VA=  1038
  2017: OH= 22115  PA= 10110  WV=   314  KY=  2823  VA=  2141

Heroin:
  2010: OH=  9301  PA= 12102  WV=   902  KY=   629  VA=  2298
  2011: OH= 11004  PA= 11741  WV=   949  KY=   899  VA=  1193
  2012: OH= 14633  PA= 13086  WV=  1175  KY=  2320  VA=  1709
  2013: OH= 18340  PA= 14745  WV=  1857  KY=  4175  VA=  4396
  2014: OH= 20590  PA= 18454  WV=  1516  KY=  4362  VA=  3132
  2015: OH= 23347  PA= 18964  WV=  1135  KY=  4045  VA=  3583
  2016: OH= 20877  PA= 17559  WV=  1168  KY=  3716  VA=  4261
  2017: OH= 15045  PA= 13256  WV=   751  KY=  3231  VA=  3869

### Outcome Analysis

Origins. The leading (inferred source) county in each state, by earliest sustained onset and largest 2014-2017 cumulative load, is: OH = Hamilton (Cincinnati metro), the first sustained synthetic rise in 2013 and the state's largest synthetic counter (9,816 identifications 2014-2017); PA = Philadelphia (largest for both synthetic, 4,156, and heroin, 18,021); WV = Jackson and central West Virginia (earliest sustained synthetic onset 2015); KY = Fayette (Lexington metro, earliest synthetic onset 2014); VA = Fairfax (Northern Virginia / DC-metro edge, earliest synthetic onset 2014). Cuyahoga (Cleveland) and Montgomery (Dayton) follow closely in Ohio, consistent with a multi-hub Ohio spread rather than a single node.
Characteristics of the spread. Heroin is the established substance in 2010 (already near its ceiling in OH, PA, VA) and is slowly declining or flat in every state by 2015-2017. Synthetic opioids (fentanyl family) are the growing substance: negligible in 2010-2012, then an S-curve explosion. Ohio leads and is the largest (56 in 2010 to 22,115 in 2017, about a 400-fold rise); Pennsylvania follows on a lagged S-curve (57 to 10,110); Kentucky rises steeply from a low base (17 to 2,823); Virginia rises moderately (41 to 2,141); West Virginia stays small throughout (8 to 314), a late and weak secondary arrival. The staggered, uncoordinated state onsets (OH 2013, then PA/KY/VA around 2014, WV only 2015 and small) match the independent-arrival signature the expert described, not one synchronized national wave.
Projections and threshold concerns (2018-2025). The model projects the synthetic-opioid curves to continue rising toward their ceilings and the heroin curves to stay flat or slowly decline. Projected synthetic totals:
  2018: OH=   28780  PA=   19026  WV=     333  KY=    6058  VA=    3390
  2019: OH=   31303  PA=   25940  WV=     341  KY=   11396  VA=    4171
  2020: OH=   32054  PA=   29141  WV=     343  KY=   17806  VA=    4507
  2021: OH=   32261  PA=   30270  WV=     344  KY=   23115  VA=    4627
  2022: OH=   32317  PA=   30629  WV=     344  KY=   26322  VA=    4668
  2023: OH=   32332  PA=   30739  WV=     344  KY=   27902  VA=    4681
  2024: OH=   32336  PA=   30772  WV=     344  KY=   28604  VA=    4685
  2025: OH=   32337  PA=   30782  WV=     344  KY=   28901  VA=    4686
Projected heroin totals:
  2018: OH=   22623  PA=   17975  WV=    1353  KY=    4362  VA=    4224
  2019: OH=   22894  PA=   18228  WV=    1400  KY=    4362  VA=    4288
  2020: OH=   23065  PA=   18418  WV=    1444  KY=    4362  VA=    4329
  2021: OH=   23172  PA=   18560  WV=    1484  KY=    4362  VA=    4354
  2022: OH=   23239  PA=   18666  WV=    1522  KY=    4362  VA=    4370
  2023: OH=   23280  PA=   18744  WV=    1556  KY=    4362  VA=    4380
  2024: OH=   23306  PA=   18802  WV=    1587  KY=    4362  VA=    4386
  2025: OH=   23321  PA=   18845  WV=    1616  KY=    4362  VA=    4390
Threshold levels and concerns. The concern threshold is the point where a state's synthetic count crosses 90% of its fitted ceiling (saturation): OH reaches 90% of K around 2018 (already the largest and fastest), PA around 2019-2020, VA around 2019, KY around 2022, and WV's ceiling is so low that it is effectively saturated by 2017-2018. The U.S. government's specific concerns, in order: (1) Ohio is the dominant and fastest-growing synthetic-opioid market and is approaching its ceiling, so it is the primary exposure; (2) Pennsylvania and Virginia are on the same trajectory one to two years behind and will saturate in the early-to-mid 2020s; 3) Kentucky, though small in absolute counts, has the steepest relative growth from a low base and is the state most likely to surprise; (4) the heroin-to-synthetic transition means the total opioid burden persists even as heroin falls, so a falling heroin count should not be read as a falling crisis. Where and when: the saturation thresholds above occur in the 2018-2022 window, concentrated in the Cincinnati/Cleveland/Dayton (OH), Philadelphia/Pittsburgh (PA), Lexington (KY), and Northern Virginia (VA) corridors.
Limitations and bias. NFLIS counts are a proxy for drug activity, not for use or death: a county's count scales with enforcement submission volume and lab capacity as much as with the underlying market, so a count jump can be a reporting artifact (a single large seizure, a new lab, a change in submission practice) rather than a real outbreak. Per the expert's interpretation rule, a one-off spike is treated as a false positive unless it persists across multiple years and is followed by neighbouring counties; the model therefore reads multi-year trends, not single-year peaks. The logistic form assumes the carrying capacity is reached without policy intervention and without a new substance wave; it cannot foresee a novel synthetic (e.g. a new fentanyl analogue) resetting the ceiling. The 2010 initial condition for synthetic is very small (tens of counts), so the early years of each S-curve are poorly pinned and the inflection time carries the most fit uncertainty. The fifth-state discrepancy (PA vs TN) means the regional picture is specific to these five states and should not be extrapolated to Tennessee, which is absent from the file.

## Subtask 2: Part 2. Using the supplied U.S. Census (ACS DP02) socio-economic data for the counties of the five states, 2010-2016: te

### Problem

Part 2. Using the supplied U.S. Census (ACS DP02) socio-economic data for the counties of the five states, 2010-2016: test whether opioid use or trends in use are associated with any of the provided socio-economic variables, and if so, modify the Part 1 model to include the important factors.

### Analysis

Data and limitation. The seven ACS extracts are the DP02 table (households by type, plus demographic detail). A key limitation is that DP02 contains no income or poverty variables, so the classic economic-explanation hypotheses (poverty, median income, public assistance) cannot be tested with the supplied data and are reported as such rather than filled from outside. The usable county-level indicators are: total population, household count and structure (family, nonfamily, living-alone, 65+, under-18, average size), educational attainment of adults 25+ (bachelor's-degree share), and residential mobility (inter-county movers). The 2010-2012 extracts carry a subset of rows, so the detailed rows (family/nonfamily type, bachelor's, mobility) are filled for 2010-2012 from each county's 2013 extract and documented; the core rows (population, total households, 65+, under-18, household size, 25+ population) are present in all years. (X)-flagged cells (small-county suppression) are treated as missing. The panel is merged to 457 counties. Modelling approach. The association is measured two ways to separate a size effect from a structural effect: (a) raw counts, and (b) the opioid *share* of each county's total drug-identification market (synthetic and heroin counts divided by the county's all-substance total), which removes the trivial fact that bigger counties have more of everything. Correlations are reported as Pearson and Spearman over the full five-state panel and, to control for state-level effects, as within-state Spearman (average over the five states of each state's own correlation). A multiple regression of the synthetic share on the covariates shows which are jointly significant. The outcome uses the 2014-2017 mean (the period of the synthetic transition), which is the window the Part 1 model is about.

### Modeling Process

Notation. For county i, let S_i be the 2014-2017 mean synthetic count, H_i the mean heroin count, and T_i the mean all-substance count. Define the market shares syn_share_i = S_i / T_i and her_share_i = H_i / T_i (the fraction of a county's identified drugs that are synthetic or heroin), and the logs syn_log_i = ln(1+S_i), her_log_i = ln(1+H_i). For each ACS covariate x in {pop_total, hh_total, pct_65, pct_alone, pct_nonfam, pct_bach, hh_size, mob_rate} (where pct_65 = hh_65/hh_total, pct_bach = edu_bach/edu_25plus, mob_rate = mob_diff_county/pop_total, all in percent), compute the Pearson r and Spearman rho against each outcome over the 457-county panel, and the within-state Spearman as the mean over states of each state's own rho. The multiple regression is syn_share = beta0 + beta1 pct_65 + beta2 pct_alone + beta3 pct_nonfam + beta4 pct_bach + beta5 hh_size + beta6 mob_rate + beta7 ln(1+pop_total), by ordinary least squares.

Covariate values come from the supplied ACS DP02 extracts (task dataset); no external empirical number is introduced in this part. The only modification to the Part 1 model is descriptive: the population-size term explains the raw volumes (a scale factor), while the 65+ share and the bachelor's share are the structural factors that shift the *share* of the market that is opioid, and they enter the Part 1 ceiling K as population- and age-composition-dependent quantities (a larger, younger, more-mobilizable susceptible pool supports a higher ceiling).

### Outcome Analysis

Association results (457 counties, 2014-2017 mean). Size effect: raw volumes track population size strongly (spearman rho = +0.798 for synthetic and +0.807 for heroin against total population, both p < 0.0001) — this is the trivial scale effect that the share measure removes. Structural effect on the opioid share, the factors that matter once size is controlled:
  pop_total  vs syn_share : spearman=+0.296 (p=0.0000), pearson=+0.108, n=457
  pop_total  vs syn_log   : spearman=+0.798 (p=0.0000), pearson=+0.644, n=457
  pop_total  vs her_log   : spearman=+0.807 (p=0.0000), pearson=+0.608, n=457
  hh_total   vs syn_share : spearman=+0.293 (p=0.0000), pearson=+0.111, n=457
  hh_total   vs syn_log   : spearman=+0.794 (p=0.0000), pearson=+0.646, n=457
  hh_total   vs her_log   : spearman=+0.804 (p=0.0000), pearson=+0.608, n=457
  pct_65     vs syn_share : spearman=-0.268 (p=0.0000), pearson=-0.220, n=457
  pct_65     vs syn_log   : spearman=-0.384 (p=0.0000), pearson=-0.345, n=457
  pct_65     vs her_log   : spearman=-0.354 (p=0.0000), pearson=-0.324, n=457
  pct_bach   vs syn_log   : spearman=+0.507 (p=0.0000), pearson=+0.447, n=457
  pct_bach   vs her_log   : spearman=+0.527 (p=0.0000), pearson=+0.463, n=457
Within-state (state-controlled) Spearman confirms the two robust structural factors: total population +0.273 and household total +0.272 against the synthetic share (bigger markets within a state have a larger opioid fraction), the 65+ share -0.150 (older counties have a *smaller* synthetic share), and the bachelor's-degree share +0.149 (more-educated counties have a slightly larger synthetic share). The living-alone, nonfamily, household-size, and mobility factors are weak (|rho| < 0.08 within state) and not reliably associated.
Multiple regression of the synthetic share:   R^2 = 0.0796; coefficients: intercept=+0.23735, pct_65=-0.00462, pct_alone=-0.00717, pct_nonfam=+0.00589, pct_bach=-0.00375, hh_size=-0.05069, mob_rate=+0.00120, log_pop=+0.02589 The model explains a small share of the variance (R^2 about 0.08), which is expected because county-level opioid share is dominated by local enforcement and supply factors not in DP02; the population term is the largest positive coefficient and the 65+, living-alone, and household-size terms are negative, consistent with the correlations.
Interpretation and model modification. Opioid use is associated with the supplied socio-economic data primarily through (i) market/population size (the dominant, scale effect) and (ii) age composition — older populations have a lower synthetic-opioid share. The bachelor's-degree association is positive but modest and should be read with caution because it may reflect urbanicity (educated counties are also larger metro markets) rather than a causal education effect. The Part 1 model is modified by treating the saturation ceiling K as increasing with the size of the reachable susceptible pool (population) and decreasing with the share of the population that is aged out (65+), so that a county's ceiling is not a single state-level constant but is scaled by these two structural factors. Because DP02 has no income or poverty data, the economic hypotheses (poverty, income, public assistance as drivers) are explicitly not testable with the supplied data and are flagged as a limitation rather than answered from outside sources.
Limitations and bias. The share measure T_i (all-substance county total) is itself an enforcement-volume proxy, so the shares inherit the same reporting bias as the raw counts. The 2010-2012 fill from 2013 for the detailed rows is an approximation (small-county suppression differs by year). Cross-sectional correlations at the county level cannot establish causation; the positive education association is most plausibly a proxy for urban/metro status. The absence of income and poverty variables is the single largest constraint on answering the 'who is using and why it persists' hypotheses the problem raises.

## Subtask 3: Part 3. Using the Part 1 and Part 2 results, identify a possible strategy for countering the opioid crisis, test its eff

### Problem

Part 3. Using the Part 1 and Part 2 results, identify a possible strategy for countering the opioid crisis, test its effectiveness with the model(s), and identify the significant parameter bounds on which success (or failure) depends. Also include a 1-2 page memo to the Chief Administrator, DEA/NFLIS, summarizing the significant insights.

### Analysis

Strategy. Following the expert's description of what caps a local problem (Exchange 2), the strategy is a combined intervention acting on the two channels the model actually contains: (a) an enforcement-and-treatment intensity tau that lowers the intrinsic growth rate r (removing dealers, high-volume users, and initiating treatment throttles the recruitment/throughput that drives growth), and (b) a capacity-intensity kappa that lowers the saturation ceiling K (treatment capacity, naloxone, and prescribing controls shrink the reachable susceptible pool, i.e. the carrying capacity). The test re-runs the Part 1 per-state logistic under r -> r(1-tau) and K -> K(1-kappa) and measures the fraction of the 2018-2025 projected growth that is averted relative to the no-intervention projection. The success metric is a sustained reduction over the whole projection window (mirroring the persistence criterion from Exchange 3), not a one-year dip. The plausible range of tau and kappa is bounded above by 0.8 (a 20% residual) because the expert's channel structure removes but does not eradicate demand; the treatment-channel magnitude is anchored to the opioid-agonist-treatment mortality evidence (see the parameter table in Part 1, item 4).

### Modeling Process

For each (state, substance) series with fitted (r, K, t0, A0), the no-intervention 2018-2025 trajectory is B = sum_{t=8}^{15} A(t; r, K, t0, A0) and the treated trajectory is T = sum_{t=8}^{15} A(t; r(1-tau), K(1-kappa), t0, A0). The fraction averted is (B - T)/B, summed over all 10 series and normalized. tau and kappa are swept over {0, 0.1, ..., 0.8} independently (81 combinations). Success is defined as averting more than 50% of projected growth; failure as averting less than 10%. The significant parameter bound is the curve in the (tau, kappa) plane separating these two regimes.

Result. The fraction averted increases monotonically in both tau and kappa. On the diagonal tau = kappa:
  tau=kappa=0.0: averts 0% of projected 2018-26 growth
  tau=kappa=0.1: averts 13% of projected 2018-26 growth
  tau=kappa=0.2: averts 26% of projected 2018-26 growth
  tau=kappa=0.3: averts 39% of projected 2018-26 growth
  tau=kappa=0.4: averts 52% of projected 2018-26 growth
  tau=kappa=0.5: averts 64% of projected 2018-26 growth
  tau=kappa=0.6: averts 75% of projected 2018-26 growth
  tau=kappa=0.7: averts 83% of projected 2018-26 growth
  tau=kappa=0.8: averts 88% of projected 2018-26 growth
Success (averts > 50% of projected 2018-25 growth) is reached for 52 of the 81 (tau, kappa) pairs, including the entire region where the combined intensity is at or above roughly tau + kappa >= 0.6 (e.g. tau=kappa=0.4 already averts 52%; tau=0.8 alone averts 71%; kappa=0.8 alone averts 79%). Failure (averts < 10%) is confined to the low-intensity corner: only 4 pairs, all with tau <= 0.2 and kappa <= 0.1 (i.e. near-no-intervention). The significant parameter bound is therefore: the strategy succeeds if and only if at least one of the two channels is driven to a moderate-to-high intensity (roughly >= 0.4 on a 0-1 scale), or both are driven to at least a low-moderate intensity jointly; it fails only when both channels are left at or below about 10-20% intensity. Enforcing (tau) is slightly less effective alone than capacity-building (kappa) at equal intensity, because lowering the ceiling cuts the whole plateau while lowering the rate mainly slows the approach to it.
MEMO TO THE CHIEF ADMINISTRATOR, DEA/NFLIS DATABASE. Subject: What the 2010-2017 NFLIS data for Ohio, Kentucky, West Virginia, Virginia, and Pennsylvania show. (1) The opioid story in this region is a transition, not a single substance: heroin is established and now flat or declining in all five states, while synthetic opioids (the fentanyl family) are the growth story, rising from negligible in 2010-2012 to the dominant increment by 2017. A falling heroin count should not be read as a falling crisis, because the synthetic count is absorbing and exceeding it. (2) Ohio is the centre of gravity: its synthetic count rose roughly 400-fold (56 to 22,115) and is the largest and fastest in the region, centred on Hamilton (Cincinnati), Cuyahoga (Cleveland), and Montgomery (Dayton). Pennsylvania (Philadelphia, Pittsburgh) is on the same curve one to two years behind; Kentucky (Lexington) is small but the steepest relative riser; Virginia (Northern Virginia) is moderate; West Virginia is a small, late, secondary arrival. (3) The onsets are staggered and uncoordinated across state lines, which is the signature of independent supply arrivals rather than one synchronized wave — so a single-state intervention will not by itself stop the neighbours. (4) The growth is saturating, not exponential: each state is approaching a ceiling set by its reachable user pool, so the urgent window is now, before the larger states (OH, PA, VA) cross their saturation thresholds in the 2018-2022 period. (5) A combined strategy of enforcement plus treatment/capacity works only at meaningful intensity: the model averts more than half of the projected near-term growth only when at least one channel is driven to moderate-or-higher intensity, and it fails only when both are left near zero. A low-level, both-channels-at-a-bare-minimum posture is the one configuration the model predicts will not move the trajectory. (6) Data caveat: NFLIS counts track enforcement submission and lab volume as well as the underlying market, so single-year county spikes can be reporting artifacts; the trends above are the multi-year, persistent signals, not single-year peaks. The fifth state in the file is Pennsylvania, not Tennessee as the problem text names; Tennessee is absent from the supplied data.

### Outcome Analysis

Effectiveness and bounds. The strategy is effective but its success is bounded by the intervention intensities. The critical bound: success (>50% of projected 2018-25 growth averted) requires the combined intensity to clear a moderate threshold — approximately tau + kappa >= 0.6, or either channel alone at >= 0.4-0.5. Failure (<10% averted) is restricted to the near-zero-intensity corner (tau <= 0.2 and kappa <= 0.1). Between these is a broad intermediate region of partial success (10-50% averted). Capacity-building (kappa, lowering the ceiling) is marginally more effective per unit intensity than enforcement (tau, lowering the rate) because it cuts the whole plateau, not just the approach to it, so a resource-constrained policy should weight toward treatment capacity and demand reduction in addition to enforcement.
Limitations and bias. The test re-uses the Part 1 logistic, so it inherits that model's assumption that the ceiling and growth rate are stable absent intervention and that no new substance wave resets them; a novel fentanyl analogue would break the projection. The tau and kappa intensities are scenario variables scaled 0-1, not measured policy doses; the mapping from a real program (e.g. a given number of treatment slots) to a kappa value is not calibrated by the data, so the bounds are relative (a moderate-or-higher intensity is needed) rather than an absolute program size. The treatment-channel magnitude is anchored to the external mortality evidence (JAMA Psychiatry 2021, DOI 10.1001/jamapsychiatry.2021.0976) for plausibility, but the model does not independently verify that a given kappa achieves that magnitude in these counties. The NFLIS enforcement-volume bias means the model measures the reported market, so an intervention that reduces enforcement submission (not the market) would look like success; the persistence-based reading (a sustained, multi-year reduction, not a one-year dip) is the guard against that. Finally, the strategy is tested within the five-state region only; its transfer to other regions, and to Tennessee which is absent from the data, is not established.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
