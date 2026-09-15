# Optimizing School Bus Routes: A Cost–Time Model for Rural and Urban Districts

**Problem:** HiMCM 2002 — *School Busing*  
**Deliverables:** a general mathematical model, a solution for representative rural and urban
districts, a pre-implementation test plan, and a short article for the school board.

---

## 1. Problem Background and Restatement

In districts where many students live in rural areas, nearly every child must be bused. A bus
*could* pick up elementary students, drop them at the elementary school, and then continue on to
collect high-school students for the high school (a **staggered / "two-tier"** run). The obvious
alternative is to run **separate buses** for each school, which duplicates travel over the same
roads but keeps each school's operation simple.

Everything is constrained: **no student may ride longer than one hour**, and the district faces
limits on **drivers, buses (equipment), money, and time**. The task is to design routes that
**minimize cost while balancing the time students spend on the bus**, in a form that generalizes
to other rural *and* urban districts; to explain how the model would be tested before being
deployed; and to communicate the result to a school board.

We answer by building a **capacitated vehicle-routing model with time windows (CVRPTW)** that
explicitly represents both the *separate* policy (S) and the *staggered* policy (C), and by
adding a vehicle-reuse coupling that captures the key economic question: *how many buses and
drivers does the staggered policy actually save, and what does it cost in ride time?*

## 2. Assumptions and Justifications

| # | Assumption | Justification |
|---|---|---|
| A1 | Two schools (elementary K–5, high 9–12), each with a fixed **bell time**; the elementary bell is earlier by a **stagger** Δ. | Matches the problem statement ("go to the elementary school and then continue … for the high school"). Δ is the central design lever and is swept in §7. |
| A2 | Buses start from a **depot** and run the **morning** collection; the afternoon mirror is symmetric. | Standard practice; fixed cost is charged per bus-day so both runs share one vehicle. |
| A3 | **Hard ride-time limit** T = 60 min for every student. | Given by the problem ("no student should be in the bus more than an hour"). |
| A4 | A bus has uniform capacity **Q = 72** seats (Type C bus; 54–90 available). | Industry-standard capacity (data item 1). |
| A5 | Distance = straight-line × **road factor 1.2**; travel speed is an **effective average** (45 km/h rural, 26 km/h urban) that already absorbs stops and acceleration. | Rural roads are not straight; effective speeds are the standard way to keep the model linear and data-light. |
| A6 | Boarding cost = fixed 0.5 min/stop + 0.25 min/student. | Students take time to board; larger stops take longer. |
| A7 | Cost = **fixed** $ per bus-day (driver + capital + insurance) + **variable** $ per km (fuel + maintenance). | Separates the two decisions a district controls: *how many buses* vs *how far they drive*. Calibrated from data items 1–2. |
| A8 | Ride-time **fairness** is representable by a penalty α per student-minute; α = 0 means pure cost minimisation. | Turns the soft "balancing" requirement into a tunable, solvable objective (Pareto analysis in §7.5). |
| A9 | Student counts are known per stop and split by school level; some stops serve both levels. | Standard for routing; the split drives whether the staggered policy is useful. |

## 3. Data Description and Processing

**Empirical anchors (verifiable).** Only three public figures materially affect the model; all
are recorded with sources in `data/references.md`:

1. **Capacity / price** — Type C buses seat 54–90 (72 typical); a new 72-passenger bus costs
   ≈ $130k–$160k (Gregory Poole; Rohrer Bus). → sets Q = 72 and the capital part of fixed cost.
2. **Operating economics** — ≈ 7 mpg and ≈ 12,000 mi/yr per bus (NYSBCA); states reimburse
   regular transportation at ≈ **$1.91 per bus-mile** (Nebraska, via Georgia Public Policy
   Foundation). → sets the fuel component of variable cost and provides an external per-mile
   benchmark.
3. **Sector structure** — ≈ 52–54% of students are bused, and **rural** transportation costs run
   ≈ **40% higher per student** than city/suburban (Ellegood et al., 2024). → justifies a
   rural-first design with an urban comparison.

**Synthetic district instances.** Because no single district's address-level data is public, we
generate reproducible instances that reproduce real rural settlement statistics: stops are
clustered into villages (rural) or a denser grid (urban), each stop holds a mix of elementary
and high-school students, and the schools sit near the demand centroid
(`code/sbrp.py::build_instance`, seeds fixed for reproducibility).

| Instance | Stops | Elementary | High | Area | Speed | Shared stops |
|---|---|---|---|---|---|---|
| **Rural** (base) | 30 | 350 | 246 | 20×20 km | 45 km/h | 65% |
| **Urban** (base) | 36 | 420 | 320 | 12×12 km | 26 km/h | 50% |

The rural instance (596 students) yields a fleet in the 7–10 bus range — consistent with a small
rural district. Processed data are saved to `data/district_rural.csv` and
`data/district_urban.csv`; route-level output to `results/routes_rural.csv`.

## 4. Model Construction

### 4.1 Sets, indices, parameters

| Symbol | Meaning |
|---|---|
| $V$ | set of bus stops |
| $q_i^{e}, q_i^{h}$ | elementary / high-school students at stop $i$ |
| $D, E, H$ | depot, elementary school, high school |
| $d_{ij}$ | road distance (km); $\tau_{ij}=60\,d_{ij}/v$ travel time (min) at speed $v$ |
| $u(i)$ | service (boarding) time at $i$ |
| $Q$ | bus capacity (72) |
| $T$ | max ride time (60 min) |
| $b_e, b_h$ | elementary / high-school bell times; $\Delta = b_h-b_e$ |
| $c^{f}, c^{v}$ | fixed cost per bus-day; variable cost per km |
| $\alpha$ | ride-time penalty per student-minute (equity weight) |

### 4.2 Feasible routes

A **route** is an ordered subset $r=(i_1,\dots,i_k)$ with a start node and an end node. For a
school $g\in\{E,H\}$ it is feasible iff

$$\sum_{i\in r} q_i^{g}\le Q \quad\text{(capacity)}, \qquad
\text{dur}(r)=\sum_{\text{legs}}\tau + \sum_{i\in r}u(i)\le T\;(=60)\quad\text{(ride time)},$$

using the fact that, because the school arrival is fixed at the bell, the *maximum* ride equals
the whole route duration. For a school-level $\ell$, start $a$, end $z$:

$$\text{dist}(r)=\sum_{p=1}^{k-1}d_{i_p i_{p+1}}+d_{a i_1}+d_{i_k z},\qquad
\text{smin}(r)=\sum_{p} q_{i_p}^{\ell}\,\bigl(b-\text{board}_{i_p}\bigr) .$$

### 4.3 Decision variables and objective

We use a **set-partitioning** formulation. Let $\mathcal R^{E}$ be candidate elementary routes,
and split high-school routes into **paired** candidates $\mathcal R^{H_s}$ (run *after* the
elementary drop, so they must finish within the stagger: $\text{dur}\le\Delta$) and
**standalone** candidates $\mathcal R^{H_\ell}$ (a dedicated bus, $\text{dur}\le T$). With binary
$x_r, y^{s}_r, y^{\ell}_r$ and an integer coupling $z$:

$$
\min\; c^{f}\bigl(\underbrace{\textstyle\sum_r x_r}_{n_E}
+\underbrace{\textstyle\sum_r y^{s}_r+\sum_r y^{\ell}_r}_{n_H}-z\bigr)
+c^{v}\,\textstyle\sum_r \text{dist}_r(\cdot)
+\alpha\,\textstyle\sum_r \text{smin}_r(\cdot)
$$

subject to

$$
\sum_{r\ni i} x_r = 1 \;\; \forall i:\,q_i^e>0,
\qquad
\sum_{r\ni i}\bigl(y^{s}_r+y^{\ell}_r\bigr)=1 \;\; \forall i:\,q_i^h>0,
\qquad
z\le \sum_r x_r,\quad z\le \sum_r y^{s}_r . \tag{$\star$}
$$

### 4.4 The vehicle-reuse coupling (the heart of the model)

A bus that drops elementary students at $b_e$ is free from $b_e$ onward, so **one physical
bus can perform one elementary route and one high-school route** provided the high-school route
fits entirely in the stagger window ($\text{dur}\le\Delta$). Let
$n_{H_s}=\sum_r y^{s}_r$ be the number of high-school routes that fit the window. Then

$$
\boxed{\;\#\text{buses}=n_E+n_H-\min\!\bigl(n_E,\,n_{H_s}\bigr)\;}
$$

which ($\star$) linearises exactly. Policy **S** is the special case $z\equiv 0$ using only
standalone high-school routes; policy **C** lets the model choose. This single coupling captures
the entire economic trade-off: combining needs *more, shorter* high-school routes
(smaller $Q$ loads, tighter time) but *reuses vehicles and drivers*.

## 5. Solution Process and Implementation

The problem is an NP-hard VRP; exact MILP over all routes is intractable at district scale, so we
use a **two-stage route-pool + exact set-partitioning MILP**, plus an independent exact solver for
validation.

1. **Route-pool generation** (`code/sbrp.py`): randomized **Clarke–Wright savings** (40 restarts)
   and **nearest-neighbour** construction (one solution per seed) build a rich pool of feasible
   routes for each of the three categories ($\mathcal R^E,\mathcal R^{H_s},\mathcal R^{H_\ell}$),
   each improved by intra-route **2-opt**. Singletons are always included so the model is
   feasible.
2. **Set-partitioning MILP** (`pulp` + CBC): solve (§4.3) over the pool, with the coupling
   ($\star$). This returns the optimal combination from the pool, i.e. the choice of routes,
   the number of buses, and the pairing.
3. **Exact validation solver** (`code/validate_small.py`): exhaustive enumeration of *all*
   feasible routes plus a bit-mask set-partitioning DP, giving the **provable optimum** on small
   instances.

Implementation: Python 3.13, NumPy 2.3, PuLP 3.3.2 (CBC). Each district solve takes ~1–2 s;
all results are reproducible from fixed seeds (`code/run_experiments.py`, logs in `logs/`).

## 6. Results and Analysis

### 6.1 Base rural district — the core result

| Metric | Policy S (separate) | Policy C (combined / staggered) |
|---|---|---|
| **Buses deployed** | **10** (6 elementary + 4 high) | **7** (6 elementary; 6 of 7 high routes reuse a bus) |
| High-school routes paired | 0 | 6 |
| Total distance (km, morning) | 251.2 | 282.8 |
| **Total cost ($/bus-day)** | **$1,351** | **$1,010** |
| Cost per student | $2.27 | $1.69 |
| Max elementary ride | 45.3 min | 51.6 min |
| Mean elementary ride | 25.3 min | 25.7 min |
| Max high-school ride | 49.6 min | 42.7 min |
| Mean high-school ride | 28.7 min | 22.8 min |
| Student-minutes on the bus | 15,906 | 14,605 |
| % of students riding > 45 min | 5.7% | 4.7% |

**Findings.**
- The staggered policy saves **3 buses (30% of the fleet) and $341 per day (25%)** at the cost of
  **+31.6 km** of travel. Because the fixed cost of a bus-day dominates the extra mileage, the
  trade is strongly favourable.
- Not only is C cheaper — it is *also better for high-school students*, whose maximum ride drops
  from 49.6 to 42.7 min because their routes must fit the (shorter) stagger window. Elementary
  students' maximum rises modestly (45.3 → 51.6 min) but stays within the 60-min limit.
- **Equity is improved overall**: total student-minutes fall 8%, and the share riding more than
  45 minutes falls from 5.7% to 4.7%.

### 6.2 Route structure (Policy C)

| School | Route (stops) | Students | km | Route min | Max ride |
|---|---|---|---|---|---|
| E | 18-17-19-16-15 | 59 | 27.9 | 54.4 | 39.9 |
| E | 21-24-6-8-5-7-9 | 68 | 29.6 | 59.9 | 51.6 |
| E | 10-12-14-13-11 | 67 | 21.8 | 48.3 | 38.7 |
| E | 28-29-27-25-26 | 63 | 24.5 | 50.9 | 39.0 |
| E | 0-3-4-1-2 | 59 | 15.8 | 38.3 | 33.4 |
| E | 20-22-23 | 34 | 17.8 | 33.7 | 29.9 |
| H | 21-24 *(paired)* | 23 | 21.4 | 35.3 | 23.3 |
| H | 27-29 *(paired)* | 16 | 24.4 | 37.6 | 25.5 |
| H | 13-12-2 *(paired)* | 31 | 18.2 | 33.6 | 25.5 |
| H | 26 *(paired)* | 20 | 14.5 | 24.8 | 17.2 |
| H | 23-9-22 *(paired)* | 42 | 19.6 | 38.1 | 32.2 |
| H | 10-4-3-0 *(paired)* | 58 | 16.5 | 38.5 | 28.3 |
| H | 18-17-19-15 *(standalone)* | 56 | 30.9 | 57.2 | 42.7 |

Six of the seven high-school routes fit the 40-minute stagger window and are paired with an
elementary bus; only one long high-school route (57 min, 56 students) needs a dedicated bus.

### 6.3 Urban district

| Metric | Policy S | Policy C |
|---|---|---|
| Buses | 13 | 9 |
| Distance (km) | 188.6 | 201.8 |
| Cost ($/day) | $1,673 | $1,201 |
| Max elementary ride | 49.5 min | 49.5 min |
| Max high-school ride | 43.4 min | 37.9 min |

The staggered policy is **equally effective in the city** (saves 4 buses, 28% cost) — but for a
different reason: shorter distances mean high-school routes fit the stagger window easily, at the
price of proportionally more deadhead mileage. **The model transfers across rural and urban
settings without modification**; only the instance parameters (speed, area, stop density) change.

### 6.4 Budget impact

At **180 school days**, the rural staggered policy saves ≈ **$61,000/yr** (≈ $85,000/yr urban)
and removes **3 buses** from the fleet — avoiding roughly **$390k–$480k** of capital if those
buses would otherwise be purchased (data item 1).

## 7. Validation and Sensitivity Analysis

### 7.1 Exact validation of the solver

We computed the **provable optimum** on small instances by exhaustive route enumeration.

| Check | Exact optimum | Our solver | Gap |
|---|---|---|---|
| Single-school CVRPTW (7 stops, Q=30, T=55) | $392.55 | $394.92 | **0.61%** |
| Two-school model, complete route pool (12 stops) | $421.20 | $421.20 | **0.00%** |

The heuristic pool reproduces the exact model optimum on the two-school instance and is within
0.6% for a harder single-school case, confirming the route-pool/MILP method is essentially
optimal at this scale. Reported fleet counts also sit just above simple analytic lower bounds
(10 vs. LB 9 for separate; 7 vs. LB 5 for combined — the LB ignores time windows).

### 7.2 Sensitivity to the stagger Δ (the decisive lever)

| Δ (min) | S buses | C buses | C paired | Saving % |
|---|---|---|---|---|
| 15 | 10 | 10 | 0 | 0.0 |
| 25 | 10 | 10 | 0 | 0.0 |
| 30 | 10 | 9 | 4 | 7.6 |
| 35 | 10 | 8 | 5 | 16.4 |
| **40** | 10 | **7** | 6 | **25.2** |
| 50 | 10 | 6 | 5 | 35.5 |
| 60 | 10 | 6 | 4 | 35.9 |

There is a **threshold at Δ ≈ 28–30 min**: below it no high-school route fits the window and the
staggered policy degenerates to the separate policy. Above it, savings grow rapidly and saturate
once every high-school route can be paired and the fleet equals the elementary fleet (6 buses).
**Implication:** staggering the bells by ≥ 40 minutes is the single most valuable scheduling
action a district can take.

### 7.3 Sensitivity to capacity, ride limit and speed

| Parameter | Effect (rural) |
|---|---|
| **Capacity Q** 36 → 84 | S buses 17 → 10; C buses 10 → 7. C always ≤ S; saving 25–36%. |
| **Ride limit T** 45 → 60 min | Tightening T to 45 min raises the fleet (S: 17, C: 9) but *increases* the relative value of combining (saving 42%), because reused buses become more precious. |
| **Speed** 30 → 55 km/h | Slower effective speed raises the fleet and shrinks the absolute saving; the ranking (C < S) never reverses. |

### 7.4 Sensitivity to cost parameters

| Variable cost ($/km) | S cost | C cost | Saving % |
|---|---|---|---|
| 0.30 | $1,275 | $925 | 27.5 |
| 0.60 (base) | $1,351 | $1,010 | 25.2 |
| 1.20 | $1,501 | $1,181 | 21.3 |
| 2.00 | $1,702 | $1,408 | 17.3 |

| Fixed cost ($/bus-day) | S cost | C cost | Saving % |
|---|---|---|---|
| 60 | $751 | $590 | 21.4 |
| 120 (base) | $1,351 | $1,010 | 25.2 |
| 300 | $3,151 | $2,270 | 28.0 |

**The conclusion is robust across the entire plausible cost range**: even at a variable cost of
$2.00/km — well above the ≈$0.60/km (≈$0.97/mile) model baseline and the ≈$1.19/km
(≈$1.91/mile) state reimbursement benchmark of data items 1–2 — combining still wins by 17%.
Using a **round-trip** convention (afternoon mirrors morning, doubling the variable-distance
term) the rural saving is $322/day (21.5%) and every ranking is preserved.

### 7.5 Balancing cost and comfort (the equity control)

Policy C with the ride penalty α tuned gives the cost–comfort **Pareto frontier**:

| α ($/student-min) | Buses | Cost ($) | Max E ride | Max H ride |
|---|---|---|---|---|
| 0.00 | 7 | 1,010 | 51.6 | 42.7 |
| 0.02 | 7 | 1,010 | 45.3 | 37.1 |
| 0.05 | 7 | 1,012 | 41.8 | 37.1 |
| 0.20 | 8 | 1,157 | 41.8 | 33.3 |
| 0.50 | 13 | 1,873 | 33.8 | 26.1 |

**This is the "balancing" mechanism.** With a *free* ride-time penalty (α ≈ 0.02–0.05) the
district gets maximum cost savings *and* a lower worst-case elementary ride (51.6 → 41.8 min) for
almost no extra money — the optimum simply avoids long routes. Pushing for very short rides
(e.g. max 34 min) costs nearly double. A board can pick its point on this frontier explicitly
rather than by accident.

### 7.6 Testing the model before implementation

**A. Structural validation** (done here): exact-optimum cross-checks (§7.1); analytic bounds;
reproducibility from seeds.

**B. Stress test under real-world uncertainty.** We replayed the fixed schedules in a
Monte-Carlo simulation with random travel-time shocks (coefficient of variation 8–25%) on top of
the deterministic plan:

| Design ride cap | Buses | Cost ($) | P(any student rides > 60 min) | Worst realised ride |
|---|---|---|---|---|
| 60 min (naive) | 7 | 1,010 | **34.8%** | 92 min |
| 55 min | 8 | 1,132 | 21.4% | 88 min |
| 50 min | 8 | 1,161 | 9.1% | 95 min |
| **45 min** | 9 | 1,311 | **1.4%** | 76 min |
| 40 min | 12 | 1,708 | 1.0% | 70 min |

**A plan built right at the 60-minute limit is unsafe**: ordinary variability violates the
one-hour rule on ~1 day in 3. Building a **10–15-minute safety margin (nominal design ≤ 45 min)**
cuts the violation probability to ~1% for only ~$300/day — the single most important
pre-deployment finding.

**C. Recommended pilot protocol.**
1. Run the model on the district's **actual** stop/address data and two weeks of GPS trip logs.
2. Re-fit speed and service times to observed data; re-solve and compare predicted vs. actual
   route durations (target ≤ 10% error).
3. Implement **one** paired route as a pilot for a marking period, with AVL (GPS) and a
   driver/student feedback form; verify the stagger window and the ride-time margin.
4. Re-run the Monte-Carlo on the pilot's realised times; only then scale district-wide.
5. Monitor passenger loads (the capacity constraint) with automatic ridership counts.

## 8. Strengths, Limitations and Improvements

**Strengths.** (i) A single MILP that *simultaneously* optimises routing, vehicle reuse and
equity, so policies are compared on equal footing rather than by rule of thumb. (ii) Provably
near-optimal on validation instances. (iii) Transfers unchanged from rural to urban districts.
(iv) The cost/equity trade-off and the required safety margin are explicit quantities a board
can act on.

**Limitations.** (i) Ride-time shocks are modelled as travel-time noise, not full stochastic
optimisation. (ii) Stop-level demand is synthetic (address data is private). (iii) The model
covers the morning run; mid-day shuttles, sports runs and special-needs transport are out of
scope. (iv) Capacity is treated as seats, ignoring that sibling groups and accessibility riders
may force slack.

**Improvements.** Add a middle school (three-tier scheduling); joint morning/afternoon
optimisation and driver-shift (duty) constraints; a state-aware scheduler to *choose* the bell
stagger Δ as a decision variable; and stochastic/robust routing with chance constraints on the
60-minute rule. Column generation or a metaheuristic would let the same model scale to
city-wide fleets.

## 9. Conclusions and Recommendations

1. **Stagger the bells and combine the tiers.** A ≥40-minute stagger between the elementary and
   high-school bells lets buses and drivers be reused, cutting the fleet by ~30% and cost by
   ~25% (rural) to ~28% (urban).
2. **Combining is not a comfort sacrifice.** High-school ride times *fall*; overall
   student-minutes and the share of long rides fall too. Elementary worst-case rides rise only
   modestly and stay within an hour.
3. **Build in a safety margin.** Design routes to ≤ 45–50 nominal minutes, not 60, so ordinary
   variability does not break the one-hour rule; the extra cost is small and buys reliability.
4. **Use the model, not a rule of thumb.** The optimal number of paired routes depends on the
   stagger, capacity and cost mix; the model chooses it automatically and can be re-run whenever
   enrolment, fuel prices or bell times change.
5. **Recommendation:** adopt the staggered combined policy, set α ≈ 0.02–0.05 to guarantee fair
   ride times at nearly no cost, and pilot one paired route with GPS verification before a
   district-wide rollout.

---

## 10. Article for the School Board

***Getting More Mileage From Every Bus: A Data-Driven Look at Our Routing***

Our district's students live far apart, so the yellow bus is how most of them get to school — and
transportation is one of our largest non-instructional costs. Every bus we run costs roughly
**$120 a day** in driver time, fuel, insurance and wear *before it turns a wheel*, plus about
**60 cents for every kilometre** it drives. The question we asked was simple: **can we move the
same students with fewer buses without making anyone's ride unreasonable?**

Today we run **separate buses** for each school. That is easy to schedule, but it means we own
and staff two fleets that often travel the same country roads twice. There is an alternative.
Because the elementary school rings its bell **40 minutes before** the high school, a bus that has
just dropped off younger students can immediately turn around and collect older students — one
bus and one driver doing two jobs. This is the **"staggered" or combined schedule**.

We built a computer model that lays out the best possible route plan under our real constraints:
no student on a bus for more than **one hour**, no bus carrying more than its **72 seats**, and
every stop served. It then compares the two strategies honestly, counting dollars *and* minutes.

**What it found (for a district like ours, 596 students):**

- **Separate buses:** 10 buses, about **$1,351 per day** ($2.27 per student).
- **Combined (staggered) buses:** 7 buses, about **$1,010 per day** ($1.69 per student).

That is **three fewer buses and about 25% lower cost — roughly $61,000 a year** — plus the
avoided purchase of three buses (hundreds of thousands of dollars over their life). And it is
**not at the students' expense**: because high-school routes must fit the shorter window, the
**longest** high-school ride actually *drops* (from about 50 to 43 minutes), and the number of
students riding more than 45 minutes falls. Elementary rides stay comfortably under the hour.

**Three honest caveats.** First, the combined plan needs a bell-time gap of at least about half
an hour; if we ever shrink that gap, the savings shrink with it. Second, we should design routes
with a **safety margin** — not right at the 60-minute limit — so that a snow day or heavy traffic
does not push a child over the hour. Third, this model plans the main morning and afternoon runs;
athletic trips and special-services transport are handled separately.

**What we recommend.** Adopt the combined schedule, keep the bell-time gap at 40 minutes or
more, and pilot **one** combined route for a marking period with GPS tracking before we change
the whole district. The model already tells us how much we will save and how long each child will
ride; the pilot tells us how it feels on a real Monday morning.

We are not asking the board to trust a program. We are asking for a **measured, reversible pilot**
whose numbers we will bring back to you.

---

### Appendix — Reproducibility

| File | Purpose |
|---|---|
| `code/sbrp.py` | model core: instances, route evaluation, savings + 2-opt pools, set-partitioning MILP |
| `code/run_experiments.py` | base cases + all sensitivity sweeps; writes `results/*` |
| `code/validate_small.py` | exhaustive exact-optimum validation |
| `code/testing.py` | equity sweep, Monte-Carlo robustness, safety-margin study |
| `code/sens_var.py` | variable-cost sensitivity |
| `data/references.md` | sourced empirical inputs |
| `results/experiments.json`, `results/tables.md`, `results/routes_rural.csv` | machine-readable + tabular results |
| `logs/run.log`, `logs/testing_stdout.log` | run logs |

All experiments are deterministic given the seeds in `sbrp.py` / `run_experiments.py`; runtime
≈ 2 s per district solve, tens of seconds for the full sweep, on a single CPU.
