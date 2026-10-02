# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — Problem 2015_C (ICM Human-Capital Churn)

Three fixed exchanges were run, one question each, sequenced so each builds on the
previous reply. Questions were asked in plain language (no modelling terms), and each
reply was turned into a concrete model parameter or decision rule before the next
exchange.

## Exchange 1 — anchor for σ and the churn-diffusion mechanism

**Question (expert_question_1.md):** "In ICM's table, salaries are written as multiples of a
company median income (σ), e.g. senior managers at 8σ. Which job level does that median
income σ actually correspond to?"

**Reply (paraphrased):** σ is the pay of a mid-career individual contributor (front-line /
experienced-worker level), not a supervisor or manager. Because most of the 370 positions sit
in the non-supervisory ranks, the company-wide median falls in that band; the problem's own
CEO-to-median ratio of ~10 is consistent with this.

**How the reply was used:** The experienced-employee salary cell was a bare σ in the raw CSV
(its only value). Exchange 1 confirms that cell is the company median, so the cleaned dataset
sets experienced-employee salary = 1.0σ and treats the whole sheet as "multiples of σ" with
σ itself being the experienced-worker pay. This anchors every monetary quantity in the model
in units of σ without needing an absolute dollar value — consistent with the problem's
stated convention that decisions are made in relative σ. It also validates the level-aggregated
pay structure (σ ≈ 1.0 at level "Experienced employee", rising to 8σ at Senior manager).

## Exchange 2 — hiring capacity / boundary condition under a churn surge

**Question (expert_question_2.md):** "If a third of all positions fell empty at once, could the
company realistically refill them within a year, or would some stay vacant? Roughly how long?"

**Reply (paraphrased):** No — filling ~90 of 370 vacancies in a year is not realistic. ICM
already runs at ~85% filled and is actively hiring only 8–10% of positions (~2/3 of
vacancies), so steady-state external throughput is roughly 30–37 hires/year. Front-line roles
fill in ~1–3 months, supervisory/managerial roles in 4–9+ months, with a long tail beyond a
year for mid-level and specialized roles.

**How the reply was used:** This gave the model two hard constraints that were missing from the
data and that the naive model violated:
1. A **company-wide external-hiring cap** (~30–37 external hires/year, plus internal promotions
   which add no net headcount). Without it, the model let a surge be absorbed instantly.
2. A **per-level recruitment lead time (pipeline lag)** taken from the data's "median time to
   recruit" column (1–7 months), so a vacancy opened in month 0 is not filled until its lead
   time elapses. The model was calibrated so the *observed* 18% churn (36% at mid-level, 2×
   average) is balanced at the current 85% fill — i.e., 85% is the steady state and the churn
   scenarios (25%, 35%, 30%-mid-level) are perturbations of it.

## Exchange 3 — decision-relevant uncertainty threshold (what "filled" means)

**Question (expert_question_3.md):** "What share of positions filled is generally considered
healthy for a company, before managers start feeling the real pain of understaffing?"

**Reply (paraphrased):** Healthy fill is in the mid-90s percent (~95–97%). Below about
90–92% managers feel real operational pain (redistributed work, overtime, uncovered critical
roles). ICM's 85% is already chronically understaffed; the problem's 80% target would be a
staffing crisis.

**How the reply was used:** This set the **productivity-pain threshold** in the model:
productivity is full above a 92% fill ratio and degrades linearly (slope 0.5) below it. It also
defines the decision framing for Task 4 — "sustaining 80%" is treated as a *crisis* level
(well below the healthy band), so the answer distinguishes "still above 80%" from "in a
staffing crisis." It separates planning-level insight (the 85%→83% drift at 25% churn is
manageable) from an operational trigger (falling below ~90% = pain, below 80% = crisis).

## What did NOT happen

No exchange produced neither a parameter nor a decision rule. All three replies were
integrated: (1) σ anchor → data value; (2) hiring cap + lead time + steady-state calibration →
model constraints; (3) pain threshold → productivity rule and decision framing. The expert's
sentences were not copied into the submission; only the values, constraints and thresholds
travelled into the model.
