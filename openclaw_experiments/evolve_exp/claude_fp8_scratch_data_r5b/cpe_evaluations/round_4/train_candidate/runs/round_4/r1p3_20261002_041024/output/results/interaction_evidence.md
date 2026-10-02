# Interaction Evidence

Expert channel status: the human-expert API was down for the entire run. All three
exchanges were attempted at the prescribed points, in order, each building on the
state of the previous exchange; every attempt returned
`RuntimeError('Direct human-expert API call failed')` (exchange 1, reply file
`expert_reply_1.json`) or a controller timeout with no request/reply file created
(exchanges 2 and 3). No expert sentence is therefore used anywhere in the
submission, and no value below is attributed to an exchange. Per the policy
("an exchange that produces neither [a parameter nor a code change] did not
happen"), each question is recorded here with the assumption it was meant to
test, and that assumption is instead sourced from the task dataset or a staged
retrieval.

## Exchange 1 — Data provenance and completeness
- Question (`expert_question_1.md`): "Why do the officer, X-ray, and belt time
  records stop partway through the day, and do the early, fully recorded hours
  represent a normal operating period?"
- Reply: FAILED — `expert_reply_1.json` = `{"ok": false, "error":
  "RuntimeError('Direct human-expert API call failed')"}`.
- Effect on work: none from the expert. The representativeness question was
  instead resolved from the data itself: the recording is one continuous 9h55m
  window (00:00→09:55); arrival rates are flat (0.07–0.10 pax/min) until
  minute ~520, then burst to 0.17–0.26 pax/min, and the sensor gaps begin in
  that same late window — so the gaps mark missing peak-period data, not a
  routine sampling artifact. Service-time parameters are therefore estimated
  per column from all available rows (n = 7–39), and the peak-period
  arrival rate is estimated separately from the tail and used as the
  sensitivity input.

## Exchange 2 — Key structural assumption
- Question (`expert_question_2.md`): "When lines back up at a checkpoint, does
  the slowdown tend to clear on its own, or does it usually keep building until
  staff add lanes?"
- Reply: FAILED — controller never produced `expert_request_2.json` /
  `expert_reply_2.json` (wait command timed out at the 70 s cap on two
  attempts).
- Effect on work: none from the expert. The assumption it was meant to test —
  whether a congestion episode is self-clearing at the observed staffing — was
  instead resolved empirically: the body-scan queue depth grows from a mean of
  2.5 (first 10 arrivals) to 12.5 (last 10), and the x-ray-side queue proxy
  from 1.6 to 33.5, with no decay anywhere in the window despite arrival rates
  only doubling. Congestion at observed staffing is not self-clearing; the
  model's base case is therefore an unstable (rho → 1) queue, and every
  proposed modification is evaluated on whether it restores rho < 1.

## Exchange 3 — Interpretation context for uncertainty
- Question (`expert_question_3.md`): "What is the longest security line you
  would be willing to stand in before deciding you had lost your flight?"
- Reply: FAILED — controller never produced `expert_request_3.json` /
  `expert_reply_3.json` (wait command timed out at the 70 s cap).
- Effect on work: none from the expert. The decision-relevant threshold was
  instead set from the task's own framing (risk of missing the scheduled
  flight) and standard airport practice: a 45-minute gate cutoff is used as
  the miss-flight risk horizon (retrieved, see parameter table in
  solution.json), and model results are reported as the probability that
  total wait exceeds that horizon, plus the variance (std) of wait — the
  two quantities the task asks to reduce.
