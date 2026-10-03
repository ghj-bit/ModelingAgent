# Interaction Evidence — 2017_ICM_Problem_D

Ten exchanges with the human expert. Each question (≤20 words, common-sense, no
modelling terms) was written to `logs/operator_feedback/expert_question_N.md`, the
staged helper returned a reply, and the reply was turned into work before the next
exchange. Below: the question, a condensed form of the reply, and the concrete
parameter / equation / test the reply produced. No expert wording is copied into
`solution.json`; only the value, constraint, or test carried over.

## Exchange 1 — where lines grow fastest
- **Q:** When airport security lines get very long, which single step in the process makes them get worse the fastest?
- **Reply (condensed):** The ID/document check (Zone A) is the step that most amplifies long lines; a single-server, human-paced step every passenger must pass, with variable service time.
- **Work:** Fixed the causal skeleton as two stages in series — an ID stage feeding a screening-lane stage — and made "which stage's utilization reaches 1 first" the bottleneck test. This is the structure of `mm_c.py`; it is validated *against* the data in the bottleneck analysis (the data show the lane stage saturates before the ID stage, so the expert's prior is treated as a hypothesis to test, not a given).

## Exchange 2 — how many officers at the ID check
- **Q:** At a busy checkpoint, is the ID check done by a single officer for everyone, or do several officers each run their own short line?
- **Reply (condensed):** Several officers run parallel short lines; passengers join the shortest. The dataset's two ID-check time columns correspond to two officers working in parallel.
- **Work:** Modelled the ID stage as an M/M/c with c parallel servers (c=2 regular, c=1 Pre-Check), not M/M/1. This is what makes the ID stage non-binding in the base model (rho_id ≈ 0.3–0.6).

## Exchange 3 — what sets the number of open lanes
- **Q:** When a checkpoint gets crowded, what decides how many screening lanes are actually opened at once?
- **Reply (condensed):** Staffing and anticipated volume, not physical lane count. Rule of thumb ≈ 1 Pre-Check lane per 3 regular lanes; lanes are in single digits to low tens; lanes can't open instantly on a surge.
- **Work:** Set the base staffing 3 regular lanes / 2 Pre-Check lanes (≈1:3). "Surge capacity" becomes the headline intervention (Exchange 10), and the "can't open a lane instantly" limitation is recorded as a model weakness (surge must be planned ahead, not reactive).

## Exchange 4 — what a flagged passenger does to the lane
- **Q:** When the X-ray flags a bag or the body scan beeps, what happens to that one passenger, and about how long is the lane blocked?
- **Reply (condensed):** The flagged passenger is pulled to a side area (Zone D) for a hand search / pat-down; the lane keeps moving. Delay to that passenger is on the order of 1–5 minutes.
- **Work:** Modelled secondary inspection as a branch that does **not** block the lane — a flagged fraction leaves the main lane and takes a 180 s (3 min, mid of 1–5) side-service. This is the `FLAG_SVC=180` parameter and the "no lane blocking" decision rule in `des_model.py`.

## Exchange 5 — flag rate
- **Q:** Roughly what fraction of passengers get flagged for a secondary search or pat-down at a typical checkpoint?
- **Reply (condensed):** A few percent — roughly 1–5%, lower for Pre-Check, higher for regular.
- **Work:** Set flag probabilities 5% regular / 2% Pre-Check (upper/lower end of the 1–5% range). These are `FLAG_P_REG=0.05`, `FLAG_P_PRE=0.02`.

## Exchange 6 — peak arrival rate and per-lane throughput
- **Q:** At a busy morning peak, roughly how many passengers reach the checkpoint per hour?
- **Reply (condensed):** ~1,000–2,000/hr at a large checkpoint, 2,000–3,000/hr at a major hub peak. A single lane handles ~150–250/hr.
- **Work:** Calibrated `LANE_REG=18 s` (≈200 pax/hr, mid of 150–250) and `LANE_PRE=12 s` (≈300 pax/hr, Pre-Check faster). Set the peak-demand sweep to 1000 / 1500 / 2000 pax/hr (hub peak). This is the load axis of every bottleneck and intervention run.

## Exchange 7 — do travelers stay put or line-shop
- **Q:** Do travelers in a checkpoint line tend to stay put, or do they watch the other lines and move to the shortest one?
- **Reply (condensed):** Both. Short parallel queues (ID check) → some line-shopping; long committed lanes (Zone B) → essentially no switching.
- **Work:** Gave the cultural model (Exchange 8) its two-regime structure: a `load_balance` lever is meaningful at the short parallel ID stage and nearly inert at the long committed lane stage. This bounds how much behavioral tuning can move the bottleneck.

## Exchange 8 — do mixed-culture travelers queue differently
- **Q:** If travelers from different countries share one checkpoint, do they all queue the same way, or do some try harder to find the fastest line?
- **Reply (condensed):** Not the same. The difference is mainly in how much line-shopping / jockeying / cutting they do, not the physical process. Most visible at the short parallel ID queues; the spread shifts variance more than mean throughput.
- **Work:** Built `culture.py` with three behavioral levers — `load_balance` (fraction joining shortest line), `svc_mult` (service-time multiplier, e.g. slow traveler), `cut` (fraction who edge forward). Ran the five traveler-style profiles (US personal-space, Swiss collective, CN individual, slow, fast). Confirmed the expert's expectation: culture moves **variance (p90) and load-balance, not mean throughput much**.

## Exchange 9 — do Pre-Check and regular back up into each other
- **Q:** When Pre-Check travelers and regular travelers are both waiting, does one group's slowness back up into the other group's line?
- **Reply (condensed):** No — the groups are physically separated (separate queues, lanes, equipment). The only coupling is the shared officer pool (staffing allocation).
- **Work:** Modelled the two channels as **independent** M/M/c queues (no cross-backup), with the shared-officer pool recorded as the only coupling — and the reason "add a Pre-Check lane" (mod2) does not fix the regular lane. This is the structural justification for analyzing the channels separately in `mm_c.checkpoint`.

## Exchange 10 — the single change that cuts worst-line surprises most
- **Q:** Of all the changes a checkpoint can make, which single one do you think cuts the worst long-line surprises the most?
- **Reply (condensed):** Flexible, cross-trained surge staffing that can add an ID position and a lane on short notice — surge capacity rather than a fixed reconfiguration.
- **Work:** Made **surge staffing** (add regular + Pre-Check lanes when a queue builds) the primary intervention, mod3b/mod4 in `mm_c.py`. The result: at R=1500 the base is unstable (lane rho>1); mod3b (+2 reg, +1 pre lane) restores stability with combined sojourn 32.1 s; mod4 (+2 reg, +2 pre lane) gives 28.7 s. This is the quantified version of the expert's recommendation, and the core of the policy recommendations (part d).
