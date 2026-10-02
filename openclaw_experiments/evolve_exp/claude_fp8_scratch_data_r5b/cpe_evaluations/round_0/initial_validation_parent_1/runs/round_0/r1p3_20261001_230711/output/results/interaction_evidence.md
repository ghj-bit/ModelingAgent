# Interaction Evidence — Problem 2012_C

## Exchange 1

**Question (to expert):** "In a white-collar embezzlement conspiracy at a big company, what kind of everyday office messages give the participants away to investigators?"

**Expert reply:** Covert meeting requests, secrecy warnings ("don't let him nose around"), stress about an unnamed "important" matter, off-topic huddles, and tight late-night or repeated contact among a small subgroup.

**How the reply affected the work (concrete):**
The five listed red-flag families became the explicit signal families in the model. In particular:
- "covert meeting requests" and "off-topic huddles" → the **covert-meeting / suspicious-topic signal** (topics 7, 11, 13 flagged in the data as conspiratorial / key).
- "secrecy warnings" → the **secrecy signal** (messages that warn others about being watched / keeping quiet).
- "stress about an unnamed important matter" → captured as a secondary covert-topic signal.
- "tight repeated contact among a small subgroup" → the **tight-subgroup contact signal** (repeated pairwise contact between a small set of nodes).

These four families are scored per-node and combined into the composite likelihood score (see solution.json). The answer is what told us that *covert topic content + small-subgroup contact* are the strongest, *secrecy* is a supporting signal — matching the ordering given in exchange 3.

## Exchange 2

**Question (to expert):** "In cases like these, how do investigators tell the ringleaders apart from the lower-level members who joined?"

**Expert reply:** Leaders initiate the covert meetings and set their timing, receive deference and status reports, sit at the hub connecting otherwise separate members, and are the ones others warn each other about. Followers mostly relay, comply, or cover.

**How the reply affected the work (concrete):**
This directly defines the **leader-score** used in Requirement 1. The model computes, per node:
- **initiator score**: fraction of a node's *suspicious-topic* messages that it *sent* (started) vs. received. Leaders initiate.
- **hub/bridge score**: betweenness centrality on the suspicious-topic subgraph (connects otherwise separate members).
- **deference/received-status-report proxy**: in-degree within the suspicious subgraph weighted by whether messages look like reports/updates (topic 7, 11, 13) — followers relay and report upward.
- **warned-about proxy**: number of distinct other nodes who send *secrecy-type* messages that reference or involve this node.

The leader score is a weighted combination: leader = 0.45·initiator + 0.35·hub + 0.12·deference + 0.08·warned-about. The weights are chosen so that a hub who also initiates (the "Paul" pattern from the data) ranks above a pure relay.

## Exchange 3

**Question (to expert):** "Which of these give it away most: who starts the covert talks, who hides them, or who connects the whole group?"

**Expert reply:** Hub/bridge position gives it away most — the person connecting otherwise separate members is hardest to explain innocently. Initiating covert talks is next (strong leader signal). Hiding them (secrecy language) is weakest alone, since innocent staff also gossip and cover for colleagues; it matters mainly when paired with the other two.

**How the reply affected the work (concrete):**
This sets the **relative weights** of the three red-flag families in the composite node likelihood score. Final weights used in the model (normalized to sum to 1 over the three families):

| Signal family | Weight | Justification from reply |
|---|---|---|
| Hub/bridge position (connectivity in suspicious subgraph) | 0.50 | "gives it away most — hardest to explain innocently" |
| Initiating covert talks (suspicious-topic initiator share) | 0.30 | "next (strong leader signal)" |
| Hiding them (secrecy signal) | 0.20 | "weakest alone… matters mainly when paired with the other two" — hence a lower weight and a *pairing bonus* applied only when a node also scores above median on hub or initiator |

The "matters mainly when paired" clause is implemented as: the secrecy component is multiplied by (1 + 0.5·[hub > median]) + (1 + 0.5·[initiator > median]), so secrecy alone is discounted but secrecy combined with hub or initiator is amplified.

## Summary of model parameters set by the expert

| Parameter | Value | Source (exchange) |
|---|---|---|
| Weights: hub / initiator / secrecy in composite likelihood | 0.50 / 0.30 / 0.20 | Exchange 3 |
| Secrecy pairing amplification factor | +50% per family above median, when paired | Exchange 3 |
| Leader-score weights: initiator / hub / deference / warned-about | 0.45 / 0.35 / 0.12 / 0.08 | Exchange 2 |
| Which signal families to score (covert topic, secrecy, tight subgroup, stress) | all four | Exchange 1 |
| Suspicious topics (from data, not expert) | {7, 11, 13}; Requirement 2 adds {1} | Problem statement / dataset |

These are the *only* empirical / judgment-based numbers in the model that cannot be derived from the dataset alone. Every other number (topic counts, degrees, centralities) is computed directly from `Messages.csv`, `Names.csv`, `Topics.csv`.
