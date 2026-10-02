# Expert Interaction Evidence

Three exchanges, one question each, qualitative only. All questions
answerable without modelling background; no numerical parameters requested
or received.

## Exchange 1 — Mechanism
Question: "Do lab reports mainly track the real drug supply reaching a
county, or how hard local police search that year?"

Reply (substance): the NFLIS series is a *reporting* series, not a
prevalence series. A case enters only when local enforcement makes a
seizure and submits evidence. In small rural counties the level of counts
is driven by enforcement/submission behavior (task forces, grants,
submission thresholds, lab intake policy); the underlying supply sets a
floor and drives the substance *mix* more reliably than the *level*.
Raw cross-county / cross-year comparisons of counts are unreliable
without normalizing for enforcement effort.

How the reply was turned into work (this exchange governed model form):
- Modeling variable changed from "prevalence" to "reported identifications";
  all downstream claims are framed as statements about the reported series.
- Model structure (see solution.json, mathematical_modeling_process):
  reported count N(c,t) = e(c,t) * S(c,t) * z(c,t), where e is an
  unobserved enforcement/submission factor that multiplies counts, S is the
  supply-driven component, z is noise. Because e is unobserved, the model
  does NOT estimate S directly; it models the reported series and uses the
  *composition* (fentanyl vs heroin vs other synthetic) as the supply signal,
  since composition is less sensitive to e than level. This is the concrete
  modeling consequence: Part 1 dynamics model is fit on level-normalized
  and composition shares, not raw counts.
- Interpretation rule adopted: a county-year count change is attributed to
  supply only if accompanied by a composition change AND a correlated change
  in neighboring counties (see Exchange 2 for the full test).

## Exchange 2 — Boundary / transition
Question: "When lab report counts spike sharply, what signs tell a real
supply shift from just an enforcement push?"

Reply (substance): a real supply shift is indicated by (a) a change in
substance mix, (b) correlation across neighboring counties with different
agencies, and (c) persistence after the enforcement/grant cycle ends. An
enforcement push is isolated to one or a few counties, tracks a specific
agency's activity, is abrupt and reversible, and leaves the drug mix
unchanged.

How the reply was turned into work:
- Defined an operational "supply-shift test" used in Part 1 to classify
  county-year spikes: a spike is classified as supply-driven iff it
  (i) coincides with a composition change (fentanyl or other-synthetic
  share rising relative to heroin), (ii) is accompanied by a rise in at
  least one neighboring county in the same or adjacent year, and
  (iii) is not fully reversed within one year. Spikes failing the test are
  classified as enforcement artifacts and excluded from the "spread"
  narrative. This test is applied in code (Part 1) and the classification
  result is reported per county.
- Set the sensitivity/validity bound for the level-based spread model:
  because e(c,t) is unobserved and can be agency-linked and reversible,
  the level of the spread model is only valid as a relative, same-state
  comparison within a rolling 2-year window; absolute cross-state or
  long-horizon level comparisons are flagged as low-confidence.

## Exchange 3 — Interpretation of uncertainty
Question: "A county has almost no reports one year, then many the next.
Is that a new drug problem there?"

Reply (substance): not on that evidence alone. In low-volume rural
counties, small-count instability (1-2 to 10-20 reports is a handful of
cases, not an epidemic) and changes in submission behavior can produce
exactly this pattern with no supply change. A real new problem requires the
same three corroborations as Exchange 2: composition change, neighboring-
county corroboration, and (in real practice) health-data corroboration.

How the reply was turned into work:
- Set a minimum-count threshold for treating a county-year as a reliable
  observation: county-years with fewer than 10 total narcotic/heroin
  identifications are flagged as low-count and excluded from any
  rate-per-capita or threshold-crossing claim; they are reported only as
  raw counts with a low-reliability flag. This directly implements
  "percent changes are meaningless at these counts."
- The "new problem" determination rule in Part 1 (identifying where use
  may have started) requires the three-part corroboration, not a single
  county's jump; the resulting origin list is therefore the set of
  counties whose first reliable signal is corroborated regionally.
- All Part 1/2/3 results that depend on a county-year below the
  minimum-count threshold are annotated as low-reliability in
  subtask_outcome_analysis.

## Compliance note
No numerical parameter was taken from any expert reply. All three replies
supplied qualitative logic (mechanism, transition test, uncertainty rule)
which was translated into model structure and decision rules as recorded
above. All empirical numerical values in solution.json are either from the
task's own datasets (NFLIS counts, ACS estimates) or from the staged
search helper with a recorded source.
