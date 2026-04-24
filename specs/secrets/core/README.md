# Secret Core

This is the clean documentation view for `SECRET-0001`.

Use this directory when you want the logical secret model without backend,
materializer, provider, or deployment detail. The canonical imported bundle
still lives under [`../secret-0001/`](../secret-0001/).

## Topics

- [`secret-object.md`](secret-object.md) maps the `SecretObject` and
  `SecretVersion` records.
- [`lifecycle.md`](lifecycle.md) maps version states, transitions, and events.
- [`class-policy.md`](class-policy.md) maps secret classes and lifecycle-core
  materialization policy.
- [`schemas/`](schemas/) points to the canonical `SECRET-0001` schemas.

## Boundary

`core/` owns the answer to:

- what a secret is;
- how versions move between lifecycle states;
- which class policy constrains ordinary use;
- which lifecycle event evidence must exist.

It does not choose the backend, issue a local runtime session, bind providers,
or define deployment truth. Those belong in [`../materialization/`](../materialization/)
and [`../provider-plane/`](../provider-plane/).
