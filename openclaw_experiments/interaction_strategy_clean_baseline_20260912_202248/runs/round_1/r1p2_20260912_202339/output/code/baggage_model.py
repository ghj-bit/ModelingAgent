"""
ICM 2003 - Aviation Baggage Screening Strategies
Core quantitative model: EDS sizing, arrival-rate refinement, scheduling,
ETD augmentation, cost, and national scaling.

Reproducible: python baggage_model.py
Outputs: results/model_results.json  (+ prints human-readable summary)
"""
import json
import math
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RES = os.path.join(ROOT, "results")
os.makedirs(RES, exist_ok=True)

rng = np.random.default_rng(20030412)

# ----------------------------------------------------------------------------
# 1. INPUT DATA (Technical Information Sheet, Table 1)
# ----------------------------------------------------------------------------
# (flight_type, seats, n_flights_A, n_flights_B, occ_lo, occ_hi)
TABLE1 = [
    (1, 34, 10, 8, 0.70, 1.00),
    (2, 46, 4, 6, 0.70, 1.00),
    (3, 85, 3, 7, 0.70, 1.00),
    (4, 128, 3, 5, 0.60, 1.00),
    (5, 142, 19, 9, 0.60, 1.00),
    (6, 194, 5, 10, 0.60, 1.00),
    (7, 215, 1, 2, 0.60, 1.00),
    (8, 350, 1, 1, 0.50, 1.00),
]

# Baggage checking behaviour: 20% zero, 20% one, 60% two bags
P_BAGS = np.array([0.20, 0.20, 0.60])
BAGS_MEAN = float((np.array([0, 1, 2]) * P_BAGS).sum())          # 1.4
BAGS_VAR = float(((np.array([0, 1, 2])**2 * P_BAGS).sum()) - BAGS_MEAN**2)  # 0.64

# EDS / ETD performance envelope (from the problem statement)
EDS_THRU_RANGE = (160, 210)      # bags / hour
EDS_THRU_MID = 180.0             # midpoint used as base case
EDS_AVAIL = 0.92                 # operational fraction of time
EDS_UNIT_COST = 1_000_000.0
EDS_INSTALL = {"A": 100_000.0, "B": 80_000.0}

# ETD assumptions (see report for sources/sensitivity)
ETD_SAMPLES_PER_HOUR_MIN = 180.0   # Federal Register 67 FR 48436 (2002) certification floor
ETD_EFF_BAGS_PER_HOUR = 90.0       # effective incl. sample acquisition/swab (assumption)
ETD_UNIT_COST = 50_000.0           # assumption
ETD_INSTALL = 20_000.0             # assumption

# Passenger arrival window before scheduled departure (minutes)
ARR_MIN, ARR_MAX = 45.0, 120.0
ARR_WINDOW = ARR_MAX - ARR_MIN     # 75 minutes


# ----------------------------------------------------------------------------
# 2. DEMAND MODEL
# ----------------------------------------------------------------------------
def occupancy_moments(lo, hi):
    return (lo + hi) / 2.0, (hi - lo) ** 2 / 12.0

def airport_demand(col):
    """Mean/variance of passengers and checked bags for one airport column."""
    rows, pax_mean, pax_var, bag_mean, bag_var = [], 0.0, 0.0, 0.0, 0.0
    for (t, s, a, b, lo, hi) in TABLE1:
        n = a if col == "A" else b
        mo, vo = occupancy_moments(lo, hi)
        pm = mo * s
        pv = vo * s * s
        bm = BAGS_MEAN * pm
        bv = BAGS_MEAN**2 * pv + BAGS_VAR * pm
        pax_mean += n * pm
        pax_var += n * pv
        bag_mean += n * bm
        bag_var += n * bv
        rows.append(dict(type=t, seats=s, n=n, seats_total=n * s,
                         occ_mean=mo, pax_mean=n * pm, bags_mean=n * bm))
    return dict(rows=rows, pax_mean=pax_mean, pax_sd=math.sqrt(pax_var),
                bags_mean=bag_mean, bags_sd=math.sqrt(bag_var))

def bags_quantile(demand, q=0.95):
    """95th percentile of total peak-hour bags (normal/CLT approximation)."""
    # z-scores
    z = {0.90: 1.2816, 0.95: 1.6449, 0.99: 2.3263}[q]
    return demand["bags_mean"] + z * demand["bags_sd"]


# ----------------------------------------------------------------------------
# 3. EDS SIZING MODELS
#    M1  aggregate: all peak-hour bags cleared inside the 60-min peak hour
#    M2  arrival-rate: peak screening rate set by the 75-min pax arrival window
#    M3  scheduling: departures spread over a horizon H >= 75 min
# ----------------------------------------------------------------------------
def peak_rate_per_min(bags_total, depart_span_min):
    """Peak bag-arrival rate (bags/min) under the physical arrival model.

    Each flight's bags arrive uniformly over a 75-min window.  With departures
    spread over a span H, the peak rate equals total/max(H,75).
    """
    return bags_total / max(depart_span_min, ARR_WINDOW)

def eds_from_rate(rate_per_min, throughput, avail=EDS_AVAIL):
    hourly = rate_per_min * 60.0
    return int(math.ceil(hourly / (throughput * avail))), hourly

def eds_count(bags_total, throughput, span_min=60.0, avail=EDS_AVAIL):
    """M2/M3 sizing: span_min is the departure span (physical arrival model)."""
    return eds_from_rate(peak_rate_per_min(bags_total, span_min), throughput, avail)

def eds_count_aggregate(bags_total, throughput, hours=1.0, avail=EDS_AVAIL):
    """M1 sizing: clear all bags belonging to the peak hour within that hour."""
    return eds_from_rate(bags_total / (60.0 * hours), throughput, avail)

def eds_table(demand, span_min):
    out = {}
    for thr in (160, 180, 210):
        n, hr = eds_count(demand["bags_mean"], thr, span_min)
        n95, _ = eds_count(bags_quantile(demand, 0.95), thr, span_min)
        out[thr] = dict(deterministic=n, hourly_equiv=round(hr, 1), q95=n95)
    return out

def eds_table_aggregate(demand):
    out = {}
    for thr in (160, 180, 210):
        n, hr = eds_count_aggregate(demand["bags_mean"], thr)
        n95, _ = eds_count_aggregate(bags_quantile(demand, 0.95), thr)
        out[thr] = dict(deterministic=n, hourly_equiv=round(hr, 1), q95=n95)
    return out


# ----------------------------------------------------------------------------
# 4. ETD AUGMENTATION
# ----------------------------------------------------------------------------
def etd_counts(bags_total, alarm_rates=(0.05, 0.10, 0.20),
               etd_rates=(90.0, 165.6)):
    out = {}
    for pa in alarm_rates:
        alarms = bags_total * pa
        out[pa] = {er: int(math.ceil(alarms / (er * EDS_AVAIL))) for er in etd_rates}
    return out


# ----------------------------------------------------------------------------
# 5. COST MODEL
# ----------------------------------------------------------------------------
def capital_cost(n_eds, n_etd, airport, eds_install=None, etd_install=None):
    ei = EDS_INSTALL[airport] if eds_install is None else eds_install
    et = ETD_INSTALL if etd_install is None else etd_install
    return n_eds * (EDS_UNIT_COST + ei) + n_etd * (ETD_UNIT_COST + et)

def tco_10yr(capex, maint_frac=0.10):
    return capex + maint_frac * capex * 10.0


# ----------------------------------------------------------------------------
# 6. SCHEDULING MODEL
#    Optimal departure-time distribution minimises the peak bag-arrival rate.
#    Within any span H <= 75 the peak is invariant (total/75): scheduling inside
#    the peak hour cannot reduce the requirement.  Spreading beyond 75 min does.
#    We minimise a system cost  C(H) = capex(H) + disruption(H).
# ----------------------------------------------------------------------------
def disruption_cost(H, flights, per_flight_min_penalty=120.0, H_ref=60.0):
    """Airline/airport cost of shifting the departure bank beyond the peak hour.
    Model: every flight-minute of departure displacement from the nominal
    60-min bank costs `per_flight_min_penalty` USD (schedule disruption,
    missed connections, passenger inconvenience).  Total displacement for a
    uniform spread over H is flights*(H-60)/4 (average shift).
    """
    shift = max(0.0, H - H_ref)
    total_flight_minutes = flights * shift / 4.0
    return per_flight_min_penalty * total_flight_minutes

def optimal_horizon(demand, flights, throughput=EDS_THRU_MID,
                    per_flight_min_penalty=120.0, maint_frac=0.10, life=10.0,
                    airport="A", H_max=120):
    """Search H in [60, H_max] min for the least system cost.

    H_max is a hard operational cap: a 'peak-hour' departure bank cannot be
    stretched arbitrarily without breaking connecting-flight waves, curfews and
    runway-slot contracts, so we bound the allowable spreading.
    """
    best = None
    for H in range(60, H_max + 1, 5):
        n, _ = eds_count(demand["bags_mean"], throughput, span_min=H)
        capex = n * (EDS_UNIT_COST + EDS_INSTALL[airport])
        dis = disruption_cost(H, flights, per_flight_min_penalty)
        tco = tco_10yr(capex, maint_frac)
        sys_cost = tco + life * dis
        if best is None or sys_cost < best["system_cost"]:
            best = dict(H=H, n_eds=n, capex=capex, system_cost=sys_cost,
                        disruption=dis, tco=tco)
    return best

def horizon_curve(demand, throughput=EDS_THRU_MID, airport="A",
                  horizons=(60, 75, 90, 105, 120, 150, 180, 240)):
    """EDS requirement as a function of the departure-bank span H."""
    return {H: dict(peak_rate=round(peak_rate_per_min(demand["bags_mean"], H), 2),
                    hourly=round(peak_rate_per_min(demand["bags_mean"], H) * 60, 1),
                    n_eds=eds_count(demand["bags_mean"], throughput, H)[0])
            for H in horizons}


def adoption_curve(demand, throughput=EDS_THRU_MID, airport="A",
                   H_target=120.0, fracs=(0.0, 0.25, 0.5, 0.75, 1.0)):
    """Partial-adoption (conditional) procurement curve.

    A share ``f`` of the peak-hour flights is re-timed to widen the effective
    departure bank to ``H_target`` minutes; the remaining ``1-f`` stay in the
    60-minute core.  The stationary (core) flights' bags still peak at
    (1-f)L/75, while the re-timed flights contribute fL/H_target.  Hence

        r_peak(f) = L * [ (1-f)/75 + f/H_target ],   N(f)=ceil(60 r_peak(f)/(c*eta)).

    ``f`` is an *adoption/cooperation* share that the airport cannot enforce,
    so it is reported as a conditional curve rather than a single optimum.
    """
    L = demand["bags_mean"]
    out = {}
    for f in fracs:
        rate = L * ((1 - f) / ARR_WINDOW + f / H_target)      # bags/min
        hourly = rate * 60.0
        n = int(math.ceil(hourly / (throughput * EDS_AVAIL)))
        out[f] = dict(peak_rate=round(rate, 2), hourly=round(hourly, 1), n_eds=n)
    return out

def break_even_adoption(demand, target_n, throughput=EDS_THRU_MID, H_target=120.0):
    """Minimum re-timing share f that permits a fleet of target_n EDS.

    Solve ceil(60*L*[(1-f)/75 + f/H]/(c*eta)) <= target_n for the smallest f.
    """
    L = demand["bags_mean"]
    for i in range(0, 101):
        f = i / 100.0
        rate = L * ((1 - f) / ARR_WINDOW + f / H_target)
        if math.ceil((rate * 60.0) / (throughput * EDS_AVAIL)) <= target_n:
            return round(f, 2)
    return None


# ----------------------------------------------------------------------------
# 7. NATIONAL / REGIONAL SCALING
# ----------------------------------------------------------------------------
def scaling(airport_profile, airports):
    """Simple tier decomposition of a region/nation."""
    out = {}
    for name, (frac, flight_scale) in airport_profile.items():
        n_ap = round(airports * frac)
        out[name] = dict(airports=n_ap, flight_scale=flight_scale)
    return out


# ----------------------------------------------------------------------------
# 8. RUN
# ----------------------------------------------------------------------------
def main():
    results = {"meta": {
        "bag_mean_per_pax": BAGS_MEAN,
        "bag_var_per_pax": BAGS_VAR,
        "eds_throughput_range": EDS_THRU_RANGE,
        "eds_throughput_base": EDS_THRU_MID,
        "eds_availability": EDS_AVAIL,
        "arrival_window_min": ARR_WINDOW,
    }}

    demand = {c: airport_demand(c) for c in ("A", "B")}

    # --- per-airport demand ---
    dem_out = {}
    for c in ("A", "B"):
        d = demand[c]
        dem_out[c] = dict(pax_mean=round(d["pax_mean"], 1),
                          pax_sd=round(d["pax_sd"], 2),
                          bags_mean=round(d["bags_mean"], 1),
                          bags_sd=round(d["bags_sd"], 2),
                          bags_q95=round(bags_quantile(d, 0.95), 1),
                          rows=[{k: (round(v, 3) if isinstance(v, float) else v)
                                 for k, v in r.items()} for r in d["rows"]])
        nfl = sum(r["n"] for r in d["rows"])
        dem_out[c]["n_flights"] = nfl
        dem_out[c]["n_seats"] = sum(r["seats_total"] for r in d["rows"])
    results["demand"] = dem_out

    # --- EDS sizing under three planning assumptions ---
    eds_out = {}
    for c in ("A", "B"):
        d = demand[c]
        eds_out[c] = {
            "M1_aggregate_60min": eds_table_aggregate(d),
            "M2_arrival_window": eds_table(d, span_min=60.0),
            "M3_spread_120min": eds_table(d, span_min=120.0),
            "M3_spread_180min": eds_table(d, span_min=180.0),
        }
    results["eds"] = eds_out

    # --- ETD ---
    results["etd"] = {
        c: etd_counts(demand[c]["bags_mean"]) for c in ("A", "B")
    }

    # --- costs (base design = M2 arrival-window, throughput 180, q95) ---
    DAILY_MULTIPLE = 10.0   # daily bags ~ 10 x the busiest-hour bags (assumption)
    cost = {}
    for c in ("A", "B"):
        d = demand[c]
        n_eds = eds_count(bags_quantile(d, 0.95), EDS_THRU_MID, span_min=75.0)[0]
        n_etd = int(math.ceil(bags_quantile(d, 0.95) * 0.10 / (90.0 * EDS_AVAIL)))
        capex = capital_cost(n_eds, n_etd, c)
        annual_bags = d["bags_mean"] * DAILY_MULTIPLE * 365
        cost[c] = dict(n_eds=n_eds, n_etd=n_etd, capex=round(capex),
                       tco_10yr=round(tco_10yr(capex)),
                       annual_bags=round(annual_bags),
                       per_bag_basis=round(tco_10yr(capex) / (annual_bags * 10), 4))
    results["cost_base"] = cost

    # --- policy comparison (capital, USD) ---
    n_eds_m1 = {c: eds_count_aggregate(demand[c]["bags_mean"], EDS_THRU_MID)[0] for c in ("A", "B")}
    n_eds_m2 = {c: eds_count(demand[c]["bags_mean"], EDS_THRU_MID, 75.0)[0] for c in ("A", "B")}
    n_eds_m3 = {c: eds_count(demand[c]["bags_mean"], EDS_THRU_MID, 120.0)[0] for c in ("A", "B")}
    n_etd_10 = {c: int(math.ceil(demand[c]["bags_mean"] * 0.10 / (90.0 * EDS_AVAIL))) for c in ("A", "B")}
    def policy_cost(n_eds, n_etd):
        tot = 0.0
        for c in ("A", "B"):
            tot += n_eds[c] * (EDS_UNIT_COST + EDS_INSTALL[c])
            tot += n_etd[c] * (ETD_UNIT_COST + ETD_INSTALL)
        return tot
    results["policies"] = {
        "P0_EDS_only_M1": dict(n_eds=n_eds_m1, n_etd={c: 0 for c in ("A", "B")},
                               capex=round(policy_cost(n_eds_m1, {c: 0 for c in ("A", "B")}))),
        "P1_EDS_M2_plus_ETD": dict(n_eds=n_eds_m2, n_etd=n_etd_10,
                                    capex=round(policy_cost(n_eds_m2, n_etd_10))),
        "P2_EDS_sched120_plus_ETD": dict(n_eds=n_eds_m3, n_etd=n_etd_10,
                                          capex=round(policy_cost(n_eds_m3, n_etd_10))),
    }

    # --- ETD-primary cost/capacity comparison ---
    results["etd_mix"] = {
        "eds_cost_per_1000_bags_hr_capacity": round(EDS_UNIT_COST / (EDS_THRU_MID * EDS_AVAIL) * 1000, 1),
        "etd_cost_per_1000_bags_hr_capacity": round(ETD_UNIT_COST / (90.0 * EDS_AVAIL) * 1000, 1),
        "ratio_eds_over_etd_unit_cost": round((EDS_UNIT_COST / (EDS_THRU_MID * EDS_AVAIL)) /
                                              (ETD_UNIT_COST / (90.0 * EDS_AVAIL)), 2),
    }

    # --- cost across throughputs for the conservative M1 policy ---
    cost_m1 = {}
    for c in ("A", "B"):
        d = demand[c]
        row = {}
        for thr in (160, 180, 210):
            n, _ = eds_count_aggregate(d["bags_mean"], thr)
            capex = n * (EDS_UNIT_COST + EDS_INSTALL[c])
            row[thr] = dict(n_eds=n, capex=round(capex), tco=round(tco_10yr(capex)))
        cost_m1[c] = row
    results["cost_M1"] = cost_m1

    # --- scheduling ---
    sched = {}
    for c in ("A", "B"):
        d = demand[c]
        nfl = sum(r["n"] for r in d["rows"])
        opt = optimal_horizon(d, nfl, throughput=EDS_THRU_MID,
                              per_flight_min_penalty=120.0, airport=c, H_max=120)
        sched[c] = dict(optimal=opt,
                        curve=horizon_curve(d, airport=c),
                        adoption=adoption_curve(d, airport=c),
                        break_even={
                            "n25": break_even_adoption(d, 25),
                            "n27": break_even_adoption(d, 27),
                            "n30": break_even_adoption(d, 30),
                            "n31": break_even_adoption(d, 31),
                        },
                        baseline_H60=dict(
                            n_eds=eds_count(d["bags_mean"], EDS_THRU_MID, 60.0)[0],
                            peak_rate=round(peak_rate_per_min(d["bags_mean"], 60.0), 2)),
                        peak_rates={H: round(peak_rate_per_min(d["bags_mean"], H), 2)
                                    for H in (60, 75, 90, 120, 180, 240)})
    results["scheduling"] = sched

    # --- sensitivity ---
    sens = {}

    # throughput sensitivity
    sens["throughput"] = {
        c: {thr: eds_count(demand[c]["bags_mean"], thr, 75.0)[0]
            for thr in (160, 170, 180, 190, 200, 210)} for c in ("A", "B")
    }
    # occupancy sensitivity (uniform occ within declared range -> expand/compress)
    occ_sens = {}
    for c in ("A", "B"):
        d = demand[c]
        occ_mult = {}
        for m in (0.90, 0.95, 1.00, 1.05, 1.10):
            bags = d["bags_mean"] * m
            occ_mult[round(m, 2)] = eds_count(bags, EDS_THRU_MID, 75.0)[0]
        occ_sens[c] = occ_mult
    sens["occupancy_multiplier"] = occ_sens
    # bag-per-pax sensitivity
    bpp_sens = {}
    for c in ("A", "B"):
        d = demand[c]
        row = {}
        for bpp in (1.0, 1.2, 1.4, 1.6, 1.8):
            bags = d["pax_mean"] * bpp
            row[bpp] = eds_count(bags, EDS_THRU_MID, 75.0)[0]
        bpp_sens[c] = row
    sens["bags_per_pax"] = bpp_sens
    # availability sensitivity
    avail_sens = {}
    for c in ("A", "B"):
        d = demand[c]
        avail_sens[c] = {a: eds_count(d["bags_mean"], EDS_THRU_MID, 75.0, avail=a)[0]
                         for a in (0.80, 0.85, 0.92, 0.95, 1.00)}
    sens["availability"] = avail_sens
    results["sensitivity"] = sens

    # --- national/regional scaling ---
    # Midwest region: 193 airports; national: 429 airports (problem statement)
    # Tier profile chosen to reflect a hub-and-spoke size distribution.
    tiers = {
        "large (like A/B)": (0.05, 1.00),
        "medium":           (0.15, 0.50),
        "small":            (0.30, 0.20),
        "very small":       (0.50, 0.05),
    }
    def regional(airports):
        base_ags = {c: eds_count(demand[c]["bags_mean"], EDS_THRU_MID, 75.0)[0]
                    for c in ("A", "B")}
        avg_base = (base_ags["A"] + base_ags["B"]) / 2.0
        tot = 0
        detail = {}
        for name, (frac, fs) in tiers.items():
            n_ap = round(airports * frac)
            eds = int(math.ceil(avg_base * fs))
            detail[name] = dict(airports=n_ap, eds_each=eds, eds_total=n_ap * eds)
            tot += n_ap * eds
        return tot, detail
    reg_tot, reg_detail = regional(193)
    nat_tot, nat_detail = regional(429)
    results["scaling"] = dict(
        region_193=dict(total_eds=reg_tot, detail=reg_detail),
        national_429=dict(total_eds=nat_tot, detail=nat_detail),
        region_cost_edges=round(reg_tot * (EDS_UNIT_COST + 0.09e6)),
        national_cost_edges=round(nat_tot * (EDS_UNIT_COST + 0.09e6)),
    )

    # --- optimised departure schedule (concrete) for the recommended horizon ----
    def build_schedule(d, H, n_blocks=8):
        """Distribute flights of each type across n_blocks to equalise bag load."""
        block_len = H / n_blocks
        loads = [0.0] * n_blocks
        assign = [dict() for _ in range(n_blocks)]
        flights = []
        for r in d["rows"]:
            for _ in range(r["n"]):
                flights.append((r["type"], r["bags_mean"] / r["n"]))
        flights.sort(key=lambda x: -x[1])
        for t, bags in flights:
            k = int(np.argmin(loads))
            loads[k] += bags
            assign[k][t] = assign[k].get(t, 0) + 1
        return dict(block_min=block_len,
                    blocks=[dict(block=i + 1, start_min=round(i * block_len, 1),
                                 end_min=round((i + 1) * block_len, 1),
                                 flights=dict(sorted(assign[i].items())),
                                 n_flights=sum(assign[i].values()),
                                 bag_load=round(loads[i], 1))
                            for i in range(n_blocks)])
    results["schedule_120min"] = {c: build_schedule(demand[c], 120.0) for c in ("A", "B")}

    with open(os.path.join(RES, "model_results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    # ---- console summary ----
    for c in ("A", "B"):
        d = results["demand"][c]
        print(f"=== Airport {c} ===")
        print(f"  flights={d['n_flights']}  seats={d['n_seats']}")
        print(f"  pax={d['pax_mean']}  bags={d['bags_mean']} (sd {d['bags_sd']}, q95 {d['bags_q95']})")
        print(f"  EDS M1(60min) thr180: {results['eds'][c]['M1_aggregate_60min'][180]['deterministic']}")
        print(f"  EDS M2(75min) thr180: {results['eds'][c]['M2_arrival_window'][180]['deterministic']}")
        print(f"  EDS M3(120min) thr180: {results['eds'][c]['M3_spread_120min'][180]['deterministic']}")
        print(f"  ETD @10% alarm: {results['etd'][c][0.1]}")
        print(f"  adoption curve: {results['scheduling'][c]['adoption']}")
        print(f"  break-even f: {results['scheduling'][c]['break_even']}")
        print(f"  cost base: {results['cost_base'][c]}")
        print(f"  optimal horizon: {results['scheduling'][c]['optimal']}")
    print("regional 193:", results["scaling"]["region_193"]["total_eds"], "EDS")
    print("national 429:", results["scaling"]["national_429"]["total_eds"], "EDS")
    print("Wrote", os.path.join(RES, "model_results.json"))


if __name__ == "__main__":
    main()
