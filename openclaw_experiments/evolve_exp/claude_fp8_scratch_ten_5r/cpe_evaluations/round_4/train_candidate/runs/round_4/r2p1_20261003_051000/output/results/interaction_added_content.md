# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — Task 2024_C (MM-Bench, Wimbledon momentum)

Ten exchanges, one question each, each reply turned into a model input/constraint
before the next question was asked.

## Exchange 1
Q: When a player is behind badly, what is the single biggest signal they are about to play better again?
Reply: Serve-hold quality (easy, low-stress holds; first-serve % and free points on serve) is the leading turnaround indicator.
How it affected the work: became the `hold_ease` feature in predict.py (fraction of p1's trailing 3 service games won without a deuce) and the primary coach advice. Computed per match; for 2023-wimbledon-1701 it is a live mid-match signal.

## Exchange 2
Q: How many hours into a long five-setter does energy/concentration most often drop?
Reply: ~2.5–3.5 h, i.e. late 4th into 5th, after ~200+ points; gradual, not a sharp threshold; earlier for older/heat.
How it affected the work: set the fatigue boundary in model.py — the `time` feature (normalized point index) is the fatigue proxy, and the 200+ point mark is the domain-of-validity edge for the decay-based momentum. For the 2023 final (334 points) this maps to the 4th/5th-set window.

## Exchange 3
Q: Under pressure in a tight service game, what to focus on to avoid double-faulting?
Reply: Commit fully to the first serve — high-percentage target, same rhythm on both serves, "play the point not the score".
How it affected the work: grounds the serve-advantage weighting in model.py (b = break bonus, first-serve points weighted higher). For 1701, p1's first-serve win rate 0.702 vs second-serve 0.500 and 7 double faults confirm the first-serve-commitment advice is data-supported.

## Exchange 4
Q: Serve under attack — higher first-serve % or more aces?
Reply: Percentage over power; aces are a low-percentage gamble that feeds attackable second serves.
How it affected the work: justifies modeling aces as rare +2 severity rather than a primary lever; coach advice prioritizes first-serve in-rate over aces.

## Exchange 5
Q: Missing break chances — first fix?
Reply: Aggressive, deep, controlled return (take it early, aim deep/center) rather than passive deep position.
How it affected the work: informs the return-depth feature context; for 1701, return_depth was ND 60%/D 40% for both players, supporting the "go deeper on return" advice.

## Exchange 6
Q: After a bad stretch — change routine or keep doing the same?
Reply: Keep the process, narrow focus to one controllable cue; change the plan only for a genuine tactical pattern.
How it affected the work: coach advice framing — stability of process over reactive change; supports the EWMA (smooth) formulation of momentum rather than a reactive one.

## Exchange 7
Q: Older vs much younger — who loses the edge first in a long match?
Reply: The younger player usually retains speed/recovery/shot quality longer; the older player's edge goes first (absent fitness exceptions).
How it affected the work: the key structural factor for the 2023 final (Alcaraz 20 vs Djokovic 36). Used to interpret the 5th-set swing toward Alcaraz and to advise the older player's fatigue window.

## Exchange 8
Q: Most common mistake by the trailing player once the match is back on their side?
Reply: Over-hitting — chasing aces/winners, shortening points, raising UE rate; instead keep the disciplined process that produced the turnaround.
How it affected the work: predicts the post-turnaround UE spike as a model check; the `winners_aces6` and `UE6` features in predict.py capture this. Advice: do not try to finish in one game.

## Exchange 9
Q: Serve-based vs return-based edge — which is more durable?
Reply: Strong serving is the durable base; return-based success is higher-variance and more fragile.
How it affected the work: supports weighting serve-based points (own-serve holds) as the stable momentum component and break points as the volatile, higher-severity component in the EWMA.

## Exchange 10
Q: Preparing for a new opponent — single data point studied first?
Reply: The opponent's first-serve percentage and hold rate — most stable, self-controlled, dictates match structure, transfers across matches.
How it affected the work: the generalization rule for the coach memo — compute each opponent's first-serve % and hold rate as the primary prep metric; the model's hold_ease feature is the in-match analog.
