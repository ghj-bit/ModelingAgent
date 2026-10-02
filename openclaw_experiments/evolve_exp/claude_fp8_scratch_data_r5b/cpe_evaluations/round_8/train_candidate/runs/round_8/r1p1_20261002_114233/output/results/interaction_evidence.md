# Interaction Evidence — Problem 2024_C (Tennis Momentum)

Three expert exchanges. Each reply was converted into a concrete model
parameter, constraint, or design decision before the next exchange. All three
are applied in `code/momentum.py` and `code/predict.py`.

## Exchange 1 — Operational mechanism / causal driver
**Question** (expert_question_1.md): When a player suddenly dominates for a
stretch, what is the main real-world reason — form/confidence shifting, or a
random run of points?
**Reply** (expert_reply_1.json, logs/expert1.log): Both operate, but the
*dominant* driver of a sudden **sustained** swing is a genuine form/confidence
state change (a single high-leverage point — a saved break point, a net-cord
winner, a double fault — flips risk-taking and shot selection for several
games). Short runs (4–6 points) are mostly random noise, amplified by the
serve advantage.
**How it changed the work:** This is the causal-hierarchy answer. It fixed the
momentum model as a **persistent state** (an OU-style relaxation, `M_t =
M_{t-1} + alpha(db_t - M_{t-1})`) rather than a per-point statistic — a single
point cannot create momentum, and it decays slowly. It also fixed the null
hypothesis to test: because short runs are random but sustained swings are a
state change, the coach's "all swings are random" claim is tested by comparing
the *persistent* de-biased momentum's extreme values and swing counts against
a pure i.i.d.-points-with-serve-advantage simulation. Parameter: small `alpha`
(slow time-constant), validated by sweep over alpha ∈ {0.1, 0.2, 0.3}.

## Exchange 2 — Causal hierarchy / dominant observable drivers
**Question** (expert_question_2.md): What on-court signs tell you the flow of
play is about to shift?
**Reply** (expert_reply_2.json, logs/expert2.log): The reliable precursors are
serve-quality drift (first-serve % dropping, slower second serves, more double
faults), an error-type change (unforced errors on routine balls), return
depth/position, body language, point-length/rally pattern (losing long rallies),
and score context (a break point, a long tight game). Crucially: **a single cue
is weak; several together are meaningful.**
**How it changed the work:** This fixed the *feature set* for the swing
prediction model (task 3) and its structure. `code/predict.py` builds a
**combined** precursor score from several weak cues (leading player's recent
unforced-error rate, double-fault rate, winner rate, recent rally-length
z-score, and break-point context, plus the de-biased momentum edge) rather than
any single indicator. The learned sign pattern matches the reply: the leading
player's *rising* errors (UE, DF) and *falling* winner rate, plus a long
rally, and no break point, are what foreshadow the flow reversal.

## Exchange 3 — Decision-relevant uncertainty threshold
**Question** (expert_question_3.md): If a number showed one player winning
about 60% of recent points, would you treat it as a real lead, or nothing
special?
**Reply** (expert_reply_3.json, logs/expert3.log): Nothing special on its own —
the server wins roughly 60–70% of his own points, so a 60% recent share is
close to the serve baseline and carries little signal. It becomes meaningful
only when it **departs from the serving baseline** and **persists across
games** (e.g. a returner winning ~60% against serve, or holding ~60% across
several of the opponent's service games).
**How it changed the work:** This set the *threshold* and the de-biasing rule.
The metric is measured **against the serve baseline**, not as a raw share:
`db_t = m_t - b_serve` where `b_serve = +b` if player 1 is serving, `-b` if
player 2 is serving. This removed the server's built-in advantage before
declaring a "lead." The baseline `b` was then *calibrated from the dataset
itself* (target 1701: p1-server 0.627, p2-server 0.598 → b = 0.66; all-match
first-serve 0.766, second-serve 0.55), which lands inside the 60–70% range the
expert quoted — an independent confirmation. A "lead" is reported only when the
de-biased, *persistent* momentum is nonzero, and the random-null comparison
(Exchange 1) quantifies whether a given value is above what chance alone
produces.

## Summary of what each exchange supplied
| Exchange | Supplied | Where it lives in the model |
|---|---|---|
| 1 | Momentum = persistent form state, not coin noise; short runs random, sustained swings real | OU relaxation `M_t`; null = i.i.d. points with serve advantage |
| 2 | Swing precursors = several combined weak cues (serve drift, errors, rally length, break context) | Combined precursor score in `predict.py` (6 features) |
| 3 | 60% ≈ serve baseline = ordinary; lead must depart baseline AND persist | De-biasing `db_t = m_t - b_serve`; calibrated b = 0.66; persistence threshold |

No reply text is reproduced into the submission; only the values, constraints,
and design decisions travel.
