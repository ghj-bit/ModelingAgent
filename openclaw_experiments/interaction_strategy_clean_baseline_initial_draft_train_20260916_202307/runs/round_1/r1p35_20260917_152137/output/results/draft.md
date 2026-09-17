# Prioritizing the UN Sustainability Goals — Modeling Plan Draft

**Problem ID:** 2023_Prioritizing_the_UN
**Source:** ICM 2023, Problem D
**Document type:** Initial modeling blueprint (planning only — no solving performed)
**Status:** Draft for downstream modeling rounds

> Scope note: This document is a *roadmap*. It intentionally contains no computed results,
> no fitted models, no executed analysis, and no final conclusions. All statements are
> prospective ("will", "is planned to", "is expected to").

---

## 1. Problem Background and Restatement

### 1.1 Background

The United Nations has adopted 17 Sustainable Development Goals (SDGs) as an interconnected
blueprint for global peace and prosperity under the 2030 Agenda (A/RES/70/1, 2015). Because
the goals interact — progress toward one can augment or erode another — and because resources
(funding, technology, political attention) are finite, decision-makers face a prioritization
problem: which goals most effectively advance the overall UN mission, and how should priorities
shift under external shocks (technology, pandemics, climate change, war, refugee movements).

### 1.2 Restatement of the Task

The modeling effort will address five linked subproblems:

1. **Network construction** — build a directed and/or weighted network representing
   relationships among the 17 SDGs.
2. **Prioritization** — use the network to rank goals by their leverage in advancing the
   UN mission, and project plausible outcomes over roughly the next decade.
3. **Achievement impact** — determine how achieving a specific goal (e.g., No Poverty,
   Zero Hunger) would restructure the network and reshuffle priorities; also consider whether
   additional goals should be proposed.
4. **Global-factor influence** — characterize how technological advance, pandemics, climate
   change, war, and refugee movements perturb the network and the priorities.
5. **Generalization** — articulate how other organizations (national governments,
   NGOs, firms) could reuse the network-based prioritization approach.

### 1.3 Intended Deliverable

A 25-page solution document (one-page summary sheet + full solution) that the future
modeling rounds will produce. This draft defines *how* that document will be built.

---

## 2. Objectives and Subproblems

### 2.1 Primary Objective

To design a reproducible, defensible framework that (a) represents inter-SDG dependencies as
a network, and (b) derives, ranks, and stress-tests priorities over a ~10-year horizon.

### 2.2 Decomposition into Workstreams

| # | Workstream | Core question | Planned output |
|---|-----------|---------------|----------------|
| W1 | Network representation | What are the nodes, edges, directions, and weights? | Specification + construction procedure |
| W2 | Priority derivation | Which goals have the most leverage? | Ranking methodology + decision criteria |
| W3 | Scenario / perturbation analysis | How do achievements and shocks reshape priorities? | Scenario playbooks + comparison protocol |
| W4 | Extension and generalization | What new goals, and how do other actors reuse this? | Extension criteria + transfer template |

### 2.3 Success Criteria (for the downstream modeling)

- The network is **interpretable** (edge semantics are documented).
- The ranking method is **robust** to reasonable parameter changes (verified by sensitivity plan).
- The scenario analysis is **reproducible** from documented inputs and assumptions.
- The generalization section provides **actionable transferable guidance**, not generic prose.

---

## 3. Assumptions

Assumptions are grouped by layer. Each will carry a documented justification and a planned
validation approach to be executed in later rounds.

### 3.1 Structural assumptions (network)

- **A1 — Finite node set.** The system will be modeled with the 17 canonical SDGs as the
  baseline node set; any proposed additional goals will be modeled as candidate nodes.
  *Justification:* matches the official agenda. *Validation:* compare against official UN
  indicator framework as a cross-check on granularity.
- **A2 — Pairwise interaction semantics.** Inter-SDG influence will be modeled as pairwise,
  directed links whose sign denotes synergy (+) or trade-off (−), with magnitude denoting
  strength. *Justification:* keeps the model tractable and interpretable. *Validation:*
  compare sign/magnitude against published SDG interaction literature.
- **A3 — Quasi-static network.** For any single decision snapshot the network will be treated
  as fixed; dynamics will be handled through explicit scenario perturbations rather than
  continuously evolving edges. *Validation:* repeat under the "dynamic edges" variant in W3.

### 3.2 Behavioral / policy assumptions

- **A4 — Leverage proxies effectiveness.** A goal's priority will be proxied by its
  network leverage (centrality and cascade potential), under the assumption that high-leverage
  actions advance the mission more per unit effort. *Validation:* triangulate with an
  alternative criterion (e.g., bottleneck / critical-path framing).
- **A5 — Bounded and substitutable effort.** A fixed budget of attention/funding will be
  allocated across goals; effort is partially substitutable. *Validation:* sensitivity to
  budget level and to allocation elasticity.
- **A6 — Uniform baseline capability.** Goals will be assumed comparable in "unit cost of
  progress" at baseline, with departures handled as explicit parameters.

### 3.3 Data / evidence assumptions

- **A7 — Mixed evidence will be normalized.** Because evidence is heterogeneous (expert
  opinion, indicator statistics, literature), it will be normalized onto a common scale.
  *Validation:* inter-source consistency checks.
- **A8 — Structural stability over the horizon.** Relationship sign/strength will be assumed
  to remain stable within a decade unless a scenario explicitly alters it, treating structural
  change as an explicit scenario rather than an implicit assumption.

### 3.4 Assumption register

A living assumption register will be maintained (ID, statement, justification, confidence,
validation method, status). This register will be carried forward into the solution document.

---

## 4. Data Processing Plan

No dataset is bundled with this problem; the modeling rounds will therefore build an evidence
base. This section specifies *how* that base will be assembled and processed. No data will be
collected or transformed during this planning phase.

### 4.1 Data sources (planned)

1. **Official SDG indicator framework** (UN SDG indicators, tier classification) — for
   indicator mapping and progress baselines.
2. **Published SDG interaction studies** — for edge sign/strength evidence.
3. **Structured expert elicitation** — to fill gaps and supply uncertainty ranges.
4. **Macro context series** (e.g., pandemics, conflict, climate, displacement indicators) —
   for scenario parameterization.

### 4.2 Preprocessing pipeline (planned)

1. **Harmonization** — align units, scales, and time references to a common schema.
2. **Missingness handling** — document gaps; use imputation only with explicit flags and
   sensitivity coverage.
3. **Normalization** — map heterogeneous evidence onto a common signed/weighted scale.
4. **Provenance tagging** — record source, date, and confidence for every edge/parameter.
5. **Quality gating** — flag low-confidence entries for sensitivity emphasis.

### 4.3 Feature / structure construction (planned)

- **Adjacency layer:** directed signed strengths (W1 core artifact).
- **Node attribute layer:** indicators, baseline progress, uncertainty, cost proxies.
- **Scenario parameter layer:** shock magnitudes and durations for W3.
- **Intervention layer:** goal-achievement toggles for subproblem 3.

### 4.4 Data usage strategy

- **Reuse vs. collect:** prefer authoritative existing sources; collect only where gaps block
  modeling.
- **Reproducibility:** every derived artifact will be traceable to a documented source and
  transformation.
- **Splitting:** evidence will be partitioned into (i) construction data and (ii) held-out
  or literature-consensus checks for validation.

---

## 5. Candidate Model Framework

This section enumerates candidate frameworks. Final selection will occur in later rounds;
multiple candidates are retained here to support a comparison plan.

### 5.1 Network construction (W1)

- **C1 — Expert-weighted signed digraph.** Nodes = SDGs; edges = signed directed strengths
  from literature and elicitation.
- **C2 — Correlation / co-movement network.** Edges = statistical association between goal
  progress indicators, with causality treated cautiously.
- **C3 — Hybrid layered graph.** Combine literature-derived semantics (C1) with statistical
  co-movement (C2) via a fusion rule and confidence weighting.

**Mathematical ideas:** adjacency matrix **W** with sign structure; asymmetry for directed
influence; sparsification thresholds; bootstrapped edge confidence intervals.

### 5.2 Priority derivation (W2)

- **C4 — Centrality / influence ranking.** Degree, eigenvector, Katz/Bonacich, betweenness,
  PageRank-style influence on the signed graph.
- **C5 — Cascading / diffusion models.** Linear threshold or independent-cascade propagation
  to estimate cascade size as a leverage proxy.
- **C6 — Optimization / portfolio view.** Maximize projected mission advance subject to
  budget and interaction constraints (e.g., knapsack / LP / QP with synergy-terms).
- **C7 — Structural bottleneck analysis.** Identify critical paths and controlling nodes.

**Advantages/limitations (schematic):**

| Candidate | Strength | Limitation |
|-----------|----------|------------|
| C4 centrality | simple, interpretable | ignores dynamics & budget |
| C5 cascade | captures spillover | threshold params uncertain |
| C6 optimization | decision-relevant | sensitive to objective form |
| C7 bottleneck | surfaces dependencies | not a ranking by itself |

### 5.3 Achievement-impact & scenario analysis (W3)

- **C8 — Node-removal / goal-achievement surgery.** Remove or collapse a node, re-run ranking,
  quantify priority shift (rank deltas, centrality deltas).
- **C9 — Shock injection.** Perturb edge weights and node states per scenario to emulate
  technology, pandemic, climate, war, displacement.
- **C10 — Comparative scenario matrix.** Cross achievements × shocks to map priority regimes.

### 5.4 Extension & generalization (W4)

- **C11 — Candidate-goal screening.** Criteria (distinctness, non-redundancy, leverage,
  measurability) to evaluate proposed additional goals.
- **C12 — Transfer template.** Abstract the framework into a reusable recipe parameterized by
  any organization's goal set and constraints.

### 5.5 Planned variables (naming only; values to be determined later)

- Node attributes: baseline progress, uncertainty, cost proxy, horizon target.
- Edge attributes: sign, magnitude, confidence, direction.
- Decision variables: allocation shares across goals; activation toggles.
- Scenario variables: shock type, magnitude, duration, scope.

---

## 6. Implementation Roadmap

Planning-level only; no code will be written in this phase. The roadmap defines the sequence,
modules, and artifacts for subsequent rounds.

### 6.1 Planned workflow

1. **Scoping & assumption register** → freeze A1–A8 with justifications.
2. **Evidence assembly** → build source catalog and provenance tags.
3. **Network construction** → produce adjacency + confidence layers (C1–C3).
4. **Priority engine** → implement C4–C7 on the constructed network.
5. **Scenario engine** → implement C8–C10 (achievement + shocks).
6. **Extension module** → apply C11–C12.
7. **Validation sweep** → run the Section 7 plan.
8. **Reporting** → assemble the ≤25-page solution and summary sheet.

### 6.2 Required modules (functional spec)

- `ingest` — source loading, harmonization, provenance.
- `graph_build` — adjacency construction, fusion, sparsification.
- `rank` — centrality / cascade / optimization priority estimators.
- `scenario` — node-achievement surgery and shock injection.
- `compare` — rank-shift and regime comparison utilities.
- `validate` — sensitivity, robustness, and consistency checks.
- `report` — tables/figures generation for the deliverable.

### 6.3 Artifacts to be produced in later rounds

- Decision: final network variant and edge semantics.
- A reproducible pipeline config (parameters, seeds, thresholds).
- Scenario definitions and comparison protocol.
- Validation report and assumption-register update.
- Final ≤25-page solution document with one-page summary sheet.

### 6.4 Milestones (qualitative)

- **M1:** assumption register frozen and evidence catalog complete.
- **M2:** network artifact approved with confidence layer.
- **M3:** priority engine + baseline ranking method selected.
- **M4:** scenario results available for all five global factors.
- **M5:** validation complete and priorities declared stable or flagged.
- **M6:** solution document assembled.

---

## 7. Validation Strategy

### 7.1 Evaluation metrics (planned)

- **Ranking stability:** rank-correlation across methods and parameter draws.
- **Edge-evidence agreement:** concordance of constructed edges with held-out literature.
- **Scenario distinguishability:** degree to which scenarios produce separable priority regimes.
- **Interpretability score:** fraction of edges/nodes with documented, defensible semantics.

### 7.2 Validation methods (planned)

1. **Cross-method triangulation** — compare C4–C7 rankings; flag disagreements.
2. **Bootstrap / Monte-Carlo robustness** — resample evidence and edge confidences; measure
   ranking variance.
3. **Hold-out literature checks** — test constructed edges against independent studies.
4. **Ablation** — remove individual candidate mechanisms to test necessity.
5. **Scenario replay** — verify that shock injection produces the expected qualitative shifts.

### 7.3 Sensitivity analysis (planned)

- **Parameter sensitivity:** edge thresholds, cascade thresholds, budget elasticity.
- **Structural sensitivity:** sparse vs. dense network; directed vs. undirected; with/without
  additional candidate goals.
- **Objective-form sensitivity:** centrality-based vs. optimization-based priority criteria.
- **Assumption stress tests:** challenge A2 (pairwise), A4 (leverage proxy), A8 (stability).

### 7.4 Definition of "validated" for later rounds

A priority ranking will be considered trustworthy only if it is (i) stable under bootstrap and
parameter sweeps and (ii) agreed upon by at least two independent method families, or else the
disagreement will be explicitly reported as a finding.

---

## 8. Expected Result Interpretation

This section describes how future outputs *will* be read; it reports no findings.

- **Network read-out:** edge signs/magnitudes will be interpreted as synergy vs. trade-off,
  with confidence shown alongside to prevent overclaiming.
- **Priority read-out:** high-leverage goals will be interpreted as efficient focal points,
  not as exclusive funding mandates; low-leverage goals may still be urgent on equity grounds.
- **Achievement scenario read-out:** achieving a goal will be interpreted through the
  resulting rank deltas and any emergence of new bottlenecks.
- **Global-factor read-out:** each factor will be interpreted by how it redistributes leverage
  (e.g., which goals gain/lose priority), not solely by average effects.
- **Generalization read-out:** the transfer template will be interpreted as guidance for other
  actors to instantiate with their own goal sets and constraints.

Reporting conventions (planned): always pair a priority claim with its confidence and the
method family that produced it; separate *descriptive* (network) from *prescriptive* (priority)
statements.

---

## 9. Limitations and Improvements

### 9.1 Anticipated limitations

- **Evidence scarcity/heterogeneity** may weaken edge confidence for some SDG pairs.
- **Aggregation loss:** collapsing rich interdependencies to pairwise links will discard
  higher-order interactions.
- **Normative load:** any prioritization embeds value judgments; results are model-conditional.
- **Horizon uncertainty:** a decade-ahead projection is subject to structural change that a
  quasi-static model captures only via scenarios.
- **No ground truth for priority:** priority "correctness" cannot be directly measured.

### 9.2 Planned improvements

- **Higher-order structures:** hypergraph or multi-layer extensions to capture group effects.
- **Dynamic networks:** time-varying edges and feedback loops rather than static snapshots.
- **Causal strengthening:** move from association to causal evidence where available.
- **Participatory calibration:** broaden expert elicitation to reduce single-source bias.
- **Uncertainty-first reporting:** foreground confidence intervals and disagreement metrics.

### 9.3 Planned comparison across variants

A final comparison matrix will contrast model variants (static vs. dynamic, sparse vs. dense,
centrality vs. optimization) so that the downstream solution can justify its chosen design and
transparently disclose trade-offs.

---

## Appendix A — Planning Checklist (to be executed in later rounds)

- [ ] Assumption register A1–A8 frozen with justifications.
- [ ] Evidence catalog with provenance tags complete.
- [ ] Network variant selected; edge semantics documented.
- [ ] Priority method family selected and cross-checked.
- [ ] Achievement and shock scenarios defined for all five global factors.
- [ ] Validation sweep executed; stability reported.
- [ ] Extension criteria applied; transfer template drafted.
- [ ] ≤25-page solution + one-page summary assembled.

## Appendix B — Out-of-Scope for This Draft

- No numerical results, no fitted parameters, no experiments, no figures.
- No final prioritization list and no conclusions.
- All content above is a prospective modeling plan only.
