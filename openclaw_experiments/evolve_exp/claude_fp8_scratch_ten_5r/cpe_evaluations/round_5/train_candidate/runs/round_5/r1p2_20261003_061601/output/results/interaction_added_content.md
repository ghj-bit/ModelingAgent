# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — 2021_C (Vespa mandarinia report triage)

Ten exchanges, one question each. Each reply was converted into a concrete
parameter, constraint, or decision rule in the models below. No reply text is
reused verbatim in the submission; only values and rules travel.

**Exchange 1** (Q: can the lab classify a report with no usable photo?)
Reply: firm positives essentially require physical or photographic evidence;
no-photo reports end up Negative or Unverified.
→ Work: binary feature `is_img` (image attached, from the images sheet) as a
first-class predictor; classification target restricted to the two firm lab
outcomes (Positive ID / Negative ID); Unverified/Unprocessed (2,357 rows)
treated as the actionable triage pool, not as labels.
→ Parameter: p(positive | no usable evidence) ≈ 0 (constraint on the model's
support: positives in the labeled set all have usable evidence).

**Exchange 2** (Q: what share of public reports arrive with a clear photo?)
Reply: any photo on roughly a third to a half of reports; a clear,
diagnostic photo on the order of 10–30%.
→ Work: validated against dataset — 46.2% of 4,440 reports carry ≥1 image
file (3,305 attachments, 3,196 images), i.e. in the expert's range; the
dataset itself is therefore not photo-scarce, so `is_img` is a *discriminative*
variable, not a missing-data nuisance. Documented in data-cleaning notes.
→ Interval where it holds: Washington reporting, 2018–2020.

**Exchange 3** (Q: which insects are most often mistaken for the giant
hornet?)
Reply: bald-faced hornet, yellowjackets, paper wasps, mud daubers,
bumblebees, hoverflies.
→ Work: negative-class composition check. Lab Comments of the 2,069 Negative
IDs are dominated by golden digger wasps, bald-faced hornets, cicada killers,
wood wasps/horntail sawflies, yellowjackets — consistent with the expert's
list. This defines the *confusion set* the classifier must separate; it is why
generic size/color words in notes have weak signal (they match both classes).

**Exchange 4** (Q: when do reports come in, are winter reports common?)
Reply: reports peak late summer/early fall (Aug–Oct, September peak); winter
reports uncommon and almost always misidentification.
→ Work: features `in_season` (month ∈ {8,9,10}) and `winter` (month ∈
{11,12,1,2}) in the logistic model; also the seasonal window for the
eradiation calculation (one "season" = Aug 1–Oct 31).
→ Check: 50.5% of all reports fall in Aug–Oct (95% CI [49.0%, 51.9%]),
consistent with a reporting surge on a low seasonal background.

**Exchange 5** (Q: how are reports near prior confirmed detections
prioritized?)
Reply: proximity to a prior positive is among the strongest positive signals;
high priority within a few km, especially same/next season; diagnostic photo
and right season raise priority further.
→ Work: feature `dist_pos` = distance to nearest *earlier-dated* Positive ID
(time-respecting, computed by a date-sorted sweep), plus `dist0` to the 2019
BC discovery region anchor (49.06, −123.46). These are the two strongest
coefficients in the model (OR 0.095 and 0.127 — each step of distance away
from established presence cuts odds roughly 8–9-fold). The triage ranking in
Task 3 is exactly the expert's rule: distance to prior positives, season,
photo.

**Exchange 6** (Q: how long before declaring the hornet gone?)
Reply: no fixed period; judgment call; several years; at least 2–3
consecutive seasons with no confirmed detections plus continued surveillance.
→ Work: eradiation criterion in Task 5: evidence = consecutive silent
full-seasons (each with the season's actual reporting effort) AND zero
confirmed detections; a quantified rule (posterior probability the pest is
still present falls below a threshold, e.g. 5%) is computed for 1–3 silent
seasons and compared against the 2–3 season norm; the model's season-level
detection probability drives the calculation.

**Exchange 7** (Q: how many follow-ups can the lab do in a busy season?)
Reply: a few dozen — roughly 20–50 field follow-ups per busy season.
→ Work: the investigation budget K ∈ {10, 20, 30, 50, 75} in the top-K
precision table of Task 3; K = 20–50 is the operationally realistic range.
All top-K results reported for this range; K = 50 captures 13/14 positives
(93%).

**Exchange 8** (Q: how often should the model be updated?)
Reply: end of each season; mid-season refresh only after a large batch of new
confirmed labels (hundreds, or a new confirmed cluster).
→ Work: Task 4 update policy: Bayesian logistic update / refit at season
boundaries; trigger-based mid-season refresh rule (new labeled batch ≥ 100
rows, or ≥ 3 new positives within 30 km of an existing cluster, or a shift in
the seasonal reporting rate > 2 SE). Label-arrival lag (days–weeks) justifies
not updating per report.

**Exchange 9** (Q: how far does the hornet usually spread between sightings?)
Reply: local — a few km per season (worker foraging 1–2 km from the nest;
queen dispersal up to 30 km is a maximum, not routine); long jumps are rare
and usually human-mediated.
→ Work: the radial growth fit in Task 1 (power law on distance-from-origin vs
time: exponent b ≈ 0.12, i.e. near-stationary), the 95% prediction intervals
on the spread radius at 45/90/180 days (≈ 0.2–1.8 km), and the spatial
prior in the model (short decay scale of dist_pos). Also bounds the
"next sighting" location prediction in Task 1: within ~2 km of the last
nest in the same season, up to ~30 km in the next (queen-founding) season.

**Exchange 10** (Q: which reports are most likely to be completely wrong?)
Reply: no usable photo + vague text; winter/early-spring; far from any prior
detection; describing common look-alikes; alarmed/inexperienced observers.
→ Work: the four negative-likelihood regimes map onto model features and are
used to *bound* the scores of the Unverified pool: no-image + off-season +
distant reports are down-ranked; the model's ranking reproduces exactly this
ordering on the 2,342 Unverified + 15 Unprocessed records (score range
0.95 → ~0; top-ranked are near-positives, in-season or adjacent to the
established cluster).

---

## Data cleaning record (stated per workflow step 2)

Source: `2021MCM_ProblemC_DataSet.xlsx` (4,440 rows) +
`2021MCM_ProblemC_ Images_by_GlobalID.xlsx` (3,305 attachments).

Repairs made:
- 3 `Detection Date` values were literal `<Null>` strings → set to missing.
- 18 rows had submission date earlier than detection date (clock/reporting
  artifact) → lag clipped to 0 and flagged `lag_flag`; lags > 2 y flagged.
- No duplicate `GlobalID`s found (0 removed).
- Attachment presence derived per `GlobalID` from the images sheet:
  `is_img` (≥1 image file), `is_vid`, `n_files`; 2,052 reports (46.2%) have
  ≥1 image — matches the expert's stated third-to-half (exchange 2).
- `Lab Status` categories kept as-is: Positive ID 14, Negative ID 2,069,
  Unverified 2,342, Unprocessed 15.
- `Lab Comments` 2 nulls (among negatives) — unused as a label source.

## Key numbers used in solution.json (with intervals)

- Base rate among firm-labeled reports: 14/2,083 = 0.67%, 95% CI
  [0.38%, 1.14%] (Clopper–Pearson).
- Model AUC = 0.988, 95% CI [0.984, 0.991] (50-fold stratified CV);
  LogLoss 0.167 [0.160, 0.174]; Brier 0.058 [0.056, 0.061].
- Top-K: K=20 → 10/14 positives (precision 0.50, lift 74); K=50 → 13/14
  (0.26, lift 39); K=75 → 14/14 (0.19, lift 28).
- Weekly report counts: variance/mean ≈ 168 → strongly overdispersed
  (negative binomial r ≈ 0.22), i.e. bursty.
- Positive interarrival: 13 intervals, mean 29.1 d; 95% CI on the mean
  interarrival ≈ [18 d, 55 d].
- Aug–Oct reporting share: 50.5%, 95% CI [49.0%, 51.9%].
- Radial spread: b ≈ 0.12 (near-stationary); 95% PI on radius at 180 d:
  [0.2, 1.8] km.
- Per-report detection probability (full 2020 season, n=2,159 reports):
  p̂=0.67%; P(no detection | present) for one silent season ≈ (1−p̂)^n;
  posterior probability pest still present after 1/2/3 silent seasons:
  ≈ 5e-4 / <1e-5 / <1e-6 (prior 0.5) — far below any reasonable alarm
  threshold; the binding constraint is surveillance effort, not the count of
  silent seasons.

## Parameter table (empirical inputs with provenance)

| name | value | interval | source |
|---|---|---|---|
| max queen dispersal range | 30 km | — | task problem statement ("range estimated at 30km") |
| usable-photo share of public reports | 10–30% (any photo: third–half) | — | expert exchange 2; validated: dataset image share 46.2% |
| seasonal peak of reports | Aug–Oct, Sept peak; winter rare | — | expert exchange 4; dataset check 50.5% CI [49.0, 51.9] |
| field follow-up capacity | 20–50 per season | — | expert exchange 7 (sets K range) |
| typical per-season spread | a few km (worker forage 1–2 km) | — | expert exchange 9 |
| eradiation judgment horizon | 2–3 consecutive seasons + surveillance | — | expert exchange 6 |
| update cadence | end of season; mid-season only on large label batches | — | expert exchange 8 |
| confusion species set | bald-faced hornet, yellowjackets, digger wasps, cicada killers, wood wasps, bumblebees, hoverflies | — | expert exchange 3; dataset Lab Comments composition |
