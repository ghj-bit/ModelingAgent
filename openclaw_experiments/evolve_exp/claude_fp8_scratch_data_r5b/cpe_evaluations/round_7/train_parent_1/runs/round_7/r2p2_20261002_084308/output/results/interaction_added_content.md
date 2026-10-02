# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — Problem 2021_C (Vespa mandarinia)

Three fixed expert exchanges. Each reply is turned into a concrete parameter,
constraint, or decision rule in the model; the value and its interval/holding
conditions are recorded. The raw replies are inputs to the work, never copied
into solution.json.

## Exchange 1 — Data provenance (data handling)

**Question** (expert_question_1.md): Of the many public hornet reports that were
never officially confirmed or rejected, what is the usual reason they stay
undecided?

**Expert reply (paraphrased):** Most unverified reports stay undecided because
they lack usable evidence — no photo or specimen, or an image too blurry/distant
to distinguish Vespa mandarinia from look-alikes. A secondary cause is resource
limits (reports sit in the review queue), not inherent ambiguity. Genuinely
ambiguous images (clear picture of a plausible look-alike) are a minority.

**How it was turned into work (source: Exchange 1):**
- **Parameter / constraint:** A report's *evidence quality* is modelled as a
  binary covariate `has_image` (≥1 attachment) plus `n_attachments`. This is the
  operational reason a report is "Unverified" (no usable photo/specimen), so the
  classifier explicitly conditions on whether a specimen/photo exists rather than
  assuming all reports are equally informative.
- **Data-handling decision:** "Unverified" (2342 records) and "Unprocessed" (15)
  are *not* treated as a random sample of the true positive rate. Because the
  dominant reason they are undecided is the absence of a usable specimen (not a
  coin-flip), they are held out of the supervised fit (which uses only
  Positive vs Negative IDs) and are instead *scored* by the classifier. This
  prevents the model from building on non-representative, evidence-deficient
  inputs.
- **Interval / holding condition:** The claim that "lack of evidence" is the
  dominant reason holds for the bulk of the unverified set; the residual
  genuinely-ambiguous minority is covered by the model's own uncertainty (wide
  posterior on those records) rather than by assuming representativeness.

**Quantified check (from the dataset):** Only 68 of the 2342 "Unverified"
reports have an attachment, versus 2043/2069 of "Negative ID" and 11/14 of
"Positive ID". The sharp drop in image prevalence among unverified records is
consistent with the "no usable photo" explanation, supporting treating the
unverified set as evidence-deficient rather than a random subsample.

## Exchange 2 — Key structural assumption (model validity)

**Question** (expert_question_2.md): When reports arrive without any usable
photo, can the lab still rule most of them out from the description alone, or
must it check them in person?

**Expert reply (paraphrased):** Most can be ruled out from the written
description alone — no in-person visit is needed for the bulk. The notes carry
enough signal (size, colour, behaviour, plus location and date) to exclude common
look-alikes (yellowjackets, bald-faced hornets, paper wasps, cicada killers).
In-person/specimen checking is reserved for the minority whose description is
genuinely consistent with Vespa mandarinia (large, orange-and-black head, ground
nest, late-season timing) or which sit near a known detection.

**How it was turned into work (source: Exchange 2):**
- **Structural assumption validated:** *text-only triage suffices for most
  exclusions.* This justifies a text-feature model as the primary signal rather
  than requiring image analysis (no PIL/cv2 in the environment, so pixel-level
  analysis was infeasible anyway). The model therefore builds on the written
  notes: size descriptors (big/huge/large, inches), state (dead/captured/live),
  species cues (hornet, asian, killer, yellow-jacket, bald-faced, paper-wasp,
  cicada-killer), nest type (ground vs tree/building), season (fall vs summer),
  and colour (orange head, yellow stripe, black).
- **Constraint on decision rule:** Field verification is a *small residual*,
  targeted at reports whose description is consistent with VGH *or* near a known
  detection. This is exactly the top-N prioritization rule adopted in part (C):
  rank all reports by predicted probability and dispatch the limited field team
  to the top of that list, where the spatial-proximity term (distance to a
  confirmed positive) encodes the "near a known detection" condition.
- **Interval / holding condition:** The assumption holds for the bulk of the
  no-photo reports; it does not hold for the genuinely-consistent-minority, which
  is precisely the set the top-N rule surfaces for in-person follow-up.

## Exchange 3 — Interpretation context / decision threshold (risk tolerance)

**Question** (expert_question_3.md): When deciding whether a hornet sighting
really is the Asian giant hornet, which mistake do you treat as worse — missing
a real one, or sending a field team on a false alarm?

**Expert reply (paraphrased):** Missing a real one is far worse. A missed
positive can be an undetected nest whose new queens disperse up to ~30 km and
found new colonies the following spring — a potentially irreversible, spreading
population with severe honeybee losses by the time it is found. A false alarm
costs one bounded, recoverable field visit. The asymmetry favours tolerating many
false alarms to avoid even one miss, but not so far as to make triage
meaningless: rank reports so the scarce field visits go to the highest-probability
ones, accepting a low-but-nonzero miss rate rather than driving false alarms to
zero.

**How it was turned into work (source: Exchange 3):**
- **Decision rule / cost structure:** The prioritization is an *asymmetric-cost
  ranking*, not a fixed-probability threshold. The cost of a false negative
  (missed nest → ~30 km dispersal, irreversible) dominates the cost of a false
  positive (one field visit). Formally, with cost C_FN >> C_FP, the
  cost-minimising rule for a fixed field budget is to investigate the reports
  with the highest P(VGH) first (rank by score) rather than to apply a
  probability cut-off. The model therefore reports expected true/false positives
  and expected precision as a function of the field budget N (top-N), so the
  state can trade recall against number of visits.
- **Risk-tolerance parameter:** The decision is made at a *target recall* (miss
  rate), not a threshold. From the top-N sweep, the model states the recall
  (fraction of true positives captured) achieved per budget: e.g. a budget of
  N=50 visits captures ~61% of expected true positives, N=200 ~82%, N=500 ~99%.
  The recommended operating point is the smallest N at which the expected miss
  rate is "low but non-zero" — matching the expert's guidance — rather than N
  large enough to drive false alarms to zero.
- **Interval / holding condition:** The asymmetry (C_FN >> C_FP) holds because a
  missed nest is effectively irreversible at discovery while a false visit is
  bounded; it holds over the ~30 km queen-dispersal scale and the one-season
  window before new queens found new colonies.

---

**Note on provenance:** No empirical value was filled from memory. All
distributional/decisional parameters used by the model are either (a) read from
the supplied dataset (class prior, report rate, detection geometry, feature
prevalence) or (b) supplied by an expert exchange above (evidence-availability
reasoning, text-only-triage validity, and the false-negative/false-positive
cost ordering). The queen dispersal range of ~30 km is stated in the problem
statement itself and is used as the spatial-scale reference in the spread
analysis, not as an externally retrieved constant.
