# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction evidence: how each expert reply shaped the model

All ten exchanges are summarized below. No reply text is quoted verbatim in the submission; this file documents the mapping from reply to model element.

## Exchange 1 — first response to a report
- **Question:** When Washington officials get a public hornet sighting report, what do they typically do first — dispatch, request specimen/photo, or monitor?
- **Reply (summary):** Desk triage first: a state entomologist reviews photo/specimen/description and assigns positive/negative/unverified before any field resources are committed; only evidence-bearing reports trigger a field visit.
- **Model impact:** Defined the two-stage verification process that the data reflect (evidence → desk classification → optional field visit). This justified treating `Lab Status` as a left-truncated sample, motivated the plausibility/selection analysis, and made desk triage the zero-cost tier of the Subproblem 3 two-tier policy. Also set the Subproblem 4 trigger: a new Positive ID is a priority update event.

## Exchange 2 — evidence behind true positives
- **Question:** What fraction of real giant-hornet reports are backed by a clear photo or specimen?
- **Reply (summary):** No published figure; qualitatively most true positives have some supporting evidence (workflow requires it), plausibly 80–95%; the rarer case is a photo diagnostic enough for classification.
- **Model impact:** Motivated using `has_image` / `n_img` as evidence-quality proxies rather than pixel content, and interpreting the fitted negative `has_image` coefficient as a selection effect (the verified set is evidence-conditional), not as "photos hurt."

## Exchange 3 — credibility factors
- **Question:** Which details make a report credible to a state entomologist?
- **Reply (summary):** Ranking: (1) diagnostic photo or specimen; (2) size relative to a known reference; (3) location near the known invasion area; (4) nest or multiple individuals; (5) corroborating behavior/timing/address. Weak reports: vague, no photo, look-alike.
- **Model impact:** Chose the keyword feature set in `model.py` — `size_big`, `bee_hive`, `nest`, `multiple`, `killed`, `specimen_sent`, `photo_word` — and the distance-to-cluster feature, matching the expert credibility ordering.

## Exchange 4 — distant reports
- **Question:** Are sightings far from confirmed areas treated as unlikely, or the same as others?
- **Reply (summary):** Distance lowers the prior and the priority but is a weight, not a dismissal rule: a far report with credible evidence is still reviewed, and isolated long-distance finds are how satellite populations are detected (a queen ranges ~30 km).
- **Model impact:** Distance was implemented as a continuous logistic feature (`d_core_km`), not a hard geographic filter; the 30 km founding range became the spatial scale of the Subproblem 1 spread model; the desk-review safety tier in the prioritization policy exists so far-but-evident reports are never dropped.

## Exchange 5 — time to find and destroy a nest
- **Question:** After lab confirmation, how long to find and destroy the nest?
- **Reply (summary):** Days to a few weeks; dominated by catching/tagging a live forager; one to three weeks when the nest must be located, a day or two if already known.
- **Model impact:** Calibrated the per-colony-season removal rate in the Subproblem 1 colony projection: a colony found in season is removed before producing new queens, supporting `mu_c = 0.30/season` (interval [0.1, 0.6]) and the "establishment rarer than removal" baseline.

## Exchange 6 — reporting surge after a discovery
- **Question:** How many extra public reports follow a confirmed colony, and why?
- **Reply (summary):** A local spike — a handful to a few dozen extra reports within days to weeks, clustered near the site, mostly false positives (look-alikes), driven by publicity/priming, decaying over a few weeks.
- **Model impact:** Motivated the news-surge term in the report-process model (M2: decaying exponential at each confirmation week) and the Subproblem 4 finding that a confirmation changes the composition of the unverified pool within days, forcing a rescore. The observed 2020 surges (report rate ~3x within two weeks of the May 27 confirmation) are this mechanism.

## Exchange 7 — clean period before declaring a colony gone
- **Question:** How long without a confirmed report before being confident a colony is gone?
- **Reply (summary):** About one full season at minimum (queens overwinter, so weeks/months prove little); in practice 2–3 consecutive clean active seasons plus sustained trapping is strong evidence; one clean season is suggestive only.
- **Model impact:** Set the decision criterion of Subproblem 5: the model quantifies exactly this — 2 clean active seasons give a 0.005 false-eradication probability under N=1 surviving colony, 3 seasons 0.0004; the winter-blindness point (winter counts for nothing) is built into the season-based criterion.

## Exchange 8 — field-trip budget
- **Question:** How many field investigation trips can the agency realistically complete per active season?
- **Reply (summary):** Order of tens, not hundreds: a small team, each trip most of a day plus travel, concentrated in late summer/fall; desk triage is what makes this feasible.
- **Model impact:** Set the operational cap in Subproblem 3: the marginal-yield rule alone would take k ≈ 400 trips, but the budget caps k at ~40–80; recommended operating point k = 40 trips/season (interval [10, 80]), expected yield 9.34 positives.

## Exchange 9 — seasonal operation
- **Question:** Does surveillance operate all year or mainly in warm months?
- **Reply (summary):** Warm months only (roughly late summer–fall, some spring queen activity); winter is a detection blind spot, not evidence of absence.
- **Model impact:** Defined the active season as Jul–Nov in the `season` feature and the report-process model; made "clean active season" the time unit for eradication testing; set the Subproblem 4 update cadence (weekly in-season, monthly in winter).

## Exchange 10 — trap-check cadence
- **Question:** How often are monitoring traps checked?
- **Reply (summary):** Weekly to biweekly in the active season (1–2 weeks), more often at peak or near known detections, suspended in winter.
- **Model impact:** Provided the operational cadence for the trap channel in Subproblem 5: `p_trap = 0.6` per season (interval [0.3, 0.9]) combined with 50% zone coverage, and the weekly in-season floor for Subproblem 4 model updates.
