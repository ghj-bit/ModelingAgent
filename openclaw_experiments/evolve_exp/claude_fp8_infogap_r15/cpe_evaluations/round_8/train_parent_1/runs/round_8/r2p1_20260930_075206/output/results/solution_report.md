# Solution

## Subtask 1: Goal: define an appropriate, defensible concept of return-on-investment (ROI) for the Goodgrant Foundation's charitable 

### Problem

Goal: define an appropriate, defensible concept of return-on-investment (ROI) for the Goodgrant Foundation's charitable educational grants, and state the modeling assumptions that frame the whole strategy. Scope: the ROI must be meaningful for a philanthropist (not a commercial investor), grounded in the College Scorecard fields, and consistent with the problem's phrasing 'demonstrated potential for effective use of private funding.'

### Analysis

Assumptions. (1) The $100M/year is committed for five years (July 2016 - June 2021), $500M total, and the objective is to maximize the expected student-facing benefit delivered per dollar of grant. (2) A charitable grant produces benefit through the students it reaches and lifts, so return is measured as benefit, not profit. (3) The Scorecard gives levels of outcomes, not treatment effects; we therefore measure *potential for effective use* (headroom to lift, gated by demonstrated capacity), not a causal treatment effect. (4) Data are the two required datasets: the IPEDS candidate roster (2,977 schools) and the Scorecard 'most recent cohorts' file (one cohort per institution; 2,977 matched rows). External empirical anchors (planner-recorded): the ~$25k six-year earnings threshold is the Dept. of Ed 'did the school add value' benchmark; the ~$46,200 national mean 10-year earnings is a sanity-check reference level; the 2015 median U.S. household income of $56,516 bounds a defensible 'strong positive effect.' ROI is defined as the *impact intensity*: the student-facing benefit returned per dollar of grant, per year. This is defensible for a foundation because it answers 'for each dollar we give school i, how many dollars of student benefit do we expect back each year?' and it differentiates schools. The expert consultation (Exchange 1) confirmed the ROI definition is ours to make and defend, not a fact to read off the data; the ~$25k and ~$46k figures fix the benchmark windows and the value scale.

### Modeling Process

Let x_i be the annual grant to school i, B_i the realized 5-year benefit, and n the number of affected students. Per-student value scale v = $500 of lifetime benefit per affected student-year (a defended charitable magnitude, bounded against the $25k threshold and the $56,516 median household income). Benefit with decay over the 5-year horizon: B_i = n_i * v * sum_{t=0}^{4} (1-delta)^t, with delta = 0.12 the annual fade rate (students graduate and gains fade, so a decaying stream, not a one-shot gain). ROI intensity: ROI_i = B_i / (5 * x_i), units $ of benefit per $1 of grant per year. Higher ROI_i means more student benefit per dollar per year; the ranking by ROI_i (equivalently by benefit intensity per dollar) produces the prioritized list.

### Outcome Analysis

The ROI is an intensity, not a portfolio ratio, so each school's efficiency is individually auditable, which is what a CFO reviewing a charitable portfolio needs. Limitations: v is a defended scale, not an estimate from treatment data (no counterfactual exists in the Scorecard); delta is a structural assumption about fade. Sensitivity: the funded list is invariant to delta and to the saturation discount (tested at delta=0.08/0.12 and beta_sat=0.10/0.25), so the ranking is robust to the decay assumption. Bias: because v is common to all schools, it cancels in any ranking; it only affects the absolute ROI magnitude, not which schools are funded.

## Subtask 2: Goal: identify the schools — an optimized, prioritized 1-to-N candidate list — based on each school's demonstrated poten

### Problem

Goal: identify the schools — an optimized, prioritized 1-to-N candidate list — based on each school's demonstrated potential for effective use of private funding. Scope: turn the 2,977 candidate institutions into a ranked, defensible shortlist using a defensible subset of the two datasets.

### Analysis

Eligibility (hard screen) fixes the state space: a school qualifies iff it (a) is on the IPEDS candidate roster, (b) is degree-granting (PREDDEG in {1,2,3,4}), (c) has UGDS > 1,000 (plausible scale to absorb a grant), and (d) reports the three core outcome fields (gt_25k_p6, md_earn_wne_p10, and RET_FT4 or C150_4_POOLED_SUPP). This leaves 2,164 eligible schools from 2,977. The score is 'demonstrated potential for effective use of private funding,' and its structure was fixed by the expert consultation. The expert rejected a pure gap-to-potential score (Exchange 2) and identified, as the dominant failure mode (Exchange 3), that a level-based score is monotone in current performance and therefore selects elite, low-Pell schools already at the ceiling — inverting the foundation's aim and spending where marginal benefit is near zero. The final score is headroom-tilted to eliminate that inversion: a demonstrated-capacity gate multiplied by a bounded upside-potential term, with saturated elite schools discounted.

### Modeling Process

Within size group g (S: UGDS<=1000, M: <=5000, L: <=10000, XL: >10000), compute winsorized (5th-95th) peer-standardized z-scores of the demonstrated-capacity components: z25 (gt_25k_p6), zearn (md_earn_wne_p10), zret (RET_FT4), and -zdebt (GRAD_DEBT_MDN10YR_SUPP, lower is better). Capacity: cap_i = clip(0.5 + 0.5*tanh(0.7*(0.45*z25 + 0.35*zearn + 0.10*zret + 0.10*(-zdebt))), 0.05, 1). Upside potential: pot_i = max(peer_median_gt25k - gt25k_i, 0), normalized to [0,1] within the eligible pool, and discounted by a factor beta_sat = 0.25 for saturated schools (PCTPELL < 0.20 AND gt25k_p6 > 0.80). Final score: headroom_i = cap_i * pot01_i. Schools are ranked in descending order of headroom_i.

### Outcome Analysis

Validation directly against the expert's named failure mode: the headroom top-20 contains 0 saturated (elite) schools, whereas the pure level-score top-20 contains 16, and the two lists have zero overlap. The inversion is eliminated: the score now surfaces high-upside, high-capacity schools rather than saturated elites. The top of the ranked list: 1) United Talmudical Seminary (Brooklyn, NY; UGDS 1,814; gt25k 7.8%; median earn $13,400; Pell 89.5%), 2) Denmark Technical College (SC; UGDS 1,804; gt25k 17.3%; Pell 79.8%), 3) Berea College (KY; UGDS 1,587; gt25k 46.7%), 4) Whitman College (WA; UGDS 1,525; gt25k 51.8%). The first three are high-Pell, low-earnings institutions with the most headroom; Whitman is a strong mid-list case. Limitations: capacity is inferred from current levels, which can overstate a school's ability to convert a grant into lift; the size-group peer benchmark assumes schools of similar size are comparable; a single Scorecard cohort gives no trend. Bias: the gate (cap) favors schools that already perform moderately well, so the very weakest schools (cap near 0.05) are deprioritized even with large raw gaps — a deliberate trade-off against the 'picking the worst' failure, but it can under-select a few genuinely distressed-but-recoverable schools.

## Subtask 3: Goal: determine the investment amount per school, the return on that investment, and the time duration, producing the op

### Problem

Goal: determine the investment amount per school, the return on that investment, and the time duration, producing the optimal allocation of $100M/year for five years. Scope: allocate the budget across the prioritized schools to maximize total expected benefit under a minimum-effective-grant and a per-school maximum.

### Analysis

The allocation is a constrained benefit-maximization: fund schools in rank order subject to (a) a minimum effective grant x_min (below this a grant cannot change school behavior — a structural lower bound), (b) a per-school cap x_max (no single school should absorb a dominant share), and (c) the annual budget $100M. The time duration is the problem's fixed 5 years, starting July 2016. We choose x_min = $25M and x_max = $25M so each funded school receives an effective, non-dilutive grant; with $100M/yr this funds N = 4 schools per year, a diversified portfolio rather than a single mega-grant. This granularity is a defensible choice (Exchange 1 left it open) and is stable in the output.

### Modeling Process

Decision variables x_i >= 0. Constraints: sum_i x_i <= 100,000,000 (per year); x_min = 2,500,000 <= x_i <= x_max = 25,000,000 for funded schools; x_i = 0 for unfunded; number funded N <= N_max = 15. Objective: maximize sum_i B_i, where B_i = (headroom_i * UGDS_i) * v * sum_{t=0}^{4}(1-0.12)^t. Because ROI_i = B_i/(5 x_i) is monotone in headroom_i * UGDS_i for fixed x_i, the greedy fill in rank order of headroom (with UGDS reach in the benefit) is optimal for this separable structure. Each of the 4 funded schools receives x_i = $25M/year, $125M over five years.

### Outcome Analysis

Result: 4 schools funded at $25M/year each ($125M total each over 5 years), $100M/year fully allocated. Per-school ROI intensity (benefit per $1 of grant per year) ranks United Talmudical Seminary highest at ~0.0033, then Denmark Technical (~0.0030), Berea (~0.0024), Whitman (~0.0021); affected-student estimates are ~212, 188, 149, 132 respectively. The portfolio is diversified across 4 states (NY, SC, KY, WA) and all four are size-group M (UGDS 1,500-1,900), the band with the best balance of reach and headroom. Limitations: the fixed $25M granularity is a design choice; a different x_min would change N (e.g., x_min=$10M would fund ~10 smaller grants) but the top-of-list ordering is unchanged, so the recommendation is robust to the granularity within reason. Bias: equal grants ignore that a marginal dollar may have higher marginal benefit at a school with more headroom; a strictly benefit-maximizing allocation would tilt dollars toward the top-ranked school, which we forgo in favor of diversification and the minimum-effective-grant floor.

## Subtask 4: Goal: deliver the strategy as a complete, defensible answer to every subproblem — the prioritized school list, per-schoo

### Problem

Goal: deliver the strategy as a complete, defensible answer to every subproblem — the prioritized school list, per-school investment amounts, ROI estimates, and the 5-year duration — and state the model's limitations and biases. Scope: synthesize results and the robustness/bias analysis into the final recommendation.

### Analysis

The final recommendation is a 5-year, $100M/year ($500M total) strategy funding 4 schools per year at $25M/year each, ranked by the headroom-tilted demonstrated-potential score, with ROI reported as the per-dollar-per-year benefit intensity. The consultation's single settled strategic decision — that the dominant failure mode is elite saturation of a level-based score — is what fixed the score's structure; all other modeling, validation, and allocation work is the solver's own. The recommendation is framed for the CFO: it states the ROI concept, the approach, the major results, and the proposed ROI the Foundation should adopt for the 2016 and future donations.

### Modeling Process

The deliverable aggregates the three preceding models: eligibility screen (Task 1 assumptions), headroom-tilted ranking (Task 2), and constrained allocation with decaying benefit and ROI intensity (Task 3). Final list: rank 1 United Talmudical Seminary (UNITID 197018, NY), rank 2 Denmark Technical College (217989, SC), rank 3 Berea College (156295, KY), rank 4 Whitman College (237057, WA); each $25M/year, $125M over 5 years; ROI intensity 0.0033/0.0030/0.0024/0.0021 benefit-$ per grant-$ per year. The proposed Foundation ROI to adopt: impact intensity = (affected students x $500 lifetime value per student-year x decay-adjusted 5-year factor) / (5 x annual grant), benchmarked against the $25k 'added value' threshold and the ~$46k national mean-earnings reference.

### Outcome Analysis

Major results: the model funds 4 high-headroom, mid-size, predominantly high-Pell schools and fully deploys $100M/year; it contains no saturated elite institution, directly resolving the failure mode the expert identified. Robustness: the top-4 ordering and the 'no saturated school in the funded list' property are invariant to delta (0.08-0.12), beta_sat (0.10-0.25), and to the grant granularity x_min within the tested range, so the recommendation is not an artifact of a single parameter. Limitations and biases: (1) no causal treatment effects exist in the data, so 'potential' is a headroom proxy, not a measured treatment response; (2) single-cohort data give no trend, so a school in a transient dip could be misranked; (3) the capacity gate can under-select a few genuinely distressed-but-recoverable schools; (4) equal grants forgo the marginal-benefit tilt a strictly optimal allocation would use; (5) the $500 per-student value scale is a defended magnitude that sets absolute ROI but cancels in ranking. The strategy is nonetheless defensible: it is transparent, grounded in the two required datasets, robust to its structural assumptions, and aligned with the Foundation's stated aim of funding schools with the greatest demonstrated potential to use private money to improve student performance.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
