# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence

## Exchange 1: Data-Model Structural Fit

**Question:** When the peak-hour flights depart, do their checked bags reach screening all at once or in separate waves?

**Expert Reply:** In separate waves. Checked bags reach screening in flight-tied batches — passengers check in over a window ahead of each departure, so each flight's bags arrive as a lump concentrated in the hour or two before its boarding time, not spread uniformly across the peak hour. Flights departing in the same peak hour therefore produce overlapping waves, and screening must be sized for the coincident peak (sum of simultaneous flight-level flows), not the hour-average.

**How the reply affected the work:**
- **Parameter/Constraint:** The model must size the EDS/ETD fleet to the **coincident peak** of simultaneous flight-level bag flows, not the hour-average. This is a hard structural constraint on the model's throughput calculation.
- **Equation change:** The peak bag flow is computed as `F_a = B_a' / 0.5` (bags per hour), where `B_a'` is the total adjusted bag count and `0.5` is the peak window fraction (30 minutes, worst-case assumption). This reflects the expert's finding that bags arrive in a narrow window, not uniformly across the hour.
- **Source:** Exchange 1.
- **Interval:** The peak window fraction (0.5) is a worst-case assumption; if the actual window is longer (e.g., 0.75), the required EDS count decreases proportionally.

## Exchange 2: Dominant Bias or Selection Mechanism

**Question:** When a flight is cancelled or delayed, does its bag flow simply disappear, or does it spread out over a longer time window?

**Expert Reply:** Both happen, and they are different mechanisms:
- **Cancelled flight:** its bags largely disappear from the peak-hour flow. Passengers are rebooked onto later flights, so their bags shift to a later window (or a later day) rather than arriving in the original peak hour. Net effect on the peak hour: multiplicative thinning.
- **Delayed flight:** its bags do not disappear; they spread out. The flight's bag stream is pushed later and smeared over a longer window, so some of its bags fall outside the original peak hour and the remainder arrives over an extended interval.

So the dominant effect on the peak-hour flow is reduction — cancellations remove bags outright, and delays push part of the flow out of the window. The scheduled table therefore over-states the realized coincident peak, and sizing to the full scheduled flow is a conservative (oversizing) bias.

**How the reply affected the work:**
- **Parameter/Constraint:** The model must adjust the scheduled bag count for disruptions (cancellations and delays) before computing the peak flow. The adjustment is multiplicative: `B_a' = B_a * (1 - cancellation_rate) * (1 - delay_spread_fraction)`.
- **Equation change:** The disruption adjustment is applied to the scheduled bag count before computing the peak flow. The cancellation rate is 2% (given in the problem statement), and the delay spread fraction is 10% (conservative estimate).
- **Source:** Exchange 2.
- **Interval:** The delay spread fraction (10%) is a conservative estimate; if the actual fraction is lower (e.g., 5%), the model oversizes the fleet by ~5%.

## Exchange 3: Validation or Interpretation Criterion

**Question:** When an airport has just enough screening machines to handle a normal peak hour, what makes you decide to buy one more machine?

**Expert Reply:** The trigger is reliability margin, not average throughput. You buy one more machine when the existing fleet has no spare capacity to absorb the two things that actually happen: a machine going down (each EDS is only operational ~92% of the time, so with N machines you routinely lose one) and a day when the peak runs above plan. If the fleet is sized so that every machine must run at full rate for the whole peak hour with zero downtime, that is not "just enough" — it is a single point of failure, and the operational signal is that a single breakdown or a modest surge forces either a queue that breaches the 100% screening mandate or unacceptable passenger delay.

So the decision rule is: buy the extra machine when the fleet cannot clear the peak flow with one machine out of service and still keep queues within the airport's tolerance. The margin is one unit of redundancy, not a percentage buffer.

**How the reply affected the work:**
- **Parameter/Constraint:** The model must add a reliability margin of **one extra EDS and one extra ETD** to the base required count. This is a hard decision rule, not a percentage buffer.
- **Equation change:** The total required device count is `base_required + 1`, where `base_required = ceil(peak_flow / effective_throughput)`. The `+1` is the reliability margin.
- **Source:** Exchange 3.
- **Interval:** The reliability margin is one unit of redundancy, which is appropriate for a security mandate where under-screening is unacceptable. If the airport's tolerance for delay is higher (e.g., the airport can absorb a 15-minute queue), the margin could be reduced to zero, but this is not recommended.
