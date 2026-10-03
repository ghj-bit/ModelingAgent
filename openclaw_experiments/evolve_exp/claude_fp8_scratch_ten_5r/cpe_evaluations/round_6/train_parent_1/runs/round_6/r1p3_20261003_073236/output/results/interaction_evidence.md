# Interaction Evidence — Problem 2017_D (TSA checkpoint)

10 expert exchanges, one question each, each reply turned into model work before the next exchange.
Files: `logs/operator_feedback/expert_question_N.md` / `expert_request_N.json` / `expert_reply_N.json`.

| # | Question (abridged) | Reply (gist) | How the reply was used |
|---|---|---|---|
| 1 | Longest lines: too few lanes or slow bin sorting? | Lane availability dominant; per-passenger divest time secondary, binding only when nearly all lanes already open. | Fixed structural topology: bottleneck = screening stage (open lanes), not the belt. Modification 1 (dynamic lane opening) targets it. Queueing analysis centered on utilization of screening lanes. |
| 2 | Open extra lane first or speed up existing lanes? | Open lanes first if staffing permits; urge pace only as secondary. | Supervisor decision rule in simulation: open a lane when queue length crosses a threshold and a spare officer exists; this is the control law for the "flex lanes" policy. |
| 3 | Typical peak lane count at a very busy US airport? | ~10–20 regular lanes at peak (largest checkpoints ~20–30 total incl. Pre-Check). | Calibration of baseline scenario: L=12 regular, 4 Pre-Check lanes in base case; sweeps run L=8,12,16,20. |
| 4 | Fraction of bags flagged for secondary search? | 1–3% flagged at belt, mostly resolved at belt; side-room escalation well under 1% of all passengers. | Zone D parameters: flag rate p=0.02 (sweep 0.01–0.05); belt-resolve fraction 0.9 (add ~40 s); side-room fraction 0.05 of flags (add ~180 s). |
| 5 | Duration of a routine pat-down? | 1–3 min routine (longer if escalated). | Zone D pat-down service time d_p=120 s, uniform [60,180], used when scanner alarm (p≈0.03). |
| 6 | Typical share of Pre-Check travelers? | ~45% (problem statement), range 40–50%. | Arrival split: 45% Pre-Check / 55% regular (sweep 35–55%). |
| 7 | Arrival swing morning rush vs midday? | Peak 5–8 a.m. ≈ 2–4× the midday rate; driven by banked departures. | Time-of-day arrival profile λ(t): base 0.7 pax/min, ×2.5 morning bank 5–8 a.m., ×1.8 evening bank 3–7 p.m., ×0.6 midday lull. |
| 8 | Second line build in late afternoon? | Yes, second bank 3–7 p.m., broad, comparable or slightly lower than morning. | Confirmed evening bank in λ(t); simulation day 5:00–21:00 captures both peaks. |
| 9 | Frequency of short arrival bursts (cluster 10–30 within ~1–2 min)? | Occasional, a few times per hour at peak; absorbed as transient spike unless staffing thin. | Burst superposition on arrivals: at peak hours, Poisson bursts of 10–30 every ~15–30 min; used to generate the high-variance tail in wait time and to test queue-buffer (buffer of pre-divested bins) robustness. |
| 10 | Do lines keep steady order or do people switch lanes often? | Mostly steady FCFS; lane switching rare, only when a lane is faster, directed by officer, or lane opens/closes. | Queue discipline FCFS, no spontaneous lane hopping in baseline; lane switching modeled as minor perturbation for the "individual-efficiency" cultural variant (low rate), not the dominant dynamic. |

No reply was copied into the submission; the values above are used as calibrated inputs, recorded with their interval and source (this exchange) in the parameter table of `results/solution.json`.
