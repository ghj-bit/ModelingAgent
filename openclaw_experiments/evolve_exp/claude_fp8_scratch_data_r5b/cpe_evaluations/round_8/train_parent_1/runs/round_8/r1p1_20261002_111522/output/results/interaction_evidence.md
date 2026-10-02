# Interaction Evidence

## Exchange 1 — Core structural assumption
Question: In a big tennis match, when one player suddenly starts winning many points in a row, do you feel the other player's effort and confidence really drop, or is a long run of points mostly just chance?

Reply (summarized): runs are mostly structural — service holds make point outcomes streaky even between evenly matched players; a 4–6 point run is routine. A genuine psychological/physiological component exists but is smaller than the run suggests, short-lived (a few points to one game), and often reverses. Treat a run as real only when accompanied by observable markers: rising unforced errors, falling first-serve percentage, slower tempo, or a break of serve.

How it changed the work:
- Constraint adopted: the momentum metric must NOT be based on raw point-run length. It is built from event markers only (unforced errors, double faults, aces/winner ratios, break points converted/missed), each weighted from the data.
- Decay horizon adopted: expert says the real component lasts "a few points or one game" → exponential decay constant set to a half-life of ~4 points (≈ one game), tested via sweep at 3, 4, 6, 8 points.
- The coach's "random" claim is tested against marker-weighted momentum, not run length.

## Exchange 2 — Causal direction
Question: When you see a player losing control of a match, which comes first: the mistakes, or the drop in effort and confidence?

Reply (summarized): mistakes (error clusters, double faults) come first, or at least become visible first; the confidence drop is lagging and often inferred backward from the errors. Caveat: entangled, not a measured ordering; sometimes a player tightens up before errors show.

How it changed the work:
- Directionality rule adopted: in the swing-prediction model, error-cluster features are treated as leading (causal antecedent) and are entered as predictors of the NEXT points, never as responses. The model therefore predicts swings from recent errors, not from recent point wins.
- Test added: a Granger-style lead/lag check — compare predictive accuracy of (a) recent point outcomes vs (b) recent error markers; the latter should dominate, which the data confirm (see task 4 outcome).
- Bias stated explicitly in the submission: correlation between confidence and errors cannot be separated from the data alone; the model claims only predictive, not psychological, causation.

## Exchange 3 — Interpretation threshold
Question: During a live match, how strong a signal of an imminent swing do you need before you'd actually act on it?

Reply (summarized): act only when a cluster of 2–3 independent observable markers coincides (rising UEs/DFs, falling first-serve percentage, tempo change, ideally a break); one marker is a hint, a cluster is a signal; even then the action is modest and reversible; the false-alarm base rate is high.

How it changed the work:
- Decision rule adopted: a "swing alert" is declared only when ≥2 of {error-surge, serve-collapse, break-event} markers fire within the trailing window. Single-marker alerts are suppressed.
- Alert threshold calibrated so the alert rate in the 30-match dataset matches the coach's implied false-alarm tolerance: alerts fire at roughly 5–10% of points (see task 4, precision/recall computed against subsequent sign changes).
- Memo advice to coaches is framed as "adjust tactics modestly when a marker cluster appears", never as a wholesale change of plan, matching the expert's risk framing.
