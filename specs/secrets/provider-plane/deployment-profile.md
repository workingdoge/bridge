# Deployment Profile

Canonical source:

- [`SECRET-0003.provider-integration-attestation-audit-deployment.md`](../secret-0003/SECRET-0003.provider-integration-attestation-audit-deployment.md)
- [`deployment-profile.schema.json`](../secret-0003/schemas/deployment-profile.schema.json)
- [`provider-selection-matrix.yaml`](../secret-0003/policy/provider-selection-matrix.yaml)

`DeploymentProfile` binds a concrete environment to a subset of providers and
default secret-class bindings.

It names environment type, platform, identity posture expectations,
authoritative provider ids, default backend and materializer bindings, logging
policy, burn and restore behavior, and emergency queue policy.

Deployment profile truth is still local to the consuming deployment. The bridge
repo provides the schema and reference examples.
