# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence (2021 MCM Problem C)

Ten exchanges, one question each, all run through `code/wait_for_expert_reply.py`
(request/reply JSON in `logs/operator_feedback/`). For every exchange: the
question (verbatim), the reply, and the concrete effect it had on the model
(workflow rule: only values, constraints, and tests travel from a reply into
the solution — reply text is never copied into `solution.json`).

---

## Exchange 1 — size of the insect
**Question:** "People reporting a giant hornet sighting often say how big it was. What size (in inches or cm) do real Asian giant hornets typically reach, and how do ordinary wasps they get mistaken for usually compare?"
**Reply (substance):** the pest is about 1.5–2 inches (3.5–5 cm); lookalikes top out around 0.75–1.5 inches; the closest in size is the European hornet.
**Effect:** set the size thresholds in `code/vespa_features.py` (`size_ge_2in` at ≥1.5 in, `size_le_1in` at ≤1 in) and the numeric-size regexes (inches and cm); the feature `size_large_word` and the numeric size features enter the logistic model as the only text evidence of size.

## Exchange 2 — lookalike species
**Question:** "In the Pacific Northwest, which ordinary wasps or hornets do people most often mistake for a giant hornet, and how do they look compared to it?"
**Reply (substance):** most common confusions are European hornet, bald-faced hornet, yellowjackets, paper wasps, cicada killers, and digger wasps; the orange-yellow head is the key diagnostic that separates the pest.
**Effect:** built the species lexicon (`sp_european_hornet`, `sp_bald_face`, `sp_yellowjacket`, `sp_paper_wasp`, `sp_cicada_killer`, `sp_digger_wasp`, `sp_wood_wasp`, generic hornet/wasp/bee markers) and the `ctx_orange_head` pattern in `code/vespa_features.py`.

## Exchange 3 — specimens vs. photos
**Question:** "When someone finds or kills the insect and reports it, is a dead specimen usually enough for officials to tell exactly what species it was?"
**Reply (substance):** an intact dead specimen is nearly definitive for species ID; a photo is suggestive but not conclusive.
**Effect:** motivated the attachment-type features in the logistic model (`ctx_dead`, `ctx_captured` text markers; `n_photos`, `has_video` attachment counts) and the triage priority rule (specimen > photo) used in Part D.

## Exchange 4 — spatial spread bound
**Question:** "Once a single giant hornet is confirmed in an area, how far from it can the next nest be reasonably expected to appear?"
**Reply (substance):** queens can disperse up to about 30 km, but most new nests appear within a few kilometers of the parent.
**Effect:** (a) set the MLE grid for the spatial kernel range in `code/vespa_spread.py` Part B to R ∈ [5, 60] km (bracketing the 30 km dispersal bound, fitted value R = 21 km); (b) justified using nearest-confirmed-positive distance (`dist_pos_km`) as the leading spatial feature of the logistic model.

## Exchange 5 — response times
**Question:** "If the state gets a new giant-hornet sighting report, roughly how quickly can investigators usually start checking it, and how often do they re-review the report list?"
**Reply (substance):** field response takes days to about two weeks; the report list is re-reviewed weekly to monthly.
**Effect:** fixed the revisit cadence for the model-updating protocol in Part 4 (weekly re-scoring of the report queue, monthly re-estimation of model parameters).

## Exchange 6 — reporting surges
**Question:** "After people report a giant hornet in their area, do neighbors tend to report more insects there afterward, and does that extra reporting last for a while?"
**Reply (substance):** yes — awareness drives a local surge in reports of all large wasps; the surge decays over weeks to months.
**Effect:** motivated the decaying publicity-shock regressors in `code/vespa_spread.py` Part A (half-life 2 weeks, 8-week support, shocks at the 2019-09 BC confirmation and the 2020-07 Blaine viral reports); also motivates the caveat that report counts measure attention, not infestation.

## Exchange 7 — seasonality and fall clues
**Question:** "In the Pacific Northwest, when are giant hornets actually seen flying, and how do people who see one in fall usually describe what they found?"
**Reply (substance):** active July–November with peak Aug–Oct; fall sightings are often "the size of my thumb," ground nests, or activity near hives with large bee losses.
**Effect:** defined the `in_season` (Jul–Nov) and `is_fall` (Aug–Oct) indicators in `code/vespa_model.py`, and the fall-clue context features (`ctx_ground_nest`, `ctx_honey_bee_hive`, `ctx_multiple`, `ctx_dead`, `ctx_captured`, `ctx_attack_bee`).

## Exchange 8 — feedback to reporters
**Question:** "When officials can't confirm a giant hornet and just close the report, do reporters usually notice that, and does the state publicly confirm when a hornet area is finally cleared?"
**Reply (substance):** generally no — there is no per-report feedback to the public, and no per-area closure notices.
**Effect:** justified treating the 2,342 "unverified" rows as *unlabeled* rather than negative — they are the population to score, not training data — and it rules out using reporter behavior as a label signal.

## Exchange 9 — persistence and eradication norm
**Question:** "Do giant hornets tend to return to the same area year after year, and roughly how many seasons would pass with nothing found before people there could really consider it gone?"
**Reply (substance):** populations can persist for several years; the working norm is roughly three clean seasons (a 2–4 season range).
**Effect:** set the persistence parameter `p_p` in the Part E eradication sweep and provided the external check that the computed 2–4 season rule matches the ~3-season expert norm.

## Exchange 10 — triage practice
**Question:** "When state agencies have limited staff, what do they look at first to decide which new insect sighting reports to check immediately?"
**Reply (substance):** the practical order is specimen/photo evidence first, then location (proximity to known nests), then timing (in-season), then description details.
**Effect:** validated the Part D policy — rank by the logistic score (which embeds location and timing) and override toward reports carrying specimen or photo evidence; the top-20 prioritized list is reported with attachment counts to show the two criteria agree.
