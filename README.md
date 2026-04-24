# Bridge

`bridge` is the domain home for the bridge adapter contract, the secret suite,
and bridge-specific realization profiles layered over Premath. This README is
written for downstream consumers — repos that import bridge as a Nix flake
input.

## Boundary

- **Premath kernel doctrine stays upstream** in `fish/sites/premath/`. If you need
  kernel types, depend on premath directly — bridge does not restate them.
- **Bridge owns** the adapter contract, the three-part secret suite, the
  bridge-premath realization profile, and the conformance surface. Schemas,
  reference implementations, and Nix modules ship from here.
- **Your repo owns** live provider bindings, deployment profiles, attestation
  data, revocation snapshots, and mode state. Bridge gives you the schemas and
  reference impls; you supply the real values and your workload package.

## What you get

### Spec surface

The `specs/` tree is the active normalized surface. 42 JSON schemas are
organized across 7 stable type families (Ingress, Authority, Interpretation,
Admission, Secret Core, Realization, Audit). See
[`specs/TYPE-FAMILIES.md`](specs/TYPE-FAMILIES.md) for the canonical map.

| Spec area | Covers | Entry point |
|-----------|--------|-------------|
| `bridge-adapter/` | Adapter contract: ingress, authority, interpretation, admission | [`specs/bridge-adapter/README.md`](specs/bridge-adapter/README.md) |
| `secrets/secret-0001/` | Secret object and lifecycle core | [`specs/secrets/secret-0001/`](specs/secrets/secret-0001/) |
| `secrets/secret-0002/` | Backend and materialization profile, signer-session and witness-realization edge | [`specs/secrets/secret-0002/`](specs/secrets/secret-0002/) |
| `secrets/secret-0003/` | Provider integration, attestation, audit, deployment | [`specs/secrets/secret-0003/`](specs/secrets/secret-0003/) |
| `bridge-premath-0001/` | Bridge-specific Premath realization profile | [`specs/bridge-premath-0001/`](specs/bridge-premath-0001/) |

### Nix modules

| Module | Platform | Purpose |
|--------|----------|---------|
| `nixosModules.bridgeSidecar` | NixOS (systemd) | Reference HTTP sidecar over SECRET-0003. You supply the five authority paths. |
| `nixosModules.bridgeAgentService` | NixOS (systemd) | Reference workload attachment that depends on the sidecar. You supply the workload package and executable. |
| `darwinModules.bridgeSidecar` | nix-darwin (launchd) | Same sidecar as a launchd daemon. |

The exported `bridgeSidecar` package is a **bounded reference HTTP sidecar over
SECRET-0003**, not a production-hardened deployment. Production consumers
should treat it as a contract reference and substitute their own hardened
implementation.

### Apps and checks

```bash
nix run .#bridge-conformance-check    # validate the spec surface
nix run .#bridge-property-check       # planner-law property checks
nix run .#reference-planner -- --help # SECRET-0002 reference planner
nix run .#bridge-sidecar -- --help    # reference sidecar binary
nix flake check                       # full check suite
```

## Quick start

Add bridge as a flake input and import the modules you need. Starter example
data for the five required authority paths lives in
`specs/secrets/secret-0003/examples/`:

- `provider-catalog.example.json`
- `deployment-profile.nixos-host.json` (or `deployment-profile.workstation.json`)
- `attestation-result.good.json`
- `revocation-snapshot.clean.json`
- `mode-state.normal.json`

### NixOS

```nix
{
  inputs.bridge.url = "github:workingdoge/bridge";

  outputs = { self, nixpkgs, bridge, ... }: {
    nixosConfigurations.example = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        bridge.nixosModules.bridgeSidecar
        bridge.nixosModules.bridgeAgentService
        ({ pkgs, ... }: {
          services.bridgeSidecar = {
            enable = true;
            providerCatalog = ./provider-catalog.json;
            deploymentProfile = ./deployment-profile.json;
            attestationResult = ./attestation-result.json;
            revocationSnapshot = ./revocation-snapshot.json;
            modeState = ./mode-state.json;
          };
          services.bridgeAgentService = {
            enable = true;
            package = pkgs.callPackage ./pkgs/example-agent.nix { };
            executable = "example-agent";
          };
        })
      ];
    };
  };
}
```

### nix-darwin

```nix
{
  outputs = { self, darwin, bridge, ... }: {
    darwinConfigurations.example = darwin.lib.darwinSystem {
      system = "aarch64-darwin";
      modules = [
        bridge.darwinModules.bridgeSidecar
        ({ ... }: {
          services.bridgeSidecar = {
            enable = true;
            providerCatalog = ./provider-catalog.json;
            deploymentProfile = ./deployment-profile.json;
            attestationResult = ./attestation-result.json;
            revocationSnapshot = ./revocation-snapshot.json;
            modeState = ./mode-state.json;
          };
        })
      ];
    };
  };
}
```

## Module options reference

### `services.bridgeSidecar` (NixOS and Darwin)

| Option | Type | Default | Required |
|--------|------|---------|----------|
| `enable` | bool | `false` | — |
| `package` | package | reference sidecar from this flake | — |
| `providerCatalog` | path | — | yes |
| `deploymentProfile` | path | — | yes |
| `attestationResult` | path | — | yes |
| `revocationSnapshot` | path | — | yes |
| `modeState` | path | — | yes |
| `listenAddress` | string | `"127.0.0.1"` | — |
| `listenPort` | port | `8181` | — |
| `auditLogPath` | string | `"/var/lib/bridge-sidecar/audit-events.jsonl"` | — |

The Darwin module additionally exposes `workingDirectory`
(`/var/lib/bridge-sidecar`), `stdoutPath` (`/var/log/bridge-sidecar.out.log`),
and `stderrPath` (`/var/log/bridge-sidecar.err.log`).

### `services.bridgeAgentService` (NixOS)

Requires `services.bridgeSidecar.enable = true`.

| Option | Type | Default | Required |
|--------|------|---------|----------|
| `enable` | bool | `false` | — |
| `package` | package | — | yes |
| `executable` | string | — | yes |
| `arguments` | list of string | `[]` | — |
| `bridgeFlag` | null or string | `"--bridge-url"` | — |
| `bridgeUrl` | string | derived from sidecar listen address/port | — |
| `environment` | attrs of string | `{}` | — |
| `serviceName` | string | `"bridge-agent"` | — |

The workload also receives `BRIDGE_SIDECAR_URL` in its environment regardless
of `bridgeFlag`. Set `bridgeFlag = null` to rely on the env var only.

Source: [`modules/nixos/bridge-sidecar.nix`](modules/nixos/bridge-sidecar.nix),
[`modules/nixos/bridge-agent-service.nix`](modules/nixos/bridge-agent-service.nix),
[`modules/darwin/bridge-sidecar.nix`](modules/darwin/bridge-sidecar.nix).

## Going deeper

- [`specs/TYPE-FAMILIES.md`](specs/TYPE-FAMILIES.md) — canonical map of the 7
  stable type families
- [`specs/bridge-adapter/README.md`](specs/bridge-adapter/README.md) — adapter
  contract and assembly rules
- [`specs/secrets/README.md`](specs/secrets/README.md) — secret suite overview
- [`specs/bridge-premath-0001/`](specs/bridge-premath-0001/) — Premath
  realization profile
- [`PROVENANCE.md`](PROVENANCE.md) — import record and authority split
