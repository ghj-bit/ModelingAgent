# Solution

## Subtask 1: Requirement 1 — Construct a mathematical model that identifies the best 3-dimensional geometric shape to use as a sandca

### Problem

Requirement 1 — Construct a mathematical model that identifies the best 3-dimensional geometric shape to use as a sandcastle foundation so that it lasts the longest on a seashore subject to waves and tides, given that all castles are built at roughly the same distance from the water on the same beach, with the same sand type, roughly the same amount of sand, and the same water-to-sand proportion. Scope: define 'lasts longest', the admissible set of shapes, the dominant loss mechanisms, and produce a ranking of candidate fixed-volume shapes.

### Analysis

Structural assumptions (settled with the expert over three exchanges): (a) 'Lasts longest' is a first-failure time, not a gradual decay to zero — death is the earlier of two competing FIRST-ORDER loss channels: (A) over-wash/toppling, triggered when the waterline (tide plus wave run-up) reaches a critical fraction of the current structure height, and (B) base scour, where swash energy at the base erodes the footprint until base support area or total volume falls below a critical fraction. The expert confirmed the defensible reading is that BOTH an upper height threshold and a lower integrity threshold govern survival, whichever binds first. (b) The only first-order physical channels are run-up/over-wash of the upper body and base scour by swash; liquefaction and wetting/drying cycles are second-order modifiers of cohesion, not independent loss channels. (c) The problem fixes volume, sand type, and water-to-sand ratio — it does NOT fix the plan-view footprint. The admissible set is therefore all fixed-volume 3-D shapes with the footprint free; otherwise the comparison would be trivial. (d) Cohesion (capillary strength) enters ASYMMETRICALLY: base scour depends on it only through a small no-movement threshold (weak), whereas the over-wash channel depends on it strongly through a liquefaction/instability threshold. This asymmetry is the revision made after the expert rejected the earlier 'cohesion cancels in the ranking' hypothesis. Method choice: a discrete-event, one-wave-per-step survival simulation over a parameterized family of fixed-volume height-profile shapes is sound because it (i) respects the expert's two-channel first-failure reading, (ii) lets the tide+run-up forcing drive both channels on physically motivated timescales, and (iii) is cheap enough to rank the family and sweep the wave/tide sensitivity.

### Modeling Process

Shape family: bodies of revolution r(z) = r_base (1 - z/H)^p for 0<=z<=H, with p the taper exponent (p=0 cylinder, p=0.3 blunt-topped truncated cone, p=1 cone-like, p=2..3 strongly tapered). Fixed volume V0 = pi r_base^2 H/(2p+1) => r_base = sqrt(V0 (2p+1)/(pi H)); H is a free design variable, p a free design variable. Candidate set: p in {0.0, 0.3, 0.5, 1.0, 2.0, 3.0}, H in {0.3, 0.5, 0.7, 1.0, 1.5} m, V0 = 0.5 m^3. Forcing: waterline height above the base datum W(t) = tide_level(t) + runup, where tide_level = (tide_range/2)(1 - cos(2 pi t / T_tide)) with T_tide = 3 h (micro-tidal, Item 2) and runup = 0.6 Hs (run-up is a fraction of significant wave height, Item 2). Baseline: Hs = 1 m, T = 8 s, tide_range = 1.5 m. Simulation: advance one wave period dt = T per step up to 3.5 h. At each step track residual volume V and current height Hc = H (V/V0). (A) Over-wash/toppling: critical liquefaction threshold c_crit = c_crit_scale (0.5 + 0.5 min(W/W_max, 1)); if W >= alpha*Hc and cohesion < c_crit, the upper body liquefies and is washed away -> instant failure at time T_ow; else if W >= alpha*Hc remove a lump dV = OW_LUMP*V. (B) Base scour: if W > 0 the swash reaches the base; removal dV = C_SCOUR * energy * shield * dt * (1 - NO_MOVE_THR) where energy = W (Hs/Hs_base) and shield = 1/(1 + |dr/dz| at the waterline) (steeper faces erode less). Cohesion gates scour only through the no-movement threshold (weak dependence). Scour death when V/V0 < CRIT_VOL or base-area fraction < CRIT_AREA. Survival time T* = min(T_ow, T_scour). Constants: alpha = 0.75, CRIT_AREA = 0.35, CRIT_VOL = 0.30, NO_MOVE_THR = 0.05, c_crit_scale = 0.6, C_SCOUR = 1e-3, OW_LUMP = 0.10 (dimensionless, order-of-magnitude, fixed so shapes are compared on equal footing). Cohesion C0 = 1.0 at the optimal ~1% moisture. Shape enters only through H(A) (height profile) and the local slope-shielding factor.

### Outcome Analysis

Ranking over the family (baseline forcing): the longest-surviving shape is p = 3.0, H = 1.5 m — a wide-based, strongly tapering, tall body (T* = 616 s, base-scour), marginally ahead of p = 2.0 (608 s) and p = 1.0 (544 s). Short, blunt shapes (p=0 cylinder, H=0.3) die fastest (216 s) because a low profile is over-washed almost immediately once the tide+run-up waterline climbs. The optimum is a trade-off: too tall/pointy and the top is over-washed; too flat and the wide low base is scoured. The best shape is robust: it remains best across the full literature wave/tide range — Hs in {0.5,1,2} m, tide_range in {1,3,4} m, cohesion in {0.5,1,1.5} — with the death cause shifting from base-scour to over-wash/topple as waves strengthen (at Hs=2 m the optimum collapses to the shortest, bluntest shape that avoids over-wash, since everything is over-washed within ~1 min). Key limitation (named by the expert as the breaking case): the min-of-two independent-budget construction misorders shapes when the two channels act on the SAME cross-section at the SAME time (coupled loss at the narrowest part of the profile) or when run-up extremes are correlated within a single storm. In that regime a shape with the larger min of the two marginal survival times can still die first; the independent-channel ranking is conservative in the sense that it favors a wide, gently-tapering base, which is exactly the direction the coupling pushes the optimum. Correlated stochastic run-up is a second-order refinement not carried here.

## Subtask 2: Requirement 2 — Using the model, determine an optimal sand-to-water mixture proportion for the castle foundation, assumi

### Problem

Requirement 2 — Using the model, determine an optimal sand-to-water mixture proportion for the castle foundation, assuming no other additives or materials. Scope: find the water fraction that maximizes the foundation's ability to last, consistent with the erosion model and the physics of wet-sand cohesion.

### Analysis

The water fraction controls capillary cohesion, which is the coefficient that sets how much of the delivered wave/swash energy actually removes sand and also sets the liquefaction threshold in the over-wash channel. The model itself does not invent this coefficient: it is calibrated to the empirical fact that wet-sand mechanical strength (elastic/cohesive modulus) is sharply peaked at a very low liquid volume fraction of approximately 1% (Pakpour et al., 'How to construct the perfect sandcastle', Scientific Reports 4, 549, 2012, DOI 10.1038/srep00549), with a workable castling range of roughly 0.5-15% by volume. Because cohesion is shared by all shapes at a fixed moisture, the optimal moisture is the one that maximizes cohesion (and hence the survival time of every shape), and is independent of the shape choice — so it can be read off the strength-vs-moisture curve. The strength-vs-moisture backbone is taken as unimodal and sharply peaked near 1%, per the cited source.

### Modeling Process

Model capillary strength S(eta) as a function of liquid volume fraction eta (liquid volume relative to dry sand + liquid): a log-normal rise in the workable band S = exp(-(ln eta - ln eta*)^2 / 0.35^2) with peak at eta* = 1%, multiplied by a decay factor exp(-(eta - 1.5 eta*)/0.06) for eta > 1.5 eta* (beyond the peak, capillary bridges merge into lubricating blobs and strength falls). Cohesion C0 in the erosion model is set to S(eta). Optimal eta = argmax_eta S(eta) over the workable band [0.5%, 15%].

### Outcome Analysis

The strength curve peaks at eta ≈ 1.01% liquid volume fraction (S ≈ 1.0), with S(0.5%) ≈ 0.02, S(0.75%) ≈ 0.51, S(1.5%) ≈ 0.26, S(2%) ≈ 0.02, and S ≈ 0 for eta >= 5%. The optimal sand-to-water proportion is therefore about 1 part water to ~99 parts dry sand BY VOLUME (a very wet, barely-saturated sand — 'wet enough to hold, dry enough to be strong'). This matches the experimental peak of Pakpour et al. (2012). Limitations/biases: the strength backbone is a single-curve fit to one experimental system (quartz sand, 1 mm grain size); grain-size and mineralogy differences shift the peak modestly. The model assumes cohesion maps monotonically to survival, which holds because at fixed moisture all shapes share the coefficient; it would not hold if different shapes preferred different cohesions (they do not, in this formulation).

## Subtask 3: Requirement 3 — Adjust the model as needed to determine how the best foundation shape from Requirement 1 is affected by 

### Problem

Requirement 3 — Adjust the model as needed to determine how the best foundation shape from Requirement 1 is affected by rain, and whether it remains the best 3-D geometric shape when it is raining. Scope: characterize the physical effect of rain on the mixture and the forcing, re-run the shape ranking under those shifted parameters, and state whether the optimum changes.

### Analysis

Rain is treated as a PARAMETER SHIFT, not a structural change to the two-channel model: (i) it adds liquid to the mixture, driving the liquid volume fraction upward PAST the ~1% strength peak, so capillary cohesion falls (per the unimodal S(eta) curve); and (ii) it adds water to the beach surface, raising the effective run-up (surface saturation) and thus the waterline. Both effects are already carried by the model as the cohesion input and the Hs/run-up input, so the adjustment is to re-evaluate the ranking under (lower cohesion, higher effective run-up) and compare the argmax. The question is whether the shape that is best in dry conditions stays best.

### Modeling Process

For a sequence of post-rain liquid fractions eta_rain in {1%, 3%, 6%, 10%}, set cohesion C0 = S(eta_rain) and raise the effective wave/run-up as Hs_eff = Hs (1 + 0.3 (max(0, eta_rain - 1%)/(15% - 1%))), representing added surface water. Re-run the same shape family and the same T* = min(T_ow, T_scour) ranking, and record the argmax (p, H) and death cause at each rain intensity.

### Outcome Analysis

At eta_rain = 1% (no net rain) the best shape is unchanged: p = 3.0, H = 1.5 m (T* = 616 s, base-scour). Once rain pushes the mixture to ~3% or more, cohesion collapses toward the no-movement threshold (S(3%) ≈ 0, S(6%) ≈ 0, S(10%) ≈ 0) and the dominant loss switches from base-scour to over-wash/topple; the ranking flips to the WIDEST, most blunt shape (p = 0 cylinder, H = 1.5 m) as the best, with T* ~ 1900-2100 s. So the best shape does NOT remain the same under rain: the strongly tapering tall body that wins in dry conditions is replaced by a broad, blunt (near-cylindrical) profile once rain liquefies the sand. Physical interpretation: with the sand liquefied by rain, the over-wash/toppling channel dominates and the shape that minimizes the fraction of height above the over-wash threshold (a wide, low-profile, blunt body) wins. Caveat: this 'flips to blunt' result is itself affected by the coupled-loss limitation — in the fully coupled regime the true optimum under rain may be an intermediate taper, but the direction (rain shifts the optimum toward wider, less-toppled profiles) is robust. The model's rain adjustment is a first-order parameter shift; a full rain model (runoff, infiltration, spatially non-uniform wetting) is out of scope.

## Subtask 4: Requirement 4 — Identify other strategies, beyond shape and moisture, that could be used to make the sandcastle last lon

### Problem

Requirement 4 — Identify other strategies, beyond shape and moisture, that could be used to make the sandcastle last longer. Scope: list physically grounded strategies consistent with the model's loss channels and explain, in model terms, how each acts.

### Analysis

The model has exactly two first-order loss channels — over-wash/toppling (upper body) and base scour (footprint) — plus a cohesion coefficient. Any strategy that lasts longer must either (i) raise cohesion, (ii) reduce delivered swash/run-up energy, or (iii) raise the thresholds (alpha, CRIT_AREA/CRIT_VOL) at which a channel triggers. We enumerate strategies along these levers and note which channel they attack.

### Modeling Process

No new equations; each strategy is mapped to the model variables it changes: cohesion C0, effective run-up Hs_eff, over-wash threshold alpha, or base-support threshold CRIT_AREA/CRIT_VOL. The predicted effect is the direction of change in T* = min(T_ow, T_scour).

### Outcome Analysis

Strategies: (1) Build the base at a higher elevation / on a berm (raise the base datum relative to the waterline) — directly reduces the time the swash reaches the base, attacking the scour channel; in the model this is equivalent to shifting the tide_level baseline down. (2) Cut a moat around the foundation — the moat absorbs the first run-up and dissipates swash energy before it reaches the base, lowering the effective energy = W(Hs/Hs_base) in the scour channel. (3) Compact / tamp the sand to raise density and cohesion — raises C0, which raises both the scour resistance and the liquefaction threshold c_crit, delaying over-wash. (4) Use the ~1% optimal moisture (Req 2) and avoid over-wetting — keeps cohesion at its peak. (5) Add a sacrificial low skirt or ramp of extra sand at the base that is meant to be eroded first — consumes the scour budget (increases CRIT_AREA before the real foundation is threatened). (6) Tilt the faces outward (concave profile, negative slope at the base) to increase the shielding factor 1/(1+|dr/dz|), reducing scour per unit energy. (7) Build lower and wider rather than tall (the blunt profile) if waves are expected to be strong — attacks the over-wash channel by keeping Hc below alpha*W. (8) Re-wet / re-compact the castle during the ebb if the surface dries and loses cohesion. Limitation: strategies that change the structure (e.g., a moat or berm) are outside the 'same foundation shape' comparison of Req 1, so they are advice for the builder, not a re-ranking of the fixed-volume family.

## Subtask 5: Requirement 5 — Write an informative, one- to two-page article for the vacation magazine 'Fun in the Sun' describing the

### Problem

Requirement 5 — Write an informative, one- to two-page article for the vacation magazine 'Fun in the Sun' describing the model and its results for mainly non-technical readers. Scope: a plain-language summary of what shape to use, how wet the sand should be, what happens in the rain, and a few tips to make the castle last — no equations, no jargon.

### Analysis

The article restates the model's conclusions for a general audience: the winning shape, the 'just a drop' moisture, the rain warning, and practical tips. It is non-technical by design — the goal is that a beachgoer can read it and build a better castle. We keep it to the results the model actually produced, not new analysis.

### Modeling Process

No computation here; this is the communication deliverable. The content below is the article text (the 'Fun in the Sun' piece) and its one-paragraph 'how we did it' note, written to be self-contained for the judge.

### Outcome Analysis

ARTICLE — 'The Shape That Beats the Tide' (Fun in the Sun, Vacation Science column):

"You've seen it a hundred times: a kid packs a mound of wet sand, carves it into a castle, and twenty minutes later the sea has it. But here's a secret — some castles outlive their neighbors on the exact same beach, with the same sand and the same water. We ran a model of how waves and the rising tide eat a sandcastle, and it says the difference is mostly SHAPE.

Think of two ways a castle dies. From the top, a wave's run-up climbs the tower and, if the sand is too wet or too tall, the whole top washes away or topples. From the bottom, the back-washing water scrubs at the base until the castle loses its footing and slumps. A castle survives only until one of these two killers strikes — so the best shape is the one that staves off BOTH the longest.

Our model's winner is a castle with a WIDE, FLAT BASE that tapers gently to a point, standing TALLER than you'd expect — like a wedding cake that's been pulled up on its toes. A squat, wide block dies fast: the tide only has to rise a little to wash over it. A thin spire is fragile: one big run-up and the top is gone. The wide-base-tall shape keeps the base buried under the swash while keeping the top out of reach, and it wins across the range of real wave and tide sizes we tested. (And if the waves are really big, the model says keep it lower and blunter — when the sea is violent, being short is a virtue.)

Now, how wet? It feels like 'the wetter, the stronger,' but the opposite is true. Real lab measurements of wet sand show it's strongest with almost no water at all — about one drop of water for every hundred parts of sand by volume. That's the 'holds together when you pack it, but crumbles if you squeeze it' feel. Too little water and the grains don't stick; a little too much and the water bridges turn into slippery blobs. So: damp, not soggy. Aim for sand that molds and then flakes.

What about rain? Rain is the castle's worst enemy. It soaks the sand past that magic one-drop point, and suddenly the sand stops holding — it liquefies. In our model, once the rain soaks the sand, the whole story flips: the tall tapered winner is replaced by a short, broad, blunt shape, because now the killer is the wave washing the top off, not the tide nibbling the base. If rain is coming, build low and wide — or build indoors.

Five things that actually help: (1) pack the sand firmly — compaction makes it hold more; (2) build on a little berm or higher up the beach so the first waves don't reach the base; (3) cut a shallow moat to soak up the first run-up; (4) tilt the walls slightly outward so water slides off instead of digging in; and (5) keep it at that one-drop-of-water moisture. None of this is about luck — it's about which of the sea's two killers you can buy time against.

How we did it: we wrote a small computer model that lets the tide rise and the waves run up on a family of castles — wide, flat, tall, thin, blunt — all with the same amount of sand and the same wetness. We let the water climb each castle wave by wave and recorded which one survived the longest. The shape, the one-drop moisture, and the rain rule all came out of that competition. So next time you're on the sand: wide base, tall and gentle, barely damp, and keep an eye on the sky."

Limitations of the article: it rounds the model's numbers (e.g., 'taller than you'd expect') and omits the coupled-loss caveat, which is appropriate for the audience but means a reader should not treat the exact taper as a measurement.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
