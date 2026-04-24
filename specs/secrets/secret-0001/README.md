# SECRET-0001 Bundle

`SECRET-0001` is the **Secret Core** bundle. It defines what a secret is, how
versions move through lifecycle state, and which policy fields constrain later
materialization.

It is not the backend-selection layer and it is not the provider-deployment
layer. Read it with [`../SUITE-FLOW.md`](../SUITE-FLOW.md).

## Contents

- `SECRET-0001.secret-object-and-lifecycle-core.md`
  - normative draft core
- `schemas/secret-object.schema.json`
  - canonical metadata schema for logical secrets and their versions
- `schemas/secret-event.schema.json`
  - audit-grade lifecycle event schema
- `schemas/materialization-request.schema.json`
  - request contract for local materialization
- `schemas/materialization-grant.schema.json`
  - bounded grant/lease contract
- `state/secret-lifecycle.yaml`
  - version-oriented lifecycle state machine
- `policy/secret-class.defaults.yaml`
  - starter class defaults
- `python/reference_validator.py`
  - reference validator / decision harness

## Intended use

Use this bundle with the bridge artifacts:

1. the bridge determines whether a caller is allowed to attempt a bounded secret use;
2. `SECRET-0001` defines how the secret itself is represented, activated,
   rotated, revoked, recovered, and destroyed;
3. `SECRET-0003` supplies provider facts for attestation, revocation, mode, and
   audit readiness;
4. `SECRET-0002` turns the admitted request plus lifecycle and provider facts
   into a concrete `MaterializationSession`.

## Materialization vocabulary

This bundle includes `MaterializationRequest` and `MaterializationGrant` as the
generic lifecycle-core lease vocabulary. Runtime bridge-to-secret session
issuance should use `SECRET-0002` `MaterializationPlanRequest` and
`MaterializationSession`.

The split is:

- `SECRET-0001` decides whether a secret version and class policy are eligible
  for bounded use.
- `SECRET-0002` decides the selected backend, selected materializer, local
  handle shape, TTL, teardown, and denial record.
- `SECRET-0003` decides whether provider facts and deployment state are fresh
  enough to trust the runtime path.

## Important design rule

These records are **metadata and control objects**. They intentionally exclude raw plaintext secret values.

## Quickstart

The normalized bridge tree currently stages the schemas and reference validator
for `SECRET-0001`; it does not stage the original example objects.

Validate a downstream or local example secret object:

```bash
python3 python/reference_validator.py validate-secret <secret-object.json>
```

Generate an allow/deny materialization decision:

```bash
python3 python/reference_validator.py authorize \
  <secret-object.json> \
  <materialization-request.json>
```

## Caveats

This is a contract bundle, not a production CKMS. It does **not** implement:

- real cryptographic generation/import,
- real HSM/KMS integration,
- real revocation fanout,
- real attestation verification,
- durable audit transport,
- secure destruction of external backends.

It is meant to make the missing lifecycle semantics explicit and machine-readable.
