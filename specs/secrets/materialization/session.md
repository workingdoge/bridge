# Materialization Session

Canonical source:

- [`SECRET-0002.backend-and-materialization-profile.md`](../secret-0002/SECRET-0002.backend-and-materialization-profile.md)
- [`materialization-session.schema.json`](../secret-0002/schemas/materialization-session.schema.json)

`MaterializationSession` is the concrete record of a planned, issued, or denied
local secret-use session.

It binds:

- bridge trace and decision effect;
- secret id, secret class, backend profile, and materializer profile;
- consumer identity;
- session epoch and secret epoch;
- issued and expiry timestamps;
- handle kind and handle reference;
- constraints, revalidation triggers, teardown actions, and deny reasons.

The session record never carries raw plaintext secret values. The handle may be
a bounded file-like surface, file descriptor, socket reference, operation
reference, keychain reference, opaque handle, or denial marker.
