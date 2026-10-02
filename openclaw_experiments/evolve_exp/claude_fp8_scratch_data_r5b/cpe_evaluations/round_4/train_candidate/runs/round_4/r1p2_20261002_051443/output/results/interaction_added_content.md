# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence

## Status summary

The consultation ran into a controller-side failure. All three exchanges were
attempted in the prescribed manner (question file written, then the single
foreground `wait_for_expert_reply.py` command). The human-expert API behind the
controller returned a runtime error and did not deliver a substantive reply for
any exchange. Per policy, an exchange that produces neither a parameter/constraint
nor an executed change "did not happen" — so this file records exactly that,
rather than prose about what the expert meant. No expert text was ever received
to incorporate, and nothing in `solution.json` is derived from an expert reply.

## Exchange 1 — Data provenance

- **Question (as written to `logs/operator_feedback/expert_question_1.md`):**
  "Are the reviews with zero helpfulness votes just ones nobody bothered to vote
  on, or does zero mean votes were never recorded?"
- **Command run:** the documented
  `wait_for_expert_reply.py --request expert_request_1.json --reply expert_reply_1.json --timeout 70 --exchanges 3`.
- **Controller outcome:** the controller wrote `expert_request_1.json` but the
  reply `expert_reply_1.json` was written with `{"ok": false, "error":
  "RuntimeError('Direct human-expert API call failed')"}`. The foreground command
  therefore exited with the consultation-failed message.
- **Effect on the work:** none — no parameter, constraint, or equation was
  supplied, so nothing was changed. The zero-vote field is handled instead by a
  data-driven rule that the analysis itself derives and states in
  `solution.json`: `total_votes == 0` is treated as *no vote cast* (the review
  was not up-voted by anyone), and the helpfulness rate is computed only over
  reviews with `total_votes > 0`. This is a stated modeling assumption grounded
  in the dataset, not an expert input.
- The command was run a second time after the failure to check for controller
  recovery; it returned the same `ok:false` reply, so no new information arrived.

## Exchange 2 — Structural assumption (rating stability)

- **Question (as written to `expert_question_2.md`):**
  "In your experience, does a product's rating level stay fairly steady, or can
  it flip quickly in a short span?"
- **Command run:** the documented
  `wait_for_expert_reply.py --request expert_request_2.json --reply expert_reply_2.json --timeout 70 --exchanges 3`.
- **Controller outcome:** the controller never created `expert_request_2.json`;
  the command timed out at 70 s. No reply file was produced.
- **Effect on the work:** none. The rating-stability assumption is tested
  directly on the data instead: a per-product 2-year rolling mean-star trend and
  a 12-month review-growth test are computed and reported in `solution.json`,
  which is a reproducible substitute for the intended expert validation.

## Exchange 3 — Interpretation context

- **Question (as written to `expert_question_3.md`):**
  "When you watch a new product's early reviews, how few good reviews would you
  trust before calling it a winner or a dud?"
- **Command run:** the documented
  `wait_for_expert_reply.py --request expert_request_3.json --reply expert_reply_3.json --timeout 70 --exchanges 3`.
- **Controller outcome:** the controller never created `expert_request_3.json`;
  the command timed out at 70 s. No reply file was produced.
- **Effect on the work:** the decision-relevant threshold is set by the data
  instead: the success/failure composite is evaluated only for products with at
  least 5 reviews, and the analysis reports how many products meet that bar. The
  choice of 5 is stated as an assumption and is swept so the recommendation does
  not hinge on it.
