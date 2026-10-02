# Expert Interaction Evidence

Three exchanges, each one question; every reply was converted into a model
parameter, feature, or decision rule before the next exchange.

## Exchange 1

- **Question** (`logs/operator_feedback/expert_question_1.md`): When your lab
  gets a dead hornet for testing, which findings settle it as NOT Vespa
  mandarinia right away, before you even look at size?
- **Reply** (`expert_reply_1.json`): the decisive immediate rule-outs are
  structural, not size-based: a dark/black head (V. mandarinia has a large
  bright orange-yellow head), a uniformly dark abdomen or narrow yellow bands
  on black (yellowjacket pattern instead of broad orange-yellow bands), a
  slender elongated body (paper wasp / mud dauber instead of bulky robust
  form), clear or dark wings (instead of amber-tinted), or a non-wasp insect
  at all (hairy bee, hoverfly, moth, beetle). Size is confirmatory, not the
  first filter.
- **How the reply became work**: this set the feature hierarchy of the
  misclassification model. Structural descriptors (color pattern, body form,
  wings) are the fields a lab checks first, so the model must separate reports
  that *contain* such descriptors from those that only assert "big". Because
  the dataset's free-text Notes rarely state color, the proxy used is
  `mentions_size` (numeric cm/mm/in or size words) plus `size_in` (extracted
  numeric length), and the lab's own confirmation practice — that only reports
  with a physical specimen or clear photo can be resolved — is represented by
  `has_photo`. The rule "size is confirmatory, not decisive" is encoded as a
  constraint: no size-only report profile is allowed to reach the top of the
  priority queue; size must act together with location/season/cluster. This is
  visible in the fitted model (`code/fit3.py`, `results/fit3.json`):
  `mentions_size` alone moves the predicted probability from 0.008% to 0.12%
  at the median 150 km distance, while only the combined profile
  (cluster + size + killed, 60 km, October) reaches 66.7%.

## Exchange 2

- **Question** (`expert_question_2.md`): When several large-insect sightings
  come in on the same week in one town, do you treat them as one event or
  separate cases?
- **Reply** (`expert_reply_2.json`): separate cases for classification (each
  report keeps its own reporter, photo, location, wording; merging would
  destroy the signal and inflate the confirmation rate) but one possible
  cluster for prioritization — multiple independent reports in one town in a
  short window are themselves evidence, because a single nest sends out many
  foragers. Practical rule: keep records separate, let spatio-temporal
  proximity enter as a feature (count of nearby reports in a short window).
- **How the reply became work**: implemented verbatim as two code paths.
  (a) The classifier treats every report as an independent row (no merging)
  and adds `cluster2w` = count of other reports within 25 km and +/-14 days
  (`code/classify_model_v2.py`). (b) Prioritization runs a separate
  town-scale cluster detector — single-linkage components linked by <=10 km
  and <=7 days, size >=3 (`code/cluster_v3.py`, `results/clusters_v3.json`):
  63 clusters covering 4167/4349 reports; 13 of the 14 confirmed detections
  fall inside clusters; the positive rate inside the top-10 clusters is
  0.707% (95% CI [0.377, 1.206]) vs 0.444% outside, and the top-10 clusters
  capture 13/14 confirmed detections while using only 88.9% of all reports —
  i.e. the cluster unit, not the individual report, is the prioritization
  object. The windows (25 km / 14 days in the feature; 10 km / 7 days for
  cluster definition) follow the "same town, same week" scale the reply gave.

## Exchange 3

- **Question** (`expert_question_3.md`): If no Asian giant hornet has been
  confirmed in a region for a full year of watching, would you call it
  eradicated?
- **Reply** (`expert_reply_3.json`): no — a quiet year is absence of
  confirmed sightings, not proof of eradication, because detection is
  imperfect (reports bias toward populated areas; low-density rural/forested
  populations can persist undetected), the life cycle hides the insect
  (queens overwinter in soil; early-season colonies are small), and absence of
  detections only supports eradication if surveillance was adequate and
  spatially representative. Stronger claim: multiple consecutive years
  (commonly about 3) of zero confirmed detections under sustained, adequate
  surveillance, plus no new nests or overwintering queens found; even then it
  is probabilistic.
- **How the reply became work**: the eradication criterion in the solution is
  exactly this compound rule (3 years, adequate surveillance, no new nests or
  overwintering queens), and the strength of the evidence was quantified in
  `code/analysis2.py`: a Bayesian comparison of H0 (eradicated,
  confirmed-detection rate 0) vs H1 (active, Gamma(1, 1/2) prior, mean 2
  confirmed/month, matching the observed 2020 pace) with prior odds 1:1.
  Zero confirmed detections for T months gives posterior P(active) = 0.0117
  at T=6, 0.0032 at T=12, 0.0008 at T=24, 0.00038 at T=36 — a single quiet
  year leaves P(active) ~ 0.3%, supporting the expert's "not eradicated"
  answer numerically, while three quiet years push it below 0.05%. The
  surveillance-adequacy proxy computed from the data: 2020 monthly report
  volume (mean 422, median 252, max 1343) and 100% geocoding of reports; the
  model's stated limitation is that public reporting is denser in populated
  coastal areas, so the zero-confirmation evidence applies to monitored areas
  and must be supplemented with trapping in rural/forested terrain.
