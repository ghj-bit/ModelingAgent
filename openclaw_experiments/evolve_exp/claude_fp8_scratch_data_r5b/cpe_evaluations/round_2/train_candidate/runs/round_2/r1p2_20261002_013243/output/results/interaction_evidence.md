# Expert Interaction Evidence — MCM 2019_C (Opioid Crisis, MM-Bench 2019_C)

Three exchanges, one question each. Each reply was converted into a model
component before the next exchange. The expert's words are quoted here for the
evidence record only; the submission (solution.json) restates the substance in
the model's own formulation and contains no verbatim exchange text.

## Exchange 1 — Dominant operational mechanism

**Question (expert_question_1.md):**
"When drug seizures appear in many nearby counties at once, what does a
veteran of drug enforcement actually conclude first: one source spreading
outward, or many independent suppliers arriving separately?"

**Reply (summary):** The default prior is *one source spreading outward*
through existing social/transport networks, so connected counties light up
together; independent suppliers produce staggered, uncoordinated timing. The
judgment flips toward independent arrivals or a common external driver when
counties show different substance signatures, share no transport corridor, or
the simultaneity is explained by a regional enforcement/reporting change.

**How it changed the work:** This fixed the structural form of the Part 1 model.
Rather than assuming every county is an independent Poisson source, the model
treats each state as a single saturating compartment in which one (or a few)
seeding nodes recruit the rest of the county network — a within-state diffusion
process. The staggered cross-state onsets (OH 2013 → PA 2014 → KY 2014-15 → VA
2014-16, WV much later and smaller) are read as the signature of *independent
arrivals* across state lines rather than one national wave, so the inter-state
coupling is kept weak and the per-state curves are fit independently. The
outbreak detector (Part 1 origin identification) uses "does the elevation
persist and propagate to neighbours" as the real-signal test, directly from this
reply.

## Exchange 2 — Operational boundary / threshold

**Question (expert_question_2.md):**
"When one county's drug problem gets very large, what stops it from growing
much further?"

**Reply (summary):** The binding constraint is the market's *carrying
capacity*, not the supply of drugs. Growth stops when recruitment of the
reachable susceptible pool is exhausted and removal channels catch up:
enforcement/incarceration, harm-driven attrition (overdose, incarceration,
recovery, aging out), supply-side friction (rising price, fragmented
distribution), and treatment/diversion capacity (methadone, buprenorphine,
naloxone, PDMP/prescribing controls).

**How it changed the work:** This is the justification for modelling growth as
a *logistic* (saturation-capped) process rather than exponential. Each
(state, substance) series is fit to A(t) = K / (1 + z e^{-r(t-t0)}), where K is
the saturation ceiling (the carrying capacity) and r the intrinsic growth rate.
The ceiling K is what bounds the projection; it is what makes the 2018-2026
forecast plateau instead of diverge. It also defines the two intervention
levers in Part 3: an enforcement/treatment intensity tau that scales the growth
rate r downward, and a capacity-intensity kappa that scales the ceiling K
downward (shrinking the reachable susceptible pool). The interval over which
this holds is the 2010-2017 observation window and the near-term projection,
i.e. while the same removal channels (enforcement, treatment, attrition) remain
in place.

## Exchange 3 — Interpretation of uncertainty / bias

**Question (expert_question_3.md):**
"What makes a big jump in a county's drug test results a real outbreak instead
of a one-off spike?"

**Reply (summary):** A real outbreak is distinguished by *persistence and
propagation*, not the size of the jump: counts stay above baseline for multiple
consecutive periods; the elevated county is followed by rises in adjacent or
socially/transport-linked counties; the same substance signature appears across
the affected counties; and the jump is corroborated by more than one data
stream rather than a single reporting/lab/administrative change.

**How it changed the work:** This became the validation logic for interpreting
Part 1 results and for the Part 3 strategy. (a) Origin identification requires
a county's elevation to *persist* (multiple consecutive years above baseline)
and to be *followed by neighbours*, not a single-year spike — this is why the
leading counties are judged on their multi-year 2014-2017 cumulative load and
their earlier onset, not on a single peak year. (b) It defines the model's
bias analysis: a one-off county spike in the raw NFLIS counts is a false
positive (a reporting/lab artifact or a single large seizure) and must not be
read as a new source; conversely the model's state-level smoothing and the
requirement that a trend persist across periods before it is reported as a
"concern" is the guard against exactly that artifact. (c) For Part 3, the
strategy's success metric is framed as a *sustained* reduction in the projected
trajectory over the whole 2018-2026 window (a persistent effect), not a
one-year dip, mirroring the persistence criterion.

---

## Provenance of parameters

No parameter in the model was taken from the expert as a number. The expert
supplied qualitative structure (diffusion mechanism, saturation ceiling,
persistence-based signal test). All quantitative values are either (i) fit to
the supplied NFLIS/ACS data, or (ii) in the solution.json parameter table with
a full reference (a DOI) for the one external empirical magnitude used to
anchor the treatment channel.
