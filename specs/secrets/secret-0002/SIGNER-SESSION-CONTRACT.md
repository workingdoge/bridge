# SECRET-0002 Signer Session Contract

Status: Draft adjunct contract

This note refines the existing `signing-key` realization path into a narrow
signer-session edge for downstream consumers.

It is intentionally types-first.
It is not a free-form signer DSL.

## Purpose

`SECRET-0002` already defines:

- `MaterializationPlanRequest`
- `MaterializationSession`
- signing-key bindings
- unix-socket and agent-proxy materializers

What it leaves implicit is the small operation surface a conforming signer
broker exposes once a signing session has been issued.

This note makes that edge explicit so a downstream repo can move from direct
keystore access toward:

- a session-open artifact,
- a typed composite open-session artifact when the downstream protocol needs
  more than a bare handle,
- a narrow local handle such as `SIGNER_SOCKET`,
- typed sign request/response messages,
- burn/revoke/expiry semantics carried by the session.

## Design rule

The stable semantic center is a set of types, not a mini language.

Conforming implementations SHOULD use:

- existing `MaterializationSession` as the session-open record,
- `SessionOpenArtifact` when the protocol requires additional open-session
  settlement material beyond the issued session,
- a bounded handle such as `socket-ref` or `opaque-handle`,
- typed `SignatureRequest` and `SignatureResponse` objects,
- repo-local protocol transport only as a realization detail.

A transport may choose JSON over a Unix socket, an agent framing protocol, or
another narrow local request/response mechanism, but that transport MUST NOT
be treated as the canonical contract.

## Session-open relation

For signer use, the canonical session-open artifact remains
`MaterializationSession`.

Some downstream protocols need a composite settlement artifact in addition to
the issued session record. In those cases, the conforming extension type is
`SessionOpenArtifact`.

A signing session is conforming only when all of the following hold:

- `secret_class = signing-key`
- `decision = allow`
- `bridge_decision_effect = accept`
- `constraints.non_exportable = true`
- `handle.kind ∈ {socket-ref, opaque-handle}`
- `backend_operation.kind = sign-proxy`

The session-open artifact carries:

- bridge trace and upstream decision anchors,
- secret and binding identity,
- session epoch and expiry,
- allowed consumer identity,
- revalidation triggers and teardown actions,
- the local signer handle reference.

When the downstream protocol requires an explicit open-settlement artifact,
`SessionOpenArtifact` carries the bounded protocol-specific material derived
from the session and authority context without widening into reusable key
material.

## Type surface

### 1. Unlock bootstrap

Unlock bootstrap is not the signing authority.

Examples:

- macOS Keychain password lookup
- password file
- workstation-local bootstrap token

This note does not standardize bootstrap payloads because they remain local
consumer policy.

### 2. Approval authority

Approval is also not the signing authority.

Examples:

- passkey assertion
- Touch ID gate
- human approval record

Approval material may gate session issuance, but it does not replace the
session or the signer operation types.

### 3. Signing authority

The signing authority is the backend named by the selected
`BackendProfile` and `BackendBinding`.

Examples:

- HSM-rooted signer
- remote signer backend
- local encrypted keystore

### 4. Session open

The session-open type is `MaterializationSession`.

The local broker may project one environment variable or launch argument from
this type, such as:

- `SIGNER_SOCKET`
- `SIGNER_HANDLE_REF`

but those are local bindings over the canonical session type, not replacements
for it.

### 5. Signature request

`SignatureRequest` is the typed operation request carried over the local signer
transport.

It identifies:

- the session,
- the requested signing operation,
- the payload or payload reference,
- the caller trace metadata needed for audit and replay defense.

### 6. Signature response

`SignatureResponse` is the typed result of that operation.

It identifies:

- whether the operation was allowed,
- the session and request it corresponds to,
- the produced signature or opaque signature reference,
- deny reasons when refused.

### 7. Session open artifact

`SessionOpenArtifact` is the typed composite artifact returned when a
downstream protocol needs explicit open-session settlement material after a
`MaterializationSession` has been issued.

It identifies:

- the session and bridge trace it is bound to,
- the artifact action and credential family it serves,
- the signed open transaction bytes or equivalent open operation bytes,
- the deterministic `channel_id`,
- the initial `cumulative_amount`,
- the initial voucher signature or opaque voucher reference,
- deny reasons when the session cannot be opened.

## Minimal protocol

The minimal protocol is:

1. obtain a conforming `MaterializationSession`
2. if needed by the downstream protocol, derive one `SessionOpenArtifact`
3. project the local handle from `handle.ref`
4. send one `SignatureRequest`
5. receive one `SignatureResponse`
6. close, expire, revoke, or burn the session

That is a small typed protocol, not a general-purpose signer language.

## Session invariants

A conforming signer broker SHALL:

- reject requests for nonexistent, expired, revoked, denied, or burned
  sessions;
- reject open-artifact derivation for nonexistent, expired, revoked, denied, or
  burned sessions;
- reject requests whose consumer identity does not match the session binding;
- refuse to widen a non-exportable session into reusable key material;
- emit deny responses rather than silently downgrading policy failures;
- treat burn, epoch change, or attestation loss as immediate revalidation
  triggers.

## Downstream guidance

Downstream repos SHOULD move from:

- direct keystore or key access in the client process

toward:

- `MaterializationSession`
- `SessionOpenArtifact` when a session-class protocol needs explicit
  open-settlement material
- local `socket-ref` or `opaque-handle`
- typed `SignatureRequest`
- typed `SignatureResponse`

The bridge-owned contract stops there.

Concrete broker/server implementation remains downstream until it stabilizes.
