# Expert Interaction Evidence — MM-Bench 2017_D (TSA Checkpoint)

Ten exchanges, one question each. Each reply was converted into a model
parameter, constraint, or structural decision before the next exchange.
Question text lives in `logs/operator_feedback/expert_question_N.md`; the
modeling impact is recorded below. No expert phrasing is copied into the
submission — only the value/constraint it supplied.

## Exchange 1 — queue structure (structural branch)
- **Q:** Can passengers switch to a shorter lane, or must they stick with the
  lane they first join?
- **Reply (gist):** Lanes have their own feeder queues; passengers commit to
  the lane they enter. Switching is rare, only before reaching the divesting
  tables. Treat lane choice as fixed at joining.
- **Impact on work:** Set the model's routing rule to *fixed lane membership
  at arrival* (no cross-lane switching in the baseline). This is the structural
  anchor that every later parameter hangs on. It also makes "shared line" a
  genuine *modification* to test, not the default.

## Exchange 2 — cut-in rate (parameter branch)
- **Q:** Rough share of passengers who try to jump the line on a long day?
- **Reply (gist):** A small minority, well under 5%, rises somewhat when a
  lane stalls; an empirical judgment.
- **Impact on work:** Calibrated `P_CUT = 0.02` (2%) as the base cut-in
  probability in the simulator, with a cultural multiplier on top (part c).
  Interval held: [0.01, 0.05].

## Exchange 3 — ID-check staffing (structural/parameter)
- **Q:** One ID-check officer while the lane waits, or two side by side?
- **Reply (gist):** One ID-check station per lane, single officer. The two
  "ID Check Process Time" columns are two different officers/lanes, not
  parallel service of one queue.
- **Impact on work:** Modeled ID check as a **single server per lane** (M/M/1
  per lane), not a pooled multi-server station. Interpreted the dataset's two
  ID columns as two lanes' data, not parallel servers — this changed how the
  dataset columns were read during cleaning.

## Exchange 4 — X-ray belt behavior (structural)
- **Q:** Do officers clear the bag belt as bags arrive, or let it build?
- **Reply (gist):** The X-ray is a continuous-flow device; bags are fed in one
  at a time as loaded, with only brief pauses for flagged bags. Sustained
  accumulation is not normal.
- **Impact on work:** Modeled X-ray as a **continuously-operating server**
  processing bags as they arrive (per-bag service ~7.5 s from dataset exit
  gaps), rather than a batch/queue-then-clear server. Added a flag-induced
  brief stoppage (exchange 6).

## Exchange 5 — officer breaks (boundary condition)
- **Q:** Do officers take regular breaks or stay the whole shift?
- **Reply (gist):** Periodic relief with a break every couple of hours plus a
  meal; lanes are staffed to cover rotation. Sustained unstaffed gaps are the
  exception (staffing shortage) — itself a source of long-line variance.
- **Impact on work:** Treated stations as **continuously staffed** over the
  30-min simulation window (breaks are ~2-hr-scale, outside the peak window),
  and recorded *staffing shortage* as a named failure mode / limitation in the
  solution rather than modeling it as a periodic server-down cycle.

## Exchange 6 — flagged-bag impact (parameter + boundary)
- **Q:** When a bag is flagged for secondary search, how big a deal is the
  slowdown?
- **Reply (gist):** Real but usually modest; one officer pulled for ~1–2 min,
  lane throughput drops. Flag rate is a few percent. Becomes a big deal when
  flags cluster or staffing is thin.
- **Impact on work:** Calibrated `P_FLAG = 0.05` and `T_FLAG = 60 s`
  (secondary-search duration). Added flag events as a **variance source**:
  they inject a 60-s server delay, and their clustering explains tail
  wait-time variance. Interval for flag rate held: [0.03, 0.08].

## Exchange 7 — rush-hour regime (boundary / operating point)
- **Q:** In morning rush, do lanes run at full speed or get overwhelmed?
- **Reply (gist):** Lanes are saturated (running at max rate) but demand
  exceeds capacity, so lines keep growing through the peak. Bottleneck is
  throughput, not lane availability. Eases when the surge subsides or extra
  lanes open.
- **Impact on work:** Fixed the simulation's **operating point at high
  utilization** (~0.70–0.85 per lane) so the system is in the "saturated but
  growing" regime the expert described, rather than an under-loaded one. This
  is what makes the baseline exhibit the long-line variance the problem asks
  about.

## Exchange 8 — surge capacity (boundary / modification feasibility)
- **Q:** Is there extra screening space that can be opened on short notice?
- **Reply (gist):** Modest and slow — more physical lane positions than are
  staffed, so opening a lane is a staffing decision taking minutes to tens of
  minutes. Realistic fast response is reallocating officers, not opening a new
  lane.
- **Impact on work:** Calibrated `SURGE_LAG = 300 s` (5 min) to open a spare
  lane, and made "surge lane" one of the tested modifications. The 300-s lag
  is why the surge variant under-performs a structural fix — a concrete,
  expert-grounded reason.

## Exchange 9 — dominant bottleneck station (parameter priority)
- **Q:** Which part do passengers most complain is slow — ID check, divesting,
  or body scan?
- **Reply (gist):** The divesting / belt-loading step, not ID check or body
  scan. It is the slowest station, where the queue visibly stalls, most
  affected by unfamiliar travelers.
- **Impact on work:** Confirmed **divest/belt-load as the primary throughput
  bottleneck** (service ~28.6 s from the dataset's "Time to get scanned
  property" column). This justified (a) pacing each lane on the serial
  ID+divest chain, and (b) making divest time the parameter that traveler
  style modulates in part c. Body scan (11.6 s) and X-ray (7.5 s) overlap with
  divest, so they do not extend the cycle.

## Exchange 10 — feasibility of early divesting (modification check)
- **Q:** If passengers could start unloading at the back of the line, would
  most do so?
- **Reply (gist):** No — divesting is coupled to the belt/bins/table only at
  the front. A minority (frequent travelers, Pre-Check) would; the typical
  slow traveler would not. Early unloading would not meaningfully relieve the
  bottleneck.
- **Impact on work:** **Rejected "early divesting at the back of the line" as
  a standalone modification** (insufficient adoption) and did not build it as
  one of the two headline modifications. Instead the two modifications are the
  lane-allocation rebalance and the shared-line routing, both of which the
  model shows improve throughput and cut variance. This exchange pruned the
  modification space before finalizing part b.

---

### Parameter table (empirical inputs, with source)
| name | value | interval [a,b] | source |
|---|---|---|---|
| P_CUT (cut-in share) | 0.02 | [0.01, 0.05] | exchange 2 |
| P_FLAG (bag flag rate) | 0.05 | [0.03, 0.08] | exchange 6 |
| T_FLAG (secondary search) | 60 s | [30, 120] | exchange 6 |
| SURGE_LAG (open spare lane) | 300 s | [120, 600] | exchange 8 |
| T_ID (ID-check service) | 18 s | [15, 25] | exchange 9 ("tens of seconds") |
| T_DIV (divest/belt-load) | 28.6 s | dataset mean, n=29 | task dataset, belt column |
| T_SCAN (mmwave server) | 11.6 s | dataset exit-gap mean, n=40 | task dataset |
| T_XRAY (per-bag X-ray) | 7.5 s | dataset exit-gap mean, n=11 | task dataset |
| T_RETR (belt retrieval) | 8 s | [5, 15] | estimate, post-X-ray belt |
| PRE_DIV_SCALE (pre-check divest) | 0.70 | [0.6, 0.8] | problem statement (skip shoes/belts/jackets) |
| LAMBDA per lane (rush) | 54 pax/hr | utilization 0.70–0.85 | exchange 7 (saturated regime) |
