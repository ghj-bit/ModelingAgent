# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — MM-Bench 2006_C (MCM 2007 HIV/AIDS)

Policy: 10 fixed exchanges, structural anchoring before numerical filling.
Each exchange is recorded with its question, the expert's reply (summary), and
the concrete change it made to the model (parameter, equation, or decision rule).

## Exchange 1 — Structural: does the epidemic plateau?
Q: With no intervention, does infected count climb without limit or level off?
A: Levels off. Logistic-like curve driven by depletion of the susceptible pool;
high-risk individuals infected first; approaches an endemic equilibrium set by R0.
Plateau ~10–30% in generalized heterosexual sub-Saharan African epidemics, over 1–2 decades.
**Model change:** Adopted a **logistic-saturation SIR-style** model, not exponential.
State variable = infected adults; growth rate proportional to (carrying capacity − current),
where carrying capacity K_i = R0-dependent fraction of the sexually-active adult population.
This is the architectural decision the whole Task 1 model rests on.

## Exchange 2 — Parameter: plateau height
Q: Fraction of adults infected at peak in hard-hit African countries?
A: 15–30% typical; 25–40% in Botswana, Swaziland, Lesotho, Zimbabwe; 5–15% most others.
**Model change:** Set per-country carrying capacity K. Botswana/Swaziland/Lesotho/Zimbabwe:
K = 0.275 (mid of 25–40%). Other high-prevalence African countries: K = 0.175 (mid 15–30%).
Lower-burden countries: K = 0.10 (mid 5–15%). K bounds the logistic term.

## Exchange 3 — Parameter: speed of rise
Q: Years from <5% to peak?
A: 10–15 years typical (mid-1980s to late 1990s/early 2000s); fastest ~10 yr, slower 15–20 yr.
**Model change:** Calibrated logistic growth rate r = ln( (K/p0) − 1 ) / t_rise, where p0 is the
1999 prevalence and t_rise is the years to go from p0 to 0.9·K. For high-prevalence countries
already near peak in 1999, r is small (near-plateau). For countries still climbing (e.g. India,
Nigeria, Thailand early) r is larger. This r drives the baseline (Task 1) projection.

## Exchange 4 — Parameter: untreated lifespan
Q: Years from infection to death with no treatment?
A: ~8–11 yr average (central ~10). 5–15% rapid progressors (2–5 yr); 5–10% long-term
non-progressors (15–20+ yr). Survival from AIDS onset ~1–2 yr.
**Model change:** Death rate d_i for untreated infected = 1/10 yr⁻¹ (central). Used in the
outflow of the infected compartment. ARV treatment reduces this substantially (see Task 2).

## Exchange 5 — Boundary: cost of ARV treatment failure
Q: Stopping ARVs — death, or just sicker temporarily?
A: Return to the fatal untreated trajectory (progressive, eventually fatal), not a transient
setback. Partial adherence → regimen failure + resistance.
**Model change:** In Task 2/3 ARV scenarios, a patient who drops out of treatment does NOT
recover to a healthy state; they re-enter the untreated infected compartment with the remaining
untreated-survival clock. This prevents the model from treating ARV as a reversible "cure."

## Exchange 6 — Parameter: 2006 foreign aid level
Q: Billions USD/yr foreign donors in 2006?
A: ~$2–3B/yr (bilateral + multilateral + philanthropic, PEPFAR + Global Fund), up from <1B in 2000.
**Model change:** Baseline annual foreign aid A_2006 = $2.5B (midpoint), the anchor of the
aid-financing trajectory in Task 2.

## Exchange 7 — Structural: aid trajectory 2006→2050
Q: Aid pattern — keep rising, level off, decline?
A: Rapid growth to ~2010, plateau for a decade or two, then gradual real-term decline
(donor fatigue, competing priorities, falling epidemic burden).
**Model change:** Piecewise aid trajectory A(t): (i) 2006→2010 exponential ramp from 2.5B to
~5B; (ii) 2010→2030 plateau ~5B; (iii) 2030→2050 slow decline ~4%/yr real. This A(t) is the
budget that funds ARV coverage and vaccine R&D.

## Exchange 8 — Structural: vaccine availability
Q: By 2006, had any preventive HIV vaccine been given to a human?
A: Yes for >10 yr (Phase I from ~1987), but NONE licensed or proven effective. AIDSVAX (2003)
and STEP showed no protection; none licensed by 2006.
**Model change:** Baseline (Task 2 scenario 2) assumes **no vaccine before ~2015**; vaccine
becomes available at 2018 (planning assumption, post-2006 R&D horizon), ramping coverage after.
Task 4's "accelerate R&D" shifts this availability date earlier (2015 with funded R&D).

## Exchange 9 — Parameter: vaccine efficacy
Q: Share of vaccinated people actually protected?
A: Modest, ~30–60% (RV144 2009 reference ≈31%, waning); optimistic licensed product 50–60%.
Not near-total.
**Model change:** Vaccine efficacy ε_v = 0.45 (central of 30–60%), applied to the infection
rate of vaccinated susceptibles. Combined with coverage fraction to scale the effective
infection rate downward.

## Exchange 10 — Parameter: duration of vaccine protection
Q: Lifelong protection, or waning with re-dosing?
A: Waning; protection declines over a few years, needs periodic boosters (RV144 efficacy fell
markedly within ~1 yr).
**Model change:** Vaccine protection is modeled as a **decaying shield**: efficacy ε_v(t) =
ε_v · exp(−λ_w · t_since_vaccination), λ_w ≈ 1/2 yr⁻¹ (half-life ~2 yr), with an annual booster
resetting the clock for those still covered. This makes vaccine impact a flow, not a one-time stock.

## Parameter provenance table (for solution.json)

| name | value | interval | source (exchange) |
|---|---|---|---|
| R0 / plateau fraction (hard-hit: BW, SW, LS, ZW) | 0.275 | [0.25, 0.40] | Exch. 2 |
| R0 / plateau fraction (other high-burden Africa) | 0.175 | [0.15, 0.30] | Exch. 2 |
| R0 / plateau fraction (lower-burden) | 0.10 | [0.05, 0.15] | Exch. 2 |
| Years <5%→peak (rise duration) | 12 | [10, 15] | Exch. 3 |
| Untreated survival (infection→death) | 10 yr | [8, 11] | Exch. 4 |
| Untreated death rate d = 1/10 | 0.10 yr⁻¹ | [0.09, 0.125] | Exch. 4 |
| Foreign aid 2006 | $2.5B | [2, 3]B | Exch. 6 |
| Aid peak (post-2010 plateau) | $5.0B | — | Exch. 7 (trajectory shape) |
| Aid decline post-2030 | 4%/yr real | — | Exch. 7 |
| Vaccine availability year (baseline) | 2018 | [2015, 2020] | Exch. 8 |
| Vaccine availability (funded R&D) | 2015 | — | Exch. 8 + Task 4 |
| Vaccine efficacy ε_v | 0.45 | [0.30, 0.60] | Exch. 9 |
| Vaccine waning half-life | 2 yr (λ_w=1/2) | — | Exch. 10 |
| ARV cost (DOTS) | $1,100/patient/yr | — | Task statement (given) |
| ARV resistance (adherence<90%) | 5% chance | — | Task statement (given) |
| Vaccine incremental cost | $0.75/dose (3-dose EPI) | — | Task statement (given) |

Dataset-derived values (not from exchanges): 1999 HIV+ counts per country, populations,
life expectancy, income classification, DTP3/TT2 vaccination coverage — all from the supplied
spreadsheets (see task dataset_description).
