# Interaction Evidence

Three expert exchanges, one question each, in the required order.

## Exchange 1 — operational definition of the trend measure

**Question** (full text in `logs/operator_feedback/expert_question_1.md`): When public
agencies tracked how fast HIV was spreading in the 1990s, which kind of measurement did
they rely on most to decide whether an epidemic was still growing, and why — the single
1999 country stock of HIV-positive people, or the serial prevalence measurements among
urban women of childbearing age?

**Reply (summary)**: Agencies relied on the serial antenatal-clinic (ANC) prevalence
time series, not the single-year stock count. A one-year count is a stock, not a trend;
the 1999 stock itself was largely modeled from the same surveillance data. Serial
measurements from the same clinics give direction and speed of change; pregnant women
were the practical sentinel group because antenatal visits already test routinely,
giving comparable samples across years. Caveat: the data are biased toward urban,
sexually active women and under-represent men, rural areas and high-risk groups.

**How the reply became work** (in `code/calibrate_g.py`):
- The epidemic-growth constant g is estimated from the *serial* ANC prevalence series
  (slope of log-prevalence vs. year, mid-decade years 1992/1996/1999), not from the
  1999 stock. g_ref = 0.2172 = median over the 6 African countries with >= 2 ANC
  observations (Benin 0.415, Niger 0.384, Namibia 0.220, Cameroon 0.215, Zambia 0.064,
  Tanzania -0.037).
- The 1999 UNAIDS stock is used only as the initial *level* I(1999) of the infected
  pool, consistent with the reply that it is a derived level.
- Known bias (urban women) is carried into the limitations: g_ref is a continent
  surrogate for the 6 selected countries, none of which has its own ANC series in the
  file; sensitivity to g is bounded below (g clipped to [0, 0.25]).

## Exchange 2 — causal direction: what drives incidence vs. deaths

**Question** (`expert_question_2.md`): In practice, what is the one factor that mostly
decides whether new infections keep rising year after year, and what factor mainly
decides how many infections turn into AIDS deaths in the same period?

**Reply (summary)**: The factor that decides whether new infections keep rising is the
effective reproduction number — whether each infected person infects more or fewer than
one new person — driven by behavior/contact patterns and prevention coverage, not by
the death rate. The factor that decides how many infections turn into AIDS deaths in a
given period is how long people live with HIV before dying (the infection-to-death
progression rate), which is strongly modified by ARV availability: without treatment
roughly a decade from infection to death; with treatment deaths are pushed far into
the future.

**How the reply became work** (in `code/model.py`):
- Incidence is modeled by a transmission term NewInc = beta * S * I / (S+I) with beta
  calibrated to the observed growth — i.e., the model's dominant mechanism is
  transmission dynamics (R>1 while g>0), not mortality.
- Deaths are modeled as a *delayed* survival outflow: Out_u = I/TAU_P with TAU_P = 10 yr
  (untreated infection-to-death, per the reply's "roughly a decade") and
  Out_t = I/TAU_T with TAU_T = 25 yr for the ARV-treated fraction — the reply's
  "with treatment, deaths are pushed far into the future". AIDS deaths in a year are
  therefore decoupled from same-year incidence, exactly the causal structure stated.
- ARV acts on the survival channel (TAU_P -> TAU_T for the covered share), and only
  secondarily on incidence through the reduced infected pool — not the other way round.

## Exchange 3 — decision-relevant robustness threshold

**Question** (`expert_question_3.md`): When planning HIV spending over decades, what
makes a projection of future infections trustworthy enough to actually budget on, and
what sign would you look for that a projection has become unreliable?

**Reply (summary)**: A projection is budgetable when it is built on a transmission
model whose parameters are anchored to observed data (measured prevalence trends,
prevention/treatment coverage, survival time) and is re-fitted as new surveillance
rounds arrive; trust comes from reproducibility from those inputs and from near-term
(1-3 yr) predictions having matched subsequent observation. Long horizons are only as
good as the assumption that the key drivers evolve plausibly. The sign of unreliability:
short-horizon predictions start missing systematically in one direction — observed
values persistently diverging from the projected path, or the model needing
ever-larger parameter adjustments to stay on track. Persistent one-sided error means a
structural driver has changed; do not budget on it until re-estimated.

**How the reply became work**:
- The near-term check required by the reply: the no-intervention model's 2006-2020
  path was verified against the 1999 baseline and the calibrated g (the model is
  constructed to match the observed trend by construction, which is the closest
  "near-term match" available with data ending in 1999/2005).
- The one-sided-error warning is operationalized as the sensitivity blocks in
  `code/model.py`: beta x0.5/x1.5 (T1 2050 moves 2-12x depending on how far the country
  is from its carrying level; i.e., the projection is *structurally* sensitive to the
  transmission parameter in low-prevalence countries), ARV adherence 0.70/0.95 (T2_arv
  2050 moves little in budget-limited countries, large in Australia), and vaccine
  availability 2013 vs 2015 (T2_vac 2050 moves 5-22%). Where these bands diverge in
  one direction, the solution flags the result as a signal only within the stated
  assumption, not a budgetable point estimate.
- The "re-fit as surveillance arrives" condition is stated as a model limitation: the
  projection is valid only until the first post-2006 ANC round contradicts the near-term
  path; at that point the beta and g parameters must be re-estimated, which the code
  supports (single-constant calibration).

## Note on what was NOT requested
No feedback was requested for coding, debugging, derivations, or computation. All
three questions were common-sense questions about how the epidemic is actually
measured, what drives it, and when a projection stops being trustworthy.
