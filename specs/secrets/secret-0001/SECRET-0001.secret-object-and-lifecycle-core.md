# SECRET-0001 — Secret Object and Lifecycle Core
Version: 0.1  
Status: Draft normative core  
Date: 2026-04-12

## 1. Purpose

This document defines the minimum object model and lifecycle rules for secret management behind the bridge. It is meant to close the gap between **authorization** and **actual secret management**.

A conforming implementation SHALL define:

1. a `SecretObject` metadata record,
2. one or more `SecretVersion` records,
3. a lifecycle state machine,
4. a materialization contract,
5. revocation, recovery, and destruction rules,
6. audit events for every state transition and every materialization.

This document does **not** pick a particular backend. It is written so the backend may be a CKMS, HSM-backed service, KMS, Vault-class system, or a combination.

## 2. Relationship to the bridge

The bridge decides **whether** a consumer may request a secret-bound action.  
SECRET-0001 decides **what a secret is**, **how it lives**, **how it is rotated/revoked/destroyed**, and **how it may be materialized locally**.

The bridge SHALL NOT be treated as a substitute for lifecycle management.

## 3. Conformance

A system conforms to SECRET-0001 only if all of the following hold:

- All managed secrets are represented by `SecretObject` plus one or more `SecretVersion` records.
- Every active version has a defined cryptoperiod, storage reference, wrapping/protection mode, revocation policy, and materialization policy.
- Raw plaintext secret material is absent from ordinary metadata, audit records, logs, traces, and model context.
- Only `active` versions may be materialized for runtime use.
- Materialization is local, bounded, auditable, and TTL-limited.
- Revoked, retired, archived, or destroyed versions cannot be used for ordinary runtime materialization.
- Destruction is terminal for ordinary runtime use.
- Recovery never silently resurrects a known-compromised version into the same trust epoch.

## 4. Core model

### 4.1 SecretObject

A `SecretObject` is the canonical metadata record for one logical secret.

It SHALL identify:

- the secret’s class,
- ownership and administrative responsibility,
- domain and labels,
- lifecycle policy,
- materialization policy,
- recovery policy,
- one or more versions,
- audit anchors.

A `SecretObject` SHALL NOT embed raw plaintext secret material.

### 4.2 SecretVersion

A `SecretVersion` is one concrete generation/import/derivation of secret material associated with a `SecretObject`.

A version SHALL carry at least:

- `version_id`,
- `state`,
- `epoch`,
- provenance,
- storage reference,
- protection/wrapping information,
- cryptoperiod,
- revocation data,
- timestamps,
- audit trace anchors.

A version MAY refer to externally managed secret material by reference rather than by local ciphertext, but the reference SHALL still be bound to the same lifecycle and audit rules.

### 4.3 Secret classes

At minimum, implementations SHOULD distinguish among:

- password
- api-token
- database-credential
- oauth-client-secret
- symmetric-key
- asymmetric-private-key
- asymmetric-keypair
- certificate-keypair
- signing-key
- wrapping-key
- recovery-share
- bootstrap-secret
- seed
- dynamic-credential-template

A class MAY refine policy defaults such as maximum TTL, backup rules, escrow rules, or dual-authorization requirements.

## 5. Lifecycle states

The lifecycle state machine is version-oriented.

### 5.1 States

- `staged`: generated, imported, or restored, but not yet usable.
- `active`: usable for runtime materialization.
- `suspended`: temporarily blocked from materialization.
- `revoked`: permanently blocked for future runtime materialization.
- `retired`: superseded by a newer version; not for ordinary runtime materialization.
- `archived`: moved off the hot path for evidentiary retention or controlled recovery.
- `destroyed`: terminal state; ordinary secret use is impossible.

### 5.2 Required transition rules

Allowed transitions are:

- `∅ -> staged` by generate, import, derive, or restore
- `staged -> active` by activate
- `active -> suspended` by suspend
- `suspended -> active` by unsuspend
- `active -> revoked` by revoke
- `suspended -> revoked` by revoke
- `active -> retired` by rotate-forward or retire
- `suspended -> retired` by retire
- `retired -> archived` by archive
- `revoked -> archived` by archive
- `archived -> staged` by restore, subject to recovery policy
- `retired -> destroyed` by destroy
- `revoked -> destroyed` by destroy
- `archived -> destroyed` by destroy

No other transition SHALL occur.

### 5.3 State semantics

- `active` is the only ordinary state from which runtime materialization is allowed.
- `suspended` is reversible; `revoked` is not.
- `retired` indicates orderly replacement, not compromise by itself.
- `revoked` SHALL invalidate future runtime materialization even if ciphertext still exists.
- `destroyed` SHALL be terminal.
- A restore from `archived` SHALL create a new or freshly staged trust context; it SHALL NOT silently erase evidence that an earlier version had been archived, revoked, or compromised.

## 6. Materialization

### 6.1 General rule

Secret materialization SHALL be treated as a separate, local act.

A materialization SHALL be bound to:

- a `SecretObject`,
- a specific `SecretVersion`,
- a consumer identity,
- a host or workload context,
- a method,
- a TTL,
- an audit trace.

### 6.2 Allowed methods

Implementations MAY support methods such as:

- `fd-pass`
- `memfd`
- `unix-socket`
- `tmpfs-file`
- `agent-proxy`
- `cloud-kms-decrypt`
- `os-keychain-ref`

`env-var` materialization SHOULD be disabled by default and SHALL require explicit policy opt-in.

### 6.3 Required properties

A conforming materialization grant SHALL:

- never inline raw plaintext in ordinary audit output,
- bind to one consumer,
- carry an expiry,
- be revocable by epoch or handle invalidation,
- carry exportability = false unless explicitly approved,
- specify destruction on expiry or consumer exit.

### 6.4 Denial rules

Materialization SHALL be denied when any of the following hold:

- the version is not `active`,
- the bridge is in `burn` mode,
- the requested method is not allowed by policy,
- the requested TTL exceeds policy,
- the consumer binding does not match policy,
- the version epoch is stale or revoked,
- the workload or host attestation policy fails.

## 7. Rotation, revocation, recovery, destruction

### 7.1 Rotation

Rotation SHALL create a new version.  
A rotation SHALL NOT overwrite history.

If overlap is permitted, the overlap window SHALL be explicit and bounded.  
Outside the overlap window, the older version SHALL transition to `retired` or `revoked`.

### 7.2 Revocation

Every runtime-usable secret class SHALL define:

- a revocation authority,
- a propagation target or channel,
- a maximum propagation delay,
- the epoch or version field used to invalidate outstanding grants.

Revocation SHALL block future materialization immediately in the controlling authority, even if downstream consumers take additional time to observe the revocation signal.

### 7.3 Recovery

Recovery SHALL be policy-driven.

For `wrapping-key`, `recovery-share`, and similarly sensitive classes:

- split knowledge or quorum SHOULD be used,
- restore SHOULD require dual authorization,
- restored material SHALL enter `staged`, not `active`,
- restore SHALL record provenance and recovery basis.

Known-compromised material SHALL NOT be restored directly into ordinary active runtime use.

### 7.4 Destruction

Destruction SHALL be terminal for ordinary runtime use.

A destruction event SHALL specify:

- what was destroyed,
- which storage locations or references were affected,
- who approved it,
- whether recovery capability remains,
- evidence of completion or residual exceptions.

If destruction leaves escrow or offline backup copies intact, that SHALL be stated explicitly; otherwise the audit record is misleading.

## 8. Invariants

A conforming implementation SHALL preserve these invariants.

### INV-1 Metadata plaintext prohibition
`SecretObject`, `SecretVersion`, `SecretEvent`, and `MaterializationGrant` records SHALL NOT contain raw plaintext secret values.

### INV-2 Local-only materialization
Raw secret values SHALL exist only in a local execution context and for bounded time.

### INV-3 Active-only use
Only `active` versions may be used for ordinary runtime materialization.

### INV-4 Bounded authority
A materialization grant SHALL NOT outlive the lesser of:
- the requested TTL,
- the class policy maximum,
- the version expiry,
- the bridge/issuer epoch validity.

### INV-5 Epoch invalidation
Revocation or burn SHALL invalidate outstanding grants through epoch or equivalent freshness checking.

### INV-6 Non-erasable history
Rotate, revoke, archive, restore, and destroy SHALL create audit evidence; they SHALL NOT silently rewrite history.

### INV-7 Destroyed is terminal
A `destroyed` version SHALL NOT transition to any other state.

### INV-8 Recovery is not concealment
Recovery SHALL preserve evidence of prior compromise, revocation, archive, or destruction decisions.

## 9. Sheaf interpretation

For a context `U`, let:

- `Meta(U)` be secret metadata and policy,
- `Lease(U)` be admissible local secret leases or grants,
- `Mat(U)` be actual local materializations,
- `Rec(U)` be recovery authorities and backup relationships,
- `Ev(U)` be evidence.

A good design has:

- `Meta` behaving like a sheaf of consistent metadata/policy,
- `Lease` behaving like a sheaf of admissible local authority,
- `Mat` behaving like a presheaf whose global sections are intentionally empty or trivial,
- `Ev` behaving like a cosheaf that accumulates evidence upward.

In other words: **metadata and policy may glue; plaintext should not.**

## 10. Minimum assessment checklist

Before calling a system “secret management,” the following SHALL be answerable for each secret class:

1. Where is the secret born?
2. How is it generated or imported?
3. Where does it live at rest?
4. Under what protection boundary does it live?
5. Who may activate it?
6. Who may materialize it?
7. How long may plaintext exist locally?
8. How is rotation triggered and recorded?
9. How is revocation propagated?
10. What is the recovery path?
11. What is the destruction path?
12. What evidence remains afterward?

## 11. Tailoring still required

This core does not choose:

- the concrete backend or cryptographic module,
- exact label taxonomies,
- attestation providers,
- revocation SLAs,
- dual-authorization roster,
- escrow/quorum roster,
- retention durations,
- break-glass criteria.

Those MUST be tailored locally.

## 12. Reference alignment

This core is aligned with:

- NIST SP 800-57 Part 1 Rev. 5 for lifecycle-oriented key management,
- NIST SP 800-130 for CKMS design specification topics,
- NIST SP 800-152 for CKMS requirements,
- NIST SP 800-193 for platform trust, detection, and recovery,
- NIST SP 800-53A Rev. 5 for assessment methodology.

