# Modeling Blueprint Draft — "Moving North" (MCM 2020)

**Problem ID:** `2020_Moving_North`
**Document type:** Initial modeling plan draft (roadmap only)
**Status:** Planning / pre-solution. This document contains no solved results, no fitted parameters, no executed experiments, and no final conclusions. All numeric placeholders are symbolic and are intended to be *estimated during the later modeling stage*.

---

## 1. Problem Background and Restatement

### 1.1 Context

Global ocean temperatures are expected to shift the geographic ranges of marine species. When local water temperatures depart from a species' thermal tolerance and reproductive optimum, populations tend to migrate toward waters that remain suitable. The Maine-to-Canada northward migration of American lobster is given as a motivating example of this phenomenon and of the economic disruption it can cause to fisheries that depend on a stable local stock.

### 1.2 Our Client and Their Concern

The client is a consortium of Scottish North Atlantic fishery managers representing the interests of **small Scotland-based fishing companies**. These companies:

- historically operate out of current Scottish ports,
- often use **vessels without on-board refrigeration**, and
- therefore depend on short trip durations so that catch can be landed fresh within a marketable quality window.

The two focal species are **Scottish herring** and **Scottish mackerel**, both economically significant to the Scottish fishing industry. The core worry is that warming waters will push these stocks northward (and/or into deeper or otherwise displaced habitats) to the point that the *distance and transit time* from existing ports becomes incompatible with fresh-fish operations.

### 1.3 What the Problem Ultimately Asks

Stated in planning terms, the task will require a chain of connected sub-models:

1. **Temperature-to-habitat mapping** — where will suitable thermal habitat for herring and mackerel be located over a ~50-year horizon under plausible warming trajectories?
2. **Range-shift prediction** — where are the two populations *most likely* to be located across those years?
3. **Operational feasibility threshold** — at what point (in time) does stock displacement exceed the practical harvesting-and-delivery envelope of a small, non-refrigerated vessel operating from a current port, and how does that threshold depend on the *rate* of warming (best / worst / most-likely)?
4. **Business strategy assessment** — should small companies adapt, and if so, which combinations of relocation, vessel capability, and other operational changes are economically attractive?
5. **Jurisdictional complication** — how are the proposed strategies altered if part of the stock migrates into the territorial waters of another coastal state?
6. **Communication deliverable** — a lay-audience article for *Hook Line and Sinker* magazine.

### 1.4 Deliverables to Be Produced Later

- A ≤20-page technical solution (summary sheet + 1–2-page magazine article + solution, ≤24 pages total).
- A one-page summary sheet.
- A one- to two-page magazine article.
- Supporting figures, sensitivity tables, and (if applicable) code/data appendices referenced by the main report.

> **Note on data availability:** The run workspace currently exposes no bundled input dataset (`output/data`, `output/code`, `output/logs`, `output/results` are empty at plan time). Section 4 therefore specifies the *acquisition* plan for public / authoritative sources that the later modeling stage will need to assemble, document, and version.

---

## 2. Objectives and Subproblems

### 2.1 Primary Objective

To build a defensible, transparent modeling framework that (a) projects the future spatial distribution of Scottish herring and mackerel under ocean-warming scenarios, (b) translates that projection into the operational and economic viability of small Scottish fishing companies, and (c) evaluates and ranks adaptation strategies under realistic ecological, economic, and legal constraints.

### 2.2 Subproblems (Mapping to Problem Requirements)

| # | Subproblem | Requirement addressed | Intended output of later modeling |
|---|-----------|----------------------|-----------------------------------|
| S1 | Build a **thermal-habitat / species-distribution model** for herring and mackerel driven by sea surface and sub-surface temperature fields. | Req. 1 | Time-resolved maps of habitat suitability and most-likely stock location over ~50 years. |
| S2 | Define and calibrate a **warming-rate scenario set** (best / most-likely / worst case). | Req. 1–2 | A small family of temperature trajectories that bound the plausible future. |
| S3 | Define an **operational feasibility criterion** for a small non-refrigerated vessel (range, transit time, catch-freshness window, trip economics). | Req. 2 | A threshold function mapping stock displacement to "still practical / no longer practical." |
| S4 | Estimate **elapsed time until infeasibility** for each scenario. | Req. 2 | Scenario-indexed time windows (expressions, to be evaluated later). |
| S5 | Assess the **"change vs. don't change" decision**. | Req. 3 | A decision rule with stated justification tied to model outputs. |
| S6 | Model and compare **adaptation strategies** (relocation of assets; proportion of longer-endurance / refrigeration-capable vessels; port-of-landing changes; fleet pooling; mixed strategies). | Req. 3a | Strategy catalogue + economic comparison framework. |
| S7 | Analyze the effect of a **portion of the stock entering foreign territorial waters**. | Req. 4 | Constraint/penalty extension of the strategy model. |
| S8 | Draft the **magazine article** outlining seriousness and proposed solution. | Req. 5 | Plain-language narrative derived from the model's logic (not from results at this draft stage). |

### 2.3 Interdependency Structure

S1 and S2 are the *ecological core*. S3 converts ecological output into an *operational language* (time, distance, freshness, cost). S4–S6 are the *decision core* that consumes S1–S3. S7 modifies S3–S6 with legal/geopolitical constraints. S8 communicates the whole chain. This separation matters because it lets each block be validated independently and swapped (e.g., replace the species model without rebuilding the economic model).

---

## 3. Assumptions

Assumptions are grouped. For each group we state the assumption, the justification, and how it will be validated or stress-tested later. Assumptions should be tagged as **CORE** (structural, changes conclusions if violated) or **WORKING** (convenience, reversible).

### 3.1 Ecological / Species Assumptions

| ID | Assumption | Justification | Later validation approach | Type |
|----|-----------|---------------|---------------------------|------|
| A1 | Temperature (especially upper-thermal-range suitability) is the dominant driver of herring and mackerel distribution. | Problem statement frames the issue explicitly as temperature-driven migration. | Compare model-skill against observed historical range shifts; test whether adding salinity/depth/prey materially improves fit. | CORE |
| A2 | Each species has an identifiable thermal tolerance band and an optimum; habitat suitability can be expressed as a function of temperature. | Standard species-distribution / thermal-niche framing. | Literature parameterization + sensitivity sweep over tolerance bounds. | CORE |
| A3 | Populations track suitable habitat with some lag (not instantaneous). | Range shifts are known to lag environmental change. | Sensitivity to lag constant; compare with/without lag. | WORKING |
| A4 | Suitable habitat is essentially continuous at the scale of the analysis (fine-scale aggregation/ontogenetic detail may be ignored). | Keeps model tractable at basin scale. | Resolution sensitivity test. | WORKING |
| A5 | Projections assume stocks remain viable/present, i.e., we model *relocation*, not *collapse*. | Requirement asks for "locations," implying persistence. | Scenario where recruitment fails is a stated limitation, not modeled. | WORKING |
| A6 | Mackerel (a more pelagic, wide-ranging species) and herring (more site-faithful, with spawning-ground attachment) may need different mobility treatment. | Ecological realism; the two species behave differently. | Compare shared- vs. species-specific parameterization. | CORE |

### 3.2 Climate / Warming Assumptions

| ID | Assumption | Justification | Later validation approach | Type |
|----|-----------|---------------|---------------------------|------|
| A7 | Plausible futures can be bounded by a small scenario set (best, most-likely, worst) instead of an ensemble of full GCM runs. | Requirement 2 asks for exactly these three cases. | Ensure the bounding scenarios bracket an ensemble/CMIP-style spread; report sensitivity to scenario construction. | CORE |
| A8 | Warming is treated as a smoothly evolving trend over the horizon with optional stochastic variability. | Enables clean "elapsed-time" estimates. | Add interannual variability and re-check timing robustness. | WORKING |
| A9 | Background basin-scale temperature fields vary primarily in latitude and depth (with regional Scottish-shelf structure retained). | Simplification for spatial modeling. | Regional downscaling sensitivity. | WORKING |

### 3.3 Operational / Business Assumptions

| ID | Assumption | Justification | Later validation approach | Type |
|----|-----------|---------------|---------------------------|------|
| A10 | A "small company" is characterized by limited capital, current port base, and vessels without on-board refrigeration. | Glossary definition supplied by the problem. | Represent as a parameterized cost/capability profile rather than a single fixed entity. | CORE |
| A11 | Freshness/quality is bounded by a maximum time from catch to landing (a "freshness window"). | Proxy for absence of refrigeration. | Sensitivity over plausible window lengths. | CORE |
| A12 | Feasibility is governed by an effective operating radius = f(vessel speed, trip duration, turning/set time, weather margins, fuel). | Standard fishing-trip geometry. | Sensitivity over speed, range, and turnaround time. | CORE |
| A13 | Economic attractiveness is judged by a profit (or net-present-value) criterion comparing strategies over the horizon, accounting for capital cost of adaptation. | Standard business-decision framing; keeps strategies comparable. | Vary discount rate and capital constraints. | CORE |
| A14 | Markets/ports are broadly substitutable (fish can be landed and sold from a different Scottish port if the company relocates). | Enables relocation to be modeled as a viable strategy. | Test partial-substitutability variants. | WORKING |
| A15 | Fuel, labour, and fish-price trajectories can be represented as bounded ranges/scenarios rather than precise forecasts. | These are highly uncertain. | Sensitivity analysis over ranges. | WORKING |

### 3.4 Legal / Geopolitical Assumptions

| ID | Assumption | Justification | Later validation approach | Type |
|----|-----------|---------------|---------------------------|------|
| A16 | Territorial sea = 12 nautical miles from baseline (UNCLOS 1982 definition supplied in the glossary). | Explicitly given. | N/A — definitional. | CORE |
| A17 | Access to foreign territorial waters by Scottish vessels may be restricted or require licensing; a penalty/constraint is a reasonable abstraction. | Problem asks how a foreign-territory shift affects the proposal. | Model both "closed" and "licensed-access" variants. | CORE |
| A18 | EEZ / high-seas access regimes beyond the 12-nm band are treated as a secondary extension. | Keeps scope aligned with the requirement's explicit territorial-water focus. | Flag as future extension. | WORKING |

### 3.5 Modeling / Scope Assumptions

| ID | Assumption | Justification | Later validation approach | Type |
|----|-----------|---------------|---------------------------|------|
| A19 | A 50-year horizon is the planning window. | Requirement 1 specifies 50 years. | None needed; fixed by task. | CORE |
| A20 | Model outputs are comparative and directional (which strategy is better, roughly when), not precise point forecasts. | Marine projections carry wide uncertainty. | Present uncertainty bands, not point values. | CORE |

---

## 4. Data Processing Plan

### 4.1 Data to Be Acquired (no dataset is bundled at plan time)

The later modeling stage will need to assemble and document, at minimum:

| Data class | Purpose | Candidate sources (to be confirmed and cited) |
|-----------|---------|-----------------------------------------------|
| Historical sea surface temperature (SST) fields | Calibrate/validate temperature-habitat relationship | NOAA OISST / ERSST, HadISST, Copernicus (CMEMS) reanalysis |
| Sub-surface / depth-resolved temperature | Herring and mackerel occupy different depths; depth matters | CMEMS reanalysis, Argo-derived products |
| Climate projection temperature fields | Build 50-year best/likely/worst scenarios | CMIP-class projections / IPCC scenario-consistent products, downscaled for the NE Atlantic |
| Bathymetry / shelf geometry | Define habitat mask and realistic movement corridors | GEBCO / regional bathymetry |
| Species occurrence / catch records | Fit and validate the thermal-habitat model | ICES assessment & survey data, national fisheries statistics (e.g., Scottish/UK fleet data), OBIS/GBIF occurrences |
| Thermal tolerance / biological parameters | Constrain the species niche | Peer-reviewed literature (per species and life stage) |
| Port locations and landing statistics | Define "current locations" and market endpoints | Scottish port authority / national statistics |
| Vessel capability & cost data | Parameterize the operational model | Fleet statistics, vessel-class specifications, fuel/cost references |
| Fishery economics (prices, subsidies, capital costs) | Build the economic comparison | Market price series, industry reports |
| Maritime boundaries | Test territorial-water scenarios | Public maritime-boundary datasets (UNCLOS-informed) |

**Rule for the later stage:** every external input must be recorded with source, access date, spatial/temporal resolution, and units; uncertain inputs must enter as ranges, not point values.

### 4.2 Preprocessing (Planned Steps)

1. **Harmonization** — unify coordinate reference systems, time indexing, units (°C, depth in m, distances in nm/km), and file formats.
2. **Grid reconciliation** — regrid heterogeneous sources (SST, projections, bathymetry, occurrence) onto a common spatial grid appropriate to the shelf scale.
3. **Temporal aggregation** — construct annual/seasonal fields from monthly data; define seasonal spawning/relevant windows per species.
4. **Missing-data handling** — interpolate coastal/shelf gaps; flag (do not silently fill) areas with weak coverage.
5. **Quality screening** — remove or down-weight erroneous occurrence points, duplicate records, and coordinates on land.
6. **Bias/trend check** — detect and document any discontinuities across SST product versions and projection baselines; align scenario baselines to a common reference period.
7. **Reproducibility** — all steps scripted, versioned, and re-runnable from raw inputs.

### 4.3 Feature Construction (Planned)

Feature families to be derived for later modeling:

- **Thermal features:** mean SST, seasonal amplitude, degree-days above/below thresholds, sub-surface temperature at species-relevant depths, rate of temperature change (°C/decade), thermal-anomaly fields.
- **Spatial features:** latitude, longitude, distance-from-current-port, depth, distance-to-coast, shelf-front proximity.
- **Habitat-suitability index (HSI):** constructed later as a temperature-and-depth response function per species (functional form chosen in Section 5).
- **Scenario features:** warming scenario label, year index, cumulative warming to date.
- **Operational features:** effective operating radius, achievable round-trip transit time, catch-quality margin relative to the freshness window.
- **Economic features:** expected gross value per trip, fuel and labour cost per trip, capital cost per adaptation option.

### 4.4 Data Usage Strategy

- **Calibration / training:** historical occurrence + historical temperature → fit the thermal-habitat relationship.
- **Validation hold-out:** reserve a subset of years/regions (temporal and spatial hold-out, not random only) to test predictive skill.
- **Projection input:** scenario temperature fields → project HSI and likely stock location forward.
- **Operational linkage:** projected stock location + vessel parameters + port locations → feasibility and economics.
- **Transparency:** maintain a data dictionary and a provenance log; all derived features must be traceable to raw sources.

### 4.5 Known Data Risks (to be managed later)

- Coarse resolution of shelf-scale ocean data near Scottish waters.
- Sparse or biased species records (fishing effort is not uniform in space).
- Mismatch between historical catch locations (effort-driven) and true abundance.
- Projection spread across climate models (reason scenarios, and report spread).
- Time-lag between observed biological response and observed temperature (confounds calibration).

---

## 5. Candidate Model Framework

The framework is intentionally modular: **(A) Temperature/Scenario layer → (B) Habitat & Movement layer → (C) Operational layer → (D) Economic/Decision layer → (E) Legal-constraint layer.** Each layer is independently validatable and swappable.

### 5.1 Layer A — Warming-Rate / Scenario Models

**Purpose:** generate the family of future temperature trajectories that drives everything downstream.

**Candidate approaches:**
- **Deterministic linear/exponential trend models** for the most-likely case, with bracketing slopes for best/worst.
- **Satellite/reanalysis trend extrapolation** calibrated to historical NE Atlantic warming.
- **Scenario-consistent trajectories** anchored to published emissions pathways (bounded, not exhaustive).
- Optional **stochastic overlay** (AR/random-walk variability) to represent interannual noise.

**Key variables:** year `t`; SST field `T(lat, lon, depth, t)`; warming rate `r` (°C/decade); scenario index `s ∈ {best, likely, worst}`.

**Advantages:** simple, transparent, directly answers Requirement 2's "how rapidly." **Limitations:** coarse; ignores regional feedbacks; sensitive to chosen baselines.

### 5.2 Layer B — Species Thermal-Habitat and Movement Models

**Candidate model families (to be compared, not all fitted at once):**

1. **Thermal-niche response / HSI models**
   - Define HSI = f(T, depth, season) using tolerance curves (Gaussian / piecewise / beta-shaped) or threshold (thermal-limit) functions.
   - Map HSI over space and time; "most likely location" = HSI-weighted centroid or highest-suitability region.

2. **Species Distribution Models (SDMs)**
   - Statistical: logistic regression / GLM / GAM relating occurrence to temperature and covariates.
   - Machine-learning: MaxEnt / Random Forest / boosted trees for non-linear niche edges.
   - Output: presence-probability maps → converted to likely stock center-of-mass over time.

3. **Bioclimate-envelope / shifting-envelope models**
   - Translate the current realized thermal envelope northward as the isotherm migrates; track the displaced envelope.

4. **Advection–diffusion / reaction–diffusion (movement) models**
   - PDE form (or its discretized/cellular-automaton analogue) where population density `N(x,y,t)` evolves under:
     - a diffusion term (spreading),
     - an advection term toward favorable habitat (gradient of suitability),
     - a reaction term (local growth/recruitment),
     - a carrying-capacity field set by HSI.
   - Allows explicit modeling of **lag** and **front speed**.

5. **Agent-/individual-based alternatives (fallback)** for representing schooling/migratory behavior if data support it.

**Key variables:** HSI(x,y,t); population density N(x,y,t); stock centroid C(t) = (x̄(t), ȳ(t)); mobility/lag parameters; per-species thermal parameters.

**Model-comparison intent:** use 1–3 for tractable "most-likely-location" maps and 4 (or a simplified gradient-following variant) when *timing/lag* is central. The framework should report where the two disagree.

**Advantages:** interpretable, data-light at the niche level, and directly tied to "where will they be." **Limitations:** assumes temperature dominance; niche transferability across time is uncertain; center-of-mass hides range fragmentation.

### 5.3 Layer C — Operational Feasibility Model

**Purpose:** turn "the fish moved X nm north" into "can a small, non-refrigerated vessel still land fresh fish?"

**Candidate approaches:**
- **Geometric reachability model:** effective operating radius `R = f(vessel speed, max trip time, fishing/set time, weather/fuel margin)`; feasible iff stock location lies within `R` of a landing port.
- **Time-budget model:** transit-in + fishing + transit-out ≤ freshness window (directly encodes the no-refrigeration constraint).
- **Cost-per-trip model:** fuel ∝ distance; crew-time; ice/quota handling; compare against expected revenue.
- **Fleet-mix model:** if a fraction of the fleet becomes longer-endurance/refrigerated, aggregate feasible range and capacity shift accordingly.

**Key variables:** operating radius R; round-trip time; freshness window W; displacement D(t) of stock from port; feasible-set indicator; trips per season; cost per trip; catch value per trip.

**Advantages:** simple and auditable; connects ecology to business in one step. **Limitations:** idealized geometry (ignores weather days, quota, market timing) unless extended.

### 5.4 Layer D — Economic / Decision Model

**Purpose:** decide whether to change, and rank strategies.

**Candidate approaches:**
- **Cost–benefit / NPV model:** compare status-quo vs. each strategy over the horizon, discounting future cash flows; include one-off capital costs (new vessel, refrigeration, relocation) and recurring costs.
- **Break-even analysis:** the year(s)/warming level at which status quo profit crosses zero, per scenario.
- **Multi-criteria decision analysis (MCDA):** score strategies on profitability, risk, capital requirement, operational disruption, regulatory exposure — for cases where a single monetary metric is too narrow for "economically attractive."
- **Optimization:** choose the *proportion* of a fleet to upgrade / split of assets across ports to maximize expected NPV subject to capital constraint (LP/MILP formulation).

**Strategy catalogue (candidates to be modeled, per Requirement 3a):**
1. Relocate some/all assets to a port closer to the projected stock center.
2. Upgrade a proportion of vessels to longer-endurance / refrigeration-capable (relaxes the freshness window).
3. Change landing ports only (keep home port, land nearer the fish).
4. Fleet pooling / joint ventures to share upgraded capacity.
5. Diversify target species or shift effort seasonally.
6. Hybrid: partial relocation + partial vessel upgrade.

**Key variables:** strategy index; capital outlay; operating cost per trip; expected catch and price; discount rate; horizon; NPV / profit.

**Advantages:** standard, comparable, and directly answers "should they change / how." **Limitations:** inherently sensitive to price/cost/discount assumptions → must be paired with strong sensitivity analysis.

### 5.5 Layer E — Legal / Territorial-Water Constraint

**Purpose:** address Requirement 4 — the effect of a proportion `p` of the stock moving into another state's 12-nm territorial sea.

**Candidate approaches:**
- **Constraint modification:** if feasible fishing area ⊂ foreign territorial waters, either exclude it (hard constraint) or apply an access/penalty cost (soft constraint).
- **Scenario grid:** sweep the fraction of stock in foreign waters, `p ∈ [0,1]`, and the access regime (closed / licensed / open) to see how the optimal strategy changes.
- **Risk-adjusted decision model:** treat access uncertainty as a probability-weighted penalty in Layer D.

**Key variables:** proportion in foreign waters `p`; access regime; access cost/fee; resulting effective feasible stock; strategy robustness.

**Advantages:** simple, modular add-on. **Limitations:** regime details are political and uncertain → present as scenarios, not predictions.

### 5.6 Integrated Framework Summary

```
[A] Warming scenarios ─► [B] Habitat & movement ─► stock location C(t), D(t)
                                                        │
                                                        ▼
                                      [C] Operational feasibility (R, W, time, cost)
                                                        │
                                                        ▼
                     [D] Economic/decision model (NPV / MCDA / optimization)
                                                        ▲
                                                        │
                     [E] Territorial-water constraint (p, access regime) ─┘
```

---

## 6. Implementation Roadmap

### 6.1 Required Modules

| Module | Responsibility | Depends on |
|--------|---------------|-----------|
| M1 Data ingestion & harmonization | Download/import, unit/CRS normalization, provenance logging | — |
| M2 Scenario generator | Produce best/likely/worst temperature trajectories | M1 |
| M3 Habitat/suitability engine | Compute HSI fields per species per year | M1, M2 |
| M4 Movement/location estimator | Stock centroid and range over time (incl. lag) | M3 |
| M5 Operational feasibility | Radius/time/freshness threshold; infeasibility detection | M4 |
| M6 Economic engine | NPV/profit per strategy; break-even; ranking | M5 |
| M7 Territorial-water module | Access constraints/penalties; `p`-sweep | M5, M6 |
| M8 Visualization & reporting | Maps, time-series, scenario ribbons, strategy comparison | M4–M7 |
| M9 Sensitivity & validation harness | Automated sweeps, hold-out scoring, uncertainty bands | all |

### 6.2 Workflow Sequence (Later Execution Order)

1. **Acquire & document data** (M1) — produce data dictionary + provenance log.
2. **Build & calibrate temperature scenarios** (M2) — define best/likely/worst with explicit rationale.
3. **Fit/parameterize habitat models** (M3) — per species, temperature+ (optionally depth, season).
4. **Validate habitat models** on held-out years/regions before projection.
5. **Project stock location** forward 50 years (M4) — output centroid time-series + uncertainty bands.
6. **Define vessel/port parameter profiles** for "small company" archetypes (M5).
7. **Compute infeasibility timing** per scenario (M5) — best/likely/worst elapsed times.
8. **Assess change-vs-no-change** and enumerate strategies (M6).
9. **Compare strategies** economically (M6), with MCDA as a cross-check.
10. **Layer in territorial-water scenarios** (M7) and re-rank strategies.
11. **Run full sensitivity/uncertainty analysis** (M9).
12. **Produce figures and draft technical report + magazine article** (M8).

### 6.3 Algorithmic / Computational Notes (Planning Level, No Code)

- Prefer vectorized array operations over spatial grids for the habitat layer; the movement layer may need iterative time-stepping.
- Keep scenario and sensitivity runs as parameterized configurations so the whole pipeline can be re-run cheaply.
- Separate "expensive" steps (data regridding, model fitting) from "cheap" steps (plotting, re-ranking) to keep iteration fast.
- Enforce reproducibility: fixed seeds for any stochastic component; deterministic data hashes recorded.

### 6.4 Staffing / Task Split (Logical, Not Literal)

- **Ecological track:** M1–M3 (data + habitat modeling).
- **Movement track:** M4 (location/timing).
- **Operations/economics track:** M5–M7.
- **Integration & communication track:** M8–M9 + the magazine article.

---

## 7. Validation Strategy

### 7.1 Validation of the Ecological Layer

- **Temporal hold-out:** calibrate on earlier decades, test predicted range shifts in later observed decades.
- **Spatial hold-out:** withhold a region/stock and test transferability.
- **Benchmark comparison:** check that modeled present-day habitat matches known herring/mackerel distributions.
- **Cross-model agreement:** compare SDM vs. envelope vs. movement-model projections; investigate disagreements.
- **Skill metrics (to be selected later):** e.g., AUC/TSS for presence models; centroid displacement error; correlation of predicted vs. observed shift direction.

### 7.2 Validation of the Operational Layer

- **Face validity:** confirm that current (present-day) scenarios are classified as *feasible* — the model should not declare today infeasible.
- **Threshold consistency:** verify the freshness/radius threshold behaves monotonically with distance and speed.
- **Historical plausibility:** check the criterion against known operating ranges of similar small vessels.

### 7.3 Validation of the Economic Layer

- **Break-even sanity:** no-change strategy should be attractive under low-warming/short-horizon cases and unattractive under high-warming cases.
- **Ranking stability:** ensure strategy rankings do not flip under minor parameter perturbations (or, if they do, report the flip points).
- **External plausibility:** cross-check cost/capital magnitudes against industry references.

### 7.4 Sensitivity Analysis (Planned)

Sweep, at minimum:
- warming rate (best/likely/worst and intermediate);
- thermal-tolerance bounds per species;
- movement lag / mobility;
- freshness window W and vessel speed/range;
- capital cost of adaptation and discount rate;
- fish price and fuel cost;
- fraction of stock in foreign territorial waters `p`, and access regime.

Report outputs as **ranges and ranked robustness**, not single numbers. Identify which assumptions are *decision-critical* (i.e., change the recommended strategy if varied).

### 7.5 Uncertainty Communication

- Present scenario bands on all location-vs-time curves.
- Distinguish **structural uncertainty** (model-family disagreement) from **parametric uncertainty** (input ranges).
- State explicitly which conclusions are robust across scenarios and which are conditional.

---

## 8. Expected Result Interpretation

*(What the later outputs will mean — not the outputs themselves.)*

- **Location maps/trajectories** will be interpreted as *most-likely stock centroids with uncertainty bands*, reflecting where the suitable thermal habitat is expected to reside, not as precise fishing-ground guarantees.
- **Elapsed-time estimates** will be interpreted comparatively: the best case is the most optimistic warming rate yielding the longest viable window; the worst case the shortest; the most-likely a central estimate — each reported with its sensitivity range.
- **Change-vs-no-change decision** will be read off the economic layer: if status-quo profit remains positive across scenarios for the horizon, "no change" may be justified; otherwise adaptation is indicated. The justification must explicitly reference the assumptions it depends on.
- **Strategy comparisons** will be reported as ranked options with their capital requirements and break-even conditions, so a resource-limited company can choose based on its own constraint.
- **Territorial-water results** will be interpreted as scenario-conditional: how the recommended strategy shifts as `p` and access regime vary.
- **Magazine article** will translate the mechanism (fish follow temperature; too far = too slow = not fresh = not profitable) and the adaptation logic into non-technical language, without overstating precision.

---

## 9. Limitations and Improvements

### 9.1 Anticipated Limitations

1. **Temperature-dominance simplification** — ignores prey availability, oxygen, acidification, fishing pressure, and ecological interactions.
2. **Scenario coarseness** — three scenarios cannot capture the full future distribution; "rate of change" is modeled as a small family of trends.
3. **Center-of-mass abstraction** — actual populations may fragment or shift along multiple fronts; a single centroid can mislead.
4. **Operational idealization** — weather days, quotas, market timing, and seasonality are simplified.
5. **Economic parameter uncertainty** — prices, fuel, capital costs, and discount rates are highly uncertain.
6. **Legal simplification** — territorial-water treatments abstract complex licensing/political realities; EEZ/high-seas regimes are secondary.
7. **Single-stock framing** — herring and mackerel may interact or share fleet capacity; interactions are not initially modeled.
8. **Data quality** — sparse/biased species records and coarse shelf-scale temperature products limit calibrational fidelity.

### 9.2 Planned Improvements / Extensions

- Replace the coarse scenario family with an ensemble spread for a richer uncertainty picture.
- Add depth-resolved and seasonal habitat modeling; incorporate spawning-ground fidelity for herring.
- Couple multi-species / fleet-capacity interactions.
- Introduce explicit EEZ/high-seas and bilateral-access modeling alongside territorial waters.
- Extend the economic model with stochastic prices/costs and risk preferences (e.g., expected shortfall).
- Validate against independent case studies (e.g., the Maine-lobster analogue) as a qualitative cross-check.
- Strengthen reproducibility: public dataset snapshots, documented parameter tables, and a re-runnable pipeline.

### 9.3 Open Questions to Resolve During Modeling

- Which species-model family best balances interpretability and predictive skill at this scale?
- How should "too far away" be defined — a single distance threshold, or a distance-plus-time-plus-cost composite?
- How should the three scenarios be constructed so they genuinely bound the plausible future?
- What proportion of the fleet upgrading triggers a qualitatively different optimal strategy?
- How sensitive is the recommended strategy to the territorial-water fraction `p`?

---

### Appendix — Planning Conventions

- Placeholder notation (e.g., `R`, `W`, `D(t)`, `p`, `C(t)`) is symbolic and will be specified only during the modeling stage.
- All assumptions are tagged CORE / WORKING to prioritize sensitivity testing.
- No numbers in this document are results; they are structural placeholders.
