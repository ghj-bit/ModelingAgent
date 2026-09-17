# Modeling Blueprint Draft — Reducing Illegal Wildlife Trade (ICM 2024, Problem F)

> Status: **Planning draft only.** This document is a roadmap for future modeling work. It contains no computed results, no data analysis, no fitted models, and no final conclusions. All statements are future-oriented.

---

## 1. Problem Background and Restatement

Illegal wildlife trade (IWT) is described as a major global illicit economy, estimated at up to $26.5 billion annually and ranked as the fourth-largest illegal trade worldwide. The problem asks the modeling team to design a **data-driven, 5-year intervention project** aimed at significantly reducing IWT, addressed to a **specific client** capable of executing it.

The problem decomposes into several linked demands:

- **Client selection and justification** — choose an actor with the authority, resources, and motivation to run the project, and argue why that actor is well matched to the intervention.
- **Project suitability** — use research and data to argue that the chosen project is important and viable.
- **Resource and power requirements** — identify what additional authorities, capabilities, and funding the client would need.
- **Impact prediction and analysis** — estimate the measurable change in IWT expected over 5 years if the project is implemented.
- **Feasibility and sensitivity** — assess the probability of success and identify the conditions that most affect outcomes.
- **Complex-systems framing** — treat IWT as one component of a larger interconnected system (e.g., climate change, other trafficking networks) and justify both the benefits and drawbacks of a complexity lens.

Deliverables ultimately expected by the contest: a 1-page client memo, a one-page summary sheet, and a solution of up to 25 pages. This draft plans the modeling path that would produce those deliverables; it does not produce them.

Because IWT is a socio-economic, network, and enforcement phenomenon with scarce and biased data, the plan must explicitly manage data uncertainty and the coupling between ecological, economic, and governance subsystems.

---

## 2. Objectives and Subproblems

The overarching objective will be to **design and justify a quantified 5-year project that a named client could implement to measurably reduce illegal wildlife trade**, supported by a defensible data-analysis chain and a complexity-based rationale.

Proposed subproblem decomposition:

- **SP1 — Client and mission alignment.** Establish a selection framework (authority, resources, coverage, motivation, leverage) and justify a single primary client, optionally with partner actors.
- **SP2 — System characterization.** Build a conceptual and, later, quantitative description of the IWT system: source countries → transit → destination markets, key species/products, actors, and drivers (poaching incentives, demand, corruption, enforcement).
- **SP3 — Baseline and data construction.** Define the baseline IWT state (levels, flows, trends) from available indicators, with explicit treatment of measurement gaps and bias.
- **SP4 — Intervention design.** Enumerate candidate interventions (enforcement, demand reduction, supply-side livelihood substitution, traceability, financial disruption, cross-domain integration) and select a coherent portfolio over 5 years.
- **SP5 — Impact model.** Specify a model that maps the selected interventions to changes in IWT outcomes over the 5-year horizon.
- **SP6 — Feasibility and sensitivity.** Define success probability and identify which assumptions/parameters dominate outcome variance.
- **SP7 — Complex-systems justification.** Plan the argument for treating IWT as part of a larger system, including benefits and drawbacks of the complexity framework.
- **SP8 — Communication artifacts.** Plan the structure of the client memo, summary sheet, and full solution (not authored here).

Each subproblem will be paired with a clear deliverable fragment so the final write-up can be assembled from independently validated parts.

---

## 3. Assumptions

Assumptions are grouped and each will carry a justification and a future validation route. They are stated now as planning hypotheses.

**A. Scope and system boundary**
- A1. A single primary client (e.g., a transnational enforcement/coordination body, an international conservation NGO, or a multi-government consortium) can be identified whose mandate covers most of the relevant IWT network. *Justification:* the problem requires one client with real execution power. *Future validation:* mandate/coverage evidence from institutional documents and literature.
- A2. The 5-year horizon is treated as the decision period; ecological and market lag effects beyond 5 years will be acknowledged but not modeled as outcomes.

**B. Data assumptions**
- B1. Seizure records, trafficking reports, and trade databases provide an imperfect but usable proxy for true IWT volume. *Justification:* direct measurement is infeasible. *Future validation:* triangulation across independent sources and bias diagnostics.
- B2. Known reporting biases (enforcement intensity, species prominence, geographic skew) can be modeled explicitly rather than assumed away. *Future validation:* sensitivity of results to alternative bias corrections.
- B3. Proxy economic and governance indicators (e.g., price data, corruption indices, GDP) are sufficiently comparable across regions for a coarse-grained model.

**C. Modeling assumptions**
- C1. IWT can be represented as a system of coupled stocks/flows (species populations, market demand, enforcement pressure, illicit flows) at an aggregated level.
- C2. Intervention effects are separable enough to be estimated individually before being combined, while interaction terms will still be tested.
- C3. Behavioral responses (adaptation, displacement, deterrence) are directionally predictable but uncertain in magnitude; they will be treated as parameters with ranges, not fixed values.

**D. Complexity framing**
- D1. Cross-domain integration (climate, other trafficking) yields non-trivial, tractable couplings rather than overwhelming the model.
- D2. The complexity framework adds explanatory and decision value that outweighs its added modeling cost — to be argued explicitly, including drawbacks.

**E. Feasibility assumptions**
- E1. The client can realistically acquire the additional powers/resources identified in SP1/SP4 within the first phase of the project.
- E2. Success can be defined against measurable, agreed indicators even under data limitations.

---

## 4. Data Processing Plan

This section plans data handling; no data will be processed in this draft.

**4.1 Source identification (planned)**
- Enforcement and seizure databases (national and international trafficking records, customs seizures).
- Species population and conservation-status datasets (red-list style indicators).
- Market and price proxies for illegal wildlife products.
- Governance/economic covariates (corruption perception, GDP, enforcement budgets) at country-year resolution.
- Literature-derived parameters for behavioral and enforcement elasticity values.

**4.2 Preprocessing pipeline (planned)**
- **Ingestion and schema harmonization:** unify units, taxonomy labels, years, and geographies across heterogeneous sources.
- **Deduplication:** detect double-counted seizure events across agencies.
- **Missing-data handling:** distinguish structurally missing (unmeasured) from randomly missing; plan multiple-imputation or explicit missingness modeling.
- **Bias correction:** construct and document adjustment factors for enforcement-intensity and reporting bias; preserve adjusted vs. raw series separately.
- **Normalization:** standardize flows to comparable scales (e.g., per-capita or per-trade-volume denominators) where appropriate.

**4.3 Feature construction (planned)**
- **Flow features:** source→transit→destination intensity indicators.
- **Pressure features:** enforcement effort, penalty severity, interception rates.
- **Demand features:** price dynamics, market demand proxies, substitute availability.
- **Vulnerability features:** species abundance, endemism, protected-area overlap.
- **System features:** cross-domain coupling indicators (e.g., co-occurrence with other trafficking or climate stress).

**4.4 Data usage strategy (planned)**
- Split data conceptually into a **calibration/estimation set** (for model parameters), a **validation set** (for out-of-sample checks), and a **scenario set** (for 5-year projections).
- Maintain a **data-quality ledger** documenting provenance, transformation, and uncertainty for every series, so results can be traced and audits are possible.
- Define an explicit **"no-silent-assumption" rule**: any imputation or bias adjustment must be recorded and stress-tested.

---

## 5. Candidate Model Framework

The plan will combine complementary model classes rather than rely on one. Candidate models are listed with roles, variables, math ideas, and trade-offs.

**5.1 System-dynamics / stock-flow component**
- *Role:* represent species populations, illicit flows, enforcement and demand as coupled stocks and flows over 5 years.
- *Variables:* population stock, poaching rate, supply chain flow, market demand, enforcement pressure, detection probability.
- *Math ideas:* coupled ordinary differential/difference equations; feedback loops; delays.
- *Pros:* transparent, scenario-friendly, accommodates delays and feedback.
- *Cons:* parameter-hungry; aggregated; risk of over-fitting to assumed parameters.

**5.2 Network / graph component**
- *Role:* model the trade network (routes, hubs, actors) to locate high-leverage intervention points.
- *Variables:* nodes (regions/markets), edges (flow intensity), centrality and vulnerability metrics.
- *Math ideas:* graph theory, flow/cut analysis, network disruption and percolation ideas.
- *Pros:* identifies chokepoints; supports targeted enforcement design.
- *Cons:* data-hungry; edge weights are usually uncertain proxies.

**5.3 Statistical / econometric component**
- *Role:* estimate relationships between enforcement, prices, demand, and observed seizure activity.
- *Variables:* outcomes (seizure/IWT proxies), predictors (enforcement, economic, governance, seasonal).
- *Math ideas:* panel/repeated-measures regression, difference-in-differences style comparison designs, time-series models.
- *Pros:* ties model to data; enables uncertainty quantification.
- *Cons:* confounding and reverse causality; weak identification under poor data.

**5.4 Optimization / decision component**
- *Role:* allocate limited budget/effort across interventions to maximize projected IWT reduction subject to constraints.
- *Variables:* decision variables (intervention intensities per year/region), budget, capacity constraints.
- *Math ideas:* constrained optimization / resource allocation / portfolio selection; possibly multi-objective trade-offs.
- *Pros:* yields actionable, defensible resource plan.
- *Cons:* objective and constraints are contested; sensitive to model error.

**5.5 Probabilistic / Bayesian & simulation component**
- *Role:* represent uncertainty in parameters and propagate it to outcome distributions and success probability.
- *Math ideas:* Bayesian parameter estimation with priors from literature; Monte Carlo simulation; probabilistic sensitivity analysis.
- *Pros:* supports feasibility claims and confidence statements.
- *Cons:* prior sensitivity; computational cost; needs careful elicitation.

**5.6 Complexity / cross-domain coupling layer**
- *Role:* formalize IWT as part of a larger system (climate stress, other illicit trades, governance shocks), including feedbacks.
- *Math ideas:* coupled subsystem modeling, interaction terms, resilience/tipping-point concepts.
- *Pros:* matches problem's stated complex-systems requirement; can reveal leverage across domains.
- *Cons:* added complexity, harder validation, risk of unidentifiable couplings.

**Integration approach (planned):** use the network + statistical layers to inform and constrain the system-dynamics core; embed the optimization layer on top of the core; wrap everything in the probabilistic layer; expose the complexity layer through explicit coupling parameters and scenario exploration.

---

## 6. Implementation Roadmap

Planned workflow, staged so each stage is independently checkable:

- **Stage 0 — Framing.** Finalize client candidates, define success metrics, lock the 5-year horizon and system boundary.
- **Stage 1 — Data assembly.** Identify sources, build the preprocessing and bias-correction pipeline, produce the data-quality ledger.
- **Stage 2 — Baseline construction.** Define baseline IWT state and trends from adjusted indicators (no projections yet).
- **Stage 3 — Structural modeling.** Implement the system-dynamics core and the network layer; connect them via shared flow definitions.
- **Stage 4 — Statistical estimation.** Estimate key relationships (enforcement↔interception, price↔demand, etc.) with uncertainty; feed estimates as parameters/priors into the structural core.
- **Stage 5 — Intervention portfolio.** Enumerate interventions, encode them as levers in the core, and run the optimization layer to propose a portfolio.
- **Stage 6 — Projection & uncertainty.** Simulate the 5-year trajectory under the portfolio; produce outcome distributions and success-probability measures.
- **Stage 7 — Sensitivity & complexity layer.** Run sensitivity analyses (below) and evaluate cross-domain couplings.
- **Stage 8 — Communication artifacts.** Assemble the client memo, summary sheet, and full solution from validated components.

**Required modules (planned):**
- Data ingestion & harmonization module.
- Bias/missingness correction module.
- Baseline & feature store.
- System-dynamics simulator.
- Network analysis module.
- Statistical estimation module.
- Optimization/portfolio module.
- Uncertainty & sensitivity engine.
- Scenario & reporting module.

**Tooling direction (planned, not executed here):** a reproducible pipeline with a shared configuration file, seeded random processes for simulation, and version-controlled data/model artifacts. All computation is deferred to a future implementation phase.

---

## 7. Validation Strategy

**7.1 Evaluation metrics (planned)**
- *Predictive:* fit/error of statistical components against held-out data; calibration of probabilistic forecasts.
- *Structural:* plausibility of simulated trajectories; conservation of flows; consistency of feedback signs.
- *Decision:* projected IWT reduction; robustness of the recommended portfolio; cost-effectiveness per unit reduction.
- *Feasibility:* estimated probability of achieving the stated goal, with confidence bounds.

**7.2 Validation methods (planned)**
- **Out-of-sample testing** of statistical relationships and baseline reconstruction.
- **Cross-source triangulation** to check that different data proxies agree directionally.
- **Back-casting / hindcasting:** test whether the model can reproduce known historical episodes when run backward.
- **Face validity with domain reasoning:** compare model behavior against documented IWT dynamics and expert expectations.
- **Consistency audits:** verify that network, statistical, and system-dynamics components agree on shared quantities.

**7.3 Sensitivity analysis (planned)**
- **Parameter sensitivity:** one-at-a-time and global (variance-based) screening to rank influential parameters.
- **Structural sensitivity:** compare alternative model structures and intervention-effect assumptions.
- **Scenario sensitivity:** explore high/low enforcement capacity, market demand shocks, cross-domain disturbances.
- **Bias sensitivity:** test whether conclusions change under alternative bias-correction treatments of the data.
- **Cross-domain coupling sensitivity:** vary the strength of climate/other-trafficking couplings to see when they change policy recommendations.

**7.4 Success criteria for the model (planned)**
- The plan will be judged adequate if it yields a stable recommended portfolio under reasonable parameter ranges, with clearly identified conditions for success and failure — not if it produces a single point forecast.

---

## 8. Expected Result Interpretation

This section describes how future results would be read; no results are produced here.

- **Outcome framing.** Results will be interpreted as *conditional projections* — "if the client executes portfolio X under assumptions Y, projected IWT change lies in range Z" — not as deterministic predictions.
- **Role of uncertainty.** Uncertainty intervals will be treated as first-class outputs; wide intervals will be read as a signal to prioritize information-gathering interventions, not as model failure.
- **Client-facing reading.** For the client, the key interpretation will be the actionable portfolio, the required powers/resources, and the conditions under which success is likely, expressed in mission-relevant terms.
- **Complexity reading.** Cross-domain couplings will be interpreted as leverage opportunities (acting on shared drivers) and as risk channels (external shocks propagating into IWT), with drawbacks acknowledged where the complexity lens reduces precision.
- **Decision-linked interpretation.** Every headline number will be tied to a decision it informs (where to enforce, what to fund, what to monitor), so results are judged by decision value rather than by raw accuracy alone.

---

## 9. Limitations and Improvements

**Anticipated limitations**
- **Data scarcity and bias:** IWT is covert; proxies are noisy and enforcement-driven, so absolute levels will be uncertain and observed trends partly reflect enforcement changes rather than true trade.
- **Aggregation:** coarse-grained system and network models may miss local dynamics and actor-level behavior.
- **Parameter dependence:** system-dynamics and simulation outputs will lean heavily on literature priors and elicited values.
- **Causal identification:** distinguishing intervention effects from external shocks will remain difficult.
- **Complexity cost:** the complexity layer may reduce interpretability and is hard to validate.
- **Client specificity:** a single-client framing may understate multi-actor coordination needs.

**Planned improvements / extensions**
- Strengthen causal inference via quasi-experimental comparison designs where natural variation exists.
- Add finer-grained regional or actor-level submodels where data permit.
- Incorporate adaptive-management loops: re-estimate parameters as the project generates new monitoring data.
- Expand the coupling layer to explicitly model drivers shared with climate stress and other trafficking.
- Develop a formal uncertainty-prioritization step that ranks which additional data would most reduce decision uncertainty.
- Add stakeholder/expert elicitation to calibrate priors and validate plausibility.

---

## Appendix — Planning Checklist

- [ ] Client candidates shortlisted and justified (SP1).
- [ ] System boundary and success metrics fixed (SP2, Stage 0).
- [ ] Data sources identified; preprocessing and bias plans defined (Section 4).
- [ ] Model components specified with interfaces (Section 5).
- [ ] Implementation stages and modules enumerated (Section 6).
- [ ] Validation and sensitivity protocol defined (Section 7).
- [ ] Interpretation conventions agreed (Section 8).
- [ ] Limitations and improvement path documented (Section 9).

*This draft intentionally contains no computations, no data analysis, no fitted models, and no final conclusions.*
