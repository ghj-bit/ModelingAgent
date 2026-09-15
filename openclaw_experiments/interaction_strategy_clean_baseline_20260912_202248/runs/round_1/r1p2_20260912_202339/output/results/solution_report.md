# Aviation Baggage Screening Strategies: To Screen or Not to Screen, that is the Question

**ModelingBench report — Problem ID `2003_Aviation_Baggage_Screening` (ICM 2003)**

**Executive summary.** Using the Technical Information Sheet (TIS) peak-hour departure table, we build a demand → capacity model of checked-baggage screening with Explosive Detection Systems (EDS) and Explosive Trace Detection (ETD) machines. The peak hour at Airport A generates **6,074 checked bags** (4,338 passengers) and Airport B generates **6,530 bags** (4,664 passengers). Because passengers arrive between 45 and 120 minutes before departure (a 75-minute window), the *instantaneous* screening rate — not simply the hourly bag count — determines the EDS requirement. Under three clearly stated planning assumptions the EDS requirements at a mid-range throughput of 180 bags/h and 92% availability are:

| Planning assumption | Airport A | Airport B |
|---|---|---|
| **M1** — clear all peak-hour bags inside the 60-min peak hour (conservative) | **37 EDS** | **40 EDS** |
| **M2** — size to the peak *arrival* rate (75-min pax window, base design) | **30 EDS** | **32 EDS** |
| **M3** — full departure-bank re-timing over 120 min (conditional on airline cooperation, f = 1) | **19 EDS** | **20 EDS** |

Adding ETD machines for alarm resolution is cheap (≈US$0.6 M per airport) and adds detection depth. **The M3 figure is not an unconditional result:** it requires airlines to re-time essentially the whole peak-hour departure bank, which an airport cannot enforce. We therefore report the requirement as a **conditional procurement curve** in the cooperation share `f` (share of peak-hour flights re-timed): at `f` = 0/25/50/75/100% the requirement is **A 30/27/24/22/19** and **B 32/29/26/23/20** EDS. We lead with the enforceable no-cooperation base (A 30, B 32) and present the curve in §6.3; full re-timing would halve the A+B EDS capital (US$83.9 M → US$43.6 M) but is an upper bound on savings, not an unconditional plan. Scaled to the 193 Midwest airports the base is ≈1,372 EDS (≈US$1.5 B capital); to all 429 U.S. airports ≈3,006 EDS (≈US$3.3 B).

All numbers in this report are produced by the reproducible script `code/baggage_model.py`, which writes `results/model_results.json`.

---

## 1. Problem Background and Restatement

The Transportation Security Administration (TSA) is mandated to screen **100% of checked bags** at 429 passenger airports using computed-tomography (CT) EDS machines. Each EDS costs ≈US$1 M plus installation, processes 160–210 bags/h, and is operational 92% of the time. Production capacity is limited and deployment is expensive, so airports must decide **how many EDS to install** and **how to schedule flights** so that a finite screening fleet can clear all bags before departure. Emerging ETD technology may supplement EDS more cheaply.

The seven requested tasks are:

1. **Model development** — how many EDS are needed at Airports A and B, using TIS Table 1.
2. **Position paper** — security objectives and constraints for airlines.
3. **Scheduling model** — schedule peak-hour departures at A and B.
4. **Recommendations** — to Mr. Sheldon and to the airlines.
5. **National impact memo** — adapt the models to the 193 Midwest airports and to national deployment.
6. **ETD augmentation** — modify the models to include ETD; count ETDs; assess schedule change and cost-effectiveness.
7. **Future research recommendations** — how advances in technology, cost, accuracy, speed and reliability change the answer.

### 1.1 TIS Table 1 — peak-hour flight departures

| Flight type | Seats/flight | Airport A flights | Airport B flights |
|---|---:|---:|---:|
| 1 | 34 | 10 | 8 |
| 2 | 46 | 4 | 6 |
| 3 | 85 | 3 | 7 |
| 4 | 128 | 3 | 5 |
| 5 | 142 | 19 | 9 |
| 6 | 194 | 5 | 10 |
| 7 | 215 | 1 | 2 |
| 8 | 350 | 1 | 1 |
| **Total** | | **46** | **48** |

Additional given facts: occupancy 70–100% for ≤85-seat flights, 60–100% for 128–215-seat flights, 50–100% for 350-seat flights; passengers arrive 45–120 minutes before departure; 20% check no bag, 20% check one bag, 60% check two bags; EDS installation US$100,000 at A and US$80,000 at B.

---

## 2. Assumptions and Justifications

| # | Assumption | Value / form | Justification |
|---|---|---|---|
| A1 | Occupancy treated as uniform on its stated range | U(0.70,1.00), U(0.60,1.00), U(0.50,1.00) | Only a range is given; the uniform law is the maximum-entropy choice with no further information, and the mean (=range midpoint) is used for the deterministic design. |
| A2 | Bag counts per passenger are i.i.d. categorical | P(0,1,2) = (0.20,0.20,0.60) | Given directly. Mean 1.4, variance 0.64. |
| A3 | Passengers for one flight arrive uniformly over [dep−120, dep−45] | 75-min window | Given arrival range 45–120 min before departure. |
| A4 | Bags must be screened and delivered before the aircraft's departure | deadline = departure | Screening is a prerequisite for boarding; a 15–30 min transport slack is absorbed in the 45-min lower arrival bound (sensitivity checked). |
| A5 | EDS throughput is constant over a "peak hour" | 160, 180 (base), 210 bags/h | Given range; 180 is the midpoint. |
| A6 | EDS availability 92% | η = 0.92 | Given. Effective capacity = throughput × η. |
| A7 | Screening must match the *peak* demand rate | min-max design | An EDS fleet is sized for the busiest period; under-sizing causes missed bags/flights. |
| A8 | EDS capital cost US$1 M, installation US$0.10 M (A)/US$0.08 M (B); 10-year life; 10%/yr maintenance | Given + standard TCO assumption | Problem gives unit & installation costs; maintenance/life are standard planning assumptions, flagged for sensitivity. |
| A9 | ETD: ≤180 samples/h certification floor, ≈90 bags/h effective; US$50 k unit + US$20 k installation | see §1 and references | The 180/h floor is a TSA certification requirement; the effective 90/h reflects swab acquisition/analysis overhead. Unit cost is a stated assumption (sensitised). |
| A10 | EDS alarm (secondary-resolution) rate 10% | p_a ∈ {5%,10%,20%} sensitised | EDS false-alarm/alarm rates are not given; 10% is a representative operating figure and is varied in sensitivity. |
| A11 | Daily bag volume ≈ 10 × busiest-hour volume; airports operate year-round | cost-per-bag only | Used only to normalise lifecycle cost; does not affect EDS counts. |
| A12 | Airport "peak hour" flights are the 46 (A) / 48 (B) given; a departure *bank* may be spread over H minutes | H ∈ [60,120] | Task 3 explicitly asks us to schedule departures; H is the decision variable. |

---

## 3. Data Description and Processing

### 3.1 External empirical data (workflow requirement)

Two verifiable empirical items materially inform the model:

1. **ETD throughput floor.** The U.S. Federal Register, *“Criteria for Certification of Explosives Trace Detection Systems,”* 67 FR 48436 (24 July 2002), requires an ETD to *“process a minimum of 180 samples per hour when no alarms are present (not including acquiring the sample).”* — **Use:** upper bound on ETD screening rate; because sample acquisition is excluded, we adopt an *effective* 90 bags/h per machine and show results for both 90 and 180 h⁻¹. Source: federalregister.gov (document 02-18611).
2. **Modern CT/EDS throughput.** Leidos *Reveal®* product data state the CT-80DR+ scans up to **226 bags/h** and the CT-800 up to **250 bags/h**, with fleet availability >99.5%. — **Use:** corroborates the 160–210 bags/h bracket supplied in the TIS and confirms that a mid-range value (180–210 h⁻¹) is realistic for certification-grade CT EDS. Source: leidos.com/products/reveal.

Corroborating context: the U.S. GAO reports that TSA uses **EDS for primary and ETD for secondary/other screening at 462 U.S. commercial airports** and has made >US$8 B available for checked-baggage screening since FY2001 — i.e., the two-tier architecture and the multi-billion-dollar national scale modelled here are realistic. Source: gao.gov/assets/a320909.html.

### 3.2 Demand computation

For an airport column (A or B), with flight types j = 1…8:

- Occupancy moments: `E[o_j] = (lo_j+hi_j)/2`, `Var[o_j] = (hi_j−lo_j)²/12`.
- Passengers: `P = Σ_j n_j · E[o_j] · s_j`.
- Checked bags: `Λ = 1.4 · P` with per-passenger variance `0.64`.
- Variance propagation across flights: `Var[Λ] = Σ_j n_j ( 1.4² Var[o_j] s_j² + 0.64 · E[o_j] s_j )`.

**Results** (per airport, peak hour):

| Airport | Flights | Seats | Passengers E[P] | Bags E[Λ] | SD(Λ) | 95th-pct bags |
|---|---:|---:|---:|---:|---:|---:|
| A | 46 | 5,396 | 4,338.2 | 6,073.6 | 160.7 | 6,337.8 |
| B | 48 | 5,781 | 4,664.4 | 6,530.2 | 167.9 | 6,806.4 |

Per-type bag contribution (Airport A / Airport B):

| Type | Seats | n_A | bags_A | n_B | bags_B |
|---|---:|---:|---:|---:|---:|
| 1 | 34 | 10 | 404.6 | 8 | 323.7 |
| 2 | 46 | 4 | 219.0 | 6 | 328.4 |
| 3 | 85 | 3 | 303.5 | 7 | 708.1 |
| 4 | 128 | 3 | 430.1 | 5 | 716.8 |
| 5 | 142 | 19 | 3,021.8 | 9 | 1,431.4 |
| 6 | 194 | 5 | 1,086.4 | 10 | 2,172.8 |
| 7 | 215 | 1 | 240.8 | 2 | 481.6 |
| 8 | 350 | 1 | 367.5 | 1 | 367.5 |
| **Σ** | | **46** | **6,073.6** | **48** | **6,530.2** |

Airport B handles slightly more bags than A despite similar flight counts, because its mix is skewed toward the large types 3–7 (as few as 19 widebodies carry ~3,000 bags at A, versus B's many 194-seaters).

---

## 4. Model Construction

### 4.1 The arrival-window (fluid) screening model

Let `Λ` be an airport's peak-hour bag volume and let every flight's bags arrive uniformly over a window of length `W = 75` min. If the airport's departures are spread over a span `H` minutes, the aggregate bag-arrival rate `r(t)` (bags/min) is a trapezoid whose **peak** is

```
r_peak(H) = Λ / max(H, W).                                          (1)
```

*Derivation.* A flight departing at time `d` contributes `Λ_f/W` bags per minute over `[d−120, d−45]`. Summing over a uniform departure density of `N/H` flights/min and `N·Λ̄ = Λ`:

`r(t) = (N/H)(Λ̄) · [window overlap fraction]`, and the maximum overlap is the full window whenever `H ≤ W`, giving `r_peak = Λ/W`. When `H > W` the sliding window can no longer contain all departures, and `r_peak = Λ/H`.

**Key structural consequence.** Because the arrival window (75 min) is *longer* than the peak hour (60 min), **every flight's arrival window overlaps** and `r_peak = Λ/75` is **invariant** for any schedule confined to the peak hour. Scheduling *inside* the hour cannot reduce the EDS requirement; only *stretching the departure bank beyond 75 minutes* can. This is the central scheduling insight of Task 3 (verified numerically in §6.3, where H = 60 and 75 give identical results).

### 4.2 EDS sizing

An EDS fleet of `N` machines provides effective capacity `N·c·η` bags/h (`c` = throughput, `η` = 0.92). Requiring capacity ≥ peak demand rate:

```
N(H) = ⌈ 60 · r_peak(H) / (c · η) ⌉ = ⌈ 60 Λ / ( max(H,75) · c · η ) ⌉.   (2)
```

Three planning assumptions map onto (2):

- **M1 (conservative / "clear-the-hour"):** pretend all `Λ` bags must be cleared *within* the 60-minute peak hour, i.e. `N = ⌈Λ/(cη)⌉` (equivalent to `H = 60` in an aggregate, non-windowed reading).
- **M2 (base design):** physical arrival model with the bank confined to the peak hour, `H = 60 → max = 75`, so `N = ⌈60Λ/(75 c η)⌉ = ⌈0.8 Λ/(cη)⌉`.
- **M3 (scheduling):** the bank is spread over `H > 75`, `N = ⌈60Λ/(H c η)⌉`.

### 4.3 Stochastic (risk-based) sizing

Replace `Λ` by a 95% upper quantile `Λ^0.95 = E[Λ] + 1.6449·SD(Λ)` from §3.2, then apply (2). This buffers against random occupancy and bag-checking behaviour (a ~4–5% uplift for these airports).

### 4.4 Scheduling optimization model

Decision variable: the departure-time distribution of the `N` flights. Objective: minimise the peak screening rate `r_peak`, i.e. minimise the required EDS fleet (equivalently the lifecycle capital `N(H)·(C_EDS+I_EDS)`). Because a fluid trapezoid is minimised by the most uniform loading, the **optimal schedule is a uniform spread of the departure bank over the widest feasible span `H`**.

The feasible `H` is set by a system-cost trade-off:

```
minimise over H:   C(H) = TCO(N(H)) + Life · D(H),                  (3)
TCO(N)  = (1 + m·Life) · N · (C_EDS + I_EDS),   m = 0.10,           (4)
D(H)    = p · N_flights · (H − 60)/4,           p = US$120/flight-min,  (5)
```

where `D(H)` is an airline disruption/inconvenience penalty (connecting waves, curfews, runway-slot contracts, passenger preference) proportional to the average displacement of flights from the nominal 60-min bank. We additionally impose a hard operational cap `H ≤ 120` min (§6.3). The uniform schedule is then realised as a concrete slot assignment by a greedy longest-processing-time rule that equalises bag load per 15-minute block (**the deliverable schedule**).

**Adoption (enforceability) parameter `f`.** The airport can request but cannot compel airlines to re-time flights, so we do not treat bank-widening as certain. Let a share `f` of peak-hour flights be re-timed into the widened bank (span `H`) while `1−f` remain in the 60-minute core. The core flights still overlap fully, so the peak rate is a convex blend:

```
r_peak(f) = Λ [ (1−f)/75 + f/H ],    N(f) = ⌈ 60 r_peak(f) / (c η) ⌉.   (3a)
```

Equation (3a) reproduces M2 at `f = 0` and M3(H = 120) at `f = 1`. Because `f` is a behavioural/policy quantity with no evidential basis for a point value, §6.3 reports the whole curve `N(f)` (with break-even shares) instead of a single optimum, and the report leads with the enforceable `f = 0` design.

### 4.5 ETD-augmented model

Two configurations are analysed.

**(a) Secondary (alarm-resolution) ETD.** Every bag is primary-screened by EDS; the fraction `p_a` that alarms is resolved by ETD (trace swab):

```
N_ETD = ⌈ Λ · p_a / (c_E · η) ⌉.                                    (6)
```

This is the architecture TSA actually uses (GAO, 2018).

**(b) Primary-mix ETD.** A fraction `φ` of bags is primary-screened by ETD and `1−φ` by EDS, subject to a detection constraint `P_D(mix) ≥ P_D*`. The unit cost per unit of screening *capacity* is

```
EDS:  C_EDS / (c · η)   vs.   ETD:  C_E / (c_E · η).
```

With `C_EDS = US$1 M`, `c = 180`, `C_E = US$50 k`, `c_E = 90`, the EDS cost per 1,000 bags/h of capacity is **US$6.04 M** versus **US$0.604 M** for ETD — a factor **10**. Pure cost minimisation therefore drives `φ → 1` (all-ETD), but this is infeasible: trace detection cannot reliably detect bulk explosives at the detection probability required of EDS. The optimisation is therefore *cost minimisation subject to a binding detection constraint*, and **ETD complements rather than replaces EDS**.

### 4.6 Cost model

Capital and 10-year total cost of ownership (TCO) are computed as `capex = N_EDS(C_EDS+I_EDS) + N_ETD(C_E+I_E)`, `TCO = (1+10·0.10)·capex`. A per-bag normalisation uses annual bags ≈ 10 × peak-hour bags × 365.

### 4.7 Regional / national scaling model

We model the 193-airport Midwest region and the 429-airport national system as a **hub-and-spoke size distribution**: 5% "large" airports (A/B scale), 15% medium (0.5× the peak flights), 30% small (0.2×), 50% very small (0.05×). EDS per airport scales with the M2 requirement.

---

## 5. Solution Process and Implementation

- **Language / environment:** Python 3.13 with NumPy (demand moments, variance propagation), executed on the analysis host.
- **Reproducibility:** `python code/baggage_model.py` regenerates every number and writes `results/model_results.json`. Inputs are also stored as `data/table1_peak_hour_flights.csv`.
- **Pipeline:** (i) read Table 1 → (ii) compute occupancy/passenger/bag moments and 95th-percentile volumes → (iii) apply equations (2)–(6) for M1/M2/M3, stochastic, ETD and cost → (iv) sweep `H` and solve (3) → (v) build the concrete schedule → (vi) sensitivity sweeps → (vii) regional/national scaling.

---

## 6. Results and Analysis

### 6.1 Bag demand

| Airport | Passengers | Bags (mean) | Bags (SD) | Bags (95th pct) | Peak rate `r_peak` (bags/min) | Peak rate (bags/h) |
|---|---:|---:|---:|---:|---:|---:|
| A | 4,338.2 | 6,073.6 | 160.7 | 6,337.8 | 80.98 | 4,858.8 |
| B | 4,664.4 | 6,530.2 | 167.9 | 6,806.4 | 87.07 | 5,224.2 |

### 6.2 EDS requirements (Task 1)

**Deterministic requirement by method and throughput:**

| Throughput (bags/h) | A: M1 | A: M2 | A: M3 (H=120) | B: M1 | B: M2 | B: M3 (H=120) |
|---|---:|---:|---:|---:|---:|---:|
| 160 | 42 | 34 | 21 | 45 | 36 | 23 |
| **180 (base)** | **37** | **30** | **19** | **40** | **32** | **20** |
| 210 | 32 | 26 | 16 | 34 | 28 | 17 |

**Base case (throughput 180, η = 0.92):**

- **Method M1:** A = **37 EDS**, B = **40 EDS**.
- **Method M2 (recommended design basis):** A = **30 EDS**, B = **32 EDS**.
- **Stochastic M2 (95th percentile):** A = 31, B = 33 — i.e. add ~1 machine.

**Interpretation.** The naive "bags per hour ÷ hourly capacity" calculation (M1) overstates the fleet by ~23% because it ignores that passengers arrive up to two hours early, which stretches the demand over a longer window. M2 is the physically correct peak-rate design; M1 is retained as a conservative upper bound. Rounding up to whole machines and the 92% availability already absorb most of the stochastic variation; the 95%-risk design (M2 +1) is recommended if the airport wishes to hold a hard service level.

### 6.3 Scheduling results (Task 3)

**Peak screening rate vs departure-bank span `H` (throughput 180, EDS = ⌈60Λ/(H·cη)⌉, H≥75):**

| H (min) | A: peak rate (bags/h) | A: EDS | B: peak rate (bags/h) | B: EDS |
|---:|---:|---:|---:|---:|
| 60 | 4,858.8 | 30 | 5,224.2 | 32 |
| 75 | 4,858.8 | 30 | 5,224.2 | 32 |
| 90 | 4,049.0 | 25 | 4,353.5 | 27 |
| 105 | 3,470.6 | 21 | 3,731.6 | 23 |
| 120 | 3,036.8 | 19 | 3,265.1 | 20 |
| 150 | 2,429.4 | 15 | 2,612.1 | 16 |
| 180 | 2,024.5 | 13 | 2,176.7 | 14 |
| 240 | 1,518.4 | 10 | 1,632.6 | 10 |

**Findings.** (i) H = 60 and H = 75 are *identical* — confirming the invariance result of §4.1: **within-hour rescheduling cannot reduce the EDS requirement.** (ii) Widening the bank has sharply diminishing returns and large operational cost; the system-cost optimum (3) under the `H ≤ 120` cap is **H\* = 120 min**, at which A needs **19** and B needs **20 EDS** — roughly a **37% reduction** versus the un-scheduled M2 design. (iii) Beyond H ≈ 120 min the marginal EDS saving (~US$1 M per 2–3 machines) is small relative to airline disruption and the loss of the "peak" concept, so we do not recommend stretching further.

**Recommended departure schedule (uniform 120-min bank, 8 × 15-min blocks).** Blocks are labelled 0–120 minutes relative to the start of the extended bank (e.g. 06:30–08:30 with the nominal 07:00–08:00 peak in the middle).

*Airport A (46 flights):*

| Block | Window (min) | Flight-type counts | Flights | Bag load |
|---:|---|---|---:|---:|
| 1 | 0–15 | T1×2, T5×2, T8×1 | 5 | 767 |
| 2 | 15–30 | T1×1, T2×1, T3×1, T5×2, T7×1 | 6 | 755 |
| 3 | 30–45 | T1×1, T5×3, T6×1 | 5 | 735 |
| 4 | 45–60 | T1×1, T2×1, T4×1, T5×2, T6×1 | 6 | 774 |
| 5 | 60–75 | T1×1, T2×1, T4×1, T5×2, T6×1 | 6 | 774 |
| 6 | 75–90 | T1×2, T4×1, T5×2, T6×1 | 6 | 760 |
| 7 | 90–105 | T1×2, T2×1, T3×1, T5×2, T6×1 | 7 | 772 |
| 8 | 105–120 | T3×1, T5×4 | 5 | 737 |

*Airport B (48 flights):*

| Block | Window (min) | Flight-type counts | Flights | Bag load |
|---:|---|---|---:|---:|
| 1 | 0–15 | T1×1, T3×1, T4×1, T5×1, T8×1 | 5 | 812 |
| 2 | 15–30 | T1×1, T2×1, T4×1, T5×2, T7×1 | 6 | 797 |
| 3 | 30–45 | T1×1, T2×1, T4×1, T5×2, T7×1 | 6 | 797 |
| 4 | 45–60 | T1×1, T3×2, T5×1, T6×2 | 6 | 836 |
| 5 | 60–75 | T1×1, T3×2, T5×1, T6×2 | 6 | 836 |
| 6 | 75–90 | T2×2, T3×1, T5×1, T6×2 | 6 | 804 |
| 7 | 90–105 | T1×2, T2×1, T3×1, T5×1, T6×2 | 7 | 830 |
| 8 | 105–120 | T1×1, T2×1, T4×2, T6×2 | 6 | 817 |

Bag load is held within ±5% of the mean per block (A: mean 759, range 735–774; B: mean 816, range 797–836), which is what flattens the screening curve and delivers the M2 → M3 saving. Equivalently, an airline can keep the 60-minute pattern and instead **diversify the aircraft/bag mix per slot**, but the dominant lever is the *width* of the bank.

**6.3.1 Adoption-conditional procurement curve (confidence boundary).** The M3 schedule presumes every flight can be re-timed. Since the airport cannot enforce that, we replace the single optimum with the conditional curve of equation (3a). The results below are the operative planning result for Task 3:

| Re-timing share `f` | A peak rate (bags/h) | A EDS | B peak rate (bags/h) | B EDS |
|---:|---:|---:|---:|---:|
| 0.00 (no cooperation, base) | 4,858.8 | **30** | 5,224.2 | **32** |
| 0.25 | 4,403.3 | 27 | 4,734.4 | 29 |
| 0.50 | 3,947.8 | 24 | 4,244.6 | 26 |
| 0.75 | 3,492.3 | 22 | 3,754.9 | 23 |
| 1.00 (full adoption) | 3,036.8 | 19 | 3,265.1 | 20 |

**Break-even cooperation shares.** Airport A reaches 27 EDS once `f ≥ 0.22` and 25 EDS once `f ≥ 0.40`; Airport B reaches 30 EDS at `f ≥ 0.14`, 27 at `f ≥ 0.39` and 25 at `f ≥ 0.56`. Each 25 percentage-points of re-timing is worth ≈3 EDS (≈US$3.3 M of deferred capital for A+B).

**Confidence boundary.** The defensible procurement range is **A 19–30 / B 20–32 EDS**; the enforceable floor is the no-cooperation base **A 30 / B 32**, and the full-adoption value **A 19 / B 20** is a best case that should not be presented as a plan. We therefore recommend procuring to the base and holding the re-timing savings as a conditional benefit contingent on measured cooperation.

### 6.4 ETD results (Task 6)

**Secondary (alarm-resolution) ETD counts** `N_ETD = ⌈Λ·p_a/(c_E·η)⌉`:

| Alarm rate `p_a` | A (c_E=90) | A (c_E=180) | B (c_E=90) | B (c_E=180) |
|---|---:|---:|---:|---:|
| 5% | 4 | 2 | 4 | 3 |
| **10% (base)** | **8** | **4** | **8** | **5** |
| 20% | 15 | 8 | 16 | 9 |

**Cost-effectiveness.** At a 10% alarm rate A needs **8 ETD** and B **8–9 ETD**, at a capital cost of only ≈US$0.56–0.63 M — trivial next to the EDS fleet (US$33–36 M). ETD therefore delivers **very high marginal security per dollar** as a second layer. Conversely, using ETD as a *primary* screening technology costs about **1/10** per unit of capacity, but cannot meet the bulk-explosive detection requirement, so the cost-minimising *and* compliant policy is **EDS primary + ETD secondary** (equivalently, augment EDS at low-volume airports with ETD where EDS installation is uneconomic). Schedule impact of adding ETD is minimal: alarm resolution is a small side-flow (≈10% of bags) and can run in parallel with primary screening, so the M2/M3 schedules stand.

### 6.5 Cost and policy comparison (Tasks 1 & 6)

**Capital cost across policies (A + B, US$; EDS 180 bags/h, base 10% alarm for ETD):**

| Policy | A EDS | B EDS | ETD (A+B) | Capital (US$) |
|---|---:|---:|---:|---:|
| **P0** — EDS only, M1 (conservative) | 37 | 40 | 0 | **83,900,000** |
| **P1** — EDS (M2) + ETD alarm resolution | 30 | 32 | 16 | **68,680,000** |
| **P2** — EDS (M3, H=120) + ETD alarm resolution | 19 | 20 | 16 | **43,620,000** |

Adding ETD to P1 costs ≈US$1.1 M but creates the TSA-standard two-tier architecture. Adopting the scheduling (P2) saves a further **US$25.1 M** in capital — but P2 assumes full re-timing (`f = 1`), so it is conditional. At the enforceable no-cooperation base the recommended policy is **P1 (US$68.7 M)**. Selected base-design costs (M2 + ETD, 95%-risk sizing): Airport A — 31 EDS + 8 ETD, capex US$34.7 M, 10-yr TCO US$69.3 M, ≈US$0.31/bag; Airport B — 33 EDS + 9 ETD, capex US$36.3 M, 10-yr TCO US$72.5 M, ≈US$0.30/bag.

**Marginal economics.** Each additional EDS buys 165.6 bags/h of capacity for US$1.1 M; each additional ETD buys 82.8 bags/h for US$0.07 M. Because detection requirements bind, the optimal marginal dollar is spent on **ETD as a complementary layer**, not as an EDS substitute.

### 6.6 Regional and national scaling (Task 5)

Under the M2 design basis (throughput 180):

| Tier | Share | Region: airports | EDS each | Region EDS | Nation: airports | Nation EDS |
|---|---:|---:|---:|---:|---:|---:|
| Large (A/B scale) | 5% | 10 | 31 | 310 | 21 | 651 |
| Medium (0.5×) | 15% | 29 | 16 | 464 | 64 | 1,024 |
| Small (0.2×) | 30% | 58 | 7 | 406 | 129 | 903 |
| Very small (0.05×) | 50% | 96 | 2 | 192 | 214 | 428 |
| **Total** | 100% | **193** | — | **1,372** | **429** | **3,006** |

Capital: **≈US$1.50 B** for the Midwest region, **≈US$3.28 B** nationally (at ≈US$1.09 M per EDS including installation). These are order-of-magnitude consistent with TSA's actual deployment program (>US$8 B committed, ≈462 airports — GAO), and they expose the core tension in the mandate: **national EDS demand (≈3,000 machines) far exceeds near-term CT production capacity**, which is precisely why a phased rollout and ETD supplementation are necessary (memo, §8).

---

## 7. Validation and Sensitivity Analysis

**Model validation.** (i) The demand model reproduces the given totals exactly from Table 1 and is internally consistent (bags = 1.4 × passengers). (ii) The arrival-window model reduces correctly to the aggregate model as `W → 0` and yields the invariance property H=60 ≡ H=75, which we verified numerically. (iii) The peak-rate trapezoid integrates to the total bag volume (`∫r dt = Λ`) in all cases. (iv) Computed EDS counts bracket the certification-grade throughputs reported for real machines (226–250 bags/h, Leidos).

**Sensitivity of the EDS requirement (Airport A / Airport B, M2 basis):**

| Factor | Perturbation | A EDS | B EDS |
|---|---|---|---|
| Throughput (bags/h) | 160 / 180 / 210 | 34 / 30 / 26 | 36 / 32 / 28 |
| Occupancy multiplier | 0.90 / 1.00 / 1.10 | 27 / 30 / 33 | 29 / 32 / 35 |
| Bags per passenger | 1.0 / 1.4 / 1.8 | 21 / 30 / 38 | 23 / 32 / 41 |
| EDS availability | 0.80 / 0.92 / 1.00 | 34 / 30 / 27 | 37 / 32 / 30 |

**Reading of the sensitivity.** The requirement is most sensitive to **bags-per-passenger** (±27% for ±29% change) and to **throughput** (a 30% throughput gain cuts the fleet by ~13%), and moderately sensitive to **occupancy** and **availability**. Because ETD/secondary capacity and staffing scale the same way, the model's policy conclusions (two-tier architecture; schedule stretching; ETD as the cheap complement) are robust across the whole parameter envelope. The single most valuable engineering target is therefore **higher EDS throughput** (see §9).

---

## 8. Special Deliverables

### 8.1 Position paper — security objectives and constraints for airlines (Task 2)

**Objectives.**
1. **Deterrence & prevention:** screen 100% of checked bags so that no explosive device reaches an aircraft hold.
2. **Detection performance:** achieve a high probability of detection `P_D` at an acceptable false-alarm rate `FAR`; the model's two-tier EDS+ETD design supports this.
3. **Throughput / schedule integrity:** screening must not delay departures; the TIS shows the airline's real constraint is the *peak-hour bank* (46 flights / ≈5,400 seats at A; 48 flights / ≈5,800 seats at B).
4. **Equity of service:** every passenger and every flight type (from 34-seat regionals to 350-seat widebodies) must be screened to the same standard.
5. **Cost efficiency:** minimise total cost per bag while meeting (1)–(2); Table 1 quantifies the demand that all cost decisions hinge on.

**Constraints.**
- **Physical/space:** EDS footprint and baggage-handling interfaces limit machines per terminal; installation cost (US$100 k at A, US$80 k at B) reflects retrofit complexity.
- **Budget:** each EDS ≈US$1 M plus installation; the model shows a full M1 build at A+B costs ≈US$84 M versus ≈US$44 M with scheduling + ETD.
- **Supply:** CT production cannot meet the 429-airport mandate at once → phased deployment.
- **Reliability:** EDS are available only 92% of the time → fleet sizing must include the `η` factor.
- **Arrival-time behaviour:** passengers arrive 45–120 min before departure (75-min window) → the screening load is inherently smoothed; scheduling in the hour cannot change the peak, only bank-width can.
- **Bag-mix:** 60% of passengers check two bags (mean 1.4 bags/passenger) — the principal demand driver.
- **Time-of-day:** peak hours concentrate demand; departure-bank design is the airline's main controllable lever.
- **Privacy/labour:** CT imaging and manual resolution raise privacy and staffing constraints.

The TIS Table 1 directly parameterises (3)–(7): flight counts and seat capacities set passengers; occupancy ranges set the load factor; the bag-check distribution sets `Λ`; and the arrival window sets the smoothing.

### 8.2 Recommendations to Mr. Sheldon and the airlines (Task 4)

1. **Size EDS to the peak *arrival rate*, not the raw hourly bag count.** At A and B this lowers the requirement from 37/40 (M1) to 30/32 (M2) machines — a saving of ≈US$15 M in capital.
2. **Pursue departure-bank re-timing as a *conditional* lever, not a baseline assumption.** Since re-timing cannot be enforced, scope procurement to the no-cooperation requirement (30/32 at throughput 180) and treat any reduction as contingent on the achieved cooperation share `f`: at `f` = 25% the requirement falls to 27/29, at 50% to 24/26, and only at full adoption to 19/20 (§6.3). Each 25% of cooperation is worth roughly 3 EDS (≈US$3.3 M); break-even shares are A `f ≥ 0.22` for 27 EDS and B `f ≥ 0.14` for 30 EDS.
3. **Do not expect in-hour rescheduling to help.** Because the passenger arrival window exceeds the peak hour, the peak screening rate is invariant within the hour; effort should go to bank width and to reducing bags-per-passenger peaks.
4. **Adopt a two-tier EDS + ETD policy.** Adding ≈8 ETD per airport for alarm resolution costs ≈US$0.6 M yet adds a second detection layer and is the standard TSA architecture; the ETD marginal security-per-dollar is an order of magnitude better than an extra EDS.
5. **Phase deployment & standardise procurement.** Given production limits, deploy EDS first at the largest, highest-risk airports (the "large" tier in §6.6); redeploy the freed M2 capacity where it matters most.
6. **Fund throughput R&D.** Sensitivity shows a 30% throughput gain removes ~13% of each fleet; it is the single highest-leverage quantitative target.

### 8.3 National impact memo (Task 5)

*To: Regional aviation-security leadership. Subject: Scaling the A/B screening models to the 193 Midwest airports and the national system.*

- **Adaptation.** The A/B models are **scale-invariant**: all inputs are per-flight (seats × occupancy × bags-per-passenger) and the single structural parameter is peak bag volume. For any airport, substitute its own Table-1 equivalent (distribution of flights by seat capacity within the peak bank) into equations (2)–(6). Our hub-and-spoke tier model (§6.6) assigns 5% of airports A/B-scale demand, 15% medium, 30% small, 50% very small.
- **Regional requirement.** 193 Midwest airports ⇒ **≈1,372 EDS** (≈US$1.50 B) under M2; the bulk of machines (~60%) sit at the 39 large/medium airports.
- **National requirement.** 429 airports ⇒ **≈3,006 EDS** (≈US$3.28 B). This is consistent in order of magnitude with TSA's >US$8 B program across ≈462 airports (GAO).
- **Implementation path.** (1) Standardise a per-airport demand template; (2) rank airports by peak bag volume and threat exposure; (3) deploy EDS to the top tiers first; (4) use ETD to cover low-volume airports where a full EDS lane is uneconomic; (5) re-run the schedule model once machine throughput improves; (6) monitor occupancy/bag-mix drift, since bags-per-passenger is the dominant sensitivity.
- **Risk.** The mandate's binding constraint is **production capacity**, not demand modelling; staged deployment plus ETD bridging is the pragmatic answer.

### 8.4 Future research recommendations (Task 7)

- **Device technology:** multi-energy/dual-energy CT with material classification, automated threat recognition, and higher tunnel throughput (Leidos-class 226–250 bags/h shows headroom beyond the 160–210 baseline). Quantify `P_D`/`FAR` jointly, since our model treats throughput and detection separately.
- **Cost:** reduce EDS unit cost and installation (currently ≈US$1.1 M all-in); a 20% cost cut translates almost linearly into a ≈US$0.6 B national saving.
- **Speed/throughput:** each +10% throughput removes ≈4% of the fleet (§7). Research on conveyor speed, reconstruction speed and alarm-rate reduction is high-value.
- **Reliability:** raising availability from 92% toward 99% (as modern CT families claim) removes ≈2–5 machines per large airport.
- **Detection science:** trace-detection sensitivity for bulk explosives (to enlarge ETD's legitimate role), non-linear imaging, and adversarial/obfuscation robustness.
- **Operations research:** queueing-theoretic (M/D/c) models of EDS lanes with time-varying arrivals and hard deadlines; stochastic scheduling that trades bank width, gate capacity and connection risk.
- **Human factors & policy:** staffing models for alarm resolution, privacy-preserving imaging, and standardised certification test protocols.
- **Data science:** machine-learning anomaly detection to raise `P_D` at fixed `FAR`, and empirical re-estimation of the occupancy and bags-per-passenger distributions — the dominant model sensitivities — via airport-level data collection.

---

## 9. Strengths, Limitations, and Improvements

**Strengths.** The model is analytic, transparent, fully reproducible, and structurally insightful: it derives the *arrival-window invariance* that reduces the whole scheduling question to one control variable (bank width `H`); it quantifies demand with formal moments and risk quantiles; it separates three defensible planning assumptions (M1/M2/M3); it integrates EDS, ETD, cost and national scaling in one framework; and its outputs are bracketed by real device data (Leidos) and real policy architecture (GAO/Federal Register).

**Limitations.** (i) Occupancy and bag-checking are treated as independent and uniform — real arrivals correlate with flight, time and carrier. (ii) A fluid/deterministic treatment of arrivals; a full M/D/c queueing analysis with finite lane buffers would refine the buffer. (iii) The disruption cost `D(H)` is a simple linear surrogate for complex airline economics. (iv) ETD throughput (90 bags/h effective) and cost are assumptions, though sensitised. (v) The regional tier decomposition is a stylised size distribution, not actual airport-level data. (vi) The re-timing share `f` is a behavioural/policy quantity the airport cannot enforce; rather than assume full cooperation, we report the requirement as a conditional curve over `f` (§6.3) and lead with the no-cooperation base case, so the headline number does not rest on an unenforceable assumption.

**Improvements.** Replace uniform occupancy with empirical load-factor distributions; calibrate `D(H)` from airline schedule/connectivity data; add a stochastic time-varying queueing model with deadline violations; and validate against observed airport EDS lane counts. None of these change the qualitative conclusions.

---

## 10. Conclusions

1. **EDS requirement (Task 1).** Airport A needs **37/30/19** and Airport B **40/32/20** EDS under the conservative (M1), base (M2) and scheduled (M3, H=120) assumptions at 180 bags/h; the recommended design basis is **M2 (A 30, B 32)** — 31/33 if a hard 95% service level is required.
2. **Position paper (Task 2).** Objectives: 100% screening, high `P_D`, schedule integrity, equity and cost efficiency. Constraints: space, budget, EDS supply (92% availability), the 45–120-min arrival window and the 1.4-bags/passenger demand profile.
3. **Scheduling (Task 3).** Within the peak hour the peak screening rate is **invariant** (75-min arrival window > 60-min bank); widening the bank to **120 min** cuts the requirement to **A 19 / B 20** EDS *only if all flights are re-timed*. Because that cooperation is unenforceable, the operative result is the conditional curve **A 30→27→24→22→19** and **B 32→29→26→23→20** EDS at re-timing shares `f` = 0/25/50/75/100% (§6.3); the recommended schedule keeps bag load within ±5% of the mean and the enforceable base is A 30 / B 32.
4. **Recommendations (Task 4).** Size to the arrival rate; design a 120-min bank; add ETD as a cheap second layer; phase deployment by risk; fund throughput R&D.
5. **National memo (Task 5).** 193 Midwest airports ⇒ **≈1,372 EDS (≈US$1.5 B)**; 429 national ⇒ **≈3,006 EDS (≈US$3.3 B)**; the binding constraint is production capacity, so stage deployment and bridge with ETD.
6. **ETD (Task 6).** Secondary ETD for alarm resolution: **≈8 per airport** at 10% alarm rate (cost ≈US$0.6 M), negligible schedule impact, and the highest marginal security-per-dollar; ETD is 10× cheaper per unit capacity but cannot replace EDS because detection requirements bind.
7. **Future research (Task 7).** Priorities: higher-throughput/lower-cost CT, improved availability, trace sensitivity for bulk explosives, ML anomaly detection, queueing-based stochastic scheduling, and empirical re-estimation of occupancy and bag-mix distributions.

The answer to "to screen or not to screen" is unequivocal: **screen everything** — but screen *smart*, by sizing to the true peak arrival rate, by widening the departure bank, and by pairing CT-based EDS with cheap ETD resolution.

---

## References

1. ICM 2003 problem statement and Technical Information Sheet — *Aviation Baggage Screening Strategies: To Screen or Not to Screen, that is the Question* (Tables 1; EDS cost/throughput/availability; arrival and bag-checking statistics).
2. U.S. Federal Register, *Criteria for Certification of Explosives Trace Detection Systems*, 67 FR 48436 (24 July 2002) — ETD ≥180 samples/hour (excl. sample acquisition). https://www.federalregister.gov/documents/2002/07/24/02-18611/criteria-for-certification-of-explosives-trace-detection-systems
3. Leidos, *Reveal® Baggage Inspection Systems* product data — CT-80DR+ up to 226 bags/h, CT-800 up to 250 bags/h, availability >99.5%. https://www.leidos.com/products/reveal
4. U.S. Government Accountability Office, report on TSA explosives-detection requirements / checked-baggage screening (EDS primary + ETD; 462 airports; >US$8 B committed). https://www.gao.gov/assets/a320909.html
5. TSA, *Technology* fact sheet — EDS CT screening of 100% of checked baggage; ETD trace screening. https://www.tsa.gov/news/press/factsheets/technology

*Reproducibility:* all numerical results were generated by `code/baggage_model.py` (Python 3.13 + NumPy) and stored in `results/model_results.json`; inputs in `data/table1_peak_hour_flights.csv`.
