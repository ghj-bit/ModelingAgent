# Interaction evidence — 2017_D (MM-Bench)

Ten expert exchanges, one question each. Question files: `logs/operator_feedback/expert_question_N.md`;
controller-recorded request/reply files: `expert_request_N.json` / `expert_reply_N.json`.
Each reply was turned into a model parameter before the next exchange. Values below are the
model parameters as used (my formulation, not the expert's text).

| N | Question (short) | Value used in model | Where used |
|---|---|---|---|
| 1 | Passengers/hour per open lane? | `mu = 180 pax/h per lane` (interval [100, 200]; real lanes run 100–150 when interrupted) | Base service rate of one lane in the discrete-event simulation and the M/M/c load check |
| 2 | Pre-Check speed advantage? | `t_pre = 0.70 * t_reg` (interval [0.60, 0.80]; saving is divestiture/reclaim only, bounded) | Per-passenger service-time split in the simulation |
| 3 | Secondary-screening rate? | `p_sec = 0.15` regular (interval [0.10, 0.20]); `p_sec_pre = 0.03` (order of a few %) | Bernoulli event in simulation; variance driver |
| 4 | Time added by secondary? | `t_sec = 3 min` (interval [2, 5]); bag+pat-down sequential 5–8 | Added service time for the event |
| 5 | Peak-to-trough volume swing? | Daily curve with double peaks 6–9 a.m. and 3–7 p.m., busiest hour 3–5× the quiet hour (full-day up to 5–8×) | Arrival-rate function λ(t) in the simulation day |
| 6 | Lane-opening delay? | `t_open = 10 min` central (interval [5, 15]); only 1–3 min if staffed-and-gated | Opening lag in the dynamic-lane policy |
| 7 | Pre-Check line speed at peak? | Allocation norm 1 Pre-Check lane : 3 regular while 45% of demand is Pre-Check; wait inversion at peak | Lane-allocation scenario in simulation (base case) |
| 8 | Cross-cultural line behavior? | Culture affects spacing, lane-switching, gap-filling (arrival variance per lane), not per-passenger service time; first-time international travelers slower | Sensitivity scenarios (spacing σ, lane-switching fraction, group share) |
| 9 | Group screening behavior? | Groups of ≥3 screen as one unit occupying lane space ~2–3× longer than a solo traveler | Group-blocking service-time multiplier in simulation |
| 10 | Staff's main lever for long queues? | Opening extra lanes (linear in lanes, slow to act, capped by staff/equipment); fallback triage/expedite | Dynamic-lane policy M2; staffing ceiling in scenario M1 |

## Consequences of replies on the work

- Exchanges 1–2 fix the lane capacity (180 pax/h) and the Pre-Check/regular service split;
  the whole simulation is calibrated to these before any scenario is run.
- Exchanges 3–4 define the secondary-screening random shock (15% × ~3 min) that the model
  identifies as the main variance source; the variance-reduction recommendation follows from it.
- Exchange 5 shapes λ(t); the base-day simulation shows peak waits concentrate 6–9 a.m. and
  3–7 p.m., matching the double-peak shape.
- Exchange 6 (10 min opening lag) is why a pre-staged (staffed-and-gated) extra lane beats a
  cold-open one; this becomes modification M2's design constraint.
- Exchange 7 justifies re-balancing lane allocation to demand (1:3 norm vs 45% Pre-Check share)
  as modification M1; the simulation confirms Pre-Check waits invert at peak under the base allocation.
- Exchange 8 sets up the cultural sensitivity analysis as changes to queueing behavior
  (lane-switching, spacing) and arrival variance, deliberately not to per-passenger service time.
- Exchange 9 adds the group-blocking effect: ~15% of arrivals as groups of 3–4 occupying the
  divestiture area 2–3× longer, modeled as a service-time multiplier.
- Exchange 10 motivates the dynamic staffing policy in M2 and caps the "open unlimited lanes"
  scenario at the realistic staffing ceiling.
