# Interaction Evidence — MM-Bench 2012_C

Three expert exchanges, one question each, in the order the interaction policy
requires (mechanism → causal hierarchy → decision threshold). Each reply was
converted into a parameter, assumption, or decision rule in the model before the
next exchange. No expert sentence, phrasing or structure is reproduced in
`solution.json`; only the values, constraints, and decisions that the replies
support appear there.

## Exchange 1 — operational structure of the data

**Question** (file: `logs/operator_feedback/expert_question_1.md`): whether
message traffic between conspirators in a real investigation arrives as a
steady, even stream or in bursts/clusters around key events.

**Reply (summary of substance):** conspiracy traffic is overwhelmingly bursty,
not steady; it clusters around planning meetings, deadlines, arrests, money
transfers, perceived threats, with long quiet lulls; timing and temporal
clustering are themselves signal — a burst of suspicious-topic messages among
a small set of people around a common event is more indicative of coordination
than the same volume spread evenly; this holds over the full observation window
of the kind of case in question.

**How the reply became work:**
- Adopted as modeling assumption A1 (recorded in `solution.json`, task 1,
  `task_analysis`): conspiracy traffic is event-clustered, not uniform.
- Interval of validity: the whole observation period of the case (no
  sub-window qualification was given or needed).
- Because the supplied `Messages.csv` carries **no timestamps**, a true temporal
  burst test was impossible; the reply therefore dictated the design of the
  burstiness feature: instead of clustering over time, clustering is measured
  as the concentration of suspicious-topic volume across a node's neighbors
  (coefficient of variation of the positive suspicious edge weights incident
  on the node). This is feature f4 in the model (`code/model.py`, feature
  `burst`), weighted 0.3 in the score. The feature is documented in
  `solution.json` task 1 as a proxy whose temporal version is the
  highest-value upgrade once transcripts with timestamps exist (task 3).
- The EZ case in the problem statement (topic-3 messages clustering tightly
  among Dave/George/Ellen/Harry while social topic-5 traffic is scattered)
  independently corroborates the same regularity, so the assumption is
  consistent with both the expert's account and the worked example.

## Exchange 2 — causal hierarchy: direct coordination vs hidden broker

**Question** (file: `logs/operator_feedback/expert_question_2.md`): given the
bursty structure, whether heavy suspicious-topic exchanges between two people
usually indicate direct coordination between them, or that both are actually
talking to a third person who drives the activity.

**Reply (summary of substance):** neither reading is the reliable default, but
heavy two-way suspicious exchange more often means **direct coordination**;
the "both talk to a third person" reading is a **hub-and-spoke** pattern —
many pairs linked through one central node, a leader/broker — and is
distinguishable structurally, not volumetrically: a strong two-way tie =
direct working relationship; low mutual traffic plus heavy traffic to a common
node = broker pattern. Conspirators minimize exposure, so suspicious content
concentrates on few direct ties.

**How the reply became work:**
- Adopted as assumption A2 (task 1, `task_analysis`) and as the rationale for
  using **two different kinds of centrality** in the score:
  - direct suspicious connectivity (features f1 suspicious weighted degree and
    f2 suspicious degree) captures the *direct coordination* reading;
  - eigenvector centrality on the suspicious subgraph (feature f3) captures the
    *broker/leader* reading — a node scores high precisely when its suspicious
    partners are themselves well connected, the structural signature of the
    hub-and-spoke pattern the expert described.
- It also dictated the **leader-nomination rule** used in task 1 and task 4:
  leaders are nominated by eigenvector centrality on the suspicious subgraph,
  not by raw degree — because raw degree cannot separate a busy participant
  from a quiet broker, which is exactly the distinction the reply drew. Result:
  Alex (n21) and Yao (n67) nominated as coordinating/leader candidates
  (eigenvector scores ~0.98–1.00 vs next-highest ~0.78).
- Validity interval: the whole observation window; the reply made no
  window-specific qualification.

## Exchange 3 — decision-relevant threshold for the priority list

**Question** (file: `logs/operator_feedback/expert_question_3.md`): how wrong
the ordering of a suspect priority list can be before the list stops being
useful for surveillance and interrogation.

**Reply (summary of substance):** the ordering does not need to be precise; it
needs to be **useful at the top and honest about uncertainty**. True
conspirators concentrated in roughly the top 10–20% of the ranking = the list
is doing its job; scattered uniformly = useless. Moderate misordering inside
the top tier (e.g. 3rd vs 7th) rarely changes outcomes. What breaks usefulness
is **confident wrongness**: a known-innocent near the top, or a real
conspirator buried far down. The **discriminating cut** separating
"investigate" from "don't" is often more valuable to the DA than the fine
order.

**How the reply became work:**
- Set the model's validation and reporting criteria (used in tasks 1, 2, 4):
  - the **primary validation metric** is concentration of known conspirators
    in the top tier plus exclusion of known innocents from it — implemented as
    Youden's J on the 15 known labels for cut selection, and reported as
    "all 7 known conspirators in the top 13 of 83 (top 16%), within the
    expert's 10–20% band; all 8 known non-conspirators at or below the cut".
  - the **discriminating cut** is reported as the decision-relevant output,
    with the fine rank order explicitly demoted to secondary: every task's
    outcome analysis states that the cut line, not the exact order, is what
    the DA acts on, and ranks 10–23 in the Requirement 2 case are reported as
    an "ambiguous band" rather than being over-interpreted.
  - the **bias check** the expert named — a known-innocent near the top is the
    worst failure — is reported concretely: in the base case the highest
    scoring known-innocent (Paige, 0.3056) lands exactly at the cut, and the
    Requirement 2 dilution (Darlene, known-innocent, scoring above the newly
    revealed conspirator Chris) is reported as the model's honest failure mode
    under a noisier topic set, not hidden.
- Validity interval: applies to any priority list for investigative
  resourcing (the reply was stated generally, not case-specific).

## Cross-check

- No expert text appears in `solution.json`: the container contains only the
  model's own formulation of the premises it supplies (bursty coordination,
  direct-vs-broker structure, top-tier/cut decision criterion) together with
  the computed numbers that use them.
- Each exchange produced a concrete model element before the next question was
  asked: Exchange 1 → feature f4 + assumption A1; Exchange 2 → feature f3 +
  leader rule + assumption A2; Exchange 3 → validation metrics, cut-selection
  rule (Youden J), and the reporting hierarchy (cut > rank order).
- No requests for help with coding, debugging, computation, or standard
  derivations were made; all three questions were common-sense questions about
  how real investigations behave, each under the twenty-word limit.
