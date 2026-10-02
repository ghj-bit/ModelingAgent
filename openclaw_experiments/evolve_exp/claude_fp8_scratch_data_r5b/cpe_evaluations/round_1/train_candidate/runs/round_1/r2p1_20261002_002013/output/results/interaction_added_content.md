# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence

Three fixed exchanges. Each reply is converted into a concrete parameter,
constraint, or decision rule that the model/submission uses. The replies are
recorded here only as evidence; the submission itself states the resulting
values and rules in its own formulation.

## Exchange 1 — Core mechanism (what distinguishes a true sighting)

**Question (expert_question_1.md):** "In the hundreds of hornet reports you've
seen, when someone truly finds a real Asian giant hornet versus just a big
ordinary hornet, what single thing usually gives the true one away?"

**Reply (summary, verbatim kept in expert_reply_1.json):** The reliable
diagnostic is the *head* — a massive, wide, orange-yellow head with large
eyes set far apart. Overall *size* is what reporters actually notice, but size
alone is unreliable (perspective, distance, photo scaling mislead).

**How it shaped the work:**
- The free-text notes overwhelmingly report *size* ("big", "large", "enormous"),
  which the expert confirms is NOT discriminative. My text feature `note_len`
  and size-words therefore carry little signal, and the model correctly does
  not rely on them (their coefficients are small / negative after standardization).
- The diagnostic (head shape, solid orange-yellow head, coloration) is a
  *specimen-level* trait that a report only carries if a specimen or a clear
  photo was submitted. This is encoded as the `has_specimen` feature (notes
  mentioning specimen / "sent to lab") and the image features (`nimg`,
  `max_dim`). A report that is far from a known cluster yet has a clear
  specimen photo is therefore ranked up; a report that is merely "a big
  hornet" is not.
- Operational consequence for prioritization: a high-priority report is one
  that (i) is spatially near a confirmed cluster, (ii) is in the active season,
  and (iii) has a specimen/clear image — because only the specimen lets the
  lab confirm the head morphology. Reports with only a distant, size-only
  description are deprioritized even if they look dramatic.
- Interval/validity: this is an expert empirical judgment on morphology; it
  holds for *V. mandarinia* vs. other large wasps in the Pacific Northwest and
  is the basis for treating "has specimen / clear image" as a gate, not a
  weight.

## Exchange 2 — Operational constraint (crew capacity)

**Question (expert_question_2.md):** "When the state gets a report that looks
like it could be a real giant hornet, how many field crews do they
realistically have to chase those down at once?"

**Reply (summary, in expert_reply_2.json):** Very few — on the order of **one
or two field crews** at any one time (a small dedicated unit), stretched by
travel time and season.

**How it shaped the work:**
- This fixes the action budget **K ≈ 2** concurrent investigations. The
  deliverable therefore cannot be "investigate all top-N reports"; it must be a
  *total ordering* of reports so the agency always knows the single next
  highest-value report to dispatch, and a queue of the next ~2.
- The priority score is a single scalar per report (the logistic
  P(positive | features)) so that ordering is well-defined and monotone.
  Reporting the top-10/top-25 as "the list" would overstate capacity; instead
  I report the score distribution of the top-K (K = 10, 25, 50, 100) as a
  *sensitivity* to show how the ranking degrades past the realistic K, and
  flag that only ~2 can be actioned concurrently.
- Interval/validity: K ∈ [1, 2] concurrent crews; valid across the season,
  tighter in fall when travel and volume peak.

## Exchange 3 — Interpretation / success criterion (eradication)

**Question (expert_question_3.md):** "After the hornet has been knocked out,
if reports keep coming in every month, what would finally convince you the
state is truly clear of it?"

**Reply (summary, in expert_reply_3.json):** A *sustained* absence of
*confirmed* positives despite continued reporting pressure — not a quiet
stretch. Concretely: no confirmed detection for **at least two to three full
seasons** (including a complete spring emergence and a fall reproductive
cycle) while the public keeps submitting reports at a normal rate and they are
still actively investigated and tested. The clincher is negative evidence from
*targeted surveillance* (no hornets in traps, no queens/nests at known or
suspected sites, no confirmed workers), because a single confirmed worker or
nest resets the clock. Passive-report silence alone is not sufficient — if
reports dried up you could not distinguish eradication from lost surveillance.

**How it shaped the work:**
- The eradication rule is therefore a **joint condition**:
  (a) 0 confirmed positives for 2–3 consecutive full seasons (Sep–Nov window
  each year, at least one spring + one fall cycle),
  (b) reporting volume held at a normal baseline (surveillance still live),
  (c) targeted surveillance (traps + site checks) returns zero workers/nests.
- This turns my quantitative result into a decision rule. I computed the
  probability of observing 0 confirmed positives in n confirmed reports at the
  fall positive rate p = 0.020 (upper 95% bound 0.038): with n ≥ 200 confirmed
  reports per season the false-"eradicated" probability at p = 0.038 drops
  below 0.5% ( (1-0.038)^200 ≈ 4.3e-4 ), so 2–3 such seasons is the right
  evidence level. A single confirmed worker or nest resets the clock, matching
  the expert's "clincher" criterion.
- Interval/validity: the 2–3 season window and the per-season n are calibrated
  to the measured fall positive rate and its Wilson interval from the data;
  the criterion is a rule of thumb from agency practice, stated to hold for a
  single established colony in one state.
