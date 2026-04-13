# Secrets

The secret suite is imported here as part of the bridge domain stack.

Included families:

- `secret-0001/` secret object and lifecycle core
- `secret-0002/` backend and materialization profile
- `secret-0003/` provider integration, attestation, audit, deployment

The original source bundle also carried duplicated bridge material. That
duplicate bridge surface is intentionally not re-imported here; the active
bridge adapter surface comes from `specs/bridge-adapter/`.
