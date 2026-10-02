# Interaction evidence — MCM 2017 C (Problem 2017_C)

## Exchange 1

**Question** (`logs/operator_feedback/expert_question_1.md`):
"You have ridden these Seattle-area freeways at rush hour. Do the heavy traffic
counts on the spreadsheets reflect what actually jams the roads, or do drivers
spread their trips over time to dodge the rush?"

**Reply** (summary of `logs/operator_feedback/expert_reply_1.json`): the ADT
figures are a 24-hour total but the jamming is driven by the peak-hour share;
on these corridors the peak-hour volume is roughly 8–12% of ADT, and the peak
direction in the peak hour reaches about 2,000–2,400 vehicles per lane per
hour — at or above practical freeway capacity (~2,000 pcphpl). Drivers do shift
some trips, but commuting is time-anchored so the peak stays sharply
concentrated; the heavy counts are consistent with real congestion, not an
artifact of trip spreading.

**How the reply was turned into work:**
- Calibration: peak-hour factor f = 0.10, interval [0.08, 0.12], source:
  exchange 1. Used as the ADT→peak-hour conversion in `code/model.py`
  (demand q_lane = ADT·f·d/(100·lanes)).
- Validation design: since the counts are a 24-hour total, the model is built
  to compare peak-hour **demand per lane** against per-lane **capacity**, with
  capacity at the practical-capacity level (c0 = 2,000 vphpl, see parameter
  table), and the congestion test is per segment at the lane level — not a
  daily flow comparison that would be an artifact of trip spreading.
- Sensitivity: f swept over [0.08, 0.12] (see `logs/run/model.log` sweep
  block); tipping points move with f, so conclusions are stated over that
  interval.

## Exchange 2

**Question** (`logs/operator_feedback/expert_question_2.md`):
"When connected self-driving cars ride shoulder to shoulder in one platoon, do
they take up noticeably less road space than the same number of ordinary cars?"

**Reply** (summary of `logs/operator_feedback/expert_reply_2.json`): yes,
noticeably but moderate — connected cars follow at ~0.5–1.0 s headways versus
1.5–2.0 s for humans, often cited as ~1.5–2× vehicles per lane per hour in a
platoon; the car footprint itself does not shrink, and at low speeds/dense
queues the saving largely disappears (the gain comes at speed).

**How the reply was turned into work:**
- Calibration: platoon per-lane capacity multiplier m = 1.5, interval
  [1.5, 2.0], source: exchange 2. Mixed-traffic per-lane capacity in
  `code/model.py`: c_mix(p) = c0·(1 + α·p)·(1 − g_pen·p), with α = 0.5
  (so full-share mixed capacity ≈ 1.5·c0, i.e. at the low end of the
  exchange-2 range) and g_pen = 0.15 (residual dispersion penalty from the
  humans still in the mix; swept [0.10, 0.20]).
- The exchange-2 caveat "gain comes at speed, vanishes in queues" is encoded
  as the distinction between the **fleet-only** platoon multiplier (m = 1.5–2.0)
  and the **mixed-traffic** uplift (α·p, capped below m): the dedicated-lane
  test uses the fleet-only capacity while the mixed corridor uses c_mix.
- Sensitivity: α swept [0.4, 0.5, 0.7] and g_pen [0.10, 0.15, 0.20]
  (`logs/run/model.log`); the I-5/I-405 no-tipping result is robust across
  all 24 sweep combinations.

## Exchange 3

**Question** (`logs/operator_feedback/expert_question_3.md`):
"If one extra lane were reserved only for the connected fleet, what rush-hour
gain on I-5 would convince you that it was worth stealing from other drivers?"

**Reply** (summary of `logs/operator_feedback/expert_reply_3.json`): a dedicated
lane must carry **more people per hour than the general lane it displaced**,
not merely move its own cars faster; a general-purpose lane at rush hour moves
~2,000 vehicles/h ≈ 2,400–2,800 people/h at 1.2–1.4 occupancy, so the
convincing figure is on the order of 3,000–4,000+ people/h; below that the lane
is a net loss for the corridor.

**How the reply was turned into work:**
- Decision rule implemented as the HBO test in `code/model.py`
  (`dedicated_lane_test`): a dedicated lane is "worth" iff
  min(c0·(1+α·p), p·q_lane0)·occ ≥ min(q_lane0, c0)·occ, i.e. its person
  throughput meets or exceeds the displaced general lane's person throughput
  (q_lane0 = corridor-weighted vphpl at p = 0; occ = 1.25, interval
  [1.2, 1.4], source: exchange 3).
- Result (`logs/run/model_dedicated.log`): under fleet-priority demand the
  test is NOT met at p = 0.10 or 0.50 on any corridor; at p = 0.90 it is met
  only on I-405 (2,728 vs 2,500 people/h), and still not on I-5 (2,159 vs
  2,399). This is the model's answer to "under what conditions should lanes be
  dedicated."
