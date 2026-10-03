# Interaction Evidence — MM-Bench 2003_C

Ten expert exchanges, one question each, each building on the previous reply.
For each: the question, the reply (summarized in my own words — the raw reply
lives in `logs/operator_feedback/expert_reply_N.json`), and how the reply became
work (a parameter, constraint, equation, or decision rule, with the value and
interval it supports and where the model uses it).

---

## Exchange 1 — dominant mechanism: bags per passenger
**Q:** On a typical commercial flight, about how many checked bags does each
passenger have?
**Reply:** U.S. domestic ~0.5–0.8 checked bags per passenger; planning figure
~0.6. Empirical judgment.
**Became work:** Sets the core conversion from seats (the only passenger count
in Table 1) to bag volume. Parameter `bags_per_seat = 0.6`, interval [0.5, 0.8].
Used in `peak_bags()` for every airport and task; swept in `sweep_bps.log`.

## Exchange 2 — constraint on the screening window
**Q:** How long before a flight's scheduled departure do checked bags typically
need to arrive at the airport?
**Reply:** Accepted up to ~45 min before departure (30–45 min cutoff, 60 at
large hubs); plan on bags arriving 45–60 min pre-departure, hard cutoff 30–45.
**Became work:** Defines the hard deadline each flight's bag batch must be
screened by. Parameters `cutoff_min = 45` (interval [30,45]) and
`arrival_min = 55` (interval [45,60]). `cutoff_min` is the screening window in
`schedule()` (a flight's bags must clear in `per_min × cutoff_min`); the
departure-stagger in Task 3 keeps every flight inside it.

## Exchange 3 — parameter within the constraint: peak queue wait
**Q:** When an EDS line is busy at peak, how long do bags usually wait in line
before being scanned?
**Reply:** 2–5 min normally, up to 5–10; 10–20+ only when a machine is down or
demand spikes. One EDS clears a bag every ~17–22 s.
**Became work:** Parameter `queue_max_min = 10` (interval [5,10]) is the
service-level bound; it cross-checks the line sizing (the queue must not exceed
this under normal peak). The 17–22 s/bag figure independently confirms the
160–210 bags/h rate range used in `EDS_RATE`.

## Exchange 4 — parameter for the ETD task: high-risk share
**Q:** For the enhanced double-screening rule, about what fraction of all
checked bags belong to high-risk passengers?
**Reply:** ~20% — the rule applies to all bags of the 20% of high-risk
passengers, so the bag fraction ≈ the passenger fraction (an upper bound).
**Became work:** Parameter `HIGH_RISK = 0.20` (interval [0, 0.2], upper bound).
Used in `etd_units()` (the double-screened bag stream) and in the combined
detection-residual equation in Task 6/7.

## Exchange 5 — parameter for cost: EDS labor
**Q:** Roughly what annual cost does it take for labor to operate one EDS
machine at a busy airport?
**Reply:** ~$100,000–$200,000/yr (2–4 screeners at $40–60k/position, 16–20
h/day). Empirical judgment.
**Became work:** Parameter `etsd_labor = 150_000` (interval [100k, 200k]). ETD
labor is 10× this (problem statement). Both feed the opex line in Task 6
(`opex = n_eds × etsd_labor + n_etd × 10 × etsd_labor`).

## Exchange 6 — edge case: one EDS down at peak
**Q:** If one EDS breaks down during the peak hour, what usually happens to bag
screening that hour?
**Reply:** Load redirects to remaining lines at/near max; waits jump to 10–20+
min; if capacity is insufficient some bags miss the 30–45 min cutoff. Airports
keep a spare/redundant unit.
**Became work:** Adds the redundancy term `spare = 1` to the EDS sizing rule
(`eds_units = ceil(bags/eff) + spare`). Without it, a single failure at 92%
availability pushes the line over capacity and bags miss cutoffs — this is the
domain-of-validity bound on the base sizing.

## Exchange 7 — ETD placement (determines whether its reliability compounds)
**Q:** When a bag needs both EDS and ETD screening, do the two scans usually
happen one after the other on the same bag?
**Reply:** Sequentially — EDS first (primary, higher throughput), then ETD for
the flagged/high-risk bag. ETD is the slower secondary step.
**Became work:** Fixes the system topology: ETD does **not** parallel the EDS,
so it only carries the high-risk stream (20% of bags) and its throughput does
not reduce the EDS count. This is why ETD sizing is
`ceil(bags × 0.20 / eff_etd)` and why "ETDs should not replace EDSs" in Task 6
— they screen different populations sequentially.

## Exchange 8 — scale-up structure for Task 5
**Q:** Across all 193 Midwest airports, do most handle far fewer peak-hour
flights than the two large ones we studied?
**Reply:** Yes — A and B are the top of the distribution; the distribution is
heavily skewed, most airports are small/non-hub with a handful or no
peak-hour flights.
**Became work:** The Task 5 memo's adaptation rule: the same per-airport model
is applied to each airport's own Table-1-style peak mix; because the
distribution is skewed, EDS needs concentrate at the few large hubs, and most
airports need 0–2 units (many can share a regional mobile unit). This shapes
the recommendation to fund hubs first.

## Exchange 9 — edge case that bounds ETD's added value
**Q:** In real operations, about how often does an explosive slip past an EDS
scan and get missed?
**Reply:** Very low but non-zero; the stated 98.5% implies ~1.5% in test
conditions, field performance commonly ~1–5% (detection ~95–99%) depending on
threat, clutter, machine condition.
**Became work:** Parameters `miss_lo = 0.01`, `miss_hi = 0.05` (field EDS miss
interval). These drive the combined-detection residual in Task 6/7:
`residual = miss × (1 − 0.20 + 0.20 × (1 − 0.997))`, a constant ~19.9%
reduction, and the value argument that ETD adds a 2nd, independent detection
layer only on the 20% high-risk stream.

## Exchange 10 — failure mode that breaks the schedule
**Q:** At a busy airport during the peak hour, what single thing most often
causes checked bags to miss their flight?
**Reply:** The bag arriving at the screening line too late relative to the
departure cutoff — checked/dropped after the 30–45 min cutoff, or reaching the
EDS queue with too little time left. Breakdowns and queues contribute but are
secondary.
**Became work:** Confirms the Task 3/4 model's binding constraint is the
cutoff-time window, not raw throughput — so the schedule staggers departures
(large aircraft first, earliest slots) to give the largest bag batches the most
screening lead-time, and the Task 4 recommendation is to protect cutoff
compliance (check-in cutoffs, early screening slots for large aircraft) rather
than add machines.

---

### Parameter table (single source of truth, also in solution.json)
| name | value | interval [a,b] | source |
|---|---|---|---|
| bags_per_seat | 0.6 | [0.5, 0.8] | exchange 1 |
| cutoff_min | 45 | [30, 45] | exchange 2 |
| arrival_min | 55 | [45, 60] | exchange 2 |
| queue_max_min | 10 | [5, 10] | exchange 3 |
| HIGH_RISK | 0.20 | [0, 0.20] | exchange 4 |
| etsd_labor | 150,000 | [100,000, 200,000] | exchange 5 |
| spare | 1 | [0, 2] | exchange 6 |
| ETD-after-EDS | sequential | — (topology) | exchange 7 |
| field EDS miss | 0.01 / 0.05 | [0.01, 0.05] | exchange 9 |
| Midwest size skew | A,B top; most small | — (structure) | exchange 8 |
| dominant failure | late bag vs cutoff | — (constraint) | exchange 10 |

Fixed (problem-statement) values: EDS rate 160–210/h (mid 185), availability
0.92, accuracy 0.985, price $1M, install ~$5k; ETD rate 40–50/h (mid 45),
availability 0.98, accuracy 0.997, price $45k, labor 10× EDS; cancellation 2%/day.
