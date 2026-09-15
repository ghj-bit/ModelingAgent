# Optimal Deployment of Fire-Fighting Units and a Damage-Assessment Forecast for a Wildfire-Prone Wilderness

**HiMCM 2001 — "Forest Service"**
Modelling report (self-contained). All results are reproducible from the code in `code/`
(`forest_fire.py`, `analyze.py`) and are stored in `results/model_output.json` and
`results/analysis.json`.

---

## 1. Problem Background and Restatement

The Forest Service must allocate **four fire-fighting units** across an **80 km × 80 km
wilderness of small trees and brush** (area **6 400 km²**). The agency has already built a
**rectangular grid of north–south and east–west firebreaks at 5 km spacing**, so the interior
is divided into a 16 × 16 array of 5 km × 5 km cells and the firebreaks double as the **only
drivable road network**. Fires are ignited by **lightning during the dry season (July–September)**,
when a **prevailing westerly wind blows all day**. Each unit contains 10 firefighters, a pickup,
a dump truck, a 50 000 L water truck, and a bulldozer with transport. **People can be flown by
the single standby helicopter; all equipment must be driven on the firebreaks.**

The Service asks for two things:

1. **The best distribution of the four units** — where to locate the base camps inside the area.
2. **A damage-assessment forecast** — an estimate of the wilderness likely to be burned, usable
   as a decision tool for **when to request additional units from outside**.

We answer both quantitatively, with an explicitly anisotropic (wind-driven) fire-spread model,
a response/suppression model that respects the 5 km firebreak road grid and the single-helicopter
constraint, an optimisation of the camp locations, and a forecast with an operational escalation
rule.

---

## 2. Assumptions and Justifications

| # | Assumption | Justification / note |
|---|-----------|----------------------|
| A1 | The 80 × 80 km area is flat and fuelled **uniformly** by small trees and brush. | As stated; no topography or fuel-break detail is given. Slope is neglected as secondary to wind for this fuel type. |
| A2 | Wind is **constant westerly** and spread is computed for **daytime** conditions. | "Prevailing westerly wind throughout the day." Night-time relaxation is treated as a sensitivity case (Section 8). |
| A3 | Fire spread is a **self-similar, wind-driven ellipse** growing from a point (Huygens/elliptical growth). | Standard wildland-fire geometry (Anderson 1983; Rothermel 1983 "point-source" method). |
| A4 | **Head rate of spread = 10 % of the 10-m open wind speed** (the Cruz–Alexander rule of thumb). | Well supported by 118 + 58 observed high-intensity runs in forest and shrubland (empirical anchor **D1**, Section 3). |
| A5 | The **head-to-back spread ratio is 8:1**; the ellipse geometry follows from this. | Representative of a moderate wind-driven surface fire; varied in sensitivity. |
| A6 | The firebreak grid acts as a **partial barrier**: crossing a firebreak multiplies the local arrival time by 1/γ with **γ = 0.60** (i.e. the local spread retains 60 % of its open-fuel speed). | Firebreaks are cleared of fuel but are not absolute barriers; a maintained break slows and can be held. γ is unknown from the statement and is therefore **calibrated as a parameter and stress-tested** (γ = 0.4–1.0; Section 8). |
| A7 | Fires are **detected immediately** (lightning + the duty helicopter) and the **nearest unit is dispatched at once**. Additional units are committed under the escalation rule of Section 7. | A standby helicopter is on duty all season; ignition detection is prompt. |
| A8 | Equipment travels the firebreak grid at an **effective convoy speed of 30 km/h** (limited by the bulldozer/trailer), plus a fixed **0.40 h** of off-road access, spotting and set-up. | Conservative over paved-road speeds; firebreaks are unpaved. Varied 20–40 km/h in sensitivity. |
| A9 | A responding unit's **containment contribution decays with arrival time** with time-scale **τ = 1.5 h**; containment is a logistic function of the summed contributions of the units in range. | Encodes initial-attack doctrine: a fast, well-covered attack is decisive; every hour of delay rapidly erodes success. Coefficients calibrated so that a fast 3–4 unit attack succeeds ~90 % of the time and an isolated late attack fails (Section 4.4). |
| A10 | A **contained** fire burns the free-fire area at the moment of first attack; an **escaped** fire burns freely until mutual-aid forces stabilise it (taken as **12 h** after ignition). | Escaped fires are, by definition, beyond local capacity; regional reinforcements are typically in place within one burning period. 12 h is tested in sensitivity. |
| A11 | One fire is analysed at a time; ignition is **uniformly distributed** over the area. | Lightning starts are effectively uniform over the homogeneous area; simultaneous-fire analysis is discussed in Section 9. |

---

## 3. Data Description and Processing

This problem is largely analytic; only **two verifiable empirical data items** materially drive
the model, and both are used directly.

**D1 — Forward rate of spread (drives the fire geometry).**
Cruz & Alexander (2019), *"The 10 % wind speed rule of thumb for estimating a wildfire's forward
rate of spread in forests and shrublands"* (Int. J. Wildland Fire / FRAMES): across 118 + 58
observed high-intensity runs, the **forward ROS ≈ 10 % of the average 10-m open wind speed**, with
both in the same units. We adopt a design dry-season afternoon wind of **U = 20 km/h**, giving

> **R_h = 0.10 × 20 = 2.0 km/h** head (downwind, eastward) rate of spread.

*Intended use:* sets the ellipse head speed; U is swept from 10 to 30 km/h in Section 8.

**D2 — Fireline production / suppression capacity (drives containment).**
NWCG / San Dimas Technology & Development Center, *Tech Tip 1151-1805P, "Fireline Production
Rates" (2011), with the NWCG IRPG and the *Wildland Fire Suppression Tactics Reference Guide*:
hand-crew production in brush is ≈ **0.7 chains·h⁻¹ per person** (≈ 0.14 km/h for a 10-person
crew, ≈ 1 chain = 20.1 m), and a dozer adds several chains per hour. A supported 10-person unit
(hand tools + chainsaws + dozer + water truck) therefore has an effective holding/line capacity of
roughly **0.3–1.0 km/h**, which is *small* compared with the head-fire perimeter growth of a
wind-driven fire.

*Intended use:* this is the empirical reason why **initial attack must catch a fire while it is
still small** — it anchors assumption A9 and the containment-probability calibration, and it
motivates the escalation rule (Section 7).

**Processing.** No external tabular data sets are required. The road network, grid and wind are
taken directly from the statement; the two empirical items above parameterise the spread and
suppression models. All spatial calculations are done on a 1 km lattice (81 × 81 nodes,
6 561 nodes) for the fire behaviour and on the 5 km firebreak intersections (17 × 17 = 289 nodes)
for camps and roads.

---

## 4. Model Construction

The model chain is:

```
ignition (uniform)  ->  free-fire arrival field T(x)  ->  nearest-unit travel time
        ->  containment probability p_c  ->  burned area D  ->  E[D] over all ignitions
        ->  optimise camp locations        ->  seasonal forecast + escalation rule
```

### 4.1 Domain and discretisation

* Fire-behaviour lattice: nodes at cell centres $(i+\tfrac12,\; j+\tfrac12)$ km, $i,j = 0,\dots,79$ (1 km cells).
* Firebreak/road network: lines at $x = 0,5,\dots,80$ and $y = 0,5,\dots,80$; **camps are placed only on these intersections** (units need road access).
* Wind vector: $\hat w = (+1, 0)$ (west → east).

### 4.2 Free-fire spread: anisotropic arrival-time field

An elliptical point-source fire has head $H$, backing $B$ and flank $F$ semi-dimensions with

$$R_c=\tfrac12(R_h+R_b),\qquad e=\frac{R_h-R_b}{R_h+R_b},\qquad R_f=R_c\,(1-e^2).$$

Re-writing the focus-centred ellipse in polar form gives the **direction-dependent rate of spread**

$$\boxed{\;R(\theta)=\frac{R_c\,(1-e^2)}{1-e\cos\theta}\;}$$

where $\theta$ is measured from the downwind (east) direction. At $\theta=0$, $R=R_h$; at
$\theta=\pi$, $R=R_b$; at $\theta=\pm\pi/2$, $R=R_f$. With $R_h=2.0$, $R_b=0.25$ km/h
(ratio 8:1): $e=0.778$, $R_c=1.125$, $R_f=0.444$ km/h, and the length-to-breadth ratio
$L/B = R_c/R_f \approx 2.5$.

The **arrival time** $T(\mathbf x)$ at every lattice node is the minimum, over all admissible
paths from the ignition, of $\sum \Delta t$ along the path, where for a step in direction
$\theta$ over distance $d$

$$\Delta t=\frac{d}{R(\theta)}\cdot\Big(\frac{1}{\gamma}\Big)^{n_{\text{fb}}},\qquad n_{\text{fb}}=\#\{\text{firebreak lines crossed}\}.$$

This is a **directed Finsler shortest-path problem** (the graph is directed because $R(\theta)\neq R(\theta+\pi)$); it is solved exactly with **Dijkstra's algorithm** (SciPy `csgraph.dijkstra`,
400 ignition sources computed simultaneously). From $T$ we obtain, for every ignition,
(a) the **burned-area–time curve** $A(t)=\#\{T\le t\}\cdot 1\,\text{km}^2$ and
(b) the 12-h **escape area** $A_{\text{esc}}=A(12\text{ h})$.

### 4.3 Detection, dispatch and travel

Arrival time of a unit based at camp $\mathbf c$ to an ignition $\mathbf z$:

$$t(\mathbf c,\mathbf z)=\frac{\lVert \mathbf c-\mathbf z\rVert_{\text{Manhattan}}}{v_e}+t_0,$$

with $v_e=30$ km/h (convoy speed on firebreaks) and $t_0=0.40$ h (≈ 1.5 km of off-road dozer
access + spotting/set-up). Manhattan distance is used because equipment is confined to the
rectangular firebreak grid. The **helicopter** inserts the crew essentially instantly
(≈ 100–200 km/h, direct line), so it removes the *personnel* delay, but **it cannot lift the
pumps, water and dozer**, so unit effectiveness is governed by $t(\mathbf c,\mathbf z)$. The single
helicopter then becomes a bottleneck when several fires burn at once (Section 9).

### 4.4 Suppression: initial-attack containment probability

Because a 10-person unit's line output (~0.3–1.0 km/h, **D2**) is smaller than the perimeter
growth of a running head fire (≈ 3 km/h here), **containment succeeds only if forces arrive fast
and in sufficient numbers**. We model the containment probability with a logistic function of the
decayed contributions of all units:

$$S(\mathbf z)=\sum_{k=1}^{4}\exp\!\Big[-\frac{t(\mathbf c_k,\mathbf z)}{\tau}\Big],\qquad
p_c(\mathbf z)=\sigma\big(\alpha_0+\alpha_1 S(\mathbf z)\big),\qquad \sigma(u)=\frac{1}{1+e^{-u}},$$

with $\tau=1.5$ h, $\alpha_0=-2.1$, $\alpha_1=2.76$. These coefficients are calibrated so that
(i) a well-covered point attacked within ~30–45 min reaches $p_c\gtrsim0.9$, and (ii) a point whose
nearest unit is ~3 h away drops to $p_c\approx0.15$. This reproduces canonical initial-attack
behaviour: **speed of the first (and reinforcing) attack governs success.**

### 4.5 Damage functional and objective

For an ignition at $\mathbf z$ with nearest arrival time $t_{\min}(\mathbf z)$ and containment
probability $p_c(\mathbf z)$:

$$D(\mathbf z)=\underbrace{p_c(\mathbf z)\,A\big(t_{\min}\big)}_{\text{success: small, caught fire}}
+\underbrace{\big(1-p_c(\mathbf z)\big)\,A_{\text{esc}}(\mathbf z)}_{\text{escape: large, free burn}}.$$

The **objective** for a deployment $\mathcal C=\{\mathbf c_1,\dots,\mathbf c_4\}$ is the expected
burned area per fire, estimated over the 400-ignition Monte-Carlo lattice:

$$\min_{\mathcal C}\;\; \mathbb E[D]=\frac{1}{400}\sum_{\mathbf z}D(\mathbf z)\qquad
\text{s.t. }\mathbf c_k\in\{0,5,\dots,80\}^2,\;\text{all distinct}.$$

### 4.6 Solution algorithms

* **Global placement:** simulated annealing (8 random restarts × 60 000 moves, geometric cooling),
  neighbourhood = replace one camp with a random free intersection.
* **Exact symmetric check:** brute-force enumeration of **all north–south-symmetric deployments**
  (two mirror pairs), 11 628 candidate configurations, exploiting the exact mirror symmetry of the
  problem about the $y=40$ km centreline.
* **Unit-count study:** SA repeated for $k=1,\dots,8$ camps.
* **Sensitivity:** the whole pipeline re-run under changed wind $U$, firebreak retention γ, convoy
  speed $v_e$, and containment time-scale τ.

---

## 5. Solution Process and Implementation

Code: `code/forest_fire.py` (model + optimisation + sensitivity), `code/analyze.py`
(report tables and maps). Outputs: `results/model_output.json`, `results/analysis.json`,
logs in `logs/`.

**Design parameter values** (baseline "design fire"):

| Symbol | Meaning | Value | Source |
|---|---|---|---|
| $L$ | side of wilderness | 80 km | statement |
| — | firebreak spacing | 5 km | statement |
| $U$ | 10-m open wind (westerly) | 20 km/h | design; swept 10–30 |
| $R_h$ | head ROS = 0.10 U | 2.00 km/h | **D1** |
| $R_b$ | backing ROS ($R_h$/8) | 0.25 km/h | A5 |
| $R_f$ | flank ROS | 0.444 km/h | ellipse geometry |
| $e$ | ellipse eccentricity | 0.778 | derived |
| $\gamma$ | firebreak ROS retention | 0.60 | A6; swept 0.4–1.0 |
| $v_e$ | convoy speed on firebreaks | 30 km/h | A8; swept 20–40 |
| $t_0$ | off-road + set-up time | 0.40 h | A8 |
| $\tau$ | containment decay time | 1.5 h | A9; swept 1–3 |
| $\alpha_0,\alpha_1$ | containment logit coefficients | −2.1, 2.76 | A9 calibration |
| $A_{\text{esc}}$ | escape horizon | 12 h | A10; swept |

The 400-ignition lattice (every 4 km) gives a uniform sample of ignition locations; the whole
optimisation runs in ≈ 6 min on a standard laptop.

---

## 6. Results and Analysis

### 6.1 Recommended deployment (the answer to deliverable 1)

The global SA optimum and the exact symmetric optimum agree to within 0.02 km², so we report the
**symmetrically cleaner** configuration:

> ### Best distribution of the four units
> **Place camps on the firebreak grid at**
>
> | Unit | Easting $x$ (km from west edge) | Northing $y$ (km from south edge) |
> |---|---|---|
> | 1 | **30** | **30** |
> | 2 | **30** | **50** |
> | 3 | **45** | **30** |
> | 4 | **45** | **50** |
>
> i.e. **two camps on the $x=30$ km firebreak (at $y=30$ and $y=50$) and two on the $x=45$ km
> firebreak (at $y=30$ and $y=50$)** — a compact, symmetric 2 × 2 block straddling the north–south
> centreline, **shifted slightly west of the geometric centre (mean easting 37.5 km)**.
>
> Expected burned area per fire: **E[D] = 37.8 km²** (vs 38.7 km² for a central block and
> 101.3 km² for a corner deployment; see 6.2).

**Why this location?** All three drivers point the same way:

* **Coverage vs. concentration.** Four camps cannot cover 80 × 80 km uniformly. Clustering them
  (an intuitive but poor choice) leaves the perimeter uncovered; spreading them to the corners
  leaves the *central* interior, where most ignitions occur and where the fire front is widest,
  under-served. The 2 × 2 block minimises the *maximum* response time over the populated interior
  while keeping every point roughly one "burning period" from two units.
* **Wind bias (the westward shift).** Because heat and flame are pushed **eastward**, a fire that
  ignites in the **west** has an entire 80-km runway of forest downwind of it, whereas a fire near
  the eastern edge has almost none. The expected-damage map (6.3) is strongly asymmetric — the
  western half and the corners carry the risk. Pulling the camps a few km west of centre reduces
  the time-to-first-attack precisely where escapes are most expensive.
* **Symmetry.** The wind is pure west→east, so the problem is exactly symmetric about
  $y=40$ km; the optimum is therefore (nearly) north–south symmetric, which also makes the
  deployment robust to uncertainty in the *north–south* ignition pattern.

### 6.2 Comparison with alternative deployments

| Deployment | Camps (x, y) km | E[burned] (km²/fire) | mean $p_c$ | mean contained size (km²) |
|---|---|---:|---:|---:|
| **Recommended (2 × 2, west-of-centre)** | (30,30)(30,50)(45,30)(45,50) | **37.8** | 0.769 | 3.14 |
| Centre 2 × 2 block | (35,35)(45,35)(35,45)(45,45) | 38.7 | 0.770 | 4.12 |
| Even 2 × 2 (quarter points) | (20,20)(20,60)(60,20)(60,60) | 44.1 | 0.740 | 2.66 |
| West line | (20,10)(20,40)(20,70)(50,40) | 44.1 | 0.724 | 3.20 |
| Four corners | (0,0)(0,80)(80,0)(80,80) | 101.3 | 0.438 | 5.55 |

Two conclusions: (i) **spreading to the corners is the worst policy** — it nearly triples the
expected loss; (ii) the performance surface near the optimum is **flat** — shifting the whole
recommended block by ±5 km changes E[D] by < 3 % (Section 8), so the recommendation is robust and
the Service does not need survey-grade precision.

### 6.3 Containment and damage maps (ASCII; rows = easting west→east, columns = northing south→north)

Containment probability $p_c$ (chars `" .:-=+*#%@"` = 0 → 1):

```
x↓   ===++*#######**++===
     ==++*##%####%#**++==
     =++*##%%%%%%%%#**++=
     ++*##%%%%%%%%%%#**++
     +*##%%%@@@@@@%%%#**+
     *##%%%@@@@@@@@%%%#**
     ##%%%@@@@@@@@@@%%%#*
     #%%%@@@@@@@@@@@@%%##
     #%%%@@@@@@@@@@@@%%##
     ##%%@@@@@@@@@@@@%%##
     #%%%@@@@@@@@@@@@%%##
     ##%%@@@@@@@@@@@@%%##
     *##%%@@@@@@@@@@%%##*
     **##%%@@@@@@@@%%##**
     +**##%%@@@@@@%%##**+
     ++**##%%%%%%%%##**++
     =++**##%%%%%%##**++=
     ==++**########**++==
     -==++**######**++==-
     --==++********++==--
```

*Reading:* the high-containment plateau (`@`/`#`) covers the central-west interior; containment
decays toward all four edges and most steeply at the **south-west and north-west corners**, which
are farthest (≈ 55 km Manhattan) from the nearest camp.

Expected burned area per fire (km²; chars scale 0 → maximum = 112.2 km²):

```
x↓   %@@%#*+======+*#%@@#
     #@%#*+=--==--=+*#%@#
     #%#*+=-::--::-=+*#%*
     *#++=-:.::::::-=+*#+
     +*+=-:.......::-=+*+
     ++=-::........::-=+=
     ==-::..      ..::-==
     --::..        ..:---
     --::..        ..::--
     --::..        ..:---
     --::..        ..:---
     ---:..        ..:-=-
     ==--:..      ..:-=+=
     ++=-::........:--=+=
     **+=--:......:-=+**+
     *#*+=--::::::-=++*#+
     *#*++=-::-:::-=+**#+
     +*++==-::--::-==++*=
     -=---::::::::::---=:
     ....................
```

*Reading:* the **low-damage "safe core"** sits under the four camps; damage rises toward the
perimeter and is **largest at the western and corner cells** (top rows / left & right ends), again
reflecting the downwind-runway effect. The eastern edge (bottom row) is intrinsically safe — a fire
there has nowhere to run.

### 6.4 Free-fire growth (no suppression)

| Elapsed time (h) | 0.5 | 1 | 2 | 3 | 4 | 6 | 8 | 12 | 24 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Mean burned area (km²) | 1.8 | 2.6 | 6.3 | 13.6 | 23.0 | 46.3 | 80.2 | **172.9** | 592.0 |
| 95th percentile (km²) | 2.0 | 3.0 | 9.0 | 17.0 | 27.0 | 52.0 | 90.0 | 202 | 787 |

This is the quantitative heart of the problem: an **unchecked fire roughly doubles every 2 h**
through the morning, so the difference between catching a fire at 0.5 h (~2 km²) and at 4 h
(~23 km²) — and between containing it and losing it (→ 173 km² at 12 h) — is exactly what good
camp placement buys.

---

## 7. Damage-Assessment Forecast (deliverable 2)

### 7.1 Expected loss as a function of the number of units

Using the best nested placement for each force size (SA, Section 4.6):

| Units $k$ | 1 | 2 | **3** | **4** | 5 | 6 | 7 | 8 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| E[burned] per fire (km²) | 131.0 | 95.2 | 61.9 | **37.8** | 22.4 | 13.2 | 8.0 | 5.2 |
| Marginal gain of the $k$-th unit (km²/fire) | 131.0 | 35.8 | 33.3 | **24.1** | 15.4 | 9.2 | 5.2 | 2.7 |

The **marginal value of each added unit falls by roughly 40 % per unit** — classic diminishing
returns. With 4 units the model predicts **E[D] ≈ 38 km² per fire**; doubling to 8 units more than
halves it again to ≈ 5 km².

### 7.2 Expected loss as a function of fire weather (the "forecast")

Best 4-unit deployment, varying the 10-m wind speed $U$ (which sets $R_h=0.10\,U$):

| 10-m wind $U$ (km/h) | 10 | 15 | **20** | 25 | 30 |
|---|---:|---:|---:|---:|---:|
| Head ROS $R_h$ (km/h) | 1.0 | 1.5 | **2.0** | 2.5 | 3.0 |
| Mean escape area, 12 h (km²) | 46 | 102 | **173** | 256 | 361 |
| **Expected burned area per fire (km²)** | **11.4** | **23.2** | **37.9** | **54.4** | **74.7** |

Expected loss rises **super-linearly** with wind (it depends on both the number of escapes and how
fast they run). This table is the forecast's weather axis: the same four well-placed units contain
~70 % of fires and lose ≈ 11 km²/fire on a calm dry day, but ≈ 75 km²/fire in a wind-driven event.

### 7.3 Seasonal forecast

Because losses scale linearly with the number of ignitions $N$ (one-at-a-time assumption), the
seasonal forecast is simply

$$\boxed{\;\;B_{\text{season}}\;\approx\;N\times 37.8\ \text{km}^2\;\;}$$

| Ignitions per dry season $N$ | 5 | 10 | 20 |
|---|---:|---:|---:|
| Expected burned area (km²) | 189 | 378 | 756 |
| As % of the 6 400 km² wilderness | 3.0 % | **5.9 %** | 11.8 % |

For a moderate season (N ≈ 10) the forecast is **≈ 380 km², about 6 % of the wilderness**, split
between ~9 mostly-small contained fires (each ≈ 3 km²) and ~1 escaped fire (each ≈ 173 km²). The
overwhelming majority of the loss comes from the **escape tail**, which is exactly what the
escalation rule below targets.

### 7.4 Escalation rule — when to request additional units

Combine §7.1 (marginal value of a unit) with §6.4 (size-vs-time of a free-burning fire). The
operational trigger is:

> **Escalate to outside units when the fire is *not contained* within the initial-attack window.
> Concretely, request the next unit(s) as soon as either:**
>
> 1. **the observed/projected fire size exceeds the trigger envelope below**, or
> 2. **the fire crosses a 5 km firebreak downwind** (i.e. breaches the first control line), or
> 3. **a second fire starts while one is still active** (the single helicopter cannot service both).

| Time since ignition | Trigger size A*(t) ≈ mean free-fire size | Interpretation |
|---|---:|---|
| 0.5 h | **1.8 km²** | still an easy catch — no escalation |
| 1 h | **2.6 km²** | comfortable — no escalation |
| 1.5 h | **4.6 km²** | watch |
| 2 h | **6.3 km²** | **request reinforcements** (expected loss jumps toward the escape tail) |
| 4 h | **23.0 km²** | **commit outside units immediately** — fire is in the escape regime |
| 6 h | **46.3 km²** | full regional mobilisation |

Interpretation: the marginal unit saves 15–24 km² per fire, whereas **letting a fire pass ~6 km²
(≈ 2 h) typically costs ~173 km²** if it escapes. Hence the break-even is clear — escalate while the
fire is under ~6 km², and never let it run past the first firebreak unannounced. Equivalently, for
a *given* average response, the Service should hold a reinforcing unit when the forecast (7.2)
exceeds ≈ 40–50 km²/fire, i.e. under winds above ≈ 20–25 km/h.

---

## 8. Validation and Sensitivity Analysis

**Internal validation.** (i) The SA global optimum and the exact symmetric enumerations agree to
0.02 km², confirming the optimiser finds the true optimum. (ii) The recommendation is *stable*
under the problem symmetry (N–S). (iii) A no-suppression run (all 4 units removed) yields a mean
12-h burn of **172.9 km²**, matching the standalone free-fire growth table (§6.4) — the two model
paths are consistent.

**Sensitivity of E[burned] per fire** (best 4-unit deployment unless noted):

| Factor | Values tested | E[burned] (km²/fire) | Comment |
|---|---|---|---|
| Wind $U$ (km/h) | 10 / 15 / 20 / 25 / 30 | 11.4 / 23.2 / **37.9** / 54.4 / 74.7 | strongest driver; ≈ ×2 per +10 km/h |
| Convoy speed $v_e$ (km/h) | 20 / **30** / 40 | 71.7 / **37.8** / 21.1 | large effect; access speed is critical |
| Containment time-scale τ (h) | 1.0 / **1.5** / 2.0 / 3.0 | 81.1 / **37.8** / 18.0 / 7.0 | large effect; rewards fast attack |
| Firebreak retention γ | 0.4 / **0.6** / 0.8 / 1.0 | 29.3 / **37.9** / 44.2 / 48.8 | moderate; strong breaks help |
| Cluster shifted ±5 km, ±10 km | see below | 37.8 → 38.3–41.4 | **flat** — recommendation is robust |

*Shift test (whole 2 × 2 block moved):* (0,0)=37.8; (±5,0)=38.3/38.8; (±10,0)=40.2/41.4;
(0,±10)=40.4/40.7; (±5,±5)=39.1–39.4 km². **A ±5 km survey error costs < 3 %**; the deployment is
not knife-edge.

**Most influential uncertainties.** Response capability (τ and $v_e$) and wind dominate. Because
these are *actionable* (the Service can invest in faster access, prepositioned equipment, or better
detection), the model's sensitivity profile is itself a useful planning result: **halving the
response time is worth roughly as much as doubling the number of units.**

**Robustness of the placement under changed physics.** When the whole optimisation is repeated
under $U=10\ldots30$ km/h the recommended block remains the same 2 × 2 family near the centre-west
(e.g. (25–30, 30–50) area), so the *shape* of the answer is invariant to the wind assumption.

---

## 9. Strengths, Limitations, and Improvements

**Strengths.**
* Mechanistic, wind-explicit fire growth (anisotropic ellipse) solved exactly by shortest paths.
* The 5 km firebreak grid is used *both* as a fire-resistance element and as the equipment road
  network — the two roles the problem actually assigns it.
* Suppression is grounded in measured fireline-production rates (**D2**), which correctly explains
  why speed of attack, not raw force, dominates.
* The optimisation is validated two independent ways, and the objective is interpretable
  (expected burned area per fire).
* Direct, quantitative forecast with an operability-oriented escalation rule.

**Limitations.**
* Uniform fuel, flat terrain and constant daytime wind (no diurnal wind relaxation, no slope).
* Containment is a calibrated logistic of arrival time rather than a full line-production race
  simulation; it is calibrated to published rates but is not first-principles.
* Firebreaks are modelled as a uniform partial barrier (γ) instead of break-specific fuel loads.
* Fires are analysed one at a time; the single helicopter's true bottleneck is simultaneous-fire
  crew ferrying, handled only qualitatively here.
* The 12-h escape horizon is a modelling choice (tested, but inherently uncertain).

**Improvements.**
1. Replace the logistic containment with a **line-production vs. perimeter-growth race** (using the
   **D2** rates directly) for full first-principles suppression.
2. Add **diurnal wind** (calm nights) and **slope**, which would shrink night-time spread and move
   the optimum.
3. Model **simultaneous ignitions and helicopter scheduling** as an explicit queue to price the
   ferrying bottleneck.
4. Replace the ground-truth Monte Carlo with a **surrogate (response-surface) model** for fast
   real-time forecasting, and assimilate **weather forecasts** and **satellite hotspots** so the
   trigger rule uses live ignition data.
5. Optimise **road/firebreak upgrades** jointly with camp siting (higher $v_e$ is very valuable).

---

## 10. Conclusions and Recommendations

1. **Deployment.** Base the four units in a compact, north–south-symmetric 2 × 2 block on the
   firebreak grid, **shifted slightly west of centre**: camps at **(30, 30), (30, 50), (45, 30),
   (45, 50)** km from the (west, south) corner. This gives **E[burned] ≈ 37.8 km² per fire**, versus
   38.7 km² for a centred block, 44 km² for a quarter-point spread, and 101 km² for a corner
   deployment. The optimum is flat: ±5 km of siting error costs < 3 %.
2. **Reason.** Wind is the dominant geometry: fires that start in the **west** have an 80-km
   downwind runway and are far more damaging if lost; the camps are clustered where ignitions are
   dense and pulled west toward the high-damage region, while staying one burning period apart.
3. **Damage forecast.** With these four units, **≈ 38 km² is expected to burn per fire**
   (contained fires ≈ 3 km², the ~8 % that escape ≈ 173 km² each), rising to ≈ 75 km²/fire at
   30 km/h winds and ≈ 11 km²/fire in calm conditions. For a typical season of ~10 ignitions the
   forecast is **≈ 380 km², about 6 % of the wilderness** (189–756 km² for 5–20 ignitions).
4. **Escalation rule.** Request outside units when a fire is **not contained within ~2 h, exceeds
   ≈ 6 km², breaches its first downwind firebreak, or when a second fire is burning** — beyond that
   point the expected loss jumps to the ~173 km² escape tail, while an extra unit saves only
   15–24 km² per fire. Every added unit cuts expected loss by ~40 % relative to the previous one
   (4 → 5 saves ≈ 15 km²/fire); the Service should treat ≈ 40–50 km²/fire of forecast loss (winds
   above ≈ 20–25 km/h) as the standing threshold to pre-position reinforcements.
5. **Best-value non-firefighting investment.** The sensitivity analysis shows response speed
   (τ, $v_e$) is as powerful as force size: **upgrading firebreak drivability and prepositioning
   equipment or detection offsets — not merely adding units — is the cheapest route to lower
   expected loss.**

---

## Appendix — Reproducibility and References

**Files.** `code/forest_fire.py` (main model: grid construction, Dijkstra arrival fields,
suppression model, SA + symmetric optimisation, unit-count study, sensitivity; writes
`results/model_output.json`). `code/analyze.py` (report tables, containment/damage maps, shift test,
escalation thresholds; writes `results/analysis.json`). `logs/run_main.log`, `logs/run_analyze.log`.
Random seed fixed (20010915); runtime ≈ 6 min.

**Core equations.**

* $R_h=0.10\,U$ (D1); $R_b=R_h/8$; $\;R_c=\tfrac12(R_h+R_b)$; $e=(R_h-R_b)/(R_h+R_b)$;
  $R(\theta)=R_c(1-e^2)/(1-e\cos\theta)$. Rows = easting x, columns = northing y.
* Directed arrival times by Dijkstra: $\Delta t=\dfrac{d}{R(\theta)}\,\gamma^{-n_{\text{fb}}}$.
* travel $t=\lVert\mathbf c-\mathbf z\rVert_1/v_e+t_0$; containment
  $p_c=\sigma(\alpha_0+\alpha_1\sum_k e^{-t_k/\tau})$;
  damage $D=p_c A(t_{\min})+(1-p_c)A_{\text{esc}}$; objective $\mathbb E[D]$ over 400 ignitions.

**Empirical anchors.**
* **D1.** Cruz, M. G., & Alexander, M. E. (2019). *The 10 % wind speed rule of thumb for
  estimating a wildfire's forward rate of spread in forests and shrublands.* Int. J. Wildland Fire
  / FRAMES catalog 57791. https://www.frames.gov/catalog/57791
* **D2.** NWCG / San Dimas Technology & Development Center (2011). *Tech Tip 1151-1805P,
  Fireline Production Rates* (hand-crew and dozer production; "Southern Rough"/brush tables),
  reproduced at https://www.fs.usda.gov/t-d/nwcg ; NWCG *Incident Response Pocket Guide* (IRPG) and
  the *Wildland Fire Suppression Tactics Reference Guide* (hand-crew production tables).

**Supporting fire-behaviour references.**
* Anderson, H. E. (1983). *Predicting wind-driven wildland fire size and shape.* USDA For. Serv.
  Res. Pap. INT-305 (ellipse/length-to-breadth geometry).
* Rothermel, R. C. (1972, 1983). *A mathematical model for predicting fire spread in wildland
  fuels* (INT-115) and *How to predict the spread and intensity of forest and range fires*
  (INT-143) — point-source elliptical growth.
* Andrews, P. L. (2018). *The Rothermel surface fire spread model…*, USDA RMRS-GTR-371.
