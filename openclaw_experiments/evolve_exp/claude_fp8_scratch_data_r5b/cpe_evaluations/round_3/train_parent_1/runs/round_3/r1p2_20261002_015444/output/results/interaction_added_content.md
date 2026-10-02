# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — MCM 2017 C (2017_C)

Three expert exchanges, one question each. Each reply was turned into a model
parameter or decision rule before the next exchange; the value (not the expert's
sentences) is what enters the model.

## Exchange 1 — peak-to-average traffic ratio

**Question:** On a busy Seattle-area freeway, how many times larger is the
rush-hour hourly car count than a typical non-peak hour? Rough multiple.

**Reply (summarized):** Peak is roughly 2–4× off-peak, central ~3×. Peak-hour
volumes are about 8–12% of the daily total; off-peak daytime hours ~3–4% each.
Empirical judgment. On already-congested corridors the peak/off-peak ratio is
smaller because demand is capped by capacity.

**Turned into work:** The data give *average daily* traffic (ADTT), but the model
needs a peak-hour demand. Used `peak_frac = 0.10` (central of the 8–12% peak
fraction) to convert ADTT → peak-hour veh/h: `q = ADTT × 0.10`. The "capped by
capacity" note is reflected in the result that these corridors are saturated at
peak (see outcomes). Interval of validity: urban freeway peak hour, 2015 volumes.
This governed the entire capacity model.

## Exchange 2 — willingness to shift departure time

**Question:** Commuters currently stuck in rush-hour gridlock: would they
willingly drive at off-peak hours if a fast dedicated self-driving lane were
available? Roughly how many?

**Reply (summarized):** Only a modest minority. Most peak trips are
schedule-locked. Congestion-pricing / flexible-work evidence: about 10–25% of
peak-period travelers would shift departure time if given a genuinely faster,
reliable option; higher where hours are flexible, lower where rigid. Order of
1 in 10 to 1 in 4. Empirical judgment.

**Turned into work:** This is a *demand-suppression* lever, not just capacity.
Modeled a policy in which a fast, reliable AV option induces a fraction
`shift_frac` of peak demand to move off-peak, lowering peak demand:
`q_eff = q × (1 − shift_frac × p)` (the inducement scales with AV availability p).
Set `shift_frac = 0.18` (midpoint of 10–25%), interval [0.10, 0.25]. Swept over
the full interval to show sensitivity. Applied to the dedicated-lane /
managed-lane policy scenario.

## Exchange 3 — effect of a dedicated lane on total throughput

**Question:** Taking a general-use highway lane and making it self-driving-
car-only: in your experience, would that usually reduce total traffic
throughput, hold it steady, or increase it?

**Reply (summarized):** Usually reduce total throughput near-term, often
persistently. A dedicated lane's throughput is capped by the share of vehicles
eligible to use it; at 10–50% penetration it is underused while the remaining
general lanes absorb nearly all demand, so total throughput falls. Holds steady
or improves only at high penetration (roughly 50%+, reliably near 90%), and only
if AVs actually achieve shorter headways. Reduce at low penetration, neutral in
the middle, potentially increase at high penetration. Empirical judgment.

**Turned into work:** Directly validated the dedicated-lane computation in the
model (one lane reserved to AV, rest general-use). The model's dedicated-lane
scenario reproduces exactly this signature: at p=0.10 and p=0.50 the dedicated
arrangement is more oversaturated than pooled operation (throughput falls), and
it only approaches/improves at p=0.90. This is used as the decision rule for the
"should lanes be dedicated?" question: **do not dedicate lanes below ~50%
penetration**; only consider it near 90% and contingent on realized headway
gains.

---

All three replies are empirical judgments (not precise figures); the values used
are the central estimates, with the stated intervals carried as sensitivity
bounds. No expert text is reproduced in the submission.
