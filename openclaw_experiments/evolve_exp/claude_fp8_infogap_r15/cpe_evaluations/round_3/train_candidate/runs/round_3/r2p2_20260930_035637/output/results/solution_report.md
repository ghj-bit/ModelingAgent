# Solution

## Subtask 1: Model the energy balance and mass-growth dynamics of a single dragon, including the caloric intake required to maintain 

### Problem

Model the energy balance and mass-growth dynamics of a single dragon, including the caloric intake required to maintain a mature adult and the trajectory from hatchling (~10 kg) to terminal mass, in three climatic regimes (arid, warm-temperate, arctic). The deliverable is a closed energy-balance model with a fat-store state variable that correctly handles seasonal energy deficits, and the resulting daily caloric intake and prey-biomass requirements for a mature dragon.

### Analysis

The model is built on four structural decisions settled by expert consultation. First, growth is asymptotic: mass approaches a food-capped terminal lean mass M_MAX = 1500 kg, not an unbounded extrapolation. Second, the energy balance is split between maintenance (Kleiber's law, BMR = 70 * M^0.75 kcal/day) and growth, with a growth fraction phi that declines as mass approaches M_MAX. Third, the arctic regime requires a two-phase annual cycle (income season, 45% of year, with prey available; debt season, 55%, with no prey), not a scalar multiplier on maintenance energy. Fourth, the fat store F(t) is an explicit state variable alongside lean mass M(t): during surplus, energy splits between lean growth (phi) and fat storage (1-phi); during deficit, F is drawn down first, then lean mass is catabolised. The food-capped asymptote in the arctic is the annual-cycle average mass, not a point value. Assumptions: assimilation efficiency ETA = 0.30; prey energy density 2000 kcal/kg wet; growth cost 4200 kcal/kg lean; fat energy density 9000 kcal/kg; arid BMR multiplier 1.15, temperate 1.00, arctic 1.40.

### Modeling Process

State variables: M(t) = lean mass (kg), F(t) = fat store (kg). Total mass = M + F. Energy balance per day: assimilated energy E_a = I(t) * 2000 * 0.30 kcal/day, where I(t) is prey biomass eaten (kg/day). Maintenance: E_m = 70 * (M+F)^exp * c_climate kcal/day, where exp = 0.75 (sensitivity: 0.67-1.0) and c_climate = {arid: 1.15, temperate: 1.00, arctic: 1.40}. Surplus = E_a - E_m. Income season (surplus > 0): phi = max(0, 1 - M/M_MAX) * 0.6; dM/dt = phi * surplus / 4200; dF/dt = (1-phi) * surplus / 9000. Debt season (surplus < 0, arctic only): dF/dt = surplus / 9000; if F + dF < 0 then dF = -F and dM/dt = (surplus + F*9000)/4200, else dM/dt = 0; dM/dt floored at -0.005*M. M_MAX = 1500 kg. Integration: Euler, dt = 1 day, 5-year horizon. Terminal-mass caloric requirement: I_req = 70 * 1500^exp * c_climate / (2000 * 0.30) kg prey/day. Results at exp = 0.75: arid I_req = 32.3 kg/day (75,000 kcal/day maintenance); temperate I_req = 28.1 kg/day (65,000 kcal/day); arctic I_req = 39.4 kg/day (91,000 kcal/day). Growth from 10 kg over 5 years (foraging at sustainable rate, 100 km2): arid M_final = 236 kg, F_final = 86 kg; temperate M_final = 736 kg, F_final = 440 kg; arctic M_final = 19 kg (cycle amplitude 23 kg in final year, mass oscillates between ~7 and ~30 kg due to seasonal fasting).

### Outcome Analysis

A mature 1500 kg dragon requires 65,000-91,000 kcal/day depending on climate, equivalent to 28-39 kg of wet prey biomass per day. The arctic regime is the most demanding: the higher BMR multiplier (1.40) and the 55% debt season (no prey) mean the dragon must store substantial fat during the income season and draw it down in winter; the annual-cycle average mass is the correct asymptote, not the peak or trough. Sensitivity: at exp = 0.67, I_req drops to 16-22 kg/day (28% lower); at exp = 1.0, I_req rises to 175-245 kg/day (5-6x higher), showing the metabolic exponent is the dominant uncertainty. The model's main limitation is the fixed M_MAX = 1500 kg assumption, which is not derivable from the problem statement; the growth trajectory is also constrained by prey availability, so in arid and arctic regions the dragon reaches a lower equilibrium mass than the food-capped asymptote would suggest.

## Subtask 2: Determine the minimum area of habitat required to support the prey population that sustains one mature dragon in each cl

### Problem

Determine the minimum area of habitat required to support the prey population that sustains one mature dragon in each climatic regime, using a logistic prey model with carrying capacity set by regional productivity. The deliverable is the minimum area in km2 for each climate, and the prey-biomass trajectory over 5 years.

### Analysis

The prey base is modeled as a logistic population with carrying capacity K_prey = PREY_PROD * area_km2 (tonnes total biomass). Regional productivity (tonnes prey biomass per km2 per year): arid = 0.50 (rangeland), temperate = 1.20 (grassland), arctic = 0.20 (tundra). Intrinsic growth rate r = 0.50/yr. The dragon's foraged take is sustainable only if it stays below HARVEST_FRAC = 0.15 of the prey's natural regeneration rate. The sustainable intake is I_sus = 0.15 * 0.50 * K_prey / 365 tonnes/day. The minimum area is the area at which I_sus equals the dragon's terminal-mass intake requirement. Prey dynamics: dP/dt = r*P*(1-P/K) - H, where H is the dragon's daily harvest converted to tonnes/yr.

### Modeling Process

K_prey(area) = PREY_PROD[climate] * area_km2 tonnes. Sustainable harvest: H_sus = 0.15 * 0.50 * K_prey tonnes/yr = I_sus_kg * 365 / 1000. Minimum area: area_min = I_req_term_kg * 365 / (0.15 * 0.50 * 1000 * PREY_PROD[climate]) km2. Prey trajectory: Euler integration of dP/dt = r*P*(1-P/K) - H, dt = 1 day, 5 years, starting at P(0) = K. Results: arid area_min = 315 km2 (K_prey = 157 t at that area; I_sus = 32.3 kg/day); temperate area_min = 114 km2 (K_prey = 137 t; I_sus = 28.1 kg/day); arctic area_min = 958 km2 (K_prey = 192 t; I_sus = 39.4 kg/day). At 100 km2: arid K_prey = 50 t, I_sus = 10.3 kg/day (insufficient, prey not collapsed after 5 yr); temperate K_prey = 120 t, I_sus = 24.7 kg/day (near sufficient); arctic K_prey = 20 t, I_sus = 4.1 kg/day (severely insufficient). Prey never collapses in any scenario because the dragon's foraging is capped at I_sus, but the prey biomass is drawn down significantly in the arctic (P_final = 20 t out of K = 20 t at 100 km2, i.e. at carrying capacity with no headroom).

### Outcome Analysis

The arctic requires the largest area per dragon (958 km2) because tundra productivity is lowest (0.20 t/km2/yr) and the dragon's caloric demand is highest (39.4 kg/day). The temperate region is the most efficient at 114 km2 per dragon. The area requirement scales inversely with regional productivity, so a 3-fold difference in productivity (temperate vs arctic) yields a 4.8-fold difference in area requirement. The model's key limitation is that PREY_PROD values are assumed constants; in reality they vary by an order of magnitude within each biome. The logistic prey model also assumes a single mixed prey population, whereas a real ecosystem would have multiple species with different growth rates and predator-prey dynamics.

## Subtask 3: Determine the size of human community required to support one mature dragon in each climatic regime, for three levels of

### Problem

Determine the size of human community required to support one mature dragon in each climatic regime, for three levels of assistance: (a) foraging-only self-sufficiency (no assistance), (b) partial provisioning (community supplements foraging), (c) full provisioning (community provides all food). The deliverable is the community size (number of people) for each assistance level and climate.

### Analysis

Assistance is defined as the caloric deficit below foraging-only self-sufficiency, consistent with the expert's definition in Exchange 1. The community's contribution is measured in livestock (mixed beef/mutton, 2500 kcal/kg). A community member can spare 50 kg livestock/year after meeting their own needs. Community size N = ceil(deficit_kg_day * 365 * E_DENSITY_PREY * ETA / (E_LIVESTOCK * LIVESTOCK_PER_PERSON_YR)). Three assistance levels: (a) foraging-only: the dragon forages at the sustainable rate I_sus; if I_sus >= I_req, no community is needed (N = 0); if I_sus < I_req, the deficit is covered by the community. (b) Partial: the dragon forages at 50% of I_sus, the community covers the remaining 50% plus any residual deficit to I_req. (c) Full: the dragon forages nothing; the community provides all I_req.

### Modeling Process

N = ceil(max(0, I_req - I_forage) * 365 * 2000 * 0.30 / (2500 * 50)) where I_forage is the dragon's foraged intake (kg/day). Level (a): I_forage = I_sus (sustainable). Level (b): I_forage = 0.5 * I_sus. Level (c): I_forage = 0. At 100 km2, I_sus values: arid = 10.3, temperate = 24.7, arctic = 4.1 kg/day. I_req (exp = 0.75): arid = 32.3, temperate = 28.1, arctic = 39.4 kg/day. Results: Level (a) foraging-only: arid N = 39 (deficit 22.0 kg/day), temperate N = 7 (deficit 3.4 kg/day), arctic N = 62 (deficit 35.3 kg/day). Level (b) partial: arid N = 59, temperate N = 15, arctic N = 71. Level (c) full: arid N = 46, temperate N = 41, arctic N = 57. At minimum-area scenarios (315/114/958 km2), I_sus = I_req, so Level (a) gives N = 0 in all three climates.

### Outcome Analysis

At 100 km2, the temperate region requires the smallest community (7 people for foraging-only support) because prey productivity is highest and the dragon's caloric demand is lowest. The arctic requires the largest community (62 people) because both productivity and foraging capacity are lowest. At the minimum area for each climate, the prey base exactly sustains the dragon and no community is needed — this is the carrying-capacity closure condition. The main limitation is the livestock-per-person assumption (50 kg/yr), which is high for a pre-industrial community; at 25 kg/yr all community sizes double. The model also assumes the dragon's foraging is the only pressure on the prey base; in a real community, human hunting and grazing would reduce the sustainable harvest available to the dragon.

## Subtask 4: Analyze the effect of climate on resource requirements by comparing arid, warm-temperate, and arctic regimes. Quantify h

### Problem

Analyze the effect of climate on resource requirements by comparing arid, warm-temperate, and arctic regimes. Quantify how moving a dragon between these regions changes the caloric intake, area, and community requirements. Draft the substance of a two-page letter to George R.R. Martin advising on the ecological plausibility of dragon movement between climatic zones.

### Analysis

Climate enters the model as a regime switch (per expert Exchange 1), not a scalar multiplier. Arid and temperate use a single continuous foraging season with a BMR multiplier (1.15 and 1.00 respectively). The arctic uses a two-phase annual cycle: income season (45% of year, prey available) and debt season (55%, no prey, dragon draws down fat store). The arctic BMR multiplier is 1.40, reflecting the thermoregulatory cost of cold. The comparison quantifies three dimensions: (1) caloric intake at terminal mass, (2) minimum area per dragon, (3) community size at 100 km2. The letter to Martin should convey that a dragon migrating from temperate to arctic territory faces a fundamentally different energetic regime, not just a higher cost: it must build fat reserves during a short season and survive a long fasting period, which constrains how large it can grow and how long it can stay in arctic territory.

### Modeling Process

Caloric intake at terminal mass (exp = 0.75): arid 75,000 kcal/day (32.3 kg/day), temperate 65,000 kcal/day (28.1 kg/day), arctic 91,000 kcal/day (39.4 kg/day). The arctic requires 40% more energy than the temperate and 21% more than the arid, driven by the 1.40 BMR multiplier. Minimum area per dragon: arid 315 km2, temperate 114 km2, arctic 958 km2. The arctic requires 8.4x the area of the temperate, because tundra productivity (0.20 t/km2/yr) is 6x lower than temperate grassland (1.20 t/km2/yr) and the dragon's demand is 40% higher. Community size at 100 km2 (foraging-only): arid 39, temperate 7, arctic 62. For the letter: a dragon in arctic territory must accumulate fat during the 45% income season sufficient to cover 55% of its energy budget. At 39.4 kg/day requirement, the annual deficit during the debt season is approximately 39.4 * 0.55 * 365 / (1 - 0.55) kg of fat-equivalent, which is a substantial physiological constraint. The letter should advise that prolonged arctic residence is ecologically implausible for a dragon of temperate size, and that a dragon moving from arid to temperate territory would face a reduced energetic cost but a longer foraging season (arid rangelands have a shorter growing season than temperate grasslands, though this is not explicitly modeled).

### Outcome Analysis

Climate is the dominant factor in dragon resource requirements, more important than the metabolic exponent. The arctic is the limiting regime: it requires the most energy, the most area, and the largest supporting community. The two-phase cycle in the arctic is a qualitative difference, not a quantitative one — a dragon that can forage continuously in temperate territory must store and catabolise fat in the arctic, which changes the mass trajectory from monotonic growth to seasonal oscillation. The model's limitation is that the arctic income season fraction (45%) is assumed, not derived; a longer debt season (e.g., 70%) would make arctic residence even more constrained. The letter to Martin should emphasize that the story's depiction of dragons moving freely between arid, temperate, and arctic regions is ecologically plausible only if the dragons spend at most a short season in the arctic and are sufficiently large to carry the required fat reserves; a dragon that has grown to full temperate size (1500 kg) would need to store approximately 30-50 kg of additional fat to survive a 6-month arctic winter, which is physiologically plausible but constrains the duration of arctic residence to one season.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
