# Interaction Evidence — MM-Bench 2020_C

Three exchanges were attempted, one per round, in the order the policy prescribes
(question N written before the work it governs; each question grounded in the
previous exchange's status). The controller created the request for exchange 1
but the expert backend failed; no answer was ever received in any round.

## Exchange 1 — data provenance and completeness
- **Question** (`expert_question_1.md`): The microwave and pacifier data stop at
  8/31/2015 while the hair-dryer data also ends the same day. Were all three sets
  cut off at the same date by the data provider, or does one category's file stop
  early?
- **Reply:** none. `expert_reply_1.json` = `{"ok": false, "error": "RuntimeError('Direct human-expert API call failed')"}`.
- **Effect on work:** the reply was not an input to the model. The gap was instead
  resolved directly from the data (a permitted, self-contained step): all three
  files end exactly on 2015-08-31 and their review volumes grow roughly
  exponentially through 2015 (hair dryer 3,143 reviews in 2015; pacifier 5,796;
  microwave 549), with no per-category early stop. I therefore model every file
  as a common 2015-08-31 cutoff of an otherwise growing review stream, and treat
  pre-2012 periods (sparse, e.g. 8 hair-dryer reviews in 2002) as low-power
  baseline rather than representative steady state. This becomes Assumption A3
  and the window choice (recent-window statistics reported alongside full-span).

## Exchange 2 — what helpful-vote counts mean
- **Question** (`expert_question_2.md`): Customers on Amazon often click
  "helpful" on a review without first reading the full review body. In your
  experience with this kind of marketplace data, would you expect the
  helpful-vote counts to reflect how carefully shoppers read reviews, or mostly
  which reviews are easiest to spot and skim?
- **Reply:** none — the controller produced no `expert_request_2.json` /
  `expert_reply_2.json` within the 70 s handshake (the expert channel had already
  failed in exchange 1). No retry was permitted by the controller's file
  discipline, so the exchange produced no model input.
- **Effect on work:** none from the expert. I recorded the question and treated
  the helpfulness signal's meaning as an unresolved interpretive caveat: the
  analysis therefore does NOT use `total_votes`/`helpful_votes` as a primary
  quality signal (they are reported as secondary, with a visibility-confounding
  caveat), and the primary success signal is built from star ratings plus text
  content, where provenance is unambiguous.

## Exchange 3 — interpretation threshold (early vs established products)
- **Question** (`expert_question_3.md`): When a new product gets its first few
  reviews online, do shoppers tend to judge it more harshly, more leniently, or
  about the same as a well-established product with hundreds of reviews?
- **Reply:** none — same channel failure; no request/reply files were created.
  No model input resulted from this exchange.
- **Effect on work:** none from the expert. The interpretation threshold was set
  from the data instead: a product's rolling reputation is reported only once it
  has >= 8 reviews spanning >= 6 months (the per-product trend cohort sizes are
  122 / 42 / 280 for hair dryer / microwave / pacifier), which is the point at
  which a slope estimate is not dominated by a handful of early ratings.

## Honesty note
Because the expert API failed in all three rounds, no expert value, constraint,
or equation enters the model. Every quantitative input in `solution.json` comes
from the task's own three TSV files. The three questions above are recorded so
the consultation is auditable; the evidence of the channel failure is the
controller's own `expert_reply_1.json` (ok=false) and the absence of
`expert_request_2/3.json`. No reply was ever copied into the submission.
