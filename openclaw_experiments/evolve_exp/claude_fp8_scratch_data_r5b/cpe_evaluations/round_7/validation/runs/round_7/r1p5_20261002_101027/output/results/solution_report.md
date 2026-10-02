# Solution

## Subtask 1: Part I.A: Build a clean 2009 energy profile for each of the four border states (CA, AZ, NM, TX) from the EIA SEDS datase

### Problem

Part I.A: Build a clean 2009 energy profile for each of the four border states (CA, AZ, NM, TX) from the EIA SEDS dataset, quantifying each state's total energy consumption, its fuel mix, and its use of cleaner/renewable sources.

### Analysis

Assumptions: (1) the 14 headline variables (TETCB total consumption, TEPRB total production, PATCB petroleum, NGTCB natural gas, CLTCB coal, NUETB nuclear, HYTCB hydro, WYTCB wind, SOTCB solar, GETCB geothermal, WWTCB wood & waste, EMTCB ethanol, RETCB EIA renewable total, ESTCB electricity sold) in Billion Btu summarize each profile; (2) 'cleaner/renewable' is reported on two frames — a total-consumption share and a renewable-ELECTRICITY share (hydro+wind+solar+geothermal over electricity sold), because electricity is the frame in which renewable adoption is decided; (3) nuclear is a low-carbon source but is NOT a renewable, so it is shown separately and excluded from the renewable share. Method: pivot the long (MSN, State, Year, Data) table to a state-year panel for the 14 variables, compute shares = fuel/total in 2009. This is sound because it uses the EIA's own total and by-fuel totals directly, with no cross-unit conversion needed.

### Modeling Process

Data cleaning: 105,744 raw rows, 0 nulls in Data, 0 duplicate (MSN,State,Year); 567 negative values occur only in net-import codes (excluded from the profile set); 18,173 zeros (17%) are genuine zeros (wind/solar/geothermal not deployed before the 1980s-90s), not missing. Profile for state s, 2009: total T_s = TETCB_s,2009; share of fuel f = f_s,2009 / T_s,2009; renewable-electricity share = (HY+ WY + SO + GE)_s,2009 / ESTCB_s,2009; total-renewable share = RETCB_s,2009 / T_s,2009.

### Outcome Analysis

2009 profiles (Billion Btu; total consumption): CA 8.01e3 (petroleum 44.8%, natural gas 29.9%, coal 0.7%, nuclear 4.2%, hydro 3.4%, geothermal 1.6%, wind 0.7%, solar 0.4%); AZ 1.45e3 (petroleum 37.2%, natural gas 25.9%, coal 28.4%, nuclear 22.1%, hydro 4.3%); NM 0.67e3 (coal 45.7%, natural gas 36.9%, wind 2.3%, no nuclear; petroleum the remainder); TX 11.3e3 (petroleum 48.8%, natural gas 30.7%, coal 13.3%, nuclear 3.8%, wind 1.7%). Total-renewable share of consumption 2009: CA 8.9%, AZ 7.1%, NM 5.3%, TX 3.2%. Renewable-electricity share of electricity sold 2009: CA 55.1%, AZ 27.2%, NM 24.8%, TX 17.7%. Interpretation: CA is a hydro+geothermal+wind renewable leader; AZ's clean electricity is dominated by a single large nuclear plant plus hydro, not renewables; NM is a coal producer with fast-growing wind; TX is a large fossil (oil/gas/coal) economy just beginning wind. Similarity: all four are energy-producing states with large fossil shares. Differences: CA has the deepest renewable electricity base; AZ/NM are fossil exporters whose renewables are young; TX is the largest total consumer with the lowest renewable share but the steepest recent wind growth. Limitations/bias: shares mix primary and final energy; RETCB includes biomass/wood so the total-renewable share is a floor; the electricity frame ignores that some renewable generation is exported.

## Subtask 2: Part I.B: Develop a model characterizing how each state's energy profile evolved 1960-2009, and interpret the results fo

### Problem

Part I.B: Develop a model characterizing how each state's energy profile evolved 1960-2009, and interpret the results for the governors, focusing on cleaner/renewable usage and the similarities/differences among the states and their drivers (geography, industry, population, climate).

### Analysis

The expert (Exchange 1) rejected a smooth-trend characterization: each state's renewable profile is a low, roughly flat baseline punctuated by discrete level-shifts (dams, PURPA, wind/solar/geothermal plant openings, RPS) plus hydro weather noise. Assumptions therefore: (1) the renewable-electricity share follows baseline + level-shifts + noise, NOT a single extrapolatable trend; (2) the trend is fit only on the post-1990 window (the era of modern wind/solar/geothermal); (3) level-shift years are detected from the data as large positive year-over-year jumps; (4) total consumption grows roughly linearly. Method: fit the post-1990 slope of the renewable share per state, detect level-shift years, and decompose each state's path into a flat fossil-dominated baseline and a growing renewable-electricity component. This is sound because it matches the observed structure (step-ups, not drift) and avoids over-fitting a curve to lumpy data.

### Modeling Process

For state s let S_s,y = (HY+WY+SO+GE)_s,y / ESTCB_s,y be the renewable-electricity share. Fit slope_b = polyfit(year, S) over 1990-2009 (Exchange 1: post-1990 window). Detect level-shifts: years y where d/dy of each fuel > 0.15 x the fuel's mean (CA wind/solar/geo ~1989; NM wind 2004-2008; TX wind 2008-2009). Total consumption T_s,y grows with CAGR C_s = (T_2009/T_1960)^(1/49)-1 (CA 1.73%, AZ 3.40%, NM 1.46%, TX 1.93%/yr). The profile = flat fossil baseline T - renewables + rising renewable-electricity component S x electricity.

### Outcome Analysis

Evolution 1960-2009: all four grew total consumption (AZ fastest, 3.4%/yr, driven by population and a 1970s-80s energy boom). Renewable-electricity share trajectories: CA high and volatile (69% 2000, dipping to 55% 2009 as nuclear/hydro weather varied) but always the largest, anchored by the Colorado/State Water hydro system and Geysers geothermal plus new wind/solar; AZ high on hydro+one nuclear plant but flat-to-declining renewable share (27% 2009) as its fossil base grew; NM stepped up sharply with wind (5.3% 2000 -> 24.8% 2009) while remaining coal-heavy; TX started near zero renewable electricity (1.3% 2000) and stepped up fast with wind (17.7% 2009) off a huge fossil base. Post-1990 renewable-share slope (CA -0.05, AZ -0.22, NM +0.18, TX +0.06 pp/yr) shows the lumpy, non-smooth behavior Exchange 1 warned about — a smooth trend would misread CA as declining and TX as flat. Similarities: all are energy producers with large fossil (oil/gas/coal) shares and a flat low renewable baseline through the 1980s. Differences and drivers: geography/industry — CA (diverse, hydro+geo+wind, large population), AZ (hot climate, hydro+nuclear, booming population), NM (coal+gas producer, emerging wind), TX (oil/gas/coal giant, newest wind). Climate drives hydro (CA/AZ weather-sensitive) and the appeal of solar (AZ/NM/TX). Population/industry drive demand growth (AZ/TX). Limitations/bias: level-shift detection is threshold-based; hydro weather noise makes CA's share look volatile; the post-1990 window excludes the early-hydro era.

## Subtask 3: Part I.C: Determine which of the four states had the 'best' profile for use of cleaner, renewable energy in 2009, and ex

### Problem

Part I.C: Determine which of the four states had the 'best' profile for use of cleaner, renewable energy in 2009, and explain the criteria and the choice.

### Analysis

Criteria must reflect the compact's stated aim (increased use of cleaner, RENEWABLE sources), so the ranking is led by the renewable-electricity share (the frame where renewable adoption is decided), with the total-renewable share of consumption as a secondary check and nuclear (clean but not renewable) reported separately so it cannot masquerade as renewable. Assumption: 'best' = largest current share of genuine renewable electricity, not largest absolute tonnage (that would reward the biggest state, TX, for reasons unrelated to renewable intensity). Method: rank states by renewable-electricity share in 2009, tie-break by total-renewable share, and inspect the mix (which renewables) to confirm the leader is broad-based rather than a single source.

### Modeling Process

Score_s = (HY+WY+SO+GE)_s,2009 / ESTCB_s,2009. Rank descending. Secondary: RETCB_s,2009 / TETCB_s,2009. Mix check: number of distinct renewables > trivial threshold. CA: 55.1% (hydro 30.7, geo 14.4, wind 6.4, solar 3.5); AZ: 27.2% (hydro 25.0, solar 1.9); NM: 24.8% (wind 20.4); TX: 17.7% (wind 16.6).

### Outcome Analysis

California has the best 2009 profile for cleaner/renewable use: the highest renewable-electricity share (55.1% of electricity) AND the highest total-renewable share of consumption (8.9%), and the broadest mix (hydro, geothermal, wind, solar all material). Arizona is second on renewable-electricity (27.2%) but only because of hydro plus a single large nuclear plant — its renewable (non-nuclear) base is thin and flat, so it is not the best on the compact's renewable criterion. New Mexico is third (24.8%, now wind-led and the fastest riser) and Texas fourth (17.7%) despite the largest absolute renewable build-out, because its enormous fossil base keeps its share low. Choice and rationale: CA, by the renewable-intensity criteria the compact cares about, with AZ/NM/TX distinguished by a single dominant source (nuclear/hydro, wind, wind) rather than a broad renewable portfolio. Limitation: if 'clean energy' were meant to include nuclear, AZ would rise; the criterion choice is explicit and defensible for a renewable-focused compact.

## Subtask 4: Part I.D: Predict each state's energy profile (as defined in I.A) for 2025 and 2050 in the absence of any policy changes

### Problem

Part I.D: Predict each state's energy profile (as defined in I.A) for 2025 and 2050 in the absence of any policy changes.

### Analysis

Three expert exchanges shape this. (Exchange 1) Do not extrapolate a smooth trend: model the renewable profile as baseline + level-shifts + hydro weather noise, fit post-1990, and report a range. (Exchange 2) The binding ceiling on renewable share is SUPPLY (new plants built), not demand; demand grows slowly and is non-binding, and intermittent wind/solar must be derated (not counted at full value) with a curtailment ceiling. (Exchange 3) Report bands graded by width (usable <=~10pp, marginal <=20pp, useless >20-25pp) and pair each number with its driver. Assumptions: (1) total consumption grows near-linearly; (2) the renewable-electricity share rises at a modest supply-limited step rate (the no-policy baseline holds RPS build-out at 2009 level and lets only continued cost-driven wind/solar and firm hydro/geothermal creep it up); (3) a firm-capacity/curtailment ceiling caps the share; (4) the total-renewable share tracks the renewable-electricity share via each state's 2009 ratio.

### Modeling Process

Parameter table (calibrated inputs): demand growth g = 0.8%/yr central, [0.5, 1.2] range, source: EIA Annual Energy Outlook 2011 / Short-Term Energy Outlook reference case (US energy & electricity demand growth 2010-2030), https://doi.org/10.2172/1019039. Renewable supply-limited step rate r_s (pp renewable-electricity/yr): CA 0.35, AZ 0.30, NM 0.35, TX 0.30, derived from the post-2009 EIA wind+solar build-out (national wind+solar generation grew ~8-12%/yr through 2020) derated to an in-state no-policy share, source: EIA Short-Term Energy Outlook, https://www.eia.gov/todayinenergy/detail.php?id=46531 and the EIA 2009-2020 wind/solar growth record. Intermittency derate wind 0.85, solar 0.80; firm-capacity/curtailment ceiling 75% (band high 80%), source: expert Exchange 2 (empirical judgment). Hydro-weather noise band +/-3pp (2025), +/-6pp asymmetric-up (2050), source: expert Exchange 1. Band-width threshold usable<=10pp, marginal<=20pp, useless>20-25pp, source: expert Exchange 3. Forecast: T_s,y = T_s,2009 x (1+g)^(y-2009); renewable-electricity share S_s,y = min(S_s,2009 + r_s (y-2009), 75%); total-renewable share = k_s x S_s,y with k_s = (total-renew 2009 share)/(renew-elec 2009 share); renewable energy = total-renewable share x T_s,y.

### Outcome Analysis

No-policy predictions (total consumption in TBtu; total-renewable share of consumption; renewable energy in TBtu): CA 2025 9094, 9.81%, 892; 2050 11099, 11.22%, 1245. AZ 2025 1652, 8.37%, 138; 2050 2016, 10.34%, 208. NM 2025 761, 6.52%, 50; 2050 929, 8.39%, 78. TX 2025 12834, 4.01%, 515; 2050 15663, 5.35%, 838. All four grow total consumption; all four raise their renewable share, but modestly, because with no new policy the RPS build-out is not continued and only cost-driven wind/solar and firm hydro/geothermal creep in. Bands: renewable-electricity share 2050 CA 66.5-75.5%, AZ 36.5-45.5%, NM 36.2-45.2%, TX 27.0-36.0%; total-renewable-share 2050 band widths 1.5-2.4pp, all graded 'usable' under the Exchange-3 threshold, so these baselines can anchor a target. Interpretation for the governors: without policy, CA stays the renewable leader but barely improves; AZ/NM/TX improve slowly; the gap persists because each state's fossil base is large and the binding constraint is how fast new plants are built, not how much power is wanted. Limitations/bias: the no-policy baseline deliberately understates what continued RPS would achieve (that is the compact's job, Part II); supply-limited step rates are empirical and could be faster with cheaper wind/solar; the curtailment ceiling is a simplification of firm-capacity limits.

## Subtask 5: Part II.A: Using the comparison, the 'best' criteria, and the no-policy predictions, set renewable-energy usage targets 

### Problem

Part II.A: Using the comparison, the 'best' criteria, and the no-policy predictions, set renewable-energy usage targets for 2025 and 2050 as goals for the new four-state energy compact.

### Analysis

Targets must sit ABOVE the no-policy baseline (otherwise policy does nothing) and must be framed as ranges/floors, not points, per Exchange 3 (a point goal is useless; a floor/range paired with its driver is usable). The policy lift is the compact's added contribution on top of the baseline. Assumptions: (1) a fixed policy lift of +4pp (2025) and +10pp (2050) on the total-renewable share, calibrated to CA SB100 directionality (100% clean electricity by 2045) and the TX/NM RPS build-out; (2) hard floors so the laggards are not left behind (2025 floor 10%, 2050 floor 15%); (3) each state also names its renewable-electricity goal consistent with its 2009 mix. Method: target_s,y = max(no-policy_baseline_s,y + lift_y, floor_y), stated as [target-1.5, target+2.0].

### Modeling Process

Lift = {2025: +4pp, 2050: +10pp} on the total-renewable share (policy-driven, above the no-policy baseline of Part I.D). Floors: 2025 >= 10%, 2050 >= 15%. target_s,y = max(baseline_s,y + lift_y, floor_y); range = [target-1.5, target+2.0]; target renewable energy = target% x T_s,y. Directionality anchors: CA SB100 (100% clean electricity by 2045), Texas 1999 RPS, and the observed post-2009 wind/solar growth (EIA).

### Outcome Analysis

Compact targets (total-renewable share of consumption, with range): 2025 — CA 13.8% [12.3,15.8], AZ 12.4% [10.9,14.4], NM 10.5% [9.0,12.5], TX 10.0% [8.5,12.0] (combined 11.6%, 2824 TBtu). 2050 — CA 21.2% [19.7,23.2], AZ 20.3% [18.8,22.3], NM 18.4% [16.9,20.4], TX 15.4% [13.9,17.4] (combined ~18%, 5341 TBtu). In renewable-electricity terms the 2050 goal is roughly CA ~70%, AZ ~40%, NM ~40%, TX ~30% of in-state electricity from renewables. These are deliberately a step above the no-policy baseline (CA 11.2%->21.2%, TX 5.4%->15.4%), so the compact's policies must add ~10pp by 2050 — the measurable contribution of the agreement. Ranges (not points) satisfy the Exchange-3 decision threshold, and each target is paired with its driver (build rate / RPS / CA SB100). Limitation: the lift is a policy choice, not a physical necessity; if funding or transmission lags, the upper ends are not guaranteed.

## Subtask 6: Part II.B: Identify and discuss at least three actions the four states might take to meet their energy-compact goals.

### Problem

Part II.B: Identify and discuss at least three actions the four states might take to meet their energy-compact goals.

### Analysis

The model says the binding constraint is SUPPLY — how fast new renewable plants (plus transmission and storage for firmness) can be built (Exchange 2) — and that growth is lumpy and event-driven (Exchange 1). The actions therefore target the build-out and the firmness/curtailment limits, not demand. Each action is tied to the mechanism that the model identified as binding.

### Modeling Process

Action -> mechanism it relaxes in the model: (1) Joint transmission & siting: raise the inter-state transmission ceiling that currently caps how much wind/solar can be delivered (relaxes the Exchange-2 firm-capacity/curtailment ceiling). (2) Harmonized RPS + shared procurement: set a common renewable-portfolio standard and a four-state procurement pool to smooth the lumpy level-shifts (Exchange 1) into a steady build rate. (3) Storage/backup & firm-renewable investment: co-invest in battery storage and firm geothermal/hydro to count wind/solar closer to full value (raises the effective supply ceiling, Exchange-2 derate). (4) Shared permitting & interconnection queue: cut time-to-build so the step rate r_s rises (directly increases the baseline used in Part I.D).

### Outcome Analysis

Discussion: (1) Joint transmission and siting is the single highest-leverage action because the model's ceiling is supply/delivery, not demand — without added interstate lines the wind in NM/TX and the solar in AZ cannot reach load, and surplus is curtailed or exported rather than counted in-state. (2) A harmonized renewable portfolio standard plus a shared procurement pool converts the lumpy, event-driven history (Exchange 1) into a predictable build rate, letting the states commit to the Part II.A ranges with confidence and avoiding the all-or-nothing plant-opening risk. (3) Storage/backup and firm-renewable (geothermal, run-of-river hydro) investment directly raises the effective value of intermittent wind/solar (Exchange 2's derate), so each MW counts more toward the target. (4) A shared permitting/interconnection queue shortens time-to-build, raising the step rate that drives the whole forecast. Together these raise the supply-limited ceiling faster than any single state could, which is precisely the value the compact adds over the no-policy baseline. Limitation: transmission and storage are capital- and politically intensive; benefits accrue on 10-20 year timescales, so near-term (2025) targets rely more on wind/solar cost declines than on these infrastructures.

## Subtask 7: Part III: Prepare a one-page memo to the four Governors summarizing the 2009 state profiles, the no-policy predictions, 

### Problem

Part III: Prepare a one-page memo to the four Governors summarizing the 2009 state profiles, the no-policy predictions, and the recommended compact goals.

### Analysis

The memo condenses Parts I-III for a non-technical audience: one sentence per state's 2009 character, the no-policy trajectory, and the recommended 2025/2050 goals with the top actions. It states the key assumptions (supply is the binding constraint; growth is lumpy; targets are ranges) and is kept to a single page.

### Modeling Process

Memo content is drawn directly from the computed results: 2009 profiles (Part I.A), no-policy 2025/2050 forecasts (Part I.D), and compact targets (Part II.A). No new computation.

### Outcome Analysis

MEMO TO: Governors of CA, AZ, NM, TX — BORDER RENEWABLE ENERGY COMPACT. RE: State energy profiles (2009), no-policy outlook, and recommended compact goals. WHERE WE STAND (2009): All four states are major energy producers dominated by fossil fuels, but their renewable positions differ sharply. CA is the clear renewable leader — 55% of its electricity already came from renewables (hydro, geothermal, wind, solar) and it had the cleanest overall mix. AZ's electricity is clean but mostly from one big nuclear plant and hydro, with little true renewable. NM is a coal producer with rapidly growing wind. TX is the largest energy consumer with the lowest renewable share (18% of electricity) but the steepest recent wind growth. WITHOUT NEW POLICY: If no compact policies are adopted, each state still grows total energy use and still adds some wind/solar, but only slowly — by 2050 the renewable share of total consumption would reach roughly CA 11%, AZ 10%, NM 8%, TX 5%. The gap between the states persists because the real limit is how fast new renewable plants and the lines to carry them can be built, not how much power is wanted. RECOMMENDED GOALS: Set binding four-state targets, stated as ranges: by 2025, at least 10-14% of each state's total energy from renewables (combined ~12%); by 2050, 15-21% (combined ~18%), with CA leading (~21%). These sit ~10 percentage points above the no-policy path by 2050 — the measurable value of the compact. TOP ACTIONS: (1) Build shared interstate transmission so NM/TX wind and AZ solar can reach all four states; (2) adopt a common renewable portfolio standard with a shared procurement pool to steady the build; (3) co-invest in storage and firm geothermal/hydro so wind and solar count at full value; (4) run a shared permitting queue to speed construction. RECOMMENDATION: Adopt the 2025 and 2050 targets above and fund the transmission and storage actions first, since they remove the binding constraint the model identifies.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
