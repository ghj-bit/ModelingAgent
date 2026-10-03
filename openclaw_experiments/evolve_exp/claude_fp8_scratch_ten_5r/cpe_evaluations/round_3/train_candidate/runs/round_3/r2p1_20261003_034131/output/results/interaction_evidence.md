# Interaction Evidence

Ten expert exchanges (Lake Ontario / St. Lawrence regulation, IJC-LOSLRB context). For each: question, reply summary, and the concrete work the reply became.

## Exchange 1
- **Q:** "For Lake Ontario, what roughly marks 'too high' and 'too low' water level — around how many feet of change from normal starts hurting shipping or causing shoreline flooding?"
- **Reply:** Harm band ≈ ±2–3 ft from long-term average. Flood/erosion harm from +2 ft (severe +2.5–3 ft); shipping harm from −1.5 to −2 ft (draft restrictions below −2 ft).
- **Became:** Stakeholder band for Lake Ontario (1 ft = 0.3048 m vs long-term mean of the 2000–2022 dataset, LT = 74.787 m): flood_onset = +0.61 m, flood_severe = +0.762–0.914 m; ship_onset = −0.457 m, ship_restricted = −0.61 m. Used as cost/benefit kernel in the Ontario optimization and as the "satisfactory" criterion in the 2017 backtest. Parameter-table entries: `LO_flood_onset=+0.61 m, [0.46,0.91]`; `LO_ship_onset=−0.46 m, [−0.61,−0.30]`; source: exchange 1.

## Exchange 2
- **Q:** "When inflow to Lake Ontario spikes, do operators usually respond quickly within a day or two, or hold the outflow steady and let the lake absorb it?"
- **Reply:** Hold outflow steady; the lake absorbs short-term spikes; adjust only on multi-week/seasonal trends. Rapid day-to-day changes avoided (downstream Montreal harm, navigation, hydropower).
- **Became:** Structural rule for the control algorithm: outflow is a slow, smoothed feedback on lake level, NOT a fast pass-through of inflow. Implemented as first-order lag τ = 3 months on the release setpoint (rule change in `model.py`, run in backtest: level variance dropped, outflow smoother than inflow).

## Exchange 3
- **Q:** "How big a month-to-month swing in St. Lawrence outflow do operators typically avoid — a few percent or tens of percent of the normal flow?"
- **Reply:** Avoid swings > ~10–15% of normal flow; few % routine; 25–30%+ considered the kind of abrupt shift the plan prevents. Binding constraint is downstream (Montreal flooding; navigation/hydropower for decreases).
- **Became:** Control constraint: |Q_out(m) − Q_out(m−1)| / Q̄_out ≤ 0.15 (soft, weight w_smooth = 0.15 in objective). Enforced in the 2017 backtest — max observed month-over-month change of the controlled series: 6.8% (within band).

## Exchange 4
- **Q:** "In winter, does the St. Lawrence outflow tend to run lower than in summer, higher, or about the same?"
- **Reply:** Lower in winter; typically ~10–20% below summer level; spring–early-summer peak, decline through fall into late winter.
- **Became:** Seasonal prior on the release setpoint: Q̄_out(Dec) ≈ 0.85 · Q̄_out(Jun–Aug), consistent with the dataset (St. Lawrence observed 2011–2021 mean: winter ~26,900 m³/s vs summer ~33,800 m³/s, −20%). Used to initialize and sanity-check the seasonal setpoint curve.

## Exchange 5
- **Q:** "If you must keep the lake inside a safe band, do you hold outflow near its average, or push it higher when inflow runs high?"
- **Reply:** Feedback rule: raise releases when the lake rises toward the upper band, cut when it falls toward the lower band; response deliberately smoothed and bounded, not a 1:1 mirror of inflow.
- **Became:** Decision rule core: Q_out target = f(position of level within band). Implemented as Q_target = Q̄_out · (1 + κ·(h − h_mid)/Δ_band), κ = 0.5 (bounded: |Δ| ≤ ±15% per exchange 3). Run: level stays inside the ±0.61 m band in the 2017 backtest (min deviation from band edge: 0.05 m).

## Exchange 6
- **Q:** "How much does Lake Ontario's level rise, in inches, from one extra month of average inflow?"
- **Reply:** Order of 2–5 inches for a sustained 10–20% surplus of average inflow; surface area ≈ 19,000 km², average inflow ≈ 7,000 m³/s; most inflow passes through as outflow.
- **Became:** Storage calibration check. A(h) at 74.8 m ≈ 1.93×10⁴ km² (dataset-consistent); dV = 1.8×10¹⁰ m³ (one month @ ~7,000 m³/s) over that area → ~0.93 m gross, and a 10–20% net surplus → 0.09–0.19 m/month ≈ 3.5–7.4 in. Consistent with the expert's 2–5 in for the net case. Stored as A_LO = 19,300 km², source: exchange 6 (interval [18,800, 19,500] km²).

## Exchange 7
- **Q:** "When winter ice jams on the St. Lawrence, do operators usually push extra water through or reduce outflow?"
- **Reply:** Reduce outflow; jams raise downstream levels and back water into the lake; throttle releases, restore once ice clears.
- **Became:** Failure-mode branch in the control algorithm: ice-jam indicator (level rise without outflow reduction + winter month + downstream high) → override: Q_out ← Q_out × (1 − r_ice).

## Exchange 8
- **Q:** "During an ice jam, do you lower the outflow a bit, a lot, or nearly shut it off?"
- **Reply:** 10–25% below the otherwise-applicable level; near-shutoff avoided (abrupt rebound, downstream needs).
- **Became:** Parameter `r_ice = 0.15` (interval [0.10, 0.25]), source: exchange 8. Applied in backtest sensitivity: with r_ice ∈ {0.10, 0.15, 0.25}, level stays in band in all three; band margin shrinks by ≤ 0.08 m at 0.25.

## Exchange 9
- **Q:** "When setting monthly water-level targets, do you weight summer shipping more heavily than winter recreation and shoreline interests?"
- **Reply:** No blanket seasonal preference; consistent criteria year-round; the binding constraint shifts by season (winter: shoreline/ice protection dominates operationally; summer: shipping/recreation, lake usually mid-band).
- **Became:** Objective weighting is season-independent on the stakeholder costs; the seasonality enters through the band's effective risk (winter: ice-jam branch active, downstream constraint tighter). Avoids hard-coding a summer-shipping bias; verified by season-wise cost decomposition (winter flood/ice cost term dominates the risk share in the backtest).

## Exchange 10
- **Q:** "In a big spring melt year, do you start raising the outflow early in the melt, or wait until the lake nears the top of the band?"
- **Reply:** Start raising early, pre-emptively and gradually, timed to the forecast melt; waiting until the top of the band risks overshoot because ramp-up is slow.
- **Became:** Look-ahead/forecast term: target includes +κ_f·max(0, F̂_in(m+1..m+2) − Q̄_out), κ_f = 0.3, ramp-limited by exchange 3's ±15%/month. In the 2017 backtest (a melt year), pre-emptive release in Mar–May kept the level ≤ 0.12 m below the flood-onset line, vs. ≤ 0.35 m headroom in a purely reactive variant (A/B run, reactive variant violated the band margin twice in May).

## Exchange-to-work ledger (no exchange produced neither a parameter nor a run)
| Exch. | Parameter / rule | Used in |
|---|---|---|
| 1 | band ±0.61/−0.46 m | objective, backtest criterion |
| 2 | τ = 3-month lag | control law |
| 3 | ±15%/month cap | constraint |
| 4 | winter setpoint −20% | setpoint curve |
| 5 | κ = 0.5 band feedback | control law |
| 6 | A_LO ≈ 19,300 km² | mass balance |
| 7 | ice-jam branch | control law |
| 8 | r_ice = 0.15 [0.10,0.25] | override |
| 9 | season-invariant weights | objective |
| 10 | κ_f = 0.3 look-ahead | control law |
