"""
validate_small.py - Validation of the routing engine and the route-pool heuristic.

Two independent checks are performed on small instances drawn from the rural district:

  1. Single-school exact DP : an exhaustive set-partitioning DP over ALL feasible routes
     (every subset, every ordering) gives the provably optimal CVRPTW solution for one
     school. Compared against (a) the savings heuristic and (b) the pool-based MILP.

  2. Two-school exact pool : build the MILP with the COMPLETE route pool (all feasible
     routes enumerated) -> optimum of the model. Compared against the MILP restricted to
     the heuristic pool -> measures the quality loss of the pool heuristic.
"""

from __future__ import annotations
import os
import sys
import math
import itertools

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from sbrp import (Params, build_instance, route_distance, route_profile, make_route,
                  savings_routes, nn_routes, build_pools, solve_sbrp, summarize)
import pulp


def enumerate_all_routes(stop_ids, loads, start, end, cap_time, p, dist):
    """All feasible routes (subset + min-distance feasible ordering), exhaustively."""
    routes = []
    n = len(stop_ids)
    for r in range(1, n + 1):
        for comb in itertools.combinations(stop_ids, r):
            if sum(loads[s] for s in comb) > p.cap + 1e-9:
                continue
            best = None
            for perm in itertools.permutations(comb):
                dur = route_profile(list(perm), start, end, p, dist, loads)[0]
                if dur > cap_time + 1e-9:
                    continue
                d = route_distance(list(perm), start, end, dist)
                if best is None or d < best[0]:
                    best = (d, list(perm))
            if best is not None:
                routes.append(tuple(best[1]))
    return routes


def exact_single_school(stop_ids, loads, start, end, cap_time, p, dist):
    """Exact min-cost CVRPTW for one school via subset-cost + set-partition DP."""
    n = len(stop_ids)
    sub_cost = {}
    for mask in range(1, 1 << n):
        comb = [stop_ids[i] for i in range(n) if (mask >> i) & 1]
        if sum(loads[s] for s in comb) > p.cap + 1e-9:
            continue
        best = None
        for perm in itertools.permutations(comb):
            dur = route_profile(list(perm), start, end, p, dist, loads)[0]
            if dur > cap_time + 1e-9:
                continue
            d = route_distance(list(perm), start, end, dist)
            if best is None or d < best[0]:
                best = (d, list(perm))
        if best is not None:
            sub_cost[mask] = (p.fixed_cost + p.var_cost_km * best[0], best[0], best[1])
    full = (1 << n) - 1
    INF = float("inf")
    # dp[mask] = (cost, distance, n_routes)
    dp = {0: (0.0, 0.0, 0)}
    for mask in range(1, 1 << n):
        low = mask & (-mask)
        bestc = None
        s = mask
        while s:
            if s & low and s in sub_cost:
                rest = mask ^ s
                if rest in dp:
                    c = dp[rest][0] + sub_cost[s][0]
                    dd = dp[rest][1] + sub_cost[s][1]
                    nr = dp[rest][2] + 1
                    if bestc is None or (c, nr) < (bestc[0], bestc[2]):
                        bestc = (c, dd, nr)
            s = (s - 1) & mask
        if bestc is not None:
            dp[mask] = bestc
    return dp.get(full, (INF, INF, 0))


def run_validation(seed: int = 7) -> dict:
    out = {}
    # ---------------- small single-school (elementary) ----------------
    p = Params(seed=seed)
    inst = build_instance(p)
    S = inst["S"]
    loadse = inst["loads_e"]
    small = [s for s in range(S) if loadse[s] > 0][:7]
    p_small = Params(seed=seed, cap=30, max_ride=55.0)
    dist = inst["dist"]
    DEPOT, ELEM = inst["DEPOT"], inst["ELEM"]

    exact_cost, exact_dist, exact_n = exact_single_school(small, loadse, DEPOT, ELEM,
                                                          p_small.max_ride, p_small, dist)

    rng = np.random.default_rng(seed + 5)
    heur_routes, _ = savings_routes(small, loadse, DEPOT, ELEM, p_small.max_ride, p_small,
                                    dist, rng, n_runs=30, jitter=0.8)
    heur_dist = sum(route_distance(r, DEPOT, ELEM, dist) for r in heur_routes)
    heur_cost = p.fixed_cost * len(heur_routes) + p.var_cost_km * heur_dist

    out["single_school"] = dict(
        n_stops=len(small), cap=p_small.cap, max_ride=p_small.max_ride,
        exact_routes=int(exact_n),
        exact_cost=round(exact_cost, 2), exact_dist=round(exact_dist, 1),
        heur_routes=len(heur_routes), heur_cost=round(heur_cost, 2), heur_dist=round(heur_dist, 1),
        gap_pct=round((heur_cost - exact_cost) / exact_cost * 100.0, 2))

    # ---------------- small two-school, full pool = exact ----------------
    p2 = Params(seed=seed, cap=30, max_ride=60.0, stagger=40, n_runs_savings=15, pool_cap=5000)
    inst2 = build_instance(p2)
    loadsh = inst2["loads_h"]
    S2 = inst2["S"]
    e_stops = [s for s in range(S2) if loadse[s] > 0][:6]
    h_stops = [s for s in range(S2) if loadsh[s] > 0][:6]
    DEP2, ELE2, HIG2 = inst2["DEPOT"], inst2["ELEM"], inst2["HIGH"]

    full = dict(
        pool_E=set(enumerate_all_routes(e_stops, loadse, DEP2, ELE2, p2.max_ride, p2, dist)),
        pool_Hs=set(enumerate_all_routes(h_stops, loadsh, ELE2, HIG2, p2.stagger, p2, dist)),
        pool_Hl=set(enumerate_all_routes(h_stops, loadsh, DEP2, HIG2, p2.max_ride, p2, dist)),
    )
    # heuristic pool restricted to the SAME small sub-problem (for an apples-to-apples gap)
    _, pe = savings_routes(e_stops, loadse, DEP2, ELE2, p2.max_ride, p2, dist,
                           np.random.default_rng(seed + 77), n_runs=15, jitter=0.8)
    _, phs = savings_routes(h_stops, loadsh, ELE2, HIG2, p2.stagger, p2, dist,
                            np.random.default_rng(seed + 88), n_runs=15, jitter=0.8)
    _, phl = savings_routes(h_stops, loadsh, DEP2, HIG2, p2.max_ride, p2, dist,
                            np.random.default_rng(seed + 99), n_runs=15, jitter=0.8)
    pe |= nn_routes(e_stops, loadse, DEP2, ELE2, p2.max_ride, p2, dist,
                    np.random.default_rng(seed + 111), n_random=30)
    phs |= nn_routes(h_stops, loadsh, ELE2, HIG2, p2.stagger, p2, dist,
                     np.random.default_rng(seed + 222), n_random=30)
    phl |= nn_routes(h_stops, loadsh, DEP2, HIG2, p2.max_ride, p2, dist,
                     np.random.default_rng(seed + 333), n_random=30)
    for s in e_stops:
        pe.add((s,))
    for s in h_stops:
        phs.add((s,))
        phl.add((s,))
    heur_pools = dict(pool_E=pe, pool_Hs=phs, pool_Hl=phl)

    sol_full = solve_sbrp(inst2, p2, full, allow_share=True, use_short_H=True, use_long_H=True,
                          time_limit=60)
    sol_heur = solve_sbrp(inst2, p2, heur_pools, allow_share=True, use_short_H=True,
                          use_long_H=True, time_limit=60)
    out["two_school"] = dict(
        n_e_stops=len(e_stops), n_h_stops=len(h_stops), cap=p2.cap,
        full_pool_obj=round(sol_full["objective"], 2), full_buses=sol_full["n_buses"],
        heur_pool_obj=round(sol_heur["objective"], 2), heur_buses=sol_heur["n_buses"],
        gap_pct=round((sol_heur["objective"] - sol_full["objective"]) / sol_full["objective"] * 100.0, 2),
        pool_sizes_full={k: len(v) for k, v in full.items()})

    return out


if __name__ == "__main__":
    import json
    res = run_validation()
    print(json.dumps(res, indent=2))
