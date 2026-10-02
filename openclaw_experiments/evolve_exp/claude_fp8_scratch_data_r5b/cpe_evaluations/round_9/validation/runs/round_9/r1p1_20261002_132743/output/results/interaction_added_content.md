# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — MM-Bench 2002_C

Three expert exchanges, one question each. Each reply is input, not content: what
travels into the model is the value, the constraint, the equation, and the test —
in my own formulation. No expert sentence appears in solution.json.

---

## Exchange 1 — Structural validity: is a single year's vital rates a usable snapshot?

**Question (expert_question_1.md):** I asked whether a scrub patch's conditions
change enough year to year that next year's survival and breeding in the *same*
patch could look very different from this year's, or whether a patch stays
consistent — framed as field common-sense, no modelling terms.

**Reply (expert_reply_1.json), substance:** Florida scrub is a **fire-maintained**
system. Absent burning, vegetation density rises ~6%/yr, so a patch's open sandy
area shrinks measurably within a few years — that directly moves the habitat
variable used to predict Fa, Sj, Sa. On top of that, **rainfall is highly
variable**, and reproduction and juvenile survival are drought/wet-year sensitive,
so a single year's measured vital rates are a **noisy snapshot of a patch that is
also drifting directionally**. Practical implication: substantial within-patch
year-to-year variation plus a systematic downward trend in habitat quality between
fires; a one-year measurement per patch is a weak estimate of that patch's typical
rates.

**How the reply changed the work (source: Exchange 1):**
- **Constraint added to the model:** the Task 3 fitted relationships
  `Fa(S), Sj(S), Sa(S), C(S)` (S = patch size or open sandy habitat) are
  interpreted as holding at a **reference, recently-burned fire regime**, and they
  drift between fires. I state this explicitly as the interval of validity rather
  than presenting them as stationary constants.
- **Equation affected:** Task 6. The 6%/yr vegetation-density growth is the
  governing number; I model open-sandy fraction after k years of regrowth from a
  just-burned state as `open_frac(k) ≈ (1.06)^(-k)` and use it to set the burning
  interval that keeps patches in the viable band.
- **Bias/limitation recorded:** single-year, per-patch vital rates carry a
  systematic downward drift (fire) plus stochastic variation (rainfall); the Task 2
  cohort and the Task 2/3 rates are point estimates, not patch-typical means. This
  is why the viability line in Task 5 is treated as a threshold subject to error
  (which Exchange 3 then quantifies).

---

## Exchange 2 — Dominant bias: why a marked lizard is "not found"

**Question (expert_question_2.md):** When a marked juvenile is not found at the end
of the 350 m, 6-month recapture search, is it more likely that it died, moved
beyond 350 m, or was still nearby but missed?

**Reply (expert_reply_2.json), substance:** For a small, cryptic, ground-dwelling
lizard the **dominant** reason for non-recapture is **missed detection while it is
still nearby** — not death, not long-distance movement. Detection probability in
such 6-month surveys is well below 1. Of the remainder, **death is more likely than
movement beyond 350 m**: juvenile dispersal for this size is tens to a couple
hundred meters, and 350 m already covers most of the plausible range, so
emigration past the radius is the *least* likely explanation. Ranking: missed
detection > death > moved beyond 350 m (an empirical judgment, not a precise
figure).

**How the reply changed the work (source: Exchange 2):**
- **Bias mechanism identified:** the recapture histogram is **right-truncated at
  350 m and detection-limited**, so it *under-counts* true survivors; non-recapture
  is dominated by undetected-but-alive lizards, not mortality.
- **Parameter/constraint in the model (Task 4):** the recapture-based migration
  survival `P = 1 − exp(−350/λ)` (λ = mean hop distance ≈ 103 m from the interior
  50–250 m bins) is reported as a **lower bound** on true migration survival
  (`P_is_lower_bound = True`), not as an estimate of mortality. I do **not**
  attribute the non-recaptured fraction to death. The robust, decision-relevant
  output is the **migration-distance distribution** (mean ≈ 103 m) plus the ~10 %
  juvenile migration rate; P only scales how many of the migrants arrive alive.
- **Validation implication:** the 350 m bin (0.01) sits above the 0.00 at 300 m —
  non-monotone, which a smooth survival curve cannot do — confirming the 350 m
  point is the truncation/detection tail, so I fit the decay only on the monotone
  interior bins (50–250 m).

---

## Exchange 3 — Decision-relevant uncertainty threshold

**Question (expert_question_3.md):** Given the numbers came from single-year,
fire-driven, noisy measurements, roughly how far off could the population estimate
be, or how many patches could be misclassified, before the state's decision on
where to prioritize protection would actually change?

**Reply (expert_reply_3.json), substance:** The decision is **robust to large error
in the total population** — off by a factor of ~2 (half to double) would rarely
change the ranking or the broad policy conclusion; state prioritization is driven
by *relative patch value* and *presence/absence of viable populations*, not the
absolute headcount. It is **fragile on which patches are classified viable**: a
patch near the viability threshold flips with modest error in Fa, Sj, or Sa, and a
plausible **±20–30 % error band** in those rates is enough to flip borderline
patches. Practical threshold: the decision changes when the **set** of viable
patches changes, not when the total moves; if misclassification stays confined to a
few borderline patches, priorities hold.

**How the reply changed the work (source: Exchange 3):**
- **Threshold turned into a runnable test:** I added a sensitivity sweep that
  perturbs Fa, Sj, Sa independently by a uniform factor in `[−p, +p]` (p = 0.20 and
  0.30, 400 random draws each) and counts, per patch, the **fraction of trials in
  which the patch flips across the λ = 1 viability line**. A patch is flagged
  *borderline* if it flips in ≥ 10 % of trials. This operationalizes "the decision
  changes when the set of viable patches changes."
- **Result (reported in Task 5 outcome):** at ±20 %, 7 patches are borderline
  (2, 9, 10, 13, 15, 17, 20); at ±30 %, 8 (adds 12). The pattern is exactly the
  expert's: the clearly-viable large patches (2, 15, 17, 20, and 12 at ±30 %) are
  most likely to flip **down** (they sit just above λ = 1), while the mid-sized
  patches (9, 10, 13) are most likely to flip **up** (just below). The clearly
  small and clearly large patches are stable. I report the total landscape
  population (≈ 3.9 × 10³) as robust to ~2× error, and I present the viable-patch
  list as a core set (large, self-sustaining) plus a flagged borderline set whose
  classification is decision-uncertain.

---

## Provenance note

No empirical parameter in solution.json is filled from memory. Every empirical
number is either (a) in the task's own dataset (table1, table2, histogram, table3),
or (b) the built-in 6%/yr vegetation-density growth from the problem statement, or
(c) the ~10 % juvenile migration rate from the problem statement, or (d) supplied
by an expert exchange above (the 6%/yr fire-drift mechanism, the detection
dominance of non-recapture, and the ±20–30 % / ~2× decision thresholds). The
expert-exchange values are carried as *qualitative constraints and thresholds* that
shape the model's interpretation and validation; they are not copied verbatim.
