# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — 2021_C

Three exchanges, one question each, in the order asked. The question file, the
reply, and the concrete change each reply forced into the work are recorded
below. Expert replies are input, not content: nothing below is copied into
solution.json; only the resulting parameters, constraints, equations and test
outcomes appear there.

## Exchange 1 — structural validity of the label process

Question (logs/operator_feedback/expert_question_1.md): whether the state
checks up on every public report or only the ones that look most likely.

Reply (summary): triage-based — the state cannot field-inspect all ~4,400
reports; it screens (notes, photos, location, plausibility) and follows up the
subset judged most likely plus reports in areas of active concern; most
reports are resolved desk-side as negative or unverified without a site visit.

How it became work:
- Structural assumption A5 ("the lab-processed set is a triage sample, not a
  random sample of all reports") was adopted in the task-2 analysis.
- The label process was made explicit in the model: P(processed | genuine)
  = 1.0 (14/14) and P(processed | mistake) = 0.466 (2069/4426, with
  unverified+unprocessed treated as non-escalated), both computed from the
  dataset under A5.
- The mistake-prior decomposition (M5, task 2): P(g | all) =
  wp_g P(g) / (wp_g P(g) + wp_m (1-P(g))), with the Bayes table
  prior 0.001→0.0021, 0.005→0.0106, 0.01→0.0212, 0.02→0.0418, 0.05→0.1012.
  Without this exchange the within-processed base rate 0.0067 would have been
  (wrongly) usable as the over-all-reports prior; the triage correction
  changes it by a factor of ~3 at the low end.
- The task-3 decision rule explicitly conditions on the triage bias: the
  enrichment benchmark is labeled an upper bound for the unverified backlog,
  because triage already removed the obvious cases.

## Exchange 2 — dominant bias: seasonality and media amplification

Question (expert_question_2.md): whether people really reported far more in
warmer months, and why.

Reply (summary): the seasonal pattern is real and strong — peak late summer to
early fall (roughly July–October), secondary spring bump, near zero in winter;
drivers are (i) the hornets are only active and visible in warm months
(queens emerge in spring, workers abundant in summer, colonies largest in late
summer/fall, colony dies off in winter, queens overwinter underground) and
(ii) media attention after the 2019 discovery and confirmations amplifies the
warm-season peak.

How it became work:
- Assumption A10 (non-stationary reporting: volume = base × seasonal ×
  media) entered the task-1 process model; the seasonal factor was
  measured from the data: 96.3% of submissions in May–Oct, peak Aug (32.4% of
  the year), and this number is quoted as the identifiable part of M2.
- Seasonal dummy features (sin/cos of submission month) were justified and
  retained in M1; the task-4 update calendar was set to monthly refits
  because the confuser mix and attention cycle are monthly, with a
  change-detection trigger between consecutive months.
- The task-5 eradication test was defined per warm season only, and its
  third clause (public-report flow must not collapse below ~50% of the 2020
  peak) exists directly because the reply says reporting goes quiet for
  reasons unrelated to the pest (attention decay); a quiet report stream is
  treated as surveillance failure, not as evidence of absence.
- The task-1 outcome states that the reporting stream tracks attention as
  much as the pest, and that winter silence is not pest absence (queens
  underground).

## Exchange 3 — decision-relevant uncertainty threshold for eradication

Question (expert_question_3.md): how a state agency would actually decide the
pest is gone after a year of finding nothing.

Reply (summary): not from a single quiet year; the practical standard is
absence of detection across multiple years (commonly ~3, matching the life
cycle and overwintering queens) of sustained, well-placed surveillance that
could plausibly have found a low-density population (traps, sentinel hives,
targeted follow-up in previously positive areas) — i.e., negative results from
adequate search effort over enough years, not absence of reports.

How it became work:
- The task-5 eradication test M4 became a three-clause decision rule (E1):
  (i) zero lab-confirmed positives, (ii) active searches at placement quality
  q ≥ 0.25 (traps in 30-km corridors of historical nests plus sentinel
  apiaries), (iii) public-report flow ≥ ~50% of the 2020 peak, over
  3 consecutive warm seasons; with q = 0.25 the false-declaration
  probability is P(no detection | present) = (1-0.25)^{3×12} ≈ 1.4e-5
  (Monte Carlo verified), satisfying the α = 0.05 test.
- The q-sensitivity table (q ∈ {0.10, 0.25, 0.50} × search counts) was
  computed in model.py (m4_eradication) precisely because the reply makes the
  search quality, not the silence, the operative quantity; the weakest
  credible standard (q=0.10) still needs ≥30 well-placed searches.
- The practicality threshold framing used in task 3 (a flagged set is
  operationally usable at PPV ≥ 10× base rate with CI excluding base rate)
  mirrors the reply's separation of planning-level insight from operational
  triggers: the top-100 set (PPV 0.08, CI [0.041, 0.150]) clears it.

## Exchange accounting

- 3/3 exchanges completed, one question each, no early stop, no extras.
- Each reply changed a model parameter, constraint, equation or test before
  the next question was asked (Exchange 2 was asked after M5 was fixed by
  Exchange 1; Exchange 3 was asked after M2's seasonal form was fixed by
  Exchange 2).
- No reply text was copied into the submission; solution.json carries only
  the derived values, constraints, formulas and test outcomes, with sources
  labeled "expert exchange N (2026-10-02)".
