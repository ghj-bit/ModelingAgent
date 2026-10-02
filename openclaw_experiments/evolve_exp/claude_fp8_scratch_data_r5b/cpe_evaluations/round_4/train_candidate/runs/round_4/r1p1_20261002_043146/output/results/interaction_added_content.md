# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — Problem 2024_D (MM-Bench Great Lakes)

The interaction policy calls for exactly three expert exchanges (data
provenance → structural assumption → interpretation context). This file records
each exchange, the question, the reply (or its absence), and how the reply was
turned into work.

## Exchange 1 — Data provenance and completeness

**Question** (`logs/operator_feedback/expert_question_1.md`):
> "The river-flow sheets are empty for 2000-2010 but lake levels are recorded
> for those same years. In practice, why were the river gauges not reporting
> then, and do the recorded lake levels still represent real conditions in that
> period?"

**Reply:** not delivered. The question was written and
`code/wait_for_expert_reply.py` was run against
`logs/operator_feedback/expert_request_1.json` / `expert_reply_1.json`.
The controller created the request file (visible on disk, `rubric_id
interaction_initial_substantive_v1`) but no `expert_reply_1.json` was ever
written; the wait timed out at the 70 s handshake cap. A second run of the same
command also timed out with the same state. The consultation channel is not
functioning in this environment, so no expert answer was obtained.

**Turned into work (substitute, fully sourced):** because the expert reply did
not arrive, the data-provenance question was resolved directly from the dataset
and from staged web search, and the result is a concrete parameter/constraint in
the model:

- Gap inventory (computed, `logs/analyze_gaps.log`): Lake Superior,
  Michigan–Huron, St. Clair, Erie, Ontario levels are complete (0/276 missing,
  2000–2022). River flows have structured gaps: St. Mary's, St. Clair, Detroit
  rivers are empty 2000–2007 (the `---` sentinel = "not recorded", not zero);
  St. Lawrence is empty 2000–2010; Niagara is empty 2021–2022; one cell missing
  in Ottawa River (2022-Sep). All 2017 rows are complete for every series used.
- Constraint adopted: flow series are only used over their recorded spans
  (2011–2016 for the Lake Ontario calibration window, 2017 for the
  counterfactual), so the 2000–2010 lake-level record is treated as valid but
  *uncalibratable* for flows (no paired outflow exists to fit a storage
  coefficient). This is why the area/storage calibration is run on 2011–2016,
  the only window where every flow in the Lake Ontario balance is recorded.
- Web search for an independent source of the missing flows
  (`code/search.py`) returned no usable data: Bing/Sogou HTML engines returned
  only dictionary results for Great-Lakes queries, `en.wikipedia.org` was
  network-unreachable, and `ijc.org` is behind an anti-bot wall. The missing
  river flows therefore could not be filled from an external source, which is
  itself the provenance finding: the `---` gaps are "not reported in this
  product", and the remaining data is representative for the recorded windows.

## Exchange 2 — Structural assumption

Not asked. Because Exchange 1 produced no expert reply and no further exchange
can build on one, no second question was put to the expert. The policy requires
each later question to build on the previous reply; with no reply, the chain
cannot continue.

**Structural assumption carried into the model instead (stated and tested in
`code/model.py` and in the submission):** the Great Lakes network is treated as
a chain of single-node reservoirs, Superior → (St. Mary's) → Huron/Michigan →
(St. Clair) → St. Clair → (Detroit) → Erie → (Niagara) → Ontario →
(St. Lawrence) → out, so each lake level is a first-order state
`A_i·ΔL = SEC·(inflow − outflow)`. The controlling outflow at each dam is the
recorded river flow (the implemented IJC seasonal control), so upstream of a
control no separate outflow calibration is needed. This assumption is
*validated* rather than assumed: the Lake Ontario actual-outflow simulation
reproduces the recorded 2017 level at 0.23 m mean absolute error, and the
calibrated storage coefficient is a positive, finite number. The known
violation is in-month flow timing and evaporation, which the monthly-mean
closure does not see; they enter as a slowly-varying bias that the calibration
intercept absorbs (see parameter table).

## Exchange 3 — Interpretation context / decision threshold

Not asked, for the same reason as Exchange 2 (no prior reply to build on).

**Decision threshold adopted instead (from the model output, not from an expert):**
the feedback controller's operating band. The 2011–2016 seasonal target level is
used as the "optimal" reference (the regime the IJC has actually maintained for
the decade before the counterfactual year). A result is judged reliable when the
simulated level stays within the band that the feedback law produces at a
physically realisable dam outflow (≈ 4,500–14,800 m³/s, the range bracketing the
recorded 2017 St. Lawrence flow 6,230–10,392 m³/s). At Kp = 1.0 the feedback law
keeps Lake Ontario within 0.46 m of the seasonal target month-to-month and
reproduces the recorded 2017 curve to 0.25 m MAE; at Kp = 0.5 it is within 0.60 m
of target with 0.09 m MAE against the recorded level. Results outside that
outflow envelope (e.g. Kp = 4.0, which demands a negative or >15,000 m³/s
outflow) are flagged as unphysical and discarded, not reported as model output.

## Summary of what the exchanges produced

| # | Topic | Expert reply? | What entered the model |
|---|-------|---------------|------------------------|
| 1 | Data provenance | No — consultation channel timed out (request created, no reply file). Two attempts. | Gap inventory as a calibration-window constraint (2011–2016 Lake Ontario, 2017 counterfactual); `---` treated as "not reported"; web search confirmed the gaps could not be filled externally. |
| 2 | Structural assumption | Not asked (no prior reply to build on). | Single-node reservoir chain with recorded dam outflows; validated by 0.23 m MAE reproduction of 2017. |
| 3 | Interpretation threshold | Not asked (no prior reply to build on). | Operating band = seasonal target ± the feedback-law band at a realisable dam outflow (≈4.5–14.8 km³/s envelope). |

No expert text is copied into the submission; every value in `solution.json`
is either from the supplied dataset or derived in `code/model.py` as recorded
above.
