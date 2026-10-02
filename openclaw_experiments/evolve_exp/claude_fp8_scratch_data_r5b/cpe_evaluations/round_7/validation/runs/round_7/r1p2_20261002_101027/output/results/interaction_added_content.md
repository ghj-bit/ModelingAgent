# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence

## Exchange 1 — Structural Assumption
**Question (plain language):** In a country like South Africa or India, would the
AIDS epidemic keep rising in one steady, smooth way over many decades on its
own, or do external factors (policy, behavior change, a drug, an economic
shock) usually bend the trend abruptly, making the recent trend a poor guide to
the long future?

**Expert reply (summary):** Reject smooth extrapolation as a real-world
description. A generalized epidemic follows a *wave*: rapid rise, a peak, then
decline as the susceptible pool depletes and behavior changes — so the shape
itself bends without deliberate intervention. External forces (behavior change
e.g. Uganda in the 1990s, treatment rollout, economic shocks, policy) bend it
abruptly. The 1999–2005 slope is only a short-horizon baseline and should be
allowed to peak and turn over rather than rise indefinitely.

**How the reply changed the work:**
- **Decision:** Rejected a constant-growth / recent-trend extrapolation of the
  1999 HIV count. Instead the Task-1 baseline uses an **age-structured
  epidemic wave** (a susceptible→infectious dynamic across 5-year age bands
  15–49) in which the number living with HIV (PLHIV) rises, **peaks, then
  declines** as susceptibles deplete and the effective per-contact transmission
  falls. No country is allowed to grow without bound.
- **Parameter / constraint introduced (source: Exchange 1):** the baseline
  trajectory is required to be *unimodal* (rise→peak→fall) over 2006–2050,
  matching the expert's "wave" mechanism; the 1999–2005 observed slope is used
  only to calibrate the short-horizon rise, not to extrapolate.
- **Interval:** this structural rule holds over the full 2006–2050 horizon.

This directly addresses model validity (the functional form must reflect a
self-limiting epidemic, not unbounded growth).

## Exchange 2 — Causal Mechanism
**Question (building on Exchange 1):** When a country's AIDS case numbers
eventually level off and fall on their own (no new medicine, no vaccine),
what is the main driver — (a) the shrinking pool of uninfected young adults
left who could be infected, or (b) people/community actually changing behavior
(condoms, fewer partners, response to visible deaths) so risk per encounter
genuinely drops? And roughly how many years after the peak would a clear
decline take to appear?

**Expert reply (summary):** Neither alone. In real generalized epidemics both
operate, but (b) behavior change **dominates the downslope**; (a)
susceptible-pool exhaustion is the **weaker** of the two. In a generalized
epidemic prevalence rarely exceeds ~20–30% of adults, so 70–80% of the
high-risk age group is still uninfected — the pool is far from exhausted.
What bends the curve is behavior: condom use, partner reduction, and
critically the behavioral response to visible mortality (people change when
they see people dying). Uganda's 1990s decline was behavior, not saturation.
(a) still contributes: as prevalence rises, effective risk per encounter can
fall because infected people are more likely to mix within the infected
network (homophily), and mortality removes infected people from the
transmission pool. Timing: after peak, a clear decline typically takes
roughly **5–15 years**, often ~10; it is rarely abrupt — the peak is usually
a **plateau** that bends over a decade or more.

**How the reply changed the work:**
- **Decision:** The model's downslope is driven by a **behavior-change factor
  that decays the effective per-contact transmission rate β(t)**, triggered by
  the cumulative visible AIDS mortality and by rising prevalence — NOT by
  susceptible-pool exhaustion. I therefore do **not** rely on the classic SIR
  "susceptible depletion" mechanism as the primary driver.
- **Equation change (source: Exchange 2):** I added two explicit terms to the
  force-of-infection:
  1. A **behavioral reduction** β(t) = β0·exp(−κ·M_visible(t))·(1 − λ·prev(t)),
     where M_visible(t) is cumulative AIDS deaths (visible mortality) and
     prev(t) is adult prevalence. κ (sensitivity to visible mortality) and
     λ (behavioral response to prevalence) are the two behavior-change
     parameters.
  2. A **homophily / mixing reduction**: as prevalence rises, a growing share
     of high-risk contacts are already infected, so the effective new
     transmission scales with the uninfected-fraction of the network.
- **Constraint introduced (source: Exchange 2):** the epidemic peak is modeled
  as a **broad plateau**, and the post-peak decline is required to unfold over
  ~5–15 years (centered ~10), i.e. the model must not produce a sharp,
  single-year spike followed by a cliff. This is enforced by making κ and λ
  act gradually (slow adaptation) and by calibrating the behavior-response
  time constant to ~10 years.
- **Interval / value:** prevalence upper bound ~20–30% (adult) used as the
  realistic plateau ceiling; post-peak decline time-constant ≈ 10 years
  (range 5–15). Source: Exchange 2.

This addresses inference validity: the model does not claim the downslope is
caused by running out of susceptibles (a weaker, often-wrong mechanism); it
attributes it to behavior change plus a smaller saturation/mixing effect.

## Exchange 3 — Interpretation / Uncertainty Threshold
**Question (building on Exchanges 1–2):** When comparing two long-range
projections that differ mainly because of best-guess starting numbers and
rates, at roughly what gap size do you consider the difference real enough to
change a funding decision — is a 20% gap worth acting on, or do you only act
when the gap is much bigger (say 50% or more)?

**Expert reply (summary):** Treat a **20% gap as noise; act only when the gap
is roughly 50% or more**. The inputs (1999–2005 prevalence estimates,
behavior-change rates, death rates) carry country-level uncertainties easily
±20–30%, and those compound over 25–40 years of projection; a 20% difference
in a 2030 count is well inside that band and is not a signal about which
policy is better. What matters for a funding decision is not the point
estimate but **whether the ranking of options flips**. Act only when the gap
is (1) large (order 50%+), **and** (2) **robust across plausible values** of
the uncertain inputs (the conclusion does not reverse when the starting count
or the behavior/death rates are varied within their plausible ranges), **and**
(3) points the same way across multiple countries, not just one. A 20% gap
that survives none of these tests should not move money; a 50%+ gap that
survives all three should.

**How the reply changed the work:**
- **Decision rule (source: Exchange 3):** The Task-2/Task-4 policy
  comparison is evaluated against a **robust-dominance threshold**, not point
  estimates. A scenario is recommended over another only if, under the base
  case, it reduces (or changes) the cumulative number of people living with
  HIV / cumulative AIDS deaths by **≥ 50%** AND that superiority **survives**
  a ±30% perturbation of every uncertain input (starting HIV count,
  behavior-change rate, HIV mortality rate, ARV coverage, vaccine efficacy and
  timing) AND the same scenario wins in **multiple** selected countries
  rather than a single one.
- **Sensitivity protocol introduced (source: Exchange 3):** I run a
  ±30% sweep on the four uncertain inputs and report, for each country and
  scenario, whether the ranking is stable. A scenario difference of only ~20%
  is reported as within the uncertainty band and is explicitly **not** used
  to justify reallocating funds.
- **Interval / values:** uncertainty band on inputs ≈ ±20–30% (country level,
  compounding); decision threshold ≈ 50% on the outcome gap. Source:
  Exchange 3.

This addresses practicality / result analysis: the final recommendation is
framed in terms of robust, decision-relevant confidence rather than abstract
statistical precision.
