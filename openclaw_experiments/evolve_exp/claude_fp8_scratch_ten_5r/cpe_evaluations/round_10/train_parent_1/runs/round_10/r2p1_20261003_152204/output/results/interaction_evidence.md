# Interaction Evidence

10 expert exchanges, mechanism → constraint → parameter sequencing. Each reply was
converted into a model parameter or structural decision before the next exchange.

| # | Question | Reply (substance) | How it was used |
|---|----------|-------------------|-----------------|
| 1 | Are bags screened one at a time or in batches? | One at a time, continuous stream; per-bag cycle time governs throughput (160-210 b/h); queuing is buffering only. | Structural: EDS is a single-server stream, no batch efficiency; the 160-210 figure is the true per-machine rate. Model uses per-bag service, no batch factor. |
| 2 | With several machines side by side, what limits the count? | Peak-hour bag volume vs effective per-machine throughput (nominal rate x ~92% availability); space/labor/cost limit deployment but not the count. | Constraint: dimensioning is bags / (rate x availability); space/labor/cost treated as secondary feasibility checks, not the sizing rule. |
| 3 | What fraction of a flight's checked bags arrive during the departure peak hour? | No fixed fraction; for peak-hour analysis it is standard to treat it as ~1 (essentially all bags for peak-hour departures presented within the hour), with 2% cancellations as the only reduction. | Parameter: peak-hour bags = MU x seats x 0.98 for flights departing in the hour; no arrival-spread discount. |
| 4 | What fraction of passengers check at least one bag? | ~60-75% (empirical); legacy/higher ~70-80%, low-cost ~40-60%; central ~0.7 for peak planning. | Parameter: checked-passenger fraction = 0.70, interval [0.60, 0.75]. |
| 5 | Typical load factor for domestic flights at busy US airports? | ~80-90%; central ~0.85 for peak planning. | Parameter: load factor = 0.85, interval [0.80, 0.90]. |
| 6 | What queue length / wait is unacceptable at a final screening lane? | Target avg wait < ~10 min; sustained > ~20 min is a service failure; 15-20 people/lane is a practical trigger to add a lane. | Parameter: W_MAX = 10 min, interval [10, 20]; used as the service-level constraint in Tasks 2 and 4. |
| 7 | How many bags does a checking passenger usually have? | ~1.1-1.2 per checking passenger. | Parameter: bags/checking passenger = 1.15, interval [1.1, 1.2]. Combined with #4 and #5 gives MU = 0.70 x 0.85 x 1.15 ≈ 0.80 bags/seat (interval [0.75, 0.85]), the central demand factor in Tasks 1, 3, 5, 6, 7. |
| 8 | How long before departure do passengers finish checking in? | Check-in closes 30-45 min before (domestic); most bags dropped 45-90 min ahead; treat check-in complete by the cutoff. | Parameters: CHECKIN_LEAD = 75 min (complete, interval [45, 90]); DUE_LEAD = 45 min (bag in hold). These set the screening window and the due-time rule in Task 3. |
| 9 | How often do machines break down during a busy day? | Routine; 92% availability ≈ 45-50 min down per machine per 10-h day; failures cluster; losing one machine mid-peak is realistic. | Parameter: OPH = 10 h; supports sizing on availability-adjusted throughput and the Task 4 recommendation of 1-2 spare machines (sensitivity: one down -> 62.1 / 61.5 min screening, breaches the hour). |
| 10 | What happens to a bag with an unclear scan? | Diverted to secondary manual review (image review, hand search, ETD swab if needed); held out of the main stream; does not change per-machine rate for bags that clear. | Structural + parameter: alarmed bags = bags x (1 - 0.985) go to a separate manual channel at ~15 min/bag (SECONDARY_MIN); drives the secondary-staffing recommendation in Tasks 4 and 7 and the accuracy-sensitivity in Task 7. |

## Provenance note
MU = 0.80 bags/seat is the only empirical constant not in the problem statement or
dataset; it is built from exchanges 4 (0.70), 5 (0.85), and 7 (1.15) with interval
[0.75, 0.85], and is swept in model.py (`--sweep MU=0.75,0.80,0.85`). All other
numerical parameters (EDS_RATE 160-210, EDS_AVAIL 0.92, ETA_RATE 40-50, ETA_AVAIL
0.98, EDS accuracy 98.5%, ETD accuracy 99.7%, 20% ETD fraction, 2% cancellation,
device costs) come from the problem statement or the Table 1 dataset note.
