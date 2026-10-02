# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — Task 2017_D (TSA Checkpoint Throughput)

Three exchanges, one question each, in the order the policy requires.
Question files: `logs/operator_feedback/expert_question_N.md`
Reply files: `logs/operator_feedback/expert_reply_N.json` (controller-owned)

---

## Exchange 1 — Data provenance / completeness

**Question (as asked):** "In the recorded data, why are some passengers'
processing times missing — equipment down, staff away, or something else?"

**Expert reply (paraphrased, not verbatim):** The blanks are a
*data-recording artifact*, not operational downtime. The ID-check and X-ray
columns are per-officer / per-station splits (officer 1 vs. officer 2), so a
passenger processed at one station leaves the other column blank by design.
Additional gaps come from officers skipping logs during congestion, passengers
bypassing a step (e.g. Pre-Check skips some procedures), and manual-entry
dropouts. The expert flagged this as an empirical judgment from the column
design, not a verified fact.

**How the reply became work:**
- Treated the missingness as *structural*, not a signal of an idle station.
  Consequence in `clean_estimate.py`: **no interpolation** of the blank cells;
  column statistics (mean/median/p10/p90) computed on observed values only.
  Interpolating structural blanks would have fabricated service times and
  biased the bottleneck location.
- The two-officer ID columns (ID Check 1 / 2) justified modeling **two ID
  officers sharing the regular lane group** in `simulate.py` (`n_id = 2` for
  the regular group, 1 for Pre-Check), rather than a single serial ID gate.
- The "officers skip logging under congestion" note is the operational reason
  the ID columns are complete only for the first ~10 rows and sparse after:
  it is why the observed inter-call intervals (~8–15 min) reflect a
  congestion window, not the per-passenger document-check time. This drove the
  decision to calibrate ID *document work* (~30 s) separately from the logged
  *call interval*, rather than using the raw column as a service time.

**Interval / validity:** applies to the 58-row observation window
(~0–595 min on the regular-lane clock). The structural-blank interpretation
holds for the officer-1/2 split columns specifically; the arrival-time columns
have a different gap pattern (trailing NaNs where a lane simply had no more
arrivals recorded).

---

## Exchange 2 — Key structural assumption (the bottleneck)

**Question (as asked):** "At a real checkpoint, which single step most often
becomes the long line you see forming?"

**Expert reply (paraphrased):** The **X-ray / baggage screening step**
(conveyor + secondary search) is the visible long line. It is the slowest and
most variable step per passenger: the service time is set by the *slowest* of
a passenger's several bins, not the average, and a flagged bag triggers a
secondary search that blocks the lane for minutes. The walk-through scanner
(mmWave / metal detector) is comparatively fast and rarely the binding
constraint. ID check can queue but is quick per passenger and usually
staffed to match; the X-ray lane is where throughput is genuinely
capacity-limited and where variance accumulates. Again an empirical judgment
from process structure, not a measured figure.

**How the reply became work:**
- Set the **X-ray conveyor as the modeled binding constraint** and the
  primary variance source in `simulate.py`: serial bin throughput
  (`xray_bin` × `bins`) on a shared FCFS conveyor, with a **flagged-bag
  secondary search** (`flag_prob`, `flag_time = 150 s`) added in series —
  exactly the "slowest of the bins + occasional lane-blocking secondary
  search" the expert described.
- The "service time = slowest bin, not average" point is implemented by
  charging the full `bins × xray_bin` in series (no overlap), rather than
  parallelizing a passenger's bins.
- It justified the modeling choice that the body-scan gate is fast and
  non-binding (short `body_scan`, one gate per lane) so that the X-ray queue
  — not the scanner queue — is where wait time and its variance accumulate.
  Validation: in every run the `mean_xray_queue_min` is the dominant
  stage-queue term, confirming the bottleneck sits where the expert said.

**Interval / validity:** holds for the standard US checkpoint process in the
problem statement (Zones A–D). It is the structural assumption linking the
data (per-station timestamps) to the model output (total wait + variance);
if the true bottleneck were the ID stage instead, the modification results
below would reorder.

---

## Exchange 3 — Interpretation context / decision threshold

**Question (as asked):** "How many minutes of checkpoint wait would most
travelers call too long before they start feeling upset?"

**Expert reply (paraphrased):** Most travelers start feeling upset around
**20–30 minutes** of total checkpoint wait; below ~10 min almost no one
complains, and beyond ~30–45 min the experience becomes a common source of
anger and missed-flight anxiety. Not a sharp threshold — it shifts with
context (tolerated longer when arriving early, when the delay is explained,
or when everyone is delayed equally; less tolerated when the line looks
understaffed or a flight is at risk). An empirical judgment from general
service-waiting norms, not a measured figure.

**How the reply became work:**
- Set two **decision-relevant thresholds** in `simulate.py`:
  `wait_complaint_min = 20` (upset begins) and `wait_hard_min = 45`
  (anger / missed-flight anxiety). These are the metrics the results are
  reported against — `pct_over_20min` and `pct_over_45min` — so that a
  scenario is judged on *actionable* passenger-experience confidence rather
  than on the abstract mean alone.
- The "not a sharp threshold, shifts with context" qualifier is why the
  solution reports the **full wait distribution** (mean, std, p50, p90, p95,
  max) plus both threshold-exceedance rates, instead of a single point
  estimate: a modification can look similar on the mean yet differ sharply
  on the tail that actually drives complaints.
- It framed the recommendation in part (d): target p90/p95 and the
  >45-min tail for variance reduction, since those are the waits the expert
  identified as the anger / missed-flight regime.

**Interval / validity:** a population-level passenger-perception threshold,
used as a reporting/decision yardstick rather than a physical model
parameter; it does not change the queue dynamics, only how the outputs are
interpreted and which of them are decision-relevant.

---

## What did NOT come from the expert (to keep the provenance clean)

- All **service-time calibrations** (divest 150 s regular / 75 s Pre-Check,
  X-ray 20 s/bin, body scan 40 s, belt collect 29 s, ID document work 30 s,
  flag probability 10 %/4 %, flag time 150 s) are calibrated from the
  supplied dataset's observed values and the process description in the
  problem statement — not from any exchange.
- The **arrival rate** (5 pax/min total, 45/55 split) is set from the
  problem statement's 45 % Pre-Check figure and the observed arrival gaps in
  the dataset, chosen to put the regular X-ray stage near capacity
  (ρ ≈ 0.9) so the congestion the expert described is reproduced.
- The Pre-Check **enrollment share** beyond the problem's stated ~45 % was
  sought via the staged `search.py` helper (scholarly + web) but no
  authoritative current figure was retrievable in this environment; the
  model therefore uses the problem statement's own 45 % and notes this as a
  limitation rather than importing an unverifiable number.
