# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence

Policy: 10 exchanges, one question each, each reply must be turned into a parameter, constraint, equation change, or decision rule.

| # | Question (short form) | Reply (gist) | How the reply was used in the work |
|---|---|---|---|
| 1 | Which stage causes the longest waits: ID-check officer, or bin prep/X-ray? | Zone B bin-prep / X-ray conveyor is the true capacity constraint; ID check is a fast, low-variance server (~10-30 s) and only dominates under officer shortage or a burst. | Set the structural bottleneck of the base model: the belt (X-ray) is the binding constraint (utilization 1.0), and the ID-check stage is modeled as a fast M/M/c queue. Drives the throughput cap and the queue-variance analysis; also motivates modification (1) as the primary lever. |
| 2 | How long until belt backup spills visibly to the front of the line? | No fixed time; near-immediate (a few minutes) when the belt is saturated and the physical buffer is short; delayed proportionally to holding-area size. Queue grows at net rate (arrivals - belt service). | Added the physical buffer as a finite capacity (N) to the M/M/c/N queue; justified modeling the belt backup as near-immediate (no delay term) so that wait-time variance is driven by belt utilization. Informed the staffing/buffer-size sensitivity (larger buffer delays spill, at the cost of space). |
| 3 | How much faster is Pre-Check divestiture than regular? | 20-40% less divestiture time (regular ~30-60 s vs Pre-Check ~20-40 s); bigger effect is lower variance (more uniform, shorter tail). | Set per-class service times: regular divestiture mean ~45 s (range 30-60), Pre-Check mean ~30 s (range 20-40), with lower CV for Pre-Check. Feeds the belt-utilization comparison that shows why 1 Pre-Check lane per 3 regular lanes is under-provisioned (Pre-Check demand is higher and faster). |
| 4 | How many bags per hour does one X-ray belt process? | 150-300 bags/hour ideal (one bag per 12-25 s); in practice 100-200 bags/hour because of loading/reclaiming and flagged-bag secondary searches stalling the belt. | Set belt service rate mu_belt = 120 bags/hour (range 100-200), the binding service rate in the queueing model. The flagged-bag stall is captured as a reduction from ideal to effective rate and motivates modification (2) (dedicated secondary-search lane off the belt). |
| 5 | What fraction of bags get flagged for secondary hand search? | 5-15% of bags; higher under strict protocol/high threat, lower for Pre-Check (simpler, less cluttered bags). | Set flag rate p_flag = 10% regular (range 5-15), p_flag = 5% Pre-Check. Feeds the belt-stall term (secondary search off-belt) and the body-scanner secondary (pat-down) sub-model; used in the variance decomposition. |
| 6 | What fraction of travelers get a pat-down after the body scanner? | 1-5% of travelers; higher under strict protocol/high threat, lower for Pre-Check (expedited, alarm less). | Set pat-down rate p_patdown = 3% regular (range 1-5), p_patdown = 1% Pre-Check. Adds a secondary-service stage (off the main body-scan line) in the Zone-D sub-model; contributes to the wait-time variance tail. |
| 7 | Do regular travelers switch to the Pre-Check lane if it looks shorter? | Only occasionally and informally; normally no because access is gated. They switch when the lane is unstaffed/loosely policed, or when TSA opens the Pre-Check lane to all during peak congestion. | Justified modeling the two lanes as separate queues (no cross-joining) in the base case, and created a distinct policy lever: "open the Pre-Check lane to all travelers at peak" (demand-splitting modification). This is a real, observed practice, so it is a legitimate recommendation. |
| 8 | Which is longer for most travelers: the body scanner or bin preparation? | Bin prep dominates (regular 30-60 s, Pre-Check 20-40 s); body scanner is fast and low-variance (a few seconds). Only the pat-down minority adds ~1 min+. | Confirmed the variance decomposition: bin prep is the high-variance, long service stage (drives CV and the wait tail), scanner is low-variance. Sets scanner service time ~10 s (low CV) and pat-down service ~60 s in the Zone-D sub-model. |
| 9 | Do some travelers move through screening noticeably slower, and why? | Yes, wide spread: unfamiliarity (biggest), high item load, physical factors (age, mobility, children), compliance/attention, language/cultural unfamiliarity. Divestiture is heavy-tailed; a minority take 2-3x the median and disproportionately clog the belt. | Basis for the cultural/behavioral sensitivity analysis: defined traveler "styles" (familiar/fast, average, slow/unfamiliar) as a mixture over divestiture time with a heavy tail (a minority at 2-3x median). Modeled as a 3-component mixture so that a slow/unfamiliar-heavy population raises the tail and hence wait-time variance. Informed the recommendation to provide assistance/wayfinding to reduce the unfamiliar-traveler tail. |
| 10 | During busiest flight banks, do airports add more open lanes? | Usually yes, but capped by physical lane count, shift-based staffing (planned in advance, cannot flex instantly), and cost pressure (opened to a target wait-time standard, not zero queue). Arrival rate rises faster than lane capacity, so lines and spill-back occur at peak. | Justified the peak-hour modeling: c rises (more lanes) but lambda rises faster, so utilization rho stays high / exceeds 1 at peak. Constrained c to a max lane count and officer pool. Informed recommendations: pre-staff flight banks (dynamic staffing schedule) and set a target-wait standard rather than chasing zero queue. Confirms the model's peak scenario is valid. |

## Summary of calibrated parameters from expert exchanges

| Parameter | Value | Interval | Source |
|---|---|---|---|
| ID-check service time | ~15-20 s | 10-30 s | Exchange 1 |
| Bin-prep / divestiture (regular) | ~45 s | 30-60 s | Exchange 3, 8 |
| Bin-prep / divestiture (Pre-Check) | ~30 s | 20-40 s | Exchange 3, 8 |
| Belt throughput (bags/hr) | 120 | 100-200 | Exchange 4 |
| Bag flag / secondary rate | 10% (reg), 5% (Pre-Check) | 5-15% | Exchange 5 |
| Pat-down rate | 3% (reg), 1% (Pre-Check) | 1-5% | Exchange 6 |
| Body scanner service time | ~10 s, low CV | few seconds | Exchange 8 |
| Pat-down service time | ~60 s | ~1 min | Exchange 8 |
| Divestiture heavy-tail multiplier | minority at 2-3x median | 2-3x | Exchange 9 |

All values above are expert-judged empirical estimates (the consultation), used as calibrated inputs. Pre-Check share (45%), $85 fee, 5-year validity, and 1:3 Pre-Check-to-regular lane ratio come from the problem statement. Arrival and per-station service times come from the dataset.
