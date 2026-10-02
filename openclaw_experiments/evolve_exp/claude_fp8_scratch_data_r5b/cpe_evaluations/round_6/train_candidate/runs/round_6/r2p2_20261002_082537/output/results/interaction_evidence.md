# Interaction Evidence — 3 expert exchanges

The consultation followed the interaction strategy: Exchange 1 isolated the
data-generation selection mechanism, Exchange 2 validated the temporal/state
structure, Exchange 3 set the bias-aware interpretation threshold. Each reply was
turned into a concrete constraint in the model before the next exchange.

## Exchange 1 — Selection mechanism (missing enrichment fields)

**Question (expert_question_1.md):** Are missing serve-speed values in the Wimbledon
point data because the equipment only records "big" points, making unrecorded ones the
ordinary points — or is it random?

**Expert reply (paraphrased, not copied):** Neither extreme. The dominant cause is
*selective operator/system logging of a subset of shots*. Coverage is driven by which
matches/points were charted in detail; it is patchy and clustered by match and by
stretches within a match — not tied to point importance, and not independent per-point
dropout. The unrecorded points are an **availability-biased subset**, not a meaningful
"ordinary points" sample and not a clean random sample. Missingness is informative about
data collection, not about the point's importance.

**How the reply changed the work:**
- Data-cleaning decision: the four enrichment fields (`speed_mph`, `serve_width`,
  `serve_depth`, `return_depth`) were **excluded from the momentum computation** and
  treated as uninformative about point quality. The momentum model uses only the 15 core
  score/event fields, which were verified 100% complete.
- Validation run (`eda_clean.py`): confirmed the mechanism empirically — serve-speed
  coverage per match ranges from 0.0 (some matches fully unlogged) to ~0.99, with only
  ~16 state-changes of coverage per match on average, i.e. coverage comes in stretches,
  matching the operator-logging (availability) signature rather than per-point random
  dropout. This confirmed we could safely ignore the missing enrichment values without
  biasing the momentum signal.
- Interval/condition: the exclusion holds for the entire dataset; it is a structural
  feature of how the data was generated, not a match-specific artifact.

## Exchange 2 — Temporal/state structure (what a "swing" really is)

**Question (expert_question_2.md):** When a player wins several points in a row then fades,
is that usually a temporary dip, a real shift, or just chance?

**Expert reply (paraphrased):** Most apparent momentum swings are *temporary fluctuations
plus normal run-to-run variation*, not a permanent change in who is better. Genuine
lasting shifts within a match are rare. Distinguishing evidence: (i) duration — a real
shift persists across multiple games and a set boundary, while a run of 3–5 points is
common by chance; (ii) serve-hold structure — because the server wins most points, a real
shift shows as *breaks of serve* and *holds under pressure (saving break points)*, not raw
point streaks; (iii) quality — a real shift involves the opponent winning the "big" points
and the previously-dominant player losing points on their own serve.

**How the reply changed the work:**
- Model-structure decision: momentum was computed at the **game/scoreline level**, not
  from raw point streaks. The signal `sig` combines a serve-normalized point residual with
  explicit break-of-serve events (`game_resid`) and break-point-save events
  (`save_resid`), so a "run" of points only registers as momentum if it changes the
  scoreline via breaks or holds — exactly the structure the expert said distinguishes real
  shifts from noise.
- Parameter constraint: runs of 3–5 points were *not* treated as signal; this set the
  floor for what the metric counts (game-level events), and it justified the point-level
  randomness test being conducted at the point layer where streaks were shown to be
  chance.

## Exchange 3 — Bias-aware interpretation threshold

**Question (expert_question_3.md):** How much of a sustained advantage — how many games or
breaks in a row — would make you truly believe the match's balance has shifted, not just a
lucky stretch?

**Expert reply (paraphrased):** Points alone essentially never qualify (runs of 3–5 are
routine; even 6–8 consecutive points carry little weight). The threshold: a run of
**3–4 consecutive games including at least one break of serve**, or **two breaks of serve
in a set**, or a decisive set (6–2 or better) carried into the next. A single break or any
point streak is within normal variation.

**How the reply changed the work:**
- Decision rule: the swing-detection rule in the model flags a "momentum shift" only at the
  game/break level — specifically requiring a break of serve, with a stronger signal at two
  breaks in a set. A single break and any point streak are classified as noise.
- Interpretation threshold: model outputs (the momentum trace) are reported as a reliable
  signal of "who is better now" only when backed by a game-level event (break/hold under
  pressure); otherwise the value is treated as consistent with the chance baseline. This is
  why the random-momentum tests (point and game level) and the swing-prediction AUC are the
  central results: the bias-aware reading is that swings are mostly chance, and the metric's
  value is in tracking the *scoreline-anchored* state, not in forecasting reversals.

## Summary of what traveled into the submission

| Exchange | Value / constraint that entered the model | Used in |
|---|---|---|
| 1 | Enrichment fields (speed/width/depth/return_depth) are availability-biased → excluded; core 15 fields complete | data cleaning, momentum model input set |
| 2 | Real shifts = breaks of serve + holds under pressure; 3–5 pt runs = chance | momentum computed at game level with break/save events |
| 3 | Threshold for a real shift = 2 breaks in a set, or 3–4 games incl. a break; single break/point streak = noise | swing-detection decision rule + interpretation threshold |

No expert sentence was copied into the submission; only the operationalized values
and decision rules above were integrated.
