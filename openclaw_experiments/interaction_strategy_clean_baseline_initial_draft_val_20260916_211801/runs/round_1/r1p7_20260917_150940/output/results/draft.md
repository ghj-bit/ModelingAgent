# Record Insurance — Modeling Blueprint (Initial Draft)

**Problem ID:** 2016_Record_Insurance
**Title:** Record Insurance
**Source:** IM2C 2016
**Document type:** Modeling plan draft (roadmap only — no solving, no data analysis, no computation)
**Status:** Initial draft for future modeling work

---

## 1. Problem Background and Restatement

### 1.1 Background

In athletics, organizers of distance-running events (for example, the 15,000 m road race) frequently advertise large performance bonuses to attract elite athletes. A well-known case is the Zevenheuvelenloop in Nijmegen, the Netherlands, where a substantial bonus (for example, 25,000 euro) was offered for a new world record. The organizing committee that offers such a bonus carries the full financial exposure: if the record is broken, a large one-off payment must be made, but if no record is broken the committee keeps the money. Because the committee did not purchase insurance, it retained a low-frequency / high-severity financial risk.

Insurance transfer is the natural alternative: an insurer would accept the risk in exchange for a premium. The problem is therefore fundamentally about **risk quantification, pricing, and a buy-versus-self-insure decision** for record-break bonuses.

### 1.2 Restatement of the Required Subproblems (as currently understood)

The statement asks for a strategic approach that will address five connected questions. This blueprint frames each as a future modeling task rather than an answer:

1. **Average cost of the bonus.** The central quantity to be defined is the *expected cost per race* of a bonus offer, interpreted as the bonus amount divided by the expected number of races elapsed before a record is broken (equivalently, bonus × the per-race record-break probability in a suitable renewal/point-process framing). The plan will need to define this quantity precisely, including edge cases (back-to-back records, records broken more than once in a season, censoring at the end of the observation window).

2. **Insurer pricing criteria.** A future model will need to describe how an insurer would mark up this expected cost to obtain a premium: covering operating costs, the time value of money (premium collected now, payout later), the cost of capital / risk loading for the variance of the payout, and a target profit margin. The plan will treat the mark-up as a structured, decomposable surcharge rather than a single arbitrary percentage.

3. **Organizing-committee decision.**
   (a) Criteria for whether the committee should buy insurance, given long-horizon sponsorship commitments, budget constraints, and the possibility of self-insuring (retaining risk and provisioning reserves).
   (b) An explicit characterization of the *risk of not purchasing insurance* — the chance and magnitude of a budget shortfall, not just its average.

4. **Multi-event track meet.** For a large meet with 40 events (20 men's, 20 women's), the plan will need a portfolio view: which subset of events should be insured so that aggregate exposure and premium outlay are jointly acceptable. This is a portfolio selection problem with correlated tail risk across events.

5. **General decision scheme.** A clear, implementable framework that any organizing committee can apply event by event, given their own risk appetite, bonus size, budget, and insurance quotes.

### 1.3 Deliverables the Future Solution Should Produce

- A formal definition of expected bonus cost per race and its uncertainty.
- A transparent premium-pricing structure (base expected loss + explicit loadings).
- A buy / self-insure / hybrid decision rule with an explicit risk-preference parameter.
- A reproducible portfolio method for the 40-event meet.
- A generalized, step-by-step decision scheme that is usable beyond the motivating example.

---

## 2. Objectives and Subproblems

### 2.1 Overall Objective

To design a coherent, defensible decision framework that lets an event organizer quantify record-break risk, price or evaluate insurance for a single race, and choose an optimal insurance/self-insurance portfolio across many events.

### 2.2 Decomposition into Workstreams

| ID | Workstream | Core question the future model must answer |
|----|-----------|--------------------------------------------|
| W1 | Record-break process | How should the probability and timing of world-record breaks be modeled over time? |
| W2 | Single-race expected cost | How should the average bonus cost per race be defined and computed from W1? |
| W3 | Insurer pricing | How should an insurer translate expected loss into a premium with explicit loadings? |
| W4 | Committee decision (single race) | Under what conditions should a committee buy insurance versus self-insure? |
| W5 | Risk of not insuring | How should downside risk (probability and size of loss) be measured and reported? |
| W6 | Multi-event portfolio | Which of 20+20 events should be insured, and how much total risk should be retained? |
| W7 | General scheme | How can W1–W6 be packaged into a reusable, implementable procedure? |

### 2.3 Dependencies and Sequencing

W1 → W2 → W3 → W4 → W5 → W6 → W7 forms the primary chain. W6 depends on W3 (pricing) and W4/W5 (risk metrics). W7 is a synthesis layer that depends on all others. Work on W6's combinatorial structure can begin in parallel with W3 once W1/W2 prototypes exist.

---

## 3. Assumptions

The following will be adopted as working assumptions. Each is listed with its purpose and a planned future validation route. All are provisional and should be stress-tested, not treated as fixed truth.

### 3.1 Structural / Modeling Assumptions

- **A1 — Bonus is a fixed lump sum.** The bonus amount (e.g., 25,000 euro) is a known constant per race, not indexed or split. *Purpose:* makes the payout a well-defined random variable. *Validation:* revisit against actual contracts (tiered bonuses, shared records).
- **A2 — One payable bonus per race.** At most one record-break bonus is triggered per event per edition. *Purpose:* bounds severity per period. *Validation:* check race rules for multi-record provisions.
- **A3 — Record progression follows a stochastic point/record process.** Record breaks occur as random events with a probability that may vary slowly over time, rather than as a deterministic schedule. *Purpose:* justifies modeling a waiting time to the next record. *Validation:* goodness-of-fit of candidate point-process models to historical record times.
- **A4 — Non-stationary record-break intensity (working hypothesis).** The probability of a break will likely decline over decades as records approach physiological limits, but may spike with technological/doping/pacing changes. *Purpose:* motivates time-varying rather than constant hazard. *Validation:* trend tests on inter-record intervals.
- **A5 — Field/talent dependence.** Break probability will be assumed to depend on the quality of the assembled elite field and on course conditions. *Purpose:* links bonus attractiveness to break probability. *Validation:* compare fields in record-setting vs. non-record years.
- **A6 — Independence across events within a meet (first-cut).** As a first approximation, breaks in different events will be treated as independent, with a later relaxation via a shared common factor. *Purpose:* keeps the portfolio model tractable initially. *Validation:* estimate cross-event correlation of break indicators and compare to the independence baseline.
- **A7 — Insurer is risk-neutral in expectation plus explicit loadings.** The insurer's premium will be modeled as expected loss times a structured loading factor. *Purpose:* separates the objective expected-loss core from subjective/capital loadings. *Validation:* compare modeled premiums to any published sports-event insurance pricing or analogous event-insurance benchmarks.

### 3.2 Financial / Decision Assumptions

- **A8 — Discounting applies.** Payouts occur at the time a record is set, while premiums are collected in advance; a discount rate will be used to place both on a common present-value basis. *Purpose:* enables the time-value-of-money component of W3. *Validation:* sensitivity to the chosen rate.
- **A9 — Budget and sponsorship horizon.** The committee has a multi-year horizon with planned sponsorship/budget, so both per-season cash flow and cumulative exposure matter. *Purpose:* defines the decision objective (not just a one-shot expectation). *Validation:* scenario analysis over budget levels.
- **A10 — Risk aversion is representable.** The committee's preferences can be captured by a specified risk measure/utility (e.g., expected shortfall tolerance or a risk-aversion coefficient). *Purpose:* makes "should we buy?" a well-posed optimization. *Validation:* compare decisions across several risk-aversion settings.
- **A11 — Self-insurance means reserves.** Self-insuring is modeled as retaining risk and holding a reserve/provision rather than as zero cost. *Purpose:* makes the buy-vs-self-insure comparison fair. *Validation:* check against treasury/capital-cost practice.

### 3.3 Scope Assumptions

- **A12 — Only world-record bonuses are in scope.** Other prize money and operational costs are out of scope unless they interact with the decision. *Purpose:* bounds the problem. *Validation:* confirm no secondary bonuses are decision-relevant.
- **A13 — Historical data availability.** Public world-record histories and race results will be assumed sufficient to estimate break intensities; data gaps will be handled explicitly (see §4). *Purpose:* feasibility of calibration. *Validation:* data audit early in implementation.

---

## 4. Data Processing Plan

This section describes what data will be sought and how it will be prepared. **No data will be analyzed at this drafting stage** — the plan is forward-looking.

### 4.1 Data Inventory to Gather

- **D1 — World-record history** for the relevant 15k (and, for the multi-event meet, all 20+20 events): date and mark of each ratified record, with athlete and location.
- **D2 — Race editions** for the focal event(s): year, date, winning time, whether a record was set, and the elite field quality where available.
- **D3 — Field strength proxies:** winning time, runner-up gap, number of sub-threshold athletes, national/international representation.
- **D4 — Conditions:** course profile, weather where obtainable, and any known regulatory or equipment changes.
- **D5 — Financial parameters:** bonus amounts, any historical insurance quotes/premiums (if discoverable), plausible discount and loading rates.
- **D6 — Multi-event universe:** for the 40-event meet, event list, historical record-break frequencies per event, and bonus sizes.
- **D7 — Country/era composition** (Ethiopia/Netherlands/Kenya win shares provided in the source narrative) as contextual covariates for a qualitative/empirical prior.

### 4.2 Preprocessing Steps

1. **Normalization and de-duplication** of record entries across sources; reconcile conflicting marks/dates.
2. **Time indexing:** convert all dates to a common timeline; define event editions as ordered periods.
3. **Outcome construction:** create binary record-break indicators per edition and inter-record waiting times.
4. **Censoring handling:** treat the period after the last recorded break as right-censored; plan for survival-style estimators rather than naive averaging.
5. **Covariate alignment:** join field-strength and condition features to editions where available; otherwise record as missing with a documented pattern.
6. **Currency and inflation alignment** for bonus and premium values across years.
7. **Versioned data snapshots** stored under `data/`, with a manifest describing provenance and cleaning steps.

### 4.3 Feature Construction (future)

- **Waiting-time features:** time since last record, number of editions since last record.
- **Trend features:** rolling record-improvement rate, decades-since-record-saturation proxy.
- **Field features:** field-quality index built from D3.
- **Event metadata:** men's/women's, distance/type, historical break base rate.
- **Common-factor proxies:** calendar-year indicators and global performance-trend variables to enable later dependence modeling.

### 4.4 Data Usage Strategy

- **Calibration set:** historical editions up to a chosen cutoff will be used to estimate break intensities.
- **Hold-out set:** the most recent editions will be reserved to evaluate predictive calibration of the break process.
- **Qualitative inputs:** the win-share and narrative statistics will be used as priors/context, not as hard constraints.
- **Missing-data policy:** prefer explicit modeling of missingness over silent imputation; document any imputation for sensitivity testing.

---

## 5. Candidate Model Framework

This section lists *candidate* approaches, their variables, the mathematical ideas involved, and their trade-offs. Selection will occur during future implementation.

### 5.1 Workstream W1 — Record-Break Process

- **Candidate M1a: Bernoulli-per-edition model.** Each race independently breaks the record with probability *p*. Variables: *p* per event/gender. Idea: geometric waiting time; expected races to a break = 1/P(break per race). *Strength:* simple, transparent, easy to communicate. *Limitation:* ignores time trends and heterogeneity.
- **Candidate M1b: Non-homogeneous Poisson / hazard model.** Break events arrive with a time-varying intensity λ(t). Variables: intensity parameters, trend terms. Idea: survival/hazard analysis; waiting-time distribution derived from λ. *Strength:* accommodates declining break rates and covariates. *Limitation:* more data-hungry; specification-sensitive.
- **Candidate M1c: Extreme-value / threshold model.** Model the probability that a new mark surpasses the current record using a distribution of best performances. Variables: tail-index/threshold parameters. *Strength:* ties probability to athletic performance distributions. *Limitation:* requires dense performance data.
- **Candidate M1d: Bayesian hierarchical rate model.** Event- and gender-specific rates drawn from a common prior, allowing partial pooling for rare events. Variables: hyperparameters, event offsets. *Strength:* robust for low-count events (essential for the 40-event meet). *Limitation:* prior sensitivity to check.

### 5.2 Workstream W2 — Single-Race Expected Cost

- **Candidate M2a: Simple expectation.** Expected cost per race = B × E[break indicator per race], with B the bonus. *Idea:* E[cost] = B·P(break). *Strength:* matches the problem's stated definition. *Limitation:* undefined/awkward when *p* is estimated as 0.
- **Candidate M2b: Renewal-reward formulation.** Treat break times as a renewal process; average reward per unit time via renewal-reward theorem. Variables: inter-renewal distribution, reward B. *Idea:* long-run average cost = B / E[waiting time]. *Strength:* handles repeated records cleanly. *Limitation:* stationarity assumption conflicts with A4; needs a non-stationary extension.

### 5.3 Workstream W3 — Insurer Pricing

- **Candidate M3a: Expected-loss-plus-loadings.** Premium = expected discounted loss × (1 + operating + capital/risk + profit loadings). Variables: loading rates, discount rate. *Idea:* decomposes the premium so each factor (operating cost, time value, profit) is explicit. *Strength:* directly answers subproblem 2; auditable. *Limitation:* loadings initially assumed rather than derived.
- **Candidate M3b: Risk-loading via variance/expected-shortfall principles.** Add a loading proportional to the standard deviation or an expected-shortfall measure of the payout. Variables: risk coefficient. *Idea:* capital-at-risk pricing. *Strength:* reflects insurer solvency needs. *Limitation:* requires the payout distribution, not just its mean.
- **Candidate M3c: Actuarial credibility / experience rating.** Blend long-run event rates with recent experience. Variables: credibility weights. *Strength:* robust pricing with limited data. *Limitation:* requires a credibility framework choice.

### 5.4 Workstream W4 — Buy vs. Self-Insure Decision

- **Candidate M4a: Expected-value comparison.** Buy if premium < expected retained loss saving. *Strength:* simple benchmark. *Limitation:* ignores risk aversion.
- **Candidate M4b: Mean–variance / certainty-equivalent.** Compare certainty equivalents under a utility or risk-aversion coefficient. Variables: risk aversion γ. *Strength:* captures preference; tunable. *Limitation:* γ must be elicited.
- **Candidate M4c: Expected-shortfall / budget-shortfall constraint.** Buy if uninsured expected shortfall exceeds the premium-plus-reserve cost. Variables: confidence level, reserve cost. *Strength:* directly targets the "risk of not insuring" question. *Limitation:* tail estimate quality depends on the break model.
- **Candidate M4d: Multi-period cash-flow / reserve optimization.** Optimize over the sponsorship horizon with discounting and reserve accumulation. *Strength:* matches long-term sponsorship framing (A9). *Limitation:* more parameters; needs scenario analysis.

### 5.5 Workstream W6 — Multi-Event Portfolio

- **Candidate M6a: Independent portfolio aggregation.** Sum per-event exposures under independence; apply a portfolio-level risk measure. *Strength:* simple baseline. *Limitation:* ignores correlation (A6).
- **Candidate M6b: Correlated / common-factor portfolio.** Introduce a shared factor (e.g., global talent/era) so tails co-move. Variables: factor loadings, correlation. *Strength:* more realistic aggregate tail. *Limitation:* correlation estimation is hard with sparse breaks.
- **Candidate M6c: Optimization / selection under budget.** Choose the subset of events to insure maximizing risk reduction per premium euro, subject to a budget. Variables: binary insure/retain decisions. *Strength:* answers subproblem 4 directly. *Limitation:* combinatorial; needs heuristics or convex relaxation.

### 5.6 Workstream W7 — General Decision Scheme

- **Candidate M7a: Decision-tree / flowchart procedure.** A sequential test (estimate rate → compute premium → compare to risk metric → decide) parameterized by the committee's risk appetite. *Strength:* implementable and explainable. *Limitation:* aggregation of multiple criteria needs a rule.
- **Candidate M7b: Multi-criteria scoring framework.** Weighted criteria (cost, risk reduction, attractiveness to athletes, budget fit). *Strength:* handles soft factors from the statement. *Limitation:* weights are judgmental; must be elicited/justified.

### 5.7 Cross-Cutting Variables

| Variable | Symbol (proposed) | Role |
|----------|-------------------|------|
| Bonus amount | B | payout if record broken |
| Per-race break probability | p (or intensity λ(t)) | core risk driver |
| Expected races to break | E[T] | denominator of average cost |
| Average bonus cost per race | C = B·p ≈ B/E[T] | primary output of W2 |
| Discount rate | r | time value of money |
| Operating/capital/profit loadings | ℓ_ops, ℓ_cap, ℓ_prof | premium build-up |
| Premium | Π | insurer quote to compare against |
| Risk-aversion / confidence level | γ or α | decision preference |
| Reserve cost of capital | c_res | self-insurance cost |
| Insure/retain decision per event | x_i ∈ {0,1} | portfolio selection |

---

## 6. Implementation Roadmap

### 6.1 Planned Module Structure (under `code/`)

- `data_loader` — ingest and validate D1–D7; write clean tables to `data/`.
- `break_process` — fit/estimate W1 candidate models; produce per-event break probabilities/intensities and uncertainty.
- `pricing` — implement W3 premium build-up given break-process outputs and financial parameters.
- `decision` — implement W4 risk metrics, buy/self-insure rules, and scenario sweeps.
- `portfolio` — implement W6 aggregation and selection for the 40-event meet.
- `reporting` — assemble tables/figures for the final write-up (figures generated only in the later solving phase).
- `config` — central place for assumptions (A1–A13), parameters, and scenario definitions.
- `utils` — shared math/statistics helpers and reproducibility utilities.

### 6.2 Algorithmic Workflow (planned)

1. Audit and load data; produce a data-quality report.
2. Estimate break-process parameters with uncertainty (prefer methods that stay stable for rare events, e.g., hierarchical/Bayesian or credibility blending).
3. Derive expected races to break and the average cost per race (W2).
4. Build the premium model (W3) with transparent loadings.
5. Compute risk metrics (probability of loss, expected shortfall) for the uninsured case (W5).
6. Apply the single-race decision rule under several risk appetites (W4).
7. Scale to the 40-event portfolio: aggregate, then optimize the insure/retain subset under a budget (W6).
8. Package the parameterized decision scheme (W7) and document usage.

### 6.3 Engineering Practices

- **Reproducibility:** fixed seeds, pinned configurations, versioned data snapshots, a run manifest in `logs/`.
- **Modularity:** each workstream behind a stable interface so models can be swapped (e.g., Bernoulli → hazard model) without rewriting downstream code.
- **Configuration-driven scenarios:** all financial and preference parameters live in config, not in code.
- **Compute planning:** the single-race analysis is lightweight; portfolio optimization may need simulation and should be structured for parallel/sampled evaluation.
- **Artifacts:** intermediate tables and model diagnostics stored under `results/` and `logs/`.

### 6.4 Milestones (planning placeholders)

- **M-1:** Data audit complete; assumptions A1–A13 reviewed and annotated.
- **M-2:** W1/W2 prototype with uncertainty quantification.
- **M-3:** W3 pricing prototype with explicit loadings.
- **M-4:** W4/W5 decision and risk metrics for the focal race.
- **M-5:** W6 portfolio method for the 40-event meet.
- **M-6:** W7 generalized scheme + full write-up.

---

## 7. Validation Strategy

### 7.1 Evaluation Metrics (to be computed in the later solving phase)

- **Calibration of the break process:** predicted vs. observed record-break frequencies; probability-integral-transform / reliability diagnostics; log-score or Brier score on held-out editions.
- **Waiting-time accuracy:** predicted vs. observed distribution of inter-record gaps (where data permit).
- **Pricing reasonableness:** implied premium relative to expected loss; stability of loadings; comparison against the simple "add a percentage" benchmark from the statement.
- **Decision stability:** how often the recommended decision flips under small parameter changes (a robustness indicator).
- **Portfolio metrics:** aggregate expected cost, aggregate expected shortfall, premium spend, and retained-risk reduction versus the all-or-nothing baselines.

### 7.2 Validation Methods

- **Backtesting / hold-out:** fit on historical editions, evaluate on reserved recent editions (§4.4).
- **Cross-validation variants:** leave-last-k-editions-out for the time series; leave-one-event-out for the portfolio to test transfer across event types.
- **Baseline comparisons:** compare every candidate model against (i) the Bernoulli/coin-flip baseline and (ii) the problem's naive average-cost framing.
- **External plausibility checks:** sanity-check premiums and loadings against general event-insurance and capital-cost reasoning.
- **Consistency checks:** ensure the average cost definition is internally consistent under both the expectation and renewal formulations.

### 7.3 Sensitivity Analysis (planned)

- Sweep the discount rate, loading factors, and risk-aversion/confidence parameters and record decision boundaries.
- Test sensitivity to the break-process specification (Bernoulli vs. hazard vs. hierarchical) and to independence vs. correlated-event assumptions.
- Vary budget levels and sponsorship horizons to see how the buy/self-insure recommendation shifts.
- Quantify the cost of the independence assumption by comparing aggregate tails with and without a common factor.

### 7.4 Robustness and Threats to Validity

- **Sparse data:** rare events give noisy rate estimates; mitigation via hierarchical pooling and explicit uncertainty propagation.
- **Non-stationarity:** athletic records change regime over decades; mitigation via time-varying models and regime sensitivity.
- **Structural breaks:** rule/equipment/doping changes; mitigation via documented regime segmentation in sensitivity tests.
- **Judgmental parameters:** risk appetite and loadings; mitigation via transparent ranges and decision-region reporting rather than single point answers.

---

## 8. Expected Result Interpretation

The final modeling work is expected to produce the following *kinds* of outputs (no values are computed here):

- **A per-race risk profile:** a distribution for whether and when the record will next be broken, summarized by a per-race break probability and the expected number of races to a break.
- **An average-cost statement:** a defensible definition and estimate of the average bonus cost per race, with an uncertainty interval rather than a single number.
- **A premium decomposition:** a premium expressed as the expected loss plus separately identified components for operating costs, time value of money, capital/risk, and profit — making explicit how much of the premium is "risk" versus "margin."
- **A buy-vs-self-insure decision map:** regions of (bonus size, break probability, risk appetite, budget) in which buying is preferred and regions in which self-insuring with reserves is preferred, plus a quantification of the downside risk of remaining uninsured.
- **A portfolio recommendation rule:** a method that, for the 40-event meet, ranks and selects events to insure based on risk reduction per euro of premium, under a stated budget and dependence assumption.
- **A generalized scheme:** a step-by-step, parameterized procedure any committee can follow, including the data it must gather and the judgments it must make.

Interpretation notes to carry into the final report: results should be read as **decision-support ranges conditioned on assumptions**, not as precise predictions; the value of the framework lies in making the risk, the pricing logic, and the trade-offs explicit and auditable.

---

## 9. Limitations and Improvements

### 9.1 Anticipated Limitations

- **Data sparsity** limits the precision of rare-event rate estimates and correlation estimates.
- **Model dependence:** conclusions may shift between Bernoulli, hazard, and extreme-value specifications.
- **Assumed loadings and preferences** inject judgment into the pricing and decision layers.
- **Independence assumptions** in the first-cut portfolio model may understate aggregate tail risk.
- **Static parameters** may miss regime changes in athletic performance.
- **Unmodeled strategic behavior:** organizers' bonus choices may themselves influence field quality and thus break probability.

### 9.2 Planned Improvements

- Replace first-cut independence with a realistic dependence structure once correlation evidence is assembled.
- Move from assumed loadings to derived capital loadings using the payout distribution.
- Add regime-switching or change-point components if backtests suggest non-stationarity.
- Introduce a feedback loop linking bonus level to field quality and break probability.
- Extend the decision scheme to incorporate non-financial objectives (athlete attraction, media value) via the multi-criteria layer (M7b).
- Validate the general scheme on a second, independent event to demonstrate transferability.

---

## Appendix A — Planning Checklist

- [ ] Confirm problem interpretation (W1–W7) with stakeholders.
- [ ] Finalize the list of assumptions (A1–A13) and their validation routes.
- [ ] Complete the data audit and preprocessing (D1–D7).
- [ ] Prototype the break process and expected-cost definitions.
- [ ] Build the premium decomposition.
- [ ] Implement single-race and portfolio decision rules.
- [ ] Run backtests, cross-validation, and sensitivity sweeps.
- [ ] Package the general decision scheme and write the final report.

## Appendix B — Notes on Scope Discipline

This document is intentionally confined to planning. It contains **no computed results, no fitted parameters, no executed experiments, and no final conclusions**. All numbers appearing in the statement (for example, the 25,000 euro bonus and the "every 25 races" illustration) are quoted only as problem inputs for framing and are not used to produce answers here. Any quantitative work belongs to the subsequent solving phase, informed by this blueprint.
