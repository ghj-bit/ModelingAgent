# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — Problem 2021_C (Vespa mandarinia report triage)

Ten exchanges, one question each, in order. For each: the question, the reply
(summarized), and the concrete change it caused in the work (parameter,
equation, decision rule, or test).

## Exchange 1 — queen dispersal distance
- **Q:** How far would a queen typically fly to found a new colony?
- **A (summarized):** About 30 km (20–40 km; most daughters much closer to the
  parent nest).
- **Used in:** `spread_model.py` — daughter-nest distance
  d ~ Uniform(0, D) with founding rate mu·exp(−d/D); D = 30 km is the
  dispersal kernel scale. Interval: the 20–40 km band is the model's domain of
  validity for the spatial spread component.
- **Source:** exchange 1 (confirms the problem statement's 30 km figure).

## Exchange 2 — what makes a wasted trip
- **Q:** Which reports are most often wasted trips?
- **A (summarized):** No usable photo / blurry or distant photos / flying-only
  shots; generic notes with no size, color or location detail; locations far
  from the known area; long lag between detection and submission. Positives
  cluster in clear close-up photos plus distinctive descriptions.
- **Used in:** feature design in `build_features.py` (image count/quality
  proxies, keyword families, `km_to_first_pos`, `det_sub_gap_days`) and the
  prioritization decision rule (rank by P(positive), tie-break recency).
  The three strongest model coefficients (km_to_first_pos, image presence,
  evidence keywords) match this qualitative ordering.
- **Source:** exchange 2.

## Exchange 3 — field effort per report
- **Q:** How much field effort does one investigation take?
- **A (summarized):** 2–4 person-hours nearby, up to a full day if remote.
- **Used in:** `prioritization_value.py` — cost per report
  h(km) = 2.0 + 0.02·km_to_first_pos person-hours (2 h at 0 km ≈ nearby;
  8 h at 300 km ≈ full day for a remote site). The budget sweep (8–168 h) is
  expressed in staff-days of this unit.
- **Source:** exchange 3.

## Exchange 4 — follow-up latency
- **Q:** How long before a new report gets a follow-up?
- **A (summarized):** Days to ~2 weeks; high-quality reports within 1–2 days
  in season; low-priority ones may wait weeks or never.
- **Used in:** (a) the update-cadence rule in `eradication_rule.py` —
  retrain at least every 4 weeks and immediately when the weekly positive
  fraction shifts by more than its Wilson half-width; (b) the deployment
  probability d (fraction of reports actually followed up) in the
  eradication computation, swept over 0.10–0.30 to reflect that only a
  minority of reports get field follow-up.
- **Source:** exchange 4.

## Exchange 5 — last confirmed detection (background)
- **Q:** When did the last confirmed PNW sighting turn out a dead end?
- **A (summarized):** No reliable in-dataset date; background only: the last
  confirmed WA detection was fall 2021, eradication declared 2024.
- **Used in:** none quantitatively — explicitly treated as out-of-dataset
  background. Recorded here so the boundary of the data's validity
  (through Oct 2020) is visible.
- **Source:** exchange 5 (declined as a data point).

## Exchange 6 — staffing
- **Q:** How many field staff can be assigned at once?
- **A (summarized):** A handful, roughly 2–6, scaling seasonally.
- **Used in:** `prioritization_value.py` — the 168 h budget = 21 staff-days
  ≈ 2–6 staff working ~1–2 weeks, i.e. the top of the plausible seasonal
  capacity; smaller budgets (8–48 h) are the normal state.
- **Source:** exchange 6.

## Exchange 7 — busy-week report volume
- **Q:** How many reports in a busy late-summer week?
- **A (summarized):** Tens per week, with spikes after media coverage; the
  dataset itself is the better guide (4,440 total).
- **Used in:** the fitted weekly Poisson rate (120.4 reports/week average,
  peak 350/week in August) supersedes the verbal estimate; the spike-after-
  -media mechanism is encoded as the time-varying intensity in `report_flow.py`.
- **Source:** exchange 7 + dataset.

## Exchange 8 — seasonal peak
- **Q:** In what month do most reports arrive?
- **A (summarized):** Peak August–September, tapering by October.
- **Used in:** validated by the dataset (August = 1,440 submissions, the
  maximum); the sinusoidal season term in the Poisson GLM (`report_flow.py`)
  and the peak-rate multiplier (×3) in `eradication_rule.py` both use this.
- **Source:** exchange 8 + dataset.

## Exchange 9 — eradication confidence
- **Q:** What gives confidence the hornet is really gone?
- **A (summarized):** 3+ consecutive years of zero confirmed detections
  **under sustained surveillance** (trapping and reporting at normal or higher
  intensity); absence only counts if searching did not drop.
- **Used in:** `eradication_rule.py` — the formal rule: under continued peak
  surveillance (R = 330 reports/week, p = 0.0067 positive fraction,
  d = 0.15 deployment), a zero-positive detection window of ≥ 9 weeks has
  P(0) ≤ 0.05 if the pest is still present, so observing such a window is
  95%-level evidence of absence; and 3 consecutive clean peak seasons
  (each with q ≈ 0.013 zero-season probability) drives the false-eradication
  error to ≤ 0.05³-scale. The rule explicitly conditions on surveillance
  level, per the reply.
- **Source:** exchange 9.

## Exchange 10 — new vs old reports
- **Q:** Do teams investigate newer reports first or older ones first?
- **A (summarized):** Newer first, weighted by likelihood; fresh high-quality
  reports near the detection area within 1–2 days; old reports only if
  resources allow or if they cluster.
- **Used in:** `prioritization_value.py` — recency-only ranking is the
  benchmark policy; the model-ranked policy (P(positive) first, recency as
  tie-break) beats it 28–16300× in expected confirmed positives per budget,
  which quantifies the value of likelihood-weighting on top of recency.
  The cluster exception (old reports at one site) is captured by the
  spatial-km feature rather than age alone.
- **Source:** exchange 10.

## What each exchange failed to change (for honesty)
- Exchange 5 contributed no parameter (out of dataset; recorded as boundary).
- Exchange 7's verbal range (20–100/week) was superseded by the fitted rate
  (120/week average) — the dataset, as the expert themselves suggested,
  wins.
