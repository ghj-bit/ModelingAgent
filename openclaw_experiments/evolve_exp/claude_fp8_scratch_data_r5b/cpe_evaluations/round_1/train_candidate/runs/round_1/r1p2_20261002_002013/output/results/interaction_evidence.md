# Interaction evidence (expert consultation, 3 exchanges)

## Exchange 1 — mechanism (2026-10-02)

**Question (expert_question_1.md):**
> ICM keeps marginal employees for a full career to avoid churn, while good
> middle managers leave. In your experience, what is the single biggest thing
> that pushes a good middle manager to quit?

**Reply (expert_reply_1.json):**
> "Being stuck with no realistic path to promotion or growth."

**How the reply became work (not just prose):**
- Established the **dominant churn mechanism**: the exit hazard of a
  middle-level employee is driven first by whether a promotion path is open,
  second by contagion from departed contacts, third by pay/quality factors.
- Implemented as a multiplicative hazard in `code/icm_model.py`:
  `hazard_i = lambda_i · P(i) · C(i) · Q(i)`, where
  - `P(i)` = promotion-path factor. For the three middle levels
    (junior manager, experienced supervisor, inexperienced supervisor),
    `P = P_STUCK` when fewer than 0.5 open superior slots per incumbent
    exist, else `P = 1`. `P_STUCK = 2.0` is the magnitude; the *logic*
    (no path → elevated churn) is the exchange-1 input. This reproduces
    issue 4 (middle managers churn at ~2× the company rate) as an
    emergent property rather than a hard-coded constant.
  - `C(i) = 1 + κ·f_prev` (churn contagion from recently departed contacts,
    issue 2); `Q(i)` = quality factor (marginal employees kept, issue 8).
- Recorded in `logs/model_spec.md` §2 with source "exchange 1".
- The magnitude `P_STUCK` is pending exchange 2 (bounds); a sensitivity
  sweep over `P_STUCK ∈ {1.2, 1.5, 2.0, 3.0}` is already wired
  (`--sweep P_STUCK=...`) so exchange-2 bounds can be applied in one command.

**Baseline run after this exchange** (`results/scenarios_base.json`,
`logs/icm_model_base.log`): S0 middle-manager churn ≈ 14–17/yr per middle
level (~2× the 18% company rate), org productivity recovers 76.8% → 85.2%
→ 92.5% over two years at 85% fill.

## Exchange 2 — boundary condition (2026-10-02)

**Question (expert_question_2.md):**
> You said a stuck manager quits when there is no realistic path up. In a
> company this size, how many open higher-level jobs is a realistic number
> of promotion openings per year before people start feeling there is no
> way up?

**Reply (expert_reply_2.json):**
> "Roughly 5–10% of the mid-level population per year. For ICM's
> middle-manager tier (order 50–80 people), that's about 3–8 promotion
> openings per year; below roughly 3, the 'no way up' feeling sets in.
> This is an empirical judgment, not a precise figure."

**How the reply became work:**
- Added two calibrated parameters to `code/icm_model.py` `defaults()`:
  - `PROMOTE_RATE = 0.08` — realistic promotion-opening rate, mid-tier
    (exchange 2: 5–10%, midpoint used; holds for a mid tier of ~50–80).
  - `PROMOTE_MIN = 3` — floor below which the "no way up" feeling sets in
    (exchange 2: "below roughly 3").
- Rewrote the promotion-path factor: a middle level is **stuck** (hazard ×
  `P_STUCK`) exactly when its *actual* per-incumbent opening rate
  (superior vacancies / incumbents) falls below the *realistic* opening
  rate `PROMOTE_RATE`. This makes the 2× middle churn an emergent property:
  at 85% fill the superior levels have few open seats, so the actual rate
  is below 8% → stuck → 2×. It also makes the model *responsive*: if HR
  keeps the senior levels adequately open, the stuck multiplier switches
  off and middle churn drops.
- The promotion channel is now **capped** at `max(PROMOTE_MIN,
  PROMOTE_RATE × mid_size)` ≈ 5–6 promotions/yr (vs. previously
  unbounded), so internal promotion cannot silently absorb the whole
  churn — the rest must come from external hiring within `hire_cap`.
- Re-ran all scenarios (`results/scenarios_base.json`,
  `logs/icm_model_base.log`): S0 middle churn ≈ 11–16/yr per level,
  org fill recovers 85% → 95% → 97% over two years; S3a (no external
  recruiting) now degrades the middle tier (exp sup 83% filled, JM 95%)
  because internal promotion alone cannot replace 30% churn — a
  decision-relevant finding.

**Interval / validity:** `PROMOTE_RATE` and `PROMOTE_MIN` are quoted by the
expert as an empirical judgment for a mid tier of order 50–80; ICM's tier
is 70 (20+25+25), inside that range. Treated as the planning value, with
`sweep` support for sensitivity.

## Exchange 3 — interpretation / success criteria (2026-10-02)

**Question (expert_question_3.md):**
> When you look at a company's HR health, what single number tells you
> fastest whether things are getting out of hand?

**Reply (expert_reply_3.json):**
> "Annual churn rate among mid-level managers — when it runs at roughly
> twice the company average and keeps climbing, HR health is deteriorating."

**How the reply became work:**
- Defined the model's **primary output metric** (the one the HR manager
  watches): `mid_to_org_churn_ratio` = (annual mid-tier churn rate) /
  (annual company-wide churn rate), computed per year in
  `code/icm_model.py` and stored in every scenario row.
- Encoded the **decision threshold**: `hr_health = "deteriorating"` iff
  `ratio ≥ 2.0` **and** `ratio ≥ previous year's ratio` (i.e. "runs at
  roughly twice the company average and keeps climbing"); `"stable"` if
  `ratio < 2.0`; `"improving"` otherwise. The 2.0 threshold and the
  "keeps climbing" clause are the exchange-3 input.
- Re-ran all scenarios (`results/scenarios_base.json`): S0 (baseline 18%)
  and S3 (30% in JM+exp sup) both flag **deteriorating** in year 1
  (ratio 2.24 and 2.10, rising), matching the problem statement that
  middle-manager churn is ICM's biggest challenge; S1/S2 (uniform
  25%/35%) stay **stable** (ratio 1.4–1.6) because a uniform high rate
  keeps the mid tier proportionally — the deterioration signal is
  specifically about the *relative* mid-tier burden, not absolute churn.
- This metric is what Tasks 4 and 5 are now answered in: a scenario is
  "HR-healthy" only if `hr_health` stays stable/improving.

**Interpretation rule now used in the submission:** report the
mid-to-org churn ratio and its year-over-year direction alongside every
fill-rate and budget figure; a rising ratio ≥ 2× is the action trigger.
