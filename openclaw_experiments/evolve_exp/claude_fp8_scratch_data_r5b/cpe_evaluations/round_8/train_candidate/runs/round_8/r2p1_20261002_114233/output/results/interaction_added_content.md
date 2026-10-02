# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence

Three exchanges, one question each. Each reply was converted into a model
parameter / equation / decision rule before the next exchange.

## Exchange 1 — Operational mechanism of "momentum"

**Question (expert_question_1.md):** When watching a tennis match, do short
bursts of winning points and big plays change how the players actually play —
does the player losing a run start hitting more risky shots / more errors, or
does shot selection and error rate stay pretty steady?

**Reply (summary of what travels into the model):** Runs *do* change how players
play, but **modestly and asymmetrically**, not as a dramatic switch.
- The player **losing** the run takes on **more risk** (bigger serves, more
  line-aiming, earlier winner attempts) → rise in unforced errors and double
  faults, shorter rallies.
- The player **on** the run plays **safer** → higher first-serve %, more
  margin; error rate falls.
- The effect is **real but small** relative to baseline noise; point outcomes
  are close to independent and the **serve advantage dominates**. Runs look
  dramatic largely because of randomness; the behavioral shift is a
  **second-order effect**.
- It is **state-dependent**: strongest at high-stakes moments (break points,
  set points, late sets) and for players with fragile confidence; weak for
  stable temperament or early in a set.

**How it changed the work:**
- Parameter/assumption: momentum is a *state-dependent* deviation, not a
  raw point count. The metric M_t compares each point to a **state-conditioned
  fair baseline** (serve + break-point + high-stakes), so M_t measures
  performance *relative to what the serve advantage already explains*.
  Baselines are estimated from the data (see parameter table in
  solution.json: serve win rates 0.743–0.766 first / 0.507–0.553 second;
  break-point server win 0.635–0.665).
- The behavioral-shift direction (trailing player raises UFE and DF, leading
  player tightens serve) became the **feature construction** in the
  prediction model: trailing/under-pressure indicators are the server's
  first-serve-in rate and the UFE rate of the player in danger.
- Interval/condition of validity: the drift is "small relative to baseline
  noise," which justifies treating M_t as a *surprise* signal rather than a
  level, and using it in the momentum flow rather than as a match-winning
  probability.

## Exchange 2 — Causal hierarchy / dominant leading indicators

**Question (expert_question_2.md):** When a player about to see a swing is in
danger, which single thing do you most watch — drop in first-serve %, jump in
unforced errors, or losing short exchanges? What does it mean?

**Reply:** The single most informative is a **drop in first-serve
percentage — but only for the *server*** in danger. The serve is the one stroke
the player fully controls; missing first serves is the earliest, cleanest sign
that rhythm/confidence is slipping (steering or over-hitting), and it has
mechanical consequences (second serves get attacked → more return pressure,
longer defensive rallies) that turn a wobble into a lost game. **Caveat:** it
is a *server-side* indicator; for a **returner** in danger watch instead for a
**jump in unforced errors** (over-committing on the return). Losing short
exchanges is the **weakest** leading indicator — a *symptom* of the other two,
not an independent cause.

**How it changed the work:**
- Changed the **feature set / causal ordering** of the prediction model.
  Primary leading indicators: `fsin` (server's first-serve-in rate, trailing
  window) and `ufe_srv` / `ufe_ret` (UFE rate of the server vs the returner),
  each computed **for the player who is the server** at that point (server-side
  logic per the reply).
- Excluded "losing short exchanges / short-rally loss" as an independent
  feature, per the reply that it is only a symptom — it is not in the model's
  driver list.
- This is a direct causal-hierarchy statement used to order the predictors:
  serve-rhythm slip → attacked second serve → lost game, rather than treating
  all three as independent causes.

## Exchange 3 — Decision-relevant uncertainty threshold

**Question (expert_question_3.md):** If a tool said a swing was "likely coming
soon," how far out / how often wrong could it be before a coach would ignore
it at a changeover? What kind of call is actually useful?

**Reply:** A changeover call is worth acting on only if it is **specific to the
next few games (~2–4 games, ~10–20 min)** and **right clearly more often than
not**. Working threshold: **ignore a warning that fires more than about a third
of the time without the swing happening** ("wrong half the time is noise").
What is useful is **not a probability but a named, actionable cue tied to a
specific player and a specific mechanism** (e.g. "your first-serve % dropped
the last two service games — commit to the target"), about the *current* match
state, not a generic tendency. A bare "momentum is about to swing" is not
useful.

**How it changed the work:**
- Decision rule / threshold: the prediction model's **alert threshold is set
  where the false-alarm rate ≤ 1/3** (precision ≥ ~0.5), and it is reported at
  that operating point rather than as a raw probability. This is exactly the
  threshold used in the holdout and out-of-fold metrics (false_alarm ≤ 0.31).
- Horizon parameter: the label window **H = 20 points** and swing
  persistence **hold = 6 points** encode the "next 2–4 games, must persist"
  criterion — a swing must last at least a game-length run to be "real,"
  matching the near-term, actionable horizon.
- Output form: the deliverable is framed as a **mechanism-specific, named
  cue** (which player, which mechanism — serve slip vs return UFE), not a
  bare "momentum" number. The model's coefficient table (server first-serve-in
  and UFE signs) is what produces that named cue.
- Interval/validity: the threshold (≤1/3 false alarm) and horizon (2–4 games)
  hold for the *changeover decision* context the expert described; they are
  stated as the model's operating constraints in the solution.
