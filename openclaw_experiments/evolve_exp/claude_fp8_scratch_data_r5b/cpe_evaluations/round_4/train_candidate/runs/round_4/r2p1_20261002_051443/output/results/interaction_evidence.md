# Interaction Evidence — Problem 2024_D (Great Lakes network control model)

## Exchange 1 (data provenance)
**Question (expert_question_1.md):** The river flow data for 2000-2008 is blank
("---"). Does that mean these rivers had no measured flow records for those
years, or that the records existed but were simply left out? Can the later
years (2009-2022) be treated as representative of normal lake and river
behaviour?

**Reply:** none. The expert consultation API was unreachable
(`RuntimeError('Direct human-expert API call failed')` / timeout on two
attempts; the sibling run `r2p1_20261002_032758` of the same batch shows the
identical failure, so it is environmental). See `logs/expert_api_status.md`.

**Effect on work:** none from the expert. The data-handling decision is taken
from the data itself and recorded as an assumption: 2000-2008 flows are treated
as unmeasured, not as zero; where the model needs them it uses the seasonal
profile (per-month mean over the complete years 2009-2021), and the
2000-2008 portion of every result is reported as "flows unmeasured" rather than
as a quantitative statement.

## Exchange 2 (structural assumption)
**Question (expert_question_2.md):** If the lake's inflow and outflow stay
roughly steady over a month, would you expect the lake's water level to be
about the same at the start and end of that month? What in real lake life would
break that?

**Reply:** none (same API failure).

**Effect on work:** the structural assumption — the lake water balance
dS/dt = Q_in − Q_out is closed to within a few hundred m3/s at the monthly
scale, so lake level responds to net flow month-to-month without unmodelled
storage terms — is instead validated against the data: the annual closure
residual (net observed flow minus dS from the level-area curve) is
0.021 km3/yr mean / 0.028 km3/yr rms for Ontario 2009-2021, 0.003 km3/yr over
the complete-St. Lawrence window 2012-2022 (≈0.1% of annual throughput of
~7000 km3). That is the evidence the assumption holds; it is reported as such,
not as expert endorsement.

## Exchange 3 (interpretation threshold)
**Question (expert_question_3.md):** When lake levels swing a couple of feet,
which group suffers most first — the people whose homes flood at the shore, or
the shipping companies that need deep water — and roughly how big a swing
starts to hurt each?

**Reply:** none (same API failure).

**Effect on work:** the decision-relevant threshold is therefore set from the
IJC operating ranges rather than from the expert: for each lake the
shipping/shoreline band (e.g. Ontario 74.30-75.65 m, Erie 174.00-175.10 m) is
the accept/reject criterion, and the 2017 comparison is stated as
"simulated inside band: X/12 months, observed Y/12", with the stakeholder
direction (flooding = above band, shipping = below band) named per month.

## Summary
All three exchanges were attempted in the required order, each question written
to `logs/operator_feedback/expert_question_N.md` and the handshake command run
once in the foreground per the protocol. The expert API failed in all three;
the model therefore contains no expert-supplied values. Every empirical value
used is either from the task dataset (2000-2022 levels/flows) or listed with a
full reference in the `mathematical_modeling_process` parameter table of
`solution.json`. No reply text appears anywhere in the submission.
