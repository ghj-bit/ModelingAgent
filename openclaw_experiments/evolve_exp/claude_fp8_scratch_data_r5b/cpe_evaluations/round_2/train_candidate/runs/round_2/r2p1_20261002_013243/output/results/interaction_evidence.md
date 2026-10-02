# Interaction Evidence — 2015_C (ICM Human-Capital / Churn Model)

Three exchanges were run. Each reply is recorded, and the concrete way it entered
the model is stated. No expert sentence is copied into the submission.

## Exchange 1 — dominant mechanism
- Question (expert_question_1.md): what makes someone leave next — bad experience,
  coworkers leaving, or a better job?
- Reply (expert_reply_1.json): all three act, but ranked (1) coworker-departure /
  contagion, (2) dissatisfaction (stuck mid-level, poor fit), (3) external
  opportunity. Dissatisfaction is the predisposing condition; contagion is the
  proximate trigger; opportunity is the enabling condition.
- Used in work: the churn model separates a baseline (intrinsic) departure rate by
  level from a contagion term that multiplies a level's churn when its close ties
  have left. Dissatisfaction enters as an elevated base rate for the three
  middle-management levels (matching the stated 2× turnover), not as the diffusion
  driver. This is the causal hierarchy of the equations in task 2.

## Exchange 2 — boundary / saturation
- Question (expert_question_2.md): how many leavers before a stable employee
  seriously considers quitting?
- Reply (expert_reply_2.json): no sharp threshold; a range. ~3–5 departures among
  close ties over a short window shifts a stable employee to active
  consideration; below ~2–3 it is absorbed; above ~5–6 in ~a year it compounds and
  becomes self-reinforcing. Two conditions matter more than the count: the leavers
  must be close ties, and clustered in time.
- Used in work: the contagion intensity is made a function of the number of
  recently-departed close ties, with a soft response that is small for 1–2,
  steepens through 3–5, and saturates/compounds beyond ~6 within a rolling ~1-year
  window. The rolling window is why churn is modeled quarterly. The "compounding
  beyond 5–6" becomes the positive-feedback term that, in scenario 4, drives the
  system toward collapse when the base rate is high.

## Exchange 3 — interpretation / signal vs artifact
- Question (expert_question_3.md): in a small firm, how to tell a real spreading
  trouble from a few unrelated quits?
- Reply (expert_reply_3.json): look at the edges, not the count. A real cluster =
  leavers form a chain/clique in the informal network (each was a close tie of a
  prior leaver or shared workgroup/supervisor) and are clustered in time. Coincidence
  = network-distant leavers, differing reasons, spread over time.
- Used in work: the model's "churn risk" output is defined per node from its
  connected leavers (edges), not from the company-wide count. The model reports a
  contagion index = (fraction of close ties that left recently) and flags a
  "spreading" signal only when the index exceeds a background level AND the leavers
  are mutually connected within the window. This is the signal/artifact rule that
  task 5 (middle-manager contagion) and the results-interpretation sections rely on.
