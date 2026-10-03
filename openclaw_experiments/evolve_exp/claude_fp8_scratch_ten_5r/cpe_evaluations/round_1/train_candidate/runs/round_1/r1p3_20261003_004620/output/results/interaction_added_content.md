# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — 2021_C (Vespa mandarinia)

Ten expert exchanges. Each row: exchange, question (abridged), reply (abridged),
and how the reply was turned into model work. Full question/reply text lives in
`logs/operator_feedback/expert_question_N.md` / `expert_reply_N.json`.

| # | Question theme | Reply (gist) | Turned into |
|---|----------------|--------------|-------------|
| 1 | Most-mistaken look-alike species | European hornet, yellowjackets, bald-faced hornet, paper wasps, cicada killers, carpenter bees | Defined the confusion pool; text features (`has_size`, `has_color`, `has_behav`) encode the cues a misreport is built from; excluded species-specific image features |
| 2 | Which look-alikes are actually common in WA | Yellowjackets/bald-faced common; **European hornet NOT established in WA** | Removed European-hornet cues from the feature rationale; model discriminates on size/color/behavior/photo/location/season, not species name |
| 3 | Photo vs specimen vs description | Description-only most common > photo >> specimen | `has_photo`, `n_photos` features; treated photo presence as the main evidence-tier feature |
| 4 | Season of reports | Peak Aug–Oct, max in September | Seasonal sine term (peaking ~week 52 of the 2019-09-01 origin) in the spread Poisson model; month_sin/cos in classifier |
| 5 | How reports spread after a detection | Burst near detection in days, fades over weeks; real spread ~km/season | Awareness pulse in spread model: distance-weighted (exp(-d/R)) decaying (exp(-Δw/τ), τ=4 wk) contribution from each confirmed detection |
| 6 | Time before new reports after eradication | ~2 full seasons (incl. one Aug–Oct peak) minimum; 1–2 seasons to detect a survivor | Eradication criterion: ≥2 seasons, zero confirmed + consistent-with-baseline mistaken rate; detection-probability sweep over N active colonies |
| 7 | Triage priority | Photo/specimen + credible description + near detection + in-season + reliable reporter | Prioritization score = P_real from classifier (which already folds in photo, behavior, distance, season) — directly answers subproblem 3 |
| 8 | Lab confirmation time | Minutes–hours per specimen; end-to-end days–weeks (logistics); photo screening quick but often inconclusive | Justifies treating "unverified" as a missing-data tier rather than negative; lag feature; keeps unverified out of classifier training labels |
| 9 | Review cadence | Daily–weekly in season (Jul–Oct); monthly/seasonal off-season; full re-prioritization 1–2×/year | Update cadence for subproblem 4: weekly re-score during Aug–Oct, seasonal re-fit off-season |
| 10 | What reports describe | Size > color > behavior > bee-damage; behavior and bee-damage most informative | Feature importance check: `has_behav` and `has_bee` retained as the diagnostic text cues; `has_size`/`has_color` weaker (consistent with fit) |

## Parameters sourced from exchanges (for the parameter table in solution.json)

- `tau_awareness = 4.0 weeks` — awareness fade after a confirmed detection (exchange 5: "burst in days to a couple of weeks, fades over weeks to a month"). Interval [2, 8] weeks.
- `R_aware ∈ {10, 25, 50} km` — spatial reach of a detection's reporting boost (exchange 5). Sweep in spread model; likelihood flat across the range, so the estimate is not sensitive.
- `p_detect_per_season = 0.7` — probability a surviving colony yields a detectable report in one active season (exchange 6: "likely within one to two seasons"). Interval [0.5, 0.9].
- `season_peak = week 52` (≈ late Aug–Sep of the second season) — exchange 4.
- `n_peak_weeks = 13` (Aug–Oct) — exchange 4/6.
- Update cadence: weekly in-season, seasonal off-season — exchange 9.
