# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction evidence — MM-Bench 2020_D (Huskies team dynamics)

Policy: structural anchoring before numerical filling; 10 fixed exchanges, one
short common-sense question each, each reply converted into a model element
before the next question. Questions live in `logs/operator_feedback/`; replies
in `expert_reply_N.json`.

## Exchange 1 — dominant mechanism (structural)
- Q: "When this kind of soccer team actually plays well together, what matters
  most: quick short passing, long balls into space, or something else?"
- A (gist): quick, short, high-tempo passing in the middle/attacking thirds that
  creates and exploits numerical or spatial advantage; long balls only as a
  targeted complement (runner in space, mismatch). Successful teams: high
  completion, short average pass, high tempo, dense connected network with a
  few hubs, forward progression rather than sideways recycling.
- Converted to work: this is the model's dominant mechanism. The passing
  network (pass_network.py) and the indicators (perf_indicators.py,
  event_model.py) are all built around pass tempo, pass length mix, network
  density/reciprocity/hubs and forward progression. Success-index weights
  reward tempo and penetration (forward line-breaking), not volume.

## Exchange 2 — primary constraint
- Q: "When a team pushes quick short passing, what is the biggest way it can
  backfire against a strong opponent?"
- A (gist): losing the ball in dangerous areas under coordinated pressing,
  especially near own goal, converting directly into high-quality counters.
  Secondary: sterile sideways recycling against a deep block, inflating
  possession without chances.
- Converted to work: defined the two failure modes the model must penalize.
  (a) Turnover-in-danger: built into the counter-exposure indicator
  (event_model.py, next exchange) and the low-third passing share. (b)
  Sterile recycling: recycling indicator (internal passes starting and ending
  in own third) enters the success index with negative weight.

## Exchange 3 — parameter for the constraint
- Q: "When a pressing opponent wins the ball near your own goal, how many
  seconds do you need to get back in position?"
- A (gist): no fixed number; roughly 5–10 s to restore compact shape; the
  most dangerous counterattack window is the first 3–5 s before the block
  re-forms.
- Converted to work: the 3–5 s window is the calibrated parameter of the
  counter-exposure indicator (event_model.py): a Huskies pass received by an
  opponent (ball-loss proxy) counts as exposed if the opponent's next event
  within 5 s is a shot or a forward pass. Interval of validity: short-to-
  mid-block re-formation under coordinated press, per the reply.

## Exchange 4 — discriminator: worked vs busy
- Q: "How would a coach tell the difference between a match where quick
  passing really worked and one where it just looked busy?"
- A (gist): outcome, not volume — ball progressing toward goal, line-breaking
  passes into the attacking third, sequences ending in shots; busy = high
  counts with sideways/backward circulation and few chances.
- Converted to work: penetration indicator (share of internal passes whose
  destination is the attacking third) and its ratio to recycling
  (pen_ratio = penetration/recycling*10) are the "worked vs busy" tells;
  penetration carries the second-largest positive weight in the success
  index.

## Exchange 5 — parameter: shot quality vs finishing
- Q: "When a team creates plenty of chances but rarely scores, what is the
  usual reason?"
- A (gist): finishing quality and shot quality, not creation — low-value
  chances (distance, tight angle) or poor conversion; also chance creation
  concentrated in one or two players.
- Converted to work: close-shot share (shots from final third, central
  channel 25–75), shot-taker HHI (creation concentration) and conversion
  (goals per shot) added to event_model.py. Data verdict: conversion
  correlates with goal differential (r=0.47), close-shot share is nearly
  constant (x is attacker-normalized, so nearly every shot registers in the
  final third) and correlates negatively with differential — the Huskies'
  problem is finishing/decision quality, not chance location.

## Exchange 6 — adjustment hierarchy (tactics first)
- Q: "On a bad run, what do successful teams usually change first: the player
  lineup, the tactics, or the training focus?"
- A (gist): tactics first (shape, roles, progression — fastest lever, no
  personnel turnover); targeted one/two-position lineup changes next (not
  wholesale, to protect cohesion and the passing network); training last
  (weeks, medium-term).
- Converted to work: shaped the advice section (task 3): levers are ordered
  tactics → targeted personnel → training. Central-vs-wide passing share
  (event_model.py) quantifies the tactical shape: wider passing correlates
  with goal differential (r=+0.17) — the data supports shifting progression
  to the wings/overloads as the first tactical lever.

## Exchange 7 — strategy by opponent strength
- Q: "When facing a strong opponent, what adjustment makes a weaker team most
  likely to avoid defeat?"
- A (gist): compact, defensive, deep block; concede possession deliberately;
  fewer risky short passes under pressure, more direct exits; attack only
  through quick purposeful transitions/set pieces; make the game low-scoring
  and win on a small number of chances.
- Converted to work: strategy model split by opponent strength
  (strength_proxy = opponent goals in that match, terciles). Data: vs strong
  opponents the Huskies only lost (8 losses, 0 wins); the low-scoring,
  low-risk game plan is exactly what the data shows is missing. The
  counter-exposure penalty in the success index is the quantified version of
  "avoid turnovers in your own half".

## Exchange 8 — generalization: what good teamwork looks like
- Q: "What is the clearest everyday sign that a group of colleagues is
  working well together as a team?"
- A (gist): work moves without explicit coordination — smooth handoffs,
  picking up unfinished work unasked, problems raised early, decisions at
  the level where the information sits; negative test: absence of a member
  does not stall the work.
- Converted to work: mapped to network terms in task 4: smooth handoffs =
  reciprocal dyads and 2-relay chains (relay rate: 211/match in wins vs
  151 in ties, 194 in losses); robustness = redundancy (top-2 players
  carry only ~29% of pass origins; ~14 players touch the ball per match);
  early problem-raising has no analogue in passing data — noted as a
  limitation for generalizing to non-sport teams.

## Exchange 9 — robustness mechanism
- Q: "If one key player is unavailable, how do good teams keep functioning
  well?"
- A (gist): the system, not the individual, carries the load — shared roles,
  understudies, simplified approach spreading creative burden, collective
  pattern training; teams built around one player's brilliance degrade
  sharply when that player is absent.
- Converted to work: hub-dependence indicators (event_model.py): hub_share
  (share of pass origins from the season's top playmaker M1) and
  rest_entropy (entropy of the remaining origin distribution). Data: M1's
  share is higher in wins (0.138) than ties (0.089) — moderate hub use is
  fine; M1-absent matches (n=5): -0.40 avg goal differential vs -0.36 with
  him, i.e. mild degradation, and rest_entropy correlates with differential
  (r=-0.13, more spread = marginally worse here, small sample).

## Exchange 10 — edge case / training priority
- Q: "When a coach has only a short pre-season, which habit is most worth
  training until it becomes automatic?"
- A (gist): collective defensive organization and the immediate reaction to
  losing the ball (press or drop, no thinking) — prevents the most costly
  goals, is trainable in a short pre-season via a shared trigger, independent
  of individual talent; second: 1–2 core passing-and-movement shapes.
- Converted to work: the top recommendation in task 3 is defensive
  transition training (press-or-drop after ball loss), directly targeting
  the counter-exposure risk (exposed-loss rate 2.5% in losses, 0% in wins
  and ties); the model's validity boundary (edge case) is defined as
  "normal tempo, coordinated block"; under extreme pressing the 3–5 s
  window may close before shape is restored (per exchange 3, then the
  objective is delay, not re-formation).

## Notes
- No request was made for coding, debugging, or computation help; all
  questions concerned real-world soccer/team practice.
- Expert sentences were paraphrased into parameters/indicators only; no
  reply text was copied into the submission.
