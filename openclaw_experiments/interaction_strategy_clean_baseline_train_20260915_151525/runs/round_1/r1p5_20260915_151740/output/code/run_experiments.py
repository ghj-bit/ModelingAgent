"""
run_experiments.py - End-to-end experiments for the School Busing model.

Produces:
  results/experiments.json   machine-readable results
  results/tables.md          all markdown tables used by the report
  results/routes_rural.csv   route-by-route detail for the rural base case
  data/district_rural.csv    the synthetic rural instance
  data/district_urban.csv    the synthetic urban instance
  logs/run.log               run log
"""

from __future__ import annotations
import os
import sys
import json
import math
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from dataclasses import replace
from sbrp import (Params, build_instance, save_instance_csv, build_pools, solve_sbrp,
                  summarize, lower_bounds)
import validate_small

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")
DATA = os.path.join(ROOT, "data")
LOGS = os.path.join(ROOT, "logs")
for d in (RESULTS, DATA, LOGS):
    os.makedirs(d, exist_ok=True)

_LOG = []


def log(msg: str) -> None:
    print(msg)
    _LOG.append(msg)


def to_py(o):
    if isinstance(o, dict):
        return {k: to_py(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [to_py(v) for v in o]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    return o


def make_params(name: str = "rural", **kw) -> Params:
    base = {}
    if name == "urban":
        base = dict(n_villages=12, stops_per_village=3, village_sd_km=0.9, area_km=12.0,
                    speed_kmh=26.0, target_elem=420, target_high=320, shared_prob=0.5)
    base.update(kw)
    return Params(name=name, **base)


def ride_shares(sol, loads, thresholds):
    """Share (%) of students whose ride exceeds each threshold, student-weighted."""
    tot = 0.0
    over = {t: 0.0 for t in thresholds}
    for r in sol["routes_E"] + sol["routes_H"]:
        for i, s in enumerate(r["order"]):
            w = loads[s]
            tot += w
            for t in thresholds:
                if r["ride"][i] > t:
                    over[t] += w
    return {t: (100.0 * over[t] / tot if tot else 0.0) for t in thresholds}


def solve_pair(p: Params, save_routes: bool = False):
    inst = build_instance(p)
    pools = build_pools(inst, p)
    lb = lower_bounds(inst, p)
    t0 = time.time()
    solS = solve_sbrp(inst, p, pools, allow_share=False, use_short_H=False, use_long_H=True)
    t1 = time.time()
    solC = solve_sbrp(inst, p, pools, allow_share=True, use_short_H=True, use_long_H=True)
    t2 = time.time()
    sumS = summarize(solS, inst, p)
    sumC = summarize(solC, inst, p)
    allloads = {**inst["loads_e"], **inst["loads_h"]}
    thr = [30, 45, 60]
    sumS["ride_shares"] = ride_shares(solS, allloads, thr)
    sumC["ride_shares"] = ride_shares(solC, allloads, thr)
    sumS["solve_s"] = round(t1 - t0, 2)
    sumC["solve_s"] = round(t2 - t1, 2)
    if save_routes:
        with open(os.path.join(RESULTS, "routes_rural.csv"), "w", encoding="utf-8") as f:
            f.write("policy,school,route_id,stops,n_students,distance_km,route_minutes,max_ride_min\n")
            for pol, sol in (("S", solS), ("C", solC)):
                for j, r in enumerate(sol["routes_E"]):
                    f.write(f"{pol},E,{j},\"{'-'.join(map(str,r['order']))}\",{int(r['riders'])},"
                            f"{r['distance']:.2f},{r['duration']:.1f},{max(r['ride']):.1f}\n")
                for j, r in enumerate(sol["routes_H"]):
                    f.write(f"{pol},H,{j},\"{'-'.join(map(str,r['order']))}\",{int(r['riders'])},"
                            f"{r['distance']:.2f},{r['duration']:.1f},{max(r['ride']):.1f}\n")
    return inst, solS, solC, sumS, sumC, lb


def main():
    results = {}

    # ---------------- base cases ------------------------------------------------
    log("== base rural ==")
    p_rural = replace(make_params("rural"), time_limit=25)
    instR, solSR, solCR, sumSR, sumCR, lbR = solve_pair(p_rural, save_routes=True)
    save_instance_csv(instR, os.path.join(DATA, "district_rural.csv"))
    results["base_rural"] = dict(S=sumSR, C=sumCR, lb=lbR)
    log(f"  rural  S: buses={sumSR['n_buses']} cost=${sumSR['cost_usd']}")
    log(f"  rural  C: buses={sumCR['n_buses']} cost=${sumCR['cost_usd']}")

    log("== base urban ==")
    p_urban = replace(make_params("urban"), time_limit=25)
    instU, solSU, solCU, sumSU, sumCU, lbU = solve_pair(p_urban)
    save_instance_csv(instU, os.path.join(DATA, "district_urban.csv"))
    results["base_urban"] = dict(S=sumSU, C=sumCU, lb=lbU)
    log(f"  urban  S: buses={sumSU['n_buses']} cost=${sumSU['cost_usd']}")
    log(f"  urban  C: buses={sumCU['n_buses']} cost=${sumCU['cost_usd']}")

    # ---------------- sensitivity sweeps ---------------------------------------
    def sweep(base, key, values, fieldS="cost_usd", fieldC="cost_usd"):
        rows = []
        for v in values:
            p = make_params(base, **{key: v})
            p = replace(p, time_limit=15, n_runs_savings=25)
            _, _, _, sS, sC, _ = solve_pair(p)
            rows.append(dict(value=v,
                             S_buses=sS["n_buses"], S_cost=sS["cost_usd"],
                             C_buses=sC["n_buses"], C_cost=sC["cost_usd"],
                             C_shared=sC["n_H_short"],
                             S_elem_max=sS["ride_elem"]["max"], S_high_max=sS["ride_high"]["max"],
                             C_elem_max=sC["ride_elem"]["max"], C_high_max=sC["ride_high"]["max"],
                             saving_pct=round((sS["cost_usd"] - sC["cost_usd"]) / max(sS["cost_usd"], 1) * 100, 1)))
            log(f"  {key}={v}: S={sS['n_buses']}b/${sS['cost_usd']}  C={sC['n_buses']}b/${sC['cost_usd']}")
        return rows

    log("== sweep: stagger (min) ==")
    sens_stagger = sweep("rural", "stagger", [15, 20, 25, 30, 35, 40, 50, 60, 70])

    log("== sweep: max ride (min) ==")
    sens_ride = sweep("rural", "max_ride", [45, 50, 55, 60, 70, 80])

    log("== sweep: capacity (seats) ==")
    sens_cap = sweep("rural", "cap", [36, 48, 60, 72, 84])

    log("== sweep: fixed cost per bus-day ($) ==")
    sens_fixed = sweep("rural", "fixed_cost", [60, 90, 120, 180, 240, 300])

    log("== sweep: shared-stop fraction ==")
    sens_shared = sweep("rural", "shared_prob", [0.2, 0.35, 0.5, 0.65, 0.8, 0.95])

    log("== sweep: effective speed (km/h) ==")
    sens_speed = sweep("rural", "speed_kmh", [30, 35, 40, 45, 50, 55])

    results["sensitivity"] = dict(stagger=sens_stagger, max_ride=sens_ride, cap=sens_cap,
                                  fixed_cost=sens_fixed, shared_prob=sens_shared, speed=sens_speed)

    # ---------------- validation -----------------------------------------------
    log("== validation ==")
    val = validate_small.run_validation()
    results["validation"] = val
    log(json.dumps(to_py(val), indent=2))

    # ---------------- save ------------------------------------------------------
    with open(os.path.join(RESULTS, "experiments.json"), "w", encoding="utf-8") as f:
        json.dump(to_py(results), f, indent=2)
    with open(os.path.join(LOGS, "run.log"), "w", encoding="utf-8") as f:
        f.write("\n".join(_LOG))

    write_tables(results)
    log("done.")


# ----------------------------------------------------------------------------------
def md_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join(["---"] * len(headers)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


def write_tables(res: dict) -> None:
    lines = ["# Experiments - generated tables\n"]
    b = res["base_rural"]
    lines.append("## Base rural district\n")
    lines.append(md_table(
        ["Metric", "Policy S (separate)", "Policy C (combined)"],
        [["Buses", b["S"]["n_buses"], b["C"]["n_buses"]],
         ["Elementary routes", b["S"]["n_E_routes"], b["C"]["n_E_routes"]],
         ["High-school routes", b["S"]["n_H_routes"], b["C"]["n_H_routes"]],
         ["  of which paired (short)", b["S"]["n_H_short"], b["C"]["n_H_short"]],
         ["Total distance (km)", b["S"]["distance_km"], b["C"]["distance_km"]],
         ["Total cost ($/day)", b["S"]["cost_usd"], b["C"]["cost_usd"]],
         ["Cost per student ($)", b["S"]["cost_per_student"], b["C"]["cost_per_student"]],
         ["Max elem ride (min)", b["S"]["ride_elem"]["max"], b["C"]["ride_elem"]["max"]],
         ["Mean elem ride (min)", b["S"]["ride_elem"]["mean"], b["C"]["ride_elem"]["mean"]],
         ["Max high ride (min)", b["S"]["ride_high"]["max"], b["C"]["ride_high"]["max"]],
         ["Mean high ride (min)", b["S"]["ride_high"]["mean"], b["C"]["ride_high"]["mean"]],
         ["Student-minutes on bus", b["S"]["student_minutes"], b["C"]["student_minutes"]],
         ["% students riding >45 min", round(b["S"]["ride_shares"][45], 1), round(b["C"]["ride_shares"][45], 1)],
         ["Lower bound buses (analyt.)", b["lb"]["buses_sep_lb"], b["lb"]["buses_comb_lb"]]]))
    u = res["base_urban"]
    lines.append("\n## Base urban district\n")
    lines.append(md_table(
        ["Metric", "Policy S", "Policy C"],
        [["Buses", u["S"]["n_buses"], u["C"]["n_buses"]],
         ["Distance (km)", u["S"]["distance_km"], u["C"]["distance_km"]],
         ["Cost ($/day)", u["S"]["cost_usd"], u["C"]["cost_usd"]],
         ["Max elem ride", u["S"]["ride_elem"]["max"], u["C"]["ride_elem"]["max"]],
         ["Max high ride", u["S"]["ride_high"]["max"], u["C"]["ride_high"]["max"]]]))
    for name, rows in res["sensitivity"].items():
        lines.append(f"\n## Sensitivity: {name}\n")
        lines.append(md_table(
            ["value", "S buses", "S cost", "C buses", "C cost", "C paired", "Saving %",
             "S maxElem", "C maxElem", "S maxHigh", "C maxHigh"],
            [[r["value"], r["S_buses"], r["S_cost"], r["C_buses"], r["C_cost"], r["C_shared"],
              r["saving_pct"], r["S_elem_max"], r["C_elem_max"], r["S_high_max"], r["C_high_max"]]
             for r in rows]))
    v = res["validation"]
    lines.append("\n## Validation\n")
    lines.append(md_table(
        ["Check", "Exact", "Heuristic", "Gap %"],
        [["Single-school CVRPTW (7 stops)", v["single_school"]["exact_cost"],
          v["single_school"]["heur_cost"], v["single_school"]["gap_pct"]],
         ["Two-school full pool (12 stops)", v["two_school"]["full_pool_obj"],
          v["two_school"]["heur_pool_obj"], v["two_school"]["gap_pct"]]]))
    with open(os.path.join(RESULTS, "tables.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
