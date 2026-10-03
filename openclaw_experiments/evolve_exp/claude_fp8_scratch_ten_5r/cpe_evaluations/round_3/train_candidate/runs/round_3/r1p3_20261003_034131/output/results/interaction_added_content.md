# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — 2021_C (Vespa mandarinia)

Ten expert exchanges. Each reply was converted into a named model parameter/constraint
or a changed rule; the values below are what entered the model (source: the exchange).
No expert wording is reproduced in the submission.

| # | Question (short form) | Reply (short form) | Model use |
|---|---|---|---|
| 1 | Photo vs words+location for triage | Words + location drive triage; photo secondary/often unusable; location strongest filter | Structured the feature set: text keywords + spatial features as primary predictors; image *count* (not content) used only as a proxy; no image-content model |
| 2 | Distance to confirmed detection that matters | ~5 km = follow up almost always; 20–30 km = plausible, screened; >30 km = low priority outlier | Spatial tiers in risk score: d≤5 km ×2.0, 5–30 km ×1.0, >30 km ×0.5 (multipliers) |
| 3 | Reporter behavior after a negative result | Mostly never report again; re-reporting (rare) clusters ~seasonally | Dedup rule: same-reporter repeats carry no independent evidence; no "cooldown" term needed |
| 4 | Rural vs urban at equal distance | Rural/small-town reports worked harder; urban lone reports more likely misid; effective radius wider in rural | urban/rural multiplier: local report-density proxy → rural ×1.5, suburban ×1.0, urban ×0.75 |
| 5 | Trust in short/sloppy notes | Detailed note (name+size+behavior) is a strong upward modifier; weak note is near-neutral, not penalizing | `note_rich` (0–4 aspects) feature in the logistic model; risk score uses probability (not a hard penalty) so weak notes are near-neutral |
| 6 | Corroboration vs same-person repeat | Independent nearby report = strong corroboration (can raise a tier); same-person repeat = deduped, mildly discounted | `corroborated` = independent report within 5 km & 7 days (same-ID excluded); corroboration ×1.5 in risk score; dedup rule in data cleaning |
| 7 | New nest → more local reports? | Confirmed nest reliably generates a local cluster over following weeks/months; isolated far sighting = probable one-off | Spread model interprets positives as cluster-forming; eradication rule penalizes new clusters; spatial-only baseline motivated |
| 8 | Monthly investigation capacity | ~20–50 field follow-ups/month in busy season; binding constraint = field time, small staff | Capacity parameter C=35/mo (range 20–50); monthly top-C recall evaluation; top-N prioritization framing |
| 9 | Eradication bar | 3 consecutive years with no confirmed nest/specimen/credible sighting; keep targeted surveillance after (ports, prior nests, apiaries) | Eradication decision rule: 3 quiet seasons + background report volume + no unexplained cluster + no negative-ID cluster; residual miss probability (1−q)^3 with q∈[0.3,0.9] |
| 10 | How often to refresh prioritization | Weekly formal re-run in season, monthly/less in winter; immediate on: new positive, cluster, clear photo, capacity change, new-area detection | Update-cadence rule in the model: weekly in-season, monthly off-season, plus 5 event triggers |

## How each reply was turned into work

1. **Exch 1** → feature design decision: primary model = text keywords + spatial + image *counts*; image content intentionally excluded (expert: photos mostly unusable). The image-only sub-model (AUC 0.738) shows photos carry less signal than text.
2. **Exch 2** → the three spatial multipliers in `risk_raw` (near 2.0 / mid 1.0 / far 0.5). Without this, spatial-only recall top100 was 0.571; the tiers encode the 5/30 km operational bands.
3. **Exch 3** → dedup rule (same-reporter repeats excluded from corroboration; no repeat penalty term).
4. **Exch 4** → `urban_rural` multiplier computed from local 10 km/30-day report density (rural ×1.5, urban ×0.75).
5. **Exch 5** → `note_rich` feature (count of {insect named, size given, behavior, location} present, 0–4). Enters the logistic fit and the image-only fit.
6. **Exch 6** → `corroborated` flag (independent report ≤5 km & ≤7 days) and the ×1.5 corroboration multiplier; same-ID repeats excluded.
7. **Exch 7** → interpretation of the positive chronology (clusters, not one-offs) and the cluster test inside the eradication rule.
8. **Exch 8** → `capacity` parameter (35/mo, 20–50) and the monthly top-35 recall evaluation (2020 season recall 0.333).
9. **Exch 9** → eradication rule (3 seasons) and the residual-miss computation `(1−q)^3` for q ∈ {0.3, 0.6, 0.9} → {0.343, 0.064, 0.001}.
10. **Exch 10** → update-cadence block: weekly in-season / monthly off-season + 5 immediate-refresh triggers.
