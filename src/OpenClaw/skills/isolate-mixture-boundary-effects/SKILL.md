---
name: isolate-mixture-boundary-effects
description: Separate theoretical mixture or regime-switching effects from transition, censoring, thinning, and boundary implementation artifacts. Use when pooled stochastic results differ from within-regime behavior or an aggregate discrepancy is attributed to changing regimes.
---

# Isolate Mixture And Boundary Effects

## Applicability Gate

Use when observations are pooled across regimes, segments, states, periods, or populations and transitions can alter observed samples. Abstain when the process has one homogeneous regime or boundaries cannot affect observation construction.

## Workflow

1. Define the observation unit and derive the correct mixture weights. Distinguish time weights, event weights, exposure weights, and sampling weights.
2. Derive aggregate moments or a reference distribution for an ideal mixture without transition mechanics.
3. Generate an independent pure-mixture control at the same sample size as the production result.
4. Tag transition-crossing observations in the production-equivalent generator. Compare crossing, non-crossing, and pooled subsets.
5. Estimate the sampling distribution of the target statistic. Test the production result and pure-mixture control against theory on the same uncertainty scale.
6. Attribute the discrepancy to theoretical heterogeneity, transition mechanics, finite-sample error, or an unresolved combination. Do not collapse these causes into one explanation.
7. Document the transition algorithm, conditional scope of invariants, and any aggregate change in the final analysis.

Use the law of total variance as a baseline diagnostic:
`Var(X) = E[Var(X | R)] + Var(E[X | R])`. The second term can increase pooled
variance even when every regime is implemented correctly. Compute mixture weights
from how observations are sampled, not merely from regime duration.

## Generalization Examples

- **Urban mobility:** Headways are pooled across morning, midday, and evening
  regimes. Compare the theoretical regime mixture with simulated pooled headways,
  then tag trips crossing a schedule boundary to test whether transition logic
  adds extra variance.
- **Renewable generation:** Wind output combines weather states. Build a pure
  state-mixture control using event-frequency weights, compare it with the
  switching simulator, and isolate ramp-transition observations.
- **Multi-center health study:** Outcomes differ across hospitals. Decompose
  within-center and between-center variance before treating a pooled discrepancy
  as measurement error, and test whether transfer-day records create a separate
  boundary effect.

## Required Evidence

- Closed-form or independently computed mixture reference.
- Pure-mixture control and transition-tagged production check.
- Sampling-error estimate with justified acceptance bounds.
- Structured comparison of pooled, within-regime, and boundary subsets.

## Stop Rules

- Do not compare a pooled mixture directly with a component distribution and call the difference an implementation defect.
- Do not declare boundaries harmless without isolating boundary observations.
- Avoid full-model reruns when a read-only targeted generator check is sufficient.
