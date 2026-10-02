# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — Problem 2003_C (EDS/ETD screening capacity)

Three expert exchanges, one question each. Each reply was turned into a concrete
model element before the next question was asked. The expert replies are input,
not content: only the resulting constraint / assumption / test is used in the
submission, in my own formulation.

## Exchange 1 — dominant operational mechanism

**Question (expert_question_1.md):** In practice, what most often prevents a
departing flight from leaving on time: late-arriving checked bags, the screening
process itself, or passenger boarding delays?

**Reply (summary):** Late-arriving bags and passenger boarding are the dominant
causes of departure delay; the screening process itself is rarely the binding
constraint. Screening is a parallel, high-throughput process that usually keeps
up. It becomes binding only under (a) a machine outage (~92% EDS availability),
(b) a concentrated arrival surge within the peak hour, or (c) added secondary
screening (ETD) that lengthens the per-bag path.

**How the reply shaped the work:**
- Established that the model's core deliverable is a *capacity* question (does
  the screening subsystem clear the peak-hour bag load within its time window),
  not a delay-attribution model. I therefore sized the EDS fleet by total
  bags-per-hour against the screening time budget, rather than by per-flight
  punctuality.
- Confirmed that EDS availability (~92%) and concentrated arrival surges are the
  two mechanisms that can make screening the binding constraint — both are
  explicit stress cases in Task 3's schedule feasibility check.
- Flagged ETD as the factor that "lengthens the per-bag path," motivating the
  separate ETD-lane capacity check in Task 6 rather than folding ETD into the
  EDS lane.

## Exchange 2 — operational boundary / robustness threshold

**Question (expert_question_2.md):** If a screening machine fails during the
peak hour, does the backlog build up to delay flights, or do crews absorb it by
another means?

**Reply (summary):** Crews usually absorb a single machine failure without
delaying flights, provided spare capacity exists — a failed EDS's bags are
rerouted to operating machines, which have slack because bags arrive spread over
a window. Backlog builds and flights are delayed only when there is no spare
capacity: the remaining machines are near their throughput limit, the failure
coincides with a concentrated arrival surge, or multiple machines fail at once.

**How the reply shaped the work:**
- Converted directly into the **one-outage robustness rule** in the fleet-sizing
  equation: provision `m` EDSs so the *surviving* `m-1` machines can still clear
  the full peak-hour bag load, i.e. `(m-1)·EDS_rate·EDS_avail·H ≥ bags`. This
  made the recommended fleet `n_eds = max(n_eds_deterministic, n_eds_robust)`.
  For Airport A (R=0.6) this raised the recommendation from 38 to 39 EDSs; for
  B from 40 to 41.
- Gave the validity boundary of the schedule model: the schedule is feasible
  only while spare capacity exists; the model reports per-flight feasibility so
  the boundary is visible, not assumed.

## Exchange 3 — interpretation of "keeps up" / signal vs artifact

**Question (expert_question_3.md):** When screening is reported to keep up on a
busy day, is that judgment based on no delayed departures, or on something else
you can point to?

**Reply (summary):** Not on the absence of delayed departures. "Screening keeps
up" is a judgment about the screening subsystem's own queue: bags clear the
screening point within the time budget (queue drains rather than grows through
the peak), machine utilization stays below capacity leaving slack to absorb a
failure or surge, and any delays that do occur are traced to late-arriving bags
or boarding — not to bags waiting on a machine. Delayed departures still happen
for other reasons, so their presence does not contradict the claim, and their
absence alone would not establish it.

**How the reply shaped the work:**
- Defined the model's validation/interpretation criterion: success is measured
  by (i) the screening queue draining within the peak-hour budget and (ii)
  machine utilization below 100% with slack — **not** by zero delayed
  departures. I report utilization (`util_eds`) and per-flight feasibility as
  the success indicators, and I explicitly state in the limitations that
  departure-delay counts are not a valid screen for screening adequacy.
- Distinguished the screening signal from confounding artifacts (boarding and
  late-bag delays), so the recommendation does not over-claim that the fleet
  eliminates all delays.

## Values taken from the exchanges (no numeric parameters were requested)

None of the exchanges supplied a numerical parameter; all three gave qualitative
operational logic. The model's numeric inputs therefore come entirely from the
task's own dataset and problem statement (see the parameter table in
solution.json), and the checked-baggage fraction `R` — the one value not in the
dataset — is treated as a calibrated operational assumption with interval
[0.45, 1.0] and a sensitivity sweep, not as an expert-supplied figure.
