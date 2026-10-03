# Expert Interaction Evidence — Problem C (Goodgrant Foundation $100M/yr)

Ten exchanges, one question each, all completed before or during modeling. Questions in `logs/operator_feedback/expert_question_N.md`, replies in `logs/operator_feedback/expert_reply_N.json`. Every reply below is converted into a model element; nothing is copied verbatim into the submission.

## Exchange 1 — selection direction (structural)
- **Question:** When large donors pick which colleges to fund for student success, do they fund struggling high-need schools to lift them up, or proven schools that already do well?
- **Reply (gist):** The norm is funding proven or promising institutions with demonstrated capacity to absorb and scale change, with a tilt toward schools serving many low-income students that already show effectiveness — not the weakest schools. Weak institutions lack leadership, data infrastructure, and absorptive capacity.
- **Turned into work:** This resolved the central structural ambiguity (which side of the performance distribution to fund). Consequences in the model: (1) the composite score rewards above-peer performance (`Comp_i` is a standardized gap vs state-need peer medians, base 0.75), not below-peer "room to improve"; (2) a hard eligibility bar requiring reported outcomes (Exchange 7) rather than imputation; (3) assumption A3 in `task_analysis` of solution.json. Parameter: the scoring direction itself (no numeric value). Interval of validity: US higher-ed philanthropy at $100M/yr scale.

## Exchange 2 — dominant value metric (structural)
- **Question:** When judging whether a college delivers good value to its students, which outcome matters most: graduation, four-year retention, or students' later earnings?
- **Reply (gist):** Later earnings relative to debt matter most; graduation is a necessary gate (earnings data only cover graduates); retention is the weakest standalone measure. Raw earnings are confounded by intake, so value is earnings conditional on completion and debt.
- **Turned into work:** (1) ROI numerator is the PV earnings premium of an additional completion (K × completions gained), not a headcount of graduates — `mathematical_modeling_process` formula `ROI_i = G_i·K/x_i`; (2) completion enters as the gate/conversion term `G_i`, earnings quality as the `Earn_i` factor (debt-adjusted); (3) retention demoted to a screening signal, not the objective. Assumption A2 (charitable ROI = student earnings return).

## Exchange 3 — grant sizing (quantitative structure)
- **Question:** When a foundation splits its grant money across several schools, does it give roughly equal amounts to each, or more to the bigger or hungrier schools?
- **Reply (gist):** Not equal. Differentiated, size- and need-weighted amounts: scale of the (low-income) problem, absorptive capacity, strategic role; a tiered allocation with a few larger anchor grants and a larger tail of smaller grants.
- **Turned into work:** The allocation is not equal-split. Water-fill weights `w_i = 0.5·(C_i/ΣC) + 0.5·(L_i/ΣL)` (merit + low-income scale), per-school bounds GMIN=3M, GMAX=4%·B, and the anchor/core tier split (50/50 of slots). Recorded in the parameter table as GMIN/GMAX with source "Exchanges 3 and 6".

## Exchange 4 — time schedule (boundary)
- **Question:** For a five-year, $100M-a-year education grant, how do foundations typically split the money across the years?
- **Reply (gist):** Not flat: year 1 smaller (planning/startup), years 2–4 peak implementation, year 5 taper/sustainability. Caveat: the problem fixes $100M/yr, which pushes toward level annual outlays; the ramp is a tendency, not a requirement.
- **Turned into work:** (1) Portfolio-level outlay held at level $100M/yr (the problem's fixed annual total) — stated in assumption A6 and the duration recommendation; (2) within each grant, the tranche shape (front-loaded years 2–4, sustainability year 5) is reported in the duration recommendation; (3) effect discounting uses years 3–5 (midpoint 0.889 at r=4%), consistent with a ramped deployment rather than day-1.

## Exchange 5 — effect timing and magnitude (quantitative parameter)
- **Question:** If a grant helps a college's student success, how fast do you expect the effect to show up? Within a year, or only after several years?
- **Reply (gist):** Little measurable effect in year 1; real payoff after 3–5 years, strongest at 5+; completion outcomes are lagged by definition; 5-year grant window is the minimum to observe completion effects.
- **Turned into work:** (1) delta (completion lift) = 0.05 central, interval [0.03, 0.10], held for 5-year grants at capacity-screened institutions — the key empirical parameter, cross-supported by the intervention-lit search (doi:10.3102/1686532); (2) effect discounted with `disc(3..5)` = mean of (1+r)^-t for t∈{3,4,5}; (3) year-1 = implementation assumed in the schedule; (4) limitation (4) in the outcome analysis (ROI figures are planning estimates; revisit with year-2 leading indicators).

## Exchange 6 — portfolio size (quantitative parameter)
- **Question:** In practice, how many schools would a foundation realistically fund with a $100M-a-year program?
- **Reply (gist):** Dozens — roughly 20–100 direct grantees, grants typically $1M–$10M per year; hundreds only if money flows through intermediaries that sub-grant.
- **Turned into work:** N = 60 central, interval [20, 100] (parameter table); sweep over N ∈ {20,40,60,80,100} in `model.py --sweep N`; GMIN/GMAX bounds calibrated so annual grants fall in the $0.8M–$4M range; recommendation logic for N=60 in the outcome analysis.

## Exchange 7 — disqualifier (structural)
- **Question:** What is one thing that would make a foundation avoid funding an otherwise good college? Name a single deal-breaker.
- **Reply (gist):** Lack of capacity/infrastructure to absorb and account for the money — no functioning institutional research, no ability to track outcomes, no financial controls.
- **Turned into work:** Hard eligibility filter in `model.py::eligibility`: school must report RET_FT4 and md_earn_wne_p10 (missingness treated as failing the accountability bar, not imputed — the data-cleaning decision documented in `task_analysis`), UGDS ≥ 500, STABBR present; drops 1,460 of 2,977 to 1,517. Plus the `Cap_i` capacity term from repayment track record.

## Exchange 8 — risk tolerance (boundary)
- **Question:** In a candidate list ranked by expected payoff, do funders keep only safe bets, or do they deliberately include some riskier bets too?
- **Reply (gist):** Deliberate minority of higher-risk, higher-upside bets; barbell portfolio — core of demonstrated performers carries most dollars, smaller riskier tail; risk is bounded and must still clear the capacity bar.
- **Turned into work:** (1) Barbell structure: top 50% of funded slots = anchors with the largest grants (anchor_share = 0.5, interval [0.35, 0.7]); (2) "riskier" = lower composite score (further from proven performers) within the top N, all still passing the Exchange-7 bar; (3) GMAX cap keeps the tail bounded.

## Exchange 9 — cross-field standard (quantitative structure)
- **Question:** When comparing colleges across different fields of study, do funders judge a business school and a nursing school by the same earnings standard?
- **Reply (gist):** No — field is one of the strongest determinants of earnings; benchmark within field or adjust for program mix, not one flat dollar threshold.
- **Turned into work:** Peer-adjustment design: `Earn_i` divides the school's above-$25k earnings headroom by its state × need-quintile peer median mE_i (fallback to national quintile when the state-need cell has <25 schools). This adjusts for program-mix and state wage differentials as far as the data allow; the residual limitation (K is not field-specific) is stated in limitations (3).

## Exchange 10 — need weighting (quantitative parameter)
- **Question:** For an education foundation, does a dollar that gets a low-income student to graduate count as more impact than the same dollar at a wealthier school?
- **Reply (gist):** Yes — marginal effect is larger where completion barriers are higher (counterfactual is drop-out, not graduate-regardless); mission alignment and counterfactual/need weighting are standard. Caveat: the school must still be able to convert the money.
- **Turned into work:** `Need_i = 1 + P_i` (Pell share) multiplies the composite and the effect (`(0.6 + 0.4·P_i)` in G_i); assumption A4; parameter line "Pell-weight form" in the table with source Exchange 10. The caveat is honored by the Cap_i term and the eligibility bar.

## Summary of the consultation's contribution
- Structural (fixed the model's skeleton): Exchanges 1 (fund proven+high-need, not weakest), 2 (ROI = earnings conditional on completion and debt), 7 (accountability/absorptive-capacity bar as hard filter), 9 (peer/field-adjusted earnings standard).
- Quantitative calibration (parameters with intervals and validity ranges in the solution.json parameter table): Exchanges 3 (sizing rule), 4 (level $100M/yr + within-grant ramp), 5 (delta = 5pp [3–10]), 6 (N = 60 [20–100], grant bounds), 8 (anchor_share 0.5 [0.35–0.7]), 10 (Need_i = 1 + P_i).
- No exchange was used for coding help, validation of calculations, or mathematical derivations; no reply text appears verbatim in the submission.
