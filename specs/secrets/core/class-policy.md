# Class Policy

Canonical source:

- [`SECRET-0001.secret-object-and-lifecycle-core.md`](../secret-0001/SECRET-0001.secret-object-and-lifecycle-core.md)
- [`secret-class.defaults.yaml`](../secret-0001/policy/secret-class.defaults.yaml)
- [`materialization-request.schema.json`](../secret-0001/schemas/materialization-request.schema.json)
- [`materialization-grant.schema.json`](../secret-0001/schemas/materialization-grant.schema.json)

Class policy records the lifecycle-core defaults for a secret class: rotation
mode, maximum active age, overlap window, revocation SLA, allowed methods,
maximum TTL, recovery mode, and backup or escrow expectations.

`MaterializationRequest` and `MaterializationGrant` are the generic
lifecycle-core lease vocabulary. They describe whether class policy and version
state permit bounded use.

For runtime bridge-to-secret issuance, prefer the concrete
[`MaterializationPlanRequest`](../materialization/plan-request.md) and
[`MaterializationSession`](../materialization/session.md) vocabulary from
`SECRET-0002`. The lifecycle-core grant is an abstraction, not the final local
handle/session artifact.
