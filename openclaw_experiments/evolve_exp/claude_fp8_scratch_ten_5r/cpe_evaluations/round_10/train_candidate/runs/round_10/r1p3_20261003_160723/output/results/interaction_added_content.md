# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence

Ten exchanges, mechanism → constraint → parameter sequence. Each reply is
converted into a model parameter, constraint, or equation change below.

## Exchange 1 (mechanism branch)

**Q:** What causes the biggest swings in control between players during a
hard-fought tennis match?

**A (summary):** Primary driver = break of serve / the service game (server
wins ~60–80% of points on grass). Secondary: clutch points (break/set points,
tiebreaks), clusters of unforced errors or winners, double fault at a critical
moment, and cumulative fatigue in later sets.

**Use in model:** Established the dominant behavioral mechanism. The point-win
probability baseline `p_p1(t)` is conditioned on server identity and score
state first, so the structural serve effect is separated from the residual
"form" signal. The momentum index `M_t` is defined as the filtered residual
after removing `p_p1(t)`. The 5×5 score-state lookup `S` is calibrated so the
aggregate server win rate matches the dataset value (~67%). Candidate flow
drivers (breaks, clutch points, UE clusters, fatigue) become the feature set
for the swing predictor (Subproblem 3).

## Exchange 2 (constraint branch)

**Q:** What stops a player's run of form in a tennis match, and around how
long do such runs usually last?

**A (summary):** Runs end via: the player's own serve game ending (break or
rotation to receive), a cluster of UEs/DFs, a successful opponent adjustment,
or physical/fatigue drift. Clutch points are where runs most often break.
Length: typically 2–5 consecutive points, occasionally 6–8, rarely beyond
8–10; in games, usually 1–2, rarely 3+.

**Use in model:** Set the run-length threshold for "swing detection" at
4 consecutive points (mid-range of the 4–6 from exchange 7, consistent with
the 2–5 typical from here). This is the `--runlen` parameter used in the
random-swing test (Subproblem 2). The constraint that runs end at clutch
points motivated including `p1_break_pt`/`p2_break_pt` as event markers in
the key-moments table. The constraint that runs end when the serve rotates
motivated the score-state conditioning (a run cannot persist across a serve
change without a break).

## Exchange 3 (parameter branch)

**Q:** In tiebreaks on grass, about how often does the point's server win it,
compared to normal games?

**A (summary):** Tiebreak server wins ~65–75% of points on grass (higher than
the ~60–65% for normal grass service points). First-serve points in tiebreaks
~70–80%, second-serve points ~50–55%.

**Use in model:** Set the tiebreak baseline `p_p1 = 0.68` for server=1
(midpoint of 65–75%). This is a separate branch in `point_winprob()` from the
non-tiebreak 5×5 lookup. The 1st/2nd serve split in tiebreaks (70–80% vs
50–55%) is consistent with the overall 1st/2nd serve split in the dataset
(75.4% vs 53.0%), so the serve-number adjustment (+0.04 / −0.12) is applied
in both branches.

## Exchange 4 (constraint branch)

**Q:** What is the one physical limit that most often causes a player's game
to collapse mid-match?

**A (summary):** Aerobic/energy depletion — cumulative fatigue reducing
first-step quickness and serve/return quality, showing up as clusters of UEs,
double faults, and lost break points, especially in later sets. Heat and
hydration accelerate it.

**Use in model:** Added `set_no` and `p1_distance_run`/`p2_distance_run` as
features in the swing predictor (Subproblem 3), on the hypothesis that fatigue
accumulates with set number and distance run. The negative coefficient on
`M_lag1` in the trained model (−0.292) is consistent with fatigue-driven mean
reversion: as the flow-holder fatigues, the momentum index decays. The advice
to the player (Subproblem 3 outcome) includes preparing aerobic base and
heat/hydration for 4th and 5th sets.

## Exchange 5 (parameter branch)

**Q:** What single on-court sign most reliably tells a coach that the flow is
about to swing to the other player?

**A (summary):** A drop in first-serve percentage and first-step quickness in
the player who currently holds the flow — visible as more second serves,
shorter/defensive returns, and a cluster of UEs or DFs over a few points.
This precedes the break rather than following it.

**Use in model:** This is the leading indicator for the swing predictor.
The model proxies it through: (a) `serve_no` (more second serves → serve_no=2
frequency rises), (b) the momentum index `M_lag1` (a flow-holder whose serve
is dropping will start losing points, driving M toward zero), and (c) `rally_count`
(shorter/defensive returns → shorter rallies). The advice to the player
(Subproblem 3 outcome) explicitly names first-serve percentage as the
earliest observable marker to monitor.

## Exchange 6 (constraint branch)

**Q:** What is the main limit on what a coach can change during a tennis
match, while play is underway?

**A (summary):** The rules and the clock: no timeouts, intervention confined
to ~90-second changeovers and ~120-second set breaks. At Wimbledon 2023,
off-court coaching was from the stands only. What a coach can change:
verbal instruction and tactical adjustment (target, return position, serve
patterns, tempo, encouragement). Technique, fitness, stroke mechanics,
equipment are fixed.

**Use in model:** This is an operational constraint on the advice, not a
parameter in the equations. It shapes the Subproblem 3 outcome: the advice
to the player is limited to things executable in 90–120 second windows
(one target, one tempo change), not complex tactical overhauls. It also
explains why the model's in-match predictive signal must be simple enough
for a player to act on in a changeover (the momentum index sign and the
first-serve % trend are both readable in a 90-second break).

## Exchange 7 (parameter branch)

**Q:** How many points in a row does a player typically need to win to truly
"take over" a tennis match's flow?

**A (summary):** ~4–6 consecutive points, or about two consecutive games
(including a break), before the flow visibly shifts. Runs of 2–3 are common
noise; 4–6 spanning a break or hold-to-love is where control becomes
apparent. Beyond ~8–10 is decisive but rare.

**Use in model:** Set the flow-shift threshold at 4 consecutive points
(`--runlen 4` in the random-swing test). This is the cutoff used to compute
"fraction of runs ≥ 4" in both the observed and bootstrap distributions
(Subproblem 2). The "two consecutive games including a break" criterion is
reflected in the key-moments table, which flags break points and game
victors as the structural events where the flow index sign-flips.

## Exchange 8 (parameter branch)

**Q:** What first-serve percentage is typical for a top player on grass, and
how far does it drop when struggling?

**A (summary):** Typical: 60–70% for a match, elite servers 65–70%. When
struggling: drops to 45–55%, a fall of ~10–15 percentage points. A drop into
the low 40s or below is a clear sign of trouble.

**Use in model:** Parameter table entry: `first_serve_pct_typical = 0.65,
interval [0.60, 0.70]` and `first_serve_pct_struggling = 0.50, interval
[0.45, 0.55]`. These calibrate the serve-number adjustment in `p_p1(t)`:
the +0.04 for 1st serve and −0.12 for 2nd serve are chosen so that the
model's implied 1st/2nd serve split (75.4%/53.0% in the dataset) is
consistent with the expert's typical/struggling ranges. The advice to the
player (Subproblem 3 outcome) uses the 65% → 50% drop as the warning
threshold: if first-serve % falls below ~55%, the server's structural
advantage is eroding and a swing is likely within the next 1–2 games.

## Exchange 9 (mechanism branch)

**Q:** In a big-match flow swing, is it mostly physical fatigue or mostly
mental/psychological, in your experience?

**A (summary):** Mostly psychological. A lost clutch point, double fault, or
squandered lead triggers a shift in confidence, risk tolerance, and
decision-making; the player tightens or over-hits, the opponent gains
belief. The psychological turn precedes the visible physical decline.
Fatigue accelerates/exposes an already-fragile mental state rather than
initiating the swing.

**Use in model:** This determined the interpretation of the momentum index
`M_t`: it is primarily a psychological-form indicator, not a physical-fatigue
indicator. The negative coefficient on `M_lag1` in the swing predictor
(−0.292) is interpreted as the psychological mean reversion: after a player
gets "hot," confidence-driven risk-taking eventually produces an error or
a lost clutch point, and the flow reverts. The Subproblem 2 verdict
(point-level runs are near-random) is consistent with this: the psychological
swing operates at the game/set level (breaks, tiebreaks), not the point
level. The advice to the player (Subproblem 3 outcome) is therefore
primarily mental: rehearse the response to a lost break point or squandered
lead, because these are the psychological triggers.

## Exchange 10 (parameter branch)

**Q:** After a player takes a big swing, how long does the new "hot hand"
usually last before fading?

**A (summary):** Typically 1–2 games, or roughly 4–8 points, before it
fades. The most common pattern: the run carries through the remainder of the
current game and the next one, then normalizes. Beyond ~2 games or ~8–10
points is uncommon and reflects a genuine serving/level mismatch rather than
a transient hot hand.

**Use in model:** Set the momentum forgetting factor `lambda = 0.85`,
giving a half-life of `ln(0.5)/ln(0.85) ≈ 4.26` points, consistent with the
4–8 point fade time. This is the `--lambda` parameter in `model.py`. The
"1–2 games" pattern is reflected in the score-state conditioning: the
momentum index is allowed to persist across one serve rotation (the next
game) but the 5×5 lookup `S` resets at each new game (score returns to
0-0), so the structural baseline does not carry a run across games. The
advice to the player (Subproblem 3 outcome) uses the 1–2 game fade: a player
who is behind after a break should expect the flow to normalize within 2
games if they hold serve and convert their next break point.

## Summary of parameters from exchanges

| Parameter | Value | Interval | Source |
|---|---|---|---|
| server_win_rate_1st_serve | 0.754 | [0.70, 0.80] | task dataset |
| server_win_rate_2nd_serve | 0.530 | [0.48, 0.58] | task dataset |
| tiebreak_server_win | 0.68 | [0.65, 0.75] | exchange 3 |
| momentum_forgetting lambda | 0.85 | [0.80, 0.90] | exchange 10 |
| flow_shift_threshold (points) | 4 | [4, 6] | exchange 7 |
| first_serve_pct_typical | 0.65 | [0.60, 0.70] | exchange 8 |
| first_serve_pct_struggling | 0.50 | [0.45, 0.55] | exchange 8 |
| run_length_typical | 2–5 pts | [2, 5] | exchange 2 |
| run_length_decisive | 8–10 pts | [8, 10] | exchanges 2, 7 |
| hot_hand_duration | 1–2 games / 4–8 pts | [1, 2] games | exchange 10 |
| flow_swing_mechanism | psychological | — | exchange 9 |
| coach_intervention_window | 90 s / 120 s | — | exchange 6 |
