# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — MCM 2019-C

Ten exchanges, one question each. Questions asked before the work they governed;
each reply converted into a model parameter, structural rule, or test.
Question files: `logs/operator_feedback/expert_question_N.md`; reply files:
`logs/operator_feedback/expert_reply_N.json` (controller-owned, unedited).

## Exchange 1 — entry route for fentanyl
- **Q**: In Appalachian counties around 2013-2015, when fentanyl started showing
  up in lab testing, how did it usually arrive — replacing prescription pills,
  mixed into heroin, or sold as counterfeit pills?
- **Reply (gist)**: Predominantly mixed into / sold as heroin (potency booster in
  the heroin supply); counterfeit pills secondary, growing only ~2015-16 onward;
  fentanyl replacing pills was not the 2013-2015 pattern.
- **Conversion**: Structural rule in the Part 1 model: the synthetic-opioid
  process is coupled to the heroin process — the spread term feeds from the
  combined hub supply, and the 2014-2016 explosive growth in the data (synthetic
  share 0.3%-45%) is read as heroin-market entry, not a pill-substitution event.
  Origin detection for synthetic therefore reports the first fentanyl-
  adulterated-heroin signal (2013-2014 counties), with the 2010 fentanyl counts
  (single digits per state) treated as background, not origins.

## Exchange 2 — does a doubling in one county make neighbors jump within a year?
- **Q**: If a county's fentanyl-in-heroin problem doubles year over year, does
  nearby county lab testing usually jump within about a year?
- **Reply (gist)**: Not necessarily / not in lockstep; counts reflect local
  submission behavior and lab capacity; when spread does occur it is via shared
  supply chains / transport corridors (metro area spanning counties), adjacency
  alone weak; timing 1-3 years, usually gradual.
- **Conversion**: (a) Part 1 model: county-to-county spread is modeled through
  corridor/hub coupling, not plain adjacency; the neighbor term uses a 2-year
  delay (DELAY=2 in `model_part3.py`, mid-range of the stated 1-3y). (b)
  Calibration constraint: the spread coupling kappa is set small
  (KAPPA=0.05, further scaled by /20 on the hub term) so that neighbor
  trajectories are gradual rather than lockstep doublings; the Part 3 baseline
  check (5-state total 2018→2030 stays within ~20% of the state-momentum
  extrapolation) is the test that the coupling does not over-spread.

## Exchange 3 — city count behavior at the shift
- **Q**: When a mid-size city's heroin market shifts to fentanyl-adulterated
  supply, does the city's own lab testing count rise, fall, or hold?
- **Reply (gist)**: Usually rises, often sharply (more seizures/submissions,
  labs reporting fentanyl as a distinct substance); can dip for the heroin
  series specifically; net total rises.
- **Conversion**: Interpretation rule applied to the 2014-2017 data: the
  simultaneous synthetic surge and (later) heroin decline in OH/PA/KY is the
  displacement signature the model encodes — growth term on synthetic is
  positive while the heroin series enters its decay regime; threshold
  "crossings" are therefore reported on the net narcotic-analgesic total and on
  the synthetic series separately, and a rising synthetic count is taken as a
  genuine signal, not an artifact, in growing counties.

## Exchange 4 — urban vs rural concentration
- **Q**: In 2017-era Appalachian counties, where did most fentanyl seizures
  cluster — big-city lab hubs, or rural counties far from any city?
- **Reply (gist)**: Metro/urban counties and their lab hubs; rural rising later
  and at lower counts, with submissions flowing to regional labs.
- **Conversion**: Hub set used in `model_part3.py` (HAMILTON/CINCINNATI,
  CUYAHOGA/CLEVELAND, FRANKLIN/COLUMBUS, MONTGOMERY; PHILADELPHIA, ALLEGHENY;
  JEFFERSON/LOUISVILLE, BOONE/LEXINGTON; RICHMOND, CHESTERFIELD; KANAWHA/
  CHARLESTON, MERCER, MONONGALIA, HARRISON) — chosen as the metro counties with
  high 2010-2017 synthetic totals, matching the data (2017 top counties are
  metros in every state). Origin-detection table in the solution is therefore
  reported hub-first with rural first-crossings flagged as later-arriving.

## Exchange 5 — socioeconomic gradient
- **Q**: In the worst-affected Appalachian counties, was the problem worse in
  poorer/less-educated or wealthier/more-educated towns?
- **Reply (gist)**: Poorer, less-educated, the dominant pattern; initial
  prescription wave was cross-income but the gradient sharpened as the crisis
  shifted to heroin/fentanyl; lab counts are a weak proxy and the association
  should be tested against census variables.
- **Conversion**: Part 2 hypothesis selection — education/poverty variables
  prioritized for the census correlations; the pooled result (hs_grad_pct vs
  na_rate: r = −0.144, OLS coef −0.067 per percentage point, p < 0.001,
  controls year+state) and the 2016 state cross-sections (KY r=−0.135,
  OH r=−0.093, PA/VA/WV near zero or weaker) confirm a negative
  education gradient on the total opioid incident rate. The Part 2 "modified
  model" adds hs_grad_pct as a covariate; the Part 3 strategy is aimed at
  education-poor, corridor-adjacent counties first.

## Exchange 6 — naloxone diffusion lag
- **Q**: After big cities got naloxone distribution going, how long before
  nearby rural counties saw it arrive?
- **Reply (gist)**: Commonly 3-7 years, longer in the most remote counties;
  driven by policy/infrastructure diffusion (state health departments,
  standing orders, pharmacy opt-in), not geography alone.
- **Conversion**: Part 3 parameter LAG (rural naloxone onset after metro onset)
  swept over {3, 5}, both inside the stated 3-7y interval; headline case uses
  LAG=3. The model applies naloxone to deaths only (not to counts), matching
  the reply that local programs act on the demand/harm side.

## Exchange 7 — rural lab routing
- **Q**: In a rural county, do police usually send most drug evidence to a
  state lab, a neighboring city's lab, or a local lab?
- **Reply (gist)**: Rural counties rarely have local labs; most evidence goes to
  state labs / regional satellites; city-lab routing is the exception.
  Consequence: county counts are a proxy for lab-service catchment, not strict
  local seizure volume.
- **Conversion**: Stated limitation of the entire county-level analysis
  (solution limitations section); motivates using state-level totals for the
  threshold/projection analysis and county level only for origin/ranking.
  Also justifies not reading single-county spikes as local outbreaks (used in
  Exchange 8).

## Exchange 8 — local jump vs regional wave
- **Q**: When a county's seizures jump to a new high, is it usually a local
  problem spreading, or part of a wider state/regional wave?
- **Reply (gist)**: Usually a wider state/regional wave; metro hubs first, then
  adjacent/rural counties over 1-3 years; lone county jumps can be
  lab-routing/submission artifacts and should be checked against neighbors.
- **Conversion**: Part 1 state-level fit is the primary projection engine (not
  county-level extrapolation); county-level origin detection requires a county
  to be consistent with its state trajectory (the reported first-crossings all
  sit inside the state's rising window). Part 3: the policy effect g_s(t) is
  state-wide (a wave-level lever), applied uniformly to all counties of a
  state, with staggered county response emerging from the county-level
  saturation states.

## Exchange 9 — what happens if doubling continues
- **Q**: If a rural county's fentanyl problem keeps doubling each year and
  nothing is done, what usually happens after a few more years?
- **Reply (gist)**: It stops doubling and saturates — S-shape, plateau at a
  high endemic level set by the using population and lab capacity; supply
  shocks can spike/dip but not renew sustained doubling; small-count "doubling"
  is an artifact.
- **Conversion**: (a) The Part 1 projection for the synthetic series is an
  S-curve (logistic) at state level, not pure exponential; the baseline 2030
  target in Part 3 is the state-momentum extrapolation capped at 3x the 2017
  level (the plateau cap). (b) County invasion rates capped at 2.0/yr
  (doubling) in `model_part3.py` so that tiny-count counties cannot inflate the
  projection; (c) "success" in Part 3 is defined as holding the 2030 count at
  or below the 2020 level (plateau prevention), not an impossible return to
  2017.

## Exchange 10 — what actually brings numbers down
- **Q**: When a county's fentanyl numbers finally went down, was it more from
  local health programs or state-wide policy changes (laws, funding)?
- **Reply (gist)**: State-wide policy changes (enforcement, scheduling,
  prescribing regulation, lab/naloxone funding) dominate; local health
  programs are secondary and act on deaths, not counts; declines are often just
  the saturation phase; lone drops can be artifacts.
- **Conversion**: The Part 3 strategy is a state-level policy package (g_inf,
  the asymptotic reduction of the endemic level K_c and of the invasion rate)
  plus metro-first naloxone (e_inf, LAG) — exactly the two-lever structure the
  reply prescribes. The sweep bounds reported as the success/failure boundary:
  g_inf >= 0.4 with tau <= 3 holds all five states' 2030 count below their 2020
  level; g_inf <= 0.2 does not (states_below_2020 drops to 4-5 with weak
  reductions); naloxone effectiveness e_inf 0.3-0.7 changes death reduction
  24%-77% but barely moves counts, confirming the reply that counts respond to
  policy, deaths to naloxone.
