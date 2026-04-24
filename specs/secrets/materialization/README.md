# Materialization

This is the clean documentation view for `SECRET-0002`.

Use this directory when you want the concrete bridge-to-secret realization
surface: backend selection, materializer selection, binding, plan request,
session issuance or denial, signer operation, and witness realization.

The canonical imported bundle still lives under [`../secret-0002/`](../secret-0002/).

## Topics

- [`backend-profiles.md`](backend-profiles.md)
- [`materializer-profiles.md`](materializer-profiles.md)
- [`bindings.md`](bindings.md)
- [`plan-request.md`](plan-request.md)
- [`session.md`](session.md)
- [`signer-session.md`](signer-session.md)
- [`witness-realization.md`](witness-realization.md)
- [`schemas/`](schemas/)
- [`examples/`](examples/)

## Boundary

`materialization/` owns the answer to:

- which backend authority holds, unwraps, issues, or proxies the secret;
- which local last-mile path may expose a bounded handle or plaintext surface;
- which binding joins secret class, backend profile, materializer profile, and
  consumer kind;
- whether a `MaterializationSession` issues a usable handle or a denial record.

It does not define logical lifecycle state or provider authority. Those belong
in [`../core/`](../core/) and [`../provider-plane/`](../provider-plane/).
