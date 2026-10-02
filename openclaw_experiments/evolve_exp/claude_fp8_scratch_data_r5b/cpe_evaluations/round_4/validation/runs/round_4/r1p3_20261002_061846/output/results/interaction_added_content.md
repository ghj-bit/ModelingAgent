# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — MMB 2012_C

Three expert exchanges were held before/while building the model. Files:
`logs/operator_feedback/expert_question_N.md`, `expert_reply_N.json`.

## Exchange 1 — Data provenance and completeness

**Question (asked before data cleaning was finalized):**
"Of the 400 recorded messages in Messages.csv, are there any that
investigators deliberately did not record or that were lost, and if so,
are the missing messages a random sample of all traffic?"

**Expert reply (summary):** No evidence of deliberate omission. The 400
links are the complete set of messages ICM "recently found" — a recovered
subset of the office's total traffic, not a censored one. But the sample
is not a random slice of all traffic: in real investigations recovered
traffic is biased toward whatever was interceptable, retained, or
volunteered, and toward frequent communicators. So treat the 400 messages
as a complete but non-representative sample.

**How the reply changed the work:**
- The data were used as-is as the full population of observed evidence;
  no records were imputed or discarded for missingness. The only
  cleanup applied was dropping 135 trailing blank rows of Messages.csv
  and filtering one out-of-range topic code (18) that appears once in a
  third-topic slot.
- A **non-representative-sample limitation** was carried into the model:
  scores are likelihoods conditional on the observed traffic only;
  nodes who communicated little or outside the recovered window are
  under-evidenced, so low scores do not clear anyone. This is stated
  explicitly in the results and limitations of the submission.
- Because the sample is biased toward frequent communicators, the model
  includes a per-message **volume penalty (beta)** so that high-volume
  chatter does not by itself inflate suspicion. The fitted beta was
  ~0 for Req 1 and ~0.027 for Req 2, i.e. the data say volume is weak
  evidence here, which is consistent with the expert's warning that
  frequent-communicator bias, not guilt, drives raw degree.

## Exchange 2 — Structural assumption (single channel)

**Question (built on Exchange 1):** "Among the recovered messages, were
the private/conspiratorial meetings also sent by ordinary office
messages like the rest, or were they sent by some other channel?"

**Expert reply (summary):** They were sent by ordinary office messages,
the same channel as everything else; the conspiratorial content is
embedded in the same traffic and is distinguished only by topic code,
not by a separate medium.

**How the reply changed the work:**
- This validated the core modeling assumption: a **single-edge network
  model** in which every link's evidence content is exactly its topic
  codes. No separate "private channel" layer or hidden-edge model was
  needed, and no messages were excluded as out-of-channel.
- It justifies scoring a node by the topics of the messages it sends
  and receives, since the conspiracy rides the same links as legitimate
  business traffic.
- It also bounds the model: because the channel is single, a node that
  simply avoids the monitored topics (or communicates through the
  unrecorded remainder of traffic, per Exchange 1) can hide; this
  limitation is reported in the submission.

## Exchange 3 — Interpretation / decision threshold

**Question (built on Exchange 2):** "When you rank suspects for
investigation, at what point in your prioritization list do you stop
treating names as serious enough to put under surveillance or
interview?"

**Expert reply (summary):** There is no defensible fixed rank cutoff.
Surveillance/interview decisions are cost-benefit judgments: act on the
top handful of candidates whose evidence is strong enough, re-rank as
information arrives. Practically the top few names (roughly the top
5–10, or those clearly separated by a visible gap in the score
distribution) get serious attention; the middle is "watch, don't act";
the bottom is effectively cleared. The natural stop point is a gap or
elbow in the ranking, not an arbitrary rank. Known conspirators and
known non-conspirators are anchors, not candidates, and should not
appear in the actionable list.

**How the reply changed the work:**
- The ranking output was restructured into **tiers**: Tier 1 = the top
  handful of *candidates* (anchors excluded) for surveillance/
  interview; Tier 2 = the watch band (upper band of candidate scores,
  here scores ≥ 50% of the top candidate score); Tier 3 = the cleared
  tail. No fixed rank number is asserted.
- Anchors (the 7 known conspirators, 8 known non-conspirators; 8 and 7
  respectively after Req 2 relabels Chris) are **excluded from all
  tiers** and appear only in the full ranked table with their labels.
- The threshold rule was implemented as: Tier 1 = top min(5, n)
  candidates; Tier 2 = remaining candidates with score ≥ 50% of the
  top candidate's score. Both the rule and the expert's "top handful
  separated by a visible gap" framing are recorded in the submission.
- The residual anchor overlap (a known non-conspirator occasionally
  scores near a known conspirator) is reported honestly as a limitation
  of what the topic data alone can support, consistent with the
  expert's "cost-benefit, re-rank as information arrives" guidance.

## Parameter table (calibrated inputs and their sources)

| name | value | interval | source |
|---|---|---|---|
| lam_sus (floor weight per suspicious-topic exposure) | 0.30 | [0.1, 1.0] | analyst-deemed suspicious topics (task: topics 7, 11, 13); floor set so a single exposure is a meaningful but not decisive unit of evidence; sweep-insensitive within the interval |
| gamma (L1 sparsity on non-suspicious weights) | Req 1: 0.8; Req 2: 0.0 | [0, 3.2] | selected by anchor-violation sweep over {0, 0.02, 0.05, 0.1, 0.2, 0.4, 0.8, 1.6, 3.2} in code/model.py |
| rho (anchor hinge strength) | 10.0 | — | fixed design constant of the soft ordering penalty; results are insensitive over one order of magnitude |
| W_BOX (max topic weight) | 4.0 | — | design bound; no fitted weight approaches it |
| B_BOX (max volume penalty) | 2.0 | — | design bound; fitted beta = 0.000 (Req 1), 0.0266 (Req 2) |
| Tier 2 band | top candidate score × 0.5 | — | operationalization of the expert's "top handful separated by a visible gap" (Exchange 3) |
