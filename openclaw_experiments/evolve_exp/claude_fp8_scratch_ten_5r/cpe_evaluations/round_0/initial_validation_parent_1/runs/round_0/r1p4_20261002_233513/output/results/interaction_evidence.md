# Interaction Evidence — Problem 2016_C (Goodgrant Foundation)

Ten exchanges, one question each. For each: the question, the reply (paraphrased
value), and the concrete way the reply entered the model (parameter,
constraint, or decision rule) with the interval it supports and where it is
used in `code/clean_model.py`.

## Exchange 1 — fund size vs. school budget
- **Question:** How does a few million dollars of outside philanthropic
  funding compare with a typical American college's annual budget?
- **Reply (value):** A few million is small-to-moderate: 1–10% of annual
  revenue at small/mid schools, well under 1% at large universities. It funds
  a targeted program, not the operating budget.
- **Effect on work:** Sets the per-school grant scale as a program budget, not
  a capital injection. Used to justify per-school doses in the $1–10M/yr range
  and to rule out facility-style uses. Interval [1e6, 1e7] $/yr/school.
  Feeds `PARAMS.dose_min`, `dose_max` (code/clean_model.py:PARAMS).

## Exchange 2 — timing of effects
- **Question:** When do students at a grant-funded college first show
  improved results?
- **Reply (value):** Little in year 1; intermediate metrics (persistence,
  credits) move in years 2–3; graduation effects appear only in years 3–5
  because completion lags entry by 4–6 years.
- **Effect on work:** `completion_lag = 4` years [4,6] and
  `effect_year = 2` [1,3] in PARAMS. The completion model counts only cohorts
  that can finish inside the 5-year window: window = (5−4+1)/5 = 0.4
  (dose_to_completions). The donor-score also weights retention (a 1–2-year
  metric) alongside graduation.

## Exchange 3 — who suffers most from not finishing
- **Question:** Which group suffers most — Pell students, heavy borrowers, or
  students at small schools?
- **Reply (value):** Heavy borrowers who drop out most; Pell recipients less
  (no debt burden); school size itself is not the driver.
- **Effect on work:** Candidate score loads burden signals weighted so debt
  and loan share are primary (0.20 + 0.15) with Pell need (0.30) — see
  build_scores. Schools whose students borrow heavily and do not finish are
  prioritized.

## Exchange 4 — who big donors fund
- **Question:** Do big education donors pick the most struggling schools or
  well-run mid-tier schools?
- **Reply (value):** Mid-tier capable schools with demonstrated capacity; the
  worst are avoided because they cannot absorb the grant.
- **Effect on work:** Capacity term (RET_FT4 retention) weighted 0.20 in the
  score, and the extreme-need tail (top 10% of the need rank) is damped by
  50% and capped at 2.0 robust-std units (build_scores, "mid-tier capable,
  real need" rule).

## Exchange 5 — concentration of the $100M
- **Question:** Smaller amounts to more schools, or larger to fewer?
- **Reply (value):** Larger to fewer, with a floor: below ~$1–2M/yr/school a
  grant cannot fund a coherent intervention; above ~$5–10M/yr it cannot be
  absorbed productively; a 20–50 school portfolio is the practical middle.
- **Effect on work:** `dose_floor = 1e6` [5e5, 2e6], `dose_min = 2e6`
  [1e6, 2e6], `dose_max = 1e7` [5e6, 1e7] in PARAMS; allocation clips doses
  to [floor, max] (allocate). The N-sweep (20→150) tests the 20–50 band;
  N=50 at $2M/yr/school is the base case, and N=75–100 ($1.33–1.0M) sits at
  the floor boundary.

## Exchange 6 — best use of a few million
- **Question:** What does a college do well with a few million — advising,
  aid, faculty, facilities?
- **Reply (value):** Advising and completion programs first; aid second;
  faculty and facilities poor fits.
- **Effect on work:** The model's intervention is specified as an
  advising/completion program (decision rule, stated in task_analysis); all
  effect estimates (completions per dollar) are therefore program effects,
  not capital effects.

## Exchange 7 — persistence after the grant
- **Question:** After the grant ends, do completion improvements fade or keep?
- **Reply (value):** They fade substantially but not to zero; institutionalized
  practices persist, staff-dependent effects decay over the following years.
- **Effect on work:** `fade_rate = 0.10` [0.05, 0.20] per year in PARAMS.
  Post-grant survival of each year's incremental completions:
  persist = mean of (1−fade_rate)^t, t=1..5 = 0.737, applied in
  dose_to_completions.

## Exchange 8 — earnings premium of completion
- **Question:** How much higher is a typical graduate's salary than a
  mid-way dropout's, per year?
- **Reply (value):** ~$20,000/yr, range $10k–$25k.
- **Effect on work:** `earn_gap = 20000` [10000, 25000] in PARAMS. Value per
  completion = earn_gap × Σ(1+0.03)^−t over a 40-year career = 20000 × 23.11
  ≈ $462k present value (roi_calc). Sensitivity run: ROI 1.13 at 10k, 2.83
  at 25k (logs/sweep_params.log).

## Exchange 9 — the donor's leading indicator
- **Question:** Besides graduation, what single improvement would a donor
  most want to see?
- **Reply (value):** First-to-second-year retention/persistence — the
  earliest measurable signal, moving within 1–2 years.
- **Effect on work:** RET_FT4 enters the candidate score (0.20 weight) and is
  reported as the primary near-term KPI in the outcome analysis; graduation
  (COMP4) is the payoff metric. `persist_weight`/`grad_weight` = 0.5/0.5
  in PARAMS document the dual-KPI structure.

## Exchange 10 — ceiling on completions per dollar
- **Question:** Is there a realistic ceiling on completions one dollar can
  plausibly create?
- **Reply (value):** Yes, and it is low: roughly $10k–$50k of grant money per
  additional completion; the binding constraint is student population and
  program reach, not money.
- **Effect on work:** `cost_per_degree = 30000` [10000, 50000] and
  `max_frac = 0.10` [0.05, 0.15] in PARAMS. The completion function caps
  headroom at max_frac × enrollment × (1 − current completion rate) and makes
  reach saturating: 1 − exp(−dose/cost_per_degree) (dose_to_completions).
  At the $2M/yr base dose the saturation factor is 1.0, so the population
  ceiling, not the dose, binds — consistent with the expert.

## Notes
- All ten replies were converted into parameters/constraints before the next
  exchange; no reply was used as content in the submission.
- Empirical parameters not covered by an exchange are either computed from
  the supplied data (cleaning statistics, score weights are analyst choices
  grounded in exchanges 3–4 and 9) or standard modeling conventions (real
  discount rate 3% over a 40-year career, used only to discount the earnings
  stream).
- The scholarly search (code/search.py, logs/search1.log, logs/search2.log)
  returned no usable values for earnings baselines or cost-per-degree; the
  expert exchanges above are the source for those parameters.
