# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — MM-Bench 2002_C (Florida scrub lizard)

Ten exchanges, mechanism → constraint → parameter sequencing. Each reply was turned
into model content before the next question was asked.

| # | Question (abridged) | Reply (gist) | How it entered the work |
|---|---|---|---|
| 1 | What usually happens to a baby lizard moving between patches? | Most die en route in the unsuitable matrix (predation, desiccation, vehicles); survivors settle in nearby patches. | Task 4: migration modeled as a loss process — the histogram is a survivor distribution, so P(recapture \| released) ≈ 1.0 is a lower bound and the distance-decay shape is the survival shape. Task 5: immigration treated as a weak subsidy, not a rescue. |
| 2 | How far apart are patches usually? | ~200 m to a few km; the histogram only observed to 350 m, so far dispersal is unobserved. | Task 4: state explicitly that the 350 m survey truncation means true migration survival is even lower; Task 5: no patch is "rescued" by distant sources — only nearby patches matter. |
| 3 | Worse for a patch: small, or far from others? | Small is usually worse — small size degrades the vital rates themselves (low sandy area → low Fa, Sj, Sa) and lowers carrying capacity; distance only weakens a small immigrant inflow. | Task 3/5: the dominant driver of patch quality is sandy habitat area, which is why all vital-rate functions and C are regressed on sandy area; viability is judged primarily on size (C), not connectivity. |
| 4 | What makes a small patch unable to hold a lasting population? | Low C (demographic stochasticity, skewed sex ratios), degraded vital rates, weak rescue by immigration, inbreeding/edge effects. | Task 5 viability rule: a patch is viable only if its equilibrium total is large enough to buffer stochasticity — threshold NMIN on C, tested at 15/25/40. |
| 5 | How many lizards would ~1 ha of open sand support? | On the order of a handful to ~10–20 lizards; far too few to be viable on its own. | Task 5: sets NMIN = 25 as the central minimum-viable population (with sensitivity 15 and 40); patches below it are classified non-viable. Also sanity-checks C magnitudes. |
| 6 | How often are controlled burns needed? | Roughly every 5–15 years, with ~5–10 years the common target; consistent with 6%/yr vegetation growth closing canopy in ~a decade or two. | Task 6: burn every ~8 years (central) as the recommended cycle; model shows open sand closes by 10× in ~30 years absent fire, so a fixed 5–10 year rotation keeps patches on the early-successional plateau. |
| 7 | How soon do lizards come back into a burned patch? | Months to a year or two; burn improves the patch; refill speed depends on nearby surviving sources. | Task 6: burning is net positive for lizards (immediately usable open sand), so the policy can recommend burning without a long productivity penalty; isolated patches recover slowly, reinforcing the conservation of nearby source patches. |
| 8 | Do lizards stay in one patch or move? | Mostly stay; adults don't migrate; only ~10% of juveniles disperse and most die. | Task 5: per-patch model with no adult movement; juveniles leave at rate 0.10 with migration survival from Task 4; metapopulation coupling is weak, so the landscape total is essentially the sum of per-patch equilibria. |
| 9 | Biggest threat besides fire? | Development and fragmentation — housing, agriculture, mining convert and isolate scrub; fire suppression is the main within-patch threat. | Task 1: recommendations prioritize protecting patch size and sandy-area proportion (the Task-3 drivers) and connectivity; Task 6 distinguishes within-patch (fire) from landscape-level (development) threats. |
| 10 | Do landowners consent to preservation? What blocks it? | Often yes via easements/mitigation banks/Florida Forever, but conditionally; blockers: development value, property-rights resistance, funding limits, burn-management burden, fragmented ownership. | Task 1: obstacles section — cost, enforcement, and maintenance (burning) costs, not just initial acquisition; recommends funding + education + incentives, matching the stated obstacles. |

## Data cleaning
- table1.csv, table2.csv, table3.csv: clean; table2 patch id "C" vs "c" (cosmetic, not used).
- histogram.csv: values in five distance bins; sum of proportions = 1.000 (survivor proportions of released juveniles recaptured within the 350 m survey radius).
- No missing values, duplicates, or encoding problems found.

## Model results (see results/model_out.json, logs/model.log)
- Task 2: Fa ≈ 3.53 eggs/female/yr (mean adult clutch from y = 0.21·SVL − 7.5 at SVL 45.8–56 mm); Sj = 180/972 = 0.185; Sa = (20/180 + 2/20)/2 = 0.106.
- Task 3: Fa = 5.737 + 0.0709·S (r² = 0.77); Sj = 0.134 + 0.0008·S (r² = 0.66); Sa = 0.072 + 0.0011·S (r² = 0.81); C = 36.9·S^0.221 (r² = 0.83), S = sandy habitat (ha).
- Task 4: P(recapture ≤ 350 m | released) = 1.000 (survivors); conditional on recapture: 67% ≤ 100 m, 30% at 100–200 m, 3% at 200–350 m.
- Task 5: landscape total ≈ 1389 lizards; with NMIN = 25, 28 patches viable, 1 not (patch 18, S = 0.13 ha). At NMIN = 15 all 29 viable; at NMIN = 40, 21 viable.
- Task 6: burn every 8 years (range 5–10); without fire, vegetation density compounds 6%/yr (×10 in ≈ 38 yr).
