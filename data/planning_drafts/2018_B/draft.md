# Modeling Blueprint Draft — MM-Bench 2018_B

**Problem ID:** `2018_B`
**Source:** MM-Bench, 2018 (MCM/ICM-style)
**Document type:** Initial modeling *plan* (roadmap only). This draft contains no computations, no fitted models, no data analysis, and no final results or conclusions. All statements are forward-looking proposals for the downstream modeling/solving stage.

**Provided data reference:** `2018_MCM_Problem_B_DATA.pdf` (data supplement of the original problem). At the time of writing this plan, the `data/` workspace directory is empty; the file is expected to be staged later. Section 4 therefore specifies a *conditional* ingestion plan: if the PDF is unavailable, the pipeline will fall back to curated public sources (UN World Population Prospects, UNESCO/Ethnologue-style speaker statistics, national census language tables, international migration stocks/flows, internet/social-media penetration, and trade/tourism indicators). Collection in that fallback case is a downstream implementation task, not part of this planning document.

---

## 1. Problem Background and Restatement

### 1.1 Background (as given)

Roughly 6,900 languages are spoken on Earth today. About half of the world's population claims one of ten languages as a native language, in descending order of native speakers: Mandarin (incl. Standard Chinese), Spanish, English, Hindi, Arabic, Bengali, Portuguese, Russian, Punjabi, Japanese. When *total* speakers (native plus second/third/etc. language speakers) are counted, both the set and the ordering shift relative to the native-speaker list.

The number of speakers of a language will be treated as a dynamic quantity that can rise or fall over time under multiple influences, including (but not limited to):

- governmental promotion or suppression of languages;
- languages used in education;
- social pressure and prestige effects;
- migration and assimilation of cultural groups;
- immigration/emigration with countries speaking other languages;
- globalization channels that let geographically distant languages interact: international business, global tourism, electronic communication/social media, and machine-assisted translation.

The assignment explicitly instructs that unpredictable, high-impact/low-probability events (e.g., asteroid collisions that could abruptly end or reshape linguistic trends) be ignored.

### 1.2 Client scenario

A large multinational service company headquartered across New York City (USA) and Shanghai (China) is expanding internationally. It wants each new office staffed by employees who speak both English and one or more additional languages. The COO commissions an investigation into (i) global language trends and (ii) candidate locations for new offices.

### 1.3 Restated requirements (what must be answered)

- **Part I-A:** Model the *over-time distribution* of language speakers, driven by the listed influences and any additional factors the team identifies, anchored to projected trends.
- **Part I-B:** Use that model to project native-speaker and total-speaker counts over a **50-year horizon**; assess whether any language in the *current* top-ten lists (native or total) will be displaced by another language; explain the mechanism.
- **Part I-C:** Given projected global population and migration patterns, determine whether the *geographic distributions* of these languages shift over the same horizon, and if so, how.
- **Part II-A:** Propose **six new international office locations** and the language(s) each office would use, derived from the Part I model; discuss whether short-term vs. long-term recommendations differ.
- **Part II-B:** Evaluate whether **fewer than six** offices might suffice given evolving global communications; specify what additional information would be needed and how the trade-off would be analyzed.
- **Part III:** A **1–2 page memo** to the COO summarizing results and recommendations.

### 1.4 Deliverable inventory

1. A documented language-dynamics model (structure, parameters, calibration target).
2. 50-year projections of native and total speaker counts, plus rank-stability/entry-exit analysis of the top-ten lists.
3. Geographic distribution projections of the top languages under population/migration scenarios.
4. A location-scoring framework and a ranked set of six (or fewer) candidate office cities with associated languages.
5. Short-term vs. long-term recommendation comparison.
6. A decision-analytic analysis of the "open fewer offices" option, with a stated additional-data request list.
7. The executive memo.

---

## 2. Objectives and Subproblems

### 2.1 Primary objective

Build a coherent, calibratable, and stress-testable framework that projects global language use (native and total speakers) and language geography over ~50 years, and converts those projections into defensible office-location and language-coverage recommendations for the client.

### 2.2 Subproblem decomposition

| ID | Subproblem | Planned output (to be produced downstream) |
|----|------------|--------------------------------------------|
| SP1 | Define and segment the speaker population (native vs. L2/non-native) and the language set of interest (top-10 plus "challenger" languages). | A formal state vector and language taxonomy. |
| SP2 | Formalize the influence/force structure (government, education, pressure, migration, globalization channels) as measurable drivers. | A driver inventory mapped to data proxies. |
| SP3 | Model native-speaker dynamics with population and fertility/mortality structure. | Native-speaker trajectory model. |
| SP4 | Model second-language acquisition, retention, and attrition. | L2 transition/transition-matrix or learning-rate model. |
| SP5 | Couple SP3+SP4 to obtain total speakers and rank evolution. | Joint native+total speaker projection. |
| SP6 | Add spatial structure: population growth + migration by region to project geographic distributions. | Regional/geographic language-share projection. |
| SP7 | Build a location-selection scoring model combining language coverage, business relevance, market size, and operational cost. | City ranking + six-office portfolio. |
| SP8 | Time-horizon analysis: short-term vs. long-term recommendation divergence. | Scenario comparison memo section. |
| SP9 | Optimization/decision analysis for the "fewer than six offices" question. | Marginal-value/coverage analysis + additional-data request. |
| SP10 | Communicate outcomes to the COO. | 1–2 page memo. |

### 2.3 Scope boundaries

- Time horizon: ~50 years (with short-term ~5–10 yr and long-term ~50 yr sub-horizons).
- Geographic resolution: country/region first; city-level only for the office-selection layer.
- Language resolution: the ten listed languages plus a controlled set of plausible challengers (e.g., other high-growth or high-spread languages) selected in SP1.
- Excluded: catastrophic tail events per the problem note.

---

## 3. Assumptions

Each assumption below is stated with a justification and a planned validation/relaxation path.

### 3.1 Population and demographic assumptions

- **A1 — Demographic backbone is exogenous and trusted.** Global and regional population, age structure, fertility, and mortality will be taken from a standard projection source rather than modeled from scratch. *Justification:* language dynamics are a small perturbation on demographics; re-deriving demography adds noise. *Validation:* compare 2+ independent projection sources; adopt a central case and use alternatives as scenarios.
- **A2 — Migration flows are scenario-parameterized.** Immigration/emigration will be treated as scenario inputs (low/central/high) rather than fully endogenized. *Justification:* migration is policy- and shock-dependent and hard to forecast. *Validation:* sensitivity sweep across flow multipliers.
- **A3 — Regional carry-over of language into destination countries is gradual.** Migrants and their descendants adopt destination languages over multi-generation timescales while possibly retaining heritage languages. *Justification:* consistent with observed assimilation/retention literature. *Validation:* test multiple assimilation-horizon values.

### 3.2 Linguistic assumptions

- **A4 — Two-track speaker accounting.** Native and non-native (L2+) speaker stocks are modeled separately and additively to give total speakers; a person may contribute to multiple languages' L2 stock but to exactly one native language. *Justification:* matches the problem's native vs. total distinction. *Validation:* internal consistency checks (sum constraints, non-negativity).
- **A5 — Prestige/utility drives L2 acquisition.** L2 acquisition rates will be modeled as increasing in a language's economic/prestige utility index (trade, employment, media, education). *Justification:* captures the background's "social pressure / business / media" drivers. *Validation:* compare fitted drivers against historical L2 growth anecdotes.
- **A6 — Education and government policy shift slowly.** Policy effects will be modeled as smooth or stepwise parameter changes rather than abrupt state changes, absent shocks. *Justification:* institutional inertia. *Validation:* scenario toggles for policy-shift timing.
- **A7 — Machine translation compresses the value of learning low-utility languages but does not eliminate high-utility learning.** Modeled as a time-varying modifier on acquisition incentive. *Justification:* reflects the background's translation-technology point. *Validation:* contrast "translation-cheap" vs. "translation-expensive" scenarios.
- **A8 — No new languages of material size emerge; no catastrophic language extinction events.** *Justification:* directly inherited from the problem note (ignore high-impact/low-probability events) and reasonable over 50 years. *Validation:* documented as a modeling boundary.

### 3.3 Client/decision assumptions

- **A9 — "Speak English + one or more languages" is a hard staffing constraint** for each office. *Justification:* stated by the problem. *Validation:* confirm against client usage during sensitivity analysis.
- **A10 — Office value depends on market access, talent availability, cost, and language coverage.** *Justification:* standard location-selection factors. *Validation:* weight sensitivity analysis (SP7).
- **A11 — Comparative rankings matter more than absolute magnitudes** for the displacement (Part I-B) and location (Part II-A) questions. *Justification:* the problem asks about *replacement* and *choices*, which are ordinal. *Validation:* rank-stability testing under parameter perturbation.

### 3.4 Data assumptions

- **A12 — Provided/fallback sources are sufficiently consistent** to be harmonized via crosswalks (language ↔ country ↔ region). *Justification:* independent sources define languages/territories differently. *Validation:* reconciliation checks and documented mapping rules.

---

## 4. Data Processing Plan

> This section plans data work; it does **not** execute it. No data is analyzed here.

### 4.1 Sources (expected)

- **Primary provided file:** `2018_MCM_Problem_B_DATA.pdf` — to be parsed for speaker statistics, tables, and any per-language/per-region figures.
- **Fallback/auxiliary (only if needed, collected downstream):** UN World Population Prospects (population + migration), national census language tables, UNESCO education-language indicators, internet/social-media penetration, trade and tourism indicators, GDP/HDI-style utility proxies, and translation-technology adoption indicators.

### 4.2 Extraction and ingestion pipeline (planned)

1. **PDF/text extraction** of tables and figures from the provided supplement; convert tables to structured records.
2. **Schema design**: a tidy long-format table keyed by `(language, region, year, metric, value, source, confidence)` covering native speakers, L2+ speakers, population, migration, and driver proxies.
3. **Provenance tagging**: every record carries source and a confidence/quality flag.
4. **Crosswalk construction**: standardized language codes and country→region groupings to reconcile differing definitions.

### 4.3 Cleaning and preprocessing (planned)

- Unit harmonization (counts in persons; thousands/millions normalized).
- Year alignment to a common grid (e.g., 5-year or annual as available).
- Missing-data handling: interpolation along time, hierarchical imputation (global→region→country), and explicit missingness flags; never silently fill.
- Outlier and definitional-break detection with documented flags (do not blindly remove).
- Duplicate/overlap resolution across sources with precedence rules.

### 4.4 Feature construction (planned)

- **Speaker stocks:** native stock, L2+ stock, total stock per language per region per year.
- **Demographic features:** population, age structure, growth rates, net migration.
- **Driver indices:** government-promotion proxy, education-language exposure, prestige/utility index (economic + media + trade), translation-technology adoption index.
- **Spatial features:** region-level language shares and diaspora concentrations.
- **Client features (for Part II):** language coverage demand signals, market size/attractiveness, talent availability, cost-of-operation proxies.

### 4.5 Data usage strategy

- **Calibration window:** historical series for fitting dynamic parameters.
- **Hold-out window:** most recent observed period reserved for out-of-sample checks.
- **Scenario inputs:** migration, policy, and translation-technology paths supplied as exogenous scenario sets (low/central/high).
- **Splitting discipline:** no target leakage from hold-out into calibration; document every transformation.
- **Contingency:** if the provided PDF is unavailable or insufficient, the fallback source set and crosswalk rules above define the substitute ingestion path (executed downstream, not here).

---

## 5. Candidate Model Framework

> Candidate methods are listed for selection during implementation. No model is fitted or solved here.

### 5.1 Overall architecture (planned)

A **layered, modular** framework:

- **Layer 0 — Demographic engine:** exogenous population/migration projections.
- **Layer 1 — Native-speaker dynamics:** per-language native stocks driven by regional population and fertility/language-transmission rates.
- **Layer 2 — L2 acquisition/retention/attrition:** transition model turning population into second-language speakers as a function of utility/prestige/education/policy.
- **Layer 3 — Coupling & aggregation:** combine to total speakers; compute ranks.
- **Layer 4 — Geographic layer:** regional language-share maps under migration scenarios.
- **Layer 5 — Decision layer:** location scoring/optimization and portfolio selection.

### 5.2 Candidate models by subproblem

| Subproblem | Candidate approach(es) | Notes / trade-offs |
|-----------|------------------------|--------------------|
| SP3 native dynamics | Cohort-component projection; logistic/Bass-style diffusion for language transmission; gravity-style transfer under migration | Cohort model is standard & transparent; diffusion captures adoption shape; gravity captures spatial transfer. |
| SP4 L2 dynamics | Compartmental (SIR-like susceptible→learner→speaker→attritor); Markov transition matrices; discrete-choice/utility-driven learning rates | Compartmental is intuitive and calibratable; Markov gives cleaner age/generation structure; utility models ground drivers in economics. |
| SP5 coupling | System of coupled ODE/difference equations; multi-state projection; agent/individual-level simulation (sensitivity-grade) | ODE/state system preferred for tractability; ABM reserved as exploratory cross-check. |
| Rank dynamics (I-B) | Rank-tracking via projected stocks; rank-transition/markov-chain-on-orderings; Monte Carlo rank stability | Enables explicit "replacement" answers and probability of displacement. |
| Geography (I-C) | Regional share projection; spatial diffusion/migration model; gravity model of diaspora formation | Gravity model leverages population/migration data; share projection gives interpretable maps. |
| Location selection (II-A) | Multi-criteria decision analysis (weighted scoring / AHP / TOPSIS); facility-location optimization (max-coverage / p-median) | MCDA gives transparent rankings; optimization enforces "exactly/at most six" constraints. |
| Fewer offices (II-B) | Marginal-coverage analysis; cost-benefit / ROI; scenario decision trees; sensitivity/robustness of diminishing returns | Directly addresses the "fewer than six" trade-off and names missing information. |

### 5.3 Illustrative mathematical ideas (to be finalized later)

- **Native stock:** `N_l(t+1) = Σ_r [ (1-μ) · τ_l,r · P_r(t) · s_l,r(t) ] + migration terms`, where `s_l,r` is regional share and `τ_l,r` a transmission/retention factor.
- **L2 stock:** compartmental flow with rates `β_l(utility, education, policy, translation)` for acquisition and `δ_l` for attrition.
- **Total speakers:** `T_l = N_l + L2_l` (with multi-language L2 accounting rules).
- **Utility index:** `U_l(t) = f(trade, employment, media, prestige, tourism, translation-adoption)`.
- **Location score:** `Score_c = Σ_k w_k · z_k(c)` over normalized criteria, with constraints from the coverage requirement.
- **Coverage/fewer-offices:** maximize expected covered demand minus cost `Σ offices`, with diminishing marginal returns analyzed explicitly.

These are *structure sketches only*; coefficients, functional forms, and calibration are deferred.

### 5.4 Advantages and limitations by candidate

- **Cohort/demographic:** interpretable, standard, data-hungry for language-specific transmission.
- **Compartmental L2:** transparent mechanism, needs utility calibration, may oversimplify heterogeneity.
- **Markov/generation:** captures assimilation, requires generation-level data.
- **Gravity/spatial:** leverages migration data, sensitive to distance/friction assumptions.
- **ABM:** high expressiveness, calibration/computation heavy — cross-check only.
- **MCDA/AHP/TOPSIS:** transparent and stakeholder-friendly, weight-sensitive.
- **Facility-location optimization:** enforces constraints optimally, requires clean demand/cost inputs.

### 5.5 Variables (planned taxonomy)

- **State:** `N_l,r(t)`, `L2_l,r(t)`, `T_l(t)`, ranks.
- **Exogenous:** `P_r(t)`, migration `M_r,r'(t)`, policy/education indicators, translation-adoption.
- **Parameters:** transmission/retention, acquisition/attrition rates, utility weights, spatial friction.
- **Decision:** office set, office languages, staffing/coverage constraints.

---

## 6. Implementation Roadmap

> This is a build plan. No code has been written or run.

### 6.1 Modules to be developed

1. **`ingest`** — PDF/table extraction + tidying to the long schema.
2. **`harmonize`** — crosswalks, unit/year alignment, missingness handling.
3. **`features`** — driver-index construction and speaker-stock assembly.
4. **`demo`** — demographic preprocessing (exogenous scenario paths).
5. **`dynamics`** — native + L2 + coupling engine (parameterizable).
6. **`rankgeo`** — rank tracking and geographic share projection.
7. **`scenarios`** — scenario management (migration/policy/translation multipliers).
8. **`decision`** — location scoring, portfolio optimization, fewer-office analysis.
9. **`validation`** — backtests, sensitivity sweeps, rank-stability Monte Carlo.
10. **`report`** — figures/tables and memo drafting (downstream).

### 6.2 Workflow sequence (planned)

1. Lock the language/region taxonomy and assumptions register.
2. Build and validate the ingestion/harmonization pipeline.
3. Construct features and driver indices.
4. Implement and calibrate native dynamics.
5. Implement and calibrate L2 dynamics; couple to total.
6. Produce scenario-based 50-year projections and rank analyses (I-A/I-B).
7. Add geographic layer and produce distribution projections (I-C).
8. Build decision layer; score cities; select six-office portfolio (II-A).
9. Run fewer-office marginal/decision analysis and compile additional-data request (II-B).
10. Draft the COO memo (Part III).

### 6.3 Computational design (planned)

- Deterministic core (state-system integration) + Monte Carlo wrapper for uncertainty.
- Vectorized tabular processing for features; clear separation of data vs. model config.
- Config-driven scenarios (no hard-coded assumptions in code paths).
- Reproducibility: fixed seeds, documented versions, artifact logs.

### 6.4 Risk register (planning-level)

| Risk | Planned mitigation |
|------|--------------------|
| Provided PDF missing/insufficient | Fallback curated sources + documented crosswalks (Section 4.5). |
| Divergent definitions across sources | Crosswalk rules + confidence tags. |
| Over-parameterization | Prefer parsimonious core; sensitivity over fitting more knobs. |
| Unstable ranks near cut-off | Rank-stability Monte Carlo. |
| Subjective location weights | Multi-weight scenarios + stakeholder-review-ready MCDA. |

### 6.5 Milestones (sequenced, not dated)

M1 taxonomy+assumptions → M2 data pipeline → M3 native model → M4 L2+coupling → M5 projections/ranks → M6 geography → M7 decision layer → M8 fewer-office analysis → M9 memo.

---

## 7. Validation Strategy

### 7.1 Evaluation metrics (planned)

- **Fit/backtest:** MAPE/RMSE on held-out speaker counts; directional-accuracy of trends.
- **Ranking realism:** rank-correlation between predicted and observed historical orderings.
- **Consistency:** accounting identities hold (non-negativity, sum constraints, native unique-assignment).
- **Decision quality:** rank stability of office portfolios under perturbations; constraint satisfaction.
- **Robustness:** output spread across scenarios (not just central case).

### 7.2 Validation methods (planned)

- **Hold-out temporal backtesting** (calibrate on early years, test on recent).
- **Cross-source consistency checks** where overlapping data exist.
- **Degenerate/edge-case tests** (zero migration, frozen policy, extreme translation adoption).
- **Structural checks** against known qualitative facts (e.g., native vs. total orderings differ).
- **Expert/qualitative review** of parameters and assumptions register.

### 7.3 Sensitivity and uncertainty analysis (planned)

- One-at-a-time sweeps over key parameters (transmission, acquisition, attrition, spatial friction, utility weights).
- Multi-parameter Monte Carlo with output distributions for trajectories and ranks.
- Scenario matrix (migration × policy × translation-adoption) to bound outcomes.
- Decision-layer weight sensitivity for the office portfolio (and the fewer-office option).
- **Displacement analysis:** probability that any top-ten entry is overtaken, and which challenger is most likely.

---

## 8. Expected Result Interpretation

> This section describes how future outputs should be read, not what they are.

- **Trajectory outputs** will be interpreted as *scenario-conditional projections*, not forecasts; the central case plus uncertainty bands should be reported together.
- **Native vs. total divergence** should be explained via the L2 layer (a language may hold native rank while rising/falling in total rank, or vice versa).
- **Displacement (I-B)** should be reported as a graded likelihood with the mechanism (utility, education, migration) and the specific challenger language, acknowledging proximity to rank cut-offs.
- **Geographic shifts (I-C)** should be described as redistribution of shares (diaspora growth, urbanization, regional population weights), distinguishing share change from absolute-count change.
- **Office recommendations (II-A)** should be presented as a ranked, criterion-transparent portfolio with per-office language coverage, and with explicit short-term vs. long-term splits where the ranking diverges.
- **Fewer offices (II-B)** should be framed as a diminishing-returns/coverage trade-off, with the marginal value of the 6th vs. 5th vs. 4th office, and a concrete list of additional information (client budgets, latency/real-time needs, remote-work capacity, translation-tool capabilities, hiring constraints, tax/legal factors).
- **Memo (III)** should translate technical outputs into decisions, risks, and next steps for the COO.

---

## 9. Limitations and Improvements

### 9.1 Anticipated limitations

- Data scarcity/unevenness for L2 speakers and for many regions; heavy reliance on proxies.
- Aggregation error from country→language mapping (multilingual states, mixed households).
- Utility/prestige indices are subjective and hard to validate directly.
- Scenario dependence: results inherit migration/policy/translation assumptions.
- Modeling 6,900 languages is infeasible; the plan restricts to the ten listed plus a controlled challenger set, which may miss emergent languages.
- Machine-translation's long-run effect is genuinely uncertain; modeled only parametrically.

### 9.2 Planned improvements (future work)

- Enrich L2 data via census microdata and survey harmonization.
- Increase regional resolution (sub-national, city-level) for the geographic layer.
- Replace parametric utility indices with econometrically estimated drivers.
- Add generation-structured (age×generation) linguistic matrices.
- Incorporate network/social-media diffusion signals more directly.
- Formalize uncertainty propagation end-to-end (into the decision layer).
- Validate against independent future data releases as they appear.

### 9.3 Explicitly out of scope

- Catastrophic/unknown-shock modeling (per problem instruction).
- Full endogenization of migration and policy (kept as scenarios).
- Real-time translation-technology forecasting.

---

## Appendix A — Assumptions ↔ Requirements Traceability

| Requirement | Assumptions relied upon | Subproblems | Planned section output |
|-------------|-------------------------|-------------|------------------------|
| I-A (model distributions over time) | A1–A8 | SP1–SP5 | §5, §6 |
| I-B (50-yr native/total; displacement) | A4, A5, A11 | SP3–SP5, rank layer | §7.3, §8 |
| I-C (geographic distribution change) | A2, A3, A12 | SP6 | §5.2, §6 |
| II-A (six offices; short vs long) | A9, A10 | SP7, SP8 | §5.2, §8 |
| II-B (fewer than six; extra info) | A9, A10 | SP9 | §5.2, §8 |
| III (memo) | — | SP10 | §8 |

## Appendix B — Planning Checklist (to be satisfied downstream)

- [ ] Data presence confirmed (`2018_MCM_Problem_B_DATA.pdf`) or fallback documented.
- [ ] Assumptions register finalized and versioned.
- [ ] Model modules implemented per §6 and calibrated per §4.5.
- [ ] Validation per §7 completed with reported metrics.
- [ ] Scenario matrix executed; ranks and geography reported with uncertainty.
- [ ] Decision layer produces ranked portfolio + fewer-office analysis.
- [ ] Memo drafted for the COO.

---

*End of planning draft. This document is a blueprint only; no solving, computation, or analysis has been performed.*
