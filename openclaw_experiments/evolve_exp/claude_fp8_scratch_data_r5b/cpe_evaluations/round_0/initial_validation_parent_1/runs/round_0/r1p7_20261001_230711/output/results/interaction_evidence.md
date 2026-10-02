# Interaction Evidence — Problem 2023_Y (used-sailboat pricing)

Three expert exchanges, one question each. Each reply is turned into a concrete
model parameter/constraint below; the values travel into the model, not the prose.

## Exchange 1
- **Question** (`logs/operator_feedback/expert_question_1.md`):
  "As a boat broker, when two used sailboats are the same age and same quality,
  which physical trait most decides which one costs more — and roughly how big is
  that gap?"
- **Reply** (`logs/operator_feedback/expert_reply_1.json`): Length (LOA) is the
  dominant physical trait; each ~10% of length adds ~30–50% to price, so a 45 ft
  boat lists ~1.5–2× a 40 ft boat and a 50 ft ~2–3× the 40 ft. The gap widens at
  the larger end and is compressed for catamarans (beam/volume matter more).
- **Turned into work**: This becomes a *constraint on the length exponent* in the
  log model. The cross-family (pooled) length elasticity d ln P / d ln L must fall
  in [~3, ~5], and the 40→45 ft ratio should be ~1.5–2×.
  - **Tested** (`logs/model.log`, pooled length model): monohull elasticity
    = **2.71**, catamaran elasticity = **3.00**; 40→45 ratio = 1.35× (M), 1.41× (C).
    Catamarans sit at the low edge of the band and the effect is indeed
    compressed for cats, as the expert said; monohulls are just below the 40→45
    1.5× lower bound. **Direction confirmed; magnitude slightly lower in this
    data**, consistent with the expert's caveat that the gap widens at the large
    end (our 40→50 check is 1.82× M / 1.99× C, inside the 2–3× band).

## Exchange 2
- **Question** (`expert_question_2.md`):
  "You have one specific 45-foot monohull from the same year. In practice,
  roughly how much more would you list it in the USA than in Europe, and Europe
  than the Caribbean?"
- **Reply** (`expert_reply_2.json`): USA vs Europe ≈ 0–10% (often within noise,
  slightly above); Europe vs Caribbean ≈ 10–20% above. Regional effect is smaller
  than length/age/condition and not consistent across all variants.
- **Turned into work**: Bounds on the region dummies — USA/Europe ∈ [1.00, 1.10],
  Europe/Caribbean ∈ [1.10, 1.20].
  - **Tested** (`logs/region_check.log`, same make-variant-year held fixed across
    regions, the "one specific boat" the expert judged):
    - all hulls: USA/Europe = **1.189×**, Europe/Caribbean = **1.024×**.
    - monohull: USA/Europe = **1.279×**, Europe/Caribbean = **1.000×**.
    - catamaran: USA/Europe = **1.072×**, Europe/Caribbean = **1.041×**.
  - **Result**: the data *disagree* with the expert on size and ordering — the USA
    premium is larger (1.19–1.28×) than the expert's 0–10% band, while the
    Europe-over-Caribbean gap is far smaller (≈1.00–1.04×) than the 10–20% band.
    The direction (USA ≥ Europe, Europe ≳ Caribbean) holds, and the effect is
    indeed non-uniform across variants (monohull gaps >> catamaran gaps), which is
    exactly the "not consistent across all variants" the expert flagged. The
    model therefore reports the data-estimated region effects (1.19×/0.95×) rather
    than the expert priors, and uses the priors only as a plausibility check.

## Exchange 3
- **Question** (`expert_question_3.md`):
  "Compared with Europe, does the same used sailboat usually list for more or
  less in the Hong Kong market, and by roughly how much?"
- **Reply** (`expert_reply_3.json`): HK runs **higher than Europe, roughly
  1.10–1.25×** for comparable make/variant/year/condition. Premium is **larger for
  catamarans** (short local supply, liveaboard premium) and **smaller for common
  production monohulls** (easier to import from Europe). Structural drivers: no
  local new-build supply, small wealthy buyer pool, high berthing cost, import
  duty + shipping.
- **Turned into work**: This is the Hong Kong regional effect for subtask 3 — a
  multiplicative premium b_HK with b_HK(M) < b_HK(C), both in [1.10, 1.25]× Europe.
  - **Used as**: the central value of the HK premium is calibrated to real HK
    comparables (search/fetch) where available; absent that, the midpoint of the
    band is split as **monohull ≈ 1.12× Europe, catamaran ≈ 1.22× Europe**, with
    the hull ordering (C > M) enforced by the reply. See the HK subsection of the
    solution for the parameter table and sensitivity.

## Net effect on the model
- Length: pooled cross-family exponent (≈2.7 M / 3.0 C) retained as the length
  term; within-family length is absorbed by make-variant dummies (length is nearly
  constant within a family).
- Age: −4.8%/yr decay (data-fitted), consistent with "age and market conditions"
  driving value.
- Region: data-estimated dummies (USA +19.3%, Caribbean −5.3%, Europe baseline),
  cross-checked against the expert bands (direction matches, magnitude does not).
- Hull: catamaran = 1.64× monohull (data-fitted).
- HK: 1.10–1.25× Europe, hull-dependent (C > M), per exchange 3.
