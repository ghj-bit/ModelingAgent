# Interaction Evidence — 2017_D (TSA checkpoint modeling)

Ten exchanges. For each: question, reply (abridged), and how it became work.
All expert-sourced values are used as calibrated inputs in `code/sim.py` and
recorded in the parameter table of `results/solution.json`.

## Exchange 1 — where the bottleneck is (structural)
- **Q:** At a busy US airport checkpoint, which step do passengers most often
  complain about taking too long: ID check, bins/X-ray, or body scanner?
- **Reply (abridged):** The bin/X-ray step — removing shoes, belts, jackets,
  electronics, liquids, loading bins, and reclaiming belongings — is the
  dominant complaint and main bottleneck; longest single service step (tens of
  seconds to a minute-plus), ID check is a few seconds, body scanner ~5–10 s.
- **Work:** Fixed the model's causal topology: bin/prep station is the
  dominant server in each lane; body scan set to ~15 s (upper end of the
  stated 5–10 s, covering alarm re-scans). The simulation structure
  (ID → bin → belt reclaim ∥ body scan, with the belt as a shared reclaim
  server) is built around this. `code/sim.py`.

## Exchange 2 — queue discipline (structural rule)
- **Q:** When many travelers line up at a US checkpoint, do people let others
  jump ahead, or is going out of turn strongly frowned upon?
- **Reply (abridged):** Strongly frowned upon; FCFS is enforced socially and
  physically by the single-file line. Narrow exceptions: officer-directed,
  re-joining after a send-back, obvious medical/mobility need.
- **Work:** Model assumption A6 (strict FCFS within each lane, no voluntary
  preemption) and A7 (adjacent-lane shifts only; no line shopping — later
  confirmed in exchange 10). FCFS is the state-transition rule of the
  simulation; the exceptions become the pat-down/flag side channels that
  serve out-of-band.

## Exchange 3 — ID-check service time (parameter)
- **Q:** At a busy checkpoint, roughly how long does one passenger take at
  the ID desk before the next is called?
- **Reply (abridged):** ~10–20 s, typically ~15 s; 5–10 s for quick checks,
  30 s+ when documents cause problems.
- **Work:** ID desk service = lognormal(15 s, cv 0.29) in `sim.py`
  (cv 0.29 carries the tail to the 30 s+ case). Replaces the dataset's
  5–20 min ID column, which exchange 4 showed is not a service time.

## Exchange 4 — meaning of the dataset ID column (data interpretation)
- **Q:** From your knowledge of airport operations, what do the recorded
  5–20 minute ID-check times in this dataset likely include?
- **Reply (abridged):** Not service times — they are queue waits (interval
  from joining the queue to the desk, plus the ~15 s interaction), possibly
  compounded by timestamp-definition gaps and headway aggregation.
- **Work:** Data-cleaning decision: the ID columns C/D are treated as
  wait-plus-service observations, NOT as service-time calibrations. Service
  time comes from exchange 3. Documented in the task 1 data section of
  `solution.json`; the censored-tail rule for those columns is still applied
  (last recorded value per unit is a lower bound).

## Exchange 5 — belt behavior (structural)
- **Q:** After placing bags on the belt, do passengers stand by until their
  bins come out, or walk off and reclaim later?
- **Reply (abridged):** They stand by the machine and wait for their own bins;
  no holding area exists and unattended bags are a security concern. Only a
  bag pulled for secondary screening is waited on separately.
- **Work:** Confirms the belt reclaim server blocks the passenger (passenger
  completion = max(belt reclaim, body scan, pat-down)), i.e. the belt is in
  the passenger's critical path, modeled as a per-lane shared reclaim server
  in `sim.py`. Flagged bags form the separate Zone D channel (exchange 6).

## Exchange 6 — bag flags (parameters)
- **Q:** How often does an X-ray officer flag a bag for secondary search,
  and how long does it take?
- **Reply (abridged):** ~5–15% of bags, commonly ~10%; secondary search
  ~1–3 min (under a minute for a quick visual check, several minutes if the
  passenger must be located or a pat-down is also triggered).
- **Work:** `FLAG_PROB = 0.10`, `FLAG_TIME = 90 s` (midpoint of 1–3 min)
  added to the belt server in `sim.py`; sensitivity swept 0.05–0.20
  (logs/sweep_flag.log) — throughput effect only, not queue-wait effect,
  because the queue is bin-bound (see below).

## Exchange 7 — pat-downs (parameters)
- **Q:** How often is a person pulled aside for a pat-down after the scanner,
  and how long does it take?
- **Reply (abridged):** ~2–5% routinely (~2–3%), rising to 5–10% under
  heightened screening or opt-outs; ~1–3 min, ~30–60 s for a quick check.
- **Work:** `PAT_PROB = 0.03`, `PAT_TIME = 120 s`, served at a dedicated
  pat-down officer per lane in `sim.py`; swept 0.02–0.10
  (logs/sweep_pat.log).

## Exchange 8 — personal-space norms (cultural sensitivity)
- **Q:** Do travelers cluster close together in line, or keep noticeable
  distance from the person ahead?
- **Reply (abridged):** Noticeable distance, ~0.5–1 m (arm's length to a
  couple of feet); compresses under crowding; disappears at the front where
  people crowd the belt.
- **Work:** Cultural parameterization for subproblem c: the US baseline keeps
  a personal-space buffer, which is why the "tight-packing" (Swiss-style
  collective efficiency) variant in `code/culture.py` shortens belt-reclaim
  congestion (28.6 → 23 s, cv 0.49 → 0.30). Result: wait mean −15%,
  p95 wait −16% (logs/culture.log). The buffer also motivates the
  recommendation to space queue lanes and stage the reclaim area.

## Exchange 9 — Pre-Check speed advantage (parameter)
- **Q:** Do Pre-Check travelers usually prepare bags much faster, and why?
- **Reply (abridged):** Faster but moderately so: no shoes/belts/light
  jackets/laptop removal means fewer bins and less repacking; they are also
  more experienced. Core actions remain, so the saving is a fraction of the
  regular belt time, not an order of magnitude; the bigger Pre-Check
  advantage is the shorter queue.
- **Work:** `BIN_PRE_MULT = 0.70` (30% shorter bin/prep service) in
  `sim.py`; the "shorter queue" half is exactly Modification 1
  (rebalancing Pre-Check lane capacity), whose measured benefit (−52% mean
  wait at peak) is dominated by queue length, matching the expert's framing.

## Exchange 10 — lane-switching behavior (structural rule)
- **Q:** At a big airport with several lines, do travelers walk between
  security areas to pick the shortest line, or stay with the line they
  joined?
- **Reply (abridged):** Mostly stay put — checkpoints are physically
  separated, other lines not visible, switching costs minutes. Exceptions:
  shifting to a visible adjacent lane within one hall; frequent flyers who
  know a faster checkpoint.
- **Work:** Assignment rule in `sim.py`: passengers commit to their population
  (Pre-Check / regular) and round-robin over its lanes; no cross-population
  or cross-hall migration. This bounds the model's scope to a single
  checkpoint hall and justifies why Modification 3 (dynamic lane merging)
  must be operator-driven rather than passenger-driven.

## What the expert exchanges did not cover
Arrival rate shape (Poisson assumed from the dataset inter-arrivals), the
45% Pre-Check share (given in the problem statement), and the 1:3 Pre-Check
lane ratio (given in the problem statement). No value in the model comes
from memory without a recorded source.

## Model outcome summary (for the record)
- Queue is **bin/prep-bottleneck-bound**: sweeping flag rate (0.05→0.20) and
  pat-down rate (0.02→0.10) moves total throughput but barely moves queue
  wait (logs/sweep_flag.log, logs/sweep_pat.log). This is why the
  modifications target the bin step and lane allocation, not secondary
  screening.
- At the observed peak load (0.32 pax/min), the current 1:3 staffing is
  unstable (wait mean 8034 s, max 22399 s); demand-matched 3:4 staffing
  cuts mean wait 53% and p95 wait 66% (logs/peak_base.log, logs/peak_bal.log).
- Cultural variants: slow-traveler style +22% mean wait, +25% p95; tight
  packing −15%; prepared-traveler −19% (logs/culture.log).
