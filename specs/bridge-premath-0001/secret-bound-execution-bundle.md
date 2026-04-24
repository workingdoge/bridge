# Secret-Bound Execution Bundle

This note is the reader-facing fibre-bundle view of `BRIDGE-PREMATH-0001`.

The Premath kernel doctrine stays upstream in `fish/sites/premath/`. Bridge
only instantiates that doctrine for the bridge adapter plus secret suite.

## Bundle Shape

Treat each admissible secret-bound execution as a fibre over a Premath context:

```text
base category C:
  admissible Premath contexts

fibre over Gamma:
  bridge/secret artifacts valid in Gamma

local charts:
  BridgeChart
  SecretCoreChart
  ProviderPlaneChart
  MaterializationChart
  AuditChart

gluing:
  compatible chart sections assemble into Def(Gamma)
```

The bundle IDs `SECRET-0001`, `SECRET-0002`, and `SECRET-0003` are import
identities. They are not the runtime order. Runtime order is chart-sensitive:
provider facts from `SECRET-0003` may be needed before `SECRET-0002` can issue
a materialization session, and audit evidence from `SECRET-0003` closes the
event after the session or denial.

## Base

The base object is `PremathContext`.

It carries stable coordinates for:

- request and witness identity,
- interpretation identity,
- secret object and version,
- resource-to-secret binding,
- requested method and policy limits,
- provider facts and mode epoch,
- audit stream position.

Context morphisms are admissible refinements. Reducing TTL, narrowing scope,
selecting a concrete secret version, or refreshing provider facts may be
pullbacks. Widening authority, weakening non-exportability, resurrecting a
revoked version, or silently restoring from burn is not a pullback.

## Fibre

The fibre over `Gamma` is the groupoid of bridge/secret realizations valid in
that context.

In the current bridge surface, representative fibre objects are:

- bridge decision and policy input,
- `SecretObject` / `SecretVersion`,
- `ProviderDecision`,
- `MaterializationPlanRequest`,
- `MaterializationSession`,
- `AuditEnvelope`,
- `CompatibilityWitness`,
- `GluedBundle`.

Raw plaintext secret values are intentionally not global sections of this
bundle. If a deployment needs to model plaintext or local handles, it should do
so in a separate leaf-local presheaf outside `Def(Gamma)`.

## Charts

The clean chart view is:

| Chart | Compatibility bundle | Role |
| --- | --- | --- |
| `SecretCoreChart` | `SECRET-0001` | secret identity, version lifecycle, class policy |
| `ProviderPlaneChart` | `SECRET-0003` | provider catalog, deployment facts, attestation, revocation, mode |
| `MaterializationChart` | `SECRET-0002` | backend/materializer choice and bounded session issuance |
| `AuditChart` | `SECRET-0003` | durable audit envelope and checkpoint evidence |

This is why the docs have a non-linear shape. The suite is not a list; it is a
cover of one execution object.

## Overlaps

Charts glue through named overlap objects:

- `K_req`: request, witness, actor, tool, resource, and consumer identity,
- `K_secret`: secret/version plus resource-to-secret seam,
- `K_policy`: method, TTL, mode, confidentiality, integrity, exportability,
- `K_facts`: deployment, provider catalog, attestation, revocation, mode epoch,
- `K_audit`: trace, stream, sequence, payload hash, previous hash.

The overlaps are the review surface. A fixture is meaningful when it shows what
two charts must agree on, not merely which files were present.

## Sections And Obstructions

A successful allow path is a global section of `Def(Gamma)`: compatible local
sections glue into one audit-capable secret-bound execution object.

A denied or burned path is not a failure to produce evidence. It is an
obstruction to a usable materialization section. The conforming global object
still exists as a denial or burn record when it carries teardown and audit
evidence.

Examples:

- failed attestation obstructs a usable materialization session;
- revoked secret version obstructs a usable materialization session;
- burn mode obstructs new sessions and preserves teardown/audit obligations;
- TTL widening is not an admissible context refinement;
- restore creates a fresh base context rather than inverting burn.

## Fixture Rule

Bridge fixtures should therefore come in pairs when possible:

- a golden glued bundle showing descent succeeds for a usable execution path;
- an obstruction bundle showing why no usable materialization section exists.

The current starter fixtures are:

- `examples/example.glued-bundle.json`
- `examples/example.glued-bundle.burn-obstruction.json`
