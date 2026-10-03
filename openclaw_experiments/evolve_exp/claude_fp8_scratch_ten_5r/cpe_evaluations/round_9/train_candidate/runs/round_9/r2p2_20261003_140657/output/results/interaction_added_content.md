# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — 2017_D (MM-Bench)

Ten exchanges, one question each, mechanism-constraint-parameter sequencing.
The expert's replies were turned into model parameters/constraints as listed.
No reply text is reproduced verbatim in the submission; only the value,
constraint, or equation that each reply grounded is carried into the model.

## Exchange 1 (structural / mechanism)
- **Q:** At a busy checkpoint, when a line suddenly gets very long, which station is it usually stuck at?
- **A (distilled):** The bottleneck is the Zone B divesting/binning table at the front of
  each lane — human-paced, highly variable, shared by the whole lane. X-ray belt and
  walk-through scanner run at fixed mechanical pace and are rarely the constraint.
  Zone A (ID check) is fast and staffed in parallel, so it usually clears.
- **Work it became:** Fixed the model shape — a queueing network in which Zone B
  (divesting) is the dominant, variable, single-server bottleneck; X-ray and scanner
  are near-deterministic low-variance stations. All modification designs target Zone B.

## Exchange 2 (constraint on the mechanism)
- **Q:** Beyond the number of open lanes, what stops a single lane from processing faster at the divesting table?
- **A (distilled):** The divesting table is a single-server, human-paced, sequential
  station: one passenger at a time; the next cannot start until the previous clears
  the table and steps to the scanner. Limits: serial table/bin occupancy, passenger-
  paced (not officer-paced) task time, bin recirculation, downstream blocking, and
  conveyor spacing. Even with unlimited lanes, each lane's divesting throughput is
  capped by one-at-a-time, passenger-controlled loading.
- **Work it became:** Constraint C1 — per-lane Zone B is a M/G/1-style single server
  with service time set by the passenger, not staff; adding officers does not reduce
  it. This is why "add officers" is not the fix; the fix must reduce passenger-paced
  work or add parallel table capacity.

## Exchange 3 (parameter — the key one)
- **Q:** How many seconds does a regular non-Pre-Check passenger typically spend loading bins at the divesting table?
- **A (distilled):** Regular ~30–60 s, central 40–45 s; Pre-Check ~15–25 s (skips
  shoes/belt/jacket, laptop stays in bag). Strongly right-skewed; unprepared/elderly/
  family travelers 90 s+; that tail drives the variance.
- **Work it became:** Zone B service-time distributions: regular ~ Gamma/Lognormal
  centered 40–45 s with a heavy right tail (P90≈90 s); Pre-Check ~ Gamma centered
  20 s. The tail is the modeled source of wait-time variance.

## Exchange 4 (parameter — fixed mechanical pace)
- **Q:** For a clean pass, how many seconds does the walk-through metal detector or millimeter-wave scanner take?
- **A (distilled):** Metal detector ~3–7 s; millimeter-wave ~5–10 s (brief stationary
  pose + processing pause). Near-fixed, low variance; treat clean-pass scanner as a
  ~5–8 s constant. The real delay here is the alarm→pat-down minority (Zone D), not
  the clean-pass majority.
- **Work it became:** Scanner = constant ~6 s service, negligible variance. Variance
  injected separately at Zone D (alarm branch).

## Exchange 5 (parameter — Zone D / variance source)
- **Q:** What share alarm and need a pat-down, and how long does the pat-down take?
- **A (distilled):** ~1–3% alarm (higher for millimeter-wave, implants, bulky
  clothing). Pat-down central ~90 s, right-skewed; routine under a minute, but a
  secondary search, bag re-check, or wait for a same-sex officer can push 4–5 min+.
  Low rate → little effect on mean throughput, but a meaningful variance and
  localized-stall source, especially when the officer is pulled from another station.
- **Work it became:** Zone D = Bernoulli(p≈2%) branch adding ~90 s (heavy-tailed) to
  the lane, with a probability of "officer borrow" that stalls a second lane — the
  modeled generator of occasional unexplained localized lines.

## Exchange 6 (parameter — Pre-Check mix)
- **Q:** What share of security passengers at a large US airport actually use Pre-Check when screening?
- **A (distilled):** ~40–50% enroll; effective on-the-day usage often 35–45% (some
  enrolled travelers stay in the regular lane — airline/itinerary/companions). Hub
  business airports 50%+, leisure airports below 40%. 45% is a reasonable central.
- **Work it became:** Pre-Check share p_pre as a model input, base 0.45, swept
  0.35–0.55. The data snapshot itself shows ~55% pre-check arrivals, so the model is
  run at the dataset mix as a second scenario.

## Exchange 7 (structural — lane allocation, the congestion driver)
- **Q:** With four open lanes and half the passengers Pre-Check, how are lanes split?
- **A (distilled):** Not proportional to demand — a fixed staffing rule: 1 Pre-Check
  lane for every 3 regular lanes. So 4 lanes → 1 Pre-Check + 3 regular, even though
  Pre-Check is ~half the volume. The single Pre-Check lane therefore carries the
  heavier per-lane load. Ratio flexes with staffing (some airports 1:2 or open a
  second Pre-Check lane at peak).
- **Work it became:** Lane-allocation parameter (n_pre : n_reg). Base case 1:3
  (as the problem states); the central finding of the model is that 1:3 with a 45–55%
  Pre-Check mix overloads the Pre-Check lane relative to demand — the "unpredicted"
  Pre-Check line. Modification M1 reallocates lanes proportional to effective demand.

## Exchange 8 (parameter — cultural / queueing behavior, Part c)
- **Q:** When travelers stand close together in a queue versus keeping personal space, how does that affect the speed of loading the divesting table?
- **A (distilled):** Personal space affects how fast the queue FEEDS the table, not
  the loading task. Close-packed → table continuously occupied, throughput at cap.
  Generous spacing → dead-time gaps between occupants; table idles; loss scales with
  gap size relative to the ~40–45 s load. Effect is modest (a few seconds) unless
  spacing/cut-avoidance norms are strong, then idle gaps accumulate and the lane slows.
- **Work it became:** Cultural style = a table-utilization loss. Model adds an
  inter-occupant dead-time δ (seconds) that reduces effective Zone B service rate
  by δ/(S_B+δ). δ swept to represent: close-packed/collective (δ≈0), US personal-space
  (δ≈2–4 s), strong cut-avoidance/slow (δ≈5–8 s). Accommodation: pre-staged bin
  stations and a "call-forward" pacing that keeps the table fed, decoupling arrival
  spacing from service occupancy.

## Exchange 9 (parameter — arrival process / surge)
- **Q:** How do arrivals vary over a day — steady, or bursts after flight waves?
- **A (distilled):** Bursts driven by flight departure banks (30–60 min clusters, then
  lulls). Passengers arrive ~1–2 h pre-departure, so the checkpoint sees surge-and-lull
  with 2–4 peaks/day. Peak-hour rate ~2–3× the daily mean. Partly predictable
  (schedule) but noisy: self-selected arrival times (right-skewed) plus delays,
  cancellations, one large aircraft → the "unexplained" long lines.
- **Work it became:** Arrivals = non-homogeneous Poisson with a diurnal envelope and
  a surge multiplier (peak 2.5× mean, swept 2–3×) plus random event shocks. The model
  is evaluated at peak (the regime that produces the observed variance), not the mean.

## Exchange 10 (parameter — recovery / drain, variance)
- **Q:** After a surge clears and arrivals drop, how quickly do the lines drain back down?
- **A (distilled):** Quickly — a few minutes to ~15 min, not hours. A lane clears ~1
  passenger/40–60 s; once arrivals < service rate the backlog empties at the net
  margin. Drain slower than fill (builds fast, empties at net margin). Tail effects:
  a few pat-downs, an X-ray alarm, or a bin shortage re-stall a lane; if the next
  flight bank arrives before the backlog clears, the line never fully drains.
- **Work it became:** Validated the M/M/c-style drain dynamics (net-margin
  clearance) used for the steady-state vs. peak comparison. The "next wave arrives
  before drain completes" condition is the model's instability criterion: a lane
  becomes unstable (queue grows) when ρ = λ/μ → 1, and a transient surge that leaves
  a residual backlog at the start of the next bank produces the persistent line.

## Parameter table carried into the model (sources = exchanges)
| parameter | value / interval | source |
|---|---|---|
| Zone B service, regular S_B_reg | central 42 s, range [30,60], P90≈90 | Exch 3 |
| Zone B service, Pre-Check S_B_pre | central 20 s, range [15,25] | Exch 3 |
| Scanner (clean pass) S_scan | 6 s, range [5,10], ~deterministic | Exch 4 |
| X-ray belt S_xray | ~5–8 s per bag (low variance) | Exch 2, 4 (fixed pace) |
| Zone D alarm p_alarm | 2%, range [1,3] | Exch 5 |
| Zone D pat-down S_patdown | central 90 s, range [60, 300+] | Exch 5 |
| Pre-Check share p_pre | 45% base, range [35,55] (dataset ≈55%) | Exch 6 |
| Lane split n_pre:n_reg | base 1:3; M1 reallocates | Exch 7 |
| Cultural dead-time δ | [0,8] s (close-packed 0, US 2–4, strong 5–8) | Exch 8 |
| Arrival surge peak/mean | 2.5×, range [2,3] | Exch 9 |
| Arrival process | non-homog Poisson, 2–4 diurnal peaks | Exch 9 |
| Drain / stability | net-margin; unstable as ρ→1 | Exch 1 |
| Bottleneck identity | Zone B divesting table | Exch 1 |
