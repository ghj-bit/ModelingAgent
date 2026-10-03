# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — MM-Bench 2024_C (tennis momentum)

Policy: mechanism → constraint → parameter sequencing; 10 fixed exchanges; each reply
converted into a model element before the next question. Questions in
`logs/operator_feedback/expert_question_N.md`, replies in `expert_reply_N.json`.

| # | Question (≤20 words) | Reply (gist) | How it changed the work |
|---|---|---|---|
| 1 | When a tennis player is clearly dominating, what does the other player do to stop the slide? | Change something: adjust serve patterns/return position/rally tactics, use pauses to break tempo; convert the few break chances that appear. | Defines the *recovery mechanism*. Swings are treated as state changes in play pattern, not isolated points → features in the swing model must include pattern-change indicators (serve width fraction, error/winner rates, break-point events). |
| 2 | When a player tries to break rhythm, what mainly makes it fail? | Failure when the change is not sustained (revert after 1–2 points), mis-targeted, or low-percentage (forcing errors); a strong opponent can absorb variation. | Establishes the *constraint* on the recovery mechanism: persistence + targeting. Justifies the lookback window (sustained change over a few games, not a single point) and the requirement that a swing label requires a preceding opposite stretch (≥2 games) — a one-off blip is not a swing. |
| 3 | About how many points of a comeback streak before you'd trust it's real, not luck? | ~8–12 points with a change in how points are won; below 5–6 points it is indistinguishable from random variation. | **Parameter:** run threshold K. Prediction label uses K=5 (conservative lower bound of the 5–6 noise floor); the momentum flow visualization treats runs <5 points as noise. Interval [5, 12] recorded. |
| 4 | How many minutes to settle back into rhythm after a disrupted stretch? | No fixed number; visible within ~1–2 service games (5–10 min); brief interruptions fade within a game; >15–20 min of poor play means the change failed. | **Parameter:** recovery/settling window ≈ 1–2 service games. Sets the EWMA half-life scale (games, not minutes) and the feature lookback (~3 games ≈ 30 points ≈ one settling window). |
| 5 | Which small signs first hint a slump is turning around? | Serve quality returns first (hold serve comfortably), fewer cheap unforced errors on routine balls, winning "free" points, longer competitive rallies. | Feature design: my_uferr_rate, my_win_rate, rally_avg, break-density and serve-pattern features are the *leading* indicators; model weights (see results) confirm flow/pressure terms dominate, consistent with these cues being early but partial. |
| 6 | Coaching a player against a swing-prone rival, what habit is emphasized most? | Fixed repeatable between-point routine; play each point on its own terms; hold serve as anchor, don't chase during opponent's hot stretch. | Basis for the coach memo's core advice (stable self-level, serve as anchor) and for interpreting the momentum metric operationally: a player "loses" flow mostly through their own error/serve drift, which is what the metric's serve-corrected surprise actually measures. |
| 7 | Do swings happen in table tennis about as often as in tennis? | Yes in kind/frequency; shorter swings, more game-decisive, less serve-anchored (serve advantage smaller, ~55–60% vs 60–70%). | Generalizability section: the serve-corrected EWMA transfers in form; the serve-advantage baseline parameter must be re-estimated per sport (here 0.673 overall from dataset; expert range 0.60–0.70 men's, 0.55–0.62 women's, 0.55–0.60 table tennis). |
| 8 | In a deciding fifth set, do swings look different? How? | Fewer but shorter and heavier swings; anchored to serve and high-pressure points; often driven by one player's level dropping (fatigue). | Justifies the `set_no` feature and the finding that late-set swings are break-point-driven; supports the "level-drop, not level-rise" reading of the final's fourth-set reversal in the case study. |
| 9 | Which moments most reliably trigger a player to play worse? | Self-inflicted losses on high-stakes points: double faults/unforced errors on break or set points, failed break-point conversions, lost game from 40-0, broken right after breaking. | **Feature:** `self_loss_pressure` = self-inflicted point losses on break points in the last ~3 games; appears in the top-4 coefficient ranking of the fitted model, confirming the expert trigger list is statistically present. |
| 10 | Do women's matches show flow swings like the men's? | Yes, same triggers and structure; weaker serve anchor (~55–62% vs 60–70%), more frequent smaller swings (breaks/re-breaks common). | Generalizability: model is sex-invariant in form; only the serve-advantage baseline shifts, so the same code applies to women's data with a re-estimated baseline. Recorded as an interval, not a dataset value (women's data not in this dataset). |

## Parameter table (empirical inputs with provenance)

| name | value | interval | source |
|---|---|---|---|
| server point-win rate (dataset, overall) | 0.6731 | [0.60, 0.70] | task dataset Wimbledon_featured_matches.csv (31 matches, 7284 points); expert exchanges 7, 10 |
| server point-win on first serve (dataset) | 0.7541 | [0.65, 0.85] | task dataset |
| server point-win on second serve (dataset) | 0.5295 | [0.40, 0.65] | task dataset |
| break-point conversion (dataset) | 0.3512 | [0.30, 0.40] | task dataset |
| per-score-state server win probabilities | match-specific, shrinkage prior 0.70 (30-point pseudo prior) | state-dependent | estimated from task dataset per match (momentum.py `build_win_probs`) |
| tiebreak server edge | 0.52 (shrinkage) | [0.35, 0.75] | estimated from task dataset, clamped |
| EWMA half-life (points) | 20 | [10, 40] | sweep in momentum.py (`--sweep`): 10→12 runs/max\|M\|=1.38; 20→8/2.15; 40→3/3.15; chosen 20 balances run count vs noise; consistent with expert reply 4 (settling over ~1–2 games ≈ 10–20 points) |
| swing-run threshold K (points) | 5 | [5, 12] | expert exchange 3 (runs <5–6 indistinguishable from noise; 8–12 trusted) |
| preceding opposite streak required | ≥2 games | — | expert exchange 2 (change must be sustained) |
| feature lookback for rate features | 30 points (~3 games) | [20, 40] | expert exchange 4 (settling within 1–2 service games) |
| women's serve advantage (generalizability) | ~0.55–0.62 | [0.55, 0.62] | expert exchange 10 (not in dataset) |
| table-tennis serve advantage (generalizability) | ~0.55–0.60 | [0.55, 0.60] | expert exchange 7 (not in dataset) |
| tennis serve advantage (men's, literature cross-check) | ~0.60–0.70 | [0.60, 0.70] | expert exchanges 7, 8; dataset value 0.6731 lies inside |

Every other number in the submission is computed from the task dataset by the
scripts in `code/` (momentum.py, predict2.py, metrics_summary.py) with logs in `logs/`.
