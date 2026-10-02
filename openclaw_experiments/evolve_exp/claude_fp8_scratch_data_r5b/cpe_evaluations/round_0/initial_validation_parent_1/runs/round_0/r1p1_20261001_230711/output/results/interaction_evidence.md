# Interaction Evidence

## Exchange 1 (governs Task 1)

**Question** (expert_question_1.md): "In Florida practice, what is the single biggest real
obstacle to actually preserving scattered scrub habitat patches for a species like the
scrub lizard?"

**Reply** (expert_reply_1.json): the biggest obstacle is land ownership and economics —
scrub survives on high-value upland real estate as a fragmented mix of private parcels,
subdivisions, citrus/agriculture, and military or state land. Protection means buying many
small tracts or restricting owner use, hitting cost, willing-seller limits, and
property-rights/political resistance. Fragmentation compounds this: each patch is too small
to be a priority alone, so protection depends on coordinating many owners, and fire-dependent
scrub needs ongoing burning that adjacent homeowners resist.

**How the reply became work** (Task 1 in solution.json):
- Constraint adopted: preservation is a multi-owner coordination problem, not a single-estate
  one — so the recommendation is landscape-scale acquisition/purchase priority (largest,
  most connected patches first) plus transferable development rights and conservation easements,
  which target exactly the two obstacles the reply named (buying many small tracts; restricting
  owner use).
- Constraint adopted: fire as the recurring maintenance cost — the Task 1 recommendation list
  includes a prescribed-burning program as the central ongoing management action, and the
  stated obstacle of adjacent-resident opposition to burning is carried into the obstacles
  paragraph. Interval: present-day Florida land tenure, as stated by the expert (exchange 1).

## Exchange 2 (governs Task 4)

**Question** (expert_question_2.md): "In the field, how far do young Florida scrub lizards
typically travel when they leave their natal patch?"

**Reply** (expert_reply_2.json): tens of meters — most juvenile dispersal is roughly 10–100 m,
bulk under ~50 m; movements beyond a few hundred meters are rare, the histogram's 350 m survey
radius is an outer bound, not a typical distance (empirical judgment from scrub-lizard movement
studies).

**How the reply became work** (Task 4 in solution.json):
- Constraint adopted: typical juvenile movement range 10–100 m, median ≲50 m (source: exchange 2).
  Used to set the working pair-patch distance for the migration-survival estimate: P(survive
  migration i→j) is evaluated at D = 50 m (bulk-of-movement distance), giving p_m ≈ 0.50 from
  the recapture histogram (42% within 50 m + ~8% of the 50–100 m bin), and at the outer bound
  350 m, giving p_m ≈ 1.00 (99% recaptured). The histogram's 350 m survey radius is treated as
  the detection bound, consistent with the expert's characterization.
- The Task 5 dispersal correction uses p_m = 0.545 (recapture mass within 50 m + half of the
  50–100 m bin) rather than the survey-radius value, because only the ~10% of juveniles that
  actually disperse matter and the bulk of their movements are under 50 m (exchange 2).
  Interval: typical juvenile dispersal in Florida scrub, as stated by the expert (exchange 2).

## Exchange 3 (governs Task 6)

**Question** (expert_question_3.md): "How often are Florida scrub areas burned in current
management practice to keep the open sandy habitat healthy?"

**Reply** (expert_reply_3.json): fire-dependent system needing burning roughly every 5–15 years
to stay open and sandy; typical managed return intervals ~5–10 years, some sites 3–8 years where
hardwoods/sand pine encroach; in practice many managed patches are burned less often than the
ecological ideal (10–20+ years or fire-suppressed) due to smoke management, weather windows,
staffing, liability, and neighbor objections. Target interval ~5–15 years, achieved interval
frequently longer (empirical judgment).

**How the reply became work** (Task 6 in solution.json):
- Constraint adopted: target burn return interval 5–15 years, central practice 5–10 years
  (source: exchange 3). The 6%/yr vegetation-density growth rate from the problem statement is
  used to compute how fast open-sand suitability decays between burns: openness modeled as
  O(t) = exp(−0.06 t) (first-order decay at the observed 6%/yr vegetation-growth rate), mean
  cycle openness = (1 − e^{−0.06T})/(0.06T). Requiring mean openness ≥ 0.80 gives T ≈ 7.7 yr;
  ≥ 0.75 gives T ≈ 10.1 yr — both inside the expert's 5–15 yr window, so the recommended
  policy is a **5–10 year controlled-burn rotation** (5–8 yr on fast-encroaching sites), with
  the reply's practical caveats (weather windows, smoke management, liability, neighbor
  objections) carried into the implementation-conditions paragraph.
- The reply's observation that actual achieved intervals are often 10–20+ yr motivates the
  policy recommendation that burn rotations be scheduled, funded, and enforced (rotation
  calendar per patch) rather than ad hoc, since letting intervals drift past ~10 yr drops mean
  openness below the 0.75 working threshold. Interval: current Florida scrub fire-management
  practice, as stated by the expert (exchange 3).
