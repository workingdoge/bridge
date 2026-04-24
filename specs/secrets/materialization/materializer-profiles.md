# Materializer Profiles

Canonical source:

- [`SECRET-0002.backend-and-materialization-profile.md`](../secret-0002/SECRET-0002.backend-and-materialization-profile.md)
- [`materializer-profile.schema.json`](../secret-0002/schemas/materializer-profile.schema.json)
- [`profile-matrix.yaml`](../secret-0002/policy/profile-matrix.yaml)

A `MaterializerProfile` defines the last-mile delivery path from an admitted
secret-bound action into a local consumer surface.

Supported materializer profile families include:

- `systemd-credential`
- `memfd-pass`
- `unix-socket-proxy`
- `tmpfs-file`
- `cloud-kms-decrypt`
- `os-keychain-ref`
- `agent-proxy`

`env-var` delivery is not part of the preferred `SECRET-0002` profile set.
Use handle or proxy patterns when feasible.
