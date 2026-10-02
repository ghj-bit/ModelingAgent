# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — Problem 2020_D (Huskies soccer passing network)

## Exchange 1 — structure of the teamwork signal
**Question (file: logs/operator_feedback/expert_question_1.md):** When you scout a team, what passing habit most clearly shows they play as one unit, not eleven individuals?

**Reply (abridged):** The clearest sign is a dense, reciprocal passing core among outfield players — the ball circulates through many players, most give and receive from several teammates, few isolated nodes. The opposite — one or two hub players dominating origins and destinations with near-isolated others — reads as individuals plus a distributor. Secondary sign: balanced involvement, no large gap between busiest and quietest outfield players. Qualitative, not a precise threshold.

**How the reply turned into work:**
- Added a match-level cohesion indicator with two parts, implemented in `code/analysis.py`:
  1. Pass reciprocity `R = 2·|{(i,j): i→j and j→i}| / (|out-stubs| + |in-stubs|)` on the Huskies' outfield pass dyads (goalkeeper excluded as a structural non-participant in midfield circulation);
  2. Involvement balance: ratio `B = p90/p10` of per-player pass involvement (out+in), with `p10` floored at 1 to keep the ratio finite; lower B = more balanced.
- The expert's hub-and-spoke warning is operationalized as an anti-metric: a hub player = the argmax of in-degree share; its share is reported per match and per season.

## Exchange 2 — dominant selection mechanism
**Question (file: expert_question_2.md):** Do the same players keep getting the ball in every match, or does who plays the ball shift a lot from game to game?

**Reply (abridged):** It shifts a lot. The passing network is not stable across matches: dominance depends on opponent pressing/shape, score/game state, lineup, rotation, injuries, substitutions, and tactic (defending deep vs dominating possession). A stable core of regular starters exists, but their pass share and network position vary substantially match to match.

**How the reply turned into work:**
- Season aggregates are computed as means over matches, **never** as a single pooled network: pooling would mix opponents, scorelines, and lineups into one artificial structure and mask the game-to-game variance the expert says is the real signal.
- Match-state conditioning: all Huskies indicators are computed separately for (a) full match, (b) minutes 0–45 vs 45–90 of the match clock, (c) the last-20-minute segment, to expose tactic-switch dynamics (defending vs attacking phases).
- Opponent-conditioned contrast: indicators are computed per OpponentID (2 home + 2 away games each) and the between-opponent spread is reported, so "universal strategy" vs "opponent-dependent strategy" (Problem 2's explicit question) is answered with numbers, not assertion.
- Substitution events from fullevents.csv are parsed to identify lineups; late-game involvement changes test the substitution-effect channel.

## Exchange 3 — validation / interpretation criterion
**Question (file: expert_question_3.md):** If one squad habit shows up in only a few games, how many matches would you want it to last before calling it a real trait?

**Reply (abridged):** A handful of games is not enough. A pattern should appear in at least about a third to half of the season — roughly 12–19 of 38 games — and ideally recur across different opponents and both home and away, before it counts as a real trait rather than a matchup-specific or short-run artifact.

**How the reply turned into work:**
- Persistence gate applied in `code/analysis.py`: a structural habit (e.g., "reciprocal core between player pair (i,j)", "balanced involvement", "dominant 2-way dyad") is classified **stable** only if it holds in ≥ 12 of 38 matches (~1/3, the low end of the expert's band, applied as a filter — 19 would over-filter a 38-game sample) AND in ≥ 2 different opponents AND in both home and away fixtures. Everything below the gate is reported as **transient** (likely matchup/lineup-driven) and is excluded from the advice-to-coach conclusions (Problem 3) but retained in the descriptive results.
- This gate is the operational distinction between "team trait" and "artifact of a particular matchup", which is the bias analysis for the season-level claims.
