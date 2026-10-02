# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence (3 exchanges)

## Exchange 1 — before Part 1 origin/characterization work
**Question (expert_question_1.md):** "In the Appalachian counties you know, where would new drug trouble typically start first: in a town, or between towns?"
**Reply (expert_reply_1.json, key points):** Trouble shows up first in towns, not between towns. Reasons: supply/distribution needs density (dealers, pill mills, labs locate at county seats, cities with hospitals, highway interchanges, colleges); NFLIS identification counts follow enforcement and lab access, so town-bearing counties light up first; rural interior counties lag by a few years as use spreads outward via social networks and stays under-recorded longer.

**How the reply became work:**
- Parameter/constraint in the model: origin detection is restricted to counties containing the state's metro/micropolitan nodes (county seats along the I-75/I-64/I-77/I-81 corridors); rural interior counties are modeled as laggards with a lag of "a few years" (held as 2-3 years in the transition analysis, interval supported by the reply's qualitative judgment).
- Decision rule: earliest-sustained-activity ranking (cumulative opioid identifications >= 5 within a county) computed first, then the town/rural ordering applied as the tie-breaker and interpretation layer. Run: code/part1.py output lists the earliest active counties per state; the report's origin answers follow the town-first ordering (e.g., OH: Columbus/Cincinnati-area metro counties; KY: Louisville metro (Jefferson, Kenton, Campbell); WV: Charleston metro (Kanawha, Greenbrier, Monroe); VA: Richmond/Norfolk metro counties), with rural interior (e.g., WV northern panhandle, KY east-central hollows) classified as lagging per the expert's expectation.
- Interval of validity: 2010-2017 NFLIS identification window, five-state region.

## Exchange 2 — before threshold/early-warning calibration
**Question (expert_question_2.md):** "For a county to be a warning sign, is a big total more telling than a steep recent rise?"
**Reply (expert_reply_2.json, key points):** A steep recent rise is the warning sign; a big total mostly reflects county size, population, metro center, hospital, or police/lab pipeline and is stable year to year (little new information). Use the big total to locate where the burden already is (resource allocation) and the steep recent rise to flag where trouble is emerging (early warning).

**How the reply became work:**
- Decision rule change: the early-warning indicator is defined as the change in per-capita identifications (ids per 100k) between consecutive 3-year windows, not the raw total; the per-capita rate is used instead of raw counts precisely because the reply identifies raw totals as confounded by county size. Run: code/part8.py / part9.py compute flag performance of T/100k levels of the 2014 per-capita rate against 2013->2016 risers: T=3/100k gives precision 0.59, recall 0.75, F1 0.66 (best F1), so T=3/100k is adopted as the warning threshold, interval 2010-2016 calibration window.
- The "big total" half became the second, separate output: state-level burden ranking (Ohio > Virginia > Kentucky > West Virginia by 2016 per-capita rate and total) for resource allocation, distinct from the rise-based early-warning list.

## Exchange 3 — before the Part 3 strategy design
**Question (expert_question_3.md):** "If rising counties get help early, what does a good response depend on?"
**Reply (expert_reply_3.json, key points):** Success hinges on (a) the rise being real and sustained, not a reporting artifact (new lab, new submitting agency, testing-policy change, backlog clearing); (b) enough lead time — the county must still be small in absolute burden when help arrives, or it is no longer "early"; (c) local capacity — functioning health department, treatment/MAT access, prescriber oversight, police/lab infrastructure, with help that builds capacity in rural counties; (d) supply-side reach — external supply chains on highway corridors defeat local demand-side-only measures; (e) sustained multi-year commitment — one-off grants fail.

**How the reply became work:**
- Model structure for Part 3 (code/part3c.py): the intervention has three explicit parameters mirroring the reply — kappa (annual fraction of the active case pool removed by treatment/capacity; capacity bound c = max absorbable share of the wave, encoding "capacity"); L (lead time in years before the response engages, encoding "enough lead time" and "sustained commitment" — a response that starts too late cannot reach the wave); and T (warning threshold at which the response triggers).
- Validity gate (artifact check, from point a): a county's rise must be sustained across two consecutive years before it qualifies for the response (implemented as the two-year confirmation in the strategy; in the simulation this is the T-crossing condition combined with L).
- Run results (part3c.py): baseline (no response) state wave peaks 2.4-14.5% of county population share by end of window (OH highest). kappa x L sweep: with kappa=0.3 the wave is cut from 0.071 to 0.019 (mean across states) when the response engages within ~2 years of the warning (L<=2); delaying to L=3 raises it back to 0.023. Capacity bound: c must be >= 0.25 of the wave for kappa=0.3 to hold its effect (c=0.05-0.1 absorbs nothing useful). Threshold: T <= 0.01 of population keeps the trigger early enough; T=0.05 defeats it. Critical effectiveness: kappa >= 0.08-0.10 per year is needed for a 30% wave reduction; lead time must stay within ~5 years for any 10% benefit at kappa=0.3. These bounds are the "significant parameter bounds success is dependent upon" requested by Part 3.
- Strategy statement: target the 150 counties identified as risers (2013->2016 rise >= 3 ids/100k from a base >= 1/100k) with MAT/capacity investment triggered at 3 ids/100k (Exchange 2 threshold), requiring sustained two-year confirmation (Exchange 3 validity gate), sustained multi-year funding (Exchange 3 commitment), and paired highway-corridor supply interdiction (Exchange 3 supply-side reach).
