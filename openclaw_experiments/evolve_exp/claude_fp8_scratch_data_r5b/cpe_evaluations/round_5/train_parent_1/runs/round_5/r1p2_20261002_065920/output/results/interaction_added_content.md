# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — ICM Human-Capital Churn Model (2015_C)

Three expert exchanges, one question each, in the order asked. Each reply was
converted into a concrete model parameter before the next exchange.

## Exchange 1 — Data provenance (asked before modelling)

**Question (full text in `logs/operator_feedback/expert_question_1.md`).**
The experienced-employee salary cell was garbled in `table1.csv`; I had
tentatively filled it at 0.5σ. I asked the expert whether a seasoned factory
employee's pay is about half the company median, roughly equal to a new
employee's, or something else, and whether the seven-level pay table is
complete/trustworthy.

**Expert reply (summary).** A seasoned production worker sits *at or slightly
above* the company median — roughly 0.9–1.2σ — not at half of it; half the
median is closer to an entry-level/clerical wage. The seven levels are usually
all populated, but recruitment-cost and training-cost values are frequently
*estimated* (allocated averages) rather than tracked per hire; salaries are the
most reliable column, recruitment time/cost the least. A garbled single cell is
a plausible artifact, not systematically missing levels.

**How it changed the work.**
- Experienced-employee salary re-set from 0.5σ → **1.0σ** (midpoint of the
  expert's 0.9–1.2σ range). This is the value used in `table1_clean.json` and
  everywhere in the model. It also restores the correct ordering (experienced
  employee now earns more than a new employee/clerk at 0.9σ).
- Consequence for σ: with 150 new employees + 30 clerks + 110 experienced
  employees at ≤1.0σ, the 185th/186th ordered salary is 0.9σ, so **σ = 1.0** is
  self-consistent (verified in `logs/clean_table1.log`). I treat σ as the
  normalization unit for all costs/salaries, per the dataset description.
- I flagged recruitment-cost and training-cost columns as *estimated* inputs
  (higher uncertainty) in the assumptions, while treating salary as the anchor.

## Exchange 2 — Key structural assumption (build on Exchange 1)

**Question (full text in `expert_question_2.md`).** Given the pay table is
broadly complete, I asked whether, when a middle manager or skilled worker
quits, the position is left genuinely empty for weeks/months (lost output,
overtime) or covered by a stopgap (acting/under-qualified/internal move) so the
post is rarely empty — i.e. is the dominant cost of churn the empty seat or the
temporary stopgap?

**Expert reply (summary).** The dominant pattern is the *temporary stopgap*, not
the empty seat — but the balance differs by level. Skilled production workers:
seat backfilled fast by internal move / overtime; rarely truly empty; cost shows
as overtime pay, lower throughput, a less-experienced person. Middle managers
(junior managers, experienced supervisors): hardest to cover; a stopgap is
common but the role needs specific experience, so the seat stays partly vacant
or thinly covered for the full 3–6 month search lag — *both* a degraded stopgap
and a long period of reduced managerial capacity. The seat is almost never
literally empty, but frequently filled by someone less qualified than the
departing person; the quality gap persists until the proper hire is trained.
Dominant cost = the stopgap (lost productivity + training/ramp of the
replacement), with empty-seat cost secondary and concentrated in mid-level roles.

**How it changed the work.** This became the core model structure:
- Each seat has a **quality index** (1.0 = fully-trained incumbent; a stopgap
  seat carries a lower quality `q_stop`). Headcount (filled seats) is therefore
  *not* the right productivity measure — I model a **quality-weighted
  productivity index** = (full seats + q_stop·stopgap seats)/370.
- Stopgap qualities by level (my encoding of "less qualified, mid-level most
  degraded"): senior 0.80, junior-manager 0.40, exp-supervisor 0.40,
  inexp-supervisor 0.50, exp-employee 0.70, inexp-employee 0.70, clerk 0.70.
- A departing seat is immediately covered by a stopgap (headcount preserved) and
  a requisition is opened that lands after the median `t_rec` months; on landing
  the seat returns to quality 1.0. This is why headcount fill stays in the
  84–91% band while productivity sags — the two are now distinct outputs.
- The "3–6 month thin coverage for middle managers" is exactly the `t_rec` of 5–6
  months for those levels, so the mid-level stopgap dwell time is captured.
- Because the seat is rarely *empty*, the answer to Task 4's "can ICM sustain 80%
  fill" is yes on headcount at all three churn rates — the *binding* constraint
  the model surfaces is the quality/productivity dip, not vacancy count. I report
  both, and the indirect productivity-loss cost as a separate line.

## Exchange 3 — Interpretation context for uncertainty (build on Exchange 2)

**Question (full text in `expert_question_3.md`).** Given (1) recruitment and
training costs are estimated rather than measured, and (2) the productivity
index rests on assumed stopgap-quality levels, I asked the expert what level of
deterioration in the model's headline numbers would make a conclusion
unsuitable for an HR decision — i.e., the decision-relevant threshold, not an
abstract error bar.

**Expert reply (summary).** Three decision lines, not one. (a) Effective
capacity: a **sustained ~5% drop is only a first warning** (normal wobble at 18%
churn with constant stopgaps); a **sustained ~10% loss is a red flag requiring
action**; **15%+ is a crisis**. "Sustained" is the operative word — a dip that
recovers within a quarter or two is noise; a decline persisting across several
quarters and still trending down is the signal. Because the "capable" number
rests on a judgment of stopgap effectiveness, do not act on the point estimate
alone — act only when the decline is large enough to survive that uncertainty.
(b) Middle management: act *immediately*, on a structural test rather than a
percentage — when the **internal promotion pipeline is exhausted** (stopgaps are
being drawn from people not plausibly promotable, or the same mid-level seats
turn over repeatedly). A 30% churn concentrated in junior managers and
experienced supervisors with **no external recruiting** hits that condition well
before the company-wide number looks alarming, because the mid-level pool is
small and non-substitutable. The line is: company-wide ~10% sustained decline,
*or* mid-level pipeline exhaustion — whichever comes first.

**How it changed the work.**
- I adopted the **three-tier decision scale** (5% warning / 10% sustained red
  flag / 15%+ crisis) and evaluated every scenario against it. None of the
  headcount or 2-year-average scenarios crosses 10% sustained; the Task 5
  no-external-recruiting case is the exception on the *structural* test: its
  mid-level promotion pipeline (15% qualified pool, 50% promo share) is
  exhausted, mid-level effective coverage collapses toward ~55%, and 307 of 370
  seats sit on non-promotable stopgaps by month 24 — flagged as the critical
  failure mode and the one scenario that warrants immediate action.
- I report **sustained** vs **transient** decline: the 24-month trajectory shows
  each scenario's effective-capacity dip recovering or flattening (transient,
  → within the 5% warning band) versus the no-external case, which is still
  trending down at month 24 (→ structural, crosses the line).
- I foreground the **rank order** of scenarios (base < 25% < 35% < no-external)
  as the robust result and give absolute budget/loss figures with an uncertainty
  caveat (recruiting/training costs are estimated inputs per Exchange 1), since
  the expert said not to act on the point estimate alone.
- The contagion weight β (Task 2) is reported as a *sensitivity* (0.0 → 0.20),
  with the qualitative finding — network contagion roughly doubles 24-month
  churn versus base hazard alone — because its magnitude is exactly an estimated
  input whose rank-order effect (contagion > no contagion) is the robust part.

---
All three exchanges produced a parameter/constraint that is present in the model
and the final `solution.json`. No exchange is unspent; none is used as content —
only the values, thresholds, and structural choices above.
