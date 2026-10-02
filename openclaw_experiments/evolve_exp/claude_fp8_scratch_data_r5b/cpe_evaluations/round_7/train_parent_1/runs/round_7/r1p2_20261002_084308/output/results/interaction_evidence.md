# Interaction Evidence — 2021_C (Vespa mandarinia report triage)

Three exchanges, one question each, in the order below. For each: the question,
the expert reply (verbatim), and how the reply was turned into work (parameter,
constraint, equation or decision rule, with the executed result).

---

## Exchange 1 — data provenance

**Question** (`expert_question_1.md`):
> In this state hornet-reporting program, what is the main reason some public
> reports arrive with no photo or video, or with the sighting date left blank or
> clearly wrong? Are those incomplete reports systematically different from
> complete ones, so that using only the labeled reports would skew the picture of
> what the public actually sees?

**Reply** (summarized; verbatim in `expert_reply_1.json`): reporting is
voluntary and low-effort; missing media/dates track reporter diligence and
channel (phone/email transcribed by staff), not the insect. Incomplete reports
are systematically different: photo-bearing reports skew toward engaged,
closer, more urban/suburban reporters with settled or dead specimens; blank or
vague dates cluster with casual retrospective reports. Restricting to labeled
reports over-represents well-documented submissions and skews the picture
geographically, temporally, and by confidence.

**Turned into work** (executed, `logs/probe_gap.log`, `code/model.py`):
- Quantified the gap the reply described: among the 2,083 *labeled* reports
  98.6% carry a file; among the 2,342 *Unverified* reports only 2.9% do. The
  labeling pipeline itself is media-gated: no photo → not lab-verified.
- Consequence imposed on the classifier: it may be fit only on the labeled set
  (the lab-verified sample), and its predicted probability P(positive) is
  interpreted as the probability *conditional on the report being lab-verifiable*
  (i.e. carrying an attachment or a specimen). This is stated as an explicit
  assumption and a bias in the submission (Section 2 of solution.json): the
  score transfers to attachment-less Unverified reports only to the extent that
  note text, date and location features dominate; the model therefore includes
  `n_files`, `n_images`, `n_video` and `has_pdf/zip/doc` as features so that
  the attachment signal is modeled rather than assumed away.
- Date handling rule fixed by the reply ("dates entered loosely or defaulted"):
  Excel serial-0 values ("12/30/1899", 8 records), `<Null>` (3), and out-of-range
  years (1980, 1600, 515, 1200; 5 more) are treated as *unreported* (NaT), not
  parsed — 72 records in total — and a `month_missing` feature is added so the
  classifier can use the gap instead of inheriting a wrong season.

---

## Exchange 2 — key structural assumption (independence)

**Question** (`expert_question_2.md`):
> The confirmed giant hornet reports in this data all cluster in a few places in
> western Washington, while thousands of other reports come from all over the
> state. From what you know of how a newly introduced hornet colony spreads, is
> it fair to treat each new report as an independent event, or do reports tend to
> arrive in bursts from the same place?

**Reply** (summarized; verbatim in `expert_reply_2.json`): not independent for
confirmed reports. Queens disperse on the order of tens of km, workers forage
within a few km of the nest, so confirmed detections cluster tightly around a
few colonies; reports arrive in spatial and temporal bursts, often the same nest,
foragers, or even the same reporter/neighbors. Independence is poor for the
positives and only roughly acceptable for the background of negatives.

**Turned into work** (executed, `logs/model.log`, Part C of `code/model.py`):
- The spread analysis was **not** built as a homogeneous Poisson process over
  individual reports (that assumption is rejected). Instead the spread is
  modeled as a *cluster* process: two colony-era clusters (2019 core, 2020
  expansion), with the queen-range radius **R = 30 km** taken from the problem
  statement as the dispersion scale, and reported as nearest-neighbor distances
  between confirmed reports.
- Results: 14 confirmed reports; median pairwise distance 9.7 km; **all 9 of
  the 2020 confirmed reports fall within 30 km of the 2019 core** (fraction 1.0,
  Wilson 95% CI [0.701, 1.0]); median distance from a 2020 confirmation to the
  nearest 2019 confirmation is 8.3 km. This is the quantitative basis for the
  claim "the pest has not spread beyond the founding area within the observation
  window" (Part 1 of the submission).
- The independence assumption was *checked* where the reply says it roughly
  holds — the 2020 negative (background) reports — with a quadrant-occupancy
  test against a binomial(null) split at the state median: quadrant counts
  528/528/488/488 out of 2,032, p = 0.318 → independence is **not** rejected
  for the background, consistent with the expert's assessment, so the negative
  reports may be pooled as a background rate without a cluster correction.

---

## Exchange 3 — interpretation context (decision threshold)

**Question** (`expert_question_3.md`):
> If a report gets a high suspicion score from our model, what would you actually
> do differently with it, and at what level of certainty would you decide not to
> send anyone out to check it?

**Reply** (summarized; verbatim in `expert_reply_3.json`): a high score changes
*when and how* you investigate, not whether a report is "true" — escalate ahead
of the queue, route to the nearest inspector, and collapse clustered high-score
reports into one team dispatch. The threshold should be set *low*: a missed
nest is far costlier than a wasted trip, so tolerate many false alarms;
investigate a substantial fraction of the highest-scoring reports, not only
near-certain ones. Exact numbers are an empirical judgment.

**Turned into work** (executed, `logs/model.log`, Part B of `code/model.py`):
- Operationalized as an explicit cost-benefit rule rather than a fixed
  probability cut: investigating the top *t* scored reports has expected utility
  `U(t) = d · Σ_{i≤t} p_i − c·t` (expected damage averted minus visit cost),
  with visit cost **c** and missed-nest cost **d** as the free parameters.
  Per the reply, the operating point is chosen to tolerate false alarms
  (d ≫ c), and a sweep over `c ∈ {0.5,1,2,5}` × `d ∈ {5,10,20}` (relative
  units) was executed: the optimal visit count ranges from ~975 to ~1,425 of
  the 2,357 unverified/unprocessed reports (41–60%), i.e. "a substantial
  fraction of the highest-scoring reports", matching the expert's operating
  guidance. Default `c = 1, d = 10` → visit **1,270** reports (54%),
  investigate-all-above `p* ≈ 0.101`.
- The cluster-collapse rule from the reply is implemented as the dispatch
  recommendation: the 1,270 are not 1,270 separate trips; reports within
  30 km of each other in the same month are grouped, so the dispatch count is
  the number of (30 km × month) clusters among them, which the model reports
  alongside the visit count.
- The "not send anyone out" region is defined by the same rule: a report is
  left alone when `p_i < p*` *and* it lies outside any high-score cluster —
  exactly the "more likely a look-alike and not clustered" case the expert
  describes.

---

## Compliance notes

- No reply text was copied into `solution.json`; the values that travel are
  `R = 30 km` (problem statement), the cluster statistic (9/9 within 30 km,
  CI [0.701, 1.0]), the utility rule `U(t) = d·Σp − c·t`, the sweep result
  (t* ≈ 975–1,425; 41–60%), and the default operating point (t* = 1,270,
  p* ≈ 0.101).
- All three exchanges produced a parameter, constraint or decision rule that was
  executed; none is prose-only.
