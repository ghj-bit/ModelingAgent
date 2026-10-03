# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — Problem 2020_D (Huskies Network)

Ten expert exchanges, one question each. Each reply is input: it became a
parameter, a constraint, a decision rule, or a change to the model. No reply
text is copied into the submission.

## Exchange 1
- **Question:** When a team wins, is it from passing/moving together, or from individual players shining on their own?
- **Reply (gist):** Wins usually come from coordinated multi-pass build-up, not individual brilliance. Individual quality acts as a *multiplier*, not the primary cause.
- **Turned into work:** Sets the dominant behavioral mechanism. The teamwork score is **team-level (coordination-driven)**, with individual player skill entering as a multiplicative factor rather than an additive one. This decides the structure of the scoring model in `model.py` (the `T` teamwork term is the base; star-player contribution scales it).

## Exchange 2
- **Question:** In a build-up from own goal up to attack, which positions receive the ball next?
- **Reply (gist):** Build-up flows G → D → M → F (goalkeeper → defender → midfielder → forward). Forwards receive late, near the attacking third.
- **Turned into work:** Validates the **layered, directed network structure**. The model treats the passing network as a directed, position-stratified flow and measures it with a "progression index" (average forward displacement of each pass) plus a position-chain check (G→D→M→F ordering frequency). This is the structural indicator used in the micro/meso/macro network analysis.

## Exchange 3
- **Question:** What makes a run of passes a good attacking move, not just a long chain?
- **Reply (gist):** Forward/dangerous progression, breaking lines, and an end product (shot/chance/penetration). Long lateral chains that never threaten goal are "sterile possession."
- **Turned into work:** Defines the **success metric**: an attacking move is scored by (a) net forward advance, (b) zone gain (into attacking third / penalty area), (c) termination in a shot/chance. Implemented as the "effective attack" detector in `model.py` — a pass sequence earns credit only when it gains territory and ends near goal. Distinguishes productive from sterile possession.

## Exchange 4
- **Question:** When a team is losing late, do they pass shorter/safer or bigger/riskier?
- **Reply (gist):** Trailing teams take bigger, riskier, more direct passes (pass length and forward intent rise, completion drops). Protecting a lead → shorter, safer passing.
- **Turned into work:** Adds a **game-state-dependent tempo/risk parameter**. The model computes, per match, pass length and forwardness conditioned on the scoreline at that time (leading / level / trailing) and checks the expected direction (trailing ⇒ longer, more forward passes). This is the "adaptability/dynamical" indicator.

## Exchange 5
- **Question:** On a strong team, do touches concentrate on a few stars or spread evenly?
- **Reply (gist):** Strong teams spread touches fairly evenly (broad distribution, midfield as hub, forwards fewer-but-more-dangerous). High concentration ⇒ weaker, dependent teams.
- **Turned into work:** Defines the **contribution-distribution metric** = Gini coefficient of touches (and of pass counts) across the 30 Huskies players. Lower Gini = more balanced = better teamwork. This is a first-class performance indicator alongside coordination.

## Exchange 6
- **Question:** Which part of the field do successful attacking passes aim at?
- **Reply (gist):** The central attacking zone in front of goal / inside the penalty box, central attacking third, and space behind the defensive line. Flanks and own-half are lower value.
- **Turned into work:** Defines the **spatial value weighting** used in pass scoring: a pass's value is weighted by the destination zone (central penalty area / central attacking third = high; flanks and own half = low). Implemented as a zone-value table in `model.py` keyed on destination x (forwardness) and y (centrality).

## Exchange 7
- **Question:** Do chances come more from open-play passing or set pieces?
- **Reply (gist):** Open play produces ~70–80% of goals/chances; set pieces ~20–30%.
- **Turned into work:** Calibrates the **open-play vs set-piece weighting** in the chance-creation model. The season "expected-chances" estimate weights open-play attacks and set-piece attacks in that ratio; the model verifies the data's own split against it. Recorded as an empirical parameter with interval [0.7, 0.8] for open play.

## Exchange 8
- **Question:** How much does it matter that the receiving teammate is already in a good position?
- **Reply (gist):** Receiver position (space, orientation, options) is a *primary* determinant of pass value, arguably more than the pass itself. Passing to a well-placed, open, forward-facing receiver creates value; passing to a marked/backward receiver kills the move.
- **Turned into work:** Adds the **receiver-position term** to the pass-value formula. Pass value = f(forwardness) × g(destination zone value) × h(receiver spatial quality). The receiver term is the destination centrality/forwardness, making the model's pass score depend on *where the receiver is*, not just the pass vector. This is the micro (dyadic) scale indicator.

## Exchange 9
- **Question:** Across a season, how should a coach judge whether the team's approach is working?
- **Reply (gist):** By whether *process and results align* over the season: sustained chance creation, balanced involvement, adaptability across opponents/home-away/game-state, converting into points. Good results with poor process = fragile; good process with lagging results = sound, needs finishing/luck.
- **Turned into work:** Defines the **season-level evaluation**: a composite that aligns a process score (coordination + balance + progression) with a results score (points, goal difference), and explicitly separates "deserved" (underlying) from "achieved" (scoreline) to flag fragility. This drives the advice to the coach in subtask 3 and the generalization in subtask 4.

## Exchange 10
- **Question:** If you could change just one thing about a struggling team's passing, what would it be?
- **Reply (gist):** Improve the *quality of progression, not the quantity* — make passes purposeful and forward/dangerous into central areas, breaking lines, to well-placed receivers. Not more passes or higher completion.
- **Turned into work:** Defines the **primary coaching recommendation** and the model's top-priority indicator. The model is built so that the single most actionable output is the "progression quality" gap (forward/central effective passes vs. total passes), and the advice to the coach in subtask 3 leads with this. Closes the loop with Exchange 3.

## Consolidated parameter table (empirical inputs)

| name | value | interval | source |
|---|---|---|---|
| open_play_share_of_chances | 0.75 | [0.70, 0.80] | expert exchange 7 |
| coordination_drives_wins (qualitative structure) | team-level term is base, individual = multiplier | n/a (structural) | expert exchange 1 |
| buildup_flow | G→D→M→F ordering | n/a (structural) | expert exchange 2 |
| dangerous_zone | central penalty area / central attacking third | n/a (structural) | expert exchange 6 |
| receiver_position_weight | primary determinant of pass value | n/a (structural) | expert exchange 8 |
| balance_indicator | low Gini of touches = stronger | n/a (structural) | expert exchange 5 |
| game_state_effect | trailing ⇒ longer/more forward passes | n/a (structural) | expert exchange 4 |
| season_judgment | process ∩ results alignment | n/a (structural) | expert exchange 9 |

Dataset-derived values (no expert input needed): all counts, player IDs,
positions, coordinates, times, match results — from `data/*.csv`.
