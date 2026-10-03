# Interaction evidence — 2024_C (Wimbledon momentum)

Ten exchanges, one question each, in order. For each: question, reply (summarized), and the concrete effect on the work.

## Exchange 1
- **Q:** In a close Grand Slam match, is a player who has just lost several points in a row usually visibly less focused or confident at the start of the next game?
- **A:** Not reliably. The effect is weak, short-lived, and resets at the changeover; elite players treat each game as a fresh unit. Visible loss of focus is more likely after losing a game on serve or squandering break points, not after a point run alone.
- **Effect:** This fixed the structural rule of the momentum model: the EWMA state is *reset at every game boundary* (multiplicative discount), not a continuous decay. Parameter `game_boundary_reset_weight = 0.3` (interval [0.3, 1.0], sweep-validated) encodes the partial-reset: the state is not zeroed (some form carries over) but strongly discounted. Also motivated the exclusion of tiebreak games from swing labels (no serve structure to reset against).

## Exchange 2
- **Q:** How many seconds do tennis players get for the changeover between games, and how many seconds at a set break in a Grand Slam?
- **A:** 90 seconds between games; 120 seconds at a set break (ITF Grand Slam rules).
- **Effect:** Parameter table entries `changeover_duration = 90 s` and `set_break_duration = 120 s`, intervals [90,90] and [120,120]. These justify the game-boundary reset (a discrete rest interval exists in the physics of the match) and are cited in the solution.json parameter table with source "expert exchange 2".

## Exchange 3
- **Q:** At the end of a set in a Grand Slam, do players switch ends before the two-minute rest?
- **A:** Yes. Change ends first, then the 120-second break; the clock starts once the change is complete.
- **Effect:** Confirmed the set-break is a single 120 s event (not 90 s + ends-change), so the model applies one reset of weight 0.3 at set boundaries, not two. Also used in the coaching memo (end-change is a physical state reset).

## Exchange 4
- **Q:** When the lead player on serve faces break points, do top players typically hit harder and take more risks, or play it safe?
- **A:** Neither uniformly; the dominant pattern is not "hit harder". Most elite servers lean on their best, highest-percentage serve and avoid double faults; risk-taking rises only on second serve or for first-strike players. Many become more conservative.
- **Effect:** Informed the swing-predictor's `bp` and `bp_lead` features and their interpretation: break points are *not* the moment of maximum swing risk (the model found coefficients -0.47 and -0.31, i.e. swings are less likely on break points). The coaching advice "reinforce the conservative serve routine in the danger window" is grounded in this reply.

## Exchange 5
- **Q:** At Wimbledon, do top players usually serve harder on break points, or hit their safer, higher-percentage serve?
- **A:** Safer, higher-percentage serve. Grass rewards placement over pace on big points; risk-taking only on second serve on break point or for first-strike players.
- **Effect:** Confirmed exchange 4 for the specific surface (grass/Wimbledon). Strengthened the surface-generalizability claim in task 3: the "tighten on big points" behavior is surface-consistent, so the model's big-point coefficients should transfer across surfaces after re-fitting baselines.

## Exchange 6
- **Q:** In the deciding fifth set of a Grand Slam, do players generally change their style, or keep the same plan all set?
- **A:** Keep the same plan with modest tightening: higher first-serve percentage, fewer unforced errors, more selective attacking. No wholesale style change; individual variation is large.
- **Effect:** The model includes `set_no` as a feature (near-zero coefficient, -0.045, consistent with "no style change") and the coaching memo advises "keep the plan, tighten execution" for deciding sets. Also supports treating the fifth set of the final (Alcaraz 6-4) with the same model parameters, not a separate regime.

## Exchange 7
- **Q:** When a player is one set point or match point away from winning, do they usually play tighter or bolder?
- **A:** Usually tighter (conservative, error-averse), but modest and individual. The returner facing the point often plays freer. Tightness shows most on serving for set/match (double faults, tentative second serves).
- **Effect:** The `set_pt` feature's coefficient (-0.534) is negative — swings are less likely at set/match points — matching this reply. The coaching memo's point 4 ("big points are where players tighten, not where swings happen; prepare lock-down routines") is grounded here.

## Exchange 8
- **Q:** Do coaches believe short runs of lost points signal a real drop in form, or are they mostly random?
- **A:** The analytical view (the problem's coach persona) holds short runs are mostly consistent with chance; point outcomes are near-independent with win probabilities ~0.6-0.65, so runs of 3-5 occur frequently by chance. The traditional view attributes runs to specific causes (serve falter, physical issue), not self-sustaining momentum. Coaches agree short runs are weak evidence; longer runs, runs crossing game boundaries, or runs with a visible technical change are taken more seriously.
- **Effect:** This directly shaped the coach-claim test (task 2): the null model is i.i.d. with the data's own consecutive-win probability, and the "run" scale is L_min = 3 (the coaching-relevant scale). The result (ratio 0.98, observed = expected) is the quantitative confirmation of the expert's "mostly random, weak signal" view, and the memo's point 2 ("do not react to short runs") follows.

## Exchange 9
- **Q:** Before a big match against a new opponent, what do tennis players focus on most in preparation?
- **A:** Opponent's patterns and their own serve/return plan: scouting serve placement on big points and by court, return position, backhand/forehand weakness, fatigue/movement issues; building a specific game plan; rehearsing trusted patterns; match-day logistics. Physical/mental conditioning is done in prior weeks, not the final pre-match window.
- **Effect:** The task 4 memo's preparation advice (point 5) is this: opponent-specific tactical scouting plus consolidating one's own reliable patterns. It also justifies why the model's features are *point-level* (serve placement context, rally length, big-point flags) rather than physical-conditioning variables — those are not observable in the data and, per the expert, are not the pre-match focus.

## Exchange 10
- **Q:** Do these preparation habits apply equally to women's matches and shorter table-tennis rallies, or only long Grand Slam points?
- **A:** They apply broadly but the emphasis shifts: women's Grand Slam matches use the same process (different tactical content); table tennis uses the same logic compressed to serve/receive and the first three balls (rallies are short, so rally-construction planning is minimal).
- **Effect:** The task 3 generalizability answer: the framework transfers to women's matches (same structure, re-estimate baselines), other surfaces (re-fit serve probabilities), and table tennis (replace the game-level swing definition with point-level; the "long one-sided run predicts the flip" mechanism is expected to survive). This is the boundary-condition answer that closes the "how generalizable" sub-question.

## Cross-cutting usage
- Exchanges 1-3 fixed the *structure* of the momentum model (game-boundary reset, 90/120 s intervals, ends-change sequence).
- Exchanges 4-7 fixed the *interpretation* of the swing predictor's big-point features and the coaching rules for big points.
- Exchange 8 fixed the *null hypothesis* of the randomness test.
- Exchange 9 fixed the *preparation advice* in the memo.
- Exchange 10 fixed the *generalizability domain*.
- No expert reply was copied into solution.json; all values travel as numbers, constraints, or equations in my own formulation. All empirical numbers in solution.json are either in its parameter tables (with source = exchange or supplied dataset) or come from the supplied dataset.
