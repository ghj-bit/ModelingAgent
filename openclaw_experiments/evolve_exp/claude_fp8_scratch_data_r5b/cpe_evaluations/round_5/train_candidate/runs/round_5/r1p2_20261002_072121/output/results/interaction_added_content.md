# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction evidence — 2015_C (ICM Human Capital)

Three expert exchanges, one question each, in the order they governed the work.

## Exchange 1 — causal mechanism (asked before the dynamics were built)

**Question** (`logs/operator_feedback/expert_question_1.md`):
> Our model treats yearly churn as each worker having a fixed 18% chance of leaving, unaffected by who else quit. In real companies, does one person quitting measurably raise the odds that their teammates quit in the same year, or do most people leave for personal reasons regardless of colleagues?

**Reply** (`logs/operator_feedback/expert_reply_1.json`): peer contagion is real but modest relative to personal/economic drivers; empirically a departing close colleague raises a colleague's quit hazard by roughly 10–50% in relative terms over the following months; quits cluster within work groups; treating churn as an independent per-person probability is a reasonable first-order approximation, and contagion matters mainly for short-horizon dynamics and for the "churn diffuses" mechanism, not for the long-run average rate.

**How the reply became work** (source of every value marked [E1] below):
- Added a contagion term to the monthly hazard in `code/icm_model.py` (`run_one`):
  `p = base_p · min(BETA_MAX, 1 + BETA_PER_DEP · per_team) · beta`, where
  `per_team = Σ 0.5^(age/3) / (N_level / TEAM_SIZE)` over recent level
  departures (team-size proxy, 3-month decay half-life).
- Calibrated `BETA_PER_DEP = 0.30` (per departing close colleague) at the
  middle of the expert's 10–50% relative band, with `BETA_MAX = 3.0` as a
  saturation cap (an employee cannot have more than a handful of close
  colleagues quit in the window).
- `beta = 0` reproduces the independent-hazard baseline, so the expert's
  "first-order approximation is reasonable" is honored as the model's
  reference point; `beta = 1` is the base case.
- `MONTHS_PER_50PCT = 3` encodes the expert's "following months" time
  window (a departure 3 months old still contributes half of a fresh one).
- Validity interval: the calibration holds for short-horizon (months to
  ~1 year) dynamics; the expert explicitly noted it does not shift the
  long-run average rate, which is why the base churn rates remain pinned
  to the problem's 18% anchor.
- Sensitivity: the beta sweep (0.0 → 2.0) brackets the expert's band and
  is reported in the submission as the model's main uncertainty axis.

## Exchange 2 — operational constraint (asked after the dynamics, before finalizing productivity accounting)

**Question** (`logs/operator_feedback/expert_question_2.md`):
> After a worker quits, we treat the seat as empty until the replacement starts. In practice, how do the remaining teammates cope during that gap — do they simply work at full speed and let quality slip, or do they temporarily absorb part of the departed person's workload?

**Reply** (`logs/operator_feedback/expert_reply_2.json`): teammates almost always absorb part of the departed workload; short gaps are covered by picking up critical tasks and letting low-priority work slide; longer gaps show up as overtime, deferred maintenance/backlog, and quality/morale erosion; the realistic picture is "overloaded people, partial coverage, deferred work", not "full speed, lower quality".

**How the reply became work** (source of every value marked [E2] below):
- Changed the productivity accounting in `run_one` from "each vacant seat
  = 1.0 lost seat-month" to: the team absorbs `ABSORB = 0.6` of each
  vacant seat's work (overtime/strain, no output loss), and the remaining
  `1 − ABSORB = 0.4` is charged as deferred backlog at the level's salary
  value. 0.6 is the midpoint of the expert's "somewhat more, but not
  enough to fully replace" statement, applied within the short-gap regime
  (vacancies in this model last 1–7 months, i.e. weeks-to-months gaps).
- Added `load_shock[name] += q` on departures, decaying with a 3-month
  half-life, so the strain is a transient that relaxes while the gap
  persists — the expert's "initial absorption, later strain" pattern.
- The new-hire ramp (50% capacity during the level's recruitment lead
  time) was retained alongside, since it is a separate, data-anchored
  effect (Table 1 lead times).
- Validity interval: holds for the weeks-to-months gap regime of this
  simulation; the expert noted the absorption share depends on role
  substitutability and team slack, which the model does not resolve.

## Exchange 3 — decision-relevant uncertainty threshold (asked after results existed, before the verdicts were written)

**Question** (`logs/operator_feedback/expert_question_3.md`):
> Our model's two-year cost figures carry about a 10 percent margin of error. When deciding whether to budget extra recruiting money, what size of difference between two scenarios would you actually act on?

**Reply** (`logs/operator_feedback/expert_reply_3.json`): act on between-scenario differences of roughly 20% or more; below ~10–15% the gap is inside the noise; 15–20% is suggestive but marginal; recruiting dollars are only part of the picture (headcount and time-to-fill differences can still warrant action); and because the error is systematic/shared, between-scenario comparisons partially cancel the common error, so a 15% between-scenario gap is more trustworthy than a 15% gap against an external benchmark.

**How the reply became work** (source of every value marked [E3] below):
- `main()` now tags every cost comparison with a verdict using the
  expert's thresholds: `ACT` if the largest relative scenario difference
  ≥ 20%, `MARGINAL` if ≥ 12%, otherwise `noise-band`
  (`TH_ACT = 0.20`, `TH_NOISE_HI = 0.15` in `code/icm_model.py`).
- All outcome verdicts in the submission are between-scenario comparisons
  (e.g. 25%-churn vs 18%-churn recruiting cost), following the expert's
  caveat that same-model comparisons cancel shared systematic error.
- Headcount/time-to-fill metrics (fill-rate trajectory, peak vacancies)
  are reported alongside the dollar metrics, per the expert's caveat that
  small dollar gaps can still warrant action when headcount effects are
  large.
- Validity interval: the thresholds apply to the two-year budget
  decisions in tasks 3–5; they were not applied to the network
  statistics of task 1 (a structural, not a forecasting, result).

## What each exchange did NOT do

- No expert sentence, phrasing or structure was copied into
  `results/solution.json`; only the values, constraints and thresholds
  above (each tagged [E1], [E2], [E3]) entered the model or the verdicts.
- No exchange was used for coding, debugging, or data processing.
