# Expert Interaction Evidence — Problem 2016_C (Goodgrant $100M/5yr)

Policy: 10 fixed exchanges, one question each, sequential. Every reply below
was converted into a model parameter, constraint, or code change before the
next exchange; the value/range, the model location, and the interval of
validity are recorded per exchange.

## Exchange 1 — dominant selection mechanism (structural branch)

- **Question** (`expert_question_1.md`): "When picking which colleges deserve extra money to improve student performance, what do big donors like the Gates Foundation actually look at first?"
- **Reply (key points)**: first screen is student population served (high Pell / first-gen / minority share) + demonstrated capacity to use money well + alignment with funder portfolio; scale and cost-effectiveness only after these. Not rankings or prestige.
- **Effect on work**: established the model's dominant mechanism = need-first, capacity-gated selection. This became the three-component scoring architecture: (1) need/mission fit from `PCTPELL` + minority-serving flags (HBCU/NANTI/HSI), (2) capacity (retention, completion, financial stress), (3) ROI potential. Weights: need component `alpha_need = 0.4` (highest, per the reply's priority ordering), capacity `alpha_cap = 0.3`, ROI `alpha_roi = 0.3` — `code/model.py:69-76`. Interval: applies to the full candidate universe of 4-year and 2-year US postsecondary institutions in the IPEDS list.

## Exchange 2 — plausible effect sizes (parameter branch, conditional on Exch 1)

- **Question**: "When a charity funds a college for five years, what kinds of student gains can you realistically see from such funding?"
- **Reply (key points)**: retention gains ~1–5 percentage points; completion gains ~1–3 points, slower, visible in later cohorts; equity-targeted groups improve relatively more; effects lag spending; no transformational jumps in 5 years.
- **Effect on work**: calibrated the outcome model's effect band. `eff_ret_lo=1.0, eff_ret_hi=5.0` retention points, `eff_comp_lo=1.0, eff_comp_hi=3.0` completion points, interpolated by each school's capacity score (`code/model.py:106-109`). Also motivated using intermediate/leading indicators (retention) rather than headline completion alone in the ROI index, and the 5-year student-benefit horizon `UGDS * 5`. Interval: 5-year funding window, institutions with measurable baselines.

## Exchange 3 — grant size realism (parameter branch)

- **Question**: "How much money per school is a realistic amount for a donor to give so the school can actually use it well?"
- **Reply (key points)**: usable grant ≈ $0.5M–$5M per year; $1–2M/yr sweet spot; below ~$250K/yr too small to fund a real program; above ~$5–10M/yr hard to absorb; 20–100 schools per year at $1–5M each is the realistic spread of $100M.
- **Effect on work**: set the allocation bounds in the water-filling allocator: `min_grant = $500,000` (per-school floor, i.e., $250K/yr over the 2-year ramp start) and `max_grant = $5,000,000` (initially; tightened in Exch 10) — `code/model.py:84-121`. School-count target 50 (mid of 20–100) — `--n-schools 50`. Interval: annual disbursement scale, mid-sized US institutions.

## Exchange 4 — allocation shape (structural branch, second structure)

- **Question**: "Should the $100 million each year be split evenly across chosen schools, or more toward the top of the list?"
- **Reply (key points)**: more toward the top, not even; diminishing marginal return; tiered allocation with a floor below which a school is not funded.
- **Effect on work**: replaced uniform allocation with a rank-tapered water-filling scheme: raw weight `(n-i+1)^powe` with `powe=2`, then iterative water-filling that pins grants at the min/max bounds and reallocates the residual, with a floor so no funded school receives below `min_grant` — `code/model.py:84-121`. Result: 50 schools, grants $0.5M–$4M, top of list receives the largest grants (see `results/investment_strategy.csv`).

## Exchange 5 — what counts as evidence of success (parameter/verification branch)

- **Question**: "When reviewing grants after a few years, what kind of results would convince a donor the money worked?"
- **Reply (key points)**: movement in the targeted outcomes (retention, credits, pass rates, completion for the funded population) vs a credible counterfactual; dose–response across funding levels; persistence after the grant ends; plausible mechanism. Activity reports and enrollment growth do not convince.
- **Effect on work**: fixed the charity ROI definition in the model: ROI index = value of incremental retention + completion points + earnings-band improvement for the funded student population, per $1M donated (`code/model.py:112-131`), explicitly **not** enrollment or spending. The model also encodes the dose–response test: `delta_retention_pts` and `delta_earn_share` are increasing functions of the per-school capacity/ROI scores, so larger grants (higher-ranked schools) predict larger effects — reproduced in the output table (rank-1..8 schools: retention effect 3.8–4.9 pts). Interval: 3–5 year evaluation window, peer-matched comparison.

## Exchange 6 — commitment schedule (structural branch)

- **Question**: "When giving money over five years, do donors usually commit the whole amount upfront, or set it free year by year?"
- **Reply (key points)**: multi-year pledge with annual, performance-contingent disbursement; renewal conditional on milestones; larger first-year/startup tranche common.
- **Effect on work**: the allocation is per-year: the $100M computed each year is the **annual tranche** to each selected school, not the 5-year total. The 5-year strategy is the re-application of the same prioritized list annually, with later-year tranches contingent on meeting the outcome milestones of Exch 5 (retention/completion movement vs counterfactual). This is stated in the submission's `subtask_outcome_analysis` as the disbursement rule; the model outputs the annual amounts.

## Exchange 7 — exclusion criteria (boundary branch)

- **Question**: "Which schools would a donor avoid funding, even if they need help badly?"
- **Reply (key points)**: avoid for-profit/mission-misaligned institutions, schools with no absorptive capacity, already-wealthy high-endowment schools, too-small/unstable institutions, and schools with no measurable outcome to move.
- **Effect on work**: added a hard exclusion filter in `code/clean_data.py:57-73`: `excluded = excl_forprofit | excl_tiny | excl_nodata`, where `excl_forprofit = (CONTROL == 3)` (scorecard control code verified against institution names: 1 = public, 2 = private, 3 = for-profit), `excl_tiny = UGDS < 100`, `excl_nodata = missing PCTPELL and both retention measures`. Applied in `code/model.py:31` before scoring. Result: 105 of 2,936 joined schools excluded (1 for-profit, 104 sub-scale, 4 no-data, overlapping), leaving 2,738 analyzable after data-signal filters.

## Exchange 8 — funding duration (parameter branch)

- **Question**: "When donors pick a short list of favorite schools, how long do they usually keep funding each one?"
- **Reply (key points)**: 3 years typical first commitment, renewals to 5–8 total; 5 years is the common ceiling for a single commitment; 1-year grants produce no measurable outcome.
- **Effect on work**: fixed the per-school commitment horizon at 5 years (the program's own window) with the effect model of Exch 2 applied over that horizon; 1-year or shorter tranches are not treated as sufficient to move outcomes, consistent with the annual-disbursement rule of Exch 6. `students_benefit_5yr = UGDS * 5` in the ROI index (`code/model.py:110`).

## Exchange 9 — first-year tranche sizing (parameter branch)

- **Question**: "When a school is getting a five-year grant, how does the donor decide how much to give it in year one?"
- **Reply (key points)**: year one sized by startup cost of the intervention and the absorptive ceiling (~1–2% of operating revenue); larger startup tranche, then steadier amounts; unproven schools start smaller.
- **Effect on work**: implemented a startup-weighted tranche schedule: year-1 tranche = 1.25 × the level annual amount, years 2–5 each 0.9375 ×, preserving the 5-year total equal to the committed amount (1.25 + 4×0.9375 = 5). Level annual amount = `grant_usd / 5` from the allocation. The 1.25 startup factor is bounded so no year's tranche exceeds the $5M/yr absorptive ceiling of Exch 3. This schedule is reported per school in the submission.

## Exchange 10 — who receives the largest grants (boundary/consistency check)

- **Question**: "In education philanthropy, which schools usually get the largest multi-million-dollar grants?"
- **Reply (key points)**: the biggest grants go where absorptive capacity, execution history, and funder visibility are highest — large, well-known institutions, proven grant executors — not necessarily where need is greatest.
- **Effect on work**: consistency check on the Exch 4 taper: the model's largest grants go to schools high on the composite score, which jointly requires need AND capacity AND ROI potential — i.e., capacity-gated, matching the "big checks go where capacity is highest" pattern. Consequence: the per-school ceiling was tightened from $5M to `max_grant = $4,000,000` (≈ $800K/yr, comfortably within the 1–2%-of-revenue absorptive band for the funded population) so no single school's annual tranche approaches the distortion threshold from Exch 3. Final run: `--n-schools 50 --min-grant 500000 --max-grant 4000000 --powe 2` → 50 schools, total exactly $100,000,000, grants $0.5M–$4.0M.
