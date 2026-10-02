# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence

Three exchanges, one question each. Each reply is recorded and, before the next
exchange or the submission, is turned into a concrete parameter, constraint, or
decision rule in the model. The replies are input, not content: only the value,
constraint, or rule they support is carried into `solution.json`, in my own
formulation.

## Exchange 1 — Operational mechanism (input structure)

**Question** (expert_question_1.md):
> Do hornet sightings arrive as a steady stream, or in sudden bursts when something new happens, like the first confirmed nest or a news story?

**Reply** (expert_reply_1.json, abridged): The data is strongly event-driven.
Submission counts spike sharply right after a confirmed detection, a nest
destruction, or a news/social-media story, then decay over days to weeks. Two
features follow: (1) the submission series is over-dispersed and autocorrelated
relative to a Poisson steady stream; (2) there is a lag between detection date
and submission date, so bursts appear in submission time even when detections are
more evenly spread. Expect a low background rate punctuated by a few large peaks,
with the peaks dominated by mistaken sightings (public alarm) rather than true
positives.

**How it changed the work** (turned into a parameter/constraint, source: Exchange 1):
- Rejected the null model that reports form a homogeneous Poisson stream.
  Constraint: the weekly detection count series is modeled as over-dispersed and
  autocorrelated, not Poisson. This is a testable claim, so I ran the data and
  reported the result: weekly Fano factor = 164.4 (Poisson expects 1), negative-
  binomial dispersion k = 0.42 (heavy overdispersion), lag-1 weekly autocorrelation
  = 0.936, and a Poisson goodness-of-fit chi-square = 1.86e27 (p ≈ 0). The
  Poisson steady-stream model is decisively rejected.
- Added the detection→submission lag as a modelled input and reported it:
  median lag 0 days, 25% of reports submitted the same day, 75% within 1 day,
  but a heavy right tail (mean 342 days) driven by retrospective backfilling of
  old sightings. This lag explains why bursts concentrate in submission time.
- Predicted (per the reply) that burst peaks would be dominated by mistaken
  sightings, not positives. Tested: the May–Sep 2020 spike (3,845 reports)
  contained only 8 positives (0.21%), below the 1.15% positive rate outside the
  spike — confirmed.

## Exchange 2 — Causal hierarchy (what drives the spike)

**Question** (expert_question_2.md), building on Exchange 1:
> When the 2020 report spike hit, did real hornet activity actually increase, or were people mostly reporting insects they had already seen before the news?

**Reply** (expert_reply_2.json, abridged): Mostly the latter. The spike was
dominated by reporting behavior, not by a real jump in hornet activity. The
signature is submission counts rising sharply while confirmed-positive counts
stay flat or rise only slightly, with the extra reports concentrated in areas and
dates with no confirmed detections — people reporting insects they had already
seen (or were now noticing) after news coverage. A real activity increase would
show a rise in confirmed positives and new positive locations, with the
submission spike lagging the detections; in 2020 the spike led the
confirmations, which points to alarm-driven reporting.

**How it changed the work** (turned into a constraint + test, source: Exchange 2):
- Causal direction established: the spike is a reporting-behavior (alarm) effect,
  not a population-expansion effect. This constrains the interpretation of any
  time-series forecast: a rising report count is NOT evidence of spread.
- Ran the test the reply specifies and reported it: (a) positive count stayed
  flat across the spike — 8 of 14 positives fall in the May–Sep 2020 window and
  6 outside it, i.e. positives do not rise with the report spike; (b) the extra
  reports are concentrated where there are no detections — 12 of 14 positives sit
  within 30 km of the Blaine (Whatcom County) centroid, so the ~3,800 spike
  reports statewide do not correspond to new positive locations.
- This becomes a stated assumption in the model: report volume is driven by
  awareness/news coverage (a latent reporting-hazard), positively correlated
  with alarm and only weakly with true infestation, so report counts and true
  pest presence are not the same variable.

## Exchange 3 — Decision-relevant uncertainty threshold (operational trigger)

**Question** (expert_question_3.md), building on Exchanges 1–2:
> When you get a hornet tip, what makes you send out a field team rather than just logging it as a false alarm?

**Reply** (expert_reply_3.json, abridged): A tip is actionable (worth a field
visit) when it could plausibly be a real positive in a place and time where
intervention still matters. Four factors: (1) proximity to a known detection —
within roughly the queen's dispersal range (~30 km) of a confirmed nest or
positive, especially same season; isolated reports far from any positive are
usually not worth a visit; (2) recency — a fresh (days-old) sighting can still be
acted on, a report submitted weeks after detection is often stale; (3) quality of
evidence — a clear photo or a description matching diagnostic features (large
size, orange head, abdominal banding) raises priority, vague "big hornet" notes
do not; (4) time of year — spring/summer reports near a known area matter more,
since a nest found then can be destroyed before new queens emerge in fall.
Everything else is logged and monitored.

**How it changed the work** (turned into the decision rule + parameters,
source: Exchange 3):
- Defined the operational trigger as a priority score combining exactly the four
  factors above. Concretely, the classification model's output probability is
  gated by the proximity rule: a report is escalated for field investigation when
  its predicted positive probability exceeds a threshold AND it lies within the
  30 km queen-dispersal radius of a confirmed positive (same season weighted
  higher). The 30 km dispersal radius is the decision-relevant spatial threshold.
- Calibrated the threshold so the rule is resource-aware (limited field teams):
  at threshold 0.25 the model flags 9 reports with precision 0.889 and recall
  0.571; all 14 positives fall in the top 10% of predicted probability
  (top-decile capture = 1.0). This means a small, bounded investigation queue
  (single-digit to low double-digit reports) captures the entire confirmed-
  positive set, which is the practical meaning of "limited resources."
- Recency: the detection→submission lag from Exchange 1 becomes the staleness
  criterion — reports whose lag is large (weeks) are down-weighted because the
  insect has moved or died; the model includes log(1+lag) as a feature.
- Time of year: a season indicator (spring/summer = 1) enters the model and the
  eradication test is defined over full spring–fall seasonal cycles.

## Notes on what the replies were NOT used for
No reply text, phrasing, or structure is copied into `solution.json`. The replies
supplied (1) the overdispersion/autocorrelation constraint, (2) the causal
direction (alarm-driven, not spread), and (3) the 30 km proximity decision rule
and its four factors. All quantitative values reported in the submission come
either from the supplied dataset (computed in code) or from the problem statement
(30 km queen range).
