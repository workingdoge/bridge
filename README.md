# Bridge

`bridge` is the domain home for the bridge adapter contract, the secret suite,
and bridge-specific realization profiles layered over Premath.

Boundary:

- Premath kernel doctrine stays upstream in `fish/sites/premath/`.
- This repo owns domain-specific bridge and secret specs plus their
  normalization and conformance surfaces.
- Live provider bindings, funded runtime, and first proof stay in downstream
  consumer repos until they generalize.
- Organize the bridge surface around stable type families first:
  `Ingress`, `Authority`, `Admission`, `Secret Core`, `Realization`, and
  `Audit`.

Repo map:

- `.agents/skills/bridge/` repo-authored source of truth for the shared bridge
  skill
- `modules/` repo-owned exported Nix module surface
- `specs/` normalized active spec surface
- `specs/TYPE-FAMILIES.md` canonical type-family map for interface shaping
- `references/source-bundles/` retained source bundles for provenance
- `scripts/bridge-conformance-check.sh` repo-owned conformance check
- `flake.nix` minimal Nix export surface for repo checks and the reference
  planner plus module exports
- `PROVENANCE.md` authority split and import record

Workflow:

- use `bd ready --json`
- claim with `bd update <id> --claim --json`
- close with `bd close <id> --reason "..." --json`
- run `scripts/bridge-conformance-check.sh` after spec-surface changes

Nix surface:

- `nix run .#bridge-conformance-check`
- `nix run .#bridge-property-check`
- `nix run .#reference-planner -- --help`
- `nix run .#bridge-sidecar -- --help`
- `inputs.bridge.nixosModules.bridgeSidecar`
- `inputs.bridge.darwinModules.bridgeSidecar`
- `nix flake check`

Module surface:

- the flake exports repo-owned `bridgeSidecar` modules for NixOS and
  nix-darwin
- the flake also exports a repo-owned reference package at
  `packages.<system>.bridgeSidecar`
- these are normalized consumer modules derived from the `SECRET-0003` deploy
  examples under `specs/secrets/secret-0003/deploy/`
- the modules default `services.bridgeSidecar.package` to that reference
  package
- consuming repos still provide the provider catalog and deployment profile
  paths
- this is intentionally a module surface first, not a broad `lib.*` API
- the exported package is the `SECRET-0003` reference harness, not a
  production-hardened sidecar

Example:

```nix
{
  inputs.bridge.url = "path:/path/to/bridge";

  outputs = { self, bridge, ... }: {
    nixosConfigurations.example = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        bridge.nixosModules.bridgeSidecar
        ({ pkgs, ... }: {
          services.bridgeSidecar = {
            enable = true;
            package = pkgs.callPackage ./pkgs/bridge-sidecar.nix { };
            providerCatalog = ./provider-catalog.json;
            deploymentProfile = ./deployment-profile.json;
          };
        })
      ];
    };
  };
}
```
