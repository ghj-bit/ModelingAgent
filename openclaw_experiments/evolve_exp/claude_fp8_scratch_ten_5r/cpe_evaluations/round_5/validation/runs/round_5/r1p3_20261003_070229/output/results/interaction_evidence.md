# Interaction Evidence — MM-Bench 2012_C

All exchanges targeted structural/behavioral ambiguity about how conspirators
actually behave in message traffic, following the structural-validity-first policy.
Each reply is turned into a named constraint of the model (see code/model.py and
solution.json parameter table, source = exchange N).

## Exchange 1
**Q:** Do crime-ring members talk secretly about the scheme, or only exchange
ordinary work messages?
**Reply (gist):** Neither extreme: coordination happens but is disguised inside
ordinary channels; the detectable signal is structural (who talks to whom,
reciprocally, on the few scheme topics), not lexical.
**Effect on work:** Defined the whole model class: no text-content features are
available, so the model is a pure structural network model with topic-conditioned
edges. Suspicious topics (7,11,13) are the only "scheme" channels; all views are
computed on the topic-7/11/13 subnetwork.

## Exchange 2
**Q:** Do executives usually take part directly in schemes, or let lower-level
employees do the work?
**Reply (gist):** Execution is by lower/mid-level staff; executives, if involved,
are enablers/beneficiars with small traffic footprint, detectable by position
(low activity, high betweenness / common contact of clusters), not volume.
**Effect on work:** Justifies view V5 (Brandes betweenness on the suspicious
subnetwork) as the executive indicator and justifies down-weighting raw traffic
(V1, weight 0.3 instead of 1.0) so that low-activity positional players are not
buried by chatters. Directly answers the Jerome/Dolores/Gretchen sub-question
using position, not volume.

## Exchange 3
**Q:** Do members of a secret planning group only keep in touch with the same
handful, or does the talk spread to many employees?
**Reply (gist):** Tight, stable inner core for the scheme, but each member keeps
broad ordinary contacts; the signal is concentration: a small shared partner
subset carries the disproportionate sensitive/reciprocal traffic, and the subsets
overlap heavily across core members.
**Effect on work:** Motivated V3 (share of a node's suspicious partners that are
known-guilty) and V3b (max pairwise Jaccard overlap of suspicious partner sets
with any known-guilty member) — the shared-circle test, weight 1.0 + 0.7.

## Exchange 4
**Q:** Does innocent gossip about a suspected scheme spread widely, or stay in a
small circle?
**Reply (gist):** Broad but shallow: one-off, scattered, rarely returned;
clustered *around* the conspirators as a topic, not among themselves.
**Effect on work:** Justifies V2 (reciprocity: per partner pair
min(A_ij,A_ji)/(A_ij+A_ji) on suspicious topics), which scores 0 for one-way
gossip ties and rewards mutual exchange; separates gossipers from core.

## Exchange 5
**Q:** If finance/card-system files get skimmed: few insiders who run the
systems, or an outside gang?
**Reply (gist):** Insiders with system access are the necessary ingredient;
outsiders are downstream; the enabling insiders are few, technically positioned,
low-profile in traffic.
**Effect on work:** Reinforces V1 down-weighting (0.3) and the low-activity-
suspect profile; also motivates reporting which known topics (1,5,15) are
"adjacent/cover" (finance, security) rather than treating every topic equally.

## Exchange 6
**Q:** Do ring members keep ranks obvious in daily messages, or talk casually as
equals?
**Reply (gist):** Casual surface, but hierarchy shows as directed asymmetry:
leaders are the ones others seek out, whose messages get replies, who set timing.
**Effect on work:** Motivated V4 (net out−in suspicious-topic flow toward the
known core), weight 0.5, as the leadership/asymmetry indicator.

## Exchange 7
**Q:** Do recruited members keep talking to old friends, or drift apart?
**Reply (gist):** Old ties persist; what shifts is the allocation of
sensitive-topic/reciprocal communication toward the new core; drift is slow.
**Effect on work:** Confirms that total-degree isolation is NOT a signal;
supports scoring by concentration (V3/V3b) and reciprocity (V2) rather than by
loss of old links; the model therefore uses no isolation/degree-drop feature.

## Exchange 8
**Q:** Do conspirators act nervous/avoidant toward their boss?
**Reply (gist):** No — they work harder to look routine; behavior toward the
boss stays normal; the shift is in who else they talk to and on which topics.
**Effect on work:** Justifies not using supervisor-contact features; the
executive assessment for Jerome/Dolores/Gretchen relies on betweenness (V5) and
core overlap (V3), not on contact patterns with the executives themselves.

## Exchange 9
**Q:** When a plan partly falls through, do remaining members scatter or
regroup?
**Reply (gist):** Regroup; contact is maintained, briefly intensified after a
setback; scattering is the exception.
**Effect on work:** Informs the limitations section: a single time slice of
traffic is sufficient for a snapshot ranking, but longitudinal re-runs would
detect the post-setback intensification; the priority list is a snapshot, not
a dynamic state.

## Exchange 10
**Q:** Do the people who skim money talk constantly with the planners, or only
on rare important occasions?
**Reply (gist):** Episodic, low-frequency but stable, sensitive-topic links;
ranking by volume alone would miss them.
**Effect on work:** Final confirmation of V1 down-weighting (0.3) and of
retaining V3/V3b (stable core-adjacency) and V2 (reciprocity of the few
sensitive exchanges) as the dominant views; a peripheral skimmer connected to
the core on topics 7/11/13 still ranks via V3/V3b despite low total volume.

## Parameters taken from the dataset (not from exchanges)
- Suspicious topic set {7,11,13}: problem statement (three deemed suspicious).
- Known guilty {Jean, Alex, Elsie, Paul, Ulf, Yao, Harvey}; known innocent
  {Darlene, Tran, Jia, Ellin, Gard, Chris, Paige, Este}: problem statement.
- Adjacent/cover topic set {1,5,15} (company finances; database security
  complaints naming Paige/Chris/Este; security-training policy set by Paige and
  Chris): Topics.csv descriptions.

## Data cleaning performed
- 135 message rows with blank start/end nodes dropped (535→400 valid links).
- One link carried topic code 18 (not in Topics.csv, 1..15); retained but
  weighted as non-suspicious (0.2).
- 5 duplicated names (Elsie 7/37, Jerome 16/34, Gretchen 4/32, Beth 14/38,
  Neal 17/31): the known-set/executive names were matched to the duplicate with
  the higher suspicious-core connectivity (Elsie=7, Jerome=34, Gretchen=4,
  Beth=38, Neal=17); all models are computed on node indices, and the
  duplicate pairs never talk to each other on any topic, so the choice only
  affects the name label, not any score.
- Multi-topic links (up to 3 topics per message) each counted for their topic.
