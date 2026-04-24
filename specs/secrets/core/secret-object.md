# Secret Object

Canonical source:

- [`SECRET-0001.secret-object-and-lifecycle-core.md`](../secret-0001/SECRET-0001.secret-object-and-lifecycle-core.md)
- [`secret-object.schema.json`](../secret-0001/schemas/secret-object.schema.json)

`SecretObject` is the logical record for one managed secret. It names the secret
class, owner, domain, lifecycle policy, materialization policy, recovery policy,
versions, and audit anchors.

`SecretVersion` is one concrete generation, import, or derivation of that
secret. It carries state, epoch, provenance, storage reference, protection
metadata, cryptoperiod, revocation data, timestamps, and audit anchors.

The object and version records are metadata and control objects. They do not
carry raw plaintext secret material.

Downstream runtime code should reference a secret by `secret_id` plus an
eligible version selector. It should not infer backend, materializer, or local
handle shape from the object alone.
