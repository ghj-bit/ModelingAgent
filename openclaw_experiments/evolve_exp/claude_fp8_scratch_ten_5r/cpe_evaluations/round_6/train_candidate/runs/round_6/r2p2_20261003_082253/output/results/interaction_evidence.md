# Interaction Evidence — 2017_C (MM-Bench)

Ten expert exchanges, one question each. All question/reply pairs are on disk
under `logs/operator_feedback/` (expert_question_N.md / expert_reply_N.json).
The reply is input, not content: each is listed below with the concrete model
parameter, rule, or scenario it drove, plus where in the code/results it is used.

## Exchange 1 — platoon headway magnitude
- Q: On a Seattle highway, do cooperating self-driving cars in a line drive much
  closer together than ordinary cars, or about the same?
- Reply (key values): ordinary drivers ≈ 1.5–2 s headway; cooperating platoons
  ≈ 0.3–0.7 s (tightest 0.1–0.3 s); a platoon carries 2–4× vehicles per lane.
- **Used in work**: set model parameters `t_lead = 1.75 s` (range 1.5–2.0) and
  `t_plat = 0.5 s` (range 0.3–0.7) in `code/platoon_model.py`; the 2–4× platoon
  factor is the target the model must reproduce (it does: C(0.9)/C(0) ≈ 2.3×).
  Interval of validity: highway free-flow, string-stable platoons.

## Exchange 2 — who sets the gap
- Q: Does a car behind an ordinary driver hold the tight automatic spacing?
- Reply: No — the leader binds. Behind a non-cooperating car, even a full
  automatic falls back to ordinary ≈1.5–2 s headway. Tight spacing needs
  **both** vehicles cooperating.
- **Used in work**: structural rule of the model — a platoon is a maximal run of
  cooperating CAVs; each run carries one human entry gap `t_lead` plus
  (L−1)·`t_plat` internal gaps. Mean CAV run length L = p/(1−p) from geometric
  mixing. This is the core of `cap_lane(p)` in `code/platoon_model.py`.
  Consequence: at low p the capacity gain is nearly zero (verified: p=0.1 gives
  +6%, p=0.3 +13% lane capacity).

## Exchange 3 — lane-change expectation
- Q: If an autonomous car's lane runs out of room, do passengers expect lane
  changes?
- Reply: Yes — lane change is the default expectation, conditional on a safe
  gap; waiting is acceptable only when no safe gap exists, but passively holding
  a dying lane is not.
- **Used in work**: motivates the dedicated-lane scenario design — CAVs in a
  dedicated lane must be able to merge out before it ends, so the model assigns
  CAV demand to the dedicated lane only up to its capacity and routes overflow
  to the remaining (mixed) lanes; an equilibrium is declared only when **both**
  the dedicated and the remaining lanes are under their capacity simultaneously.
  This appears in the `dedicated` scenario block of `code/platoon_model.py`
  (the `eq` condition on both `v_ded` and `v_rem`).

## Exchange 4 — gap availability for merging
- Q: Do fast-lane drivers leave large empty gaps for merging traffic?
- Reply: No — gaps in dense freeway traffic are only ~1–2 car lengths beyond
  minimum; merges depend on the entering driver finding/forcing a gap
  (ramp metering, zipper merges), not on courtesy.
- **Used in work**: justifies treating dedicated-lane CAVs as capacity-limited
  and forbidding the model from assuming dedicated-lane capacity transfers to
  mixed lanes when CAV demand is low (no "courtesy spillover"); also supports
  the random-mixing (geometric run) assumption rather than an ordered/alternating
  one, which would overstate gains at low p. Used in `cap_lane` and the
  dedicated scenario of `code/platoon_model.py`.

## Exchange 5 — speed vs throughput
- Q: How much faster do platoons travel than ordinary drivers in free flow?
- Reply: Essentially not faster at all — speed is set by the speed limit and
  traffic ahead; platooning buys capacity (vehicles/hour), not velocity. Any
  speed gain is a small indirect 0–5 mph from smoother control.
- **Used in work**: model fixes free-flow speed at `V_FREE = 65 mph` for all p
  and applies the headway gain only to throughput (`C(p) = 3600 / t_mean(p)`);
  the 0–5 mph smoothing effect is inside the error bar of the parameter
  intervals, so it is noted in limitations rather than added as a term.
  Used in `code/platoon_model.py` (`V_FREE`, `cap_lane`, `greenshields_v`).

## Exchange 6 — the underused lane on SR 520
- Q: When traffic backs up on the SR 520 bridge, which lane do drivers complain
  about most?
- Reply: The HOV/carpool lane — it sits largely empty while general lanes jam;
  it is the natural candidate to convert to a self-driving-only lane.
- **Used in work**: shapes the policy question — the dedicated-lane scenario is
  evaluated as a conversion of the underused lane (k = 1 of 2 on SR 520), and
  the result section answers "under what conditions should lanes be dedicated"
  with the equilibrium conditions for each route. Drives the SR 520 row of
  `results/platoon_results.json` and the dedicated-lane discussion in
  `solution.json`.

## Exchange 7 — lane changes make jams worse
- Q: In stop-and-crawl, do driver lane changes make jams better or worse?
- Reply: Worse — each lane change forces a brake that propagates backward as a
  shockwave; the effect is strongest near capacity where gaps are small.
- **Used in work**: supports (a) the Greenshields speed–flow curve being applied
  per-lane rather than allowing cross-lane relief, and (b) the "equilibrium
  exists only below capacity" result — near-capacity operation degrades rather
  than self-corrects. Also grounds the model's bias note that results are
  conservative for corridors with many merges. Used in `greenshields_v` and the
  limitations text of `solution.json`.

## Exchange 8 — dedicated-lane compliance
- Q: Would ordinary drivers mostly stay away from a self-driving-only lane?
- Reply: Yes — legally barred, not by choice; leakage is opportunistic solo
  drivers under weak enforcement / heavy congestion, worse at peak; peak-only
  restrictions leak off-peak.
- **Used in work**: the dedicated-lane scenario assumes 100% CAV in the
  dedicated lane (compliance ≈1), and the limitations text carries the
  violation leakage as a known bias; the model is run for peak-hour conditions
  (where leakage is highest in practice), making the dedicated-lane results a
  conservative upper bound on real-world gains. Used in the dedicated block of
  `code/platoon_model.py` and the limitations field of `solution.json`.

## Exchange 9 — perceived congestion
- Q: Does a slow steady crawl feel worse than a stop that then lets you move?
- Reply: A steady crawl feels worse than stop-and-go that actually moves —
  perceived progress, not mean speed, drives annoyance; a long dead stop is
  worst of all.
- **Used in work**: motivates using travel time (mean speed) **and** the
  equilibrium flag as the reported metrics, rather than flow alone — a
  route that "carries the volume" but crawls near jam density is reported as
  non-equilibrium. The ≥25% capacity-gain tipping-point threshold is chosen so
  that the reported travel-time drops correspond to visible progress gains.
  Used in the metric selection of `code/platoon_model.py` (tt_min, equilibrium,
  tipping_point_p).

## Exchange 10 — platoon lifetime
- Q: How long does a platoon keep tight spacing before a human breaks in?
- Reply: Seconds to a couple of minutes; at rush hour near capacity expect
  break-in within seconds to a minute; a human insertion propagates a braking
  wave and dissolves the spacing.
- **Used in work**: the model's steady-state geometric-mixing assumption is
  exactly the time-average of this break-in/reform process, so the parameter
  p is interpreted as the **time-average** CAV fraction in a lane, not the
  fleet share. The sensitivity analysis over t_plat (0.3–0.7 s) covers the
  degradation from fresh to near-dissolved platoons. This is recorded in the
  parameter table of `solution.json` (source: exchange 10) and in the
  robustness section.

## Summary of reply → work mapping
| Exchange | Model artifact | Location |
|---|---|---|
| 1 | t_lead=1.75 s [1.5,2.0], t_plat=0.5 s [0.3,0.7] | platoon_model.py, cap_lane |
| 2 | platoon = CAV run; L=p/(1−p); one human entry gap per run | platoon_model.py, cap_lane |
| 3 | both-lane equilibrium condition for dedicated scenario | platoon_model.py, dedicated block |
| 4 | no spillover of dedicated-lane slack; random mixing | platoon_model.py |
| 5 | V_FREE fixed at 65 mph; gain is throughput-only | platoon_model.py, greenshields_v |
| 6 | dedicated lane = conversion of the underused lane (SR 520) | solution.json, route 520 |
| 7 | per-lane Greenshields; no cross-lane relief; near-capacity degradation | platoon_model.py, greenshields_v |
| 8 | 100% CAV compliance assumption + leakage bias note | platoon_model.py, solution.json |
| 9 | travel time + equilibrium flag as metrics; 25% tipping threshold | platoon_model.py, output schema |
| 10 | p = time-average CAV fraction; t_plat sweep covers dissolution | solution.json parameter table |
