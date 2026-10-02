# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — Problem 2018_C

## Exchange 1

**Question** (written to `logs/operator_feedback/expert_question_1.md`):
When you judge how "green" a state's energy system is, does it count more if it
uses more renewable energy in absolute amount, or if renewable energy makes up a
larger share of what the state uses overall?

**Reply** (from `logs/operator_feedback/expert_reply_1.json`):
Share matters more than absolute amount. "Greenness" is a property of the mix,
not the size. The standard criterion is the renewable share of total energy
consumption (and, secondarily, of electricity generation). Absolute amounts are
useful only for context — e.g., how much total renewable capacity the compact
can bring to bear — not as the ranking metric itself.

**How the reply became work:**
- Parameter/constraint: the Part I-C "best profile" ranking metric is the
  renewable share RSH = RET/TET (renewable consumption as a share of total
  energy consumption), not absolute renewable consumption. Recorded as
  constraint C1 with source "expert exchange 1"; valid interval: the 2009
  cross-state comparison (and all target-setting that follows from it).
- Secondary metric: renewable share of electricity generation (renewable
  electricity Btu / total renewable electricity Btu, state production) is
  carried as a supporting dimension, also from exchange 1.
- Effect on model: `profile.py` ranks the four states by `rsh_pct` and reports
  absolute `ret_Btu` only as context; the ranking used in the Part I-C outcome
  and the Part II-A targets is the share ranking.

## Exchange 2

**Question** (written to `logs/operator_feedback/expert_question_2.md`), building
on exchange 1: given that the data show the whole-state renewable share barely
moved 1960-2009 while states got greener mainly through the electricity mix,
would the governors want a separate, steeper goal for where the electricity
comes from, and if so tougher, looser, or the same?

**Reply** (from `logs/operator_feedback/expert_reply_2.json`):
Yes — a separate, steeper goal for electricity, tougher than the whole-state
goal. Electricity is the one sector where renewables substitute directly and at
scale; transportation and industrial heat are dominated by liquid fuels and
process heat and penetrate slowly. Same percentage-point gain is far easier in
electricity. Setting only the overall goal would let states meet it through
electricity alone while the rest of the energy system stays unchanged —
exactly the pattern the data show. Electricity goals are typically set several
times higher than whole-energy goals in this era.

**How the reply became work:**
- Parameter/constraint: constraint C2 — the compact carries two target metrics,
  (i) renewable share of total energy consumption (whole-state) and (ii)
  renewable share of in-state electricity generation, with the electricity
  target set higher (roughly several times the whole-state target in
  percentage points) and reached sooner (earlier date). Source: expert
  exchange 2; interval: 2025 and 2050 targets.
- Effect on model/decision rule: `targets.py` solves for the whole-state 2025/2050
  share targets from the Part I-D no-policy baseline (extrapolation, see
  `predict.py`) plus a policy uplift, and sets the 2025/2050 electricity-mix
  targets at a multiple of the whole-state uplift, reaching the final
  electricity level by 2035 rather than 2050. The Part II-A goals stated in
  `solution.json` are the dual-metric pair from this rule.

## Exchange 3

**Question** (written to `logs/operator_feedback/expert_question_3.md`), building
on exchanges 1-2: when a state sets a 2050 renewable-energy goal, is it
sensible to put in a 2035 halfway milestone, and would governors find it useful
or red tape?

**Reply** (from `logs/operator_feedback/expert_reply_3.json`):
Yes — a 2035 milestone is sensible and useful, not red tape. A 2050 target
alone is unenforceable; an interim checkpoint is a near-term accountability
test and the point at which a governor's own record can be judged. It lets
governors claim visible progress within their terms and flags off-trajectory
early, before correction becomes expensive. Standard practice is a long-horizon
goal paired with a 2030-2035 checkpoint. Caveat: the milestone must use the
same share-based metric as the final goal or it becomes a loophole.

**How the reply became work:**
- Parameter/constraint: constraint C3 — the compact's goals include an
  intermediate 2035 checkpoint on the same share-based metrics as the 2050
  goals (C3a: same metric as C1/C2, per the reply's caveat). Source: expert
  exchange 3; interval: 2035 checkpoint, lying between the 2025 and 2050
  targets on a monotone path.
- Effect on model/decision rule: `targets.py` computes the 2035 checkpoint as a
  point on the same trajectory (monotone share path) as the 2050 target, so the
  compact states goals for 2025, 2035, and 2050 on identical metrics. The Part
  III memo summarizes the 2009 profiles, the no-policy predictions, and the
  2025/2035/2050 goals.
