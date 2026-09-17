# The Best Summer Job — Initial Modeling Plan Draft

**Problem ID:** `2020_The_Best_Summer`
**Source:** HiMCM 2020
**Document type:** Modeling blueprint draft (planning only — no solution, no computation, no results)

---

## 1. Problem Background and Restatement

A team of high-school students must choose a "best" summer job from a set of heterogeneous opportunities. The jobs differ along many axes: compensation (hourly rate, weekly hours, duration), access/location (fully remote, walkable/bikeable, or requiring a drive or train), the nature of the work (physically active versus sedentary and analytical), scheduling flexibility, and non-monetary value (skill building, enjoyment, social contact, resume value). At the same time, students value discretionary time for recreation, exercise, outings, and socializing, and their individual financial needs and personal preferences differ.

This document **plans** how the problem will be modeled. It does **not** solve it. No data will be analyzed, no numbers computed, no model fitted, and no ranking produced here. The intent is to specify, in forward-looking terms:

- the factors that a model should consider (Sub-question 1),
- the structure and algorithm of a decision-support model that maps an individual student's situation and preferences to an evaluation of job options (Sub-question 2),
- how the model will be tested against a set of fictional student personas with plausible data (Sub-question 3),
- the data, implementation, and validation strategy that a later solving phase will execute.

The final intended deliverable for the solving phase will be a PDF of no more than 25 pages, consisting of a one-page Summary Sheet plus the complete solution. This draft is upstream of that artifact and will serve as its scaffolding.

---

## 2. Objectives and Subproblems

### 2.1 Overarching Objective

To design a general, transferable decision-support framework that lets *any* high-school student, given their own situation and preferences, evaluate and rank a set of summer-job offers in a principled, explainable, and reproducible way.

### 2.2 Subproblem 1 — Factor identification

- **Goal:** Enumerate and describe the factors a student should consider when comparing summer jobs.
- **Intended coverage:** compensation, time commitment, commute cost and time, transportation accessibility, schedule flexibility, physical-activity level, skill/resume value, social interaction, enjoyment, stress, job feasibility/attainment probability, and available recreation time.
- **Required classification for each factor:** quantitative or qualitative; constant or variable; deterministic or probabilistic; with units where applicable (e.g., currency/hour, currency/week, hours/week, minutes/day, kilometers, probability).
- **Planned output of the solving phase:** a structured factor table plus a discussion of why each factor matters and how factors interact.

### 2.3 Subproblem 2 — Model or algorithm

- **Goal:** Build a model (or coordinated set of models) that consumes a student's profile and preferences as inputs and returns an evaluation (score and/or ranking) of each candidate job.
- **Planned components:** a factor/weight elicitation mechanism; a normalization scheme that makes heterogeneous units comparable; a scoring/aggregation rule; and a sensitivity mechanism that shows how results respond to preference changes.
- **Design requirement:** the model must handle both quantitative and qualitative factors, and must be interpretable so that a student can see *why* one job ranks above another.

### 2.4 Subproblem 3 — Fictional-persona testing

- **Goal:** Validate the framework's behavior on at least ten fictional persons created with reasonable data.
- **Planned components:** a documented persona-generation methodology; a persona data table; and an analysis plan describing which behaviors (rankings, trade-offs, sensitivity patterns) will be examined.
- **Constraint:** the personas and their data are *designed inputs* for testing, not empirical observations.

### 2.5 Deliverable map

| Deliverable | Maps to | Status in this draft |
|---|---|---|
| Factor taxonomy and description | Subproblem 1 | Planned (§5, §4) |
| Decision model / algorithm | Subproblem 2 | Planned (§5, §6) |
| Persona test harness and analysis | Subproblem 3 | Planned (§4, §6, §7) |
| Summary Sheet + full solution PDF | Overall | Out of scope here |

---

## 3. Assumptions

The following assumptions are proposed to make the problem tractable. Each will be justified and revisited during validation.

**A1. Finite, known choice set.** A student evaluates a finite set of concrete job offers (on the order of a handful to a few dozen) rather than an open-ended market. *Justification:* decision support is realistic only over concrete alternatives. *Validation:* stress-test with varying set sizes.

**A2. Additive, compensatory preferences.** Multi-factor trade-offs can be reasonably approximated by a weighted aggregation in which a strong score on one factor can partly offset a weak score on another. *Justification:* widely used and explainable in MCDA; keeps the model transparent. *Validation:* compare against a non-compensatory (e.g., lexicographic or elimination) check.

**A3. Factor independence at aggregation time.** Factors will be treated as (near) independent in the base model, with interaction/penalty terms handled as optional extensions (e.g., available recreation time as a constraint rather than a raw factor). *Justification:* simplifies elicitation. *Validation:* test a variant with interaction terms and compare rankings.

**A4. Bounded rationality / satisficing allowed.** The "best" job is best *for a given student under their stated preferences and constraints*, not a universal optimum. *Justification:* mirrors the problem's framing of individual situations. *Validation:* persona-by-persona discussion.

**A5. Preference measurability.** Students can express factor importance on a bounded importance scale (or through pairwise comparisons) that is stable enough over the decision window. *Justification:* required for weighting. *Validation:* test weight perturbations (§7).

**A6. Time and money are the principal scarce resources.** The model will treat weekly time budget and money as the primary constraints, with recreation time derived from the time budget. *Justification:* directly reflects the problem's emphasis on earning versus free time. *Validation:* vary time budget and observe feasibility boundaries.

**A7. Probabilistic factors can be represented by distributions or scenario values.** Uncertain quantities such as the probability of actually landing a job offer, variability in hours, or transportation delays will be represented explicitly (probability, range, or scenario) rather than as fixed scalars. *Justification:* the problem explicitly distinguishes deterministic from probabilistic factors. *Validation:* scenario analysis in §7.

**A8. Monetary normalization uses a single reference period.** All income and cost quantities will be expressed over a common horizon (e.g., per summer season or per week) before aggregation. *Justification:* needed for comparability. *Validation:* unit-consistency checks.

**A9. Personas are illustrative, not empirical.** Fictional persons will be constructed for coverage of plausible student types, not sampled from a real population. *Justification:* the problem asks for fictional persons. *Validation:* documented construction rationale.

**A10. Non-monetary and qualitative factors are legitimately consequential.** Enjoyment, skill building, and social value are treated as real objectives, not soft afterthoughts. *Justification:* the problem explicitly values recreation and quality of experience. *Validation:* confirm they can change rankings in a sensible direction.

---

## 4. Data Processing Plan

No dataset is supplied with this problem; the "data" is (i) the structured description of job offers and (ii) the student preference/profile inputs, including the fictional personas. The processing plan therefore focuses on schema design, elicitation, transformation, and normalization.

### 4.1 Data sources and provenance

- **Synthetic/organizational inputs (planned):** job-offer records and persona profiles will be constructed by the team based on realistic, documented reasoning.
- **Optional external anchors (planned):** if used at all, minimum-wage references, typical commute speeds, or typical summer lengths may be cited as *context* for choosing plausible ranges; they will not be treated as a fitted dataset.
- **Provenance discipline:** every numeric range in the persona/job tables will carry a short justification note so that assumptions are auditable.

### 4.2 Proposed entity schema

- **Student profile entity:** identifier; weekly available time; start-up resources (e.g., transportation access, whether remote work is feasible); financial need/goal; physical-activity preference; desired recreation hours; factor weights; scheduling constraints.
- **Job-offer entity:** identifier; hourly rate; contracted hours/week; expected duration/weeks; work mode (remote/on-site); commute distance and mode; commute time and cost; activity type (physical/sedentary); skill-development tags; social-interaction level; flexibility rating; hiring probability; qualitative descriptors.
- **Evaluation entity (produced by the model):** per-job factor scores, aggregate score, rank, and the contribution breakdown.

### 4.3 Preprocessing steps (planned)

1. **Schema validation:** confirm every job/persona record contains all required fields; flag missing values.
2. **Unit harmonization:** convert all rates, hours, distances, times, and costs to a single consistent unit system per factor dimension.
3. **Horizon alignment:** convert weekly/daily quantities to a common seasonal horizon and, where useful, retain per-week views.
4. **Missing-data policy:** define fallback rules (e.g., default values, exclusion, or explicit "unknown" handling) before any scoring.
5. **Outlier/plausibility screening:** bound-check values (e.g., non-negative hours, rates within plausible range) to keep personas "reasonable" as the problem requires.

### 4.4 Feature construction (planned)

- **Net effective earnings:** gross income minus commute and other work-related costs over the horizon (definition fixed at modeling time, computed in the solving phase).
- **Time-budget features:** work hours, commute hours, and residual recreation time.
- **Activity-balance features:** degree of physical versus sedentary work relative to the student's preference.
- **Value features:** composite indices for skill development, social interaction, enjoyment, and flexibility derived from qualitative ratings via a documented scaling rule.
- **Risk features:** representation of hiring probability and hours variability.
- **Accessibility features:** whether the job is reachable given the student's transportation resources and time constraints.

### 4.5 Data usage strategy (planned)

- **Elicitation:** capture student preferences via a simple, documented instrument (importance ratings and/or pairwise comparisons) intended to be usable by non-experts.
- **Normalization:** map each factor onto a common bounded scale using a method chosen at modeling time (e.g., min–max, ratio-to-ideal, or utility curves), with direction (benefit vs. cost) fixed per factor.
- **Aggregation:** combine normalized factors with weights (§5).
- **Persona generation:** construct at least ten personas spanning the space of plausible students (see §6.4), each with a coherent preference profile and job set, so that the framework is exercised across regimes rather than at a single point.
- **Reproducibility:** all elicitation values, normalization choices, and persona records will be stored in a single documented input file so results can be regenerated.

---

## 5. Candidate Model Framework

### 5.1 Modeling paradigm

The core framework will primarily be a **Multi-Criteria Decision Analysis (MCDA)** approach, because the problem is inherently multi-objective (money vs. free time vs. work character vs. personal fit) with mixed quantitative/qualitative inputs. Complementary or alternative approaches will be considered and compared.

### 5.2 Candidate models (to be evaluated and selected in the solving phase)

1. **Weighted Sum Model (WSM) / weighted scoring.** Normalize each factor, weight by importance, sum. *Advantages:* transparent, easy for students to understand, fast. *Limitations:* fully compensatory; sensitive to normalization and weights.
2. **Weighted Product Model (WPM).** Multiplicative aggregation. *Advantages:* less prone to a single large factor dominating; scale-invariant behavior. *Limitations:* zero values are pathological; less intuitive.
3. **Analytic Hierarchy Process (AHP).** Pairwise comparisons to derive weights and consistency. *Advantages:* structured elicitation; consistency check. *Limitations:* comparison load grows with factor count.
4. **TOPSIS.** Rank by closeness to ideal and distance from anti-ideal. *Advantages:* intuitive "closest to ideal" semantics; handles benefit/cost directions naturally. *Limitations:* still depends on normalization and weights.
5. **Multi-Attribute Utility Theory (MAUT).** Encode preferences as utility curves per factor. *Advantages:* captures non-linear preferences (e.g., diminishing returns of extra hours) and risk attitude. *Limitations:* more elicitation effort.
6. **Goal programming / constraint-based optimization.** Treat recreation-time and income targets as goals/constraints and seek the least-violating option. *Advantages:* naturally expresses "earn enough while keeping free time." *Limitations:* requires target specification.
7. **Pareto-frontier / multi-objective view.** Present non-dominated trade-offs (e.g., income vs. recreation) rather than forcing a single scalar. *Advantages:* honest about incommensurable objectives. *Limitations:* may leave the student to choose among several.
8. **Probabilistic/scenario extensions.** Represent hiring probability and variable hours via expected value, scenario analysis, or simple Monte Carlo. *Advantages:* addresses the problem's probabilistic factor class. *Limitations:* requires distributional assumptions.

**Planned relationship among models:** a transparent weighted/utility core for the main ranking, with AHP as an optional weighting route, TOPSIS as a ranking cross-check, goal programming and Pareto views as complementary lenses, and a probabilistic layer to handle uncertain factors. The solving phase will justify a primary model and document the others as alternatives/robustness checks.

### 5.3 Variable specification (planned)

- **Decision variables:** the choice of job *j* from the offer set (a selection/sorting problem, not a continuous optimization).
- **Input parameters:** per-job factor values (rates, hours, commute, activity type, etc.); per-student weights and constraints.
- **Derived quantities:** net effective earnings, recreation hours, normalized factor scores, aggregate scores/utilities, ranks.
- **Uncertain quantities:** hiring probability, hours variability, commute variability, duration variability.
- **Constraints (planned):** maximum tolerable commute, minimum required recreation hours, minimum acceptable income (if specified), eligibility/accessibility.

### 5.4 Mathematical ideas to be used (planned, not executed)

- Normalization transforms and directed scoring.
- Weighted aggregation (sum, product) and utility functions.
- Pairwise-comparison eigenvector weighting with consistency ratio (AHP route).
- Distance-to-ideal ranking (TOPSIS route).
- Constraint/goal formulation (goal programming route).
- Expectation and scenario evaluation for probabilistic factors.
- Sensitivity/perturbation analysis of weights and inputs.

### 5.5 Advantages and limitations of the framework

- **Advantages:** interpretable to students; accommodates mixed data types; modular (swap weighting or aggregation); explicitly separates objectives; supports personalization; and exposes trade-offs rather than hiding them.
- **Limitations (to be acknowledged in the solution):** reliance on subjective weights; compensatory assumptions may mask hard constraints; normalization choice can shift rankings; qualitative ratings are coarse; probabilistic inputs rest on assumed distributions; and the "best" result is preference-conditional, not universal.

---

## 6. Implementation Roadmap

### 6.1 Solution workflow (planned)

1. **Factor specification:** finalize the factor taxonomy with classification and units (Subproblem 1 artifact).
2. **Schema & elicitation design:** define the student-profile and job-offer schemas and the preference-elicitation instrument.
3. **Normalization module design:** fix direction and scaling per factor.
4. **Weighting module design:** implement importance-rating and optional AHP routes.
5. **Aggregation module design:** implement the primary scoring rule plus alternates (WPM/TOPSIS/utility).
6. **Constraint/goal layer design:** encode recreation-time and income considerations.
7. **Probabilistic layer design:** specify how uncertain factors will be represented and evaluated.
8. **Persona construction:** design ten-plus fictional persons and their job sets.
9. **Test harness:** apply the model to each persona, capture rankings and contribution breakdowns.
10. **Sensitivity & robustness:** run weight/input perturbations and cross-model comparisons.
11. **Interpretation & write-up:** explain behavior, trade-offs, and limitations; assemble Summary Sheet and solution.

### 6.2 Algorithms (planned)

- Directed normalization (benefit vs. cost).
- Weighted aggregation; weighted product as a variant.
- Optional eigenvector-based pairwise weighting with a consistency check.
- TOPSIS distance ranking as a cross-check.
- Goal/constraint feasibility screening.
- Scenario/expected-value evaluation for uncertain factors.
- Perturbation sweeps for sensitivity analysis.

### 6.3 Required modules (planned architecture)

- **Input layer:** persona profiles, job-offer records, preference weights, constraints.
- **Transform layer:** unit harmonization, feature construction, normalization.
- **Model layer:** weighting, aggregation, constraint handling, probabilistic evaluation.
- **Analysis layer:** ranking, contribution decomposition, sensitivity sweeps, cross-model comparison.
- **Reporting layer:** tables describing factors, personas, and ranking behaviors (descriptive, not prescriptive results in this draft).

### 6.4 Fictional-persona design plan (Subproblem 3)

- **Coverage dimensions:** financial need (low/high), free-time preference (low/high), physical-activity preference (prefers active / prefers sedentary), transportation access (remote-capable / walk-bike / drive-train), risk tolerance, and skill-development priority.
- **Target:** at least ten personas chosen to span these dimensions, including boundary cases (e.g., a student who cannot drive, a student prioritizing savings, a student prioritizing training for a sport).
- **Job sets:** each persona will face a small varied set of offers differing in rate, hours, mode, and character, so comparisons are meaningful.
- **Data rationale:** every persona attribute and job value will be paired with a short justification so the fictional data is "reasonable," as required.
- **Analysis plan (descriptive):** the solving phase will report *how* rankings respond to persona type (e.g., whether higher-need personas favor higher-income jobs and whether active-preference personas penalize sedentary roles), together with any surprising or counterintuitive patterns and their causes.

### 6.5 Reproducibility and tooling (planned)

- Single documented input file for all persona/job/weight data.
- Deterministic pipeline with fixed seeds for any stochastic evaluation.
- Clear separation of model selection, weighting, and aggregation so variants can be swapped and compared.

---

## 7. Validation Strategy

### 7.1 Evaluation approach

Because the problem has no ground-truth "correct" ranking, validation will emphasize **internal consistency, robustness, and interpretability** rather than accuracy against a label.

### 7.2 Planned validation methods

1. **Face validity with personas:** check that rankings for each persona align with a sensible reading of that persona's stated priorities; document any mismatches.
2. **Weight sensitivity analysis:** perturb factor weights within reasonable ranges and observe ranking stability (identify fragile vs. robust decisions).
3. **Input perturbation:** vary job-factor values and student constraints to map decision boundaries.
4. **Model-to-model comparison:** compare rankings across WSM, WPM, AHP-weighted, TOPSIS, and utility variants; report where they agree and diverge.
5. **Constraint-vs-compensation check:** confirm that hard constraints (e.g., minimum recreation time, commute limits) are enforced and not silently traded away.
6. **Probabilistic robustness:** under scenario/expected-value treatment, examine whether uncertain factors flip rankings.
7. **Extreme/boundary cases:** include personas and jobs at the extremes to test behavior at the feasible edges.
8. **Explainability audit:** verify that each ranking can be decomposed into interpretable factor contributions.

### 7.3 Metrics (planned, mostly qualitative/ordinal)

- Rank stability under perturbation (ordinal agreement, e.g., share of top-choice jobs preserved).
- Rank correlation between model variants (planned as an ordinal agreement measure).
- Constraint-satisfaction rate (fraction of recommended options meeting hard constraints).
- Decomposition clarity (whether contributions explain the outcome).

### 7.4 Sensitivity analysis plan

- One-at-a-time weight sweeps to identify the most decision-critical factors.
- Multi-factor simultaneous perturbation to check for interaction effects.
- Threshold analysis: for each persona and job pair, how much a weight/value must change to flip the ranking.

---

## 8. Expected Result Interpretation

The solving phase is expected to produce, and this draft anticipates, the following *kinds* of findings (no numbers are computed here):

- **A factor taxonomy** that is comprehensive, classified, and unit-labeled, usable as a checklist by students.
- **A transparent model** whose outputs include not just a ranking but a contribution breakdown, so a student can see the drivers of a recommendation.
- **Persona-dependent rankings:** different personas will plausibly reach different "best" jobs, demonstrating that "best" is preference- and situation-conditional.
- **Identified trade-off structure:** likely a tension between income and recreation/commute time, with the model exposing rather than hiding it.
- **Robust vs. fragile decisions:** some top choices should remain stable across reasonable weight changes, while near-ties should be flagged as sensitive.
- **Qualitative factors mattering:** enjoyment, skill value, and social/activity fit should be capable of changing rankings, supporting the problem's emphasis on work character and lifestyle.

Interpretation guidance planned for the write-up: present the model as *decision support*, not as an oracle; state clearly that recommendations are conditional on inputs; and translate outputs into plain-language advice a high-school student could act on.

---

## 9. Limitations and Improvements

### 9.1 Anticipated limitations

- **Subjectivity of weights:** results depend on how preferences are elicited; different elicitation methods may shift outcomes.
- **Compensatory assumption:** a weighted sum can let a very high income offset a very poor fit; hard constraints mitigate but do not eliminate this.
- **Normalization sensitivity:** the choice of scaling can alter near-tie rankings.
- **Coarse qualitative scales:** transforming ratings (e.g., "high/low" enjoyment) into numbers is lossy.
- **Assumed probabilistic inputs:** hiring probability and hours variability require distributional assumptions that may be untestable from synthetic data.
- **Persona design bias:** fictional personas reflect the designers' imagination and may under-represent some real student situations.
- **Static single-period view:** the model may not capture within-summer dynamics (changing hours, renegotiation, multiple sequential jobs).

### 9.2 Planned improvements / extensions

- **Behavioral/robust methods:** consider robust or regret-based ranking to reduce sensitivity to weights.
- **Non-linear utility:** adopt utility curves to capture diminishing returns and risk attitude more faithfully.
- **Group decision support:** extend to multiple stakeholders (student plus family) with aggregated preferences.
- **Real-data calibration:** if real wage/commute data becomes available, calibrate ranges and validate qualitative scaling.
- **Dynamic/temporal modeling:** allow for multi-period planning (e.g., stacked or sequential summer jobs).
- **Constraint hardening:** elevate recreation time and accessibility from soft factors to explicit hard constraints where appropriate.
- **Tooling:** package the model as a simple interactive checklist/calculator that students can realistically use.
- **Equity considerations:** examine whether the framework behaves fairly across students with different access to transportation or remote work.

---

## Appendix — Scope and Compliance Note

This document is a **planning blueprint only**. It intentionally contains:

- no computed values, rankings, or fitted models,
- no data analysis or executed experiments,
- no final conclusions or solutions.

Its sole purpose is to specify the modeling workflow, assumptions, candidate methods, data-processing plan, implementation plan, and validation strategy that a subsequent solving phase will carry out for the HiMCM 2020 "The Best Summer Job" problem.
