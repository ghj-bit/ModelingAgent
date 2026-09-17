# Modeling Blueprint Draft

**Problem ID:** `2023_Preparing_for_Olympic`
**Title:** Preparing for Olympic Medal Ceremonies (MidMCM 2023, Problem C)
**Document type:** Initial modeling plan draft — roadmap only, not a solution.
**Status:** Planning artifact. Contains no computed results, no data analysis, and no final conclusions.

---

## 1. Problem Background and Restatement

The International Olympic Committee (IOC) will host the Paris 2024 Summer Olympic Games from July 26 to August 11, 2024. Invitations have been extended to 203 National Olympic Committees (NOCs). The Games are planned to feature 40 sports and 329 medal events spread across 37 venues, mostly in and around Paris but with at least one overseas location (Tahiti). Every medal event culminates in a medal ceremony at which Gold, Silver, and Bronze medals are awarded and the national flags of the winning countries are displayed.

The IOC must decide, in advance, how many medals and how many (and which types of) flags to order so that ceremonies are never interrupted by shortages while avoiding wasteful over-ordering and storage/logistics burdens. The core tension is between **supply adequacy** (a ceremony must never lack the right medal or flag) and **cost/efficiency** (inventory should not vastly exceed realistic need).

In planning terms, the task decomposes into three linked decisions:

1. **Venue schedule construction** — for a chosen venue among La Défense Arena, Bercy Arena, and Stade de France, construct a plausible medal-ceremony schedule consistent with the event program.
2. **Medal demand modeling** — for that venue, and then for all three venues, estimate medal quantities (Gold / Silver / Bronze) required.
3. **Flag demand modeling** — determine how many flags and which national flags are needed, accounting for repeat winners, simultaneous or overlapping ceremonies, and display/backup requirements.
4. **Communication and generalization** — articulate the model to the IOC and assess whether it will transfer to all 37 venues and to future Games, including the Winter Olympics.

Templates/anchors for scheduling and venue facts will be drawn from the referenced public sources listed in the problem; the model is expected to be transparent and defensible rather than exhaustive.

---

## 2. Objectives and Subproblems

### 2.1 Primary objective
Design a modeling framework that determines an appropriate order quantity of medals and flags for Olympic medal ceremonies such that expected shortages are minimized while surplus is bounded, and that generalizes across venues and Games.

### 2.2 Subproblems
- **SP1 — Schedule design.** Choose and justify one focus venue (La Défense Arena, Bercy Arena, or Stade de France). Propose a structured method to build a medal-ceremony schedule for that venue.
- **SP2 — Medal demand model.** Formulate a model mapping event/venue characteristics to the number of Gold, Silver, and Bronze medals required (including a reasoned safety margin).
- **SP3 — Flag demand model.** Formulate a model for flag count and flag-type composition, capturing winners-per-NOC, concurrency, ceremony display needs, and backup policy.
- **SP4 — Cross-venue application.** Specify how the SP2/SP3 models will be applied to the other two venues and then to all three collectively (aggregate vs. per-venue inventory).
- **SP5 — Communication.** Plan a 1–2 page IOC letter structure explaining the model and its effectiveness.
- **SP6 — Generalization/reflection.** Plan an assessment of applicability to all 37 venues, future Summer Games, and the Winter Olympics.

### 2.3 Deliverables (planned)
- A schedule template for the selected focus venue.
- Two linked demand models (medals, flags) with defined variables and parameters.
- A generalization protocol and sensitivity framework.
- A structured outline for the IOC letter (not written here).

---

## 3. Assumptions

The following assumptions are proposed for later validation. Each is stated with a rationale and a planned validation approach.

### 3.1 Structural / scope assumptions
- **A1.** Every one of the 329 medal events produces exactly one Gold, one Silver, and one Bronze award. *Justification:* standard Olympic convention. *Validation:* cross-check against official event counts and any documented exceptions (e.g., ties, shared awards) from public sources.
- **A2.** A medal ceremony is associated with a specific event and occurs at a determinable venue and time. *Validation:* reconcile against published Paris 2024 schedule sources.
- **A3.** The focus venue hosts a well-defined subset of events; the schedule can be constructed from event-to-venue assignment. *Validation:* verify venue capacity/usage plausibility.
- **A4.** Each participating NOC is identified by a unique country code and a unique flag design. *Validation:* check NOC list consistency and edge cases (e.g., neutral athlete designations).

### 3.2 Demand-behavior assumptions
- **A5.** Medal outcomes are uncertain ex ante, so demand must be modeled probabilistically (or with worst-case bounds) rather than deterministically. *Validation:* compare probabilistic and worst-case inventories for reasonableness.
- **A6.** Flag demand is driven by ceremony display rules and possibly repeat-winner reuse; flags may be reusable across ceremonies within a session/venue. *Validation:* test sensitivity to reuse vs. non-reuse assumptions.
- **A7.** Each ceremony requires displaying the flags of Gold, Silver, and Bronze medalists simultaneously (three flags per ceremony), subject to flag-design reuse. *Validation:* confirm against observed medal-ceremony practice from public descriptions.

### 3.3 Operational assumptions
- **A8.** Backup/safety stock is required to cover breakage, loss, defective items, or ceremony failure. *Validation:* sensitivity analysis over safety-stock fractions.
- **A9.** Medal and flag inventory may be shared or pooled across venues, or held per venue; both policies will be modeled. *Validation:* compare pooled vs. distributed policies.
- **A10.** Initial planning may treat each NOC as equally likely to win any given event, then relax this with seeding/strength priors. *Validation:* compare uniform-prior results against strength-informed priors.

### 3.4 Neutral / boundary assumptions
- **A11.** Overseas venues (e.g., Tahiti) impose additional logistics lead time that could justify extra buffer. *Validation:* scenario analysis on lead time.
- **A12.** Data used is limited to public reference material and the problem statement (no confidential IOC data). *Validation:* document all sources and mark estimated values.

---

## 4. Data Processing Plan

No data will be analyzed in this draft; the plan below describes how data will be obtained, prepared, and used later.

### 4.1 Data sources (planned)
- Problem statement facts (203 NOCs, 40 sports, 329 events, 37 venues, date range).
- Referenced IOC / Paris 2024 public pages (event list, schedule, venue concept).
- Any provided auxiliary files/tables (e.g., event-to-venue listings) if present in the workspace.

### 4.2 Data acquisition / extraction
- **D1.** Enumerate medal events and map them to sports and venues.
- **D2.** Enumerate NOCs and their flag identifiers.
- **D3.** Extract venue event assignments and daily schedule structure for the three target venues.

### 4.3 Preprocessing (planned)
- Standardize event names, venue names, and NOC codes (normalization and de-duplication).
- Resolve missing/ambiguous venue assignments with documented rules and flags for unknowns.
- Build a tidy event–venue–day–session table.
- Define a consistent "ceremony unit" record (one per event) with venue, day, session, and medal set.

### 4.4 Feature construction (planned)
- Venue-level aggregates: number of events, events per day, peak events per session/day.
- Concurrency features: simultaneous ceremonies needing the same flag design.
- NOC-level features: expected participation, prior strength proxies (optional), regional representation.
- Reuse features: flag-design reuse opportunities within/between ceremonies.

### 4.5 Data usage strategy
- Training/calibration vs. scenario data separation if historical results are used.
- Explicit separation of **known structure** (schedule, venues, NOC list) from **uncertain quantities** (winners, medaling NOCs).
- Documented provenance and uncertainty tags for every field.

---

## 5. Candidate Model Framework

### 5.1 Schedule construction model (SP1)
- **Candidate approaches:** (a) rule-based assignment using published event–venue mapping; (b) constraint-based scheduling (each event assigned once; venue/day capacity respected); (c) template matching to the official daily schedule structure.
- **Key variables:** event index, venue, day, session, ceremony time slot, number of ceremonies per slot.
- **Math ideas:** bipartite matching / assignment problem, capacity constraints, precedence by session.
- **Advantages/limits:** constraint models are explainable and auditable; they depend heavily on the accuracy of venue assignments and may not capture broadcast/operational nuances.

### 5.2 Medal demand model (SP2)
- **Candidate approaches:**
  - (a) Deterministic floor model: medals = number of events at venue (×3 types), plus safety stock.
  - (b) Probabilistic demand model: treat winners as random; estimate distributions for counts and buffer via quantiles.
  - (c) Robust/worst-case model: size inventory so shortage probability stays below a target.
- **Key variables:** events per venue by type, demand distribution parameters, target service level, safety-stock fraction, per-item loss rate.
- **Math ideas:** binomial/multinomial sampling of winners, quantile-based safety stock, newsvendor-style framing, mixed integer bounding.
- **Advantages/limits:** (a) is transparent but ignores risk; (b) captures risk but needs distributional assumptions; (c) is conservative but may over-order.

### 5.3 Flag demand model (SP3)
- **Candidate approaches:**
  - (a) Coverage model: one flag per potential winning NOC per ceremony context (worst case 203 × 3).
  - (b) Reuse-aware model: count distinct flag designs needed concurrently × safety margin.
  - (c) Probabilistic model: estimate expected number of distinct medals-winning NOCs, size inventory to a service level.
- **Key variables:** flag designs (country flags), per-ceremony flag requirement, concurrency peak, reuse policy, replacement rate, spare stock.
- **Math ideas:** set-cover / distinct-count estimation, occupancy problems (balls-in-bins), expected distinct winners under uniform or weighted priors, peak concurrent demand.
- **Advantages/limits:** (a) trivially safe but wasteful; (b) realistic but requires scheduling concurrency detail; (c) efficient but prior-sensitive.

### 5.4 Cross-venue aggregation model (SP4)
- **Candidate approaches:** per-venue inventories vs. pooled central inventory vs. hybrid (central + venue buffers).
- **Math ideas:** portfolio/aggregation effects (pooling reduces total buffer), multi-location inventory with lead time.
- **Advantages/limits:** pooling lowers totals but increases logistics complexity; must weigh against overseas venue lead times.

### 5.5 Generalization framework (SP6)
- Parameterized model where venue count, event count, NOC count, and Games type (Summer/Winter) are inputs, to test transferability.

---

## 6. Implementation Roadmap

Although no code is written here, the following module structure is planned:

1. **Data module** — load and normalize event/venue/NOC lists; produce tidy tables.
2. **Schedule module** — apply the chosen schedule-construction method to the focus venue, then to the other two.
3. **Medal demand module** — compute deterministic and probabilistic inventory requirements with configurable service level and buffer.
4. **Flag demand module** — compute coverage, reuse-aware, and probabilistic flag requirements.
5. **Aggregation module** — combine venus under pooled vs. distributed policies.
6. **Sensitivity module** — sweep key parameters (service level, safety stock, reuse, prior weights).
7. **Reporting module** — assemble model descriptions, tables, and the IOC letter outline (written later by the solver, not here).

Planned workflow: define inputs → build schedule → generate demand distributions → compute inventory under policies → sensitivity sweeps → document. Each module should expose parameters so assumptions (Section 3) are easy to vary.

---

## 7. Validation Strategy

### 7.1 Evaluation metrics (planned)
- **Shortage risk:** probability that demand exceeds inventory per venue/type (target service level).
- **Surplus/overage:** excess inventory relative to expected need (cost proxy).
- **Coverage:** fraction of scenarios in which all ceremonies are fully supplied.
- **Robustness:** stability of recommended quantities across parameter ranges.

### 7.2 Validation methods
- **Internal consistency:** deterministic floor must be ≤ probabilistic recommendation must be ≤ worst-case bound.
- **Cross-checks:** schedule totals should reconcile with event counts; flag types should reconcile with NOC list.
- **Scenario testing:** uniform vs. strength-weighted priors; reuse vs. no-reuse; pooled vs. distributed.
- **Backcasting (if historical data available):** apply the model to a past Games' winners and compare recommended vs. required quantities.

### 7.3 Sensitivity analysis (planned)
- Vary service level, safety-stock fraction, per-item loss rate, concurrency assumptions, and NOC strength priors.
- Identify which parameters most influence recommended totals and where model recommendations change materially.

---

## 8. Expected Result Interpretation

This section describes how results will be read once produced (no results are produced here).

- **Recommended medal quantities** would be interpreted as a function of event counts, service level, and buffer, with the deterministic count forming a lower anchor and the robust bound forming an upper anchor.
- **Recommended flag sets** would be interpreted through the lens of coverage vs. reuse: a coverage-based number represents an upper bound, while a reuse-aware/probabilistic number represents the efficient target, with the gap explained by concurrency and winner diversity.
- **Cross-venue aggregation** would be read as a trade-off between pooling economies and logistics/lead-time risk.
- **Model effectiveness** (for the IOC letter) would be framed as: adequacy guaranteed at a stated service level, surplus bounded, and parameters explainable to a non-technical audience.

---

## 9. Limitations and Improvements

### 9.1 Anticipated limitations
- Dependence on assumption A5–A7 for probabilistic and reuse behavior; results shift meaningfully with these assumptions.
- Venue event assignments may be incomplete or ambiguous, weakening schedule realism.
- Uniform-likelihood priors may misrepresent medal concentration among strong NOCs.
- Cost data (unit medal/flag cost, storage, transport) is not provided; efficiency framing will rely on proxies.
- Transfer to Winter Olympics changes event mix, venue count, and NOC composition; parameters must be revisited.

### 9.2 Planned improvements
- Incorporate strength/prior information (e.g., historical medal tables) to refine winner distributions.
- Model ties/shared medals and any multi-bronze events explicitly.
- Add time-phased supply (deliveries during the Games) rather than a single pre-order.
- Expand aggregation modeling to include transport lead time and overseas venues.
- Validate against at least one historical Games as a sanity benchmark.

---

## Verification Checklist (self-check for this draft)

- [x] `draft.md` created at the required path.
- [x] Contains only planning content (workflow, assumptions, candidate methods, data plan, implementation plan, validation).
- [x] No computed results, no data analysis, no executed experiments, no final conclusions.
- [x] Future-oriented language used throughout.
