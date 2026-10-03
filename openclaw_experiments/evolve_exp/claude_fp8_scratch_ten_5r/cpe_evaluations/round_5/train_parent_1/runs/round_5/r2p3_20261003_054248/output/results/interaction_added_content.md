# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — Problem 2024_D (Great Lakes water-level control)

Ten expert exchanges were conducted. Each question was a single ≤20-word common-sense
question; no question requested coding, derivation, or computation. Each reply was
turned into a concrete parameter, constraint, or equation in the model
(`output/code/great_lakes_model.py`).

| # | Question (abridged) | Expert reply (abridged) | Effect on the model |
|---|---------------------|-------------------------|---------------------|
| 1 | What lake level do shipping companies worry about falling below? | The shipping (lake-level) floor is about 74.2 m above IGLD85; below that, vessels can't safely navigate the lower lakes. | Set `LWD = 74.20 m`. Used as the **navigation constraint** in the cost function: `nav = max(0, LWD − H)/0.1 × 10`. |
| 2 | What level would shore owners start to worry about flooding? | Shore owners start worrying roughly 0.3 m above the normal level (≈74.6 m), i.e. near 74.9 m, and it gets serious around 0.6 m above normal. | Set `NORM = 74.60 m`, `FLOOD1 = 74.90 m`, `FLOOD2 = 75.20 m`. Used as the **flooding constraint**: mild above F1, weighted ×2 above F2. |
| 3 | Do the dam operators release a fixed amount of water each month, or do they vary it by season? | They vary it by season — more in the spring/summer when inflow is high, less in winter. | Introduced **seasonal (band-based, season-gated) release** rather than a fixed release; release target follows measured inflow `I` plus a seasonal `SEASON_GAIN`. |
| 4 | Roughly how much water does the St. Lawrence dam let through in a typical month? | Typical monthly outflow is on the order of 5,000–11,000 m³/s, depending on season. | Set release **bounds** `qmin = 4500 m³/s`, `qmax = 11000 m³/s`; 2017 actual releases observed in 6711–10392 m³/s (inside the range). |
| 5 | If you open the dam more, how many weeks or months before the lake level visibly drops? | The lake responds over several months, not days — a change in release takes roughly a season to show up in the level. | Justifies a **damping horizon** (`horizon = 6` months) in the P-controller: `Q = I − A·(err/horizon)/t·gain`, avoiding over-correction. |
| 6 | Does ice on the river in winter limit how much water the dam can let through? | Yes — on the St. Lawrence, ice limits the outflow in the winter months. | Added **ice-month cap**: in months 10, 11, 0, 1 (`ICE_MONTHS`), `Q = min(Q, ice_cap = 6000 m³/s)`. |
| 7 | In a very wet year, do operators try to lower the lake early to make room? | Yes — in wet years they draw the level down toward the lower part of the normal range (roughly 0.3–0.6 m above normal) to create capacity. | Set control **band** `band = (74.35, 74.85) m` (mid = 74.60), i.e. keep the level within ~0.3–0.6 m of normal to pre-position capacity. |
| 8 | Does the Niagara River ice matter for the Ontario outflow? | Niagara ice is negligible compared with the St. Lawrence — the St. Lawrence ice is the real constraint. | Niagara outflow treated as **unconstrained**; only the St. Lawrence (Cornwall) outflow carries the ice cap. |
| 9 | Which lake's stakeholders should the control mainly protect? | Focus on **Lake Ontario** — its shore and navigation stakeholders are the priority. | Scoping: the modelled control loop and all cost accounting are applied to **Lake Ontario** (St. Lawrence outflow is the manipulated variable). |
| 10 | Besides the main river inflow, is there runoff or rain that lands on the lake itself? | Yes — there is also lakeshore runoff and precipitation/evaporation on the lake, so the river inflow alone does not fully account for the level change. | Justifies the **residual unmeasured-inflow term** `U(H) = ubar + c1·(H − Hbar)` added to the balance, absorbing runoff, precip/evap, and datum offset: `dH = (I + U(H) − Q)·t / A(H)`. |

All 10 exchanges are recorded in `output/logs/operator_feedback/`
(`expert_question_N.md`, `expert_request_N.json`, `expert_reply_N.json`, N = 1…10).
