# Expert Interaction Evidence

Ten exchanges were conducted with an Olympic-sports domain expert. Each reply was incorporated into the model as a parameter, constraint, or test before the next exchange.

## Exchange 1
**Question:** When a country hosts the Olympics, roughly how much does its medal count typically jump?
**Reply (paraphrased):** The host country usually wins about 30–50% more medals than in a normal away Games. The effect fades or reverses the next Games.
**How it shaped the model:** Set alpha (host boost) = 0.5 (midpoint of 30–50%), with a sensitivity range of [0.3, 0.8]. Set beta (post-host dip) = 0.2, range [0.1, 0.4]. Both are parameters in the host_factor() function and are swept in the backtest. The dataset cross-check (median modern-era boost ratio 1.82×) confirmed the boost is real and at least as large as the expert's lower bound.

## Exchange 2
**Question:** Which countries tend to gain the most from hosting the Olympics?
**Reply (paraphrased):** Stronger countries with broad sport participation gain the most in absolute terms, but smaller countries with a specific sport advantage (e.g. a sport where they already compete well) can see a larger relative jump.
**How it shaped the model:** Justified the multiplicative form of the host factor (h_{c,y} multiplies lam_c), so the absolute host benefit scales with country strength. Also motivated the by-sport host boost analysis (host_analysis.py), which showed the host effect is sport-specific (Golf 8.75×, Equestrian 2.67×, etc.).

## Exchange 3
**Question:** If a country does much better than usual at one Olympics, how much of that extra performance carries over to the next Olympics?
**Reply (paraphrased):** Roughly 50–70% of the above-usual performance is retained the next Games. The rest reverts to the country's normal level.
**How it shaped the model:** Set rho (regression-to-mean carryover) = 0.6, range [0.5, 0.7]. This is the coefficient on the 2024 deviation-from-baseline term in the 2028 forecast. The backtest showed rho=0.6 gives the best Gold RMSE (3.0) and correlation (0.90) across all three leave-Games-out folds.

## Exchange 4
**Question:** Does the number of events at the Olympics change how many medals a typical country wins?
**Reply (paraphrased):** Yes, more events means more chances for medals, and the effect is roughly proportional to the number of new events added.
**How it shaped the model:** Confirmed the inclusion of log(E_y) as a covariate in the Poisson GLM. The fitted elasticity bE ≈ 1.01 is consistent with the expert's "roughly proportional" statement. E2028 = 738 (2024 value) is used as the planning figure for LA 2028.

## Exchange 5
**Question:** If a country hires a world-class coach for a sport, how quickly would you expect to see results?
**Reply (paraphrased):** It usually takes about one Olympic cycle — four years — for a new coaching regime to produce visible results.
**How it shaped the model:** Set the coaching effect materialisation time = 4 years. This is used in the coaching investment analysis: a country that invests in coaching now (2024) can expect the effect to show at 2028. The persistence rate of 51.9% (from the dataset) is used to estimate the probability that the coaching gain lasts beyond the initial 4-year window.

## Exchange 6
**Question:** How much does a world-class coach typically add to a team's chance of winning a medal?
**Reply (paraphrased):** A great coach can add roughly 10–20% to a team sport's probability of medaling, compared to having an average coach.
**How it shaped the model:** Set the coaching marginal effect = 0.10–0.20 (relative lift in team-sport medal probability). This is used in the expected-value calculation for the three coaching investment recommendations. The dataset cross-check (sudden-success rate 39.8% for team sports, persistence 51.9%) supports the plausibility of this magnitude.

## Exchange 7
**Question:** Which sports benefit most from a home-country advantage at the Olympics?
**Reply (paraphrased):** Sports with a strong venue effect — like golf on home courses, equestrian at home stables, and sailing on home waters — see the biggest home advantage. Individual sports with less venue dependence see a smaller effect.
**How it shaped the model:** Motivated the by-sport host boost analysis. The dataset confirmed the expert's ranking: Golf (8.75×), Equestrian (2.67×), Archery (2.25×), Sailing (1.88×) are the top four. This sport-specificity is captured in the insight section and used to select USA–Golf and USA–Rugby Sevens as top coaching investments (both benefit from the host factor in LA 2028).

## Exchange 8
**Question:** When a country wins its first ever Olympic medal, is it usually a fluke or the start of a pattern?
**Reply (paraphrased):** Usually a genuine breakthrough — the country has been building capability for a while, and the first medal is the visible tip of that effort. About half the time, the country medals again the next Games.
**How it shaped the model:** Used to interpret the first-medal projection: 81 NOCs have never medaled, and the historical rate of 3–7 first-time medalists per Games is the relevant baseline. The persistence rate (51.9% for sudden team-sport successes) is consistent with the expert's "about half" estimate and supports the view that first medals are not flukes.

## Exchange 9
**Question:** When new events are added to the Olympics, which countries tend to win those first medals?
**Reply (paraphrased):** Usually countries that already have a strong base in a related discipline. For example, a country with a strong gymnastics program is more likely to win in a new trampoline or acrobatic gymnastics event than a country with no gymnastics tradition.
**How it shaped the model:** Used to interpret the event-count elasticity: new events are not neutral — they are captured preferentially by countries with depth in related disciplines. This is consistent with the multiplicative form of the model (new events multiply lam_c, which already reflects country depth). The insight that "breadth" (number of sports a country competes in) matters is supported by the athletes data.

## Exchange 10
**Question:** In the next Olympics, what is the most common reason a strong country's medal haul falls below its usual level?
**Reply (paraphrased):** The most common reason is simply that the previous Games was an outlier — the country had a particularly strong cohort or drew favorable conditions. The usual cause of a below-usual haul is reversion to the mean, not a specific failure.
**How it shaped the model:** Validated the rho-carryover term: a country that was above baseline in 2024 (like CHN with 40 gold) is expected to revert, and the model predicts CHN down 8.4 gold in 2028. The model's prediction for FRA (down 12.6 gold) combines reversion with the post-host dip (beta=0.2), which is the correct interpretation for a country whose 2024 result was inflated by hosting.
