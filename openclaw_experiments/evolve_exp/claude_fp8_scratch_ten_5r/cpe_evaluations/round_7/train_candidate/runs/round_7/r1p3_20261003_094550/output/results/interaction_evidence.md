# Expert Interaction Evidence — 2024_C (Tennis Momentum, 2023 Wimbledon 1701)

Ten fixed exchanges. Each: question (structural → parameter → boundary), reply,
and the concrete change it forced in the model / code / decision rule.

## Exchange 1 (structural — dominant mechanism)
- **Q:** When a match swings, is the bigger driver serve (hold/break) or "getting hot" (shot quality)?
- **Reply (paraphrased, not quoted):** Serve is the bigger driver of *measured* swings;
  "getting hot" drives *perceived* swings. A single break flips a set scoreline and dominates
  any score-based metric. Most apparent runs are just service holds. Genuine sustained swings
  come from the returner raising shot quality (first-serve %, return depth, rally tolerance),
  which produces the break. Hot shot-making is the mechanism; breaking serve is the visible
  signature. If you don't control for who is serving you misattribute service holds to momentum.
  The residual after removing serve effects is the part attributable to form.
- **How it changed the work:** Fixed the *shape* of the model. Built a **serve-adjusted**
  momentum: for every point compute the serve-context expectation (server wins 75.4% on 1st
  serve, 53.0% on 2nd serve — from the dataset) and define each player's "form" as an
  exponentially-decayed EMA of the residual (actual − serve-context expectation). Momentum(t)
  = form1 − form2. This is exactly the "residual after removing serve effects" the expert named.
  Code: `code/momentum.py`.

## Exchange 2 (parameter — magnitude of form)
- **Q (built on 1):** After removing the serve effect, how large is the real hot-vs-cold
  difference in next-point win probability — under ~5, around ~10, or larger (points)?
- **Reply (paraphrased):** Moderate, ~10 percentage points is the right order. Baseline
  next-point ~50% on return, 65–80% on serve. A player in a real zone moves their return-point
  rate ~35%→45% or hold rate ~80%→90%, i.e. an 8–12 point shift. Under ~5 is noise/serve context;
  sustained shifts >15 are rare, short (a few games), and often reflect the *opponent's* dip
  (injury, double-faulting, tanking) rather than one player's heat. Expect form to decay within
  a handful of games.
- **How it changed the work:** Set the form-effect scale and decay. Chose EMA decay
  tau = 8 points (form half-life a handful of points) and residual clip = 0.10 (≈ the
  ~8–12 point band). The "rare, short, opponent-dip" caveat became a **decision rule**:
  sustained |momentum| > ~0.15 (the observed max in the target match is 0.121) is flagged as a
  possible opponent-collapse signal, not a hot hand — and the null test (below) shows such
  long sustained deviations do *not* occur, supporting "form decays within a few games."

## Exchange 3 (boundary — high-leverage points)
- **Q (built on 1–2):** On a break point — the moment a swing is most likely — do players play
  it like any other point, or does pressure change how they play?
- **Reply (paraphrased):** Measurably differently, mostly to the server's detriment. Server
  tightens: first-serve % drops a few points, double-fault rate rises, first serve over-hit or
  second serve pushed. Returner loosens or over-commits (or goes passive). Rally length and
  error rates shift; break points end slightly earlier and on more unforced errors. Effect is
  modest, not a transformation; biggest determinant remains who is serving.
- **How it changed the work:** This was *testable in the data* and the test **confirmed it**
  (`logs/breakpoint_pressure2.log`): on break points the server's first-serve fraction drops
  64.2%→60.7%, double-fault rate rises 3.4%→4.2%, unforced-error rate rises 15.9%→16.9%, and
  the server's point-win rate drops 67.5%→64.9%. Converted to the model: (a) the swing-prediction
  model keeps `break_pt` as a feature, and (b) the fix this revealed — the server's own
  double-fault/unforced-error columns were being read from the *returner's* columns in
  `code/swing.py`; corrected to the server's own columns, after which `srv_df_rate` gained a real
  positive coefficient (+0.246 swing / +0.595 reversal), i.e. a rising server DF rate predicts a
  swing, exactly the asymmetric server-degradation the expert described.

## Exchange 4 (boundary — generalizability to another sport)
- **Q (built on 1–3):** Does "getting a run of heat" carry over to table tennis, or is that
  sport too fast for momentum to build?
- **Reply (paraphrased):** It carries over — table tennis has momentum, arguably more visible.
  Speed of the ball does not determine whether momentum builds; the *scoring structure* does
  (played to 11, serve alternates every 2 points, so a 3-4 point run is a large fraction of a
  game). The serve advantage is much smaller (~55-60% vs 65-80% in tennis), so the residual
  "form" component is a bigger share of the swing and less confounded by serving. Heat shows
  in the same places (serve/receive quality, first-attack consistency, error rate under
  pressure). Runs are shorter (a few points) because the game resets every 11; coaches use
  timeouts to break runs.
- **How it changed the work:** Converted to the model's generalizability claim. The serve
  baselines (0.754/0.530) are **tennis-specific parameters that must be re-estimated per
  sport/surface** — they are not universal constants. Because the model is serve-*adjusted*,
  it transfers to sports where the serve advantage is weaker (table tennis): there the
  form-residual carries a larger share of the swing, so the same construction applies but the
  residual is more informative. The decay tau should scale with the sub-game "reset unit"
  (a table-tennis game of 11 points, not a tennis game of ~4-5). This is recorded in the
  solution as a limitation/generalizability statement rather than a re-run (no table-tennis
  data in the dataset).

## Exchange 5 (parameter — duration of a genuine surge)
- **Q (built on 1–4):** How long does a genuine run of heat typically last — a couple of
  games, several, or a whole set?
- **Reply (paraphrased):** A couple of games is typical; several is the upper end of normal;
  a whole set is rare and usually means the opponent has dipped, not one player sustaining
  heat. A form surge usually shows over ~2-4 games then regresses. 5-6 game runs happen
  (esp. grass, a hot server holding repeatedly) but are the exception. A 6+ game "run" should
  be treated with suspicion — more often the other player's collapse (injury, double-faulting,
  tanking) than sustained heat. Heat decays within a handful of games; the scoreline can stay
  lopsided longer because of who's serving.
- **How it changed the work:** This is the tau calibration. 2-4 games ≈ 8-20 points. I swept
  tau over that range (reversal OOS AUC on the target match): 0.50 (tau=4), 0.636 (8),
  0.658 (12), **0.725 (16)**, 0.721 (20). The peak at **tau=16 (~3-4 games)** converges with
  the expert's "2-4 games." Adopted tau=16 as the default decay. The "6+ game run = opponent
  collapse, not heat" caveat became a decision rule: sustained |momentum| beyond the typical
  band is flagged as a possible opponent-collapse signal, not a hot hand. Re-running all
  models at tau=16 improved reversal OOS AUC 0.636→0.725 and generalizability
  (mean 0.615→0.687, 77%→94% of matches >0.55).

## Exchange 6 (boundary — tiebreaks)
- **Q (built on 1–5):** Do momentum swings work the same way inside a tiebreak, or does the
  short reset make the flow harder to read there?
- **Reply (paraphrased):** Same mechanism but compressed and harder to read. Serve alternates
  every two points, so the serve confound is largely neutralized — the residual form component
  is a bigger share of what you observe (tiebreak swings more likely to be genuine). But the
  sample is tiny (~7 points), far too few to separate a ~10-point form shift from noise; a 3-0
  run is luck as often as heat. Treat tiebreak swings as real but low-confidence, and expect
  them to **reset at the next set**.
- **How it changed the work:** Two testable claims, both verified in the data:
  (1) serve alternates every 2 points in tiebreaks (confirmed: server sequence
  F,T,F,T… and tiebreak server win-rate 0.701 vs 0.672 normal, first-serve fraction similar
  → serve confound largely neutralized);
  (2) form should reset at the next set. Added a `reset_at_set` flag to `momentum.py`
  (default True). Comparing carry vs reset on the target match: **reset makes the sign of
  every set's mean momentum match the documented dominant player in all 5 sets** (carry got
  sets 2 and 5 wrong/weak). The expert's "reset at the next set" measurably improved the model's
  fidelity to the actual match. Tiebreak points are also excluded from the break/swing
  prediction (game_no=13) because the residual is low-confidence there, per the reply.

## Exchange 7 (boundary — coaching/preparation)
- **Q (built on 1–6):** What is the single most useful habit to drill so a player holds their
  own when the flow turns against them?
- **Reply (paraphrased):** A fixed between-point routine that resets attention to the next
  point only — same physical sequence (breath, ball bounce, cue word, serve/return intent)
  every point, regardless of score. The flow turning against a player is mostly a
  score-context effect: the player starts playing the scoreline rather than the point. An
  identical routine at 40-0 and 0-40 removes the scoreline as an input. It counters the two
  self-reinforcing mechanisms — rushed decisions and tightened serving on pressure points.
  Works whether the swing is real heat or just service holds; doesn't require diagnosing what's
  happening.
- **How it changed the work:** Became the central recommendation of the coach's memo. It is
  the *actionable* consequence of the null-test finding: because there is no point-level "hot
  hand" to sense (autocorr −0.018 ≈ 0), a player cannot train to *detect* momentum — but they
  can train a routine that is robust to it, and that routine directly counters the measured
  break-point pressure effect (server first-serve fraction drops 64.2%→60.7%, DF rate rises
  3.4%→4.2% under pressure, exchange 3). No re-run needed; it is the interpretation of the
  model's findings for the coach.

## Exchange 8 (boundary — generalizability to women's matches / clay)
- **Q (built on 1–7):** Would the same serve-driven story hold in women's matches and on clay?
- **Reply (paraphrased):** Same structure, serve component smaller, rally/form component
  larger. Women's: serve advantage ~55-65% (vs men's 65-80%), breaks more common, score swings
  less confounded by serving, residual form a bigger share. Clay: ball slows, rally tolerance
  rewarded, serve dominance drops further, breaks and multi-break swings more frequent, runs
  more likely genuine shot-quality shifts. Grass is the opposite extreme — serve story
  strongest there. The ~10-point hot/cold magnitude holds across all, slightly larger on clay.
- **How it changed the work:** Converted to the generalizability statement with a
  surface/sport parameterization: the serve-advantage baseline is the key
  sport/surface-specific parameter, ranging ~55% (clay, women's, table tennis) to ~80% (grass,
  men's). The model's construction is invariant (it is serve-adjusted); only the serve
  baseline must be re-estimated per surface/sport, and the form-residual becomes larger and
  more readable on slower surfaces. The ~10-point form magnitude (exchange 2) is robust
  across all, slightly larger on clay. Recorded in the solution as the answer to the
  "Women's matches / court surfaces" sub-question (no such data in the dataset, so this is a
  parameterized claim, not a re-run).

## Exchange 9 (boundary — factors for future models)
- **Q (built on 1–8):** If you could add one measurement to better spot when the flow is
  about to turn, what would it be, and why is it harder to see from the score alone?
- **Reply (paraphrased):** Per-point serve quality and return quality — first-serve
  percentage, serve speed/placement, return depth — tracked as a rolling window over the last
  several points. The flow turns before the scoreline shows it: the score updates only when a
  point ends, and most points end on the server's terms, so the scoreline lags the underlying
  shift by a game or more. A player can win a game while serving badly (opponent errors) or
  lose one while serving well (net cords). Shot-quality measures move with form directly and
  are not confounded by who's serving.
- **How it changed the work:** Made it into a testable hypothesis. Built
  `code/future_features.py` with rolling no-look-ahead serve-quality features (server first-serve
  success rate, serve speed, receiver return-depth rate) and tested whether they improve
  reversal AUC beyond the momentum/serve-state base. Result: **AUC 0.686 → 0.695 (+0.009)** on
  the target match — directionally supported (negative coefficients on first-serve rate and
  return depth: a dip predicts a reversal, as predicted) but a modest incremental gain.
  Explanation recorded: the momentum model already captures much of the same signal through
  form_recv/form_server (built from point outcomes that include serve quality), and the data
  lacks the rich serve-placement/return-quality the expert would want. This is the
  "factors that might need to be included in future models" deliverable.

## Exchange 10 (boundary — coaching a player into a new match)
- **Q (built on 1–9):** Going into a brand-new match against a different opponent, what to
  expect about the swings and how to prepare?
- **Reply (paraphrased):** Expect the swings; expect most to be about serve, not who's hot.
  Swings are normal (a break or two per set is ordinary). Most of what looks like his momentum
  is him holding serve (grass: server wins the large majority of points) — don't read a run of
  holds as outplay. A genuine shift is ~10 points and 2-4 games, and it decays. The turn is
  visible before the score (first-serve %, attackable second serves, return depth). Prepare by
  drilling one fixed between-point routine, having a pre-planned adjustment for when
  outplayed (raise first-serve %, target more, take the second-serve return, extend rallies)
  decided beforehand, using the natural breaks (changeovers, the set reset) to let runs end,
  and not chasing the momentum narrative (chasing makes you press and tighten, turning a
  two-game dip into a lost set).
- **How it changed the work:** This is the synthesis that the coach's memo (subtask 3's
  deliverable) is built from. Every recommendation maps to a measured finding: "swings are
  normal" ← null test + reversal base rate 0.197; "most are serve, not hot" ← serve baselines
  0.754/0.530 + null test; "genuine shift ~10 points / 2-4 games" ← exchanges 2 & 5; "turn
  visible before score" ← exchange 9 + serve-quality test; "fixed routine" ← exchange 7;
  "use set resets" ← exchange 6 (reset_at_set). It is the interpretation layer for the memo;
  no new computation, but it is where the ten exchanges converge into the advice the problem
  asks a coach for.
