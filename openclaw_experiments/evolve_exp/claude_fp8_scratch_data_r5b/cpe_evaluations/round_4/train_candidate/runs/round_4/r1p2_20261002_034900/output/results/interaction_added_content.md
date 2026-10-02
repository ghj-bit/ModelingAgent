# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence

## Exchange 1 — Data Provenance and Completeness

**Question asked** (written to `logs/operator_feedback/expert_question_1.md`):
> Do most Amazon products keep receiving new reviews for years, or does a
> product's review activity fade quickly after it's launched?

Rationale: profiling showed the three files are not drawn from a common time
window — hair_dryer 2008–2014 (6 yrs), pacifier 2009–2014 (6 yrs), but
**microwave only 1/1/2013–9/9/2013 (8 months)**. The reputation-trend deliverable
depends on whether a within-slice rating slope is a genuine reputation shift or
a launch-ramp artifact, which is exactly the fact this question targets.

**Controller / expert reply:** NOT OBTAINED.
- The controller created `expert_request_1.json` on the first wait.
- The subsequent reply attempt returned
  `{"ok": false, "exchange": 1, "error": "RuntimeError('Direct human-expert API call failed')"}`.
- Re-signalling the question file (fresh writes, cleared stale request/reply)
  and re-running `wait_for_expert_reply.py` produced no further request or reply.

**Effect on the work (honest record):** No expert value was obtained, so no
parameter or constraint was sourced from this exchange. Per policy, I did not
fabricate a reply or substitute an expert sentence. The structural assumption the
question was meant to settle — *is a within-slice trend a reputation signal or a
launch artifact* — is resolved instead **directly from the data**: I compute each
product's review-count and rating-by-month, fit the within-window slope, and
separately flag single-window products (microwave) as "launch-window, trend not
interpretable" rather than trusting their slope. This makes the assumption
empirical and reproducible without the expert reply, and the analysis is
therefore grounded in the supplied data, not in an unverified external claim.

**Status:** Exchange 1 question was posed; the expert reply could not be
retrieved due to a controller-side API failure. The question's underlying concern
was addressed in-data rather than via the expert.
