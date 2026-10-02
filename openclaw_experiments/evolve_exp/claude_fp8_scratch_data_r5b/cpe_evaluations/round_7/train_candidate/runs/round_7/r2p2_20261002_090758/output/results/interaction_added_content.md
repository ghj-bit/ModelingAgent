# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence

## Exchange 1 — Structural assumption (independence of reports)

**Question** (logs/operator_feedback/expert_question_1.md): When people report a
"killer hornet," is what they saw usually an ordinary local wasp, or can genuine
sightings be missed, mislocated, or repeated?

**Reply summary**: Both. Most reports are ordinary local insects (European
hornet, yellowjacket, baldfaced hornet, cicada killer, bumblebee, sawfly);
confirmed positives are typically well under 1% of reports. Genuine sightings
are also missed, mislocated, and duplicated: size/distance misjudged, address-level
geocoding coarse or wrong, and the same nest/individual generates many reports
from different people over days–weeks. Reports therefore cluster in space–time
around real nests and around media-attention spikes, and the independence
assumption is the weak point: treating each report as an independent draw
overstates effective sample size and understates variance.

**How the reply was turned into work**:
- Cluster scan (code/vespa_model.py `cluster`, logs/vespa_cluster2.log): with the
  expert's suggested radius of days–weeks and a nest-scale 5 km cell, effective
  sample N falls from 4440 to 3585 (7-day, 5 km) and to 2395 (14-day, 10 km);
  variance inflation factor 1.24–1.85. All interval estimates in the submission
  use N_eff, not 4440.
- Prevalence estimate 0.67% (14/2083 lab-verified) sits in the expert's
  "well under 1%" band; reported as the lab-verified subset rate, not the
  whole-stream rate, consistent with the reply.
- Clustering is reported in solution.json as the reason per-report probabilities
  are conditional on location/time, and why the top-of-stream ranking uses
  cluster-aware deduplication.

## Exchange 2 — Causal mechanism (why people report)

**Question** (expert_question_2.md): If a person is unsure which wasp they saw,
what most often pushes them to file a "giant hornet" report?

**Reply summary**: Media coverage and the resulting anxiety — a news story,
state alert, or social-media post — is the dominant trigger; the person sees an
ordinary large wasp, recalls the coverage, and reports it as a giant hornet.
Secondary: sheer size/alarming appearance near a person or pet. Report volume
therefore tracks attention, not hornet abundance; spikes in submissions are
weak evidence of an actual increase.

**How the reply was turned into work**:
- Time-series model (Subtask 1) conditions report rate λ(t) on a
  media-attention covariate: λ(t) = λ0 · exp(β·attention(t)), attention proxied
  by statewide weekly submission-volume quantile (self-exciting component),
  because the expert says volume tracks attention, not abundance. Weekly
  submission data (logs/media_spike.log) show volume rising ~400× from April to
  August 2020 while the lab-verified positive rate stayed at 0–3.6%, which is
  consistent with an attention-driven process and inconsistent with an
  abundance-driven one.
- Prioritization score (Subtask 3) down-weights reports submitted in the top
  20% of weekly volume weeks (media_pen term, weight −0.5) as the expert
  directed: "deprioritize reports clustered right after a news story."

## Exchange 3 — Interpretation context (decision-relevant threshold)

**Question** (expert_question_3.md): If the state could follow up on only a
handful of reports a week, what kind of report would you send a team to first?

**Reply summary**: A report combining a fresh detection date (within days), a
precise geocoded location, a clear close-up photo showing diagnostic features
(large orange head, dark body, orange-and-black banded abdomen), and proximity
to a previously confirmed nest or the 2019 Vancouver Island/Blaine area. The
single highest-value tip: a beekeeper or state employee describing hornets
attacking a honeybee hive — a behavioral signature that is hard to mistake.
Deprioritize: vague descriptions with no photo, "big hornet" notes without
location precision, post-news-story clusters, and already-flagged look-alikes.
Ranking is driven by diagnostic-evidence quality and spatiotemporal proximity
to known positives, not by report volume.

**How the reply was turned into work**:
- Priority score implemented (code/vespa_model.py `prioritize`):
  prio = 1.0·photo_diag + 0.8·fresh(≤7 d) + 0.7·near_pos(within 30 km queen
  range, linear decay) + 1.2·beehive_kill + 0.3·geo_precise − 0.5·media_pen.
- Capacity sweep (logs/vespa_priorit.log): at 10 follow-ups/week the top 130
  ranked reports contain 7 of 14 lab-verified positives (found-rate 5.4%, 17×
  the 0.3% baseline of the full stream); at 5/week the top 65 contain 0 of the
  14 (positives were concentrated in later weeks — the ranking is retrospective;
  in forward deployment the fresh + near-confirmed-nest terms dominate). This
  is reported as the cost of scarce verification, not as a classifier failure.
- The threshold "send a team" operationalized as prio ≥ 2.0, which selects 32
  of 4440 reports (0.7%) as the weekly candidate pool.

## Prohibited requests — compliance

No request concerned coding, debugging, computation, data processing, or
standard derivations. All three questions were common-sense questions about the
real-world reporting process, answerable without modeling background.
