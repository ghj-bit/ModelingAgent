# Jet Lag — Modeling Blueprint Draft

**Problem ID:** `2017_Jet_Lag` · **Source:** IM2C 2017
**Document type:** Initial modeling plan draft (roadmap only — no solving performed)
**Status:** Planning / pre-modeling

> This document is a *blueprint*. It describes how the problem **will** be modeled, what
> assumptions **will** be made, which candidate methods **will** be considered, and how
> results **will** be validated. It intentionally contains **no computed results, no data
> analysis, no fitted models, and no final conclusions.**

---

## 1. Problem Background and Restatement

### 1.1 Context
The International Meeting Management Corporation (IMMC) needs an algorithm that recommends
the best place(s) to hold an international meeting. Participants travel from home cities
scattered across the globe to a meeting location. Recent travel across time zones (and, to a
lesser degree, across climates and seasonal regimes) produces jet lag that can impair the
intellectual performance of participants during a short, intensive meeting. The meeting
consists of roughly three intensive days of hard intellectual teamwork with roughly equal
contribution from all participants. Cost is a secondary criterion subject to a limited
budget; the IMMC cannot afford to bring participants in a week early to acclimatize, nor to
grant recovery time afterward.

### 1.2 Restatement (what the algorithm must do)
Given:
- the set of participants and their home cities,
- approximate meeting dates,
- any additional client-supplied information the IMMC may request,

the algorithm should output a **ranked list of recommended meeting locations** (regions,
time zones, or specific cities) that **maximize overall meeting productivity**, with
**cost as a secondary, tie-breaking / constrained criterion**.

### 1.3 Why this is nontrivial
- Participants are distributed globally, so no location is convenient for everyone.
- Jet lag depends jointly on direction of travel, number of time zones crossed, arrival
  lead time, local time-of-day scheduling, individual physiology, and seasonal/climate
  factors.
- Productivity over a multi-day meeting is a *dynamic* quantity (day-1 impairment differs
  from day-3 impairment), so a single scalar "distance" objective is insufficient.
- The feasibility set (cities worldwide) is effectively continuous at the city level but
  discrete at the airport/region level, and cost adds a secondary layer.

### 1.4 Deliverables (planned)
1. A formal objective/utility formulation of "overall meeting productivity."
2. A candidate-location scoring pipeline (features → productivity score).
3. A recommendation/ranking mechanism over candidate locations with cost as a secondary
   criterion.
4. A validation and sensitivity framework supporting the two required scenarios.

---

## 2. Objectives and Subproblems

### 2.1 Primary objective
Maximize the expected aggregate intellectual productivity of all participants across the
three intensive meeting days, evaluated at candidate meeting locations.

### 2.2 Secondary objective
Among locations with comparable primary productivity, prefer lower total/derived cost,
subject to a budget ceiling.

### 2.3 Subproblems (planned decomposition)
- **SP1 — Jet-lag quantification.** Define a per-participant, per-day impairment measure
  as a function of travel direction, time-zone shifts, arrival lead time, and meeting
  schedule.
- **SP2 — Circadian/adaptation modeling.** Represent how a participant's internal clock
  shifts toward destination local time over the days of the meeting.
- **SP3 — Aggregation / group productivity.** Combine individual impairments into a group
  productivity measure that respects the "approximately equal contribution" premise
  (e.g., bottleneck/average/weighted aggregation).
- **SP4 — Candidate location space.** Define and enumerate the discrete set of candidate
  meeting locations (global cities / time zones / regions).
- **SP5 — Scheduling interaction.** Decide how meeting-time-of-day choices (start times,
  break placement) can mitigate residual desynchrony.
- **SP6 — Cost layer.** Define a secondary cost proxy and integrate it as a soft constraint
  or tie-breaker.
- **SP7 — Scenario instantiation.** Instantiate the framework on the two required scenarios
  (mid-June small meeting; January big meeting).
- **SP8 — Ranking & explanation.** Produce a ranked recommendation list with interpretable
  rationale.

### 2.4 Success criteria for the plan (planned)
- The blueprint must be internally consistent: objectives ↔ assumptions ↔ features ↔
  model ↔ validation must line up.
- Both required scenarios must be expressible within the same framework without bespoke
  hacks.
- Validation must be defined *before* results are interpreted.

---

## 3. Assumptions

Each assumption is listed with a working justification and a future validation approach.

### A1 — Productivity is monotonically decreasing in jet-lag impairment, per day.
- *Justification:* Cognitive performance literature commonly links circadian misalignment to
  reduced attention/decision quality.
- *Future validation:* stress-test monotonicity by examining ranking stability under
  alternative impairment→productivity mappings (e.g., linear vs. saturating).

### A2 — Impairment is driven primarily by time-zone shift magnitude and direction.
- *Justification:* Eastward travel is generally harder to adapt to than westward; shift
  magnitude dominates.
- *Future validation:* compare rankings with and without directional asymmetry.

### A3 — Adaptation proceeds at a bounded daily rate toward destination time.
- *Justification:* Circadian phase shifts progress gradually; a per-day adaptation rate is
  a standard simplification.
- *Future validation:* sweep the adaptation rate and observe rank stability.

### A4 — Arrival lead time is fixed/short (no pre-meeting acclimatization week).
- *Justification:* Explicitly stated by IMMC constraints.
- *Future validation:* treat lead time (e.g., 0–2 days) as a scenario parameter and check
  sensitivity.

### A5 — Meeting days are roughly equal in workload and contribution.
- *Justification:* Stated in the problem ("approximately equally").
- *Future validation:* test weighted aggregation variants.

### A6 — Group productivity aggregates individual productivities with a bottleneck or
weighted-average rule.
- *Justification:* Team intellectual work is often limited by the least-fit member; average
  captures total throughput.
- *Future validation:* compare bottleneck, mean, and trimmed-mean aggregations.

### A7 — Climatic/seasonal mismatch is a secondary modifier, not the primary driver.
- *Justification:* The problem stresses time zones first, climate/season second.
- *Future validation:* include a mild climate-mismatch penalty and test its marginal effect.

### A8 — Any city/region is a feasible venue (no visa/political constraints).
- *Justification:* Explicitly stated assumption in the problem.
- *Future validation:* not needed for correctness; document as given.

### A9 — Cost is a proxy and secondary; a coarse cost model suffices.
- *Justification:* Problem says cost is not of primary importance but budget is limited.
- *Future validation:* sensitivity to cost weighting; confirm primary ranking is stable.

### A10 — Participants' chronotypes are homogeneous unless data suggests otherwise.
- *Justification:* No individual-level data supplied.
- *Future validation:* add chronotype heterogeneity as an extension (morning/evening types).

---

## 4. Data Processing Plan

> Plan only. No data will be analyzed or transformed in this draft.

### 4.1 Input data (expected)
- **Participant roster:** home city per participant, with multiplicity (e.g., Scenario 2 has
  duplicate cities).
- **Meeting timing:** approximate dates (mid-June; January) and duration (3 days).
- **Geographic reference data:** city → country/region, latitude/longitude.
- **Temporal reference data:** city/region → UTC offset (and, where relevant, daylight
  saving behavior for the given dates).
- **Cost proxy data (optional, coarse):** travel distance or a coarse fare/route proxy.

### 4.2 Preprocessing steps (planned)
1. **City normalization:** canonical names, resolve duplicates (e.g., two participants from
   the same city) while preserving counts.
2. **Timezone resolution:** map each city to a UTC offset for the specific meeting period,
   accounting for DST where applicable (mid-June vs. January matter).
3. **Time-zone-shift computation:** for each (home city, candidate location) pair, compute
   signed shift = candidate offset − home offset (positive = eastward).
4. **Distance/route proxy:** compute great-circle distance as a stand-in for travel burden
   and as an input to the cost proxy.
5. **Season/climate tagging:** attach a coarse hemisphere/season tag based on date to
   support the secondary climate-mismatch modifier.
6. **Missing-data policy:** define defaults (e.g., assume a standard adaptation rate) and
   document all fallbacks.

### 4.3 Feature construction (planned)
Per (participant, candidate location) pair:
- signed time-zone shift (magnitude + direction),
- absolute shift,
- great-circle travel distance (or route proxy),
- estimated arrival lead time (scenario parameter),
- seasonal/climate mismatch flag or magnitude,
- destination local time of meeting start (for scheduling interaction).

Per candidate location (aggregated over participants):
- distribution of individual shifts (mean, max, spread),
- bottleneck impairment (worst-off participant),
- count of participants crossing a threshold shift,
- aggregated cost proxy.

### 4.4 Data usage strategy
- **Required scenarios** instantiate the framework end-to-end (validation targets).
- **Synthetic candidate grid** (global sample of cities/time zones) supports ranking and
  sensitivity sweeps.
- **No data will be analyzed in this phase**; this section only fixes the schema and
  contracts for later implementation.

---

## 5. Candidate Model Framework

> Candidate methods only. Selection will happen during implementation based on validation.

### 5.1 Variables (planned notation)
- Participants `i = 1..N`, home offset `H_i`, home coordinates.
- Candidate location `c` with offset `O_c`.
- Signed shift `Δ_i(c) = O_c − H_i`; magnitude `|Δ_i(c)|`.
- Meeting days `d = 1..3`.
- Adaptation parameter `k` (zones adapted per day).
- Residual desynchrony after `d` days: a function of `Δ_i(c)`, `k`, and lead time.
- Per-participant day-`d` impairment `imp_i(c,d)`.
- Per-participant day-`d` productivity `p_i(c,d)` (decreasing in impairment).
- Group productivity `P(c)` (aggregation over `i`, and over `d`).
- Cost proxy `Cost(c)`; budget `B`; cost weight `λ`.

### 5.2 Candidate modeling approaches

**(a) Deterministic phase-adaptation model (baseline).**
Model residual desynchrony as initial shift reduced by a bounded daily adaptation rate,
then map residual to impairment. Simple, interpretable, fast to sweep.

**(b) Weighted/additive utility model.**
Group productivity as a weighted sum of per-participant, per-day productivity terms, with
optional asymmetry for travel direction and day-index decay.

**(c) Bottleneck / min-based aggregation model.**
Group productivity governed by the least-productive participant, capturing the "team is
limited by its weakest member" intuition; can be blended with the mean.

**(d) Directionally asymmetric shift model.**
Explicitly penalize eastward shifts more than westward shifts, and treat small shifts as
near-negligible.

**(e) Scheduling-interaction model.**
Optimize meeting start time-of-day (and break placement) jointly with location to reduce
residual desynchrony impact.

**(f) Cost-constrained selection model.**
Augment the productivity objective with a cost proxy via a soft penalty `λ·Cost(c)` or a
hard budget constraint with productivity maximization.

**(g) Multi-criteria ranking model.**
Combine productivity (primary) and cost (secondary) into a lexicographic or
Pareto-frontier ranking, exposing trade-offs rather than collapsing them.

### 5.3 Mathematical ideas underpinning candidates
- Monotone decreasing maps from |residual shift| to productivity.
- Satisficing/bounded adaptation dynamics (phase progresses but not instantaneously).
- Aggregation operators: mean, min (bottleneck), trimmed mean, ordered weighted averaging.
- Directional asymmetry terms in the per-participant cost.
- Lexicographic or weighted-sum scalarization for multi-criteria ranking.
- Sensitivity sweeps over free parameters (adaptation rate, impairment slope, cost weight).

### 5.4 Advantages / limitations (planned)
- *Advantages:* interpretable, scenario-reusable, low data requirements, easy to
  sensitivity-test, decomposable into independently validatable modules.
- *Limitations:* coarse physiological realism, homogeneous chronotype assumption,
  approximate climate modifier, coarse cost proxy, no individual-level empirical data.

---

## 6. Implementation Roadmap

> Roadmap only. No code will be written or run in this phase.

### 6.1 Proposed module structure
1. `ingest` — load participant rosters and scenario parameters.
2. `geo` — city normalization, timezone resolution, distance computation.
3. `features` — build (participant × candidate) and (candidate) feature tables.
4. `impairment` — compute per-participant, per-day impairment.
5. `productivity` — map impairment to individual/group productivity.
6. `selector` — candidate scoring, ranking, cost layer, budget handling.
7. `sensitivity` — parameter sweeps and stability diagnostics.
8. `report` — assemble ranked recommendations with explanations.

### 6.2 Planned workflow
1. Encode assumptions A1–A10 as explicit, swappable configuration.
2. Build the geographic/timezone reference layer for the two scenario dates.
3. Generate the candidate location set (scenario-grounded + global sample grid).
4. Compute features for each (participant, candidate) pair.
5. Apply the impairment model and per-day productivity mapping.
6. Aggregate to group productivity; layer cost.
7. Rank candidates; extract top-K with rationale.
8. Run sensitivity sweeps; record stability of the ranking.
9. Produce per-scenario recommendation artifacts.

### 6.3 Algorithmic choices to evaluate
- Enumerate-and-score for discrete candidate grids; continuous/regional refinement optional.
- Joint optimization over start-time-of-day when scheduling interaction is enabled.
- Lexicographic vs. weighted-sum multi-criteria handling for the cost layer.

### 6.4 Required resources / interfaces
- A scenario definition contract (participants, dates, duration, budget, parameters).
- A candidate-location dataset (cities/regions with offsets and coordinates).
- A configuration surface exposing all assumption parameters for sensitivity testing.

---

## 7. Validation Strategy

### 7.1 Evaluation metrics (planned)
- **Primary:** aggregate group productivity score per candidate location.
- **Ranking metrics:** top-K overlap / rank correlation across model variants.
- **Robustness:** spread of scores and rank stability under parameter perturbation.
- **Interpretability:** whether top recommendations admit a clear jet-lag rationale.
- **Constraint checks:** budget feasibility and cost-secondary compliance.

### 7.2 Validation methods (planned)
- **Scenario grounding:** run both required scenarios and check the recommendations are
  sane relative to the geographic spread of participants.
- **Cross-model agreement:** compare deterministic vs. bottleneck vs. asymmetric variants.
- **Ablation:** remove individual components (direction asymmetry, climate modifier, cost
  layer) and observe impact.
- **Internal consistency:** verify monotonicity and limiting-case behavior (zero shift →
  full productivity; extreme shift → severe impairment).
- **Edge cases:** single participant, participants all in one time zone, antipodal spread.

### 7.3 Sensitivity analysis (planned)
- Sweep adaptation rate `k` and impairment slope.
- Sweep cost weight `λ` and budget ceiling `B`.
- Sweep arrival lead-time assumptions (0–2 days).
- Sweep aggregation rule (mean vs. bottleneck vs. trimmed mean).
- Report which recommendations are stable vs. parameter-sensitive.

### 7.4 Validation acceptance (planned)
- Recommendations should be stable within a documented tolerance band across reasonable
  parameter ranges, or the instability must be explicitly characterized and reported.

---

## 8. Expected Result Interpretation

> Interpretive framing only — no results are produced here.

- The algorithm is expected to output a **ranked list of candidate locations**, likely
  favoring venues that minimize the *worst-case* and *average* jet-lag burden across the
  participant mix, rather than favoring any single participant.
- Different aggregation philosophies (mean vs. bottleneck) are expected to produce
  potentially different top choices; the interpretation will report both and explain the
  divergence.
- Cost is expected to act as a secondary discriminator among productivity-comparable
  candidates.
- Results will be presented as **recommendations with rationale and uncertainty bands**,
  not as a single definitive answer.
- The two required scenarios will be reported side by side to show how participant
  geography (widely vs. moderately spread) shapes the recommendation.

---

## 9. Limitations and Improvements

### 9.1 Known limitations (planned)
- No individual-level physiological or chronotype data; heterogeneity is assumed away.
- Simplified adaptation dynamics and impairment→productivity mapping.
- Coarse climate/season moderation; coarse cost proxy.
- Candidate space discretization may miss optimal intermediate venues.
- Homogeneous treatment of travel fatigue vs. pure time-zone shift.

### 9.2 Planned improvements / extensions
- Introduce chronotype heterogeneity (morning/evening types) and personality/workload
  factors.
- Replace coarse cost proxy with route-aware or fare-aware estimates.
- Add joint optimization of meeting schedule (start time, break placement) with location.
- Extend to multi-city or regional (zone-level) recommendations and hierarchical venues.
- Incorporate any client-supplied constraints (accessibility, language, facilities) as
  additional soft criteria.
- Calibrate parameters against any available empirical performance/adaptation literature
  if the IMMC can supply it.

### 9.3 Scope discipline
This draft deliberately stops at the planning boundary. All numeric results, data
exploration, model fitting, and conclusions are deferred to the implementation phase.

---

*End of initial modeling blueprint draft.*
