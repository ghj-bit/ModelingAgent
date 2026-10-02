# Interaction evidence — 2002_C (Florida scrub lizard)

Three expert exchanges, one question each, in order. Files: `logs/operator_feedback/expert_question_N.md`, `expert_reply_N.json`.

## Exchange 1 — structural fit of the loss process

**Question:** In your experience, is losing a scrub lizard's habitat usually from one big event or from slow gradual change, and which matters more for survival?

**Reply (summary):** Habitat loss in Florida scrub is overwhelmingly slow and cumulative, not catastrophic. Main processes: fire suppression (scrub closing into dense forest), conversion to citrus/pasture/development, fragmentation over decades. A patch can keep its area yet become unsuitable as vegetation closes in. Gradual loss matters more than any single event because the lizard is a poor disperser between isolated patches: slow degradation progressively eliminates viable patches and prevents recolonization. The decisive factor is the rate of gradual loss relative to persistence and dispersal ability.

**How the reply became work:**
- Task 1 (factor list and policy) is framed around the RATE of gradual loss of open sandy habitat, not rare events; fire suppression is listed as the common root cause.
- Task 3: the structural predictor for all vital rates and density is chosen as open sandy area (the thing that slowly closes), consistent with the expert's mechanism; the two-predictor fit is reported as ill-conditioned (A–S correlation 0.96) and the single-predictor sandy-area fits are the operational functions.
- Task 6: the 6%/year vegetation-density increase is treated as the quantitative expression of this slow-closure mechanism, and the burn interval is derived from it.

## Exchange 2 — selection mechanism in the migration/recapture data

**Question:** When a scrub lizard patch has fewer juveniles, do you see them moving to neighboring patches or just disappearing?

**Reply (summary):** Local disappearance, not rescue flow. Juvenile migration is a fixed, low-probability event (~10%), driven by density and dispersal opportunity, not by a patch being short of juveniles. A patch with few juveniles is a poor-recruitment patch (low Sj, degraded or too-small sandy area), which also means fewer juveniles available to emigrate. Scrub lizards are poor dispersers and patches are isolated, so a leaver has a low chance of reaching and surviving in a neighbor. Typical outcome: the patch declines toward local extinction; immigration is real but sparse and largely independent of the source patch's juvenile count.

**How the reply became work:**
- Task 2: the cohort is treated as closed (no immigration/emigration of tracked individuals) — stated assumption.
- Task 4: the histogram (recaptures by distance, sums to 1) is interpreted as the distribution of DISTANCE moved by survivors only; the migration survival probability P(survive i→j) = 0.10 (problem's "about 10 percent of juveniles migrate") is the calibrated value, with the histogram giving mean survivor distance 81 m as a summary. The per-neighbor survival is noted to be lower than 0.10.
- Task 5: the metapopulation is modeled as per-patch closed stage models with a small (≤10% of emigrants) immigration correction; declining patches go to local extinction and are not rescued; the viability classification (patches 3 and 18 not viable) rests on this.

## Exchange 3 — recovery criterion after fire

**Question:** After a prescribed burn, how long does it take before scrub lizards start breeding normally in that patch again?

**Reply (summary):** On the order of 2–5 years. The immediate post-burn period is poor (burn removes cover and litter; survival dips). Breeding resumes as vegetation regrows to the sparse, low structure the species needs; recovery of suitable structure takes a couple of years, full return to normal fecundity and recruitment more like 3–5 years. Depends on burn intensity, soil, rainfall; very hot or too-frequent burns delay recovery; moderate, patchy burns recover faster.

**How the reply became work:**
- Task 6: post-burn recovery modeled as R(t) = 1 − exp(−t/τ) with τ = 1.5 yr, giving R(3) = 0.86, R(5) = 0.97 (interval over which it holds: the expert's 2–5 yr judgment). Constraint (i): do not re-burn before T ≈ 3 yr (R(T) ≥ 0.8). Constraint (ii): vegetation closure V(T) = 1.06^T ≤ 1.30 (from the problem's 6%/year), giving T ≤ 4.3 yr, outer bound 7 yr (V = 1.50). Recommended burn rotation: 5–7 years, mosaic application, moderate patchy burns, never twice within 3 years, never more than ~7 years without fire.
- Task 1: the burning recommendation cites the 2–5 yr recovery and the too-frequent-burns warning as the reason for the 3-year minimum gap.

## Provenance note

All three replies are used as qualitative mechanisms and calibrated values (0.10 migration rate is the problem's own number; the expert's numbers are the 6%/yr from the problem and the 2–5 yr recovery from Exchange 3). No expert sentence appears in solution.json; each reply is converted to a parameter, constraint, or decision rule as recorded above.
