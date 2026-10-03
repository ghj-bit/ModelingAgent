# Interaction Evidence — Task 2024_D (Great Lakes water-level control)

Ten expert exchanges, one question each. All questions in `logs/operator_feedback/expert_question_N.md`, replies in `expert_reply_N.json` (via `expert_request_N.json`). Each reply below is recorded with the concrete model element it produced; the expert's prose is not carried into the submission.

## E1 — Who suffers most at low water levels?
- Q: at dangerously low levels, which stakeholder suffers most — shippers, shore towns, power plants?
- Reply (gist): shippers; light-loading or halted transits are an immediate hard loss. Shore towns actually benefit (less flooding/erosion); hydropower loss is partial/gradual (head/efficiency only).
- Effect on model: stakeholder cost structure for Lake Ontario (Task 1/5).
  - `C_ship = c_s · max(0, D_req − D_eff)` where effective draft `D_eff` is the controlling clearance at the minimum level reached (low-level binding constraint; ships cannot run without clearance, so the loss is a hard step, not a slope).
  - Shoreline cost only for high levels: `C_flood = c_f · max(0, h − h_flood)`. No shoreline cost below the band.
  - Hydropower: small quadratic in deviation from a comfortable head, weight one order of magnitude below shipping at equal normalized distance.
- Interval/validity: applied to the operating band derived from 2000–2020 Lake Ontario data.

## E2 — Are shippers compensated for running light?
- Q: are ship operators paid/penalized for shallow-draft runs, or do they just carry less?
- Reply (gist): no compensation; loss is reduced cargo per trip and higher unit cost; contracts may impose deadfreight for shortfall.
- Effect on model: loss is proportional to foregone tonnage per transit, i.e. linear in the deficit of usable draft; no fixed penalty term. `C_ship` as above, linear in `max(0, D_req − D_eff)`.

## E3 — Operator response when a lake is near the top of range?
- Q: what do operators do to outflow when a lake sits near the top of its range?
- Reply (gist): increase outflow to draw the level back down; the response is "release more, up to the downstream limit" — not unlimited drawdown.
- Effect on model: the control law is band-tracking with one-sided release: `Q_out(t) = clamp(Q_base + K·(h − h̄), Q_min, Q_cap)` where `h̄` is the band center and `Q_cap` is the downstream-limited release cap (next exchange). The algorithm is a proportional (P) controller on lake height error, actuated on the dam release only.

## E4 — How binding is the downstream flooding cap?
- Q: does the downstream-flooding concern actually stop much, or is it a rare worry?
- Reply (gist): real and frequently binding; it caps releases rather than stopping them; the two structures sit in series, and Lake Ontario's outflow is limited by Montreal-harbor conditions, so Ontario can be held above target precisely because more release is forbidden.
- Effect on model: explicit hard constraint `Q_out(t) ≤ Q_cap(t)` in the control problem; `Q_cap` varies with the downstream state (St. Lawrence level proxy) and is binding in wet periods. This is the key structural constraint distinguishing the model from a free-release optimizer.

## E5 — Priority during a spring surge?
- Q: during a spring snowmelt surge, which matters more — drawing the lake down fast, or not flooding the river below?
- Reply (gist): downstream flood protection binds; the upstream lake is slower and partially self-correcting, so its drawdown is the secondary objective, pursued only up to the downstream limit.
- Effect on model: lexicographic objective — (1) never exceed the downstream release cap, (2) keep lake height inside the band. In surge months (Apr–May, the data show the Ottawa River peak at 2–3× its mean), the release cap is tightened: `Q_cap(t) = Q_cap0 · min(1, (h_down,band_top − h_down)/Δh_down + 1)`, i.e. the cap falls as the downstream lake/river rises toward its own band top.

## E6 — Consequence of an over-forecast surge?
- Q: if a forecast overestimates a surge and operators hold back water, what happens?
- Reply (gist): the upstream lake stays elevated / misses its drawdown; downstream towns see lower-than-expected flow (the feared flood does not materialize). The error is shifted upstream and is recoverable later, but the lake can sit high for weeks if wet conditions continue.
- Effect on model: motivates the asymmetric risk weights — holding back (over-release of caution) is the conservative, recoverable error, so the controller may prefer to hold when forecast error is large in wet seasons; also motivates the "missed drawdown compounds" term: cost of being above band grows with duration above the band (`C_above += c_a · max(0, h − h̄_top) · T_above`), which is the mechanism that makes a weeks-long high-water spell expensive.

## E7 — Effect of ice jams?
- Q: what do ice jams on the St. Lawrence do to river flow and upstream level?
- Reply (gist): a jam is a physical blockage — it constrains the channel, backs water up upstream (local flooding), throttles conveyance, and downstream flow can drop then surge on release. Winter conveyance is therefore reduced and less predictable; the downstream limit tightens in winter.
- Effect on model: seasonal conveyance factor in the St. Lawrence reach: `C_conv(t) = C0 · (1 − β_ice · I_ice(t))` with `I_ice` active Dec–Mar. The release cap for Lake Ontario during winter is multiplied by `C_conv`, so the same outflow sets a higher backwater level; the model's winter sensitivity analysis perturbs `β_ice`.

## E8 — Frequency and direction of forecast error?
- Q: how often are water-level forecasts off enough to matter, and which direction do they err?
- Reply (gist): consequential errors are a routine occurrence, not rare; roughly symmetric overall, but the *damaging* tail is skewed toward overestimates of incoming water in spring (they cause holding back and a high lake); underestimates cause over-release but are caught and corrected faster.
- Effect on model: the 2017 backtest uses a perturbed-inflow Monte Carlo with error distribution matched to that description: Gaussian on log-inflow with σ ≈ 0.15 for base months, and a one-sided skew in Apr–May (mean shift +0.10σ toward over-forecast, i.e. the over-estimate tail is fatter). The controller's robustness is measured as % of runs staying inside band vs. the actual 2017 policy.

## E9 — Confidence in the annual plan?
- Q: how confident are operators in sticking to their planned annual water level?
- Reply (gist): the "plan" is a target band (order tens of cm to a meter wide), routinely revised, hit with moderate confidence at best; they expect to miss it in wet springs and to be cap-constrained in other seasons.
- Effect on model: the band for Lake Ontario is set from the data (see Task 5): monthly band center = seasonal mean of 2000–2020; half-width ≈ 0.5 m (upper end of the expert's stated tens-of-cm-to-meter range, chosen because the problem states 2–3 ft ≈ 0.6–0.9 m deviations are the consequential ones, so the band is set so that a typical seasonal swing fits and a 0.6 m+ excursion is an event). The success metric for the 2017 comparison is "fraction of months with |h − h̄| inside the band", with the band taken as [h̄ − 0.5, h̄ + 0.5] m.

## E10 — Which lake is blamed on the dam for weather-driven problems?
- Q: which of the five lakes is most often blamed on dam releases for problems that are really weather-driven?
- Reply (gist): Lake Ontario — it is the only one with a visible named lever (Moses-Saunders at Cornwall), it has the most active shoreline-stakeholder controversy, and the Montreal flood constraint often forces holding water against Ontario's own target; the other four have no comparable single control structure at their outlet.
- Effect on model: confirms the problem's own emphasis (consideration 5) and the attribution split the model must make: for Lake Ontario, decompose 2017 level deviation into (a) the part the release could have removed (cap not binding) and (b) the part forced by inflow/Ottawa + the Montreal cap (cap binding). Result feeds the memo's honesty point: a control algorithm can only own the (a) share.
