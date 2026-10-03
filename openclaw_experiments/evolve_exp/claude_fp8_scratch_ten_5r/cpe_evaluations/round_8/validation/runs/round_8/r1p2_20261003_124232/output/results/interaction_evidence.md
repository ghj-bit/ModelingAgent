# Expert Interaction Evidence — 2006_C (HIV/AIDS resource allocation)

Policy: mechanism → constraint → parameter → edge case, 10 fixed rounds.
All questions were ≤20-word common-sense questions; all replies were converted
into model parameters/constraints before the next round (see "Used as").

## Exchange 1 (structural — dominant mechanism)
- **Q:** When an HIV epidemic grows fastest in a poor country with little treatment, what usually drives it the most?
- **Reply (gist):** Heterosexual transmission through high-risk sexual networks — concurrent partnerships, low/inconsistent condom use, untreated STIs, mobility/migration — is the main engine in poor, low-treatment generalized epidemics; mother-to-child and unsafe injections are secondary. Long infectious duration (no treatment) amplifies each infection.
- **Used as:** Core transmission structure of the model: force of infection proportional to the infectious pool (acute, asymptomatic, AIDS) in a single sexual network; no separate IDU/MTCT compartments for the selected generalized-epidemic countries (Ukraine noted as a limitation). Recorded as the mechanism in task_analysis of solution.json tasks 1-3.

## Exchange 2 (constraint — what stops the growth)
- **Q:** What stops the epidemic from simply growing forever in a country with no interventions?
- **Reply (gist):** Susceptible-pool saturation plus behavior change; effective reproduction declines toward 1, incidence peaks and levels off (logistic S-curve). Mortality also removes infected. Prevalence stabilizes well below 100%, often ~10-30% in worst-hit settings; can decline if mortality + behavior change outpace incidence.
- **Used as:** Three model terms: (a) saturation factor (S/S0) in the force of infection; (b) behavior-change factor (1 - 0.35(1-exp(-prev/0.10))); (c) hard ceiling guard at prevalence 0.30 (interval [0.10,0.30]) that clamps lambda. These produced the S-shaped baseline trajectories in Task 1.

## Exchange 3 (parameter — natural history, total)
- **Q:** Without treatment, roughly how many years does a person with HIV typically survive before dying of AIDS?
- **Reply (gist):** Median ~8-11 years (commonly ~10); 1-2 for rapid progressors, 15-20+ for long-term non-progressors; resource-poor settings at the shorter end, ~7-10 years.
- **Used as:** asymptomatic_yrs = 10 (interval [7,11]) + AIDS-stage duration; total survival ≈ 10 yr. Drives the A→R progression rate (1/10 per yr), R death rate (1/3 per yr, AIDS_yrs = 3), and the incidence calibration I0 = H0/10.

## Exchange 4 (parameter — natural history, staging)
- **Q:** After infection, how many years of healthy life are lost before AIDS symptoms typically appear?
- **Reply (gist):** Same ~8-11 yr (≈10) asymptomatic interval; in resource-poor settings 7-10 yr.
- **Used as:** Confirmed the A-compartment duration = 10 yr (AIDS_yrs = total - asymptomatic ≈ 3 yr, interval [2,4]); validated the two-stage natural-history split used in calibration.

## Exchange 5 (parameter — infectiousness timing)
- **Q:** How many years after HIV infection does the highest risk of passing it to a partner usually occur?
- **Reply (gist):** First weeks to months (acute/primary phase, viral load in the millions) is the per-contact peak; then a lower plateau through the asymptomatic years; then a late rise as AIDS develops. Two high-risk periods: acute and late-stage.
- **Used as:** acute_mult = 4 (interval [2,6]) applied to the E and R compartments in the infectious-load term: lambda ∝ 4E + A + T(1-supp) + 4R + D.

## Exchange 6 (constraint — ARV delivery limit)
- **Q:** In a low-income country, what usually limits how many people can actually start antiretroviral treatment?
- **Reply (gist):** The binding constraint is health-system absorptive/delivery capacity, not drug price: clinicians, labs/monitoring, adherence counseling, supply chains, testing/linkage; financing is the enabling constraint; structured DOTS-style monitoring is required to avoid resistance.
- **Used as:** ARV enrollment in the model is capacity-capped (growth 10-30%/yr of the untreated pool, decaying with coverage) rather than fund-capped; the $1,100/person-year DOTS cost (task statement) is documented as dominated by non-drug delivery costs; adherence monitoring is named as the top operational investment in the Task 4 recommendation.

## Exchange 7 (parameter — scale-up speed)
- **Q:** How fast can a poor country realistically expand antiretroviral treatment to new patients each year?
- **Reply (gist):** ~10-30%/yr early scale-up, often slower; fastest documented (Botswana, Uganda) 30-50% for a few years from a low base; growth decelerates as the easy-to-reach patients are enrolled.
- **Used as:** enroll_growth = clip(0.10 + 0.15·min(GNP,3000)/3000, 0.10, 0.30) (interval [0.10,0.30]); this cap is why ARV prevalence effects are gradual rather than step-function in Tasks 2-3.

## Exchange 8 (edge case — community effect of treatment)
- **Q:** When HIV treatment coverage gets high, does the whole population's risk drop even among unvaccinated people?
- **Reply (gist):** Yes — treatment-as-prevention: virally suppressed patients are far less infectious; at high coverage the effective reproduction can fall below 1 and incidence declines population-wide. Cautions: needs durable suppression; no immunity conferred; risk rebounds if coverage/adherence lapses.
- **Used as:** treatment_prevention = 0.95 (interval [0.90,0.98]): T patients are 5% as infectious in the force of infection. This is the mechanism behind ARV's large person-years-averted in Task 2 and its erosion in Task 3 when resistance drops patients out of suppression.

## Exchange 9 (edge case — data validity)
- **Q:** How reliable is the 1999 country-by-country HIV count data, and where is it weakest?
- **Reply (gist):** Modeled estimates, not counts; weakest exactly in high-burden poor generalized-epidemic countries (sparse, unrepresentative antenatal surveillance, large extrapolation); also weak in low/concentrated epidemics; strongest in rich countries. Treat as order-of-magnitude with wide uncertainty.
- **Used as:** 1999 counts used only as order-of-magnitude anchors: model calibrated on rates (I0 = H0/10) rather than absolute level-matching; ±factor-of-2 uncertainty on absolute H stated as a limitation in Task 1; country-selection scoring kept count as one of three components (60%) so no single weak datum dominates the selection.

## Exchange 10 (edge case — floor under treatment)
- **Q:** In a rich country that already treats most people with HIV, what still keeps new infections from falling to zero?
- **Reply (gist):** Undiagnosed/untreated (often acute-phase) infections; treatment confers no immunity; imperfect viral suppression (adherence, resistance, interruptions); concentrated transmission in key populations; importation. Incidence falls substantially but plateaus above zero, not elimination.
- **Used as:** Justifies the model's persistent-positive-incidence floor: the S_eff = S + V(1-veff) term leaves 30% of vaccinated people susceptible, and the behavior-change term does not drive lambda to zero; Australia's trajectory (prevalence → ~0.12% by 2050 but nonzero incidence) is reported as a plateau, not elimination. Informs the Task 4 "bounded terminal investment" argument: the vaccine + ARV combination approaches but does not guarantee zero.

## Work product traceability
- Mechanism (ex1) → transmission structure, all tasks.
- Constraints (ex2, ex6) → saturation/ceiling/behavior terms; capacity-capped ARV enrollment.
- Parameters (ex3, ex4, ex5, ex7, ex8) → asymptomatic_yrs=10, aids_yrs=3, acute_mult=4, enroll_growth 10-30%, treatment_prevention=0.95, all in the parameter table of solution.json task 1/2 mathematical_modeling_process.
- Edge cases (ex8, ex9, ex10) → prevalence floor behavior, data-uncertainty treatment, plateau interpretation, Task 4 argument.
- No reply text is copied verbatim into solution.json; values, intervals, and the exchange numbers are the recorded provenance.
