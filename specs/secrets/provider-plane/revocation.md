# Revocation

Canonical source:

- [`SECRET-0003.provider-integration-attestation-audit-deployment.md`](../secret-0003/SECRET-0003.provider-integration-attestation-audit-deployment.md)
- [`revocation-snapshot.schema.json`](../secret-0003/schemas/revocation-snapshot.schema.json)

The revocation provider is the authoritative source for revoked issuer, witness,
secret version, and secret epoch status.

`RevocationSnapshot` carries the source id, snapshot id, observed time,
freshness bound, issuer epoch, revoked issuers, revoked JTIs, revoked secret
versions, and revoked secret epochs.

Revocation dominates stale local allow paths. A revoked secret version or epoch
must block new materialization and invalidate outstanding sessions according to
policy.
