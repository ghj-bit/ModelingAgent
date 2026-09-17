# Repeater Coordination — Modeling Blueprint (Initial Draft)

**Problem ID:** `2011_Repeater_Coordination`
**Source:** MCM 2011
**Document type:** Modeling plan / blueprint. This draft is a roadmap for future modeling work and intentionally contains **no computed results, no completed analysis, and no final conclusions**. All statements are forward-looking.

---

## 1. Problem Background and Restatement

### 1.1 Context

The VHF radio band used for this problem operates essentially by **line-of-sight (LOS)** propagation: a transmitter can only reach a receiver within an unobstructed path, which limits direct mobile-to-mobile communication. **Repeaters** are placed at elevated locations to receive weak signals, amplify them, and retransmit them on a different frequency, thereby extending effective coverage so that low-power users (e.g., mobile stations) can communicate over larger distances.

Repeaters can interfere with one another unless they are **sufficiently separated geographically** or **sufficiently separated in frequency**. A second, orthogonal interference-mitigation mechanism is the **Continuous Tone-Coded Squelch System (CTCSS)**, also called **Private Line (PL)**. Each repeater is assigned a distinct subaudible tone; users transmitting through that repeater send the tone, and the repeater only responds to signals bearing its own PL tone. Because two nearby repeaters using *different* PL tones will ignore each other's traffic, they can share the same frequency pair, increasing the number of repeaters (and users) that can be accommodated in a given area.

### 1.2 Restatement of the Task

The problem to be modeled concerns a **flat circular service area of radius 40 miles**. Within it, a set of repeaters must be deployed so that a target number of **simultaneous users** can be served while keeping co-channel/adjacent-channel interference acceptably low.

Three connected sub-questions are implied:

- **(Q1)** Determine the **minimum number of repeaters** needed to accommodate **1,000 simultaneous users**.
- **(Q2)** Determine how the required deployment changes when the demand grows to **10,000 simultaneous users**.
- **(Q3)** Discuss how the result is affected by **defects in line-of-sight propagation**, specifically **mountainous terrain** that blocks or degrades LOS paths.

### 1.3 Given Parameters (to be formalized, not yet used)

- Service area: flat circle, radius ≈ 40 miles.
- Spectrum available: **145–148 MHz** (a 3 MHz band).
- Repeater transmit/receive offset: transmitter is either **+600 kHz** or **−600 kHz** relative to the receiver frequency.
- CTCSS: **54 distinct PL tones**.
- User counts of interest: **1,000** and **10,000** simultaneous users.
- Physical mechanism coupling repeaters: LOS propagation and interference coexistence (geographic separation and/or frequency separation and/or PL-tone separation).

### 1.4 Intended Deliverables (future)

The completed study should deliver: (i) a repeatable deployment model, (ii) the minimum repeater counts and the corresponding channel/tone assignment structure, (iii) a growth/reuse analysis for the 10,000-user case, and (iv) a qualitative-to-semi-quantitative discussion of terrain effects, all with supporting assumptions and sensitivity analysis.

---

## 2. Objectives and Subproblems

### 2.1 Primary Objective

Design a modeling framework that will determine the **minimum number of repeaters** required to serve a specified number of simultaneous users within the 40-mile-radius circular area under the stated spectrum, offset, and CTCSS constraints, and to explain how that minimum scales with demand and degrades under realistic propagation.

### 2.2 Subproblems (planned decomposition)

1. **Coverage / geometry subproblem.** Characterize the maximum reliable service radius of a single repeater and the geometry of tiling the circular area with overlapping coverage cells.
2. **Capacity subproblem.** Relate the number of repeaters to the number of simultaneous users each can support, given channel and PL-tone availability.
3. **Spectrum / channel-assignment subproblem.** Model how the 145–148 MHz band, the ±600 kHz offset, and 54 PL tones generate the *effective number of independent channels* per site and the *reuse constraints* between sites.
4. **Interference / reuse subproblem.** Encode minimum geographic separation and frequency separation rules (possibly as a co-channel reuse distance or as a graph-coloring / channel-assignment problem).
5. **Demand scaling subproblem.** Determine how the optimal deployment changes from 1,000 to 10,000 users (denser sites, more tones, more channels, or a mix).
6. **Terrain subproblem.** Extend the LOS-coverage assumption to mountainous terrain by introducing blockage/shadowing and evaluating robustness of the deployment.

### 2.3 Success Criteria for the Future Model (planned)

- Produces a defensible **lower bound** and a **constructive upper bound** on the minimum repeater count.
- The bound is **stable** under reasonable parameter variation (sensitivity analysis).
- The deployment construction satisfies all explicitly stated constraints (coverage, spectrum, offset, tones, interference).
- The terrain extension shows a transparent, parameterized path from the ideal flat case to a degraded case.

---

## 3. Assumptions

Each assumption below is stated as something that **will be adopted** in the future model, with a justification and a planned validation approach. Assumptions are grouped by role.

### 3.1 Geometric / Propagation Assumptions

- **A1. Flat-Earth ideal case.** For Q1–Q2 the ground will be modeled as perfectly flat, so LOS range is limited only by the radio horizon/apature rather than terrain. *Justification:* the statement explicitly says "flat circular area." *Validation:* compare ideal-case results against a terrain-augmented case (Q3).
- **A2. Isotropic, circular coverage.** A single repeater's usable service region will be approximated as a disk of a characteristic radius `R_service`. *Justification:* tractable geometry; common in spectrum-planning models. *Validation:* perturb `R_service` in sensitivity analysis and, optionally, consider non-circular/hexagonal tilings.
- **A3. Characteristic service radius.** `R_service` will be treated as a model input (a parameter), not computed from first principles initially; a candidate value derivable from repeater height/power will be explored later. *Justification:* the problem supplies no power/height data, so the radius must be parameterized. *Validation:* test the deployment's sensitivity to `R_service`.
- **A4. Interference is distance- and frequency-driven.** Whether two repeaters can coexist will be governed by (i) geographic separation and (ii) frequency separation, optionally augmented by (iii) PL-tone separation. *Justification:* stated directly in the problem. *Validation:* vary the co-channel reuse distance threshold.

### 3.2 Spectrum / Hardware Assumptions

- **A5. Channelization of the band.** The 145–148 MHz band will be discretized into channels by an assumed channel spacing (a parameter to be decided), giving a finite set of possible receive frequencies; each receive frequency defines a frequency pair via the ±600 kHz offset. *Justification:* practical radio systems are channelized; the offset is given. *Validation:* test several channel-spacing conventions and confirm ranking stability.
- **A6. Offset convention.** Each repeater will use exactly one offset (+600 kHz or −600 kHz); a pair's transmit and receive frequencies are thus fixed. The choice/alternation of offset will be modeled as an assignment decision that also affects interference. *Justification:* given in the statement. *Validation:* compare a single-offset rule vs. a mixed-offset scheme.
- **A7. Tone reuse.** Each of the 54 PL tones will be reusable across geographically separated repeaters; tone reuse is limited by co-channel reuse distance (repeaters sharing both frequency and tone must be far apart). *Justification:* this is the stated purpose of PL. *Validation:* vary the effective number of usable tones.
- **A8. Uniform user behavior.** Users will be assumed to be distributed and to demand service uniformly in a simplified baseline, with an alternative clustered/non-uniform demand scenario explored later. *Justification:* the problem gives no spatial demand distribution. *Validation:* compare uniform vs. clustered demand.
- **A9. Traffic per user.** Each simultaneous user will be assumed to occupy (or share) one logical channel/tone channel on its serving repeater; a model for how many simultaneous users one repeater supports will be specified (e.g., a fixed-capacity parameter or a blocking-based model). *Justification:* capacity data are not provided; parameterization is required. *Validation:* sensitivity sweep on per-repeater capacity.

### 3.3 Modeling-Scope Assumptions

- **A10. Static / steady-state analysis.** The model will represent a peak-demand snapshot, not dynamic time evolution. *Justification:* "simultaneous users" implies a steady-state peak. *Validation:* discuss qualitatively how time-varying demand could alter results.
- **A11. Negligible external interference.** Only repeater-to-repeater interference and terrain blockage will be considered initially. *Justification:* scope control. *Validation:* note as a limitation.
- **A12. Homogeneous repeaters.** All repeaters will be assumed identical in power/sensitivity/coverage. *Justification:* no heterogeneity data given. *Validation:* mention heterogeneous deployment as an extension.

---

## 4. Data Processing Plan

> Note: no external dataset is provided; the "data" are the parameters embedded in the problem statement. The plan below describes how those parameters will be structured and how any auxiliary/derived quantities will be generated.

### 4.1 Parameter Inventory and Encoding

- Extract and tabulate all given constants into a single **parameter table**: area radius, band edges (145/148 MHz), offset magnitude (±600 kHz), number of tones (54), and target user counts (1,000 / 10,000).
- Mark every *adopted* parameter that is **not** given (service radius, channel spacing, per-repeater user capacity, interference thresholds) as a **configurable input** with a default and a range for sensitivity analysis.

### 4.2 Derived Feature Construction (planned)

- **Frequency-pair set.** Enumerate the family of valid (receive, transmit) pairs implied by the band edges and the ±600 kHz offset, under the adopted channel spacing, along with the resulting usable count.
- **Interference-separation metrics.** Define computable pairwise separations between repeaters: Euclidean distance, frequency difference (in channels), and tone difference/identity.
- **Coverage geometry primitives.** Define the disk-tiling / lattice parameters (cell size, overlap factor) as functions of the service radius and the circular boundary.
- **Demand descriptors.** Define user-density fields (uniform baseline; clustered alternative) over the disk.

### 4.3 Data Usage Strategy

- Use given constants **as hard constraints** (band edges, offset, tone count).
- Use adopted parameters as **scenario knobs** for sensitivity analysis rather than fixed truths.
- Keep all inputs in an explicit configuration object so that every future experiment is reproducible and traceable to an assumption (A1–A12).

### 4.4 Reproducibility Plan

- Record every parameter, its source (given vs. adopted), and its tested range.
- Version the parameter configuration alongside the model so results can be regenerated when assumptions change.

---

## 5. Candidate Model Framework

The plan is to develop a **layered model**: a geometric/topological layer, a spectrum/channelization layer, and an assignment/optimization layer, then extend with terrain. Candidates are listed for each layer; the eventual model will likely combine one option per layer.

### 5.1 Layer 1 — Coverage Geometry (how many sites to cover the disk)

- **Candidate 1A: Disk-covering / circle-packing bound.** Model minimum number of coverage disks of radius `R_service` needed to cover a radius-40 disk; yields an analytic lower bound and a lattice-based upper bound. *Advantages:* transparent, few parameters. *Limitations:* ignores interference, assumes circular cells.
- **Candidate 1B: Hexagonal-cell tiling.** Approximate coverage by a honeycomb lattice; each cell hosts a repeater. *Advantages:* structurally matches frequency reuse (classic cellular). *Limitations:* boundary of the circle does not tile cleanly; needs edge treatment.
- **Candidate 1C: Continuous/optimization placement.** Treat site locations as continuous decision variables minimizing count subject to coverage. *Advantages:* optimal in ideal geometry. *Limitations:* heavier computation; likely used selectively.

### 5.2 Layer 2 — Spectrum / Channelization (how many independent channels exist)

- **Candidate 2A: Channel-count model.** Given band width and adopted channel spacing, count available receive channels; pair each with its ±600 kHz offset to size the frequency-pair set.
- **Candidate 2B: Offset-aware pairing model.** Enumerate valid pairs and classify them as mutually compatible or interfering based on frequency separation, incorporating the ±600 kHz offset into the interference rule.
- **Candidate 2C: Tone-multiplexing model.** Multiply the effective channel supply by the PL-tone dimension where geographic separation permits, capturing the statement's core mechanism (nearby repeaters sharing a frequency pair with different tones).

### 5.3 Layer 3 — Assignment / Reuse Optimization

- **Candidate 3A: Graph-coloring / channel-assignment formulation.** Nodes = repeaters; edges = "cannot share the same frequency (+tone)"; colors = frequency-pair/tone resources; minimize repeaters and/or satisfy a required channel supply. *Advantages:* directly encodes interference and reuse; well-studied. *Limitations:* NP-hard in general; needs heuristics for large instances.
- **Candidate 3B: Co-channel reuse-distance model.** Encode interference as a minimum reuse distance; derive a reuse factor and combine with the geometric layer to get a reuse-pattern-based capacity. *Advantages:* analytic and interpretable. *Limitations:* idealized, assumes regular layouts.
- **Candidate 3C: Mixed-integer / set-covering formulation.** Decision variables for site activation, coverage of demand, and resource assignment; objective = minimize active repeaters. *Advantages:* flexible, couples all constraints. *Limitations:* solution complexity; may require decomposition or heuristics.

### 5.4 Candidate Variables (planned)

- **Decision variables:** number and locations of repeaters; frequency pair assigned to each; offset (+/−) per site; PL tone assigned per site; mapping of users/demand to repeaters.
- **Derived variables:** coverage radius per site, reuse distance, reuse factor, effective channels per site, serviceable users per site, unmet demand.
- **Parameters:** band edges, offset, tone count, service radius, channel spacing, per-repeater capacity, interference thresholds, demand distribution, terrain blockage parameters (for Q3).

### 5.5 Mathematical Ideas to Employ

- **Bounds and duality:** combine an analytic lower bound (from area/coverage and from resource supply) with a constructive upper bound (an explicit feasible deployment) to bracket the minimum.
- **Resource-supply inequality:** relate required user count to (number of sites) × (channels per site) × (tones reuse factor) to derive a capacity lower bound on the number of repeaters.
- **Reuse arithmetic (Cellular-style):** define reuse factor from geometry + interference distance and combine with site count.
- **Graph theory / combinatorial optimization:** coloring, set covering, MIP for the assignment layer.
- **Geometry of disk covering:** lattice/hexagon bounds for the coverage layer.
- **Terrain extension:** visibility/occlusion logic (line-of-sight between site and user blocked by terrain) plus a blockage/shadow probability model.

### 5.6 Advantages and Limitations of the Overall Framework

- **Advantages:** modular (each layer can be validated separately), interpretable, supports both analytic bounds and constructive deployments, and naturally accommodates demand scaling and terrain.
- **Limitations:** heavily dependent on adopted parameters (service radius, capacity, channel spacing, interference distance); idealized geometry may under/over-estimate real deployments; combinatorial layers may require heuristics.

---

## 6. Implementation Roadmap

### 6.1 Planned Modules

1. **`config` module.** Central parameter registry capturing given constants vs. adopted parameters and their sensitivity ranges (ties back to §4).
2. **`geometry` module.** Disk-covering/hex-lattice utilities: coverage counting, boundary handling, coverage-gap checks.
3. **`spectrum` module.** Frequency-pair enumeration, offset handling, tone bookkeeping, effective-channel computation.
4. **`interference` module.** Pairwise compatibility rules (distance/frequency/tone), reuse-distance computation, conflict-graph construction.
5. **`assignment` module.** Graph-coloring heuristic / MIP / set-covering solver for site-and-resource assignment.
6. **`demand` module.** User-density fields (uniform baseline, clustered alternative) and demand-to-capacity mapping.
7. **`bounds` module.** Analytical lower-bound derivation and constructive upper-bound generation for the minimum repeater count.
8. **`terrain` module.** Blockage/occlusion model and degradation analysis for Q3.
9. **`analysis` module.** Scenario runners and sensitivity sweeps; result aggregation (to be populated in the solving phase).

### 6.2 Workflow (planned sequence)

1. Formalize parameters and assumptions into `config`.
2. Build the geometric layer; obtain coverage-only bounds (Q1 baseline).
3. Build the spectrum layer; compute effective channel/tone supply.
4. Build the interference layer; derive conflict/reuse structure.
5. Build the assignment layer; construct a feasible deployment and its count; derive the capacity lower bound.
6. Combine lower and upper bounds → bracketed minimum for **1,000 users**.
7. Re-run with **10,000 users**; compare structure (more sites vs. denser reuse vs. more tones/channels).
8. Extend with `terrain`: introduce blockage and recompute coverage/deployment; assess robustness.
9. Run sensitivity analysis across adopted parameters; document stability and drivers.

### 6.3 Tooling Plan (non-binding)

- Use a general-purpose scientific stack for geometry, graphs, and optimization.
- Keep everything configuration-driven so scenarios are reproducible and independent of hard-coded numbers.
- Maintain a clean separation between "model definition" and "experiment execution" to preserve the planning/solving distinction.

### 6.4 Milestone Checkpoints

- **M1:** parameter table + assumption register frozen.
- **M2:** coverage-only bound produced (Layer 1).
- **M3:** spectrum + interference structure produced (Layers 2–3 inputs).
- **M4:** feasible deployment + bracketed minimum for 1,000 users.
- **M5:** scaled analysis for 10,000 users.
- **M6:** terrain-augmented analysis.
- **M7:** sensitivity report and assumption audit.

---

## 7. Validation Strategy

### 7.1 Internal Consistency Checks

- **Bound consistency:** verify lower bound ≤ constructed upper bound for every scenario.
- **Feasibility audit:** confirm each constructed deployment independently satisfies coverage, spectrum, offset, tone, and interference constraints.
- **Constraint traceability:** map each constraint back to a stated problem requirement or a labeled assumption (A1–A12).

### 7.2 Cross-Model Validation

- Compare the **analytic reuse-distance model** against the **graph-coloring/MIP assignment** on small instances where an exact answer can be enumerated.
- Compare **hex-lattice** vs. **continuous** placement on the ideal disk to gauge geometry-induced error.
- Cross-check the **capacity lower bound** against the **constructive deployment count** to detect over- or under-estimation.

### 7.3 Evaluation Metrics (planned)

- Minimum repeater count (per scenario) and its bracket width (upper − lower bound).
- Coverage efficiency (served area vs. union of coverage disks).
- Resource utilization (channels and tones used; reuse factor achieved).
- Constraint-violation count (must be zero for a valid solution).
- Robustness margin (how much parameters can vary before the count changes).

### 7.4 Sensitivity and Robustness Analysis

- Sweep **service radius**, **channel spacing**, **per-repeater capacity**, and **interference/reuse distance**, and record how the minimum count and its structure respond.
- Vary **demand distribution** (uniform vs. clustered) and **demand level** (1,000 vs. 10,000).
- For terrain, sweep **blockage fraction / shadow probability** and observe coverage loss and required count growth.

### 7.5 Scenario and Boundary Testing

- Test degenerate/edge cases: very large vs. very small service radius; channel spacing that yields few vs. many channels; tone count as binding vs. non-binding.
- Check the circular boundary treatment (sites near the edge, partial cells).

---

## 8. Expected Result Interpretation

> Forward-looking interpretation guidance only; no results are produced in this draft.

- The final answer will likely be presented as a **range with a recommended construction**: an analytical lower bound, a constructive feasible deployment (upper bound), and an argued "best estimate" between them.
- **For 1,000 users**, the binding constraint is expected to be debated between *coverage geometry* and *spectrum/tone supply*; the interpretation should explain which constraint dominates and why.
- **For 10,000 users**, the interpretation should distinguish between two qualitatively different responses: adding **more physical sites**, vs. exploiting **denser reuse** via more channels/tones. The clarity of this trade-off is a key deliverable.
- **For terrain (Q3)**, the expected narrative is that blockage reduces effective coverage and increases the required repeater count, or forces relocation to ridge/hilltop sites; the interpretation should quantify the direction and relative magnitude of the effect while acknowledging modeling uncertainty.
- Every headline number should be reported **with its governing assumptions and the range within which it holds**.

---

## 9. Limitations and Improvements

### 9.1 Anticipated Limitations

- **Parameter dependence:** service radius, channel spacing, per-repeater capacity, and interference thresholds are not given and will dominate the answer; results are only as credible as their assumed ranges.
- **Idealized geometry:** circular coverage and flat-earth assumptions ignore terrain, clutter, and antenna directionality (except in the simplified Q3 extension).
- **Static model:** no dynamic traffic, scheduling, or handoff effects.
- **Combinatorial simplifications:** optimization layers may rely on heuristics; optimality is not guaranteed on large instances.
- **Homogeneous repeaters and uniform demand** may not reflect real deployments.

### 9.2 Planned Improvements / Extensions

- **Physics-based coverage:** derive `R_service` from link-budget and radio-horizon models instead of assuming it.
- **Realistic terrain:** replace the simple blockage model with a digital-elevation-based LOS/occlusion computation and site optimization on high ground.
- **Traffic modeling:** move from static capacity to blocking/dynamic-demand models.
- **Heterogeneous infrastructure:** allow variable repeater power/height and directional antennas.
- **Formal optimization:** replace heuristics with exact/decomposition methods where instance size permits, and quantify the optimality gap.
- **Uncertainty quantification:** propagate parameter uncertainty into a distribution over the minimum repeater count rather than a point estimate.

### 9.3 Open Questions to Resolve in the Solving Phase

- What channel spacing and per-repeater capacity conventions should be treated as standard for VHF repeater planning?
- Should PL tones be modeled as independent of frequency reuse, or as a shared finite resource across the whole area?
- Is the intended interpretation of the ±600 kHz offset a hard per-repeater constraint (one offset each) or a system-level pairing rule?
- How should "simultaneous users" be mapped to required logical channels — one channel per user, or a shared-channel/blocking model?

---

## Appendix A — Assumption Register (to be maintained)

| ID | Assumption | Source (Given/Adopted) | Planned Validation |
|----|------------|------------------------|--------------------|
| A1 | Flat-earth for Q1–Q2 | Given ("flat") | Compare to Q3 terrain case |
| A2 | Circular coverage disk | Adopted | Perturb radius; try hex |
| A3 | `R_service` parameterized | Adopted | Sensitivity sweep |
| A4 | Interference via distance/frequency/tone | Given | Vary reuse threshold |
| A5 | Channelized band | Adopted | Vary channel spacing |
| A6 | One offset per repeater | Given | Single vs. mixed offset |
| A7 | Tone reuse across area | Given | Vary usable tone count |
| A8 | Uniform demand (baseline) | Adopted | Uniform vs. clustered |
| A9 | Per-repeater capacity parameter | Adopted | Capacity sweeps |
| A10 | Steady-state / peak snapshot | Adopted | Qualitative dynamic discussion |
| A11 | Negligible external interference | Adopted | Note as limitation |
| A12 | Homogeneous repeaters | Adopted | Heterogeneous extension |

## Appendix B — Planned Module ↔ Section Traceability

| Module | Supports | Sections |
|--------|----------|----------|
| `config` | parameter & assumption control | §3, §4 |
| `geometry` | coverage layer | §5.1, §6 |
| `spectrum` | channelization layer | §5.2, §6 |
| `interference` | compatibility & reuse | §5.3, §7 |
| `assignment` | optimization layer | §5.3, §6 |
| `demand` | user/demand mapping | §4.2, §5.4 |
| `bounds` | lower/upper bracketing | §5.5, §7 |
| `terrain` | Q3 extension | §5.5, §8 |
| `analysis` | scenarios & sensitivity | §7.4 |

---

*End of blueprint draft. This document defines what will be modeled and how; it deliberately contains no computations, no data analysis, and no final results.*
