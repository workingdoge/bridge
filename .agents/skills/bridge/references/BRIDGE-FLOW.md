# Bridge Flow

Use this when a task needs the concrete bridge-owned flow, not just a high
level summary.

## Boundary

- Premath kernel doctrine stays upstream in `fish/sites/premath/`.
- This repo owns the bridge adapter contract, secret suite, and bridge-specific
  realization profiles.
- Live provider bindings, local secret files, funded runtime, and first proof
  stay in downstream repos.

## Canonical flow

### 1) Bridge admission

Start here:

- `specs/bridge-adapter/adapter-contract.md`
- `specs/bridge-adapter/provider-mapping.yaml`
- `specs/bridge-adapter/schemas/authorize.request.schema.json`
- `specs/bridge-adapter/schemas/provider-results.schema.json`
- `specs/bridge-adapter/schemas/policy-input.schema.json`

The adapter turns:

- external `AuthorizeRequest`
- authoritative `ProviderResults`

into:

- assembled `PolicyInput`
- bridge decision
- audit record
- mode command or mode state artifacts

Important rule:
- caller input is not authoritative
- the adapter resolves authoritative preflight and runtime facts

### 2) Bridge-to-secret handoff

Start here:

- `specs/secrets/secret-0002/SECRET-0002.backend-and-materialization-profile.md`
- `specs/secrets/secret-0002/schemas/materialization-plan-request.schema.json`
- `specs/secrets/secret-0002/schemas/materialization-session.schema.json`

Normalized handoff:

- `MaterializationPlanRequest`

Core rule:

- `decision_effect != accept` is non-materializable
- a denied or burn case may still emit a denied `MaterializationSession` for
  audit and teardown planning
- a conforming system does not issue a usable secret handle from a non-accept
  bridge decision

### 3) Session surface

The planner or materializer chooses a bounded outcome:

- handle
- proxy
- bounded plaintext surface
- denied session

The bridge-owned secret surface is about bounded issuance, TTL, revocation,
mode, and teardown. It is not a license to hand ambient power to a caller or a
model.

For `signing-key` sessions, downstream consumers SHOULD continue with a small
typed protocol:

- `MaterializationSession` as the session-open artifact
- `SessionOpenArtifact` when the downstream protocol needs explicit composite
  open-session settlement material
- `SignatureRequest` over the local signer handle
- `SignatureResponse` as the bounded signing result

This is a typed session edge, not a signer DSL.

### 4) Burn and restore

Bridge mode artifacts live under:

- `specs/bridge-adapter/schemas/mode-command.schema.json`
- `specs/bridge-adapter/schemas/mode-state.schema.json`
- `specs/bridge-adapter/examples/example.mode-command.burn.json`
- `specs/bridge-adapter/examples/example.mode-state.json`

Secret profiles then inherit the mode boundary for session invalidation and
teardown.

## Examples

Good concrete starting points:

- `specs/bridge-adapter/examples/example.authorize-request.json`
- `specs/bridge-adapter/examples/example.provider-results.accept.json`
- `specs/bridge-adapter/examples/example.policy-input.accept.json`
- `specs/bridge-adapter/examples/example.decision.accept.json`
- `specs/bridge-adapter/examples/example.decision.burn.json`
- `specs/secrets/secret-0002/examples/example.plan-request.analytics-db.json`
- `specs/secrets/secret-0002/examples/example.plan-request.burn.json`
- `specs/secrets/secret-0002/examples/generated.materialization-session.allow.json`
- `specs/secrets/secret-0002/examples/generated.materialization-session.deny.json`
- `specs/secrets/secret-0002/examples/generated.session-open-artifact.signing-key.allow.json`
- `specs/secrets/secret-0002/examples/example.signature-request.signing-key.json`
- `specs/secrets/secret-0002/examples/generated.signature-response.signing-key.allow.json`

## Conformance

After repo changes to the normalized bridge-owned surface, run:

```bash
scripts/bridge-conformance-check.sh
```

This checks the normalized bridge spec surface. It is not a substitute for
downstream live-proof verification.

After planner or bridge-to-secret handoff changes, also run:

```bash
scripts/bridge-property-check.sh
```

This is the semantic property harness for `SECRET-0002` planner invariants.
