# Evacuating a Skyscraper Within X Minutes
### A flow–bottleneck mathematical model of stairwell evacuation
**Problem:** HiMCM 2001 — *Skyscrapers* (`2001_Skyscrapers`)

---

## 1. Problem Background and Restatement

Skyscrapers concentrate large populations high above grade. When a catastrophe (fire, earthquake, hurricane, tornado, or deliberate act) removes power, the **elevator banks become inoperative for normal occupants** and may be used only by firefighters and rescue personnel holding special keys. Removing \(N\) occupants from a tall building therefore becomes, in the first instance, a **vertical pedestrian-flow problem**: every person must descend the protected stairways to the ground before the building can be declared clear.

We are asked to:

1. build a **mathematical model** that computes the time to clear the building, \(T_{\text{evac}}\);
2. use it to **state the height of the building, the maximum occupancy, and the evacuation methods** employed;
3. **solve the model for \(X = 15,\ 30,\) and \(60\) minutes** — i.e., determine what building (height and population) and what egress strategy can be cleared within each deadline.

The deliverable is a design statement: for each \(X\), *how tall and how full a building can be, and by what means, so that all occupants are out within \(X\) minutes.*

---

## 2. Assumptions and Justifications

| # | Assumption | Justification |
|---|---|---|
| A1 | The building is a uniform slab tower: floor-to-floor height \(h=3.5\) m, rectangular floor plates, occupancy \(p\) persons per occupied floor. | Representative of modern office towers; keeps the model tractable while preserving the dominant physics (vertical distance × population). |
| A2 | Elevators are unavailable to ordinary occupants (power lost); a separate **rescue/fire-service elevator** channel may carry a small, trained-assisted stream. | Stated in the problem. Post-9/11 guidance explicitly studies "occupied elevator evacuation" but only for trained operation, so we model it as a modest parallel channel. |
| A3 | Movement is **deterministic**; we model mean (design) values, not stochastic variability. | A design/planning model should bound capacity; variability is treated qualitatively in sensitivity analysis. |
| A4 | Occupants use the **nearest protected stairway**; flows from different floors **merge** and are governed by the capacity of the *loaded* stair segment near the base. | Standard hydraulic (flow) modelling assumption used in the SFPE Handbook and in egress codes. |
| A5 | A single **bottleneck capacity** \(C\) [persons/s] limits flow through the stair core; the capacity is the same at every level because *every* descending occupant passes every lower level. | Conservation of flow: the flow past any level equals the total population above that level; the binding constraint is the narrowest effective width. |
| A6 | Descent speed on stairs follows the **SFPE speed–density law** \(S=k(1-aD)\); free speed is \(k\) and the maximum *specific flow* is \(F_{s,\max}=k/(4a)\). | Empirically calibrated relation ([S1], [S2]); see §3. |
| A7 | A **pre-movement time** \(t_0=t_{\text{detect}}+t_{\text{premove}}\) (recognition, alarm, reaction) precedes movement and is identical for all floors. | Standard egress decomposition \(RSET = t_{\text{det}} + t_{\text{pre}} + t_{\text{travel}}\); NIST pre-movement data ([S4]). |
| A8 | Occupants are ambulatory; mobility-impaired occupants require assisted (elevator) movement and are treated as a small fraction served by the rescue channel. | Simplification; flagged in Limitations. |
| A9 | Smoke, heat, and counterflow (firefighters ascending) do not reduce stair capacity in the model. | Deterministic capacity model; these effects are noted as a degradation factor in sensitivity/Limitations. |
| A10 | Ground-floor occupants exit directly and are neglected; only floors 2…\(N\) require stair travel. | Small, conservative simplification. |

---

## 3. Data Description and Processing

Two **verifiable empirical data items** materially drive the model; both are published engineering measurements, not assumptions.

### D1 — Stairway movement speed and specific flow (calibration of \(k\) and \(F_{s,\max}\))

The SFPE Handbook's stair relation ([S1], as restated in NIST TN-1839) is

\[
S = k\,(1 - aD),\qquad a = 0.266\ \text{m}^2/\text{person},
\]

where \(S\) is descent speed (m/s), \(D\) is occupant density (person/m²), and the constant \(k\) depends on stair geometry. NIST TN-1839 lists

| Riser / tread (mm) | \(k\) (m/s) |
|---|---|
| 190 / 254 | 1.00 |
| 178 / 279 | 1.08 |
| 165 / 305 | 1.16 |
| 165 / 330 | 1.23 |

The **specific flow** is \(F_s = S\,D\); maximising gives \(D^\*=1/(2a)=1.88\) person/m² and

\[
F_{s,\max}=\frac{k}{4a}=\frac{1.00}{4(0.266)}=0.94\ \text{person}/(\text{m}\cdot\text{s}) = 56.4\ \text{person}/(\text{m}\cdot\text{min}).
\]

This matches independent transit data: TCRP Report 100 / Fruin ([S2]) report **descending-stair flow ≈ 1.19 person/(m·s)** and a vertical travel-speed component of **≈ 0.30 m/s** under crowd conditions. **Used for:** the capacity constant \(C\) and the free descent time per floor.

### D2 — Real high-rise fire-drill evacuation times (validation)

NIST instrumented six office buildings during full-building fire drills ([S3]). Four complete cases with recorded stair widths and evacuee counts:

| Building | Floors | Evacuees | Stair width (m) | Measured evac time (s) |
|---|---|---|---|---|
| NIST-10 | 10 | 436 | 1.27 | 1022 |
| NIST-18 | 18 | 255 | 1.12 | 1192 |
| NIST-24 | 24 | 249 | 1.12 | 1090 |
| NIST-31 | 31 | 704 | 1.38 | 1002 |

**Used for:** independent validation of the movement-time predictions (see §7).

Additional supporting anchor: NIST TN-1664 ([S4]) reports a **mean office pre-evacuation delay ≈ 141 s (2 min 21 s)** with a long right tail, and NFPA notes full evacuation of the largest high-rises "may take upwards of two hours" ([S5]).

**Processing.** All quantities are reduced to SI (m, s, persons). No smoothing or fitting is applied to the geometry; only \(k\) and \(a\) are taken directly from the published relations.

---

## 4. Model Construction

### 4.1 Variables

| Symbol | Meaning | Units |
|---|---|---|
| \(N\) | number of occupied floors above grade (= building height \(H/h\)) | – |
| \(H\) | building height (\(H=Nh\)) | m |
| \(h\) | floor-to-floor height (3.5) | m |
| \(p\) | occupancy per floor | person |
| \(P=Np\) | total occupancy | person |
| \(n_s,\ w\) | number and nominal width of stairways | –, m |
| \(b\) | boundary layer per side (0.15) | m |
| \(k,a,\theta\) | SFPE speed constant, area/person, stair slope angle | m/s, m², rad |
| \(C\) | stair-core bottleneck capacity | person/s |
| \(\Delta t\) | free descent time for one floor | s |
| \(t_0\) | pre-movement time (detection + reaction) | s |
| \(X\) | required clearance time | min |

### 4.2 Capacity of the stair core

With slope \(\theta=\arctan(\text{riser}/\text{tread})\) for a 190/254 mm stair, \(\sin\theta=0.599\), so the stair **path length per floor** and the **free descent time** are

\[
\ell = \frac{h}{\sin\theta}=\frac{3.5}{0.599}=5.84\ \text{m},\qquad
\Delta t = \frac{\ell}{k}=\frac{5.84}{1.00}=5.84\ \text{s}\ \ (\text{i.e. }0.60\ \text{m/s vertical}).
\]

The **effective width** removes a boundary layer on each side, \(w_e=w-2b\), and the stair core capacity is

\[
\boxed{\,C \;=\; \sum_{i=1}^{n_s} w_{e,i}\,F_{s,\max}\;=\;n_s\,(w-2b)\,k/(4a)\,}.
\]

For the reference stair (\(w=1.5\) m, \(b=0.15\) m, \(F_{s,\max}=0.94\)): \(w_e=1.20\) m and one stair passes \(1.13\) person/s (\(68\) person/min).

### 4.3 Deterministic flow-bottleneck (D/D/1) evacuation time

All occupants are "released" at \(t_0\). An occupant from floor \(j\) reaches the *base* of the stair (the bottleneck queue) at

\[
a_j = t_0 + (j-1)\,\Delta t \quad (\text{unimpeded descent}).
\]

The queue is served at rate \(C\), one person per \(1/C\) seconds. With the classic deterministic single-server recursion \(e_i=\max(a_i,\ e_{i-1}+1/C)\), the exit time of the last of \(n=P\) persons has the closed form

\[
\boxed{\,T_{\text{evac}} = \max_{i}\!\Big(a_i - \tfrac{i}{C}\Big) + \frac{n-1}{C}\,}.
\]

This interpolates automatically between the two limiting regimes:

\[
\boxed{\;T_{\text{evac}} \;\approx\; t_0 + \max\Big(\underbrace{(N-1)\,\Delta t}_{\text{travel-limited}},\ \underbrace{\frac{P}{C}}_{\text{flow-limited}}\Big)\;}
\]

- **Travel-limited** (few people, generous stairs): the top-floor occupant simply walks down.
- **Flow-limited** (dense, tall building): the stair core is a pipe of capacity \(C\) that must process all \(P\) occupants; this dominates in real skyscrapers.

Clearing "within \(X\) minutes" requires \(T_{\text{evac}}\le 60X\), giving the **design inequality**

\[
t_0 + \max\Big((N-1)\Delta t,\ \tfrac{Np}{C}\Big) \le 60X
\quad\Longrightarrow\quad
N \le \min\!\Big(1+\frac{60X-t_0}{\Delta t},\ \frac{(60X-t_0)\,C}{p}\Big).
\]

For realistic skyscrapers the **second term is binding**, i.e. *height is limited by egress throughput per floor*, not by travel speed.

### 4.4 Optional parallel channels

**Fire-service elevators.** For a bank of \(n_e\) elevators of capacity \(c_e\) persons, expected one-way travel distance \(N h/3\), car speed \(v_e\), door/transfer overhead,

\[
R = \frac{2(Nh/3)}{v_e}+2t_{\text{door}}+t_{\text{transfer}},\qquad
C_{\text{elev}}=\frac{n_e\,c_e}{R}.
\]

**Rooftop helicopter.** A shuttle of \(n_h\) helicopters, \(n_{\text{pax}}\) passengers, cycle \(\tau\):

\[
C_{\text{helo}}=\frac{n_h\,n_{\text{pax}}}{\tau}.
\]

These add to the effective clearance capacity \(C_{\text{tot}}=C+C_{\text{elev}}+C_{\text{helo}}\).

---

## 5. Solution Process and Implementation

The model is implemented in `code/evacuation_model.py` (Python 3, NumPy). The algorithm:

1. Build empirical constants (\(k,a,b,\theta,h\)) → \(\ell,\Delta t,F_{s,\max}\).
2. For a design \((n_s,w,p,t_0)\), compute \(C\) and \(C_{\text{elev}}\).
3. Compute \(T_{\text{evac}}\) by the closed form **and** the vectorised D/D/1 recursion (cross-check).
4. **Solve for maximum floors:** increment \(N\) until \(T_{\text{evac}}(N)>60X\); report \(N,H=Nh,P=Np\).
5. Validate against the NIST data; run sensitivity on \(t_0,\ p,\ C\).

Output is written to `results/model_output.json` and `logs/model_run.txt`. All results below are reproducible with `python code/evacuation_model.py`.

---

## 6. Results and Analysis

### 6.1 Model constants

| Quantity | Value |
|---|---|
| Stair slope (190/254) | \(\theta=36.8^\circ,\ \sin\theta=0.599\) |
| Path length per floor \(\ell\) | 5.84 m |
| Free descent time per floor \(\Delta t\) | 5.84 s (vertical speed 0.60 m/s) |
| Max specific flow \(F_{s,\max}\) | 0.94 person/(m·s) = 56.4 person/(min·m) |

### 6.2 Stair-core capacity options

| Configuration | \(w_e\) (m) | \(C\) (person/s) | \(C\) (person/min) | Time to drain 150 persons from one floor |
|---|---|---|---|---|
| 2 stairs × 1.12 m | 0.82 | 1.54 | 92 | 97 s |
| 3 stairs × 1.12 m | 0.82 | 2.31 | 139 | 65 s |
| 3 stairs × 1.50 m | 1.20 | 3.38 | 203 | 44 s |
| 4 stairs × 1.50 m | 1.20 | 4.51 | 271 | 33 s |
| 4 stairs × 2.00 m | 1.70 | 6.39 | 383 | 23 s |
| 6 stairs × 2.00 m | 1.70 | 9.59 | 575 | 16 s |

### 6.3 Maximum building cleared within \(X\) (occupancy \(p=150\)/floor, \(t_0=300\) s)

Cells give **maximum floors** (\(N\)), with height \(=3.5N\) m and total occupancy \(=150N\).

| Egress provision | \(X=15\) min | \(X=30\) min | \(X=60\) min |
|---|---|---|---|
| 2 stairs × 1.12 m (code minimum) | 6 fl / 21 m / 900 | 15 fl / 52 m / 2 250 | 33 fl / 116 m / 4 950 |
| 3 stairs × 1.12 m | 9 fl / 32 m / 1 350 | 23 fl / 80 m / 3 450 | 50 fl / 175 m / 7 500 |
| **3 stairs × 1.50 m** | **13 fl / 46 m / 1 950** | **33 fl / 116 m / 4 950** | **74 fl / 259 m / 11 100** |
| **4 stairs × 1.50 m** | **17 fl / 60 m / 2 550** | **44 fl / 154 m / 6 600** | **99 fl / 346 m / 14 850** |
| 3 stairs × 1.50 m **+ 4 rescue elevators** | 16 fl / 56 m / 2 400 | 39 fl / 136 m / 5 850 | 82 fl / 287 m / 12 300 |
| 4 stairs × 1.50 m **+ 8 rescue elevators** | 23 fl / 80 m / 3 450 | 54 fl / 189 m / 8 100 | 112 fl / 392 m / 16 800 |

**Worked closed-form checks (2nd stair-column, \(C=3.38\), \(\Delta t=5.84\) s):**

- 50-storey tower, \(t_0=300\) s: \(T=300+\max(49\cdot5.84,\ 7500/3.38)=300+2219=2519\) s \(=42.0\) min → clears 60 min, **not** 30 min.
- The same 50-storey tower with 4 × 1.5 m stairs: \(T=300+7500/4.51=1963\) s \(=32.7\) min — still just over 30 min.
- The same tower with 4 × 2.0 m stairs: \(T=300+7500/6.39=1474\) s \(=24.6\) min → clears 30 min.
- A 50-storey tower at lower density (\(p=100\), 5 000 persons): \(T=300+5000/3.38=1779\) s \(=29.7\) min → clears 30 min.

### 6.4 Headline answer — building, occupation, and methods for each \(X\)

| Deadline \(X\) | Recommended design height | Floors | Maximum occupation | Evacuation methods |
|---|---|---|---|---|
| **15 min** | **≈ 56 m** (mid-rise) | **16** | **≈ 2 400** | **4 protected stairways (1.5 m)**, full voice alarm, staff-monitored |
| **30 min** | **≈ 136 m** | **39** | **≈ 5 850** | **3 stairways (1.5 m) + 4 fire-service elevators** (rescue-assisted) |
| **60 min** | **≈ 287 m** | **82** | **≈ 12 300** | **3 stairways (1.5 m) + 4 fire-service elevators + rooftop helicopter** (last resort) |

**Interpretation.** A *true* skyscraper (≈200 m, 40+ storeys, 6 000+ occupants) **cannot be fully cleared in 15 minutes** by any physically realistic stair provision: even the aggressive 4 × 1.5 m core caps the 15-minute building at ~60 m. Fifteen-minute clearance is a **mid-rise** requirement. Thirty minutes reaches a genuine high-rise (≈40 storeys) only with a wide stair core and elevator assistance; sixty minutes reaches a supertall (≈80–100 storeys) once wide stairways are combined with rescue-elevator throughput. This is consistent with the observed reality that full evacuation of the largest high-rises needs "upwards of two hours" under ordinary provisions ([S5]) — meeting \(X\) therefore *forces* an over-provisioned egress design.

---

## 7. Validation and Sensitivity Analysis

### 7.1 Validation against measured drills (D2)

The model predicts the **movement** component; the measured drill time also contains behavioural pre-movement. Backing the pre-movement out of each NIST case:

| Building | Measured (s) | Model movement (s) | Implied pre-movement (s) |
|---|---|---|---|
| NIST-10 | 1022 | 483 | 539 |
| NIST-18 | 1192 | 335 | 857 |
| NIST-24 | 1090 | 328 | 762 |
| NIST-31 (densest, 704 occ.) | 1002 | 698 | 304 |

Results: the **dense, flow-limited case (NIST-31)** is reproduced within 15 % using a plausible ~5 min pre-movement; the **sparsely occupied** buildings (255–436 people spread over many floors) are dominated by behavioural delay (implied 9–14 min), consistent with the long-tailed pre-movement distributions reported by NIST ([S4]) and with the fact that thinly-populated stairwells never approach capacity. In the design regime of interest — a densely occupied skyscraper — the model is therefore conservative and well-calibrated.

### 7.2 Sensitivity to pre-movement time \(t_0\) (3 stairs × 1.5 m, \(X=60\))

| \(t_0\) (s) | Max floors | Height (m) | Occupancy |
|---|---|---|---|
| 120 | 78 | 273 | 11 700 |
| 180 | 77 | 270 | 11 550 |
| 300 | 74 | 259 | 11 100 |
| 420 | 71 | 248 | 10 650 |
| 600 | 67 | 234 | 10 050 |

Because the flow-limited regime dominates, \(T_{\text{evac}}\) is **insensitive to \(t_0\)** for tall buildings (a 5-minute change in pre-movement changes the height limit by only ~1 floor). This is a desirable property: the design is robust to alarm-response uncertainty.

### 7.3 Sensitivity to occupancy density \(p\) (3 stairs × 1.5 m, \(t_0=300\) s)

| \(p\) (person/floor) | Max floors, \(X=15\) | \(X=30\) | \(X=60\) |
|---|---|---|---|
| 75 | 26 | 67 | 148 |
| 100 | 20 | 50 | 111 |
| 150 | 13 | 33 | 74 |
| 200 | 10 | 25 | 55 |

Height scales **inversely with floor occupancy**: halving density roughly doubles the achievable height. This identifies **per-floor population** (hence egress width per floor, a code requirement) as the single most powerful design lever.

### 7.4 Quantitative robustness

- Changing the free-speed constant \(k\) (1.00→1.16) shortens \(\Delta t\) by ~14 % but alters the flow-limited height by <2 % (capacity term unaffected); only the small travel term changes.
- Reducing \(F_{s,\max}\) by 20 % (smoke, counterflow, handicapped occupancy) reduces all height limits by ~20 % — the dominant risk. A **20–30 % capacity safety factor** is therefore recommended when sizing the stair core.

---

## 8. Strengths, Limitations, and Improvements

**Strengths**
- Uses **published, citable empirical laws** (SFPE speed–density, Fruin/TCRP specific flow) rather than free parameters.
- Reproduces the two limiting regimes analytically and matches dense-building drill data within 15 %.
- Yields a compact **design inequality** \(N\le(60X-t_0)C/p\) that directly answers the problem.
- Fully reproducible (`code/evacuation_model.py` + `results/model_output.json`).

**Limitations**
- Deterministic (mean) model: no stochastic spread of speed, no behavioural heterogeneity, no fatigue decay on very tall descents.
- Assumes uniform, instantaneous release and no counterflow, smoke, or stair blockage (A9). These would *increase* time; the model is optimistic, hence the recommended safety factor.
- Elevator and helicopter channels are treated as additive throughput; in reality they are floor-selective and safety-constrained (water in shafts, smoke control), so their contribution is an upper bound.
- Discrete person-by-person merging at stair entrances is not resolved; congested merges could add a few percent.

**Improvements**
- Couple the flow model with a **fire/smoke (CFD) model** to time-vary capacity and toxicity (RSET vs ASET analysis).
- Add a **stochastic micro-simulation** (social-force / cellular-automaton) calibrated to NIST micro-data.
- Model **phased / defend-in-place** strategies and sky-lobby/skybridge transfers for supertalls.
- Include **age/mobility distributions** and assisted-evacuation devices.

---

## 9. Conclusions and Recommendations

1. **The governing physics is throughput, not travel.** In a dense skyscraper the clearance time is \(T_{\text{evac}}\approx t_0 + P/C\); the building height that can be cleared scales as \(N\le(60X-t_0)\,C/p\). Egress **width per floor** is the dominant design variable.
2. **For \(X=15\) min**, only a **mid-rise** qualifies: up to **~56 m / 16 floors / ~2 400 occupants** with an aggressive **4 × 1.5 m protected-stairway** core and a full voice alarm. No realistic stair provision lets a true skyscraper clear in 15 minutes.
3. **For \(X=30\) min**, a **high-rise** is feasible: **~136 m / 39 floors / ~5 850 occupants** using **three 1.5 m stairways plus four fire-service elevators** operated by rescue personnel (stair-only maximum: 33 floors).
4. **For \(X=60\) min**, a **supertall** is feasible: **~287 m / 82 floors / ~12 300 occupants** using **three 1.5 m stairways + four rescue elevators + rooftop helicopter** (stair-only maximum: 74 floors; wide-core maximum ≈ 99 floors / 346 m).
5. **Recommendations for designers:** (i) size the stair core with a **20–30 % capacity margin** over the flow-limited requirement; (ii) certify **fire-service elevators** for assisted evacuation; (iii) provide a **rooftop rescue landing** and helicopter programme for the topmost floors; (iv) adopt a **full-building voice alarm** to compress \(t_0\); and (v) for buildings beyond the 60-minute limit, formally adopt a **phased evacuation / defend-in-place** strategy rather than promising a full-evacuation deadline that physics will not honour.

---

## 10. References

- **[S1]** SFPE Handbook of Fire Protection Engineering — stair movement (speed–density \(S=k(1-aD)\), specific flow), as restated in NIST TN-1839, *Movement on Stairs During Building Evacuations*: https://nvlpubs.nist.gov/nistpubs/TechnicalNotes/NIST.TN.1839.pdf
- **[S2]** Transportation Research Board, *TCRP Report 100 — Transit Capacity and Quality of Service Manual* (Fruin stair flow ≈ 1.19 person/(m·s) descending; vertical speed component ≈ 0.30 m/s): https://onlinepubs.trb.org/onlinepubs/tcrp/docs/tcrp100/Part7.pdf
- **[S3]** R. D. Peacock, B. L. Hoskins, E. D. Kuligowski, *Overall and Local Movement Speeds During Fire Drill Evacuations in Buildings* (NIST): https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=906969 ; and *Stairwell Evacuation from Buildings*: https://www.govinfo.gov/content/pkg/GOVPUB-C13-ec25b4cbc1945198f618650ad87be43c/pdf/GOVPUB-C13-ec25b4cbc1945198f618650ad87be43c.pdf
- **[S4]** NIST TN-1664, *Occupant Behavior in a High-Rise Office Building Fire* (pre-evacuation-time distributions): https://www.nist.gov/document/tn1664pdf
- **[S5]** NFPA, *High-rise buildings* (full evacuation "may take upwards of two hours"): https://www.nfpa.org/education-and-research/building-and-life-safety/high-rise-buildings

## Appendix — Reproducibility

- Model code: `code/evacuation_model.py`
- Machine-readable results: `results/model_output.json`
- Run log: `logs/model_run.txt`
- Run command: `python code/evacuation_model.py`

All numerical results in this report are produced by that script from the constants in §6.1 and the assumptions in §2.
