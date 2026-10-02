# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence

## Exchange 1
- Question: "In rural counties where police activity is low, are reported drug cases a fair measure of actual opioid use, or do they mostly reflect where police happen to look?"
- Reply (summary): Reported drug cases are not a fair measure of actual use in low-activity rural counties; counts reflect enforcement intensity + lab submission behavior combined with true prevalence, and low counts can mean little enforcement rather than little use. Location can also be attributed to the submitting agency's county when incident location is missing.
- Effect on work:
  - Structural assumption: county-level NFLIS case counts are treated as an enforcement-weighted proxy, not prevalence. Consequences:
    1. All "spread" analysis is done on rates relative to county total substance counts (share of identifications) and on normalized growth, so enforcement-scaling differences partially cancel.
    2. Model includes an enforcement-intensity covariate (TotalDrugReportsState per capita) in the Part 2 regression to separate the enforcement channel from the prevalence channel.
    3. Interpretation rule: county-level point predictions of use are not reported; only relative rankings and threshold-crossing behavior of normalized counts are reported. Threshold decisions use a relative criterion (county exceeding a quantile of the state distribution for 2 consecutive years), consistent with treating counts as a proxy (interval of validity: the 2010-2017 observation window of the supplied NFLIS data).
  - Source of constraint: Exchange 1 reply.

## Exchange 2
- Question: "In counties hit hard by opioid abuse, is high poverty a cause of the abuse, or does the abuse itself push incomes and jobs down?"
- Reply (summary): Neither direction is identifiable from panel/cross-sectional data; both are plausible and mutually reinforcing (feedback loop). Poverty is a correlated, jointly-determined variable, not an exogenous cause.
- Effect on work:
  - Part 2 regression is reframed: the socioeconomic covariates enter as *associated drivers* (concurrent controls), and the report explicitly states that coefficients are associative, not causal, and that the poverty<->use feedback loop means the true effect of any single covariate is directionally ambiguous.
  - Consequence for Part 3: the counter-strategy model treats the poverty channel as a feedback term: county use U_t feeds back into a socioeconomic stress index S_t (addiction -> labor loss), and S_t feeds U_{t+1}. This feedback loop is what the strategy must break; the simulation includes a stress-feedback parameter (delta) so that success/failure bounds can be stated in terms of breaking the loop rather than shifting a single covariate.
  - Source of constraint: Exchange 2 reply (interval of validity: the joint-determination logic applies to the 2010-2017 panel used here).

## Exchange 3
- Question: "For a state deciding where to spend anti-drug money, how big a rise in county drug cases over two years would make a county a top priority?"
- Reply (summary): No single defensible absolute threshold. Decision-relevant criterion: relative to county baseline and state; >=100% rise over 2 years = strong signal, 50-100% moderate, <50% noise. Require a minimum absolute base (order of tens of cases) so small counties are not triggered by 2->6 jumps. Pair trend with a prevalence-independent indicator before committing resources.
- Effect on work:
  - Threshold/decision rule adopted in Part 1 (alert) and Part 3 (intervention targeting):
    * ALERT: a county-year is a priority target iff (cases_t/cases_{t-2} - 1) >= 0.5 (moderate) or >= 1.0 (severe), AND cases_{t-2} >= 10 (absolute base floor, per the "order of tens" guidance), AND the county's normalized rate (cases per 100k total identifications) is above the state median (enforcement-independence check from Exchange 1).
    * Severity tiers: moderate (>=50% 2-yr rise), severe (>=100%).
  - These values enter model.py as constants T_MOD=0.5, T_SEV=1.0, BASE_FLOOR=10, with interval of validity: the 2010-2017 observation window; the rule is stated to hold for county-level NFLIS-style counts and should be re-tuned if enforcement policy changes materially.
  - Source of constraint: Exchange 3 reply.
