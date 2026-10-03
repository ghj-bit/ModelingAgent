# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence

Ten exchanges, one question each. Each reply was turned into a parameter,
constraint, equation, or decision rule before the next exchange. The
questions asked only for common-sense, real-world knowledge; no modelling
structure, notation, or formulation was put to the expert.

---

## Exchange 1 — Host effect: what changes and how long it lasts
**Question:** When a country hosts the Olympics, what actually changes there
that helps it win more medals, and how long does that extra success tend to
last after the Games?
**Reply (key points):** Hosts get automatic qualification / larger teams,
enter more events (including host-proposed ones), benefit from home crowd and
familiarity, and boost funding in the run-up. Judging effects are small and
not reliably documented. The boost is concentrated in the host Games and decays
quickly — roughly 20–50% above baseline, most gone by the next Games, a modest
residual sometimes for one further cycle if investment continues.
**How it was used:** Calibrated the host term `h_M`. The data-derived host
ratio (median host-year / non-host-year count) came back near 1.0, so the
*median* host effect is small; but the 20–50% upper bound from the reply is
applied as the host multiplier for the U.S. in 2028 (`h_Gold = h_Total = 0.35`,
the midpoint of the stated range). The decay rule (boost is host-year only, no
lasting legacy) is encoded as `I[host(c,t)]` — an indicator that is 1 only in
the host year, 0 otherwise. Interval over which it holds: the host Games and
at most the immediately following cycle.

## Exchange 2 — No lasting legacy of past hosting
**Question:** For a country that hosted decades ago (e.g. the U.S. in 1996),
does that old hosting leave any lasting extra medal strength compared with a
country that never hosted?
**Reply (key points):** No. The mechanisms (automatic qualification, extra
entries, home crowd, favourable programme) exist only for that edition and
disappear immediately. Funding/infrastructure can leave a modest residual for
one cycle at most, then is indistinguishable from the underlying trajectory.
"Hosts do better forever" is a confound — host-bid winners are already large,
wealthy medal powers. Treat past hosting as having no lasting effect; it
should not be a predictor.
**How it was used:** Constraint — the model has *no* term for past hosting.
The host indicator is 1 only in the actual host year. This is what makes the
U.S. 2028 prediction a clean "baseline × (1 + 0.35)" rather than a permanent
upward shift, and it is the reason the walk-forward validation does not credit
non-host years with a host effect.

## Exchange 3 — What makes a tiny country win its first medal
**Question:** Countries like Dominica and Saint Lucia won their first medals in
2024. What makes a tiny country finally win its first medal, and is that luck
or something that sticks around?
**Reply (key points):** Almost always a single exceptional individual, not a
broad program — one athlete in a small-field / niche / newly-added event, often
a diaspora athlete, sometimes a favourable draw. Mostly luck with a small
sticky component (the medal can trigger funding and the athlete may return),
but it is a low-probability tail outcome. A first medal is a weak predictor of
a second within one or two cycles; treat it as a rare-event process with a
small persistence term, not a step change in baseline.
**How it was used:** Justifies modelling first medals as a *rare-event
Poisson process* rather than a deterministic or step-function change. The
persistence term is kept small (a returning country's baseline stays low; see
the `0.3` shrinkage prior for countries with no recent history in
`predict_country`). The "single athlete / niche event" mechanism is why the
2028 first-medal estimate is driven by the *number of low-depth events* and
the count of still-medal-less nations, not by any baseline shift.

## Exchange 4 — Coach vs athlete: how much a coach moves the count
**Question:** How different is a famous coach from a famous athlete — how much
can one coach really move a whole country's medal count, compared with one
athlete?
**Reply (key points):** A coach moves a country's count far less than a single
star athlete and through a different channel. An athlete directly delivers
1–3 medals; a coach cannot win directly and is bounded by the athletes
available — realistically 1–3 medals at the margin for a mid-tier country, near
zero for a country with no athletes in that sport. Largest in team sports and
technical/judged disciplines (volleyball, gymnastics, diving, wrestling) where
tactics and talent development compound; smallest where individual talent
dominates. The effect is a slow, program-level multiplier, not a single Games.
**How it was used:** (a) Sets the magnitude for the coach-effect estimate:
1–3 medals at the margin for a mid-tier country, near zero without an athlete
pool, slow to materialize. (b) Determines *where* to look for evidence and
where to recommend coach investment — team/judged sports. The data scan
(coach_scan) counts (NOC, Sport) pairs whose medal count jumps ≥2 in a cycle
while the athlete pool is roughly stable (ratio 0.6–1.6), as a proxy for a
coaching/selection change rather than a new talent pool. It found 379 such
cases; the average jump is 3.65 medals in team/judged sports and 4.53 in
individual sports (individual-sport jumps are often a single dominant athlete,
consistent with the reply). This calibrates the "great coach" contribution to
roughly 1–4 medals per affected program per cycle.

## Exchange 5 — Why some countries are always strong in one sport
**Question:** What causes long-standing strength in one sport (e.g. China in
diving/gymnastics), and can a country build it deliberately?
**Reply (key points):** A self-reinforcing pipeline: deep domestic talent base
(large participation, early selection), sustained funding, full-time coaching,
a competitive domestic circuit, plus sport-specific fit (body types, cultural
prestige, role models). Medals bring funding and prestige, which recruit more
talent, which wins more medals — a feedback loop lasting decades. It can be
built deliberately but slowly (10–20 years), and only with a large enough
population/diaspora, sustained funding, imported elite coaching, and a sport
not already saturated. Small countries can build strength in narrow,
low-depth events but rarely across a whole sport.
**How it was used:** This is the core justification for the *persistent
baseline* in the model. Because strength is a slow feedback loop, a country's
recent count is the best predictor of its near-future count — the baseline is
a weighted recent history (0.65/0.25/0.10 over the last three Games) rather
than a fresh structural estimate. It also drives the recommendation logic:
coach investment is most effective where a pipeline already exists (to amplify
it) and in 10–20 year horizons, not as a single-cycle fix.

## Exchange 6 — Do programme changes really change the medal table?
**Question:** When the Olympics add or drop sports/events, does that really
change which countries win medals, or is it mostly noise?
**Reply (key points):** Real but modest and unevenly distributed — not pure
noise, not a game-changer for the overall table. It shifts medals at the
margin, not the top (a rounding error for top powers, a meaningful fraction
for mid-tier/small countries). It favours whoever already has athletes in the
added discipline, and can create first medals for tiny countries via new
low-depth events. Net effect on the standings: small; the table is driven by
population, wealth, and sport pipelines. Worth modelling as a country-specific
term, second-order compared with structural drivers.
**How it was used:** Calibrated the programme term `g_M = 0.3` as a
*second-order, country-specific* multiplier. `Eprog_{c,t}` is the relative
change between the two Games in the number of events in the sports where
country c actually placed athletes in the prior Games (i.e. it only rewards
existing strength, exactly as the reply says). It is clipped to ±0.5 and
multiplies the baseline, so it is a small perturbation, not a driver.

## Exchange 7 — The single biggest structural driver
**Question:** Setting aside hosting and programmes, what is the single biggest
reason one country wins far more medals than another year after year — and
does that reason change over a few years?
**Reply (key points):** Population size combined with wealth (GDP per capita):
a large, prosperous country has both a bigger talent pool and the resources to
develop athletes. Neither alone suffices (India is populous but underperforms;
the Netherlands and Australia punch above their population). A secondary
factor is sport-specific institutional depth. It does *not* change over a few
years — population and wealth move slowly, so underlying capacity is highly
stable over one or two cycles; year-to-year swings are mostly noise, host
effects, and programme changes around a persistent baseline.
**How it was used:** Confirms the model's architecture: a *stable baseline*
dominates, with host and programme as small time-varying corrections. The
structural inputs (log-population and log-GDP-per-capita) were *tested* as the
primary driver in an early version of the model and found to under-predict
top powers by 2–43× (GBR actual 65 vs structural 1.5), which is exactly the
"neither alone suffices / institutional depth dominates" point in the reply.
The final model therefore anchors on recent realised counts (the persistent
baseline, E5) and treats population × wealth as context rather than the
regressor. The structural data (2024 population and GDP-per-capita per
country) is retained in the parameter table as calibrated input for the
small-country shrinkage prior and for interpreting *why* the table looks the
way it does.

## Exchange 8 — Is last Games' count a good anchor for the next?
**Question:** If a country won, say, 20 medals in 2024, would you trust its
2028 count to land near 20, or do you expect a big swing?
**Reply (key points):** Expect it to land near 20 — no big swing. The count is
highly persistent because it is driven by slow-moving structural factors.
Typical swing is on the order of a few medals (roughly ±10–20%), not a
doubling or halving. Larger moves have an identifiable cause: hosting, a
programme change, a boycott, or a single dominant athlete/cohort aging in or
out. Treat the prior count as a strong central anchor with a modest
prediction interval.
**How it was used:** This is the central decision rule for the 2028
projection. The point prediction is the weighted recent baseline
(0.65 × 2024 + 0.25 × 2020 + 0.10 × 2016), which for a stable country is
dominated by the 2024 count — i.e. 2024 *is* the central anchor, exactly as
the reply says. The "identifiable causes" for larger moves are precisely the
model's two correction terms (host indicator for the U.S.; programme term),
so a country without either cause gets a prediction near its 2024 count. The
±10–20% swing is the target width of the prediction interval, which the
validation sweep (k, c0) is tuned to match.

## Exchange 9 — What the ±10–20% uncertainty actually is
**Question:** When you say the swing is usually ±10–20%, what does that
actually look like in medals for a mid-sized country — is the uncertainty
mostly from losing a few stars, or from the whole pool shrinking at once?
**Reply (key points):** For a mid-sized country at ~20 medals, ±10–20% means
roughly ±2–4 medals (a count plausibly anywhere from ~16 to ~24). The
uncertainty is mostly *idiosyncratic*, not pool-wide: a few stars aging out
(one dominant athlete can carry 1–3 medals), a single strong cohort moving
past its prime, and event-level luck (close finals, injuries, draws). The
whole pool shrinking at once is rare in a four-year window. Treat the band as
"which specific athletes are still there," not "the country's capacity
collapsed."
**How it was used:** Sets the *form* and *width* of the prediction interval.
The interval is Poisson-ish, `sigma = k*sqrt(p) + c0`, which is heteroscedastic
— wide in relative terms for small counts (where one or two athletes move the
whole number) and ~±15–20% for a mid-sized count of ~20, matching the
reply's "16 to 24." The validation sweep (see model log) chose
`k = 0.35, c0 = 2.0` so that walk-forward 95% coverage is 93.9% (Gold) and
86.7% (Total) — consistent with an idiosyncratic, bounded band that is honest
about missing some cohort-level swings.

## Exchange 10 — How many new first-medal countries per cycle, and the odds
**Question:** Four tiny countries won their first medals in 2024. In a typical
Olympic cycle, how many brand-new first-medal countries should one expect,
and is it more often one, two, or a handful?
**Reply (key points):** A handful — typically 2–5 new first-medal countries per
Summer Games; 2024's four is squarely normal. Not one or two, not dozens.
Bounded by how many countries remain medal-less (60+) and how rare a first
medal is for any single tiny nation. The count fluctuates — some Games one or
two, others five or more — depending on programme changes (new low-depth
events create more chances) and whether a cohort of tiny nations has a
standout athlete at the same time. Treat it as a small, roughly Poisson-like
count centred around 3–4.
**How it was used:** Calibrated the 2028 first-medal estimate. The historical
count per Games (from the data) over the last eight Games
(1996–2024) is [17, 7, 4, 8, 7, 4, 5, 5]; the 1996 value of 17 is an outlier
(the first Games of the post-Cold-War expansion of smaller NOCs), so the
*recent steady-state* mean over 2000–2024 is 5.4, and the full 1996–2024 mean
is 7.1. The reply's "centre around 3–4" is the *typical* cycle, with 2024's
four and the recent 4–8 range. The model reports the Poisson estimate with
`lambda ≈ 5–7`, gives `P(count ≥ 4)`, and states the odds as the Poisson tail,
consistent with "a handful, roughly Poisson-like." The "new low-depth events
create more chances" mechanism is why the 2028 estimate is conditioned on the
LA2028 programme being at least as large as Paris 2024 (738 events).
