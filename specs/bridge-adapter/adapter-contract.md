# Bridge Adapter Contract v0.2

This bundle wires the **external caller contract** to the existing
`input.preflight`, `input.events`, `input.runtime_request`,
`input.interpretation`, and `input.witness` policy contract.

## What the adapter is allowed to trust

The adapter may trust only:

- the signed witness after schema and signature verification,
- locally verified proof-of-possession facts,
- authoritative time,
- authoritative revocation results,
- authoritative mode/burn-controller results,
- authoritative resource policy lookup,
- authoritative attestation results,
- durable audit-sink status.

The adapter **MUST NOT** trust caller-supplied values for current mode, authoritative time, resource policy, revocation status, or preflight booleans.

## External request shape

The caller sends an `AuthorizeRequest` with:

- `witness`
- `call.requested_tool`
- `call.requested_resource`
- `call.source_domain`
- optional `call.destination_domain`
- optional `call.cross_domain`
- optional `call.payload_hash`
- `call.session_nonce`
- `call.rp_initiated`
- `call.pop_proof`

## Internal provider contract

Before evaluation, the adapter resolves `ProviderResults` from local or remote
authoritative providers. The provider results are then assembled into the
policy-engine input.

The adapter **SHALL** fail closed when any required provider is unavailable or returns unverifiable data.

## Assembly algorithm

1. Validate the authorize request and witness schemas.
2. Verify the witness signature.
3. Verify proof-of-possession against `witness.pop_key`.
4. Check issuer revocation and witness `jti` revocation.
5. Check replay state for the witness and bound context.
6. Resolve current mode from the burn/mode controller.
7. Resolve authoritative time.
8. Resolve attestation and compare it to `witness.posture_digest`.
9. Resolve source context, interpretation binding, and typed observation for
   the foreign observation when the input is not self-describing.
10. Canonicalize admitted tool, resource, and source-domain identity from the
    interpreted observation when present.
11. Resolve canonical resource policy for the canonicalized
    `requested_tool + requested_resource`.
12. Check subject/delegation authorization.
13. Check evidence sink readiness.
14. Assemble the policy input.
15. Emit a durable audit record for the request and the final decision.

## Fail-closed requirements

The adapter **MUST DENY** when:

- schema validation fails,
- signature verification fails,
- proof-of-possession fails,
- revocation status is unavailable or negative,
- authoritative time is unavailable,
- attestation freshness or match checks fail,
- interpretation is unavailable, `unknown`, `ambiguous`, or `stale`,
- resource policy lookup fails,
- audit sink is unavailable and no durable emergency queue exists.

The adapter **MUST BURN** rather than merely deny when the burn-trigger event set indicates systemic compromise or control-plane corruption.

## Burn semantics

The adapter does not decide burn policy by itself. It consumes authoritative burn triggers from the mode controller and assembles them into `input.events`. Once any burn trigger is true, the policy layer returns a burn decision and the adapter must:

- stop minting or redeeming across the relevant cut-set,
- preserve evidence,
- switch to safe/degraded handling,
- require fresh restore authorization and fresh key epoch before returning to normal.

## Secret-bound handoff

When the requested resource resolves to a secret binding, the adapter SHALL
assemble a `MaterializationPlanRequest` before any local secret materialization
path is attempted.

That handoff SHALL carry:

- bridge trace and witness identity,
- the bridge decision effect plus deny or burn reasons,
- bridge policy-input and decision references,
- explicit `binding_id` and resource-to-secret seam data,
- secret identity and class,
- consumer identity and requested method,
- bridge-derived authority bounds such as effective TTL and materialization
  budget.

The adapter SHALL NOT widen bridge effective authority while building this
handoff.

If the bridge decision effect is `deny` or `burn`, the adapter MAY still emit a
handoff object when local policy requires a denied materialization session for
audit continuity, but the downstream planner SHALL NOT issue a usable secret
handle from that non-accept effect.

## Canonicalization requirements

The adapter **SHALL** canonicalize:

- resource identifiers,
- domain identifiers,
- admitted tool/resource/domain identity from interpreted observations when
  interpretation is carried,
- content hashes,
- witness serialization before signature verification and witness hashing.

This prevents scope confusion, replay aliasing, and audit hash instability.

## Files in this bundle

- `schemas/authorize.request.schema.json`
- `schemas/source-context.schema.json`
- `schemas/interpretation-binding.schema.json`
- `schemas/interpreted-observation.schema.json`
- `schemas/interpretation-result.schema.json`
- `schemas/provider-results.schema.json`
- `schemas/policy-input.schema.json`
- `schemas/decision.schema.json`
- `schemas/audit-record.schema.json`
- `schemas/mode-command.schema.json`
- `schemas/mode-state.schema.json`
- `openapi/bridge-adapter.openapi.yaml`
- `provider-mapping.yaml`
- `python/reference_adapter.py`
