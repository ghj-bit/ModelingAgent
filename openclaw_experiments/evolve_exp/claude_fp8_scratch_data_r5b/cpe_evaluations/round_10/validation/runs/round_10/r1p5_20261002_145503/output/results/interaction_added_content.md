# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — MM-Bench 2018_C

Three expert exchanges, one question each, in order. The controller owned the
request/reply files; the agent read the reply and turned it into a model input.

## Exchange 1 — Operational definition of the key variable

**Question (expert_question_1.md):**
> When a governor asks "how much renewable energy does our state use?", do they
> want how much of the state's total energy needs are met by clean sources, or
> the raw amount of clean energy generated, and what typically gets left out of
> that picture?

**Reply (summary):** The governor wants the **share** — the fraction of total
energy consumption met by clean/renewable sources, not the raw BTU amount. A raw
total is meaningless without a denominator. The picture typically leaves out:
consumed-vs-generated (imports/exports), the all-energy-vs-electricity-only
denominator difference, hydro/biomass treatment, and the renewable-vs-clean
(nuclear) distinction.

**How the reply became work:** This fixed the model's input structure. The energy
profile for each state was defined as the renewable/clean **share** of total
end-use energy (denominator `TETXB`), not an absolute BTU figure. Two share
definitions were adopted and reported side by side because the reply flagged the
renewable-vs-clean and all-energy-vs-electricity conflation:
- `renewable share = (solar SOTCB + wind WYTCB + geothermal GERCB + hydro HYTCB + wood/waste WWTCB) / TETXB`
- `clean share = renewable share + nuclear NUETB / TETXB`
The absolute renewable BBtu is still reported for context, but the decision and
comparison metric is the share. Interval: applies to the 1960–2009 profile and
the 2009 "best" ranking.

## Exchange 2 — Causal direction / dominant mechanism

**Question (expert_question_2.md):**
> Why do some states get most of their power from clean sources while
> neighboring states don't — what on-the-ground factors most decide it?

**Reply (summary):** Dominant factors, in rough order: natural-resource
endowment (hydro, wind, solar, geothermal); federal/legacy infrastructure
(already-built zero-fuel-cost clean base); state policy (RPS, net metering,
tax incentives); utility structure and transmission/import access; incumbent
fuel economics and sunk industry; geography/climate load shape. Neighbors
diverge mainly because of endowment + legacy + policy, not "clean intent".

**How the reply became work:** This became the explanatory framework for the
evolution and similarity/difference analysis. It told the agent which state-level
drivers to test against the data rather than treat the share as a free trend:
- Resource endowment is visible directly in the data as which renewable component
  dominates each state: CA = hydro (272,187 BBtu, 2009) + growing solar (31,397);
  AZ = hydro + large nuclear legacy; NM = wind + wood/waste; TX = wind (195,455,
  fastest growing 2005–2009) + nuclear legacy.
- The incumbent-fuel-economics driver is why the all-energy renewable share stays
  low everywhere even where the electricity mix is clean: transport and thermal
  loads are fossil-bound (petroleum 37–49% + gas 7–26% of end-use in all four).
- It justified the decision to interpret the 2009 "best" state on the clean
  *share* and recent *rate of change* (endowment + momentum) rather than raw
  totals, and to attribute the inter-state differences to endowment/legacy/policy
  in the interpretation rather than to a single aggregate trend.
Interval: 1960–2009.

## Exchange 3 — Robustness threshold for the 2025/2050 forecast

**Question (expert_question_3.md):**
> Predicting energy use decades ahead without policy changes — when would you
> trust such a projection, and what would make you doubt it?

**Reply (summary):** Trust a no-policy projection only as a **baseline trend
extrapolation**, and only when (a) the trend is well identified over a long
stable record (50 y is adequate for slow aggregates), (b) the horizon is ~1–2
decades, (c) the drivers are not at a turning point. Distrust it where there are
structural breaks in the window, where the variable is a **share** (renewable
shares inflected up by policy and cost decline), where policy is the dominant
lever (true for renewables), or when the horizon exceeds the data's variability
scale.

**How the reply became work:** This set the forecast discipline and its
interpretation limits:
- Total end-use was forecast by **log-linear** extrapolation (well-identified,
  R² 0.87–0.96, slow-moving aggregate) — treated as a reliable baseline.
- Renewable/clean **shares** were NOT projected as point predictions. Because the
  reply identified shares as policy/cost-inflected, the model reports, for each
  horizon, (i) the long-window linear trend value and (ii) a recent-5-year trend
  value, and explicitly flags the 2050 share as low-confidence / not a
  commitment. The wide gap between the two (e.g. TX renewable share 1.5% on the
  long trend vs 15.4% on the recent wind/solar ramp) is itself the reported
  uncertainty, reflecting the policy/cost inflection the expert named.
- The 2025 point estimates are presented as the more trustworthy baseline (within
  the ~1-decade reliable window); 2050 is presented as a range with the caveat
  that "no policy change" is itself unrealistic for renewables.
Interval: forecast horizons 2025 (reliable) and 2050 (low confidence).

---
All three replies were turned into concrete model inputs (share metric + two
denominators, driver-based interpretation, and the forecast reliability
hierarchy with the trend-vs-recent-trend band). No reply text was copied into the
submission; the values, the metric definitions, and the reliability caveats are
stated in the agent's own formulation in solution.json.
