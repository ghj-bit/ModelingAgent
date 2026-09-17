# -*- coding: utf-8 -*-
"""Print sensitivity + yaw-aware tables for the bicycle-wheel model."""
import numpy as np
import bicycle_wheel_model as m

grades = [i for i in range(0, 11)]

# ---- sensitivity over dm ----
print("=== Sensitivity: threshold headwind w* (m/s) vs dM (kg)  [dCdA=0.0035] ===")
hdr = "grade%  " + "".join(f"{d:>7.2f}" for d in [0.2, 0.35, 0.5, 0.7, 1.0])
print(hdr)
for G in grades:
    row = f"{G:6d}  "
    for dm in [0.2, 0.35, 0.5, 0.7, 1.0]:
        r = m.threshold_headwind(G/100.0, dm=dm, method="integral")
        val = 0.0 if r[0] == 'always_solid' else r[1]
        row += f"{val:7.2f}"
    print(row)

print("\n=== Sensitivity: threshold headwind w* (m/s) vs dCdA (m^2)  [dM=0.5] ===")
print("grade%  " + "".join(f"{d:>7.4f}" for d in [0.002, 0.003, 0.0035, 0.005, 0.008]))
for G in grades:
    row = f"{G:6d}  "
    for dCdA in [0.002, 0.003, 0.0035, 0.005, 0.008]:
        r = m.threshold_headwind(G/100.0, dCdA=dCdA, method="integral")
        val = 0.0 if r[0] == 'always_solid' else r[1]
        row += f"{val:7.2f}"
    print(row)

print("\n=== Yaw-aware model: min total wind speed (m/s) for disc to win ===")
print("        (wind direction psi = angle from direction of travel; 0=headwind)")
print("grade%  " + "".join(f"{p:>7d}" for p in [0, 20, 30, 45, 60, 90]))
for G in grades:
    row = f"{G:6d}  "
    for psi in [0, 20, 30, 45, 60, 90]:
        w = m.threshold_windspeed_yaw(G/100.0, psi)
        row += ("   n/a " if w is None else f"{w:7.2f}")
    print(row)

print("\nNote: 'solid always better' entries are shown as 0.00; 'n/a' = disc never wins "
      "up to 60 m/s.")
