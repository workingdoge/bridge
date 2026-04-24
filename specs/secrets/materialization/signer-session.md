# Signer Session

Canonical source:

- [`SIGNER-SESSION-CONTRACT.md`](../secret-0002/SIGNER-SESSION-CONTRACT.md)
- [`signature-request.schema.json`](../secret-0002/schemas/signature-request.schema.json)
- [`signature-response.schema.json`](../secret-0002/schemas/signature-response.schema.json)

The signer-session edge narrows `signing-key` materialization into a typed
operation surface.

The session-open artifact remains `MaterializationSession`. For a conforming
signing session, the handle is a bounded `socket-ref` or `opaque-handle`, and
the backend operation is a non-exportable `sign-proxy`.

The local broker may choose JSON over a Unix socket, agent framing, or another
narrow transport. That transport is a realization detail; the stable contract
is the session plus `SignatureRequest` and `SignatureResponse`.
