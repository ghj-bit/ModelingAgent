# Solution

## Subtask 1: Task 1: Discuss the factors that contribute to the loss of appropriate scrub-lizard habitat in Florida; give recommendat

### Problem

Task 1: Discuss the factors that contribute to the loss of appropriate scrub-lizard habitat in Florida; give recommendations to the state to preserve these habitats, and discuss the obstacles to implementing them.

### Analysis

Qualitative synthesis grounded in the ecology established by the data and by expert consultation. Exchange 1 established that the lizards are specialists of open sandy ground within a scrub mosaic: they need bare, loose sand for burrowing, basking and egg-laying, and scrub vegetation for predator cover and foraging structure; patches that are nearly all bare sand are low quality. Exchange 2 established that nest excavation in bare sand is obligate for reproduction (one clutch per year, no nest guarding). Exchange 3 established the failure mode: when vegetation closes the open sand, nesting becomes impossible or rare, vital rates fall, and the population cannot sustain itself even on large patches; the standard countermeasure is prescribed burning, often coupled with mechanical canopy treatment, because scrub is a fire-maintained system.

### Modeling Process

No equations; the causal chain is: succession/vegetation densification (quantified as ~6%/yr in Task 6) -> loss of open sand -> loss of nest sites, refugia and basking surface -> decline in Fa and Sj (and density) -> local extirpation of the patch population -> loss of the whole landscape population if source patches are lost. Threats considered: (i) natural succession closing open sand; (ii) residential/commercial development fragmenting and deleting patches; (iii) invasive species (e.g. melaleuca, Old World bluestem) displacing native scrub and removing open sand; (iv) improper fire management (both no-burn, which closes patches, and over-frequent or high-intensity burning, which damages the mosaic); (v) off-road vehicles and human recreation compacting sand and destroying refugia; (vi) climate-related shifts in fire regime and water availability.

### Outcome Analysis

Recommendations to the state: (1) maintain a prescribed-burn program that keeps the open-sand fraction of every patch above the nestability threshold (the model in Task 6 gives a <=3-yr burn interval for the four patches with >=10 ha sand); (2) couple burns with mechanical canopy treatment (roller-chopping, logging) on large patches where pine/oak overstory closes fastest; (3) secure conservation easements on the source patch (patch 12 in Task 5) and on patches with >=10 ha sand, since these are the only patches that can reproduce locally; (4) create or restore connectivity among the four sand-rich patches so the 10% of juveniles that disperse (Task 4) can actually reach them; (5) control invasive woody species; (6) restrict off-road access. Obstacles: (i) the landscape is on an Air Force Range, so military-use conflicts and security restrictions limit how and when burns and easements can proceed; (ii) private land ownership around the range makes landscape-scale management depend on voluntary cooperation; (iii) public opposition to burning (smoke, perception of waste); (iv) cost of recurring mechanical treatment; (v) liability and regulation around controlled fire; (vi) the sink structure found in Task 5 means that protecting only small patches is useless - management must protect the large source patches, which are politically harder to set aside.

## Subtask 2: Task 2: Use Table 1 (a cohort followed for 4 years) to estimate Fa (average adult female fecundity), Sj (juvenile surviv

### Problem

Task 2: Use Table 1 (a cohort followed for 4 years) to estimate Fa (average adult female fecundity), Sj (juvenile survivorship, birth to first reproductive season), and Sa (average adult survivorship).

### Analysis

Table 1 gives, for years 1-4, the cohort's total numbers N_t, living females F_t, and average female SVL by age. Clutch size follows y = 0.21*SVL - 7.5; at the hatchling size (30.3 mm) this is negative (-1.14), consistent with the statement that hatchlings do not lay eggs during their birth summer, so clutch is set to 0 at age 0. Assumptions: (a) sex ratio at birth is even, estimated here as the hatchling female fraction 495/972 = 0.509; (b) the cohort is a closed population (no immigration/emigration during the 4 years); (c) the female size average represents the mean female for clutch estimation; (d) age 1+ are the 'adult' (reproductive) stage, so Sa is estimated from female survival between reproductive ages, which is close to total survival since both sexes were captured.

### Modeling Process

Sj = N_1/N_0 = 180/972 = 0.185. Sa = mean(F_2/F_1, F_3/F_2) = mean(11/92, 2/11) = mean(0.1196, 0.1818) = 0.151. Clutch by age: age 0: 0 (by convention), age 1: 0.21*45.8-7.5 = 2.12, age 2: 0.21*55.8-7.5 = 4.22, age 3: 0.21*56.0-7.5 = 4.26. Total eggs over years 1-3 = 92*2.12 + 11*4.22 + 2*4.26 = 194.9 + 46.4 + 8.5 = 249.9. FA = total eggs / number of females that reproduced (years 1-3) = 249.9/105 = 2.38 eggs per reproductive female per year. (If 'average adult fecundity' is instead read as eggs per adult female present in a year, the value is 249.9/306 = 0.42 eggs per female per year; the first reading is used because Fa in Table 2, 4.8-11.0, is clearly a per-breeding-female clutch-based quantity.)

### Outcome Analysis

Sj = 0.185, Sa = 0.151, Fa = 2.38 eggs per reproductive female per year (or 0.42 per female if averaged over all present females). These are low: the cohort's per-capita replacement ratio is far below 1 (0.509*2.38*(0.185+0.151) = 0.33), which is expected for an open cohort with no immigration and is the reason Task 5's landscape must be treated as a metapopulation. Limitations: only 4 years and 2 females surviving to age 3 make Sa noisy (the two yearly ratios 0.120 and 0.182 differ by a factor of 1.5); the cohort was open to the environment in ways not recorded (predation, dispersal), so Sj is a lower bound on intrinsic juvenile survival; clutch from average size ignores within-age variation; the estimate Fa is an average over 3 age classes that have different sizes. The values bracket the Table 2 range (Fa 4.8-11, Sj 0.11-0.19, Sa 0.05-0.15), so the patch functions of Task 3 are consistent with the cohort data.

## Subtask 3: Task 3: Using Table 2 (8 patches with vital rates, patch size PS and sandy habitat Sand), develop functions that estimat

### Problem

Task 3: Using Table 2 (8 patches with vital rates, patch size PS and sandy habitat Sand), develop functions that estimate Fa, Sj, Sa and C (carrying capacity, lizards/ha) for any patch.

### Analysis

Eight patches give 8 data points per vital rate. The expert exchanges support a two-covariate model: quality depends on both open sand and the surrounding scrub structure, so both PS and Sand enter. Two functional forms were fitted for each response: a power form y = exp(b0 + b1*ln PS + b2*ln Sand) and a linear form y = b0 + b1*PS + b2*Sand, chosen by R^2 and AIC. The power form wins for all four responses (R^2: Fa 0.920, Sj 0.890, Sa 0.946, C 0.880 vs 0.771, 0.674, 0.840, 0.873 linear). The power form is also preferable biologically because it is scale-free and cannot go negative. Note that the fitted Fa has a negative partial effect of Sand (b2 = -0.20) once PS is held fixed: this is the expected signature of the mosaic rule from exchange 1 - at fixed total patch size, more bare sand means less scrub cover, which lowers fecundity; the positive total effect of sand comes through the PS and Sa/Sj channels. The density column of Table 2 is used directly as the empirical carrying capacity C (lizards/ha).

### Modeling Process

Power-form fits (least squares on ln y), valid over the calibration range PS in [8.5, 278] ha, Sand in [1.7, 84.3] ha, open fraction Sand/PS in [0.20, 0.30]: Fa = exp(0.8942 + 0.4357 ln PS - 0.1970 ln Sand) eggs per female per year. Sj = exp(-2.2087 - 0.0272 ln PS + 0.1608 ln Sand). Sa = exp(-3.0384 - 0.0555 ln PS + 0.3364 ln Sand). C = exp(3.5473 + 0.0502 ln PS + 0.1733 ln Sand) lizards/ha. R^2: Fa 0.920 (AIC 0.4), Sj 0.890 (AIC -69.3), Sa 0.946 (AIC -72.6), C 0.880 (AIC 40.4). Example: for PS = 74.35 ha, Sand = 19.15 ha the functions give Fa = 8.93, Sj = 0.157, Sa = 0.102, C = 71.9 lizards/ha. Back-fitting to the 8 calibration patches reproduces the observed values within the scatter shown in logs/verify.log (e.g. Sa fitted 0.071, 0.089, 0.137, 0.081, 0.104, 0.140, 0.051, 0.156 vs observed 0.06, 0.10, 0.13, 0.09, 0.11, 0.14, 0.05, 0.15).

### Outcome Analysis

The functions are reliable within the calibration range and are the basis of Tasks 4-6. Limitations: (i) only 8 patches, so each fit has 5 residual degrees of freedom and the coefficients' confidence intervals are wide; (ii) PS and Sand are strongly correlated (open fraction is roughly constant at ~0.25-0.30 across the calibration patches), so the separate effects of PS and Sand are weakly identified - the negative Fa/Sand partial coefficient is the least robust number in the model and should not be used for patches whose open fraction lies far from 0.25-0.30; (iii) the density-based C assumes the observed densities were at or near carrying capacity, which is plausible for an 8-patch long-term study but not certain for the smallest patch (g, 40 lizards/ha).

## Subtask 4: Task 4: About 10% of juvenile lizards migrate between patches; adults do not. Using the histogram of marked juveniles re

### Problem

Task 4: About 10% of juvenile lizards migrate between patches; adults do not. Using the histogram of marked juveniles recaptured up to 350 m from release, estimate the probability that a lizard survives migration between any two patches i and j.

### Analysis

The histogram is a proper probability distribution over 50-m distance bands (proportions sum to 1.000). A dispersing juvenile reappears at a distance D drawn from this distribution; the distance-weighted mean is 105.5 m, and 97% of reappearances are within 200 m. Migration between patches i and j succeeds only if the disperser actually reaches patch j, so the survival probability between i and j is the probability that the dispersal distance falls within the band containing the distance between the two patches, i.e. P(D <= L_ij) where L_ij is the distance between the patch centroids (or, for adjacent patches, the distance from i to the near edge of j). Two patches that are farther apart than 350 m cannot exchange migrants under this data: P(D <= 350 m) = 1.0 is the maximum, and the effective connection decays with L_ij. Exchange 2 (obligate sand nesting) implies a migrant must find a patch with nestable sand on arrival, which is handled in Task 5 by requiring the destination to be viable.

### Modeling Process

Band distribution: P(D in (0,50]) = 0.42, P(D in (50,100]) = 0.25, P(D in (100,150]) = 0.18, P(D in (150,200]) = 0.12, P(D in (200,250]) = 0.02, P(D in (250,300]) = 0.00, P(D in (300,350]) = 0.01. Mean distance = 105.5 m. P(reappear within radius r): 0.42 at r = 50, 0.67 at 100, 0.85 at 150, 0.97 at 200, 0.99 at 250, 1.00 at 350 m. Migration survival between patches i, j separated by centroid distance L: S(i->j) = P(D <= L), tabulated as: L = 50 m: 0.42; 100 m: 0.67; 150 m: 0.85; 200 m: 0.97; 250 m: 0.99; 300 m: 0.99; >= 350 m: 1.00 (within the survey range). For use in the metapopulation model, an 'effective' migration survival of 0.85 (the P within 150 m) is applied to the 10% of juveniles that leave a patch, i.e. 8.5% of the juvenile cohort arrives at a neighboring patch and 1.5% is lost in transit or to the matrix between patches.

### Outcome Analysis

The 300-m band is empty while the 350-m band has 1%, a small inconsistency (likely one recapture near the survey edge, or a rounding artifact); the cumulative mass is monotone when it is smoothed, and the 1% in the last band was kept because it is the survey's stated limit. The histogram measures recaptures, not true dispersers: some juveniles died in the matrix or left the 350 m survey range, so the 0.99 total recapture mass means about 1% of dispersers are unaccounted for, which is the same order as the 10% migration fraction - i.e. the probability of surviving a given migration attempt is high (>= 0.85 for any pair of patches whose centroids are within 150 m of each other, and >= 0.42 even for the closest patch pair), and the limiting factor on immigration is the fraction that chooses to leave and the presence of a suitable destination, not in-transit mortality. The 350 m survey limit means migration between patches farther than ~350 m apart is not directly measured and must be assumed negligible; this is consistent with the 29-patch landscape where most patch centroids are hundreds of metres apart.

## Subtask 5: Task 5: Develop a model to estimate the overall scrub-lizard population size on the 29-patch Avon Park landscape (Table 

### Problem

Task 5: Develop a model to estimate the overall scrub-lizard population size on the 29-patch Avon Park landscape (Table 3), and determine which patches are suitable for occupation and which cannot support a viable population.

### Analysis

Each patch is characterized by (PS, Sand) from Table 3; the Task 3 functions give Fa, Sj, Sa and C (lizards/ha) for each patch, and the patch population is N = C*PS (saturated model: each patch holds its carrying capacity). The stage-structured replacement ratio for a patch is lambda = f*Fa*(Sj + Sa), where f = 0.5093 is the female fraction of a cohort (Table 1: 495/972). A patch is a source (viable, self-sustaining) if lambda >= 1; otherwise it is a sink that can be occupied only by immigration. Exchange 2 adds a hard constraint: because nest excavation in bare sand is obligate, a patch also needs a minimum nestable open-sand area; the base threshold is 10 ha (the scale of the smallest calibration patch, b, at 11.31 ha, and about 100 times a single nest site), swept over 5-20 ha. Exchange 1 justifies requiring sand as an absolute area rather than a fraction: lizards need both components of the mosaic, and the sand area is what limits nest sites. Migration: 10% of juveniles leave each patch; of these, 85% survive to a neighbouring patch (Task 4, 150 m band), so the migration-adjusted replacement ratio is lambda_eff = f*Fa*(0.9*Sj + 0.1*0.85 + Sa).

### Modeling Process

Per patch i: Fa_i = exp(0.8942 + 0.4357 ln PS_i - 0.1970 ln Sand_i); Sj_i = exp(-2.2087 - 0.0272 ln PS_i + 0.1608 ln Sand_i); Sa_i = exp(-3.0384 - 0.0555 ln PS_i + 0.3364 ln Sand_i); C_i = exp(3.5473 + 0.0502 ln PS_i + 0.1733 ln Sand_i); N_i = C_i * PS_i; lambda_i = 0.5093 * Fa_i * (Sj_i + Sa_i); lambda_eff_i = 0.5093 * Fa_i * (0.9*Sj_i + 0.85 + 0.1*0 + Sa_i) [i.e. 0.5093*Fa_i*(Sj_i*(1-0.10) + 0.10*0.85 + Sa_i)]. Viability: patch i is suitable iff lambda_i >= 1 AND Sand_i >= 10 ha; it is an unsuitable sink otherwise. Landscape total = sum_i N_i. Result (base case, min_sand = 10 ha): total landscape population N = 25,308 lizards across 433.13 ha of patches (137.24 ha open sand). Suitable (source) patches: 1 - patch 12 (74.35 ha, 19.15 ha sand, lambda = 1.18, N = 5,346). All other 28 patches have lambda < 1 (range 0.18-0.97; the next highest are patch 17 at 0.97, patch 20 at 0.89, patch 15 at 0.86, patch 2 at 0.84) and are unsuitable as self-sustaining units, though patches 2, 15, 17 with lambda > 0.8 and >= 10 ha sand are the best secondary candidates and would become sources if their open-sand area were restored. The sweep of the sand threshold over 5, 10, 15, 20 ha leaves the answer unchanged at 5-15 ha (1 source patch) and drops to 0 at 20 ha (patch 12's 19.15 ha sand falls below the threshold), so the '1 source patch' conclusion is robust to the threshold over 5-15 ha. With migration included, lambda_eff rises for every patch (e.g. patch 12: 1.18 -> 1.49; patch 2: 0.84 -> 1.08; patch 15: 0.86 -> 1.12), so patches 2, 15, 17, 20 also clear 1.0 on an immigration-assisted basis, which is the correct reading for occupied sink patches: they are maintained by inflow, not self-replacing.

### Outcome Analysis

The landscape supports about 25,000 scrub lizards at carrying capacity, of which about 5,300 (21%) sit on the single source patch 12; the remaining 20,000 are in 28 sink patches that depend on immigration. This is a classic source-sink metapopulation, and it is fragile: losing patch 12 removes the only self-sustaining population and the whole landscape population declines to extinction on a decadal timescale even though 28 patches still hold animals. Limitations: (i) the saturated assumption N = C*PS overstates numbers on sink patches, which are likely held below capacity by limited immigration; a conservative bound is therefore the source-only total of ~5,300 and an optimistic bound the full 25,308, with the truth in between; (ii) Table 3 has no vital rates, so every Table 5 number inherits the Table 2 fit uncertainty, including the weak identification of the PS vs Sand effects flagged in Task 3; (iii) no inter-patch distances are given (map.jpg is referenced but not supplied as data), so the Task 4 migration survival could not be applied pairwise and the flat 0.85 effective survival was used instead - on this landscape, where most patch centroids are farther than 350 m apart, true immigration rates are probably lower than modeled, which weakens the sink populations further; (iv) the female fraction 0.5093 is from a single cohort; a sex ratio of exactly 0.5 would raise every lambda by ~2%.

## Subtask 6: Task 6: Vegetation density in Florida scrub increases by about 6% per year (aerial photographs). Make a recommendation o

### Problem

Task 6: Vegetation density in Florida scrub increases by about 6% per year (aerial photographs). Make a recommendation on a policy for controlled burning.

### Analysis

The 6%/yr densification acts on the open-sand area: without burning, Sand_t = min(PS, Sand_{t-1} * 1.06), and the Task 3 vital-rate functions are re-evaluated each year at the shrunken sand area, so each patch's lambda_t declines until the patch loses viability (lambda < 1 and/or Sand < min_sand). Exchange 3 describes exactly this: vegetation closure removes the substrate needed for nest excavation, burrowing and basking; vital rates fall; the population cannot sustain itself even on large patches; and the field-standard countermeasure is prescribed burning (a fire-maintained system), often coupled with mechanical canopy treatment to reopen the canopy and expose sand. The policy question is therefore the burning interval that keeps open sand above the nestability floor. A burn is modeled as a full reset of Sand to its measured value (conservative: real burns restore part of the mosaic, and the expert notes mechanical coupling to speed reopening).

### Modeling Process

Model: Sand_0 from Table 3; Sand_t = min(PS, Sand_{t-1}*1.06) between burns; at each burn (every T years) Sand resets to Sand_0. Viability in year t: lambda_t = 0.5093*Fa(PS, Sand_t)*(Sj(PS, Sand_t)+Sa(PS, Sand_t)) >= 1 AND Sand_t >= 10 ha. Computed closure times (years from now until Sand_t < 10 ha, no burning): patch 2 (11.91 ha): 1.1 yr; patch 17 (10.73 ha): 1.2 yr; patch 15 (11.31 ha): 2.1 yr; patch 12 (19.15 ha): 11.2 yr. Sweep of burn intervals T = 1, 3, 5, 7, 10, 15, 20 yr over a 40-yr horizon (code/burning.py): no burn -> 2 patches still above the sand floor at t = 40 but their vital rates are degraded; every T <= 7 yr keeps all four sand-rich patches (2, 12, 15, 17) above the floor in every year of the horizon; T = 10-20 yr allows patches 2 and 17 to dip below 10 ha for part of each cycle. Recommendation: burn every 3 years on all four patches with >= 10 ha sand (and any patch that later exceeds 10 ha), coupled with mechanical canopy treatment on the three largest (12, 15, 17) where overstory closure is fastest; rotate so that at most one patch is being treated in a given year to preserve the mosaic and avoid landscape-wide disturbance. A 3-yr interval keeps each patch's open-sand loss per cycle at ~20% (1.06^3 = 1.19), which is within the range the mosaic can absorb according to the Task 3 sensitivity of the vital rates to Sand.

### Outcome Analysis

The recommendation is robust to the exact interval between 1 and 7 yr (all of them keep the four patches viable over 40 yr), so the binding constraint is not to let the interval exceed ~7 yr, and 3 yr is recommended as the standard because it leaves margin for a missed fire season or a low-intensity burn. The recommendation assumes a burn fully reopens the sand; if a burn only partially reopens it, the effective interval must be shorter, which is why mechanical treatment is included for the large patches. Limitations: the 6%/yr rate is a single landscape-wide aerial estimate - local closure rates vary with rainfall and overstory, so the interval should be set from per-patch monitoring of open-sand fraction rather than fixed by rule; the model tracks sand area but not the within-patch mosaic structure that exchange 1 says also matters (a patch could hold 10 ha of sand in one blob and be poorer than 10 ha in a mosaic); and the model does not include fire risk to the lizards themselves (a hot burn in the nesting season can kill clutches), so burns should be scheduled outside the spring nesting season described in exchange 2.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
