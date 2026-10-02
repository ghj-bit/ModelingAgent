# Interaction evidence — 3 exchanges with the domain expert (soccer coach)

Each exchange: question (common-sense, not coding/computation), paraphrased reply, and
concretely how the reply changed the model/work. Replies were used as input
(parameters/constraints/tests), never copied verbatim into the solution.

## Exchange 1 — What do the recorded passes actually represent?

- **Question (logs/operator_feedback/expert_question_1.md):** Does the match
  data list every pass a player attempted, including those intercepted or
  missed, and does it say where the player intended to pass?
- **Paraphrased reply:** The list contains only completed passes. There is no
  field for the intended receiver, and a pass that was intercepted or missed
  simply does not appear. So any connection in the data is a connection that
  actually materialized, and pass volume alone does not tell how risky or
  accurate the play was.
- **How it changed the work (became model constraints/tests):**
  1. Edge semantics fixed: an edge in the passing network means "these two
     players reliably find each other", not "these two players try to pass to
     each other". All density/centrality statements in the solution are
     explicitly interpreted this way.
  2. Constraint: no accuracy/interception rate may be estimated from this data
     (the denominator — attempts — is missing). This is recorded as a stated
     bias/limitation, and the expert's own remedy (see Exchange 3) is noted as
     the follow-up measurement.
  3. Test used: cross-team pairs (235 recorded passes between opponents) were
     treated as misassigned/completed cross-team events, not as "attempts".

## Exchange 2 — How long does it take a new coach's style to show?

- **Question (expert_question_2.md):** The head coach changed three times this
  season (matches 1–9, 10–14, 15–38). From coaching experience: does the team's
  way of playing visibly change within a few matches of a new coach arriving,
  and does it usually take a whole season before the team settles into a stable
  style?
- **Paraphrased reply:** A new coach's style is recognizable within roughly the
  first 3–5 matches (formation, pressing height, build-up, mix of passes). A
  genuinely settled, fluent style takes most of a season. The short second
  stint (5 matches) should be treated as entirely transitional, and the third
  coach's team is reasonably considered settled from around the 4th–5th match
  of that stint.
- **How it changed the work (became the validation design):**
  1. The season was split into three regimes R1 (m1–9), R2 (m10–14),
     R3 (m15–38); all season-level aggregates were computed both on the whole
     season and on a *settled* set: R1 matches 4–9 plus R3 matches 19–38
     (n=26), with R2 excluded as all-transition (parameter: transition window
     = first 4 matches of each regime; settle point of R3 = match 19).
  2. The regression and all significance tests (block bootstrap, LOO,
     permutation) were run on the settled set, not the raw season, to remove
     coach-change non-stationarity as a confound.
  3. Test used: regime-3 transition (m15–18) vs settled (m19–38) comparison —
     density 1.418 vs 1.502 and pass-type diversity 0.681 vs 0.730, a measurable
     settling shift, corroborating the expert's mechanism and justifying the
     split.

## Exchange 3 — Would you still act on the advice without completion data?

- **Question (expert_question_3.md):** Since the data cannot show intercepted
  or failed passes, how much would it matter to know the true completion rate
  before deciding which links/players to build next season around?
- **Paraphrased reply:** Completion and interception rates are core coaching
  numbers and are not irrelevant. But a coach would still act on the
  completed-pass network: it tells who is reliably reached, which links carry
  the ball forward, and who is central to circulation. The volume of a link
  must not be read as quality — a heavily used link may be safe or may be a
  habitual mistake. The missing accuracy information would be filled from
  film review, not from this dataset.
- **How it changed the work (became the recommendation rule):**
  1. Constraint on the Task-3 advice: recommendations are limited to *structure
     and role* (which players to centralize, which links to develop, who is
     exposed), explicitly not to "pass more" advice, because volume ≠ quality.
  2. The top recommendations in the solution are therefore about the backbone
     (the midfield triangle and the back-line build-up chain) and about
     reducing dependence on single hubs, not about increasing pass counts.
  3. Limitation statement: the one number the coach most wants (completion /
     interception) is declared as unmeasurable from this data, with the
     expert-specified remedy (video review) named as the follow-up.
