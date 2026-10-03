# Expert Interaction Evidence — MM-Bench 2017_D (TSA Checkpoint)

Policy: structural anchoring before numerical filling. Exactly 10 exchanges, one question each,
each later question building on the earlier replies. Questions were plain-language, single,
<=20 words, answerable without any modeling background. All parameter values below are used in
`code/checkpoint_sim.py` / `code/queue_model.py`; the exchange number is the recorded source.

## Exchange 1 — structure (dominant bottleneck)
- Q: "At a busy airport security checkpoint, which step makes the long line move slowest:
  showing documents to an officer, or going through the scanner with bags?"
- Reply (gist): the bag-screening step (Zone B/C) is the slow step and the bottleneck; the
  ID/document check is a short, near-uniform ~10–30 s transaction with little variability,
  while the screening step bundles several serial sub-tasks (unloading bins, X-ray pass,
  walk-through, reclaim/repack) at roughly 1–3 min per passenger and is highly variable
  (flagged bags, pat-downs, re-scans add large random delays).
- How it shaped the work: model structure fixed — checkpoint = fast ID-check stage + slow
  variable screening stage. ID check modeled as M/M/1 with ~10–30 s service (officer capacity
  rarely binds); all waiting-time dynamics and variance analysis focus on the screening stage.
  No further structure questions were asked.

## Exchange 2 — structure (dominant variance driver inside the bottleneck)
- Q: which causes the biggest, most unpredictable delays: flagged bags, failed body scans,
  or slow packers?
- Reply (gist): flagged bags cause the largest and most unpredictable delays — a Zone-D manual
  bag search of ~1–5 min per event, highly variable, and it blocks the lane. Pat-downs are
  disruptive but shorter/bounded (~30 s–2 min, often resolved by re-scan). Packing is routine
  and raises the mean but adds little variance.
- How it shaped the work: the screening service-time distribution is a two-part model:
  base screening (packing + scan + reclaim) + an indicator-driven Zone-D search block.
  Variance reduction is attacked where the reply places the variance: reducing the flag
  probability and making searches off-line (Modification 2, see task b).

## Exchange 3 — parameter (flag rate)
- Q: fraction of bags flagged for extra manual search on a normal busy morning?
- Reply (gist): ~5–15%, commonly 5–10%, rising during peaks.
- Model input: base flag probability p_f = 0.08, sensitivity interval [0.05, 0.15] (source: exchange 3).

## Exchange 4 — parameter/structure (blockage propagation)
- Q: when a bag is pulled off for manual search, does the lane keep moving or back up?
- Reply (gist): the lane backs up — the flagged passenger occupies the exit/reclaim area and
  cannot clear until the search finishes; the belt keeps feeding in, so the queue grows behind
  the blockage for the duration of the search; short buffer on the belt defers the stoppage
  slightly.
- Model input: Zone-D search is a lane-blocking event of duration drawn from [60 s, 300 s]
  (source: exchanges 2, 4); the simulator implements an exit-blocking mechanism — while a
  search is active, no passenger may depart the lane. This is the mechanism that makes the
  off-line search modification measurable.

## Exchange 5 — parameter (staffing response)
- Q: are more open lanes added as the morning peak arrives?
- Reply (gist): yes, lane count follows a staffing plan tied to forecast volume; extra lanes
  open in the 1–2 h before the peak and close after; openings are lumpy/lagged (discrete steps
  when staff arrive); the Pre-Check:regular lane ratio ~1:3 is a policy choice that may not
  track the ~45% Pre-Check passenger share.
- Model input: default scenario is 4 regular + 1 Pre-Check lane at peak, 2+1 before peak;
  policy lever in task b (dynamic staffing). The 1:3 ratio mismatch with the 45% share is
  itself flagged as a structural inefficiency in task a (Pre-Check lane under-supplied).

## Exchange 6 — parameter (routing)
- Q: do passengers join the shortest line or stick with the first line entered?
- Reply (gist): Zone B is a pooled queue feeding open lanes — effectively "next available
  server"; where self-selection occurs, passengers pick the visibly shortest line (jockeying);
  no switching after commitment (bins on belt).
- Model input: pooled single queue, FCFS routing to the next available lane; jockeying variant
  (shortest-queue joining) is a scenario switch in `checkpoint_sim.py`.

## Exchange 7 — behavior (no place-keeping)
- Q: do passengers give up their place to re-pack?
- Reply (gist): essentially never — re-packing happens in place at the front; slow packers
  block the lane; only directed removal by an officer pulls someone out.
- Model input: no voluntary abandonment, no place-giving; packing delay is embedded in the
  service time at the front of the lane.

## Exchange 8 — parameter (group service)
- Q: do groups process one-by-one or together?
- Reply (gist): together — bins loaded consecutively, members scan back-to-back and wait for
  each other at reclaim; a group is a block whose time is roughly the sum of members' times
  plus shared overhead; a slow or pat-down member holds the whole group and can stall the lane.
- Model input: a fixed fraction g of arrivals are groups of size 2–5 (geometric-ish), modeled
  as batch service: lane service time = sum of member base times + shared reclaim overhead;
  batch arrivals are one source of the heavy right tail. Fraction g and group sizes are
  scenario parameters (default g = 0.15).

## Exchange 9 — parameter (abandonment)
- Q: in a long, slow line do passengers mostly grumble or leave to re-book?
- Reply (gist): mostly stay and grumble; abandonment negligible; only a small minority with
  large connection buffers or flexible tickets leave; the queue is essentially closed.
- Model input: closed queue (zero abandonment) as base case; a small abandonment tail
  (fraction leaving only when wait > 60 min, default 0.005) as a robustness check, showing
  that abandonment does not relieve the peak (result in task a/c).

## Exchange 10 — parameter (culture as mean shift)
- Q: do passengers from different countries behave very differently, or is the spread mostly
  within any one nationality?
- Reply (gist): within-country spread dominates; cultural norms shift the mean only (e.g.,
  personal-space norm → looser queue, slower closure; efficiency-first norm → gap-filling);
  treat nationality as a small adjustment to mean and variance of service/queue behavior,
  not a separate behavioral regime.
- Model input: cultural sensitivity study (task c) implemented as multipliers on packing time
  and personal-spacing (queue-closure) rate: US baseline (1.0, 1.0), "personal-space" profile
  (1.15 packing, 0.85 closure), "efficiency-first" profile (0.90 packing, 1.10 closure),
  "slower-traveler" profile (1.25 packing, 0.90 closure) — a within-band shift of the means,
  never a separate service regime. Recommendations in task d follow: accommodation via
  staffing/mix, not separate cultural queues.

## Values traceable only to the task's own dataset
- Pre-Check share ≈ 45% (stated in problem statement; arrival columns corroborate the two
  lane populations).
- $85 Pre-Check fee, 5-year validity, 1 Pre-Check lane per 3 regular lanes (problem statement;
  lane ratio also confirmed in exchange 5).
- Service-time distributions (ID check, scan times, belt-to-belt dwell) estimated from the
  cleaned CSV (see `code/clean_data.py` output table in results).
