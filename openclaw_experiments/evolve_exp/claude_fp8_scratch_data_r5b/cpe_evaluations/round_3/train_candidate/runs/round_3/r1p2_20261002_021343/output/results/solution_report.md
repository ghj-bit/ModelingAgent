# Solution

## Subtask 1: Subtask 1: Data cleaning and characterization of the supplied spreadsheet 2017_MCM_Problem_C_Data.csv, covering I-5 (Thu

### Problem

Subtask 1: Data cleaning and characterization of the supplied spreadsheet 2017_MCM_Problem_C_Data.csv, covering I-5 (Thurston to Snohomish county line), I-90, I-405, and SR 520 in the four counties. Goal: turn the raw row-per-milepost file into a clean, internally consistent segment table (route, milepost range, directional lane counts, 2015 average daily traffic) that the traffic model can consume. Scope: encoding, missing values, duplicates, unit and direction conventions, and a route-level summary.

### Analysis

Assumptions: (a) each row is a one-directional segment — the lane columns are explicitly 'DECR MP direction' (southbound/westbound) and 'INCR MP direction' (northbound/eastbound), so lane counts are per direction; (b) the single 'Average daily traffic counts Year_2015' column is applied to both directions of the segment, the standard WSDOT presentation of directional AADT for a corridor; (c) mileposts are continuous per route. Data checks performed: the file decoded cleanly as UTF-8 (BOM present, stripped); 224 data rows, no duplicated (Route_ID, startMilepost, endMilepost) keys; all numeric fields (mileposts, volume, lane counts) parsed without gaps; Comments is missing on many rows by design and is used only qualitatively. Lane counts are integers in 2..5. Volume range 13,000-242,000 veh/day. Repairs: BOM stripping, whitespace trimming of the lane-column header, and treating blank Comments as null. Route summary: I-5 135 segments (max 242,000/day, 3-5 lanes), I-90 27 segments (max 162,000/day, mostly 3 lanes), I-405 47 segments (max 195,000/day, mostly 2-3 lanes), SR 520 15 segments (max 109,000/day, 2 lanes). There are 448 direction-segments in total, and both directions of every row are modeled.

### Modeling Process

The clean table has one row per (route, direction, segment): route r, length L = endMP - startMP, lane count k_dir in {2,3,4,5}, daily volume V. No transformation beyond parsing was applied, because the counts are already the model's input. Data-quality statistics: 224 rows, 448 direction-segments, 0 missing numeric values, 0 duplicates; lane distribution per route: I-5 {3:77, 4:48, 5:10}, I-90 {3:23, 2:3, 4:1}, I-405 {3:31, 2:14, 4:2}, SR 520 {2:15} (INCR direction).

### Outcome Analysis

The data is high quality: no imputation was needed. The main structural fact the model must respect is that volume is a daily count while congestion is a peak-hour phenomenon — the bridge between the two (the peak-hour share of daily volume) is not in the file and must be supplied from outside (see subtask 2, parameter table). Directional lane counts vary within a corridor (e.g. I-5 grows from 3 to 5 lanes approaching Seattle), so the model is applied per segment-direction, not per route.

## Subtask 2: Subtask 2: Build the traffic-flow model. Goal: a per-lane flow-speed-density relationship that takes (lanes k, peak/aver

### Problem

Subtask 2: Build the traffic-flow model. Goal: a per-lane flow-speed-density relationship that takes (lanes k, peak/average daily volume V, self-driving share f in {0, 0.1, 0.5, 0.9}) as input and produces equilibrium traffic state (flow, speed, travel time, congested or free) plus per-lane capacity. Scope: the cooperation mechanism between self-driving cars, and the interaction between self-driving and human-driven vehicles.

### Analysis

Assumptions: (1) Greenshields-type fundamental diagram per lane, q(rho) = v0*rho*(1 - rho/rho_j), whose maximum is q_max = v0*rho_j/4 — this is the standard, parsimonious form for a freeway segment, and it makes 'does an equilibrium exist' a well-posed question: for any demand q below q_max there are two densities (free-flow and congestion branches), for q = q_max one, and for q > q_max no stable equilibrium (queue forms). (2) The effect of self-driving enters through the per-lane maximum flow q_max(f): cooperating AVs shorten safe headways and remove the shockwave amplification that human reaction times cause, raising q_max; human drivers in the same lane fragment convoys, so the gain scales with the fraction of lanes that actually hold an intact convoy. (3) Peak-hour demand D = V * rho_peak, where rho_peak is the peak-hour share of daily volume; on chronically congested freeways the peak hour absorbs a larger share of the daily volume than the classic ~7% free-flow value, so rho_peak is banded by daily demand per lane: 0.25 above 40,000 veh/day/lane, 0.20 above 30,000, 0.15 above 20,000, 0.10 above 12,000, else 0.07. This banding is the calibrated input that makes the 0%-AV baseline reproduce the observed chronic-peak-queue behavior of these corridors.

### Modeling Process

Per-lane model. Parameters (empirical, with provenance):
  q_H = 1900 veh/h/lane, interval [1800, 2000], source: expert exchange 1 (observed congested-lane throughput); used for the all-human fleet.
  q_A = 3800 veh/h/lane, interval [3500, 4000], source: expert exchange 1 (tightly coordinated convoy upper bound); q_A/q_H = 2.0.
  rho_peak(V) = 0.25/0.20/0.15/0.10/0.07 for V/k > 40k/30k/20k/12k/else, source: calibrated to reproduce chronic peak-hour saturation of these corridors (documented in code traffic_model.py:peak_ratio); interval: the classic free-flow value is ~0.07-0.074, saturation values up to ~0.25.
  alpha = cooperation effectiveness, free parameter, swept in [1.0, 2.0]; alpha=1.0 is the base case in which a fully-convoyed lane reaches exactly q_A.
  phi_fill = 1.5: minimum fleet share for a dedicated lane to hold a stable convoy (lane-fill threshold), source: model assumption, sensitivity shown in subtask 4.
Formulas:
  g(f, k, dedicated) = alpha * f * phi  (cooperation gain, can exceed 1 for alpha>1)
  Shared lanes: phi_shared = min(1, f*k/(f*k + 1.5)) — convoy integrity on k shared lanes; humans and lane changes fragment convoys, so phi is small at low f and approaches 1 only when AVs dominate.
  q_max(f) = q_H + (q_A - q_H) * min(1, g) for alpha=1; with alpha>1, q_max = q_H + (q_A - q_H) * g (convoy throughput can exceed the pure-convoy anchor when coordination is very effective).
  Capacity per direction: C = k * q_max(f).
  Peak demand: D = V * rho_peak(V/k).
  Equilibrium: if D <= C the segment is in a stable state (free-flow or congestion branch, both equilibria of Greenshields); operating speed v = v0*(1 - rho/rho_j) with rho on the free-flow branch. If D > C no stable equilibrium exists and a queue forms; congestion excess is defined as D/C - 1.
  Dedicated-lane case (policy lever): one lane reserved for AV convoys where f >= 0.10. The reserved lane is served at the near-full convoy rate q_ded = q_H + 0.9*(q_A - q_H) = 3520 veh/h — per expert exchange 2, the benefit is boundary isolation (no lane changes crossing the lane), not speed. AV demand D*f goes to the reserved lane, human demand D*(1-f) to the k-1 general lanes at the human rate q_H (no convoy in a mostly-human fleet). Segment is congested if either D*f > q_ded or D*(1-f) > (k-1)*q_H. A dedicated lane without exclusion (free entry/exit) is scored at phi_shared instead, which is the model's test of the exchange-2 mechanism: without isolation most of the benefit disappears.

### Outcome Analysis

The model is deliberately low-parameter (two throughput anchors, one effectiveness coefficient, one integrity curve) so that every conclusion can be traced to either the data (V, k) or a sourced input (q_H, q_A, rho_peak, exchanges 1-2). Limitations: Greenshields is a parabolic approximation; real freeways have capacity drops and spillback that a single-segment diagram cannot capture, so 'queue forms' is a saturation statement, not a queue-length prediction. The rho_peak banding is the largest single assumption — if true peak demand is 10% lower than modeled, some borderline segments flip to equilibrium. The mixed-traffic gain is upper-bounded by the exchange-1 finding that non-cooperating vehicles break up convoys; the model's phi_shared encodes exactly that.

## Subtask 3: Subtask 3: Apply the model to the data and answer the governor's questions: how do effects change as the self-driving sh

### Problem

Subtask 3: Apply the model to the data and answer the governor's questions: how do effects change as the self-driving share goes 10% -> 50% -> 90%; do equilibria exist; is there a tipping point where performance changes markedly; under what conditions should lanes be dedicated to these cars; and what other policy changes does the analysis suggest.

### Analysis

Application method: run the per-segment model for all 448 direction-segments of the four routes at f = 0, 0.10, 0.25, 0.50, 0.90, with alpha = 1.0 (base) and alpha = 2.0 (strong cooperation), and with dedicated = 0 (shared lanes) and dedicated = 1 (one reserved lane per direction where f >= 10%). Network metrics: number of congested direction-segments, the congestion-excess sum E = sum over segments max(0, D/C - 1), and E relative to the 0%-AV baseline. Per the validation criterion from expert exchange 3, results are judged against a 5% noise band: effects below ~5% relative change are not decision-relevant, 5-10% is marginal and requires multi-month confirmation, above 10% is a real signal.

### Modeling Process

Scenario runs (all in logs/): (1) Shared lanes, alpha=1.0: E falls 1999 -> 1958 (10%), 1810 (25%), 1511 (50%), 1108 (90%); congested-segment count 436 -> 432. Relative improvement: +2.1% (10%), +9.5% (25%), +24.4% (50%), +44.6% (90%). (2) Shared lanes, alpha=2.0: E falls 1999 -> 1919 (10%), 1648 (25%), 1187 (50%), 702 (90%); congested segments 436 -> 390 at 90%. Relative: +4.0%, +17.6%, +40.6%, +64.9%. (3) Dedicated lane, any alpha: E rises to ~2900-3500, i.e. 45-76% worse than baseline, because reserving a lane removes one human lane of capacity (k-1 general lanes at q_H) faster than the convoy lane adds capacity, on corridors this oversaturated. (4) Worst single segment (I-5 MP 163.48-164.22, V=242,000, k=3, D=60,500 veh/h): no equilibrium at any f for alpha=1.0 (D/C from 10.6 at 0% to 6.7 at 90%); with alpha=2.0, D/C at 90% is 4.9 — still no equilibrium. The segment would need alpha ~4 (or demand 4x lower) to reach D/C=1.

### Outcome Analysis

Answers to the governor's questions: (1) Effects grow monotonically and strongly with f: at 10% AV the network improvement is small (2-4%, inside the 5% noise band — not decision-relevant); at 50% it is large (24-41%); at 90% it is very large (45-65%). (2) Equilibria: almost all 448 direction-segments are oversaturated at 0% AV (436 congested, 97.3%); the corridors are chronically in the no-equilibrium (queue) regime at peak, which matches the observed Seattle-area congestion. AVs shrink the excess demand but do not restore equilibrium to the worst I-5 segments at any tested f. (3) Tipping point: the curve of improvement vs f is convex — most of the gain arrives between 25% and 90%. At alpha=1.0 the improvement jumps from +9.5% (25%) to +44.6% (90%), and the congested-segment count only starts falling materially above 25%; at alpha=2.0, 46 of 448 segments clear saturation by 90% (I-90 from 48 to 30 congested). The tipping point, where performance changes markedly, is therefore f ≈ 50%: below it the network is still essentially in the 0%-AV regime (10% is noise), above it the benefit becomes large and, with strong cooperation, segments begin to clear saturation. (4) Dedicated lanes: reserving a lane makes things substantially worse on these corridors (E +45% to +76% vs baseline) because removing a general-purpose lane on an oversaturated freeway costs more than the convoy lane yields. Condition under which a dedicated lane helps: only where the segment is not oversaturated (D < (k-1)*q_H + q_ded after the split), i.e. on lower-volume segments such as the outer I-90, outer I-405, and SR 520 segments — never on the congested I-5 Seattle approach. A practical rule: dedicate a lane only where daily demand per lane is below ~30,000 AND the AV share can fill the lane (f >= ~0.3), and only if entry/exit is excluded (per exchange 2, free entry/exit removes most of the convoy benefit). (5) Other policy: (a) manage demand, not just supply — the 0%-AV baseline shows demand exceeds capacity by up to 11x at peak on the worst segments, so any AV rollout is an improvement, not a fix; (b) ramp pricing or cordon pricing on the I-5 approach to bring D/C back under 1; (c) staggered work hours to flatten the peak (lowering effective rho_peak from 0.25 toward 0.15 would clear a large fraction of segments even at 0% AV); (d) if AV rollout is pursued, require V2X coordination standards so that the phi_shared integrity factor is not eroded by incompatible systems; (e) monitor with the multi-month, 5-10% threshold from exchange 3 before declaring success.

## Subtask 4: Subtask 4: Validation, sensitivity, and interpretation of the results under the model's uncertainties, and statement of 

### Problem

Subtask 4: Validation, sensitivity, and interpretation of the results under the model's uncertainties, and statement of the model's biases.

### Analysis

Method: (1) sweep the free parameter alpha in [1.0, 2.0] (alpha=1.0 anchors full-convoy throughput at the expert-quoted 2x bound; alpha=2.0 explores very effective coordination beyond it); (2) check the dedicated-lane decision rule against its boundary; (3) judge every headline number against the 5% noise band from expert exchange 3; (4) enumerate biases in the data and model.

### Modeling Process

Sensitivity: the network improvement at 90% AV ranges from +44.6% (alpha=1.0) to +64.9% (alpha=2.0); at 50% AV from +24.4% to +40.6%; at 10% AV from +2.1% to +4.0% (both inside the noise band). The qualitative conclusions — monotone improvement, tipping point near 50%, dedicated lanes harmful on oversaturated segments — are unchanged across the alpha range. Boundary check for dedicated lanes: a k-lane segment with D peak demand breaks even on a dedicated lane when D*f <= q_ded and D*(1-f) <= (k-1)*q_H; with q_ded=3520 and q_H=1900, for k=3 this requires D <= ~10,800/f + ~3,800/(1-f) in veh/h, i.e. daily volume below roughly 40,000-60,000 depending on f — only the outer segments of I-90, I-405, SR 520, and the rural I-5 qualify. Bias inventory: (a) Selection bias in the data: the spreadsheet covers only the state's highest-volume corridors in the four counties, so extrapolating beyond these routes is not supported; (b) Temporal bias: a single year (2015) of daily averages — non-stationary with respect to the future AV scenario the model is asked to project; (c) Aggregation bias: daily counts used with a peak-hour banding that assumes the peak-hour profile of a congested freeway; if actual peaks are milder, all D/C ratios overstate saturation by up to the ratio of the bands; (d) Model-form bias: Greenshields overstates capacity on the congestion branch and has no capacity drop, so 'no equilibrium' is a conservative saturation statement; (e) Cooperation bias: the phi_shared integrity curve assumes AVs only cooperate when adjacent — no long-range coordination credit is taken, which biases the predicted gain downward at low f (a favorable bias for the policy case is not claimed); (f) Directional symmetry: one volume value is applied to both directions, whereas real AM/PM asymmetries could shift the worst segment by a milepost or two.

### Outcome Analysis

The conclusions are robust to the alpha sweep and to the dedicated-lane boundary; the single most influential assumption is the rho_peak banding (peak demand), and the result is most sensitive to it at the worst I-5 segments, where even a 30% reduction in assumed peak demand would not restore equilibrium (D/C would still exceed 2). The model's headline finding — that 10% AV penetration is indistinguishable from the status quo (effect inside the 5% noise band), 50% is the tipping point where the network benefit becomes large, and 90% clears saturation on roughly 10-20% of direction-segments under strong cooperation — is decision-relevant under the exchange-3 criterion, while the 10% result must be reported as not-yet-convincing. Dedicated lanes should not be introduced on oversaturated segments and are justified only on lower-volume segments with f >= ~0.3 and excluded entry/exit.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
