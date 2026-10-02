# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence — 2003_C

## Exchange 1
- **Question** (expert_question_1.md): "At a busy US airport, roughly how many checked bags does a typical departing passenger have on average?"
- **Reply** (expert_reply_1.json): about 0.5–0.7 checked bags per departing passenger (roughly half to two-thirds of passengers check at least one bag, a small share check two or more); ~0.6 is a common planning figure. Empirical judgment; varies with carrier business model, route type, season.
- **Effect on work**: set parameter `r = 0.6, interval [0.5, 0.7]` — checked bags per departing passenger. It scales the peak-hour bag load: `L = r * occ * B` (B = seat-slots in the peak hour from table1.csv). Used in Tasks 1, 3, 6 sizing; the [0.5, 0.7] interval drives the best/worst-case split of the EDS recommendation.

## Exchange 2
- **Question** (expert_question_2.md): "Of the checked bags screened, what fraction is it typical that passengers have them checked close to the gate rather than well ahead?"
- **Reply** (expert_reply_2.json): typically 5–15% of checked bags are tendered close to the gate; the large majority are tendered at the counter/curbside well before departure and enter the normal baggage flow. Empirical judgment.
- **Effect on work**: together with Exchange 3, set `f = 0.60, interval [0.45, 0.65]` — the share of peak-hour bags tendered early enough to be screened within the pre-departure window at all (the remainder can be screened in a later window, so it does not load the peak hour). Used in the flow-vs-slot split `L_f = f*L` (Task 1 sizing) and the per-departure slot load in the Task 3 schedule feasibility check.

## Exchange 3
- **Question** (expert_question_3.md): "During a busy peak hour, how many minutes before departure do most passengers finish checking their bags?"
- **Reply** (expert_reply_3.json): most bags are tendered 45–90 minutes before departure (domestic); airlines commonly cut off counter check-in about 30–45 minutes before domestic departure; only a small late fraction arrives within the last 30–45 minutes. Empirical judgment.
- **Effect on work**: set `m = 60, interval [45, 90]` minutes — the pre-departure screening deadline each flight's bags must clear by. It defines the departure-slot capacity in the Task 3 model: a slot of m minutes holds `e * avail * rate * m/60` bags, and the schedule is feasible iff every departure's in-window bag load fits its own slot. It also bounds the effective screening window used in Task 1 (`h = 2 h` per cohort is compatible with a 60-minute clearance deadline plus queue absorption).

All three values enter `code/model.py` as calibrated inputs with their intervals; the full parameter table with sources is in `solution.json`.
