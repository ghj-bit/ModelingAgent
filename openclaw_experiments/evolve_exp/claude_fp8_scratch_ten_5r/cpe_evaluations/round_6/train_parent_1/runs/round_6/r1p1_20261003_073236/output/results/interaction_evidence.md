# Expert Interaction Evidence — Task 2024_C (Tennis momentum)

Ten exchanges, one question each. For every exchange the reply was converted
into a parameter, constraint, or model/decision-rule change before the next
exchange. Values used in the model carry the exchange number as their source.

## Exchange 1 — run persistence vs immediate counter
- **Question:** When one player goes on a strong run of points, does the
  opponent answer with a short burst right away, or does the run continue for
  a while before changing?
- **Reply (gist):** runs continue for a while; point outcomes are close to
  independent once conditioned on server; the main run-terminating mechanism is
  structural — the serve changes hands at each game boundary (server wins
  roughly 60–80% of points). Empirical judgment.
- **Used in work:** This fixed the *structural* design of the momentum model.
  Instead of a psychological "hot hand" process, the model is a
  serve-conditioned Bernoulli baseline (P(server wins point) by serve number)
  with momentum defined as the cumulative *surprise* relative to that
  baseline; flow shifts are expected to be concentrated at game boundaries /
  serve changes. It also justified the null hypothesis tested in subproblem 2
  (runs are random once serve is conditioned). The 60–80% server point-win
  band was checked against the data: observed 76.2% (1st serve) and 58.9%
  (2nd serve) pooled — consistent.

## Exchange 2 — typical run length
- **Question:** How long do streaks of points by one player typically last
  before the other gets one back?
- **Reply (gist):** most commonly 2–4 points, occasionally 5–6, rarely
  beyond; the practical ceiling is structural (game boundary / serve change).
  Empirical judgment.
- **Used in work:** Set the expectation band for the randomness analysis in
  subproblem 2: mean run length of raw point outcomes in the data was 2.98
  (final, 334 pts) and 2.94–3.17 in the five backtest matches — inside the
  expert's 2–4 band, supporting "typical runs are short." The long-run
  structural ceiling was used to choose the game (not the point) as the
  natural unit for flow: the per-game flow score and EWMA over games in
  subproblem 1, and swing detection at game boundaries in subproblem 3.

## Exchange 3 — second-serve speed trade-off
- **Question:** How much does a player slow his second serve to get it in,
  versus the first?
- **Reply (gist):** second serves are about 15–25% slower, roughly 10–20 mph
  lower (a 115–130 mph first serve drops to ~90–105); more spin and higher
  clearance; bigger for big servers. Empirical judgment.
- **Used in work:** Calibrated the two-serve structure of the point model.
  Data check: mean first-serve speed 119.3 mph (median 121) vs 98.9 mph
  (median 99) for second serve — a 21.5 mph / 18% drop, within the expert's
  band — and server point-win probability falls from 76.2% (1st) to 58.9%
  (2nd) pooled. The model therefore uses a separate baseline for serve_no = 1
  and 2 rather than a single "server" effect; this is what makes the surprise
  term meaningful (a point won on second serve is worth more information than
  one won on first serve).

## Exchange 4 — what marks a turnaround
- **Question:** What kind of points, if any, most often mark the start of a
  sudden turnaround?
- **Reply (gist):** high-leverage points at game boundaries — break points
  (saved or converted), change of server, tiebreak points, set-ending points;
  ordinary mid-game points rarely do. Empirical judgment.
- **Used in work:** Defined the *cue set* tested in the swing-prediction model
  (subproblem 3): break point present, previous game broken, previous game
  against the flow, long (deuce) game, late position in game. It also set the
  validation design: swings are measured at game boundaries and cues are taken
  from the preceding game. Outcome: pooled across 31 matches, a game won
  *against* the current flow precedes a further flow reversal at rate 64.0%
  vs 51.3% baseline (n=734) — the only cue with a real lift, matching the
  expert's "high-leverage points at boundaries" pattern; break-point and
  long-game cues showed no lift.

## Exchange 5 — how many points before the serve changes hands
- **Question:** How many points are usually won before a player's serve
  changes hands to the opponent?
- **Reply (gist):** the serve changes at the end of a game, not after a fixed
  run; a service game typically lasts 4–6 points (deuce games 7–10+); the
  server usually wins 3–4 of those points. Empirical judgment.
- **Used in work:** Justified game as the aggregation unit and the scale of
  the surprise accumulation: a typical game contributes ~4–6 points of
  surprise, so an EWMA weight of 0.4 on the game flow score keeps roughly the
  last 2–3 games in view (the window over which a "flow" is meaningful). Data
  check: mean game length 334/55 ≈ 6.1 pts in the final; game-hold rate 76.1%
  in the final, 83.9% pooled.

## Exchange 6 — serve behavior on break point
- **Question:** Down a break point, does a player usually serve harder or
  slower and safer?
- **Reply (gist):** slower and safer on average — more first-serve percentage,
  modest pace reduction, more margin; a weak, player-dependent tendency, not
  a rule. Empirical judgment.
- **Used in work:** Motivated including *serve_no* (first vs second) and
  break-point context in the predictor, and set the expectation that
  break-point effects would be small — consistent with the null lift found
  for the break-point cue (0.133 vs 0.513 baseline after a previous break).
  It bounded the claim: the model does not attribute swings to a
  "playing-it-safe" mechanism it cannot measure from the data (shot
  placement is absent), which is recorded as a limitation.

## Exchange 7 — timescale of momentum swings
- **Question:** Do momentum swings usually happen all at once, or over a
  stretch of several games?
- **Reply (gist):** the sustained shift builds over several games; the
  single-point "instant" flip is the scoreboard culmination of a gradual
  drift, usually confirming a shift already underway. Empirical judgment.
- **Used in work:** Set the horizon for swing validation to a multi-point /
  multi-game window (25 points ≈ 4–5 games) rather than the next single
  point, and motivated the EWMA construction (memory of a few games) instead
  of a one-point hot-hand indicator. The forward-validation hit rate
  (~50%) is reported against this timescale.

## Exchange 8 — errors under pressure
- **Question:** Serving under big pressure late in a match, do unforced
  errors usually go up or down?
- **Reply (gist):** up on average — tension tightens the serve-and-first-shot
  pattern, concentrated on the highest-leverage points; modest and
  player-dependent. Empirical judgment.
- **Used in work:** Added error/winner differentials as *explanatory* (not
  predictive) diagnostics in the match-flow analysis: in the final, Alcaraz
  hit 19.8 winners/100 pts vs 9.6 for Djokovic, with comparable unforced
  errors (13.5 vs 12.0/100) and Djokovic's double-fault rate 0.9% vs
  Alcaraz's 2.1%. This supports the interpretation that the swings in set 4
  (Djokovic's comeback) were driven by shot-making collapse on the trailing
  side's key points, and it is the mechanism the coach memo advises players to
  manage (serve routine under pressure). It also defines a future-model
  feature: error rate on high-leverage points.

## Exchange 9 — behavior after a tight set
- **Question:** After winning a tight set, do players usually play more
  freely or more carefully?
- **Reply (gist):** more freely on average, but modestly and transient —
  typically a game or two; the player who *lost* the tight set is more likely
  to tighten up, especially if he had led. Empirical judgment.
- **Used in work:** Used to interpret the set-to-set pattern in the final:
  after Alcaraz won the tight tiebreak set 2, his point momentum stayed
  positive through the opening of set 3 (end-of-set momentum +0.37, set won
  6–1); after losing set 1 badly, Djokovic's flow recovered only gradually
  through sets 2–4. The transient (1–2 game) timescale reinforced the short
  EWMA memory chosen (weight 0.4 on game flow ≈ 2–3 games).

## Exchange 10 — single best indicator of an impending flow change
- **Question:** What single factor, more than any other, tells you a match's
  flow is about to change?
- **Reply (gist):** the change of server at a game boundary — the moment the
  dominant player must receive or the trailing player serves — with
  break/tiebreak points at that boundary as the concrete trigger. Empirical
  judgment.
- **Used in work:** This is the structural rule the swing model implements:
  flow is evaluated *per game* (the serve-ownership unit), a swing is a
  reversal of the running game-flow direction at a game boundary, and the
  cue analysis is anchored to the preceding game (server, break, leverage).
  The advice-to-coaches conclusion follows from it: the reliable "tell" is the
  boundary itself plus who is serving the next game, not any in-point signal.

---

### Parameter table (empirical inputs, with sources)

| Parameter | Value | Interval | Source |
|---|---|---|---|
| Server point-win rate, 1st serve | 0.762 (pooled) / 0.656 (final) | 0.60–0.80 | Dataset (7284 pts); expert band from exchange 1 |
| Server point-win rate, 2nd serve | 0.589 (pooled) / 0.533 (final) | 0.5–0.7 | Dataset; consistent with 15–25% slower 2nd serve, exchange 3 |
| First-serve speed | 119.3 mph mean | 115–130 | Dataset (4322 serves) |
| Second-serve speed | 98.9 mph mean | 90–105 | Dataset (2210 serves); drop within exchange-3 band |
| Server game-hold rate | 0.839 (pooled) / 0.761 (final) | 0.75–0.85 | Dataset (1188 games) |
| Typical service-game length | ~5–6 pts (final 6.1) | 4–6 typical, 7–10 deuce | Dataset; exchange 5 |
| Typical point run length | 2.98–3.17 mean (matches) | 2–4 typical | Dataset; exchange 2 |
| Typical timescale of a flow shift | 2–3 games (EWMA memory) | 1–2 to several games | Expert judgment, exchanges 5, 7, 9; encoded as EWMA weight 0.4 |
| Swing validation horizon | 25 points | ~4–5 games | Expert judgment (exchanges 5, 7), set as model constant |
| High-leverage-point effect on flow reversal | +12.8 pts lift (64.0% vs 51.3%) | — | Dataset (31 matches, 734 cue games); pattern from exchange 4 |
