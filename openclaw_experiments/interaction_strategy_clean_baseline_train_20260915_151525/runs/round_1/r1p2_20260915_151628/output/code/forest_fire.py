"""
Forest Service (HiMCM 2001) -- resource-allocation model.

Model chain
-----------
1. Free-fire spread: anisotropic Huygens/elliptical arrival-time field on a 1 km
   lattice (directed Finsler graph solved with Dijkstra). Head ROS follows the
   10%-of-wind rule of thumb (Cruz & Alexander 2019). The 5 km firebreak grid is
   represented as a partial barrier (firebreak retention factor GAMMA_FB).
2. Response: equipment convoy travels the 5 km firebreak road network
   (Manhattan distance), crews can be lifted by the single helicopter.
3. Suppression: initial-attack containment probability as a logistic function of
   the arrival times of the responding units.
4. Damage: contained fires burn the free-fire area at first attack; escaped
   fires burn the free-fire area until mutual aid arrives (T_ESC).
5. Optimisation: place 4 base camps on firebreak intersections to minimise the
   expected area burned.
6. Forecast: expected burned area per fire / per season + escalation rule.

Everything here is text/numeric; no figures are produced.
"""
import numpy as np, math, json, time, itertools, os
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra

RNG = np.random.default_rng(20010915)

# ----------------------------------------------------------------------------
# Geometry
# ----------------------------------------------------------------------------
L = 80.0          # km, side of the square wilderness
DX = 1.0          # km, lattice spacing for the fire-spread calculation
N = int(L / DX)   # 80 nodes per axis
xs = np.arange(N) + 0.5
ys = np.arange(N) + 0.5
XX, YY = np.meshgrid(xs, ys, indexing='ij')     # XX[i,j] = x of node (i,j)
FLAT = np.arange(N * N).reshape(N, N)
FIREBREAK = 5.0   # km, firebreak / road spacing


def ncross(a, b):
    """Number of multiples of FIREBREAK strictly between coordinates a and b."""
    lo, hi = (a, b) if a < b else (b, a)
    kmin = int(lo // FIREBREAK) + 1
    kmax = int(math.ceil(hi / FIREBREAK)) - 1
    return max(0, kmax - kmin + 1)


# ----------------------------------------------------------------------------
# Fire-spread graph
# ----------------------------------------------------------------------------
DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]


def build_graph(U_open, gamma_fb, hbr=8.0):
    """Directed graph of fire arrival times. head ROS R_h = 0.10*U_open."""
    R_h = 0.10 * U_open
    R_b = R_h / hbr
    R_c = 0.5 * (R_h + R_b)
    ecc = (R_h - R_b) / (R_h + R_b)
    base = R_c * (1.0 - ecc ** 2)

    rows, cols, data = [], [], []
    for i in range(N):
        for j in range(N):
            for di, dj in DIRS:
                i2, j2 = i + di, j + dj
                if not (0 <= i2 < N and 0 <= j2 < N):
                    continue
                dist = math.hypot(di, dj) * DX
                th = math.atan2(dj, di)               # wind blows toward +x (east)
                ros = base / (1.0 - ecc * math.cos(th))
                nfb = ncross(xs[i], xs[i2]) + ncross(ys[j], ys[j2])
                w = dist / ros * (1.0 / gamma_fb) ** nfb
                rows.append(FLAT[i, j]); cols.append(FLAT[i2, j2]); data.append(w)
    return csr_matrix((data, (rows, cols)), shape=(N * N, N * N)), dict(
        R_h=R_h, R_b=R_b, R_f=base, ecc=ecc)


def ignition_nodes(step=4):
    ii = np.arange(2, N, step)          # 2,6,...,78  -> 20 per axis
    jj = np.arange(2, N, step)
    return np.array([FLAT[i, j] for i in ii for j in jj]), ii, jj


def free_fire(U_open, gamma_fb, t_grid, t_esc):
    """Return area-vs-time for each ignition, escape area, and reach-east time."""
    M, par = build_graph(U_open, gamma_fb)
    ign, ii, jj = ignition_nodes()
    D = dijkstra(M, directed=True, indices=ign)          # (400, N*N)
    T = D.reshape(-1, N, N)
    area = np.zeros((len(ign), len(t_grid)))
    for k, t in enumerate(t_grid):
        area[:, k] = (T <= t).sum(axis=(1, 2)) * DX * DX
    k_esc = int(np.argmin(np.abs(t_grid - t_esc)))
    escape = area[:, k_esc].copy()
    t_east = T[:, N - 1, :].min(axis=1)
    XZ = np.array([xs[i] for i, _ in
                   [(i, j) for i in ii for j in jj]])
    YZ = np.array([ys[j] for _, j in
                   [(i, j) for i in ii for j in jj]])
    return dict(area=area, escape=escape, t_east=t_east, XZ=XZ, YZ=YZ,
                par=par, T=T, t_grid=t_grid)


# ----------------------------------------------------------------------------
# Response + suppression
# ----------------------------------------------------------------------------
V_EQUIP = 30.0        # km/h effective convoy speed on firebreaks
T_CONST = 0.40        # h: off-road spotting/deploy (1.5 km @ 10 km/h) + setup
TAU = 1.5             # h, decay of a unit's containment contribution
ALPHA0, ALPHA1 = -2.1, 2.76

CAMP_COORDS = [(cx, cy) for cx in range(0, 81, 5) for cy in range(0, 81, 5)]  # 289 nodes


def candidate_travel(model, v_equip=V_EQUIP):
    """(289, n_ign) matrix of equipment arrival times (h) camp -> ignition."""
    XZ, YZ = model['XZ'], model['YZ']
    C = np.empty((len(CAMP_COORDS), len(XZ)))
    for c, (cx, cy) in enumerate(CAMP_COORDS):
        C[c] = (np.abs(cx - XZ) + np.abs(cy - YZ)) / v_equip + T_CONST
    return C


def evaluate(camp_idx, C, model, tau=TAU, a0=ALPHA0, a1=ALPHA1):
    """Expected burned area (km^2) for a camp configuration."""
    tt = C[list(camp_idx)]                       # (k, n_ign)
    a_min = tt.min(axis=0)
    s = np.exp(-tt / tau).sum(axis=0)
    pc = 1.0 / (1.0 + np.exp(-(a0 + a1 * s)))
    nT = model['area'].shape[1]
    idx = np.clip(np.round(a_min / (model['t_grid'][1] - model['t_grid'][0])).astype(int),
                  0, nT - 1)
    afree = model['area'][np.arange(len(a_min)), idx]
    dmg = pc * afree + (1.0 - pc) * model['escape']
    return float(dmg.mean()), pc, afree


# ----------------------------------------------------------------------------
# Optimisation
# ----------------------------------------------------------------------------
def sa_optimise(C, model, k=4, iters=60000, restarts=8, seed=0):
    rng = np.random.default_rng(seed)
    n = len(CAMP_COORDS)
    best_global, best_val = None, np.inf
    for r in range(restarts):
        cur = list(rng.choice(n, size=k, replace=False))
        cur_val, _, _ = evaluate(cur, C, model)
        T0 = 5.0
        for it in range(iters):
            T = T0 * (1 - it / iters) + 1e-3
            new = cur.copy()
            pos = rng.integers(k)
            cand = rng.integers(n)
            while cand in new:
                cand = rng.integers(n)
            new[pos] = cand
            val, _, _ = evaluate(new, C, model)
            if val < cur_val or rng.random() < math.exp(-(val - cur_val) / T):
                cur, cur_val = new, val
            if cur_val < best_val:
                best_val, best_global = cur_val, cur.copy()
    return best_global, best_val


def brute_force_symmetric(C, model):
    """Optimal config restricted to north-south symmetry (two mirror pairs)."""
    half = [c for c in range(len(CAMP_COORDS)) if CAMP_COORDS[c][1] <= 40]
    idx_of = {c: i for i, c in enumerate(half)}
    mirror = {}
    for c in half:
        cx, cy = CAMP_COORDS[c]
        m = CAMP_COORDS.index((cx, 80 - cy))
        mirror[c] = m
    best, bv = None, np.inf
    for c1, c2 in itertools.combinations(half, 2):
        if CAMP_COORDS[c1][1] == 40 or CAMP_COORDS[c2][1] == 40:
            continue  # keeps each camp distinct after mirroring
        cfg = [c1, mirror[c1], c2, mirror[c2]]
        if len(set(cfg)) < 4:
            continue
        val, _, _ = evaluate(cfg, C, model)
        if val < bv:
            bv, best = val, cfg
    return best, bv


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def main():
    t0 = time.time()
    t_grid = np.arange(0, 30.0001, 0.25)
    T_ESC = 12.0
    print("Building free-fire fields (U_open=20, gamma_fb=0.6) ...")
    model = free_fire(20.0, 0.6, t_grid, T_ESC)
    C = candidate_travel(model)
    print("  free-fire build %.1fs" % (time.time() - t0),
          "| corridor head ROS %.2f km/h (R_f=%.2f)" % (model['par']['R_h'], model['par']['R_f']))

    # reference configurations
    def idx(cx, cy):
        return CAMP_COORDS.index((cx, cy))
    refs = {
        "corners (0/80)": [idx(0, 0), idx(0, 80), idx(80, 0), idx(80, 80)],
        "even 2x2": [idx(20, 20), idx(20, 60), idx(60, 20), idx(60, 60)],
        "centre cluster": [idx(35, 35), idx(45, 35), idx(35, 45), idx(45, 45)],
        "west line": [idx(20, 10), idx(20, 40), idx(20, 70), idx(50, 40)],
    }
    report = {"refs": {}, "seeds": {}}
    for name, cfg in refs.items():
        v, pc, af = evaluate(cfg, C, model)
        report["refs"][name] = dict(cfg=[[CAMP_COORDS[c][0], CAMP_COORDS[c][1]] for c in cfg],
                                    E_damage=v, mean_pcontain=float(pc.mean()),
                                    mean_contained_size=float(af.mean()))
        print("REF %-16s E[burn]=%8.1f km2  p_contain=%.3f  contained size=%.2f"
              % (name, v, pc.mean(), af.mean()))

    print("SA optimisation (8 restarts x 60k iters) ...")
    best, bv = sa_optimise(C, model, seed=1)
    coord = [CAMP_COORDS[c] for c in best]
    print("  SA best:", coord, "E[burn]=%.1f km2" % bv)
    report["sa"] = dict(cfg=[list(c) for c in coord], E_damage=bv)

    print("Brute-force symmetric optimum ...")
    sb, sbv = brute_force_symmetric(C, model)
    scoord = [CAMP_COORDS[c] for c in sb]
    print("  sym best:", scoord, "E[burn]=%.1f km2" % sbv)
    report["sym"] = dict(cfg=[list(c) for c in scoord], E_damage=sbv)

    # choose the recommended configuration (symmetric if essentially as good)
    if sbv <= bv * 1.002:
        rec, recv, tag = sb, sbv, "symmetric"
    else:
        rec, recv, tag = best, bv, "SA"
    report["recommended"] = dict(cfg=[list(CAMP_COORDS[c]) for c in rec],
                                 E_damage=recv, kind=tag)
    print("RECOMMENDED (%s): %s  E[burn]=%.1f km2" %
          (tag, [CAMP_COORDS[c] for c in rec], recv))

    # unit-count study using greedy nested placement on the recommended config family
    print("\nUnit-count study (best nested placement) ...")
    def best_k(k, iters=40000, restarts=6):
        b, bvv = sa_optimise(C, model, k=k, iters=iters, restarts=restarts, seed=7)
        return b, bvv
    unit_tab = {}
    for k in range(1, 9):
        b, bvv = best_k(k)
        v0 = evaluate([], C, model) if k == 0 else None
        unit_tab[k] = dict(cfg=[list(CAMP_COORDS[c]) for c in b], E_damage=bvv)
        print("  k=%d  E[burn]=%8.1f km2  cfg=%s" % (k, bvv, [CAMP_COORDS[c] for c in b]))
    report["unit_tab"] = unit_tab

    # no-suppression baseline (all fires escape) and perfect baseline
    report["baseline_no_suppression"] = float(model['escape'].mean())
    print("\nNo-suppression mean escape burn = %.1f km2" % model['escape'].mean())

    # sensitivity
    print("\nSensitivity analysis ...")
    sens = {}
    def run(U, g):
        m = free_fire(U, g, t_grid, T_ESC)
        Cc = candidate_travel(m)
        vbest, _ = sa_optimise(Cc, m, k=4, iters=25000, restarts=4, seed=3)
        vv, pc, af = evaluate(vbest, Cc, m)
        return vbest, vv, pc.mean(), m
    for U in [10, 15, 20, 25, 30]:
        cb, vv, pc, m = run(float(U), 0.6)
        sens[f"U={U}"] = dict(E_damage=vv, p_contain=pc, cfg=[list(CAMP_COORDS[c]) for c in cb],
                              R_h=m['par']['R_h'], escape=float(m['escape'].mean()))
        print("  U=%2d km/h -> R_h=%.2f, E[burn]=%8.1f, p_c=%.3f, cfg=%s"
              % (U, m['par']['R_h'], vv, pc, [CAMP_COORDS[c] for c in cb]))
    for g in [0.4, 0.8, 1.0]:
        cb, vv, pc, m = run(20.0, g)
        sens[f"gamma_fb={g}"] = dict(E_damage=vv, p_contain=pc,
                                     cfg=[list(CAMP_COORDS[c]) for c in cb])
        print("  gamma_fb=%.1f -> E[burn]=%8.1f, p_c=%.3f" % (g, vv, pc))
    # travel speed
    for v in [20.0, 40.0]:
        Cc = candidate_travel(model, v_equip=v)
        vv, pc, af = evaluate(rec, Cc, model)
        sens[f"v_equip={v}"] = dict(E_damage=vv, p_contain=float(pc.mean()))
        print("  v_equip=%.0f -> E[burn]=%8.1f, p_c=%.3f" % (v, vv, pc.mean()))
    # tau / alpha
    for tau in [1.0, 2.0, 3.0]:
        vv, pc, af = evaluate(rec, C, model, tau=tau)
        sens[f"tau={tau}"] = dict(E_damage=vv, p_contain=float(pc.mean()))
        print("  tau=%.1f -> E[burn]=%8.1f, p_c=%.3f" % (tau, vv, pc.mean()))
    report["sensitivity"] = sens

    # seasonal damage-forecast table for the recommended config
    print("\nSeasonal forecast (recommended config) ...")
    vrec, pcrec, afrec = evaluate(rec, C, model)
    fc = dict(E_damage_per_fire=vrec, mean_pcontain=float(pcrec.mean()),
              mean_size_contained=float(afrec.mean()),
              p95_escape=float(model['escape'].max()),
              area_km2=L * L)
    for nfires in [5, 10, 20]:
        fc[f"season_{nfires}"] = nfires * vrec
    report["forecast"] = fc

    report["meta"] = dict(U_open=20.0, gamma_fb=0.6, v_equip=V_EQUIP,
                          T_const=T_CONST, tau=TAU, alpha=[ALPHA0, ALPHA1],
                          T_ESC=T_ESC, n_ignition=len(model['XZ']),
                          R_h=model['par']['R_h'], R_f=model['par']['R_f'],
                          runtime_s=time.time() - t0)

    os.makedirs("results", exist_ok=True)
    with open("results/model_output.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print("\nSaved results/model_output.json  (%.1fs)" % (time.time() - t0))


if __name__ == "__main__":
    main()
