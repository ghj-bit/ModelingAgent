# Solution

## Subtask 1: Part I.A — Using the supplied data, create an energy profile for each of the four border states (CA, AZ, NM, TX) as of 2

### Problem

Part I.A — Using the supplied data, create an energy profile for each of the four border states (CA, AZ, NM, TX) as of 2009: how much energy each consumes and produces, how much is renewable, and the mix of fuel/sector that defines each state.

### Analysis

Data (ProblemCData.xlsx, sheet 'seseds') is long-format: (MSN, StateCode, Year, Data), 105,744 rows = 4 states x 583 MSN codes x 50 years (1960-2009). Cleaning: no nulls, no duplicate (MSN,State,Year) keys, all Data values numeric; 22 MSN codes defined in 'msncodes' are absent from the data (noted, none material to renewables). A profile is built from the dataset's own aggregate codes: total energy consumption TETCB, total production TEPRB, renewable consumption RETCB (verified to equal exactly the sum of hydro HYTCB + wind WYTCB + solar SOTCB + geothermal GETCB + biomass BMTCB in 2009), nuclear NUETB, population TPOPP, and the five renewable components. A profile is a vector of 2009 levels plus each state's renewable share of consumption and of production. This is descriptive, not predictive, so no extrapolation enters here.

### Modeling Process

For each state s: renewable share of consumption rshare_s = RETCB_s / TETCB_s; share of production pshare_s = RETCB_s / TEPRB_s; per-capita consumption epc_s = TETCB_s / TPOPP_s (population in thousands). Component split comp_s(k) = component_k,s / RETCB_s for k in {hydro, wind, solar, geothermal, biomass}. All values read directly from the 2009 row of the dataset (unit: Billion Btu).

### Outcome Analysis

2009 profiles (Billion Btu): CA: pop 36.9M, consumes 8.01M, produces 2.61M (net importer), renewable 712.7k = 8.9% of consumption (38.2% hydro, 31.5% biomass, 17.9% geothermal, 8.0% wind, 4.4% solar), nuclear 4.2% of consumption. AZ: pop 6.6M, consumes 1.45M, produces 0.57M (importer), renewable 103.5k = 7.1% (60.6% hydro, 34.2% biomass, 4.6% solar), nuclear 22.1% — the most nuclear-intensive of the four (Palo Verde). NM: pop 2.0M, consumes 0.67M, produces 2.41M (large net exporter of fossil), renewable 35.6k = 5.3% (48.5% biomass, 42.4% wind, 7.4% hydro), no nuclear. TX: pop 24.8M, consumes 11.3M, produces 11.9M (net exporter), renewable 356.6k = 3.2% (54.8% wind, 41.6% biomass, 2.8% hydro), nuclear 3.8%. The four are distinct archetypes: CA a large diversified-consumer with the biggest and most balanced renewable base; AZ small, hydro- and nuclear-anchored; NM a small fossil-exporter pivoting to wind; TX a giant fossil producer/consumer whose renewables are almost entirely wind. Limitations: 'renewable' here is the dataset's definition (hydro+wind+solar+geothermal+biomass); per-capita and per-dollar intensity (TETPB, TETGR) are available but not the primary axis.

## Subtask 2: Part I.B — Develop a model characterizing how each state's energy profile evolved 1960-2009, interpreted for the governo

### Problem

Part I.B — Develop a model characterizing how each state's energy profile evolved 1960-2009, interpreted for the governors, identifying similarities and differences and their plausible drivers (geography, industry, population, climate).

### Analysis

A single smooth trend over all 50 years is structurally invalid here (see the model-structure assumption below). The model therefore (1) uses recency weighting and (2) tracks the renewable *level* and its five components, because the share is a ratio whose numerator, not its near-flat denominator, does the work. Evolution is summarized as a piecewise narrative (level + share by decade) rather than one fitted curve, and interpreted against each state's geography/industry. Similarity: all four states show total consumption flattening after ~2000 (efficiency + slow growth) while renewable levels rise. Differences: the *source* of each state's renewables differs, driven by geography (hydro in CA/AZ, wind in NM/TX, geothermal+solar in the Southwest, biomass/agriculture in CA/TX/AZ) and industry (NM/TX fossil-exporters, CA consumer-driven).

### Modeling Process

share_s(t) = RETCB_s(t)/TETCB_s(t). The 1960-2009 path is summarized at 1960/1980/2009 with growth factor g_s = share_s(2009)/share_s(1960). The evolution is piecewise, not a single fit: each component's 2000-2009 realized growth (hydro, wind, solar, geothermal, biomass separately) is reported, and the dominant 2000-2009 driver per state is identified. Recency weights w_t = lambda^(2009-t), lambda=0.85, are used wherever a rate is estimated, so late-decade step changes (not 1960-1979 history) drive the characterization. This is the same weighting carried into the Part I.D forecast.

### Outcome Analysis

Renewable share of consumption, %: CA 1960=7.8 -> 1980=9.0 -> 2009=8.9 (growth 1.14x, roughly flat, hydro-dominated). AZ 12.8 -> 15.9 -> 7.1 (growth 0.56x — the share actually FELL as fossil and nuclear rose). NM 2.2 -> 1.3 -> 5.3 (growth 2.38x, driven by a wind step in 2005-2009). TX 1.1 -> 0.7 -> 3.2 (growth 2.80x, the fastest riser, driven by the Texas wind build-out). Similarity: every state's total consumption is near-flat 2000-2009 (CA +0.2%, AZ +9.1%, NM -1.0%, TX -6.3%), so the rising renewable share in NM/TX and flat-to-falling share in CA/AZ are numerator stories, not denominator stories. Differences and drivers: CA's renewables are a mature, balanced mix (hydro+geothermal+biomass) that has not grown much in share because its fossil and nuclear base is large; AZ's profile is dominated by hydro and a big nuclear block; NM and TX are the two states where wind became the leading renewable in the 2000s. Geography (rivers -> hydro in CA/AZ; plains -> wind in NM/TX; sun -> solar in all; magma/geology -> geothermal in CA), industry (fossil export in NM/TX; agribusiness biomass in CA/AZ/TX), and population (CA/TX large, AZ/NM small) explain the split. Bias note: EIA consumption data count renewable electricity in Btu at the electric-power sector; the small early wind/solar values are genuinely near-zero, not censoring, but the fast 2000s growth partly reflects new reporting coverage as capacity scaled.

## Subtask 3: Part I.C — Determine which state had the 'best' renewable-energy profile in 2009, and explain the criteria and the choic

### Problem

Part I.C — Determine which state had the 'best' renewable-energy profile in 2009, and explain the criteria and the choice.

### Analysis

'Best' is judged on a renewable-specific criterion, not on how 'clean' the whole energy mix is (nuclear inflates AZ's non-fossil share but is not renewable). Three criteria: (1) renewable share of consumption (the headline indicator of a state's actual reliance on cleaner energy); (2) renewable share of production (self-sufficiency); (3) diversification of the renewable mix (robustness — a single-source state is more exposed to drought or a one-resource downturn). The choice is CA.

### Modeling Process

Rank states by renewable share of consumption rshare, then tie-break/justify with pshare and the number of renewable components contributing >=5% of that state's renewables (diversification count). rshare: CA 8.9 > AZ 7.1 > NM 5.3 > TX 3.2. pshare: CA 27.4 > AZ 18.1 > TX 3.0 > NM 1.5. Diversified components (>=5%): CA=5 (all), AZ=3, NM=2, TX=3.

### Outcome Analysis

California has the best renewable profile in 2009: it leads both on renewable share of consumption (8.9%) and on renewable share of production (27.4%), and it is the only state with a genuinely diversified five-source renewable mix (hydro 38.2%, biomass 31.5%, geothermal 17.9%, wind 8.0%, solar 4.4%). AZ is second (7.1% consumption) but its mix is hydro+biomass and its stronger claim is nuclear, which is not renewable. NM and TX trail on share but are the states with the fastest recent momentum (wind). Criteria caveat: if 'best' were instead defined as fastest-growing, NM/TX would lead; the choice depends on the criterion (stock vs. momentum), and the criterion stated here — the best *current* renewable profile for a compact to build on — is CA. Limitation: share is relative to each state's own total, so a large state like TX can have a big absolute renewable base (356.6k Btu, second only to CA's 712.7k) yet a low share because its fossil base is enormous.

## Subtask 4: Part I.D — In the absence of any policy change, predict each state's energy profile (renewable consumption level and sha

### Problem

Part I.D — In the absence of any policy change, predict each state's energy profile (renewable consumption level and share) for 2025 and 2050, based on the historical evolution and the state-profile differences established above.

### Analysis

Structure assumption (validated with the domain expert): the renewable history is lumpy/regime-shifted, not a smooth trend, so a 50-year smooth fit is rejected. Because total energy use is near-flat, the renewable share is driven by the renewable *numerator* (new generation), not the denominator; therefore the model projects the renewable LEVEL component-by-component and holds the 2009 total-consumption denominator constant. Each component is grown at a recency-weighted rate clipped to a plausible band, then capped at a resource ceiling, so a one-off step (e.g. TX wind +3793% 2000-2009) is not extrapolated to an impossible level. A +/-30% band is reported because, in the policy setting, an over-forecast (unreachable target) is the more damaging error.

### Modeling Process

For component k in state s with 2009 value R0_s,k: rate r_s,k = clip(recency-weighted slope of log(R_s,k) over 2000-2009, 0, 12%); ceiling cap_s,k = c_k * TETCB_s(2009) with c_k in {hydro 0.10, wind 0.20, solar 0.10, geothermal 0.03, biomass 0.10} (resource ceilings as a share of total consumption). Forecast level R_s(t) = sum_k min(R0_s,k * (1+r_s,k)^(t-2009), cap_s,k). Share s_s(t) = R_s(t)/TETCB_s(2009). Band: [0.70*R_s(t), 1.30*R_s(t)]. Recency weights lambda^(2009-t), lambda=0.85, window=10 (sensitivity: lambda in {0.80,0.90,0.95}, window in {6,8,15} — shares move by only ~1-2 percentage points, so the result is robust). Central case uses the conservative rate clip (declining hydro held flat) to avoid over-claiming. Parameter table (empirical inputs): resource-ceiling shares c_k: hydro=0.10, wind=0.20, solar=0.10, geothermal=0.03, biomass=0.10, interval [0.05,0.30], source: expert exchanges 1-3 (regime-shifted history, numerator-driven share, ±20-30% decision band) plus the dataset's own 2000-2009 component growth rates (e.g. TX wind, CA hydro) used to clip the rates.

### Outcome Analysis

Absent policy change (conservative central case; renewable level in Billion Btu and share of 2009-held-constant total consumption): CA: 2025 ~946k Btu = 11.8% (band 8.3-15.4%), 2050 ~1760k Btu = 22.0% (band 15.4-28.6%). AZ: 2025 ~220k = 15.1% (10.6-19.7%), 2050 ~267k = 18.3% (12.8-23.8%). NM: 2025 ~165k = 24.6% (17.2-32.0%), 2050 ~215k = 32.0% (22.4-41.6%). TX: 2025 ~1820k = 16.1% (11.3-21.0%), 2050 ~3620k = 32.0% (22.4-41.6%). Interpretation: even doing nothing, every state's renewable share roughly doubles by 2050 (wind in TX/NM, biomass+solar in CA/AZ). NM and TX reach a similar ~32% share by 2050 but from very different bases (NM already higher in 2009, TX far larger in absolute Btu). CA's absolute renewable base is the largest and keeps growing but its share rises least because its total is huge. Key caveats/biases: (1) the held-flat denominator is the single biggest assumption — if total energy falls further (efficiency), shares would be higher; if it rises (population/economic growth), shares lower; this is exactly the second-order effect the expert flagged. (2) Component rates are clipped to a ceiling, so 2050 values are floors, not expectations; the true value lies in or above the reported band. (3) 'Absence of policy change' is optimistic about construction (it assumes current build-out continues) and pessimistic about cost (it ignores falling solar/wind prices that have historically accelerated adoption), so the central case should be read as a planning floor, not a forecast of most likely reality.

## Subtask 5: Part II.A — Based on the four-state comparison, the 'best-profile' criteria, and the no-policy forecasts, set renewable-

### Problem

Part II.A — Based on the four-state comparison, the 'best-profile' criteria, and the no-policy forecasts, set renewable-energy usage targets for 2025 and 2050 as goals for the new four-state compact.

### Analysis

A 'realistic' compact goal should sit above the no-policy (do-nothing) floor — otherwise it sets no new obligation — but inside the +30% defensible band, so each state can credibly reach it with a normal build-out program. Targets are set as a state-specific 2025/2050 renewable share of total consumption, anchored to each state's no-policy forecast and lifted by a uniform policy margin that pulls the laggards (NM, TX) toward the leader's trajectory and the leader (CA) toward its own resource ceiling. The margin is chosen so no target exceeds the +30% band of the no-policy forecast (the threshold at which a target stops being defensible).

### Modeling Process

Target_s(y) = no-policy share_s(y) + margin_s, where margin_s = a uniform uplift applied so that (a) the 2025 target is at most the +30% band of the 2025 no-policy share, and (b) the 2050 target is at most the +30% band of the 2050 no-policy share, and (c) every state's 2050 target reaches at least a common floor so the compact is a genuine shared commitment. Rounding to whole percent. No-policy 2025 shares: CA 11.8, AZ 15.1, NM 24.6, TX 16.1; no-policy 2050 shares: CA 22.0, AZ 18.3, NM 32.0, TX 32.0.

### Outcome Analysis

Recommended four-state compact goals (renewable share of total consumption): 2025 — CA 15%, AZ 18%, NM 28%, TX 18%; 2050 — CA 27%, AZ 24%, NM 35%, TX 35%. (2025 targets = no-policy +~3-4pp, each inside the +30% band; 2050 targets = no-policy +~4-5pp, NM and TX meeting a common ~35% floor that matches their natural wind end-games while CA pushes its already-best profile higher.) Rationale: CA (best 2009 profile) leads in level and aims for the most ambitious absolute base; NM and TX use their wind momentum to hit a shared ~35% by 2050; AZ, small and hydro/nuclear-anchored, gets a realistic path to ~24%. All 2025/2050 targets are achievable by construction (within the +30% do-nothing band), and each is above the do-nothing floor, so every goal requires new build-out rather than drift. Sensitivity: if the denominator (total energy) falls more than assumed, all targets are easier to hit; if it rises, the +30% cushion absorbs moderate overruns.

## Subtask 6: Part II.B — Identify and discuss at least three actions the four states might take to meet the compact's renewable goals

### Problem

Part II.B — Identify and discuss at least three actions the four states might take to meet the compact's renewable goals.

### Analysis

Actions are chosen to attack the specific gap between the no-policy floor and the 2025/2050 targets, and to correct the structural weak points found in the profiles (single-source dependence in AZ/NM, small absolute bases, grid/interconnection friction between the states). They are supply- and institution-side, matching the numerator-driven mechanism: the share rises only when new renewable capacity is built and delivered.

### Modeling Process

Not a numeric model; a decision rule linking each action to a profile weakness identified in Part I. Action i is valid if it (a) raises the renewable numerator in at least two states, (b) is within the +30% build-out envelope that makes the targets achievable, and (c) addresses a driver (geography/industry/grid) identified in Part I.B.

### Outcome Analysis

Three actions: (1) Joint regional wind corridor and interconnection — NM and TX are the wind states and share the same plains geology; a four-state compact can fund shared transmission and coordinate siting so each state's wind (TX 195k Btu, NM 15k Btu in 2009) is built out and moved where needed, directly lifting the two laggards' numerators. (2) Cross-state renewable procurement and RPS harmonization — CA already leads on RPS and a diversified mix (8.9% in 2009); aligning the four states' renewable portfolio standards and creating a shared procurement market lets CA's purchasing power and AZ's hydro/nuclear reliability backstop the variable wind in NM/TX, smoothing supply and making the 2050 ~35% targets credible for everyone. (3) State-supported solar and storage build-out plus demand-side efficiency — solar is small but growing in every state (CA 4.4%, AZ 4.6% of renewables in 2009); because the share is a ratio, pairing new solar/wind with efficiency (which flattens the denominator and was already visible 2000-2009) is the cheapest way to close the gap, and storage addresses the intermittency that is the main practical obstacle to the wind-heavy NM/TX end-states. Together these raise the numerator (actions 1, 3) and manage the denominator and delivery (actions 2, 3), which is exactly what the numerator-driven share mechanism requires.

## Subtask 7: Part III — A one-page memo to the four Governors summarizing the 2009 state profiles, the no-policy-change predictions f

### Problem

Part III — A one-page memo to the four Governors summarizing the 2009 state profiles, the no-policy-change predictions for energy usage, and the recommended compact goals.

### Analysis

Synthesis deliverable: one page, decision-oriented, in plain language. It leads with the comparison the Governors need (who is where in 2009), states what happens if they do nothing (the floor), and closes with the specific numbers to adopt. It deliberately keeps the three expert-informed caveats visible but brief: the do-nothing case is a floor, the denominator (total energy use) is the key uncertainty, and targets were set inside the defensible +30% band so they are achievable.

### Modeling Process

No new computation; the memo is a faithful restatement, in one page, of the Part I.A profiles, the Part I.D no-policy forecasts (central case + ±30% band), and the Part II.A targets, with the Part II.B actions listed as the three means to reach them.

### Outcome Analysis

MEMO — To the Governors of CA, AZ, NM, TX; Re: Renewable-energy profiles and compact goals (2025/2050). WHERE WE ARE (2009): California is the leader — the largest renewable base (712.7 billion Btu) at 8.9% of consumption, with a diversified five-source mix (hydro, biomass, geothermal, wind, solar). Arizona is second at 7.1%, anchored by hydro and a big nuclear plant. New Mexico is at 5.3% and Texas at 3.2%, but both are rising fastest on wind. All four states stopped growing total energy use around 2000, so progress now comes from building more clean capacity, not from demand shrinking. IF WE DO NOTHING: renewable shares still roughly double by 2050 — CA to ~22%, AZ to ~18%, NM to ~32%, TX to ~32% — but only because the current build-out keeps going; this is a floor, not a plan, and the band is wide (about ±30% by 2025) because the 2000s were lumpy. WHAT THE COMPACT SHOULD COMMIT TO: 2025 renewable shares of CA 15%, AZ 18%, NM 28%, TX 18%; 2050 shares of CA 27%, AZ 24%, NM 35%, TX 35%. Every goal is above the do-nothing floor and inside the achievable band, so each requires real new build-out but is still reachable. HOW TO GET THERE: (1) build a shared four-state wind corridor and interconnection (NM+TX); (2) harmonize renewable procurement/RPS so CA's market and AZ's reliability backstop the variable wind; (3) fund solar plus storage and efficiency in all four states. The one number to watch is total energy use — if it keeps falling, every target gets easier; if it climbs, the cushion absorbs it. Recommendation: adopt the 2025/2050 targets above as the compact's binding renewable-energy goals.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
