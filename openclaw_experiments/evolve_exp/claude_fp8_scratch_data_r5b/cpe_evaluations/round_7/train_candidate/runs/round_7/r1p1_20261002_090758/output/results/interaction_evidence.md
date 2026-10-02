# Interaction Evidence — Problem 2019_C (Opioid crisis, 5 states)

Three fixed exchanges, one question each. Each reply was turned into a concrete
model component before the next question was asked. No reply text is copied into
the submission; only the values, constraints, equations, and tests travel.

## Exchange 1 — Core structural assumption (asked before building the model)

**Question:** When drug lab reports go up in one county over a few years, does
that usually mean actual drug use there really rose by about the same amount, or
can it rise even when actual use didn't change much?

**Reply (gist):** Lab reports can rise substantially without a matching rise in
actual use. Counts measure *enforcement and testing activity*, not consumption.
Divergence comes from reporting/processing artifacts, enforcement intensity,
composition shifts (heroin→fentanyl), and small-county noise (a handful of cases
can double a small county's count). A several-fold rise in one county is weak
evidence of a proportional rise in use; directional trends across many counties
are more trustworthy than any single county's magnitude.

**How it changed the work:**
- The model's output variable is defined as *reported identifications*, and every
  rate is computed **per 100,000 population** (population from the ACS extract),
  never as a raw count. This is the structural fix: it removes the
  population-scale reporting channel before any interpretation.
- A **small-county noise floor** was added: counties below a minimum population
  are flagged and their single-county magnitudes are not used as evidence of a
  "source"; only cross-county directional patterns are.
- Single-county spikes are treated as candidate reporting artifacts, not
  evidence of origin. Origin detection therefore requires a *sustained* rise,
  not a one-year jump.

## Exchange 2 — Causal mechanism / directionality (built on reply 1)

**Question:** When a county's opioid reports are high, is that because the area
genuinely has more drug use, or because more police are searching and submitting
samples there?

**Reply (gist):** Both, and usually entangled — but the enforcement/submission
side explains more of the *variation between counties* than actual use does.
High-report counties typically have an active task force, a busy lab, aggressive
interdiction (interstates, metro corridors), or a large institutional population
(jails, rehab) that generates submissions. A county can post high counts with
modest true prevalence. Treat county-level counts as a joint signal of use *and*
enforcement; be cautious about ranking counties by "actual drug problem" from
report volume.

**How it changed the work:**
- County **ranks are interpreted as concentration of the reported signal, not
  as a severity/need ranking**. The write-up states this limitation explicitly
  and never presents a "worst county" list as a drug-use ranking.
- The Part 2 regression is framed as **association, not causation**: census
  socio-economic factors are tested as correlates of the reported signal, and the
  write-up notes the enforcement channel can confound any such association.
- A **population-normalized rate** is the covariate throughout (rate, not count),
  so the between-county enforcement/population channel is at least partly
  controlled before testing socio-economic association.

## Exchange 3 — Interpretation context / decision threshold (built on reply 2)

**Question:** For deciding where to send resources first, what level of opioid
activity in a county would you treat as an emergency demanding immediate action,
versus a slow-building problem to watch?

**Reply (gist):** No defensible absolute *count* threshold exists — the same
number means different things in a county of 5,000 vs 500,000. Judge on **rate
and trajectory, not raw volume**. Emergency-level (order-of-magnitude, empirical
judgment): roughly **100+ opioid identifications per 100,000 population per year,
sustained 2+ years**; a **doubling within ~2–3 years** from an elevated base, or
a **sharp shift toward fentanyl/synthetic opioids**; a county that is an
**early riser relative to its neighbors** (first in a cluster to climb) — where
seeding appears. Slow-building/watch: low rate with flat/gently-rising trend, or
high counts explained by a single lab, jail, or task force. Caveat: because
counts mix use and enforcement, an aggressive task-force county may overstate
need and a weak-enforcement county may understate it; confirm with an independent
indicator before committing resources.

**How it changed the work:**
- The Part 3 **threshold and classification rules are fixed to these values**:
  emergency iff rate ≥ 100/100k/yr sustained 2+ years; warning on a doubling in
  ≤3 years or a compositional shift to fentanyl; seeding on early-riser status.
  These enter `part1_analysis.py` / `part3_strategy.py` as named constants with
  the interval [source: expert exchange 3, order-of-magnitude judgment].
- **Rate + trajectory + neighbor comparison** is the decision rule, not raw
  volume. The "where and when" forecast uses the Part 1 national trajectory
  extrapolated to the per-100k emergency threshold.
- The strategy's effectiveness test is bounded by the caveat: success depends on
  the enforcement-mix bias being small enough that rate+trajectory is a valid
  triage signal; this is the key parameter bound reported in Part 3.

## Parameters sourced from the exchanges (also in solution.json parameter table)

| name | value / interval | used in | source |
|---|---|---|---|
| emergency_rate_threshold | 100 identifications per 100k per year (order-of-magnitude) | Part 1 thresholds, Part 3 triage | expert exchange 3 |
| emergency_sustain_years | 2 (years the rate must be sustained) | Part 1 thresholds, Part 3 triage | expert exchange 3 |
| warning_doubling_years | ≤3 (years to double from elevated base) | Part 1 "when" forecast, Part 3 | expert exchange 3 |
| compositional_shift | fentanyl share rise as a warning trigger | Part 1 composition, Part 3 | expert exchange 3 |
| county_signal_interpretation | counts = joint use+enforcement signal; rank = concentration not severity | Part 1/2 interpretation | expert exchange 2 |
| rate_normalization | all rates per 100,000 population | all parts | expert exchange 1 |
| small_county_noise_floor | single-county spikes in small counties = artifact risk | Part 1 origin detection | expert exchange 1 |
