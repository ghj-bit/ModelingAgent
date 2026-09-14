---
name: validate-stochastic-transformations
description: Verify stochastic inputs after scaling, resampling, truncation, censoring, conditioning, or time-varying transformation. Use when simulation conclusions depend on a transformed random process and the transformed distribution or invariants have not been checked directly.
---

# Validate Stochastic Transformations

## Applicability Gate

Use this skill only when code transforms a random input and a reported conclusion depends on the transformed process. Abstain when inputs are deterministic, unchanged, or already covered by an independent executable check with current hashes.

## Workflow

1. State the intended transformed law and the properties that should remain invariant or change predictably: support, mean, variance, coefficient of variation, quantiles, dependence, or conservation identities.
2. Trace the actual production transformation from source parameters through the executed call path. Do not infer behavior from comments alone.
3. Derive the expected post-transformation properties analytically when possible. Mark approximations and their domains.
4. Build a targeted verification using fixed seeds and production-equivalent transformation logic. Compare empirical properties with theory using sampling-error-aware tolerances such as confidence intervals, standard errors, or a justified goodness-of-fit test.
5. Add a reference control that bypasses unrelated model components. Separate a correct transformation from downstream model behavior.
6. Run the smallest dependency-complete check first. Perform a full production rerun only if shared execution logic changed.
7. Propagate verified results into the implementation summary, validation analysis, and final report. Qualify any property that holds only conditionally or within regimes.

For a constant scaling `Y = X / a`, explicitly check `E[Y] = E[X] / a`,
`Var(Y) = Var(X) / a^2`, and unchanged `CV(Y)`. For truncation, conditioning,
or nonlinear transformations, recompute the target moments or reference CDF
instead of assuming scale invariance.

## Generalization Examples

- **Traffic demand:** A simulator divides vehicle headways by an hourly demand
  multiplier. Derive the scaled mean and CV, sample transformed headways with a
  fixed seed, and store a table comparing theory and simulation for every period.
- **Energy forecasting:** Residual scenarios are clipped to keep demand
  nonnegative. Compare the clipped mean, variance, tail probability, and energy
  balance with the intended truncated distribution before using the scenarios in
  capacity planning.
- **Reliability analysis:** Component lifetimes are accelerated by a stress
  factor. Verify the transformed survival curve and hazard assumptions, then show
  that the reported system-failure probability comes from the transformed sample.

## Required Evidence

- Executable verification code or auditable calculations.
- Structured results containing settings, seeds, sample size, theoretical values, empirical values, tolerances, and pass/fail checks.
- A trace from each report claim to the executed result.
- Hashes or equivalent identity checks for reused production artifacts.

## Stop Rules

- Do not claim distribution preservation from matching one moment.
- Do not use an arbitrary percentage tolerance when sampling uncertainty can be estimated.
- Stop and report a limitation when the intended transformed law cannot be derived or independently approximated.
