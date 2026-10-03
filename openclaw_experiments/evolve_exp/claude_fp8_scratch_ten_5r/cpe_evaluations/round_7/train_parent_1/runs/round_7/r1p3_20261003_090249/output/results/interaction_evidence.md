# Expert Interaction Evidence — MM-Bench 2024_C (Tennis Momentum)

Ten exchanges, one question each, in order. For each: the question, a summary of
the reply, and the concrete effect on the model (parameter, equation, decision
rule, or test). Expert replies are used as input only; no reply text is copied
into the submission.

## Exchange 1 — structural choice: what measures dominance
- **Question:** When rating how strongly a player is dominating point by point,
  do you look mainly at who is winning the points, or at who is hitting more
  winners / making fewer mistakes?
- **Reply (summary):** Rate dominance by points won — point outcomes are the
  only currency that changes the score and already embed winners, errors,
  serve and rally dynamics. Use winner/error counts as explanatory support,
  not the primary measure.
- **Effect on work:** Fixed the model skeleton. The flow metric is built on
  point outcomes (`point_victor`), not on winner/error tallies. Winners and
  unforced errors enter only as secondary features in the swing-prediction
  model (`predict.py` / `predict_game.py`), consistent with the reply.

## Exchange 2 — calibration: run length that signals a genuine shift
- **Question:** In a top-level match, how many points in a row of a player
  clearly dominating before you'd say the momentum has genuinely turned?
- **Reply (summary):** Roughly 4–6 consecutive points is a genuine shift; 3–4
  if the run includes a break of serve. Below 3 is normal variance (servers
  win ~65–75% of service points). 7+ is rare and clearly meaningful. Empirical
  judgment, not a precise threshold.
- **Effect on work:** Set the run-length detection parameter L = 4 in the
  swing detector (`momentum.py detect_swings`), with the break-inclusive
  variant (3–4) noted as the lower bound. Also used to interpret the
  run-length distribution in `run_analysis.py` (observed longest runs vs the
  4–6 band).

## Exchange 3 — mechanism: how form dips develop
- **Question:** When a player's form clearly dips during a set, is it usually
  a sudden shift or does it build up over several games?
- **Reply (summary):** Gradual build-up over ~2–4 games is the norm; sudden
  single-point flips are the exception and usually have an identifiable
  trigger (bad line call, double fault at break point, opponent's run).
- **Effect on work:** Justified the game-level (not point-level) prediction
  design. `predict_game.py` uses a 4-game lookback window (G = 4) and
  rolling service statistics, matching the 2–4 game build-up. The point-level
  predictor (`predict.py`) was kept only as a contrast (pooled AUC 0.487),
  supporting the expert's "gradual" reading.

## Exchange 4 — indicator: what signals the set is turning
- **Question:** If your player is serving well but losing most return points,
  is that the moment you'd expect the set to start turning against them?
- **Reply (summary):** No — that is a normal stable state. The real warning is
  erosion on the serve side: first-serve percentage dropping, points lost on
  one's own serve, or a break conceded. Return-game struggles are dangerous
  only when paired with shaky service games.
- **Effect on work:** Defined the warning indicators used in
  `cohort.py` and `predict_game.py`: service-point win rate (hold rate) and
  second-serve win rate as primary predictors; return rates kept as controls.
  The cohort test (service-erosion cohorts) was built around this rule.

## Exchange 5 — coach's response: how to react to losing on serve
- **Question:** Do you advise players to keep serving the same way when they
  start losing points, or to change the serve first?
- **Reply (summary):** Change the serve first, but placement and pattern, not
  the motion. Vary width (body/wide/center), mix serve looks; do not
  abandon a working delivery mid-match.
- **Effect on work:** Motivated the serve-pattern analysis in
  `serve_pattern.py`: server win rates by `serve_width`, and repeat-same-width
  vs new-width comparisons, to test whether pattern variation shows up in the
  data.

## Exchange 6 — ranking: first-serve rate vs pattern
- **Question:** How important are serve-placement/pattern changes when
  struggling, compared with just hitting the first serve more?
- **Reply (summary):** First-serve percentage is the dominant lever — the
  first-vs-second serve gap is roughly 15–25 percentage points. Placement
  variation is the secondary fix, most useful when first serves are landing
  but being returned well.
- **Effect on work:** Calibrated the serve parameter table: the data's
  first-serve hold 0.754 vs second-serve hold 0.530 (gap 22.5 pp) sits
  inside the expert's 15–25 pp band, confirming the calibration. The
  coaching memo ranks (1) first-serve percentage, (2) placement variation,
  (3) steady point construction, per this ordering.

## Exchange 7 — preparation: facing a volatile opponent
- **Question:** Facing an opponent known for wild form swings, what one
  preparation do you prioritize?
- **Reply (summary):** Hold your own serve and stay steady through their hot
  streaks; play the percentages on your service games, don't match runs
  shot-for-shot. High first-serve percentage, conservative point construction,
  treat a lost return game as normal. Avoid the unforced-error spiral —
  the opponent's dip is coming.
- **Effect on work:** Becomes the central recommendation of the memo and of
  the subtask-outcome advice. Also informed the model interpretation: the
  flow metric F is used as a "stay the course" cue (ride the opponent's surge)
  rather than a "change everything" cue.

## Exchange 8 — generalization: women's tennis
- **Question:** Does the same hold-serve/stay-steady advice work in women's
  tennis, or does the style change it?
- **Reply (summary):** Yes, same core advice, shifted emphasis. Serve is a
  smaller advantage in the women's game (lower server win share, more breaks),
  so holding serve buys less security; the return game matters relatively
  more. Steady play and avoiding the UE spiral matter at least as much.
- **Effect on work:** Used in the generalizability discussion (subtask
  outcome): the model's serve-adjusted point metric remains valid, but the
  serve-adjustment term carries less weight and return-game statistics gain
  relative importance; advice to coaches is unchanged in direction.

## Exchange 9 — generalization: table tennis
- **Question:** Do the momentum-swing ideas carry over to table tennis, or
  does the faster pace make them less useful?
- **Reply (summary):** They carry over and are more useful: table tennis is
  more serve-dominated and point-short; a run of 3–4 points can decide a
  game (games to 11). Use the same serve-adjusted point metric with a
  slightly lower shift threshold (3–5 points, fewer if a serve-rotation break
  is included). Swings happen faster with less build-up.
- **Effect on work:** Used in the generalizability discussion: the model
  transfers with a smaller window (shorter decay weight / shorter lookback)
  and a lower swing threshold; the game-level lookback design maps to
  "points-per-game" scaling (11-point games ⇒ lookback of 3–5 points).

## Exchange 10 — summary advice
- **Question:** The single most important piece of advice you'd give a tennis
  player about handling momentum during a match?
- **Reply (summary):** Hold your own serve and stay steady through the
  opponent's hot streaks; don't match their runs shot-for-shot. Swings are
  largely noise plus the opponent's own form dips; the reliable edge is not
  conceding serve during their peaks.
- **Effect on work:** Consolidates the memo's headline recommendation and the
  final interpretation of the randomness test: the data's near-random
  point-swing statistics (bootstrap and run-length tests) are consistent with
  "swings ≈ noise + form dips," and the actionable lever is serve stability,
  not chasing the swings.

## Parameter table (empirical values used in the model)

| name | value | interval / notes | source |
|---|---|---|---|
| first-serve server point-win rate | 0.754 | [0.70, 0.80] across matches | task dataset, `serve_no=1` points (n=4657) |
| second-serve server point-win rate | 0.530 | [0.45, 0.60] | task dataset, `serve_no=2` points (n=2627) |
| first/second serve gap | 22.5 pp | expert band 15–25 pp | exchange 6 (band); dataset (value) |
| server hold rate (game) | 0.857 | — | task dataset (n=1188 games) |
| break-point server hold rate | 0.649 | — | task dataset (n=504 break points) |
| genuine-shift run length | 4 (band 4–6; 3–4 with a break) | expert empirical judgment | exchange 2 |
| form-dip build-up window | 2–4 games → G = 4 game lookback | expert empirical judgment | exchange 3 |
| serve-erosion warning rule | drop ≥ 0.15 in service-point win rate over 3 games | threshold chosen at half a typical per-game rate; cohort n=219 | exchange 4 (rule); dataset (test) |
| per-match point-win logit intercept b0 | 0.55–1.70, mean 1.15 (sd 0.29) | fitted per match | task dataset (calibrated) |
| second-serve logit penalty b1 | −0.34 to −1.81, mean −1.04 (sd 0.33) | fitted per match | task dataset (calibrated) |
