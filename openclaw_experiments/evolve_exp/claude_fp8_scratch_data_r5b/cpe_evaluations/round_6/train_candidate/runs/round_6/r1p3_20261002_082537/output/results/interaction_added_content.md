# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — Problem 2017_C

Three exchanges, one question each, in `logs/operator_feedback/expert_question_{1,2,3}.md`
with replies in `expert_reply_{1,2,3}.json`. Each reply was converted into a model
parameter or decision rule before the next exchange; the affected work is noted.

## Exchange 1 — selection mechanism in the data
- **Question:** *On these Washington highways, do the daily traffic counts represent one
  typical weekday, or do they include the special surges of Friday and holiday weekends?*
- **Reply (summary):** The "Average daily traffic counts Year_2015" column is an annual /
  seasonal average (AADT-style): total traffic over a period divided by number of days. It
  deliberately smooths day-to-day variation, so it does **not** capture Friday-afternoon or
  holiday-weekend surges. It is appropriate for average/typical-day capacity analysis but
  under-
states peak-hour and peak-day demand; peak conditions need a peak-hour factor applied to
  the averages.
- **Turned into work:** The model does **not** treat ADT as the worst case. Peak-hour
  directional demand is derived as `d = ADT × PEAK_SHARE × DIR_SPLIT` with
  `PEAK_SHARE = 0.12` (share of the day's volume in the peak hour) and `DIR_SPLIT = 0.5`.
  Both are CLI parameters in `code/model.py` and both appear in the solution.json
  parameter table with their intervals. The bias note that the yearly average understates
  peak demand is carried into the solution's limitations.

## Exchange 2 — temporal / state-dependence structure
- **Question:** *Since the counts are yearly averages, do these Seattle freeways jam at
  rush hour every single weekday, or only on a few bad days each week?*
- **Reply (summary):** Every weekday, not just a few bad days. These corridors are
  chronically over capacity in the peak direction during the weekday commute; recurring
  peak-hour demand routinely exceeds design capacity, so congestion is a near-daily,
  structural condition (two peaks, worse Fridays/holidays). A high annual average is
  itself evidence of heavy loading most days.
- **Turned into work:** Justifies a **steady-state (equilibrium)** supply-demand model
  rather than a transient dynamics model. The model computes a fixed VCR = demand/capacity
  per segment and a corridor equilibrium at which throughput saturates at capacity. The
  baseline result (mean VCR ≈ 3.0, 98% of segments at/over capacity) is the structural
  congested equilibrium the expert described. This is stated in `task_analysis`
  (steady-state choice) and `subtask_outcome_analysis` (equilibria: yes).

## Exchange 3 — bias-aware interpretation threshold for lane dedication
- **Question:** *If a lane set aside for driverless cars could only hold a few more cars
  than before, would you still set it aside for them?*
- **Reply (summary):** No, not on that basis alone. A dedicated lane is justified only if
  the capacity it adds for the automated fleet **exceeds** the capacity it removes from
  general traffic. A few extra cars in the dedicated lane against a whole lane's worth of
  displaced human traffic is a net loss. Dedication makes sense only when the automated
  lane's throughput gain is large enough to offset the capacity everyone else loses —
  i.e. high enough SD share and strong cooperation benefit. At low penetration or weak
  gains, do not dedicate.
- **Turned into work:** The dedicated-lane decision rule in `code/model.py::dedicate()` is
  exactly this net-benefit test: `net = T(p, n_ded) − T(p, 0)` summed over all segments and
  both directions; dedicate iff `net > 0`. The model's `--dedicate` and `--tipping` runs
  implement the rule, and the results (net gain ≈ +30,000 veh/h ≈ 2.4% of baseline at
  10% SD, largest at low penetration, → 0 at p=1) feed the solution's dedicated-lane and
  policy recommendations. The "a few more cars is a net loss" case is the decision
  threshold the rule encodes.

## Note on reply use
No expert sentence, phrasing, or structure was copied into `solution.json`. Only the
values, constraints, equations, and the decision rule were carried over, in the model's own
formulation (peak-share/directional-split derivation, steady-state VCR, net-benefit
dedication test).
