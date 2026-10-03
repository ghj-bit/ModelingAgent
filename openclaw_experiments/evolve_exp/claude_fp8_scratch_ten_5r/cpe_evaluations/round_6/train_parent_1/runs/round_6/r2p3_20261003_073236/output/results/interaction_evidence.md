# Interaction Evidence — 2017_D (TSA Checkpoint Throughput & Variance)

Ten expert exchanges. Each reply became a model parameter, decision rule, or a
run whose outcome is reported. Questions are qualitative (<=20 words); replies
are field-practice estimates, not data.

## Exchange 1 — secondary inspection duration (structural parameter, Zone D)
Q: How long does a flagged bag take for extra search?
A: ~1–3 min routine secondary bag check; 5–10 min if an explosive-trace swab is
positive/ambiguous or a supervisor is needed; a full bag dump can exceed that.
Used as: `SEC_DELAY_ROUTINE = 90 s`, `SEC_DELAY_ESCALATED = 420 s` in
`checkpoint_model.py`; `p_esc = 0.10` mixes the two. Drives the tail of the wait
distribution and the S2 alarm-spike scenario.

## Exchange 2 — lane counts at a busy hub (topology)
Q: How many lanes open at once at a busy checkpoint, incl. Pre-Check?
A: ~5–12 total; common config 1 Pre-Check per 3 regular, so 6–9 regular + 2–3
Pre-Check at a hub; small airports 2–4 total.
Used as: baseline topology `n_reg = 8`, `n_pre = 3` (within the stated 1:3 range);
congested case `n_reg = 6, n_pre = 2`; light case `n_reg = 10`.

## Exchange 3 — per-lane throughput (service-rate calibration)
Q: How many passengers can one lane clear per hour end-to-end?
A: ~200/hr regular, 250–350/hr Pre-Check; drops to 100–150/hr under congestion /
high alarm rate.
Used as: calibration target for the per-lane service chain. Baseline achieves
~10.6 pax/min total across 11 lanes ≈ 185/hr/lane, in the stated regular range.
Pre-Check modeled 25% faster at the body stage (fewer divestiture items).

## Exchange 4 — operator first response to a backup (decision rule)
Q: What do staff do first when a lane is overwhelmed?
A: 1) open/reassign lanes (fastest lever, throughput ∝ open lanes); 2) reallocate
staff within the checkpoint (pull from underloaded Pre-Check to regular, add a
floater to the belt); 3) demand-side (redirect eligible to Pre-Check, throttle the
ID feed).
Used as: scenario ordering in `scenarios.py` and the S3 dynamic-staffing case
(open 2 reg lanes + 2 secondary officers).

## Exchange 5 — dominant cause of a sudden long line (variance driver)
Q: What single cause makes a line suddenly much longer than normal?
A: A transient mismatch of demand vs. capacity — an unexpected surge (clustered
flights, a bank of delayed flights) hitting fixed/reduced lanes, and/or a supply
loss (breaks, shift change, callouts); plus alarm/secondary-rate spikes that stall
one lane and cascade. Baseline capacity is usually adequate.
Used as: the S2 alarm-spike scenario (`p_sec = 0.35`, `n_sec_officers = 1`), which
reproduces the "unpredictable long line": p95 wait jumps 1690 s → 10484 s.

## Exchange 6 — cross-cultural speed differences (sensitivity magnitude)
Q: Do travelers from different countries move at noticeably different speeds?
A: Modest, ~10–30% in divestiture/queue movement; driven more by familiarity and
frequency (business vs. leisure, families, non-English speakers) than nationality.
Culture mainly affects queue spacing/behavior, not raw service speed.
Used as: the `culture` knob scaling regular stage time: slow = 1.2, baseline = 1.0,
fast = 0.85 (a 15% span, inside the 10–30% band). C1–C5 scenarios.

## Exchange 7 — accommodating different paces (mechanism)
Q: What keeps fast and slow travelers from slowing each other down?
A: Lane segmentation by traveler type; a self-identified "ready/express" lane;
staggered feed / metering at the ID check (batch release); a pre-divestiture
staging area that removes unpacking from the critical lane.
Used as: design of the cultural-accommodation recommendation and the
`pre_belt_frac` / lane-pool separation in the model; informs recommendation R3.

## Exchange 8 — cost-effectiveness of a lane vs. a belt screener (policy input)
Q: New lane vs. one more belt screener — which improves throughput per dollar?
A: A belt screener wins per dollar when the belt/X-ray is the bottleneck (raises a
lane from ~100–150/hr back toward 200+/hr for marginal labor); a new lane wins
when lane count itself is the constraint (queues form before the belt).
Used as: the bottleneck-dependent recommendation (R1 add belt staff first, R2 open
lanes only when queue forms pre-belt).

## Exchange 9 — Pre-Check / regular interaction (shared resources)
Q: Does a longer/shorter Pre-Check line ever hurt the regular line?
A: Hurts via shared staffing/equipment/downstream (Pre-Check often overstaffed
relative to its ~45% demand; occupies machines/floor; both merge at Zone C).
Helps via demand diversion (each eligible passenger routed to Pre-Check leaves the
regular queue and divests faster).
Used as: the S4 reallocation scenario (`n_pre = 2, n_reg = 10`) showing the
tradeoff — Pre-Check mean wait worsens 651 s → 926 s while regular improves
slightly; supports recommendation R4 (reallocate only when regular queue is the
binding constraint).

## Exchange 10 — single highest-leverage change (policy centerpiece)
Q: If only one change could cut long lines and their unpredictability?
A: Dynamic, demand-matched lane staffing — flex open lanes and belt screeners to
track real-time arrivals, exploiting the usually-underloaded Pre-Check lane;
addresses variance (absorbs transient capacity losses), cheaper and faster than
permanent lanes. Works only if staffing is genuinely flexible (cross-trained
floaters / on-call).
Used as: recommendation R1 (the centerpiece) and the S3 dynamic-staffing scenario,
which cuts p95 wait 1690 s → 1308 s at the baseline load.

## What the exchanges changed in the work
- Parameters set from replies: secondary delay (E1), lane topology (E2), service
  rate target (E3), culture span (E6), reallocation tradeoff (E9).
- Decision rules / scenarios: operator response ladder (E4) → S3; variance driver
  (E5) → S2; accommodation mechanisms (E7) → R3; cost rule (E8) → R1/R2
  ordering; dynamic staffing (E10) → R1 + S3.
- No reply was used as a computed value; each was converted to a parameter,
  constraint, or a run whose numbers appear in `scenarios.csv` / `solution.json`.
