# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — 2018_C (four-state energy compact)

Three fixed expert exchanges. Each reply became a concrete constraint or
equation in `code/analysis.py`, not prose. The expert was asked only common-sense
questions about the real-world behavior of these states' energy history; no model
structure or notation was put to them.

## Exchange 1 — Structural validity: steady trend vs. lumpy history
**Question (expert_question_1.md):** For these four states, did the shift toward
cleaner, renewable energy move steadily over the decades, or in lumps tied to
one-off events like oil-price spikes?

**Reply (summarized, verbatim kept in expert_reply_1.json):** The history is
*lumpy, not steady* — renewable/cleaner shares moved in steps tied to
identifiable events (big-hydro build-out, 1973/79 oil shocks, PURPA 1978 and
California's RPS, nuclear units coming online in AZ/TX, TX wind taking off only
in the late 1990s–2000s). A single smooth curve fitted over 1960–2009
misrepresents both level and direction; extrapolating it to 2025/2050 is
unreliable. This is an empirical judgment.

**How it became work:** Rejected a single 50-year smooth trend/logit of the
renewable share as the forecast. The model instead (a) weights recent years
heavily (recency weights `lambda^(2009-t)`) and (b) projects each renewable
*component* (hydro, wind, solar, geothermal, biomass) separately, capping each
at a resource ceiling so a one-off step (e.g. TX wind, +3793% 2000→2009) is not
extrapolated to absurdity. The "absent any policy change" central case is the
conservative end of this. Implemented in `forecast()` / `wloglin()` in
`code/analysis.py`.

## Exchange 2 — Bias mechanism: what actually drives the number
**Question (expert_question_2.md):** If a governor is deciding how much
renewable energy to require by 2025, does the size of that number depend more
on how much total energy the state will still use (barely growing), or on how
many new renewable plants actually get built? Which one really moves the needle?

**Reply (summarized, verbatim in expert_reply_2.json):** The renewable *share*
is renewable output divided by total energy use. With the denominator (total
energy use) roughly flat, the share is driven almost entirely by the numerator —
new renewable capacity and generation. Demand-side changes (efficiency, slower
growth) are second-order; the binding lever is construction of new renewable
plants, not the trajectory of total energy use. Empirical judgment about the
arithmetic of shares under near-flat demand.

**How it became work:** Changed the forecast target from the *share* to the
renewable *level* (Btu). The model projects the renewable numerator
component-by-component, then divides by a held-constant 2009 total-consumption
denominator (`T0`), because the data show total consumption near-flat
2000→2009 (CA +0.2%, AZ +9.1%, NM −1.0%, TX −6.3%). The share is then a derived
quantity. Implemented in `forecast()` (`R2025 = Σ component 2025`,
`share = R2025 / T0`).

## Exchange 3 — Decision-relevant uncertainty threshold
**Question (expert_question_3.md):** Roughly, how wrong would your 2025 number
have to be before the target you'd set from it would be badly off — if the real
amount of renewable energy in a state by 2025 turned out to be a lot more or a
lot less than you planned on?

**Reply (summarized, verbatim in expert_reply_3.json):** A target set from a
2025 forecast is badly off when the miss is large enough to change the policy
decision, not when it merely misses the number. Roughly ±20–30% in the 2025
renewable amount is the threshold where the target stops being defensible; a
miss of 2× or more (double or half) is what genuinely breaks it. The asymmetry
matters: an *over*-forecast means the target is unreachable and gets abandoned
(the more damaging failure for a governor); an *under*-forecast means the target
is trivially met and sets no real policy. Given the lumpy, step-driven history,
misses of this size are plausible over a 15-year horizon.

**How it became work:** (a) The model reports a ±30% defensible band around every
forecast (`low = 0.70·R`, `high = 1.30·R`, with matching shares), not a single
point estimate. (b) The central 2025 case is set at the conservative end of the
band (component rates clipped to [0, 12%], declining hydro held flat) because the
over-forecast is the more damaging error for a governor — over-claiming an
unreachable target is worse than under-claiming one that is trivially met.
Implemented in `forecast()` (`2025_low_BBtu/2025_high_BBtu` and the conservative
rate clip).

---
No exchange produced only prose: each reply maps to a named constraint/equation
in `code/analysis.py` and to a reported number in `results/solution.json`.
