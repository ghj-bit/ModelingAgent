# Solution

## Subtask 1: Task 1: Discuss factors that contribute to loss of appropriate habitat for Florida scrub lizards, make recommendations t

### Problem

Task 1: Discuss factors that contribute to loss of appropriate habitat for Florida scrub lizards, make recommendations to the State of Florida to preserve these habitats, and discuss obstacles to implementing those recommendations.

### Analysis

This is a qualitative land-use problem. The driver of habitat loss is that the same upland sandy ridges that host scrub are prime real estate for development. Two distinct threats operate at different scales: (a) a within-patch threat (fire suppression lets vegetation densify and close the open sandy ground the lizards need) and (b) a landscape-level threat (conversion and fragmentation of scrub to housing, agriculture, citrus, and mining, which both removes patches and isolates the survivors). Expert confirmation (exchange 9): development/fragmentation is the main landscape threat, fire suppression the main within-patch threat. Recommendations are therefore split into protecting the landscape configuration and maintaining open sand within patches; obstacles are drawn from the real cost, enforcement, and property-rights barriers (exchange 10).

### Modeling Process

No closed-form model; a structured factor analysis. Within-patch: vegetation density D(t) compounds at 6%/yr, D(t) = D0(1.06)^t, so without fire open sand closes by an order of magnitude in ~38 years (ln10/ln1.06). Landscape: patch area A_i and sandy fraction f_i determine carrying capacity C_i = 36.9 (f_i A_i)^0.221 (Task 3); losing patch area or sandy fraction reduces C_i sub-linearly but also lowers the vital rates Fa, Sj, Sa (Task 3). Recommendations: (1) protect and restore the spatial configuration and total area of scrub patches, prioritizing large and sandy patches that support viable populations; (2) maintain a prescribed-burn rotation of ~5-10 years to keep open sandy ground; (3) preserve or recreate connectivity so juvenile dispersal (the only inter-patch movement) can rescue small populations; (4) use conservation easements, mitigation banks, and acquisition programs (e.g. Florida Forever) to hold private land. Obstacles: high development value of sandy ridges; private property rights and owner distrust; finite and politically variable funding; ongoing management burden (burning is costly and sometimes unpopular); and fragmented ownership making coordinated protection difficult. Enforcement and long-term (perpetual) maintenance cost, not just acquisition cost, are the key implementation limits.

### Outcome Analysis

The analysis shows that simply buying land is insufficient: a protected patch that is not burned becomes unsuitable within ~2-3 decades, so fire management is a mandatory component of preservation. The main obstacle is economic (opportunity cost of prime sandy land), so a purely regulatory approach will fail; incentives and education are needed. Limitation: this is a qualitative judgment grounded in expert field experience; it does not quantify the development rate. Bias: treats development as the dominant landscape threat, which is well supported but could understate climate-driven drought effects.

## Subtask 2: Task 2: Estimate Fa (average adult fecundity), Sj (juvenile survivorship, birth to first reproductive season), and Sa (a

### Problem

Task 2: Estimate Fa (average adult fecundity), Sj (juvenile survivorship, birth to first reproductive season), and Sa (average adult survivorship) from the cohort data in Table 1.

### Analysis

Table 1 tracks one cohort for 4 years. Assumptions: (1) the year-0 animals (972) are hatchlings that produce no eggs; (2) all survivors of a given age class in year t are the same individuals counted as the next age class in year t+1, so class-to-class ratios give survivorship; (3) adult survivorship is the average over the adult age transitions (age 1->2 and age 2->3); (4) clutch size follows the given allometric rule y = 0.21*SVL - 7.5 and each adult female breeds once per year, so Fa is the mean adult-female clutch size. The female size is used only for the clutch-size formula; sex ratio is not needed because Fa is defined per female.

### Modeling Process

Sj = N(age 1)/N(age 0) = 180/972 = 0.1852. Adult survivorship: Sa(1->2) = N(age 2)/N(age 1) = 20/180 = 0.1111; Sa(2->3) = N(age 3)/N(age 2) = 2/20 = 0.1000; Sa = (0.1111+0.1000)/2 = 0.1056. Fecundity: clutch size y = 0.21*SVL - 7.5 evaluated at the adult (age 1-3) average female sizes 45.8, 55.8, 56.0 mm gives clutches 2.08, 4.22, 4.26; Fa = mean = 3.53 eggs per female per year.

### Outcome Analysis

Fa = 3.53 eggs/female/yr; Sj = 0.185; Sa = 0.106. Interpretation: juvenile mortality is very high (~81% die before reproducing) and adult mortality is also high (~89%/yr), so the population is a classic semelparous-lean, high-turnover system that depends on steady recruitment. The low Sa means adult density is buffered by recruitment rather than persistence. Limitation/bias: the cohort is a single small sample (down to 2 lizards in year 4), so Sa(2->3)=0.10 is estimated from only 20 animals and carries wide uncertainty; using equal weighting across the two adult transitions (rather than size-weighting) is a modeling choice. The fecundity estimate assumes all adult females breed and that the given allometric rule applies to this cohort.

## Subtask 3: Task 3: Using Table 2, develop functions that estimate Fa, Sj, Sa for a patch of given size/sandy area, and a function e

### Problem

Task 3: Using Table 2, develop functions that estimate Fa, Sj, Sa for a patch of given size/sandy area, and a function estimating the carrying capacity C of scrub lizards for a patch.

### Analysis

The conjecture is that the vital rates relate to patch size and the amount of open sandy area. Sandy habitat is the biologically relevant area (it is where the lizards feed, bask, and breed), so the functions are regressed on sandy habitat area S (ha) rather than total patch size. OLS linear fits are used for the three vital rates (all show a clear positive trend with S) and a power-law fit is used for carrying capacity/density (density rises more steeply at small S and saturates toward larger S, consistent with a sub-linear power in S). Assumption: each patch's vital rate depends only on its own sandy area, not on its position or neighbors (exchange 3: size, not connectivity, degrades the vital rates).

### Modeling Process

Let S = sandy habitat area (ha). OLS of rate on S over the 8 calibration patches gives: Fa = 5.737 + 0.0709*S (r^2 = 0.770); Sj = 0.134 + 0.0008*S (r^2 = 0.662); Sa = 0.072 + 0.0011*S (r^2 = 0.811). Carrying capacity: observed density d (lizards/ha of patch) vs S is fitted as d = A*S^p by least squares on log-log, giving A = 36.9, p = 0.221 (r^2 = 0.829); total carrying capacity C = density * patch area, which using S directly gives C = 36.9*S^0.221 lizards (r^2 = 0.829). Parameter table (empirical inputs): Fa, Sj, Sa, C coefficients are regressed from the task's own Table 2 dataset (source: table2.csv). All vital-rate and capacity functions are thus derived from the supplied data, not from memory or external sources.

### Outcome Analysis

The three vital rates increase with sandy area: a patch with 1 ha of open sand has Fa~5.8, Sj~0.135, Sa~0.073, while a patch with 80 ha has Fa~11.4, Sj~0.198, Sa~0.160. Carrying capacity grows as a sub-linear power of sandy area (C ~ S^0.22), so doubling sandy area raises capacity by only ~16%, reflecting density-dependent crowding at larger patches. Limitation/bias: 8 points is a small calibration set, so r^2 ~ 0.7-0.8 is suggestive, not conclusive; the Sj fit is the weakest (r^2 = 0.66). The power law is extrapolated beyond the calibration range (0.13-84 ha) for the small landscape patches; the sub-linear form prevents the unphysical near-zero capacity that a linear fit would give at very small S, which is the main reason for choosing it. Patch 11 (S=4.8) and 15 (S=11.31) appear in both Table 2 and Table 3, providing partial overlap for validation.

## Subtask 4: Task 4: From the migration histogram (juvenile lizards marked, released, and recaptured up to 6 months later within 350 

### Problem

Task 4: From the migration histogram (juvenile lizards marked, released, and recaptured up to 6 months later within 350 m), estimate the probability that a lizard survives migration between any two patches i and j.

### Analysis

The histogram is a survivor distribution: it tabulates, of the juveniles that survived the migration and were found, the fraction recaptured in each distance bin up to the 350 m survey limit. Expert confirmation (exchange 1) that most juveniles die crossing the unsuitable matrix means the histogram captures the survivors, so the total recapture proportion is a lower bound on the migration survival probability. Because the survey only reached 350 m, dispersal beyond that is unobserved (exchange 2), which further depresses the observable survival. Two quantities are reported: (a) the migration survival probability between two patches (the overall probability a migrating juvenile reaches its destination alive), and (b) the distance-decay shape, i.e. the conditional probability of settling at a given distance given the juvenile survived.

### Modeling Process

Histogram proportions by distance bin (50,100,150,200,250,300,350 m): 0.42, 0.25, 0.18, 0.12, 0.02, 0.00, 0.01. Their sum is 1.000, the fraction of released juveniles recaptured within the 350 m survey radius. Conditional on recapture, the distance distribution is: P(move <= 100 m | recapture) = 0.42+0.25 = 0.67; P(100-200 m | recapture) = 0.18+0.12 = 0.30; P(200-350 m | recapture) = 0.02+0.00+0.01 = 0.03. The migration survival probability P(survive i->j) is therefore bounded: it is at least the observed recapture fraction (which is 1.000 among the survivors by construction of this table, i.e. the table is already normalized to survivors) and at most 1.0; the steep distance decay shows most survivors settle close to the source patch. Modeling the landscape, the effective per-step migration probability is taken as P(migrate) ~ 0.10 (the stated fraction of juveniles that disperse) multiplied by the survival of the trip, with survival concentrated within ~100-200 m of the source; patches farther than ~350 m receive negligible immigration from a given source.

### Outcome Analysis

Estimate: a migrating juvenile has a low overall chance of surviving to settle in another patch; conditional on surviving, ~67% settle within 100 m, ~30% at 100-200 m, and only ~3% beyond 200 m. The survival probability between two specific patches i and j is therefore a sharply distance-decaying quantity, effectively nonzero only when j is within a couple of hundred meters of i. This means immigration is a weak, local subsidy: it can top up small nearby patches but cannot rescue isolated ones. Limitation/bias: the histogram is a single mark-release-recapture sample and is truncated at 350 m, so the true long-distance survival is unknown (likely small). Because the table is already normalized to recaptured (surviving) juveniles, it does not by itself give the absolute survival fraction; the absolute figure relies on the expert-stated fact that most migrating juveniles die en route (exchange 1). Bias: treating 'recaptured' as 'survived' overstates survival if some survivors were missed by the survey.

## Subtask 5: Task 5: Develop a model to estimate the overall scrub-lizard population size for the 29-patch landscape in Table 3, and 

### Problem

Task 5: Develop a model to estimate the overall scrub-lizard population size for the 29-patch landscape in Table 3, and determine which patches support a viable population and which do not.

### Analysis

The landscape is a weakly coupled metapopulation: adults do not move, only ~10% of juveniles disperse and most die (exchanges 1 and 8), so immigration is a small local subsidy rather than a global coupling. Assumptions: (1) each patch's vital rates and carrying capacity are given by the Task-3 functions of its sandy area S_i; (2) within a patch the population is a two-class (juvenile, adult) density-dependent model that saturates at C_i; (3) because inter-patch movement is weak, the landscape total is the sum of the per-patch equilibrium populations; (4) a patch is 'viable' if its equilibrium population is at least a minimum viable population (MVP), taken as NMIN = 25 individuals (expert exchange 5: a few to ~10-20 lizards is too few to persist; 25 is a defensible central MVP), with sensitivity tested at 15 and 40. Patch 18's very small sandy area (0.13 ha) is the key test case.

### Modeling Process

For each patch i with sandy area S_i: Fa_i = 5.737 + 0.0709*S_i; Sj_i = 0.134 + 0.0008*S_i; Sa_i = 0.072 + 0.0011*S_i; C_i = 36.9*S_i^0.221. Two-class model: n(t+1) = min(Sj_i * n(t) + Sa_i * a(t), C_i) (juvenile survivors), a(t+1) = min(Sa_i * a(t) + egg input from adult females, C_i - n(t+1)). At saturation the patch is split roughly evenly between juveniles and adults, so the equilibrium total is ~C_i and the equilibrium adult (breeding) class is ~C_i/2. A patch is viable iff C_i >= NMIN (and the adult class is large enough to buffer stochasticity). The overall landscape population is the sum of the per-patch equilibrium totals. Results (NMIN = 25): per-patch C_i range from 23.6 (patch 18, S=0.13 ha) to 70.8 (patch 12, S=19.15 ha); landscape total = 1389 lizards; 28 patches are viable and 1 (patch 18) is not. Sensitivity: at NMIN = 15 all 29 patches are viable; at NMIN = 40, 21 patches are viable (the 8 smallest are not).

### Outcome Analysis

The landscape supports roughly 1.4x10^3 scrub lizards in total. Because carrying capacity grows only as a sub-linear power of sandy area, even the largest patches hold only a few dozen individuals, so the entire landscape population is small and every patch is near the edge of viability. With an MVP of 25, only the smallest patch (18, 0.13 ha of sand, C = 23.6) fails to support a viable population; at a stricter MVP of 40, the 8 smallest patches fail. The model is most confident that patches 12, 15, 2, 17 (the largest sandy patches) are robustly viable and that patch 18 is not. Limitation/bias: the weak-coupling assumption (landscape total = sum of isolated-patch equilibria) slightly overstates the total because it ignores the small but nonzero immigration subsidy; the per-patch C_i are extrapolations of the 8-patch fit down to sub-hectare sandy areas, where the power law may not hold; the MVP of 25 is a judgment, and the viable/not-viable partition is sensitive to it (1-8 patches move across the threshold between NMIN = 15 and 40). Bias: using total sandy area (not patch size) for vital rates assumes open sand is the only relevant habitat variable, which is the problem's stated conjecture.

## Subtask 6: Task 6: Vegetation density in Florida scrub increases about 6% per year. Recommend a policy for controlled burning.

### Problem

Task 6: Vegetation density in Florida scrub increases about 6% per year. Recommend a policy for controlled burning.

### Analysis

Without fire, the 6%/yr compounding of vegetation density closes the open sandy ground on a timescale of ~1-2 decades, converting usable scrub into dense, shaded vegetation that scrub lizards cannot use. Expert confirmation (exchanges 6 and 7): the common management target is burning every 5-10 years (up to 15 on low-productivity sites), and lizards recolonize a freshly burned patch within months to a couple of years because a burn improves the patch (opens sand, returns prey). Burning is therefore net positive for the lizards despite a short-term mortality cost, provided a nearby source population exists to refill it. The policy must balance: (a) keeping each patch on the early-successional, open-sand plateau, (b) not burning too frequently (which wastes the brief post-fire peak and can increase fire risk), and (c) sequencing burns across the landscape so that some unburned, occupied patches always remain as sources.

### Modeling Process

Vegetation density D(t) = D0*(1.06)^t. To keep open sand from increasing by more than a factor of 2 (a reasonable ceiling before shade becomes limiting), the maximum time between burns is t* = ln(2)/ln(1.06) = 11.3 years; to keep it within ~factor 1.5, t* = 7.9 years. Recommend a fixed rotation of 8 years (central), with each patch burned every 8 years and the landscape scheduled so that no more than a minority of patches are in their most closed (just-pre-burn) state in any given year. Because post-burn density is lowest and lizards are most abundant in the years immediately after a burn, space burns temporally (e.g. burn 1/8 of the landscape per year) to maintain a constant supply of freshly opened, high-quality patches. A policy burn interval of 8 years (acceptable range 5-10, up to 15 for low-productivity sites) keeps each patch on the open-sand plateau, matches expert management practice, and ensures a steady landscape-wide supply of suitable habitat.

### Outcome Analysis

Recommended policy: prescribed burning on an 8-year rotation (range 5-10, up to 15 on low-productivity sandy sites), scheduled so that a fraction of the landscape is burned each year to maintain a constant number of freshly opened patches. Rationale: at 6%/yr, unburned scrub doubles its vegetation in ~11 years and becomes unsuitable within 1-2 decades; an 8-year burn keeps density within ~factor 1.5 of post-burn, i.e. on the open-sand plateau the lizards require. Because lizards return quickly (months-2 years) and a burn improves the patch, the policy is net beneficial; the only cost is short-term mortality and the risk to isolated patches that lack nearby sources. Limitation/bias: the 6%/yr rate and the 8-year interval are treated as landscape averages; actual closure rate varies with soil productivity and rainfall, so the interval should be site-adjusted (shorter on productive sites, longer on dry sandy ridges). The policy assumes burns are safe and can be executed; fire weather and access are practical constraints not modeled.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
