# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction evidence — 10 expert exchanges

Protocol: one question per exchange, written to `logs/operator_feedback/expert_question_N.md`, answered via `wait_for_expert_reply.py` (replies in `expert_reply_N.json`). Expert text is treated as input, never copied into the solution.

## Exchange 1
- **Question:** In a long tennis match, which matters more to a player's form: the last few points just played, or the whole stretch since the last break of serve?
- **Reply (substance):** Depends on the horizon. Point-to-point execution decays within a handful of points (short carry-over); game/set-level state is governed by the stretch since the last break of serve, which is the natural reset boundary of the scoreboard. Momentum-like runs are modest and largely explained by serve alternation.
- **Effect on the work:** Set the two-timescale design of the momentum index: (a) point-outcome carry-over with a short half-life, (b) state reset at each break of serve. Chose half-life 6 points (order of "a handful") and the break-reset EWMA as the core state; kept game score as a separate structural feature.

## Exchange 2
- **Question:** In practice, what makes a server lose control of their serve during a match — is it mostly physical tiredness, or mental pressure?
- **Reply (substance):** Mostly mental pressure; fatigue is secondary and gradual. The tell is abrupt, score-linked loss of control (serve percentage drops, double faults cluster when serving for the set) vs. a gradual, time-linked decline for fatigue.
- **Effect on the work:** Justified conditioning the swing-prediction triggers on score state (advantage/break points, serving for the set) rather than match time; used abrupt double-fault clustering, not elapsed time, as the mental-pressure signal in the indicator model.

## Exchange 3
- **Question:** When a player is about to break a rival's serve, do coaches usually say it's the rival's double faults, lost second serves, or their own aggressive returns that make the break happen?
- **Reply (substance):** Coaches frame breaks as created by the returner's aggression; the server's second-serve weakness is the enabling condition and double faults the symptom that pressure has taken hold.
- **Effect on the work:** Treated server errors (double faults, lost points on second serve) as *indicators of deteriorating server state* that feed the momentum index and swing triggers, rather than as independent causes; the break itself resets the index (see exchange 1).

## Exchange 4
- **Question:** When a player loses their first big point of the match, do they usually recover right away, or does the shake-up last through several more points?
- **Reply (substance):** Recovery is usually within a point or two; what persists is the structural score state produced (lost break/set), not a psychological carry-over. Repeated losses of big points (a tightening pattern) are what produce longer slumps.
- **Effect on the work:** Argued against a "big-point shock" term that decays over many points; instead the model carries consequence through the score structure and through repeated-event streaks (losing streak of the leader), which is exactly what the streak feature of the swing predictor captures.

## Exchange 5
- **Question:** Which single shot does a player lose control of first when they start cracking — their serve, forehand, or backhand?
- **Reply (substance):** The serve goes first: it is the only fully self-initiated stroke, most pressure-sensitive; groundstrokes hold up longer because they borrow rhythm from the incoming ball.
- **Effect on the work:** Gave serve-side statistics (serve win rate, double faults on serve) priority in the feature set; the server-advantage prior and serve-state features are the backbone of both the momentum index and the swing triggers.

## Exchange 6
- **Question:** In a tight match, what does a player watch for to know the opponent is struggling — long points they win, quick errors, or slow returns?
- **Reply (substance):** Hierarchy: quick errors first (clearest, earliest tell of mental tightening), then slow returns/movement (physical, late-match), while long points the opponent wins are the opposite of a struggle sign.
- **Effect on the work:** Defined the swing-prediction tells: double faults and clusters of unforced errors in the last few points ("quick errors") as trigger features; explicitly excluded long-rally-won indicators and treated long rallies as neutral. This is the Stage-2 trigger of the two-stage swing rule.

## Exchange 7
- **Question:** Do top players handle a tough stretch by changing their game plan, or by staying calm and playing the same shots?
- **Reply (substance):** Top players stay calm and keep the same shots through a tough stretch (variance, not a broken plan); genuine plan changes come only from persistent structural problems across games.
- **Effect on the work:** Supported a short-memory momentum process: a losing run alone should not permanently shift expectations (the index mean-reverts toward the server prior), which is why the EW index is used as a *temporary* deviation blended with the structural server term rather than as a persistent state.

## Exchange 8
- **Question:** When coaching a player to a match, is studying the rival's weaknesses more important than preparing the player's own confidence and routines?
- **Reply (substance):** Own routines and confidence are the base; rival scouting is a secondary modifier that only works if the player can execute.
- **Effect on the work:** Informed the generalizability argument: models of *one player's* routine-like tendencies (serve win rate, error rates) transfer better across matches than models of a specific matchup, so the swing predictor is built from within-player, within-point features (serve state, own errors, streaks) rather than opponent-specific terms.

## Exchange 9
- **Question:** Can a coach realistically use point-by-point data from other matches to predict how a player will react under pressure in a new match?
- **Reply (substance):** Only weakly, and only as a prior on stable tendencies (serve %, error rate on big points over many pressure points), never as a reliable forecast of a specific new match; pressure samples are small and noisy.
- **Effect on the work:** Set the evaluation protocol for the swing-prediction model: train on the focus match 2023-wimbledon-1701, freeze the rule, and test on the other 30 matches as an out-of-sample prior; report that the transferable part is the *shape* of the indicator (neutral-momentum zone + quick-error tell), not precise probabilities.

## Exchange 10
- **Question:** How reliable are the serve speeds and unforced-error counts in official match statistics, in your experience?
- **Reply (substance):** Serve speed is radar-measured (accurate to ~±1-2 mph, good for within-match comparison, not precise cross-event comparison). Unforced-error counts are the least reliable official stat: human chartist judgment, broadly consistent within one match but noisy across matches.
- **Effect on the work:** Restricted speed_mph to within-match relative use only (and excluded it from cross-match predictors); treated unforced-error features as noisy tells (used in clusters/thresholds, never as exact counts) and reported this as a data-quality limitation of the swing-prediction model.
