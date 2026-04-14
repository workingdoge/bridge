# SECRET-0002 — Backend and Materialization Profile
Version: 0.1  
Status: Draft normative profile  
Date: 2026-04-12

## 1. Purpose

This document defines the concrete **backend boundary** and **last-mile materialization profile**
that SECRET-0001 intentionally left open. It answers the questions:

1. *Which backend trust boundary actually holds or issues the secret?*
2. *Which last-mile path may deliver a handle or bounded plaintext surface to the consumer?*
3. *Which profile combinations are admissible for each secret class?*
4. *What MUST happen on revocation, burn, teardown, and recovery?*

A conforming implementation SHALL define:

- one `BackendProfile`,
- one `MaterializerProfile`,
- one `BackendBinding` for each managed secret or secret class,
- one `MaterializationSession` record for each issued or denied session.

## 2. Relationship to other artifacts

- **Bridge Spec v0.2** decides whether a caller may attempt a secret-bound action.
- **SECRET-0001** defines the secret object and lifecycle core.
- **SECRET-0002** defines *where* the secret lives and *how* it reaches a consumer.

Authorization alone is not secret management. Lifecycle alone is not enough either.
A conforming deployment needs all three.

## 2.1 Bridge-to-secret handoff

The normalized handoff from Bridge Spec v0.2 into SECRET-0002 SHALL be a
`MaterializationPlanRequest`.

The bridge adapter SHALL assemble this object after bridge admission is decided
and before any local secret materialization path is chosen.

For a secret-bound request, the handoff SHALL carry at least:

- bridge request identity and witness identity;
- bridge decision effect plus deny or burn reasons;
- hashes or equivalent references tying the handoff back to the bridge policy
  input and decision artifacts;
- explicit resource-to-secret seam data including `binding_id`;
- secret identity and class;
- consumer identity and attestation basis;
- requested method and requested TTL;
- bridge-derived authority bounds such as effective TTL, non-exportability, and
  materialization budget;
- current mode and bridge epoch.

The planner SHALL treat `decision_effect != accept` as non-materializable.
It MAY still emit a denied `MaterializationSession` for audit and teardown
planning, but it SHALL NOT issue a usable secret handle from a non-accept
bridge decision.

## 3. Conformance

A system conforms to SECRET-0002 only if all of the following hold:

- every materializable secret has exactly one selected backend profile and one selected materializer profile at decision time;
- the selected profiles are compatible with the secret class and binding policy;
- the backend profile states its trust boundary, protection mode, revocation mechanism, and recovery mode;
- the materializer profile states its plaintext surface, handle type, TTL limits, revalidation triggers, and teardown rules;
- direct model access to a secret backend is prohibited;
- burn mode invalidates new sessions and tears down active sessions according to policy;
- raw plaintext secret values are absent from profile, binding, session, and audit metadata.

## 4. Backend profiles

A `BackendProfile` SHALL declare the concrete trust boundary and protection regime for a secret class.

### 4.1 Supported backend types

- `hsm-rooted`
- `kms-envelope`
- `vault-dynamic`
- `external-reference`
- `os-keychain-bootstrap`

Other types MAY be added locally, but SHALL preserve the invariants in this document.

### 4.2 Backend requirements

#### 4.2.1 `hsm-rooted`

`hsm-rooted` SHOULD be used for root or high-assurance key classes such as signing keys,
wrapping keys, recovery shares, and other non-exportable private key material.

A conforming `hsm-rooted` profile SHALL satisfy:

- `export_policy ∈ {non-exportable, wrapped-only}`;
- `root_key_online = false` for the highest-trust root key tier;
- dual control for destructive or recovery operations;
- attestation or equivalent trust evidence for online consumers of derived operations.

#### 4.2.2 `kms-envelope`

`kms-envelope` is for ciphertext-at-rest patterns where the backend protects a wrapping key
and the actual secret value is released only to a bounded local materializer.

A conforming `kms-envelope` profile SHALL satisfy:

- `storage_mode = ciphertext-at-rest`;
- plaintext is not persisted by the backend profile;
- unwrap/decrypt operations are auditable;
- recovery and rotation paths are explicit.

#### 4.2.3 `vault-dynamic`

`vault-dynamic` is for secrets that are **issued on demand** and revoked by lease, epoch,
or disablement, rather than archived as long-lived reusable secret values.

A conforming `vault-dynamic` profile SHALL satisfy:

- `storage_mode = dynamic-issued` or `reference-only`;
- revocation uses lease or equivalent short-lived invalidation;
- plaintext credential values are not archived as enduring metadata;
- session TTL is bounded by the issued lease and local profile TTL.

#### 4.2.4 `external-reference`

`external-reference` is for cases where the backend holds authority but the bridge never
receives the underlying secret value, only a handle or operation reference.

A conforming `external-reference` profile SHALL satisfy:

- `storage_mode = reference-only` or `hardware-sealed`;
- direct export of underlying key material is prohibited;
- the consumer receives a handle or proxy path, not a reusable plaintext value.

#### 4.2.5 `os-keychain-bootstrap`

`os-keychain-bootstrap` is for human-side or workstation-local bootstrap material.

A conforming `os-keychain-bootstrap` profile SHALL satisfy:

- it is used only for local bootstrap or user-side secrets unless a separate policy explicitly permits more;
- the keychain or OS store is not treated as the sole source of truth for shared infrastructure secrets;
- export and sync risks are documented in local policy.

## 5. Materializer profiles

A `MaterializerProfile` SHALL define the last-mile delivery path.

### 5.1 Supported materializer types

- `systemd-credential`
- `memfd-pass`
- `unix-socket-proxy`
- `tmpfs-file`
- `cloud-kms-decrypt`
- `os-keychain-ref`
- `agent-proxy`

`env-var` delivery is intentionally absent from this profile set.

### 5.2 Materializer requirements

#### 5.2.1 `systemd-credential`

`systemd-credential` SHOULD be the preferred Linux/systemd path when a service needs a file-like
or credential-directory surface under tight service scoping.

A conforming `systemd-credential` profile SHALL:

- bind the session to a systemd unit or equivalent consumer;
- require destroy-on-exit or equivalent cleanup;
- revalidate on burn and epoch change;
- keep audit and redaction obligations.

#### 5.2.2 `memfd-pass`

`memfd-pass` is for a single process that can consume a file descriptor or memfd style surface.

It SHOULD be preferred over general tmp files when the application supports it.

#### 5.2.3 `unix-socket-proxy`

`unix-socket-proxy` is for proxy-style use cases where the consumer should invoke a narrow operation
without receiving a reusable plaintext secret value.

It SHOULD be preferred for signing, decrypt, and high-assurance non-exportable operations.

#### 5.2.4 `tmpfs-file`

`tmpfs-file` MAY be used only when the target application insists on a path and no safer profile is feasible.

A conforming `tmpfs-file` profile SHALL:

- use a bounded tmpfs or equivalent non-persistent path;
- unlink or shred-equivalent on exit if feasible;
- require log redaction and model re-entry prohibition.

#### 5.2.5 `cloud-kms-decrypt`

`cloud-kms-decrypt` is for remote-handle or operation-reference flows where the backend performs unwrap/decrypt
and the consumer receives only the outcome or a bounded handle.

#### 5.2.6 `os-keychain-ref`

`os-keychain-ref` is for local macOS or similar OS store references. It SHOULD remain on the local workstation side.

#### 5.2.7 `agent-proxy`

`agent-proxy` is for a local broker or sidecar mediating secret use or dynamic issuance. It is the preferred
pattern when the goal is to avoid handing reusable power to a general-purpose model.

## 6. Binding rules

A `BackendBinding` SHALL link a secret class or secret id to one backend profile and one materializer profile.

Binding rules SHALL satisfy:

- the secret class MUST be allowed by both selected profiles;
- `requested_ttl ≤ min(materializer.max_ttl_s, binding.max_ttl_s_override if present)`;
- the binding MUST specify the allowed consumer kind and allowed modes;
- `direct_model_access_prohibited = true`;
- `non_exportable = true` for root keys, wrapping keys, signing keys, and proxy-only profiles.

## 7. Materialization sessions

A `MaterializationSession` is the concrete record of a planned or issued local session.

A session SHALL include:

- `binding_id`;
- the upstream bridge decision effect;
- binding of secret id, secret class, backend profile, and materializer profile;
- consumer identity;
- bridge trace;
- session epoch and secret epoch;
- handle kind and handle reference;
- teardown actions and revalidation triggers;
- deny reasons when denied.

A session SHALL NOT include raw plaintext secret values.

For `signing-key` sessions, the narrow post-session operation edge is further
spelled out in `SIGNER-SESSION-CONTRACT.md`.

## 8. Required planning algorithm

A conforming planner SHALL:

1. validate the selected profiles and binding;
2. deny if the bridge decision effect is not `accept`;
3. deny if `mode = burn`;
4. deny if the request method does not match the selected materializer profile;
5. deny if the consumer kind or requested TTL violates either local policy or
   the bridge-derived authority bounds;
6. require attestation when the backend trust boundary or binding demands it;
7. select the narrowest feasible plaintext surface;
8. prefer handle/proxy patterns over reusable plaintext where feasible;
9. emit a `MaterializationSession` record whether the request is allowed or denied.

## 9. Burn and teardown semantics

Burn is not just a policy bit. It is an operational cut.

For every allowed binding, local policy SHALL state whether burn:

- revokes the handle,
- closes any proxy/socket,
- invalidates lease or epoch,
- unlinks local files,
- tears down the consumer session,
- preserves the audit trail.

Every materializer profile SHALL define teardown actions on expiry and on consumer exit.

## 10. Invariants

### INV-1 No plaintext metadata
Backend profiles, materializer profiles, bindings, and sessions SHALL exclude raw plaintext secret values.

### INV-2 One backend, one materializer
Each materializable secret MUST have exactly one selected backend profile and one selected materializer profile at decision time.

### INV-3 Narrowest surface
If a profile combination can satisfy the use case via handle or proxy, the planner SHALL NOT widen the plaintext surface without an explicit policy override.

### INV-4 Burn invalidates
Burn SHALL deny new sessions and invalidate existing sessions according to binding and materializer teardown rules.

### INV-5 TTL boundedness
No session may outlive the lesser of the request TTL, the materializer maximum TTL, the binding override, the backend lease, or the current trust epoch.

### INV-6 Non-exportable stays non-exportable
A binding marked non-exportable SHALL NOT be paired with a materializer whose surface or handle semantics imply reusable export.

### INV-7 Local workstation stores are not global authority
`os-keychain-bootstrap` and `os-keychain-ref` profiles SHALL be treated as local bootstrap or user-side profiles unless an explicit policy says otherwise.

## 11. Sheaf interpretation

Let:

- `Back(U)` be backend authority and trust-boundary choices over context `U`;
- `MatProf(U)` be materializer choices over `U`;
- `Bind(U)` be admissible profile bindings;
- `Sess(U)` be admissible local materialization sessions;
- `Ev(U)` be evidence.

A good design has:

- `Back`, `MatProf`, and `Bind` behaving like policy-bearing sheaves;
- `Sess` behaving like a sheaf of **local** admissible sessions only;
- actual plaintext surfaces still behaving like a presheaf with intentionally empty global sections;
- `Ev` behaving like a cosheaf, because evidence accumulates outward.

The backend is the global authority plane; the materializer is the local section; plaintext should never become a global section.

## 12. Tailoring still required

SECRET-0002 does not choose:

- a specific vendor or product,
- exact attestation providers,
- exact FIPS validation requirements,
- exact burn propagation SLA,
- exact backup site design,
- exact local cleanup primitives on every platform.

Those SHALL be tailored locally.

## 13. Reference alignment

This profile is aligned with:

- NIST SP 800-57 Part 1 Rev. 5 for lifecycle-oriented key management,
- NIST SP 800-130 for CKMS design topics,
- NIST SP 800-152 for CKMS requirements,
- NIST SP 800-193 for protect/detect/recover platform trust,
- FIPS 140-3 for cryptographic module requirements,
- systemd credential guidance for Linux service credential delivery,
- Apple Keychain / Keychain Services guidance for local OS-managed user secret storage.
