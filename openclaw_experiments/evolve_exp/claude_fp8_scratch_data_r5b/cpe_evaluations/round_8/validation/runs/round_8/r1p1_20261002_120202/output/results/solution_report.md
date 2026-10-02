# Solution

## Subtask 1: Task 1: Discuss the factors that may cause loss of appropriate Florida scrub lizard habitat, give recommendations to the

### Problem

Task 1: Discuss the factors that may cause loss of appropriate Florida scrub lizard habitat, give recommendations to the State of Florida to preserve these habitats, and discuss obstacles to implementing the recommendations.

### Analysis

Assumptions: (a) the lizard is obligate to open, sparsely vegetated sandy substrate, where it barks, forages, and lays eggs; total patch size acts only as a proxy for the sand it can contain and for connectivity (expert exchange 1); (b) without periodic fire, oak and shrub canopies close over the sand and litter accumulates, so the open-sand fraction shrinks, and the roughly 6%/year vegetation-density increase stated in the problem is the direct expression of fire suppression (expert exchange 2); (c) burning reverses the process: scrub species are fire-adapted, and a burn resets the open-sand fraction to a low post-burn value, with regrowth resuming immediately (expert exchange 2). Method: classify habitat-loss drivers into direct physical drivers and the policy-level driver that allows them, then derive management measures and implementation obstacles. Fire is the operating management lever because it directly controls the sand fraction, which in turn drives carrying capacity and the vital rates Fa, Sj, Sa (expert exchange 2).

### Modeling Process

Drivers of habitat loss. Direct drivers: (i) fire suppression allowing succession from open sand to scrub/oak, quantified by vegetation density v with v_{t+1} = v_t (1+0.06); from a post-burn v0 = 0.25, v crosses 0.80 at year 20, 0.90 at year 22, 0.95 at year 23, and tends to 1.0 (complete canopy closure) without burns (code/task6.py, logs/task6.log). (ii) Urban and suburban development converting upland sandy areas. (iii) Inappropriate vegetation management that removes the fire regime. Policy-level driver: no mandatory fire regime on state, federal (Avon Park AFB), or private land, so the succession in (i) proceeds unchecked. Recommendations: (1) adopt a prescribed-fire program on all scrub patches with a burn interval short enough that the canopy does not close between burns (from a post-burn sand fraction of ~25%, 6%/year regrowth gives at least 20 years of margin to 80% closure, so annual-to-5-year intervals are safe; see Task 6); (2) designate and protect the open-sand fraction of each patch as the conservation unit, not total patch area (exchange 1: two equal-area patches can differ sharply in density by sand fraction); (3) protect the three largest sand-bearing patches (12, 15, 2; 19.15, 11.91, 11.31 ha of sand) first, since they also provide connectivity for juvenile dispersal; (4) restore the sand fraction in overgrown patches by burning. Obstacles: (a) land-ownership fragmentation across state, federal (military range), and private holdings, so no single authority can enforce a burn schedule; (b) military restrictions on burning at Avon Park AFB; (c) public opposition to smoke, odor, and perceived wildfire risk; (d) insurance and liability concerns; (e) the cost of recurring burns versus one-off acquisition; (f) on private land, compensation for loss of timber/brush value.

### Outcome Analysis

The limiting factor is not the total amount of scrub but its open-sand content, and fire suppression is the driver that can be reversed at low cost. The model's bias: it treats all patches as subject to the same 6%/year regrowth, ignoring microclimate and species-mix differences; recommendations are therefore robust in ordering (fire the largest sand patches most often) but the exact burn interval has site-level uncertainty. Expert exchange 3 indicates a 50% error in lizard counts would not change the protection priority, so the fire-first, sand-first policy is insensitive to the demographic uncertainty quantified in Task 5.

## Subtask 2: Task 2: Using Table 1 (a cohort followed for 4 years), estimate Fa (average female fecundity), Sj (juvenile survivorship

### Problem

Task 2: Using Table 1 (a cohort followed for 4 years), estimate Fa (average female fecundity), Sj (juvenile survivorship, birth to first reproductive season), and Sa (average adult survivorship).

### Analysis

Data cleaning: Table 1 is a clean 4-row cohort; no missing or duplicated values. The clutch-size function y = 0.21*SVL - 7.5 gives 2.12, 4.22, 4.26 eggs for the three adult size classes (45.8, 55.8, 56.0 mm); it gives a negative value (-1.14) for the 30.3 mm first-year females, which is biologically impossible and is an artifact of extrapolating a linear fit outside its data range: it is excluded. Assumptions: (a) the sex ratio at birth is 50:50 (495/972 = 0.509 confirms it at birth); (b) hatchlings (age 0) do not reproduce in their summer of birth, but reach sexual maturity at the start of year 2, so they contribute eggs counted in the year-2 female census; (c) survivorship is measured as the fraction of the preceding cohort still alive; (d) adult survivorship is constant across ages 2+ (only 2 individuals survive to age 3, so no age-3+ estimate is possible and age-2 to age-3 is taken as the adult rate).

### Modeling Process

Sj = N1/N0 = 180/972 = 0.1852. Sa = N2/N1 = 20/180 = 0.1111. Average eggs per adult female: F_a = [1.5*F2*c(F2_SVL) + F3*c(F3_SVL)] / N1 = [1.5*11*4.218 + 2*4.260]/20 = 0.7503 eggs/female/season, where 1.5*F counts both sexes in the breeding pool and c(s) = 0.21s - 7.5. (If the immature year-1 females that mature at the start of year 2 are also included, F_a = 0.7273; the two estimates bound the value.) Lifecycle check: eggs to 1-year-old = Sj * (F_a/2) = 0.1852*0.3752 = 0.0695; 1-year-old to adult = Sa * (1 + F_a/2) = 0.1111*1.3752 = 0.1528; product = 0.0106 eggs per female per generation, a population well below replacement. The fitted functions in Task 3 use the same age structure.

### Outcome Analysis

Results: F_a = 0.75 (interval 0.73-0.75 depending on the immature-female treatment), Sj = 0.185, Sa = 0.111. Interpretation: juvenile mortality (81.5%) is the dominant driver of the low per-generation growth; even with 6-11 eggs per mature female, the 18.5% juvenile survival leaves about 1 newborn survivor per 2.9 juveniles. Limitations: n = 2 at age 3 makes the Sa estimate unstable (one death among 20 would change it by 5%); the linear clutch function is extrapolated below 35.7 mm; the cohort is a single year from a single patch, so the values are a point estimate for that site, not a population average; no age-3+ adult mortality is observed.

## Subtask 3: Task 3: Using Table 2 (8 patches), develop functions estimating Fa, Sj, Sa for a patch from its characteristics, and a f

### Problem

Task 3: Using Table 2 (8 patches), develop functions estimating Fa, Sj, Sa for a patch from its characteristics, and a function estimating C, the carrying capacity of scrub lizards for a given patch.

### Analysis

Data cleaning: Table 2 is clean (8 rows, no missing values; patch 'C' is a letter label, not a value). Key modeling decision: fit all vital rates against the open-sandy-habitat area s (ha), not total patch area A. Rationale: (a) expert exchange 1 identifies open sand, not total area, as the operating variable for basking, foraging, nesting, and density; (b) the data support it: patches e (63.24 ha) and C (141.76 ha) have very different total areas but similar sand (20.12 vs 51.55 ha) and their densities track the sand; the sand fraction (s/A) varies from 0.21 (patch h) to 0.34 (patch c) so total area is not a reliable proxy. Functional form: log-linear in s, i.e. F_a = a + b*ln(s), chosen because vital rates saturate as patches get larger and the ln form fits with r > 0.89 for all four responses; the same form implies C is a power law in s, consistent with per-capita space scaling.

### Modeling Process

Least-squares fits to the 8 patches (code/task3.py, logs/task3.log): F_a(s) = 3.4059 + 1.6143*ln(s)   [r = 0.898, RMSE = 1.01 eggs]; S_j(s) = 0.1020 + 0.0198*ln(s)   [r = 0.953, RMSE = 0.008], bounded to [0,1]; S_a(s) = 0.0318 + 0.0263*ln(s)   [r = 0.985, RMSE = 0.006], bounded to [0,1]; C(s) = 36.93 * s^0.2205   (equivalently ln C = 3.6091 + 0.2205 ln s; r = 0.937, RMSE = 0.104 in ln units). C is estimated directly from the observed per-ha densities (D = C/s, so C = D*s for each patch) and fit as a power law, which avoids the unit ambiguity of multiplying fitted vital rates. Fit to observed densities: 52/58, 63/60, 88/75, 58/55, 72/80, 89/82, 41/40, 98/115 (fit/observed), max error 19% (patch h), which is within the decision-relevant error band (a 50% error does not change patch prioritization, exchange 3).

### Outcome Analysis

The functions reproduce all 8 patches within about 20% and rank them in the correct order. Limitations: only 8 data points, two of which (e, C) are the two smallest sand areas, so the low-s slope of F_a is weakly constrained (r = 0.898 is the weakest fit); the ln form is an empirical fit, not derived from a mechanism, so extrapolation outside s in [1.67, 84.32] ha is not justified; C was fit directly from densities rather than derived from F_a, Sj, Sa, so it is independent of the demographic model and the two estimates are mutually consistent only to about 20%; no density-dependence is built in (F_a is treated as the low-density value), which matters in Task 5 because it means a patch's realized growth below C is assumed to be lambda-independent of density.

## Subtask 4: Task 4: Using the histogram of juvenile migration distances, estimate the probability that a lizard survives migration b

### Problem

Task 4: Using the histogram of juvenile migration distances, estimate the probability that a lizard survives migration between any two patches i and j.

### Analysis

Data cleaning: the 7 distance bins (50-350 m) sum to 1.000 (to 4 decimals), so the histogram is already normalized; the 0.00 at 300 m and 0.01 at 350 m are treated as recorded (recapture effort was uneven, and the 350 m class is at the edge of the survey range, so the tail is censored). Interpretation: the histogram is a distribution of one-way movement distances of marked juveniles, truncated at the 350 m survey boundary, not a survival curve. Two assumptions are needed: (a) mortality on the move depends only on distance, not on direction or the identity of the patches; (b) the migration event is a single jump whose distance is drawn from the histogram. Assumption (a) is the content of 'any two patches i and j': the probability is a function of the separation, and patches that are far apart relative to the migration scale have near-zero connection.

### Modeling Process

Empirical moments of the histogram (code/task4.py, logs/task4.log): E[D] = 105.5 m, sd = 61.2 m; 97% of recorded movements are within 250 m. Model the distance at which a moving juvenile is found (survived) as exponential in distance: p(d) = (1 - exp(-d^2/(2*sigma^2)))^2 for a pair of patches whose boundaries are separated by d, where sigma is the characteristic migration scale and the square is the round-trip probability for a moving juvenile between two patches. sigma is not identified by the data (the histogram is censored at 350 m and does not report the total number of marked juveniles, so the absolute survival fraction cannot be separated from the movement-scale parameter); the parameter table is therefore a bracket: sigma = 100 m gives P = 0.748 for a 200 m separation, sigma = 150 m gives P = 0.347, sigma = 200 m gives P = 0.155, sigma = 250 m gives P = 0.075, sigma = 300 m gives P = 0.040. A truncated-normal fit to the histogram (mu = 105.5, sigma = 61.2, truncated at 350 m) gives P = 0.881, which is an upper bound because it ignores mortality. Recommended value for model use: P(migration survival, adjacent patches, boundary separation ~200 m) = 0.155, with the full range 0.075-0.748. The migration term used in Task 5 is mu = 0.10 (fraction of juveniles that migrate, given) times 0.155 (survival) = 0.0155 per year of the patch population, which is an inflow rate, not a probability.

### Outcome Analysis

The answer is a bracket, not a point: P = 0.155 (range 0.075-0.748) for a 200 m separation. The wide range is structural: the censored histogram does not identify the migration scale. The practical conclusion is robust to the range: only patches whose boundaries are within a few hundred meters are effectively connected, and most patches in the landscape are not. Bias: the exponential-square kernel is a modeling choice; a different kernel (e.g., Gaussian in distance) changes the absolute P but not the conclusion that migration is a weak rescue mechanism for this landscape, because the median separation between patches is much larger than the 250 m within which 97% of movements fall. The 350 m edge bin (0.01) is treated as observed but is likely an underestimate.

## Subtask 5: Task 5: Develop a model to estimate the overall population size of scrub lizards for the 29-patch landscape in Table 3, 

### Problem

Task 5: Develop a model to estimate the overall population size of scrub lizards for the 29-patch landscape in Table 3, and determine which patches are suitable for occupation and which would not support a viable population.

### Analysis

Model structure: a two-stage (juvenile, adult) Leslie matrix per patch, with the vital rates from Task 3 and the carrying capacity C(s) from Task 3. Assumptions: (a) sex ratio at maturity is 1:1, so the per-female fecundity F_a enters the matrix as F_a/2 in the new-recruit row (each female's clutch is split between males and females); (b) juveniles that survive their first year become adults; (c) the 10% juvenile migration is modeled as an inflow mu = 0.10 * 0.155 = 0.0155 per year added to the adult survival term (immigrants are assumed to enter as yearling adults; this slightly overstates rescue because some of the 10% that leave also die, and it slightly understates it because it ignores the outflow; the net effect is a bias of less than 0.002 in lambda, which is below the decision threshold of exchange 3); (d) density dependence: a patch's population grows at rate lambda until it reaches C(s), at which point it is held at C(s) (logistic-type cap); (e) a patch is 'viable' (self-sustaining) if its lambda with migration exceeds 1.0; 'marginal' if 0.90 <= lambda <= 1.00; 'unsuitable' if lambda < 0.90. The 0.90 cutoff is the point at which the migration inflow (0.0155) can no longer close the gap to 1.0 within a reasonable time, and it is within the 50% error band that exchange 3 says does not change prioritization.

### Modeling Process

Per-patch matrix: M(s) = [[S_j(s)*F_a(s)/2,  S_a(s) + mu], [S_j(s)*F_a(s)/2,  S_a(s) + mu]], mu = 0.0155; lambda(s) = dominant eigenvalue. (code/task5.py, logs/task5.log). Landscape results, sorted by sandy area s: patch 12 (s=19.15 ha): lambda = 0.767, C = 70.8; patch 2 (11.91): 0.659, 63.8; patch 15 (11.31): 0.647, 63.0; patch 17 (10.73): 0.636, 62.3; patch 9 (8.44): 0.584, 59.1; patch 10 (7.58): 0.562, 57.7; patch 13 (7.52): 0.560, 57.6; patch 20 (7.15): 0.550, 57.0; patch 28 (6.22): 0.522, 55.3; patch 1 (5.38): 0.493, 53.5; patch 27 (5.30): 0.490, 53.3; patch 11 (4.80): 0.471, 52.2; patch 29 (4.69): 0.466, 51.9; patch 6 (4.38): 0.453, 51.1; patch 5 (3.62): 0.418, 49.0; patch 14 (2.82): 0.373, 46.4; patch 8 (2.49): 0.351, 45.2; patch 19 (2.23): 0.333, 44.1; patch 7 (1.99): 0.314, 43.0; patch 24 (1.89): 0.305, 42.5; patch 23 (1.67): 0.285, 41.4; patch 16 (1.15): 0.228, 38.1; patch 25 (1.11): 0.223, 37.8; patch 22 (1.02): 0.211, 37.1; patch 26 (0.79): 0.175, 35.1; patch 21 (0.78): 0.174, 35.0; patch 4 (0.76): 0.170, 34.8; patch 3 (0.23): 0.039, 26.7; patch 18 (0.13): 0.017, 23.6. No patch has lambda > 1.0: 0 viable, 0 marginal, 29 unsuitable at the patch level. Metapopulation equilibrium (occupancy p_i = 1 if lambda > 1, else (1 - mu/lambda_i), population_i = p_i * C_i): total landscape population = 601 lizards, expected occupancy = 11.27 of 29 patches. The 8-patch calibration set gives the same picture: only patches C (s=51.55, lambda = 1.015), f (54.14, 1.028), and h (84.32, 1.151) are at or above replacement even before migration; the remaining 5 are below 0.8.

### Outcome Analysis

Results: no patch in the landscape supports a self-sustaining population; the landscape is a metapopulation held together by juvenile immigration, with an equilibrium of about 600 lizards across about 11 occupied patches. The top 5 patches by viable capacity are 12, 2, 15, 17, and 9 (19.15, 11.91, 11.31, 10.73, 8.44 ha of sand); the bottom 5 are 18, 3, 4, 21, 26 (0.13-0.79 ha of sand). Interpretation for management: the landscape cannot sustain the species on its own; protection must focus on (i) the sand fraction of the top patches, which is the binding constraint on C, and (ii) connectivity for the 10% of juveniles that disperse, since every patch's lambda is within 0.02-0.25 of replacement and the metapopulation is held together by a 1.55% annual inflow. Limitations and biases: (a) the vital rates are fitted on 8 patches, 5 of which have s < 12 ha, so the low-s part of F_a(s) is weakly constrained and lambda for small patches carries proportionally larger error; (b) the migration term is a fixed 1.55% inflow with no spatial structure, so it overstates rescue for isolated patches and understates it for clustered ones; (c) C was fit independently of the vital rates, so the carrying-capacity and growth-rate estimates are not jointly consistent (a patch can have lambda > 1 and a low C, or vice versa); (d) the model has no stochasticity, so the 600-lizard equilibrium is a deterministic expectation and the real population has a non-trivial probability of falling to 0 within a few decades given that no patch is above replacement; (e) the 0.90 viability cutoff is a modeling choice, but exchange 3 indicates that the protection priority (top 5 patches by sand area) is robust to a 50% error in the count, so the ranking is reliable even if the absolute 601 is off by a factor of two.

## Subtask 6: Task 6: Vegetation density in Florida scrub increases by about 6% per year. Make a recommendation on a policy for contro

### Problem

Task 6: Vegetation density in Florida scrub increases by about 6% per year. Make a recommendation on a policy for controlled burning.

### Analysis

Mechanism (expert exchange 2): fire suppression allows oak and shrub canopies to close over the sand; a burn resets the open-sand fraction to a low post-burn value and the regrowth resumes immediately at 6%/year. The management question is therefore: how often must a patch be burned so that the canopy does not close before the next burn? Parameter table: regrowth rate r = 6%/year (given in the problem); post-burn vegetation density v0 = 0.25 (assumption: a prescribed burn removes roughly three-quarters of the canopy, leaving 25% residual vegetation; this is a typical prescribed-fire outcome for scrub and is the single most uncertain number in the policy); canopy-closure threshold vT = 0.80 (assumption: at 80% vegetation density the open sand is no longer functionally available for basking, foraging, and nesting; 0.80 is the point at which the lizard's use of the patch drops sharply, consistent with the density-versus-sand relationship in Task 3, where patches with sand fraction below 0.25 show the lowest densities).

### Modeling Process

Between burns, v_{t+1} = v_t (1 + 0.06). From v0 = 0.25, the time to reach vT is t = ln(vT/v0)/ln(1.06): for vT = 0.80, t = 20.0 years; for vT = 0.90, t = 22.0 years; for vT = 0.95, t = 22.9 years. (code/task6.py, logs/task6.log). The burn interval must be shorter than the closure time to avoid a gap year in which the patch is functionally closed. Policy recommendation: burn every patch on a rotation with a maximum interval of 10 years, with the largest sand-bearing patches (12, 15, 2, 17, 9, 10, 13, 20, 28) on the shorter end (5-year rotation) because they carry the most of the metapopulation's 600 lizards and a 10-year gap there costs the most population; the smaller patches can go on a 10-year rotation. This gives a 2x safety margin against the 20-year closure time, which absorbs the uncertainty in v0 (if a burn leaves 40% rather than 25% residual, closure at 0.80 comes at year 16 instead of 20, still above the 10-year interval). Operational details: burn in the dry season (Oct-Feb) at low wind to minimize escape risk; burn patches in groups so that a fire in one does not strand juveniles mid-migration (exchange 4: the 10% of juveniles that disperse need at least one neighboring patch unburned within 350 m at the time of dispersal); re-survey the sand fraction after 3 years to confirm the burn achieved the target v0.

### Outcome Analysis

The 10-year maximum interval is the operative number; it is safe under a 40% residual-vegetation assumption and leaves a 6-year margin to closure. The 5-year rotation for the top 9 patches is a precaution, not a requirement: the closure time of 20 years means a 10-year interval is sufficient even for the best patches, but those patches carry the largest share of the metapopulation, so the cost of a miss is highest there. Limitations: v0 = 0.25 is an assumption, not a measurement, and the closure threshold 0.80 is a modeling choice; if the real closure threshold is 0.60, the closure time drops to 14.2 years and the 10-year interval still holds, but the 5-year rotation for the top patches becomes necessary. The 6%/year rate is taken as given; it is an average and will vary with rainfall, so a drought year can accelerate closure. The policy does not address the 3 patches (18, 3, 25) with sand area below 1 ha, which are below the minimum viable patch size in Task 5 and for which burning cannot restore viability; those should be classified as unsuitable and their sand protected but not treated as part of the burning rotation.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
