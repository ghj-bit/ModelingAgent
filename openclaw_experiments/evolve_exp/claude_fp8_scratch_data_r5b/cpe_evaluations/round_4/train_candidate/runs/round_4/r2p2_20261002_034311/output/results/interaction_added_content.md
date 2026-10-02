# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — 2020_C

## Exchange 1 (Data Provenance)

- Question written to `logs/operator_feedback/expert_question_1.md`: asked the
  expert what shoppers typically infer when a review shows zero total
  helpfulness votes (nobody read it / nobody found it useful / product page is
  new), because 33–72% of reviews in the three files have `total_votes = 0` and
  helpfulness-based measures must be interpreted against that baseline.
- `wait_for_expert_reply.py` was run once against
  `expert_request_1.json` / `expert_reply_1.json`.
- Result: the controller wrote `expert_reply_1.json` with
  `{"ok": false, "error": "RuntimeError('Direct human-expert API call
  failed')"}`. **The expert consultation failed; no substantive answer was
  received.**
- Effect on the work: none of the expert's judgments could be incorporated.
  All calibration was instead done from the supplied data itself. Where the
  zero-vote baseline matters (helpfulness measures), the analysis restricted
  helpfulness statistics to the voted subset (42% hair dryer, 33% microwave,
  28% pacifier of reviews) and reported the zero-vote share explicitly, so no
  claim depends on an unverifiable interpretation of the missing votes.

## Exchanges 2 and 3

Not executed: the policy requires each question to build on the previous
reply, and Exchange 1 returned no answer. The fixed 3-exchange budget was
consumed by the failed call; no further expert questions were sent.

All parameters in `solution.json` are therefore either computed from the three
supplied TSV files or are standard, data-internal quantities (no external
values were needed, so no staged-helper retrieval was required).
