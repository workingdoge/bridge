# SECRET-0003 Bundle

`SECRET-0003` is the **Provider Authority and Audit** bundle. It defines who
supplies authoritative runtime facts, how a deployment binds those providers,
and how durable evidence is emitted.

It does not define logical secret lifecycle and it does not issue local secret
sessions. Read it with [`../SUITE-FLOW.md`](../SUITE-FLOW.md).

## Contents

- `SECRET-0003.provider-integration-attestation-audit-deployment.md`
  - normative integration profile
- `ASSESS-0001.production-readiness-checklist.md`
  - production-readiness checklist
- `schemas/`
  - provider catalog, deployment profile, attestation, revocation, mode, request, decision, audit envelope, and audit checkpoint schemas
- `openapi/secret-provider-sidecar.openapi.yaml`
  - starter sidecar/provider API
- `policy/provider-selection-matrix.yaml`
  - recommended profile defaults by environment
- `python/reference_sidecar.py`
  - executable contract harness
- `python/test_reference_sidecar.py`
  - basic integration tests
- `deploy/`
  - NixOS, nix-darwin, and Kubernetes deployment templates
- `examples/`
  - validated example inputs and generated decisions/audit envelopes

## Validation performed

- validated example JSON files against the included schemas
- ran the reference sidecar to generate accept, deny, and burn decisions
- ran the included Python tests

## Flow position

`SECRET-0003` sits on both sides of `SECRET-0002`:

1. Before materialization, it supplies provider facts: attestation, revocation,
   mode, time, deployment profile, and audit readiness.
2. After decision or session activity, it supplies durable evidence:
   `AuditEnvelope` and `AuditCheckpoint`.

`ProviderDecision` is provider-readiness evidence. It is not the bridge
admission decision and it is not a `SECRET-0002` materialization session.

## Important caveat

The reference sidecar is a **contract harness**, not a production cryptographic or HSM/KMS/Vault implementation.
Real deployments still need:
- real provider adapters,
- durable audit storage,
- attestation and revocation integrations,
- secret backend credentials and trust roots,
- operational approvals and exercises.
