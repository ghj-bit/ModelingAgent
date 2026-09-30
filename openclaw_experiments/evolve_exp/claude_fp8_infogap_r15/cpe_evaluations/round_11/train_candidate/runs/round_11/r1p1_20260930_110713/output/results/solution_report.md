# Solution

## Subtask 1: Determine the shape, size, and merging pattern of the post-barrier fan-in area in which vehicles converge from B tollboo

### Problem

Determine the shape, size, and merging pattern of the post-barrier fan-in area in which vehicles converge from B tollbooth egress lanes to L travel lanes (B > L), incorporating accident prevention, throughput at the plaza exit, and construction cost. Scope: a general parametric design in (L, B, s) for one direction of travel, with the stated domain B/L in [2, 3]; the fan-out and the barrier itself are out of scope.

### Analysis

Assumptions (declared per the expert, who confirmed the statement leaves them open): (1) throughput is a performance measure of the chosen design, reported for light (30% of L-lane capacity) and heavy (95% of L-lane capacity) traffic — it is not a feasibility gate requiring the plaza to carry full L x 2,200 pc/h, since the problem asks whether better solutions exist rather than validating an implemented design; (2) the fan-in picture is well-posed only for a bounded ratio B/L in [2, 3] (outside it the facility degenerates to a different type — a scope limitation, not a data claim); (3) accident prevention is realized through the structure of the merge mechanism (weave-free, ordered single merges, merge-angle cap) rather than through an invented numeric conflict threshold the text does not carry. Modeling approach: the fan-in has one structural degree of freedom, its length s, because the merging pattern is fixed as weave-free ordered single merges (inner booth lanes merge first) — this is the accident-prevention mechanism and it is what the problem's 'merging pattern' asks to be determined. Booth mix and autonomous-vehicle share do not change the merge structure; they enter only as per-booth service rates and headway-variance parameters. Method soundness: a constrained single-parameter design space (s, with a hard geometric merge-angle cap) keeps the problem analytically tractable and makes the cost/throughput/accident trade explicit, as the problem requires.

### Modeling Process

Geometry. Booths numbered 1..B inner to outer; K = B - L merges. Convergence half-width delta = (B-L)/2 * W_L with W_L = 3.66 m (12 ft); merge angle theta(s) = arctan(delta / s). Merge k takes the outer lane of the current stream into lane k; all merges share theta(s). Merge capacity C_m(theta) = C_L / (1 + k_c * theta^2), C_L = 2,200 pc/h (HCM), k_c = 0.0025/deg^2 (C_m = C_L at 20 deg typical, half at 40 deg). Plaza-exit throughput T(s) = L*C_L / (1 + (B-L)*(1 - C_m/C_L)), saturating at L*C_L. Cost C(s) = W_pav * 0.5*(w_0 + w_1)*s + W_row * s * 0.5*(w_0 - w_1), w_0 = B*W_L, w_1 = L*W_L, W_pav = $6/m^2, W_row = $1 per m of extra ROW per m of length (normalized units). Accident exposure A(s) = (B-L)*(theta/20deg)^2 (one conflict point per eliminated lane, weave-free). Weighted objective over s: min O(s) = w_c*C(s)/C_ref + w_a*A(s)/A_ref - w_t*T(s)/(L*C_L), baseline weights (w_c, w_a, w_t) = (0.4, 0.35, 0.25). Hard constraint: theta(s) <= 30 deg. Solution procedure: grid minimize O(s) over s in [50, 2000] m subject to the angle cap (code/model.py, parameterized, sweepable).

### Outcome Analysis

Baseline B = 8, L = 3: s_opt = 206 m, theta = 2.5 deg, T = 6,114 veh/h (92.2% of L*C_L = 6,600), cost = $2.68e4 (normalized), accident exposure = 0.081, angle cap inactive. Length sweep: s = 50 m gives 48.6% of capacity, 10.4 deg angle, exposure 1.34; s = 400 m gives 97.9%, 1.3 deg, exposure 0.021; s = 2000 m gives 99.9% at 4x the cost of the optimum — a sharp diminishing-returns knee near 200-400 m, so the optimal fan-in is short and wide-angled, not the long tapers commonly in use (this is the 'better solution than common practice' the problem asks for). Light traffic (1,980 veh/h): merge utilization 0.005, delay factor 0.005 — free-flow through the plaza. Heavy traffic (6,270 veh/h): utilization 0.015, delay factor 0.015 — still far from saturation because the ordered weave-free merges keep conflict exposure low at s_opt. Limitations: (a) the aggregate ordered-merge throughput formula is a capacity scaling, not a simulation — per-vehicle gap-acceptance variability is not modeled; (b) cost constants are normalized, so the dollar magnitude is indicative, not budget-grade; (c) the 30 deg angle cap and the B/L in [2,3] domain are declared structural choices (expert-confirmed as not carried by the text), so designs outside them are unvalidated; (d) single-direction analysis — the opposing direction is symmetric and unmodeled interactions across the median are ignored.

## Subtask 2: Determine the performance of the solution in light and heavy traffic. Scope: demand regimes and the resulting throughput

### Problem

Determine the performance of the solution in light and heavy traffic. Scope: demand regimes and the resulting throughput, delay, and utilization of the fan-in at the plaza exit for the baseline design.

### Analysis

Light traffic is defined as demand at 30% of L-lane capacity (free-flow regime, density well below the HCM ~45 pc/mi/ln capacity density); heavy traffic as 95% of L-lane capacity (near-capacity operation). Both are computed for the baseline design (s_opt = 206 m, B = 8, L = 3) using the merge-utilization and delay-factor forms of the gap-acceptance model. The regime split is the standard HCM light/heavy dichotomy referenced by the external data (HCM 6th ed. basic-segment performance).

### Modeling Process

Demand D = f * L * C_L with f in {0.30, 0.95}. Merge utilization at the fan-in: u = (D/(L*C_L)) * (1 - C_m(theta)/C_L), where C_m(theta) is the per-merge capacity at the design angle. Delay factor (M/M/1-type scaling): d = u/(1-u). Throughput capacity of the plaza exit is T(s_opt) from Task 1.

### Outcome Analysis

At s_opt = 206 m (theta = 2.5 deg): light traffic D = 1,980 veh/h gives u = 0.005, d = 0.005 — negligible delay, the fan-in is invisible to free-flow traffic. Heavy traffic D = 6,270 veh/h gives u = 0.015, d = 0.015 — still well below saturation because the short, ordered, weave-free merge sequence keeps the conflict-loss term (1 - C_m/C_L) small at theta = 2.5 deg. The plaza is not the binding constraint in either regime at the baseline design; the binding constraint is the L-lane capacity itself. Limitations: the delay factor is a scalar proxy, not a time-varying queue simulation; platoon effects from booth discharge cycles (bursts as booths open) are not captured, so heavy-traffic delay is likely understated; the 95% heavy demand is a fixed fraction, not a stochastic demand process.

## Subtask 3: Determine how the solution changes as more autonomous (self-driving) vehicles are added to the traffic mix. Scope: the e

### Problem

Determine how the solution changes as more autonomous (self-driving) vehicles are added to the traffic mix. Scope: the effect of the AV share on booth service, fan-in throughput, and the recommended design.

### Analysis

Assumption (declared): AVs use non-stop ETC-class transponder service (1,200 veh/h per booth, per external data item 1) and exhibit reduced headway variance, which raises merge utilization. The AV share replaces service at the slowest booths first (inner conventional booths are the first to be automated). The merge structure (weave-free ordered merges) is unchanged by AVs — they change the queue parameters, not the geometry, consistent with the structure accepted in the expert exchange.

### Modeling Process

AV share alpha in [0,1]. Each booth's service rate is 1,200 veh/h if it is ETC-class or AV-operated, else its type rate (350 conventional, 500 exact-change). The effective service coefficient k_c is reduced by 50% * alpha to represent lower headway variance (C_m = C_L/(1 + k_c*(1-0.5*alpha)*theta^2)). Throughput T_av = L*C_L / (1 + (B-L)*(1 - C_m_av/C_L)).

### Outcome Analysis

AV share raises effective booth service from 6,500 veh/h (no AVs, baseline 2 conv + 2 exact + 4 etc mix) to 9,600 veh/h (full AV/ETC), and the reduced headway variance lifts fan-in throughput correspondingly. The recommended geometry (s_opt, merge pattern) is unchanged: AVs improve the queue parameters but the structural optimum over s is set by the cost/accident/throughput trade, which is geometry-driven. Limitations: the 50% headway-variance reduction at full AV share is a declared assumption, not a measured value (the external data does not carry an AV-specific headway statistic); mixed human/AV interaction at the merge point (human driver responding to an AV's merge) is not modeled; the result is monotone in alpha, so there is no interior optimum — more AVs weakly improve performance, with the largest gain coming from replacing conventional booths.

## Subtask 4: Determine how the solution is affected by the proportions of conventional (human-staffed), exact-change (automated), and

### Problem

Determine how the solution is affected by the proportions of conventional (human-staffed), exact-change (automated), and electronic toll-collection booths. Scope: the effect of booth-type mix on per-booth service, fan-in throughput, and — per the expert-identified failure mode — on the feasibility of the ordered inner-first merge pattern.

### Analysis

Booth types carry service rates 350 (conventional), 500 (exact-change), 1,200 (ETC) veh/h (external data item 1). The mix affects (a) the booth-queue submodel (per-booth discharge rates, arrival headways into the fan-in) and (b) the merge-order feasibility condition identified by the expert in Exchange 3: ordered inner-first merging inverts when the per-booth service-rate dispersion across booth types exceeds the headway spacing the ordered sequence assumes, i.e., when a fast outer booth discharges into a gap the slow inner lane has not yet vacated. The booth mix is the only input that changes this dispersion, so it is the primary bias axis for the merge mechanism (per the policy's bias-quantification rule).

### Modeling Process

Mix (n_conv, n_exact, n_etc), sum = B. Per-booth discharge rate mu_i = SVC[type_i]/3600 veh/s; demand split rho_i = 1/B. Ordered inner-first feasibility: cumulative clearing times Q(i) = sum_{j<=i} rho_j/mu_j must be non-decreasing in i (each inner lane clears before the outer flow reaches its merge). Break-even dispersion r_be = max mu_max/mu_min such that Q is non-decreasing, found by bisection on the slowest booth's rate scale. Throughput T from Task 1 with the mix affecting only the queue submodel (the geometry/merge structure is mix-invariant).

### Outcome Analysis

Across the mix sweep (B = 8): the geometric optimum s_opt = 206 m and the merge pattern are mix-invariant (the structure does not change with the mix, by design). The mix affects the booth-queue service: all-ETC gives 9,600 veh/h total booth service vs 2,800 veh/h all-conventional, a 3.4x dispersion in per-booth rates at the mixed extreme (4 conv + 2 exact + 2 etc, dispersion 3.43). Merge-order feasibility: with demand split evenly across booths, the cumulative-clearing test Q(i) non-decreasing holds for every mix tested, because the inner booths discharge first and their slower rate is compensated by the even demand split — the break-even dispersion r_be = 1.0 (no inversion) for even splits. The failure mode the expert identified (order inversion) requires a demand split that overloads the inner slow booths relative to the outer fast ones; with even demand splits it is not triggered, which is itself a finding: the ordered-merge mechanism is robust to booth mix under even demand, and its break-even is set by the demand split, not the mix alone. Bias-quantification (per policy): the break-even is the inner-most conventional share p_inner_conv at which order inverts — computed as a function of the demand-split skew; under even splits the break-even is p_inner_conv = 1.0 (never inverts), and it drops as the demand concentrates on inner booths. Limitations: the even demand split is a declared assumption — real toll demand is not evenly split across booths (lane choice is correlated with destination), and the break-even p_inner_conv is therefore a structural boundary, not a measured operating point; the Q(i) test is a deterministic clearing-time criterion, not a stochastic gap-acceptance simulation, so it identifies the order-inversion boundary but not the probability of a merge conflict at a given dispersion.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
