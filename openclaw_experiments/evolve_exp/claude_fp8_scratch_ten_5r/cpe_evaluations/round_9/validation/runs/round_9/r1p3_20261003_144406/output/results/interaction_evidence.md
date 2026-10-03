# Interaction Evidence — 2012_C (10 exchanges)

Policy: mechanism → constraint → parameter, one question per round. Each reply was
converted into a model element before the next exchange. No reply text is copied into
the submission; only values/constraints/equations carry over.

## Exchange 1 — dominant mechanism
- Q: how do covert groups keep in touch — tight self-talking circle vs. scattered in company-wide chatter?
- Reply (gist): tight, dense sub-group with internally concentrated traffic; routine traffic stays
  diffuse as camouflage; leaders show up as bridges/hubs, not the most talkative.
- Model effect: the conspiracy is modeled as a *community* (dense subgraph of suspicious-topic
  links) embedded in a diffuse background. Scoring is driven by topic-7/11/13 edge
  concentration inside the core, not by total message volume. Leader metric = betweenness over
  the all-topic graph (bridge position), not degree.

## Exchange 2 — primary constraint on the mechanism
- Q: what forces members of a tight circle to still talk to outsiders on everyday business?
- Reply (gist): workflow dependencies (approvals, files, sign-offs), reporting lines, cover
  maintenance, physical/logistical necessity; boundary is porous on routine topics only, while
  sensitive-topic traffic stays concentrated inside.
- Model effect: two-layer structure. Layer 1 (all topics): ordinary, porous, expected for
  everyone — used only for connectivity/bridge structure. Layer 2 (suspicious topics):
  the discriminating layer. A node is a candidate by its *suspicious-layer* position, never by
  all-topic volume; the all-topic layer only feeds the broker metric.

## Exchange 3 — content-level constraint
- Q: what content is most dangerous because it passes as ordinary business?
- Reply (gist): scheduling/logistics talk, vague urgency, budget/finance talk, concern/cover
  chatter, insider shorthand — low-information, high-frequency contact between the same few
  people on individually innocuous topics.
- Model effect: justifies *repeated* same-pair suspicious contact as signal (the pair-level
  repetition count), and treats topic 1 (company finances) as plausible cover for embezzlement —
  which is why Requirement 2's "topic 1 is connected" scenario is not a shock: it is the
  natural cover layer. Pair repetition on suspicious topics is weighted in the score.

## Exchange 4 — parameter: conspiracy size
- Q: what fraction of employees is actually in on the scheme, in real cases?
- Reply (gist): small minority; a few percent to ~10%, occasionally 15–20%; for 83 nodes with
  7 known guilty, plausible total ≈ 10–20 conspirators.
- Model effect: calibration parameter. `conspiracy_size = 16, interval [10, 20],
  source: expert exchange 4 (real-world white-collar case scale, 83-node setting)`.
  Used for (a) the decision threshold in the priority list — cut at the rank where the score
  separates from the unlabeled mass, expected to land near rank ~10–20; (b) sanity check:
  if the model flags >30 nodes above threshold, the threshold is too low, not the data.

## Exchange 5 — parameter: identity disambiguation
- Q: how do employees/investigators distinguish two same-named people?
- Reply (gist): in records, unique identifier (employee ID/node number), never the name string;
  two same-named employees are distinct nodes that must be kept separate.
- Model effect: the node number is the identity; duplicate names (Jerome 16/34, Elsie 7/37,
  Neal 17/31, Beth 14/38, Gretchen 4/32) are treated as five *distinct* people. No
  name-merging is performed. The problem's named guilty parties (Jean, Alex, Elsie, Paul, Ulf,
  Yao, Harvey) are resolved by node id: Jean 18, Alex 21, Elsie 7 (node 37 is a different
  person), Paul 43, Ulf 54, Yao 67, Harvey 49. Known innocents: Darlene 48, Tran 64, Jia 65,
  Ellin 68, Gard 74, Chris 0, Paige 2, Este 78.

## Exchange 6 — parameter: leader signature
- Q: what marks leaders vs. rank-and-file when caught?
- Reply (gist): structural position, not volume — brokerage/betweenness on paths between
  sub-clusters; issuing instructions; broad span of contact; legitimate access; often *low*
  personal suspicious-topic density (they delegate sensitive contact).
- Model effect: leader score = betweenness centrality on the all-topic graph (normalized),
  combined with suspicious-degree. Senior-manager check (Jerome 16/34, Delores 10, Gretchen
  4/32) reads: high all-topic centrality + any suspicious contact = high concern; high
  centrality + zero suspicious contact = consistent with the "insulated asset" pattern,
  flagged for indirect review, not cleared.

## Exchange 7 — constraint: record flaws
- Q: what record flaws most often weaken such cases?
- Reply (gist): identity ambiguity without a unique key; missing metadata/timestamps;
  unverified provenance; subjective topic coding; coverage gaps; stripped context;
  undocumented normalization.
- Model effect: (a) data-cleaning step explicitly documents the repairs (blank rows dropped,
  topic 18 on row 215 treated as a coding error and the link kept on topics 1/6 only,
  self-loops 3→3 and 30→30 kept as internal traffic, duplicate links 0↔2 and 18↔48 kept —
  repetition is signal per exchange 3); (b) limitations section of the submission states that
  topic codes are analyst-assigned (subjective, single source) and there are no timestamps —
  the model is a *prioritization* instrument, not proof.

## Exchange 8 — parameter: core stability
- Q: do main players keep the same trusted contacts throughout, or swap in new people?
- Reply (gist): stable core of persistent repeated ties; expansion only at the edges, slowly;
  the sensitive-topic links stay with the same few; detectable signature = persistent dense
  core + slowly changing periphery.
- Model effect: the model treats repeated same-pair suspicious edges as core evidence
  (repetition weight), and the core/periphery split (dense core vs. singly-attached fringe)
  as the categorization boundary. One-shot suspicious contacts to an otherwise quiet node are
  treated as fringe, not core.

## Exchange 9 — parameter: senior-manager mode of entry
- Q: how is a senior manager usually brought into the scheme?
- Reply (gist): deliberately, early, by a trusted insider; limited deniable role (authority,
  approvals, access, cover — not hands-on); contact through one or two intermediaries;
  low direct suspicious traffic; strong tie to one core member; often the last exposed.
- Model effect: for the three senior-manager nodes the check is (broad all-topic centrality)
  + (≥1 suspicious link) + (that link runs through a top-scoring core member) → "senior
  involvement, indirect" flag. Absence of direct suspicious traffic does not clear them;
  it is precisely the expected pattern.

## Exchange 10 — parameter: first discriminating test
- Q: what single test on the records do investigators run first to separate guilty from innocent?
- Reply (gist): check whether the suspect's suspicious-topic traffic is *concentrated inside
  the known conspirator group* rather than spread across ordinary colleagues; concentration on
  the core, not volume, is the discriminator.
- Model effect: this becomes the first term of the score — for each node, the fraction of its
  suspicious-topic edge volume that lands on the known-conspirator set (7 nodes), computed
  with both endpoints' suspicious edges. A known innocent's suspicious traffic concentrated on
  the core (if any) is a false-positive to be examined; a candidate's suspicious traffic
  scattered across unlabeled colleagues lowers its rank relative to a node whose suspicious
  traffic is core-concentrated. This term is also the decision rule for the
  conspirator/non-conspirator line (Req. 1).

## Parameter table (all empirical inputs, per workflow step 5)

| name | value | interval [a,b] | source |
|---|---|---|---|
| conspiracy_size (total guilty, of 83) | 16 | [10, 20] | expert exchange 4 |
| suspicious_topics (base case) | {7, 11, 13} | — | task dataset (Topics.csv flags) |
| suspicious_topics (Req 2 scenario) | {1, 7, 11, 13} | — | task statement (Requirement 2) |
| identity key | node number, names never merged | — | expert exchange 5 |
| leader metric | betweenness on all-topic graph | — | expert exchange 6 |
| senior-manager rule | centrality + ≥1 suspicious link via core intermediary | — | expert exchange 9 |
| first discriminator | fraction of suspicious edge volume on known-conspirator set | — | expert exchange 10 |
