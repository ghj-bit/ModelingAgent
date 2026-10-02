# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — 2017_D (airport security checkpoint)

Three expert exchanges were attempted, one per round, exactly as the policy
requires. The question files, controller request/reply files, and outcomes:

## Exchange 1 — data provenance and completeness

- **Question** (`logs/operator_feedback/expert_question_1.md`): why do the
  second ID-checker, second X-ray scanner and belt-retrieval columns stop
  being recorded partway through the file, and can the remaining records be
  treated as a fair picture of normal passenger flow?
- **Status**: the controller created `expert_request_1.json` from the
  question, but the expert API call failed
  (`expert_reply_1.json`: `ok=false`,
  `error: RuntimeError('Direct human-expert API call failed')`).
  **No expert answer was received.**
- **How the work handled the gap**: the missing columns were treated as
  uninformative (see data-cleaning notes below). The model relies only on
  the consistently recorded columns (arrival times, ID-check durations,
  MMW exit times, belt-retrieval times), and every derived rate carries an
  uncertainty band in `solution.json`. No calibration from an expert
  exchange was possible, so none is claimed.

## Exchange 2 — key structural assumption (builds on Exchange 1)

- **Question** (`logs/operator_feedback/expert_question_2.md`): since the
  service-time records cover only the first part of the morning, is the rest
  of the day's passenger stream steady enough for the measured rates to stand
  in for typical flow?
- **Status**: the controller never created `expert_request_2.json` within the
  70 s handshake window; repeated waits timed out. **No expert answer was
  received.**
- **How the work handled the gap**: steadiness is treated as an assumption
  (stated in `solution.json`), and its consequences are bounded by a
  sensitivity sweep over demand multipliers (1.0–2.0× arrival rate) and
  service-time CVs. The bottleneck identification is robust across that
  range, so the assumption does not change the conclusions.

## Exchange 3 — interpretation context (builds on Exchanges 1–2)

- **Question** (`logs/operator_feedback/expert_question_3.md`): given that the
  belt-retrieval data is the thinnest and the belt is the slowest step, how
  long a queue would passengers start to treat as a real problem rather than
  normal?
- **Status**: the controller created no `expert_request_3.json`; waits timed
  out. **No expert answer was received.**
- **How the work handled the gap**: decision-relevant thresholds are set from
  the data itself (e.g. a modification is recommended only if it cuts the
  95th-percentile checkpoint time by at least one order of magnitude, which
  it does) and from operational plausibility (staffing must not raise
  utilization above ~85%). These thresholds are stated explicitly in
  `solution.json` as the interpretation context, with their source noted as
  the model's own validation rather than an expert exchange.

## Honest summary

None of the three exchanges produced an expert reply: one failed at the
expert-API level and two were never picked up by the controller. Consequently,
**no parameter in `solution.json` is sourced from an expert exchange.** Every
empirical parameter is sourced from the task's own dataset (with the
intervals over which it holds) or from a public reference where a value could
not be derived from the data. The gaps that the exchanges were meant to close
(data representativeness, steadiness, decision threshold) are instead closed
by stated assumptions plus sensitivity analysis, as documented above.
