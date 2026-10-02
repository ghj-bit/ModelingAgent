# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — MM-Bench 2023_C (Wordle)

Three expert exchanges were run. Each question was written to `logs/operator_feedback/expert_question_N.md`, the command `code/wait_for_expert_reply.py` run in the foreground, and the reply recorded to `logs/operator_feedback/expert_reply_N.json`. The reply is input, not content: what travels into the model is a value / constraint / equation, in my own formulation. No expert sentence is reproduced in solution.json.

## Exchange 1 — Operational definition of the reported-results count
**Question (expert_question_1.md):** "Does the number of reported Wordle results on a day reflect the total number of players, or only the people who chose to tweet their score? If only some players report, roughly who skips reporting on a given day?"
**Reply (summary):** Only the people who chose to tweet are counted. The file is a self-selected, Twitter-mined sample, not the full player base. Skippers are (a) the large majority of casual players who never post, (b) players who failed (X), since losing is less shareable, (c) 1-try / 6-try tails (under-reported relative to the 2–4 "brag" range), (d) hard-mode players (a minority whose reporting behaviour may differ), and (e) day-to-day variation from external factors (weekday, news cycle, word interest). The report fraction is not constant across days or outcomes.
**How it changed the work:**
- Constraint adopted: the count modelled is a *reported-results* process, explicitly a self-selected subset, not "number of players". I never relabel `Number of reported results` as player population.
- The volume model (Q1) is framed as modelling the Twitter-reporting process, and its prediction interval for Mar 1 2023 is stated as an interval on reported results, not on true daily players.
- A model-uncertainty/limitation item was added: the count can move for reasons unrelated to the word (reporting appetite), which is why the volume model includes a time/weekday structure and a wide, asymmetric (log-normal) interval rather than a tight one.

## Exchange 2 — Bias of the posted outcome percentages
**Question (expert_question_2.md):** "If the posted percentages only come from the players who tweeted, do they still represent the typical player's outcome for that word, or are they skewed toward brag-worthy scores?"
**Reply (summary):** Skewed. The percentages are conditional on having tweeted, and the tweet decision is not outcome-neutral: 2–4 tries are over-represented; X, 1-try and 6-try are under-represented. The direction is fairly consistent (toward mid-range wins, away from losses) but the magnitude varies with word difficulty and day — harder words likely have a larger failure under-reporting gap. The distribution is directionally informative about relative difficulty but is not the true population distribution.
**How it changed the work:**
- Constraint adopted: every predicted outcome distribution is labelled "share among *reporting* players", and I do not present it as the true outcome distribution of all players.
- The Q3 prediction for EERIE is interpreted as a ranking/relative-difficulty signal (most mass in the 5–6 try and X region → hard), not as exact population percentages.
- A limitation/bias item was added to Q3 and Q4: the X (failure) tail is the most under-reported, so predicted X for a hard word is a lower bound on the true population failure rate; the whole distribution is shifted toward the middle.
- This reinforced the choice of X_pct as the primary *relative* difficulty signal while flagging its absolute value as biased-low for hard words.

## Exchange 3 — Robustness threshold for a prediction
**Question (expert_question_3.md):** "Given that the posted results under-report failures on hard words, when would a predicted outcome distribution for a new word be trustworthy enough to use, and when should it be treated as too uncertain?"
**Reply (summary):** Trustworthy when the word is easy-to-moderate and the use is relative (ranking, rough central tendency), with a narrow interval and well-represented inputs. Too uncertain when the word is hard or unusual (rare letters, repeated letters, deceptive patterns such as EERIE), when absolute percentages — especially the X and 1-try tails — are needed, or when the word is unlike the training data or the day is unusual. For hard words: trust the direction (harder than average), not the numbers. For easy words: numbers usable within a few points.
**How it changed the work:**
- Decision rule adopted for confidence statements: I report a *confidence tier* per word — "usable for ranking; treat absolute X as a lower bound" for hard/unusual words (EERIE tier), "usable to within a few points" for easy words. This is stated in Q3/Q4 subtask_outcome_analysis.
- EERIE, which the expert named as a deceptive/hard pattern (repeated E, 3 vowels), is explicitly placed in the "trust direction, not numbers" tier, and its X prediction is labelled a lower bound.
- The model's backtest (LOO MAE ≈ 2.2 percentage points on X; 95% prediction-interval coverage ≈ 0.955) is reported as the *within-distribution* calibration, with the caveat that it does not capture the between-word reporting bias of Exchange 2 — so confidence for a new, unlike word (EERIE) is downgraded from what the in-sample coverage alone would suggest.

## Net effect
The three replies converted from prose into: (1) a self-selection constraint on the count variable, (2) a "reporting-players, not population" labelling rule plus an X-tail bias caveat, and (3) a confidence-tier decision rule. None of the expert's sentences appear verbatim in solution.json; only the values, constraints, and decision rules above are integrated.
