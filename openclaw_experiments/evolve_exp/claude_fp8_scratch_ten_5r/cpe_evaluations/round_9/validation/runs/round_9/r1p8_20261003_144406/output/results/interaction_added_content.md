# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — Task 2025_C (MM-Bench)

Ten exchanges, mechanism → constraint → parameter sequencing. Each reply is
converted into a named model parameter/constraint below (source = exchange N).
No expert sentence is copied into solution.json; only the calibrated value,
constraint, or decision rule travels, in my own formulation.

## Q1 — Dominant mechanism (structural)
- **Question:** In practice, is the number of medals a country wins driven more
  by how strong and deep its athlete pool is, or by how many medal events it
  actually enters?
- **Reply (gist):** The talent pool depth is the dominant driver; event counts
  are essentially identical for all countries (a shared constant, subject to
  qualification), so they are not a country-specific advantage. What differs is
  how many athletes a country can qualify and how many are world-class.
  Population, wealth, and the sports system (federations, funding, depth)
  explain the US/China/USSR/Germany/UK dominance. Event count matters only at
  the margin — concentrating on sports with many medal events (swimming,
  athletics, gymnastics, rowing) converts a modest pool into more medals, and
  hosts gain from added events/automatic entries — a secondary effect.
- **Used as:** Model structure = **two-factor multiplicative model**:
  `Medals(c,y) = TalentIntensity(c,y) × EventExposure(y)` where talent intensity
  (driven by population/wealth/federation strength) is the country-specific
  primary factor and event exposure is a shared Games-level constant with
  country-specific entry share. Host and sport-concentration are marginal
  multipliers. Source: exchange 1.

## Q2 — Primary constraint
- **Question:** Even for a country with a big pool of talented athletes, what
  mostly limits how many Olympic medals it can actually win in a single Games?
- **Reply (gist):** The binding limit is the **entry/qualification quota
  system**, not talent. A fixed number of athletes per event (≈2–3 individuals,
  1–2 teams) and capped delegation size mean a deep pool converts only a small
  fraction into medal chances. Practical ceiling ≈ (events entered) × (max
  entries per event); the US tops out ~120–130 despite greater depth.
- **Used as:** **Saturation/entry-slot constraint.** Medals are bounded by
  entry slots: `Medals ≤ Entries(c) × p_medal`, and entries are quota-capped
  (2–3/event). Justifies a saturating (entry-limited) response rather than
  unbounded linear growth in talent, and a per-slot medal probability. Source:
  exchange 2.

## Q3 — Conversion parameter
- **Question:** Of the athletes a strong country actually enters across all
  its events, what rough fraction typically win at least one medal?
- **Reply (gist):** **~20–35%** of entered athletes medal; top nations (US,
  China) near the upper end ~30–35%, countries ranked ~5th–15th ~15–25%.
  Team-event medals are shared, so the individual share is a bit higher than
  the raw medal/athlete ratio.
- **Used as:** `p_medal ≈ 0.20–0.35`, with a strength-dependent curve
  (top ≈ 0.32, mid ≈ 0.20). Calibrates the talent→medal conversion. Source:
  exchange 3.

## Q4 — Host-country boost
- **Question:** Compared to the same country competing away from home, how much
  extra does the host country typically gain in total medals? Roughly what
  percentage boost, and why?
- **Reply (gist):** **≈ +10–20% total medals** for the host vs. away; upper end
  for smaller/emerging hosts, lower end for already-dominant hosts. Causes:
  automatic entry, added/shifted events, home crowd/no travel/familiar
  conditions/morale; partly a one-time investment surge. Largest for
  mid-sized hosts (AUS 2000, UK 2012, BRA 2016); smallest for US/China.
- **Used as:** `host_mult(y) = 1 + h`, h ∈ [0.10, 0.20], applied to the host
  country only, larger for smaller base. This is the 2028 LA (US host)
  multiplier. Source: exchange 4.

## Q5 — Great-coach mechanism
- **Question:** When a famous coach moves to a new country's team, what does
  the improvement usually come from — the coach's methods, or the better
  athletes and funding that tend to follow?
- **Reply (gist):** Mostly the **coach's methods/program-building**, not athlete
  influx (citizenship blocks bringing athletes; funding follows after
  results). A great coach changes training systems, talent ID, tactics,
  culture, lifting the existing pool. **Bounded and real, but only where raw
  talent exists and coaching/development is weak**; where the talent base is
  absent, no coach produces medals. Modest and hard to separate from
  concurrent investment.
- **Used as:** Great-coach effect modeled as a **conditional additive boost**
  to a sport's medal expectation: `+coach_boost(sport,c)` applied only where
  `TalentBase(sport,c) > threshold` (participation present, medal tradition
  weak). No effect where talent base ≈ 0. Source: exchange 5.

## Q6 — Great-coach magnitude
- **Question:** When a great coach lifts a sport that already has some talented
  athletes, how many extra medals per Games is that usually worth, over
  several years?
- **Reply (gist):** **Typically 1–3 extra medals per Games** in that sport,
  after a full 4-year cycle; rarely immediate or large. A single breakthrough
  discipline ≈ 1–2; a multi-discipline program overhaul ≈ 3–4 at the high end.
  Gains beyond that reflect concurrent funding/talent surge, not coaching alone.
- **Used as:** `coach_boost ≈ 1–3 medals` per sport (up to 3–4 for a
  multi-discipline overhaul). Bounds the three-country coach-investment
  estimates. Source: exchange 6.

## Q7 — First-medal mechanism
- **Question:** For a small country that has never won an Olympic medal, what
  is the usual first step that finally gets it that first medal?
- **Reply (gist):** Almost always **one exceptional individual in an individual
  (non-team) event**, often a low-barrier sport with many medal events where a
  small nation can concentrate resources, or a diaspora/recruited athlete with
  citizenship eligibility. Routes: diaspora talent, one focused sport, or
  wildcard/universality entries. Not broad depth. Once achieved, it triggers
  funding/participation growth.
- **Used as:** First-medal model = **Poisson "one standout" process**: each
  never-medaled country gets a first-medal probability driven by (a) presence
  of a recruitable/diaspora individual in a low-barrier individual event,
  (b) universality quota entries, (c) concentration of resources in one sport.
  Expected count over the 2028 Games = sum of these per-country probabilities.
  Source: exchange 7.

## Q8 — First-medal count
- **Question:** Of the many countries that have still never won an Olympic
  medal, about how many do you expect to win their first medal at a single
  upcoming Games?
- **Reply (gist):** **Typically 1–3 countries**, occasionally 4–5 in a Games
  with many new events or a large host participation push. Paris 2024 had 4
  (Albania, Cabo Verde, Dominica, Saint Lucia) — on the high side. Low rate
  because it requires one exceptional individual; the eligible pool is small.
- **Used as:** Calibration anchor: **E[# first-medal countries at 2028] ≈ 1–3**
  (LA 2028 is a host with a participation push → toward the 3–4 end). Source:
  exchange 8.

## Q9 — Prediction-interval width
- **Question:** When you predict a top country like the US will win a certain
  total of medals, how wide should the honest range of outcomes be?
- **Reply (gist):** An honest **80–90% interval ≈ ±15–20 total medals** (e.g.,
  point ~120 → range ~100–140). US total has ranged ~100–130 across recent
  non-boycotted Games; swings of 10–15 are common. **Golds: ±8–12.** Spread
  from host effect, program changes, form/injury of a few multi-medal stars,
  and team-sport runs worth 5–10 medals at once.
- **Used as:** Uncertainty specification: total-medal σ ≈ 15–20 (≈ 1.25×σ for
  80–90%), gold σ ≈ 8–12, for a top country; scaled by base size for smaller
  countries. Sources of variance enumerated in the model. Source: exchange 9.

## Q10 — Biggest non-host disruptor (insight)
- **Question:** Aside from the host country, what is the biggest single factor
  that makes a strong country's medal count jump or drop sharply from one
  Games to the next?
- **Reply (gist):** The biggest non-host factor is **systemic disruption of the
  athlete pipeline** — a boycott or absence/return (1980/1984 swung US/USSR by
  30–60 medals), or collapse/emergence of a state sports system (post-1991
  Soviet breakup redistributed a superpower across a dozen NOCs; China's rise
  added a new top-tier contender). Dwarfs normal variation. Absent shocks, the
  next factors are **turnover of a few multi-medal stars** (a swimmer/gymnast
  worth 4–6) plus **sport-program changes** adding/cutting events a country is
  strong in. Episodic, not routine.
- **Used as:** (a) Insight section — medal time series are dominated by
  episodic pipeline shocks, so a model must not extrapolate linearly;
  (b) **outlier handling:** boycott years (1980, 1984) and the Soviet
  dissolution (1992 onward) are excluded/flagged in the calibration window;
  (c) variance model adds a "star-turnover + program-change" shock term on top
  of the host term. Source: exchange 10.

## Termination
All 10 exchanges used. The mechanism (talent depth), its constraint (quota
entry slots), and the critical parameters (conversion rate, host boost,
coach-effect size, first-medal count, interval width, shock structure) are all
empirically grounded. No further expert feedback is requested; the model is
built below.
