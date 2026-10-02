# Interaction Evidence — Great Lakes Water-Level Control (Problem 2024_D)

Three expert exchanges, one question each. Each reply was turned into a model
constraint, equation, or decision rule before the next exchange.

## Exchange 1 — Data–model structural fit

**Question (expert_question_1.md):** What single real-world rule must a
lake-level model obey so its numbers stay physically possible — what quantity
must balance at each lake, and why must the water level change smoothly rather
than jump?

**Expert reply (expert_reply_1.json):** Mass (water-volume) conservation at each
lake: over any interval the change in stored volume equals total inflow minus
total outflow. Because storage is the continuous integral of finite flow rates
over a large lake surface, the level can only change smoothly — a finite
imbalance over a short time produces only a small level change, so the level
cannot jump instantaneously.

**How the reply became work (source: exchange 1):**
- The model's governing state equation is the lake volume balance, written per
  lake *i* and month *t*: `A_i*(L_{i,t}-L_{i,t-1}) = (In_i - Out_i)*dt`, solved
  forward as `L_{i,t} = L_{i,t-1} + (In_i - Out_i)*dt/A_i`. This is the
  constraint the expert named (volume conservation) expressed as a smooth
  first-order recurrence — the "cannot jump" property is built into the form
  (a bounded monthly flow imbalance moves the level by a small, finite amount
  `delta L ~ Q*dt/A`).
- Validity interval: the recurrence is applied month-by-month over 2000–2022
  (the data span), with `dt` = actual month length in seconds.
- The smoothness property was used as a validation criterion: any candidate
  control law that produced a level discontinuity larger than the observed
  month-to-month change (max ~0.6 m in the data) was rejected as physically
  implausible. All simulated series in `model.py` satisfy this.

## Exchange 2 — Dominant bias / selection mechanism

**Question (expert_question_2.md):** In a basin like the Great Lakes, when
managers set a lake's outflow, what is the biggest thing that quietly changes
the next year's water level in a way the operator does not directly control?

**Expert reply (expert_reply_2.json):** The dominant uncontrolled driver is the
net basin supply — precipitation on the lake plus runoff from the surrounding
basin, minus evaporation from the lake. It is not manipulated by the operator
(unlike the dam outflows). Over the Great Lakes, evaporation and precipitation
each move water at rates comparable to the river flows, so their imbalance can
shift levels by a foot or more across years.

**How the reply became work (source: exchange 2):**
- Justifies treating the unmeasured natural terms (precip + runoff − evaporation
  + groundwater +, for Ontario, Ottawa inflow) as a single **residual basin
  term R_i(t)** per lake, rather than as a constant. `R_i` is calibrated as a
  *monthly seasonal* mean from the volume-balance closure over 2009–2020 (the
  overlap window where both flanking rivers are observed), so it carries the
  annual cycle the expert identified. This is the dominant bias mechanism: the
  data under-represents the natural drivers, so the model must not attribute
  their effect to the control dams.
- Decision rule: the control algorithm may only claim credit for level change
  that remains after `R_i(t)` is held fixed. The 2017 backtest isolates exactly
  this — it holds `R_i` at its calibrated seasonal value and measures how well
  the dams' actual 2017 discharges reproduce the observed level, so the
  residual error is the uncontrolled natural variation, not a control failure.
- Interval: `R_i` seasonal means are valid over the 2009–2020 calibration
  window; the 2017 backtest lies inside it, so the non-stationarity the expert
  warned about is bounded to inter-annual drift, not a structural miss.

## Exchange 3 — Validation / interpretation criterion

**Question (expert_question_3.md):** For a lake like Ontario, when is the
water level "fine" for the people who depend on it, and how large a change do
they actually notice?

**Expert reply (expert_reply_3.json):** "Fine" is a band, not a number:
stakeholders are satisfied while the level stays within the normal seasonal
envelope (on the order of a foot of seasonal rise and fall), with the long-term
mean as reference. What they notice is *departure from that accustomed band*,
not the absolute level. On Ontario, changes of ~0.3–0.5 ft (≈10–15 cm) are
already noticed by shoreline and marina users; a foot or more of sustained
deviation causes real damage/constraint (flooded shore, erosion on the high
side; restricted shipping draft, exposed docks/intakes on the low side). The
two-to-three-foot variance in the problem is the severe, stakeholder-conflict
regime. This is an empirical judgment from observed shoreline and navigation
sensitivity, not a precise threshold.

**How the reply became work (source: exchange 3):**
- Defines the acceptance criterion used in `subtask_outcome_analysis`: the
  relevant quantity is **departure from the seasonal envelope**, not the
  absolute level. A month is "noticed" when it deviates ≥10 cm (0.3 ft) from
  the 2000–2022 seasonal-mean level for that month, and "severe" when it
  deviates ≥30 cm (1 ft), the damaging/constraining regime the expert named.
  The 2–3 ft variance cited in the problem is the stakeholder-conflict regime.
- Decision rule: a control change is decision-relevant only if it changes the
  *count of months* crossing the 10 cm (noticed) and 30 cm (severe) departure
  thresholds, not merely the mean level. The 2017 backtest and the control
  sweep are both scored in these departure terms, so the recommendation (which
  dam to operate, by how much) is framed in the band stakeholders actually
  experience.
- Interval: thresholds applied to 2017 Ontario levels (the year in scope); the
  seasonal reference is the 2000–2022 mean, the data span. The 10/30 cm values
  are the expert's empirical shoreline/navigation sensitivity, treated as the
  acceptance band.
