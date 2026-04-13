# BRIDGE-PREMATH-0001 starter bundle

This bundle adds a Premath indexing layer on top of the uploaded bridge +
secret-management suite.

## Contents

- `BRIDGE-PREMATH-0001.premath-gluing-profile.md`
  - normative draft profile
- `ts/interfaces.ts`
  - starter interface surface
- `schemas/premath-context.schema.json`
  - shared context object
- `schemas/context-morphism.schema.json`
  - admissible refinement object
- `schemas/request-overlap.schema.json`
- `schemas/secret-overlap.schema.json`
- `schemas/policy-overlap.schema.json`
- `schemas/facts-overlap.schema.json`
- `schemas/audit-overlap.schema.json`
- `schemas/compatibility-witness.schema.json`
- `schemas/glued-bundle.schema.json`
- `examples/example.context.json`
- `examples/example.context-morphism.reduce-ttl.json`
- `examples/example.glued-bundle.json`

## What this bundle adds

- a single shared execution context
- explicit overlap keys for gluing
- explicit context morphisms for pullback
- an explicit bridge-to-secret seam
- a global glued object with compatibility witnesses

## What it intentionally does not do

- it does not put raw plaintext secret material in the global object
- it does not treat restore as an ordinary inverse to burn
- it does not claim `Sigma_f` / `Pi_f` support in the core profile

## Suggested next implementation step

Thread the overlap objects and `PremathContext` through the reference adapter,
planner, and sidecar so the existing suite can emit a `GluedBundle` directly.
