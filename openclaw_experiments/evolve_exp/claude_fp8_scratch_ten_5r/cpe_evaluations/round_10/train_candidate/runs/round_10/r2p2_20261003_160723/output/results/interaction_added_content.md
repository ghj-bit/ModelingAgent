# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — 2017_D (TSA checkpoint bottleneck model)

## Exchange 1
**Question:** Do passengers finish the body scan before they reach the belt to collect their bags?
**Reply (gist):** The body scan (millimeter-wave/metal detector, + possible pat-down) and the bag X-ray run as two *parallel* streams. A passenger may reach the post-X-ray belt before, at, or after finishing the body scan; there is no enforced ordering. In practice the body-scan + pat-down step is often the longer and more variable of the two.
**How it shaped the work:** Sets the core system structure. The model must treat "bag X-ray" and "body scan" as two parallel services; a passenger's completion time is the max of the two stream completions. The body-scan side is the dominant, most variable service — the likely bottleneck. This drives the queueing structure (two parallel queues, exit gated by the slower one).

## Exchange 2
**Question:** On a busy morning, which step causes most of the piling up?
**Reply (gist):** The bottleneck is the X-ray/bag-screening stream and the downstream Zone D secondary screening — not ID check or the body scanner. The X-ray conveyor is a single shared resource per lane with a long, variable service time (bins, laptops, liquids, flagged items); a flagged bag pulls an officer off the line, compounding slowdown. Body scanning is comparatively fast and parallelizable; ID check is quick. Piling up concentrates at the Zone B queue feeding the X-ray lanes and at the post-X-ray belt; Zone D secondary screening is the main source of variance.
**How it shaped the work:** Re-orients the bottleneck. The dominant queue is the Zone B → X-ray stream; the key variance driver is the flag rate (a Bernoulli "bag flagged" event) that routes a share of passengers to Zone D with a much longer secondary service time. The model must carry: per-lane X-ray service time (variable), a flag probability p_flag, and a Zone D secondary service time. These become the calibrated parameters to pin down (exchanges 3+).

## Exchange 3
**Question:** Out of roughly 100 bags going through the X-ray, how many usually get flagged for a closer look?
**Reply (gist):** ~5–15 out of 100, on the order of 10%, is the usual X-ray flag rate; varies with passenger/item mix and how aggressively the operator flags. Pre-Check bags tend to be flagged at a lower rate than regular-lane bags.
**How it shaped the work:** Pins the Bernoulli flag probability. Base p_flag ≈ 0.10, sensitivity interval [0.05, 0.15]; Pre-Check uses a lower value (see exchange for Pre-Check specifics). This parameter sets the fraction of the flow routed to Zone D and thus the tail of the wait-time distribution.

## Exchange 4
**Question:** How many minutes does a closer manual inspection usually take?
**Reply (gist):** Routine manual bag inspection is on the order of 1–3 minutes, central ~2 min. Simple re-scan/swab under a minute; a full unpack-and-search, explosives-trace swab, or pat-down can run 3–5 min or more. The distribution is right-skewed — a small fraction of inspections take much longer and drive most of the variance.
**How it shaped the work:** Zone D secondary service time: base ≈ 2 min, range [1, 3], tail [3, 5+]. Right-skewed tail justifies modeling it with a skewed distribution (e.g., lognormal) in the simulation. This is the dominant contributor to wait-time variance, per exchange 2.

## Exchange 5
**Question:** How many passengers, one after another, can one open lane screen per hour?
**Reply (gist):** ~100–200/hour per open lane, central ~150/hour for a regular lane. A fast lane approaches 200/h; heavy bin use, laptops/liquids, or frequent secondary screening drops it toward 100/h. Pre-Check lanes run higher, often 200–300/h (central ~250), because passengers divest less and are flagged less.
**How it shaped the work:** Sets the per-lane service capacity (1/rate): regular ≈ 600s/passenger (interval [300, 360]... i.e. 100–200/h → 3–6 min), central 4 min (240s); Pre-Check central ~144s (2.4 min), range [120, 180]s. These calibrate the lane service-time in the queueing model and give the utilization ρ = λ/μ.

## Exchange 6
**Question:** How many passengers reach the checkpoint in a minute during a busy morning?
**Reply (gist):** ~10–30/minute at a single checkpoint at busy-morning peak, central ~15–20/minute. Large hubs approach 30/min; smaller/moderate checkpoints nearer 10/min. This is the arrival rate to compare against lane capacity (~2.5/min per regular lane) to size how many lanes must be open for a stable queue.
**How it shaped the work:** Sets the arrival rate λ (Poisson in the simulation), central ~17.5/min, sensitivity [10, 30]/min. Combined with lane capacity, utilization ρ = λ/(N·2.5) — stability requires N ≥ λ/2.5 ≈ 7 lanes at central peak. This λ is the key lever for the variance-reduction analysis: the checkpoint operates near saturation at peak, where wait variance explodes.

## Exchange 7
**Question:** Of all passengers using a checkpoint on a typical day, what share is in Pre-Check?
**Reply (gist):** ~40–50%, central ~45% (the problem statement itself cites ~45% enrollment). Varies by airport/time of day; lower at smaller airports, higher at large hubs with business travelers.
**How it shaped the work:** Sets the Pre-Check mixing proportion p_pc = 0.45, sensitivity [0.40, 0.50]. With 1 Pre-Check lane per 3 regular lanes but 45% of demand, Pre-Check lanes run at much higher utilization — a structural imbalance the model must capture and the recommendations must address.

## Exchange 8
**Question:** When the line grows long, do most travelers switch to an open lane?
**Reply (gist):** No — most commit to a lane once they enter the Zone B queue; the physical layout (railings, single-file queue, belongings on the belt) makes mid-queue switching impractical, and the social norm against "cutting" discourages it. Switching happens mainly at lane-selection, and even then most pick the nearest/shortest-looking queue and stay. A long line mostly lengthens waiting rather than redistributing passengers.
**How it shaped the work:** Establishes the queue discipline as *non-pooling / lane-committed* by default, not a shared FCFS pool. This is the key cultural/behavioral parameter: a parameter "share of travelers who will re-queue to a shorter lane" (lane-switching propensity) defaults low. The cultural sensitivity (Americans respect personal space / anti-cutting → very low propensity; cultures prioritizing individual efficiency → higher) modulates this. A shared serpentine queue (one line feeding multiple lanes) is a direct structural remedy to remove the commitment bottleneck.

## Exchange 9
**Question:** Do people tend to bring more bags and bins into the screening lane?
**Reply (gist):** Yes — most arrive with a carry-on plus a personal item; each of those plus divested items (shoes, belt, jacket, electronics, liquids, laptop) goes in its own bin, so a passenger commonly occupies 2–4 bins (families/heavy travelers more). Bin count, not passenger count, loads the X-ray conveyor: more bins → longer belt occupancy → slower effective per-lane throughput. Pre-Check uses fewer bins (no shoe/belt/jacket removal, laptop stays in bag), a large part of why their lanes run faster.
**How it shaped the work:** Makes the X-ray (dominant) stream's service time a function of bins-per-passenger: regular mean ~3 bins, Pre-Check ~1.5–2 bins. This is why the two lane types have different service rates even at the same arrival intensity, and it lets the model predict that reducing divestment (a modification) cuts X-ray time per passenger.

## Exchange 10
**Question:** How long does checking one traveler's ID and boarding pass usually take?
**Reply (gist):** ~10–20 s per traveler for a routine ID/boarding-pass check, central ~15 s. Quick glance-and-wave (familiar/Pre-Check) under 10 s; slower check (scrutiny, fumbling, flagged pass) 30 s or more. One of the fastest steps, rarely the bottleneck.
**How it shaped the work:** Sets the Zone A (ID check) service time: central 15 s, range [10, 20], tail ~30 s. Confirms ID check is not the bottleneck (consistent with exchange 2), so it is a fast pre-stage in the queueing model.

## Calibrated parameter table (all values from exchanges; dataset-derived noted)
| name | value | interval [a,b] | source |
|---|---|---|---|
| p_flag (regular) | 0.10 | [0.05, 0.15] | exchange 3 |
| p_flag (Pre-Check) | 0.05 | [0.02, 0.08] | exchange 3 (Pre-Check lower) |
| Zone D secondary service (min) | 2.0 | [1, 3], tail [3,5+] | exchange 4 |
| regular lane capacity (pass/hr) | 150 | [100, 200] | exchange 5 |
| Pre-Check lane capacity (pass/hr) | 250 | [200, 300] | exchange 5 |
| arrival rate (pass/min, peak) | 17.5 | [10, 30] | exchange 6 |
| Pre-Check share | 0.45 | [0.40, 0.50] | exchange 7 (problem states ~45%) |
| lane-switching propensity (base) | low (~0.1) | [0, 0.5] | exchange 8 (most do not switch) |
| bins/passenger (regular) | 3 | [2, 4] | exchange 9 |
| bins/passenger (Pre-Check) | 1.75 | [1, 2.5] | exchange 9 |
| ID check service (s) | 15 | [10, 20], tail ~30 | exchange 10 |
| body scan vs X-ray ordering | parallel; body+patdown more variable | — | exchange 1 |
| dominant bottleneck | X-ray stream + Zone D secondary | — | exchange 2 |

## How the model used the exchanges (work performed)
- Data cleaned (clean_data.py, derive_throughput.py): belt-to-belt property mean 28.6s
  (5-68s, CV 0.48); ID-check officer throughput 32-54/hr (fast, not the bottleneck);
  X-ray and body-scan are the slower resources. Confirms exchange 1 (parallel streams)
  and exchange 2 (X-ray + Zone D is the binding stage).
- model4.py: fixed-demand M/M/c discrete-event simulation. Calibrated so the 8-lane
  peak sits at per-lane utilization rho=0.85 (base lane service ~40.6s incl. flag/Zone-D
  tail and pat-down tail; total arrival 0.167/s ~ 600/hr ~ 75/hr/lane). Results:
  base mean wait 21s, p95 97s, CV 1.57. Lane sweep shows a sharp phase transition:
  4 lanes (rho 1.7) -> mean wait 8.6 hr; 8 lanes (0.85) -> 21s; 12 lanes (0.57) -> 0.4s.
- Modifications (same demand): +4 lanes -> wait 0.4s; pflag 0.10->0.05 -> mean wait 9s
  (-56%); Zone D 2->1 min -> 6s (-70%); bins 3->2 -> 12s (-44%); serpentine CV -25% ->
  -8%. The Zone-D tail and the flag rate are the dominant variance levers.
- culture2.py: exact M/M/1-per-lane cultural sensitivity. Committed routing (exchange 8)
  gives imbalanced lane loads: baseline -> 37.5% of lanes unstable (rho>1); courteous
  (anti-cutting) -> 50% unstable, max lane rho 1.84. Efficient travelers (re-queue)
  self-balance to 12.5% unstable. A system-level serpentine/shared queue (w->0) puts
  every lane at rho=0.85 with 0 unstable lanes and uniform wait 226s.
