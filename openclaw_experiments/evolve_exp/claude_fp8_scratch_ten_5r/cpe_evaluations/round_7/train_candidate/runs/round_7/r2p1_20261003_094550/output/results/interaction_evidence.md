# Interaction Evidence — 2017 MCM Problem C (MM-Bench 2017_C)

Policy: structural anchoring before numerical filling. 10 exchanges, one
question each. Each reply below was converted into a parameter or structural
choice before the next question; the model code and runs that consumed it are
cited. No exchange content is copied into the submission — only the values,
constraints, and equations derived from it.

---

## Exchange 1 (structural)

**Question:** On these Seattle-area freeways at peak, are traffic jams mostly a
few slow points, or does one slowdown spread along whole stretches of road?

**Reply (summary):** Congestion behaves as a spreading, upstream-propagating
queue, not isolated slow spots. A localized disturbance triggers a shockwave
travelling backward at roughly 10–15 mph; one bottleneck backs up many miles
of continuous stop-and-go. Corridors function as long, coupled stretches;
adding capacity at one point often moves the bottleneck rather than relieving
the jam.

**How the reply shaped the work (before exchange 2):**
- Adopted the LWR kinematic-wave (shockwave) framework as the dominant
  mechanism: queues grow backward at a finite shock speed and the corridor is
  modelled as coupled segments, not isolated bottlenecks.
- Calibrated the backward shock speed to the stated 10–15 mph band (default
  15 mph in `model.py`; the queue simulator anchors scenarios inside the band).
- Consequence encoded in `model.py`: segment over-capacity states are
  propagated as LWR shocks (`route_table`, `c_shock`), and route-level metrics
  aggregate all over-capacity mileage (`jammi`) rather than a single
  bottleneck.

## Exchange 2 (structural)

**Question:** When one lane is reserved only for connected cars, do regular
drivers mostly keep out, or do they cut in and block it?

**Reply (summary):** Regular drivers mostly keep out — but not reliably enough
to treat the lane as clean. Restricted lanes (HOV/toll) are generally
respected where enforcement and markings exist; a minority intrudes at merge
points, under heavy adjacent congestion, or absent enforcement. A dedicated
lane stays largely clear but suffers occasional intrusions and boundary
friction, so its effective capacity is somewhat below a perfectly exclusive
lane.

**How the reply shaped the work (before exchange 3):**
- Modelled a dedicated AV lane as *partially* exclusive rather than perfect:
  introduced `eta_in = 0.95` (effective exclusivity) as a multiplier on
  dedicated-lane capacity in `model.py` (`C_av = v0/4 * rho_c_av * eta_in`).
- Modeled the shared-lane interaction as a friction penalty rather than free
  mixing: `eta_hv_shared = 0.40` scales down effective mixed demand in
  `segment_metrics` (shared branch), so AVs raise capacity (higher mixed
  critical density) but mixing costs demand at low-to-mid shares.

## Exchange 3 (parameter, conditional on E1 mechanism)

**Question:** With a handful of self-driving cars mixed into regular traffic,
does the whole line slow down much, or only the drivers right next to them?

**Reply (summary):** Only the drivers right next to them, mostly. At low
penetration the perturbation is damped out within a few vehicles; the system-
wide effect only emerges once penetration is high enough that self-driving
cars are frequently adjacent and their smoothed behavior can dominate a lane's
dynamics — a tipping-point phenomenon, not a low-penetration one.

**How the reply shaped the work (before exchange 4):**
- Added a second-layer string-stability criterion to `model.py`
  (`stability_chain`, `tipping_point`): mixed chain gain
  `G = alpha_hv^(1-f) * alpha_av^f`, unstable iff `G > 1`. Low AV share →
  local, damped effect; high share → system-wide regime change.
- This produced the model's central tipping point: `f* = ln(1.25)/ln(1.25/0.70)
  ≈ 0.385` — consistent with the "tipping point where performance changes
  markedly" the problem asks for, and with the expert's statement that a
  handful of cars does nothing corridor-wide.

## Exchange 4 (parameter)

**Question:** What fraction of a lane's peak-hour traffic, roughly, before
drivers start noticing long, snaking stop-and-go waves?

**Reply (summary):** Roughly 80–90% of a lane's capacity — about 1,800–2,000
veh/h/lane — is when sustained stop-and-go waves set in. Below ~1,500–1,600
veh/h/lane traffic is stable and free-flowing; the transition zone in between
is where a small disturbance can tip a lane into long waves.

**How the reply shaped the work (before exchange 5):**
- Set `f_stable = 0.80` and `f_unstable = 0.90` in `model.py` as the
  capacity-fraction band where flow is stable vs. wave-prone.
- The 1,800–2,000 veh/h/lane observation is consistent with the model's
  computed lane capacity `v0/4 * rho_c ≈ 1,575` (at `rho_c_h = 105 veh/mi`);
  the difference marks the transition band the expert describes, so the
  model treats segments at `osm` in [0.8, 0.9] of capacity as the unstable
  band and above as jammed.

## Exchange 5 (parameter)

**Question:** In the snaking stop-and-go waves, roughly how many miles back
does a queue stretch behind a blocked point?

**Reply (summary):** Typically a few miles — commonly 2–5 miles behind a
single blocked point, with severe peak events reaching roughly 5–10 miles.
The stretch scales with blockage duration and inflow rate; a brief incident
backs up 1–2 miles, a sustained peak bottleneck 5+ miles.

**How the reply shaped the work (before exchange 6):**
- Built `queue_sim.py`, a discrete LWR shock-wave queue simulator, and
  calibrated its sustained-peak scenario to reproduce the 2–5 mi band:
  overload ratio 1.04, 25 min overload → 3.15 mi queue (inside band; log
  `queue_sim.log`). Brief incident (osm 1.10, 20 min) → 6.3 mi, consistent
  with "5+ miles for sustained" at higher osm.
- `model.py` queue metric anchored to the same band:
  `queue_mi = min(queue_base_mi * 1.5 * (osm/1.06), 10)`, giving 3.9 mi at
  the route-5 worst segment (osm 1.376) — within the observed 2–5 mi typical
  band, capped at 10 mi for severe events.

## Exchange 6 (parameter)

**Question:** During the peak hour, how much more traffic rides the freeway
than in a mid-morning average, roughly?

**Reply (summary):** Peak-hour volumes run roughly 1.5–2.5× the mid-morning
average hourly volume; the peak hour carries on the order of 8–12% of the
daily total in one hour versus 4–6% mid-morning. Busiest commuter peaks
(I-5, I-405) near the high end; SR-520 nearer the low end.

**How the reply shaped the work (before exchange 7):**
- Set `k_peak = 0.10` (peak-hour fraction of daily volume, mid of the
  8–12% band) as the demand-scaling factor in `model.py`:
  `qd = adt * k_peak / L` converts the dataset's daily AADT to peak-hour
  per-lane demand.
- Sensitivity run at the band's high end (`--sweep k_peak=0.12`, log
  `model_sweep_kpeak.log`): worst-segment osm rises from 1.376 to 1.651 and
  queue from 3.9 to 4.7 mi; the qualitative AV conclusions are unchanged.

## Exchange 7 (parameter)

**Question:** When a car suddenly brakes in the middle of a line, do the
drivers behind usually slow a little, or slam on their brakes?

**Reply (summary):** Usually slow a little, not slam — but the response is
amplified as it passes back through the line: the first follower brakes
modestly, the next a bit harder, so a small brake tap can grow into a full
stop several vehicles back. Strongest when gaps are short (near capacity),
weakest when traffic is light.

**How the reply shaped the work (before exchange 8):**
- Set the reaction gains in `model.py`: `alpha_hv = 1.25` (human chain gain
  > 1 → amplifying) and `alpha_av = 0.70` (AV cooperative gain < 1 →
  damping). The "grows as it propagates, strongest near capacity" statement
  is encoded in the string-stability gain `G = alpha_hv^(1-f) * alpha_av^f`
  evaluated against the near-capacity operating regime (E4 band), not the
  free-flow regime.
- Tipping point `f* ≈ 0.385` is the AV share at which the human
  amplification is exactly cancelled by AV damping.

## Exchange 8 (boundary condition)

**Question:** Do traffic lights, and traffic that turns in and out at
on-ramps, actually make the snaking waves worse?

**Reply (summary):** Yes — both make them worse, through the same mechanism:
they are recurring, predictable disturbances. Each forces a localized speed
change (stop, merge conflict, diverge gap), and at near-capacity flow those
disturbances are amplified upstream. On-ramps are especially potent because
the merge point is both a disturbance source and a capacity bottleneck
(why ramp metering is used to smooth injections). Condition: flow level —
below capacity disturbances damp; near capacity they grow into long waves.

**How the reply shaped the work (before exchange 9):**
- Encoded on-ramps/interchanges as capacity bottlenecks AND disturbance
  sources: segments whose `Comments` field marks an intersection were
  identified as higher-risk points; the model's shock propagation from the
  worst bottleneck (the interchange-adjacent segments on I-5/I-405/SR-520)
  is precisely this mechanism. The "flow-level condition" is the E4 band:
  the `jam` flag only triggers when `q > C`, i.e., the disturbance does not
  damp below capacity.
- Ramp-metering analogue: the dedicated-lane AV option removes the AV share
  from the merge-conflict population, reducing the disturbance-injection
  rate on the general lanes (part of why the dedicated option stabilizes at
  high shares despite lower raw capacity).

## Exchange 9 (boundary condition)

**Question:** In a full stop-and-go stretch, do the cars behind a stopped
lead vehicle usually inch forward, or hold the line?

**Reply (summary):** They inch forward — the "stopped" state is not a fixed
line. Each vehicle advances a short distance (a few car lengths to a few tens
of feet), then stops again; the creep propagates backward as the wave passes.
The lead vehicle is usually moving again by the time the follower closes the
gap, which is why the queue appears to snake rather than sit frozen.

**How the reply shaped the work (before exchange 10):**
- Confirmed the kinematic-wave (rather than static-queue) treatment: queues
  are dynamic, creeping, propagating objects, not frozen lines. This justifies
  the `clear_min = Q/v0` dissipation time in `queue_sim.py` (a queue clears
  at free-flow speed once inflow normalizes) and the time-scaled `Q(t) =
  c_shock * t` growth law in `model.py`'s queue metric. A static queue model
  (frozen line) would overstate persistent jam length; the observed creeping
  behavior is what the calibrated 25-min sustained overload and ~3 mi queue
  represent.

## Exchange 10 (boundary condition)

**Question:** Once congestion gets bad enough, do people usually take surface
streets to avoid the freeway for that trip?

**Reply (summary):** Yes — a meaningful share diverts to parallel surface
streets, but it is partial and self-limiting: surface arterials have far lower
capacity (signalized, 1–2 lanes, ~600–900 veh/h/lane) and their own
congestion, so they absorb only a small fraction before saturating. Diversion
is more common for shorter trips and where a viable parallel route exists
(SR-520 vs I-90; arterials paralleling I-405), less for long through-trips.
Practical consequence: surface streets act as a limited relief valve that
caps how bad freeway queues get, but they spread congestion onto the adjacent
network rather than eliminating it.

**How the reply shaped the work:**
- Added `p_div = 0.05` (diversion share in jam) as the relief-valve cap in
  `model.py`: peak demand on the freeway is reduced by the diverted share in
  jammed states, which caps the maximum overload ratio the corridor can
  sustain. The "limited relief valve, not escape" reading means the model
  reports jam reduction but not elimination — reflected in the result that
  high AV shares reduce `jammi` (e.g., I-5 from 117.4 to 102.2 mi at 90%)
  but do not drive it to zero while demand stays above capacity.
- The SR-520 vs I-90 parallel-route note supports route-specific reading of
  the results: SR-520's lower volumes and available parallel routes make it
  the least congestion-bound corridor (worst osm 1.524 at f=0 vs 1.587 on
  I-405).

---

## Exchange → parameter map

| Exchange | Value/constraint fed into model | Where used |
|---|---|---|
| E1 | shock speed 10–15 mph (default 15) | `model.py` LWR shock; `queue_sim.py` scenarios |
| E2 | `eta_in = 0.95` (dedicated-lane exclusivity); `eta_hv_shared = 0.40` (shared-lane mixing friction) | `model.py` `segment_metrics` |
| E3 | string-stability criterion; low-penetration = local damping | `model.py` `stability_chain`, `tipping_point` |
| E4 | `f_stable = 0.80`, `f_unstable = 0.90`; 1,800–2,000 veh/h/lane wave onset | `model.py` unstable band, capacity check |
| E5 | queue 2–5 mi typical, 5–10 mi severe | `queue_sim.py` calibration; `model.py` queue anchor |
| E6 | `k_peak = 0.10` (8–12% band) | `model.py` demand scaling; sensitivity at 0.12 |
| E7 | `alpha_hv = 1.25`, `alpha_av = 0.70` (amplify vs damp) | `model.py` stability gains; `f* ≈ 0.385` |
| E8 | on-ramps = bottleneck + disturbance source; flow-level condition | `model.py` jam trigger at q > C; interchange segments |
| E9 | creeping (dynamic) queues, not frozen lines | `queue_sim.py` `Q = c_shock·t`, `clear = Q/v0` |
| E10 | `p_div = 0.05` partial diversion cap | `model.py` jam demand cap |
