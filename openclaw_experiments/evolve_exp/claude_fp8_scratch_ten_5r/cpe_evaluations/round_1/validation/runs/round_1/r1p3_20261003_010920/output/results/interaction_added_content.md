# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — MM-Bench 2012_C (Crime Busting Network Model)

Ten exchanges, one question each. Each reply became a calibrated input to the
model; the value/range, the source (exchange), and the interval over which it
holds are recorded below. No reply text is copied into the submission; only the
calibrated value and how it is used.

## Exchange 1 — Who runs a fraud ring?
**Question:** In real embezzlement or fraud rings at companies, are the usual masterminds the senior managers, or lower-level staff?
**Reply (summarized):** Lone embezzlement is usually lower/mid-level (direct custody of funds). Organized fraud conspiracy — the relevant case here — is typically run by mid-level managers and sometimes senior managers (authority to override controls/direct subordinates), with lower-level staff as participants.
**Calibrated input used:** Leader-likelihood prior is elevated for mid-to-senior managers but NOT tied to seniority alone; leaders are expected to span levels, with the organizer more often mid-level. Interval: corporate office settings. Source: exchange 1.
**Where it enters:** `task_analysis` (leader-prior assumption) and the requirement to examine the three senior managers (Jerome, Delores, Gretchen) by structural position rather than rank.

## Exchange 2 — Do masterminds talk to many people?
**Question:** In organized office fraud rings, do the masterminds usually talk to many people, or stay in the background and pass messages through a few intermediaries?
**Reply (summarized):** Masterminds stay in the background, using a few trusted intermediaries. In a message network they show up as **low-degree but high-betweenness** nodes (few direct links, positioned on paths between otherwise separate clusters) — the more common pattern.
**Calibrated input used:** Leader-detection metric = high betweenness (brokerage) with modest degree, NOT raw degree. Interval: organized conspiracies in a message network. Source: exchange 2.
**Where it enters:** `leader_score` weights betweenness (brokerage) as the dominant term and gates it on covert-topic participation; the "insulated organizer" pattern (high betweenness, low degree) is what the leader term rewards. This is why the top leaders (Franklin betweenness=1.0, Sherri 0.74) are brokers, not the highest-degree nodes.

## Exchange 3 — Do key people message more?
**Question:** When a company is planning a scheme, do the key people message each other more, less, or about the same as before the scheme?
**Reply (summarized):** About the same volume, but the *pattern* shifts: more traffic on covert/suspicious topics, tighter reciprocal ties among the core, routing through intermediaries, reduced contact to outsiders. The useful signal is **a change in structure and topic mix, not raw message count**.
**Calibrated input used:** Conspirator-likelihood score down-weights raw degree/volume and up-weights (a) fraction of a node's traffic on suspicious topics (topic mix) and (b) structural centrality (embedding in a well-connected core). Interval: planning phase of an office conspiracy. Source: exchange 3.
**Where it enters:** `score` = struct_weight·susp_frac + eig_weight·eigenvector + clus_weight·clustering; raw degree is deliberately NOT a membership feature (only used in the leader term). Validated by sweep: P@5=0.80 is robust whenever the covert-topic weight dominates.

## Exchange 4 — Are leaders caught first or last?
**Question:** In a fraud ring, are the actual leaders usually among the first few people to be caught, or the last?
**Reply (summarized):** Usually last or never. Leaders are insulated; operational participants surface first and plea-bargain. Detection must target **structural position (betweenness, brokerage, intermediary chains), not raw activity or degree**.
**Calibrated input used:** Confirms the betweenness/brokerage-over-degree design and that the model should distinguish "operational participant" (high covert activity, caught first) from "organizer" (structural broker, caught last). Source: exchange 4.
**Where it enters:** The two-tier output — conspirator-membership score (catches operational participants) vs. leader/broker score (catches organizers) — directly implements this. Limitation noted: a careless or well-witnessed leader can surface early.

## Exchange 5 — Close friends or strangers?
**Question:** Do fraud conspirators usually include a few close friends, or strangers from different departments?
**Reply (summarized):** Mostly people who already know each other — pre-existing trust. Conspirators form **dense, tightly-knit subgroups** (high clustering) within one or a few functional areas, with a small number of bridging ties; not randomly scattered.
**Calibrated input used:** Clustering coefficient is a positive membership feature (dense core). Expect a dense core cluster plus a few bridge nodes. Source: exchange 5.
**Where it enters:** `score` includes clus_weight·clustering; the top-ranked nodes (Ulf clustering 0.38, Yao 0.29, Sherri 0.22) sit in dense subgroups. Bridge nodes (high betweenness) are separately flagged by the leader term.

## Exchange 6 — Hidden or open?
**Question:** Do people involved in a scheme tend to hide the messages, or are they fairly open but unusual in content?
**Reply (summarized):** Fairly open in channel, unusual in content. Conspirators use normal channels (a sudden absence of traffic is itself a red flag); they conceal *meaning*, not existence. The signal is **topic composition and structure**, not channel anomalies. This is exactly why the EZ case and this case flag "suspicious" topics (here 7, 11, 13) that read as innocuous.
**Calibrated input used:** No penalty for open-channel / high-volume traffic; the suspicious-topic set {7,11,13} is the primary content signal. Source: exchange 6.
**Where it enters:** The model weights edges carrying suspicious topics 2× (suspicious_weight over topic_weight) and computes per-node covert-fraction susp_frac as the primary membership signal. No channel-absence or volume-anomaly features are used.

## Exchange 7 — How many conspirators?
**Question:** In white-collar fraud cases, how many actual conspirators are there usually relative to the whole office?
**Reply (summarized):** A small minority — a handful, roughly 5–15 in an office of this size (83), i.e. ~6–18%; rarely more than ~5–10% in real offices, proportion shrinking with org size.
**Calibrated input used:** Expected total conspirators ≈ 5–15 of 83. This calibrates how to read the priority list in tiers and where the discriminate line should sit (flag a small minority as high-priority, not half the office). Source: exchange 7.
**Where it enters:** The discriminate line (top 17 HIGH-priority nodes, ~20% of 83, bracketing the 5–15 true-conspirator expectation with a precision-first top-5) is read as "top handful are the likely conspirators; the rest of the HIGH tier is the investigation fallback." The 7 known conspirators are consistent with a total in the 5–15 range.

## Exchange 8 — Few strong or many mild?
**Question:** When investigators get a priority list, is it better to flag a few people strongly or a larger list mildly?
**Reply (summarized):** A short, sharply ranked list with a clear cutoff (the "discriminate line") — high-precision, actionable. A long mild list wastes scarce surveillance/interrogation resources. The list should concentrate on the strongest signals, hedging across many only as a fallback tier.
**Calibrated input used:** Output form = ranked priority list with a clear cutoff (HIGH vs LOW), high-precision top tier. Source: exchange 8.
**Where it enters:** The `flag` column (score ≥ 1.055 ⇒ HIGH) is the discriminate line; the top handful (Elsie, Ulf, Alex, Marion, Paul) is the primary actionable tier, with a sharp drop into LOW. The leader shortlist is deliberately short (2 brokers) rather than a long mild list.

## Exchange 9 — How do senior managers appear?
**Question:** Do senior managers who help a scheme usually appear in the messages, or stay out of them?
**Reply (summarized):** Usually they appear, but **sparsely and indirectly** — low-volume, low-degree nodes, a few messages to trusted subordinates/peers. Complete absence is itself an anomaly. Two patterns: the insulated organizer (high betweenness, low degree) or the legitimate-cover participant (routine-looking managerial messages carrying coordination). For Jerome, Delores, Gretchen: present but not central by volume; judged by structural position and topic mix, not message count.
**Calibrated input used:** Senior managers are assessed by betweenness + covert-topic mix, NOT by volume/degree; present-but-sparse is the expected shape of an involved manager. Source: exchange 9.
**Where it enters:** The senior-manager readout uses susp_frac and betweenness (not degree). Result: Gretchen (node 4) is HIGH and a leader (betweenness 0.26, susp_frac 0.58); Gretchen (node 32) HIGH (betweenness 0.50); Jerome (16) and Jerome (34) LOW; Delores (10) HIGH in the conspiracy tier (rank 10, susp_frac 0.59) but not a leader-broker. So at least one senior manager (a Gretchen) and possibly Delores are implicated in the conspiracy tier, while the senior-manager *leader* slot is more consistent with the mid-level brokers Franklin/Sherri.

## Exchange 10 — How much does "be discreet" raise suspicion?
**Question:** If a message says "be discreet" or uses coded words, how much should that raise suspicion?
**Reply (summarized):** Modestly — a weak-to-moderate signal, not a strong one, and not sufficient by itself. It is a *content* signal that, in this dataset, only enters through topic coding (the topics already embed it, e.g. Topic 7's "be discreet" reminders). Its real value is as a **modifier** that amplifies other evidence when it co-occurs with suspicious topics inside an already-suspicious cluster; isolated, it is noise.
**Calibrated input used:** Discretion-seeking / coded-language cues are treated as a small amplifier, not a standalone flag. Since we only have topic codes (no transcripts), these cues are already absorbed into the suspicious-topic weights and are not added as a separate feature. Source: exchange 10.
**Where it enters:** Requirement 3 discussion (semantic/text analysis) and the note that Topics.xls descriptions were used to justify the suspicious-topic set {7,11,13} (Topic 7 = private meeting with "be discreet" reminders; Topic 11 = flaws in accounting/credit-card/audit systems; Topic 13 = keeping Paige/Ellin/Chris off-line). No separate "coded-language" feature is applied, consistent with its weak-to-moderate, modifier-only status.

## Summary of calibrated parameter table
| Parameter | Value / range | Source | Interval of validity |
|---|---|---|---|
| Suspicious topics | {7, 11, 13} | task statement (Req 1) | this case |
| Leader prior | mid/senior managers, organizer often mid-level | exchange 1 | corporate fraud conspiracy |
| Leader signal | high betweenness, low degree (brokerage) | exchange 2 | organized conspiracy message network |
| Membership signal | covert topic mix + structure, NOT raw volume | exchange 3 | planning phase |
| Leader vs participant | organizer = broker, caught last; participant = high activity, caught first | exchange 4 | fraud ring |
| Core structure | dense tight subgroup + few bridges | exchange 5 | collusive ring |
| Channel pattern | open channel, unusual content; no volume anomaly | exchange 6 | corporate message traffic |
| Expected # conspirators | ~5–15 of 83 (small minority) | exchange 7 | office of ~83 |
| Output form | short sharply-ranked list + clear cutoff | exchange 8 | investigative use |
| Senior-manager pattern | present but sparse; judge by betweenness + topic mix | exchange 9 | senior managers in a scheme |
| "Be discreet"/coded cues | weak-to-moderate amplifier, not standalone | exchange 10 | content signal via topic coding |
| suspicious_weight / topic_weight ratio | 2.0 / 1.0 (swept 1–4, ordering invariant) | model sweep `logs/sweep1.log` | this dataset |
| struct_weight, eig_weight, clus_weight | 1.0, 0.6, 0.4 (swept, P@5=0.80 when struct≥1.0 & eig≤0.6) | model sweep `logs/sweep2.log` | this dataset |
| Leader threshold | 0.90 absolute (short broker shortlist) | exchange 8 + model output | this dataset |
| Membership threshold | 1.055 (top ~17, ~20% of nodes) | exchange 7 + 8, quantile of score | this dataset |
