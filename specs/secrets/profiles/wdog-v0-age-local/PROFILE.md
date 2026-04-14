# PROFILE: wdog-v0-age-local

Version: v0 (draft, active)
Scope: workingdoge-LLC's v0 primary host (wdog-primary-01) operational secrets.
Status: Admissible SECRET-0002 profile instance. No live runtime yet; the
profile is realized by the host NixOS config at
`fish/sites/workingdoge/cloud/host/secrets.nix`.

## 1. Purpose

Name the concrete BackendProfile × MaterializerProfile × BackendBinding
combination that workingdoge's v0 primary uses to hold operational secrets
(Cloudflare / Latitude API tokens, cache signing key once lane G lands,
bridge future session tokens, etc.).

Exists because SECRET-0002 requires every conforming deployment to declare
one of each. workingdoge's v0 primary is the first funded-runtime instance
that will hold real secrets; writing the profile down in bridge is how the
admissibility question gets answered.

This profile is explicitly v0. When the v0 primary is retired or elastic
compute arrives, a new profile directory (e.g. `wdog-v1-multi-host-age`)
is filed instead of edit-in-place.

## 2. BackendProfile

Name: `age-encrypted-files-on-local-disk`

Shape:
- Secrets live as `age`-encrypted files on the host's root filesystem.
- Encryption is to a set of age recipients, each of which is a public
  key bound to an identity holder.
- At least one recipient is the **host age identity** of the
  consuming machine. Additional recipients (e.g. off-host break-glass
  identity, multi-machine replicas) MAY be included.
- The encrypted files are in a path readable only by the file system's
  custody boundary; in v0 this is a single Unix user/group with 0700
  directory permissions.

Trust anchors:
- The host age identity is a trust root (SECRET-0001 + spine §2.6 of the
  consuming repo's operational-spine note).
- Backup of the host age identity is mandatory off-host per spine §3.3.

Non-goals:
- No remote key service (no HashiCorp Vault, no AWS KMS, no Cloudflare
  Secrets Manager). Those are separate BackendProfiles for future
  instances.
- No hardware security module integration. Revisit if threat model grows.

## 3. MaterializerProfile

Name: `file-backed-handle`

Shape:
- The materialization artifact is a filesystem path on the host,
  owned by a specific user, with specific mode bits.
- When a consumer (systemd unit, application) needs the secret, it reads
  the file at that path using its own OS credentials. No session
  negotiation, no handle rotation mid-read.
- Materialization happens at service-start time (systemd-tmpfiles or
  equivalent plants the decrypted file; service consumes it; service
  shutdown may or may not unplant depending on binding.persistAtShutdown).

Admission:
- Materialization is admissible per SECRET-0002 only if the bridge
  decision for the requesting `AuthorizeRequest` was `accept`. In v0
  there is no live bridge runtime, so admission is **implicit operator
  consent**: by committing a per-secret binding in this profile, the
  operator declares the materialization pre-admitted.
- When a bridge runtime ships, admission becomes explicit and this
  profile's admission-pathway section gains a pointer to the
  `MaterializationSession` record produced per consumption.

Non-goals:
- No short-lived in-memory handle model (that's a different
  MaterializerProfile, e.g. `ephemeral-envvar-handle`).
- No tmpfs-only storage (v0 file-backed handles may persist across
  reboots; tmpfs variant is future).

## 4. BackendBinding (shape)

Per-secret, the binding is:

```text
BackendBinding = {
  name:         string           // e.g. "cloudflare-mutation-token"
  path:         absolute path    // filesystem location of the decrypted file
  owner:        unix user        // e.g. "custody"
  group:        unix group       // e.g. "custody"
  mode:         octal string     // e.g. "0400"
  recipients:   list of age pubkey references
  authorityClass: enum           // observational | mutation | publish | trust-root
                                 //   from spine §2.6 of the consuming repo
  persistAtShutdown: bool        // whether the decrypted file survives service stop
}
```

Each binding is a git-committed record in the consuming repo's operational
tree. In workingdoge v0 this means each operational secret has a
`sops.secrets.<name>` entry in `cloud/host/secrets.nix` whose options
map onto this BackendBinding schema. sops-nix is one valid mechanism;
agenix-rekey with file outputs is another; any age-compatible file
materializer that honors the mode/owner/group fields conforms.

## 5. MaterializationSession (shape)

Per consumption event, a session record is:

```text
MaterializationSession = {
  session_id:      opaque identifier (v0: the file path acts as the cookie)
  binding_name:    string (references the BackendBinding)
  session_mode:    enum { issue, deny, burn, restore }
  issued_at:       timestamp
  expires_at:      timestamp or null  (v0: null; file lifetime == service lifetime)
  consumer:        systemd unit name or service identity
  audit_record:    reference to the AuditRecord produced by the admission
                   decision, if one was produced (null in v0 no-live-bridge mode)
}
```

v0 admits sessions implicitly at operator-commit-time. Sessions never
appear as runtime records because no runtime issues them. When a live
bridge runtime ships, sessions become explicit artifacts written to the
custody compartment's state directory.

Burn semantics (SECRET-0001):
- A denied or burnable binding MAY still emit a denied MaterializationSession
  for audit and teardown planning.
- A conforming system MUST NOT issue a usable secret handle when the
  session's mode is `deny` or `burn`. In v0 this means operators MUST
  NOT commit a BackendBinding record for a secret class that has been
  burned.

## 6. Admissibility under SECRET-0002

This profile satisfies the SECRET-0002 conformance sentence
(one BackendProfile + one MaterializerProfile + per-secret BackendBinding +
per-session MaterializationSession) for the workingdoge v0 primary.

The profile does NOT satisfy:
- Bridge runtime admission (no live runtime in v0 — implicit operator
  consent model).
- Rotation contract (v0 relies on operator re-commit to rotate; the
  profile will gain a rotation-pathway section when bridge runtime
  ships).
- Multi-consumer distribution (v0 is single-host; multi-host is a new
  profile instance, not an edit-in-place).

## 7. Non-goals (explicit)

- No replication across hosts.
- No HSM-backed signing.
- No provider-hosted key custody (HashiCorp Vault / AWS KMS / Cloudflare
  Secrets Manager).
- No live bridge MaterializationSession runtime.
- No automatic re-encryption on recipient change.

## 8. Consuming repos

- `workingdoge` — v0 primary host (wdog-primary-01). Lane E.4 in
  `workingdoge-00l` instantiates this profile via sops-nix in
  `cloud/host/secrets.nix`.
- Future: AAC's production host, if the AAC IAM epic (workingdoge-6mu)
  determines age-local is the right AAC v0 profile too. More likely AAC
  files its own profile directory (e.g. `aac-v0-...`) because AAC's
  Cloudflare + identity environment differs.
