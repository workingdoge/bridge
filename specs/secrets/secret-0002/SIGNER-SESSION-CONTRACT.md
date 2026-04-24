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
- a narrow local handle such as `SIGNER_SOCKET`,
- typed sign request/response messages,
- burn/revoke/expiry semantics carried by the session.

## Design rule

The stable semantic center is a set of types, not a mini language.

Conforming implementations SHOULD use:

- existing `MaterializationSession` as the session-open record,
- a bounded handle such as `socket-ref` or `opaque-handle`,
- typed `SignatureRequest` and `SignatureResponse` objects,
- repo-local protocol transport only as a realization detail.

A transport may choose JSON over a Unix socket, an agent framing protocol, or
another narrow local request/response mechanism, but that transport MUST NOT
be treated as the canonical contract.

## Session-open relation

For signer use, the canonical session-open artifact remains
`MaterializationSession`.

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

## Minimal protocol

The minimal protocol is:

1. obtain a conforming `MaterializationSession`
2. project the local handle from `handle.ref`
3. send one `SignatureRequest`
4. receive one `SignatureResponse`
5. close, expire, revoke, or burn the session

That is a small typed protocol, not a general-purpose signer language.

## Witness realization

Signer sessions also participate in the `SECRET-0002` witness-realization
vocabulary defined in `WITNESS-REALIZATION-CONTRACT.md`.

That vocabulary layers a `WitnessRealizationRecord` over the existing signer
artifacts:

- `Challenge` identifies the bridge-domain operation, such as `sign` or
  `refuse-signature`;
- `StateRead` references the current `MaterializationSession` and, when
  present, the `SignatureRequest` and `SignatureResponse`;
- `ActionSelection` records the chosen signer-session action;
- `WitnessPlan` and `WitnessArtifact` name the artifact family carrying the
  evidence;
- `ValidatorProfile` names the bridge-local validation context;
- `ValidationResult` records `accepted`, `denied`, `burned`, `stale`, or
  `ambiguous`;
- `StateTransition` records the next session state or receipt reference.

This record is coherence metadata over the signer flow. It does not replace the
session, request, response, or audit artifacts, and it does not introduce
provider-specific receipt bytes into the bridge contract.

## Session invariants

A conforming signer broker SHALL:

- reject requests for nonexistent, expired, revoked, denied, or burned
  sessions;
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
- local `socket-ref` or `opaque-handle`
- typed `SignatureRequest`
- typed `SignatureResponse`

The bridge-owned contract stops there.

Concrete broker/server implementation remains downstream until it stabilizes.
