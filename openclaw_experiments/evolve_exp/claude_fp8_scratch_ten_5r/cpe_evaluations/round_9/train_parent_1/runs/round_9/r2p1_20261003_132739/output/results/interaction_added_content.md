# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — Task 2024_C (Tennis Momentum, Wimbledon 2023 Final)

Ten exchanges, one question each, each answer converted into a model element
before the next exchange. Full question/reply texts in
`logs/operator_feedback/expert_question_N.md` / `expert_reply_N.json`.

| N | Question (topic) | Key content of reply | How it changed the work |
|---|---|---|---|
| 1 | What changes on court when a swing happens? | Runs = clusters of serves/holds; driven by first-serve %, unforced-error rise, court-position control, not a force | Fixed the model shape: momentum must be an observable, point-level function of serve state and shot quality, not an unobserved latent. Broke-point weighting (w=2) added to the EMA because break clusters dominate runs. |
| 2 | What reliably ends a run? | The trailing player's hold of serve; a run extends only via a break | Runs are bounded by game structure. Momentum computed on a per-game-bounded basis; swing events defined at game level (consecutive games), not arbitrary point windows. |
| 3 | How long do genuine runs last? | 2–3 games (one break + surrounding holds); 4+ is a strong, uncommon signal | Set the event scale: swing = ≥2 consecutive games (primary), 3+ (secondary); 4+ flagged as collapse/mismatch signal in interpretation. |
| 4 | What is seen first before a run starts? | Order: serve/return quality → neutral-rally control → opponent UFE rate; scoreboard last | Feature set for the swing predictor: (1) server first-serve success in trailing window, (2) net rally control (winners − opponent UFE), (3) opponent UFE rate, (4) recent point form. Predict at game boundaries, labeled by run start. |
| 5 | When is a swing unpredictable? | Tight serve-dominated states (both holding, few break points) and close late tiebreaks — no mechanism to detect; also late close sets | Domain-of-validity statement for the predictor; tested a break-point-window "mechanism-present" gate: gating HURT (AUC 0.716 → 0.539), so the gate was dropped as unsupported and reported honestly as a limitation. |
| 6 | What does a coach actually use from scouting the opponent? | Prioritized game plan: serve/return targeting, rally patterns, pressure points (where weakness shows: 2nd serves, break points, late sets); 2–3 executable cues; NOT used to predict swings | Built per-match pressure profile (2nd-serve win rate, hold/convert rates on break points, late-match win rate) for both finalists; drives the pre-match advice section. |
| 7 | What to do at the changeover when losing a run? | (1) Reset the serve with 1–2 technical cues, (2) shrink goal to the next hold only; no momentum talk, no lectures | Changeover advice in memo; consistent with model: the flow variable is serve-condition based, so a serve reset is the lever. |
| 8 | Do champions differ in run handling? | Narrow gap: they stop bleeding on their own serve and shorten memory; much of it is just better serving under pressure | Ran the hold-after-run test (code/run_stopping.py). Data REFINED the claim: after a 2-game run only 19% hold (winner 20/64, loser 11/98); after a 3-game run 3–8%. Runs compound more often than reset — reported as a limitation of the "champion resets" narrative and a bias in the model. |
| 9 | Realistic goal when down a break? | Hold, then hunt ONE break back early; do not chase the set | Ran the break-recovery test (code/recovery.py): across all 896 breaks, 13% hold the next service game but 92% regain a break within 4 games (final: 97%). Parity is the normal state; runs are transient. Informs the advice and the interpretation of flow swings. |
| 10 | What to tell a player who blows set 1 6–1? | Least informative set; reset to next service game; keep the game plan; sets restart at 0–0; caveat: untouchable-serve mismatch is a real exception | Framing of the final in the report (set 1 was serve-dominance, not a plan collapse; Alcaraz won 3 straight); the mismatch caveat is recorded as a model boundary condition. |

## Values taken from exchanges (used as calibrated constraints, not as fitted numbers)
- Run scale: 2–3 games typical; 4+ = strong signal (exchange 3) → event thresholds.
- Importance weights: break-point moments weighted 2× in the momentum EMA (exchange 1).
- Mechanism ordering for features (exchange 4) → feature construction order.
- Abstain condition for the predictor in serve-dominated close states (exchange 5) → tested, not supported, reported as limitation.
- Advice content: serve reset + one-hold target at changeover (exchange 7); hold-then-one-break when down a break (exchange 9); no wholesale plan change after a dropped set (exchange 10).

## Data-driven findings that refined or contradicted the expert narrative
1. Randomness test (code/random_test.py): point-level runs in the final are fully
   consistent with the permutation baseline (max 7 consecutive points; p=0.93
   against 1000-bootstrapped permuted signs; max own-serve streak 9, p=0.44).
   At the point level the coach's "it's random" claim survives; momentum, if
   present, lives at the game/set level, matching exchange 2 (runs are hold/break
   clusters, not point streaks).
2. Run stopping (code/run_stopping.py): after a 2-game run, 31/162 (19%) of the
   broken player's next service games were held; after a 3-game run 6/67 (9%).
   Contradicts the simple "champions hold and reset" story (exchange 8) — runs
   tend to extend.
3. Break recovery (code/recovery.py): 92% of break-conceders regain a break
   within 4 games — the match stays at parity; swings are short-lived at the
   game level.
4. Serve advantage from data: server wins 67.3% of points overall; 75.5% after
   first serve vs 53.0% after second serve (the serve_no interaction the problem
   flags as must-be-handled).
