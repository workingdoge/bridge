# SECRET-0003 Bundle

This bundle completes the provider-side portion of the secret-management suite.

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

## Important caveat

The reference sidecar is a **contract harness**, not a production cryptographic or HSM/KMS/Vault implementation.
Real deployments still need:
- real provider adapters,
- durable audit storage,
- attestation and revocation integrations,
- secret backend credentials and trust roots,
- operational approvals and exercises.
