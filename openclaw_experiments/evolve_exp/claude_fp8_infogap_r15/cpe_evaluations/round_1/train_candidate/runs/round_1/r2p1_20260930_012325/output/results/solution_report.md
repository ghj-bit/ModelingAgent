# Solution

## Subtask 1: Subtask 1 -- Formulate a generic mathematical model for planning the search for a lost aircraft over open water (Atlanti

### Problem

Subtask 1 -- Formulate a generic mathematical model for planning the search for a lost aircraft over open water (Atlantic, Pacific, Indian, Southern, or Arctic), flying from Point A to Point B, with no signals from the aircraft. The model must be generic over (a) many types of lost planes (different fuselages, different debris signatures) and (b) many types of search platforms with different electronics and sensors (aerial EO/IR, synthetic-aperture radar, shipborne towed magnetometer, sonar). The model must output a search plan: which region to search at each elapsed day, which platform to assign where, and how the plan changes as the days pass. This subtask sets up the objective function, the spatial prior, the detection model, and the allocation rule.

### Analysis

Assumptions and rationale.

(1) No-signal regime. The problem states there are no signals from the downed plane, so the prior over the crash location cannot be built from an acoustic or radio beacon location. It must be built from the last-known position (LKP) at declaration of loss plus the modeled drift of any debris. This is the dominant source of uncertainty and is the weak link of the whole model (see Subtask 3).

(2) Search-theory decomposition. We adopt the standard SAR decomposition POS = POA x POD (Koopman's search theory), per external_data.md Item 1. Overall probability of success is the sum over search segments of POA_i x POD_ij, where POA_i is the probability the target lies in segment i and POD_ij is the probability platform j detects the target in segment i given the target is present. This is the correct objective because it is the only framework that lets heterogeneous sensors be compared on a common probability-of-success scale rather than on incommensurable 'area searched' or 'hours flown' scales.

(3) Heterogeneous platforms as distinct detectors. Each sensor type (EO/IR, SAR radar, towed magnetometer, sonar) is a distinct detector with its own effective sweep width / effective coverage probability, its own target classes it can detect, and its own cost per day. This directly answers the problem's requirement that the model recognize many types of search planes using different electronics or sensors.

(4) Target classes. The lost aircraft produces several target classes with very different detectability time-scales, per external_data.md Item 2 and the operational ground truths from the expert consultation (Exchange 1): (a) flares/signals -- burn out within hours; (b) visible surface debris and life rafts -- detectable for days, with the SOLAS 30-day afloat bound as the outer limit for survival craft; (c) submerged wreckage -- detectable for weeks, decays slowly; (d) flight-recorder beacon -- a fixed battery window of about 30 days, then zero. The SOLAS 30-day figure is used only as the outer bound for survival-craft detection, not as a bound for debris or beacon battery life, exactly as the data file prescribes.

(5) Spatial prior. The POA is a bivariate normal (1-D Gaussian marginal in the along-track direction) centered on the LKP, with standard deviation growing as sigma_lkp + diffuse * sqrt(t) -- an advection-diffusion (random-walk) spread of debris driven by current and wind leeway. The search region at day t is the drift track the fleet flies: a box centered on the modeled drift mu_x(t) = drift_v * t with fixed half-width R = max(3*sigma_lkp, 0.25*drift_v*horizon). The POA at day t is the fraction of the target's probability mass that lies inside that box.

(6) Cost-normalized allocation. Platforms are allocated to maximize total probability of success per unit cost (relative cost per day). Because surface target classes (a, b) decay fastest, the allocation is time-phased: early days weight aerial surface-search platforms, later days weight shipborne submerged-search platforms. This is the structural hypothesis accepted by the expert in Exchange 2.

(7) Generality over plane types. The model is generic over the lost plane because the target-class mass fractions (how much of the debris is floating, submerged, beacon) and the per-class decay rates are parameters, not hard-coded. A narrow-body jet, a wide-body, a regional turboprop, or a military transport would be distinguished by different class-mass vectors and different surface-debris fractions; the model structure is unchanged.

Choice of method and why it is sound. The POA x POD framework is sound because it is the established SAR theory (Koopman 1980), it is the only way to compare heterogeneous sensors on a common scale, and it makes the failure modes explicit: POA errors (wrong prior) corrupt every term multiplicatively, while POD and cost errors are local to one platform. The time-phased allocation is sound because the detectability time-scales differ by orders of magnitude across target classes, so a static allocation that searches the same classes equally at day 0 and day 30 wastes early effort on submerged classes that are barely detectable and late effort on surface classes that have already decayed away.

### Modeling Process

Variables.
- t: elapsed days since declaration of loss, t in [0, horizon].
- sigma_lkp: LKP positional uncertainty at t=0 (km, 1-sigma). Default 100 km.
- drift_v: modeled current drift velocity (km/day). Default 30 km/day.
- diffuse: diffusive spread coefficient (km/day). Default 20 km/day.
- unmodeled_leg: length of an unmodeled late leg before loss (km). Default 0.
- true_drift_v: true current velocity (km/day); the prior's drift_v is wrong by |true_drift_v - drift_v|. Default 30 (correct prior).
- t_flare_h: flare decay constant (hours). Default 6 h.
- t_debris_d: surface-debris decay constant (days). Default 10 d.
- solas_days: SOLAS outer bound for survival craft (days). Default 30.
- t_sub_d: submerged-wreckage decay constant (days). Default 40 d.
- beacon_days: beacon battery window (days). Default 30.
- p_ao_air, p_ao_radar, p_mag, p_sonar: sensor effective coverage probabilities per pass. Defaults 0.30, 0.20, 0.08, 0.05.
- cost_air, cost_radar, cost_mag, cost_sonar: relative cost per day. Defaults 5, 7, 3, 4.
- horizon_days: search horizon (days). Default 30.
- class_mass: prior mass fractions over target classes. Defaults flare 0.10, debris 0.35, submerged 0.40, beacon 0.15.

Target-class detectability (POD factor), as a function of elapsed time t (days):
  flare:     d_flare(t) = exp(-24 t / t_flare_h)
  debris:    d_debris(t) = exp(-t / t_debris_d) * 0.1  for t > solas_days
             (SOLAS hard-stop: survival-craft detectability collapses after 30 d)
  submerged: d_submerged(t) = exp(-t / t_sub_d)
  beacon:    d_beacon(t) = 1  for t <= beacon_days, else 0

Spatial prior (POA).
- Target distribution at day t: N( mu_true(t), s(t) ), where
  mu_true(t) = unmodeled_leg + true_drift_v * t   (the true target position)
  s(t) = sigma_lkp + diffuse * sqrt(t)            (1-sigma spread)
- Search region at day t: the drift track box [ mu_modeled(t) - R, mu_modeled(t) + R ], where
  mu_modeled(t) = drift_v * t                      (the prior's drift estimate)
  R = max(3 * sigma_lkp, 0.25 * drift_v * horizon) (fixed sweep half-width)
- POA at day t = integral of N(mu_true(t), s(t)) over the search box
  = 0.5 * [ erf( (hi - mu_true) / (s*sqrt(2)) ) - erf( (lo - mu_true) / (s*sqrt(2)) ) ]
  where lo = max(mu_true - 6 s, mu_modeled - R), hi = min(mu_true + 6 s, mu_modeled + R).
  POA = 0 if hi <= lo (target entirely outside the box).

Per-platform probability of success at day t.
For platform j in {air, radar, mag, sonar} with sensor coverage p_j and detectable-class set C_j:
  POS_j(t) = POA(t) * [ sum over c in C_j of class_mass[c] * w_{j,c} * p_j * d_c(t) ] * cov
  where w_{j,c} is the platform's relative weight on class c (air: debris 1.0, flare 1.0; radar: debris 0.6, flare 0.3; mag: submerged 1.0; sonar: submerged 0.8, beacon 1.0) and cov = 0.5 is the fraction of the region one pass covers.

Time-phased, cost-normalized allocation.
- Phase weight for surface platforms (air, radar): w_surf(t) = 1 - t/horizon (early).
- Phase weight for shipborne platforms (mag, sonar): w_sub(t) = t/horizon (late).
- Effort score for platform j: E_j = sum_t POS_j(t) * w_j(t) / cost_j.
- The platform with the largest E_j per day is the best single-platform choice; the allocation rule is to fly the platform with the largest E_j at each day, and to run one aerial and one shipborne platform concurrently (one in the surface phase, one in the submerged phase).

Solution procedure (implemented in code/search_model.py).
1. Set defaults and any command-line overrides (all constants are CLI parameters).
2. For each day t in [0, horizon]: compute POA(t) by integrating the 1-D Gaussian over the drift-track box.
3. For each platform j: compute POS_j(t) from the class sum and sensor coverage.
4. Apply the time-phased weight and divide by cost to get the effort score E_j.
5. Report per-day POS per platform, the best platform by POS/cost, and the total effort score per platform.
6. Sweep any single parameter over a range (e.g. --sweep unmodeled_leg=0,100,300,600) to study sensitivity.

### Outcome Analysis

Baseline results (defaults, 30-day horizon, correct prior: true_drift_v = drift_v = 30 km/day, unmodeled_leg = 0).

Per-day POS (probability of success for one pass of that platform):
  day  air    radar   mag    sonar
   0  0.0673  0.0239  0.0160  0.0117
   5  0.0306  0.0123  0.0136  0.0104
  10  0.0180  0.0072  0.0116  0.0093
  15  0.0106  0.0043  0.0100  0.0084
  20  0.0063  0.0025  0.0086  0.0076
  25  0.0037  0.0015  0.0074  0.0070
  30  0.0022  0.0009  0.0064  0.0064

Total effort score (sum of POS * phase-weight / cost over 30 days):
  air    0.0771  (best, POS/cost 0.000498)
  radar  0.0216  (POS/cost 0.0000996)
  mag    0.0455  (POS/cost 0.000490)
  sonar  0.0300  (POS/cost 0.000242)

Interpretation.
- Aerial EO/IR is the best single platform on a POS-per-cost basis in the early phase, because it has the highest sensor coverage (0.30) and the surface target classes (flare, debris) carry the largest combined class mass (0.45) and decay fastest, so early effort on them is worth the most.
- The towed magnetometer is a close second (POS/cost 0.000490 vs 0.000498) and becomes the best platform once the prior is corrupted (see below), because its cost (3/day) is the lowest and the submerged class (mass 0.40) decays slowest, so it remains valuable late in the search.
- SAR radar is the worst on POS/cost because it is the most expensive (7/day) and its sensor coverage (0.20) is lower than EO/IR (0.30); it is retained in the fleet for day/night and cloud-cover operation, which the model does not explicitly represent.
- Sonar is the most expensive per unit POS because it detects only the slow-decaying submerged and beacon classes and has the lowest sensor coverage (0.05); it is the long-tail platform for the final 30-day beacon window.

The plan that follows from the allocation: days 0-10, fly aerial EO/IR over the near-LKP drift track (surface phase); days 10-30, transition to shipborne towed magnetometer and sonar over the expanded track (submerged phase). Run one aerial and one shipborne platform concurrently throughout, which the model approximates as the sum of the two best platforms' effort scores.

Limitations and biases.
- The class-mass vector (flare 0.10, debris 0.35, submerged 0.40, beacon 0.15) is a prior belief, not a measurement. A plane that breaks up on impact (more surface debris) or one that sinks intact (less surface debris) would shift the allocation. The model is generic over this, but the default vector is a judgment.
- The decay constants are SAR operational defaults, not derived from the problem text (per Exchange 1). The sensitivity of the allocation to the surface-debris decay constant is studied in Subtask 3.
- The cost figures are relative, not absolute; the allocation rule (maximize POS per unit cost) is scale-invariant, so the relative ranking is robust to the absolute cost scale.
- The model does not represent weather, which degrades aerial sensor coverage (especially EO/IR) and limits ship operation. A realistic plan would re-weight toward SAR radar and sonar in bad weather; the model treats sensor coverage as constant.

## Subtask 2: Subtask 2 -- Study how the search plan and the probability of success depend on the key parameters, in particular the pr

### Problem

Subtask 2 -- Study how the search plan and the probability of success depend on the key parameters, in particular the prior-error parameters that the expert identified in Exchange 3 as the sharpest failure mode: the length of an unmodeled late leg before loss (unmodeled_leg) and the error in the assumed current velocity (true_drift_v vs drift_v). Also study the sensitivity to the LKP positional uncertainty (sigma_lkp) and the surface-debris decay constant (t_debris_d). The goal is to quantify how much the probability of success collapses when the prior is wrong, and to identify which parameters the searchers should invest most in tightening.

### Analysis

The expert's Exchange-3 reply identified the prior as the weak link: a late, large course change or a long unmodeled leg before loss places the bivariate-normal POA in the wrong place, so every POA x POD product is near zero regardless of how well POD and cost are handled. The mechanism is multiplicative in POA, so a wrong prior corrupts the whole objective, not just one term. The sensitivity study is designed to confirm this and to quantify the collapse.

The model implements the prior error in two ways, both of which grow the separation between the search box (centered on the modeled drift mu_modeled(t) = drift_v * t) and the true target (at mu_true(t) = unmodeled_leg + true_drift_v * t):
- The unmodeled_leg parameter shifts the true target off the LKP at t=0 by a fixed distance. This represents a late turn or a long leg the prior did not model.
- The true_drift_v parameter makes the assumed current wrong: the separation grows linearly in time as |true_drift_v - drift_v| * t, so even a small current error becomes a large positional error by day 30.

The POA at day t is the fraction of the target's Gaussian mass inside the drift-track box; as the separation grows, the box leaves the target and POA -> 0. Because POS = POA x POD x cov, the probability of success collapses with the prior error, and the allocation (which platform to fly) can flip as the relative value of the slow-decaying submerged class (detected by the cheap shipborne platforms) grows against the fast-decaying surface class (detected by the aerial platforms).

The study sweeps each parameter over a range while holding the others at defaults, and reports the best platform and the best POS/cost for each value. This isolates the effect of each parameter on the allocation and on the success rate.

### Modeling Process

Sweeps performed (code/search_model.py --sweep NAME=a,b,c):

1. Unmodeled leg: unmodeled_leg in {0, 100, 300, 600} km, all other parameters at defaults (drift_v = true_drift_v = 30, sigma_lkp = 100).
   Result: best POS/cost and best platform:
     leg=0    air    0.000498
     leg=100  air    0.000476
     leg=300  mag    0.000273
     leg=600  mag    0.0000289
   The success rate collapses by a factor of ~17 from leg=0 to leg=600, and the best platform flips from aerial (air) to shipborne (mag) at leg=300. The flip occurs because the unmodeled leg shifts the target off the early drift track, where the aerial platforms are searching; the target is then found, if at all, in the later days when the track has spread to include it, and the cheap shipborne platforms dominate the late phase on a POS/cost basis.

2. Current-velocity error: true_drift_v in {0, 15, 30, 45, 60} km/day, drift_v fixed at 30, unmodeled_leg = 0.
   Result: best POS/cost and best platform:
     true_v=0    air    0.000399
     true_v=15   air    0.000466
     true_v=30   air    0.000498  (correct prior, baseline)
     true_v=45   air    0.000466
     true_v=60   air    0.000399
   The success rate is symmetric in the current error (as expected: the separation |true_v - drift_v| * t depends only on the magnitude of the error, not its sign). A 30 km/day current error (true_v = 0 or 60) reduces the success rate by ~20% relative to the correct prior. The best platform does not flip over this range because the current error grows the separation gradually, not instantly as the unmodeled leg does.

3. LKP positional uncertainty: sigma_lkp in {50, 100, 200, 400} km, unmodeled_leg = 0, correct prior.
   Result: best POS/cost and best platform:
     lkp=50   air    0.000505
     lkp=100  air    0.000498
     lkp=200  mag    0.000528
     lkp=400  mag    0.000540
   The success rate is fairly insensitive to sigma_lkp over this range (within ~8%), and the best platform flips to shipborne at lkp=200. A larger LKP uncertainty spreads the target distribution, so the fixed search box captures a smaller fraction of the mass early on; but the diffusive spread s(t) = sigma_lkp + diffuse*sqrt(t) also grows, which partially offsets the effect. The net result is a mild sensitivity and a late-phase flip to the cheap shipborne platforms, which benefit from the larger search area they can cover.

4. Surface-debris decay: t_debris_d in {5, 10, 20} days, all other parameters at defaults.
   Result: best POS/cost and best platform:
     decay=5    mag    0.000490
     decay=10   air    0.000498
     decay=20   air    0.000674
   A faster-decaying surface class (decay=5) shifts the best platform to shipborne (mag), because the surface class is gone early and the slow-decaying submerged class dominates. A slower-decaying surface class (decay=20) makes the aerial platform (air) clearly better and raises the success rate by ~35% relative to decay=10, because the early surface phase is worth more. This confirms the time-phased allocation: the value of the early aerial effort is directly proportional to how long the surface debris remains detectable.

Solution procedure. Each sweep is a single command that re-runs the model over the parameter range and reports the best platform and best POS/cost for each value. The model code is unchanged across sweeps; only the command-line constant changes.

### Outcome Analysis

The sensitivity study confirms the expert's Exchange-3 diagnosis: the prior is the weak link, and the two prior-error parameters (unmodeled_leg and true_drift_v) are the ones that collapse the probability of success.

Key findings.
- The unmodeled leg is the sharpest failure. A 600 km unmodeled leg (a late turn or a long leg the prior did not model) reduces the best POS/cost by a factor of ~17 relative to the correct prior, and flips the best platform from aerial to shipborne. This is the case the expert identified as 'more severe because it corrupts the prior itself rather than only the drift term.' The model reproduces this: the target is off the early drift track, so the aerial platforms searching that track find nothing, and only the later, wider track (where the cheap shipborne platforms dominate on POS/cost) has a chance.
- The current-velocity error is the second failure mode, and it is symmetric: a 30 km/day error in either direction reduces the success rate by ~20%. Because the separation grows linearly in time, a small current error becomes a large positional error by day 30. This is why the expert's reply named 'a strong time-variable current advecting debris outside the diffusion ellipse' as the same total failure, though less severe than the LKP case: a constant current error is a fixed offset in the drift term, while a time-variable current is a growing offset.
- The LKP positional uncertainty is a mild parameter: the success rate varies by only ~8% over sigma_lkp = 50 to 400 km. The searchers should tighten the LKP, but it is not the dominant failure.
- The surface-debris decay constant is a strong parameter for the allocation: a faster-decaying surface class shifts the best platform to shipborne, and a slower-decaying one makes the aerial platform clearly better and raises the success rate by ~35%. This confirms the time-phased allocation and tells the searchers that the value of the early aerial effort depends directly on how long the surface debris remains visible.

Implications for the search plan.
- The searchers should invest most in tightening the prior: the unmodeled leg and the current-velocity estimate. Concretely, this means (a) reconstructing the last-known flight path as precisely as possible (ADS-B, radar, satellite tracks) to bound the unmodeled leg, and (b) using the best available ocean-current model for the region to bound the drift velocity. These two investments reduce the dominant failure modes directly.
- The LKP uncertainty is worth tightening, but it is a second-order effect.
- The surface-debris decay constant should be estimated from the aircraft type and the sea state: a plane that breaks up on impact produces more long-lived surface debris, which raises the value of the early aerial effort. The model is generic over this; the airline should feed in the expected surface-debris fraction for the specific aircraft type.
- The allocation flips to shipborne platforms as the prior is corrupted. This is a useful diagnostic: if the searchers have a good prior, the aerial platforms dominate the early phase; if the prior is poor, the cheap shipborne platforms dominate, and the searchers should reallocate effort accordingly rather than continuing to fly the aerial platforms over a track that does not contain the target.

## Subtask 3: Subtask 3 -- Identify and analyze the failure modes of the model, in particular the one the expert identified in Exchang

### Problem

Subtask 3 -- Identify and analyze the failure modes of the model, in particular the one the expert identified in Exchange 3 as the sharpest: a late, large course change or a long unmodeled leg before loss that places the POA in the wrong place, so every POA x POD product is near zero regardless of how well POD and cost are handled. Also analyze the second failure mode (a strong time-variable current advecting debris outside the diffusion ellipse) and the model's biases (the class-mass prior, the decay constants, the cost scale, the absence of weather effects). The goal is to state plainly where the model breaks, why it breaks, and what the searchers can do about it.

### Analysis

The model's failure modes are structural, not numerical. They arise from the multiplicative structure of the objective (POS = POA x POD x cov) and from the fact that the POA is a parametric prior (a Gaussian centered on the LKP plus modeled drift) that can be wrong in a way the model cannot detect from its own outputs.

The sharpest failure (Exchange 3): a wrong prior.
If the true target is not where the prior says it is -- because of an unmodeled late leg (the aircraft turned after the last known position) or because the assumed current velocity is wrong -- the search box is centered on the wrong place, and the POA (the fraction of the target's mass inside the box) drops toward zero. Because POS = POA x POD x cov, every platform's probability of success collapses at once, and the cost-normalized allocation (which platform to fly) is computed on the collapsed values. The model cannot detect this from its own outputs: a low POS/cost is indistinguishable, in principle, from a prior that is simply in a low-probability region. This is the fundamental limitation of any parametric-prior search model, and it is why the expert named it the sharpest failure: it corrupts the prior itself, not just one term.

The second failure: a strong time-variable current.
A time-variable current (a jet, a meander, a sudden shift) advects the debris at a velocity that is not the constant drift_v the prior assumes. The separation between the box and the target grows as the integral of the current error over time, which for a time-variable current can be larger than for a constant error of the same average magnitude. The model represents this as a constant true_drift_v offset, which captures the constant-error case exactly and the time-variable case approximately (as an average). The model does not represent the variance of a time-variable current, which would widen the target distribution and partially offset the positional error.

Biases.
- Class-mass prior: the mass fractions (flare 0.10, debris 0.35, submerged 0.40, beacon 0.15) are a judgment, not a measurement. A plane that breaks up on impact (more surface debris) or one that sinks intact (less surface debris) would shift the allocation. The bias is in the allocation, not in the structure.
- Decay constants: the surface-debris and submerged-wreckage decay constants are SAR operational defaults, not derived from the problem text (per Exchange 1). The sensitivity study (Subtask 2) shows the allocation is sensitive to the surface-debris decay constant: a faster-decaying class shifts the best platform to shipborne. The bias is in the phase boundary (when to switch from aerial to shipborne), not in the overall structure.
- Cost scale: the cost figures are relative. The allocation rule (maximize POS per unit cost) is scale-invariant, so the relative ranking of platforms is robust to the absolute cost scale. The bias is in the absolute success rate, not in the allocation.
- Absence of weather: the model treats sensor coverage as constant. In practice, bad weather degrades aerial EO/IR coverage (the highest-coverage platform) and limits ship operation, so a realistic plan would re-weight toward SAR radar and sonar in bad weather. The model does not represent this, so its allocation is biased toward aerial platforms in the early phase.

What the searchers can do about the failure modes.
- The model cannot correct a wrong prior. The mitigation is to invest in the steps that tighten the prior itself, which is what the non-technical airline paper (Subtask 4) recommends: reconstruct the last-known flight path precisely (ADS-B, radar, satellite tracks) to bound the unmodeled leg, and use the best available ocean-current model to bound the drift velocity. These two investments reduce the dominant failure modes directly.
- The model can detect a prior that is wrong in a particular way: if the searchers have an independent estimate of the current velocity (from ocean models) that differs from the drift_v they used, the model can be re-run with the corrected true_drift_v, and the change in POS/cost tells them how much the prior error mattered. This is a posterior diagnostic, not a correction: it tells them the prior was wrong, but it does not tell them the right prior.
- The time-phased allocation is robust to the failure modes in the sense that it always reallocate to the platform with the best POS/cost at each day. When the prior is corrupted, the allocation flips to the cheap shipborne platforms, which is the correct response: if the aerial platforms are searching a track that does not contain the target, the searchers should stop flying them and move to the platforms that can cover the larger, later track.

### Modeling Process

Failure-mode analysis.

1. Wrong prior (sharpest failure).
Let the true target position at day t be mu_true(t) = L + v_true * t, where L is the unmodeled leg and v_true is the true current. Let the prior's estimate be mu_modeled(t) = v_assumed * t (the prior assumes the target started at the LKP, L=0, and drifted at v_assumed). The separation is
  delta(t) = |mu_true(t) - mu_modeled(t)| = |L| + |v_true - v_assumed| * t  (in the 1-D along-track approximation).
The search box at day t has half-width R = max(3*sigma_lkp, 0.25*drift_v*horizon). The POA is the fraction of N(mu_true(t), s(t)) mass inside the box, where s(t) = sigma_lkp + diffuse*sqrt(t). As delta(t) grows relative to s(t) and R, the POA drops toward zero. The probability of success for platform j at day t is
  POS_j(t) = POA(t) * [class sum]_j * p_j * cov,
so it collapses with the POA. The cost-normalized effort score E_j = sum_t POS_j(t) * w_j(t) / cost_j collapses with it, and the allocation (argmax_j E_j) is computed on the collapsed values.

The POA as a function of the separation delta(t), for a fixed s(t) and R, is
  POA = 0.5 * [ erf( (R - delta) / (s*sqrt(2)) ) - erf( (-R - delta) / (s*sqrt(2)) ) ]  (when the box is centered at the prior's estimate and the target is at distance delta).
For delta >> R + s, POA ~ 0. For delta << R - s, POA ~ 1. The transition is sharp: the POA drops from ~1 to ~0 over a separation range of order s + R. This is why the failure is so severe: a prior error of a few hundred km (comparable to s + R) collapses the POA, and the model has no way to recover.

2. Time-variable current (second failure).
If the current is time-variable, v_true(t), the true target position is mu_true(t) = L + integral_0^t v_true(t') dt'. The separation is
  delta(t) = |L + integral_0^t (v_true(t') - v_assumed) dt'|.
For a time-variable current, the integral can be larger than for a constant current error of the same average magnitude, because the current can push the debris in one direction and then another, accumulating a net displacement. The model represents this as a constant true_drift_v offset, which captures the constant-error case exactly and the time-variable case as an average. The model does not represent the variance of the time-variable current, which would widen the target distribution (increase s(t)) and partially offset the positional error. This is a known limitation: the model is conservative in the sense that it does not credit the searchers for the extra spread a time-variable current would produce, but it is also blind to the case where the time-variable current produces a net displacement larger than the constant-error case.

3. Bias analysis.
- Class-mass prior: the allocation is proportional to the class-mass vector. A change in the class-mass vector (e.g. more surface debris for a plane that breaks up) shifts the allocation toward the platforms that detect that class. The structure is unchanged; the allocation moves.
- Decay constants: the phase boundary (when to switch from aerial to shipborne) is set by the relative decay rates of the surface and submerged classes. A faster-decaying surface class moves the boundary earlier; a slower-decaying one moves it later. The overall structure (early aerial, late shipborne) is robust; the boundary moves.
- Cost scale: the allocation rule is scale-invariant (maximize POS per unit cost), so the relative ranking of platforms is robust to the absolute cost scale. Only the absolute success rate changes with the cost scale.
- Absence of weather: the model treats sensor coverage as constant. In bad weather, the aerial EO/IR coverage (the highest, 0.30) would drop, and the allocation would shift toward SAR radar (0.20, works in cloud) and sonar (0.05, unaffected by weather). The model does not represent this, so its early-phase allocation is biased toward aerial platforms.

### Outcome Analysis

The model's failure modes are structural and are dominated by the prior error. The key results are:

- The unmodeled leg is the sharpest failure. A 600 km unmodeled leg reduces the best POS/cost by a factor of ~17 and flips the best platform from aerial to shipborne. This is the case the expert identified as 'more severe because it corrupts the prior itself.' The model reproduces this exactly: the target is off the early drift track, so the aerial platforms find nothing, and only the later, wider track (where the cheap shipborne platforms dominate on POS/cost) has a chance.

- The current-velocity error is the second failure mode, and it is symmetric. A 30 km/day error in either direction reduces the success rate by ~20%. The model captures the constant-error case exactly and the time-variable case approximately (as an average). The model is blind to the variance of a time-variable current, which would widen the target distribution and partially offset the positional error.

- The LKP positional uncertainty is a mild parameter: the success rate varies by only ~8% over sigma_lkp = 50 to 400 km. The searchers should tighten the LKP, but it is not the dominant failure.

- The surface-debris decay constant is a strong parameter for the allocation: a faster-decaying surface class shifts the best platform to shipborne, and a slower-decaying one makes the aerial platform clearly better and raises the success rate by ~35%. This confirms the time-phased allocation.

The model's biases are in the allocation (class-mass prior, decay constants, absence of weather), not in the structure. The structure (POA x POD, cost-normalized, time-phased) is robust to these biases: it always reallocate to the platform with the best POS/cost at each day, and it flips to the cheap shipborne platforms when the prior is corrupted, which is the correct response.

The searchers cannot use the model to correct a wrong prior -- the model cannot detect a wrong prior from its own outputs. The mitigation is to invest in tightening the prior itself: reconstruct the last-known flight path precisely (ADS-B, radar, satellite tracks) to bound the unmodeled leg, and use the best available ocean-current model to bound the drift velocity. This is the recommendation in the non-technical airline paper (Subtask 4). The model can also be used as a posterior diagnostic: if the searchers have an independent estimate of the current velocity that differs from the one they used, they can re-run the model with the corrected value and see how much the POS/cost changed, which tells them how much the prior error mattered.

## Subtask 4: Subtask 4 -- Prepare a 1-2 page non-technical paper for the airlines to use in their press conferences concerning their 

### Problem

Subtask 4 -- Prepare a 1-2 page non-technical paper for the airlines to use in their press conferences concerning their plan for future searches. The paper must explain, in plain language, how the search is planned, what the model does, what the main uncertainties are, and what the airline and the searchers are doing to reduce those uncertainties. It must be honest about the limits of the model (the prior is the weak link) without undermining public confidence in the search effort.

### Analysis

The non-technical paper is a communication deliverable, not a modeling deliverable. Its purpose is to let the airline explain its search plan to the public, the media, and the families of the missing, in plain language, without making promises the model cannot keep. The paper must be honest about the model's limits (the prior is the weak link, the search can fail even with a perfect plan) while making clear that the searchers are doing everything they can to tighten the prior and to allocate the search effort where it is most likely to succeed.

The paper is structured as follows: (1) What we are looking for and why it is hard. (2) How we plan the search: the probability-of-success framework, the spatial prior, the different sensors. (3) The main uncertainties: the last-known position, the ocean currents, how long the debris stays visible. (4) What we are doing to reduce those uncertainties. (5) An honest statement of the limits.

The paper uses no formulas and no technical terms beyond 'probability,' 'ocean current,' and 'sensor.' It explains the POA x POD framework as 'we divide the search area into sections, estimate how likely the plane is in each section, and how likely each sensor is to find it, and we fly the sensors where the product of those two numbers is highest.' It explains the time-phased allocation as 'we search for floating debris early, when it is most visible, and for the sunken wreckage later, when the floating debris is gone.' It explains the prior-error failure as 'if our estimate of where the plane is is wrong, the search can miss it even with the best sensors; this is why we work hard to pin down the last-known position and the ocean currents.'

### Modeling Process

The paper is written in plain English, 1-2 pages, with the following structure and key points.

Title: 'How We Plan the Search for a Lost Aircraft'

Section 1 -- What we are looking for, and why it is hard.
A plane that goes down in the open ocean leaves no signal. We must find the wreckage, or the parts of it that float, using aircraft and ships with different sensors. The ocean is vast, the currents move the debris, and the debris sinks and degrades over time. The search is a race against time: the longer we wait, the harder it is to find the floating parts, and the search area we must cover grows as the currents spread the debris.

Section 2 -- How we plan the search.
We divide the search area into sections. For each section, we estimate two numbers: (1) how likely the plane is to be in that section, based on where we last knew it to be and how the currents have moved since; and (2) how likely our sensors are to find it if it is there, based on the type of sensor (aircraft with cameras, aircraft with radar, ships with magnetic detectors, ships with sonar) and the type of debris (floating, sunken, or the black-box beacon). We multiply those two numbers to get the chance of success in that section, and we fly the sensors where that product is highest, per unit of cost. We search for floating debris early, when it is most visible, and for the sunken wreckage later, when the floating debris is gone. We use different aircraft and ships because no single sensor is best for everything: cameras see floating debris but not sunken wreckage; radar works in cloud and at night; magnetic detectors and sonar find sunken wreckage.

Section 3 -- The main uncertainties.
There are three main uncertainties. First, where the plane went down: we know the last position where we had a signal, but the plane may have turned or continued flying for some time after that, and we may not know exactly how long. Second, how the currents have moved the debris: the ocean currents in the region are not perfectly known, and a small error in the current speed becomes a large error in the debris position after many days. Third, how long the debris stays findable: floating debris sinks and degrades over days to weeks; the black-box beacon has a battery that lasts about 30 days.

Section 4 -- What we are doing to reduce the uncertainties.
We reconstruct the last-known flight path as precisely as possible, using all available data (satellite, radar, and aircraft reports), to bound how far the plane could have flown after the last known position. We use the best available ocean-current model for the region to estimate how the currents have moved the debris, and we update the model as new current data becomes available. We use the right sensors at the right time: cameras early, when the floating debris is most visible; magnetic detectors and sonar later, for the sunken wreckage. We keep the search area as small as the data allows, because a smaller area is easier to cover thoroughly.

Section 5 -- An honest statement of the limits.
We want to be clear about the limits of this approach. If our estimate of where the plane is is wrong -- if the plane turned after the last known position, or if the currents moved the debris in a direction we did not expect -- the search can miss it even with the best sensors and the best plan. No search plan can guarantee a find; the probability of success depends on how well we know where the plane is, and that is the hardest part. We are doing everything we can to tighten that estimate, and we will keep updating the search plan as we learn more. We understand how important this is, and we are committed to searching as long and as thoroughly as the evidence warrants.

### Outcome Analysis

The paper is 1-2 pages of plain English, structured as above. It explains the search plan, the main uncertainties, and what the searchers are doing to reduce them, and it is honest about the model's limits without undermining public confidence. The key message is: the search is planned to maximize the chance of success per unit of effort, using the best available estimate of where the plane is; the main risk is that that estimate is wrong, and the searchers are working to tighten it; no search can guarantee a find, but the plan is the best available and it is updated continuously.

The paper is appropriate for a press conference: it is clear, honest, and does not make promises the model cannot keep. It does not use technical terms beyond 'probability,' 'ocean current,' and 'sensor.' It does not quote specific numbers (the probability of success, the search area, the number of aircraft), because those depend on the specific case and would be misleading in a general press statement. It focuses on the approach and the uncertainties, which are the same for any lost-aircraft search over open water.

The paper is consistent with the model: the POA x POD framework is explained as 'how likely the plane is in each section times how likely the sensors are to find it'; the time-phased allocation is explained as 'floating debris early, sunken wreckage later'; the prior-error failure is explained as 'if our estimate is wrong, the search can miss it.' The paper does not mention the specific decay constants, the class-mass vector, or the cost figures, because those are case-specific and would be misleading in a general statement.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
