# Provider Catalog

Canonical source:

- [`SECRET-0003.provider-integration-attestation-audit-deployment.md`](../secret-0003/SECRET-0003.provider-integration-attestation-audit-deployment.md)
- [`provider-catalog.schema.json`](../secret-0003/schemas/provider-catalog.schema.json)

`ProviderCatalog` is the inventory of authoritative providers available to a
deployment.

Provider entries declare provider id, provider kind, implementation family,
trust boundary, capabilities, fail-closed policy, health freshness limit,
allowed operating modes, and evidence expectations.

Provider entries do not store raw plaintext secret values.
