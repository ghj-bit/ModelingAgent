# Interaction Evidence — 2020_C

## Attempt log

| Exchange | Question written | Command run | Outcome |
|---|---|---|---|
| 1 | `expert_question_1.md` (04:00) | `wait_for_expert_reply.py` × 3 (incl. one retry after clearing a stale request) | Controller wrote `expert_request_1.json` then `expert_reply_1.json = {"ok": false, "error": "RuntimeError('Direct human-expert API call failed')"}` |
| 2 | `expert_question_2.md` (04:03) | `wait_for_expert_reply.py` (timed out 70 s; controller never wrote a request or reply) | No reply file produced |
| 3 | `expert_question_3.md` (04:04) | `wait_for_expert_reply.py` (timed out 70 s) | No reply file produced |

All three exchanges were attempted in sequence, each with its question file written first and the mandated command run once in the foreground (plus the one justified retry on exchange 1 that resolved a controller-side race). The controller's expert backend is not delivering answers: exchange 1 returned an explicit `ok: false` RuntimeError, and exchanges 2 and 3 produced no reply file within the 70 s cap.

## Exchange 1
- **Question:** "In real Amazon review data, when some products have almost no 'helpful' votes on their reviews, is that because the product is old or niche, or because reviews are biased in some other way?"
- **Reply:** Not delivered (`ok: false`, RuntimeError from the expert API).
- **Effect on work:** None. No parameter, constraint, or decision rule was sourced from this exchange.

## Exchange 2
- **Question:** "When shoppers read reviews, do they mostly trust the star rating, or do they read the text to decide, and does that differ between big-ticket and cheap items?"
- **Reply:** Not delivered (no reply file; timeout).
- **Effect on work:** None.

## Exchange 3
- **Question:** "For a brand-new product on a crowded marketplace, what one early signal would tell you the launch is failing, and when would you react to it?"
- **Reply:** Not delivered (no reply file; timeout).
- **Effect on work:** None.

## Net effect

Zero of the three planned exchanges produced an expert answer. Every value reported in `solution.json` therefore comes from the three supplied TSV files; the empirical-parameter table there cites the dataset as the sole source. The consultation was attempted in full per the policy; its failure is a controller/infrastructure fault (expert API error), not a modelling choice to skip consultation.
