"""
testing.py - Pre-implementation testing of the school-busing model.

  A) Equity control: sweep the ride-time penalty alpha and show the cost / ride-time
     trade-off frontier for Policy C (cost vs. comfort).
  B) Robustness (Monte-Carlo): replay the deterministic schedules under travel-time
     uncertainty (driver, weather, traffic) and measure the probability that the
     one-hour ride limit or the bell times are violated. This informs the operating
     safety margin recommended before real deployment.
"""

from __future__ import annotations
import os
import sys
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from dataclasses import replace
from sbrp import (Params, build_instance, build_pools, solve_sbrp, summarize, route_profile)
from run_experiments import make_params


def alpha_sweep():
    print("### A) Equity-control sweep (Policy C, rural)\n")
    print("| alpha ($/student-min) | buses | cost ($) | maxElem | meanElem | maxHigh | meanHigh | student-min |")
    print("|---|---|---|---|---|---|---|---|")
    for a in [0.0, 0.02, 0.05, 0.10, 0.20, 0.50]:
        p = replace(make_params("rural"), alpha_ride=a, time_limit=25)
        inst = build_instance(p)
        pools = build_pools(inst, p)
        sol = solve_sbrp(inst, p, pools, allow_share=True, use_short_H=True, use_long_H=True)
        s = summarize(sol, inst, p)
        print(f"| {a:.2f} | {s['n_buses']} | {s['cost_usd']} | {s['ride_elem']['max']} | "
              f"{s['ride_elem']['mean']} | {s['ride_high']['max']} | {s['ride_high']['mean']} | "
              f"{s['student_minutes']} |")


def simulate_routes(routes, p, inst, speed_factor, rng, leg_cv=0.0):
    """Replay fixed schedules under a realised speed factor. Returns (max_ride, late_minutes)."""
    dist = inst["dist"]
    loads = {}
    loads.update(inst["loads_e"])
    loads.update(inst["loads_h"])
    worst_ride = 0.0
    worst_late = 0.0
    for r in routes:
        order = list(r["order"])
        start, end = r["start"], r["end"]
        deadline = p.bell_elem if r["level"] == "E" else p.bell_high
        speed = p.speed_kmh * speed_factor
        # actual duration
        dur = 0.0
        prev = start
        for s in order:
            leg = dist[prev, s] / speed * 60.0
            if leg_cv > 0:
                leg *= max(0.2, 1.0 + rng.normal(0, leg_cv))
            dur += leg + p.service_fixed + p.service_per_student * loads[s]
            prev = s
        leg = dist[prev, end] / speed * 60.0
        if leg_cv > 0:
            leg *= max(0.2, 1.0 + rng.normal(0, leg_cv))
        dur += leg
        worst_ride = max(worst_ride, dur)
        arrival = r["depart"] + dur
        worst_late = max(worst_late, arrival - deadline)
    return worst_ride, worst_late


def robustness():
    print("\n### B) Monte-Carlo robustness of the rural schedules\n")
    base = make_params("rural")
    results = {}
    for pol, kw in (("S", dict(allow_share=False, use_short_H=False, use_long_H=True)),
                    ("C", dict(allow_share=True, use_short_H=True, use_long_H=True))):
        p = replace(base, time_limit=25)
        inst = build_instance(p)
        pools = build_pools(inst, p)
        sol = solve_sbrp(inst, p, pools, **kw)
        routes = sol["routes_E"] + sol["routes_H"]
        rng = np.random.default_rng(12345)
        for cv in [0.08, 0.12, 0.18, 0.25]:
            n = 2000
            over60 = 0
            late = 0
            worst = 0.0
            for _ in range(n):
                f = max(0.5, rng.normal(1.0, cv))
                wr, wl = simulate_routes(routes, p, inst, f, rng, leg_cv=cv)
                if wr > 60.0:
                    over60 += 1
                if wl > 0:
                    late += 1
                worst = max(worst, wr)
            results[(pol, cv)] = (100.0 * over60 / n, 100.0 * late / n, worst)
            print(f"policy {pol}  speed-CV={cv:.2f}:  P(ride>60min)={100.0*over60/n:5.1f}%  "
                  f"P(late arrival)={100.0*late/n:5.1f}%  worst ride={worst:.1f} min")
    return results


def margin_test(cv: float = 0.12):
    """Design at different nominal ride-time caps, then stress-test at CV.
    Shows the safety margin needed so that the realised ride stays <= 60 min."""
    print(f"\n### C) Safety-margin study (Policy C, rural, speed-CV={cv})\n")
    print("| nominal cap (min) | buses | cost ($) | P(ride>60min) | P(late) | worst ride |")
    print("|---|---|---|---|---|---|")
    base = make_params("rural")
    for cap in [40, 45, 50, 55, 60]:
        p = replace(base, max_ride=cap, time_limit=25)
        inst = build_instance(p)
        pools = build_pools(inst, p)
        sol = solve_sbrp(inst, p, pools, allow_share=True, use_short_H=True, use_long_H=True)
        s = summarize(sol, inst, p)
        routes = sol["routes_E"] + sol["routes_H"]
        rng = np.random.default_rng(999)
        n = 3000
        over = late = 0
        worst = 0.0
        for _ in range(n):
            f = max(0.5, rng.normal(1.0, cv))
            wr, wl = simulate_routes(routes, p, inst, f, rng, leg_cv=cv)
            if wr > 60.0:
                over += 1
            if wl > 0:
                late += 1
            worst = max(worst, wr)
        print(f"| {cap} | {s['n_buses']} | {s['cost_usd']} | {100.0*over/n:.1f}% | "
              f"{100.0*late/n:.1f}% | {worst:.1f} |")


if __name__ == "__main__":
    alpha_sweep()
    robustness()
    margin_test()
