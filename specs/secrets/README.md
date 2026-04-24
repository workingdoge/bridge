# Secrets

The secret suite is the bridge-owned domain stack for secret identity,
lifecycle, provider facts, materialization, and evidence.

Start with [`SUITE-FLOW.md`](SUITE-FLOW.md). The individual bundle IDs are
stable import identities, but the operational contract is a single flow across
the three bundles.

## Included Families

| Family | Role | Entry point |
| --- | --- | --- |
| `core/` | Clean view over secret identity, version lifecycle, and class policy | [`core/README.md`](core/README.md) |
| `materialization/` | Clean view over backend/materializer selection and session realization | [`materialization/README.md`](materialization/README.md) |
| `provider-plane/` | Clean view over provider facts, deployment binding, sidecar API, and audit | [`provider-plane/README.md`](provider-plane/README.md) |
| `secret-0001/` | Secret object, version lifecycle, class policy, and lifecycle-core grant vocabulary | [`secret-0001/README.md`](secret-0001/README.md) |
| `secret-0002/` | Backend/materializer selection, plan requests, materialization sessions, signer-session edge, and witness realization | [`secret-0002/README.md`](secret-0002/README.md) |
| `secret-0003/` | Provider catalog, deployment profile, attestation, revocation, mode, audit, and sidecar reference | [`secret-0003/README.md`](secret-0003/README.md) |

The `core/`, `materialization/`, and `provider-plane/` directories are the
reader-facing documentation view. The `secret-0001/`, `secret-0002/`, and
`secret-0003/` directories remain the canonical compatibility paths for the
imported bundle files, schemas, examples, harnesses, and checksum manifests.

## Runtime Shape

The runtime read order is:

```text
bridge admission
  -> SECRET-0001 SecretObject / SecretVersion
  -> SECRET-0003 provider facts
  -> SECRET-0002 MaterializationPlanRequest / MaterializationSession
  -> optional SECRET-0002 signer operation
  -> SECRET-0003 AuditEnvelope
```

`SECRET-0001`, `SECRET-0002`, and `SECRET-0003` intentionally expose adjacent
request/decision artifacts. They are not interchangeable:

- `SECRET-0001` gives the lifecycle-core request/grant abstraction.
- `SECRET-0003` gives provider-readiness and deployment-fact evidence.
- `SECRET-0002` gives the concrete bridge-to-secret materialization session.

## Import Boundary

The original source bundle also carried duplicated bridge material. That
duplicate bridge surface is intentionally not re-imported here; the active
bridge adapter surface comes from `specs/bridge-adapter/`.

Live provider bindings, local secret file paths, funded runtime, and deployment
proof remain downstream unless they stabilize into bridge-owned shared
infrastructure.
