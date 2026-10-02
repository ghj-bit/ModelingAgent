# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — Problem 2017_C (self-driving cars and highway capacity)

Three expert exchanges, one question each. Each reply is converted below into a
concrete parameter or constraint in `code/traffic_model.py`; the value, its
source (this exchange), and the interval over which it holds are recorded. The
replies are input to the model, not content — nothing here is copied verbatim
into `solution.json`.

## Exchange 1 — Data provenance / representativeness of the daily counts

**Question (paraphrase).** The 2015 daily-traffic counts vary 2-3x from one
segment to the next on the same highway. Are those differences mostly real
differences in how busy each section is, or partly differences in how the
counts were measured?

**Expert reply (summary).** Mostly real: volumes genuinely swing along a
corridor (urban core >> outer segments, steps at interchanges/river crossings),
and the pattern is stable year to year. There is a secondary measurement
component: counts mix permanent continuous counters, short-duration counts
expanded to a daily average, and some carried-forward estimates, giving a
segment-to-segment scatter of roughly ±10-30% (plus directional/seasonal
expansion error). The 2-3x spread is dominated by real demand.

**How it became work (parameter + interval).**
- Model input `D_s` = the supplied 2015 average daily traffic for segment *s*
  is treated as the representative mean of a real, stable demand distribution.
- **Measurement-uncertainty band: ±15% central, up to ±30% outer**, on each
  segment's daily volume. Propagated through the peak-hour and capacity steps
  into an uncertainty band on the volume-to-capacity ratio `V/C`. Because the
  dominant term is real demand (not measurement), the band is used only to
  classify *borderline* segments (those within the band of the 85% threshold),
  not to doubt the overall congestion ranking.
- Source: Exchange 1. Holds for: all 224 segments, 2015 AADT figures.

## Exchange 2 — The key structural assumption (steady state vs peak hour)

**Question (paraphrase).** Is it fair to compare each road's usual daily traffic
directly to how many cars its lanes can carry, or is rush-hour traffic so far
above the daily average that real jams come from short peak surges?

**Expert reply (summary).** Not fair to compare daily volume to a 24-hour
capacity. The daily count is a 24-hour average; capacity is a per-hour rate. On
urban freeways the peak hour carries roughly **8-12% of the daily total**, and
the peak-direction hour can be higher. A segment whose daily volume looks
comfortably below "lanes x hourly capacity x 24" can still be over capacity for
one to two hours each morning and evening. Jams are driven by those short peak
surges. Consequence: compare **peak-hour demand (a peak-hour factor on the
daily count) against hourly lane capacity**, not daily vs daily; using the
daily average systematically understates congestion and the benefit of any
intervention.

**How it became work (equation change).**
- This is the load-bearing assumption. The model's core ratio is **not**
  `D_s / (24 * lanes * c)` (which would understate congestion). Instead:
  `V_peak,s = PHF * D_s / N_s`  (peak-hour demand per lane),
  `V/C = V_peak,s / c`, where `c` = free-flow capacity per lane (pc/h) and
  `N_s` = lanes in the peak direction.
- `PHF` (peak-hour factor = peak-hour volume / daily volume) is set to a **base
  of 0.11** with a sensitivity interval **[0.08, 0.12]**, exactly the
  expert's stated 8-12% (the upper end also covers the "peak direction hour can
  be higher" note). The model is swept over this interval and the results are
  reported as a band.
- Source: Exchange 2. Holds for: the 24-hour daily counts in the dataset and
  peak-hour freeway demand.
- This is also the answer to "do equilibria / a tipping point exist": congestion
  is governed by the peak-hour V/C, and the model's tipping point is the
  self-driving penetration at which the *effective* peak-hour V/C crosses the
  85% breakdown threshold — not a daily-traffic crossing.

## Exchange 3 — Decision-relevant threshold / risk tolerance

**Question (paraphrase).** How close does traffic get to a lane's full carrying
ability before you'd say it is genuinely too crowded and needs real action,
versus just being a bit slow on a bad day?

**Expert reply (summary).** Practical freeway-lane carrying ability is about
2,000 pc/h (roughly 1,800-2,300 by condition). Bands: below ~70% of capacity
(normal flow), ~70-85% (unstable, watch), above ~85-90% (flow breaks down,
stop-and-go, disproportionate delay — real action warranted). Working threshold
= **~85% of hourly lane capacity in the peak hour**.

**How it became work (thresholds + decision rule).**
- **Decision threshold V/C* = 0.85** (a segment "needs action" when its
  peak-hour V/C >= 0.85). Secondary bands used for classification: 0.70
  (unstable/watch) and 0.90 (severe/breakdown).
- **Free-flow capacity per lane c = 2,000 pc/h**, interval **[1,800, 2,300]**
  (the expert's condition-dependent range). The self-driving capacity-boost
  model is calibrated so that at the low end of the self-driving share it
  reproduces the observed 2,000 pc/h baseline, and swept over [1,800, 2,300]
  for the "does it change the policy" question.
- Source: Exchange 3. Holds for: freeway/limited-access segments in peak hour.

## Net effect on the model
The three replies jointly fix the model's operating point: use **peak-hour**
demand (Exchange 2, PHF in [0.08,0.12] on the daily counts), compare it to
**hourly per-lane** capacity (Exchange 3, c = 2,000 pc/h in [1,800,2,300]), flag
**V/C >= 0.85** as the action threshold (Exchange 3), and carry a **±15-30%**
volume-uncertainty band (Exchange 1) only to flag borderline segments. The
self-driving cooperative-capacity gain is then the one additional, literature-
sourced term (search.py), added on top of this expert-fixed baseline.
