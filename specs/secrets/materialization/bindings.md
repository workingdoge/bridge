# Bindings

Canonical source:

- [`SECRET-0002.backend-and-materialization-profile.md`](../secret-0002/SECRET-0002.backend-and-materialization-profile.md)
- [`backend-binding.schema.json`](../secret-0002/schemas/backend-binding.schema.json)
- [`profile-matrix.yaml`](../secret-0002/policy/profile-matrix.yaml)

A `BackendBinding` links a secret class or secret id to one selected backend
profile and one selected materializer profile.

The binding is where the profile choice becomes concrete for a managed secret
or class. It must name allowed consumer kind, allowed modes, TTL override if
any, handle binding, exportability constraints, and direct-model-access policy.

A binding marked non-exportable must not be paired with a materializer whose
surface implies reusable export.
