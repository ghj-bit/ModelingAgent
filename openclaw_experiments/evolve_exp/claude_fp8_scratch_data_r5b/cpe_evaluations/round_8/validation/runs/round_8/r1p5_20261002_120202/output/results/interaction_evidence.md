# Interaction evidence — 2018_C

Three expert exchanges, one question each. For each: the question, the reply,
and how the reply was turned into work (a parameter/constraint/equation/decision
rule, not prose). No expert sentence is copied into solution.json; only the
value/constraint travels, in our own formulation.

## Exchange 1 — Operational mechanism (governs the Part I.B evolution model)

**Question:** Over the past 50 years, in a typical western US state, has the share
of energy from cleaner and renewable sources tended to grow slowly and steadily
year after year, or does it usually stay flat for a long time and then jump
upward when a new power source, like big hydro dams or large wind farms, comes
online?

**Reply (summary):** Neither pattern dominates cleanly. The renewable share is
mostly flat for long stretches and steps up when large capacity is added, but the
steps are modest and can be partly offset by growth in total demand. Over 1960–2009
the big renewable source was large hydro, which came online decades earlier, so
its share was already substantial and then roughly flat or declining as total
energy use grew. Wind and solar additions were small until the 2000s, when wind
farms began adding visible increments. Net: long flat periods punctuated by
discrete upward steps, no smooth year-after-year growth.

**Turned into work:**
- Structural constraint on the Part I.B model: the renewable share is modeled as a
  STEP process, not a smooth trend. Flat plateaus (hydro, geothermal, biomass — the
  sources that came online long ago) plus logistic ramps (wind, solar — the 2000s
  frontier sources), on top of a log-linear demand trend. A single exponential or
  linear fit to the share is explicitly rejected as the wrong mechanism.
- Verified against the dataset before adopting: wind steps in NM (2004–09: 1,871 →
  15,096 T Btu) and TX (2001–09: 816 → 195,455 T Btu) while hydro is flat — matches
  the step structure. Fitted share MAE 0.36–4.07 pp across states.
- Source recorded in solution.json parameter table as "expert exchange 1".

## Exchange 2 — Causal hierarchy / dominant drivers (governs Part I.D forecast drivers)

**Question (built on Exchange 1):** When projecting a state's future energy use
with no new government action, which single real-world factor do you find most
shapes whether a state adds more wind and solar in coming decades, and why does
that factor matter more than the others?

**Reply (summary):** The decisive factor is the relative cost of new generation —
the delivered cost of new wind/solar versus the marginal cost of running existing
fossil plants, including cheap in-state natural gas. In the absence of new policy,
investment follows economics: a state with abundant cheap gas (notably Texas)
meets load growth with low-cost dispatchable generation so renewables penetrate
mainly where already cost-competitive; a state with high fossil costs and strong
wind/solar resource (California, increasingly New Mexico and Arizona) adds
renewables because they are the cheapest new option. Geography, population growth,
and climate shape the level of demand but do not by themselves trigger a mix shift.
Empirical judgment, not a precise figure.

**Turned into work:**
- The Part I.D no-policy forecast is split into two coupled projections with
  different drivers, exactly as the reply prescribes:
  - demand LEVEL E(t) driven by geography/population/industry (the fitted log-linear
    growth rate g per state);
  - renewable MIX driven by relative cost — i.e., the forecast does NOT assume the
    share rises on its own. The only non-policy mix movement is a decelerating
    "cost-creep" term (wind/solar costs keep falling for learning/technology reasons),
    calibrated to the 2000–2009 frontier growth.
- Consequence (reported, not assumed): with no policy, every state's renewable
  SHARE falls, because the fossil base grows and the renewable step stops at its
  2009 level. This is the "do nothing" baseline the compact must beat.
- The cost-continuation (creep) term and the cheap-gas caveat for TX are recorded
  in the Part I.D analysis and the parameter table as "expert exchange 2".

## Exchange 3 — Decision-relevant uncertainty threshold (governs Part II.A targets)

**Question (built on Exchange 2):** When governors set a 2050 renewable-energy
target for a state, roughly how far off would your 2050 estimate need to be before
you would call the number too unreliable to base that long-term policy goal on?

**Reply (summary):** Rule of thumb: if the 2050 estimate could plausibly be off by
more than about a factor of two — or, as a share, if the projected renewable share
could reasonably land more than roughly 15–20 percentage points away from the point
estimate — it is too unreliable to anchor a binding 2050 target. 2050 is 40+ years
out and the dominant drivers (fuel prices, technology cost curves, federal policy,
demand growth) are not forecastable better than order-of-magnitude. Practical
implication: base the 2050 goal on a range or directional commitment (e.g.,
"renewables to become the majority source") rather than a single hard percentage,
and reserve precise numeric targets for nearer horizons (2025, maybe 2035).
Empirical judgment.

**Turned into work:**
- Part II.A targets are made asymmetric in precision to respect the threshold:
  - 2025 (≈16 years out, tighter): a PRECISE per-state number = no-policy 2025
    floor + 4 pp policy uplift (CA 11.4%, AZ 9.1%, NM 7.5%, TX 6.3%; 4-state
    energy-weighted ~8.4%).
  - 2050 (41 years out, point estimate off by >~2x / >15–20 pp possible): a RANGE
    plus directional commitment — "renewables become the majority source (>50%),"
    with a planning floor of ~16–21% and ceiling ~60% per state (4-state floor
    ~18%). A single 2050 number is explicitly NOT given, per the threshold.
- The threshold value (factor-of-two / 15–20 pp) is recorded in the parameter
  table and the Part II.A analysis as "expert exchange 3".
