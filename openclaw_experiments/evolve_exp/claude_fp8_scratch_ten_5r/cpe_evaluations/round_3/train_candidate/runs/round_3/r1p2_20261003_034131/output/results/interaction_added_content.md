# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — Task 2017_D (TSA Security Checkpoint)

Ten exchanges, one question each. Each reply is converted into a named model
parameter (tagged X1..X10 in the model's parameter table) or a change to the
decision logic, with the exchange recorded as its source.

## Exchange 1
- **Q:** Which part of the checkpoint usually has the longest passenger line at morning peak: document check, screening belt, or the collection belt?
- **Reply (gist):** The Zone B screening-belt queue. It has the longest per-passenger service time (divestiture, bin loading) and is the shared resource deliberately under-provisioned relative to demand (one Pre-Check lane per three regular lanes despite ~45% Pre-Check use). Document check is seconds per passenger; the collection belt is a pass-through, not a queue.
- **Used as:** Structural confirmation that the Zone B divestiture/screening stage is the primary bottleneck. The model is built as a queueing chain with Zone B as the binding resource; zone-level load ratios and queue-length comparison in Part a rest on this. No separate numeric parameter.

## Exchange 2
- **Q:** When an open screening lane fills up, what do officers actually do to relieve it?
- **Reply (gist):** Open additional lanes by pulling officers from other posts (document check, secondary, breaks) and redirect passengers to the new lane; with fixed staffing, pull Pre-Check-eligible passengers into the underused Pre-Check lane and otherwise let the queue drain.
- **Used as:** Decision rule for the capacity-expansion control in Part b (dynamic lane opening with cross-posting), and the basis of Modification M1 (open extra lanes during peak) and the Pre-Check re-routing in M3.

## Exchange 3
- **Q:** How many minutes to open an extra screening lane?
- **Reply (gist):** About 10 minutes planning figure, range 5–15 (officer relocation, power-up, X-ray calibration/self-test, divestiture table setup; a few extra minutes for handoff if pulled from another post).
- **Used as:** `lane_opening_time = 10 min, interval [5, 15]` (source: exchange 3). Used in the control simulation: a lane opened at time t only serves passengers arriving after t + 10 min. Sensitivity: the M1 benefit shrinks if opening is slow; at 15 min the queue still grows substantially before relief arrives.

## Exchange 4
- **Q:** How often are bags stopped at X-ray for hand search, out of ten bags?
- **Reply (gist):** About 1–2 per ten (10–20%). Higher in regular lanes during high alert; lower in Pre-Check lanes.
- **Used as:** `bag_flag_rate_regular = 0.15, interval [0.10, 0.20]` (source: exchange 4); `bag_flag_rate_precheck = 0.10, interval [0.05, 0.15]` (Pre-Check lower, same exchange). Drives the Zone D bag secondary load.

## Exchange 5
- **Q:** How long does a secondary hand-search of a stopped bag take?
- **Reply (gist):** About 1–3 minutes per bag, ~2 min planning figure; simple cases under a minute, complex/re-scan cases 5+ minutes.
- **Used as:** `bag_secondary_time = 2 min, interval [1, 3]` (source: exchange 5).

## Exchange 6
- **Q:** How often do passengers fail the walk-through body scan and get a pat-down, out of ten?
- **Reply (gist):** About 1–2 per ten (10–20%); lower in Pre-Check lanes, higher under heightened posture.
- **Used as:** `body_flag_rate_regular = 0.15, interval [0.10, 0.20]` (source: exchange 6); `body_flag_rate_precheck = 0.08, interval [0.05, 0.12]`. Drives the Zone D pat-down load.

## Exchange 7
- **Q:** Do passengers walk straight out after screening, or stop back to fix something?
- **Reply (gist):** Mostly straight out, but a meaningful minority dwell briefly at the collection belt to re-dress/repack, occupying the collection area and blocking the belt exit; a small fraction double back for missed or held items.
- **Used as:** `collection_dwell_rate = 0.25, interval [0.15, 0.35]` — share of passengers who pause at the collection belt; dwell duration 1–2 min, ~1.5 (source: exchange 7, qualitative; value chosen as planning figure within the described behavior). This makes Zone C a small but real server rather than zero time, and is the mechanism behind the recommendation to add a re-pack station beyond the exit.

## Exchange 8
- **Q:** When lines get long, do passengers switch lanes themselves, or are they directed?
- **Reply (gist):** Officers direct them; passengers stay in the line they joined (can't see which lane is shorter, crossing the rope is cutting). The officer at the head of the Zone B queue waves the next passenger to whichever lane is free. Self-switching only at the margin (new lane visibly called, a few assertive cutters).
- **Used as:** Routing rule: single merged Zone B queue with officer-directed dispatch to the shortest free lane (optimal joining) — not passenger self-selection. Cultural sensitivity: the "cutting stigma" (Americans) keeps self-switching near zero; a norm that tolerates self-switching raises variance because slow self-sorting lags lane status.

## Exchange 9
- **Q:** How busy is a typical big-airport checkpoint on a weekday morning vs. its busiest time?
- **Reply (gist):** Weekday morning is at or near its busiest (6–9 a.m. departure bank is the daily peak, 80–100% of normal-day max); holiday mornings run higher; off-peak mid-day/evening is a fraction of peak.
- **Used as:** Peak/off-peak demand factor: `peak_arrival_factor = 1.0, interval [0.8, 1.0]` (weekday morning ≈ peak) and `offpeak_arrival_factor = 0.35, interval [0.2, 0.5]` (fraction of peak) (source: exchange 9, qualitative ranges). Defines the two demand scenarios the model is run in.

## Exchange 10
- **Q:** How far apart do passengers stand in a security checkpoint line?
- **Reply (gist):** About 0.5–1 m in a US queue; closer (~0.5 m) when long and roped, farther (~1 m+) when short. Set by physical density, culturally variable.
- **Used as:** `personal_spacing_us = 0.5–1 m, planning value 0.75 m` (source: exchange 10). Used two ways: (i) queue-capacity/density constraint — how many passengers a given footprint holds before the line overflows or blocks; (ii) cultural sensitivity (Part c): a smaller norm (e.g., 0.5 m, collective-density style) packs more passengers per footprint (higher throughput headroom, more congestion at the divestiture point); a larger norm (e.g., 1.5 m) reduces physical density, easing local blockage but lengthening the visible line (and reducing queue-area capacity).

## Summary of how replies entered the model
- X1 → bottleneck identification structure (Zone B binding).
- X2 → lane-opening / re-routing control logic.
- X3 → `lane_opening_time` = 10 [5,15] min.
- X4 → `bag_flag_rate_regular` = 0.15 [0.10,0.20]; `bag_flag_rate_precheck` = 0.10 [0.05,0.15].
- X5 → `bag_secondary_time` = 2 [1,3] min.
- X6 → `body_flag_rate_regular` = 0.15 [0.10,0.20]; `body_flag_rate_precheck` = 0.08 [0.05,0.12].
- X7 → `collection_dwell_rate` = 0.25 [0.15,0.35], dwell ≈ 1.5 [1,2] min.
- X8 → officer-directed routing decision rule (no self-switching baseline).
- X9 → `peak_arrival_factor` = 1.0 [0.8,1.0]; `offpeak_arrival_factor` = 0.35 [0.2,0.5].
- X10 → `personal_spacing_us` = 0.75 [0.5,1.0] m (density + cultural sensitivity).
