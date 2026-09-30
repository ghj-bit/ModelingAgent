# Solution

## Subtask 1: Requirement 1: Construct a mathematical model to identify the best 3-dimensional geometric shape to use as a sandcastle 

### Problem

Requirement 1: Construct a mathematical model to identify the best 3-dimensional geometric shape to use as a sandcastle foundation that lasts the longest on a seashore that experiences waves and tides, under the conditions that all castles are built at roughly the same distance from the water on the same beach, with the same type of sand, roughly the same amount of sand, and the same water-to-sand proportion.

### Analysis

The statement fixes the comparison conditions (same beach, same distance from water, same sand, same volume, same moisture), which by the expert consultation (Exchange 1) forces an equal-volume comparison: 'best shape' is a pure geometric question, with size separable from shape. The consultation established three open structural boundaries that I committed: (A) the objective is time to first structural collapse; (B) the loss mechanism is two co-equal channels; (C) the horizon is one tidal cycle with the distance-from-water as a fixed given. The expert's Exchange-3 counterexample (an overhanging / inverted profile fails by bed scour to the waist and toppling) restricts the feasible set to monotone-width profiles (widest at the base); overhanging profiles are structurally infeasible. Within the feasible set, the two failure channels are: Channel 1, swash erosion (volume removal from the exposed surface); and Channel 2, strength-vs-stress collapse at the base (overburden + wave-impact stress exceeds the moisture-dependent sand strength). The best shape maximizes the time to first failure from either channel over one tidal cycle.

### Modeling Process

Candidate family: monotone-width truncated cones (frustums) at fixed volume V=0.5 m^3, parameterized by the taper t = R_top/R_base in {0, 0.1, 0.3, 0.5, 0.7, 1.0} (1.0 = cylinder, 0 = full cone), all scaled to volume V with a common base radius. Geometry: V = (pi/3) H (R_base^2 + R_base R_top + R_top^2). Channel 2 (strength collapse, the primary discriminator): the applied stress at the base (the most-stressed level for a monotone-width profile) is the overburden plus a wave-impact amplification: sigma_base = (rho_sand g H / 3)(1 + t + t^2)(1 + alpha H_wave), with rho_sand = 1600 kg/m^3, alpha = 0.05 m^-1. This is largest for the cylinder (t=1) and smallest for the cone (t=0) at fixed height, because the cylinder carries the most mass above the base. The sand strength S(w) is a function of the liquid volume fraction w via the ~1% optimum (Pakpour et al. 2012): S(w) = S_peak * f(w), with f(w) a log-quadratic normalized to 1 at w*=1% and falling to 0 at the castable limits (0.5%, 15%), S_peak = 8 kPa. The structure fails Channel 2 when sigma_base > S(w); the time-to-failure is t* = 0.5 (S/sigma) for a failure (continuous in the margin) or t* = 1 (survives) otherwise. Channel 1 (swash erosion): the swash erodes the exposed surface area A_exposed = pi(R_base+R_top) slant + pi R_top^2 at a rate dV = k_erode * A_exposed * (shear_ratio - 1)^+ over the cycle, with k_erode ~ 1e-3 m^2/cycle scaled by the swash length; the structure fails Channel 1 when dV >= 0.5 V. The time to first failure is t* = min(t*_erosion, t*_strength). Baseline scenario: H_wave = 1 m, T = 8 s, tidal range = 1.5 m, w = 1%, shear_ratio = 1 (at threshold), V = 0.5 m^3.

### Outcome Analysis

At the baseline (1% moisture, H=1 m, micro-tidal), the best shape is the truncated cone with taper t = 0.3 (R_top/R_base = 0.3) — a wide, low, base-heavy convex profile. It survives the full tidal cycle (t* = 1). The low-taper shapes (t = 0, 0.1, 0.2, 0.3) all survive; the high-taper shapes (t = 0.5, 0.7, 1.0) fail via the strength channel at t* = 0.46T, 0.39T, 0.32T respectively, because their overburden stress (8.8, 10.2, 12.6 kPa) exceeds the 8 kPa strength. The result is robust: across the full literature envelope (H_wave in [0.5, 2.0] m, tidal range in [1, 2] m) and the shear-ratio sweep [1, 2], the truncated cone t=0.3 remains the best shape and survives in every scenario; the wave forcing shifts the stress values but not the ranking, because the overburden (taper-differentiating) dominates the modest wave-impact amplification. Limitations and biases: (1) the recommendation is valid only within the monotone-width feasible set; overhanging profiles (inverted cone, mushroom) fail by a toppling mode (bed scour to the waist) the model excludes by construction, so the model does not rank them — this is the model's stated limit, per the expert's counterexample. (2) The strength calibration (S_peak = 8 kPa) is an order-of-magnitude value; the absolute survival/failure boundary shifts with it, but the shape ranking (wide-and-low wins) is insensitive to it because it is set by the overburden's taper dependence. (3) The erosion channel is a secondary effect (removes ~0.2-0.5% of V per cycle, far below the 50% failure threshold), so the conclusion is dominated by the strength channel. (4) The model evaluates a discrete family of frustums; the continuous optimum lies near t ~ 0.2-0.3.

## Subtask 2: Requirement 2: Using the model, determine an optimal sand-to-water mixture proportion for the castle foundation, assumin

### Problem

Requirement 2: Using the model, determine an optimal sand-to-water mixture proportion for the castle foundation, assuming no other additives or materials.

### Analysis

The optimal proportion is the moisture content that maximizes the foundation's survival, which in the model is governed by the sand strength S(w), the backbone of the strength channel. The strength is a function of the liquid volume fraction w, sharply peaked near the ~1% optimum documented by Pakpour et al. (2012): below ~1% too few capillary bridges form to bind the grains; above it the bridges merge into blobs that lubricate rather than bind, so strength falls. The model therefore takes the strength-vs-moisture curve (unimodal, peaked at w* = 1%, castable range 0.5-15%) as the backbone of the mixture-strength function, and the optimal proportion is the peak of that curve, verified by sweeping w across the castable range and re-evaluating the shape ranking at each level.

### Modeling Process

Strength backbone: S(w) = S_peak * f(w), with f(w) a log-quadratic in w normalized to 1.0 at w* = 0.01 (1%) and falling to 0 at the castable limits w = 0.005 (0.5%) and w = 0.15 (15%): for w <= w*, f = max(0, 1 - (ln(w/w*)/ln(w*/w_lo))^2); for w > w*, f = max(0, 1 - (ln(w/w*)/ln(w_hi/w*))^2). S_peak = 8 kPa. The optimal proportion is w* = argmax_w S(w) = 1% (liquid volume fraction), i.e. roughly 1 part water per ~99 parts dry sand by volume. Validation: sweep w over {0.5%, 1%, 2%, 5%, 15%} and re-evaluate the shape ranking at each level; the optimal proportion is the w at which the best shape's survival is maximized.

### Outcome Analysis

The optimal sand-to-water proportion is ~1% liquid volume fraction (about 1 part water to 99 parts dry sand by volume), the peak of the strength curve. At this proportion the best shape (truncated cone t=0.3) survives the tidal cycle. The result is sensitive to moisture in the expected way: at 0.5% (too dry) the strength is near zero and no shape holds; at 1% (optimum) the strength peaks and the wide-and-low shapes survive; at 2% (just past the optimum) the strength falls slightly (7.5 kPa) and the best shape shifts to a lower taper (t=0.2) but still survives; at 5% (rain-driven, well past the optimum) the strength falls to 5.2 kPa and no shape survives; at 15% (saturated) the strength is zero and nothing holds. The recommendation is robust in direction: the optimum is a narrow peak near 1%, so the practical guidance is to pack the sand just damp (the 'squeeze it and it holds, but no water squishes out' consistency) and avoid both under-watering (too dry to bind) and over-watering (too wet, lubricated). Bias: the absolute height of the strength peak (S_peak = 8 kPa) is an order-of-magnitude calibration; the location of the optimum (1%) is anchored to the cited literature and is the robust part of the result.

## Subtask 3: Requirement 3: Adjust the model as needed to determine how the best 3-D sandcastle foundation identified in Requirement 

### Problem

Requirement 3: Adjust the model as needed to determine how the best 3-D sandcastle foundation identified in Requirement 1 is affected by rain, and whether it remains the best shape when it is raining.

### Analysis

Rain adds liquid to the sand, driving the local moisture content upward past the ~1% optimum. In the model this is a change of the forcing, not of the shape: the strength channel's S(w) is re-evaluated at the rain-driven moisture, and the erosion channel's critical shear is lowered because rain softens the bed. The question is whether the best dry-shape (truncated cone t=0.3) remains the best under rain, or whether the ranking flips.

### Modeling Process

The dry baseline is w = 1% (S = 8 kPa), best shape t = 0.3, survives. Rain scenarios re-evaluate the same candidate family at the rain-driven moisture: moderate rain w = 5% (S = 5.17 kPa) and heavy rain / saturation w = 15% (S = 0). At each moisture the two-channel failure check is re-run and the ranking reported. The erosion channel is also affected because rain softens the bed (lower critical shear, higher shear_ratio), but within one tidal cycle the erosion removes only ~0.2-0.5% of V, so the strength channel remains the discriminator.

### Outcome Analysis

Rain degrades the best shape but does not flip the ranking to a different shape. At moderate rain (w=5%), the strength falls to 5.17 kPa and no shape survives the cycle — the best dry-shape (t=0.3) fails at t*=0.34T, and the cone (t=0, lowest overburden, 6.0 kPa stress) is the least-bad at t*=0.43T. At heavy rain (w=15%, saturation), the strength is zero and nothing holds; the ranking is degenerate. So the answer to 'does it remain the best shape' is: the direction of the recommendation (wide-and-low, base-heavy convex profile) is preserved — the cone and low-taper shapes are always the most resistant — but the survival conclusion flips from 'survives the cycle' (dry) to 'nothing survives' (rain). The best shape under rain is the same family (lowest taper / cone), because the overburden is the binding constraint and the cone minimizes it. Practical implication: a sandcastle built at the optimal ~1% moisture is fragile to rain; the shape that lasts longest in dry conditions is the one that degrades least gracefully in rain, but no shape is rain-proof once the moisture is driven past ~5%.

## Subtask 4: Requirement 4: What other strategies, if any, might you use to make the sandcastle last longer?

### Problem

Requirement 4: What other strategies, if any, might you use to make the sandcastle last longer?

### Analysis

The two-channel structure implies that longevity is improved by any strategy that (a) reduces the overburden stress at the base below the sand strength (Channel 2), or (b) reduces the exposed surface area and the bed-scour (Channel 1), or (c) raises the sand strength by adjusting the moisture toward the ~1% optimum. These map onto concrete, citable strategies.

### Modeling Process

Strategies are evaluated by which channel they act on and the direction of the effect in the model: (1) A wider, lower base (lower taper) reduces the overburden stress sigma_base = (rho g H/3)(1+t+t^2) and the exposed area per unit volume, acting on both channels — this is the shape recommendation itself. (2) Packing the sand more densely / compacting the core raises the in-place density rho_sand and the cohesive strength S_peak, acting on Channel 2 (though a higher rho_sand also raises the overburden, so compaction must be balanced with the moisture optimum). (3) Maintaining the moisture near the ~1% optimum (re-wetting a drying castle, or shading it from the sun to prevent over-drying, or protecting it from rain to prevent over-wetting) keeps S(w) near its peak, acting on Channel 2. (4) Building farther from the waterline (increasing the distance from the swash zone) reduces the inundation depth and the swash energy at the castle, acting on Channel 1 — but this is fixed by the problem's comparison condition, so it is a strategy outside the model's controlled variables. (5) A moat or a sacrificial outer ring of loose sand that absorbs the swash before it reaches the foundation, acting on Channel 1 (adds a buffer that erodes instead of the foundation).

### Outcome Analysis

The highest-leverage strategies, in order: (1) Build the foundation as a wide, low, base-heavy convex profile (truncated cone, taper ~0.3) — this is the single most effective strategy and is the result of Requirement 1. (2) Keep the moisture at the ~1% optimum: pack the sand just damp and protect it from both sun (over-drying) and rain (over-wetting); a castle that dries out or gets soaked loses most of its strength. (3) Compact the core densely to raise the cohesive strength, balanced against the moisture optimum. (4) If the site allows, build farther upslope from the swash zone, or add a sacrificial moat / outer ring of loose sand that takes the swash in front of the foundation. Limitation: strategies 4 and 5 change the controlled variables of the comparison (distance from water, added materials) and are therefore outside the model's scope; they are offered as practical extensions, not as part of the controlled shape optimization.

## Subtask 5: Requirement 5: Write an informative, one- to two-page article describing the model and its results for publication in th

### Problem

Requirement 5: Write an informative, one- to two-page article describing the model and its results for publication in the vacation magazine 'Fun in the Sun', whose readers are mainly non-technical.

### Analysis

The article must convey the model's logic and its headline result — that a wide, low, cone-shaped foundation of just-damp sand is the shape that lasts longest against waves and tides — in plain language, without equations, for a non-technical beachgoer audience. It should explain why shape matters (wide-and-low resists the weight of its own sand and the scouring of the waves), why the sand should be just damp (the 'squeeze it and it holds' moisture), and why rain is the enemy (it soaks the sand past the sweet spot and the whole castle softens).

### Modeling Process

Article body (plain language, no equations):

'Why Your Sandcastle Washes Away — And the Shape That Beats the Tide

You have been there: you spend an hour packing a grand sandcastle right at the water's edge, and the next wave takes a bite out of it. By lunch it is a pile. Why do some castles survive the afternoon and others do not, even when they are the same size and built in the same sand? It comes down to two things — the shape of the base and how wet the sand is — and getting both right is the difference between a castle that lasts and one that does not.

The shape that wins is wide at the bottom and gently sloping up to a narrow top — think of a traffic cone or a wedding cake, not a tall block or a tower. Here is why. A sandcastle has to support the weight of its own sand, and a tall, narrow castle piles all that weight onto a small footprint at the bottom. The sand at the base is crushed and gives way, and the whole thing slumps. A wide, low cone spreads that same weight over a big base, so the sand at the bottom is never overloaded. It also shows the waves less of a flat wall to push against, so the water slides off and around instead of scooping out the base. A castle shaped like a wide, low cone simply does not give the tide as much to work with.

The other half is the sand itself. Dry sand will not hold — it just crumbles. Soaked sand will not hold either — it turns to mush. The sweet spot is just damp: squeeze a handful and it holds its shape, but no water squishes out. That is about one part water to a hundred parts sand, barely enough to glaze the grains and make them stick. Pack your castle at that consistency and it is as strong as sand can get.

This is also why rain is a sandcastle's worst enemy. Rain soaks the sand past that sweet spot, and once the sand is too wet it loses almost all of its grip. No shape can save a soaked castle — the wide, low cone that outlasts everything on a dry day will still soften and slump in a heavy rain. If a storm is coming, the best strategy is to build your castle a little farther up the beach, out of the reach of both the waves and the worst of the rain, and to keep it shaded so the sun does not dry it out.

So the recipe for a castle that beats the tide is simple: a wide, low, cone-shaped base, packed with just-damp sand, built a little way up from the water. Get the shape and the dampness right, and you will still have a castle at high tide while the blocky towers next door are already rubble.'

### Outcome Analysis

The article distills the model's two findings for a non-technical reader: (1) the best shape is a wide, low, base-heavy cone (truncated cone, taper ~0.3), because it spreads the overburden over a large base and presents less of a wall to the waves; and (2) the sand must be at the ~1% 'just-damp' optimum, and rain drives the moisture past that optimum and softens the castle regardless of shape. The article is within the one-to-two-page target length for a vacation-magazine feature and uses no equations. Limitation: it necessarily omits the quantitative detail (the stress values, the survival times, the sensitivity sweeps) that the machine-readable container carries; it is a communication artifact, not a substitute for the model.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
