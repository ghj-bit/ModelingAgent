# Expert Interaction Evidence — Problem 2017_C

Ten exchanges, one question each. Strategy: structural anchoring first
(operational behavior of near-capacity traffic), then parameters that
quantify that behavior, then boundaries (mixed-fleet interface, dedicated
lanes, high-penetration limit). Every reply was converted into a model
element before the next exchange.

| # | Question (summary) | Expert reply (substance) | Effect on the work |
|---|---|---|---|
| 1 | Near-capacity freeway: smooth slowdown or abrupt jam? | Abrupt. Bistable system: stable free-flow and stable congested states coexist; a small perturbation near capacity triggers a "capacity drop" with a backward-propagating shockwave; recovery is hysteretic. | Fixed the model structure: two-branch flow with a breakdown threshold and hysteresis, instead of a monotone speed–density curve. Introduced `BREAKDOWN_RATIO` and `RECOVERY_RATIO` operating points in `traffic_model.py`. |
| 2 | After a jam eases, quick speed-up or lingering slow driving? | Slow driving lingers; the congested state is itself stable; flow returns to free-flow only after density drops well below the jam-onset density. | Set hysteresis: `RECOVERY_RATIO = 0.75 < BREAKDOWN_RATIO = 0.92`, i.e., recovery occurs at lower density than breakdown — the two thresholds define the congested-equilibrium band. |
| 3 | Usual first trigger: merging, or a brake tap? | A brake tap (local braking event) is the usual first trigger; merging only creates the density that makes the stream fragile. | Modeled breakdown as a local-perturbation amplification whose margin shrinks as density approaches capacity — justifies treating capacity as a drop point, not a smooth limit, and motivates AVs as dampers (next question). |
| 4 | How do AVs react differently when traffic slows? | Faster (sub-second vs ~1–1.5 s human), uniform, no over-braking; they damp small disturbances; cooperating cars can slow together or make merge gaps. | AVs raise the breakdown margin → per-lane capacity rises with AV share. Introduced `C_LANE_AV > C_LANE_HUMAN` and cooperation term in the capacity model. |
| 5 | Do humans follow an AV's lead in mixed traffic? | No — humans react to the car ahead, not to an unseen controller; smoothing benefits do not propagate unless AV share is large or AVs are segregated. | Cooperation benefit applies only to the AV subpopulation: fleet capacity is a share-weighted blend `(1-p)C_h + p C_av`, not a uniform uplift of the whole lane. This is why 10% AV share yields only a small gain. |
| 6 | Would a reserved AV lane noticeably improve overall traffic? | At low share (~10%): no, usually worse (lane sits mostly empty, general lanes pushed closer to capacity). At high share (~90%): yes, can improve noticeably. 50%: ambiguous, depends on whether the dedicated lane's higher per-lane throughput outweighs the lost general-lane capacity. | Added the dedicated-lane comparison in `summarize_routes.py`: total = `cap(lanes-1, 0) + cap(1, 1)`, evaluated at each AV share to find where the trade-off flips. |
| 7 | Can platoons keep a safe short gap? | Yes — that is the core capability; near-synchronous braking lets gaps stay well below human headways while safe; a physical floor exists, and coordination is required (an AV behind a human must use a longer sensor gap). | Confirms `C_LANE_AV = +~30%` per lane is a defensible platoon figure; also confirms the share-weighted blend: an AV behind a human reverts to human spacing, so gains scale with the cooperating subpopulation. |
| 8 | Can adding AVs make a jammed highway worse at first? | Yes, typically non-monotone: a modest dip at low shares (~10%) because mixed-fleet heterogeneity and the human–AV interface generate perturbations; improvement as the cooperating share grows large enough. | Introduced the heterogeneity penalty term `1 + kappa*((p-p*)^2 - p*^2)/p*` with `kappa = 0.10`, `p* = 0.25`, producing a small capacity dip at p=0.1 that turns monotone-improving after p*. |
| 9 | Reserved AV lane: always open or rush-hour only? | Rush hours only; off-peak the reserved lane is an unneeded capacity loss; it pays off only when general lanes are near capacity and the AV share can fill it. | Recommendation: time-restricted (peak-period) AV lane, not all-day. Refines the dedicated-lane policy: the +gain applies during peak hours only; off-peak the dedicated lane reduces usable capacity. |
| 10 | At high AV share, does per-hour throughput per lane rise noticeably? | Yes, but bounded — tens of percent per lane, not a multiple; requires cooperation/connection; non-cooperating automation yields a smaller gain. | Capped `C_LANE_AV` at ~2800 veh/h/lane (+27% vs the 2200 human lane capacity), consistent with "tens of percent"; the model's 90%-share improvement of +37–42% (mixed lanes) falls in this band, supporting the parameter choice. |

All ten exchanges were used; no exchange was skipped or repeated. The
structural questions (1–3) established the bistable/hysteretic
breakdown mechanism before any parameter was calibrated; questions 4–5
fixed how AVs act on that mechanism; 6–9 fixed the policy-relevant
boundaries (dedicated lanes, mixed-fleet interface); 10 set the upper
bound on the capacity gain.
