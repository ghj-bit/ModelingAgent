# Solution

## Subtask 1: Define a charitable return-on-investment (ROI) concept for the Goodgrant Foundation and identify the logical boundaries 

### Problem

Define a charitable return-on-investment (ROI) concept for the Goodgrant Foundation and identify the logical boundaries that govern it: the attribution baseline for the return, the form of the ROI (benefit-per-dollar vs discounted cumulative vs annual rate), and which of {number of schools N, per-school amount, per-school duration} are free decision variables. This subtask sets the ground truth every later subtask parameterizes against; it does not yet compute any school-level value.

### Analysis

The problem asks for a 'return on investment defined in a manner appropriate for a charitable organization' but leaves three structural choices undefined. We resolved each with the expert (consultation Exchange 1, Operator 1 open-ended). Assumptions: (1) the grant's effect on student outcomes is not directly observed in the data, so the ROI must be an *expected* return built from observable outcome metrics; (2) the defensible return is the *incremental* benefit above a matched reference, not the full outcome level the school already produces (crediting the level double-counts historical value-added; crediting only the grant's own effect is unobservable); (3) the $100M/yr is a hard annual budget over a fixed five-year outer window (2016-2021). The matched reference is a peer band of institutions comparable to the funded school, so the increment measures the grant's contribution to moving the school toward or above that band rather than the school's pre-existing quality.

### Modeling Process

ROI form (Exchange 1 ruling): ROI_i = PV(incremental benefit stream) / cost_i, a discounted cumulative benefit divided by cost. Benefit-per-dollar was rejected because it ignores timing; an annual rate was rejected because the data support no return stream. The benefit stream is discounted at rate r, with the 6-year (share >$25k) and 10-year (median earnings) outcome lags respected. Decision variables (Exchange 1 ruling): N (number of schools), per-school amount a_i, and per-school duration d_i are all free, subject to the annual budget sum(a_i over funded i, year t) <= 100,000,000 and the five-year outer window 0 <= start_i, start_i + d_i <= 5. Structural limits (a per-school grant large enough to matter, small enough to be absorbed) are constraints on a_i, not fixed values. The attribution baseline is the increment over the matched reference: benefit_i = f(outcome_i) - f(reference_i), with f the outcome-to-benefit map and reference_i the peer band for school i.

### Outcome Analysis

Outcome: the charitable ROI is a discounted cumulative incremental benefit per dollar. The increment is measured against a peer band (not the raw outcome level and not the unobservable grant-only effect). N, a_i, and d_i are free within the budget and window. Limitation: the reference band must be observable from the data; a finer band (regional, matched on admissions) was proposed in Exchange 2 but rejected, so the fallback uses a coarser, fully observable state-level peer band (Subtask 2). Bias: the increment is a *potential* gain, so the ROI is an upper-bound-like estimate of the grant's return, not a measured causal effect.

## Subtask 2: Choose the defensible subset of the IPEDS/Scorecard data, define the peer-baseline and the outcome-to-benefit map, and c

### Problem

Choose the defensible subset of the IPEDS/Scorecard data, define the peer-baseline and the outcome-to-benefit map, and compute a school-level ROI for every candidate institution. The deliverable is the ranking input: a per-school ROI and a data-coverage flag for all 2,936 candidate schools with Scorecard data.

### Analysis

Data subset (defendable): the 2,936 institutions in the IPEDS candidate file that also appear in the Scorecard Most Recent Cohorts file (1,706 four-year, 914 two-year degree-granting). Variables used, with data-dictionary definitions: md_earn_wne_p10 = median earnings of students working and not enrolled 10 years after entry (primary outcome, 96% coverage); gt_25k_p6 = share of students earning over $25,000/year 6 years after entry (the 'did the school add value' indicator, the $25k threshold approximating high-school-graduate earnings, 97% coverage); UGDS = undergraduate degree-seeking enrollment (scale, 100%); PCTPELL = Pell Grant share (need, 99.8%); C150_4_POOLED_SUPP = 150% completion rate for four-year institutions (secondary quality signal); C200_L4_POOLED_SUPP = 200% completion rate for two-year institutions (the performance metric for sub-baccalaureate schools, 34% coverage); GRAD_DEBT_MDN10YR_SUPP and RPY_3YR_RT_SUPP retained as context. Assumptions: (1) four-year and two-year institutions are scored on different outcome sets because the two-year earnings peer band is an artifact (Exchange 3); (2) a school at or above its state median receives a bounded 'retention' increment (retention_frac times the gap to the state 75th percentile) rather than the full gap, encoding that a grant to an already-strong school buys defense of position, not further gain; (3) missing/suppressed outcomes do NOT silently drop the school (Exchange 3) - the benefit is scaled by a coverage factor so a high-need small school with partial data stays in the candidate list but ranks below fully-observed peers.

### Modeling Process

Peer baseline (Exchange 3 fallback, state-level, degree-grouped): for four-year schools reference_i = state median of md_earn_wne_p10 over four-year schools in that state (with >=5 observed; else national four-year median); for two-year schools reference_i = state median over two-year schools. Increment (four-year): inc_earn_i = max(0, md_earn_i - ref_earn_i), with the retention clause inc_earn_i = retention_frac * max(0, P75_state - md_earn_i) when md_earn_i >= ref_earn_i; inc_gt25_i defined analogously on gt_25k_p6. Increment (two-year): inc_comp_i = max(0, C200_i - ref_C200_i) with the same retention clause. Outcome-to-benefit map: per-student annual benefit = w_earn * inc_earn_i + w_gt25 * inc_gt25_i * val_cross + 0.5 * (inc_comp_i) * val_comp, where val_cross = max(0, national median earnings - 25000) is the dollar value of a student crossing the $25k threshold, val_comp = val_cross (proxy for the earnings value of completing), and w_earn, w_gt25 are weights (sum with the completion weight = 1). The benefit is scaled by coverage_i (fraction of primary metrics observed, floored at 0.34) and by enrollment UGDS_i to get the school's annual benefit. Discounting: the earnings part is discounted by (1+r)^10 and the gt25/completion part by (1+r)^6, then the 5-year grant-period stream is valued at PV = annual_benefit_lagged * (1/mean_t(1+r)^t) * 5. ROI_i = PV_benefit_i / a_i.

### Outcome Analysis

Result: every one of the 2,936 candidates carries an ROI and a coverage flag; 470 candidates have partial coverage (coverage < 1) and remain in the list rather than being dropped. The top of the ranking is led by Salt Lake Community College (ROI ~16.3) followed by Ball State, UMass-Boston, UMass-Amherst, and University of Rhode Island (ROI ~12.4). The state-level peer band is coarse: a school in a state with a low earnings median can look high-ROI partly because of its state's composition, not purely its own potential. This is the failure mode Exchange 3 identified and is mitigated (not eliminated) by the degree-grouping and the national fallback for thin states. The completion metric for two-year schools (34% coverage) is the weakest link: most two-year schools have no C200 value, so their increment is scored on the available earnings metrics with a coverage penalty, which systematically ranks observed two-year schools above unobserved ones.

## Subtask 3: Optimize the allocation: produce the 1-to-N prioritized candidate list, the per-school investment amount, the time durat

### Problem

Optimize the allocation: produce the 1-to-N prioritized candidate list, the per-school investment amount, the time duration, and the expected portfolio return, subject to the $100M/yr budget and five-year window. The deliverable is the funded portfolio and the ranked list of all candidates.

### Analysis

Per Exchange 1, N, a_i, and d_i are free; per the Exchange 2 rejection, we do NOT use an equal-marginal-ROI allocation (it presupposes a smooth observable marginal-benefit function of grant size the data lack). Fallback (Exchange 3): rank schools by ROI_i, assign a uniform per-school grant g = budget / N_target (set once from the data's scale), and fund the top N schools until the annual budget binds; the per-school duration is the full five-year window (the grant is spread over the whole window, with outcomes measured at the 6/10-year lags). Assumptions: (1) a uniform grant is defensible because the data contain no information to differentiate marginal returns by school size; (2) the 'large enough to matter' lower bound and 'absorbable' upper bound on a_i are enforced as constraints (1M <= a_i <= 10M); (3) N_target = 50 is a structural choice giving g = $2M/school, within both bounds.

### Modeling Process

Allocation: order candidates by ROI_i descending; g = 100,000,000 / 50 = 2,000,000; fund the top N = floor(100,000,000 / g) = 50 schools, each with a_i = g and d_i = 5 years. Constraints: sum(a_i) = 100,000,000 per year (binding); 1,000,000 <= a_i <= 10,000,000; 0 <= start_i, start_i + 5 <= 5 (so start_i = 0, the full window). Portfolio return: total PV benefit = sum of funded PV_benefit_i; portfolio ROI = total PV benefit / total cost. The prioritized list is the full 2,936-row ranking; the funded list is the top 50.

### Outcome Analysis

Result: 50 schools funded at $2M each = $100M/yr for five years; 48 four-year and 2 two-year (Salt Lake Community College, Central New Mexico Community College); spread across 26 states; median funded enrollment 12,947; all 50 funded schools have full data coverage (the coverage penalty correctly kept partially-observed schools out of the top 50). Total discounted PV benefit of the funded portfolio is ~$5.58e8 over the window against $5.0e8 total cost (5 years x $100M), a portfolio-level discounted return of roughly 1.12x. Per-school ROI ranges from ~2.4 (LIU Brooklyn, last funded) to ~16.3 (Salt Lake Community College, first). Sensitivity (sweep): at r=0.03 the portfolio PV rises to ~$6.96e8 and at r=0.07 it falls to ~$4.50e8 for N=50; widening N to 100 (g=$1M) raises total PV to ~$7.28e8 at r=0.05 but admits lower-ROI schools. Limitations and biases: (1) the uniform grant is blind to the fact that a $2M grant is a larger share of a small college's budget than of a large one, so the 'absorbable' bound is not truly enforced at the margin; (2) the state-level baseline means the portfolio over-represents schools in states with low outcome medians; (3) the two funded two-year colleges enter only because their observed completion lift is large, so the two-year presence in the portfolio is fragile to the 34% completion coverage; (4) the ROI is a potential-gain estimate, not a measured causal effect, so the 1.12x portfolio return should be read as an upper-bound-like planning figure, not a promise.

## Subtask 4: Validate the model against the data's own reference levels, analyze the robustness to the exchange-settled failure modes

### Problem

Validate the model against the data's own reference levels, analyze the robustness to the exchange-settled failure modes, and state the model's limitations and biases for the CFO letter and the final report.

### Analysis

Validation anchors (from the planner-recorded external data, cited not re-searched): the $25k threshold approximates high-school-graduate annual earnings (the 'did the school add value' line); national mean earnings 10 years after entry ~$46,200 (2011 cohort, 2013 dollars) is a sanity-check level for any earnings-based return; the 2015 U.S. median household income $56,516 bounds what a defensible per-student benefit is. The data's own national median of md_earn_wne_p10 over candidates is ~$37,000, below the ~$46k Brookings mean because the candidate pool skews to two-year and lower-selectivity institutions - consistent and defensible. The robustness analysis targets the two failure modes the expert identified in Exchange 3: (a) suppressed/missing outcomes silently dropping high-need small schools, and (b) the two-year earnings peer band being an artifact.

### Modeling Process

Failure-mode (a) test: we deliberately kept the 470 partial-coverage candidates in the ranking and applied a coverage floor of 0.34 so their benefit is reduced, not zeroed. We then checked whether any funded school had coverage < 1 (none did) and whether high-Pell, small-enrollment schools (the 'high-grant-need' class) appear in the candidate list (they do, ranked below fully-observed peers). Failure-mode (b) test: two-year institutions are scored on C200 completion, not on the four-year earnings metrics; we verified the funded two-year colleges are ranked on the completion increment. Robustness: a sweep over r in {0.03,0.05,0.07} and N_target in {25,50,100} shows the portfolio PV benefit is monotone decreasing in r and increasing in N, with the per-school ROI distribution stable (min ROI 1.6-3.2 across the sweep), so the ranking is not an artifact of a single discount rate or portfolio size.

### Outcome Analysis

The model is internally consistent: the national median earnings of the candidate pool (~$37k) sits between the $25k 'added value' threshold and the ~$46k national mean, as expected for a pool that includes many two-year and lower-selectivity schools. The coverage floor successfully keeps high-need small schools in the candidate list (mitigating failure mode a) while the degree-grouped completion metric keeps two-year schools from being scored on an artifact earnings band (mitigating failure mode b). Residual biases: (1) the state-level baseline over-credits schools in low-median states - the single largest structural bias; (2) the uniform $2M grant does not scale to school budget, so the 'absorbable' constraint is only a bound, not a true marginal condition; (3) the 34% completion coverage makes the two-year ranking fragile; (4) the ROI is a potential-gain (upper-bound-like) estimate, so the ~1.12x portfolio return is a planning figure, not a measured causal return; (5) the retention clause (retention_frac=0.25) is a judgment parameter - a higher value would credit more to already-strong schools and shift the portfolio toward them. These limitations are the content of the bias analysis the CFO letter must carry.

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
