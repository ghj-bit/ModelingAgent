# Interaction Evidence — MCM 2019 C (opioid NFLIS + Census)

Three expert exchanges, one question each. Each reply is converted below into a
concrete model parameter, constraint, or decision rule (not copied verbatim
into the submission).

## Exchange 1 — Data provenance
**Question (expert_question_1.md):** The NFLIS file lists OH, KY, WV, VA and
Pennsylvania, but the problem names Tennessee. Which counties should the model
treat as the fifth state?
**Reply (paraphrased, expert_reply_1.json):** Treat Tennessee as the fifth
state; the file's Pennsylvania listing is a data-file discrepancy. Use the five
named states; flag the PA block as the substitute for TN.
**Turned into work:**
- The pipeline keys the five state-blocks on the internally-consistent
  `FIPS_State` column (not the `State` letter labels, which are internally
  inconsistent with the FIPS codes and with real geography).
- Mapping applied in `pipeline.py` (`FIPS_STATE_LABEL`): FIPS 39→OH, 21→KY,
  54→WV, 51→VA, 42→TN. The FIPS-42 block (labeled "PA" in the file, county
  names ALLEGHENY/BLAIR/BERKS/ADAMS = real PA counties) is reported under the
  named fifth state "TN" and the discrepancy is flagged as a data-integrity
  limitation in `subtask_outcome_analysis`.
- Consequence: the modeled region is the five named states; the 5th-state
  records are the FIPS-42 block.

## Exchange 2 — Structural assumption (counts vs prevalence)
**Question (expert_question_2.md):** Do lab-reported drug-identification counts
track actual opioid use, or police enforcement activity?
**Reply (paraphrased, expert_reply_2.json):** They mainly track enforcement /
reporting activity (cases opened, seizures submitted, lab coverage), i.e. a
proxy for detected/supplied presence × enforcement intensity, confounded by
lab-reporting coverage — **not** a prevalence measure. Cross-county/cross-year
comparisons are only meaningful if enforcement and reporting are roughly stable.
**Turned into work:**
- Constraint: absolute county counts are not prevalence. The model therefore
  normalizes every county rate by county population (Census total population,
  column DP02_0001) to express "per 100,000 residents" rates, which removes
  the size confound and is the fairest cross-county comparison available.
- The trend / relative-spread analysis (which county grew fastest, when a
  county started, the synthetic→heroin transition) is reported as a
  *relative* detection signal, and the caveat that a heavy-enforcement,
  light-use county reads high (and vice versa) is carried into the
  limitations. Population denominators come from the supplied Census files.
- The model is not over-claimed as a prevalence / mortality model; it is a
  "detected-supply + enforcement" diffusion model, matching the data's actual
  meaning.

## Exchange 3 — Interpretation threshold (outbreak definition)
**Question (expert_question_3.md):** What single-year rise makes a county read
as a genuine new outbreak rather than noise?
**Reply (paraphrased, expert_reply_3.json):** No clean cutoff, but an empirical
judgment: a ~2–3× year-over-year jump (≈ +100%–200%) *sustained* into the next
year reads as a real outbreak; below ~+50% is ordinary fluctuation. Two
qualifiers matter more than the multiple: (a) base size — in small counties a
ratio jump can be a handful of cases, so require a meaningful absolute
increase; (b) persistence — a true outbreak stays elevated 2+ years, a one-year
spike that reverts is a reporting/enforcement artifact.
**Turned into work (becomes the outbreak-detection decision rule):**
- Parameter: outbreak ratio threshold `R = 2.0` (lower bound of 2–3×), with a
  sensitivity band up to 3.0 (reported via a `--sweep` of R).
- Constraint (absolute floor): a county only counts as "outbreaking" if the
  absolute increase also clears a floor scaled to the state median, so a
  handful-of-cases doubling in a small county is not flagged. Implemented as
  `abs_increase >= max(10, 0.10 * state_median_level)`.
- Constraint (persistence): the elevated level must be sustained in the
  following year (level_t >= 0.75 * level_{t-1} at the elevated year), so a
  single-year spike that reverts is reclassified as an artifact.
- These three rules are applied to the per-100k synthetic-opioid series to
  detect new outbreak counties (Part 1 "where use started" and "future
  thresholds"), and the threshold is swept in `model.py`.

## Files
- Questions: `logs/operator_feedback/expert_question_{1,2,3}.md`
- Request/reply (controller-owned): `logs/operator_feedback/expert_{request,reply}_{1,2,3}.json`
- Model consuming these: `code/pipeline.py` (mapping, population normalization),
  `code/model.py` (outbreak rule, R sweep), Census join in `code/census.py`.
