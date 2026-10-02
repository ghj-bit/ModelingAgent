# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence

Three expert exchanges, one question each. Questions were short, common-sense, and
about the real-world checkpoint, not the model. Each reply became a parameter,
constraint, or decision rule in the model or its interpretation.

## Exchange 1 — Data-Model Structural Fit

**Question (expert_question_1.md):**
"When you watched this checkpoint, how do you know a person actually left before a
later person reached the scanner?"

**Reply (expert_reply_1.json), in substance:** The columns are independent
per-station timestamp streams (arrivals, ID-check, scanner exit, X-ray exit, belt
time), not a tracked passenger path. There is no passenger ID linking a person
across zones, so "left before a later person reached the scanner" is not
observable; only aggregate flow and per-station service times are.

**How the reply became work:** This is the structural constraint of the whole
model. Because the streams are independent and unlinked, the model does NOT track
individuals through zones A→B→C. Instead each zone is treated as an aggregate
flow node:
- The two arrival streams (Pre-Check, Regular) define the inflow rates
  (λ_pre = 6.53/min, λ_reg = 4.63/min from inter-arrival means).
- The station-level columns define per-station service times (ID-check duration,
  belt round-trip duration, MMW inter-exit spacing), used as the service-time
  parameters of each node.
- The belt round-trip ("Time to get scanned property") is folded into the
  screening server as a fixed per-passenger time, since the conveyor moves every
  bag on it.
The model is therefore a set of per-lane M/M/1 queues fed by the arrival rates,
not a discrete-event network of named passengers. This is what makes the model
structurally valid for this data: it only uses aggregate flows and service times,
which is exactly what the data supports.

## Exchange 2 — Dominant Bias / Selection Mechanism

**Question (expert_question_2.md), building on reply 1:**
"Of these sparse, separate station streams, which one do you think undercounts the
true flow the most, and why?"

**Reply (expert_reply_2.json), in substance:** The ID-check stream undercounts most.
It is the only station where the recorded time is a *process duration*
(arrival-to-"next called forward") rather than an exit timestamp, and it has the
most missing values — so it captures only the subset of passengers an officer
happened to log, not the full arrival flow. The arrival streams are the most
complete and should be treated as the true inflow; scanner-exit and X-ray-exit
streams are partial samples of outflow.

**How the reply became work:** This fixed the bias analysis and the choice of
which column feeds which model input:
- The arrival streams are used as the **true inflow** (λ_pre, λ_reg). They are the
  least biased measure of how many passengers actually arrive.
- The ID-check duration column is used **only** for its per-passenger service-time
  value (~10–13 s), **not** as a count of throughput. Because it is a logged-
  duration subset with the most missing values, using it to estimate flow would
  undercount; the model therefore takes its *rate* from the arrival streams and
  its *service time* from the ID-check durations.
- Scanner-exit / X-ray-exit columns are treated as **partial outflow samples**:
  their inter-exit spacings calibrate body-scan and X-ray service times but are
  not used to infer arrival counts.
This directly prevents the model from being biased by the sparse ID-check stream
and is recorded as a limitation/bias in the submission.

## Exchange 3 — Validation / Interpretation Criterion

**Question (expert_question_3.md), building on reply 2:**
"For a TSA manager, what sign in the queue's behavior would say a line is now
unsafe, not merely slow?"

**Reply (expert_reply_3.json), in substance:** A queue is unsafe, not merely slow,
when it stops being a queue: the physical waiting area saturates and passengers
back up past the checkpoint's designed holding capacity — into the concourse,
blocking other lanes or egress — so crowding itself becomes the hazard. The sign
is a *growing, unbounded* line with no self-clearing: arrivals persistently exceed
the maximum service rate, so the backlog never drains even after the peak, and
passengers are held in a dense, unmanaged mass where screening and emergency egress
can no longer be controlled. Slow is a long but bounded wait; unsafe is a line that
keeps growing and spills out of the controlled area.

**How the reply became work:** This supplied the operational safety criterion the
model uses to distinguish "slow" from "unsafe":
- The model tracks a **queue-growth indicator**: the end-of-horizon queue length
  and a `growing` flag that is true when the queue ends at or above a holding-
  capacity threshold (HOLD_CAP = 40 passengers, the physical waiting-area capacity)
  and does not drain. This is the operationalization of "a line that keeps growing
  and spills out of the controlled area."
- A scenario is classified **unsafe** (ρ ≥ 1, arrivals exceed service capacity,
  unbounded growth) rather than merely **slow** (ρ < 1, long but bounded wait).
  The base case (ρ_pre = 5.2, ρ_reg = 1.67) is therefore flagged unsafe, not slow.
- The safety decision rule used in the recommendations: add/rebalance capacity until
  both ρ_pre < 1 and ρ_reg < 1 (both queues drain), which the simulation confirms
  at 6 pre + 6 regular lanes (mean wait 2.0 min, no growth) and at pre-heavy
  8/6 or reg-heavy 6/8 (mean wait ~1.3 min).
This criterion is what makes the model's output decision-relevant: a manager
reads "safe/slow" vs "unsafe/growing" and acts on the growth flag, not on a raw
wait-time number alone.

## Provenance of expert-influenced values

| Model element | Value / form | Source |
|---|---|---|
| Node structure (aggregate M/M/1 per lane, no tracked passenger) | structural constraint | Exchange 1 |
| Inflow rates λ_pre, λ_reg from arrival streams only | 6.53/min, 4.63/min | Exchange 2 (bias) + dataset |
| ID-check column used for service time only, not flow | ~10–13 s | Exchange 2 (bias) |
| Scanner/X-ray columns as partial outflow (service time only) | 11.6 s MMW, 7.5 s X-ray | Exchange 2 (bias) + dataset |
| Safety criterion: growing/undrained queue vs bounded wait | `growing` flag, HOLD_CAP=40 | Exchange 3 |
| Decision rule: operate with ρ_pre<1 and ρ_reg<1 | stability threshold | Exchange 3 |

No expert sentence was copied into solution.json; only the values, constraints,
and decision rules above were integrated, in the model's own formulation.
