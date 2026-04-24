# Lifecycle

Canonical source:

- [`SECRET-0001.secret-object-and-lifecycle-core.md`](../secret-0001/SECRET-0001.secret-object-and-lifecycle-core.md)
- [`secret-lifecycle.yaml`](../secret-0001/state/secret-lifecycle.yaml)
- [`secret-event.schema.json`](../secret-0001/schemas/secret-event.schema.json)

Lifecycle is version-oriented. The ordinary runtime rule is simple: only
`active` versions may be materialized for ordinary use.

States:

- `staged`
- `active`
- `suspended`
- `revoked`
- `retired`
- `archived`
- `destroyed`

Rotation creates a new version rather than rewriting history. Revocation and
burn invalidate outstanding grants or sessions by epoch or equivalent freshness
checking. Restore enters a fresh staged context; it does not silently return
compromised or archived material to ordinary active use.

Lifecycle events are audit-grade records. They should preserve evidence for
activation, rotation, revocation, archive, restore, and destruction.
