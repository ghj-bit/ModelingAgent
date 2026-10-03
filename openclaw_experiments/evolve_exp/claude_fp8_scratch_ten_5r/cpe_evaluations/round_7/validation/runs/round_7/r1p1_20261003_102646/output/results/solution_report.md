# Solution

## Subtask 1: Task 1. Discuss the factors that cause appropriate scrub-lizard habitat to be lost in Florida, make recommendations to t

### Problem

Task 1. Discuss the factors that cause appropriate scrub-lizard habitat to be lost in Florida, make recommendations to the state to preserve the habitat, and discuss the obstacles to implementing those recommendations.

### Analysis

Habitat loss has two distinct mechanisms that must not be conflated. The first is outright conversion: Florida scrub grows on high, dry, sandy uplands, which is exactly the land most in demand for residential, commercial and agricultural development and for roads, mining and citrus. Conversion removes habitat entirely. The second is in-situ degradation: fire suppression. Scrub is a fire-dependent community; without fire, vegetation (oak, palmetto, saw-palmetto) densifies at roughly 6% per year, the open sandy microhabitat the lizards need is lost, and the patch closes up within about 15-20 years even though the land is still nominally 'scrub'. The two interact: development fragments the landscape, and fragmented, small, isolated patches are harder to burn and more prone to closing. The recommendations are therefore (a) stop conversion by protecting the largest intact patches and connecting them, and (b) manage degradation by maintaining a regular, properly-interval controlled-burn program. Obstacles are structural and political rather than technical.

### Modeling Process

This subtask is qualitative, but the degradation component is quantified by the vegetation-density growth. Let V(t) be the relative vegetation (non-sand) density; V grows at ~6%/yr, so the open-sandy fraction decays roughly as 1/(1+0.06 t), which reaches near-closure (little open sand) in about 15-20 years without fire. The conservation value of a patch to the lizard is therefore a function of its open-sandy area (see Task 3), which is why the two mechanisms are linked: conversion removes sand area directly, and suppression shrinks the usable sand area over time.

### Outcome Analysis

Recommendations to the state: (1) acquire or secure conservation easements on the largest, most intact scrub patches and on the corridors between them, prioritizing patches that exceed the minimum viable population (see Task 5) so the money buys self-sustaining source populations; (2) maintain a landscape-scale controlled-burn program on an 8-12 year interval, longer for no reason (see Task 6), with rotating patchy burns that leave unburned refugia; (3) coordinate with the county governments that hold land-use authority and with the Air Force Range that holds the Avon Park landscape. Main obstacles: most remaining scrub is privately owned, so the state must buy, regulate or compensate, and takings constraints limit regulation; acquisition is expensive and funding (e.g. the Florida Forever program) is chronically short of the acreage needed; much scrub is already in small, isolated, platted tracts where development pressure is highest; land-use decisions sit at the county level where growth interests usually outweigh conservation; and mining, agriculture and roads compete for the same sandy uplands. The model's main bias here is that it treats habitat as reducible to open-sandy area, whereas microhabitat quality and connectivity also matter.

## Subtask 2: Task 2. Using the cohort in Table 1, estimate Fa (average adult fecundity), Sj (juvenile survivorship, birth to first re

### Problem

Task 2. Using the cohort in Table 1, estimate Fa (average adult fecundity), Sj (juvenile survivorship, birth to first reproductive season) and Sa (average adult survivorship).

### Analysis

The cohort was followed for 4 years. Year 1 (age 0) = 972 hatchlings; year 2 (age 1) = 180; year 3 (age 2) = 20; year 4 (age 3) = 2. Hatchlings (age 0) do not lay eggs; clutch size for reproductive females is y = 0.21*SVL - 7.5 eggs, where SVL is snout-to-vent length in mm. Sj is the fraction of hatchlings surviving to the first reproductive season (age 0 -> age 1). Sa is the average probability an adult (age >= 1) survives a year. Fa is the average number of eggs a reproductive female produces per year, taken at the size of a first-year (age 1) reproductive female, which is the reproductive adult at the base of the cohort.

### Modeling Process

Sj = N(age1)/N(age0) = 180/972 = 0.185. Adult survivorship over the two adult transitions: N(age2)/N(age1) = 20/180 = 0.111 and N(age3)/N(age2) = 2/20 = 0.100; the cohort-weighted average Sa = (20 + 2)/180 = 0.122 (simple mean of the two ratios is 0.106). Fecundity: the age-1 females average SVL 45.8 mm, so Fa = 0.21*45.8 - 7.5 = 2.12 eggs/female/yr. (Larger age-2/3 females at 55.8-56 mm would give 4.22-4.26 eggs, but the first-reproductive-season adult is the relevant reproductive base; the value 2.12 is used as the central estimate, with 2-4.3 as the plausible range as females grow.)

### Outcome Analysis

Estimates: Fa = 2.12 eggs/female/yr, Sj = 0.185, Sa = 0.122. The per-capita product Fa*Sj ~ 0.39 means each female replaces well under one of herself, so persistence depends on the ~0.12 adult survivorship carrying the population and on the density dependence that lets numbers sit at carrying capacity. Limitations: only 4 years and a small tail of the cohort (2 animals at age 3), so Sa is estimated from just 20 -> 2 survivors and is statistically weak; a single year's birth cohort is used, so seasonal or environmental variation is not captured; and the clutch-size function was applied at the age-1 size, so Fa carries the uncertainty of the assumption about which age class is 'the adult'.

## Subtask 3: Task 3. Using Table 2 (8 patches), develop functions that estimate Fa, Sj and Sa for a patch from its size and open-sand

### Problem

Task 3. Using Table 2 (8 patches), develop functions that estimate Fa, Sj and Sa for a patch from its size and open-sandy area, and a function that estimates the carrying capacity C of a patch.

### Analysis

Eight patches give paired observations of vital rates against patch size P (ha) and open-sandy area S (ha). Ordinary-least-squares linear fits are used. Sandy area is the stronger predictor than total patch size for all three vital rates (higher R^2), which makes ecological sense: it is the open sand that supports the lizards, not the total patch area. Carrying capacity is estimated as C = (density) x (sandy area), where density is itself regressed on sandy area.

### Modeling Process

Least-squares fits (x = open-sandy area S, ha): Fa = 5.737 + 0.07094*S (R^2=0.77); Sj = 0.1338 + 0.000761*S (R^2=0.66); Sa = 0.0720 + 0.001080*S (R^2=0.81); density = 50.24 + 0.6927*S lizards/ha (R^2=0.84). Carrying capacity: C(S) = (50.24 + 0.6927*S) * S, i.e. the predicted density on the sandy habitat times the sandy area. Two-term fits (S and P) gave only marginal improvement (e.g. Sa = 0.0701 - 0.0004*P + 0.0023*S, R^2=0.84), so the single-variable sandy-area form is retained for parsimony.

### Outcome Analysis

The functions are monotone increasing in open-sandy area: bigger open-sand patches have higher fecundity, higher juvenile and adult survivorship, and higher density, hence a larger C. Example: a patch with 50 ha of open sand predicts Fa ~ 9.3, Sj ~ 0.17, Sa ~ 0.126, density ~ 85 lizards/ha, C ~ 4,250 lizards. Limitations: only 8 patches, so the fits are sensitive to the extremes (the two largest patches); the linear forms may not hold far outside the observed sandy-area range (~1.7 to 84 ha); and the vital rates are patch averages that themselves come from a single year of data. Density is the weakest link in C because it is measured, not fitted, and the C(S) function inherits that uncertainty.

## Subtask 4: Task 4. Using the migration histogram, estimate the probability that a lizard survives migrating between any two patches

### Problem

Task 4. Using the migration histogram, estimate the probability that a lizard survives migrating between any two patches i and j. About 10% of juveniles migrate; adults do not.

### Analysis

The histogram gives the proportion of recaptured juveniles by distance moved (50 m bands up to 350 m): 0.42, 0.25, 0.18, 0.12, 0.02, 0, 0.01. It is a distribution of successful-move distances. The chance of completing a move declines steeply, faster than linearly, with the gap distance, because a dispersing juvenile is continuously exposed to predation, desiccation and starvation across non-scrub ground; each extra meter multiplies the risk. The survival probability is therefore modeled as an exponential decay in the gap distance D(i,j), scaled so the distribution's mean move distance is reproduced.

### Modeling Process

Treat the histogram as a distribution over the band midpoints (25, 75, ..., 325 m). Its mean is 80.5 m (sd 61.2 m). Model the probability that a juvenile survives a move of distance D as P_survive(D) = exp(-D / 80.5). Because 10% of juveniles attempt migration, the expected fraction of a patch's new juveniles that arrive at a patch D metres away is 0.10 * exp(-D/80.5): ~0.054 at 50 m, ~0.029 at 100 m, ~0.016 at 150 m, ~0.008 at 200 m, ~0.002 at 300 m. Between two specific patches i and j the probability is 0.10 * exp(-D(i,j)/80.5), with D(i,j) the centre-to-centre gap.

### Outcome Analysis

Migration is a short-range process: most successful moves are under 150 m, and the expected arrival fraction at a neighbouring patch is of order 1-5% of the new juveniles, falling to well under 1% beyond ~200 m. This makes immigration a modest supplement that can sustain small, marginal patches but cannot rescue a patch that is far from any source. Limitations: the histogram is of successful recaptures within 350 m, so it under-represents very long or failed moves and the true mean move distance may be larger; the exponential is a smooth fit to 7 banded proportions rather than a measured survival curve; and D(i,j) was not given as a distance matrix (no map coordinates), so the formula is provided as a function of the gap, to be evaluated once pairwise distances are known.

## Subtask 5: Task 5. Develop a model to estimate the overall scrub-lizard population of the 29-patch landscape in Table 3, and determ

### Problem

Task 5. Develop a model to estimate the overall scrub-lizard population of the 29-patch landscape in Table 3, and determine which patches support a viable population and which do not.

### Analysis

Each patch is modelled as a discrete logistic population of total (both sexes) lizards N_i with carrying capacity C_i from Task 3: N_{t+1} = N_t + r_i * N_t * (1 - N_t/C_i), so N_i tends to C_i if the intrinsic growth r_i is positive and declines toward zero (rescued only by immigration) if r_i is negative. The intrinsic per-capita growth at an equilibrium 50/50 sex ratio is r_i = F(S_i)*Sj(S_i) + 0.5*Sa(S_i) - 1, using the Task-3 vital-rate functions, because each individual produces F eggs (on half of them being female), of which Sj survive as new cohorts, and half the patch (the adults) survives at rate Sa. A patch is self-sustaining only if it can hold a minimum viable population; the expert-grounded threshold is on the order of a few hundred, taken as MVP = 200 lizards (low end of the 200-500 range). Immigration (Task 4) is added as a small inflow to declining patches.

### Modeling Process

For each of the 29 patches compute sandy area S_i, then C_i = (50.24 + 0.6927*S_i)*S_i and r_i = F(S_i)*Sj(S_i) + 0.5*Sa(S_i) - 1 with the Task-3 fits. Equilibrium N_i* = C_i if r_i > 0; otherwise N_i* = the immigration-rescued steady state (inflow balanced by decline), which is small. Classify by C_i against MVP=200 and the sign of r_i: viable-self-sustaining (C>=200 and r>0); viable-capacity-needs-support (C>=200 but r slightly negative, i.e. a large source patch under mild pressure); marginal (100<=C<200); not viable (C<100). Parameter table (empirical values with provenance; all other numbers are derived from the task's own datasets): MVP = 200 lizards, interval [200, 500], source: expert exchange 2 (no published threshold; empirical judgment of a few hundred breeding individuals for a small short-lived lizard); controlled-burn return interval = 8-12 years, interval [5, 15] years, source: expert exchange 3 (typical managed Florida-scrub burn cycle).

### Outcome Analysis

The overall landscape population at equilibrium is about 2,189 lizards. The distribution is strongly dominated by the largest patches: patch 12 (74.4 ha, 19.2 ha sand) is the only patch with positive intrinsic growth and a full carrying capacity, N* ~ 1,216. Thirteen patches (1, 2, 6, 9, 10, 11, 13, 15, 17, 20, 27, 28, 29) have carrying capacity >= 200 but a small negative intrinsic growth; these are suitable for occupation and can be treated as source patches that need management (burning, protection) to hold or restore growth - several (2, 15, 17) are only ~2-3% below replacement and would likely turn positive with better open-sand condition. Five patches (5, 7, 8, 14, 19) are marginal (C ~ 100-200). Ten patches (3, 4, 16, 18, 21, 22, 23, 24, 25, 26) are too small (C < 100) to support a viable population and depend on immigration from larger sources. Limitations: the per-patch model ignores the spatial coupling between patches (no distance matrix is supplied, so immigration is folded in as a small uniform inflow); the vital-rate functions are extrapolated to small patches they were not measured on; and MVP=200 is an empirical judgment, so the viable/marginal boundary is approximate.

## Subtask 6: Task 6. Vegetation density in the Florida scrub increases by about 6% per year. Make a recommendation on a policy for co

### Problem

Task 6. Vegetation density in the Florida scrub increases by about 6% per year. Make a recommendation on a policy for controlled burning.

### Analysis

The scrub is fire-dependent: without burning, vegetation densifies at ~6%/yr and the open-sandy habitat that the lizards require closes up in roughly 15-20 years, after which fecundity and survivorship fall and the local population declines to extinction (small patches first). A normal, well-managed burn kills only a minority of the lizards (they flee into refugia and recolonize within a season or two), so the fire is a net benefit; the hazards are a fire regime that is too hot, too frequent, or applied to a small isolated patch with no unburned refuge nearby. The policy must therefore keep the burn interval short enough to stay well ahead of the ~15-20 year closure, and must be structured so lizards always have an unburned refuge.

### Modeling Process

Let the open-sandy fraction decay as ~1/(1+0.06 t) absent fire. To keep it from closing, burn before closure, i.e. on an interval clearly under ~15 years. Recommended return interval: 8-12 years (within the 5-15 year managed range), longer only where fuels and access justify it. For small or isolated patches (no adjacent scrub to serve as a refuge or recolonization source) lean to the shorter end of that interval and burn in small, patchy, rotating strips that leave unburned sandy refugia inside the patch; never burn a whole small patch at once. Exception: if a patch has already closed to dense oak/palmetto, is very small and isolated, holds only a few tens of lizards, or has uncontrollable fuel loads (e.g. near a developed interface), defer burning and first restore open sand by mechanical treatment (mowing, roller-chopping, selective clearing), then resume a normal burn cycle once a patchy, low-intensity fire can be carried.

### Outcome Analysis

Policy: a landscape-scale, scheduled controlled-burn program on an 8-12 year interval, with the interval shortening and the burns becoming more patchy as patch size and isolation increase, and with mechanical restoration in place of fire for patches that have already closed up or are too small and isolated to burn safely. This directly counters the 6%/yr densification (burn well before the ~15-20 yr closure), maintains the open-sandy habitat that Task 3 shows drives Fa, Sj, Sa and carrying capacity, and protects the source patches that Task 5 shows the landscape depends on. Limitations: the 6%/yr rate is an aerial-photograph average that varies with rainfall and fuel load; the 8-12 yr interval is an empirical management target rather than a fitted optimum; and the policy does not yet account for smoke-management and wildland-urban-interface constraints that can force longer intervals in practice, which is precisely when patches risk closing.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
