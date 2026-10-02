# Interaction Evidence — MM-Bench 2020_D (Huskies network problem)

Three expert exchanges were run, one per round, before the model step they
governed. Full question/reply texts are in
`logs/operator_feedback/expert_question_N.md` / `expert_reply_N.json`.

## Exchange 1 — operational definition of the data (asked before network construction)

Question (paraphrased): is the recorded set of passes a faithful record of
how the team played, or a sample of what happened, and in practice what
makes event tracking miss part of a match?

Expert reply (key points): event data is a **sample, not a complete
record**. It captures completed, on-ball actions as judged by the tracker:
failed, intercepted, or cleared passes are not logged as passes (or are
logged as the opponent's event), so the network reflects *successful* ball
movement, not attempted movement; off-ball play (runs, positioning,
pressing, decoy runs) generates no event; borderline calls (deflection,
header, 50/50) are human coding judgments; non-pass touches (dribbles,
carries, tackles, shots) are excluded by construction; brief tracking lapses
can miss or misattribute events. The passing network is therefore a
reliable proxy for deliberate, completed ball circulation, but it
under-represents failed attempts, off-ball structure, and defensive work.

**How this became work:**
- The entire passing network (task 1) is defined over *completed* passes
  only; this is stated as an explicit assumption in the submission, with the
  bias made visible: edge counts are floors on attempted interaction, and
  any metric built on pass volume (tempo, breadth) inherits the same
  survivor bias.
- Because off-ball work is invisible, no indicator in the model relies on
  off-ball structure; the dynamical indicators are all computed from
  on-ball events that are actually recorded (pass tempo, pass-streak/flow,
  substitution timing, half-level pass profile).
- Because failed attempts are absent, completion rate is not used as a
  quality indicator (it is near-constant by construction of the data); the
  indicators use structure (distribution, channels) instead of volume.

## Exchange 2 — validating the causal direction (asked after the baseline network, before the outcome model)

Question (paraphrased): when a team's passing looks much better against one
opponent than another, is it the passing that is working, or usually
something else (e.g. the opponent sitting deep); what do coaches most often
get wrong about a team's passing?

Expert reply (key points): usually the **match context, not the passing**.
Pass volume/completion is driven by the opponent's defensive posture
(deep blocks let a team complete many short safe passes; high press forces
longer riskier balls and turnovers), by game state (leading teams pass
differently; chasing games inflate pass counts), and by opponent
quality/style. Coaches most often misread raw completion/volume as
quality, attribute passing swings to their own team when it is the
matchup, and confuse possession with penetration (safe sideways/backward
passing looks good statistically but does not advance the ball).

**How this became work (concrete model changes, run and reported):**
- The outcome model regresses win on the teamwork score **with two
  controls**: `opp_strength` = points the opponent earned in the *other*
  leg of the fixture (leave-one-out, no leakage) and `gap_mean` = the
  match's mean cumulative own-shot minus opponent-shot count in 15-minute
  blocks (game-state proxy). File: `code/model.py`.
- Volume is deliberately **not** a quality indicator: `n_pass` has OR 1.01
  (null) in the univariate fit, and pass rate by outcome (loss 279 / tie 232
  / win 302 passes per game) is reported as context, not evidence of
  quality.
- The teamwork score T is built from *structural* features (distribution
  evenness, network breadth, forward share) rather than volume, exactly the
  "penetration, not possession" distinction.
- The finding that raw volume/structure is weakly *anti*-correlated with
  wins (r = -0.32 for T) is framed as the common-cause artifact the expert
  described, not as "more teamwork is worse": after the controls, T's
  coefficient is small and not significant (see below), so the honest
  conclusion is that the observed passing structure does not carry an
  independent win signal once opponent and scoreline are accounted for.

## Exchange 3 — robustness threshold for recommendations (asked before the task-3 strategy step)

Question (paraphrased): how strong and consistent must a passing pattern be
before a coach should change training/tactics next season — half the games
enough, or nearly every game and still in the tougher matches?

Expert reply (key points): a pattern in ~50% of matches is noise, a
hypothesis, not a basis for change. The bar is: present in the large
majority of games (order of 70-80%+), showing up in both wins and losses
(not only when the team happens to win), surviving the tough matches (a
pattern that holds only against passive opponents is a matchup artifact),
and being a mechanism, not a mere correlation.

**How this became work (decision rule applied, run and reported):**
- The decision rule used in task 3: a structural pattern is *recommendable*
  only if (i) it is present in ≥70% of the 38 games, (ii) it appears in
  both wins and losses, and (iii) it holds in the strong-opponent subset
  (opp_strength ≥ 3). Files: `code/channels.py`, `code/model.py`.
- Applied to the D→F (defender-to-forward) channel: df_rate is elevated in
  wins (0.114 vs 0.090/0.080 in losses/ties), but it is above the season
  median in only 19/38 games (50%) and in 8/13 wins vs 11/15 losses. Under
  the threshold, this is a **hypothesis, not a recommendation** — it does
  not meet the 70% bar and it is more common in losses than wins. This is
  reported as the negative robustness result that shapes the advice: the
  network analysis does *not* identify a single universally effective
  channel, and the coach's actionable changes should target the features
  that do pass the threshold (consistency of the midfield hub, tempo
  discipline, late-game freshness via substitutions — see submission).
- The model's own fit check uses the same standard: the teamwork model's
  T coefficient (-0.105) lies inside the 200-shuffle null range (max |beta|
  = 0.148), so T is not treated as a reliable win signal; the submission's
  conclusions are restricted to statements that pass the consistency bar.

## Summary of values/constraints transferred from the exchanges

| Item | Value/range | Source | Where used |
|---|---|---|---|
| Passing network = completed passes only (floor on attempts) | definition | Exchange 1 | task 1 assumptions; all indicators |
| No completion-rate or raw-volume quality indicator | constraint | Exchanges 1+2 | indicator set in task 2 |
| Opponent-strength control (other-leg points, leave-one-out) | control variable | Exchange 2 | `model.py` outcome model |
| Game-state control (shot-gap in 15-min blocks) | control variable | Exchange 2 | `model.py` outcome model |
| Recommendation bar: ≥70% of games, wins and losses, holds vs strong opponents | decision rule | Exchange 3 | task 3 strategy filter (`channels.py`) |
| D→F channel fails the bar (50% of games; 8/13 wins vs 11/15 losses) | result | Exchange 3 criterion | task 3 negative recommendation |
