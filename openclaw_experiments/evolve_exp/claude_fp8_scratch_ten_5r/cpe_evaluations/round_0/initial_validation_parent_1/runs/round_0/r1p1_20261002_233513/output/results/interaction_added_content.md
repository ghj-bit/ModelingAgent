# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — 2002_C Florida Scrub Lizard

Ten exchanges, one question each. For each: the question, a summary of the reply, and exactly how the reply entered the work (parameter, equation, decision rule, or constraint).

## Exchange 1
- **Q:** In your experience, what are the main reasons Florida scrub habitat has been lost over the past decades?
- **Reply (summary):** Loss drivers in order: urban/residential development (largest historical), agricultural conversion, fire suppression (canopy closure), fragmentation, sand mining. Fire suppression and fragmentation are the ongoing drivers.
- **How it was used:** Task 1 deliverable. The factor list and recommendations (acquire/protect, manage fire, connect patches) and obstacles are structured around these five drivers. No numeric value.

## Exchange 2
- **Q:** When Florida tried to protect scrub, what obstacles slowed the down?
- **Reply (summary):** Private ownership, cost/funding limits, landowner resistance and litigation, small scattered parcels, fire management difficulty near development, competing priorities/weak enforcement.
- **How it was used:** Task 1 obstacles section. These are the implementation obstacles listed against each recommendation. No numeric value.

## Exchange 3
- **Q:** Do juvenile scrub lizards ever move more than 350 m between habitat patches?
- **Reply (summary):** Yes — 350 m is only the survey limit, a sampling artifact. Dispersal of 0.5–1 km+ is plausible; data cannot quantify it.
- **How it was used:** Task 4 constraint. Migration survival is estimated from the histogram over the 0–350 m range it actually covers, and this exchange is cited as the reason the histogram tail (which is censored at 350 m) is treated as a lower bound: a fraction of migrants move beyond the surveyed range and are not in the data. No numeric value entered the model.

## Exchange 4
- **Q:** Does a moving juvenile survive an open-scrub migration about as long as it does staying put?
- **Reply (summary):** No — migration is substantially riskier (predation, desiccation, no shelter in the matrix). Dispersal mortality commonly removes half or more of migrants; model it as a distinct, lower per-migration factor.
- **How it was used:** Task 4/5 decision rule. Juvenile migration survival P is a separate multiplier applied to migrants, and is constrained to be materially below the resident juvenile rate (Sj ≈ 0.185). This is the justification for the value P = 0.5 (≈ half of migrants, the expert's central judgment) as the base case, with a sensitivity range below Sj.

## Exchange 5
- **Q:** In scrub patches, what limits how many lizards can live — total area or open sandy ground?
- **Reply (summary):** Open sandy ground, not total area. Density is best per hectare of sandy habitat. Carrying capacity is set by open sandy area.
- **How it was used:** Task 3 carrying-capacity function. Drives the choice to regress lizard density on **sandy habitat** (not patch size). Verified on Table 2: Density vs Sandy Habitat gives r ≈ 0.95, vs Patch Size r ≈ 0.85. The C(S) function is fitted to sandy area.

## Exchange 6
- **Q:** In practice, how small a scrub patch still holds a lizard group that can persist on its own?
- **Reply (summary):** No sharp threshold. Working rule: ~20–50 ha of open sandy ground for a viable standalone patch; below ~10 ha generally not viable alone; small patches persist only via immigration (metapopulation).
- **How it was used:** Task 5 viability decision rule. A patch is "suitable/viable" if its modelled resident population is self-sustaining (local net growth ≥ 0, i.e. λ ≥ 1) **and** its sandy habitat ≥ ~10 ha; patches below that are "unsuitable in isolation" and only occupied if connected to a larger source via immigration. The 10 ha floor is used as the isolation threshold.

## Exchange 7
- **Q:** What makes scrub managers choose how often to burn — a good-bad tradeoff or a minimum need?
- **Reply (summary):** Tradeoff. Too rare → vegetation closes, carrying capacity falls. Too frequent → direct mortality, egg loss, favors grasses. Interval is multi-year, commonly ~3–10 years, pushed longer by smoke/liability.
- **How it was used:** Task 6 policy. The burn interval is modeled as a tradeoff between the ~6%/yr vegetation regrowth (habitat loss) and direct burn mortality. The 3–10 yr range is the search band for the recommended interval; the model selects the interval that maximizes long-run average population / sandy habitat.

## Exchange 8
- **Q:** When scrub is burned, do managers burn each patch separately or the whole area at once?
- **Reply (summary):** Separately, staggered over years. Reasons: differing fuel load, mosaic maintenance, refugia/recolonization, permitting constraints.
- **How it was used:** Task 6 policy structure. The recommended policy is a **staggered (mosaic) burn schedule** — each patch on its own return interval, a rotating subset burned each year — not a synchronized landscape-wide burn. This is the decision rule for the policy recommendation.

## Exchange 9
- **Q:** When a scrub patch is burned, how does the amount of open sandy ground and the lizards change?
- **Reply (summary):** Burn sharply opens sandy ground (removes encroachment), which then declines ~6%/yr. Lizards: immediate crash (direct mortality, egg/food loss), then recovery while habitat is open, then slow decline as it closes.
- **How it was used:** Task 6 dynamic equations. Defines the post-burn state: sandy habitat resets to (near) patch-max after a burn; a burn-mortality term (fraction of residents killed) is applied to the population in the burn year; and the ~6%/yr regrowth is the decay term. These are the two new state transitions in the Task 6 model.

## Exchange 10
- **Q:** Which patches do managers choose to burn first when scrub vegetation is closing in?
- **Reply (summary):** Most-encroached first (longest past target interval, closest to losing sandy ground), subject to burnability and keeping refugia.
- **How it was used:** Task 6 prioritization rule. The staggered schedule is assigned in order of encroachment — patches furthest from a burn / lowest current sandy-habitat fraction get the earliest next burn — with a subset left as unburned refugia so the mosaic is maintained.
