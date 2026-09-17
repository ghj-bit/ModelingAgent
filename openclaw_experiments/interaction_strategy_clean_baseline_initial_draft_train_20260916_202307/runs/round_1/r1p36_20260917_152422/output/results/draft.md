# Modeling Blueprint Draft — The Future of the Olympics (ICM 2023, Problem Z)

> Status: **planning draft only**. This document is a roadmap for future modeling work.
> It deliberately contains no computed results, no executed experiments, and no final
> conclusions. All statements are written in future-oriented / prospective language.

---

## 1. Problem Background and Restatement

The International Olympic Committee (IOC) will face a structurally declining pool of
candidate host cities and nations for both the Summer and Winter Games. Historically,
hosting the Games will have been framed as a prestige opportunity, yet recent host
cities will have absorbed substantial cost overruns, infrastructure debt, displaced
communities, and uncertain long-run returns. In response, the Interdisciplinary
Committee on Modern Games (ICMG) will need creative, defensible strategies that keep
the Olympic movement viable, financially sustainable, and globally unifying.

Two broad families of reform will likely need to be evaluated:

1. **Permanent / rotating host locations** (a fixed set of recurring venues), and
2. **Decomposition of the Games** into four smaller seasonal events (Winter, Spring,
   Summer, Fall), each with a lighter hosting burden.

The deliverable will be framed as a decision-support package: a quantitative evaluation
of hosting impacts across several metric families, a comparison of candidate reform
strategies on feasibility, timeline, and impact, and a one-page memorandum to the IOC.

**Anticipated final deliverables (to be produced in later phases):**
- A one-page summary sheet of approach and key conclusions.
- A complete solution document with the modeling framework and analysis.
- A one-page policy memorandum to the IOC.

This draft will only define *how* those deliverables will be produced.

---

## 2. Objectives and Subproblems

**Overarching objective.** To construct a repeatable, transparent decision framework
that will rank candidate "future of the Olympics" strategies by their projected impact
on a multi-perspective metric set, and that will yield concrete policy recommendations.

**Subproblems to be decomposed and modeled.**

- **SP1 — Metric system design.** Define and operationalize metrics for hosting impact
  across the requested perspectives:
  - *Economic*: expected net public cost, cost overrun risk, GDP/employment multipliers,
    tourism and tax base effects, infrastructure legacy value.
  - *Land use*: venue footprint, new-build vs. reuse ratio, brownfield/greenfield
    pressure, post-Games legacy use, ecological disturbance.
  - *Human satisfaction*: athlete experience (venue quality, travel burden, scheduling),
    spectator experience (access, affordability, atmosphere), resident sentiment.
  - *Travel*: athlete and spectator travel distances, number of trips, carbon footprint,
    visa/logistics friction.
  - *Future opportunities*: legacy infrastructure reuse, youth-sport participation
    pipeline, bidding-pipeline attractiveness, commercial/sponsorship optionality.
  - *Host prestige / soft power*: reputational gain, media reach, diplomatic and civic
    spillovers.

- **SP2 — Characterization of the bid-decline problem.** A diagnostic subproblem that
  will estimate *why* the candidate pool is shrinking, framed as a function of the SP1
  metrics (i.e., which impact dimensions will drive bidding decisions).

- **SP3 — Strategy generation.** Enumerate a structured menu of candidate strategies
  (status quo; permanent host; small rotating set; four-season split; hybrid models;
  regional co-hosting).

- **SP4 — Impact evaluation.** For each strategy, project the SP1 metric vector under
  explicit scenarios and express trade-offs.

- **SP5 — Feasibility, timeline, and implementation.** Assess governance, legal,
  financial, and logistical feasibility; propose phased implementation timelines.

- **SP6 — Recommendation synthesis.** Convert strategy rankings into a prioritized set
  of policy recommendations and a one-page memorandum.

---

## 3. Assumptions

Each assumption below will be stated explicitly, justified, and paired with a planned
validation route. Assumptions will be treated as *revisable parameters*, not fixed truth.

**A1. Data availability.** It will be assumed that sufficient public and academic data
will be obtainable (IOC reports, World Bank/UN indicators, prior host-city studies,
budget/audit documents, media and sentiment corpora). *Justification:* the problem is
retrospective in nature and is well documented in the literature. *Validation:* a
data-availability audit will be performed before modeling; any gap will be handled by
sensitivity bounds rather than silent imputation.

**A2. Metric comparability across heterogeneous Games.** It will be assumed that
economic, land-use, travel, and satisfaction metrics can be normalized to a
per-Games or per-capita comparable scale using deflators, PPP adjustments, and
population/area normalizers. *Justification:* raw figures across decades and countries
will not be directly comparable. *Validation:* cross-check normalizations against
independently published indices.

**A3. Causal interpretability of historical relationships.** It will be assumed that
historical cost/benefit and satisfaction patterns will carry partial predictive
signal for future strategies. *Justification:* structural reform extrapolation requires
some transferability. *Validation:* out-of-sample back-testing on held-out Games and
counterfactual reasonableness checks.

**A4. Preference aggregation.** It will be assumed that stakeholder preferences
(IOC, host government, athletes, spectators, residents) can be represented by
explicit, auditable weights. *Justification:* multi-criteria ranking requires
aggregation. *Validation:* weight-elicitation via documented stakeholder perspectives
plus full weight-sensitivity analysis.

**A5. Strategy space is finite and enumerable.** It will be assumed that the candidate
reform space can be represented by a finite set of archetype strategies with tunable
parameters (e.g., number of permanent venues, season count). *Justification:* enables
structured comparison. *Validation:* expert review / scenario extension to confirm no
major archetype is omitted.

**A6. Time horizon and discounting.** It will be assumed that impacts will be assessed
over a multi-decade horizon with a stated social discount rate. *Validation:*
discount-rate sensitivity sweep.

**A7. Exogenous macro conditions.** It will be assumed that climate, geopolitical, and
macroeconomic conditions will be modeled as scenarios rather than point forecasts.

---

## 4. Data Processing Plan

*No data will be analyzed in this draft; this section only specifies the intended
pipeline. The workspace `data/` directory is currently empty, so the plan anticipates
external and public data acquisition.*

**4.1 Data sources to be assembled (planned).**
- Historical host-city financial and audit records (budgets, overruns, public debt).
- Macroeconomic and demographic indicators (World Bank, IMF, UN, national statistics).
- Venue/infrastructure inventories and land-use records.
- IOC operational reports and bid-document archives.
- Travel/transport statistics and emissions factors for flights and ground transport.
- Survey / sentiment data and published athlete and spectator satisfaction studies.
- News and social-media corpora for prestige and sentiment proxies.

**4.2 Preprocessing steps (planned).**
- Schema harmonization across heterogeneous sources (units, currencies, years).
- Currency deflation and PPP normalization to a common base year.
- Missing-data treatment strategy (documented rules; bounds instead of silent fill).
- Outlier identification with domain-justified retention/exclusion decisions.
- Provenance and versioning: every derived field will be traceable to its raw source.

**4.3 Feature construction (planned).**
- Aggregate metric features per Games/strategy: cost index, reuse ratio, footprint,
  travel intensity, satisfaction index, prestige index, opportunity index.
- Derived composite indicators to be built only after the base features are validated.
- Scenario features encoding strategy archetype parameters (venues, seasons, region).

**4.4 Data usage strategy (planned).**
- A documented split between *calibration* data (historical Games) and *evaluation*
  data (held-out Games / scenario generators).
- A single canonical data dictionary that will govern all downstream modules.

---

## 5. Candidate Model Framework

The framework will be **multi-model and layered**, so that assumptions in one layer
can be isolated and stress-tested without invalidating the whole analysis. No single
model will be relied upon as the sole evidence source.

**5.1 Layer 1 — Metric construction layer.**
- *Composite indicator design* (normalization → weighting → aggregation).
- *Candidate approaches:* min–max / z-score normalization, entropy or CRITIC
  weighting, expert AHP weighting; DEA for efficiency-style comparisons.

**5.2 Layer 2 — Diagnostic layer (why bids decline).**
- *Candidate approaches:* econometric demand/participation models of bidding
  (logit/probit on whether a city will bid), regression of bid interest on impact
  metrics, and structural causal reasoning (DAG) to separate cost drivers from
  perceived risk.

**5.3 Layer 3 — Cost/benefit and impact projection layer.**
- *Candidate approaches:* cost–benefit analysis (CBA) with Monte Carlo simulation of
  overrun distributions; system-dynamics or input–output style multipliers for
  economic spillover; land-use footprint accounting.
- *Travel layer:* network / distance models (origin–destination matrices,
  gravity models) to project athlete-spectator trip counts and emissions.

**5.4 Layer 4 — Satisfaction and prestige layer.**
- *Candidate approaches:* ordinal/utility models for satisfaction; NLP-based
  sentiment and media-reach scoring for prestige; survey-based discrete-choice models
  for spectator and athlete preferences.

**5.5 Layer 5 — Multi-criteria decision layer.**
- *Candidate approaches:* weighted-sum / weighted-product scoring; TOPSIS; PROMETHEE;
  Pareto frontier analysis to expose non-dominated strategies; multi-attribute utility
  theory for explicit trade-off representation.

**5.6 Layer 6 — Feasibility, timeline, and scenario layer.**
- *Candidate approaches:* scenario planning (baseline / reform / stress), phased
  roadmap scheduling, and a feasibility scorecard combining legal, governance,
  financial, and logistical readiness.

**5.7 Key variables (indicative, to be finalized).**
- Decision variables: strategy archetype parameters (permanent-venue count, number of
  seasonal events, host rotation size, co-hosting structure).
- State/exogenous variables: cost overruns, demand/travel volumes, macro conditions.
- Output variables: the normalized SP1 metric vector and composite scores.

**5.8 Advantages and limitations (to be documented for each candidate model).**
- *Advantages anticipated:* transparency, reusability, and explicit uncertainty.
- *Limitations anticipated:* data heterogeneity, subjectivity in weights, extrapolation
  risk beyond observed Games, and model-form uncertainty. Each limitation will map to a
  planned sensitivity or robustness test.

---

## 6. Implementation Roadmap

The work will proceed in gated phases; each phase will produce a checkpoint artifact
that will be reviewed before the next phase begins.

- **Phase 0 — Scoping and data audit.** Fix objectives, metric definitions, stakeholder
  weighting scheme, and complete the data-availability audit.
- **Phase 1 — Metric construction.** Implement normalization and weighting pipelines;
  produce a validated metric dictionary.
- **Phase 2 — Diagnostic modeling.** Build and back-test the bid-decline / demand model.
- **Phase 3 — Impact projection.** Implement CBA, travel, land-use, satisfaction, and
  prestige modules; produce per-strategy metric vectors with uncertainty bounds.
- **Phase 4 — Multi-criteria decision analysis.** Rank strategies; compute Pareto
  frontier and trade-off surfaces.
- **Phase 5 — Feasibility and timeline.** Attach feasibility scorecards and phased
  implementation schedules to top strategies.
- **Phase 6 — Synthesis and deliverables.** Produce the summary sheet, complete
  solution, and the one-page IOC memorandum.

**Required modules (planned).**
- Data ingestion + ETL and provenance module.
- Normalization/weighting module.
- Econometric/diagnostic module.
- CBA + simulation module (Monte Carlo / scenario engine).
- Travel-network / emissions module.
- Satisfaction & prestige (survey + NLP) module.
- MCDM ranking module.
- Reporting module (plots, tables, memorandum generator).

**Algorithms anticipated:** regression and discrete-choice estimation, Monte Carlo
simulation, network/gravity computations, text-sentiment scoring, AHP/entropy
weighting, TOPSIS/PROMETHEE, and Pareto-front computation. *(None will be executed in
this planning draft.)*

**Workflow conventions:** versioned data artifacts, reproducible scripts, a fixed
random seed policy for simulations, and a single source-of-truth configuration file
for weights, discount rate, and scenario definitions.

---

## 7. Validation Strategy

**7.1 Evaluation metrics (planned).**
- *Predictive:* error on held-out host-Games outcomes (cost, travel, satisfaction).
- *Ranking stability:* agreement of strategy orderings across methods and weights.
- *Uncertainty calibration:* coverage of prediction/credible intervals.
- *Decision quality:* robustness of the recommended strategy to input perturbation.

**7.2 Validation methods (planned).**
- Leave-one-Games-out / temporal back-testing for the diagnostic and projection layers.
- Cross-method triangulation: confirm that MCDM rankings will agree across at least
  two aggregation methods before being reported.
- External benchmarking against published Olympic cost and impact literature.
- Expert/stakeholder review of metric definitions and assumptions.
- Documented counterfactual checks (e.g., does a reform strategy plausibly change the
  drivers identified in SP2?).

**7.3 Sensitivity and robustness analysis (planned).**
- One-at-a-time and global sensitivity analysis over weights, discount rate, overrun
  distributions, and demand assumptions.
- Scenario stress tests (optimistic / baseline / adverse).
- Weight-perturbation analysis to detect ranking flips and report stable vs. unstable
  strategy orderings.
- Monte Carlo propagation of input uncertainty into final rankings.

---

## 8. Expected Result Interpretation

*Interpretation guidance only; no results will be produced here.*

- Final outputs will be **relative rankings and trade-off profiles**, not precise
  point predictions; reported numbers will carry uncertainty bounds.
- A strategy that is Pareto-non-dominated (and robust across weighting schemes) will be
  considered a candidate recommendation; unstable rankings will be flagged explicitly.
- Metric trade-offs will be surfaced rather than hidden: e.g., a strategy may improve
  land-use and cost while degrading travel or prestige, and this will be reported.
- The memorandum will translate the multi-criteria outcome into actionable policy
  language, stating both the recommended strategy and its key conditions/risks.
- Interpretation will emphasize *which metric drivers* are most influential on the
  recommendation, so the IOC can see the levers it can control.

---

## 9. Limitations and Improvements

**Anticipated limitations.**
- Data heterogeneity and historical bias will limit precision and comparability.
- Stakeholder weighting will introduce subjectivity; conclusions will be conditional
  on stated weights.
- Extrapolation to radical reforms (permanent hosts, four-season split) will extend
  beyond the observed historical record and carry structural uncertainty.
- Causal claims will remain provisional given the observational nature of the data.

**Planned improvements / extensions.**
- Enrich data with primary survey collection and finer-grained sentiment corpora.
- Replace heuristic weights with stakeholder-elicited or data-driven objective weights.
- Add agent-based or system-dynamics simulation for second-order effects (tourism
  displacement, long-run legacy dynamics).
- Extend the framework to climate-risk-adjusted venue viability and to regional
  co-hosting coalition models.
- Build an interactive decision dashboard for scenario exploration by the IOC.

---

*End of modeling blueprint draft. No problem solving, computation, experiment, or
final conclusion is contained in this document; all content is forward-looking
planning guidance for subsequent modeling phases.*
