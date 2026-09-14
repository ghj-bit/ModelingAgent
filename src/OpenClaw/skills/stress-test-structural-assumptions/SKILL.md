---
name: stress-test-structural-assumptions
description: Test whether an unsupported but decision-relevant structural modeling assumption changes the recommendation. Use for alternative topologies, allocation rules, dependence structures, behavioral rules, or system configurations that are plausible from the problem statement.
---

# Stress Test Structural Assumptions

## Applicability Gate

Use only when the statement leaves a structural choice ambiguous and a plausible alternative could change the final decision. Do not test cosmetic variants or assumptions that cannot affect a requested output.

## Workflow

1. Name the decision or conclusion at risk and the structural assumption supporting it.
2. Justify one realistic alternative without inventing task-specific facts.
3. Hold data, objectives, constraints, sample sizes, and evaluation metrics fixed. Change only the structural mechanism under test.
4. Use paired seeds or common random numbers when simulation permits. Report uncertainty for both configurations and their difference.
5. Check feasibility identities and reproduce the parent configuration before comparing the alternative.
6. Classify the outcome as invariant, conditional, or reversed. If invariant, quantify the margin to the decision boundary; if conditional, state the condition precisely.
7. Update assumptions, implementation, validation, recommendation, and limitations consistently.

Define the decision margin before testing. For a threshold decision, report the
alternative model's confidence bound relative to the threshold. For a ranking or
allocation decision, report whether the ordering or selected allocation changes,
not only whether the objective value changes.

## Generalization Examples

- **Warehouse design:** The primary model pools inventory across sites. Compare
  one plausible decentralized policy using the same demand traces and costs; state
  whether the recommended capacity allocation changes and by what margin.
- **Evacuation planning:** The model assumes centrally assigned routes. Test a
  decentralized route-choice rule under paired scenarios and compare clearance
  time, bottleneck use, and the selected intervention.
- **Epidemic modeling:** A homogeneous-mixing model supports a control policy.
  Evaluate one network or age-stratified alternative with matched calibration and
  determine whether the policy threshold is invariant, conditional, or reversed.

## Required Evidence

- Explicit baseline and alternative formulations.
- Reproducible comparison code or auditable analysis.
- Structured results with uncertainty and decision margins.
- A report statement that distinguishes robustness from equivalence.

## Stop Rules

- Test at most one high-impact structural alternative per invocation.
- Do not claim robustness from qualitative discussion alone.
- Do not replace the primary model merely because the alternative is more complex.
