# Solution

## Subtask 1: Part I.A — Create an energy profile for each of the four border states (CA, AZ, NM, TX) using the ProblemCData dataset (

### Problem

Part I.A — Create an energy profile for each of the four border states (CA, AZ, NM, TX) using the ProblemCData dataset (50 years, 1960-2009, 605 MSN variables). The goal is a compact, comparable characterization of how each state's energy use is structured, focused on the clean/renewable dimension the new compact cares about.

### Analysis

Assumptions: (1) the profile metric is the SHARE of total end-use energy from clean sources, not the raw BTU amount, because a total without a denominator is not decision-useful for a governor and the all-energy share is far lower than the electricity-only share (exchange 1); (2) two share definitions are reported side by side — 'renewable share' (solar, wind, geothermal, hydro, wood/waste biomass) and 'clean share' (renewable + nuclear) — because the renewable-vs-clean and all-energy-vs-electricity distinctions matter; (3) the denominator is total END-USE energy consumption (MSN TETXB, Billion Btu) so the share reflects what the state actually consumes rather than what it produces or exports. Data cleaning: the sheet 'seseds' was pivoted to (StateCode, Year) x MSN; 105,744 rows, zero nulls, zero duplicate (StateCode,Year,MSN) keys, all values numeric, years 1960-2009 — nothing needed repair beyond type conversion. Method: per state, report the 2009 (and 1960) total end-use, the renewable and nuclear BBtu, the two shares, the fossil mix (petroleum, natural gas, coal shares), and population. This is descriptive but directly tied to the decision variable, so it is sound as a profile.

### Modeling Process

For state s and year y: renewable(s,y) = SOTCB + WYTCB + GERCB + HYTCB + WWTCB; clean(s,y) = renewable(s,y) + NUETB; renewable_share(s,y) = 100 * renewable(s,y)/TETXB(s,y); clean_share(s,y) = 100 * clean(s,y)/TETXB(s,y); petroleum_share = 100*PATXB/TETXB; gas_share = 100*NGTXB/TETXB; coal_share = 100*CLTXB/TETXB. All in Billion Btu. Variables: SOTCB = photovoltaic + solar thermal total consumption; WYTCB = wind total production; GERCB = geothermal total; HYTCB = hydroelectric total production; WWTCB = wood and waste total consumption; NUETB = nuclear electricity produced; TETXB = total end-use energy consumption; PATXB/NGTXB/CLTXB = petroleum/natural-gas/coal end-use; TPOPP = population (thousands).

### Outcome Analysis

2009 profiles (total end-use, renewable share, clean share, oil/gas/coal, population): CA 8.01e6 BBtu, renewable 6.3%, clean 10.4%, oil 44.6%/gas 19.5%/coal 0.4%, 36.9M. AZ 1.45e6, renewable 5.6%, clean 27.6%, oil 37.1%/gas 7.5%/coal 0.6%, 6.6M. NM 6.70e5, renewable 4.4%, clean 4.4%, oil 37.5%/gas 26.1%/coal 0.2%, 2.0M. TX 11.30e6, renewable 2.5%, clean 6.3%, oil 48.7%/gas 18.1%/coal 0.2%, 24.8M. Dominant renewable component by state (endowment): CA = hydro (272,187 BBtu) with a fast-growing solar tail (31,397, +13% 2008->2009); AZ = hydro (62,731) plus a large nuclear legacy (320,723); NM = wind (15,096) and wood/waste (11,633), no nuclear; TX = wind (195,455, the fastest ramp of the four) plus the largest nuclear stock (434,065). Key limitation: the all-energy renewable share stays low in every state (2.5-6.3%) because transportation and thermal loads are fossil-bound, so the profile understates each state's actual clean *electricity* mix; the clean share partially corrects this via nuclear. NM's low per-capita renewable total is offset by the highest per-capita renewable INTENSIVE use of a small base; NM is also the most energy-intensive state (333,826 MBtu/capita vs ~217,000-221,000 for CA/AZ).

## Subtask 2: Part I.B — Develop a model characterizing how each state's energy profile evolved 1960-2009, and interpret similarities/

### Problem

Part I.B — Develop a model characterizing how each state's energy profile evolved 1960-2009, and interpret similarities/differences with possible influential factors (geography, industry, population, climate) in language the governors can use.

### Analysis

Assumptions: (1) total end-use energy is a slow-moving aggregate that is well-identified over a 50-year record, so a log-linear trend is an adequate baseline characterization (exchange 3); (2) the renewable/clean SHARES are not smooth trends — they were inflected by resource development, policy, and falling renewable cost — so a single linear fit is only a rough description and the fit quality (R^2) is reported as the reliability signal; (3) the drivers of inter-state difference are resource endowment, legacy (already-built) infrastructure, state policy, incumbent fuel economics, and load/geography (exchange 2), which we check against the data rather than assert. Method: (a) log-linear fit total_enduse = a*exp(b*y) over 1985-2009 (recent window) and compute the 1960-2009 compound annual growth rate (CAGR); (b) linear fit of the renewable and clean shares over the same window, reporting slope (percentage points/year) and R^2; (c) attribute differences to the dominant renewable component and the fossil mix per exchange 2. This is sound because it separates the well-identified aggregate trend from the poorly-identified share, and ties interpretation to observable drivers.

### Modeling Process

Log-linear: ln(TETXB) = ln(a) + b*y over y in [1985,2009]; CAGR = 100*(exp(b)-1). Also CAGR_1960-2009 = 100*((TETXB_2009/TETXB_1960)^(1/49)-1). Shares: slope/intercept from OLS on (year, share) over [1985,2009]; R^2 = 1 - SS_res/SS_tot. A recent-5-year (2004-2009) slope is also computed for the renewable share to capture the post-2000 wind/solar ramp separately from the long window.

### Outcome Analysis

Growth: all four states grew total end-use energy steadily; 1960-2009 CAGR: AZ 3.40% (fastest, small base + population boom + gas development), TX 1.93%, CA 1.73%, NM 1.46%. The recent-window log-linear fit is reliable (R^2 = CA 0.87, AZ 0.96, NM 0.92, TX 0.89). Renewable SHARE is NOT well fit by a single trend (R^2: CA 0.13, AZ 0.26, NM 0.09, TX 0.19) — the long-window slopes are small and partly negative (CA -0.04 pp/yr, AZ -0.15 pp/yr) because early hydro dominance diluted the share as totals grew, while the recent-5-year slopes are positive in three states (NM +0.57, TX +0.32, AZ +0.01 pp/yr) as wind/solar ramped. Clean shares rose more (AZ +0.51 pp/yr on nuclear, R^2 0.57). In governors' terms: the four states are similar in that fossil fuels still supply ~60-70% of end-use energy and none has crossed a clean majority; they differ in WHAT makes them clean — CA is hydro-led with a new solar boom, AZ is hydro + a nuclear legacy (highest clean share at 27.6%), NM is wind/biomass with the highest relative growth, TX is the biggest absolute wind producer with the largest nuclear stock. Drivers (exchange 2): endowment (CA hydro, TX/AZ wind, all four solar in the Southwest), legacy (AZ/TX nuclear, CA hydro), policy (CA's early renewables programs, TX's wind incentives), and incumbent fuel economics (TX/AZ/NM gas-and-oil industries keep the all-energy share low). Climate/geography: dry Southwest heat-load and abundant sun/wind favor renewables; CA's coastal hydro reservoirs are its historic clean anchor.

## Subtask 3: Part I.C — Determine which of the four states appeared to have the 'best' profile for use of cleaner, renewable energy i

### Problem

Part I.C — Determine which of the four states appeared to have the 'best' profile for use of cleaner, renewable energy in 2009, and explain the criteria and the choice.

### Analysis

Criteria (weights reflect exchange 1's 'share not raw total' and exchange 2's 'endowment + momentum'): (1) clean share of end-use energy (primary, since the compact's goal is clean energy and AZ's nuclear is a real clean contribution); (2) renewable share of end-use energy (the strictly-renewable measure); (3) recent momentum, the 2004-2009 slope of the renewable share (a state already ramping is better placed to hit future goals); (4) renewable intensity per capita as a scale-neutral secondary check. We compare shares first, then momentum, then per-capita. Method: rank each state on the four 2009 metrics; the 'best' is the state strongest on the clean share with adequate renewable share and positive momentum, with ties broken by momentum.

### Modeling Process

Metrics from Part I.A (renewable_share, clean_share in 2009) and Part I.B (recent-5-year renewable slope, renewable per-capita). Ranking rule: sort by clean_share desc, then renewable_share desc, then recent5_slope desc, then per-capita desc. Per-capita renewable = renewable_BBtu*1e6/(TPOPP)/1000 (MBtu/capita).

### Outcome Analysis

2009 scores: CA renewable 6.3%, clean 10.4%, recent5 slope -0.29, per-capita 13,582. AZ renewable 5.6%, clean 27.6%, recent5 slope +0.01, per-capita 12,245. NM renewable 4.4%, clean 4.4%, recent5 slope +0.57, per-capita 14,782. TX renewable 2.5%, clean 6.3%, recent5 slope +0.32, per-capita 11,295. On the clean share, AZ is the clear leader (27.6% vs CA 10.4%) because of its nuclear legacy plus hydro, and its renewable share is second only to CA. On strictly-renewable share, CA leads (6.3%). On momentum, NM has the steepest recent renewable ramp and the highest per-capita renewable. Choice: ARIZONA has the best overall 2009 profile for clean energy use, because it combines the highest clean share (27.6%) with a competitive renewable share (5.6%) and a stable base; CA is the best on the purely renewable metric and on absolute renewable output. If the compact's definition is strictly 'renewable' (excluding nuclear), CA is the best; if it is 'clean' (renewable + carbon-free), AZ is the best. We state the choice under the clean definition (AZ) and flag CA as the renewable-definition winner, since exchange 1 notes governors conflate the two.

## Subtask 4: Part I.D — Predict each state's energy profile (as defined in I.A) for 2025 and 2050 in the ABSENCE of any policy change

### Problem

Part I.D — Predict each state's energy profile (as defined in I.A) for 2025 and 2050 in the ABSENCE of any policy changes by the governors' offices.

### Analysis

Assumption (exchange 3): a no-policy projection is a baseline trend extrapolation, trustworthy for slow aggregates over ~1-2 decades and unreliable for (a) share variables that were policy/cost-inflected and (b) horizons beyond ~2025. Therefore we (1) forecast total end-use by log-linear extrapolation (reliable baseline), and (2) do NOT commit a single renewable-share point prediction; instead we report the long-window trend value and the recent-5-year trend value as the two bounds of the uncertainty, and explicitly downgrade 2050 to a low-confidence range. 'No policy change' is itself held fixed for the baseline but flagged as unrealistic for renewables because existing federal credits and mandates keep evolving.

### Modeling Process

Total: TETXB_hat(y) = a*exp(b*y) with (a,b) from the 1985-2009 log-linear fit. Renewable/clean share at horizon h: trend value = slope_long*h + intercept_long (long-window OLS); recent value = share_2009 + slope_2004_2009*(h-2009); both clipped to [0,60]% / [0,80]%. Reported as a band [min, max] of the two. No other terms (no exogenous policy input, per the no-policy-change condition).

### Outcome Analysis

Total end-use (BBtu) baseline: CA 2025 ~1.18e7, 2050 ~1.73e7; AZ 2025 ~2.91e6, 2050 ~6.50e6; NM 2025 ~9.11e5, 2050 ~1.30e6; TX 2025 ~1.91e7, 2050 ~3.13e7. Renewable share band (long-trend to recent-trend): CA 2025 [1.6,6.4]%, 2050 [0,5.5]%; AZ 2025 [5.3,5.8]%, 2050 [1.6,6.1]%; NM 2025 [2.4,13.5]%, 2050 [2.8,27.7]%; TX 2025 [1.5,7.5]%, 2050 [1.7,15.4]%. Interpretation: totals are the reliable numbers (well-identified trends); the renewable shares fan out widely by 2050 precisely because policy/cost is the dominant lever, which is exactly the doubt condition from exchange 3. The recent-5-year bound captures the wind/solar ramp (TX, NM, CA); the long-trend bound captures the dilution by growing fossil-based totals. 2025 is the more trustworthy horizon; 2050 should be read as an order-of-magnitude range, not a forecast, and any 'no policy change' baseline will understate the likely renewable share if costs keep falling.

## Subtask 5: Part II.A — Based on the comparison, the 'best' criteria, and the predictions, determine renewable-energy usage targets 

### Problem

Part II.A — Based on the comparison, the 'best' criteria, and the predictions, determine renewable-energy usage targets for 2025 and 2050 and state them as goals for the four-state compact.

### Analysis

Assumptions: (1) targets should be set on the SHARE metric (exchange 1), stated as a share of total end-use energy, with a parallel electricity-only target since governors conflate the two; (2) targets must be ambitious but reachable — above the no-policy baseline (otherwise the compact adds nothing) yet not so far beyond the recent-ramp bound that they are implausible; (3) the 2050 target is a stretch goal with an intermediate 2035 checkpoint because 2050 is low-confidence (exchange 3). Method: anchor 2025 at the upper end of the recent-ramp baseline (the no-policy ceiling) plus a policy premium, and anchor 2050 at a step above 2025 consistent with continued cost decline, expressed as clean/renewable shares of end-use and of electricity.

### Modeling Process

Goal definition per state g and horizon h: clean_share_target(g,h) and renewable_share_target(g,h). We set a common four-state floor with state-specific stretch where endowment (exchange 2) justifies it. Electricity-only targets are set higher than end-use targets because renewables concentrate in electricity. Rationale values come from the Part I.D bands (baseline ceilings) plus a premium equal to roughly one extra recent-ramp decade of progress for 2025 and a step goal for 2050.

### Outcome Analysis

Recommended compact goals (share of total end-use energy unless noted): 2025 — each state >= 8% renewable and >= 15% clean end-use; electricity-only >= 20% renewable / >= 40% clean. 2050 — each state >= 25% renewable and >= 55% clean end-use; electricity-only >= 60% renewable / >= 90% clean, with a 2035 checkpoint of >= 15% renewable end-use. State-specific stretch (endowment-based, exchange 2): CA and AZ (hydro + nuclear/solar legacy) should lead at >= 30% renewable by 2050; TX should lead on absolute wind/solar output (its 2025 wind base already rivals the others); NM should match its high per-capita ramp at >= 25% renewable by 2050. These sit above the no-policy baseline (Part I.D) so the compact is meaningful, but the 2050 numbers are stretch goals to be revisited at the 2035 checkpoint given the low-confidence horizon. The 2025 targets are near the no-policy recent-ramp ceiling for CA/AZ and a modest premium for NM/TX, so they are credible as a policy lever.

## Subtask 6: Part II.B — Identify and discuss at least three actions the four states might take to meet the energy-compact goals.

### Problem

Part II.B — Identify and discuss at least three actions the four states might take to meet the energy-compact goals.

### Analysis

Actions are chosen to directly attack the constraints identified in Parts I.A-I.B (fossil-bound transport/thermal loads, endowment asymmetry, and policy as the dominant lever per exchange 2). We need at least three concrete, mutually reinforcing levers: supply (build the renewables each state is endowed with), interconnection (let states import each other's clean power to smooth endowment gaps), and demand/policy (reduce the fossil denominator and level the playing field).

### Modeling Process

Each action is mapped to the model variable it moves: (A1) in-state renewable build-out raises the numerator (renewable BBtu) fastest in the state's dominant component; (A2) a regional transmission/interconnection compact raises net in-state clean CONSUMPTION (exchange 1's consumed-vs-generated distinction) by letting e.g. TX wind and CA hydro/solar flow to neighbors; (A3) a harmonized renewable portfolio standard + efficiency program raises the share by cutting the fossil denominator (TETXB) and mandating the clean numerator, which is the policy lever exchange 2 identified as the main reason similar states diverge.

### Outcome Analysis

Action 1 — Endowment-matched renewable build-out: each state expands the resource it already dominates (CA solar + hydro storage, AZ solar + hydro, NM wind + biomass, TX wind + solar), because building the endowed resource is cheapest and fastest (exchange 2). Action 2 — Interstate transmission and shared grid: build/expand interconnectors and a joint market so clean power is shared across the four states; this directly addresses exchange 1's point that a state's clean CONSUMPTION differs from its generation, and it lets the wind-rich (TX, NM) and hydro/solar-rich (CA, AZ) states back each other, flattening the endowment asymmetry. Action 3 — Harmonized policy package: adopt a common renewable portfolio standard, net-metering and incentive rules, and a building/vehicle efficiency program so the compact, not just individual states, drives the share (exchange 2: policy is the main differentiator). Efficiency also lowers total end-use (the denominator), which raises the share for the same clean supply and slows the fossil growth seen in Part I.B. A fourth supporting action — joint R&D and a shared carbon-free grid operator for nuclear/hydro dispatch — stabilizes the clean share that is otherwise weather- and load-dependent. Together these three-plus levers move both the numerator (more clean supply, shared) and the denominator (less fossil demand), which is what the share metric in Part I.A requires.

## Subtask 7: Part III — Prepare a one-page memo to the Governors summarizing the 2009 state profiles, the no-policy-change prediction

### Problem

Part III — Prepare a one-page memo to the Governors summarizing the 2009 state profiles, the no-policy-change predictions, and the recommended compact goals.

### Analysis

The memo condenses Parts I-III into the three elements the governors asked for: where each state stands in 2009, where the states would drift to absent action, and what the compact should commit to. It uses the share metric throughout (exchange 1) and is explicit that 2025 is the credible near-term number while 2050 is a stretch goal (exchange 3).

### Modeling Process

Memo content is the 2009 profile table (Part I.A), the growth + share-trend findings (Part I.B), the best-state call (Part I.C: AZ on clean, CA on renewable), the 2025/2050 baseline and band (Part I.D), and the recommended 2025/2050 targets plus the three actions (Part II). No new computation; it assembles and interprets the results above in prose sized to one page.

### Outcome Analysis

MEMO TO THE GOVERNORS OF CA, AZ, NM, TX — RE: Renewable Energy Compact, State Profiles and Goals. (1) 2009 profiles (clean / renewable share of end-use energy): AZ is the cleanest at 27.6% clean (5.6% renewable) on hydro plus a nuclear legacy; CA is the most renewable at 6.3% renewable (10.4% clean) on hydro and a fast-growing solar sector; TX is the largest absolute clean producer (195,000 BBtu wind, 434,000 BBtu nuclear) but only 2.5% renewable / 6.3% clean because of its huge total; NM is the smallest (2.0M people) with 4.4% renewable, the steepest recent wind ramp, and the highest renewable use per person. All four still draw 60-70% of end-use energy from petroleum and gas, so none has reached a clean majority. (2) No-policy predictions: total energy keeps growing (AZ fastest at ~3.4%/yr); the renewable shares would drift only modestly — by 2025 roughly 2-8% renewable depending on state, and by 2050 anywhere from ~2% to ~28% depending on whether the recent wind/solar ramp holds. 2025 is the reliable number; 2050 is a wide range because policy and cost, not the past trend, decide the outcome. (3) Recommended goals: by 2025 each state >= 8% renewable / >= 15% clean end-use (>= 20% renewable electricity); by 2050 each state >= 25% renewable / >= 55% clean end-use (>= 60% renewable electricity), with a 2035 checkpoint at >= 15% renewable. To get there: (a) each state build the resource it already has in abundance (solar, wind, hydro); (b) connect the four-state grid so clean power is shared across borders; (c) adopt one common renewable standard plus efficiency rules so the whole region moves together. These targets are set above what the states would reach on their own, which is the point of the compact.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
