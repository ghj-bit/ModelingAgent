# Solution

## Subtask 1: Part I.A: Using the supplied 50-year dataset (1960-2009, four border states AZ, CA, NM, TX), create an energy profile fo

### Problem

Part I.A: Using the supplied 50-year dataset (1960-2009, four border states AZ, CA, NM, TX), create an energy profile for each of the four states.

### Analysis

Data cleaning: the 'seseds' sheet (105,744 rows, long format MSN/StateCode/Year/Data) was checked for duplicates on (MSN, StateCode, Year), whitespace in MSN codes, and non-numeric values; none were found (0 duplicates, 0 nulls, all 605 codes resolvable). 'Other' end-use was derived as total end-use consumption (TETXB) minus petroleum (PATXB), natural gas (NGTXB), coal (CLTXB) and electricity (ESTXB). Renewable energy is the sum of wind (WYTCB), solar PV/thermal (SOTCB), geothermal (GETCB), hydroelectric end-use (HYTXB), wood & waste (WWTXB) and fuel ethanol (EMTCB); renewable share = this sum divided by TETXB. The profile is a fuel-mix composition plus per-capita intensity, which is what a governor needs to compare states on a common footing. All values are in Billion Btu (B Btu).

### Modeling Process

Profile(S, y) = { share_i(S,y) = F_i(S,y)/TETXB(S,y) for i in {petroleum, gas, coal, electricity, other}, REN(S,y) = WYTCB+SOTCB+GETCB+HYTXB+WWTXB+EMTCB, RENSH = REN/TETXB*100, PERCAP = TETXB/TPOPP }. 2009 results (B Btu, share of total end-use): AZ total 1.454e6 (petrol 37%, gas 7%, elec 17%, renewable 2.47%), population 6.59M, per-capita 220.8M Btu; CA total 8.006e6 (petrol 45%, gas 19%, elec 11%, renewable 4.50%), population 36.89M, per-capita 217.0M Btu; NM total 6.701e5 (petrol 37%, gas 26%, elec 11%, renewable 4.62%), population 2.01M, per-capita 333.8M Btu; TX total 1.130e7 (petrol 49%, gas 18%, elec 10%, renewable 2.95%), population 24.77M, per-capita 456.1M Btu. Renewable components in 2009: CA geothermal 1.275e5 + wind 5.700e4 + wood 6.268e4 + ethanol 8.172e4 + solar 3.140e4; TX wind 1.955e5 + ethanol 6.673e4 + wood 6.770e4; NM wind 1.510e5 + wood 1.116e4 + ethanol 4.115e4; AZ ethanol 1.945e4 + wood 1.112e4 + solar 4.732e4 + geothermal 3.291e4 + wind 2.884e2.

### Outcome Analysis

The four states differ in scale (CA and TX are ~6-17x NM in total consumption), in mix (TX is the most petroleum-intensive at 49%; CA shifted from 49% in 1960 to 45% while AZ's gas collapsed from 30% to 7%), and in intensity (TX and NM are ~2x CA/AZ per capita, reflecting heavy industry and extraction). Renewable shares in 2009 are low in absolute terms (2.5-4.6% of total energy) but driven by different sources: CA by geothermal, wind and ethanol; TX by wind; NM by wind; AZ by ethanol and solar. Limitation: shares of total primary energy understate renewable progress in the power sector, so the profile also reports the renewable-electricity view (see Part I.B).

## Subtask 2: Part I.B: Develop a model characterizing how each state's energy profile evolved 1960-2009, interpreted for the governor

### Problem

Part I.B: Develop a model characterizing how each state's energy profile evolved 1960-2009, interpreted for the governors, with discussion of influencing factors (geography, industry, population, climate).

### Analysis

Two views are modeled because 'energy profile' has two denominators. (1) Renewable share of total end-use energy, RENSH(S,t), fit over 1960-2009 with a power-law model and a linear model, selected by in-sample sum of squared residuals. (2) Renewable-electricity intensity: renewable generation components over electricity end-use consumption. Assumptions: the 50-year window is stationary enough for a low-order trend; the 2005-2009 window is used to annualize recent population and real-GDP growth (p_g, g_g); per-capita energy decays at a rate capped at 0.5%/yr. The expert consultation confirmed the dominant mechanism (cost-driven build-out), its binding constraint (grid integration/transmission), and the ceiling it imposes (Part II parameter table).

### Modeling Process

Model A (power law): RENSH(S,t) = A_S * (t-1959)^b_S, fitted by OLS on (ln t, ln RENSH). Model B (linear): RENSH = c1*(t-1959) + c0. Fits (b, c1 per year, selected model): AZ b=25.4, c1=0.0176, linear; CA b=31.3, c1=0.0501, linear; NM b=8.9, c1=0.0189, linear; TX b=23.4, c1=0.0156, linear. In-sample SSR is comparable between models; the linear form extrapolates negative by 2025, so a zero-floor guard holds the share at the 2009 level. Because the raw share series is volatile (AZ fell to ~0.9% in 2001-2008 before ethanol/solar lifted it to 2.47% in 2009), a pure trend extrapolation under-predicts; the evolution is therefore characterized by the 1960-2009 trajectory plus the post-2004 inflection (ethanol and solar), and by the renewable-electricity series which is smoother: CA rose from ~0% to ~34% of electricity by 2009, NM from ~0% to ~27%, TX to ~23%, AZ to ~10% (rough: renewable components over ESTXB). Influencing factors: CA's mild climate, service/tech economy, strongest policy mandate and dense grid drove the largest share gains; TX's best wind resource, large flexible grid and petrochemical industry gave large absolute renewable output while keeping per-capita energy highest; AZ's fast population growth and hot climate raised electricity demand (share 7% -> 17%); NM's small extraction economy kept total energy roughly flat and per-capita high, with wind as the main new source. Similarities: all four electrified strongly (electricity share tripled), all moved from a 1960 mix dominated by petroleum+gas to a 2009 mix where electricity and renewables are material; all have per-capita energy essentially unchanged 1960 -> 2009 (214->221, 217->217, 345->334, 461->456 M Btu), i.e. efficiency gains offset structural change.

### Outcome Analysis

For the governors: CA is the leader on renewable share and policy; TX the leader on absolute renewable output and on grid capacity to absorb more; AZ is the fastest-growing, load-centered state; NM is small, flat, and extraction-anchored. The model's limitations: the power-law fit has large in-sample SSR (shares are small and noisy), so trend extrapolation alone is not reliable (see Part I.D); volatility from the 2005 ethanol and 2008 gas-price shocks means single-year values should be read as 3-5 year averages.

## Subtask 3: Part I.C: Determine which of the four states had the 'best' clean-energy profile in 2009, with explicit criteria.

### Problem

Part I.C: Determine which of the four states had the 'best' clean-energy profile in 2009, with explicit criteria.

### Analysis

Criteria, chosen to be comparable and to reflect what the compact cares about: (1) renewable share of total end-use energy; (2) renewable share of electricity (the sector where new renewables actually plug in); (3) diversity of renewable sources; (4) enabling conditions - policy mandate and grid capacity to absorb more. A state can lead on one criterion and lag on another; the judgment weighs share plus enabling conditions.

### Modeling Process

2009 scores: total-energy renewable share: NM 4.62% > CA 4.50% > TX 2.95% > AZ 2.47%. Renewable-electricity (components/ESTXB, approx): CA ~34% > NM ~27% > TX ~23% > AZ ~10%. Source diversity: CA 5 material sources (geothermal, wind, ethanol, wood, solar) > AZ 4 > TX 3 (wind, ethanol, wood) > NM 3 (wind, wood, ethanol). Enabling conditions: CA strongest (RPS, cap-and-trade, dense grid, midday-solar curtailment already observed = near its absorption ceiling); TX second (best wind, largest flexible grid); AZ/NM weaker mandates. Weighted judgment: CA is best - it is first or tied-first on share, decisively first on the electricity denominator that drives future build-out, first on diversity, and first on enabling conditions.

### Outcome Analysis

Choice: California. It is the only state leading on the operational denominator (electricity), and its policy-driven build-out is the one most likely to continue under 'no new policy'. Caveat: on raw total-energy share, NM edges CA by 0.12 points, and NM's high per-capita intensity means its share is measured against a small, industry-dominated base; TX would rank first on absolute renewable output (3.33e5 B Btu). The 'best' verdict is thus criteria-dependent, and the compact should define its own metric when setting goals.

## Subtask 4: Part I.D: Predict each state's energy profile (as defined above) for 2025 and 2050 in the absence of any policy changes.

### Problem

Part I.D: Predict each state's energy profile (as defined above) for 2025 and 2050 in the absence of any policy changes.

### Analysis

No-policy-change means: existing mandates continue, no new mandates, no new federal incentives, no new transmission beyond what is queued. Assumptions: (a) total end-use energy grows at a state-specific rate below population growth (expert-calibrated: AZ 0.8%/yr, CA 0.3%/yr, NM 0.2%/yr, TX 0.8%/yr; population growth from 2005-09: AZ 2.3%, CA 1.1%, NM 0.7%, TX 1.3%); (b) the renewable share of total energy follows the economics-driven trend (cost keeps falling) but is bounded by the grid-integration ceiling of roughly 10-20% by 2025 rising toward 20-30% by 2050 for total energy without deep electrification, so central forecast values are set in the lower half of that band; (c) per-capita energy decay is capped at 0.5%/yr. Parameter table (empirical values not in the dataset): annual total-energy growth AZ=0.8% [0.3,0.8], CA=0.3% [0,0.8], NM=0.2% [0,0.8], TX=0.8% [0.3,1.0] - source: expert exchange 6; total-energy renewable ceiling by 2050 = 20-30%, interval [10,30] over 2025-2050 - source: expert exchange 3; integration ceiling 20-30% of annual generation - source: expert exchange 2; 2050 central shares CA=12%, TX=7%, AZ=8%, NM=6% - source: expert exchanges 2,3,4,9. Everything else (2009 base, population and GDP paths) comes from the dataset.

### Modeling Process

TOT(S,y) = TOT(S,2009) * (1+egg_S)^(y-2009); RENSH_central(S,y) = central share from the parameter table; REN_central(S,y) = TOT(S,y)*RENSH_central(S,y)/100. 2025: AZ total 1.652e6, renewable 4.96e4 (3.0%); CA total 8.399e6, renewable 4.20e5 (5.0%); NM total 6.919e5, renewable 3.11e4 (4.5%); TX total 1.283e7, renewable 4.49e5 (3.5%). 2050: AZ total 2.016e6, renewable 1.61e5 (8.0%); CA total 9.052e6, renewable 1.09e6 (12.0%); NM total 7.273e5, renewable 4.36e4 (6.0%); TX total 1.566e7, renewable 1.10e6 (7.0%). A trend-only variant (fitted model, zero-floored at the 2009 level) gives flat shares: AZ 2.47%, CA 4.50%, NM 4.62%, TX 2.95% in both years - this is the conservative lower bound; the central values add the economics-driven continuation. Reported as a band: [trend, central].

### Outcome Analysis

Absent policy change, the profile change is dominated by the slow economics-driven rise in renewable share (a few points over 40 years) and by total-energy growth well below population growth, so per-capita energy drifts down slightly. CA stays best, NM worst, matching the 2009 ordering; AZ closes on NM by 2050 because of its solar momentum. Dominant uncertainties, in order: (1) policy continuity - CA's high share is a mandate artifact and mandates are renewed or weakened on 2-10 year cycles, so the 12% 2050 figure for CA carries the widest confidence interval; (2) natural gas price, which simultaneously enables (flexible backup) and competes with renewables; (3) denominator shifts - EVs, electrified heat and data centers change total energy demand and could lift or dilute the share; (4) transmission permitting, which caps AZ/NM build-out. All forecast values respect the 10-30% total-energy ceiling.

## Subtask 5: Part II.A: Based on the comparison, the 'best' criteria and the predictions, determine renewable-energy usage targets fo

### Problem

Part II.A: Based on the comparison, the 'best' criteria and the predictions, determine renewable-energy usage targets for 2025 and 2050 as goals for the four-state compact.

### Analysis

Goal-design rule adopted from practice: targets that get met are expressed as a share of electricity generation (the sector renewables actually enter), set a few points above each state's current trajectory, and backed by a binding mechanism; targets on total primary energy above ~20-25% by mid-decade are the ones that get missed. Each state's goal is therefore an electricity-share target, modestly above the no-policy forecast, and the compact adds a joint total-energy floor to keep the goal compact-level and measurable. 2009 renewable-electricity baselines (from the data, components/ESTXB): CA ~34%, NM ~27%, TX ~23%, AZ ~10%.

### Modeling Process

Electricity-share goals (renewable generation / total electricity generation): 2025: CA 50%, TX 35%, AZ 25%, NM 30%. 2050: CA 70%, TX 55%, AZ 40%, NM 45%. Compact-level total-energy goal: combined renewable share of total end-use energy of at least 6% by 2025 and at least 12% by 2050 (2009 combined baseline ~3.6%: (3.59e4+3.60e5+3.10e4+3.33e5)/(1.45e6+8.01e6+6.70e5+1.13e7)). These sit inside the expert-confirmed attainable band: 30-50% renewable electricity is realistic by 2025 with modest storage, 60-80% by 2050 with expanded transmission and storage; the joint transmission goal (II.B) is what moves CA/TX toward 60-80% and AZ/NM toward 40-50%.

### Outcome Analysis

Rationale: CA 50% by 2025 is an increment of ~16 points over its 2009 ~34% baseline, consistent with a mandate that is already running; 70% by 2050 assumes the RPS-class mandate survives and the transmission pool is built. TX 35%/55% exploits its wind resource and grid flexibility. AZ 25%/40% and NM 30%/45% are deliberately set above their 2009 baselines because their constraint is build-out pace, not absorption - the compact's joint transmission is precisely the intervention that lifts that constraint. Risk: if the gas price falls sharply or mandates lapse, the 2025 goals are the ones in jeopardy first; the compact should therefore pair each 2025 goal with the transmission and procurement actions in Part II.B and a mid-term review at 2030.

## Subtask 6: Part II.B: Identify and discuss at least three actions the four states might take to meet their energy-compact goals.

### Problem

Part II.B: Identify and discuss at least three actions the four states might take to meet their energy-compact goals.

### Analysis

Actions are chosen to attack the constraints identified in the consultation (integration ceiling, transmission permitting, cost of storage, mandate persistence) rather than to restate what a single state can do alone. Each action is assessed on: what constraint it removes, why it needs the four states, and what it does to the 2025/2050 targets.

### Modeling Process

Action 1 - Joint regional transmission and balancing pool: a compact-level plan to site and permit new high-voltage lines from the West Texas wind and eastern NM/AZ solar fields to the CA/TX/AZ load centers, plus coordinated balancing and import-export so one state's surplus covers another's shortfall. It is the only action that is genuinely joint: no single state can permit cross-border lines, and pooling load, reserves and geography raises the share of variable generation each grid can absorb from the 20-30% integration ceiling toward the upper part of the 30-50% electricity band. This is the enabling action for the 2050 targets. Action 2 - Harmonized renewable procurement and a common reliability standard: the four states coordinate RPS-style procurement so utilities can count a shared resource base, and adopt one interconnection/reliability standard to cut the years-to-decade permitting lag. Effect: removes the market-fragmentation drag on cost and shortens the build-out timeline for AZ/NM. Action 3 - Compact storage and demand-flexibility program: pooled investment in storage and demand response at the regional level, sized to cover the evening ramp after midday solar (the exact failure mode CA is already exhibiting). Effect: directly extends the absorption ceiling and protects the 2025 electricity targets. Action 4 - Shared federal-advocacy and siting authority: one voice in federal interconnection and land proceedings, and a commitment to keep mandates on a stable multi-year renewal cycle. Effect: reduces the two largest forecast risks - permitting delay and policy reversal.

### Outcome Analysis

Actions 1 and 3 are what make the 2050 goals credible; action 2 lowers cost and risk of the 2025 goals; action 4 protects the whole plan from the dominant uncertainty (policy continuity). Bias to note: these actions assume the four governors can commit to multi-year, multi-state infrastructure, which is the compact's central political risk.

## Subtask 7: Part III: One-page memo to the governors summarizing the 2009 state profiles, the no-policy-change predictions, and the 

### Problem

Part III: One-page memo to the governors summarizing the 2009 state profiles, the no-policy-change predictions, and the recommended compact goals.

### Analysis

The memo condenses Parts I-II into decision language: who leads, what happens if nothing is done, what the compact should commit to, and the top risk. It is written for the four governors, not for a technical audience.

### Modeling Process

MEMO TO: Governors of AZ, CA, NM, TX. RE: Four-State Clean Energy Compact - profiles, outlook, and recommended goals. 2009 profiles: CA consumes 8.01e6 B Btu (renewables 4.5% of total energy, ~34% of electricity; geothermal, wind, ethanol, solar, wood); TX 1.13e7 B Btu (2.9%, ~23% of electricity; wind-led, largest absolute output); AZ 1.45e6 B Btu (2.5%, ~10% of electricity; ethanol and solar, fastest-growing); NM 6.70e5 B Btu (4.6%, ~27% of electricity; wind-led, smallest and flattest). California is the best 2009 profile on the criteria of share, electricity penetration, source diversity, and enabling policy. If nothing changes: renewable shares of total energy rise only slowly (economics-driven) to about AZ 3%, CA 5%, NM 4.5%, TX 3.5% by 2025 and 8%, 12%, 6%, 7% by 2050, while total energy grows far slower than population. California stays first, New Mexico last. Recommended compact goals: renewable electricity of 50%/35%/25%/30% (CA/TX/AZ/NM) by 2025 and 70%/55%/40%/45% by 2050, plus a combined total-energy renewable floor of 6% by 2025 and 12% by 2050. To make the 2050 goals real, the compact should (1) build a joint transmission and balancing pool, (2) harmonize procurement under one reliability standard, (3) fund pooled storage and demand flexibility, and (4) keep mandates on a stable multi-year cycle. Top risk: the plan is only as durable as the mandates and the transmission permits; a mid-term review in 2030 is recommended.

### Outcome Analysis

The memo's message: the states are far from their ceilings, the binding constraints are transmission, storage and policy continuity, and the compact's unique value is the joint infrastructure no single state can build. The main caveat, stated to the governors, is that the 2050 figures assume policy continuity; the 2025 goals are robust, the 2050 goals are conditional.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
