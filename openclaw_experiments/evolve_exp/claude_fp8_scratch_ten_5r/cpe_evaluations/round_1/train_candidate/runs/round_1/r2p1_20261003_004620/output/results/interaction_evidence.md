# Expert interaction evidence — MM-Bench 2015_C (ICM human-capital churn)

Ten exchanges, one question each, all logged in `logs/operator_feedback/`.
Each reply was converted into a model input or rule before the next question.
Expert replies are inputs, not content: nothing below is copied verbatim into the submission.

## Exchange 1 — Backfill mechanism
- Question: how vacancies for supervisors/managers are actually filled.
- Reply: internal promotion is the dominant path for supervisory and middle-management backfill; external hiring is reserved for entry/specialist roles or when no qualified internal candidate exists; faster and cheaper internally.
- **Used as**: backfill rule of the model — promotion ladder (empinex→empexp 15%/yr, supinex→supexp 12%/yr, empexp→junior 8%/yr, junior→senior 5%/yr) runs *before* external hiring, so every supervisor/managerial vacancy is first offered internally; external recruitment only covers the residual, capacity-limited by the 2/3-of-vacancies and 9%/yr caps from the problem statement.

## Exchange 2 — Churn contagion timing
- Question: how quickly coworkers start considering leaving after a colleague quits.
- Reply: gradual and lagged, peaking in the months to about a year after the exit; strongest for close ties and same-level peers, especially mid-level managers; a decaying influence, not a same-day reaction.
- **Used as**: contagion mechanism — each monthly quit at level k adds influence to level k and its direct feeder/reporting neighbors, linearly decaying over a 6-month window, transferring at most 30% of a leaver's baseline quit risk per tie, capped at 2× baseline risk (`CONTAG_STRENGTH=0.3`, `DECAY_MO=6`).

## Exchange 3 — Composition of departures
- Question: share of annual departures that are quits vs. let-go/retirement.
- Reply: typically 60–75% quits, 10–20% retirement, 10–20% involuntary; for ICM, because few are relieved (issue 8), the quit share is plausibly 75–85%.
- **Used as**: constraint — 80% of departures modeled as quits, 10% as retirements (senior/junior only), 10% as involuntary at the low end; the problem's 18% churn rate is applied to quits, which is what drives the network dynamics.

## Exchange 4 — New-hire productivity ramp
- Question: how long until a new hire matches a veteran's skill level.
- Reply: roughly 1–3 years for skilled/professional roles (6–12 months routine, 1–2 years moderate complexity, 2–3+ years specialized/managerial); firm-specific knowledge takes longest.
- **Used as**: `NEWBIE_RAMP_YR = 1.5` central value in [1, 3]; every hire or promotion enters at 70% of full output (`NEWBIE_FRACTION = 0.3`) and matures at 1/1.5-yr rate.

## Exchange 5 — Span of control
- Question: how many working employees one supervisor/manager looks after.
- Reply: front-line ~8–15 (commonly 10–12); middle managers 4–8 direct reports, indirect reach 40–100; senior 3–7.
- **Used as**: `SPAN = 10` (central of 8–15) — one supervisor per ~10 subordinates; the 50 supervisors cover the 205 employees/clerks, which fixes the two reporting tiers of the network (senior→50 middle managers→subordinates).

## Exchange 6 — Degree of the work-network
- Question: how many coworkers one person regularly works with day to day.
- Reply: order of 10–20, common working figure ~12–15.
- **Used as**: `AVG_DEG = 12` (central of 10–20) — target mean degree of the Erdős–Rényi work-network, p ≈ 12/369 ≈ 0.0325.

## Exchange 7 — What suffers first when understaffed
- Question: when openings can't be filled fast, what suffers first — quality, output, or morale.
- Reply: morale first (weeks–months), output next or alongside, quality last (people compensate, defects surface later).
- **Used as**: ordering of the damage cascade in the model — (i) overwork raises baseline quit risk for the levels whose vacancies persist (feedback term ∝ vacancy rate, added to base risk), (ii) filled-position loss cuts output, (iii) quality treated as a lagged effect that surfaces in month ~6+ of sustained understaffing, which the 24-month horizon only begins to show. This also justifies the productivity loss being driven by fill-rate and ramp, not by an ad-hoc quality factor.

## Exchange 8 — Average tenure
- Question: typical years at a company before quitting.
- Reply: ~3–5 years; 1–3 at entry level, 5–10+ for mid-level/managerial; 18%/yr implies ~5–6 yr.
- **Used as**: (i) cross-check on 18% rate (1/0.18 ≈ 5.6 yr, inside the stated range — rate retained); (ii) promotion-ladder rates set so that an employee needs ~3–5 accumulated years before reaching a management level (0.15 + 0.08 ≈ multi-year climb), matching the problem's tenure requirements for advancement (issue 6).

## Exchange 9 — Manager ramp-up
- Question: how long after a promotion before a manager manages at full strength.
- Reply: ~3–6 months to full effectiveness; first 1–2 months weakest; internal promotions ramp faster (weeks–~3 months) than external hires (6–12 months).
- **Used as**: promoted managers enter the destination level at 70% of full output (`NEWBIE_FRACTION`) for the ramp period; internal promotions therefore lose less productivity than the same seat filled externally, which is the quantitative advantage the no-external scenario forfeits.

## Exchange 10 — Hiring response to churn spikes
- Question: when several coworkers quit at once, do companies speed up hiring?
- Reply: yes, but with a lag and only partially — requisitions are triaged toward critical roles; recruiting time and budget cap the response; ICM is already capacity-limited (hiring only 8–10% of positions, ~2/3 of vacancies), so a churn spike raises intent more than actual fill rate.
- **Used as**: the hiring channel is deliberately *not* made reactive — a fixed 9%/yr capacity cap, 2/3-of-vacancies ceiling, and no demand-response term. This is the key reason the 25%/35% scenarios drift to low fill rates: hiring intent rises, actual filling does not.

## Parameters sourced from the problem statement itself (not from exchanges)
- σ = 1.0 median salary (derived: expanding each level to its headcount, the median of the 370-employee salary distribution is 1.0σ, consistent with the experienced-employee average listed as σ and the CEO-to-median ratio of ~10×); churn 18%/yr; middle-manager churn 2× average = 36%/yr; 85% of 370 positions filled; 8–10% of positions actively being hired (~2/3 of vacancies); recruitment times/costs and training costs per table1.csv.
- Data repair: table1.csv contained 21 corrupted 2-byte sequences (U+FFFD) where σ belonged; every corrupted token was recovered as σ from the column pattern (median cost, salary, training columns all scale in σ) and the derived check σ = 1 median-salary passed exactly.
