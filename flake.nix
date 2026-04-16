{
  description = "bridge: canonical bridge and secret domain contracts with repo-owned conformance surfaces";

  nixConfig = {
    extra-trusted-public-keys = "devenv.cachix.org-1:w1cLUi8dv3hnoSPGAuibQv+f9TZLr6cv/Hm9XgU50cw=";
    extra-substituters = "https://devenv.cachix.org";
  };

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
    # Keep Codex reproducible while consuming the shared tusk wiring.
    llm-agents.url = "github:numtide/llm-agents.nix?rev=b91b0e1583091847cf4f8a8fcaad92d66227abfb";
    devenv-root = {
      url = "file+file:///dev/null";
      flake = false;
    };
    devenv = {
      url = "github:cachix/devenv";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    tusk = {
      url = "git+https://github.com/workingdoge/tusk?ref=main&rev=e539c9b795640663b54c638b378315e0ae20b784";
      inputs.devenv.follows = "devenv";
      inputs.llm-agents.follows = "llm-agents";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = inputs@{ self, nixpkgs, tusk, devenv, ... }:
    let
      systems = [
        "aarch64-darwin"
        "x86_64-darwin"
        "aarch64-linux"
        "x86_64-linux"
      ];

      forAllSystems = f: nixpkgs.lib.genAttrs systems (system: f system);
    in
    {
      formatter = forAllSystems (system: nixpkgs.legacyPackages.${system}.nixfmt-rfc-style);

      nixosModules = {
        bridgeSidecar = import ./modules/nixos/bridge-sidecar.nix { inherit self; };
        bridgeAgentService = import ./modules/nixos/bridge-agent-service.nix;
      };

      darwinModules = {
        bridgeSidecar = import ./modules/darwin/bridge-sidecar.nix { inherit self; };
      };

      packages = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          tuskBeads = tusk.apps.${system}.beads.program;
          tuskCodex = tusk.apps.${system}.codex.program;
          beads = pkgs.writeShellApplication {
            name = "bd";
            text = ''
              exec ${tuskBeads} "$@"
            '';
          };
          pythonEnv = pkgs.python3.withPackages (ps: with ps; [ jsonschema hypothesis ]);
          bridgeSidecarRuntime = pkgs.runCommand "bridge-sidecar-runtime" {} ''
            mkdir -p "$out/share/bridge-sidecar"
            cp -R ${./specs/secrets/secret-0003/python} "$out/share/bridge-sidecar/python"
            cp -R ${./specs/secrets/secret-0003/schemas} "$out/share/bridge-sidecar/schemas"
          '';
          repoCodex = pkgs.writeShellApplication {
            name = "codex";
            runtimeInputs = [
              beads
              pkgs.git
            ];
            text = ''
              set -eu

              tracker_root="''${BEADS_WORKSPACE_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
              export BEADS_WORKSPACE_ROOT="$tracker_root"

              exec ${tuskCodex} "$@"
            '';
          };

          bridgeConformanceCheck = pkgs.writeShellApplication {
            name = "bridge-conformance-check";
            runtimeInputs = [
              pkgs.jq
              pkgs.python3Minimal
              pkgs.ripgrep
            ];
            text = ''
              exec ${./scripts/bridge-conformance-check.sh} --repo ${self} "$@"
            '';
          };

          bridgePropertyCheck = pkgs.writeShellApplication {
            name = "bridge-property-check";
            runtimeInputs = [ pythonEnv ];
            text = ''
              exec ${./scripts/bridge-property-check.sh} --repo ${self} "$@"
            '';
          };

          referencePlanner = pkgs.writeShellApplication {
            name = "reference-planner";
            runtimeInputs = [ pythonEnv ];
            text = ''
              exec python3 ${./specs/secrets/secret-0002/python/reference_planner.py} "$@"
            '';
          };

          bridgeSidecar = pkgs.writeShellApplication {
            name = "bridge-sidecar";
            runtimeInputs = [ pythonEnv ];
            text = ''
              runtime=${bridgeSidecarRuntime}/share/bridge-sidecar
              export PYTHONPATH="$runtime/python''${PYTHONPATH:+:$PYTHONPATH}"
              exec python3 "$runtime/python/reference_sidecar_server.py" --schema-dir "$runtime/schemas" "$@"
            '';
          };
        in
        {
          inherit beads bridgeConformanceCheck bridgePropertyCheck referencePlanner bridgeSidecar;
          codex = repoCodex;
          default = bridgeConformanceCheck;
        });

      apps = forAllSystems (system: {
        beads = {
          type = "app";
          program = "${self.packages.${system}.beads}/bin/bd";
          meta = {
            description = "Beads CLI";
          };
        };
        codex = {
          type = "app";
          program = "${self.packages.${system}.codex}/bin/codex";
          meta = {
            description = "Repo-pinned Codex";
          };
        };
        bridge-conformance-check = {
          type = "app";
          program = "${self.packages.${system}.bridgeConformanceCheck}/bin/bridge-conformance-check";
        };
        bridge-property-check = {
          type = "app";
          program = "${self.packages.${system}.bridgePropertyCheck}/bin/bridge-property-check";
        };
        reference-planner = {
          type = "app";
          program = "${self.packages.${system}.referencePlanner}/bin/reference-planner";
        };
        bridge-sidecar = {
          type = "app";
          program = "${self.packages.${system}.bridgeSidecar}/bin/bridge-sidecar";
        };
        default = self.apps.${system}.bridge-conformance-check;
      });

      checks = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          bridgeAgentEval = nixpkgs.lib.nixosSystem {
            system = "x86_64-linux";
            modules = [
              self.nixosModules.bridgeSidecar
              self.nixosModules.bridgeAgentService
              ({ pkgs, ... }: {
                system.stateVersion = "25.05";
                services.bridgeSidecar = {
                  enable = true;
                  listenAddress = "127.0.0.1";
                  listenPort = 8181;
                  providerCatalog = ./specs/secrets/secret-0003/examples/example.provider-catalog.json;
                  deploymentProfile = ./specs/secrets/secret-0003/examples/example.deployment-profile.json;
                  attestationResult = ./specs/secrets/secret-0003/examples/example.attestation-result.ok.json;
                  revocationSnapshot = ./specs/secrets/secret-0003/examples/example.revocation-snapshot.clear.json;
                  modeState = ./specs/secrets/secret-0003/examples/example.mode-state.normal.json;
                };
                services.bridgeAgentService = {
                  enable = true;
                  package = pkgs.hello;
                  executable = "hello";
                };
              })
            ];
          };
        in
        {
          bridge-conformance-check = pkgs.runCommand "bridge-conformance-check" {
            nativeBuildInputs = [ self.packages.${system}.bridgeConformanceCheck ];
          } ''
            bridge-conformance-check >/dev/null
            touch "$out"
          '';

          bridge-property-check = pkgs.runCommand "bridge-property-check" {
            nativeBuildInputs = [ self.packages.${system}.bridgePropertyCheck ];
          } ''
            bridge-property-check >/dev/null
            touch "$out"
          '';

          reference-planner-help = pkgs.runCommand "reference-planner-help" {
            nativeBuildInputs = [ self.packages.${system}.referencePlanner ];
          } ''
            reference-planner --help >/dev/null
            touch "$out"
          '';

          bridge-sidecar-help = pkgs.runCommand "bridge-sidecar-help" {
            nativeBuildInputs = [ self.packages.${system}.bridgeSidecar ];
          } ''
            bridge-sidecar --help >/dev/null
            touch "$out"
          '';

          bridge-agent-service-eval = pkgs.writeText "bridge-agent-service-execstart" (
            bridgeAgentEval.config.systemd.services.bridge-agent.serviceConfig.ExecStart + "\n"
          );
        });

      devShells = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          pythonEnv = pkgs.python3.withPackages (ps: with ps; [ jsonschema hypothesis ]);
          devShellModule = {
            imports = [
              devenv.flakeModules.readDevenvRoot
              tusk.devenvModules.tusk-skill
              tusk.devenvModules.ops-skill
              tusk.devenvModules.bridge-skill
            ];

            tusk.consumer = {
              enable = true;
              extraPackages = [
                pkgs.jq
                pkgs.python3Minimal
                pythonEnv
                pkgs.ripgrep
              ];
              smokeCheck.skillChecks = [
                ".codex/skills/tusk"
                ".codex/skills/ops"
                ".codex/skills/bridge"
              ];
              extraEnterShell = ''
                [ -f "$DEVENV_ROOT/.envrc.local" ] && . "$DEVENV_ROOT/.envrc.local"
                [ -f "$DEVENV_ROOT/.env.local" ] && . "$DEVENV_ROOT/.env.local"

                echo "bridge devenv shell"
                echo "  nix run .#bridge-conformance-check"
                echo "  nix run .#bridge-property-check"
                echo "  nix run .#reference-planner -- --help"
              '';
            };
          };
        in
        {
          default = tusk.lib.mkRepoShell {
            inherit system pkgs;
            flakeInputs = inputs;
            modules = [ devShellModule ];
          };
        });
    };
}
