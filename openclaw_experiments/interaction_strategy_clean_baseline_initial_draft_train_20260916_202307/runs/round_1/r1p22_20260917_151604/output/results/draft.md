# Modeling Blueprint Draft
## Measuring the Evolution and Influence in Society's Information Networks
### ICM 2016 Problem D — Planning Document (Draft, Not a Solution)

> **Status:** Planning draft only. This document specifies a modeling roadmap, assumptions, candidate methods, data plans, implementation steps, and validation strategy. It intentionally contains **no computed results, no data analysis, no fitted models, no executed experiments, and no final conclusions.** All statements are forward-looking and to be executed in later stages.

---

## 1. Problem Background and Restatement

Society's information networks have evolved across eras defined by the dominant communication technology:

1. **1870s** — Newspapers delivered by rail; stories relayed by telegraph.
2. **1920s** — Radio becomes a common household appliance.
3. **1970s** — Television reaches most homes.
4. **1990s** — Households begin adopting the early internet.
5. **2010s** — Mobile phones provide near-global connectivity.

Across these eras, the **speed of information flow** and the **perceived value of information** appear to co-evolve: faster, wider-reaching media change what is considered "news," who can originate it, and how quickly public opinion can be moved. The problem asks us to model this co-evolution and to use it both retrospectively (explain history) and prospectively (project to ~2050), while also modeling how public interest and opinion can be influenced within today's densely connected networks.

### Restatement of Tasks (as planning targets)

- **(a) Model Development.** Design a framework describing information flow and a definition (or set of criteria) for what qualifies as "news."
- **(b) Model Validation.** Plan how the framework would be calibrated and validated against historical data, and how it would be used to reproduce/compare with present-day communication.
- **(c) Future Prediction.** Plan a projection of communication network relationships and capacities around 2050.
- **(d) Public Influence Modeling.** Plan a model of how public interest and opinion can be influenced through today's information networks.
- **(e) Information Spread Analysis.** Plan how information value, initial opinion, message form, source, and network topology jointly drive spread and influence.

### Why This Is a Hard Modeling Problem

- **Heterogeneous eras:** Each period has a different dominant medium, different cost structures, different audience sizes, and different measurement conventions.
- **Data scarcity and incomparability:** Historical data comes from many sources with inconsistent definitions, coverage, and granularity.
- **Coupled dimensions:** Speed, value, reach, trust, and opinion dynamics are interlinked, so a single monolithic model may be unwieldy.
- **Forward extrapolation risk:** Projecting to 2050 exceeds the calibration range; structural change (not just parameter drift) is likely.

---

## 2. Objectives and Subproblems

### 2.1 Primary Objectives

- **O1.** Articulate a unified, era-agnostic representation of an information network (actors, channels, messages, and value attributes).
- **O2.** Formulate a quantitative notion of "information value" and a criterion that distinguishes "news" from non-news.
- **O3.** Model the coupled dynamics of information **flow speed/reach** and **value/impact** across eras.
- **O4.** Provide a validation pathway anchored in historical data, and a comparison pathway against present-day reality.
- **O5.** Produce a principled projection of network relationships and capacity around 2050.
- **O6.** Model opinion/interest influence in a modern, networked public arena, including misinformation dynamics.
- **O7.** Establish a decision-oriented use case: given information value, initial opinion, message form, source, and topology, characterize expected spread and influence.

### 2.2 Subproblem Decomposition (planning-level)

| ID | Subproblem | Related Task | Planned Deliverable |
|----|------------|--------------|---------------------|
| S1 | Unified network representation across eras | (a) | Formal schema + era parameterization table (to be filled later) |
| S2 | Definition and operationalization of information value | (a), (e) | Value model specification + candidate indicators |
| S3 | "News" classification criteria | (a) | Decision rule / scoring rubric blueprint |
| S4 | Flow-and-reach dynamics model | (a), (c) | Candidate dynamic model options + state variables |
| S5 | Historical validation design | (b) | Validation protocol + metric list |
| S6 | Present-day reconciliation design | (b) | Comparison protocol |
| S7 | 2050 projection design | (c) | Scenario/scaling approach options |
| S8 | Opinion dynamics and influence model | (d), (e) | Coupled opinion-spread model options |
| S9 | Source, message form, and topology sensitivity | (e) | Experiment design (factorial/ablation plan) |
| S10 | Robustness and sensitivity framework | (b), (c) | Sensitivity analysis plan |

### 2.3 Deliverables (planned)

- A written modeling framework with clearly separated sub-models.
- A data specification (required variables, sources, granularity, era mapping).
- A pipeline blueprint (preprocessing → features → calibration → simulation → validation → projection).
- A validation and sensitivity design.
- An interpretation guide stating what kinds of results would support or refute the framework.

---

## 3. Assumptions

Assumptions are grouped by role. Each includes a **justification** and a **future validation approach**.

### 3.1 Structural / Representational Assumptions

- **A1. Network abstraction is valid across eras.** Any era's information system can be represented as a directed (or time-stamped) graph of sources, intermediaries, and receivers, with channels as edges. — *Justification:* enables a common modeling language and comparability. — *Validation:* check that historical descriptive accounts can be mapped without contradiction; run structural sanity checks per era.
- **A2. Messages can be summarized by a small set of attributes** (value, novelty, emotional valence, durability, format). — *Justification:* keeps models tractable and comparable. — *Validation:* test sensitivity of outputs to the attribute set; compare against richer representations.
- **A3. Eras are distinguishable but connected.** Each era has a dominant medium, yet adoption overlaps between adjacent eras. — *Justification:* matches the historical record of gradual technological diffusion. — *Validation:* model overlap via adoption curves rather than hard cutoffs.

### 3.2 Dynamic / Behavioral Assumptions

- **A4. Speed and value are coupled.** Faster distribution raises the marginal value of timely content and alters selection pressure on what becomes "news." — *Justification:* observed co-evolution of media speed and news character. — *Validation:* test whether unidirectional (value→speed or speed→value) or bidirectional coupling better reproduces historical trends.
- **A5. Adoption of a medium follows a bounded diffusion process** (e.g., S-curve-like), not unbounded growth. — *Justification:* technology adoption is routinely bounded by population and utility saturation. — *Validation:* compare competing adoption functional forms for fit to historical series.
- **A6. Opinion responds to exposure in a bounded, saturating way** (diminishing returns per repeated exposure). — *Justification:* avoids runaway effects and matches saturation intuitions. — *Validation:* test monotone saturating vs. linear response in scenario experiments.
- **A7. Sources differ in credibility and reach**, and these differences persist over short horizons. — *Justification:* central to influence and misinformation modeling. — *Validation:* perturbation tests on source-credibility parameters.

### 3.3 Data / Measurement Assumptions

- **A8. Historical proxy indicators** (circulation, penetration, adoption rates, consumption time) are usable stand-ins for underlying flow/reach. — *Justification:* direct network measurements do not exist historically. — *Validation:* cross-source consistency checks; triangulation across at least two proxies per era.
- **A9. Data from different eras can be normalized to a common scale** (e.g., per-capita, share-of-population, or index forms). — *Justification:* required for cross-era comparison. — *Validation:* sensitivity to normalization choice; report results under multiple normalizations.
- **A10. Missing/ambiguous historical values can be handled via documented imputation and sensitivity bounds.** — *Justification:* historical records are incomplete. — *Validation:* compare imputation strategies; bound output uncertainty via scenario envelopes.

### 3.4 Scope Assumptions

- **A11. Global aggregates are acceptable first**, with regional disaggregation deferred. — *Justification:* keeps the first modeling pass tractable.
- **A12. The 2050 projection is a scenario-conditional projection**, not a single-point forecast. — *Justification:* long-horizon structural change implies irreducible uncertainty.
- **A13. Human behavior parameters are stable within an era** and may shift only across era boundaries. — *Justification:* simplifies calibration; treated as a modeling simplification to be relaxed later.

---

## 4. Data Processing Plan

> This section specifies **what data will be required and how it will be handled**. No data will be analyzed in this draft.

### 4.1 Data Requirements (to be sourced later)

| Category | Planned variables | Role |
|----------|-------------------|------|
| Medium availability | Household penetration/adoption per medium per year | Flow capacity proxy |
| Reach | Circulation (newspapers), radio/TV ownership, internet/mobile subscriptions | Network size proxy |
| Consumption | Time/attention per medium, frequency of use | Intensity proxy |
| Speed | Latency/transmission-time anecdotes, publication-to-reception intervals | Flow-speed proxy |
| Content/value proxies | News volume, event coverage, salience measures | Value proxy |
| Context/events | Major world events and their era-specific propagation narratives | Validation anchors |
| Modern network data | Platform-level spread statistics, engagement metrics, false-information studies | Task (b),(d),(e) |

### 4.2 Preprocessing Plan

1. **Source cataloging:** record provenance, era, unit, coverage, and known caveats for every series.
2. **Unit harmonization:** convert to per-capita or share-of-population where possible; document conversion factors.
3. **Temporal alignment:** map all series to a common annual (or era-block) time axis; explicitly flag interpolated points.
4. **Missing-data treatment:** define a default imputation approach and at least one alternative; retain a "missingness" flag.
5. **Normalization:** plan multiple candidate normalizations (min–max, z-score, index-to-baseline, log) to test stability.
6. **Outlier/anomaly handling:** define detection criteria and a policy for retention vs. winsorization.
7. **Era tagging:** assign each observation to an era plus a continuous "adoption share" descriptor to allow overlap.

### 4.3 Feature Construction Plan

- **Capacity features:** adoption share, reach density, channel multiplicity.
- **Speed features:** expected latency, propagation half-life proxies.
- **Value features:** composite information-value index (components to be specified), novelty/durability proxies.
- **Network features (modern era):** degree distribution, clustering, community structure, centralization.
- **Source features:** credibility tier, reach tier, origin diversity.
- **Message-form features:** format category (text/audio/visual/interactive), length, emotional load proxy.

### 4.4 Data Usage Strategy

- **Calibration set:** earlier eras (e.g., 1870s–1990s) used to fit/constrain the core dynamics.
- **Hold-out validation:** the 2010s block and modern data used as an out-of-sample check.
- **Anchoring cases:** selected major events used as qualitative/quantitative validation scenarios.
- **Projection inputs:** only structural parameters and scenarios feed the 2050 projection; no leakage from validation outcomes.
- **Governance:** maintain a data dictionary and a reproducibility log; keep raw vs. processed layers separated.

### 4.5 Data Quality and Bias Considerations (planning)

- Survivorship and reporting bias in historical records.
- Definitional drift (what counted as "news," what counted as "circulation").
- Coverage gaps in early eras and non-Western contexts.
- Modern-platform metrics are platform-defined and non-identical across platforms.
- Planned mitigation: multi-proxy triangulation, explicit uncertainty bands, and scenario-based sensitivity.

---

## 5. Candidate Model Framework

The framework is envisioned as **modular sub-models** sharing a common representation, rather than a single monolithic equation. Candidate options are listed; selection will occur in later stages.

### 5.1 Sub-Model A — Network Representation (S1)

- **Candidate 1:** Static layered graph per era (sources → intermediaries → receivers).
- **Candidate 2:** Temporal/contact-sequence network with per-message timestamps.
- **Candidate 3:** Multiplex network (broadcast + peer + algorithmic channels as layers).
- **Advantages:** shared language; supports both historical and modern data.
- **Limitations:** historical edges must be inferred; aggregations may hide heterogeneity.
- **Selection criterion:** ability to encode era-specific media without redefining the schema.

### 5.2 Sub-Model B — Information Value and "News" Definition (S2, S3)

- **Value hypotheses to compare:**
  - Value as a function of **timeliness**, **relevance**, **novelty**, **credibility**, and **reach**.
  - Value as **supply/demand equilibrium** between producers and audience attention.
  - Value as **marginal impact** on opinion/reception.
- **"News" criterion candidates:**
  - Threshold scoring rubric over value dimensions.
  - Bayesian/classifier-style decision rule (features → newsworthy probability).
  - Structural definition (crosses a latency/reach threshold within a time window).
- **Advantages:** yields operational criteria; enables task (e) factor analysis.
- **Limitations:** value is multidimensional and era-dependent; definition risks circularity.
- **Selection criterion:** criterion must be computable from planned features and produce stable era-to-era ordering.

### 5.3 Sub-Model C — Flow/Reach and Speed Dynamics (S4)

- **Candidate 1:** Compartmental diffusion (SIR/SEIR-like) adapted to information.
- **Candidate 2:** Cascade / branching-process models (per-message reproduction).
- **Candidate 3:** Adoption-diffusion (Bass-style) for medium penetration.
- **Candidate 4:** Hybrid: medium adoption governs transmission parameters of a spread process.
- **State variables:** potential audience, active spreaders, saturated/informed, latency, reach.
- **Advantages:** well-understood, calibratable, interpretable.
- **Limitations:** compartmental models assume homogeneity; cascades need topology.
- **Selection criterion:** best historical fit plus interpretable parameters across eras.

### 5.4 Sub-Model D — Coupled Speed–Value Dynamics

- **Candidate 1:** Two-state coupled ODE system (speed ↔ value feedback).
- **Candidate 2:** Delay/age-structured model where value decays with latency.
- **Candidate 3:** Agent-based model where value emerges from agent attention allocation.
- **Advantages:** directly addresses the problem's core co-evolution claim.
- **Limitations:** feedback direction and strength are uncertain; identifiability risk.
- **Selection criterion:** must reproduce qualitative era trends, not just micro fit.

### 5.5 Sub-Model E — Opinion/Influence Dynamics (S8)

- **Candidate 1:** Opinion dynamics (bounded confidence / Deffuant / Hegselmann–Krause).
- **Candidate 2:** Voter/Ising-type models with external influence fields.
- **Candidate 3:** Agent-based belief updating with source credibility weighting.
- **Candidate 4:** Coupled spread + opinion (e.g., "spread of behaviors") framework.
- **Advantages:** captures polarization, influence, and misinformation.
- **Limitations:** heavy parameterization; calibration data limited.
- **Selection criterion:** must accommodate A7 (source heterogeneity) and A6 (saturation).

### 5.6 Sub-Model F — Topology and Source/Message-Form Effects (S9)

- **Topology candidates:** random, small-world, scale-free, community-structured; plus empirically anchored modern topologies.
- **Source candidates:** uniform vs. credibility-tiered vs. reach-tiered source mix.
- **Message-form candidates:** format-dependent transmission/retention multipliers.
- **Advantages:** directly supports designed factorial comparisons for task (e).
- **Limitations:** combinatorial experiment size; confounding.
- **Selection criterion:** design must isolate each factor's marginal contribution.

### 5.7 Sub-Model G — Projection Framework (S7)

- **Candidate 1:** Parameter extrapolation with bounded adoption functions.
- **Candidate 2:** Scenario tree (e.g., incremental vs. transformative technological change).
- **Candidate 3:** Structural-break-aware trend model with expert-informed bounds.
- **Advantages:** communicates a range, not a false point precision.
- **Limitations:** out-of-sample, long horizon, structural change.
- **Selection criterion:** transparency and defensibility of scenario logic.

### 5.8 Cross-Model Integration Vision

A staged integration is planned: **Representation → Value/News → Flow Dynamics → Coupled Speed–Value → Opinion/Influence → Projection**, with shared parameters (adoption share, latency, reach, credibility) flowing between modules. Loose coupling is preferred initially to preserve interpretability.

---

## 6. Implementation Roadmap

> Planning only. No code will be written or executed in this stage.

### 6.1 Planned Modules

| Module | Purpose |
|--------|---------|
| `data_ingest` | Source cataloging, loading, provenance tagging |
| `preprocess` | Unit harmonization, alignment, imputation, normalization |
| `features` | Feature construction (capacity, speed, value, network, source, form) |
| `model_value` | Information-value and news-criterion scoring |
| `model_flow` | Flow/reach/speed dynamic simulation |
| `model_coupled` | Speed–value coupled dynamics |
| `model_opinion` | Opinion/influence and misinformation dynamics |
| `simulate_topology` | Network generators and empirical topology loaders |
| `experiment` | Factorial/ablation experiment driver |
| `validate` | Metrics, hold-out checks, error analysis |
| `project_2050` | Scenario construction and projection harness |
| `report` | Figures/tables generation (future stage) |

### 6.2 Planned Workflow

1. **Specify** schema and era parameterization (S1) and freeze the data dictionary.
2. **Acquire and catalog** data; run preprocessing and produce the processed layer.
3. **Construct features** and the information-value/news scoring pipeline.
4. **Calibrate** flow dynamics on earlier eras; hold out 2010s/modern.
5. **Estimate/compare** coupled speed–value model variants.
6. **Set up opinion/influence model**; run topology/source/message-form experiments.
7. **Validate** via hold-out and anchoring cases; run sensitivity analyses.
8. **Project to 2050** under scenarios; wrap uncertainty bounds.
9. **Document** results interpretation and limitations for the final report.

### 6.3 Algorithmic Toolkit (candidate, to be selected later)

- ODE/compartmental solvers and delay models.
- Monte Carlo simulation for cascades and ABMs.
- Numerical optimization / parameter estimation (grid, gradient-based, or global search).
- Model comparison via information criteria or cross-validation.
- Network statistics and community detection for topology characterization.
- Global sensitivity analysis (variance-based / regression-based screening).

### 6.4 Engineering/Reproducibility Plan

- Versioned inputs with a data dictionary and provenance log.
- Deterministic seeds and recorded environment for simulations.
- Separation of raw / processed / outputs directories (already reflected in workspace layout).
- Tests for preprocessing invariants and model boundary behavior.
- Config-driven experiment definitions to enable reproducible scenario runs.

---

## 7. Validation Strategy

### 7.1 Evaluation Metrics (planned)

| Dimension | Planned metric family |
|-----------|-----------------------|
| Historical fit | Error metrics on held-out series (relative/absolute error, correlation) |
| Trend reproduction | Directional and turning-point agreement with historical narratives |
| Calibration quality | Goodness-of-fit with parsimony penalty (information criteria) |
| Predictive check | Out-of-sample error on 2010s/modern block |
| Structural fidelity | Network statistic comparisons (degree, clustering, community structure) |
| Opinion outcomes | Distributional agreement with documented opinion shifts |
| Robustness | Stability of rankings/outputs under perturbations |

### 7.2 Validation Methods (planned)

- **Temporal hold-out:** calibrate on early eras, test on later eras.
- **Cross-proxy triangulation:** validate using independent proxies within each era.
- **Anchor-case studies:** selected historical events compared against model-implied spread behavior.
- **Backtesting of "news" criterion:** assess whether the rule would classify recognized events appropriately (qualitative rubric).
- **Out-of-sample modern comparison:** compare model-implied present-day network behavior against documented modern communication patterns.
- **Simulation-based checks:** null/alternative scenario runs to confirm expected qualitative behavior (e.g., monotonicity, saturation bounds).

### 7.3 Sensitivity and Uncertainty Plan

- **One-at-a-time screening** for parameter influence.
- **Global variance-based sensitivity** for interaction effects and dominant drivers.
- **Scenario envelopes** for the 2050 projection (best/central/transformative).
- **Structural sensitivity:** compare alternative model structures (e.g., compartmental vs. cascade).
- **Data-perturbation sensitivity:** alternative imputations and normalizations.
- **Reporting standard:** uncertainty ranges and assumptions attached to every headline claim.

### 7.4 Known Validity Threats (to be monitored)

- Overfitting to historical narratives.
- Identifiability issues in coupled feedback systems.
- Extrapolation beyond calibration range.
- Proxy validity gaps (what is measured vs. what is modeled).
- Modern-platform data non-representativeness.

---

## 8. Expected Result Interpretation

> This section describes **how future results would be read**, not what they are.

- **If the coupled speed–value model reproduces era trends**, it would support the hypothesis that faster media systematically reshape the selection pressure on news and its perceived value.
- **If flow-only models suffice**, that would suggest value dynamics are dominated by capacity/reach rather than feedback — a meaningful negative result for the coupling hypothesis.
- **If "news" criterion rankings are stable across eras**, it would indicate an era-invariant core definition; instability would indicate era dependence and motivate a regime-switching formulation.
- **Modern out-of-sample performance** would indicate whether historically calibrated mechanisms still explain today's networked communication, or whether new mechanisms (algorithmic curation, platform virality) must be added.
- **2050 scenarios** should be presented as conditional ranges: what the network would look like under incremental vs. transformative technology trajectories.
- **Opinion/influence experiments** would be interpreted as sensitivity maps — how spread and influence change with value, initial opinion, message form, source credibility, and topology — rather than as prescriptive claims.
- **Robustness of rankings** across perturbations would determine how much confidence to place on any single recommended lever.

---

## 9. Limitations and Improvements

### 9.1 Anticipated Limitations

1. **Historical data sparsity and incomparability** across eras and regions.
2. **Proxy validity**: measured quantities approximate flow/reach/value imperfectly.
3. **Simplified value representation**: a low-dimensional attribute set cannot capture full semantic richness.
4. **Homogeneity assumptions** in compartmental/cascade models vs. real heterogeneity.
5. **Limited calibration data for opinion dynamics**, especially historically.
6. **Projection uncertainty toward 2050** dominated by structural breaks, not parameter noise.
7. **Global-aggregate focus** in the first pass, under-representing regional variation.
8. **Circularity risk** between "what is news" and "what has high value."

### 9.2 Planned Improvements / Extensions

- **Richer representation:** multiplex and algorithmic-channel layers; heterogeneous agents.
- **Semantic/LLM-assisted message-form features** to better capture content effects (to be considered in later stages).
- **Regional disaggregation** and cross-country comparison.
- **Bayesian/uncertainty-first estimation** to formalize credible intervals instead of point fits.
- **Endogenous technology adoption** so media availability co-evolves with usage rather than being exogenous.
- **Adversarial/misinformation module** grounded in documented false-information dynamics.
- **Structural-break detection** to make 2050 scenarios regime-aware.
- **Human-in-the-loop expert elicitation** for scenario bounds.

### 9.3 Next Steps (to be executed in later modeling stages)

1. Finalize the data specification and freeze the schema.
2. Decide between candidate sub-models using pre-registered comparison criteria.
3. Build the preprocessing and feature pipeline.
4. Run calibration, validation, and sensitivity experiments.
5. Execute the 2050 scenario projections.
6. Prepare the full modeling report with figures, tables, and uncertainty statements.

---

*End of planning draft. No results, computations, or conclusions are reported here; all content is a forward-looking modeling roadmap.*
