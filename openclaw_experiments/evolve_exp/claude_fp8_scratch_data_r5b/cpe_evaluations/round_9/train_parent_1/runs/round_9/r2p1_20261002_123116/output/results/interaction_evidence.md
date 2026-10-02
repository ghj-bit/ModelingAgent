# Expert Interaction Evidence — MM-Bench 2021_C (Vespa mandarinia report triage)

Three exchanges, one question each. Each reply became a concrete parameter,
constraint, or decision rule in `code/build_model.py`; no reply text is copied
into the submission.

## Exchange 1 — Operational mechanism of report arrival

**Question (expert_question_1.md):** "Do reports of a new hornet sighting arrive
as a steady, even trickle, or in sudden bursts after news spreads and people
start looking?"

**Reply (summary):** Bursts, not a steady trickle. Public-report data of this
kind is event-driven: volume spikes after media coverage, official
announcements, nest discoveries/destructions, or the start of a seasonal
"hornet watch," then decays. Two consequences: (1) arrivals are not a
constant-rate Poisson process — expect overdispersion/clustering, so a
non-homogeneous or self-exciting process is more appropriate; (2) the
*submission* date, not the detection date, carries the burst signal, and the
lag between them is informative.

**How it changed the work (concrete):**
- Arrival model: built a **non-homogeneous Poisson with decaying exponential
  impulses** (rate `λ(t)=λ_floor + Σ a·exp(-(t−t_k)/τ)`) at each confirmed
  submission day, fit on a τ grid {5,10,20,30,50,100}, and compared AIC against
  a homogeneous Poisson. This is the model in section "arrival" of the
  submission.
- Used **Submission Date** (not Detection Date) as the arrival clock, and kept
  `lag_days = Submission − Detection` as a feature and as the informative
  delay.
- Eradication test: the "quietness" window must span a post-news *season*, not
  just days (burst logic) — stated as an assumption in the eradication section.
- Update cadence: event-triggered refit after any confirmed positive, on top of
  a monthly seasonal floor.

**Caveat reported honestly:** with only 14 confirmed submissions, AIC favored
the homogeneous model (113.1 vs 134.5), so the burst structure is asserted by
domain logic (this reply) but under-powered in the data; I report both.

## Exchange 2 — Causal hierarchy / dominant driver of a true ID

**Question (expert_question_2.md):** "When the lab confirms a report, what
single thing makes them most confident it really is the giant hornet?"

**Reply (summary):** A clear, close-up photograph (or physical specimen)
showing the diagnostic features — large orange head/eyes, broad orange-and-
black banded abdomen, ideally with a size reference. A confirmed specimen or an
unambiguous image beats any written description, because text notes are
subjective and often describe generic "big hornet" features shared by
look-alikes.

**How it changed the work (concrete):**
- The classification model treats **image/specimen availability** (`n_imgs`,
  `n_files`, video) and **proximity to a confirmed cluster** as first-class
  features, not mere metadata — this matches the expert's "image beats text."
- **Ablation test** (section "classif.ablation_no_image") quantifies the
  contribution of the image features by refitting without them and comparing
  ROC-AUC / PR-AUC, so the claim is checked, not asserted.
- Text (TF-IDF on Notes) is kept but positioned as a *secondary* signal, and
  its positive-weight terms (specimen, caught, live, captured) are reported as
  the textual proxy for "something was actually collected," consistent with
  the expert's logic.

## Exchange 3 — Decision-relevant uncertainty threshold

**Question (expert_question_3.md):** "If your model ranks reports to
investigate, how wrong can it be before you'd stop trusting it?"

**Reply (summary):** No universal number; it depends on base rate and cost
asymmetry. Positives are rare (a few percent), so a ranking model is only
useful if it concentrates positives far above the base rate in the top-ranked
tier. Stop trusting it when top-decile/top-N precision falls to roughly the
base rate (i.e. no better than random). Working rule: the model is worth
acting on only if it lifts precision to at least *several times* the base rate
in the tier you can actually investigate; also distrust it if precision is
unstable across time/geography (fitting the news-burst artifact) or if errors
are systematically the costly kind (false negatives on genuine positives).

**How it changed the work (concrete):**
- Defined the **decision-relevant success metric** as *lift of expected
  positives over the true base rate* in the top-C tier actually investigable:
  `lift(C) = E[positives caught in top C] / (C · p̂_base)`, with
  `p̂_base = 0.0067` (Wilson 95% CI [0.004, 0.011]). This is the table in the
  prioritization section.
- The model is declared **trustworthy** because lift ≈ 14–27× base rate across
  all capacities C ∈ {10,20,50,100} — well above the "several times" bar.
- Added the **false-negative emphasis**: recall of 1.0 on the holdout (all 3
  holdout positives retrieved) is reported as the guard against the costly
  error the expert flagged.
- Added the **stability check**: score correlation between two half-data
  refits (0.94) and a temporal holdout, to guard against fitting the
  news-burst artifact.
