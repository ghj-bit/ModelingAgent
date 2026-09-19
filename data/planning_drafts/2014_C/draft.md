# Modeling Plan Draft — MM-Bench 2014_C
## Influence and Impact in Research and Non-Research Networks

**Problem ID:** 2014_C  ·  **Source:** MM-Bench / ICM 2014 Problem C
**Document type:** Modeling blueprint draft (planning only — no solutions, no data analysis, no computations)
**Status:** Initial roadmap for future modeling work

> **Scope note.** This document is deliberately future-oriented. It specifies *what will be built, why, and how it will be validated*. It contains no fitted models, no computed metrics, no network statistics, and no conclusions. All quantities named below are objects to be constructed at a later stage.

---

## 0. Working Context Note (data availability)

The problem statement references source material by URL rather than shipping a numerical table:

- `Erdos1.htm` — the Erdős co-author listing (approx. 510 co-authors of Paul Erdős; the statement cites the Oakland ENP file `https://files.oakland.edu/users/grossman/enp/Erdos1.html`).
- `NetSciFoundation.pdf` — an optional list of candidate foundational network-science papers.

The current staging directory (`output/data/`) is **empty**, and the benchmark's `dataset_path`/`dataset_description` fields are **empty objects**. This is consistent with the problem being a *data-acquisition-and-modeling* task rather than a fixed-tabular-data task. Therefore the data plan below treats **source acquisition, parsing, and entity resolution of the Erdős co-author listing as a first-class modeling subproblem**, not as a given. (This section will be revisited and updated once files are staged or fetched.)

---

## 1. Problem Background and Restatement

Academic influence is commonly quantified through citation and co-authorship networks. Co-authorship of a manuscript typically signals a strong influential link between researchers. Paul Erdős is an extreme case: a prolific collaborator whose co-author network is so large that "Erdős numbers" are used as a proximity index within mathematics.

The ICM 2014 Problem C asks a team to **analyze influence and impact in research networks and in other areas of society**, structured as six deliverables:

1. **Build the Erdős-1 co-author network.** Construct the network of approximately 510 researchers who co-authored a paper with Erdős, **excluding Erdős himself**. The raw listing reportedly exceeds 18,000 lines; only links among the Erdős-1 set are retained (links to people outside that set are discarded). Then **analyze the structural properties** of the resulting network. Where necessary, the network may be **restricted in size** purely to calibrate an influence-measurement algorithm.
2. **Develop network-based influence measure(s)** that identify which Erdős-1 members are most influential *within the network*, interpreted as (a) authors of important works and/or (b) connectors of important researchers — with Erdős explicitly absent from all roles.
3. **Measure influence of research papers.** Select a foundational set of network-science papers (from the attached list and/or discovered ones), build their influence (co-authorship and/or citation) networks, and develop a model that ranks their relative influence; identify the most influential paper and justify the reasoning. Then extend the discussion to measuring the role/influence of an **individual researcher**, a **university/department**, and a **journal**, including what data would be needed.
4. **Transfer the algorithm to a different influence domain** (e.g., songwriters, bands, actors, directors, journalists, novelists, bloggers, or another chosen dataset), optionally restricted by genre, geography, or size.
5. **Discuss the science, understanding, and utility** of modeling influence/impact in networks, including decision-oriented use cases (e.g., choosing collaborators to grow influence quickly, or selecting a graduate school/advisor).
6. **Write a report (≤20 pages, excluding summary sheet)** covering methodology, network-based measures, results, and honest treatment of strengths, weaknesses, and sensitivity.

**Restatement in planner terms:** the deliverable is a *reusable, transferable influence-and-impact measurement framework* over attributed relational data, demonstrated on a hand-built Erdős co-authorship graph and then re-instantiated on a second, deliberately different domain.

---

## 2. Objectives and Subproblems

### 2.1 Top-level objective
Design a coherent methodology that (i) reconstructs and characterizes a curated co-authorship network, (ii) defines and computes defensible influence measures for nodes, edges, groups, and artifacts (papers/venues/institutions), and (iii) demonstrates generality by transferring the same measurement stack to a second domain.

### 2.2 Subproblem decomposition

| ID | Subproblem | Core question to be answered later |
|----|-----------|-----------------------------------|
| SP-1 | **Data acquisition & entity resolution** | How will the Erdős co-author listing be parsed into a clean node set and an incidence list, given messy HTML/HTML-like text and name-variant ambiguity? |
| SP-2 | **Network construction** | How will the Erdős-1 induced subgraph be constructed, and how will edge weights (counts of co-authored papers, recency, strength) be defined? |
| SP-3 | **Structural characterization** | Which descriptive and structural properties (degree distributions, connectivity, components, clustering, path structure, assortativity, core–periphery) will be estimated? |
| SP-4 | **Node-level influence model** | Which centrality/importance measures (and combinations) will quantify an Erdős-1 member's influence, and how will they be validated against external proxies? |
| SP-5 | **Paper-level influence model** | How will a citation/co-author network over a foundational paper set be built and ranked, and what makes one paper "most influential"? |
| SP-6 | **Group/organization-level influence** | How will influence of researchers, departments/universities, and journals be defined from the same primitives? |
| SP-7 | **Cross-domain transfer** | How will the pipeline be re-instantiated on a second domain without domain-specific hard-coding? |
| SP-8 | **Interpretation & decision support** | How will the measures translate into actionable guidance (collaborator selection, advisor/school choice), and what are their epistemic limits? |

### 2.3 Planned deliverables (future artifacts)
- A reproducible **data-to-graph pipeline** (parsing → entity resolution → graph build).
- A **measure library** covering node, edge, subgraph, and artifact-level influence.
- A **transferability demonstration** on one non-academic domain.
- A **validation package** (baselines, perturbation tests, sensitivity sweeps).
- A **report** (≤20 pages) with a summary sheet, structured to the six ICM deliverables.

---

## 3. Assumptions

Each assumption is stated with a justification and the validation step that will later test or relax it.

### 3.1 Modeling assumptions
- **A1 — Co-authorship ⇒ undirected link.** Two Erdős-1 researchers will be linked if they co-authored at least one paper together; the link is undirected. *Justification:* co-authorship is symmetric. *Later validation:* test a directed/weighted-asymmetric variant where seniority or ordering encodes direction.
- **A2 — Erdős excluded entirely.** Erdős will be removed as a node, and the graph will be the **induced subgraph** on Erdős-1 members. *Justification:* the statement explicitly requires this, because Erdős would otherwise dominate every centrality. *Later validation:* compare induced-subgraph results against a "star-removed" baseline to confirm robustness.
- **A3 — Node identity = researcher.** Each researcher is one node; the ~510 figure is the approximate target universe. *Justification:* required node definition. *Later validation:* sensitivity to the exact node count after entity resolution.
- **A4 — Edge strength semantics.** Edge weights will be defined as a monotone function of shared-publication count (and possibly recency or paper significance). *Justification:* multiple co-authored papers imply a stronger tie. *Later validation:* compare binary vs. count-weighted vs. recency-decayed results.
- **A5 — Bounded calibration is acceptable.** A reduced-size subnetwork will be permitted for algorithm calibration. *Justification:* statement grants this latitude. *Later validation:* confirm calibration conclusions hold after scaling to the full network.
- **A6 — "Influence" is multi-dimensional.** No single scalar will be assumed sufficient; influence will be treated as a vector of separately interpretable components (reach, brokerage, prestige, productivity proxies). *Justification:* the problem asks for measures that capture both importance of works and connective role. *Later validation:* assess agreement/disagreement across components via rank correlation.
- **A7 — Foundational paper set is flexible.** The candidate paper list will be treated as a seed, not a closed set; the set may be augmented by clearly relevant discovered works. *Justification:* statement explicitly allows "papers you discover." *Later validation:* test ranking stability under set expansion/contraction.
- **A8 — Transfer domain is chosen, not prescribed.** The second domain will be selected for data availability, clarity of "collaboration/link" semantics, and comparability of the measurement stack. *Justification:* statement offers an open menu. *Later validation:* document why the chosen domain stresses the same constructs (nodes, ties, artifacts).
- **A9 — Citations are a noisy proxy for influence.** Where citation data is used, it will be treated as a proxy subject to field, age, and coverage biases. *Justification:* standard bibliometric caveat. *Later validation:* bias-adjustment or normalization checks.

### 3.2 Assumptions about data provenance
- **A10 — Source fidelity.** The Erdős-1 listing and paper list will be used as documented, with any acquisition/transcription uncertainty logged. *Later validation:* cross-check against a second snapshot of the same source if retrievable.
- **A11 — Sanctioned access.** Any external data acquisition will respect source terms, rate limits, and licensing; no restricted scraping. *Later validation:* provenance log per data field.

---

## 4. Data Processing Plan

*(Planning only — describes the future pipeline, not executed steps.)*

### 4.1 Source acquisition (SP-1)
- **Primary:** obtain `Erdos1.htm` (or the ENP HTML page) and the optional `NetSciFoundation.pdf`; record retrieval timestamp, URL, and checksum for reproducibility.
- **Fallback:** if a file is unavailable, plan for an equivalent public snapshot of the same listing, clearly flagged as a substitute.
- **Provenance ledger:** a table mapping every downstream artifact to its raw source and transformation stage.

### 4.2 Parsing the co-author listing (SP-1)
- Convert HTML/HTML-like text to a structured **line-oriented intermediate records** format.
- Identify the atomic unit of a record: most likely **(anchor author, co-author list per paper)** blocks; determine whether each line encodes an author→co-author pair, a paper→co-author list, or an author→paper list.
- Extract candidate **author name strings** and any embedded metadata (paper titles, years, journal hints) if present.
- Robustly handle: encoding artifacts, nested markup, footnotes, entries for people outside the Erdős-1 set, and duplicated lines.
- **Output (planned):** a normalized `pairs` or `paper→author-set` table plus a `discarded` log for out-of-universe entries.

### 4.3 Entity resolution of researcher names (SP-1, critical)
Because co-author listings are notorious for name ambiguity, this stage will define an explicit, auditable resolution policy:
- **Canonicalization:** unify initials/accents/abbreviation variants; strip honorifics and suffixes.
- **Blocking:** group candidate duplicates by surname + initial pattern to keep comparisons tractable.
- **Matching rule hierarchy:** (i) exact-match after canonicalization; (ii) rule-based merges for well-known equivalences; (iii) optionally a string-similarity score with a conservative threshold; (iv) a manual override list for known homonyms/homographs.
- **Universe restriction:** keep only nodes belonging to the Erdős-1 set; route all others to the discard log.
- **Audit:** produce a `merge_decisions` table (kept/split/merged + reason) so decisions are reviewable and reversible.
- **Sensitivity:** the node set will be built under ≥2 resolution settings (strict, lenient) so downstream influence rankings can be tested for identity-resolution sensitivity.

### 4.4 Network construction (SP-2)
- **Node set:** resolved Erdős-1 researchers (Erdős excluded).
- **Edge set:** induced-edges among the node set where a shared-publication event exists.
- **Edge weight candidates:** binary; co-publication count; count with recency decay; count weighted by estimated paper significance.
- **Representations to plan for:** adjacency list, sparse adjacency matrix, edge list with weights and evidence references, and a companion **hypergraph / bipartite** representation (author–paper incidence) so that both pairwise-network and incidence-based analyses remain available.
- **Self-loops and multi-edges:** collapse multi-edges into weights; forbid self-loops.

### 4.5 Structural feature construction (SP-3)
Descriptive and structural features to be computed later (definitions only, values deferred):
- Degree and strength summaries; degree distribution shape (and its tail behavior).
- Connected components (largest component size, fragmentation).
- Local clustering / transitivity; triangles.
- Distance structure: diameter, average shortest path, eccentricity (with component caveats).
- Degree/strength assortativity; mixing patterns.
- Core–periphery and k-core decomposition.
- Weight–topology relationship (do weighted ties concentrate in a core?).

### 4.6 Foundational-paper and metadata tables (SP-5)
- Build a **paper register** from the seed list: title, authors, venue, year, and (where obtainable) a stable identifier (DOI/URL).
- Plan a **citation-edge table** (paper → citing paper) and/or a **co-authorship-of-paper-authors** projection.
- Record coverage limitations explicitly (which papers lack retrievable citation or author data).

### 4.7 Second-domain data plan (SP-7)
- Choose a domain with naturally **bipartite** structure (e.g., people↔works: writers↔songs/books, actors↔films, directors↔films).
- Apply the **same** parsing → entity resolution → graph build → measure stack to prove transferability.
- Restrict by genre/geography/size for tractability, and document the restriction criteria.

### 4.8 Data quality and integrity controls
- Duplicate-line detection and de-duplication with logged counts.
- Missingness profiling per field; explicit "unknown" handling.
- Consistency checks (e.g., every edge references two in-universe nodes).
- Freeze a **versioned snapshot** of each processed table to enable exact re-runs.

---

## 5. Candidate Model Framework

*(Model families under consideration — no fitting performed.)*

### 5.1 Network representation layer
- **Graph model:** undirected (and optionally weighted) simple graph \(G=(V,E,w)\); Erdős excluded; plus a **bipartite incidence model** \(B=(A \cup P, E_B)\) linking authors \(A\) to papers \(P\), from which \(G\) is the one-mode projection.
- **Why both:** the bipartite view avoids double-counting artifacts of projection and supports "important works" reasoning; the projection is the natural substrate for classic centralities.

### 5.2 Node-level influence measures (SP-4)
Candidate families, to be selected and combined later:
- **Degree / strength** — connectivity volume.
- **Closeness centrality** — average proximity to others (component-aware).
- **Betweenness centrality** — brokerage / bridging role between other researchers.
- **Eigenvector / PageRank-style centrality** — recursive prestige within the network.
- **Katz / Bonacich-style measures** — attenuated-walk influence with a tunable decay (Bonacich's family is explicitly suggested by the source list).
- **Core/periphery and k-core membership** — embeddedness in the network's dense core.
- **Key-player / group-capture measures** (e.g., Borgatti-style "key players" notions) — influence as ability to hold a set together or fragment it.
- **Structural-hole / constraint measures** — access to non-redundant connections.
- **Weight-aware variants** — all of the above recomputed on the weighted graph.

**Planned combination strategy:** treat influence as a **multi-criteria composite**. Options to be compared later include (i) rank aggregation across measures, (ii) a weighted composite score with sensitivity-tested weights, and (iii) a Pareto/dominance view that reports researchers strong on multiple axes rather than collapsing to one number.

### 5.3 Edge- and group-level influence
- **Edge influence:** tie strength and bridge detection (e.g., edges whose removal most increases distance / fragments the core).
- **Group influence:** community detection (modularity-based, label propagation, spectral) and per-community "leader" identification; core–periphery fitting (Borgatti–Everett style) as a structural rather than partitional view.
- **Organization-level (SP-6):** aggregate node measures to departments/universities/journals via **sum / mean / top-k / share-of-elite** statistics, with an explicit discussion of which aggregation best answers "impact of a unit."

### 5.4 Artifact (paper) influence model (SP-5)
- **Citation-network substrate:** directed citation graph over the foundational set (and optionally its citation closure).
- **Prestige measures:** PageRank/Eigenfactor-style eigenvector-on-citations; Katz; citation-count baselines.
- **Path-based influence:** whether a work lies on important citation paths (broker/bridge role).
- **Temporal/diffusion view:** model influence as **downstream propagation** — how many later works (or later authors) trace back to a paper, possibly via a **threshold/cascade** model (Valente-style thresholds) or a **search/navigation** model (Kleinberg-style small-world navigation) to express "papers that shaped subsequent research."
- **Comparative criterion:** define, in advance, what "most influential" will mean operationally (e.g., dominant under prestige + reach + durability), and pre-register the comparison logic so the later ranking is auditable.

### 5.5 Cross-domain unified model (SP-7)
- Abstract the pipeline as **entity–collaboration–artifact** triples so the same measures apply to (researcher–coauthor–paper) and (e.g., artist–collaborator–work).
- Choose measures that are **scale-free in interpretation** (normalized centralities, distribution-fit diagnostics) to avoid domain-size artifacts.

### 5.6 Decision-support / utility layer (SP-8)
- **Collaborator choice:** plan a framework where candidate new ties are scored by the resulting change in a chosen influence objective (conceptually a *marginal-gain* view: which prospective collaborator would raise the objective most). — Design only; no optimization will be run here.
- **Advisor/school choice:** map department-level influence aggregates and network position into a comparable decision table, with explicit caveats about proxy validity.

### 5.7 Advantages / limitations of the candidate framework
| Family | Advantages | Limitations to plan around |
|--------|-----------|----------------------------|
| Degree/strength | Transparent, cheap, interpretable | Confounds activity with influence |
| Betweenness | Captures brokerage | Costly at scale; sensitive to missing nodes |
| Eigenvector/PageRank | Captures recursive prestige | Sensitive to degree bias and dangling nodes |
| Katz/Bonacich | Tunable decay, handles walks | Decay parameter must be justified |
| Core/periphery & k-core | Robust structural summary | Coarse; not a ranking by itself |
| Key-player/group-capture | Answers "who holds it together" | Combinatorial cost; needs careful objective |
| Citation prestige (PageRank) | Standard, field-relative | Field/age/coverage bias |
| Diffusion/threshold | Captures downstream impact | Needs temporal ordering and assumptions |
| Composite/Pareto | Robust to single-metric quirks | Weight-selection subjectivity |

---

## 6. Implementation Roadmap

*(No code will be written in this planning stage; this is the module blueprint.)*

### 6.1 Module decomposition
1. **`ingest`** — retrieval + provenance ledger (checksums, timestamps, source metadata).
2. **`parse`** — HTML/text → line-oriented raw records; discard-out-of-universe logging.
3. **`resolve`** — name canonicalization, blocking, matching rules, merge-decision audit; emits node table.
4. **`build_graph`** — edge extraction, weighting, projection; emits graph + incidence objects.
5. **`features`** — structural feature computation (distributions, components, clustering, distances, assortativity, cores).
6. **`measures`** — centrality/influence library (node, edge, group, artifact).
7. **`community`** — partitioning + core–periphery fitting.
8. **`papers`** — paper register + citation graph + artifact influence scoring.
9. **`transfer`** — domain-agnostic re-run of ingest→measures on the second domain.
10. **`validate`** — baselines, perturbations, sensitivity sweeps, stability metrics.
11. **`report`** — figure/table generation and the ≤20-page write-up (future stage).

### 6.2 Planned workflow (ordered)
1. Acquire and freeze sources (SP-1).
2. Parse and audit; define node universe (SP-1).
3. Entity-resolve under ≥2 settings; freeze node/edge tables (SP-1/2).
4. Build the induced Erdős-1 graph + incidence representation (SP-2).
5. Compute structural properties (SP-3).
6. Implement and cross-check the measure library (SP-4).
7. Build the foundational-paper citation/co-author network and artifact scores (SP-5).
8. Aggregate to department/journal/unit level (SP-6).
9. Re-run the stack on the second domain (SP-7).
10. Run the validation package (Section 7).
11. Translate to decision-support discussion and draft the report (SP-8; report stage).

### 6.3 Engineering practices to adopt
- **Reproducibility:** versioned data snapshots, fixed random seeds, pinned dependencies, deterministic ordering.
- **Modularity:** domain-specific logic confined to ingestion/parsing; measure library stays domain-agnostic.
- **Scalability:** sparse structures; algorithms chosen with complexity noted (e.g., exact vs. sampled betweenness for large graphs).
- **Traceability:** every ranking traceable to a named measure, weighting, and resolution setting.
- **Calibration:** use the permitted reduced subnetwork to debug/calibrate before full-scale runs.

### 6.4 Risk register (planned mitigations)
| Risk | Planned mitigation |
|------|-------------------|
| Source not retrievable / changed | Fallback snapshot + provenance flag; plan for substitute |
| Name over-merging / under-merging | Dual-resolution runs; audit table; sensitivity of rankings |
| Missing ties to out-of-universe authors | Explicit discarding rule; document information loss |
| Centrality artifacts on disconnected graphs | Component-aware measures; report on largest component |
| Citation data coverage gaps | Coverage report; restrict claims to retrievable subset |
| Transfer-domain mismatch | Pre-screen domains on bipartite fit and data quality |
| Over-claiming "most influential" | Pre-register multi-criteria criterion; present rank sensitivity |

---

## 7. Validation Strategy

### 7.1 Evaluation philosophy
Because ground-truth "influence" labels are unavailable, validation will combine **internal consistency**, **external-proxy agreement**, and **robustness** checks. Success will be defined as *stability and defensibility*, not a single correctness score.

### 7.2 Candidate evaluation metrics (to compute later)
- **Rank-stability metrics:** Spearman/Kendall correlation of rankings across measures, weightings, and graph variants.
- **Set-overlap metrics:** Jaccard overlap of top-k influential sets across settings.
- **Structural fit metrics:** how well core–periphery / power-law / other distributional models describe the observed structure (diagnostics only).
- **Predictive-proxy checks:** agreement between network influence and an external proxy (e.g., a bibliometric index or an independent importance list) via rank correlation.
- **Reproducibility checks:** identical outputs under fixed seeds and re-runs.

### 7.3 Validation methods
1. **Internal cross-validation of measures** — do structurally different measures converge on a stable influential core, or diverge meaningfully (and if so, why)?
2. **External-proxy triangulation** — compare network-derived rankings against at least one independent importance proxy (e.g., an Erdős-number/ENP-style listing or a bibliometric score), reporting agreement and disagreements.
3. **Resolution-sensitivity** — rerun under strict/lenient entity resolution and compare.
4. **Weighting-sensitivity** — binary vs. count vs. recency-decayed edges.
5. **Structural perturbation** — random edge/node removal at increasing rates; measure ranking degradation (robustness curves).
6. **Boundary/definition sensitivity** — induced-subgraph vs. star-removed baselines; largest-component vs. full-graph analyses.
7. **Paper-set sensitivity** — expand/contract the foundational paper list; test ranking stability.
8. **Transfer consistency** — verify the same measures carry sensible meaning in the second domain (e.g., domain experts would not be surprised by the leaders).
9. **Degenerate-case tests** — tiny networks, disconnected graphs, and single-component edge cases to confirm graceful behavior.

### 7.4 Sensitivity analysis plan
- **Parameter sweeps:** Katz/Bonacich decay, PageRank damping, community-resolution, threshold parameters.
- **Weighting sweeps:** measure-weights in any composite.
- **Data sweeps:** resolution strictness; inclusion/exclusion of borderline papers.
- **Reporting:** each sweep summarized as a stability/robustness curve; conclusions declared only where findings survive the sweep.

### 7.5 Acceptability criteria (pre-registered)
- A ranking will be treated as *reportable* only if it is stable (above a chosen rank-correlation bar) across resolution, weighting, and perturbation settings.
- "Most influential paper/researcher" claims will be reported **with** the range of settings under which they hold, and flagged where they do not.

---

## 8. Expected Result Interpretation

*(Interpretation guidance for later — no results are produced here.)*

- **Structural properties** are expected to be described qualitatively (e.g., whether the network is dense in a core with a sparse periphery, whether distances are short, whether ties are assortative), and will be interpreted **relative to** known properties of collaboration networks — without asserting specific values at this planning stage.
- **Node influence** will be interpreted as a **multi-faceted** concept: a researcher may be highly influential through *reach* (many connections), *brokerage* (connecting otherwise separate groups), *prestige* (connection to influential others), or *embeddedness* (membership in the dense core). The report will explain *which facet* drives each prominent name.
- **Paper influence** will be interpreted through **downstream consequence**: a paper will be called influential to the extent that later work depends on, cites, or is navigable through it, with the comparative criterion stated explicitly.
- **Organization/journal influence** will be interpreted as an aggregation choice and its sensitivity, emphasizing that aggregation is itself a modeling decision.
- **Cross-domain results** will be interpreted as evidence of **transferability** and as a stress test of the measures' domain-independence.
- **Decision-support implications** will be framed as **conditional recommendations** (given a chosen objective and data quality), not universal prescriptions.

---

## 9. Limitations and Improvements

### 9.1 Known limitations (to be acknowledged in the later report)
- **Data provenance fragility.** The Erdős-1 listing is a scraped/curated source; parsing and name-resolution errors propagate into rankings.
- **Name ambiguity.** Homonyms and name variants are a fundamental source of error; even dual-resolution runs cannot eliminate residual ambiguity.
- **Missing out-of-universe links.** Discarding links to non-Erdős-1 co-authors removes genuine structure and may bias brokerage estimates.
- **Proxy validity.** Citations and co-authorship are imperfect proxies for "importance" and "influence."
- **Temporal blindness (baseline).** A static graph ignores the chronology that underlies real influence dynamics.
- **Scalability of certain measures.** Exact betweenness and key-player objectives are expensive at scale, forcing approximations.
- **Transfer-domain generality.** Findings in one non-academic domain may not generalize; transferability is demonstrated, not proven.
- **Single-metric attractiveness.** Composite scores risk hiding disagreement among facets; this is mitigated (not solved) by Pareto reporting.

### 9.2 Planned improvements / extensions
- **Temporal/dynamic networks:** add year-stamped layers to study how influence accrues and decays over time.
- **Probabilistic entity resolution** with confidence scores propagated into ranking-uncertainty estimates.
- **Bayesian / statistical network models** (e.g., exponential-family random-graph or latent-space models; Snijders-style statistical social-network modeling) to test whether observed structure exceeds chance.
- **Improved influence definitions:** field-normalized citation measures; durability/recency-weighted impact; diffusion-cascade modeling.
- **Robust aggregation:** rank-aggregation methods (e.g., Borda, Copeland, or optimized aggregation) with uncertainty intervals.
- **Multiple transfer domains** to strengthen generality claims.
- **Open, auditable artifacts:** release the processed tables and the resolution audit to enable external reproduction.
- **Decision-theoretic layer:** formalize collaborator/advisor choice as an optimization with explicit utility and constraints (design only at this stage).

---

## Appendix A — Traceability to ICM 2014 Task List

| ICM Task | Planner section(s) |
|----------|--------------------|
| 1 — Build & analyze Erdős-1 network | §2 (SP-1/2/3), §4.1–4.5, §5.1–5.3, §6 |
| 2 — Influence measures for members | §2 (SP-4), §5.2, §5.3, §7 |
| 3 — Paper/researcher/unit/journal influence | §2 (SP-5/6), §4.6, §5.4, §5.3 |
| 4 — Apply to another domain | §2 (SP-7), §4.7, §5.5, §6 |
| 5 — Science & utility of influence modeling | §2 (SP-8), §5.6, §8 |
| 6 — Report (≤20 pages) | §6.1 module 11, §9, Appendix B |

## Appendix B — Report Structure (planned, future stage)
1. Summary sheet (excluded from page count).
2. Problem restatement and modeling objectives.
3. Data acquisition and network construction.
4. Structural properties of the Erdős-1 network.
5. Influence measures (node, edge, group, artifact, organization).
6. Foundational-paper influence study.
7. Cross-domain transfer demonstration.
8. Science and utility of influence modeling.
9. Strengths, weaknesses, and sensitivity analysis.
10. Conclusions, reproducibility notes, and references.

---

*End of planning draft. This document contains no computed results, no data analysis, and no final conclusions; it is a blueprint for subsequent modeling work.*
