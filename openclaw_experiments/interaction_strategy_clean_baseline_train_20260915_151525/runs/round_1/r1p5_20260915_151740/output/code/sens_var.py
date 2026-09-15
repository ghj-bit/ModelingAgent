import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dataclasses import replace
from run_experiments import make_params, solve_pair

print("| var_cost ($/km) | S buses | S dist | S cost | C buses | C dist | C cost | saving % |")
print("|---|---|---|---|---|---|---|---|")
for v in [0.3, 0.6, 0.9, 1.2, 1.6, 2.0]:
    p = replace(make_params("rural"), var_cost_km=v, time_limit=25)
    inst, solS, solC, sS, sC, lb = solve_pair(p)
    sav = round((sS["cost_usd"] - sC["cost_usd"]) / sS["cost_usd"] * 100, 1)
    print(f"| {v} | {sS['n_buses']} | {sS['distance_km']} | {sS['cost_usd']} | "
          f"{sC['n_buses']} | {sC['distance_km']} | {sC['cost_usd']} | {sav} |")
