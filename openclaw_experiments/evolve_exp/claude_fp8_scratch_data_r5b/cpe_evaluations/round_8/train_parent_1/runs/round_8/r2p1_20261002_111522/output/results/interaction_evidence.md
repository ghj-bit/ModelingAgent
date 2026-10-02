# Interaction evidence — MM-Bench 2024_C (Wimbledon momentum)

Three expert exchanges, one question each, sequenced as: structural
assumption → causal mechanism → interpretation threshold. Each reply was
turned into a concrete parameter, constraint, or test before the next
exchange.

## Exchange 1 — structural assumption (independence vs persistence)

**Question** (`logs/operator_feedback/expert_question_1.md`): whether runs of
consecutive points in a big match are caused by the opponent getting worse
rather than luck, and whether a good game carries into the next.

**Reply** (`expert_reply_1.json`): runs are largely luck — point outcomes are
close to independent given serve-conditional probabilities (~0.6–0.65 on
serve); opponent degradation is real but second-order; games do not start
fresh, but carryover is weak relative to the serve rotation; score pressure
(break/set points) matters more than "momentum" from the previous game.

**How the reply became work:**
1. It fixed the null model for the randomness test: the coach's claim must be
   tested against "independent points with server win probability P", not
   against 50/50. `code/runs_test.py` implements exactly that null (real
   serve pattern kept, outcomes resampled at P, N_SIM = 2000 per match).
2. It set the value of the calibrated parameter **P = 0.673** (own-serve
   point-win probability, pooled over all 31 matches) and its role: the
   serve-adjusted surprise a_t = ±log(P/(1−P)) is only defined relative to
   this baseline, and the expert's 0.6–0.65 range brackets the estimate.
3. It determined which "swings" count: the expert says a genuine stretch
   persists over games, so a one-point blip is not a swing. `swing_label`
   in `code/predictor2.py` requires the new leader to hold for H = 10
   points after the flip.

## Exchange 2 — causal mechanism (what drives a genuine stretch)

**Question** (`expert_question_2.md`): given that the streak itself is
mostly chance, what does the stronger player actually do or stop doing
during a genuine strong stretch?

**Reply** (`expert_reply_2.json`): serve-hold mechanics and error discipline —
the server keeps holding (serve rotation favors him), fewer unforced errors
especially on return games, first-serve percentage holds up under pressure,
and conversion of break points / clutch execution at high-leverage points.
The underlying point-win rate barely moves; there is no self-reinforcing
"momentum force".

**How the reply became work:**
1. It defined the mechanism test in `code/mechanism_test.py`: during "hot"
   states (|M| > 0.15) vs "cold" states (|M| < 0.05), compare the hot
   player's error rate over the next 5 points and his next-point win rate.
   Prediction from the reply: hot player errors **less** during hot
   stretches.
2. **Result (the reply, verified on the data):** hot error rate
   0.611/5 pts vs cold 0.706/5 pts — a −0.094 point reduction in the hot
   player's error rate during hot states, pooled over all 31 matches. The
   error-discipline mechanism is present and directionally correct, but
   small — consistent with the expert's "real but small".
3. It set the operating constraint for the predictor: since the mechanism
   lives in serve quality and error control (both slow variables on the
   scale of games, not points), the model's useful information must come
   from game-scale features (serve, game score, set context), not from the
   raw recent point streak. The final feature set in `predictor2.py`
   reflects this: `srv_next`, `lead`, `deuce`, `set` dominate the weight
   profile, and the raw streak terms (a1, a2, a5) have near-zero weights
   (a5 = 0.006).

## Exchange 3 — interpretation threshold (when is the tool trustworthy)

**Question** (`expert_question_3.md`): what would a coach need to see in the
readout to trust it live, and what would make them stop using it?

**Reply** (`expert_reply_3.json`): four acceptance criteria — (1) a hit rate
clearly above the base rate of swings, not above 50%; (2) calibration:
stated confidence must match realized frequency; (3) lead time long enough
to act (a game or more ahead of the flip); (4) consistency across matches,
not just the training match. Kill criteria: if the only signal is
"who's serving and the game score" (already-known tennis), or if warnings
fire at base rate, or if confidence doesn't match outcomes.

**How the reply became work:** `code/calibration.py` implements the four
criteria literally as pass/fail tests on the trained predictor's out-of-sample
probabilities:

| Criterion | Requirement (from reply) | Measured | Pass |
|---|---|---|---|
| 1. Hit rate | precision > 1.2 × base rate | precision 0.059 vs base 0.052, lift 1.12 | **fail** |
| 2. Calibration | stated vs realized within 0.10 | 0.064 stated vs 0.059 realized | pass |
| 3. Lead time | ≥ H/2 = 5 points before flip | 1.5 points | **fail** |
| 4. Consistency | pooled AUC > 0.55 | 0.502 | **fail** |

The honest verdict: the predictor is **calibrated but not actionable** — it
neither beats the base rate nor gives enough lead time, and its only signal
is serve/score context (matching the expert's kill criterion). The momentum
score itself, by contrast, does track who is playing better (leader matches
the set victor at set end in 99.1% of 117 sets), so it is retained for
describing match flow, while the swing-prediction claim is rejected. This
verdict is reported as the model's limitation and the basis of the memo's
advice.
