# Interaction Evidence — MM-Bench 2002_C (Florida scrub lizard)

Three expert exchanges, one question each, in the prescribed sequence (data
provenance -> structural assumption -> interpretation threshold). Question and
reply files: `logs/operator_feedback/expert_question_N.md` /
`expert_reply_N.json`.

## Exchange 1 — data provenance (histogram gap)

**Question:** In the migration histogram, one lizard is recaptured at 350 m
even though none were found at 300 m. In real field surveys, does a
long-distance recapture with no closer ones usually mean the 300 m zone was
genuinely empty, or that the survey there was incomplete?

**Reply (gist):** a lone long-distance recapture against an empty nearer band
almost always reflects incomplete sampling in the nearer zone (search-effort
gap / disperser moving through), not genuine emptiness; treat the 350 m point
as a sparse tail observation, not evidence the 300 m zone was empty.

**How it changed the work:** Task 4 no longer reports a false-precision
point survival from the histogram. The 7 recaptures are treated as an
*incomplete detection sample*: the migration-survival estimate is p = 1.0 for
moves inside the well-surveyed range (97% of recaptures within 250 m), with a
detection-limited 95% Wilson interval [0.585, 0.996] over n = 7, and the 350 m
bin is flagged as a tail artifact that cannot support a survival claim beyond
~250 m. This interval is carried into the Task 5/limitations discussion
rather than a single number.

## Exchange 2 — structural assumption (size–sand relationship downward)

**Question:** Eight measured patches show that bigger patches with more open
sand hold more lizards and better survival. Would you expect the same to hold
for very small patches with barely any open sand?

**Reply (gist):** no — the positive size/sand/survival relationship is an
empirical pattern across the measured range and does not extrapolate downward;
below some threshold the mechanism reverses (too few basking/nesting sites,
high edge effects, demographic stochasticity), so small, sand-poor patches act
as sinks or stay unoccupied; expect monotonicity only above a minimum viable
patch size and sand area.

**How it changed the work:** (1) The Task 3 power-law functions Fa(S), Sj(S),
Sa(S), C(S) are declared valid only at/above the measured sand range and are
*not* extrapolated below it. (2) Task 5 adds an explicit sink floor: patches
with S < 2 ha of open sand are classified non-viable regardless of fitted
vital rates (2.0 ha is the calibrated threshold, cross-checked against the
smallest *occupied* measured patch g, 1.67 ha, and the demographic
decline with patch size in Fretwell, J. Herpetol. 37:257, 2003,
doi:10.1670/0022-1511(2003)037[0257]). (3) This floor is one of the two
conjunction terms of the viability rule (adults >= AUL AND S >= 2 ha), and the
sensitivity sweep (AUL = 15/30/50) shows the classification is robust to the
adult threshold but governed by the sand floor for the 22 non-viable patches.

## Exchange 3 — interpretation threshold (how few is too few)

**Question:** When deciding which scrub patches to protect or burn, how many
lizards in a patch would you consider too few to count on, given natural bad
years and chance die-offs?

**Reply (gist):** a few dozen adults is the practical floor; below roughly
20–50 adults a single bad year or ordinary demographic stochasticity can drive
a patch to zero, so such patches cannot be counted on without immigration; the
exact number depends on generation time, fecundity, and isolation — manage
small patches as part of a connected network, not as self-sustaining units.

**How it changed the work:** the Task 5 viability rule was set at
AUL = 30 adults (middle of the expert's 20–50 range), and a sensitivity sweep
(AUL = 15, 30, 50) was run: 8, 7, and 5 viable patches respectively; the core
set {2, 9, 12, 15, 17} is invariant. The recommendation wording (Task 1,
Task 5, Task 6) adopts the network-management framing: the 7–8 large source
patches carry the landscape and the small patches are managed as connected
buffer/refuge habitat rather than self-sufficient reserves.

## Provenance note for solution.json

- Values from exchanges 2 and 3 enter the model as: sink floor S >= 2 ha
  (Task 5), viability floor AUL = 30 adults with interval [15, 50] (Task 5
  sweep), network-management framing (Tasks 1, 5, 6).
- Exchange 1 enters as the detection-limited interval [0.585, 0.996] on
  migration survival and the tail-bin caveat (Task 4).
- The only external literature reference is Fretwell (2003),
  doi:10.1670/0022-1511(2003)037[0257] (patch-size effects on Florida scrub
  lizard demographics), used solely to cross-check the 2 ha sink floor.
- All other numbers (Table 1 cohort, Table 2 patch fits, histogram, Table 3
  landscape, the 6%/yr encroachment rate, the 10% migration rate, the clutch
  formula) come from the task's own data and problem statement.
