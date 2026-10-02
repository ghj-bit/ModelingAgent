# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — 2017_C

Three exchanges, one question each, in the order required by the interaction policy.
Request/reply files are in `logs/operator_feedback/` (controller-owned).

## Exchange 1 — Core mechanism

**Question (expert_question_1.md):**
> When a few self-driving cars join a normal highway, what is the single most important way they help traffic move better?

**Reply (expert_reply_1.json, paraphrased):** The single most important effect is smoothing: an SDV with good sensors and short reaction time follows the car ahead at a smaller, steadier gap and damps the stop-and-go waves that human drivers amplify. This reduces the phantom-braking cascades that cause most congestion at high density, so throughput rises even at low penetration. The benefit holds only if the SDV's car-following is stable and it can see far enough ahead; if it mimics human reaction times or drives conservatively with large gaps, the benefit largely disappears.

**How the reply became work:** It set the causal framework for the whole model. The model's core assumption is that SDVs raise *effective lane capacity* (not free-flow speed), via smaller/steadier headways and shockwave damping, so capacity gain scales with penetration even at low f. It also imposed a validity condition used in the limitations section: if SDVs drive with human-like gaps the benefit vanishes (motivating the policy recommendation that the fleet be mandated to cooperative car-following, and the G sweep's lower bound G=1 as the "conservative SDV" case). Recorded in solution.json as the mechanism assumption (task_analysis, assumption 3) and in the parameter table (G).

## Exchange 2 — Boundary condition / saturation point

**Question (expert_question_2.md, built on the smoothing mechanism):**
> If most cars on a road are self-driving, roughly how much less space between cars can they safely keep than human drivers?

**Reply (expert_reply_2.json, paraphrased):** At high automation penetration, cooperative SDVs can safely run at roughly one-third to one-half the headway of human drivers — about 50-70% less space. Concretely: humans hold ~1.5-2 s headway at highway speed; cooperating SDVs with short reaction times and V2V coordination can plausibly run ~0.5-1 s. That is roughly 2-3x higher lane throughput in the ideal case. Stated as an empirical/engineering judgment, assuming stable car-following, reliable sensing and coordination; without those, the reduction shrinks toward zero.

**How the reply became work:** It fixed the saturation point of the model: G, the per-lane throughput multiplier at 100% cooperative penetration, was set to 2.0 (middle of the expert's 2-3x range), with the sweep range [1, 3] taken from the 0.5-1 s vs 1.5-2 s headway statement. It also cross-checked the v_f = 60 mph assumption (1.5-2 s headway at highway speed is consistent with ~60 mph). Both are in the parameter table of solution.json with the source recorded as Exchange 2. The 2-3x ideal gain is the ceiling used in the dedicated-lane calculation (a fully cooperative reserved lane runs at c0(1+G)).

## Exchange 3 — Interpretation / decision threshold

**Question (expert_question_3.md, built on the throughput bounds):**
> By how much would you need to see peak-hour congestion drop before recommending dedicated self-driving car lanes?

**Reply (expert_reply_3.json, paraphrased):** A dedicated-lane recommendation needs a large, durable peak-hour improvement, not a marginal one. As a rule of thumb: peak-hour delay or travel time falling by roughly 20-30% or more on the affected corridor, holding up across the 10% → 50% → 90% penetration range, before recommending lane dedication. The bar is high because dedicating a lane removes capacity from general-purpose traffic, so the gain must clearly exceed that loss. If the improvement is only a few percent, or appears only at high penetration, the lane is more likely to worsen overall congestion than relieve it. Stated as an empirical judgment; the exact figure depends on how much the dedicated lane raises throughput versus how much general capacity it takes away.

**How the reply became work:** It became the model's decision rule: thr = 0.25 (midpoint of the expert's 20-30% band) applied as "recommend a dedicated lane only if the peak-delay reduction is >= 25% at all three penetration levels and the dedicated configuration's capacity change is positive." The rule was executed in code/model.py (the "clear 25% threshold @f=..." lines) and its outcome — all four corridors clear the bar at all three penetrations in the base case, SR-520 and the 2-lane I-405 segments first — is the answer to the Governor's dedicated-lane question in solution.json. The expert's reasoning (dedication costs general capacity) is reflected in the model's explicit net-capacity term c_ded = (L-1)c0 + c0(1+G) rather than a gross gain.

## Compliance notes

- Exactly 3 exchanges, one short question each (all ≤ 20 words), no parts, no modelling terminology, no parameter values requested in advance.
- Every reply was converted into a named parameter or decision rule before the next exchange: Exch.1 → mechanism assumption + validity condition; Exch.2 → G = 2.0 [1,3] and v_f cross-check; Exch.3 → thr = 0.25 [0.20,0.30] decision rule, executed in code.
- No expert sentence, phrase or structure was copied into solution.json; only values, constraints and the decision rule travel, in the model's own formulation.
- No requests were made for coding, debugging, computation, or data processing.
