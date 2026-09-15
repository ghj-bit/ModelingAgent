"""
Adolescent Pregnancy (HiMCM 2001 Problem A) - full analysis pipeline.
Reproducible: reads ../data/*.csv, prints a full results digest, and writes
machine-readable + markdown summaries into ../results/ and ../logs/.

Run:  python analysis.py
"""
import json
import os
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
RES = os.path.join(ROOT, "results")
LOG = os.path.join(ROOT, "logs")
os.makedirs(RES, exist_ok=True)
os.makedirs(LOG, exist_ok=True)

out_lines = []


def p(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    out_lines.append(s)


# ----------------------------------------------------------------------------
# 0. External national benchmarks (verifiable empirical anchors)
# ----------------------------------------------------------------------------
# NCHS / NVSR age-specific US teen birth rates, per 1,000 females.
# Source: NCHS, "Births to Teenagers in the United States, 1940-2000",
#         National Vital Statistics Reports 49(10), 2001 (and ASPE/HHS table).
NAT_BR_1999 = {"10-14": 0.9, "15-17": 28.7, "18-19": 80.3, "15-19": 49.6}
NAT_BR_1998 = {"10-14": 1.0, "15-17": 30.4, "18-19": 82.0, "15-19": 51.1}
NAT_BR_2000 = {"15-19": 47.7}
# NCHS "Recent Trends in Teenage Pregnancy 1990-2002": US teen pregnancy rate
# 15-19 in 2000 = 84.8 per 1,000 (2002 = 76.4). 2002 outcome split (NCHS):
US_PREG_2002 = 757000
US_BIRTHS_2002 = 425000
US_ABORT_2002 = 215000
US_FETAL_2002 = 117000
US_BIRTH_SHARE = US_BIRTHS_2002 / US_PREG_2002          # ~0.561
US_ABORT_SHARE = US_ABORT_2002 / US_PREG_2002          # ~0.284
US_FETAL_SHARE = US_FETAL_2002 / US_PREG_2002          # ~0.155
# percent of US teen births to unmarried mothers, 2000 (NVSR 49-10) = 78.7%
US_UNMARRIED_2000 = 0.787

p("=" * 78)
p("ADOLESCENT PREGNANCY - ANALYSIS DIGEST")
p("=" * 78)

# ----------------------------------------------------------------------------
# 1. Load data
# ----------------------------------------------------------------------------
cty = pd.read_csv(os.path.join(DATA, "teen_pregnancy_county_2000.csv"))
reg = pd.read_csv(os.path.join(DATA, "teen_pregnancy_regional_1998_1999.csv"))
ages = ["10_14", "15_17", "18_19"]
age_lbl = {"10_14": "10-14", "15_17": "15-17", "18_19": "18-19"}

cty["preg_total"] = cty[[f"preg_{a}" for a in ages]].sum(axis=1)
cty["birth_total"] = cty[[f"birth_{a}" for a in ages]].sum(axis=1)
cty["unmar_total"] = cty[[f"unmar_{a}" for a in ages]].sum(axis=1)

# ----------------------------------------------------------------------------
# 2. Region totals and composition
# ----------------------------------------------------------------------------
p("\n--- 2. REGION TOTALS (county table) ---")
tot_preg = {a: int(cty[f"preg_{a}"].sum()) for a in ages}
tot_birth = {a: int(cty[f"birth_{a}"].sum()) for a in ages}
tot_unmar = {a: int(cty[f"unmar_{a}"].sum()) for a in ages}
P = sum(tot_preg.values())
B = sum(tot_birth.values())
U = sum(tot_unmar.values())
p("pregnancies:", tot_preg, "total", P)
p("births     :", tot_birth, "total", B)
p("unmarried B:", tot_unmar, "total", U)

rows = []
for a in ages:
    rho = tot_birth[a] / tot_preg[a]
    nb = tot_preg[a] - tot_birth[a]
    rows.append(dict(age=age_lbl[a], pregnancies=tot_preg[a], births=tot_birth[a],
                     non_birth=nb, retention=rho, nonbirth_share=nb / tot_preg[a],
                     unmarried=tot_unmar[a], unmarried_share=tot_unmar[a] / tot_birth[a]))
comp = pd.DataFrame(rows)
p("\nComposition table (region):")
p(comp.to_string(index=False, float_format=lambda x: f"{x:.4f}"))

region_retention = B / P
p(f"\nRegion overall retention B/P = {region_retention:.4f}  "
  f"(non-birth share {1-region_retention:.4f})")
p(f"National birth share of teen pregnancies = {US_BIRTH_SHARE:.4f}")
p(f"Region vs national birth share ratio     = {region_retention/US_BIRTH_SHARE:.3f}")

# ----------------------------------------------------------------------------
# 3. Binomial hypothesis test: does the region resolve pregnancies like the US?
# ----------------------------------------------------------------------------
p("\n--- 3. BINOMIAL TEST vs national outcome shares ---")
bt = stats.binomtest(B, P, US_BIRTH_SHARE, alternative="greater")
p(f"H0: birth prob = {US_BIRTH_SHARE:.3f} (US 2000). Observed {B}/{P} = {region_retention:.4f}")
p(f"p-value (one-sided, greater) = {bt.pvalue:.3e}")
exp_births = US_BIRTH_SHARE * P
p(f"Expected births under H0 = {exp_births:.1f}; observed = {B}; "
  f"excess = {B-exp_births:.0f} ({(B/exp_births-1)*100:.1f}%)")

# per-age binomial tests (15-17, 18-19 use same national share as reference)
p("\nPer-age binomial test (reference national birth share):")
for a in ages:
    t = stats.binomtest(tot_birth[a], tot_preg[a], US_BIRTH_SHARE, alternative="greater")
    p(f"  {age_lbl[a]:>5}: {tot_birth[a]}/{tot_preg[a]} = {tot_birth[a]/tot_preg[a]:.4f}"
      f"   p={t.pvalue:.3e}")

# ----------------------------------------------------------------------------
# 4. Pregnancy-outcome decomposition (Guttmacher fetal-loss model)
#    F = 0.20*B + 0.10*A ;  P = A + B + F  =>  A = (P - 1.20*B)/1.10
# ----------------------------------------------------------------------------
p("\n--- 4. OUTCOME DECOMPOSITION (Guttmacher fetal-loss model) ---")
dec = []
for a in ages:
    P_a, B_a = tot_preg[a], tot_birth[a]
    A_a = max((P_a - 1.20 * B_a) / 1.10, 0.0)
    F_a = 0.20 * B_a + 0.10 * A_a
    dec.append(dict(age=age_lbl[a], preg=P_a, births=B_a, abortions=A_a, fetal=F_a,
                    abort_ratio=A_a / (A_a + B_a)))
decdf = pd.DataFrame(dec)
p(decdf.to_string(index=False, float_format=lambda x: f"{x:.3f}"))
A_tot = decdf["abortions"].sum()
p(f"\nRegion implied abortion ratio (A/(A+B)) = {A_tot/(A_tot+B):.4f}")
p(f"US teen abortion ratio (2002 NCHS/Guttmacher) = {US_ABORT_2002/(US_ABORT_2002+US_BIRTHS_2002):.4f}")

# ----------------------------------------------------------------------------
# 5. County-level indicators and Composite index
# ----------------------------------------------------------------------------
p("\n--- 5. COUNTY INDICATORS ---")
for a in ages:
    cty[f"rho_{a}"] = cty[f"birth_{a}"] / cty[f"preg_{a}"]
cty["rho_all"] = cty["birth_total"] / cty["preg_total"]
cty["young_share"] = cty["preg_10_14"] / cty["preg_total"]
cty["unmar_share"] = cty["unmar_total"] / cty["birth_total"]

# concern-weighted pregnancy load  W = 3*P1014 + 2*P1517 + 1*P1819
cty["concern_load"] = 3 * cty["preg_10_14"] + 2 * cty["preg_15_17"] + 1 * cty["preg_18_19"]
cty["load_share"] = cty["concern_load"] / cty["concern_load"].sum()

for c in ["rho_all", "young_share", "unmar_share"]:
    mu, sd = cty[c].mean(), cty[c].std(ddof=1)
    cty["z_" + c] = (cty[c] - mu) / sd
cty["TPPI"] = 0.6 * cty["z_rho_all"] + 0.4 * cty["z_young_share"]
cty = cty.sort_values("TPPI", ascending=False).reset_index(drop=True)

show = cty[["county", "preg_total", "birth_total", "unmar_total", "rho_all",
            "young_share", "unmar_share", "concern_load", "load_share", "TPPI"]]
p(show.to_string(index=False, float_format=lambda x: f"{x:.4f}"))

# data-quality checks
p("\nData-quality checks:")
bad = cty[cty["birth_total"] > cty["preg_total"]]
for _, r in bad.iterrows():
    p(f"  ANOMALY: county {int(r['county'])} births_total ({int(r['birth_total'])}) "
      f"> pregnancies_total ({int(r['preg_total'])})")
for a in ages:
    b = cty[cty[f"birth_{a}"] > cty[f"preg_{a}"]]
    for _, r in b.iterrows():
        p(f"  ANOMALY(age): county {int(r['county'])} {age_lbl[a]}: "
          f"births {int(r[f'birth_{a}'])} > pregnancies {int(r[f'preg_{a}'])}")
u_gt_b = cty[cty["unmar_total"] > cty["birth_total"]]
p(f"  counties with unmarried_total > births_total: {len(u_gt_b)}")
# county sums vs 1999 aggregate
p("\nConsistency: county sums vs regional aggregate series")
p(f"  county sums 2000-tbl: {tot_preg} / {tot_birth}")
p(f"  aggregate 1999      : 10-14 {309}/{208}, 15-17 {3882}/{3048}, 18-19 {6714}/{5391}")

# ----------------------------------------------------------------------------
# 6. Chi-square tests of county heterogeneity
# ----------------------------------------------------------------------------
p("\n--- 6. CHI-SQUARE HETEROGENEITY TESTS ---")
# (a) county x outcome (birth vs non-birth)
tab = np.column_stack([cty["birth_total"].values, (cty["preg_total"] - cty["birth_total"]).values])
chi2, pv, dof, _ = stats.chi2_contingency(tab)
p(f"(a) county x outcome (birth/non-birth): chi2={chi2:.2f}, dof={dof}, p={pv:.3e}")
# (b) county x age composition of pregnancies
tab2 = cty[[f"preg_{a}" for a in ages]].values
chi2b, pvb, dofb, _ = stats.chi2_contingency(tab2)
p(f"(b) county x age composition: chi2={chi2b:.2f}, dof={dofb}, p={pvb:.3e}")
# (c) county x marital status of births
tab3 = np.column_stack([cty["unmar_total"].values, (cty["birth_total"] - cty["unmar_total"]).values])
chi2c, pvc, dofc, _ = stats.chi2_contingency(tab3)
p(f"(c) county x marital status: chi2={chi2c:.2f}, dof={dofc}, p={pvc:.3e}")

# ----------------------------------------------------------------------------
# 7. Trend analysis 1998 -> 1999 (Poisson / exact binomial on counts)
# ----------------------------------------------------------------------------
p("\n--- 7. TREND 1998 -> 1999 ---")
trend_rows = []
for a in ["10-14", "15-17", "18-19"]:
    for metric in ["pregnancies", "births"]:
        v98 = int(reg[(reg.year == 1998) & (reg.age_group == a)][metric].iloc[0])
        v99 = int(reg[(reg.year == 1999) & (reg.age_group == a)][metric].iloc[0])
        n = v98 + v99
        # exact Poisson/Poisson comparison via conditional binomial (equal exposure)
        bt2 = stats.binomtest(v99, n, 0.5)
        trend_rows.append(dict(age=a, metric=metric, y1998=v98, y1999=v99,
                               pct=(v99 - v98) / v98 * 100, p=bt2.pvalue))
tdf = pd.DataFrame(trend_rows)
p(tdf.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
tot98 = reg[reg.year == 1998][["pregnancies", "births"]].sum()
tot99 = reg[reg.year == 1999][["pregnancies", "births"]].sum()
p(f"\nRegion all-ages: pregnancies {tot98['pregnancies']} -> {tot99['pregnancies']}"
  f" ({(tot99['pregnancies']/tot98['pregnancies']-1)*100:+.2f}%)")
p(f"Region all-ages: births      {tot98['births']} -> {tot99['births']}"
  f" ({(tot99['births']/tot98['births']-1)*100:+.2f}%)")

# ----------------------------------------------------------------------------
# 8. Concentration of burden
# ----------------------------------------------------------------------------
p("\n--- 8. CONCENTRATION ---")
sh = cty["load_share"].values
hhi = np.sum(sh ** 2)
y = np.sort(sh)
n = len(y)
gini = (2 * np.sum(np.arange(1, n + 1) * y)) / (n * np.sum(y)) - (n + 1) / n
p(f"Concern-weighted load HHI = {hhi:.4f}; county Gini = {gini:.4f}")
top3 = cty.nlargest(3, "load_share")[["county", "load_share"]]
p("Top-3 counties by concern-weighted load:")
for _, r in top3.iterrows():
    p(f"  county {int(r['county'])}: {r['load_share']*100:.1f}%")

# ----------------------------------------------------------------------------
# 9. Save outputs
# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
# 8b. Rate identifiability / scenario analysis
#     Absolute rates need denominators that the problem does not provide.
#     Show how the 'problem factor' depends on the anchoring assumption.
# ----------------------------------------------------------------------------
p("\n--- 8b. RATE IDENTIFIABILITY / SCENARIOS (15-19) ---")
P19 = tot_preg["15_17"] + tot_preg["18_19"]
B19 = tot_birth["15_17"] + tot_birth["18_19"]
NAT_PREG_2000 = 84.8  # per 1,000, NCHS/Guttmacher
# Scenario A: anchor on national PREGNANCY rate -> implied female pop
NA = P19 / (NAT_PREG_2000 / 1000)
rateA = B19 / NA * 1000
# Scenario B: anchor on national BIRTH rate -> implied female pop
NB = B19 / (NAT_BR_2000["15-19"] / 1000)
rateB = P19 / NB * 1000
p(f"15-19 pregnancies={P19}, births={B19}, retention={B19/P19:.4f}")
p(f"Scenario A (anchor preg rate={NAT_PREG_2000}/1000): implied N={NA:,.0f}; "
  f"region birth rate={rateA:.1f}/1000 = {rateA/NAT_BR_2000['15-19']:.2f}x national")
p(f"Scenario B (anchor birth rate={NAT_BR_2000['15-19']}/1000): implied N={NB:,.0f}; "
  f"region preg rate={rateB:.1f}/1000 = {rateB/NAT_PREG_2000:.2f}x national")
p(f"Assumption-free core: region retention / national retention = {(B19/P19)/US_BIRTH_SHARE:.2f}")

result = dict(
    scenarios=dict(P19=P19, B19=B19, NA=float(NA), rateA=float(rateA),
                   NB=float(NB), rateB=float(rateB)),
    region_totals=dict(pregnancies=tot_preg, births=tot_birth, unmarried=tot_unmar,
                       P=P, B=B, U=U, retention=region_retention),
    national=dict(birth_share=US_BIRTH_SHARE, abort_share=US_ABORT_SHARE,
                  fetal_share=US_FETAL_SHARE, unm_share=US_UNMARRIED_2000,
                  br_1999=NAT_BR_1999),
    binomial_p=bt.pvalue, excess_births=float(B - exp_births),
    decomposition=decdf.to_dict(orient="records"),
    counties=cty.to_dict(orient="records"),
    chisq=dict(outcome=pv, age=pvb, marital=pvc),
    trend=tdf.to_dict(orient="records"),
    hhi=float(hhi), gini=float(gini),
)
with open(os.path.join(RES, "analysis_results.json"), "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, default=float)
with open(os.path.join(LOG, "analysis_log.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out_lines))
p("\nSaved results/analysis_results.json and logs/analysis_log.txt")
