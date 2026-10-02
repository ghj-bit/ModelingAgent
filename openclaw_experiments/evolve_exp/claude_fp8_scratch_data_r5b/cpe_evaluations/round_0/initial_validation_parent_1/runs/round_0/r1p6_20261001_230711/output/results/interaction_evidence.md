# Interaction Evidence — MM-Bench 2020_D (Huskies passing network)

Policy: exactly 3 expert exchanges. Each reply was converted into a concrete
model constraint or test before the next exchange.

## Exchange 1

**Question** (logs/operator_feedback/expert_question_1.md):
"When a team plays a much stronger opponent, does it typically keep passing
patiently and keep its usual shape, or does it drop deeper and defend with
fewer players up front? What do you have seen in practice?"

**Reply** (logs/operator_feedback/expert_reply_1.json): a clearly weaker team
almost never keeps its usual shape; it drops deeper, compresses the space
between lines, commits fewer players forward, and relies on counters and
long clearances rather than patient build-up. Two qualifications: (a) it is a
tendency, not a rule — some teams/coaches keep possession as identity; (b) the
shift is conditional on game state (scoreline, phase) and interacts with
opponent strength and coaching style rather than acting alone.

**Conversion to work** (constraint C1, source: exchange 1, interval: any
match where the opponent has scored ahead of the Huskies, late in the phase,
or where the opponent is empirically stronger):

1. The passing-network analysis is stratified by matchup quality: opponents
   are binned by season points and goals difference, and all network
   indicators are compared strong-vs-weak opponents to test whether the
   Huskies' passing behaviour shifts with opponent strength (as the reply
   predicts it should for the weaker side in any fixture).
2. Shape/tempo indicators are also stratified by in-match game state: the
   first-half network is compared with the second-half network in matches
   where the score changed, so "deeper, compressed, fewer players forward"
   becomes the testable prediction of a lower average pass length, a lower
   mean attack-third share of passes, and reduced forward-node betweenness.
3. Because it is a tendency, not a rule, the model reports indicator
   *differences* and their variability (standard deviations), not binary
   style labels.

Work done before exchange 2: data cleaning (see below) and the full indicator
battery described by constraint C1 were implemented and run.

Data cleaning applied (results/profile.json): dropped 147 self-pass rows
(artifact); clipped coordinates to [0,100] (no out-of-range values found);
clamped 0 negative EventTime values; lower-cased Outcome; removed exact
duplicate rows (none present). 38 matches, 23,282 passes, 59,271 full events
survive; 30 Huskies player nodes.

## Exchange 2

**Question** (expert_question_2.md): "When judging whether teammates really
play well together, what do you look for on the field beyond the scoreboard?
What would make you say two players are well in sync?"

**Reply** (expert_reply_2.json): anticipation rather than reaction. Evidence
of sync: (a) finding each other in tight/advanced areas, not just safe
sideways balls — volume alone is weak evidence; (b) reciprocity and balance —
one-way feeding shows dependence, not sync; (c) off-ball coordination;
(d) positional interchange/cover; (e) progression — combinations must break
lines, not circulate. Sync = frequent + reciprocal + forward-progressing +
holds up against strong opponents and under pressure.

**Conversion to work** (constraint C2, source: exchange 2, interval: any dyad
of Huskies players, season and per match):

1. Dyad "sync" indicator implemented as a composite of four measured
   components per ordered dyad (i,j): total weighted volume V_ij (frequent);
   reciprocity R_ij = 2·A_ij·A_ji/(A_ij+A_ji)^2 ∈ [0,1] (balance, one-way
   dependence penalised); forward share P_ij = share of the dyad's passes with
   positive x-progress (progression); final-third share T_ij = share of the
   dyad's passes whose destination lies in the opponent's final third
   (activity in dangerous/contested areas). sync_ij = (V_ij/V_max)^0.25 ·
   (0.30·R + 0.35·P + 0.35·T). The 0.25 exponent keeps volume from
   dominating, matching "volume alone is weak evidence".
2. Because off-ball runs and zone interchange are not in the data, C2's
   items (c) and (d) are declared out of scope and listed as a model
   limitation, not silently dropped.
3. "Holds up under pressure" test: top-sync dyads were required to be
   re-ranked on the subset of passes made in the opponent final third and in
   2H-while-trailing situations; M1–F2 and D5–F2 stay in the top five in both
   subsets (results/model_results.json: top_sync_dyads), supporting the
   composite over raw volume, which would rank M1–M3 (a mid-field
   circulation pair, T = 0.074) higher.

Work done before exchange 3: full indicator battery (season, 38-match, 10-min
window, tier- and game-state-stratified) implemented and run (see
logs/network_model.log).

## Exchange 3

**Question** (expert_question_3.md), built on the computed result that the
team's shape barely changes across opponent tiers (att3 share 0.255–0.310)
and that trailing-2H play still attacks (att3 share 0.318): "Your data shows
the team plays almost the same shape against weak and strong opponents, and
trails yet keeps attacking late. What would you change in their play to turn
more draws and narrow losses into wins?"

**Reply** (expert_reply_3.json): the core issue is that the team does not
adapt its risk profile to game state or opponent. Three changes: (1) increase
risk when level or trailing late — push an extra player forward, accept a
more open back line, trade safety for chance creation in the final
20–30 minutes; (2) vary the approach by opponent — vs weak teams commit more
numbers forward and press high to force turnovers in their half; vs strong
teams keep the compact block but make counters faster and more direct; (3)
convert territorial control into shots — too many safe sideways/backward
passes and too few line-breaking final-third entries; reward progressive
passes and runs in behind rather than recycling. Unifying rule: shape and
tempo must be conditional on scoreline and opponent, not fixed.

**Conversion to work** (constraint C3, source: exchange 3, interval: any
match state; operationalized as the decision rule of the advisory model in
subtask 3):

1. The advisory model becomes a conditional policy on two discrete inputs
   (opponent tier ∈ {weak, mid, strong}, score state ∈ {leading, level,
   trailing}), each cell prescribing a target range for the measurable
   indicators that proxy the reply's three levers: final-third pass share,
   forward-pass share, and shot volume per 10-minute window (results/
   model_results.json: by_opponent_tier and game_state give the observed
   baselines the targets are set against).
2. The three levers are tested against the data: vs weak opponents the
   observed forward-pass share (0.561) and final-third share (0.255) are the
   lowest of the three tiers, i.e. the team already plays *cautiously* vs
   weak sides — the data contradicts a "dominating but not converting"
   story for weak opponents, and the advice is therefore to raise risk and
   final-third entries there, quantified as +0.04 final-third share and +1
   shot per 10 min vs the observed weak-tier baseline.
3. The reply's "risk when trailing late" lever is the one the data most
   supports changing: 2H-trailing final-third share is already 0.318 (highest
   of any state) yet the team wins only 3 of 10 ties and 0 of 14 strong-tier
   matches, so the prescribed change is tempo/risk (shorter pass interval
   toward the observed 9.67 s average, more line-breaking passes) rather
   than more territory.
4. Universality check (subtask 4): the conditional-policy structure is the
   generalization proposed for team design; the reply's "not a rule"
   qualifier from exchange 1 is retained as the model's bias note — the
   policy is a tendency-level recommendation, and per-coach style (Coach1/2/3
   spans the 38 matches) is a known uncontrolled factor.
