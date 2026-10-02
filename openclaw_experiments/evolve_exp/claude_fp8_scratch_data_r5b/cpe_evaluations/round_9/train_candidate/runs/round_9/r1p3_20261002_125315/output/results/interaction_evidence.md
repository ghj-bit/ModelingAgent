# Expert Interaction Evidence — MM-Bench 2023_C (Wordle)

Three exchanges were held, one question each, in sequence. Files: `logs/operator_feedback/expert_question_N.md`, `expert_request_N.json`, `expert_reply_N.json`.

## Exchange 1 — structural validity of the count model

**Question:** Are the daily reported-result totals basically independent of surrounding days, or does the game's popularity move in waves that make nearby days depend on each other?

**Reply (summary):** Nearby days are not independent. The totals show (a) a broad upward trend through 2022 after the NYT acquisition, (b) day-of-week effects, and (c) short-term persistence — a viral spike or a hard/easy word carries over several days. A trend + weekly-seasonality + autocorrelated-error model is appropriate; an independent-per-day model would understate uncertainty.

**How it changed the work (concretely):**
- Model A (`code/model.py`, `model_A`) was specified as log N = intercept + linear year-fraction trend + six day-of-week dummies + AR(1) error, exactly the structure the reply endorsed.
- The AR(1) coefficient was estimated from data (phi = 0.7845) and the 60-day prediction interval for 2023-03-01 uses the AR(1) h-step forecast variance sigma^2(1-phi^2h)/(1-phi^2) rather than the independent-draw variance; this is what widens the interval to [5,126, 16,488].
- The reply's "wave-like" claim was checked against the data: raw ACF of ln N is 0.997 at lag 1, 0.981 at lag 7; after trend+weekly removal the residual ACF stays at 0.77-0.78 over lags 1-5, confirming persistence beyond what the trend explains. Recorded in task 1's outcome analysis.

## Exchange 2 — dominant bias mechanism and validation design

**Question:** Who tends to report scores on Twitter, and does that habit differ for hard words versus easy words?

**Reply (summary):** The reporting population is self-selected toward engaged, competitive players; casual solvers rarely post. The habit interacts with difficulty: on easy words the marginal sharer is less motivated, on hard/high-failure days posting becomes a signal, so the reporting share of solvers rises with difficulty. The reported distribution is therefore biased toward better players and the bias itself varies with word difficulty — a real confounder for any difficulty model built on these percentages.

**How it changed the work (concretely):**
- Task 3 (EERIE distribution prediction) states its scope as the distribution among reporters, not all players, and lists the difficulty-dependent selection as the dominant structural bias; the confidence statement is explicitly downgraded for the X bucket because the bias is strongest precisely where the estimate is smallest.
- Task 4 (difficulty classifier) carries the same caveat: the target variable (mean tries among reporters) is itself a self-selected, difficulty-dependent sample, which is named as one of the three reasons CV accuracy is only moderate (RMSE 0.347 tries, 3-class accuracy 53.5%).
- Validation design consequence: because the 2022 series is non-stationary (trend + adoption ramp), plain random CV would overstate skill; Model B therefore adds a temporal holdout (fit on first 309 days, test on last 50) alongside 5-fold CV, and Model A a 30-day walk-forward backtest. Both are reported in the solution.
- The reply's mechanism (reporting share rises with difficulty) is directionally consistent with the data: the hardest word (PARER, 48% X) has N = 2,569, the smallest count in the file, i.e. hard days have fewer and differently selected reporters. This is noted qualitatively, not as a fitted parameter.

## Exchange 3 — decision-relevant uncertainty threshold

**Question:** Roughly how far off could a difficulty estimate be before you would stop trusting it for comparing words?

**Reply (summary):** Do not trust differences smaller than about 3-5 percentage points of solve rate (equivalently about 0.1-0.2 tries); differences below that band are within rounding, self-selection bias and day-to-day sample noise. Differences of 8-10+ percentage points are robust. EERIE, a double-letter word likely on the harder end, is trustworthy only if it sits well outside that band from its neighbors. This is an empirical judgment, not a precise figure.

**How it changed the work (concretely):**
- Task 4's EERIE verdict is framed by this band: predicted difficulty 3.93 tries vs the easy/medium boundary 3.998 tries — a gap of 0.07 tries, inside the 0.1-0.2-try trust band. The reported classification is therefore "easy class, but boundary-adjacent and not certifiable as easy," with the model's 80th-percentile error (0.45 tries) quoted as the statistical counterpart of the expert band.
- The band is used as a decision rule, not just a comment: any word whose prediction lies within 0.2 tries of a quantile boundary is reported as boundary-adjacent rather than confidently labeled. (EERIE is the only word the problem asks about, and it triggers this rule.)
- The band is also why the solution distinguishes "shape" predictions (high confidence, far outside the band) from individual bucket levels (moderate) in task 3.
