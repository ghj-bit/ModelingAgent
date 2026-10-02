# Interaction evidence — MM-Bench 2024_C (momentum in tennis)

Three expert exchanges, one question each, exactly as required. Each reply was
converted into a model constraint or a run-and-reported test before the next
exchange. Expert text is quoted only here (the evidence file); nothing from the
replies is copied into solution.json.

## Exchange 1 — data-generation / selection mechanism

**Question (written to expert_question_1.md):**
Why would speed and distance data be missing for some points, and does the
missingness track point type?

**Expert reply (verbatim, from expert_reply_1.json):** Missing speed/distance is
mostly instrumentation and logging gaps, not random: unrecorded serves (especially
second serves, lets, and unreturned aces), Hawk-Eye/tracking dropouts, and points
where the feed simply wasn't captured. Distance zeros cluster where tracking
failed or the point ended on the serve (no running). So yes — missingness tracks
point type: serve-only points, aces, double faults, and short rallies are
over-represented among blanks. It is not missing-at-random; treat it as
informative.

**How the reply was turned into work (verified, then used):**
- I tested the expert's claim against the data (logs/verify_missingness.log).
  The observed pattern differs in detail from the expert's guess: speed blanks
  are nearly absent on serve-only (rally_count==1) points (0.2% blank) but
  concentrate on 2-shot return points (19.3% blank) and second serves (15.9%
  vs 7.2% for first serves). Distance zeros (0.43% of rows) cluster in a handful
  of matches, consistent with tracking dropouts.
- **Constraint adopted (E1):** serve speed and distance are missing-not-at-random.
  The model never imputes `speed_mph` or `distance_run`. They are used only on
  rows where recorded, and their blank/zero pattern is treated as an indicator of
  the point type that produced the gap. This is why the point-level model keys on
  `serve_no` (first/second) rather than on raw speed, and why no speed regressor
  appears in the model at all.

## Exchange 2 — temporal / state structure

**Question (written to expert_question_2.md):**
When one player starts dominating a tennis match, does the run usually
continue, bounce back, or last about how long?

**Expert reply (verbatim, from expert_reply_2.json):** Runs do both; at point
level they mostly revert — over a match, point outcomes are close to independent
given the server, so a run of 3–5 points is usually just the base rate, not a
swing. What persists is at the game/set scale — a break of serve, a change in who
holds, or a shift in first-serve percentage tends to carry for several games.
What coaches actually read: body language, first-serve percentage and
second-serve aggression, return position/depth, unforced-error type. A genuine
swing typically lasts ~2–4 games (10–25 points), or until the next
changeover/break resets it. Anything shorter is noise.

**How the reply was turned into work (verified, then used):**
- Point level (logs/runs_test.log): P(next point won by same player | run of
  length 1,2,3) = 0.541 / 0.559 / 0.567, dropping to 0.430 / 0.402 at runs of
  4 and 5. Runs of points revert — confirming the expert's point-level claim.
- Game level (logs/game_runs.log): median game streak = 1, mean = 1.39,
  P(streak>=2) = 0.18. A genuine swing is an unusual, game-scale event.
- **Constraints adopted (E2):** (a) every point probability is conditional on
  the server and serve number (the dominant, non-momentum structure); (b)
  momentum is defined on a game-scale state — the per-point advantage series is
  an EWMA of model residuals with half-life 6 points (~one game), not a raw
  streak; (c) point-level streaks are reported against their base rate as noise.

## Exchange 3 — bias-aware interpretation threshold

**Question (written to expert_question_3.md):**
As a coach, how many straight games or points by one player would convince you
the match has genuinely turned?

**Expert reply (verbatim, from expert_reply_3.json):** A break of serve plus the
hold that follows — two straight games, roughly 8–12 points — is the first thing
I'd call a genuine turn. Three straight games (a double break, or break-hold-break)
convinces me. Two or three straight points never does; that's the base rate.

**How the reply was turned into work (verified, then used):**
- I computed, over all 31 matches (1188 games), the persistence structure around
  breaks (logs/debug_streak2.log): after a game that was a **break**, the same
  player wins the next game 86.2% of the time (152 break games) — the
  "break + hold" is the recurring, coach-recognized turn; after a **hold**, the
  opponent wins the next game 83.7% of the time (independent serving games).
  P(next game changes winner | prior streak >= 2) = 0.681 vs 0.741 for a single
  game — mild but real persistence at the game scale.
- **Constraint adopted (E3):** the swing detector's threshold is set at a
  break followed by a hold (2 straight games) as the "turn", with 3 straight
  games as the convincing case; point streaks of 2–3 are explicitly below the
  actionable threshold and reported as base rate. The model's actionable signal
  is therefore the break/hold state, not any point-run.

## Bias-aware reading of the results

Given E1 (the record is a selected view — blanks tie to point type) and E2/E3
(momentum is game-scale), a model output is treated as a robust signal only
when it persists over at least a break + hold and its magnitude exceeds what the
permutation null produces. In this dataset the max per-point advantage in the
featured match (0.309 on the EWMA scale) falls inside the null distribution
(p = 0.775), and in none of the 31 matches does the max advantage reach p < 0.1
under the server-conditioned permutation test. The reliable, bias-resistant
signal in the data is at the game scale (break/hold persistence above), not at
the point scale.
