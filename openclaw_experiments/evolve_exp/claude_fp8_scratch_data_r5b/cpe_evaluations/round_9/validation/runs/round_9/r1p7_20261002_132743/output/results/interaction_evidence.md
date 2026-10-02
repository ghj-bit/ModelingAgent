# Expert Interaction Evidence — Problem 2023_Y (Sailboat Pricing)

Three exchanges, one question each. Files: `logs/operator_feedback/expert_question_N.md`,
`expert_request_N.json`, `expert_reply_N.json`. The replies below are the expert's input;
only the values and constraints they support were carried into the model. No reply text
was copied into `solution.json`.

## Exchange 1 — Structural validity (independence of listings)

**Question:** Is it reasonable to treat each listing as an independent price observation,
or do listings for the same boat model from the same year cluster together because their
prices were set off one common reference price?

**Reply (summary):** Rejecting independence. Sellers/brokers anchor to shared references
(manufacturer list price, model book value, each other's asking prices), so same
make/variant/year listings are correlated. The effective sample size is the number of
distinct make/variant/year groups, not the row count; standard errors under independence
would be too narrow. Clustering is strongest within region and within model-year.

**How it changed the work:** The model's covariance was changed from the OLS formula to a
cluster-robust (Huber-White) sandwich with cluster = make/variant/year
(`code/model.py: ols`). Mono has 699 clusters vs 2336 rows; cat 189 vs 1073. All
standard errors, t-statistics, and the "significant at any level" claims in
`solution.json` are the cluster-robust ones. This is the parameter/constraint the reply
supplied: *inference unit = make/variant/year group*.

## Exchange 2 — Bias mechanism and validation design (asking vs transaction price)

**Question:** Given listings are asking prices, does survivorship (unsold boats stay
listed, quick sales drop out) mean December asking prices tend to sit above, below, or
around the price a boat would actually fetch, and by roughly how much?

**Reply (summary):** Asking prices sit **above** transaction prices. Sellers post
aspirational prices and negotiate down; overpriced boats linger in the snapshot. Typical
negotiated discount is ~5–15%, larger for long-listed boats. So predicted "price" is an
asking-price estimate and should be labeled as such.

**How it changed the work:** A discount parameter d was introduced: transaction estimate
P_t = (1-d)*P_a, with d = 0.10 (central), interval [0.05, 0.15], sourced to this exchange.
This is used to report a transaction-price RMSE (mono ~11.8%, cat ~7.7% at d=0.10)
alongside the asking-price RMSE, and to frame every quoted figure in `solution.json` as an
asking-price estimate. The validation constraint — that level coefficients are
asking-price coefficients — is carried into the Subproblem 1 and 4 analysis.

## Exchange 3 — Decision-relevant uncertainty threshold

**Question:** For a Hong Kong broker deciding whether to list a used sailboat, how large
must the model's price-estimate error be before it becomes useless in practice?

**Reply (summary):** Useful while typical error (RMSE) is within ~±5–10% of price (same
order as the negotiation band); useless beyond ~±15–20%. Decision boundary ~10–15%:
below it, act on the estimate; above it, use the model only for coarse ranking.

**How it changed the work:** The 10% (useful) / 15% (useless) thresholds became the
interpretation rule for every precision figure. Concretely: the catamaran transaction
RMSE (~7.7%) is reported as decision-ready (inside the 5–10% band); the monohull
transaction RMSE (~11.8%) is reported as just outside it, so it is presented as a price
band / directional guidance rather than a single quotable number. This threshold is the
framing of Subproblems 1, 4, and 5 in `solution.json`.

## Traceability of carried values

| Carried value / constraint | Interval | Source exchange | Where used in model |
|---|---|---|---|
| Inference unit = make/variant/year (cluster-robust SE) | — | Exchange 1 | `ols()` covariance in `code/model.py` |
| Asking→transaction discount d | [0.05, 0.15], central 0.10 | Exchange 2 | Transaction RMSE; "asking-price estimate" labeling |
| Decision threshold: useful ≤ ~10%, useless > ~15% | [5%, 20%] | Exchange 3 | Interpretation of precision in Subtasks 1, 4, 5 |

No expert sentence, phrase, or structure was copied into the submission; only the values
and constraints above, restated in the model's own formulation, are present.
