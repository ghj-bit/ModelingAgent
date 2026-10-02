# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction evidence — problem 2006_C

Three expert exchanges, one question each, in the order asked.

## Exchange 1 — operational mechanism of spread

**Question (as asked):** In the hardest-hit countries, did HIV/AIDS infections mostly spread through everyday contact (steady spread), or in waves tied to outbreaks and hotspots?

**Reply (summary of what the expert said):** No everyday-contact spread. Transmission ran through sexual networks in concentrated waves tied to hotspots (transport corridors, mining and trading towns, sex workers and their clients), with rapid explosive growth in the 1980s–1990s and then outward diffusion into the general population. Southern/East African countries (Botswana, Zimbabwe, South Africa, Swaziland) show wave-like saturation: prevalence climbing steeply then plateauing.

**How the reply changed the work (implemented in `code/model.py`):**
- The incidence term was made wave-shaped rather than a constant rate:
  `R(t) = Rmax·exp(−κ·x(t))` with wave position `x(t) = x0 + (t − 2006)`,
  i.e. a surge that decays exponentially as the core sexual networks saturate
  (Exchange 1, "waves … then plateauing").
- The wave position `x0` is solved from each country's 2006 prevalence
  (`x0 = −ln(1−p0)/κ`), so high-prevalence countries enter the post-saturation
  decay phase while low-prevalence countries are still near the top of the
  wave — the "explosive growth → diffusion" structure, per country.
- This replaced the first (rejected) design in which all countries shared one
  uniform constant incidence rate and grew identically.

## Exchange 2 — causal hierarchy of the late-1990s plateau

**Question (as asked):** Why did some African countries see infection levels level off in the late 1990s, like Kenya and Uganda?

**Reply (summary of what the expert said):** Two dominant mechanisms: (1) saturation of the core transmission groups — once prevalence among sex workers, clients and their partners is very high, susceptibles run out and incidence falls without any intervention (Kenya, Uganda had passed their steepest phase by the mid-1990s); (2) behavior change plus AIDS mortality — Uganda's early prevention campaigns reduced partner change and raised condom use, while AIDS deaths removed infected people from the pool, flattening measured prevalence. Caveat: a prevalence plateau is not the same as falling incidence — deaths can hold prevalence flat while new infections continue (Kenya: plateau largely saturation + mortality; Uganda: saturation + genuine behavioral decline).

**How the reply changed the work (implemented in `code/model.py`):**
- Added a behavioral-decline factor `exp(−δ·max(0, t−1990))` on the incidence
  term, `δ = 0.02 /yr`, applied to the general-epidemic country in the selected
  set (South Africa); zero for the concentrated-epidemic countries.
- AIDS mortality was made an explicit state equation: `A_{t+1} = A_t +
  (new_infections)/10 − A_t·d_AIDS·(1−coverage·E_ARV)`, with AIDS deaths
  `d_AIDS = 0.30/yr` removing infected from the pool — the mortality arm of the
  plateau, per the expert's "deaths removed infected people from the pool".
- The "prevalence flat ≠ incidence falling" caveat is carried into the outcome
  analysis: reported 2050 levels are prevalence-like stock measures, and the
  scenario comparisons are read on the stock and on the trend sign, not as
  incidence claims.

## Exchange 3 — decision-relevant uncertainty threshold

**Question (as asked):** For planning AIDS funding to 2050, how off can projections of infection numbers be before planners would not trust them?

**Reply (summary of what the expert said):** No formal threshold. Practical tolerance: roughly a factor of 2 over a 10–15 year horizon; ±20–30% over 5–10 years is still usable for allocation. Beyond about 2× (100% high or 50% low), or a wrong direction of change, planners treat the projection as untrustworthy for committing funds. Over 2006–2050, errors of 3–10× are expected and acceptable — long-horizon numbers are for strategy and relative prioritization, not line-item budgets. The binding constraint is whether the *ranking of countries* and the *sign of the trend* are stable under reasonable assumptions.

**How the reply changed the work (implemented):**
- Validation was structured as a ranking/trend-sign stability test, not a
  point-estimate accuracy test. Sweeps of `K_RATE` (0.05–0.20), `RMAX`
  (0.05–0.20) and `E_ARV` (0.30–0.80) were run (`logs/sw_k2.log`,
  `logs/sw_r2.log`, `logs/sw_e2.log`); the 2050 country ranking and the
  post-2015 declining trend sign were checked for stability across all of
  them (see `subtask_outcome_analysis` of Task 4 in `solution.json`).
- The reported 2050 point estimates are framed accordingly: planning-level
  strategy numbers, with factor-of-several uncertainty, and the recommendation
  is built on the stable ranking (India ≫ USA ≫ Brazil ≫ Ukraine > South
  Africa > Australia) rather than on the exact magnitudes.

---

### Rule compliance
- No verbatim copy of expert text into `solution.json`; only values, constraints
  and structural changes travel.
- No expert feedback was requested for coding, debugging, derivation or data
  processing; all three questions are about the real-world system.
- Exactly three exchanges, each building on the previous reply.
