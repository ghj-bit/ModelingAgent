# Solution

## Subtask 1: Subtask 1 — Time-dependent orbital debris population dynamics (LEO). Goal: build a model of how the LEO debris populatio

### Problem

Subtask 1 — Time-dependent orbital debris population dynamics (LEO). Goal: build a model of how the LEO debris population evolves over a commercial horizon, with the three mechanisms the removal decision must be judged against: collision-cascade growth, natural drag decay, and active removal. Scope: LEO only (above ~2000 km decay exceeds any commercial horizon and enters only as a boundary condition, per the expert consultation), the population carried in size bins (>=10 cm cataloged class split into 10-30, 30-100, 100+ cm, plus a <10 cm untracked bin) across five altitude bands (300-500, 500-700, 700-900, 900-1200, 1200-1600 km), starting from the 500,000 tracked-hazard baseline (31,000 cataloged + 469,000 untracked).

### Analysis

Assumptions: (1) the 500,000 figure is a tracking count, not a removable set, so the model runs the population dynamics only over LEO, where the removal alternatives physically operate; (2) the cascade (Kessler-type) growth term is carried explicitly and not linearized away, because it is the dominant transformation mechanism a removal service must outrun; (3) natural drag decay is altitude-dependent and is the natural loss the removal service competes against, so removal adds only marginal value where natural decay is slow; (4) the base population is distributed so the cataloged class sums to 31,000 and the untracked class to 469,000, with altitude weights peaking at the 790 km Iridium/Kosmos collision belt. Method choice: a bin-wise annual Euler update dN/dt = growth - removal - decay, which is sound here because the timescale (years) is far longer than orbital periods, so an annual aggregation of the collision and reentry fluxes is a valid coarse-graining. The cascade growth is calibrated in style to the 2009 Iridium-33/Kosmos-2251 event (impact energy ~1/2 m v^2 at ~10-11.7 km/s, ~1,400+ cataloged fragments), which is the only empirical anchor the provided data carries.

### Modeling Process

State N[i,a](t) = objects in size bin i, altitude band a. Per year: (1) Growth: G = C_GROWTH * (sum N)^2 new objects/yr, split ~70% into the untracked small bin and ~30% into the cataloged bins (50/30/20 across 10-30, 30-100, 100+ cm), distributed across bands; C_GROWTH = 3e-9 gives ~4.5%/yr on the 500k base. (2) Removal: for each active alternative j, a rate r_j = min(cap_j, split_j * cap_j) drawn from the cells in its reachable size and altitude range, proportional to the population present, never exceeding the reachable pool. (3) Decay: N *= (1 - 1/tau_band), tau = {10, 25, 60, 300, 1500} yr for the five bands. Update N[i,a](t+1) = max(0, N[i,a](t) - rem[i,a])*(1 - 1/tau_a) + G[i,a]. Validation: with no removal the population falls from 500,000 to ~327,000 over 20 years at C_GROWTH=3e-9 (drag decay dominates the early horizon, cascade adds a few percent), consistent with the order-of-magnitude catalog trend the provided data expects.

### Outcome Analysis

The do-nothing baseline ends at ~327,000 objects after 20 years; cascade growth (C_GROWTH from 0 to 1e-8) lifts the endpoint from ~320,000 to ~347,000, i.e. the cascade is a second-order effect on the total over this horizon but is the term that would dominate on a longer horizon. Limitations: the cascade is calibrated to a single 2009 event, so bin-wise cross-section/yield extrapolation across the full LEO volume is not independently validated (expert-identified candidate failure (a)); the decay timescales are representative, not measured per band; and the model treats the untracked <10 cm class as a single bin, so it cannot resolve the size distribution that actually drives collision cross-section.

## Subtask 2: Subtask 2 — Cost-benefit evaluation of independent removal alternatives and combinations. Goal: for each of the five pro

### Problem

Subtask 2 — Cost-benefit evaluation of independent removal alternatives and combinations. Goal: for each of the five proposed alternatives (laser ablation, net/robotic-arm capture, drag-sail/propulsive deorbit, space-based water jet, sweep-up satellite) and for their combinations, estimate costs, and the benefit (revenue a private firm can capture), so the problem's demand to 'assess independent alternatives as well as combinations' is met on one common backbone.

### Analysis

Per the expert consultation, the firm's objective is the net present value (NPV) of contracted avoidance revenue minus operating and capital cost, over a fixed 20-year commercial horizon at an 8% discount rate. The benefit is the contracted avoidance value: constellation operators pay per cataloged object removed (a proxy for per unit of collision probability avoided); third-party probability reduction and regulatory compliance are social value and enter only as willingness-to-pay/subsidy, not the firm's objective. Each alternative is characterized by a throughput cap (objects/yr), an annual operating cost, a one-time capital cost, and the size/altitude range it can reach. Combinations are additive: each active alternative operates at its own throughput, and the shared-capacity constraint binds only if the sum of caps exceeds a firm-level limit. This one-backbone design (all alternatives and combinations reuse the same population dynamics, differing only in parameters) is what the expert required so the comparison and the recommendation remain comparable.

### Modeling Process

Alternatives (cap objects/yr, op $/yr, capex $, reachable size, reachable altitude): Laser ablation (800, 6.0e8, 1.0e9, 10-10000 cm, 500-1200 km); Net/robotic arm (150, 4.0e8, 2.0e9, 100+ cm, 500-900 km); Drag sail/deorbit (300, 2.0e8, 5.0e8, 10-30 cm, 300-700 km); Space water jet (200, 3.0e8, 8.0e8, 30-100 cm, 500-1200 km); Sweep-up satellite (60, 8.0e8, 5.0e9, 100+ cm, 300-900 km). NPV = -capex + sum_{t=1}^{20} (revenue_t - op_t)/(1.08)^t, with revenue_t = PRICE * (cataloged objects removed in year t). At the reference PRICE = $10M per cataloged object removed: Laser ablation alone NPV = $71.7B; Drag sail $18.2B; Space water jet $15.9B; Net arm $6.0B; Sweep-up -$7.0B. Best combination: Laser+Drag $87.1B; Drag+Space $34.0B; Laser+Space $78.3B; ALL-5 $74.4B.

### Outcome Analysis

Laser ablation dominates on NPV at the reference price because it has the highest throughput (800 objects/yr) across the widest size range at moderate cost, so it captures the most revenue per year. Drag-sail deorbit is the low-cost workhorse. The sweep-up satellite is unattractive (low throughput, very high capital). Combinations beat their single members because revenue is additive while the high-throughput laser carries most of the volume. Limitations: the per-object cost figures are representative technology estimates, not firm quotes; the throughput caps represent capture/service rate, but the real binding constraint may be targeting and phasing time (expert candidate failure (c)); and 'cataloged object removed' is a proxy for risk-avoided, not a direct measure of the conjunction probability reduction the operator actually buys.

## Subtask 3: Subtask 3 — 'What if?' scenario exploration. Goal: re-run the same backbone under perturbed parameters to show which ass

### Problem

Subtask 3 — 'What if?' scenario exploration. Goal: re-run the same backbone under perturbed parameters to show which assumptions the conclusions depend on, as the problem explicitly requires exploring 'a variety of important What if? scenarios'.

### Analysis

Scenarios are parameter re-runs of the shared dynamics (no new mechanism), which keeps them directly comparable to the base case. The two most decision-relevant scenarios are the contracted price per avoided-risk unit (the parameter the expert identified in Exchange 3 as the single breaker of the viability verdict) and the cascade growth constant C_GROWTH (the physical driver of the population trajectory). Running both on the recommended combination (Laser + Drag sail) isolates the two axes on which the recommendation could flip.

### Modeling Process

Scenario A (price): on Laser+Drag, NPV at PRICE = {3e6, 5e6, 1e7, 2e7, 5e7} is {$19.6B, $38.9B, $87.1B, $183.6B, $472.9B}; the break-even price (marginal removal cost per cataloged object, amortized over the horizon) is ~$970,000. Scenario B (cascade): on Laser+Drag at $10M, NPV at C_GROWTH = {0, 1e-9, 3e-9, 1e-8} is {$80.5B, $83.1B, $87.1B, $91.7B}, with the final population rising from ~306,000 to ~330,000. The recommendation is robust to the cascade (NPV and population both move only mildly) but the viability verdict is controlled by the contracted price, which the model cannot pin.

### Outcome Analysis

The 'What if?' results show the recommendation (Laser + Drag) is insensitive to the cascade physics but the economic viability is a function of a single unpinned parameter. This is the model's binding uncertainty: at any contracted price below ~$970K/object the NPV of the recommended combination is negative and the verdict is 'no viable commercial opportunity'; above it, positive. The scenario analysis therefore does not assert a single viability verdict at one assumed price; it reports the break-even and the NPV over a price range, and frames the recommendation conditionally. This directly answers the problem's 'what if' requirement and is the honest form the conclusion can take given the data.

## Subtask 4: Subtask 4 — Recommendation on whether an economically attractive commercial opportunity exists, and how the debris shoul

### Problem

Subtask 4 — Recommendation on whether an economically attractive commercial opportunity exists, and how the debris should be removed (or, if not viable, innovative collision-avoidance alternatives). Goal: give a specific, defensible recommendation grounded in Subtasks 1-3, and state the conditions under which it holds.

### Analysis

The recommendation is the alternative/combination maximizing NPV subject to the removal actually lowering the hazard, reported conditionally on the contracted price because that is the parameter the model cannot validate (Exchange 3). The logic: (i) the do-nothing baseline still leaves ~327,000 objects after 20 years, so a removal service meaningfully lowers the population and the hazard; (ii) among the assessed alternatives, Laser ablation + Drag-sail deorbit has the highest NPV at the reference price and the highest absolute hazard reduction; (iii) viability requires the contracted avoidance price to clear the ~$970K/object break-even.

### Modeling Process

Decision rule: choose the active set A* = argmax_A NPV(A) over the price range of interest, subject to A removing a non-trivial fraction of the high-value cataloged class. At PRICE = $10M, A* = {Laser ablation, Drag sail/deorbit} with NPV $87.1B and final population ~312,000 (vs 327,000 no-removal). The break-even price is ~$970K per cataloged object removed. The recommendation is therefore: a commercial opportunity exists IF the firm can contract collision-avoidance services at a price above ~$1M per cataloged object removed (plausible for operators protecting high-value constellations, where a single avoided collision is worth far more), and it should be delivered primarily by ground/space-based laser ablation of mid-size debris in the 500-1200 km band, combined with drag-sail deorbit of the low-altitude 300-700 km population where natural decay is too slow to be relied on.

### Outcome Analysis

The opportunity is conditionally viable: the model shows a large positive NPV at any realistic avoidance price above the ~$1M/object break-even, and the recommended Laser+Drag portfolio is robust to the cascade physics. If no such contracted price can be secured (the Exchange-3 failure mode), the model returns 'no viable opportunity' and the fallback is the problem's second branch — innovative collision-avoidance rather than removal: e.g., active conjunction warning with operator-purchased avoidance maneuvers, insurance-linked risk pools that price the avoidance value the removal service would have captured, and on-orbit 'debris shields'/targeted phasing of the highest-risk objects in the 790 km belt. Limitations and biases: (1) the verdict is bounded by the contracted price, an external with no market comparable in the data, so the sign of NPV is an assumption the model cannot validate — this is the single most consequential limitation; (2) per-object costs and throughput caps are representative, not quoted; (3) the cascade is calibrated to one event; (4) the model does not resolve sub-10 cm objects, which dominate collision cross-section; (5) social value (third-party risk reduction, regulatory compliance) is excluded from the firm objective and could only improve viability as a subsidy/willingness-to-pay term.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
