"""Secondary analysis for the Forest Service report (text tables + ASCII maps)."""
import numpy as np, json, itertools
import forest_fire as ff

t_grid = np.arange(0, 30.0001, 0.25)
model = ff.free_fire(20.0, 0.6, t_grid, 12.0)
C = ff.candidate_travel(model)
REC = [ff.CAMP_COORDS.index(p) for p in [(30, 30), (30, 50), (45, 30), (45, 50)]]

out = {}

# 1. free-fire timeline (mean over ignition points)
area = model['area']
sel = [0.5, 1, 2, 3, 4, 6, 8, 12, 24]
mean_area = area.mean(axis=0)
idx = [int(np.argmin(np.abs(t_grid - t))) for t in sel]
out['timeline'] = {str(t): float(mean_area[i]) for t, i in zip(sel, idx)}
print("Free-fire mean area (km^2) vs time (h):")
for t, i in zip(sel, idx):
    print("   t=%4.1f h  A=%7.2f km2   (95th pct %7.1f)" % (t, mean_area[i], np.percentile(area[:, i], 95)))

# 2. recommended-config statistics
v, pc, af = ff.evaluate(REC, C, model)
esc = model['escape']
dmg = pc * af + (1 - pc) * esc
out['rec'] = dict(E=float(v), mean_p=float(pc.mean()),
                  p_contain_gt50=float((pc > 0.5).mean()),
                  mean_afree=float(af.mean()),
                  mean_contained_size=float(af[pc > 0.5].mean()),
                  p90_contained=float(np.percentile(af[pc > 0.5], 90)),
                  mean_escape=float(esc.mean()),
                  frac_escape=float((pc < 0.5).mean()))
print("\nRecommended config stats:")
print("   E[burn]=%.1f  mean p_contain=%.3f  P(contain>0.5)=%.3f" % (v, pc.mean(), (pc > 0.5).mean()))
print("   mean size of contained fires=%.2f km2  (90th pct %.2f)" % (af[pc > 0.5].mean(), np.percentile(af[pc > 0.5], 90)))
print("   mean size of escaped fires=%.1f km2" % esc.mean())

# 3. ASCII containment-probability map (20x20 over ignition lattice)
ii = np.arange(2, ff.N, 4); jj = np.arange(2, ff.N, 4)
P = pc.reshape(len(ii), len(jj))
chars = " .:-=+*#%@"
print("\nContainment-probability map (rows = y south->north top->bottom, cols = x west->east):")
lines = []
for a in range(len(ii)):
    row = "".join(chars[min(9, int(P[a, b] * 10))] for b in range(len(jj)))
    lines.append(row); print("   " + row)
out['pc_map'] = lines

# 4. ASCII expected-damage map (per ignition, km^2)
DD = dmg.reshape(len(ii), len(jj))
print("\nExpected burned-area map (km^2 per fire, chars scale 0..max):")
dmax = DD.max()
dlines = []
for a in range(len(ii)):
    row = "".join(chars[min(9, int(DD[a, b] / dmax * 10))] for b in range(len(jj)))
    dlines.append(row); print("   " + row)
out['dmg_map'] = dlines; out['dmg_max'] = float(dmax)

# 5. flatness around optimum: shift the whole cluster
print("\nE[burn] for shifted cluster (dx,dy in km):")
shift_tab = {}
for dx, dy in [(0, 0), (5, 0), (10, 0), (-5, 0), (-10, 0), (0, 10), (0, -10), (5, 5), (-5, -5)]:
    cfg = []
    for (cx, cy) in [(30, 30), (30, 50), (45, 30), (45, 50)]:
        nx, ny = min(80, max(0, cx + dx)), min(80, max(0, cy + dy))
        cfg.append(ff.CAMP_COORDS.index((nx, ny)))
    vv, pcc, _ = ff.evaluate(cfg, C, model)
    shift_tab["(%d,%d)" % (dx, dy)] = float(vv)
    print("   d=(%3d,%3d)  E=%.1f" % (dx, dy, vv))
out['shift_tab'] = shift_tab

# 6. escalation thresholds: free-fire size at attack time (mean & p95)
print("\nEscalation thresholds (free-fire size vs elapsed time):")
thr = {}
for t, i in zip([0.5, 1, 1.5, 2, 3, 4, 6],
                [int(np.argmin(np.abs(t_grid - t))) for t in [0.5, 1, 1.5, 2, 3, 4, 6]]):
    thr[str(t)] = dict(mean=float(mean_area[i]), p95=float(np.percentile(area[:, i], 95)))
    print("   t=%4.1f h  mean=%7.2f  p95=%7.2f km2" % (t, mean_area[i], np.percentile(area[:, i], 95)))
out['thresholds'] = thr

with open("results/analysis.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2)
print("\nSaved results/analysis.json")
