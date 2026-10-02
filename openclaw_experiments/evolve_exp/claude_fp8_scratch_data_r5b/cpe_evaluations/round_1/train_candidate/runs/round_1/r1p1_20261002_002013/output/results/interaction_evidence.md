# Interaction evidence — expert exchanges (2021 MCM Problem C)

Three exchanges, one question each, sequenced mechanism → constraints →
interpretation. The reply of each exchange is recorded here as evidence and
was turned into concrete modeling work as described below. The scored
submission (solution.json) does not restate the exchange texts.

## Exchange 1 (mechanism)

Question file: `logs/operator_feedback/expert_question_1.md`
Request/reply: `expert_request_1.json` / `expert_reply_1.json`

- Question: when the state is deciding whether to send an inspector, which
  single feature of a report most tells a real Vespa mandarinia from a
  mistaken one?
- Reply (paraphrased as evidence): a report describing a physical specimen —
  its size, color pattern, or the captured/dead body itself — carries far
  more weight than anything else; a photo alone is often of the wrong insect
  because the reporter does not know what they saw.
- How it became work: this is the mechanism-level input that selected the
  dominant feature of the triage model. `code/model_classify.py` builds the
  `SpecimenMention` feature (Notes mentioning a captured/killed/sent/
  collected specimen) and uses the logistic model
  P(positive | HasImage, SpecimenMention, ActiveSeason, RecentLag) with
  SpecimenMention as the signal the expert identified as decisive. The
  data confirm it is the only feature whose effect interval excludes 1
  (OR 2.945, 95% CI [1.079, 8.040], computed on the whole processed pool,
  n=2,083). The reply also justifies the two-tier triage in Task 3: reports
  with a specimen mention get the first field response, photo-only reports
  get the second tier, matching the expert's ranking of what an inspector
  can verify.

## Exchange 2 (constraints)

Question file: `logs/operator_feedback/expert_question_2.md`
Request/reply: `expert_request_2.json` / `expert_reply_2.json`

- Question: how many reports per week can the state actually investigate?
- Reply (paraphrased as evidence): not hundreds — realistically a few up to a
  few dozen a week, depending on the season.
- How it became work: this fixed the operating scale of the
  prioritization. The dataset contains no capacity figure, so
  `code/model_classify.py` reports the operating characteristics of the
  triage ranker over k = 10, 25, 50, 100, 200, 500 (positives found,
  Wilson-CI positive rate, expected positives, recall@k) as a sensitivity
  range spanning "a few" to "a few dozen per week" rather than assuming one
  point capacity. The interval over which this input holds is the whole
  dataset window (2019-07 .. 2020-12), i.e. the season the state was
  running the full reporting campaign.

## Exchange 3 (interpretation)

Question file: `logs/operator_feedback/expert_question_3.md`
Request/reply: `expert_request_3.json` / `expert_reply_3.json`

- Question: how long with no confirmed reports could a state be confident
  the pest was really gone?
- Reply (paraphrased as evidence): winter silence means nothing — the queens
  are underground and nobody sees them; the meaningful measure is full
  active seasons (spring through fall) with no confirmed positives, and you
  would want at least two of them in a row to be confident.
- How it became work: this supplied both the time window used in every
  seasonal calculation and the structure of the Task 5 decision rule.
  `code/common.py` defines the active season as May–October; the
  eradication analysis in `code/model_update_eradication.py` counts clean
  *active* seasons, not calendar months, and its conclusion rule —
  "two consecutive clean active seasons under maintained surveillance" —
  comes directly from this exchange. The binomial detection grid
  C(m) = 1 − ((1 − π)^λ)^m quantifies how strong that rule is across
  detection probabilities π ∈ [0.1, 0.9] and seasonal establishment rates
  λ ∈ [1, 10]; the interval over which the exchange's input holds is the
  biological cycle (annual queen overwintering / adult activity), which the
  model treats as fixed.

## Summary of inputs carried into the models

| Input | Source | Where used |
|---|---|---|
| Specimen mention = dominant, inspector-verifiable signal | Exchange 1 | `SpecimenMention` feature, tier order in Tasks 2–3 |
| Capacity = "a few to a few dozen per week", not hundreds | Exchange 2 | k-sensitivity grid k=10..500 in Task 3 |
| Confidence = ≥2 full clean active seasons, not calendar gaps | Exchange 3 | May–Oct season window everywhere; Task 5 rule C(m), m≥2 |
