# Interaction-Attributed Content

This arm starts from the problem statement alone, so there is
nothing to diff against. The run's own record of the exchange is
reproduced below; treat the reported change as its account of the
work, not as a controller-computed diff.

# Interaction Evidence

Three expert exchanges, one question each, sequenced to resolve the model's
core structural assumption, its causal mechanism, and the decision-relevant
uncertainty threshold. Question -> reply -> how the reply changed the work.

---

## Exchange 1 — Core structural assumption: what makes a patch usable

**Question** (`expert_question_1.md`):
> For Florida scrub lizards, how much of the scrub area they live in is
> typically bare open sand?

**Reply** (`expert_reply_1.json`): Open sand is typically a minority of a
patch, on the order of 10–40% bare, the rest under scrub oak / rosemary /
palmetto / shrub cover. Patches below roughly 5–10% open sand are unsuitable;
the best habitat has a substantial open-sand component (~20–40%). Empirical
judgment, not a measured constant.

**How it changed the work:**
- Added the constant `SAND_FRAC_MIN = 0.05` to `code/model.py` as the
  lower bound on the open-sand fraction of a suitable patch.
- The carrying-capacity / density function `dens_of(size, sand)` is forced to
  0 for any patch whose `sand/size < SAND_FRAC_MIN` (no usable substrate).
- Task 5 viability: a patch below the sand floor is classed **unsuitable**.
- The interval over which it holds: expert-stated range 5–10%; the model uses
  5% as the hard floor and the sweep `--sweep SAND_FRAC_MIN=0.10,0.20`
  re-runs the burning policy at the upper end of the range to show sensitivity.
  Source: expert exchange 1.

---

## Exchange 2 — Causal mechanism: what happens when the sand disappears

**Question** (`expert_question_2.md`):
> You said below about 5-10% open sand makes a patch unsuitable. What happens
> to a lizard in a scrub patch whose open sand has disappeared under dense
> thick growth?

**Reply** (`expert_reply_2.json`): The lizard is effectively lost from that
patch. Scrub lizards are obligate users of bare sand for basking, egg-laying
(females bury clutches in loose sand), and open-ground foraging / predator
escape. When sand is overgrown, those functions vanish: no nesting substrate,
no basking sites, shaded cluttered ground. Result is **local extirpation**,
not mere density reduction. Adults may persist briefly in shrinking remnants,
but with no successful recruitment the population declines to zero. Adults do
not migrate, so an overgrown patch cannot be rescued by immigration — only
juveniles disperse, and they move out of, not into, a degraded patch. Such a
patch becomes a demographic sink or is unoccupied.

**How it changed the work:**
- Established the causal direction: loss of open sand -> loss of nesting and
  basking habitat -> recruitment collapse -> local extinction, a one-way
  process (not a reversible density change). This is why the model treats a
  patch that cannot replace itself (Leslie eigenvalue λ < 1) as a **sink**
  rather than a simply "smaller" population.
- The non-migratory adult rule is encoded directly: the model has no adult
  immigration term, so a sink patch's population only decays — matching the
  expert's "cannot be rescued" statement. Task 4's juvenile migration
  probability is therefore a one-way (juvenile-only) dispersal kernel, and the
  landscape model does not add adult rescue to any patch.
- Task 5 outcome framing: "suitable" means the patch is self-sustaining
  (λ ≥ 1) *and* has adequate sand; "marginal" means adequate sand but a sink
  (λ < 1) — occupied only transiently by juvenile immigrants, not viable
  long-term. Source: expert exchange 2.

---

## Exchange 3 — Decision-relevant threshold: what counts as a healthy population

**Question** (`expert_question_3.md`):
> For scrub patches that still support lizards, how many animals per hectare
> would you say is a healthy, self-sustaining local population?

**Reply** (`expert_reply_3.json`): In good habitat, a healthy
self-sustaining local density is roughly 10–50 lizards/ha, best open-sand
patches at the upper end, marginal patches at the low end. Densities below
about 5–10/ha generally indicate a patch too sparse or too small to be
reliably self-sustaining. Empirical judgment from typical survey densities,
not a precise constant.

**How it changed the work:**
- Added the constant `DENS_SUSTAIN = 5.0` lizards/ha as the lower bound of
  the self-sustaining density band.
- Task 5: the model's fitted densities (27–76 lizards/ha across the 29
  patches) are compared against this band. Every patch in the landscape sits
  at or above the ~10/ha lower end of the healthy band, so density alone does
  not disqualify a patch; the binding constraint for viability is the
  self-replacement rate (λ) and the sand fraction, which is consistent with
  the expert's framing that the *low end* of the band (marginal patches) is
  where the risk lies. The density check therefore acts as a floor, not a
  ceiling, and the λ ≥ 1 self-sustainability test is the decisive viability
  criterion. Source: expert exchange 3.

---

## Notes on use of the replies

No reply text was copied into the submission. The three replies contributed
exactly three calibrated inputs — `SAND_FRAC_MIN = 0.05` (exchange 1), the
sink / no-adult-rescue rule (exchange 2), and `DENS_SUSTAIN = 5.0` lizards/ha
(exchange 3) — each recorded in `code/model.py` with the exchange as its
source, and each used in a place the model actually computes with them. All
other numbers in the submission come from the task's own four datasets.
