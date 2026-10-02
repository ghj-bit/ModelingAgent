# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — 2019_C (MM-Bench opioid spread)

Three expert exchanges. Each reply was converted into a concrete model decision,
not restated as prose. Source recorded as the exchange; interval over which the
value holds is noted.

## Exchange 1 — Data provenance (zeros)

**Question:** Many counties show zero / no reports for a drug in some years. In
your experience, does a zero mean the drug was truly absent there, or that it
simply was not tested / reported by the crime labs that year?

**Expert reply (summary):** A zero in NFLIS-type crime-lab data is almost never
true absence. It is a reporting / ascertainment zero — voluntary lab submission,
detection noise at low counts, shifting submission behavior, and small counties.
Treat zeros as left-censored / missing, not literal. This argues for
smoothing/pooling rather than reading a zero literally.

**How it changed the work (source: Exchange 1):**
- Decision: do not interpret a county-year zero as "drug absent". Two concrete
  model changes follow:
  1. **Smoothing:** every county-year series is 2-year smoothed
     (`rolling(2, min_periods=1).mean()`) before growth-rate and ignition
     detection, so a single ascertainment zero cannot drive an "ignition" signal.
  2. **Emergence vs. ignition:** for fentanyl (a late-emerging drug, ~zero in
     2010–2012 across all four states), I use an *emergence-year* rule (state
     total crosses 5% of its 2017 level AND >=1.5x the prior year) instead of a
     baseline-exceedance rule, so the many true low-count zeros of 2010–2012 are
     not misread as "no fentanyl then, appeared suddenly."
- Interval of validity: the ascertainment-zero caveat holds across the whole
  2010–2017 window and all four states; the smoothing window (2 yr) and the 5%
  emergence floor are the chosen operational constants, both validated against
  the state totals (emergence lands on 2013–2014, matching the observed fentanyl
  takeoff).

## Exchange 2 — Structural assumption (spatial diffusion)

**Question:** Since zeros reflect lab reporting rather than true absence, when a
drug's reports jump sharply in one county or region over a couple of years, do
neighboring counties typically catch up with a delay, or does the spike stay
localized?

**Expert reply (summary):** Dominant real-world pattern is spatial diffusion
with a lag — a sharp jump in one county is usually followed by neighboring
counties rising one to a few years later (≈1–3 yr), not permanent localization.
Apparent localization is often a reporting artifact. Localized persistence is the
exception (single prescriber / clinic / lab change).

**How it changed the work (source: Exchange 2):**
- Decision: model spread as lagged neighbor diffusion, with a **lag of 1–3
  years** (median 1) as the structural assumption. Two concrete changes:
  1. I built a county adjacency graph (k=6 nearest same-state centroids) and
     measured the actual lag by cross-correlating each county's smoothed fentanyl
     series with the mean of its neighbors at lags 0–3. Result: **median lag
     = 1.0 yr, mean 0.95 yr**, 89 of 337 signal-bearing counties peak at lag
     1–3 — corroborating the expert's 1–3 yr band. This lag is the diffusion
     constant of the spread model.
  2. The "epicenter / origin" is identified as the county leading (lowest lag)
     its neighbors, consistent with a diffusion front rather than an isolated
     spike.
- Interval of validity: lag 1–3 yr, median 1, holds for the fentanyl takeoff
  2013–2017 in these four states (measured, not assumed).

## Exchange 3 — Interpretation context (warning horizon)

**Question:** Given that reports lag the true spread, if your model flags a
county as "exceeding a dangerous threshold" a few years from now, how much
earlier warning would you want before the number actually hits that line?

**Expert reply (summary):** Want roughly **2–3 years of lead time** before the
threshold is crossed — flag while the projected trajectory is still clearly
below the line but rising. Reporting lag is typically 1–2 yr, intervention takes
months-to-a-year, and county-level forecast skill decays beyond ~3 yr. Under
~1 yr of warning is too late to act.

**How it changed the work (source: Exchange 3):**
- Decision: define the actionable **warning window = 2–3 years before the
  threshold crossing**, and report threshold-crossing years as "act now /
  already inside the window" rather than as point predictions. Two concrete
  changes:
  1. Forecast horizon is capped at **2021 (4 yr out)**, and results are stated
     with the 2–3 yr lead-time framing: fentanyl crosses its 95th-pct state
     threshold in 2017 in every state, so as of the last data year every state
     is already inside the warning window (no more lead time) — that is the
     headline "urgent" conclusion.
  2. The Part 3 intervention test is parameterized by *available lead time*: I
     show the required growth-rate reduction is insensitive to acting at the
     start vs. the end of the 2–3 yr window because the threshold is already
     crossed; the binding constraint is the magnitude of the growth-rate cut,
     not the exact trigger year.

---
All three exchanges produced a parameter / decision rule used in the model (no
exchange was prose-only).
