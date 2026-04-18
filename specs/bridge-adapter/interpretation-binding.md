# Bridge Observation Interpretation Binding

This note defines the bridge-domain family that assigns stable meaning to
foreign observations after authoritative fact resolution and before admission
assembly.

It is not a decoder-cache note.

The semantic center is:

- which interpretation is admissible for a foreign observation in a given
  source context

Implementation mechanisms such as decoder registries, caches, parser tables,
and runtime memoization remain downstream realization choices.

## Why this family exists

Bridge already separates:

- `Ingress` for untrusted caller or foreign input
- `Authority` for authoritative facts resolved from trusted providers
- `Admission` for the bridge-owned assembled input and decision surface
- `Audit` for durable evidence and receipt material

What is still implicit is the meaning-assignment step between `Authority` and
`Admission`.

That step is needed whenever a foreign observation is not self-describing:

- contract logs and calldata
- versioned webhook payloads
- provider payload families whose schema changes over time
- source objects that keep one identifier while their runtime or schema changes

## Topology

The family should be read as:

```text
foreign observation
        |
        v
Ingress
        |
        v
Authority
resolve source facts, version facts, validity facts,
and other authoritative context required for interpretation
        |
        v
Interpretation
choose an admissible meaning profile for the observation
under the resolved source context
        |
        v
typed bridge-local observation
        |
        v
Admission
assemble bridge-owned admitted input or handoff objects
        |
        v
Audit
record which interpretation binding was used and why
```

The critical split is:

- `Authority` tells bridge what is true about the source context
- `Interpretation` tells bridge which meaning profile is admissible there
- `Admission` assembles the resulting typed material into bridge-owned decision
  or handoff objects

## Source context

Interpretation is indexed by source context, not merely by one foreign object
identifier.

The source context should be strong enough to carry:

- source profile identity
- network, venue, or domain coordinate
- source object identity
- runtime or schema identity
- payload facet identity such as selector, topic, route kind, or event type
- validity coordinate such as epoch, block height, version window, or other
  bounded context position

This is why contract address alone is not a sufficient interpretation key.

Proxy upgrades, implementation swaps, schema drift, and version windows are not
parsing accidents. They are changes in source context.

## Interpretation binding

An interpretation binding is the bridge-owned claim that:

- for source context `s`
- observation `o`
- meaning profile `p`

the profile `p` is admissible for interpreting `o` at `s`.

This family must allow at least:

- admitted interpretation
- unknown interpretation
- ambiguous competing interpretations
- stale interpretation whose validity window no longer matches the source
  context

Bridge should not force unknown or ambiguous observations directly into
`Admission`.

## Grothendieck reading

The clean reading is fibered.

- the base is the category of source contexts
- over each source context sits a family of admissible interpretation profiles
- bridge works in the total space of interpreted observations, not in a flat
  table of parser hints

In that reading:

- a decoder registry is one downstream realization of a chosen cleavage
- a cache is memoized realization of that choice
- audit records are witnesses of which lift was chosen for a concrete
  observation

So the bridge-domain object is not "decoder lookup".

It is:

- admissible interpretation binding over foreign source context

## Consequences for admission and audit

`Admission` should consume typed observations or typed facts whose
interpretation family has already been made explicit.

`Audit` should be able to name:

- the foreign observation identity
- the resolved source context
- the selected interpretation profile
- the authority basis for that selection
- the resulting typed observation or admitted handoff

That is stronger than merely recording that a payload was parsed.

It records that the bridge admitted a specific meaning assignment.

## Downstream realization note

Downstream repos such as `kurma` may realize this family with:

- local interpretation-binding registries
- local decoder caches
- lineage stores from raw observation to typed observation
- projection into carrier or receipt systems

Those runtime choices are downstream realization, not the canonical semantic
center of this family.

## Normative carrier surface

This note is not the only carrier of the family.

The normative bridge-owned carrier surface is:

- `schemas/source-context.schema.json`
- `schemas/interpretation-binding.schema.json`
- `schemas/interpreted-observation.schema.json`
- `schemas/interpretation-result.schema.json`

Those carriers are what the adapter, audit, and conformance surfaces consume.
