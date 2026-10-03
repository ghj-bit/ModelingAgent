# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence

Problem: MM-Bench 2024_C — tennis momentum in the 2023 Wimbledon final (Alcaraz vs Djokovic, match 2023-wimbledon-1701).

Interaction strategy followed: structural anchoring before numerical filling. 10 exchanges, exactly one common-sense question each, each ≤20 words, each building on the prior reply.

## Exchange 1 (structural)
Q: "In tennis, is short-term form driven mainly by the player serving, or by the player returning?"
A (summary): The server. First-serve points are won ~70–80% on tour; second-serve at/above 50%. Over short windows the serving player has a structural edge; "form" swings track who is serving and how well. Returning is a modifier (break-point conversion, disrupting rhythm), not the primary driver.
Work turned into: Established the dominant mechanism — serve dominance. This set the structure of the whole model: the point is standardized by a serve-specific expectation (first-serve vs second-serve point-win rate), so the "form" signal is the deviation from the server's structural edge, not raw point wins. Calibrated from data: first-serve server point-win = 0.755, second-serve = 0.529 (baseline mode of momentum_model.py, excluding 99 tiebreak points).

## Exchange 2 (structural — what breaks the mechanism)
Q: "What most often breaks a server's run of success and hands the game to the returner?"
A (summary): Most common breaker is a drop in first-serve effectiveness — missed first serves forcing attackable second serves, visible as a cluster of double faults, low first-serve %, or slower/less accurate serves. Second: returner raising their level at the right moment, converting break points. Dominant mechanism is serve degradation (the server's own game slipping), not the returner suddenly dominating.
Work turned into: Named the two causal features the prediction model uses — first-serve fraction / second-serve count, and double faults — plus break-point conversion. These became the feature set in predict_game.py.

## Exchange 3 (parameter, referencing serve-degradation)
Q: "For tour-level players, roughly what share of double faults per serve game signals a serve slipping?"
A (summary): ~1 DF per service game is a warning; 2+ in a game is a clear signal. Tour baseline is well under 0.5 DF/service game (often 0.2–0.3), so even one is above normal.
Work turned into: Set the double-fault threshold in the break-prediction rule at df≥2 (clear signal), with df≥1 as the softer warning used in the combined rule (bp_faced≥1 OR df≥2).

## Exchange 4 (parameter — memory horizon)
Q: "When a player seems 'in form,' how many recent points does that feeling usually reflect?"
A (summary): Roughly the last 5–15 points (~1–2 games). Below 5, a run is indistinguishable from noise (serving alternates, so 2–4 streaks happen by chance). Beyond 15–20 it is a sustained/set-level trend, not a hot streak.
Work turned into: Chose the momentum memory window. The exponential-momentum decay (half-life ≈4 points) and the W=8 feature window in predict_swings.py sit inside this 5–15 window; the <5-noise finding justifies not interpreting sub-5-point runs as form.

## Exchange 5 (structural — early indicator)
Q: "On the court, what early sign tells a coach the flow of play is about to turn?"
A (summary): The earliest reliable sign is a drop in the server's first-serve effectiveness — first serves going in less often, second serves frequent, returner stepping in. This shift precedes the visible swing (break point, double fault, lost game). The turn is signaled by the server's own service game slipping, not the returner dominating.
Work turned into: Confirmed the *lead* direction: serve-degradation features are leading indicators of a swing, so the model evaluates them at the point just before the swing, not after. This is the design of the "pre-swing" feature evaluation in predict_swings.py.

## Exchange 6 (boundary — when a lead is real)
Q: "How much of a lead should a player bank before it counts as a real advantage?"
A (summary): One break = real but vulnerable (routinely erased). Two breaks = banked. One set = real; two sets (best-of-five) = decisive. In points, a lead only feels banked once it exceeds the ~5–15-point noise window, so a 2–3 point cushion is not a real lead.
Work turned into: Set the magnitude threshold for counting a "swing" / a real momentum lead. The momentum metric's swing threshold (both sides of a zero-crossing must reach |m|>thr) and the interpretation that a lead below the noise window is not a real advantage feed the definition of a "real" swing vs a noise flicker.

## Exchange 7 (boundary — generalization)
Q: "Does short-term momentum behave the same in women's matches as in men's?"
A (summary): Broadly yes in mechanism, no in magnitude. Same structural drivers (serve dominance, serve degradation, break points, 5–15 window), so the qualitative model transfers. But women's tour serving is less dominant (breaks more frequent, holds less automatic), rally variance higher, so runs/swings are more common and short streaks noisier. Structure generalizes; parameters (serve win rates, break frequency, baseline swing rate) must be recalibrated, not reused.
Work turned into: Stated the model's generalization boundary and calibration requirement in the submission (limitations): the structural model transfers across women's matches, other tournaments and surfaces, and table-tennis-like rally sports, but the empirical parameters (serve point-win rates, break base rate, noise-window length) must be re-estimated on the new population rather than copied.

## Exchange 8 (parameter — reset speed)
Q: "How fast can a player reset after a bad run of points and start winning again?"
A (summary): A bad run is usually reset within about one game (a few points), driven mostly by the serve changing hands — a player who lost several return points gets the serve back within 2–4 points and reasserts control. Longer slumps across multiple service games are the exception and usually reflect a genuine problem (serve degradation, injury, bad matchup), not ordinary variance.
Work turned into: Justified the per-game recentering in the momentum metric and the finding that a sustained slump across several service games (not a single bad game) is the signal of a real problem — used in the memo's advice to coaches (do not over-react to one game; react to a multi-game serve-degradation trend).

## Exchange 9 (structural — pre-match indicator)
Q: "What past-match stat best tells a coach when a rival player is vulnerable?"
A (summary): The single most telling stat is the opponent's first-serve percentage (tied to double faults per service game). A rival with low first-serve % or DF-prone serve is structurally vulnerable — forced onto attackable second serves. Second: break points conceded/converted against them. These beat aggregate stats (winners, total points) because they identify the specific mechanism (serve degradation).
Work turned into: Basis for the pre-match preparation advice in the memo: profile the opponent's first-serve % and DF/service-game from prior matches to identify where to press; use break-point conversion against them as the second indicator.

## Exchange 10 (boundary — data needed to trust a read)
Q: "How many recent points does a coach need before trusting a read on the opponent's form?"
A (summary): Roughly 5–15 points (1–2 games); below 5 it is noise. For a coach the practical threshold is a full service game or two of the opponent serving — enough to see whether first-serve % and second-serve frequency are holding or slipping, since that is the mechanism that signals vulnerability.
Work turned into: Set the minimum observation length for trusting a form read / swing prediction to ~one service game (consistent with the W=8 window and the game-level break-prediction design). Used to state the model's data-requirement boundary in the submission.

## Note on verbatim non-use
The values and constraints above were integrated into the model (serve-adjusted momentum metric, double-fault and break-point thresholds, 5–15-point noise window, game-level recentering, recalibration requirement, pre-match serve-profile) in this author's own formulation. No expert sentence was copied into solution.json; the reply files under logs/operator_feedback/ hold the raw exchanges.
