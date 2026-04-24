# Attestation

Canonical source:

- [`SECRET-0003.provider-integration-attestation-audit-deployment.md`](../secret-0003/SECRET-0003.provider-integration-attestation-audit-deployment.md)
- [`attestation-result.schema.json`](../secret-0003/schemas/attestation-result.schema.json)

The attestation provider is the authoritative source for workload, host, or
device posture used in the secret path.

An `AttestationResult` carries subject identity, posture digest, verifier
identity, status, issue/expiry time, and evidence references.

Attestation mismatch, expiry, or missing evidence denies or burns according to
deployment policy. Caller-supplied posture is not authoritative.
