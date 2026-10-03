# Interaction Evidence — 2019_C (10 exchanges)

Each exchange: question (expert_question_N.md), reply (expert_reply_N.json), and how the reply
was converted into the model (parameter, constraint, or rule). Values used in solution.json.

## Exchange 1 — substance grouping (structural)
Q: In 2017 Appalachia, "the fentanyl problem" = fake pills or powder?
Reply: illicitly manufactured fentanyl, predominantly powder (mixed into heroin or pressed into
counterfeit pills); counterfeit pills real but secondary in 2017; pharmaceutical fentanyl minor.
Model effect: three tracked groups — `synthetic` (pharmaceutical opioid analgesics: oxycodone,
hydrocodone, hydromorphone, methadone, fentanyl, tramadol, oxymorphone, buprenorphine), `heroin`
(heroin entries, which in practice include fentanyl-adulterated powder per Exch. 2-3), and
`fentanyl_analog` (illicit research-chemical fentanyls, tracked as the novel-substance signal).
No clean separation is possible in the data (Exch. 2), so the heroin group is treated as the
"heroin/fentanyl-powder" channel.

## Exchange 2 — counterfeit pills counted under brand names
Q: Are counterfeit pills reported as "oxycodone" treated as oxycodone risk?
Reply: no — labeling artifact; investigators treat them as fentanyl cases.
Model effect: oxycodone/hydrocodone counts carry a fentanyl component; a rising synthetic count
in a county is therefore also a fentanyl-threat indicator. Implemented as a cross-group coupling:
the fentanyl channel receives a fraction f_coup of synthetic-channel spread (f_coup = 0.25,
sensitivity 0.10-0.40; justified by the 2013-2017 fentanyl share of the synthetic channel in the
data, see below). Reported as an explicit assumption, not as expert fact.

## Exchange 3 — cause of 2016-17 jumps
Q: What did investigators attribute sudden county jumps to?
Reply: fentanyl entering the local heroin supply (adulterated powder or counterfeit pills);
same users, more potent supply; sometimes a new dealer network/route.
Model effect: the 2016-17 inflection is modeled as a supply-shock step on the fentanyl channel
(step size from data: state-level fentanyl-analog + fentanyl growth 2015->2016->2017), not as a
change in user counts. This justifies a regime-switch term in the fentanyl equations.

## Exchange 4 — no retroactive retesting
Q: Do labs retest old evidence, making old years' counts jump later?
Reply: no systematic retesting of closed cases; counts are by year of receipt; within-year
detection improved 2013-2017, so some of the fentanyl rise is detection improvement.
Model effect: the time series is treated as submission-anchored (valid for trend modeling);
a detection-growth covariate is NOT added retroactively, but a caveat is carried in
limitations: part of the fentanyl growth 2013-2017 is measurement, so its fitted growth rate is
an upper bound; sensitivity of the 2018-2020 forecast to a 0-50% detection-deflation factor.

## Exchange 5 — spread lag and direction
Q: Neighbors hit within 1-2 years?
Reply: usually yes, 1-3 years along corridors; adjacency insufficient; spread hierarchical
(metro -> rural); supply shocks can hit non-adjacent counties sharing a dealer network.
Model effect: (a) diffusion kernel uses neighbor graph with distance-decay exp(-d/L), L = 15 km
swept 10-30 km; (b) hierarchical seeding: edge weight from county j to i multiplied by
w_ij = 1 + a_h * hubness_j (hubness = standardized county total reports 2010-2015), a_h = 0.5;
(c) lag: diffusion uses x_{j,t-1} (one-year-lagged neighbor state), matching the 1-3 year
observed lag with L controlling speed; (d) limit acknowledged: shared-network simultaneous
arrival breaks pure spatial diffusion — carried as a limitation, partially covered by the
state-level common shock term s_t.

## Exchange 6 — flat county = plateau, not solved
Q: What happens when a county's counts stop growing?
Reply: substitution, saturation, reporting artifact, or displacement to neighbors; flat =
steady state at elevated prevalence; genuine decline rare, requires supply disruption or
large-scale treatment/naloxone.
Model effect: the model includes a saturation term (log1p of own prior count as the growth
driver, so growth rate declines with level) and a mean-reversion-to-plateau term; predictions
beyond a local peak are clipped: forecast horizon limited to 2 years past any county's detected
peak (see Exch. 8), and post-peak predicted growth is damped by factor 0.5 per year (saturation
assumption; sensitivity 0.3-0.7).

## Exchange 7 — rural protection factors
Q: What keeps a rural county untouched?
Reply: no transportation corridor, small dispersed population, no anchor metro, isolation,
few high-volume prescribers; protection = delay, not immunity; one route can flip a county.
Model effect: county baseline b_c regressed on ACS covariates (population_in_households as the
"market size" proxy, nonfamily_households and living_alone as social-isolation proxies,
pct_bachelors_plus as human-capital proxy); counties with small population get a higher
introduction-lag via the diffusion weight (spread into i scaled by 1/(1 + pop_i/pop_med)) —
thin markets are seeded later; "delay not immunity" implemented by never setting spread weight
to zero, only reducing it.

## Exchange 8 — prediction horizon past a peak
Q: How long to trust a post-peak climb prediction?
Reply: at most 1-2 years, and only if the peak is an artifact, a new supply shock is arriving,
or the county is a still-seeding metro hub.
Model effect: forecast horizon = 3 years (2018-2020) but county-level forecasts after that
county's in-sample or predicted peak are flagged low-confidence and damped (0.5x/yr); hub
counties (top-quartile total reports) exempt from damping (they may keep seeding). Threshold
exceedance predictions are reported with these flags.

## Exchange 9 — what triggers a state alarm
Q: What caseload level triggers "crossing a threshold"?
Reply: rate and trend, not raw count — cases per 100k; trend trigger roughly a doubling or
sustained steep rise over 2-3 years; novel-substance override at very low counts (single digits
to low tens of first fentanyl identifications); clustering alerts.
Model effect: threshold definitions used in the report (rates per 100k population from ACS
population_in_households; trend trigger = yoy growth >= 50% or 2-year CAGR >= 25%;
fentanyl novel-substance override = first-year appearance of fentanyl_analog >= 5 cases in a
county). These are the alert thresholds the model predicts will be crossed where/when.

## Exchange 10 — interventions that worked
Q: What single intervention bent the curve, and at what cost?
Reply: no single intervention reliably bent case counts; closest = MAT expansion (buprenorphine/
methadone) + naloxone distribution; naloxone cuts deaths without reducing counts; MAT reduces
deaths and sometimes prevalence where capacity is large relative to addicted population;
supply disruption produces sharp temporary drops that reverse; costs: naloxone ~tens of $/kit,
MAT ~thousands of $/patient/yr (empirical, not reliable).
Model effect (Part 3): intervention modeled as two multipliers on the state-year growth rate:
MAT capacity ratio rho = (MAT slots)/(est. addicted population) reduces growth by factor
(1 - eff_MAT * min(1, rho/rho_sat)) with eff_MAT in [0.1, 0.3], rho_sat = 0.3 (saturated
capacity ratio assumption, sensitivity 0.15-0.5); naloxone coverage nu reduces *deaths*, not
case counts, so it does not enter the case-count model — it is reported as the death-side
benefit, with death reduction ~ 30-50% per literature-typical naloxone access (kept as
calibrated input, source below). Success bound: strategy succeeds (bends case-count curve) only
if eff_MAT * min(1, rho/rho_sat) >= 0.15, i.e. combined MAT capacity must reach ~15% effective
reduction; failure bound: if rho < 0.1, the growth reduction < 5% and the curve is unchanged.

## Empirical parameter table (for solution.json)
| name | value | interval | source |
|---|---|---|---|
| f_coup (synthetic->fentanyl cross-coupling) | 0.25 | [0.10, 0.40] | data-derived: state-level fentanyl-analog+fentanyl share of synthetic channel 2015-2017 (this dataset); expert Exch. 1-2 justify the direction |
| a_h (hierarchical hubness weight) | 0.5 | [0.0, 1.0] | assumption calibrated to Exch. 5 (metro seeds rural); sweep in model |
| L (spatial decay, km) | 15 | [10, 30] | calibrated by OOS R2 sweep; Exch. 5 lag 1-3 yr sets scale |
| post-peak damping | 0.5/yr | [0.3, 0.7] | Exch. 6, 8 |
| eff_MAT | 0.20 | [0.10, 0.30] | Exch. 10 (MAT reduces deaths and sometimes prevalence; no single lever) |
| rho_sat (saturated MAT capacity ratio) | 0.30 | [0.15, 0.50] | Exch. 10 ("only where capacity large relative to addicted population") |
| naloxone death reduction | 0.40 | [0.30, 0.50] | literature: CDC naloxone co-prescribing and bystander access studies (CDC; see solution for full refs) — used on death side only |
| trend alert trigger | yoy >= 50% or 2yr CAGR >= 25% | — | Exch. 9 |
| novel-substance override | first fentanyl_analog >= 5 cases | [1, 10] | Exch. 9 |
| MAT cost | ~$10,000/patient/yr | [5,000-20,000] | Exch. 10 ("several thousand per patient per year") |
| naloxone kit cost | ~$50/kit | [10-100] | Exch. 10 ("tens of dollars per kit") |
