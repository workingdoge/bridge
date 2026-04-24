# Sidecar API

Canonical source:

- [`secret-provider-sidecar.openapi.yaml`](../secret-0003/openapi/secret-provider-sidecar.openapi.yaml)
- [`reference_sidecar.py`](../secret-0003/python/reference_sidecar.py)
- [`reference_sidecar_server.py`](../secret-0003/python/reference_sidecar_server.py)

The sidecar API is the reference provider-plane transport for `SECRET-0003`.

It validates provider catalog, deployment profile, request, attestation,
revocation, and mode inputs, then emits provider-readiness decisions and audit
envelopes.

The exported sidecar is a contract harness, not a production cryptographic,
HSM, KMS, Vault, or audit implementation.
