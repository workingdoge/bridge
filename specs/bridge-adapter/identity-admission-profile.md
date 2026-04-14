# Bridge Identity Admission Profile

## Status

This file is a bridge-owned profile note.

Read it after:

- `adapter-contract.md`
- `../TYPE-FAMILIES.md`
- `../secrets/secret-0002/SECRET-0002.backend-and-materialization-profile.md`
- `../secrets/secret-0003/SECRET-0003.provider-integration-attestation-audit-deployment.md`
- `../bridge-premath-0001/BRIDGE-PREMATH-0001.premath-gluing-profile.md`

The normative schema and contract surfaces remain the source of truth for
object shape, policy input, decision effects, and materialization handoff.
This note does not replace them.

## Purpose

This note profiles local identity-admission semantics onto the active bridge
domain stack.

Its job is to say how to read bridge authorization and secret-bound handoff in
terms of:

- principal presentation,
- assertion,
- admission,
- entitlements, and
- obstructions.

The goal is not to define identity for all systems.
The goal is to give the bridge suite a precise local identity reading over the
existing `Ingress`, `Authority`, `Admission`, and `Realization` families.

## Boundary

The ownership split is:

- the general local identity and admission semantic core is upstream of
  `bridge`,
- Premath owns reusable kernel and admissibility law when those laws are
  promoted into the Premath spec tree,
- `bridge` owns the domain-specific realization profile for bridge requests,
  authoritative provider facts, policy decisions, and secret-bound handoff.

So this note is not Premath kernel doctrine.
It is also not a downstream runtime implementation guide.
It is the bridge-domain profile that sits between those two layers.

## Relationship to Premath

Premath matters here, but in a bounded way.

If the reusable layer of this work hardens, Premath is the right home for the
kernel or admissibility claims such as:

- locality of validity scopes,
- refinement under narrower context,
- gluing only from compatible local presentations,
- witness-bearing rejection and admission boundaries.

Bridge does not own those reusable laws.
Bridge owns the bridge-specific realization of those ideas.

`BRIDGE-PREMATH-0001` already gives the bridge-specific Premath gluing profile:

- shared execution contexts,
- admissible refinements,
- overlap objects,
- bridge-to-secret seam,
- glued bundles.

This note is narrower.
It says how principal presentation and admission should be read inside that
bridge-specific context geometry.

## Scope

This note defines:

- the local bridge validity scopes for identity-admission reasoning,
- the mapping from identity-admission terms onto the bridge type families,
- the reading of bridge decisions as admitted or non-admitted authority,
- the local entitlement surface carried by an accepted bridge decision,
- the distinction between bridge identity-admission obstructions and Premath
  gluing or compatibility failures.

This note does not define:

- a new generic identity model,
- one provider-specific identity protocol,
- one deployment-specific runtime binding,
- one new bridge schema,
- one new planner or sidecar implementation,
- one universal issuer or actor directory for all deployments.

## Local Scope Geometry

The relevant validity scope in bridge is not a tenant-wide identity record.
It is a bounded secret-bound request context.

A bridge-local identity-admission scope is determined by at least:

- one `AuthorizeRequest`,
- the witness and call facts bound to that request,
- the authoritative fact set resolved into `ProviderResults`,
- the deployment profile and provider catalog in force,
- the current mode and epoch surfaces,
- the resource-to-secret seam, including `binding_id`,
- the requested method and requested TTL,
- the selected decision stage, such as admission only or secret-bound handoff.

Typical scopes include:

- one request before authoritative provider resolution,
- one authoritative request context after `ProviderResults` assembly,
- one admitted or denied bridge decision over a concrete resource-to-secret
  seam,
- one non-materializable or materializable handoff into
  `MaterializationPlanRequest`,
- one issued or denied `MaterializationSession`.

Refinement in bridge therefore includes:

- tightening requested TTL,
- narrowing requested method,
- narrowing secret version or binding,
- refreshing authoritative provider facts,
- moving into more restrictive mode,
- advancing from bridge decision to secret-bound planning without widening
  authority.

## Term Mapping

| General term | Bridge profile reading |
| --- | --- |
| validity scope | one secret-bound request context under active provider facts, deployment profile, mode state, and seam binding |
| principal presentation | the bridge-local appearance of the actor, consumer, witness issuer, and verifier surfaces bound to one request |
| assertion | the request package together with witness material, authoritative provider facts, policy assembly, and any resulting handoff object |
| admitted principal | a principal presentation accepted for one bounded bridge decision context |
| entitlements | the effective authority bounds carried by an `accept` decision and preserved into the handoff |
| obstruction | a typed reason the request or its presenter cannot be admitted or cannot proceed to materialization |

This is a profile mapping only.
It does not claim that the current bridge schemas already contain every field a
more general identity doctrine might eventually standardize.

## Principal Presentation in Bridge

A principal presentation in bridge is the local appearance of the requestor and
its supporting identity surfaces inside one request context.

The relevant bridge surfaces are distributed across:

- the witness inside `AuthorizeRequest`,
- the caller's requested tool, resource, and session nonce,
- subject and consumer identity surfaces derived during provider resolution,
- attestation results and posture bindings,
- issuer, key-epoch, and revocation surfaces,
- verifier and deployment-profile identities,
- mode and audit authority identities.

Under this reading:

- issuer corresponds to the witness issuer and any authoritative issuer or
  key-epoch surfaces used during validation,
- subject corresponds to the actor or workload requesting the bridge action,
- credential class corresponds to the active witness, attestation, and
  proof-of-possession regime,
- scope corresponds to the bounded request context above,
- validity corresponds to freshness-bounded provider facts, revocation
  snapshots, and the active mode or epoch surfaces.

Bridge therefore does not start from a global user table.
It starts from a local presented request with authoritative identity facts
resolved around it.

## Assertion in Bridge

A bridge assertion is never just the raw `AuthorizeRequest`.

The raw request is only untrusted ingress.
The meaningful assertion package grows as the bridge stack resolves and narrows
authority:

1. ingress assertion:
   raw request plus witness and call facts
2. authority-resolved assertion:
   request plus `ProviderResults`, attestation, revocation, time, mode, and
   deployment facts
3. admission assertion:
   assembled `PolicyInput` plus resulting `Decision`
4. realization-bound assertion:
   secret-bound `MaterializationPlanRequest` and resulting
   `MaterializationSession`, when the bridge decision effect is materializable

This matches the bridge contract already in force:

- the adapter trusts only verified witness material and authoritative provider
  results,
- caller-supplied preflight authority is not trusted,
- the bridge-to-secret handoff must not widen effective authority while moving
  from decision to materialization planning.

## Admission in Bridge

The admission operator in bridge is the adapter plus policy layer acting over
the assembled request context.

Operationally, that means:

- validate the request and witness,
- resolve authoritative facts,
- assemble `PolicyInput`,
- evaluate policy into `Decision`,
- if secret-bound, derive `MaterializationPlanRequest`,
- permit materialization only from an `accept` effect and never from `deny` or
  `burn`.

The identity-admission reading is:

an `accept` decision means the presented principal has been admitted for one
bounded bridge action under one bounded secret-bound scope.

That admission is local.
It does not imply general administrative standing outside the current request
context.

## Admitted Principal and Entitlements

Bridge does not need a standalone `AdmittedPrincipal` schema to reason
correctly.
It is enough to treat admission as the local outcome of the bridge decision
surface.

The entitlement surface carried by an admitted bridge decision is exactly the
bounded authority the bridge contract says may survive into downstream
realization.

The relevant bridge-local entitlements include:

- `DecisionEffect`
- requested and effective method
- requested and effective TTL
- non-exportability
- materialization budget
- binding and seam constraints
- consumer identity bound to the resulting session
- allowed backend and materializer path

This is the right bridge reading of entitlements because bridge authority is
not an abstract role lattice first.
It is a bounded action lattice:

- may this actor attempt this action,
- over this secret seam,
- by this method,
- for this long,
- under this mode,
- with this export or non-export boundary.

No silent widening is allowed.
That is already bridge law.
The handoff into `MaterializationPlanRequest` preserves bridge-derived
authority bounds; it does not mint stronger authority downstream.

## Obstructions

Identity-admission obstructions in bridge include at least:

- invalid or unverifiable witness,
- proof-of-possession failure,
- revoked issuer or revoked witness identity,
- stale or missing authoritative time,
- failed or stale attestation,
- unsupported or denied delegation,
- unavailable or unverifiable provider result,
- mode state requiring deny or burn,
- resource-policy denial,
- consumer identity mismatch,
- non-materializable decision effect,
- revocation or epoch state dominating a stale local allow path.

These are bridge-domain admission obstructions.
They are not the same thing as Premath gluing failure.

## Boundary to Premath Gluing

`BRIDGE-PREMATH-0001` gives the bridge-specific context, refinement, overlap,
and gluing profile.
That matters here, but it is a different layer.

The key distinction is:

- bridge identity-admission obstructions answer whether a presented request may
  be admitted and carried toward secret use,
- Premath or bridge-Premath compatibility witnesses answer whether local charts
  or overlap objects fit together coherently under the chosen gluing profile.

Those two layers may interact, but they are not interchangeable.

For example:

- a revoked issuer is a bridge admission obstruction even if no gluing problem
  exists,
- an incompatible overlap witness is a compatibility or gluing problem even if
  the raw request identity is otherwise acceptable.

So Premath contributes the reusable locality or gluing law vocabulary, while
bridge keeps authority over the domain-specific admission surface.

## Reading the Bridge Type Families Through This Profile

The active bridge families can be read in this order:

1. `Ingress` gives the untrusted request and requested action shape.
2. `Authority` resolves the trustworthy local identity and posture facts.
3. `Admission` assembles those facts into `PolicyInput` and yields bounded
   decision authority.
4. `Realization` carries that bounded authority into secret-bound planning and
   session issuance without widening it.
5. `Audit` preserves the evidence chain needed to explain the admission outcome
   later.

That ordering is the bridge-local identity-admission story.

## Promotion Boundary

This note should become schema or contract work only if it exposes a concrete
gap such as:

- missing actor or issuer identity fields,
- missing reason-code classes that block deterministic admission reporting,
- missing authority-bound fields in `Decision` or
  `MaterializationPlanRequest`,
- missing links between admission outcome and audit identity.

Until then, the correct next step is profile clarity, not schema churn.
