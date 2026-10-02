# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — Problem 2017_C

Three exchanges, one question each. Each reply was converted into a model input
or decision rule before the next exchange was asked.

## Exchange 1 — Operational input structure

**Question:** During peak hours, do vehicles on these highways arrive in a fairly
even stream, or in noticeable bursts of cars?

**Expert reply (summary):** Peak-hour traffic is not a steady even stream. It
arrives in bursts and waves — platoons form behind slower or merging traffic,
and flow fluctuates on time scales of seconds to minutes. This stop-and-go /
platooning burstiness is strongest precisely when volume approaches capacity,
i.e. at peak. Coarser variation (ramp-up, plateau, decline) also exists over the
peak period.

**How the reply affected the work:**
- Parameter added: **peak-hour burstiness / platooning factor** `beta`. Inflow
  is modeled as nonuniform; short-time-scale platooning is treated as a capacity
  derating that is largest as the volume-to-capacity ratio rho approaches 1.
  This is used in the mixed-flow (AV + human) capacity reduction term so that a
  higher human fraction => more platooning => more derating.
- The model uses a **peak hour** (15-min peak volume) rather than the daily
  average as the decision-relevant input; the daily counts are scaled by a
  peak-factor `f_peak` to obtain the peak volume that drives the capacity
  constraint.

## Exchange 2 — Dominant driver of the AV benefit

**Question:** When self-driving cars coordinate, does the main capacity gain
come from smoother, steadier flow, or from letting them travel faster?

**Expert reply (summary):** The main gain is smoother, steadier flow — reduced
spacing (headway) between vehicles and damped stop-and-go waves — not higher
speed. The benefit is fundamentally a density/headway effect, not a speed
effect. Running faster is secondary and self-limiting: free-flow speed is capped
by geometry/speed-limit/safety, and raising speed actually reduces achievable
density. So the payoff appears as increased throughput and reduced delay, not
shorter free-flow travel times.

**How the reply affected the work:**
- Parameter added: **headway reduction factor** `h` (fractional reduction in the
  minimum space-headway for the AV share). The AV benefit enters the model as a
  **capacity (throughput) increase** at roughly constant free-flow speed, not as
  a speed increase.
- The model's AV effect is therefore written as: effective capacity
  `c_eff = c_base * (1 + h * p_av * cooperation)` where `p_av` is the AV share
  and `cooperation` ∈ [0,1] scales how much of the theoretical headway
  tightening is realized. Speed `v_ff` is held at the free-flow value; the gain
  is a density effect on the capacity plateau, exactly as the expert described.
- Because the benefit is a density effect that is strongest near capacity, the
  throughput gain concentrates where rho is high — consistent with the
  burstiness/platooning derating of Exchange 1 (they offset each other at high
  rho for a low AV share, and the AV headway gain dominates for a high AV share).

## Exchange 3 — Decision-relevant threshold for a dedicated lane

**Question:** For adding a dedicated self-driving lane, roughly what change in
delay makes it worth it?

**Expert reply (summary):** A dedicated lane is worth it only if the throughput/
delay gain to the remaining general-purpose traffic is large enough to offset the
capacity removed. Empirical planning rule: dedicating a lane removes roughly
20–33% of the capacity of a 3–5 lane road, so the self-driving lane must carry
enough vehicles to more than compensate — typically the gain must be on the order
of 10–20% or more in total corridor throughput (or equivalent delay reduction)
before it clearly pays off. Below roughly 10%, the loss of a general-purpose
lane usually cancels the benefit. This is a judgment range, not a precise figure;
the exact threshold depends on the AV share and how much headway tightening is
actually achieved.

**How the reply affected the work:**
- Parameters added:
  - **dedicated-lane capacity loss** `L_lane ≈ 1/l` (fraction of total capacity
    removed by converting one lane), l = lanes per direction, taken in [20%,33%].
  - **decision threshold** `T_thr ≈ 10%` (minimum total-corridor throughput gain
    required for a dedicated lane to be justified). The model computes, for each
    corridor and AV share, the net throughput change from dedicating a lane and
    compares it to `T_thr`; only when net gain > T_thr is the dedicated lane
    recommended.
- Decision rule added: `recommend dedicated lane` iff
  `throughput_gain_total - L_lane * baseline > T_thr`. This is applied per
  corridor in the results.
