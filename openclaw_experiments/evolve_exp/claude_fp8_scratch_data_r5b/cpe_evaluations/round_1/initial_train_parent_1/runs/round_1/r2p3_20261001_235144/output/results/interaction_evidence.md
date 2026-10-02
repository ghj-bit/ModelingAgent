# Expert Interaction Evidence

Three exchanges, one question each. Each reply was turned into a concrete
model constraint before the next exchange.

## Exchange 1

**Question (expert_question_1.md):** On a busy freeway like I-5 through King
County, during a peak-hour jam, do drivers actually change lanes and follow one
another closely, or do they keep wide gaps and mostly stay in their own lane?

**Reply (summary):** Peak-hour flow is high-density, short-headway,
platoon-following; headways shrink to roughly one-to-two car lengths in a jam;
lane-changing is frequent but constrained; wide gaps are essentially absent in
a true jam.

**How it changed the work:** Confirmed the baseline regime is high-density
(Greenshields) rather than free-flow. This is why the model uses a
Greenshields fundamental diagram with a *calibrated jam density* and a
service-limit volume-to-capacity ratio, and why the peak-hour demand is a
fraction of the daily ADT (peak factor) rather than the ADT itself. The
dominant-queue (capacity-constrained) interpretation of VCR >= 1 is grounded
in the jam state the expert described.

## Exchange 2

**Question (expert_question_2.md):** Would people be willing to drive much
closer to the car in front if it were self-driving, or do they keep a big
cushion no matter what?

**Reply (summary):** The gain is concentrated in self-driving-following-
self-driving pairs, where gaps can shrink substantially. Human-following-CAV
cushion shrinks only modestly; CAV-following-human actually *enlarges* the gap.
In mixed traffic, expect little net headway reduction.

**How it changed the work:** This is the key constraint. It justifies the
sub-linear mixing law C(p) = C0 (1 + a p^b) with b < 1 (default 0.85): the
capacity benefit is *not* proportional to the CAV share because most pairs are
still human-human or human-CAV. It also explains why the model predicts
dedicated lanes do **not** help at 10–50% penetration (a converted human lane
costs more than the CAV-CAV gain recovers) and why the gain only becomes large
near 90%. Sensitivity: b = 0.6 vs 0.85 vs 1.0 shifts the 50%-share VCR between
1.02 and 1.06, so the conclusion (tipping near 50–70%) is robust to the exact
exponent.

## Exchange 3

**Question (expert_question_3.md):** If most cars were self-driving and could
travel closer together, would the biggest improvement show up on the busiest,
slowest stretches, or matter equally everywhere?

**Reply (summary):** Biggest on the busiest, slowest (capacity-constrained)
stretches, not everywhere. Headway reduction converts to throughput only where
the road is the binding constraint. Caveats: the gain is largest where
congestion is recurrent and demand-driven, not at hard bottlenecks (merges,
ramps, incidents); and the benefit scales with local penetration.

**How it changed the work:** Justifies reporting results per segment and
flagging the network bottleneck (I-405, VCR 1.22 at p=0) as the place to act
first, rather than assuming a uniform benefit. It also shapes the
interpretation: the model's "capped segment" count is the demand-driven
congestion measure the expert described, and the caveat that a hard bottleneck
cannot be relieved by closer upstream following is carried into the
limitations (the macroscopic model cannot separate merge/ramp bottlenecks from
demand saturation on the given data).
