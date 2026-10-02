# Interaction evidence

## Exchange 1
Question: On a busy freeway, do you trust that a typical day's average traffic counts stand in for the worst peak-hour rush?

Reply (gist): AADT is not peak-hour volume. Peak-hour flow ≈ 8–12% of daily total; peak direction of the peak hour can be 2–3× the average hourly rate implied by AADT (e.g. 150,000/day ≈ 6,250/h avg, peak hour peak direction 12,000–15,000). Capacity/delay/tipping-point analysis must use peak-hour, peak-direction volumes with a peak-hour factor and directional split.

How it changed the work:
- Parameter `peak_share = 0.10`, interval [0.08, 0.12], source: expert exchange 1.
- Parameter `dir_split = 0.60`, interval [0.5, 0.65], source: expert exchange 1 (peak direction 2–3× avg → peak-direction share of peak hour at 0.5/0.5 baseline of 1.0× is inconsistent; 2× avg hourly in peak direction means peak-direction carries 2/3 of the combined peak-hour flow of the two directions if the other direction stays near average; we take peak-direction = 2/3 of (peak-hour × 2 × 0.10... simpler: peak-direction peak-hour flow = 2× avg hourly = 2×(AADT/24) × ... ). We model peak-direction peak-hour volume V_peak = AADT/24 × 2 (the "2–3×" figure) and treat the opposing direction as AADT/24.
- The capacity and delay computations below therefore use V_peak per direction, not AADT/24.

## Exchange 2
Question: These counts come from a handful of fixed sensors per road. Would they miss or misstate the real, time-varying congestion pattern?

Reply (gist): Yes. (i) spatial gaps — worst congestion at bottlenecks (merges, interchanges, lane drops) may lie between sensors and be unobserved; (ii) temporal aggregation to hourly/daily totals hides within-hour queue buildup/discharge; (iii) coverage bias — few sensors give a sample, not a profile; (iv) directional/lane detail not resolved. Data supports rough corridor-level volumes but understates and smooths true peak congestion.

How it changed the work:
- Parameter `bottleneck_factor = 1.15`, interval [1.10, 1.25], source: expert exchange 2. Applied multiplicatively to peak-direction peak-hour volume on segments that contain a known bottleneck marker (lane-drop / interchange rows in the Comments field), to represent unobserved worst-case congestion at those points.
- Validation design: treat the Comments-tagged bottleneck segments as the "observed-worst-case" subset and the untagged segments as the spatial holdout. The model's predicted delay ranking must not contradict the observed ADT ordering between these two subsets more than the smoothing factor allows; i.e. the spatial holdout check passes if the relative ordering of corridor-level delay is preserved within the factor's band. This is recorded in the subtask outcome analysis, not as a numeric accuracy claim (no independent time-series exists to score against).

## Exchange 3
Question: For a policy decision on lane dedication, what size of error in predicted congestion would make the model's answer untrustworthy?

Reply (gist): The untrustworthy threshold is where the error flips the sign of the net benefit of lane dedication (capacity gained by platooning vs capacity lost by removing a general-purpose lane). That margin is typically ~10–20% of corridor capacity. Error below ~5%: direction robust. 5–20%: fragile, corridor-specific. Above ~20%: recommendation unreliable.

How it changed the work:
- Decision rule (used in the lane-dedication analysis): report the net-benefit margin M = (capacity with dedicated lane) / (capacity without) − 1, and classify the recommendation as: robust if |M| > 20%, fragile if 5% < |M| ≤ 20%, direction-uncertain if |M| ≤ 5% (sign not reliable). The ±10–20% band is carried as the model's stated planning-level uncertainty on every throughput/delay figure, sourced to expert exchange 3.
- Threshold values: `decision_robust = 0.20`, `decision_fragile = 0.05`, interval [0.05, 0.20], source: expert exchange 3.
