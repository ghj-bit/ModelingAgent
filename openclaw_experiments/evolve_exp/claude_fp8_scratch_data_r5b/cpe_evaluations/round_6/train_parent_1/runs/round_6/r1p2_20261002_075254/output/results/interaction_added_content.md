# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — Problem 2024_C (tennis "momentum", MM-Bench)

Three exchanges, one question each, in order. The reply of each was converted into a
concrete parameter, equation change, or decision rule before the next exchange.

## Exchange 1 — Data provenance

Question (file: `logs/operator_feedback/expert_question_1.md`): in the point-by-point
data, when shot-detail columns (ace, winner, unforced error, net point, distance run,
serve speed/width/depth, return depth) are zero/blank, does that mean the event
genuinely didn't happen, or the recorder didn't log it — and is the rest of the data
still representative?

Expert reply (summarized in my words): the shot-detail fields are optional,
partially-coded annotations; a zero/blank mostly means "not logged for that point,"
not "event absent." Coverage is partial and inconsistent, and missingness may correlate
with point type or match. The core scoring/outcome fields (point_victor, server,
serve_no, scores, game/set victors, points won) are structurally required to advance
the match and are reliably complete. Shot details are usable for aggregate tendencies
but not as a complete per-point event record.

How the reply changed the work (constraint, applied before Exchange 2):
- The match-flow metric (Task 1) and all randomness tests (Task 2) are built **only**
  from the core outcome fields; no zero in a shot-detail column is interpreted as an
  event.
- The swing-prediction features (Task 3) use the outcome fields plus `rally_count` and
  distance-run columns treated as **present/absent-indicator features**, never as
  "0 = event did not happen." A missing `speed_mph` is dropped from serve-speed
  statistics rather than counted as a zero-speed serve.
- Data-cleaning statement (step 2 of the workflow) records the fields that were
  checked for missingness and how each was handled.

## Exchange 2 — Key structural assumption

Question (file: `expert_question_2.md`): is a run of elevated recent point-win share
(a rolling-window metric, baseline-adjusted for server) a real short-lived state a
player can hold for minutes, or is what looks like a hot streak just the random
scatter a constant-skill null would produce?

Expert reply (in my words): both are real and not mutually exclusive, but the burden of
proof sits with the "hot streak" reading. A rolling share over a 10–20-point window has
large null variance (roughly 0.11–0.16 standard deviation at 20 points), so runs above
baseline appear routinely by chance. Genuine short-lived form shifts do exist in
tennis (a few minutes of elevated serving/return/error-avoidance). A single elevated
window cannot distinguish real momentum from noise: the claim needs persistence
(does the elevation survive beyond the window that generated it?) or a null-model
comparison.

How the reply changed the work (equations/tests, run before Exchange 3):
- The metric is declared a **candidate signal**: Task 1 reports the flow value but does
  not itself assert "momentum exists."
- Task 2 is a formal null test: (a) a serve-adjusted baseline Bernoulli model of point
  outcomes; (b) permutation / circular-block bootstrap of point outcomes that breaks
  temporal structure while preserving per-server outcome rates; (c) compare the
  observed long-run length (points of same victor) and the observed maximum
  deviation of the rolling flow from its null distribution. The observed statistic
  is significant only if it exceeds the 95th percentile of the null.
- A **persistence test** is added: does flow elevation in window t predict further
  elevation in t+1 beyond the null? This is the persistence check the expert
  named, and its outcome (yes/no, with effect size) is reported in Task 2.
- The reported effect sizes carry the expert's null-variance figure as a sanity check.

## Exchange 3 — Interpretation context / decision threshold

Question (file: `expert_question_3.md`): how confident must a coach be, mid-match,
before acting on (a) "who is ahead on recent form" or (b) "the flow is about to flip"
— and in practice, what separates a real now from a false one?

Expert reply (in my words): no single universal threshold; it depends on the cost of a
wrong action versus missing a real shift. Practitioner bars: for "who's ahead," the
signal must be sustained across a meaningful stretch (roughly a set, or at least
several games) and large enough to exceed normal scatter — a one- or two-game edge in
recent form is treated as noise. For "about to flip," a much weaker claim: coaches
require corroborating evidence (behavior, serve quality, error type, a specific
trigger such as a long game, a break point, or a change of ends) — a lone statistical
blip is ignored. What separates real from false in practice: (1) persistence — the
signal survives beyond the window that generated it; (2) corroboration — it agrees
with something observable; (3) magnitude — clearly beyond random scatter; (4)
context — it aligns with known match dynamics. If a signal lacks persistence and
corroboration, treat it as noise; if it has both, act with a **low-cost adjustment**
(tactical tweak, reset routine), not a drastic change, because even genuine shifts
are short-lived and uncertain.

How the reply changed the work (decision rules, applied to Tasks 1–3):
- Task 1 flow is annotated as *actionable* only when its magnitude exceeds the
  null's 95th percentile **and** it persists (holds across the next several games).
  A one- or two-game recent-form edge is labeled noise, per the reply.
- Task 3 swing predictors are reported with two gates before a swing is flagged:
  (i) the model's probability exceeds a threshold chosen so that flagged swings are
  rare (precision-oriented, cost of a false alarm > cost of a miss, per the
  reply's cost framing), and (ii) corroboration — the flag coincides with an
  observable trigger the reply lists (break point, long game, change of ends,
  server's first-serve % dropping in the window). Flags without corroboration are
  reported as "candidate only."
- Coach advice in the solution (Task 4 memo content) is framed as low-cost
  adjustments contingent on persistence + corroboration, not as dramatic
  mid-match changes.
- The decision rule is stated explicitly in Task 3's outcome analysis with its
  operating point (the probability threshold and the corroboration rule), so a
  reader can see where the threshold came from.

## Provenance note

No external empirical value is needed beyond the supplied dataset: baseline point
probabilities, serve rates, break-point frequencies, and the null distributions are
all estimated from the data itself. The parameter table in
`mathematical_modeling_process` therefore lists data-derived estimates (with the
matches they were computed over) and the two expert-supplied items: the
persistence/corroboration decision rule (Exchange 3) and the candidate-signal
framing (Exchange 2). No values from memory were used.
