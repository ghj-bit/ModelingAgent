# Expert Interaction Evidence

Ten exchanges, one question each (files `logs/operator_feedback/expert_question_N.md`,
replies in `expert_reply_N.json`). Each reply is converted into a model element below.

| # | Question (short) | Expert answer (gist) | How the reply became work |
|---|---|---|---|
| 1 | How long does a hot-streak carry-over last? | A few points, ~2–4, occasionally to end of current game; serve advantage and changeovers reset it | Set EWMA half-life of the momentum indicator to 3 points (λ=0.5^(1/3)); sensitivity run over half-life 2–10 (`momentum_model.py --sweep`), chosen by lead-change count and final-lead agreement |
| 2 | Which single event most shifts form? | Being broken is #1; barely-won long rallies second; aces largely neutral | Event amplification in the momentum input: a break won contributes +1.5× the residual, a break conceded −1.5×; points won on ≥10-shot rallies get +1.2× (weights in `momentum_model.momentum_series`) |
| 3 | Does a lost break point cause defensive play for several points? | No — 1–2 points at most; the *converter* of a break point carries the lift longer | Asymmetric treatment: the break event itself (game_victor on opponent serve) is the state change; the point lost is damped, not amplified. Reflected in the amplification rule of #2 and in the swing model's reliance on the break as the flow-reset event |
| 4 | Does the converter's edge last beyond the next game? | About one game, then it washes out | Justifies a short (3-point) memory and the use of *recent* (last-3/5-point) features only in the swing predictor; no long-horizon form state carried |
| 5 | What signs precede a flow flip? | Break points appearing for the first time, first-serve percentage dropping (more 2nd serves), long rallies starting to go the other way, more unforced errors; 1–2 games ahead | Feature set of the swing-prediction model: `bp_now`, 2nd-serve exposure (`srv_s2_last3`, `srv_s2_weak`), receiver's unforced-error trend (`rec_ue`), receiver momentum `m` (captures the rally-direction shift) |
| 6 | Are 3–4 point runs mostly skill or luck? | Mostly luck; server wins ~65–75% of own service points, so short runs are expected by chance | Null model for the coach test: per-point Bernoulli with serve-number-specific probabilities (0.75/0.53 server-side, 0.25/0.47 receiver-side), calibrated from the dataset; runs compared against that null rather than a uniform coin |
| 7 | How does fatigue show up: errors or serve? | Serve degrades first (1st-serve % down, speed down a few mph, tentative 2nd serves), unforced errors follow later | Fatigue indicator = 2nd-serve share and serve-speed trend; serve speed by set computed across ≥4-set matches (120.3 → 118.9 mph, mild decline); unforced-error trend used as a secondary, noisier feature |
| 8 | What to scout in an unfamiliar opponent? | Hold and break rates, 1st-serve % and 2nd-serve vulnerability, break-point conversion/save, response after being broken, serve speed and rally length | Scouting profile table computed for all 31 matches (hold rate, break rate, BP conversion); break-back rate within 2 games = 76.7% (n=790) used in the pre-match advice |
| 9 | Does the swing advice transfer to table tennis? | Logic transfers, signals do not — no serve-hold structure; watch service-reception points, runs near the 11-point game boundary, error rate | Generalizability discussion in the solution: the serve-adjusted residual + EWMA construction requires a serve-hold structure; the transferable core is "structural scoring event + serve-quality degradation," not the specific features |
| 10 | Are swings more frequent in the final set? | Yes — serve degradation erodes the server's advantage and score leverage raises variance; magnitude may be smaller | Verification computed: momentum zero-crossings in set 5 (e.g., 18 in the final) vs. fewer in earlier sets; the model's leverage feature includes set score + game gap |

No reply was copied into the submission; only the numeric/constraint content above
(half-life ≈ 3, event ordering, ~65–75% serve-win, scout metrics, table-tennis
caveat) is used, and each appears in `solution.json` in its own formulation with
this file as the recorded source.
