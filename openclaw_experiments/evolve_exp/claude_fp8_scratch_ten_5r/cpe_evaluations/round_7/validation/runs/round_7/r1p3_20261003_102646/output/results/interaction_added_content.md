# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction evidence — MM-Bench 2012_C

Ten exchanges, one question each, strictly sequential (structural anchoring →
parameter calibration → boundary definition). Files: `logs/operator_feedback/
expert_question_N.md`, `expert_reply_N.json`.

| # | Question (gist) | Reply (value/constraint) | Where it entered the work |
|---|---|---|---|
| 1 | Who would a small risky group naturally recruit? | Trusted, frequent, two-way contacts of the already-implicated; people who discuss the suspicious topics with them; bridges between clusters; small circle | Structure of the whole model: score built from (a) known-conspirator contact K, (b) suspicious-topic participation T, (c) bridge position B — the three recruit profiles |
| 2 | One message with a guilty coworker vs ten ordinary messages? | Much more revealing — but only if it carries a suspicious topic or is repeated; a lone trivial message with a conspirator is weak | K component design: `sp_ij` flag — suspicious-topic contact counts full, ordinary contact down-weighted ×0.4; repetition required for ordinary contact to count |
| 3 | How many separate messages with one confirmed conspirator start to feel suspicious? | 1–2 weak; 3–5 start of a sustained relationship; >5 or any suspicious-topic clearly suspicious | Normalization constant tau=3 in K(i)=Σ(N_ij/3)^0.7·f; the /3 places the "sustained relationship" boundary at the expert's 3–5 |
| 4 | Organizer: central hub or quiet bridge? | Bridge in the overall network, hub within the conspirator subgroup; not the loudest office hub | B component = 0.5·betweenness + 0.5·degree-to-known-conspirators; hub-in-subgroup term (degC) added explicitly; office-wide hubness deliberately not rewarded |
| 5 | Suspect the people a known innocent avoids? | No — general low profile is uninformative; only selective avoidance of already-suspicious people is a mild secondary signal | No avoidance term in the score (would be noise per expert); noted in limitations as a deliberately excluded weak signal |
| 6 | Would a senior manager personally handle a risky scheme? | Less likely to execute; directs/delegates; signature = indirect ties to a mid-level bridge, weaker and easier to miss | Manager analysis uses score + betweenness + degC jointly, not raw traffic volume; frames the Dolores/Jerome/Gretchen assessment; motivates treating mid-list bridge managers as candidates rather than clearing them on low volume |
| 7 | What topics surround risky contact? | Mundane deniable topics as cover; signal = co-occurrence/adjacency of ordinary and suspicious topics between the same pair | A (cover-traffic adjacency) component: non-suspicious messages of i to nodes carrying suspicious traffic; stated in Req 3 as the per-pair chi-square extension |
| 8 | What does an investigation check first? | The contact set of the known wrongdoers, ranked by frequency, reciprocity, topic; then shared associates, then sensitive topics; untied people set aside | K is the second-largest weight (0.30) after T (0.35); model starts scoring from C's neighborhood; people with no tie to C score near zero (verified: Tran, Gard bottom) |
| 9 | Clear-cut guilty vs borderline employee? | Guilty = multiple independent converging signals (no single innocent reading); borderline = one ambiguous signal; difference is redundancy, not link strength | Redundancy multiplier (1+0.25·(m−1)) for m ≥ 2 active components; single-signal nodes stay mid-list (surveillance tier), not top tier |
| 10 | How many people actually get closely watched? | 10–20 for a case of this size; top ~10–15 unidentified candidates plus a short passive tier; list capped by surveillance capacity | Watch list set to 15 unidentified (within 10–20); secondary passive tier defined as 0.10–0.19 band; Req 4 generalizes the same capacity logic to biopsies in the biological-network example |

## How replies were turned into work
- Exchanges 1–4 fixed the model structure (which signals exist and their
  ordering) before any weight was chosen — no parameter was asked for before
  the mechanism it quantifies was confirmed.
- Exchanges 2–3 produced the numeric constants in K (tau=3, exponent 0.7,
  down-weight 0.4); `code/model.py` takes all weights on the command line and
  `--sweep w_t=0.2,0.35,0.5` was run (logs/sweep_wt.log): top-15 watch list
  retains 15/15, 12/15, 10/15 respectively — stability checked.
- Exchange 10 fixed the output size (15 active + passive tier) and the two-tier
  categorization (active / passive / cleared) reported in the submission.
- No reply text was copied into solution.json; only the values, constraints and
  decision rules above were integrated, in the model's own formulation.

## Model runs
- `logs/explore_data.log` — data cleaning (135 blank rows dropped; 400 valid
  messages; 2 self-loops; 20 repeated pairs kept; duplicate names flagged;
  one topic-18 artifact noted).
- `logs/model_s1.log` — scenario 1 full ranking, watch list, managers.
- `logs/model_s2.log` — scenario 2 (topic 1 added to suspicious set, Chris
  moved to known conspirators).
- `logs/check_bc.log` — betweenness validation (max 1719, Franklin; graph
  connected, 83 nodes).
- `logs/check_sep.log` — ground-truth separation check on unforced scores
  (conspirators min 0.499; non-conspirators max 0.349).
- `logs/verify_top.log` — per-candidate suspicious-topic counts supporting the
  top-15 list.
