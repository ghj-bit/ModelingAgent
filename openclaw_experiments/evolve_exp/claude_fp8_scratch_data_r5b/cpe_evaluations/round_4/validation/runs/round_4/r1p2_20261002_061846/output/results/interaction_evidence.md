# Interaction evidence — problem 2006_C

Three expert exchanges, one question each, in the order they governed the work.
Controller-managed request/reply files: `logs/operator_feedback/expert_{question,reply}_N.md|json`.

## Exchange 1 — data provenance

**Question** (≤20 words): *Do such label variations and missing entries in a WHO
data file usually mean the country was not measured, rather than a low or zero rate?*

**Reply (gist):** blanks/absent rows mean "not reported / not measured", not zero;
label variation ("USA" vs "United States", "Russian Federation" vs "Russia") is
naming inconsistency, not missingness; the blank TT2 cell for the USA is a
reporting artifact (the USA does not use TT2 as a routine indicator), undefined,
not 0.

**How the reply became work (code/`model.py`):**
1. `load_data()` now normalizes labels before any join
   (`g["country"].str.strip().replace({"USA": "United States of America"})`,
   same fix on the income and vaccination sheets) — this is what made the USA
   and Russian Federation rows joinable at all.
2. Absent 1999 counts are treated as *unknown*, never 0: the two affected
   selected countries (USA, Russia) get imputed 1999-2001 adult prevalences
   (USA 0.0062, Russia 0.0004; GDB country estimates,
   search.py: https://doi.org/10.1016/s0140-6736(17)32154-2) multiplied by the
   task-dataset adult pool, and the imputation is flagged in `inputs.*.cases_src`.
3. The blank TT2 for the USA is replaced by `0.6 × DTP3` as an explicit
   documented proxy (USA DTP3 = 93.9%); using 0 would have zeroed the USA
   adult-cohort vaccine ceiling, exactly the distortion the reply warned about.

## Exchange 2 — structural assumption

**Question** (≤20 words): *In countries hard hit by AIDS for decades, does the
number of infections level off or keep rising, and why?*

**Reply (gist):** incidence flattens (true saturation of the susceptible pool);
the infected *count* plateaus rather than growing without bound, but the plateau
can be very high and is set by the balance of new infections against AIDS
mortality, not by saturation alone; a pure logistic on cumulative infections
ignoring mortality under/over-states the plateau — without treatment the
plateau is reached sooner and lower.

**How the reply became work:**
1. The model's core equation was built as an SIS steady state,
   `I*(y) = S(y)·r_eff(y)/d_eff(y)`, i.e. the count is the balance of new
   infections (`S·r_eff`) and removals by death (`d_eff`), not a logistic on
   cumulative infections. The relaxation
   `I(y) = I(y-1) + (I* − I)·min(1, d_eff)` makes the plateau level and its
   approach speed both mortality-driven.
2. Consequence checked in the results: in the no-intervention scenario the
   plateau of `I` tracks the mortality term — e.g. South Africa I(2050) = 4.28M
   vs 4.20M in 1999 because the calibrated incidence ≈ death removal at
   equilibrium; India's count keeps rising only because its adult pool grows
   (3.70M → 4.95M), i.e. the demographic drift the reply described, not
   unbounded transmission growth.
3. The reply also fixed the reporting quantity: the model records `inc`
   (annual new infections = `I*·d_eff`) and `dth` separately, so that the
   prevalence-vs-incidence distinction of Exchange 3 is computable from the
   same run.

## Exchange 3 — interpretation context

**Question** (≤20 words): *When deciding whether to fund treatment versus
prevention, would a planner mainly care about the difference in projected
infection counts, or about something else?*

**Reply (gist):** a planner compares infections averted (incidence, not the
standing count — ARV raises prevalence by keeping people alive, so raw counts
make ARV look worse than it is) and cost per infection averted; the two
interventions act on different parts of the process and are complementary.

**How the reply became work (code/`analyze.py` and the Task 4 numbers):**
1. Scenario comparison was computed as *incidence averted*
   (`Σ_y [inc_none(y) − inc_scenario(y)]`, 2006-2050, person-years), not as the
   difference of the `I` counts. Results: ARV averts 15.6M person-years of
   infections at $421.8B (≈$27,100 per averted person-year); vaccine averts
   25.3M at $0.71B (≈$28); both averts 31.3M at $283.0B.
2. This is precisely why the ARV scenario *raises* the 2050 count in the base
   run (South Africa 4.28M → 6.21M) while still averting 15.6M person-years of
   new infections — the two views are both reported, and the allocation
   recommendation in Task 4 is written on incidence-averted / cost-per-infection
   av averted, as the reply requires.
3. The white-paper framing (white paper to the UN) uses cost per infection
   averted at the margin as the decision metric, with the complementary-roles
   argument (treatment acts on the survival/infectivity side, the vaccine on
   the susceptible-pool side) carried over into the Task 4 text.
