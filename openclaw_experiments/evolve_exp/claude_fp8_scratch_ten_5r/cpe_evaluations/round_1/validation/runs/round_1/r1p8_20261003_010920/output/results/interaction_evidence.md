# Interaction Evidence

Expert: real-world Olympology common sense. 10 fixed exchanges, one question each, ≤20 words each.
All replies converted into model inputs / decision rules before the next exchange.

## Exchange 1 — 2028 LA program (new / dropped sports)
**Question:** Compared with the 2024 Paris Olympics, which new sports are set to debut at the 2028 Los Angeles Olympics, and which existing sports are expected to be dropped from the program?

**Reply (summary):** 2028 adds five new medal sports — baseball/softball, cricket (T20), flag football, lacrosse (sixes), squash — and drops breaking (a one-off Paris addition); boxing's inclusion was uncertain (not in the initial list). Additions are host-nation-chosen, consistent with IOC practice of letting hosts propose optional sports.

**How it was used (model input, exchange 1):**
- The 2028 event program is an exogenous input, not in the provided data (programs.csv ends at 2024). Built `P_2028` = 2024 program adjusted by:
  - ADD (1 event each, per the IOC announcement the expert paraphrased): Baseball, Softball (1 event each — T20 cricket 1 event, flag football 1 event, lacrosse sixes 1 event, squash 2 events [M/W]).
  - DROP: Breaking (BKG, 2 events in 2024) removed.
  - Boxing: retained (IOC confirmed boxing for LA 2028; expert noted it was only *uncertain* in the initial list — a modeling choice, not an assumption the reply forced).
- This drives the event-based component of every 2028 country projection (sub-problem 5) and the "most likely to improve" list (host-favored sports like flag football, lacrosse, cricket, baseball/softball are US/strong-nation sports → boost the host and a few others).
- Interval of validity: applies to the 2028 Games program specifically.
- Source: exchange 1 (paraphrasing IOC announcements; the provided dataset does not contain 2028 program).

## Exchange 2 — Great-coach effect size (team sports, one Games)
**Question:** In team sports like gymnastics and volleyball, roughly how many extra Olympic medals would you expect a single world-class coach to add for a country in one Games, compared with the same team without them?

**Reply (summary):** Central estimate ~0–1 extra medal per Games, ceiling 0–2; in volleyball the ceiling is 1 (one team event), in gymnastics 1–2 for a small athlete group. Highly conditional: largest when the country is already near the podium; ~0 for a country far from contention. Treat a single-Games estimate as very uncertain.

**How it was used (model parameter + decision rule, exchange 2):**
- Calibrated the "great coach" component: ΔC_coach(sport, country) is applied ONLY if the country is podium-adjacent in that sport (measured: the country has won ≥1 medal in that sport in 2016 or 2024, or is within the top-12 by 2024 sport-medals). Magnitude: +1 medal (central) with a 90% interval [0, 2] for a team event (ceiling 1 → modeled as a Poisson(1) capped at the number of medal events the sport has), and +1.5 (interval [0, 3]) for a multi-event technical sport (gymnastics, diving, rowing crew-type) where a coach spans several athletes.
- This is an upper-bound "what-if" lever for sub-problem 6 (three countries to invest in): it answers "how much could a great coach plausibly add," not a forecast — so the base 2028 forecast does NOT include it.
- Interval of validity: one Games cycle (4 yr), team/technical sports only.
- Source: exchange 2.

## Exchange 3 — First-medal pathway for a small country
**Question:** For a small country trying to win its very first Olympic medal, which individual sports are realistically the best bets, and why are team sports much harder?

**Reply (summary):** Best first-medal bets are individual, multi-event, low-depth sports — weightlifting, wrestling, judo, boxing, taekwondo, shooting, archery, athletics; plus swimming/track and gymnastics (more events but deeper fields). One standout athlete can medal alone; these sports have several weight classes/events = multiple shots. Team sports need 10-20 athletes at international standard simultaneously plus years of infrastructure — a far higher depth threshold. Cites Dominica and Saint Lucia's 2024 athletics golds.

**How it was used (model input, exchange 3):**
- Built the first-medal *probability* for each of the 68 never-medaling 2024 participants as a weighted function of (a) the country's athlete depth in the exchange-3 "low-depth individual" sports (weightlifting, wrestling, judo, boxing, taekwondo, shooting, archery, athletics, swimming, gymnastics) in 2024, and (b) the historical base rate of ~5 new medalist countries per Games (from the dataset, 2000-2024). A country's P(first medal in 2028) = base_rate * (its depth in target sports / median depth in target sports), capped at 0.5.
- This converts the raw count of 68 candidates into a probabilistic projection: expected number of first-time medalists in 2028 = sum of P_c, with a Poisson interval. (Computed in firstmedal.py; result reported in the outcome.)
- Also drives the "which countries are most likely to break through" ranking (sub-problem 4).
- Interval of validity: current (2024) field of never-medaling participants; one Games cycle.
- Source: exchange 3 (mechanism) + dataset (base rate 5.0/games, 2000-2024).

## Exchange 4 — Host effect decomposition (new sports vs general home advantage)
**Question:** When a host country adds sports it is strong in, like baseball or soccer, does that meaningfully boost its own total medal count, or is the home advantage mostly in sports everyone already plays?

**Reply (summary):** New host-chosen sports add a small, targeted bump of ~1-5 extra medals (baseball/softball alone at most ~2 for a dominant host). The bulk of home advantage is a diffuse 10-30% lift across the existing program (preparation, crowd, scheduling, no travel, automatic qualification slots), larger in aggregate than the new-sport additions.

**How it was used (model parameter, exchange 4):**
- Split the host effect into two additive terms in the 2028 forecast:
  (a) diffuse home advantage = the size-dependent absolute bonus already in host_bonus() (data-fit, median ~+24 total for a mid-size host);
  (b) new-sport bonus = +3 total medals (band [1,5]) for the host ONLY, credited to the five sports the US added/kept for 2028 that it is strong in (Baseball&Softball, Flag football, Cricket, Lacrosse, Squash). This is the exchange-4 "1-5 targeted" term, central 3.
- This is added on top of the diffuse bonus for the US only. Net US 2028 total = model baseline + diffuse bonus + new-sport bonus.
- Interval of validity: 2028 host (United States) specifically.
- Source: exchange 4.

## Exchange 5 — Post-host reversion (does the boost linger?)
**Question:** After a country hosts the Olympics and does well, does it usually drop back to normal at the next Games, or does the hosting boost linger for a while?

**Reply (summary):** Mostly drops back — the boost is temporary (auto-qualification, crowd, no travel, one-off program additions all disappear). Reversion is partial, not complete: hosts typically settle a few % to ~10% *above* their pre-host baseline at the next Games because hosting leaves durable infrastructure, funding, coaching, and talent pipeline. Pattern: sharp bump at home Games, substantial fall at next Games, settling slightly above the original level.

**How it was used (model decision rule, exchange 5):**
- For the country that hosted the *most recent* Games (France, 2024) forecasting 2028: the baseline is the **pre-host** level (mean of 2016 and 2020, excluding the 2024 host peak) times a lingering factor of 1.05 (central of the "few % to ~10%" range). This replaces the naive mean(2020,2024) which would over-weight the 2024 peak.
  - France pre-host baseline = mean(2016:38, 2020:33) ≈ 35.5; ×1.05 ≈ 37; the event-scaling then adjusts. (Implemented in forecast_2028 via a `recent_host` override.)
- For countries that hosted 2+ Games ago (China 2008, Japan 2020 for the 2024 baseline), no override — their 3-game mean baseline already reflects the lingering effect.
- This sharpens the "most likely to do worse" list: France's drop is from its 2024 peak, not a structural decline.
- Interval of validity: the single post-host Games (2028 for France).
- Source: exchange 5.

## Exchange 6 — Specialization vs breadth for small nations
**Question:** For a small country with limited Olympic funding, is it more effective to concentrate on one or two sports where it has a talent pool, or to spread athletes across many sports?

**Reply (summary):** Concentrate on one or two sports with an existing talent pool. Medals are won at the top of a deep field; spreading thin leaves every program below the medal threshold. Pick sports with many medal events and low global depth (weightlifting, wrestling, judo, taekwondo, shooting, archery, individual athletics/swimming) so one standout has several shots. Team/deep sports are poor targets.

**How it was used (model parameter + insight, exchange 6):**
- Made the sport-weight shrinkage **size-dependent**: small/specialized nations (recent total < 5 medals/game) get shrink=0.0 (keep their actual concentration — the data shows ~100% of their gold in 1-2 sports), while large diversified nations (>=10 medals/game) get shrink=0.3 (toward the global distribution). This sharpens the model for the tail countries and is the quantitative expression of the "specialize" norm.
- Underpins the original-insight that a country's medal output is set by depth in a narrow sport portfolio, not breadth — and the concrete investment advice (specialize where medal-per-athlete return is highest).
- Interval of validity: current period; one Games cycle.
- Source: exchange 6 (norm) + dataset (top-3-sport share: small nations ~1.0, powerhouses 0.4-0.6).

## Exchange 7 — Trend in first-ever medal winners
**Question:** Over the last few Olympics, is the number of countries winning their first-ever Olympic medal going up, down, or about the same?

**Reply (summary):** Roughly flat to slightly increasing; ~1-3 countries per recent Games (2024's 4 — Albania, Cabo Verde, Dominica, Saint Lucia — unusually high). Mildly upward long-run because more NOCs and more events give small nations more chances, but noisy year-to-year and dependent on whether events are added in low-depth sports.

**How it was used (model parameter, exchange 7):**
- Recalibrated the first-medal base rate from the dataset's 5.0 new-medalist-countries/games (which counts all countries medaling for the first time in the *dataset window*, including mid-size ones) down to **3.0** (central of "a few" per Games, 2024's 4 treated as the high end). This is the expected count of *first-ever* medalists in 2028, scaled across the 68 never-medaling 2024 participants by their low-depth-sport depth. Expected 2028 first-time medalists therefore drops from 6.6 to ~3.4, with a Poisson 90% PI.
- Interval of validity: current field of never-medaling participants; one Games cycle.
- Source: exchange 7 (rate) + dataset (depth weights).

## Exchange 8 — Volatility of strong countries' totals
**Question:** For a consistently strong country like the US or China, how much does its total medal count usually swing from one Olympics to the next — a lot or only a little?

**Reply (summary):** Only a little — top nations' totals are stable (US ~100–130, China ~70–90 recent Games); typical game-to-game variation ±5–15% of the total, driven by host effects, program changes, and a few sports swinging. High stable baseline with modest fluctuations; an empirical regularity.

**How it was used (model parameter, exchange 8):**
- Capped the 90% prediction-interval RELATIVE half-width at 15% for large-μ country totals (and golds): for every 2028 forecast where the NB interval's half-width exceeds 15% of the point estimate, the interval is re-centered and clamped to ±15%. Small-μ countries (where 15% is tiny) keep the data-calibrated NB width, so the cap only binds for the big, stable nations — matching the expert's "±5–15%" regularity. Implemented in model.py `main()` interval block (`rel_cap = 0.15`).
- Interval of validity: medal-rich countries (large μ), one Games cycle.
- Source: exchange 8.

## Exchange 9 — Do first-medal countries keep winning?
**Question:** When a small country wins its first Olympic medal, how often does it keep winning medals at the next Olympics?

**Reply (summary):** Mostly not — first medals are usually one-off or sporadic; only ~1/4 to 1/3 of first-time medalists medal again at the very next Games. Pattern: a single standout athlete medals, then the country returns to zero when that athlete retires. Exceptions: countries pairing the first medal with real investment / a broader low-depth-sport talent pool (e.g. weightlifting, athletics programs) → recurring medals.

**How it was used (model parameter, exchange 9):**
- Added a cohort-retention projection to firstmedal.py: P(follow-up medal at 2032 | first medal at 2028) = 0.30 (central of [0.25, 0.33]). Expected 2032 medalists attributable to the 2028 first-medal cohort = E₂₀₂₈ × (1 + 0.30), with a Poisson 90% PI (fields `expected_medalists_2032_from_2028_cohort`, `pi90_2032_low/high`, `p_followup_medal_2032`).
- Also drives the investment insight: a first medal is not a pipeline — sustained results require program investment, which is the quantitative rationale for sub-problem 6's advice (invest in depth, not just one athlete) and for prioritizing 2028 candidates whose target-sport depth exceeds the median (they are the more likely "exceptions" that recur).
- Interval of validity: one Games cycle (2028 → 2032).
- Source: exchange 9.

## Exchange 10 — Longevity of host-chosen sports
**Question:** When an Olympic host city leaves behind new sports or venues, how long does the country usually keep competing in them?

**Reply (summary):** Only briefly — host-chosen sports (baseball/softball, breaking, etc.) are typically dropped at the next Games, so the host loses the stage almost immediately; where the sport stays, the host's edge fades within ~1–2 cycles as one-off investment and momentum dissipate. Venues are more durable (decades), but they sustain existing permanent-sport programs, not the adoption of a new sport.

**How it was used (decision rule, exchange 10):**
- Investment rule in coach.py: the three sub-problem-6 picks are constrained to sports that REMAIN in the program (all three picks are permanent-sport picks), explicitly not the 2028 one-off additions (cricket, flag football, lacrosse, squash); added `longevity_note` to results/coach_analysis.json stating that host-chosen-sport edge fades within 1–2 cycles, so durable returns come from infrastructure sustaining permanent sports.
- Reinforces the exchange-4 split: the +3 host new-sport bonus is a ONE-GAMES term (it is NOT extended to 2032), while the diffuse home advantage and venue-driven infrastructure effects are the durable terms.
- Interval of validity: 2028 host (United States); one-to-two Games cycles for the fading edge.
- Source: exchange 10.
