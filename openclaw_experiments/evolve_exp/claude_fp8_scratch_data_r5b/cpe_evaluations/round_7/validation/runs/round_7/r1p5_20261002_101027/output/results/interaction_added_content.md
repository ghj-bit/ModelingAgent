# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — Problem 2018_C (Border Energy Compact)

Three expert exchanges, one question each, each turned into a concrete model
parameter/constraint before the next exchange. Expert text is input only; the
submission carries values, constraints and equations, not the expert's sentences.

## Exchange 1 — Core structural assumption

**Question (expert_question_1.md):** For a state with no new policy, is its renewable
energy share of total consumption a smooth gradually-changing trend, or lumpy — driven by
occasional big events (a big plant, a cheap new technology)?

**Reply (summarized, expert_reply_1.json):** Reject the smooth-trend as the primary
characterization. The series is a low roughly-flat baseline punctuated by level shifts
(hydro dams, PURPA, wind/geothermal/solar plant openings, RPS) plus weather-driven
hydro noise. A single smooth extrapolation is badly wrong, especially for TX (wind) and
CA. A trend fit is defensible as a "no-new-policy" baseline only if (a) fit on the
post-1990 period, (b) identified policy/plant events are treated as level shifts, and
(c) a range, not a point path, is presented.

**How it changed the work (forecast.py, Part I.D):**
- Dropped the smooth-trend extrapolation. Model = baseline + discrete level-shifts + a
  hydro-weather noise term; trend window fixed to post-1990 (`--start 1990`).
- Every 2025/2050 output is a range, not a point; a hydro-noise spread (±3 pp at 2025,
  ±6 pp at 2050, asymmetric upward) is applied to the renewable-electricity share.
- Level-shift detection run on the data flagged the real step years (CA wind/solar/geo
  ~1989, NM wind 2004-08, TX wind 2008-09), confirming the baseline+shifts structure.

## Exchange 2 — Causal mechanism / directionality

**Question (expert_question_2.md):** For one of these states, which is the stronger ceiling
on how much renewable electricity can actually be used — the electricity it needs (demand)
or how many renewable generators it can physically build (supply)?

**Reply (summarized, expert_reply_2.json):** The binding ceiling is SUPPLY (new plants
built), not demand. In a no-policy world demand is large, grows slowly and predictably, and
is far below what new renewables could supply, so it is non-binding. Two qualifications:
(firm vs. nameplate) intermittent wind/solar can't be counted at full value without
storage/backup, so the effective ceiling is lower than raw capacity; and (curtailment)
surplus shows as exports/curtailment, not higher in-state share. Model renewables as
supply-limited: share rises only as fast as new plants come online.

**How it changed the work (forecast.py, targets.py):**
- Demand treated as non-binding: total consumption forecast on a slow, near-linear
  growth (central 0.8%/yr, range 0.5-1.2%/yr) — it does not cap renewables.
- Renewable growth made supply-limited: the renewable-electricity share rises at a modest
  step rate (0.30-0.35 pp/yr central), the no-policy baseline.
- Intermittency derate: wind/solar credited at 0.85/0.80 of nameplate when mapped to
  share; a firm-capacity/curtailment ceiling caps the renewable-electricity share at
  75% (band high 80%), so surplus is not counted as in-state share.

## Exchange 3 — Interpretation context for uncertainty

**Question (expert_question_3.md):** When I give a projected 2050 renewable share with an
uncertainty range, how wide can the range be before it becomes useless for setting a real
policy target?

**Reply (summarized, expert_reply_3.json):** A range is usable when its width is small
enough that the policy conclusion doesn't flip across it. For a share figure: usable
~±5-10 pp; marginal ±10-20 pp (state as a range/floor, not a point); useless >±20-25 pp
or a band spanning most of the plausible range. Acceptable width must be asymmetric-aware
(lumpy step-ups lengthen the upside tail) and paired with its driver (build rate / policy
events), not presented as a bare number. Empirical judgment, not a precise threshold.

**How it changed the work (forecast.py, targets.py, Part II.A):**
- Added an explicit band-width check (exchange3_band_check): each 2050 total-renewable
  share band is graded usable/marginal/useless at the ±10 / ±20 pp thresholds. All four
  states come out "usable" (2050 widths 1.5-2.4 pp), so the baselines can anchor a target.
- Targets (Part II.A) are therefore stated as RANGES/floors (a policy lift added to the
  no-policy baseline, e.g. 2025 ~10-14%, 2050 ~15-21% combined ~18%), never bare points,
  each paired with its driver (build rate / RPS / CA SB100 directionality).

## Reproduction

- Data prep/profiles: `code/prep_and_profile.py` -> `logs/prep_and_profile.log`
- Forecast: `code/forecast.py` -> `logs/forecast.log` (sweep: `--sweep TX,0.2,1.6`)
- Targets: `code/targets.py` -> `logs/targets.log`
- Request/reply files: `logs/operator_feedback/expert_request_N.json` /
  `expert_reply_N.json`; questions: `logs/operator_feedback/expert_question_N.md`.
