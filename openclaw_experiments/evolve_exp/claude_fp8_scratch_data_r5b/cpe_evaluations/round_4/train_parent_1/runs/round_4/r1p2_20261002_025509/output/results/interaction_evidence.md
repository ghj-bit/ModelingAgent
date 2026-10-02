# Interaction Evidence — MM-Bench 2020_C

Three expert exchanges, one question each, in order. File names: `logs/operator_feedback/expert_question_N.md`, `expert_reply_N.json`.

## Exchange 1 — Selection structure of review data

**Question:** On Amazon, are most customers who buy a product silent, with only a few leaving a star rating or a written review? Roughly what fraction actually rate or review?

**Reply (summary):** Yes. On the order of 1–5% of buyers post a star rating; written reviews are a subset, roughly 1–3%. Higher-consideration items (microwaves) draw somewhat higher review rates than low-involvement items (pacifiers); dissatisfied buyers are over-represented among posters. Reviewers are a small, self-selected minority; the data are not a representative sample of all buyers.

**How the reply became work:**
- Adopted as a modeling constraint: all rates are estimated *among reviewers* only, and no quantity in the analysis claims to be a rate over the full buyer population.
- Set the review-participation interval p_review ≈ 0.01–0.05 (exchange 1), used qualitatively when interpreting the share of verified purchases and the meaning of a product's displayed average (see the parameter table in `solution.json`).
- Because the silent majority is 3–4-star "mildly satisfied" buyers, the observed mean star must be read as a conditional mean (mean among posters), which is what every star statistic in the submission is.

## Exchange 2 — Direction of the selection bias

**Question:** Among the people who do leave ratings and reviews, is the average star rating you would expect from them lower, higher, or about the same as the true average satisfaction of all buyers? Why?

**Reply (summary):** Higher than the true average. Posting is driven disproportionately by strong positive feeling (delighted buyers want to reward the product) and the mass of mildly-satisfied silent buyers (would-be 3–4 stars) is missing. Dissatisfied buyers are also over-represented, but the net effect on the mean is upward. The gap is larger for cheap, low-involvement items and smaller where dissatisfaction drives posting (defective products).

**How the reply became work:**
- Added a bias-analysis section to `solution.json` (subtask 1 and the outcome field of every subtask): observed means are conditional on posting and biased upward; the bias grows as product quality falls (more complaint-driven posting) — so a falling displayed average overstates the deterioration, while a high displayed average overstates true satisfaction.
- Used to set the interpretation rule: a product's displayed average is tracked *relative to its own history and to category peers*, never as an absolute satisfaction level.
- The direction (upward) was used to justify why the 1-star share p1, rather than the mean, is the robust quality indicator in the success/failure classifier: p1 is less inflated by positive selection because dissatisfaction also drives posting.

## Exchange 3 — Operational warning criterion

**Question:** When judging whether a newly launched product is trending up or down from its first months of ratings and reviews, what single change would a marketing manager most trust as a warning sign?

**Reply (summary):** A sustained drop in the average star rating over successive months — a decline persisting across several consecutive months, not a one-month dip. It is the least noisy signal and robust to small, self-selected samples. Early months have few reviews, so single-month swings are noise; a rating drop accompanied by rising review volume is a stronger warning than a drop on flat volume.

**How the reply became work:**
- Defined the "trouble month" indicator used in the success/failure classifier: a product-month is flagged when (i) volume-weighted mean star over a W-month window is falling by more than THETA stars/month, (ii) at least 3 consecutive months show the decline, and (iii) monthly volume n ≥ K (noise guard for early months). Parameters: W = 3, K = 30, THETA = 0.2 (swept in `code/model2.py --sweep`).
- The volume condition encodes the expert's "drop with rising/adequate volume is a stronger warning": low-volume months are excluded from flags rather than treated as evidence.
- The flag count per dataset (e.g. 0 sustained-decline months for hair dryers at these settings) is reported in `solution.json` as the empirical answer to "is any product's reputation currently decreasing": across all three categories no product shows a *sustained* decline, consistent with the expert's warning that isolated monthly dips are noise.

## Provenance note

No expert sentence was copied into the submission; the values that travel are the intervals (p_review ∈ [0.01, 0.05]), the bias direction (upward mean bias), the warning definition (sustained ≥3-month decline, volume-conditioned), and the parameter values (W=3, K=30, THETA=0.2), each integrated into the model where it is used.
