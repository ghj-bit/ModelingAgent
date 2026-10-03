# Expert Interaction Evidence — 2019_C (NFLIS opioid spread, 5-state MCM)

Policy: constraint-prioritization. 10 exchanges, one question each; each reply turned into a model parameter, rule, or test before the next exchange.

## Exchange 1
Q: A rising county identification count — more cases or more enforcement?
Reply (paraphrased): supply-side/enforcement indicator; count = presence x enforcement effort x submission consistency; one case yields many identifications; a rise is not a prevalence rise.
Used as: **measurement model assumption** — NFLIS counts treated as a proxy y = x * enforcement * submission, not as user counts. All "growth" claims in the report are phrased as identifications, and per-capita/state-share normalization is used to strip population and lab-throughput effects (results/af_panel per10k, opioid_share in nflis_opioid_share.csv). Interval: 2010-2017, 5 states.

## Exchange 2
Q: How does a DEA analyst check a county's real problem is growing?
Reply: triangulate with harm outcomes (overdose deaths/ED visits), treatment demand, supply composition shift (heroin->fentanyl), and normalize county identifications as share of county total + per capita; watch for step-changes tied to task forces.
Used as: **signal-validation rule** — model1b computes per-capita rates and the heroin/synthetic composition by state-year (synthetic peaks 2017 in OH while heroin peaked 2013-2015: composition shift is a model input, not an output). Composition-shift test reported in solution Part 1.

## Exchange 3
Q: Single number to watch for a county turning serious?
Reply: per-capita overdose death (or ED visit); least gameable; but not available in supplied data.
Used as: **limitation + proxy choice** — overdose data absent from supplied datasets, so the model's "serious" trigger is the county's own baseline-relative jump (exchange 6), not a fixed national threshold. Recorded in solution Part 1 limitations.

## Exchange 4
Q: Spread to neighbors or independent ignition?
Reply: dominant pattern is contagion into neighboring counties (supply routes, social ties, shared institutions) with occasional independent ignition at distinct sources; core-and-spillover.
Used as: **structural model choice** — Part 1 uses a spatial autoregressive diffusion term A_d @ x_t over a corridor adjacency graph (89 edges on I-64/I-65/I-70/I-71/I-74/I-75/I-77/I-79/I-81/US-23/US-52/US-60/US-11 corridors, code/build_adjacency2.py), plus an autonomous-growth term rho*x_t to allow independent ignition. Estimated beta_diff is small and statistically insignificant (t=0.84) — i.e., in this data the between-county channel is weak relative to within-county persistence; reported as a null result with the corridor graph as the sensitivity case.

## Exchange 5
Q: How long before a local response measurably slows a rural county's problem?
Reply: typically 3-7 years from visibility, often longer or never; detection lag 1-2 years; response is reactive, bends the curve.
Used as: **strategy-model ramp lag** — Part 3 simulation applies treatment effects only after a 4-year ramp (midpoint of 3-7), i.e., suppression factor f(t)=min(t/4,1) (code/model5b.py). Domain of validity: rural Appalachia counties, multi-year horizon.

## Exchange 6
Q: First state-agency action when identifications jump above a clear threshold?
Reply: verify/interpret first (rule out reporting artifact, check composition), then alert/convene, naloxone, surveillance escalation; thresholds are not standardized — agencies react to jumps relative to the county's own baseline and neighbors, not fixed national numbers.
Used as: **threshold definition** — Part 1 threshold = county-level 2010-2017 mean + 2 standard deviations (baseline-relative, per exchange rule), not a national constant. Crossing table: 139 of 394 counties crossed at least once (results/model2_results.json crossings); historical crossings 2010-2016, forecast crossings 2018-2022 where predicted value exceeds the county level.

## Exchange 7
Q: Which single response reduces a county's problem most over the long run?
Reply: sustained expanded access to MOUD (buprenorphine/methadone); naloxone saves lives but not incidence; enforcement displaces supply; works only if capacity and retention are real.
Used as: **Part 3 strategy choice** — treatment-expansion scenario is the primary tested strategy; parameterized by reach fraction and a 0.50 per-year log-growth reduction among the treated at full rollout.

## Exchange 8
Q: Does treatment cut seizures/identifications, or mainly overdose deaths?
Reply: mainly overdose deaths; seizures/identifications track enforcement and supply composition and stay flat or rise; any seizure effect is slow, weak, masked by fentanyl shift.
Used as: **model boundary condition** — Part 3 scenario effects are applied to the identification process only through the demand channel and are reported as *at most* proportional to treated share; the report states explicitly that the model's 9.8-19.3% five-year identification reductions are upper-bound, and the primary expected effect is on harm (deaths), which the supplied data cannot score. This bounds interpretation of the strategy results.

## Exchange 9
Q: What fraction of a rural county's opioid-dependent population can realistically be reached and retained in treatment over a few years?
Reply: small minority, ~10-25%, often single digits to ~15% in weakest rural counties; retention is the binding constraint.
Used as: **calibrated parameter** — reach in {0.10, 0.15, 0.20, 0.25} (plus 0.40 as optimistic case); the 10-25% band brackets the expert estimate. Source: exchange 9.

## Exchange 10
Q: When does treatment expansion matter less (problem already declining)?
Reply: when the decline is supply-driven, cohort-driven, measurement-driven, capacity already unsaturated, or the remaining users are hardest to reach; treatment matters most when untreated demand is the binding constraint.
Used as: **boundary condition / validity domain** — Part 3 results are interpreted conditionally: in counties already declining on the natural trajectory (all four states are at or past their 2013-2017 peaks except OH), the marginal value of treatment is smaller; the model's suppression term is scaled by (x - median x) so counties far above their peers (untreated-demand-constrained) gain more, and near/under-median counties (declining or measurement-driven) gain little. Failure bound reported: below reach ~0.10 with a 4-year ramp, five-year reductions are under ~10% of identifications.

## Exchange-to-work mapping check
Every reply produced a named parameter, rule, equation change, or test with its interval and source as above; no exchange was used for code or computation help.
