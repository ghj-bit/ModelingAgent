# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence

Three exchanges were held, one question each, in order. Files: `logs/operator_feedback/expert_question_N.md` and `expert_reply_N.json`.

## Exchange 1 — structural fit

**Question:** The seven percentages (1–6 tries, X) for each day sum to 100%. What single rule must the model never break, and what kind of guess could produce impossible numbers?

**Reply (summary):** The seven values must be a valid probability distribution — non-negative and summing to exactly 100% — because each player falls into exactly one of the seven mutually exclusive, exhaustive outcomes. An unconstrained regression or per-category model that can go negative or drift off 100% produces physically impossible outputs.

**How it changed the work:** The outcome model (subproblem 2) was built as a softmax (multinomial) regression, so non-negativity and sum-to-100 hold by construction for every prediction, including the EERIE forecast. The raw data columns (which summed to 98–126 due to source rounding) were clipped to [0,100] and renormalized to sum to exactly 100 before any modeling. The hard-mode model was likewise specified as a binomial GLM (a proportion bounded in [0,1]) rather than an unconstrained regression.

## Exchange 2 — dominant bias mechanism

**Question:** The data come only from people who post scores on Twitter. Who is overrepresented, and in which direction does that skew the picture?

**Reply (summary):** Posters skew toward committed, engaged players (daily play, low try counts, more Hard Mode); casual players who fail or quit under-post. The reported distribution therefore looks easier than the true player population: higher 1–3 try shares, lower X (failure) share, more Hard Mode. The data overstate skill and understate difficulty.

**How it changed the work:** The prediction in subproblem 2 is explicitly scoped to the Twitter-reporting population, with the scope stated as a first-order uncertainty rather than a footnote. The subproblem-2 outcome analysis includes an explicit bias statement that the all-player distribution would show higher X and lower 1–3 try shares. The subproblem-1 hard-mode result (word effects real but R²≈0.03) is interpreted against this background: word choice is a weak lever on hard-mode participation.

## Exchange 3 — validation / interpretation criterion

**Question:** Since the data are from engaged Twitter players only, when should a prediction about this same player group be treated as reliable, and when should it be discounted for being stretched to non-posters?

**Reply (summary):** Reliable when the target is the same self-selected reporting population on comparable days (same era, similar participation and difficulty) — then the model is interpolating over a well-sampled population. Discount it for the broader player base, with the largest discount on the X and 1–3 try shares, where posting bias bites hardest.

**How it changed the work:** The confidence statement in subproblem 2 is structured around this criterion: the EERIE prediction is presented as trustworthy for the reporting population (interpolation within the 2022 era), with a three-part caveat list — population scope, bootstrap tail uncertainty (wide for 1-try and X), and the weak word-feature signal (60-day holdout MAE 0.0347 vs 0.0383 for the null). The subproblem-1 prediction interval for March 1, 2023 is interpreted as an order-of-magnitude band, consistent with the "comparable days" condition being only partially met (one year of extrapolation).
