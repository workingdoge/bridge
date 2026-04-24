# Backend Profiles

Canonical source:

- [`SECRET-0002.backend-and-materialization-profile.md`](../secret-0002/SECRET-0002.backend-and-materialization-profile.md)
- [`backend-profile.schema.json`](../secret-0002/schemas/backend-profile.schema.json)
- [`profile-matrix.yaml`](../secret-0002/policy/profile-matrix.yaml)

A `BackendProfile` declares the trust boundary and protection regime for a
secret class.

Supported backend profile families include:

- `hsm-rooted`
- `kms-envelope`
- `vault-dynamic`
- `external-reference`
- `os-keychain-bootstrap`

The backend profile describes where authority lives. It does not decide the
last-mile local surface; that is the `MaterializerProfile`.
