# Expert Interaction Evidence — Problem 2017_C

All 10 exchanges completed; questions in `logs/operator_feedback/expert_question_N.md`,
replies in `expert_reply_N.json`. Values below were integrated into `code/model.py`
and its parameter table in `results/solution.json`.

## Exch. 1 — Breakdown threshold
Q: Do stop-and-go breakdowns start below full daily capacity?
A: Yes — breakdown is governed by peak-hour flow at a bottleneck reaching ~80–90% of
that bottleneck's capacity; the congested branch is a *stable* equilibrium once entered.
**Used as:** `theta = 0.85`, interval [0.8, 0.9]; the FREE/SAG bimodal state rule and
the hysteresis (persistent SAG) in the model; sensitivity run over [0.8, 0.9].

## Exch. 2 — Platoon capacity ceiling
Q: How much more throughput from tight platoons vs ordinary cars?
A: Theoretical ceiling ~1.5–2×; realistic mixed-traffic gain 30–70% (midpoint ~0.5×).
**Used as:** `gain_max = 1.7`, interval [1.5, 2.0]; `gain_mid = 0.5`, interval [0.3, 0.7];
sensitivity over both bounds (VFC at f=0.5 moves ~±4%).

## Exch. 3 — Penetration scaling, no tipping cliff
Q: Fraction at which capacity gain suddenly stops growing?
A: No cliff; gain scales with the *square* of the cooperative fraction; saturates as
f→1; steepest below ~30–40%, near ceiling by 70–90%.
**Used as:** gain law `g(f) = (gain_max−1)·gain_mid·f²`; the answer to the problem's
"tipping point" question (smooth saturation, kink only where SAG segments clear theta).

## Exch. 4 — Peak-hour share of daily traffic
Q: Fraction of a day's cars in the single busiest hour?
A: ~8–12% (K-factor), commonly 9–10% on urban freeways.
**Used as:** `kfact = 0.10`, interval [0.08, 0.12]; sensitivity over full range
(pct_SAG on I-5 at f=0 moves 86% → 54–90%).

## Exch. 5 — Free-flow lane capacity
Q: Vehicles/hour one freeway lane carries near capacity?
A: ~2,000 ideal; 1,800–1,900 realistic sustained.
**Used as:** `c_lane = 2000`, interval [1800, 2000].

## Exch. 6 — Dedicated lanes and safety
Q: Do self-driving cars need a dedicated lane for safety?
A: No — safety rationale for dedication is *segregation* to capture the platooning
gain, not lane-keeping itself.
**Used as:** policy conclusion — dedicated lanes justified only where platooning gain
can be banked (high-demand peak corridors), not on safety grounds; modelled as the
"dedicated-lane" scenario in the policy section.

## Exch. 7 — Heavy-vehicle share
Q: Truck/large-vehicle share on these freeways?
A: 5–8% on urban segments; 1 heavy vehicle ≈ 1.5–3 passenger-car equivalents.
**Used as:** `p_heavy = 0.06`, interval [0.05, 0.08]; `p_hf = 2.0`, interval [1.5, 3.0];
enter as `C_H = C_LANE/(1 + p_heavy·(p_hf−1))`.

## Exch. 8 — Free-flow speed
Q: Typical free-flow speed on these freeways?
A: ~60 mph interstates, ~55 mph SR-520/constrained segments.
**Used as:** `speed` column: IS=60, SR=55; drives travel-time estimates in results.

## Exch. 9 — Breakdown-flow throughput
Q: Throughput per lane during stop-and-go?
A: Drops to ~1,400–1,700 veh/h/lane vs ~1,800–2,000 free flow.
**Used as:** `c_bkd = 1500`, interval [1400, 1700]; SAG segments carry C_BKD instead
of C_L in the effective-capacity accounting.

## Exch. 10 — Breakdown frequency/directionality
Q: How often does stop-and-go appear on these freeways?
A: Near-daily on peak-direction commute segments in rush hour; congestion directional
and time-bounded (~6–9 am / 3–7 pm windows).
**Used as:** validates treating peak-hour demand as the sizing quantity and explains
why the SAG state, once entered, persists through the ~4 h peak window; basis for the
travel-time loss estimate in results.
