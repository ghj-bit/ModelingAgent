# Expert Interaction Evidence — Task 2006_C (MM-Bench HIV/AIDS resource allocation)

Three exchanges were conducted, each a single common-sense question. Each reply
was converted into a concrete model element before the next exchange.

## Exchange 1 — structural fit (before building the intervention model)
**Question:** When countries get better at treating HIV with drugs, do they usually
get the total number of infected people to drop, or mostly to keep those infected
people alive and still carrying the virus?

**Reply (expert):** Effective ARV therapy sharply reduces AIDS deaths and keeps
infected people alive, so the number of people *living with* HIV (prevalence)
typically rises rather than falls. Incidence can decline somewhat because
treatment lowers viral load and thus transmission, but this effect is partial and
often offset by the larger pool of surviving infected people. Total infected count
usually does not drop; it stabilizes or grows, while deaths fall.

**How the reply changed the work:** The ARV intervention term was NOT modeled as
a direct reduction in the infected count. Instead ARVs (i) cut AIDS-related
mortality (extending survival, which *raises* the stock of people living with
HIV), and (ii) reduce onward transmission only partially (viral load reduction).
This made the "ARV only" scenario produce a rising, not falling, prevalence —
the physically correct signature. See model section: ARV acts on the mortality
rate d_ARV and on a transmission multiplier, never directly on dI.

## Exchange 2 — dominant bias / selection mechanism (built on Exchange 1)
**Question:** HIV is often hidden for years. In a poor country in 2003, could the
true number of infected people be higher or lower than the official figures, and
roughly why?

**Reply (expert):** Higher, usually substantially. Official figures were
underestimates: little testing and weak surveillance built from a small number
of sentinel sites (often antenatal clinics in urban areas) extrapolated to the
whole country; the long asymptomatic period meant most infected never sought
testing; stigma and under-reporting, with deaths attributed to TB/"slim"/malaria
rather than AIDS; coverage gaps in sparsely monitored or conflict-affected areas.
Direction clear (true > official); size an empirical judgment, often on the order
of tens of percent, larger where testing was weakest.

**How the reply changed the work:** Added an explicit bias/selection analysis and
a multiplicative undercount sensitivity factor U applied to the 1999 prevalence
base: baseline case uses U = 1.0 (reported figures), with a sensitivity band
U = 1.3–2.0 (tens-of-percent undercount) that scales the whole 2006–2050
trajectories upward. The bias is strongest in the low-income, weak-surveillance
countries (India, South Africa, Ukraine) and weakest in the high-income ones,
which is exactly where the sentinel/antenatal extrapolation was thinnest.

## Exchange 3 — validation / interpretation criterion (built on Exchange 2)
**Question:** For a UN deciding where to spend HIV/AIDS money, what matters more:
cutting new infections, or keeping already-infected people alive? Which should
come first?

**Reply (expert):** Cutting new infections matters more and should come first —
prevention is the only lever that changes the long-run trajectory; averting one
infection avoids its entire lifetime of future care and transmission costs.
Treatment is a recurring per-person-per-year cost with no endpoint, and (per
Exchange 1) it tends to raise prevalence. Treatment has a prevention benefit
(lower viral load), and in a mature generalized epidemic it is both a
humanitarian obligation and marginally cost-effective. Forced to rank: prevention
first, treatment second, funded to the extent resources allow after prevention.

**How the reply changed the work:** Fixed the decision rule and the framing of
Task 4's recommendation. The allocation is ranked prevention (vaccine) first and
ARV second, and the comparison across the three scenarios is presented in terms
of *trajectory* (2050 prevalence and lifetime averted infections) rather than
short-run mortality alone. The resource split and the "speed vaccine development
via R&D" recommendation for 2006–2010 are justified by this criterion.
