# Bridge Type Families

This note organizes the bridge domain stack by stable type families rather than
by vendor or transport names.

Use this map when shaping new schemas, exported modules, or runtime interfaces.
Products such as Vault, KMS, `agenix`, or `/etc` paths are implementations or
delivery choices, not the canonical semantic center.

## Families

### 1. Ingress

Untrusted caller input and requested action shape.

Primary types:

- `AuthorizeRequest`
- requested method
- requested TTL
- consumer and resource references

Primary surface:

- `specs/bridge-adapter/schemas/authorize.request.schema.json`

### 2. Authority

Authoritative facts resolved from trusted providers before admission or
materialization.

Primary types:

- `ProviderResults`
- `AttestationResult`
- `RevocationSnapshot`
- `ModeState`
- time authority result
- `ProviderCatalog`
- `DeploymentProfile`

Primary surface:

- `specs/bridge-adapter/schemas/provider-results.schema.json`
- `specs/secrets/secret-0003/schemas/*.schema.json`
- `specs/secrets/secret-0003/SECRET-0003.provider-integration-attestation-audit-deployment.md`

### 3. Admission

Bridge-owned assembly and decision types.

Primary types:

- `PolicyInput`
- `Decision`
- `DecisionEffect`
- deny and burn reasons
- bridge authority bounds

Primary surface:

- `specs/bridge-adapter/schemas/policy-input.schema.json`
- `specs/bridge-adapter/schemas/decision.schema.json`
- `specs/bridge-adapter/adapter-contract.md`

### 4. Secret Core

What the secret is across lifecycle and epoch boundaries.

Primary types:

- `SecretObject`
- `SecretVersion`
- `SecretClass`
- lifecycle state
- recovery policy
- materialization policy

Primary surface:

- `specs/secrets/secret-0001/SECRET-0001.secret-object-and-lifecycle-core.md`
- `specs/secrets/secret-0001/schemas/*.schema.json`

### 5. Realization

The bounded handoff from an admitted action into a concrete secret-use session.

Primary types:

- `BackendProfile`
- `MaterializerProfile`
- `BackendBinding`
- `MaterializationPlanRequest`
- `MaterializationSession`
- `SignatureRequest`
- `SignatureResponse`
- session handle kind
- teardown policy

Primary surface:

- `specs/secrets/secret-0002/SECRET-0002.backend-and-materialization-profile.md`
- `specs/secrets/secret-0002/schemas/*.schema.json`

### 6. Audit

Durable evidence and receipt material across bridge and secret flows.

Primary types:

- bridge audit record
- `AuditEnvelope`
- `AuditCheckpoint`
- trace id and event hash anchors

Primary surface:

- `specs/bridge-adapter/schemas/audit-record.schema.json`
- `specs/secrets/secret-0003/schemas/audit-envelope.schema.json`
- `specs/secrets/secret-0003/schemas/audit-checkpoint.schema.json`

## Implementation rule

Organize reusable interfaces around these type families:

- fact providers serve `Authority`
- bridge adapters assemble `Admission`
- planners and materializers realize `Realization`
- products such as Vault, KMS, HSM, `agenix`, or local files implement lower
  roles, not the top-level semantic model

## Current repo split

- `bridge-adapter/` centers `Ingress`, `Authority`, and `Admission`
- `secrets/secret-0001/` centers `Secret Core`
- `secrets/secret-0002/` centers `Realization`
- `secrets/secret-0003/` centers `Authority` and `Audit`
- `bridge-premath-0001/` gives the bridge-specific realization profile over
  those families
