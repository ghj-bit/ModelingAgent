# Interaction Evidence — 2006_C

Ten expert exchanges, one question each, each reply converted into a model
parameter or decision rule before the next exchange. Files:
`logs/operator_feedback/expert_question_N.md` / `expert_reply_N.json`.

## Exchange 1 — country selection criterion
- **Q:** When judging which countries are "most critical" for an HIV/AIDS effort,
  which single number matters most: total cases or share of the population infected?
- **Reply (gist):** neither alone; for a UN resource-allocation problem the
  defensible single number is total cases (resources reach people, absolute scale
  of need); prevalence share is a secondary severity indicator.
- **How it was turned into work:** Task 1 selection ranked candidate countries
  per continent by absolute HIV+ count (1999 sheet) with prevalence share
  reported alongside. Selected: South Africa, India, Ukraine, USA, Brazil,
  Australia (`code/select_countries.py`, `data/country_selection.csv`).

## Exchange 2 — foreign-aid share for a middle-income country
- **Q:** For a country like South Africa, roughly what share of AIDS care can
  foreign aid realistically fund in the 2006-2050 period?
- **Reply (gist):** small minority, on the order of 10-25% of total need, often
  less; upper-middle-income countries are largely self-financed; donors
  concentrate on low-income, high-burden countries; treat aid as a marginal
  supplement.
- **How it was turned into work:** South Africa's 2006 aid set low (25M USD) in
  `AID_2006` of `code/model.py`; Brazil likewise modest (35M USD); the two
  high-income countries (USA, Australia) are modeled as donors, not recipients,
  self-funded at the same per-person costs.

## Exchange 3 — ARV program ramp shape
- **Q:** When antiretroviral programs in poor countries scale up, does patient
  care start small and grow gradually, or start large at once?
- **Reply (gist):** gradual, starting small — a decade-or-more S-shaped ramp
  limited by delivery capacity (staff, labs, supply chains, adherence support),
  not just money.
- **How it was turned into work:** ARV coverage in `model.py` uses a logistic
  ramp `R(t) = R(t-1) + (C(t)-R(t-1))*s_arv` with `s_arv = 0.25/yr` and 2006
  starting coverage taken from Appendix 1 (0-2% in most selected countries),
  not a step jump.

## Exchange 4 — epidemic growth shape
- **Q:** In a country where HIV runs rampant and uncontrolled, does the number of
  people living with the virus keep rising steadily, or level off?
- **Reply (gist):** it levels off — logistic S-shape; plateau once adult
  prevalence reaches roughly 15-25% in generalized epidemics; deaths lag
  infections by years so the living count can still rise before it too levels off.
- **How it was turned into work:** the model's saturation term
  `D(t) = 1 - I(t)/K` with per-country plateau prevalence
  `PREV_MAX` (5-20% of the 15-49 population) implements the plateau; this is the
  mechanism behind the Task 1 "no intervention" projections.

## Exchange 5 — consequence of drug resistance
- **Q:** If a common HIV drug stops working because of resistance, what happens
  to the patients relying on that treatment?
- **Reply (gist):** they deteriorate and die on roughly the untreated timeline —
  fully so where second/third-line therapies are unavailable (poor countries,
  per the problem's assumption); in rich countries patients survive by regimen
  switching.
- **How it was turned into work:** Task 3 scenarios move resistant patients into
  `Ir` with no ARV mortality benefit (full progression rate) and resistance only
  applies outside the high-income self-funded countries (`resist and key not in
  DOMESTIC_FULL`), matching the problem's "prohibitively expensive outside
  Europe, Japan, USA" clause.

## Exchange 6 — total aid for the six-country group
- **Q:** Taking all six selected countries together, roughly how much foreign
  aid per year would realistically be available for HIV/AIDS starting in 2006?
- **Reply (gist):** a few hundred million to roughly $1-2 billion per year,
  rising over the following decade; only India (low income) and Ukraine
  (lower-middle) are genuinely aid-eligible; global 2006 donor funding was only
  ~$2-3B across all recipients.
- **How it was turned into work:** `AID_2006` allocations sum to ~$410M in 2006
  (India 250M, Ukraine 100M, Brazil 35M, South Africa 25M, USA/Australia 0),
  within the expert's low-to-mid range; grown at real 4%/yr (`aid_g`), with a
  sweep available (`--sweep AID_G=...`).

## Exchange 7 — vaccine protection duration
- **Q:** How many years of continuous protection would a reasonably good HIV
  vaccine be expected to give before a booster dose would be needed?
- **Reply (gist):** on the order of 3-5 years (plausible range ~2-10); no HIV
  vaccine has shown durable efficacy; a defensible modeling choice is ~5 years
  with re-vaccination.
- **How it was turned into work:** `dv = 5.0` years in `model.py` (baseline),
  with cohort-based protection expiry (`frac = min(1, age/dv)`); a sweep over
  duration is available via `--sweep DV=...`.

## Exchange 8 — allocation between treatment and prevention
- **Q:** With a limited HIV/AIDS budget, should more money go to treating people
  already infected, or to vaccinating healthy people?
- **Reply (gist):** neither extreme — fund treatment to a meaningful coverage
  level (humane imperative, partially preventive via viral load), but the
  marginal dollar goes to the vaccine, which is the only intervention that can
  end rather than manage the epidemic; the vaccine share should rise over the
  2006-2050 horizon.
- **How it was turned into work:** Task 4 recommendation (1): maintain ARV
  coverage to a meaningful level in every scenario while directing the marginal
  resource (and the 2006-2010 R&D acceleration) to the vaccine; the model's
  `both` scenario quantifies the combined benefit that justifies this split.

## Exchange 9 — R&D acceleration of the vaccine date
- **Q:** If rich countries spend heavily on HIV vaccine research between 2006
  and 2010, by roughly how many years could the vaccine's arrival be pulled
  forward?
- **Reply (gist):** modest — roughly 2-5 years, not a decade; arrival is gated
  by scientific discovery, not mainly by money.
- **How it was turned into work:** Task 4 scenario: baseline vaccine
  availability `y_vac = 2025`; accelerated R&D moves it to 2020-2023. The sweep
  `--sweep Y_VAC=2020,2025,2030` (logs/sweep_yvac.log) quantifies the gain:
  e.g. India 2050 prevalence 3.34M (2025) vs 3.10M (2020), cumulative new
  infections 2006-50 falling ~0.9M; South Africa 2050 2.90M vs 2.85M.

## Exchange 10 — donor coordination failures
- **Q:** When many foreign donors fund the same country's AIDS programs, what
  goes wrong if their programs are not coordinated?
- **Reply (gist):** duplication and fragmentation — parallel clinics/labs/supply
  chains/reporting systems; overlap and gaps; diluted accountability; strained
  local capacity; distorted priorities; unsustainable parallel structures that
  collapse when a donor exits; hence one plan, one authority, one monitoring
  system.
- **How it was turned into work:** Task 4 recommendation (3): single national
  AIDS plan with one coordinating authority and harmonized reporting ("three
  ones"), donor funds channeled through the national plan, with continuity
  safeguards for treatment programs at donor exit.
