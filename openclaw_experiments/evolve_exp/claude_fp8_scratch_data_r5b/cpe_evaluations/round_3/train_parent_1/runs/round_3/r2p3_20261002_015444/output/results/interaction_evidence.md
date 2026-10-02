# Expert Interaction Evidence — Problem 2003_C

## Exchange 1

**Question** (`expert_question_1.md`):
When passengers board a commercial flight, what fraction of the seated passengers typically check at least one bag? Give a rough share, not a precise figure.

**Reply** (paraphrased): Roughly half to two-thirds of seated passengers check at least one bag. Domestic leisure routes run higher (50–70%); short-haul business-heavy or low-cost-carrier routes run lower (30–50%). A reasonable central estimate for modeling is about 50–60%. This is an empirical judgment, not a precise figure.

**How the reply became work**: The reply supplied the check-share parameter p = 0.55, interval [0.50, 0.60], which is the dominant empirical input to the bag-load model (Task 1). It enters as `B = seats * p * bags_per_checker * (1 - cancel)`. The interval [0.50, 0.60] is the basis of the sensitivity sweep over p in `code/model.py` (`--sweep 0.50,0.55,0.60`), which shows the EDS count spanning 16–20 (A) and 17–21 (B) across the band. The source is recorded in the parameter table of `solution.json` (Task 1, `mathematical_modeling_process`).

## Exchange 2

**Question** (`expert_question_2.md`):
At a busy airport screening hall, when one device is down for maintenance, do operators simply slow down the whole line, or do they keep other units running at full speed? Which happens in practice?

**Reply** (paraphrased): Operators keep the remaining units running at full speed and absorb the outage by letting queues build; they do not throttle the working machines. The line is a parallel-server system: throughput is set by the number of functioning units, not by a synchronized line speed. If the outage is long enough, bags are held or diverted to other lines.

**How the reply became work**: The reply confirmed the parallel-server structure that the capacity-matching model (Task 1) assumes: the effective throughput is `N * r * o` where o = 0.92 is the per-machine availability, and a down machine reduces throughput by a direct fraction rather than slowing the working machines. This is the structural assumption behind `N = ceil(B / (r * o))` — the division by the per-machine effective rate, not by a synchronized line speed. It also justifies the spare-machine recommendation in Task 4: because a down machine is a direct throughput loss (not a coordinated slowdown), the correct hedge is an extra machine, not a slower schedule. The source is recorded in Task 1's `task_analysis` (assumption 3) and Task 4's `mathematical_modeling_process`.

## Exchange 3

**Question** (`expert_question_3.md`):
When a baggage scanner needs a routine maintenance check, is the whole peak hour disrupted, or is that work done off-peak or staggered among the machines?

**Reply** (paraphrased): Routine maintenance is normally scheduled off-peak or staggered among machines, not done during the peak hour. Units are taken out of service during low-traffic periods (early morning, late evening, overnight) or one at a time so the remaining units cover the load. The realistic peak-hour disruption is unplanned breakdowns, not routine maintenance — which is why models treat availability as a random ~92% (EDS) / ~98% (ETD) uptime rather than assuming a scheduled peak-hour outage. This is standard operational practice.

**How the reply became work**: The reply confirmed that the 0.92 EDS availability factor in the model represents random unplanned breakdowns during the peak hour, not a planned maintenance outage. This justifies using `o = 0.92` as a random-availability multiplier on the throughput (`r * o`) rather than as a scheduled-capacity reduction (which would require fewer machines to be running for a planned fraction of the hour). It also supports the Task 4 recommendation to schedule routine maintenance off-peak or staggered, so that the peak-hour model's random-availability assumption is operationally consistent. The source is recorded in Task 1's `task_analysis` (assumption 5) and Task 4's `mathematical_modeling_process` (recommendation 4).
