# Interaction Evidence — Problem 2020_D (Huskies team-dynamics network)

Three expert exchanges were run, in order, each question written before the
work it governs, each later question building on the previous reply.

## Exchange 1 — Data provenance and completeness

**Question** (`logs/operator_feedback/expert_question_1.md`): which of three
data imperfections most affects what the passing network can say about who
plays together well — (a) missing intercepted/out-of-bounds passes, (b)
position-slot labels that blur individual players across games, or (c)
rounded coordinates — and whether a same-slot appearance in two different
games should be read as the same person.

**Reply (summary of `expert_reply_1.json`)**: the position-slot labels are by
far the biggest problem. Missing failed passes are a real but modest
distortion (roughly a tenth to a fifth of attempts, concentrated in risky
forward/long passes, so the network slightly overstates safe backward
connectivity but preserves relative who-passes-to-whom structure). Rounded
coordinates are negligible (about 1 m on a 100-unit field). A slot such as
"M2" is a *role*, not a person; over 38 games the same slot is routinely
filled by different individuals, so treating same-slot appearances across
games as one player conflates distinct people. Treat same-slot appearances in
different games as different people unless continuity is verified; use
slot-level networks for role/formation structure, not for individual
partnership claims.

**How the reply became work** (before Exchange 2):
- Parameter/constraint adopted: *identity granularity = (match, slot)*, not
  season-slot. Every match-level network, degree/reciprocity/triad
  computation in `code/clean_and_network.py` and `code/role_network_summary.py`
  is built per match so that a slot appearing in two games is two nodes, not
  one. The season-level slot network (60+ nodes) is used only for role-level
  structure and is explicitly labelled as such, never for individual
  partnership claims.
- Data-handling rule adopted: failed passes (interceptions, out of bounds)
  are treated as a known ~10–20% missing block, non-random, concentrated in
  long/forward passes. This is stated as a bias in the model's limitations
  rather than corrected, because no receiver record exists to reconstruct
  them; it bounds how much "connectivity" numbers can overstate safe
  backward structure.
- Rounded coordinates accepted as negligible (~1 m); no correction applied.

## Exchange 2 — Key structural assumption

**Question** (`expert_question_2.md`), built on Exchange 1: first-cut
numbers showed wins and losses have nearly identical network *shape*
(reciprocity 0.43 vs 0.42, mean out-degree ~7 in all three outcome groups).
Is the difference in outcomes driven by the web of who-connects-to-whom
(slow, structural) or by where the ball is played and how much risk is taken
(fast, tactical) — and which of the two levers can a coach actually pull week
to week?

**Reply (summary of `expert_reply_2.json`)**: the second lever — where the
action happens and how much risk the team takes — is what usually decides
individual matches and is the one a coach pulls week to week. The web is
comparatively stable over a season (which is why win/loss shapes look
identical); it reflects formation and roles and changes slowly. Treat network
shape as a slowly-varying structural backdrop; treat field position, pass
risk, and opponent-specific adaptation as the match-to-match levers.

**How the reply became work** (before Exchange 3): this fixed the two-layer
model structure that `code/model_match_outcome.py` then estimated. Features
were split into a structural block (pass volume, mean out-degree,
reciprocity) and a positional/risk block (mean origin/destination x, share of
passes landing in opponent and final third, mean and p90 pass distance, share
of long passes >25 units, share of Launch/High/Cross subtypes). Three
logistic regressions were fit to the win-vs-(tie|loss) label — all features,
positional/risk only, structural only — plus a one-vs-rest three-class
model, to test whether the fast levers (as the expert predicted) carry the
match-to-match signal.

## Exchange 3 — Interpretation context / decision threshold

**Question** (`expert_question_3.md`), built on Exchanges 1–2: with 38 games
and 11 features per game, some individual numbers may be noise. Before
acting on "teams that pass more and keep their rhythm tend to win; pushing
passes higher helps a little," what single thing should the data team
confirm, and at what point does a single-season pattern become something to
only *watch* rather than act on?

**Reply (summary of `expert_reply_3.json`)**: the decisive check is that the
pattern is not just "good teams pass more because they are winning" — i.e.
that passing volume/rhythm is a cause, not a consequence, of game state (a
team ahead late protects the lead by keeping the ball). Concretely, show the
pattern holds when the game is still level — e.g. first-half or
pre-first-goal passing predicting the outcome. General threshold: a
single-season number is something to *watch*, not act on, until it (a)
survives that game-state control and (b) repeats across a second season or
against held-out games.

**How the reply became work** (final analysis pass):
`code/robustness_checks.py` implemented the demanded checks:
- **R1 (game-state control)**: refit the model on first-half passes only.
  Result: first-half accuracy 0.763 vs full-match 0.632, with the
  pass-volume coefficient *larger* in the first half (1.408 vs 0.674).
  The signal is not purely a score-state artifact — if anything it is
  stronger before scores separate.
- **R2 (per-opponent sign consistency)**: for the 7 opponents played twice
  with both a win and a non-win, the win-minus-nonwin delta in
  final-third-pass share is positive in 6/7 cases — the most consistent
  lever in the dataset.
- **R3 (leave-one-out)**: pass-volume and final-third-pass coefficients keep
  their sign in 38/38 refits; reciprocity flips in 3/38 (weaker).
- **R4 (bootstrap, n=200)**: coefficient signs for volume/final-third are
  stable in ~85–89% of resamples; bootstrap accuracy mean 0.704 (sd 0.083).

These results set the decision threshold used in the submission: the
pass-volume and final-third-pass levers are *actionable* (they survive the
game-state control and held-out refits); the reciprocy/web-shape levers are
reported as *watch, don't act* — consistent with the expert's threshold.
