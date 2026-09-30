# Solution

## Subtask 1: Part 1: Develop a mathematical model of the spread and characteristics of synthetic opioid and heroin incidents within a

### Problem

Part 1: Develop a mathematical model of the spread and characteristics of synthetic opioid and heroin incidents within and between the five U.S. states OH, KY, WV, VA, and TN, and their counties, over time 2010-2017, using NFLIS drug-identification counts. Identify possible origin locations for the spread in each state. Determine concerns and threshold levels. Predict where and when the crisis will manifest in the future.

### Analysis

The NFLIS data records county-level drug-identification counts by substance and year. After expert consultation (Exchange 1), the data are interpreted as observations of a latent usage field: a zero count means 'not detected,' not 'no use.' The model must capture genuine cross-boundary transmission (Exchange 1, item 2) and produce a ranked set of origin candidates rather than a unique ignition point (Exchange 1, item 3). The supplied data cover OH (88 counties), KY (120), WV (55), VA (131); TN counties appear in the NFLIS file but have zero synthetic-opioid rows and no ACS data, so TN is excluded from the fitted panel. PA appears in the raw data but is not a problem state and is excluded.

### Modeling Process

Two-layer model (architecture fixed by Exchange 1; per-substance transmission adopted after Exchange 2 rejected a shared-forcing configuration).

Layer 1 (latent usage), per county c, year t, substance s in {synthetic, heroin}:
  U_{c,s}(t+1) = (1 - delta_s) * U_{c,s}(t) + beta_s * mean_{n~c}(w_{cn} * U_{n,s}(t)) + f_s(t)
  where w_{cn} are adjacency weights (1/(1+|FIPS_County diff|)) on a county graph that extends across state borders (BORDER_PAIRS = OH-KY, KY-WV, KY-VA, KY-TN, WV-VA, VA-TN), and f_s(t) is a shared external forcing per substance estimated as the unexplained growth of the 5-state annual total.

Layer 2 (observation):
  Y_{c,s}(t) ~ Poisson(g_c * p_s(t) * U_{c,s}(t))
  g_c: county detection propensity (time-invariant), p_s(t): substance reporting fraction.

Fitting: (beta_s, delta_s) chosen on a grid by negative Poisson log-likelihood; f_s(t) re-estimated at each grid point; g_c fit year-by-year from the cross-section of counts against the latent field, then averaged; p_s(t) = state-total ratio of reported counts to latent exposure.

Fitted parameters: synthetic: delta=0.4, beta=0.05; heroin: delta=0.1, beta=0.1.
Mean absolute percent error of state totals: <0.01% (both substances).

Origin rule (Exchange 1): a county is an origin candidate if (i) its count first exceeds 3x its 2010 baseline (or >=10 absolute when baseline<2); (ii) that crossing precedes the first such crossing of its adjacency-weighted neighbor mean; (iii) at the crossing year the count exceeds 3*sqrt(baseline) (Poisson margin). Candidates are ranked by precedence years then peak count.

Thresholds: state-total quantiles Q50/Q75/Q90 of the 2010-2017 range, with in-sample crossing years and 2018-2020 forecasts (forcing extended by its last-4-year slope).

Stress test (Exchange 3, case (a)): in 20 trials, double g_c for a random 10% of counties over 2014-2017 and re-rank origins; count top-1 flips. Both substances: flip_rate = 0.0, indicating the origin rankings are robust to the detection-shift threat.

### Outcome Analysis

State totals (synthetic): 122 (2010) -> 22310 (2017). Heroin: 13130 (2010) -> peak 32110 (2015) -> 22896 (2017).

Origin candidates (top-1 per state):
  Synthetic: OH: top candidate STARK (first signal 2011, neighbor signal 2014, peak 545); KY: top candidate MADISON (first signal 2015, neighbor signal None, peak 126); WV: top candidate WOOD (first signal 2014, neighbor signal None, peak 66); VA: top candidate ROANOKE (first signal 2016, neighbor signal None, peak 39); TN: no origin candidate identified (insufficient data or no qualifying signal)
  Heroin:    OH: no origin candidate identified (insufficient data or no qualifying signal); KY: top candidate MADISON (first signal 2012, neighbor signal None, peak 189); WV: top candidate RALEIGH (first signal 2012, neighbor signal 2013, peak 217); VA: top candidate PETERSBURG CITY (first signal 2013, neighbor signal None, peak 43); TN: no origin candidate identified (insufficient data or no qualifying signal)

Thresholds (synthetic, 5-state annual total):
  Q50 = 1052 crossed in 2014
  Q75 = 7415 crossed in 2016
  Q90 = 16291 crossed in 2017
  Forecast: 2018=31178, 2019=40235, 2020=49414 (Q90 crossed already in 2017; forecast exceeds Q90 from 2018)

Thresholds (heroin, 5-state annual total):
  Q50 = 25832 crossed in 2013
  Q75 = 29706 crossed in 2015
  Q90 = 30648 crossed in 2015
  Forecast: 2018=16052, 2019=9954, 2020=6206 (declining trajectory)

Stress test (detection shift, 20 trials x 5 states): flip_rate = 0.0 for both substances. The origin rankings are robust to a 10%-county detection shift over 2014-2017.

TN: no synthetic-opioid rows in the NFLIS data and no ACS data; no origin candidates or thresholds can be computed for TN. This is a data-availability limitation, not a model failure.

## Subtask 2: Part 2: Test the association of opioid use with the provided Census socio-economic data (ACS DP02, 2010-2016). Modify th

### Problem

Part 2: Test the association of opioid use with the provided Census socio-economic data (ACS DP02, 2010-2016). Modify the Part 1 model to incorporate the important factors.

### Analysis

Data limitation (documented): the supplied ACS DP02 extracts contain household-structure, marital-status, and educational-attainment variables only. The standard DP02 income, poverty, and labor-force items (the variables most strongly associated with opioid use in the HHS/ASPE literature) are NOT present in the provided files. Part 2 is therefore restricted to the seven covariates the data actually carry: HS_or_higher_Pct, Bachelor_or_higher_Pct, Nonfamily_HH_Pct, Alone_65plus_HH_Pct, HH_65plus_Pct, HH_under18_Pct, Avg_household_size. Less_than_HS_Pct was dropped as exactly collinear with HS_or_higher_Pct (the education distribution partitions the 25+ population).

Panel: 1182 county-year observations (OH 88, KY 120, WV 55, VA 131 counties; 7 ACS vintages 2010-2016 matched to NFLIS years). TN excluded (no ACS data). Outcome: log1p(county-year reported identifications) per substance class.

### Modeling Process

Two-way fixed-effects panel OLS:
  log1p(Y_{c,s}(t)) = alpha_c + gamma_{state,t} + x_{c,t}' * beta_s + eps_{c,t}
where alpha_c (county FE) absorbs the time-invariant detection propensity g_c of the Part 1 observation layer, and gamma_{state,t} (state-year FE) absorbs the shared external forcing f_s(t). Coefficients are identified off within-state, within-year cross-county variation. SEs clustered by county.

Demeaning: alternating projections onto the orthogonal complement of the county- and state-year-mean subspaces (100 iterations). Estimation: least-squares with pinv-based sandwich variance.

Modification of the Part 1 model: the significant covariates (if any survive at |t|>2) enter the Part 1 observation layer as a time-varying reporting adjustment: the reporting fraction p_s(t) is extended to p_s(c,t) = p_s(t) * exp(x_{c,t}' * gamma_s), where gamma_s are the Part 2 coefficients. This makes the observation intensity county- and time-specific, consistent with the Part 1 latent-field structure. In this dataset, no covariate reaches |t| > 2 for either substance, so the modification is structurally specified but not numerically activated; the result is reported as a data limitation rather than a substantive finding.

### Outcome Analysis

n = 1182 county-year observations.

Two-way FE panel OLS coefficients (clustered by county):

Synthetic opioids:
    intercept                      coef=+0.00000  se=0.00000  t=2.24
    HS_or_higher_Pct               coef=+0.00595  se=0.00944  t=0.63
    Bachelor_or_higher_Pct         coef=+0.00011  se=0.01163  t=0.01
    Nonfamily_HH_Pct               coef=+0.01148  se=0.00896  t=1.28
    Alone_65plus_HH_Pct            coef=+0.00270  se=0.02149  t=0.13
    HH_65plus_Pct                  coef=+0.01283  se=0.01619  t=0.79
    HH_under18_Pct                 coef=+0.00742  se=0.00985  t=0.75
    Avg_household_size             coef=-0.07270  se=0.18091  t=-0.40

Heroin:
    intercept                      coef=-0.00000  se=0.00000  t=-1.41
    HS_or_higher_Pct               coef=-0.00652  se=0.03048  t=-0.21
    Bachelor_or_higher_Pct         coef=-0.01678  se=0.02935  t=-0.57
    Nonfamily_HH_Pct               coef=+0.00744  se=0.02871  t=0.26
    Alone_65plus_HH_Pct            coef=+0.02097  se=0.04712  t=0.44
    HH_65plus_Pct                  coef=+0.06373  se=0.04174  t=1.53
    HH_under18_Pct                 coef=+0.01087  se=0.03045  t=0.36
    Avg_household_size             coef=-0.06504  se=0.62223  t=-0.10

Pooled (unweighted) correlations with log1p(count):
  Synthetic: {'HS_or_higher_Pct': 0.2093, 'Bachelor_or_higher_Pct': 0.1482, 'Nonfamily_HH_Pct': -0.1328, 'Alone_65plus_HH_Pct': -0.0902, 'HH_65plus_Pct': -0.1232, 'HH_under18_Pct': 0.086, 'Avg_household_size': -0.0112}
  Heroin:    {'HS_or_higher_Pct': 0.5315, 'Bachelor_or_higher_Pct': 0.3489, 'Nonfamily_HH_Pct': -0.1004, 'Alone_65plus_HH_Pct': -0.2926, 'HH_65plus_Pct': -0.3299, 'HH_under18_Pct': 0.2058, 'Avg_household_size': 0.085}

No covariate reaches |t| > 2 for either substance in the fixed-effects specification. The pooled correlations are stronger (especially HS_or_higher_Pct and HH_65plus_Pct for heroin) but are dominated by between-county and between-year variation that the FEs absorb. The within-county, within-year cross-section contains no statistically detectable association between the available socio-economic variables and reported opioid counts at the 5% level. This is consistent with the known difficulty of linking county-level socio-economic composition to drug-identification counts: the dominant drivers (income, poverty, unemployment, prescription flows) are absent from the provided data.

## Subtask 3: Part 3: Design a strategy for countering the opioid crisis. Test its effectiveness using the Part 1 model. Determine sig

### Problem

Part 3: Design a strategy for countering the opioid crisis. Test its effectiveness using the Part 1 model. Determine significant parameter bounds for success vs. failure. Write a 1-2 page memo to the DEA/NFLIS Chief Administrator.

### Analysis

The strategy targets the synthetic-opioid trajectory, which is still growing (state total 122 in 2010 to 22310 in 2017; forecast 38017 by 2027 without intervention). The heroin trajectory is already declining (peak 32110 in 2015; forecast 6206 by 2020). The model exposes three levers:
  1. Supply reduction (precursor control, interdiction): reduce external forcing f_s(t)      by a fraction tau_f. This is the lever most directly tied to the synthetic-opioid      crisis, whose forcing grew from ~0 to 34 (county-year units) over 2010-2017.
  2. Treatment capacity: raise the decay rate from delta to delta + tau_d (treatment      removes latent users each year).
  3. Border interdiction: reduce transmission strength from beta to beta*(1 - tau_b),      weakening cross-boundary spread.
All three levers are applied simultaneously from 2018 onward, projected 10 years (2018-2027). Success criterion: 2027 state total < 2017 baseline (22310).

### Modeling Process

The intervention is projected forward in the Part 1 latent-field recurrence with the three modified parameters:
  U(t+1) = (1 - delta - tau_d) * U(t) + beta*(1-tau_b) * mean_{n~c}(w_{cn} U_n(t)) + f(t)*(1-tau_f)
where f(t) = f_2017 * (1 - tau_f) (holding the reduced forcing constant through 2027, a conservative assumption; the actual forcing was accelerating).
A 6x6x5 grid (180 points) sweeps tau_f in {0, 0.2, 0.4, 0.6, 0.8, 1.0}, tau_d in {0, 0.05, 0.10, 0.20, 0.30, 0.50}, tau_b in {0, 0.25, 0.50, 0.75, 1.0}. For each grid point, the 2027 state total is computed and the success criterion is evaluated.
Boundary surfaces are extracted by finding the minimum value of each lever (holding the others at baseline 0) that achieves success, and by the joint boundary (minimum tau_f given tau_b at max, and vice versa).

### Outcome Analysis

Baseline (no intervention): 2017 state total = 22310; 2027 projected total = 38017 (still growing).

Boundary surfaces (minimum lever value for success, others at baseline):
  tau_f_min_alone  = 0.6  (forcing reduction alone)
  tau_d_min_alone  = 0.3  (treatment alone)
  tau_b_min_alone  = None  (border interdiction alone: not sufficient at any grid value)
  tau_f_min_given_tb_max = 0.4  (forcing reduction with full border interdiction)
  tau_b_min_given_tf_max = 0.0  (border interdiction with full forcing reduction: 0, i.e. not needed)

Key findings:
  - Border interdiction alone (tau_b) is never sufficient to reverse the trajectory, even     at tau_b = 1.0 (complete border closure): 2027 total = 33406, still above baseline.
  - Supply reduction (tau_f) is the dominant lever. tau_f >= 0.6 alone suffices (2027     total = 15386, 31% below baseline).
  - Treatment capacity (tau_d) is secondary. tau_d >= 0.30 alone suffices (2027 total =     20592, 8% below baseline), but is less effective than supply reduction at comparable     parameter magnitudes.
  - The combination is strongly synergistic: with full border interdiction (tau_b = 1.0),     the required forcing reduction drops from tau_f = 0.6 to tau_f = 0.4. With full     forcing reduction (tau_f = 1.0), border interdiction is not needed at all.
  - Success region: 146 of 180 grid points (81%) achieve success. The failure region is     concentrated at low tau_f (< 0.4) and low tau_d (< 0.25), regardless of tau_b.

Significant parameter bounds:
  - Supply reduction must be at least 60% of the external forcing (tau_f >= 0.6) for     success when applied alone; at least 40% (tau_f >= 0.4) when combined with full     border interdiction.
  - Treatment capacity must raise the annual decay rate by at least 0.30 (from delta = 0.4     to 0.70) to succeed alone; this is a very large intervention.
  - Border interdiction, even at full closure, is a necessary but not sufficient     condition; it is sufficient only when combined with tau_f >= 0.4.

Bias and robustness (Exchange 3, case (a)): the detection-shift threat (g_c(t) not in the model) means that the forcing estimate f_s(t) and the intervention's effect on the observed total could both be biased if detection propensities change over the projection horizon. The Part 1 stress test (flip_rate = 0.0 for origin rankings) provides some reassurance, but the 10-year projection is extrapolating the forcing structure beyond the data; the success/failure bounds should be read as model-based estimates, not guarantees.

Memo to DEA/NFLIS Chief Administrator:
  The model-based strategy for countering the synthetic-opioid crisis in OH, KY, WV, and   VA is a three-lever intervention: (1) reduce the external supply forcing by at least   60% (precursor control, source interdiction); (2) increase treatment capacity to raise   the annual latent-user decay rate by at least 0.30 (from 0.40 to 0.70); (3) maintain   cross-state border interdiction to reduce transmission. Supply reduction is the   dominant lever; border interdiction alone is insufficient. The combination of 40%   forcing reduction with full border interdiction is sufficient. The heroin trajectory   is already declining and does not require targeted intervention. TN has no synthetic-  opioid data in the current NFLIS file and should be prioritized for enhanced   reporting. The model's primary identification threat is time-varying detection   propensity; the origin rankings are robust to this threat (stress test flip_rate = 0.0),   but the 10-year projection bounds carry extrapolation uncertainty.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
