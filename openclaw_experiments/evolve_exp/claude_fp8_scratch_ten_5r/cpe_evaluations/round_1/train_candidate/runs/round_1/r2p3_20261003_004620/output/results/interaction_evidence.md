# Expert Interaction Evidence (Problem 2021_C, Vespa mandarinia triage)

Ten exchanges, one question each. For each: the question, a summary of the reply, and how the
reply was converted into a parameter, constraint, or change in the model/code (with where).

## Exchange 1 — First verification step (triage mechanism)
- **Q:** In Washington, when the public reports a suspected Asian giant hornet, what is the agency's usual first step to check the report?
- **Reply (gist):** First step is remote desk review by state entomology staff: photos/video + notes compared against known AGH appearance vs look-alikes; this produces Negative ID / Unverified status. Only reports with strong evidence (specimen, clear close-up, trained observer) trigger follow-up contact, site visit, or trap placement.
- **Used in work:** Defines the two-stage verification process. Task 3 queue is built as desk-review-first (free filter) + field-visit queue (scarce resource); the operating model's cost structure (free desk review vs ~half-day field visit) comes from this. Also justifies treating "Unverified" as the pool the model must prioritize.

## Exchange 2 — Dominant look-alikes
- **Q:** Among false reports that turn out to be false, which insects are mistaken most often?
- **Reply (gist):** Other large wasps/hornets — European hornet (Vespa crabro), yellowjackets/bald-faced hornets (Dolichovespula), paper wasps; also bumble bees, carpenter bees, hoverflies; the lab comments in the dataset typically name these.
- **Used in work:** Cross-checked against data: among the 2,069 negatives, 444 lab comments name a confuser; counts: bumble bee 79, yellowjacket 54, paper wasp/Polistes 44 (combined), European hornet 2. This empirical check validated the k_bee feature (bumble-bee confuser signal) and is reported in Task 2 analysis and outcome.

## Exchange 3 — Value of a specimen / clear photo
- **Q:** When you see a report with a clear close-up photo or a captured specimen, how much does that raise confidence it is really a giant hornet?
- **Reply (gist):** Substantially — the single strongest evidence short of a confirmed nest; a specimen is essentially confirmatory; distant/blurry photos or text-only remain weak because look-alikes are easily confused at a distance.
- **Used in work:** Motivates the k_specimen feature (specimen commitment in notes) and the hard override rule R1 in Task 3 (specimen-committing reports queue ahead of model scores < 0.5). Data check: k_specimen has coefficient +1.06 (odds ~x2.9), the strongest positive coefficient; 13 of the top-28 unverified reports have k_specimen = 1.

## Exchange 4 — Seasonal pattern of false reports
- **Q:** Do false reports show a pattern by month or season? If so, roughly what?
- **Reply (gist):** Strong seasonal pattern: peak late summer/early fall (~Aug-Oct, largest colonies, foraging workers, active queens), smaller spring rise (Apr-Jun, overwintering queens emerge), lowest in winter (Dec-Feb).
- **Used in work:** Justifies cyclical month encoding (sin_m, cos_m) in the logistic model rather than linear month terms. Data check: reports peak Aug 2020 (1,346) / Sep 2020 (656), trough Feb (3); uniformity chi-square X2=1868.5, p<1e-300; cos_m coefficient +1.75 (second-largest in the model). Reported in Tasks 1 and 2.

## Exchange 5 — Spatial pattern / observer density
- **Q:** Do false reports concentrate in certain kinds of places (farms, gardens, suburbs)? Any clear pattern?
- **Reply (gist):** Concentrate in residential/suburban areas (yards, gardens, porches, parks) because that is where people are and where flowering habitat attracts look-alikes; rural/farm produces a share too but fewer people report. Key point: it is a reporting-effort/observer-density pattern, not a hornet-habitat pattern; spatial models should account for population density.
- **Used in work:** Motivates the n_reports_25km feature (count of other reports within 25 km) as a population-density/reporting-effort proxy, and the explicit caveat (in Task 2 limitations) that "no reports" ≠ "no hornets" in rural areas.

## Exchange 6 — Clustering near confirmed sightings
- **Q:** Do false reports cluster near real confirmed hornet sightings? Why?
- **Reply (gist):** Yes — two mechanisms: (1) attention/awareness spillover after publicized detections raises local reporting effort (and hence false reports); (2) genuine look-alike co-occurrence (the same habitat that produces a real detection produces plausible false reports). Consequence: proximity to a confirmed sighting is informative but confounded; use it as a feature while controlling for local reporting effort, not as a standalone signal.
- **Used in work:** Directly drove the leakage decision: distance-to-nearest-positive (dist_pos_km) and staff-submission markers (k_employee) were EXCLUDED from the operating model. A reference fit including them reached AUC 0.9942 vs 0.847 for the leak-safe model — the gap is quantified and reported as a leakage ceiling, not capability (Task 2). n_reports_25km is kept as the confounding control per the expert's advice.

## Exchange 7 — Post-confirmation response timing
- **Q:** How long does the agency typically wait after a confirmed sighting before sending crews back to recheck the area?
- **Reply (gist):** No fixed interval — acts within days to ~1-2 weeks, with immediate intensified trapping/visual surveys in a roughly 1-5 km radius repeated through the active season (through October); if nothing found, surveillance continues at reduced intensity into the next season (undetected nest could produce overwintering queens).
- **Used in work:** Defines the post-positive protocol in Task 3 (on a positive: switch the 1-5 km radius to intensive trapping through October) and the 30 km at-risk region guard in Task 5's eradication rule. The "reduced intensity into next season" point supports the 3-season (not 1-season) eradication window.

## Exchange 8 — Eradication evidence standard
- **Q:** What would convincing evidence be that the hornet is truly gone from Washington? How long?
- **Reply (gist):** Absence of detections despite adequate surveillance, not mere absence of reports: no confirmed positive (no nest, specimen, or DNA/eDNA trace) anywhere in the state across at least three consecutive full seasons — three years as the rule of thumb spanning the multi-year life cycle and overwintering-queen risk. Evidence only counts if surveillance effort is maintained at a level sufficient to have detected the hornet (continued trapping, public reporting, look-alike screening at roughly active-year intensity); zero detections under weak surveillance proves nothing.
- **Used in work:** Becomes the quantitative eradication rule in Task 5: T = 3 active seasons (Apr-Oct each), alpha = 0.05, Poisson absence model P(0 | nest) = exp(-3*lambda_nest) < 0.05 rules out nests with detectability >= -ln(0.05)/3 = 1.03 events/yr; surveillance-adequacy condition (b) = documented >= 50% of 2020 active-year intensity; the "weak surveillance proves nothing" caveat is stated as limitation (4).

## Exchange 9 — When report volume signals real spread
- **Q:** When new reports pile up over time, at what point does it feel like a real spread, not just noise?
- **Reply (gist):** Real spread = confirmed positives appearing in new, spatially distinct locations over time — not raw report volume (dominated by reporting effort and seasonal activity). Threshold: two or more confirmed positive IDs separated by more than the ~30 km queen dispersal range, in different seasons/years, persisting rather than one-off; a single detection or positives clustered within a few km = one incipient colony, not spread.
- **Used in work:** (a) Task 1 spread analysis: the 11 WA positives are mutually within ~30 km (median pairwise < 1 km; bounding box ~32x19 km around Bellingham), so by this criterion the data show ONE corridor, not spread — that is the interpretive conclusion. (b) Task 5: the "two or more confirmations > 30 km apart in different seasons" condition is the persistence/establishment trigger that blocks an eradication claim and restarts the clock.

## Exchange 10 — Field-visit capacity
- **Q:** How many field visits can the agency realistically send out per week to follow up on reports?
- **Reply (gist):** No published figure; a state agency with a small dedicated team (a handful of entomologists/inspectors) can do on the order of a few to roughly 10-20 field visits per week in the active season. Each visit costs ~half a day to a day including travel; the same staff also run trapping, lab screening, outreach. The gap between visits/week and thousands of reports is exactly why triage is necessary.
- **Used in work:** Sets the budget B in Task 3: plan at B = 14 visits/week with B = 7 and B = 28 as bounds (within the few-to-10-20 range); expected yield computed per weekly batch (positives per visit ~ q_14 = 0.36 in the historical replay, CI [0.13, 0.65]). Recorded as an empirical parameter with its source (exchange 10) in the Task 3 analysis.

## Parameter table (empirical inputs, per submission rules)
| name | value | interval | source |
|---|---|---|---|
| queen dispersal range | 30 km | [30, 30] | problem statement (MMBench 2021_C) |
| field visits per week (active season) | 14 (planning), bounds 7 / 28 | [~few, ~20] | exchange 10 |
| post-confirmation response radius | 1-5 km | [1, 5] | exchange 7 |
| post-confirmation response timing | days to ~2 weeks, then through October | — | exchange 7 |
| eradication evidence window | 3 consecutive active seasons | [3, 3] | exchange 8 (rule of thumb) |
| surveillance adequacy threshold | >= 50% of 2020 active-year intensity | — | agent's operationalization of exchange 8 |
| eradication confidence level alpha | 0.05 | — | standard convention |
| real-spread criterion | >=2 confirmations >30 km apart across seasons | — | exchange 9 |
| recency weight half-life for model updates (tau) | 90 days | — | agent choice, motivated by observed awareness-decay timescale (exchanges 1, 6, 9) |

All other numbers in solution.json come from the task's own dataset (4,440 reports + 3,305 attachment metadata rows).

## Note on use of replies
No expert wording was copied into solution.json; each reply is reflected only as a parameter value,
a constraint (triage structure, leakage exclusion, eradication rule), or a decision rule (R1 override,
real-spread trigger), with the exchange number as its provenance.
