# Expert Interaction Evidence — Problem 2003_C (EDS/ETD baggage screening)

Ten exchanges, one question each, mechanism → constraint → parameter order.
All questions are qualitative, answerable without modelling background.

## Exchange 1 (mechanism)
**Q:** When a large flight's checked bags arrive together at the screening line during the busy hour, how are they handled — one batch through the scanners, or one at a time?
**A (summary):** Bags move one at a time; each bag is loaded, scanned, cleared/flagged, then the next proceeds. Batching only exists upstream (per-flight grouping and reconciliation). Capacity is a serial service rate.
**Used in work:** `code/model.py` models each EDS lane as a single-server queue with serial service rate 160–210 bags/hr (no batch acceleration). The "bags" column is the workload unit; a flight's bags produce queueing delay, not a bulk pass.

## Exchange 2 (primary constraint)
**Q:** What is the single hardest limit operators face when the scanner is the only screening step that must finish before departure?
**A (summary):** The serial service rate of the scanner itself; no staffing or batching can beat it; the plane cannot leave until its last bag is scanned.
**Used in work:** The binding constraint in the model is the aggregate serial scan rate K·(rate·availability); departure deadline is a hard constraint. This fixes the model structure as a capacity/deadline problem, not a staffing problem.

## Exchange 3 (parameter: lead time)
**Q:** How many minutes before scheduled departure must a flight's bags start scanning on a normal day?
**A (summary):** No fixed number; rule of thumb ~1 minute per 3 bags plus buffer for queueing and 8% downtime; narrow-body ~30–50 min, wide-body ~1.5–2 h; assumes scanner dedicated to the flight.
**Used in work:** Calibrates the screening window W (bag cutoff → departure). The 1-min/3-bags rule at the low-rate end equals exactly 1/(160/60) min/bag = the model's per-bag scan time at 160 bags/hr, so the window must exceed own-scan time; base window set to 45 min, swept over 30/45/60/90 min (`logs/model_sweep_window.log`).

## Exchange 4 (parameter: checked-bag share)
**Q:** What share of passengers on a full flight usually checks at least one bag?
**A (summary):** ~60–70% typically, common planning figure ~2/3; leisure long-haul higher (70–80%), business short-haul lower (40–50%); ~1 bag per passenger as upper bound.
**Used in work:** Workload conversion factor c (bags per seat) calibrated to 0.65, interval [0.4, 1.0]; swept in `logs/model_sweep_bagrate.log`. All EDS-count results are reported over this interval.

## Exchange 5 (mechanism refinement: queue discipline)
**Q:** When several flights' bags queue for the same scanners, which flight's bags get scanned first?
**A (summary):** Earliest-departure-first (deadline-driven), with flight-level segregation (a flight's stream processed to completion before switching) and risk/secondary-screening overrides.
**Used in work:** The Task-3 scheduler in `code/model.py::schedule()` implements EDF (departures ordered by time; release times ordered consistently), with per-flight contiguous blocks. Priority flagging feeds the Task-6 ETD dual-screening rule.

## Exchange 6 (parameter: delivery buffer)
**Q:** How many minutes early do airlines normally deliver a flight's bags to the screening line?
**A (summary):** ~45–60 min standard planning buffer; wide-body/long-haul 90–120 min; short-haul narrow-body as little as 30–40 min. Slack absorbs queueing, ~8% EDS downtime, and re-screening.
**Used in work:** Sets the base scheduling window W = 45 min (lower end of stated norm, since the peak hour has no international long-haul bank), consistent with Exchange 3's buffer guidance; the 30/45/60/90 sweep covers the stated range.

## Exchange 7 (constraint: operating hours/staffing)
**Q:** Does the screening line run around the clock, or only certain hours?
**A (summary):** Not 24/7; windows matched to departure banks, idle overnight; hubs keep a reduced subset of lanes for red-eyes; staffing (not machine availability) is the binding constraint on hours; peak-hour demand is what sizes the line.
**Used in work:** Machines are sized for peak demand, then run a reduced bank off-peak (16 operating hours assumed per day in cost/utilization figures); the ETD labor-cost multiplier (×10 EDS labor) means ETD lines are only opened during screening windows, not around the clock.

## Exchange 8 (parameter: re-screening frequency)
**Q:** When scanners clear a bag but officers suspect something, how common is manual re-check, and what triggers it?
**A (summary):** Uncommon but routine, a few percent of bags. Triggers: operator-flagged anomalies, EDS alarms requiring resolution, random/risk-based selection, ETD confirmation under dual screening.
**Used in work:** A secondary-resolution workload of a few percent of bags is routed to the ETD station and a manual inspection position; this is folded into the ETD lane count for the 20% dual-screening policy (Task 6) and into the limitation discussion (model sizes lanes on the 20% policy load, which dominates the alarm-resolution load).

## Exchange 9 (mechanism refinement: parallel resolution)
**Q:** Can a flagged bag be manually re-checked on the spot without stopping the line?
**A (summary):** Yes — pulled off to a separate inspection/ETD position and resolved in parallel; the belt keeps running. Line slows only if the resolution area is unstaffed/occupied or an un-clearable alarm triggers a flight-level hold.
**Used in work:** The model keeps ETS lanes and ETD stations as separate parallel servers (no blocking term), matching the parallel-resolution practice; the flight-level hold case is recorded as a limitation/bias (worst case not modeled).

## Exchange 10 (constraint: parallel lanes)
**Q:** During the busiest departure hour, is one screening line enough, or do big airports spread bags over several parallel lanes?
**A (summary):** Several parallel lanes at large airports; one lane cannot absorb the peak wave; lanes are pooled (any bag to any open lane) with EDF applied across the bank; active lanes scale with the peak, off-peak runs fewer.
**Used in work:** The core sizing rule K = bags/(rate·availability·window) is the pooled multi-lane capacity rule from this exchange; results are reported as a bank of K parallel EDS lanes (and a smaller ETD bank for Task 6), with a note that off-peak operation uses a reduced bank.

## Reply-handling rule compliance
Each reply became (a) a named parameter or constraint with value/interval and this exchange as source, or (b) a structural change to `code/model.py` (serial service, deadline constraint, EDF scheduler, parallel-lane sizing, separate ETD bank) that was then executed (`logs/model_base.log`, `logs/model_sweep_bagrate.log`, `logs/model_sweep_window.log`). No reply text was copied into `solution.json`; values travel as calibrated inputs with this evidence file as provenance record.
