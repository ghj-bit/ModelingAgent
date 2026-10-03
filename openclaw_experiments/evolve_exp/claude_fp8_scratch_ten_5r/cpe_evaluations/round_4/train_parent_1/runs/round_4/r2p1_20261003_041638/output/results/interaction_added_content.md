# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — MM-Bench 2024_C (Tennis Momentum)

All 10 exchanges completed. Each reply is converted into a concrete model
input (parameter, constraint, feature, or decision rule) below. Expert
sentences are not copied into the submission; only the value/constraint travels.

**Question / Reply / How the reply changed the work**

---
**Exchange 1 — Duration of a "hot stretch."**
Q: *In a big tennis match, when a player "gets hot" and seems to own play, how long does that hot stretch usually last before it fades?*
Reply: hot stretch ≈ 1–2 games / ~8–15 points; runs of consecutive points rarely exceed 5–7; runs beyond 2–3 games uncommon.
**Used as:** momentum decay time-constant `TAU = 10` points (half-life ~7 pts, a few minutes of play) in the AR(1) momentum process (`momentum_model.py`, `swing_predict*.py`). Also sets the swing-prediction horizon `H = 5` points.

---
**Exchange 2 — Server conservatism under break pressure.**
Q: *When a serve is about to fail or break point arrives, does a player's confidence visibly change, and does that shift how they play?*
Reply: server tightens/conservatises (higher first-serve %, less pace) and win-rate on those points drops; returner goes free-swinging; effect small and player-dependent.
**Used as:** (a) break-point context in the point-win model — server hold on break point = 0.650 vs 0.753 on first serve (data) and a `BP_PRESSURE=0.05` downward nudge to server win-probability on break point; (b) the `bp` feature in the swing predictor.

---
**Exchange 3 — What triggers a genuine momentum flip.**
Q: *When momentum flips mid-match, what in-play event most reliably triggers it — a winner, a break, or a string of errors?*
Reply: a break of serve is the reliable flip trigger (resets structure); error clusters are a leading indicator culminating in a break; isolated winners are the least reliable.
**Used as:** (a) the larger momentum kick `K_BREAK = 0.35` (vs `K_POINT=0.10`) fires exactly on a break (game won by the non-server) in the momentum trace; (b) an `err_cluster` (trailing player's unforced errors over last 3 points) feature in the swing predictor; (c) the negative result that a pure "predict next break" target (T2) is *not* better than base — breaks confirm the flip, they do not precede it.

---
**Exchange 4 — What a coach weighs in a new opponent.**
Q: *When preparing a player for a new opponent, what about the opponent matters most to a coach's game plan?*
Reply: opponent's serve/return profile dominates (first-serve %, second-serve strength, return as weapon/liability); then movement/weak wing; then pressure behavior. Surface/form are secondary.
**Used as:** the cross-match comparison framework — each match's serve-context point-win rates and pressure behavior become the player "profile" used to argue generalizability, and the memo advice for coaches is organized around serve/return scouting.

---
**Exchange 5 — Early warning signs before a lead changes hands.**
Q: *Just before the lead in a set changes hands, what warning signs does a coach see coming first?*
Reply: order is (1) leader's service holds become uncomfortable (more deuces, more 2nd serves, more 30-30) → (2) opponent's return pressure builds → (3) conservative body language → (4) error cluster → (5) break. Structural indicators come before emotional ones.
**Used as:** the swing-prediction target is a *momentum direction change* (flow shifting to the other player), and the leading structural features — `abs_m` (magnitude of current momentum), `net_games`, `bp` — are exactly the "uncomfortable hold / return pressure" signals; the model learns that high `abs_m` predicts persistence, while erosion of `net_games`/serve context predicts an imminent flip.

---
**Exchange 6 — Pressure and error rates.**
Q: *In a tense set or fifth set, does the pressure of the situation make players hit more errors?*
Reply: yes but modest and concentrated in high-leverage points (break/set points, tiebreaks) and specific players; mechanism is a drop in first-serve % under pressure; errors often appear as unforced errors on routine balls.
**Used as:** the `set_no` leverage feature and the set-point context in the point-win model (server hold on set point = 0.6408, lower than 0.753 first-serve); justifies concentrating prediction effort on high-leverage points rather than assuming a uniform error inflation.

---
**Exchange 7 — Surface generality.**
Q: *Does a "momentum shift" work the same way on hard courts as on grass courts, in your experience?*
Reply: same mechanism, different magnitude/frequency: grass = faster, noisier, serve-driven; hard = more gradual/persistent; clay = most inertial.
**Used as:** a domain-of-validity statement for the model and the memo: the model is calibrated on grass (Wimbledon) and its `TAU=10` decay (short, abrupt swings) is grass-specific; on hard/clay the same AR(1) form applies but `TAU` should be enlarged (more persistent momentum). Recorded as a limitation, not a refit.

---
**Exchange 8 — Transfer to other sports.**
Q: *Does the "momentum" idea transfer well to other sports like table tennis, or is it mostly a tennis phenomenon?*
Reply: transfers well to table tennis and any point-based, serve/possession-structured sport (volleyball, badminton, squash); poorly to continuous-flow sports (soccer, hockey).
**Used as:** the generalizability conclusion — the model is a property of the point-scoring/serve-structure, not of tennis specifically; table tennis is the closest analogue. Stated in the memo and limitations.

---
**Exchange 9 — A coach's concrete response to losing the momentum.**
Q: *When a player feels the opponent "has the momentum," what concrete thing would you tell them to do on the next point?*
Reply: reset the point structure, not the score — serve/return to a safe high-percentage target (body/middle), take pace off, force the opponent to play one extra ball; end the run with a low-risk point, not an attempted winner.
**Used as:** the actionable coaching advice in the memo: when the momentum model shows a sustained opponent lead (large negative `m`), the recommended play is a high-`%` conservative first ball to stop the run of free points, consistent with the data that second serves / safe balls win ~52.8% (vs 75.3% first serve) — i.e., a controlled, lower-risk point breaks a run.

---
**Exchange 10 — Fatigue vs confidence in a long fifth set.**
Q: *In a long fifth set, does fatigue matter as much as confidence in deciding who holds the momentum?*
Reply: confidence is primary; fatigue is a secondary late-stage amplifier that erodes first-serve % and movement after ~3–4 hours, amplifying (not creating) an existing edge.
**Used as:** a limitation and a memo nuance — the point-level model captures the confidence/execution channel (the driver); a fatigue term is a candidate *modifier* for very long fifth sets (degrade `p_firstserve_server` late in the match) and is flagged as a future-model factor, not something the current dataset (which lacks a per-point physical load beyond distance) can quantify.

---

## Provenance note
Every empirical number reported in `solution.json` is either (a) computed from
the supplied `Wimbledon_featured_matches.csv` (see `data_clean.py` context table)
or (b) supplied by one of the 10 exchanges above (interval and exchange recorded
in the parameter table inside `mathematical_modeling_process`).
