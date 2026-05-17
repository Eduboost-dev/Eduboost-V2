# Beta Evidence Integrity Repair Report

Generated at: `2026-05-17T11:10:26Z`

## Summary

This repair quarantines placeholder/manual-bypass/local-mock/synthetic evidence and restores truthful beta readiness semantics.

| Gate | Previous status | Repaired status | Source type | Integrity |
|---|---|---|---|---|
| remote_ci | green | green | github_actions | valid |
| branch_protection | synthetic_invalid | synthetic_invalid | github_branch_protection | synthetic_invalid |
| content_gate | waived | waived | release_owner_waiver | valid |
| staging_smoke | synthetic_invalid | synthetic_invalid | unknown | synthetic_invalid |
| backup_drill | synthetic_invalid | synthetic_invalid | unknown | synthetic_invalid |
| restore_drill | synthetic_invalid | synthetic_invalid | unknown | synthetic_invalid |
| rollback_drill | synthetic_invalid | synthetic_invalid | unknown | synthetic_invalid |
| alertmanager_drill | synthetic_invalid | synthetic_invalid | unknown | synthetic_invalid |

## Release rule

Beta readiness is blocked unless every required gate has trusted real evidence or an explicit approved waiver for the content gate only.
