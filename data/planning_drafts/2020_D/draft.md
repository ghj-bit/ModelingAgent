# Modeling Blueprint Draft — MM-Bench 2020_D (ICM / Huskies Soccer Passing-Network Analysis)

> **Status:** Initial modeling plan draft. This document is a *roadmap for future modeling work*, not a solution. It contains no computed results, no executed analysis, and no final conclusions. All statements are written in future-oriented language.

---

## 1. Problem Background and Restatement

### 1.1 Context

The problem is set in a competitive team-sport setting, which the statement presents as the most informative controlled environment for studying team processes. The Huskies, a soccer (football) team, have engaged the modeling firm *Intrepid Champion Modeling (ICM)* to characterize how complex interactions among players on the field relate to team success. The provided season data cover 38 games against 19 opponents (each played twice), and the statement reports that the dataset spans 23,429 passes among 366 players (30 Huskies, 336 opponents) and 59,271 total game events.

The framing stresses that team success is *more than the additive sum of individual ability*: it emerges from diversity of skills, the balance between individual and collective performance, and the ability to coordinate over time. The analytical setting is therefore a **networked, multi-scale, and dynamical system**.

### 1.2 Core Restatement

Given the three staged data tables (`matches.csv`, `passingevents.csv`, `fullevents.csv`), the planned work will:

1. Construct a **ball-passing network** in which players are nodes and passes are links, and use it to identify network patterns — dyadic and triadic configurations, team formations, and other structural indicators/properties — across **multiple spatial and temporal scales** (micro/pairwise → macro/all players; minute-level → whole-game → whole-season).
2. Define **performance indicators of successful teamwork** beyond points/wins (play-type diversity, coordination, distribution of contributions, adaptability, flexibility, tempo, flow), and build a **model** that captures the structural, configurational, and dynamical aspects of teamwork, clarifying whether strategies are universally effective or opponent-dependent.
3. Translate model insights into **structural strategy advice** for the coach for next season.
4. **Generalize** the findings to the design of more effective teams in broader societal problem-solving contexts, and identify what additional aspects of teamwork a generalized model would need to capture.

### 1.3 Dataset Inventory (structural, as staged)

- `matches.csv` — one record per Huskies match (MatchID, OpponentID, Outcome, OwnScore, OpponentScore, Side, CoachID). This is the **outcome/label and context table**.
- `passingevents.csv` — one record per pass (both Huskies and opponents), with TeamID, Origin/Destination player IDs, period, time, pass subtype, and origin/destination field coordinates on a [0,100]×[0,100] attacking-oriented grid. This is the **primary network-construction table**.
- `fullevents.csv` — one record per game event across all event types/subtypes (Pass, Shot, Duel, Free Kick, Save attempt, Substitution, etc.), with coordinates and, where applicable, destination players. This is the **event-context and outcome (e.g., shots/goals) table**.

Player identifiers encode team and nominal position as `TeamID_<Position><##>` with positions `G`, `D`, `M`, `F`. Coordinates are expressed from the *attacking team's* perspective, which has direct implications for cross-team alignment (see §4).

### 1.4 Deliverables of the Future Modeling Effort

- A reproducible **passing-network construction pipeline** (per match, per team, per time window).
- A **multi-scale structural/pattern characterization** (dyadic, triadic, meso/formation, macro).
- A **performance-indicator suite and teamwork model** linking structure/configuration/dynamics to success.
- A **coaching recommendation framework** derived from the model.
- A **generalization discussion** and specification of missing dimensions required for broad team-performance models.

---

## 2. Objectives and Subproblems

### 2.1 Overall Objective

To build an interpretable, multi-scale, network-based model that explains how the Huskies' passing structure and team dynamics relate to match and season success, and to convert that model into actionable structural strategy guidance — and, at a higher level, into transferable principles for designing effective teams.

### 2.2 Subproblem Decomposition

**Subproblem 1 — Passing-network construction and multi-scale pattern discovery.**
The future work will build directed, weighted (by pass frequency) and typed (by pass subtype) player networks for each match and each team, aggregate them across the season, and analyze:
- *Micro (pairwise/dyadic):* link strengths, reciprocity, pass success, preferred passing partnerships.
- *Triadic:* triad census/motif analysis, triangles, transitivity, local clustering.
- *Meso (group/formation):* communities/modules (positional lines, units), formation reconstruction from average positions, subnetworks per position group.
- *Macro (whole team):* density, centralization, global efficiency, entropy, and network-level shape.
- *Spatial scales:* pitch zones, pass direction/flow fields, between-zone connectivity.
- *Temporal scales:* minute-level windows, half-to-half shifts, whole-game, whole-season trajectory.

**Subproblem 2 — Performance indicators and teamwork model.**
The work will define teamwork-success indicators that go beyond points/wins, will formalize structural, configurational, and dynamical features, and will build a model relating those features to outcomes. Sub-questions will include:
- Which indicator families (diversity, coordination, contribution distribution, adaptability, flexibility, tempo, flow) capture teamwork success?
- Are structural strategies **universally effective** or **opponent-contingent**? This will require opponent-aware modeling (interaction effects / opponent-conditioned coefficients).
- How do instantaneous (per-possession), match-level, and season-level dynamics differ?

**Subproblem 3 — Coaching recommendations.**
The future work will translate fitted relationships into concrete structural strategies (e.g., preferred passing configurations, distribution-of-play targets, tempo/adaptability guidance) framed as *options* conditioned on opponent type, and will flag which changes the network evidence will suggest for next season.

**Subproblem 4 — Generalization to team design.**
The work will discuss how network-derived teamwork principles could transfer beyond sport, and will enumerate the additional dimensions (e.g., task interdependence, communication, knowledge diversity, time pressure, turnover) that a general team-performance model would need to capture.

### 2.3 Dependency Structure Among Subproblems

Subproblem 1 is a prerequisite for Subproblem 2 (features feed the model); Subproblem 2 is a prerequisite for Subproblems 3 and 4 (recommendations and generalizations derive from the model). This defines the phased implementation in §6.

---

## 3. Assumptions

Each assumption is paired with its justification and the future approach for testing/relaxing it.

### 3.1 Data-Generation Assumptions

| # | Assumption | Justification | Future Validation Approach |
|---|-----------|---------------|----------------------------|
| A1 | Each row in `passingevents.csv` represents one attempted pass, and a pass link indicates an *attempted* connection (not necessarily completed). | The table is named "passing events" and includes subtype labels; no explicit success flag is provided in the schema. | Cross-check pass counts against `fullevents.csv` Pass-type records; sensitivity-test analyses using only "completed-looking" passes (destination player present) versus all attempts. |
| A2 | Player IDs are stable within the season, and the team/position encoding in IDs is reliable. | The statement describes the ID scheme as a fixed encoding. | Verify uniqueness/counts (≈30 Huskies, 366 total) and check for any ID reused inconsistently across matches. |
| A3 | `EventTime` is measured within each period, and absolute match time requires reconstructing the second half by adding the first-half duration. | The schema states time is "during the MatchPeriod." | Validate monotonicity of reconstructed time; check boundary behavior around half transitions. |
| A4 | Coordinates are attacking-oriented, so the *same physical direction* may map to different coordinate values for the two teams. | The schema explicitly states the [0,100] frame is from the attacking team's perspective. | Normalize both teams to a common frame and verify home/away and first/second-half orientation consistency. |
| A5 | Match outcomes (win/tie/loss) and scores in `matches.csv` are accurate success labels at match level. | Provided as the official result table. | Use as ground truth; also derive goal events from `fullevents.csv` as a consistency check. |
| A6 | `CoachID` and `Side` are valid contextual covariates that may explain structural variation (e.g., coach change, home advantage). | Included by design in `matches.csv`. | Treat as covariates/controls; test their explanatory contribution. |

### 3.2 Modeling Assumptions

| # | Assumption | Justification | Future Validation Approach |
|---|-----------|---------------|----------------------------|
| A7 | Passing structure is a meaningful proxy for coordination and teamwork. | Passing is the dominant coupling mechanism in soccer and the only explicit interaction data provided. | Triangulate with event-context metrics (shots, possession, duels) from `fullevents.csv`. |
| A8 | Aggregating events into windows (minute, half, match) preserves enough dynamics for comparison across scales. | Continuous tracking is unavailable; event-level aggregation is the natural discretization. | Sensitivity analysis over window length; compare stable findings across granularities. |
| A9 | An observed network feature is informative only relative to an appropriate null/random baseline. | Raw counts conflate volume with structure. | Degree-preserving / volume-matched null models and opponent-matched comparisons (see §7). |
| A10 | Match-level outcomes can be treated as the success signal, with matches as the unit of analysis. | Only 38 matches: this constrains model complexity. | Use regularized/parsimonious models and hierarchical structure to respect the small sample. |
| A11 | Opponent identity modulates the effectiveness of a given structure (i.e., strategies may be opponent-contingent). | The statement explicitly raises this possibility. | Model interaction/conditioning on opponent; report both pooled and opponent-specific effects. |
| A12 | Unobserved factors (player quality, injuries, tactics) are treated as noise/random effects rather than omitted structure. | No direct measurements are provided. | Use random/mixed effects where feasible; acknowledge as a limitation in §9. |

### 3.3 Scope Assumptions

| # | Assumption | Justification | Future Validation Approach |
|---|-----------|---------------|----------------------------|
| A13 | One season of a single team is sufficient to *demonstrate* methodology and derive preliminary structural guidance, but not to claim universal laws. | Data scope as provided. | Frame generalization as hypotheses for future multi-team/multi-season validation (§4 of the problem, §9 here). |
| A14 | "Success" will be modeled primarily via match outcome and goal difference, with secondary process-based success indicators. | Aligns with the stated need for indicators "in addition to points or wins." | Report results across several success definitions for robustness. |

---

## 4. Data Processing Plan

This section describes *what will be done*, not anything computed.

### 4.1 Ingestion and Integration

- Load all three tables with explicit type control (categorical IDs, numeric time/coordinates).
- Join keys: `MatchID` across all tables; (`MatchID`, `TeamID`) for team-scoped views; `OriginPlayerID`/`DestinationPlayerID` for player-level views.
- Build a **master event timeline** by concatenating `passingevents` and the relevant `fullevents` records, ordered by reconstructed absolute time.

### 4.2 Cleaning and Consistency Checks (planned)

1. **Missingness handling:** `DestinationPlayerID` is defined to be NaN for non-pass/non-substitution events; missingness will be treated as *structurally meaningful*, not imputed blindly.
2. **Duplicate/anomaly detection:** check for duplicated event rows, impossible timestamps, and out-of-range coordinates.
3. **Time reconstruction:** define absolute match time per event using period + within-period time, with a documented convention for the half boundary.
4. **Coordinate normalization:** re-express both teams' coordinates in a single physical frame so Huskies and opponents can be compared and overlaid (resolving the attacking-orientation issue in A4). Document the transformation and verify with position sanity checks (e.g., goalkeeper near own goal).
5. **Cross-table reconciliation:** reconcile pass records in `passingevents` against Pass events in `fullevents`; flag and document residual discrepancies.
6. **Team/player parsing:** split player IDs into TeamID and position code; build a player registry with team and nominal position; identify the Huskies roster subset.

### 4.3 Feature Construction (planned feature families)

**Structural (network) features — per match, per team, per window:**
- Degree/strength distributions; in/out weighted degree; centrality measures (degree, betweenness, closeness, eigenvector/PageRank).
- Density, reciprocity, transitivity, global/local clustering, average path length, efficiency.
- Centralization (e.g., Gini/HHI of pass participation) and contribution concentration.

**Configurational (motif/formation) features:**
- Dyadic partnerships (most frequent/weighted links).
- Triad census and triad/triangle motifs; motif z-scores versus null models.
- Community/module structure (Louvain/spectral) and correspondence to position groups.
- Formation reconstruction from average player positions (spatial clustering of player nodes), zone occupancy, and between-zone pass flows.

**Spatial features:**
- Pitch zoning (e.g., thirds/lanes), pass origin→destination displacement vectors, forward/lateral/backward progression, field-zone entropy.
- Pass-type mix (Head/Simple/Launch/High/Hand/Smart/Cross) and its regional distribution.

**Dynamical/temporal features:**
- Tempo: pass/event rate per time window.
- Ball-transition processes: possession-sequence Markov chains; transition matrices between zone/player states.
- Flow/rhythm metrics: burstiness, inter-event time distributions, sequence-length distributions.
- Adaptability/flexibility: magnitude and rate of structural change across windows and halves; responsiveness to game state (leading/trailing).
- Volatility/consistency of network structure across the season.

**Process/outcome context (from `fullevents` and `matches`):**
- Shots, saves, duels, fouls, offsides, substitutions timing; goals and goal difference; home/away; coach.

### 4.4 Normalization and Data-Usage Strategy

- **Volume control:** normalize structural metrics by possession/pass volume so that a team passing more does not mechanically "look" more connected.
- **Comparison baselines:** compare Huskies' features both (a) across their own matches and (b) against the opponent's network in the same match (a natural within-match contrast).
- **Temporal aggregation:** maintain a hierarchy (window → half → match → season) so findings can be reported at each level.
- **Sample discipline:** with 38 matches, features will be pooled/evaluated using cross-validation and dimension control; documented train/test or leave-one-match-out splits will prevent overfitting narratives.

### 4.5 Reproducibility

All processing steps will be scripted and versioned under `code/`, with intermediate artifacts and run logs under `logs/`, so that any downstream result will be traceable to a specific pipeline stage.

---

## 5. Candidate Model Framework

The work will deliberately consider *several* candidate models at each layer, weighing advantages and limitations before selecting.

### 5.1 Layer A — Network Representation

**Candidate A1: Directed weighted multigraph (pass network).**
Nodes = players; directed edge weight = pass count (optionally typed by pass subtype). Advantages: simple, interpretable, supports the full standard network-metric toolkit. Limitations: collapses time and space; loses sequence order.

**Candidate A2: Typed/multiplex network (one layer per pass subtype or per position group).**
Advantages: captures play-type diversity and role structure. Limitations: sparsity.

**Candidate A3: Time-windowed / temporal network sequence.**
A family of networks indexed by time window. Advantages: captures dynamics, adaptability, tempo. Limitations: window-size sensitivity.

**Candidate A4: Sequence/Markov representation of possessions.**
Model ball transfer as a stochastic process over players/zones. Advantages: captures order and flow; supports tempo and rhythm metrics. Limitations: state-space size.

*Plan:* use A1 as the backbone, with A2/A3/A4 as complementary views; report which structural conclusions are stable across representations.

### 5.2 Layer B — Structural / Pattern Analysis

**B1: Motif and triad census with null-model testing** — counts/z-scores of dyadic and triadic configurations versus Erdős–Rényi and degree-preserving randomized baselines. Advantage: identifies over/under-represented coordination patterns. Limitation: needs careful null specification.

**B2: Centrality and centralization** — identify structurally central players/units and whether play is star-concentrated or distributed.

**B3: Community detection and formation reconstruction** — map modules and spatial clustering to tactical units/formations.

**B4: Spatial network overlay** — project pass flows onto the pitch to read progression and zone connectivity.

**B5: Diversity/entropy measures** — Shannon entropy and related indices over pass types, directions, and targets to quantify play-type diversity.

### 5.3 Layer C — Teamwork Performance Model

**Candidate C1: Composite teamwork index (unsupervised).**
PCA/factor analysis or entropy-weighted aggregation over the feature families (diversity, coordination, distribution, adaptability, tempo, flow). Advantages: transparent, reduces dimensionality. Limitations: interpretability of composite; weighting subjectivity. Validation: stability of loadings across matches.

**Candidate C2: Regularized regression / classification of outcomes.**
LASSO/elastic-net or gradient-boosted models mapping features to match outcome or goal difference. Advantages: handles many correlated features, supports feature selection. Limitations: 38 matches → strict regularization and cross-validation required; interpretability handled via coefficients/importance.

**Candidate C3: Hierarchical / mixed-effects model.**
Outcome ~ structural features + (1|Opponent) + (1|Coach) + Side, possibly with random slopes. Advantages: respects the repeated-opponent structure (each opponent faced twice), controls for unobserved opponent quality, allows partial pooling. Limitations: small N per group.

**Candidate C4: Opponent-contingent model.**
Add structural-feature × opponent-type interactions (or opponent-conditioned coefficients) to test universality versus contingency. Advantages: directly answers the "universally effective vs opponent-dependent" question. Limitations: data-hungry; will be explored conservatively.

**Candidate C5: Dynamical-state model (optional/exploratory).**
Hidden Markov model or state-space model over possession/game-phase states to characterize tempo, flow, and adaptability; or a Markov-chain transition model over zones/players. Advantages: captures time-evolving coordination and game-state response. Limitations: estimation complexity on event data.

**Candidate C6: Network-of-networks / graph-embedding approach (alternative).**
Learn player/node embeddings (e.g., spectral or node2vec-style) to summarize roles and compare structures across matches. Advantages: compact, powerful comparison. Limitations: reduced interpretability; used as a complement, not the primary lens.

*Selection philosophy:* prefer interpretable models (B/C1–C4) as primary, using more complex models (C5–C6) as robustness/complementary checks. Model complexity will be constrained by the 38-match sample size.

### 5.4 Success/Label Definitions (to be modeled)

- Primary: match outcome (win/tie/loss) and goal difference.
- Secondary process indicators: shots/efficiency from `fullevents`, progression into dangerous zones, possession control.
- Season-level: aggregate success, consistency, and trajectory.

---

## 6. Implementation Roadmap

### 6.1 Tooling (planned)

- Language: Python. Data: `pandas`, `numpy`. Networks: `networkx` (primary), with `graph-tool`/`igraph` considered for motif/community performance. Statistics/ML: `scipy`, `statsmodels`, `scikit-learn`. Visualization: `matplotlib`/`plotly`. Reproducibility: scripts + config files.

### 6.2 Module Breakdown (placed under `code/`)

1. `ingest` — load and type the three tables; build master event timeline.
2. `clean` — missingness handling, time reconstruction, coordinate normalization, reconciliation, player registry.
3. `network_build` — construct per-match/per-team/per-window networks (A1–A4).
4. `structure` — centrality/centralization, motif & triad census with null models, community detection, formation reconstruction.
5. `spatial` — zoning, flow fields, progression, pass-type regional mix.
6. `temporal` — tempo, Markov transitions, burstiness, adaptability/flexibility metrics.
7. `features` — assemble the normalized feature store across scales.
8. `models` — composite index, regularized regression, mixed-effects, opponent-contingent, dynamical-state (C1–C6).
9. `validate` — CV, null-model tests, sensitivity analyses, robustness checks.
10. `report` — automated tables/figures and narrative-ready summaries for the final write-up.

### 6.3 Phased Workflow

- **Phase 0 — Scaffolding:** set up `code/`, `logs/`, configuration, and reproducibility conventions.
- **Phase 1 — Data integration & QC:** implement §4.1–4.2; produce a clean event dataset and player registry.
- **Phase 2 — Network construction:** implement §4.3 networks (A1–A4).
- **Phase 3 — Structure/pattern analysis:** implement B1–B5 with null-model testing.
- **Phase 4 — Feature store:** assemble and normalize multi-scale features (§4.4).
- **Phase 5 — Teamwork modeling:** implement C1–C4, then exploratory C5–C6.
- **Phase 6 — Validation:** execute §7.
- **Phase 7 — Interpretation & recommendations:** produce coaching guidance and generalization discussion.

### 6.4 Engineering Conventions

- Every stage writes versioned intermediate artifacts to `logs/`/`results/`.
- All randomness (null models, embeddings, CV splits) is seeded and recorded.
- Parameters (window size, edge thresholds, cluster counts, regularization strengths) live in config, not hard-coded, to support sensitivity analysis.

---

## 7. Validation Strategy

### 7.1 Network-Structure Validation

- **Null models:** compare observed motif counts, clustering, and centralization against Erdős–Rényi, configuration-model, and degree-preserving randomized graphs. Report z-scores/p-values.
- **Volume controls:** re-run structural comparisons on volume-normalized or possession-matched data.
- **Cross-representation stability:** confirm conclusions hold across A1–A4.

### 7.2 Model Validation

- **Cross-validation:** k-fold and leave-one-match-out for predictive models; report AUC/accuracy/log-loss/calibration for classification and R²/MAE for continuous outcomes.
- **Regularization & selection:** nested CV for hyperparameters; report selected features and stability.
- **Hierarchical diagnostics:** mixed-model residual checks; variance components for opponent/coach random effects.
- **Baseline comparison:** benchmark against naive baselines (majority class, score-only, volume-only) to demonstrate incremental value of structural features.

### 7.3 Robustness and Sensitivity Analysis

- Window length (minute-level vs half vs match); pitch-zone granularity; edge-weighting scheme (count vs success-weighted); minimum-pass thresholds for edges; number of communities/formation clusters; composite-index weighting scheme; success-label definition.
- Report which findings are **invariant** versus **parameter-sensitive**.

### 7.4 External / Face Validity

- Sanity-check reconstructed formations and roles against soccer domain knowledge (e.g., goalkeeper/defensive/midfield/forward structure).
- Check consistency of dynamical conclusions against known soccer phenomena (e.g., tempo shifts, game-state effects).
- Where possible, frame recommendations so they can be reviewed by the coach/domain expert (qualitative validation).

### 7.5 Opponent-Contingency Testing

- **Universality test:** does a structural strategy's coefficient remain stable across opponents (pooled vs opponent-conditioned)?
- **Counter-strategy test:** examine whether opponent structural features moderate the Huskies' structure→success relationship (interaction terms).
- Report effect sizes with uncertainty; avoid over-claiming from small per-opponent samples.

---

## 8. Expected Result Interpretation

This section describes *how outputs will be read*, without asserting any outcome.

### 8.1 Structural Findings

- Motif/triad z-scores will be interpreted relative to random baselines: over-represented triads will be read as signature coordination patterns; under-represented ones as avoided configurations.
- Centralization and contribution-distribution metrics will be interpreted along a "star-dependent ↔ distributed" axis, informing whether the Huskies rely on a few hubs or spread play.
- Community/formation reconstruction will be read as emergent tactical shape, to be compared across matches and opponents.

### 8.2 Performance-Indicator Findings

- Composite index and regression coefficients (with uncertainty) will be interpreted as the structural/process features most associated with success, with explicit caution about correlation versus causation.
- Opponent-contingent results will be read as either *universal* (stable across opponents) or *adaptive* (context-dependent), directly answering the statement's universality question.

### 8.3 Coaching Recommendations

- Recommendations will be framed as **structural strategy options** (configuration, distribution, tempo, adaptability targets), each tied to the evidence and to the opponent context in which it is expected to help; each will carry an explicit confidence/limitation note.

### 8.4 Generalization

- Transferable principles (e.g., diversity, balance of individual/collective contributions, temporal coordination) will be presented as *hypotheses* for broader team design, with a companion list of dimensions a generalized model must add (task interdependence, communication, knowledge/skill diversity, time pressure, membership turnover, feedback loops).

### 8.5 Reporting Discipline

- Every reported pattern will be accompanied by its null-model/sensitivity context and its uncertainty, to avoid over-interpretation from a single team-season.

---

## 9. Limitations and Improvements

### 9.1 Data Limitations

- **Single team, single season (38 matches):** limits statistical power and external validity; per-opponent conclusions will be fragile.
- **No physical/tracking data:** positioning between events, off-ball movement, and pressure are unobserved; only event endpoints are known.
- **No player-quality/fitness/injury/lineup metadata:** player identity is purely positional.
- **Pass attempts vs completions ambiguity:** success semantics depend on how pass records are interpreted.
- **Coordinate orientation complexity:** requires careful normalization; residual misalignment could bias spatial features.

### 9.2 Methodological Limitations

- **Aggregation loses microstructure:** windowing may hide rapid coordination.
- **Network metrics can conflate volume with structure** unless normalized (handled via §4.4/§7.1).
- **Composite indices embed weighting choices** (addressed via sensitivity analysis).
- **Causal inference is not guaranteed:** associations between structure and success may be confounded by opponent strength, game state, or tactics.
- **Small-N model complexity:** advanced models (C5/C6) risk overfitting and will be used conservatively.

### 9.3 Planned Improvements / Extensions

- Extend to **multiple teams/seasons** to test universality of findings.
- Incorporate **tracking/positional and pressure data**, expected-goals-style value, and lineup/quality covariates.
- Add **explicit game-state conditioning** (score, time remaining) and **in-game adaptation modeling**.
- Explore **causal/structural modeling** (e.g., instrumental or temporal-precedence designs) for stronger claims.
- Build a **transferable team-performance framework** spanning sports and non-sports team settings, enumerating the additional constructs (communication, diversity, interdependence) required.

### 9.4 Cross-Cutting Caveat

Because the entire plan operates on a single team-season, all structural conclusions will be presented as *evidence-based hypotheses and decision support*, not as validated universal laws. Cross-domain generalization (Subproblem 4) will be offered as a structured research agenda rather than a proven result.

---

*End of initial modeling blueprint draft. No data were analyzed, no models were fitted, and no results were produced in the preparation of this document.*
