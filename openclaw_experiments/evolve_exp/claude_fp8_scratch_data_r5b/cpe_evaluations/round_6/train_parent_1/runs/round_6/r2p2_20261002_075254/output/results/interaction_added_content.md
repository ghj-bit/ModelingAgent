# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — Task 2024_C (Tennis Momentum)

Three expert exchanges, one question each, in order. Each reply is turned into
concrete work before the next exchange.

## Exchange 1 — Data provenance & completeness

**Question (expert_question_1.md):**
"Is a blank serve-speed entry in a scorebook a missed recording, or left blank for certain points?"

**Expert reply (paraphrased value, not verbatim):** Missing values in the
Wimbledon/IBM point-by-point feed are *structural*, not recording failures.
- Serve speed is populated only for serves that are actually hit and measured;
  it is absent on faults/lets and where radar did not register.
- `winner_shot_type` is populated only when a winning shot is recorded
  (p1_winner/p2_winner = 1); blank on points ending by error, double fault,
  ace, or forced error.
- A blank therefore means "event not applicable / did not occur", **not**
  "the statistician forgot". The data are representative of the underlying
  process for the columns that do carry values.

**How this changed the work (turns into a parameter/constraint):**
1. **Missing-value policy fixed.** Blanks in `serve_width`/`serve_depth`/
   `return_depth`/`speed_mph` (the "NA" codes) and `winner_shot_type`="0" are
   treated as *structurally absent* (event did not occur / not applicable), so
   they are NOT imputed and NOT counted as errors. They are excluded from any
   statistic that needs them (e.g. serve-speed features, shot-type features)
   rather than averaged to a fake value. This is the constraint that governs
   the feature set in the momentum and swing-prediction models.
2. **Data-cleaning rule.** The "NA" string codes are converted to NaN and the
   model reports, per feature, how many points it is defined on, so a reader
   sees exactly which points a feature applies to.

**Verification against the data** (profile2.log / profile5.log):
- 0 duplicated rows, 0 true missing cells after treating "NA"/"0" codes as
  absent.
- `winner_shot_type` is "0" on 5619/7284 points and populated (F/B) on 1665 —
  consistent with "populated only when a winner is recorded".
- `serve_width`/`serve_depth` are "NA" on 54 points each; `speed_mph` has a few
  blanks; `return_depth` is "NA" on 1309 points (return depth only makes sense
  when a return is actually struck). All are structurally absent, matching the
  expert's account.
- Therefore the supplied data are complete and representative for the
  point-level outcome variables (point_victor, server, serve_no, scores,
  game/set victor, distance, rally) which have zero missing values, and the
  optional descriptive columns are conditionally populated. The model is built
  on the complete columns and uses the conditional columns only where defined.

## Exchange 2 — Key structural assumption: what triggers a momentum turn

**Question (expert_question_2.md):**
"When a tennis player has lost several straight points and the flow turns
against them, what usually triggers the turn?"

**Expert reply (paraphrased value, not verbatim):** The single most reliable
trigger is the **service-game boundary / change of server** — a run of points
frequently ends when the trailing player gets to serve or the opponent's
service game ends, because the serve advantage (roughly 60–80% of service
points won at tour level) is large enough to reset the flow. Secondary
triggers: (i) a high-value point (break point / set point / deuce–advantage
swing) whose cost is disproportionate to its count; (ii) an error-cluster
reversal — the trailing player stops donating unforced errors and/or starts
landing first serves (the biggest single lever); (iii) a long physical point or
a stoppage that shifts who dictates rallies. Runs are typically short (a few
points) and statistically hard to separate from random streaks; the reliable
structural trigger is the service boundary, **not a psychological switch**.

**How this changed the work (turns into a parameter/constraint + model change):**
1. **Structural-assumption constraint.** The swing-prediction model is built on
   the assumption that a "momentum turn" is primarily a *structural* event
   (service game boundary, high-leverage point, error cluster), not an
   unobservable psychological state. This rules out trying to infer a hidden
   "morale" variable and instead conditions the predictor on observable
   structural features: server change / game boundary, whether the point is a
   break point or set point, and a rolling unforced-error / first-serve rate.
2. **Feature set for the swing predictor** (implemented in `swing_predictor.py`):
   - `server_change` / `new_game` (1 when the server or game just changed) —
     the dominant structural trigger per the expert.
   - `is_break_point`, `is_set_point` (high-leverage points).
   - Rolling trailing-player `unforced-error` count and `first-serve` rate
     (error-cluster reversal).
   - Trailing `point run` length and the current momentum-metric level `M`.
   The target is "does the flow of play (sign of M, or a swing of ≥2 points to
   the trailing player) change within the next k points." This directly
   operationalises the expert's triggers as model inputs.
3. **Calibration value.** The expert's "60–80% of service points won at tour
   level" is a qualitative range that *bounds* the serve advantage my own
   serve-model estimates (0.68–0.77 on first serve, 0.55 on second), so the two
   are consistent; I use my data-estimated values in the model and cite the
   expert range only as a sanity bound (Exchange 2).

## Exchange 3 — Interpretation context: decision-relevant threshold

**Question (expert_question_3.md):**
"When a point-by-point stat shows a big lead, when would you trust it as real,
rather than noise?"

**Expert reply (paraphrased value, not verbatim):** Trust a lead only when it is
anchored to *structural, repeatable* advantages, not a raw point count:
- It **survives the service boundary** — persists across a change of server
  (the player also wins points on the opponent's serve or holds comfortably). A
  lead built on a single service game is mostly serving noise.
- It is **large relative to the sample** — 2–3 points is normal streak
  variance; roughly **5+ points** or a multi-game lead is unlikely to be chance.
- It is **corroborated by process stats** (first-serve %, unforced-error rate,
  winners, break points created/converted), not just the scoreboard.
- It occurs at a **high-value juncture** (break point, set point, tiebreak).
Empirical judgment: point-level leads under ~3 points are indistinguishable
from random streaks; the scoreboard alone is weak evidence.

**How this changed the work (turns into a parameter/constraint + decision rule):**
1. **Decision threshold.** I adopt a decision-relevant rule for when a
   "momentum" reading is actionable: report the momentum metric M only when it
   is (a) sustained across a service-game boundary, (b) corresponds to a
   cumulative surplus of ≥ ~3–5 points (below that is within random-streak
   variance), and (c) is corroborated by the process statistics. I quantify the
   random-streak band from the data: the standard deviation of the point
   surplus over a 5-point window is ~sqrt(sum p_i(1-p_i)) ≈ 1.0–1.1 points, so
   a lead of <3 points is within ~3 sigma of a zero-mean random streak and is
   *not* trusted; a 5+ point surplus is. This converts the expert's qualitative
   "5+ points" into a data-backed decision rule.
2. **Reporting constraint.** The match-flow visualization and the memo's
   "who is performing better" readout therefore report the *direction and
   magnitude* of M but flag any reading below the 3-point-surplus / single-
   service-game threshold as "within noise" rather than as a real advantage.
   This directly addresses the practicality / result-analysis criteria: the
   coach is told when a stat is a real advantage vs. noise, and the advice is
   to act on process stats (first serve, unforced errors) at high-value
   junctures rather than chasing point-count streaks.
