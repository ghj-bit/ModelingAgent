# Expert Interaction Evidence — Task 2017_D (TSA checkpoint)

Three exchanges, one question each, in the order the policy requires (data
provenance → structural assumption → interpretation threshold). Each reply is
recorded and the specific model change it drove.

## Exchange 1 — Data provenance

**Question** (`expert_question_1.md`): Why do several log columns trail off with
many blanks partway through the day, and does that make the recorded rows a fair
picture of a normal day or biased toward the quiet early period?

**Reply (summary, `expert_reply_1.json`)**: Logging is manual (an officer logs
timestamps at one station), not sensor-driven. Recording stops when that officer
rotates off, is pulled to another lane, or the checkpoint shifts to a busier
configuration. The surviving rows are therefore **biased toward the quiet early
period** and under-represent exactly the peak congestion the problem is about.
Treat them as a partial early-day sample, not a fair full-day picture.

**Effect on the work** (concrete):
- The measured early-day rates (Pre-Check λ≈6.53, Regular λ≈4.63 pax/min; belt
  "time to get scanned" mean 28.6 s) are used only as the **low-load slice** to
  calibrate *service times and process structure*, never as the peak rate.
- Peak arrival rates are instead calibrated from an external congestion anchor
  (published O'Hare-era checkpoint wait level) rather than by scaling the early
  rates — see the parameter table in `solution.json`.
- A data-handling assumption is recorded: trailing missing values are a
  staffing/observation artifact (exchange 1), so columns are truncated to their
  valid prefix (arrival columns full length; process-time columns to their last
  valid row) and no imputation is applied.

## Exchange 2 — Structural assumption

**Question** (`expert_question_2.md`): Given the rows only cover the quiet early
period, is it reasonable to scale the measured early rates up to model the busy
peak, or does the way passengers actually arrive make that scaling unreliable?

**Reply (summary, `expert_reply_2.json`)**: Scaling up is unreliable. Arrivals
are **strongly non-homogeneous** — they track the flight departure schedule,
producing sharp banks of departures, plus day-to-day variation. The quiet period
is a low-rate regime with regular, independent arrivals; the peak is a high-rate
regime where arrivals **cluster in bursts**. A linear scale-up understates both
the peak queue length and the variance. Use the early data for service times and
process structure, but model the peak with a **time-varying arrival profile tied
to flight schedules**.

**Effect on the work** (concrete):
- The simulator (`model.py: simulate_tail_wait`) uses a **piecewise, peak-shaped
  arrival profile**: a low baseline rate (45% of the peak) for most of the window
  plus a 45-minute departure-bank surge at the peak rate, instead of a constant
  rate. This directly implements the "non-homogeneous, flight-driven peak"
  instruction.
- The `iat_cv_mult` knob models burstiness (higher CV = more door-bunching),
  which is the variance-reduction lever in the cultural sensitivity (part c).
- The calibration target is set at a high-but-stable utilization (ρ≈0.85 for the
  regular pool), i.e. the congested regime the expert describes, not a scaled
  constant rate.

## Exchange 3 — Interpretation threshold

**Question** (`expert_question_3.md`): When judging how well a checkpoint is
doing, which single number matters most to passengers deciding how early to
arrive — typical wait, worst-case wait, or person-to-person spread — and roughly
what level of it means the checkpoint is badly failing travelers?

**Reply (summary, `expert_reply_3.json`)**: The **worst-case (upper-tail) wait**
matters most, because passengers plan around the bad day to avoid missing a
flight; a good average with an occasional 45–60 min blowup still forces everyone
to pad their arrival. A checkpoint is **badly failing travelers when the
worst-case wait regularly reaches ~30–45 minutes or more**; typical waits of
10–20 min are tolerable. It is the tail that drives behavior.

**Effect on the work** (concrete):
- The **decision metric** is the 95th-percentile (upper-tail) wait of the
  peak-window, not the mean; `model.py` reports `p95_worst` (max across lane
  classes) as the pass/fail number.
- The **failure threshold** is `FAIL_LO_MIN = 30` (the lower bound of the expert's
  30–45 min band); a scenario "passes" only if its worst-class p95 < 30 min.
- Scenario D (staffing Pre-Check to 4 lanes) is the configuration that brings the
  worst-class p95 down to the ~30 min threshold, and is the recommended policy.

## How the replies became parameters/constraints

| Reply element | Where it enters the model | Value/range | Interval of validity |
|---|---|---|---|
| Early rows = low-load, biased sample (E1) | rates used only for service-time calibration, not peak | λ_early 4.63–6.53 pax/min; belt 28.6 s | quiet early period |
| Non-homogeneous, bursty peak (E2) | peak-shaped arrival profile; iat_cv_mult knob | 45-min surge at peak rate; CV 1.0–1.6 | a departure-bank peak |
| Upper-tail wait is the metric; ~30 min failure band (E3) | p95 worst-class pass/fail; FAIL_LO_MIN=30 | threshold 30 min (band 30–45) | per-trip decision |

No expert sentence is reproduced in `solution.json`; only the values,
constraints, and thresholds above travel into the submission.
