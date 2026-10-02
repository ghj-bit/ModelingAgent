# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction evidence — 2015_C (ICM human-capital churn)

## Exchange 1
- **Question** (`expert_question_1.md`): "When a valued employee quits, how many coworkers typically leave with them or within a few months afterwards?"
- **Expert reply (summary)**: no reliable single figure; churn literature frames this as voluntary-turnover contagion / spillover — one departure *raises the odds* that other coworkers quit rather than producing a fixed number of followers. Typical magnitude: well below one additional quit per departure (roughly 0.1–0.5 additional quits in a few months), concentrated in the leaver's immediate team and close informal ties; occasionally a tightly knit subgroup or a manager's exit triggers a cluster of 2–5 exits (tail, not norm).
- **Use in work**: sets the contagion intensity `beta = 0.3 [0.1, 0.5]` in the SIS-style churn-diffusion model (code `churn_model.py`, parameter `BETA`). Interval: short-horizon (few months) per departure, local team. Source: exchange 1, cross-checked against the contagion-talent-turnover literature (e.g. https://doi.org/10.1080/13678868.2023.2238247). Model change: hazard of a non-manager node is `h = r0*L + beta*mean(churn of neighbors)`; the 2–5 cluster tail motivates the manager-level multiplier (see Exchange 2).

## Exchange 2
- **Question** (`expert_question_2.md`): "When middle managers leave, is it mainly because of their own dissatisfaction, or because of problems around them?"
- **Expert reply (summary)**: proximate cause is the manager's own dissatisfaction, but it is shaped by surrounding conditions — blocked promotion ladders, pay/recognition, the supervisor above, workload, and a peer group that is also churning. Treating it as purely individual would misdiagnose it.
- **Use in work**: (a) justifies the level-specific baseline rates — middle-manager baseline set at exactly 2x the company-wide 18% = 36% (problem statement) and treated as *endogenous*: `L_m = L_m,base + kappa*<churn in layer>` with `kappa = 0.5` (self-reinforcing stagnation, bounded so L stays < 1); (b) gives the manager multiplier on contagion: because managers carry coordination load, their departures are taken more strongly to heart, so neighbor pressure enters with weight `w_m = 1.5` for manager neighbors vs `1.0` for other neighbors. (c) Promotion channel: blocked ladders are structural, so the promotion path is the lever the model uses in the Task 5 "promote only qualified" scenarios rather than rate changes.

## Exchange 3
- **Question** (`expert_question_3.md`): "At what point does high turnover start to noticeably hurt company performance, before anyone quits?"
- **Expert reply (summary)**: no sharp cliff; gradual. Damage becomes noticeable in the mid-teens to low-20s percent annual turnover (≈ ICM's current 18%); below ~10% absorbed without visible loss; from ~15% upward the pre-departure (anticipatory, social) effects bite — coverage work, continuous onboarding, knowledge leakage, declining discretionary effort — with the mid-level manager tier showing it first because it carries coordination/knowledge-transfer load.
- **Use in work**: sets the productivity penalty curve: `P(r) = 1 − 0.5*r` for r ≥ 0.15 and a mild `1 − 0.1*r` below (piecewise-linear loss, continuous at 15%); the anticipatory channel is modeled as a morale factor that also feeds back into L (disengagement raises dissatisfaction → endogenous churn). Decision-relevant thresholds adopted: **safe** r < ~10%, **noticeable damage** r ≈ 15–20%, **unsuitable for decision-making** when results flip only under parameter values outside the stated intervals. Manager-tier weighting: manager vacancy months count with weight 1.5 in the productivity loss.

## How the replies changed the model (concrete)
1. Contagion term added to hazard with `beta=0.3` (exch. 1) — without it the churn process is pure independent Poisson and Task 2's "diffusion" claim is unsupported.
2. Endogenous middle-manager rate `L_m(L) = 0.36 + 0.5*<layer churn>` replacing a fixed 36% (exch. 2) — this is what makes the Task 5 "30% churn in junior managers + experienced supervisors, no external recruiting" simulation cascade instead of flatly holding 30%.
3. Piecewise productivity penalty with break at 15% and manager weight 1.5 (exch. 3) — supplies the "indirect effects" quantification in Tasks 4/5 and the decision threshold the answers use to classify 25%/35% churn as unsustainable.
4. All three parameters enter the calibrated-input table in `solution.json` with source = the exchange, plus a literature cross-check where available.
