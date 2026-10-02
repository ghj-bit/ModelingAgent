# Expert Interaction Evidence — MM-Bench 2015_C (ICM Human Capital Model)

Three exchanges, one question each, in order. For each: the question asked, the
reply received, and how the reply became a parameter, constraint, or decision
rule in the model (with where and how it is used).

---

## Exchange 1 — mid-level churn rate

**Question (expert_question_1.md):**
"In a mid-size company, which kind of employee is most likely to quit after a few years?"

**Reply (expert_reply_1.json, in substance):** The mid-level employee — junior
managers and experienced supervisors — is the one most likely to quit after a
few years: proven competence, portable skills, and a blocked promotion path.
Early-career staff leave sooner for different reasons; senior staff rarely
leave. The expert explicitly said mid-level turnover typically runs well above
the company average — **around twice the overall rate**.

**How it became work:** This reply is the source for the mid-level churn
multiplier in `code/model.py`. The company-wide churn rate is 18% (given in the
problem), and the two mid-level tiers (Junior manager, Experienced supervisor)
were set to **2 × 18% = 36%** in the `churn_rate()` function (MID = {JM, ES}).
This is a parameter, not an assumption the model derived: the 2× value and the
identification of exactly which tiers are "mid-level" come from this exchange,
and they hold over the range of churn scenarios tested (18%, 25%, 35% all-level
and the 30% mid-level task). The problem statement itself mentions the mid-level
rate is "twice the average rate of the rest of the company" for issue 4; the
exchange confirmed that is the right reading and the right two tiers, and was
used to keep 2× as the constant rather than re-estimating it.

**Where it is used:** `code/model.py`, `MID = {"JM", "ES"}` and
`churn_rate()` — every simulation in this run.

---

## Exchange 2 — does promoting a few calm the rest?

**Question (expert_question_2.md, building on exchange 1):**
"You noted mid-level staff churn most when promotion stalls. In practice, does
promoting a few good ones really calm the rest of that group down?"

**Reply (expert_reply_2.json, in substance):** No — not much, and not for long.
Promoting a few visible people gives a short morale signal but the effect is
weak and fragile: it is zero-sum and visible (everyone else sees the ladder is
still closed to them), it does not change the structural fact that higher-level
slots are few and fixed, and repeated selective promotion can backfire by
raising perceived unfairness and cynicism, which *raises* churn. It only calms
the group when paired with genuine expansion of advancement paths (lateral
moves, role enrichment, pay progression without title change).

**How it became work:** This reply bounded the "promotion as a retention tool"
option in the task-5 scenario (promote only qualified employees, no external
recruiting). Rather than model internal promotion as reducing the mid-level
churn rate meaningfully, I added a small, one-year-only morale term: a
`--retained` fraction of mid-level churn avoided in year 1, set to 10%
(weak, short-lived, exactly as the reply described), decaying to 0 in year 2
(because the effect is not durable). Without it, the scenario would have
overstated the benefit of "promote qualified people." The 10% is a parameter the
reply supports in value and direction; the decay-to-zero is a constraint the
reply directly states ("not for long").

**Where it is used:** `code/model.py`, `retained` argument to `simulate()` and
`churn_rate()`, run as `--retained 0.10` in the task-5 scenario
(`logs/model_task5_final.log`). The contrast with `--retained 0` shows the
difference is small (2-yr fill 0.743 vs 0.741), consistent with the reply's
"weak" characterization.

---

## Exchange 3 — what happens to the team covering a long vacancy?

**Question (expert_question_3.md, building on exchange 2):**
"If you can't fill key roles for months, what usually happens first to the rest
of the team that covers them?"

**Reply (expert_reply_3.json, in substance):** First overload and role blur —
the remaining team absorbs the missing person's work informally, with longer
hours, deferred work, and shortcuts on non-urgent duties. Then morale drops and
stress rises because the gap feels invisible and unpaid to management. If the
vacancy persists for months, the strongest performers — the same mid-level, most
marketable people — start looking elsewhere, so a persistent vacancy triggers
**secondary churn** rather than being absorbed quietly.

**How it became work:** This reply added a new dynamic process to the model that
was not in the first version: **vacancy-triggered secondary churn**. I added a
`SECONDARY_CHURN = 0.05` rate applied to mid-level headcount, proportional to
the number of seats left unfilled (below the 85% steady-state fill) at the end
of the previous year. The 5% is a parameter I set as a small per-unfilled-seat
effect on the most marketable tiers, matching the reply's "strongest performers
start looking elsewhere" mechanism and its emphasis that this is a *secondary*
(effect smaller than the primary churn) but real and compounding. The
proportionality to unfilled seats is a constraint the reply implies ("if the
vacancy persists for months").

**Where it is used:** `code/model.py`, `SECONDARY_CHURN` and the `sec` term in
`churn_rate()`/`simulate()`. It is active in every scenario and is what makes
the 35% churn case worse than a naive one-shot calculation would suggest
(2-yr fill drops to 0.649 with secondary churn vs ~0.654 without), and it
drives the task-5 finding that unfilled mid-level seats cascade into further
departures.

---

## What the exchanges did not do

- No exchange asked for, or supplied, a formula, derivation, or computation.
- No reply is copied verbatim into `solution.json`; only the values and
  mechanisms above (2× mid-level rate, weak/short promotion morale effect,
  vacancy-triggered secondary churn) travel into the model, in my own
  formulation.
- The three replies are consistent with each other: mid-level staff are the
  churn hotspot, promotion alone does not fix it, and unfilled seats make it
  worse.
