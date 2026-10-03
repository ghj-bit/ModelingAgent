# Interaction Evidence — Problem 2017_D (TSA Checkpoint Modeling)

Ten expert exchanges were run, one question each. Each reply is converted into a
concrete parameter, constraint, or model change below (value/range, source =
exchange number, and the interval over which it holds). The replies are input,
not content: no reply text is copied into the submission.

## Exchange 1 — Dominant bottleneck
- **Q:** At a busy US checkpoint, which step slows the line most: removing shoes/laptops, the body scan, or collecting bags afterward?
- **A (summary):** Reclaim-and-re-dress at the X-ray belt exit (Zone C) is the dominant line-slowing step. Re-dressing/reclaim ≈ 30–60 s per passenger and is highly variable/self-paced; divestment ≈ 10–20 s; the scan itself is only a few seconds. The *variance*, not just the mean, makes it the bottleneck.
- **Used in model:** Set reclaim mean `t_reclaim = 45 s` (range 30–60 s) and reclaim as the variance driver; lane occupancy = divest + scan + reclaim, so reclaim dominates. Holds for a busy US checkpoint during the peak window.

## Exchange 2 — Secondary-screening rate
- **Q:** During peak, how often do X-ray bags trigger alarms needing extra officer attention?
- **A (summary):** Combined bag-alarm + pat-down rate ≈ low-to-mid teens percent; bag alarms ≈ 5–10 %, body-scan failures ≈ 1–3 % (higher in regular lanes, lower in Pre-Check). Each secondary event consumes an officer for a variable 1–3 min.
- **Used in model:** `p_bag = 0.07`, `p_body = 0.02` (regular lane ≈ 9 % combined; Pre-Check scaled down by 0.4×/0.1×). Secondary events are modeled as officer work in Zone D that does *not* block the main belt (they are parallel), matching "an officer is consumed" rather than "the lane stops."

## Exchange 3 — Which queue grows first near capacity
- **Q:** Near capacity, which queue gets longer first — ID check or the screening belt?
- **A (summary):** The ID-check line (Zone A) grows first: it is a few-server station with short fixed service and little buffer. The belt lags and only binds at higher load when the reclaim step saturates.
- **Used in model:** Justifies a two-stage series model (ID pool → lane pool) with the ID stage as the upstream, low-buffer queue and the lane stage as the downstream saturation point. Drives the choice to right-size both stages to a utilization target and to study the ID stage separately.

## Exchange 4 — Pre-divestment in the ID line
- **Q:** If the ID line is long, should officers let passengers start removing shoes/laptops while they wait?
- **A (summary):** No, not in the ID line itself — undressing in the ID queue means passengers hold loose items into a second queue and slow their own bin prep. What helps is (a) adding ID capacity / splitting Pre-Check and regular flows, and (b) moving divestment to a wider parallel prep area so it overlaps belt movement.
- **Used in model:** Modification M1 is implemented as a *pre-divestment lane* that removes a fraction (40 %) of divestment work from the lane occupancy (divestment overlaps earlier), NOT as passengers undressing in the ID line. This is the model change the reply supports.

## Exchange 5 — Abandoned bins
- **Q:** In the US, how often do passengers leave belongings in the reclaim bin and walk away?
- **A (summary):** Rare, ≈ 1–3 % of passengers, mostly distracted/rushed or juggling children; rate rises when the belt is congested and bins mix. Each event is costly out of proportion: an officer secures/logs the item and the belt can stall.
- **Used in model:** Models belt stoppages as an occupancy-inflating event on the lane (Poisson stop per lane-occupancy, mean stall 45 s). Congestion raises the effective stop exposure, capturing the "belt stalls while the abandoned bin is cleared" mechanism without a separate rare-event channel.

## Exchange 6 — Holiday surge magnitude
- **Q:** During holiday surges, does a checkpoint handle roughly double its usual count?
- **A (summary):** No — typically 1.3–1.6× the daily count, with peak-hour throughput 1.5–2× the normal peak hour. Capacity is bounded by lanes/officers/belt speed, so airports add staffing; the surge is spread over a longer window.
- **Used in model:** The "peak burst" scenario uses a demand multiplier of 1.5 (the stated mid-range) rather than 2.0, applied to the arrival rate. This bounds the surge study to a realistic 1.3–1.6× envelope.

## Exchange 7 — Pre-arrival ID check acceptance
- **Q:** Would most passengers accept a short pre-arrival ID check to shorten the in-line wait?
- **A (summary):** No — the in-line ID check is short and not the pain point; the pain is total time and its variance. A mandatory pre-arrival step adds an obligation many travelers can't/won't complete, creating a two-tier flow. Passengers accept comparable trade-offs only when voluntary and bundled with a benefit (Pre-Check).
- **Used in model:** Excludes a mandatory pre-arrival ID check from the recommended modifications. Recommends *voluntary* Pre-Check-style opt-in and in-checkpoint changes only; the model does not credit a pre-arrival step.

## Exchange 8 — Cultural spacing in queues
- **Q:** At Japanese/Singaporean checkpoints, do passengers stand closer together than in the US?
- **A (summary):** Yes — noticeably, on the order of half the US spacing or less. A real cultural norm, not a rule. Tighter spacing holds more people in the same queue footprint and changes the queue-length-to-wait mapping and physical space per waiting passenger, but does not change service times or throughput.
- **Used in model:** Cultural spacing affects the *physical* queue footprint and the visible-line-to-wait mapping, not service rates. Therefore the cultural sensitivity analysis is applied to (i) the reclaim variance multiplier `k_reclaim` (traveler style/pace) and (ii) noted as a physical-queue-length effect, consistent with "does not change service times." This drives the `k_reclaim` sweep (0.8 efficient / 1.0 US / 1.3–1.6 variable).

## Exchange 9 — Bags vs metal as a line-slower
- **Q:** Which slows a line more: travelers with many carry-on bags, or travelers wearing lots of metal?
- **A (summary):** Many carry-on bags slow the line more: more bins, more belt time at both divestment and reclaim (reclaim is dominant), higher odds of a manual search, and they consume belt length/bin supply. Metal items add mostly a one-time divestment cost. A 3+-bag passenger adds on the order of 20–40 extra seconds; a heavily metal-laden passenger ~5–15 s. The bag effect is also more variable.
- **Used in model:** Bag count is treated as the variance and occupancy driver (more bags → longer, more variable reclaim/divest), consistent with reclaim dominance. Supports keeping bag-related variability in the service-time distributions and the secondary-screening probability rather than treating metal as the primary line-slower.

## Exchange 10 — Behavior when the belt stops
- **Q:** When the belt slows or stops, do passengers block the exit to find their bags?
- **A (summary):** Yes — scanned passengers stop at the reclaim point and wait for their own bin rather than stepping aside; the reclaim area fills with stationary passengers. It is self-reinforcing: stopped belt → delayed reclaim → blocked exit → backup propagates upstream. Strongest among multi-bag or flight-anxious passengers; a primary reason reclaim is the dominant bottleneck.
- **Used in model:** Justifies modeling belt stoppages as a *self-reinforcing* occupancy inflation on the lane (a stop adds to the lane's occupancy, which increases the next stop's exposure), rather than as an isolated delay. This is the mechanism that makes the reclaim stage the binding, variance-producing bottleneck and is the target of Modification M2 (side tables that reduce reclaim variance and shorten stalls).

## Consolidated parameter table (empirical inputs)
| Parameter | Value | Interval | Source |
|---|---|---|---|
| Reclaim & re-dress mean | 45 s | 30–60 s | Exchange 1 |
| Divestment mean | 20 s | 10–20 s | Exchange 1 |
| Body scan (mm-wave) mean | 6 s | few s | Exchange 1 |
| ID check mean | 11 s | 5–15 s | dataset (ID Check Process Time cols) |
| Bag-alarm rate (regular) | 0.07 | 0.05–0.10 | Exchange 2 |
| Body-scan failure rate (regular) | 0.02 | 0.01–0.03 | Exchange 2 |
| Pre-Check secondary scaling | 0.4× / 0.1× | — | Exchange 2 |
| Surge demand multiplier | 1.5 | 1.3–1.6 | Exchange 6 |
| Belt-stop mean stall | 45 s | — | Exchange 5 (costly out of proportion) |
| Abandoned-bin incidence | 1–3 % | 1–3 % | Exchange 5 |
| Reclaim variance multiplier (culture) | 0.8 / 1.0 / 1.3 / 1.6 | 0.8–1.6 | Exchanges 8, 9, 10 |
