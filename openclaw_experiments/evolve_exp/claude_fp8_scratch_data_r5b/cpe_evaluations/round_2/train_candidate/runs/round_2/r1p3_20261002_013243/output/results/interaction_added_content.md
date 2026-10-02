# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — 2003_C (MM-Bench / IMA 2004 M: EDS checked-bag screening)

Three expert exchanges, one question each, fixed. Each reply was converted into a model
parameter/constraint before the next exchange; the value and the interval over which it holds are
recorded here. No expert sentence is reproduced verbatim into the submission — only the value,
constraint, or decision rule travels.

---

## Exchange 1 — Dominant operational mechanism

**Question (expert_question_1.md):**
When a large airport's checked-bag screening comes close to its capacity during the morning peak,
what is the first thing that actually breaks in practice, and why?

**Expert reply (paraphrased, full text in expert_reply_1.json):**
The failure is in the bag flow *into* the EDS line, not in the machines themselves. EDS throughput
is the binding constraint but is not smooth: at ~92% availability a machine is down ~8% of the time,
and with a small fleet the survivors must absorb a downed unit's load. Peak bag arrivals are bursty
(banks of departures), so surge demand exceeds effective capacity before the average hour is full.
The queue propagates backward through the baggage system onto ticket counters/curb check-in;
passengers are held and departure banks slip. The system fails at the intake interface because there
is no buffer to absorb the surge and no slack to cover an outage.

**How the reply became work (before Exchange 2):**
- Introduced an *availability-adjusted* per-unit capacity `c = r_thr * r_av` (r_av = 0.92) instead of
  nominal throughput, so a downed unit reduces the effective fleet.
- Introduced the *N+1 outage margin* as a design rule: `N = max(N_min + 1, r_min)`.
- Made the model a *peak-hour* (surge) model, not a daily-average model, because the bursty bank
  arrival is what breaks the system.
- The scheduling task (Task 3) is framed as keeping the instantaneous bag flow under `c` so the queue
  does not propagate to check-in — the exact failure mode described.

---

## Exchange 2 — Operational boundary / threshold

**Question (expert_question_2.md):**
Given that the screening line breaks when one machine is down during a bank of departures: how many
screening machines would airports in your region find acceptable to operate with, knowing one may be
out of service at any moment? And what on the ground signals that the count is no longer adequate?

**Expert reply (paraphrased, full text in expert_reply_2.json):**
Airports treat **N+1 as the minimum acceptable configuration** — enough machines to cover the
peak-hour bag load with one unit out of service. In practice a large facility lands at **3–5 EDS
units at the peak**, not the bare arithmetic minimum of 2. On-the-ground signals that the count is
no longer adequate: (1) bags queuing at check-in/curb rather than at the EDS infeed (queue
propagated backward past the baggage system); (2) departure banks slipping — flights held or bags
left behind; (3) recovery time exceeding the gap between banks — the line never catches up before the
next surge; (4) operators running machines at the top of the 160–210 bags/hr range continuously, with
no margin for a second outage or a slow bag.

**How the reply became work (before Exchange 3):**
- Set `r_nplus1 = 1` (outage margin) and `r_min = 3` (regional floor for a large facility), interval
  [3,5], in the parameter table. For Airports A & B the floor does not bind (N_min ≈ 37–39), but the
  floor is what adapts the model to smaller airports in Task 5 (tiering: 3/2/1 by size).
- The four adequacy signals became Task 4's operational monitoring recommendation (R5): watch bags
  backing up at check-in/curb, banks slipping, recovery time outlasting the bank gap, and machines
  pinned at the top of the throughput range as the early-warning that the deployed count is short.
- The "no margin for a second outage" point reinforced using the conservative r_thr = 175 (not 210).

---

## Exchange 3 — Interpretation of uncertainty / bias

**Question (expert_question_3.md):**
When the screening capacity is calculated from average flight data like Table 1, what should an
airport director watch for so the resulting device count isn't misleading in a real worst-case peak
hour?

**Expert reply (paraphrased, full text in expert_reply_3.json):**
Average-based counts understate real peak need in several ways: (1) averages hide the peak — bags
arrive in banks within the hour, not evenly, so sizing to the average hour leaves the surge
uncovered; (2) cancellations cut both ways — the 2% daily rate reduces average demand but does
nothing for the worst-case hour, so do not net it out of a peak design; (3) load factor, not seats —
bags scale with passengers carried, not seats offered, and the peak flight is typically near-full;
(4) availability is not 100% — the 92% figure means design must cover the peak with one unit out
(N+1); (5) the throughput range — using best-case 210 instead of a conservative 160–180 hides
shortfalls; (6) connecting/transfer bags and oversize items add load not visible in departure counts.
If the count is derived from the average hour at best-case throughput with no outage margin, it is
misleading.

**How the reply became work (after Exchange 3, into the final model and submission):**
- `r_cf = 0.88` (peak load factor, interval [0.80, 0.95]) — bags computed from passengers carried
  (seats × load factor), not seats offered.
- `r_bag = 1.2` (checked bags per seated passenger, interval [0.8, 1.5]) — the dominant demand
  driver; swept 0.8→1.5 (design count 31→47 at A), so it is the largest sensitivity in the study.
- `r_x = 1.02` (extra screened fraction for transfer/oversize/manifest, interval [1.0, 1.05]) —
  the load not visible in the departure counts.
- `r_edt = 0.04` (false-alarm re-examine, interval [0.02, 0.10]) — rework folded into effective
  demand.
- The 2% cancellation is explicitly excluded from peak design (documented in Task 1) as a
  deliberate conservatism; it is reported, not applied, in the parameter table.
- These six caveats became the "limitations and biases" text of Tasks 1 and 3 and the Task 7
  sensitivity ranking (throughput and bags-per-passenger as the highest-leverage parameters).

---

## Provenance note on empirical values

The device parameters (throughput 160–210, availability 92%, ETD 40–50, 98%, accuracies 98.5%/99.7%,
costs $1M/$45k, 20% slice, 10x labor) come from the task problem statement itself. The demand-side
parameters (r_bag, r_cf, r_x) and the design rules (N+1, r_min floor, conservative throughput,
exclude cancellations from peak) come from the three expert exchanges. Two scholarly references
support the bands: DOI 10.1016/j.jairtraman.2019.04.003 (extra-baggage demand, newsvendor framing)
and DOI 10.1257/jep.6.2.45 (US airline load-factor/competition history); the canonical cost-benefit
study for the device-configuration space is DOI 10.1111/j.1539-6924.2006.00736.x. These are cited in
the solution.json parameter table, not from memory.
