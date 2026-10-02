# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — MM-Bench 2003_C

Three exchanges, one question each. Each reply was converted into a
parameter or decision rule in `code/model.py` before the next exchange.

## Exchange 1

**Question** (`expert_question_1.md`): At a busy airport during the morning
peak, do most passengers' checked bags for a departure arrive roughly one to
two hours before the flight leaves, or right near gate time?

**Reply (summary)**: The dominant pattern is check-in on terminal arrival,
1–2 hours before scheduled departure; a minority (late arrivals,
connections, gate-checked) present bags near gate time. The screening load
is driven by the check-in arrival curve, not gate times.

**How it changed the work**:
- Model parameter: bag-arrival window = `[t-d-2h, t-d]` per flight
  (`WINDOW = 120` in `model.py`).
- 80% of each flight's bags spread uniformly over the first 80 min of that
  window; 20% ("late" fraction, `LATE_FRAC = 0.20`) over the final 40 min,
  matching the "minority near gate time" statement.
- Sizing rule uses the peak of that arrival curve, not the average (see
  Exchange 3).

## Exchange 2

**Question** (`expert_question_2.md`, builds on reply 1): Bags from a flight
usually reach the screening line 1-2 hours before the flight leaves. When
does the last bag for that flight typically have to be screened so it is
still loaded in time?

**Reply (summary)**: Roughly 30–45 minutes before scheduled departure
(~45–60 for international/widebody); the screening line must clear a
flight's bags by that cutoff, not at gate time.

**How it changed the work**:
- Model parameter: screening buffer `offset ∈ [30, 45]` min before
  departure; baseline `offset = 40` (`--offset`).
- Deadline rule: a flight's bag stream must finish screening by `dep -
  offset`; the schedule's per-flight feasibility test is
  `L / (n_eds · cap) ≤ offset`.
- Sweep `offset=35,40,45,60` (logs/sweep_offset.log) shows the answer is
  stable at 11–12 EDS across the expert's whole interval, with +2 units at
  the 60-min (international) end.

## Exchange 3

**Question** (`expert_question_3.md`, builds on replies 1–2): A bag can be
checked up to 1-2 hours before departure and must be screened by 30-45
minutes before. How do airlines and airports make sure enough scanners are
working at the right times?

**Reply (summary)**: They size to the *peak* of the bag-arrival curve with
margin, not to the daily average; treat available capacity as ~92% of
installed; keep multiple pooled units in one screening area so a failed
unit's load shifts to others (maintenance off-peak); manage the queue to
drain ahead of the cutoff; smooth demand with check-in incentives.

**How it changed the work**:
- Sizing rule (replaces a naive average-throughput count): required
  machines = `max(peak arrival rate / cap, total bags / (120·cap))` plus
  headroom for the late-check surge; `cap = 160·0.92/60` bags/min per
  machine (the 92% is applied to *available* capacity, per the reply).
- Standby/pooling: `m_installed = ceil(m_required · 1.05)`
  (`STANDBY_FRAC = 0.05`), the margin for a failed unit shifting load.
- Queue must drain ahead of `dep - offset` (buffer before cutoff), which is
  the `offset` constraint in the scheduler.

## Reply-as-input, not content

No sentence from any reply was copied into `solution.json`. Only the
numerical values and the decision rules above (window 1–2 h, buffer 30–45
min, peak sizing, 92% availability, 5% standby) travel into the model, in
its own formulation.
