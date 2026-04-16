# Bridge KB Proof Boundary

## Purpose

This note defines the smallest bridge-owned proof seam for work that touches
the upstream `NERVE-KB` stack and the carried `kurma` realization surface.

Its job is not to make `bridge` the semantic home of `NERVE-KB`, and it is not
to make `bridge` a generic knowledge runtime.

Its job is to state what `bridge` may consume as a bridge-domain proof or
realization surface, what remains upstream semantic law, and what remains
carried runtime or compiler work.

## Topology

This seam is a `2`-simplex.

- vertex A: `nerve`
  - canonical owner of the `NERVE-KB` semantic substrate
- vertex B: `kurma`
  - carrier or runtime realization over `Premath -> KCIR`
- vertex C: `bridge`
  - first bridge-domain proof or consumer seam

The common contract is:

- the `NERVE-KB` witness-carrying semantic substrate as carried through
  `Premath -> KCIR` into a bridge-domain proof surface

## Owner Split

### Upstream `nerve`

`nerve` remains the semantic home of:

- typed knowledge objects,
- context, patch, and gluing semantics,
- vector and retrieval doctrine,
- query-planner and witness-frontier semantics,
- answer and session memory doctrine,
- promotion, compaction, sync, trust, and proof semantics.

`bridge` MUST NOT restate or redefine those semantics here.

### `kurma`

`kurma` remains the carried home of:

- `Premath -> KCIR` realization,
- storage and runtime layout,
- query planning and retrieval execution,
- witness realization and receipt carriage,
- compiler or runtime method over the semantic substrate.

`bridge` MUST NOT absorb those runtime or compiler responsibilities merely
because it is the first proof consumer.

### `bridge`

`bridge` may own only the bridge-domain proof seam:

- how bridge-owned witness, admission, interpretation, realization, and audit
  families consume a carried semantic or witness surface,
- what bridge-specific realization or profile constraints are required for the
  seam to remain bridge-correct,
- and what bridge must demand before a carried surface is admissible for a
  bridge-domain proof.

## Bridge-Owned Consumption Surface

For this class of seam, the admissible bridge-owned question is:

> what bridge-domain artifact or profile note is needed so a carried semantic
> or witness surface can participate honestly in bridge admission,
> interpretation, realization, or audit?

That means bridge may consume the seam through existing bridge families:

- `Interpretation`
- `Admission`
- `Realization`
- `Audit`

and through the bridge-specific Premath realization profile already staged in
`BRIDGE-PREMATH-0001`.

## What Bridge Must Not Re-Own

`bridge` MUST NOT turn this seam into:

- a generic knowledge base,
- a generic retrieval engine,
- a generic query planner,
- a generic session-memory runtime,
- or a replacement semantic substrate for `NERVE-KB`.

It also MUST NOT widen into:

- downstream provider bindings,
- local secret files,
- funded runtime proof,
- or operator-control projections that belong in a consumer such as `tusk`.

## Smallest Honest Bridge Artifact

The smallest honest bridge-owned artifact for this seam is:

- one bridge-domain boundary or profile note that states:
  - what part of the carried seam bridge consumes,
  - which bridge type families are in scope,
  - what bridge requires before that seam is admissible,
  - and what remains upstream or carried out of scope.

That is enough to prove the bridge-side boundary without prematurely building a
runtime.

## Validation Rule

When shaping or reviewing future bridge work in this area, ask:

1. Is the slice still bridge-domain, or has it turned into `NERVE-KB`
   semantics?
2. Is the slice still a bridge proof seam, or has it turned into `kurma`
   carriage/runtime work?
3. Is the slice still a bridge profile or boundary note, or has it drifted into
   downstream provider/runtime proof?

If the answer to any of those is yes, split the issue and route it back to the
owning repo.

## Follow-Up Split

Use this default execution order:

1. upstream semantic cleanup in `nerve` when the seam is semantically unclear
2. carried runtime or compiler work in `kurma` when the seam is method-unclear
3. bridge-domain proof note or realization-profile work in `bridge`
4. later consumer projection work in `tusk` or another consumer repo

This keeps the first live proof in the first real consumer without turning that
consumer into the owner of the whole stack.
