# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — MM-Bench 2012_C

Policy: structural anchoring before numerical filling. 10 exchanges, one
qualitative question each, each building on the previous reply. Every reply is
converted into a parameter, constraint, equation, or decision rule used in
`code/model.py`; nothing below is copied verbatim into `solution.json`.

| # | Branch | Question (short) | Reply (gist) | What it became in the model |
|---|--------|------------------|--------------|-----------------------------|
| 1 | Mechanism | Do plotters message each other or outsiders? | Mainly each other; covert plotting is denser and more reciprocal within the group. Signal strongest in suspicious-topic messages, not total traffic. | **Dominant mechanism fixed**: model on the suspicious-topic directed sub-graph, looking for dense/recursive within-group structure. Total volume is not the evidence. |
| 2 | Constraint | What else makes two workers message a lot — does it make them chatty on suspicious topics? | Routine collaboration (projects, floor, reporting lines) drives most traffic and does NOT make a pair chatty on suspicious topics, except when a legit tie is used as cover. | **Constraint fixed**: ordinary traffic = background/baseline layer only; suspicious-topic traffic is the discriminator. Ordinary layer used to normalize how chatty a pair is, not as evidence. |
| 3 | Parameter | Do the 12 non-suspicious topics carry plotting clues? | Mostly ordinary chatter; useful as pattern/baseline, and some "ordinary" topics can be mislabeled/dual-use (EZ: budget topic was entangled). | Weights: suspicious topics weighted heavily, ordinary topics = background. Boundary of {7,11,13} treated as not perfectly clean (Req 3 discussion). |
| 4 | Parameter | Roughly how many of the 83 are in on it? | A small handful, ~10–20 (10–25%), deliberately small to avoid exposure. Expect a clearly separated top tier. | Threshold/interpretation: look for a clearly separated top tier; ~12-node top tier in base run is consistent. Informs cutoff (S≥0.30 ≈ 12 nodes). |
| 5 | Edge case | A clean person heavy on suspicious topics — in on it or the target? | Usually the target/subject/gatekeeper, not a member. Distinguishing feature: a conspirator initiates AND receives (reciprocal within group); a clean target mostly appears as the *object*. | **Decision rule**: membership judged by who they exchange suspicious traffic with (embeddedness) and reciprocity, not raw suspicious-topic volume. Added `init_ratio = I/(I+A)` term to penalize pure recipients (targets). |
| 6 | Parameter | Of topics 7/11/13, which is closest to the actual crime? | Topic 11 (credit-card system flaws) is the operational core/mechanism; 7 (secret meeting) and 13 (knock-offline) are secondary instrumental support. | Topic weights: w11=1.0 > w13=0.8 > w7=0.6. |
| 7 | Edge case | Must each pair message each other back a lot? | No — reciprocity is a confidence booster, not a gate. Membership judged by connection to the cluster as a whole; a coordinator talks to several members who may not message each other. A receive-only member is weak evidence (target). | Membership = cluster embeddedness (degree in suspicious layer) + seed proximity (handles coordinator→members who don't link directly). Reciprocity kept as a *boost* term, not a gate. |
| 8 | Parameter | Are the 7 known plotters assumed guilty or re-checked? | Fixed positive seeds (ground truth); use to propagate to suspicious-topic neighbors and calibrate the pattern, but don't let them dominate (bare adjacency is weak). | 7 known conspirators = fixed positive seeds, pinned top, seed-proximity diffusion to neighbors (2-hop, decayed), not re-litigated. |
| 9 | Parameter | How to spot the leader vs. foot-soldiers? | Leader = hub in suspicious-topic network: high degree + betweenness, brokers across subgroups, initiates coordination, asymmetric (sends directives), often lower raw volume. Check who the top hub defers to. | Leader score L = 0.5*(betweenness) + 0.3*(out−in balance) + 0.2*(embeddedness). Nominate top-L candidates. |
| 10 | Edge case | The 8 confirmed-clean: pull out or keep in? | Keep in the model as fixed negative seeds to calibrate the clean pattern and validate, but remove from the candidate pool / priority list and from propagation. | 8 known non-conspirators = fixed negative seeds: excluded from the candidate pool, used as a false-positive validation check (none ranked high). |

## Validation of the seed handling (per Exch 8 & 10)
- 7 positive seeds pinned to ranks 1–7 (ground truth), consistent with "assume
  guilty, don't dominate."
- 8 negative seeds (Chris 0, Paige 2, Darlene 48, Tran 64, Jia 65, Ellin 68,
  Gard 74, Este 78) are **absent from the candidate pool** (75 candidates, not 83),
  exactly as instructed. No known-clean person is ranked as a suspect.
- Known-clean **Paige (2)** and **Ellin (68)** are the named *targets* of topic 13
  (knock-offline) in `Topics.csv` — consistent with Exch 5 (clean heavy-on-topic =
  target/object of the plot), and correctly excluded rather than flagged.
