# Expert Interaction Evidence — MM-Bench 2015_C (ICM Human-Capital churn)

Three exchanges, one qualitative question each, in the mandated order. Each reply
was converted into a model constraint before the next exchange. No expert number
was treated as an empirical fact; replies supplied the mechanism, boundary, and
interpretation lens only.

## Exchange 1 — dominant mechanism (before building the churn model)
**Question:** *When an employee quits, is it mainly that person's own decision, or does it usually spread because coworkers and friends leave together?*

**Reply (summary):** Voluntary turnover is predominantly **individual** — driven by pay, advancement, dissatisfaction, and external offers. Peer "spread" is real but **secondary**: having churned contacts measurably raises an employee's own churn probability (social contagion / peer influence), yet it explains only a **modest share** of departures, not the majority. Contagion matters most in **tight, cohesive subgroups and among mid-level managers**, where turnover is already elevated.

**How the reply changed the work:**
- The churn model is built on an **individual hazard rate per employee** `h_i` (level-specific), NOT on a network-dominant mechanism.
- A **peer-contagion modifier** `×(1 + β·frac_churned_neighbors)` was added as an *amplifier*, not the driver.
- Contagion coupling was concentrated in **mid-level (junior manager / experienced supervisor) subgroups**, which have the highest base hazard.
- The contagion magnitude was set so it explains a *modest* share: the `contagion.py` sweep (β = 0.0–0.5, 12 mo, 3% seed) yields an excess of **0 → 6.2%** of annual departures, peaking ~3.7% at β = 0.3. This is the quantitative realization of "modest share."
- Interval of validity: the "modest share" holds while β ≤ ~0.5 and contagion is confined to mid-level clusters; it would overstate contagion if applied company-wide at high β.

## Exchange 2 — operational boundary (built on E1)
**Question:** *If the company stopped hiring outsiders and only promoted from within, which job levels would run empty first?*

**Reply (summary):** The **entry-level / lowest positions run empty first**. Internal promotion is a **zero-sum upward flow**: every promotion moves someone up, and with no external intake at the base the bottom drains continuously. The **top is fed last** (kept alive by promotions from below). The shortage **propagates upward** — mid-levels (junior managers, supervisors) follow as their feeder pool disappears, even though those are the highest-churn levels. Ordering is structural: *lowest first, highest last*.

**How the reply changed the work:**
- Task 5's "no external recruiting" scenario is modeled as **external intake = 0**, with internal promotion as the *only* upward flow. The model therefore **cannot hold mid-levels** once the base feeder pool thins — reproduced in the simulation: with no external recruiting, fill drops 80.5% → 64.8% over 2 yr and junior-manager fill collapses to **44%**.
- The promotion flow is capped so it is *zero-sum*: a person promoted out of a level is subtracted from the source and added to the destination, and no level is refilled beyond its nominal headcount (capacity clip).
- This is the **operational boundary** for validity: any "promote-from-within-only" recommendation is only viable over a horizon where the base levels can be externally replenished; the model flags the horizon where the pyramid empties bottom-up.

## Exchange 3 — interpretation of signal vs. artifact (built on E1+E2)
**Question:** *What would tell you a rise in departures is a real trend worth acting on, versus just normal yearly variation?*

**Reply (summary):** A rise is a **signal** when it shows (a) **persistence** across 2–3 consecutive years or monotonic drift (with ~370 positions and 18% churn ≈ 65–70 exits/yr, single-year swings of several points are normal noise); (b) **concentration** in specific levels/subgroups (mid-levels), not a diffuse uniform rise; (c) **composition shift** — departures disproportionately high-performers, short-tenure, or network-central people (costlier than the raw count); (d) **leading indicators moving together** (rising vacancies, longer time-to-fill, promotion shortfalls, clustering of exits among connected coworkers — a contagion signature); and (e) **external corroboration** (exceeds the broader labor market). A single-year rise with none of these is normal variation.

**How the reply changed the work:**
- Results are reported as **level-specific fill trajectories across both years**, not a single aggregate number, so *concentration* (junior managers / experienced supervisors draining fastest) is visible and can be checked against a "diffuse" null.
- A **signal test** was applied: the mid-level collapse (junior-manager fill 71% → 44% in Task 5, sustained over 2 yr, with matching rise in vacancies and promotion shortfall) is flagged as a *genuine signal*, whereas a one-year wobble in base-level fill is treated as noise.
- **Composition/bias lens**: the model's cost is weighted by salary (higher-level departures cost more per head), so a raw "departures" count understates the true cost when the mix shifts toward mid-levels — this is the model's key bias, and it is reported in every subtask's outcome analysis.
- **Contagion signature** (clustering of exits among connected coworkers) is the diagnostic that distinguishes a contagion-driven event from an exogenous (market-wide) one; the `contagion.py` layer can be run to check whether excess departures cluster in mid-level neighborhoods.

---
### Provenance note
No empirical number in the submission is taken from these exchanges. The replies
supplied (1) the mechanism hierarchy (individual hazard > contagion), (2) the
zero-sum promotion / bottom-up-drain boundary, and (3) the signal-vs-artifact
criterion. All numeric churn rates, salaries, recruitment costs, and the
contagion excess come from the supplied `table1.csv` or from cited external
sources listed in `solution.json` (parameter table).
