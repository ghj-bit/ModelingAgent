---
name: fuse-verified-patches
description: Merge complementary refinements from independent solution branches while preserving verified parent invariants. Use when two branches address different defects and both have executable or auditable validation evidence.
---

# Fuse Verified Patches

## Applicability Gate

Fuse only when both candidate patches are valid, materially useful, and semantically complementary. Abstain when they duplicate the same conclusion, conflict without a resolvable model choice, or lack validation.

## Workflow

1. Identify the lowest common ancestor, primary branch, and donor branch.
2. Extract each patch as a semantic delta: defect, changed claim, modified logic, evidence, downstream files, and preserved invariants.
3. Compare primary, donor, and ancestor versions. Detect code, data, assumption, report, and conclusion conflicts before editing.
4. Keep the primary branch authoritative. Replay only the donor's verified semantic change; never overwrite whole files blindly.
5. Run the donor's targeted validation in the fused workspace, then run regression checks for every primary invariant affected by the merged dependency graph.
6. Regenerate downstream analyses and the final report from fused authoritative artifacts.
7. Accept the fusion only if both improvements remain present, supported, and non-contradictory.

Represent each patch before fusion as `{defect, assumptions_changed,
logic_changed, evidence, downstream_claims, preserved_invariants}`. Use this map
to decide whether the donor can be replayed independently or requires conflict
resolution.

## Optimizer Examples

- **Model structure plus input validation:** One search branch validates an
  alternative network structure; another verifies transformed stochastic inputs.
  Replay the input-validation patch into the stronger structural branch and run
  both the transformation check and the structural decision regression.
- **Data calibration plus uncertainty analysis:** One branch improves source
  calibration while another adds bootstrap intervals. Merge the calibration
  change first, regenerate the bootstrap from calibrated data, and reject stale
  uncertainty results copied from the donor.
- **Algorithm correction plus report repair:** One branch fixes solver logic and
  another repairs evidence traceability. Apply the solver fix, regenerate results,
  then replay only report mappings that remain valid against the new outputs.

## Required Evidence

- Three-way change map.
- Both parent patch specifications and validation artifacts.
- Post-fusion targeted checks and regression results.
- List of preserved, invalidated, and regenerated artifacts.

## Stop Rules

- Prefer a minimal semantic replay over file-level replacement.
- Abort when the donor adds report volume without resolving an outstanding risk.
- Abort when preserving one invariant invalidates the other and no principled tradeoff is available.
