# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence (Problem 2003_C — EDS/ETD screening)

Ten exchanges, one question each. Each reply was converted into a named model
parameter or constraint before the next question.

| # | Question (short) | Reply (essence) | How it entered the model |
|---|---|---|---|
| 1 | Are bags unloaded together or in waves? | Spread-out, bursty arrival stream; each flight's bags arrive in a lump tied to its arrival/unload, not one batch nor a smooth rate. | **Structural mechanism.** Peak-hour demand modelled as a superposition of per-flight lumps spread over the hour with short-term surges above the hourly mean. Drives the per-minute demand profile used for sizing and scheduling. |
| 2 | Checked bags per passenger? | 0.5–0.8 bags/passenger; leisure higher, business lower; sanity anchor 70–130 bags per 130–180-seat narrowbody. | `bag_yield = 0.65` (sensitivity 0.5–0.8). Combined with `occupancy = 0.85` (assumption, within the 70–130 anchor) gives bags/flight = 0.65×0.85×seats. |
| 3 | Seconds per bag at the EDS? | ~15–25 s (nominal 20 s); matches 160–210 bags/hr; real cycle longer due to jams/review/alarms; 92% availability cuts effective throughput. | `eds_cycle_s = 20` (17–23); effective capacity per machine = 0.92×3600/20 = 16.6 bags/min. |
| 4 | Share of bags flagged for secondary? | 10–30%, nominal ~20%, mostly false alarms. | `flag_rate = 0.20` (0.10–0.30). Adds secondary-review labor and a throughput penalty. |
| 5 | Seconds to clear a flagged bag? | ~1–3 min, nominal 2 min; ~6× the 20 s primary; highly variable, labor-intensive. | `secondary_clear_s = 120` (60–180). Secondary labor demand = flagged bags × 120 s. |
| 6 | Minutes before takeoff must bags clear? | ~30–45 min, nominal 30 min; the binding deadline is the bag-acceptance cutoff (domestic), compressing the screening window. | `cutoff_min = 30` (30–45). A flight's bags must clear by `departure − 30`. Defines the per-flight screening window and the scheduling constraint. |
| 7 | EDS and ETD inline or separate? | Separate stations in series with a transfer step; ETD is the slower manual step, only a subset (mandated ≤20%) passes through after EDS. | ETD modelled as a separate serial station with a transfer; ETD demand = dual-screened bags only. |
| 8 | Seconds per bag at the ETD? | ~1–2 min (nominal 1 min); consistent with 40–50 bags/hr; ~3–4× slower than EDS primary. | `etd_cycle_s = 75` (60–120); effective capacity per ETD = 0.98×3600/75 ≈ 47 bags/hr. |
| 9 | What share actually needs ETD? | Routine 2–5%; the 20% is a policy ceiling for targeted high-risk flights, not routine. | Base case `dual_share = 0.20` (the mandated ceiling, per Task 6 wording); sensitivity at routine 0.03. ETD count driven by the mandated 20% case. |
| 10 | What is done when screening can't keep up? | Divert bags to overflow/spare lines; hold bags for a later flight; triage by risk/cutoff; add labor; loosen thresholds; delay departure only as a last resort. | **Validity/boundary.** Sizing includes a surge/overflow buffer; the schedule's objective is to minimise late-clear (cutoff-miss) bags, with the overflow + hold-bag response as the fallback rather than departure delay. |

## Parameter table (all empirical inputs)

| name | value | interval [a,b] | source |
|---|---|---|---|
| bag_yield (checked bags/passenger) | 0.65 | [0.5, 0.8] | Expert exchange 2 |
| occupancy (fraction of seats with a checked bag, assumed) | 0.85 | [0.8, 0.95] | Model assumption, within exchange-2 anchor (70–130 bags / 130–180 seats) |
| eds_cycle_s (primary scan+clear per bag) | 20 | [17, 23] | Expert exchange 3 |
| eds_availability | 0.92 | [0.92, 0.92] | Problem statement (92% operational) |
| flag_rate (secondary-inspection share) | 0.20 | [0.10, 0.30] | Expert exchange 4 |
| secondary_clear_s (per flagged bag) | 120 | [60, 180] | Expert exchange 5 |
| cutoff_min (bag-acceptance cutoff before departure) | 30 | [30, 45] | Expert exchange 6 |
| etd_cycle_s (per bag) | 75 | [60, 120] | Expert exchange 8 |
| etd_availability | 0.98 | [0.98, 0.98] | Problem statement (98% operational) |
| etd_accuracy | 0.997 | [0.997, 0.997] | Problem statement |
| eds_accuracy | 0.985 | [0.985, 0.985] | Problem statement |
| dual_share (bags needing EDS+ETD) | 0.20 | [0.03, 0.20] | Expert exchange 9 (ceiling); mandated 20% per problem |
| cancel_rate (flights cancelled/day) | 0.02 | [0.02, 0.02] | Problem statement (dataset note) |
| labor_etd_multiple (ETD labor vs EDS) | 10 | [10, 10] | Problem statement |

## Sizing logic
- Effective EDS capacity/machine/hour = availability × 3600 / cycle = 0.92×3600/20 = 165.6 bags/h.
- Peak-hour bags (Airport A) = Σ seats×flights × bag_yield×occupancy = 5396×0.65×0.85 ≈ 2,977 bags.
- Required machines = ceil(peak_bags / (capacity/machine × hour-utilisation)) with a surge buffer; the bursty arrival profile (exch. 1) raises the instantaneous peak above the hourly mean, so a buffer is added.
