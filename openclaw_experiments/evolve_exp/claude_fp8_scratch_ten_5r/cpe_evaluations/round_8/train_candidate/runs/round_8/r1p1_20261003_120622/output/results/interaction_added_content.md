# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Expert Interaction Evidence — MM-Bench 2003_C

Ten exchanges. Policy: structural anchoring before numerical filling; mechanism →
constraint → parameter → edge case. Each reply was converted into a model
parameter, constraint, or decision rule before the next question.

## Exchange 1 — Structural: what defines the bottleneck
**Q:** In practice, is the screening bottleneck set by the one hour with the most
bags, or by making sure bags finish before each flight's check-in closes?
**Reply (abridged):** The per-flight check-in cutoff (30–45 min before departure)
is the binding constraint, not the peak-hour total. Bags arrive spread across the
check-in window; the operative constraint is cumulative screening capacity keeping
pace with cumulative bag arrivals feeding each flight's cutoff.
**Effect on work:** Set the binding constraint = per-flight deadline (30–45 min
pre-departure cutoff), not peak-hour throughput. Peak hour retained only as a
stress condition on that deadline.

## Exchange 2 — Constraint: what stops spacing out departures
**Q:** Airlines can space out departure times to smooth bag arrivals. What usually
stops them from spacing flights far apart in the peak hour?
**Reply (abridged):** Runway/slot scarcity, connecting-bank structure, demand
peaking, competitive slot capture, and tight crew/aircraft rotations force
departures to cluster; the airport cannot force wide spacing.
**Effect on work:** Model departure clusters as fixed (cannot be freely smoothed).
Scheduling (Task 3) therefore optimizes over the fixed cluster, not by spreading
flights arbitrarily.

## Exchange 3 — Constraint: which failure mode misses deadlines
**Q:** With departure clusters fixed by slots, which usually matters more for
missing screening deadlines: bags arriving too fast for lanes, or broken scanners
slowing the lines?
**Reply (abridged):** Scanner reliability matters more — it is stochastic, ~1 in
12 devices down (92%), and a mid-peak failure removes 160–210 bags/hr with no
warning, creating a queue that misses several flights' cutoffs. Arrival surges are
a predictable planning problem.
**Effect on work:** Reliability, not arrival rate, is the dominant risk driver.
Sizing must treat a mid-peak EDS failure as the governing stress case.

## Exchange 4 — Parameter: how to survive a mid-peak failure
**Q:** To survive a scanner dying mid-peak, do airports usually buy an extra spare
unit, or rely on faster service during that hour?
**Reply (abridged):** Buy a spare / hold a hot standby. EDS throughput is fixed by
the machine and cannot be dialed up; labor cannot speed a CT scanner. The standard
practice is to size the fleet with one more unit than the peak workload requires.
**Effect on work:** Added a mandatory +1 spare EDS on top of the peak-hour
requirement. Service rate held at nominal (not raised).

## Exchange 5 — Parameter: checked-bag fraction
**Q:** On a typical packed domestic flight, roughly how many checked bags show up
per seat, on average?
**Reply (abridged):** About 0.5–0.7 checked bags per seat, planning figure ≈0.6;
varies with route type and season.
**Effect on work:** Set bags per seat ρ = 0.6, interval [0.5, 0.7]. Bag volume
per flight = seats × ρ × (1 − 0.02 cancellations).

## Exchange 6 — Parameter: arrival window
**Q:** For a flight, over roughly how many hours before departure do its checked
bags show up at the screeners?
**Reply (abridged):** About 2–3 h pre-departure, heavily front-loaded into the
last 60–90 min; check-in opens 3–4 h out, cutoff 30–45 min.
**Effect on work:** Front-loaded arrival profile: most bag volume concentrates in
the final ~1.5 h. Used peak_frac = 0.5 (half of daily bag volume in the busiest
hour) as base, swept 0.4–0.6 to bound the result.

## Exchange 7 — Parameter: nominal rate meaning
**Q:** Do the stated bags-per-hour figures for these machines already include the
extra manual checks of flagged bags, or is that separate?
**Reply (abridged):** Separate. 160–210 (EDS) and 40–50 (ETD) are raw machine scan
throughput, not end-to-end cleared-bags rate. Flagged bags go to manual
resolution downstream, so effective cleared rate is lower and the gap widens with
the alarm rate.
**Effect on work:** Treated nominal rates as machine capacity and applied a
derating factor f to effective cleared rate (base 0.95, swept 0.90–1.00).

## Exchange 8 — Parameter: alarm / false-positive rate
**Q:** Of the bags a CT scanner alarms on, what fraction are false alarms that end
up needing a manual look?
**Reply (abridged):** Roughly 95–99% of EDS alarms are false alarms; the alarm rate
on scanned bags is on the order of a few percent, so essentially all pulled-aside
bags need a manual look or re-scan.
**Effect on work:** Set EDS alarm rate = 0.04 (few percent), swept 0.03–0.05.
Manual-resolution load driven by false positives; ETD stage-2 load = alarms +
mandated dual-screen fraction.

## Exchange 9 — Edge case: consequence of a mid-peak failure
**Q:** When a scanner does fail mid-peak, is the usual result one missed flight,
or several flights' bags piling up?
**Reply (abridged):** Several flights pile up — the outage hits multiple flights
with overlapping check-in windows; clearing the backlog takes time, so the
disruption spans more than one flight's cutoff.
**Effect on work:** Governing stress case = peak arrival rate with one EDS down
and the accumulated backlog still queued. This is why the +1 spare is required
for the whole cluster, not just one flight.

## Exchange 10 — Structural (Task 6): EDS vs ETD arrangement
**Q:** When bags must go through both the CT scanner and the trace machine, do
they run one after the other on each bag?
**Reply (abridged):** Yes, sequential. Two-stage line: EDS first, then ETD if the
bag alarms or is in the mandated dual-screening fraction. The slower stage (ETD,
40–50/hr) sets the dual-screened rate; ETD workload is driven by the EDS alarm
rate plus the mandated fraction, not all bags.
**Effect on work:** ETD modeled as a sequential downstream stage (capacities do
not add). ETD units sized for (alarms + dual fraction) at the slower ETD rate;
ETD does not replace EDS — it adds a stage-2 requirement.

## Notes
- No reply text was copied into solution.json; only the values, constraints, and
  decision rules above were integrated, each cited to its exchange.
- Empirical parameters sourced to exchanges 5, 6, 7, 8 are listed in the
  parameter table of the solution's mathematical_modeling_process field.
