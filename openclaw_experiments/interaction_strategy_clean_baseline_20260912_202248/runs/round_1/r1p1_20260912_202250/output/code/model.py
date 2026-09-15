"""
Managing Sustainable Tourism in Juneau, Alaska  (MCM 2025, Problem B)
=====================================================================
Reproducible model implementation.  v2

Components
----------
1.  Parameter calibration from the two verified empirical anchors.
2.  Daily social-welfare model with resident-equity weighting; efficient
    peak load and efficient (Pigouvian) marine-passenger fee.
3.  Seasonal simulation 2024-2035 under policy scenarios
    (status quo / caps only / fees only / integrated).
4.  Revenue-reinvestment portfolio (concave water-filling allocation).
5.  Sensitivity: OAT elasticities + variance-based Sobol' indices.
6.  Adaptation: destination stress index + closed-form efficient policy rule.

Run:  python model.py
"""
import os, json, math, sys, time
import numpy as np
from scipy.optimize import minimize, brentq

HERE = os.path.dirname(os.path.abspath(__file__))
RES  = os.path.join(HERE, "..", "results")
LOG  = os.path.join(HERE, "..", "logs")
os.makedirs(RES, exist_ok=True); os.makedirs(LOG, exist_ok=True)
RNG = np.random.default_rng(20250912)

# =====================================================================
# 1.  PARAMETERS
# =====================================================================
P = dict(
    # population & baseline visitation
    N_res=30_000, C_2023=1_670_000, L_2023=200_000,
    season_days=200, peak_C_2023=20_000,
    # economic calibration (CBJ Cruise Impacts Report 2024)
    spend_pax=191.6, spend_line=23.4, spend_crew=9.6, marine_rev=22.3e6,
    retention=0.55, sales_tax=0.05, bed_tax=0.07, head_tax0=5.0,
    land_spend=250.0,
    # environment
    e_c=0.35, e_l=0.12, SCC=185.0,
    # social / infrastructure
    K0=10_000.0, kappa=19.5, K_env=15_000.0, phi=1.0e-4, iota=4.0,
    L_cap=4_000.0, lambda_r=2.2,          # resident equity weight on local disamenity
    # dynamics
    g=0.030, beta=0.96, eps_fee=0.50, eps_bedtax=0.50, fare=2_000.0,
    # policy
    f_cap_week=16_000.0, f_cap_sat=12_000.0, ships_cap=5,
)
RHO = P["retention"]
m_c = RHO*(P["spend_pax"]+P["spend_line"]+P["spend_crew"]) + P["marine_rev"]/P["C_2023"]
m_l = RHO*P["land_spend"]
P["m_c"] = m_c; P["m_l"] = m_l

# =====================================================================
# 2.  CORE
# =====================================================================
def congestion(V, K0, kappa):        return 0.5*kappa*V**2/K0
def site_damage(V, K_env, phi):     return phi*max(0.0, V-K_env)**2

def daily_welfare(C, L, p=P):
    V = C+L
    benefit = p["m_c"]*C + p["m_l"]*L
    carbon  = p["SCC"]*(p["e_c"]*C + p["e_l"]*L)
    social  = p["lambda_r"]*(congestion(V,p["K0"],p["kappa"]) +
                             site_damage(V,p["K_env"],p["phi"]))
    infra   = p["iota"]*V
    return benefit - carbon - social - infra

def emc_cruise(C, L, p=P):
    V=C+L
    return (p["SCC"]*p["e_c"] + p["lambda_r"]*(p["kappa"]*V/p["K0"] +
            2*p["phi"]*max(0.0,V-p["K_env"])) + p["iota"])
def emc_land(C, L, p=P):
    V=C+L
    return (p["SCC"]*p["e_l"] + p["lambda_r"]*(p["kappa"]*V/p["K0"] +
            2*p["phi"]*max(0.0,V-p["K_env"])) + p["iota"])

def solve_peak_day(p=P, cap_week=None, weights=(1.0,1.0)):
    wc, wl = weights
    def neg(x):
        C,L = x
        if cap_week is not None: C = min(C, cap_week)
        L = min(L, p["L_cap"]); C = max(C,0.0); L=max(L,0.0)
        return -daily_welfare(C,L,p)
    best=None
    for C0 in (8000,14000,16000,20000,24000):
        for L0 in (1000,3000,4000):
            r=minimize(neg,[C0,L0],method="Nelder-Mead",
                       options=dict(xatol=1,fatol=1e-4,maxiter=5000))
            if best is None or r.fun<best.fun: best=r
    C,L = best.x
    if cap_week is not None: C=min(C,cap_week)
    L=min(L,p["L_cap"]); C=max(C,0.0); L=max(L,0.0)
    V=C+L
    return dict(C=float(C),L=float(L),V=float(V),welfare=float(daily_welfare(C,L,p)),
                benefit=float(p["m_c"]*C+p["m_l"]*L),
                carbon=float(p["SCC"]*(p["e_c"]*C+p["e_l"]*L)),
                congestion=float(p["lambda_r"]*congestion(V,p["K0"],p["kappa"])),
                site=float(p["lambda_r"]*site_damage(V,p["K_env"],p["phi"])),
                infra=float(p["iota"]*V),
                emc_c=float(emc_cruise(C,L,p)), emc_l=float(emc_land(C,L,p)))

def efficient_load(m, e, kappa, K0, lam, SCC, iota):
    """closed-form efficient daily load where m = SCC*e + lam*kappa*V/K0 + iota."""
    numer = m - SCC*e - iota
    if numer <= 0: return 0.0
    return numer*K0/(lam*kappa)

def seasonal_profile(days, a=5.0, b=5.0):
    x=(np.arange(days)+0.5)/days
    f=x**(a-1)*(1-x)**(b-1)
    return f/f.mean()

def simulate(year, policy, base=P):
    p=dict(base); days=int(p["season_days"])
    growth=(1+p["g"])**(year-2023)
    C_target=p["C_2023"]*growth; L_target=p["L_2023"]*growth
    fee=policy.get("fee",p["head_tax0"]); bed=policy.get("bed_tax",p["bed_tax"])
    d_fee=1-p["eps_fee"]*max(0.0,fee-p["head_tax0"])/p["fare"]
    d_bed=1-p["eps_bedtax"]*max(0.0,bed-p["bed_tax"])
    C_target*=max(0.3,d_fee); L_target*=max(0.3,d_bed)
    disp=policy.get("dispersal",0.0)
    L_target*=(1+policy.get("disp_gain",0.15)*disp)
    p["e_c"]*= (1-policy.get("carbon_cut",0.0))
    p["K0"] *= (1+policy.get("cap_expand",0.0))
    p["kappa"]*=(1-policy.get("social_cut",0.0))
    Cs=seasonal_profile(days,5.0,5.0)*(C_target/days)
    Ls=seasonal_profile(days,3.5,3.5)*(L_target/days)
    if policy.get("cap_week") is not None: Cs=np.minimum(Cs,policy["cap_week"])
    Ls=np.minimum(Ls,p["L_cap"])
    Vs=Cs+Ls
    benef=p["m_c"]*Cs.sum()+p["m_l"]*Ls.sum()
    carbon=p["SCC"]*(p["e_c"]*Cs.sum()+p["e_l"]*Ls.sum())
    carbon_t=p["e_c"]*Cs.sum()+p["e_l"]*Ls.sum()
    cong=p["lambda_r"]*sum(congestion(v,p["K0"],p["kappa"]) for v in Vs)
    site=p["lambda_r"]*sum(site_damage(v,p["K_env"],p["phi"]) for v in Vs)
    infra=p["iota"]*Vs.sum()
    welfare=benef-carbon-cong-site-infra
    gross=p["spend_pax"]*Cs.sum()+p["land_spend"]*Ls.sum()
    fee_rev=fee*Cs.sum(); bed_rev=bed*p["land_spend"]*Ls.sum()*0.6
    sales=p["sales_tax"]*gross; total_rev=fee_rev+bed_rev+sales+p["marine_rev"]
    social=cong+site+infra
    rwi=float(np.clip(1-social/max(benef,1.0),0,1))
    return dict(year=year,C=float(Cs.sum()),L=float(Ls.sum()),V=float(Vs.sum()),
                peak_C=float(Cs.max()),peak_V=float(Vs.max()),benefit=float(benef),
                carbon_cost=float(carbon),carbon_t=float(carbon_t),congestion=float(cong),
                site=float(site),infra=float(infra),welfare=float(welfare),
                gross_spend=float(gross),fee_rev=float(fee_rev),bed_rev=float(bed_rev),
                sales_rev=float(sales),total_rev=float(total_rev),rwi=rwi)

# =====================================================================
# 3.  SCENARIOS
# =====================================================================
SCEN = {
 "S0_status_quo": dict(),
 "S1_caps_only":  dict(cap_week=P["f_cap_week"]),
 # fees only: revenue recycled to shore-power/abatement, but NO volume cap and
 # NO capacity/dispersal investment -> volume keeps growing.
 "S2_fees_only":  dict(fee=137.0, bed_tax=0.12, carbon_cut=0.15),
 "S3_integrated": dict(cap_week=P["f_cap_week"], fee=137.0, bed_tax=0.12,
                       dispersal=1.0, carbon_cut=0.15, cap_expand=0.12, social_cut=0.20),
}
def run_scenarios(years=(2024,2026,2028,2030,2033,2035)):
    table={n:[simulate(y,pol) for y in years] for n,pol in SCEN.items()}
    disc={n: sum(simulate(y,pol)["welfare"]*P["beta"]**(y-2026) for y in range(2026,2036))
          for n,pol in SCEN.items()}
    return table,disc

# =====================================================================
# 4.  REINVESTMENT PORTFOLIO
# =====================================================================
PORTFOLIO={
 "Infrastructure (water/wastewater/roads/dock)":0.25,
 "Transit & shuttle (congestion, dispersal)":0.22,
 "Workforce / affordable housing fund":0.20,
 "Environmental restoration & monitoring":0.18,
 "Carbon abatement / shore power":0.10,
 "Marketing of less-visited attractions":0.05,
}
def allocate(R,w):
    a=np.array(list(w.values())); a=a/a.sum()
    x=R*a**2/(a**2).sum()
    return {k:float(v) for k,v in zip(w.keys(),x)}

# =====================================================================
# 5.  SENSITIVITY
# =====================================================================
def oat_sensitivity(base_out, keys, pct=0.20):
    res={}; base_C=base_out["C"]; base_W=base_out["welfare"]
    for k in keys:
        row={}
        for sgn in (+1,-1):
            p=dict(P); p[k]=P[k]*(1+sgn*pct)
            p["m_c"]=RHO*(p["spend_pax"]+p["spend_line"]+p["spend_crew"])+p["marine_rev"]/p["C_2023"]
            p["m_l"]=RHO*p["land_spend"]
            o=solve_peak_day(p)
            row["hi" if sgn>0 else "lo"]=(o["C"],o["welfare"])
        eC=((row["hi"][0]-row["lo"][0])/(2*base_C))/pct if base_C else 0
        eW=((row["hi"][1]-row["lo"][1])/(2*abs(base_W)))/pct if base_W else 0
        res[k]=dict(elasticity_C=float(eC),elasticity_W=float(eW),
                    C_range=[row["lo"][0],row["hi"][0]],
                    W_range=[row["lo"][1],row["hi"][1]])
    return res

SOB_KEYS=["spend_pax","land_spend","SCC","e_c","kappa","phi","g","eps_fee"]
def _model_output(theta, base=P):
    p=dict(base)
    for k,v in zip(SOB_KEYS,theta): p[k]=v
    p["m_c"]=RHO*(p["spend_pax"]+p["spend_line"]+p["spend_crew"])+p["marine_rev"]/p["C_2023"]
    p["m_l"]=RHO*p["land_spend"]
    pol=dict(cap_week=p["f_cap_week"],fee=137.0,bed_tax=0.12,dispersal=1.0,
             carbon_cut=0.15,cap_expand=0.12,social_cut=0.20)
    return sum(simulate(y,pol,base=p)["welfare"]*p["beta"]**(y-2026)
               for y in range(2026,2036))/1e9
def sobol_analysis(n=1024,seed=7):
    rng=np.random.default_rng(seed)
    lo=np.array([120.,150., 51.,0.20,10.,0.2e-4,0.010,0.03])
    hi=np.array([280.,350.,300.,0.55,30.,2.0e-4,0.060,0.25])
    D=len(lo)
    A=lo+(hi-lo)*rng.random((n,D)); B=lo+(hi-lo)*rng.random((n,D))
    fA=np.array([_model_output(a) for a in A]); fB=np.array([_model_output(b) for b in B])
    varY=np.var(np.concatenate([fA,fB]))
    S1=np.zeros(D); ST=np.zeros(D)
    for i in range(D):
        AB=A.copy(); AB[:,i]=B[:,i]
        fAB=np.array([_model_output(r) for r in AB])
        S1[i]=np.mean(fB*(fAB-fA))/varY
        ST[i]=np.mean((fA-fAB)**2)/(2*varY)
    return dict(names=SOB_KEYS,S1=S1.tolist(),ST=ST.tolist(),varY=float(varY))

# =====================================================================
# 6.  ADAPTATION
# =====================================================================
DESTINATIONS=[
 # name, income/spend proxy m_d ($/visitor), ghg intensity frac of Juneau,
 # visitors-per-capacity cap_ratio, fee elasticity, dispersion, heritage fragility
 dict(name="Juneau, AK (cruise)",        m=137, ghg=0.95, cap_ratio=2.0, eps=0.10, disp=0.75, frag=1.00),
 dict(name="Venice, IT (overnight+day)", m=160, ghg=0.35, cap_ratio=2.4, eps=0.35, disp=0.40, frag=1.50),
 dict(name="Barcelona, ES",              m=150, ghg=0.30, cap_ratio=1.6, eps=0.40, disp=0.60, frag=1.10),
 dict(name="Santorini, GR (cruise)",     m=120, ghg=0.90, cap_ratio=3.2, eps=0.15, disp=0.20, frag=1.20),
 dict(name="Machu Picchu, PE",           m= 90, ghg=0.20, cap_ratio=2.8, eps=0.30, disp=0.25, frag=1.30),
 dict(name="Banff, CA",                  m=140, ghg=0.25, cap_ratio=1.4, eps=0.45, disp=0.65, frag=1.00),
]
def adaptation(d):
    e_c=d["ghg"]*P["e_c"]; lam=P["lambda_r"]; kappa=P["kappa"]*d["frag"]; K0=P["K0"]; iota=P["iota"]
    # current peak load (in units of K0) == cap_ratio
    V_peak_units=d["cap_ratio"]
    v_eff=min(V_peak_units,(d["m"]-P["SCC"]*e_c-iota)/(lam*kappa))
    reduction=100*max(0.0,1-v_eff/max(V_peak_units,1e-9))
    stress=100*(0.35*min(d["cap_ratio"]/3.0,1.0)+0.25*(1-d["eps"])+
                0.20*d["ghg"]+0.20*(1-d["disp"]))
    fee_fit=100*(1-d["eps"]); cap_fit=100*(d["cap_ratio"]/3.0); disp_fit=100*d["disp"]
    rec=("Cap-first + fee" if cap_fit>=fee_fit and disp_fit<50
         else ("Fee-first" if fee_fit>disp_fit else "Dispersal-first + fee"))
    return dict(name=d["name"],stress=round(stress,1),eff_fee=round(d["m"],0),
                load_reduction_pct=round(reduction,1),
                fee_fit=round(fee_fit,1),cap_fit=round(cap_fit,1),disp_fit=round(disp_fit,1),
                rec=rec)

# =====================================================================
def main():
    t0=time.time()
    print("="*74); print("MANAGING SUSTAINABLE TOURISM - JUNEAU, ALASKA (MCM 2025 B)"); print("="*74)
    print(f"unit values: m_c=${m_c:.2f}/cruise-pax  m_l=${m_l:.2f}/land-visitor  "
          f"m_c-m_l gap=${m_c-m_l:+.2f}")

    # 1. validation against reported 2023 values
    b23=simulate(2023, dict())
    print("\n[1] Baseline 2023 validation (model vs reported):")
    print(f"    cruise passengers        model={b23['C']:>12,.0f}   reported=1,670,000")
    print(f"    peak-day cruise pax      model={b23['peak_C']:>12,.0f}   reported<=20,000")
    print(f"    cruise-linked spending   model=${(P['spend_pax']+P['spend_line']+P['spend_crew'])*1.67e6/1e6:>9,.0f}M  reported=$375M")
    print(f"    marine/port revenue      model=${P['marine_rev']/1e6:>9,.1f}M  reported=$22.3M")
    print(f"    carbon footprint         model={b23['carbon_t']/1e3:>9,.0f} ktCO2e (order-of-magnitude check)")

    # 2. optimisation
    peak = solve_peak_day()                                  # equity-weighted, capped L only
    peak_unc = solve_peak_day(dict(P), )                     # same (L capped)
    p1=dict(P); p1["lambda_r"]=1.0
    socio = solve_peak_day(p1)                               # pure monetised (lambda_r=1)
    eff_fee = peak["emc_c"]
    P["eff_fee"]=eff_fee
    print("\n[2] welfare-optimal peak day (equity-weighted, lambda_r=%.1f):"%P["lambda_r"])
    print(f"    C*={peak['C']:.0f}  L*={peak['L']:.0f}  V*={peak['V']:.0f}   welfare/day=${peak['welfare']:,.0f}")
    print(f"    efficient marine fee f* = ${eff_fee:.2f}/pax ; EMC_land=${peak['emc_l']:.2f}")
    print(f"    pure-monetised optimum V (lambda_r=1): {socio['V']:.0f}   "
          f"(official cap = {P['f_cap_week']:.0f})")

    # scenario dict update with computed efficient fee
    SCEN["S2_fees_only"]["fee"]=eff_fee
    SCEN["S3_integrated"]["fee"]=eff_fee
    table,disc=run_scenarios()
    print("\n[3] Scenario simulation:")
    hdr=f"    {'scenario':<16}{'yr':>5}{'C(M)':>8}{'L(k)':>7}{'peakV':>8}{'CO2(kt)':>9}{'wel$M':>8}{'RWI':>6}{'rev$M':>8}"
    print(hdr)
    for n,rows in table.items():
        for r in rows:
            if r['year'] in (2026,2030,2035):
                print(f"    {n:<16}{r['year']:>5}{r['C']/1e6:>8.2f}{r['L']/1e3:>7.0f}"
                      f"{r['peak_V']:>8,.0f}{r['carbon_t']/1e3:>9.0f}{r['welfare']/1e6:>8.1f}"
                      f"{r['rwi']:>6.2f}{r['total_rev']/1e6:>8.1f}")
    print("    discounted 2026-35 welfare ($M):",{k:round(v/1e6,1) for k,v in disc.items()})

    # 4. reinvestment
    scen={y:simulate(y,SCEN["S3_integrated"]) for y in range(2026,2036)}
    new_rev=float(np.mean([scen[y]["fee_rev"]+scen[y]["bed_rev"]-P["head_tax0"]*scen[y]["C"] for y in scen]))
    alloc=allocate(new_rev,PORTFOLIO)
    print(f"\n[4] mean annual NEW public revenue = ${new_rev/1e6:.1f}M")
    for k,v in alloc.items(): print(f"      {k:<46} ${v/1e6:6.2f}M")

    # 5. sensitivity
    keys=["spend_pax","land_spend","SCC","e_c","kappa","phi","g","eps_fee"]
    oat=oat_sensitivity(peak,keys)
    print("\n[5] OAT elasticities (peak C*, net welfare):")
    for k,v in oat.items():
        print(f"      {k:<12} eC={v['elasticity_C']:+.3f}   eW={v['elasticity_W']:+.3f}")
    sob=sobol_analysis(n=1024)
    print("    Sobol S1 / ST:")
    for nm,s1,st in zip(sob["names"],sob["S1"],sob["ST"]):
        print(f"      {nm:<12} S1={s1:+.3f}  ST={st:+.3f}")

    # 6. adaptation
    adapt=[adaptation(d) for d in DESTINATIONS]
    print("\n[6] Destination adaptation:")
    for a in adapt:
        print(f"      {a['name']:<28} stress={a['stress']:5.1f} eff_fee=${a['eff_fee']:5.0f} "
              f"loadcut={a['load_reduction_pct']:5.1f}%  {a['rec']}")

    out=dict(params={k:(round(v,6) if isinstance(v,float) else v) for k,v in P.items()},
             unit_values=dict(m_c=m_c,m_l=m_l),
             peak_optimal=peak, peak_monetised=socio, efficient_fee=eff_fee,
             scenarios=table, discounted_welfare_10y=disc,
             new_revenue=new_rev, portfolio_allocation=alloc,
             oat=oat, sobol=sob, adaptation=adapt, runtime_s=round(time.time()-t0,2))
    with open(os.path.join(RES,"results.json"),"w",encoding="utf-8") as f:
        json.dump(out,f,indent=2,default=float)
    print(f"\nSaved -> results/results.json  ({out['runtime_s']}s)")

if __name__=="__main__":
    main()
