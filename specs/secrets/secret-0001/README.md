# SECRET-0001 bundle

This bundle adds the missing **secret object and lifecycle core** behind the bridge.

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
- `examples/*`
  - sample objects and materialization flow

## Intended use

Use this bundle with the bridge artifacts:

1. the bridge determines whether a caller is allowed to attempt a bounded secret use;
2. SECRET-0001 defines how the secret itself is represented, activated, materialized, rotated, revoked, recovered, and destroyed.

## Important design rule

These records are **metadata and control objects**. They intentionally exclude raw plaintext secret values.

## Quickstart

Validate an example secret object:

```bash
python3 python/reference_validator.py validate-secret examples/example.secret-object.dynamic-db-template.json
```

Generate an allow/deny materialization decision:

```bash
python3 python/reference_validator.py authorize \
  examples/example.secret-object.dynamic-db-template.json \
  examples/example.materialization-request.json
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
