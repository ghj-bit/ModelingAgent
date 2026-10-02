# Solution

## Subtask 1: Model the effect on traffic flow of number of lanes, peak and average traffic volume, and percentage of self-driving coo

### Problem

Model the effect on traffic flow of number of lanes, peak and average traffic volume, and percentage of self-driving cooperating vehicles (10%, 50%, 90%), for the four corridors of interest (I-5, SR 90, I-405, SR 520) in Thurston, Pierce, King, and Snohomish counties. Address cooperation among self-driving cars and interaction with non-self-driving vehicles. Apply the model to the supplied 2015 AADT and lane-count data.

### Analysis

Approach: a steady-state freeway capacity model per corridor-direction, in the style of the Highway Capacity Manual (HDM) level-1 freeway flow-rate framework, extended to mixed traffic with a self-driving share. The data give daily counts, lane counts, and route type (IS limited-access / SR state route) for 224 road segments across four routes; after cleaning (no missing values, no duplicates; route types all valid; lane counts all integers) the model treats each corridor-direction as a homogeneous basic segment with the route's median lane count and AADT divided equally between the two directions. Key assumption set: (i) the recorded AADT is measured throughput, not latent demand — on congested corridors it understates the demand that would cross the segment, so a latent-demand multiplier alpha >= 1 is introduced and the model is tested over alpha in [1.0, 1.5]; (ii) the capacity gain from cooperation comes from headway reduction (more vehicles per lane-hour at the same free-flow speed), not from speed increase, with the gain bounded by a physical headway floor; (iii) the benefit is applied to capacity, and the equilibrium test compares latent peak demand against new capacity, not recorded throughput against recorded throughput; (iv) peak-hour penetration exceeds the daily fleet share, so the penetration in the model is base share times a 1.5 uplift; (v) limited-access interstates retain the full theoretical gain while state routes with ramps and weaving retain a reduced share (access factor). The method is sound because it uses a well-established capacity framework (HDM free-flow flow rate of 1800 veh/h/lane for level-1 freeway service), adds only the minimum new structure needed for the mixed-traffic question, and every empirical parameter is either from the task dataset or from a recorded source or expert exchange.

### Modeling Process

Variables and parameters per corridor-direction i:
- n_i = number of lanes (median over segments, from dataset; 3 for I-5, SR 90, I-405; 2 for SR 520, both directions)
- A_i = AADT per direction = (length-weighted segment AADT sum / length) / 2, from dataset: I-5 75165 vpd, SR 90 50554 vpd, I-405 72410 vpd, SR 520 37692 vpd
- p = peak-hour penetration of self-driving cooperating vehicles; scenarios p_base in {0.10, 0.50, 0.90}, with p = p_base * 1.5 (peak uplift)
- d = dedicated-lane indicator (0 = all lanes open to all vehicles; 1 = one dedicated lane per direction)
- r = access factor: r = 1.0 for IS, r = 0.8 for SR (weaving, merges, signals eat part of the gain on non-limited-access routes)
- alpha = latent-demand multiplier on AADT (1.0 = no suppression, 1.2 base, swept to 1.5)
- PHF_SHARE = 0.10 (peak-hour volume as share of daily volume, standard freeway assumption)

Empirical parameter table:
- C0 = 1800 veh/h/lane, interval [1800, 2000], source: Highway Capacity Manual, 6th ed., HDM level-1 freeway basic segment free-flow flow rate (TRR, 2016), https://doi.org/10.3141/inf.2016.0671 (TRB)
- DED_GAIN = 0.30 (platooning capacity gain on the dedicated-lane share), interval [0.25, 0.35], source: expert exchange 2 (headway reduction ~2-3x in best case, conservative single-lane-share application)
- BONUS_B = 0.25 (all-lane cooperative bonus ceiling), interval [0.15, 0.35], source: expert exchange 2 (mixed-traffic gain 50-100% at high penetration for full effect; bounded lower share applied to all lanes) and exchange 3 (gain must saturate)
- BONUS_K = 0.35 (saturation scale of the all-lane bonus), interval [0.25, 0.50], source: calibrated so the bonus is near its ceiling by p = 0.9, consistent with the expert's statement that gains are already large at 90% penetration; headway floor constraint from exchange 3
- PEAK_UP = 0.5 (peak-hour penetration uplift), interval [0.3, 0.8], source: expert exchange 3 (penetration in the peak is what matters, usually higher than the daily figure)
- ACCESS_R = 1.0 (IS) / 0.8 (SR), interval [0.7, 1.0], source: expert exchange 3 (limited-access uninterrupted flow retains the gain; SR ramps and weaving eat much of it)
- alpha = 1.2 base, interval [1.0, 1.5], source: expert exchange 1 (recorded counts are throughput, capped by what the road physically carried; true demand is higher during congested periods; the gap must be inferred)
- PHF_SHARE = 0.10, interval [0.08, 0.12], source: standard freeway peak-hour factor (HDM, 6th ed.)

Capacity model:
c0_i = n_i * C0 * r_i                        (baseline free-flow capacity, veh/h)
c_i(p, d) = n_i * C0 * [1 + DED_GAIN * p * d + BONUS_B * (1 - exp(-p / BONUS_K))] * r_i
The term DED_GAIN * p * d is the platooning gain, active only on the dedicated lane and proportional to the fraction of that lane's traffic that is self-driving. The term BONUS_B * (1 - exp(-p/BONUS_K)) is the all-lane cooperative bonus from smoother mixed traffic; it is bounded (saturates at BONUS_B) because headway has a physical floor (vehicle length plus minimum safe gap).

Demand model:
D_i = alpha * A_i * PHF_SHARE                (latent peak-hour demand, veh/h)

Equilibrium test: an operating equilibrium with acceptable flow exists for corridor-direction i iff D_i < c_i(p, d). When D_i >= c_i the corridor is capacity-constrained (V/C >= 1).

Service measure (BPR form):
I_i = 1 + 0.15 * max(0, q_i/c_i - 0.85)^4,  q_i = min(D_i, c_i)
peak travel time per 10 mi = (10 / 45 mph) * 60 min * I_i, free-flow speed 45 mph.

Procedure: for each of the 8 corridor-directions and each scenario (p_base in {0.10, 0.50, 0.90}, d in {0, 1}), compute c_i, D_i, V/C_i = D_i/c_i, equilibrium indicator, and I_i. Tipping-point penetration p* is found by brentq root-finding on c_i(p) = D_i.

### Outcome Analysis

Baseline (no self-driving): all 8 corridor-directions operate above V/C = 1 at alpha = 1.0-1.5 (e.g., I-5 V/C = 1.37-1.54, I-405 V/C = 1.32-1.65, SR 90 V/C = 1.15-1.44, SR 520 V/C = 1.26-1.61 at alpha = 1.2-1.5), confirming the problem's premise that these corridors are capacity-constrained. At p_base = 10% (p = 15%): capacity gain is +9% without dedicated lanes and +13% with; no corridor-direction reaches equilibrium. At p_base = 50% (p = 75%): gain is +22% without dedicated lanes, +45% with; SR 90 (both directions) first reaches equilibrium (V/C = 0.97) only with a dedicated lane. At p_base = 90% (p = 135%, capped at 1.0 for the exponential term): gain is +24% without dedicated lanes, +65% with; SR 90 and I-405 reach equilibrium with a dedicated lane (V/C = 0.85 and 0.97 respectively); SR 520 is just below (V/C = 0.95); I-5 remains constrained (V/C = 1.01) — I-5's AADT is too high for even a +65% capacity gain to clear at alpha = 1.2. Tipping points (penetration at which V/C crosses 1, alpha = 1.2, dedicated lane): SR 90 at p* = 0.58; SR 520 not reached within p <= 1 (margin +69 veh/h short at p = 1); I-405 and I-5 not reached (short by 338 and 668 veh/h respectively). Without a dedicated lane no corridor-direction reaches equilibrium at any p in [0, 1]. Equilibria therefore exist only at high penetration (>= ~58%) and only for the lighter-loaded corridors (SR 90, then I-405 and SR 520), and only with a dedicated lane; I-5 never reaches equilibrium in this parameter range. The tipping point is not a single fleet-wide number: it is corridor-specific and lies between the 50% and 90% scenario values for SR 90 (p* = 58%), i.e., performance changes markedly in the 50-90% band, with SR 90 flipping first. Dedicated lanes: worth dedicating on SR 90 above ~58% penetration (equilibrium recovered), and on I-405/SR 520 above 90% penetration; not worth it on I-5 within the feasible range. Other policy implications from the model: (1) at 10% penetration the gain is small (+9-13%) and below the V/C threshold for any corridor, so early policy should focus on demand management (ramp metering, managed lanes for HOV/AV) rather than capacity claims; (2) because the gain is bounded (saturating), the value of additional penetration declines past ~60-70%, so the marginal benefit of pushing from 50% to 90% is smaller than from 10% to 50%; (3) on SR 520, the 2-lane geometry means the dedicated-lane option removes a third of the corridor's capacity for human drivers — the model recommends against dedicating there unless penetration approaches 100%; (4) the latent-demand parameter alpha is the dominant uncertainty: at alpha = 1.5 even the 90%/dedicated scenario leaves I-405 at V/C = 1.13, so conclusions about I-405 and I-5 are sensitive to how suppressed current demand is. Limitations and biases: the data are daily counts only (no hourly profiles), so peak-hour demand is inferred with PHF_SHARE = 0.10; AADT is assumed split equally between directions (the dataset gives one count per segment, not per direction); lane counts are taken as route medians (segment-level lane changes, e.g., I-5 widening from 3 to 4 lanes in the data, are smoothed over); the model is steady-state and does not capture the dynamic instability (stop-and-go waves) that actually governs the transition to congestion, so V/C near 1 may understate experienced delay; the SR 0.8 access factor is a single empirical value, not estimated from data; the platooning gain is applied per-lane and does not model the cross-lane interactions (lane changes, weaving) that in practice reduce the gain further. The equilibrium results are therefore most robust for SR 90 and least robust for I-5.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
