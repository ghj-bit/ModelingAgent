# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — Problem 2020_D (Huskies passing network)

Three exchanges, one question each, asked in sequence before the work they governed.
Files: `../logs/operator_feedback/expert_question_N.md`, `expert_request_N.json`, `expert_reply_N.json`.

## Exchange 1 — structural assumption (asked before building the season network)

**Question (verbatim file):** "From experience watching or playing soccer: are the pass patterns a team uses in one season basically the same habit set, or do players change their passing habits match to match or during a game?"

**Expert reply (summary):** A recognizable baseline style exists and is fairly stable across a season, but the realized pass network in any single match is a context-dependent variation: it shifts with opponent and scoreline (leading = sideways/backward, lower tempo; chasing = direct, longer, riskier), with clock/fatigue/substitutions, with personnel, and with home/away conditions.

**How the reply became work:**
- Parameter/constraint: the analysis design was split into a **season-level macro network** (stable baseline) and a **per-match / 5-minute-bucket micro layer** (context-dependent variation). This is the two-scale structure of Task 1's model; without this reply the pooled season network would have been treated as the only level.
- Constraint added to Task 2: any indicator claiming to predict outcome must be checked for consistency *within* match contexts, which motivated the match-level direction-consistency test.
- Interval: holds across a full season of one team (38 matches, 3 coaching regimes in this data).

## Exchange 2 — causal mechanism (asked after the structural baseline was established)

**Question (verbatim file):** "Teams vary their passing game by match situation. When a team is winning, what do players typically do with the ball to preserve the lead?"

**Expert reply (summary):** Winning teams switch to lower-risk, ball-retention passing: more sideways and backward passes, shorter and safer passes concentrated among defenders and holding midfielders, fewer forward/penetrative/long passes and crosses; the network concentrates in the back line and holding midfielders to run down the clock and avoid dangerous turnovers.

**How the reply became work:**
- Hypothesis turned into a computed test (`scoreline_test` in `code/network_model.py`): H = "forward displacement is smaller in winning matches than in losing ones".
- Result: E[dx | win] = 3.84 vs E[dx | loss] = 4.11 field units; backward share 0.407 (win) vs 0.394 (loss). **Verdict: directionally confirmed, small magnitude (~6% of mean displacement).**
- This became Task 2's scoreline-response model and Task 3's Rule B (make retention-when-leading an explicit, trained rule with target forward share < 0.55, since the observed effect is smaller than best practice).
- Causal framing (per exchange policy): the scoreline->passing link is treated as a behavior the team can control; the passing->outcome link is kept correlational because opponent quality moves both.

## Exchange 3 — interpretation threshold (asked after the mechanism was quantified)

**Question (verbatim file):** "As a coach, how much difference in a team's passing patterns between winning and losing games would you need to see before trusting it as a real coaching problem worth fixing?"

**Expert reply (summary):** Coaches trust a pattern only on recurrence and consistency, not magnitude alone: the same directionally stable shift across roughly a third or more of the season's games (10+ of 38), recurring under the same condition. A shift in isolated games, or one that flips direction, is noise (scoreline, opponent quality, game state confound it).

**How the reply became work:**
- Decision rule embedded in the analysis: an indicator is reported as decision-relevant only if its win-vs-loss direction is stable in >= 10 matches; otherwise it is reported as "no evidence / noise".
- Applied: opponent shots (r=-0.576, p=0.0002, stable across the decisive matches) passes the rule -> Task 3 Rule A (high confidence). Forward share is direction-consistent (median-above fraction 0.385 in wins vs 0.533 in losses) but small -> Task 3 Rule B (medium confidence). Gini r=+0.317, p=0.052 -> Rule C (exploratory). Density, forward/backward share, and both entropies (|r|<0.16, p>0.35) fail the rule -> reported as honest null results, and the coach is explicitly told not to train on variety.
- The rule also set the confidence labels (high/medium/exploratory) in Task 3's recommendations.

## Compliance notes

- No exchange asked for coding, debugging, math derivation, or computation help.
- No expert phrasing is copied into `solution.json`; only the values, hypotheses, thresholds, and their outcomes (all computed in `code/network_model.py`, logged in `logs/network_model.log`) are integrated.
- All empirical numbers in the submission are computed from the task's own dataset; no external literature parameters were needed, so no search-based calibration table exists.
