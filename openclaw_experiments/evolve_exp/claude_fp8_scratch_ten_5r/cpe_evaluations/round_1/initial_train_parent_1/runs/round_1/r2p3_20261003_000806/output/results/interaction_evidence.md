# Interaction evidence — 2021_C (Vespa mandarinia triage)

Ten expert exchanges, one question each. Each reply was turned into a parameter,
constraint, or decision rule in the model before the next exchange. The value that
travels into the submission is the number/constraint, restated in my own words —
not the expert's phrasing.

## Exchange 1
**Q:** When your state agency sends field teams to check a public hornet report, what kind of report gets checked first?
**A (gist):** Clear photo/specimen first (esp. beekeeper or hive attack); then proximity to a known positive (≤30 km); then active season; then detailed specific notes. Deprioritize text-only, distant, off-season, or vague reports.
**Effect on work:** Defined the triage hierarchy used in the priority score. I built an expected-value ranking with factors: image presence, proximity to a confirmed positive (30 km window), season, and note-specificity. This is the structure of sub-task 3.

## Exchange 2
**Q:** What do mistaken big-hornet reports most often turn out to be, in your experience?
**A (gist):** Mostly European hornet (*Vespa crabro*), yellowjackets, bald-faced hornets, paper wasps, cicada killers, carpenter bees. A genuine *V. mandarinia* is a small minority of all submissions.
**Effect on work:** Justifies the heavy class imbalance the classifier must handle (14 positives / 2,069 negatives) and motivates a high-precision, recall-weighted ranking rather than accuracy. Informs the baseline misclassification rate ≈ (negative + unverified) / total used in the sub-task 2 framing.

## Exchange 3
**Q:** If a public report has no photo at all, what makes you take it seriously?
**A (gist):** A specific checkable cue: nest description (ground/cavity), honeybee hive attack (mass kill/decapitation), concrete size & appearance, location near a detection in-season, or a credible submitter. Discount vague size-only, winter, distant, or no-detail reports.
**Effect on work:** Added keyword features `kw_nest`, `kw_hive_attack`, `kw_bees` (hive-attack phrases), and `kw_size` to the logistic model so that text-only but specific reports can outrank vague photo reports. This is a direct change to the feature set, then re-run.

## Exchange 4
**Q:** With limited field teams, when would you leave a report uninvestigated even if it looks plausible?
**A (gist):** When expected value of checking is low relative to cost: outside the actionable window (past season / >30 km from any detection), the plausible cue is unverifiable and non-diagnostic, it duplicates an already-checked site, higher-priority reports saturate the teams, or the report is stale. Investigate only when a positive would change action.
**Effect on work:** Added the deferral constraints to the prioritization rule: an *actionability* filter (distance ≤ 60 km, active season), a *staleness* decay by days since detection, and a *cutoff* by field-capacity K. This shapes sub-task 3 into an allocation problem with constraints, not just a ranking.

## Exchange 5
**Q:** How often would you want the triage list re-ranked as new reports arrive?
**A (gist):** Re-rank continuously but on a fixed cadence tied to deployment: daily in-season, weekly or less off-season, plus event-driven re-rank for high-priority triggers (confirmed positive, credible nest, hive attack).
**Effect on work:** Set the model-update cadence for sub-task 4: continuous scoring on each new report, full re-fit / re-ranking daily during the active season (Mar–Nov), weekly off-season, and an out-of-cycle re-rank when a high-priority trigger arrives. I express this as an update rule with two frequencies plus an event trigger.

## Exchange 6
**Q:** After a season with no confirmed finds, what would make you say the hornet is gone?
**A (gist):** Not one quiet season. Need: zero confirmed positives across a full active season under sustained (or higher) reporting volume, no credible nest/hive-attack reports, no detections near prior sites or within 30 km, and consistent negative lab results on the high-likelihood subset. Want 2–3 consecutive such seasons. A drop in reporting alone proves nothing.
**Effect on work:** Defined the eradication decision rule for sub-task 5: a multi-season (2–3) condition on (i) zero positives, (ii) no credible nest/hive-attack reports, (iii) no in-range detections, (iv) negative results on the high-priority subset, with surveillance effort held constant. I quantify the power of this rule under a detection-sensitivity assumption.

## Exchange 7
**Q:** How many field visits could a state realistically spare for hornet follow-ups in a season?
**A (gist):** Tens to low hundreds — roughly 50–200 site visits per season. Reports vastly exceed capacity; only a small percentage can be visited.
**Effect on work:** Calibrated the resource constraint K for the allocation problem (sub-task 3) to K ∈ [50, 200], with a base case of K = 100 visits/season. I report expected positives found as a function of K over that range.

## Exchange 8
**Q:** Do giant hornet queens usually survive the winter in Washington soil, and how often?
**A (gist):** Overwintering in soil is the normal part of the life cycle (mated queens are the only stage that survives winter), but winter mortality is high. Only a minority of overwintering queens survive — order of magnitude a few percent to a few tens of percent, varying with soil and winter severity. Washington's cool wet winters are not ideal.
**Effect on work:** Set the per-season queen-overwinter survival parameter for the spread model (sub-task 1) to s_overwinter ∈ [0.05, 0.30], base case 0.15. This bounds how fast a population can grow and is the key reason establishment is difficult.

## Exchange 9
**Q:** How big can a single giant hornet colony grow before winter kills most of it?
**A (gist):** A mature colony peaks in late summer/early fall at a few hundred workers — commonly ~200–400, occasionally up to ~500–700 in a strong colony. Then it collapses and only mated queens overwinter. Small by social-insect standards, which matters for detection.
**Effect on work:** Set peak per-colony worker population N_peak ∈ [200, 400], base 300, in the spread model. Because a colony is small, a low-density population is hard to find — this feeds the detection-sensitivity assumption used in the eradication power calculation.

## Exchange 10
**Q:** How hard is it to spot a single active giant hornet nest during a normal field visit?
**A (gist):** Very hard. The nest is hidden (underground / cavity), the colony is small so forager traffic is low, activity is intermittent and seasonal, and a single visit is a snapshot. A normal visit confirms a sighting far more reliably than it finds a nest; finding the nest takes repeated, dedicated effort.
**Effect on work:** Set the single-visit nest-detection probability (sensitivity) low — I use s = 0.5 as the base case with a range [0.5, 0.9] for the eradication power calculation, and note that a single visit is a sighting-confirmation, not a nest-find. This drives the recommendation that eradication needs multiple seasons and sustained effort, not one clean visit.

## Parameters that came from the supplied dataset / problem statement (not from the expert)
- 30 km queen dispersal range — stated in the problem statement.
- 14 positive / 2,069 negative / 2,342 unverified / 15 unprocessed labels — from the dataset.
- Report counts, coordinates, dates, notes, and image attachments — from the dataset.
- Loper, Norderud & Peterson (2021), *PeerJ* 9:e10690 — geographic potential / invasion simulation for *V. mandarinia* in North America; source for the invasion-dynamics structure and county risk. Retrieved via the staged helper.

## How each reply was used (checklist)
1. Triage hierarchy → priority-score factors (sub-task 3).
2. Lookalike composition → class-imbalance framing, high-precision ranking (sub-task 2).
3. Text-only credible cues → keyword features added to the logistic model (sub-task 2/3).
4. Deferral / expected-value rule → actionability, staleness, and K-cutoff constraints (sub-task 3).
5. Re-rank cadence → update rule, daily in-season / weekly off-season + event trigger (sub-task 4).
6. Multi-season eradication condition → eradication decision rule + power calc (sub-task 5).
7. Field capacity 50–200 → resource constraint K (sub-task 3).
8. Overwinter survival 5–30% → spread-model per-season survival parameter (sub-task 1).
9. Colony peak 200–400 workers → spread-model colony size + detection difficulty (sub-task 1/5).
10. Hard-to-find single nest → low single-visit sensitivity, multi-season requirement (sub-task 5).
