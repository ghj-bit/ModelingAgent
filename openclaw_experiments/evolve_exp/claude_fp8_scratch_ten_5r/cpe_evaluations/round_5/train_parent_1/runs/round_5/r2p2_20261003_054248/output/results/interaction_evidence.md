# Expert interaction evidence — 2021_C (MM-Bench)

All 10 exchanges completed. Questions were about real-world practice; each reply
was turned into a model input before the next exchange.

| # | Question (abridged) | Reply (value/range) | Where it entered the model |
|---|---|---|---|
| 1 | First thing the field team wants from a caller | A clear photo/video is the single strongest discriminator; without one, precise location+date | Feature `img` (photo/video attached) in the misclassification logistic model; feature set for the priority score |
| 2 | Who among no-photo callers can supply a specimen | Beekeepers / ag / insect hobbyists — they trap and preserve; ordinary homeowners rarely keep a body | Feature `cred` (reporter self-identifies as beekeeper/entomologist/citizen scientist) and `spec` (specimen/capture mentioned) |
| 3 | Realistic monthly field-verification capacity | ~20–60/month (few-dozen), up to ~100 in surge, <20 off-season | Capacity constraint C=40/month used for the top-N investigation list and cost argument |
| 4 | Most trust-building / most doubt-inducing element | Corroboration by a second report or a knowledgeable accurate description; doubt from vague generic descriptions + location/time that doesn't fit, post-media clusters | Ranks `cred`/`spec` above bare size claims; distance-from-cluster and season terms in the spatial prior; media-spike effect treated as a volume shock, not a true-positive signal |
| 5 | Response window for fresh report near active area | Same-day to 3 days; beyond ~1 week deprioritize unless new corroboration | Feature `fresh` (submission within 7 days of detection); freshness multiplier in priority score |
| 6 | Standard for declaring eradication | Several consecutive zero-confirmed seasons (typically 3, 2–5), against *active* surveillance; lapsing surveillance voids the count | Eradication analysis: K consecutive zero-discovery seasons inverted against the cluster-discovery Poisson; surveillance-maintenance condition stated |
| 7 | Fresh distant sighting away from known nests | Triage, don't rush; prior is mis-ID; strong corroboration (photo/specimen/knowledgeable observer) jumps the queue | Priority = predicted P(AGH) × corroborating factors; distance alone lowers, not raises, priority (matches data: only 9% of spring-2020 reports within 30 km) |
| 8 | Media-spike effect on call volume | Several-fold to order-of-magnitude spike for 1–3 weeks, decaying; surge is low-quality no-evidence reports; positive rate per report drops sharply | Weekly-volume Poisson with step shocks at the 3 media events; deviance/Pearson dispersion reported; spike modeled as volume, not signal |
| 9 | Spring re-detection after winter | Same infestation continuing (overwintering queens); winter gap must not reset spatial prior; only far+corroborated spring sighting = new incursion | Seasonal continuity assumption in the spread model; no spatial-reset in the priority scoring across seasons |
| 10 | Report-checking cadence in peak season | Daily triage/re-ranking; batched field deployment; re-score on new confirmations or clusters; weekly in off-season | Update strategy: daily re-scoring during active season, triggered re-scoring on confirmations; batched C=40/month deployment |

## Parameter table (empirical inputs with provenance)

- `queen_founding_range = 30 km, interval [30, 30], source: problem statement (task dataset description)`. Used as `near30` boundary and the "one queen-range" band in the spread/eradication analysis.
- `monthly_field_capacity = 40, interval [20, 60] (up to ~100 in surge), source: exchange 3`. Used for the top-N investigation list and cost argument.
- `response_freshness_window = 7 days (same-day–3 days act; >1 week stale), interval [1, 7], source: exchanges 5 and 10`. Used as `fresh` feature and priority multiplier.
- `eradication_zero_seasons = 2 (full, active-surveillance) to 3 (reduced), interval [2, 3] (policy range 2–5), source: exchange 6, cross-checked against the fitted discovery Poisson`. Used in the eradication-evidence calculation.
- `media_spike = several-fold, decaying over 1–3 weeks, source: exchange 8`. Used as step-shock indicators in the weekly-volume model (magnitudes estimated from data).
- `spring_redetection = continuation, not new incursion (unless far + corroborated), source: exchange 9`. Structural assumption of the spread model.
- `misID_baseline = 1 − 14/2048 = 0.9932, Wilson 95% CI [0.9886, 0.9959], source: task dataset (labeled outbreak-era records)`. Baseline misclassification rate.
- `cluster_discovery_rate mu = 1.0 per season, 95% CI [0.24, 5.57], source: task dataset (2 WA cluster discoveries over 2 active seasons, Poisson MLE)`.
- `vespa_mandarinia_life_cycle = one active season (Apr-Oct in WA), overwintering as mated queens in soil; workers die in winter, new colonies founded each spring; related: six-year control/eradication plan for the close relative V. velutina, DOI 10.1002/ps.6264 (retrieved via crossref, confirms multi-year control campaigns as standard for invasive giant hornets); invasion-dynamics simulations for V. mandarinia, DOI 10.7717/peerj.10690 (retrieved via crossref)`. Used for the seasonal structure of the spread model and the multi-year eradication standard.
- `inrange_passive_positive_rate = 9/152 = 0.059, Wilson 95% CI [0.0315, 0.1087], source: task dataset (2020 labeled reports within 30 km of a confirmed cluster)`.
