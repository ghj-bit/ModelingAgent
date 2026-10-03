# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction evidence — MM-Bench 2002_C (Florida scrub lizard)

Ten expert exchanges, one question each. For every exchange: the question, the
reply (gist), and the concrete work the reply produced in the model.

## Exchange 1
**Q:** What is the biggest day-to-day threat to Florida scrub lizard habitat on military ranges like Avon Park Air Force Range?
**Reply:** Fire suppression and vegetation encroachment (~6%/yr closing of open
sandy scrub), compounded by unexploded ordnance and safety limits that make
controlled burns hard to run; fragmentation and range infrastructure secondary.
**Work:** Threat ranking for Task 1: fire suppression/encroachment = primary,
fragmentation + infrastructure = secondary. Encroachment rate 6%/yr (from the
problem) drives the Task 5 encroachment sweep and the Task 6 burn policy.
Parameter: `encroach = 0.06/yr, interval [0.03, 0.09]`, source: problem
statement + exchange 1 (expert confirmed it is the binding threat).

## Exchange 2
**Q:** Every few years, does a single scrub lizard survive its trip to another patch, or do they all usually die?
**Reply:** Dispersers usually survive the trip; recapture data measure movement
and short-term survival up to 6 months, not establishment; the bottleneck is
the destination patch's open sandy area.
**Work:** Task 4: migration survival treated as high (~0.95–0.99) rather than
lethal; the metapopulation model (Task 5) applies a 0.97 trip-survival factor
to emigrants, and the establishment step is the destination patch's C_i, not a
separate mortality.

## Exchange 3
**Q:** How many lizards can one acre of open sandy scrub realistically support before food runs out?
**Reply:** Not food-limited; ceiling set by space/shelter; order of magnitude
~5–20 lizards per acre (~10–50/ha in good open sandy habitat); the Table 2
density column is the anchor.
**Work:** Task 5: density is per open-sandy hectare (not per total patch
hectare), so C_i = D(H_i)·H_i with D anchored on Table 2. Expert range
[10, 50]/ha is reported as the validation band for D; the fitted D(H) gives
50–64/ha across the landscape, at the upper edge of that band (densities rise
with sandy area).

## Exchange 4
**Q:** How far from the open sandy center does a lizard need to travel to reach another patch?
**Reply:** No single distance; the histogram's 350 m survey radius is the outer
limit of detectable movement; tens to a few hundred meters, not kilometers;
>~350 m of unsuitable matrix ≈ isolation.
**Work:** Task 4: survival function defined only on [0, 350] m (empirical CDF
of the histogram); Task 5: inter-patch trip survival 0.97 = P(survive) at the
350 m boundary (exponential fit to the histogram, λ≈0.01/m); patches farther
than ~350 m apart in the matrix are treated as effectively isolated (no map
coordinates supplied, so exchange is scaled by C_i with that caveat stated).

## Exchange 5
**Q:** How many lizards can a patch hold before its population stops growing?
**Reply:** Carrying capacity set by open sandy area (space/shelter),
~10–50 lizards/ha; C_i ≈ open sandy area × that density.
**Work:** Confirms the Task 3/5 construction C_i = D(H_i)·H_i as the carrying
capacity function; viability rule C_i ≥ 10 lizards.

## Exchange 6
**Q:** In real scrub areas, does the population crash right after a fire, or recover quickly?
**Reply:** Transient dip after a burn (direct mortality + lost cover), then
recovery over ~1–3 years; often higher densities than pre-burn overgrown
conditions; danger is too-frequent burns or, more common, fire suppression.
**Work:** Task 6 burn simulation: burn year = 0.7 multiplier (30% dip),
recovery boost λ+0.10 while cover ≤ 0.5; the policy conclusion that
suppression (no burns) is the worst outcome, not burning itself.

## Exchange 7
**Q:** What does a scrub patch look like when it's doing well for its lizards?
**Reply:** Open, sandy, low and patchy: bare/sparsely vegetated sand dominant,
low scattered shrubs, full sun for basking/nesting, maintained by periodic
fire.
**Work:** Task 1 description of target habitat state; Task 6: "healthy" cover
band = low, sparse vegetation (the burn_low side of the reset band); Task 5:
the sand-ratio H/S column is the health indicator (healthy patches ≈ open and
sandy).

## Exchange 8
**Q:** How much of a scrub patch should stay open and sandy for the lizards to thrive?
**Reply:** No precise threshold; ~half or more open sand = good habitat,
<~20–30% = marginal/unsuitable; use the sandy/total ratio.
**Work:** Task 5 viability: patches with sand ratio < 0.2 flagged
unsuitable (e.g., patches 18: 0.08, 26: 0.93 is high but tiny; 3: 0.17,
20: 0.18, 14: 0.18, 23: 0.20 marginal); the ratio column is reported with
every landscape result.

## Exchange 9
**Q:** About 10% of juveniles leave a patch: does that usually help it or hurt it?
**Reply:** Usually helps both the source (relieves density pressure) and the
landscape (recolonization, sustains small patches); only if the destination is
suitable.
**Work:** Task 5 metapopulation: emigration is not net harm — the model
accounts for the 10% juvenile loss against the density relief and the
immigration gain (immig vs out_emig per patch); the source-patch net growth
includes −out_emig explicitly.

## Exchange 10
**Q:** When does the Florida scrub lizard start leaving its home patch to find a new one?
**Reply:** Ontogenetic: between birth and first reproductive season (first
year), ~10% of juveniles; adults do not migrate.
**Work:** Task 5: the migration term is applied only to the juvenile cohort
(0.10 × Fa×Sj×C_i emigrants per year), never to the adult pool; Task 4's
survival probability is a juvenile-trip probability. Model structure fixed:
one-pulse juvenile dispersal per year.

## Parameters supplied by exchanges (also in solution.json)
- `encroach = 0.06 /yr, interval [0.03, 0.09]` — problem statement (aerial
  photos) + exchange 1 (confirmed as the binding threat).
- `migrate = 0.10` of juveniles — problem statement, exchanges 9–10
  (ontogenetic timing, net-beneficial role).
- `D ≈ 10–50 lizards/ha open sand` — exchange 3/5 (empirical band; Table 2
  density column is the fitted anchor, D(H) = 50.24 + 0.6927·H, R²=0.84).
- `trip survival ≈ 0.97 at 350 m; ≤350 m is the movement domain` —
  exchanges 2, 4 + histogram data.
- `burn: 30% transient dip, 1–3 yr recovery, suppression is the worst
  outcome` — exchange 6.
- `suitable habitat ≈ ≥50% open sand; <20–30% marginal` — exchange 8.
