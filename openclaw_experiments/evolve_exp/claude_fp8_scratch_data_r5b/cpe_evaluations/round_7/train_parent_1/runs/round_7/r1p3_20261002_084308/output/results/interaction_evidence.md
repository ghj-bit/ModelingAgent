# Interaction Evidence — MM-Bench 2015_C (ICM Human-Capital Churn)

Three exchanges, one question each, each reply converted into a model input.

## Exchange 1 — Data provenance / the missing salary cell
**Question (expert_question_1.md):** The table lists a salary for most job levels,
but the pay for the "experienced employee" level is missing. In a company like
ICM, how does the typical pay of an experienced regular employee usually compare
to the company's overall median pay, and roughly what multiple would you expect?

**Reply (expert_reply_1.json):** An experienced regular (non-managerial) employee
sits somewhat **above** the company-wide median — the median is pulled down by
the many lower-level and entry positions, while experienced staff carry a
tenure/skill premium. Empirical expectation: roughly **1.1× to 1.4× the median**,
modestly above median but well below the management tiers.

**How it entered the work:**
- Parameter: `ee_salary` (Experienced-employee salary, in σ) = **1.25σ**, interval **[1.1, 1.4]σ**.
- Used to (a) repair the missing `table1.csv` cell, (b) compute the company
  median-salary proxy σ and the CEO-to-median ratio, (c) set the salary
  distribution of the network layer. Source: Exchange 1.
- Data repair: `table1.csv` was GBK-encoded; all σ glyphs decoded, and the single
  missing salary cell (Experienced employee) was filled with 1.25σ from this reply.

## Exchange 2 — Structural assumption: is 85% a steady state?
**Question (expert_question_2.md):** ICM typically keeps only 85% of its 370
positions filled. Does that 85% reflect a stable, normal level of vacancies the
company lives with, or a position that keeps drifting downward over time as it
fails to keep up with departures?

**Reply (expert_reply_2.json):** 85% is best read as a **stable, chronic
vacancy level the company lives with**, not a downward drift. Real organizations
under continuous hiring pressure settle into a persistent "structural vacancy"
band: departures are offset by a steady inflow, so the unfilled fraction
stabilizes at what the hiring pipeline can sustain. ICM's own numbers support a
self-consistent steady state (~15% vacant, ~10% in the hiring pipeline, ~5%
not yet actionable). A downward drift would require hiring capacity to fall
persistently below the departure rate, which the description does not imply.

**How it entered the work:**
- This fixed the **core structural assumption** of the fill model: the 85% fill is
  an *equilibrium band*, not a decaying trajectory. Consequently the model makes
  churn a fraction of the **filled** workforce (departures scale with the current
  fill level), which is self-limiting and produces a stable equilibrium rather
  than a collapse to zero. Source: Exchange 2.
- Hiring-capacity parameter: HR is "actively hiring about 8–10% of positions",
  so `hire_frac` = 0.09 (band 0.08–0.10). The model's recovery term is tuned so
  the no-shock baseline hovers near the 85% band, consistent with this reply.

## Exchange 3 — Interpretation context: the crisis threshold
**Question (expert_question_3.md):** The company usually runs with about 85% of
positions filled. If your analysis shows it dropping to a certain fill level, at
what point would you, as the person running the business, treat that as a serious
crisis needing an immediate fix, rather than just uncomfortable short-staffing?

**Reply (expert_reply_3.json):** A drop to roughly **75% or below** is a serious
crisis needing immediate action. Reasoning: 85% is the chronic level and ~10% is
normally in the pipeline; ~75% means vacancies have roughly doubled and the
pipeline no longer keeps pace, with functional coverage lost in critical
(mid-level) roles. **Between 85% and ~78–80% is uncomfortable but manageable;
below ~75% the shortfall degrades operations and can feed further churn**,
warranting emergency intervention.

**How it entered the work:**
- Decision rule / interpretation threshold: `crisis_fill = 0.75`,
  tolerable band **[0.78, 0.85]**. Every fill-level result is reported against
  these two lines:
  * baseline 18%: fill 0.85→0.70 (2 yr) — crosses below 0.78 (uncomfortable) and
    reaches 0.70 (below the 0.75 crisis line) → churn is already eroding the band.
  * 25%: →0.60 (clearly crisis), 35%: →0.49 (deep crisis).
  * This threshold is what turns the model's fill trajectories into the
    "sustain 80%?" verdicts required by Task 4. Source: Exchange 3.

## Note on non-content
No expert wording is copied into solution.json. Only the numeric values and
bands above (1.1–1.4σ; 0.75 / 0.78–0.85 band; 0.08–0.10 hire share) travel into
the model, in my own formulation.
