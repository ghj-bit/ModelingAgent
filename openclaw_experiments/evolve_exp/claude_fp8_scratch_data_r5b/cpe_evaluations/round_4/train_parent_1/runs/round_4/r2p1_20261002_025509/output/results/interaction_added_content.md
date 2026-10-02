# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — Great Lakes (2024_D)

Three fixed exchanges. Each reply was converted into a concrete model
parameter, constraint, or decision rule before the next exchange.

## Exchange 1 — data-model structural fit

**Question.** "In practice, how does a lake's water level change over a month
relate to how much water flows in versus out?"

**Reply (summary).** Over a month, the level change is the net water balance
divided by the lake's surface area:
`Δlevel ≈ (inflow − outflow + precipitation − evaporation) / area × dt`.
Because the lakes are enormous, large imbalances produce small level changes
(area-damped). Level responds with a lag because outflow is head-driven
(level-dependent), giving the system memory. So month-to-month level change is
a smoothed, area-damped *integral* of net inflow, not a direct proportional
readout of the gauged flows.

**How it changed the work.** This fixed the model *form*: a volume-balance
equation `dL = g·(Qout − Qin) + C` with `g = dt/A` (area-damped gain), not a
direct `level ↔ flow` regression. I tested a direct OLS `dLevel ~ flow` and it
failed (R² = 0.03–0.28 across the five lakes), exactly as the "integral, not a
readout" warning predicted. The physical gain was set to `g = dt/A`
(1.405e-4 m per m³/s per month for Ontario, A = 1.8721e10 m²). The head-driven
lag justified treating the controlled outflow as the IJC's lever on the level,
not as a cause of the seasonal swing.

## Exchange 2 — dominant bias mechanism

**Question.** "In the Great Lakes data, what is the main reason a lake's level
can rise or fall even though the recorded river flows barely changed?"

**Reply (summary).** The recorded river flows are only part of the balance. The
two largest non-river terms — precipitation directly on the lake and
evaporation from it, plus other ungauged fluxes (groundwater, runoff,
diversions) — are not in the flow records at all, and over a month can be
comparable to or larger than the river terms. The huge surface area damps and
integrates the imbalance, and head-driven outflow lags the level, so the level
moves mainly because these ungauged fluxes shift the balance, not because the
gauged flows changed.

**How it changed the work.** This justified the model's residual term `C`
(seasonal climatology of the net ungauged flux) as the *dominant* predictable
signal, with the gauged outflow as a secondary, controllable correction. It
also motivated the sensitivity analysis to environmental conditions (the
ungauged P/E/runoff are precisely the environmental terms). The model was
therefore structured as: level = seasonal shape (ungauged residual) + dam
adjustment (gauged outflow), with the residual carrying the seasonality.

## Exchange 3 — validation / interpretation criterion

**Question.** "When comparing a new lake-level control plan to last year's
actual water levels, what difference counts as good enough that the plan
genuinely helps the people who rely on the lake?"

**Reply (summary).** There is no single universal number; it is
stakeholder-specific and seasonal. A plan helps only if it (a) moves the level
in the right direction for the affected stakeholder, (b) at the right time of
year, and (c) by at least a few centimeters to ~0.3 m in the sensitive season.
Shoreline/flood interests care about shaving high-water peaks; navigation cares
about keeping levels above draft depth in low-water periods; ecosystem
interests care about preserving the seasonal swing, not flattening it. A plan
that helps one group while harming another, or that shifts levels by only a
centimeter or two year-round, does not genuinely help.

**How it changed the work.** This set the 2017 backtest's interpretation
lens: I evaluate the model *by stakeholder and season*, not by a single global
error. Concretely I report (i) the high-water window (May–Jul 2017, levels
>75.5 m, peak 75.81 m) for shoreline/flood, (ii) the low-water window for
navigation (none in 2017 — the lake never dropped below 74.6 m), and (iii) the
preserved seasonal range (1.19 m) for ecosystem. The "right direction, right
time, ≥ a few cm in the sensitive season" rule is the pass criterion for any
proposed control change.
