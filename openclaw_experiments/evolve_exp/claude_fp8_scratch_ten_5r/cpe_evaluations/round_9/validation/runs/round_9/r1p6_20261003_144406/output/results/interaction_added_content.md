# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — Problem 2020_D (Huskies passing network)

Policy: mechanism → constraint → parameter sequencing, 10 exchanges, one question
each. Questions asked in plain language; every reply converted into a model input
before the next exchange. No advisory ("what should we do") questions were asked.

## Exchange 1 — mechanism (dominant driver of passing success)
- **Q:** "In soccer, what makes a team pass successfully together on the field, more than individual skill alone?"
- **A (gist):** success is a relational/structural property — off-ball movement that creates
  passing options, positional spacing (width/depth/lanes), timing, shared tactical
  understanding, and decision speed under pressure; passing success drops under press
  and in congested areas.
- **Used as:** the structural branch that shapes the whole model. The network is treated
  as the object of analysis (edges = viable passing options), not player skill.
  Concrete model targets derived: (i) mutual-dyad fraction as "pre-arranged option"
  indicator; (ii) node clustering as local option density; (iii) the "options under
  press" constraint handled in exchange 2. Recorded in `mathematical_modeling_process`
  of tasks 1 and 4 (criterion G1 rationale).

## Exchange 2 — constraint (what limits the mechanism)
- **Q:** "What most limits a team's passing options when opponents press, and how do coaches usually counter it?"
- **A (gist):** the press closes time and space around the carrier and screens the
  nearest lanes; counters are a third man for numerical superiority, building out from
  goalkeeper/defenders, switching play/width, long outlets/target forwards, rotation.
- **Used as:** the limiting constraint on the passing mechanism: a pressed carrier
  loses the nearest options first, so the network must contain redundant short routes
  (third-man outlets) and at least one long outlet. Concrete model uses: (i) the
  hub-overload criterion G5 (a 3.6x-mean hub is pressable — single nearest-option
  failure); (ii) the D3/G1 third-man-outlet recommendation in task 3 change (1);
  (iii) the long-pass share (39.0% season, 37.9% in 2H) read as the "bypass the press"
  channel in the per-half and game-state statistics.

## Exchange 3 — parameter (recovery clock after losing the ball)
- **Q:** "How quickly does a team usually regain passing control after losing the ball in open play?"
- **A (gist):** most recoveries happen in a 5–15 s counter-press window; a large share
  within ~5 s, most within 10–15 s; otherwise reorganization takes much longer.
- **Used as:** calibration of the dynamic model's recovery clock and the turnover gap
  threshold. Model inputs: T_rec = 15 s (interval [5,30]) as the counter-press window;
  turnover gap = 20 s (interval [10,30]) for splitting possession spans; recovery rate
  nu ≈ 1.1 /s (interval [0.5,2]) from the measured median 0.9 s. Validation against
  data: 81.5% of 8,151 measured loss events show a Huskies ball event within 5 s and
  90.3% within 15 s — the team operates at the fast edge of the expert norm. These
  rows appear in the task 2 parameter table.

## Exchange 4 — parameter (directional pass mix)
- **Q:** "In a typical match, what fraction of passes are forward passes moving the ball toward the opponent's goal?"
- **A (gist):** roughly 40–50% forward; backward+lateral the slight majority; varies
  with style and game state.
- **Used as:** (i) sanity band for the measured directional shares (forward 41.6%,
  backward 26.1%, lateral 32.3% — inside the expert band, confirming the +/-5-unit
  forward threshold is not misclassifying); (ii) the baseline against which
  game-state responses are judged (task 2 I_adapt): behind 41.7% vs level/ahead
  41.9% = no shift, contrasted with the expected directness increase from exchange 6.

## Exchange 5 — parameter (build-up spacing)
- **Q:** "How far apart do teammates usually stay from each other when building up an attack?"
- **A (gist):** nearest supporting options about 8–15 m; lines separated 15–25 m
  vertically; team length 30–40 m settled, 50+ m attacking; too close = one defender
  covers two, too far = risky passes.
- **Used as:** the physical spacing constraint on the pass-length distribution. The
  field is normalized to 100 units; the measured mean pass length 24.0 units (~72 m)
  and long-pass share 39% are consistent with 10–20 m nearest-support spacing only if
  ~a third of passes are the long "bypass the press" channel — used as a consistency
  check in task 1 and as a calibration bound (interval [8,25] m) in the task 2
  parameter table.

## Exchange 6 — parameter (game-state tempo shift)
- **Q:** "Do teams usually play more patiently or more quickly when losing a game late on?"
- **A (gist):** the trailing side speeds up and plays more directly (faster
  circulation, more long balls/crosses, players pushed forward, more risk); the
  leading side slows down.
- **Used as:** the expected-sign prior for the adaptability indicator. The measured
  I_adapt ≈ 0 (forward share 0.417 behind vs 0.419 level/ahead; pass length 24.23 vs
  23.76) shows the Huskies do NOT make the norm shift — this gap is the basis of
  task 3 change (3): install a behind-state response targeting long-pass share up
  toward ~50% from the 2H baseline 37.9% in the last 20 minutes while trailing, with
  success measured next season as I_adapt > 0.05.

## Exchange 7 — parameter (position-level pass volume)
- **Q:** "Which player position typically makes the most passes in a team, and roughly what share of total passes is that?"
- **A (gist):** midfielders are the main distribution hubs; midfield ≈ 40–50% of team
  passes; forwards the fewest.
- **Used as:** benchmark for the measured position shares (D 42.6%, M 37.0%, F 15.9%,
  G 4.5%). The combined D+M share of 79.6% confirms the build-out-from-the-back style;
  the top hub being M1 (1248 passes, betweenness rank 1) matches "central midfielder
  as main hub". Used in task 1 (meso/formation interpretation) and task 3 (hub
  rotation M1 → M3/D3).

## Exchange 8 — parameter (post-goal style change)
- **Q:** "When a team scores, does its passing style usually change noticeably in the following minutes?"
- **A (gist):** only modestly and briefly; the scorer drops slightly deeper and
  recycles; the conceding side increases tempo and directness for the next
  ~5–15 minutes; the change is in intent, not shape.
- **Used as:** bounds for any goal-conditional window: effects are short (5–15 min)
  and belong mainly to the conceding side. This justifies not building a
  goal-event-triggered model for the Huskies' own style (their own response is small
  by the norm) and frames the 15-min windows in task 1 as the appropriate temporal
  resolution. Recorded in the task 2 parameter table.

## Exchange 9 — mechanism (position stability)
- **Q:** "How long do soccer players usually keep the same position before swapping during a match?"
- **A (gist):** nominal position is set by the starting formation and holds for the
  whole match; only substitutions, red cards or tactical shifts reassign roles;
  in-phase drift (overlap, drop) is transient, not a swap.
- **Used as:** licenses the core data assumption that the 30 Huskies player IDs are
  stable nodes within a match (substitution re-numbers the same nominal slot), so
  per-match and season networks are well-defined on the same node set. Recorded in
  task 1 assumptions (iii) and the task 4 limitation "membership fixed per match".

## Exchange 10 — mechanism (post-goal reorganization speed)
- **Q:** "After a goal, do teams usually reorganize quickly or play loosely for a while?"
- **A (gist):** reorganization is quick — within roughly a minute of restart both
  teams are back in shape; what changes is aggression/risk for several minutes, not
  structure; loose play is brief and atypical.
- **Used as:** confirms the network-structure assumption is robust across goal
  restarts (shape persists, only rates change), so the per-match structure indicators
  (density, clustering, triad fractions) are not contaminated by post-goal chaos.
  Recorded in task 2 analysis (why structure stays near-constant across outcomes:
  the team keeps its shape, and G4 in task 4 follows).

## Conversion audit
Every exchange produced a model input: E1 → structural framing (tasks 1/4);
E2 → press constraint & G5, task 3 change 1; E3 → recovery clock nu, T_rec,
20 s turnover gap (task 2 parameter table); E4 → directional threshold validation
& I_adapt baseline; E5 → spacing bound [8,25] m; E6 → expected sign for I_adapt,
task 3 change 3; E7 → position-share benchmark, hub identity; E8 → 5–15 min
goal-condition window bound; E9 → stable-node assumption; E10 → shape-persistence
justification for per-match structure metrics. No exchange was dropped; no
reply text was copied verbatim into solution.json (values, constraints, and
criteria only, in the model's own formulation).
