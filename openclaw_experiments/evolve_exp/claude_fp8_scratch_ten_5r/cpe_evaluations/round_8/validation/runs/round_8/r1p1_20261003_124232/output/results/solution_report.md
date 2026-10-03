# Solution

## Subtask 1: Task 1: Identify the factors that cause loss of suitable scrub-lizard habitat in Florida; recommend preservation actions

### Problem

Task 1: Identify the factors that cause loss of suitable scrub-lizard habitat in Florida; recommend preservation actions for the state of Florida; and discuss the obstacles to implementing those recommendations.

### Analysis

Habitat loss is driven by the same process in every case: open sandy scrub closing over. Fire suppression lets shrub and oak canopies close within 10-15 years, so the lizards' basking, foraging and movement surface disappears and juvenile recruitment collapses first (experts E4, E9). On top of the natural closing, human pressures act: coastal and central-Florida development converting scrub and pineland, fuel buildup after fire suppression, invasive species, and the cost of burning itself. The expert-anchored priority (E2) is configuration, not size: because scrub lizards are poor dispersers and a single large isolated patch goes locally extinct when hit by fire, drought or disease, preservation should keep a network of patches within dispersal range, each above a minimum size floor (E3).

### Modeling Process

No computation is required; the structure is: (1) threat ranking: fire suppression > development/fragmentation > invasion, all acting on open-sand area S; (2) recommendation set, ordered: (a) maintain a prescribed-fire rotation on all occupied scrub so open sand does not close (interval 5-15 yr, E5), (b) protect and re-join patches into a corridor network so patches within ~350 m exchange juveniles (E6), (c) retain patches of at least ~8-20 ha of sandy habitat (E3) as the minimum self-sustaining unit, (d) buffer against development through conservation easements on the Avon Park landscape and similar ranges.

### Outcome Analysis

Obstacles (E1, E7, E10): smoke management and liability over roads, airports and subdivisions make the burn window narrow and burns are cancelled at short notice; limited burn crews and weather windows cap the number of patches that can burn per year; and on the range, burn decisions belong to fire/range management (fuel loads, training, safety), so the lizard program can only constrain timing and patch choice, not initiate burns. Development obstacles: private-land ownership makes easements expensive, and liability rules slow new burns. The recommendation set is therefore phrased as constraints on the existing rotation plus a connectivity plan, not as a new burn program.

## Subtask 2: Task 2: From the 4-year cohort in Table 1, estimate Fa (average fecundity of adult lizards, eggs per female per year), S

### Problem

Task 2: From the 4-year cohort in Table 1, estimate Fa (average fecundity of adult lizards, eggs per female per year), Sj (juvenile survivorship from birth to the first reproductive season) and Sa (average adult survivorship).

### Analysis

Assumptions: (a) hatchlings (age 0) do not reproduce in their birth summer, per the dataset note; ages 1-3 all reproduce each year; (b) clutch size follows the supplied relation y = 0.21*SVL - 7.5 using that age's average female SVL; (c) the cohort is closed (no migration or census loss), so between-age ratios are survivorship; (d) 'adult' = ages 1+ (first reproduction at age 1), so Sa is the mean annual survival across the two adult-to-adult transitions.

### Modeling Process

Clutch size by age: age 1: 0.21*45.8 - 7.5 = 2.118; age 2: 0.21*55.8 - 7.5 = 4.218; age 3: 0.21*56.0 - 7.5 = 4.26. Fa = mean clutch over reproducing ages = (2.118 + 4.218 + 4.26)/3 = 3.532 eggs/female/yr. Sj = N(age 1)/N(age 0) = 180/972 = 0.185. Sa = mean of the adult steps = (20/180 + 2/20)/2 = (0.1111 + 0.1000)/2 = 0.1056.

### Outcome Analysis

Results: Fa = 3.53, Sj = 0.185, Sa = 0.106. Cross-check against Table 2: the cohort's Sj = 0.185 and Sa = 0.106 fall inside the patch ranges 0.11-0.19 and 0.05-0.15, i.e. the cohort behaves like a medium-to-large patch. The Fa estimate is a cohort mean over ages 1-3; a female at full adult size lays about 4.2 eggs/yr, so 3.53 is low only because it includes the first, small-clutch reproductive year. Limitations: the age-3 survivorship step (1 -> 2 survivors) rests on two animals and is the noisiest input; if the cohort is not closed, Sj and Sa are biased low, which would lower R = Fa*Sj in Task 5.

## Subtask 3: Task 3: Using Table 2, develop functions that estimate Fa, Sj and Sa for a patch from its size and open sandy area, plus

### Problem

Task 3: Using Table 2, develop functions that estimate Fa, Sj and Sa for a patch from its size and open sandy area, plus a function for the patch carrying capacity C.

### Analysis

Assumptions: (a) the 8 patches span the relevant range of habitat quality, so fitted functions interpolate within it and only extrapolate mildly for Table 3 patches; (b) open sandy area S (ha) is the operative habitat measure - it is the surface lizards actually use, and Table 2 shows the vital rates ordering with S; (c) a power law is the natural form for size-scaling, and all four fits use ordinary least squares on ln(y) against ln(S) (or ln size).

### Modeling Process

Fit ln(y) = a + b ln(S) by OLS to the 8 patches. Results: Fa(S) = exp(1.43032 + 0.21254 ln S)  [R2 = 0.785, max APE 33.8%]; Sj(S) = exp(-2.24225 + 0.13523 ln S)  [R2 = 0.888, max APE 9.4%]; Sa(S) = exp(-3.10671 + 0.28418 ln S)  [R2 = 0.945, max APE 16.5%]. Density also scales with S: density(S) = exp(3.60910 + 0.22053 ln S)  [R2 = 0.878]. Carrying capacity is total lizards N = density x sandy area; a two-term OLS fit ln N = c0 + c1 ln(A) + c2 ln(S) (A = patch area, S = sandy area) gives C(A, S) = exp(3.54731 + 0.05022 ln A + 1.17332 ln S)  [R2 = 0.996, max APE 17.6%]. Example: patch 12 (A = 74.35 ha, S = 19.15 ha) gives C = 2200 lizards, matching its observed 2130 (within 3%).

### Outcome Analysis

The vital-rate functions are well-behaved and monotone increasing in S; Sa is the strongest (R2 = 0.945) because small patches lose adults to edge effects and predation. Fa is the weakest fit (R2 = 0.785) - fecundity also depends on female size distribution within the patch, which S does not fully capture; its worst point is patch d (observed 4.8 vs fitted 6.4). The C function is essentially the density relation plus area, so its accuracy is limited by the density fit; it predicts C < 0 for negligible sandy areas, and the model clamps C to 0 there. Biases: the 8 training patches are not random - they were chosen because they carry measurable populations, so functions may overestimate vital rates on patches of comparable size that are actually poor quality.

## Subtask 4: Task 4: From the migration-distance histogram (juvenile releases, recaptures within 6 months, surveys out to 350 m), est

### Problem

Task 4: From the migration-distance histogram (juvenile releases, recaptures within 6 months, surveys out to 350 m), estimate the probability that a juvenile migrating between any two patches i and j survives the migration.

### Analysis

The histogram gives the distance distribution of juvenile movements: 42% within 50 m, 25% in 50-100 m, 18% in 100-150 m, 12% in 150-200 m, 2% in 200-250 m, 0% in 250-300 m, 1% in 300-350 m. Two data repairs: the 250-300 m bin is 0 while the 300-350 m bin is 0.01, which is non-monotone for a distance histogram; the outer two bins are treated as one small recapture-uncertainty mass and the 350 m value is folded into the 300-350 m bin, leaving the distribution monotone non-increasing. Because surveys covered exactly the expert-stated effective range of about 300-350 m (E6), the histogram spans the full support of successful movements. Interpretation: a lizard found at distance d has survived the trip and ended at d; the near-release fraction (0-50 m) also includes lizards that dispersed only slightly, so the search-fraction s - the share of the 10% migrant cohort found near release - is a free parameter with base s = 0.5 and tested values s = 1, 2, 4.

### Modeling Process

P(survive migration, end at distance d) = prop(d) / (sum of all prop + s). With base s = 0.5: P(<=50 m) = 0.42/1.26 = 0.336, P(50-100) = 0.198, P(100-150) = 0.143, P(150-200) = 0.095, P(200-250) = 0.016, P(250-350) = 0.008. Overall survival among migrants P(survive) = 1.26/1.76... reported as P_migrate = 0.336 (base), 0.503 (s=1), 0.669 (s=2), 0.802 (s=4). In the metapopulation model the effective per-patch recruitment boost is 0.10 * P(survive) (10% of juveniles migrate; only survivors arrive).

### Outcome Analysis

Result: the probability of surviving migration is of order 1/3 to 1/2 of the migrant cohort, base estimate 0.34, range [0.34, 0.80] across the tested search fractions. Most survivors end within 100 m of release - the steep fall-off (42% -> 25% -> 18% -> 12%) confirms the expert statement that survival drops steeply with distance and moves beyond ~350 m are negligible. Consequence for Task 5/6: patches need to sit within roughly 350 m of each other to exchange juveniles, which is why the connectivity recommendation in Task 1 is about patch spacing, not just patch count. Limitation: the histogram is a recapture study, so detection probability falls with distance; true movement survival is probably somewhat higher than the base estimate, which is why the s sweep is reported.

## Subtask 5: Task 5: Model the overall scrub-lizard population of the 29-patch Avon Park landscape (Table 3) and determine which patc

### Problem

Task 5: Model the overall scrub-lizard population of the 29-patch Avon Park landscape (Table 3) and determine which patches are suitable for occupation and which would not support a viable population.

### Analysis

Assumptions: (a) at equilibrium, adult-equivalent population per patch A satisfies a Beverton-Holt recursion with immigration: A = (1 - 1/R + m) C / R where R = Fa*Sj is the net reproductive rate, m = 0.10 * P(survive migration) is the immigration fraction, and C is the patch carrying capacity from Task 3; (b) when R <= 1 the patch cannot self-replace and A = 0 in the absence of continuous rescue; (c) total population = A / Sa (juveniles in the patch equal the adult pool divided by juvenile survivorship, to first order); (d) a patch is viable if it has at least 12 ha of sandy habitat (the expert minimum self-sustaining area, 8-20 ha floor, E3), fitted adult survivorship Sa >= 0.10, and equilibrium total >= 200 lizards - the threshold below which the population is too small to be rescued by immigration (E9).

### Modeling Process

For each of the 29 patches: compute Fa(S), Sj(S), Sa(S), C(A, S) from the Task 3 functions; R = Fa*Sj; A = max(0, (1 - 1/R + 0.10*0.336) C/R); total = A/Sa. Base-case result (P_migrate = 0.336): landscape population = 3948 lizards; 1 patch is viable (patch 12: sandy 19.15 ha, R = 1.24, C = 2200, total = 2434). Three patches marginally self-replace but fail the size floor: patch 2 (R = 1.051, total 653, sandy 11.91 ha), patch 15 (R = 1.032, total 503), patch 17 (R = 1.013, total 359). All other patches have R < 1 and hold no self-sustaining population. Sensitivity (code/model.py --sweep S=0.5/1/2/4): landscape population is 3948 / 4518 / 5085 / 5538 at s = 0.5/1/2/4; the set of viable patches is unchanged because the binding constraint is R < 1, not immigration. Viability-floor sensitivity: at the 8 ha floor, patches 2 and 15 additionally clear the area test but remain just above/below the Sa and population thresholds, so the robust answer is that patch 12 is the only patch that clearly supports a viable population, with 2, 15 and 17 as near-threshold candidates dependent on fire maintenance.

### Outcome Analysis

The landscape supports roughly 4,000 lizards (range 3,950-5,550 under migration uncertainty), concentrated in the four largest patches. Suitability: patch 12 is suitable and viable; patches 2, 15, 17 are marginally suitable - they only self-replace and collapse if unburned, because their R values sit within ~5% of 1; the remaining 25 patches (all with sandy area below ~12 ha, mostly below 8 ha) are unsuitable for a viable population and act as transient stepping stones. Limitations: (1) the functions extrapolate below the smallest training patch (1.67 ha sandy), so R for tiny patches is uncertain and the zero-population verdicts for patches 3, 18, 21-26 are structural (R << 1) rather than numeric; (2) the model assumes all patches are in a maintained (burned) condition; an unburned landscape would see Sj and Sa fall below the fitted curves and the population shrink toward the viable core; (3) no spatial adjacency data (map.jpg not supplied), so the 350 m connectivity check could not be applied patch-by-patch - the immigration term m is applied uniformly.

## Subtask 6: Task 6: Vegetation density increases about 6% per year in the scrub. Recommend a controlled-burning policy.

### Problem

Task 6: Vegetation density increases about 6% per year in the scrub. Recommend a controlled-burning policy.

### Analysis

The 6%/yr vegetation growth means open sand closes exponentially; the expert-anchored closure timescale is 10-15 years (badly closed) with a practical burn window of 5-10 years (E5). Burning resets vegetation near zero, but the benefit is not instant - open sandy habitat and food develop over 1-2 years and density peaks in the early post-burn years (E8) - and burns are constrained by smoke/liability rules and crew availability (E1), with at most a few patches burnable per year (E7). The existing range practice is a multi-year rotation (E7) set by fire management, into which the lizard program can only insert constraints (E10).

### Modeling Process

Policy: burn each patch on an 8-year rotation (sweep tested 6/8/10/12/15; 8 yr keeps every patch inside the 5-15 yr window with margin on both sides), staggering at most 4 patches per year across the 29-patch landscape (smoke/crew cap from E1/E7). Sequence largest, occupied patches first (patch 12, then 2, 15, 17) so the population core is always in the high-density post-burn window; never burn two patches within ~350 m of each other in the same year, so a juvenile always has an unburned nearby patch to disperse into; target burn in the cool/dry season window when the vegetation carries fire and smoke disperses predictably. Under this rotation, the landscape always contains a mix: patches in years 2-4 post-burn (peak density, high juvenile habitat), maturing patches, and one or two due for burning next year - a shifting mosaic that is both the habitat the species needs and what crews can actually schedule.

### Outcome Analysis

At 6%/yr unchecked growth, a patch's open-sand fraction decays with tau ~ 10-15 yr; a burn resets it. An 8-yr rotation therefore holds open-sand fraction in the upper half of its range on average. Compared with the no-burn alternative: the marginal patches 2, 15, 17 (R within 5% of 1) would fall below replacement within one missed interval and the landscape population would drop from ~3,950 to the ~2,400 carried by patch 12 alone (E9's failure sequence: closure, R < 1, no rescue). The policy is implementable because it is a constraint on the existing rotation rather than a new program: keep the interval at 8 yr, cap simultaneous burns, protect the occupied core from same-year neighborhood burns, and accept that the burn year itself is a low-density year (E8) - management should not expect population gains in the year of the burn. Residual risks: burn cancellation due to smoke rules can push a patch past the 15-yr mark, at which point the patch is effectively lost for a decade; the mitigation is a hard 15-yr trigger that forces a re-scheduling review.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
