# Creating Sudoku Puzzles — Initial Modeling Plan (Draft)

**Problem ID:** `2008_Creating_Sudoku_Puzzles`
**Source:** MCM 2008
**Document type:** Modeling blueprint / planning draft (no solving performed)
**Status:** Initial draft — all statements are future-oriented intentions, not results.

> Scope note: This document is a *roadmap for future modeling*. It deliberately contains no
> computed values, no fitted models, no executed experiments, no plots, and no final conclusions.
> Any numeric placeholders below are named as *targets to be determined*, never as findings.

---

## 1. Problem Background and Restatement

### 1.1 Background

Sudoku is a constraint-satisfaction puzzle played on a 9×9 grid partitioned into nine 3×3 boxes.
A completed grid (a *solution*) places the digits 1–9 exactly once in every row, column, and box.
A *puzzle* is a partially filled grid whose givens (clues) admit exactly one completion.
Puzzle designers care about two things: (a) **uniqueness** of the solution, and (b) **difficulty**,
which is not a formal property of the grid alone but a function of the solving techniques required.

### 1.2 Restatement of the Task

The task will be to design, in the future modeling effort, an algorithm that:

1. **Constructs** Sudoku puzzles of *specifiable difficulty*.
2. **Defines metrics** that quantify difficulty, with an explicit mapping from metric values to
   difficulty levels.
3. **Scales** the metric-and-level scheme to an arbitrary number of levels *K* (not just a fixed
   small set), showing at least four levels as an illustration.
4. **Guarantees a unique solution** for every generated puzzle (a hard correctness constraint).
5. **Analyzes algorithmic complexity** and pursues a design objective of **minimizing complexity**
   while still satisfying all of the above.

### 1.3 Why This Is a Modeling Problem (and not just a coding exercise)

Three coupled goals — construct, grade, and control — create a tension:

- Making a puzzle *hard* tends to *increase construction cost* and *raise the risk of multiple solutions*;
- Making construction *cheap* tends to produce puzzles of uncontrolled or narrow difficulty;
- Grading must be *objective, reproducible, and monotone* enough that increasing *K* merely refines
  an existing scale rather than redefining it.

The modeling framework will therefore be organized around an explicit **generate → grade → select
→ verify** loop with a complexity budget attached to each stage.

### 1.4 Deliverables (to be produced later)

- A written construction algorithm with pseudocode and a complexity argument.
- A formal difficulty metric (or family of metrics) plus a level-assignment rule.
- A demonstration of **at least four difficulty levels**, extensible to arbitrary *K*.
- A proof/mechanism of uniqueness as an invariant of the pipeline.
- A complexity analysis and a discussion of the complexity-minimization objective.

---

## 2. Objectives and Subproblems

### 2.1 Primary Objective

Design an extensible, uniqueness-guaranteeing Sudoku generation algorithm whose difficulty is
*controlled* by a quantifiable metric and whose computational complexity is *analyzed and minimized*.

### 2.2 Subproblems (decomposition)

| # | Subproblem | Core question to be modeled |
|---|------------|-----------------------------|
| S1 | Solution generation | How will we produce valid full 9×9 grids efficiently and uniformly enough for downstream use? |
| S2 | Clue removal / puzzle carving | How will we remove givens so that exactly one solution remains? |
| S3 | Uniqueness certification | What efficient test will certify a single solution at every accepted puzzle? |
| S4 | Difficulty metric design | Which quantities (technique usage, search effort, clue count, etc.) best capture human/algorithmic difficulty? |
| S5 | Level quantization | How will continuous or ordinal metric values be mapped to *K* levels in an extensible way? |
| S6 | Complexity analysis | What will be the asymptotic cost of each stage, and where will the design minimize it? |
| S7 | Validation & falsification | How will we test uniqueness, level separation, monotonicity, and reproducibility? |

### 2.3 Cross-Cutting Requirements

- **Extensibility:** *K* will be a configuration parameter, not a hard-coded constant.
- **Correctness first:** uniqueness will be an enforced invariant, not a post-hoc filter that discards
  most of the output.
- **Reproducibility:** the pipeline will be seeded so every puzzle and every metric value can be regenerated.
- **Comparability:** metric definitions will be fixed before level thresholds so thresholds cannot be
  tuned per puzzle to manufacture separation.

---

## 3. Assumptions

Each assumption below states (i) the assumption, (ii) its justification, and (iii) the future
validation approach that will be used to test or relax it.

### A1 — Digit/notation symmetry
Assumption: relabeling digits, permuting rows/columns within a band/stack, and transposing the grid
do not change difficulty.
Justification: these operations preserve the constraint structure exactly.
Future validation: apply the transformation group during testing and confirm metric invariance; treat
any drift as evidence the metric captures surface features rather than structure.

### A2 — Difficulty is solver-relative but acceptable if "family-relative"
Assumption: difficulty can be defined via a *fixed, documented* solver/technique family rather than a
universal human notion.
Justification: a universal human difficulty is not well-defined; a solver-relative scale is objective and
reproducible.
Future validation: cross-check metric rankings against multiple independent solver families and, if
available, published human-rated puzzles; report where rankings diverge.

### A3 — Minimal or near-minimal givens are not automatically optimal
Assumption: clue count alone is an insufficient and potentially misleading difficulty proxy.
Justification: sparse hard puzzles exist and dense easy puzzles exist.
Future validation: correlation analysis between clue count and the proposed difficulty metric, reported as
a diagnostic, not as a definition.

### A4 — Unique solvability is decidable cheaply enough inside the loop
Assumption: an exact uniqueness test can be implemented with bounded search and is affordable per candidate.
Justification: 9×9 Sudoku uniqueness testing is a well-studied, bounded exact-counting problem.
Future validation: benchmark the tester's cost separately and confirm it dominates neither the whole
pipeline nor the theoretical complexity bound.

### A5 — Difficulty levels may be defined by thresholds on a scalar score
Assumption: a one-dimensional score (possibly a weighted aggregation) will be adequate to order puzzles.
Justification: extensibility demands a scalar or orderable score to quantize into *K* bins.
Future validation: test monotonicity of perceived difficulty and check for level overlap; escalate to a
multi-dimensional metric if overlap is unavoidable at large *K*.

### A6 — Stochastic stages are acceptable if seeded
Assumption: randomized grid generation and carving are acceptable provided runs are reproducible.
Justification: determinism is required for reproducible research, not for the algorithm to be correct.
Future validation: re-run with fixed seeds and confirm bit-identical outputs.

### A7 — Target level distribution is designer-chosen
Assumption: the required proportion of puzzles per level will be an explicit input (e.g., uniform or skewed).
Justification: level *count* is specified by the task but level *proportions* are not.
Future validation: sweep proportions and confirm the generator can hit them within tolerance.

### A8 — 9×9 classic rules are the baseline instance
Assumption: the baseline instance will be standard 9×9 with 3×3 boxes; generalization to *n²×n²* will be
discussed as an extension, not implemented in the base design.
Justification: the problem statement targets classic Sudoku.
Future validation: sketch how the design would scale to order-*n* boards and note the cost implications.

---

## 4. Data Processing Plan

No dataset is supplied with this problem; the "data" will be generated and the source of truth will be
the puzzle objects themselves. The data plan therefore covers **artifact schemas, synthetic corpora, and
feature construction**.

### 4.1 Inputs

- **Primary input:** the mathematical structure of Sudoku (grid, boxes, constraint rules) and the task
  specification (four or more levels, uniqueness, complexity objective).
- **Optional reference input (if available later):** a small corpus of published puzzles with human
  difficulty ratings, used *only* as an external sanity check for the metric, not as training data.

### 4.2 Artifact Schemas (to be defined before implementation)

1. **Solution record:** the completed 9×9 grid plus the seed and generation parameters that produced it.
2. **Puzzle record:** the givens grid, the reference solution, the difficulty score, the assigned level,
   and a uniqueness certificate flag.
3. **Metric record:** per-puzzle breakdown of each metric component (e.g., component scores and their
   aggregation weights).
4. **Run manifest:** configuration (*K*, thresholds, seeds, budget caps) and the version of metric
   definitions used.

### 4.3 Preprocessing

- **Canonicalization:** apply the A1 transformation group to produce a canonical form, enabling
  de-duplication and fair comparison across puzzles.
- **Validation of structure:** every grid will be checked for rule conformance before any metric is applied;
  malformed grids will be discarded by construction, not repaired heuristically.
- **Seeding and provenance:** each artifact will carry its seed and step history so it can be replayed.
- **Deduplication:** detect duplicates and near-duplicates within and across runs using canonical forms and
  structural fingerprints.

### 4.4 Feature Construction (candidate metric components)

Features will be constructed at three conceptual levels and later aggregated:

- **Givens-level (static):** clue count, per-digit clue frequency, clue distribution across rows/columns/boxes,
  symmetry of givens.
- **Technique-level (solver-derived):** counts and depths of deductive steps (singles, pairs, pointing pairs,
  box-line reductions, hidden subsets, and—only if needed—bounded search/backtracking counts), recorded on a
  *fixed technique ladder*.
- **Search-level (behavioral):** number of branches explored, depth of the deepest branch, and time-to-solve
  under a fixed canonical solver with deterministic tie-breaking.

### 4.5 Data Usage Strategy

- **Generated corpora:** the generator will produce stratified samples across candidate score ranges, forming
  the empirical basis for threshold selection and level separation.
- **Split by purpose, not by randomness:** a *calibration* subset will be used to fit/choose thresholds and
  aggregation weights; a disjoint *holdout* subset will be used to test level separation and stability.
- **No leakage across levels:** thresholds and weights will be frozen using the calibration subset before the
  holdout subset is scored.
- **Provenance discipline:** metric definitions will be versioned so threshold choices remain auditable.

---

## 5. Candidate Model Framework

### 5.1 Overall Architecture — a Four-Stage Coupled Pipeline

The framework will be organized as a loop with explicit interfaces:

```
[Stage A: Full-solution generation]
        ↓ (valid, complete grids)
[Stage B: Gradual carving / clue removal]
        ↓ (candidate puzzles)
[Stage C: Uniqueness certification]  ── reject ──┐
        ↓ (certified unique puzzles)            │
[Stage D: Difficulty scoring & level assignment]│
        ↓                                        │
   accepted, leveled puzzle   ←─────────────────┘ (targeted re-carving if level unmet)
```

The design intent is that rejection in Stage C or a level miss in Stage D triggers a *local* retry only,
so that the pipeline does not rebuild expensive earlier stages.

### 5.2 Candidate Models per Subproblem

**S1 — Full solution generation (candidate models):**
- *M1a. Seed-and-solve:* start from an empty (or partially filled) grid and solve with randomized
  constraint propagation + backtracking.
- *M1b. Transform-and-fill:* generate a base Latin/pattern grid and apply the A1 symmetry group to obtain
  a family of solutions cheaply.
- *M1c. Algorithmic pattern construction:* use known constructive patterns (shifted-band constructions) that
  yield valid grids in near-linear time.
- *Advantages/limitations:* M1a is simple but costlier per grid; M1b/M1c are cheap but may require care to
  avoid structural bias. Bias matters because it constrains the reachable difficulty range downstream.

**S2 — Carving / clue removal (candidate models):**
- *M2a. Random-order gradual removal* with uniqueness re-check after each removal.
- *M2b. Minimal-puzzle search:* remove to a locally minimal clue set, then re-add clues to reach a target
  difficulty band (a "clue-budget adjuster").
- *M2c. Guided removal:* order removals by a predicted difficulty contribution so that carving steers toward
  a target band rather than wandering.
- *Advantages/limitations:* M2a is trivially simple but has unpredictable cost and wide score variance; M2b
  gives lower clue counts but requires careful bookkeeping; M2c adds a model/ranking component (higher
  design complexity) but is the key lever for *targeted* difficulty and for minimizing wasted iterations.

**S3 — Uniqueness certification (candidate models):**
- *M3a. Exact solution counting* with early termination at the second solution (counts ∈ {0, 1, ≥2}).
- *M3b. Constraint-propagation-only test* to certify uniqueness when the puzzle is solvable by deduction alone,
  falling back to M3a only when deduction stalls.
- *M3c. Certificate-based:* retain, for each accepted puzzle, the deduction sequence that proves uniqueness —
  making the certificate both the uniqueness proof and part of the difficulty metric.
- *Advantages/limitations:* M3a is guaranteed but potentially expensive; M3b/M3c trade completeness of the fast
  path for speed, with M3a as the reliable fallback. M3c is attractive because it makes the uniqueness proof
  *and* the difficulty evidence the same artifact.

**S4 — Difficulty metric design (candidate models):**
- *M4a. Givens-based score:* function of clue count and clue distribution.
- *M4b. Technique-ladder score:* weighted sum over counts/depths of techniques on a fixed ladder (i.e., a
  solver-effort measure).
- *M4c. Search-effort score:* branch counts/depths of a canonical deterministic solver.
- *M4d. Aggregated/hierarchical score:* normalize M4a–M4c components and combine with calibrated weights.
- *Advantages/limitations:* M4a is cheap but weak (Assumption A3); M4b/M4c are more meaningful but require a
  canonical solver definition to be reproducible; M4d is the most flexible and the most likely to remain stable
  as *K* grows, at the cost of extra design choices (weights, normalization).

**S5 — Level quantization (candidate models):**
- *M5a. Quantile binning:* score quantiles over the calibration corpus define *K* levels (extensible: just
  change *K*).
- *M5b. Fixed monotone thresholds:* designer-set cut points on the score scale, chosen once and reused.
- *M5c. Distribution-matching / optimization:* choose thresholds (and, if needed, generation parameters) so the
  achieved level distribution matches a target, formulated as a constraint/optimization problem.
- *Advantages/limitations:* M5a is automatic and inherently extensible but corpus-dependent (thresholds move if
  the corpus changes); M5b is stable and comparable over time but requires a calibrated scale; M5c offers the
  most control at the highest design cost.

**S6 — Complexity analysis (candidate models):**
- Formal cost model decomposing total cost into (generation per grid) × (candidate puzzles) × (certification
  cost) × (expected retries per accepted puzzle), with retry probability driven by the *target* level.
- Analysis will be reported as: worst-case bound, expected-case under stated distributional assumptions, and an
  amortized cost per *delivered level-K puzzle*.
- The minimization objective will be interpreted as minimizing this amortized cost subject to the constraint
  that uniqueness holds for 100% of delivered puzzles and that each level is reachable.

### 5.3 Key Variables and Notation (to be formalized later)

- Grid and constraint structure: 9×9 cells, row/column/box constraint sets.
- Decision variables in carving: the binary "given vs. blank" indicator per cell.
- Difficulty score: a scalar *D* with components *D_givens*, *D_technique*, *D_search*.
- Level assignment: a monotone partition function mapping *D* to one of *K* ordered levels.
- Complexity budget: cap parameters on retries, depth, and total solver steps per puzzle.

### 5.4 Mathematical Ideas to Be Used

- Constraint satisfaction and exact solution counting (uniqueness as "solution count = 1").
- Constraint propagation / unit propagation and other deductive closures for cheap certification.
- Monotone quantization and quantile statistics for extensible level definition.
- Amortized/worst-case complexity analysis, and possibly a constrained optimization formulation for M5c.
- Optional: symmetry-group reduction to avoid redundant search and to canonicalize outputs.

---

## 6. Implementation Roadmap

### 6.1 Modules (to be built later; interface-first)

1. **Grid core:** representation, rule checking, symmetry-group transforms, canonicalization.
2. **Solution generator:** one or more of M1a/M1b/M1c behind a common interface.
3. **Uniqueness certifier:** exact counting with early exit, plus optional fast deduction path.
4. **Canonical solver:** deterministic, tie-broken solver used as the reference for technique/search metrics.
5. **Difficulty scorer:** component computation + aggregation; metric definitions versioned.
6. **Level quantizer:** *K*-parameterized thresholding (M5a/M5b/M5c).
7. **Carving controller:** removal ordering, target-band steering, local retry policy.
8. **Orchestrator:** ties stages together, enforces budgets, emits artifacts and run manifest.
9. **Artifact/IO layer:** schemas from §4.2, dedup, and replay from seed.
10. **Experiment harness:** stratified sampling, calibration/holdout split, metric/separation reports.

### 6.2 Workflow (intended sequence of future work)

1. Fix metric definitions and artifact schemas *before* generation.
2. Implement and independently test the uniqueness certifier (correctness is a prerequisite).
3. Implement solution generation and validate grid validity and diversity.
4. Implement carving with the simplest policy (M2a) as a baseline, then add guided carving (M2c).
5. Calibrate score aggregation weights and level thresholds on the calibration corpus.
6. Freeze thresholds; evaluate level separation and stability on the holdout corpus.
7. Formalize the cost model and produce the complexity analysis.
8. Sweep *K* (including *K* ≥ 4) and target-level distributions to demonstrate extensibility.
9. Document limitations, failure modes, and extension paths.

### 6.3 Engineering Constraints and Reproducibility

- All randomness will be seeded; each artifact will record its seed and configuration.
- Budget caps (retries, depth, time) will be explicit parameters, not silent defaults.
- The metric code will be versioned with the thresholds so results remain auditable.
- Independent verification: the uniqueness certifier will be cross-checked by a second, independently written
  checker before being trusted as the pipeline's invariant enforcer.

### 6.4 Complexity-Minimization Levers (design targets)

- Prefer cheap *targeted* carving over blind carving to reduce expected retries.
- Prefer deduction-only certification when it succeeds, with exact counting as the fallback.
- Reuse generated solutions and symmetry transforms instead of regenerating from scratch.
- Bound and instrument every loop; report amortized cost per delivered leveled puzzle.

---

## 7. Validation Strategy

### 7.1 Correctness Validation

- **Uniqueness:** every delivered puzzle will be checked with an independent certifier; the acceptance
  criterion will be *zero* violations across all delivered puzzles.
- **Validity:** every grid will be checked for full rule conformance.
- **Replayability:** re-running with the same seed and configuration will be required to reproduce the same
  artifacts.

### 7.2 Difficulty-Metric Validation

- **Monotonicity:** scores will be tested for monotone agreement with independent solver-effort measures
  (e.g., search counts from a second solver family).
- **Invariance:** metric values will be tested for invariance under the A1 transformation group.
- **Separation:** distributions of scores across adjacent levels will be tested for overlap; overlap magnitude
  will be reported as the key diagnostic for whether *K* is too large for the chosen metric.
- **External sanity check (optional):** where published human-rated puzzles exist, rank-correlation between
  the metric and human ratings will be reported as supporting—not definitive—evidence.

### 7.3 Extensibility Validation

- **Sweep *K*:** the same metric definitions will be reused across different *K* values; only the quantizer
  changes. Results will be reported as refinement of the same scale.
- **Target-distribution fidelity:** achieved level frequencies will be compared against the requested target
  distribution, within a pre-declared tolerance.
- **Reachability:** every declared level will be shown to be *achievable* by the generator within budget.

### 7.4 Complexity Validation

- The theoretical cost model (§5.2, S6) will be compared against measured behavior trends as an empirical
  check of the model's structure (trend agreement, not exact constants).
- Sensitivity of amortized cost to (i) target difficulty level, (ii) *K*, and (iii) carving policy will be
  characterized.

### 7.5 Sensitivity and Robustness Analysis

- Vary metric aggregation weights and observe level-assignment stability.
- Vary solver tie-breaking rules and observe score stability.
- Vary corpus size for quantile-based thresholding (M5a) and observe threshold drift.
- Vary budget caps and observe the trade-off between delivered-puzzle rate and cost.

### 7.6 Falsification Criteria (pre-declared)

The framework will be considered *failing* if any of the following hold in future evaluation:
- Any delivered puzzle admits more than one solution.
- Adjacent levels are indistinguishable under the metric (near-total overlap).
- Metric values are not invariant under structural symmetries.
- Level assignment changes drastically under small, defensible weight changes.
- Amortized cost grows faster than the analyzed bound without explanation.

---

## 8. Expected Result Interpretation

This section states how future results *will be read*, not what they are.

- **Uniqueness certificate:** a pass will mean the pipeline satisfies the hard constraint; a fail will be
  treated as a pipeline bug or an under-specified certifier, not as an acceptable rate.
- **Difficulty scores:** will be interpreted as *relative* orderings within a fixed, documented solver family.
  Absolute score values will be treated as scale-dependent and comparable only within the same metric version.
- **Level assignments:** will be interpreted as monotone partitions of the score scale; small boundary
  ambiguity will be expected and reported rather than hidden.
- ***K* sweep:** increasing *K* should *refine*, not *redefine*, levels; results will be read as evidence about
  how much resolution the metric can support.
- **Complexity analysis:** will be read as an amortized cost statement per delivered leveled puzzle, with the
  minimization objective interpreted as reducing retries and certification cost without weakening uniqueness.
- **Trade-off interpretation:** expected tension between hardness and cost will be reported as a frontier
  (harder levels costing more per delivered puzzle), with the chosen operating point justified explicitly.

---

## 9. Limitations and Improvements

### 9.1 Anticipated Limitations

- **Solver-relative difficulty:** any metric tied to a solver family may not reflect human perception.
- **Metric bias from structure:** grid-generation bias (M1b/M1c) may restrict reachable difficulty ranges.
- **Non-monotone overlap:** at large *K*, adjacent levels may overlap, revealing metric resolution limits.
- **Threshold instability:** quantile-based thresholds (M5a) may drift with corpus composition.
- **Certification cost:** exact uniqueness counting can dominate cost for the hardest levels.
- **Single-metric reduction:** collapsing difficulty to one scalar may hide multi-dimensional structure.
- **Scope of generalization:** the baseline will target 9×9 and treat larger-board generalization as an extension.

### 9.2 Potential Improvements (future directions)

- **Multi-dimensional difficulty:** represent difficulty as a vector and use dominance/ordering rather than a
  single scalar, if scalar overlap proves unavoidable.
- **Learned ranking:** fit a ranking model from human-rated puzzles (if a corpus becomes available) to calibrate
  the technique-ladder weights—while keeping the metric reproducible and versioned.
- **Adaptive carving:** incorporate a lightweight predictive model of the score to steer carving, reducing retries.
- **Certificate reuse:** make the deduction certificate the joint proof of uniqueness and the basis of the
  technique score, unifying Stages C and D.
- **Generalization:** extend the framework to order-*n* Sudoku and to Sudoku variants (diagonal, non-standard boxes),
  and examine how complexity scales.
- **Cost-aware thresholds:** jointly optimize thresholds and generation parameters (M5c) to hit target level
  distributions at minimum amortized cost.
- **Human-facing validation:** small-scale human or published-rating validation of level ordering.

---

## Appendix — Planning Checklist (verification intent)

- [ ] Algorithm design covers construct + grade + control, with uniqueness as an enforced invariant.
- [ ] Difficulty metric is defined *before* thresholds and is versioned.
- [ ] Level scheme is parameterized by *K* and demonstrated for *K* ≥ 4 in future work.
- [ ] Complexity of every stage is analyzed; minimization levers are explicit.
- [ ] Validation covers correctness, monotonicity, invariance, separation, extensibility, and robustness.
- [ ] Falsification criteria are pre-declared.

*(End of draft — planning content only; no solving, computation, or results are included.)*
