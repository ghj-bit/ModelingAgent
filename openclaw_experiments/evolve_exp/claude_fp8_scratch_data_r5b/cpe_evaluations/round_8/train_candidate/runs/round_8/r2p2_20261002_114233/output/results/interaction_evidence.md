# Interaction Evidence — 2003_C (EDS/ETD screening, Airports A & B)

Three expert exchanges, one question each, each reply converted into a model
element before the next exchange.

## Exchange 1 — operational structure of the screening input

**Question** (`logs/operator_feedback/expert_question_1.md`):
When a plane's bags all arrive at the screening line at once, are they scanned
in one short burst or spread over the hour?

**Reply** (`logs/operator_feedback/expert_reply_1.json`): one short burst; a
flight-sized batch is processed back-to-back by the available units; peak
machine demand is driven by the largest simultaneous/overlapping batch, not by
the hourly total alone.

**Converted into work:**
- Model input structure changed from "uniform stream over the hour" to
  "flight-sized bursts arriving at check-in open", one FIFO backlog served by
  all N machines in parallel (`code/eds_model.py`, `simulate()` / event-time
  FIFO processing).
- Sizing criterion: N must absorb the peak overlapping-batch load within the
  flight deadline, not merely match hourly total ÷ hourly rate.
- Validity: holds for the 2003-era checked-bag flow at the two airports' peak
  departure hour; the burst is the whole flight's checked bags (100% screening
  mandate, no bypass).

## Exchange 2 — what happens when bursts outrun throughput

**Question** (`expert_question_2.md`): if several bursts line up and machines
cannot keep up with one before the next flight's bags arrive, what happens to
the bags in practice?

**Reply** (`expert_reply_2.json`): they queue in a staging area; no abandonment,
no bypass; backlog grows within the hour; the flight either waits (preferred,
briefly) or bags are offloaded; staging space and labor bind before machine
capacity; under the 100% mandate a bag cannot be released without an EDS scan.

**Converted into work:**
- The model is a single FIFO service center with a growing backlog — no
  "skip a batch" or "partial screening" branch exists in the code.
- Added operational constraints to Task 2's constraint set: physical staging
  space and handler labor are binding before machine count; the binding
  effect is a growing queue and departure delay, not lost bags.
- Schedule (Task 3) reports per-flight queue position and slip so the
  staging-space requirement can be read off (peak backlog ≈ 2,900–3,200 bags
  at minimum N; at minimum N + 4 the peak backlog falls ≈ 25%).
- Same queuing logic applied to the ETD overlay lane (Task 6): the 20%
  overlay is a scaled copy of the same burst sequence at 4–5x lower
  per-lane rate, so the sustained-throughput estimate (13–16 lanes)
  under-counts by ~40–60%; the event-time sim gives 23/25 (A/B) ETD lanes
  at rX = 40 — the exchange-1/2 insight re-used, not a new assumption.

## Exchange 3 — decision-relevant hold threshold

**Question** (`expert_question_3.md`): roughly how long can a flight wait for
its bags before the airline would rather delay or cancel?

**Reply** (`expert_reply_3.json`): ~10–20 min absorbed routinely (empirical
judgment, not a fixed rule); 15–30 min tolerated only without cascading
rotation/crew effects; beyond ~30 min the airline delays or cancels.
Planning threshold ≈ 15–30 min of bag-wait.

**Converted into work:**
- Deadline parameter in the model: a flight is delayed iff its bags clear
  after `min(D − S_LOAD + Th, horizon)`, with `Th = 15` (soft) and `Th = 30`
  (hard) minutes; results reported for both.
- Task 1 sizing runs on Th = 30 (hard limit = the number of machines that
  guarantees no delay); the Th = 15 row quantifies the cost of planning to
  the soft threshold (N ≈ 1.6–1.9× larger, i.e. ~$16M–$19M extra per
  airport at ~$1M/machine).
- Task 7 sensitivity: the hold threshold is the single most decision-relevant
  input — halving it (30 → 15 min) roughly doubles the EDS count at fixed
  throughput; a 10 min/machine throughput gain (~5%, within the 160–210 range)
  cuts the count ~7–8%, less than the threshold lever.

## What the exchanges did NOT change

- No EDS/ETD physical parameters (rates 160–210 / 40–50 bags/h, uptime 92% /
  98%, accuracies 98.5% / 99.7%, costs $1M / $45k) — all from the task
  statement.
- The 2% cancellation rate — task dataset note.
- Empirical inputs that remain outside the exchanges (checked-bag intensity,
  check-in window, screening cutoff, bag-handling time) are listed in the
  solution.json parameter table with their provenance.
