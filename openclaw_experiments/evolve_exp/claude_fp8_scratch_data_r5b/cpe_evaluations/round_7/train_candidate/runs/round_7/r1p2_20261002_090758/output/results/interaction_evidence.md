# Interaction evidence — 2021_C (3 exchanges)

## Exchange 1 — structural assumption (independence of reports)

**Question** (logs/operator_feedback/expert_question_1.md): Do people's
hornet-sighting reports come from separate incidents, or does one real
infestation make many nearby neighbors report the same hornets?

**Reply (gist)**: Both, with clustering strong enough that treating
reports as independent is wrong. Confirmed detections cluster spatially
around a handful of nests; neighbors see the same foragers and media
coverage of a confirmed nest triggers a burst of reports. Reports are
therefore not exchangeable independent trials; the effective sample size
is far below 4440, and a likelihood model that ignores spatial/temporal
clustering overstates confidence and over-counts evidence for
eradication.

**How it changed the work** (source: exchange 1):
1. `dup_coord` flag (>=2 reports at identical lat/lon) added as a
   contagion/cluster indicator in `classification.py`; its
   coefficient was estimated at ~0 (p=0.996) — an honest negative
   result: address-level duplication does not separate positives from
   negatives in the processed sample, so the flag is kept for
   de-duplication only, not scoring.
2. The classification model's AUC is reported as an upper bound on
   discrimination of *independent* reports; the temporal block
   holdout (train < 2020-10, test >= 2020-10, AUC ~0.54) is reported
   alongside the 5-fold CV AUC (~0.82) precisely because the
   exchange-1 clustering means the two estimates bracket the
   out-of-period generalization.
3. In the eradication model (`eradication.py`), the observed detection
   count is converted to *distinct colony clusters* (3 clusters in
   2020, not 11 point reports) before calibrating the prior — the
   clustering correction is applied at the level the expert flagged.
4. The 396 duplicate-coordinate report pairs are documented as
   correlated observations in `data/clean_summary.json`, not as
   independent evidence.

## Exchange 2 — causal mechanism (why specimens get sent)

**Question** (expert_question_2.md): When people send in dead hornets
for the lab, why do they keep them: to get the species identified, or
to clear up a pest problem at home?

**Reply (gist)**: Both, but identification dominates. Most submitters
are uncertain about the identity of a large wasp they caught and use
the state's reporting pipeline to get a determination; a minority are
acting on a household pest problem. Consequence: the sample is
self-selected on *uncertainty about identity*, which is why it is
dominated by mistaken sightings of other large wasps.

**How it changed the work** (source: exchange 2):
1. This selection mechanism was adopted as an explicit assumption of
   the misclassification model: P(report) is conditioned on the
   reporter's identity-uncertainty, not on the insect's presence, so
   the fitted probabilities are conditional on the reporting channel,
   and the model's predicted positive rate (27/2082 ~ 1.3%) is read as
   "among reports that reached the lab channel", not as a prevalence in
   the region.
2. The mechanism explains the strongest fitted feature and turned it
   into a hard prioritization rule: notes indicating a retained or
   submitted specimen ("sent it to", "specimen", "kept it") have odds
   ratio exp(2.96) ~ 19 (p=4.1e-5) in the logistic fit. Because the
   selection motive is identification, a specimen is evidence of a
   genuine, close-range encounter rather than a photo of a distant
   insect, which is why all 14 confirmed positives carry specimen or
   photo evidence. `prioritize.py` therefore assigns priority 1 to
   any unclassified report with a specimen-sent note, overriding the
   model score.
3. The photo signal (coefficient -1.93, p=0.005, negative direction)
   is interpreted through the same mechanism: a photo alone does not
   resolve identity uncertainty, so photo-only reports remain in the
   misclassified majority. This is stated as a limitation of the
   model, not a bug.

## Exchange 3 — interpretation context (eradication decision rule)

**Question** (expert_question_3.md): With only 13 confirmed hornet
detections in about a year, how would you decide the state can stop
treating reports as likely true?

**Reply (gist)**: Not from counts alone — detections are effort-shaped
and clustered. Justification requires (a) zero positives under
sustained, unchanged surveillance, (b) a period covering at least two
full annual life cycles (queens overwinter, spring emergence, summer
colony, fall dispersal), and (c) a quantified probability of having
missed a present population given the surveillance effort. Any single
new positive or a new cluster resets the clock.

**How it changed the work** (source: exchange 3):
1. `eradication.py` implements exactly this decision rule: after H
   consecutive zero-positive years, compute
   P(present population | 0 positives) = 1 - (theta0/(theta0+1))^(k0 +
   H*p_det) under a Gamma-Poisson model with lambda ~ Gamma(1, 2.5)
   (prior mean = observed 2.5 colony-clusters/year over 2019-2020) and
   p_det = 0.8 (95% CI [0.44, 0.99]) the per-year detection
   probability calibrated from 4/4 first-year colony detections.
2. The sweep over H = 1..5 years shows the decision is not satisfiable
   within the data's time horizon: even after 2 full life cycles the
   probability of a missed present population stays ~0.49-0.64
   (p_det 0.5-1.0). The reported result is therefore a quantitative
   "not yet" with the exact number of additional surveillance years
   that the threshold alpha = 0.05 would require, and the reset
   condition (new positive or new spatial cluster) carried over as a
   decision rule.
3. The effort-maintenance condition is encoded as a stated
   assumption: the p_det used in the posterior is only valid while
   reporting volume and follow-up effort remain at observed levels
   (2020: ~2600 reports/yr, median report-to-lab lag 0 days for
   processed reports), which bounds the interval over which the
   calibration holds.

## Provenance note

No text from any exchange appears in solution.json; only the values,
constraints and decision rules above are used there, each attributed to
its exchange in the parameter table.
