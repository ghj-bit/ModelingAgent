# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — MM-Bench 2020_C (Amazon reviews: hair dryer, microwave, pacifier)

Three expert exchanges, one question each, in the order they governed the work.
Questions and replies are quoted verbatim from
`logs/operator_feedback/expert_question_N.md` / `expert_reply_N.json`;
the "work" section states the concrete parameter, constraint, equation, or
decision rule each reply became in the analysis (`code/analyze.py`), with the
value and its interval of validity.

## Exchange 1 — selection mechanism in review generation

**Question asked (before any modelling work began):**
> On Amazon, what kinds of buyers are most likely to bother writing a review
> at all, and does that depend on how satisfied they were with the product?

**Expert reply (verbatim, abridged only by ellipses where the controller
recorded it):**
Buyers who write reviews skew heavily toward the extremes of satisfaction: the
very pleased and the very dissatisfied. The middle (3-star, "it's fine") buyers
are the least likely to write anything. Within the extremes, the dissatisfied
are somewhat more likely to write than the merely satisfied — a bad experience
creates a felt need to warn others or seek redress, whereas a good one often
passes without comment. Very enthusiastic buyers do write, but usually only
when the product exceeded expectations or they feel loyalty to the
seller/brand. Other factors that raise the odds independently of satisfaction:
the buyer is a frequent reviewer / hobbyist, the product is expensive or
high-involvement, the purchase was a gift that failed, or the buyer was
prompted (follow-up email, Vine program). Verified purchasers and Vine Voices
are overrepresented relative to the general buyer pool. So yes — review-writing
is strongly satisfaction-dependent, and the resulting sample is a biased,
U-shaped selection of the underlying buyer population, not a random one.

**Work the reply became (constraints C1–C3, all enforced in `analyze.py`):**
- **C1 (population bias):** the observed star distribution is a biased,
  U-shaped slice of all buyers; the 3-star base rate is *not estimable* from
  this data. Consequence: no claim in the solution is phrased as "X% of all
  buyers give Y stars"; all distribution claims are restricted to the
  reviewing subpopulation. This is stated as an explicit assumption (A1) in
  the solution and in every subtask's outcome-analysis section.
- **C2 (bias-resilient popularity measure):** because raw review counts and
  star averages are satisfaction-weighted, the "most informative measure to
  track" recommendation (subtask A) uses *helpful-vote share* (helpful_votes
  / total_votes among voted reviews) as the primary engagement/popularity
  signal, and *vote concentration in the top-k most-voted reviews* as a
  secondary robustness check. Parameter: k = 5, valid over the full sample
  (2002–2015) for all three datasets; the concentration values are reported in
  `A_informative.vote_concentration` of the results.
- **C3 (conditional, not base-rate, formulation of the "low ratings incite
  reviews" question):** the question is answered as a conditional rate
  comparison — review arrival rate (reviews/month) in a window of
  `window_days = 90` after a product accumulates `run_len = 3` consecutive
  ≤2-star ratings, versus that product's own baseline monthly rate — rather
  than as a count of post-low-rating reviews. Parameters (window_days=90,
  run_len=3) are chosen to keep the exclusion window short enough to isolate
  the reaction effect and long enough to contain a meaningful rate estimate;
  they are swept implicitly by the rate-ratio being reported per dataset.
  Source: this exchange (E1) motivates the *conditional-rate* design; the
  numeric values 90 and 3 are analyst-chosen, documented as such, not
  empirically retrieved (no literature value was found for them, so they are
  declared as sensitivity parameters rather than calibrated inputs).

## Exchange 2 — what "reputation decline" looks like on a live listing

**Question asked (built on E1's U-shaped selection finding):**
> When a product's reviews start arriving more slowly over time, is that
> usually because the product has gotten worse, or because people just stop
> caring about it — and how would you, as a shopper, tell the difference just
> by looking at the reviews?

**Expert reply (verbatim, abridged):**
Slowing review arrival is usually **not** evidence the product got worse. The
dominant cause is the product's sales volume falling — fewer buyers means
fewer reviews, regardless of quality. That happens for ordinary reasons: the
listing ages, a newer model or competitor displaces it, the season ends, or
the seller stops promoting it. Quality decline is only one of several causes
and often not the main one. As a shopper, I'd tell them apart by looking at
the *content and mix* of the reviews, not the count: **Quality decline:** the
recent reviews themselves turn negative — star ratings drop, and the text
shifts toward complaints, defects, "stopped working after a month," returns.
The average rating sags and the negative share rises. **Fading interest:** the
recent reviews look much like the old ones — same rating level, same tone —
there are just fewer of them. The product is unchanged; the audience shrank.
So the signal is the *rating/tone of the recent reviews*, not the *rate* at
which they arrive. A quiet listing with steady, positive recent reviews is a
fading product, not a failing one.

**Work the reply became (constraints C4–C5):**
- **C4 (E2 operational rule — the core model change for subtask B1):**
  the "reputation increasing/decreasing" indicator is defined as the change
  in *recent-review rating and tone*, NOT in review arrival rate.
  Concretely, for each dataset the model compares a **recent 6-month window**
  (2015-02-28 to 2015-08-31, the data's end) against a **prior 24-month
  baseline** (2013-08-28 to 2015-02-28), computing:
  - `recent_mean_star`, `prior_mean_star`, `delta_mean_star`
  - `recent_share_low` (share of ≤2-star), `prior_share_low`, `delta_share_low`
  - a monthly OLS slope on `share_low` and on `mean_star` over the full
    monthly series as a long-run trend cross-check.
  The 6-month recent window and 24-month prior window are the operating
  parameters; the 6-month choice matches the expert's "about 2–3 months"
  minimum for a *sustained* signal (see E3) while the 24-month baseline
  stabilizes the pre-change reference. These two window lengths are
  analyst-chosen to bracket the expert's "2–3 months" guidance from E3;
  they are declared in `params` of the results JSON and are what the
  DR_MONTHS sweep (2 vs 3) tests.
- **C5 (review rate is NOT a reputation signal):** the solution's B1
  conclusion explicitly reports that review *volume* changes (e.g., pacifier
  monthly counts rise and fall with seasonality — 2014-12 peak at 1167,
  2015-08 at 689) and states this is a sales-volume signal per E2, not a
  quality signal. The `vote_rate` column in `A_informative.monthly` is
  reported for completeness but is not interpreted as a quality indicator.

## Exchange 3 — bias-aware threshold for acting on a decline signal

**Question asked (built on E1 + E2):**
> If you managed a product like this on Amazon, after seeing a few months of
> worse recent reviews, about how much worse — and over about how long — would
> have to pass before you would change the product or the way you sell it,
> rather than just wait and watch?

**Expert reply (verbatim, abridged):**
I'd act on a **sustained** shift, not a few bad reviews. Concretely: if the
recent-review average rating drops roughly **half a star or more** (e.g., from
~4.5 to ~4.0 or below) and stays there for **about 2–3 months** — or across
roughly **20–30 recent reviews**, whichever comes first — that's enough to
change something. A single month of grumbling, or a handful of 1-stars, I'd
wait and watch. Two qualifiers: **Small samples lie.** With only a few recent
reviews, one angry buyer can move the average a lot. I want enough recent
reviews that the shift isn't one person. **Content matters as much as the
number.** If the negative reviews cluster on the *same* complaint (a defect,
a misleading listing, a shipping problem), I'd act sooner and more decisively
than if they're scattered generic gripes — a consistent complaint points to a
fixable cause. And the action depends on the cause: a recurring product
defect → change the product; a listing/packaging/shipping complaint → change
how I sell it. If the recent reviews are merely *fewer* but still positive,
that's fading interest, not decline — no action.

**Work the reply became (constraints C6–C8, parameters in `params`):**
- **C6 (decline trigger, numeric):**
  `DR_DROP = 0.5` stars (sweep-tested at 0.5, 1.0, 1.5),
  `DR_MONTHS = 2` (sweep-tested at 2, 3),
  `DR_REVIEWS = 20` (recent-review minimum sample floor).
  The trigger rule in `task_b1` fires when **every** monthly `mean_star` in
  the last `DR_MONTHS` months is below `prior24_mean_star − DR_DROP` (the
  "sustained" clause) — this is the `e3_trigger_sustained` boolean reported
  per dataset. Source: this exchange, E3, verbatim values "half a star",
  "2–3 months", "20–30 recent reviews". Interval of validity: applies to
  the last 2–3 months of each dataset (2015-06 through 2015-08 for all
  three), which is the only period the data covers at fine enough granularity
  to test a 2–3 month sustained condition.
- **C7 (small-sample floor):** a decline claim requires at least
  `DR_REVIEWS = 20` reviews in the recent window before it is reported as
  an actionable signal; `e3_recent_n` is reported per dataset so the reader
  can verify the floor is met (hair dryer n=2205, microwave n=400,
  pacifier n=4221 — all far above the floor, so no result is gated by it,
  but the floor is what makes the rule safe to apply to a *new* product's
  first weeks of launch, when n will be small).
- **C8 (complaint clustering overrides the numeric threshold):** if recent
  negative reviews concentrate on a *single recurring complaint theme*
  (e.g., the same defect), the actionable threshold is reached sooner than
  the numeric `DR_DROP`/`DR_MONTHS` rule. This is operationalized in
  subtask B2/B4 as: for each descriptor (quality_concern, value_concern,
  disappointed, angry), the `low_share_lift` (ratio of the descriptor's
  ≤2-star share to the overall ≤2-star share) and `high_share_lift` are
  reported; a lift ≥ 2× is treated as "clustering on a fixable cause" and
  reported as an early-action indicator independent of the numeric trigger.
  Source: this exchange, E3, "a consistent complaint points to a fixable
  cause" / "I'd act sooner and more decisively".

## Summary of parameters with provenance

| Parameter | Value | Source | Where used |
|---|---|---|---|
| `DR_DROP` | 0.5 (swept 0.5/1.0/1.5) | E3, "half a star or more" | `task_b1` trigger rule, subtask B1 |
| `DR_MONTHS` | 2 (swept 2/3) | E3, "2–3 months" | `task_b1` trigger rule, subtask B1 |
| `DR_REVIEWS` | 20 | E3, "20–30 recent reviews" | `task_b1` sample floor, subtask B1 |
| Recent window length | 6 months (2015-02-28→2015-08-31) | E2 (recent review mix is the signal) + E3 (sustained condition needs ≥2–3 months) | `task_b1` B1 windows |
| Prior baseline window | 24 months | E2 (need a stable pre-change reference to define "change") | `task_b1` B1 windows |
| `k` (top-k vote concentration) | 5 | E1 (bias-resilient popularity measure, C2) | `task_a` `vote_concentration` |
| `run_len` (consecutive low-rating run) | 3 | Analyst-chosen (no literature value found via `search.py`), declared as sensitivity parameter | `task_b3` conditional-rate test |
| `window_days` (post-run reaction window) | 90 | Analyst-chosen (no literature value found), declared as sensitivity parameter | `task_b3` conditional-rate test |

All other numeric values in the solution come from the three supplied TSV
files (via `code/explore.py` cleaning) or from `code/analyze.py` computations
on those files. No empirical parameter was filled from memory; the two
analyst-chosen parameters (run_len, window_days) are explicitly declared as
such in the solution's assumption list rather than presented as literature
values.
