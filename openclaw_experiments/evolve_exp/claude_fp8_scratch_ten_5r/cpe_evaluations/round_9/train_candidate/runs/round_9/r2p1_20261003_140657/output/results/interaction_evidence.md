# Interaction Evidence — MM-Bench 2024_C (tennis momentum)

Ten exchanges, one question each, mechanism → constraint → parameter sequencing.
Questions and replies in `logs/operator_feedback/`.

| # | Question (abridged) | Key content of reply | How the reply became work |
|---|---|---|---|
| 1 | What single thing tells you play swung? | A break of serve is the one event that cannot be explained by the baseline server edge; runs of points are common and often random. | Chose breaks as the anchor of the flow metric: point-level signal is serve-advantage-adjusted (x = ±1 vs. serve expectation), so breaks are what push the EMA away from the serve baseline. |
| 2 | Usual cause of a serve breaking down mid-match? | Drop in first-serve percentage, not power — fatigue/tightness pushes the server onto attackable second serves; the returner then dictates. | Made first-serve availability the central predictor: features `fv5` (first-serve rate over the last ~12 points) and `n2s` (share of second serves in the serving game) entered the break predictor; the momentum signal also keys on second-serve points. |
| 3 | How many games to recover after a break? | Usually the very next service game holds (~75–80% hold rate); what matters is whether the break is consolidated (breaker then holds → set usually decided) or broken back at once. | Validated hold rate in data: 83.9% overall. Defined "swing" as a sign change in the game-average momentum and checked consolidation: a break stands only if the breaker then holds, which the game-by-game timeline for 2023-wimbledon-1701 shows (e.g., set 3 breaks at games 1, 5, 7 all consolidated; set 4 break-back at game 9 erases the swing). |
| 4 | First moment you suspect an impending break? | Falling first-serve rate first; then a two-point deficit for the server (0–30/15–30); then break point. | Ordered the predictor features in that sequence (fv5 → n2s → elapsed/set). Verified in data: holds when facing 0 BPs = 98.7%, after 1 BP = 36.6%, after 2+ BPs (0–40/AD) = 47.7% — note 0–40 is easier to hold than a single BP (the "saved" pressure resets), which is exactly why the first-serve/deficit sequence, not the break-point flag alone, is the warning signal. |
| 5 | Does a set winner play noticeably stronger in the next set? | No consistent quality jump; what carries over is situational (serve order, loser's urgency), not a momentum boost. | No set-transition parameter in the model; the EMA memory (λ=0.1, ~half-life 6 points ≈ 1–2 games) is short enough that a set win decays rather than compounding. |
| 6 | Do breaks cluster or scatter? | Cluster: the same condition (first-serve dip, fatigue, hot return) persists over a stretch of games, so breaks bunch, then long runs of holds follow. | Tested clustering in data: observed per-match break counts vs. i.i.d. game-level simulation (same hold rate, same n_games, seed 42, 2000 sims). In the final target match: 10 observed breaks vs. 10.94 simulated (p95 16) — within random range; the dataset as a whole matches the i.i.d. expectation (186 breaks vs. ~190 simulated), i.e., clustering is present at the level of individual bad stretches, not in the match-level count. |
| 7 | How long does a bad serving stretch last? | A handful of games, typically two to four; rarely more than about half a set. | Set the momentum memory scale: λ=0.1 (half-life ≈ ln2/0.1 ≈ 6.6 points ≈ 1.1 games) so the metric tracks a 2–4 game stretch; the λ sweep (0.03–0.3) showed no setting that beats the serve baseline for next-game prediction, confirming the stretch is short and not exploitable as a persistent state. |
| 8 | Do swings show more in later sets? | Somewhat — fatigue lowers first-serve percentages for both players and stakes raise pressure, so sets 4–5 are more swing-prone; effect modest. | Checked in data: break rate by set = 14.9%, 17.6%, 16.0%, 14.8%, 18.5% — only set 5 shows a clear rise, a weak version of the expert's claim. Added `elapsed` (match hours) as a predictor; its coefficient ≈ 0 (0.002), so the data does not support a strong late-match swing effect. |
| 9 | What makes a player most vulnerable to a swing? | Structural: players whose point-winning depends on one fragile asset (serve) with no fallback; secondary: poor fitness, tightness on big points, one-dimensional games. | Basis for the coaching memo (task 4): the model's strongest signals are all about the serve (first-serve availability, second-serve share), which is the "single asset"; the memo advises managing serve consistency and avoiding over-pressing when the opponent's serve is under pressure. |
| 10 | How do players react right after losing a break point? | Two normal patterns: a deliberate serve reset (higher first-serve %, safer targets) → hold; or a flat, distracted game → another break chance. Rarely a sudden surge of aggression. | Informs the interpretation of the momentum trajectory after break points: a rising curve after a lost BP is the reset pattern, a flat/falling curve is the vulnerable pattern; the game-by-game timeline for 1701 shows both (e.g., set 2 game 8 fv=0.20 after the tiebreak-ward swing vs. set 5 games 4, 8, 10 all fv=0.5–1.0 holds). |

## Cross-check of expert-cited figures against the dataset

| Quantity | Expert value | Data value (interval) |
|---|---|---|
| Service-game hold rate | ~75–80% | 83.9% overall (846 held / 1008 games); by set 78–92% |
| First-serve point-win prob | server advantage large | 76.6% (n=2257) |
| Second-serve point-win prob | attackable | 55.3% (n=1310) |
| First-serve availability | ~60–65%, dips under fatigue | 61–65% in every half-hour bin of the 3h+ sample; no monotone fatigue dip (see `logs/expert_vals.log`) |
| Hold after facing 1 BP | — | 36.6% (n=172) |
| Hold from 0–40/AD (2+ BPs) | — | 47.7% (n=130) |
| Breaks per match vs. i.i.d. | cluster, but bounded | 186 observed, ≈190 i.i.d. expected (seed 42, 2000 sims) |

No value was copied from memory; all figures above were computed from the supplied dataset or come from the exchanges (which are cited in solution.json where used).
