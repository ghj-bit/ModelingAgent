# -*- coding: utf-8 -*-
"""
The Bicycle Wheel Problem (MCM 2001, Problem A)
Rear-wheel choice: solid disc vs. spoked, front wheel always spoked.

This script implements the "power-balance / threshold-wind-speed" model.

Units: SI (m, s, kg, N, W).  Speeds reported in m/s *and* km/h.

Author: modeling agent (autonomous run)
"""

import numpy as np
import json, os

# ----------------------------------------------------------------------
# 0. Global physical constants and reference data
# ----------------------------------------------------------------------
g      = 9.81          # m/s^2
rho    = 1.226         # kg/m^3  air density, sea level, 15 C (ISA)
crr    = 0.004         # rolling-resistance coefficient, tyre on asphalt
M_ref  = 80.0          # kg  reference rider+bike (used for validation only)

# problem-given kinematics
V_START_KPH = 45.0
V5_KPH      = 37.0     # after 100 m on a 5 % grade  (lose ~8 kph)
L_REF       = 100.0    # m  reference length over which the deceleration is defined

v0     = V_START_KPH/3.6          # 12.5 m/s
v5     = V5_KPH/3.6               # 10.277... m/s
# deceleration is proportional to grade  a = c_dec * G
c_dec  = (v0**2 - v5**2) / (2.0*L_REF*0.05)   # m/s^2 per unit grade

# wheel data (differences drive the entire comparison)
DM_DEFAULT    = 0.50    # kg   disc is heavier
DCDA_DEFAULT  = 0.0035  # m^2  disc has lower drag area (head-on)

# ----------------------------------------------------------------------
# 1. Rider speed profile on a constant-grade incline
# ----------------------------------------------------------------------
def speed_stats(G, c=c_dec, v0=v0, L=L_REF):
    """Return (v_end, v_bar, mean_v2) over the first L metres of grade G.

    Constant deceleration a = c*G  =>  v(s)^2 = v0^2 - 2*a*s.
    v_bar      = distance average of v
    mean_v2    = distance average of v^2
    Returns None if the rider cannot cover L metres.
    """
    a = c*G
    disc = v0**2 - 2.0*a*L
    if disc <= 0.0:
        return None
    v_end = np.sqrt(disc)
    if abs(a) < 1e-12:
        v_bar   = v0
        mean_v2 = v0**2
    else:
        k = 2.0*a
        v_bar   = (2.0/(3.0*k))*(v0**3 - disc**1.5)/L
        mean_v2 = v0**2 - k*L/2.0
    return v_end, v_bar, mean_v2

# ----------------------------------------------------------------------
# 2. Threshold headwind
# ----------------------------------------------------------------------
def threshold_headwind(G, dm=DM_DEFAULT, dCdA=DCDA_DEFAULT,
                       method="integral"):
    """Headwind w* at which the power required by the two rear wheels is equal.

    Difference in propulsive power  DeltaP = P_solid - P_spoked :

        DeltaP = v * [ dm*g*(G+crr) + 0.5*rho*(dCdA_solid-dCdA_spoked)*(v+w)^2 ]
               = v * [ dm*g*(G+crr) - 0.5*rho*dCdA*(v+w)^2 ]        (dCdA>0)

    method='integral' : average over the reference O100 m of incline
    method='average'  : evaluate at the distance-averaged speed
    method='start'    : evaluate at the initial speed v0

    Returns ('always_solid', None)   if w*<=0  (solid better for any wind>=0)
            ('ok', w*)               otherwise
    """
    st = speed_stats(G)
    if st is None:
        return ('no_climb', None)
    v_end, v_bar, mean_v2 = st
    K = 2.0*dm*g*(G+crr) / (rho*dCdA)          # constant part (m^2/s^2)

    if method == "integral":
        var = mean_v2 - v_bar**2               # >=0
        val = K - var
        if val <= 0.0:
            return ('always_solid', None)
        return ('ok', np.sqrt(val) - v_bar)
    elif method == "average":
        val = K
        if val <= 0.0:
            return ('always_solid', None)
        return ('ok', np.sqrt(val) - v_bar)
    elif method == "start":
        val = K
        if val <= 0.0:
            return ('always_solid', None)
        return ('ok', np.sqrt(val) - v0)
    else:
        raise ValueError(method)

# ----------------------------------------------------------------------
# 3. Validation: propulsive power at 45 km/h on the level
# ----------------------------------------------------------------------
def level_power(v, CdA=0.25, mass=M_ref):
    """Steady power to hold speed v on flat ground (rider+frame only)."""
    F = crr*mass*g + 0.5*rho*CdA*v**2
    return F*v

# ----------------------------------------------------------------------
# 4. Yaw-aware wheel-drag model (supplementary / Task 3 discussion)
# ----------------------------------------------------------------------
# Axial drag coefficient referenced to the wheel side area A_ref = pi*R^2.
# Representative fits informed by Greenwell et al. (1995) and Tew & Sayers
# (1999) as summarised in the 2001 MCM papers:
#   * spoked wheel : C increases gently with yaw
#   * disc wheel   : C falls sharply with yaw (sail effect)
R_WHEEL = 0.35
A_REF   = np.pi*R_WHEEL**2

def C_spoked(phi_deg):
    return 0.058 + 0.0020*phi_deg

def C_disc(phi_deg):
    return max(-0.008, 0.050 - 0.0026*phi_deg)

def wheel_drag_area_diff(phi_deg):
    """(CdA_disc - CdA_spoked) for the rear wheel (0.75 interference factor)."""
    return 0.75*A_REF*(C_disc(phi_deg) - C_spoked(phi_deg))

def yaw_of(v, Vw, psi_deg):
    """yaw angle (deg) and relative air speed (m/s) for wind speed Vw at
    angle psi from the direction of travel (0=dead headwind)."""
    psi = np.radians(psi_deg)
    vrel_x = v + Vw*np.cos(psi)
    vrel_y = Vw*np.sin(psi)
    vrel = np.hypot(vrel_x, vrel_y)
    phi = np.degrees(np.arctan2(vrel_y, vrel_x))
    return phi, vrel

def threshold_windspeed_yaw(G, psi_deg, dm=DM_DEFAULT):
    """Minimum TOTAL wind speed (at angle psi) above which the disc wins,
    using the yaw-dependent wheel-drag model and the average incline speed."""
    st = speed_stats(G)
    if st is None:
        return None
    _, v_bar, _ = st
    # difference of the Oenergy per metre: dm*g*(G+crr)*... - 0.5*rho*dCdA(phi)*vrel^2
    def f(Vw):
        phi, vrel = yaw_of(v_bar, Vw, psi_deg)
        dCdA = wheel_drag_area_diff(phi)          # <=0
        return dm*g*(G+crr) + 0.5*rho*dCdA*vrel**2
    lo, hi = 1e-6, 60.0
    flo, fhi = f(lo), f(hi)
    if flo <= 0.0:          # already favourable in still air
        return 0.0
    if fhi > 0.0:           # never favourable up to 60 m/s
        return None
    for _ in range(200):
        mid = 0.5*(lo+hi)
        if f(mid) > 0.0:
            lo = mid
        else:
            hi = mid
    return 0.5*(lo+hi)

# ----------------------------------------------------------------------
# 5. Reporting helpers
# ----------------------------------------------------------------------
def fmt(v):
    if v is None: return "n/a"
    return f"{v:6.2f}"

def main():
    out = {}
    out['constants'] = dict(g=g, rho=rho, crr=crr, v0=v0, c_dec=c_dec,
                            v_end_5pct=v5)
    # ---- validation ----
    out['level_power_45kph_W'] = level_power(v0)

    # ---- Task 1 table (integral method, central parameters) ----
    grades = [i/100.0 for i in range(0, 11)]
    table = []
    for G in grades:
        st = speed_stats(G)
        res = threshold_headwind(G, method="integral")
        res_avg = threshold_headwind(G, method="average")
        res_start = threshold_headwind(G, method="start")
        table.append(dict(
            grade_pct=round(G*100, 2),
            v_end=round(st[0], 3) if st else None,
            v_bar=round(st[1], 3) if st else None,
            w_star=res[1] if res[1] is not None else (0.0 if res[0]=='always_solid' else None),
            w_star_status=res[0],
            w_star_avg=(0.0 if res_avg[0]=='always_solid' else res_avg[1]),
            w_star_start=(0.0 if res_start[0]=='always_solid' else res_start[1]),
        ))
    out['table_integral'] = table

    # ---- sensitivity over dm and dCdA ----
    sens = []
    for dm in [0.2, 0.35, 0.5, 0.7, 1.0]:
        row = dict(dm=dm, vals=[])
        for G in grades:
            r = threshold_headwind(G, dm=dm, method="integral")
            row['vals'].append(0.0 if r[0]=='always_solid' else r[1])
        sens.append(row)
    out['sens_dm'] = sens
    sens2 = []
    for dCdA in [0.002, 0.003, 0.0035, 0.005, 0.008]:
        row = dict(dCdA=dCdA, vals=[])
        for G in grades:
            r = threshold_headwind(G, dCdA=dCdA, method="integral")
            row['vals'].append(0.0 if r[0]=='always_solid' else r[1])
        sens2.append(row)
    out['sens_dCdA'] = sens2

    # ---- Task 3, yaw-aware supplementary ----
    yawtab = []
    for psi in [0, 20, 30, 45, 60, 90]:
        row = dict(psi=psi, vals=[])
        for G in grades:
            w = threshold_windspeed_yaw(G, psi)
            row['vals'].append(w if w is not None else None)
        yawtab.append(row)
    out['yaw_thresholds'] = yawtab

    print(json.dumps(out, indent=1, default=str))

    # ---------- pretty print main table ----------
    print("\n=== TASK 1 : threshold headwind (integral over 100 m) ===")
    print(f"{'grade%':>6} {'v_end(m/s)':>10} {'v_bar(m/s)':>11} "
          f"{'w*(m/s)':>9} {'w*(km/h)':>10}  status")
    for row in table:
        print(f"{row['grade_pct']:6.0f} {row['v_end']:10.2f} {row['v_bar']:11.2f} "
              f"{row['w_star']:9.2f} {row['w_star']*3.6:10.2f}  {row['w_star_status']}")
    return out

if __name__ == "__main__":
    main()
