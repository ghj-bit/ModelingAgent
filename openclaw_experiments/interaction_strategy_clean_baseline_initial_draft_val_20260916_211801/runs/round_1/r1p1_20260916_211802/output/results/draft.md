# Airline Overbooking — Initial Modeling Plan (Blueprint Draft)

**Problem ID:** 2002_Airline_Overbooking
**Source:** MCM 2002
**Document type:** Modeling blueprint / roadmap (NOT a solution)
**Status:** Draft — future-oriented plan. No results, computations, or conclusions are included by design.

> Note on scope: This document is intentionally limited to planning artifacts — workflow, assumptions, candidate methods, data plan, implementation roadmap, and validation strategy. It contains no fitted models, no executed experiments, and no numeric findings.

---

## 1. Problem Background and Restatement

### 1.1 Background
Airlines routinely sell more reservations than an aircraft's seat capacity because a fraction of confirmed passengers do not show up (no-shows, cancellations, missed connections). When realized demand to board exceeds capacity, one or more passengers must be "bumped" (denied boarding). Historically, carriers absorb this risk because the marginal revenue of an extra booking usually exceeds the expected cost of compensating a bumped passenger.

The problem is set against a stressed operating environment:
- **Reduced flight frequency** between point A and point B (fewer alternative reaccommodation options),
- **Heightened security** at and around airports (longer processing, more late/missed connections),
- **Passenger fear and reduced travel demand** (shifted no-show behavior),
- **Large industry revenue losses**, which tighten the acceptable risk buffer.

### 1.2 Restatement
We are asked to develop a mathematical model that:
1. Examines how **different overbooking schemes** affect the **revenue** an airline receives;
2. Determines an **optimal overbooking level** (number of reservations above capacity, or equivalently an overbooking rate) that **maximizes expected/appropriate revenue** for a particular flight;
3. **Reflects the current-stress context** described above;
4. Considers **alternatives for handling bumped passengers** (no compensation, rebooking on later flights / partner airlines, cash or ticket incentives, voluntary-bump auctions, etc.);
5. Produces a **short memorandum to the CEO** summarizing the analysis.

### 1.3 Deliverables (planned, not produced here)
- D1: A formalized revenue model with an explicit decision variable (overbooking level) and cost/penalty structure.
- D2: A trade-off analysis of overbooking schemes (per-scheme optimal overbooking level and resulting revenue profile).
- D3: A sensitivity analysis over demand, no-show, capacity, compensation, and reaccommodation parameters.
- D4: A CEO memorandum translating model outputs into a decision recommendation logic.

---

## 2. Objectives and Subproblems

### 2.1 Primary Objective
Determine the overbooking policy that maximizes expected (or risk-adjusted) net revenue for a given flight, given uncertain show-up behavior and the cost of denied boarding under alternative bump-handling schemes.

### 2.2 Subproblems
- **SP1 — Demand & show-up characterization.** Model the stochastic process of reservations and final show-ups (booking counts, cancellation/no-show distribution, dependency on the stress context).
- **SP2 — Revenue formulation.** Build a net revenue function = ticket revenue from boarded passengers − denied-boarding costs − spill/lost-goodwill costs, under each bump-handling scheme.
- **SP3 — Optimization of overbooking level.** Find the optimal number overbooked (or overbooking rate) as a function of capacity, fare, show-up distribution, and compensation rules.
- **SP4 — Scheme comparison.** Compare naive/current practices vs. voluntary-auction/compensation-based schemes, and quantify the value of each under the stressed context.
- **SP5 — Context effects.** Translate "fewer flights, security, fear, revenue loss" into model parameter shifts (e.g., reduced reaccommodation capacity, altered no-show rates, tighter risk tolerance) and study their impact.
- **SP6 — Deliverable generation.** Produce the CEO memo structure and the decision-support framing (future step).

### 2.3 Scope Boundaries (for this draft)
Objectives above are *planned*. No estimation, fitting, or optimization is performed in this document.

---

## 3. Assumptions

Each assumption is stated as a working hypothesis for the future model, with justification and a planned validation/revision route.

### 3.1 Demand & Booking
- **A1 — Booking arrivals are modeled as a stochastic count.** Justification: reservations arrive at random; a Poisson-like process is standard and tractable. *Validation route:* compare Poisson vs. Negative Binomial (over-dispersion) via future goodness-of-fit tests on synthetic/real booking data.
- **A2 — Show-up behavior is Bernoulli per passenger (independent).** Justification: first-order tractable; enables clean expectation formulas. *Validation route:* test over-dispersion and correlation (group travel, families) in future data and relax toward a more general model.
- **A3 — Show-up probability may depend on the stress context.** Justification: security and fear plausibly shift no-show rates. *Validation route:* scenario/parameter sweeps rather than a single fixed value.

### 3.2 Capacity & Operations
- **A4 — Aircraft capacity is fixed for the flight.** Justification: aircraft assignment is a given per flight.
- **A5 — Reaccommodation capacity is limited and context-dependent.** Justification: the problem explicitly reduces A→B flights, so alternative-seat supply is scarce. *Validation route:* parameterize reaccommodation availability and sweep it.
- **A6 — Compensation structure is exogenous and known per scheme.** Justification: schemes are the object of study; treated as policy parameters.

### 3.3 Economic / Decision
- **A7 — A single representative flight with a fixed fare (or fare classes treated as parameters).** Justification: isolates the overbooking decision; extensible to multi-fare later.
- **A8 — Risk-neutral baseline, with a planned risk-averse extension.** Justification: expected-revenue maximization is the natural first benchmark; airlines may also care about variance/reputation. *Validation route:* compare risk-neutral vs. CVaR/utility objectives.
- **A9 — Bumped passengers incur a cost that may include compensation, rebooking cost, and goodwill/reputation loss.** Justification: captures the full economic consequence of denial.

### 3.4 Simplifying (to be relaxed later)
- **A10 — No cancel-and-rebook gaming or overbooking of multiple flights simultaneously** in the baseline; treated as an extension.

---

## 4. Data Processing Plan

> No dataset was supplied with the problem statement. The plan therefore includes both (a) sourcing publicly available / literature parameters and (b) generating synthetic data from an assumed ground-truth generator for model development and stress testing.

### 4.1 Data Requirements
- **Demand side:** reservations per flight, seasonality, booking curves, fare classes.
- **Show-up side:** historical no-show / cancellation rates by route, season, and context.
- **Cost side:** compensation levels, rebooking costs, voucher values, goodwill estimates.
- **Operational side:** capacity by aircraft type, frequency (A→B), load factors, reaccommodation availability.

### 4.2 Data Sources (planned)
- Published airline/aviation industry statistics (load factor, no-show, denied-boarding rates).
- Academic literature on overbooking (e.g., classic revenue-management results) for parameter ranges.
- **Synthetic data generator:** a controlled simulator with known parameters used to validate that the future optimization recovers the true optimum.

### 4.3 Preprocessing Pipeline (planned steps)
1. **Schema definition** — define columns/units for booking, show-up, capacity, cost, context flags.
2. **Cleaning** — handle missing values, outliers (e.g., irregular operations days), and unit normalization.
3. **Context tagging** — label observations/flags for the stressed regime (reduced frequency, security, fear) to support scenario analysis.
4. **Distribution fitting (future)** — fit candidate count/binary distributions and record parameter estimates with uncertainty.
5. **Train/holdout split** — reserve data (or simulated regimes) for out-of-sample validation of the eventual policy.

### 4.4 Feature Construction (planned)
- Overbooking level Δ = reservations − capacity.
- Realized boarded count = min(reservations, capacity) − bumped, etc. (definitional construct, not computed here).
- Effective show-up rate; risk flags; reaccommodation scarcity index.
- Cost-per-bumped-passenger aggregated across schemes.

### 4.5 Data Usage Strategy
- **Development:** synthetic data with known ground truth → verify the optimizer finds the planted optimum.
- **Robustness:** real/industry parameters → scenario sweeps.
- **Reporting:** uncertainty bands propagated to the CEO memo (future).

---

## 5. Candidate Model Framework

### 5.1 Model A — Static Newsvendor-Style Overbooking (baseline)
- **Idea:** Overbooking is a newsvendor problem: overbook too little → lost revenue (underage cost); overbook too much → denied-boarding cost (overage cost). Optimal overbooking satisfies a critical-fractile condition balancing marginal revenue vs. marginal bump cost.
- **Variables:** capacity C, reservations R, overbooking level Δ = R − C, show-up probability p, fare f, bump cost b.
- **Potential strengths:** analytically tractable; closed-form critical ratio; intuitive.
- **Limitations:** single-period, ignores reaccommodation dynamics and multi-class fares; may not capture the stressed context directly.

### 5.2 Model B — Stochastic Show-up / Binomial Boarding Model
- **Idea:** Model the number of show-ups as a binomial (or over-dispersed) random variable conditioned on bookings; derive expected boarded, expected bumped, and expected revenue in closed/expectation form.
- **Variables:** as above plus distribution parameters.
- **Strengths:** explicit probabilistic treatment; directly yields expected denied-boarding count.
- **Limitations:** independence assumption; needs relaxation for group travel.

### 5.3 Model C — Compensation-Scheme / Auction-Oriented Model
- **Idea:** Extend A/B to compare bump-handling schemes: (i) no compensation, (ii) rebooking on later/partner flights, (iii) fixed cash/voucher incentive, (iv) voluntary-bump auction with escalating incentives. Each scheme changes the cost function (fixed cost, opportunity cost, or bid-distribution-dependent cost).
- **Variables:** scheme indicator, compensation level, reaccommodation probability/cost, auction bid distribution.
- **Strengths:** directly addresses the "alternatives for bumped passengers" requirement.
- **Limitations:** auction modeling needs assumptions on passenger bid behavior; more parameters.

### 5.4 Model D — Dynamic / Multi-Period Booking-Curve Model
- **Idea:** Reservations arrive over time; overbooking decisions and cancellation opportunities evolve. Could be framed as a dynamic program or sequential decision policy.
- **Strengths:** more realistic; captures early vs. late bookings and cancellations.
- **Limitations:** higher complexity; harder to validate with limited data.

### 5.5 Model E — Risk-Adjusted Objective
- **Idea:** Replace pure expected revenue with a risk-aware objective (mean-variance, CVaR, or a concave utility) to reflect tightened industry finances and reputational cost.
- **Strengths:** matches the "losses of billions" context; yields conservative overbooking.
- **Limitations:** requires choosing a risk preference; adds a policy judgment.

### 5.6 Recommended Path (planned)
Start with **Model B embedded in Model A** for a clean baseline, layer **Model C** for scheme comparison, apply **Model E** for the stressed-context recommendation, and treat **Model D** as a stretch extension. Model selection would be justified by tractability + direct coverage of problem requirements.

---

## 6. Implementation Roadmap

### 6.1 Algorithms (planned)
- Analytical solution of the critical-fractile condition (baseline).
- Numerical expectation evaluation and grid/root search over Δ for the binomial/over-dispersed model.
- Monte Carlo simulation for the full cost structure (reaccommodation, auctions, multi-class fares).
- One-dimensional / constrained optimization over overbooking level; possibly convex-optimization formulation for extensions.

### 6.2 Workflow Stages
1. **Formalize** the revenue and cost functions; define all variables/parameters.
2. **Derive** the expected-revenue expression and (where possible) the optimality condition.
3. **Synthesize** ground-truth data and confirm the optimizer recovers the known optimum.
4. **Implement** scheme variants (no-comp, rebook, incentive, auction).
5. **Optimize** overbooking level per scheme; build trade-off curves.
6. **Stress-test** via scenario sweeps and Monte Carlo.
7. **Package** results into structured tables/figures (future) and draft the CEO memo (future).

### 6.3 Required Modules (planned)
- `params` — configuration and scenario definitions.
- `demand_model` — booking/show-up stochastic generators and distribution fits.
- `revenue_model` — net revenue and scheme-specific cost functions.
- `optimizer` — analytic + numerical search over overbooking level.
- `simulator` — Monte Carlo engine for validation and stress tests.
- `analysis` — sensitivity, scenario, and risk-analysis routines.
- `reporting` — result tables/figures and memo generation (future).

### 6.4 Dependencies / Tooling (planned, not executed here)
- Language: Python (NumPy/SciPy/Pandas) for modeling and simulation.
- Reproducibility: fixed random seeds, versioned parameter files, deterministic scenario definitions.

---

## 7. Validation Strategy

### 7.1 Evaluation Metrics (planned)
- Expected net revenue per flight.
- Expected number of bumped passengers; probability of at least one bump.
- Load factor / spoilage (empty seats from under-overbooking).
- Cost decomposition (compensation, rebooking, goodwill).
- Risk metrics (revenue variance, CVaR) for the risk-adjusted variant.

### 7.2 Validation Methods
- **Analytic vs. simulation consistency:** closed-form/analytic expectations checked against Monte Carlo estimates (with convergence checks).
- **Ground-truth recovery:** synthetic data with a known optimum must be recovered by the optimizer.
- **Benchmark comparison:** naive policies (no overbooking; fixed-percentage overbooking; industry-rule-of-thumb) vs. optimized policy.
- **Out-of-sample policy test:** evaluate chosen overbooking level on held-out demand regimes.
- **Internal consistency:** monotonicity checks (revenue should respond sensibly to Δ, fare, bump cost).

### 7.3 Sensitivity Analysis (planned)
- Sweep show-up probability, fare, compensation cost, capacity, and reaccommodation availability.
- Tornado/one-at-a-time analysis + multi-parameter scenario grid.
- Identify the parameters to which the optimal overbooking level is most sensitive, and report ranges rather than point policies.
- Explicit stress-context scenarios: fewer flights, security delays, elevated fear, tighter finances.

---

## 8. Expected Result Interpretation

Planned interpretation logic (no values produced here):
- The optimum overbooking level is expected to sit where the marginal fare revenue from an extra booking balances the marginal expected denied-boarding cost.
- Higher compensation cost / scarcer reaccommodation / greater risk aversion should **reduce** the recommended overbooking level.
- Higher fare relative to bump cost, or lower show-up probability, should **increase** the recommended overbooking level.
- Scheme comparison is expected to show that well-designed incentive/auction schemes reduce total bump cost and permit (carefully) higher overbooking than no-compensation schemes, but with reputational trade-offs.
- In the stressed context, the model is expected to recommend more conservative overbooking than in normal conditions.
- Outputs will be presented as **policy ranges with confidence bands**, not single point prescriptions, given parameter uncertainty.

---

## 9. Limitations and Improvements

### 9.1 Anticipated Limitations
- Independence and single-period assumptions may overstate the simplicity of real show-up behavior.
- Sparse/absent real data limits empirical grounding; reliance on synthetic and literature parameters.
- Simplified reaccommodation and auction-behavior modeling.
- Single-flight scope ignores network effects and multi-flight/aircraft-type interactions.
- Fare simplification (single class in baseline) may understate revenue-management complexity.

### 9.2 Planned Improvements
- Over-dispersed and correlated show-up models (group travel, families).
- Dynamic, multi-period booking-curve formulation.
- Multi-class fare / nested booking structures.
- Endogenous reaccommodation and partner-airline network modeling.
- Explicit risk-aversion calibration and reputation/goodwill dynamics.
- Empirical calibration if airline data becomes available; Bayesian treatment of parameter uncertainty.
- Extension to a network-level overbooking policy.

---

### Appendix — Planning Workflow Traceability

| Planned Section | Workflow Step | Status |
|---|---|---|
| §1 Background & Restatement | Problem Understanding | Planned |
| §2 Objectives & Subproblems | Problem Understanding | Planned |
| §3 Assumptions | Assumptions | Planned |
| §4 Data Processing Plan | Data Plan | Planned |
| §5 Candidate Model Framework | Modeling Framework | Planned |
| §6 Implementation Roadmap | Implementation Plan | Planned |
| §7 Validation Strategy | Validation Plan | Planned |
| §8 Expected Result Interpretation | (reporting logic) | Planned |
| §9 Limitations & Improvements | (iteration) | Planned |

*End of blueprint draft. No solving, computation, or conclusions were performed.*
