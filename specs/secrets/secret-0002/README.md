# SECRET-0002

`SECRET-0002` is the **Realization** bundle. It takes an admitted secret-bound
action, a lifecycle-eligible secret, and fresh provider facts, then plans or
denies a bounded local materialization session.

It is the concrete bridge-to-secret session layer. It is not the logical secret
lifecycle owner and it is not the production provider plane. Read it with
[`../SUITE-FLOW.md`](../SUITE-FLOW.md).

## Surface

- `SECRET-0002.backend-and-materialization-profile.md`
- `schemas/` backend, materializer, binding, plan-request, and session schemas
- `SIGNER-SESSION-CONTRACT.md` narrow signer-session edge over issued sessions
- `WITNESS-REALIZATION-CONTRACT.md` bridge-local realization vocabulary over
  session, signer, audit, and validation artifacts
- `policy/profile-matrix.yaml`
- `examples/` generated materialization-session examples
- `python/reference_planner.py` as reference material, not runtime authority

## Inputs and Outputs

Inputs:

- bridge admission artifacts, especially bridge decision effect and authority
  bounds;
- `SECRET-0001` `SecretObject` / `SecretVersion` lifecycle and class policy;
- `SECRET-0003` provider facts for attestation, revocation, mode, and audit
  readiness;
- selected `BackendProfile`, `MaterializerProfile`, and `BackendBinding`.

Outputs:

- `MaterializationSession` with either an issued bounded handle or a denial
  record;
- optional `SignatureRequest` / `SignatureResponse` for signing-key sessions;
- `WitnessRealizationRecord` as bridge-local coherence metadata over the
  session, signer, audit, and validation artifacts.

## Adjacent Artifacts

`SECRET-0001` also contains a generic `MaterializationGrant`. Treat that as the
lifecycle-core lease abstraction. `SECRET-0002` `MaterializationSession` is the
runtime realization artifact that names backend operation, handle kind,
revalidation triggers, teardown actions, and deny reasons.

`SECRET-0003` contains `ProviderDecision`. Treat that as provider-readiness
evidence, not as a replacement for either bridge admission or
`MaterializationSession`.

The original bundle did not include a dedicated README for this family, so this
repo adds this wrapper note to keep the imported secret surface consistent.
