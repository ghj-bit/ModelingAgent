# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — 2012_C

Three exchanges, one question each. For each: the question, the expert's reply
(summarized), and — critically — the concrete parameter, constraint, equation,
or decision rule the reply became, plus where the model uses it.

## Exchange 1 — Structural assumption (normal message-traffic structure)

**Question.** In a workplace, do workers send messages to a few favorite
coworkers repeatedly, or spread them evenly? Is heavy contact with a few
people normal office life or a sign of something?

**Reply (summarized).** Workplace traffic is strongly concentrated — most
people talk to a small set of close collaborators and barely reach the rest;
degree distributions are heavy-tailed. Heavy contact with a few people is
normal and, by itself, a weak indicator. It only signals conspiracy in
combination with other evidence (suspicious topics, tight otherwise-unexplained
cluster). "Frequency relative to role and topic is what matters."

**Became in the model (source: exchange 1).**
- **Constraint: do NOT use raw message volume as a conspiratorial score.**
  The feature set deliberately has no plain in-degree/out-degree term. The
  only degree-like feature is *suspicious-degree* (distinct neighbors reached
  **via suspicious topics**, feature index 4) and normalized *total degree*
  (feature index 5), which the logistic fit is allowed to down-weight — it in
  fact did (weight ≈ 0.034, near zero). This encodes the expert's
  "frequency alone is a weak indicator; frequency relative to topic is what
  matters."
- **Design decision: score by topic-conditioned structure, not traffic
  volume.** The dominant learned weights are on suspicious-topic exposure,
  outgoing suspicious messages, and adjacency to known conspirators — i.e. the
  "combination with other evidence" the expert required, not raw centrality.

## Exchange 2 — Causal mechanism (who sends the secret messages)

**Question.** In an embezzlement conspiracy, do the people doing the actual
criminal job (moving money, breaking in) send the secret messages, or are the
secret messages planning chatter from the organizers while others stay quiet?

**Reply (summarized).** Both patterns occur, but in a small fraud conspiracy
the **organizers are usually the heaviest senders on the secret topics**; the
hands-on operators communicate less on secret topics (their work is technical,
often done alone, and they appear mostly as recipients or brief
acknowledgments). Peripheral members stay quiet and are hard to separate from
innocent people by traffic alone. Causal direction is roughly
coordination → execution; message volume on suspicious topics points more
reliably at organizers than at operators, and operators must be caught through
other signals (position, access, adjacency to known conspirators).

**Became in the model (source: exchange 2).**
- **Added a directional organizer feature: outgoing suspicious-topic message
  count (feature index 1, `sus_out`).** Asymmetric (sender-weighted) rather
  than the undirected exposure, so heavy *senders* on secret topics rank high
  — matching "organizers are the heaviest communicators." It is separate from
  total exposure so the fit can weigh planning-chatter volume on its own.
- **Added the operator-catch features the expert said traffic alone cannot
  supply: (a) adjacency to known conspirators over suspicious edges (feature
  index 2, `adj_known`) and (b) a role-risk feature (feature index 6) built
  from Topics.csv content** (Chris/Paige/Ellin are named as security-policy
  authors and as the targets of the topic-13 offline plan). This operationalizes
  "operators must be caught through position, access, and topic adjacency to
  known conspirators," not through their own message volume.
- **Stated limitation in the report:** quiet peripheral members / hands-on
  operators are under-detected by any traffic-based model; the report says so
  explicitly rather than claiming full coverage.

## Exchange 3 — Decision threshold (how many names are actionable)

**Question.** Since the list is for surveillance/interrogation, not arrest,
roughly how many names at the top would investigators work through first, and
how far down does a name become too low to act on?

**Reply (summarized).** A working shortlist of **~10–20 names** is the
realistic top tier; below about **rank 30–40** the list stops being
actionable (cost of investigating exceeds expected payoff). The exact cutoff
should track the model's own score distribution — a clear gap/elbow in the
ranked scores should set the line, not a fixed number.

**Became in the model (source: exchange 3).**
- **Tiering rule (decision rule), `tier()` in code/model.py:**
  - ranks 1–20 → `T1-actionable` (the surveillance/interrogation shortlist),
  - ranks 21–40 → `T2-watch` (keep on file, do not yet act),
  - rank 41+ → `T3-monitor`.
  These bounds (20 / 40) are the expert's shortlist size and the "below ~30–40
  not actionable" threshold, applied to this 83-node case.
- **Elbow check reported:** the summary reports the score gap between the
  known-conspirator block and the known-non-conspirator block
  (`sep_ok` / `sep_gap`) so the cutoff is justified by the score
  distribution, not asserted — per the expert's "let the gap set the line."
  In Req1 all 7 known conspirators fall in ranks 1–11 and all 8 known
  non-conspirators in ranks 24–83, i.e. the actionable shortlist (top 20)
  captures every confirmed conspirator with margin.

## What the replies did NOT do
The replies were used only as inputs (the constraints, features, and tier
bounds above). No expert sentence, phrase, or structure is copied into
`results/solution.json`; the values (weights 20 / 40, the feature choices, the
"no raw volume" constraint) travel in my own formulation, integrated where the
model uses them. No reply stands in for a derivation or a computation.
