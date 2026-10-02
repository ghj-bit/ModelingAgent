# Interaction Evidence

Three expert exchanges, one question each, asked in sequence before the work each governed.

## Exchange 1

**Question** (`logs/operator_feedback/expert_question_1.md`): "In your field work, does a scrub patch's ability to support lizards depend mostly on its total size, or on how much open sand it has?"

**Reply** (paraphrased; full text in `logs/operator_feedback/expert_reply_1.json`): Open sand is the operative variable. Scrub lizards are obligate to open, sparsely vegetated sandy substrate (basking, foraging, egg-laying). Total patch size matters only as a proxy for how much sand a patch contains and for connectivity; two equal-area patches can differ sharply in density by sand fraction. A large overgrown patch can support fewer lizards than a smaller open one.

**How it was used in the work:**
- Chose sandy-habitat area s (ha), not total patch area A, as the independent variable for all Task 3 functions and for the Task 5 classification. This is the decision the answer turned on: fitting F_a, S_j, S_a, C against A instead of s would have given weaker fits (the sand fraction varies 0.21-0.34 across Table 2) and a different ranking of Table 3 patches.
- Task 1 recommendation: protect the open-sand fraction as the conservation unit, not total patch area.
- Task 5: patch ranking by s, not by patch size (patch 12 ranks first on s = 19.15 ha even though several patches are larger in total area).

## Exchange 2

**Question** (`logs/operator_feedback/expert_question_2.md`): "What usually makes a scrub patch lose its open sand, and can that be reversed by fire?"

**Reply** (paraphrased; full text in `logs/operator_feedback/expert_reply_2.json`): Fire suppression is the main cause. Without periodic fire, oak and shrub canopy closes over the sand, litter accumulates, open sandy area shrinks — the standard mechanism behind the ~6%/year vegetation-density increase in the problem. Reversible by fire: burning reopens the canopy and restores bare sand; scrub species are fire-adapted; open sand returns over a few years post-burn and regrowth resumes immediately, so repeated burns at an appropriate interval are needed.

**How it was used in the work:**
- Task 1: identified fire suppression as the primary, policy-addressable driver of habitat loss, and burning as the management lever that directly controls the sand fraction.
- Task 6: the entire burn-interval calculation. The 6%/year regrowth (given) is the post-burn regrowth rate; a burn resets vegetation density to a low post-burn value v0; closure time from v0 at 6%/year is ln(vT/v0)/ln(1.06) = 20.0 yr (vT = 0.80), 22.0 yr (0.90), 22.9 yr (0.95). The "repeated burns at an appropriate interval" instruction is what makes the interval a hard policy constraint rather than a one-time restoration.
- Task 5 limitation note: because regrowth resumes immediately, any gap in the burn schedule erodes the sand fraction on a 20-year clock, so the metapopulation equilibrium of ~600 lizards is conditional on the burn regime in Task 6.

## Exchange 3

**Question** (`logs/operator_feedback/expert_question_3.md`): "If your lizard count for a patch is off by half, would that change which patches you protect first?"

**Reply** (paraphrased; full text in `logs/operator_feedback/expert_reply_3.json`): No, not for prioritization. Patch ranking is driven by sand fraction and patch size, which are measured from aerial imagery and are far more reliable than a lizard count. A count off by half shifts all patches roughly proportionally, so the ordering is largely preserved. It would change the decision only for two patches whose estimated populations are within about a factor of two of each other; even then the tie-break should fall back on sand area and connectivity, not the count. A 50% count error is tolerable for prioritization; it matters for absolute totals and close calls.

**How it was used in the work:**
- Set the decision-relevant uncertainty threshold: the model's output is judged at the planning level, where a 50% error in the population estimate does not invalidate the protection priority. This is why the Task 5 answer reports the ranking (top 5 patches: 12, 2, 15, 17, 9 by sand area) as the robust result and the absolute total (601 lizards) as the less reliable one.
- Task 5: the 0.90/1.00 viability cutoff and the "no patch is self-sustaining" conclusion are framed with this tolerance in mind — the ranking of which patches to protect first (by sand area) is the load-bearing result, and it does not depend on the count being within 50%.
- Task 1: the recommendation to protect the top sand-bearing patches first is explicitly justified as robust to the demographic uncertainty quantified in Task 5.
- Task 3: the ~20% fit error in C(s) is reported as within the decision-relevant band.

## Parameter table (calibrated inputs from exchanges)

| Parameter | Value | Interval | Source |
|---|---|---|---|
| Primary habitat variable | open sandy area s (ha), not total area A | — | Exchange 1 |
| Fire suppression as primary habitat-loss driver | yes | — | Exchange 2 |
| Fire reverses canopy closure | yes, over a few years post-burn | — | Exchange 2 |
| Repeated burns required (regrowth resumes immediately) | yes | — | Exchange 2 |
| Decision-relevant count error threshold | 50% does not change protection priority | [factor 2] | Exchange 3 |
| Tie-break for close patches | sand area and connectivity, not count | — | Exchange 3 |

All other empirical values (6%/year regrowth, 10% juvenile migration, clutch function, Table 1-3 data) come from the task's own problem statement and datasets, not from the exchanges.
