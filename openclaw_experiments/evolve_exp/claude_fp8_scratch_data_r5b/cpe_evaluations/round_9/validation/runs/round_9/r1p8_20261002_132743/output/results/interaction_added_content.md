# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence

Three exchanges were held (one question each, asked before the answer was
seen). Each answer was converted into a concrete parameter, constraint, or
code/decision change before the next exchange. No expert prose is reproduced
in the submission; only the resulting values and constraints travel.

## Exchange 1 — Persistence of sport-level strength

- **Question** (`logs/operator_feedback/expert_question_1.md`): does a
  country's strength in a given sport persist across Games, or do
  single-Games results swing like noise?
- **Reply summary** (`logs/operator_feedback/expert_reply_1.json`):
  sport-level national strength is persistent across decades; single-Games
  swings are largely noise.
- **How it changed the work**: the Poisson panel's additive
  country + sport structure was adopted as the core predictor
  (`log lambda = a_c + b_s + g_t + ...`), and per-Games deviations were
  damped rather than extrapolated. This is why the 2028 projection carries
  2024 sport shares forward (plus 2016–2020 recurring strength) instead of
  reacting to any one Games' sport-level result. Holdout validation
  (temporal, 2000–2024) confirms error stays flat across holdout years
  (total-medal RMSE 2.0–2.7), consistent with persistence + noise.

## Exchange 2 — Host-country medal effect

- **Question** (`logs/operator_feedback/expert_question_2.md`): do host
  countries win noticeably more medals, and by roughly how much?
- **Reply summary** (`logs/operator_feedback/expert_reply_2.json`): hosts
  win roughly 20–40% more total medals, partly via newly added or changed
  events; the effect decays after the host Games.
- **How it changed the work**:
  1. A host indicator `H_{c,t}` entered the Poisson model; the fitted
     coefficient is 0.214 (≈ +24% in multiplicative terms), inside the
     stated 20–40% band — used as the 2028 US adjustment.
  2. A post-host decay term `d_p*P_{c,t}` (hosted within the previous 2
     Games) was added, per the "decays after" part of the reply.
  3. The raw empirical host/non-host total ratio (mean 2.01, 90% CI
     [1.32, 2.70], n=8, data `results/projection_summary.json`) was
     **rejected** as the point boost because it is confounded with program
     growth (the data band is wider than the expert's 20–40%); it is kept
     only as a sensitivity/uncertainty reference. The Monte Carlo draws the
     US host multiplier from Normal(exp(0.214), 10%), clipped to [1.15,
     1.45], i.e. the expert-consistent range.

## Exchange 3 — Decision-relevant uncertainty threshold

- **Question** (`logs/operator_feedback/expert_question_3.md`): how many
  medals of uncertainty makes a projection useless for a national
  committee's investment decision?
- **Reply summary** (`logs/operator_feedback/expert_reply_3.json`): ±10–15
  medals is useless; ±3–5 is usable; for large countries relative precision
  is acceptable.
- **How it changed the work**:
  1. The projection table reports 90% prediction intervals per country
     (total and gold), with `interval_width` computed.
  2. A `decision_grade` flag marks rows whose interval width is ≤ 10
     medals as "yes" (the exchange's usability threshold), so committees
     know which of their own projections are actionable; ~8 of 91 countries
     qualify (small, stable ones: Romania, Turkey, Kenya, Norway, Poland,
     Croatia, Ireland, Denmark).
  3. For large countries (top 3 hold ~27% of 2024 medals) the report
     emphasizes relative (rank) uncertainty rather than absolute medal
     counts, per the reply.
