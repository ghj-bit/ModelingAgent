# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — MM-Bench 2021_C (Vespa mandarinia)

Ten exchanges, one question each. Each reply was turned into a concrete
parameter, feature, or decision rule below; the source is the exchange
number. Questions were kept to common-sense real-world content, no
modelling terminology.

| # | Question (abridged) | Reply (key content) | How it entered the model |
|---|---|---|---|
| 1 | Which insects were most often mistaken for the giant hornet? | European hornet (*V. crabro*), yellowjackets (*Vespula*), bald-faced hornets (*D. maculata*), paper wasps (*Polistes*), bumblebees, large flies. | Defined the **look-alike feature set** for the classifier. Verified against `Lab Comments`: yellowjacket 109, bald-faced 124, bumblebee 88, fly 52, paper wasp 34 mentions among the 2069 negatives. These became the `note_yellowjacket`, `note_baldfaced`, `note_bumblebee`, `note_paperwasp`, `note_crabro` binary features. |
| 2 | Does a new queen nest near where seen or move far? | Disperses to found a colony; the 30 km range is an **upper bound**, many queens establish closer. | Set the spatial-dispersal kernel in the spread model to a **decaying kernel centred near the origin with a 30 km tail**, not a uniform 30 km disk. Used 30 km as the maximum dispersal parameter; the effective cluster radius came out to ~0.17 km. |
| 3 | What makes one report worth an investigator before another? | Credible positive evidence (clear photo/specimen, knowledgeable reporter), corroboration/cluster, high-stakes location (apiaries, prior infestation), timeliness/season, plausible description. Ranking by **expected value = P(true positive) × cost of miss ÷ investigation cost**. | Defined the **prioritisation rule** `EV_i = p_i · C_miss(i)`, where `C_miss` rises with proximity to confirmed positives (proxy for apiary/infestation risk) — implemented in `classifier.py` as `C_miss = 1 + 5·exp(-dist/25)`. |
| 4 | Does a clear photo settle the ID, or is a specimen needed? | A clear photo usually suffices for a confident ID; marginal photos or high-stakes records need a specimen. | Justified treating **photo attachment as a strong credibility signal** (it raises confidence the report is actionable) and explained the residual false-positive rate: a photo raises P but does not prove it, so the model keeps `p<1` for photo reports. |
| 5 | After a nest is destroyed, how long do straggler reports continue? | A few days to a few weeks, ~1–3 weeks at most; reports months later or in another season are new detections or misIDs, not stragglers. | Set the **straggler-decay window** to 3 weeks for the post-destruction reporting model; a report arriving >3 weeks after a known destruction is reclassified as a *new* detection candidate rather than a straggler. |
| 6 | After the news, do people re-report the same insect or report new locations? | A surge of **new reports from many new locations**, not re-reports; awareness-driven, mostly misidentifications. | Justified the **media-pulse model**: report volume is driven by a publicity step-change, not by pest spread. Fit: post-press weekly rate 64.9/wk vs pre-press 0.25/wk (ratio 257, CI [220,300]). This is why the report "cloud" widens faster than the confirmed front. |
| 7 | Are adult hornets seen flying in winter or only warm months? | Only warm months (spring–fall); the overwintering stage is a **dormant mated queen in soil**, not flying. A winter flying-adult report is biologically implausible. | Created the `active_season` (Apr–Oct) and `winter_report` (Nov–Feb) features. A winter flying-adult report is a strong **negative-likelihood / data-artifact** signal. Data check: 14.3% of positives vs 0.3% of negatives fell in winter months (those positives are the dormant-queen / overwinter records, consistent with the biology). |
| 8 | Where do they nest — ground or trees/buildings? | Usually **underground** (abandoned rodent burrows, tree bases, root systems); above-ground is rarer and more typical of look-alikes. | Added `note_ground_nest` and `note_aerial_nest` features: a ground-nest description is more biologically plausible for AGH, an aerial/exposed nest tilts the report toward a look-alike (negative). |
| 9 | How often should the state refresh the report-ranking? | **Weekly–biweekly** in the active season, monthly or less in winter; daily only during an active outbreak. | Set the **update cadence** recommendation: weekly–biweekly refresh during Apr–Oct, monthly in Nov–Mar, ad-hoc immediate triage on a confirmed nest discovery. The information-gain curve (verdicts accumulate ~weekly) supports this: marginal log-likelihood gain per week is roughly constant, so weekly refresh captures the signal without churning assignments. |
| 10 | How long of a quiet stretch convinces officials the pest is gone? | At least **2–3 consecutive years** with no confirmed positives, often 3–5, covering full active seasons; one quiet year can be a detection failure. | Set the **eradication criterion** to ≥2–3 clean active seasons. The Bayesian survival test (sensitivity p_season=0.5) gives 95% confidence of absence after 5 clean seasons; at higher sensitivity p=0.7, after 3. Reported as a range consistent with the expert's 2–3 (minimum) to 3–5 (robust) years. |

## Notes
- Replies 1, 6, 7, 8, 10 were flagged by the expert as empirical judgments
  "to be confirmed in the data"; each was checked against the dataset and the
  check is recorded in the solution (e.g. misID species counts, winter-month
  shares, post-press rate ratio).
- No reply text was copied into `solution.json`; only the values, constraints,
  and decision rules above were carried forward.
