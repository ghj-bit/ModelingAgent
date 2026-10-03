# Expert Interaction Evidence — Task 2006_C (HIV/AIDS resource allocation)

Policy: mechanism → constraint → parameter. 10 exchanges, one question each.
Files: logs/operator_feedback/expert_question_N.md / expert_reply_N.json.

## Exchange 1 — structural (dominant transmission mechanism)
Q: In the fastest-spreading epidemics, was spread driven by many partners in the
population or by a few high-risk groups?
Reply: Generalized epidemics (sub-Saharan Africa) = population-wide heterosexual
transmission with multiple concurrent partnerships; prevalence saturates whole
adult cohorts. Concentrated epidemics (China, Russia, Vietnam) = high-risk groups
(IDUs, sex workers) with limited spillover.
Use in model: determines model form. South Africa, Nigeria, Ethiopia (generalized)
use a population-level SI-type incidence on the 15–49 susceptible pool. India and
the United States (concentrated, low general-population prevalence) use the same
form with a much lower per-partnership transmission rate, reflecting limited
spillover into the general population.

## Exchange 2 — constraint (what caps the rise)
Q: What caps how fast prevalence can rise within a generation — behavior or deaths?
Reply: Behavior first: new-partner rate offset by behavior change (fewer partners,
condoms, saturation of the most connected) and susceptible depletion. AIDS deaths
lag infection by ~8–10 years, so they act on a slower timescale; they set the
long-run plateau rather than capping the rise.
Use in model: the baseline (no-intervention) trajectory contains an
endogenous behavior-change/susceptible-depletion term so prevalence approaches a
plateau instead of growing indefinitely; AIDS deaths (delayed ~8–10 y) enter as
the slow exit that flattens prevalence at high levels.

## Exchange 3 — parameter (natural history, untreated)
Q: Typical years from infection to AIDS death untreated, and ARV extension?
Reply: Untreated adults in poor countries ~8–10 years (median ~9–10). Effective
ARV converts to chronic condition: extends life ~20–30+ years if started early
with good adherence; started at advanced AIDS, gain is only a few years.
Use in model: untreated AIDS progression rate = 1/9 y⁻¹ (interval 1/10–1/8 y⁻¹);
treated survival extends to near-normal (treated AIDS exit rate set to
background mortality), consistent with the life-expectancy series in the data.

## Exchange 4 — parameter (peak level)
Q: Typical peak adult prevalence in the worst-hit African countries?
Reply: ~20–30% typical; extreme cases (Botswana, Swaziland, Zimbabwe, Lesotho,
South Africa) ≥25–30% late 1990s–early 2000s; a few reached ~35–40% in the most
affected cohorts. Epidemic self-slowed at that level (susceptible depletion +
behavior change), plateau rather than continued climb.
Use in model: calibrates the plateau parameter. 1999 implied 15–49 prevalence
(South Africa ≈ 18.7%, Ethiopia ≈ 9.0%) sits below these peaks; the no-
intervention model is tuned so South Africa approaches ~25–30% adult prevalence
by the early 2000s and then bends, not beyond.

## Exchange 5 — parameter (time to flatten after peak)
Q: How long after the peak until the epidemic flattens on its own?
Reply: Prevalence flattens within ~5–10 years after the peak; incidence falls
first, then prevalence plateaus as deaths and new infections balance; worst-hit
countries plateaued by late 1990s–early 2000s, about a decade after the steepest
rise.
Use in model: sets the rate at which the behavior-change/susceptible-depletion
brake engages (time constant ~5–10 y after incidence peaks).

## Exchange 6 — parameter (ARV coverage in practice)
Q: In a poor country, what share of eligible infected adults actually receives
ARVs?
Reply: A small minority — typically a few percent to ~10% of clinically eligible,
often far less in the poorest settings; Appendix 1 shows most of sub-Saharan
Africa under 1–3%, a handful higher (Uganda ~6%, Botswana ~8%), near zero in
South Africa, Zambia, Zimbabwe, Mozambique, Namibia at the time. Uptake limited
by testing/linkage, drug supply, staffing, adherence support.
Use in model: ARV scenarios are supply-capped by foreign-aid funds at <$1,100 per
treated person-year (DOTS, problem statement) AND by a practical coverage ceiling
of ~10% of prevalent infected in low-income countries in the near term, rising
slowly as systems build; this double cap drives the allocation analysis.

## Exchange 7 — parameter (vaccine uptake ramp)
Q: When a new HIV vaccine is introduced, how fast does coverage climb in the
first several years?
Reply: Slow then accelerating over ~5–15 years: years 1–2 pilot, a few percent to
~10–20%; years 3–5 rapid scale-up to ~30–60%; years 5–15 gradual approach to the
steady-state ceiling set by the country's routine immunization performance
(DTP3 for new cohorts, TT2 for older cohorts); new antigens lag established
vaccines by several years.
Use in model: vaccine coverage C(t) follows a logistic ramp with ~5 y time
constant reaching the country's DTP3 (new-cohort) / TT2 (older-cohort) ceiling
from the vaccination dataset, starting at the assumed availability year.

## Exchange 8 — parameter (vaccine efficacy and duration)
Q: Realistic protection per vaccinated person; does it last for life?
Reply: Modest: ~50–60% susceptibility reduction is the optimistic first-
generation target (RV144 showed ~31%); 90–100% sterilizing not realistic.
Protection wanes over ~3–5 years, needing boosters; >10 y durability not
reasonable; real-world efficacy below headline figure due to subtype mismatch.
Use in model: vaccine efficacy E = 0.5 on susceptibility (interval 0.3–0.6);
protection wanes after 4 y (re-vaccination/booster assumed through EPI);
no herd immunity is assumed (partial efficacy + heterogeneous mixing).

## Exchange 9 — parameter (foreign-aid scale)
Q: How much international HIV aid per year in the early 2000s, and was it
growing?
Reply: Order of $1–2 bn/yr (~$1.5 bn around 2002–03), mostly bilateral plus
UNAIDS/WHO programs; growing but lumpy — Global Fund (2002, first grants
2003–04), PEPFAR (announced 2003, funds from 2004), World Bank MAP; by mid-
2000s $5–8 bn/yr, several-fold in a few years.
Use in model: Task-2 resource curve starts at ~$1.5 bn/yr (2006, six selected
countries' realistic share of the developing-world total), with step increases in
2004–05 (PEPFAR/Global Fund) and smooth growth to a few billion by the 2010s,
then slower growth; ARV treatment counts = funds/($1,100/person-year).

## Exchange 10 — structural (treatment vs prevention weighting)
Q: Where did the epidemic get its biggest lasting help — treating the sick or
preventing new infection?
Reply: Prevention, over the long run, though on different timescales and not
substitutes. ARV gave immediate visible gains (mortality cut, some transmission
reduction via viral load) but cannot end an epidemic — must be continuous and
indefinite, leaves susceptibles untouched. Prevention is what bends the curve
downward (Uganda 1990s, Thailand 100% condom program, before mass treatment).
Treatment's lasting contribution: keeping infected alive and reducing
transmission; prevention's: ending epidemic growth.
Use in model: shapes the Task-4 allocation rule — ARV as immediate mortality
relief and transmission-reduction complement; vaccine/prevention as the
long-run curve-bender. Also justifies the combined scenario interacting both
effects (ARV lowers incidence via reduced viral load ~50% among treated)
without double counting: they act on different pools (treated vs susceptibles).

## Exchange-usage statement
Every reply above became a parameter or a modeling rule (listed in solution.json,
mathematical_modeling_process, with intervals). No exchange produced prose only;
each reply's use is stated in the solution container where the value is consumed.
