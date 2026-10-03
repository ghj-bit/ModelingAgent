# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — 2017 ICM Problem D (MM-Bench 2017_D)

Ten exchanges, one question each, strictly sequential: each question builds on
the previous reply. Questions are in `logs/operator_feedback/expert_question_N.md`;
replies in `expert_reply_N.json`. This file records the question, the essence
of the reply (paraphrased, not verbatim), and concretely how the reply changed
the work (parameter value, equation, decision rule, or test).

## Exchange 1 — structural: how the ID check actually works
- **Question:** Does a lane share one ID-check officer, and how long does the
  check take per passenger?
- **Reply (essence):** One shared officer per queue (sometimes one per queue
  side); 5–15 s per passenger; effective throughput 4–8 pax/min/officer; the
  officer also directs passengers and document fumbling adds time.
- **Work impact:** Zone A modeled as a shared M/M/c station (c=2 baseline),
  not per-lane. Service time `S_ID = 0.125 min` (mean of 5–15 s), uniform
  ±25% jitter in `sim.py`.

## Exchange 2 — parameter: the belt stretch and where it is slow
- **Question:** How long is the whole bin-to-reclaim stretch, and is the
  X-ray belt the slow part?
- **Reply (essence):** 1–3 min per passenger; divestiture and re-dress/reclaim
  dominate, belt transit is seconds; the belt becomes binding mainly when bins
  run short, the belt stops for re-runs/flagged searches, or lane count limits
  throughput.
- **Work impact:** `S_BELT = 2.0 min` (central of 1–3) as the lane pacing
  resource; the data column "Time to get scanned property" (mean 28.6 s) is
  reinterpreted as belt transit only, not the whole stretch. Congestion term
  added: each passenger queued ahead of you on the belt adds `BELT_STOP = 0.25
  min` to your belt cycle (belt stalls/re-runs).

## Exchange 3 — parameter/mechanism: what a flagged bag does
- **Question:** When a bag is flagged, what happens and how much does the line
  stall?
- **Reply (essence):** Belt stops or bag diverted to Zone D; officer opens bag,
  often an ETD swab (30–60 s); routine 1–5 min, full unpack/pat-down 5–10 min;
  the whole lane stalls; a single flag adds minutes to everyone queued behind.
- **Work impact:** Flagged bags route to a Zone D server with
  `S_D = 3.0 min` (central of 1–5 + swab); belt-stop penalty of Exchange 2
  captures the propagation to passengers behind. This is the dominant
  variance mechanism in the model.

## Exchange 4 — parameter: how often flags and pat-downs happen
- **Question:** How common are X-ray flags and body-scanner fails?
- **Reply (essence):** Both low-probability, high-impact: roughly 1–5% of bags
  flagged (mostly false alarms; PreCheck less), 1–5% of passengers pat-down
  (PreCheck far less).
- **Work impact:** `P_FLAG = 0.03`, `P_PAT = 0.03` (mid-range); PreCheck
  factors `PRE_FLAG_F = 0.5`, `PRE_PAT_F = 0.3`. These rare events drive the
  tail (p90/p99) of the wait distribution.

## Exchange 5 — parameter: peak load and saturation point
- **Question:** At a busy morning peak, how many passengers per minute enter a
  4-lane checkpoint, and when do lines start crawling?
- **Reply (essence):** 10–20 pax/min at peak; lanes sustain ~3–5 pax/min each,
  so a 4-lane checkpoint saturates around 12–20 pax/min; queues past ~15–30
  per lane make waits climb nonlinearly.
- **Work impact:** Simulation arrival rate `LAM_PEAK = 12 pax/min` (conservative
  mid-peak); load sensitivity runs at 3/12/15 pax/min. The model's baseline
  sits at/above saturation, consistent with the problem's long-line premise;
  the ~15–30/lane threshold is reflected in the nonlinear belt-stop term.

## Exchange 6 — parameter: how much faster PreCheck really is
- **Question:** Compared to a regular passenger, how much faster is PreCheck
  through the belt area, and why?
- **Reply (essence):** 20–40% less time (≈30–60 s saved) because of fewer
  divestiture/reclaim steps (no shoes/belts/jackets, laptop stays in bag);
  metal/electronics/liquids still removed, so the gain is partial; PreCheck
  bags also flag less, lowering variance.
- **Work impact:** `PRE_BELT_F` updated 0.7 → 0.80 (mid of 20–40% faster);
  the reduced flag/pat-down factors of Exchange 4 stay as the variance channel.

## Exchange 7 — structural: how managers actually respond to a surge
- **Question:** What do security managers do first on a surge — open lanes,
  add officers, or something else — and how fast?
- **Reply (essence):** First and fastest: rebalance existing staff (seconds to
  minutes); then open an idle lane with a full complement (minutes to ~10–15
  min); calling in new officers is slowest (tens of minutes to hours).
- **Work impact:** Scenario `M6_surge_rebalance` = reallocation (extra
  PreCheck circuit + extra regular circuit staffed from idle posts),
  `M7_dynamic_lanes` = +1 lane at peak; `M5_dynamic_staff` (hiring) kept as
  the slowest lever for comparison. The modification set now spans the real
  response hierarchy.

## Exchange 8 — boundary: do passengers switch or leave lines
- **Question:** Do people switch lines or leave when one gets long, and what
  makes them give up?
- **Reply (essence):** Switching is limited: only before committing to a lane,
  only to a clearly shorter adjacent queue; balking at the entrance is common
  when another checkpoint exists; reneging is rare (missing a flight dominates);
  perceived stalls and uncertainty drive abandonment more than raw length.
- **Work impact:** Model keeps passengers committed once in a lane (no
  mid-lane reneging), which is the right boundary given the expert's answer;
  the individual-style run allows pre-commitment lane choice (join-shortest),
  matching "switching before committing." Uncertainty/variance is therefore a
  first-class output (std, p90/p99 reported, not just the mean).

## Exchange 9 — boundary: what causes surprise long lines
- **Question:** What causes surprise long lines at normally fast airports —
  staffing, surge, or equipment?
- **Reply (essence):** Usually a coincidence: staffing gaps (breaks, shift
  changes, sick calls) reduce lanes below what the arrival rate needs; a surge
  (delayed flight, arrival bank) on top of thin staffing triggers it; equipment
  stalls are rarer but turn a queue into a visible stall.
- **Work impact:** The M7 test (dynamic lanes) is framed against this failure
  mode: capacity tracking demand keeps utilization below the nonlinear zone.
  Limitations section of the submission cites this as the model's blind spot
  (it holds lane count fixed per scenario, so it cannot itself generate a
  staffing-gap event; M7 approximates the remedy).

## Exchange 10 — judgment: which single change helps most
- **Question:** Which single change would cut waiting and its swings most?
- **Reply (essence):** Flex the number of open lanes to match the arrival rate
  in real time: the checkpoint is capacity-limited (lanes ≈ 3–5 pax/min each),
  adding a lane raises throughput nearly linearly and cuts both mean and
  variance by keeping queues below the ~15–30/lane threshold; it is also the
  cheapest and fastest lever.
- **Work impact:** `M7_dynamic_lanes` is promoted to the headline
  recommendation. Simulation result: at peak (12 pax/min) M7 cuts mean wait
  82.7 → 54.4 min (−34%) and p90 148.1 → 116.4 min (−21%) vs baseline; the
  ranking M7 > M6 > M4 ≈ M3 > M5 > M1 ≈ M2 holds across all three cultural
  styles and at light (3) and heavy (15) loads.

## Model changes that did NOT come from exchanges
- 5-minute discretization of the arrival data (`data_prep.py`,
  `discretize_data.py`) and the empirical PreCheck share (55.2%, from the
  dataset) — data processing, not consultation.
- M/M/c closed-form calibration (`parametric_baseline.py`) — standard
  derivation, prohibited topic for the expert.
- Uniform ±25% service-time jitter — modeling choice.
