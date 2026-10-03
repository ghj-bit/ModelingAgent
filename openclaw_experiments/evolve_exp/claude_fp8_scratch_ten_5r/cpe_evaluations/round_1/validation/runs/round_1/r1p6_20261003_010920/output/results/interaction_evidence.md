# Interaction Evidence — MM-Bench 2020_D (Huskies passing network)

Ten expert exchanges. Each reply was converted into a parameter, window, decision rule
or diagnostic in `code/model.py` / `results/tables/`; none is quoted verbatim in solution.json.

| # | Question (gist) | Reply (gist) | Where the reply went into the work |
|---|---|---|---|
| 1 | What marks a team playing well together? | Players act as one connected unit: short, stable inter-player distances; quick short passes; a nearby option always available | Core hypothesis of the model: *compactness* = median pass length per match, inverted into the teamwork index T (`model.py`: `compact = g.pass_len.median()`, `z(-T.compact)`). Interval: all 38 matches. |
| 2 | What does the goalkeeper contribute to the unit? | Organizes/coordinates defensive shape and communication; full field view | Rationale for excluding the goalkeeper from the *passing* network (no G->G links observed, 0.0 in formation_blocks) and for reading defensive compactness through pass geometry (D-block rows) rather than GK actions. |
| 3 | How early is a team's shape readable? | Within first 10–15 min; read firms up ~15–20 min | Defines the "early window" of the first 15 min (AbsTime < 900 s) used for `early_len`, `early_rate`, and the early-shape diagnostic `corr(early_len, points) = +0.224`, `corr(early_rate, points) = +0.259`. |
| 4 | Who gets credit on winning teams? | The squad earns wins; contributions (goals, assists, support work) are distributed, even if reporting concentrates on stars | Motivates the *balance* indicator = 1 − Gini of passes per player; it is the single strongest single component (corr with points +0.242) and appears in T. |
| 5 | How do teams usually break down? | Fatigue and loss of compactness in the last 15–20 min or after sustained pressing: lines stretch, attack/defense disconnect | Defines the "late window" AbsTime ≥ 4500 s. Resulting diagnostic `late_len` correlates −0.391 with points (strongest of all indicators): losing matches show pass lengths growing late (late−early +1.78) vs winning matches shrinking (−1.92). |
| 6 | Does better connection beat individual talent? | Over a season usually yes, against comparable talent; single matches can go either way | Frames the model's scope as season-level and justifies correlating T with opponent strength (corr(T, opponent season points) = +0.310: stronger opponents were met by higher-connection games). |
| 7 | When a team is winning, does passing stay the same or speed up? | Character changes: same short base, more patient circulation punctuated by faster direct bursts; average speed looks lower | Tempo kept in T only as a secondary term; main T variant `T_def` (compactness + diversity + balance, no tempo) reported alongside. `tempo_character` result: winning-matches tempo 2.93 vs losing 2.72 passes/min, with similar forward bias — consistent with "same base, situational bursts" rather than uniform acceleration. |
| 8 | How long before a new player/tactic clicks? | ~5–10 matches for a player, 4–8 for a tactic (empirical, not fixed) | Sets the adaptability horizon: a change is judged over ≥5 matches, so the adaptability check splits the 38-game season into two 19-game halves and tests T stability by context (T std by half/side: 0.24–0.44). |
| 9 | What does a coach change first when struggling? | Tighten defensive shape, drop the line, simplify to safe short passing before adding creativity | Informs the S3 recommendations (defensive compactness first; short-pass simplification) and the interpretation of the high D->D (14.0%) and D->M (14.6%) block shares as the safety base the team should protect. |
| 10 | Formation vs connections, which matters more over a season? | Connections matter more; formation is only a starting template, connections convert it into results and survive opponent counter-strategies | Final framing: S4 generalization centers on the passing network (dyad/triad/connection indicators) rather than position template; the position block table is reported as the template within which the network operates. |

## Notes on what was NOT asked
No questions were needed for: network definitions (standard), coordinate scaling (given in data
docs), or statistics (computable). Search (`code/search.py data`) was used for a literature check on
typical pass distances; results were not specific enough to calibrate a parameter, so compactness is
normalized within-season (z-scores), which needs no external constant. The only externally sourced
numbers in the solution are the two empirical windows from exchanges 3 and 5 (15 min early / last
15 min), recorded in the parameter table of solution.json.
