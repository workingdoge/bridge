# Secret Suite Flow

This note is the map for the `SECRET-0001`, `SECRET-0002`, and
`SECRET-0003` bundle shape.

Read it before treating any one bundle as the whole secret-management contract.
The bundle IDs are stable import identities; the operational shape is a single
flow across them.

## Read Order

1. `SECRET-0001` names the secret and its lifecycle.
2. `SECRET-0003` supplies provider facts needed to trust a runtime decision.
3. `SECRET-0002` selects a backend and materializer, then issues or denies a
   bounded materialization session.
4. `SECRET-0003` carries the durable audit envelope for the resulting event.

The order is not numeric at runtime. `SECRET-0003` provider facts are consulted
before a `SECRET-0002` materialization session is allowed.

## Artifact Flow

```text
Bridge adapter
  AuthorizeRequest
  ProviderResults
  PolicyInput
  Decision
    |
    v
SECRET-0001: Secret Core
  SecretObject
  SecretVersion
  lifecycle state
  class materialization policy
    |
    v
SECRET-0003: Provider Authority
  ProviderCatalog
  DeploymentProfile
  AttestationResult
  RevocationSnapshot
  ModeState
  ProviderDecision
    |
    v
SECRET-0002: Realization
  BackendProfile
  MaterializerProfile
  BackendBinding
  MaterializationPlanRequest
  MaterializationSession
  SignatureRequest / SignatureResponse
  WitnessRealizationRecord
    |
    v
SECRET-0003: Audit
  AuditEnvelope
  AuditCheckpoint
```

## Bundle Boundaries

| Bundle | Primary job | Should contain | Should not become |
| --- | --- | --- | --- |
| `SECRET-0001` | Secret identity, version lifecycle, and class policy | `SecretObject`, `SecretVersion`, lifecycle events, policy defaults | backend selection, provider SPI, deployment truth |
| `SECRET-0002` | Bounded realization of an admitted secret-bound action | backend/materializer profiles, bindings, plan requests, sessions, signer-session edge, witness-realization records | lifecycle authority, provider control plane, production sidecar |
| `SECRET-0003` | Provider facts, deployment binding, and durable evidence | provider catalog, deployment profile, attestation, revocation, mode, audit envelope, sidecar reference | logical secret lifecycle, materialization planner |

## Adjacent Request Types

The suite has three request/decision surfaces because they sit at different
layers:

- `SECRET-0001` `MaterializationRequest` / `MaterializationGrant` is the generic
  lifecycle-core lease vocabulary.
- `SECRET-0003` `ProviderRequest` / `ProviderDecision` is the provider-readiness
  and deployment-fact vocabulary.
- `SECRET-0002` `MaterializationPlanRequest` / `MaterializationSession` is the
  concrete bridge-to-secret realization vocabulary.

Conforming implementations should prefer the `SECRET-0002` session vocabulary
for runtime materialization, while preserving the `SECRET-0001` grant vocabulary
as the lifecycle-core abstraction and the `SECRET-0003` decision vocabulary as
provider-fact evidence.

## Naming Rule

Keep `decision` words scoped:

- bridge `Decision` decides admission;
- `SECRET-0003` `ProviderDecision` decides whether provider facts permit the
  deployment path;
- `SECRET-0002` `MaterializationSession.decision` decides whether a usable local
  handle or denial record is issued.

Do not collapse these into one artifact unless the lost boundary is explicitly
replaced by another typed record.
