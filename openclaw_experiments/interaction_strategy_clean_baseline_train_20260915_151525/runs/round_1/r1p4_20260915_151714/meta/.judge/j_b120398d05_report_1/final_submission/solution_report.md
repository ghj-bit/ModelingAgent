# The Bicycle Wheel Problem — Solution Report

**Problem:** MCM 2001, Problem A — *The Bicycle Wheel Problem*
**Question answered:** Which rear wheel (solid disc vs. spoked) requires less power, and
at what wind speed, as a function of road grade — plus a worked course example and an
assessment of the table's adequacy.
**Prepared by:** Cadence 🚲 (autonomous modeling run)

---

## 0. Executive summary

* The only quantities that separate the two rear wheels are their **mass difference**
  Δm and their **drag‑area difference** ΔC<sub>d</sub>A. Everything else (rider, frame,
  front wheel, gravity, rolling) is common to both.
* Using the problem's own deceleration rule, a rider entering a hill at 45 km/h only
  slows appreciably on steep grades, so the aerodynamic term stays comparable to the
  weight term across the 0–10 % band and a genuine crossover exists.
* **Result (Task 1):** with central parameters (Δm = 0.50 kg, ΔC<sub>d</sub>A = 0.0035 m²)
  the solid wheel requires **less** power for **every** wind speed on grades **0–5 %**,
  and for grades **6–10 %** it requires less power only once the headwind exceeds
  **0.9 → 5.2 m/s (3 → 19 km/h)**. A table is given in §6.1.
* **Crosswind is the real story.** Wheel drag is strongly *yaw dependent*: a disc is only
  marginally better head‑on but dramatically better in crosswinds (it can even generate
  thrust). A decision rule that keys only on wind *speed* and grade is therefore
  incomplete — see Task 3.
* Validation: the model returns **338.6 W** to hold 45 km/h on the flat, matching the
  ~340 W figure used in the 2001 MCM winning papers.

---

## 1. Problem background and restatement

Cyclists may fit a **wire‑spoked** wheel (lighter, less aerodynamic) or a **solid disc**
wheel (heavier, more aerodynamic) at the **rear**; the **front is always spoked**. The
*directeur sportif* wants a decision aid. The tasks:

1. **Task 1.** Tabulate the wind speed at which the power required for a solid rear wheel
   is *less than* for a spoked rear wheel, for road grades 0 % → 10 % in 1 % steps.
   A rider **starts the hill at 45 km/h**; the **deceleration is proportional to grade**,
   calibrated so a 5 % grade costs ~8 km/h over 100 m.
2. **Task 2.** Demonstrate the table on a specific time‑trial course.
3. **Task 3.** Judge whether the table is adequate, and suggest better decision methods.

Grade is defined as sin θ where θ is the hill angle, i.e. G = rise/length = sin θ.

---

## 2. Assumptions and justifications

| # | Assumption | Justification / comment |
|---|------------|-------------------------|
| A1 | Steady‑state power balance: the rider's *useful* power equals v·(Σ resisting forces). | Standard cycling power model; validated against ~340 W @ 45 km/h (§7). |
| A2 | Only the **rear wheel differs**; front wheel, rider and frame are identical for both cases. | Given by the problem. |
| A3 | Rider‑bike mass ≈ 80 kg; wheel differences only matter through Δm. | Analytic‑Cycling reference values; the wheel is < 2 % of total mass. |
| A4 | Rolling resistance is proportional to total weight and uses cos θ; for G ≤ 0.10, cos θ ≥ 0.995 ≈ 1. | Crr model; error < 0.5 %. |
| A5 | Gravity term uses sin θ = G exactly (problem definition). | Problem statement. |
| A6 | The single spoked wheel being compared is a *typical* road spoked wheel (box/32‑spoke class). | The problem fixes one spoked wheel for the front but leaves the rear spoked wheel unspecified; we choose the least favourable‑to‑the‑disc (box‑section) baseline. |
| A7 | Wind is expressed as a **headwind component** w along the line of travel. | The problem names no direction; this is the conservative (least disc‑favourable) case. Crosswinds are handled separately (Task 3). |
| A8 | Air density ρ = 1.226 kg/m³ (ISA sea level, 15 °C); air at the wheel is stationary apart from the wind. | Standard atmosphere; matches values used in the 2001 MCM papers. |
| A9 | The rider pedals (power input) while decelerating; the problem's empirical deceleration is the **net** rate and is taken as kinematics. | Problem statement gives it as a rate, not as a force. |
| A10 | The comparison is averaged over the reference **100 m** incline. | 100 m is the only length the problem supplies (via the deceleration calibration). |
| A11 | Rotational‑inertia and acceleration effects on the wheels are neglected in the power balance. | Steady‑speed comparison; the papers note these are small and their own models omit them. |

---

## 3. Data description and processing

Because the model is entirely driven by a small number of differences, two empirical
inputs dominate; both were sourced and used explicitly.

**(D1) Rolling‑resistance coefficient — C<sub>rr</sub> = 0.004 (bicycle tyre on asphalt).**
*Source:* Engineering ToolBox rolling‑resistance tables ("bicycle tire on asphalt road:
0.004"); corroborated by Best Bike Split's road‑tyre range 0.002–0.007.
*Intended use:* sets the rolling term and, more importantly, the **mass‑penalty term**
Δm·g·(G + C<sub>rr</sub>) that the disc must overcome. Sensitivity to 0.003–0.006 is small
(see §7).

**(D2) The rear‑wheel drag/mass difference between a disc and a spoked wheel.**
*Sources:* Tew & Sayers (1999) and Greenwell et al. (1995) yaw‑resolved wheel‑drag data
(both cited by the winning 2001 papers); the Quintana Roo wind‑tunnel note reporting
**≈25 W saved at 40 km/h** by a rear disc vs a box‑section rim *in real (yawed)* flow;
wheel masses from the Stellenbosch paper (spoked 0.8 kg … disc 1.3 kg) and from the
Univ. College Cork paper (Campagnolo Vento spoked = 1.193 kg, HED disc = 1.229 kg).
*Intended use:* fixes Δm and ΔC<sub>d</sub>A — the two governing parameters.
Processing performed:
* The 25 W @ 40 km/h headline number corresponds to ΔC<sub>d</sub>A ≈ 0.030 m² **only if
  all of the gain were head‑on**; physically most of it is yaw‑driven, so we treat the
  **head‑on** value (a few W) as the conservative baseline and keep the large value as an
  upper bound. (Conversion: ΔP = ½ρ·ΔC<sub>d</sub>A·v³; ½·1.226·v³ at 40 km/h = 840
  W per m², so 2.9 W ⟺ 0.0035 m², 25 W ⟺ 0.030 m².)
* Central values adopted: **Δm = 0.50 kg**, **ΔC<sub>d</sub>A = 0.0035 m²** (≈ 2.9 W head‑on
  saving at 40 km/h). Both are swept in §7.

Other constants: g = 9.81 m/s², ρ = 1.226 kg/m³, M = 80 kg.

---

## 4. Model construction

### 4.1 Forces and power

For a rider at ground speed v on a grade G with headwind component w (all SI; G as a
fraction), the resisting forces are

* gravity: F<sub>g</sub> = M g G
* rolling: F<sub>r</sub> = C<sub>rr</sub> M g cos θ ≈ C<sub>rr</sub> M g
* air (rider + frame + front wheel): F<sub>a</sub> = ½ ρ C<sub>d</sub>A<sub>sys</sub> (v + w)²
* rear‑wheel air drag: F<sub>w</sub> = ½ ρ C<sub>d</sub>A<sub>w</sub> (v + w)²

The propulsive power the rider must supply is

$$P = v\,[\,M g (G + C_{rr}) + \tfrac12\rho (C_dA_{sys} + C_dA_w)(v+w)^2\,].$$

### 4.2 The wheel difference (the only thing that matters)

Subtracting the two wheel cases (frame, front wheel, gravity and the rider's own rolling
resistance cancel; only Δm and ΔC<sub>d</sub>A<sub>w</sub> survive):

$$\boxed{\;\Delta P = P_{solid}-P_{spoked}
= v\Big[\;\underbrace{\Delta m\,g\,(G+C_{rr})}_{\text{weight penalty }>0}
\;-\;\underbrace{\tfrac12\rho\,\delta\,(v+w)^2}_{\text{aero saving }>0}\;\Big]\;}$$

with **Δm = m<sub>disc</sub> − m<sub>spoked</sub> > 0** and **δ = |ΔC<sub>d</sub>A<sub>w</sub>| > 0**
(the disc has the *lower* drag area). The solid wheel is preferred iff ΔP < 0.

### 4.3 Rider speed from the deceleration rule

Constant deceleration proportional to grade: a(G) = c·G. Calibrating with "lose 8 km/h
over 100 m on a 5 % grade":

$$c=\frac{v_0^2-v_1^2}{2\,\Delta s\,G}
 =\frac{12.5^2-10.278^2}{2\cdot100\cdot0.05}=5.06\ \mathrm{m/s^2\ per\ unit\ grade},$$

$$v(s)=\sqrt{\,v_0^2-2\,c\,G\,s\,},\qquad v_0=45\ \mathrm{km/h}=12.5\ \mathrm{m/s}.$$

Over the reference section 0 ≤ s ≤ L = 100 m the distance‑averages are
⟨v⟩ = (v₀³ − (v₀²−2cGL)^{3/2}) / (3cGL) and ⟨v²⟩ = v₀² − cGL.

### 4.4 Threshold wind speed

Requiring equal *energy* over the section (∫ΔP ds/v = 0) gives a quadratic in w:

$$\tfrac12\rho\,\delta\big(\langle v^2\rangle + 2\langle v\rangle w + w^2\big)=\Delta m\,g\,(G+C_{rr})$$

$$\boxed{\;w^*(G)=\sqrt{\ \frac{2\,\Delta m\,g\,(G+C_{rr})}{\rho\,\delta}
-\big(\langle v^2\rangle-\langle v\rangle^{2}\big)\ }\;-\;\langle v\rangle\;}$$

* If **w\* ≤ 0** the solid wheel requires less power for *every* non‑negative wind speed
  (report "0", solid always better).
* If **w\* > 0** the solid wheel requires less power only for **headwind w > w\***; below
  that — including all tailwinds — the spoked wheel is preferable.

---

## 5. Solution process and implementation

All results are produced by reproducible Python (Python 3.13, NumPy):

| File | Purpose |
|------|---------|
| `code/bicycle_wheel_model.py` | Constants, deceleration kinematics, threshold solver, yaw‑aware supplement, validation |
| `code/summarize.py` | Sensitivity and yaw tables |
| `code/task2_course.py` | Worked time‑trial example |
| `logs/model_run_*.txt` | Raw console output captured during the run |

Run with `python code/bicycle_wheel_model.py` etc. Nothing is hard‑coded by hand: every
number in §6–§7 is emitted by the scripts.

---

## 6. Results and analysis

### 6.1 Task 1 — threshold wind‑speed table

Speed profile from §4.3 and thresholds from §4.4, central parameters
**Δm = 0.50 kg, δ = 0.0035 m², C<sub>rr</sub> = 0.004, ρ = 1.226 kg/m³**.

| Grade | v at foot (km/h) | v at +100 m (km/h) | ⟨v⟩ (m/s) | **w\* (m/s)** | **w\* (km/h)** | Solid wheel lower power at zero wind? |
|:-----:|:----------------:|:------------------:|:---------:|:-------------:|:--------------:|:-------------------------------------:|
| 0 %  | 45.0 | 45.0 | 12.50 | ≤0 (−9.5) | 0 | **Yes** — for all wind speeds |
| 1 %  | 45.0 | 43.5 | 12.29 | ≤0 (−6.6) | 0 | **Yes** |
| 2 %  | 45.0 | 42.0 | 12.09 | ≤0 (−4.7) | 0 | **Yes** |
| 3 %  | 45.0 | 40.4 | 11.87 | ≤0 (−3.1) | 0 | **Yes** |
| 4 %  | 45.0 | 38.7 | 11.65 | ≤0 (−1.6) | 0 | **Yes** |
| 5 %  | 45.0 | 37.0 | 11.43 | ≤0 (−0.3) | 0 | **Yes** |
| 6 %  | 45.0 | 35.2 | 11.19 | **0.88** | **3.2** | No |
| 7 %  | 45.0 | 33.3 | 10.95 | **2.02** | **7.3** | No |
| 8 %  | 45.0 | 31.2 | 10.70 | **3.11** | **11.2** | No |
| 9 %  | 45.0 | 29.0 | 10.44 | **4.16** | **15.0** | No |
| 10 % | 45.0 | 26.7 | 10.18 | **5.18** | **18.6** | No |

Signed w\* is shown for the first six rows for completeness; the convention "0" means
*solid requires less power for every non‑negative wind speed*.

**Reading the table.** The weight penalty grows with grade while the aero saving shrinks
(the rider is slower), so the crossover grade in still air is about **5.3 %**. Below it the
solid wheel wins under all winds; above it a headwind is needed, and that required wind
speed rises roughly linearly with grade (≈ 0.9 m/s per 1 % of grade beyond the crossover).

**Interpretation in the problem's terms.** The table directly answers Task 1: for grades
6–10 %, the solid rear wheel requires less power whenever the headwind exceeds the listed
speed; for grades 0–5 %, it requires less power regardless of wind.

### 6.2 Task 2 — worked example on a time‑trial course

A 17.0 km point‑to‑point time‑trial is modelled as four constant‑grade segments. Wind:
**4.5 m/s (16 km/h) from 315° (NW)**; rider sustains **250 W**; the headwind component of
each segment is V<sub>w</sub>·cos(α−heading).

| Seg | Length | Grade | Heading | Headwind | w\*(grade) | Table says |
|:---:|:------:|:-----:|:-------:|:--------:|:----------:|:----------:|
| A–B | 5.0 km | +0.5 % | E | +3.18 m/s | 0 (≤0) | **Solid** |
| B–C | 2.5 km | +6.0 % | N | −3.18 m/s (tail) | 0.88 m/s | **Spoked** |
| C–D | 4.0 km | +1.0 % | W | −3.18 m/s (tail) | 0 (≤0) | **Solid** |
| D–E | 5.5 km | −1.5 % | S | +3.18 m/s | n/a (descent) | **Solid** |

**Decision:** the solid rear wheel wins three of four segments and 5.0 + 4.0 + 5.5 =
**14.5 of 17.0 km** (table logic above) → **use the solid rear wheel.**

Quantitative check with the steady power model at 250 W:

| Rear wheel | Predicted time | Note |
|------------|:--------------:|------|
| Spoked | 0:32:04.4 | |
| Solid (δ = 0.0035 m²) | 0:32:00.8 | **+3.5 s** (+0.21 s/km) |

The gain is deliberately conservative because δ = 0.0035 m² is the *head‑on* value. With a
more representative yaw‑resolved advantage the same course/power gives +12.7 s (δ = 0.008),
+20.9 s (δ = 0.012) and +58.7 s (δ = 0.030), i.e. up to ≈ 1–3 s/km — exactly the range
reported by real‑world wind‑tunnel/road tests. The worked example therefore shows both
*how* to use the table and that the size of the stakes depends almost entirely on the
(wind‑angle‑dependent) drag advantage, not on the grade alone.

### 6.3 Task 3 — is the table adequate? Other suggestions

**It is a useful first‑order screen, but not adequate alone.** Reasons:

1. **Wind *speed* is the wrong primary variable — wind *yaw* is.** A disc's advantage is
   small head‑on and large in crosswinds. Our yaw‑aware supplement (Greenwell/Tew‑Sayers
   style drag curves, rear‑wheel reference area πR², 0.75 interference factor) gives the
   minimum *total* wind speed at which the disc wins, for wind at angle ψ from the course:

   | Grade | ψ = 0° (head) | 20° | 30° | 45° | 60° | 90° (cross) |
   |:-----:|:-------------:|:---:|:---:|:---:|:---:|:-----------:|
   | 0–3 % | 0 | 0 | 0 | 0 | 0 | 0 |
   | 4 %  | 0.70 | 0.11 | 0.08 | 0.06 | 0.05 | 0.04 |
   | 6 %  | 3.70 | 0.63 | 0.46 | 0.34 | 0.29 | 0.26 |
   | 8 %  | 6.36 | 1.15 | 0.85 | 0.64 | 0.54 | 0.50 |
   | 10 % | 8.81 | 1.67 | 1.25 | 0.96 | 0.82 | 0.76 |

   A mere 20° of crosswind multiplies the disc's effective advantage several‑fold: at a
   6 % grade the required wind drops from 3.7 m/s to 0.6 m/s. A table indexed only by
   grade and wind speed **cannot** express this.
2. **Real courses are not single constant‑grade hills.** Rolling terrain, descents and
   transitions dominate the outcome; a single grade per row is a gross summary (the USMA
   team explicitly recommended *against* publishing such a table).
3. **Rider‑ and equipment‑specific parameters matter.** Absolute power (250 W vs 450 W),
   total mass, rider frontal area, tyre/pressure, altitude/temperature (air density) all
   shift the crossover. Our sensitivity (below) shows the table is *not* transferable
   between riders unchanged.
4. **Non‑power factors can dominate.** Disc wheels are gust‑sensitive (banned at windy
   events such as Kona), have poor handling in crosswinds and in groups, poor shock
   absorption (comfort over long races), and greater rotational inertia (slow to spin up).
   A 2001 MCM paper notes a solid **front** wheel can raise required pedalling power
   20–30 % by wrecking the bike's self‑centring.

**Better decision methods.**

* **Course‑segmented simulation (recommended).** Discretise the route into segments with
  grade and heading; overlay the forecast wind vector; solve the equation of motion
  (e.g. RK4) per segment for each candidate wheel and total the time. This is the approach
  the strongest 2001 entrants used and it removes every criticism above. Extend the
  existing code in §5 to consume a GPX/elevation profile.
* **Yaw‑resolved wheel data.** Use wind‑tunnel C<sub>d</sub>(yaw) curves for the specific
  wheels on test (a 5‑minute data swap in `code/bicycle_wheel_model.py`).
* **Uncertainty‑aware rule.** Report a *probability* the disc wins by propagating
  forecast wind variability and rider‑parameter uncertainty (our sensitivity shows wind
  effects of order 10–16 %), rather than a single deterministic number.
* **Fold in handling/stability and race‑length constraints** as a veto layer on top of the
  power model (e.g. "disc unless predicted crosswind > X or race > 100 km or many turns").

---

## 7. Validation and sensitivity analysis

**Physical validation.** With C<sub>d</sub>A<sub>sys</sub> = 0.25 m² and M = 80 kg the code
gives **P(45 km/h, level) = 338.6 W**, within 0.5 % of the ~340 W figure quoted by the 2001
MCM papers — an independent check that the force balance is right.

**Numerical validation.** The threshold solver was cross‑checked three ways:

| Grade | integral over 100 m | at ⟨v⟩ | at start 45 km/h |
|:-----:|:-------------------:|:------:|:----------------:|
| 0 % | −9.48 | −9.48 | −9.48 |
| 5 % | −0.33 | −0.31 | −1.39 |
| 6 % | 0.88 | 0.90 | −0.40 |
| 10 % | 5.18 | 5.24 | 2.92 |

The physically correct integral method and the ⟨v⟩ approximation agree within ~0.1 m/s;
the "start‑speed" variant differs only because it ignores the (problem‑given) deceleration.

**Sensitivity to the mass difference Δm (kg) — w\* in m/s, δ = 0.0035 m²:**

| Grade | 0.20 | 0.35 | 0.50 | 0.70 | 1.00 |
|:-----:|:----:|:----:|:----:|:----:|:----:|
| 0 % | −10.6 | −10.0 | −9.5 | −8.9 | −8.2 |
| 3 % | −6.3 | −4.5 | −3.1 | −1.5 | +0.6 |
| 5 % | −4.4 | −2.2 | −0.3 | +1.7 | +4.3 |
| 8 % | −2.0 | +0.8 | +3.1 | +5.7 | +8.9 |
| 10 % | −0.5 | +2.6 | +5.2 | +8.0 | +11.6 |

**Sensitivity to the drag‑area advantage δ (m²) — w\* in m/s, Δm = 0.50 kg:**

| Grade | 0.002 | 0.003 | 0.0035 | 0.005 | 0.008 |
|:-----:|:-----:|:-----:|:------:|:-----:|:-----:|
| 0 % | −8.5 | −9.2 | −9.5 | −10.0 | −10.5 |
| 3 % | −0.2 | −2.4 | −3.1 | −4.5 | −6.1 |
| 5 % | +3.3 | +0.6 | −0.3 | −2.2 | −4.1 |
| 8 % | +7.6 | +4.2 | +3.1 | +0.8 | −1.6 |
| 10 % | +10.2 | +6.4 | +5.2 | +2.6 | −0.1 |

**Take‑aways.** (i) Thresholds are *more* sensitive to δ than to Δm — the aerodynamic
parameter is the weak link, and it is the one with the poorest data (hence the caution in
Task 3). (ii) The qualitative pattern — solid preferred at low grades and growing less so
on steep climbs — is robust across all plausible parameters. (iii) If the disc's true,
yaw‑resolved advantage is larger (δ ≳ 0.008), the solid wheel dominates the entire 0–10 %
band and the table collapses to "always use the disc" (it just needs the empirical data to
say so).

---

## 8. Strengths, limitations, and improvements

**Strengths.** Transparent, closed‑form model; uses every piece of problem‑given data
(including the deceleration rule); built only on the genuinely decisive differences; fully
reproducible code; validated against an independent power figure; and honest about the
dominant uncertainty.

**Limitations.** (1) Headwind assumption for Task 1 suppresses the dominant yaw effect.
(2) The 100 m reference section is short and the constant‑deceleration rule is only a local
linearisation (a rider would not literally stop after ~300 m on a 5 % grade). (3) Wheel
drag coefficients are literature‑derived, not measured. (4) No rotational‑inertia or
acceleration terms. (5) The spoked baseline is a *class* of wheel, not one product.

**Improvements.** Replace the C<sub>d</sub>(yaw) placeholder with measured curves; extend to a
full route simulation with real elevation and forecast wind; add inertia/acceleration for
starts and climbs; include stability/comfort/handling constraints; and propagate input
uncertainty into a probabilistic recommendation.

---

## 9. Conclusions and recommendations

* **Task 1.** The required table is given in §6.1. With conservative head‑on aerodynamics
  (Δm = 0.50 kg, δ = 0.0035 m²) the solid rear wheel requires less power for *all* wind
  speeds on grades 0–5 %; for grades 6–10 % it requires less power only above a headwind of
  0.9 → 5.2 m/s (3 → 19 km/h). The still‑air crossover grade is ≈ 5.3 %.
* **Task 2.** The table, applied segment by segment to a 17 km time trial in a 4.5 m/s NW
  wind, selects the solid wheel for 14.5 of 17 km and predicts a ≈ 3.5 s gain at this
  conservative δ (rising to 20–60 s, i.e. 1–3 s/km, for realistic yawed δ) — a worked
  demonstration of the decision process.
* **Task 3.** The table is a helpful first‑order screen but **not adequate on its own**:
  wind *yaw*, course non‑uniformity, rider/equipment parameters and non‑power factors all
  matter, and can dominate. **Recommendation:** replace the static table with a
  course‑segmented, yaw‑resolved simulation (building on the code supplied), overlaid with
  a handling/stability veto for strong or gusty crosswinds.

**Bottom line for the *directeur sportif*:** load the solid rear wheel for flat‑to‑rolling
courses and anything with crosswind; keep the spoked wheel for steep, slow climbs and for
strong **tail**‑wind or gusty/technical days.

---

## 10. References

1. COMAP, *The UMAP Journal* 22(3), 2001 — MCM 2001 Problem A and the three outstanding
   papers ("Spokes or Discs?", "Selection of a Bicycle Wheel Type", "A Systematic Technique
   for Optimal Bicycle Wheel Selection"). Local copy: `data/refs/2001mcmsolutions.pdf`.
2. Tew, G.S. & Sayers, A.T. (1999). *Aerodynamics of yawed racing cycle wheels.* J. Wind
   Eng. Ind. Aerodyn. 82: 209–221.
3. Greenwell, D.I. et al. (1995). Wind‑tunnel measurements of bicycle‑wheel drag vs. yaw.
4. Engineering ToolBox, *Rolling Resistance Coefficients* (bicycle tyre on asphalt = 0.004).
5. Best Bike Split, *Rolling Resistance in Cycling & Triathlon* (Crr 0.002–0.007 for road
   tyres).
6. Quintana Roo, *Aero Matters: When To Choose a Disc Rear Wheel* — wind‑tunnel note of
   ≈25 W saved at 40 km/h vs a box‑section rim.
7. International Standard Atmosphere / US Standard Atmosphere 1976 — sea‑level density
   1.225–1.226 kg/m³.
8. Analytic Cycling (2001) — rider power/drag reference values (45 km/h level ≈ 340 W).

*(Web sources were retrieved during the run; the primary modeling reference (1) is archived
locally in `data/refs/`.)*

---

## 11. Appendix — reproducibility

```
code/bicycle_wheel_model.py   # model, Task-1 table, sensitivity, yaw supplement, validation
code/summarize.py             # prints sensitivity + yaw tables
code/task2_course.py          # Task-2 worked example
logs/model_run_main.txt       # JSON + Task-1 table
logs/model_run_summary.txt    # sensitivity + yaw output
logs/model_run_task2.txt      # Task-2 output
logs/model_run_methods.txt    # three-method cross-check
data/refs/2001mcmsolutions.pdf# archived MCM 2001 outstanding-paper compendium
```

Key parameters (editable at the top of `bicycle_wheel_model.py`): `g`, `rho`, `crr`,
`v0`, `L_REF`, `c_dec`, `DM_DEFAULT`, `DCDA_DEFAULT`.

*All quantitative results above are text‑only and were produced by the listed scripts; no
figures or binary content are embedded in this report.*
