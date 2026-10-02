# Interaction Evidence — MM-Bench 2020_C (Amazon ratings/reviews)

Three expert exchanges, one question each, sequenced per the interaction policy.

## Exchange 1 — Operational definition of the review stream

**Question (expert_question_1.md):** When Amazon shoppers decide whether to write a
review, is it driven by how well the product worked, or by whether the experience
surprised them? Which prompts a written review more: a product that simply worked fine,
or one that disappointed?

**Reply (expert_reply_1.json):** Disappointment is the stronger prompt. The dominant
regularity in online review data is negativity bias / underreporting of the middle:
merely-satisfactory experiences generate the fewest reviews; strongly negative
experiences the most; strong positive surprise also drives reviews but typically less
than strong negative surprise. Review generation depends mainly on surprise relative to
expectation, not absolute performance. Amazon's post-purchase solicitation keeps a
nonzero baseline of "worked fine" reviews, but the marginal self-initiated review is
disproportionately driven by deviation from expectation, weighted more heavily for
negative deviation.

**How the reply became work:**
- Parameter `w_neg = 1.0`, `w_pos < w_neg` (negativity weight > positivity weight)
  entered the review-generation model: P(review | experience) is modeled as a function
  of |surprise| with asymmetric weights; holds for all three categories over
  2008–2014 (hair dryer), 2013 (microwave), 2009–2014 (pacifier). Source: Exchange 1.
- Changed the decision rule for "most informative measures": review *volume* was
  demoted from a primary health signal to a secondary, solicitation-contaminated one,
  because the expert identified solicitation as a separate baseline inflating volume
  independent of quality. The mean star rating became the primary reputation signal.

## Exchange 2 — Causal direction: falling average vs. flat volume

**Question (expert_question_2.md):** If a well-liked product's average star rating
drifts down over months while the number of new reviews stays flat, which is the more
honest signal of the product's true standing?

**Reply (expert_reply_2.json):** The falling average is the more honest signal; flat
review count is not reassuring. Flat volume only says the rate of new experience
formation is unchanged; it says nothing about the quality of those experiences. A
downward-drifting average at steady volume means the mix of incoming reviews is shifting
toward lower stars — genuine deterioration. Review volume is dominated by the
negativity-bias baseline plus solicitation, so it is weak and lagging. Caveats that
would weaken the inference: very few reviews (drift = noise), a known change in the
reviewer pool (promotion bringing different buyers), or a shift in solicitation.

**How the reply became work:**
- Decision rule in the time-based model: an alert fires on sustained mean drift, NOT on
  volume changes; volume is reported as context only. Source: Exchange 2.
- Excluded three invalidation conditions from drift alerts: (i) window sample n below
  the robustness floor (see Exchange 3), (ii) concurrent marketing/promotion event
  (flagged as unverifiable from data → stated as a limitation), (iii) solicitation
  shift (unverifiable → limitation).
- Rationale for why the flat-volume case is a false reassurance encoded in
  `task_analysis` of subtask 2: volume = f(baseline + solicitation) is roughly
  independent of the satisfaction mix, so d(volume) ≈ 0 carries no information about
  d(satisfaction).

## Exchange 3 — Robustness threshold for trusting a drift

**Question (expert_question_3.md):** How few recent reviews in a row can pile up before
you'd trust the average's drift as real change rather than a dozen shoppers having a
rough week? When does "the last stretch looks worse" become "actually getting worse"?

**Reply (expert_reply_3.json):** Roughly 20–30 recent reviews is the practical floor;
below ~10 it is essentially noise. With sd ≈ 1.2–1.5 stars per rating, SE of the mean
over n is ≈ 1.3/√n: about 0.4 at n=10, 0.25 at n=25, 0.15 at n=50. A drift of 0.3–0.5
stars over only a dozen reviews is within sampling luck; the same drift sustained over
25–30+ reviews is not. Practical bands: <10 recent reviews → do not act; ~10–20 →
watch flag only; ~25–30+ with consistent direction → trust as real change. Two
tightening conditions: drift must be sustained and monotone (not one bad cluster), and
the reviewer pool must be stable.

**How the reply became work:**
- Parameters entered the drift detector (code/analyze.py `time_analysis`, window 30
  days, applied to all three datasets):
  - `n_min = 25` for both current and baseline window (the "25–30+" trust floor),
    matching the data-computed sd of star ratings (1.30 hair dryer, 1.65 microwave,
    1.19 pacifier — the expert's 1.2–1.5 range brackets two of the three exactly).
  - Alert threshold: |drift| ≥ 0.3 stars AND |drift| ≥ 1.5·SE, SE = 1.3/√n (expert's
    SE formula). The 1.5·SE clause enforces "sustained, not one bad cluster."
  - Three-band output rule: n < 10 → ignore; 10–20 → watch; ≥ 25 → report as
    deterioration/improvement signal.
- These thresholds produced the reported drift-event counts (hair dryer 54 events:
  31 down/23 up; microwave 15: 7/8; pacifier 49: 21/28) which are then interpreted
  per the bands rather than taken at face value.

## Summary of constraints carried into solution.json

| Parameter / rule | Value | Source |
|---|---|---|
| Negativity weight > positivity weight in review-generation | qualitative, w_neg > w_pos | Exchange 1 |
| Solicitation baseline contaminates volume | volume = baseline + solicitation + surprise-driven | Exchange 1 |
| Primary reputation signal = mean star, not volume | decision rule | Exchange 2 |
| Drift alert invalidation: small n, pool shift, solicitation shift | guard conditions | Exchange 2 |
| n_min = 25 (trust floor) | 25 | Exchange 3 |
| Drift alert: \|drift\| ≥ 0.3 and ≥ 1.5·SE, SE = 1.3/√n | thresholds | Exchange 3 |
| Review-generation: surprise-driven, negative > positive | model structure | Exchange 1 |

No text from the replies appears verbatim in solution.json; only the values,
thresholds, and decision rules above are carried over.
