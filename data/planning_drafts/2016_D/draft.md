# Modeling Blueprint Draft

## MM-Bench 2016_D — The Evolution of Information Flow, Value, and Influence in Communication Networks (1870s → 2010s → 2050)

> **Status: PLANNING DRAFT — NOT A SOLUTION.**
> This document is a roadmap for future modeling work. It contains no data analysis, no
> computations, no fitted parameters, no experimental runs, and no final results or
> conclusions. All statements are forward-looking ("will", "would", "is expected to").
> The staged `data/` directory is currently empty and the dataset schema
> (`dataset_path`, `dataset_description`, `variable_description`) is unpopulated; the data
> plan below therefore assumes the dataset will be **assembled** from the sample sources
> named in the problem addendum plus standard public statistical series.

---

## 1. Problem Background and Restatement

### 1.1 Context

Information now propagates through a dense, technology-connected communications network.
The speed and reach of a piece of information appear to depend both on its **inherent
value** (how important, novel, or newsworthy it is) and on the **position and connectivity**
of the nodes that carry it (influential hubs, central actors, popular media channels). The
Institute of Communication Media (ICM) hypothesizes that a durable cultural drive to share
information — serious and trivial alike — has always existed, but that the *mechanism,
purpose, and functionality* of society's information networks have changed dramatically.

The problem frames this evolution across **five reference periods**:

| Period | Dominant / emergent channel | Character of the network |
|--------|------------------------------|---------------------------|
| 1870s  | Newspapers (rail delivery), telegraph | Sparse, hub-and-spoke, physically bounded, day-to-week latency |
| 1920s  | Radio becoming a household item | Broadcast, one-to-many, regional-to-national reach |
| 1970s  | Television in most homes | Mass broadcast, high simultaneous reach, low interactivity |
| 1990s  | Early household internet | Bidirectional, narrowband, growing but uneven penetration |
| 2010s  | Always-carried mobile connection | Ubiquitous, multiplexed, near-instant, peer-to-peer + platform |

### 1.2 Restatement of the Assignment

Working as ICM's Information Analytics Division, the task is to **model the relationship
between the speed/flow of information and the inherent value of information** across the
five periods, and then to project that relationship forward. The assignment decomposes into
five stated sub-tasks (a)–(e), restated in Section 2. The deliverable is a set of coupled
models plus explicit documentation of the **assumptions** and **data** used, and a
validation demonstration against known present-day reality.

### 1.3 Restated Deliverable Scope

- A modeling framework that (i) represents information flow over a network and (ii) filters
  or scores what "qualifies as news."
- A reliability demonstration: use historical data to predict the present and compare with
  observed present reality.
- A forward projection of network relationships and capacities around **2050**.
- A mechanism model of how public interest and opinion can be shifted through modern
  information networks.
- A synthesis of how **information value, initial opinion/bias, message or source form, and
  network topology/strength** jointly govern the spread of information and influence.

---

## 2. Objectives and Subproblems

### 2.1 Primary Objective

To build an integrated, historically grounded, and validation-tested modeling framework that
quantifies how the **value** and **flow speed/reach** of information co-evolve with
communication network technology, and to use that framework for retrospective explanation,
present-day verification, and forward projection (including a ~2050 scenario).

### 2.2 Subproblem Map (statement task → modeling objective)

| Task | Modeling objective | Planned output form |
|------|--------------------|---------------------|
| (a) | Build a flow model + a newsworthiness/filtering model | Coupled diffusion model and a news-value scoring/classification model |
| (b) | Backtest: historical calibration → predict "today" → compare with reality | Retrospective validation harness and error/agreement report (future execution) |
| (c) | Project network relationships and capacities to ~2050 | Scenario-based extrapolation of connectivity, bandwidth, and adoption saturation |
| (d) | Model opinion/interest change via today's networks | Opinion-dynamics + influence-propagation model on modern topologies |
| (e) | Decompose the effects of value, bias, message/source form, topology | Sensitivity/factorial analysis over the coupled model's drivers |

### 2.3 Cross-Cutting Requirements

- **Assumption register**: every assumption will be recorded, justified, and tagged as to how
  it can be tested.
- **Data provenance ledger**: every input series will be linked to its source and period.
- **Reproducibility**: all planned steps will be specified so a future solver can execute
  them deterministically.

---

## 3. Assumptions

Assumptions are grouped by role. Each will be justified and paired with a future validation
approach. These are *planned* assumptions; they will be revised once data is assembled.

### 3.1 Scope and Period Assumptions

- **A1 — Five discrete regime snapshots.** The five periods will be treated as representative
  "technology regimes," with each regime summarized by a characteristic network topology and
  a characteristic transmission latency. *(Justification: clean comparison across eras.
  Validation: test whether model outputs are sensitive to regime boundary placement.)*
- **A2 — Path dependence is second-order.** Within a regime, the network will be assumed
  quasi-static over the short horizon of a single news event. *(Validation: compare against
  cases where network structure changed mid-event.)*
- **A3 — Cross-period comparability.** "News value," "reach," and "speed" will be defined on
  **normalized, dimensionless scales** so eras can be compared despite differing absolute
  population and technology. *(Validation: re-scale alternatives; check ranking stability.)*

### 3.2 Information-Flow Assumptions

- **A4 — Population homogeneity within a node class.** Individuals will be aggregated into
  compartments or agent classes rather than modeled one-to-one at world scale.
  *(Validation: compare aggregate vs. sampled agent simulation.)*
- **A5 — Transmission is probabilistic per contact opportunity.** Spreading will be modeled as
  a stochastic process governed by a per-contact transmission probability and a contact-rate
  parameter that is regime-specific. *(Validation: fit to historical adoption/reach curves.)*
- **A6 — Limited attention / carrying capacity.** Each node will have finite capacity to
  process information, implying saturation dynamics. *(Validation: compare logistic vs.
  unbounded growth fits.)*
- **A7 — Value modulates transmission but does not fully determine it.** High-value items will
  be assumed to spread faster/further, but with diminishing marginal returns.

### 3.3 Value / Newsworthiness Assumptions

- **A8 — Newsworthiness is multi-dimensional and observable through proxies.** Candidate
  dimensions (novelty/surprise, impact, prominence, proximity, emotional valence, conflict,
  timeliness) will be proxied by measurable features.
- **A9 — "Qualifies as news" is a filtering/threshold decision** — modeled both as a
  rule/threshold and as a probabilistic classifier.
- **A10 — Value is partially subjective** and depends on the receiving population's prior
  state; it will be modeled as context-dependent rather than absolute.

### 3.4 Opinion / Influence Assumptions

- **A11 — Opinions live on a bounded continuum** (e.g., a normalized belief axis) with
  possible bias/anchoring toward an initial position.
- **A12 — Update rules are local**: agents revise opinions primarily through network
  neighbors and trusted sources, with a possible confirmation-bias weighting toward
  like-minded sources.
- **A13 — Message form and source credibility act as multiplicative amplifiers/attenuators**
  on transmission and persuasion.

### 3.5 Projection Assumptions (to ~2050)

- **A14 — Technology adoption follows a saturating diffusion pattern** (e.g., logistic/Bass),
  so extrapolation beyond observed data will be handled with bounded, scenario-based curves.
- **A15 — No unforeseeable paradigm rupture is modeled as the base case**; alternative
  "disruption" scenarios will be carried separately rather than folded into the central path.

### 3.6 Justification and Future Validation Approach (summary)

Each assumption above will be justified by (i) domain plausibility from communication
theory, (ii) traceability to the sample data sources, and (iii) the degree to which it
simplifies an otherwise intractable model. Future validation will use: regime-boundary
perturbation tests, aggregate-vs-agent comparison, alternative functional forms for growth
and transmission, and explicit sensitivity ranking (see Section 7).

---

## 4. Data Processing Plan

> No data is currently staged. The plan below describes the dataset that **will be
> assembled**; it is a construction blueprint, not an analysis.

### 4.1 Data Sources to Assemble

**A. Sample sources named in the addendum (primary candidates):**

- Newspaper circulation trends over ~60 years (media-cmi / industry reports).
- BBC technology piece on media/technology availability.
- Scottish Government publication on communications/media availability.
- MIT Technology Review: smartphone adoption speed.
- Facebook newsroom statistics (reach/connected users).
- Poynter / Pew: TV vs. digital vs. print/radio news consumption.
- Pew Research: "Watching, Reading and Listening to the News" (media-consumption shares).
- The Conversation: "Hard evidence — how false information spreads online."
- Historical/media-communication references (Quora, Lardbucket primer, First Monday).

**B. Standard public statistical series to supplement (to be confirmed against licensing
and accessibility):** ITU (telecom/ICT indicators), World Bank (population, urbanization,
income), UNESCO (literacy, media), national census/statistical offices (newspaper, radio,
TV, internet, mobile penetration by decade), and network-measurement literature for modern
topology parameters.

**C. Event case studies (for calibration/illustration, not results):** paired events of
comparable "value" in different eras — e.g., an assassination-type event in the 1860s vs.
an analogous event today; and a purely entertainment/trivial item — to anchor the
speed-vs-value relationship.

### 4.2 Data Organization

- **Period panel table** — one row per (period × region/scope) with columns for channel
  availability, penetration, typical latency, interactivity, and source credibility.
- **Adoption time series** — per-technology cumulative adoption curves (newspaper, radio,
  TV, internet, mobile) to support diffusion fitting.
- **News-consumption shares** — media mix per period.
- **Event feature table** — per historically documented event: era, a value/newsworthiness
  feature vector, observed reach proxy, and observed time-to-reach proxy.
- **Modern network snapshots** — structural statistics (degree distribution, clustering,
  path length, community structure) for 2010s topologies.

### 4.3 Preprocessing Steps (planned)

1. **Source ingestion & documentation**: record source, year, unit, and scope for each series.
2. **Harmonization**: align units (per-capita vs. absolute), geographic scope, and time
   granularity (decade → annual where possible).
3. **Normalization**: min–max or z-score to dimensionless comparative scales (per A3).
4. **Missing-data policy**: define interpolation for interior gaps and explicit exclusion or
   imputation-with-flag for sparse eras; quantify remaining uncertainty.
5. **Outlier/anomaly handling**: document outliers (wars, depressions, regulatory shifts)
   and decide, per case, to keep (as regime context) or down-weight.
6. **Unit-consistency checks**: cross-source triangulation where two sources overlap.
7. **Provenance ledger**: every processed series traceable to its raw source.

### 4.4 Feature Construction (planned)

- **Value/newsworthiness features**: novelty/surprise proxy (information-theoretic), impact
  proxy, prominence/authority, geographic/social proximity, sentiment/emotional arousal,
  conflict/threat, timeliness.
- **Flow features**: contact rate, transmission probability, reach fraction, time-to-peak,
  half-life, cascade size/breadth.
- **Network features**: degree centrality, betweenness, clustering coefficient, average path
  length, community modularity, assortativity (homophily), tie strength.
- **Opinion features**: initial mean/variance of belief, polarization index, bias parameter,
  confidence bound.

### 4.5 Data Usage Strategy

- **Calibration split**: earlier periods/events for parameter estimation.
- **Validation split**: later periods held out for backtesting (Section 7).
- **Scenario inputs**: separate forward-looking parameter ranges for 2050 (Section 5.5).

---

## 5. Candidate Model Framework

The framework will be **multi-layer and coupled**: a *network substrate*, a *flow/diffusion
layer*, a *value/filtering layer*, and an *opinion/influence layer*, with a *projection
layer* on top.

### 5.1 Network Substrate Models (per period)

| Candidate | Idea | Advantages | Limitations |
|-----------|------|-----------|-------------|
| Lattice / regular graph | Uniform local connectivity | Simple; analytic tractability | Unrealistic for modern networks |
| Erdős–Rényi random graph | Independent random ties | Baseline for comparison | No clustering/hubs |
| Watts–Strogatz small-world | High clustering + short paths | Captures "six degrees" behavior | Static; uniform rewiring |
| Barabási–Albert scale-free | Preferential attachment → hubs | Reproduces influencer hubs | Idealized growth history |
| Empirical / multilayer networks | Measured or reconstructed topologies | Realistic for 2010s | Data-hungry; harder to generalize |

**Plan:** map each historical period to an appropriate substrate family (sparse
hub-and-spoke → broadcast star/clique mix → scale-free + multilayer for the 2010s) and use
the same diffusion layer across substrates to isolate topology effects.

### 5.2 Information-Flow / Diffusion Layer

- **Compartmental epidemic models**: SIR/SIS, extended to SEIZ or analogous
  "susceptible–exposed–skeptic–infected" variants to represent belief, skepticism, and
  non-adoption — well suited to aggregate, era-scale flow.
- **Cascade models**: Independent Cascade (IC) and Linear Threshold (LT) for event-level,
  node-resolved spread; supports influence-maximization analysis.
- **Threshold/Complex-contagion models**: for cases requiring multiple exposures.
- **Bass / logistic diffusion**: for technology adoption and the slow emergence of a channel.
- **Information-theoretic flow**: entropy/surprise definitions to link "value" to an
  intrinsic spreading propensity; graph-based flow/random-walk formulations for speed.

**Coupling idea (to be formalized):** a transmission rate that is an increasing,
diminishing-returns function of the item's value score, modulated by source credibility and
message form, and scaled by regime-specific contact rates.

### 5.3 Value / Newsworthiness ("Filter") Layer

- **Rule/threshold filter**: a weighted, normalized newsworthiness index with a
  decision threshold.
- **Probabilistic classifier**: logistic/regularized linear model (with a possible
  nonlinear extension) mapping the value feature vector to a "news vs. non-news" or priority
  score — interpretable coefficients are important for task (e).
- **Information-theoretic "surprise"** measure as an intrinsic-value proxy, paired with
  prominence and impact terms.
- **Bayesian updating** framing to represent context-dependent value (A10).

### 5.4 Opinion / Influence Layer

- **DeGroot / Friedkin–Johnsen** linear consensus models as baselines.
- **Bounded-confidence (Hegselmann–Krause)** for polarization and echo-chamber effects.
- **Voter / Sznajd** discrete-opinion models.
- **Axelrod cultural dissemination** for multi-attribute opinion.
- **Agent-based models (ABM)** coupling individual bias, source trust, and network position
  — the main vehicle for tasks (d) and (e).
- **Influence maximization** (greedy/CELF-style heuristics on IC/LT) to identify which
  sources/topologies most shift opinion.

### 5.5 Projection Layer (→ ~2050)

- **Bounded extrapolation** of adoption/penetration via saturating curves with uncertainty
  envelopes.
- **Scenario construction** (e.g., high/central/low adoption, plus an explicit
  "technology disruption" scenario) rather than a single point forecast.
- **Capacity modeling**: combine per-channel bandwidth/latency assumptions into a
  projected network-capacity profile.

### 5.6 Variables (planned notation)

- **Network**: adjacency/graph G, degree distribution, clustering C, path length L,
  modularity Q, tie strength w.
- **Flow**: transmission probability β, contact/recovery rates, reach R(t), time-to-peak,
  basic reproduction-like threshold quantity, cascade size.
- **Value**: feature vector v, newsworthiness score N(v), credibility s, message form m.
- **Opinion**: belief x_i, bias b_i, confidence ε, polarization index.
- **Regime parameters**: latency, penetration p, interactivity, capacity.

---

## 6. Implementation Roadmap

> Implementation will occur only in a future solving phase. This section specifies modules,
> algorithms, and workflow so that phase can proceed deterministically.

### 6.1 Planned Technology Stack

- **Language**: Python (scientific stack).
- **Libraries (planned)**: NumPy/SciPy (numeric, ODE fitting), pandas (data handling),
  NetworkX (graph construction/analysis), Mesa or custom (ABM), scikit-learn (classifier),
  matplotlib/plotly (future visualization), SALib or equivalent (sensitivity analysis).

### 6.2 Required Modules

1. `data_ingest` — source readers, provenance ledger, unit harmonization.
2. `feature_build` — value, flow, network, and opinion feature construction.
3. `netgen` — period-specific network generators + empirical loader.
4. `flow` — compartmental ODE + cascade simulator.
5. `value_filter` — newsworthiness index and classifier.
6. `opinion_abm` — opinion-dynamics / influence agent engine.
7. `projection` — adoption extrapolation + scenario engine for ~2050.
8. `validate` — backtesting harness, metrics, sensitivity driver.
9. `report` — future assembly of tables/figures (not produced in this draft).

### 6.3 Workflow

1. Ingest and document sources → build period panel and feature tables.
2. Generate/reconstruct per-period networks.
3. Calibrate flow parameters on earlier periods/events.
4. Fit and validate the value-filter model.
5. Run retrospective backtest (calibrate on past → predict present).
6. Run opinion/influence experiments for tasks (d) and (e).
7. Run projection scenarios to ~2050.
8. Execute sensitivity and uncertainty analyses.
9. Assemble reproducibility package and future report.

### 6.4 Reproducibility Controls

- Fixed random seeds; configuration files for all parameters; versioned data snapshots;
  documented environment; script-per-section layout under `code/` with outputs to
  `results/` and run logs to `logs/`.

---

## 7. Validation Strategy

### 7.1 Evaluation Metrics (planned)

- **Flow layer**: fit error against adoption/reach curves (e.g., RMSE/MAE on normalized
  scales), time-to-peak error, cascade-size distribution distance (e.g., KS or
  log-likelihood on a fitted distribution).
- **Value/filter layer**: classification metrics (accuracy, precision/recall, AUC) and
  ranking quality (e.g., precision@k) against labeled events.
- **Opinion layer**: agreement between simulated and observed opinion trajectories
  (correlation, distributional distance); polarization-index error.
- **Projection layer**: interval coverage and out-of-sample error on already-observed years.

### 7.2 Validation Methods

- **Temporal backtesting (primary for task b)**: calibrate on earlier periods, predict a
  later, already-observed period, compare with reality; iterate in a rolling-origin scheme
  across the five regimes.
- **Hold-out period testing**: reserve at least one period for genuine out-of-sample check.
- **Case-study validation**: reproduce documented spread of selected historical vs. modern
  events; check ordinal predictions (faster/wider today) and relative magnitudes.
- **Cross-topology robustness**: test whether conclusions hold across multiple network
  families, not just one.
- **Cross-model triangulation**: compare aggregate ODE vs. agent-based results; require
  agreement in qualitative directions.

### 7.3 Sensitivity and Uncertainty Analysis (planned)

- One-at-a-time parameter sweeps for interpretability.
- Global sensitivity (variance-based, e.g., Sobol or an equivalent) to rank which inputs —
  value, bias, message/source form, topology, strength — most drive spread and opinion
  change (directly supports task e).
- Scenario envelopes for the 2050 projection (assumption A14/A15).
- Robustness to regime-boundary placement (A1) and normalization choices (A3).

### 7.4 Validity Threats to Track

- Overfitting to sparse historical series.
- Aggregation bias masking network effects.
- Survivorship/selection bias in historical "news" examples.
- Unidentifiable parameters when data is thin.

---

## 8. Expected Result Interpretation

> Interpretive guidance only — no results are computed here.

- **Expected output families (future):** normalized speed/reach curves by period; a
  newsworthiness scoring function with interpretable weights; topology-dependent cascade
  statistics; opinion-trajectory and polarization profiles; bounded ~2050 capacity scenarios
  with uncertainty bands.
- **How they would be read:** higher value and more central sourcing should associate with
  faster/wider spread, with the *strength* of that association being regime-dependent.
  The framework would let one ask comparative questions (e.g., how a high-value item's reach
  and timing differ across eras) rather than assert single numbers.
- **Decision-relevance:** the factor-ranking from sensitivity analysis (Section 7.3) is
  intended to indicate which levers — value, bias, source/message form, or topology —
  most plausibly shift public interest and opinion, informing ICM's communication analysis.
- **Interpretation caveats:** outputs should be read as **model-conditional scenarios**
  within stated assumptions, not as predictions of specific real events.

---

## 9. Limitations and Improvements

### 9.1 Anticipated Limitations

- **Data sparsity and quality** in pre-digital eras; heterogeneous definitions of "news,"
  "reach," and "medium."
- **Aggregation vs. individual dynamics**: compartmental models may miss mesoscale network
  effects; ABMs may be hard to calibrate historically.
- **Parameter identifiability**: value, bias, and credibility may be entangled and hard to
  separate from limited data.
- **Extrapolation risk** to ~2050: adoption and topology may not follow historical patterns.
- **Value subjectivity**: "inherent value of information" is partly socially constructed and
  not fully observable.
- **Causal vs. correlational**: retrospective agreement does not establish causation.

### 9.2 Planned Improvements / Extensions

- Enrich with direct empirical network data and experiment-verified diffusion studies.
- Move toward **multilayer / multiplex** networks reflecting simultaneous channels.
- Introduce **time-varying and adaptive** topologies and tie strengths.
- Add **heterogeneous agent** traits (credibility perception, susceptibility, activity).
- Include **adversarial/misinformation** dynamics and correction mechanisms.
- Adopt **Bayesian / ensemble** calibration to carry uncertainty explicitly into projections.
- Expand validation to additional, independent historical case studies and non-U.S. regions.

### 9.3 Immediate Next Steps (for the future solving phase)

1. Confirm and assemble the data sources listed in Section 4.1; build the provenance ledger.
2. Finalize the value-feature definitions and label scheme for the filter model.
3. Select the initial period-specific network families and generate baselines.
4. Implement the coupled flow + value prototype and the backtesting harness.
5. Implement the opinion/influence ABM and the ~2050 scenario engine.
6. Run the planned validations and sensitivity analyses, then draft the full report.

---

*End of planning draft. This document intentionally contains no computed results, no
executed experiments, and no final conclusions.*
