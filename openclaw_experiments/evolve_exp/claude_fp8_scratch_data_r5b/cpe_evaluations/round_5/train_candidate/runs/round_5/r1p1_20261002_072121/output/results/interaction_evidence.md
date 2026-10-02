# Interaction Evidence

Three expert exchanges, one question each, in order. Each reply is turned into a
named parameter or constraint of the model (value, interval, source = the
exchange, and the interval over which it holds). The reply text is input only;
the model carries the value/constraint, not the phrasing.

## Exchange 1 — causal mechanism / data-model consistency

**Question (asked before building the state equation):** Whether a lake level
follows a change in dam outflow almost immediately, or stays put and only moves
after weeks or months of a sustained change.

**Reply (summary):** A lake is a large storage reservoir; a sustained change of
a few hundred to a few thousand m³/s moves the level only centimetres per week,
and full adjustment takes weeks to a season or more. The immediate effect is
felt downstream in the river, not in the lake level.

**How it changed the work:**
- Established the model structure: a first-order storage (mass-balance)
  integrator, `A_k · dL_k/dt = In_k − Out_k`, integrated month by month — NOT an
  instantaneous level = f(flow) response. This is the core equation in
  `mathematical_modeling_process` and the `reapply()` step in `code/model.py`.
- Consequence: the control variables are sustained releases, and a one-month
  outflow change does not by itself move the level — the model integrates it.
- Parameter: response is integrating (lag on the order of weeks–a season); the
  month-by-month `reapply()` loop is the discrete form of this.

## Exchange 2 — operational constraints / boundary conditions

**Question (builds on Ex. 1's slow response):** Roughly how far can a lake level
move before things get genuinely bad — flooding the shore if too high, or
blocking ships if too low.

**Reply (summary):** The practically meaningful "genuinely bad" band is on the
order of 1–2 feet, i.e. roughly 0.3–0.6 m, about the long-term average, in each
direction (flooding high, navigation restriction low). Empirical, not a precise
threshold.

**How it changed the work:**
- Parameter: `GOOD_BAND = 0.40 m`, the half-width of the acceptable operating
  band, interval [0.30, 0.60] m, source = Exchange 2.
- This becomes the constraint/target of the "optimal water level" algorithm: the
  control objective keeps each month's level within ±0.40 m of the lake's
  long-term monthly mean, and the `in_band` result (months inside the band) is
  the reported success metric. It holds for the Great Lakes as a class, about the
  long-term monthly average.

## Exchange 3 — decision-relevant uncertainty threshold

**Question (builds on Ex. 1–2's narrow band):** How big must a prediction error
be before it changes a management decision, versus an error small enough to
ignore for planning.

**Reply (summary):** Below ~0.1 m (a few inches) ignore for planning; ~0.1–0.15 m
is borderline (matters only for the most sensitive stakeholders); above
~0.15–0.3 m it is decision-changing because the whole "bad" band is only 1–2 ft.

**How it changed the work:**
- Parameter: `DEC_ERR = 0.12 m`, the decision-relevant error threshold, interval
  [0.10, 0.15] m, source = Exchange 3.
- Used to interpret the model's accuracy: a prediction error under ~0.1 m is
  planning-adequate; results are reported against this. The model's closure RMSE
  (~0.13 m/month, see balance output) sits at the borderline, which is why the
  submission frames the level predictions as planning-level and the in-band
  (Ex. 2) count as the decision metric rather than raw level error.
