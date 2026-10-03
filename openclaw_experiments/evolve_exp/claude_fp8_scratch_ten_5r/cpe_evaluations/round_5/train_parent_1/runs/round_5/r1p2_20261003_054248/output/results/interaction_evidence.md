# Expert Interaction Evidence — Task 2021_C (Vespa mandarinia)

This file records each expert exchange: the question asked, the reply received,
and how the reply became a parameter, constraint, or decision rule in the model.
It is kept separate from the submission (solution.json).

Model architecture (what the exchanges feed into):
- A Bayesian logistic classification model predicting P(report is a true Vespa
  mandarinia sighting | features). Features: distance to known nest clusters,
  detection month (life-cycle seasonality), attachment presence, and text
  keyword flags. Distance to the source-nest cluster is the dominant predictor
  (LOO-CV AUC 0.989 for distance alone; 0.989 for the full model).
- A discrete spatial–temporal spread process (queen founding, colony growth,
  dispersal) parameterized partly by these expert estimates.
- A prioritization rule (rank reports by posterior probability, process the top
  K the state's lab capacity allows) and an update / eradication rule.

## Exchange log

### Exchange 1 — colony worker output (spread model, Q1)
- **Q:** How many worker hornets does a single nest typically raise over one summer?
- **Reply:** A mature colony produces on the order of a few hundred workers —
  commonly ~100–300 at peak, some large nests reaching several hundred. Empirical
  estimate; varies with climate, prey, nest age.
- **Used as:** colony peak-worker count `W_peak` = 100–300 (central ~200),
  interval [100, 300], source: Exchange 1 (expert empirical judgment). Enters the
  spread model as the number of foragers that generate detection/report events
  and the pool of queens produced at the end of the season. Interval holds over a
  single summer season for a nest that survives to maturity.

### Exchange 2 — discovery & eradication latency (spread + eradication, Q1/Q5)
- **Q:** When a nest is discovered, how fast is it found and destroyed, and what
  triggers discovery?
- **Reply:** Discovery is report-driven (a confirmed worker sighting, a live
  trapped hornet, or a beekeeper reporting a hive attack), not systematic search.
  Once confirmed, the nest is physically located (tracking tagged hornets / flight
  lines) and destroyed within **days to a few weeks** — commonly **1 to several
  weeks** from first confirmed detection. Nests are often found **late in the
  season**, after workers are numerous.
- **Used as:** detection-to-eradication delay `τ_erad` = 1–several weeks
  (central ~2 weeks), interval [~3 days, ~4 weeks], source: Exchange 2. Two
  consequences: (a) in the spread model a nest stays productive and spreads
  queens for `τ_erad` after its first confirmed report, so the expected
  undetected-active window is the latency from founding to first report plus
  `τ_erad`; (b) for Q5 (eradication evidence) it means a "quiet period" shorter
  than `τ_erad` is not yet safe evidence, because a late-season nest can still be
  undetected during the response window. The report-driven discovery mechanism
  is itself a structural assumption of the spread model (reports, not
  exhaustive search, are the detection process).

### Exchange 3 — queen dispersal kernel (spread model, Q1)
- **Q:** Is 30 km typical or an outer limit, and how far do most queens fly?
- **Reply:** 30 km is the **outer limit / maximum** per-generation jump, not a
  typical distance. Most queens found within **a few km, often under 1–2 km**,
  when good habitat is available. 10–30 km is the **tail**, occurring when
  queens are wind-carried or local sites are saturated.
- **Used as:** per-generation queen-dispersal kernel `k(d)` with typical scale
  `σ_near` ≈ 1–2 km and a rare heavy tail out to the 30 km maximum. Modeled as a
  two-component (mixture) radial kernel: a dominant short-range component
  (median ~1 km, most mass within ~2 km) plus a low-weight 10–30 km tail; the
  30 km cap is the hard support (max jump), source: Exchange 3 (and the problem
  statement, which fixes 30 km as the maximum). This governs the expected number
  of daughter nests per parent per season and the spatial autocorrelation of
  detections. The cap `d_max` = 30 km, interval [30, 30] (fixed by the problem);
  the typical-scale estimate interval [0.5, 3] km.

### Exchange 4 — what distinguishes a real sighting (classification features, Q2)
- **Q:** What makes a real giant-hornet sighting different from people mistaking
  ordinary wasps / other hornets?
- **Reply:** Reliable markers are **size** (workers ~3–4 cm, queens ~5 cm,
  clearly bigger than yellowjackets / paper wasps / European hornets) and the
  **bright orange-yellow head** with a mostly dark thorax and banded
  orange-and-dark abdomen. European hornets are a key look-alike but have a
  **reddish-brown** head/thorax, not orange-yellow. Most mistaken reports are
  ordinary wasps / yellowjackets or the European hornet, and scale is misjudged
  from **photos with no size reference**. Genuine reports usually carry a clear
  close-up showing the orange head, or a report of an unusually large hornet
  **near honeybee hives**.
- **Used as:** (a) the label "Positive ID" is effectively *lab-confirmed Vespa
  mandarinia*, so the model's target is a confirmed sighting, not "any hornet";
  (b) the text features encode the discriminative cues — a size word (large /
  huge / giant / inches / cm) and a bee-hive context word (hive / bees /
  honeybee) both raise the posterior, matching "clear close-up of orange head"
  and "near honeybee hives"; (c) because scale is misjudged from photos lacking a
  reference, *attachment presence* is a weak positive cue (a photo is not
  evidence of a Vespa) — this is why `has_file` is only a mild feature
  (AUC 0.60), consistent with the reply; (d) European-hornet misidentification
  is the dominant false-positive source, which is a structural assumption: the
  negative class is mostly look-alike species, not "no insect." Worker size
  3–4 cm, queen ~5 cm, interval [3,5] cm, source: Exchange 4.

### Exchange 5 — what the lab needs to confirm a positive (Q2, Q3)
- **Q:** Does the lab need a physical specimen, or is a good photo enough?
- **Reply:** A **good photo is often enough** — clear close-ups of the
  diagnostic features (orange-yellow head, dark thorax, banded abdomen) plus a
  credible report routinely confirm a positive. A **specimen is preferred** and
  typically **required when the image is ambiguous, lacks a size reference, or
  is borderline**; not mandatory for every confirmation. A **substantial share of
  confirmed positives are photo-based**; specimens are collected mainly for
  **first-in-area** detections or when **authoritative/genetic** verification is
  wanted.
- **Used as:** (a) a report can be resolved to *positive or negative* from a
  photo alone when the image is unambiguous — this makes the "Unverified" status
  interpretable as "insufficient or absent image, and no specimen sent," i.e. an
  information gap, not a species verdict; (b) it defines the **investigation
  action** in Q3: "follow-up" = (i) request/obtain a usable photo or specimen and
  (ii) run it through the lab. A report already carrying a usable photo has a
  lower follow-up cost, so the model can fold *whether a usable image is present*
  into the cost of resolving a report; (c) **first-in-area** reports warrant a
  specimen, which raises their investigation value beyond their raw posterior —
  an explicit tie-in with the spatial feature (reports near, but not at, known
  nests are first-in-area candidates). This is a structural rule: resolve-from-
  photo probability `p_resolve|photo` is high for unambiguous images and drops
  for ambiguous/size-less ones, source: Exchange 5.

### Exchange 6 — triage cadence (update frequency, Q4)
- **Q:** During the busy summer, how often does the state review new reports to
  decide what to investigate — daily, weekly, or batch?
- **Reply:** **Daily / essentially continuous** during the active season — new
  reports are screened as they arrive and follow-up decisions made on a **daily
  cadence**, because a live hornet or hive attack is time-sensitive. **Batch
  review** only in the **off-season** or when volume is low.
- **Used as:** the model-update cadence for Q4. The classification model is a
  Bayesian posterior; with ~hundreds of new reports per week at the summer peak
  (data: up to ~1,400 submissions in August), the correct policy is an
  **online / daily update** of the posterior during the season (Bayes' rule on
  each newly resolved report), not a batch re-fit, because (i) the seasonal
  prior itself drifts (see Q1 seasonality), and (ii) the state acts daily. In the
  **off-season** (low volume) a lower-frequency (e.g. weekly/monthly or
  end-of-season) re-estimate suffices. Concretely: update frequency
  `Δt_update` = 1 day (in-season), weekly–monthly (off-season), source:
  Exchange 6. This also bounds the *staleness* of the prioritization ranking: a
  report's rank is recomputed daily, so the max age of a stale priority during
  the season is ~1 day.

### Exchange 7 — eradication evidence threshold (Q5)
- **Q:** How long without any confirmed sightings before being reasonably
  confident the state is free of hornets?
- **Reply:** **No fixed clock alone** establishes freedom — it depends on
  **surveillance intensity**. Under continued active surveillance (traps + public
  reporting), a reasonable working threshold is **~2–3 consecutive years with no
  confirmed detections** (no trapped workers, no hive attacks), given the annual
  life cycle and the need to observe at least **two full seasons of queen
  emergence and colony founding**. A single missed nest releases new queens each
  fall, so one quiet year is weak evidence. If surveillance is reduced, the
  required period **lengthens**, because absence of detections then reflects
  absence of looking as much as absence of hornets.
- **Used as:** the eradication decision rule for Q5. Model the probability the
  state is actually free as a function of the run-length of confirmed-negative /
  no-positive seasons `T` *and* the surveillance/detection probability `p_det`:
  `P(free | T years no positive) = 1 − (1 − p_det)^…`-style compounding over the
  number of *opportunity windows* (each summer = one queen-release opportunity).
  The **2–3 year** threshold (interval [2,3], source: Exchange 7) is the value of
  `T` at which this probability crosses a high confidence level (e.g. ≥0.95) under
  *normal* surveillance; it **lengthens** if `p_det` drops (surveillance reduced),
  which the model expresses as `T* ∝ 1/p_det`-type scaling. This directly encodes
  the reply's "absence of looking vs. absence of hornets" distinction and the
  life-cycle requirement (≥2 full seasons). The rule: declare eradication only if
  (i) ≥2–3 full seasons with zero confirmed positives *and* (ii) surveillance
  effort held at or above the level used to estimate `p_det`; otherwise the
  quiet-period clock is reset.

### Exchange 8 — investigation capacity (prioritization threshold, Q3)
- **Q:** How many reports can the state realistically *investigate* in a busy
  week at peak?
- **Reply:** **A few dozen per week (≈20–50 field investigations)** is a
  realistic ceiling for a small state team (3–5 people part-time on hornet work).
  A single site visit (travel, inspection, specimen handling, documentation)
  consumes a substantial fraction of a person-day. **Desk screening** (photo +
  note review) can handle **hundreds per week**; **physical investigation** (trap
  checks, site visits, specimen collection) is the scarce resource — tens, not
  hundreds.
- **Used as:** the two-tier resource model behind Q3's prioritization rule.
  Let `C_screen` = hundreds/week (unconstrained) and `C_invest` = 20–50/week
  (binding), interval [20,50], source: Exchange 8. The prioritization problem is
  then: desk-screen **all** reports (cheap), and allocate the **K = 20–50
  field-investigation slots/week** to the reports maximizing expected value.
  Expected value per report = `P(positive | features) × V_detect − c_invest`,
  where `V_detect` is the value of finding/confirming a true hornet (nest
  removal, preventing honeybee losses, first-in-area confirmation) and
  `c_invest` is the per-investigation cost. Because `C_invest` is binding and
  `C_screen` is not, the model **ranks** reports by `P(positive|features)` and
  processes the top `K` each day/week, dropping the rest to a monitoring queue —
  exactly the "rank by posterior, take the top the lab capacity allows" rule.
  The daily cadence (Exchange 6) makes `K` a per-day budget of ~3–7 investigations
  during the season. A report is *promoted* to field investigation if its
  posterior exceeds the threshold implied by the K-th highest score, or if it is
  a first-in-area (Exchange 5) report regardless of marginal posterior.

### Exchange 9 — strongest single discriminator (feature weighting, Q2/Q3)
- **Q:** If you had to put one report at the very top, what feature would matter
  most — location, size, a bee-hive attack, or time of year?
- **Reply:** A **bee-hive attack** (hornets attacking/destroying a honeybee hive)
  matters most — the single strongest positive indicator. It is a **behavioral
  signature** ordinary wasps/yellowjackets do not produce at that scale, implies
  **multiple large hornets** at a **specific, actionable location**, and carries
  **highest urgency** (a colony is being lost and a nest is likely nearby).
  **Location** (inside a known detection zone) and **time of year** (late
  summer/fall, when colonies are large and workers forage widely) are useful
  secondary filters that raise the prior; **size** helps but is often misjudged.
  A credible hive-attack report **outranks all of these**.
- **Used as:** feature weighting and the **urgency override** in Q3. (a) The
  bee-hive-attack indicator `hive_attack` is given the **largest positive weight**
  among text features — it is a near-diagnostic behavioral marker (unlike
  "large," which is misjudged), so it strongly lifts the posterior. This matches
  the data: "bee_words" (hive/bees/honeybee) is a positive cue and hive-attack
  language is the clearest. (b) It adds an **urgency term** to the value function
  `E[V] = P(pos)·V_detect − c_invest + β·urgency`, where `urgency` is high for a
  hive attack (active colony loss, nest likely nearby ⇒ time-sensitive). This
  justifies promoting a credible hive-attack report to field investigation
  even at a moderate posterior. (c) Confirms the seasonality prior peaks in
  **late summer/fall** (colony size + foraging range), consistent with the
  data's July–August detection peak and the problem's life-cycle description.
  (d) Confirms **location** (inside a known detection zone) as the top spatial
  prior — consistent with distance-to-cluster being the dominant feature.

### Exchange 10 — detection completeness (spread precision + eradication, Q1/Q5)
- **Q:** If a hornet is genuinely present, how often is it actually reported and
  confirmed — do almost all turn up, or are many missed?
- **Reply:** **Many are missed.** Detection is strongly incomplete: a genuine
  presence is usually confirmed only when a worker happens to be seen, trapped,
  or caught attacking a hive; **most hornets never generate a confirmed report**.
  Reasons: workers forage over wide areas and are inconspicuous individually;
  public reports are **dominated by mistaken sightings**, so genuine ones are
  diluted; traps sample only a small fraction of the landscape; nests are hidden
  and found late. So confirmed detections are a **small, biased "tip of the
  iceberg"** subset of actual hornet activity. **Absence of confirmed reports is
  weak evidence of absence** unless surveillance effort is high and sustained.
- **Used as:** the **detection probability `p_det`** (per hornet-presence per
  season, probability of at least one confirmed detection) — set **low**,
  central ~0.1–0.3, interval [0.1, 0.5], source: Exchange 10. Three uses:
  (a) **Q1 spread precision** — the observed detections under-sample the true
  process, so the model treats each confirmed detection as a *censored*
  observation; the spread model is fit by likelihood to the *confirmed*
  detections under the censoring `p_det`, and prediction intervals are widened
  accordingly (the model can bound the *rate* and *direction* of spread but not
  the exact number of undetected nests — precision is limited by `p_det`).
  (b) **Q2 base rate** — "public reports are dominated by mistaken sightings"
  is the empirical prior for the low base rate of true positives among reports
  (data: 14 confirmed / 2083 lab-processed ≈ 0.7% of processed, far lower than
  the true-presence prevalence because of the dilution), which sets the logistic
  prior. (c) **Q5** — it is the quantitative content of "absence is weak
  evidence of absence": the eradication rule (Exchange 7) is only valid when
  `p_det` is held high (sustained trapping + reporting); the required
  quiet-period `T*` scales with `1/p_det`, so the 2–3 year threshold assumes
  `p_det` at the high end of its range. This is a **structural assumption**: the
  observation model is a binomial thinning of the true presence process with
  rate `p_det`.

---

## Summary: how the 10 exchanges shaped the model

| # | Parameter / rule | Value (interval) | Where it is used |
|---|------------------|------------------|------------------|
| 1 | W_peak colony workers/season | 100-300 (central ~200) | spread model colony growth (Q1) |
| 2 | tau_erad detection-to-eradication | 1-4 weeks (central ~2) | spread model active window; eradication latency (Q1, Q5) |
| 3 | queen dispersal kernel | typical 1-2 km, hard cap 30 km, rare 10-30 km tail | spread model spatial kernel (Q1) |
| 4 | discriminative cues / look-alikes | size 3-4 cm (queen ~5 cm); orange head; European hornet = main false positive; photos w/o size ref misjudged | classification features; text cues (Q2) |
| 5 | lab confirmation mechanism | photo often enough; specimen for ambiguous/size-less/first-in-area | "investigation" action; Unverified interpretation; first-in-area promotion (Q2, Q3) |
| 6 | triage cadence | daily in season; batch off-season | update frequency (Q4) |
| 7 | eradication threshold | 2-3 clean seasons at active surveillance; lengthens if surveillance drops | eradication rule (Q5) |
| 8 | investigation capacity | 20-50 field investigations/week (3-7/day); screening unconstrained | prioritization K / two-tier resource model (Q3) |
| 9 | strongest cue | bee-hive attack (behavioral signature, highest urgency); location + season secondary | value function urgency override + feature weighting (Q2, Q3) |
| 10 | detection completeness | strongly incomplete; "tip of the iceberg"; absence weak unless surveillance high | p_det censoring (Q1), base-rate dilution (Q2), eradication p_det scaling (Q5) |

Every empirical number the model reports appears either in a per-task parameter
table in solution.json (with value, interval, and the exchange/reference as
source) or comes from the task's own dataset. The expert's wording was NOT
copied into the submission; only the values, constraints, and decision rules
were carried over.
