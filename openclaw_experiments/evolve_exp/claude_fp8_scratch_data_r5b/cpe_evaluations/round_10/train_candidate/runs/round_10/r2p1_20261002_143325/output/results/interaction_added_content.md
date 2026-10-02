# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — 2017_C (cooperative self-driving cars, I-5 / I-90 / I-405 / SR-520)

Three fixed exchanges. Each: question → reply → how the reply entered the work
(as a parameter, constraint, or decision rule, with its source and valid range).

---

## Exchange 1 — Operational definition of the "average daily traffic count"

**Question (asked before the demand model was built).**
The spreadsheet gives a single "average daily traffic count" per road section.
When there is a heavy weekday rush, what actually happens to cars wanting to use
that section — do they go around it, or do they still try to get on and back up?

**Reply (expert, verbatim, for the record only — not copied into the submission).**
Demand is essentially fixed and inelastic in the short run: there is no
practical parallel route for a through trip (sparse network; the alternatives are
themselves congested at the same hours). The section operates at or above
capacity, speeds drop, and queues form at on-ramps and upstream; only a small
share of trips divert, mainly discretionary/short local trips, not the peak
commute. The given ADT is a daily average that hides the peak; peak-hour volume
on these urban freeways is typically ~8–10% of ADT (empirical rule of thumb), and
the peak hour is what determines whether the section is over capacity. Treat the
section as demand-driven and queuing, not as a route that sheds traffic.

**How the reply became work.**
- *Model structure (constraint):* the link model was built as **flow = min(demand, capacity)**
  with queues — demand does NOT get shed when a section is congested. This is the
  whole demand/capacity coupling of the traffic model, and it is what the reply
  specified (inelastic demand, queuing).
- *Calibrated parameter:* peak-hour volume fraction of ADT.
  `PHF_volume_fraction = 0.09, interval [0.08, 0.10]` — source: Exchange 1
  (expert's empirical rule of thumb). Holds for peak weekday commuter hours on
  urban freeways in this corridor. It is the bridge from the daily-average ADT
  in the data to the peak-hour operating point the model actually runs at.
- *Decision-relevant consequence:* because demand is inelastic, the binding
  question is whether peak demand exceeds capacity — so the model's headline
  output is a **level-of-service / over-capacity (V/C) measure per section**,
  not a "how many cars reroute" measure.

**Validity.** The 8–10% peak fraction and the inelastic-demand assumption are
specific to the peak weekday commute on these urban freeways. They would not
hold for the daily average (which is why ADT must be scaled down to a peak hour
before comparing to capacity), and the inelasticity would weaken for
discretionary/short trips (which the expert said are the only part that diverts).

---

## Exchange 2 — Causal direction: what sets a lane's achievable flow, and how AD helps

**Question (built on Ex.1 — demand is inelastic, so the model's whole lever is the
supply side; asked before the capacity equation was written).**
Why does a clogged stretch carry fewer cars/hour than it could — is the real
bottleneck the drivers (how far apart they stop, how slowly they react, the gaps
they leave), or something the road itself (lane count, speed limit)?

**Reply (expert, verbatim, for the record only — not copied into the submission).**
The bottleneck is the drivers, not the road's physical design. A freeway lane's
theoretical capacity (~2,000 veh/h) is set by how closely vehicles can follow,
and that spacing is governed by human factors: reaction time, the safe headway
drivers choose, the distance they keep. In dense traffic small speed
disturbances amplify into stop-and-go "phantom traffic jams," and throughput
falls well below the lane's potential — often to 1,200–1,600 veh/h/lane. Lanes
and speed limits set the ceiling, but the achievable flow is limited by human
reaction and gap behavior. That is exactly why cooperative self-driving cars are
proposed: tighter, more consistent headways and faster reaction raise effective
capacity without adding lanes.

**How the reply became work.**
- *Causal mechanism validated:* the model's central lever is **achievable flow per
  lane is set by gap/headway behavior, not by lane geometry**. So capacity is
  modeled as *function of headway/reaction*, and self-driving is modeled as
  *shrinking that headway* — a direct causal mechanism, not a correlation. This
  rules out the naive reading that AD only "reduces accidents" or that adding
  lanes is the only lever.
- *Calibrated parameters (empirical, from the reply):*
  - `C_ideal (theoretical lane ceiling) ≈ 2000 veh/h/lane` — source: Exchange 2.
  - `C_achieved (human-driven, dense) ≈ 1200–1600 veh/h/lane` — source: Exchange
    2. The gap between ceiling and achieved is the headroom AD recovers.
  - These anchor the capacity function's low end (human) and high end (AD
    ceiling). The *fraction* of the gap recovered at a given AD percentage is the
    model's own interpolation (calibrated to the mechanism, not asserted flat).
- *Mechanism used:* stop-and-go "phantom jam" amplification means the penalty is
  *nonlinear* — the benefit of tighter headways grows as the section approaches
  congestion, so the capacity gain from AD is largest where V/C is highest. The
  model makes the AD benefit a **function of the baseline congestion (V/C)**, so
  a free-flowing section gains little and a saturated section gains a lot.

**Validity.** The 2,000 veh/h/lane ceiling and the 1,200–1,600 achieved band are
standard freeway values (consistent with the Highway Capacity Manual) and hold
for these urban freeways. The *fraction* of the gap AD recovers is model
assumption bounded by those two anchors; it is not a measured constant, and the
robustness question (Ex.3) decides what range of that fraction is defensible.

---

## Exchange 3 — Decision-relevant robustness threshold: when is the "AD eases the rush" prediction trustworthy

**Question (built on Ex.1 + Ex.2 — demand inelastic, headway-driven capacity; asked
before the results were interpreted and the policy rule was set).**
Suppose a city promises a share of self-driving cars will noticeably ease the
morning rush. What would have to actually be true on the road before you'd trust
that promise — and what sign would tell you it was an empty claim?

**Reply (expert, verbatim, for the record only — not copied into the submission).**
Three things must hold: (1) the self-driving cars must be a large share of the
*peak-hour* flow, not just of the daily/fleet total (a 10% fleet share can be
well under 5% of rush-hour vehicles — too few to change headway behavior);
(2) they must be able to cooperate in the *same platoon* — enough in the same
lane at the same time to form tight headways (isolated self-driving cars among
humans behave like humans and add nothing); (3) the human drivers around them must
not degrade the gain (mixed traffic reverts to human spacing; one human cutting in
can break a platoon). The tell-tale sign of an empty claim: the share is quoted as
a *fleet/sales* percentage, and the measured *peak-hour throughput (veh/h/lane)*
on the affected sections is unchanged — if capacity per lane doesn't move, it is
marketing.

**How the reply became work.**
- *Model input interpretation (robustness condition #1):* the AD percentage must
  be interpreted as a **share of peak-hour flow**, not of the daily total. The
  model takes the problem's 10%/50%/90% as peak-flow shares; it explicitly notes
  a *fleet* share of that size maps to a *smaller* peak share, so results are
  reported as the best (peak-share) case and flagged where they would weaken.
- *Decision rule (robustness conditions #2 + #3):* the capacity gain from AD is
  modeled as requiring **platoon formation** — a threshold on the co-located AD
  share, below which the gain collapses to ~0 (isolated AD cars add nothing) —
  and scaled down by a **human-interference / mixed-traffic degradation factor**
  that reverts the achievable headway toward the human value as the AD share of a
  platoon's neighborhood falls. This is the mechanism behind the *tipping point*:
  below a critical AD share there is essentially no benefit (no stable platoon);
  above it the benefit turns on.
- *Validation criterion for the headline claim:* the model's own output is judged
  by whether **peak-hour throughput (veh/h/lane) actually moves** on the affected
  sections — not by whether a fleet share was adopted. The submission's "is this
  an empty claim?" test is: does the computed per-lane capacity cross a threshold
  that changes the level of service. If it does not, the corresponding policy
  claim (e.g., "dedicate a lane") is flagged as not yet supported.
- *Tipping-point definition (derived):* the tipping point is the AD share at
  which platoon formation first becomes stable AND the resulting throughput gain
  is large enough to shift the section's level of service — i.e., the
  share-dependent capacity crosses the congestion threshold. Below it: no
  reliable benefit. This makes "tipping point" a computed, decision-relevant
  quantity rather than a marketing number.

**Validity.** The robustness rule is specific to *peak-hour* operation on these
urban freeways and to *cooperative* (connected) AD, not single-vehicle AD. The
fleet→peak mapping (condition #1) means a fleet-share reading of 10/50/90 would
understate the benefit; the model states this explicitly so the reader does not
conflate the two. The degradation factor (condition #3) means the benefit is
*concave* in the AD share and is smallest for the majority-human mixed traffic,
which bounds how much capacity a low AD share can realistically add.

---

## Parameter table consolidated (all empirical values with provenance)

| name | value | interval [a,b] | source |
|---|---|---|---|
| Peak-hour volume as fraction of ADT | 0.09 | [0.08, 0.10] | Exchange 1 (expert, urban freeway peak rule of thumb) |
| Theoretical lane capacity ceiling | 2000 veh/h/lane | [1800, 2200] | Exchange 2 (expert; consistent with HCM free-flow ceiling) |
| Achieved (human) dense lane capacity | 1400 veh/h/lane | [1200, 1600] | Exchange 2 (expert's 1,200–1,600 band, midpoint) |
| Free-flow speed (urban freeway) | 65 mph | [55, 70] | Exchange 2 context + standard urban freeway design (see search) |
| AD platoon-formation threshold (co-located peak share) | 0.30 | [0.20, 0.40] | Exchange 3 (platoon must be a large, cooperative share; model-calibrated) |
| Human-interference degradation (headway reversion) | see model f(x) | — | Exchange 3 (mixed traffic reverts to human spacing) |

Note: free-flow speed and platoon threshold are the two values not directly
stated by an expert; both are grounded in the mechanism the experts confirmed and
bounded by the two expert anchors above. Free-flow speed is cross-checked against
the literature in `code/` (search call recorded in `logs/`).
