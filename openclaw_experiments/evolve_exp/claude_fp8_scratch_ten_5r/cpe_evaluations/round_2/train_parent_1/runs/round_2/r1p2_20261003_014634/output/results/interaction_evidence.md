# Interaction Evidence — 2019_C

## Exchange 1
**Question (expert_question_1.md):** When local law enforcement sends seized-drug samples to a forensic lab, are those drug reports generally tied to the community where the evidence was collected, or can a single lab report many cases from far-away areas?

**Reply (expert_reply_1.json):** Reports are predominantly local to the submitting county — the county recorded is normally the county of the investigating agency, which usually matches the seizure location. A single lab can still cover distant counties (state labs serving the whole state, federal labs, missing-location imputation, multi-jurisdiction task forces), so the county field is a reasonable proxy for the seizure community but reflects the submitting agency's location, not necessarily the exact seizure point.

**How the reply was turned into work:**
- Parameter/constraint: county-level NFLIS DrugReports counts are treated as a locally representative proxy for local drug-incident activity (validity condition: state-level spatial aggregation smooths residual attribution noise; county-level counts used only for relative spread analysis, not absolute incidence).
- Equation/code change: in `code/prepare.py` (to be run), county-year matrices are normalized by TotalDrugReportsCounty before cross-county spread analysis; state-level aggregation uses raw sums. This keeps the model robust to the attribution noise the reply describes.
- Interval of validity: all five states, 2010–2017.

## Exchange 2
**Question (expert_question_2.md):** In a county's typical year, do drug labs report only a tiny share of the opioid cases that actually happen, and does that reported share stay roughly stable year to year?

**Reply (expert_reply_2.json):** Not tiny, and not stable. NFLIS covers labs handling ~88% of the nation's state/local drug cases, so reported counts are a substantial share of the forensic caseload (problem statement corroborates the 88% figure). Caveats: counts reflect cases submitted and analyzed by labs, not all use (true denominator much larger); year-to-year DrugReports mix real trend with reporting artifacts (lab participation, submission practices, testing priorities, backlogs, counties entering/leaving the panel).

**How the reply was turned into work:**
- Parameter/constraint: reporting coverage ~0.88 of state/local forensic drug cases (interval [0.8, 0.9]), source: exchange 2 reply, corroborated by problem statement. Validity: all five states, 2010–2017.
- Constraint: DrugReports counts are not absolute incidence; model output must be framed as "reported-identification" dynamics, and year-to-year differences may contain reporting artifacts.
- Equation/code change: in the model script, (i) county panel-membership stability check is run (count of counties reporting >=1 opioid identification per year, state by state) to flag panel churn as an artifact channel; (ii) state-level growth rates are estimated from 2013→2017 (post-panel-stabilization window) in addition to 2010→2017, and both are reported; (iii) spread/epidemic indicators use share-of-substances (DrugReports / TotalDrugReportsCounty) rather than raw counts, which is partially robust to lab-participation artifacts.
- Domain-of-validity note: predictions beyond 2017 assume reporting behavior stays in the 2013–2017 regime.

## Exchange 3
**Question (expert_question_3.md):** When a new type of drug starts showing up in one county, does it usually begin in big cities, small towns, or does it depend on something else?

**Reply (expert_reply_3.json):** No rule of city size. First appearance is driven by (a) connectivity to supply routes/distribution hubs (interstates, major metro markets, prison-release flows), (b) presence of an existing opioid-using population and active retail market (often mid-size cities and surrounding counties), and (c) reporting/lab artifacts — a county can look "first" simply because its lab tests and reports that substance while neighbors' do not; local enforcement and submission practices also shift apparent timing.

**How the reply was turned into work:**
- Parameter/constraint: source of first-appearance is supply-connectivity + receptive-market + detection artifact, not city size (mechanism choice for Part-1 origin inference), source: exchange 3.
- Equation/code change: the origin-inference rule in the model is therefore: a county is a candidate origin for substance s if it has (i) high pre-spike reported level of the same or adjacent substance class (receptive market), (ii) early reporting of substance s relative to neighboring counties (supply/detection lead), and (iii) its first-appearance signal persists in at least 2 of the following 3 years (to suppress one-off lab-artifact spikes). City size alone is not used as an origin criterion; population enters only as a detection-sensitivity covariate in Part 2.
- Domain of validity: 2010–2017 five-state panel; the rule treats first-appearance years 2010–2013 for heroin and 2013–2015 for fentanyl as the emergence windows.

## Exchange 4
**Question (expert_question_4.md):** In the Appalachian region, which kind of county tends to have the highest opioid problems: a poorer one, one with more joblessness, or one with fewer years of schooling?

**Reply (expert_reply_4.json):** Joblessness / economic dislocation is the closest single correlate; low educational attainment is a close second and largely overlapping (proxy for the same distress); poverty alone is the weakest and noisiest. The three are collinear ecological associations, not precise thresholds.

**How the reply was turned into work:**
- Prior for Part-2 regression: expected coefficient ordering |beta_joblessness| >= |beta_education| > |beta_poverty-like|, with strong multicollinearity among the distress covariates. Source: exchange 4.
- Code change: the Part-2 regression (in `code/model2.py`) will use standardized covariates and report VIFs; because the supplied ACS DP02 file contains no income/poverty/unemployment columns, the "economic distress" proxy that exists in the data is household-structure (female-headed, no-husband households) plus low educational attainment (inverse of PCT_HS_GRAD) and small population; the poverty/unemployment ordering from the reply is carried as a *prior to check*, and the answer will explicitly state which covariate dominates in this data.
- Validity: ecological, county level, Appalachian five-state context.

## Exchange 5
**Question (expert_question_5.md):** When law enforcement or a state wants to stop fentanyl from spreading to a new county, what kind of action actually works best?

**Reply (expert_reply_5.json):** Supply-side disruption (upstream trafficking organizations, distribution hubs, mail/shipping routes, retail-market shutdowns) outperforms county-border enforcement; harm reduction (naloxone, MAT/treatment) blunts deaths and works even when supply action fails; cross-jurisdiction task forces matter. What fails: local border-style enforcement, one-off seizures, supply-only strategies without treatment capacity. Success conditions: sustained upstream disruption AND local treatment/naloxone capacity — remove either and the drug reappears.

**How the reply was turned into work:**
- Strategy choice for Part 3 (constraint): counter-strategy = (i) sustained upstream/regional supply disruption reducing the inter-county spread coefficient, + (ii) county-level treatment/naloxone capacity raising local recovery. Source: exchange 5.
- Equation change: Part-3 model tests the strategy by reducing spread coefficient D by factor (1 - eta_s) and adding a recovery term r*capacity to local incidence dynamics; "success" = projected 2018–2024 fentanyl identification counts below the no-intervention baseline by a pre-set margin; failure modes tested: eta_s alone without capacity (drug reappears), capacity without sustained eta_s (spread continues). Parameter bounds to be computed in `code/model3.py`: minimum sustained disruption eta_s and minimum capacity share for success.
- Validity: five-state region, 2018–2024 projection horizon.

## Exchange 6
**Question (expert_question_6.md):** In the mid-2010s, which opioid was spreading the fastest through these rural counties: heroin, prescription pills, or fentanyl?

**Reply (expert_reply_6.json):** Fentanyl, by a wide margin (2014–2017). Sequence: prescription pills (2000s–early 2010s) → heroin surge (~2010–2014) as pill supply tightened → fentanyl displacing/adulterating heroin from ~2014. Fentanyl potent, cheap, mailable, mixed into heroin / pressed into counterfeit pills. Heroin growth flattened/reversed as fentanyl took over; prescription pill reports declining by mid-2010s. Caveat: apparent speed partly detection (labs testing/reporting fentanyl more).

**How the reply was turned into work:**
- Prior for growth ordering (to be verified by the Gompertz g estimates): g_FENT > g_HER ≈ flat/declining, prescription-class declining. Source: exchange 6.
- Data check run (in `code/model1.py` HER run + prescription-class aggregation): confirm fentanyl g exceeds heroin g for each state 2014–2017, and that heroin turns flat after ~2014 in OH/KY (which the raw sums already show: OH heroin peaked 2015 at 23,347 then fell to 15,045 in 2017; KY peaked 2014 at 4,362 then fell to 3,231 in 2017).
- Validity: five-state Appalachian region, 2014–2017; detection caveat carried into limitations.

## Exchange 7
**Question (expert_question_7.md):** When officials set an alert level for a county's drug problem, do they compare it to the state's own normal, or to a fixed national standard?

**Reply (expert_reply_7.json):** Thresholds are state/county-relative, not a fixed national standard. A county is flagged when its rate/count rises above its own historical average or above the state/regional distribution of counties, by some multiple (e.g. 1.5–2× the state median or its own prior-year level). Within-state, trend-based thresholds are used because absolute levels differ by an order of magnitude across states. Caveat: some federal programs use uniform absolute thresholds (e.g. overdose deaths per 100,000) for national designation, but operational local alerts are state- or county-relative.

**How the reply was turned into work:**
- Constraint/validation for Part-1 thresholds: the warning threshold T_warn is set as the 90th percentile of each state's own 2010–2017 yearly series (state-relative), consistent with the reply's "within-state, trend-based" practice. The crisis threshold (3-year growth > 50%) is likewise a within-state trend rule. A fixed national constant is deliberately NOT used.
- Parameter: alert multiple ~[1.5, 2.0]× the state median or prior-year level (source: exchange 7). My 90th-percentile rule is a fixed quantile of the within-state distribution, which sits near the 1.5–2× multiple for the observed distributions; I report both readings (90th percentile and 2× state median) so the alert is robust to either operational convention.
- Domain of validity: all five states, 2010–2017; applies to both HER and FENT alert levels.

## Exchange 8
**Question (expert_question_8.md):** In a small rural county, is addiction treatment and overdose-reversal coverage generally easy to reach, or is it often scarce?

**Reply (expert_reply_8.json):** Often scarce in small rural Appalachian counties. Treatment capacity is thin (few/no buprenorphine or methadone prescribers, long waitlists, clinics concentrated in larger towns, travel of an hour or more; MAT is the scarcest). Naloxone coverage depends on pharmacies/health departments/first responders; rural pharmacies may not stock it and lay distribution is thinner than in metros. Workforce shortages, limited transit, and weak broadband compound the gap. Coverage exists but is thin and uneven.

**How the reply was turned into work:**
- Parameter for Part-3 strategy model: baseline county treatment/naloxone capacity in the five-state region is LOW (baseline share c0 ~[0.2, 0.5], i.e. thin and uneven), so the counter-strategy's recovery term r*c0 starts small and the strategy's success margin depends on *building* capacity, not just disruption. Source: exchange 8.
- Constraint: capacity is an investment variable, not a free parameter — the Part-3 sweep treats "capacity share targeted" as the lever (with a realistic floor: the reply says even targeted coverage is hard to reach everywhere, so the strategy is tested up to a maximum feasible capacity, not 100%).
- Domain of validity: rural Appalachian counties, five-state region, 2018-2024 projection horizon.

## Exchange 9
**Question (expert_question_9.md):** Once a drug has reached most counties in a state, does its spread to the few remaining counties tend to slow down, or keep going?

**Reply (expert_reply_9.json):** Keep going, but the *rate* of new-county appearance slows — not the same thing. (a) Geographic frontier saturates: new counties gained per year falls and flattens as few counties remain unexposed (a ceiling effect, not a real slowdown). (b) The drug keeps spreading *within* counties — prevalence/case counts/penetration keep rising even after every county has some cases. (c) Reintroduction and churn: counties can drop to zero and reappear; new substances restart the frontier. (d) Reporting artifacts: apparent late spread can be a lab newly testing, not genuine arrival. Net: new-county spread decelerates toward zero as counties saturate, while total burden typically keeps growing.

**How the reply was turned into work:**
- Model interpretation/validation for Part 1: confirms the two-layer structure — the SIR county-spread term c_t saturates at N (new-county appearances flatten, matching the observed fentanyl penetration flattening at 0.94-0.97 in OH/PA), while the state-level count S_t keeps growing (burden deepens inside counties). The saturating-approach growth model with K = reporting-system bound is the right reading: county-coverage saturates, count does not stop growing until the reporting ceiling binds.
- Constraint on Part-3 "where" prediction: a county is a *lasting* hotspot only if its share persists; a county that drops to zero and reappears (churn) is flagged by the persistence rule (>=2 of next 3 years). "Reached" is not permanent — the model must not treat first-appearance as terminal.
- Parameter: new-county appearance rate decelerates toward 0 as c_t -> N (built into the SIR (N-c)/N factor); source: exchange 9.
- Domain of validity: all five states, 2010-2024.

## Exchange 10
**Question (expert_question_10.md):** What would convince you that a drug-outbreak warning was a real signal and not just a bump in the numbers from a single busy month?

**Reply (expert_reply_10.json):** A real signal shows: (a) persistence — the elevated level holds for several consecutive months/quarters, not one spike; (b) consistency across independent indicators — lab reports rise with overdose ED visits, naloxone administrations, and/or deaths, not one series alone; (c) a clear structural break — departure from the county's own baseline and normal noise by a wide margin (~1.5-2× typical level), sustained; (d) geographic coherence — neighboring counties or the same supply corridor show the same rise, not one isolated county; (e) a plausible mechanism — a new substance or known supply disruption; (f) not a reporting artifact — not explained by a lab newly testing or a backlog clearing. Absent persistence and corroboration, a one-month rise is noise.

**How the reply was turned into work:**
- Validation criteria for the Part-1 alert (signal vs. artifact) — the alert rule is required to satisfy, before a county is declared a crisis: (i) persistence: the elevated count holds for >=2 consecutive years (not a one-year spike); (ii) a structural break: the county's count is >=1.5x its own baseline (prior-year or 3-yr mean), consistent with the ~1.5-2x margin; (iii) geographic coherence: >=1 neighboring/adjacent-supply-corridor county in the same state also elevated (not isolated). These are the "where" and "when" confirmation filters on top of the T_warn threshold.
- Parameter: signal margin ~[1.5, 2.0]× the county's own baseline, sustained >=2 periods (source: exchange 10).
- Constraint: because the NFLIS data is a single lab-report series (no ED/naloxone/death series supplied), the cross-indicator corroboration (b) cannot be computed from the supplied data; it is recorded as a limitation and the alert is framed as "reported-identification signal," with the other four criteria (persistence, break, coherence, mechanism, non-artifact) all applied in-model.
- Domain of validity: all five states, 2010-2024; applies to the county-level "where" prediction.
