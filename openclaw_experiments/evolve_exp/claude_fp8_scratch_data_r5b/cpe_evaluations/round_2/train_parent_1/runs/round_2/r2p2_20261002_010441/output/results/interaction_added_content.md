# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — 2019_C (Opioid Crisis, NFLIS/Census)

Three exchanges, one question each. Each reply was converted into a model
parameter or constraint before the next exchange; no reply text is copied into
the submission.

## Exchange 1
**Question:** *When opioid use first spread into a small region, which place
types do you most often see it start in first, and why?*

**Reply (summary):** Earliest sustained take-off is seen in small-to-mid-size
cities and their immediate metro counties (county seats along transport
corridors), driven by pharmacy/clinic supply, enough density to sustain a
market, deindustrialized economic distress, and tight peer/kinship networks.
Rural counties light up later as spillover.

**Conversion to work (used in model):**
- Parameter: `place_type` ordinal = {metro-core, small-city/county-seat,
  rural}, with small-city/county-seat assigned the highest "seed propensity"
  and metro-core the second highest; rural lowest. This is the prior used to
  break ties in the origin-detection ranking (earliest sustained activity,
  then seed-propensity, then observed growth). Source: Exchange 1.
- Constraint: origin candidates are reported as county-seats/small cities
  rather than the largest metros; the model's "earliest sustained start"
  score is interpreted through this lens. Source: Exchange 1.
- Interval of validity: the expert frames this as an empirical
  generalization for Appalachia/Ohio Valley, so it is applied to the five
  problem states (OH, KY, WV, VA) and not exported.

## Exchange 2
**Question:** *When you work with people in small cities affected by opioid
abuse, what tends to help most, and what tends to backfire?*

**Reply (summary):** Helps — low-barrier local treatment (MAT) capacity,
harm reduction (naloxone), trusted local messengers, economic/structural
support, non-punitive framing. Backfires — punitive enforcement-first
responses, and especially abrupt prescribing/pill-mill crackdowns without
treatment capacity (drives users to illicit heroin/fentanyl, raising deaths).

**Conversion to work (used in model):**
- Parameter: `treat_rate` (fraction of uncontrolled users entering effective
  treatment per year) = base 0.25, sensitivity 0.1–0.4. This is the
  effectiveness of the "helps" bundle. Source: Exchange 2.
- Parameter/constraint: `enforcement` (annual punitive-enforcement intensity)
  with a **backfire term**: when `enforcement` exceeds `treat_rate`, a
  positive term `0.5*(enforcement - treat_rate)` is added to the uncontrolled
  use fraction, i.e. enforcement outpacing treatment capacity *increases*
  measured use/overdose risk (substitution to illicit supply). Success
  requires `enforcement ≤ treat_rate`. Source: Exchange 2.
- Decision rule: the recommended strategy pairs treatment-capacity expansion
  with harm reduction and explicitly bounds enforcement below the treatment
  ramp (no crackdown-first). Source: Exchange 2.

## Exchange 3
**Question:** *In towns that got treatment capacity quickly, roughly how long
did it take to see the change in overdose problems?*

**Reply (summary):** ~1–3 years to a measurable change in overdose, 2–5 years
for a clear sustained decline; harm reduction (naloxone) shows within months
to ~1 year; the lag is capacity ramp-up + enrollment/retention + relapse
churn.

**Conversion to work (used in model):**
- Parameter: `lag` (years from intervention start to first measurable effect)
  = base 2, sensitivity 1–5, consistent with the stated 1–3 year measurable
  window. `ramp` (rate of treatment-coverage expansion) = base 0.5/yr,
  sensitivity 0.2–1.0. Source: Exchange 3.
- Constraint: the strategy model is evaluated over a 5-year horizon; the
  model's "first measurable change" (year the uncontrolled-use fraction first
  drops below baseline) must fall within 1–3 years to be consistent with the
  expert's observed lag. The base case (lag=2) yields first measurable change
  in year 3, within the stated window; lag≥5 fails it. Source: Exchange 3.
- Parameter: `horizon = 5` years, matching the "full effect by ~5 years"
  upper bound. Source: Exchange 3.

## Where the values live
All three exchanges' values enter `code/model.py` as named parameters
(`place_type` prior in origin ranking; `treat_rate`, `enforcement` and the
backfire term in `strategy()`; `lag`, `ramp`, `horizon` in `strategy()`).
The Part-3 sweep over `RAMP`, `LAG`, `TREAT`, `ENF` (logs/model_sweep.log)
tests exactly the bounds the replies support. No expert sentence appears in
solution.json; only the parameters, constraints, and their tested outcomes
are reported there, in the model's own formulation.
