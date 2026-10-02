# Interaction Evidence — MCM 2017-C (Self-Driving Cars on Seattle Freeways)

Three expert exchanges, one question each, sequenced to resolve the highest-impact
modeling uncertainties. The expert is a domain practitioner, not a modeler; every
question was answerable by common sense about real freeways.

---

## Exchange 1 — Core mechanism

**Question (as asked):**
> When self-driving cars that coordinate with each other share a highway with
> regular drivers, what is the single biggest reason they let the whole road
> carry more cars?

**Expert reply (paraphrased for the record; not copied into the submission):**
The dominant reason is that coordinated self-driving cars run at much shorter
following distances (headways) than human drivers, because vehicle-to-vehicle
coordination removes the human reaction-time and perception limits that force
large safety gaps. Shorter headways mean more vehicles pass a point per hour at
the same speed, so the same lanes carry more traffic.

**How the reply became work:**
This fixed the causal mechanism of the model. Effective per-lane capacity was
made an explicit function of the self-driving share *p* through a headway blend:
the all-human time headway τ_h = 3 s is replaced, as *p* grows, by the shorter AV
headway τ_av = 1 s (with a small platoon bonus φ = 0.25 for cooperating AVs).
Capacity C(p) is inversely proportional to the blended headway, normalized so
C(0) = C_h. This is the entire "cooperation" and "interaction" mechanism the
problem asks for, and it is implemented in `code/model.py::c_lane`.

---

## Exchange 2 — Boundary / operational constraint

**Question (as asked, building on Exchange 1):**
> On a typical busy Seattle freeway, how many cars per hour does one lane
> actually carry in free-flowing traffic?

**Expert reply (paraphrased):**
Roughly 1,800–2,200 vehicles per hour per lane in free-flow conditions; about
2,000 is the standard planning figure. The expert flagged this as an empirical
rule of thumb, not a precise value, varying with speed and driver mix.

**How the reply became work:**
This set the absolute scale of the capacity axis. The model's all-human per-lane
free-flow capacity was set to **C_h = 2000 veh/h/lane**, with the expert's
1,800–2,200 range used as the sensitivity band (swept at 1,800 and 2,200). This
anchors the volume-to-capacity ratio (VCR) and therefore the entire congestion
and travel-time computation. Recorded as an exchange-sourced parameter in the
submission parameter table.

---

## Exchange 3 — Interpretation / success criterion

**Question (as asked, building on Exchange 2):**
> When would you tell a state DOT that adding a self-driving car fleet has
> clearly made the commute meaningfully better for ordinary drivers?

**Expert reply (paraphrased):**
When the ordinary (non-self-driving) driver's own peak travel time drops
noticeably — a sustained reduction of roughly 10–20% or more on the affected
corridors — and this holds at realistic adoption, not a best case. In practice
that means the self-driving share is high enough (well past the low end, likely
30–50%+) that shorter headways raise effective capacity enough to absorb the peak
volume, *and* the benefit is not eaten by induced demand or by dedicated-lane
rules that take capacity away from regular drivers. If ordinary drivers see no
measurable change or a worsening, the fleet has not clearly helped them.

**How the reply became work:**
This set the decision threshold and the policy test:
- The **10–20% peak travel-time reduction** is used as the "meaningfully better"
  bar. The model reports dT at each *p* and flags where it crosses −10%.
- The "well past the low end, likely 30–50%+" guidance is compared against the
  model's tipping point (the *p* where the −10% bar is first crossed).
- The "dedicated-lane rules that take capacity away from regular drivers"
  caveat is modeled directly as a scenario: 25% of lanes dedicated to AVs only,
  with the regular-driver capacity computed on the remaining lanes. The result
  (VCR ~1.7, large travel-time increase) is the quantitative answer to "should
  lanes be dedicated": not on these corridors at these adoption levels.
- "Sustained, not a best case" motivates the parameter sensitivity sweep (11
  overrides) showing the conclusions hold across the expert's stated ranges, not
  just at one point estimate.

---

## Provenance of expert-derived numbers

| Parameter | Value | Interval | Source |
|---|---|---|---|
| Per-lane free-flow capacity C_h | 2000 veh/h | [1800, 2200] | Exchange 2 (expert, empirical rule of thumb) |
| AV headway τ_av vs human τ_h | 1 s vs 3 s | τ_av ∈ [0.6, 1.4] swept | Exchange 1 mechanism; τ_h 2–3 s standard; swept 0.6–1.4 s |
| Platoon bonus φ | 0.25 | [0, 0.5] swept | Exchange 1 (cooperation); swept 0.5 |
| "Meaningfully better" bar | 10–20% peak dT | [10, 20]% | Exchange 3 |
| Realistic high adoption | 30–50%+ | — | Exchange 3 |
| Dedicated-lane test | 25% of lanes AV-only | [25, 34]% swept | Exchange 3 caveat; swept 34% |

All other empirical inputs (peak-hour factor 0.9, 4%-of-AADT peak-hour,
45% peak-20-min, free-flow speed 65 mph, BPR α=0.15, β=4.0) are standard
US-Highway-Capacity-Manual planning values cited by full reference in the
submission; they were not retrievable from the web in this environment (only
scholarly DOIs were reachable), so they are declared as standard planning
constants with their conventional ranges.
