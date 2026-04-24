# SECRET-0002 Witness Realization Contract

Status: Draft adjunct contract

This note defines the bridge-owned witness-realization vocabulary for
`SECRET-0002` signer and materialization artifacts.

It is not the bridge-adapter authority witness schema.
It is not a Premath kernel doctrine.
It is not a provider receipt format.

The purpose is narrower: name the typed bridge-local record that says how an
admitted or denied bridge action was realized, observed, validated, and carried
into the next session state.

## Boundary

Bridge owns this vocabulary where it is about:

- `MaterializationSession` issuance, denial, revocation, expiry, and teardown;
- `SignatureRequest` and `SignatureResponse` over a bounded signer session;
- bridge audit records, audit envelopes, and compatibility witnesses as
  evidence references;
- validator profiles that are specific to bridge materializers, signer brokers,
  provider sidecars, or bridge-specific Premath gluing.

Bridge does not own:

- generic Premath witness doctrine;
- provider-specific receipt bytes;
- funded runtime, wallet, Tempo, OpenAI, or payment policy;
- downstream secret file paths or local deployment proof.

## Vocabulary

The canonical bridge-local carrier is `WitnessRealizationRecord`.

It is a record over existing bridge artifacts. It does not replace
`MaterializationSession`, `SignatureRequest`, or `SignatureResponse`.

### Challenge

`Challenge` is the concrete bridge-domain question to be realized.

Examples:

- issue or deny a materialization session;
- sign or refuse a signature request;
- revoke, expire, burn, or tear down an active session;
- validate a bridge-specific compatibility witness.

### StateRead

`StateRead` is the bounded state observed before action selection.

For signer sessions it SHOULD include:

- `materialization_session_ref`;
- current `session_state`;
- current `bridge_decision_effect`;
- `signature_request_ref` when a sign operation is being evaluated;
- `signature_response_ref` when the realization already produced a result;
- authority, audit, or compatibility references needed to replay the decision.

### ActionSelection

`ActionSelection` names the chosen bridge-domain action and why that action is
admissible from the observed state.

Examples:

- `issue-session`;
- `deny-session`;
- `sign`;
- `refuse-signature`;
- `revoke-session`;
- `expire-session`;
- `tear-down-session`;
- `burn-session`.

### WitnessPlan

`WitnessPlan` states which artifact family will carry evidence for the selected
action and which validator profile is expected to judge it.

Artifact families include:

- `materialization-session`;
- `signature-request`;
- `signature-response`;
- `audit-record`;
- `audit-envelope`;
- `compatibility-witness`;
- `denial-reason`.

### WitnessArtifact

`WitnessArtifact` is the concrete evidence reference and digest.

It points at an existing bridge-owned artifact or downstream artifact reference
without embedding provider-local or payment-local bytes.

### ValidatorProfile

`ValidatorProfile` names the bridge-local validation context.

Validator profile kinds are:

- `bridge-adapter`;
- `secret-materializer`;
- `signer-broker`;
- `provider-sidecar`;
- `premath-gluing`.

The profile may cite bridge law references or upstream Premath profile
references, but it does not move that upstream law into `SECRET-0002`.

### ValidationResult

`ValidationResult` records the validator verdict.

Verdicts are:

- `accepted`;
- `denied`;
- `burned`;
- `stale`;
- `ambiguous`.

Denied, stale, burned, or ambiguous results MUST NOT be coerced into a usable
secret handle or successful signature.

### StateTransition

`StateTransition` records the next session state and any receipt reference.

For signer sessions, allowed state targets are the same session-state family as
`MaterializationSession`: `planned`, `issued`, `revoked`, `expired`, `denied`,
or `torn_down`.

## Signer-session realization

A conforming signer realization follows this shape:

1. read a conforming `MaterializationSession`;
2. read a `SignatureRequest` if the challenge is a sign operation;
3. select `sign` only if the session is issued, unexpired, non-exportable,
   bound to the requesting consumer, and still under an `accept` bridge decision
   effect;
4. emit a `SignatureResponse` with either a signature reference or deny reasons;
5. emit or reference audit material for the selected action;
6. record a `WitnessRealizationRecord` linking the challenge, state read,
   selected action, witness artifact, validation result, and next session state.

The record is a coherence carrier. It makes the realization shape inspectable
without turning a signer broker into a general-purpose proof engine.

## Invariants

A conforming `WitnessRealizationRecord` SHALL:

- preserve the bridge trace used by the underlying session or operation;
- reference existing session, request, response, audit, or compatibility
  artifacts rather than copying raw secret material;
- preserve `bridge_decision_effect` and session state;
- keep non-exportable signing sessions non-exportable;
- record refusals, stale state, burn state, and ambiguous validation explicitly;
- avoid provider-specific, wallet-specific, payment-specific, or funded-runtime
  fields.

It SHALL NOT:

- issue new authority by itself;
- widen a denied or burned session into a usable handle;
- replace `MaterializationSession`, `SignatureRequest`, or `SignatureResponse`;
- redefine Premath kernel witness doctrine inside bridge.

## Schema and example

The machine-checkable carrier is:

- `schemas/witness-realization-record.schema.json`

The signing-key example is:

- `examples/example.witness-realization.signing-key.json`
