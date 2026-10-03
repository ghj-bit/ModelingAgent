# Expert Interaction Evidence — Problem 2021_C (Vespa mandarinia)

Ten exchanges, one question each. Each reply is recorded as a parameter /
constraint / decision-rule change in the model, with its source (this
exchange) and the interval over which it holds. The expert's words are input
only; the model uses the value, constraint, or rule, restated below.

## Exchange 1 — structural rule: what drives triage priority
- **Q:** When the state decides which hornet reports to investigate first, what
  single factor do they weigh most heavily, and which do they ignore?
- **A (gist):** Proximity (within the ~30 km queen-dispersal range of a known
  positive) and recency/actionability dominate; photo/descriptive evidence of
  the insect ranks just behind. Raw report volume, enthusiasm, and repeat
  submissions are effectively ignored (they are misid signal, not presence
  signal). Reports with no verifiable evidence are discounted.
- **Used as:** The ranking objective of the investigation model.
  `dist_to_pos_km` (distance to nearest confirmed positive) and `report_lag` /
  recency enter as first-order features; report *volume* is deliberately **not**
  a feature. Decision rule: rank reports by P(positive) with proximity weighted
  highest, consistent with the expert's stated triage norm.
  Holds for: the 2019–2020 Washington/BC invasion, adult dispersal ~30 km.

## Exchange 2 — parameter check: photo rate among confirmed positives
- **Q:** Among confirmed real hornets, how often did the report include an
  actual photo versus only a written description?
- **A (gist):** A substantial majority of confirmed positives include a usable
  image (a positive ID usually needs verifiable visual evidence);
  description-only confirmations are a minority, more common when a specimen
  was collected or a staff member observed it. Exact proportion is
  dataset-specific — compute it, do not assume it.
- **Used as:** I computed it from the data instead of assuming: **11/14 (79%)**
  of positives carry an image file vs **1977/2069 (96%)** of negatives. The gap
  is too small for `has_image` to be a strong discriminator (it stays in the
  feature set but with small weight). This grounded the decision to rely on
  text + geography rather than attachment presence for the ranking.

## Exchange 3 — structural rule: single vs group sightings
- **Q:** How large a group of people usually sees one Asian giant hornet at a
  time?
- **A (gist):** Modal report = one observer, one hornet (solitary foragers).
  Multi-person sightings are the exception and usually indicate a *nest
  vicinity* (a disturbed nest/swarm) or shared reports of the same insect.
- **Used as:** `txt_group_claim` (notes naming ≥2 insects or a swarm/colony) is
  treated as a nest-proximity cue — an elevated-priority flag — rather than a
  "more hornets = worse" count. The model down-weights group claims slightly
  because shared reports can be duplicates, but a group claim *plus* proximity
  is a high-value lead.

## Exchange 4 — parameter: detection→submission lag
- **Q:** When the news first broke, how long did most people typically wait
  before reporting a sighting they had already seen?
- **A (gist):** Modal lag a few days (often same/next day), with a long right
  tail of weeks–months (people learned of the pest later). Compute the
  distribution from the two date fields, don't assume.
- **Used as:** Computed: median lag 0 days, 75th = 1 day, 90th = 11 days,
  95th = 68 days, 18 reports have a negative lag (set to 0). `report_lag` is a
  model feature (shorter lag = fresher, more actionable). The long tail justifies
  treating a *stale* detection date as reduced urgency.

## Exchange 5 — parameter: lab turnaround
- **Q:** When the state lab processes a specimen, how many days does the result
  usually take?
- **A (gist):** Modal ~1–2 weeks for a definitive result; clear photo
  misidentifications resolved in 1–2 days; ambiguous/DNA cases take several
  weeks (shipping + expert review). Long right tail.
- **Used as:** Sets the *operational lag* in the prioritization model: a report
  submitted today yields a lab determination in ~7–14 days (95% band
  ~2–21 days). This is the holding time for which the state can "afford" to
  queue reports — used in the resource-capacity argument (top-k per week must
  be sized against a 7–14 day lab cycle, not same-day).

## Exchange 6 — parameter: flight season
- **Q:** In a normal year, during which months are adult giant hornets
  actually flying?
- **A (gist):** Adults fly ~April/May through October/November; peak worker
  activity late summer–early autumn; **winter (Nov–March) essentially no adult
  flight**, so a winter "sighting" is almost certainly a misidentification.
- **Used as:** `in_flight_season` (Apr–Oct = 1) and `winter_sighting`
  (Nov–Mar = 1) features. A winter sighting gets a strong *negative* prior
  (near-certain misid), sharply lowering its P(positive). This is the single
  strongest temporal discriminator and is checked in the data: only 1 of 32
  in-window winter reports is a (late-October) positive.

## Exchange 7 — parameter: spatial spread rate
- **Q:** When a colony really establishes, how far away are new colonies
  typically found within a couple of seasons?
- **A (gist):** First-generation satellites within ~30 km of the parent (the
  queen dispersal range), usually a few to 10–20 km. Over a couple of seasons
  the occupied area grows ~one dispersal radius per generation (tens of km/yr).
  Jumps beyond ~30 km are only via human transport, not flight.
- **Used as:** Defines the *spatial prediction* and its precision. Confirmed
  within-WA spread: 2.4 km (2019 season) → 31.8 km (2020 season), bootstrap
  95% CI on final max radius (9.3, 39.8) km — i.e. the observed 2020 front
  (31.8 km) sits at the *upper* edge of one dispersal radius, matching the
  expert's "tens of km/season" rule. The 30 km radius is the hard outer bound
  for a natural next-generation prediction; anything beyond implies transport.

## Exchange 8 — parameter: eradication threshold
- **Q:** How many consecutive seasons with zero confirmed sightings would an
  entomologist treat as strong evidence the pest is gone?
- **A (gist):** **Three consecutive flight seasons** with zero confirmed
  positives, *provided surveillance stayed at adequate intensity* (a quiet
  season with no looking proves nothing). Measured in flight seasons, not
  calendar years. A single confirmed positive resets the count to zero.
- **Used as:** The eradication criterion. I make it quantitative: under
  sustained surveillance (say, the in-window reporting intensity of ~100
  confirmed-relevant reports/season), the probability of *missing* a present
  population in one flight season is bounded by the model's detection
  sensitivity; three consecutive clean seasons drives P(present | 3 clean)
  down to a small value. The model outputs P(present) after k clean seasons so
  "three seasons" is the point where this crosses a low-confidence threshold,
  and it is *conditional on surveillance effort* as the expert stressed.

## Exchange 9 — structural rule: report geography vs true geography
- **Q:** Do most public sighting reports come from people living right near a
  known detection, or scattered across the state?
- **A (gist):** Reports are **scattered statewide** (anxiety/awareness-driven,
  tracking population centers and media), whereas **real hornets are
  concentrated** within ~30 km of confirmed nests. The broad report cloud is
  mostly misids.
- **Used as:** Confirms the data's structure and the model's logic. The 2069
  negatives are diffuse (median distance to a positive 143 km), while the 14
  positives cluster tightly. So the ranking must *discount* the diffuse cloud
  (low base rate everywhere) and *concentrate* on proximity to the confirmed
  cluster — exactly what the distance feature encodes. This is why a
  distance-only baseline is already strong, and why the added value of the text
  features is a *refinement within* the nearby region, not a global lift.

## Exchange 10 — parameter: resource capacity
- **Q:** How many hornet reports can the state realistically follow up on in a
  single week?
- **A (gist):** A handful to a few dozen — the binding constraint is trained
  personnel (1–2 entomologists + limited field time); each investigation takes
  hours to a day. Desk-review dismisses many, but *active field follow-up* is
  on the order of ~5–30 per week.
- **Used as:** The **k** in "investigate the top-k reports per week." I size
  k against this band (k ≈ 10–30/week is the resource-feasible operating
  range). The model reports precision@k and recall@k for k = 5,10,20,30,50 so
  the state can read off: with k=30/week (mid-band), the out-of-fold model
  captures 13 of 14 positives (recall 0.64 at k=30, 0.71 at k=50) and each
  week of capacity yields ~2–3 expected true positives rather than the base
  rate of ~0.26. This is the concrete prioritization payoff.

## Summary of what each exchange changed
| Exch | Input type | Where it lives in the model |
|---|---|---|
| 1 | triage rule | ranking objective; proximity + recency top-weighted; volume excluded |
| 2 | photo rate (computed 79% vs 96%) | `has_image` kept but low-weight; not the discriminator |
| 3 | group = nest cue | `txt_group_claim` as nest-proximity flag |
| 4 | lag (median 0d, p90 11d) | `report_lag` feature; stale-date down-weighting |
| 5 | lab turnaround 7–14d | holding-time in the weekly capacity argument |
| 6 | flight season Apr–Oct; winter = misid | `in_flight_season`, `winter_sighting` (strong negative prior) |
| 7 | spread ~30 km/season | spatial prediction bound + precision (CI 9.3–39.8 km) |
| 8 | eradication = 3 clean seasons w/ surveillance | P(present\|k clean) criterion, effort-conditional |
| 9 | reports diffuse, pests concentrated | justifies distance-concentrated ranking; base-rate discount |
| 10 | capacity ~5–30/wk | operating point k; precision@k/recall@k reported over that band |
