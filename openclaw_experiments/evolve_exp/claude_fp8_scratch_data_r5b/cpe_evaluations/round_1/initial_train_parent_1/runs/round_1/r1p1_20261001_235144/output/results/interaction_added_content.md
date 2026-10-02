# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — Problem 2021_C (Vespa mandarinia triage)

Three exchanges, fixed. Files `expert_question_N.md`, `expert_request_N.json`,
`expert_reply_N.json` are controller-owned copies in
`logs/operator_feedback/`.

## Exchange 1

**Question:** People report large wasps to hornet-hotline sites. Which single
detail in a written report is the most reliable signal that it may really be
the Asian giant hornet, and why?

**Reply (summary):** A report of a large wasp attacking or entering a
honeybee hive — the "deadly embrace" predation behavior — is the most
diagnostic single detail. Mistaken sightings are usually large native wasps
(yellowjackets, bald-faced hornets, paper wasps) seen at flowers or garbage;
honeybee predation is a behavior few local species perform, so tying the
insect to hive predation is more diagnostic than size or color.

**How the reply changed the work:** the candidate feature list for the
classifier was built around this behavior class. Features
`f_bee_predation` (report links the insect to bees/hive + attack verb, either
word order, within 160 chars), `f_hive_context` (any hive/honeybee mention)
were defined directly from this guidance. The study (`logs/feature_study.log`)
then showed what the data supports: no positive report actually describes
hive predation (0/14 positives, 12/2069 negatives), while 28 negatives do —
so the expert-identified signal is *specific but absent in the labeled data*.
It was kept in the model with the honest consequence: its posterior
probability is pinned near the prior (p ≈ 0.036, posterior a=1, b=27), i.e.
the model cannot confirm it from this data, and the report must say so.
Interval over which the constraint holds: the 2019-09 to 2020-10 report
stream in this dataset.

## Exchange 2

**Question:** In Washington, are public sightings of giant hornets
concentrated in particular counties or regions, or do they come in evenly
from all over the state?

**Reply (summary):** Public reports come from all over the state (volume
tracks population, densest in the Puget Sound corridor), but confirmed
positives are strongly concentrated in the northwest corner — Whatcom
County (Blaine, Birch Bay, Custer area) near the Canadian border, a smaller
number in adjacent Skagit County, plus one 2019 detection on Vancouver
Island. That is the only region with reproducing colonies.

**How the reply changed the work:** this became the spatial prior for the
point-process model. Concretely:
- the Poisson study window was restricted to the NW corner (350 km box
  around the positives; validated against the data: 14/14 confirmed
  positives lie at lat ≥ 48.6, lon ≤ −121.5, while only 512/4440 reports do);
- the homogeneous background rate was calibrated against the 2069 negative
  reports (the statewide reporting stream) rather than assumed, so the
  model is a *clump + diffuse background* — exactly the structure the
  expert described;
- the prioritization rule uses this: a report inside the clump region gets a
  multiplicative spatial score that no report outside it can match, which
  matches the expert's claim that region — not report volume — carries the
  signal.

## Exchange 3

**Question:** How many lab-confirmed Asian giant hornets would you expect to
find by chance in a year with no hornets actually present in Washington?

**Reply (summary):** Zero, or effectively zero. Lab confirmation requires
physical examination (or a clear photo) by an entomologist identifying the
species by morphology; misidentifying another species as Vespa mandarinia at
that stage is rare. Even a single confirmed positive is therefore a
meaningful signal, not background noise.

**How the reply changed the work:** this set the null hypothesis for the
eradication test. H0 of the SPRT is p0 = 0.001 (a residual chance
false-positive rate for a confirmed ID, chosen as a small positive value to
avoid a degenerate log-likelihood, and an upper envelope consistent with
"essentially zero"). Because p0 is so small, the decision rules simplify:
- any single new confirmed positive is treated as a signal of an active
  colony (the reply's "not background noise"), i.e. the test declares
  ACTIVE on the first positive;
- the evidence required to *declare eradication* is a run of new reports
  with zero confirmed positives, quantified by the SPRT (α = 0.05,
  β = 0.10) and a fixed-horizon Bayes factor against H1: a persistent
  colony yields p1 ≈ 7/2700 ≈ 0.0026 positives among new reports
  (14 confirmed over two seasons vs ~2700 seasonal reports). The model
  computes: expected SPRT stop after ~1400 all-negative reports;
  BF01(0 positives, n = 1000) ≈ 4.9, ≈ 24 at n = 2000. So the evidence for
  eradication is a full season (~1000–2000 reports) with zero confirmations,
  not a short silence.
