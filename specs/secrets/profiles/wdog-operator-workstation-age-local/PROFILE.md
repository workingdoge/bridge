# PROFILE: wdog-operator-workstation-age-local

Version: v0 (draft, active)
Scope: workingdoge-LLC's operator workstation-rooted bootstrap secrets
       used to provision wdog-primary-01 before the host exists.
Status: Admissible SECRET-0002 profile instance. No live runtime yet; the
profile is instantiated by the operator's sops-age tree committed in
`fish/sites/workingdoge/cloud/host/secrets/bootstrap/` (downstream lane,
filed separately after this profile lands).

## 1. Purpose

Name the concrete BackendProfile × MaterializerProfile × BackendBinding
combination that workingdoge uses to hold **pre-host** provisioning
secrets — the tokens that `tofu apply` and `nixos-anywhere` need to
create the v0 primary before any host-side secret custody exists.

Exists because `wdog-v0-age-local` is **host-rooted**: its BackendProfile
trust anchor is the v0 primary's host age identity, and its
MaterializerProfile (`file-backed-handle`) materializes to
`/var/lib/custody/secrets/` on the host. That profile cannot admit
Hetzner Cloud API tokens or Cloudflare mutation tokens during the first
apply, because:

- The host doesn't exist yet — `tofu apply` is what creates it.
- The consumer of these tokens is a short-lived provisioning subprocess
  on the operator's workstation (`tofu`, `hcloud`, `nixos-anywhere`),
  not a long-running systemd unit on the primary.
- The trust anchor is the operator's workstation identity, not the
  (non-existent) host identity.

The SECRET-0002 profile-matrix (`specs/secrets/secret-0002/policy/profile-matrix.yaml`)
recommends `backend.macos-keychain-bootstrap` + `materializer.agent-proxy`
for operator-workstation-local API token use. This v0 profile **deviates**
by using an age-on-workstation backend + ephemeral-envvar materializer
instead. The deviation is explicit and v0-bounded (see §6 Admissibility).
A `wdog-operator-workstation-keychain-agent` profile is the intended
successor once an operator-side agent-proxy broker ships.

This profile is explicitly v0. When the operator workstation becomes
multi-host, when a broker/agent-proxy is available, or when bridge-runtime
MaterializationSession records land, a new profile directory (e.g.
`wdog-operator-workstation-keychain-agent` or `wdog-v1-broker-mediated`)
is filed instead of edit-in-place.

## 2. BackendProfile

Name: `age-encrypted-files-on-operator-workstation`

Shape:
- Secrets live as `age`-encrypted files on the operator's workstation
  filesystem, committed to the consuming repo under a designated
  bootstrap/ subdirectory (path named by the consuming repo; in
  workingdoge v0 this is `cloud/host/secrets/bootstrap/`).
- Encryption is to a set of age recipients, each of which is a public
  key bound to an identity holder.
- At least one recipient is the **operator workstation age identity**.
  Additional recipients (e.g. off-workstation break-glass identity,
  co-operator identities) MAY be included.
- The consuming repo's `.sops.yaml` SHOULD route these files to a
  separate recipient set from host-materialized files; see §4
  BackendBinding shape.

Trust anchors:
- The operator workstation age identity is a trust root (SECRET-0001 +
  spine §3.1 of the consuming repo's operational-spine note: operator
  workstation trust anchor).
- Backup of the workstation age identity is mandatory off-workstation;
  loss of the key with no backup means every binding in this profile
  must be rotated (tokens re-minted upstream, new recipient installed,
  re-encryption across bindings).

Non-goals:
- No remote key service (no HashiCorp Vault, no AWS Secrets Manager,
  no cloud-hosted key custody). Those are different BackendProfiles.
- No OS keychain integration. Matrix recommends that path for the
  vNext profile (`wdog-operator-workstation-keychain-agent`); v0 uses
  the same `age`-file backend as the host profile for operational
  consistency during the first apply.
- No hardware security module integration.
- No admission for host-materialized secrets. Those belong to
  `wdog-v0-age-local`; mixing backends in one profile would violate
  SECRET-0002 §2's one-BackendProfile-per-profile rule.

## 3. MaterializerProfile

Name: `ephemeral-envvar-handle`

Shape:
- The materialization artifact is a **process environment variable**
  set in a short-lived subprocess (the provisioning tool) by the
  operator's shell.
- Materialization happens at subprocess-start: the operator (or a
  wrapper script) decrypts the binding's ciphertext via `sops`, exports
  the plaintext into the subprocess env (`HCLOUD_TOKEN=... tofu apply`,
  etc.), and the subprocess consumes it for the duration of the apply.
- Teardown is subprocess exit: the env var goes with the process. No
  persistence into files, keychain, or any longer-lived surface.
- The plaintext MUST NOT be logged, persisted to shell history, or
  echoed to a terminal whose scrollback is not the operator's workstation.

Admission:
- Materialization is admissible per SECRET-0002 only if the bridge
  decision for the requesting `AuthorizeRequest` was `accept`. In v0
  there is no live bridge runtime, so admission is **implicit operator
  consent**: by invoking the documented provisioning wrapper with a
  committed BackendBinding, the operator declares the materialization
  pre-admitted.
- When a bridge runtime ships, admission becomes explicit and this
  profile's admission-pathway section gains a pointer to the
  `MaterializationSession` record produced per subprocess invocation.

Non-goals:
- No file-backed handle (that's `wdog-v0-age-local`'s materializer).
- No unix-socket proxy or agent-proxy (those are different materializers,
  recommended by the matrix for vNext).
- No persistence across subprocess invocations. Each apply = one session.

## 4. BackendBinding (shape)

Per-secret, the binding is:

```text
BackendBinding = {
  name:            string           // e.g. "hcloud-mutation-token"
  ciphertext_path: relative path    // repo-relative path to the sops-encrypted file
                                    //   (e.g. "cloud/host/secrets/bootstrap/hcloud.yaml")
  envvar_name:     string           // env var exported into the subprocess
                                    //   (e.g. "HCLOUD_TOKEN")
  recipients:      list of age pubkey references
                                    //   MUST include at least the operator
                                    //   workstation age identity
  authorityClass:  enum             // observational | mutation | publish | trust-root
                                    //   from spine §2.6 of the consuming repo
  scope:           string           // semantic scope descriptor
                                    //   e.g. "hetzner-cloud-project:<name>"
                                    //   e.g. "cloudflare-account:<id>"
  rotation:        string           // rotation policy — v0: "rotate-per-apply"
                                    //   (operator mints a fresh token for each
                                    //    provisioning run, old ciphertext burned)
  consumer:        string           // subprocess name that consumes this binding
                                    //   e.g. "tofu", "nixos-anywhere"
}
```

Each binding is a git-committed record in the consuming repo's
bootstrap/ subdirectory. In workingdoge v0 this lives at
`cloud/host/secrets/bootstrap/` with a matching entry in
`cloud/host/secrets/.sops.yaml` creation-rules that routes the
ciphertext to the operator-workstation recipient list (separate from
the host-recipient list for `wdog-v0-age-local`).

Recipient separation from `wdog-v0-age-local` is MANDATORY: a binding
in this profile MUST NOT list the host age identity as a recipient,
because the host is not a legitimate consumer of a workstation-rooted
bootstrap secret. Mixing recipients would violate §4.2 spine
compartment separation of the consuming repo.

## 5. MaterializationSession (shape)

Per consumption event, a session record is:

```text
MaterializationSession = {
  session_id:      opaque identifier (v0: subprocess pid + start time acts as cookie)
  binding_name:    string (references the BackendBinding)
  session_mode:    enum { issue, deny, burn, restore }
  issued_at:       timestamp (subprocess exec)
  expires_at:      timestamp (subprocess exit; not null — bounded by process life)
  consumer:        subprocess identifier (argv[0] + invocation env digest)
  audit_record:    reference to the AuditRecord produced by the admission
                   decision, if one was produced (null in v0 no-live-bridge mode)
}
```

v0 admits sessions implicitly at operator-commit-time and at
provisioning-wrapper-invocation-time. Sessions do not appear as
runtime records because no runtime issues them. When a live bridge
runtime ships, sessions become explicit artifacts written to the
operator workstation's audit directory and replicated to the custody
compartment post-install.

Burn semantics (SECRET-0001):
- A denied or burnable binding MAY still emit a denied MaterializationSession
  for audit and teardown planning.
- A conforming system MUST NOT export a usable secret envvar when the
  session's mode is `deny` or `burn`. In v0 this means operators MUST
  NOT commit a BackendBinding record for a secret class that has been
  burned, and MUST rotate the upstream token if a prior ciphertext is
  known-exposed.

Token exposure beyond the subprocess (e.g. operator paste into a
conversation, shell history capture, unintended file write) burns the
session and obligates rotation. The profile cannot recover an exposed
token; it can only bound the exposure to future subprocesses and rotate
the ciphertext.

## 6. Admissibility under SECRET-0002

This profile satisfies the SECRET-0002 conformance sentence
(one BackendProfile + one MaterializerProfile + per-secret BackendBinding +
per-session MaterializationSession) for workingdoge's operator-workstation
bootstrap class.

The profile does NOT satisfy:
- Profile-matrix recommended shape for `api-token`
  (`backend.macos-keychain-bootstrap` + `materializer.agent-proxy`). The
  v0 deviation is explicit (§1) and the successor profile is named.
- Bridge runtime admission (no live runtime in v0 — implicit operator
  consent model).
- Persistent session records (v0 sessions are ephemeral with the
  subprocess).
- Multi-operator distribution (v0 is single-operator; multi-operator
  is a new profile instance, not an edit-in-place).

## 7. Non-goals (explicit)

- No host-materialized secrets (that's `wdog-v0-age-local`).
- No agent-proxy broker (matrix-aligned vNext).
- No keychain backend (matrix-aligned vNext).
- No persistence of plaintext across subprocess invocations.
- No CI-runner access to these bindings. The operator workstation and
  the CI runner are different spine §3.1 trust anchors; a CI-accessible
  bootstrap profile would be a separate profile instance.
- No automatic re-encryption on recipient change.
- No cross-workstation replication of the age identity.
