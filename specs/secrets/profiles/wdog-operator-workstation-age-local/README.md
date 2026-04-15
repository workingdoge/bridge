# wdog-operator-workstation-age-local

Profile instance for workingdoge-LLC's operator-workstation-rooted
**bootstrap** secrets — the pre-host class that `tofu apply` and
`nixos-anywhere` need to provision the v0 primary before host-side
secret custody exists.

See `PROFILE.md` for the SECRET-0002 conformance shape:
- BackendProfile = age-encrypted files on the operator's workstation
- MaterializerProfile = ephemeral env-var handle (subprocess-scoped,
  no persistence past subprocess exit)
- BackendBinding schema = per-secret ciphertext_path + envvar_name +
  recipients (workstation identity, NOT host)
- MaterializationSession schema = subprocess lifetime = session lifetime

## How this relates to wdog-v0-age-local

Both profiles serve the same consumer (workingdoge-LLC v0), but they
cover disjoint classes of secret:

| Profile                               | Class               | Trust anchor            | Materializer                 |
|---------------------------------------|---------------------|-------------------------|------------------------------|
| `wdog-v0-age-local`                   | host-runtime        | host age identity       | file-backed handle           |
| `wdog-operator-workstation-age-local` | workstation-bootstrap | workstation age identity | ephemeral envvar (subprocess) |

A given secret belongs to **exactly one** profile. Recipients MUST NOT
be mixed: a host-runtime binding does not list the workstation key as
a recipient and vice versa.

## Profile-matrix deviation

The SECRET-0002 profile-matrix recommends
`backend.macos-keychain-bootstrap` + `materializer.agent-proxy` for
`api-token` on an operator workstation. This v0 profile uses an
age-on-workstation backend + ephemeral-envvar materializer instead,
which gives lower friction for the first funded-runtime apply at the
cost of bypassing the recommended broker. PROFILE.md §1 names the
intended successor (`wdog-operator-workstation-keychain-agent`).

## Consumed by

- Future workingdoge issue (not yet filed): instantiate this profile in
  `fish/sites/workingdoge/cloud/host/secrets/bootstrap/` with the
  workstation recipient pubkey and per-secret BackendBindings for
  `hcloud-mutation-token`, `cloudflare-mutation-token`, etc.

## NOT consumed by

- The v0 primary's host runtime (that is `wdog-v0-age-local`).
- home's `arj` darwin host (different trust anchor; future separate
  profile).
- CI runners (different spine §3.1 trust anchor; future separate
  profile if CI ever needs bootstrap secrets).
