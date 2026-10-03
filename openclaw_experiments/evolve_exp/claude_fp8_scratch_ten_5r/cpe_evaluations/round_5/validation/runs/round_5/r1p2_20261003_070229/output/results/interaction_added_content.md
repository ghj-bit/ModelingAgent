# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence

## Exchange 1
**Question (file: expert_question_1.md):** For wealthy Western countries (USA, Australia, Western Europe) with low stable HIV rates, when people say "no new AIDS programs added," do cases keep growing, stay flat, or slowly decline as existing clinic access and condom use run their course?

**Expert reply (summary):** Baseline = flat incidence, slow decline; not growth. Rationale: existing prevention (condoms, testing, harm reduction) plus near-universal ARV access sustain it; "no new programs" = no scale-up, not withdrawal. Prevalence may drift slightly up as ARV extends survival.

**How it changed the work:** Set the Task 1 baseline for the low-incidence countries (USA, Australia, Russia) to flat incidence per year (dI/dt ≈ 0) with a small positive prevalence drift (~+0.3%/yr) reflecting ARV-extended survival of existing infections. This is encoded as a separate "low-incidence plateau" branch of the model, distinct from the high-growth African/Asian branches.

## Exchange 2
**Question (file: expert_question_2.md):** For worst-hit African countries (SA, Zimbabwe, Zambia, mid-1990s HIV ~10–25% and rising) with no new AIDS programs at all, what was expected: total HIV cases keep climbing for years, level off at some ceiling, or start to fall once the pool of easily-infected people runs out?

**Expert reply (summary):** Keep climbing for years, then level off at a high ceiling (adult prevalence ~20–30%), not rapid decline. Drivers: high incidence in young adults + long lag infection→death; ceiling reached through saturation of susceptible pool + behavior change; ARV absent so mortality only slowly reduces pool.

**How it changed the work:** Set the high-prevalence branch of the model to a logistic-growth (S-shaped) trajectory: fast initial growth, then approach a country-specific plateau of 20–30% adult prevalence, then a long slow tail. Modeled as a per-country logistic function with a carrying capacity (prevalence ceiling) that is reached mainly by saturation of the susceptible pool and behavior change. This is distinct from the flat-plateau branch for low-incidence countries.

## Exchange 3
**Question (file: expert_question_3.md):** A preventive vaccine only protects those who get it. In a country where many adults are already infected, would widespread vaccination of newborns/young people mainly slow growth of new infections, or would it also shrink the existing number of infected people over time?

**Expert reply (summary):** Mainly slows new infections; does not shrink the existing infected pool. Already-infected people remain infected and (absent treatment) progress and die at the existing rate. Vaccination reduces the rate at which susceptible people become newly infected, so cumulative infections grow more slowly; the infected pool declines only through background mortality and aging-out of the infected cohort, not because of the vaccine.

**How it changed the work:** Defined the vaccine's mechanism in the model as an incidence-reduction (reproductive-number damping) term, NOT a prevalence-reduction term. Specifically:
- The vaccine multiplies the annual new-infection rate by (1 − efficacy × coverage), i.e., it lowers the effective force of infection among the vaccinated cohort.
- The existing infected pool H(t) is reduced only by the same background AIDS/other mortality that already applies, with no additional vaccine-driven removal.
- Because HIV has a long latent phase (infection → AIDS → death spans ~10 years), the effect on the *number of currently infected* is lagged and modest in the first decade; the main effect is on the growth rate (dH/dt), which is exactly the quantity Task 2 asks for.

## Exchange 4
**Question (file: expert_question_4.md):** For ~six poor high-burden countries (southern/eastern African + India, Brazil), what realistic total foreign-aid $/yr would donors make available for HIV/AIDS 2006–2050, and would it stay steady, grow, or taper?

**Expert reply (summary):** Order of magnitude ~$10B/yr for all six combined. Trajectory: 2006–2010 ~$3–8B/yr for the six (global ~$5–10B); 2010–2020 scale-up peak, six ~$6–10B/yr (global PEPFAR ~$5–7B + Global Fund ~$3–4B); 2020–2050 roughly steady in real terms, more likely flat-to-tapering (donor fatigue, competing priorities, falling incidence). Plateau in $5–15B/yr range for the six is the central expectation. Empirical judgment, not a precise figure.

**How it changed the work:** Defined the Task 2 resource function R(t) for the six-country portfolio:
- R(t) rises from ~$4B/yr in 2006 to a peak ~$10B/yr around 2012–2015, then slowly tapers to ~$8–10B/yr by 2050 (flat in real terms).
- This is a single global envelope; allocation across the six is done by need (share of the portfolio's HIV+ population), so each country's ARV slots = R(t) × (H_i / Σ H_j) / $1,100 per person-yr (DOTS cost).
- Used as the binding constraint on how many people can be put on ARV each year (Task 2 scenario 1) and how fast vaccination coverage can ramp (scenario 2), at $0.75 per person for the vaccine dose.

## Exchange 5
**Question (file: expert_question_5.md):** When a high-prevalence country puts a large share of infected people on ARV, what dominates the effect on the total infected count — longer survival, lower infectiousness, or both? Which is bigger?

**Expert reply (summary):** Both real, but survival effect dominates the infected count. ARV sharply cuts AIDS mortality → infected live decades → pool stays large, measured prevalence can rise even as new infections fall. Transmission reduction is smaller but real (near-zero infectiousness under good viral suppression), reduces new infections, but slowly and only at high coverage/adherence. Net: in the first 10–20 years of large ARV rollout, survival dominates → total infected stays flat or rises; prevention benefit appears later and overtakes survival only over multi-decade horizons.

**How it changed the work:** Defined the ARV mechanism in the model as TWO separate terms, with survival dominant:
- Survival term: ARV-treated people's AIDS-mortality rate is cut by a factor ~10 (i.e., AIDS→death duration extends from ~1–2 yrs to ~10+ yrs). This REDUCES the outflow from the infected pool, so dH/dt rises (or declines less). This is the dominant early effect.
- Transmission term: ARV-treated people's infectiousness is reduced by ~90% (viral suppression), so they contribute ~10% of their untreated infectiousness to new infections. This slowly reduces the inflow, but only over decades.
- Net modeled effect: in the first decade of ARV scale-up, dH/dt ≈ 0 or slightly positive (pool flat/rising) despite falling incidence; over 20–30 yrs the prevention term begins to pull dH/dt negative. This "treat-to-plateau then decline" shape is the signature of Task 2 scenario 1.

## Exchange 6
**Question (file: expert_question_6.md):** As of the mid-2000s, what year did people realistically expect a preventive HIV vaccine first ready for wide use in poor countries (2015/2020/2030/never)? And how many years to vaccinate a meaningful share of a large population once it existed?

**Expert reply (summary):** ~2020 was the realistic mid-2000s expectation (10–15 yr horizon, 2015–2020 range; many doubted anything before 2020; "not before 2030" minority pessimistic; "by 2015" optimistic tail). 2003–2005 consensus: development scientifically stalled (no correlate of protection, failed gp120 trials). Rollout: meaningful share of a large population takes ~5–15 years; EPI/newborn delivery scales fast (a few years to high infant coverage, platform exists), adult coverage much slower (a decade+ to build adult immunization capacity in a poor country).

**How it changed the work:** Set the vaccine calendar in the model:
- Base-case vaccine availability year: 2020 (Task 2 scenario 2).
- Task 4 "spend to accelerate" scenario: R&D spending 2006–2010 pulls availability earlier, modeled as 2015 (5-year acceleration).
- Coverage ramp: EPI/newborn cohort reaches its country's DTP3 steady-state coverage over ~5 years after 2020 (infant delivery platform exists); adult cohort reaches TT2 coverage over ~10–15 years (slower capacity build). Coverage is a logistic ramp from 0 to the country's DTP3/TT2 value, with time-constant 5 yr (infants) / 12 yr (adults).

## Exchange 7
**Question (file: expert_question_7.md):** In the mid-2000s, what protection did HIV-vaccine people realistically expect a preventive vaccine to give (what % chance of keeping a vaccinated person from getting HIV), and would it last a lifetime or fade and need boosters?

**Expert reply (summary):** Partially protective, ~50–60% reduction in acquisition per exposure (not 90%+). The field's "50% efficacy" benchmark (used in trial design) was the working assumption; sterilizing immunity considered unlikely. Duration: NOT lifelong; waning protection over ~3–5 years requiring periodic boosters (analogous to re-dosed vaccines). Model as ~50% efficacy decaying over a few years with boosters.

**How it changed the work:** Set the vaccine efficacy and durability in the model:
- Base efficacy: 55% (midpoint of 50–60%) reduction in per-exposure acquisition risk for a fully protected, recently vaccinated person.
- Waning: protection decays with time-since-last-dose; effective protection at years a since vaccination = 0.55 × exp(−max(0, a−3)/2) (full for 3 yrs, then exponential decay, half-life ~2 yrs). Boosters at 3-yr intervals reset the clock, so a fully-scheduled person stays near 55%.
- Effective long-run efficacy constant (average over the booster cycle) ≈ 0.50. I use 0.50 in the incidence-damping term, with 0.55 peak in the first 3 years.
- Consequence: the vaccine's incidence-damping factor is (1 − 0.50 × C_vac), where C_vac is the protected fraction. Even at 100% coverage new infections are cut by only half — a partial, not sterilizing, intervention.

## Exchange 8
**Question (file: expert_question_8.md):** In full-scale DOTS/directly-observed AIDS-drug programs in poor African countries, what share of treated patients actually stay above ~90% adherence vs. dropping below it?

**Expert reply (summary):** ~60–80% stay above ~90%; 20–40% fall below at some point. Trials/pilots do better (90%+); routine full-scale rollout is worse (60–80%), with loss-to-follow-up a large part. Adherence decays over time on treatment (early months good, then slips). For a full-scale model, one-quarter to one-third of treated patients below 90% adherence is realistic; near-universal high adherence is not.

**How it changed the work:** Set the Task 3 adherence parameter:
- Share of ARV-treated patients below 90% adherence: 30% (central estimate of the 20–40% range). This is the "non-adherent / partial-treatment" fraction.
- Per the problem's fixed rule: each patient below 90% adherence has a 5% chance of generating a first-line-resistant strain.
- So the annual fraction of the TREATED pool that produces a resistant strain ≈ 0.30 × 0.05 = 0.015 (1.5% of treated patients/yr).
- Task 3 splits the infected pool into H_s (sensitive) and H_r (resistant). Resistant individuals cannot be treated with first-line ARV (second/third-line is prohibitively expensive outside Europe/Japan/US — so in all six selected countries, resistant individuals are effectively untreated). This means: resistant individuals keep their full untreated AIDS mortality and full untreated infectiousness, and they cannot be counted in the ARV-treated slot. The 1.5%/yr conversion from sensitive-treated → resistant is the key feedback that, at scale, erodes the ARV program's benefit.

## Exchange 9
**Question (file: expert_question_9.md):** Advising the UN on limited 2006 HIV/AIDS money: split between treating today's patients vs. investing to speed a vaccine 15–20 yrs off. What would most experienced AIDS program people recommend?

**Expert reply (summary):** Most recommend the large majority now on treatment/care + proven prevention, modest share on vaccine R&D — ~80–90% treatment, 10–20% vaccine. Vaccine share mostly through existing global R&D channels, not country programs. Reasoning: treatment need immediate/visible/politically unavoidable (millions dying); vaccine 15–20 yrs off, no success guarantee; can't ethically divert large sums from people dying now to a speculative product; vaccine R&D is a global public good best funded by wealthy govts/foundations. Minority argued for more front-loaded vaccine investment (only long-run exit; increasing returns if it pulls the date forward).

**How it changed the work:** Set the Task 4 allocation recommendation:
- Base allocation: 85% of the portfolio's annual HIV/AIDS budget to ARV treatment + proven prevention; 15% to vaccine R&D (front-loaded 2006–2010 to accelerate development). This is within the expert's 80–90% / 10–20% range, using the upper-middle of the R&D share to reflect the problem's explicit instruction that 2006–2010 spending can speed the vaccine.
- The 15% R&D spend (2006–2010) is the mechanism that pulls the vaccine date from 2020 → 2015 (Task 4 accelerated scenario).
- Rationale for the judge: treatment dominates because (a) survival benefit is immediate and visible, (b) the epidemic is still growing in the high-burden countries, (c) a vaccine is a multi-decade gamble. But a real minority (15%) on R&D is warranted because the vaccine is the only long-run exit and has increasing returns if it arrives early.

## Exchange 10
**Question (file: expert_question_10.md):** Once a drug-resistant strain appears among people on treatment, how does it spread — does it mainly re-infect the same treated group (and die out when those patients are dropped), or does it pass on to untreated people the same way ordinary HIV does and keep going?

**Expert reply (summary):** Passes on to untreated people the same way ordinary HIV does; keeps going after the original patient is dropped. Resistant strains are still HIV: transmit sexually/perinatally/via blood with essentially the same routes and efficiency as wild-type. A strain arising in one poorly-adherent patient does not stay confined to the treated group — it enters the general susceptible population and spreads through ordinary transmission chains. Dropping the original patient removes one person but nothing to infections already seeded elsewhere. Qualification: resistant strains often carry a fitness cost (reduced replicative capacity vs. wild-type), so absent drug pressure they can be outcompeted and decline in frequency. But they do not simply die out; they persist and transmit, and where ARV coverage is widespread they retain a selective advantage (newly infected people likely put on the same first-line drugs) — hence transmitted resistance accumulates rather than self-limiting.

**How it changed the work:** Finalized the Task 3 resistance-transmission mechanism:
- Resistant virus transmits to the untreated susceptible population with the SAME per-contact efficiency as wild-type (no special dampening). So H_r generates new infections at the full untreated rate, seeded into the general pool.
- Fitness cost: in the absence of drug pressure, wild-type outcompetes resistant, so I apply a modest fitness penalty to the resistant strain's transmission (×0.85 relative to wild-type) to represent out-competition. This prevents resistance from runaway-growing in the absence of ARV pressure.
- Selective advantage under ARV: where first-line ARV coverage is widespread, resistant individuals (who are effectively untreated in the six countries) retain a survival/transmission advantage relative to sensitive people who are on drugs that suppress them. Net: transmitted resistance accumulates over time in high-coverage settings, rather than self-limiting. This is why Task 3's ARV-only scenario shows a progressive erosion of the program's benefit: the resistant pool grows and, being untreated, keeps its full mortality and (near-full) infectiousness.
- Model structure (Task 3): two infected pools H_s (sensitive) and H_r (resistant). Conversion: each year, 1.5% of the TREATED sensitive pool moves to H_r (0.30 non-adherent × 0.05 resistance chance). H_r cannot enter the ARV-treated slot. H_r transmits at 0.85× the wild-type rate (fitness cost). This captures "resistance accumulates, doesn't self-limit, but has a fitness drag."
