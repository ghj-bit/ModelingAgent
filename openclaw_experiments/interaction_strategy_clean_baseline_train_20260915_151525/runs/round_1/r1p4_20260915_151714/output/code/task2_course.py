# -*- coding: utf-8 -*-
"""Task 2: worked example of using the Task-1 table on a time-trial course."""
import numpy as np
import bicycle_wheel_model as m

# ------------------------------------------------------------------
# Course definition: (name, length_km, average_grade, heading_deg, surface)
# heading_deg = compass azimuth of the rider's direction of travel
# ------------------------------------------------------------------
course = [
    ("A-B", 5.0, 0.005, 90),    # gentle rise, heading east
    ("B-C", 2.5, 0.060, 0),     # steep climb, heading north
    ("C-D", 4.0, 0.010, 270),   # gentle rise, heading west
    ("D-E", 5.5, -0.015, 180),  # slight descent, heading south
]

wind_from_deg = 315.0          # wind blowing FROM the north-west
Vw = 4.5                       # m/s  total wind speed
alpha = wind_from_deg + 180.0  # direction the air moves toward

def headwind_component(heading_deg):
    d = np.radians(alpha - heading_deg)
    return Vw*np.cos(d)

# ------------------------------------------------------------------
# Table lookup: linear interpolation of w* over the 0-10 % grade range
# ------------------------------------------------------------------
grades = np.array([i/100.0 for i in range(0, 11)])
wstar = np.array([ (0.0 if m.threshold_headwind(G)[0]=='always_solid'
                    else m.threshold_headwind(G)[1]) for G in grades ])

def lookup_wstar(G):
    return float(np.interp(G, grades, wstar))

# ------------------------------------------------------------------
# Speed / time estimate with the steady power model
# (rider + frame CdA = 0.25 m^2; the rear wheel changes CdA by -dCdA and
#  mass by +dM; solve P = v[F for the given wheel] for v)
# ------------------------------------------------------------------
CdA_sys = 0.25
M_rider_bike = 80.0
P_in = 250.0                   # sustained power (W)

def steady_speed(P, G, wh, dCdA, dM):
    CdA = CdA_sys - dCdA
    mass = M_rider_bike + dM
    def resid(v):
        F = m.crr*mass*m.g + mass*m.g*G + 0.5*m.rho*CdA*(v+wh)**2
        return F*v - P
    lo, hi = 0.5, 30.0
    for _ in range(200):
        mid = 0.5*(lo+hi)
        if resid(mid) < 0: lo = mid
        else: hi = mid
    return 0.5*(lo+hi)

print(f"Wind: {Vw} m/s from {wind_from_deg:.0f} deg  ({Vw*3.6:.1f} km/h)")
print(f"Rider power: {P_in:.0f} W\n")
print(f"{'seg':>4} {'len(km)':>8} {'grade%':>7} {'headwind':>9} "
      f"{'w*(m/s)':>8} {'disc?':>6}")
tot_t_spk = tot_t_disc = tot_len = 0.0
for name, Lkm, G, hdg in course:
    wh = headwind_component(hdg)
    if G >= 0:
        ws = lookup_wstar(G)
        disc = wh > ws
    else:
        disc = True            # descending -> aero/momentum favours the disc
    v_spk  = steady_speed(P_in, G, wh, 0.0, 0.0)
    v_disc = steady_speed(P_in, G, wh, m.DCDA_DEFAULT, m.DM_DEFAULT)
    L = Lkm*1000.0
    tot_len += L
    tot_t_spk  += L/v_spk
    tot_t_disc += L/v_disc
    print(f"{name:>4} {Lkm:8.1f} {G*100:7.1f} {wh:9.2f} "
          f"{ws:8.2f} {str(disc):>6}")

def hms(t):
    h = int(t//3600); mm = int((t%3600)//60); ss = t%60
    return f"{h:d}:{mm:02d}:{ss:04.1f}"

print(f"\nAggregate decision from the table: "
      f"{'SOLID' if sum(1 for _,_,G,h in course if G<0 or headwind_component(h)>lookup_wstar(G)) > len(course)/2 else 'SPOKED'}"
      f" rear wheel")
print(f"Total distance           : {tot_len/1000:.1f} km")
print(f"Time, spoked rear wheel  : {hms(tot_t_spk)}")
print(f"Time, solid rear wheel   : {hms(tot_t_disc)}  (dCdA={m.DCDA_DEFAULT:.4f})")
print(f"Advantage of solid wheel : {tot_t_spk-tot_t_disc:+.1f} s "
      f"({(tot_t_spk-tot_t_disc)/(tot_len/1000):+.2f} s/km)")

# time gain for a larger (yawed-flow) drag-area advantage
for dCdA in [0.008, 0.012, 0.030]:
    t_spk = t_disc = 0.0
    for name, Lkm, G, hdg in course:
        wh = headwind_component(hdg); L = Lkm*1000.0
        t_spk  += L/steady_speed(P_in, G, wh, 0.0, 0.0)
        t_disc += L/steady_speed(P_in, G, wh, dCdA, m.DM_DEFAULT)
    print(f"  dCdA={dCdA:.4f} m^2 -> solid gains {t_spk-t_disc:+.1f} s "
          f"({(t_spk-t_disc)/(tot_len/1000):+.2f} s/km)")
