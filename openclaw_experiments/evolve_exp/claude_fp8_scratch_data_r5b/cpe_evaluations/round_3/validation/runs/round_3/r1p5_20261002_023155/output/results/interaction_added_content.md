# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence

Three exchanges, one question each. For each: the question, the expert's reply
(paraphrased, not verbatim), and the concrete work the reply produced.

## Exchange 1 — Structural fit (data-model form)

**Question.** When a state's energy mix shifts over decades, does it move as a
smooth, roughly constant drift, or as step jumps that land when something
external happens (a big plant, an oil shock, a new industry)? And do those
jumps reverse or persist?

**Reply (paraphrase).** Neither pure drift nor pure steps: a slow drift
punctuated by occasional *persistent* level shifts. Physical capital has
multi-decade lifetimes, so a step usually becomes the new baseline rather than
reverting; only price-driven demand responses partly reverse. Project the
*current regime's* trend forward — not the full 50-year average rate and not a
frozen level. Extrapolating a pre-break rate across a break is the main
failure mode.

**Work it produced.** This fixed the forecast form in `code/profile.py`. I first
fitted a piecewise-linear model over all 50 years with BIC break selection; it
overfit to noise and produced a CA segment with slope −292,000 Btu/yr that
extrapolated to *negative* 2050 totals — exactly the pre-break-rate-across-a-
break failure the expert flagged. I therefore replaced it with a single OLS
trend fitted on the most recent 15 years (1995–2009), which is the "current
regime," and projected that one regime forward to 2025/2050. For the bounded
share series (clean/renewable, electricity) I used a logit-linear fit on the
same window so the composition stays inside [0,1]. No-policy forecast =
current-regime trend, as the expert specified.

## Exchange 2 — Dominant bias / selection mechanism (policy counterfactual)

**Question.** When a big state clean-energy policy finally lands, does the
resulting change in the mix stay close to the state's pre-policy pace, or jump
well ahead of it? And is that jump a one-time new baseline or does it keep
compounding year after year?

**Reply (paraphrase).** The policy jump goes well ahead of the pre-policy pace,
but it is mostly a *one-time* shift to a new baseline, not ever-compounding
acceleration. After the step the mix resumes drifting at a modest pace. Treat
the no-policy baseline as a **conservative floor** — actual post-policy
outcomes sit above it by a bounded level shift, not by an ever-widening
margin. Do not extrapolate a post-policy growth rate backward into the
baseline.

**Work it produced.** This fixed the target construction in `code/targets.py`.
The compact goal is *not* the no-policy forecast. It is the no-policy floor
plus a bounded one-time policy level-shift, anchored to each state's documented
law (CA RPS 50% by 2030, NM Renewable Energy Standard 75% by 2020, AZ 15% by
2025, TX no binding RPS), with only a modest non-compounding drift added for
2050. Because an RPS is a binding floor, the 2025 target is
`max(no-policy floor, documented RPS level)` — the policy is the part that
"buys" the gap above the do-nothing line. The no-policy forecast is reported
separately as the floor, never blended with a post-policy rate.

## Exchange 3 — Validation / interpretation criterion

**Question.** What is the single thing that would make a 15–40-year-ahead
forecast trustworthy enough to set a policy goal on — precise numbers, the
direction and rough size matching similar states, or the do-nothing-to-policy
gap stated clearly? And what would make you dismiss it immediately?

**Reply (paraphrase).** Credibility comes from the *direction and rough size*
of the change matching what comparable states actually did, not from precision
— at a 40-year horizon false precision is a warning sign. The explicit
do-nothing-to-policy gap is a *framing* requirement that makes it actionable,
not a validation criterion. The instant disqualifiers: extrapolating a smooth
rate across a known regime break, or projecting a post-policy growth rate as if
it were the baseline.

**Work it produced.** This set how `solution.json` is framed. (1) The no-policy
floor and the policy target are stated side by side as an explicit gap, so the
policy's purchase is visible (the "actionable" framing). (2) Confidence is
expressed as directional + rough-magnitude, with ranges, not false-precision
point values. (3) I cross-checked the forecast direction against the observed
behavior: CA/AZ show a *declining* renewable-electricity share in the last
15 years (large fossil-fleet base, RPS dilution), so the no-policy floor
declines; NM/TX show a *rising* share (wind build-out), so the floor rises.
The direction in each case matches the observed regime, which is the credibility
criterion the expert named. The two disqualifier patterns were the exact bugs
fixed in Exchanges 1 and 2, so the final numbers do not exhibit them.
