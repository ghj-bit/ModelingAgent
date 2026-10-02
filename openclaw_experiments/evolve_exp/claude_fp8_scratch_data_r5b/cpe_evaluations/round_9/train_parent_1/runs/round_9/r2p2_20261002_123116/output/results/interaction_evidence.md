# Expert Interaction Evidence — Problem 2017_C (MM-Bench)

Three exchanges, one question each. Each reply became a concrete parameter or
decision rule in the model (code/model.py) before the next exchange. No reply
text was copied into solution.json; only the extracted values, constraints, and
equations were carried forward.

---

## Exchange 1 — Operational mechanism (input structure)

**Question (expert_question_1.md):**
"On these Seattle-area highways, is the daily traffic count spread evenly over
the day, or does most of it bunch into a few peak-hour rush windows?"

**Reply (expert_reply_1.json):** The daily count is strongly peaked; the AM and
PM commute windows (roughly 6–9 a.m. and 3–7 p.m.) carry a disproportionate
share, with the peak hour typically around 8–10% of the daily total and the two
peak windows together often 25–35%. The daily average is not a good proxy for
the capacity-critical flow; the peak-hour volume is what drives congestion.

**How it changed the work (before Exchange 2):** I converted each segment's
daily AADT to a peak-hour demand using **pf = 0.09** (interval [0.08, 0.10]),
so the model's volume-to-capacity ratio x = (AADT·pf) / (lanes·c0) is evaluated
on the peak hour, not the daily average. This is the single input that makes
the baseline congestion (all four corridors in LOS F at peak) physically
meaningful. Recorded in solution.json subtask 1 parameter table with this
exchange as the source.

---

## Exchange 2 — Causal hierarchy (dominant driver of the SD effect)

**Question (expert_question_2.md):**
"Do a few self-driving cars among normal traffic help much, or do they need a
cooperating group first?"

**Reply (expert_reply_2.json):** Mainly the latter. A few isolated self-driving
cars mixed into human-driven traffic produce little capacity gain; the clear
benefit comes when they can cooperate (platooning, short coordinated headways,
smoother merging), which requires a meaningful cluster, not a scattered few. The
effect is strongly nonlinear in the SD share: negligible at low percentages,
pronounced only once enough cooperating vehicles are present to form platoons.

**How it changed the work (before Exchange 3):** I built the self-driving
capacity effect as a **nonlinear smoothstep** in the SD share p:
G(p) = g_max·S((p − p_th)/w), S(t) = 3t² − 2t³, with p_th = 0.25 (the
"meaningful cluster" onset, interval [0.20, 0.30]) and w = 0.15 (onset width,
[0.10, 0.20]). G(p) is ≈0 below p_th and saturates to g_max above p_th + w —
exactly the expert's "negligible at low p, pronounced at high p" with no
artificial cliff. I set g_max = 0.45, bounded above by the literature result
that full platooning can roughly double throughput (DOI 10.1016/j.trc.2017.01.023).
I then ran code/model.py and swept p_th and g_max, which produced the central
result that **all-lane mixing alone has no tipping point to free flow at any
plausible parameter** — a conclusion the expert's nonlinearity made the model
able to state (a linear model would have predicted a low-p tipping point).
Recorded in solution.json subtask 2 parameter table with this exchange as the
source.

---

## Exchange 3 — Decision-relevant uncertainty threshold

**Question (expert_question_3.md):**
"For a self-driving lane to be worth building, what cut in peak-hour delay
would count as a real win?"

**Reply (expert_reply_3.json):** A real win is a substantial cut, not a marginal
one: a dedicated lane is worth building if it reduces peak-hour delay for the
affected traffic by roughly 20–30% or more, and/or raises peak-hour throughput
enough to move the bottleneck back toward free flow. Below about 10% the gain is
within normal day-to-day variation and would not justify the lost general-purpose
lane capacity. The threshold should be judged on the peak window, not the daily
average.

**How it changed the work (final exchange):** I encoded the decision rule
**R >= D_thr = 0.25 → "worth building"; R >= D_no = 0.10 → "marginal"; else
"no-credit"**, where R = (x_mixed − x_ded) / x_mixed is the relative peak-hour
congestion reduction of the dedicated-lane scenario versus the all-lane-mixed
baseline at the same p. This threshold is what turns the model's x-values into
the Governor's answer: the dedicated lane is no-credit at p = 10–50%, "worth"
at p ≥ 70%, and it is net-negative (worsens human traffic) at p < 50% because it
strips a general-purpose lane before the SD fleet is large enough to fill the
express lane. The "judge on the peak window, not the daily average" instruction
is why the metric is peak-hour x, consistent with Exchange 1. Recorded in
solution.json subtask 3 parameter table with this exchange as the source.

---

## Summary of what each reply became

| Exchange | Value / constraint adopted | Where it is used |
|----------|----------------------------|------------------|
| 1 | pf = 0.09 (interval [0.08, 0.10]) | AADT → peak-hour demand; baseline x and all LOS |
| 2 | G(p) smoothstep, p_th = 0.25, w = 0.15, g_max = 0.45 | Self-driving capacity gain; no-free-flow result |
| 3 | D_thr = 0.25, D_no = 0.10 | Dedicated-lane "worth building" decision rule |

All three replies are used as calibrated inputs; none stands in for a
derivation, computation, or result, and none was copied verbatim into the
submission.
