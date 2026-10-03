# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — MM-Bench 2012_C

Ten exchanges, one question each. Each reply is converted below into a
concrete model parameter or decision rule; the question file, request/reply
JSON and the code location that implements the rule are listed per exchange.

## Exchange 1 — metric weighting
- Question: quiet tight-group chatterer vs broad-reacher — which is the more
  likely co-conspirator?
- Reply (gist): neither alone is decisive; the signal is contacts **concentrated
  on the suspected group**, plus insularity of a small tight group; high raw
  degree is weak evidence (hubs are usually managers/coordinators).
- Turned into work:
  - `METRIC_WEIGHTS` in `code/conspiracy_model.py`: concentration metrics
    `sus_ratio` (0.24), `susp_in`/`susp_out` (0.16 each), `sus_clique` (0.16),
    `insularity` (0.12) dominate; raw `degree` set to 0.01 (demoted).
  - Validation: known conspirators occupy ranks 1–7 (mean 6.0) vs known
    non-conspirators (mean 37.6) in R1.

## Exchange 2 — leader count
- Question: leader-to-participant ratio in fraud rings?
- Reply (gist): small core, ~2–5 organizers, roughly 1 leader per 3–5
  participants; in a small office case expect 1–3 true organizers.
- Turned into work: leader nomination capped at 3 candidates
  (`cands[:5]` printed, 3 selected for the report per the 1–3 estimate);
  constant `LEADER_PER_PARTICIPANT = 0.25` documented in the parameter table.

## Exchange 3 — leader identity signal
- Question: whose calendar/location do organizers set for secret meetings?
- Reply (gist): the **initiator of the scheduling broadcast** to several
  others is the leader signal; the host may be a decoy.
- Turned into work: leader sub-score uses topic-7 (secret-meeting topic)
  message volume of a node, 50% weight in `leader = 0.5*norm(X7.sum(1)) +
  0.3*norm(broker) + 0.2*norm(anchor out-traffic)`.

## Exchange 4 — breadth is role
- Question: many coworkers — boss or friendly person?
- Reply (gist): usually role-driven (managers, coordinators); high degree
  alone is weak; conspiratorial distinction is contact concentration, not
  breadth.
- Turned into work: confirmed the `degree` weight demotion (0.01) from
  exchange 1; no high-degree non-anchor outranks the known group except the
  flagged hub-adjacent candidates, which are explicitly reported as
  "managerial-breadth, low conspiracy support".

## Exchange 5 — non-conspirators look ordinary
- Question: does contact with a cleared employee stop?
- Reply (gist): no — cleared people's traffic looks like any ordinary
  employee's; a negative label must not structurally suppress or boost.
- Turned into work: known non-conspirators are used **only as validation
  anchors for rank separation**, never as negative edges in the scoring
  graph (no negative weighting of their neighbors).

## Exchange 6 — planning traffic > execution traffic
- Question: who matters more for spotting fraud — talkers or doers?
- Reply (gist): planning/coordination talkers are the detectable signal in
  message data; doers often operate in routine-looking or off-message
  channels.
- Turned into work: suspicious-topic (planning: 7/11/13, +1 in R2) metrics
  carry 60%+ of total weight; generic volume metrics carry little.

## Exchange 7 — lockouts are confounders
- Question: why do companies suddenly lock employees out of the network?
- Reply (gist): defensive IT action (incident, patch, legal hold); treat as a
  confounder, not guilt evidence; a traffic drop around it is not a change in
  guilt.
- Turned into work: noted as a limitation in the submission; the single
  traffic dip around the topic-13 off-line period (Paige/Ellin/Chris) is
  documented as expected confounding, not used as evidence.

## Exchange 8 — leaders are mid-level insiders
- Question: top executives or mid-level staff run workplace fraud?
- Reply (gist): usually mid-level organizers with authority but low profile;
  seniority alone is weak — senior managers count only if their traffic
  concentrates on conspirators/suspicious topics.
- Turned into work: no seniority prior applied to Jerome/Dolores/Gretchen;
  they enter the report only via their ordinary scores (R1: ranks 10, 47,
  66 and 31/26/66; none in top 7).

## Exchange 9 — core clique + broker structure
- Question: direct contact or relay through one person?
- Reply (gist): dense direct clique at the center; core-to-peripheral
  contact routed through a broker/lieutenant; a node between the core and
  unconnected peripherals is a likely organizer.
- Turned into work: `broker` metric (neighbors of i that are pairwise
  disconnected, weight 0.10) + 30% of the leader sub-score; `sus_clique` and
  `clique_density` score the core-clique signal.

## Exchange 10 — persistence and privacy of ties
- Question: a few private messages a week for years — trustworthy closeness?
- Reply (gist): yes — persistence + privacy beat volume; weight by reciprocity
  and by whether the tie carries suspicious topics.
- Turned into work: `sus_recip` (suspicious-topic reciprocity, 0.10) and
  `reciprocity` (0.06) metrics; tie strength = mutual + suspicious-topic,
  exactly the rule stated.

## Parameter table (calibrated inputs used by the model)
| name | value | interval | source |
|---|---|---|---|
| leader:participant ratio | 1:4 | [1:5, 1:3] | expert exchange 2 |
| leader sub-score weights | (0.5, 0.3, 0.2) on (sched, broker, anchor-out) | scheduler 0.4–0.6 | expert exchanges 3, 9 |
| suspicious-topic weight boost (R2) | +50% on suspicious metrics | +30%–+80% | task Requirement 2 + exchange 6 |
| metric weights (11 metrics) | see code `METRIC_WEIGHTS` | concentration >> breadth | expert exchanges 1, 4, 6, 9, 10 |
| self-loops, exact duplicates | dropped (2 + 9 rows) | — | data cleaning |
| out-of-range topic 18 (1 row) | kept as non-suspicious | — | data cleaning |
