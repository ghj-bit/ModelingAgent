---
name: propagate-verifiable-evidence
description: Carry a validated modeling or implementation correction through authoritative artifacts into the final report without stale claims or unnecessary reruns. Use after any refinement changes a model assumption, code path, result, limitation, or recommendation.
---

# Propagate Verifiable Evidence

## Applicability Gate

Use after a concrete correction or new validation result exists. Do not invoke for stylistic edits that leave claims and evidence unchanged.

## Workflow

1. Record the corrected claim, affected dependency scope, changed source artifacts, and validation evidence.
2. Classify artifacts as modified, regenerated, preserved, invalidated, or metadata. Verify reused artifacts by hash or an equivalent identity check.
3. Update only downstream documents whose claims depend on the correction: assumptions, implementation, validation, results, limitations, recommendations, and special deliverables.
4. Regenerate the final report from authoritative artifacts rather than manually patching disconnected copies.
5. Check every changed numerical or methodological claim against its executed result, units, configuration, seed, and uncertainty statement.
6. Remove stale contradictions and duplicated explanations. Keep secondary evidence concise or move it to supporting material.
7. Write a compact evidence manifest linking claim, source path, validation path, and report location.

For every changed claim, record a compact row such as
`claim_id | source artifact | execution/result artifact | report section | status`.
Use `status` values such as `updated`, `preserved`, or `invalidated`; never treat
the Agent's narrative as proof that a computation ran.

## Generalization Examples

- **Parameter recalibration:** An external measurement changes one fitted
  parameter. Regenerate dependent predictions and sensitivity results, preserve
  unrelated analyses by hash, and update every report table and recommendation
  that uses the parameter.
- **Solver correction:** A constraint-handling bug is fixed. Execute a focused
  regression case, rerun invalidated optimization scenarios, replace stale
  objective values, and verify that the final recommendation uses the corrected
  feasible solution.
- **New robustness test:** A structural alternative leaves the decision unchanged.
  Add the comparison result and uncertainty margin to validation and limitations,
  while keeping the primary model and avoiding a duplicate second solution.

## Required Evidence Chain

```text
source basis -> model claim -> identified defect -> correction
-> executable validation -> structured result -> analysis
-> downstream artifact -> final report claim
```

## Stop Rules

- Do not list bookkeeping files as substantive modifications.
- Do not rerun unaffected production computations.
- Do not declare completion while the final report predates the correction or validation.
