# Materialization Plan Request

Canonical source:

- [`SECRET-0002.backend-and-materialization-profile.md`](../secret-0002/SECRET-0002.backend-and-materialization-profile.md)
- [`materialization-plan-request.schema.json`](../secret-0002/schemas/materialization-plan-request.schema.json)

`MaterializationPlanRequest` is the normalized handoff from bridge admission
into secret materialization planning.

It carries:

- bridge request and witness identity;
- bridge decision effect and deny or burn reasons;
- references tying the handoff to policy input and decision artifacts;
- resource-to-secret seam data, including `binding_id`;
- secret identity and class;
- consumer identity and attestation basis;
- requested method and TTL;
- bridge-derived authority bounds;
- mode and bridge epoch.

`decision_effect != accept` is non-materializable. A planner may emit a denied
session for audit and teardown planning, but it must not issue a usable handle.
