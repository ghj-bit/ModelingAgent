# Gerrymandering — Initial Modeling Plan Draft

**Problem ID:** `2007_Gerrymandering`
**Title:** Gerrymandering
**Source:** MCM 2007
**Document type:** Modeling blueprint draft (planning only — no solving, no computation, no final results)

> This document is a *roadmap*. It defines objectives, assumptions, candidate models, data handling, implementation steps, and validation strategy for a future modeling effort. It deliberately contains **no computed values, no fitted models, no executed experiments, and no conclusions.**

---

## 1. Problem Background and Restatement

The United States Constitution fixes the size of the House of Representatives and apportions seats to states in proportion to population, but it does not prescribe how each state's congressional districts should be drawn geographically. The absence of a geometric rule has historically produced district shapes that many observers regard as "unnatural," and the drawing process is politically sensitive.

**Restated core question.** Given the authority to redraw a state's congressional districts:

1. Define a principled, defensible notion of a "simple" (compact, natural-looking) district.
2. Construct a districting plan in which **every district contains the same population** (the only explicit hard rule stated in the problem).
3. Provide a **convincing fairness argument** addressed to the voters of the state.
4. Apply the method to the **State of New York** to produce geographically simple districts.

**Interpretation of scope.** The task is a *baseline* exercise: the goal is not to optimize partisan advantage, but to establish a neutral, reproducible reference map driven only by stated geometric and population criteria. "Simple" is left open by the problem and must therefore be defined explicitly, justified to the public, and made operational.

---

## 2. Objectives and Subproblems

### 2.1 Primary objectives
- **O1.** Provide an explicit, articulated definition of "simple"/"compact" districts that is intuitive to voters and mathematically operational.
- **O2.** Build a method that partitions a state into the required number of districts satisfying **equal-population** and **contiguity** rules.
- **O3.** Demonstrate the method on New York State and produce a planned set of geometrically simple districts.
- **O4.** Construct a fair and transparent argument defending the plan to voters (criteria, neutrality, reproducibility).

### 2.2 Subproblems
- **S1 — Defining simplicity.** Translate informal notions (e.g., "normal-looking," "not sprawling") into candidate quantitative measures and select/justify one or a weighted family.
- **S2 — Population equality.** Decide and justify the tolerance for equal-population (exact vs. bounded deviation), given that census geography is discrete and populations are integer.
- **S3 — Geometric partitioning.** Formulate the district-drawing task as an optimization/partitioning problem and select a solution approach.
- **S4 — Contiguity and integrity.** Ensure each district is one connected region and choose whether to respect boundaries (counties, existing neighborhoods, water).
- **S5 — Fairness argument.** Design an evidence strategy (compactness comparisons, neutrality across seeds/parameters, reproducibility) to support perceived fairness.
- **S6 — Application to New York.** Specify how the general method will be instantiated for New York (number of districts, data vintage, geographic resolution).

### 2.3 Intended deliverables
- A written definition of district "simplicity" plus justification.
- A reproducible districting procedure (algorithmic pipeline).
- A planned (not computed) map-quality evaluation framework.
- A New-York-specific application plan.
- A voter-facing fairness narrative structure.

---

## 3. Assumptions

Assumptions are organized as *working assumptions* (taken as given for planning), each with justification and a planned validation approach.

| # | Assumption | Justification | Planned validation approach |
|---|-----------|---------------|-----------------------------|
| A1 | A congressional district can be represented as a union of discrete census geographic units (blocks and/or tracts). | Census data are published on discrete units; continuous geometry is impractical for exact population accounting. | Re-derive at two resolutions (tract vs. block) and compare robustness of results. |
| A2 | Population is attributed to a unit by its census count, and units are treated as atomic (not split mid-unit). | Simplifies equal-population accounting and preserves data integrity. | Compare schemes with/without allowed unit splitting. |
| A3 | Each district must be a single, connected region (contiguity). | "Natural" districts implicitly assume connectivity; disconnected districts are not administrable. | Programmatic connectivity check on the district graph. |
| A4 | Equal population is enforced within a small, explicitly justified tolerance. | Exact integer equality is generally infeasible on discrete units. | Sensitivity analysis over several tolerance levels. |
| A5 | "Simple" can be captured by compactness/regularity measures (e.g., perimeter–area based). | Compactness measures are established, computable, and communicable to voters. | Compare several measures and check they yield consistent rankings. |
| A6 | Land area and interior boundaries are the relevant geometry; large water bodies will be handled by a stated rule. | Coastal/lake geography (Lake Ontario, Lake Erie, Long Island Sound, etc.) distorts naive area/perimeter metrics. | Test alternative water-boundary treatments and observe effect on metrics. |
| A7 | Political neutrality: the baseline plan will not use partisan or demographic criteria as objectives. | The problem asks for a "purely baseline" simple-shape exercise. | Record explicitly which variables are (and are not) in the objective. |
| A8 | A single fixed apportionment year / number of NY districts will be chosen and stated. | District count and population targets depend on census vintage. | Document the chosen vintage; verify consistency of units and counts. |

These are **planning assumptions**; none has been tested in this document.

---

## 4. Data Processing Plan

### 4.1 Data to be acquired
- **Population counts** at the smallest available census geography (blocks; aggregated tracts) for the chosen vintage.
- **Geographic boundaries** (cartographic boundary / TIGER-style polygons) for the same geographies, plus the state outline.
- **Topological adjacency** relationships between neighboring units (shared-edge/touching).
- **Reference maps** of existing congressional districts for comparison purposes only.
- Optional contextual layers: county boundaries, major water bodies, and (for fairness discussion) county/city names.

### 4.2 Preprocessing steps (planned)
1. **Unit selection** — choose the working spatial resolution; specify a fallback if a unit's geometry is missing or degenerate.
2. **Identifier reconciliation** — align population records and geometry by shared geographic identifiers; define a rule for unmatched records.
3. **Interior/exterior boundary handling** — decide how state boundary, coastline, and lake shorelines enter the perimeter measures.
4. **Zero/small-population units** — define treatment for unpopulated or water units (e.g., attach to a neighbor or assign zero weight).
5. **Adjacency graph construction** — build the node (unit) / edge (shared boundary) graph; verify each node's degree; document disconnected components (e.g., islands).
6. **Island / disconnected-component policy** — decide whether islands must be attached to mainland districts and record the rule.
7. **Target population computation** — define each district's ideal population conceptually (state total divided by district count); the precision and tolerance are planning parameters, not yet evaluated.

### 4.3 Feature construction (planned)
- Node weights: population.
- Edge attributes: shared-boundary length (used in compactness proxies and cut penalties).
- Node geometry attributes: area, perimeter, centroid, convex-hull area, circumscribing circle.
- Derived candidate compactness features: perimeter-based ratios and circumscribed-circle-based ratios (formulas to be selected in the framework section).

### 4.4 Data usage strategy (planned)
- A **primary** resolution for the main plan.
- A **secondary** coarser/finer resolution used only for robustness checks.
- A strict separation between *objective inputs* (population + geometry) and *diagnostic inputs* (existing districts, contextual layers) so the baseline remains neutral.

No data will be processed as part of this planning document.

---

## 5. Candidate Model Framework

The districting task will be framed as a **constrained geometric partitioning problem** on a weighted adjacency graph.

### 5.1 Decision variables (conceptual)
- **Assignment variables:** which district each geographic unit is assigned to.
- **Auxiliary/soft variables:** incidence of a unit lying on a district boundary; per-district shape descriptors.
- **Design parameters:** number of districts, population tolerance, compactness measure, boundary-integrity preferences.

### 5.2 Hard constraints
- **C1 Equal population:** each district's population within the stated tolerance of the ideal.
- **C2 Contiguity:** each district induces a connected subgraph.
- **C3 Coverage/partition:** every unit assigned to exactly one district.
- **C4 Non-empty:** each district contains at least the required population mass.

### 5.3 Candidate modeling approaches (to be compared)

**M-A. Compactness-optimal graph partitioning (central candidate).**
Minimize a compactness penalty (a function of district area/perimeter or cut edges) subject to C1–C4. Suitable solution techniques include mixed-integer programming for small instances and heuristic/metaheuristic search (local search, simulated annealing, tabu) for state-scale instances.

**M-B. Region-growing / seed-and-grow.**
Seed district centers, then grow contiguous regions until population targets and compactness criteria are met. Simple and fast; final quality depends heavily on seeding strategy, so multiple seeds will be considered.

**M-C. Geometric tessellation methods.**
Centroidal Voronoi tessellation / Lloyd-style relaxation, or Voronoi partitions on population-adjusted centers, to obtain regular, visually "natural" cells; then snap to the discrete unit graph and repair population/contiguity violations. Strong on visual simplicity, weaker on exact population equality.

**M-D. Spectral / clustering partitioning.**
Graph spectral methods or constrained k-means-style clustering with contiguity post-processing; useful for initializing other methods.

**M-E. Recursive splitting.**
Recursively bisect the state along compact cuts (splitline-style) until the required number of equal-population pieces is reached. Highly reproducible and easy to explain to voters.

**M-F. Ensemble / null-distribution methods (diagnostic).**
Markov-chain-style sampling of the space of valid districting plans (e.g., recombination-style moves) to establish a baseline distribution of compactness. Used to judge whether the proposed plan is typical or unusually simple — not to select the final plan.

### 5.4 Mathematical ideas to be used
- Graph partitioning and minimum-cut objectives.
- Weighted load-balancing under a connectivity constraint.
- Convex-hull / isoperimetric inequalities as the conceptual basis for "compactness."
- Randomized search and multi-start heuristics for large discrete spaces.
- Ensemble/sampling arguments for fairness (placing the chosen plan within a distribution of valid plans).

### 5.5 Advantages and limitations (anticipated)
- **M-A/M-F** are principled and give a defensible fairness argument, but are computationally demanding and sensitive to objective weighting.
- **M-B/M-D** are scalable and easy to run, but the search is heuristic and may need many restarts.
- **M-C** yields visually natural shapes but needs a discrete repair step for exact population/contiguity.
- **M-E** is the most transparent to voters but may be less compact than an optimized plan.
- A **hybrid** strategy (geometric initialization + graph-local optimization + ensemble diagnostic) is anticipated as the leading candidate.

### 5.6 Planned comparison criteria for models
Fidelity to constraints, measured shape simplicity, reproducibility, computational feasibility at NY scale, and communicability to a general audience.

---

## 6. Implementation Roadmap

### 6.1 Modules (to be built)
1. **Ingestion module** — load population and geometry data; reconcile identifiers.
2. **Graph builder** — construct adjacency, node weights, edge lengths; flag islands/disconnected components.
3. **Compactness feature module** — compute candidate shape descriptors for any proposed region.
4. **Partition engine** — implement the chosen model(s) from Section 5 (one primary, several comparators).
5. **Constraint verifier** — check population, contiguity, and partition completeness for any plan.
6. **Diagnostics/ensemble module** — sample valid plans to build a compactness baseline.
7. **Visualization module** — render planned districts and metric summaries for the fairness narrative.
8. **Reporting module** — assemble the voter-facing fairness argument and technical appendix.

### 6.2 Workflow (planned sequence)
1. Acquire and reconcile data → resolve assumptions A1–A4.
2. Build and validate the adjacency graph (connectivity, island policy).
3. Instantiate the primary partitioning model; implement comparator models.
4. Run constraint verification on intermediate plans.
5. Evaluate compactness across models and resolutions.
6. Generate the ensemble diagnostic for the fairness argument.
7. Instantiate the method specifically for New York.
8. Produce the fairness narrative and technical documentation.

### 6.3 Engineering considerations (planned)
- **Reproducibility:** fixed seeds, versioned inputs, deterministic post-processing.
- **Scalability:** NY at block resolution is large; coarser resolution or hierarchical decomposition may be needed first.
- **Configuration:** all soft/hard parameters exposed so alternatives can be compared cleanly.
- **Modularity:** the partition engine interchangeable, so multiple models can be benchmarked on the same graph.

---

## 7. Validation Strategy

### 7.1 Evaluation metrics (planned)
- **Constraint metrics:** maximum per-district population deviation; contiguity (connected components per district); complete coverage.
- **Compactness metrics:** multiple perimeter/area-based ratios and circumscribing-circle-based ratios; convex-hull fill ratio; boundary-length totals.
- **Structural metrics:** number of county/unit splits, number of boundary edges.
- **Fairness/neutrality diagnostics:** comparison to the ensemble compactness distribution; stability of plans across seeds and parameter settings.
- (Fairness-demographic metrics such as partisan-symmetry measures will be considered only as *diagnostics*, consistent with assumption A7.)

### 7.2 Validation methods (planned)
1. **Constraint verification** — programmatic checks on every produced plan.
2. **Metric convergence** — verify that compactness improvements stabilize (no further gains from longer search).
3. **Cross-model comparison** — rank plans from the different models under identical metrics.
4. **Cross-resolution consistency** — confirm results are not artifacts of a single geographic resolution.
5. **Ensemble comparison** — locate the chosen plan relative to a distribution of valid plans.
6. **Human-legibility review** — confirm shapes read as "simple" to a non-expert, supporting the fairness claim.

### 7.3 Sensitivity analysis (planned)
- **Population tolerance** — vary the permitted deviation and observe metric changes.
- **Boundary/water treatment** — vary how coastlines and lakes enter compactness measures.
- **Objective weighting** — vary the trade-off among compactness, cut edges, and boundary integrity.
- **Randomness** — vary seeds and initializations to test stability.
- **Resolution** — vary census unit granularity.

No metric will be computed in this document.

---

## 8. Expected Result Interpretation

*(Interpretation of *anticipated* outputs — not actual findings.)*

- The output will be interpreted as **one defensible baseline plan** among many valid plans, not as a uniquely correct map.
- Compactness scores will be read **relative to the ensemble distribution** and **relative to comparator models**, not as absolute verdicts.
- The equal-population constraint will be reported as a **tolerance statement**, explicitly quantifying the residual deviation.
- Fairness will be argued through **transparency, reproducibility, and neutrality of criteria**, rather than through any claim of political balance.
- The New York application will be presented as a **worked instantiation of the general method**, illustrating how the framework scales from definition to concrete state-level map.

---

## 9. Limitations and Improvements

### 9.1 Anticipated limitations
- **Subjectivity of "simple."** Any compactness measure encodes value judgments; different measures can rank plans differently.
- **Discretization artifacts.** Census-unit granularity limits achievable regularity; unit splitting may be needed for tighter equality.
- **Scalability.** Exact optimization at block resolution may be intractable; heuristics trade optimality for speed.
- **Geographic distortions.** Coastlines, lakes, and islands complicate compactness measurement and contiguity handling.
- **Scope.** Purely geometric criteria may underrepresent representation-related concerns (e.g., community integrity), which are explicitly outside the baseline objective.
- **Model-selection ambiguity.** No single model is uniformly best; results depend on the comparison criteria chosen.

### 9.2 Planned improvements / extensions
- **Multi-resolution and hierarchical** approaches to improve both tractability and fidelity.
- **Ensemble-based fairness standards** (outlier testing, distribution-based comparisons).
- **Interactive review tooling** for voter/stakeholder feedback on candidate plans.
- **Broader metric families** to reduce reliance on any single compactness definition.
- **Extension studies** to other states to test generalizability.
- **Documentation of the boundary between objective criteria and diagnostic criteria** to strengthen the neutrality claim.

---

## Appendix A — Planning Checklist (to be completed in later rounds)

- [ ] Finalize the definition of "simple" and its justification.
- [ ] Fix census vintage, NY district count, and population tolerance.
- [ ] Confirm data acquisition, reconciliation, and adjacency-graph validation.
- [ ] Implement primary and comparator partition models.
- [ ] Build constraint verifier and compactness feature module.
- [ ] Run cross-model, cross-resolution, and ensemble validations.
- [ ] Instantiate the method for New York.
- [ ] Assemble the voter-facing fairness narrative.

*This checklist captures intended future work. Nothing in this draft has been executed, and no results are reported.*
