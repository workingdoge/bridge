# Mode

Canonical source:

- [`SECRET-0003.provider-integration-attestation-audit-deployment.md`](../secret-0003/SECRET-0003.provider-integration-attestation-audit-deployment.md)
- [`mode-state.schema.json`](../secret-0003/schemas/mode-state.schema.json)

The mode controller is the authoritative source for `normal`, `degraded`,
`safe`, and `burn` mode.

`ModeState` carries mode, mode epoch, controller id, change time, reason, scope,
and restore prerequisites.

Burn mode dominates new session issuance for the affected cut-set. Restore
requires fresh provider facts and whatever approvals the deployment profile
declares.
