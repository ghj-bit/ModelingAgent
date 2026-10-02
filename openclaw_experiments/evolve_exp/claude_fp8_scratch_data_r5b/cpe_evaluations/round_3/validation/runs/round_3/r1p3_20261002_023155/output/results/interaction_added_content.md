# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — 2012_C (Crime Busting)

Three expert exchanges, one question each, in sequence. Each reply is turned into a
concrete element of the model below; nothing in this file is copied into solution.json.

## Exchange 1 — data/model structural fit

**Question:** When office workers secretly coordinate, does each person usually talk to
just a few close coworkers, or do they end up chatting with many different people?

**Reply (gist):** Covert coordination shows a small dense core: each conspirator
concentrates most messages with a handful of recurring partners plus a long tail of
routine cover traffic. Degree alone is weak evidence; repeated, topic-specific exchange
with the same few people is the stronger signal.

**How the reply became work (model element E1):**
- The graph is modeled as directed weighted edges where each message contributes +1 to
  the sender->recipient weight, and multi-topic messages contribute once per topic.
- Following the "dense core, weak degree" guidance, raw degree is NOT a primary score.
  Instead the model uses (a) suspicious-topic volume, (b) *repeat-contact* structure:
  weighted betweenness on the suspicious-topic subgraph plus ego-subgraph clustering /
  fraction of ties to already-flagged nodes.
- The two-phase score (Req. 1) is: S1 = normalized suspicious-topic in+out volume;
  S2 = betweenness centrality in the suspicious subgraph + share of traffic with
  known conspirators. Final rank = mean of normalized components, i.e. convergence
  across distinct signals. Interval of validity: small dense-core regime (a few dozen
  actors, tens to hundreds of messages), which is exactly this dataset (83 nodes, 400
  links).

## Exchange 2 — dominant bias / selection mechanism

**Question:** Besides the suspicious meeting planning and system flaws, what other kind
of ordinary-looking talk would make you suspect people are covering their tracks?

**Reply (gist):** Cover-up talk is meta-communication: warnings to keep quiet,
deflection scripts, innocuous topics woven in as camouflage, management of who is
watched/kept out of the loop, denial clusters. The tell is the *pattern* — low-
information reassurance among the same few people, clustered around suspicious topics.

**How the reply became work (model element E2):**
- Topics are not all equal even outside the three "suspicious" codes. Topic 1 (company
  finances, liquid assets) and topics 4 and 6 (the Paige controversy / promotion
  politics, which name the key non-conspirators as the people being watched) carry
  cover-up / surveillance-adjacent content. The model therefore builds a secondary
  "soft-suspicious" weight for topics 1, 4, 6 with a small weight (w_soft = 0.25 vs
  w_hard = 1.0 for 7, 11, 13), and an *adjacency* term: traffic on soft topics *with the
  same partners as hard-topic traffic* is up-weighted (the camouflage pattern), while
  soft-topic traffic to unrelated partners is not.
- Concretely, per node: camo_score = soft-topic volume restricted to partners who also
  exchange hard topics, normalized. This enters the final score at 15%.
- Bias acknowledged: message traffic is a censored sample (only 400 links of a much
  larger true traffic; transcripts unavailable). Counts underrepresent true volume and
  are heterogeneous across people (different message habits), so all volume terms are
  rank-normalized rather than used in absolute units, and the validation criterion
  (below) is what makes the conclusion decision-relevant.

## Exchange 3 — validation / interpretation criterion

**Question:** If investigators get a ranked suspect list, what would make them trust it
enough to start acting on the top names first?

**Reply (gist):** Trust requires convergence across independent metrics, robustness to
perturbations, recovery of the known conspirators at the top and known non-conspirators
at the bottom, a visible separation gap, and consistency with the EZ precedent.

**How the reply became work (model element E3 — the decision rule and validation):**
- Validation metric computed on the labeled 15 (7 known conspirators, 8 known
  non-conspirators): the mean rank of known conspirators vs known non-conspirators, and
  a "clean separation" test: the lowest-ranked known conspirator outranks the
  highest-ranked known non-conspirator.
- Robustness: the full pipeline is re-run with each of the three hard topics dropped in
  turn, with all score weights jittered by ±20%, and with each known conspirator
  removed from the prior; top-15 membership and the separation property are recorded.
- Leader nomination: senior managers Jerome (16, 34), Delores (10), Gretchen (4, 32) are
  scored like everyone else and additionally tested: if a manager scores above the
  50th percentile of the full list, they are nominated as a possible leader/figurehead.
- Requirement 2 re-run: topic 1 is promoted to hard (w=1.0) and Chris (0) added to the
  known-conspirator prior; the same pipeline is re-run and the diff of the ranking is
  reported.

All three reply-derived elements (E1 dense-core metrics, E2 camouflage/soft-topic
term, E3 convergence + robustness + separation validation) appear in the code
(code/model.py) and in the solution.json fields, in this work's own formulation.
