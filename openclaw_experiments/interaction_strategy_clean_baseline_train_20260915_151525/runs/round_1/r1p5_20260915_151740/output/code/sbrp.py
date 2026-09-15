"""
sbrp.py - School Bus Routing Problem (SBRP) core library.
HiMCM 2002 "School Busing".

Model family:
  * Capacitated Vehicle Routing Problem with Time Windows (CVRPTW) per school,
    solved (a) by a randomized Clarke-Wright savings + 2-opt construction and
    (b) exactly (small instances) / near-exactly (set-partitioning MILP) for validation.
  * Two operating policies:
        S = "separate"   : dedicated buses per school (elementary fleet + high fleet).
        C = "combined"   : staggered ("two-tier") operation where a bus that has just
                           dropped elementary students can immediately run a high-school
                           route, reusing the same vehicle + driver.
  * A coupling variable z = number of high-school routes served by a reused bus.
    number_of_buses = n_E + n_H - z ,  z <= n_E , z <= (#high routes that fit the stagger).

This module is pure Python + numpy + pulp. Deterministic given Params.seed.
"""

from __future__ import annotations

import math
import json
import os
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Tuple, Optional

import numpy as np
import pulp


# --------------------------------------------------------------------------------------
# Parameters
# --------------------------------------------------------------------------------------
@dataclass
class Params:
    name: str = "rural"
    # ---- geometry / demand -----------------------------------------------------------
    n_villages: int = 6
    stops_per_village: int = 5
    village_sd_km: float = 1.6
    area_km: float = 20.0
    target_elem: int = 350
    target_high: int = 250
    shared_prob: float = 0.65
    # ---- transport -------------------------------------------------------------------
    road_factor: float = 1.2      # detour factor: road distance / straight-line distance
    speed_kmh: float = 45.0       # effective average speed (rural) incl. accel/decel
    cap: int = 72                 # seats (Type C school bus, 3 per bench)
    max_ride: float = 60.0        # hard cap: minutes any student may ride
    bell_elem: int = 480          # 08:00, minutes after midnight
    stagger: int = 40             # minutes between elementary bell and high-school bell
    # ---- economics -------------------------------------------------------------------
    fixed_cost: float = 120.0     # $ per bus deployed per school day (driver + capital + ins.)
    var_cost_km: float = 0.60     # $ per km (fuel + maintenance + tyres)
    alpha_ride: float = 0.0       # $ per student-minute (equity / comfort weight)
    # ---- service ---------------------------------------------------------------------
    service_per_student: float = 0.25   # minutes boarding per student
    service_fixed: float = 0.5          # minutes per stop (door open / check)
    # ---- search ----------------------------------------------------------------------
    seed: int = 7
    n_runs_savings: int = 40
    pool_cap: int = 2500
    time_limit: int = 45

    @property
    def bell_high(self) -> int:
        return self.bell_elem + self.stagger


# --------------------------------------------------------------------------------------
# Instance construction
# --------------------------------------------------------------------------------------
def build_instance(p: Params) -> dict:
    """Build a synthetic but realistic rural / urban school district.

    Stops are clustered (villages) to mimic rural settlement patterns; each stop holds a
    number of elementary (K-5) and high-school (9-12) students. The elementary school, the
    high school and the bus depot are placed near the demand centroid.
    """
    rng = np.random.default_rng(p.seed)
    centers = rng.uniform(1.2, p.area_km - 1.2, size=(p.n_villages, 2))
    raw = []
    for c in centers:
        for _ in range(p.stops_per_village):
            x, y = c + rng.normal(0.0, p.village_sd_km, 2)
            x = float(np.clip(x, 0.0, p.area_km))
            y = float(np.clip(y, 0.0, p.area_km))
            ne = int(rng.integers(5, 16))
            nh = int(rng.integers(4, 13)) if rng.random() < p.shared_prob else 0
            raw.append([x, y, ne, nh])
    raw = np.array(raw, dtype=float)
    S = raw.shape[0]

    # scale student counts to the district targets
    se = raw[:, 2].sum()
    sh = raw[:, 3].sum()
    ke = p.target_elem / se if se > 0 else 0.0
    kh = p.target_high / sh if sh > 0 else 0.0
    for i in range(S):
        raw[i, 2] = max(1.0, float(round(raw[i, 2] * ke)))
        if raw[i, 3] > 0:
            raw[i, 3] = max(1.0, float(round(raw[i, 3] * kh)))

    # school / depot placement near the demand centroid
    cx = float((raw[:, 0] * raw[:, 2]).sum() / raw[:, 2].sum())
    cy = float((raw[:, 1] * raw[:, 2]).sum() / raw[:, 2].sum())
    elem = np.array([cx, cy])
    high = elem + np.array([0.16 * p.area_km, 0.05 * p.area_km])
    depot = high.copy()

    coords = np.vstack([raw[:, :2], depot, elem, high])
    DEPOT, ELEM, HIGH = S, S + 1, S + 2

    dx = coords[:, 0][:, None] - coords[:, 0][None, :]
    dy = coords[:, 1][:, None] - coords[:, 1][None, :]
    dist = np.sqrt(dx * dx + dy * dy) * p.road_factor

    loads_e = {i: float(raw[i, 2]) for i in range(S)}
    loads_h = {i: float(raw[i, 3]) for i in range(S)}

    return dict(params=p, coords=coords, dist=dist, S=S,
                DEPOT=DEPOT, ELEM=ELEM, HIGH=HIGH,
                loads_e=loads_e, loads_h=loads_h, stops=raw)


def save_instance_csv(inst: dict, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("stop_id,x_km,y_km,n_elementary,n_high_school\n")
        for i, row in enumerate(inst["stops"]):
            f.write(f"{i},{row[0]:.4f},{row[1]:.4f},{int(row[2])},{int(row[3])}\n")


# --------------------------------------------------------------------------------------
# Route evaluation
# --------------------------------------------------------------------------------------
def route_distance(order: List[int], start: int, end: int, dist: np.ndarray) -> float:
    if not order:
        return 0.0
    d = 0.0
    prev = start
    for s in order:
        d += dist[prev, s]
        prev = s
    d += dist[prev, end]
    return d


def route_profile(order: List[int], start: int, end: int, p: Params,
                  dist: np.ndarray, loads: Dict[int, float]) -> Tuple[float, List[float], float]:
    """Return (duration_min, board_times_rel, distance_km) for a route order."""
    rel = 0.0
    board: List[float] = []
    prev = start
    for s in order:
        rel += dist[prev, s] / p.speed_kmh * 60.0
        board.append(rel)
        rel += p.service_fixed + p.service_per_student * loads[s]
        prev = s
    rel += dist[prev, end] / p.speed_kmh * 60.0
    return rel, board, route_distance(order, start, end, dist)


def make_route(order: List[int], start: int, end: int, p: Params, dist: np.ndarray,
               loads: Dict[int, float], level: str, cap_time: float) -> dict:
    duration, board, d = route_profile(order, start, end, p, dist, loads)
    deadline = p.bell_elem if level == "E" else p.bell_high
    dep = deadline - duration                     # absolute departure time from `start`
    ride = [deadline - (dep + bt) for bt in board]
    riders = sum(loads[s] for s in order)
    smin = sum(loads[order[i]] * ride[i] for i in range(len(order)))
    feas = (duration <= cap_time + 1e-9) and (riders <= p.cap + 1e-9)
    return dict(order=tuple(order), start=int(start), end=int(end), level=level,
                distance=float(d), duration=float(duration), ride=[float(x) for x in ride],
                riders=float(riders), student_minutes=float(smin),
                feasible=bool(feas), depart=float(dep))


# --------------------------------------------------------------------------------------
# Heuristic: randomized Clarke-Wright savings + 2-opt
# --------------------------------------------------------------------------------------
def _two_opt(order: List[int], start: int, end: int, cap_time: float, p: Params,
             dist: np.ndarray, loads: Dict[int, float], max_iter: int = 60) -> List[int]:
    order = list(order)
    n = len(order)
    improved = True
    it = 0
    while improved and it < max_iter:
        improved = False
        it += 1
        for a in range(n - 1):
            for b in range(a + 1, n):
                new = order[:a] + order[a:b + 1][::-1] + order[b + 1:]
                if sum(loads[s] for s in new) > p.cap + 1e-9:
                    continue
                if route_distance(new, start, end, dist) < route_distance(order, start, end, dist) - 1e-9:
                    dur = route_profile(new, start, end, p, dist, loads)[0]
                    if dur <= cap_time + 1e-9:
                        order = new
                        improved = True
    return order


def savings_routes(stop_ids: List[int], loads: Dict[int, float], start: int, end: int,
                   cap_time: float, p: Params, dist: np.ndarray, rng: np.random.Generator,
                   n_runs: int = 1, jitter: float = 0.6, collect_pool: bool = True):
    """Randomized Clarke-Wright savings. Returns (best_routes, pool_set_of_tuples)."""
    best_routes = None
    best_key = None
    pool = set()

    for _ in range(n_runs):
        routes = [[s] for s in stop_ids]
        ids = list(stop_ids)
        pairs = []
        for a in range(len(ids)):
            for b in range(a + 1, len(ids)):
                i, j = ids[a], ids[b]
                sav1 = dist[i, end] + dist[start, j] - dist[i, j]
                sav2 = dist[j, end] + dist[start, i] - dist[j, i]
                pairs.append((max(sav1, sav2) + (rng.random() - 0.5) * jitter, i, j))
        pairs.sort(key=lambda z: z[0], reverse=True)

        while True:
            idx_of = {}
            for ri, r in enumerate(routes):
                for s in r:
                    idx_of[s] = ri
            merged = False
            for _, i, j in pairs:
                ri = idx_of.get(i)
                rj = idx_of.get(j)
                if ri is None or rj is None or ri == rj:
                    continue
                A, B = routes[ri], routes[rj]
                cand = None
                if A[-1] == i and B[0] == j:
                    cand = A + B
                elif A[-1] == i and B[-1] == j:
                    cand = A + B[::-1]
                elif A[0] == i and B[0] == j:
                    cand = A[::-1] + B
                elif A[0] == i and B[-1] == j:
                    cand = A[::-1] + B[::-1]
                if cand is None:
                    continue
                if sum(loads[s] for s in cand) > p.cap + 1e-9:
                    continue
                dur = route_profile(cand, start, end, p, dist, loads)[0]
                if dur > cap_time + 1e-9:
                    continue
                delta = (route_distance(cand, start, end, dist)
                         - route_distance(A, start, end, dist)
                         - route_distance(B, start, end, dist))
                if delta < -1e-9:
                    routes[ri] = cand
                    routes.pop(rj)
                    merged = True
                    break
            if not merged:
                break

        routes = [_two_opt(r, start, end, cap_time, p, dist, loads) for r in routes]
        if collect_pool:
            for r in routes:
                pool.add(tuple(r))
        key = (len(routes), round(sum(route_distance(r, start, end, dist) for r in routes), 6))
        if best_key is None or key < best_key:
            best_key = key
            best_routes = [list(r) for r in routes]

    return best_routes, pool


# --------------------------------------------------------------------------------------
# Route-pool generation for the set-partitioning model
# --------------------------------------------------------------------------------------
def _cap_pool(pool: set, dist: np.ndarray, start: int, end: int, cap: int) -> set:
    if len(pool) <= cap:
        return pool
    ranked = sorted(pool, key=lambda o: route_distance(list(o), start, end, dist))
    keep = set(ranked[:cap])
    # guarantee singleton coverage
    for o in pool:
        if len(o) == 1:
            keep.add(o)
    return keep


def nn_routes(stop_ids: List[int], loads: Dict[int, float], start: int, end: int,
              cap_time: float, p: Params, dist: np.ndarray,
              rng: Optional[np.random.Generator] = None, n_random: int = 40) -> set:
    """Nearest-neighbour construction of complete solutions; one solution per seed."""
    pool = set()
    seeds = list(stop_ids)
    for seed in seeds:
        unassigned = set(stop_ids)
        routes = []
        first = seed
        while unassigned:
            cur = first if first in unassigned else min(unassigned, key=lambda s: dist[start, s])
            first = None
            route = [cur]
            unassigned.discard(cur)
            while True:
                best, bestd = None, 1e18
                cand_list = list(unassigned)
                if rng is not None and len(cand_list) > 2:
                    rng.shuffle(cand_list)
                for s in cand_list:
                    if sum(loads[x] for x in route) + loads[s] > p.cap + 1e-9:
                        continue
                    if route_profile(route + [s], start, end, p, dist, loads)[0] > cap_time + 1e-9:
                        continue
                    d = dist[route[-1], s] + (rng.random() - 0.5) * 0.0 if rng is not None else dist[route[-1], s]
                    if d < bestd:
                        bestd, best = d, s
                if best is None:
                    break
                route.append(best)
                unassigned.discard(best)
            routes.append(_two_opt(route, start, end, cap_time, p, dist, loads))
        for r in routes:
            pool.add(tuple(r))
    for _ in range(n_random):
        unassigned = set(stop_ids)
        routes = []
        while unassigned:
            cur = rng.choice(list(unassigned))
            route = [cur]
            unassigned.discard(cur)
            while True:
                cand_list = list(unassigned)
                rng.shuffle(cand_list)
                picked = None
                for s in cand_list:
                    if sum(loads[x] for x in route) + loads[s] > p.cap + 1e-9:
                        continue
                    if route_profile(route + [s], start, end, p, dist, loads)[0] > cap_time + 1e-9:
                        continue
                    picked = s
                    break
                if picked is None:
                    break
                route.append(picked)
                unassigned.discard(picked)
            routes.append(_two_opt(route, start, end, cap_time, p, dist, loads))
        for r in routes:
            pool.add(tuple(r))
    return pool


def build_pools(inst: dict, p: Params) -> dict:
    S = inst["S"]
    dist = inst["dist"]
    loadse = inst["loads_e"]
    loadsh = inst["loads_h"]
    DEPOT, ELEM, HIGH = inst["DEPOT"], inst["ELEM"], inst["HIGH"]
    rng = np.random.default_rng(p.seed + 101)

    elem_stops = [s for s in range(S) if loadse[s] > 0]
    high_stops = [s for s in range(S) if loadsh[s] > 0]

    _, pool_E = savings_routes(elem_stops, loadse, DEPOT, ELEM, p.max_ride, p, dist, rng,
                               n_runs=p.n_runs_savings, jitter=0.8)
    _, pool_Hs = savings_routes(high_stops, loadsh, ELEM, HIGH, p.stagger, p, dist,
                                np.random.default_rng(p.seed + 202),
                                n_runs=p.n_runs_savings, jitter=0.8)
    _, pool_Hl = savings_routes(high_stops, loadsh, DEPOT, HIGH, p.max_ride, p, dist,
                                np.random.default_rng(p.seed + 303),
                                n_runs=p.n_runs_savings, jitter=0.8)

    pool_E |= nn_routes(elem_stops, loadse, DEPOT, ELEM, p.max_ride, p, dist,
                        rng=np.random.default_rng(p.seed + 111), n_random=60)
    pool_Hs |= nn_routes(high_stops, loadsh, ELEM, HIGH, p.stagger, p, dist,
                         rng=np.random.default_rng(p.seed + 222), n_random=60)
    pool_Hl |= nn_routes(high_stops, loadsh, DEPOT, HIGH, p.max_ride, p, dist,
                         rng=np.random.default_rng(p.seed + 333), n_random=60)

    # singletons always present
    for s in elem_stops:
        pool_E.add((s,))
    for s in high_stops:
        pool_Hs.add((s,))
        pool_Hl.add((s,))

    pool_E = _cap_pool(pool_E, dist, DEPOT, ELEM, p.pool_cap)
    pool_Hs = _cap_pool(pool_Hs, dist, ELEM, HIGH, p.pool_cap)
    pool_Hl = _cap_pool(pool_Hl, dist, DEPOT, HIGH, p.pool_cap)
    return dict(pool_E=pool_E, pool_Hs=pool_Hs, pool_Hl=pool_Hl)


# --------------------------------------------------------------------------------------
# Set-partitioning MILP (policy S and C)
# --------------------------------------------------------------------------------------
def solve_sbrp(inst: dict, p: Params, pools: dict, allow_share: bool = True,
               use_short_H: bool = True, use_long_H: bool = True,
               time_limit: Optional[int] = None) -> dict:
    S = inst["S"]
    dist = inst["dist"]
    loadse, loadsh = inst["loads_e"], inst["loads_h"]
    DEPOT, ELEM, HIGH = inst["DEPOT"], inst["ELEM"], inst["HIGH"]
    tl = p.time_limit if time_limit is None else time_limit

    R_E = [make_route(list(o), DEPOT, ELEM, p, dist, loadse, "E", p.max_ride)
           for o in pools["pool_E"]]
    R_E = [r for r in R_E if r["feasible"]]
    R_Hs = []
    if use_short_H:
        R_Hs = [make_route(list(o), ELEM, HIGH, p, dist, loadsh, "H", p.stagger)
                for o in pools["pool_Hs"]]
        R_Hs = [r for r in R_Hs if r["feasible"]]
    R_Hl = []
    if use_long_H:
        R_Hl = [make_route(list(o), DEPOT, HIGH, p, dist, loadsh, "H", p.max_ride)
                for o in pools["pool_Hl"]]
        R_Hl = [r for r in R_Hl if r["feasible"]]

    prob = pulp.LpProblem("SBRP", pulp.LpMinimize)
    x = [pulp.LpVariable(f"x{i}", cat="Binary") for i in range(len(R_E))]
    ys = [pulp.LpVariable(f"ys{i}", cat="Binary") for i in range(len(R_Hs))]
    yl = [pulp.LpVariable(f"yl{i}", cat="Binary") for i in range(len(R_Hl))]

    nE = pulp.lpSum(x)
    nH = pulp.lpSum(ys) + pulp.lpSum(yl)
    pair = pulp.lpSum(ys)
    z = pulp.LpVariable("z", lowBound=0, cat="Integer")

    distv = (pulp.lpSum(R_E[i]["distance"] * x[i] for i in range(len(R_E)))
             + pulp.lpSum(R_Hs[i]["distance"] * ys[i] for i in range(len(R_Hs)))
             + pulp.lpSum(R_Hl[i]["distance"] * yl[i] for i in range(len(R_Hl))))
    sminv = (pulp.lpSum(R_E[i]["student_minutes"] * x[i] for i in range(len(R_E)))
             + pulp.lpSum(R_Hs[i]["student_minutes"] * ys[i] for i in range(len(R_Hs)))
             + pulp.lpSum(R_Hl[i]["student_minutes"] * yl[i] for i in range(len(R_Hl))))

    if allow_share:
        prob += z <= nE
        prob += z <= pair
        buses = nE + nH - z
    else:
        prob += z == 0
        buses = nE + nH

    prob += p.fixed_cost * buses + p.var_cost_km * distv + p.alpha_ride * sminv

    # Cover exactly the stops that the supplied pools are meant to serve (derived from the
    # pools themselves so that sub-problems / validation subsets work as intended).
    elem_stops = sorted({s for r in R_E for s in r["order"]})
    high_stops = sorted({s for r in (R_Hs + R_Hl) for s in r["order"]})

    for s in elem_stops:
        prob += pulp.lpSum(x[i] for i, r in enumerate(R_E) if s in r["order"]) == 1
    for s in high_stops:
        expr = (pulp.lpSum(ys[i] for i, r in enumerate(R_Hs) if s in r["order"])
                + pulp.lpSum(yl[i] for i, r in enumerate(R_Hl) if s in r["order"]))
        prob += expr == 1

    solver = pulp.PULP_CBC_CMD(msg=0, timeLimit=tl, gapRel=0.02)
    status = prob.solve(solver)

    chosen_E = [R_E[i] for i in range(len(R_E)) if x[i].value() and x[i].value() > 0.5]
    chosen_Hs = [R_Hs[i] for i in range(len(R_Hs)) if ys[i].value() and ys[i].value() > 0.5]
    chosen_Hl = [R_Hl[i] for i in range(len(R_Hl)) if yl[i].value() and yl[i].value() > 0.5]
    chosen_H = chosen_Hs + chosen_Hl
    n_buses = len(chosen_E) + len(chosen_H) - (min(len(chosen_E), len(chosen_Hs)) if allow_share else 0)

    return dict(policy=("C" if allow_share else "S"), status=pulp.LpStatus[status],
                objective=float(pulp.value(prob.objective)),
                n_E_routes=len(chosen_E), n_H_routes=len(chosen_H),
                n_H_short=len(chosen_Hs), n_H_long=len(chosen_Hl),
                n_buses=int(n_buses), routes_E=chosen_E, routes_H=chosen_H,
                pool_sizes=dict(E=len(R_E), Hs=len(R_Hs), Hl=len(R_Hl)))


# --------------------------------------------------------------------------------------
# Solution summary
# --------------------------------------------------------------------------------------
def summarize(sol: dict, inst: dict, p: Params) -> dict:
    rE, rH = sol["routes_E"], sol["routes_H"]
    dist_total = sum(r["distance"] for r in rE) + sum(r["distance"] for r in rH)
    riders = sum(r["riders"] for r in rE) + sum(r["riders"] for r in rH)
    smin = sum(r["student_minutes"] for r in rE) + sum(r["student_minutes"] for r in rH)
    cost = p.fixed_cost * sol["n_buses"] + p.var_cost_km * dist_total

    def stats(rs, loads):
        """Student-weighted ride-time statistics (each stop weighted by its student load)."""
        total = 0.0
        smin_l = 0.0
        mx = 0.0
        mn = 1e18
        for r in rs:
            for i, s in enumerate(r["order"]):
                w = loads[s]
                rt = r["ride"][i]
                total += w
                smin_l += w * rt
                mx = max(mx, rt)
                mn = min(mn, rt)
        if total == 0:
            return dict(n=0, max=0.0, mean=0.0, min=0.0, student_minutes=0.0)
        return dict(n=int(total), max=round(mx, 2), mean=round(smin_l / total, 2),
                    min=round(mn, 2), student_minutes=round(smin_l, 0))

    return dict(policy=sol["policy"], status=sol["status"],
                objective=round(sol["objective"], 2),
                n_buses=sol["n_buses"], n_E_routes=sol["n_E_routes"], n_H_routes=sol["n_H_routes"],
                n_H_short=sol["n_H_short"], n_H_long=sol["n_H_long"],
                distance_km=round(dist_total, 1), students=round(riders, 0),
                cost_usd=round(cost, 0),
                cost_per_student=round(cost / max(riders, 1), 2),
                student_minutes=round(smin, 0),
                ride_elem=stats(rE, inst["loads_e"]), ride_high=stats(rH, inst["loads_h"]),
                pool_sizes=sol["pool_sizes"])


# --------------------------------------------------------------------------------------
# Simple analytic lower bounds (for validation)
# --------------------------------------------------------------------------------------
def lower_bounds(inst: dict, p: Params) -> dict:
    loadse, loadsh = inst["loads_e"], inst["loads_h"]
    TE = sum(loadse.values())
    TH = sum(loadsh.values())
    bE = math.ceil(TE / p.cap)
    bH = math.ceil(TH / p.cap)
    buses_sep_lb = bE + bH
    buses_comb_lb = max(bE, bH)
    # distance lower bound: a route visiting k stops at least needs to reach the farthest
    # stop it serves and return to school -> radial bound. Sum over stops of 2*radial
    # divided by capacity gives a crude capacity-based distance bound.
    dist = inst["dist"]
    DEPOT, ELEM, HIGH = inst["DEPOT"], inst["ELEM"], inst["HIGH"]
    radE = sum(dist[DEPOT, s] for s in range(inst["S"]) if loadse[s] > 0)
    radH = sum(dist[DEPOT, s] for s in range(inst["S"]) if loadsh[s] > 0)
    dist_lb_sep = 2.0 * (radE / p.cap + radH / p.cap)
    dist_lb_comb = 2.0 * (radE / p.cap) + 2.0 * (radH / p.cap)  # same order of magnitude
    return dict(elem_total=TE, high_total=TH,
                buses_sep_lb=buses_sep_lb, buses_comb_lb=buses_comb_lb,
                dist_lb_sep=round(dist_lb_sep, 1), dist_lb_comb=round(dist_lb_comb, 1))


# --------------------------------------------------------------------------------------
# Quick self-test
# --------------------------------------------------------------------------------------
if __name__ == "__main__":
    p = Params()
    inst = build_instance(p)
    print("stops:", inst["S"], "elem:", sum(inst["loads_e"].values()),
          "high:", sum(inst["loads_h"].values()))
    print("lower bounds:", lower_bounds(inst, p))
    pools = build_pools(inst, p)
    print("pool sizes:", {k: len(v) for k, v in pools.items()})
    solS = solve_sbrp(inst, p, pools, allow_share=False, use_short_H=False, use_long_H=True)
    print("S:", summarize(solS, inst, p))
    solC = solve_sbrp(inst, p, pools, allow_share=True, use_short_H=True, use_long_H=True)
    print("C:", summarize(solC, inst, p))
