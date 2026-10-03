# Interaction Evidence — 2017_D (MM-Bench)

Ten expert exchanges, mechanism → constraint → parameter sequencing.
Each reply was turned into a calibrated parameter or a change to the model
(`code/analyze_2017d.py`, PARAMS table and scenario structure) before the next
question was asked. Full question/reply text is in
`logs/operator_feedback/expert_question_N.md` and `expert_reply_N.json`;
transcripts in `logs/expert_exchange_N.log`.

| # | Question (short) | Reply (value/constraint) | How it became work |
|---|------------------|--------------------------|--------------------|
| 1 | When a bag is flagged, does the owner wait or walk away? | Owner stands by and waits; the flagged passenger occupies the belt/exit area for the whole secondary search — a local bottleneck distinct from the pat-down lane. | Established the dominant mechanism: a flagged bag **blocks the lane's reclaim point** while the search runs. This is why the model puts the secondary-search time into the lane's effective service and makes the belt a shared, blocking resource. |
| 2 | What stops opening more lanes — money, buildings, or staff? | Trained TSO staff is the binding constraint (recruitment/background-check/training lag, attrition); money secondary, space least binding. | Set the constraint that limits the "add a lane" lever: any modification that adds capacity must be staff-limited, not space- or budget-limited. This shapes which modifications are realistic (reallocate existing TSO sets, add one lane, rather than build new checkpoints). |
| 3 | How long does a manual bag search take? | ~2 min average (1–3 min routine), 5+ min tail. | `manual_search_s = 120 s, interval [60, 300]` — the Zone D bag-search service time, right-skewed. |
| 4 | How often does the belt fill and force a pause at peak? | Recurring, bursty stall at peak — on the order of once every few minutes; negligible off-peak. | `belt_stall_peak_s = 180 s, interval [90, 300]` — the belt-stall frequency at peak. Feeds the belt-capacity term in lane service and the instability finding (the current single Pre-Check lane goes unstable when stalls are included). |
| 5 | How often does a passenger fail the body scan / detector (pat-down)? | ~2% overall (few % for mmWave, <1% for WMD); Pre-Check lower. | `patdown_rate_reg = 0.02, interval [0.01, 0.03]`; Pre-Check uses 0.3×. Drives the pat-down (Zone D) secondary queue load. |
| 6 | How long does a pat-down take? | ~3–4 min average (2–5 min routine), 5–10+ min tail. | `patdown_s = 210 s, interval [120, 300]` — pat-down service time. |
| 7 | Busiest morning banks: lines longest near 7 or near 10? | Longest near 7; 6:30–7:30 a.m. is the peak, by 10 a.m. the lull sets in. | Set the model's operating point to the **6:30–7:30 a.m. peak bank** (≈2–3× the dataset daily-mean arrival rate), which is where the variance and "unexplained long lines" concentrate. |
| 8 | Do regular-lane travelers stand in Pre-Check lines to skip? | No — Pre-Check is gated by eligibility (boarding pass / KTN); leakage negligible. | Treated the two lane types as **segregated queues** with no cross-flow; each modeled independently (no queue-merging term). |
| 9 | In a slow-traveler culture, are lines tighter or more relaxed/jostly? | Relaxed spacing but jostly and less orderly — lower throughput per person, uneven crowding, less disciplined flow. | Cultural sensitivity axis: model the "relaxed / individual-efficiency" traveler style as **slower service (75 s divest) with higher variability (cv 1.8)** and the "collective-efficiency" style as faster and more orderly (35 s, cv 0.6). |
| 10 | How long to unpack shoes/belt/jacket/laptop into bins? | ~45–60 s average for a prepared regular-lane traveler, 1–2 min unprepared; Pre-Check 15–30 s (no shoes/belt/jacket, laptop stays in bag). | `divest_reg_s = 45 s, interval [30, 120]` and `divest_pre_s = 25 s, interval [15, 30]` — the divestiture service time, the largest and most variable component of lane service. |

## Provenance note
- Exchange-sourced parameters (1, 3–10): values and intervals above, each tied to its exchange number.
- Problem-statement-sourced: `precheck_share = 0.45` (45% enroll in Pre-Check).
- Dataset-sourced: `belt_retrieve_s = 28.6 s` (mean of "Time to get scanned property"), `id_service_s = 10 s` (mean of ID Check Process Time 1/2), and the arrival rates (pre 6.5/h, reg 4.6/h daily mean) from the cleaned CSV. `mmw_service_s = 30 s` and `xray_bag_s = 15 s` are planning figures consistent with the dataset belt dwell; the X-Ray/ID event columns are censored (present only while that officer was working), so their raw inter-event gaps are arrival-rate artifacts, not service times.
- `flag_rate_reg = 0.08, interval [0.05, 0.15]` is a planning figure (exchange 1 establishes that flagging is routine and blocking; the exact rate is not in the dataset).

## What the model did with the replies
The structure (a flagged bag blocks the reclaim point, two segregated lane
types, a staff-limited lane count, a peak-bank operating point, and a
cultural service-time/variability axis) comes directly from exchanges 1, 2, 8,
9 and 7. The quantitative parameters come from exchanges 3, 4, 5, 6 and 10 plus
the dataset. The key result — that the single Pre-Check lane is the
throughput/variance bottleneck and that it goes **unstable (rho > 1)** once
belt stalls are included in lane service — is the quantitative expression of
exchanges 1 and 4.
