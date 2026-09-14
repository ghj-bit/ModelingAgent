---
name: reconcile-static-dynamic-models
description: Reconcile analytical, equilibrium, or steady-state results with finite-horizon, nonstationary, or simulation results. Use when a solution presents both model classes but transfers conclusions between them without a quantitative scope comparison.
---

# Reconcile Static And Dynamic Models

## Applicability Gate

Use when two model views describe the same requested outcome at different temporal or structural scales. Abstain when the models answer different subproblems and no cross-model claim is made.

## Workflow

1. Map variables, units, initial conditions, horizon, arrival or forcing process, and performance estimands between the two models.
2. State which analytical assumptions the dynamic model violates or relaxes.
3. Create a bridge case where both models should agree, then verify agreement within numerical and sampling error.
4. Compare the target scenario using matched metrics and uncertainty. Separate transient, nonstationary, boundary, and finite-horizon effects.
5. Test whether the final decision remains unchanged, requires an adjustment, or is valid only in a stated operating region.
6. Give each model a clear role: explanation, fast approximation, optimization, stress testing, or operational prediction.
7. Propagate the reconciliation into model scope, results, limitations, and recommendations.

Use a bridge case that disables the dynamic feature: constant forcing instead of
time-varying forcing, a long horizon after warm-up instead of a short transient,
or fixed controls instead of adaptive controls. Agreement in this case validates
the metric mapping before differences in the target case are interpreted.

## Generalization Examples

- **Inventory control:** Compare a steady-state reorder approximation with a
  daily finite-horizon simulation. First use constant demand as a bridge case,
  then quantify seasonality and start-up effects on stockout risk and the chosen
  reorder point.
- **Transportation:** Reconcile an equilibrium assignment with a time-stepped
  congestion simulation. Match demand, travel-time definition, and network state;
  explain whether peak transients change the recommended capacity expansion.
- **Population dynamics:** Compare an equilibrium population level with a
  seasonal stochastic simulation. Verify convergence under constant conditions,
  then report how seasonal forcing changes extinction risk and management advice.

## Required Evidence

- Crosswalk of assumptions, metrics, and units.
- Agreement check on a shared bridge case.
- Quantitative target-case comparison with uncertainty or error bounds.
- Explicit decision-level reconciliation.

## Stop Rules

- Do not compare unlike metrics or unmatched horizons.
- Do not call two values comparable without a numerical criterion.
- Do not force agreement when the models intentionally estimate different quantities.
