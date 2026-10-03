# Interaction evidence — 10 exchanges

All ten exchanges completed; one question each, each building on the previous reply.
Files: `logs/operator_feedback/expert_question_N.md` / `expert_reply_N.json`.

## E1 — Dominant mechanism: why habitat is lost
- **Q:** When a Florida scrub patch is burned to keep it open, what is the single biggest practical obstacle to carrying out the burn?
- **Reply (gist):** smoke management and liability — keeping smoke off roads/populated areas; narrow weather windows; burns often cancelled at short notice.
- **Turned into work:** Task 1 obstacle list and Task 6 scheduling constraint (burns are weather-window-limited; crew capacity caps how many patches burn per year). Recorded as constraint in Task 1/6 analysis.

## E2 — Structural anchor: what preservation must prioritize
- **Q:** When Florida managers preserve scrub lizard habitat, which matters more: keeping each patch large, or keeping many patches close together?
- **Reply (gist):** connectivity matters more, because lizards are poor dispersers and a single large isolated patch is vulnerable to local extinction; but there is a minimum-area floor below which a patch is unoccupiable — configuration first, not below the size floor.
- **Turned into work:** Task 1 recommendation hierarchy (corridors/retention over single big reserves); Task 5 viability test requires BOTH a size floor AND positive reproduction — the floor is E3's number.

## E3 — Parameter: the size floor
- **Q:** Roughly how many acres of scrub does a patch need before it can hold a self-sustaining group of scrub lizards?
- **Reply (gist):** on the order of a few tens of acres; commonly cited minimum viable patches ≈ 20–50 acres (≈ 8–20 ha) of suitable open sandy scrub; larger (hundreds of acres) for long-term persistence. Empirical judgment.
- **Turned into work:** viability floor `min_acc = 12 ha` sandy (midpoint of 8–20 ha), source = this exchange. Used in Task 5 patch classification; sensitivity: at 8 ha patches 2, 15, 17 become viable (3 viable total); at 20 ha only patch 12 survives.

## E4 — Constraint on the mechanism: how closing-over acts
- **Q:** When a Florida scrub area is left unburned for years, what mainly happens to the young scrub lizards?
- **Reply (gist):** open sand closes with shrubs/oak; juveniles hit hardest (lose basking/foraging ground, higher predation); population ages and declines.
- **Turned into work:** Task 6 time-dependence — burn benefit is not immediate and fades if unburned again (with E8); Task 5 limitation: fitted rates assume maintained open habitat, so a closing patch's Sj and Sa fall below the fitted curve.

## E5 — Parameter: closing timescale
- **Q:** About how many years can a Florida scrub area go between burns before the open sand gets badly taken over?
- **Reply (gist):** 5–15 years, practical target every 5–10; by 10–15 years open sand largely gone.
- **Turned into work:** Task 6 burn-interval window [5, 15] yr; degradation tau = 10 yr (open-sand fraction ~ exp(-age/10)); 8-year rotation keeps patches inside the window.

## E6 — Constraint: migration range
- **Q:** How far can a young scrub lizard realistically travel between scrub patches in order to survive the trip?
- **Reply (gist):** a few hundred meters, up to about 300–350 m (why surveys went to 350 m); most successful moves are tens to ~200 m; survival drops steeply with distance; beyond 350 m effectively negligible.
- **Turned into work:** Task 4 — the histogram already spans exactly 0–350 m, so it is the full support of the migration distance distribution; patches farther than ~350 m apart do not exchange juveniles (connectivity cutoff in Task 5/6 narrative).

## E7 — Constraint: burn scheduling
- **Q:** On Avon Park, do nearby patches tend to get burned together in the same year, or on a rotating schedule?
- **Reply (gist):** rotating schedule, multi-year rotation, deliberate mosaic so the landscape keeps a mix of age classes; all-at-once would synchronize closure; also forced by crews, weather windows, smoke rules.
- **Turned into work:** Task 6 rotation: 29 patches burned on an 8-yr cycle, ≤ 4 patches/year (smoke/crew cap), staggered largest patches first; mosaic keeps some recently-burned (high-density) and some maturing patches simultaneously.

## E8 — Calibration: burn effect timing
- **Q:** Does a patch that just got burned support more scrub lizards than one left unburned a long time?
- **Reply (gist):** yes, but advantage is not instant and not permanent: bare ground after burn, open sand/food develops over 1–2 years, population peaks in early post-burn years, fades if unburned again.
- **Turned into work:** Task 6 policy timing — burn the maturing patch, do not count on the burn year's population; peak benefit ~ years 2–4; the 8-yr rotation (E5/E7) keeps the window inside [5, 15].

## E9 — Edge case: first failure mode
- **Q:** What is the usual first cause of failure for a managed Florida scrub lizard population?
- **Reply (gist):** fire suppression / too-long burn intervals — canopy closes, recruitment collapses, population ages; compounded by small size and isolation, so no rescue by immigration → local extinction.
- **Turned into work:** Task 5/6 — the binding failure sequence is (1) habitat closes, (2) R = Fa·Sj falls below 1, (3) no immigration rescue for small isolated patches. Task 6 burn interval ≤ 15 yr is the preventive control; the Task 5 "viable" flag anticipates exactly this.

## E10 — Institutional constraint: decision sequence
- **Q:** On this air force range, does the lizard program usually decide burns first, or the other way around?
- **Reply (gist):** burns are decided first by fire/range management (fuel loads, training, weather, crews, smoke rules); the lizard program is a constraint, not the driver — its lever is timing and patch selection (avoid wrong season, avoid burning the last occupied patches).
- **Turned into work:** Task 6 recommendation is phrased as constraints on the existing rotation, not a new burn program: (a) keep 8-yr interval (within 5–15), (b) never burn the occupied/viable patch (12) in the same year as its nearest neighbors, (c) sequence burns to leave a mosaic.

## How the reply values are used (parameter table)
| name | value | interval | source |
|---|---|---|---|
| min viable sandy area | 12 ha | [8, 20] ha | exchange 3 (20–50 ac) |
| burn interval window | 8 yr target | [5, 15] yr | exchanges 5, 7 |
| open-sand degradation tau | 10 yr | [8, 15] yr | exchange 5 (badly closed by 10–15) |
| migration effective range | 350 m | [300, 350] m | exchange 6 |
| post-burn density peak | years 2–4 | [1, 5] yr | exchange 8 |
| burn cap per year | 4 patches | — | exchanges 1, 7 (crews/smoke) |
| first failure driver | fire suppression | — | exchange 9 |
| decision authority | fire mgmt sets burns | — | exchange 10 |
