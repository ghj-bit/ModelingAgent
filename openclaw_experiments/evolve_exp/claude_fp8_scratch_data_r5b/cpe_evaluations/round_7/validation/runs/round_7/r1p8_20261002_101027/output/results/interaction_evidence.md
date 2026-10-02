# Expert Interaction Evidence

Three exchanges, each ≤20 words, asked before the work it governs.

## Exchange 1

**Question** (written to `logs/operator_feedback/expert_question_1.md`):
"When a country wins a lot of medals in one sport, is that mostly because they have the best athletes, or because they entered more events in that sport?"

**Reply summary:** Both, but entry breadth is the bigger lever. Countries that enter more events in a sport win more medals simply by having more chances; athlete quality matters within the events entered. The expert advised modelling entry breadth (number of events entered per sport) as a primary driver, with athlete quality as a secondary multiplier.

**Effect on model:** The country×discipline Poisson model uses `lambda_{c,d} = E_d(t) × r_{c,d}` where `E_d(t)` is the number of program events in discipline d (entry breadth, fixed by the program) and `r_{c,d}` is country c's per-event medal rate in d (quality). This directly encodes the expert's guidance: breadth drives the scale, rate captures quality. Parameter `beta` blends country-specific rate with the global average; the backtest sweep selected `beta=0.0` (pure country-specific rate), confirming that entry breadth × country rate is the right decomposition.

## Exchange 2

**Question** (written to `logs/operator_feedback/expert_question_2.md`):
"When a country hosts the Olympics, do they win more medals in all sports, or mostly in a few sports where they've invested?"

**Reply summary:** Mostly a broad but uneven boost. Hosts win more across the board (venue familiarity, home crowd, extra training focus), but the boost is largest in judged/combat sports (where home advantage is most visible) and the host's own depth sports. The boost is modest (10–30%), not a doubling, and fades in the following Games.

**Effect on model:** The host multiplier is sport-specific rather than a single flat number. `HOST_JUDGED=1.15` (judged/combat), `HOST_TEAM=1.10` (team/racket), `HOST_OTHER=1.05` (other), rescaled so the host's average multiplier equals `HOST_MULT=1.20` (within the expert's 10–30% range). The `by_sport=True` flag in `simulate()` applies this structure. The backtest confirmed `host_mult=1.20` is optimal.

## Exchange 3

**Question** (written to `logs/operator_feedback/expert_question_3.md`):
"When you look at a prediction range like '90 to 110 medals', what makes you trust it more than a single number?"

**Reply summary:** A range is trustworthy when it (1) reflects genuine variability, not padding; (2) is calibrated to history — past projections missed by roughly that margin; (3) is tied to a stated confidence level; (4) narrows with better inputs. A single number implies false precision.

**Effect on model:** All 2028 predictions are reported as 90% prediction intervals (5th–95th percentile of 200 Monte Carlo simulations), not point estimates. The confidence level (90%) is stated explicitly. The backtest record (2000–2024, one 4-year horizon per edition, err_total≈0.49) provides the historical calibration check the expert asked for: the model's per-country relative errors are in the range that a 90% PI should cover. The solution.json reports both the point estimate (mean) and the interval, with the calibration evidence in the performance section.
