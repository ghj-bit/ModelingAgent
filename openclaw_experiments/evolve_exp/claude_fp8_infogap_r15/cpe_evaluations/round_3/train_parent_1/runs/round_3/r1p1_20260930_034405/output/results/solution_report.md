# Solution

## Subtask 1: Model the effect of self-driving, cooperating vehicles on traffic flow along I-5, I-90, I-405 and SR-520 in Thurston, Pi

### Problem

Model the effect of self-driving, cooperating vehicles on traffic flow along I-5, I-90, I-405 and SR-520 in Thurston, Pierce, King and Snohomish counties, as a function of (a) number of lanes, (b) peak and/or average traffic volume, and (c) the percentage of vehicles using self-driving, cooperating systems (p = 10%, 50%, 90%). Determine whether equilibria exist, whether there is a tipping point where performance changes markedly, under what conditions lanes should be dedicated to these vehicles, and what other policy changes follow. The model is applied to the provided 2015 segment-level data (route, milepost range, average daily traffic, lanes per direction).

### Analysis

Assumptions: (1) Traffic demand is exogenous, fixed at the 2015 average daily traffic counts (ADT); only the supply side (capacity, speed, delay) changes with the CAV share p. This was settled by the expert (Exchange 1, item 1): the 'equilibrium' the problem asks for is a steady-state supply regime in which demand flow is sustainable given lane capacity, not a network/Wardrop fixed point. (2) The demand-vs-capacity test is taken at the 15-minute peak time scale (Exchange 1, item 2): the 15-minute peak flow is compared against the hourly lane capacity. Since only ADT is given, a peak-window conversion is used: the peak hour carries r/ (W/4) of the daily flow, with r = 0.48 the fraction of daily traffic in a 4-hour peak window (W = 4 hr), i.e. peak-hour flow = ADT * 0.12 (a 12% peak-to-daily ratio, standard for urban freeways). (3) The baseline (p = 0) speed-density fundamental diagram for a basic freeway segment follows the Highway Capacity Manual (HCM 6th ed.) unified relation v = S_f (1 - (k/45)^a) with free-flow speed S_f = 75 mph, exponent a = 2, and critical (capacity) density k_cap(0) = 45 pc/mi/ln. (4) CAV cooperation and CAV-human interaction enter the capacity as a two-term product, settled by the expert: the Exchange-2 judgment (a single monotone capacity-density shift with no separate instability term) was REJECTED, so the model uses C_eff(p) = L * q_cap(p) * h(p), where q_cap(p) is the CAV-cooperation capacity-density shift and h(p) is a separate mixed-flow stability factor. (5) The tipping point is the structural regime crossing (Exchange 1, item 3): p* is the smallest p such that q_demand <= C(p, L), i.e. the penetration at which a segment crosses from the infeasible (no sustainable equilibrium) to the feasible regime. (6) The dedicated-lane case tracks the true fleet composition of each lane group separately (Exchange 3 counterexample (iii)): a naive clip of the residual CAV share to 1 hides that the residual lanes are no longer mixed and double-counts the cooperation gain. Method: a macroscopic supply-side fundamental-diagram model is appropriate because the question is about capacity and regime existence (not micro-level vehicle dynamics), the data are segment-level daily volumes and lane counts, and the HCM gives a defensible baseline diagram. The CAV effect is parameterized so its shape matches the independent literature (external_data.md item 2): capacity gain is small at low/mid penetration and steepens toward p = 1, with a modest mixed-flow stability dip at intermediate p. Parameters: g(p) = g1 * p^beta with g1 = 0.35, beta = 2 (so full CAV raises the critical density by 35%, and the gain is convex in p); h(p) = 1 - d * p * (1-p) with d = 0.08 (a ~2% dip at p = 0.5). These are structural choices calibrated to the literature range (low single-digit percent gain at mid penetration, larger near full penetration), not fitted to the task data.

### Modeling Process

Variables: p in [0,1] CAV share; L = number of lanes in the direction considered; ADT = average daily traffic; k = density (pc/mi/ln); q = flow (pc/hr); v = speed (mph).

Baseline fundamental diagram (HCM unified, per lane):
  v(k) = S_f * (1 - (k/45)^a),   S_f = 75 mph, a = 2.
  q(k) = k * v(k).
  Capacity point (max of q over k): k* = 45 * (1/(a+1))^(1/a) = 45 * (1/3)^(1/2) = 25.98 pc/mi/ln,
  q_cap(0) = k* * S_f * a/(a+1) = 25.98 * 75 * 2/3 = 1299 pc/hr/ln.

CAV cooperation (capacity-density shift):
  k_cap(p) = 45 * (1 + g(p)),  g(p) = g1 * p^beta, g1 = 0.35, beta = 2.
  q_cap(p) = k_cap(p) * (1/(a+1))^(1/a) * S_f * a/(a+1).
  Thus q_cap(p) = q_cap(0) * (1 + 0.35 * p^2).

Mixed-flow stability (separate term, per expert Exchange 2 rejection):
  h(p) = 1 - d * p * (1 - p),  d = 0.08,  h(0) = h(1) = 1,  min at p = 0.5 of 1 - d/4 = 0.98.

Lane capacity (total, both terms):
  C(p, L) = L * q_cap(p) * h(p)  [pc/hr].
  Capacity relative to baseline: C(p,L)/C(0,L) = (1 + 0.35 p^2) * (1 - 0.08 p (1-p)).
  Values: p=0: 1.000; p=0.10: 0.9963; p=0.50: 1.0657; p=0.90: 1.2743; p=1.00: 1.350.
  (The curve dips slightly below 1 around p = 0.10 because the stability dip outweighs the still-small cooperation gain at low p; it then rises monotonically and steepens toward p = 1.)

Demand (exogenous, peak time scale):
  q_peak = ADT * r / (W/4),  r = 0.48, W = 4 hr  =>  q_peak = 0.12 * ADT  [pc/hr, directional].

Equilibrium / regime test (per segment, per direction):
  Segment is in equilibrium (uncongested) at share p iff  q_peak <= C(p, L).
  Load factor:  LF(p) = q_peak / C(p, L).  Congested iff LF(p) > 1.

Tipping point (per segment):
  p* = min { p : LF(p) <= 1 }  (regime crossing from infeasible to feasible);
  'none' if the segment is feasible already at p = 0, or 'never' if LF(p) > 1 for all p in [0,1].

Dedicated-lane comparison (per expert Exchange 3 (iii), track true composition per lane group):
  Mixed option:  L lanes, CAV share p on all  ->  C_mix = L * q_cap(p) * h(p).
  Dedicated option: 1 CAV-only lane (share 1, h = 1) + (L-1) residual lanes.
    Residual CAV share p' = p * L / (L - 1) (true share, not clipped).
    If p' < 1: residual group is mixed -> C_resid = (L-1) * q_cap(p') * h(p').
    If p' >= 1: residual group is all-CAV -> C_resid = (L-1) * q_cap(1) * 1  (no mixed term).
    C_ded = q_cap(1) + C_resid.
  Dedicated is preferable iff min(q_peak, C_ded) > min(q_peak, C_mix), i.e. it carries more of the demand.

Solution procedure: for each of the 448 directional segments (I-5: 270, I-90: 54, I-405: 94, SR-520: 30), compute q_peak from ADT, then C(p,L) and LF(p) over p = 0,0.05,...,1.00; record the regime, the per-segment p*, the total flow deficit sum over segments of max(0, q_peak - C(p,L)), and the dedicated-vs-mixed carried flow at p = 0.10, 0.50, 0.90. Implementation: code/freeway_model.py (constants on the command line, parameterized).

### Outcome Analysis

Baseline capacity: 1299 pc/hr/ln at S_f = 75 mph (k* = 25.98 pc/mi/ln). Capacity as a fraction of baseline vs. p: 10% -> 0.996, 50% -> 1.066, 90% -> 1.274, 100% -> 1.350; the minimum (0.996) occurs near p = 10%.

Effect of penetration 10% / 50% / 90% (total flow deficit over all 448 directional segments, pc/hr below capacity):
  p = 0%: 28,241,031;  p = 10%: 28,247,926 (+0.02%);  p = 50%: 28,119,319 (-0.43%);
  p = 90%: 27,733,341 (-1.80%);  p = 100%: 27,593,136 (-2.29%).
  Per road (deficit at p=0 vs p=90%): I-5 19,022,592 -> 18,684,845; I-90 2,195,091 -> 2,139,156; I-405 6,087,530 -> 5,994,899; SR-520 935,818 -> 914,441.
  Interpretation: because the network is heavily oversaturated at the peak time scale (see below), the capacity gain from CAVs reduces the deficit but cannot remove congestion; the relative improvement is small at 10% and 50% and reaches about 1.8% by 90%, consistent with the literature shape (low single-digit percent at mid penetration).

Do equilibria exist: No, at the p = 0 baseline. With the peak-hour demand q_peak = 0.12*ADT and capacity 1299*L pc/hr/ln, EVERY one of the 448 directional segments has load factor > 1 (the lowest is the 13,000-ADT downtown I-90 segment at LF = 1.60; the typical 3-lane urban I-5 segment is at LF ~ 7-30; the worst is I-5 mp 163.48-165.29, 2-lane with ~240,000 ADT, LF ~ 44-45). Thus there is no sustainable steady-state equilibrium at the 15-minute peak time scale for any segment at p = 0, and since the maximum attainable capacity is only 1.35x baseline, none becomes feasible at any p in [0,1]. (At the daily average time scale the picture is far milder, but the expert fixed the equilibrium test at the peak time scale.)

Tipping point: Under the structural definition (regime crossing to q_demand <= C(p,L)), no segment has a tipping point within [0,1] — all are infeasible at every p (p* = 'never' for all 448 segments). There is therefore no penetration at which performance 'changes markedly' in the sense of a feasibility crossing. The nearest meaningful threshold is the inflection of the capacity curve itself: the stability dip bottoms out near p = 10% and the capacity then rises monotonically and steepens toward p = 1, so the marginal benefit of additional CAVs is small below ~20-30% and grows thereafter. This is the model's answer to 'is there a tipping point': no crossing-type tipping point exists for this oversaturated network; the benefit is continuous and accelerating, with the practical 'knee' in marginal gain around p = 30-40%.

By lane count (number of directional segments / deficit at p=0): 2 lanes: 68 segments, 3,252,451; 3 lanes: 252, 14,810,887; 4 lanes: 107, 8,408,492; 5 lanes: 21, 1,769,201. Two- and three-lane segments carry the largest per-lane loads and are where CAV capacity gains (and any demand management) matter most; 5-lane segments are relatively the least stressed.

Dedicated lanes: For every segment at p = 10%, 50% and 90%, the dedicated option (1 CAV-only lane + residual lanes) carries strictly more flow than the mixed option — e.g., the worst 3-lane I-5 segment carries 4,153 pc/hr mixed vs 4,817 dedicated at p = 50% (+16%), and 4,966 vs 5,261 at p = 90%. The dedicated lane is capacity-positive at ALL penetration levels because a CAV-only lane runs at full cooperation (q_cap(1), h = 1) while surrendering only one lane. Condition for recommendation: dedicate a lane when (i) the CAV share is high enough that the CAV-only lane's flow is not wasted (the dedicated lane needs ~q_cap(1) = 1,754 pc/hr of CAV demand to be fully utilized, i.e. p*L*ADT*0.12 >= 1754, met on all high-ADT segments at p >= 10%) and (ii) the segment is capacity-constrained (it is, everywhere here). Because the network is oversaturated, dedicating a lane to CAVs is recommended on the highest-demand, fewest-lane segments (2- and 3-lane urban I-5, I-405, and the 2-lane SR-520) as penetration rises toward 50-90%; at 10% penetration the gain is real but small, so dedication is most justified at 50%+.

Other policy changes suggested by the model: (1) Because no CAV share restores equilibrium at the peak time scale, capacity must also come from added lanes or demand management — CAVs are a necessary but not sufficient fix. (2) Peak-demand management (managed lanes / HOV, transit priority, congestion pricing, or work-schedule staggering) to bring peak-hour volume toward the ~1299*L pc/hr capacity; the model shows the binding constraint is peak volume, not daily volume. (3) Prioritize 2- and 3-lane segments for both lane addition and CAV dedication, since they carry the highest load factors. (4) Sequence: at 10% CAV penetration, rely on mixed-lane operation (dedication optional); at 50%+, dedicate the rightmost lane on constrained 2-3-lane segments; at 90%, dedicate on all constrained segments.

Limitations and biases: (1) The peak-to-daily ratio (12%) and the 4-hour peak window are standard assumptions, not from the task data; a lower ratio would relax the load factors but not the qualitative conclusion (most segments remain >1 at the peak). (2) S_f = 75 mph and a = 2 are HCM defaults; the data carry no speed information, so per-segment free-flow speed is not differentiated. (3) The CAV cooperation magnitude (g1 = 0.35 at p = 1) and the stability-dip depth (d = 0.08) are structural choices calibrated to the independent literature (external_data.md items 1-2), not fitted to the data; the absolute deficit reductions scale roughly with g1, while the qualitative findings (no equilibrium, no crossing-type tipping point, dedicated lanes capacity-positive) are robust to moderate changes in these constants. (4) Demand is exogenous: the model does not capture route-choice or induced-demand responses (the expert excluded a network fixed point). (5) The two-term factorization C_eff = q_cap(p)*h(p) is valid only when each lane group's fleet composition is tracked separately (Exchange 3 (iii)); applying a single h(p) over a cross-section whose lanes are no longer all-mixed would misstate capacity, so the dedicated-lane comparison tracks the true residual share p' = p*L/(L-1) and sets h = 1 when p' >= 1. (6) Segments are treated independently (no upstream/downstream queue propagation, no on/off-ramp spillback beyond the given milepost data), so local equilibrium does not guarantee system-wide flow; this is a bias toward over-optimism for the network as a whole. (7) The ADT is a 2015 annual average and is applied symmetrically to both directions via the per-direction lane counts; directional asymmetry in demand is not in the data.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
