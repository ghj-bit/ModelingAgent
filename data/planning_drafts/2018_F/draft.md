# Modeling Blueprint Draft — MM-Bench 2018_F

**Problem ID:** `2018_F`
**Title:** MM-Bench 2018_F — The Cost of Privacy: Pricing Personal Information (PI)
**Document type:** Initial modeling plan / roadmap — **planning only, no solution executed**
**Source:** MM-Bench 2018, Problem F
**Status:** Draft v0.1 (pre-modeling)

> Scope note: This document is a *blueprint*. It defines the intended modeling workflow, assumptions, candidate methods, data plan, implementation plan, and validation strategy. It intentionally contains **no computed results, no fitted models, no experiments, and no final conclusions**. All statements are forward-looking ("will", "is intended to", "a candidate approach is").

---

## 1. Problem Background and Restatement

Electronic communication and social-media economies have made personal information (PI) a pervasive, tradable, and increasingly valuable asset. Individuals differ widely in how much they will trade privacy for convenience, price reductions, social standing, medical benefit, or safety. The same individual may freely trade purchasing data yet guard health data; different subgroups (age, citizenship, profession, risk exposure) hold sharply different valuations. PI also carries externalities: one person's disclosure can reveal information about others who are socially, professionally, economically, or demographically linked.

The problem asks a policy-analysis team to **quantify the cost/value of privacy** in electronic communications and transactions across society, and to turn that quantification into a **usable pricing and policy framework**.

**Core question.** What is the monetary value of keeping PI protected, or equivalently, what would others pay to have or use it? And who should govern it — government regulation, a privacy industry, or the individual?

The task explicitly frames five cross-cutting tensions that any model must eventually represent:

1. **Public-good vs. private-good character of data** (public-health tracing, at-risk-population protection vs. commodification).
2. **Domain dependence** (purchasing, social media, health/medical behave differently).
3. **Subgroup dependence** (risk, demographics, culture, politics).
4. **Element-level value** (name vs. name + photo vs. national ID: components of a record are not equally valuable).
5. **Systemic / network / cascade effects** (correlated data, breach cascades, community risk).

**Deliverable of the eventual modeling effort.** A defensible, transparent pricing structure for PI, strata-aware policy analysis, an assessment of market (supply/demand) dynamics, breach-liability considerations, and a two-page policy memo to a national decision maker.

---

## 2. Objectives and Subproblems

The eventual effort will be organized around the eight stated tasks. The plan maps each task to a modeling objective, an intended output artifact, and a dependency on the shared framework.

### 2.1 Primary objective
To construct a **unified, parameterized valuation framework** for PI that (a) prices protection/usage across domains and subgroups, (b) admits element-level decomposition, (c) accommodates market and dynamic effects, (d) captures network/cascade externalities, and (e) supports concrete policy recommendations.

### 2.2 Task-to-objective map

| Task | Modeling objective | Intended artifact (future) | Depends on |
|------|-------------------|----------------------------|-----------|
| **T1** | Define the parameter/measure space for privacy risk: individual characteristics + domain characteristics | A structured **taxonomy of parameters & measures** (subgroup axes × domain axes) | Framework skeleton |
| **T2** | Model cost of privacy across ≥3 domains (social media, financial, health); weight tradeoffs/risks; decompose record elements | **Base pricing model** + element weighting scheme | T1 taxonomy |
| **T3** | Scale pricing to individuals/groups/nations; assess supply–demand forces; model individual control over sale | **Aggregation & market model** | T2 base model |
| **T4** | State assumptions/constraints (regulation, culture, politics); assess "privacy as human right"; add time dynamics | **Assumptions register** + dynamic extension | T2/T3 |
| **T5** | Generational differences in risk-to-benefit perception; aging dynamics; PI vs. PP vs. IP comparison | **Cohort/lifecycle submodel** + analogy analysis | T4 dynamics |
| **T6** | Network effects / correlated data; community-level risk and responsibility | **Network-externality submodel** | T2/T3 |
| **T7** | Massive breach / cascade scenario; agency liability to individuals | **Breach-impact & liability module** | T2/T3/T6 |
| **T8** | Two-page policy memo with defined PI scope | **Policy memo** (final narrative) | All above |

### 2.3 Success criteria (to be judged later)
- The framework will be **transparent** (every price derives from stated parameters).
- It will be **portable** across the three mandated domains.
- It will be **strata-aware** without collapsing to a single global number.
- It will **degrade gracefully** under missing data (documented fallback rankings).
- It will yield **actionable, scoped** policy recommendations rather than a single verdict.

---

## 3. Assumptions

Assumptions are grouped by category. Each is paired with a justification and a planned future validation approach. These will be revisited and stress-tested rather than treated as fixed.

### 3.1 Structural / scope assumptions
1. **PI is treated as an economic good with both private and public dimensions.** *Justification:* the task asks for a price point while also demanding public-good considerations. *Future validation:* compare private-market price estimates against public-good shadow-value estimates; test sensitivity to the public/private mix.
2. **The three mandated domains (social media, financial, health) are representative of the domain space.** *Justification:* stated explicitly by the task. *Future validation:* check whether a fourth domain (e.g., location/mobility) would materially shift aggregate results (out-of-sample domain test).
3. **Prices are expressed in a common monetary unit and are comparable across domains once normalized.** *Justification:* the task asks for a single "pricing structure." *Future validation:* cross-domain normalization robustness checks (per-record vs. per-attribute vs. per-θ, see §5).

### 3.2 Behavioral assumptions
4. **Individuals are heterogeneous but can be partitioned into a finite set of subgroups with approximately homogeneous risk/valuation.** *Justification:* Task 1 explicitly invites subgroup categorization. *Future validation:* within-cluster variance checks; compare against a fully individual-level (non-clustered) model.
5. **Willingness to accept (WTA) / willingness to pay (WTP) is the observable proxy for the value of privacy.** *Justification:* standard welfare-economics approach for non-market goods. *Future validation:* convergence of stated-preference and revealed-preference estimates; scope test and embedding-effect checks.
6. **An individual's decision to share own data affects connected others.** *Justification:* stated in Task 6. *Future validation:* network-model perturbation tests and external-consistency checks.
7. **Preferences drift over time and across cohorts.** *Justification:* Tasks 4 and 5 demand a dynamic element. *Future validation:* back-tests against historical attitude trends if any become available.

### 3.3 Market / institutional assumptions
8. **A partial market for PI can be modeled even though it is currently opaque.** *Justification:* Task 3 explicitly asks whether supply/demand applies. *Future validation:* compare model-implied equilibria against observed data-broker price lists / breach-black-market reports (as illustrations only).
9. **Regulation and cultural/political constraints act as boundaries/constraints on the feasible price space rather than as free variables.** *Justification:* Task 4 requires constraints. *Future validation:* scenario sweeps across regulatory regimes.

### 3.4 Data / methodological assumptions
10. **In the absence of a provided dataset, parameter values will be sourced from literature, public surveys, market reports, and reasoned elicitation (documented).** *Justification:* the dataset definition was empty (see §4.1). *Future validation:* expert-review and triangulation across ≥2 independent sources per key parameter.
11. **Model uncertainties can be handled probabilistically (distributions/priors) rather than as point estimates.** *Justification:* enables sensitivity and robustness analysis. *Future validation:* posterior-predictive / Monte-Carlo convergence checks.

Assumptions 1–11 will be logged in an **Assumptions Register** (id, statement, rationale, owner, validation method, invalidation risk) maintained as the modeling proceeds.

---

## 4. Data Processing Plan

### 4.1 Data availability (important)
The stated **Dataset Definition is empty**: `dataset_path = []`, `dataset_description = {}`, `variable_description = {}`. The staged `data/` directory is **empty**. Consequently, the plan must be **data-first in method but data-agnostic in content**: it must specify *what data it would need*, *how it would be sourced*, *how it would be cleaned and fused*, and *how the model degrades if a source is missing*.

### 4.2 Data needs by task

| Data category | Example variables (future work) | Used by |
|---------------|--------------------------------|---------|
| Demographic / subgroup | age, cohort, income, education, citizenship, occupation, region | T1, T3, T5 |
| Domain exposure | social-media usage, financial-account activity, health-record context | T1, T2 |
| Valuation/preference | WTA/WTP, privacy-concern scales, consent behavior | T2, T3, T4, T5 |
| Record-element inventory | name, DOB, gender, address, national ID, photo, biometrics | T2 |
| Market / price proxies | data-broker price bands, breach-market prices, ad-targeting revenues | T3, T7 |
| Regulatory / legal | jurisdiction rules, protected-record categories, price regulations | T4 |
| Network structure | friendship/family/work/mobility links (or proxies) | T6 |
| Breach incidents | size, data types, affected populations, remediation costs | T7 |

### 4.3 Sourcing strategy (candidate, to be finalized)
- **Stated-preference instruments:** design a survey/vignette plan (contingent valuation, discrete-choice experiments) for WTA/WTP across domains and record elements.
- **Revealed proxies:** enumerate candidate public sources (privacy-concern indices, ad-tech revenue benchmarks, breach reports, data-broker listings) to calibrate ranges — used as illustrative anchors, not as authoritative ground truth.
- **Expert elicitation:** structured elicitation to fill sparse cells (e.g., national-level or rare-subgroup valuations).
- **Synthetic/simulation inputs:** where no source exists, a documented simulation design (parametric scenarios) will be used to keep the model testable end-to-end.

### 4.4 Preprocessing plan (future)
1. **Schema harmonization** — define a canonical schema for individuals × domains × record-elements.
2. **Unit normalization** — convert monetary quantities to a common unit; document year/adjustment conventions.
3. **Missing-data handling** — multiple imputation for survey gaps; explicit "unknown" encoding for structurally absent fields; documented fallback rankings when a whole source is unavailable.
4. **Outlier & validity screening** — detect protest responses, scope-inconsistency, satisficing in elicitations.
5. **Encoding of categorical strata** — one-hot / ordinal for demographics; domain and element dictionaries as controlled vocabularies.
6. **Provenance & versioning** — every input gets a source tag (T1-source, T2-source…) to support auditing and regeneration.

### 4.5 Feature construction (future)
- **Element value vectors:** per-record-element importance scores (name, DOB, gender, ID, photo, …).
- **Domain risk descriptors:** sensitivity, re-identification risk, resale liquidity, public-good weight.
- **Subgroup risk indices:** composite of exposure, harm severity, and protection capacity.
- **Network features:** degree, centrality, correlation strength (for T6).
- **Temporal/cohort features:** birth cohort, lifecycle stage, adoption-trend slope (for T4/T5).

### 4.6 Data usage strategy
- A **calibration/training split** will be used to fit parameter weights; a **held-out** portion (or out-of-sample domain/subgroup) will be reserved for validation.
- Where data are simulated, **scenario grids** will replace the classic train/test split, with parameters swept and results reported as ranges.

---

## 5. Candidate Model Framework

The framework is intended as a **layered stack**: a core valuation kernel, then extensions for aggregation/market, dynamics, networks, and breach cascades. Each layer lists candidate models, key variables, the mathematical idea, and advantages/limitations.

### 5.1 Layer 0 — Shared notation and kernel
Intended notation (to be finalized):
- Subgroup index `g` (demographics/risk class); domain index `d` (social/financial/health); record-element index `e`.
- Privacy valuation `V(g, d, e)` — value of protecting one element/record.
- Risk of exposure `R(g, d, e)`; benefit of sharing `B(g, d, e)`; protection cost `C(g, d, e)`.
- Weights `w(·)` for tradeoffs, stratified by subgroup/domain.

**Candidate kernel forms (to compare):**
- **(a) Additive risk–benefit score:** `V = Σ_e w_e (Risk_e − Benefit_e) + protection cost`. Simple, interpretable; limitation: assumes independence across elements.
- **(b) Multiplicative/hazard form:** `V = Π_e f_e(...)`, capturing that combining name+photo is worth more than the sum. Advantage: models synergy; limitation: needs careful calibration.
- **(c) Utility-theoretic expected-value:** `V = Σ_s p_s · U(harm_s)` over exposure scenarios `s`, with `U` a concave (risk-averse) utility. Advantage: theoretically grounded, handles catastrophic events; limitation: utility elicitation is hard.
- **(d) Hedonic / attribute-price:** regress observed price proxies on attributes. Advantage: data-driven; limitation: needs market data that may be absent.

**Element decomposition (Task 2 sub-question).** A dedicated sub-model will estimate the marginal contribution of each element and of element **combinations**, e.g. incremental value of `photo | name`, using interaction terms or a Shapley-style attribution over element coalitions. *Planned technique:* coalition/Shapley attribution to value "name alone" vs "name+photo" consistently.

### 5.2 Layer 1 — Subgroup × Domain pricing (Tasks 1–2)
- **Candidate approach:** a **stratified panel** where each (subgroup, domain) cell gets a price derived from the kernel, with **weights stratified** by subgroup/domain.
- **Partitioning:** candidate clustering (k-means / latent-class / decision-tree segmentation) over risk/valuation features; number of clusters selected via information criteria.
- **Variables:** from §4.5.
- **Advantage:** directly answers "different weights by subgroup/category." **Limitation:** risk of over-fragmentation reducing statistical power; mitigated by hierarchical pooling (partial pooling / multilevel models).

### 5.3 Layer 2 — Aggregation & market (Task 3)
- **Aggregation:** combine individual valuations into group and national aggregates via population weighting / welfare aggregation (sum, average, or distributionally-weighted).
- **Supply–demand model (candidate):** a market-clearing model where supply = individuals willing to sell at a price, demand = data buyers' marginal value; equilibria found analytically or via simulation. Candidate demand curves from ad-tech/insurance/research value chains.
- **Individual control:** an agent-choice model in which each individual chooses share vs. withhold to maximize personal (and possibly prosocial) utility; extends the market model with **self-ownership**.
- **Advantage:** answers the "is supply/demand appropriate?" question structurally. **Limitation:** PI markets are non-competitive and opaque; results must be framed as scenario bounds.

### 5.4 Layer 3 — Dynamics, cohorts, temporal drift (Tasks 4–5)
- **Candidate:** a **dynamic/state-transition model** (system dynamics or discrete-time Markov) tracking preferences, exposure, and prices over time.
- **Generational submodel:** cohort effects represented as cohort-specific parameters evolving with age and with technological adoption; distinguish **age effect**, **cohort effect**, **period effect** (APC-style decomposition).
- **PI vs. PP vs. IP:** an **analogy/ontology analysis** mapping ownership, exclusivity, transferability, and liability properties; will be formalized as a property-comparison matrix and discussed qualitatively (not a numeric result).
- **Advantage:** captures the "changing beliefs about worth" requirement. **Limitation:** long-horizon dynamics are weakly identified without longitudinal data.

### 5.5 Layer 4 — Network effects (Task 6)
- **Candidate models:** graph-based models (graph Laplacian diffusion / influence models), correlation-aware valuation where `V_i` depends on neighbors' disclosure, and a **community-risk** aggregation.
- **Key idea:** model the externality as a spillover term `Σ_{j∈N(i)} κ_ij · disclosure_j` affecting `i`'s risk; then assess how price systems aggregate to communities/nations.
- **Responsibility question:** framed as an assignment problem of liability across individuals, communities, and institutions.
- **Advantage:** addresses correlated-data concern directly. **Limitation:** network data may be unavailable → fallback to stylized/assumed topologies with sensitivity sweeps.

### 5.6 Layer 5 — Breach & cascade (Task 7)
- **Candidate models:** cascade/threshold models (information cascades, percolation) for large multi-person breaches; **compound loss** model combining direct misuse + dark-web resale + ransom + remediation; liability-allocation model (proportional responsibility, negligence standards).
- **Key idea:** a breach instantaneously shifts a large cohort from "protected" to "exposed," stressing the kernel's handling of correlated, simultaneous exposure and of second-order harms.
- **Advantage:** tests model resilience and links pricing to direct-compensation questions. **Limitation:** cascade parameters are highly uncertain; results will be presented as scenarios.

### 5.7 Design principle across layers
Maintain **one shared kernel** reused by every layer so that layers stay mutually consistent, and expose **all strata weights** as explicit, auditable parameters.

---

## 6. Implementation Roadmap

*No code will be written or run in this planning phase; the following is the intended build sequence.*

### 6.1 Modules (future)
1. **`params/`** — parameter & assumption registry (machine-readable), with sources and ranges.
2. **`kernel/`** — core valuation kernel + element-attribution (Shapley/interaction) component.
3. **`strata/`** — subgroup clustering + domain descriptors.
4. **`aggregate/`** — group/national aggregation + market clearing + individual-choice extension.
5. **`dynamics/`** — temporal/cohort submodel.
6. **`network/`** — graph externality model.
7. **`breach/`** — cascade & liability module.
8. **`analysis/`** — sensitivity, scenario sweeps, uncertainty propagation.
9. **`report/`** — figure/report generation and the policy-memo templating.

### 6.2 Workflow (phases)
- **Phase A — Framing & registry:** finalize notation, assumptions register, parameter register. *Exit:* all identifiers and sources documented.
- **Phase B — Kernel build:** implement kernel + element attribution; unit-test on synthetic sanity cases. *Exit:* kernel reproduces documented monotonicity properties.
- **Phase C — Stratified pricing (T1–T2):** build strata, produce per-cell pricing surfaces. *Exit:* ≥3 domains covered, weights auditable.
- **Phase D — Aggregation & market (T3):** implement aggregation + supply/demand + individual-control scenarios.
- **Phase E — Dynamics & cohorts (T4–T5):** implement time/cohort drift and the PP/IP comparison matrix.
- **Phase F — Networks & breach (T6–T7):** implement externality and cascade/liability modules.
- **Phase G — Validation & sensitivity:** run the full validation suite (§7).
- **Phase H — Synthesis & memo (T8):** produce policy memo with defined PI scope.

### 6.3 Engineering practices (future)
- **Config-driven** runs (no hard-coded parameters) to enable sweep/scenario analysis.
- **Reproducibility:** seeded randomness, pinned versions, provenance tags for every input.
- **Testing:** property-based tests (ordinal sanity: adding an identifier element should not lower value), regression tests on scenario outputs.
- **Separation of concerns:** model layer (compute) vs. reporting layer (narrative), so assumptions can change without rewriting narratives.

### 6.4 Risk register (planning-level)
| Risk | Impact | Planned mitigation |
|------|--------|--------------------|
| No real dataset | High | Documented synthetic/scenario design + external-range calibration |
| Parameter identifiability | High | Partial pooling; report ranges not points; sensitivity-first design |
| Over-fragmented subgroups | Medium | Information-criterion cluster selection; hierarchical pooling |
| Market model opacity | Medium | Present as scenario bounds, not forecasts |
| Network data absence | Medium | Stylized topologies + sweep |
| Value-laden weighting | Medium | Explicit, auditable weights; multiple weighting philosophies compared |

---

## 7. Validation Strategy

### 7.1 Validation goals
To establish that the framework is **internally consistent**, **robust to assumptions**, and **useful for policy** even under data scarcity.

### 7.2 Candidate evaluation metrics (future)
- **Ordinal/face validity:** monotonicity tests (more identifying elements ⇒ not less valuable; higher exposure risk ⇒ higher protection value).
- **Scope validity:** splitting a record into its elements should approximately reconstruct the record value (additivity check).
- **Cross-source agreement:** deviation between literature-, survey-, and market-derived valuations (triangulation error).
- **Stability:** rank-correlation (e.g., Spearman) of subgroup/domain orderings across parameter perturbations.
- **Calibration/coverage:** for simulated scenarios, share of held-out cases within predicted uncertainty bands.
- **Decision-relevance:** does the ranking of policy options flip under plausible parameter ranges? (robustness of recommendations).

### 7.3 Validation methods (future)
1. **Internal consistency checks** (monotonicity, additivity, boundary behavior).
2. **Cross-validation** where any real data exist (leave-one-domain-out, leave-one-subgroup-out).
3. **Expert review** of parameter ranges and policy implications.
4. **Back-testing** against historical reference points (if obtainable), used as illustration only.
5. **Comparative model validation** — compare kernel variants (additive vs. multiplicative vs. utility-based) and report where they agree/disagree.

### 7.4 Sensitivity & uncertainty analysis (future)
- **One-at-a-time (OAT)** sweeps to screen influential parameters.
- **Global sensitivity** (variance-based, e.g., Sobol-type) to quantify parameter importance and interactions.
- **Monte-Carlo uncertainty propagation** to produce price ranges/distributions.
- **Scenario analysis** for regulatory regimes, cultural contexts, generational mixes, network topologies, and breach magnitudes.
- **Stress testing** at extreme values (fully public, fully protected, catastrophic breach) to find model breakpoints.

---

## 8. Expected Result Interpretation

*(Interpretation guidance for future outputs — not results themselves.)*

- **Price outputs** will be **distributions/ranges with explicit scenario dependence**, not single "true" numbers; they should be read as *policy-relevant value bands* conditioned on stated assumptions.
- **Strata differences** will be interpreted as *relative* value signals across subgroups/domains, useful for targeted policy, rather than as precise individual entitlements.
- **Element decomposition** will inform which record components warrant the strongest protection or the largest compensation.
- **Market/dynamic layers** will advise *whether and how* supply–demand logics can be responsibly applied to PI, and how individual control changes incentives.
- **Network and breach layers** will inform liability design and community-responsibility arguments.
- The **policy memo** will translate model outputs into a scoped recommendation with an explicit PI taxonomy (which data types are covered) and an assessment of the "privacy as a human right" question.

**Interpretation cautions.** Outputs will be most credible for *relative comparisons* and *robust orderings*; absolute monetary values will be presented with uncertainty and clearly labeled as model-conditional.

---

## 9. Limitations and Improvements

### 9.1 Anticipated limitations
- **No provided dataset** ⇒ heavy reliance on literature elicitation and simulation; external validity is the central concern.
- **Non-market good** ⇒ WTA/WTP measurement is subject to scope, embedding, and hypothetical bias.
- **Value-laden weights** ⇒ normative choices (risk aversion, public-good weight) shape outputs; must be made explicit.
- **Aggregation ethics** ⇒ summing or averaging individual values embeds distributional judgments.
- **Network/market/cascade parameters** ⇒ weakly identified; results are scenario bounds.
- **Cross-cultural generality** ⇒ findings may not transfer across jurisdictions without re-calibration.

### 9.2 Planned improvements (future iterations)
- Acquire or construct **real survey data** (vignette/DCE) to replace simulated valuation inputs.
- Add a **fourth domain** (e.g., location/mobility) as an out-of-sample test of portability.
- Implement **formal partial-pooling multilevel models** to reduce over-fragmentation.
- Add **behavioral modules** (bounded rationality, present bias) to the individual-choice layer.
- Develop **policy-robustness reports** that explicitly flag recommendation flips across scenarios.
- Build an **interactive scenario explorer** for the decision maker.

### 9.3 Explicit scope statement
This draft defines *how* the team intends to model the cost of privacy and produce a pricing/policy framework. It contains **no executed computation, no fitted model, no experiment, and no final conclusion**; all quantitative content will be produced in later, separately documented modeling phases.

---

*End of draft blueprint — planning only.*
