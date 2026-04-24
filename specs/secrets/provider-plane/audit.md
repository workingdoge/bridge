# Audit

Canonical source:

- [`SECRET-0003.provider-integration-attestation-audit-deployment.md`](../secret-0003/SECRET-0003.provider-integration-attestation-audit-deployment.md)
- [`audit-envelope.schema.json`](../secret-0003/schemas/audit-envelope.schema.json)
- [`audit-checkpoint.schema.json`](../secret-0003/schemas/audit-checkpoint.schema.json)

The audit sink is the authoritative durability target for evidence.

`AuditEnvelope` records allow, deny, burn, restore, rotate, materialize,
revoke, suspend, archive, destroy, and recovery events. The envelope is
sequenced and hash-linked, and it carries secrecy-preserving metadata rather
than raw plaintext.

`AuditCheckpoint` records the latest durable committed point in a stream.
Emergency sealed queues are allowed only when explicitly permitted by the
deployment profile and reconciled after recovery.
