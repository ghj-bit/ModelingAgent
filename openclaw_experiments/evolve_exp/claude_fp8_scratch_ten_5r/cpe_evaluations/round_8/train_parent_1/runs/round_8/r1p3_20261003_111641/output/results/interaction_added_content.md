# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — Problem 2017_D (TSA checkpoint)

Policy followed: structural anchoring before numerical filling. Each question
builds on the previous reply; each reply was converted into a model element
before the next exchange. Ten exchanges, one question each.

## Exchange 1 — structural: dominant bottleneck
- Q: In a busy US checkpoint, which single step do passengers complain about most, and why?
- A (gist): The divestiture/reclaim step (Zone B/C) dominates complaints — it is the
  only step passengers are physically active in, it is slow and awkward, the queue
  visibly stalls there, and reclaim wait is unpredictable because bin exit times vary
  with X-ray flags and secondary searches. ID check and the scanner are brief and passive.
- Work produced: sets Zone B (belt) as the modeled bottleneck and the primary state
  transition of the system; Zone A and the scanner are modeled as fast service stages.
  Drives subproblem a (bottleneck identification).

## Exchange 2 — parameter: belt service time (given E1)
- Q: How many seconds does a typical passenger spend at the belt on the divest/reclaim cycle?
- A (gist): ~30–60 s total for regular passengers (15–30 s divest + 15–30 s reclaim);
  10–20 s for Pre-Check/frequent travelers; 60–90 s+ for families/heavy travelers.
- Work produced: belt service time distribution used in the simulation:
  regular ~ U(30,60) with a heavy tail to 90 s; Pre-Check ~ U(10,20) s. (Exchange 9
  confirms and refines the Pre-Check values.)

## Exchange 3 — edge case: source of the variance spikes
- Q: What triggers the sudden, unexplained line surges at normally short-wait airports?
- A (gist): A temporary loss of parallel capacity, not a demand surge — lane closures /
  staffing gaps (losing 1 of 3–4 lanes cuts throughput 25–33 % instantly), single slow or
  flagged passengers (1–3 min lane block), equipment stoppages, arrival bunching (flight
  banks), and divestiture clustering. At short-wait airports the buffer staffing is thin,
  so variance comes from capacity drops and service-time outliers.
- Work produced: the variance mechanism in the model = (i) stochastic lane outages with
  thin buffer staffing, (ii) service-time outliers/flags. Justifies modeling the surge
  statistics (P90/P95 wait) rather than the mean alone.

## Exchange 4 — parameter: flag rate (given E3's outlier mechanism)
- Q: What fraction of passengers gets pulled aside for extra search on a normal day?
- A (gist): ~2–5 % overall; Pre-Check ~1–2 %, regular ~3–6 %; it clusters by traveler
  type and hour, and can run well above the daily average inside a leisure flight bank.
- Work produced: flag probability p_flag = 0.045 regular / 0.015 Pre-Check in the
  simulation, with a multiplier in bank/peak conditions (sensitivity lever).

## Exchange 5 — cultural norms (subproblem c)
- Q: What differences do you actually notice between nationalities at the belt?
- A (gist): Personal-space norms (US/N. Europe) keep a visible gap, don't close up,
  don't reach past others → wastes belt length, slower effective service at high load.
  Collective-efficiency norms (Swiss/German/Nordic) self-organize, pre-divest, lower
  variance. Individual-efficiency norms (Chinese, some Indian/Middle Eastern) edge
  forward, fill gaps, start early → higher throughput per lane but chaotic reclaim and
  more "cutting" complaints. Groups/families occupy the belt longer regardless of
  nationality. Infrequent vs frequent traveler often dominates nationality.
  Culture mainly shifts spacing discipline, pre-divestiture timing, and queue-position
  assertiveness → changes both mean service time and its variance.
- Work produced: the three cultural profiles used in the subproblem-c sensitivity sweep
  (personal-space / collective / individual) as multipliers on belt service mean and
  standard deviation, plus a frequent-traveler effect. This is the basis of the
  accommodation design (pre-divest zones, lane assignment by traveler type).

## Exchange 6 — boundary behavior during a lane outage (given E3)
- Q: When one lane shuts down mid-bank, what happens to the people already in its line?
- A (gist): They are merged into adjacent open lanes (often let go first / interleaved)
  because stranding them causes complaints. The merge costs throughput: a 30–90 s
  disruption per merge event plus a temporary dip in that lane's rate. Positional
  conflict ("cutting") is the main friction and culture-dependent. If no adjacent lane
  can absorb them, the line simply grows in place until the lane reopens.
- Work produced: the outage handling in the simulation — lost capacity plus a transient
  merge penalty of 30–90 s on the surviving lane(s), and queue growth in place when at
  capacity. This is the variance-spike mechanism modeled for subproblems a and b.

## Exchange 7 — structural: queue geometry
- Q: Do travelers pick a specific lane's line, or stand in one shared line feeding all lanes?
- A (gist): Busy US checkpoints use a single shared feeder queue (serpentine) that feeds
  all open screening lanes; a staff member directs each passenger to the next free lane.
  Per-lane lines exist mainly at small/low-traffic checkpoints or physically separated
  Pre-Check lanes, where travelers self-select the shortest visible line. With a shared
  feeder, a lane outage just reduces the number of servers draining the common queue;
  the merge penalty applies mainly to per-lane configurations or the redirect moment.
- Work produced: the simulation's core queue is an M/G/c shared-feeder (serpentine) queue
  — one arrival stream, c parallel servers (lanes), directed assignment. This is the
  structural backbone of the whole model and the reason a lane outage reduces server
  count rather than stranding a dedicated line.

## Exchange 8 — parameter: staffing response lag (given E3, E7)
- Q: How quickly do supervisors open extra lanes when the shared line grows, and what triggers it?
- A (gist): Reactively, not preemptively; ~5–15 min from visible queue growth to an added
  lane actually screening. Triggers: the line reaching a physical threshold (rope/doorway/
  spilling into concourse), complaints, or break-rotation timing. The lag is because
  opening a lane needs a free officer, a supervisor decision, and setup time. The system
  responds to the symptom after the line already formed — a major source of the
  overshoot-then-drain variance.
- Work produced: the control policy in the "current process" simulation is reactive
  threshold-based staffing with a 5–15 min lead time. This is what modification b2
  (preemptive/forecast-based staffing) replaces, and it is a named model parameter.

## Exchange 9 — validating a key model assumption: Pre-Check speed-up (given E2)
- Q: Does Pre-Check's reduced divestiture actually make the belt step noticeably faster, and by how much?
- A (gist): Yes, noticeably. Pre-Check belt step ~10–20 s vs regular ~30–60 s — roughly
  2–3× faster, saving 20–40 s per passenger; the saving is almost entirely on the divest
  side (fewer bins, laptop stays in bag). The gap shrinks when Pre-Check passengers still
  have liquids/electronics out or are infrequent. Pre-Check's real advantage is often
  lower variance (fewer bins, fewer alarms, fewer belt stalls), not just lower mean.
- Work produced: confirms and pins the Pre-Check service-time values used in E2; justifies
  modeling Pre-Check as a faster, lower-variance server class. Supports the recommendation
  to shift capacity toward Pre-Check and to treat Pre-Check expansion as a variance-reducer.

## Exchange 10 — policy lever: pre-queue divestiture (given E5)
- Q: Do pre-queue divest tables (divest while waiting) genuinely speed things up, or backfire?
- A (gist): They help, with conditions. They work when the area is sized to the queue and
  staffed so people actually use it — then belt occupancy drops toward the Pre-Check-like
  10–20 s and its variance drops too; the gain is largest for infrequent travelers and
  families (the main belt-stallers). They backfire when the table is too small/far (people
  divest twice), when passengers won't divest early (strong personal-space/queue-order
  norms — they wait their turn), or when they just relocate the bottleneck into the queue
  without net throughput gain if the belt wasn't the binding constraint. Net: they convert
  belt time into queue time and mainly buy variance reduction, not raw throughput, unless
  the belt was the constraint.
- Work produced: modification b1 (pre-queue divest zone) and its modeled effect — a
  reduction in belt service mean and variance, with the condition that it only reduces
  total wait when the belt is the binding constraint; it relocates time into the queue
  otherwise. Drives the conditionality of the subproblem-d recommendations.

## Summary of how the replies shaped the model
- E1 → Zone B belt = modeled bottleneck (subproblem a).
- E2, E9 → belt service-time distributions for regular and Pre-Check.
- E3, E6 → variance mechanism: thin-buffer lane outages + merge penalty + service outliers.
- E4 → flag/pull-aside probability.
- E5 → cultural profiles (personal-space / collective / individual) and frequent-traveler effect (subproblem c).
- E7 → shared-feeder M/G/c queue as the structural backbone.
- E8 → reactive 5–15 min staffing lag as the baseline control policy (replaced in b2).
- E10 → pre-queue divest zone as modification b1, with its conditionality (subproblems b, d).

All ten exchanges produced at least one concrete model element (parameter, mechanism,
or structural decision). No exchange produced only prose.
