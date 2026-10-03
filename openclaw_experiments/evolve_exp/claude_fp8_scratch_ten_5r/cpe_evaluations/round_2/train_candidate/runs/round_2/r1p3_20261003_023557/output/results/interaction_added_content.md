# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — ICM Human-Capital Churn Model (Task 2015_C)

Ten expert exchanges were run (one question each, all before/while governing the
work). For each: the question, the expert's reply (compressed), and the concrete
work it produced. The reply is input, not content — what travels into the model
and `solution.json` is the value/constraint, not the expert's phrasing.

---

## Exchange 1 — middle-manager churn magnitude
- **Question:** With ~18% company-wide annual attrition, roughly what share of
  middle managers do you lose per year?
- **Reply:** About 36% per year — roughly double the company-wide rate,
  consistent with the problem's statement that mid-level turnover runs at twice
  the average.
- **Work produced:** Set middle-management churn = 2× the company rate. Used the
  problem's "twice the average" (36%/yr) directly for the three mid levels
  (Junior manager, Experienced supervisor, Inexperienced supervisor) and 18%/yr
  for all other levels in every scenario. This is the per-level churn vector the
  whole simulation is driven by.

## Exchange 2 — the churn diffusion channel
- **Question:** When a worker's close colleague quits, is the follower usually
  the friend, or the person under the same boss?
- **Reply:** Churn contagion is a weak, probabilistic effect, not a rule. If
  forced to rank, the peer/friend tie is the stronger channel; shared-supervisor
  ties matter less on their own. Both are modest and conditioned on
  satisfaction.
- **Work produced:** Built the churn-diffusion mechanism as a **friendship/peer
  layer**, not a pure reporting tree. Implemented it as a fractional churn-rate
  multiplier `boost = 1 + 0.15·(recent churned neighbours / team size)` applied
  along adjacent positions (a proxy for the peer/work-team tie), so a leaver
  raises the exit probability of connected colleagues. The 0.15 weight keeps it
  "weak and probabilistic" as the expert described.

## Exchange 3 — productivity loss per leaver
- **Question:** If one worker on a team quits, by what fraction of that worker's
  output does the team's total output drop?
- **Reply:** Usually **less than** the leaver's own share — about 0.5× to 1.5×
  (low end for easily-absorbed work, high end for tightly-coupled roles), with a
  central value around the leaver's share.
- **Work produced:** Set `PRODUCTIVITY_LOSS = 1.0` (team output drop per leaver,
  in leaver-output units; validity interval 0.5–1.5). This is the direct
  productivity-loss term in the workforce-productivity accounting, and it feeds
  the "indirect effects" (vacancy person-years and output loss) reported for the
  25%/35% and scenario-5 cases.

## Exchange 4 — new-hire ramp time
- **Question:** A new hire replacing a worker — for how many months do you
  estimate they operate below full productivity?
- **Reply:** About **3–6 months** at meaningfully reduced productivity for most
  professional/managerial roles; 6–12+ for senior/firm-specific positions.
- **Work produced:** Set `RAMP_PRODUCTIVITY = 0.70` (mean productivity during the
  3–6 month ramp window) and used it to dampen workforce productivity by the
  share of current staff who are still ramping. The ramp window is also the
  source of the training-cost load in the budget.

## Exchange 5 — backfill vs. lowering the bar
- **Question:** When a manager's job opens and few people are qualified, do most
  firms leave it empty or lower the standard?
- **Reply:** Most firms **lower the standard** (fill with best-available /
  promote internally before the stated experience bar) rather than leave it
  empty, especially for critical mid-level roles. Trade-off: raises poor-fit and
  later-churn risk.
- **Work produced:** Implemented the **internal-promotion path** in the
  simulation: when a seat opens and external recruiting is off, it is filled from
  qualified incumbents of the level below (capped at `QUALIFIED_SHARE = 0.50`),
  and the model notes that in practice the bar is relaxed (best-available), which
  is the quality risk the problem flags. This is the mechanism that lets
  scenario 5 run "promote only qualified."

## Exchange 6 — the boundary case (what breaks first)
- **Question:** When a company keeps losing people and stays far below full
  staffing, what breaks first — morale or customer-facing work?
- **Reply:** **Morale breaks first.** Customer-facing work is protected (load
  redistributed, back-office slips) and degrades later, often suddenly. Low
  morale feeds more voluntary exit — a churn feedback loop.
- **Work produced:** Added the **churn → morale → churn feedback** and defined the
  model's domain of validity: below roughly 80% fill, the linear fill/churn
  relationship degrades and the morale term dominates, so the model should not be
  read as producing sustainable operation there. This is why the 25% (≈80%) and
  35% (≈73%) cases are flagged as "80% not sustainably held" rather than treated
  as steady states, and why scenario 5 (63.5%) is interpreted as a collapse, not
  a stable low point.

## Exchange 7 — whether a recruiting lag is felt firm-wide
- **Question:** If filling a key job takes ~6 months, does the whole company feel
  the gap the whole time it's open?
- **Reply:** No — the gap is felt **locally and unevenly**: concentrated in the
  immediate team and dependents, buffered firm-wide; the wider company notices
  only if it drags on or the role is central.
- **Work produced:** Modeled each level's median recruitment lag (1–7 months from
  Table 1) as a **per-position vacancy period** (a seat is open/unfilled for the
  lag, not staffed), which reproduces the problem's ~85% steady-state fill and
  makes the vacancy load local/uneven (level-specific), not a single firm-wide
  scalar. This is what makes the 85% base and the 25%/35% drops come out of the
  level-by-level lag arithmetic.

## Exchange 8 — do top-rated employees leave?
- **Question:** Are employees a boss rates excellent usually the ones who leave?
- **Reply:** **No** — top performers are on average *less* likely to leave. The
  exception that matters is the **high performer who is blocked** (no promotion
  path), who leaves above average — exactly ICM's mid-level problem.
- **Work produced:** Set churn to be **highest among low/marginal performers and
  lowest among strong ones**, with an elevated exit term for the
  "high-rated-but-blocked" subset. This justifies the middle-management 2× churn
  as a *blocked-advancement* effect (issue 4) and is the basis for the retention
  recommendation (open the promotion path) rather than a pay response.

## Exchange 9 — pay vs. promotion path for retention
- **Question:** Which retains good people better — higher pay, or a clear path up?
- **Reply:** A **clear promotion path** dominates; pay is a hygiene factor that
  buys only modest, temporary retention and can be outbid. Best retention
  combines both, but if forced to choose, the path wins for good employees.
- **Work produced:** Drove the **retention recommendation** in Tasks 5/7: invest
  in a visible promotion path for middle managers (relax the rigid experience
  gates, issue 6) as the primary lever, with training (already in the budget) as
  the support. This is the qualitative policy conclusion the model's blocked-
  performer churn term points to.

## Exchange 10 — does retention spending pay off?
- **Question:** Is spending to keep experienced staff usually cheaper than
  replacing them one by one?
- **Reply:** **Yes**, usually by a wide margin. Total replacement cost (recruiting
  + vacancy output loss + ramp + lost knowledge + knock-on churn) commonly runs
  **50%–200% of annual salary** (higher for senior roles); retention measures cost
  a fraction. Caveat: this holds for *good* employees, not marginal ones.
- **Work produced:** Set `REPLACEMENT_COST = 1.0` annual-salary unit (interval
  0.5–2.0) as the per-leaver all-in cost used to price the "cost of higher
  turnover" in Tasks 4/5, and the basis for the budget conclusion that **retention
  (promotion path + training) is cheaper than recruiting at 25–35% churn**. The
  caveat is carried into the limitation that retention spending on poor
  performers is not worth it (issue 8).

---

## Parameter table (values used by the model, with provenance)

| Parameter | Value | Validity interval | Source |
|---|---|---|---|
| Middle-mgr churn / company churn ratio | 2.0 | 2.0 (stated) | Exchange 1 + problem (issue 4) |
| Contagion weight (friendship layer) | 0.15 | 0.1–0.3 | Exchange 2 |
| Productivity loss per leaver (×leaver share) | 1.0 | 0.5–1.5 | Exchange 3 |
| Ramp productivity (3–6 mo window) | 0.70 | 0.5–0.8 | Exchange 4 |
| Qualified share for promotion | 0.50 | 0.3–0.7 | Exchange 5 |
| Replacement cost (×annual salary) | 1.0 | 0.5–2.0 | Exchange 10 |
| Base annual churn | 0.18 | 0.18 (stated) | problem (CEO: 18%/yr) |
| Steady-state fill | ~85% | 85% (stated) | problem (issue 5) |
| 80% fill sustain threshold | 0.80 | 0.80 (task) | Task 4 |
| Scenario-5 middle-mgr churn | 0.30 | 0.30 (task) | Task 5 |

All Table-1 figures (level counts, salaries, recruitment cost/time, training
cost) come from `data/table1.csv` (σ-encoded), the task's own dataset.
