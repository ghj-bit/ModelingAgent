# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — 2012_C

## Exchange 1 — Operational definition of the data variable

- Question: `logs/operator_feedback/expert_question_1.md` (message traffic as a clue to involvement — is a person's activity count a reliable signal?)
- Reply (summary): traffic measures willingness to communicate on the observed channel, not actual involvement. Silence is uninformative (deliberate withdrawal or off-channel contact looks identical to innocence), so low activity is a weak negative signal. High activity conflates genuine conspiratorial contact with general chattiness, so raw counts rank sociability, not guilt. What carries signal is structure and content: counterpart identity, reciprocity, clustering, and the topics used.
- How the reply entered the work: the score uses share-based (volume-normalized) quantities, never raw message counts. `T(v) = suspicious-topic messages / total messages sent by v` (chattiness normalization, per the reply's "normalize activity by each person's overall volume") and `C(v) = share of v's contacts who are known conspirators` (counterpart identity, per "weight topic and counterpart identity far above message count"). Interval of validity: within this office, this channel, this 400-message sample.

## Exchange 2 — Causal direction of a strong tie

- Question: `logs/operator_feedback/expert_question_2.md` (heavy two-way chatting: plotting together, or just working in the same team? the one clue to tell them apart?)
- Reply (summary): tie strength mostly tracks organizational proximity — same team/project — and is close to uninformative about guilt by itself. The first clue to rely on is whether the tie is confined to the suspicious topics: legitimate colleagues talk about everything, a conspiratorial pair shows a narrow, topic-restricted channel — disproportionately flagged topics, thin ordinary-topic traffic. Caveat given: conspirators may also be genuine teammates, so topic concentration is strong but not decisive.
- How the reply entered the work: the model's primary discriminator is topic concentration relative to the person's own traffic (component T), not edge strength; contact to known conspirators (component C) is treated as secondary corroboration, and the final ranking is a clear-gap decision (see Exchange 3). The "not decisive" caveat is carried into the limitations section of solution.json (requirement 4).

## Exchange 3 — Robustness threshold for acting on a signal

- Question: `logs/operator_feedback/expert_question_3.md` (how unusual must the topic concentration be before acting — one odd message, or standing out from the office baseline?)
- Reply (summary): never act on a single flagged message (forwarding, mis-addressing, chance placement with 15 topics and 400 links). Act only on a person whose flagged-topic share is clearly above the office baseline — top of the distribution, ideally repeated across multiple messages and multiple distinct counterparts; a single tie to a known conspirator plus one flagged message is suggestive, several flagged exchanges with several conspirators is actionable. With 7 known conspirators among 83 the base rate is low, so a clear gap, not a marginal one, is required; the right threshold is where the concentration separates a small cluster from the bulk, visible only after ranking.
- How the reply entered the work: the decision rule is relative: rank all 83 nodes by S(v) and treat the top of the distribution as the watch list, requiring (i) multiple suspicious-topic messages (susv ≥ 3) and (ii) concentration across multiple distinct suspicious contacts. The known-conspirator block (ranks 1–8) and known-innocent block (ranks 13, 16, 19, 57–80) define the visible gap: the actionable watch list is the non-identified nodes sitting in the top of the distribution with that support — Seeni (5), Dolores (9), Jerome/16 (10) — i.e., "top handful, clear gap", exactly the reply's criterion. Base-rate caution is stated in the outcome analysis.
