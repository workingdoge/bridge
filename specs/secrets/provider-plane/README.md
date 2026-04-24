# Provider Plane

This is the clean documentation view for `SECRET-0003`.

Use this directory when you want authoritative runtime facts, deployment
binding, provider readiness, durable audit, the reference sidecar API, or
deployment templates.

The canonical imported bundle still lives under [`../secret-0003/`](../secret-0003/).

## Topics

- [`provider-catalog.md`](provider-catalog.md)
- [`deployment-profile.md`](deployment-profile.md)
- [`attestation.md`](attestation.md)
- [`revocation.md`](revocation.md)
- [`mode.md`](mode.md)
- [`audit.md`](audit.md)
- [`sidecar-api.md`](sidecar-api.md)
- [`schemas/`](schemas/)
- [`examples/`](examples/)
- [`deploy/`](deploy/)

## Boundary

`provider-plane/` owns the answer to:

- which providers are authoritative;
- which deployment profile binds the providers;
- whether attestation, revocation, mode, time, and audit facts are fresh enough;
- how durable audit envelopes and checkpoints are shaped.

It does not define logical secret lifecycle or issue a local materialization
session. Those belong in [`../core/`](../core/) and
[`../materialization/`](../materialization/).
