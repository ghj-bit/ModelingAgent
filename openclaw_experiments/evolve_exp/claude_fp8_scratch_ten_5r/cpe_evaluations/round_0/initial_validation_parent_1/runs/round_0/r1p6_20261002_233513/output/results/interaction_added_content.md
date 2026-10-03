# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — Task 2020_D (MM-Bench, ICM Network Problem)

Ten exchanges, one question each, in order. Each row: the question (summarized),
the value/constraint the reply supplied, and the concrete change it forced in
the model or analysis. All expert-supplied values used in solution.json are
listed here as their source.

## Exchange 1
- **Question:** When a team is clearly outperforming its opponent, how do
  coaches usually respond to protect a late lead?
- **Reply (condensed):** Defensive substitutions, lower block, low-risk
  possession-and-clearance style: fewer forward passes, more sideways/backward
  passes, longer clearances, time-wasting. An empirical regularity, not a rule;
  degree varies with scoreline and time.
- **Used in the work:**
  - *Constraint C1 (state-dependent passing direction):* a team protecting a
    lead shifts to backward/sideways passing. Parameterized as:
    `p_fwd(t) = p_fwd0 - a_prot * 1{score > 0} * w_time(t)`, where
    `w_time(t)` ramps up over the final stretch of the match.
    The model's dynamic term `a_prot` was calibrated against the observed
    decline of the forward-pass fraction in the final 15 min of matches the
    Huskies led (computed from passingevents.csv; see Task 3 results).
  - *Parameter table line:* `a_prot = 0.25, interval [0.1, 0.5], source:
    expert exchange 1 (qualitative) + calibration on late-match forward-pass
    fraction from passingevents.csv`.

## Exchange 2
- **Question:** Does the sideways/backward shift appear early when winning,
  or only late?
- **Reply:** Only late, and mainly on a narrow (one-goal) lead. With a
  2+ goal cushion teams keep playing more freely. Roughly the last 15–20 min,
  intensifying in the final 10.
- **Used in the work:**
  - *Refinement of C1:* the protection weight is gated on both
    `score_diff == 1` (narrow-lead gate `g_narrow = 1 if |sd|==1 else
    0.4*1{|sd|>=2}`) and time: `w_time(t) = 1` for the final 15 min
    (t >= 75 min of 90 min), linear ramp from 60–75 min. This produced the
    time-window used in Task 3: matches split into `pre (0–60)`, `mid
    (60–75)`, `late (75–90)` thirds, and the forward-fraction comparison was
    restricted to the late window.
  - *Interval over which the constraint holds:* final ~15 min, narrow lead.

## Exchange 3
- **Question:** After an early concession, does passing change before
  halftime, or only at the break?
- **Reply:** Only a modest in-half uptick in urgency (more forward/direct
  passing, higher tempo); the substantive structural change comes at halftime.
- **Used in the work:**
  - *Constraint C2 (goal-triggered tempo response):* a team that concedes
    shows a transient increase in attacking intent for the rest of the half.
    Parameterized as `tempo(t) = tempo0 * (1 + b_urg * 1{conceded, t < half_end})`,
    with the effect decaying toward the half-end.
  - *Calibration:* `b_urg` was set to the observed ratio of forward-pass
    fraction in the 10 min after the first Huskies-conceded goal vs the 10 min
    before it (computed in Task 3; the data showed a small uptick, consistent
    with the "modest" qualitative reply, so the value was kept small,
    `b_urg = 0.10, interval [0.05, 0.2], source: expert exchange 3 (qualitative)
    + calibration on passingevents.csv`).
  - *Structural half-boundary term:* halftime treated as a state reset in the
    season-level transition model (Task 4): `P(formation change at halftime)
    > P(formation change mid-half)`, implemented as a step change in the
    Markov transition matrix applied only between the two halves.

## Exchange 4
- **Question:** In a pushing-up losing team, do midfielders or forwards make
  the most passes?
- **Reply:** Midfielders, clearly: the ordering is midfielders > defenders >
  forwards in passes made, whether chasing or protecting.
- **Used in the work:**
  - *Constraint C3 (position-level passing hierarchy):* used to define
    "contribution" in the teamwork indicators (Task 2): per-position
    pass-share `s_p = passes_p / total_passes`, and the expected ordering
    `s_M > s_D > s_F` (GK excluded) was used as a sanity check on the
    Huskies' data and as the baseline against which "balanced contribution"
    (high evenness across all outfield positions) is defined.
  - *Indicator:* the *position balance* indicator `E_pos = -Σ_p (s_p/3) ln(s_p/3)`
    over {D, M, F} normalized to [0,1], with 1 = perfectly even. The
    expert's ordering says a "normal" team sits below 1; a team exceeding its
    own season baseline is more balanced. Computed per match in Task 2.

## Exchange 5
- **Question:** Do coaches keep the same starters most of the season, or
  rotate widely, even in poor runs?
- **Reply:** Stable core (about 7–9 regular starters), rotation at the edges
  (2–4 spots), driven by availability not results; poor results alone do not
  trigger wide rotation.
- **Used in the work:**
  - *Parameter:* core size `k_core = 8, interval [7, 9], source: expert
    exchange 5`. Used in Task 3 to define the Huskies' "core" as the 8 players
    with the most appearances, and `churn = 1 - (avg passes of core) /
    (total passes)` as a squad-stability indicator.
  - *Constraint C4 (lineup persistence):* in the season-level Markov model
    (Task 4), the probability of changing the core lineup between consecutive
    matches was set low (`q_stay = 0.75, interval [0.6, 0.9], source: expert
    exchange 5 (qualitative: stable core)`), with the remainder split among
    edge-rotation events. Poor results were explicitly *not* allowed to raise
    `q_stay` in the model (per the reply that poor results alone do not
    trigger wide rotation); only coach change (Exchange 6) or a very heavy
    loss (Exchange 8) raises churn.
  - The model was tested against the data: the Huskies' actual lineup
    persistence was computed and compared to `q_stay` (Task 3).

## Exchange 6
- **Question:** After a mid-season coach change, how fast does passing style
  change — a few games, or the whole rest of the season?
- **Reply:** Visible shift within about 3–6 matches; partial and gradual in
  degree, consolidating over the following weeks; not a season-long
  transformation.
- **Used in the work:**
  - *Parameter:* `T_style = 5, interval [3, 6], source: expert exchange 6`.
  - *Constraint C5 (coach-change transient):* the Huskies changed coaches
    between Match 9 and Match 10 (Coach1 → Coach2) and again between Match 14
    and Match 15 (Coach2 → Coach3) per matches.csv. The dynamic model (Task 3)
    applies an exponential transient to the passing-style vector
    (forward-fraction, pass-length, position-balance):
    `style_i(t) = style_i^new + (style_i^old - style_i^new) * exp(-(t - t_c)/T_style)`
    where `t_c` is the coach-change match and `t` counts matches after it.
    This gave the model a way to attribute the large observed style jump
    around Match 10/15 to the coach change rather than to opponent effect.
  - The transient was fit to the data: the actual forward-fraction trace over
    matches 10–20 was compared to the exponential (Task 3 results).

## Exchange 7
- **Question:** Over a full season, does a reliable set of familiar players
  matter more than more individual talent overall?
- **Reply:** Familiarity/coordination is the more reliable season-long driver
  at a given talent level; talent sets the ceiling. Teams with talent but
  churn underperform; modest talent with a stable core overperforms.
- **Used in the work:**
  - *Constraint C6 (cohesion dominates at equal talent):* in the
    season-level model (Task 4), team success (expected points) was made a
    function primarily of a *cohesion score* `H` (built from the Task 2
    indicators: position balance, pass-completion, core persistence,
    dyadic/triadic stability) rather than of roster size or raw individual
    statistics (which the dataset does not contain anyway).
  - *Weighting:* in the composite teamwork score
    `T = 0.35*E_pos + 0.25*Stab_d + 0.25*Completion + 0.15*CorePersist`,
    the cohesion terms (E_pos, Stab_d, CorePersist) carry 0.75 of the weight
    vs 0.25 for the pure-efficiency term (Completion), reflecting
    "familiarity is the driver, raw output is the ceiling". Source: expert
    exchange 7 (qualitative weighting choice).
  - *Generalization (Task 4):* the claim "coordination, not raw individual
    output, is the transferable success factor" was stated as the main
    generalization from soccer to other teams, with the caveat from the reply
    that talent still bounds the ceiling.

## Exchange 8
- **Question:** When facing the same opponent twice, how much does the second
  match's style differ from the first?
- **Reply:** Only modestly — a variation on the same theme; targeted
  opponent-specific tweaks, not a reinvention. More change after a heavy loss.
- **Used in the work:**
  - *Constraint C7 (re-match continuity):* in the season model (Task 4), when
    the Huskies faced the same opponent for the second time, the expected
    change in the passing-style vector was bounded to be smaller than the
    season-average match-to-match change
    (`||Δstyle_rematch|| <= 0.6 * ||Δstyle_avg||`, factor 0.6
    `interval [0.4, 0.8], source: expert exchange 8 (qualitative: moderate
    difference, not wholesale change)`).
  - *Asymmetry:* if the first meeting was a heavy loss (opponent scored 2+
    more), the bound is relaxed (`x 1.5`) — used for the few repeat-opponent
    pairs in matches.csv (e.g. Opponent1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,
    14, 15, 16, 17, 18, 19 each twice).

## Exchange 9
- **Question:** Beyond goals, what on-field signs show a team playing well
  together when the score is level?
- **Reply (process indicators):** passes per possession, completion under
  pressure, forward progression into final third; chances created and quality;
  possession share and field tilt; off-ball movement/third-man/one-touch
  exchanges; defensive compactness and recovery; tempo and transition speed;
  balance of contributions and adaptability.
- **Used in the work:**
  - This list *defined the indicator set* for Task 2. The indicators actually
    computable from passingevents.csv + fullevents.csv were:
    (i) *Pass diversity* (Shannon entropy over the 7 EventSubType values),
    (ii) *Forward-progression fraction* (share of passes with
    `EventDestination_x > EventOrigin_x + 5`), (iii) *field tilt* (share of
    passes originating with `EventOrigin_x > 50`), (iv) *pass
    completion* (inferred: a pass is "completed" if the destination player's
    next event within 10 s is not a loss-of-possession event — approximation
    since there is no explicit completion flag), (v) *chances created* (shots
    and shot-like events by the Huskies from fullevents.csv per match), (vi)
    *tempo* (mean time between consecutive Huskies passes, 1/min), (vii)
    *contribution balance* E_pos (from Exchange 4), (viii) *dyadic and
    triadic stability* (stability of the top-10 most-frequent 2- and 3-player
    pass patterns across halves of the season — the micro-scale structure
    from the problem statement), (ix) *possession share* (Huskies passes /
    all passes).
  - Indicators (iv) completion and (vii)–(viii) are the ones the reply could
    not directly give numbers for; they were defined from the reply's
    qualitative categories and computed from data, and the reply's list
    *constrained which categories we included* (e.g. we included "adaptability"
    as the second-half-vs-first-half indicator shift, not as a separate
    unbounded variable).
  - The composite teamwork score `T` (Task 2) is the normalized mean of these
    indicators, weighted as in Exchange 7.

## Exchange 10
- **Question:** The single change most likely to improve a struggling team's
  results next season?
- **Reply:** Stabilize and drill a settled core (~7–9 starters) rather than
  chasing new talent; coordination is the reliable driver at a given talent
  level, and churn undercuts whatever talent exists.
- **Used in the work:**
  - This is the direct *recommendation* for Task 3 (advice to the coach):
    the #1 recommendation became "hold a stable 7–9 player core and drill
    shared passing patterns, limit rotation to 2–4 edge spots, and do not
    overhaul the lineup after a single loss" — matching the computed finding
    that the Huskies' worst-result matches correlated with higher lineup churn
    and lower E_pos (Task 3).
  - *Constraint C8 (recommendation gate):* the model's "what to change"
    rule was: recommend a change only if the corresponding indicator is both
    (a) below the team's own season baseline by more than 0.5 standard
    deviations and (b) the indicator is one the coach can control
    (lineup/patterns, not individual talent). This produced a short, targeted
    list of 3 recommendations rather than a general one (Task 3 outcome).

---

## Parameter table (consolidated; also appears in solution.json)

| Parameter | Value | Interval | Source |
|---|---|---|---|
| `a_prot` (late-lead backward-pass shift) | 0.25 | [0.1, 0.5] | Exchange 1 (qualitative) + calibration on late-match forward-pass fraction, passingevents.csv |
| Protection window `t_prot` | last 15 min | [10, 20] min | Exchange 2 |
| Narrow-lead gate | `sd == 1` full, `|sd|>=2` at 0.4 | — | Exchange 2 |
| `b_urg` (post-concession tempo uptick) | 0.10 | [0.05, 0.2] | Exchange 3 (qualitative) + calibration on passingevents.csv |
| Position pass-share baseline ordering | M > D > F | — | Exchange 4 |
| `k_core` (squad core size) | 8 | [7, 9] | Exchange 5 |
| `q_stay` (P(core lineup unchanged, match-to-match)) | 0.75 | [0.6, 0.9] | Exchange 5 (qualitative) |
| `T_style` (coach-change style transient, matches) | 5 | [3, 6] | Exchange 6 |
| Cohesion weight in composite score `T` | 0.75 (vs 0.25 efficiency) | — | Exchange 7 |
| Re-match style-change bound | 0.6 × avg (×1.5 after heavy loss) | [0.4, 0.8] × 1.5 | Exchange 8 |
| Indicator category set (Task 2) | 9 categories | — | Exchange 9 |
| Recommendation gate: baseline deviation | 0.5 sd | — | Exchange 10 |

All other numbers in solution.json come from the task's own dataset
(matches.csv, passingevents.csv, fullevents.csv) via the analysis code in
`code/`. No empirical value was taken from memory; the two values that could
not be derived from the data alone (`q_stay`, `k_core`, and the qualitative
weights) are sourced to the exchanges above, as the policy requires.

## Note on what was *not* taken from the experts
The experts gave qualitative, experience-based guidance (direction, ordering,
rough magnitudes, "empirical regularity, not a fixed rule"). All numerical
model parameters were either (a) calibrated on the Huskies' own data as
stated above, or (b) set to the qualitative value the expert supplied with an
explicit interval and the exchange as source. The experts' wording was not
copied into solution.json; only the values, constraints, and the resulting
equations and test outcomes appear there.
