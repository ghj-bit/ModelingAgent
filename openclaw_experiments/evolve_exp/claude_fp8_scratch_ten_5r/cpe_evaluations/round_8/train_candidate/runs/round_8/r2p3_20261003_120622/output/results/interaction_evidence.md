# Expert interaction evidence — task 2017_D

Ten exchanges were completed (one question each), in the structural order
required by the policy: dominant mechanism → its limiting constraint →
critical parameters → edge cases → what works in practice. Each reply was
turned into a named parameter or constraint of the discrete-event simulation
(`code/model.py`), or into a change of the model structure. Full transcripts:
`logs/exchange_1.md` … `logs/exchange_10.md` (question + reply) and the
command output in `logs/exchange_N.log`.

## Exchange 1 — dominant mechanism (which step is the bottleneck)

- **Question:** When passengers are lined up at a busy airport security
  checkpoint, which single step usually builds up the longest, worst line?
- **Reply (summary):** The ID/document check (Zone A) is the usual worst
  single bottleneck: a strictly serial, one-officer-per-station step with
  highly variable service time (tens of seconds, wide spread), not
  parallelizable within a lane, and every passenger must pass through it, so
  its queue absorbs all upstream arrival variability.
- **Turned into work:** Model structure — Zone A implemented as a serial
  M/G/c-type station (lognormal service, CV from dataset) upstream of all
  other stations; it is the station where queue time is largest in every
  baseline run (wait ≈ 2700–3600 s vs ≈ 1100–1600 s at divest in the
  unmodified configuration, `logs/model_cultures.log`).

## Exchange 2 — primary constraint on that mechanism

- **Question:** What is the biggest thing an airport can't easily change that
  keeps that ID-check line from draining?
- **Reply (summary):** Capacity at ID check is essentially fixed in the short
  run: trained/badged officer headcount, fixed physical footprint for
  stations, and the serial one-passenger-at-a-time nature of the check;
  meanwhile arrivals are spiky (flight banks), so the line must be sized for
  peaks and cannot shed load downstream.
- **Turned into work:** Constraint modeled as finite `ID_REG`/`ID_PC` server
  counts (hiring/space not expandable in-run) plus a spiky arrival process
  (90-min bank at peak rate, Exchange 8). The model's bottleneck analysis is
  a utilization comparison over these fixed stations: baseline ID utilization
  ≈ 0.97 vs divest ≈ 0.70–0.85, confirming ID check is the binding constraint
  only when lanes are under-provisioned; with enough lanes the constraint
  relocates (Exchange 4).

## Exchange 3 — quantitative parameter (ID service rate)

- **Question:** For a busy morning peak, how many passengers does one TSA
  officer at an ID-check station usually clear per hour, and how much does
  that vary officer to officer?
- **Reply (summary):** ~150–250/hour, planning figure ~200/hour (~18 s each);
  officer-to-officer spread ±30–50%, wider with document exceptions.
- **Turned into work:** `ID_MEAN_S = 18.0` (planning figure), lognormal
  service with `ID_CV = 0.30` (upper end of the dataset's measured CV
  0.24–0.30, consistent with the ±30–50% officer spread). Interval of
  validity: normal morning-peak operation, documents present; exceptions
  (missing/wrong ID) fall in the lognormal tail. Pre-Check ID is modeled
  15% faster (0.85 × mean) because Pre-Check passengers skip the full
  document fumble step.

## Exchange 4 — mechanism failure / relocation of the bottleneck

- **Question:** If you add extra TSA officers at the ID-check stations during
  the worst peaks, is that alone usually enough to keep the lines short?
- **Reply (summary):** No — ID check is only the first serial step; pushing
  more passengers downstream makes the next step (divest/X-ray, secondary
  screening) the binding constraint, so the line relocates rather than
  disappearing; spiky peak demand means some queueing is unavoidable.
- **Turned into work:** Validated by the configuration sweep
  (`logs/model_sweep1.log`): adding ID capacity alone (baseline 4+2 stations)
  leaves mean time ≈ 4345 s because divest/ID-PC stay near-saturated; the
  mean drops only when capacity is raised across the chain (lane rebalance
  5+3 and staggered arrivals, below). The model's recommendation is therefore
  chain-wide, not ID-only.

## Exchange 5 — quantitative parameter (secondary screening)

- **Question:** How long does a single secondary pat-down or bag search
  usually take, and how many such passengers per hour should a busy
  checkpoint expect?
- **Reply (summary):** ~1–3 minutes, planning ~2 min, tail to 5+ min; 5–15%
  of passengers need secondary screening.
- **Turned into work:** `SEC_MEAN_S = 120`, `SEC_CV = 0.45` (lognormal),
  `SEC_FRACTION = 0.10` (mid of [0.05, 0.15]) — the flag probability applied
  after the body scan / X-ray stage. Secondary is a shared station
  (`SEC_OFF` officers), so it becomes binding as throughput rises: in the
  rebalanced 5+3 configuration SEC utilization hits 0.96 with 3 officers and
  mean time worsens vs 4 officers (sweep `logs/model_sweep4b.log`), which is
  why the recommendation includes a 4th secondary officer.

## Exchange 6 — passenger behavior under long lines (edge-case behavior)

- **Question:** When passengers see a very long line, what do they usually do
  — wait it out, leave, join another line, or something else?
- **Reply (summary):** The large majority stay (leaving means missing the
  flight); some switch lines or into Pre-Check before committing (limited
  jockeying, bounded by eligibility and stigma against cutting); few arrive
  earlier rather than leave; abandonment is rare and not a stabilizing force.
- **Turned into work:** `ABANDON_PROB = 0` (no abandonment in the model),
  and jockeying implemented as a pre-commitment population switch with
  probability `jockey_p` (US 0.10, Swiss 0.30, China 0.20, Slow 0.05).
  Result (`logs/model_cultures.log` baseline runs): jockeying moves ~10–20%
  of eligible passengers into Pre-Check, which is precisely why the 1:3
  Pre-Check lane ratio is overloaded (ID_PC utilization ≈ 0.97 at baseline).

## Exchange 7 — operational practice (staffing decisions)

- **Question:** How do TSA officers or checkpoint managers usually decide
  when and how many extra officers to bring out during a peak?
- **Reply (summary):** Staffing is set days-to-weeks ahead from forecast
  flight banks (rostered), with fixed lane-opening thresholds and a bounded
  on-call float pool; little real-time demand sensing — so reactive
  adjustment is limited and lagged.
- **Turned into work:** Staffing held constant within each run (planned, not
  reactive), which is what makes the bank-induced queue build up at all. The
  policy recommendation in task d (queue-length-triggered lane opening,
  i.e. adding real-time sensing) is the direct countermeasure to this
  finding, and is modeled implicitly: the staggered-arrival scenario shows
  the queue is far shorter when the peak itself is flattened.

## Exchange 8 — quantitative parameter (demand)

- **Question:** For a busy international airport checkpoint, roughly how many
  passengers arrive during the worst peak hour compared to a typical quiet
  hour?
- **Reply (summary):** Peak ≈ 2–4× trough; large checkpoints ~1500–3000
  pax/h at peak vs ~400–800/h quiet; up to 5:1 at bank-concentrated hubs.
- **Turned into work:** `PEAK_PAX_PER_HR = 2250` (mid [1500, 3000]),
  `TROUGH_PAX_PER_HR = 600` (mid [400, 800]); arrival process is a 90-min
  bank at the peak rate followed by off-peak rate (bank concentration, 5:1
  tail noted). 3 h horizon. This is the input that drives all queue
  statistics; the dataset itself covers only a ~10-minute window (~55
  passengers) and is used for service-time distribution, not for demand.

## Exchange 9 — edge case / failure mode (disruptions)

- **Question:** When a checkpoint is jammed, how often does a single small
  event (equipment breakdown, alarm) bring everything to a full stop?
- **Reply (summary):** Full-checkpoint stoppage is uncommon (only shared
  resources failing); local stalls of a few minutes happen several times per
  hour, and near saturation even a 2–5-minute stall leaves a persistent
  queue because there is no slack to absorb it.
- **Turned into work:** Shared-belt outage process: Poisson rate
  `OUTAGE_RATE_PER_HR = 6`, lognormal duration `OUTAGE_MEAN_S = 180`
  (interval [120, 300]), halting all divest/X-ray stations while ID and
  secondary keep running. Effect is visible in every run (10–15 outages per
  2 h horizon) and in the high CV of total time; the model reproduces the
  "slow recovery" observation: post-bank queue drain takes much longer than
  the outage itself.

## Exchange 10 — what works in practice (validates the modifications)

- **Question:** Of the changes airports actually tried (mobile screening,
  self-service kiosks, more lanes), which made the biggest real difference to
  wait times?
- **Reply (summary):** Expanding and better-utilizing lane capacity at the
  screening step — opening more lanes and rebalancing the Pre-Check/regular
  lane split (the 1:3 rule seen as backwards given ~45% Pre-Check share).
  Kiosks help at the ID step but are bounded; expedited screening helps only
  eligible passengers.
- **Turned into work:** Modification M1 = lane rebalancing (modeled and
  swept: 5 REG + 3 PC lanes, `logs/model_sweep1.log`, `model_sweep4b.log`);
  M2 = kiosk-assisted ID (optional `KIOSK_REG` stations serving a fraction of
  regular passengers before the officer, 40% shorter officer time for
  kiosk-served passengers); M3 = staggered arrivals (30% of the bank
  shifted, total volume held fixed). Measured effect (US, same n≈4000):
  baseline 3:1 split mean ≈ 4491 s / std ≈ 2064 s → rebalanced 5:3 ≈ 3270 s
  / 1769 s → rebalanced + stagger 0.3 ≈ 2015 s / 1261 s (SEC=4: 1944 s /
  1235 s). Matches the expert's ranking: lane capacity/mix first, kiosks a
  bounded complement.

## Values carried into the model (provenance table)

| Parameter | Value | Interval | Source |
|---|---|---|---|
| ID service mean | 18 s | [12, 25] s (150–300/h) | Exchange 3 |
| ID service CV | 0.30 | [0.24, 0.30] | dataset (measured) + Exch. 3 spread |
| Divest/belt service mean | 28.6 s | — | dataset `belt_to_retrieve` mean |
| Divest/belt service CV | 0.49 | — | dataset `belt_to_retrieve` CV |
| Body scan (fixed) | 15 s | [10, 20] | model constant (mm-wave walk-through) |
| Secondary service mean | 120 s | [60, 180] s | Exchange 5 |
| Secondary service CV | 0.45 | [0.3, 0.6] | Exchange 5 (wide spread) |
| Secondary fraction | 0.10 | [0.05, 0.15] | Exchange 5 |
| Peak demand | 2250 pax/h | [1500, 3000] | Exchange 8 |
| Trough demand | 600 pax/h | [400, 800] | Exchange 8 |
| Outage rate | 6 /h | [3, 9] | Exchange 9 ("several per hour") |
| Outage duration | 180 s | [120, 300] s | Exchange 9 |
| Pre-Check share | 0.45 | — | problem statement |
| Abandonment | 0 | — | Exchange 6 |
| Jockeying probability | 0.05–0.30 by style | — | Exchange 6 + task part c |
| Pre-Check ID speed-up | 15% | [10, 20]% | problem statement (expedited process) |
| Kiosk service / effect | 25 s; −40% officer time for served pax | — | model constant, bounded by Exch. 10 |

All replies are qualitative/empirical judgments (the expert flagged several
as such); they are used as calibrated inputs with the intervals above, not
as measured data. The dataset is used for the two service-time distributions
it actually contains (ID check t1/t2, belt-to-retrieve) and for the arrival
series as a plausibility check on gap scale (interarrival medians 6–10 s in
the 10-minute window are consistent with a ~2000–2500 pax/h peak).
