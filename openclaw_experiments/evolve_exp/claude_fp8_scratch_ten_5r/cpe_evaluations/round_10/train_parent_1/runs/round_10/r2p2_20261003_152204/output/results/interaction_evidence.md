# Expert Interaction Evidence — 2017_ICM Problem D (MM-Bench 2017_D)

Ten exchanges, mechanism → constraint → parameter sequencing. Every reply is
turned into a model parameter/constraint below; the value used in the model is
in `code/model.py` (BASE dict) and the provenance line appears in
`solution.json`'s parameter table.

---

## Exchange 1 — dominant mechanism
**Q:** *At a real security checkpoint, which single stage do passengers most often get stuck at or slow the whole line down?*
**A (gist):** The bottleneck is Zone B — the divestiture/preparation step at the front of the lane. The X-ray and body scanners run at a fixed machine cycle, but the human-paced "unload" step (shoes, belt, jacket, laptop, liquids, pockets, bins) is highly variable; one slow/unprepared passenger stalls the whole lane. Secondary: bin shortage/recirculation, and Zone-D pat-down/flagged-bag secondary screening.
**Used in model:** The pipeline is serial with Zone B (divestiture) as the dominant bottleneck server; the X-ray/belt block (C) is a *fixed, parallel* machine cycle (does not drive the queue), and secondary screening (D) is a probabilistic officer-pulled add-on. This fixes the *shape* of the model (which stage is binding).

## Exchange 2 — constraint on that mechanism
**Q:** *What keeps passengers from getting through the unloading step faster, even when the line is empty and nobody is rushing them?*
**A (gist):** The physical + cognitive task itself, not queue pressure: number of items to divest, bin handling/retrieval, cognitive load & rule-unfamiliarity (the dominant source of variance), physical limits (age, mobility, children), and rule ambiguity causing hesitation/re-doing. None of it speeds up with an empty line.
**Used in model:** Divestiture time is modeled as a *task-paced* random variable (item count + cognitive load), independent of queue length — so variance persists even at low utilization. This justifies a service-time distribution (wide, high CV) rather than a queue-pressure term, and why Pre-Check (fewer items to divest) is structurally faster.

## Exchange 3 — parameter: divestiture magnitude
**Q:** *About how long does a first-time flyer versus an experienced frequent flyer usually spend at the unloading step?*
**A (gist):** Frequent flyer ≈ 20–40 s; first-time/infrequent ≈ 60–120 s (tail 2+ min); gap ~2–4×, driven by decision time and re-handling.
**Used in model:** `div_fast = U[20,40]`, `div_slow = U[60,120]` (seconds). Fast/slow mix per lane from exchange 8.

## Exchange 4 — parameter: ID check
**Q:** *How many seconds does it usually take a TSA officer to check one passenger's ID and boarding pass?*
**A (gist):** ~10 s central (5–15 routine); tail 20–30+ s for mismatches, groups, unclear documents. Pre-Check faster.
**Used in model:** `id = U[5,30]`, mean ≈10 s, two shared officers (parallel M/M/2-like servers at stage A).

## Exchange 5 — parameter: secondary-screening rate
**Q:** *Roughly what fraction of passengers get sent aside for a pat-down or a secondary bag check?*
**A (gist):** ~10–20% combined; pat-down 2–5%, bag flag 5–15%; Pre-Check low end 2–5%.
**Used in model:** `sec_rate_reg = 0.15`, `sec_rate_pre = 0.035`.

## Exchange 6 — parameter: secondary duration + constraint
**Q:** *When a passenger is sent aside for a pat-down or bag search, how long are they usually held up?*
**A (gist):** ~2 min central (1–3 min routine; quick resolution 30–60 s; full 2–5 min; tail 5–10+ min). High-variance and **officer-limited** (pulls an officer off the lane), so its line impact exceeds the raw hold time.
**Used in model:** `sec = U[60,600]` s (mean 120), applied as a path add-on; noted as a variance + officer-load amplifier in the analysis.

## Exchange 7 — parameter: recovery dynamics
**Q:** *After a sudden surge of passengers, roughly how long does the line take to get back to normal?*
**A (gist):** No single figure; governed by **drain rate** (service capacity − continuing arrivals): small surge a few–15 min; moderate (hundreds queued) 20–45 min; large/lane-outage 1–2+ h. Near saturation → slow, variable recovery.
**Used in model:** The saturation knee in the demand sweep (exchange-driven expectation reproduced): wait grows super-linearly as demand approaches divestiture capacity, and the CV stays high near saturation. Recovery/drain logic motivates the "hold demand below the knee" policy recommendation.

## Exchange 8 — traveler-type heterogeneity (cultural axis)
**Q:** *Do some travelers pack more carry-on items or divest more slowly than others, and who tends to?*
**A (gist):** Slow/heavy tail: families w/ children, infrequent flyers, international/long-haul, older/mobility-limited. Fast tail: business/frequent flyers, Pre-Check enrollees (divest less by rule).
**Used in model:** Fast/slow mix per lane: `fast_share_pre = 0.85`, `fast_share_reg = 0.35`. This is the empirical basis for the traveler-type (cultural) sensitivity in subtask (c).

## Exchange 9 — cultural mechanism
**Q:** *When people are uncomfortable being crowded or standing close to strangers, how does that slow the line?*
**A (gist):** Adds **spacing + hesitation** at the queues and belt: larger standoff gaps (same physical queue holds fewer people), delayed advance (dead time per passenger, accumulates), belt-crowding aversion, and fumbling under pressure. Net: same service capacity realized more slowly, **variance rises**; it is a *density/behavior effect, not a change in the underlying task time*.
**Used in model:** Cultural density multiplier `m` on realized divestiture: `t *= (1+0.15(m-1))` plus an extra Gaussian dead-time `~N(0, 3(m-1))` that is inconsistent across passengers → raises both mean and **variance**. This is the lever for subtask (c): personal-space culture (US-style) → higher m.

## Exchange 10 — constraint: Pre-Check lane allocation
**Q:** *Do the Pre-Check lanes usually run as fast or as slow as the regular lanes during the busy peak?*
**A (gist):** Pre-Check is genuinely faster per passenger (divests less, fewer secondaries), but the advantage is **muted** by the lane ratio: ~1 Pre-Check lane per 3 regular lanes while Pre-Check is ~45% of passengers, so Pre-Check queues can still build. Often *feels* comparable at peak.
**Used in model:** Baseline allocation `n_pre_lanes=1, n_reg_lanes=3`, 45/55 demand split. This motivates the "pc_expand" intervention (rebalance lane ratio to demand) and the finding that per-passenger speed alone does not fix a lane-ratio mismatch.

---

## Mapping of each reply to a code constant (source = exchange)

| Parameter | Value | Interval [a,b] | Source |
|---|---|---|---|
| Divestiture, frequent flyer | U[20,40] s | [20,40] | exchange 3 |
| Divestiture, first-time | U[60,120] s | [60,120] | exchange 3 |
| ID check | U[5,30] s (≈10) | [5,30] | exchange 4 |
| Secondary rate, regular | 0.15 | [0.10,0.20] | exchange 5 |
| Secondary rate, Pre-Check | 0.035 | [0.02,0.05] | exchange 5 |
| Secondary duration | U[60,600] s (≈120) | [60,600] | exchange 6 |
| Belt/X-ray full loop | U[5,68] s (mean 28.6) | [5,68] | dataset col H (clean_data.json) |
| MMW/body scan | mean 11.6 s | [3.5,37.5] | dataset (MMW col) |
| Fast-traveler share, Pre-Check | 0.85 | [0.7,0.9] | exchange 8 |
| Fast-traveler share, regular | 0.35 | [0.2,0.5] | exchange 8 |
| Pre-Check : regular lane ratio | 1:3 | — | exchange 10 |
| Pre-Check demand share | 0.45 | [0.4,0.5] | exchange 10 |
| Cultural density multiplier m | 1.0–2.0 | [1.0,2.0] | exchange 9 (US-style high m) |
| Demand (peak, 4-lane) | 240/hr | [200,300] | calibrated to sub-saturation; raw snapshot 405/hr is a peak |
